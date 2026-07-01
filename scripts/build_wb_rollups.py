"""
Generate rollup views from Wine Berserkers thread data.

Reads all raw/berserkers/threads/*.json, joins against wiki/producers/*.md
and cellar/*.md, and emits four rollup pages:

  wiki/_views/wb_top_100.md           Top 100 by mentions, with vault + cellar status
  wiki/_views/wb_momentum_2023.md     Sorted by 2023+ momentum score
  wiki/_views/wb_in_cellar.md         Producers Evan owns AND that WB also ranks
  build/wb_gap_candidates.md          WB top names not in the vault — curation candidates

`build/wb_gap_candidates.md` is the file Evan reviews when deciding whether
to onboard a new producer page. It deliberately lives in `build/` (not the
wiki) so it stays out of the canonical knowledge base until curated.

Usage:
    python scripts/build_wb_rollups.py            # dry-run (lists what it would write)
    python scripts/build_wb_rollups.py --apply    # write the files

By default uses every JSON in raw/berserkers/threads/. Pass --thread to
restrict to one slug.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _now_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
VIEWS = VAULT / "wiki" / "_views"
THREADS_DIR = VAULT / "raw" / "berserkers" / "threads"
CELLAR = VAULT / "cellar"
GAPS = VAULT / "build" / "wb_gap_candidates.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


# ----------------------------------------------------------- slug matching -

PREFIXES = ["domaine ", "chateau ", "château ", "weingut ", "weiser ",
            "fattoria ", "cantina ", "tenuta ", "le ", "la "]


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
    seen = set()
    out = []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def build_indices() -> tuple[dict[str, Path], dict[str, list[Path]]]:
    exact: dict[str, Path] = {}
    cidx: dict[str, list[Path]] = {}
    for p in sorted(PRODUCERS.glob("*.md")):
        stem = p.stem.lower()
        exact[stem] = p
        cidx.setdefault(compact(stem), []).append(p)
    return exact, cidx


def find_path(raw_name: str, exact, cidx) -> Path | None:
    for c in slug_candidates(raw_name):
        if c in exact:
            return exact[c]
    cset = {compact(c) for c in slug_candidates(raw_name)}
    cset.add(compact(raw_name))
    for cc in cset:
        hits = cidx.get(cc, [])
        if len(hits) == 1:
            return hits[0]
    return None


# -------------------------------------------------------- producer info ---

def get_fm_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def producer_info(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return {"slug": path.stem, "name": path.stem, "country": "", "region": ""}
    fm = m.group(1)
    return {
        "slug": path.stem,
        "name": get_fm_str(fm, "name") or path.stem,
        "country": get_fm_str(fm, "country"),
        "region": get_fm_str(fm, "region"),
    }


def cellar_counts() -> dict[str, int]:
    """Return {producer_slug: bottle_count} from cellar/*.md."""
    out: dict[str, int] = defaultdict(int)
    if not CELLAR.exists():
        return dict(out)
    for cf in CELLAR.glob("*.md"):
        text = cf.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        if not m:
            continue
        slug_m = re.search(r"^producer_slug:\s*(\S+)\s*$", m.group(1), re.MULTILINE)
        qty_m = re.search(r"^quantity:\s*(\d+)\s*$", m.group(1), re.MULTILINE)
        if slug_m:
            out[slug_m.group(1).strip()] += int(qty_m.group(1)) if qty_m else 1
    return dict(out)


# ----------------------------------------------------------- view builders -

def momentum_label(score) -> str:
    if score is None:
        return "—"
    if score == "inf" or score == float("inf"):
        return "🆕 new"
    s = float(score)
    if s >= 5:
        return f"🚀 {s}×"
    if s >= 2.5:
        return f"⬆ {s}×"
    if s >= 1.2:
        return f"↗ {s}×"
    if s == 0:
        return "✗ 0×"
    if s < 0.5:
        return f"↘ {s}×"
    return f"≈ {s}×"


def render_top_100(thread: dict, producers: list[dict],
                   slug_for: dict[str, str | None],
                   cellar: dict[str, int]) -> str:
    title = thread.get("title", "WB Thread")
    url = thread.get("url", "")
    out = [
        "---",
        "type: view",
        f'source: "berserkers/{thread["slug"]}"',
        f"updated: {_now_iso_date()}",
        "---",
        "",
        f"# WB Top 100 — {title}",
        "",
        f"Source: [{url}]({url}) · {thread.get('post_count', '?')} posts · "
        f"{thread.get('unique_producers', '?')} unique producers · "
        f"{thread.get('total_mentions', '?')} mentions · "
        f"{thread.get('first_post_date', '')}–{thread.get('last_post_date', '')}",
        "",
        "✅ = page exists in vault · 🍷 = bottles in cellar",
        "",
        "| # | Producer | Mentions | Era 13–14 | Era 21–22 | Era 23–26 | Momentum 23+ | Vault | Cellar |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for p in producers[:100]:
        slug = slug_for.get(p["raw_name"])
        in_vault = "✅" if slug else "—"
        bot = cellar.get(slug, 0) if slug else 0
        in_cellar = f"🍷 {bot}" if bot else "—"
        link = f"[[{slug}|{p['raw_name']}]]" if slug else p["raw_name"]
        out.append(
            f"| {p['rank']} | {link} | {p['mentions']} | "
            f"{p.get('mentions_2013_2014') if p.get('mentions_2013_2014') is not None else '—'} | "
            f"{p.get('mentions_2021_2022') if p.get('mentions_2021_2022') is not None else '—'} | "
            f"{p.get('mentions_2023_2026') if p.get('mentions_2023_2026') is not None else '—'} | "
            f"{momentum_label(p.get('momentum_score_2023'))} | "
            f"{in_vault} | {in_cellar} |"
        )
    return "\n".join(out) + "\n"


def render_momentum(thread: dict, producers: list[dict],
                    slug_for: dict[str, str | None]) -> str:
    title = thread.get("title", "WB Thread")
    out = [
        "---",
        "type: view",
        f'source: "berserkers/{thread["slug"]}"',
        f"updated: {_now_iso_date()}",
        "---",
        "",
        f"# WB Momentum 2023+ — {title}",
        "",
        "Producers ranked by acceleration of mentions in the 2023+ era vs. their",
        "earliest active era. **Excludes the literal new entrants** (no earlier",
        "baseline) — see `New Entrants` section below.",
        "",
        "## Surging — score ≥ 1.2 with prior baseline",
        "",
        "| Producer | Score | Mentions | Era 13–14 | Era 21–22 | Era 23–26 | Vault |",
        "|---|---|---|---|---|---|---|",
    ]

    def has_prior(p):
        return (p.get("mentions_2013_2014") or 0) > 0 or (p.get("mentions_2021_2022") or 0) > 0

    surging = [p for p in producers if isinstance(p.get("momentum_score_2023"), (int, float))
               and p["momentum_score_2023"] != float("inf")
               and p["momentum_score_2023"] >= 1.2]
    for p in sorted(surging, key=lambda x: -x["momentum_score_2023"])[:50]:
        slug = slug_for.get(p["raw_name"])
        link = f"[[{slug}|{p['raw_name']}]]" if slug else p["raw_name"]
        out.append(
            f"| {link} | {p['momentum_score_2023']}× | {p['mentions']} | "
            f"{p.get('mentions_2013_2014') if p.get('mentions_2013_2014') is not None else '—'} | "
            f"{p.get('mentions_2021_2022') if p.get('mentions_2021_2022') is not None else '—'} | "
            f"{p.get('mentions_2023_2026') if p.get('mentions_2023_2026') is not None else '—'} | "
            f"{'✅' if slug else '—'} |"
        )

    out += [
        "",
        "## New entrants (zero mentions before 2023)",
        "",
        "| Producer | Mentions | Era 23–26 | Vault |",
        "|---|---|---|---|",
    ]
    new_entrants = [p for p in producers
                    if (p.get("mentions_2013_2014") or 0) == 0
                    and (p.get("mentions_2021_2022") or 0) == 0
                    and (p.get("mentions_2023_2026") or 0) >= 5]
    for p in sorted(new_entrants, key=lambda x: -x.get("mentions_2023_2026", 0))[:30]:
        slug = slug_for.get(p["raw_name"])
        link = f"[[{slug}|{p['raw_name']}]]" if slug else p["raw_name"]
        out.append(
            f"| {link} | {p['mentions']} | "
            f"{p.get('mentions_2023_2026', 0)} | "
            f"{'✅' if slug else '—'} |"
        )

    out += [
        "",
        "## Fading — early-thread producers with no recent mentions",
        "",
        "| Producer | Mentions | Era 13–14 | Era 23–26 |",
        "|---|---|---|---|",
    ]
    fading = [p for p in producers
              if (p.get("mentions_2013_2014") or 0) >= 5
              and (p.get("mentions_2023_2026") or 0) == 0]
    for p in sorted(fading, key=lambda x: -x.get("mentions_2013_2014", 0))[:20]:
        slug = slug_for.get(p["raw_name"])
        link = f"[[{slug}|{p['raw_name']}]]" if slug else p["raw_name"]
        out.append(f"| {link} | {p['mentions']} | "
                   f"{p.get('mentions_2013_2014', 0)} | "
                   f"{p.get('mentions_2023_2026', 0)} |")

    return "\n".join(out) + "\n"


def render_in_cellar(threads_data: list[tuple[dict, list[dict]]],
                     slug_for: dict[str, str | None],
                     cellar: dict[str, int],
                     prod_info: dict[str, dict]) -> str:
    """One row per producer Evan owns, joined to WB rank from the
    highest-ranked thread that includes it."""
    rows: dict[str, dict] = {}
    for thread, producers in threads_data:
        for p in producers:
            slug = slug_for.get(p["raw_name"])
            if not slug or slug not in cellar:
                continue
            existing = rows.get(slug)
            if existing is None or p.get("rank", 9999) < existing["rank"]:
                rows[slug] = {
                    "slug": slug,
                    "raw_name": p["raw_name"],
                    "rank": p.get("rank", 0),
                    "mentions": p.get("mentions", 0),
                    "thread_slug": thread["slug"],
                    "thread_title": thread.get("title", ""),
                    "momentum": p.get("momentum_score_2023"),
                    "bottles": cellar[slug],
                    "country": prod_info.get(slug, {}).get("country", ""),
                    "region": prod_info.get(slug, {}).get("region", ""),
                }

    out = [
        "---",
        "type: view",
        'source: "berserkers/all"',
        f"updated: {_now_iso_date()}",
        "---",
        "",
        "# Cellar × WB — what I own that Berserkers also rank",
        "",
        f"{len(rows)} producers in your cellar overlap with WB threads.",
        "",
        "| Producer | Country | Region | Bottles | WB Rank | Mentions | Momentum | Thread |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(rows.values(), key=lambda x: x["rank"]):
        out.append(
            f"| [[{r['slug']}|{r['raw_name']}]] | {r['country']} | {r['region']} | "
            f"🍷 {r['bottles']} | {r['rank']} | {r['mentions']} | "
            f"{momentum_label(r['momentum'])} | {r['thread_title']} |"
        )
    return "\n".join(out) + "\n"


def render_gaps(threads_data: list[tuple[dict, list[dict]]],
                slug_for: dict[str, str | None],
                top_n: int = 100) -> str:
    """WB top-N producers with no matching wiki/producers/<slug>.md.
    Curation candidates — Evan reviews and decides which to onboard."""
    gaps: dict[str, dict] = {}
    for thread, producers in threads_data:
        for p in producers[:top_n]:
            if slug_for.get(p["raw_name"]) is not None:
                continue
            existing = gaps.get(p["raw_name"])
            if existing is None or p.get("rank", 9999) < existing["rank"]:
                gaps[p["raw_name"]] = {
                    "raw_name": p["raw_name"],
                    "rank": p.get("rank", 0),
                    "mentions": p.get("mentions", 0),
                    "momentum": p.get("momentum_score_2023"),
                    "thread_title": thread.get("title", ""),
                    "thread_slug": thread["slug"],
                    "tried_slugs": slug_candidates(p["raw_name"])[:3],
                }

    out = [
        "---",
        "type: gap_candidates",
        "source: berserkers",
        f"updated: {_now_iso_date()}",
        f"count: {len(gaps)}",
        "---",
        "",
        "# WB Gap Candidates — top names not in the vault",
        "",
        "Producers ranked in the WB top {} of any thread that have no matching "
        "`wiki/producers/<slug>.md`. Two follow-up actions:".format(top_n),
        "",
        "1. **Alias mismatch** — the producer is in the vault under a different "
        "spelling. Add an alias entry to `parse_wb_thread.py PRODUCER_ALIASES`, "
        "re-run `parse_wb_thread.py` against the source dump, then re-run "
        "`compile_wb_signals.py --apply`.",
        "2. **Genuinely missing** — decide whether to onboard a wiki page. Per "
        "`CLAUDE.md`: don't auto-create from a single source. WB momentum + "
        "cross-references with CSW / DTE / Raeders are the right signal.",
        "",
        "| Rank | Mentions | Momentum 23+ | Producer | Tried slugs | Thread |",
        "|---|---|---|---|---|---|",
    ]
    for g in sorted(gaps.values(), key=lambda x: x["rank"]):
        tried = ", ".join(f"`{s}`" for s in g["tried_slugs"])
        out.append(
            f"| {g['rank']} | {g['mentions']} | {momentum_label(g['momentum'])} | "
            f"{g['raw_name']} | {tried} | {g['thread_title']} |"
        )
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------- main -

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thread", help="Restrict to one thread slug "
                                     "(default: all threads in raw/berserkers/threads/)")
    ap.add_argument("--apply", action="store_true",
                    help="Write rollup files (default: dry-run)")
    args = ap.parse_args()

    if args.thread:
        sources = [THREADS_DIR / f"{args.thread}.json"]
    else:
        # Only tally JSONs — skip raw scrape dumps (<slug>.discourse.json).
        sources = sorted(p for p in THREADS_DIR.glob("*.json")
                         if not p.name.endswith(".discourse.json"))
    if not sources:
        print("No thread JSONs found.", file=sys.stderr)
        return 2

    exact, cidx = build_indices()
    cellar = cellar_counts()
    print(f"Vault: {len(exact)} producer files · cellar: "
          f"{sum(cellar.values())} bottles across {len(cellar)} producers")

    # Pre-resolve slug for every WB raw_name we'll encounter (cached)
    slug_for: dict[str, str | None] = {}
    threads_data: list[tuple[dict, list[dict]]] = []
    for src in sources:
        data = json.loads(src.read_text(encoding="utf-8"))
        thread = data["thread"]
        producers = data["producers"]
        for p in producers:
            if p["raw_name"] not in slug_for:
                path = find_path(p["raw_name"], exact, cidx)
                slug_for[p["raw_name"]] = path.stem if path else None
        threads_data.append((thread, producers))

    prod_info = {p.stem: producer_info(p) for p in PRODUCERS.glob("*.md")}

    # Build the rollups
    outputs: list[tuple[Path, str]] = []
    for thread, producers in threads_data:
        out_path = VIEWS / f"wb_{thread['slug']}_top_100.md"
        outputs.append((out_path, render_top_100(thread, producers, slug_for, cellar)))
        out_path = VIEWS / f"wb_{thread['slug']}_momentum.md"
        outputs.append((out_path, render_momentum(thread, producers, slug_for)))

    outputs.append((VIEWS / "wb_in_cellar.md",
                    render_in_cellar(threads_data, slug_for, cellar, prod_info)))
    outputs.append((GAPS,
                    render_gaps(threads_data, slug_for, top_n=100)))

    # Write or dry-run
    print(f"\n{'Writing' if args.apply else 'Would write'} {len(outputs)} files:")
    for path, content in outputs:
        size = len(content.splitlines())
        print(f"  {'WRITE' if args.apply else 'DRY  '} {path}   ({size} lines)")
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
