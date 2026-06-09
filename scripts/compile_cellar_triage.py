"""
compile_cellar_triage.py — LLM-judgment pass over cellar producers without
wiki pages (2026-06 triage; decision table curated by Claude applying Evan's
CLAUDE.md taste filters, with cellar context from cellar/*.md).

Buckets — every missing slug appears in exactly ONE:

  CREATE   — taste-fit or significant holding: seed a producer page
             (`status: seeded`, conservative summary; editorial coverage
             arrives later via ingest_csw / clippings / Raeders passes).
  NO_PAGE  — deliberately skipped: anti-taste (cult-hedonist Napa, generic
             négoce/mid-tier) or trivial one-off holdings. Recorded so the
             gap stops looking like a gap.
  REVISIT  — plausible keepers needing more info or a taxonomy addition;
             parked for a future pass with Evan.

Idempotent: existing pages are never overwritten. Output:
  wiki/producers/<slug>.md      (CREATE bucket, if missing)
  wiki/_views/cellar_triage_2026_06.md   (full decision record)

Run AFTER: nothing. Run BEFORE: link_cellar.py, ingest_csw.py,
build_rollups.py, build_views.py, build_home.py, build_wiki_index.py.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CELLAR = VAULT / "cellar"
PRODUCERS = VAULT / "wiki" / "producers"
VIEW_OUT = VAULT / "wiki" / "_views" / "cellar_triage_2026_06.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def g(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


# slug → (name, country, region, sub_region, farming[], importer_us[],
#          aliases[], summary)
CREATE: dict[str, tuple] = {
    # --- United States ---
    "ceritas": ("Ceritas", "United States", "California", "Sonoma Coast", [], [], ["Ceritas Wines"],
        "John and Phoebe Raytek's Sonoma Coast label — site-driven, early-picked Chardonnay and Pinot Noir "
        "from cool coastal parcels, made in a restrained, mineral register. The cellar also holds their rare "
        "Peter Martin Ray Cabernet (Santa Cruz Mountains) — squarely the tension/sense-of-place axis."),
    "beta": ("Beta Wines", "United States", "California", "", [], [], ["Beta"],
        "Single-vineyard California Cabernet project; the cellar holds Vare Vineyard bottlings across "
        "2015–2021 (16 bottles — one of the larger un-paged holdings). Identity/farming detail to confirm."),
    "santa_cruz_mountain_vineyard": ("Santa Cruz Mountain Vineyard", "United States", "California",
        "Santa Cruz Mountains", [], [], ["SCMV"],
        "Historic Santa Cruz Mountains estate (founded 1970s), now under Jeff Emery — structured, old-school "
        "mountain Cabernet and Pinot from sites like Bates Ranch. The Monte Bello / rugged-terroir axis at "
        "a fraction of the price."),
    "sandar_hem": ("Sandar & Hem", "United States", "California", "Santa Cruz Mountains", [], [], [],
        "Young Santa Cruz Mountains label focused on single-vineyard mountain Cabernet (Bates Ranch). "
        "Same rugged-SCM orbit as Santa Cruz Mountain Vineyard — cross-shop the two."),
    "renaissance": ("Renaissance Vineyard & Winery", "United States", "California", "Sierra Foothills (North Yuba)",
        ["organic"], [], [],
        "Legendary high-elevation, dry-farmed North Yuba estate; long-aging, low-alcohol mountain Cabernet "
        "and Syrah (Gideon Beinstock made the benchmark vintages before founding Clos Saron). The cellar's "
        "2000–2001 bottles are exactly the aged, terroir-driven California the taste filter wants."),
    "ridge": ("Ridge Vineyards", "United States", "California", "Santa Cruz Mountains", ["sustainable"], [],
        ["Ridge", "Ridge Monte Bello"],
        "Reference producer — Monte Bello is named in the cellar taste filter as the Santa Cruz Mountains "
        "benchmark. Pre-industrial winemaking, transparent site expression. Cellar currently holds only the "
        "Three Valleys field blend; Monte Bello (or Estate Cab) is the gap to fill."),
    "williams_selyem": ("Williams Selyem", "United States", "California", "Russian River Valley", [], [], [],
        "Pioneering Russian River Pinot Noir house (Burt Williams & Ed Selyem); single-vineyard bottlings "
        "with cult demand but grower-scale roots. Cellar holds aged 2009s — drink-window attention needed."),
    "vincent": ("Vincent Wine Company", "United States", "Oregon", "Willamette Valley", [], [], ["Vincent"],
        "Vincent Fritzsche's small Willamette Valley label — single-vineyard Pinot Noir (Armstrong, Zenith, "
        "Cortell-Rose) in a modest, low-extraction style. Not to be confused with Vincent Paris (Cornas)."),

    # Taste-filter reference producers (NOT cellar holdings — the CLAUDE.md
    # Napa reference set; CSW coverage exists in raw/, pages were missing):
    "dunn_vineyards": ("Dunn Vineyards", "United States", "California", "Howell Mountain", [], [],
        ["Dunn", "Randy Dunn", "Dunn Howell Mountain"],
        "Randy (now Mike) Dunn's Howell Mountain estate — tannic, low-alcohol, decades-aging mountain "
        "Cabernet that defines the rugged/farming-driven axis in the cellar taste filter. Reference "
        "producer: not yet in the cellar; a buy-list priority."),
    "corison": ("Corison", "United States", "California", "St. Helena", [], [],
        ["Cathy Corison", "Corison Winery"],
        "Cathy Corison's St. Helena benchwork — restrained, age-worthy Napa Cabernet (Kronos Vineyard) "
        "made against the opulent tide since 1987. Reference producer in the taste filter; not yet in "
        "the cellar."),

    # --- Burgundy / Beaujolais ---
    "maison_pierre_brisset": ("Maison Pierre Brisset", "France", "Burgundy", "Beaune", [], [], ["Pierre Brisset"],
        "Micro-négoce run by Pierre Brisset — small-lot Côte de Beaune and Côte de Nuits cuvées from "
        "organically farmed purchased fruit. 16 bottles in cellar across Pommard 1er, Bourgogne rouge/blanc."),
    "marcel_lapierre": ("Marcel Lapierre", "France", "Beaujolais", "Morgon", ["organic", "natural"],
        ["Kermit Lynch"], ["Lapierre"],
        "The founding house of natural Beaujolais — Marcel Lapierre (now Mathieu & Camille) made Morgon the "
        "proof that sans-soufre wine could be profound. Whole-cluster, old-vine Gamay of place."),
    "jean_foillard": ("Jean Foillard", "France", "Beaujolais", "Morgon (Côte du Py)", ["organic", "natural"],
        ["Kermit Lynch"], ["Foillard"],
        "Gang-of-Four Morgon master; Côte du Py is the benchmark for structured, age-worthy natural "
        "Beaujolais. Cellar holds the Eponym' cuvée."),
    "domaine_diochon": ("Domaine Diochon", "France", "Beaujolais", "Moulin-à-Vent", [], ["Kermit Lynch"], ["Diochon"],
        "Old-school Moulin-à-Vent — traditional semi-carbonic, old vines, wines that age like Burgundy. "
        "The cellar's 2003 Vieilles Vignes is a drink-now proof of concept."),
    "jacques_frederic_mugnier": ("Jacques-Frédéric Mugnier", "France", "Burgundy", "Chambolle-Musigny",
        [], [], ["J.-F. Mugnier", "Frédéric Mugnier"],
        "Chambolle at its most ethereal; the Nuits-Saint-Georges Clos de la Maréchale (monopole, in cellar) "
        "is William Kelley's canonical value call — 'amazing that it isn't more expensive' (see "
        "raeders_burgundy_value_picks_2026_06)."),
    "domaine_bruno_clair": ("Domaine Bruno Clair", "France", "Burgundy", "Marsannay", [], [], ["Bruno Clair"],
        "Classicist Marsannay-based domaine with holdings up and down the Côte (Clos de Bèze to Savigny "
        "La Dominode). Village Marsannay (in cellar) is the value entry to a serious old-school address."),
    "domaine_des_croix": ("Domaine des Croix", "France", "Burgundy", "Beaune", [], [], ["David Croix"],
        "David Croix's small Beaune domaine — precise, infusion-style reds from underrated Beaune 1ers "
        "(Cent-Vignes in cellar). Fits the Kelley 'quiet appellation, serious grower' value move."),
    "chateau_de_la_maltroye": ("Château de la Maltroye", "France", "Burgundy", "Chassagne-Montrachet", [], [], ["Maltroye"],
        "Chassagne estate with prime red holdings — the cellar's Clos St-Jean Rouge 1er is a direct play on "
        "Kelley's 'Chassagne rouge is the value blind spot' thesis."),
    "yann_durieux": ("Yann Durieux", "France", "Burgundy", "Hautes-Côtes de Nuits", ["natural"], [], [],
        "Prieuré-Roch alumnus making cult natural Burgundy (Recrue des Sens) in the Hautes-Côtes; "
        "Vin-de-France-labeled cuvées like Love and Pif (in cellar). High-variance, high-ceiling."),
    "domaine_florent_garaudet": ("Domaine Florent Garaudet", "France", "Burgundy", "Monthélie", [], [], ["Florent Garaudet"],
        "Young grower in Monthélie working old family vines; the Pommard Vieilles Vignes in cellar is the "
        "calling card. Grower-scale Côte de Beaune value."),
    "domaine_armand_rousseau_pere_et_fils": ("Domaine Armand Rousseau", "France", "Burgundy", "Gevrey-Chambertin",
        [], [], ["Armand Rousseau", "Rousseau"],
        "Gevrey-Chambertin's first family — Chambertin and Clos de Bèze define the appellation's ceiling. "
        "The cellar holds a 2017 Clos de la Roche; a top WB-top-100 name and the Burgundy reference point "
        "for everything else in the cellar."),

    # --- Rhône ---
    "mickael_bourg": ("Mickaël Bourg", "France", "Rhône", "Cornas", [], [], ["Mickael Bourg"],
        "Small-production Cornas vigneron (Les P'tits Bouts, 12 bottles in cellar) — hand-worked granite "
        "terraces, artisan scale. Editorial coverage pending."),
    "remy_nodin": ("Rémy Nodin", "France", "Rhône", "Saint-Péray / Cornas", [], [], ["Remy Nodin"],
        "Saint-Péray-based grower; the cellar holds his Cornas Les Eygats. Artisan northern-Rhône Syrah "
        "from a name still under the radar."),
    "louis_sozet": ("Louis Sozet", "France", "Rhône", "Cornas", [], [], [],
        "Small Cornas bottling — three bottles of the 2016 in cellar. Identity and farming detail to "
        "confirm; seeded from cellar holdings."),
    "domaine_du_tunnel_stephane_robert": ("Domaine du Tunnel (Stéphane Robert)", "France", "Rhône",
        "Saint-Péray / Cornas", [], [], ["Domaine du Tunnel", "Stéphane Robert"],
        "Stéphane Robert's Saint-Péray estate with strong Cornas holdings; Vin Noir (in cellar) is the "
        "dense, old-vine flagship. Polished but site-true northern Rhône."),

    # --- Loire / Alsace / Champagne ---
    "domaine_philippe_tessier": ("Domaine Philippe Tessier", "France", "Loire", "Cheverny", ["organic", "biodynamic"],
        [], ["Philippe Tessier"],
        "Benchmark biodynamic Cheverny — Romorantin (Cour-Cheverny) and chalk-fresh blends at artisan "
        "prices. Seven bottles across three cuvées in cellar."),
    "albert_boxler": ("Albert Boxler", "France", "Alsace", "Niedermorschwihr", [], [], ["Boxler"],
        "Grand-cru Alsace grower (Sommerberg, Brand) — chiseled, age-worthy Riesling at grower scale. "
        "The cellar's 2012 Brand is in its drinking window."),
    "etienne_calsac": ("Étienne Calsac", "France", "Champagne", "Avize (Côte des Blancs)", ["organic"], [],
        ["Etienne Calsac"],
        "Young grower in Avize farming organically on lieu-dit parcels; L'Échappée Belle (in cellar) is the "
        "blanc-de-blancs entry. Squarely the grower-Champagne filter."),
    "chartogne_taillet": ("Chartogne-Taillet", "France", "Champagne", "Merfy (Massif de Saint-Thierry)", [], [],
        ["Chartogne Taillet", "Alexandre Chartogne"],
        "Alexandre Chartogne's parcel-driven grower estate — Cuvée Sainte-Anne (in cellar) is one of the "
        "category's reference entry wines; the lieu-dit bottlings reward chasing."),

    # --- Bordeaux / Southwest ---
    "chateau_guiraud": ("Château Guiraud", "France", "Bordeaux", "Sauternes", ["organic"], [], ["Guiraud"],
        "Premier cru classé Sauternes and the first 1855 classified growth certified organic — great "
        "farming + classed-growth pedigree, the exact Bordeaux filter. Cellar holds the 2009."),
    "chateau_clerc_milon": ("Château Clerc Milon", "France", "Bordeaux", "Pauillac", [], [], ["Clerc Milon"],
        "Pauillac fifth growth in the Mouton-Rothschild stable; the cellar's 2005 is mature classed-growth "
        "claret — the drink-now Bordeaux lane."),
    "chateau_grand_corbin_despagne": ("Château Grand Corbin-Despagne", "France", "Bordeaux", "Saint-Émilion",
        ["organic"], [], ["Grand Corbin-Despagne"],
        "Family-run Saint-Émilion grand cru, organic-certified — undercovered, value-priced, farming-first. "
        "A WK-style right-bank pick."),
    "clos_de_gamot": ("Clos de Gamot", "France", "South West", "Cahors", [], [], [],
        "The Jouffreau family's historic Cahors estate — centenarian Malbec vines, traditional long-aging "
        "style. Old-school Southwest value with real cellar pedigree."),

    # --- Germany ---
    "a_christmann": ("A. Christmann", "Germany", "Pfalz", "Königsbach (Mittelhaardt)", ["biodynamic"], [],
        ["Weingut A. Christmann", "Christmann"],
        "VDP-president estate, biodynamic Mittelhaardt benchmark; Idig GG (in cellar) is its grand cru. "
        "Core German-biodynamic taste fit."),
    "julian_haart": ("Julian Haart", "Germany", "Mosel", "Piesport", [], [], [],
        "Tiny Piesport estate (Keller/Egon Müller alumnus) — precise, featherweight Mosel Riesling from "
        "Goldtröpfchen and Schubertslay parcels. Note: CT export mis-files the locale as Rheinhessen."),
    "ziereisen": ("Ziereisen", "Germany", "Baden", "Efringen-Kirchen (Markgräflerland)", [], [], ["Hanspeter Ziereisen"],
        "Hanspeter Ziereisen's Markgräflerland estate — Jura-influenced Spätburgunder and Chardonnay "
        "(Jaspis line, in cellar) raised in old wood, bottled unfined. Baden artisan benchmark."),
    "dr_wehrheim": ("Dr. Wehrheim", "Germany", "Pfalz", "Birkweiler (Südpfalz)", ["organic"], [], ["Weingut Dr. Wehrheim"],
        "Südpfalz VDP estate on the Rosenberg/Kastanienbusch slopes — limestone Chardonnay and Weissburgunder "
        "of real tension. Organic farming, grower scale."),
    "gut_hermannsberg": ("Gut Hermannsberg", "Germany", "Nahe", "Niederhausen", [], [], [],
        "The former Prussian state domaine's monopole heart of the Nahe — stony, smoke-tinged GG Riesling. "
        "Cellar holds the 2019 Hermannsberg GG Reserve."),
    "jonas_dostert": ("Jonas Dostert", "Germany", "Mosel", "Nittel (Obermosel)", ["natural"], [], [],
        "Rising Obermosel natural winemaker on limestone (not slate) — Elbling and Burgunder varieties, "
        "long élevage, minimal sulfur. The new-Mosel avant-garde."),
    "weingut_thorle": ("Weingut Thörle", "Germany", "Rheinhessen", "Saulheim", [], [], ["Thörle", "Thorle"],
        "Brothers Christoph & Johannes Thörle in Saulheim — limestone Spätburgunder (Hölle, in cellar ×12) "
        "and Riesling that rival names twice the price. Rheinhessen's quiet overachiever."),
    "juliane_eller": ("Juliane Eller (JuWel)", "Germany", "Rheinhessen", "Alsheim", [], [], ["JuWel", "Juliane Eller"],
        "Juliane Eller's JuWel estate in Alsheim — 16 bottles of Frühmesse Riesling in cellar, one of the "
        "largest un-paged holdings. Clean, precise Rheinhessen at fair prices."),
    "achim_durr": ("Achim Dürr", "Germany", "Baden", "", [], [], ["Achim Durr"],
        "Baden Pinot Noir grower (cuvée 'Tom', 4 bottles in cellar). Identity and farming detail to "
        "confirm; seeded from cellar holdings."),

    # --- Italy ---
    "ar_pe_pe": ("ARPEPE", "Italy", "Lombardy", "Valtellina", [], [], ["Ar.Pe.Pe.", "Arpepe"],
        "The Pelizzatti Perego family's Valtellina benchmark — long-macerated, decade-aging Nebbiolo from "
        "terraced alpine granite (Grumello, Inferno riservas in cellar). Mountain terroir at its purest."),
    "ronchi_di_cialla": ("Ronchi di Cialla", "Italy", "Friuli-Venezia Giulia", "Colli Orientali (Cialla)", [], [],
        ["Cialla"],
        "The Rapuzzi family estate that saved Schioppettino from extinction; varietal native reds "
        "(Refosco, Schioppettino) that age 20+ years. Cellar holds a deep 1998–1999 vertical — 15 bottles."),
    "le_due_terre": ("Le Due Terre", "Italy", "Friuli-Venezia Giulia", "Colli Orientali (Prepotto)", [], [], [],
        "Flavio & Silvana Basilicata's tiny Prepotto estate — Sacrisassi Rosso/Bianco (in cellar) are "
        "benchmark Colli Orientali blends. Artisan Friuli at its most soulful."),
    "radikon": ("Radikon", "Italy", "Friuli-Venezia Giulia", "Oslavia (Collio)", ["natural"], [], ["Stanko Radikon"],
        "Oslavia first family of skin-contact Ribolla — Stanko Radikon defined the orange-wine canon; "
        "son Saša continues. The 2008 Ribolla in cellar is the style at maturity."),
    "dario_princic": ("Dario Prinčič", "Italy", "Friuli-Venezia Giulia", "Oslavia (Collio)", ["natural"], [],
        ["Dario Princic"],
        "Oslavia natural-wine elder alongside Radikon and Gravner — amber Trebez blend (in cellar), long "
        "macerations, zero makeup. Core Friuli taste fit."),
    "i_vigneri_di_salvo_foti": ("I Vigneri di Salvo Foti", "Italy", "Sicily", "Etna", ["organic"], [],
        ["I Vigneri", "Salvo Foti"],
        "Salvo Foti's grower collective reviving alberello viticulture on Etna — old-vine Carricante and "
        "Nerello farmed by the I Vigneri crew. The island's most principled project."),
    "olek_bondonio": ("Olek Bondonio", "Italy", "Piedmont", "Barbaresco (Roncagliette)", [], [], [],
        "One-man Barbaresco estate on the Roncagliette cru (12 bottles in cellar) — old-school, "
        "small-batch Nebbiolo plus oddball Grignolino. Artisan Piedmont exactly to taste."),
    "flavio_roddolo": ("Flavio Roddolo", "Italy", "Piedmont", "Monforte d'Alba", [], [], ["Roddolo"],
        "Hermit-traditionalist of Monforte — Barolo, Barbera and the cult Bricco Appiani Cabernet (in "
        "cellar) from a tiny cantina, released late, built to age."),
    "antonio_vallana_e_figlio": ("Antonio Vallana e Figlio", "Italy", "Piedmont", "Alto Piemonte (Boca)", [], [],
        ["Vallana"],
        "Historic Alto Piemonte house famous for impossibly age-worthy Spanna; the Bernardo Vallana cuvée "
        "and Boca (in cellar) carry the torch. Aged-Nebbiolo value lane."),
    "giacomo_borgogno_figli": ("Borgogno", "Italy", "Piedmont", "Barolo", [], [], ["Giacomo Borgogno & Figli"],
        "Barolo's oldest continuous cellar (1761) — traditional riservas with deep library releases. "
        "Cellar holds the 2012 Riserva Cannubi."),
    "san_leonardo": ("Tenuta San Leonardo", "Italy", "Trentino", "Vallagarina", [], [], ["San Leonardo"],
        "The Guerrieri Gonzaga estate's claret-styled San Leonardo — Italy's most Bordeaux-classicist red, "
        "alpine freshness over power. Cellar's 1999 is mature and in window."),
    "tenuta_san_guido": ("Tenuta San Guido", "Italy", "Tuscany", "Bolgheri", [], [], ["Sassicaia"],
        "Sassicaia's estate — the original Bolgheri Cabernet, classical and cedar-toned rather than "
        "opulent. Cellar holds the 2015; cross-reference San Leonardo for the alpine sibling."),
    "paolo_bea": ("Paolo Bea", "Italy", "Umbria", "Montefalco", ["organic", "natural"], [], ["Bea"],
        "Giampiero Bea's Montefalco estate — the natural-wine reference for Sagrantino and Umbrian rosso "
        "(Rosso de Véo in cellar). Patient, unfiltered, profound."),

    # --- Austria / Spain / Czech ---
    "franz_hirtzberger": ("Franz Hirtzberger", "Austria", "Niederösterreich", "Wachau (Spitz)", [], [], ["Hirtzberger"],
        "Wachau royalty — Singerriedel Smaragd Riesling (the cellar's 1997 is a mature trophy) from steep "
        "Spitz terraces. Aged Austrian Riesling at reference level."),
    "envinate": ("Envínate", "Spain", "Canary Islands", "Tenerife (also Ribeira Sacra, Almansa)", [], [], ["Envinate"],
        "Four-friend project mining Atlantic Spain — volcanic Tenerife Listán (La Santa, in cellar), "
        "Ribeira Sacra Mencía. Hand-farmed parcels, ambient ferments; modern Spain's terroir benchmark."),
    "milan_nestarec": ("Milan Nestarec", "Czech Republic", "Moravia", "", ["natural"], [], ["Nestarec"],
        "Moravia's natural-wine star — pét-nats and skin-contact whites (Umami in cellar) with real "
        "precision under the funk. The Czech entry in the cellar's natural axis."),
}

# slug → reason (deliberate skip, recorded so the gap stops looking like one)
NO_PAGE: dict[str, str] = {
    "de_negoce": "bulk négoce label (Cameron Hughes model) — anti-taste despite 24-bottle holding; drink, don't study",
    "chateau_prieure_lichine": "generic mid-tier classed Bordeaux, young vintage — filter says skip",
    "chene_bleu": "luxury-branded Ventoux rosé — generic for taste",
    "chateau_de_pinet_gaujal_de_saint_bon": "everyday Picpoul — no editorial value",
    "beau_vigne": "cult-hedonist Napa tier — explicit filter skip",
    "bodega_catena_zapata": "generic-tier per existing filter decision (2026-05); Adrianna parcels noted but house style is the objection",
    "gargiulo_vineyards": "polished Oakville style, not the rugged/farming-driven axis",
    "paul_lato": "opulent Santa Barbara cult-adjacent — filter skip",
    "stewart": "Beckstoffer-fruit Napa luxe — filter skip",
    "jasud_estate": "cult-priced Napa boutique, no taste fit",
    "vina_cobos": "Paul Hobbs' modern-opulent Mendoza — Argentina filter wants artisan/biodynamic",
    "blankiet_estate": "Napa luxe estate — filter skip",
    "andremily": "SQN-school syrah — explicit filter skip",
    "antinori": "big-house Tuscany (Tignanello) — drink-now holding, no page needed",
    "bouchard_pere_et_fils": "négoce-generic per existing view decisions",
    "bodegas_muga": "big-house Rioja — generic mid-tier",
    "scopa": "generic Pinot Grigio one-off",
    "shafer": "Hillside Select = opulent Napa tier — filter skip",
    "dana_estates": "cult Napa — filter skip",
    "paul_hobbs": "modern-opulent Napa — filter skip",
    "bevan_cellars": "cult Napa — filter skip",
    "marcassin": "cult-hedonist chardonnay — filter skip",
    "favia": "cult-adjacent Napa — filter skip",
    "bond": "Harlan stable — explicit filter skip",
    "joseph_drouhin": "large négoce — single aged bottle, drink and enjoy",
    "domaine_william_fevre": "large-house Chablis, single bottle in window",
    "pierre_ponnelle": "defunct négoce, single 1983 bottle — drink now",
    "pierre_sparr": "négoce Alsace one-off",
    "jenny_francois": "importer house label (La Patience) — context lives on the Jenny & François importer page",
    "chateau_de_peyrassol": "rosé one-off",
    "chateau_les_mesclances": "rosé one-off",
    "the_colonial_estate": "aged Barossa one-off, outside interest areas",
    "amavi_cellars": "Walla Walla one-off",
    "swick_wines": "Oregon natural négoce one-off",
    "leo_steen": "single chenin one-off",
    "esteban_celemin": "Castilla mesa one-off",
    "pocas": "single colheita port",
    "portugal_boutique_winery": "branded-négoce one-off",
    "hugo_mendes": "single-bottle Lisboa one-off",
    "marcio_lopes": "single-bottle Douro one-off",
    "domaine_santamaria": "Corsica boutanche one-off",
    "harm": "single Kremstal bottle",
    "romano_dal_forno": "icon, but opulent Amarone is outside the interest areas — single bottle",
    "kmetija_hedele": "Slovenia one-off (taxonomy gap not worth opening for 2 bottles)",
    "dalzocchio": "Trentino pinot one-off",
    "vini_belluzzo": "single-bottle one-off",
    "will_arnold": "single-bottle CdR newcomer — watch, no page yet",
    "ashes_diamonds": "stylish retro-Napa brand — single bottle, no taste anchor",
    "apollo_s_praise": "single Finger Lakes bottle (New York taxonomy gap not worth opening yet)",
    "our_wines": "identity unverifiable from cellar data alone (8 btl Oregon Pinot) — no page until confirmed",
}

# slug → note (plausible keepers parked for a future pass)
REVISIT: dict[str, str] = {
    "frenchtown_farms": "Sierra foothills natural farming — likely keeper, confirm current status",
    "carlisle": "heritage old-vine zin/syrah — style on the rich side, decide with Evan",
    "macdonald": "To Kalon old-vine, restrained — cult-adjacent pricing, decide with Evan",
    "phelan_farm_rajat_parr": "Raj Parr biodynamic Cambria — likely keeper, young project",
    "casa_dumetz": "Sonja Magdevski's Santa Barbara label (with Clementine Carter) — pair decision",
    "clementine_carter": "sister label of Casa Dumetz — pair decision",
    "grant_marie": "boutique CA — NOTE: cellar has both grant_marie and grant_marie_winery slugs; merge first",
    "grant_marie_winery": "duplicate slug of grant_marie — merge cellar slugs before any page",
    "domaine_philippe_naddef": "trad Gevrey grower, 3 btl — solid, low urgency",
    "daniel_bouland": "old-school Morgon grower — likely keeper next Beaujolais pass",
    "domaine_chapel": "David Chapel (Lapierre-trained) Fleurie — likely keeper next Beaujolais pass",
    "domaine_marc_antonin_blain": "Blain-Gagnard scion; single Bâtard bottle",
    "domaine_odoul_coquard": "Morey grower, single bottle — low info",
    "nicolas_delfaud": "Mâcon grower — low info",
    "domaine_berlancourt": "Bourgogne blanc micro-domaine — identity to confirm",
    "domaine_rougeot": "Meursault (Pierre-Henri Rougeot, natural-leaning) — decide with Evan",
    "chateau_des_rontets": "organic Pouilly-Fuissé treetop estate — single bottle",
    "domaine_des_pierres_seches": "young Saint-Joseph grower — likely keeper next Rhône pass",
    "gerard_courbis": "Saint-Joseph VV grower — identity vs Domaine Courbis to confirm",
    "domaine_du_pegau": "iconic trad Châteauneuf — CdP outside core areas, single bottle",
    "cedric_parpette": "natural Côte-Rôtie — single bottle, low info",
    "domaine_henry_pelle": "solid Menetou-Salon grower — likely keeper next Loire pass",
    "pierre_olivier_bonhomme": "Loire natural (ex-Puzelat) — single bottle",
    "stephane_regnault": "grower Champagne, modal-jazz cuvées — single bottle",
    "weingut_knewitz": "rising Rheinhessen chardonnay — likely keeper next Germany pass",
    "richard_ostreicher": "Franken micro-grower — low info, 5 btl",
    "jan_matthias_klein": "Mosel natural (Little Bastard) — single bottle",
    "weingut_andi_weigand": "Franken natural — single bottle",
    "chateau_pichon_longueville_comtesse_de_lalande": "aged super-second (1996) — page only if aged-Bordeaux coverage grows",
    "chateau_leoville_las_cases": "aged super-second (1998) — same decision as Pichon Comtesse",
    "chateau_cos_d_estournel": "aged super-second (1997) — same decision as Pichon Comtesse",
    "la_badina": "Lessona (Alto Piemonte) — likely keeper next Piedmont pass",
    "cesare_bussolo": "La Morra dolcetto grower — low info",
    "alessandro_e_gian_natale_fantino": "Monforte trad (Dardi) — likely keeper next Piedmont pass",
    "vigneti_valle_roncati": "Fara riserva — Alto Piemonte, low info",
    "gustinella_jungimmune": "Etna artisan — verify producer identity (Gustinella) and slug",
    "diletta_tonello": "natural Durello, 6 btl — likely keeper, low info",
    "marco_sara": "Friuli natural micro — likely keeper next Friuli pass",
    "la_staffa": "Verdicchio riserva artisan — likely keeper next Italy pass",
    "candialle": "organic Panzano Chianti — decide with Evan",
    "guastaferro": "old-vine Taurasi — likely keeper next Campania look",
    "azienda_agricola_cianfagna": "Molise aglianico — needs Molise taxonomy addition",
    "la_fornace": "Montalcino artisan — low info",
    "nittnaus": "biodynamic Burgenland — keeper if Austria coverage grows",
    "mohr_niggli": "Graubünden pinot — needs Switzerland taxonomy addition",
    "weingut_sprecher_von_bernegg": "Graubünden pinot — needs Switzerland taxonomy addition",
    "muxagat_vinhos": "artisan Douro — keeper if Portugal becomes an interest area",
    "cabecas_do_reguengo": "organic Alentejo artisan — same Portugal decision",
    "vale_da_capucha": "natural Lisboa — same Portugal decision",
    "lady_of_the_sunshine": "Gina Giugni biodynamic SLO — single bottle, likely keeper later",
    "stirm": "Ryan Stirm riesling-specialist CA natural — single bottle",
    "clos_du_rouge_gorge": "Cyril Fhal Roussillon — single bottle, likely keeper later",
    "croix_courbet": "young Côtes du Jura estate (2 btl) — low info, Jura interest says look again",
    "domaine_de_la_terre_rouge": "Sierra foothills Rhône-ranger — single bottle, low urgency",
}

PAGE_TEMPLATE = """---
type: producer
name: "{name}"
slug: {slug}
aliases: [{aliases}]
country: "{country}"
region: "{region}"
sub_region: "{sub_region}"
appellations: []
farming: [{farming}]
certifications: []
importer_us: [{importers}]
retailers:
  chambers:
    championed: false
    article_count: 0
    dedicated_count: 0
    first_year: 0
    last_year: 0
  dte:
    in_portfolio: false
    cuvee_count: 0
    price_min: 0
    price_max: 0
  raeders:
    in_portfolio: false
  fass:
    in_portfolio: false
tags: []
status: seeded
_sources:
- cellar_triage_2026-06
---

# {name}

{summary}

## CSW Write-ups

_Not yet covered in the CSW archive sweep. Re-run `ingest_csw.py` after tuning aliases if coverage is expected._

## Down to Earth Wines (Panzer)

_Not yet populated._

## Raeder's

_Not yet populated._

## FASS

_Not yet populated._

## Cross-references

{crossrefs}
"""


def qlist(items: list[str]) -> str:
    return ", ".join(f'"{i}"' for i in items)


def country_hub(country: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", country)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s\-&]", "", s)
    return re.sub(r"\s+", "_", s).strip("_") + "_Producers"


def region_rollup(region: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", region)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s\-&]", "", s)
    return re.sub(r"\s+", "_", s).strip("_") + "_Producers"


def missing_cellar_slugs() -> dict[str, dict]:
    have = {p.stem for p in PRODUCERS.glob("*.md")}
    info: dict[str, dict] = defaultdict(lambda: {"bottles": 0, "entries": 0, "value": 0.0, "producer": ""})
    for p in CELLAR.glob("*.md"):
        m = FM_RE.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        fm = m.group(1)
        if g(fm, "type") != "cellar_entry":
            continue
        slug = g(fm, "producer_slug")
        if not slug or slug in have:
            continue
        try:
            qty = int(g(fm, "quantity"))
        except ValueError:
            qty = 0
        try:
            price = float(g(fm, "purchase_price_usd"))
        except ValueError:
            price = 0.0
        d = info[slug]
        d["bottles"] += qty
        d["entries"] += 1
        d["value"] += qty * price
        d["producer"] = d["producer"] or g(fm, "producer")
    return dict(info)


def main() -> int:
    missing = missing_cellar_slugs()
    bucketed = set(CREATE) | set(NO_PAGE) | set(REVISIT)
    overlap = (set(CREATE) & set(NO_PAGE)) | (set(CREATE) & set(REVISIT)) | (set(NO_PAGE) & set(REVISIT))
    if overlap:
        print(f"ERROR: slugs in multiple buckets: {sorted(overlap)}", file=sys.stderr)
        return 1
    unbucketed = sorted(set(missing) - bucketed)
    if unbucketed:
        print(f"ERROR: {len(unbucketed)} missing slugs not in any bucket:", file=sys.stderr)
        for s in unbucketed:
            print(f"  {s}", file=sys.stderr)
        return 1

    created, skipped = [], []
    for slug, (name, country, region, sub, farming, imps, aliases, summary) in sorted(CREATE.items()):
        path = PRODUCERS / f"{slug}.md"
        if path.exists():
            skipped.append(slug)
            continue
        crossrefs = [f"- [[{region_rollup(region)}|{region}]]",
                     f"- [[{country_hub(country)}|{country}]]"]
        page = PAGE_TEMPLATE.format(
            name=name, slug=slug, aliases=qlist(aliases), country=country,
            region=region, sub_region=sub, farming=qlist(farming),
            importers=qlist(imps), summary=summary,
            crossrefs="\n".join(crossrefs))
        path.write_text(page, encoding="utf-8")
        created.append(slug)

    # --- decision-record view ---
    lines = [
        "---",
        "type: view",
        "updated: 2026-06-09",
        "scope: cellar_triage",
        f"created: {len(CREATE)}",
        f"no_page: {len(NO_PAGE)}",
        f"revisit: {len(REVISIT)}",
        "---",
        "",
        "# Cellar Producer Triage (2026-06)",
        "",
        "Decision record for the cellar producers that had no wiki page "
        "(see [[architecture_review_2026_06|architecture review]]). Taste "
        "filters from CLAUDE.md applied by LLM-judgment pass "
        "(`scripts/compile_cellar_triage.py` — decision table in code). "
        "Re-running the script never overwrites existing pages.",
        "",
        f"## Created ({len(CREATE)})",
        "",
        "| Producer | Region | Cellar | Why |",
        "|---|---|---|---|",
    ]
    for slug, (name, country, region, *_rest) in sorted(CREATE.items()):
        d = missing.get(slug, {})
        cel = f"{d.get('bottles', '?')} btl" if d else "—"
        summary = CREATE[slug][7].split(". ")[0].replace("|", "/")
        lines.append(f"| [[{slug}|{name}]] | {region} ({country}) | {cel} | {summary}. |")
    lines += ["", f"## No page needed ({len(NO_PAGE)})", "",
              "| Producer slug | Cellar | Reason |", "|---|---|---|"]
    for slug, reason in sorted(NO_PAGE.items()):
        d = missing.get(slug, {})
        cel = f"{d.get('bottles', '?')} btl" if d else "—"
        lines.append(f"| `{slug}` | {cel} | {reason} |")
    lines += ["", f"## Revisit ({len(REVISIT)})", "",
              "| Producer slug | Cellar | Note |", "|---|---|---|"]
    for slug, note in sorted(REVISIT.items()):
        d = missing.get(slug, {})
        cel = f"{d.get('bottles', '?')} btl" if d else "—"
        lines.append(f"| `{slug}` | {cel} | {note} |")
    lines += ["", "*Generated by `scripts/compile_cellar_triage.py`.*"]
    VIEW_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Created {len(created)} producer pages "
          f"({len(skipped)} already existed), "
          f"{len(NO_PAGE)} no-page decisions, {len(REVISIT)} revisit.")
    print(f"Decision record: {VIEW_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
