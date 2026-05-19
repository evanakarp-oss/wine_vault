---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

_No entries yet._

## [2026-05-19] ingest | FASS email offers → 12 producer pages

Added `scripts/ingest_fass_emails.py` and ran it against the 180 FASS email
markdown files already in `raw/fass/markdown/`. Each email pitches a single
wine; the script extracts vintage / offer price / score / snippet
heuristically and matches the producer by scanning the title + opening of
the pitch body (before the "Previous Offers Still Open" footer, which
name-drops dozens of unrelated benchmark producers).

Matched 47 emails to 12 wiki producers under a new `## FASS Offers` body
section, kept distinct from the JSX-driven `## FASS` portfolio section so
the two sources never clobber each other. Top recipients: `steinmetz` (10),
`enderle__moll` (9), `francois_buffet` (8), `sven_enderle` (7). The
remaining 133 emails pitch producers not in `wiki/producers/` and are
listed in `build/fass_emails_ingest_report.md` for later curation.

Idempotent — re-run after dropping new email .md files into
`raw/fass/markdown/` and the section rebuilds in place. `--check` exits
non-zero if any page would change, suitable for CI.

