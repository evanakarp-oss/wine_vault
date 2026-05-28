---
type: raw_source
source: veritas_wines
url: https://veritaswine.com
harvested: 2026-05-28
method: websearch_snippets
---

# Veritas Wines — Source Notes

**Veritas Wines** (California, founded 1989) is a fine-wine importer and
distributor with a portfolio across France, Italy, Germany, Switzerland and
the USA. Signature focus on family-run estates, organic / biodynamic /
natural farming. Wholesale distribution in California, Nevada, Colorado,
Arizona and New Mexico; partner network in New York.

## Harvest method (2026-05-28)

The live site (`veritaswine.com`) blocks automated fetches with HTTP 403
across all paths tested from the Claude Code on the web sandbox, including:

- `/about/`, `/producers/`, `/growers-by-region/`
- `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml`,
  `/producer-sitemap.xml`
- Wayback Machine, Google cache
- Both raw curl and the WebFetch tool

Producer enumeration was done via WebSearch (Google) snippets against the
domain (`site:veritaswine.com inurl:producer …`) with ~25 targeted queries
covering each region + varietal + farming-style facet. This captures
producers that appear in Google's index — likely the majority of an active
catalog page but not guaranteed exhaustive.

## What's here

- `producers.csv` — harvested portfolio. Columns: slug, name, country,
  region, sub_region, url, notes.
- This file: provenance + method.

## Re-harvest

When veritaswine.com is reachable from your local network (the sandbox
restriction does not apply to direct browser access), the polite pattern
is to mirror `scripts/scrape_argentina_reloaded.py`:

1. fetch `/growers-by-region/`, parse links to `/producer/<slug>/`
2. fetch each producer page with a 1.5s delay
3. cache HTML to `raw/veritas/html/<slug>.html`
4. compile to `producers.csv` + per-page metadata

That gives an authoritative list and the body text for each producer page.

## Open follow-up

The vault stub pages created from this harvest carry
`_sources: ["veritas_websearch_2026-05-28"]` and have minimal bodies.
After a local re-scrape, run a `compile_veritas.py` pass to enrich each
producer page with the actual estate description, hectares, farming
certification specifics, sub-region precision, and winemaker name —
following the existing CSW / Roscioli enrichment pattern.
