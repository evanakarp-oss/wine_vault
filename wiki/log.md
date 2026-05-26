---
type: log
total_entries: 0
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-26] ingest | Hugh Johnson Atlas — Loire + SW France sub-region pages

Drafted six editorial sub-region pages from photos of the World Atlas of Wine
(Johnson & Robinson):

- `wiki/regions/Loire_Muscadet.md`
- `wiki/regions/Loire_Anjou.md`
- `wiki/regions/Loire_Saumur.md`
- `wiki/regions/Loire_Chinon_Bourgueil.md`
- `wiki/regions/Loire_Vouvray_Montlouis.md`
- `wiki/regions/South_West_Bergerac.md`

Plus a cross-cutting gap analysis at `wiki/_views/atlas_loire_sw_gaps.md`
listing ~50 producers named on the Atlas maps that lack pages in
`wiki/producers/` (only 5 of the named producers exist as pages today:
Domaine Baudry, Bernard Baudry, Chevalerie, Stéphane Guion, Clos Rougeard).

Atlas alone is a single source — none of the gap-list producers were
auto-promoted to producer pages. Promotion gated on CSW corroboration
(per CLAUDE.md curation rules). Top promotion priorities flagged in the
gap view: Huet, Clos Naudin (Foreau), Chidaine, Taille aux Loups,
Roches Neuves (Germain), Nicolas Joly, Joguet, Tour des Gendres.

Page type `region_overview` is new — lint skips non-producer types so
no schema work needed. Source is copyrighted; treat as a discovery
guide, not a paste-in.

