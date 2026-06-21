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

## [2026-06-06] view | Kelley's Burgundy value map (zip-code critique → 6 value moves)

Filed `wiki/_views/kelley_burgundy_value_2026_06.md` from the William Kelley Berserkers scrape (`raw/berserkers/William_Kelley/`). Distills his Burgundy value commentary into a repeatable buy-side framework: the NSG/Vosne "priced by zip code" critique (glamour 1ers like Vosne Suchots) and its inverse — six value moves (Chassagne Rouge; Savigny vs Volnay; buy-down-within-a-grower's-range; village wine from a Grand-Cru house e.g. Roty Marsannay; quiet classicists like Voillot; cult producers' value labels e.g. Verget). Surfaced producer-page gaps (J-C Bachelet, Paul Pillot, Mugneret-Gibourg, Felettig, Verget, Thierry Glantenay) and two dedupe candidates for lint (roty.md vs domaine_joseph_roty.md; jean_marc_et_thomas_bouley.md vs thomas_et_jean_marc_bouley.md).

## [2026-06-06] view | Raeders Burgundy value picks — top 15 under $400

Filed `wiki/_views/raeders_burgundy_value_picks_2026_06.md`. Screened the 128 Burgundy bottles under $400 in `raw/raeders/master_2026-04-25.csv` through the Kelley value framework (`kelley_burgundy_value_2026_06.md`) + Evan's curation filters. No critic scores in the scrape (score_wa=0 throughout) — judgment-based. Top pick A. & P. de Villaine Bouzeron Aligoté; standout price/quality Pierre Morey Bourgogne Aligoté ($39). Skipped zip-code trophies (Méo Vosne Chaumes, Dujac Chambolle village) and négoce-generic (Jadot/Latour/Drouhin entry).

## [2026-06-06] view | Raeders Burgundy picks v2 — re-grounded in Kelley's verbatim WB comments

Revised `wiki/_views/raeders_burgundy_value_picks_2026_06.md` to v2. Mined the William Kelley Berserkers corpus for direct quotes on the ~27 producers in the Raeders under-$400 Burgundy set; re-ranked strictly by what he actually wrote (personal buys > explicit value calls > general esteem), each pick cited to a post file. New #1 is Mugnier Clos de la Maréchale ("amazing that it isn't more expensive"). Demoted v1 picks with no WB evidence: Méo-Camuzet, Yann Durieux, Lucien Boillot, Edmond Cornu, Robert-Denogent. Noted J-C Bachelet / Paul Pillot as the names he'd want that Raeders doesn't stock under $400.

## [2026-06-09] view | WK × DTE Burgundy portfolio eval

Filed `wiki/_views/wk_dte_burgundy_2026_06.md`. Cross-referenced all 35 DTE
(Down to Earth / Panzer) Burgundy producers against the William Kelley
Berserkers corpus (4,727 posts). 22/35 appear; tiered by his verbatim
enthusiasm. Loves: Lorenzon, Bouley, Arnoux-Lachaux (price-disqualified by
his own zip-code logic). Strong/rising: Charles Audoin, Glantenay, Henri
Magnien, Javillier, Berthaut. Only pan: Michel Noëllat. Top action item:
Charles Audoin — WK's Marsannay benchmark, 19 DTE cuvées $45–65, zero
bottles owned. Flagged: `loersch.md` mis-tagged Burgundy (is Mosel); four
duplicate producer-page pairs (Bouley ×2, Cheurlin/G. Noëllat, Roty ×2,
Berthaut ×2).

## [2026-06-10] view | Auction catalog 261W top picks (1,965 lots screened)

Filed `wiki/_views/auction_261w_top_picks_2026_06.md` from a 1,965-lot auction
catalog (Delaware + Hong Kong; landed at `raw/auctions/catalog_261W_2026-06.xlsx`).
Screened all lots against the CLAUDE.md taste filters. Catalog is CA-heavy (728
lots, mostly skipped cult tier) but hides an aged restrained-Napa seam squarely
on the reference set: Dunn HM verticals ('87/'92/'04/'08), La Jota 1992 HM at
$52–70/btl, Dalla Valle 1993 at $50–71/btl, Togni '92, Montelena Estate
1984–1997 vertical. Tier-1 also: 9x 1993 Huet Cuvée Constance ($72–94/btl),
Prévost Les Béguines, 6x 2008 Clos des Goisses, 2002 Raffault Picasses
($40–53/btl), Roagna Pira '19 (97 VM, $110–140), 2020 Prüm WS Auslese 6-packs
($33–47/btl), Clos Rougeard '11, Allemand Reynard '04, Chevillon Chaignots '10,
F. Rinaldi Cannubi 6-packs ($47–58/btl, HK), Sunier Morgon cases ($15–20/btl),
Boisson Aligoté cases. Gap-fill note: vault has pages but zero bottles for
Clos Rougeard, Allemand, G. Conterno, Levet, Sunier, Marguet, Péters, Schaefer,
Boisson.

## [2026-06-10] view | 261W addendum — Bordeaux deep cuts + natural-farming sweep

Appended addendum to `wiki/_views/auction_261w_top_picks_2026_06.md` answering
two follow-ups. Sauternes is the catalog's best $/quality: 12x 2011 Doisy-Daëne
at $22–29/btl (95pts), 12x 2009 Rieussec at $29–42/btl (98pts), 1986 Coutet
Cuvée Madame. Bordeaux deep cuts: 1985 Laville Haut-Brion, 2009 Domaine de
Chevalier ($73–100/btl), organic-run 2016 La Lagune ($37–50/btl), Poujeaux
12-packs ($20–27/btl); skipped the 9-lot Le Bon Pasteur wall. Natural sweep:
2010 Philippe Pacalet NSG ($90–120), 2006 Comte Armand Épeneaux ($75–100/btl),
Chandon de Briailles Corton, Naudin-Ferrand low-SO2 cases, Didon Bourgogne
cases ($12.5–17/btl), 2007 Vieille Julienne CdP ($30–40/btl), Le Boncie
Chiesamonti case, 11x 2012 Hirsch Bohan-Dillon ($16–22/btl), 1998 Musar.

## [2026-06-10] view | 261W natural sweep part 2 — biodynamic certified + icons

Extended the natural section of `wiki/_views/auction_261w_top_picks_2026_06.md`.
Headline: 4x 2002 Rossignol-Trapet Chambertin at $175–225/btl (aged biodynamic
grand cru — best natural value in the sale). Also: 6x 2016 Stéphane Bernaudeau
Les Ongles ($158–200/btl), 2011 Comte Lafon Monthélie at $50–70 (bio, mature,
91pts), 1993 Araujo Eisele at $120–160/btl, 6x 2015 Le Ragnaie Brunello at
$37–50/btl ×2 lots, Buisson-Charles Bourgogne Rouge cases at $20–27/btl,
1990 Bürklin-Wolf Eiswein, Dominus 1990–94 run, 2001 Turley Hayne (97pts),
1959 Banyuls 6-pack at $75–100/btl. No-estimate lowball targets: Galeyrand,
Volpaia Gran Selezione, Corte Pavone. Priced-out: DRC, Guilbert-Gillet, Bizot.

## [2026-06-10] view | Zachys Palm Beach collection top picks (1,742 lots screened)

Filed `wiki/_views/zachys_palm_beach_top_picks_2026_06.md` from the Zachys
zCollections "Exceptional Palm Beach Collection" listing (NY, June 9–22;
landed at `raw/auctions/zachys_zcollections_palm_beach_2026-06.xls`). Bulk is
cult California (Schrader 116 lots, Marcassin 29, Bond 23 — skipped), but the
remainder is strong: 6x 2004 Guido Porro Santa Caterina at $20–30/btl, 9x 2012
Pataille Clos du Roy at $33–51/btl, aged Produttori riservas, 8-lot Bartolo
Mascarello ladder, 12x 2019 Ramonet Chassagne Rouge at $50–75/btl, 6x 1990
Pégau, 2007 Gonon VV, 2003 Soldera Riserva, 12x 1999 Sammarco at $54–79/btl,
1989 GPL/Rauzan-Ségla at $73–113/btl, 12x 2005 Dom. de Chevalier at $50–75/btl,
1988 Ridge Monte Bello magnum, 12x 2010 Eyrie at $20–30/btl, 2001 Királyudvar
Esszencia. Condition-aware (older cellar — shoulder fills on pre-1990 lots).
Cross-catalog overlaps with 261W flagged (Ledru, Diamond Creek, Dunn 2008,
Clos Rougeard).

## [2026-06-11] view | Maison Pierre Brisset non-English source research

Filed `wiki/_views/maison_pierre_brisset_non_english_sources_2026_06.md` —
French + Japanese record on the producer behind 7 owned cuvée-vintages (all
Fass buys, no producer page yet). Key finds: founded 2014 at Château de
Bligny after selling VoyagerMoinsCher.com to Rakuten (2010, per Firadis JP);
single 0.5 ha estate parcel (Chassagne 1er Abbaye de Morgeot, bought 2013),
everything else purchased fruit; vinifies at the "Wine Studio" custom-crush
cellar shared with Dominique Lafon + Pierre Meurgey; whites barrel-fermented,
reds steel-then-barrique, unfiltered; cuvée names decoded (Gabrius = old
Gevrey, Cassaneas = old Chassagne, ~900 btls). French critics validate: RVF
18/20 Chassagne 1er (June 2017), Hachette 2 stars (2024), B&D, Gault&Millau.
Caveat for the taste filter: no bio/HVE claim anywhere — Lafon-adjacent
custom-crush négociant, not a biodynamic grower. Follow-up: promote into
`wiki/producers/maison_pierre_brisset.md`.

## [2026-06-11] create | Maison Pierre Brisset producer page

Created `wiki/producers/maison_pierre_brisset.md` from the non-English
source research view (2026-06-11) + the four Fass articles in `raw/fass/` —
closes the largest cellar-without-page gap (16 bottles across 7
cuvée-vintages, all Fass buys). Page carries the founding story (2014,
Château de Bligny, ex-VoyagerMoinsCher/Rakuten), the 0.5 ha Morgeot estate
parcel, the Wine Studio custom-crush setup with Lafon/Meurgey, cellar
regime, cuvée name decoder, and the French critic record (RVF 18/20,
Hachette 2 stars, B&D, Gault&Millau). Evan's call: organic/bio status
irrelevant for this producer type — placed on the terroir-transparency
axis. Rollups regenerated (Burgundy_Producers + FASS_Selections now list
him); index rebuilt; lint 0.

## [2026-06-16] view | WK × Down to Earth top picks (value-first)

Cross-portfolio shortlist of William Kelley's Down to Earth (Panzer)
endorsements, framed value-first: a ~11-bottle under-$80 core plus four
trophy picks. Broadens the earlier Burgundy-only eval to Champagne
(Larmandier-Bernier, Lassaigne + Petit Clergeot, Laherte) and the Rhône
(Marc Sorrel white Hermitage), each with verbatim signal from the
`raw/berserkers/William_Kelley/` forum corpus and DTE price ranges from
frontmatter. Caveats logged for Marguet (volatile acidity), Agrapart
(no corpus enthusiasm), Arnoux-Lachaux (zip-code pricing), Michel Noëllat
(his one DTE pan). Filed at `wiki/_views/wk_dte_picks_2026_06.md`; index
rebuilt. Source layer is still forum-only — Wine Advocate clippings dir
empty, so signal is directional not scored.

## [2026-06-16] consolidate | Pull orphaned _views pages from session branches into main

Swept all per-session `claude/*` branches for `wiki/_views/` pages that
never reached `main` and consolidated 40 view pages (+1 SVG map) onto the
single read surface. Deduped overlaps per Evan's call: dropped
`rugged_mountain_cabernet_2026_06.md` (twin of the bedrock-style mountain-cab
gap view) and kept only `csw_article_archive.md` over the two older
2012-specific CSW pages (`csw_2012_and_earlier.md`,
`csw_articles_2012_and_earlier.md`). Covers Burgundy value/Vosne adjacency,
California cab canon + gaps, Raeders × importer xrefs, FASS picks, auction +
retail-offer screens, CSW article archive, and vault-meta reviews. Alternate
drafts of pages already in main (summer-white v2/v3, four gap/matrix pages
from the vault-architecture branch) were left in their branches, not merged.

Discovered `wiki/_views/` had no catalog — `build_wiki_index.py` skips the
directory by design — so views were uncataloged anywhere. Added
`scripts/build_views_index.py` + generated `wiki/_views/_index.md` (69 views)
as the single read surface, and corrected the CLAUDE.md note that wrongly
claimed views were listed in `wiki/index.md`.


## [2026-06-17] view | Auction 261W Week 25 top picks (refreshed catalog)

Evan uploaded the Week-25 Acker 261W catalog (`raw/auctions/Catalog_261W_25.xlsx`,
1,977 rows / 1,505 distinct lots) and asked for the most interesting lots. Diffed
against the Week-24 file: lot numbers are stable (same number = same wine), but the
catalog turned over ~half — 769 lots new, 727 dropped, 736 carried over. Most Week-24
hero lots already sold (Dunn '92/'87, the 7-bottle Dalla Valle '93, Prévost Les
Béguines, Clos Rougeard, Allemand, Rossignol-Trapet Chambertin, Vatan, '67 d'Yquem).

Fresh taste screen filed at `wiki/_views/auction_261w_week25_top_picks_2026_06.md`.
Headlines: Ridge Monte Bello 2013 (reference-set Cali Cab, absent from the prior
sale); a 2007 German Riesling block (Dönnhoff Hermannshöhle, J.J. Prüm Wehlener at
$18–67/btl); an aged biodynamic Beaucastel CdP vertical (1981–1990); Chandon de
Briailles 2005 Corton grand-cru cases ($75–117/btl); Dominus aged vertical; Aldo
Conterno '97 + Oddero Vigna Rionda trad Barolo; Quintarelli Primofiore '05 + Fontodi
Flaccianello; deep aged drink-now Bordeaux; grower Champagne (Prévost, Savart, Selosse).
Per a follow-up, screened for Friuli/Collio/Carso and orange wine catalog-wide — zero
hits; the Italian book is Piedmont + Tuscany + Veneto only. Views index rebuilt (70).
Committed to main per Evan's standing branch rule (CLAUDE.md, 2026-06-16).

## [2026-06-17] view | Auction 261W Week 25 — obscure/sleeper addendum

Follow-up to the Week-25 auction view: Evan asked for more obscure regions /
sleepers ("the German flag was good"). Added an "Obscure regions & sleepers"
section reading the small region buckets in full (the producer-whitelist screen
skips sleepers by design). Highlights: J.J. Christoffel + Georg Breuer + Molitor
(dry/cult-grower German), Trimbach Clos Ste Hune + Frédéric Émile (aged Alsace),
Graham's 1985 Port by the case + 1909/1940/43 Sandeman (fortified), Contino '95
+ Alvear Montilla solera + Flor de Pingus '96 (aged/biodynamic Spain), Cayuse +
Gramercy (biodynamic WA Syrah), Domaine Drouhin/Beaux Frères aged Oregon Pinot.
Flagged the "Austria" bucket as a catalog mislabel (BK Wines = Australia), and
the obscure-hunter gaps (no Jura/Gredos/real-Austria/Friuli/Madeira). Same view
file, committed to main.

## [2026-06-17] view | R Squared Selections inventory top picks (2026-06-17)

Evan uploaded R Squared's 2026-06-17 inventory (293 wines, 61 new) and asked to
"check r squared" — landing on the heels of his obscure-regions question. R Squared
is a natural/terroir importer whose book is squarely his taste: deep Jura (25),
Savoie, Friuli, traditional Piemonte, grower Champagne, Cornas, grower-Aligoté white
Burgundy. Screened the full list against the curation filters and cross-checked the
cellar (already owns Ganevat Madelon, Cogno x3, Foillard '18) + 22 existing producer
pages. Filed at wiki/_views/r_squared_picks_2026_06_17.md, leading with the obscure
regions: Ganevat/Cavarodes/Marnes Blanches/Tissot (Jura), Belluard (Savoie), Miani
(Friuli). Other highlights: Bartolo Mascarello + Giuseppe Rinaldi + Produttori +
Elio Sandri (trad Piedmont), Robert Michel 'La Geynale' library Cornas, Jerome
Prevost Les Beguines, grower Aligote wall, Keller Abtserde GG + Mosel value. Landed
raw at raw/retailers/, rebuilt the views index. Committed to main.

## [2026-06-17] view | Auction 261W Week 25 California Cabernet screen

Evan asked about the Cali Cabs in the Acker Week-25 catalog. Screened all 601
California Cab/Meritage + Red lots against the definitive Cabernet target list
and the Napa filter (rugged/site-transparent, not cult-hedonist). Filed at
wiki/_views/auction_261w_week25_cab_screen_2026_06.md as a companion refresh of
the now-stale Week-24 cab screen. Headline: Ridge Monte Bello 2013 (4x,
$225-300/btl, 97pt) — the #1 unowned Cab on the target list, absent from Week 24
— is now in the sale. Reference-set also covers Dalla Valle '93 case ($62-75/btl)
+ '92 + Maya '98, La Jota '92 ($52-70/btl), Dunn '08. Restrained adjacents: a deep
Dominus 1989-1995 vertical, Montelena Estate 1980-1993, Forman '87, Mayacamas, and
the sleeper Robert Mondavi Reserve 1987 (97pt, pre-cult To Kalon). 66 cult lots
screened out (14 Opus One, Silver Oak, Screaming Eagle, Harlan, Bond). Coverage is
narrower than Week 24 (no Corison/Togni/Spottswoode/Diamond Creek/MacDonald).
Views index rebuilt. Committed to main.

## [2026-06-17] view | Vintage guide by region (cooler-classic lens)

Evan asked to add vintage context to the vault — best vintages for regions like
Burgundy and Napa — with the explicit palate steer that he prefers less-ripe over
more-ripe (Tuscany named directly), citing the 2008 Mugnier Clos de la Maréchale
as "a bit too big." Researched cool-vs-warm vintage character 2010–2023 across
the cellar's regions (Jancis Robinson, Wine Spectator, Wine Scholar Guild, K&L,
Mosel Fine Wines, Decanter/Finest Bubble, Wine Cellar Insider) and filed a single
keeper view at wiki/_views/vintage_guide.md. It rates vintages by a ripeness lens
(❄️ cool/classic = chase · ⚖️ balanced · ☀️ warm/ripe = caution · ⚠️ hot/atypical
= skip) rather than raw quality, covering Burgundy red+white, Tuscany, Napa Cab,
Piedmont, Bordeaux, Champagne, Germany, N. Rhône, Loire reds, and Mendoza, plus a
per-region cheat sheet. Two framing principles: site structure compounds with
vintage ripeness (the Maréchale read big because the NSG monopole site is broad,
not because 2008 was a warm year — it wasn't), and in Napa/Mendoza producer beats
vintage. Reframed the 2008 Maréchale note honestly on that basis. Views index
rebuilt (73). Committed to main.

## [2026-06-18] ingest | Di Costanzo producer page (Coombsville + Moon Mtn restrained Cab)

Promoted Di Costanzo from a checklist lead to a full producer page
(`wiki/producers/di_costanzo.md`) at Evan's direction ("def want de costanzo on
our top producers"). Massimo Di Costanzo (ex-Screaming Eagle assistant winemaker
under Andy Erickson) founded the label with the 2010 vintage and inverted that
house style toward finesse: reasonable brix, all-natural acidity, organic/native
yeast, low SO2, little-to-no fining/filtration. Single-vineyard Cabs from Farella
(Coombsville's oldest Cab vines, late-1970s), Caldwell (a block formerly farmed by
Randy Dunn), and dry/organically-farmed Montecillo on Moon Mountain (the same
Sonoma site that anchors the restrained-Cab canon, also sourced by Arnot-Roberts).
Frontmatter set country=United States, region=California, sub_region=Coombsville /
Moon Mountain, farming=[organic, sustainable]. Added to the Core shortlist and
ticked the checklist (✅) in `wiki/_views/restrained_napa_sonoma_cab_canon_2026_06.md`;
rebuilt rollups (California rollup now carries it), `wiki/index.md`, and the views
index. Lint 0. Vinous/WA critic sections left as PENDING stubs — no clipping has
been ingested (the Vinous Napa list Evan recalls giving was never committed to the
repo; `raw/clippings/vinous/` holds only its README).

## [2026-06-18] ingest | Vinous Napa producer index — captured + triaged (~230 names)

Evan supplied the Vinous Napa producer list he'd been asking about (the one never
committed in prior sessions). Captured verbatim at
`raw/vinous/napa_producer_index_2026-06.md` (provenance only — a bare list, not Web
Clipper article output, so it does not feed `compile_clippings.py`). Triaged all ~230
names against the post-2026-05-29 taste filter and filed the result as a new section
("Vinous Napa producer index — full triage") in
`wiki/_views/restrained_napa_sonoma_cab_canon_2026_06.md`. New verified fits surfaced:
Hyde de Villaine (HdV) and Detert Family (both page candidates); a ◐ worth-a-look tier
(Keenan, Barnett, Burgess, O'Shaughnessy, Outpost, Ink Grade, Seavey, Selene, Snowden,
Clos du Val, Chimney Rock, Groth, Fisher, Pride, Hudson, El Molino, Haynes, Bella Oaks,
Arietta, Massican, VHR); cult/opulent and commercial/modern tiers skip-listed; the
genuine unknowns bucketed as "no signal — modern micro/garagiste, skip unless known."
Confirmed Di Costanzo appears twice on the list and already has a page (created earlier
today). Rebuilt wiki/index.md + views index; lint 0.

## [2026-06-18] ingest | HdV, Detert, VHR pages + "no signal" 60 researched off-vault

At Evan's direction ("HDV and detert u can / VHR great"), promoted three leads from
the Vinous Napa triage to full producer pages: `wiki/producers/hyde_de_villaine.md`
(Carneros; Larry Hyde × Aubert de Villaine of DRC; Burgundian restraint), 
`wiki/producers/detert_family_vineyards.md` (old-vine Cabernet Franc inside To Kalon,
Oakville; family since 1954), and `wiki/producers/vine_hill_ranch.md` (VHR — historic
southern-Oakville bench grower between Harlan & Dominus; estate Cab since 2008 by
Françoise Peschon). Marked all three ✅ in the canon view.

Separately, researched all ~60 "no signal" names from the Vinous list off-vault (5
parallel web-research agents) and re-bucketed them in the canon view's Vinous-triage
section. Six new fits surfaced — Retro Cellars (Mike Dunn, son of Randy Dunn, made at
Dunn), Tobias (Toby Forman, son of Ric Forman), Almacerro (La Jota ground, Peschon),
Fe Wines (CCOF-organic Spring Mtn), T. Berkley (old-vine Cab Franc/Chenin), Kizor
(Dunn's winemaker; off-Cab) — plus a worth-a-look tier and confirmed cult/négoce skips.
Two remain unknown (Kohue, Unity). Rebuilt California rollup, wiki/index.md, views
index; lint 0.

## [2026-06-18] view | Price check on the Vinous Napa fits + worth-a-look (~32 names)

Researched current US retail prices off-vault (4 parallel agents) for the nine
fits/pages plus the ~23-name worth-a-look tier, and filed a "Price check (2026-06)"
section (two tables) in `wiki/_views/restrained_napa_sonoma_cab_canon_2026_06.md`.
Also appended pricing notes to the hyde_de_villaine, detert_family_vineyards and
vine_hill_ranch pages. Value standouts: T. Berkley (~$32), Kizor (~$45–48), Rossi
Wallace (~$30–50), Crosby Roamann (~$74+), atLarge (~$85), Baker & Hamilton (~$90,
VHR's 2nd label). Lineage names reachable: Retro Cellars ~$50, Tobias ~$56–150.
Flagship allocation Cabs (VHR $325–345, Fe ~$339, NEOTEMPO ~$250, 001 ~$225+,
Bergman ~$295, Almacerro ~$225) run high. Two corrections logged: Retro Cellars makes
**no varietal Cabernet** (Petite Sirah + one Cab-blend), and "Remedium" is a vineyard
bottled by **Pott Wine as 'Stacked'." Prices indicative (many sources 403); lint 0.

## [2026-06-18] view | Blachon Margiriat — Fass verdict + French sources
`/ask-cellar`: does Fass like the Sébastien Blachon Saint-Joseph "Margiriat",
and what do French-language sources say? Fass (Lyle Fass) calls "Blachon Margariat"
one of his **top two Saint-Josephs of the vintage** (alongside Pierres Sèches
Revirand) and lists the white "Islaline" among his elite St-Jo blancs — strong
endorsement. French press is thin on *scores*: no Guide Hachette / RVF rating for
the Sébastien Blachon Margiriat itself; substantive French material is the
producer's own dégustation note (caveblachon.fr) — 100% Syrah, granite coteaux of
Saint-Jean-de-Muzols, vines 15–90 yrs, 100% grappe entière, 12 mo barrel; nose of
violette/litchi/eucalyptus, bouche suave. Flagged the name collision: **Cave
Sébastien Blachon** (Margiriat, St-Jean-de-Muzols) ≠ **Domaine Blachon** (Hommage
Roger, Mauves, Guide Hachette 1★). Blachon remains a Tier 1 onboard candidate (no
producer page / cellar bottle yet). Filed `wiki/_views/blachon_margiriat_fass_french_2026_06.md`.

## [2026-06-18] view | Blachon Margiriat — added LPV Rhône forum read
Follow-up to the Blachon Margiriat view: added a La Passion du Vin (LPV) section.
LPV covers Sébastien Blachon but more soberly than Fass — 2018 flagged as a
"découverte / jeune producteur à suivre" (texture fine, nez violette), Alban 2020
positively noted, and his 2018 scored ~15,5/20 mid-pack in a blind 24-bottle
Saint-Joseph horizontal (below the LPV reference tier: Guigal Vignes de l'Hospice
~16,2, Coursodon La Sensonne ~16,08, Delas Sainte-Épine ~16,07). The Margiriat
lieu-dit cuvée is not individually reviewed on LPV; the "Domaine Blachon" thread
also conflates the Mauves Hommage estate with Sébastien's cave. LPV pages 403 the
fetcher — content reconstructed from search snippets.

## [2026-06-18] view | LPV signal map — Evan's French regions
Browsed LPV (La Passion du Vin) to locate where forum signal is exceptionally
strong, mapped to Evan's French regions of interest (N. Rhône, Burgundy, Bordeaux,
Champagne, Loire, Beaujolais, Jura/Savoie). Five signal types ranked: per-producer
"fil" megathreads > organized blind horizontals/verticals (/degustations-eclectiques)
> curated best-of polls > regional circles (cercles régionaux) > annual-event coverage
(Grands Jours de Bourgogne etc.). Per-region section URLs + strongest anchor threads
captured (e.g. Rhône "Top 10 domaines les plus lus", Clape/Vincent Paris/Jamet fils;
Bordeaux millésime horizontals 1986/1989; Champagne "vignerons préférés" poll +
Lassaigne/Guiborat fils; Beaujolais by-millésime horizontals; Jura Château-Chalon /
Vin Jaune verticals). Includes a how-to-mine guide and a Berserkers-style ingest
sketch (blocker: LPV 403s the fetcher — needs a real scraper). Search-surfaced;
contents not fully fetched. Filed wiki/_views/lpv_signal_map_french_regions_2026_06.md.

## [2026-06-18] scaffold | LPV (La Passion du Vin) source section
Started LPV as a community-pulse source, mirroring the Berserkers pattern.
Added: `raw/lpv/README.md` (source layer + data contract + 403 scraper caveat),
`raw/lpv/threads/_TEMPLATE.json` (canonical JSON shape), `raw/lpv/threads/index.md`
(region-tagged registry of candidate anchor threads to ingest, N. Rhône first).
Registered `community.lpv` in `wiki/_SCHEMA.md` (frontmatter block + `## LPV` body
section, both keyed by thread `kind`: producer_fil / blind_panel / best_of_poll)
and `community.lpv.threads` in `wiki/_TAXONOMY.md` (empty table — none ingested yet).
Updated CLAUDE.md: LPV row in source-roles table, planned `*_lpv_*` pipeline under
common scripts, and an open follow-up. No producer pages carry `community.lpv` yet;
scraper + parse/compile/rollup scripts are TODO (LPV 403s the fetcher → manual paste
for now). lint 0, all --check gates green.

## [2026-06-19] ingest | Henderson Selections importer

Added Henderson Selections (Austin TX artisanal distributor/importer, est. 2012,
"Place Over Process," low-intervention small vignerons; Texas now + NY/NJ soon) as
a new importer source. Saved the full ~130-name roster to
`raw/henderson/producers_2026-06-19.md` (US West Coast + Australia, Austria, Chile,
France, Italy, Slovenia, Spain, Switzerland). Created
`wiki/importers/Henderson_Selections.md` with the roster, a curated onboarding
shortlist mapped to Evan's taste (grower Champagne bench, terroir Beaujolais,
Burgundy/Loire growers, Piedmont classicists, Skerk/Carso, Sonoma-Coast
California — Saxum/Epoch deliberately skipped), and an out-of-scope note. Did NOT
bulk-create producer pages (anti-pattern); candidates are stub wikilinks pending
per-producer LLM passes. Cross-linked the 3 roster names already in the vault via
`importer_us`: Arnot-Roberts, Hudelot-Noëllat, Elian Da Ros. Fixed a pre-existing
mis-tag surfaced by the ingest — Arnot-Roberts was filed France/Jura, corrected to
United States/California (Sonoma). Ran build_rollups + build_wiki_index; lint 0.
Open follow-up: onboard the curated Henderson candidates.

## [2026-06-19] ingest | Domaine Gallety (Côtes du Vivarais) + terroir-neighbors view
Added Domaine Gallety from the Kermit Lynch grower PDF
(https://kermitlynch.com/files/domaine-gallety.pdf). The session egress policy
blocks kermitlynch.com (host_not_allowed), so the PDF could not be fetched
directly; content was reconstructed from Kermit Lynch grower/shop pages and
importer/retailer listings via web search and saved as a stub note at
`raw/kermit_lynch/domaine-gallety.pdf`. Gallety is the benchmark estate of the
Côtes du Vivarais — a cool, west-bank, limestone AOC (status since 1999) in the
Ardèche, organic since 1979, ~15 ha clay-limestone, Syrah/Grenache reds + a
Grenache Blanc/Marsanne/Roussanne white. Created
`wiki/producers/domaine_gallety.md` (region Rhône, sub_region Côtes du Vivarais,
importer Kermit Lynch); rollups regenerated (Kermit Lynch 12→13 producers, Rhône
index 32→33). Second task — "find other producers near the same terroir that
haven't blown up yet" — filed as a keeper view
`wiki/_views/cotes_du_vivarais_terroir_neighbors_2026_06.md`: triage of
under-the-radar west-bank-limestone neighbors (Notre Dame de Cousignac + Domaine
de Vigier as search-confirmed organic in-appellation leads; Mas de Bagnols,
Belvezet, Mas de Libian, and the Brézème pair Grangeon/Lombard as verify-first
leads; Le Mazel/Calek/Azzoni flagged as the already-discovered natural-wine
cohort to skip). No pages created for the leads — view is the queue. index +
views index regenerated, lint 0.

## [2026-06-19] query | LPV vs. Berserkers scan — Côtes du Vivarais / S. Ardèche cluster
Followed the Gallety terroir-neighbors view with a community-forum check: who in
the west-bank-limestone cluster is mentioned favorably on La Passion du Vin (LPV)
vs. Wine Berserkers. Finding: it's an LPV story, near-invisible on Berserkers —
which is itself the "haven't blown up in the US" evidence. Favorable dedicated LPV
fils: Domaine Gallety (#13366, 16+ pp), Mas de Libian (#4069, 6+ pp), Domaine
Lombard/Brézème (#33636), Eric Texier/Brézème (#10299, already in vault); milder
but positive: Domaine de Vigier (#11042); mixed: Notre Dame de Cousignac (#29385,
recent notes flag alcohol heat) — demoted below Vigier; absent on both: Mas de
Bagnols, Belvezet. Berserkers had no dedicated threads for any (peripheral hits
only). Re-ranked the view's recommendations (Libian + Lombard top by esteem; Vigier
ahead of Cousignac among the organic in-appellation pair) and added a "Community
forum signal" section + LPV-vs-Berserkers table. Added an editorial community-pulse
note to the Gallety page `## Notes` (per schema, forum-standing notes are free-form,
not a hand-edited `community.lpv` block — that pipeline is still TODO). Flagged
Gallety #13366 / Libian #4069 / Lombard #33636 as clean first candidates for
`raw/lpv/threads/index.md`. Search-snippet sourced (LPV 403s the fetcher) — treat
as directional. views index regenerated, lint 0, all --check gates green.

## [2026-06-19] ingest | Berserkers Hall-of-Fame editorial threads — catalogue + source layer
Added a second kind of Berserkers source: the knowledge-rich *editorial* threads
from the WB Wine Talk Hall of Fame (#129985), distinct from the producer-mention
tally pipeline in `raw/berserkers/threads/`. Evan flagged 11 threads (2026-06-19):
trad/modern Barolo (#99925) + Bordeaux (#85688), the Clusel-Roch→Allemand N. Rhône
tour (#120248), off-beat Burgundy TNs (#112867), buying/consuming Burgundy (#146528),
California old-vine Zin vineyards (#18190), Sonoma travel (#91711), the 16-bottle
Chardonnay blowout (#101084), the '07 Oregon Pinot vintage-rehab (#45228), the
Premier Cru fraud complaint thread (#56697), and the passive subterranean root-cellar
build (#170960). New source layer `raw/berserkers/hall_of_fame/` (README data
contract + thread registry `index.md`); distillations filed as one keeper view
`wiki/_views/wb_hall_of_fame_2026_06.md`, each section mapped to Evan's curation
taste with a "Cellar take" + live thread link. WB 403s the fetcher (same as LPV), so
content is search-snippet sourced (titles/URLs/IDs + consensus producer lists are
real; post-level detail summarized) — all 11 marked `fidelity: snippet`, upgrade path
documented. N. Rhône names cross-confirmed against the LPV signal map (double
consensus). Views index regenerated (76 → 77), lint 0, all --check gates green.

## [2026-06-19] query | Northern Rhône Tour deep dive (Berserkers #120248) — 10 takeaways + producer insights
Deep read of HoF thread #120248 (the Clusel-Roch→Allemand N. Rhône cellar tour) and its
CA-vs-Rhône blind sequel #132977. New keeper view `wiki/_views/wb_northern_rhone_tour_2026_06.md`:
trip framing (Paul Gordon/Halcón + John Livingston-Learmonth, ~100 wines/day x4, day-5 CA pour),
10 key takeaways (whole-cluster house style, no new oak, multi-parcel blending, artisan vs.
Guigal/Chapoutier hillside-engineering tension, hand-ploughing, Cornas as emotional core,
Gonon = St-Joseph benchmark, serious co-op Cave de Tain, CA register-overlap not mimicry,
appellation drink-now vs. cellar logic), per-producer insights for all 8 visited domaines
(farming/winemaking + cuvées + vault status), and the full 16-wine blind ranking table (Wind
Gap + Halcón over Jamet/Gonon; young Clape closed at 11th). Linked from HoF catalogue §3 +
registry (#5 marked snippet⁺). Onboarding priorities flagged: Jamet + Auguste Clape (no vault
page), then André Perret + Cave de Tain. Search-snippet sourced (WB 403s the fetcher), cross-
checked vs. merchant/importer profiles; per CLAUDE.md the user declined the Ojai blog source.
Views index 77 → 78, lint 0, all --check gates green.

## [2026-06-19] ingest | Create Jamet + Auguste Clape producer pages (N. Rhône tour onboarding)
Closed the two highest-priority onboarding gaps from the Northern Rhône Tour deep dive:
created `wiki/producers/jamet.md` (Côte-Rôtie reference — ~8.5 ha / ~25 parcels / 17
lieux-dits, Côte Brune-dominant, whole-cluster, multi-parcel assemblage; Kermit Lynch) and
`wiki/producers/auguste_clape.md` (Cornas standard-bearer — no destemming, native yeast in
concrete, old foudres/demi-muids, no new oak / casks broken-in at Domaine Ott, terroir blend
+ younger-vine "Renaissance"; Kermit Lynch). Conservative stubs: retailer counts left at zero
for ingest_csw.py to backfill, farming left empty (neither certified) with practices in
`## Notes`; deep-dive knowledge (incl. the CA-vs-Rhône blind placements: Jamet 3rd, Clape 11th)
filed as free-form Notes per schema. Both cross-link to Allemand + the tour view; the deep-dive
view + registry updated to reflect them in-vault (remaining gaps: André Perret, Cave de Tain).
Regenerated rollups (Rhône region + Kermit Lynch importer: 13 → 15) and wiki index; reverted
incidental key-reorder churn on 11 unrelated rollup pages. Search-snippet sourced (WB 403s the
fetcher), cross-checked vs. importer/merchant profiles. Lint 0, all --check gates green.

## [2026-06-19] ingest | Backfill CSW coverage for Jamet (Clape = no genuine match)
Ran `ingest_csw.py` to fold Chambers coverage into the two new N. Rhône pages. Jamet:
two genuine dedicated articles matched — "Champet and Jamet: Cote Rotie and more" (2018-12)
and "Allemand and Jamet, Cornas and Cote Rotie" (2006-11); chambers frontmatter set
championed=true, article_count=2, dedicated_count=2, 2006–2018. Auguste Clape: the only
match was a false positive — "Different Sides of the Prism: Cain and Renaissance" (a Napa
Cabernet article that mentions Auguste Clape only in passing, via a Clos Saron profile),
caught by the 5-char "Clape" word match. No dedicated Clape article exists in the CSW corpus
(scraped 2026-04), so Clape's chambers counts left at zero and its CSW note updated to record
the false-positive rather than invite a futile re-run. NB: the global ingest run also rewrites
~197 other producer pages (vault-wide CSW drift since the last run) — deliberately NOT
committed here; that belongs in its own reviewed sweep. Regenerated wiki index; lint 0, all
--check gates green.

## [2026-06-19] query | Sonoma visit deep dive (Berserkers #91711) — trip-planning framework
Deep read of the HoF travel thread #91711 (the long-running "Planning your visit to Sonoma
County" hub). New keeper view `wiki/_views/wb_sonoma_visit_2026_06.md`. Since the thread is
~10+ yrs old and flagged (Jan 2024) for updates, the view centers the EVERGREEN framework over
the stale venue list: 10 takeaways (Sonoma is a county not a town; base by AVA cluster;
Healdsburg = the Dry Creek/RRV/Alexander hub; drive-time realities — Sonoma↔Healdsburg 1hr+ on
2-lane roads, the "Girl & the Fig then 1pm RRV Pinot needs a helicopter" quip; cap at 1–2 AVAs/
day; split-stay vs central-base; appointment-only reality; west-county orbit; dining as a
planning input; treat the thread as a template), a "where to base yourself" lodging-logic table,
an AVA character cheat-sheet, dining/lodging anchors (Catelli's, Girl & the Fig, Flambeaux,
Lynmar Bliss House — flagged verify-before-booking), and a cellar take mapping it to Evan's
restrained-California targets (Bedrock Montecillo/Moon Mtn, the old-vine Zin atlas, Arnot-Roberts
RRV/Sonoma Coast) with an itinerary skeleton. Linked from HoF catalogue §7 + registry (#3 →
snippet⁺). Search-snippet sourced (WB 403s the fetcher). Views index 78 → 79, lint 0, gates green.

## [2026-06-21] ingest | Scaffold Vinolist NYC as a trade/somm-demand source + NYC restaurant-list view
Researched [vinolistnyc.com](https://vinolistnyc.com/) — **not a shop/importer**, but a search
engine aggregating ~65 NYC **restaurant** wine lists ("65 Restaurants, 37,878 Bottles"; count
drifts on re-scrape). Founder (lower-confidence): Etesh Mangray (holds the older vinolist.com
"The Wine Database" trademark). Site 403s WebFetch **and** the host is egress-blocked, so data
extraction is blocked exactly like LPV. Integrated it the vault-native way, mirroring the
Berserkers/LPV pattern, to serve Evan's three stated uses: (1) restaurant database, (2) producer
tracking by popularity/price/prestige, (3) discovery. New keeper view
`wiki/_views/nyc_restaurant_wine_lists_2026_06.md` — taste-filtered NYC restaurant picks (grand
cellars EMP/Chambers/Le Bernardin; grower-Champagne Terroir/Compagnie; grower-French Le Veau
d'Or/Frenchette/Winona's/Ops/Lei; Italian deep-cut Peasant), a producer-tracking recipe
(list-count = popularity/prestige, min/avg/max price, momentum via dated snapshots), a v0
manual producer-sighting seed (Selosse, Agrapart, Suenen, Dhondt-Grellet, La Rogerie, Vouette &
Sorbée, Tarlant, Cordeuil, Julien Meyer, Dreyer, Joly, Clos des Plantes, Métras, Valette,
Skyaasen, Tschida — all gap-check), and a query cheat-sheet. Source layer scaffolded at
`raw/vinolist/` (README + data contract + `restaurants/_TEMPLATE.json` + taste-tagged registry +
`snapshots/` for momentum). Schema block `community.vinolist` (scaffolded) added to `_SCHEMA.md`;
`community.vinolist.restaurants` namespace registered in `_TAXONOMY.md`. CLAUDE.md updated:
Source-roles row, planned 4-script pipeline (`scrape/parse/compile/build_vinolist*`), open
follow-up. Scraper + compiler are TODO (blocked); manual-paste ingest for now. Search-snippet
sourced (Resy Hit List / Star Wine List / Wine Spectator / Decanter / VinePair); contents
flagged verify-before-quoting. Regenerated views index; gates green.
