---
type: view
updated: 2026-05-26
question: "Which of the 227 FASS unmatched producers should be onboarded — and which spelling variants should consolidate?"
source: build/fass_ingest_report.md
total_unmatched_rows: 227
distinct_producers_after_alias_merge: ~110
---

# FASS Unmatched — Triage (2026-05-26)

> **Progress — 2026-07-22:** first onboarding batch executed. 12 iconic on-taste
> Tier-1 producers created ([[jean_michel_stephan|J-M Stéphan]], [[domaine_blachon|Blachon]],
> [[philippe_naddef|Naddef]], [[perseval_farge|Perseval-Farge]], [[paul_weltner|Weltner]],
> [[david_leclapart|Léclapart]], [[joh_jos_prum|J.J. Prüm]], [[markus_molitor|Molitor]],
> [[martin_muellen|Müllen]], [[domaine_des_roches_neuves|Roches Neuves]],
> [[yvon_metras|Métras]], [[gut_hermannsberg|Gut Hermannsberg]]), six enriched with
> current Gmail offer data. Cross-source consolidation: Gonon, Pierre Brisset and
> JJ Girard were already in the vault under other slugs (`domaine_pierre_gonon`,
> `maison_pierre_brisset`, `jean_jacques_girard`) — aliased in `ingest_fass.py`, not
> re-created. **~60 Tier-1 producers still queued** below. The weekly Gmail sweep
> ([[retailer_email_offers_2026_07|offers view]]) will keep surfacing the rest.

The FASS rebuild matched only 14 of ~110 distinct producers in the portfolio.
The other ~96 are real producers, mostly NEW to the wiki. This view triages
each one against Evan's curation filters (CLAUDE.md) into onboard / watch /
skip, and identifies the spelling-variant dupes inside the unmatched list.

## How to read

- **Tier 1 — Onboard now** (~50). Iconic or directly-Evan-style; create a
  producer page from this triage row + the FASS portfolio data + a quick web
  pass. After creating, re-run `scripts/ingest_fass.py` to fold them in.
- **Tier 2 — Worth watching** (~20). Plausibly-fit producer but needs a
  little research before committing to a page (style, farming, importer).
- **Tier 3 — Skip** (~40). Generic mid-tier, broken/split row in the raw
  data, or single-bottle obscure with no Evan-style hook.
- **Alias-only** (~25 variant rows). Pure spelling/typo dupes of another
  unmatched entry; consolidates into one canonical producer.

Onboarding flow per Tier 1 producer:
1. Add an entry to `FASS_ALIASES` in `scripts/ingest_fass.py` pointing
   the canonical retailer spelling at the new slug.
2. Create `wiki/producers/<slug>.md` with frontmatter per `_SCHEMA.md`.
3. Re-run `scripts/ingest_fass.py` → `scripts/build_rollups.py` →
   `scripts/build_wiki_index.py`.

---

## Tier 1 — Onboard now

### Rhône (Northern, Cornas/Côte-Rôtie/Saint-Joseph cluster)

FASS's deepest stylistic strength. All terroir-driven grower-scale, fits
Evan's Rhône taste profile.

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `markus_molitor` | Markus Molitor (+ typo `Markus Moitor`) | 35 | $26–$116 | Iconic Mosel — actually goes in Mosel section below |
| `julien_barge` | Julien Barge | 19 | $44–$139 | Côte-Rôtie grower; Coeur de Combard + Les Côtes vertical |
| `compagnie_de_lhermitage` | Compagnie de lHermitage / Compagnie L'Hermitage / Compagnie l'Hermitage | 15 | $29–$162 | Lyle Fass's negociant project — already has 1 CSW-side article (`raw/fass/articles.csv` La Brocarde) |
| `lyle_fass_lelektsoglou` | Lyle Fass Charalambos Lelektsoglou / Georges Lelektsoglou / Hector Adrien Charalambos Lelektsoglou | 4 | $29–$68 | Same Greek-led negociant; the Lyle Fass house wine. **Merge with `compagnie_de_lhermitage`.** |
| `cuchet_beliando` | Cuchet Beliando (+ `Cuchet-Beliando Cornas` row) | 11 | $95–$117 | Cornas specialist, vintage-vertical pricing |
| `guillaume_gilles` | Guillaume Gilles | 10 | $52–$90 | Cornas grower; Robert Michel's heir (cellar style) |
| `domaine_du_tunnel` | Domaine du Tunnel (+ broken `Domaine du`) | 12 | $50–$110 | Stéphane Robert Cornas / Saint-Péray icon |
| `domaine_des_pierres_seches` | Domaine des Pierres Seches (+ broken `Domaine des`) | 14 | $29–$77 | Saint-Joseph terroir-driven |
| `gerard_courbis` | Gerard Courbis / Gerard Courbis et Fils / Gerard Courbis Pere & Fils | 8 | $50–$70 | Saint-Joseph / Cornas grower |
| `ludovic_courbis` | Ludovic Courbis | 4 | $68–$70 | Cornas; Gérard's son's project |
| `jacques_lemenicier` | Jacques Lemenicier | 7 | $42–$102 | Cornas grower |
| `mickael_bourg` | Mickael Bourg / Mikael Bourg | 10 | $37–$72 | Cornas Les P'tits Bout — Vincent Paris alum |
| `emmanuel_verset` | Emmanuel Verset | 2 | $60–$83 | Cornas Signature — Allemand's protege |
| `emmanuel_darnaud` | Emmanuel Darnaud | 2 | $42–$54 | Crozes-Hermitage / Saint-Joseph |
| `andre_francois` | Andre Francois | 5 | $20–$45 | Côte-Rôtie / Condrieu / Collines Rhodaniennes — value tier |
| `nicolas_champagneaux` | Nicolas Champagneaux | 3 | $68–$110 | Côte-Rôtie La Brocarde / La Dedicace |
| `jean_michel_stephan` | Jean Michel Stephan | 4 | $146–$155 | Côte-Rôtie natural Coteaux du Bassenon — iconic natural Rhône |
| `domaine_saint_damien` | Domaine Saint-Damien | 2 | $32–$32 | Gigondas VV |
| `domaine_de_cote_epine` | Domaine de Cote Epine / Domaine de la Cote St Epine | 5 | $26–$52 | Saint-Joseph VV Cuvée Spéciale |
| `domaine_blachon` | Domaine Blachon / Cave Sebastien Blachon | 4 | $45–$66 | Saint-Joseph Margariat / Isaline |
| `elie_bancel` | Elie Bancel | 1 | $95 | Cornas grower |
| `maison_alexandrins` | Maison Alexandrins | 7 | $43–$90 | Hermitage / Cornas négoce |
| `e_guigal` | E. Guigal | 6 | (3-pack pricing) | The LaLas (Mouline/Turque/Landonne) plus single bottles. Cellar-tier; price garbage in raw, fix manually |

### Burgundy (Côte d'Or grower cluster)

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `pierre_brisset` | Pierre Brisset / Maison Brisset / Pierre Briseet (typo) | 50 | $39–$325 | Echezeaux Grand Cru + Chambolle/Vosne 1er Cru tier; FASS's Burgundy flagship |
| `jj_girard` | JJ Girard / J.J. Girard | 24 | $32–$120 | Beaune/Pommard/Volnay 1er Cru grower |
| `chavy_chouet` | Chavy-Chouet | 17 | $35–$134 | Meursault / Puligny / St. Aubin grower icon (Hubert Chavy) |
| `julien_cruchandeau` | Julien Cruchandeau | 17 | $24–$68 | Hautes-Côtes / Ladoix / St-Aubin grower, value-tier biodynamic-leaning |
| `laurent_boussey` | Laurent Boussey (+ `Laurent & Karen Boussey`) | 18 | $33–$92 | Volnay / Monthelie 1er Cru grower |
| `domaine_berlancourt` | Domaine Berlancourt | 16 | $28–$60 | Pinault's Burgundy entry (Bourgogne tier) |
| `remi_poisot` | Remi Poisot | 12 | $40–$600 | Romanée-St-Vivant + Corton Charlemagne GC tier; serious house |
| `vincent_ledy` | Vincent Ledy | 5 | $39–$78 | Hautes-Côtes / NSG 1er Cru grower |
| `dubreuil_fontaine` | Dubreuil-Fontaine | 2 | $88–$90 | Corton Bressandes / Clos du Roi |
| `garaudet` | Garaudet / Garaudet Pere & Fils / SARL Garaudet / SARL Garaudet Pere & Fils / Sarl Garaudet Pere et Fils | 11 | $29–$85 | Monthelie / Meursault grower (Pierre Garaudet) |
| `philippe_naddef` | Philippe Naddef / Phillippe Naddef / Domaine Philippe / Domaine Philippe Naddef / Michel Naddef / Philippe Nadeff | 8 | $39–$282 | Gevrey-Chambertin / Marsannay / Fixin grower |
| `daniel_etienne_defaix` | Daniel-Etienne Defaix / Domaine Daniel-Etienne Defaix | 5 | $50–$66 | Chablis 1er Cru Les Lys / Côte de Léchet / Vaillons — classic |
| `jean_dauvissat` | Jean Dauvissat / Jean Dauvissat Pere & Fils / Jean Dauvissat Père & Fils | 13 | $29–$58 | Chablis 1er Cru grower (Cote de Lechet, Vaillons, Montmains, Fourchame) |
| `laurent_tribut` | Laurent Tribut | 4 | $58–$69 | Chablis 1er Cru (Vincent Dauvissat's brother-in-law) |
| `sebastien_dampt` | Sebastien Dampt / Sébastien Dampt | 13 | $23–$62 | Chablis 1er Cru (Vaillons / Cote de Léchet / Beugnons) |
| `domaine_servin` | Domaine Servin | 2 | $35–$85 | Chablis Grand Cru Les Clos |

### Loire

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `domaine_des_roches_neuves` | Domaine des Roches Neuves | 18 | $42–$85 | Thierry Germain — iconic biodynamic Saumur-Champigny (Franc de Pied, Clos de l'Echelier) |
| `domaine_clos_de_lecotard` | Domaine Clos de lEcotard | 2 | $70–$70 | Saumur Blanc Les Pentes — Antoine Sanzay project |

### Beaujolais

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `yvon_metras` | Yvon Metras / Yvon Métras | 3 | $47–$49 | Iconic natural Fleurie (Gang of Four–adjacent) |
| `jean_foillard` | Jean Foillard | 1 | $25 | Iconic natural Morgon (Gang of Four) |
| `chateau_thivin` | Chateau Thivin | 9 | $37–$58 | Iconic Côte-de-Brouilly (Zaccharie, La Chapelle, Les Griottes) |
| `lafarge_vial` | Lafarge Vial | 2 | $38 | Frédéric Lafarge × Chantal Vial Fleurie project |
| `domaine_du_vissoux` | Domaine du Vissoux | 1 | $26 | Pierre-Marie Chermette Fleurie Poncié — classic |

### Champagne (grower / late-disgorged tier)

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `caillez_lemaire` | Caillez-Lemaire (+ "Pur Meunier" Brut Nature variant row) | 13 | $38–$120 | Grower; Vinootheque 2008, Cuvée Jadis, Pur Meunier |
| `marie_demets` | Marie Demets | 15 | $34–$88 | Grower Extra-Brut (Intransigeance, Les Fins, La Forêt) |
| `clement_perseval` | Clément Perseval | 7 | $99–$155 | Grower 1er Cru (La Luth, Les Tremblaies, Les Rouleaux) |
| `perseval_farge` | Perseval Farge / Perseval-Farge | 5 | $98–$125 | 1er Cru Chamery grower |
| `pierre_callot` | Pierre Callot | 2 | $46–$47 | Avize Grand Cru BdB grower |
| `pierre_moncuit` | Pierre Moncuit | 1 | $53 | Les Mesnil-sur-Oger GC BdB |
| `pierre_gimmonet` | Pierre Gimmonet | 1 | $75 | Grands Terroirs Special Club |
| `marc_hebrart` | Marc Hebrart | 1 | $77 | Special Club Brut — iconic grower |
| `paul_drappier` | Paul Drappier | 1 | $58 | Brut Charles de Gaulle — Drappier negoce side |
| `etienne_calsac` | Etienne Calsac | 1 | $48 | Echappée Belle BdB Extra-Brut |
| `diot_benoit` | Diot Benoit / Diot-Legras Les | 4 | $75–$94 | Millésime VV GC / Mesnil VV — small grower |
| `sekthaus_raumland` | Sekthaus Raumland | 5 | $35–$87 | German méthode traditionnelle icon (Triumvirat, BdN Reserve) |

### Mosel / Nahe / Pfalz / Rheinhessen / Baden (German Riesling + Pinot)

Evan's deep stylistic home — heavy bias toward onboarding.

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `markus_molitor` | Markus Molitor / Markus Moitor (typo) | 36 | $26–$116 | Mosel Auslese vertical (Zeltinger Sonnenuhr, Wehlener, Brauneberger Juffer, Zeltinger Schlossberg) — iconic |
| `martin_muellen` | Martin Muellen / Martin Mullen / Martin Müllen | 26 | $25–$90 | Mosel Trarbacher Hühnerberg / Kröver Paradies trocken — terroir grower |
| `jj_prum` | JJ Prum | 2 | $49–$63 | Iconic Wehlener Sonnenuhr / Graacher Himmelreich — bedrock Mosel |
| `selbach_oster` | Selbach-Oster | 4 | $37–$39 | Mosel grower (Zeltinger Sonnenuhr GG, Anrecht) |
| `spater_veit` | Spater Veit / Spater-Veit / Später-Veit | 11 | $25–$75 | Piesporter Goldtröpfchen Pinot Noir + Auslese — small Mosel |
| `wilhelm_weber_osterman` | Wilhelm Weber-Osterman | 6 | $28–$42 | Mosel Brauneberger Juffer Auslese 1989/1993 (aged stock!) |
| `jakob_schneider` | Jakob Schneider | 1 | $36 | Niederhauser Hermannshöhle trocken |
| `gut_hermannsberg` | Gut Hermannsberg | 8 | $27–$109 | Nahe GG icon (Kupfergrube, Felsenberg, Bastei) — high priority |
| `k_h_schneider` | K.H. Schneider | 10 | $22–$40 | Nahe Felsenberg / Königsfels GG — value tier |
| `donnhoff` | already matched | | | (matched in this rebuild) |
| `dr_wehrheim` | Dr Wehrheim / Dr. Wehrheim / Dr. Wehreim | 13 | $37–$72 | Pfalz Kastanienbusch GG / Mandelberg — biodynamic-leaning |
| `dr_burklin_wolf` | Dr Burklin Wolf | 1 | $200 | Pfalz Pechstein Riesling GC — biodynamic icon |
| `a_christmann` | A. Christmann | 1 | $90 | Pfalz Idig Riesling GG — biodynamic icon |
| `okonomeriat_rebholz` | Okonomeriat Rebholz | 1 | $85 | Pfalz Kastanienbusch GG — biodynamic icon |
| `sven_klundt` | Sven Klundt | 5 | $30–$37 | Pfalz Kastanienbusch (neighbor to Rebholz/Wehrheim) |
| `kuhling_gillot` | Kuhling-Gillot | 1 | $50 | Rheinhessen Ölberg GG — biodynamic, top tier |
| `thorle` | Thorle / Thörle / Thorle Holle / Thorle Probstey / Thorle Saulheimer / Thorle Schlossberg / Thorle Blanc / Thörle Blanc de Blancs (+ all variants) | 32 | $23–$97 | Rheinhessen Saulheim — GG Riesling + Spätburgunder + Sekt; Will Goldschmitt importer (cellar style) |
| `juwel` | Juwel | 4 | $29–$33 | Rheinhessen Alsheim — under-radar |
| `wegeler` | Wegeler | 1 | $85 | Bernkasteler Doctor GG — historic estate |
| `schloss_johannisberg` | Schloss Johannisberg | 2 | $48–$78 | Rheingau historic icon (Rosalack/Grünlack) |
| `prinz_jungfer` | Prinz Jungfer | 1 | $54 | Rheingau Hallgartener Jungfer GG — Prinz family |
| `prinz_schonhell` | Prinz Schönhell | 1 | $48 | Rheingau Schönhell GG — same family |
| `andreas_laible` | Andreas Laible / Laible / Laible Am | 6 | $25–$49 | Baden Durbacher / Buhl Riesling GG / Muskateller — grower |
| `ziereisen` | Ziereisen / Hanspeter Ziereisen | 16 | $30–$182 | Baden icon (Jaspis Spätburgunder, Gutedel, Würmlin Grauburgunder) — Wasenhaus-adjacent |

### Piedmont / Lombardy / Italian North

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `cesare_bussolo` | Cesare Bussolo | 19 | $26–$200 | La Morra Barolo (La Serra, Fossati) grower |
| `vietti` | Vietti | 2 | $297 | Iconic Barolo Cerequio — collector tier |
| `arpepe` | Ar.Pe.Pe / Arpepe / ArPePe Stella | 10 | $39–$104 | Iconic Valtellina Sassella Rocce Rosse / Stella Retica — terroir Nebbiolo |
| `motalli_renato` | Motalli Renato | 11 | $30–$50 | Valtellina (Le Urscele, Valgella, Chiavennasca Rosato) — small grower |
| `cantina_menegola` | Cantina Menegola | 2 | $63 | Valtellina Sassella Riserva Speciale |
| `pier_paolo_grasso` | Pier Paolo Grasso | 3 | $83–$85 | Barbaresco Piccola Emma 1998 — aged Nebbiolo |
| `rocche_dei_barbari` | Rocche dei Barbari / Rocche Di Barbari / Rochhe de Barbari | 9 | $40–$90 | Barbaresco Alivio Riserva + Primanebbia Langhe |
| `quazzolo` | Quazzolo | 4 | $38–$46 | Barbaresco / Ovello |
| `vini_chiussima` | Vini Chiussima | 5 | $25–$60 | Carema (Northern Piedmont Nebbiolo) — under-radar |
| `tenuta_monolo_gilodi` | Tenuta Monolo Gilodi | 5 | $25 | Bramaterra Riserva 1989/1990/2003 — aged Alto Piemonte |
| `podere_ai_valloni` | Podere Ai (Valloni Boca/Sass Russ) / Podere ai Valloni | 3 | $32–$62 | Boca (Northern Piedmont Nebbiolo) — Vallana-adjacent |
| `sergio_barbaglia` | Sergio Barbaglia | 6 | $23–$48 | Boca / Colline Novaresi Croatina — Northern Piedmont |
| `vigneti_valle_roncati` | Vigneti Valle / Vigneti Valle Roncati | 6 | $30–$46 | Ghemme / Sizzano / Fara Riserva — Northern Piedmont DOCG cluster |
| `cascina_quarino` | Cascina Quarino | 3 | $34–$50 | Albugnano Superiore (Asti Nebbiolo) |
| `palazzo_schiavino` | Palazzo Schiavino | 1 | $50 | Barolo Monvigliero |

### Jura

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `caves_jean_bourdy` | Caves Jean Bourdy / Caves Bourdy / Caves Jean | 6 | $80–$92 | Iconic Château-Chalon / Vin Jaune — historic Jura |
| `frederic_lambert` | Frederic Lambert | 2 | $87–$92 | Château-Chalon / Vin Jaune |

### Savoie

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `gilles_berlioz` | Gilles Berlioz | 2 | $63–$97 | Chignin-Bergeron biodynamic icon (Les Christine, Résilience) |
| `domaine_des_rutissons` | Domaine des Rutissons | 5 | $27–$30 | Savoie Etraire de la Huy / Verdesse IGP / M. Leblanc |

### Provence

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `chateau_simone` | Chateau Simone | 2 | $82 | Palette Rouge + Blanc — iconic Provence Palette monopole |

### Bordeaux (selective — WK undercovered / aged-classic only)

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `bel_air_marquis_daligre` | Bel Air / Bel Air Marquis dAligre | 10 | $70–$88 | Margaux Cru Bourgeois Supérieur, aged-stock (1996/2009/2010/2013/2015) — long élevage = Evan-style aged classic |

### Switzerland (Graubünden Pinot Noir cluster)

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `weingut_hansruedi_adank` | Weingut Familie Hansruedi Adank (+ standalone `Adank`) | 14 | $38–$155 | Spondis Pinot Noir, Chardonnay Am Berg — Graubünden Pinot leader |
| `mohr_niggli` | Mohr-Niggli | 8 | $38–$74 | Graubünden Pinot Noir (Graf, Pilgrim, Maienfeld) |
| `patrick_adank` | Patrick Adank | 4 | $65–$192 | Chardonnay Am Berg, Pinot Noir Herrenacker — top Graubünden |
| `sprecher_von_bernegg` | Sprecher Von Bernegg / Spreccher Von Bernegg / Sprecher von | 5 | $46–$64 | Graubünden Pinot Noir (Lindenwingert, Pfaffen/Calander) + Completer |

### USA

| Slug | Retailer spelling(s) | Cuvées | Price | Why onboard |
|---|---|---:|---|---|
| `martin_woods` | Martin Woods | 5 | $55–$66 | Willamette Pinot Noir (Hyland Vineyard, Jessie James) — US boutique |

---

## Tier 2 — Worth watching (research before page)

| Slug | Retailer spelling(s) | Cuvées | Price | Why pending |
|---|---|---:|---|---|
| `richard_ostreicher` | Richard Ostreicher / Richard Oestreicher / Richard Östreicher | 23 | $37–$177 | Franken Pinot Noir + Cab/Merlot — Franken is off Evan's main map; check farming/style |
| `josef_walter` | Josef Walter / Joseph Walter / Weingut Josef Walter | 9 | $45–$107 | Franken Spätburgunder Pinot 274 — needs style check |
| `weingut_weltner` / `paul_weltner` | Weingut Weltner + Paul Weltner | 19 | $25–$64 | Franken Rödelsee Riesling/Sylvaner/Scheurebe — same producer, decide if Franken passes |
| `jurgen_von_der_mark` | Jurgen Von der Mark / Jurgen von der Mark / Jürgen von der Mark | 14 | $25–$67 | Baden Pinot Noir grower (Engerstein, Krieger des Lichts) |
| `weingut_achim_durr` / `achim_durr` / `achim_duerr` | (all variants) | 14 | $36–$54 | Baden — Pinot Noir, Cab Franc, Blaufränkisch, Syrah; broad cuvée range |
| `max_geitlinger` | Max Geitlinger / Max Geitlinger Wein | 2 | $29–$38 | Baden Merlot (off-style) |
| `weingut_riehen` | Weingut Riehen | 7 | $39–$94 | Swiss Basel-Land — Cidre + Pinot Noir + Chardonnay; small |
| `pircher` | Pircher | 7 | $36–$200 | Alto Adige Pinot Noir Stadtberg / Gewürztraminer; sourcing unclear (rows split between Switzerland and Italy in raw) |
| `le_petit_chateau` | Le Petit Chateau | 2 | $35–$37 | Swiss Vully Pinot Noir Selection |
| `wegelin` | Wegelin Weine AG / Wegelin Weisstorkel / Weggelin | 3 | $52–$56 | Swiss Eastern (Blauburgunder, Weisstorkel) — small producer |
| `daniel_monika_marugg` | Daniel And Monika Marugg | 2 | $41–$44 | Swiss Graubünden Chardonnay / Merlot-Malbec |
| `sven_enderle` / `enderle_moll` | already matched | | | n/a |
| `cianfagna` | Cianfagna / Cian Fagna | 4 | $39–$67 | Molise Aglianico / Sator Gran Maestro — under-radar Italian South |
| `vini_marino_proclamo_cilento` | Vini Marino / Vini Marino Proclamo Cilento | 6 | $31–$81 | Campania Cilento Aglianico Riserva / Fiano Tardiva |
| `calafe` | Calafe / CaLaFe Ariavecchia | 3 | $35–$37 | Campania Greco di Tufo / Taurasi |
| `vinding_montecarrubo` | Vinding Montecarrubo | 5 | $45–$50 | Sicily (Quattro Venti, Cuvée Suzanne) — small producer |
| `luna_beberide` | Luna Beberide | 1 | $46 | Bierzo Spain (Paixar A Serra) — only Spanish entry |
| `cecllia_monte` | Cecllia Monte (likely Cecilia Monte typo) | 3 | $50–$51 | Barbaresco Serracapelli 2013 |
| `tomaso_gianolo` | Tomaso Gianolo | 4 | $31–$33 | Barolo / Barbaresco — value tier |
| `rattalino` | Rattalino | 4 | $41–$58 | Barolo / Barbaresco Riserva Sel.34/35/45 |
| `tenuta_col_falco` | Tenuta Col Falco / Tenuta col Falco | 5 | $20–$32 | Montefalco Rosso / Sagrantino — Umbria value |

---

## Tier 3 — Skip

### Generic mid-tier Bordeaux

| Producer | Cuvées | Reason |
|---|---:|---|
| Chateau Bouillerot | 1 | Entre-deux-Mers $23 generic |
| Chateau Samion | 2 | $38 generic Bordeaux |
| Château Bonneau | 1 | Montagne-Saint-Émilion $37 generic |
| Vieux Chateau St. Andree | 6 | Sub-$35 generic Bordeaux — fails the "WK-undercovered" hook |

### Broken / split / single-cuvée orphans (data, not producers)

| Slug | Cuvées | Reason |
|---|---:|---|
| `domaine_des` | 8 | "Domaine des" with the second word landing in the wine column — split-row artifact. Real producers behind it: `domaine_des_remizieres`, `domaine_des_pierres_seches`, `domaine_des_miquettes`. **Fold remizières into a new entry; remap Miquettes (Saint-Joseph Madloba) into `domaine_des_pierres_seches`'s vintner if mistakenly aggregated, else its own page.** |
| `domaine_du` | 3 | Same split-row issue — folds into `domaine_du_tunnel` |
| `chateau_de` | 1 | Trinquevedel Tavel — folds into `chateau_de_trinquevedel` |
| `caves_jean` | 1 | "Caves Jean Bourdy" split — folds into `caves_jean_bourdy` |
| `cantina_del` | 2 | Cantina Del Signore — folds into `cantina_del_signore` (new entry; Gattinara/Piedmont) |
| `cascina_delsignore` | 2 | Same producer as Cantina Del Signore variant |
| `vigneti_valle` | 2 | Folds into `vigneti_valle_roncati` (Tier 1) |
| `podere_ai` | 2 | Folds into `podere_ai_valloni` (Tier 1) |
| `domaine_philippe` | 1 | Folds into `philippe_naddef` (Tier 1) |
| `sprecher_von` | 1 | Folds into `sprecher_von_bernegg` (Tier 1) |
| `laible_am` | 1 | Folds into `andreas_laible` (Tier 1) |

### Minor / single-bottle obscure with no Evan hook

| Slug | Cuvées | Reason |
|---|---:|---|
| Bellaria (Brunello generic) | 1 | $39 sub-tier Brunello |
| Petra (Toscana IGT) | 2 | $35 generic super-Tuscan |
| Raphael Chopin | 1 | Régnié Beaujolais Villages — $35 minor |
| Giuseppe Negro | 1 | Langhe Rosato $25 — minor |
| Vigneti Costacurta | 1 | Colline Novarese Croatina $21 — minor |
| Domaine Grosbot-Barbara | 1 | Saint-Pourçain $42 — niche AOC, single bottle |
| Domaine Michellas St Jemmes | 1 | Cornas Terres dArces $75 — single bottle, unknown style |
| Domaine St. Gayan | 1 | Gigondas In Nominae Patris $50 — known but single entry |
| Maison Stephan | 1 | VDF Grand Blanc $40 — split data, may fold elsewhere |
| Remy Nodin | 1 | Cornas Les Eygats $39 — single bottle |
| J. Despesse | 1 | Cornas $62 single bottle |
| Henri Gallet | 1 | Côte-Rôtie $61 single bottle (likely related to Domaine Gallet — fold) |
| Domaine Gallet | 2 | Côte-Rôtie + VDF Cuvée Gallet Jade — small producer, could move to Tier 2 |
| Markus Moitor (typo) | 1 | Folds into `markus_molitor` |
| Famille / Famlie / Familie Jouffreau | 12 across variants | Cahors Clos de Gamot — borderline; Cahors is off Evan's main map but the Clos de Gamot bottle (1986, Vignes Centenaires) is the kind of aged single-vineyard that fits. **Move to Tier 1 if accepting Southwest France** |
| Louis Sozet | 4 | Cornas $98–$102 — could be Tier 2 |
| Maison Stephan | 1 | Likely an alias of `jean_michel_stephan` (Côte-Rôtie); fold |
| La Psigula | 2 | Bramaterra (Northern Piedmont) — could be Tier 1 next to Tenuta Monolo Gilodi |
| La Chablisienne | 1 | Chablis 1er Cru Mont de Milieu $40 — co-op (mid-tier) |
| JJ Morel | 1 | Bourgogne Blanc $30 — generic |
| Michelle Luyton | 2 | Hermitage Rouge $66 — small producer (vs Luyton 2 cuvées same) |
| Luyton | 2 | Hermitage Rouge $63 — same as Michelle Luyton |

---

## Alias-only fixes — add to `FASS_ALIASES` once pages exist

These are pure spelling/typo dupes that should consolidate into one slug:

```python
# (target slugs are NEW pages — create the page first, then enable alias)
FASS_ALIASES = {
    # Markus Molitor
    "markus moitor": "markus_molitor",
    # Martin Müllen (Mosel)
    "martin muellen": "martin_muellen",
    "martin mullen": "martin_muellen",
    "martin müllen": "martin_muellen",
    # Pierre Brisset (Burgundy negociant)
    "maison brisset": "pierre_brisset",
    "pierre briseet": "pierre_brisset",
    # JJ Girard
    "j.j. girard": "jj_girard",
    # Mickael Bourg (Cornas)
    "mikael bourg": "mickael_bourg",
    # Compagnie de l'Hermitage (Lyle Fass project)
    "compagnie l'hermitage": "compagnie_de_lhermitage",
    "compagnie l’hermitage": "compagnie_de_lhermitage",
    "lyle fass charalambos lelektsoglou": "compagnie_de_lhermitage",
    "lyle fass/charalambos": "compagnie_de_lhermitage",
    "georges lelektsoglou": "compagnie_de_lhermitage",
    "hector adrien charalambos lelektsoglou": "compagnie_de_lhermitage",
    # Gerard Courbis
    "gerard courbis et fils": "gerard_courbis",
    "gerard courbis pere & fils": "gerard_courbis",
    # Richard Östreicher
    "richard oestreicher": "richard_ostreicher",
    "richard östreicher": "richard_ostreicher",
    # Philippe Naddef family
    "phillippe naddef": "philippe_naddef",
    "philippe nadeff": "philippe_naddef",
    "michel naddef": "philippe_naddef",
    "domaine philippe": "philippe_naddef",
    "domaine philippe naddef": "philippe_naddef",
    # Achim Dürr
    "achim duerr": "achim_durr",
    "achim-durr": "achim_durr",
    "weingut achim durr": "achim_durr",
    # Domaine du Tunnel
    "domaine du": "domaine_du_tunnel",
    # Domaine des Pierres Sèches
    "domaine des": "domaine_des_pierres_seches",  # ambiguous — see Tier 3
    # Caves Jean Bourdy
    "caves bourdy": "caves_jean_bourdy",
    "caves jean": "caves_jean_bourdy",
    # Garaudet (Monthelie grower)
    "garaudet pere & fils": "garaudet",
    "sarl garaudet": "garaudet",
    "sarl garaudet pere & fils": "garaudet",
    "sarl garaudet pere et fils": "garaudet",
    # Daniel-Etienne Defaix
    "domaine daniel-etienne defaix": "daniel_etienne_defaix",
    # Jean Dauvissat
    "jean dauvissat pere & fils": "jean_dauvissat",
    "jean dauvissat père & fils": "jean_dauvissat",
    "jean dauvissat pere &amp; fils": "jean_dauvissat",
    # Sébastien Dampt
    "sébastien dampt": "sebastien_dampt",
    # Andreas Laible
    "laible": "andreas_laible",
    "laible am": "andreas_laible",
    # Dr Wehrheim
    "dr. wehrheim": "dr_wehrheim",
    "dr. wehreim": "dr_wehrheim",
    # Hanspeter Ziereisen / Ziereisen
    "hanspeter ziereisen": "ziereisen",
    # ARPEPE
    "ar.pe.pe": "arpepe",
    "arpepe stella": "arpepe",
    # Cantina Del Signore
    "cantina del": "cantina_del_signore",
    "cascina delsignore": "cantina_del_signore",  # if it's the same place
    # Vigneti Valle Roncati
    "vigneti valle": "vigneti_valle_roncati",
    # Podere ai Valloni
    "podere ai": "podere_ai_valloni",
    # Sprecher Von Bernegg
    "spreccher von bernegg": "sprecher_von_bernegg",
    "sprecher von": "sprecher_von_bernegg",
    # Trinquevedel
    "château de": "chateau_de_trinquevedel",
    # Bel Air
    "bel air": "bel_air_marquis_daligre",
    "bel air marquis daligre": "bel_air_marquis_daligre",
    # Patrick Adank / Hansruedi Adank
    "adank": "weingut_hansruedi_adank",
    # Cianfagna
    "cian fagna": "cianfagna",
    # Rocche dei Barbari
    "rocche di barbari": "rocche_dei_barbari",
    "rochhe de barbari": "rocche_dei_barbari",
    # Caillez-Lemaire
    'caillez-lemaire "pur meunier" brut nature': "caillez_lemaire",
    # Yvon Métras
    "yvon métras": "yvon_metras",
    # Domaine de la Cote St Epine
    "domaine de cote epine": "domaine_de_cote_epine",
    "domaine de la cote st epine": "domaine_de_cote_epine",
    "domaine de la côte": "domaine_de_cote_epine",
    # Vini Marino Proclamo Cilento
    "vini marino proclamo cilento": "vini_marino",
    # Tenuta col Falco
    "tenuta col falco": "tenuta_col_falco",
    # Famille Jouffreau / Famlie Jouffreau / Familie Jouffreau Clos de Gamot
    "famlie jouffreau": "famille_jouffreau",
    "familie jouffreau clos de gamot": "famille_jouffreau",
    "familie jouffreau": "famille_jouffreau",
    # Cave Sebastien Blachon → Domaine Blachon
    "cave sebastien blachon": "domaine_blachon",
    # Cesare Bussolo — clean
    # Cuchet Beliando + variant
    "cuchet-beliando cornas": "cuchet_beliando",
    "cuchet-beliando": "cuchet_beliando",
    # Selbach-Oster — clean
    # Henri Gallet / Domaine Gallet
    "henri gallet": "domaine_gallet",
    # Maison Stephan → Jean Michel Stephan (verify)
    "maison stephan": "jean_michel_stephan",
    # Luyton variants
    "michelle luyton": "luyton",
    # K.H. Schneider clean
    # JJ Prum — clean
}
```

---

## Recommended onboarding sequence

1. **Top 10 by cellar fit + cuvée depth** — create these wiki pages first:
   `markus_molitor`, `chateau_thivin`, `domaine_des_roches_neuves`,
   `arpepe`, `gut_hermannsberg`, `dr_burklin_wolf`, `ziereisen`,
   `vietti`, `chateau_simone`, `bel_air_marquis_daligre`.
2. **Rhône Cornas/Côte-Rôtie cluster** (12-15 pages): `julien_barge`,
   `compagnie_de_lhermitage`, `cuchet_beliando`, `guillaume_gilles`,
   `domaine_du_tunnel`, `domaine_des_pierres_seches`, `gerard_courbis`,
   `ludovic_courbis`, `jacques_lemenicier`, `mickael_bourg`,
   `emmanuel_verset`, `emmanuel_darnaud`, `nicolas_champagneaux`,
   `jean_michel_stephan`.
3. **Burgundy growers** (~12): `pierre_brisset`, `jj_girard`,
   `chavy_chouet`, `julien_cruchandeau`, `laurent_boussey`,
   `domaine_berlancourt`, `remi_poisot`, `vincent_ledy`,
   `philippe_naddef`, `daniel_etienne_defaix`, `jean_dauvissat`,
   `sebastien_dampt`.
4. **German + Champagne grower cluster** (~15): Mosel/Nahe/Pfalz/
   Rheinhessen + Champagne grower bottlings per Tier 1 table.
5. **Defer Tier 2** until a producer has either a Vinous / WK / CSW
   article in `raw/clippings/` to anchor the page.

After each batch: re-run `scripts/ingest_fass.py` → `scripts/build_rollups.py`
→ `scripts/build_wiki_index.py` → append to `wiki/log.md`.

---

## Decisions (Evan, 2026-05-26)

- **Bel Air-Marquis d'Aligre** → **aged classic — onboard**. Long-élevage
  Cru Bourgeois counts as an exception to the "no generic mid-tier
  Bordeaux" rule. CLAUDE.md updated.
- **Cahors / Famille Jouffreau** → **Southwest France accepted**. Add
  `famille_jouffreau` (consolidating Famille / Famlie / Familie Jouffreau
  Clos de Gamot variants, 12 entries, 1986 vertical) to Tier 1.
  CLAUDE.md updated.
- **Franken** → **region opened**. Add `richard_ostreicher`,
  `josef_walter`, `paul_weltner` (consolidating with `weingut_weltner`)
  to Tier 1. CLAUDE.md updated.

Net effect: Tier 1 grows from ~50 to ~54 producers.
