---
type: importer
name: "Neal Rosenthal"
slug: neal_rosenthal
producer_count: 7
focus: ['Burgundy', 'Italy', 'Jura', 'Bordeaux']
notable_producers: ['Brovia', 'Château Le Puy', 'Jacques Puffeney', 'Michel Gahier', 'Elio Sandri']
updated: 2026-05-21
---

# Neal Rosenthal

**7 producer(s)** in the vault currently on the Rosenthal Wine Merchant portfolio (rosenthalwinemerchant.com/growers, pasted 2026-05-21). The full portfolio is 145 producers — France 86 / Italy 46 / Switzerland 5 / Austria 4 / Spain 4 — landed at `raw/rosenthal/portfolio_2026-05-21.md`. Cross-check against Raeder's: [[rosenthal_at_raeders|Rosenthal at Raeder's]] (8 producers, 13 bottles in stock).

| Producer | Country | Region | CSW | Cellar |
|---|---|---|---:|---:|
| [[brovia|Brovia]] | Italy | Piedmont | — | — |
| [[chateau_le_puy|Château Le Puy]] | France | Bordeaux | — | — |
| [[domaine_cheveau|Domaine Cheveau]] | France | Burgundy | — | — |
| [[domaine_lionnet|Domaine Lionnet]] | France | Rhône | — | — |
| [[elio_sandri|Elio Sandri]] | Italy | Piedmont | — | — |
| [[jacques_puffeney|Jacques Puffeney]] | France | Jura | — | — |
| [[michel_gahier|Michel Gahier]] | France | Jura | — | — |

## Pending verification — not on the current portfolio paste (1)

- [[bernhard_huber|Bernhard Huber]] *(Germany — Baden)* — currently tagged `importer_us: Neal Rosenthal` but not present on the 2026-05-21 paste. The pasted page contains no German producers at all, so this may be (a) Huber dropped from Rosenthal, (b) Huber moved importer, or (c) the page is country-filtered and Germany is on a separate view. **Verify before stripping the importer tag.**

## Producers at Raeder's not yet in the wiki (curation candidates)

Nine Rosenthal producers were confirmed at Raeder's in the 2026-04-25 snapshot but have no wiki page. See [[rosenthal_at_raeders]] for the full bottle-level list. Top candidates:

- Hubert Lignier *(Morey — 5 cuvées at Raeder's incl. Trilogie 2022, Volnay 2022, Gevrey 2022)*
- Paolo and Giampiero Bea *(Umbria — Montefalco; 5 cuvées incl. Sagrantino Pagliaro 2020, Cerrete 2019, Pipparello Riserva 2019 — cult biodynamic, call for price)*
- Domaine Harmand-Geoffroy *(Gevrey — Mazis-Chambertin GC 2020 $449.99)*
- Edmond Cornu & Fils *(Ladoix value — Chorey 2017, Bourgogne 2023)*
- Jean Chauvenet *(NSG 2019)*
- Georges Lignier & Fils *(Morey — Gevrey 2019)*
- Lucien Crochet *(Sancerre La Croix du Roy NV $39.99)*
- Château Pradeaux *(Bandol Rosé 2022 $29.99)*
- Domaine Bois de Boursan *(aged CdP Cuvée des Félix 2005 $89.99)*

*Hand-maintained 2026-05-21. `scripts/build_rollups.py` has a latent bug — `get_list()` regex only matches inline-flow YAML lists (`importer_us: ["X"]`) but the wiki mostly uses block style (`importer_us:\n- X`). Of the 8 producers above, only Bernhard Huber's tag happens to parse, so the script would currently surface only him. Fix in a follow-up to enable auto-regeneration.*
