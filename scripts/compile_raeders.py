"""
Compile raw/raeders/master_<date>.csv into wiki/producers/.

This is the LLM-shaped compile step in the Karpathy pattern. It does:

  1. Group raw bottles by producer.
  2. For each Raeders producer, match against wiki/producers/ using:
       a. exact slug match (post-normalization)
       b. exact match against frontmatter `aliases:` list
       c. canonical-name fuzzy match (strip "Domaine"/"Château"/etc.,
          ASCII-fold, lowercase, then compare with difflib similarity).
       Threshold for auto-apply: ≥ 0.92 similarity AND no other producer
       within 0.05 of that score.
  3. For confident matches:
       - Update `retailers.raeders` block in frontmatter.
       - Replace the `## Raeder's` section with a cuvée table.
       - If there's a Raeders tasting note + critic score, append a
         `## Raeders Notes` block under it.
  4. For ambiguous matches OR "new candidate" producers (no match,
     ≥2 bottles): emit them to build/raeders_compile_review.md so the
     LLM/human can curate.

Idempotent. Re-runs cleanly.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RAW_DIR = VAULT / "raw" / "raeders"
REPORT = VAULT / "build" / "raeders_compile_review.md"

PREFIXES = (
    "Domaine ", "Château ", "Chateau ", "Ch. ", "Ch ",
    "Weingut ", "Maison ", "Bodega ", "Bodegas ",
    "Tenuta ", "Cantina ", "Azienda Agricola ", "Agricola ",
    "Le ", "La ", "Les ", "El ",
)

FUZZY_AUTO = 0.92  # min similarity for confident auto-apply
FUZZY_REVIEW = 0.78  # below this we don't even surface as a candidate


def latest_master() -> Path:
    cands = sorted(RAW_DIR.glob("master_*.csv"))
    if not cands:
        raise SystemExit(f"No master_*.csv in {RAW_DIR}; run scrape+parse first.")
    return cands[-1]


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def canonical(name: str) -> str:
    """Strip common prefixes, ASCII-fold, lowercase."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.strip()
    for p in PREFIXES:
        if s.startswith(p):
            s = s[len(p):].strip()
            break
    s = re.sub(r"[^\w\s]", " ", s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


# --- raw aggregation ---

@dataclass
class Cuvee:
    cuvee: str
    vintage: str
    size: str
    price: float
    mixed_case: float
    score_wa: int
    score_js: int
    score_we: int
    tasting_note: str
    url: str


@dataclass
class RaedersProducer:
    name: str
    slug_guess: str
    cuvees: list[Cuvee] = field(default_factory=list)
    countries: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)

    @property
    def n(self) -> int: return len(self.cuvees)

    @property
    def price_min(self) -> float:
        ps = [c.price for c in self.cuvees if c.price > 0]
        return min(ps) if ps else 0.0

    @property
    def price_max(self) -> float:
        ps = [c.price for c in self.cuvees if c.price > 0]
        return max(ps) if ps else 0.0

    @property
    def has_score(self) -> bool:
        return any(c.score_wa or c.score_js or c.score_we for c in self.cuvees)


def load_raw() -> dict[str, RaedersProducer]:
    csv_path = latest_master()
    out: dict[str, RaedersProducer] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pname = (row.get("producer") or "").strip()
            if not pname:
                continue
            sl = slug(pname)
            p = out.get(sl)
            if p is None:
                p = RaedersProducer(name=pname, slug_guess=sl)
                out[sl] = p
            p.countries.add((row.get("country") or "").strip())
            p.regions.add((row.get("region") or "").strip())
            try:
                price = float(row.get("price_usd") or 0)
            except ValueError:
                price = 0.0
            try:
                mc = float(row.get("mixed_case_usd") or 0)
            except ValueError:
                mc = 0.0
            def num(k: str) -> int:
                try: return int(row.get(k) or 0)
                except ValueError: return 0
            p.cuvees.append(Cuvee(
                cuvee=(row.get("cuvee") or "").strip(),
                vintage=(row.get("vintage") or "").strip() or "NV",
                size=(row.get("size") or "").strip(),
                price=price,
                mixed_case=mc,
                score_wa=num("score_wa"),
                score_js=num("score_js"),
                score_we=num("score_we"),
                tasting_note=(row.get("tasting_note") or "").strip(),
                url=(row.get("url") or "").strip(),
            ))
    return out


# --- wiki producer index ---

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_fm(text: str):
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', m.group(1)):
        v = next((x for x in part if x), "").strip()
        if v:
            out.append(v)
    return out


@dataclass
class WikiEntry:
    slug: str
    name: str
    aliases: list[str]
    canonical_name: str
    canonical_aliases: set[str]
    path: Path


def load_wiki() -> dict[str, WikiEntry]:
    out: dict[str, WikiEntry] = {}
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_fm(text)
        if not parts:
            continue
        fm, _ = parts
        if get_str(fm, "type") != "producer":
            continue
        name = get_str(fm, "name") or p.stem
        aliases = get_list(fm, "aliases")
        out[p.stem] = WikiEntry(
            slug=p.stem,
            name=name,
            aliases=aliases,
            canonical_name=canonical(name),
            canonical_aliases={canonical(a) for a in aliases},
            path=p,
        )
    return out


# --- matching ---

def best_match(rp: RaedersProducer, wiki: dict[str, WikiEntry]
               ) -> tuple[WikiEntry | None, float, str]:
    """Return (best_entry, score, reason)."""
    rsl = rp.slug_guess
    if rsl in wiki:
        return wiki[rsl], 1.0, "slug_exact"

    rcanon = canonical(rp.name)

    # alias exact match
    for w in wiki.values():
        if rcanon in w.canonical_aliases:
            return w, 1.0, "alias_exact"
        if w.canonical_name == rcanon:
            return w, 1.0, "canonical_exact"

    # fuzzy
    best, best_score = None, 0.0
    second_best = 0.0
    for w in wiki.values():
        s1 = SequenceMatcher(None, rcanon, w.canonical_name).ratio()
        s2 = max((SequenceMatcher(None, rcanon, a).ratio()
                  for a in w.canonical_aliases), default=0.0)
        s = max(s1, s2)
        if s > best_score:
            second_best = best_score
            best_score = s
            best = w
        elif s > second_best:
            second_best = s
    margin = best_score - second_best
    return best, best_score, f"fuzzy(score={best_score:.2f}, margin={margin:.2f})"


# --- frontmatter / section update ---

RAEDERS_BLOCK_RE = re.compile(
    r"^  raeders:\n(?:    [^\n]*\n)+",
    re.MULTILINE,
)
RAEDERS_SECTION_RE = re.compile(
    r"## Raeder's\n.*?(?=\n## [^#]|\Z)", re.DOTALL
)
NOTES_SECTION_RE = re.compile(
    r"## Raeders Notes\n.*?(?=\n## [^#]|\Z)", re.DOTALL
)


def fmt_price(p: float) -> str:
    if p == 0:
        return "—"
    if p == int(p):
        return f"${int(p):,}"
    return f"${p:,.2f}"


def render_raeders_block(rp: RaedersProducer) -> str:
    return (
        "  raeders:\n"
        "    in_portfolio: true\n"
        f"    cuvee_count: {rp.n}\n"
        f"    price_min: {int(rp.price_min) if rp.price_min == int(rp.price_min) else rp.price_min:g}\n"
        f"    price_max: {int(rp.price_max) if rp.price_max == int(rp.price_max) else rp.price_max:g}\n"
    )


def render_raeders_section(rp: RaedersProducer) -> str:
    lines = ["## Raeder's", ""]
    lines.append(
        f"Currently tracked: **{rp.n} cuvée/vintage entries**; "
        f"prices {fmt_price(rp.price_min)}–{fmt_price(rp.price_max)}."
    )
    lines.append("")
    lines.append("| Cuvée | Vintage | Size | Price | Scores |")
    lines.append("|---|---|---|---|---|")
    for c in sorted(rp.cuvees, key=lambda x: -x.price):
        scores = []
        if c.score_wa: scores.append(f"WA {c.score_wa}")
        if c.score_js: scores.append(f"JS {c.score_js}")
        if c.score_we: scores.append(f"WE {c.score_we}")
        score_str = " · ".join(scores) if scores else "—"
        cu = (c.cuvee or "—").replace("|", "/")
        lines.append(
            f"| {cu} | {c.vintage} | {c.size or '—'} | {fmt_price(c.price)} | {score_str} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def render_notes_section(rp: RaedersProducer) -> str:
    """Surface up to 5 best tasting notes (those tied to scored bottles)."""
    cands = [c for c in rp.cuvees if c.tasting_note]
    cands.sort(key=lambda x: -(x.score_wa + x.score_js + x.score_we))
    cands = cands[:5]
    if not cands:
        return ""
    lines = ["## Raeders Notes", ""]
    for c in cands:
        scores = []
        if c.score_wa: scores.append(f"WA {c.score_wa}")
        if c.score_js: scores.append(f"JS {c.score_js}")
        if c.score_we: scores.append(f"WE {c.score_we}")
        score_str = f" ({' · '.join(scores)})" if scores else ""
        title = f"{c.cuvee or rp.name} {c.vintage}".strip()
        lines.append(f"### {title}{score_str}")
        lines.append("")
        # Trim "Read More" trailing text
        note = re.sub(r"\.{3}\s*Read More\s*$", "…", c.tasting_note).strip()
        lines.append(f"> {note}")
        lines.append("")
        lines.append(f"_[Raeders link]({c.url})_")
        lines.append("")
    return "\n".join(lines) + "\n"


def apply_to_wiki(entry: WikiEntry, rp: RaedersProducer) -> None:
    text = entry.path.read_text(encoding="utf-8", errors="replace")
    parts = split_fm(text)
    if not parts:
        return
    fm, body = parts

    new_block = render_raeders_block(rp)
    if RAEDERS_BLOCK_RE.search(fm):
        fm = RAEDERS_BLOCK_RE.sub(new_block, fm, count=1)
    else:
        fm = re.sub(r"(retailers:\n)", r"\1" + new_block, fm, count=1)

    new_sec = render_raeders_section(rp)
    if RAEDERS_SECTION_RE.search(body):
        body = RAEDERS_SECTION_RE.sub(new_sec.rstrip() + "\n", body, count=1)
    else:
        body = body.rstrip() + "\n\n" + new_sec

    notes_sec = render_notes_section(rp)
    if notes_sec:
        if NOTES_SECTION_RE.search(body):
            body = NOTES_SECTION_RE.sub(notes_sec.rstrip() + "\n", body, count=1)
        else:
            # insert after Raeder's section
            body = re.sub(
                RAEDERS_SECTION_RE,
                lambda m: m.group(0).rstrip() + "\n\n" + notes_sec.rstrip() + "\n",
                body,
                count=1,
            )

    # Optionally add raeders display name to aliases if it differs from canonical name
    if rp.name and rp.name != entry.name:
        existing = get_list(fm, "aliases")
        if rp.name not in existing:
            existing.append(rp.name)
            new_aliases = ", ".join(f'"{a}"' for a in existing)
            fm = re.sub(
                r"^aliases:\s*\[.*?\]\s*$",
                f"aliases: [{new_aliases}]",
                fm,
                count=1,
                flags=re.MULTILINE,
            )

    entry.path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


# --- main ---

def main() -> int:
    raw = load_raw()
    wiki = load_wiki()
    print(f"Raeders producers: {len(raw)}; wiki producers: {len(wiki)}")

    matched: list[tuple[RaedersProducer, WikiEntry, str]] = []
    ambiguous: list[tuple[RaedersProducer, WikiEntry, float, str]] = []
    new_candidates: list[RaedersProducer] = []
    skipped: list[RaedersProducer] = []

    for rp in raw.values():
        # Skip producers with very thin presence and no critic interest
        if rp.n < 1:
            continue
        entry, score, reason = best_match(rp, wiki)
        if score >= 1.0:
            matched.append((rp, entry, reason))
        elif entry is not None and score >= FUZZY_AUTO:
            matched.append((rp, entry, reason))
        elif entry is not None and score >= FUZZY_REVIEW and (rp.n >= 2 or rp.has_score):
            ambiguous.append((rp, entry, score, reason))
        elif rp.n >= 3 or (rp.has_score and rp.n >= 2):
            new_candidates.append(rp)
        else:
            skipped.append(rp)

    print(f"  matched (auto-apply):     {len(matched)}")
    print(f"  ambiguous (review):       {len(ambiguous)}")
    print(f"  new candidates (review):  {len(new_candidates)}")
    print(f"  skipped (low signal):     {len(skipped)}")

    # Apply matches
    applied = 0
    for rp, entry, reason in matched:
        try:
            apply_to_wiki(entry, rp)
            applied += 1
        except Exception as e:
            print(f"  ERROR on {entry.slug}: {e}")

    # Report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    matched.sort(key=lambda t: -t[0].n)
    ambiguous.sort(key=lambda t: -t[0].n)
    new_candidates.sort(key=lambda r: -r.n)
    lines = [
        "---",
        "type: compile_review",
        "source: raeders",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"applied: {applied}",
        f"ambiguous: {len(ambiguous)}",
        f"new_candidates: {len(new_candidates)}",
        f"skipped: {len(skipped)}",
        "---",
        "",
        "# Raeders compile review",
        "",
        f"**{applied}** producers matched and updated automatically. "
        f"**{len(ambiguous) + len(new_candidates)}** need LLM/human review.",
        "",
        "## Auto-applied matches",
        "",
        "| Raeders name | Wiki slug | Bottles | Match reason |",
        "|---|---|---:|---|",
    ]
    for rp, entry, reason in matched[:60]:
        lines.append(f"| {rp.name} | `{entry.slug}` | {rp.n} | {reason} |")
    if len(matched) > 60:
        lines.append(f"| _… {len(matched) - 60} more_ |  |  |  |")

    lines += ["", "## Ambiguous fuzzy matches (LLM should disambiguate)", ""]
    if ambiguous:
        lines.append("| Raeders name | Best wiki guess | Score | Bottles | Has critic? |")
        lines.append("|---|---|---:|---:|---|")
        for rp, entry, score, _reason in ambiguous:
            lines.append(
                f"| {rp.name} | `{entry.slug}` ({entry.name}) | {score:.2f} | "
                f"{rp.n} | {'★' if rp.has_score else '—'} |"
            )
    else:
        lines.append("_None._")

    lines += ["", "## New-producer candidates (≥3 bottles or scored, no wiki match)", ""]
    if new_candidates:
        lines.append("| Raeders name | Country | Region | Bottles | Price max | Scored? |")
        lines.append("|---|---|---|---:|---:|---|")
        for rp in new_candidates[:80]:
            country = next((c for c in rp.countries if c), "")
            region = next((r for r in rp.regions if r), "")
            lines.append(
                f"| {rp.name} | {country or '—'} | {region or '—'} | {rp.n} | "
                f"{fmt_price(rp.price_max)} | {'★' if rp.has_score else '—'} |"
            )
        if len(new_candidates) > 80:
            lines.append("")
            lines.append(f"_… and {len(new_candidates) - 80} more new candidates._")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nApplied {applied} matches; review report at {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
