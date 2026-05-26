"""
fix_vault_architecture.py — one-shot migration to repair the vault's
Karpathy-pattern preconditions.

Runs against `wiki/producers/`:

  1. Delete misclassified relics:
       - wiki/producers/index.md (CSW Master Index legacy — doesn't belong
         in producers/, was being grouped as "Unknown" producer)
       - wiki/producers/domaine_chanter├¬ves.md (mojibake duplicate of
         domaine_chantereves.md — both have same 3 CSW articles, the
         ASCII version has more body content)

  2. Resolve 8 CSW-surname collision pairs by deleting the false-positive
     "bare surname" page and folding aliases into the canonical producer:

         rousset       → domaine_rousset
         garon         → domaine_garon
         piane         → le_piane          (Alto Piemonte producer)
         magnien       → split: aliases on stephane_magnien + henri_magnien
                                 (page itself is mixed false positives)
         mallard       → michel_mallard
         paris         → vincent_paris     (paris.md matched every article
                                            mentioning the city — 58 articles)
         tissot        → stephane_tissot
         produttori    → produttori_del_barbaresco  (same producer)

     (bernard_baudry / domaine_baudry are kept distinct — different
     family branches, different article counts. Aliases are added to
     disambiguate.)

  3. Auto-fix `region` taxonomy violations (35 cases): regions like
     `Mosel (Dhron)` or `Barolo / Barbaresco` are not in `_TAXONOMY.md`.
     Move the granular value into `sub_region` and set `region` to the
     allowed parent per the suggestion table in `scripts/lint.py`.

  4. Backfill empty `region:` for producers where it can be inferred
     from prior knowledge of the producer (16 cases). Pure
     domain-knowledge mapping — committed to the script so it's
     reproducible and reviewable.

  5. Normalize the 5 producer pages that have no YAML frontmatter (older
     ingest format). Parse the `**Region:**` body line, emit a minimal
     valid frontmatter that satisfies the schema. Source markdown is
     preserved.

Idempotent: re-running after a clean run is a no-op (all checks
short-circuit when state is already correct).

Usage:
    python scripts/fix_vault_architecture.py            # dry-run
    python scripts/fix_vault_architecture.py --apply    # commit changes

Run `python scripts/lint.py` afterwards to confirm 0 issues, then
`python scripts/build_rollups.py` to regenerate region pages and
`python scripts/build_wiki_index.py` to refresh the index.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


# --- relics to delete outright ------------------------------------------

RELICS = [
    "index.md",                       # CSW master index, not a producer
    "domaine_chanter├¬ves.md",        # mojibake dupe of domaine_chantereves
]


# --- surname collisions: (drop_slug, keep_slug, aliases_to_add_on_keep) -

COLLISION_MERGES: list[tuple[str, str, list[str]]] = [
    ("rousset",    "domaine_rousset",            ["Rousset", "Stéphane Rousset",
                                                  "Domaine Stéphane Rousset"]),
    ("garon",      "domaine_garon",              ["Garon"]),
    ("piane",      "le_piane",                   ["Piane"]),
    ("mallard",    "michel_mallard",             ["Mallard", "Domaine Mallard"]),
    ("paris",      "vincent_paris",              ["Paris"]),
    ("tissot",     "stephane_tissot",            ["Tissot", "Domaine Tissot"]),
    ("produttori", "produttori_del_barbaresco",  ["Produttori"]),
]

# Magnien is special: `magnien.md` is the false-positive trap. Its
# articles are split between Stéphane Magnien and Henri Magnien (and a
# misc third Magnien). Drop the bare slug; the two real Magnien pages
# stay separate, each gets its own alias.
MAGNIEN_DROP = "magnien"
MAGNIEN_ALIASES: dict[str, list[str]] = {
    "stephane_magnien": ["Stéphane Magnien", "Stephane Magnien",
                         "Domaine Stéphan Magnien"],
    "henri_magnien": ["Henri Magnien"],
}

# Distinct producers that share a surname — kept separate, just disambiguated.
DISAMBIG_ALIASES: dict[str, list[str]] = {
    "bernard_baudry": ["Bernard Baudry"],
    "domaine_baudry": ["Domaine Baudry", "Matthieu Baudry"],
}


# --- region taxonomy migration ------------------------------------------
#
# Rules: if region contains a parenthesized sub-region, split. Otherwise
# look up in this table. Output: (region, sub_region). sub_region falls
# back to the original value when no override is given.

REGION_OVERRIDES: dict[str, tuple[str, str]] = {
    # raw value                                       region        sub_region
    "Saar":                                            ("Mosel",     "Saar"),
    "Basque":                                          ("",          "Basque"),       # country-dependent, see below
    "Barbaresco":                                      ("Piedmont",  "Barbaresco"),
    "Barolo / Barbaresco":                             ("Piedmont",  "Barolo / Barbaresco"),
    "Barbaresco / Barolo":                             ("Piedmont",  "Barbaresco / Barolo"),
    "Chianti Classico":                                ("Tuscany",   "Chianti Classico"),
}

# Parent inferences for `<Parent> (<sub>)` and `<Sub-of-X>` patterns.
SUBREGION_PARENT: list[tuple[str, str]] = [
    # (substring match, parent region in taxonomy)
    ("Barolo",       "Piedmont"),
    ("Barbaresco",   "Piedmont"),
    ("Verduno",      "Piedmont"),
    ("Monforte",     "Piedmont"),
    ("Castiglione",  "Piedmont"),
    ("Neive",        "Piedmont"),
    ("La Morra",     "Piedmont"),
    ("Serralunga",   "Piedmont"),
    ("Saar",         "Mosel"),
    ("Ruwer",        "Mosel"),
    ("Dhron",        "Mosel"),
    ("Enkirch",      "Mosel"),
    ("Graach",       "Mosel"),
    ("Pünderich",    "Mosel"),
    ("Punderich",    "Mosel"),
    ("Winningen",    "Mosel"),
    ("Konz",         "Mosel"),
    ("Saarburg",     "Mosel"),
    ("Mosel",        "Mosel"),
    ("Etna",         "Sicily"),
    ("Vittoria",     "Sicily"),
    ("Faro",         "Sicily"),
    ("Riviera Ligure", "Liguria"),
    ("Chianti",      "Tuscany"),
    ("Brunello",     "Tuscany"),
    ("Bolgheri",     "Tuscany"),
    ("Timorasso",    "Colli Tortonesi"),
    ("Bennwihr",     "Alsace"),
    ("Alsace",       "Alsace"),
]

# Region taxonomy lookup — kept in sync with _TAXONOMY.md (source of truth
# is the taxonomy file, this list is just the parents we use as auto-fix
# targets). Producer keeps any sub_region we extract.
KNOWN_TOP_REGIONS = {
    "Alsace", "Beaujolais", "Bordeaux", "Burgundy", "Champagne", "Corsica",
    "Jura", "Loire", "Provence", "Rhône", "Savoie", "South West",
    "Languedoc-Roussillon", "Basque (Irouléguy)",
    "Ahr", "Baden", "Franken", "Mosel", "Nahe", "Pfalz", "Rheingau",
    "Rheinhessen", "Württemberg",
    "Piedmont", "Tuscany", "Sicily", "Veneto", "Lombardy",
    "Friuli-Venezia Giulia", "Alto Adige / Südtirol", "Valle d'Aosta",
    "Marche", "Abruzzo", "Campania", "Liguria", "Colli Tortonesi",
    "Emilia-Romagna",
    "Catalonia", "Bierzo", "Rioja", "Galicia", "Jumilla",
    "Ribera del Duero", "Basque Country",
    "Mendoza", "Patagonia", "Salta", "Jujuy", "San Juan",
    "Buenos Aires Province",
}


# --- empty-region backfill (16 cases) -----------------------------------
# Domain-knowledge-driven. Each entry is (slug, region, sub_region).
# These are the producers flagged `region_empty` by lint, except
# `index.md` (deleted) and `piane.md` (deleted).

EMPTY_REGION_BACKFILL: dict[str, tuple[str, str]] = {
    "gulfi":              ("Sicily",                "Vittoria"),
    "i_fabbri":           ("Tuscany",               "Chianti Classico"),
    "montenidoli":        ("Tuscany",               "San Gimignano"),
    "le_piane":           ("Piedmont",              "Alto Piemonte"),
    "agricola_tiberio":   ("Abruzzo",               ""),
    "castell_in_villa":   ("Tuscany",               "Chianti Classico"),
    "collestefano":       ("Marche",                "Matelica"),
    "elio_ottin":         ("Valle d'Aosta",         ""),
    "istine":             ("Tuscany",               "Chianti Classico"),
    "josephus_mayr":      ("Alto Adige / Südtirol", ""),
    "mosbacher":          ("Pfalz",                 ""),
    "pacherhof":          ("Alto Adige / Südtirol", "Eisacktal"),
    "pianelle":           ("Piedmont",              "Alto Piemonte"),
    "tenuta_di_carleone": ("Tuscany",               "Chianti Classico"),
    # Also handle the three flagged in `region_not_in_taxonomy` with
    # empty value due to ''-quoting:
    "beck-hartweg":       ("Alsace",                "Dambach-la-Ville"),
    "rings":              ("Pfalz",                 "Freinsheim"),
    # produttori is being deleted (collision merge → produttori_del_barbaresco)
}


# --- frontmatter helpers ------------------------------------------------

@dataclass
class Change:
    path: Path
    kind: str
    detail: str


def split_fm(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip().strip("'") if m else ""


def set_str(fm: str, key: str, value: str) -> str:
    """Replace `key: ...` line. Preserves indentation. Quotes always."""
    pat = rf'^({re.escape(key)}):\s*.*$'
    repl = f'{key}: "{value}"'
    new_fm, n = re.subn(pat, repl, fm, count=1, flags=re.MULTILINE)
    if n == 0:
        # Insert after `slug:` if missing
        new_fm = re.sub(r'^(slug:.*)$',
                        rf'\1\n{key}: "{value}"',
                        fm, count=1, flags=re.MULTILINE)
    return new_fm


def get_aliases(fm: str) -> list[str]:
    """Parse `aliases: ["a", "b"]` (one-line list form)."""
    m = re.search(r'^aliases:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'', inner):
        v = next((x for x in part if x), "").strip()
        if v:
            out.append(v)
    return out


def set_aliases(fm: str, aliases: list[str]) -> str:
    rendered = ", ".join(f'"{a}"' for a in aliases)
    pat = r'^aliases:.*$'
    repl = f'aliases: [{rendered}]'
    new_fm, n = re.subn(pat, repl, fm, count=1, flags=re.MULTILINE)
    if n == 0:
        new_fm = re.sub(r'^(slug:.*)$',
                        rf'\1\naliases: [{rendered}]',
                        fm, count=1, flags=re.MULTILINE)
    return new_fm


# --- per-producer fix routines ------------------------------------------

def parse_paren_region(raw: str) -> tuple[str, str]:
    """`Mosel (Dhron)` → ('Mosel', 'Dhron'). `Barolo / Barbaresco` →
    ('Barolo / Barbaresco', '')."""
    m = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", raw)
    if not m:
        return (raw.strip(), "")
    return (m.group(1).strip(), m.group(2).strip())


def normalize_region(country: str, region: str) -> tuple[str, str]:
    """Return (new_region, sub_region_to_set). new_region == '' means no
    change suggested."""
    region = region.strip().strip("'\"")
    if not region:
        return ("", "")
    if region in KNOWN_TOP_REGIONS:
        return ("", "")  # already valid

    # 1. Explicit override
    if region in REGION_OVERRIDES:
        new_r, sub = REGION_OVERRIDES[region]
        if region == "Basque":
            # France → Basque (Irouléguy), Spain → Basque Country
            if country == "France":
                return ("Basque (Irouléguy)", "")
            elif country == "Spain":
                return ("Basque Country", "")
            return ("", "")
        return (new_r, sub)

    # 2. Parenthesized: Mosel (Dhron) → Mosel + Dhron
    base, paren = parse_paren_region(region)
    if base in KNOWN_TOP_REGIONS:
        return (base, paren)

    # 3. Fall back to substring parent table (Barolo (...) → Piedmont)
    haystack = region
    for needle, parent in SUBREGION_PARENT:
        if needle.lower() in haystack.lower():
            # keep whole original as sub_region for full fidelity
            return (parent, region)
    return ("", "")


def fix_region_field(text: str, path: Path) -> tuple[str, list[Change]]:
    parts = split_fm(text)
    if not parts:
        return (text, [])
    fm, body = parts
    country = get_str(fm, "country")
    region = get_str(fm, "region")
    sub_region = get_str(fm, "sub_region")
    changes: list[Change] = []

    new_region, sub_to_add = normalize_region(country, region)
    if new_region:
        fm = set_str(fm, "region", new_region)
        if sub_to_add and not sub_region:
            fm = set_str(fm, "sub_region", sub_to_add)
        elif sub_to_add and sub_region != sub_to_add:
            # don't clobber a meaningful sub_region; only fill empty
            if not sub_region:
                fm = set_str(fm, "sub_region", sub_to_add)
        changes.append(Change(path, "region_fix",
                              f"{region!r} → region={new_region!r}, sub_region={sub_to_add!r}"))

    # Empty-region backfill from curated table
    if not region and path.stem in EMPTY_REGION_BACKFILL:
        new_r, sub_r = EMPTY_REGION_BACKFILL[path.stem]
        fm = set_str(fm, "region", new_r)
        if sub_r:
            fm = set_str(fm, "sub_region", sub_r)
        changes.append(Change(path, "region_backfill",
                              f"empty → region={new_r!r}, sub_region={sub_r!r}"))

    return (f"---\n{fm}\n---\n{body}", changes)


def add_aliases(text: str, new_aliases: list[str], path: Path) -> tuple[str, list[Change]]:
    parts = split_fm(text)
    if not parts:
        return (text, [])
    fm, body = parts
    existing = get_aliases(fm)
    merged: list[str] = list(existing)
    added: list[str] = []
    for a in new_aliases:
        if a not in merged:
            merged.append(a)
            added.append(a)
    if not added:
        return (text, [])
    fm = set_aliases(fm, merged)
    return (f"---\n{fm}\n---\n{body}",
            [Change(path, "alias_add", f"+{added}")])


# --- no-frontmatter producer normalization -----------------------------

NO_FM_REGION_LINE_RE = re.compile(r"^\*\*Region:\*\*\s*(.+?)\s*$", re.MULTILINE)
NO_FM_TITLE_RE = re.compile(r"^# (.+?)\s*$", re.MULTILINE)
NO_FM_CSW_COUNT_RE = re.compile(r"\*\*CSW Coverage:\*\*\s*(\d+)\s+article", re.IGNORECASE)
NO_FM_DEDICATED_RE = re.compile(r"·\s*(\d+)\s+dedicated", re.IGNORECASE)
NO_FM_CSW_YEAR_RE = re.compile(r"\((\d{4})", re.IGNORECASE)

NO_FM_REGION_HINTS: list[tuple[str, tuple[str, str, str]]] = [
    # (substring of "**Region:**" line, (country, region, sub_region))
    ("Champagne",         ("France", "Champagne", "")),
    ("Côtes de Provence", ("France", "Provence", "Côtes de Provence")),
    ("Provence",          ("France", "Provence", "")),
    ("Bordeaux",          ("France", "Bordeaux", "")),
    ("Burgundy",          ("France", "Burgundy", "")),
    ("Loire",             ("France", "Loire", "")),
    ("Rhône",             ("France", "Rhône", "")),
    ("Alsace",            ("France", "Alsace", "")),
]


def synthesize_frontmatter(text: str, slug: str) -> str | None:
    """Build a minimal valid YAML frontmatter for a no-frontmatter
    producer page. Returns full new file body, or None if we can't
    extract enough."""
    title_m = NO_FM_TITLE_RE.search(text)
    region_m = NO_FM_REGION_LINE_RE.search(text)
    if not title_m or not region_m:
        return None
    name = title_m.group(1).strip()
    region_line = region_m.group(1)

    country, region, sub_region = "", "", ""
    for hint, mapping in NO_FM_REGION_HINTS:
        if hint in region_line:
            country, region, sub_region = mapping
            break
    if not country:
        # default best-effort
        country = "France" if "France" in region_line else ""
    # sub_region from any "—" segments after first
    parts_after = re.split(r"\s*—\s*", region_line)
    if len(parts_after) >= 3 and not sub_region:
        sub_region = parts_after[-1].strip()

    csw_count = 0
    m = NO_FM_CSW_COUNT_RE.search(text)
    if m:
        csw_count = int(m.group(1))
    csw_dedicated = 0
    m = NO_FM_DEDICATED_RE.search(text)
    if m:
        csw_dedicated = int(m.group(1))
    csw_first = csw_last = 0
    years = NO_FM_CSW_YEAR_RE.findall(text)
    if years:
        ys = sorted({int(y) for y in years if 1990 < int(y) < 2100})
        if ys:
            csw_first = ys[0]
            csw_last = ys[-1]

    fm_lines = [
        "---",
        "type: producer",
        f'name: "{name}"',
        f"slug: {slug}",
        "aliases: []",
        f'country: "{country}"',
        f'region: "{region}"',
        f'sub_region: "{sub_region}"',
        "appellations: []",
        "farming: []",
        "certifications: []",
        "importer_us: []",
        "retailers:",
        "  chambers:",
        f"    championed: {'true' if csw_dedicated > 0 else 'false'}",
        f"    article_count: {csw_count}",
        f"    dedicated_count: {csw_dedicated}",
        f"    first_year: {csw_first}",
        f"    last_year: {csw_last}",
        "  dte:",
        "    in_portfolio: false",
        "    cuvee_count: 0",
        "    price_min: 0",
        "    price_max: 0",
        "  raeders:",
        "    in_portfolio: false",
        "  fass:",
        "    in_portfolio: false",
        "tags: []",
        "_sources:",
        f"- normalized_from_no_frontmatter:{slug}.md",
        "---",
        "",
    ]
    return "\n".join(fm_lines) + text


# --- runner -------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write changes. Default is dry-run.")
    args = ap.parse_args()
    apply = args.apply

    all_changes: list[Change] = []

    # Step 1: relics
    for name in RELICS:
        p = PRODUCERS / name
        if p.exists():
            if apply:
                p.unlink()
            all_changes.append(Change(p, "relic_delete", f"deleted {name}"))

    # Step 2: surname-collision merges
    for drop, keep, aliases in COLLISION_MERGES:
        drop_p = PRODUCERS / f"{drop}.md"
        keep_p = PRODUCERS / f"{keep}.md"
        if drop_p.exists():
            if apply:
                drop_p.unlink()
            all_changes.append(Change(drop_p, "collision_drop", f"deleted {drop}.md (folded into {keep})"))
        if keep_p.exists():
            text = keep_p.read_text(encoding="utf-8")
            new_text, changes = add_aliases(text, aliases, keep_p)
            if changes and apply:
                keep_p.write_text(new_text, encoding="utf-8")
            all_changes.extend(changes)

    # 2b: magnien (drop bare slug; add aliases to two real Magniens)
    m_drop = PRODUCERS / f"{MAGNIEN_DROP}.md"
    if m_drop.exists():
        if apply:
            m_drop.unlink()
        all_changes.append(Change(m_drop, "collision_drop",
                                  f"deleted {MAGNIEN_DROP}.md (false-positive trap)"))
    for slug, aliases in MAGNIEN_ALIASES.items():
        p = PRODUCERS / f"{slug}.md"
        if p.exists():
            text = p.read_text(encoding="utf-8")
            new_text, changes = add_aliases(text, aliases, p)
            if changes and apply:
                p.write_text(new_text, encoding="utf-8")
            all_changes.extend(changes)

    # 2c: disambig aliases for distinct same-surname producers
    for slug, aliases in DISAMBIG_ALIASES.items():
        p = PRODUCERS / f"{slug}.md"
        if p.exists():
            text = p.read_text(encoding="utf-8")
            new_text, changes = add_aliases(text, aliases, p)
            if changes and apply:
                p.write_text(new_text, encoding="utf-8")
            all_changes.extend(changes)

    # Step 3+4: per-producer region normalization + empty-region backfill
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        new_text, changes = fix_region_field(text, p)
        if changes and apply:
            p.write_text(new_text, encoding="utf-8")
        all_changes.extend(changes)

    # Step 5: synthesize frontmatter for the 5 no-frontmatter pages
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---\n"):
            continue  # already has frontmatter
        rebuilt = synthesize_frontmatter(text, p.stem)
        if rebuilt:
            if apply:
                p.write_text(rebuilt, encoding="utf-8")
            all_changes.append(Change(p, "frontmatter_synth",
                                       "added YAML frontmatter from body"))

    # --- report ---
    by_kind: dict[str, int] = {}
    for c in all_changes:
        by_kind[c.kind] = by_kind.get(c.kind, 0) + 1

    mode = "APPLIED" if apply else "DRY-RUN"
    print(f"\n=== {mode}: {len(all_changes)} changes across {len(by_kind)} categories ===")
    for kind, n in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"  {kind:24s}: {n}")
    if not apply:
        print("\n(re-run with --apply to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
