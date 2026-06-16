---
type: xref_view
importer: "DNS Selections"
source_raeders_csv: "raw/raeders/master_2026-04-25.csv"
book_producer_count: 13
overlap_producer_count: 0
overlap_cuvee_count: 0
gap_producer_count: 13
min_fuzzy_score: 0.86
updated: 2026-06-13
---

# DNS Selections × Raeder's — Cross-Reference

**13** producers in the DNS Selections book tracked in the vault. **0** (0%) have a current presence at Raeder's, covering **0** cuvée/vintage listings.

_Source: `raw/raeders/master_2026-04-25.csv` (matched by canonical name; min fuzzy score = 0.86). Cross-references are by `importer_us` on the vault producer pages, not a direct lookup of the live importer book._

## Overlap — at Raeder's (0 producers, 0 cuvées)

_No DNS Selections producers currently at Raeder's._

## Gaps — in book, not at Raeder's (13 producers)

| Producer | Country | Region |
|---|---|---|
| [[benoit_ente|Benoît Ente]] | France | Burgundy |
| [[emmanuel_rouget|Emmanuel Rouget]] | France | Burgundy |
| [[patrick_piuze|Patrick Piuze]] | France | Burgundy |
| [[perrot_minot|Perrot-Minot]] | France | Burgundy |
| [[domaine_economou|Domaine Economou]] | Greece | Crete |
| [[domaine_de_kalathas|Domaine de Kalathas]] | Greece | Cyclades |
| [[domaine_glinavos|Domaine Glinavos]] | Greece | Epirus |
| [[domaine_nerantzi|Domaine Nerantzi]] | Greece | Macedonia |
| [[domaine_tatsis|Domaine Tatsis]] | Greece | Macedonia |
| [[troupis|Troupis Winery]] | Greece | Peloponnese |
| [[hatzidakis|Hatzidakis Winery]] | Greece | Santorini |
| [[koutsogiannopoulos|Koutsogiannopoulos Winery]] | Greece | Santorini |
| [[case_paolin|Case Paolin]] | Italy | Veneto |

## Method

1. Filter `wiki/producers/*.md` by `importer_us` ∋ `DNS Selections`.
2. For each producer, fuzzy-match the canonical name (NFKD ASCII-fold, strip `Domaine`/`Château`/`Weingut` prefixes, lowercase) against the producer column of `raw/raeders/master_2026-04-25.csv`.
3. Matches with score ≥ 0.86 are treated as a single producer.
4. Regenerate with `python scripts/build_importer_raeders_xref.py "DNS Selections" --apply`.

_This view is a snapshot — Raeders inventory rotates. Re-scrape via `scripts/scrape_raeders.py` + `scripts/parse_raeders_html.py` and re-run to refresh._
