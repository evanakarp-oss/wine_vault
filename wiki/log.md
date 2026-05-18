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

## [2026-05-18] query | Cellar gap analysis — regions to expand

Filed analysis as `wiki/_views/cellar_gap_analysis_2026-05.md` so it doesn't disappear into chat (per CLAUDE.md query op).

Baseline: 631 bottles / 294 entries / cross-referenced against `Curation taste` filters in CLAUDE.md.

Top region gaps surfaced (priority order):

1. **Champagne** (6 btl) — stated taste calls for grower / aged tête-de-cuvée; only Pierre Peters + Dom Pérignon pages exist. Targets: Ulysse Collin, Chartogne-Taillet, Egly-Ouriet, Vouette & Sorbée, Prévost, Bérêche, Krug Collection, Salon.
2. **Loire** (9 btl / 2 producers) — `domaine_baudry` is the #1 CSW-championed producer in the whole vault (45 articles, 20 ★) and Evan owns zero. Plus Huet, Foreau, Cotat, Joly, Mosse.
3. **Jura** (0 btl) — `Jura_Producers.md` exists; wiki ahead of cellar. Tissot, Ganevat pages built; add Overnoy-Houillon, Labet, Macle.
4. **Mosel / Saar / Nahe** (16 btl) — 7 village rollups built but cellar shallow. Falkenstein, Willi Schaefer, Schäfer-Fröhlich, Weiser-Künstler, Clemens Busch all have CSW-backed pages already.
5. **Spain — Bierzo / Galicia** (4 btl) — Castro Ventosa exists; add Raúl Pérez, Mengoba, Rodrigo Méndez, Forjas del Salnés.
6. **Beaujolais crus** (14 btl, all Lapierre) — broaden to Foillard, Métras, Dutraive, Descombes, Chignard.

Explicit no-grow zones: Napa cult Cab (hold at current Hundred Acre/Renaissance), Bordeaux mid-tier (current 8 classed-growths = stated quota), generic CA Chardonnay.

All ✓-marked wikilinks verified against producer slugs.

