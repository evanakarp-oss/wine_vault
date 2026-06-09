"""
Read wiki/My Cellar.csv (CellarTracker export, cp1252-encoded) and emit one
markdown file per cuvée-vintage into cellar/. Also populate the `## Cellar`
section on matching producer pages.

CSV columns (CellarTracker):
  Color, Category, Size, Currency, Value, Price, TotalQuantity, Quantity,
  Pending, Vintage, Wine, Locale, Producer, Varietal, BeginConsume,
  EndConsume, PScore, CScore

Output filename: cellar/{vintage}_{producer_slug}_{cuvee_slug}.md

Sentinel values:
  Vintage / BeginConsume / EndConsume: 1001 → NV; 9999 → unknown; 0 → unknown.

Producer slugs derived from CT names are remapped to canonical wiki slugs
via link_cellar.SLUG_OVERRIDES. After re-ingesting, run
`python scripts/link_cellar.py` to restore cellar↔producer wikilinks
(this script regenerates cellar bodies without them).
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from link_cellar import SLUG_OVERRIDES

VAULT = Path(__file__).resolve().parent.parent
SRC_CSV = VAULT / "wiki" / "My Cellar.csv"
CELLAR_DIR = VAULT / "cellar"
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "cellar_ingest_report.md"


def canonical_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return SLUG_OVERRIDES.get(s, s)


def cuvee_slug(wine: str, producer: str, vintage: str) -> str:
    """Derive a short cuvée slug from Wine, stripping producer prefix and vintage."""
    name = wine
    # Strip leading producer if present
    if name.lower().startswith(producer.lower()):
        name = name[len(producer):].lstrip(" -")
    # Strip leading year
    name = re.sub(r"^\d{4}\s+", "", name)
    return canonical_slug(name) or "cuvee"


def parse_year(s: str) -> int | None:
    try:
        v = int(s)
    except (TypeError, ValueError):
        return None
    if v in (0, 1001, 9999):
        return None
    return v


def render_vintage(s: str) -> str:
    y = parse_year(s)
    if y is None:
        return "NV"
    return str(y)


def money(s: str) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


@dataclass
class Bottle:
    producer: str
    producer_slug: str
    wine: str
    cuvee_display: str
    cuvee_slug: str
    vintage_display: str  # "2012" or "NV"
    size: str
    quantity: int
    value_usd: float        # CellarTracker current value estimate
    price_usd: float        # purchase price
    country: str
    region: str
    varietal: str
    drink_start: int | None
    drink_end: int | None
    color: str
    category: str

    @property
    def filename(self) -> str:
        return f"{self.vintage_display}_{self.producer_slug}_{self.cuvee_slug}.md"


def parse_locale(locale: str) -> tuple[str, str]:
    """'France, Champagne' -> ('France', 'Champagne'). Drop deeper path."""
    parts = [p.strip() for p in locale.split(",") if p.strip()]
    country = parts[0] if parts else ""
    region = parts[1] if len(parts) > 1 else ""
    return country, region


def load_bottles() -> list[Bottle]:
    with SRC_CSV.open(encoding="cp1252", newline="") as f:
        reader = csv.DictReader(f)
        bottles = []
        for row in reader:
            producer = (row.get("Producer") or "").strip()
            wine = (row.get("Wine") or "").strip()
            if not producer and not wine:
                continue
            p_slug = canonical_slug(producer) if producer else canonical_slug(wine)
            vintage = render_vintage(row.get("Vintage") or "")
            c_slug = cuvee_slug(wine, producer, vintage)
            country, region = parse_locale(row.get("Locale") or "")
            try:
                qty = int(row.get("TotalQuantity") or row.get("Quantity") or 0)
            except ValueError:
                qty = 0
            # Strip producer prefix and trailing vintage from displayed cuvée
            disp = wine
            if disp.lower().startswith(producer.lower()):
                disp = disp[len(producer):].lstrip(" -")
            disp = re.sub(r"^\d{4}\s+", "", disp).strip()
            bottles.append(Bottle(
                producer=producer,
                producer_slug=p_slug,
                wine=wine,
                cuvee_display=disp or wine,
                cuvee_slug=c_slug,
                vintage_display=vintage,
                size=(row.get("Size") or "").strip(),
                quantity=qty,
                value_usd=money(row.get("Value")),
                price_usd=money(row.get("Price")),
                country=country,
                region=region,
                varietal=(row.get("Varietal") or "").strip(),
                drink_start=parse_year(row.get("BeginConsume") or ""),
                drink_end=parse_year(row.get("EndConsume") or ""),
                color=(row.get("Color") or "").strip(),
                category=(row.get("Category") or "").strip(),
            ))
    return bottles


def render_cellar_md(b: Bottle) -> str:
    drink_lines = []
    if b.drink_start is not None:
        drink_lines.append(f"drink_window_start: {b.drink_start}")
    else:
        drink_lines.append("drink_window_start: null")
    if b.drink_end is not None:
        drink_lines.append(f"drink_window_end: {b.drink_end}")
    else:
        drink_lines.append("drink_window_end: null")

    fm = [
        "---",
        "type: cellar_entry",
        f'producer: "{b.producer}"',
        f"producer_slug: {b.producer_slug}",
        f'cuvee: "{b.cuvee_display.replace(chr(34), chr(39))}"',
        f'vintage: "{b.vintage_display}"',
        f'bottle_size: "{b.size}"',
        f"quantity: {b.quantity}",
        f"purchase_price_usd: {b.price_usd:g}",
        f"current_value_usd: {b.value_usd:g}",
        'source_retailer: ""',
        'location: ""',
        *drink_lines,
        f'country: "{b.country}"',
        f'region: "{b.region}"',
        f'varietal: "{b.varietal}"',
        f'color: "{b.color}"',
        f'category: "{b.category}"',
        "opened: []",
        "---",
        "",
        f"# {b.producer} — {b.cuvee_display} {b.vintage_display}",
        "",
        f"- **Producer:** {b.producer}",
        f"- **Cuvée:** {b.cuvee_display}",
        f"- **Vintage:** {b.vintage_display}",
        f"- **Format:** {b.size}",
        f"- **Quantity owned:** {b.quantity}",
        f"- **Purchase price:** ${b.price_usd:g}",
        f"- **Current value (CT):** ${b.value_usd:g}",
    ]
    if b.drink_start or b.drink_end:
        window = f"{b.drink_start or '?'}–{b.drink_end or '?'}"
        fm.append(f"- **Drink window:** {window}")
    fm.append(f"- **Origin:** {b.country}{(', ' + b.region) if b.region else ''}")
    fm.append(f"- **Varietal:** {b.varietal}")
    fm.append("")
    fm.append("## Notes")
    fm.append("")
    fm.append("_Free-form. Tasting notes, serving, pairings._")
    fm.append("")
    return "\n".join(fm)


# --- producer-page ## Cellar section ---

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
CELLAR_SECTION_RE = re.compile(
    r"## Cellar\n.*?(?=\n## [^#]|\Z)", re.DOTALL
)


def build_cellar_section(bottles: list[Bottle]) -> str:
    lines = ["## Cellar", ""]
    total_q = sum(b.quantity for b in bottles)
    lines.append(f"Own **{total_q} bottle(s)** across {len(bottles)} cuvée-vintage(s):")
    lines.append("")
    for b in sorted(bottles, key=lambda x: (x.vintage_display, x.cuvee_display)):
        window = ""
        if b.drink_start or b.drink_end:
            window = f" — drink {b.drink_start or '?'}–{b.drink_end or '?'}"
        price = f" @ ${b.price_usd:g}" if b.price_usd else ""
        lines.append(
            f"- {b.quantity} × {b.cuvee_display} {b.vintage_display}"
            f" ({b.size}){price}{window}"
        )
    lines.append("")
    return "\n".join(lines)


def update_producer_cellar(slug: str, bottles: list[Bottle]) -> bool:
    path = PRODUCERS / f"{slug}.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False
    fm, body = m.group(1), m.group(2)
    new_section = build_cellar_section(bottles)
    if CELLAR_SECTION_RE.search(body):
        body = CELLAR_SECTION_RE.sub(new_section.rstrip() + "\n", body, count=1)
    else:
        # Insert before Cross-references if present, else append
        if "## Cross-references" in body:
            body = body.replace(
                "## Cross-references",
                new_section.rstrip() + "\n\n## Cross-references",
                1,
            )
        else:
            body = body.rstrip() + "\n\n" + new_section
    path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")
    return True


def main() -> int:
    if not SRC_CSV.exists():
        print(f"CSV not found: {SRC_CSV}", file=sys.stderr)
        return 1
    CELLAR_DIR.mkdir(parents=True, exist_ok=True)

    bottles = load_bottles()
    print(f"Parsed {len(bottles)} cuvée-vintage rows "
          f"({sum(b.quantity for b in bottles)} bottles)")

    # Emit one file per bottle
    written = 0
    filename_clash = 0
    seen_filenames: dict[str, int] = {}
    for b in bottles:
        fn = b.filename
        if fn in seen_filenames:
            seen_filenames[fn] += 1
            fn = fn.replace(".md", f"__{seen_filenames[fn]}.md")
            filename_clash += 1
        else:
            seen_filenames[fn] = 1
        (CELLAR_DIR / fn).write_text(render_cellar_md(b), encoding="utf-8")
        written += 1

    # Update producer pages
    by_producer: dict[str, list[Bottle]] = defaultdict(list)
    for b in bottles:
        by_producer[b.producer_slug].append(b)

    updated_producers = 0
    producers_missing = []
    for slug, bs in by_producer.items():
        if update_producer_cellar(slug, bs):
            updated_producers += 1
        else:
            producers_missing.append((slug, bs))

    # Report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    producers_missing.sort(key=lambda t: -sum(b.quantity for b in t[1]))
    lines = [
        "---",
        "type: ingest_report",
        "source: cellartracker_csv",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_rows: {len(bottles)}",
        f"total_bottles: {sum(b.quantity for b in bottles)}",
        f"cellar_files_written: {written}",
        f"filename_clashes_renamed: {filename_clash}",
        f"producers_in_cellar: {len(by_producer)}",
        f"producer_pages_updated: {updated_producers}",
        f"producers_missing_wiki_entry: {len(producers_missing)}",
        "---",
        "",
        "# Cellar ingest report",
        "",
        f"Parsed **{len(bottles)}** cuvée-vintage rows ({sum(b.quantity for b in bottles)} bottles).",
        f"Wrote **{written}** files to `cellar/` and updated **{updated_producers}** producer pages "
        "with a `## Cellar` section.",
        "",
    ]
    if producers_missing:
        lines += [
            f"## Cellar producers not in wiki ({len(producers_missing)})",
            "",
            "These producers appear in your cellar but have no `wiki/producers/<slug>.md` entry. "
            "Adding entries (even stubs) lets the widget cross-link cellar ↔ editorial context.",
            "",
            "| Producer slug | Bottles | Sample cuvée |",
            "|---|---:|---|",
        ]
        for slug, bs in producers_missing:
            q = sum(b.quantity for b in bs)
            sample = bs[0].cuvee_display if bs else ""
            lines.append(f"| `{slug}` | {q} | {sample} |")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {written} cellar files; updated {updated_producers} producer pages")
    print(f"Producers in cellar without wiki entries: {len(producers_missing)}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
