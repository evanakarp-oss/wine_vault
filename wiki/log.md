---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-25] offers | weekly roundup setup + dry run (12 emails, 3 vault hits, 25 missing)

Added `raw/offers/` ingest tree, `scripts/compile_offers_roundup.py`, and the first `wiki/_views/offers_2026-05-25.md` view. Window: 2026-05-19 → 2026-05-25. Senders covered: CSW (`office@chambersstwines.com`), Flatiron (`offers@/<rep>@flatiron-wines.com`), Leon & Son (`info@leonandsonwine.com`), R Squared (`info@rsquaredselections.com`).

Two-pass extraction this week: (1) subjects + snippets for the obvious cases, (2) full `plaintextBody` via Gmail MCP for the click-through teasers (Flatiron NR, CSW Private Collections, Leon Muscadet). Vault hits: [[jacques_lassaigne|Jacques Lassaigne]] + [[franck_balthazar|Franck Balthazar]] (R Squared parcel), [[domaine_levet|Domaine Levet]] (Flatiron Northern Rhone cellar — alongside still-missing Marcel Juge + Jamet). None in cellar.

25 producers mentioned without vault pages — biggest cluster is Loire / Muscadet from Leon's New York Wine Auctions debut (Pépière dominates with ~30 lots, plus l'Ecu / Brégeon / Luneau-Papin / Delhommeau / Landron). Loire/Muscadet is a clear curation gap.

Retailer landing pages (`chambersstwines.com`, `nyc.flatiron-wines.com`, etc.) are blocked by this container's egress policy — recorded as `landing_page_url` with `landing_page_fetched: false`; view surfaces a ⚠︎ marker so the user can open manually. See `raw/offers/README.md` for the weekly workflow.

