---
type: view
updated: 2026-07-17
scope: vault_architecture
---

# Data Integration & Quality Review (2026-07)

Follow-up to [[architecture_review_2026_06|the June architecture review]].
Question asked: *how do we improve the integration and quality of the data
and the answers the vault can provide?* Every claim below was verified
against the repo on 2026-07-17.

**Verdict:** the vault's discipline layer is genuinely healthy — `lint.py`
reports 0 issues, all three `--check` hooks pass, `wiki/log.md` has 68
valid entries, and the query→view→log loop is being used constantly (90+
saved views). The problems are one integrity failure (a documented fix
pass that never landed), a missing integration layer across the six signal
sources, and no freshness model. Ranked plan below.

## What's verifiably healthy

- `lint.py`: 0 issues; `build_wiki_index.py --check`,
  `build_wiki_log.py --check`, `build_views_index.py --check` all green.
- 368 producer pages, 294 cellar entries, 97 producer pages carrying
  `community.berserkers` frontmatter signals.
- Source layers with real data: CSW (1,623 articles), Raeders (3,174
  bottles + master CSV), DTE/Fass, Berserkers `top10_in_cellar`
  (full 2013–2026), Argentina Reloaded, Vinous Napa index, cellar export.

## Headline finding: the 2026-06-09 fix pass never landed

[[architecture_review_2026_06|The June review]]'s "Fixed in the
2026-06-09 pass" section and [[cellar_triage_2026_06|the cellar triage
record]]'s "Created (58)" table describe work that is **not in the repo
and never was** (`git log --all` is empty for every artifact):

- `scripts/link_cellar.py`, `fix_crossrefs.py`, `build_home.py`,
  `compile_cellar_triage.py` — none exist.
- `wiki/HOME.md` — doesn't exist; no human entry point.
- The 58 triage producer pages (`a_christmann`, `ceritas`, `corison`,
  `ar_pe_pe`, `chartogne_taillet`, `albert_boxler`, `dunn_vineyards`, …)
  — all missing.
- Country hubs (`France_Producers`, `Italy_Producers`, …) — missing.
- Cellar↔wiki linkage — **0 of 294** cellar files contain a single
  wikilink today; only ~15 producer pages have a `## Cellar` section.
- Broken wikilinks: **667 distinct targets, 1,314 occurrences** (the
  review claimed 764 → ~10). Top offenders unchanged: `CSW Article
  Archive` (140×), `Argentina_Producers` (79×), accent variants,
  country hubs.

This is the **second** phantom-work incident — same failure mode as the
Roscioli "152 pages uploaded to Drive" episode (see CLAUDE.md open
follow-ups). Work got done in some session/surface, the *documentation*
of it got committed, the work itself didn't. The good news: both decision
records survive, so re-landing is re-execution, not re-derivation.

## Ranked recommendations

### P0 — integrity

1. **Re-land the June-9 pass for real.** The triage table is a complete
   decision record: rebuild the 58 producer pages from it (cellar
   frontmatter + CSW/raw coverage), write `link_cellar.py` (slug-override
   table is documented in the review), emit country hubs from
   `build_rollups.py`, build `wiki/HOME.md`. Verify each artifact exists
   in `git log` before logging it done.
2. **Make lint catch phantom claims.** Extend `lint.py`: (a) validate
   *every* `[[wikilink]]` target across wiki + `_views` + `cellar`
   against actual file stems (today it only checks producer-slug-shaped
   links in producer bodies — hence 1,314 misses at "0 issues");
   (b) flag any `scripts/*.py` path referenced in `log.md`/`_views`
   that doesn't exist. This turns documentation-of-work into a checkable
   assertion.
3. **Session exit rule.** Add to CLAUDE.md: a log entry may only be
   written after `git push` succeeds, and must name the files it created
   so lint rule (b) can audit it. Cheap insurance against incident #3.

### P1 — integration & freshness (biggest answer-quality lever)

4. **Unified signal layer.** Signals live in six disconnected frontmatter
   namespaces (`retailers.*`, `community.berserkers.*`, `roscioli.*`,
   cellar files, clippings, taste filters). Write `build_signals.py` →
   `build/producer_signals.json` + a generated `## Signals` block or
   HOME table: per producer, one row joining *owned bottles × WB
   momentum × Kelley mentions × critic coverage × retailer
   availability/price × taste-filter fit*. This is the join every gap
   analysis and `/ask-cellar` answer currently re-derives by hand, and
   it makes conviction rankable instead of vibes.
5. **Freshness model.** Nothing in the vault knows how old it is: 0
   producer pages carry `updated:`, retailer price blocks are undated,
   the Raeders snapshot is from **2026-04-25** (12 weeks old) yet ~20
   "at Raeders" views and the top-100 are built on it; `My Cellar.csv`
   last refreshed 2026-06-17. Add `updated:`/`as_of:` stamps (scripts
   already touch these files), a `snapshot_date` in each view's
   frontmatter naming its source vintage, and a staleness table on HOME
   ("Raeders: 83 days — re-scrape"). Re-export CellarTracker monthly,
   and use the *purchase* export to finally get purchase dates.
6. **Views lifecycle.** 90+ views with no supersession model — five
   generations of 261W auction screens, v1/v2 picks — all equally
   "current" to a reader or an LLM shortlisting from the catalog. Add
   `status: active | superseded_by: <slug> | archived` to view
   frontmatter, group `_views/_index.md` by status, and let lint flag
   dated views whose underlying snapshot has been refreshed.

### P2 — hygiene & filling wired-but-empty pipes

7. **Line-ending + heading canon lint.** 163 producer pages are CRLF —
   it's not cosmetic: `\r` gets captured inside wikilink targets
   (`[[roagna\r]]` ×7 and friends) and forks section-heading matching
   (`## Raeder's` exists in both endings; `## Raeders Notes` is a
   third variant vs. the schema's canon). One `--fix` pass to normalize
   LF + one canonical heading list derived from `_SCHEMA.md`, then lint
   both forever.
8. **Feed the empty pipelines, one each.** Wired-but-zero sources:
   Vinous/WA clippings (0 files), Vinolist NYC (0 restaurants), LPV
   (0 threads), Berserkers (1 of many candidate threads;
   `hall_of_fame` already catalogued). Don't build more pipeline —
   ingest one unit through each: one Kelley clipping, one grower-
   Champagne restaurant list via the tested manual-paste path, one LPV
   N. Rhône thread pasted into `raw/lpv/threads/`, one more WB thread.
   Each first unit proves the compile path and starts the flywheel.
9. **New source: 261W realized prices.** The weekly wheelhouse screens
   are now a core vault use, but nothing captures *hammer results*.
   A tiny `raw/auctions/results/` CSV per sale (lot, wine, estimate,
   realized) would calibrate every future value call and build a
   personal price database for exactly the aged-classic niche Evan buys.

### P3 — code robustness

10. **`scripts/lib/` extraction + tests.** Still open from June:
    frontmatter parsing is copy-pasted across ~24 scripts, slug
    normalization reimplemented 6+ ways (the root cause of cellar slug
    drift), zero tests. Extract `parse_frontmatter()` /
    `normalize_slug()`, add a pytest idempotency suite (run every
    `build_*` twice → no diff), and give `build_rollups.py` a
    `--check` wired into CI alongside the existing three.
11. **Drink-window curation pass.** Windows come straight from
    CellarTracker community data (e.g. Pichon Comtesse 1996 →
    2032–2095). A one-shot LLM pass over the ~50 most valuable bottles,
    cross-checked against Kelley/Vinous where raw coverage exists,
    would make `drink_window_due` trustworthy for actual pull decisions.

## Suggested order

(1) and (2) first — they're the trust layer everything else reports
through. Then (4)+(5) together, since the signal join is only as good as
its freshness stamps. (7) is a 30-minute `--fix`. The rest as sessions
allow.
