---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-25] offers | weekly roundup setup + dry run (12 emails, 2 vault hits)

Added `raw/offers/` ingest tree, `scripts/compile_offers_roundup.py`, and the first `wiki/_views/offers_2026-05-25.md` view. Window: 2026-05-19 → 2026-05-25. Senders covered: CSW (`office@chambersstwines.com`), Flatiron (`offers@/<rep>@flatiron-wines.com`), Leon & Son (`info@leonandsonwine.com`), R Squared (`info@rsquaredselections.com`). Vault hits this week: [[jacques_lassaigne|Jacques Lassaigne]], [[franck_balthazar|Franck Balthazar]] — both in R Squared's parcel offer; neither in cellar. 15 producers mentioned without a vault page (candidates if recurring). See `raw/offers/README.md` for the weekly workflow.

