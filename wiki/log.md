---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-25] offers | CSW Memorial Day flash sale picks (16 vault hits, 1 cellar overlap)

User pasted the live CSW Memorial Day flash sale listing (154 wines, 15% off one-day) into session — bypassing the egress-blocked landing page. Re-extracted producer mentions into the upstream offer file (`chambers_19e5afef9f888561.md` flipped from `meta` to `flash_sale`); compile script now finds **16 vault producers** (was 3) and the cellar overlay surfaces [[roagna|Roagna]] (own 2020 Langhe Rosso; CSW offering 2016 Crichet Paje).

Hand-curated shortlist saved to [[offers_2026-05-25_csw_flash_top_picks|CSW Flash Sale Picks]]. Standouts: Cavallotto 1971-81 Riservas $175-275, Produttori del Barbaresco vertical 1962-94 sub-$150, Chevalerie 2019 Bourgueils $43-47, Cappellano 2018 Pie Rupestris 1.5L $400, biodynamic grower Champagne (Beaufort / Léclapart), aged Nahe Riesling (Schäfer-Fröhlich, Dönnhoff). New curation candidates: Cappellano, André Beaufort, David Léclapart, Edmond Vatan.

Cross-retailer signal: **Valentini** (Abruzzo) now in both CSW and R Squared this week — first multi-source hit. Worth a page if a third source shows up.

## [2026-05-25] offers | weekly roundup setup + dry run (12 emails, 3 vault hits, 25 missing)

Added `raw/offers/` ingest tree, `scripts/compile_offers_roundup.py`, and the first `wiki/_views/offers_2026-05-25.md` view. Window: 2026-05-19 → 2026-05-25. Senders covered: CSW (`office@chambersstwines.com`), Flatiron (`offers@/<rep>@flatiron-wines.com`), Leon & Son (`info@leonandsonwine.com`), R Squared (`info@rsquaredselections.com`).

Two-pass extraction this week: (1) subjects + snippets for the obvious cases, (2) full `plaintextBody` via Gmail MCP for the click-through teasers (Flatiron NR, CSW Private Collections, Leon Muscadet). Vault hits: [[jacques_lassaigne|Jacques Lassaigne]] + [[franck_balthazar|Franck Balthazar]] (R Squared parcel), [[domaine_levet|Domaine Levet]] (Flatiron Northern Rhone cellar — alongside still-missing Marcel Juge + Jamet). None in cellar.

25 producers mentioned without vault pages — biggest cluster is Loire / Muscadet from Leon's New York Wine Auctions debut (Pépière dominates with ~30 lots, plus l'Ecu / Brégeon / Luneau-Papin / Delhommeau / Landron). Loire/Muscadet is a clear curation gap.

Retailer landing pages (`chambersstwines.com`, `nyc.flatiron-wines.com`, etc.) are blocked by this container's egress policy — recorded as `landing_page_url` with `landing_page_fetched: false`; view surfaces a ⚠︎ marker so the user can open manually. See `raw/offers/README.md` for the weekly workflow.

