---
type: wine_list_source
slug: peasant
name: "Peasant"
venue_type: restaurant
address: "194 Elizabeth St, New York, NY 10012"
source_url: "https://www.peasantnyc.com/"
source_format: html
list_page: "https://www.peasantnyc.com/menu/wine-list/"
updated: 2026-05-27
---

# Peasant

Wood-fired Italian, NoLita. Wine list is exclusively Italian producers
working biodynamic / sustainable / minimal-intervention. Strong overlap with
Evan's Piedmont/Friuli interest area.

## Scrape method

Wine list is rendered as HTML on the restaurant's site at
`/menu/wine-list/`. Squarespace-hosted; structure is reasonably stable.

`scrape_wine_lists.py peasant` does:

1. GET the wine list page.
2. Save raw HTML to `raw/wine_lists/peasant/raw/<YYYY-MM-DD>.html`.

If the page structure changes and `parse_wine_list.py` starts emitting
empty / malformed entries, inspect the saved HTML and update the parser
in `parse_wine_list.py::parse_peasant`.

## Format expectations

Section headers (likely region: Piedmont, Tuscany, Veneto, etc.) followed
by wine entries. Need to verify against first scraped HTML.

## Curation note

Italian-only and biodynamic-leaning = nearly 100% Evan-relevant. Even
small additions here are worth surfacing.
