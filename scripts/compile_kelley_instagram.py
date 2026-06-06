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

# ---- batch 2+: all remaining regions (researched 2026-06) ----
PRODUCERS_DATA += [
    # ---- Loire ----
    dict(slug="domaine_luneau_papin", name="Domaine Luneau-Papin", ig="domaine_luneau_papin", country="France", region="Loire", sub_region="Muscadet Sèvre-et-Maine", appellations=["Muscadet Sèvre-et-Maine"], farming=["organic", "biodynamic"], certifications=[], importer_us=[], tags=["loire", "muscadet", "white-wine-focused", "old-vines"], summary="Reference Muscadet estate in Le Landreau run by Pierre Luneau-Papin, organic/biodynamic, famous for terroir- and lees-driven, age-worthy Melon de Bourgogne from old vines on varied soils."),
    dict(slug="domaine_philippe_alliet", name="Domaine Philippe Alliet", ig="domainephilippealliet", country="France", region="Loire", sub_region="Chinon", appellations=["Chinon"], farming=[], certifications=[], importer_us=[], tags=["loire", "chinon", "cabernet-franc"], summary="Benchmark Chinon domaine making serious, structured, age-worthy Cabernet Franc from gravel and limestone-clay terroirs, including the top Coteau de Noiré."),
    dict(slug="thibaud_boudignon", name="Thibaud Boudignon", ig="thibaud.boudignon", country="France", region="Loire", sub_region="Anjou / Savennières", appellations=["Savennières", "Anjou"], farming=["organic"], certifications=[], importer_us=[], tags=["loire", "savennieres", "chenin-blanc"], summary="Star Anjou vigneron crafting some of the Loire's most coveted dry Chenin Blanc from organically farmed schist parcels in and around Savennières."),
    dict(slug="domaine_vacheron", name="Domaine Vacheron", ig="jdovacheron", country="France", region="Loire", sub_region="Sancerre", appellations=["Sancerre"], farming=["biodynamic"], certifications=["Demeter"], importer_us=[], tags=["loire", "sancerre", "biodynamic"], summary="Leading biodynamic (Demeter) Sancerre domaine, a reference for both terroir-driven Sauvignon Blanc and serious Pinot Noir reds."),
    dict(slug="domaine_lucas_salmon", name="Domaine Lucas Salmon", ig="mickael_salmon", country="France", region="Loire", sub_region="Muscadet (Château-Thébaud)", appellations=["Muscadet Sèvre-et-Maine"], farming=["organic"], certifications=[], importer_us=[], tags=["loire", "muscadet", "micro-production"], summary="~10 ha Nantais estate founded 2019 by Mickaël Salmon around Château-Thébaud and Vertou, in organic conversion, working Melon, Folle Blanche and reds."),
    dict(slug="domaine_des_quatre_piliers", name="Domaine des Quatre Piliers", ig="domainedesquatrepiliers", country="France", region="Loire", sub_region="Touraine (Noyers-sur-Cher)", appellations=["Touraine"], farming=["organic"], certifications=[], importer_us=[], tags=["loire", "touraine", "micro-production"], summary="Young 10 ha Touraine estate at Noyers-sur-Cher led by Valentin Desloges (trained with Raphaël Coche and Paul Pillot), organic from 2020, working Sauvignon, Chenin, Cabernet Franc, Pinot Noir and Côt."),
    # ---- Burgundy (reclassified during research) ----
    dict(slug="domaine_nathalie_richez", name="Domaine Nathalie Richez", ig="domaine_nathalierichez", country="France", region="Burgundy", sub_region="Côte Chalonnaise / Côte de Beaune (Chagny)", appellations=["Bouzeron", "Santenay", "Maranges", "Auxey-Duresses"], farming=["sustainable"], certifications=[], importer_us=["Neal Rosenthal"], tags=["burgundy", "cote-chalonnaise"], summary="~12 ha domaine at Chagny on the Côte de Beaune/Côte Chalonnaise border, founded 2011 by Nathalie Richez after a career change; sustainable viticulture across Bouzeron, Santenay, Maranges and Auxey-Duresses."),
    dict(slug="domaine_guilbert_gillet", name="Domaine Guilbert-Gillet", ig="domaineguilbertgillet", country="France", region="Burgundy", sub_region="Savigny-lès-Beaune", appellations=["Savigny-lès-Beaune 1er Cru", "Chorey-lès-Beaune", "Bourgogne Aligoté"], farming=["organic"], certifications=[], importer_us=[], tags=["burgundy", "cote-de-beaune", "micro-production"], summary="3.6 ha Savigny-lès-Beaune domaine founded 2020 by Benjamin and Caroline Guilbert, organically farmed, a much-hyped new-generation name across Savigny and Chorey."),
    dict(slug="domaine_du_chancelier", name="Domaine du Chancelier", ig="domaineduchancelier", country="France", region="Burgundy", sub_region="Beaune (Côte de Beaune)", appellations=["Savigny-lès-Beaune 1er Cru", "Ladoix 1er Cru", "Bourgogne Côte d'Or"], farming=["organic"], certifications=["Ecocert"], importer_us=[], tags=["burgundy", "cote-de-beaune", "micro-production"], summary="Young Beaune-based domaine of Elsa and Cédric Ehrhart, first vintage 2016, slowly acquiring parcels across the Côte de Beaune; certified organic (Ecocert)."),
    # ---- Savoie ----
    dict(slug="domaine_les_aricoques", name="Domaine Les Aricoques", ig="", country="France", region="Savoie", sub_region="Frangy", appellations=["Roussette de Savoie", "Vin de Savoie"], farming=["organic"], certifications=[], importer_us=[], tags=["savoie", "alpine", "micro-production"], summary="4.8 ha Savoie estate at Frangy started 2021 by friends Guillaume Bellona and Romain Dupont on glacial-moraine soils; organic (certification pending) and biodynamic-leaning, working Altesse, Jacquère, Mondeuse and Gamay."),
    # ---- Rhône / Provence ----
    dict(slug="domaine_de_la_vieille_julienne", name="Domaine de la Vieille Julienne", ig="vieillejulienne", country="France", region="Rhône", sub_region="Châteauneuf-du-Pape", appellations=["Châteauneuf-du-Pape", "Côtes du Rhône"], farming=["biodynamic"], certifications=[], importer_us=[], tags=["rhone", "chateauneuf-du-pape", "biodynamic"], summary="Biodynamic Châteauneuf-du-Pape estate run by Jean-Paul Daumen on the cooler northern sector and the high lieu-dit Clavin, making structured, terroir-transparent Grenache-based reds."),
    dict(slug="domaine_niero", name="Domaine Niero", ig="domaine_niero", country="France", region="Rhône", sub_region="Condrieu / Côte-Rôtie", appellations=["Condrieu", "Côte-Rôtie"], farming=[], certifications=[], importer_us=[], tags=["rhone", "condrieu", "cote-rotie"], summary="Northern Rhône domaine of Robert Niero specialising in fine Condrieu (Viognier) alongside Côte-Rôtie."),
    dict(slug="domaine_roger_sabon", name="Domaine Roger Sabon", ig="roger.sabon", country="France", region="Rhône", sub_region="Châteauneuf-du-Pape", appellations=["Châteauneuf-du-Pape", "Lirac"], farming=[], certifications=[], importer_us=[], tags=["rhone", "chateauneuf-du-pape"], summary="Long-established Châteauneuf-du-Pape house known for traditional, age-worthy cuvées including Le Secret des Sabon and Prestige."),
    dict(slug="famille_perrin_beaucastel", name="Famille Perrin / Château de Beaucastel", ig="marcperrin10", country="France", region="Rhône", sub_region="Châteauneuf-du-Pape", appellations=["Châteauneuf-du-Pape", "Côtes du Rhône"], farming=["biodynamic"], certifications=["Demeter"], importer_us=[], tags=["rhone", "chateauneuf-du-pape", "biodynamic"], summary="Iconic biodynamic (Demeter) Châteauneuf-du-Pape estate Château de Beaucastel and the broader Famille Perrin range; Marc Perrin represents the current generation."),
    dict(slug="domaine_tempier", name="Domaine Tempier", ig="domaine_tempier", country="France", region="Provence", sub_region="Bandol", appellations=["Bandol"], farming=["organic"], certifications=[], importer_us=["Kermit Lynch"], tags=["provence", "bandol", "mourvedre"], summary="The benchmark Bandol estate, organically farmed, famed for Mourvèdre-based reds (La Tourtine, Cabassaou, La Migoua) and a legendary rosé; long associated with Kermit Lynch and Lulu Peyraud."),
    # ---- Bordeaux ----
    dict(slug="chateau_pontet_canet", name="Château Pontet-Canet", ig="chateau_pontetcanet", country="France", region="Bordeaux", sub_region="Pauillac", appellations=["Pauillac"], farming=["biodynamic"], certifications=["Demeter", "Biodyvin"], importer_us=[], tags=["bordeaux", "pauillac", "biodynamic"], summary="Pioneering biodynamic 5th-growth Pauillac (Demeter/Biodyvin certified), known for using horses in the vineyard and a portion of terracotta-amphora élevage; a Left Bank reference for farming-driven classed growth."),
    dict(slug="chateau_lafleur", name="Château Lafleur", ig="lafleur.societeagricole", country="France", region="Bordeaux", sub_region="Pomerol", appellations=["Pomerol"], farming=[], certifications=[], importer_us=[], tags=["bordeaux", "pomerol", "allocation-only"], summary="Tiny, legendary Pomerol estate run by the Guinaudeau family (Société Agricole de Lafleur), prized for a singular Cabernet Franc-marked, age-worthy style that rivals the first growths."),
    dict(slug="chateau_ausone", name="Château Ausone", ig="lesprit_ausone_famillevauthier", country="France", region="Bordeaux", sub_region="Saint-Émilion", appellations=["Saint-Émilion Grand Cru"], farming=["organic"], certifications=[], importer_us=[], tags=["bordeaux", "saint-emilion", "allocation-only"], summary="Historic Saint-Émilion first growth on the limestone côte, run by the Vauthier family; tiny production of profound, ageless reds from old-vine Cabernet Franc and Merlot."),
    dict(slug="chateau_couvent_des_jacobins", name="Château Couvent des Jacobins", ig="couventdesjacobins", country="France", region="Bordeaux", sub_region="Saint-Émilion", appellations=["Saint-Émilion Grand Cru"], farming=[], certifications=[], importer_us=[], tags=["bordeaux", "saint-emilion"], summary="Saint-Émilion Grand Cru estate at the heart of the medieval town, producing supple, Merlot-led reds."),
    dict(slug="chateau_soutard", name="Château Soutard", ig="chateausoutard", country="France", region="Bordeaux", sub_region="Saint-Émilion", appellations=["Saint-Émilion Grand Cru Classé"], farming=[], certifications=[], importer_us=[], tags=["bordeaux", "saint-emilion"], summary="Historic Saint-Émilion Grand Cru Classé with a large single block of vines around the château, making structured, age-worthy reds."),
    dict(slug="chateau_corbin", name="Château Corbin", ig="chateaucorbin_grandcruclasse", country="France", region="Bordeaux", sub_region="Saint-Émilion", appellations=["Saint-Émilion Grand Cru Classé"], farming=[], certifications=[], importer_us=[], tags=["bordeaux", "saint-emilion"], summary="Saint-Émilion Grand Cru Classé on the sand-clay plateau near Pomerol, family-run, making plush Merlot-dominant wines."),
    dict(slug="chateau_cissac", name="Château Cissac", ig="chateaucissac", country="France", region="Bordeaux", sub_region="Haut-Médoc", appellations=["Haut-Médoc"], farming=[], certifications=[], importer_us=[], tags=["bordeaux", "haut-medoc", "value"], summary="Classic cru bourgeois Haut-Médoc near Pauillac, a long-standing source of traditional, age-worthy, well-priced Left Bank claret."),
    # ---- Beaujolais / Corsica ----
    dict(slug="domaine_saint_cyr", name="Domaine Saint-Cyr", ig="raph_domainestcyr", country="France", region="Beaujolais", sub_region="Anse", appellations=["Beaujolais", "Brouilly"], farming=[], certifications=[], importer_us=[], tags=["beaujolais", "gamay"], summary="Beaujolais domaine led by Raphaël Saint-Cyr near Anse, working Gamay across Beaujolais and the crus in a fresh, terroir-driven style."),
    dict(slug="clos_venturi", name="Clos Venturi", ig="clos.venturi", country="France", region="Corsica", sub_region="Corse (Calenzana)", appellations=["Vin de Corse"], farming=["organic"], certifications=[], importer_us=[], tags=["corsica", "organic"], summary="Corsican estate (part of the Venturi/Domaine Vico family) farming organically in the island's interior, championing native varieties like Sciaccarellu, Niellucciu and Vermentinu."),
    dict(slug="clos_de_mez", name="Clos de Mez", ig="clos_de_mez", country="France", region="Beaujolais", sub_region="Fleurie / Morgon", appellations=["Fleurie", "Morgon"], farming=["organic"], certifications=[], importer_us=[], tags=["beaujolais", "gamay", "organic"], summary="Beaujolais domaine of Marie-Élodie Zighera (the name plays on her initials), certified organic since 2018, making structured, age-worthy Fleurie and Morgon with native yeasts and minimal intervention."),
    dict(slug="hadrien_brissaud", name="Hadrien Brissaud", ig="hbvigneron", country="France", region="Beaujolais", sub_region="Côte de Brouilly", appellations=["Côte de Brouilly", "Brouilly"], farming=[], certifications=[], importer_us=[], tags=["beaujolais", "gamay", "micro-production"], summary="Small vigneron/négoce project launched 2021 by Hadrien Brissaud (also an art-insurance broker), making Gamay from the Beaujolais crus, notably Côte de Brouilly."),
    # ---- Alsace ----
    dict(slug="domaine_weinbach", name="Domaine Weinbach", ig="domaineweinbach", country="France", region="Alsace", sub_region="Kaysersberg", appellations=["Alsace Grand Cru Schlossberg", "Alsace Grand Cru Furstentum"], farming=["biodynamic"], certifications=["Demeter"], importer_us=[], tags=["alsace", "biodynamic", "white-wine-focused"], summary="Iconic biodynamic (Demeter) Alsace domaine at the Clos des Capucins in Kaysersberg, run by the Faller family; a reference for Riesling, Gewurztraminer and Pinot Gris from grands crus Schlossberg and Furstentum."),
    dict(slug="rolly_gassmann", name="Rolly Gassmann", ig="pierregassmann", country="France", region="Alsace", sub_region="Rorschwihr", appellations=["Alsace"], farming=[], certifications=[], importer_us=[], tags=["alsace", "white-wine-focused", "old-vines"], summary="Rorschwihr domaine famous for richly textured, often off-dry, long-aged Alsace whites released with considerable bottle age, from a mosaic of lieux-dits."),
    # ---- Italy ----
    dict(slug="stella_di_campalto", name="Stella di Campalto", ig="stelladicampalto", country="Italy", region="Tuscany", sub_region="Montalcino", appellations=["Brunello di Montalcino", "Rosso di Montalcino"], farming=["biodynamic"], certifications=["Demeter"], importer_us=[], tags=["tuscany", "montalcino", "biodynamic", "sangiovese"], summary="Cult biodynamic (Demeter) Montalcino estate (Podere San Giuseppe) on the cooler southeastern side, where Stella di Campalto makes some of the most sought-after, ethereal Brunello and Rosso."),
    dict(slug="le_ragnaie", name="Le Ragnaie", ig="le_ragnaie", country="Italy", region="Tuscany", sub_region="Montalcino", appellations=["Brunello di Montalcino", "Rosso di Montalcino"], farming=["organic"], certifications=[], importer_us=[], tags=["tuscany", "montalcino", "sangiovese", "organic"], summary="High-altitude Montalcino estate run by Riccardo Campinoti, organically farmed, prized for fresh, elegant, terroir-transparent Brunello including old-vine and single-vineyard bottlings."),
    dict(slug="pierguido_busso", name="Pierguido Busso", ig="pier_busso", country="Italy", region="Piedmont", sub_region="Barbaresco (Neive)", appellations=["Barbaresco", "Langhe Nebbiolo"], farming=[], certifications=[], importer_us=[], tags=["piedmont", "barbaresco", "nebbiolo"], summary="Family Barbaresco grower in Neive making detailed, classically styled Nebbiolo from crus such as Albesani and San Stunet."),
    dict(slug="azienda_agricola_darcy", name="Azienda Agricola D'Arcy", ig="cantina_darcy", country="Italy", region="Piedmont", sub_region="Barolo", appellations=["Barolo", "Langhe Nebbiolo", "Dolcetto d'Alba"], farming=[], certifications=[], importer_us=[], tags=["piedmont", "barolo", "nebbiolo", "micro-production"], summary="Micro Barolo project founded 2020 by New Zealand-born Tom Myers (who trained with Benjamin Leroux, Graillot, d'Angerville, Comte Armand and Rinaldi), farming the Preda cru in a precise, Burgundian-influenced style."),
    dict(slug="il_guercio", name="Il Guercio (Sean O'Callaghan)", ig="seanilguercio", country="Italy", region="Tuscany", sub_region="Chianti Classico (Gaiole)", appellations=["Chianti Classico", "Chianti"], farming=[], certifications=[], importer_us=[], tags=["tuscany", "chianti-classico", "sangiovese"], summary="Personal label of Sean O'Callaghan (Riecine's winemaker for 25 years, now also at Tenuta di Carleone), 100% Sangiovese from the high Mello vineyard in Gaiole, made in an elegant, Burgundian-leaning style."),
    # ---- Germany / Austria ----
    dict(slug="weingut_keller", name="Weingut Keller", ig="kellerdalsheim", country="Germany", region="Rheinhessen", sub_region="Flörsheim-Dalsheim", appellations=["Rheinhessen"], farming=[], certifications=[], importer_us=[], tags=["rheinhessen", "riesling", "allocation-only"], summary="Germany's most sought-after Riesling estate, run by Klaus-Peter Keller in Flörsheim-Dalsheim; legendary dry GGs (Abtserde, Hubacker, Morstein) and the Kirchspiel/G-Max, plus profound sweet wines."),
    dict(slug="weingut_aufricht", name="Weingut Aufricht", ig="johannes_aufricht", country="Germany", region="Baden", sub_region="Bodensee (Meersburg)", appellations=["Baden"], farming=[], certifications=[], importer_us=[], tags=["baden", "bodensee", "spatburgunder"], summary="Top Lake Constance (Bodensee) estate of the Aufricht brothers at Stetten near Meersburg, ~29 ha known for barrique-aged Spätburgunder and a range of Pinot-family whites."),
    dict(slug="peter_veyder_malberg", name="Peter Veyder-Malberg", ig="veydermalberg_wachau", country="Austria", region="Wachau", sub_region="Spitz", appellations=["Wachau"], farming=["organic"], certifications=[], importer_us=[], tags=["wachau", "gruner-veltliner", "riesling"], summary="Cult Wachau grower who revived steep, abandoned terraces around Spitz, farming organically for low-yield, mineral, restrained Grüner Veltliner and Riesling."),
    # ---- Spain / Portugal / Canaries ----
    dict(slug="dominio_del_aguila", name="Dominio del Águila", ig="dominio_delaguila", country="Spain", region="Ribera del Duero", sub_region="La Aguilera", appellations=["Ribera del Duero"], farming=["organic"], certifications=[], importer_us=[], tags=["ribera-del-duero", "tempranillo", "old-vines"], summary="La Aguilera estate of Jorge Monzón and Isabel Rodero reviving ancient field-blend vineyards in Ribera del Duero; organically farmed, making structured, traditional reds (Pícaro, Reserva, Canta la Perdiz) and a rare clarete."),
    dict(slug="jose_gil", name="José Gil", ig="vigneronsdelasonsierra", country="Spain", region="Rioja", sub_region="San Vicente de la Sonsierra", appellations=["Rioja"], farming=["organic"], certifications=[], importer_us=["European Cellars"], tags=["rioja", "tempranillo", "old-vines"], summary="Third-generation San Vicente de la Sonsierra grower who launched his own label in 2011 after training in Burgundy and the Mosel; organic old-vine Tempranillo made into site-specific, Burgundian-styled Rioja. Tim Atkin's Young Winemaker of the Year 2021."),
    dict(slug="bodega_cerron", name="Bodega Cerrón", ig="bodega_cerron", country="Spain", region="Jumilla", sub_region="Fuente-Álamo", appellations=["Jumilla"], farming=["organic", "biodynamic"], certifications=[], importer_us=[], tags=["jumilla", "monastrell", "organic", "biodynamic"], summary="Fourth-generation family winery near Fuente-Álamo (Albacete) under DOP Jumilla, farming high-altitude (to ~1,050 m) ecological/biodynamic vineyards; the Cerdán siblings make high-altitude Monastrell and field-blend cuvées."),
    dict(slug="niepoort", name="Niepoort", ig="niepoort_wines", country="Portugal", region="Douro", sub_region="Cima Corgo", appellations=["Douro", "Port"], farming=[], certifications=[], importer_us=[], tags=["douro", "port", "old-vines"], summary="Iconic Douro house led by Dirk Niepoort, celebrated for both classic Ports and a benchmark range of elegant, old-vine Douro table wines (Redoma, Charme, Robustus)."),
    dict(slug="suertes_del_marques", name="Suertes del Marqués", ig="jonatanwine", country="Spain", region="Canary Islands", sub_region="Valle de la Orotava (Tenerife)", appellations=["Valle de la Orotava"], farming=[], certifications=[], importer_us=["European Cellars"], tags=["canary-islands", "tenerife", "listan-negro"], summary="Leading Tenerife estate in the Valle de la Orotava, working ungrafted, braided (cordón trenzado) old vines on volcanic soils; Jonatan García Lima makes electric Listán Negro reds and Listán Blanco whites."),
    # ---- Chile ----
    dict(slug="garage_wine_co", name="Garage Wine Co.", ig="garagewineco", country="Chile", region="Maule", sub_region="Maule (Truquilemu / Sauzal)", appellations=["Maule Valley"], farming=["organic"], certifications=[], importer_us=[], tags=["chile", "maule", "old-vines", "carignan"], summary="Maule pioneer working old, dry-farmed bush-vine Carignan and País from small parcels (a founder of the 'Vigno' Carignan movement), made in tiny lots in a traditional, terroir-driven style."),
    dict(slug="pedro_parra", name="Pedro Parra y Familia", ig="pedroparraterroir", country="Chile", region="Itata", sub_region="Itata (Guarilihue)", appellations=["Itata Valley"], farming=[], certifications=[], importer_us=[], tags=["chile", "itata", "cinsault", "old-vines"], summary="Project of renowned terroir consultant Pedro Parra in Itata, making precise, granite-driven old-vine Cinsault (Imaginador, Hub, Monk, Pencopolitano) that helped put southern Chile on the fine-wine map."),
    # ---- USA ----
    dict(slug="bedrock_wine_co", name="Bedrock Wine Co.", ig="bedrockmorgan", country="United States", region="California", sub_region="Sonoma Valley", appellations=["Sonoma Valley", "California"], farming=[], certifications=[], importer_us=[], tags=["california", "sonoma", "old-vines", "field-blend"], summary="Morgan Twain-Peterson MW's Sonoma winery, a champion of California's historic old-vine, mixed-black field-blend vineyards, plus serious Zinfandel and Syrah."),
    dict(slug="under_the_wire", name="Under the Wire", ig="underthewirewine", country="United States", region="California", sub_region="Sonoma", appellations=["Sonoma"], farming=[], certifications=[], importer_us=[], tags=["california", "sonoma", "sparkling"], summary="Vintage-dated sparkling-wine project from Bedrock's Morgan Twain-Peterson and Chris Cottrell, making single-vineyard, bottle-fermented sparklers from California sites."),
    dict(slug="turley_wine_cellars", name="Turley Wine Cellars", ig="turleywine", country="United States", region="California", sub_region="Napa / Paso Robles", appellations=["California"], farming=["organic"], certifications=[], importer_us=[], tags=["california", "zinfandel", "old-vines", "organic"], summary="Larry Turley's certified-organic winery, the leading specialist in old-vine Zinfandel and Petite Sirah from dozens of historic California vineyards."),
    dict(slug="ashes_and_diamonds", name="Ashes & Diamonds", ig="ashesxdiamonds", country="United States", region="California", sub_region="Napa Valley", appellations=["Napa Valley"], farming=[], certifications=[], importer_us=[], tags=["california", "napa", "cabernet-franc"], summary="Napa winery channeling a mid-century, lower-alcohol Napa aesthetic, focused on Bordeaux varieties (especially Cabernet Franc/Sauvignon blends) farmed for freshness."),
    dict(slug="harlan_estate", name="Harlan Estate", ig="harlanestate", country="United States", region="California", sub_region="Napa Valley (Oakville)", appellations=["Napa Valley", "Oakville"], farming=[], certifications=[], importer_us=[], tags=["california", "napa", "cult", "allocation-only"], summary="Benchmark Oakville hillside cult Napa Cabernet estate; powerful, opulent, age-worthy first wine plus The Maiden. (Stylistically outside Evan's restrained-Napa filter.)"),
    dict(slug="occidental_wines", name="Occidental", ig="occidentalwines", country="United States", region="California", sub_region="Sonoma Coast (Freestone)", appellations=["Sonoma Coast"], farming=[], certifications=[], importer_us=[], tags=["california", "sonoma-coast", "pinot-noir"], summary="Steve Kistler's extreme Sonoma Coast Pinot Noir project around Freestone-Occidental, making site-specific, cool-climate Pinot from densely planted hillside blocks."),
    dict(slug="lieu_dit", name="Lieu Dit", ig="lieuxdit", country="United States", region="California", sub_region="Santa Barbara County", appellations=["Santa Barbara County"], farming=[], certifications=[], importer_us=["Skurnik"], tags=["california", "santa-barbara", "loire-varieties"], summary="Santa Barbara winery (Eric Railsback and Justin Willett) devoted to Loire grape varieties — Sauvignon Blanc, Chenin Blanc, Cabernet Franc, Melon and Pineau d'Aunis — in a pure, balanced style."),
    dict(slug="jc_cellars", name="JC Cellars", ig="jeff.cohn", country="United States", region="California", sub_region="Sonoma / Sierra Foothills", appellations=["California"], farming=[], certifications=[], importer_us=[], tags=["california", "syrah", "rhone-varieties"], summary="Jeff Cohn's Rhône-focused California label, working old-vine Syrah, Zinfandel and Rhône varieties from distinctive sites across the state."),
    dict(slug="maison_noir_wines", name="Maison Noir Wines (André Hueston Mack)", ig="andrehmack", country="United States", region="Oregon", sub_region="Willamette Valley", appellations=["Willamette Valley", "Oregon"], farming=[], certifications=[], importer_us=[], tags=["oregon", "willamette", "pinot-noir"], summary="Oregon-focused label of former Per Se/French Laundry sommelier André Hueston Mack, known for streetwear-styled labels and serious Willamette Valley Pinot Noir and Chardonnay."),
    dict(slug="forman_vineyard", name="Forman Vineyard", ig="forman_vineyard", country="United States", region="California", sub_region="Napa Valley (St. Helena)", appellations=["Napa Valley"], farming=[], certifications=[], importer_us=[], tags=["california", "napa", "cabernet-sauvignon"], summary="Ric Forman's restrained, classically styled Napa estate, a benchmark for age-worthy, balanced Cabernet Sauvignon and Chardonnay from Howell Mountain and the valley floor."),
    dict(slug="tatomer", name="Tatomer", ig="grahamtatomer", country="United States", region="California", sub_region="Santa Barbara County", appellations=["Santa Barbara County"], farming=[], certifications=[], importer_us=[], tags=["california", "santa-barbara", "riesling", "gruner-veltliner"], summary="Graham Tatomer's Santa Barbara label specialising in Austrian-inspired, age-worthy Riesling and Grüner Veltliner — a rare California focus on those varieties."),
    dict(slug="pax_wines", name="Pax", ig="paxwines", country="United States", region="California", sub_region="Sonoma County", appellations=["Sonoma County", "North Coast"], farming=[], certifications=[], importer_us=[], tags=["california", "sonoma", "syrah", "gamay"], summary="Pax Mahle's Sonoma label, an early leader of the cooler, whole-cluster, lower-alcohol California Syrah movement, also making Gamay, Trousseau and characterful whites."),
    dict(slug="rodeo_hills", name="Rodeo Hills", ig="rodeohillswine", country="United States", region="Oregon", sub_region="Dundee Hills (Willamette Valley)", appellations=["Dundee Hills", "Willamette Valley"], farming=[], certifications=[], importer_us=[], tags=["oregon", "willamette", "pinot-noir", "micro-production"], summary="Small Dundee Hills estate (winemaker Jared Etzel) on high-elevation Worden Hill, making high-acid, low-alcohol Pinot Noir and Chardonnay from a seven-acre vineyard."),
    dict(slug="andrew_will_winery", name="Andrew Will Winery", ig="camarda_chris", country="United States", region="Washington", sub_region="Vashon Island / Columbia Valley", appellations=["Washington", "Columbia Valley"], farming=[], certifications=[], importer_us=[], tags=["washington", "cabernet-sauvignon", "bordeaux-blend"], summary="Chris Camarda's Vashon Island winery, a Washington benchmark for site-specific Bordeaux-style reds (Champoux, Ciel du Cheval, Two Blondes) in an elegant, age-worthy register."),
    dict(slug="fulldraw_vineyard", name="Fulldraw Vineyard", ig="fulldrawvineyard", country="United States", region="California", sub_region="Paso Robles (Willow Creek)", appellations=["Willow Creek District", "Paso Robles"], farming=[], certifications=[], importer_us=[], tags=["california", "paso-robles", "rhone-varieties"], summary="West-side Paso Robles family grower-producer (Connor McMahon) on limestone soils in the Templeton Gap, focused on tense, balanced Rhône varietal reds and whites; first vintage 2016."),
    dict(slug="revenant_wines", name="Revenant Wines", ig="revenantwinery", country="United States", region="California", sub_region="Napa Valley (Calistoga)", appellations=["Calistoga", "Napa Valley"], farming=[], certifications=[], importer_us=[], tags=["california", "napa", "calistoga"], summary="Small Calistoga producer (Anthony Knox, founded 2005) making unfiltered, acid-driven, blended Napa reds influenced by his mentors at Kalin Cellars."),
    dict(slug="00_wines", name="00 Wines", ig="house_of_00", country="United States", region="Oregon", sub_region="Willamette Valley", appellations=["Willamette Valley", "Oregon"], farming=[], certifications=[], importer_us=[], tags=["oregon", "willamette", "chardonnay", "pinot-noir"], summary="Willamette Valley label of Chris and Kathryn Hermann pursuing intense, structured, age-worthy Oregon Chardonnay (the 'black Chardonnay' method) and Pinot Noir from old-vine sites like Chehalem Mountain."),
    dict(slug="lawrence_wine_estates", name="Lawrence Wine Estates", ig="lawrencewineestates", country="United States", region="California", sub_region="Napa Valley", appellations=["Napa Valley"], farming=[], certifications=[], importer_us=[], tags=["california", "napa"], summary="Gaylon Lawrence/Carlton McCoy MS family wine group built around Heitz Cellar (2018) and including Burgess, Stony Hill, Brendel and Ink Grade, plus Bordeaux's Château Lascombes."),
    dict(slug="kobayashi_winery", name="Kobayashi Winery", ig="kobayashiwinery", country="United States", region="Washington", sub_region="Walla Walla Valley (Rocks District)", appellations=["Walla Walla Valley"], farming=[], certifications=[], importer_us=[], tags=["washington", "walla-walla", "syrah", "cabernet-franc"], summary="Travis Allen's small, acclaimed project (made at Force Majeure in Milton-Freewater) known for Syrah, Cabernet Franc and Riesling, distinctively aged in Japanese Mizunara oak."),
    # ---- Australia / Canada ----
    dict(slug="bass_phillip", name="Bass Phillip", ig="bassphillipofficial", country="Australia", region="Victoria", sub_region="Gippsland", appellations=["Gippsland"], farming=[], certifications=[], importer_us=[], tags=["australia", "gippsland", "pinot-noir"], summary="Legendary cool-climate Gippsland estate, Australia's most celebrated Pinot Noir address (founded by Phillip Jones; later guided by Jean-Marie Fourrier), making tiny quantities of Burgundian, age-worthy Pinot."),
    dict(slug="eastern_peake", name="Eastern Peake", ig="easternpeake", country="Australia", region="Victoria", sub_region="Ballarat", appellations=["Ballarat"], farming=[], certifications=[], importer_us=[], tags=["australia", "victoria", "pinot-noir", "chardonnay"], summary="High-plateau estate near Ballarat planted in the early 1980s, now led by second-generation Owen Latta (Young Gun of Wine 2025); minimal-intervention Pinot Noir and Chardonnay plus the Latta Vino négoce project."),
    dict(slug="syrahmi", name="Syrahmi", ig="syrahmi.wine", country="Australia", region="Victoria", sub_region="Heathcote", appellations=["Heathcote"], farming=[], certifications=[], importer_us=[], tags=["australia", "heathcote", "syrah"], summary="Adam Foster's Heathcote project (launched 2004), making Rhône-influenced, elegant Shiraz from Cambrian-soil parcels, now also from his own high-density Tooboorac plantings."),
    dict(slug="solum_wines", name="Solum Wines", ig="solum.wines", country="Australia", region="Victoria", sub_region="Mornington Peninsula", appellations=["Mornington Peninsula"], farming=[], certifications=[], importer_us=[], tags=["australia", "mornington", "pinot-noir", "chardonnay"], summary="Small Mornington Peninsula label of Ryan Horaczko making minimal-intervention, wild-fermented Pinot Noir, Chardonnay and Syrah from Red Hill and Balnarring."),
    dict(slug="giant_steps", name="Giant Steps", ig="steve_flamsteed", country="Australia", region="Victoria", sub_region="Yarra Valley", appellations=["Yarra Valley"], farming=[], certifications=[], importer_us=[], tags=["australia", "yarra-valley", "chardonnay", "pinot-noir"], summary="Leading Yarra Valley single-vineyard specialist (long-time winemaker Steve Flamsteed), making precise, terroir-focused Chardonnay and Pinot Noir."),
    dict(slug="grimsby_hillside_vineyard", name="Grimsby Hillside Vineyard", ig="grimsbyhillsidevineyard", country="Canada", region="Ontario", sub_region="Niagara Peninsula (Lincoln Lakeshore)", appellations=["Niagara Peninsula", "Lincoln Lakeshore"], farming=["organic"], certifications=[], importer_us=[], tags=["canada", "niagara", "riesling", "micro-production"], summary="Historic, certified-organic Niagara escarpment vineyard (Franciosa family) first planted in 1874, supplying top Ontario winemakers (Leaning Post, Bachelder, Pearl Morissette) and bottling Riesling, Cabernet Franc, Chardonnay and Pinot Noir."),
    # ---- Japan / Sweden / China ----
    dict(slug="domaine_takahiko", name="Domaine Takahiko", ig="domaine_takahiko", country="Japan", region="Hokkaido", sub_region="Yoichi", appellations=["Hokkaido"], farming=["organic", "natural"], certifications=[], importer_us=[], tags=["japan", "hokkaido", "pinot-noir", "micro-production"], summary="Cult Hokkaido estate of Takahiko Soga in Yoichi, making tiny quantities of delicate, sought-after Pinot Noir ('Nana-Tsu-Mori') by natural, low-intervention methods."),
    dict(slug="toro_vingard", name="Torö Vingård", ig="torovingard", country="Sweden", region="Stockholm Archipelago", sub_region="Torö", appellations=[], farming=[], certifications=[], importer_us=[], tags=["sweden", "cool-climate", "micro-production"], summary="Small Swedish wine estate (presenting itself as Torö Vingård – Domaine Ganansia) on the island of Torö in the Stockholm archipelago. Details beyond the location are unverified."),
    dict(slug="domaine_muxin", name="Domaine Muxin", ig="domaine.muxin", country="China", region="Yunnan", sub_region="Cizhong", appellations=[], farming=["natural"], certifications=[], importer_us=[], tags=["china", "yunnan", "chardonnay", "micro-production"], summary="High-altitude Yunnan estate (vineyards to ~2,700 m at Cizhong) founded by Burgundy-trained Mu Chao, making a precise, mineral, native-yeast, unfined/unfiltered Chardonnay considered among China's finest."),
    # ---- Cider / Poiré ----
    dict(slug="domaine_eric_bordelet", name="Domaine Eric Bordelet", ig="domaineericbordelet", country="France", region="Normandy", sub_region="Charchigné (Mayenne)", appellations=["Poiré", "Cidre"], farming=["biodynamic"], certifications=[], importer_us=["Louis/Dressner"], tags=["normandy", "cider", "poire", "biodynamic"], summary="Former Parisian sommelier Eric Bordelet makes the reference biodynamic poiré (pear) and cidre from old orchards on schist and granite in the Mayenne, on the Normandy/Maine border — benchmark, terroir-driven traditional-method ciders."),
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
