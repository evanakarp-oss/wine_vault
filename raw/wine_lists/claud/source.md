---
type: wine_list_source
slug: claud
name: "Claud"
venue_type: restaurant
address: "90 E 10th St, New York, NY 10003"
source_url: "https://www.claudnyc.com/"
source_format: html
list_page: "https://www.claudnyc.com/wine/"
updated: 2026-05-27
---

# Claud

European bistro, East Village. Chase Sinzer + Joshua Pinsky. ~200-250 wine
selections, list rotates with the menu. French + American focus with
seasonal turnover.

Note: the restaurant is "Claud" (no e), not "Claude."

## Scrape method

Wine list rendered as HTML on `/wine/`. Cadence of list changes is somewhere
between "monthly" (per Resy/blog posts) and "with the menu" — weekly polling
is probably overkill but matches the rest of the pipeline.

`scrape_wine_lists.py claud` does:

1. GET `https://www.claudnyc.com/wine/`.
2. Save raw HTML to `raw/wine_lists/claud/raw/<YYYY-MM-DD>.html`.

## Format expectations

Need to verify against first scraped HTML. May be a flat HTML list, may be
embedded as a PDF, may be an image — Claud's site uses a custom CMS, not
Squarespace.

## Curation note

Claud's program leans Loire / Burgundy / natural — strong taste-filter
overlap. Rotating ~200 selections at a moderate cadence means new arrivals
each week should be a small, high-signal set.
