"""
Parse fass_db.jsx (FASS Selections portfolio) — same SD shape as DTE —
and update `retailers.fass` + `## FASS` on matching existing producer pages.

Unlike DTE, we DO NOT create new pages for FASS producers. Their portfolio
has heavy spelling variation ("Achim", "Achim Duerr", "Achim Durr", ...) and
creating one wiki entry per variant would pollute the wiki. Unmatched FASS
producers are logged to build/fass_ingest_report.md for later alias curation.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
JSX_PATH = Path(r"C:/Users/Evan Karp/Downloads/fass_db.jsx")
WIKI_DIR = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "fass_ingest_report.md"

# Explicit aliases for FASS producer names → wiki slug. Extend as mismatches
# surface in the report.
FASS_ALIASES: dict[str, str] = {
    "baudry": "bernard_baudry",
    "bernard baudry": "bernard_baudry",
    "matthieu baudry": "matthieu_baudry",
    # --- 2026-07-22 batch: 12 onboarded from the triage + Gmail offers ---
    "jean michel stephan": "jean_michel_stephan",
    "jean-michel stephan": "jean_michel_stephan",
    "domaine blachon": "domaine_blachon",
    "cave sebastien blachon": "domaine_blachon",
    "philippe naddef": "philippe_naddef",
    "domaine philippe naddef": "philippe_naddef",
    "michel naddef": "philippe_naddef",
    "perseval farge": "perseval_farge",
    "perseval-farge": "perseval_farge",
    "paul weltner": "paul_weltner",
    "leclapart": "david_leclapart",
    "david leclapart": "david_leclapart",
    "jj prum": "joh_jos_prum",
    "j.j. prum": "joh_jos_prum",
    "markus molitor": "markus_molitor",
    "markus moitor": "markus_molitor",
    "martin muellen": "martin_muellen",
    "martin mullen": "martin_muellen",
    "domaine des roches neuves": "domaine_des_roches_neuves",
    "thierry germain": "domaine_des_roches_neuves",
    "yvon metras": "yvon_metras",
    "gut hermannsberg": "gut_hermannsberg",
    # --- cross-source consolidation: already covered under other slugs ---
    "gonon": "domaine_pierre_gonon",
    "pierre gonon": "domaine_pierre_gonon",
    "pierre brisset": "maison_pierre_brisset",
    "maison brisset": "maison_pierre_brisset",
    "jj girard": "jean_jacques_girard",   # = DTE "Jean-Jacques Girard" (Savigny)
    "j.j. girard": "jean_jacques_girard",
}


def canonical_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def extract_sd(jsx_text: str) -> dict:
    """Pull the first JSON object from `const SEED_RAW = {...};` or similar."""
    for pattern in (
        r"const\s+SEED_RAW\s*=\s*(\{.*?\})\s*;",
        r"const\s+SD\s*=\s*(\{.*?\})\s*;",
    ):
        m = re.search(pattern, jsx_text, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    raise ValueError("SD/SEED_RAW object not found in JSX")


@dataclass
class ProducerAgg:
    name: str
    slug_guess: str
    country: str
    region: str
    cuvees: list[tuple[str, str, float]] = field(default_factory=list)

    @property
    def cuvee_count(self) -> int:
        return len(self.cuvees)

    @property
    def price_min(self) -> float:
        prices = [p for _, _, p in self.cuvees if p > 0]
        return min(prices) if prices else 0.0

    @property
    def price_max(self) -> float:
        prices = [p for _, _, p in self.cuvees if p > 0]
        return max(prices) if prices else 0.0


def aggregate(sd: dict) -> dict[str, ProducerAgg]:
    P, C, R, D = sd["P"], sd["C"], sd["R"], sd["D"]
    by_slug: dict[str, ProducerAgg] = {}
    for row in D:
        if len(row) < 6:
            continue
        p_idx, wine_name, vintage, c_idx, r_idx, price = row[:6]
        if not (isinstance(p_idx, int) and 0 <= p_idx < len(P)):
            continue
        name = P[p_idx]
        country = C[c_idx] if isinstance(c_idx, int) and 0 <= c_idx < len(C) else ""
        region = R[r_idx] if isinstance(r_idx, int) and 0 <= r_idx < len(R) else ""
        slug = FASS_ALIASES.get(name.lower(), canonical_slug(name))
        if slug not in by_slug:
            by_slug[slug] = ProducerAgg(name=name, slug_guess=slug,
                                         country=country, region=region)
        if not by_slug[slug].country and country:
            by_slug[slug].country = country
        if not by_slug[slug].region and region:
            by_slug[slug].region = region
        try:
            pf = float(price or 0)
        except (TypeError, ValueError):
            pf = 0.0
        by_slug[slug].cuvees.append((
            str(wine_name or ""),
            str(vintage) if vintage else "",
            pf,
        ))
    return by_slug


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
FASS_BLOCK_IN_FM_RE = re.compile(r"(  fass:\n(?:    [^\n]+\n)+)")
FASS_SECTION_RE = re.compile(r"## FASS\n(.*?)(?=\n## [^#]|\Z)", re.DOTALL)


def build_fass_fm_block(agg: ProducerAgg) -> str:
    return ("  fass:\n"
            "    in_portfolio: true\n"
            f"    cuvee_count: {agg.cuvee_count}\n"
            f"    price_min: {int(agg.price_min)}\n"
            f"    price_max: {int(agg.price_max)}\n")


def build_fass_section(agg: ProducerAgg) -> str:
    lines = ["## FASS", ""]
    sorted_cuvees = sorted(agg.cuvees, key=lambda x: (x[0].lower(), x[1] or "0"))
    lines.append(
        f"Currently tracked: **{agg.cuvee_count} cuvée/vintage entries**; "
        f"prices ${agg.price_min:.0f}–${agg.price_max:.0f}."
    )
    lines.append("")
    lines.append("| Cuvée | Vintage | Price |")
    lines.append("|---|---|---|")
    for wine, v, price in sorted_cuvees[:40]:  # cap at 40 rows to avoid bloat
        p_display = f"${price:.0f}" if price else "—"
        lines.append(f"| {wine or '—'} | {v or 'NV'} | {p_display} |")
    if len(sorted_cuvees) > 40:
        lines.append(f"| _… {len(sorted_cuvees) - 40} more entries_ | | |")
    lines.append("")
    return "\n".join(lines)


def update_existing(path: Path, agg: ProducerAgg) -> None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return
    fm, body = m.group(1), m.group(2)
    new_block = build_fass_fm_block(agg)
    if FASS_BLOCK_IN_FM_RE.search(fm):
        fm = FASS_BLOCK_IN_FM_RE.sub(new_block, fm, count=1)
    else:
        fm = re.sub(r"(retailers:\n)", r"\1" + new_block, fm, count=1)
    new_section = build_fass_section(agg)
    if FASS_SECTION_RE.search(body):
        body = FASS_SECTION_RE.sub(new_section + "\n", body, count=1)
    else:
        body = body.rstrip() + "\n\n" + new_section + "\n"
    path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


def main() -> int:
    if not JSX_PATH.exists():
        print(f"JSX not found: {JSX_PATH}", file=sys.stderr)
        return 1
    text = JSX_PATH.read_text(encoding="utf-8")
    sd = extract_sd(text)
    print(f"Parsed SEED_RAW: {len(sd['P'])} producers, {len(sd['D'])} wine entries")

    by_slug = aggregate(sd)
    print(f"Aggregated into {len(by_slug)} distinct producer slugs")

    matched: list[tuple[str, ProducerAgg]] = []
    unmatched: list[tuple[str, ProducerAgg]] = []

    for slug, agg in sorted(by_slug.items()):
        if not slug:
            continue
        path = WIKI_DIR / f"{slug}.md"
        if path.exists():
            try:
                update_existing(path, agg)
                matched.append((slug, agg))
            except Exception as e:
                print(f"  ERROR on {slug}: {e}", file=sys.stderr)
                unmatched.append((slug, agg))
        else:
            unmatched.append((slug, agg))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    unmatched.sort(key=lambda t: -t[1].cuvee_count)

    lines = [
        "---",
        "type: ingest_report",
        "source: fass_jsx",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_fass_producers: {len(by_slug)}",
        f"matched_existing: {len(matched)}",
        f"unmatched: {len(unmatched)}",
        "---",
        "",
        "# FASS ingest report",
        "",
        f"Parsed `{JSX_PATH.name}` — {len(sd['P'])} producers, {len(sd['D'])} wines.",
        f"Matched **{len(matched)}** existing wiki producers.",
        f"**{len(unmatched)}** FASS producers had no matching slug in wiki/producers/.",
        "",
        "Unmatched producers are NOT auto-created — spelling variations would pollute "
        "the wiki. Add entries to `FASS_ALIASES` in this script when you find a clear "
        "mapping to an existing wiki slug.",
        "",
        f"## Matched ({len(matched)})",
        "",
    ]
    for slug, a in matched:
        lines.append(f"- `{slug}` — {a.name} ({a.cuvee_count} cuvées, ${a.price_min:.0f}–${a.price_max:.0f})")
    lines += [
        "",
        f"## Top 60 unmatched by cuvée count",
        "",
        "| Name | Guess slug | Country | Region | Cuvées | Max $ |",
        "|---|---|---|---|---:|---:|",
    ]
    for slug, a in unmatched[:60]:
        lines.append(
            f"| {a.name} | `{slug}` | {a.country} | {a.region} | "
            f"{a.cuvee_count} | ${a.price_max:.0f} |"
        )
    if len(unmatched) > 60:
        lines.append(f"")
        lines.append(f"_… and {len(unmatched) - 60} more_")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nMatched {len(matched)}, unmatched {len(unmatched)}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
