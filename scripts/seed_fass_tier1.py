"""
Seed Tier 1 FASS producer pages from the 2026-05-26 triage decision.

One-shot idempotent seeder. Reads the curated PRODUCERS table below
(slug → frontmatter + summary prose) and writes one `wiki/producers/<slug>.md`
per row. Skips if the file already exists (no overwrite).

After running:
  python scripts/seed_fass_tier1.py
  python scripts/ingest_csw.py            # fold matching CSW articles
  python scripts/ingest_fass.py           # populate ## FASS sections
  python scripts/build_rollups.py
  python scripts/build_wiki_index.py
  python scripts/lint.py

The producer specs intentionally don't include `retailers.fass:` —
`ingest_fass.py` is the canonical writer for that block.
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


# ============================================================================
# Northern Rhône — Côte-Rôtie / Cornas / Saint-Joseph cluster
# ============================================================================

RHONE = [
    P(
        slug="julien_barge",
        name="Julien Barge",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        farming=["organic"],
        importer_us=["Vom Boden"],
        tags=["cote-rotie", "syrah", "grower"],
        summary=(
            "Julien Barge took over the family domaine in Ampuis from his "
            "father Gilles, who in turn worked under his grandfather Pierre. "
            "The estate sits on roughly six hectares of granite-and-mica "
            "schist across the heart of Côte-Rôtie, with a stake in the "
            "Côte Brune-adjacent lieu-dit Le Combard. Old-school élevage in "
            "barrels of varied age, low new oak, stems used selectively — "
            "the wines fall in the structured, savory, slow-aging camp "
            "rather than the modern fruit-forward style. FASS carries the "
            "domaine's full vertical of the Coeur de Combard parcel back "
            "to 2015, the basic Les Côtes, and a Saint-Joseph Blanc."
        ),
    ),
    P(
        slug="compagnie_de_lhermitage",
        name="Compagnie de l'Hermitage",
        country="France", region="Rhône",
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=[
            "Compagnie de lHermitage", "Compagnie L'Hermitage",
            "Compagnie l'Hermitage", "Lyle Fass Lelektsoglou",
            "Lyle Fass Charalambos Lelektsoglou", "Lyle Fass/Charalambos",
            "Georges Lelektsoglou", "Hector Adrien Charalambos Lelektsoglou",
        ],
        tags=["cote-rotie", "chateauneuf", "negoce", "natural-leaning"],
        summary=(
            "Lyle Fass's négociant project with the Greek-born winemaker "
            "Georges Lelektsoglou ('the Greek'), bottling tiny lots of Côte "
            "Rôtie La Brocarde, Châteauneuf-du-Pape lieu-dit Pignan, and "
            "Cairanne Vieilles Vignes alongside an entry-level VDF "
            "(Cuvée Ariane). The La Brocarde — single-parcel old-vine "
            "Syrah from the Côte Blonde — is the flagship; allocations are "
            "1-of-N limited list at FASS. Style is unfined / unfiltered, "
            "low SO2, traditional Rhône élevage. Adjacent in the FASS book "
            "to Julien Barge and the Cornas growers."
        ),
    ),
    P(
        slug="cuchet_beliando",
        name="Cuchet-Beliando",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Cuchet Beliando", "Cuchet-Beliando Cornas"],
        tags=["cornas", "syrah", "grower"],
        summary=(
            "Tiny Cornas grower — Mathilde Cuchet (Domaine du Coulet alum) "
            "and Aurélien Béliando. FASS carries a deep vintage vertical "
            "($95–$117) of their single Cornas cuvée, 2015 through 2020, "
            "which is unusual for the appellation at this price point — "
            "most growers release one or two vintages at a time. Granite, "
            "whole-cluster, traditional élevage."
        ),
    ),
    P(
        slug="guillaume_gilles",
        name="Guillaume Gilles",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC", "Côtes du Rhône AOC", "Saint-Péray AOC"],
        farming=["organic"],
        importer_us=["Selection Massale"],
        tags=["cornas", "syrah", "grower"],
        summary=(
            "Robert Michel's apprentice and now spiritual heir — Guillaume "
            "Gilles farms the Chaillot, Reynards, and other south-Cornas "
            "parcels Michel championed, plus a Côtes du Rhône Les "
            "Peyrouses and a Saint-Péray. The wines are 100% whole-cluster, "
            "long-élevage in old oak, no new wood — drier, more savory, "
            "and longer-lived than the modern Cornas style. The Nouvelle R "
            "is the basic Cornas; the named lieu-dit bottlings are "
            "limited."
        ),
    ),
    P(
        slug="domaine_du_tunnel",
        name="Domaine du Tunnel",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC", "Saint-Péray AOC", "Saint-Joseph AOC",
                      "Condrieu AOC"],
        farming=["sustainable"],
        importer_us=["Selection Massale"],
        aliases=["Domaine du"],
        tags=["cornas", "saint-peray", "syrah"],
        summary=(
            "Stéphane Robert founded Domaine du Tunnel in 1996 from a "
            "rented one-hectare Cornas parcel; the domaine now spans "
            "Cornas, Saint-Péray (both still and roussanne-driven Pur "
            "Blanc / Prestige), Saint-Joseph, and a tiny Condrieu. Vin "
            "Noir is the flagship Cornas — old-vine Syrah from Champelrose, "
            "lifted, structured. Saint-Péray Pur Blanc is the white "
            "anchor: 100% Roussanne, old vines, mineral and dense."
        ),
    ),
    P(
        slug="domaine_des_pierres_seches",
        name="Domaine des Pierres Sèches",
        country="France", region="Rhône", sub_region="Saint-Joseph",
        appellations=["Saint-Joseph AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Domaine des"],
        tags=["saint-joseph", "syrah", "grower"],
        summary=(
            "Family-run Saint-Joseph grower based in the northern Ardèche "
            "hills. FASS imports the Cuvée 1930 (old-vine, both rouge and "
            "blanc, $63–$77 tier), the Revirand lieu-dit ($52), and basic "
            "Saint-Joseph blanc + rouge at the $30-ish entry level. "
            "Granite terraces, traditional élevage, no new oak."
        ),
    ),
    P(
        slug="gerard_courbis",
        name="Gérard Courbis",
        country="France", region="Rhône", sub_region="Saint-Joseph",
        appellations=["Saint-Joseph AOC", "Cornas AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Gerard Courbis", "Gerard Courbis Pere & Fils",
                 "Gerard Courbis Père & Fils", "Gerard Courbis et Fils"],
        tags=["saint-joseph", "cornas", "syrah"],
        summary=(
            "Saint-Joseph grower (no relation to the better-known Domaine "
            "Courbis at the southern end of the appellation). The Vieilles "
            "Vignes Saint-Joseph rouge anchors the book, with a small "
            "Cornas. Père & Fils era at FASS — Ludovic Courbis (his son) "
            "bottles his own Cornas separately."
        ),
    ),
    P(
        slug="ludovic_courbis",
        name="Ludovic Courbis",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["cornas", "syrah"],
        summary=(
            "Gérard Courbis's son's micro-domaine — just Cornas, two "
            "vintages typically in the FASS book ($67–$70). Worth tracking "
            "as the next-generation Courbis project."
        ),
    ),
    P(
        slug="jacques_lemenicier",
        name="Jacques Lemenicier",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC", "Saint-Péray AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["cornas", "saint-peray", "syrah"],
        summary=(
            "Veteran Cornas grower — basic Cornas ($42–$63) and the "
            "old-vine Père Laurier ($88–$102 selection). Saint-Péray Cuvée "
            "Élégance fills out the book. Traditional style, long élevage."
        ),
    ),
    P(
        slug="mickael_bourg",
        name="Mickael Bourg",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC", "Saint-Péray AOC"],
        farming=["biodynamic"],
        importer_us=["FASS Selections"],
        aliases=["Mikael Bourg"],
        tags=["cornas", "saint-peray", "syrah", "biodynamic"],
        summary=(
            "Vincent Paris alum (worked with Allemand before that) — "
            "Mickael's flagship is the Cornas Les P'tits Bout ($66–$72), "
            "with a Saint-Péray and an entry-level VDF La Démarcante "
            "(no AOC, native fermentation, no SO2 additions at bottling). "
            "Among the younger generation pushing Cornas in a more lifted, "
            "elegant direction."
        ),
    ),
    P(
        slug="emmanuel_verset",
        name="Emmanuel Verset",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["cornas", "syrah"],
        summary=(
            "Allemand's right-hand for many years — Emmanuel Verset now "
            "bottles his own Cornas under his name and a Signature cuvée. "
            "Stylistically downstream of Allemand: granite, whole-cluster, "
            "old wood, low SO2."
        ),
    ),
    P(
        slug="emmanuel_darnaud",
        name="Emmanuel Darnaud",
        country="France", region="Rhône", sub_region="Crozes-Hermitage",
        appellations=["Crozes-Hermitage AOC", "Saint-Joseph AOC"],
        farming=["sustainable"],
        importer_us=["Robert Kacher"],
        tags=["crozes-hermitage", "saint-joseph", "syrah"],
        summary=(
            "Crozes-Hermitage négociant-grower based in Mercurol — Au Fil "
            "du Temps is the well-known mid-tier Crozes ($42 at FASS), "
            "and Dardouille is the Saint-Joseph value. Mainstream press "
            "darling for sub-$50 Northern Rhône."
        ),
    ),
    P(
        slug="andre_francois",
        name="André François",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        appellations=["Côte-Rôtie AOC", "Condrieu AOC",
                      "Collines Rhodaniennes IGP"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Andre Francois"],
        tags=["cote-rotie", "condrieu", "syrah"],
        summary=(
            "Côte-Rôtie grower (Gerine lieu-dit, $44 tier — unusually low "
            "for the appellation), Condrieu La Maladière, and an IGP "
            "Quinet at $20. Value-tier Northern Rhône — the kind of name "
            "FASS surfaces when they want a sub-$50 Côte-Rôtie that still "
            "reads as a grower wine."
        ),
    ),
    P(
        slug="nicolas_champagneaux",
        name="Nicolas Champagneaux",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        appellations=["Côte-Rôtie AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["cote-rotie", "syrah", "grower"],
        summary=(
            "Côte-Rôtie grower with two named lieu-dit cuvées at FASS — "
            "Les Grands Palaces ($110) and La Dédicace ($68–$69). "
            "Small allocations, traditional style."
        ),
    ),
    P(
        slug="jean_michel_stephan",
        name="Jean-Michel Stéphan",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        appellations=["Côte-Rôtie AOC"],
        farming=["organic", "natural"],
        importer_us=["Selection Massale"],
        aliases=["Jean Michel Stephan", "Maison Stephan"],
        tags=["cote-rotie", "syrah", "natural"],
        summary=(
            "One of Côte-Rôtie's natural-wine anchors — Jean-Michel "
            "Stéphan farms whole-cluster, indigenous yeast, zero SO2 "
            "regimes on parcels in Coteaux du Bassenon and Coteaux du "
            "Tupin (both $146–$155 at FASS). Adjacent stylistically to "
            "Dard & Ribo and the Beaujolais Gang of Four — perfumed, "
            "lifted, sometimes vintage-variable. Le Grand Blanc VDF "
            "appears under 'Maison Stephan' in the data."
        ),
    ),
    P(
        slug="domaine_saint_damien",
        name="Domaine Saint-Damien",
        country="France", region="Rhône", sub_region="Gigondas",
        appellations=["Gigondas AOC"],
        farming=["sustainable"],
        importer_us=["Selection Massale"],
        tags=["gigondas", "southern-rhone", "grenache"],
        summary=(
            "Joël Saurel's family domaine in Gigondas — the Vieilles "
            "Vignes Gigondas at $32 is one of the appellation's standing "
            "values for old-vine Grenache."
        ),
    ),
    P(
        slug="domaine_de_cote_epine",
        name="Domaine de la Côte Saint-Épine",
        country="France", region="Rhône", sub_region="Saint-Joseph",
        appellations=["Saint-Joseph AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Domaine de Cote Epine", "Domaine de la Cote St Epine",
                 "Domaine de la Côte"],
        tags=["saint-joseph", "syrah"],
        summary=(
            "Saint-Joseph grower — Vieilles Vignes Cuvée Spéciale / Cuvée "
            "Réserve ($36–$38) and an entry-level Cuvée Élégance ($26–$29). "
            "Sub-$40 grower Saint-Joseph is rare; FASS slot."
        ),
    ),
    P(
        slug="domaine_blachon",
        name="Domaine Blachon",
        country="France", region="Rhône", sub_region="Saint-Joseph",
        appellations=["Saint-Joseph AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Cave Sebastien Blachon", "Sebastien Blachon"],
        tags=["saint-joseph", "syrah"],
        summary=(
            "Sébastien Blachon's Saint-Joseph domaine — Margariat "
            "(rouge, ~$60) and Isaline (blanc) bottlings."
        ),
    ),
    P(
        slug="elie_bancel",
        name="Élie Bancel",
        country="France", region="Rhône", sub_region="Cornas",
        appellations=["Cornas AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["cornas", "syrah"],
        summary=(
            "Single-cuvée Cornas grower at FASS ($95)."
        ),
    ),
    P(
        slug="maison_alexandrins",
        name="Maison Les Alexandrins",
        country="France", region="Rhône",
        appellations=["Hermitage AOC", "Cornas AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["hermitage", "cornas", "negoce"],
        summary=(
            "Négociant project led by Nicolas Jaboulet (ex-Jaboulet) with "
            "consulting Crozes/Hermitage growers. Hermitage Blanc and "
            "Rouge alongside Cornas at $43–$90 tier. Modern, clean style "
            "vs. the natural cluster — useful for value Northern Rhône."
        ),
    ),
    P(
        slug="e_guigal",
        name="E. Guigal",
        country="France", region="Rhône", sub_region="Côte-Rôtie",
        appellations=["Côte-Rôtie AOC", "Hermitage AOC",
                      "Châteauneuf-du-Pape AOC", "Condrieu AOC"],
        farming=["sustainable"],
        importer_us=["Vintus"],
        tags=["cote-rotie", "syrah", "icon", "collector"],
        summary=(
            "The Ampuis house that built the modern Côte-Rôtie market. "
            "Guigal's single-vineyard La-Las — La Mouline (1966, "
            "Côte Blonde, with Viognier), La Landonne (1978, Côte Brune, "
            "pure Syrah), and La Turque (1985, replanted Côte Brune) — "
            "are among the world's most collected Syrahs, traditionally "
            "released in 3-packs at FASS. Outside the icons, the Brune "
            "et Blonde, Château d'Ampuis, and the Hermitage Ex-Voto "
            "round out the serious tier. Off-style for the natural-leaning "
            "vault but a Rhône completist's anchor."
        ),
    ),
]


# ============================================================================
# Burgundy — growers + Chablis cluster
# ============================================================================

BURGUNDY = [
    P(
        slug="pierre_brisset",
        name="Pierre Brisset",
        country="France", region="Burgundy",
        appellations=["Bourgogne AOC", "Pommard AOC", "Vosne-Romanée AOC",
                      "Chambolle-Musigny AOC", "Échezeaux Grand Cru AOC",
                      "Meursault AOC", "Chassagne-Montrachet AOC",
                      "Nuits-Saint-Georges AOC", "Saint-Aubin AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Maison Brisset", "Pierre Briseet"],
        tags=["burgundy", "negoce", "1er-cru", "grand-cru"],
        summary=(
            "FASS's Burgundy flagship négociant. The book spans the full "
            "Côte d'Or pyramid: Bourgogne Blanc / Rouge Cuvée Cassanéas + "
            "Cuvée Gabrius at the base; 1er Crus in Pommard (Les Charmots, "
            "Les Argillières), Volnay-adjacent, Vosne-Romanée 1er Cru "
            "Les Rouges du Dessus, Chambolle-Musigny 1er Cru Les Noirots "
            "and Les Cras, Nuits-Saint-Georges 1er Cru Aux Thorey, "
            "Chassagne-Montrachet 1er Cru Abbaye de Morgeot, Saint-Aubin "
            "1er Cru Sur Roche du Gamay, Meursault Les Grands Charrons; "
            "topped by an Échezeaux Grand Cru at $325. Same house as "
            "'Maison Brisset' in the raw data."
        ),
    ),
    P(
        slug="jj_girard",
        name="J.J. Girard",
        country="France", region="Burgundy",
        appellations=["Savigny-lès-Beaune AOC", "Beaune AOC", "Pommard AOC",
                      "Volnay AOC", "Pernand-Vergelesses AOC",
                      "Chassagne-Montrachet AOC", "Meursault AOC",
                      "Puligny-Montrachet AOC", "Gevrey-Chambertin AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["JJ Girard", "J.J. Girard"],
        tags=["burgundy", "savigny-les-beaune", "pommard", "volnay"],
        summary=(
            "Girard family domaine in Savigny-lès-Beaune — 1er Cru holdings "
            "in Beaune (Clos du Roi), Pommard (Les Chaponnières), Volnay "
            "(En Chevret, Mitans), Savigny (Les Peuillets, Les Narbantons), "
            "Pernand (Les Fichots), plus white 1er Cru in Meursault Les "
            "Charmes and Puligny Les Referts. Mid-tier Côte de Beaune "
            "grower in the $32–$120 range — useful for filling Burgundy "
            "1er Cru gaps."
        ),
    ),
    P(
        slug="chavy_chouet",
        name="Chavy-Chouet",
        country="France", region="Burgundy", sub_region="Meursault",
        appellations=["Meursault AOC", "Meursault 1er Cru",
                      "Puligny-Montrachet AOC", "Puligny-Montrachet 1er Cru",
                      "Saint-Aubin 1er Cru", "Maranges AOC",
                      "Bourgogne AOC"],
        farming=["sustainable"],
        importer_us=["Robert Chadderdon"],
        tags=["meursault", "puligny", "chardonnay"],
        summary=(
            "Hubert and Romaric Chavy's domaine in Meursault — known for "
            "racy, mineral whites with restrained oak. Top of the FASS "
            "book: Meursault 1er Cru Les Genevrières ($130–$134), "
            "Puligny-Montrachet 1er Cru Champs Gains ($129–$132), "
            "Saint-Aubin 1er Cru Les Murgers des Dents de Chien ($98–$102); "
            "village Meursault Narvaux and the Clos de Corvées de Citeau "
            "monopole at $69–$78; Bourgogne Les Femelottes at the base "
            "($35). Long Burgundy reference list for one estate."
        ),
    ),
    P(
        slug="julien_cruchandeau",
        name="Julien Cruchandeau",
        country="France", region="Burgundy", sub_region="Hautes-Côtes de Nuits",
        appellations=["Hautes-Côtes de Nuits AOC", "Bouzeron AOC",
                      "Ladoix AOC", "Saint-Aubin 1er Cru",
                      "Auxey-Duresses 1er Cru", "Beaune AOC",
                      "Nuits-Saint-Georges AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["hautes-cotes", "ladoix", "saint-aubin", "value-burgundy"],
        summary=(
            "Côte de Nuits grower based in the Hautes-Côtes — Ladoix Les "
            "Ranches, Bouzeron Cuvée Massale (Aligoté), Saint-Aubin 1er "
            "Cru L'Amandier, Auxey-Duresses 1er Cru Les Duresses, Nuits-"
            "Saint-Georges Aux Saint-Jacques VV. Quietly biodynamic-"
            "leaning and almost entirely sub-$70. The kind of grower "
            "FASS finds in the Burgundy second tier."
        ),
    ),
    P(
        slug="laurent_boussey",
        name="Laurent Boussey",
        country="France", region="Burgundy", sub_region="Monthelie",
        appellations=["Volnay AOC", "Volnay 1er Cru", "Monthelie AOC",
                      "Monthelie 1er Cru", "Meursault AOC", "Bourgogne AOC",
                      "Aloxe-Corton AOC", "Auxey-Duresses AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Laurent & Karen Boussey"],
        tags=["volnay", "monthelie", "meursault"],
        summary=(
            "Volnay-Monthelie grower with parcels in Volnay 1er Cru "
            "Taillepieds, Monthelie 1er Cru Sur la Velle / Champs Fulliot / "
            "Les Riottes, plus village Meursault VV and Aloxe-Corton Les "
            "Valozières. Pairs with Karen Boussey on the Meursault 1er "
            "Cru Les Caillerets ($92)."
        ),
    ),
    P(
        slug="domaine_berlancourt",
        name="Domaine Berlancourt",
        country="France", region="Burgundy",
        appellations=["Bourgogne AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["bourgogne", "pinault-burgundy"],
        summary=(
            "François Pinault's Burgundy project at the Bourgogne-tier — "
            "Cuvée Madamoiselle (Blanc), Cuvée La Demoiselle, Les "
            "Equinces (Bourgogne Blanc), Bourgogne Rosé, Bourgogne Rouge. "
            "Approachable entry to Pinault's wider Burgundy ambitions "
            "(Domaine Eugénie, Clos de Tart)."
        ),
    ),
    P(
        slug="remi_poisot",
        name="Rémi Poisot",
        country="France", region="Burgundy",
        appellations=["Romanée-Saint-Vivant Grand Cru",
                      "Corton-Charlemagne Grand Cru",
                      "Corton Grand Cru", "Aloxe-Corton 1er Cru",
                      "Pernand-Vergelesses AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["grand-cru", "romanee-saint-vivant", "corton-charlemagne"],
        summary=(
            "Surprise Grand-Cru-tier label at FASS — Romanée-Saint-Vivant "
            "($470–$600), Corton-Charlemagne ($173–$222), Corton "
            "Bressandes, Aloxe-Corton 1er Cru, plus a Pernand-Vergelesses "
            "1er Cru En Carradeaux at the entry tier. Tiny allocations "
            "but the depth of cru makes this a serious watch-list name."
        ),
    ),
    P(
        slug="vincent_ledy",
        name="Vincent Ledy",
        country="France", region="Burgundy",
        sub_region="Hautes-Côtes de Nuits",
        appellations=["Hautes-Côtes de Nuits AOC",
                      "Nuits-Saint-Georges 1er Cru"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["hautes-cotes", "nuits-saint-georges"],
        summary=(
            "Hautes-Côtes de Nuits grower with a Nuits-Saint-Georges 1er "
            "Cru Les Porrets-Saint-Georges Jeunes Vignes ($77). La "
            "Vacherotte is the Hautes-Côtes Pinot Noir cuvée at $39–$42."
        ),
    ),
    P(
        slug="dubreuil_fontaine",
        name="Dubreuil-Fontaine",
        country="France", region="Burgundy", sub_region="Pernand-Vergelesses",
        appellations=["Corton Grand Cru", "Pernand-Vergelesses AOC",
                      "Aloxe-Corton AOC"],
        farming=["sustainable"],
        importer_us=["Polaner"],
        tags=["corton", "pernand-vergelesses"],
        summary=(
            "Pernand-Vergelesses domaine with Corton Bressandes and Corton "
            "Clos du Roi Grand Cru parcels — classical Côte d'Or, long "
            "history, mid-priced for the cru level ($88–$90)."
        ),
    ),
    P(
        slug="garaudet",
        name="Garaudet Père & Fils",
        country="France", region="Burgundy", sub_region="Monthelie",
        appellations=["Monthelie AOC", "Monthelie 1er Cru", "Volnay AOC",
                      "Pommard AOC", "Meursault AOC", "Bourgogne AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Garaudet", "Garaudet Pere & Fils", "SARL Garaudet",
                 "SARL Garaudet Pere & Fils", "Sarl Garaudet Pere et Fils"],
        tags=["monthelie", "volnay", "pommard"],
        summary=(
            "Pierre Garaudet's Monthelie-based domaine — Monthelie 1er Cru "
            "Les Champs Fulliot (both blanc and rouge), Les Riottes, "
            "village Volnay VV, Pommard VV, Meursault Limozin and VV. "
            "Classical Côte de Beaune grower; one of FASS's deeper "
            "Monthelie sources."
        ),
    ),
    P(
        slug="philippe_naddef",
        name="Philippe Naddef",
        country="France", region="Burgundy", sub_region="Gevrey-Chambertin",
        appellations=["Gevrey-Chambertin AOC", "Gevrey-Chambertin 1er Cru",
                      "Marsannay AOC", "Fixin AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Philippe Nadeff", "Phillippe Naddef", "Michel Naddef",
                 "Domaine Philippe", "Domaine Philippe Naddef"],
        tags=["gevrey-chambertin", "marsannay", "fixin"],
        summary=(
            "Côte de Nuits grower with parcels in Gevrey-Chambertin VV, "
            "Gevrey-Chambertin 1er Cru Champeaux (highlighted at $282 in "
            "the data as 'Michel Naddef'), Marsannay Les Genelières, "
            "and Fixin VV / Fixin Blanc. Spelling variants are heavy in "
            "the raw data — all consolidate here."
        ),
    ),
    P(
        slug="daniel_etienne_defaix",
        name="Daniel-Étienne Defaix",
        country="France", region="Burgundy", sub_region="Chablis",
        appellations=["Chablis AOC", "Chablis 1er Cru"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Domaine Daniel-Etienne Defaix"],
        tags=["chablis", "1er-cru", "aged-chablis"],
        summary=(
            "Chablis grower whose unique calling card is releasing 1er "
            "Cru only after 8-10 years of bottle age — Les Lys, Côte de "
            "Léchet, Vaillons all show up on the FASS list at 10+ years "
            "post-vintage. Stylistically distinctive vs. modern Chablis: "
            "deeper, more honeyed, ready-to-drink."
        ),
    ),
    P(
        slug="jean_dauvissat",
        name="Jean Dauvissat Père & Fils",
        country="France", region="Burgundy", sub_region="Chablis",
        appellations=["Chablis AOC", "Chablis 1er Cru"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Jean Dauvissat", "Jean Dauvissat Pere & Fils",
                 "Jean Dauvissat Père & Fils"],
        tags=["chablis", "1er-cru"],
        summary=(
            "Jean Dauvissat — distinct from the better-known Vincent or "
            "René et Vincent Dauvissat lineage, though family-adjacent. "
            "Chablis 1er Cru list at FASS is unusually broad: Côte de "
            "Léchet, Fourchaume, Vaillons, Montmains, Mont-Main Sourdelle, "
            "Bas de Fourchaume, plus village Chablis Terroirs de Milly / "
            "Les Tierces. Sub-$60 across the board."
        ),
    ),
    P(
        slug="laurent_tribut",
        name="Laurent Tribut",
        country="France", region="Burgundy", sub_region="Chablis",
        appellations=["Chablis AOC", "Chablis 1er Cru"],
        farming=["sustainable"],
        importer_us=["Polaner"],
        tags=["chablis", "1er-cru", "grower"],
        summary=(
            "Vincent Dauvissat's brother-in-law — same Poinchy hamlet, "
            "same conservative Chablis aesthetic: large neutral oak, no "
            "battonage, slow élevage. Chablis 1er Cru Beauroy and Côte "
            "de Léchet are the FASS book ($68–$69)."
        ),
    ),
    P(
        slug="sebastien_dampt",
        name="Sébastien Dampt",
        country="France", region="Burgundy", sub_region="Chablis",
        appellations=["Chablis AOC", "Chablis 1er Cru",
                      "Chablis Grand Cru"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Sebastien Dampt"],
        tags=["chablis", "1er-cru", "grand-cru"],
        summary=(
            "Chablis grower in Milly — 1er Crus Vaillons, Côte de Léchet, "
            "Les Beugnons; the Maison Dampt négoce side carries Chablis "
            "Grand Cru Bougros at $62. Sub-$45 across most of the book."
        ),
    ),
    P(
        slug="domaine_servin",
        name="Domaine Servin",
        country="France", region="Burgundy", sub_region="Chablis",
        appellations=["Chablis AOC", "Chablis 1er Cru",
                      "Chablis Grand Cru"],
        farming=["sustainable"],
        importer_us=["Polaner"],
        tags=["chablis", "1er-cru", "grand-cru"],
        summary=(
            "Long-tenured Chablis estate — Chablis Grand Cru Les Clos at "
            "$85 is the headline; Chablis 1er Cru Mont de Tonnerre at "
            "$35 the entry."
        ),
    ),
]


# ============================================================================
# Loire
# ============================================================================

LOIRE = [
    P(
        slug="domaine_des_roches_neuves",
        name="Domaine des Roches Neuves",
        country="France", region="Loire", sub_region="Saumur-Champigny",
        appellations=["Saumur-Champigny AOC", "Saumur AOC"],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Louis/Dressner"],
        tags=["saumur-champigny", "cabernet-franc", "biodynamic", "icon"],
        summary=(
            "Thierry Germain's biodynamic Saumur-Champigny estate — one of "
            "the Loire's most influential producers of the modern era. The "
            "FASS book is deep: Franc de Pied (own-rooted Cabernet Franc), "
            "Clos de l'Échelier (single-vineyard), Les Mémoires (old-vine "
            "selection), Clos Romans (white), Marginale, plus Clos "
            "d'Échalier Blanc. Stylistically silky, perfumed, low SO2; "
            "Roches Neuves is the reference for what biodynamic Cabernet "
            "Franc can be at this latitude."
        ),
    ),
    P(
        slug="domaine_clos_de_lecotard",
        name="Domaine Clos de l'Écotard",
        country="France", region="Loire", sub_region="Saumur",
        appellations=["Saumur AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["saumur", "chenin-blanc"],
        summary=(
            "Saumur Blanc grower — the Pentes des Clos de l'Écotard "
            "(Chenin Blanc) is the cuvée at FASS, $70."
        ),
    ),
]


# ============================================================================
# Beaujolais
# ============================================================================

BEAUJOLAIS = [
    P(
        slug="yvon_metras",
        name="Yvon Métras",
        country="France", region="Beaujolais", sub_region="Fleurie",
        appellations=["Fleurie AOC", "Beaujolais Villages AOC"],
        farming=["organic", "natural"],
        importer_us=["Camille Rivière / Selection Massale"],
        aliases=["Yvon Metras"],
        tags=["beaujolais", "fleurie", "natural", "icon"],
        summary=(
            "Among the elder statesmen of natural Beaujolais — Métras "
            "farms Fleurie organically, ferments with native yeast, and "
            "ages without added SO2. Allocations are tight; FASS gets the "
            "Beaujolais Villages cuvée at sub-$50. The Fleurie cuvées "
            "rarely make it stateside in retail."
        ),
    ),
    P(
        slug="jean_foillard",
        name="Jean Foillard",
        country="France", region="Beaujolais", sub_region="Morgon",
        appellations=["Morgon AOC"],
        farming=["organic", "natural"],
        importer_us=["Kermit Lynch"],
        tags=["beaujolais", "morgon", "natural", "gang-of-four", "icon"],
        summary=(
            "One of Marcel Lapierre's 'Gang of Four' (with Lapierre, "
            "Thévenet, and Breton) — the founding generation of natural "
            "Beaujolais. Foillard's Morgon Côte du Py is the stateside "
            "benchmark; FASS carries the Morgon Classique at $25, the "
            "entry-level expression. Whole-cluster, semi-carbonic, native "
            "yeast, low/no SO2."
        ),
    ),
    P(
        slug="chateau_thivin",
        name="Château Thivin",
        country="France", region="Beaujolais", sub_region="Côte-de-Brouilly",
        appellations=["Côte-de-Brouilly AOC", "Brouilly AOC"],
        farming=["sustainable"],
        importer_us=["Kermit Lynch"],
        tags=["beaujolais", "cote-de-brouilly", "gamay", "icon"],
        summary=(
            "The reference estate of Côte-de-Brouilly — Geoffray family, "
            "Mont Brouilly slope. FASS book is wide: Cuvée Zaccharie (top "
            "cuvée), Cuvée Godefroy, La Chapelle (old vines), Les Griottes "
            "de Brulhié. Granite-and-blue-stone (cornieule) terroir gives "
            "the Thivin Gamays their characteristic mineral grip. Classical "
            "rather than natural, but a Beaujolais icon by any measure."
        ),
    ),
    P(
        slug="lafarge_vial",
        name="Lafarge-Vial",
        country="France", region="Beaujolais", sub_region="Fleurie",
        appellations=["Fleurie AOC"],
        farming=["biodynamic"],
        importer_us=["Skurnik"],
        tags=["beaujolais", "fleurie", "biodynamic"],
        summary=(
            "Frédéric Lafarge (of Michel Lafarge in Volnay) with Chantal "
            "Vial's family Fleurie domaine — biodynamic, low-intervention. "
            "Clos Vernay and La Joie du Palais at $38 each."
        ),
    ),
    P(
        slug="domaine_du_vissoux",
        name="Domaine du Vissoux",
        country="France", region="Beaujolais", sub_region="Fleurie",
        appellations=["Fleurie AOC", "Moulin-à-Vent AOC"],
        farming=["organic"],
        importer_us=["Weygandt-Metzler"],
        tags=["beaujolais", "fleurie", "moulin-a-vent"],
        summary=(
            "Pierre-Marie Chermette — Fleurie Poncié is the long-standing "
            "value tier ($26), with Moulin-à-Vent Les Trois Roches and "
            "Brouilly Pierreux as the cru reference points."
        ),
    ),
]


# ============================================================================
# Champagne — grower / late-disgorged tier
# ============================================================================

CHAMPAGNE = [
    P(
        slug="caillez_lemaire",
        name="Caillez-Lemaire",
        country="France", region="Champagne",
        appellations=["Champagne AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["champagne", "grower", "vintage"],
        summary=(
            "Vallée de la Marne grower whose calling card is Pinot Meunier "
            "depth (Pur Meunier) and aged vintage releases (Vinothèque "
            "2008 at $120). Cuvée Jadis (2010/2011/2012), Chardonnay de la "
            "Vallée Blanc de Blancs Brut Nature, Reflets / Éclats / Rosé "
            "Extra Brut at the NV tier. Hits the grower-champagne taste "
            "filter cleanly."
        ),
    ),
    P(
        slug="marie_demets",
        name="Marie Demets",
        country="France", region="Champagne",
        appellations=["Champagne AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["champagne", "grower", "extra-brut"],
        summary=(
            "Marie Demets's Vallée de la Marne grower house — Extra Brut "
            "and zero-dosage focus. Intransigeance, Les Fins (100% "
            "Chardonnay), La Forêt (100% Chardonnay), Singularité (Pinot "
            "Blanc), Cœur de Saignée Rosé, Cuvée 19ème Siècle, Tradition "
            "Blanc de Noirs."
        ),
    ),
    P(
        slug="clement_perseval",
        name="Clément Perseval",
        country="France", region="Champagne", sub_region="Chamery",
        appellations=["Champagne AOC", "Champagne 1er Cru"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["champagne", "grower", "1er-cru", "extra-brut"],
        summary=(
            "Chamery 1er Cru grower — Les Tremblaies Extra Brut 2013, "
            "Les Rouleaux Blanc de Blancs 2016, La Luth Extra Brut 2016, "
            "Millésime Extra Brut 2013 ($155). Tiny production, single-"
            "parcel focus. Distinct from his cousin's house Perseval-Farge."
        ),
    ),
    P(
        slug="perseval_farge",
        name="Perseval-Farge",
        country="France", region="Champagne", sub_region="Chamery",
        appellations=["Champagne AOC", "Champagne 1er Cru"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Perseval Farge"],
        tags=["champagne", "grower", "1er-cru"],
        summary=(
            "Chamery 1er Cru grower — Cuvée La Pucelle Brut Nature, "
            "Cuvée Jean Baptiste 1er Cru Brut, Coteaux Champenois Blanc, "
            "Les Goulats Brut Nature. Long-standing FASS staple."
        ),
    ),
    P(
        slug="pierre_callot",
        name="Pierre Callot",
        country="France", region="Champagne", sub_region="Avize",
        appellations=["Champagne Grand Cru", "Avize Grand Cru"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["champagne", "grand-cru", "blanc-de-blancs"],
        summary=(
            "Avize Grand Cru grower — Blanc de Blancs Vignes Anciennes "
            "(Avats parcel, 2014) at $46–$47. Compact lineup, high "
            "altitude Côte des Blancs sourcing."
        ),
    ),
    P(
        slug="pierre_moncuit",
        name="Pierre Moncuit",
        country="France", region="Champagne",
        sub_region="Le Mesnil-sur-Oger",
        appellations=["Champagne Grand Cru"],
        farming=["sustainable"],
        importer_us=["Polaner"],
        tags=["champagne", "grand-cru", "le-mesnil", "blanc-de-blancs"],
        summary=(
            "Le Mesnil-sur-Oger Grand Cru grower — Les Grands Blancs "
            "Extra Brut at the FASS price point ($53). Old-vine Mesnil "
            "Chardonnay, classical Champagne style."
        ),
    ),
    P(
        slug="pierre_gimmonet",
        name="Pierre Gimmonet & Fils",
        country="France", region="Champagne", sub_region="Cuis",
        appellations=["Champagne 1er Cru", "Champagne Grand Cru"],
        farming=["sustainable"],
        importer_us=["Terry Theise / Skurnik"],
        tags=["champagne", "grower", "blanc-de-blancs", "special-club"],
        summary=(
            "Cuis 1er Cru grower — long-running Terry Theise import. "
            "Special Club Grands Terroirs de Chardonnay 2015 at FASS "
            "($75). Reference Côte des Blancs grower, classical style."
        ),
    ),
    P(
        slug="marc_hebrart",
        name="Marc Hébrart",
        country="France", region="Champagne", sub_region="Mareuil-sur-Aÿ",
        appellations=["Champagne 1er Cru"],
        farming=["sustainable"],
        importer_us=["Terry Theise / Skurnik"],
        aliases=["Marc Hebrart"],
        tags=["champagne", "grower", "special-club"],
        summary=(
            "Jean-Paul Hébrart's Mareuil-sur-Aÿ domaine — Special Club "
            "Brut 2021 in the FASS book ($77). One of the reference grower "
            "houses on the Pinot Noir side of the Vallée de la Marne."
        ),
    ),
    P(
        slug="paul_drappier",
        name="Drappier (Paul Drappier)",
        country="France", region="Champagne", sub_region="Urville",
        appellations=["Champagne AOC"],
        farming=["sustainable"],
        importer_us=["Drappier USA"],
        tags=["champagne", "aube"],
        summary=(
            "Family-owned Aube house (Pinot Noir-led) — the Brut Charles "
            "de Gaulle is the historic single-vineyard NV cuvée ($58)."
        ),
    ),
    P(
        slug="etienne_calsac",
        name="Étienne Calsac",
        country="France", region="Champagne", sub_region="Avize",
        appellations=["Champagne AOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Etienne Calsac"],
        tags=["champagne", "grower", "extra-brut", "blanc-de-blancs"],
        summary=(
            "Avize-based grower in the new generation cohort — Échappée "
            "Belle Blanc de Blancs Extra-Brut NV ($48). Small production."
        ),
    ),
    P(
        slug="diot_benoit",
        name="Diot-Légras",
        country="France", region="Champagne", sub_region="Le Mesnil-sur-Oger",
        appellations=["Champagne Grand Cru"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Diot Benoit", "Diot-Legras", "Diot-Legras Les"],
        tags=["champagne", "grand-cru", "le-mesnil", "blanc-de-blancs"],
        summary=(
            "Le Mesnil-sur-Oger Grand Cru grower — Millésime Vieilles "
            "Vignes Grand Cru 2008 / 2010 at $75–$77, plus a Mesnil VV "
            "Grand Cru 2010 at $94. Aged Mesnil Chardonnay focus."
        ),
    ),
    P(
        slug="sekthaus_raumland",
        name="Sekthaus Raumland",
        country="Germany", region="Rheinhessen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["sekt", "method-traditional", "german-sparkling"],
        summary=(
            "Germany's reference traditional-method Sekt house — Volker "
            "Raumland is to German sparkling what Schäfer-Fröhlich is to "
            "Nahe Riesling. FASS book: Triumvirat XV Grande Cuvée Brut "
            "2015, Pinot Noir Grande Réserve Brut 2012, Chardonnay "
            "Reserve Brut 2015, Méthode Traditionnelle Cuvée Marie-Luise "
            "2019. Long-aged, dosage-restrained."
        ),
    ),
]


# ============================================================================
# Mosel / Nahe
# ============================================================================

MOSEL_NAHE = [
    P(
        slug="markus_molitor",
        name="Markus Molitor",
        country="Germany", region="Mosel",
        sub_region="Zeltingen / Wehlen / Bernkastel",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Vom Boden"],
        aliases=["Markus Moitor"],
        tags=["mosel", "riesling", "auslese", "icon"],
        summary=(
            "Mosel's largest serious grower-style estate — roughly 100 "
            "hectares across the middle Mosel. The capsule color system "
            "(green dry, white off-dry, gold sweet) and the * ranking "
            "stack (***  reserve quality) make Molitor's range one of "
            "the easier Mosel verticals to read. FASS carries the "
            "Auslese tier deep: Zeltinger Sonnenuhr / Wehlener Sonnenuhr / "
            "Brauneberger Juffer-Sonnenuhr Auslese * / ** / *** in all "
            "three capsule colors, plus Pinot-Blanc-based Wehlener "
            "Klosterberg Auslese*** and Kabinetts across Zeltinger / "
            "Graacher / Wehlener / Bernkasteler / Ürziger. Bedrock Mosel."
        ),
    ),
    P(
        slug="martin_muellen",
        name="Martin Müllen",
        country="Germany", region="Mosel",
        sub_region="Traben-Trarbach",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Martin Muellen", "Martin Mullen"],
        tags=["mosel", "riesling", "trocken", "grower"],
        summary=(
            "Tiny Traben-Trarbach grower making intensely dry Riesling "
            "from Trarbacher Hühnerberg and Kröver Paradies — Hühnerberg "
            "Spätlese Trocken ** + ***, Kröver Paradies Spätlese Trocken "
            "* Fallay / ** Alte Reben, plus a Riesling Trocken Revival "
            "and a small Trarbacher Ungsberg Spätburgunder. The trocken "
            "stack stair-steps cleanly by ripeness level."
        ),
    ),
    P(
        slug="jj_prum",
        name="J.J. Prüm",
        country="Germany", region="Mosel", sub_region="Wehlen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Rudi Wiest"],
        aliases=["JJ Prum", "J.J. Prum"],
        tags=["mosel", "riesling", "icon"],
        summary=(
            "The reference estate of off-dry Mosel Riesling — Manfred "
            "Prüm's house in Wehlen. Wehlener Sonnenuhr Kabinett and "
            "Graacher Himmelreich Auslese are the FASS book picks. The "
            "house style — sulfur-prominent in youth, mind-bendingly "
            "long-aging, slate-driven — is one of the wine world's "
            "stylistic anchors."
        ),
    ),
    P(
        slug="selbach_oster",
        name="Selbach-Oster",
        country="Germany", region="Mosel", sub_region="Zeltingen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Terry Theise / Skurnik"],
        tags=["mosel", "riesling", "gg", "kabinett"],
        summary=(
            "Johannes Selbach's Zeltingen estate — Zeltinger Sonnenuhr GG "
            "and Zeltinger Himmelreich Anrecht (a single-parcel "
            "ungrafted-vine cuvée). The Spätlese Feinherb Ur Alte Reben "
            "and other Zeltinger Sonnenuhr expressions round out the "
            "FASS list, all in the $37–$39 band."
        ),
    ),
    P(
        slug="spater_veit",
        name="Später-Veit",
        country="Germany", region="Mosel", sub_region="Piesport",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Spater Veit", "Spater-Veit"],
        tags=["mosel", "riesling", "pinot-noir", "piesporter"],
        summary=(
            "Piesporter grower with an unusual depth in Pinot Noir for "
            "the Mosel — Pinot Noir Privat ($66–$74) and Pinot Noir "
            "Reserve. The Riesling side covers Piesporter Goldtröpfchen "
            "Auslese (2018), Domherr Auslese (2005), and Goldtröpfchen "
            "Spätlese Krank (2012)."
        ),
    ),
    P(
        slug="wilhelm_weber_osterman",
        name="Wilhelm Weber-Osterman",
        country="Germany", region="Mosel", sub_region="Brauneberg",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["mosel", "riesling", "aged-mosel", "auslese"],
        summary=(
            "Aged-stock Brauneberger Juffer specialist — Brauneberger "
            "Juffer Auslese 1989 / 1993 (three lots) at $33–$42, plus "
            "Wintricher Großer Hergott Spätlese 1992. The kind of cellar "
            "release that the FASS book opportunistically surfaces."
        ),
    ),
    P(
        slug="jakob_schneider",
        name="Jakob Schneider",
        country="Germany", region="Nahe", sub_region="Niederhausen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["nahe", "riesling", "trocken"],
        summary=(
            "Niederhausen Nahe grower — Hermannshöhle Riesling Trocken "
            "Magnus at FASS ($36)."
        ),
    ),
    P(
        slug="gut_hermannsberg",
        name="Gut Hermannsberg",
        country="Germany", region="Nahe", sub_region="Niederhausen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Vom Boden"],
        tags=["nahe", "riesling", "gg", "icon"],
        summary=(
            "One of the historic Nahe estates (formerly state-owned "
            "Staatsweingut Niederhausen) — Kupfergrube, Hermannsberg, "
            "Felsenberg, and Traiser Bastei are the GG vineyards. FASS "
            "carries Kupfergrube GG Reserve 2020 ($109), Hermannsberg GG "
            "Reserve 2019, Bastei GG, Felsenberg GG, plus the entry-tier "
            "7 Terroirs Trocken. Geological depth is the calling card — "
            "slate, porphyry, melaphyre across one estate."
        ),
    ),
    P(
        slug="k_h_schneider",
        name="K.H. Schneider",
        country="Germany", region="Nahe",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["nahe", "riesling", "gg"],
        summary=(
            "Karl Heinz Schneider — Nahe GG Riesling at value pricing: "
            "Königsfels GG and Felsenberg GG both under $40, plus "
            "Domberg and Marbach Riesling Spätlese in the low-$20s. "
            "Useful Nahe value-tier."
        ),
    ),
]


# ============================================================================
# Pfalz / Rheinhessen / Rheingau / Baden / Franken
# ============================================================================

GERMANY_OTHER = [
    P(
        slug="dr_wehrheim",
        name="Dr. Wehrheim",
        country="Germany", region="Pfalz", sub_region="Birkweiler",
        appellations=[],
        farming=["organic"],
        importer_us=["Vom Boden"],
        aliases=["Dr Wehrheim", "Dr. Wehreim"],
        tags=["pfalz", "kastanienbusch", "gg", "biodynamic-leaning"],
        summary=(
            "Birkweiler family estate — neighbors of Rebholz on the "
            "Kastanienbusch hill (the porphyry-pink-sandstone GG that is "
            "Pfalz's most distinctive grand cru). FASS book covers "
            "Kastanienbusch Riesling GG (multiple vintages), Mandelberg "
            "Weissburgunder GG, Sonnenschein Spätburgunder GG, and "
            "Chardonnay Roisenberg. Quietly biodynamic-leaning."
        ),
    ),
    P(
        slug="dr_burklin_wolf",
        name="Dr. Bürklin-Wolf",
        country="Germany", region="Pfalz", sub_region="Wachenheim",
        appellations=[],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Vom Boden"],
        aliases=["Dr Burklin Wolf"],
        tags=["pfalz", "riesling", "biodynamic", "icon", "gg"],
        summary=(
            "Among Pfalz's largest top-tier estates — fully biodynamic "
            "since 2005, using its own cru classification (G.C. / P.C.) "
            "that pre-dates the VDP system. Pechstein, Kirchenstück, "
            "Jesuitengarten and the rest of the Mittelhaardt grand crus "
            "all in the book. The FASS price ($200) suggests a single "
            "cuvée — Pechstein Riesling G.C., the basalt-dominant cru "
            "across from Forster Ungeheuer."
        ),
    ),
    P(
        slug="a_christmann",
        name="A. Christmann",
        country="Germany", region="Pfalz", sub_region="Gimmeldingen",
        appellations=[],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Skurnik"],
        aliases=["Christmann"],
        tags=["pfalz", "riesling", "biodynamic", "gg", "icon"],
        summary=(
            "Steffen Christmann's Gimmeldingen estate — biodynamic, VDP "
            "Adlerwein. Idig Riesling GG (the FASS book pick at $90) is "
            "the standard-bearer: a south-facing limestone parcel on the "
            "Königsbach hill that makes one of Pfalz's most precise GGs."
        ),
    ),
    P(
        slug="okonomeriat_rebholz",
        name="Ökonomierat Rebholz",
        country="Germany", region="Pfalz", sub_region="Siebeldingen",
        appellations=[],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Vom Boden"],
        aliases=["Okonomeriat Rebholz", "Rebholz"],
        tags=["pfalz", "kastanienbusch", "biodynamic", "gg", "icon"],
        summary=(
            "Hansjörg Rebholz — the modern voice of Südpfalz, biodynamic, "
            "no malolactic, long-aging Rieslings and serious Weiss- and "
            "Spätburgunders. Kastanienbusch GG at FASS ($85) is the "
            "headline; same hill as Dr. Wehrheim and Sven Klundt."
        ),
    ),
    P(
        slug="sven_klundt",
        name="Sven Klundt",
        country="Germany", region="Pfalz", sub_region="Birkweiler",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["pfalz", "kastanienbusch", "pinot-noir", "riesling", "gg"],
        summary=(
            "Birkweiler grower neighboring Wehrheim and Rebholz on the "
            "Kastanienbusch — Kastanienbusch Riesling GG ($35) and "
            "Kastanienbusch Pinot Noir at sub-$40 — value entry to one "
            "of Germany's most distinctive porphyry crus."
        ),
    ),
    P(
        slug="kuhling_gillot",
        name="Kühling-Gillot",
        country="Germany", region="Rheinhessen",
        sub_region="Bodenheim / Nierstein",
        appellations=[],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Skurnik"],
        aliases=["Kuhling-Gillot"],
        tags=["rheinhessen", "riesling", "biodynamic", "gg", "icon"],
        summary=(
            "Carolin Spanier-Gillot's biodynamic Rheinhessen estate "
            "(sister estate to Battenfeld-Spanier). Ölberg GG ($50 at "
            "FASS) is the iconic red-slate Nierstein cru — peer to "
            "Pettenthal and Hipping."
        ),
    ),
    P(
        slug="thorle",
        name="Thörle",
        country="Germany", region="Rheinhessen", sub_region="Saulheim",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Wein-Bauer / Vom Boden"],
        aliases=[
            "Thorle", "Thörle", "Thorle Blanc", "Thörle Blanc",
            "Thorle Blanc de Blancs", "Thörle Blanc de Blancs Brut",
            "Thorle Holle", "Thörle Holle", "Thorle Probstey",
            "Thörle Probstey", "Thorle Saulheimer", "Thörle Saulheimer",
            "Thorle Schlossberg",
        ],
        tags=["rheinhessen", "saulheim", "riesling", "spatburgunder", "gg"],
        summary=(
            "Saulheim brothers Christoph and Johannes Thörle — one of "
            "the deeper Rheinhessen books at any retailer, spanning GG "
            "Riesling (Hölle, Schlossberg, Probstey), GG Spätburgunder "
            "(Hölle, Probstey), GG Silvaner (Probstey), Saulheim "
            "Spätburgunder Kalkstein at the entry tier, plus a "
            "traditional-method Blanc de Blancs Brut. Many spelling "
            "variants in the raw data — Holle / Probstey / Saulheimer / "
            "Schlossberg are vineyard names that got parsed as producer."
        ),
    ),
    P(
        slug="juwel",
        name="Juwel Weine",
        country="Germany", region="Rheinhessen", sub_region="Alsheim",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["rheinhessen", "alsheim", "spatburgunder", "riesling"],
        summary=(
            "Small Alsheim estate — Alsheim Spätburgunder and "
            "Frühmesse Riesling Trocken in the sub-$35 tier. Under-radar "
            "Rheinhessen."
        ),
    ),
    P(
        slug="wegeler",
        name="Wegeler",
        country="Germany", region="Mosel",
        sub_region="Bernkastel / Oestrich",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Skurnik"],
        tags=["mosel", "rheingau", "bernkasteler-doctor", "gg"],
        summary=(
            "Historic two-region estate (Mosel + Rheingau) — Bernkasteler "
            "Doctor GG ($85) is the headline parcel, one of the Mosel's "
            "most famous (and traditionally expensive) vineyards. The "
            "Doctor sits directly above the town of Bernkastel-Kues."
        ),
    ),
    P(
        slug="schloss_johannisberg",
        name="Schloss Johannisberg",
        country="Germany", region="Rheingau", sub_region="Johannisberg",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Loosen Bros."],
        tags=["rheingau", "riesling", "icon", "spatlese"],
        summary=(
            "The estate that gave Spätlese to the world (1775 botrytis "
            "discovery). FASS book: Rosalack Auslese ($78), Grünlack "
            "Spätlese. Rheingau's most storied historical address."
        ),
    ),
    P(
        slug="prinz_jungfer",
        name="Prinz — Hallgartener Jungfer GG",
        country="Germany", region="Rheingau", sub_region="Hallgarten",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["rheingau", "hallgarten", "gg"],
        summary=(
            "Weingut Prinz in Hallgarten — VDP organic Rheingau. The "
            "Hallgartener Jungfer GG is the parcel-name cuvée at FASS "
            "($54). Sister cuvée is Schönhell (separate FASS listing)."
        ),
    ),
    P(
        slug="prinz_schonhell",
        name="Prinz — Hallgartener Schönhell GG",
        country="Germany", region="Rheingau", sub_region="Hallgarten",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["rheingau", "hallgarten", "gg"],
        summary=(
            "Same Prinz family estate as Jungfer (separate FASS listing). "
            "Hallgartener Schönhell GG ($48) is the second of the two "
            "Hallgarten 1er-cru-equivalent parcels."
        ),
    ),
    P(
        slug="andreas_laible",
        name="Andreas Laible",
        country="Germany", region="Baden", sub_region="Durbach",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Laible", "Laible Am"],
        tags=["baden", "durbach", "riesling", "gg"],
        summary=(
            "Durbach grower — Baden Riesling specialist on the granite "
            "Plauerlein and Stollenberg hillsides. Stollenberg Riesling "
            "GG, Buhl Riesling GG (the 'Am Buhl' cuvée), Durbacher "
            "Plauerlein Klingelberger (the local Riesling name) Spätlese "
            "Trocken, Muskateller, Scheurebe. Baden Riesling is rare — "
            "this is one of its lead voices."
        ),
    ),
    P(
        slug="ziereisen",
        name="Hanspeter Ziereisen",
        country="Germany", region="Baden", sub_region="Efringen-Kirchen",
        appellations=[],
        farming=["sustainable"],
        importer_us=["Vom Boden"],
        aliases=["Hanspeter Ziereisen"],
        tags=["baden", "markgraflerland", "spatburgunder", "gutedel", "icon"],
        summary=(
            "Markgräflerland's reference estate — Hanspeter Ziereisen "
            "farms on the south-facing slopes facing Switzerland, in the "
            "shadow of the Black Forest. The Jaspis line is the top tier: "
            "Spätburgunder Alte Reben 10-4 ($182), Spätburgunder Zipsin, "
            "Gutedel Alte Reben 10-4, Chardonnay Nägelin, Grauburgunder "
            "Würmlin, Syrah Daublin. Below that, Talrain / Rhini / Schulen "
            "Spätburgunder + Gestad Syrah at $30–$45. One of the most "
            "ambitious German Pinot Noir estates."
        ),
    ),
    P(
        slug="richard_ostreicher",
        name="Richard Östreicher",
        country="Germany", region="Franken", sub_region="Sommerach",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Richard Ostreicher", "Richard Oestreicher"],
        tags=["franken", "spatburgunder", "silvaner", "cabernet-sauvignon"],
        summary=(
            "Franken (Sommerach) grower — unusually broad varietal mix "
            "for the region: Spätburgunder Katzenkopf + Scheiter + "
            "Hallburg + Rosen, Silvaner Maria im Wein / Augustbaum / "
            "Sur Lie, Cabernet Sauvignon R, Merlot, and a Bordeaux blend "
            "R (Cab S / Cab F / Merlot). One of the anchors for the "
            "newly-opened Franken region in the curation filters."
        ),
    ),
    P(
        slug="josef_walter",
        name="Josef Walter",
        country="Germany", region="Franken", sub_region="Bürgstadt",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Joseph Walter", "Weingut Josef Walter"],
        tags=["franken", "centgrafenberg", "spatburgunder"],
        summary=(
            "Bürgstadt grower — Centgrafenberg Spätburgunder J (the "
            "Hundsruck parcel, $69) and Pinot 274 ($100–$107). Same "
            "Spätburgunder zone as Rudolf Fürst (neighbor on the "
            "Centgrafenberg hill)."
        ),
    ),
    P(
        slug="paul_weltner",
        name="Paul Weltner / Weingut Weltner",
        country="Germany", region="Franken", sub_region="Rödelsee",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Weingut Weltner"],
        tags=["franken", "rodelsee", "silvaner", "riesling", "gg"],
        summary=(
            "Rödelsee grower — Küchenmeister Hoheleite GG Silvaner and "
            "Riesling, plus Schwanleite Silvaner Alte Reben and a Virgo "
            "Gaia Scheurebe at the natural end. Silvaner is the Franken "
            "calling card; Weltner is one of its serious modern voices."
        ),
    ),
]


# ============================================================================
# Piedmont / Lombardy / Italian North
# ============================================================================

ITALY_NORTH = [
    P(
        slug="cesare_bussolo",
        name="Cesare Bussolo",
        country="Italy", region="Piedmont", sub_region="La Morra",
        appellations=["Barolo DOCG", "Barbera d'Alba DOC", "Dolcetto d'Alba DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["barolo", "la-morra", "nebbiolo"],
        summary=(
            "La Morra grower — Barolo La Serra and Barolo Fossati ($155–"
            "$200), a Comune di La Morra base ($106), plus Barbera "
            "d'Alba Roscaleto, Vigna Santa Lucia, and Dolcetto. "
            "Traditional Barolo style; comparatively young estate with "
            "ambitious pricing."
        ),
    ),
    P(
        slug="vietti",
        name="Vietti",
        country="Italy", region="Piedmont", sub_region="Castiglione Falletto",
        appellations=["Barolo DOCG", "Barbaresco DOCG", "Barbera d'Alba DOC"],
        farming=["sustainable"],
        importer_us=["Dalla Terra"],
        tags=["barolo", "icon", "single-vineyard", "nebbiolo"],
        summary=(
            "One of Piedmont's reference estates — Vietti's single-"
            "vineyard Barolo program (Rocche di Castiglione, Brunate, "
            "Lazzarito, Ravera, Cerequio, Villero) helped establish the "
            "modern cru framework. Cerequio 2019 at $297 is the FASS book "
            "entry — La Morra cru, classical Vietti style. Owned by "
            "Krause family since 2016 but maintains the Currado / Vaira "
            "winemaking continuity."
        ),
    ),
    P(
        slug="arpepe",
        name="AR.PE.PE.",
        country="Italy", region="Lombardy", sub_region="Valtellina",
        appellations=["Valtellina Superiore DOCG"],
        farming=["sustainable"],
        importer_us=["Selection Massale / Polaner"],
        aliases=["Ar.Pe.Pe", "Arpepe", "ArPePe Stella"],
        tags=["valtellina", "nebbiolo", "icon", "terroir"],
        summary=(
            "Arturo Pelizzatti Perego's family domaine — the reference "
            "estate of Valtellina, the steep terraced Alpine slopes "
            "where Nebbiolo (locally called Chiavennasca) grows on "
            "granitic gneiss. FASS carries the Sassella Rocce Rosse "
            "Riserva (the flagship single-vineyard, often released 10+ "
            "years post-vintage), Sassella Nuova Regina Riserva, "
            "Sassella Stella Retica, Grumello Rocca de Piro, Valtellina "
            "Superiore Inferno Fiamme Antiche. Stylistically high-toned, "
            "perfumed, mineral — closer to grand cru Burgundy than to "
            "Barolo. Already in the cellar (per `gap_csw_buy_candidates`)."
        ),
    ),
    P(
        slug="motalli_renato",
        name="Motalli Renato",
        country="Italy", region="Lombardy", sub_region="Valtellina",
        appellations=["Valtellina Superiore DOCG", "Valgella DOCG",
                      "Sassella DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["valtellina", "nebbiolo", "chiavennasca"],
        summary=(
            "Smaller Valtellina grower — Le Urscele (Superiore Riserva), "
            "Valgella Superiore, Sassella, Chiavennasca Rosato. Sub-$50 "
            "Valtellina, useful entry to the appellation alongside AR.PE.PE."
        ),
    ),
    P(
        slug="cantina_menegola",
        name="Cantina Menegola",
        country="Italy", region="Lombardy", sub_region="Valtellina",
        appellations=["Valtellina Superiore DOCG", "Sassella DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["valtellina", "sassella", "nebbiolo"],
        summary=(
            "Valtellina grower — Sassella Riserva Speciale ($63) is the "
            "single bottling in the FASS book."
        ),
    ),
    P(
        slug="pier_paolo_grasso",
        name="Pier Paolo Grasso",
        country="Italy", region="Piedmont", sub_region="Barbaresco",
        appellations=["Barbaresco DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["barbaresco", "nebbiolo", "aged-nebbiolo"],
        summary=(
            "Barbaresco grower — Piccola Emma 1998 (multiple lots, "
            "$83–$85) is an aged-stock Barbaresco release, the kind of "
            "back-vintage opportunism the FASS book makes a habit of."
        ),
    ),
    P(
        slug="rocche_dei_barbari",
        name="Rocche dei Barbari",
        country="Italy", region="Piedmont", sub_region="Langhe",
        appellations=["Barbaresco DOCG", "Langhe DOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Rocche Di Barbari", "Rochhe de Barbari"],
        tags=["barbaresco", "nebbiolo"],
        summary=(
            "Langhe grower — Alivio Barbaresco Riserva 2016 ($67–$90) "
            "and Primanebbia Langhe Nebbiolo ($40–$50)."
        ),
    ),
    P(
        slug="quazzolo",
        name="Quazzolo",
        country="Italy", region="Piedmont", sub_region="Barbaresco",
        appellations=["Barbaresco DOCG", "Barbaresco Ovello"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["barbaresco", "ovello", "nebbiolo"],
        summary=(
            "Barbaresco grower with an Ovello (one of the appellation's "
            "best-regarded crus) cuvée at $46. Sub-$50 Barbaresco from a "
            "named cru is unusual."
        ),
    ),
    P(
        slug="vini_chiussima",
        name="Vini Chiussima",
        country="Italy", region="Piedmont", sub_region="Canavese / Carema",
        appellations=["Carema DOC", "Erbaluce di Caluso DOCG"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["carema", "nebbiolo", "erbaluce"],
        summary=(
            "Carema grower — the alpine Nebbiolo appellation directly "
            "south of Valle d'Aosta, terraced pergola vineyards on "
            "granite. Carema 2022 ($57–$60) is the headline, plus "
            "Erbaluce Pajarin (the local white grape). Under-radar Alto "
            "Piemonte."
        ),
    ),
    P(
        slug="tenuta_monolo_gilodi",
        name="Tenuta Monolo Gilodi",
        country="Italy", region="Piedmont", sub_region="Alto Piemonte",
        appellations=["Bramaterra DOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["alto-piemonte", "bramaterra", "nebbiolo", "aged-nebbiolo"],
        summary=(
            "Alto Piemonte estate (Bramaterra) — aged-stock Bramaterra "
            "Riserva 1989 / 1990 / 2003, all at $25. Bramaterra is the "
            "Spanna-driven DOC south of Gattinara; this is a hard-to-"
            "find historic cellar release."
        ),
    ),
    P(
        slug="podere_ai_valloni",
        name="Podere ai Valloni",
        country="Italy", region="Piedmont", sub_region="Alto Piemonte",
        appellations=["Boca DOC", "Colline Novaresi DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Podere Ai"],
        tags=["alto-piemonte", "boca", "nebbiolo"],
        summary=(
            "Boca grower (Alto Piemonte) — Boca Vigna Cristiana ($50–$62) "
            "and Colline Novaresi Sass Russ ($32). Boca is Spanna + "
            "Vespolina + Uva Rara on volcanic porphyry; same family of "
            "appellations as Vallana's Boca and the surrounding northern "
            "Piedmont Nebbiolos."
        ),
    ),
    P(
        slug="sergio_barbaglia",
        name="Sergio Barbaglia",
        country="Italy", region="Piedmont", sub_region="Alto Piemonte",
        appellations=["Boca DOC", "Colline Novaresi DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["alto-piemonte", "boca", "nebbiolo", "croatina"],
        summary=(
            "Alto Piemonte grower — Boca DOC ($42), Colline Novaresi "
            "Croatina ($23), and traditional-method Curticella Brut Rosé "
            "/ Dosaggio Zero (96-month / 48-month aging). Wide range "
            "for a small estate."
        ),
    ),
    P(
        slug="vigneti_valle_roncati",
        name="Vigneti Valle Roncati",
        country="Italy", region="Piedmont", sub_region="Alto Piemonte",
        appellations=["Ghemme DOCG", "Sizzano DOC", "Fara DOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Vigneti Valle"],
        tags=["alto-piemonte", "ghemme", "sizzano", "fara", "nebbiolo"],
        summary=(
            "Alto Piemonte grower with the unusual completeness of "
            "covering three DOC/Gs side-by-side: Ghemme Leblanque ($46), "
            "Sizzano Riserva Roano ($32), Fara Riserva Ciada ($30), plus "
            "Spanna Runca. Useful cross-section of the Alto Piemonte "
            "appellations."
        ),
    ),
    P(
        slug="cascina_quarino",
        name="Cascina Quarino",
        country="Italy", region="Piedmont", sub_region="Albugnano",
        appellations=["Albugnano DOC", "Albugnano Superiore DOC"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["albugnano", "asti", "nebbiolo"],
        summary=(
            "Albugnano grower (north of Asti) — Eclissi Albugnano "
            "Superiore ($50), basic Albugnano ($34). Albugnano is the "
            "small Nebbiolo-based DOC at the northern end of the "
            "Monferrato hills."
        ),
    ),
    P(
        slug="palazzo_schiavino",
        name="Palazzo Schiavino",
        country="Italy", region="Piedmont", sub_region="Verduno",
        appellations=["Barolo DOCG"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["barolo", "verduno", "monvigliero", "nebbiolo"],
        summary=(
            "Barolo Monvigliero ($50) at FASS — Verduno's most-pedigreed "
            "cru, neighbor to Burlotto's parcels. Sub-$60 Monvigliero is "
            "rare."
        ),
    ),
]


# ============================================================================
# Jura / Savoie / Provence / Bordeaux / Southwest / Switzerland / USA
# ============================================================================

OTHER = [
    P(
        slug="caves_jean_bourdy",
        name="Caves Jean Bourdy",
        country="France", region="Jura", sub_region="Arlay",
        appellations=["Château-Chalon AOC", "L'Étoile AOC", "Côtes du Jura AOC"],
        farming=["organic"],
        importer_us=["Polaner"],
        aliases=["Caves Bourdy", "Caves Jean"],
        tags=["jura", "chateau-chalon", "vin-jaune", "savagnin", "icon"],
        summary=(
            "Twelfth-generation Jura house in Arlay — the historic cellar "
            "of Château-Chalon and Vin Jaune. FASS book: Château-Chalon "
            "2017/2018 ($90–$92), Vin Jaune 2018 ($80–$87). The Bourdy "
            "name is one of the Jura's oldest continuously operating "
            "domaines and the standard for traditional, oxidative-aged "
            "Savagnin."
        ),
    ),
    P(
        slug="frederic_lambert",
        name="Frédéric Lambert",
        country="France", region="Jura",
        appellations=["Château-Chalon AOC", "Côtes du Jura AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Frederic Lambert"],
        tags=["jura", "chateau-chalon", "vin-jaune", "savagnin"],
        summary=(
            "Jura grower — Château-Chalon 2018 ($92), Vin Jaune 2018 "
            "($87). Smaller-production Jura traditional house."
        ),
    ),
    P(
        slug="gilles_berlioz",
        name="Gilles Berlioz",
        country="France", region="Savoie", sub_region="Chignin",
        appellations=["Chignin AOC", "Chignin-Bergeron AOC"],
        farming=["biodynamic"],
        certifications=["Demeter"],
        importer_us=["Camille Rivière / Selection Massale"],
        tags=["savoie", "chignin-bergeron", "roussanne", "biodynamic", "icon"],
        summary=(
            "Savoie's most influential biodynamic vigneron — Berlioz's "
            "Chignin-Bergeron (Roussanne) bottlings, Les Christines ($97) "
            "and Résilience ($63), are the appellation's reference. "
            "Mineral, age-worthy, totally hand-farmed. Adjacent stylistically "
            "to Dard & Ribo and the Northern Rhône naturals."
        ),
    ),
    P(
        slug="domaine_des_rutissons",
        name="Domaine des Rutissons",
        country="France", region="Savoie",
        appellations=["IGP Isère / Vins des Allobroges"],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["savoie", "isere", "verdesse", "etraire-de-la-huy"],
        summary=(
            "Savoie / Isère grower — Etraire de la Huy (a near-extinct "
            "Isère red variety), Verdesse IGP, M. Leblanc. Hyper-local "
            "ampelography, sub-$30 across the board."
        ),
    ),
    P(
        slug="chateau_simone",
        name="Château Simone",
        country="France", region="Provence", sub_region="Palette",
        appellations=["Palette AOC"],
        farming=["sustainable"],
        importer_us=["Kermit Lynch"],
        tags=["provence", "palette", "icon", "old-vines"],
        summary=(
            "The reference (and effectively only) estate of Palette — "
            "Crozet family, vineyards on north-facing limestone above "
            "Aix-en-Provence, vines averaging 60+ years old, three-color "
            "production from a complex Mediterranean field blend (Grenache, "
            "Mourvèdre, Cinsault, Syrah on the red side; Clairette, "
            "Grenache Blanc, Ugni Blanc, etc. on the white). Rouge and "
            "Blanc both at $82 in the FASS book. One of France's oddest "
            "monopole-grade appellations."
        ),
    ),
    P(
        slug="bel_air_marquis_daligre",
        name="Château Bel Air-Marquis d'Aligre",
        country="France", region="Bordeaux", sub_region="Margaux",
        appellations=["Margaux AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Bel Air", "Bel Air Marquis dAligre"],
        tags=["bordeaux", "margaux", "cru-bourgeois", "long-elevage",
              "aged-classic"],
        summary=(
            "Margaux Cru Bourgeois Supérieur (Boissard family) famous "
            "for its eccentric release policy — wines are held in cellar "
            "for 10–15 years before release. FASS list spans 1996 / 1998 / "
            "2005 / 2009 / 2010 / 2011 / 2013 / 2015, all at $70–$88. "
            "Old-school Margaux: predominantly Cabernet Sauvignon, long "
            "barrel élevage, no new oak. Accepted as the aged-classic "
            "Bordeaux exception in the curation filters (2026-05-26)."
        ),
    ),
    P(
        slug="famille_jouffreau",
        name="Famille Jouffreau / Clos de Gamot",
        country="France", region="South West", sub_region="Cahors",
        appellations=["Cahors AOC"],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        aliases=["Famille Jouffreau", "Famlie Jouffreau", "Familie Jouffreau",
                 "Familie Jouffreau Clos de Gamot"],
        tags=["southwest", "cahors", "malbec", "aged-cahors",
              "old-vines"],
        summary=(
            "The historic anchor of Cahors — Clos de Gamot is among the "
            "oldest continuously farmed estates in the appellation, with "
            "Vignes Centenaires (100+ year-old Malbec / Côt) parcels. "
            "FASS carries a 1986 ($160), a 2015 Vignes Centenaires "
            "($58), a 2022 Vignes Centenaires ($46), and the entry-level "
            "Clos Gamotine. Same aged-grower lens as the rest of the "
            "Tier 1 picks — anchor for opening Southwest France in the "
            "curation filters (2026-05-26)."
        ),
    ),
    P(
        slug="weingut_hansruedi_adank",
        name="Weingut Familie Hansruedi Adank",
        country="Switzerland", region="Graubünden", sub_region="Fläsch",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Adank"],
        tags=["switzerland", "graubunden", "pinot-noir", "chardonnay"],
        summary=(
            "Fläsch (Bündner Herrschaft) estate — Spondis Pinot Noir "
            "($88–$110) is the flagship, with Pinot Noir Flascher Alte "
            "Reben, Pinot Noir Graubünden, Pinot Blanc, Riesling-Sylvaner, "
            "Chardonnay (Graubünden + Am Berg), Extra Brut Blanc de Noir. "
            "Among the deepest Bündner Herrschaft books in the U.S."
        ),
    ),
    P(
        slug="mohr_niggli",
        name="Mohr-Niggli",
        country="Switzerland", region="Graubünden", sub_region="Maienfeld",
        appellations=[],
        farming=["sustainable"],
        importer_us=["FASS Selections"],
        tags=["switzerland", "graubunden", "pinot-noir"],
        summary=(
            "Maienfeld (Bündner Herrschaft) grower — Pinot Noir Graf, "
            "Pilgrim, Maienfeld, plus a Pinot Noir Graf Baselland-Schaft "
            "($74). One of the Graubünden growers with consistent FASS "
            "presence."
        ),
    ),
    P(
        slug="patrick_adank",
        name="Patrick Adank",
        country="Switzerland", region="Graubünden", sub_region="Fläsch",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        tags=["switzerland", "graubunden", "pinot-noir", "chardonnay"],
        summary=(
            "Patrick Adank's solo project — Chardonnay Am Berg ($192) and "
            "Pinot Noir Herrenacker ($192) at the top, Pinot Blanc "
            "Graubünden at the entry. Distinct from the larger Hansruedi "
            "Adank family domaine."
        ),
    ),
    P(
        slug="sprecher_von_bernegg",
        name="Sprecher von Bernegg",
        country="Switzerland", region="Graubünden", sub_region="Jenins",
        appellations=[],
        farming=["organic"],
        importer_us=["FASS Selections"],
        aliases=["Spreccher Von Bernegg", "Sprecher von"],
        tags=["switzerland", "graubunden", "pinot-noir", "completer"],
        summary=(
            "Jenins (Bündner Herrschaft) grower — Pinot Noir Lindenwingert, "
            "Pinot Noir von Pfaffen / Calander, plus Completer (a "
            "near-extinct white Graubünden grape, $58). Small production."
        ),
    ),
    P(
        slug="martin_woods",
        name="Martin Woods",
        country="United States", region="Oregon", sub_region="Willamette Valley",
        appellations=[],
        farming=["sustainable"],
        importer_us=["self-distributed"],
        tags=["willamette", "pinot-noir", "chardonnay", "us-boutique"],
        summary=(
            "Willamette Valley Pinot Noir producer — Hyland Vineyard and "
            "Jessie James single-vineyard Pinots, plus Koosah Vineyard "
            "Chardonnay. Restrained, Burgundian-aspirational style — fits "
            "the US-boutique slot in the curation filters."
        ),
    ),
]


ALL = RHONE + BURGUNDY + LOIRE + BEAUJOLAIS + CHAMPAGNE + MOSEL_NAHE \
    + GERMANY_OTHER + ITALY_NORTH + OTHER


# ============================================================================
# Page rendering
# ============================================================================

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
    for p in ALL:
        path = PRODUCERS_DIR / f"{p.slug}.md"
        if path.exists():
            skipped += 1
            continue
        path.write_text(render(p), encoding="utf-8")
        created += 1
    print(f"Seeded {created} new producer pages, skipped {skipped} existing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
