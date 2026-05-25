---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

_No entries yet._

## [2026-05-25] view | Vosne-Romanée adjacent parcels (N & S)

New study view at `wiki/_views/vosne_adjacent_parcels.md` covering the climats on
either flank of Vosne-Romanée — the NSG "Vosne shoulder" (Boudots / Damodes / Cras /
Murgers / Thorey / Chaignots) on the south side, and the Flagey-Échézeaux / Vougeot /
Chambolle-Musigny continuum on the north — with terroir notes pulled from the *World
Atlas of Wine* and a tiered value pick-list pulled from current DTE / Raeder's / CSW
coverage in the vault. Headline NSG-adjacent value: [[domaine_jean_chauvenet|Jean
Chauvenet]] (CSW's literal "Vosne value" framing), [[chicotot|Chicotot]] (DTE depth
$45–$179), [[domaine_forey|Forey]] (CSW championed, aging-grade 1). Logs gaps:
Chevillon, Gouges, Clavelier, Mugneret-Gibourg, Grivot, Lamarche, Anne Gros all
missing from the vault.

## [2026-05-25] producers | Vosne core — 8 reference pages added

Closed the gaps flagged in the `vosne_adjacent_parcels` view. New producer
pages: [[robert_chevillon|Robert Chevillon]] (NSG reference, 8 1er Crus across
both sides of the town), [[henri_gouges|Henri Gouges]] (NSG, historic AOC
founder, Pinot Gouges white mutation), [[domaine_de_l_arlot|Domaine de
l'Arlot]] (AXA-owned, Prémeaux monopoles + Suchots + RSV — full S-to-N arc),
[[bruno_clavelier|Bruno Clavelier]] (biodynamic Vosne, old-vine villages,
CSW "Rising Star 2005"), [[mugneret_gibourg|Mugneret-Gibourg]] (Vosne
allocation reference, NSG Chaignots + Échézeaux + Clos Vougeot + Ruchottes),
[[domaine_grivot|Domaine Grivot]] (Vosne, Mathilde-era, Richebourg + Boudots
+ Suchots + Beaumonts), [[domaine_lamarche|Domaine François Lamarche]]
(La Grande Rue monopole between RC and La Tâche; Malconsorts; Nicole-era
turnaround), [[anne_gros|Anne Gros]] (Vosne, upper-slope Clos Vougeot Grand
Maupertui + Chambolle Combe d'Orveau monopole + Richebourg). All pages
hand-authored with no current retailer presence (`championed: false`,
`in_portfolio: false`), tagged for future ingest if CSW/DTE/Raeder's coverage
appears. Ran `build_rollups.py` (Burgundy_Producers now 100 producers) and
`build_wiki_index.py` (460 wiki pages indexed). Lint: 0 new issues introduced;
1 false-positive `broken_wikilink` for view-page references is by design
(lint only checks producer-slug targets).

