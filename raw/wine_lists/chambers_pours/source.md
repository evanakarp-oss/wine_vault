---
type: wine_list_source
slug: chambers_pours
name: "Chambers Street Wines — Weekly Pour List"
venue_type: retail_pour
address: "148 Chambers St, New York, NY 10007"
source_url: "https://www.chambersstwines.com/"
source_format: pdf
list_page: "https://www.chambersstwines.com/"  # PDF link is embedded; URL changes weekly
last_known_pdf: "https://static1.squarespace.com/static/68ccbdaa5c055c4d4f97ede3/t/6a04da2ce3a26174991d00a2/1778702892564/WINE+LIST+5.8+%28special+pours+5.13%29.pdf"
updated: 2026-05-27
---

# Chambers Street Wines — Weekly Pour List

What's open and pouring at the Chambers Street shop in a given week.
Distinct from the **CSW article catalog** (`raw/csw/markdown/`) — that's
editorial content; this is the actual by-the-glass + open-bottle inventory.

## Scrape method

The PDF is hosted on Squarespace at a `static1.squarespace.com/static/.../`
URL that changes whenever the file is replaced. The stable entry point is
the Chambers Street homepage, where the PDF is linked (typically labeled
"This Week's Wine List" or similar).

`scrape_wine_lists.py chambers_pours` does:

1. GET `https://www.chambersstwines.com/`
2. Search the HTML for the first `static1.squarespace.com/.../WINE+LIST*.pdf`
   URL.
3. Download to `raw/wine_lists/chambers_pours/raw/<YYYY-MM-DD>.pdf`.

If step 2 fails (page structure changed), drop the PDF in
`raw/wine_lists/chambers_pours/raw/<YYYY-MM-DD>.pdf` manually and run
`parse_wine_list.py chambers_pours` directly.

## Format expectations

Per the file naming pattern (`WINE LIST 5.8 (special pours 5.13).pdf`) the
list is dated by week and includes a "special pours" callout. Sections
probably group by region. Entries are likely producer / cuvée / vintage /
price lines. Confirm against the first scraped PDF.

## Curation note

Chambers' pour list reflects what their team finds compelling enough to open
this week — high signal for an Evan-curation match. Surface even one-off
additions (especially aged Champagne, biodynamic German, Friuli/Piedmont).
