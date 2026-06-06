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

## [2026-05-26] build | Drive auto-mirror + weekly audit GitHub Actions, plus WORKFLOW.md

Eliminates the source-of-truth ambiguity that caused the original
architecture failure. Git becomes the only place to edit; Drive
becomes an auto-mirrored read-only output.

Three new artifacts:

- `.github/workflows/drive_mirror.yml` — on every push to `main`,
  runs `rclone sync . gdrive:` to overwrite the canonical Drive
  `wine_vault/` folder from the repo. Excludes `.git/`, `.github/`,
  `build/`, legacy folders. Concurrency-grouped so only the latest
  push wins. Supports manual dispatch with a dry-run flag.

- `.github/workflows/drive_audit.yml` + `scripts/drive_audit.py` —
  weekly (Sunday 18:00 UTC), lists Drive files via `rclone lsjson`,
  diffs against `git ls-files`, writes `build/drive_audit.md`,
  opens a GitHub issue (labeled `drive-drift`, `audit`) if anything
  is unique to Drive. Catches the kind of one-off Drive uploads
  that produced the Roscioli orphan and the wiki/wiki/ divergence.

- `WORKFLOW.md` — single-page guide to where edits go (Claude Code,
  Working Copy iOS, local clone) vs where they don't (Drive web UI,
  Obsidian-on-Drive, chat upload). Also documents the one-time
  Google service-account setup needed for both workflows.

CLAUDE.md + README.md updated to point at WORKFLOW.md.

**Requires (one-time)**: a Google service-account JSON key with
Drive API enabled, the service-account email shared as Editor on
the `wine_vault/` Drive folder, and the JSON added as the
`GDRIVE_SERVICE_ACCOUNT_JSON` GitHub repo secret. Full steps in
WORKFLOW.md.

## [2026-05-26] ingest | Roscioli Wine Club pulled from Drive (importer + schema patch + 4 merges)

User shared a Drive folder of orphaned Roscioli scrape outputs from
2026-05-19 that never made it into git. Pulled via the Drive MCP:

- `wiki/importers/Roscioli_Wine_Club.md` — 156-producer Italian
  importer-curator rollup (Roagna, Cascina delle Rose, Le Macchiole,
  Castello dei Rampolla, Montevertine, Le Ragnaie, Emidio Pepe,
  Arpepe, Ferrari, Tenuta delle Terre Nere as notable producers).
- Applied schema patch: added `roscioli:` top-level frontmatter block
  to `_SCHEMA.md` (between `retailers:` and `events:`).
- Registered `roscioli_wine_club` as a new `source:` taxonomy entry
  in `_TAXONOMY.md`.
- Merged 4 snippets into existing producer pages: `bruna.md`,
  `cascina_delle_rose.md`, `fratelli_alessandria.md`, `roagna.md` —
  each got `roscioli:` frontmatter + `## Roscioli Wine Club` body
  section + `[[Roscioli_Wine_Club|Roscioli Wine Club (importer)]]`
  cross-reference.
- Updated `/ask-cellar` SKILL.md: read-order now lists Roscioli as
  the strongest Italian-importer hub; anti-patterns note Italian-only
  scope.

**Gap discovered**: the 2026-05-19 patch claimed 152 new producer pages
were uploaded to Drive. Searches by parentId + fullText returned only
the 7 files above. The 152 producer pages don't exist on Drive
(scraper may have failed mid-run, or pages were deleted in a cleanup).
Logged as open follow-up; the importer rollup page lists all 156
names + profile URLs for re-seeding.

## [2026-05-26] lint | second-pass dedup from 2026-05-10 audit bundle (lint check tightened)

User shared `wine_vault_cleanup_bundle.zip` (Drive ID
`1-hEdGpaPhbEYRQpssLS1GEhrWCdqFwcE`) — a 2026-05-10 cleanup plan that
predated the git bootstrap. Most of its goals were already met by
prior commits (wiki/wiki/ Berserkers content merged, schema docs
updated, 60 lint issues cleared, GitHub set up). The bundle's
`SESSION_FINDINGS.md` surfaced 5 dedup pairs my earlier lint missed —
they had `article_count: 0` in frontmatter but real `### [...]`
article sections in the body, so the surname-collision check (gated
on article_count > 0) didn't fire.

Tightened `scripts/lint.py` to use `max(frontmatter article_count,
body ### section count)` as the effective coverage signal. That
surfaced 2 more pairs (audoin/charles_audoin, lafouge/...) plus 2
sets of genuinely-distinct producers (Bordeaux Ségur pair, Burgundy
Noëllat trio) needing aliases.

Total: 8 false-positive bare-slug pages deleted; 7 alias entries
added; 5 disambiguation alias sets added for distinct same-surname
producers.

Deleted: `lorenzon`, `guyon`, `tawse`, `bursin`, `schaefer_frohlich`,
`schafer_frohlich`, `audoin`, `lafouge` (all bare slugs that were
CSW-matcher false positives).

Producer count: 368 → 360. Lint: 0.

## [2026-05-26] lint | Drive cleanup: drop _drive_sync + wine_vault_fromdocuments references

Approved to delete from Drive:
- `_drive_sync/wine_wiki_v2/` (pre-migration legacy)
- `wine_vault_fromdocuments/` (stale 2026-04-24 ZIP snapshot)

Repo-side cleanup of references to these now-deleted paths:

- `README.md` directory map: dropped `_drive_sync/` row.
- `CLAUDE.md` directory map: dropped `_drive_sync/` row; "Drive
  duplicates" follow-up narrowed to `wiki/wiki/` only.
- `_canonical_ids.md`: marked the two folders as deleted; pruned
  cleanup checklist to `wiki/wiki/`.
- `scripts/scrape_csw_articles.py` + `scripts/scrape_blogs.py`:
  removed `_drive_sync/` fallback paths from URL discovery.
- `scripts/migrate_prose_to_yaml.py` → archived to
  `scripts/_archive/` with a deprecation header (one-shot
  migration is complete; kept as historical record).

`.gitignore` retains defensive entries for all three paths in case
they ever resurface from a future Drive sync.

Remaining Drive duplicate: `wiki/wiki/`. Audit before deleting via
`scripts/audit_drive_duplicates.py`.

## [2026-05-26] lint | curation decisions: Argentina accepted, Drive cleanup plan

Two curation/cleanup calls:

- **Argentina accepted as an interest area** in `CLAUDE.md` →
  "Curation taste". The 79 Argentina_Reloaded producer pages stay
  in place. Bias toward biodynamic / terroir-driven /
  artisan-scale producers (Chacra, Colomé, Cara Sur, Canopus,
  Altos Las Hormigas style). Argentina_Reloaded curator's
  selection (Paz Levinson) is the seed.
- **Drive duplicates cleanup plan** in `_canonical_ids.md`. Git
  is canonical; Drive is a read-only mirror. Safe delete order:
  `_drive_sync/wine_wiki_v2/` → `wine_vault_fromdocuments/` →
  `wiki/wiki/` (run `scripts/audit_drive_duplicates.py` first to
  diff slug sets — won't delete if anything is unique to Drive).
- New gap surfaced: Catena Zapata is in cellar (2 bottles) but
  has no producer page.

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


## [2026-05-26] view | gap_csw_buy_candidates_2026_05: top CSW picks against cellar gaps

Filed `wiki/_views/gap_csw_buy_candidates_2026_05.md` answering "what are top candidates in my cellar gaps, who should I consider buying from CSW". Tier 1: Domaine Baudry, Gonon, Guion (Loire CF gap), Falkenstein, Schaefer, Busch (Mosel gap), Brovia, Esmonin, Peybonhomme, Texier. Tier 2: Rateau, Trapet, Weiser-Künstler, Chevalerie, Clos du Jaugueyron, Immich-Batterieberg, La Grolet. Tier 3 (CSW + alt retailer): Bernard Baudry, Chandon de Briailles, Produttori del Barbaresco, Tissot, Magnien, Marguet, Laherte. Cross-ref [[gap_csw_championed]].

## [2026-05-26] view | gap_csw_wk_overlay_2026_05: 138 CSW champions with William Kelley signal

Filed `wiki/_views/gap_csw_wk_overlay_2026_05.md`. Overlays WK Berserkers post count (from `raw/berserkers/William_Kelley/_post_index.csv`, 4,729 posts) onto the CSW-champion gap list. 40/138 (28%) have any WK signal. Heavy converge (§1, WK≥5): Duroché, Clos Rougeard, Domaine Levet, Desvignes, Cécile Tremblay, Larmandier-Bernier, Roilette, Allemand, Chandon de Briailles, Montille, Trapet, Willi Schaefer, Michel Mallard. Note: count is 138 not 143 (recompute 12d later; cellar grew or merges).

## [2026-05-26] view | wb_top100_csw_wk_matrix_2026_05: 22 CSW-covered producers from WB top 100 × Kelley signal

Filed `wiki/_views/wb_top100_csw_wk_matrix_2026_05.md`. Crosses the Wine Berserkers "Top 10 in your cellar" top 100 (1,089 posts, ~5,000 mentions) against CSW + WK signals. §1: 16 producers with any CSW article (sorted by WK desc). §2: 6 producers with wiki page but no CSW coverage (WK signal becomes deciding). §3: 78 unmapped WB top 100 names = vault gaps. Triple-converge picks: Allemand (natural Cornas, WK 8, WB#83), Schaefer (Mosel grower, WK 6, WB#15).

## [2026-05-29] ingest | Berserkers raw backlog pass: Kelley body re-pass v2 + top10_in_cellar compile

Ran two ingests against backlogged Berserkers data. (1) `reingest_kelley_bodies_v2.py --apply`: scanned all 4,727 William Kelley forum posts against 316 producer match patterns, found 705 dated body hits across 81 producers, wrote `berserkers_kelley_body` frontmatter block to all 81 pages. Headline movers (2024+ activity): Pierre-Yves Colin-Morey, Ramonet, Denis Bachelet, Léoville Barton, Haut-Bailly, Chevalier, Chandon de Briailles, Willi Schaefer. (2) `compile_wb_signals.py raw/berserkers/threads/top10_in_cellar.json --apply`: of 100 thread producers, 13 matched existing pages and got `community.berserkers.threads.top10_in_cellar` signals + `## Berserkers` body section. 87 unmatched — major names without wiki pages (Bedrock, Rhys, Ridge, Rivers-Marie, JJ Prum, Saxum, Williams Selyem, Dujac, Bouchard, Krug, Rousseau, Keller, Dauvissat, Gonon, Huet, Chevillon, Patricia Green, Lopez de Heredia, Pegau). Report: `build/wb_signals_report.md`. Followup: triage unmatched against `parse_wb_thread.py` PRODUCER_ALIASES (many are likely alias misses for existing pages — Rousseau→`armand_rousseau`, JJ Prum→`joh_jos_prum`, etc.).

## [2026-05-29] edit | CLAUDE.md curation taste: Napa flipped from cult tier to rugged/farming-driven

Curation taste line for Napa rewritten. Previously: "true cult tier (Harlan/Hundred Acre/Ridge Monte Bello/Bond/Colgin/SQN/Schrader), not generic $250 Cab." After Evan clarified taste 2026-05-29: rugged, farming-driven, terroir-distinct — reference set Dunn / Corison / La Jota / Dalla Valle / Ridge Monte Bello. Explicit skip on Harlan/Schrader/SQN/Colgin/Hundred Acre. Overarching cellar axis added: sense of place + tension. `/ask-cellar` should now default-exclude cult-tier Napa.

## [2026-05-29] view | Vinous + WA editorial clippings still empty (no Web Clipper saves)

Audit of `raw/clippings/vinous/` and `raw/clippings/wine_advocate/` found 0 articles, only README. Pipeline (`compile_clippings.py`) is wired and ready. To populate: install Obsidian Web Clipper, save articles per the schema in each folder's README. Until then, producer pages will not have `## Vinous Reviews` or `## Wine Advocate (Kelley)` sections, even for producers Vinous/WA cover deeply. Distinct from the William Kelley Berserkers ingest (community signal) — those 81 pages got updated above.

## [2026-06-06] view | kelley_instagram_producers: 112 high-conviction producers WK follows on IG

Filed `wiki/_views/kelley_instagram_producers.md`. Extracted wine producers from William Kelley's Instagram following list (two batches provided by Evan, 2026-06-06), separating wineries/domaines/châteaux/estates from importers, somms, critics, restaurants, hotels, and personal accounts. High-conviction subset = 112 producers across all regions, Champagne excluded per request. Heaviest cohort: Burgundy (31), USA (20), Italy (10), Bordeaux (9), Loire (8). Already in vault: Rapet Père et Fils, Roagna. A lower-conviction "verify" tier (~65 ambiguous handles) and the Champagne cohort (Gallimard, R.H. Coutier, Gonet-Médeville, Cose, Guenin, Pierre Gerbais, Dehours, de Bichery; Petit Clergeot + Pierre Péters already in vault) remain in chat only. Followup: cross-reference against `wiki/producers/` for gap analysis + apply curation taste filters before onboarding keepers.
