"""
migrate_resources_to_pages.py — split `wiki/_resources.md` (flat reference
list of ~60 importers + ~120 retailers) into one-per-file Karpathy pages.

`_resources.md` was a single human-curated reference doc — useful, but
not Karpathy-shaped (one page per entity, frontmatter-typed,
wikilink-citable). This migration:

  1. Parses `_resources.md` for importer and retailer entries.
  2. For each entry, produces `wiki/importers/<Slug>.md` (or retailer
     equivalent) with proper frontmatter (type, name, slug, url, focus,
     notes).
  3. MERGES into existing auto-generated pages: keeps the auto producer
     table (between `<!-- BEGIN AUTO -->` markers), updates frontmatter
     with `url` + `notes` + curated `focus` from the reference.

After this lands, `_resources.md` becomes redundant (still kept as a
flat dump for export), and `wiki/importers/` + `wiki/retailers/` are
the canonical surfaces — discoverable through `wiki/index.md` and
linkable as `[[<slug>|Display]]` from producer pages.

Idempotent: re-running merges new content while preserving any
hand-edits between auto-markers.

Usage:
    python scripts/migrate_resources_to_pages.py            # dry-run
    python scripts/migrate_resources_to_pages.py --apply    # write files
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
RESOURCES = VAULT / "wiki" / "_resources.md"
IMPORTERS = VAULT / "wiki" / "importers"
RETAILERS = VAULT / "wiki" / "retailers"

SECTION_HEADERS = {
    "IMPORTERS — MAJOR": "importer",
    "IMPORTERS — BOUTIQUE / SPECIALIST": "importer",
    "RETAILERS — USA (alphabetical)": "retailer",
}

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
ENTRY_LINE_RE = re.compile(
    r"^(?P<name>[^|]+?)\s*\|\s*(?P<url>[^|]+?)(?:\s*\|\s*(?P<notes>.*?))?\s*$"
)


def safe_slug(name: str) -> str:
    """Match the slug convention used by build_rollups.py:safe_filename
    (preserves case + underscores for the filename), and a lowercase
    snake_case slug for the frontmatter `slug:` field."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s\-&]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "unnamed"


def slug_lower(name: str) -> str:
    return safe_slug(name).lower()


# Canonical filename overrides for entries whose resources.md name doesn't
# match the existing auto-generated page (which uses producer `importer_us:`
# values, often the short common name).
CANONICAL_FILENAME: dict[str, str] = {
    # importers
    "Polaner Selections":               "Polaner.md",
    "Kermit Lynch Wine Merchant":       "Kermit_Lynch.md",
    "Louis/Dressner Selections (LDM)":  "Louis.md",   # also alias to Dressner
    "Neal Rosenthal / Rosenthal Wine":  "Neal_Rosenthal.md",
    "Skurnik Wines & Spirits":          "Skurnik.md",
    "Skurnik / Terry Theise":           "Theise.md",
    "Kysela Père et Fils":              "Kysela.md",
    # retailers
    "Chambers Street Wines":            "Chambers_Street_Wines.md",
    "Raeders Fine Wine":                "Raeders.md",
}

# Some _resources.md entries map onto MULTIPLE existing pages (LDM splits
# into Louis + Dressner). Each extra alias gets its own merge target.
EXTRA_ALIAS_FILENAMES: dict[str, list[str]] = {
    "Louis/Dressner Selections (LDM)":  ["Dressner.md"],
}


@dataclass
class Entry:
    kind: str           # "importer" or "retailer"
    name: str
    url: str
    notes: str          # raw notes string (everything after the second |)

    @property
    def filename(self) -> str:
        return CANONICAL_FILENAME.get(self.name, safe_slug(self.name) + ".md")

    @property
    def slug(self) -> str:
        return slug_lower(self.name)

    @property
    def alias_filenames(self) -> list[str]:
        return EXTRA_ALIAS_FILENAMES.get(self.name, [])


def parse_resources(text: str) -> list[Entry]:
    """Walk the resources file section by section."""
    entries: list[Entry] = []
    current_kind: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        clean = line.strip().strip("═").strip()
        if clean in SECTION_HEADERS:
            current_kind = SECTION_HEADERS[clean]
            continue
        if clean == "NOTES":
            current_kind = None
            continue
        if not current_kind:
            continue
        # Strip backslash-escape from the legacy doc (`E\&R`, `K\&L`)
        line = line.replace(r"\&", "&").replace(r"\-", "-")
        if "|" not in line:
            continue
        m = ENTRY_LINE_RE.match(line)
        if not m:
            continue
        name = m.group("name").strip()
        url = m.group("url").strip()
        notes = (m.group("notes") or "").strip()
        if not name or len(name) > 60:
            continue
        entries.append(Entry(kind=current_kind, name=name, url=url, notes=notes))
    return entries


# --- focus extraction from free-text notes ----------------------------

REGION_KEYWORDS = [
    "Burgundy", "Bordeaux", "Champagne", "Rhône", "Rhone", "Loire",
    "Alsace", "Beaujolais", "Provence", "Jura", "Savoie", "Corsica",
    "Piedmont", "Tuscany", "Sicily", "Veneto", "Friuli", "Alto Adige",
    "Marche", "Abruzzo", "Campania", "Liguria", "Valle d'Aosta",
    "Mosel", "Pfalz", "Rheinhessen", "Nahe", "Baden", "Franken",
    "Catalonia", "Bierzo", "Rioja", "Galicia", "Ribera del Duero",
    "Mendoza", "Patagonia", "Argentina", "Chile", "Uruguay", "Portugal",
    "Austria", "Germany", "Italy", "France", "Spain", "Greece",
    "Georgia",
]

STYLE_KEYWORDS = [
    "natural", "biodynamic", "organic", "artisan", "terroir",
    "grower champagne", "grower", "fine & rare", "specialty",
]


def extract_focus(notes: str) -> list[str]:
    out: list[str] = []
    for r in REGION_KEYWORDS:
        if re.search(rf"\b{re.escape(r)}\b", notes, re.IGNORECASE):
            out.append(r)
    return sorted(set(out))


def extract_tags(notes: str) -> list[str]:
    out: list[str] = []
    for kw in STYLE_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", notes, re.IGNORECASE):
            out.append(kw.lower().replace(" ", "-"))
    return sorted(set(out))


# --- page render / merge ---------------------------------------------

AUTO_BEGIN = "<!-- BEGIN AUTO-GENERATED (build_rollups.py) -->"
AUTO_END = "<!-- END AUTO-GENERATED -->"


def render_new(entry: Entry) -> str:
    """Build a fresh page for an entry that has no existing page."""
    today = date.today().isoformat()
    focus = extract_focus(entry.notes)
    tags = extract_tags(entry.notes)
    lines = [
        "---",
        f"type: {entry.kind}",
        f'name: "{entry.name}"',
        f"slug: {entry.slug}",
        f'url: "{entry.url}"',
        f"focus: {focus}",
        f"tags: {tags}",
        f"updated: {today}",
        f"_source: wiki/_resources.md",
        "---",
        "",
        f"# {entry.name}",
        "",
    ]
    if entry.notes:
        lines.append(entry.notes)
        lines.append("")
    lines += [
        AUTO_BEGIN,
        "",
        "_No producers from this importer/retailer are tracked in the vault yet._" if entry.kind == "importer"
        else "_No producers from this retailer are tracked in the vault yet._",
        "",
        AUTO_END,
        "",
    ]
    return "\n".join(lines)


def merge_into_existing(entry: Entry, existing: str) -> str:
    """Update an existing page: enrich frontmatter (url/focus/notes
    when missing), preserve auto-section, preserve any prose body."""
    parts_match = FM_RE.match(existing)
    if not parts_match:
        return render_new(entry)
    fm, body = parts_match.group(1), parts_match.group(2)

    # Ensure url is set (preserve if non-empty, else use entry's)
    if not re.search(r'^url:\s*"[^"]+"', fm, re.MULTILINE):
        fm = re.sub(r'^url:.*$', f'url: "{entry.url}"', fm, count=1, flags=re.MULTILINE)
        if not re.search(r"^url:", fm, re.MULTILINE):
            fm += f'\nurl: "{entry.url}"'

    # Ensure focus exists; only fill when missing or empty
    existing_focus = re.search(r"^focus:\s*\[(.*?)\]\s*$", fm, re.MULTILINE)
    if not existing_focus or not existing_focus.group(1).strip():
        focus_str = str(extract_focus(entry.notes))
        if re.search(r"^focus:", fm, re.MULTILINE):
            fm = re.sub(r"^focus:.*$", f"focus: {focus_str}", fm, count=1, flags=re.MULTILINE)
        else:
            fm += f"\nfocus: {focus_str}"

    # Ensure tags exist
    if not re.search(r"^tags:\s*\[", fm, re.MULTILINE):
        tags_str = str(extract_tags(entry.notes))
        fm += f"\ntags: {tags_str}"

    # Source flag for traceability
    if "_source:" not in fm:
        fm += "\n_source: wiki/_resources.md"

    return f"---\n{fm}\n---\n{body}"


def write_page_to(entry: Entry, filename: str, apply: bool) -> str:
    dest_dir = IMPORTERS if entry.kind == "importer" else RETAILERS
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / filename
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        new_text = merge_into_existing(entry, existing)
        action = "merged"
    else:
        new_text = render_new(entry)
        action = "created"
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return action


def write_page(entry: Entry, apply: bool) -> str:
    primary = write_page_to(entry, entry.filename, apply)
    for alias in entry.alias_filenames:
        write_page_to(entry, alias, apply)
    return primary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write changes. Default is dry-run.")
    args = ap.parse_args()

    if not RESOURCES.exists():
        sys.exit(f"ERROR: {RESOURCES} not found.")

    entries = parse_resources(RESOURCES.read_text(encoding="utf-8"))
    print(f"Parsed {len(entries)} entries from {RESOURCES.name}")

    counts = {"importer_created": 0, "importer_merged": 0,
              "retailer_created": 0, "retailer_merged": 0}
    for e in entries:
        action = write_page(e, args.apply)
        counts[f"{e.kind}_{action}"] += 1

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n=== {mode} ===")
    for k, v in counts.items():
        print(f"  {k:24s}: {v}")
    if not args.apply:
        print("\n(re-run with --apply to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
