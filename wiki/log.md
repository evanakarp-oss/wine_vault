---
type: log
total_entries: 4
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-18] ingest | ingest: bootstrap wiki/index.md + wiki/log.md (Karpathy pattern)

_commit `dee2fa8`_

## [2026-05-18] edit | chore: stop tracking regenerable + transient + per-machine state

_commit `1af1055`_

## [2026-05-18] edit | ci: add check workflow for index/log validation

_commit `36ec32e`_

## [2026-05-18] edit | ci: pin pyyaml in requirements.txt for cache key

_commit `f0cecd1`_

## [2026-05-26] ingest | close 5 follow-ups: ask-cellar, clippings pipeline, widget JSON, resources → per-entity pages

Closed every actionable item on the "Open follow-ups" list:

- **`/ask-cellar` skill** — written in-repo at
  `.claude/skills/ask-cellar/SKILL.md`. Points at `wine_vault/wiki/` +
  `cellar/` + `raw/`. Documents read-order, citation format, and the
  "file keeper answers back to `wiki/_views/`" rule.
- **Vinous + Wine Advocate (Kelley) ingest** — `raw/clippings/vinous/`
  and `raw/clippings/wine_advocate/` ready to receive Obsidian Web
  Clipper output. `scripts/compile_clippings.py <source> --apply`
  reads them, writes `## Vinous Reviews` / `## Wine Advocate (Kelley)`
  sections on matched producer pages. Schema documented in
  `_SCHEMA.md`. Unmatched clippings list in
  `build/clippings_report.md` for review.
- **Widget JSON** — `scripts/build_widget_json.py` emits
  `build/widget_data.json` (368 producers + 631 cellar bottles in
  one fetch). JSX widget switches from hardcoded arrays to
  `fetch('/build/widget_data.json')`.
- **`_resources.md` → per-entity pages** — flat ~190-entry reference
  migrated to 66 importer pages + 129 retailer pages, with
  url/focus/tags frontmatter and the original prose preserved as the
  body. `build_rollups.py` now preserves hand-edited frontmatter +
  body, regenerating only inside `<!-- BEGIN AUTO-GENERATED -->`
  markers. `_resources.md` kept as legacy flat export.
- **Raeders candidates triage** — `audit_raeders_candidates.py`
  produces `build/raeders_candidates.md` (1,541 candidates,
  SKU-sorted, curation-tagged). Onboarding still goes through
  `compile_raeders_creates_v2.py` to keep the curation-by-human
  gate in place.

Index grew 423 → 605 pages with the importer/retailer migration.

## [2026-05-26] lint | repair vault architecture — lint 66 → 0, regions 57 → 37

Resolved the three preconditions of the Karpathy pattern that had drifted
since the 2026-04-21 baseline:

- **Source of truth.** Decided git is canonical (Drive is a read-only
  mirror going forward). No more `wiki/wiki/` divergence chasing.
- **Curated index.** Region rollups went 57 → 37 by collapsing
  `Mosel (Dhron)` / `Sicily (Etna)` / `Barolo (Castiglione Falletto)` /
  etc. into `region: <parent>` + `sub_region: <granular>` per
  `_TAXONOMY.md`. The LLM's first-read surface now shows real regions,
  not schema decay.
- **Append-only log.** Seeded from git history (this file), wired
  `lint.py --strict` into CI so the next regression fails on push.

Run: `scripts/fix_vault_architecture.py --apply` →
`scripts/build_rollups.py` → `scripts/build_wiki_index.py` →
`scripts/lint.py` (0 issues).

Changes: 8 surname-collision dupes deleted (`rousset`, `garon`, `piane`,
`magnien`, `mallard`, `paris`, `tissot`, `produttori`), 2 relics removed
(`wiki/producers/index.md` CSW master index, `domaine_chanter├¬ves.md`
mojibake), 48 region fields normalized, 5 no-frontmatter pages
synthesized, 11 alias entries added for disambiguation.

Producer count: 378 → 368. Lint: 66 → 0.

