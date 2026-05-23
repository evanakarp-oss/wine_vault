---
type: importer
name: "BNP"
slug: bnp
producer_count: 6
focus: ['Bordeaux']
notable_producers: ['Château Lafite Rothschild', 'Château Palmer', 'Château Ducru-Beaucaillou', 'Château Gruaud-Larose', 'Château Calon-Ségur']
updated: 2026-05-21
---

# BNP (BNP Distributing)

**6 producers** in the vault currently on the BNP Distributing portfolio (BNP producer index, pasted 2026-05-21; source page appears machine-translated to English — "Castle" for Château, "Pope Clement's" for Pape Clément, "Little Horse" for Petit Cheval, etc.). Full portfolio is **172 producers**, **heavily Bordeaux-focused** (an estimated 130+ Bordeaux châteaux including all 5 First Growths, both Pichons, Cheval Blanc, Ausone, Angélus, d'Yquem). Landed at `raw/bnp/portfolio_2026-05-21.md`. Cross-check against Raeder's: [[bnp_at_raeders|BNP at Raeder's]] (~60 producers, 150+ bottles — **the highest-value importer overlap by far**).

| Producer | Country | Region | CSW | Cellar |
|---|---|---|---:|---:|
| [[chateau_lafite_rothschild|Château Lafite Rothschild]] | France | Bordeaux — Pauillac | 1 | — |
| [[chateau_palmer|Château Palmer]] | France | Bordeaux — Margaux | 1 | — |
| [[chateau_ducru_beaucaillou|Château Ducru-Beaucaillou]] | France | Bordeaux — Saint-Julien | — | — |
| [[chateau_gruaud_larose|Château Gruaud-Larose]] | France | Bordeaux — Saint-Julien | — | — |
| [[chateau_leoville_barton|Château Léoville Barton]] | France | Bordeaux — Saint-Julien | — | — |
| [[chateau_calon_segur|Château Calon-Ségur]] | France | Bordeaux — Saint-Estèphe | — | — |

## Producers at Raeder's not yet in the wiki (curation candidates)

See [[bnp_at_raeders]] for the full bottle-level list. This is the largest single curation gap of any importer — BNP brings most of classified Bordeaux. Top by absolute bottle count + value:

**First Growths / Premier Cru** (★★ priority):
- Château Latour *(15 bottles incl. Pauillac 1970 $699.99, Les Forts de Latour 2019 $279.99)*
- Château Lafite Rothschild *(11 bottles incl. Pauillac 1967 $1,999.99, Carruades 2020/22)*
- Château Mouton-Rothschild *(8 bottles incl. Pauillac 1978 $599.99, 2009/15/18/19)*
- Château Haut-Brion *(9 bottles incl. 2018/19/21, Le Clarence)*
- Château Margaux *(5 bottles incl. 1976 $499.99, 2011 $1,399.99, Pavillon Rouge)*
- Château La Mission Haut-Brion *(4 bottles incl. 1969 $699.99, 2015 $599.99)*
- Château d'Yquem *(4 bottles — 2006/10/15/16)*
- Château Cheval Blanc *(Saint-Émilion 2010)*

**Super Seconds / 2nd–5th Growths**:
- Château Cos d'Estournel *(10 bottles incl. 2000 $889.99, 2001 $799.99)*
- Château Palmer *(8 bottles incl. 1964 $499.99, 1981 $399.99)*
- Château Pichon Comtesse / Pichon Baron *(6+ bottles combined)*
- Château Léoville Barton *(3 bottles)*
- Château Léoville Poyferré *(2)*
- Château Léoville-Las Cases *(1 — 2005)*
- Château Calon-Ségur *(3 — 1995 $199, 2015 $189, 2018 $229)*
- Château Montrose *(3 — 2011, 2022, Dame de Montrose)*
- Château Ducru-Beaucaillou *(2 — 1964 $99, 1988 $299)*
- Château Gruaud-Larose *(4 — 1975 $499, 1989 $279, 2019/20 $99 each)*
- Château Pontet-Canet *(2017)*
- Château Lynch-Bages *(5 bottles)*
- Château Branaire-Ducru *(2)*
- Château Talbot *(5 — Caillou Blanc + 4 reds)*
- Château Beychevelle *(2019)*

**Sauternes**:
- Château Rieussec *(2 — 2009 $129, 2010 $149)*
- Château Suduiraut *(3 incl. Lions de Suduiraut)*
- Château Coutet *(2003)*

**Saint-Émilion grand crus**:
- Château Angélus *(2 — Saint-Émilion 2017/2020 $499.99)*
- Château Ausone *(Chapelle d'Ausone 2012)*
- Château Figeac *(5 bottles incl. 2005 $399.99, 2018 $329.99)*
- Château Pape Clément *(4 bottles)*
- Château Canon *(5 bottles)*
- Château Canon-la-Gaffelière *(2018)*
- Château L'Évangile *(2 — 2010 $499, Blason 2018 $129)*

**Other classified Bordeaux**:
- Château Brane-Cantenac, Cantemerle, Carbonnieux, Clerc Milon, Coutet, d'Issan, Du Tertre, Duhart-Milon, Gazin, Giscours, Gloria, Grand-Puy Ducasse, Grand-Puy-Lacoste, Haut-Bages Libéral, Haut-Bailly, Haut-Batailley, Lafon-Rochet, Lagrange, Les Ormes de Pez, Malescot Saint-Exupéry, Meyney, Montlandrie, Phélan-Ségur, Rauzan-Ségla, Clos du Marquis (LLC 2nd wine), Domaine de Chevalier

## Methodology

Source name normalization handled the machine-translated "Castle" → "Château" map at compile time; the original English entries are preserved in `raw/bnp/portfolio_2026-05-21.md`. Bordeaux first-pass match rate is exceptionally high because most BNP châteaux have exact-name matches at Raeder's.

*Hand-maintained 2026-05-21. `scripts/build_rollups.py` block-style YAML bug applies — the 6 newly-tagged châteaux won't surface in the auto-rollup until the fix lands.*
