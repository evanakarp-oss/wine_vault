"""
Tier 2 + alias-consolidation seed pass for FASS unmatched producers.

Follow-up to scripts/seed_fass_tier1.py after the 2026-05-26 triage. Adds:

- 1 Tier 1 miss (Alain Burguet — should have been in tier1)
- 1 Tier 1 upgrade after research (Jürgen von der Mark, MW)
- 9 Tier 2 producers with real prose (Vinding Montecarrubo, La Psigula,
  Cianfagna, Pircher, Louis Sozet, Rattalino, Achim Dürr, Weingut Riehen)
- 4 Tier 3 stubs (Tenuta Col Falco, Tomaso Gianolo, Le Petit Chateau,
  Daniel & Monika Marugg) — minimal prose but keeps them in the rollup
- 9 alias-consolidation roots (calafe, domaine_gallet, luyton, marc_jambon,
  vini_marino, cantina_del_signore, chateau_de_trinquevedel, wegelin,
  max_geitlinger)

After running this seeder, update FASS_ALIASES in scripts/ingest_fass.py
to point the spelling variants at these new slugs, then re-run the
pipeline: ingest_csw → ingest_fass → build_rollups → build_wiki_index.

Skipped here (true Tier 3 — generic mid-tier Bordeaux, single-bottle
obscure, broken split-row data):
- Vieux Chateau St. Andree / Chateau Samion / Chateau Bouillerot /
  Chateau Bonneau / Bellaria / Petra / La Chablisienne / JJ Morel /
  Cecllia Monte / Raphael Chopin / Giuseppe Negro / Vigneti Costacurta /
  Remy Nodin / J. Despesse / Domaine Grosbot-Barbara / Domaine St. Gayan /
  Domaine Michellas St Jemmes / Luna Beberide
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS_DIR = VAULT / "wiki" / "producers"


@dataclass
class P:
    slug: str
    name: str
    country: str
    region: str
    sub_region: str = ""
    appellations: list[str] = field(default_factory=list)
    farming: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    importer_us: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    summary: str = ""


PRODUCERS = [
    # ---- Tier 1 miss ----
    P(
        slug="alain_burguet",
        name="Domaine Alain Burguet",
        country="France", region="Burgundy", sub_region="Gevrey-Chambertin",
        appellations=["Gevrey-Chambertin AOC"],
        farming=["organic", "biodynamic"],
        importer_us=["Becky Wasserman & Co."],
        aliases=["Burguet", "Jean-Luc & Eric Burguet"],
        tags=["gevrey-chambertin", "vieilles-vignes", "biodynamic",
              "wasserman-discovery", "icon"],
        summary=(
            "Gevrey-Chambertin grower discovered by **Becky Wasserman around "
            "1982** (the kingmaker for grower Burgundy in the US). Alain "
            "started the domaine in 1974; his sons Jean-Luc and Eric took "
            "over winemaking in 2009. The vineyards have been **organic for "
            "35 years (since 1991) and biodynamic since 2011** — among the "
            "earliest biodynamic adopters in the Côte de Nuits. Mes "
            "Favorites Vieilles Vignes is the iconic cuvée: a selection from "
            "**18 parcels of vines planted 1910s–1970s**, 4.5 ha total. "
            "Triple-sorted, native yeast, destemmed, 20 months in barrel "
            "(30% new). Style is lifted, perfumed, dark-cherry-driven, "
            "supple. The 2016 and 2017 vintages of Mes Favorites in the "
            "FASS book at $58–$60 are absurdly underpriced for what they "
            "are — village-tier Gevrey from this domaine punches into the "
            "1er Cru tier of most négoce houses."
        ),
    ),
    # ---- Tier 1 upgrade ----
    P(
        slug="jurgen_von_der_mark",
        name="Weingut Jürgen von der Mark",
        country="Germany", region="Baden", sub_region="Tuniberg",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Jurgen Von der Mark", "Jürgen Von der Mark",
                 "Jurgen von der Mark"],
        tags=["baden", "spatburgunder", "pinot-noir", "master-of-wine",
              "tuniberg"],
        summary=(
            "**The first German to earn the Master of Wine (MW) title** "
            "(1996). Jürgen launched his own winery in 2003, focused on "
            "Spätburgunder on a 3-hectare leased Tuniberg parcel at the "
            "foothills of the Black Forest. The 'Lied' top-quality cuvée "
            "gets a new creative name every vintage — 'Krieger des Lichts' "
            "(Warrior of Light), 'Out in the Fields,' 'Thunderstruck,' 'I "
            "took a pill in Ibiza,' 'Bad Love.' Below that, the Engertstein "
            "single-parcel Spätburgunder and Je Marche Seul make up the "
            "middle tier. The 'Cuvée #001 Blanc de Noirs' (labeled as "
            "Champagne in the FASS data but actually a Baden traditional-"
            "method sparkling) is the sleeper. **A serious MW-led project, "
            "not a curiosity** — the wines reflect a critic-level palate "
            "designing for what he himself wants to drink."
        ),
    ),
    # ---- Tier 2 (real prose) ----
    P(
        slug="vinding_montecarrubo",
        name="Vinding Montecarrubo",
        country="Italy", region="Sicily",
        appellations=["Terre Siciliane IGT"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["sicily", "syrah", "vinding-diers", "extinct-volcano"],
        summary=(
            "Peter Vinding-Diers's Sicily project — Vinding-Diers is the "
            "Danish-born winemaker who co-founded **Royal Tokaji**, was the "
            "winemaker at Château Rahoul (Pessac-Léognan), and worked across "
            "Bordeaux, Tokaji, and South Africa before settling on Sicily. "
            "The Montecarrubo estate sits on an **extinct volcano between "
            "Syracuse and Catania**. **Cuvée Suzanne** (named for his wife) "
            "is the flagship — pure Syrah, expressive and structured. **Jancis "
            "Robinson covers the 2020 vintage on her tasting-note pages**; "
            "Decanter has a published review of the 2017. CellarTracker "
            "shows 91+ averages across recent vintages. The Quattro Venti "
            "is the larger-scale cuvée; both at $45–$50 in the FASS book."
        ),
    ),
    P(
        slug="la_psigula",
        name="La Psigula",
        country="Italy", region="Piedmont", sub_region="Alto Piemonte",
        appellations=["Bramaterra DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["alto-piemonte", "bramaterra", "biellese", "nebbiolo"],
        summary=(
            "Tiny new-generation Alto Piemonte estate in Curino, in the "
            "Biellese hills — founded by young winemaker Giacomo Foglia and "
            "his wife Claudia at the foot of an old tower (hence the "
            "'Vigna Torre' cru). Bramaterra DOC: the volcanic-porphyry "
            "Spanna/Croatina/Vespolina blend south of Gattinara. Bramaterra "
            "$46, Riserva Vigna Torre $74 — under-radar entry to the "
            "appellation alongside Tenuta Sella and Antoniolo."
        ),
    ),
    P(
        slug="cianfagna",
        name="Cianfagna",
        country="Italy", region="Abruzzo", sub_region="Molise",
        appellations=["Molise Aglianico DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Cian Fagna"],
        tags=["molise", "aglianico", "central-italy"],
        summary=(
            "Acquaviva Collecroce (Molise) family estate — Aglianico del "
            "Molise Riserva 'Militum Christi' (2013) at $39 and Sator Gran "
            "Maestro Riserva (2018) at $67. Molise is a small under-mapped "
            "south-central Italian region; Cianfagna is one of its quiet "
            "serious producers, with deep oak-age Aglianico in the Taurasi-"
            "adjacent style."
        ),
    ),
    P(
        slug="pircher",
        name="Pircher",
        country="Italy", region="Alto Adige / Südtirol",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["alto-adige", "stadtberg", "pinot-noir", "gewurztraminer"],
        summary=(
            "Pinot Noir-focused estate (data has it labeled both Italy and "
            "Switzerland in places, but the Stadtberg parcel reads as Alto "
            "Adige). The Stadtberg single-vineyard Pinot Noir at $48 "
            "(or $200 4-pack) is the headline; Gewürztraminer Eglisau at "
            "$46 the white. Small allocations."
        ),
    ),
    P(
        slug="louis_sozet",
        name="Louis Sozet",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["cornas", "syrah", "aged-cornas"],
        summary=(
            "Cornas grower at FASS only via the 2015 and 2016 vintages at "
            "$97–$102 — aged-stock release window. Old-school Cornas, "
            "minimal new oak. The 2016 specifically appears in multiple "
            "FASS allocations, suggesting a librairie release rather than "
            "current-vintage supply."
        ),
    ),
    P(
        slug="rattalino",
        name="Rattalino",
        country="Italy", region="Piedmont",
        appellations=["Barolo DOCG", "Barbaresco DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["barolo", "barbaresco", "selection-numbered"],
        summary=(
            "Piedmont producer with a numbered 'Selection' series — Barolo "
            "Selection 34 (2013), Barolo Selection 35 Bussia (2014), "
            "Barbaresco Riserva Sel. 45 (2016). The Bussia cru in Barolo "
            "and the numbered-selection format suggests parcelaire bottlings "
            "from a négoce structure; the 2013/2014 vintages at $41–$58 "
            "are aged stock."
        ),
    ),
    P(
        slug="achim_durr",
        name="Weingut Achim Dürr",
        country="Germany", region="Baden",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Achim Duerr", "Achim-Durr", "Weingut Achim Durr",
                 "Achim Durr"],
        tags=["baden", "spatburgunder", "blaufrankisch", "syrah",
              "cabernet-franc"],
        summary=(
            "Baden Pinot Noir grower with an unusually broad Bordeaux- "
            "and Austria-leaning varietal range: Pinot Noir 'Tom,' Pinot "
            "Noir Hard 200, Pinot Noir Vom Keuper, Blaufränkisch "
            "(Lemberger) 'Vom Keuper' — same Vom Keuper site for both Pinot "
            "and Blaufränkisch — plus Cabernet Franc and Syrah. The Vom "
            "Keuper site name is shared with Sven Enderle's bottling — "
            "same Keuper geological formation across Baden / Württemberg. "
            "Sub-$50 across the book."
        ),
    ),
    P(
        slug="weingut_riehen",
        name="Weingut Riehen",
        country="Switzerland", region="Basel-Land",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["switzerland", "basel-land", "pinot-noir", "chardonnay",
              "cidre"],
        summary=(
            "Basel-Land producer — Le Grand Chardonnay 2015 ($86) and Le "
            "Grand Pinot Noir 2021 ($94) at the top; Le Petit Blanc + Le "
            "Petit Rouge at the entry level. The unique offer is **Le "
            "Cidre Riechner Epfel Basel-Stadt**, a late-disgorged apple "
            "cider made in the méthode traditionnelle ($39–$51) — extremely "
            "rare in US import."
        ),
    ),
    # ---- Tier 3 stubs (in the rollup, but minimal prose) ----
    P(
        slug="tenuta_col_falco",
        name="Tenuta Col Falco",
        country="Italy", region="Umbria",
        appellations=["Montefalco Rosso DOC", "Sagrantino di Montefalco DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["umbria", "montefalco", "sagrantino"],
        summary=(
            "Montefalco grower — Sagrantino di Montefalco $30, Montefalco "
            "Rosso $20, plus a Sagrantino Rosso Passito 500ml dessert. "
            "Value-tier Umbria. Sagrantino is one of Italy's most tannic "
            "natives; this is the entry-price introduction."
        ),
    ),
    P(
        slug="tomaso_gianolo",
        name="Tomaso Gianolo",
        country="Italy", region="Piedmont",
        appellations=["Barolo DOCG", "Barbaresco DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["barolo", "barbaresco", "value-piedmont"],
        summary=(
            "Sub-$35 Barolo and Barbaresco from a small négoce-grower. "
            "Entry-level Langhe Nebbiolo for under-$40 budget; not a "
            "single-cru / single-vineyard play."
        ),
    ),
    P(
        slug="le_petit_chateau",
        name="Le Petit Château",
        country="Switzerland", region="Vully",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["switzerland", "vully", "pinot-noir"],
        summary=(
            "Vully (Swiss French-speaking region between Lake Murten and "
            "Lake Neuchâtel) — Pinot Noir Selection $35–$37. The only "
            "Vully entry in the FASS book; small, niche."
        ),
    ),
    P(
        slug="daniel_and_monika_marugg",
        name="Daniel and Monika Marugg",
        country="Switzerland", region="Graubünden",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["switzerland", "graubunden", "chardonnay", "merlot"],
        summary=(
            "Small Bündner Herrschaft estate — Chardonnay and a Merlot/"
            "Malbec blend at $41–$44. Off the main Pinot-Noir focus of "
            "Graubünden — interesting curiosity."
        ),
    ),
    # ---- Alias consolidation roots (brief stubs, the spelling variants
    # point here via FASS_ALIASES) ----
    P(
        slug="calafe",
        name="Calafe",
        country="Italy", region="Campania",
        appellations=["Taurasi DOCG", "Greco di Tufo DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["CaLaFe Ariavecchia", "Calafe Ariavecchia"],
        tags=["campania", "taurasi", "aglianico", "greco-di-tufo"],
        summary=(
            "Campania producer — Taurasi $37 (Aglianico) and Greco di Tufo "
            "Ariavacchia / Ariavecchia $35 (single-vineyard Greco). "
            "Under-radar entry to Campania's two top DOCG denominations."
        ),
    ),
    P(
        slug="domaine_gallet",
        name="Domaine Gallet",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        appellations=["Côte-Rôtie AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Henri Gallet"],
        tags=["cote-rotie", "syrah", "grower"],
        summary=(
            "Côte-Rôtie grower — Côte-Rôtie 2022 at $51 (Henri Gallet "
            "spelling variant carries the 2023 at $61) plus a VDF Cuvée "
            "Gallet Jade at $26. Small estate; the basic Côte-Rôtie at "
            "$51 is the value entry to the appellation."
        ),
    ),
    P(
        slug="luyton",
        name="Luyton",
        country="France", region="Rhône", sub_region="Hermitage",
        appellations=["Hermitage AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Michelle Luyton"],
        tags=["hermitage", "syrah"],
        summary=(
            "Hermitage Rouge at $62–$66 — small allocation. Sub-$70 "
            "Hermitage Rouge is rare even in the négoce tier."
        ),
    ),
    P(
        slug="marc_jambon",
        name="Marc Jambon",
        country="France", region="Burgundy", sub_region="Mâcon",
        appellations=["Mâcon-Pierreclos AOC", "Bourgogne Aligoté AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["DOMAINE MARC JAMBON ET FILS", "Marc Jambon Et Fils"],
        tags=["maconnais", "macon-pierreclos", "aligote"],
        summary=(
            "Mâconnais grower — Mâcon-Pierreclos 'La Fossile' at $34, plus "
            "a Bourgogne Aligoté at $21 and a Macon Pierriclos Le Carruge. "
            "Sub-$40 Mâconnais grower in the Lafon-stylistic neighborhood."
        ),
    ),
    P(
        slug="vini_marino",
        name="Vini Marino — Proclamo Cilento",
        country="Italy", region="Campania", sub_region="Cilento",
        appellations=["Cilento DOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Vini Marino Proclamo Cilento"],
        tags=["campania", "cilento", "aglianico", "fiano"],
        summary=(
            "Cilento (southern Campania, coastal) producer — Cilento "
            "Aglianico Riserva (2008 / 2016 vintages, $48–$81) and Fiano "
            "Vendemmia Tardiva (2024, $31–$34). Aged Cilento Aglianico is "
            "unusual at retail."
        ),
    ),
    P(
        slug="cantina_del_signore",
        name="Cantina del Signore",
        country="Italy", region="Piedmont",
        appellations=["Gattinara DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Cantina Del", "Cascina DelSignore"],
        tags=["alto-piemonte", "gattinara", "nebbiolo",
              "metodo-classico-rose"],
        summary=(
            "Alto Piemonte producer — Gattinara 'Il Putto' 2020 at $49 "
            "plus Rosé Metodo Classico Extra Dry Millesimato 2018/2022/2023. "
            "Gattinara is the most famous of the Alto Piemonte DOCGs "
            "(volcanic porphyry Spanna); the rosé sparkling is an unusual "
            "side project."
        ),
    ),
    P(
        slug="chateau_de_trinquevedel",
        name="Château de Trinquevedel",
        country="France", region="Rhône", sub_region="Tavel",
        appellations=["Tavel AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Château de", "Chateau de Trinquevedel"],
        tags=["tavel", "rose", "grenache"],
        summary=(
            "Tavel rosé producer — 'Les Vignes d'Eugène' 2023 at $37–$41. "
            "Tavel is the only French AOC dedicated entirely to rosé; "
            "Trinquevedel is a long-tenured estate making the structured, "
            "food-oriented, dark-pink style."
        ),
    ),
    P(
        slug="wegelin",
        name="Wegelin Weine AG",
        country="Switzerland", region="Eastern Switzerland",
        sub_region="Graubünden",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Wegelin Weisstorkel", "Weggelin"],
        tags=["switzerland", "graubunden", "blauburgunder", "pinot-noir"],
        summary=(
            "Eastern Switzerland producer — Weisstorkel Blauburgunder "
            "(Pinot Noir) at $52–$56, Bothmarhalde Blauburgunder at $52. "
            "BIO-certified. Different domaine spelling variants in the raw "
            "data (Wegelin Weine AG / Wegelin Weisstorkel / Weggelin) all "
            "refer to this estate."
        ),
    ),
    P(
        slug="max_geitlinger",
        name="Max Geitlinger",
        country="Germany", region="Baden",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Max Geitlinger Wein"],
        tags=["baden", "merlot", "muller-thurgau"],
        summary=(
            "Baden grower — Merlot 2022 at $38 and a Maximal Müller "
            "(Müller-Thurgau) at $29. Off the main Baden Pinot focus; "
            "small production."
        ),
    ),
]


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def render(p: P) -> str:
    return f"""---
type: producer
name: "{p.name}"
slug: {p.slug}
aliases: {yaml_list(p.aliases)}
country: "{p.country}"
region: "{p.region}"
sub_region: "{p.sub_region}"
appellations: {yaml_list(p.appellations)}
farming: {yaml_list(p.farming)}
certifications: {yaml_list(p.certifications)}
importer_us: {yaml_list(p.importer_us)}
retailers:
  chambers:
    championed: false
    article_count: 0
    dedicated_count: 0
    first_year: 0
    last_year: 0
  dte:
    in_portfolio: false
  raeders:
    in_portfolio: false
tags: {yaml_list(p.tags)}
_sources: ["fass_tsv:portfolio_2026-05-26"]
---

# {p.name}

{p.summary}

## CSW Write-ups

_Not yet populated._

## FASS

_Not yet populated._

## Cellar

_None._

## Cross-references

- [[{p.region}_Producers|{p.region}]]
- [[FASS_Selections|FASS Selections (retailer)]]
"""


def main() -> int:
    PRODUCERS_DIR.mkdir(parents=True, exist_ok=True)
    created = skipped = 0
    for p in PRODUCERS:
        path = PRODUCERS_DIR / f"{p.slug}.md"
        if path.exists():
            skipped += 1
            continue
        path.write_text(render(p), encoding="utf-8")
        created += 1
    print(f"Seeded {created} new Tier 2 / alias-consolidation pages, skipped {skipped} existing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
