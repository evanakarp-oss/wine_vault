---
type: xref_view
importer: "Skurnik"
source_raeders_csv: "raw/raeders/master_2026-04-25.csv"
book_producer_count: 16
overlap_producer_count: 1
overlap_cuvee_count: 1
gap_producer_count: 15
min_fuzzy_score: 0.86
updated: 2026-06-13
---

# Skurnik × Raeder's — Cross-Reference

**16** producers in the Skurnik book tracked in the vault. **1** (6%) have a current presence at Raeder's, covering **1** cuvée/vintage listings.

_Source: `raw/raeders/master_2026-04-25.csv` (matched by canonical name; min fuzzy score = 0.86). Cross-references are by `importer_us` on the vault producer pages, not a direct lookup of the live importer book._

## Overlap — at Raeder's (1 producers, 1 cuvées)

| Producer | Region | Cuvées | Price range | Top vintages | Match |
|---|---|---:|---|---|---|
| [[chandon_de_briailles|Chandon de Briailles]] | Burgundy | 1 | — | NV | exact |

## Cuvée-level detail

### [[chandon_de_briailles|Chandon de Briailles]] — Burgundy

| Cuvée | Vintage | Size | Price | Scores |
|---|---:|---|---:|---|
| [Pernand Vergelesses Les Vergelesses 1er Cru](https://www.raederswine.com/wines/Domaine-Chandon-De-Briailles-Pernand-Vergelesses-Les-Vergelesses-1er-Cru-w1064616ax) | NV | 750ml | — | — |

## Gaps — in book, not at Raeder's (15 producers)

| Producer | Country | Region |
|---|---|---|
| [[domaine_trapet|Domaine Trapet]] | France | Burgundy |
| [[aj_adam|A.J. Adam]] | Germany | Mosel |
| [[clemens_busch|Clemens Busch]] | Germany | Mosel |
| [[hofgut_falkenstein|Hofgut Falkenstein]] | Germany | Mosel |
| [[immich-batterieberg|Immich-Batterieberg]] | Germany | Mosel |
| [[knebel|Knebel]] | Germany | Mosel |
| [[peter_lauer__weingut_lauer|Peter Lauer / Weingut Lauer]] | Germany | Mosel |
| [[van_volxem|Van Volxem]] | Germany | Mosel |
| [[vollenweider|Vollenweider]] | Germany | Mosel |
| [[weiser_kunstler|Weiser-Künstler]] | Germany | Mosel |
| [[willi_schaefer|Willi Schaefer]] | Germany | Mosel |
| [[zilliken|Zilliken]] | Germany | Mosel |
| [[donnhoff|Dönnhoff]] | Germany | Nahe |
| [[emrich_schonleber|Emrich-Schönleber]] | Germany | Nahe |
| [[schafer-frohlich|Schafer-Frohlich]] | Germany | Nahe |

## Method

1. Filter `wiki/producers/*.md` by `importer_us` ∋ `Skurnik`.
2. For each producer, fuzzy-match the canonical name (NFKD ASCII-fold, strip `Domaine`/`Château`/`Weingut` prefixes, lowercase) against the producer column of `raw/raeders/master_2026-04-25.csv`.
3. Matches with score ≥ 0.86 are treated as a single producer.
4. Regenerate with `python scripts/build_importer_raeders_xref.py "Skurnik" --apply`.

_This view is a snapshot — Raeders inventory rotates. Re-scrape via `scripts/scrape_raeders.py` + `scripts/parse_raeders_html.py` and re-run to refresh._
