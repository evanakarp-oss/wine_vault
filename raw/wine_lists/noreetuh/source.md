---
type: wine_list_source
slug: noreetuh
name: "Noreetuh"
venue_type: restaurant
address: "128 First Ave, New York, NY 10009"
source_url: "https://www.noreetuh.com/"
source_format: html
list_page: "https://www.noreetuh.com/menu"
updated: 2026-05-27
---

# Noreetuh

Modern Hawaiian, East Village. Wine list by GM/co-owner Jin Ahn — ~300
selections, "strong representation from France and Germany." Award-winning,
high-density list. Corkage waived on Sundays.

## Scrape method

The full menu page (which includes the wine list) lives at
`noreetuh.com/menu`. Squarespace-hosted. Their own site notes that the
listed selections are "representative" and "subject to change" — meaning
the page may not show the *full* 300-bottle list. Worth verifying:

1. First scrape: download the HTML; count entries.
2. If << 300, ping Jin or scrape the Resy/binwise mirror if one exists.

`scrape_wine_lists.py noreetuh` does:

1. GET `https://www.noreetuh.com/menu`.
2. Save raw HTML to `raw/wine_lists/noreetuh/raw/<YYYY-MM-DD>.html`.

## Format expectations

If it's the full list, expect heavy France (Champagne, Burgundy, Loire,
Alsace) and Germany (Mosel, Rheingau riesling). Otherwise it may be a
"selected highlights" subset that's still useful but won't reflect deep
inventory.

## Curation note

Aged German riesling + grower Champagne = direct Evan-taste overlap. The
restaurant's wine reputation is partly built on the depth of Jin's Mosel
section — even a tight subset of new arrivals is high-signal.
