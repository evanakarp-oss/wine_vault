---
type: view
updated: 2026-07-22
question: "Are all producers in the Down to Earth (Panzer) portfolio ingested into the vault? What's missing?"
source: raw/dte/dte_portfolio_2026-03-25.sd.json (DTE SD portfolio object, recovered from robertpanzer@hotmail.com Gmail thread 2026-03-25) × wiki/producers/
---

# Down to Earth (Panzer) — Portfolio Coverage (2026-07)

Coverage audit of the full [[Down_to_Earth_Wines_Panzer|Down to Earth]] import
book against `wiki/producers/`. The portfolio source (the `SD` object that backs
Robert Panzer's JSX widget) previously lived only on Evan's local machine; it was
**recovered from Gmail** (Panzer's 2026-03-25 "DTE portfolio" email) and landed at
`raw/dte/dte_portfolio_2026-03-25.sd.json` — so DTE is now reproducible in-repo.

## Result

- **125 producers** in the portfolio (870 cuvée/vintage entries, France / Germany / Italy / Spain).
- **109 already had vault pages** (incl. Schäfer-Fröhlich under `schafer-frohlich`).
- **16 gaps → all onboarded 2026-07-22.** Every gap was squarely on-taste for a
  curated grower importer (grower Champagne, terroir Loire Chenin, Côte d'Or growers),
  so all 16 were created as seed pages (frontmatter + DTE cuvée/price table + a
  factual summary). None fabricates critic coverage.

### The 16 onboarded

| Producer | Region | Note |
|---|---|---|
| [[marie_courtin\|Marie Courtin]] | Champagne (Côte des Bar) | Cult biodynamic single-parcel grower, zero dosage |
| [[philippe_foreau\|Philippe Foreau]] | Loire (Vouvray) | Domaine du Clos Naudin — with Huet, the reference Vouvray |
| [[francois_chidaine\|François Chidaine]] | Loire (Montlouis) | Benchmark biodynamic Chenin (Montlouis + Vouvray) |
| [[vauversin\|Vauversin]] | Champagne (Côte des Blancs) | Oger grand cru Blanc de Blancs grower |
| [[philippe_lancelot\|Philippe Lancelot]] | Champagne (Côte des Blancs) | Cramant grower, low-dosage BdB |
| [[dehu\|Déhu]] | Champagne (Vallée de la Marne) | Meunier-led grower, Brut Nature + Coteaux rouge |
| [[legrand_latour\|Legrand-Latour]] | Champagne | Chalk-strata Brut Nature cuvées (Éocène, Lutétien) |
| [[philippe_gilbert\|Philippe Gilbert]] | Loire (Menetou-Salon) | Biodynamic Sauvignon + Pinot |
| [[domaine_fl\|Domaine FL]] | Loire (Savennières) | Savennières Chenin (ex-Chamboureau/Forges) |
| [[taupenot_merme\|Taupenot-Merme]] | Burgundy (Morey-St-Denis) | Grand-cru spread: Charmes, Mazoyères, Corton |
| [[albert_morot\|Albert Morot]] | Burgundy (Côte de Beaune) | Historic Beaune 1er cru estate, great value |
| [[jean_jacques_girard\|Jean-Jacques Girard]] | Burgundy (Savigny) | Deep Savigny 1er cru spread |
| [[nicolas_rossignol\|Nicolas Rossignol]] | Burgundy (Volnay) | Volnay/Pommard/Beaune, library vintages |
| [[roger_belland\|Roger Belland]] | Burgundy (Santenay) | Santenay/Maranges + a sliver of Criots GC |
| [[chateau_de_la_maltroye\|Château de la Maltroye]] | Burgundy (Chassagne) | Chassagne in both colours |
| [[alvina_pernot\|Alvina Pernot]] | Burgundy (Puligny) | Young white domaine (Paul Pernot lineage) |

## Follow-up (not done in this pass)

- **Refresh DTE retailer sections + prices for the 109 already-covered producers.**
  The 2026-03-25 portfolio is newer than the prior ingest. Re-running
  `ingest_dte_jsx.py` against the recovered JSON would do it, **but** its
  `DTE_ALIASES` table is incomplete — a blind run would create ~17 duplicate pages
  (e.g. `guyon.md` beside `jean_pierre_guyon.md`, `tawse.md` beside `marchand_tawse`).
  Extend `DTE_ALIASES` to cover the loose-matched slugs first, then re-run.
- **Panzer's own scores.** The recovered `SD` object carries a `WK` dict of
  per-cuvée point scores (e.g. 2023 Bouley Pommard Rugiens = 100) for a subset of
  producers — a candidate feed for the `## Critic Ratings` section or a "Panzer's
  scored offers" view.
