---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-25] view | Marsannay (incl. Chenôve)

Filed `wiki/_views/marsannay.md` covering the three communes (Chenôve / Marsannay-la-Côte / Couchey), the 2024 INAO 1er Cru promotion of 12 climats (Clos du Roy, Longeroies, La Charme aux Prêtres, etc.), Chenôve flagship sites (Clos du Roy history, Le Chapitre promoted to Marsannay AOC in 2019), and a curation-tuned producer ranking. Surfaced gap: René Bouvier "Bourgogne Chapitre" text in `raw/csw/markdown/` is stale post-2019. Producer stubs to add: Jean-Yves Bizot, Bruno Clair, Charlopin Tissier, Régis Bouvier, René Bouvier.

## [2026-05-25] view | Burgundy Best Value

Filed `wiki/_views/burgundy_best_value.md` cross-indexing Kelley value picks (Berserkers thread excerpts already in vault) and CSW dedicated-article ★ champions across the value-tier appellations: Marsannay, Fixin, Auxey-Duresses, Saint-Romain, Santenay, Maranges, Mercurey, Rully, Givry, Mâconnais, Chablis, Savigny / Pernand. Producer stubs flagged: Alain Gras, Bachelet-Monnot, François Raquillet, Dureuil-Janthial, Clos Salomon.

## [2026-05-25] view | Burgundy Commune Field Guide

Filed `wiki/_views/burgundy_communes.md` — comprehensive commune-by-commune breakdown across all of Burgundy (Côte de Nuits, Côte de Beaune, Côte Chalonnaise, Mâconnais, Chablis). For each commune: Grand Cru / Premier Cru / commune-level vineyards, top producers, curation verdict (🔥/💰/👑/⏭), and Kelley-endorsement flags. Top-10 most-compelling-for-Evan ranking at top: Marsannay, Saint-Aubin, Auxey-Duresses+Saint-Romain, Mercurey+Givry, Chablis 1er Cru, Pernand+Ladoix, Chambolle Cras/Fuées, Viré-Clessé/Mâcon, Maranges, NSG south. Sources: WAW 8e (atlas excerpts), Decanter, Jasper Morris, Becky Wasserman, Flatiron, Berserkers Kelley posts.

## [2026-05-25] producers | 22 new stubs

Created producer stubs for everyone surfaced in the commune view + Kelley/Atlas/web research: jean_yves_bizot, bruno_clair, charlopin_tissier, rene_bouvier, regis_bouvier (Marsannay); alain_gras (Saint-Romain), bachelet_monnot (Maranges), francois_raquillet (Mercurey), dureuil_janthial (Rully), clos_salomon, domaine_joblot, francois_lumpp (Givry); domaine_larue, pierre_girardin (Saint-Aubin); marquis_d_angerville, michel_lafarge (Volnay); comte_armand, de_courcel (Pommard); robert_chevillon (Nuits-Saint-Georges); domaine_roumier, ghislaine_barthod, jacques_frederic_mugnier (Chambolle-Musigny); domaine_des_comtes_lafon, olivier_merlin (Meursault/Mâcon); michel_juillot, domaine_faiveley (Mercurey+); de_villaine (Bouzeron); stephane_aladame (Montagny). All flagged with Kelley-pick / Kelley-adjacent / atlas-named tags where applicable. Stubs are minimal (no retailer presence yet) — designed to make wikilinks in the views resolve while leaving room for CSW/DTE/Raeders ingest passes to populate.

