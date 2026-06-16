---
type: xref_view
importer: "David Bowler Wine"
source_raeders_csv: "raw/raeders/master_2026-04-25.csv"
book_producer_count: 18
overlap_producer_count: 0
overlap_cuvee_count: 0
gap_producer_count: 18
min_fuzzy_score: 0.86
updated: 2026-06-13
---

# David Bowler Wine × Raeder's — Cross-Reference

**18** producers in the David Bowler Wine book tracked in the vault. **0** (0%) have a current presence at Raeder's, covering **0** cuvée/vintage listings.

_Source: `raw/raeders/master_2026-04-25.csv` (matched by canonical name; min fuzzy score = 0.86). Cross-references are by `importer_us` on the vault producer pages, not a direct lookup of the live importer book._

## Overlap — at Raeder's (0 producers, 0 cuvées)

_No David Bowler Wine producers currently at Raeder's._

## Gaps — in book, not at Raeder's (18 producers)

| Producer | Country | Region |
|---|---|---|
| [[clos_du_pavillon|Clos du Pavillon]] | France | Bordeaux |
| [[tarlant|Tarlant]] | France | Champagne |
| [[eric_texier|Eric Texier]] | France | Rhône |
| [[dr_g|Dr. G]] | Germany | Mosel |
| [[immich-batterieberg|Immich-Batterieberg]] | Germany | Mosel |
| [[staffelter_hof|Staffelter Hof / Jan Matthias Klein]] | Germany | Mosel |
| [[stefan_muller|Stefan Müller]] | Germany | Mosel |
| [[gunderloch|Gunderloch]] | Germany | Rheinhessen |
| [[a_vita|'A Vita]] | Italy | Calabria |
| [[contrada_salandra|Contrada Salandra]] | Italy | Campania |
| [[criante|Criante]] | Italy | Tuscany |
| [[ilbioselvatico|ilBioSelvatico]] | Italy | Tuscany |
| [[pedralonga|Pedralonga]] | Spain | Galicia |
| [[bebame|Bebame]] | United States | California |
| [[birichino|Birichino]] | United States | California |
| [[bucklin|Bucklin]] | United States | California |
| [[day_wines|Day Wines]] | United States | Oregon |
| [[hamacher_wines|Hamacher Wines]] | United States | Oregon |

## Method

1. Filter `wiki/producers/*.md` by `importer_us` ∋ `David Bowler Wine`.
2. For each producer, fuzzy-match the canonical name (NFKD ASCII-fold, strip `Domaine`/`Château`/`Weingut` prefixes, lowercase) against the producer column of `raw/raeders/master_2026-04-25.csv`.
3. Matches with score ≥ 0.86 are treated as a single producer.
4. Regenerate with `python scripts/build_importer_raeders_xref.py "David Bowler Wine" --apply`.

_This view is a snapshot — Raeders inventory rotates. Re-scrape via `scripts/scrape_raeders.py` + `scripts/parse_raeders_html.py` and re-run to refresh._
