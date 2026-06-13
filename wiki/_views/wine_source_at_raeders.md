---
type: gap_view
source: raw/wine_source/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
wine_source_producers_captured: 12
raeders_hits: 1
raeders_bottles: 3
note: "Source is the 'Selection' subset visible in a screenshot of winesourcestore.us; full 'Our Portfolio' section was below the fold and not pasted. Treat as partial."
updated: 2026-05-21
---

# Wine Source × Raeder's — Inventory Cross-Check (partial)

Cross-checks the **12 producers visible on the Wine Source "Selection" page** (winesourcestore.us screenshot, 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25. The page has an "Our Portfolio" section below the fold that was not captured — this view is partial.

**1 of 12 visible Wine Source producers** has bottles at Raeder's (3 total). Small sample but the hit is a major one — Yann Durieux's Gevrey-Chambertin Grand Cru.

## Confirmed at Raeder's

### Burgundy (3 bottles)

| Wine Source Producer | Region | Raeder's listings |
|---|---|---|
| Yann Durieux *(project name "Recrue des Sens" — Raeder's stores as "Yann Durieux")* | Hautes-Côtes de Nuits | Gevrey-Chambertin **Grand Cru** 2020 — **$499.99**; La Gouzotte Rouge 2021 — $119.99; Love And Pif Blanc 2021 — $74.99 |

## Wine Source Selection producers NOT at Raeder's (11)

- Domaine Prieuré-Roch *(Vosne-Romanée — cult; absence is notable, would be high-priority)*
- Domaine Florence Cholet
- Aline Beauné
- Fanny Sabre *(Beaune — wiki page now tagged `importer_us: Wine Source`)*
- Domaine Jobard-Morey
- Pascal Robin
- Domaine des Mapliers
- Domaine du Clos des Fées *(Roussillon — Hervé Bizeul; starred on the source page)*
- Champagne Rodez *(Ambonnay — "Auteur de Champagne")*
- Champagne Jacques Picard *("Artisan Vigneron")*
- Champagne Jérôme Blin

## False positives caught and excluded

- *Aline Beauné* (Burgundy producer) → "Hospices de Beaune" auction lots — surname collision on "Beaune"

## Methodology

1. Source captured from a screenshot of winesourcestore.us/selection (12 visible logos). The site is blocked by the remote execution environment's network policy, so the full portfolio could not be fetched.
2. Cross-check script: same normalization + whole-token matching as previous importer views.
3. Initial pass missed Yann Durieux because "Yann Durieux (Recrue des Sens)" tokenized to require "recrue" and "sens", but Raeder's stores plain "Yann Durieux". Source file updated to record the plain name; second pass caught the match.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`. Partial — re-paste from the "Our Portfolio" section of winesourcestore.us to extend.*
