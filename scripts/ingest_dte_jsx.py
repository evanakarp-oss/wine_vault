"""
Parse dte_wines_1.jsx (Down to Earth / Robert Panzer portfolio) and fold it into
wiki/producers/ as a retailer dimension.

The JSX file encodes wines as a compact SD object:
    const SD = {"P":[producer names...],
                "C":[countries...],
                "R":[regions...],
                "D":[[p_idx, wine_name, vintage, c_idx, r_idx, price], ...]};

For each producer with SD entries:
  - if wiki/producers/<slug>.md exists: update retailers.dte frontmatter fields
    (in_portfolio=true, cuvee_count, price_min, price_max) and replace the
    "## Down to Earth Wines (Panzer)" section body with the cuvee list.
  - if no wiki file exists yet: create a minimal one with DTE as primary source.

A summary report lands in build/dte_ingest_report.md showing: matched vs new,
slug mismatches that needed aliasing, and any producers missing from the wiki.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
JSX_PATH = Path(r"C:/Users/Evan Karp/Downloads/dte_wines_1.jsx")
WIKI_DIR = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "dte_ingest_report.md"

# Explicit aliases for DTE producer names → wiki slug (when normalization alone wouldn't match).
# Extend as we discover mismatches. Lowercase keys.
DTE_ALIASES: dict[str, str] = {
    "baudry": "domaine_baudry",
    "bernard baudry": "domaine_baudry",
    # Add more as needed after report.
}


def extract_sd(jsx_text: str) -> dict:
    """Pull the JSON object from `const SD = {...};`."""
    m = re.search(r"const\s+SD\s*=\s*(\{.*?\})\s*;", jsx_text, re.DOTALL)
    if not m:
        raise ValueError("SD object not found in JSX")
    return json.loads(m.group(1))


def canonical_slug(name: str) -> str:
    """Map producer display name to wiki filename stem (lowercase snake_case).
    Strip accents → ascii; collapse whitespace/punctuation to underscores.
    """
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", " ", name)
    name = re.sub(r"[\s-]+", "_", name).strip("_")
    return name


@dataclass
class ProducerAgg:
    name: str
    slug_guess: str
    country: str
    region: str
    cuvees: list[tuple[str, str, float]]  # (wine_name, vintage, price)

    @property
    def cuvee_count(self) -> int:
        return len(self.cuvees)

    @property
    def price_min(self) -> float:
        prices = [p for _, _, p in self.cuvees if p and p > 0]
        return min(prices) if prices else 0.0

    @property
    def price_max(self) -> float:
        prices = [p for _, _, p in self.cuvees if p and p > 0]
        return max(prices) if prices else 0.0


def aggregate(sd: dict) -> dict[str, ProducerAgg]:
    P, C, R, D = sd["P"], sd["C"], sd["R"], sd["D"]
    by_slug: dict[str, ProducerAgg] = {}

    for row in D:
        # Some rows in the observed data have 6 fields: [p_idx, wine_name, vintage, c_idx, r_idx, price]
        p_idx, wine_name, vintage, c_idx, r_idx, price = row[:6]
        name = P[p_idx] if 0 <= p_idx < len(P) else ""
        country = C[c_idx] if 0 <= c_idx < len(C) else ""
        region = R[r_idx] if 0 <= r_idx < len(R) else ""

        slug = DTE_ALIASES.get(name.lower(), canonical_slug(name))
        if slug not in by_slug:
            by_slug[slug] = ProducerAgg(name=name, slug_guess=slug, country=country,
                                         region=region, cuvees=[])
        # Prefer non-empty country/region if first-seen was empty
        if not by_slug[slug].country and country:
            by_slug[slug].country = country
        if not by_slug[slug].region and region:
            by_slug[slug].region = region
        by_slug[slug].cuvees.append((wine_name, str(vintage) if vintage else "", float(price or 0)))

    return by_slug


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
DTE_BLOCK_IN_FM_RE = re.compile(r"(  dte:\n(?:    [^\n]+\n)+)")
DTE_SECTION_RE = re.compile(r"## Down to Earth Wines \(Panzer\)\n(.*?)(?=\n## |\Z)", re.DOTALL)


def build_dte_section(agg: ProducerAgg) -> str:
    lines = ["## Down to Earth Wines (Panzer)", ""]
    # Sort cuvées: oldest vintage first within each cuvée name, cuvées alphabetical
    sorted_cuvees = sorted(agg.cuvees, key=lambda x: (x[0].lower(), x[1] or "0"))
    lines.append(f"Currently tracked: **{agg.cuvee_count} cuvée/vintage entries**; "
                 f"prices ${agg.price_min:.0f}–${agg.price_max:.0f}.")
    lines.append("")
    lines.append("| Cuvée | Vintage | Price |")
    lines.append("|---|---|---|")
    for wine, v, price in sorted_cuvees:
        p_display = f"${price:.0f}" if price else "—"
        lines.append(f"| {wine} | {v or 'NV'} | {p_display} |")
    lines.append("")
    return "\n".join(lines)


def build_dte_fm_block(agg: ProducerAgg) -> str:
    return ("  dte:\n"
            f"    in_portfolio: true\n"
            f"    cuvee_count: {agg.cuvee_count}\n"
            f"    price_min: {int(agg.price_min)}\n"
            f"    price_max: {int(agg.price_max)}\n")


def update_existing(path: Path, agg: ProducerAgg) -> None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise RuntimeError(f"No YAML frontmatter in {path.name}")
    fm, body = m.group(1), m.group(2)

    new_fm_block = build_dte_fm_block(agg)
    if DTE_BLOCK_IN_FM_RE.search(fm):
        fm = DTE_BLOCK_IN_FM_RE.sub(new_fm_block, fm, count=1)
    else:
        # Insert dte block right after `retailers:` header
        fm = re.sub(r"(retailers:\n)", r"\1" + new_fm_block, fm, count=1)

    new_section = build_dte_section(agg)
    if DTE_SECTION_RE.search(body):
        body = DTE_SECTION_RE.sub(new_section + "\n", body, count=1)
    else:
        # Append at end of body
        body = body.rstrip() + "\n\n" + new_section + "\n"

    path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


def create_new(slug: str, agg: ProducerAgg) -> Path:
    """Emit a minimal producer .md file seeded entirely from DTE."""
    path = WIKI_DIR / f"{slug}.md"
    lines = [
        "---",
        "type: producer",
        f'name: "{agg.name}"',
        f"slug: {slug}",
        "aliases: []",
        f'country: "{agg.country}"',
        f'region: "{agg.region}"',
        'sub_region: ""',
        "appellations: []",
        "farming: []",
        "certifications: []",
        "importer_us: []",
        "retailers:",
        "  chambers:",
        "    championed: false",
        "    article_count: 0",
        "    dedicated_count: 0",
        "    first_year: 0",
        "    last_year: 0",
        "  dte:",
        "    in_portfolio: true",
        f"    cuvee_count: {agg.cuvee_count}",
        f"    price_min: {int(agg.price_min)}",
        f"    price_max: {int(agg.price_max)}",
        "  raeders:",
        "    in_portfolio: false",
        "  fass:",
        "    in_portfolio: false",
        "tags: []",
        f'_sources: ["dte_jsx:{JSX_PATH.name}"]',
        "---",
        "",
        f"# {agg.name}",
        "",
        "_Seeded from Down to Earth (Panzer) portfolio. Not yet covered in CSW archive sweep._",
        "",
        "## CSW Write-ups",
        "",
        "_No Chambers Street write-ups on file._",
        "",
        build_dte_section(agg),
        "## Raeder's",
        "",
        "_Not yet populated._",
        "",
        "## FASS",
        "",
        "_Not yet populated._",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    if not JSX_PATH.exists():
        print(f"JSX not found: {JSX_PATH}", file=sys.stderr)
        return 1
    if not WIKI_DIR.exists():
        WIKI_DIR.mkdir(parents=True, exist_ok=True)

    text = JSX_PATH.read_text(encoding="utf-8")
    sd = extract_sd(text)
    print(f"Parsed SD: {len(sd['P'])} producers, {len(sd['D'])} wine entries, "
          f"{len(sd['C'])} countries, {len(sd['R'])} regions")

    by_slug = aggregate(sd)
    print(f"Aggregated into {len(by_slug)} distinct producers")

    matched, created, skipped_empty = [], [], []
    for slug, agg in sorted(by_slug.items()):
        if not slug:
            skipped_empty.append(agg.name)
            continue
        path = WIKI_DIR / f"{slug}.md"
        if path.exists():
            try:
                update_existing(path, agg)
                matched.append((slug, agg))
            except Exception as e:
                print(f"  ERROR updating {slug}: {e}", file=sys.stderr)
                skipped_empty.append(agg.name)
        else:
            create_new(slug, agg)
            created.append((slug, agg))

    # Report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report_lines = [
        "---",
        "type: ingest_report",
        "source: dte_jsx",
        f"generated: \"{datetime.now().isoformat(timespec='seconds')}\"",
        f"total_producers: {len(by_slug)}",
        f"matched_existing: {len(matched)}",
        f"created_new: {len(created)}",
        f"skipped: {len(skipped_empty)}",
        "---",
        "",
        "# DTE ingest report",
        "",
        f"Parsed `{JSX_PATH.name}` — {len(sd['P'])} producers, {len(sd['D'])} wine entries.",
        "",
        f"## Matched existing wiki entries ({len(matched)})",
        "",
    ]
    for slug, a in matched:
        report_lines.append(f"- `{slug}` — {a.name} ({a.cuvee_count} cuvées, ${a.price_min:.0f}–${a.price_max:.0f})")
    report_lines.append("")
    report_lines.append(f"## Created new entries ({len(created)})")
    report_lines.append("")
    report_lines.append("These DTE producers had no pre-existing wiki entry — they may be out of scope for Chambers Street.")
    report_lines.append("")
    for slug, a in created:
        report_lines.append(f"- `{slug}` — {a.name} ({a.country}, {a.region}; {a.cuvee_count} cuvées, ${a.price_min:.0f}–${a.price_max:.0f})")
    if skipped_empty:
        report_lines.append("")
        report_lines.append(f"## Skipped ({len(skipped_empty)})")
        report_lines.append("")
        for n in skipped_empty:
            report_lines.append(f"- {n!r}")

    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\nOK: {len(matched)} matched, {len(created)} new, {len(skipped_empty)} skipped")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
