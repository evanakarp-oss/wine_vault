---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-18] ingest | Sardinia bootstrap: taxonomy + Cardedu

First Sardinian content in the vault.

- Added `Sardinia` to `_TAXONOMY.md` Italy regions (between Sicily and Veneto).
- Created `wiki/producers/cardedu.md` from `raw/csw/markdown/sardinian-spotlight-cardedu.md` (Andy Paynter, 2018-06). Sergio Loi, Ogliastra; dry-farmed, native yeasts, unfined/unfiltered. Cuvées noted: Vermentino, Monica, Cannonau. Tagged `farming: [organic]` based on article description (no certification claimed).
- Ran `scripts/build_rollups.py` — generated `wiki/regions/Sardinia_Producers.md` (1 producer).
- Ran `scripts/build_wiki_index.py` — refreshed catalog.

Existing Sardinian signals not yet promoted to producer pages (per CLAUDE.md, Raeders alone doesn't justify creating pages): Argiolas Costamolino, Surrau Naracu, Sella & Mosca Riserva. Hold for CSW or Berserkers corroboration.

Candidate next-source targets for Sardinia depth (no raw coverage yet): Tenute Dettori, Giuseppe Sedilesu, Giovanni Montisci (Barrosu), Cantina Santadi, Agricola Punica, Capichera, Panevino.

