---
type: source_readme
source: berserkers_hall_of_fame
updated: 2026-06-19
---

# Berserkers — Hall of Fame (editorial threads) source layer

A **second** kind of Berserkers source, distinct from the producer-mention tally
pipeline in `../threads/` (which counts how often a producer is named and emits
`community.berserkers` frontmatter signals + rollups).

These are the **knowledge-rich editorial threads** from the Wine Berserkers
[*Wine Talk Hall of Fame*](https://www.wineberserkers.com/t/wine-berserkers-wine-talk-hall-of-fame-thread/129985)
— style maps (trad vs. modern Barolo / Bordeaux), producer tours (N. Rhône),
vineyard atlases (old-vine Zin), buying strategy (Burgundy), travel guides
(Sonoma), cautionary tales (Premier Cru fraud), and how-to builds (passive root
cellar). The unit of value here is *distilled prose + curated lists*, not a
mention count — so the output is a single keeper catalogue in
`wiki/_views/wb_hall_of_fame_2026_06.md`, not per-producer frontmatter.

## Access constraint (read this first)

Wine Berserkers **403s the fetcher** from this environment — both the Discourse
JSON endpoint (`/t/<slug>/<id>.json`) used by `../../../scripts/scrape_wb_thread.py`
*and* WebFetch. Same posture as LPV (`raw/lpv/`). So the catalogue's distillations
are **search-snippet sourced** (Google-indexed excerpts surfaced via WebSearch):
thread titles, URLs, IDs, and the broad consensus / producer lists are real, but
post-level detail and tasting notes are summarized, not transcribed. Anything
quoted verbatim or attributed to a named poster must be verified in-browser first.

**To upgrade a thread to full fidelity:** paste the post dump into
`threads/<slug>.raw.md` (or `.discourse.json` if you can pull the JSON from a
logged-in browser) and transcribe the durable content into the catalogue page,
then flip that thread's `fidelity:` in `index.md` from `snippet` to `transcribed`.

## Layout

```
raw/berserkers/hall_of_fame/
├── README.md      this file (data contract)
├── index.md       thread registry — the prioritized HoF threads + parent
└── threads/       (optional) full post dumps once a thread is transcribed
```

## Registry row shape (see index.md)

Each row carries: `slug` (catalogue anchor + future filename stem), `title`
(verbatim WB title), `discourse_url`, `thread_id` (Discourse numeric id, or the
legacy vBulletin `t=` id where the thread predates the Discourse migration and
the new id wasn't surfaced), `category` (style-map / producer-tour /
vineyard-atlas / strategy / travel / cautionary / cellar-build / humor),
`fidelity` (`snippet` | `transcribed`), and `cellar_relevance` (a one-line map to
Evan's curation taste).

## Pipeline (today)

```
WebSearch per thread  →  distill consensus + lists  →  wiki/_views/wb_hall_of_fame_2026_06.md
                                                     →  build_views_index.py (--check gates CI)
                                                     →  wiki/log.md entry
```

No dedicated parser/compiler is warranted yet — these threads are read-and-distill,
not tally-and-aggregate. If a future thread *is* a tally (e.g. a "rank your top
Zin vineyards" poll), route it through the `../threads/` mention pipeline instead.
</content>
</invoke>
