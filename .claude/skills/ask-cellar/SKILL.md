---
name: ask-cellar
description: Answer questions about Evan's wine collection. Reads wiki/index.md first, then drills into producer/region/retailer/cellar pages, applies Evan's curation filters from CLAUDE.md, and answers in plain readable prose (Obsidian wikilinks only when writing to actual vault files). Files keeper answers back as new pages in wiki/_views/.
---

# /ask-cellar

The query skill for the wine_vault. Three preconditions, in order:

1. The current working directory IS `wine_vault/` (this repo). If not,
   refuse and ask the user to `cd` there.
2. `wiki/index.md` exists and is current. Read it first — that's the
   LLM-wiki pattern's first-read surface. If `--check` would fail,
   suggest the user regenerate before answering.
3. Apply Evan's curation taste filters from CLAUDE.md when ranking
   candidates. Don't recommend wines outside the curated style unless
   he explicitly asks for adjacent territory.

## What replaced what

This skill used to point at the old Drive `wine_wiki/` folder. It now
points at the in-repo paths only:

| Old (Drive)                | New (this repo)            |
|---|---|
| `wine_wiki/producers/`      | `wiki/producers/`          |
| `wine_wiki/regions/`        | `wiki/regions/`            |
| `wine_wiki/retailers/`      | `wiki/retailers/`          |
| `wine_wiki/cellar.csv`      | `wiki/My Cellar.csv` + `cellar/*.md` |
| `wine_wiki/raw/csw/`        | `raw/csw/markdown/`        |

If a Drive folder is referenced by old documentation or chat history,
ignore it. Git is the source of truth (see CLAUDE.md → "Architecture-fix
history").

## Read order

0. **For any question that spans producers / land / style / source / ownership
   (i.e. anything needing a join, not a single-page lookup): read the signals
   layer FIRST.** `build/producer_signals.json` (Claude Code sessions — the machine
   copy) or [[producer_signals_board_2026_07]] (via the GitHub connector). It's the
   pre-computed join of land + style + `trust_tier` + availability + critic +
   ownership + `taste_fit` + `conviction` for all producers. Shortlist from it,
   then drill in. Regenerate with `python scripts/build_signals.py` if stale.
   Rank with `taste_fit` (core > adjacent; never surface `skip`) and `trust_tier`
   (1 > 2) — this is Evan's taste + trusted-source bias, encoded. Architecture:
   [[linkage_architecture_2026_07]].
1. `wiki/index.md` — catalog of all pages. Find candidates by
   region / importer / retailer / producer / cellar entry.
2. `wiki/_TAXONOMY.md` — confirm region names and farming enum values.
3. The candidate pages themselves (`wiki/producers/<slug>.md`,
   `wiki/regions/<Region>_Producers.md`, `cellar/<vintage>_<slug>.md`).
4. `wiki/importers/Roscioli_Wine_Club.md` — 156 Italian (+ Champagne) producer profiles with video. For Italian queries by region/style, check Roscioli first — it's the strongest Italian-importer hub in the vault.
5. `raw/csw/markdown/`, `raw/raeders/markdown/`, `raw/berserkers/threads/`
   only when the wiki page lacks the detail (excerpts, scores,
   community signal).
6. CLAUDE.md → "Curation taste" — apply before recommending.

## Citation format

Two different surfaces, two different formats — don't mix them up:

- **In the chat reply itself:** plain readable names, no bracket
  syntax. The Claude Code chat UI does not render Obsidian wikilinks —
  `[[slug|Name]]` shows up to the user as literal brackets, which is
  noise, not a link. Just write **Laurent Barth** (bold is fine), and
  mention the page path in prose only if it's genuinely useful ("see
  `wiki/producers/laurent_barth.md`").
- **In any content written to a file** (a new/updated page under
  `wiki/_views/`, or an edit to a producer/region page): use Obsidian
  wikilinks, since that's what Obsidian actually renders:

  ```markdown
  [[laurent_barth|Laurent Barth]] — biodynamic Alsace, [[Mosel_Producers|Mosel rollup]] for context.
  ```

  Filenames are `lowercase_underscored.md`; the wikilink stem must
  match exactly. When in doubt, grep `wiki/producers/` for the slug.

## Filing keeper answers

If the question is worth keeping (gap analysis, drink-window
shortlist, cross-retailer comparison, theme browse), append to a new
page in `wiki/_views/`. Naming: `<theme>_<YYYY_MM>.md`. Set
`type: view` in the frontmatter. Then run:

```sh
python scripts/build_wiki_index.py    # re-index so future asks find it
# append entry to wiki/log.md: `## [YYYY-MM-DD] view | <title>`
```

Don't let analysis disappear into chat — the Karpathy pattern's whole
point is that good answers become first-class pages.

## Common query patterns

- **"What's past drink window?"** → scan `cellar/` frontmatter
  `drink_window_end` vs today's date.
- **"Top aged Champagnes I should buy?"** →
  `wiki/regions/Champagne_Producers.md`, filter to grower / late-disgorged,
  cross-ref `raw/raeders/markdown/` for current availability.
- **"What in my cellar is CSW-championed?"** → join `cellar/` with
  `wiki/retailers/Chambers_Street_Wines.md`.
- **"WK-style value Bordeaux I don't own?"** →
  `wiki/regions/Bordeaux_Producers.md` minus what's in `cellar/`,
  filter by farming + price tier.
- **"What's WB hyping that I don't own?"** →
  `wiki/_views/wb_<thread>_top_100.md` filtered to rows without ✅ (no
  vault page) or 🍷 (no cellar bottles).
- **"What in my cellar is also a WB favorite?"** →
  `wiki/_views/wb_in_cellar.md`.
- **"Producers accelerating per the WB hivemind?"** →
  `wiki/_views/wb_<thread>_momentum.md` Surging + New entrants tables.

## Anti-patterns

- Don't fabricate critic quotes — Vinous and Wine Advocate are wired
  for ingest (`raw/clippings/`) but the vault is sparse on these
  sources. If asked about a Vinous score, check `raw/clippings/vinous/`
  for an actual clipping; if absent, say so.
- Don't claim a producer is in Evan's cellar without confirming
  `cellar/<...>.md` exists.
- Don't recommend wines outside the curation style unless asked.
- Roscioli is Italian-only (plus a few Champagne growers — George Laval, Roger Brun). Don't expect French/German/Spanish coverage there.
