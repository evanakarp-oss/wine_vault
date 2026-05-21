---
type: gap_view
source: raw/rosenthal/portfolio_2026-05-21.md
raeders_snapshot: raw/raeders/master_2026-04-25.csv
rosenthal_producers_total: 145
rosenthal_by_country:
  france: 86
  italy: 46
  switzerland: 5
  austria: 4
  spain: 4
raeders_hits: 9
raeders_bottles: 18
updated: 2026-05-21
---

# Neal Rosenthal × Raeder's — Inventory Cross-Check

Cross-checks the newly-pasted Rosenthal Wine Merchant portfolio (145 producers across France 86 / Italy 46 / Switzerland 5 / Austria 4 / Spain 4, pasted 2026-05-21) against the Raeder's master inventory snapshot from 2026-04-25.

**9 of 145 Rosenthal producers** have bottles at Raeder's (18 total). Matching is **whole-token** on the producer field after normalization (lowercased, accents stripped, hyphens → spaces, prefixes like *Domaine* / *Château* / *Cave* / *Mas* / *Tenuta* dropped). Surnames ≥3 chars are kept so short surnames like "Bea" can match.

## Confirmed at Raeder's (9 producers)

| Rosenthal Producer | Region | Raeder's listings |
|---|---|---|
| Hubert Lignier | Burgundy — Morey-Saint-Denis | 5 bottles incl. Morey-St-Denis Trilogie 2022 ($139.99), Volnay 2022 ($139.99), Gevrey-Chambertin Regnard 2022 ($129.99), Monthélie 2022 ($79.99), Morey-St-Denis Les Chaffots 2022 |
| Paolo and Giampiero Bea | Italy — Umbria — Montefalco | 5 bottles, all *(call for price)*: Sagrantino di Montefalco Secco Pagliaro 2020, Montefalco Sagrantino Cerrete 2019, Montefalco Rosso Riserva Pipparello 2019, Montefalco Rosso Vigna San Valentino 2020, Rosso De Veo Umbria Rosso 2019 |
| Domaine Harmand-Geoffroy | Burgundy — Gevrey-Chambertin | Mazis-Chambertin GC 2020 — $449.99 |
| Edmond Cornu & Fils | Burgundy — Ladoix | Chorey-lès-Beaune Les Bons Ores 2017 ($41.99); Bourgogne Les Barrigards 2023 ($35.99) |
| Jean Chauvenet | Burgundy — Nuits-Saint-Georges | NSG 2019 |
| Georges Lignier & Fils | Burgundy — Morey-Saint-Denis | Gevrey-Chambertin 2019 |
| Lucien Crochet | Loire — Sancerre (Bué) | Sancerre La Croix du Roy NV — $39.99 |
| Château Pradeaux | Provence — Bandol | Bandol Rosé 2022 — $29.99 |
| Domaine Bois de Boursan | Rhône — Châteauneuf-du-Pape | CdP Cuvée des Félix 2005 — $89.99 |

## Notable Rosenthal stars NOT at Raeder's

Producers worth flagging in case Raeder's takes them in future, or worth seeking elsewhere — these are the editorial-tier Rosenthal names that did not show in the snapshot:

- **Italy**: Montevertine, Gravner, Vodopivec, Cappellano, Brovia, Monastero Suore Cistercensi, Podere Le Boncie, Pacina, Joaquin, Casa Setaro, De Fermo, Luigi Ferrando, Figli Luigi Oddero
- **France — Burgundy**: Ghislaine Barthod, Jacques Carillon, Jean & Sébastien Dauvissat, Daniel-Etienne Defaix, Domaine Bitouzet-Prieur, Henri & Gilles Buisson, Jean-Marc Pillot, Sylvain Morey, Domaine Rollin
- **France — Loire**: Philippe Foreau (Clos Naudin), Philippe Gilbert (Menetou-Salon), Château de Chaintres
- **France — Bordeaux**: Le Puy, Château de Fargues, Domaine du Jaugaret
- **France — Provence**: Château Simone, Domaine Tempier-adjacent Bandol (Pradeaux is the one we have), Domaine du Bagnol
- **France — Languedoc**: Mas Jullien, Mas Cal Demoura
- **France — Rhône**: Domaine Lionnet (Cornas), Vignobles Levet (Côte-Rôtie), Xavier Gerard, Guillaume Gilles
- **France — Jura**: Domaine de Montbourgeau, Jacques Puffeney, Michel Gahier, Overnoy-Crinquand
- **Spain**: Recaredo (Penedès), Equipo Navazos (Jerez)
- **Austria**: Anita & Hans Nittnaus, Neumeister

## Curation candidates — Rosenthal producers at Raeder's not yet in the wiki

All 8 confirmed Rosenthal-at-Raeder's producers are **absent from `wiki/producers/`**:

**Highest priority** (Burgundy grand cru / Premier cru / cult Italian, drink-now or short-term cellar):
- Hubert Lignier *(Morey, 5 cuvées in stock)*
- Paolo and Giampiero Bea *(Umbria — Montefalco; 5 cuvées incl. Sagrantino Pagliaro & Cerrete, cult biodynamic)*
- Domaine Harmand-Geoffroy *(Gevrey, Mazis-Chambertin GC)*
- Edmond Cornu & Fils *(Ladoix value)*
- Jean Chauvenet *(NSG)*
- Georges Lignier & Fils *(Morey)*

**Secondary**:
- Lucien Crochet *(Sancerre — value sub-$40)*
- Château Pradeaux *(Bandol rosé)*
- Domaine Bois de Boursan *(aged CdP)*

## Existing wiki Rosenthal pages

These 6 producer pages already exist in the wiki and are on the current Rosenthal portfolio, but **none are at Raeder's**:

- [[brovia]] *(Barolo — already tagged `importer_us: Neal Rosenthal`)*
- [[elio_sandri]] *(Piedmont)*
- [[michel_gahier]] *(Jura — Arbois)*
- [[jacques_puffeney]] *(Jura — Arbois)*
- [[domaine_cheveau]] *(Mâconnais)*
- [[domaine_lionnet]] *(Cornas)*

Of these 6, only [[brovia]] is currently surfaced in the `wiki/importers/Neal_Rosenthal.md` rollup (and even that is brittle — the rollup script's YAML parser misses block-style `importer_us:` lists; see the latent bug flagged on the [[Kermit_Lynch]] page).

## False positives caught and excluded

These token collisions matched in the first pass but are different producers (recorded so future re-runs can skip them):

- *La Torre* (Montalcino, Rosenthal) ≠ "Torre D Golban" Crianza at Raeder's *(likely Rioja)*
- *Conti* (Boca, Rosenthal) ≠ Romanée-Conti (DRC) — pure surname collision
- *Clos Saint-Andre* (Pomerol, Rosenthal) ≠ "André" Brut California sparkling
- *Champagne Guy Larmandier* (Vertus, Rosenthal) ≠ Larmandier-Bernier at Raeder's *(Pierre Larmandier's separate estate, same village/family)*

## Methodology

1. Source landed at `raw/rosenthal/portfolio_2026-05-21.md` (single dump of rosenthalwinemerchant.com/growers; producer + location pairs, country inferred from location keywords).
2. Cross-check script: normalize name (NFKD ASCII, lowercase, hyphens→spaces, strip prefixes like *Domaine/Château/Cave/Mas/Tenuta/Bodega/Cantina*), drop generic words `{de, la, saint, …}` and tokens ≤3 chars. Require **all** remaining tokens to appear as whole words in the Raeder's `producer` field.
3. Hand-audit each match against the Rosenthal region tag and Raeder's cuvée — false positives noted above.
4. **Surname-only fallback**: drop given-name particles (Paolo, Pierre, Jean, etc.) from the token set so multi-given-name producers like "Paolo and Giampiero Bea" reduce to the shared surname "Bea" and match Raeder's stored "Paolo Bea". Min-token-length lowered from 4 to 3 to keep short surnames. Same fallback re-run against the Kermit Lynch portfolio confirmed no missed matches there (8 surname-only candidates audited as false positives — Bellevue Mondotte ≠ Château de Bellevue, Nino Negri ≠ Giulia Negri, Pascal Jolivet ≠ Domaine Jolivet, etc.).

*Compiled 2026-05-21 against `raw/raeders/master_2026-04-25.csv`.*
