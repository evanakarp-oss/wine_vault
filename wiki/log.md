---
type: log
total_entries: 2
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-21] ingest | Kermit Lynch portfolio cross-checked against Raeders inventory

- Source landed: `raw/kermit_lynch/portfolio_2026-05-21.md` (146 France + 47 Italy-Grower producers, 193 total).
- Cross-check view: `wiki/_views/kermit_lynch_at_raeders.md` — 30 KL producers found at Raeder's (67 bottles in stock).
- Updated `wiki/producers/lucien_boillot.md` + `meo_camuzet.md`: added `importer_us: Kermit Lynch`.
- Hand-patched `wiki/importers/Kermit_Lynch.md` (10 → 12 producers). `scripts/build_rollups.py` has a latent bug: `get_list()` regex only matches inline-flow YAML lists, not block style, so the script grouped only 3 of 12 producers. Fix in a follow-up.
- Open question for Evan: 8 of the existing 10 wiki KL producers (Pierre André, Joncuas, Charvin, Barou, Levet, Balthazar, Esmonin, Ferme Saint-Martin) are not on the newly-pasted portfolio — likely KL dropouts.
- Portfolio completeness verified later in same session: re-pasted full kermitlynch.com/growers page (single alphabetized list, not country-grouped) and diffed against stored source — zero deltas (193 = 193).

## [2026-05-21] compile | Strip stale Kermit Lynch importer tag from 8 ex-portfolio producers

- Stripped `importer_us: Kermit Lynch` from 8 producers that are no longer on the current kermitlynch.com/growers page: Domaine Pierre André, Clos du Joncuas, Sylvie Esmonin, Domaine Charvin, Domaine Barou, Domaine Levet, Franck Balthazar, Ferme Saint-Martin.
- These were inferred from older CSW write-ups; the CSW Write-ups sections remain intact on each producer page.
- Updated `wiki/importers/Kermit_Lynch.md`: now lists 4 current KL producers (Pierre Gonon, Allemand, Méo-Camuzet, Lucien Boillot) plus a "Recently dropped" section for the 8 ex-importers.
- Updated `wiki/_views/kermit_lynch_at_raeders.md`: marked Issue 1 resolved.

