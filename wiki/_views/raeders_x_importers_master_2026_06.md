---
type: view
updated: 2026-06-13
question: "Full list, by importer, of producers stocked at Raeders — consolidated from all importer-portfolio cross-checks."
sources: raw/<importer>/portfolio_2026-05-21.md (13 pasted portfolios) + raw/raeders/master_2026-04-25.csv (3,174 bottles) + Roscioli Wine Club list
method: whole-token producer-name match (normalized: lowercased, accents stripped, prefixes dropped) per importer, manually disambiguated against the Raeders CSV. Confirmed-at-Raeders sections consolidated here; per-importer views keep the full curation/gap/false-positive detail.
---

# Raeders × Importers — Full Producer List by Importer (2026-06)

Every importer below had its actual portfolio pasted into `raw/` and
cross-checked against the Raeders snapshot (2026-04-25, 3,174 bottles). This
file consolidates the **confirmed-at-Raeders** producers from each per-importer
view into one readable roster, so the full list is readable here in a single
file.

The standalone `wiki/_views/<importer>_at_raeders.md` pages keep the rest
(curation candidates, stars *not* at Raeders, false positives caught,
methodology). Those 13 per-importer pages and the raw portfolio pastes
currently live on branch `claude/verify-raeders-kermit-inventory-meoMz`
(not yet merged to main) — the "Full detail" pointers below resolve once
that branch lands.

## Summary — overlap by importer

| Importer | Portfolio | At Raeders | Bottles |
|---|---:|---:|---:|
| **Wilson Daniels** | 52 | 30 | ~252 |
| **BNP Distributing** | 172 | ~60 | ~150 |
| **Frederick Wildman & Sons** | 297 | ~60 | ~110 |
| **Kermit Lynch** | 193 | 30 | 67 |
| **Polaner Selections** | 323 | 24 | 58 |
| **Skurnik** | 443 | 32 | 53 |
| **Grand Cru Selections** | 72 | 19 | 35 |
| **Vineyard Brands** | 127 | 9 | 19 |
| **Neal Rosenthal** | 145 | 9 | 18 |
| **David Bowler Wine** | 309 | 14 | 17 |
| **Banville Wine Merchants** | 59 | 12 | 13 |
| **Becky Wasserman & Co.** | 132 | (brokerage) | — |
| **Wine Source** | 12 | 1 | 3 |
| **Roscioli Wine Club** | 146 | 8–9 | ~20 |

> Ordered by bottle depth at Raeders. Wilson Daniels, BNP, and Wildman are the backbone — classified Bordeaux (BNP), big Italian verticals (WD), and Napa + Burgundy grand cru (Wildman).


---

## Wilson Daniels
*30 of 52 portfolio producers at Raeders (~252 bottles). Full detail: `wiki/_views/wilson_daniels_at_raeders.md`.*

### Headline bottles

- **Domaine de la Romanée-Conti Corton-Charlemagne GC 2022** — **$4,999.99** *(highest-priced bottle in Raeder's catalog)*
- GAJA Barolo Conteisa 2018 — $1,199.99
- Dal Forno Romano Amarone 2003 — $1,099.99
- Biondi-Santi Brunello Riserva 2016 — $899.99
- GAJA Barolo Sperss 2018 — $499.99
- Dal Forno Romano Amarone 2006/2008/2009 — $499.99 each
- Dal Forno Romano Amarone 2011/2013 — $429.99 each
- GAJA Barbaresco 2021 — $399.99
- Davies J. Davies Jamie Cabernet 2021 — $299.99
- Biondi-Santi Brunello 2015 — $249.99
- Val di Suga Brunello Vigna Spuntali 2013 — $229.99
- Champagne Gosset Celebris Extra Brut 2008 — $224.99

### Confirmed at Raeder's — by category

#### Burgundy (~70+ bottles)

| Producer | Region | Raeder's bottles |
|---|---|---|
| Domaine Leflaive *(Puligny + Mâconnais + Esprit all roll up here)* | Puligny / Mâconnais | **38 bottles** incl. Bienvenues-Bâtard-Montrachet 2022, Chevalier-Montrachet 2022, Bourgogne Blanc 2023, Esprit lineup (Pommard 1er Arvelets 2019 $379, Pouilly-Fuissé Clos Reyssier 2018/2019 $159, Chablis 1er Fourchaume, Corton GC, NSG, Savigny 1er Vergelesses, St-Romain) |
| Domaine Faiveley | Mercurey / Côte d'Or | **14 bottles** — Echezeaux GC en Orveaux 2023, Gevrey VV 2022/2023 ($199), Chambolle 1er Aux Beaux Bruns 2022, Mercurey monopoles (La Framboisière, Vallon Blanc), Bourgogne Rouge 2021 |
| Domaine Laroche | Chablis | **12 bottles** — Chablis Les Clos GC 2016, Fourchaumes VV 2019 ($77), Vaillons VV 2018/2019, Vaudevey 2021, St-Martin NV/2023, Mas La Chevalière Chardonnay |
| Domaine Billaud-Simon | Chablis | 5 bottles — Vaillons 1er 2021/2023 ($79), Fourchaume 2021 ($84), Tête d'Or 2021 ($59), Chablis 2023 |
| Domaine de la Romanée-Conti | Côte de Nuits | **Corton-Charlemagne Grand Cru 2022 — $4,999.99** *(via "Romanee Conti DRC" listing at Raeder's)* |

#### Italy — Piedmont (~60+ bottles)

| Producer | Region | Raeder's bottles |
|---|---|---|
| GAJA | Barbaresco / Barolo / Montalcino | **32 bottles** — Barolo Conteisa 2018 ($1,199.99) / 2019 / 2021; Sperss 2018 ($499.99); Barbaresco 2021 ($399.99); Costa Russi 2020; Alteni di Brassica SB 2022; Pieve Santa Restituta Brunello 2019/2020 ($59.99) — plus 22+ more |
| Elvio Cogno | Barolo — Novello | **28 bottles** — Bricco Pernice 2015 ($139) / 2018; Cascina Nuova 2015/2016/2018/2020 ($69-$79); Anas-Cetta Nascetta; Barbaresco Bordini; Moscato d'Asti — full range |

#### Italy — Tuscany (~60+ bottles)

| Producer | Region | Raeder's bottles |
|---|---|---|
| Castello di Volpaia | Chianti Classico | **26 bottles** across Chianti Classico (2016-2022 vintages), Riserva 2020, Citto Toscana 2021 |
| Val di Suga | Montalcino | **15 bottles** — Brunello Vigna Spuntali 2013 ($229.99) / 2018; Brunello standard 2013/2015/2016/2019; Poggio al Granchio 2013 ($99.99) / 2018; Rosso 2016 |
| Biondi-Santi | Montalcino | 8 bottles — Brunello 2015 ($249.99) / 2017 / 2019; Brunello Riserva 2015 / 2016 ($899.99); Rosso di Montalcino 2016/2020/2021 |
| Arnaldo Caprai | Umbria — Montefalco | 7 bottles — Sagrantino Collepiano 2013/2016, Montefalco Rosso Reserva, Outsider Rosso 2001 ($96.99), Grechetto Grecante |
| Tenuta Sette Cieli | Bolgheri | 6 bottles — Indaco 2013/2015/2018; Scipio 2013/2017; Yantra Toscana 2019 |

#### Italy — Veneto / Sicily / Other

| Producer | Region | Raeder's bottles |
|---|---|---|
| Dal Forno Romano | Valpolicella — Amarone | **22 bottles** — Amarone 2003 ($1,099.99), 2006/08/09 ($499.99 each), 2011/13 ($429.99 each), 2012/2016/2017 + 12 more across vintages — a deep Amarone vertical |
| Benanti | Sicily — Etna | 5 bottles — Etna Rosso 2018, Etna Bianco 2023/2024 ($32.99), Contrada Monte Serra, Contrada Rinazzo |
| Feudo Montoni | Sicily | 7 bottles — Nero d'Avola Vrucara 2015/2016/2018 ($69), Catarratto Masso, Grillo della Timpa, Lagnusa, Rosé di Adele |
| Jeio *(Bisol Prosecco)* | Veneto | Bisol Jeio Superiore DOCG NV; Prosecco Brut Rosé NV ($19.99) |

#### France — Champagne / Loire / Rhône / Provence / Alsace

| Producer | Region | Raeder's bottles |
|---|---|---|
| Champagne Gosset | Aÿ | **15 bottles** — Celebris Extra Brut 2007/2008 ($224.99), Celebris Rosé 2007/2008, Grand Rosé Brut NV ($44), Grande Réserve ($34.99), 12 Ans de Cave 2012, Grand Millésime 2015 + more |
| Domaine de Beaurenard *(incl. Famille Coulon)* | Châteauneuf-du-Pape | **13 bottles** — CdP standard 2019/2020 ($74)/2021 ($69); Boisrenard 2005 ($82)/2017/2020/2021; Boisrenard Blanc 2019 ($109); Gran Partita 2016; Côtes du Rhône Villages Rasteau 2020; CdR 2022 ($19.99) |
| Chêne Bleu | Rhône | **9 bottles** — Héloïse Red 2006/2009/2011 ($99.99); Abelard 2006/2009; Rose NV/2022 — confirms WD attribution (was earlier a false-positive for Skurnik) |
| Famille Joly | Loire — Savennières | Clos de la Coulée de Serrant 2023 ($179.99); Les Vieux Clos 2023 |
| Domaine du Nozay | Loire — Sancerre | "Clos du Nozay" Sancerre 2023 — $89.99 |
| Clau de Nell | Loire — Anjou | Violette Cuvée 2018 |
| Peyrassol | Provence | **9 bottles** — Le Clos Rouge 2019 ($109); Cuvée des Commandeurs Rouge 2020 ($32); La Croix Rose 2023; Les Commandeurs Rosé 2022; Château Peyrassol Blanc 2019; Château Peyrassol Rose 2020 ($89)/2023 |
| Pierre Sparr | Alsace | **10 bottles** — Crémant Brut Réserve NV ($22); Crémant Rosé; Gewürztraminer GC Mambourg 2018 ($49); Pinot Gris GC Mambourg ($49); Riesling GC Schoenenbourg ($49); One Alsace ($18); Grande Réserve range |

#### USA (California + Oregon)

| Producer | Region | Raeder's bottles |
|---|---|---|
| Arista Winery | California — Russian River | **11 bottles** — Ritchie Vineyard Chardonnay 2019 ($104) / 2020; UV-Lucky Well Pinot 2017 ($99); Ferrington Vineyard Pinot 2019; Russian River Pinot 2016-2019; UV El Diablo Chard 2020 |
| Bergström Wines | Oregon — Willamette | **12 bottles** — Cumberland Reserve 2015 ($149); Silice 2018 ($109) / 2021 ($119); Sigrid Chardonnay 2019 ($129); Gregory Ranch Pinot 2017 ($69) / 2019 ($82); Le Pré du Col Pinot; Old Stones Chardonnay; Pantagruel Syrah |
| Chateau Montelena | Napa | Cabernet Napa 2019; Chardonnay Napa 2022 |
| Davies Vineyards / J. Davies | Napa — Diamond Mountain | 7 bottles — J. Davies Diamond Mountain Cab 2019; Jamie 2021 ($299.99); Cab Napa 2019/2021/2022; Nobles Vineyard Pinot 2018 ($74)/2020 |
| Hyde de Villaine (HDV) | Napa — Carneros | **9 bottles** — Hyde Vineyard Chardonnay 2015 ($79)/2016/2018/2020/2022; De La Guerra Chardonnay 2023 ($55); Belle Cousine Red 2016; Ygnacia Pinot 2016/2018 ($127 each) — resolves earlier KL "Domaine de Villaine" confusion |
| Schramsberg Vineyards | North Coast | 8 bottles — J. Schram 2009 ($119); Mirabelle Blanc de Blancs NV ($32); Blanc de Blancs NV ($26); Blanc de Noirs; Brut Rosé; Mirabelle Brut Rosé |
| Mirabelle *(= Schramsberg Mirabelle)* | North Coast | Counted under Schramsberg |

---

## BNP Distributing
*~60 of 172 portfolio producers at Raeders (~150 bottles). Full detail: `wiki/_views/bnp_at_raeders.md`.*

### Headline bottles (Raeder's prices)

- Château Lafite Rothschild Pauillac 1967 — **$1,999.99**
- Château Margaux Margaux 2011 — **$1,399.99**
- Château Margaux Margaux 1976 — $499.99
- Château Latour Pauillac 1970 — **$699.99**
- Château La Mission Haut-Brion 1969 — **$699.99**
- Château Mouton-Rothschild 1978 — $599.99
- Château La Mission Haut-Brion 2015 — $599.99
- Château Palmer Margaux 1964 — $499.99
- Château L'Évangile 2010 — $499.99
- Château Angélus 2020 — $499.99
- Château Gruaud-Larose 1975 — $499.99
- Château Margaux 1976 — $499.99
- Château d'Yquem 2015 — $499.99
- Château Cos d'Estournel 2000 — $889.99
- Château Cos d'Estournel 2001 — $799.99
- Château Figeac 2005 — $399.99
- Château Palmer 1981 — $399.99
- Château Pontet-Canet 2017 — ask
- Château Léoville-Las Cases 2005 — ask

### Confirmed at Raeder's — by category

#### First Growths / Premier Cru Classé

| BNP Producer | Region | Raeder's bottle count + headlines |
|---|---|---|
| Château Lafite Rothschild | Pauillac | **11 bottles** — Pauillac 1967 ($1,999.99), 2018, 2020; Carruades 2020 ($299.99), 2022; Barons Reserve Bordeaux NV ($14.99); + |
| Château Latour | Pauillac | **15 bottles** — Pauillac 1970 ($699.99), 2014; Forts de Latour 2018, 2019 ($279.99); + |
| Château Margaux | Margaux | **5 bottles** — Margaux 1976 ($499.99), 2011 ($1,399.99), 2021; Pavillon Rouge 2018; Vivens by Durfort-Vivens 2017 |
| Château Mouton-Rothschild | Pauillac | **8 bottles** — Pauillac 1978 ($599.99), 2009, 2015, 2018, 2019, +3 |
| Château Haut-Brion | Pessac-Léognan | **9 bottles** — Pessac 2018, 2019, 2021; Le Clarence 2018; + |
| Château La Mission Haut-Brion | Pessac-Léognan | **4 bottles** — 1969 ($699.99), 2011, 2015 ($599.99), 2018 |
| Château Cheval Blanc | Saint-Émilion | 2010 |
| Château Ausone *(via Chapelle d'Ausone)* | Saint-Émilion | Chapelle d'Ausone 2012 |
| Château d'Yquem | Sauternes | **4 bottles** — 2006, 2010, 2015 ($499.99), 2016 |

#### Super Seconds & 2nd–5th Growths

| BNP Producer | Region | Raeder's listings |
|---|---|---|
| Château Cos d'Estournel | Saint-Estèphe | **10 bottles** — 2000 ($889.99), 2001 ($799.99), 2009, 2011, NV ($359.99), + |
| Château Palmer | Margaux | **8 bottles** — 1964 ($499.99), 1981 ($399.99), 2017, 2018, 2019, Alter Ego 2020/2022 |
| Château Léoville Barton | Saint-Julien | 2000, 2018, La Réserve 2015 |
| Château Léoville Poyferré | Saint-Julien | 2018; Pavillon de LP 2014 ($189.99) |
| Château Léoville-Las Cases | Saint-Julien | 2005 |
| Château Pichon Comtesse de Lalande | Pauillac | 1966 ($249.99), 2017 ($199.99) |
| Château Pichon-Longueville Baron | Pauillac | 2020, 2021, Réserve de la Comtesse 2016 |
| Château Calon-Ségur | Saint-Estèphe | 1995 ($199.99), 2015 ($189.99), 2018 ($229.99) |
| Château Montrose | Saint-Estèphe | 2011, 2022; Dame de Montrose 2011 |
| Château Ducru-Beaucaillou | Saint-Julien | 1964 ($99.99), 1988 ($299.99) |
| Château Gruaud-Larose | Saint-Julien | 1975 ($499.99), 1989 ($279.99), 2019 ($99.99), 2020 ($99.99) |
| Château Lynch-Bages | Pauillac | 1978 ($299.99), 2003 ($259.99), 2020 ($399.99), Echo 2019, + |
| Château Pontet-Canet | Pauillac | 2017 |
| Château Phélan-Ségur | Saint-Estèphe | 2015, 2022 ($69.99) |
| Château Lagrange | Saint-Julien | 1970 ($99.99), 2014 |
| Château Talbot | Saint-Julien | **5 bottles** — Caillou Blanc 2023, St-Julien 2015/2019/2020/2022 |
| Château Branaire-Ducru | Saint-Julien | 2020 ($59.99), 2022 ($69.99) |
| Château Beychevelle | Saint-Julien | 2019 |
| Château Brane-Cantenac | Margaux | 2012 ($99.99), 2019 |
| Château Rauzan-Ségla | Margaux | 2014, 2019 ($139.99) |
| Château Giscours | Margaux | 1998 ($189.99), 2022 ($119.99); Sirène 2020 |
| Château Cantemerle | Haut-Médoc | 2013, 2014 ($49.99) |
| Château Gloria | Saint-Julien | **6 bottles** — 1971/1978 ($199.99 each), 1988 ($169.99), 2018/2019, + |
| Château d'Issan | Margaux | 2010 |
| Château Du Tertre | Margaux | 2019 |
| Château Malescot Saint-Exupéry | Margaux | 2022 ($79.99) |
| Château Meyney | Saint-Estèphe | 2016 |
| Château Carbonnieux | Pessac-Léognan | Blanc 2021 |
| Château Haut-Bailly | Pessac-Léognan | 2018 |
| Château Haut-Batailley | Pauillac | 1966 ($299.99), 2012, 2020; Verso 2023 ($35.99) |
| Château Haut-Bages Libéral | Pauillac | 2012 |
| Château Lafon-Rochet | Saint-Estèphe | 1964 ($199.99), 2016 |
| Château Les Ormes de Pez | Saint-Estèphe | 2011 |
| Château Clerc Milon | Pauillac | 2005, 2018, 2019, 2020 ($239.99) |
| Château Duhart-Milon | Pauillac | 1966 ($249.99), 2016, 2018, 2020; Moulin de Duhart 2019 |
| Château Grand-Puy Ducasse | Pauillac | 1978 ($299.99) |
| Château Grand-Puy-Lacoste | Pauillac | 2007, 2018 ($109.99), 2020, 2022 ($109.99) |
| Domaine de Chevalier | Pessac-Léognan | Rouge 2022 ($99.99), Rouge GC 2009 ($169.99) |

#### Saint-Émilion grand crus

| BNP Producer | Region | Raeder's listings |
|---|---|---|
| Château Angélus | Saint-Émilion | 2017, 2020 ($499.99) |
| Château Figeac | Saint-Émilion | **5 bottles** — 2005 ($399.99), 2010, 2011, 2018 ($329.99), + |
| Château Pape Clément | Pessac-Léognan *(BNP English: "Pope Clement's")* | 1970, 2006, 2016; Clémentin 2012 ($44.99) |
| Château Canon | Saint-Émilion | **5 bottles** — 1970 ($99.99), 2010, 2011, 2018 ($199.99); + |
| Château Canon-la-Gaffelière | Saint-Émilion | 2018 ($119.99) |
| Château L'Évangile *(BNP English: "Castle The Gospel")* | Pomerol | 2010 ($499.99); Blason 2018 ($129.99) |

#### Sauternes

| BNP Producer | Region | Raeder's listings |
|---|---|---|
| Château Rieussec | Sauternes | 2009 ($129.99), 2010 ($149.99) |
| Château Suduiraut | Sauternes | 1999 ($99.99); Lions de Suduiraut 2016 ($16.99) |
| Château Coutet | Sauternes-Barsac | 2003 |

#### Other

| BNP Producer | Region | Raeder's listings |
|---|---|---|
| Clos du Marquis *(Léoville-Las Cases 2nd wine)* | Saint-Julien | 2011 |
| Château Gazin | Pomerol | 1970 ($149.99) |
| Château Montlandrie | Castillon-Côtes-de-Bordeaux | 2010 ($35.99) |
| Domaine Chavy *(Burgundy — at Raeder's as "Chavy-Chouet")* | Meursault | Casse-Têtes 2020 ($119.99) |
| Biondi-Santi *(Italy — Wildman conflict — see note)* | Tuscany — Montalcino | BNP lists with quantity 1; Raeder's bottles are the Wildman matches |

---

## Frederick Wildman & Sons
*~60 of 297 portfolio producers at Raeders (~110 bottles). Full detail: `wiki/_views/wildman_at_raeders.md`.*

### Confirmed at Raeder's — by country/region

#### France — Burgundy (high-end heavy)

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Armand Rousseau | Gevrey-Chambertin | Chambertin GC 2022 ($2,999.99); Chambertin Clos de Bèze GC 2017 ($2,999.99); Chambertin GC 2021; Charmes-Chambertin 2022 ($999.99) |
| Méo-Camuzet *(conflict — also on KL paste)* | Vosne-Romanée | 12 bottles incl. Au Cros Parantoux 2023 ($2,499.99), Corton-Charlemagne GC 2022 ($599.99), NSG Aux Murgers 2018/2020, Chaumes 2019/2022/2023, Echezeaux GC, Clos de Vougeot, Corton Perrières |
| Domaine Jacques Prieur | Meursault | Echezeaux GC 2019 — $1,199.99 |
| Sylvain Cathiard et Fils | Vosne-Romanée | NSG Aux Thorey 2021 — $499.99 |
| Domaine Nicole Lamarche | Vosne-Romanée | Echezeaux GC 2019 ($299.99); 2020 ($279.99) |
| Jacques-Frédéric Mugnier | Chambolle-Musigny | Clos de la Maréchale 1er Cru 2022 — $229.99 |
| Domaine Anne Parent | Pommard | Pommard 1er Cru Les Épenots 2016 ($139.99); 2018 |
| Domaine Antonin Guyon | Aloxe-Corton | Aloxe-Corton Les Fournières 2020; Gevrey La Justice 2011; Beaune Clos De La Chaume Monopole 2013; Volnay 1er Cru Clos des Chénes 2019 |
| Château de la Maltroye | Chassagne-Montrachet | Chassagne 1er Cru Clos St Jean Rouge 2013 ($69.99); Rouge 2009 ($69.99) |
| Domaine Labruyère | Beaujolais — Moulin-à-Vent | Le Clos Du Moulin-à-Vent Monopole 2019 — $59.99 |
| Olivier Leflaive Frères | Puligny | Puligny-Montrachet 2023 |
| Château-Fuissé | Pouilly-Fuissé | Tête de Cuvée Pouilly-Fuissé 2021 |

#### France — Champagne

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Pol Roger | Épernay | Brut Reserve NV; Rich Demi-Sec NV ($59.99) |
| Valentin Leflaive | Champagne | 5 BdB single-vineyards from Avize, CV, Le Mesnil 2014-2018 |

#### France — Loire / Rhône / Alsace

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Maison Pascal Jolivet | Sancerre | Sancerre Les Caillottes NV ($25.99); Sancerre NV; Attitude Sauvignon Blanc / Pinot Noir 2023 |
| Famille Hugel | Alsace | 11 bottles — Classic Riesling 2015/2017/2024 ($24.99); Gentil Alsace 2016/2017 ($17.99); Riesling Estate 2018 ($35.99); + 5 more |
| Château Mont-Redon | Châteauneuf | CdP 2021; Lirac 2020 ($29.99) |
| Jean-Baptiste Souillard | Crozes-Hermitage | Les Habrards 2017 — $55.99 |
| Domaine Ogereau | Saumur | Rouge Les Tailles 2019 — $29.99 |

#### Italy

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Marchesi di Barolo | Piedmont | 5 bottles — Barolo DOCG 2013/2018, Barbera d'Alba Peiragal 2019, Sarmassa 2016, Sbirolo Nebbiolo 2021 |
| Mauro Veglio | Barolo | Barolo 2018 — $42.99 |
| La Scolca | Gavi | Gavi Bianco Secco NV; Gavi di Gavi NV |
| Eugenio Bocchino | Barolo | Lu Barolo 2017 |
| Le Chiuse | Montalcino | Brunello di Montalcino 2018 — $129.99 |
| Fattoria dei Barbi | Montalcino | Brunello 1973/1975 ($99.99); Brunello 2019 ($59.99); Brunello Riserva 1997 ($299.99) |
| Soldera | Montalcino | Case Basse Toscana 2020 — **$799.99** |
| Melini *(also tagged as Poderi Melini)* | Chianti Classico | La Selvanella Riserva 2017/2019; San Lorenzo 2008 |
| Castello Monaci | Puglia | 5 bottles — Primitivo Pilùna 2021/2023; Salento Coribante; Artas 2019 ($35.99); Kreos Rosé |
| Tenuta Rapitalà | Sicily | 4 bottles — Hugonis Cab-Nero d'Avola 2018; Alto Nero 2016/2022; Viviri Grillo |
| Re Manfredi | Basilicata | Aglianico del Vulture NV |
| Bolla | Veneto | Chianti NV ($7.99) |
| Botter | Veneto | Casa Vinicola Botter Montepulciano d'Abruzzo Organic ERA NV |
| Lamberti | Veneto | Prosecco NV; Prosecco Rosé NV |
| Castelfeder | Alto Adige | Pinot Grigio 2024 — $22.99 |
| Formentini | Collio | Sauvignon 2022 — $19.99 |
| Comm. G.B. Burlotto | Verduno | *(no Raeder's match in snapshot — see false positive note)* |

#### Spain / Portugal

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Bodegas Vega Sicilia | Ribera del Duero | Único Reserva Especial R24 3-pack ($2,999.99); Macán 2018 ($119.99); Alion 2020; Valbuena 2019 |
| Bodegas Fariña *(Banville-correction: see note)* | Toro | *(no real match — earlier "Farina Lugana" was misattributed; that's Italian Banville-imported Farina, not Spanish Fariña)* |
| Piratas del Ebro | Rioja | Rioja NV ($14.99) |

#### USA — California (Napa heavy)

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Ridge Vineyards | Sonoma / Santa Cruz | 5+ bottles — Monte Bello 2022, Estate Cab 2021, Estate Chard 2022, Geyserville 2021 ($59.99), + |
| Stag's Leap Wine Cellars | Napa — Stags Leap District | 5+ bottles incl. Cask 23 2020/2021 ($599.99), Fay 2021 ($199.99), Artemis 2022 |
| Larkmead | Napa | Cab Napa 2011/2019 ($139.99); LMV Salon 2014 ($224.99); Dr. Olmo 2013 ($199.99) |
| PlumpJack | Oakville | Oakville Cab 2021 ($199.99); Reserve Chard 2023 ($65.99); Merlot 2021 ($84.99) |
| Chappellet | Napa — Pritchard Hill | Pritchard Hill Cab 2019/2021; Signature 2022 |
| Darioush | Napa | 5 bottles — Signature Cab 2022 ($149.99), Caravan 2020 ($66.99), Signature Chard 2023, Darius II 2022, Cab Franc 2022 |
| Justin | Paso Robles | 6 bottles — Cab 2019/2022, Isosceles 2014/2019, Reserve Cab 2022 ($65.99), Sauvignon Blanc |
| HALL Wines | Napa | Napa Cab 2020; Sauvignon Blanc 2023; Hall Ranch Reserve Paso 2021; Kathryn Hall Cab 2022 |
| Merry Edwards | RRV | Olivet Lane Chard 2020; Meredith Pinot 2020; Sauvignon Blanc 2023 |
| Cade Estate | Howell Mountain | Cab 2021/2022 |
| Robert Craig | Napa | 4 bottles — Affinity 2018/2019; Spring Mountain Cab 2014 ($99.99); Mt Veeder 2012 |
| Cuvaison | Los Carneros | Pinot Noir Carneros 2021 — $41.99 |
| Hestan Vineyards | Napa | 2 — Meyer Vineyard Cab 2015 ($83.99); Stephanie Cab 2017 |
| Gundlach Bundschu | Sonoma | Pinot Noir Sonoma 2021 — $22.99 |
| Brandlin | Mount Veeder | Cab Mount Veeder 2018 — $99.99 |
| Aperture Cellars | Sonoma | Cab 2021 |
| Altamura | Napa | Cab Napa 2019 |
| Amapola Creek | Sonoma | Amapola Creek Cab 2018; Cuvée Alis 2017 ($29.99) |
| Adaptation / Odette *(same family — Odette Estate)* | Stags Leap | Adaptation by Odette Cab 2018 ($89.99); 2021 |
| Caduceus | Arizona | Nagual De La Naga Red 2021 |
| Clos Du Val | Napa | Cab Napa 2021; Yettalil Red 2019 |
| Clendenen Family Vineyards | Santa Maria | Le Bon Climat Chardonnay 2018 ($59.99) |
| Domaine Anderson | Anderson Valley | Pinot Noir 2017 |
| Knights Bridge | Knights Valley | Cab 2018 |
| Radio-Coteau | Sonoma | La Neblina Pinot 2021; Las Colinas Syrah 2019 |
| Bully Hill Vineyards | NY | Love My Goat Red NV ($9.99) |
| Hindsight | Napa | Cab 2014/2018; Retrospective 20/20 2019 |
| PerUs | California | 3 bottles — Alessio Red 2019; Armaan Cab 2019; Pont Red 2020 |
| Unsorted Wines | California | Sauvignon Blanc 2019 ($12.99) |

#### USA — Oregon / Washington

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Bethel Heights | Eola-Amity | Aeolian Pinot Noir 2012 — $41.99 |
| Long Shadows | Columbia Valley | 5 bottles — Feather Cab 2018; Chester Kidder 2017; Pedestal Merlot 2019; Pirouette 2018; Saggi |
| Owen Roe | OR/WA | Abbot's Table NV ($23.99); Yakima Cab 2017 ($29.99) |

#### Australia / South Africa / Argentina

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| d'Arenberg | McLaren Vale | Coppermine Road 2002; Dead Arm Shiraz 2001 ($99.99); Footbolt Shiraz 2021 ($23.99) |
| Klein Constantia | Constantia | Estate Red Blend NV ($23.99) |
| Bodega Otronia | Patagonia | *(Argentina extreme-south — no Raeder's match in snapshot, but the wiki page exists)* |

#### Austria

| Wildman Producer | Region | Raeder's listings |
|---|---|---|
| Weingut Forstreiter | Kremstal | Grüner Veltliner Alte Reben 2019 |

---

## Kermit Lynch
*30 of 193 portfolio producers at Raeders (67 bottles). Full detail: `wiki/_views/kermit_lynch_at_raeders.md`.*

### France — confirmed at Raeder's (23 producers)

| KL Producer | KL Region | Raeder's listings (cuvée / vintage / price) |
|---|---|---|
| [[lucien_boillot\|Domaine Lucien Boillot et Fils]] | Burgundy | 9 bottles incl. Gevrey-Chambertin 1er Cru La Perrière 2019, Les Corbeaux 2017 ($119.99), Volnay 1er Cru Les Brouillards 2017 ($99.99), Pommard 2019 ($94.99), NSG 1er Cru Pruliers 2017 ($149.99) |
| Albert Boxler | Alsace | Riesling Reserve 2023 — $74.99 |
| Champalou | Loire | Vouvray Pétillant Brut NV — $25.99 |
| Daniel Chotard | Loire | Sancerre 2023 — $39.99 |
| Domaine Coche-Dury | Burgundy | Meursault 2022 — $1,299.99 |
| Bruno Colin | Burgundy | Bâtard-Montrachet GC 2022 ($1,499.99); Chassagne-Montrachet 1er La Maltroie 2022 ($229.99); Bourgogne Aligoté 2022 ($49.99) |
| Domaine de Villaine | Burgundy | A. & P. de Villaine Mercurey "Les Montots" 2022 ($89.99); Bouzeron Aligoté 2022 ($54.99); Rully 1er Champs Cloux 2021; Rully Blanc 1er Cru 2021 |
| Domaine Robert-Denogent | Burgundy | Pouilly-Fuissé 1er Cru Vers Cras VV 2021 ($99.99); Mâcon-Fuissé Les Taches 2017 ($53.99) |
| Domaine Follin-Arbelet | Burgundy | Romanée-St-Vivant 2014 |
| Domaine Gachot-Monot | Burgundy | Côtes de Nuits-Villages 2022 — $49.99 |
| M. & C. Lapierre | Beaujolais | M. Lapierre Morgon NV ($45.99); Lapierre Le Beaujolais NV ($39.99) |
| Domaine Roland Lavantureux | Burgundy | Chablis Vauprin 2022 ($69.99); Chablis Bougros 2022 |
| Domaine de Marquiliani | Corsica | Le Rosé Gris de Pauline 2023 — $32.99 |
| Domaine Jean-Claude Marsanne | Northern Rhône | Saint-Joseph 2022 — $49.99 |
| [[meo_camuzet\|Domaine Méo-Camuzet]] | Burgundy | 12 bottles incl. Vosne-Romanée Au Cros Parantoux 2023 ($2,499.99), NSG Aux Murgers 2018/2020 ($329-359), Corton-Charlemagne GC 2022 ($599.99), Vosne-Romanée Les Chaumes 2019/2022/2023, Echezeaux GC, Clos de Vougeot GC |
| Domaine de la Prébende | Beaujolais | Beaujolais 2023 — $19.99 |
| Domaine Hippolyte Reverdy | Loire | Sancerre 2024; Sancerre Rouge 2023 ($31.99) |
| Domaine la Roquète | Southern Rhône | Châteauneuf-du-Pape Clos La Roquète Blanc NV — $53.99 *(Brunier sister estate)* |
| Domaine Roulot | Burgundy | Bourgogne Blanc 2023 ($129.99); Monthélie Rouge 2022 ($149.99); Bourgogne Aligoté 2023 ($79.99) |
| Clos Sainte Magdeleine | Provence | Côtes de Provence Rosé 2023 — $29.99 |
| Famille Savary | Burgundy | Chablis 2023 ($37.99); Chablis Sélection VV 2022 |
| Domaine du Vieux Télégraphe | Southern Rhône | Châteauneuf-du-Pape White La Crau 2020 — $99.99 |

### Italy — confirmed at Raeder's (7 producers)

| KL Producer | KL Region | Raeder's listings |
|---|---|---|
| Benevelli Piero | Piedmont | Barbera d'Alba Bricco Del Pilone 2017 — $29.99 |
| Castagnoli | Tuscany | Chianti Classico Riserva Terrazze 2013 ($45.99); Salita Toscana 2013 ($59.99) |
| A. & G. Fantino | Piedmont | Alessandro & Gian Natale Fantino "Rosso dei Dardi" Nebbiolo 2017 — $22.99 |
| Villa di Geggiano | Tuscany | Chianti Classico Riserva 2016 — $52.99 |
| Silvio Giamello | Piedmont | Barbaresco Vincenziana 2021 |
| Giuseppe Quintarelli | Veneto | Valpolicella Classico Sup 2018 ($139.99); Cà del Merlo 2018 ($129.99); Primofiore 2023 ($89.99); Cabernet Alzero 2017 |
| Sesti | Tuscany | Brunello di Montalcino 2019 ($599.99) + 2020 ($129.99); Brunello "Phenomena" Riserva 2018 |
| Tintero | Piedmont | Elvio Tintero Vino Bianco Secco NV — $14.99 |

---

## Polaner Selections
*24 of 323 portfolio producers at Raeders (58 bottles). Full detail: `wiki/_views/polaner_at_raeders.md`.*

### Confirmed at Raeder's

#### Champagne (1 bottle)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Larmandier-Bernier | Vertus | Vieille Vigne Du Levant Grand Cru Extra Brut 2014 |

#### Burgundy (1 bottle)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Morin Père & Fils *(probable — Polaner lists "Morin" under Burgundy)* | Beaune | Puligny-Montrachet 2021 — $99.99 |

#### Bordeaux (1 bottle, ambiguous)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Château Lamothe de Haux *(probable — multiple Lamothe châteaux in Bordeaux)* | Bordeaux | Bordeaux White NV — $17.99 |

#### Italy — Piedmont (18+ bottles)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Roagna | Barbaresco / Barolo | 6 bottles incl. Barbaresco Pajé 2017 ($189.99); Pajé Vecchie Viti 2017/2018 ($359.99); Barolo Pira Vecchie Viti 2017; Barolo Rocche di Castiglione 2020 ($229.99); Langhe Rosso 2020 ($59.99) |
| Giacomo Conterno | Serralunga | Barolo Cerretta 2021 — **$379.99** |
| Giuseppe Mascarello | Castiglione Falletto | Barolo Monprivato 2017 ($249.99); Langhe Nebbiolo 2022 |
| Oddero *(Poderi e Cantine Oddero)* | La Morra | Barolo Brunate 2017; Barolo Riserva Vigna Rionda 2019 |
| Paitin | Treiso | Sorì Paitin Barbaresco Vecchie Vigne 2000 — $184.99 |
| Francesco Rinaldi | Barolo | Barolo Cannubi 2020 |
| Trediberri | La Morra | Barolo Berri 2019 ($49.99); Rocche dell'Annunziata 2017 ($99.99) |

#### Italy — Tuscany / Veneto (4 bottles)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Felsina *(Fattoria di Felsina)* | Chianti Classico | Chianti Classico Berardenga NV — $29.99 |
| Montepeloso | Maremma | Nardo IGT 2004 ($104.99); Toscana Eneo 2010 ($54.99) |
| Bussola | Valpolicella | Amarone della Valpolicella Classico 2013 — $99.99 |

#### Spain (3 bottles)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Descendientes de J. Palacios | Bierzo | Corullón Bierzo 2016 ($52.99); Petalos del Bierzo NV ($20.99) |
| Álvaro Palacios | Priorat / Rioja | Priorat Finca Dofí 2020 — $99.99 |

#### USA — California (30+ bottles)

| Polaner Producer | Region | Raeder's listings |
|---|---|---|
| Carlisle | Sonoma | ~10 bottles incl. Carlisle Vineyard Zin 2007/2013/2014, Montafi Ranch Zin 2014 ($54.99), Petite Sirah Palisade 2010, Derivative White 2012, Two Acres Red 2008, Dry Creek Zin 2010 |
| Bedrock | Sonoma | 5 bottles incl. Evangelho Vineyard Red 2012/2013, Heritage 2013 ($54.99), Pagani Ranch 2014, Carlisle Vineyard Zin 2014 |
| Maybach | Napa | 5 bottles incl. Amoenus Cab 2017 ($205.99), Irmgard Pinot 2012/2018/2019, Eterium Thieriot Chard 2018 |
| Walter Hansel | Sonoma | Pinot Noir Cuvée Alyce 2022 ($49.99); North Slope 2022 ($49.99); Estate RRV 2022 ($43.99) |
| Varner | Santa Cruz | 4 Chardonnays from Spring Ridge Vineyard (Amphitheater / Bee / Home blocks) 2009-2010 |
| Caterwaul | Napa | Cabernet Sauvignon 2020 ($64.99); 2021 ($69.99) |
| Rivers Marie | Napa | Cabernet Sauvignon Napa 2023 ($139.99); Calistoga Cab 2023 ($149.99) |
| Foxglove *(probable)* | Paso Robles | Zinfandel Paso Robles 2011 |
| Red Car *(probable)* | Sonoma Coast | Trolley Pinot Noir 2007 — $79.99 |

---

## Skurnik
*32 of 443 portfolio producers at Raeders (53 bottles). Full detail: `wiki/_views/skurnik_at_raeders.md`.*

### Confirmed at Raeder's

#### France (6 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Domaine François Mikulski | Burgundy — Hautes Côtes de Beaune | Chardonnay 2023 ($79.99); 2022 ($69.99) |
| Domaine de la Madone | Beaujolais | Beaujolais-Villages Nouveau NV ($12.99); 2018 |
| Paul Durdilly et Fils | Beaujolais | *(as "Pierre & Paul Durdilly")* Beaujolais Nouveau Les Grandes Coasses NV — $10.99 |
| Château Beausejour *(ambiguous — multiple St-Em estates)* | Bordeaux | St-Émilion 1970 — $199.99 |
| Château du Rouët | Provence | Rosé Côtes de Provence NV — $14.99 |

#### Germany (2 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Selbach-Oster *(Skurnik lists three variants: J & H Selbach / Selbach / Selbach-Oster — same family)* | Mosel | Zeltinger Himmelreich Riesling Eiswein 2001 |
| Strub | Rheinhessen | Niersteiner Paterberg Riesling Eiswein 2001 — $89.99 |

#### Italy (7 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Paolo Scavino | Piedmont | Barolo Rocche dell'Annunziata Riserva 2015 ($239.99); Sorriso Bianco 1999 ($49.99) |
| La Spinetta | Piedmont | Moscato d'Asti Bricco Quaglia NV — $19.99 |
| Mocali | Tuscany — Montalcino | Brunello di Montalcino 1997 — $149.99 |
| La Serena | Tuscany — Montalcino | Brunello di Montalcino Riserva Gemini 2015 — $109.99 |
| Uccelliera *(at Raeder's as "Fattoria Uccelliera")* | Tuscany — Montalcino | Brunello di Montalcino Riserva 2016 — $169.99 |
| Cosimo Taurino *(at Raeder's as "Taurino")* | Puglia | Patriglione 1997 — $79.99 |

#### Spain (7 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| La Rioja Alta | Rioja | 904 Gran Reserva 2016; Viña Alberdi Reserva NV; Viña Ardanza Reserva Especial 2019 ($46.99) |
| Clos Mogador | Priorat | Priorat 2017 ($109.99); Priorat Gratallops 2022 ($128.99) |
| El Espectacle de Montsant | Catalunya — Montsant | Espectacle de Montsant 2008 — $134.99 |
| Raventós i Blanc | Conca del Riu Anoia | Cava Brut L'Hereu 2023 — $26.99 |

#### USA — California (15+ bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Ramey Wine Cellars | Sonoma | 5 bottles incl. Annum Cab 2011, Chardonnay Fort Ross-Seaview 2022 ($59.99), Chardonnay RRV 2022/2023, Rodgers Creek Syrah 2010 ($89.99) |
| Peter Michael Winery | Knights Valley | Au Paradis Cab 2021 ($289.99); L'Esprit des Pavots 2020 ($149.99); L'Après-Midi Sauv Blanc 2023 ($85.99) |
| Mayacamas Vineyards | Mount Veeder | Cab Mount Veeder 2020; 2021 |
| Bonny Doon Vineyard | Santa Cruz | Le Vol Des Anges 2007 ($30.99); Albarino Ca del Solo NV |
| Turley | Statewide Zin | Old Vine Zinfandel California 2022 ($39.99); 2023 ($39.99) |
| Kistler Vineyards | Sonoma | Pinot Noir Russian River Valley 2023 — $99.99 |
| O'Shaughnessy | Howell Mountain | Cabernet Sauvignon Howell Mountain 2022 — $125.99 |
| Failla | Sonoma Coast | Pinot Noir Sonoma 2023 — $39.99 |
| Jax Vineyards | Napa | Y3 Taureau Red 2022 — $27.99 |

#### USA — Oregon (7 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Patricia Green Cellars | Willamette | 3 Pinots — Balcombe 2022 ($64.99), Estate Old Vine 2022 ($44.99), Willamette Reserve 2023 ($29.99) |
| Cristom Vineyards | Eola-Amity Hills | Pinot Noir Jessie Vineyard 2016 ($74.99); Mt. Jefferson Cuvée 2014 ($79.99) |
| Evening Land Vineyards | Eola-Amity | Seven Springs Estate Summum Pinot Noir 2021 — $119.99 |
| Shea Wine Cellars | Yamhill-Carlton | Pinot Noir Willamette Estate 2021 — $45.99 |

#### USA — Washington (5 bottles)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Cayuse Vineyards *(cult)* | Walla Walla | Syrah Cailloux 2021 ($139.99); Camaspelo 2013/2014 ($109.99 each); Syrah En Cerise 2018/2021 |

#### USA — New York (1 bottle)

| Skurnik Producer | Region | Raeder's listings |
|---|---|---|
| Hermann J. Wiemer Vineyard | Finger Lakes | Johannisberg Riesling Semi-Dry NV — $18.99 |

---

## Grand Cru Selections
*19 of 72 portfolio producers at Raeders (35 bottles). Full detail: `wiki/_views/grand_cru_at_raeders.md`.*

### Confirmed at Raeder's

#### Champagne (2 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Pierre Péters | Le Mesnil — Grand Cru | Montjolys Blanc de Blancs 2017 ($329.99); Cuvée Reserve Blanc de Blancs NV ($79.99) |

#### Burgundy — Côte d'Or (15 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Georges Roumier | Chambolle-Musigny | **Ruchottes-Chambertin GC 2023 — $1,799.99**; Bonnes-Mares GC 2022 |
| Domaine des Comtes Lafon | Meursault | Meursault Porusots 1er Cru 2022 — $469.99 |
| Domaine Roulot ⚠️ *also on Kermit Lynch paste — see conflict* | Meursault | Monthélie Rouge 2022 ($149.99); Bourgogne Blanc 2023 ($129.99); Bourgogne Aligoté 2023 ($79.99) |
| Fourrier Estate *(incl. JM Fourrier's "Comte de Chapelle" négoce)* | Gevrey-Chambertin | Corton-Charlemagne GC 2022 ($799.99); Comte de Chapelle Puligny 2022 ($139.99); Meursault 2022 ($129.99); Bourgogne Blanc 2022 ($59.99) |
| Dominique Lafon *(négoce label)* | Côte de Beaune | Beaune 1er Cru Les Avaux 2020 |
| Domaine des Croix | Beaune | Beaune 1er Cru Les Cents Vignes 2022 |
| Génot-Boulanger | Côte de Beaune | Pommard Vieilles Vignes 2022 |

#### Burgundy — Mâconnais (1 bottle)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Château des Quarts | Pouilly-Fuissé | Clos des Quarts PF 1er Cru Aux Quarts 2022 |

#### Chablis (1 bottle)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Moreau-Naudet | Chablis | Petit Chablis 2023 |

#### Beaujolais (2 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Chapel | Fleurie | Fleurie Charbonniers 2022 |
| Anne-Sophie Dubois | Fleurie | Fleurie L'Alchimiste 2023 — $39.99 |

#### Rhône (5 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Jean-Louis Chave *(+ Chave Selections — bottles overlap)* | Hermitage / Crozes | Hermitage Blanc 2021 ($369.99 — Estate); Hermitage Farconnet 2021 (Selections); Crozes-Hermitage Silène 2023 ($34.99 — Selections) |
| Domaine Brun-Avril | Châteauneuf-du-Pape | CdP 2020 |
| Clusel-Roch | Côte-Rôtie | Les Schistes 2022 — $99.99 |

#### Loire (4 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Arnaud Lambert | Saumur | Saumur Blanc La Rue Brézé 2020; Saumur-Champigny Montée des Roches 2021; Saumur Rouge Tue-Loup 2021 ($39.99) |
| Domaine Siret-Courtaud | Quincy | Quincy 2023 — $29.99 |

#### Bordeaux — Pomerol (8 bottles)

| GCS Producer | Region | Raeder's listings |
|---|---|---|
| Château Lafleur | Pomerol (grand cru) | Pomerol 2020 ($1,079.99); Pomerol 2012 ($899.99); Pensées de Lafleur 2014 ($249.99); 2011 ($249.99); 2019; 2002 |
| Château Bourgneuf | Pomerol | Pomerol 2018 ($99.99); Saisons de Bourgneuf Pomerol 2023 ($59.99) |

---

## Vineyard Brands
*9 of 127 portfolio producers at Raeders (19 bottles). Full detail: `wiki/_views/vineyard_brands_at_raeders.md`.*

### Headline bottles

- **Château Pétrus Pomerol 1967** — **$3,499.99** *(2nd highest in Raeder's after DRC Corton-Charlemagne 2022 $4,999.99)*
- **Château La Fleur-Pétrus Pomerol 2018** — **$1,699.99**
- Château La Fleur-Pétrus Pomerol 2016 — $799.99
- Château de Beaucastel CdP 1999 — $599.99
- Henri Boillot Meursault Genevrières 2023 — $319.99 *(note: Henri Boillot is NOT on the VB paste — only Jean-Marc Boillot — so this bottle is misattributed by the matcher; see "False positives" below)*
- Ponsot Morey-St-Denis Cuvée des Alouettes 2016 — $279.99
- Château Beaucastel CdP 1989 — $239.99

### Confirmed at Raeder's

#### France — Bordeaux (Right Bank — Pomerol)

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Pétrus + Château La Fleur-Pétrus *(JP Moueix portfolio)* | Pomerol | **7 bottles** — Château Pétrus 1967 ($3,499.99); Château La Fleur-Pétrus 2018 ($1,699.99), 2016 ($799.99), 2017, 2020, 2022 |

#### France — Rhône (Châteauneuf)

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Famille Perrin / Château de Beaucastel | CdP | 4 bottles — Château Beaucastel CdP 1989 ($239.99), 1999 ($599.99); Château de Beaucastel CdP 2021 ($99.99), 2022 |

#### France — Burgundy

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Ponsot *(Domaine + Laurent — split brand)* | Morey-St-Denis | Morey-St-Denis Cuvée des Alouettes 2016 — $279.99 |
| Henri Gouges | Nuits-Saint-Georges | Domaine Henri Gouges NSG 2017 — $79.99 |
| Thibault Liger-Belair | NSG | NSG La Charmotte 2019 |
| Jean-Marc Boillot | Beaune | Beaune 1er Cru Épenottes 2020 |

#### France — Loire / Languedoc

| VB Producer | Region | Raeder's listings |
|---|---|---|
| J. de Villebois | Loire — Pouilly-Fumé | "Les Silex Blancs" Pouilly-Fumé 2023 — $59.99 |
| Hecht & Bannier | Languedoc | Minervois 2015 ($20.99); Côtes de Provence Rosé NV ($18.99) |

#### Italy — Friuli

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Gradis'ciutta | Friuli — Collio | Ribolla Gialla 2020 — $22.99 |

#### USA — California

| VB Producer | Region | Raeder's listings |
|---|---|---|
| Forman Vineyard | Napa | Cabernet Sauvignon Napa 2016 |

---

## Neal Rosenthal
*9 of 145 portfolio producers at Raeders (18 bottles). Full detail: `wiki/_views/rosenthal_at_raeders.md`.*

### Confirmed at Raeder's (9 producers)

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

---

## David Bowler Wine
*14 of 309 portfolio producers at Raeders (17 bottles). Full detail: `wiki/_views/bowler_at_raeders.md`.*

### Confirmed at Raeder's

#### France — Burgundy

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Chandon de Briailles *(flipped from Skurnik → Bowler this commit)* | Pernand-Vergelesses | Pernand-Vergelesses Les Vergelesses 1er Cru NV |

#### France — Rhône (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Famille Isabel Ferrando *(Domaine Saint-Préfert)* | Châteauneuf-du-Pape | CdP Rouge 2020 — $115.99 |

#### Italy (3 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Schiavenza | Piedmont — Serralunga | Barolo Vigna Broglio 2013 — $49.99 |
| Arianna Occhipinti | Sicily — Vittoria | Il Frappato Terre Siciliane 2021 — $53.99 |
| La Gerla | Tuscany — Montalcino | Brunello di Montalcino Riserva gli Angeli 2007 |

#### Portugal — Douro (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Quinta do Infantado | Douro | Vintage Port 1992 — $99.99 |

#### Spain (2 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Terroir al Limit | Priorat | Historic Red 2018 — $32.99 |
| Lopez de Heredia | Rioja | Viña Tondonia Reserva 2012 |

#### USA — California (3 bottles)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Philip Togni Vineyard | Napa — Spring Mountain | Cab Napa 2018 ($189.99); 2019 ($189.99) |
| Mount Eden Vineyards | Santa Cruz Mountains | Pinot Noir Estate 2012 — $69.99 |

#### USA — Oregon (1 bottle)

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Nicolas-Jay | Willamette | L'Ensemble Pinot Noir 2021 — $79.99 |

#### USA — Washington (5 bottles) — cult Walla Walla

| Bowler Producer | Region | Raeder's listings |
|---|---|---|
| Leonetti | Walla Walla | Cab 2012 ($144.99); Reserve Cab 2005 ($169.99); Reserve Cab 2009 ($175.99) |
| Quilceda Creek | Columbia Valley | Cab Columbia Valley 2015 — **$209.99** |
| Figgins | Walla Walla | Estate Red 2012 — $139.99 |

---

## Banville Wine Merchants
*12 of 59 portfolio producers at Raeders (13 bottles). Full detail: `wiki/_views/banville_at_raeders.md`.*

### Confirmed at Raeder's

#### France — Burgundy (Côte de Nuits high-end)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Domaine Jean-Jacques Confuron | Vosne-Romanée | Romanée-Saint-Vivant Grand Cru 2016 — **$899.99** |
| Domaine Odoul-Coquard | Morey-Saint-Denis | Vosne-Romanée 2021 — $179.99 |
| Meurgey-Croses *(also listed by Banville as "Pierre Meurgey")* | Mâconnais | St-Véran 2019 — $29.99 |

#### France — Bordeaux / Provence (2 bottles)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Château du Gazin *(ambiguous — multiple Gazin properties)* | Bordeaux | Château Gazin Pomerol 1970 — $149.99 |
| Château l'Escarelle | Provence | Côtes de Provence Rosé NV |

#### Argentina (1 bottle)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Andeluna | Mendoza | 1300 NV — $19.98 |

#### Italy (7 bottles)

| Banville Producer | Region | Raeder's listings |
|---|---|---|
| Tenuta di Trinoro | Tuscany — Sarteano | Le Cupole Rosso NV — $69.99 *(Andrea Franchetti)* |
| Parusso | Barolo | Barolo Perarmando 2017 — $59.99 |
| Tolaini | Tuscany — Chianti Classico | Valdisanti 2015; 2019 |
| Terlano *(at Raeder's as "Cantina Sociale Terlano")* | Alto Adige | Pinot Grigio Alto Adige NV |
| Illuminati | Abruzzo | Montepulciano d'Abruzzo Riparosso NV |
| Farina | Veneto/Lombardy | Lugana NV — $17.99 *(see Wildman correction below)* |

---

## Becky Wasserman & Co.
*(brokerage) of 132 portfolio producers at Raeders (— bottles). Full detail: `wiki/_views/wasserman_at_raeders.md`.*

### Newly resolved at Raeder's

#### Burgundy — Côte d'Or (3 bottles)

| Wasserman Producer | Region | Raeder's listings |
|---|---|---|
| Comte Georges de Vogüé | Chambolle-Musigny | **Bonnes-Mares Grand Cru 2016 — $799.99** |
| Camille Giroud | Beaune négoce | Morey-St-Denis 1er Cru Clos des Godelles 2019 — $99.99 |
| Pierre Morey | Meursault | Bourgogne Aligoté 2023 — $38.99 |

---

## Wine Source
*1 of 12 portfolio producers at Raeders (3 bottles). Full detail: `wiki/_views/wine_source_at_raeders.md`.*

### Confirmed at Raeder's

#### Burgundy (3 bottles)

| Wine Source Producer | Region | Raeder's listings |
|---|---|---|
| Yann Durieux *(project name "Recrue des Sens" — Raeder's stores as "Yann Durieux")* | Hautes-Côtes de Nuits | Gevrey-Chambertin **Grand Cru** 2020 — **$499.99**; La Gouzotte Rouge 2021 — $119.99; Love And Pif Blanc 2021 — $74.99 |
---

## Roscioli Wine Club
*8–9 of 146 list profiles at Raeders (~20 bottles). Full detail: `wiki/_views/raeders_importer_list_overlap_2026_06.md`. Roscioli is an Italian wine-club/curator list (not one of the 13 pasted US-importer portfolios) — included here for completeness.*

### Confirmed at Raeders

| Roscioli producer | Region | Raeders example | Price |
|---|---|---|---:|
| **[[roagna\|Roagna]]** | Langhe · Barbaresco | Barbaresco Pajé 2017 | $189.99 |
| **Braida** | Monferrato · Barbera | Bricco dell'Uccellone Barbera 2020 | $89.99 |
| **Cantina Sobrero** | Castiglione Falletto · Barolo | Ciabot Tanasio Barolo 2016 | $59.99 |
| **Castello dei Rampolla** | Panzano in Chianti | Sammarco Toscana 2019 | $109.99 |
| **Lamole di Lamole** | Chianti Classico | Chianti Classico Maggiolo 2022 | $20.99 |
| **Le Macchiole** | Bolgheri | Toscana Paleo Red 1995 | $189.99 |
| **Christof Tiefenbrunner** | Alto Adige · Schiava | Pinot Grigio | $15.99 |
| **Paitin** | Langhe · Barbaresco | Sorì Paitin Barbaresco Vecchie Vigne 2000 | $184.99 |
| **Enrico Rizzi** *(probable)* | Langhe · Barbaresco | Rizzi Barbaresco 2016 | $41.99 |

---

*Consolidated 2026-06-13 from the 13 per-importer `*_at_raeders.md` views (portfolios pasted 2026-05-21) plus the Roscioli overlap view. Counts are conservative whole-token matches against the 2026-04-25 Raeders snapshot; `$0.00`/unpriced source listings are omitted from example columns. Inventory turns over — treat bottle-level detail as indicative.*
