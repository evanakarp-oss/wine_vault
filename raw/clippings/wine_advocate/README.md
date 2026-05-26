# Wine Advocate (Kelley) clippings — ingest layer

Drop one `.md` file per Wine Advocate article here. Use the Obsidian
Web Clipper. Same shape as `raw/clippings/vinous/`.

## Why "Kelley" specifically

The vault tracks William Kelley's coverage of Burgundy / Bordeaux /
Champagne / Mosel — that's the slice Evan reads. Other Wine Advocate
critics aren't ingested here; if a clipping is by someone else,
either skip it or set `critic:` accurately so downstream filters can
exclude.

Note: there is already a `raw/berserkers/William_Kelley/` directory
with 4,727 of Kelley's Berserkers forum posts. That's the *community
signal* layer (informal). This directory is for the *editorial signal*
(Wine Advocate publication). They're complementary, not duplicates.

## Filename convention

`<YYYY-MM-DD>__<producer-slug>__<short-title>.md`

## Required frontmatter

```yaml
---
type: wine_advocate_clipping
source: wine_advocate
producer_slug: armand_rousseau
critic: "William Kelley"
url: "https://www.wineadvocate.com/articles/..."
published: 2026-03-15
clipped: 2026-05-26
---
```

## How it lands

`scripts/compile_clippings.py wine_advocate --apply` writes a
`## Wine Advocate (Kelley)` section on the matched producer page,
distinct from the existing `## Berserkers (William Kelley)` section
that comes from the forum posts.
