---
type: xref_view
importer: "Zev Rovine Selections"
source_raeders_csv: "raw/raeders/master_2026-04-25.csv"
book_producer_count: 13
overlap_producer_count: 0
overlap_cuvee_count: 0
gap_producer_count: 13
min_fuzzy_score: 0.86
updated: 2026-06-13
---

# Zev Rovine Selections × Raeder's — Cross-Reference

**13** producers in the Zev Rovine Selections book tracked in the vault. **0** (0%) have a current presence at Raeder's, covering **0** cuvée/vintage listings.

_Source: `raw/raeders/master_2026-04-25.csv` (matched by canonical name; min fuzzy score = 0.86). Cross-references are by `importer_us` on the vault producer pages, not a direct lookup of the live importer book._

## Overlap — at Raeder's (0 producers, 0 cuvées)

_No Zev Rovine Selections producers currently at Raeder's._

## Gaps — in book, not at Raeder's (13 producers)

| Producer | Country | Region |
|---|---|---|
| [[meinklang|Meinklang]] | Austria | Burgenland |
| [[ewald_tscheppe_werlitsch|Ewald Tscheppe (Werlitsch)]] | Austria | Styria |
| [[maison_en_belles_lies|Maison en Belles Lies]] | France | Burgundy |
| [[alice_bouvot|Alice Bouvot (L'Octavin)]] | France | Jura |
| [[domaine_des_miroirs|Domaine des Miroirs]] | France | Jura |
| [[les_deux_terres|Les Deux Terres]] | France | Languedoc-Roussillon |
| [[les_tetes|Les Tètes]] | France | Languedoc-Roussillon |
| [[jean_pierre_robinot|Jean-Pierre Robinot]] | France | Loire |
| [[gregory_guillaume|Gregory Guillaume]] | France | Rhône |
| [[lammidia|Lammidia]] | Italy | Abruzzo |
| [[frank_cornelissen|Frank Cornelissen]] | Italy | Sicily |
| [[gabrio_bini|Gabrio Bini]] | Italy | Sicily |
| [[sikele|Sikelè]] | Italy | Sicily |

## Method

1. Filter `wiki/producers/*.md` by `importer_us` ∋ `Zev Rovine Selections`.
2. For each producer, fuzzy-match the canonical name (NFKD ASCII-fold, strip `Domaine`/`Château`/`Weingut` prefixes, lowercase) against the producer column of `raw/raeders/master_2026-04-25.csv`.
3. Matches with score ≥ 0.86 are treated as a single producer.
4. Regenerate with `python scripts/build_importer_raeders_xref.py "Zev Rovine Selections" --apply`.

_This view is a snapshot — Raeders inventory rotates. Re-scrape via `scripts/scrape_raeders.py` + `scripts/parse_raeders_html.py` and re-run to refresh._
