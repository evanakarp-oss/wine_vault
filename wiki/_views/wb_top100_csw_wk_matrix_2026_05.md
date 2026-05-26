---
type: view
updated: 2026-05-26
question: "Wine Berserkers 'Top 10 in your cellar' top 100, cross-referenced with CSW coverage and William Kelley signal"
sources:
  - raw/berserkers/threads/top10_in_cellar.json (1,089 posts, 1,115 unique producers, 4,999 mentions, 2013-2026)
  - wiki/producers/*.md retailers.chambers + retailers.berserkers_kelley
  - cellar/*.md producer/producer_slug for ownership flag
producer_count_in_thread: 100
csw_present: 16
csw_silent_with_page: 6
no_page_in_vault: 78
---

# WB Top 100 × CSW × William Kelley Matrix (2026-05)

The **Wine Berserkers "Top 10 producers in your cellar" megathread** (1,089
posts, 1,115 unique producers, ~5,000 mentions, 2013→2026) is the most
durable community-cellar signal in the vault. Top 100 by mention count are
seeded into `raw/berserkers/threads/top10_in_cellar.json`.

This view crosses that list against:
- **CSW coverage** (`★ ded/articles` = dedicated articles / total) — does Chambers cover them?
- **William Kelley** (`WK` = post count on Berserkers, `raw/berserkers/William_Kelley/_post_index.csv`, 4,729 posts) — has WK weighed in?
- **Cellar ownership** (`🍷`) — does Evan already own?

The three signals serve different jobs: WB = collector consensus, CSW = editorial conviction, WK = professional critic touchpoint. Where two or three converge is where to look first.

## §1 — CSW-present (22) — sorted by WK posts desc, then WB rank

WB top 100 producers that have at least one CSW article in the vault. The strongest cross-signal picks bubble to the top.

| WB# | mn | Producer | Region | CSW | WK | WK Years | Farming | Importer | Own |
|---:|---:|---|---|---|---:|---|---|---|:-:|
| 28 | 24 | [[dom_perignon|Dom Pérignon]] | Champagne | · 0/1 | **23** | 2017-2021 | — |  |  |
| 73 | 15 | [[chateau_leoville_barton|Château Léoville Barton]] | Saint-Julien (France) | · 0/2 | **9** | 2015-2022 | sustainable |  |  |
| 83 | 14 | [[allemand|Allemand]] | Cornas (France) | ★ 1/9 | **8** | 2018-2020 | natural | Kermit Lynch |  |
| 15 | 32 | [[willi_schaefer|Willi Schaefer]] | Graach (Germany) | ★ 5/9 | **6** | 2015-2025 | — | Skurnik, Theise |  |
| 27 | 25 | [[giacomo_conterno|Giacomo Conterno]] | Barolo (Monforte) (Italy) | ★ 2/5 | **2** | 2018-2020 | — |  |  |
| 52 | 18 | [[burlotto|Burlotto]] | Verduno (Barolo) (Italy) | ★ 1/6 | **2** | 2015-2021 | — |  |  |
| 7 | 52 | [[donnhoff|Dönnhoff]] | Nahe | ★ 2/10 | **1** | 2016-2016 | — | Skurnik, Theise |  |
| 16 | 30 | [[domaine_baudry|Domaine Baudry]] | Chinon (France) | ★ 20/45 | **1** | 2021-2021 | organic | Polaner |  |
| 98 | 12 | [[chateau_musar|Chateau Musar]] | Bekaa Valley, Lebanon (France) | ★ 3/3 | **1** | 2019-2019 | natural |  |  |
| 6 | 68 | [[produttori_del_barbaresco|Produttori del Barbaresco]] | Barbaresco (Italy) | ★ 5/10 | **0** |  | — | Polaner |  |
| 32 | 23 | [[domaine_pierre_gonon|Domaine Pierre Gonon]] | Saint-Joseph (France) | ★ 9/17 | **0** |  | organic | Kermit Lynch |  |
| 36 | 22 | [[hofgut_falkenstein|Hofgut Falkenstein]] | Saar (Konz) (Germany) | ★ 6/12 | **0** |  | — | Skurnik, Theise |  |
| 38 | 21 | [[gerard_mugneret|Gerard Mugneret]] | Vosne-Romanée (France) | ★ 2/2 | **0** |  | organic |  |  |
| 46 | 19 | [[kosta_browne|Kosta Browne]] | Sonoma Coast (United States) | · 0/1 | **0** |  | — |  |  |
| 81 | 14 | [[schafer-frohlich|Schafer-Frohlich]] | Nahe | ★ 2/6 | **0** |  | — | Skurnik, Theise |  |
| 89 | 13 | [[brovia|Brovia]] | Barolo / Barbaresco (Castiglione Falletto) (Italy) | ★ 6/13 | **0** |  | — | Neal Rosenthal |  |

## §2 — Wiki page exists, no CSW article (6) — community + WK only

Producers Berserkers loves and that the vault has documented, but where CSW has no editorial coverage. WK signal becomes the deciding factor.

| WB# | mn | Producer | Region | WK | WK Years | Farming | Importer | Own |
|---:|---:|---|---|---:|---|---|---|:-:|
| 82 | 14 | [[taittinger|Taittinger]] | Champagne | **16** | 2016-2021 | — |  |  |
| 25 | 26 | [[hudelot_noellat|Hudelot Noellat]] | Burgundy | **7** | 2015-2023 | — |  |  |
| 84 | 13 | [[denis_bachelet|Denis Bachelet]] | Burgundy | **4** | 2018-2025 | — |  |  |
| 78 | 14 | [[francois_bertheau|Francois Bertheau]] | Burgundy | **1** | 2023-2023 | — |  |  |
| 99 | 12 | [[peter_lauer__weingut_lauer|Peter Lauer / Weingut Lauer]] | Saar (Germany) | **0** |  | — | Skurnik, Theise |  |
| 100 | 12 | [[thomas_et_jean_marc_bouley|Thomas et Jean Marc Bouley]] | Burgundy | **0** |  | — |  |  |

## §3 — No wiki page in vault (78) — vault gaps

WB top-100 producers that don't have a `wiki/producers/<slug>.md` file. Either they fall outside the vault's curation focus (much of California cult, mass-market Champagne) or they're legitimate vault gaps to fill (Dujac, Huet, Fourrier, Beaucastel, Lafarge, Roumier, Cédric Bouchard — all curation-fit Burgundy/Champagne/Rhône). Listed in WB rank order.

| WB# | mn | Raw name |
|---:|---:|---|
| 1 | 98 | Bedrock |
| 2 | 94 | Rhys |
| 3 | 80 | Ridge |
| 4 | 74 | Rivers-Marie |
| 5 | 74 | JJ Prum |
| 8 | 52 | Jadot |
| 9 | 48 | Carlisle |
| 10 | 48 | Goodfellow |
| 11 | 44 | Bruno Giacosa |
| 12 | 43 | Huet |
| 13 | 36 | Saxum |
| 14 | 36 | Dujac |
| 17 | 30 | Lopez de Heredia |
| 18 | 29 | Pegau |
| 19 | 29 | Patricia Green |
| 20 | 28 | SQN |
| 21 | 28 | Chevillon |
| 22 | 27 | Williams Selyem |
| 23 | 26 | Bouchard |
| 24 | 26 | Krug |
| 26 | 25 | Myriad |
| 29 | 24 | Rousseau |
| 30 | 23 | Keller |
| 31 | 23 | Dauvissat |
| 33 | 23 | Aubert |
| 34 | 23 | Montrose |
| 35 | 22 | Fourrier |
| 37 | 21 | Drouhin |
| 39 | 21 | Copain |
| 40 | 20 | Realm |
| 41 | 20 | d'Angerville |
| 42 | 20 | G. Rinaldi |
| 43 | 20 | Cayuse |
| 44 | 20 | B. Mascarello |
| 45 | 20 | Walter Scott |
| 47 | 19 | G. Mascarello |
| 48 | 19 | Kutch |
| 49 | 19 | Mugnier |
| 50 | 19 | Halcon |
| 51 | 18 | Faiveley |
| 53 | 18 | Cappellano |
| 54 | 17 | Barthod |
| 55 | 17 | Foillard |
| 56 | 17 | Pontet Canet |
| 57 | 16 | Dunn |
| 58 | 16 | Roumier |
| 59 | 16 | Sojourn |
| 60 | 16 | Quilceda Creek |
| 61 | 16 | Beaucastel |
| 62 | 16 | Coudert |
| 63 | 16 | Cameron |
| 64 | 16 | Ceritas |
| 65 | 16 | Di Costanzo |
| 66 | 16 | Beta |
| 67 | 15 | Lafarge |
| 68 | 15 | Von Schubert |
| 69 | 15 | Felsina |
| 70 | 15 | Pichon Lalande |
| 71 | 15 | Chave |
| 72 | 15 | Kelley Fox |
| 74 | 15 | Littorai |
| 75 | 15 | Peay |
| 76 | 15 | Vajra |
| 77 | 14 | Mount Eden |
| 79 | 14 | Arcadian |
| 80 | 14 | Maison Ilan |
| 85 | 13 | DRC |
| 86 | 13 | Pichon Baron |
| 87 | 13 | Chidaine |
| 88 | 13 | Turley |
| 90 | 13 | PYCM |
| 91 | 13 | Andremily |
| 92 | 13 | MacDonald |
| 93 | 12 | Alban |
| 94 | 12 | Cedric Bouchard |
| 95 | 12 | Raveneau |
| 96 | 12 | Pepiere |
| 97 | 12 | Scherrer |

## How to read this view

**Triple-converge (CSW★ + WK ≥5 + WB top 100):**
- [[allemand|Allemand]] — natural Cornas, WK 8, WB#83, CSW★1/9. Strongest natural-leaning convergence in the entire vault.
- [[willi_schaefer|Willi Schaefer]] — Mosel/Graach grower, WK 6, WB#15, CSW★5/9. Strongest Mosel convergence.

**CSW conviction + WB community + WK silent** (CSW caught them early; community loves them; WK genre-shaped silence — not negative):
- [[domaine_baudry|Baudry]] (CSW★20, WB#16) — Loire CF foundation
- [[domaine_pierre_gonon|Gonon]] (CSW★9, WB#32) — N. Rhône benchmark
- [[gerard_mugneret|Gérard Mugneret]] (CSW★2, WB#38) — rising biodynamic Vosne
- [[hofgut_falkenstein|Falkenstein]] (CSW★6, WB#36) — Saar grower
- [[brovia|Brovia]] (CSW★6, WB#89) — Barolo traditional

**WK heavy + CSW silent** (worth investigating — vault has Burgundy growers WK posts about that CSW doesn't cover):
- [[hudelot_noellat|Hudelot-Noellat]] (WK 7, WB#25)
- [[denis_bachelet|Denis Bachelet]] (WK 4, WB#84)
- [[francois_bertheau|François Bertheau]] (WK 1, WB#78)

**Both critics silent, pure community** (vault page exists but neither CSW nor WK has weighed in — pure WB pick):
- [[peter_lauer|Peter Lauer]] (WB#99) — you own
- [[thomas_et_jean_marc_bouley|Bouley]] (WB#100)

## Caveats

- **WK post count ≠ score.** Each post could be enthusiasm, critique, or technical commentary. Click `latest_post` URLs in producer frontmatter (or `raw/berserkers/William_Kelley/topics/`) before betting big. See [[gap_csw_wk_overlay_2026_05]] for the same caveat in context.
- **Ownership detection is imperfect.** The cellar slug doesn't always match the wiki slug (`comm_g_b_burlotto` vs. `burlotto`). The `🍷` column normalizes producer names but may still miss edge cases. Verify against `cellar/*.md` before assuming a producer isn't owned.
- **Farming tags are sparse.** 17 of 22 CSW-present rows have `farming: []` in the vault. Many of those are actually organic/biodynamic but the tag hasn't been backfilled. See "Open follow-ups" in CLAUDE.md.
- **WB thread snapshot.** This is one thread (1,089 posts). Other WB threads (vintage-specific, region-specific) would surface different patterns. The Berserkers pipeline supports more threads — see `raw/berserkers/README.md`.

## Related views

- [[gap_csw_buy_candidates_2026_05]] — curated 10+8 shortlist with the suggested mixed-case build
- [[gap_csw_wk_overlay_2026_05]] — the full 138-row CSW-champion gap list with WK overlay (3 tiers)
- [[gap_csw_championed]] — the source 143-row CSW gap (`compile_csw.py` output)
