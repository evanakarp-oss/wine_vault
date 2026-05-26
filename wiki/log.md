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

