---
type: view
updated: 2026-05-31
source: raeders/master_2026-04-25.csv
candidate_pool: 275
abv_in_vault: false
abv_source: web-verified (producer sites, Decanter, Wine Enthusiast, wine-searcher)
---

# Lowest-Alcohol Tuscan / Umbrian / Veneto Reds at Raeders

**Question:** Of the Tuscan, Umbrian, and Veneto red wines Raeders sells,
which bottlings have the lowest alcohol percentage?

## Data caveat (read first)

**The Raeders scrape carries no ABV field.** Neither
`raw/raeders/master_2026-04-25.csv` nor the per-bottle markdown frontmatter
records alcohol. The only "alcohol" strings anywhere in the 3,174 Raeders
files are inside a handful of critic tasting-note excerpts (e.g. a Catena
Malbec at "13.8% alcohol") — none of them Tuscan/Umbrian/Veneto reds.

So this ranking is **not** derived from vault data. I pulled the 275
Tuscan/Umbrian/Veneto reds Raeders carries, identified the
structurally-lowest-alcohol *styles* in that set, and **web-verified ABV**
for the candidates (producer sites / Decanter / Wine Enthusiast /
wine-searcher). ABV drifts ±0.5–1% by vintage; figures below are typical
recent releases, not the exact bottle Raeders has in stock.

## The floor is ~12.5%

Nothing in the Raeders Tuscan/Umbrian/Veneto **red** set sits below ~12.5%.
These appellations don't make sub-12% reds in any volume (you'd need
Bardolino for that — Raeders carries none here). The lowest verified
bottlings:

| Rank | Wine | Region | Typical ABV | Price | Raeders product_id |
|---|---|---|---:|---:|---|
| 1 | Tommasi — Rafaèl Valpolicella Classico Superiore | Veneto | **12.5%** | $19.99 | — |
| 1 | Badia a Coltibuono — Cetamura Chianti | Tuscany | **12.5%** | $9.99 | — |
| 3 | Dissegna — Refosco dal Peduncolo | Veneto | ~12.5–13% | $19.99 | dissegna…refosco |
| 3 | Buglioni — l'Imperfetto Valpolicella Cl. Sup. | Veneto | 13% | $19.99 | — |
| 3 | Monteraponi — Chianti Classico (2021) | Tuscany | 13% | — | — |
| 6 | Santi — Ventale Valpolicella Superiore | Veneto | 13–13.5% | $15.99 | — |
| 6 | Tedeschi — Capitel Nicalò Valpolicella Superiore | Veneto | 13.5% | $11.98 | — |
| 6 | Lamole di Lamole — Chianti Classico | Tuscany | 13.5% | $20.99 | — |
| 6 | Giuseppe Quintarelli — Primofiore | Veneto | 13.5–14% | $89.99 | — |

(None of these producers has a `wiki/producers/` page — Raeders is
inventory-only per CLAUDE.md, so there are no wikilinks to cite.)

## What is NOT the answer

The high-alcohol bulk of this set — explicitly the opposite of what was
asked — runs 14.5–16.5%: every **Amarone** (Allegrini, Bertani, Dal Forno,
Masi Costasera, Tommasi, Santi, Bussola, Cesari, Buglioni Riserva,
Quintarelli), **Ripasso**, **Brunello di Montalcino** / Riserva (Biondi-Santi,
Altesino, Casanova di Neri, Il Poggione, Gaja Pieve Santa Restituta, etc.),
**Sagrantino di Montefalco** (Arnaldo Caprai, Paolo Bea, Pardi ~14.5–15.5%),
and **Bolgheri** super-Tuscans (Sassicaia, Guado al Tasso, Ornellaia, Gaja
Ca'Marcanda).

## Curation-taste lens

If the goal is low alcohol *and* aligned to Evan's terroir-driven filter
(not the cheapest commercial Valpolicella), the two standouts are:

- **Monteraponi — Chianti Classico** (~13%): traditional, high-altitude
  Radda, organic — exactly the "sense of place + tension" axis.
- **Giuseppe Quintarelli — Primofiore** (~13.5%): the entry red from a
  legendary Veneto traditionalist; lowest-ABV way into the cellar.

## To get exact numbers

Alcohol would have to be scraped per-bottle from the live
`raederswine.com` product pages (or from the back label), then added as an
`abv:` field to the Raeders frontmatter schema. Not currently captured.
