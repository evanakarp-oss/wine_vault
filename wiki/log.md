---
type: log
total_entries: 1
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
- Open questions for Evan: (a) 8 of the existing 10 wiki KL producers (Pierre André, Joncuas, Charvin, Barou, Levet, Balthazar, Esmonin, Ferme Saint-Martin) are not on the newly-pasted portfolio — KL dropouts or incomplete paste? (b) Italy paste was preceded by "GROWER" header; other KL Italy categories (Négoce / NV) may still be missing.

