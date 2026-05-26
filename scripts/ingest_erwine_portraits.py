"""
Ingest E & R Wine Shop "Producer Portraits" into wiki/producers/.

Source: https://www.erwineshop.com/producer-portraits (Squarespace blog of
~80 producer write-ups from Portland, OR retailer Ed Paladino & team).

Strategy
========
The portraits index page returns 403 to WebFetch and the host isn't on the
sandbox's curl allowlist, so the full producer list and bodies were
enumerated via Google snippets (WebSearch). Per-producer summaries below
are short excerpts pulled from those snippets, not from the live pages —
they're enough to seed editorial context plus the canonical erwineshop URL
that future LLM passes can follow up on.

What this script does
---------------------
1. Creates 76 new producer pages under wiki/producers/ for producers not
   already in the vault.
2. Appends a `## E&R Wine Shop` section to 4 existing matching pages
   (domaine_bart, domaine_chantereves, elio_ottin, marguet) with the
   portrait URL + a short excerpt. Existing frontmatter and body content
   are preserved.
3. Creates wiki/retailers/E_R_Wine_Shop.md.

Idempotent: rerunning is safe. Existing pages aren't clobbered; the
E&R section is only inserted when absent and updated in place when
present (marked by `<!-- ERWINE -->` sentinels).
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RETAILERS = VAULT / "wiki" / "retailers"

ERWINE_BEGIN = "<!-- BEGIN E&R WINE SHOP -->"
ERWINE_END = "<!-- END E&R WINE SHOP -->"


@dataclass
class Producer:
    slug: str
    name: str
    country: str
    region: str
    sub_region: str
    farming: list[str]
    tags: list[str]
    url: str
    summary: str  # 1-3 sentences pulled from WebSearch snippets


PRODUCERS_MANIFEST: list[Producer] = [
    # ---------------- FRANCE ----------------
    # Alsace
    Producer("domaine_loew", "Domaine Loew", "France", "Alsace", "Westhoffen",
             ["organic", "biodynamic"], ["alsace", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/domaine-loew",
             "Etienne Loew farms organic + biodynamic in Westhoffen, the cool northern edge of Alsace where a featherlight touch shepherds the wines toward ethereal."),
    Producer("marcel_deiss", "Domaine Marcel Deiss", "France", "Alsace", "Bergheim",
             ["biodynamic"], ["alsace", "biodynamic", "field-blend"],
             "https://www.erwineshop.com/producer-portraits/domaine-marcel-deiss",
             "Run by Jean-Michel and Mathieu Deiss in Bergheim. 26 ha of hillside vineyards across 9 communes, farmed biodynamically, known for terroir-driven field blends."),
    Producer("valentin_zusslin", "Domaine Valentin Zusslin", "France", "Alsace", "Orschwihr",
             ["organic", "biodynamic"], ["alsace", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/zusslin",
             "Five hundred years of family roots in Alsace. Zusslin has quickly risen to the top of the Alsatian hierarchy on the strength of biodynamic farming and precise winemaking."),
    Producer("vins_mader", "Vins Mader", "France", "Alsace", "Hunawihr",
             ["organic"], ["alsace"],
             "https://www.erwineshop.com/producer-portraits/mader",
             "Young and energetic Jérôme Mader took over the family domaine and made it one of Alsace's exciting producers. One of E&R's four Alsatian growers."),

    # Burgundy
    Producer("chateau_de_beru", "Château de Béru", "France", "Burgundy", "Chablis",
             ["organic", "biodynamic"], ["burgundy", "chablis", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/chateau-de-beru",
             "Chablis at the eastern frontier of Burgundy. White Burgundy with salty butter and lemon rind, biodynamic in the vineyards since 2009."),
    Producer("raphaelle_guyot", "Raphaëlle Guyot", "France", "Burgundy", "Puisaye-sur-Forterre",
             ["natural"], ["burgundy", "natural-wine", "aligote"],
             "https://www.erwineshop.com/producer-portraits/9dnf04a8hx3rjdefjpxkkujw4grvzz-wtxm9",
             "Natural-wine producer on the westernmost outcropping of Burgundy's jurassic limestone, in Puisaye. Saline pointedness and a playful, light style."),
    Producer("les_faverelles", "Les Faverelles", "France", "Burgundy", "Vézelay",
             ["organic"], ["burgundy", "vezelay", "value"],
             "https://www.erwineshop.com/producer-portraits/les-faverelles",
             "Patrick and Isabelle Bringer left Paris to make wine in Vézelay, the medieval Yonne village at the northern edge of Burgundy. Pinot Noir and Chardonnay around $25 via E&R's Almost Direct Imports."),
    Producer("sangouard_guyot", "Domaine Sangouard-Guyot", "France", "Burgundy", "Mâconnais (Vergisson)",
             [], ["burgundy", "maconnais", "chardonnay"],
             "https://www.erwineshop.com/producer-portraits/sangouard-guyot",
             "Vergisson, in the south of Burgundy where the Mâconnais produces mineral-driven Chardonnay. One of the standout addresses for Pouilly-Fuissé and Saint-Véran."),
    Producer("michel_lafarge", "Domaine Michel Lafarge", "France", "Burgundy", "Volnay",
             ["organic", "biodynamic"], ["burgundy", "volnay", "biodynamic", "cult"],
             "https://www.erwineshop.com/producer-portraits/domane-michel-lafarge-burgundy-france",
             "Volnay benchmark. Among the first to domaine-bottle in the 1930s, biodynamic since 1995. Now led by Frédéric, Chantal and Clothilde — they plow with a horse and never chased modernity."),
    Producer("nathalie_gilles_fevre", "Domaine Nathalie & Gilles Fèvre", "France", "Burgundy", "Chablis",
             ["organic"], ["burgundy", "chablis", "organic"],
             "https://www.erwineshop.com/producer-portraits/fevrechablis",
             "Nathalie was Chef du Cave at La Chablisienne for twelve years; she and Gilles started their own domaine in 2003. Vines in Vaulorent, Fourchaume and Les Preuses; organic farming."),

    # Champagne
    Producer("suenen", "Suenen", "France", "Champagne", "Côte des Blancs (Cramant)",
             ["organic"], ["champagne", "grower-champagne", "cote-des-blancs"],
             "https://www.erwineshop.com/producer-portraits/suenen-champagne",
             "Aurélien Suenen took over the family estate in his late twenties — just 2 ha of Côte des Blancs grand cru holdings (Cramant, Chouilly, Oiry) farmed meticulously."),
    Producer("christophe_mignon", "Christophe Mignon", "France", "Champagne", "Festigny (Vallée de la Marne)",
             ["organic", "biodynamic"], ["champagne", "grower-champagne", "biodynamic", "pinot-meunier"],
             "https://www.erwineshop.com/producer-portraits/champagne-christophe-mignon",
             "Pinot-Meunier specialist in Festigny. His grandfather established the vineyards in 1880; Christophe reserves 1.5 ha for his own 'Christophe Mignon' label, biodynamically farmed."),
    Producer("pascal_doquet", "Pascal Doquet", "France", "Champagne", "Vertus (Côte des Blancs)",
             ["organic"], ["champagne", "grower-champagne", "chardonnay"],
             "https://www.erwineshop.com/producer-portraits/pascal-doquet",
             "Wholly organic grower champagne. Doquet's chalk-driven Blanc de Blancs are easily among the very best quality in Champagne."),
    Producer("benoit_lahaye", "Benoit Lahaye", "France", "Champagne", "Bouzy",
             ["organic", "biodynamic"], ["champagne", "grower-champagne", "biodynamic", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/benoit-lahaye",
             "Biodynamic Bouzy. Lahaye is one of the Montagne de Reims' most thoughtful pinot-noir-driven grower champagnes."),
    Producer("de_sousa", "Champagne De Sousa", "France", "Champagne", "Avize (Côte des Blancs)",
             ["organic", "biodynamic"], ["champagne", "grower-champagne", "biodynamic", "grand-cru"],
             "https://www.erwineshop.com/producer-portraits/de-sousa",
             "Family-owned grand-cru holdings worked organically/biodynamically. ~70,000 bottles annual production, anchored in Avize and the Côte des Blancs."),
    Producer("eric_rodez", "Champagne Eric Rodez", "France", "Champagne", "Ambonnay",
             ["biodynamic"], ["champagne", "grower-champagne", "biodynamic", "ambonnay"],
             "https://www.erwineshop.com/producer-portraits/champagne-eric-rodez",
             "Eric Rodez — mayor of Ambonnay and 8th generation to run his family's grand-cru Champagne domaine. Biodynamic, parcel-by-parcel vinification."),
    Producer("franck_pascal", "Champagne Franck Pascal", "France", "Champagne", "Baslieux-sous-Châtillon (Vallée de la Marne)",
             ["organic", "biodynamic"], ["champagne", "grower-champagne", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/champagne-franck-pascal",
             "Biodynamic Vallée de la Marne grower champagne. Meunier-led blends with very low dosage and meditative attention to terroir."),

    # Beaujolais
    Producer("julien_duport", "Julien Duport", "France", "Beaujolais", "Brouilly / Côte de Brouilly",
             ["organic"], ["beaujolais", "gamay", "brouilly"],
             "https://www.erwineshop.com/producer-portraits/julien-duport",
             "Fourth-generation Beaujolais grower with parcels 'La Folie' in Brouilly and 'La Boucheratte' in Côte de Brouilly. Whole-cluster, carbonic-tradition gamay."),
    Producer("nicolas_chemarin", "Nicolas Chemarin", "France", "Beaujolais", "Marchampt (Beaujolais-Villages)",
             ["organic"], ["beaujolais", "gamay", "lunar-cycles"],
             "https://www.erwineshop.com/producer-portraits/nicolas-chemarin",
             "Marchampt, a hamlet of fewer than 50 souls in Beaujolais-Villages. Chemarin farms organically, works by lunar cycles, bottles with minimal sulfur."),

    # Rhône
    Producer("jean_louis_chave", "Domaine Jean-Louis Chave", "France", "Rhône", "Hermitage / Mauves",
             ["organic"], ["rhone", "hermitage", "syrah", "marsanne", "roussanne", "cult"],
             "https://www.erwineshop.com/producer-portraits/domaine-jean-louis-chave",
             "Defines Hermitage. The Chave family — now 16 generations — makes legendary white Hermitage, red Hermitage and the rare sweet vin de paille. Crozes-Hermitage rouge added from 2005."),

    # Jura
    Producer("cellier_saint_benoit", "Cellier Saint Benoît", "France", "Jura", "Pupillin",
             ["organic"], ["jura", "trousseau", "ploussard", "poulsard"],
             "https://www.erwineshop.com/producer-portraits/cellier-saint-benoit-jura-france",
             "Tiny Pupillin estate. Benjamin Benoit was selected as Jura's Winemaker of the Year in 2021 on the strength of a small, finely-drawn lineup."),
    Producer("fumey_chatelain", "Domaine Fumey-Chatelain", "France", "Jura", "Montigny-lès-Arsures",
             [], ["jura", "savagnin", "chardonnay"],
             "https://www.erwineshop.com/producer-portraits/domaine-fumey-chatelain-jura-france",
             "Founded ~30 years ago, ~17 ha across Jura's classic appellations. E&R sources includes a Cremant du Jura Blanc and traditional Savagnin and Chardonnay bottlings."),

    # Loire
    Producer("florian_roblin", "Florian Roblin", "France", "Loire", "Coteaux du Giennois",
             ["organic"], ["loire", "sauvignon-blanc", "pinot-noir", "gamay"],
             "https://www.erwineshop.com/producer-portraits/florian-roblin",
             "Coteaux du Giennois — north of Pouilly-Fumé and hidden in the shadow of Sancerre. One hectare of pinot/gamay planted 2006 plus sauvignon on flinty-chalky soils."),
    Producer("la_grange_tiphaine", "La Grange Tiphaine", "France", "Loire", "Amboise (Touraine)",
             ["organic", "biodynamic"], ["loire", "chenin", "cot", "amboise", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/la-grange-tiphaine",
             "Amboise-based family domaine working organically/biodynamically across Touraine. Côt, Cabernet Franc, Chenin Blanc — energetic, terroir-driven Loires."),

    # South West
    Producer("michel_issaly", "Michel Issaly — Domaine de La Ramaye", "France", "South West", "Gaillac",
             ["organic", "biodynamic"], ["south-west", "gaillac", "biodynamic", "natural"],
             "https://www.erwineshop.com/producer-portraits/michel-issaly",
             "Domaine de La Ramaye in Gaillac. Issaly is a leading voice in southwestern France's natural-wine generation, working biodynamically with native varieties."),

    # ---------------- ITALY ----------------
    # Piedmont
    Producer("giovanni_prandi", "Giovanni Prandi", "Italy", "Piedmont", "Diano d'Alba",
             [], ["piedmont", "dolcetto", "diano-dalba", "value"],
             "https://www.erwineshop.com/producer-portraits/giovanni-prandi",
             "Diano d'Alba — one of the great Dolcetto villages. Prandi makes ~1,500 cases a year from superb vineyards; extraordinary wines for the price."),
    Producer("alberto_burzi", "Alberto Burzi", "Italy", "Piedmont", "La Morra (Barolo)",
             [], ["piedmont", "barolo", "nebbiolo", "la-morra"],
             "https://www.erwineshop.com/producer-portraits/alberto-burzi",
             "Young La Morra grower. Burzi's Barolo DOCG and 'Vecchie Viti Capalot' show what the new Piedmont generation can do with classical methods."),
    Producer("matteo_correggia", "Azienda Agricola Matteo Correggia", "Italy", "Piedmont", "Roero (Canale)",
             [], ["piedmont", "roero", "nebbiolo", "arneis", "barbera"],
             "https://www.erwineshop.com/producer-portraits/matteo-correggia",
             "Canale, in the Roero north of Alba. The estate helped raise the profile of Roero, working with Nebbiolo, Arneis, Barbera and Brachetto."),
    Producer("cecilia_monte", "Cecilia Monte", "Italy", "Piedmont", "Barbaresco (Neive)",
             [], ["piedmont", "barbaresco", "nebbiolo", "neive"],
             "https://www.erwineshop.com/producer-portraits/cecilia-monte",
             "Trained at Luciano Sandrone before starting her own winery in Neive in 2000. ~2,400 cases from a parcel adjacent to Starderi, in the northernmost reach of Barbaresco."),

    # Valle d'Aosta
    Producer("lo_triolet", "Lo Triolet — Marco Martin", "Italy", "Valle d'Aosta", "Introd",
             [], ["valle-daosta", "fumin", "petite-arvine", "aosta"],
             "https://www.erwineshop.com/producer-portraits/lo-triolet",
             "Marco Martin's tiny winery in Introd. 'Trifoglio' (three-leaf clover) in local patois. Fumin, Petite Arvine and other Alpine specialties from a finely-crafted small lineup."),
    Producer("la_vrille", "La Vrille", "Italy", "Valle d'Aosta", "Verrayes",
             [], ["valle-daosta", "fumin", "cornalin", "vuillermin"],
             "https://www.erwineshop.com/producer-portraits/la-vrille",
             "Hervé Deguillame's Alpine domaine. Fumin, Cornalin, Vuillermin and other indigenous Aostan varieties under the high-elevation light of the Valle d'Aosta."),

    # Lombardy
    Producer("mamete_prevostini", "Mamete Prevostini", "Italy", "Lombardy", "Valtellina",
             ["organic"], ["lombardy", "valtellina", "nebbiolo", "alpine"],
             "https://www.erwineshop.com/producer-portraits/mamete-prevostini",
             "Valtellina — the Alpine Nebbiolo cradle of Lombardy. Prevostini farms steep terraced vineyards and bottles the appellation's classic crus (Sassella, Inferno, Grumello)."),
    Producer("terrazzi_alti", "Terrazzi Alti — Siro Buzzetti", "Italy", "Lombardy", "Valtellina",
             ["organic"], ["lombardy", "valtellina", "nebbiolo", "alpine"],
             "https://www.erwineshop.com/producer-portraits/siro-buzzetti",
             "Siro Buzzetti's tiny Valtellina project at altitude. Hand-farmed Nebbiolo (Chiavennasca) on terraced slate, traditional vinification."),

    # Alto Adige
    Producer("kuen_hof", "Kuen Hof", "Italy", "Alto Adige / Südtirol", "Bressanone (Eisacktal/Valle Isarco)",
             ["organic"], ["alto-adige", "valle-isarco", "kerner", "sylvaner"],
             "https://www.erwineshop.com/producer-portraits/kuen-hof",
             "Peter Pliger's Valle Isarco estate near Bressanone — Kerner, Sylvaner, Veltliner, Riesling from precipitous schist terraces, organically farmed."),
    Producer("tenuta_ebner", "Weingut Tenuta Ebner", "Italy", "Alto Adige / Südtirol", "Campodazzo-Renon",
             [], ["alto-adige", "vernatch", "schiava", "lagrein"],
             "https://www.erwineshop.com/producer-portraits/ebner",
             "Family Tenuta Ebner above Bolzano. Schiava, Lagrein and other Alto Adige indigenous varieties from high-altitude porphyry."),
    Producer("franz_gojer", "Franz Gojer", "Italy", "Alto Adige / Südtirol", "Santa Maddalena",
             [], ["alto-adige", "vernatch", "schiava", "lagrein", "santa-maddalena"],
             "https://www.erwineshop.com/producer-portraits/franz-gojer",
             "Santa Maddalena traditionalist. Gojer farms steep hillside vineyards around Bolzano for Schiava/Vernatsch and Lagrein at the highest quality level."),
    Producer("thomas_niedermayr", "Thomas Niedermayr", "Italy", "Alto Adige / Südtirol", "Eppan (Appiano)",
             ["organic"], ["alto-adige", "piwi", "organic", "biodiversity"],
             "https://www.erwineshop.com/producer-portraits/introducing-thomas-niedermayr-of-alto-adige",
             "Bioweingut Niedermayr at Hof Gandberg near Eppan — wholly organic for 30+ years and now working exclusively with PIWI grape varieties. Wines from a real, polycultural farm."),

    # Veneto
    Producer("giovanni_menti", "Giovanni Menti", "Italy", "Veneto", "Gambellara",
             ["organic", "biodynamic", "natural"], ["veneto", "gambellara", "garganega", "natural", "orange"],
             "https://www.erwineshop.com/producer-portraits/menti-marcobarba-garganuda",
             "Stefano Menti's small Gambellara estate. Garganega — the kingpin grape — across fresh whites, long-aging whites, skin-contact wines and pet-nat ('Marcobarba', 'Garganuda')."),

    # Friuli
    Producer("dario_raccaro", "Dario Raccaro", "Italy", "Friuli-Venezia Giulia", "Collio (Cormons)",
             [], ["friuli", "collio", "friulano", "malvasia"],
             "https://www.erwineshop.com/producer-portraits/dario-raccaro",
             "Cormons, in the heart of Collio. Raccaro is among the very finest of Friuli's white-wine specialists — pure, classical Friulano and Malvasia."),

    # Emilia-Romagna
    Producer("cantina_paltrinieri", "Cantina Paltrinieri", "Italy", "Emilia-Romagna", "Sorbara (Modena)",
             [], ["emilia-romagna", "lambrusco", "sorbara"],
             "https://www.erwineshop.com/producer-portraits/cantina-paltrinieri",
             "Lambrusco di Sorbara done right — Paltrinieri are among the great names of serious, ancestral-method and metodo-classico Lambrusco from Sorbara."),
    Producer("cantina_della_volta", "Cantina Della Volta", "Italy", "Emilia-Romagna", "Modena",
             [], ["emilia-romagna", "lambrusco", "metodo-classico"],
             "https://www.erwineshop.com/producer-portraits/cantina-della-volta",
             "Christian Bellei went all-in in 2010 with a no-holds-barred Lambrusco operation — among Emilia-Romagna's best, with serious metodo-classico bottlings."),
    Producer("villa_picta", "Villa Picta", "Italy", "Emilia-Romagna", "Villimpenta (Mantova border)",
             ["organic"], ["emilia-romagna", "lambrusco-ruberti", "natural"],
             "https://www.erwineshop.com/producer-portraits/villa-picta-returns-de49x",
             "A 3.5-ha organic farm on the Po between Emilia and Lombardia. Works with the local Lambrusco Ruberti — a thick-skinned variety only grown around Mantova."),

    # Liguria
    Producer("prima_terra", "Prima Terra — Walter De Battè", "Italy", "Liguria", "Cinque Terre (Riomaggiore)",
             ["organic", "biodynamic"], ["liguria", "cinque-terre", "sciacchetra", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/prima-terra-walter",
             "Native son of Riomaggiore and quietly one of Italy's finest winemakers for two decades. Classic Mediterranean style — stainless, old oak, skin contact — 150-200 cases per wine."),
    Producer("cantine_litan", "Cantine Litan", "Italy", "Liguria", "Cinque Terre",
             [], ["liguria", "cinque-terre", "albarola", "bosco"],
             "https://www.erwineshop.com/producer-portraits/litan",
             "USA-premiere Cinque Terre via E&R's almost-direct-imports. Steep terraced viticulture on schist-and-sandstone facing the Ligurian sea."),
    Producer("la_possa", "La Possa", "Italy", "Liguria", "Cinque Terre",
             [], ["liguria", "cinque-terre", "albarola", "bosco", "sciacchetra"],
             "https://www.erwineshop.com/producer-portraits/la-possa",
             "Samuele Heydi Bonanini's Azienda La Possa — keeper of grapes and vines for the most demanding terraces of Cinque Terre. E&R was first to bring his wines to America."),
    Producer("cian_du_giorgi", "Cian du Giorgi", "Italy", "Liguria", "Cinque Terre",
             [], ["liguria", "cinque-terre"],
             "https://www.erwineshop.com/producer-portraits/cinque-terre-the-usa-premiere-of-cian-du-giorgi",
             "Riccardo and Adeline's Cinque Terre project — USA premiere via E&R's almost-direct-imports work in Riomaggiore and the surrounding villages."),

    # Tuscany
    Producer("baricci", "Baricci", "Italy", "Tuscany", "Montalcino",
             [], ["tuscany", "brunello", "sangiovese", "montalcino"],
             "https://www.erwineshop.com/producer-portraits/baricci",
             "Montalcino traditionalist. Baricci farms north-facing Montosoli vineyards and bottles old-school Brunello di Montalcino and Rosso di Montalcino."),
    Producer("san_polino", "San Polino", "Italy", "Tuscany", "Montalcino",
             ["organic"], ["tuscany", "brunello", "sangiovese", "montalcino", "organic"],
             "https://www.erwineshop.com/producer-portraits/brunello-for-the-ages",
             "Organic Brunello di Montalcino — long-aged, terroir-explicit Sangiovese. Brunello gained DOCG status in 1980 and San Polino is one of its serious modern names."),

    # Marche
    Producer("fattoria_coroncino", "Fattoria Coroncino", "Italy", "Marche", "Castelli di Jesi (Staffolo)",
             [], ["marche", "verdicchio", "castelli-di-jesi"],
             "https://www.erwineshop.com/producer-portraits/fattoria-coroncino",
             "Valerio Canestrari outside Staffolo — makes some of the top wines in the Marches, in the promised land for Verdicchio: Castelli di Jesi."),
    Producer("caliptra", "Ca'Liptra", "Italy", "Marche", "Cupramontana (Castelli di Jesi)",
             ["organic"], ["marche", "verdicchio", "castelli-di-jesi", "organic"],
             "https://www.erwineshop.com/producer-portraits/caliptra",
             "Cupramontana — the so-called 'capital of Verdicchio'. Ca'Liptra makes serious, terroir-driven Verdicchio dei Castelli di Jesi from organic vines."),
    Producer("azienda_fiorano", "Azienda Fiorano", "Italy", "Marche", "Cossignano",
             ["organic"], ["marche", "value", "organic"],
             "https://www.erwineshop.com/producer-portraits/fiorano",
             "Paolo and Paola in Cossignano (lower Marche, near the Adriatic coast). 100% organic — vini biologici naturali — exuberant, fresh, honest, great value."),
    Producer("la_monacesca", "La Monacesca", "Italy", "Marche", "Matelica",
             [], ["marche", "verdicchio", "matelica"],
             "https://www.erwineshop.com/producer-portraits/la-monacesca",
             "Matelica — the cooler, inland Verdicchio appellation. La Monacesca is one of the touchstone producers showing Verdicchio at its long-aging best."),

    # Abruzzo
    Producer("faraone", "Azienda Agricola Faraone", "Italy", "Abruzzo", "Giulianova",
             [], ["abruzzo", "montepulciano", "trebbiano", "pecorino"],
             "https://www.erwineshop.com/producer-portraits/faraone",
             "Federico Faraone on the Abruzzo coast at Giulianova. Quiet classicists with Montepulciano d'Abruzzo, Trebbiano and the local Pecorino."),

    # Lazio
    Producer("damiano_ciolli", "Damiano Ciolli", "Italy", "Campania", "Olevano Romano (Lazio)",
             ["organic"], ["lazio", "cesanese", "olevano-romano", "organic"],
             "https://www.erwineshop.com/producer-portraits/damiano-ciolli",
             "Lazio's signature red grape, Cesanese, treated with the seriousness of a great Burgundian site. Damiano and Letiza make ~1,200 cases — 'Silene' and 'Cirsium' from Olevano Romano."),
    Producer("la_visciola", "La Visciola — Piero Macciocca", "Italy", "Campania", "Piglio (Lazio)",
             ["organic"], ["lazio", "cesanese", "piglio", "organic"],
             "https://www.erwineshop.com/producer-portraits/la-visciola",
             "Piero Macciocca makes Cesanese del Piglio organically from tiny parcels. Piglio is a hill village where Romans were making wine in 1088 and more than one Pope favored its reds."),

    # Campania
    Producer("i_cacciagalli", "I Cacciagalli", "Italy", "Campania", "Terra di Lavoro (Caserta)",
             ["organic", "biodynamic"], ["campania", "biodynamic", "pallagrello", "casavecchia"],
             "https://www.erwineshop.com/producer-portraits/i-cacciagalli",
             "Dianna Iannaccone and Mario in northwest Campania's Terra di Lavoro. Family farm working biodynamically with native Pallagrello, Casavecchia and other Caserta varieties."),
    Producer("pietracupa", "Pietracupa — Sabino Loffredo", "Italy", "Campania", "Montefredane (Irpinia)",
             [], ["campania", "irpinia", "fiano", "greco-di-tufo", "aglianico"],
             "https://www.erwineshop.com/producer-portraits/pietracupa",
             "Sabino Loffredo in Montefredane east of Naples. According to Ian d'Agata the best Greco of all. 2,000-ft vines on volcanic clay, sandstone and limestone — Fiano, Greco di Tufo, Taurasi (Aglianico)."),
    Producer("azienda_reale", "Azienda Reale", "Italy", "Campania", "Amalfi Coast",
             [], ["campania", "amalfi", "tramonti"],
             "https://www.erwineshop.com/producer-portraits/amalfi-azienda-reale",
             "Amalfi Coast viticulture — terraced vineyards on lemon-and-vine pergolas above the sea. Indigenous southern varieties on volcanic-and-limestone soils."),

    # Sicily
    Producer("i_vigneri", "I Vigneri di Salvo Foti", "Italy", "Sicily", "Mt. Etna",
             ["organic"], ["sicily", "etna", "nerello-mascalese", "nerello-cappuccio", "carricante"],
             "https://www.erwineshop.com/producer-portraits/etna-elegance-wines-from-i-vigneri-salvo-foti-ppzyz",
             "Salvo Foti revived a centuries-old union of Etna winegrowers (I Vigneri). 'It's as if I have stopped cultivating the vineyard and started cultivating people.' The reference point for traditional Etna."),

    # ---------------- UNITED STATES (Oregon) ----------------
    Producer("grape_ink", "Grape Ink", "United States", "Oregon", "North Willamette Valley",
             ["organic"], ["oregon", "willamette-valley", "trousseau", "savagnin", "mondeuse"],
             "https://www.erwineshop.com/producer-portraits/grape-ink-north-willamette-valley-oregon",
             "Jarad Hadi's outlier vineyard at the north edge of the Willamette Valley, at elevation. Trousseau, Mondeuse, Chardonnay and Savagnin — unusual choices, executed with intent."),
    Producer("crowley_wines", "Crowley Wines", "United States", "Oregon", "Willamette Valley",
             [], ["oregon", "willamette-valley", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/crowley-wines-willamette-valley-oregon",
             "East-Coast transplant trained under early Oregon greats at Erath, Brickhouse, J.K. Carriere, Archery Summit and Cameron Winery. Classic Willamette Valley Pinot Noir."),
    Producer("granville_wines", "Granville Wines", "United States", "Oregon", "Dundee Hills (Willamette Valley)",
             [], ["oregon", "dundee-hills", "chardonnay"],
             "https://www.erwineshop.com/producer-portraits/eyes-of-the-village-granville-dundee-hills",
             "Jackson Holstein and Ayla bought 20 acres in the Dundee Hills — 4 of them planted to Chardonnay originally by Joe and Jim Maresh — and are reviving that legacy."),
    Producer("kelley_fox", "Kelley Fox", "United States", "Oregon", "Dundee Hills (Willamette Valley)",
             ["organic", "biodynamic"], ["oregon", "dundee-hills", "pinot-noir", "biodynamic"],
             "https://www.erwineshop.com/producer-portraits/on-weeds-amp-birdsong-kelley-fox",
             "Pinot Noir from the historic Maresh Vineyard in the Dundee Hills. Kelley Fox farms by hand and bottles ethereal, perfumed Willamette Valley wines."),
    Producer("liska", "Liska", "United States", "Oregon", "Willamette Valley",
             [], ["oregon", "willamette-valley", "riesling", "gewurztraminer", "gamay"],
             "https://www.erwineshop.com/producer-portraits/liska-willamette-valley-oregon",
             "Chris Butler and Draga Zheleva chose the Willamette Valley specifically for the under-planted varieties — Riesling, Gewürztraminer and Gamay — that thrive there."),
    Producer("walter_scott", "Walter Scott", "United States", "Oregon", "Eola-Amity Hills (Willamette Valley)",
             [], ["oregon", "eola-amity", "chardonnay", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/walter-scott",
             "Ken Pahlow (veteran wine rep) and Erica Landon (sommelier/wine educator). Burgundian-minded Chardonnay and Pinot Noir from Eola-Amity Hills."),
    Producer("niew_vineyards", "Niew Vineyards", "United States", "Oregon", "Chehalem Mountains (Parrett Mountain)",
             ["natural"], ["oregon", "chehalem-mountains", "chardonnay", "no-till"],
             "https://www.erwineshop.com/producer-portraits/chardonnay-tai-ran-and-niew-vineyards-k2mj4",
             "Tai-Ran Niew farms 5 acres of Chardonnay on Parrett Mountain following Masanobu Fukuoka's 'do-nothing' / one-straw method. No tilling, polyculture with native plants, trees and a flock of goats."),
    Producer("lingua_franca", "Lingua Franca", "United States", "Oregon", "Eola-Amity Hills (Willamette Valley)",
             [], ["oregon", "eola-amity", "chardonnay", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/lingua-franca",
             "Winemaker Thomas Savre brings together experience at Evening Land, Domaine Dujac (Morey-St-Denis) and Domaine de la Romanée-Conti. Estate Pinot and Chardonnay in the Eola-Amity Hills."),
    Producer("shiba_wichern", "Shiba-Wichern", "United States", "Oregon", "Willamette Valley",
             [], ["oregon", "willamette-valley", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/shiba-wichern-willamette-valley-or",
             "Akiko Shiba and Chris Wichern negotiated farming-contract terms when they began in 2013 — they farm the fruit themselves and bottle small, hand-built lots."),
    Producer("forrest_schaad", "Forrest Schaad", "United States", "Oregon", "Willamette Valley",
             [], ["oregon", "willamette-valley", "pinot-noir", "old-vines"],
             "https://www.erwineshop.com/producer-portraits/forrest-schaad",
             "Forrest's father planted 4 acres of vines in 1980 from cuttings from Oregon pioneers Dick Erath and Myron Redford. Now a small family label drawing on old-vine fruit."),
    Producer("analemma_wines", "Analemma Wines", "United States", "Columbia Gorge", "Mosier (Oregon side)",
             ["biodynamic"], ["columbia-gorge", "biodynamic", "blanc-de-noir", "atavus"],
             "https://www.erwineshop.com/producer-portraits/analemma-wines",
             "Steven Thompson and Kris Fade revived the old Atavus Vineyard in Mosier in 2010 and bought a 52-acre estate in 2011. Their Champagne-method Blanc de Noir is a landmark for American Gorge viticulture."),
    Producer("bethel_heights", "Bethel Heights Vineyard", "United States", "Oregon", "Eola-Amity Hills",
             [], ["oregon", "eola-amity", "pinot-noir", "chardonnay", "old-vines"],
             "https://www.erwineshop.com/producer-portraits/bethel-heights-vineyard-eola-hills-oregon",
             "Founded 1977-1979 by Terry Casteel, Marilyn Webb, Pat Dudley and Ted Casteel — among the very few remaining own-rooted Pinot and Chardonnay plantings in the Willamette Valley."),
    Producer("loop_de_loop", "Loop de Loop", "United States", "Columbia Gorge", "Underwood Mountain (Washington side)",
             [], ["columbia-gorge", "underwood-mountain", "woman-owned"],
             "https://www.erwineshop.com/producer-portraits/loop-de-loop-underwood-mountain-columbia-gorge",
             "Julia Bailey-Gulstine and Scott Gulstine farm Light Anthology Vineyard at the foot of Underwood Mountain, an extinct shield volcano. Woman-owned, small case production."),
    Producer("hundred_suns", "Hundred Suns", "United States", "Oregon", "McMinnville (Willamette Valley)",
             [], ["oregon", "mcminnville", "rocks-district", "syrah", "pinot-noir"],
             "https://www.erwineshop.com/producer-portraits/hundred-suns-of-the-valley",
             "Renee and Grant in McMinnville, working with Rocks District AVA fruit from Milton-Freewater. 'You can taste the sunshine in each bottle.'"),
    Producer("junichi_fujita", "Junichi Fujita", "United States", "Oregon", "McMinnville (Willamette Valley)",
             ["natural"], ["oregon", "mcminnville", "pinot-noir", "no-till", "natural"],
             "https://www.erwineshop.com/producer-portraits/junichi-fujita-mcminnville-oregon",
             "McMinnville's farmer of the year. Juna vineyard at 600 ft elevation, 25 different Pinot Noir clones, no-till following Fukuoka. Labels hand-drawn on washi paper from Toyama."),
    Producer("art_science", "Art + Science", "United States", "Oregon", "Van Duzer Corridor (Willamette Valley)",
             [], ["oregon", "willamette-valley", "van-duzer", "pinot", "syrah", "cider"],
             "https://www.erwineshop.com/producer-portraits/art-science-willamette-valley-or",
             "Dan Rinke and Kim Hamblin's Roshambo ArtFarm — 50 acres in the Van Duzer corridor. Pinot, Syrah, Grüner Veltliner, some of Oregon's first Mondeuse, plus cider since 2012."),
    Producer("gonzales_wine_company", "Gonzales Wine Company", "United States", "Oregon", "Portland",
             [], ["oregon", "portland", "natural", "minority-owned", "malbec"],
             "https://www.erwineshop.com/producer-portraits/leading-the-way-her-way-gonzales-wine-company",
             "Cristina Gonzales — back to Oregon from Chiapas, inspired by Argentina (and Malbec) on a 2001 backpacking trip. One of few women-of-color winemakers in Oregon; started her label in 2009."),
]


# Producers already in the vault — append the E&R section instead of creating new pages.
EXISTING_OVERLAY: list[Producer] = [
    Producer("domaine_bart", "Domaine Bart", "France", "Burgundy", "Marsannay",
             [], [],
             "https://www.erwineshop.com/producer-portraits/domaine-bart",
             "The family home and winery at Domaine Bart dates from 1765 — 24 years before the Revolution. The Bart style is wedded to tradition: away from new wood, toward elegance, balance and authenticity of place in Marsannay."),
    Producer("domaine_chantereves", "Domaine Chanterêves", "France", "Burgundy", "Savigny-lès-Beaune",
             [], [],
             "https://www.erwineshop.com/producer-portraits/domaine-chantereves",
             "Guillaume Bott and Tomoko Kuriyama's Savigny-lès-Beaune domaine. Lovely wines that get swept up faster and faster every release; spans Burgundy classics and Aligoté projects."),
    Producer("elio_ottin", "Elio Ottin", "Italy", "Valle d'Aosta", "Saint-Christophe",
             [], [],
             "https://www.erwineshop.com/producer-portraits/elio-ottin",
             "Aosta-based grower working with Petite Arvine, Fumin and other Valle d'Aosta indigenous varieties from sun-exposed terraces around Saint-Christophe."),
    Producer("marguet", "Benoît Marguet", "France", "Champagne", "Ambonnay",
             [], [],
             "https://www.erwineshop.com/producer-portraits/benoit-marguet",
             "Benoît officially took over the family domaine in 2005 and made what many Champenois call radical changes — converting to biodynamics and parcel-vinifying the family's Ambonnay grand-cru holdings."),
]


PRODUCER_TEMPLATE = """---
type: producer
name: "{name}"
slug: {slug}
aliases: []
country: "{country}"
region: "{region}"
sub_region: "{sub_region}"
appellations: []
farming: {farming!r}
certifications: []
importer_us: []
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
  erwine:
    in_portfolio: true
    portrait_url: "{url}"
tags: {tags!r}
_sources: ["erwine_portraits"]
---

# {name}

{summary}

{erwine_block}

## Cross-references

- [[{region_link}|{region}]]
- [[E_R_Wine_Shop|E & R Wine Shop (retailer)]]
"""


def render_erwine_block(p: Producer) -> str:
    return textwrap.dedent(f"""\
        ## E&R Wine Shop

        {ERWINE_BEGIN}
        Portrait: [{p.name} — E & R Wine Shop]({p.url})

        > {p.summary}
        {ERWINE_END}""")


def region_link(region: str) -> str:
    # Match the file naming used by build_rollups.py (Region_Producers.md).
    safe = region.replace("'", "").replace("/", "").replace("  ", " ").strip()
    safe = re.sub(r"\s+", "_", safe)
    return f"{safe}_Producers"


def write_new_producer(p: Producer) -> Path:
    path = PRODUCERS / f"{p.slug}.md"
    body = PRODUCER_TEMPLATE.format(
        name=p.name,
        slug=p.slug,
        country=p.country,
        region=p.region,
        sub_region=p.sub_region,
        farming=p.farming,
        tags=p.tags,
        url=p.url,
        summary=p.summary,
        erwine_block=render_erwine_block(p),
        region_link=region_link(p.region),
    )
    path.write_text(body, encoding="utf-8")
    return path


def append_erwine_to_existing(p: Producer) -> tuple[Path, str]:
    """Append (or update in place) the E&R block on an existing producer page."""
    path = PRODUCERS / f"{p.slug}.md"
    text = path.read_text(encoding="utf-8")
    block = render_erwine_block(p)

    # If the sentinels are present, replace in place.
    if ERWINE_BEGIN in text and ERWINE_END in text:
        new_text = re.sub(
            rf"## E&R Wine Shop\n\n{re.escape(ERWINE_BEGIN)}.*?{re.escape(ERWINE_END)}",
            block,
            text,
            count=1,
            flags=re.DOTALL,
        )
        action = "updated"
    elif "## E&R Wine Shop" in text:
        # Section exists but without sentinels — leave it alone.
        return path, "skipped (existing E&R section)"
    else:
        # Insert before `## Cross-references` if present, else at end.
        if "\n## Cross-references" in text:
            new_text = text.replace(
                "\n## Cross-references", f"\n{block}\n\n## Cross-references", 1
            )
        else:
            new_text = text.rstrip() + "\n\n" + block + "\n"
        action = "appended"

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return path, action


RETAILER_TEMPLATE = """---
type: retailer
name: "E & R Wine Shop"
slug: e_r_wine_shop
url: "https://www.erwineshop.com"
location: "Portland, Oregon"
editorial_url_pattern: "https://www.erwineshop.com/producer-portraits/{{slug}}"
tags: ["pacific-northwest", "almost-direct-imports", "producer-portraits"]
---

# E & R Wine Shop

Portland, Oregon retail shop founded by Ed Paladino. Editorial voice
oriented around long-running "Producer Portraits" — first-person
write-ups of winemakers visited in their cellars, anchored by the
shop's "Almost Direct Imports" program (small French and Italian
growers brought in with minimal markup), supplemented by a deep
Oregon and Pacific Northwest bench.

The Producer Portraits index lives at
<https://www.erwineshop.com/producer-portraits>. Each portrait is a
~500-1500 word essay covering the family, the vineyards, the farming,
and what E&R has tasted across visits — closer in spirit to Kermit
Lynch's grower-by-grower introductions than to a retailer's product
copy.

## Coverage in the vault

Producer pages with an E&R portrait carry a `## E&R Wine Shop` section
with the portrait URL and a short excerpt (auto-generated by
`scripts/ingest_erwine_portraits.py`).
"""


def write_retailer_page() -> Path:
    path = RETAILERS / "E_R_Wine_Shop.md"
    path.write_text(RETAILER_TEMPLATE, encoding="utf-8")
    return path


def main() -> None:
    created, skipped, overlay_results = [], [], []

    for p in PRODUCERS_MANIFEST:
        path = PRODUCERS / f"{p.slug}.md"
        if path.exists():
            skipped.append(p.slug)
            continue
        write_new_producer(p)
        created.append(p.slug)

    for p in EXISTING_OVERLAY:
        path, action = append_erwine_to_existing(p)
        overlay_results.append((p.slug, action))

    retailer_path = write_retailer_page()

    print(f"Created {len(created)} new producer pages.")
    if skipped:
        print(f"Skipped {len(skipped)} (already exist): {', '.join(skipped)}")
    print("Overlay actions:")
    for slug, action in overlay_results:
        print(f"  {slug}: {action}")
    print(f"Wrote retailer page: {retailer_path}")


if __name__ == "__main__":
    main()
