---
type: wine_list_source
slug: estela
name: "Estela"
venue_type: restaurant
address: "47 East Houston St, New York, NY 10012"
source_url: "https://estelanyc.com/"
source_format: pdf
list_pdf: "https://hub.binwise.com/restaurant/estela/list/estela-wine-list.pdf"
updated: 2026-05-27
---

# Estela

Modern American, NoLita. Influential downtown program; wine list is curated by
the somm team and skews French (Loire, Burgundy, Jura/Savoie, Rhône) with
solid Italy + Spain + New World sections.

## Scrape method

Estela publishes their wine list as a PDF on **binwise.com** at a stable
URL (binwise is a restaurant wine-list management platform that auto-updates
the public PDF when the somm edits inventory in their system). The URL has
been stable for months — refetching it each week captures the latest state.

`scrape_wine_lists.py estela` does:

1. GET the binwise PDF URL.
2. Save to `raw/wine_lists/estela/raw/<YYYY-MM-DD>.pdf`.
3. Hash + record in `snapshot_<date>.json` metadata.

## Format expectations

Standard restaurant wine list PDF — sections by region/style, entries are
producer / cuvée / vintage / price. May include vintage-blank rows for NV
sparkling.

## Curation note

Estela's program is exactly your taste filter (Loire, biodynamic-leaning,
grower Champagne, Friuli). New arrivals here are high-priority for vault
gap analysis.
