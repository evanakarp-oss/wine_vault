---
type: log
total_entries: 3
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

## [2026-05-21] ingest | Rosenthal Wine Merchant portfolio cross-checked against Raeders inventory

- Source landed: `raw/rosenthal/portfolio_2026-05-21.md` (145 producers — France 86 / Italy 46 / Switzerland 5 / Austria 4 / Spain 4). Page does not print country labels; country inferred from location keywords during parse.
- Cross-check view: `wiki/_views/rosenthal_at_raeders.md` — 8 Rosenthal producers found at Raeder's (13 bottles in stock). Hubert Lignier dominant with 5 cuvées; Harmand-Geoffroy Mazis-Chambertin GC 2020 is the headline grand-cru bottle.
- Hand-patched `wiki/importers/Neal_Rosenthal.md`: bumped from 1 to 7 confirmed-current Rosenthal producers already in the wiki (Brovia, Le Puy, Cheveau, Lionnet, Elio Sandri, Puffeney, Gahier — the rollup script's YAML block-list bug had hidden 6 of these). Added a "Curation candidates" section for the 8 Raeder's-stocked producers without wiki pages, top picks Hubert Lignier and Harmand-Geoffroy.
- Open question for Evan: Bernhard Huber (Baden) is tagged `importer_us: Neal Rosenthal` but the pasted portfolio has NO German producers at all. Could be (a) Huber dropped, (b) moved importer, or (c) the rosenthalwinemerchant.com/growers page is region-filtered and Germany is on a separate view. Flagged on the importer page as pending verification.

