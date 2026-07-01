---
type: source_readme
source: berserkers
updated: 2026-05-08
---

# Berserkers — source layer

Wine Berserkers community threads. Each thread becomes a `threads/<slug>.json`
that downstream scripts compile into producer-page signals + rollups.

## Layout

```
raw/berserkers/
├── README.md                       this file
├── threads/
│   ├── top10_in_cellar.json        canonical structured tally
│   ├── top10_in_cellar.raw.md      raw scraped post dump (one per thread)
│   └── <future_thread>.json        next thread, same shape
```

## Thread JSON shape

```json
{
  "thread": {
    "slug": "top10_in_cellar",            // matches filename, used as key in producer frontmatter
    "title": "...",
    "url": "https://www.wineberserkers.com/t/.../<id>",
    "thread_id": 74370,
    "first_post_date": "2013-02",
    "last_post_date": "2026-03",
    "post_count": 1089,
    "unique_producers": 1115,
    "total_mentions": 4999,
    "era_breakpoints": ["2013-2014", "2021-2022", "2023-2026"],
    "scraped_at": "YYYY-MM-DD",
    "scrape_method": "discourse_json_v1 | spreadsheet_seed_v1 | manual_paste_v1"
  },
  "producers": [
    {
      "rank": 1,
      "raw_name": "Bedrock",
      "mentions": 98,
      "mentions_2013_2014": 9,
      "mentions_2021_2022": 38,
      "mentions_2023_2026": 51,
      "momentum_score_2023": 1.4,
      "first_seen": "2013-08",      // optional
      "last_seen": "2026-03",       // optional
      "notable_quotes": []          // optional, used in body section
    }
  ]
}
```

`null` is allowed for any era split or momentum field — the compiler degrades
gracefully. The seed JSON for `top10_in_cellar` has `null` era splits because
the spreadsheet only carries totals; running `parse_wb_thread.py` against a
fresh scrape repopulates them.

## Pipeline

```
scrape_wb_thread.py     URL                      → threads/<slug>.raw.md
parse_wb_thread.py      threads/<slug>.raw.md    → threads/<slug>.json
compile_wb_signals.py   threads/<slug>.json      → wiki/producers/*.md updates
build_wb_rollups.py     all threads/*.json       → wiki/_views/*.md, build/wb_gap_candidates.md
```

Each script is dry-run by default; pass `--apply` to write.

## Full-thread ingest via logged-in browser (WB 403s the scraper)

`scrape_wb_thread.py` is bot-blocked (403) from this host, so it only ever
seeds the top-100 from a spreadsheet. To land the **whole** thread (all posts →
real era splits + momentum), pull it through a logged-in browser, which is *not*
blocked:

1. **Grab** — log in to wineberserkers.com, open the thread, and run
   `scripts/wb_browser_fetch.js` in the DevTools console, **or** tap the
   one-line bookmarklet in `scripts/wb_browser_fetch.bookmarklet.txt` (works on
   mobile). Either downloads `<slug>.discourse.json` — the exact shape
   `parse_wb_thread.py` consumes. No copy-paste of posts, nothing leaves the
   browser but normal same-site requests.
2. **Parse** — drop the file at `threads/<slug>.discourse.json` and run:

   ```
   python scripts/parse_wb_thread.py raw/berserkers/threads/top10_in_cellar.discourse.json \
     --slug top10_in_cellar \
     --title "Top 10 Producers in your cellar?" \
     --thread-url https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370 \
     --merge-with raw/berserkers/threads/top10_in_cellar.json
   ```

   `--merge-with` preserves curated `notable_quotes` from the existing seed and
   overwrites the tally with full per-era counts.
3. **Compile + roll up** — `compile_wb_signals.py --apply` then
   `build_wb_rollups.py --apply`, then `build_wiki_index.py` + a `log.md` entry.

Last-resort fallback (no console/bookmarklet): paste rendered posts into
`threads/<slug>.raw.md` using `_PASTE_TEMPLATE.raw.md`, then parse that file.

## Adding a second thread

1. `python scripts/scrape_wb_thread.py https://www.wineberserkers.com/t/.../12345 --slug aged_champagne`
2. `python scripts/parse_wb_thread.py raw/berserkers/threads/aged_champagne.raw.md`
3. `python scripts/compile_wb_signals.py raw/berserkers/threads/aged_champagne.json --apply`
4. `python scripts/build_wb_rollups.py --apply`

Producer pages then carry both threads under `community.berserkers.threads.<slug>`.
