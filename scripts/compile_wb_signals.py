"""
Merge Wine Berserkers thread signals into producer .md frontmatter + body.

For each producer in raw/berserkers/threads/<slug>.json that matches a
wiki/producers/<slug>.md file:

  Frontmatter — upsert under `community.berserkers.threads.<thread_slug>`:
      rank, mentions, mentions_2013_2014, mentions_2021_2022,
      mentions_2023_2026, momentum_score_2023, last_updated.

  Body — upsert a `## Berserkers` section that lists each thread the
      producer appears in, with rank/era table and a link back to the thread.

The match logic mirrors compile_csw_cellar_signal.py: exact slug index +
compact alphanumeric index, with fuzzy candidates generated from the
producer's raw name (strip Domaine/Château/etc., handle slash-separated
names, generate `domaine_<x>` form).

Unmatched producers — i.e. WB names that have no wiki/producers/<slug>.md —
are NOT auto-created (anti-pattern: don't create producer pages from a
single source). Instead they're listed in build/wb_signals_report.md with
rank/mentions, ready for the gap-curation pass via build_wb_rollups.py.

Usage:
    python scripts/compile_wb_signals.py raw/berserkers/threads/top10_in_cellar.json
    python scripts/compile_wb_signals.py raw/berserkers/threads/*.json --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _now_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _now_iso_seconds() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "wb_signals_report.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


# ----------------------------------------------------------- slug matching -

PREFIXES = ["domaine ", "chateau ", "château ", "weingut ", "weiser ",
            "fattoria ", "cantina ", "tenuta ", "le ", "la ", "comm ",
            "comm. "]


def fold_ascii(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def to_slug(s: str) -> str:
    s = fold_ascii(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def compact(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold_ascii(s).lower())


def slug_candidates(name: str) -> list[str]:
    cands: list[str] = []
    parts = [p.strip() for p in re.split(r"\s*/\s*", name) if p.strip()]
    pieces = parts + [name]
    for p in pieces:
        if not p:
            continue
        cands.append(to_slug(p))
        low = p.lower()
        for pref in PREFIXES:
            if low.startswith(pref):
                cands.append(to_slug(p[len(pref):]))
                break
        if not any(low.startswith(pref) for pref in PREFIXES):
            cands.append("domaine_" + to_slug(p))
    if len(parts) > 1:
        cands.append("_".join(to_slug(p) for p in parts if p))
        cands.append("__".join(to_slug(p) for p in parts if p))
    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def build_slug_index() -> tuple[dict[str, Path], dict[str, list[Path]]]:
    exact: dict[str, Path] = {}
    cidx: dict[str, list[Path]] = {}
    for p in sorted(PRODUCERS.glob("*.md")):
        stem = p.stem.lower()
        exact[stem] = p
        cidx.setdefault(compact(stem), []).append(p)
    return exact, cidx


def match_path(raw_name: str,
               exact: dict[str, Path],
               cidx: dict[str, list[Path]]) -> tuple[Path | None, list[Path]]:
    cands = slug_candidates(raw_name)
    hits: list[Path] = []
    for c in cands:
        p = exact.get(c)
        if p and p not in hits:
            hits.append(p)
    if not hits:
        cset = {compact(c) for c in cands if c}
        cset.add(compact(raw_name))
        for cc in cset:
            for p in cidx.get(cc, []):
                if p not in hits:
                    hits.append(p)
    if len(hits) == 1:
        return hits[0], hits
    if len(hits) >= 2:
        # prefer the slug whose first candidate matched
        for pc in cands[:2]:
            for h in hits:
                if h.stem.lower() == pc:
                    return h, hits
        return None, hits
    return None, []


# ----------------------------------------------------- frontmatter editing -

def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


# Locate or create the nested community.berserkers.threads.<slug> block.

COMMUNITY_RE = re.compile(r"^community:\s*$", re.MULTILINE)
BERSERKERS_RE = re.compile(r"^  berserkers:\s*$", re.MULTILINE)
THREADS_RE = re.compile(r"^    threads:\s*$", re.MULTILINE)


def upsert_thread_block(fm: str, thread_slug: str, payload: dict) -> tuple[str, str]:
    """Insert/update the per-thread block under community.berserkers.threads.

    Returns (new_fm, action) where action is one of: added, updated, no_change.
    """
    lines = fm.split("\n")

    def find_line(pattern: re.Pattern) -> int:
        for i, ln in enumerate(lines):
            if pattern.match(ln):
                return i
        return -1

    def end_of_block_at(idx: int, indent: int) -> int:
        """Return the line index just past the block whose header is at idx."""
        end = len(lines)
        for j in range(idx + 1, len(lines)):
            ln = lines[j]
            if not ln.strip():
                continue
            leading = len(ln) - len(ln.lstrip(" "))
            if leading <= indent:
                end = j
                break
        return end

    # 1. Ensure `community:` exists
    cidx = find_line(COMMUNITY_RE)
    if cidx == -1:
        # Append at end of frontmatter, before any `_sources:` block if present
        insert_at = len(lines)
        for i, ln in enumerate(lines):
            if ln.startswith("_sources:") or ln.startswith("tags:"):
                insert_at = i
                break
        block = ["community:", "  berserkers:", "    threads:"]
        block.extend(_render_thread_yaml(thread_slug, payload, base_indent=6))
        lines = lines[:insert_at] + block + lines[insert_at:]
        return "\n".join(lines), "added"

    # 2. Ensure `community.berserkers:`
    bidx = -1
    cend = end_of_block_at(cidx, indent=0)
    for j in range(cidx + 1, cend):
        if BERSERKERS_RE.match(lines[j]):
            bidx = j
            break
    if bidx == -1:
        # Insert berserkers + threads block right after community:
        block = ["  berserkers:", "    threads:"]
        block.extend(_render_thread_yaml(thread_slug, payload, base_indent=6))
        lines = lines[:cidx + 1] + block + lines[cidx + 1:]
        return "\n".join(lines), "added"

    # 3. Ensure `threads:`
    tidx = -1
    bend = end_of_block_at(bidx, indent=2)
    for j in range(bidx + 1, bend):
        if THREADS_RE.match(lines[j]):
            tidx = j
            break
    if tidx == -1:
        block = ["    threads:"]
        block.extend(_render_thread_yaml(thread_slug, payload, base_indent=6))
        lines = lines[:bidx + 1] + block + lines[bidx + 1:]
        return "\n".join(lines), "added"

    # 4. Look for the specific thread block
    tend = end_of_block_at(tidx, indent=4)
    thread_header_re = re.compile(rf"^      {re.escape(thread_slug)}:\s*$")
    sidx = -1
    for j in range(tidx + 1, tend):
        if thread_header_re.match(lines[j]):
            sidx = j
            break
    new_block = _render_thread_yaml(thread_slug, payload, base_indent=6)
    if sidx == -1:
        lines = lines[:tidx + 1] + new_block + lines[tidx + 1:]
        return "\n".join(lines), "added"

    # Replace the existing block (header + indented children)
    send = end_of_block_at(sidx, indent=6)
    if lines[sidx:send] == new_block:
        return "\n".join(lines), "no_change"
    lines = lines[:sidx] + new_block + lines[send:]
    return "\n".join(lines), "updated"


def _render_thread_yaml(thread_slug: str, p: dict, base_indent: int) -> list[str]:
    pad = " " * base_indent
    out = [f"{pad}{thread_slug}:"]
    pad2 = " " * (base_indent + 2)

    def kv(key: str, val):
        if val is None:
            out.append(f"{pad2}{key}: null")
        elif isinstance(val, bool):
            out.append(f"{pad2}{key}: {'true' if val else 'false'}")
        elif isinstance(val, str):
            out.append(f"{pad2}{key}: {val}")
        else:
            out.append(f"{pad2}{key}: {val}")

    kv("rank", p.get("rank"))
    kv("mentions", p.get("mentions"))
    kv("mentions_2013_2014", p.get("mentions_2013_2014"))
    kv("mentions_2021_2022", p.get("mentions_2021_2022"))
    kv("mentions_2023_2026", p.get("mentions_2023_2026"))
    score = p.get("momentum_score_2023")
    # Render +inf as "inf" string for YAML round-tripping
    if score is not None and score == float("inf"):
        out.append(f"{pad2}momentum_score_2023: inf")
    else:
        kv("momentum_score_2023", score)
    kv("last_updated", _now_iso_date())
    return out


# ----------------------------------------------------- body section editing -

BERS_HEADER = "## Berserkers"


def render_body_section(producer_name: str, threads: list[tuple[dict, dict]]) -> str:
    """Render the full ## Berserkers body section.

    `threads` is a list of (thread_metadata, producer_payload) tuples — one
    per thread the producer appears in.
    """
    parts = [BERS_HEADER, ""]
    for thread, p in sorted(threads, key=lambda x: -x[1].get("mentions", 0)):
        title = thread.get("title", "(untitled thread)")
        url = thread.get("url", "")
        tid = thread.get("thread_id")
        unique = thread.get("unique_producers")
        post_count = thread.get("post_count")
        first = thread.get("first_post_date", "")
        last = thread.get("last_post_date", "")

        title_link = f"[{title}]({url})" if url else title
        meta_bits = []
        if tid:
            meta_bits.append(f"thread #{tid}")
        if first or last:
            meta_bits.append(f"{first}–{last}".strip("–"))
        meta = f" ({', '.join(meta_bits)})" if meta_bits else ""
        parts.append(f"### {title_link}{meta}")
        parts.append("")

        rank = p.get("rank")
        mentions = p.get("mentions")
        if rank and unique:
            lead = f"**Rank {rank}** of {unique} producers"
        elif rank:
            lead = f"**Rank {rank}**"
        else:
            lead = "Mentioned"
        if mentions and post_count:
            lead += f" — **{mentions} mentions** across {post_count} posts."
        elif mentions:
            lead += f" — **{mentions} mentions**."
        parts.append(lead)
        parts.append("")

        e1 = p.get("mentions_2013_2014")
        e2 = p.get("mentions_2021_2022")
        e3 = p.get("mentions_2023_2026")
        if any(v is not None for v in (e1, e2, e3)):
            parts.append("| Era | Mentions |")
            parts.append("|---|---|")
            parts.append(f"| 2013–2014 | {e1 if e1 is not None else '—'} |")
            parts.append(f"| 2021–2022 | {e2 if e2 is not None else '—'} |")
            parts.append(f"| 2023–2026 | {e3 if e3 is not None else '—'} |")
            parts.append("")

        score = p.get("momentum_score_2023")
        if score is not None:
            if score == float("inf") or (isinstance(score, str) and score == "inf"):
                parts.append("**Momentum 2023+:** new entrant (no earlier-era baseline).")
            elif score >= 2.5:
                parts.append(f"**Momentum 2023+:** {score}× (strongly accelerating).")
            elif score >= 1.2:
                parts.append(f"**Momentum 2023+:** {score}× (rising).")
            elif score == 0.0:
                parts.append("**Momentum 2023+:** 0.0× (dropped off — early-thread producer with no recent mentions).")
            elif score < 0.5:
                parts.append(f"**Momentum 2023+:** {score}× (fading).")
            else:
                parts.append(f"**Momentum 2023+:** {score}× (steady).")
            parts.append("")

        for q in p.get("notable_quotes", [])[:3]:
            user = q.get("user", "")
            year = q.get("year", "")
            text = q.get("text", "").strip()
            if text:
                attribution = f" — *{user}, {year}*" if user or year else ""
                parts.append(f"> {text}{attribution}")
                parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def upsert_body_section(body: str, new_section: str) -> tuple[str, str]:
    """Replace existing ## Berserkers section, or insert before next ##
    after ## CSW Write-ups, or append at end."""
    # Replace existing section
    pattern = re.compile(rf"\n{re.escape(BERS_HEADER)}\n.*?(?=\n## |\Z)", re.DOTALL)
    if pattern.search(body):
        new_body = pattern.sub("\n" + new_section.rstrip() + "\n", body)
        return new_body, "updated" if new_body != body else "no_change"

    # Insert after CSW Cellar Note if present, else after CSW Write-ups, else at end
    for anchor in ["## CSW Cellar Note", "## CSW Write-ups"]:
        idx = body.find(anchor)
        if idx >= 0:
            # Find next "## " header after this anchor
            after = body.find("\n## ", idx + len(anchor))
            if after >= 0:
                new_body = body[:after] + "\n" + new_section.rstrip() + "\n" + body[after:]
                return new_body, "inserted"
            new_body = body.rstrip() + "\n\n" + new_section
            return new_body, "appended"

    # No anchor — insert before Cross-references / Notes / Cellar / EOF
    for anchor in ["## Cross-references", "## Notes", "## Cellar"]:
        idx = body.find(anchor)
        if idx >= 0:
            new_body = body[:idx] + new_section.rstrip() + "\n\n" + body[idx:]
            return new_body, "inserted"
    new_body = body.rstrip() + "\n\n" + new_section
    return new_body, "appended"


# -------------------------------------------------------------------- main -

@dataclass
class MatchResult:
    raw_name: str
    rank: int
    mentions: int
    path: Path | None
    candidates: list[Path]
    payload: dict
    thread_meta: dict


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+",
                    help="One or more raw/berserkers/threads/<slug>.json files")
    ap.add_argument("--apply", action="store_true",
                    help="Write changes (default: dry-run)")
    ap.add_argument("--top-only", type=int, default=0,
                    help="Only annotate the top-N producers per thread (0 = all)")
    args = ap.parse_args()

    exact, cidx = build_slug_index()
    print(f"Vault has {len(exact)} producer files")

    threads_by_path: dict[Path, list[tuple[dict, dict]]] = {}
    matches: list[MatchResult] = []
    unmatched: list[MatchResult] = []
    ambiguous: list[MatchResult] = []

    for src_path in args.sources:
        src = Path(src_path)
        data = json.loads(src.read_text(encoding="utf-8"))
        thread_meta = data["thread"]
        producers = data["producers"]
        if args.top_only:
            producers = producers[:args.top_only]
        print(f"\n{src.name}: {len(producers)} producers, "
              f"thread '{thread_meta.get('title', '?')}'")

        for p in producers:
            path, hits = match_path(p["raw_name"], exact, cidx)
            mr = MatchResult(
                raw_name=p["raw_name"],
                rank=p.get("rank", 0),
                mentions=p.get("mentions", 0),
                path=path,
                candidates=hits,
                payload=p,
                thread_meta=thread_meta,
            )
            if path:
                matches.append(mr)
                threads_by_path.setdefault(path, []).append((thread_meta, p))
            elif len(hits) >= 2:
                ambiguous.append(mr)
            else:
                unmatched.append(mr)

    print(f"\nMatch results: {len(matches)} matched, "
          f"{len(unmatched)} unmatched, {len(ambiguous)} ambiguous")

    # ---- write report ----
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "type: signals_report",
        "source: berserkers",
        f'generated: "{_now_iso_seconds()}"',
        f"sources: {[str(Path(s).name) for s in args.sources]}",
        f"matched: {len(matches)}",
        f"unmatched: {len(unmatched)}",
        f"ambiguous: {len(ambiguous)}",
        f"apply_mode: {args.apply}",
        "---",
        "",
        "# Berserkers signal compile report",
        "",
        f"Compiled signals from {len(args.sources)} thread(s) into "
        f"{len(threads_by_path)} producer pages.",
        "",
    ]

    if unmatched:
        lines += [
            f"## Unmatched ({len(unmatched)})",
            "",
            "WB names with no matching `wiki/producers/<slug>.md`. These are gap candidates.",
            "Add an alias entry to `parse_wb_thread.py` PRODUCER_ALIASES if the name is",
            "actually a different spelling of an existing producer; otherwise consider",
            "adding to the vault via the standard CSW/DTE/Raeders curation flow.",
            "",
            "| Rank | Mentions | Raw name | Tried slugs |",
            "|---|---|---|---|",
        ]
        for mr in sorted(unmatched, key=lambda m: -m.mentions)[:80]:
            tried = ", ".join(slug_candidates(mr.raw_name)[:3])
            lines.append(f"| {mr.rank} | {mr.mentions} | {mr.raw_name} | `{tried}` |")
        if len(unmatched) > 80:
            lines.append(f"| … | | _{len(unmatched) - 80} more_ | |")
        lines.append("")

    if ambiguous:
        lines += [
            f"## Ambiguous ({len(ambiguous)})",
            "",
            "Multiple candidate producer files matched a single WB name. Disambiguate",
            "by adding `aliases:` entries on the correct page or splitting/renaming.",
            "",
        ]
        for mr in ambiguous[:30]:
            lines.append(f"- **{mr.raw_name}** ({mr.mentions} mentions) → "
                         f"{', '.join(p.name for p in mr.candidates)}")
        lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {REPORT}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write producer pages.")
        return 0

    # ---- apply ----
    fm_changes = body_changes = 0
    for path, threads in threads_by_path.items():
        text = path.read_text(encoding="utf-8")
        split = split_frontmatter(text)
        if not split:
            print(f"  skip (no frontmatter): {path.name}")
            continue
        fm, body = split

        # Apply each thread's frontmatter
        for thread_meta, payload in threads:
            slug = thread_meta["slug"]
            fm, action = upsert_thread_block(fm, slug, payload)
            if action != "no_change":
                fm_changes += 1

        # Re-render the full ## Berserkers section
        new_section = render_body_section(path.stem, threads)
        body, body_action = upsert_body_section(body, new_section)
        if body_action != "no_change":
            body_changes += 1

        new_text = f"---\n{fm}\n---\n{body}"
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")

    print(f"\nApplied: {fm_changes} frontmatter changes, "
          f"{body_changes} body sections updated, "
          f"across {len(threads_by_path)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
