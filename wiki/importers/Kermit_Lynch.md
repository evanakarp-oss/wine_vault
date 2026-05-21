---
type: importer
name: "Kermit Lynch"
slug: kermit_lynch
producer_count: 12
focus: ['Burgundy', 'Rhône']
notable_producers: ['Domaine Pierre Gonon', 'Méo-Camuzet', 'Domaine Pierre André', 'Clos du Joncuas', 'Allemand']
updated: 2026-05-21
---

# Kermit Lynch

**12 producer(s)** in the vault imported by Kermit Lynch (US). The full KL portfolio is 193 producers (146 France + 47 Italy Grower) — see `raw/kermit_lynch/portfolio_2026-05-21.md`. For the cross-check against Raeder's inventory, see [[kermit_lynch_at_raeders|Kermit Lynch at Raeder's]] (30 producers, 67 bottles).

| Producer | Country | Region | CSW | Cellar |
|---|---|---|---:|---:|
| [[domaine_pierre_gonon|Domaine Pierre Gonon]] | France | Rhône | 34 | — |
| [[domaine_pierre_andre|Domaine Pierre André]] | France | Rhône | 12 | — |
| [[clos_du_joncuas|Clos du Joncuas]] | France | Rhône | 10 | — |
| [[allemand|Allemand]] | France | Rhône | 9 | — |
| [[sylvie_esmonin|Sylvie Esmonin]] | France | Burgundy | 8 | — |
| [[domaine_charvin|Domaine Charvin]] | France | Rhône | 7 | — |
| [[domaine_barou|Domaine Barou]] | France | Rhône | 6 | — |
| [[domaine_levet|Domaine Levet]] | France | Rhône | 6 | — |
| [[franck_balthazar|Franck Balthazar]] | France | Rhône | 5 | — |
| [[ferme_saint-martin|Ferme Saint-Martin]] | France | Rhône | 4 | — |
| [[meo_camuzet|Méo-Camuzet]] | France | Burgundy | 1 | — |
| [[lucien_boillot|Lucien Boillot]] | France | Burgundy | 0 | — |

*Hand-patched 2026-05-21. `scripts/build_rollups.py` has a latent bug — `get_list()` regex only matches inline-style YAML lists (`importer_us: ["Kermit Lynch"]`) but the wiki uses block style (`importer_us:\n- Kermit Lynch`), so the rollup grouped only 3 of 12 producers. Fix `get_list` in build_rollups.py to also parse block lists, then this file can be regenerated.*
