"""
compile_kelley_instagram.py — generate producer pages for wineries William
Kelley follows on Instagram (source view: wiki/_views/kelley_instagram_producers.md).

LLM-judgment pass per CLAUDE.md: the decision table below is curated/researched
(region, sub_region, farming, importer, one-paragraph summary verified via web
search), and Python applies it deterministically. Idempotent: skips any slug
that already has a page. Run with --apply to write; otherwise dry-run.

    python scripts/compile_kelley_instagram.py            # dry run
    python scripts/compile_kelley_instagram.py --apply    # write pages
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"

# --- decision table -------------------------------------------------------
# Each entry: slug, name, ig (handle), country, region, sub_region,
# appellations, farming, certifications, importer_us, tags, summary.
# Fields left as [] / "" are honestly unknown (not fabricated).

PRODUCERS_DATA: list[dict] = [
    # ---- Burgundy ----
    dict(slug="domaine_georges_roumier", name="Domaine Georges Roumier",
         ig="domainegeorgesroumier", country="France", region="Burgundy",
         sub_region="Chambolle-Musigny", appellations=["Chambolle-Musigny", "Bonnes-Mares", "Musigny", "Ruchottes-Chambertin", "Corton-Charlemagne"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits", "allocation-only"],
         summary="Benchmark Chambolle-Musigny domaine run by Christophe Roumier, among the most sought-after addresses in the Côte de Nuits. Holdings span village Chambolle through grands crus Bonnes-Mares and Musigny plus the monopole Clos de la Bussière in Morey-Saint-Denis; the wines are a reference for transparent, age-worthy red Burgundy."),
    dict(slug="domaine_robert_groffier", name="Domaine Robert Groffier Père & Fils",
         ig="domaine.robert.groffier", country="France", region="Burgundy",
         sub_region="Chambolle-Musigny", appellations=["Chambolle-Musigny 1er Cru Les Amoureuses", "Bonnes-Mares", "Chambertin-Clos de Bèze"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits", "allocation-only"],
         summary="Cellared in Morey-Saint-Denis but famous for Chambolle, the Groffier family owns one of the largest holdings in the great 1er cru Les Amoureuses, alongside parcels in Bonnes-Mares and Chambertin-Clos de Bèze. Perfumed, silky reds with a devoted following."),
    dict(slug="domaine_tessier", name="Domaine Arnaud Tessier",
         ig="domaine.tessier", country="France", region="Burgundy",
         sub_region="Meursault", appellations=["Meursault", "Meursault 1er Cru Les Charmes", "Bourgogne Chardonnay"],
         farming=["organic"], certifications=[], importer_us=["Skurnik"],
         tags=["burgundy", "cote-de-beaune", "white-wine-focused"],
         summary="Meursault domaine that Arnaud Tessier built after his family stopped selling grapes to the négoce, bottling its own wines from 2007 and taking the reins at 21 when his father died in 2009. Roughly 7.5 ha across some of Meursault's best lieux-dits, farmed organically though uncertified."),
    dict(slug="domaine_jean_baptiste_boudier", name="Domaine Jean-Baptiste Boudier",
         ig="domaine_jean.baptiste_boudier", country="France", region="Burgundy",
         sub_region="Pernand-Vergelesses", appellations=["Pernand-Vergelesses", "Aloxe-Corton", "Savigny-lès-Beaune"],
         farming=["sustainable"], certifications=[], importer_us=["Skurnik"],
         tags=["burgundy", "cote-de-beaune"],
         summary="Fifth-generation Pernand-Vergelesses grower who launched his own ~6 ha estate in 2015 after apprenticeships with Nicolas Rossignol, Vieux Télégraphe, Gauby and Haut-Brion. Responsible farming and a light hand in the cellar, favouring infusion over extraction across Pernand, Aloxe-Corton and Savigny."),
    dict(slug="domaine_chopin", name="Domaine Arnaud Chopin & Fils",
         ig="domaine_chopin_arnaud", country="France", region="Burgundy",
         sub_region="Côte de Nuits-Villages (Comblanchien)", appellations=["Côte de Nuits-Villages", "Nuits-Saint-Georges 1er Cru", "Chambolle-Musigny"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits"],
         summary="Six-generation family domaine in Comblanchien at the southern edge of the Côte de Nuits, between Beaune and Nuits-Saint-Georges, now run by Arnaud Chopin with his brother Alban. ~14 ha of old-vine Pinot Noir; fresh, fine-boned reds topped by Nuits-Saint-Georges 1er Cru Aux Murgers."),
    dict(slug="maison_fatien", name="Maison Fatien Père & Fils",
         ig="maisonfatien", country="France", region="Burgundy",
         sub_region="Beaune", appellations=["Beaune", "Pommard", "Gevrey-Chambertin"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "négociant"],
         summary="Family domaine-plus-négociant created in 2000 in old-town Beaune, with ~5 ha of vines across the Côte de Beaune and Côte de Nuits supplemented by purchases of must. Charles Fatien works micro-vinifications in Cistercian-pillared cellars, labelling each cuvée with its bottle count."),
    dict(slug="domaine_fourrier", name="Domaine Fourrier",
         ig="mrfourrier", country="France", region="Burgundy",
         sub_region="Gevrey-Chambertin", appellations=["Gevrey-Chambertin", "Gevrey-Chambertin 1er Cru Clos St-Jacques", "Griotte-Chambertin"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits", "old-vines", "allocation-only"],
         summary="Cult Gevrey-Chambertin domaine led by Jean-Marie Fourrier, prized for old-vine parcels (Clos St-Jacques, Combe aux Moines) farmed with minimal intervention and a signature reductive, low-sulphur élevage. Now also a small négociant arm; the IG account is run by Louis Fourrier."),
    dict(slug="domaine_darviot_perrin", name="Domaine Darviot-Perrin",
         ig="domainedarviotperrin", country="France", region="Burgundy",
         sub_region="Meursault / Monthélie", appellations=["Meursault", "Chassagne-Montrachet", "Volnay"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune"],
         summary="Monthélie-based domaine of Didier Darviot, drawing on prime Meursault and Chassagne-Montrachet white parcels (via the Perrin side) plus Volnay and Monthélie reds. Quietly excellent, classically styled Côte de Beaune."),
    dict(slug="domaine_marshall", name="Domaine Marshall",
         ig="domaine_marshall", country="France", region="Burgundy",
         sub_region="Nuits-Saint-Georges", appellations=["Nuits-Saint-Georges", "Bourgogne"],
         farming=["organic"], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits", "micro-production"],
         summary="Nuits-Saint-Georges estate with roots in the 1960s English négociant Tim Marshall, returned to family hands in 2022 under Jean Marshall after two decades leased to Méo-Camuzet. Organic farming and a distinctive oak-free élevage in low-permeability ceramic vessels; one of the most talked-about Burgundy newcomers."),
    dict(slug="domaine_baptiste_guyot", name="Domaine Baptiste Guyot",
         ig="domainebaptisteguyot", country="France", region="Burgundy",
         sub_region="Beaune", appellations=["Beaune", "Pommard", "Volnay", "Pernand-Vergelesses"],
         farming=["sustainable"], certifications=["HVE"], importer_us=[],
         tags=["burgundy", "cote-de-beaune"],
         summary="Beaune domaine on the former Abbaye Saint-Martin farm; Baptiste Guyot took over in 2010 and works ~9 ha of Pinot Noir, Chardonnay and Aligoté across Beaune, Pernand-Vergelesses, Volnay, Pommard and Monthélie. Ploughing and organic treatments, HVE-certified since 2020."),
    dict(slug="domaine_naddef", name="Domaine Philippe Naddef",
         ig="michel_naddef", country="France", region="Burgundy",
         sub_region="Gevrey-Chambertin (Couchey)", appellations=["Gevrey-Chambertin", "Mazis-Chambertin", "Marsannay"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits"],
         summary="Couchey-based domaine known for dense, structured Gevrey-Chambertin including a parcel of grand cru Mazis-Chambertin, plus Marsannay. A traditional Côte de Nuits address with a long track record of vins de garde."),
    dict(slug="domaine_georges_joillot", name="Domaine Georges Joillot",
         ig="domaine_georges_joillot", country="France", region="Burgundy",
         sub_region="Pommard", appellations=["Pommard", "Pommard 1er Cru", "Beaune"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune"],
         summary="Family domaine in Pommard producing classic, firmly structured reds from village and 1er cru parcels, alongside neighbouring Beaune and Côte de Beaune appellations."),
    dict(slug="domaine_boyer_martenot", name="Domaine Boyer-Martenot",
         ig="boyer_martenot", country="France", region="Burgundy",
         sub_region="Meursault", appellations=["Meursault", "Meursault 1er Cru Les Charmes", "Meursault 1er Cru Les Perrières"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "white-wine-focused"],
         summary="Meursault domaine run by Vincent Boyer, with holdings in the top 1er crus Charmes, Perrières and Genevrières. Precise, mineral whites that are a reliable Meursault reference."),
    dict(slug="domaine_camille_thiriet", name="Domaine Camille Thiriet",
         ig="domainecamillethiriet", country="France", region="Burgundy",
         sub_region="Côte de Nuits (Comblanchien / Corgoloin)", appellations=["Bourgogne", "Côte de Nuits-Villages", "Nuits-Saint-Georges"],
         farming=["organic"], certifications=[], importer_us=["Grand Cru Selections"],
         tags=["burgundy", "cote-de-nuits", "micro-production"],
         summary="Started by Camille Thiriet and partner Matt Chittick as garagistes in Comblanchien (first vintage 2016), turned full domaine in 2022 with a 4.5 ha purchase in Corgoloin. Now ~6 ha farmed organically, worked by hand and by horse, with whole-bunch, native-yeast, low-input winemaking — a leading new-wave Côte de Nuits name."),
    dict(slug="domaine_briotet_d_aprigny", name="Domaine Briotet-d'Aprigny",
         ig="vins.briotet_daprigny", country="France", region="Burgundy",
         sub_region="Côte de Beaune (Beaune / Volnay)", appellations=["Beaune 1er Cru Les Theurons", "Volnay", "Côte de Beaune"],
         farming=["organic"], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "micro-production"],
         summary="Micro family domaine founded in 2022 by Christophe and Marie Briotet on inherited Côte de Beaune vines (Volnay, Beaune 1er Cru Les Theurons, the flagship Les Monsnières on the Montagne de Beaune). Organic, building a polyculture ecosystem of vines, fruit and truffle trees."),
    dict(slug="domaine_bruno_clair", name="Domaine Bruno Clair",
         ig="domaine_brunoclair", country="France", region="Burgundy",
         sub_region="Marsannay", appellations=["Marsannay", "Gevrey-Chambertin 1er Cru Clos St-Jacques", "Chambertin-Clos de Bèze", "Corton-Charlemagne"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits"],
         summary="Marsannay's leading domaine, with an unusually broad spread of holdings from Marsannay village up to grand cru Chambertin-Clos de Bèze and a coveted slice of Gevrey 1er Cru Clos St-Jacques. Classic, long-lived reds and benchmark Marsannay."),
    dict(slug="domaine_arlaud", name="Domaine Arlaud",
         ig="domaine_arlaud", country="France", region="Burgundy",
         sub_region="Morey-Saint-Denis", appellations=["Morey-Saint-Denis", "Clos de la Roche", "Bonnes-Mares", "Charmes-Chambertin"],
         farming=["biodynamic"], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits", "biodynamic"],
         summary="Morey-Saint-Denis domaine led by Cyprien Arlaud, biodynamically farmed (with horse ploughing), spanning village Morey through grands crus Clos de la Roche, Bonnes-Mares and Charmes-Chambertin. Fragrant, energetic, whole-cluster-inflected reds."),
    dict(slug="domaine_fabien_coche", name="Domaine Fabien Coche",
         ig="domainefabiencoche", country="France", region="Burgundy",
         sub_region="Meursault", appellations=["Meursault", "Meursault 1er Cru", "Auxey-Duresses"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "white-wine-focused"],
         summary="Meursault domaine of Fabien Coche (of the extended Coche family), producing dependable, well-priced Meursault and Côte de Beaune whites and reds from village and 1er cru parcels."),
    dict(slug="domaine_feuillat_juillot", name="Domaine Feuillat-Juillot",
         ig="domainefeuillatjuillot", country="France", region="Burgundy",
         sub_region="Montagny (Côte Chalonnaise)", appellations=["Montagny 1er Cru"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-chalonnaise", "white-wine-focused", "value"],
         summary="Montagny specialist in the Côte Chalonnaise run by Françoise Feuillat-Juillot, focused on a range of single-climat Montagny 1er crus — high-quality, well-priced white Burgundy."),
    dict(slug="domaine_robert_denogent", name="Domaine Robert-Denogent",
         ig="domainerobertdenogent", country="France", region="Burgundy",
         sub_region="Pouilly-Fuissé (Mâconnais)", appellations=["Pouilly-Fuissé", "Mâcon-Villages", "Saint-Véran"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "maconnais", "white-wine-focused", "old-vines"],
         summary="Fuissé-based Mâconnais domaine known for old-vine, low-yield, long-élevage Pouilly-Fuissé made in a rich, ageworthy, terroir-driven style that helped redefine expectations for the appellation."),
    dict(slug="domaine_brunet_randon", name="Domaine Brunet-Randon",
         ig="", country="France", region="Burgundy",
         sub_region="Meursault", appellations=["Meursault", "Meursault 1er Cru Les Charmes"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "white-wine-focused", "micro-production"],
         summary="Tiny ~3 ha Meursault domaine revived by Cécile Brunet Randon and her mother on plots from her grandfather's Domaine André Brunet (last bottled 1999); first vintage under the new name was 2022. Classic, barrel-aged Meursault aiming for elegance without heaviness."),
    dict(slug="domaine_bessin_tremblay", name="Domaine Bessin-Tremblay",
         ig="domainebessintremblay", country="France", region="Burgundy",
         sub_region="Chablis", appellations=["Chablis", "Chablis 1er Cru Fourchaume", "Chablis 1er Cru Montmains", "Chablis Grand Cru Valmur"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "chablis", "white-wine-focused"],
         summary="Top-tier Chablis domaine founded 1992 by architect-turned-vigneron Jean-Claude Bessin, now run by sons Romain and Antoine. ~12 ha on the best slopes (Valmur, Fourchaume, Montmains, La Forêt); precise, low-intervention, native-yeast wines. William Kelley rates it among the top six Chablis producers."),
    dict(slug="domaine_des_senons", name="Domaine des Sénons",
         ig="domainedessenons", country="France", region="Burgundy",
         sub_region="Yonne (Sens)", appellations=["IGP Yonne", "Vin de France"],
         farming=["organic"], certifications=["Ecocert"], importer_us=[],
         tags=["burgundy", "yonne", "micro-production"],
         summary="Revival of an ancient vineyard around Sens on the Yonne, founded 2017 by Frédéric Duponchel with daughter Marie and son-in-law Florian Ruscon; first commercial vintage 2022. Organically farmed Chardonnay, Pinot Noir and Pinot Gris on chalk-marl-flint soils, made with input from Bernard Raveneau and Thomas Duclos."),
    dict(slug="domaine_lefort", name="Domaine Lefort",
         ig="domaine_lefort", country="France", region="Burgundy",
         sub_region="Rully / Mercurey (Côte Chalonnaise)", appellations=["Rully", "Mercurey 1er Cru", "Bourgogne"],
         farming=["organic", "biodynamic"], certifications=[], importer_us=[],
         tags=["burgundy", "cote-chalonnaise", "biodynamic"],
         summary="Côte Chalonnaise domaine run since 2010 by David Lefort (a former medicine and philosophy student), ~5 ha of Rully and Mercurey 1er Cru. Certified organic and converting to biodynamics, natural-leaning viticulture."),
    dict(slug="ballot_millot", name="Domaine Ballot-Millot",
         ig="ballotmillot", country="France", region="Burgundy",
         sub_region="Meursault", appellations=["Meursault", "Meursault 1er Cru Les Charmes", "Meursault 1er Cru Les Perrières", "Volnay"],
         farming=[], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-beaune", "white-wine-focused"],
         summary="Long-established Meursault family domaine (now led by Charles Ballot) split between fine Meursault 1er crus (Charmes, Perrières, Genevrières) and Côte de Beaune reds from Volnay and Pommard. Polished, dependable white Burgundy."),
    dict(slug="domaine_maume_siblas", name="Domaine Maume-Siblas",
         ig="domaines_siblas_maume", country="France", region="Burgundy",
         sub_region="Gevrey-Chambertin", appellations=["Gevrey-Chambertin", "Gevrey-Chambertin 1er Cru Cherbaudes", "Mazis-Chambertin"],
         farming=["biodynamic"], certifications=[], importer_us=[],
         tags=["burgundy", "cote-de-nuits"],
         summary="Rebirth of the classic Gevrey-Chambertin Domaine Maume: after a decade leased to Tawse/Pascal Marchand (2012–2021), the vines returned to family hands as Maume-Siblas, with Thomas Maume in the cellar alongside mother Patricia Siblas. Biodynamically farmed (a legacy of the Tawse era), aiming to recapture unadorned, structured Gevrey typicity."),
]

# region -> region-index wikilink stem (for Cross-references)
def region_link(region: str) -> str:
    return region.replace(" ", "_") + "_Producers"


def fmt_list(items: list[str]) -> str:
    if not items:
        return "[]"
    inner = ", ".join(f'"{i}"' for i in items)
    return f"[{inner}]"


def render(p: dict) -> str:
    ig = p.get("ig", "")
    fm = [
        "---",
        "type: producer",
        f'name: "{p["name"]}"',
        f'slug: {p["slug"]}',
        f'aliases: {fmt_list(p.get("aliases", []))}',
        "",
        f'country: "{p["country"]}"',
        f'region: "{p["region"]}"',
        f'sub_region: "{p.get("sub_region", "")}"',
        f'appellations: {fmt_list(p.get("appellations", []))}',
        "",
        f'farming: {fmt_list(p.get("farming", []))}',
        f'certifications: {fmt_list(p.get("certifications", []))}',
        "",
        f'importer_us: {fmt_list(p.get("importer_us", []))}',
        "",
        "retailers:",
        "  chambers:",
        "    championed: false",
        "    article_count: 0",
        "    dedicated_count: 0",
        "    first_year: 0",
        "    last_year: 0",
        "  dte:",
        "    in_portfolio: false",
        "    cuvee_count: 0",
        "    price_min: 0",
        "    price_max: 0",
        "  raeders:",
        "    in_portfolio: false",
        "  fass:",
        "    in_portfolio: false",
        "",
        "roscioli:",
        "  in_portfolio: false",
        '  profile_url: ""',
        "  has_video: false",
        '  place: ""',
        '  style_hint: ""',
        '  profile_date: ""',
        "  story_count: 0",
        "",
        "events: []",
        f'tags: {fmt_list(p.get("tags", []))}',
        "",
        "discovery_source: william_kelley_instagram",
        f'instagram: "{ig}"',
        "---",
        "",
        f'# {p["name"]}',
        "",
        p["summary"],
        "",
        "## CSW Write-ups",
        "",
        "_No Chambers Street coverage on file._",
        "",
        "## Down to Earth Wines (Panzer)",
        "",
        "_Not in portfolio on file._",
        "",
        "## Raeder's",
        "",
        "_Not in portfolio on file._",
        "",
        "## FASS",
        "",
        "_Not in portfolio on file._",
        "",
        "## Cross-references",
        "",
        f'- [[{region_link(p["region"])}|{p["region"]}]]',
        "- [[CSW Article Archive]]",
        "",
        "## Notes",
        "",
        f"Added from William Kelley's Instagram following list "
        f"(see [[_views/kelley_instagram_producers|Kelley IG producers]]). "
        + (f"Instagram: @{ig}. " if ig else "")
        + "Frontmatter region/farming/importer researched 2026-06; deeper "
        "critic/retailer coverage not yet ingested.",
        "",
    ]
    return "\n".join(fm)


def main(apply: bool) -> int:
    existing = {p.stem for p in PRODUCERS.glob("*.md")}
    created, skipped = [], []
    for p in PRODUCERS_DATA:
        path = PRODUCERS / f'{p["slug"]}.md'
        if p["slug"] in existing:
            # Only overwrite pages we previously generated; never clobber
            # hand-written or otherwise-sourced producer pages.
            txt = path.read_text(encoding="utf-8", errors="replace")
            if "discovery_source: william_kelley_instagram" not in txt:
                skipped.append(p["slug"])
                continue
        if apply:
            path.write_text(render(p), encoding="utf-8")
        created.append(p["slug"])
    mode = "WROTE" if apply else "DRY-RUN would write"
    print(f"{mode} {len(created)} pages; skipped {len(skipped)} existing.")
    for s in created:
        print(f"  + {s}")
    if skipped:
        print(f"  (skipped: {', '.join(skipped)})")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    sys.exit(main(apply=ap.parse_args().apply))
