---
type: gap_view
source: raw/wasserman/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
wasserman_producers_total: 132
new_attributions: 3
co_importer_relationships: 13
updated: 2026-05-21
---

# Becky Wasserman × Raeder's — Inventory Cross-Check

Cross-checks the Becky Wasserman & Co. portfolio (132 producers — pasted 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25.

**Important context**: Wasserman is a Burgundy *brokerage*, not a pure US importer. Most producers on this list are co-represented with other US importer partners (Wildman, Bowler, GCS, Polaner, Skurnik). The output below distinguishes:
- **Newly resolved** — producers Wasserman attributes that weren't on any prior paste
- **Co-importer** — producers already attributed to other importers via prior pastes

Net new bottle attributions: **3** (Vogüé, Camille Giroud, Pierre Morey). Co-importer overlap: ~13 producers / ~20+ bottles.

## Newly resolved at Raeder's

### Burgundy — Côte d'Or (3 bottles)

| Wasserman Producer | Region | Raeder's listings |
|---|---|---|
| Comte Georges de Vogüé | Chambolle-Musigny | **Bonnes-Mares Grand Cru 2016 — $799.99** |
| Camille Giroud | Beaune négoce | Morey-St-Denis 1er Cru Clos des Godelles 2019 — $99.99 |
| Pierre Morey | Meursault | Bourgogne Aligoté 2023 — $38.99 |

## Co-importer relationships at Raeder's

These producers are on the Wasserman paste but their primary US importer was confirmed via earlier pastes. Treated as Wasserman brokerage, not new attribution. No producer page tag changes.

| Producer | Primary tag | Bottles |
|---|---|---|
| Sylvain Cathiard & Fils | Wildman | NSG Aux Thorey 2021 — $499.99 |
| Jacques-Frédéric Mugnier | Wildman | Clos de la Maréchale 1er Cru 2022 — $229.99 |
| Famille Ogereau | Wildman | Anjou Rouge Les Tailles 2019 — $29.99 |
| Jean-Baptiste Souillard | Wildman | Crozes-Hermitage Habrards 2017 — $55.99 |
| Domaine Chapel | GCS | Fleurie Charbonniers 2022 |
| Domaine des Croix | GCS | Beaune 1er Cru Cents Vignes 2022 |
| Comtes Lafon | GCS | Meursault Porusots 1er Cru 2022 — $469.99 |
| Arnaud Lambert | GCS | Saumur range — 3 bottles |
| Château des Quarts | GCS | Pouilly-Fuissé Clos des Quarts 2022 |
| Saisons (Bourgneuf 2nd label) | GCS | Pomerol 2023 — $59.99 |
| Héritiers du Comte Lafon | Skurnik | (Mâcon range) |
| François Mikulski | Skurnik | Hautes-Côtes de Beaune Chardonnay 2022/23 |
| Croix & Courbet | Bowler | Côtes du Jura 2022 — $45.99 |

## Burgundy gap analysis — only partial close

My [[burgundy_gap_analysis]] predicted Wasserman for 7 unattributed Burgundy producers. Only **1** verified:

| Predicted | On Wasserman? | Resolution |
|---|---|---|
| **Comte Georges de Vogüé** | ✓ YES | Confirmed Wasserman — $799.99 Bonnes-Mares 2016 |
| **Dujac** | ✗ NO | Still unidentified ($259) |
| **Dugat-Py** | ✗ NO | Still unidentified |
| **Geantet-Pansiot** | ✗ NO | Still unidentified |
| **Michel Niellon** | ✗ NO | Still unidentified |
| **Bruno Lorenzon** | ✗ NO | Still unidentified |
| **Ramonet** *(revised prediction)* | ✗ NO | Still unidentified |
| **Henri Boillot** | ✗ NO | Still unidentified |

So my predictions were largely wrong for Wasserman — the cult producers I thought might be brokered through Wasserman aren't. They're somewhere else (specialty importers).

## False positives caught and excluded

- *Comte Armand* (Wasserman Pommard) → Armand Rousseau (Wildman) / Armand de Brignac (Champagne) — pure surname collision
- *David Moreau* (Wasserman Santenay — has wiki page) → Moreau-Naudet (Chablis — GCS) — different producer
- *Paul Prieur & Fils* (Wasserman Sancerre) → Domaine Jacques Prieur (Wildman) — different producer
- *Brendan Stater-West* (Wasserman Loire — also on GCS) → Mark West / Mount West (California) — generic token

## Remaining Burgundy gap after WD + VB + Wasserman

Three Burgundy-specialist pastes done. Cult bottles still unidentified:

| Producer | Bottles | Max price |
|---|---:|---:|
| **Ramonet** | 9 | **$1,299.99** (Bâtard-Montrachet GC 2020) |
| Henri Boillot | 1 | $319.99 |
| Dujac | 1 | $259.99 |
| Geantet-Pansiot | 4 | $219.99 |
| Dugat-Py | 3 | $210.99 |
| Michel Niellon | 1 | $239.99 |
| Bruno Lorenzon | 2 | $99.99 |
| Hospices de Beaune | 2 | $199.99 |

**Best next pastes to try**:
- **Maisons Marques & Domaines** — would close Drouhin, A.F. Gros, William Fèvre
- **Kobrand** — Louis Jadot, Louis Latour
- **Joe Dressner / Louis-Dressner** — likely brokers Ramonet, Dugat-Py, Geantet-Pansiot
- **Mosaic Wine Imports** or **Roy Cloud** — possible for Niellon, Lorenzon, Henri Boillot

## Methodology

1. Source landed at `raw/wasserman/portfolio_2026-05-21.md` (132 producers, alphabetical A-Z structure).
2. Cross-check script: standard normalization + whole-token matching.
3. Hand-audit each match against Raeder's cuvée — flagged co-importer relationships separately from new attributions.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`.*
