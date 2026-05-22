---
type: importer
name: "Bowler"
slug: bowler
producer_count: 15
focus: ['Burgundy', 'Champagne', 'Piedmont', 'Mosel', 'Rhône']
notable_producers: ['Arnoux-Lachaux', 'Chandon de Briailles', 'Clemens Busch', 'Berthaut-Gerbet', 'Ployez-Jacquemart']
updated: 2026-05-21
---

# Bowler

**15 producer(s)** in the vault currently on the Bowler Wine portfolio (bowlerwine.com producer index, pasted 2026-05-21). The full portfolio is 309 producers across France 114 / Italy 71 / USA 44 / Spain 33 / Germany 16 / Austria 11 / Argentina 8 / Chile 8 / New Zealand 2 / Switzerland 1 / Portugal 1 — landed at `raw/bowler/portfolio_2026-05-21.md`. Cross-check against Raeder's: [[bowler_at_raeders|Bowler at Raeder's]] (14 producers, 17 bottles in stock).

| Producer | Country | Region | CSW | Cellar |
|---|---|---|---:|---:|
| [[arnoux_lachaux|Arnoux-Lachaux]] | France | Burgundy — Vosne-Romanée | — | — |
| [[berthaut-gerbet|Berthaut-Gerbet]] | France | Burgundy — Fixin | — | — |
| [[bruna|Bruna]] | Italy | Liguria | — | — |
| [[cara_sur|Cara Sur]] | Argentina | San Juan | — | — |
| [[carmelo_patti|Carmelo Patti]] | Argentina | Mendoza | — | — |
| [[chandon_de_briailles|Chandon de Briailles]] | France | Burgundy — Pernand | — | — |
| [[clemens_busch|Clemens Busch]] *(+ Theise co-tag)* | Germany | Mosel | — | — |
| [[clos_de_la_roilette|Clos de la Roilette]] | France | Beaujolais — Fleurie | — | — |
| [[desvignes|Desvignes]] | France | Beaujolais — Morgon | — | — |
| [[fratelli_alessandria|Fratelli Alessandria]] | Italy | Piedmont — Verduno | — | — |
| [[magnien|Henri Magnien]] | France | Burgundy — Gevrey | — | — |
| [[piane|Casa Coste Piane]] | Italy | Veneto — Prosecco | — | — |
| [[pielihueso|Pielihueso]] | Argentina | San Juan | — | — |
| [[ployez_jacquemart|Ployez-Jacquemart]] | France | Champagne | — | — |
| [[steinmetz|Günther Steinmetz]] | Germany | Mosel | — | — |

## Tag corrections in this commit

- **Chandon de Briailles** — flipped `importer_us: Skurnik` → `Bowler`. The producer appears on the Bowler 2026-05-21 paste; not on any of the other five paste sources (KL, Rosenthal, Skurnik, GCS, Polaner).
- **Clemens Busch** — flipped `importer_us: ["Skurnik", "Theise"]` → `["Bowler", "Theise"]`. Same pattern — Bowler paste lists Clemens Busch, Skurnik paste does not. Theise tag preserved (Theise was not pasted as a source yet, so leave intact).

## Producers at Raeder's not yet in the wiki (curation candidates)

See [[bowler_at_raeders]] for the full bottle-level list. Top by stock and editorial fit:

- **Leonetti** *(Washington — 3 bottles incl. Cab 2012 $144.99, Reserve Cab 2005 $169.99, 2009 $175.99 — cult Walla Walla)*
- **Quilceda Creek** *(Washington — Cab Columbia Valley 2015 $209.99 — cult)*
- **Figgins** *(Washington — Estate Red 2012 $139.99)*
- **Philip Togni** *(California — Cab Napa 2018 $189.99, 2019 $189.99 — cult Spring Mountain)*
- **Lopez de Heredia** *(Rioja — Viña Tondonia Reserva 2012 — cult traditional Rioja)*
- **Mount Eden Vineyards** *(California — Pinot Noir Santa Cruz Mountains 2012 $69.99)*
- **Famille Isabel Ferrando** *(Rhône — Domaine Saint-Préfert; CdP Rouge 2020 $115.99 — RESOLVES the false positive flagged on [[rosenthal_at_raeders]])*
- **Schiavenza** *(Piedmont — Barolo Vigna Broglio 2013)*
- **La Gerla** *(Tuscany — Brunello Riserva gli Angeli 2007)*
- **Arianna Occhipinti** *(Sicily — Il Frappato Terre Siciliane 2021)*
- **Quinta do Infantado** *(Douro — Vintage Port 1992)*
- **Terroir al Limit** *(Priorat — Historic Red 2018)*
- **Nicolas-Jay** *(Oregon — L'Ensemble Pinot Noir 2021)*

*Hand-maintained 2026-05-21. `scripts/build_rollups.py` will not surface most of these (block-style YAML bug). Fix in a follow-up.*
