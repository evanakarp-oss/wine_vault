---
type: log
total_entries: 11
generator: scripts/build_wiki_log.py
---

# Wiki Log

<!-- Initial entries seeded from git history by `scripts/build_wiki_log.py`. After seeding, append new entries by hand or via your ingest/compile/lint scripts. Format: `## [YYYY-MM-DD] op | title`. -->

Chronological, append-only record of vault operations. Each entry's `## ` prefix makes the log greppable with simple unix tools — e.g. `grep "^## \[" wiki/log.md | tail -5` for the five most recent operations.

## [2026-05-21] ingest | Kermit Lynch portfolio cross-checked against Raeders inventory

- Source landed: `raw/kermit_lynch/portfolio_2026-05-21.md` (146 France + 47 Italy-Grower producers, 193 total).
- Cross-check view: `wiki/_views/kermit_lynch_at_raeders.md` — 30 KL producers found at Raeder's (67 bottles in stock).
- Updated `wiki/producers/lucien_boillot.md` + `meo_camuzet.md`: added `importer_us: Kermit Lynch`.
- Hand-patched `wiki/importers/Kermit_Lynch.md` (10 → 12 producers). `scripts/build_rollups.py` has a latent bug: `get_list()` regex only matches inline-flow YAML lists, not block style, so the script grouped only 3 of 12 producers. Fix in a follow-up.
- Open question for Evan: 8 of the existing 10 wiki KL producers (Pierre André, Joncuas, Charvin, Barou, Levet, Balthazar, Esmonin, Ferme Saint-Martin) are not on the newly-pasted portfolio — likely KL dropouts.
- Portfolio completeness verified later in same session: re-pasted full kermitlynch.com/growers page (single alphabetized list, not country-grouped) and diffed against stored source — zero deltas (193 = 193).

## [2026-05-21] compile | Strip stale Kermit Lynch importer tag from 8 ex-portfolio producers

- Stripped `importer_us: Kermit Lynch` from 8 producers that are no longer on the current kermitlynch.com/growers page: Domaine Pierre André, Clos du Joncuas, Sylvie Esmonin, Domaine Charvin, Domaine Barou, Domaine Levet, Franck Balthazar, Ferme Saint-Martin.
- These were inferred from older CSW write-ups; the CSW Write-ups sections remain intact on each producer page.
- Updated `wiki/importers/Kermit_Lynch.md`: now lists 4 current KL producers (Pierre Gonon, Allemand, Méo-Camuzet, Lucien Boillot) plus a "Recently dropped" section for the 8 ex-importers.
- Updated `wiki/_views/kermit_lynch_at_raeders.md`: marked Issue 1 resolved.

## [2026-05-21] ingest | Rosenthal Wine Merchant portfolio cross-checked against Raeders inventory

- Source landed: `raw/rosenthal/portfolio_2026-05-21.md` (145 producers — France 86 / Italy 46 / Switzerland 5 / Austria 4 / Spain 4). Page does not print country labels; country inferred from location keywords during parse.
- Cross-check view: `wiki/_views/rosenthal_at_raeders.md` — 8 Rosenthal producers found at Raeder's (13 bottles in stock). Hubert Lignier dominant with 5 cuvées; Harmand-Geoffroy Mazis-Chambertin GC 2020 is the headline grand-cru bottle.
- Hand-patched `wiki/importers/Neal_Rosenthal.md`: bumped from 1 to 7 confirmed-current Rosenthal producers already in the wiki (Brovia, Le Puy, Cheveau, Lionnet, Elio Sandri, Puffeney, Gahier — the rollup script's YAML block-list bug had hidden 6 of these). Added a "Curation candidates" section for the 8 Raeder's-stocked producers without wiki pages, top picks Hubert Lignier and Harmand-Geoffroy.
- Open question for Evan: Bernhard Huber (Baden) is tagged `importer_us: Neal Rosenthal` but the pasted portfolio has NO German producers at all. Could be (a) Huber dropped, (b) moved importer, or (c) the rosenthalwinemerchant.com/growers page is region-filtered and Germany is on a separate view. Flagged on the importer page as pending verification.

## [2026-05-21] lint | Catch Paolo Bea miss; re-run KL+Rosenthal cross-checks with improved matcher

- Bug: discriminative-tokens function required tokens ≥4 chars, which dropped the 3-letter surname "Bea" from "Paolo and Giampiero Bea". Combined with KEEPING "Paolo" and "Giampiero" (given names), the all-tokens match against Raeder's stored "Paolo Bea" failed.
- Fix: lowered min token length 4 → 3 and added an explicit drop-list for common given names (Paolo, Pierre, Jean, Michel, Jacques, Hubert, Henri, Georges, Sylvain, Xavier, Etienne, Lucien, etc.). Surnames now become the discriminator.
- New match found: **Paolo and Giampiero Bea — 5 bottles at Raeder's** (Sagrantino Pagliaro 2020, Cerrete 2019, Pipparello 2019, San Valentino 2020, De Veo 2019). Rosenthal Raeder's total bumped 8 → 9 producers, 13 → 18 bottles.
- Re-ran same fix against Kermit Lynch portfolio: 8 surname-only candidates surfaced, all audited as false positives (Bellevue Mondotte ≠ Château de Bellevue, Nino Negri ≠ Giulia Negri, Pascal Jolivet ≠ KL's Northern-Rhône "Domaine Jolivet", Joseph Drouhin/Carr ≠ Clos Saint-Joseph, etc.). KL total stays at 30 producers / 67 bottles.
- Updated `wiki/_views/rosenthal_at_raeders.md` + `wiki/importers/Neal_Rosenthal.md` with the new Bea entry.

## [2026-05-21] ingest | Skurnik portfolio cross-checked against Raeders + resolves Huber

- Source landed: `raw/skurnik/portfolio_2026-05-21.md` (443 wine producers across France 133 / Italy 107 / USA 110 / Spain 54 / Germany 25 / Argentina 14). Spirits / distilleries / ciders / sojus (46 entries) filtered out at parse time.
- Cross-check view: `wiki/_views/skurnik_at_raeders.md` — **32 Skurnik producers found at Raeder's (53 bottles)** — the densest importer overlap by far, driven by Skurnik's California/Oregon/Washington coverage matching Raeder's specialty. Highlights: Ramey 5 bottles, Cayuse 5, Peter Michael 3, Patricia Green 3, La Rioja Alta 3.
- Hand-patched `wiki/importers/Skurnik.md` (1 → 18 producers). Added `importer_us: Skurnik` to 14 producer pages that already existed in the wiki: barraud, georges_noellat, chateau_de_pibarnon, clos_du_mont_olivet, altar_uco, altos_las_hormigas, matias_riccitelli, escala_humana, stella_crinita, ver_sacrum, zorzal_wines, elio_altare, cavallotto, sottimano. Four pages already had Skurnik tagged (aj_adam, willi_schaefer, donnhoff, schafer-frohlich).
- **Resolution**: Bernhard Huber question from previous Rosenthal log entry — Huber appears on Skurnik's current Baden list (one of Skurnik's two Baden producers, alongside Ziereisen). Flipped `importer_us` on bernhard_huber.md from `["Neal Rosenthal"]` → `["Skurnik"]`. Removed "Pending verification" section from `wiki/importers/Neal_Rosenthal.md`; added a "Resolved" note instead.
- New open question: Schäfer-Fröhlich (Nahe) tagged `["Skurnik", "Theise"]` but not on current Skurnik paste (Nahe section lists Hexamer, Krüger-Rumpf, Schlossgut Diel, Schneider, Dönnhoff only). Could be a Skurnik dropout (still with Theise) or a paste gap. Flagged on `wiki/importers/Skurnik.md` as pending verification.

## [2026-05-21] ingest | Grand Cru Selections portfolio cross-checked against Raeders

- Source landed: `raw/grand_cru/portfolio_2026-05-21.md` (72 producers — Burgundy 27 / Loire 11 / Champagne 11 / Rhône 4 / Beaujolais 4 / Chablis 3 / Bordeaux 3 / Roussillon 3 / Jura 2 / Corsica 2 / Provence 1 / Normandy 1).
- Cross-check view: `wiki/_views/grand_cru_at_raeders.md` — **19 GCS producers found at Raeder's (35 bottles)** — 26% hit rate, second only to Skurnik. Headline bottle: Domaine Georges Roumier Ruchottes-Chambertin GC 2023 at $1,799.99. Other major bottles: Château Lafleur Pomerol 2020 ($1,079.99), Fourrier Corton-Charlemagne 2022 ($799.99), Comtes Lafon Meursault Porusots 2022 ($469.99), JL Chave Hermitage Blanc 2021 ($369.99), Pierre Péters Montjolys 2017 ($329.99).
- Created `wiki/importers/Grand_Cru_Selections.md` with 1 currently-tagged producer (Pierre Péters — flipped `importer_us` to add Grand Cru Selections). Eighteen producers at Raeder's lack wiki pages — flagged as top-tier curation candidates (Roumier, Lafleur, Comtes Lafon, Roulot, Fourrier, Chave, Clusel-Roch, Bourgneuf).
- **Conflict flagged**: Domaine Roulot appears on BOTH the Kermit Lynch and Grand Cru Selections pastes. Real-world Roulot moved from KL to GCS around 2022, so the KL paste likely has a stale entry. No wiki action yet (no producer page exists); flagged on both `wiki/importers/Grand_Cru_Selections.md` and the GCS view.
- Ambiguous match: Savart Champagne → "Dremont & Savart Éphémère 017 Bouzy GC" at Raeder's looks like a joint cuvée, possibly related to the GCS "Ephemeral Champagne" entry. Flagged.

## [2026-05-21] ingest | Polaner Selections portfolio cross-checked against Raeders + tag corrections

- Source landed: `raw/polaner/portfolio_2026-05-21.md` (323 producers across France 131 / Italy 77 / USA 57 / Spain 32 / Portugal 15 / Argentina 6 / Chile 3 / Hungary 1 / Austria 1).
- Cross-check view: `wiki/_views/polaner_at_raeders.md` — **24 Polaner producers found at Raeder's (58+ bottles)** — heaviest absolute bottle count of the five importers checked so far. Driven by Roagna (6 bottles), Carlisle (~10 bottles), Bedrock (5), Maybach (5). Headline bottles: Giacomo Conterno Barolo Cerretta 2021 ($379.99), Roagna Barbaresco Pajé VV 2018 ($359.99), Giuseppe Mascarello Monprivato 2017 ($249.99).
- Hand-patched `wiki/importers/Polaner.md`: bumped from 10 (mostly stale) to 19 confirmed-current producers. Added `importer_us: Polaner` to 17 producer pages (agrapart, boulay, cascina_delle_rose, collestefano, georges_glantenay, giacomo_conterno, goisot, julien_sunier, larmandier_bernier, montenidoli, roagna, sigaut, trediberri, vincent_paris, franck_balthazar, arnot-roberts, domaine_boisson). Added Polaner alongside Kysela on domaine_de_montille.
- Tag corrections: (1) flipped `importer_us` on domaine_baudry from Polaner → Kermit Lynch (new KL paste lists "Bernard Baudry"; Polaner paste has none); (2) added Polaner to franck_balthazar (we stripped this from KL earlier; now confirmed on Polaner Rhône list — resolves the KL dropout).
- Open question for Evan: 8 wiki producers tagged `importer_us: Polaner` not on the freshly-pasted Polaner portfolio: Rateau, Lafouge, Chevalerie, Ceretto, Produttori del Barbaresco, Rapet Père & Fils, Jane et Sylvain, Stéphane Guion. Following the KL precedent these are probable stale tags; flagged on the Polaner rollup as pending verification.

## [2026-05-21] ingest | Bowler Wine portfolio cross-checked against Raeders + tag corrections

- Source landed: `raw/bowler/portfolio_2026-05-21.md` (309 producers across France 114 / Italy 71 / USA 44 / Spain 33 / Germany 16 / Austria 11 / Argentina 8 / Chile 8 / NZ 2 / Switzerland 1 / Portugal 1).
- Cross-check view: `wiki/_views/bowler_at_raeders.md` — **14 Bowler producers found at Raeder's (17 bottles)**. Modest hit rate (~5%) but high-quality matches: 3 Washington cult Cabs (Leonetti 3 bottles, Quilceda Creek 1, Figgins 1), Philip Togni Napa Spring Mountain, Lopez de Heredia, Mount Eden, Arianna Occhipinti, La Gerla.
- Resolution from prior session: "Famille Isabel Ferrando" bottle at Raeders (Châteauneuf-du-Pape Rouge 2020 $115.99) is BOWLER-imported (Domaine Saint-Préfert). This closes the loop on the Rosenthal "Luigi Ferrando" false positive I flagged earlier.
- Created `wiki/importers/Bowler.md` with 15 currently-tagged producers. Added `importer_us: Bowler` to 13 producer pages (arnoux_lachaux, bruna, cara_sur, carmelo_patti, clos_de_la_roilette, desvignes, fratelli_alessandria, magnien, piane, pielihueso, ployez_jacquemart, steinmetz, berthaut-gerbet).
- Tag corrections: (1) flipped `importer_us` on chandon_de_briailles from Skurnik → Bowler (Bowler paste lists it, Skurnik paste does not). (2) flipped clemens_busch from `["Skurnik", "Theise"]` → `["Bowler", "Theise"]` (Bowler is current; Theise tag preserved since Theise paste not yet sourced).

## [2026-05-21] ingest | Frederick Wildman & Sons portfolio cross-checked against Raeders

- Source landed: `raw/wildman/portfolio_2026-05-21.md` (297 wine producers — USA 84 / Italy 73 / France 58 / Spain 25 / Australia 16 / Argentina 8 / Austria 8 / Germany 6 / NZ 5 / South Africa 4 / Chile 3 / Portugal 3 / Peru 2 / Mexico 1 / Japan 1; 15 spirits filtered out).
- Cross-check view: `wiki/_views/wildman_at_raeders.md` — **~60 Wildman producers at Raeder's (~110 bottles)** — by a wide margin the heaviest Raeder's overlap of all importers cross-checked. Driven by Wildman's deep Napa book (Stag's Leap, Ridge, Larkmead, PlumpJack, Chappellet, Darioush, Cade, HALL) + Burgundy grand cru (Armand Rousseau 4 bottles incl. Chambertin GC 2022 $2,999.99, Jacques Prieur Echezeaux 2019 $1,199.99, Mugnier Maréchale, Nicole Lamarche Echezeaux, Sylvain Cathiard NSG Aux Thorey 2021 $499.99). Headline single bottle: Vega Sicilia Único Reserva Especial R24 3-pack 2010/11/12 NV at $2,999.99.
- Created `wiki/importers/Wildman.md` with 4 currently-tagged producers. Added `importer_us: Wildman` to 3 wiki pages (burlotto, guyon, otronia). Added Wildman alongside Kermit Lynch on meo_camuzet.md.
- **Conflict — Méo-Camuzet**: both KL paste and Wildman paste claim Méo-Camuzet. Same pattern as the earlier Roulot conflict (KL vs GCS). Wiki tag now carries both `Kermit Lynch` and `Wildman` pending resolution. Real-world MC has historically been Wilson Daniels in many markets — likely one paste is stale.
- **Resolution**: Pascal Jolivet ambiguity (flagged on the KL view) is resolved — Wildman's portfolio lists "Maison Pascal Jolivet" under LOIRE VALLEY, matching the Raeder's bottles. KL's "Domaine Jolivet" Northern Rhône entry is likely a separate producer or a paste error.

## [2026-05-21] ingest | Wine Source (partial — Selection page screenshot) cross-checked against Raeders

- Source landed: `raw/wine_source/portfolio_2026-05-21.md` (12 producer logos visible in a user-supplied screenshot of winesourcestore.us/selection). winesourcestore.us is blocked by the remote network policy, so the "Our Portfolio" section below the fold could not be captured — view is partial.
- Cross-check view: `wiki/_views/wine_source_at_raeders.md` — **1 of 12 visible Wine Source producers at Raeder's (3 bottles)**: Yann Durieux Gevrey-Chambertin Grand Cru 2020 ($499.99), La Gouzotte Rouge 2021 ($119.99), Love And Pif Blanc 2021 ($74.99). Cult natural-wine producer; Raeder's stores him as plain "Yann Durieux" (Wine Source labels the project "Recrue des Sens").
- Created `wiki/importers/Wine_Source.md` with 1 currently-tagged producer. Added `importer_us: Wine Source` to fanny_sabre.md (the only Wine Source producer already in the wiki).

## [2026-05-21] ingest | Banville Wine Merchants portfolio cross-checked against Raeders

- Source landed: `raw/banville/portfolio_2026-05-21.md` (59 producers — Italy 31 / France 19 / Germany 2 / NZ 2 / Oregon 2 / Argentina 1 / Austria 1 / Slovenia 1).
- Cross-check view: `wiki/_views/banville_at_raeders.md` — **12 Banville producers at Raeder's (13 bottles)**, 20% hit rate. Headline bottle: **Jean-Jacques Confuron Romanée-Saint-Vivant Grand Cru 2016 — $899.99**. Other notable: Odoul-Coquard Vosne 2021 ($179.99), Trinoro Le Cupole NV ($69.99), Parusso Barolo Perarmando ($59.99), Tolaini Valdisanti, Terlano, Illuminati.
- Created `wiki/importers/Banville.md` with 1 currently-tagged producer (Marc Sorrel — added Banville tag). Other 12 Raeder's-stocked producers are curation candidates.
- **Wildman correction**: the Wildman cross-check credited Bodegas Fariña (Toro, Spain) with Raeder's "Farina | Lugana" — that was a token collision. Lugana is Italian Garda; the producer is Banville's Italian Farina, not Wildman's Spanish Fariña. Updated Wildman view's false-positive list and corrected the entry.

