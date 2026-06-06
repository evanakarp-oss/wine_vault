"""
FASS Selections portfolio — full rebuild.

Source: `raw/fass/portfolio_2026-05-26.tsv` (canonical bulk dump) plus
`raw/fass/portfolio_curated_2026-05-26.tsv` (overlay with color/variety/
appellation enrichment when present).

Behavior:
- Strips every existing `## FASS` section AND `retailers.fass:` frontmatter
  block from `wiki/producers/*.md` before writing fresh state.
- Aggregates by canonical slug with a generous alias map + prefix-stripping
  heuristic ("Domaine ", "Weingut ", "Famille ", "Caves ", "Cantina ",
  trailing "& Fils" / "Pere & Fils" / "et Fils", etc.).
- Updates only producer pages that already exist (no auto-creation —
  spelling variation in this retailer's data is high).
- Writes color/variety/appellation enrichment from the curated overlay
  into the section table where rows can be matched.
- Generates `build/fass_ingest_report.md` listing matched + unmatched.

Idempotent: re-running produces the same vault state.
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

VAULT = Path(__file__).resolve().parent.parent
RAW_BULK = VAULT / "raw" / "fass" / "portfolio_2026-05-26.tsv"
RAW_CURATED = VAULT / "raw" / "fass" / "portfolio_curated_2026-05-26.tsv"
WIKI_DIR = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "fass_ingest_report.md"

# Explicit aliases for FASS producer names → wiki slug. Maps the messy
# retailer spellings to known wiki pages. Keys are lowercased.
FASS_ALIASES: dict[str, str] = {
    # ---- Originally-matched producers (pre-Tier-1-seed) ----
    "weingut achim durr": "achim_durr",
    "achim durr": "achim_durr",
    "achim duerr": "achim_durr",
    "achim-durr": "achim_durr",
    "gunther steinmetz": "steinmetz",
    "günther steinmetz": "steinmetz",
    "gunter steinmetz": "steinmetz",
    "bernard gripa": "domaine_gripa",
    "bernard and fabrice gripa": "domaine_gripa",
    "lauer": "peter_lauer__weingut_lauer",
    "peter lauer": "peter_lauer__weingut_lauer",
    "dönnhoff": "donnhoff",
    "weingut dönnhoff": "donnhoff",
    "donnhoff": "donnhoff",
    "enderle & moll": "enderle__moll",
    "enderle &amp; moll": "enderle__moll",
    "sven enderle": "sven_enderle",
    "patrick jasmin": "jasmin",
    "domaine jasmin": "jasmin",
    "gonon": "domaine_pierre_gonon",
    "pierre gonon": "domaine_pierre_gonon",
    "vincent paris": "vincent_paris",
    "christophe billon": "billon",
    "francois buffet": "francois_buffet",
    "françois buffet": "francois_buffet",
    "michel rebourgeon": "michel_rebourgeon",
    "domaine rebourgeon": "michel_rebourgeon",
    "kunstler": "weiser_kunstler",
    "künstler": "weiser_kunstler",
    "domaine jean-marc and hugues pavelot": "domaine_pavelot",
    "pavelot": "domaine_pavelot",
    # ---- Tier 1 seeded 2026-05-26: spelling variants ----
    "markus moitor": "markus_molitor",
    "martin muellen": "martin_muellen",
    "martin mullen": "martin_muellen",
    "martin müllen": "martin_muellen",
    "maison brisset": "pierre_brisset",
    "pierre briseet": "pierre_brisset",
    "j.j. girard": "jj_girard",
    "mikael bourg": "mickael_bourg",
    "compagnie de lhermitage": "compagnie_de_lhermitage",
    "compagnie l'hermitage": "compagnie_de_lhermitage",
    "compagnie l’hermitage": "compagnie_de_lhermitage",
    "lyle fass charalambos lelektsoglou": "compagnie_de_lhermitage",
    "lyle fass/charalambos": "compagnie_de_lhermitage",
    "georges lelektsoglou": "compagnie_de_lhermitage",
    "hector adrien charalambos lelektsoglou": "compagnie_de_lhermitage",
    "gerard courbis": "gerard_courbis",
    "gerard courbis et fils": "gerard_courbis",
    "gerard courbis pere & fils": "gerard_courbis",
    "gerard courbis père & fils": "gerard_courbis",
    "richard oestreicher": "richard_ostreicher",
    "richard östreicher": "richard_ostreicher",
    "phillippe naddef": "philippe_naddef",
    "philippe nadeff": "philippe_naddef",
    "michel naddef": "philippe_naddef",
    "domaine philippe": "philippe_naddef",
    "domaine philippe naddef": "philippe_naddef",
    "domaine du": "domaine_du_tunnel",
    "domaine des": "domaine_des_pierres_seches",
    "caves bourdy": "caves_jean_bourdy",
    "caves jean": "caves_jean_bourdy",
    "garaudet": "garaudet",
    "garaudet pere & fils": "garaudet",
    "garaudet père & fils": "garaudet",
    "sarl garaudet": "garaudet",
    "sarl garaudet pere & fils": "garaudet",
    "sarl garaudet pere et fils": "garaudet",
    "domaine daniel-etienne defaix": "daniel_etienne_defaix",
    "jean dauvissat pere & fils": "jean_dauvissat",
    "jean dauvissat père & fils": "jean_dauvissat",
    "jean dauvissat pere &amp; fils": "jean_dauvissat",
    "sébastien dampt": "sebastien_dampt",
    "laible": "andreas_laible",
    "laible am": "andreas_laible",
    "dr. wehrheim": "dr_wehrheim",
    "dr. wehreim": "dr_wehrheim",
    "hanspeter ziereisen": "ziereisen",
    "ar.pe.pe": "arpepe",
    "arpepe stella": "arpepe",
    "vigneti valle": "vigneti_valle_roncati",
    "podere ai": "podere_ai_valloni",
    "spreccher von bernegg": "sprecher_von_bernegg",
    "sprecher von": "sprecher_von_bernegg",
    "château de": "chateau_de_trinquevedel",  # not seeded but for completeness
    "bel air": "bel_air_marquis_daligre",
    "bel air marquis daligre": "bel_air_marquis_daligre",
    "adank": "weingut_hansruedi_adank",
    "cian fagna": "cianfagna",
    "rocche di barbari": "rocche_dei_barbari",
    "rochhe de barbari": "rocche_dei_barbari",
    "yvon métras": "yvon_metras",
    "domaine de cote epine": "domaine_de_cote_epine",
    "domaine de la cote st epine": "domaine_de_cote_epine",
    "domaine de la côte": "domaine_de_cote_epine",
    "vini marino proclamo cilento": "vini_marino_proclamo_cilento",
    "famlie jouffreau": "famille_jouffreau",
    "familie jouffreau clos de gamot": "famille_jouffreau",
    "familie jouffreau": "famille_jouffreau",
    "cave sebastien blachon": "domaine_blachon",
    "cuchet-beliando cornas": "cuchet_beliando",
    "cuchet-beliando": "cuchet_beliando",
    "henri gallet": "domaine_gallet",  # Domaine Gallet not seeded
    "maison stephan": "jean_michel_stephan",
    "michelle luyton": "luyton",  # Luyton not seeded
    "joseph walter": "josef_walter",
    "weingut josef walter": "josef_walter",
    "weingut weltner": "paul_weltner",
    "perseval farge": "perseval_farge",
    "etienne calsac": "etienne_calsac",
    "diot-legras les": "diot_benoit",
    "diot-legras": "diot_benoit",
    "marc hebrart": "marc_hebrart",
    "jean dauvissat": "jean_dauvissat",
    "jean dauvissat père & fils": "jean_dauvissat",
    "spater veit": "spater_veit",
    "spater-veit": "spater_veit",
    "später-veit": "spater_veit",
    "ar.pe.pe.": "arpepe",
    "podere ai valloni": "podere_ai_valloni",
    "vigneti valle roncati": "vigneti_valle_roncati",
    "kuhling-gillot": "kuhling_gillot",
    "thörle blanc": "thorle",
    "thorle blanc": "thorle",
    "thorle blanc de blancs": "thorle",
    "thörle blanc de blancs brut": "thorle",
    "thorle holle": "thorle",
    "thörle holle": "thorle",
    "thorle probstey": "thorle",
    "thörle probstey": "thorle",
    "thorle saulheimer": "thorle",
    "thörle saulheimer": "thorle",
    "thorle schlossberg": "thorle",
    "thörle": "thorle",
    "mohr-niggli": "mohr_niggli",
    "weingut familie hansruedi adank": "weingut_hansruedi_adank",
    "weingut hansruedi adank": "weingut_hansruedi_adank",
    "sébastien dampt": "sebastien_dampt",
    "yvon metras": "yvon_metras",
    "lafarge vial": "lafarge_vial",
    "rebholz": "okonomeriat_rebholz",
    "okonomeriat rebholz": "okonomeriat_rebholz",
    "christmann": "a_christmann",
    "dr burklin wolf": "dr_burklin_wolf",
    "dr. bürklin-wolf": "dr_burklin_wolf",
    "jj prum": "jj_prum",
    "selbach-oster": "selbach_oster",
    "andre francois": "andre_francois",
    "andré françois": "andre_francois",
    "jakob schneider": "jakob_schneider",
    "k.h. schneider": "k_h_schneider",
    "k h schneider": "k_h_schneider",
    "gut hermannsberg": "gut_hermannsberg",
    # ---- Tier 2 seeded 2026-05-26: spelling variants → new slugs ----
    # Alain Burguet
    "burguet": "alain_burguet",
    "jean-luc & eric burguet": "alain_burguet",
    # Jürgen von der Mark
    "jurgen von der mark": "jurgen_von_der_mark",
    "jürgen von der mark": "jurgen_von_der_mark",
    # Achim Dürr — three spellings consolidate
    "achim duerr": "achim_durr",
    "achim-durr": "achim_durr",
    "weingut achim durr": "achim_durr",
    # Cianfagna
    "cian fagna": "cianfagna",
    # Calafe — Greco di Tufo single-vineyard variant
    "calafe ariavecchia": "calafe",
    # Domaine Gallet
    "henri gallet": "domaine_gallet",
    # Luyton
    "michelle luyton": "luyton",
    # Marc Jambon
    "domaine marc jambon et fils": "marc_jambon",
    "marc jambon et fils": "marc_jambon",
    # Vini Marino
    "vini marino proclamo cilento": "vini_marino",
    # Cantina del Signore
    "cantina del": "cantina_del_signore",
    "cascina delsignore": "cantina_del_signore",
    # Château de Trinquevedel
    "château de": "chateau_de_trinquevedel",
    "chateau de": "chateau_de_trinquevedel",
    # Wegelin
    "wegelin weisstorkel": "wegelin",
    "wegelin weine ag": "wegelin",
    "weggelin": "wegelin",
    # Max Geitlinger
    "max geitlinger wein": "max_geitlinger",
    # ---- Trailing aliases for the long retailer-row names ----
    'caillez-lemaire "pur meunier" brut nature': "caillez_lemaire",
    'caillez lemaire "pur meunier" brut nature': "caillez_lemaire",
    "laurent & karen boussey": "laurent_boussey",
    "cuchet beliando cornas": "cuchet_beliando",
    "diot legras les": "diot_benoit",
}

# Common prefixes/suffixes stripped when matching against wiki slugs.
STRIP_PREFIXES = [
    "domaine ", "domaines ", "weingut ", "famille ", "familie ", "chateau ",
    "château ", "maison ", "cantina ", "vigneti ", "tenuta ", "caves ", "cave ",
    "podere ", "podere ai ", "weingut familie ",
]
STRIP_SUFFIXES = [
    " pere & fils", " pere et fils", " père & fils", " père et fils",
    " et fils", " & fils", " pere & fils",
]


def canonical_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    # HTML entity cleanup (e.g. "Enderle &amp; Moll").
    s = s.replace("&amp;", "&")
    s = re.sub(r"[^\w\s&\-]", " ", s)
    s = re.sub(r"\s*&\s*", "_", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def slug_variants(name: str) -> list[str]:
    """Generate candidate slugs to try matching against wiki/producers/."""
    cleaned = unicodedata.normalize("NFKD", name)
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    cleaned = cleaned.lower().strip().replace("&amp;", "&")
    variants: list[str] = [canonical_slug(name)]
    for prefix in STRIP_PREFIXES:
        if cleaned.startswith(prefix):
            variants.append(canonical_slug(cleaned[len(prefix):]))
    stripped = cleaned
    for suffix in STRIP_SUFFIXES:
        if stripped.endswith(suffix):
            stripped = stripped[: -len(suffix)].strip()
    if stripped != cleaned:
        variants.append(canonical_slug(stripped))
        for prefix in STRIP_PREFIXES:
            if stripped.startswith(prefix):
                variants.append(canonical_slug(stripped[len(prefix):]))
    # Dedup preserving order.
    seen = set()
    out = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def resolve_slug(name: str, existing: set[str]) -> str | None:
    key = name.lower().strip().replace("&amp;", "&")
    if key in FASS_ALIASES:
        cand = FASS_ALIASES[key]
        return cand if cand in existing else None
    for v in slug_variants(name):
        if v in existing:
            return v
    return None


@dataclass
class Cuvee:
    wine: str
    vintage: str
    price: float
    color: str = ""
    variety: str = ""
    appellation: str = ""


@dataclass
class ProducerAgg:
    name: str
    slug_guess: str
    country: str
    region: str
    subregion: str = ""
    cuvees: list[Cuvee] = field(default_factory=list)

    @property
    def cuvee_count(self) -> int:
        return len(self.cuvees)

    @property
    def price_min(self) -> float:
        prices = [c.price for c in self.cuvees if c.price > 0]
        return min(prices) if prices else 0.0

    @property
    def price_max(self) -> float:
        prices = [c.price for c in self.cuvees if c.price > 0]
        return max(prices) if prices else 0.0


PRICE_RE = re.compile(r"[^\d.]")


def parse_price(s: str) -> float:
    if not s:
        return 0.0
    cleaned = PRICE_RE.sub("", s)
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def parse_vintage_prefix(wine: str) -> tuple[str, str]:
    """Pull a 4-digit year prefix off the wine name (curated table format)."""
    m = re.match(r"^\s*(NV|\d{4})\s+(.*)$", wine)
    if m:
        return m.group(1), m.group(2).strip()
    return "", wine.strip()


def load_bulk(path: Path) -> list[Cuvee]:
    rows: list[tuple[str, Cuvee, str, str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            producer = (row.get("producer") or "").strip()
            wine = (row.get("wine") or "").strip()
            vintage = (row.get("vintage") or "").strip()
            country = (row.get("country") or "").strip()
            region = (row.get("region") or "").strip()
            subregion = (row.get("subregion") or "").strip()
            price = parse_price(row.get("price") or "")
            if not producer:
                continue
            cuvee = Cuvee(wine=wine, vintage=vintage, price=price)
            rows.append((producer, cuvee, country, region, subregion))
    return rows  # type: ignore[return-value]


def load_curated(path: Path) -> list[tuple[str, Cuvee, str, str]]:
    """Curated overlay rows. wine has vintage prefix; price is unquoted dollars."""
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            producer = (row.get("producer") or "").strip()
            wine_raw = (row.get("wine") or "").strip()
            vintage, wine = parse_vintage_prefix(wine_raw)
            price = parse_price(row.get("price") or "")
            country = (row.get("country") or "").strip()
            region = (row.get("region") or "").strip()
            appellation = (row.get("appellation") or "").strip()
            color = (row.get("color") or "").strip()
            variety = (row.get("variety") or "").strip()
            if not producer or not wine:
                continue
            cuvee = Cuvee(
                wine=wine,
                vintage=vintage,
                price=price,
                color=color,
                variety=variety,
                appellation=appellation,
            )
            rows.append((producer, cuvee, country, region))
    return rows


def aggregate(
    bulk_rows: list[tuple[str, Cuvee, str, str, str]],
    curated_rows: list[tuple[str, Cuvee, str, str]],
    existing_slugs: set[str],
) -> tuple[dict[str, ProducerAgg], dict[str, ProducerAgg]]:
    """Return (matched_by_slug, unmatched_by_canonical_slug)."""
    matched: dict[str, ProducerAgg] = {}
    unmatched: dict[str, ProducerAgg] = {}

    # Curated overlay: build (slug → wine_lower → Cuvee) lookup.
    overlay: dict[str, dict[str, Cuvee]] = defaultdict(dict)
    for producer, cuvee, country, region in curated_rows:
        slug = resolve_slug(producer, existing_slugs) or canonical_slug(producer)
        overlay[slug][cuvee.wine.strip().lower()] = cuvee

    def stash(producer: str, cuvee: Cuvee, country: str, region: str,
              subregion: str) -> None:
        slug = resolve_slug(producer, existing_slugs)
        target = matched if slug else unmatched
        key = slug or canonical_slug(producer)
        if key not in target:
            target[key] = ProducerAgg(
                name=producer, slug_guess=key, country=country,
                region=region, subregion=subregion,
            )
        agg = target[key]
        if not agg.country and country:
            agg.country = country
        if not agg.region and region:
            agg.region = region
        if not agg.subregion and subregion:
            agg.subregion = subregion
        # Overlay enrichment lookup.
        ov = overlay.get(key, {}).get(cuvee.wine.strip().lower())
        if ov:
            cuvee.color = cuvee.color or ov.color
            cuvee.variety = cuvee.variety or ov.variety
            cuvee.appellation = cuvee.appellation or ov.appellation
        agg.cuvees.append(cuvee)

    for producer, cuvee, country, region, subregion in bulk_rows:
        stash(producer, cuvee, country, region, subregion)

    # Curated-only wines (no counterpart in bulk) — add as extra rows.
    bulk_keys: dict[str, set[str]] = defaultdict(set)
    for producer, cuvee, _, _, _ in bulk_rows:
        slug = resolve_slug(producer, existing_slugs) or canonical_slug(producer)
        bulk_keys[slug].add(cuvee.wine.strip().lower())
    for producer, cuvee, country, region in curated_rows:
        slug = resolve_slug(producer, existing_slugs) or canonical_slug(producer)
        if cuvee.wine.strip().lower() not in bulk_keys[slug]:
            stash(producer, cuvee, country, region, "")

    return matched, unmatched


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
FASS_FM_BLOCK_RE = re.compile(r"  fass:\n(?:    [^\n]+\n)+")
FASS_SECTION_RE = re.compile(r"\n*## FASS\n.*?(?=\n## [^#]|\Z)", re.DOTALL)


def build_fass_fm_block(agg: ProducerAgg) -> str:
    return ("  fass:\n"
            "    in_portfolio: true\n"
            f"    cuvee_count: {agg.cuvee_count}\n"
            f"    price_min: {int(agg.price_min)}\n"
            f"    price_max: {int(agg.price_max)}\n")


def build_fass_section(agg: ProducerAgg) -> str:
    lines = ["## FASS", ""]
    sorted_cuvees = sorted(
        agg.cuvees, key=lambda c: (c.wine.lower(), c.vintage or "0")
    )
    pmin, pmax = agg.price_min, agg.price_max
    if pmin or pmax:
        lines.append(
            f"Currently tracked: **{agg.cuvee_count} cuvée/vintage entries**; "
            f"prices ${pmin:.0f}–${pmax:.0f}."
        )
    else:
        lines.append(f"Currently tracked: **{agg.cuvee_count} cuvée/vintage entries**.")
    lines.append("")
    show_enrichment = any(c.color or c.variety for c in sorted_cuvees)
    if show_enrichment:
        lines.append("| Cuvée | Vintage | Price | Color | Variety |")
        lines.append("|---|---|---|---|---|")
    else:
        lines.append("| Cuvée | Vintage | Price |")
        lines.append("|---|---|---|")
    cap = 40
    for c in sorted_cuvees[:cap]:
        p = f"${c.price:.0f}" if c.price else "—"
        if show_enrichment:
            lines.append(
                f"| {c.wine or '—'} | {c.vintage or 'NV'} | {p} | "
                f"{c.color or '—'} | {c.variety or '—'} |"
            )
        else:
            lines.append(f"| {c.wine or '—'} | {c.vintage or 'NV'} | {p} |")
    if len(sorted_cuvees) > cap:
        if show_enrichment:
            lines.append(f"| _… {len(sorted_cuvees) - cap} more entries_ | | | | |")
        else:
            lines.append(f"| _… {len(sorted_cuvees) - cap} more entries_ | | |")
    lines.append("")
    return "\n".join(lines)


def strip_fass_state(text: str) -> str:
    """Strip existing FASS frontmatter block + ## FASS section."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text
    fm, body = m.group(1), m.group(2)
    fm = FASS_FM_BLOCK_RE.sub("", fm)
    body = FASS_SECTION_RE.sub("", body)
    if not body.endswith("\n"):
        body += "\n"
    return f"---\n{fm}\n---\n{body}"


def write_fass(path: Path, agg: ProducerAgg) -> None:
    text = path.read_text(encoding="utf-8")
    text = strip_fass_state(text)
    m = FRONTMATTER_RE.match(text)
    if not m:
        return
    fm, body = m.group(1), m.group(2)
    new_block = build_fass_fm_block(agg)
    if re.search(r"^retailers:\s*$", fm, re.MULTILINE):
        fm = re.sub(r"(retailers:\n)", r"\1" + new_block, fm, count=1)
    else:
        # No retailers: key yet — append one.
        fm = fm.rstrip() + "\nretailers:\n" + new_block
    new_section = build_fass_section(agg)
    body = body.rstrip() + "\n\n" + new_section + "\n"
    path.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")


def strip_all(existing_slugs: set[str]) -> int:
    """First-pass wipe: strip every existing FASS state from all pages."""
    n = 0
    for slug in existing_slugs:
        path = WIKI_DIR / f"{slug}.md"
        original = path.read_text(encoding="utf-8")
        stripped = strip_fass_state(original)
        if stripped != original:
            path.write_text(stripped, encoding="utf-8")
            n += 1
    return n


def main() -> int:
    if not RAW_BULK.exists():
        print(f"Missing bulk TSV: {RAW_BULK}", file=sys.stderr)
        return 1
    if not RAW_CURATED.exists():
        print(f"Missing curated TSV: {RAW_CURATED}", file=sys.stderr)
        return 1

    existing_slugs = {p.stem for p in WIKI_DIR.glob("*.md")}

    bulk_rows = load_bulk(RAW_BULK)
    curated_rows = load_curated(RAW_CURATED)
    print(f"Loaded {len(bulk_rows)} bulk rows + {len(curated_rows)} curated rows")

    matched, unmatched = aggregate(bulk_rows, curated_rows, existing_slugs)
    print(f"Aggregated: {len(matched)} matched producers, {len(unmatched)} unmatched")

    wiped = strip_all(existing_slugs)
    print(f"Stripped old FASS state from {wiped} pages")

    for slug, agg in sorted(matched.items()):
        path = WIKI_DIR / f"{slug}.md"
        try:
            write_fass(path, agg)
        except Exception as e:
            print(f"  ERROR on {slug}: {e}", file=sys.stderr)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    unmatched_sorted = sorted(unmatched.items(), key=lambda kv: -kv[1].cuvee_count)
    matched_sorted = sorted(matched.items(), key=lambda kv: -kv[1].cuvee_count)

    lines = [
        "---",
        "type: ingest_report",
        "source: fass_tsv",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"bulk_rows: {len(bulk_rows)}",
        f"curated_rows: {len(curated_rows)}",
        f"matched_producers: {len(matched)}",
        f"unmatched_producers: {len(unmatched)}",
        "---",
        "",
        "# FASS ingest report (full rebuild)",
        "",
        f"Sources: `{RAW_BULK.relative_to(VAULT)}` + `{RAW_CURATED.relative_to(VAULT)}`.",
        f"Stripped FASS state from **{wiped}** existing producer pages, then re-wrote "
        f"FASS sections on **{len(matched)}** matched pages.",
        "",
        "Unmatched producers (below) are NOT auto-created — too much spelling "
        "variation in this retailer's data. To onboard one, add an entry to "
        "`FASS_ALIASES` in `scripts/ingest_fass.py` pointing to the desired wiki "
        "slug, then re-run.",
        "",
        f"## Matched ({len(matched)})",
        "",
        "| Slug | Name | Cuvées | Price range |",
        "|---|---|---:|---|",
    ]
    for slug, a in matched_sorted:
        pr = (f"${a.price_min:.0f}–${a.price_max:.0f}"
              if (a.price_min or a.price_max) else "—")
        lines.append(f"| `{slug}` | {a.name} | {a.cuvee_count} | {pr} |")

    lines += [
        "",
        f"## Unmatched ({len(unmatched)})",
        "",
        "| Name | Guess slug | Country | Region | Cuvées | Max $ |",
        "|---|---|---|---|---:|---:|",
    ]
    for slug, a in unmatched_sorted:
        lines.append(
            f"| {a.name} | `{slug}` | {a.country or '—'} | "
            f"{a.region or '—'} | {a.cuvee_count} | ${a.price_max:.0f} |"
        )

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {REPORT.relative_to(VAULT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
