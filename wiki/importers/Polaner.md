---
type: importer
name: "Polaner"
slug: polaner
producer_count: 19
focus: ['Burgundy', 'Piedmont', 'Champagne', 'California', 'Rhône']
notable_producers: ['Giacomo Conterno', 'Roagna', 'Larmandier-Bernier', 'Domaine Trapet', 'Arnot-Roberts']
updated: 2026-05-21
---

# Polaner

**19 producer(s)** in the vault currently on the Polaner Selections portfolio (polanerselections.com producer index, pasted 2026-05-21). The full portfolio is 323 producers across France 131 / Italy 77 / USA 57 / Spain 32 / Portugal 15 / Argentina 6 / Chile 3 / Hungary 1 / Austria 1 — landed at `raw/polaner/portfolio_2026-05-21.md`. Cross-check against Raeder's: [[polaner_at_raeders|Polaner at Raeder's]] (24 producers, 58+ bottles in stock — heaviest absolute bottle count among the five importers cross-checked so far).

| Producer | Country | Region | CSW | Cellar |
|---|---|---|---:|---:|
| [[agrapart|Agrapart]] | France | Champagne | — | — |
| [[arnot-roberts|Arnot-Roberts]] | USA | California | — | — |
| [[boulay|Gérard Boulay]] | France | Loire — Sancerre | — | — |
| [[cascina_delle_rose|Cascina delle Rose]] | Italy | Piedmont — Barbaresco | — | — |
| [[collestefano|ColleStefano]] | Italy | Marche | — | — |
| [[domaine_boisson|Domaine Boisson]] | France | Burgundy — Meursault | — | — |
| [[domaine_de_montille|Domaine de Montille]] *(also tagged Kysela — see note)* | France | Burgundy — Volnay | — | — |
| [[domaine_trapet|Domaine Trapet]] | France | Burgundy — Gevrey | 4 | — |
| [[franck_balthazar|Franck Balthazar]] | France | Rhône — Cornas | 5 | — |
| [[georges_glantenay|Georges Glantenay]] | France | Burgundy — Volnay | — | — |
| [[giacomo_conterno|Giacomo Conterno]] | Italy | Piedmont — Barolo | — | — |
| [[goisot|Goisot]] | France | Burgundy — Saint-Bris | — | — |
| [[julien_sunier|Julien Sunier]] | France | Beaujolais | — | — |
| [[larmandier_bernier|Larmandier-Bernier]] | France | Champagne | — | — |
| [[montenidoli|Montenidoli]] | Italy | Tuscany | — | — |
| [[roagna|Roagna]] | Italy | Piedmont — Barbaresco/Barolo | — | — |
| [[sigaut|Sigaut]] | France | Burgundy — Chambolle | — | — |
| [[trediberri|Trediberri]] | Italy | Piedmont — Barolo | — | — |
| [[vincent_paris|Vincent Paris]] | France | Rhône — Cornas | — | — |

## Pending verification — tagged Polaner but not on the 2026-05-21 paste (8)

These wiki producers carry `importer_us: Polaner` from earlier research but do NOT appear on the freshly-pasted Polaner portfolio. May be (a) Polaner dropouts, (b) tag was wrong originally, or (c) paste gap. Following the Kermit Lynch precedent (where 8 of 10 wiki tags turned out to be stale once the source was verified), recommend treating as candidates for strip after a brief sanity-check:

- [[jean-claude_rateau]] *(Burgundy — Beaune)*
- [[gilles__jean__maxime_lafouge]] *(Burgundy — Auxey-Duresses)*
- [[domaine_de_la_chevalerie]] *(Loire — Bourgueil)*
- [[ceretto]] *(Piedmont — Barolo/Barbaresco)*
- [[produttori_del_barbaresco]] *(Piedmont — Barbaresco co-op)*
- [[rapet_pere_et_fils]] *(Burgundy — Pernand-Vergelesses)*
- [[jane_et_sylvain]] *(Loire — Anjou)*
- [[stephane_guion]] *(Loire — Bourgueil)*

## Tag corrections in this commit

- **[[domaine_baudry|Domaine Baudry]]** *(Chinon)* — flipped `importer_us: Polaner` → `Kermit Lynch`. New KL paste lists "Bernard Baudry" under Loire; Polaner paste has no Baudry.
- **[[franck_balthazar|Franck Balthazar]]** *(Cornas)* — added Polaner tag. Previously stripped from KL in earlier session; now confirmed on Polaner Rhône list (so the KL strip is fully resolved — Balthazar is Polaner-imported, not KL).
- **[[domaine_de_montille|Domaine de Montille]]** *(Volnay)* — added Polaner tag alongside existing Kysela. Polaner paste lists "De Montille"; possible that Polaner is the current importer and Kysela was prior. Flagged for verification.

## Producers at Raeder's not yet in the wiki (curation candidates)

See [[polaner_at_raeders]] for the full bottle-level list. Top by stock and reputation:

- **Carlisle** *(California — ~10 bottles, deep Zin coverage)*
- **Bedrock** *(California — 5 bottles incl. Pagani Ranch, Evangelho)*
- **Maybach** *(California — 5 bottles incl. Amoenus Cab 2017 $205.99)*
- **Walter Hansel** *(California Pinot — 3 bottles)*
- **Varner** *(California Chardonnay — 4 single-block bottles)*
- **Caterwaul** *(California Cab — 2)*
- **Rivers Marie** *(California Cab — 2)*
- **Oddero** *(Barolo Brunate, Vigna Rionda Riserva)*
- **Giuseppe Mascarello** *(Barolo Monprivato 2017 $249.99, Langhe Nebbiolo 2022)*
- **Paitin** *(Sorì Paitin Barbaresco VV 2000 $184.99)*
- **Francesco Rinaldi** *(Barolo Cannubi 2020)*
- **Felsina** *(Chianti Classico Berardenga)*
- **Montepeloso** *(Tuscany — Nardo, Eneo)*
- **Bussola** *(Amarone Classico 2013 $99.99)*
- **Descendientes de J. Palacios** *(Bierzo — Corullon, Petalos)*

*Hand-maintained 2026-05-21. `scripts/build_rollups.py` will not surface most of the 19 producers above (the wiki uses block-style `importer_us:\n- Polaner` YAML which the script's regex misses). Fix in a follow-up.*
