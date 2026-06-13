---
type: gap_view
source: raw/banville/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
banville_producers_total: 59
banville_by_country:
  italy: 31
  france: 19
  germany: 2
  new_zealand: 2
  oregon: 2
  argentina: 1
  austria: 1
  slovenia: 1
raeders_hits: 12
raeders_bottles: 13
updated: 2026-05-21
---

# Banville × Raeder's — Inventory Cross-Check

Cross-checks the Banville Wine Merchants portfolio (59 producers — pasted 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25.

**12 of 59 Banville producers** at Raeder's (13 bottles in stock) — 20% hit rate, second-highest density after Grand Cru Selections. **Headline bottle: Domaine Jean-Jacques Confuron Romanée-Saint-Vivant Grand Cru 2016 — $899.99.**

## Confirmed at Raeder's

### France — Burgundy (Côte de Nuits high-end)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Jean-Jacques Confuron | Vosne-Romanée | Romanée-Saint-Vivant Grand Cru 2016 — **$899.99** |
| Domaine Odoul-Coquard | Morey-Saint-Denis | Vosne-Romanée 2021 — $179.99 |
| Meurgey-Croses *(also listed by Banville as "Pierre Meurgey")* | Mâconnais | St-Véran 2019 — $29.99 |

### France — Bordeaux / Provence (2 bottles)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Château du Gazin *(ambiguous — multiple Gazin properties)* | Bordeaux | Château Gazin Pomerol 1970 — $149.99 |
| Château l'Escarelle | Provence | Côtes de Provence Rosé NV |

### Argentina (1 bottle)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Andeluna | Mendoza | 1300 NV — $19.98 |

### Italy (7 bottles)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Tenuta di Trinoro | Tuscany — Sarteano | Le Cupole Rosso NV — $69.99 *(Andrea Franchetti)* |
| Parusso | Barolo | Barolo Perarmando 2017 — $59.99 |
| Tolaini | Tuscany — Chianti Classico | Valdisanti 2015; 2019 |
| Terlano *(at Raeder's as "Cantina Sociale Terlano")* | Alto Adige | Pinot Grigio Alto Adige NV |
| Illuminati | Abruzzo | Montepulciano d'Abruzzo Riparosso NV |
| Farina | Veneto/Lombardy | Lugana NV — $17.99 *(see Wildman correction below)* |

## Wildman correction — Farina

The Wildman cross-check ([[wildman_at_raeders]]) credited Bodegas Fariña (Toro, Spain) with the Raeder's "Farina | Lugana" bottle. That was a token collision — Lugana is Italian (Garda area), and the producer is **Banville's Farina**, not Wildman's Spanish Fariña. The Wildman view has been corrected; Farina (Italy) now sits properly under Banville.

## Notable Banville stars NOT at Raeder's

- **Markus Molitor** *(Mosel — cult Riesling)*
- Champagne Franck Pascal *(biodynamic)*
- Passopisciaro *(Etna — Franchetti)*
- Bassermann-Jordan *(Pfalz)*
- Léon Beyer *(Alsace)*
- Marc Sorrel *(Hermitage — wiki page exists, now tagged `importer_us: Banville`)*
- Ca' Viola *(Piedmont — Mascarello family)*
- Domaine Marc Morey et Fils *(Chassagne — NOTE: false positive earlier when this matched Pierre Morey; different producer)*
- Domaine Marjan Simčič *(Slovenia — cult Friuli-adjacent)*

## False positives caught and excluded

- *Domaine Marc Morey et Fils* (Banville Chassagne) ≠ Pierre Morey (Meursault) — different families
- *Cordero Mario Winery* (Banville Piedmont) ≠ Cordero di Montezemolo (different La Morra estate)
- *Maison Noir Wines* (Banville Oregon — André Hueston Mack) → generic "noir" token matched many Pinots
- *Vine & Supply* (Banville Oregon) → "Barossa Old Vine" — generic
- *Donatella Cinelli Colombini – Fattoria del Colle* → generic "del" token matched many "del" producers (Borgo, Aguila, Cerro, etc.)

## Existing wiki Banville pages

Only 1 of 59: [[marc_sorrel|Marc Sorrel]] (Hermitage). Tag added `importer_us: Banville` in this commit. Note Marc Sorrel does NOT appear at Raeder's in the 2026-04-25 snapshot — the wiki page exists from CSW write-ups.

## Methodology

1. Source landed at `raw/banville/portfolio_2026-05-21.md` (59 producers).
2. Cross-check script: standard normalization + whole-token matching.
3. Hand-audit against region tags and Raeder's cuvée — false positives noted above.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`.*
