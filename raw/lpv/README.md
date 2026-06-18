---
type: source_readme
source: lpv
updated: 2026-06-18
status: scaffolded — data contract + registry defined; scraper/compiler not yet written
---

# LPV (La Passion du Vin) — source layer

[La Passion du Vin](https://www.lapassionduvin.com) is the serious French-amateur
wine forum (~400k posts, ~6k members, founded 2002). It's a **community-pulse
source** like Wine Berserkers — different community, same job: drive gap analysis
and momentum/consensus signals on producer pages, biased to French regions.

This source layer mirrors `raw/berserkers/`. Each ingested LPV thread becomes a
`threads/<slug>.json` that downstream scripts compile into producer-page signals
(`community.lpv.*` frontmatter + a `## LPV` body section) and `_views/` rollups.

Where LPV signal is strongest (and which threads to ingest first) is mapped in
[`wiki/_views/lpv_signal_map_french_regions_2026_06.md`](../../wiki/_views/lpv_signal_map_french_regions_2026_06.md).

## ⚠️ Scraper blocker (read first)

LPV **403s the WebFetch tool** on every URL (bot protection). The Berserkers
pipeline could hit Discourse JSON endpoints directly; LPV cannot be fetched the
same way from this environment. Until a real scraper exists (browser
headers/session, or a manual paste workflow), ingest is **manual paste**:
copy a thread's posts into `threads/<slug>.raw.md`, then parse. The data
contract below is designed so a future automated scraper drops in without
changing the JSON shape.

## Layout

```
raw/lpv/
├── README.md                  this file
├── threads/
│   ├── _TEMPLATE.json         the canonical JSON shape (copy to start a thread)
│   ├── index.md               registry of candidate threads to ingest (region-tagged)
│   ├── <slug>.raw.md          raw scraped/pasted post dump (one per thread)
│   └── <slug>.json            structured, compiler-ready (one per thread)
```

## Three LPV "thread kinds" (signal differs by kind)

LPV doesn't have one tally like the Berserkers "top 10" thread; its signal lives
in three structural shapes. Each maps to `thread.kind`:

| `kind` | What it is | Signal it carries |
|---|---|---|
| `producer_fil` | a long per-producer megathread (multi-vintage CRs from many tasters) | sentiment + vintage track record for one producer |
| `blind_panel` | an organized blind horizontal/vertical (e.g. "24 Saint-Joseph 2018 à l'aveugle") | **relative rank + /20 score** within a vintage/appellation — highest trust |
| `best_of_poll` | a curated best-of / "vos préférés" / "top 3" poll | distilled community consensus (who the hive rates) |

## Thread JSON shape

See `threads/_TEMPLATE.json` for the copy-paste skeleton. Summary:

```json
{
  "thread": {
    "slug": "saint_joseph_2018_horizontale",   // matches filename; key in producer frontmatter
    "title": "Horizontale 24 Saint-Joseph rouges 2018 à l'aveugle",
    "url": "https://www.lapassionduvin.com/degustations-eclectiques/52174-...",
    "section": "degustations-eclectiques",      // LPV forum section slug
    "kind": "blind_panel",                       // producer_fil | blind_panel | best_of_poll
    "region": "Rhône",                           // top-level region per _TAXONOMY.md
    "appellation": "Saint-Joseph",               // optional finer scope
    "vintage": 2018,                             // optional (blind_panel/horizontal)
    "first_post_date": "2024-01",
    "last_post_date": "2024-02",
    "post_count": null,
    "panel_size": 24,                            // n wines tasted (blind_panel/poll); null for fil
    "scraped_at": "YYYY-MM-DD",
    "scrape_method": "manual_paste_v1 | discourse_html_v1 | template"
  },
  "producers": [
    {
      "raw_name": "Sébastien Blachon",
      "slug": "domaine_blachon",                 // optional resolved vault slug (LLM curation)
      "cuvee": "Margiriat",                       // optional
      "rank": 11,                                 // int|null — rank in panel/poll
      "score_20": 15.5,                           // float|null — blind mean /20
      "sentiment": "positive",                    // reference|positive|mixed|cautious|null
      "vintages": [2018],                         // list|null — vintages discussed
      "notable_quotes": [                         // optional, used in body section
        {"text": "texture très fine, arômes précis, jeune producteur à suivre", "author": "", "date": "2024-01"}
      ]
    }
  ]
}
```

`null` is allowed for any optional field — the compiler degrades gracefully
(same contract as Berserkers). `slug` is filled by LLM curation, not blind
string-matching (a `raw_name` like "Domaine Blachon" can mean either the Mauves
estate or the Cave Sébastien Blachon — see the Blachon view).

## Pipeline (planned — scripts not yet written)

Mirrors the Berserkers four-script pipeline. **None of these exist yet**; this
README defines the contract they'll implement.

```
scrape_lpv_thread.py    URL                  → threads/<slug>.raw.md     (TODO — blocked by 403; manual paste for now)
parse_lpv_thread.py     threads/<slug>.raw.md → threads/<slug>.json       (TODO)
compile_lpv_signals.py  threads/<slug>.json   → wiki/producers/*.md       (TODO)
build_lpv_rollups.py    all threads/*.json    → wiki/_views/*.md          (TODO)
```

Each will be dry-run by default; `--apply` to write — same convention as `*_wb_*`.

## Adding a thread (manual-paste workflow, today)

1. Copy `threads/_TEMPLATE.json` → `threads/<slug>.json`; fill `thread.*`.
2. Paste the thread's relevant posts into `threads/<slug>.raw.md` (provenance).
3. Hand-fill (or LLM-fill) the `producers[]` array, resolving `slug` per
   Evan's curation taste; leave unknown fields `null`.
4. Register the slug in `wiki/_TAXONOMY.md` → `community.lpv.threads`.
5. When `compile_lpv_signals.py` exists, run it `--apply`; until then the JSON
   is the durable record and can be read directly during `/ask-cellar`.

## Scope (Evan's French regions — see the signal map)

Priority sections to mine: `/rhone` (N. Rhône core), `/bourgognebeaujolais`,
`/bordeaux`, `/champagne`, `/loire`, `/jura-et-savoie`, and the cross-cutting
`/degustations-eclectiques` (organized blind tastings). Candidate anchor threads
per region are listed in `threads/index.md`.
