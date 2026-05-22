---
type: gap_view
source: raw/bowler/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
bowler_producers_total: 309
bowler_by_country:
  france: 114
  italy: 71
  usa: 44
  spain: 33
  germany: 16
  austria: 11
  argentina: 8
  chile: 8
  new_zealand: 2
  switzerland: 1
  portugal: 1
raeders_hits: 14
raeders_bottles: 17
updated: 2026-05-21
---

# Bowler × Raeder's — Inventory Cross-Check

Cross-checks the Bowler Wine portfolio (309 producers — pasted 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25.

**14 of 309 Bowler producers** at Raeder's (17 bottles). Modest hit rate (~5%) but high-quality matches — three Washington cult Cabs (Leonetti, Quilceda Creek, Figgins), Philip Togni Spring Mountain, Lopez de Heredia traditional Rioja, Arnoux-Lachaux's relative Chandon de Briailles, Foradori's neighbor Famille Isabel Ferrando in CdP.

## Confirmed at Raeder's

### France — Burgundy

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Chandon de Briailles *(flipped from Skurnik → Bowler this commit)* | Pernand-Vergelesses | Pernand-Vergelesses Les Vergelesses 1er Cru NV |

### France — Rhône (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Famille Isabel Ferrando *(Domaine Saint-Préfert)* | Châteauneuf-du-Pape | CdP Rouge 2020 — $115.99 |

### Italy (3 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Schiavenza | Piedmont — Serralunga | Barolo Vigna Broglio 2013 — $49.99 |
| Arianna Occhipinti | Sicily — Vittoria | Il Frappato Terre Siciliane 2021 — $53.99 |
| La Gerla | Tuscany — Montalcino | Brunello di Montalcino Riserva gli Angeli 2007 |

### Portugal — Douro (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Quinta do Infantado | Douro | Vintage Port 1992 — $99.99 |

### Spain (2 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Terroir al Limit | Priorat | Historic Red 2018 — $32.99 |
| Lopez de Heredia | Rioja | Viña Tondonia Reserva 2012 |

### USA — California (3 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Philip Togni Vineyard | Napa — Spring Mountain | Cab Napa 2018 ($189.99); 2019 ($189.99) |
| Mount Eden Vineyards | Santa Cruz Mountains | Pinot Noir Estate 2012 — $69.99 |

### USA — Oregon (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Nicolas-Jay | Willamette | L'Ensemble Pinot Noir 2021 — $79.99 |

### USA — Washington (5 bottles) — cult Walla Walla

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Leonetti | Walla Walla | Cab 2012 ($144.99); Reserve Cab 2005 ($169.99); Reserve Cab 2009 ($175.99) |
| Quilceda Creek | Columbia Valley | Cab Columbia Valley 2015 — **$209.99** |
| Figgins | Walla Walla | Estate Red 2012 — $139.99 |

## Resolution — earlier Rosenthal false positive

The Rosenthal cross-check ([[rosenthal_at_raeders]]) flagged "Luigi Ferrando" (Carema, Rosenthal) as having a candidate match at Raeder's for "Famille Isabel Ferrando Châteauneuf-du-Pape" — that was correctly excluded as a surname collision. The bottle is in fact **Bowler-imported** (Isabel Ferrando = Domaine Saint-Préfert in CdP). Loop closed.

## Notable Bowler stars NOT at Raeder's

Editorial-tier producers in the portfolio not appearing in the 2026-04-25 snapshot:

- **France — Burgundy**: Arnoux-Lachaux *(despite wiki page existing)*, Charles Lachaux, Baron Thénard, De Moor, Saumaize-Michelin, Voillot, Henri Magnien *(despite wiki page)*, Berthaut-Gerbet *(despite wiki page)*
- **France — Champagne**: Ulysse Collin, Tarlant, Bonnaire, Hugues Godmé, Le Brun Servenay
- **France — Loire**: Bellivière, Closel, Filliatreau, Pépière, Domaine Olga Raffault, Clos du Tue-Boeuf
- **France — Rhône**: Éric Texier, François Villard, Dumien-Serrette, Cristia
- **Italy — Piedmont**: Cascina 'Tavijn, Cascina degli Ulivi, Canonica, Iuli, Produttori del Gavi
- **Italy — Trentino**: Foradori
- **Italy — Friuli**: Radikon
- **Italy — Emilia-Romagna**: La Stoppa, Croci
- **Italy — Sicily**: Barraco, De Bartoli
- **Italy — Abruzzo**: Praesidium
- **Germany**: Koehler-Ruprecht, Immich-Batterieberg, Weingut Fürst
- **USA**: Birichino, Edmunds St. John, Drew Family Cellars, Andrew Will, Gramercy Cellars

## False positives caught and excluded

- *Beau!* (Beaujolais) → Beau Vigne (Napa Cab) — surname-token "beau" collision
- *Bellevue* (Bordeaux) → Bellevue Mondotte (different Saint-Émilion estate). Bowler's "Bellevue" likely a smaller Bordeaux property; the Mondotte bottles at Raeder's are von Neipperg's Premier Grand Cru Classé property.
- *Latour, Vincent* (Burgundy — Meursault) ≠ Château Latour (Pauillac First Growth) / Louis Latour (Burgundy négoce)
- *Val de Mer (Patrick Piuze)* ≠ Mer Soleil (California)
- *Lambert, Frederic* (Bowler Jura) ≠ Arnaud Lambert (Loire — Grand Cru Selections)
- *Martin, Yves* (Loire) ≠ Lingot Martin (Bugey sparkling)
- *Müller, Stefan* (Saar) ≠ Müller-Catoir (Pfalz) / Eugen Müller — different German Müller estates
- *Domaine Eden* (Mount Eden's second label) — the matching bottle is from Mount Eden Vineyards proper, counted under that entry
- *Johnson Family* (CA) ≠ Johnson Turnbull (different Napa winery)
- *White Rock Vineyards* (CA) ≠ Castle Rock / Chimney Rock — generic "rock" token
- *Day Wines* (OR) → "Rosé All Day" — generic "day" token

## Methodology

1. Source landed at `raw/bowler/portfolio_2026-05-21.md` (309 producers across 11 countries).
2. Cross-check script: normalize name, strip prefixes / generic given-name particles, parse "Lastname, Firstname" convention used by Bowler (e.g., "Latour, Vincent" → key on "Latour"). Require all remaining tokens ≥3 chars to appear as whole words in Raeder's `producer` field. Iterated GENERIC list — initial pass over-aggressively filtered cult surnames (Leonetti, Quilceda, Figgins), restored on second pass.
3. Hand-audit each match against the Bowler region tag and Raeder's cuvée.

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`.*
