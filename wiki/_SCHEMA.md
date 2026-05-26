---
type: schema
updated: 2026-04-21
---

# Wine Wiki Schema

Canonical structure for every file in `wiki/`. Enforce via the lint script (`scripts/lint.py`). The schema is designed so derived outputs (widget JSON, regional rollups, importer rollups, cellar-overlap views) can be generated deterministically, while the bulk of the content stays as LLM-editable prose.

---

## Producer page — `wiki/producers/<Snake_Case_Name>.md`

```yaml
---
type: producer
name: "Laurent Barth"                # canonical display name
slug: laurent_barth                   # matches filename stem
aliases: ["Barth, Laurent"]           # alternate spellings encountered in emails/lists

country: "France"                     # ISO-style name; see wiki/_TAXONOMY.md for allowed values
region: "Alsace"                      # top-level wine region
sub_region: ""                        # e.g. "Gevrey-Chambertin", "Mosel-Mittelmosel"
appellations: ["Alsace Grand Cru Kaefferkopf"]  # specific AOC/DOC/etc. if known

farming: ["biodynamic", "natural"]    # any of: conventional, sustainable, organic, biodynamic, natural
certifications: []                    # e.g. ["Demeter", "Ecocert"]

importer_us: ["Jenny & François"]     # may be empty; may have several over years

retailers:
  chambers:
    championed: true                  # has dedicated article or repeated coverage
    article_count: 4
    dedicated_count: 1
    first_year: 2009
    last_year: 2025
  dte:                                # Down to Earth / Robert Panzer
    in_portfolio: true
    cuvee_count: 3
    price_min: 22
    price_max: 39
  raeders:
    in_portfolio: false
  fass:
    in_portfolio: false

events: []                            # curatorial/festival appearances; see wiki/_TAXONOMY.md events
tags: ["alsace", "biodynamic", "white-wine-focused"]
---

# Laurent Barth

One-paragraph human summary. The LLM compile step writes this from the CSW excerpts + DTE context.

## CSW Write-ups

### ★ [Alsace Review Part 3: Laurent Barth](https://chambersstwines.com/blogs/articles/alsace-review-part-3-laurent-barth)
*2018-01*

Excerpt from the article (first ~2 sentences is enough).

### [Another article]
*YYYY-MM*
...

## Down to Earth Wines (Panzer)

Currently in portfolio:
- Gewurztraminer Kitterlé Grand Cru 2019 — $39
- Riesling Kessler Grand Cru 2012 — $33

## Raeder's

(empty or list)

## FASS

(empty or list)

## Cellar

- 2 × Gewurztraminer Kitterlé Grand Cru 2019 — purchased 2025-03 @ $35 — location: NYC closet — drink 2028-2035

(This section is OPTIONAL and auto-populated from `cellar/` entries.)

## Cross-references

- [[Alsace_Producers|Alsace]]
- [[Jenny_and_Francois|Jenny & François (importer)]]
- [[Chambers_Street|Chambers Street (retailer)]]

## Notes

Free-form prose. Tasting notes, vineyard details, news.
```

### Rules

1. **`slug` equals the filename stem** (no spaces, lowercase, snake_case). `name` is the display form with accents / capitalization.
2. **Booleans**: always `true` / `false`, never strings.
3. **Empty arrays**: `[]`, never omitted — the lint script flags missing keys.
4. **Retailer blocks**: a retailer key MUST be present with at minimum `in_portfolio: false` (or the CSW analogue, `championed: false`) even when there's no relationship. This is what makes cross-retailer queries cheap.
5. **Article list under `## CSW Write-ups`**: each article is a `###` header, title linked to URL, `*YYYY-MM*` italic date on the next line, short excerpt below. `★` prefix marks "dedicated" (producer named in title).
6. **Cross-references**: Obsidian `[[wikilink]]` syntax. Link text after `|` is the display form. Link stubs that don't exist yet are OK — the lint script lists them as "missing pages to create".

---

## Producer page — `community` block

The `community:` frontmatter block aggregates signals from community sources
(currently Wine Berserkers; structured for future additions like CellarTracker
TN counts, Reddit /r/wine ranking threads, etc.). It coexists with `retailers:`
and follows the same conventions: every key declared, every retailer/source key
present even when there is no relationship, every nested block consistently
indented.

```yaml
community:
  berserkers:
    threads:
      top10_in_cellar:
        rank: 15                            # int — rank within the thread, 1-indexed
        mentions: 32                        # int — total mentions across all posts
        mentions_2013_2014: 6               # int|null — mentions in this era bucket
        mentions_2021_2022: 13
        mentions_2023_2026: 13
        momentum_score_2023: 1.0            # float|null|"inf" — see below
        last_updated: 2026-05-08
      <future_thread_slug>:
        ...
```

### Field rules

1. **Thread slug** — must match a registered thread in `_TAXONOMY.md` under
   `community.berserkers.threads`. Compile-time enforced by `lint.py`.
2. **`rank`** — 1-indexed within the thread. The thread's total producer count
   lives in `raw/berserkers/threads/<slug>.json` (`thread.unique_producers`),
   not duplicated here.
3. **Era counts** — integers when known, `null` when the source data didn't
   carry per-era splits. Compiler degrades gracefully on null.
4. **`momentum_score_2023`** — ratio of (mentions in 2023+ era) ÷ (mentions in
   earliest active era). `null` for new entrants (no earlier baseline). Stored
   as `inf` (string) when serialized to YAML if the producer is technically
   new but has explicit mentions.
5. **`last_updated`** — ISO date the compiler last touched this block. Bumped
   automatically by `compile_wb_signals.py`.

### Anti-pattern

Don't hand-edit `community.berserkers.threads.*` blocks. They're regenerated
on every `compile_wb_signals.py --apply` from the canonical thread JSON.
Hand-edits will be silently overwritten.

---

## Producer page — `## Berserkers` body section

Auto-rendered by `compile_wb_signals.py`. One sub-section per thread the
producer appears in:

```markdown
## Berserkers

### [Top 10 Producers in your cellar?](https://www.wineberserkers.com/t/.../74370) (thread #74370, 2013-02–2026-03)

**Rank 15** of 1,115 producers — **32 mentions** across 1,089 posts.

| Era | Mentions |
|---|---|
| 2013–2014 | 6 |
| 2021–2022 | 13 |
| 2023–2026 | 13 |

**Momentum 2023+:** 1.0× (steady).

> Optional notable quote, attributed.
```

Inserted after `## CSW Cellar Note` (or `## CSW Write-ups` if no cellar note),
before `## Down to Earth Wines (Panzer)` / `## Cross-references` / `## Notes`.

### Anti-pattern

Don't hand-edit the `## Berserkers` section either — it's fully regenerated
from the thread JSON. If you want to add an editorial note about a producer's
WB reputation, put it in the producer's free-form `## Notes` section instead.

---

## Producer page — `## Vinous Reviews` body section

Auto-rendered by `compile_clippings.py vinous --apply` from
`raw/clippings/vinous/*.md` (Obsidian Web Clipper output).

```markdown
## Vinous Reviews

### [Weingut Keller and the Grapes of Rheinhessen](https://vinous.com/articles/...)
*2026-03-15* — Antonio Galloni

> First two sentences of the article body, auto-extracted as an excerpt.
> Used to give the LLM enough context to know what the critic said without
> needing to re-open the source clipping.
```

Inserted after `## Berserkers` (if present) or `## CSW Write-ups`,
before `## Down to Earth Wines (Panzer)`.

### Anti-pattern

Don't hand-edit. Regenerated on every `compile_clippings.py vinous`
run. Editorial notes go in `## Notes` (free-form).

---

## Producer page — `## Wine Advocate (Kelley)` body section

Same shape as `## Vinous Reviews`, sourced from
`raw/clippings/wine_advocate/*.md`. Distinct from `## Berserkers
(William Kelley)` which is the *community* signal (forum posts);
this section is the *editorial* signal (publication articles).

```markdown
## Wine Advocate (Kelley)

### [Burgundy 2022 In Bottle: Côte de Beaune](https://www.wineadvocate.com/...)
*2026-04-12* — William Kelley

> 95-99 point notes on the Côte de Beaune whites, with vintage context...
```

---

## Region index — `wiki/regions/<Region>_Producers.md`

Auto-generated by `scripts/build_rollups.py`. Example pattern from existing `Loire_Producers.md`:

```markdown
---
type: region_index
region: "Loire"
updated: 2026-04-21
---

# Loire — Producer Index

**N producers** tracked.

| Producer | Country | Sub-region | CSW | DTE | Raeder's | FASS | Cellar |
|---|---|---|---|---|---|---|---|
| [[Domaine_Baudry|Domaine Baudry]] | France | Chinon | 30 | ✓ | — | — | 4 btl |

*Source: compiled from wiki/producers/*.md*
```

---

## Importer index — `wiki/importers/<Name>.md`

```yaml
---
type: importer
name: "Neal Rosenthal"
slug: neal_rosenthal
url: "https://rosenthalwine.com"
focus: ["Burgundy", "Piedmont", "Champagne"]
notable_producers: ["Château Le Puy", "Brovia", "Bernhard Huber"]
---
```

Body: prose about the importer, pulled from `wine resources.pdf` and any Chambers editorial that mentions them.

---

## Retailer index — `wiki/retailers/<Name>.md`

```yaml
---
type: retailer
name: "Chambers Street Wines"
slug: chambers_street
url: "https://chambersstwines.com"
location: "NYC"
editorial_url_pattern: "https://chambersstwines.com/blogs/articles/{slug}"
---
```

Body: prose on the retailer's editorial voice, strengths, what kinds of producers they champion.

---

## Cellar entries — `cellar/<vintage>_<producer>_<cuvee>.md`

```yaml
---
type: cellar_entry
producer_slug: laurent_barth
cuvee: "Gewurztraminer Kitterlé Grand Cru"
vintage: "2019"
bottle_size: "750ml"
quantity: 2
purchase_date: "2025-03-12"
purchase_price_usd: 35
source_retailer: "dte"
location: "NYC closet"
drink_window_start: 2028
drink_window_end: 2035
opened: []                            # list of open events: [{date, notes}]
---
```

Body: free-form notes (serving, meal pairings, bottle condition).

---

## Derived JSON — `build/widget_data.json`

Emitted by `scripts/build_widget_json.py`. Feeds `dte_wines_1.jsx` v2. Shape:

```json
{
  "producers": [
    {
      "slug": "laurent_barth",
      "name": "Laurent Barth",
      "country": "France",
      "region": "Alsace",
      "farming": ["biodynamic", "natural"],
      "retailers": { ... same as frontmatter ... },
      "cellar_bottles": [ { "slug": "laurent_barth", "cuvee": "...", "vintage": "2019", "retailer": "dte", "price_usd": 39 } ],
      "csw_articles": [ { "title": "...", "url": "...", "date": "2018-01", "dedicated": true }, ... ],
      "editorial_summary": "one-paragraph prose pulled from body"
    }
  ],
  "wines": [
    { "producer_slug": "laurent_barth", "cuvee": "...", "vintage": "2019", "retailer": "dte", "price_usd": 39 }
  ]
}
```

Never hand-edit `build/`. Regenerate from the wiki.