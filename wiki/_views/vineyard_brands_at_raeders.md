---
type: gap_view
source: raw/vineyard_brands/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
vineyard_brands_producers_total: 127
raeders_hits: 9
raeders_bottles: 19
updated: 2026-05-21
---

# Vineyard Brands × Raeder's — Inventory Cross-Check

Cross-checks the Vineyard Brands portfolio (127 producers — pasted 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25.

**9 of 127 VB producers** at Raeder's (19 bottles in stock) — modest count, but **one of the headline bottles is the 2nd most expensive in the entire Raeder's catalog**: Château Pétrus 1967 at $3,499.99.

## Headline bottles

- **Château Pétrus Pomerol 1967** — **$3,499.99** *(2nd highest in Raeder's after DRC Corton-Charlemagne 2022 $4,999.99)*
- **Château La Fleur-Pétrus Pomerol 2018** — **$1,699.99**
- Château La Fleur-Pétrus Pomerol 2016 — $799.99
- Château de Beaucastel CdP 1999 — $599.99
- Henri Boillot Meursault Genevrières 2023 — $319.99 *(note: Henri Boillot is NOT on the VB paste — only Jean-Marc Boillot — so this bottle is misattributed by the matcher; see "False positives" below)*
- Ponsot Morey-St-Denis Cuvée des Alouettes 2016 — $279.99
- Château Beaucastel CdP 1989 — $239.99

## Confirmed at Raeder's

### France — Bordeaux (Right Bank — Pomerol)

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Pétrus + Château La Fleur-Pétrus *(JP Moueix portfolio)* | Pomerol | **7 bottles** — Château Pétrus 1967 ($3,499.99); Château La Fleur-Pétrus 2018 ($1,699.99), 2016 ($799.99), 2017, 2020, 2022 |

### France — Rhône (Châteauneuf)

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Famille Perrin / Château de Beaucastel | CdP | 4 bottles — Château Beaucastel CdP 1989 ($239.99), 1999 ($599.99); Château de Beaucastel CdP 2021 ($99.99), 2022 |

### France — Burgundy

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Ponsot *(Domaine + Laurent — split brand)* | Morey-St-Denis | Morey-St-Denis Cuvée des Alouettes 2016 — $279.99 |
| Henri Gouges | Nuits-Saint-Georges | Domaine Henri Gouges NSG 2017 — $79.99 |
| Thibault Liger-Belair | NSG | NSG La Charmotte 2019 |
| Jean-Marc Boillot | Beaune | Beaune 1er Cru Épenottes 2020 |

### France — Loire / Languedoc

| VB Producer | Region | Raeder's listings |
|---|---|---|
| J. de Villebois | Loire — Pouilly-Fumé | "Les Silex Blancs" Pouilly-Fumé 2023 — $59.99 |
| Hecht & Bannier | Languedoc | Minervois 2015 ($20.99); Côtes de Provence Rosé NV ($18.99) |

### Italy — Friuli

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Gradis'ciutta | Friuli — Collio | Ribolla Gialla 2020 — $22.99 |

### USA — California

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Forman Vineyard | Napa | Cabernet Sauvignon Napa 2016 |

## Burgundy gap analysis — partial close

Of the 5 priority importers identified in [[burgundy_gap_analysis]], Vineyard Brands closed **1 of the 4 predicted Burgundy items**:

| Predicted producer | On VB paste? | Resolution |
|---|---|---|
| **Ponsot** | ✓ YES | Confirmed VB. Morey Alouettes 2016 $279.99. |
| **Ramonet** *(9 bottles incl. Bâtard-Montrachet GC 2020 $1,299.99 — biggest single-producer gap)* | ✗ NO | Still unidentified. Revise prediction — likely **Becky Wasserman** or **Mosaic Wine Imports**. |
| **Henri Boillot** *(Meursault Genevrières $319.99)* | ✗ NO (only Jean-Marc Boillot on VB) | Still unidentified. |
| **Camille Giroud** *(Morey 1er Clos des Godelles 2019 $99.99)* | ✗ NO | Still unidentified. |

Additional unattributed Burgundy that's still open after WD + VB:
- Joseph Drouhin, A.F. Gros, William Fèvre — predicted **MMD**
- Louis Jadot, Louis Latour — predicted **Kobrand**
- Comte Georges de Vogüé, Dujac, Dugat-Py, Geantet-Pansiot, Niellon, Lorenzon — predicted **Becky Wasserman**
- Ramonet, Henri Boillot, Camille Giroud — revised prediction TBD

## False positives caught and excluded

- *Bernier* (VB Loire) → Larmandier-Bernier (Champagne — Polaner) — surname collision
- *Morey, Vincent & Sophie* (VB Chassagne) → Pierre Morey (Meursault) — different Morey family member
- *Boillot, Jean-Marc* (VB) matched Henri Boillot ($319 Meursault) and Lucien Boillot (9 bottles — KL). Henri Boillot is NOT on VB; Jean-Marc's only true match is Beaune 1er Cru Épenottes 2020. Lucien correctly attributed to KL.
- *Ernesto Catena Vineyards* (VB Argentina) → Bodega Catena Zapata (different family branch, different importer — likely Winebow)

## Methodology

1. Source landed at `raw/vineyard_brands/portfolio_2026-05-21.md` (127 producers).
2. Cross-check script: normalize name, handle "LASTNAME, FIRSTNAME" comma format (key on Lastname).
3. Second-pass spot check for "FAMILLE PERRIN, CHÂTEAU DE BEAUCASTEL" pattern caught the 4 Beaucastel bottles that the initial pass missed (initial pass only used "perrin", which is too generic).
4. Hand-audit against region tags and Raeder's cuvée.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`.*
