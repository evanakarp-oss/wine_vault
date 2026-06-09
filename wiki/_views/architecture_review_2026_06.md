---
type: view
updated: 2026-06-09
scope: vault_architecture
---

# Vault Architecture Review (2026-06)

Full-vault audit: content quality, pipeline/code layer, navigation &
linking. Verdict: foundations excellent (schema enforced, lint at zero,
idempotent generation, CI-gated index), weaknesses were cellar↔wiki
disconnection, broken-link debt, missing freshness metadata, and no human
entry point. The companion fix pass (same date, see [[log|log]]) closed the
navigation cluster; the rest are ranked follow-ups below.

## Headline findings (verified by hand)

- **Cellar↔wiki disconnect** — 173 of 187 cellar producers (93%) had no
  wiki page; **zero** of 294 cellar files contained a wikilink. 13 of
  those were slug mismatches (CellarTracker names slugify differently
  than wiki slugs, e.g. `anne_et_jean_francois_ganevat` vs
  `jean_francois_ganevat`); 160 are genuinely missing pages — including
  **Dunn and Corison**, the Napa reference set in CLAUDE.md's taste filter.
- **764 broken wikilink occurrences** across 325 targets. Systematic
  causes: `[[CSW Article Archive]]` never existed (137×), country-level
  rollups never existed (`Argentina_Producers` 79×, `Italy_Producers` 21×,
  `Germany_Producers` 21×, `France_Producers` 5×), accent-variant targets
  (`Rhône_Producers` vs `Rhone_Producers`, 20×), generators wikilinking
  producers without pages, long tail of sub-region/appellation links.
- **No freshness metadata** — producer pages carry no `updated:`;
  retailer prices in frontmatter are undated; `purchase_date` is absent
  from all 294 cellar entries (the CellarTracker list export has no
  purchase-date column, so it cannot be backfilled from `My Cellar.csv`).
- **77% of producer pages are seeded stubs** ("Not yet covered…"), with
  stub status living in prose instead of queryable frontmatter.
- **Pipeline duplication** — frontmatter parsing copy-pasted into ~24
  scripts under 3 different names; only `build_wiki_index.py` uses real
  YAML parsing; slug normalization reimplemented 6+ times (plausibly the
  root cause of the cellar slug drift). Zero test coverage.
- **CI drift gap** — CI gates `index.md` and `log.md`, but rollups and
  views have no `--check`, so they drift silently between runs.
- **No human entry point** — `_views/` analyses had zero inbound links
  (`_views` was in the index generator's skip list); two `.obsidian/`
  dirs made the vault root ambiguous; `index.md` is LLM-optimized only.
- **Misc data finds** — `arnot-roberts` was misfiled as France/Jura
  (it's Healdsburg, California); `_TAXONOMY.md` had no United States
  region section, so US region values were never validated.

## Fixed in the 2026-06-09 pass

- `scripts/link_cellar.py` (new): curated slug-override table (13
  verified mappings, 30 files re-slugged), cellar bodies wikilink their
  producer (51 entries), producer pages get `## Cellar` sections with
  per-bottle wikilinks (27 pages). `ingest_cellar.py` applies the same
  overrides on re-ingest.
- `scripts/fix_crossrefs.py` (new): CSW-archive links re-targeted to
  [[Chambers_Street_Wines|Chambers Street Wines]], accent-variant targets
  repaired, remaining location links unwrapped to plain text (policy:
  locations stay plain text until a page exists).
- `build_rollups.py` now emits country hubs (France_Producers,
  Italy_Producers, …) — region directories that the Cross-references
  sections already pointed at.
- `build_views.py` and `build_wiki_index.py` only wikilink producers
  that have pages; drink-window rows now link the cellar bottle file.
- `wiki/HOME.md` (new, via `scripts/build_home.py --check`-able):
  urgency counts, saved-analyses table, browse-by-country/region,
  cellar stats. `_views/` is now indexed in [[index|the wiki index]].
- `lint.py` validates slug-shaped wikilinks against ALL wiki+cellar
  stems (was: producer pages only).
- Repairs: `arnot-roberts` → United States/California; US regions added
  to taxonomy; nested `wiki/.obsidian/` removed (vault root = repo root).
- Broken-link occurrences: **764 → ~10** (remainder are intentional
  gap-flags in hand-written views and a schema example).

## Ranked follow-ups

1. **Cellar producer triage (160 missing pages)** — run Evan's taste
   filter over `build/cellar_ingest_report.md`'s missing list. Create
   pages for keepers (Dunn, Corison first), record "no page needed" for
   generic-tier (the Catena decision, generalized).
2. **Freshness metadata** — `updated:` on producer pages (scripts
   already touch them), `as_of:` dates on retailer price blocks. For
   purchase dates, CellarTracker's *purchase* export (not the list
   export) carries them.
3. **`status: stub|seeded|curated` frontmatter** on producer pages so
   views and Q&A can filter authoritative pages from placeholders.
4. **`scripts/lib/` extraction** — shared `parse_frontmatter()` /
   `normalize_slug()`; pytest idempotency suite (run twice = no diff);
   `--check` mode for `build_rollups.py` + CI wiring.
5. **Obsidian Bases live view** — cellar frontmatter is already
   query-ready; a Base on HOME filtered by drink window would make
   urgency live instead of build-time.
6. **Lateral producer navigation** — auto-generated "Neighbors" block
   (same sub_region / same importer) on producer pages.
7. **Importer/retailer prose** — 196 pages are tables-only; add curated
   one-paragraph "why this importer matters" above the auto markers.
