"""
Read raw/raeders/raeders_inventory_<date>.csv, group rows by producer_guess,
and fold matching producers into wiki/producers/*.md.

For each producer slug matched against an existing wiki page:
  - Update `retailers.raeders.{in_portfolio,cuvee_count,price_min,price_max}`
  - Replace the `## Raeder's` section body with a cuvée table.

Producers with no existing wiki entry are listed in the report but not created
(Raeder's inventory is 40% classed-growth Bordeaux/Burgundy that's out of scope
for the terroir-driven wiki).

Report: build/raeders_ingest_report.md
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT / "raw" / "raeders"
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "raeders_ingest_report.md"


def canonical_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def latest_inventory_csv() -> Path:
    candidates = sorted(RAW_DIR.glob("raeders_inventory_*.csv"))
    if not candidates:
        raise SystemExit(f"No raeders_inventory_*.csv in {RAW_DIR}")
    return candidates[-1]


@dataclass
class Cuvee:
    name: str
    vintage: str
    fmt: str
    price_usd: float


@dataclass
class ProducerAgg:
    producer_guess: str
    cuvees: list[Cuvee] = field(default_factory=list)

    @property
    def slug_guess(self) -> str:
        return canonical_slug(self.producer_guess)

    @property
    def cuvee_count(self) -> int:
        return len(self.cuvees)

    @property
    def price_min(self) -> float:
        prices = [c.price_usd for c in self.cuvees if c.price_usd > 0]
        return min(prices) if prices else 0.0

    @property
    def price_max(self) -> float:
        prices = [c.price_usd for c in self.cuvees if c.price_usd > 0]
        return max(prices) if prices else 0.0


def load_inventory(csv_path: Path) -> dict[str, ProducerAgg]:
    agg: dict[str, ProducerAgg] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            pg = (row.get("producer_guess") or "").strip()
            if not pg:
                continue
            slug = canonical_slug(pg)
            if slug not in agg:
                agg[slug] = ProducerAgg(producer_guess=pg)
            try:
                price = float(row.get("price_usd") or 0)
            except ValueError:
                price = 0.0
            cuvee_name = (row.get("Name") or "").strip()
            # Strip redundant producer prefix from cuvée name when present
            if cuvee_name.lower().startswith(pg.lower() + " - "):
                cuvee_name = cuvee_name[len(pg) + 3:]
            elif cuvee_name.lower().startswith(pg.lower() + " "):
                cuvee_name = cuvee_name[len(pg) + 1:]
            agg[slug].cuvees.append(Cuvee(
                name=cuvee_name or pg,
                vintage=(row.get("Vintage") or "").strip(),
                fmt=(row.get("Format") or "").strip(),
                price_usd=price,
            ))
    return agg


# --- frontmatter helpers (shared style with ingest_csw.py) ---

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_fm_field(fm: str, key: str) -> str | None:
    m = re.search(rf'^{re.escape(key)}:\s*"?(.*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1) if m else None


def update_raeders_block(
    fm: str,
    in_portfolio: bool,
    cuvee_count: int,
    price_min: float,
    price_max: float,
) -> str:
    """Replace the raeders: block with fully populated 4-key form."""
    replacement = (
        "  raeders:\n"
        f"    in_portfolio: {'true' if in_portfolio else 'false'}\n"
        f"    cuvee_count: {cuvee_count}\n"
        f"    price_min: {int(price_min) if price_min == int(price_min) else price_min}\n"
        f"    price_max: {int(price_max) if price_max == int(price_max) else price_max}\n"
    )
    # Match the existing raeders block (any number of 4-space indented lines)
    pattern = re.compile(
        r"^  raeders:\n(?:    [^\n]*\n)+",
        re.MULTILINE,
    )
    if pattern.search(fm):
        return pattern.sub(replacement, fm, count=1)
    return fm


def render_raeders_section(agg: ProducerAgg) -> str:
    lines = ["## Raeder's", ""]
    def fmt_price(p: float) -> str:
        return f"${int(p):,}" if p == int(p) else f"${p:,.2f}"
    if not agg.cuvees:
        lines.append("_Not yet populated._")
        return "\n".join(lines) + "\n\n"
    lines.append(
        f"Currently tracked: **{agg.cuvee_count} cuvée/vintage entries**; "
        f"prices {fmt_price(agg.price_min)}–{fmt_price(agg.price_max)}."
    )
    lines.append("")
    lines.append("| Cuvée | Vintage | Format | Price |")
    lines.append("|---|---|---|---|")
    for c in sorted(agg.cuvees, key=lambda c: -c.price_usd):
        name = c.name.replace("|", "/")
        lines.append(f"| {name} | {c.vintage or '—'} | {c.fmt or '—'} | {fmt_price(c.price_usd)} |")
    lines.append("")
    return "\n".join(lines) + "\n"


RAEDERS_SECTION_RE = re.compile(
    r"## Raeder's\n.*?(?=\n## [^#]|\Z)", re.DOTALL
)


def replace_raeders_section(body: str, new_section: str) -> str:
    if RAEDERS_SECTION_RE.search(body):
        return RAEDERS_SECTION_RE.sub(new_section.rstrip() + "\n", body, count=1)
    return body.rstrip() + "\n\n" + new_section


def process():
    csv_path = latest_inventory_csv()
    print(f"Reading {csv_path.name}...")
    agg = load_inventory(csv_path)
    print(f"Parsed {sum(a.cuvee_count for a in agg.values())} bottles across "
          f"{len(agg)} producers")

    matched: list[str] = []
    not_in_wiki: list[tuple[str, ProducerAgg]] = []

    for slug, a in agg.items():
        wiki_path = PRODUCERS / f"{slug}.md"
        if not wiki_path.exists():
            not_in_wiki.append((slug, a))
            continue
        text = wiki_path.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, body = parts
        if get_fm_field(fm, "type") != "producer":
            continue
        new_fm = update_raeders_block(fm, True, a.cuvee_count, a.price_min, a.price_max)
        new_body = replace_raeders_section(body, render_raeders_section(a))
        wiki_path.write_text(f"---\n{new_fm}\n---\n{new_body}", encoding="utf-8")
        matched.append(slug)

    # Report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    not_in_wiki.sort(key=lambda t: -t[1].cuvee_count)
    lines = [
        "---",
        "type: ingest_report",
        "source: raeders_csv",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"source_file: {csv_path.name}",
        f"total_bottles: {sum(a.cuvee_count for a in agg.values())}",
        f"total_raeders_producers: {len(agg)}",
        f"matched_existing_wiki: {len(matched)}",
        f"not_in_wiki: {len(not_in_wiki)}",
        "---",
        "",
        "# Raeder's ingest report",
        "",
        f"Loaded **{sum(a.cuvee_count for a in agg.values())}** bottles across "
        f"**{len(agg)}** distinct producers from `{csv_path.name}`.",
        f"Updated **{len(matched)}** existing wiki entries with Raeder's sections.",
        "",
        f"## Not in wiki ({len(not_in_wiki)})",
        "",
        "Raeder's inventory is heavy on Bordeaux classed-growths + Burgundy classicos "
        "that aren't in the terroir-driven seed list. Top 40 by cuvée count:",
        "",
        "| Producer | Slug (guess) | Cuvées | Max price |",
        "|---|---|---:|---:|",
    ]
    for slug, a in not_in_wiki[:40]:
        lines.append(
            f"| {a.producer_guess} | `{slug}` | {a.cuvee_count} | ${a.price_max:,.0f} |"
        )
    if len(not_in_wiki) > 40:
        lines.append(f"")
        lines.append(f"_… and {len(not_in_wiki) - 40} more_")

    if matched:
        lines += ["", f"## Matched wiki producers ({len(matched)})", ""]
        for slug in sorted(matched):
            lines.append(f"- `{slug}`")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nMatched {len(matched)} wiki producers, skipped {len(not_in_wiki)}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    process()
