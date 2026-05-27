---
type: source_readme
source: wine_lists
updated: 2026-05-27
---

# Wine Lists — source layer

Weekly snapshots of curated NYC wine lists. Each restaurant gets a directory,
each weekly fetch becomes a raw file + a normalized JSON snapshot. Downstream
scripts diff snapshots week-over-week to surface **new arrivals** — producers /
cuvées / vintages that weren't on the list the prior week.

This is the same pattern as `raw/berserkers/` (external signal → per-producer
data → wiki rollup). The signal here is "what good NYC wine programs are
pouring this week," which feeds gap analysis and target-list curation.

## Layout

```
raw/wine_lists/
├── README.md                         this file
├── <slug>/
│   ├── source.md                     URL, format, scrape method, notes
│   ├── raw/
│   │   ├── 2026-05-27.pdf            verbatim download
│   │   └── 2026-05-27.txt            extracted text (PDFs only; created by parse step)
│   ├── snapshot_2026-05-27.json      normalized wines
│   └── snapshot_2026-06-03.json      next week's snapshot
```

## In-scope sources (v1)

| Slug | Restaurant | Format | URL stable? |
|---|---|---|---|
| `chambers_pours` | Chambers Street Wines — weekly pour list | PDF (Squarespace) | filename rotates; refetch URL each week |
| `estela` | Estela | PDF (binwise.com) | yes, fixed URL |
| `peasant` | Peasant | HTML | yes |
| `claud` | Claud | HTML | yes |
| `noreetuh` | Noreetuh | HTML (Squarespace) | yes |

Deferred to v2 (need OCR, paywall, or no public list): Terroir Tribeca, Dame,
Café Altro Paradiso, Saint Urban.

## Snapshot JSON shape

```json
{
  "restaurant": {
    "slug": "estela",
    "name": "Estela",
    "address": "47 East Houston St, New York, NY"
  },
  "snapshot_date": "2026-05-27",
  "source_url": "https://hub.binwise.com/restaurant/estela/list/estela-wine-list.pdf",
  "source_format": "pdf",
  "source_sha256": "abc123…",
  "fetched_at": "2026-05-27T15:32:00Z",
  "wines": [
    {
      "raw_text": "Domaine Roulot, Meursault 1er Cru Charmes, 2018 ... 295",
      "producer_raw": "Domaine Roulot",
      "producer_slug": "roulot",
      "producer_slug_confidence": "high",
      "cuvee": "Meursault 1er Cru Charmes",
      "vintage": 2018,
      "region": "Burgundy",
      "sub_region": "Meursault",
      "price_usd": 295,
      "by_the_glass": false,
      "section": "Burgundy — Côte de Beaune"
    }
  ]
}
```

Producer slug normalization follows vault rules (lowercase, ASCII-folded,
underscored, common prefixes stripped — see `parse_wine_list.py:slugify`).
`producer_slug_confidence` is `"high"` if the slug matches an existing
`wiki/producers/<slug>.md`; otherwise `"low"` (candidate for a new page or
an alias entry).

## Pipeline

```
scrape_wine_lists.py    <slug>            → raw/wine_lists/<slug>/raw/<date>.{pdf,html}
parse_wine_list.py      <slug> [<file>]   → raw/wine_lists/<slug>/snapshot_<date>.json
diff_wine_lists.py      [--since DATE]    → build/wine_list_arrivals_<YYYY-WW>.json
build_wine_list_view.py [--week YYYY-WW]  → wiki/_views/wine_list_arrivals.md
                                            wiki/_views/wine_list_arrivals_<YYYY-WW>.md
```

Each script is **idempotent** and **dry-run by default** — pass `--apply` to
write to disk. Diff is keyed on `(producer_slug, cuvée_norm, vintage)`.

## Network

`scrape_wine_lists.py` uses stdlib `urllib` and runs from a machine with
public internet (your laptop, or a GitHub Action). The Claude Code on the web
sandbox has restricted outbound — fetch there will fail. **Manual-paste
fallback:** drop the wine list file at
`raw/wine_lists/<slug>/raw/<YYYY-MM-DD>.{pdf,html,txt}` and skip straight to
`parse_wine_list.py`.

## Adding a new restaurant

1. Create `raw/wine_lists/<slug>/source.md` (copy the template from an
   existing source.md).
2. Add a fetcher in `scrape_wine_lists.py::SOURCES`.
3. Add a parser in `parse_wine_list.py::PARSERS`.
4. Run the pipeline; commit the resulting `source.md` + first snapshot.
