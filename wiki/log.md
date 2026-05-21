---
type: log
total_entries: 5
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

