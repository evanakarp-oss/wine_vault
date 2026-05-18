import { useState, useMemo } from "react";

const producers = [
  // ── RADICAL NATURAL ──────────────────────────────────────────────
  {
    name: "Finca Suarez",
    winemaker: "Juanfa Suárez",
    region: "Paraje Altamira",
    province: "Mendoza",
    category: "Radical Natural",
    grapes: ["Semillon", "Malbec", "Criolla"],
    approach: "Clay tinajas, zero sulfites, native yeasts, unfiltered. Considered one of the pioneers of natural wine in Argentina. Extreme authenticity, vibrant acidity, and an artistic sensibility felt in every bottle.",
    keyWines: ["El Gavilán", "El Risueño"],
    source: "bistrosoft.com / Natural Vin",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Stella Crinita",
    winemaker: "Joanna Foster & Ernesto Catena",
    region: "Vista Flores, Tunuyán",
    province: "Mendoza",
    category: "Radical Natural",
    grapes: ["Barbera", "Petit Verdot", "Malbec"],
    approach: "Demeter-certified biodynamic since 2002. 100% spontaneous fermentation, zero SO2 at any stage, unfined and unfiltered. First non-European producers admitted to VinNatur. Production extremely small.",
    keyWines: ["Barbera", "Pet Nat Blanc"],
    source: "VellaTerra / Skurnik / Brazos Wine / Argentina Reloaded",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "El Bayeh",
    winemaker: "Daniel Manzur + Matías Michelini",
    region: "Quebrada de Humahuaca",
    province: "Jujuy",
    category: "Radical Natural",
    grapes: ["Criolla Chica", "Criolla Grande", "Moscatel Rosado"],
    approach: "Rescuing and reviving criolla varieties from century-old pergola-trained vines irrigated by traditional acequias. Whole cluster, native yeasts, low alcohol, zero sulfites. Named best discovery of 2024 by multiple Argentine sommeliers. #40 James Suckling Top 100 Argentina 2025.",
    keyWines: ["Viñas Elegidas Don Pilar", "Pequeños Parceleros de la Quebrada Maimará", "Pequeños Parceleros Tilcara"],
    source: "iprofesional.com / James Suckling 2025",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Viña Urbana",
    winemaker: "Viña Urbana team",
    region: "Mendoza",
    province: "Mendoza",
    category: "Radical Natural",
    grapes: ["Criolla", "Moscatel"],
    approach: "100% whole cluster, native yeasts, zero added sulfites, aged in clay amphorae, unfiltered. Minimum intervention in the cellar.",
    keyWines: ["Amiguito Criolla", "Amiguito Moscatel"],
    source: "viniaurbana.com.ar",
    reloaded: []
  },
  {
    name: "Cara Sucia",
    winemaker: "Héctor & Pablo Durigutti",
    region: "Santa María de Oro, Rivadavia",
    province: "Mendoza",
    category: "Radical Natural",
    grapes: ["Palomino", "Pedro Ximénez", "Ugni Blanc", "Cereza", "Sangiovese", "Bonarda", "Barbera"],
    approach: "A return to the Durigutti brothers' family origins in Rivadavia, Eastern Mendoza — a region overlooked by the premium wine boom but home to extraordinary pergola-trained vines from 1940. All organic, hand harvested, whole grape fermentation with native yeasts in unepoxy concrete eggs, co-fermented from the same vineyard, bottled unfined and unfiltered. Only ~300 cases per wine. Dedicated to reclaiming heritage varieties (Cereza, Criolla, obscure Italian varieties) that predated Argentina's Malbec marketing boom.",
    keyWines: ["Blanco Legítimo", "Sangiovese", "Cereza", "Cepas Tradicionales"],
    source: "theartisancollection.us / naturalwine.com / linerandelsen.com",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Michellini i Muffato",
    winemaker: "Gerardo Michellini & Andrea Muffato",
    region: "El Peral, Tupungato",
    province: "Mendoza",
    category: "Radical Natural",
    grapes: ["Semillon", "Chenin Blanc", "Chardonnay"],
    approach: "Pre-phylloxera vines from 1891. Natural winemaking in clay vessels, no additions, selection of historic parcels. Certezas Semillon won Best White at Argentina Reloaded London 2022.",
    keyWines: ["Certezas Semillon"],
    source: "Wine Anorak / Argentina Reloaded London 2022",
    reloaded: []
  },

  // ── LOW INTERVENTION ─────────────────────────────────────────────
  {
    name: "Matías Michelini (projects)",
    winemaker: "Matías Michelini",
    region: "Gualtallary / San Pablo",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Sauvignon Blanc", "Malbec", "Chardonnay", "Grenache"],
    approach: "Pioneer of the Argentine new wave. Native yeasts, concrete eggs, low alcohol, minimalist approach. International reference point for Gualtallary. #10 James Suckling Top 100 Argentina 2025 for Agua de Roca Sauvignon Blanc.",
    keyWines: ["Agua de Roca Sauvignon Blanc San Pablo", "Caos Chardonnay", "GarnaCHE"],
    source: "James Suckling Top 100 Argentina 2025 / Wine Enthusiast",
    reloaded: []
  },
  {
    name: "SuperUco",
    winemaker: "Michelini Brothers (JP, Matías, Gerardo, Gabriel)",
    region: "Gualtallary / Los Chacayes / Paraje Altamira",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec", "Cab Franc", "Pinot Noir"],
    approach: "100% biodynamic project co-founded in 2010. Focus on generous yet fresh Malbec from premium Uco Valley parcels. Certified biodynamic.",
    keyWines: ["SuperUco Malbec", "Los Chacayes"],
    source: "Wine Enthusiast / vinofino.club",
    reloaded: []
  },
  {
    name: "Ver Sacrum",
    winemaker: "Eduardo Soler",
    region: "Mendoza",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Grenache", "Mourvèdre", "Nebbiolo", "Criolla", "Cinsault"],
    approach: "Pioneer of Rhône varieties in Argentina since 2010. Amphora and whole cluster. Recovery of undervalued varieties with a natural approach. Paz Levinson: 'adds another dimension.'",
    keyWines: ["Grenache", "Mourvèdre", "Cinsault"],
    source: "Wine Anorak / Argentina Reloaded",
    reloaded: []
  },
  {
    name: "Mundo Revès",
    winemaker: "Quentin & Thibault Lepoutre",
    region: "Gualtallary / Los Chacayes",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Semillon", "Sauvignon Blanc", "Tokaji"],
    approach: "French brothers making skin-contact white blends with a natural and experimental approach. Featured at Argentina Reloaded London 2022.",
    keyWines: ["Skin-contact white blends"],
    source: "Argentina Reloaded / Wine Anorak",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "El Enemigo (Bodega Aleanna)",
    winemaker: "Alejandro Vigil & Adrianna Catena",
    region: "Maipú / Gualtallary / Rivadavia",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Cabernet Franc", "Malbec", "Semillon", "Bonarda"],
    approach: "Founded 2009 by Alejandro Vigil (Chief Winemaker at Catena Zapata, former INTA soil division head) and Adrianna Catena (historian, Oxford DPhil). Wild yeasts throughout. Concrete eggs and 100-year-old Alsatian oak foudres re-toasted in Italy. Single-vineyard focus across diverse terroirs: Gualtallary Cab Franc at 1,470m, Rivadavia Bonarda on clay, Semillon from Eastern Mendoza. Received first 100 pts (Robert Parker) for a South American wine. Cult project, boutique scale, restaurant and orchard at Casa Vigil. 98 pts Tim Atkin (Gran Enemigo Cab Franc 2022); 96 pts (Semillón 2024 & Bonarda 2023). As Bravas: Vigil's 1.4ha Grenache from Lunlunta on clay/gravel soils, planted with Gredos clones he brought from Spain himself — 18–24 months in foudre, low alcohol, floral and precise.",
    keyWines: ["Gran Enemigo Cab Franc (single vineyards)", "El Enemigo Semillón", "El Enemigo Bonarda", "El Enemigo Malbec", "As Bravas Grenache"],
    source: "enemigowines.com / worldsbestvineyards.com / Wine Advocate",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Pielihueso",
    winemaker: "Celina & Alejandro Bartolome (father/daughter)",
    region: "Los Chacayes / Los Sauces, Tunuyán",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Torrontés", "Sauvignon Blanc", "Chardonnay", "Malbec"],
    approach: "Founded 2017. The name means 'skin and bones' in Spanish. Practicing organic. Orange wine specialist: Naranjo is a 3–4 week skin-contact blend of Torrontés, Sauvignon Blanc, and Chardonnay, spontaneously fermented with native yeasts in concrete and stainless steel, unfined, unfiltered. Fermented in amphora and used barrique.",
    keyWines: ["Naranjo (orange wine)", "Primero Blanco", "Primero Rosado", "Los Sauces Tinto"],
    source: "bitterpops.com / highlandparkwine.com / dewinespot.co",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Las Compuertas Project (Durigutti)",
    winemaker: "Héctor & Pablo Durigutti",
    region: "Las Compuertas, Luján de Cuyo",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec", "Criolla Chica", "Bonarda/Charbono"],
    approach: "Started 2007 when the Durigutti brothers acquired 5 historic Malbec hectares on Callejón de la Reta. Now 34 ha named Finca Victoria after their mother. Organically farmed. 1943 Criolla Chica pergola vines at 1,050m on alluvial terraces of the Mendoza River. Whole grape, cold maceration in concrete eggs (no epoxy), native yeasts throughout. Criolla fermented half as red / half as white — skins removed mid-process. Recovery of one of Mendoza's most historic viticultural zones. 92 Tim Atkin (Criolla Parral); 95 Tim Atkin / 93 WE (Inframundo).",
    keyWines: ["Criolla Parral", "Tinto del Pueblo", "Inframundo Natural Blend", "Malbec 5 Suelos"],
    source: "durigutti.com / theartisancollection.us / wine-searcher.com",
    reloaded: []
  },
  {
    name: "Pie de Monte (Durigutti)",
    winemaker: "Héctor & Pablo Durigutti",
    region: "Gualtallary / Los Arboles / Vistalba",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec"],
    approach: "Single-vineyard Malbec line sourced from small growers across Mendoza's pedemonte, all vineyards of centenary lineage in conversion to organic. No oak at any stage — 11 months entirely in 3,000L concrete eggs with native yeasts. Three terroirs: Finca Las Jarillas (Gualtallary, 1,360m, alluvial/calcareous), Finca Zarluenga (Los Arboles, Valle de Uco), Finca Ruano (Vistalba, 1,020m, clay/rocky). 97 Descorchados (Las Jarillas); 95 Descorchados (Zarluenga); 91 Vinous (Ruano).",
    keyWines: ["Malbec Finca Las Jarillas (Gualtallary)", "Malbec Finca Zarluenga (Los Arboles)", "Malbec Finca Ruano (Vistalba)"],
    source: "durigutti.com / wine-searcher.com",
    reloaded: []
  },
  {
    name: "Carmelo Patti",
    winemaker: "Carmelo Patti",
    region: "Perdriel, Luján de Cuyo",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec", "Cabernet Sauvignon", "Cabernet Franc"],
    approach: "One of Mendoza's most legendary cult producers — working alone with a single employee out of a garage-scale winery in Drummond since 1986. Organic grapes from Perdriel, native yeasts only, zero chemical additives, no consultants, no manipulation. Defines his style as 'a naked wine, without anything that can cover it up.' Holds all wines a minimum of 4–5 years before release, with at least 3 years in bottle. Fermentation in concrete, aged in older oak. ~20,000 litres/year total production. Devotee following in Argentina and internationally. Cult status earned entirely through word of mouth.",
    keyWines: ["Malbec", "Cabernet Sauvignon", "Gran Assemblage", "Cabernet Franc"],
    source: "naturalwine.com / elixirwinegroup.com / bowlerwine.com / pampaswines.com",
    reloaded: []
  },
  {
    name: "Matías Riccitelli",
    winemaker: "Matías Riccitelli",
    region: "Patagonia / Río Negro",
    province: "Patagonia",
    category: "Low Intervention",
    grapes: ["Pinot Noir", "Trousseau/Bastardo", "Malbec"],
    approach: "Old vines, organic, low alcohol. 'Old Vines From Patagonia' line uses whole cluster fermentation and minimal/no sulfites. Elegant and accessible style. Paz Levinson: 'one of the most significant winemakers in Argentina today.'",
    keyWines: ["Old Vines From Patagonia", "Riccitelli Trousseau"],
    source: "bistrosoft.com / Paz Levinson",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Desquiciado",
    winemaker: "Gonzalo Tamagnini & Martín Sesto",
    region: "Cordón del Plata, Tupungato",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Grenache"],
    approach: "Pioneers of Grenache in Argentina since 2017. Vineyard in Gualtallary, natural and expressive production. Named wine of the year 2024 by multiple Argentine sommeliers.",
    keyWines: ["The Wild Side Grenache"],
    source: "iprofesional.com / Mejores vinos 2024",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Cara Sur",
    winemaker: "Rodrigo Serrano Alou",
    region: "Valle de Calingasta",
    province: "San Juan",
    category: "Low Intervention",
    grapes: ["Criolla Chica", "Chardonnay", "Malbec"],
    approach: "Rodrigo Serrano Alou's project from the remote Calingasta Valley in San Juan — one of Argentina's most compelling new terroir discoveries. 100% whole cluster, concrete aging. The Criolla Chica Paraje Hilario is an ethereal, medium-bodied red with pale color and electric freshness, ranked #9 James Suckling Top 100 Argentina 2025. Calingasta's high-altitude desert climate and granitic soils produce wines of remarkable purity.",
    keyWines: ["Cara Sur Criolla Chica Paraje Hilario", "Cara Sur Chardonnay"],
    source: "James Suckling Top 100 Argentina 2025 / Argentina Reloaded Buenos Aires 2025",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Escala Humana",
    winemaker: "Germán Masera",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Chardonnay", "Semillon", "Malbec"],
    approach: "Focused, expressive whites that balance volume and freshness with restraint. Independent winemaker recognized as part of the Argentine new wave. #7 James Suckling Top 100 Argentina 2025.",
    keyWines: ["Buscado Vivo o Muerto Chardonnay El Cerro Gualtallary"],
    source: "James Suckling 2025",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Altar Uco",
    winemaker: "JP Michelini & Daniel Kokogian",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec", "Cab Franc", "Pinot Noir"],
    approach: "Total winemaking freedom. Unique, one-of-a-kind wines with a distinct identity. Artistic labels and distinctive names. Started 2014.",
    keyWines: ["Altar Uco Malbec", "Altar Uco Pinot Noir"],
    source: "Wine Enthusiast",
    reloaded: ["Buenos Aires 2025"]
  },

  // ── CERTIFIED ORGANIC + NATURAL LINE ─────────────────────────────
  {
    name: "Chakana",
    winemaker: "Juan Pablo Michelini (consultant)",
    region: "Agrelo / Paraje Altamira",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Cab Franc", "Bonarda"],
    approach: "Andean reciprocity philosophy. Agroecological practices, transition to organic/biodynamic since 2012. Vientre Malbec: zero sulfites, no acidity correction, zero additives. 'Zero makeup. A high-risk, super transparent wine that speaks of Paraje Altamira at its purest.'",
    keyWines: ["Vientre Malbec", "Ayni", "Estate Selection Altamira"],
    source: "chakanawines.com / todoagro.com.ar / vinetur.com",
    reloaded: []
  },
  {
    name: "Marchiori & Barraud",
    winemaker: "Andrea Marchiori & Luis Barraud",
    region: "Perdriel, Luján de Cuyo / Uco Valley",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Cabernet Sauvignon", "Chardonnay"],
    approach: "Andrea and Luis co-founded Viña Cobos with Paul Hobbs in 1999, studied at UC Davis together, and launched their personal project in 2016. Centered on Andrea's family-owned Marchiori Vineyard in Perdriel — 50+ year old vines on deep alluvial soils at 900m. Certified organic throughout. Hand harvested, native yeast fermentation in small tanks. Cuartel Dos from the most prized block: 12 months in used French oak. Gualtallary Corte a new high-altitude addition. 95 Tim Atkin (Malbec Cuartel Dos); 95 Tim Atkin (Cab Sauv Cuartel Dos); 90 Vinous (Malbec).",
    keyWines: ["Malbec", "Cabernet Sauvignon", "Chardonnay", "Malbec Cuartel Dos", "Cabernet Sauvignon Cuartel Dos", "Gualtallary Corte"],
    source: "marchioribarraud.com / theartisancollection.us / wineenthusiast.com",
    reloaded: ["Rio 2024"]
  },
  {
    name: "Familia Cecchin",
    winemaker: "Familia Cecchin",
    region: "Maipú",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Cabernet Sauvignon"],
    approach: "OIA certified. Pioneers in organic wines without sulfites since 1959. Native yeasts, no tartaric acid, no SO2. Historical reference point for the Mendoza organic movement.",
    keyWines: ["Malbec Reserva No Sulfites", "Cabernet Sauvignon Organic"],
    source: "bodegacecchin.com.ar",
    reloaded: []
  },
  {
    name: "Bodega Calle",
    winemaker: "Kirk Ermisch",
    region: "Luján de Cuyo / San Carlos / Tupungato",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Cabernet Franc", "Semillon", "Torrontés", "Chardonnay"],
    approach: "Small-lot, gravity-flow boutique winery built in a 1925 cellar in Drummond, Luján de Cuyo — at the historic crossroads of Luigi Bosca, Baldini, and Lagarde. Certified organic and biodynamically farmed, native yeasts, gravity delivery to tanks, vegan, GMO-free. Dharma Reserva Red: 60% Malbec / 40% Cabernet Franc from a single organic vineyard in San Carlos, 12 months in used French oak. 91 Wine Advocate (2017 vintage). Dharma Orange: skin-contact Semillon/Torrontés/Chardonnay from 50-year-old Tupungato vines, 12 months on fine lees in concrete eggs, SO2 ≤30ppm. 5th winery admitted to the Luján de Cuyo DOC.",
    keyWines: ["Dharma Reserva Red Blend", "Dharma Orange"],
    source: "bodegacalle.com / elixirwinegroup.com / Wine Advocate",
    reloaded: []
  },
  {
    name: "Alpamanta",
    winemaker: "Peter & Beate Töpfer",
    region: "Ugarteche, Luján de Cuyo",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Cab Franc", "Sauvignon Blanc"],
    approach: "Demeter-certified biodynamic. German family with a holistic philosophy. Among the earliest serious biodynamic estates in Mendoza.",
    keyWines: ["Alpamanta Natal", "Alpamanta Estate"],
    source: "vinofino.club",
    reloaded: []
  },
  {
    name: "Bodegas Krontiras / Doña Silvina",
    winemaker: "Constantinos & Silvina Krontiras",
    region: "Luján de Cuyo",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Viognier", "Cab Franc"],
    approach: "Organic and biodynamic since 2003. 80-year-old vines. Argentine-Greek project. Part of the NOW Argentina sustainable export group.",
    keyWines: ["Doña Silvina Malbec", "Krontiras Organic"],
    source: "now-argentina.com",
    reloaded: []
  },

  // ── BIODYNAMIC ───────────────────────────────────────────────────
  {
    name: "Bodega Noemía",
    winemaker: "Hans Vinding-Diers & Countess Noemi Marone Cinzano",
    region: "Mainqué, Río Negro Valley",
    province: "Patagonia",
    category: "Biodynamic",
    grapes: ["Malbec", "Merlot", "Petit Verdot"],
    approach: "Founded 2001 after discovering abandoned pre-phylloxera Malbec vines from 1932. Demeter biodynamic and Argencert organic certified throughout. Indigenous yeast fermentation in open French oak fermenters and concrete vessels. One of the most acclaimed estates in South America. Countess formerly owned Argiano (Tuscany); Vinding-Diers named Tim Atkin Winemaker of the Year 2018.",
    keyWines: ["Noemía (flagship)", "A Lisa", "J. Alberto"],
    source: "bodeganoemia.com / Voyageurs du Vin / Wine.com",
    reloaded: []
  },
  {
    name: "Tikal (Ernesto Catena)",
    winemaker: "Ernesto Catena & Alejandro Kuschnaroff",
    region: "Vista Flores, Tunuyán",
    province: "Mendoza",
    category: "Biodynamic",
    grapes: ["Malbec", "Syrah", "Bonarda", "Cabernet Sauvignon"],
    approach: "Demeter biodynamic estate in Vista Flores — first biodynamic winery in Uco Valley open to the public. Llamas, horses, donkeys, and bees integrated into the farming ecosystem. Shares the Vista Flores property with Stella Crinita (Joanna Foster, Ernesto's wife). Multiple certified lines: Demeter biodynamic 'Natural', organic 'Amorio' (Altamira), organic 'Jubilo' (Gualtallary). Founded by Ernesto Catena, 4th generation, son of Nicolás Catena.",
    keyWines: ["Natural (Malbec/Syrah)", "Amorio Malbec", "Jubilo Malbec/Cabernet", "Patriota (Bonarda/Malbec)"],
    source: "vineconnections.com / timeout.com / worldsbestvineyards.com",
    reloaded: []
  },
  {
    name: "Altos Las Hormigas",
    winemaker: "Federico Gambetta (Alberto Antonini & Antonio Morescalchi founders)",
    region: "Paraje Altamira / Luján de Cuyo / Gualtallary",
    province: "Mendoza",
    category: "Biodynamic",
    grapes: ["Malbec", "Bonarda", "Semillon"],
    approach: "Founded 1995 by Alberto Antonini (ex-Antinori) and Antonio Morescalchi. Jardín de Hormigas vineyard (32 ha, Paraje Altamira, 1,200m) is certified organic — 40% native flora for biodiversity corridors, designed with Pedro Parra into 22 separate soil-unit parcels. Biodynamic farming following Alan York's philosophy ('grapes are not the product of a plant but of an ecosystem'). Wild yeasts, no small oak, concrete fermentation. 100 points Tim Atkin for Jardín de Hormigas Los Amantes 2021 (first vintage). Meteora: 97 pts Tim Atkin 2025 / 95 pts Vinous / #19 WE Top 100 2024.",
    keyWines: ["Jardín de Hormigas Meteora", "Jardín de Hormigas Los Amantes", "Appellation Altamira", "Appellation Gualtallary"],
    source: "altoslashormigas.com / libertywines.co.uk / nimbilityasia.com",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Bodega Chacra",
    winemaker: "Piero Incisa della Rocchetta",
    region: "Mainqué, Alto Valle del Río Negro",
    province: "Patagonia",
    category: "Biodynamic",
    grapes: ["Pinot Noir", "Chardonnay"],
    approach: "Biodynamic certified from founding (2004). Grandson of the creator of Sassicaia. Ungrafted vines planted in 1932. Indigenous yeasts, unfiltered, natural decantation only. Chardonnay collaboration with Jean-Marc Roulot. The defining reference for Argentine Pinot Noir.",
    keyWines: ["Treinta y Dos", "Cincuenta y Cinco", "Barda", "Chardonnay (with Roulot)"],
    source: "bodegachacra.com / K&L Wines",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Zorzal Wines",
    winemaker: "Michelini Brothers (JP, Matías, Gerardo)",
    region: "Tupungato",
    province: "Mendoza",
    category: "Biodynamic",
    grapes: ["Malbec", "Pinot Noir", "Cab Franc", "Torrontés"],
    approach: "Founded 2008. Concrete eggs, no oak in terroir line, native yeasts, respectful enology. One of the most influential projects in the Uco Valley. Biodynamic practices throughout.",
    keyWines: ["Terroir Único", "Eggo Franco", "Lecciones de Vuelo"],
    source: "Grand Cru Brasil / Wine Enthusiast",
    reloaded: []
  },
  {
    name: "Comarca La Matilde",
    winemaker: "La Matilde team",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Biodynamic",
    grapes: ["Malbec", "Pinot Noir"],
    approach: "Certified organic with biodynamic practices. Small artisanal production.",
    keyWines: ["La Matilde Malbec"],
    source: "vinofino.club",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Finca Dinamia",
    winemaker: "Familia Dinamia",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Biodynamic",
    grapes: ["Malbec", "Cab Franc"],
    approach: "Certified organic with biodynamic practices. Small production in the Uco Valley. Featured at Argentine organic wine fairs.",
    keyWines: ["Dinamia Malbec"],
    source: "vinofino.club / La Nación",
    reloaded: []
  },

  // ── EMERGING ─────────────────────────────────────────────────────
  {
    name: "Aguijón de Abeja (Durigutti)",
    winemaker: "Héctor & Pablo Durigutti",
    region: "Multi-region: Patagonia / Salta / Catamarca / San Juan",
    province: "Patagonia",
    category: "Emerging",
    grapes: ["Malbec", "Cabernet Sauvignon", "Bonarda", "Cabernet Franc", "Chardonnay/Semillon"],
    approach: "Durigutti brothers' multi-regional organic and natural wine project ranging across Argentina's most distinctive terroirs — from Patagonia to Catamarca to San Juan. Certified organic and natural across the range. Showcases how Argentina's diverse climates and elevations express the same varieties in radically different ways.",
    keyWines: ["Malbec (Patagonia)", "Cabernet Sauvignon (Salta)", "Bonarda (San Juan)", "Malbec Reserva (Patagonia)"],
    source: "mercadobio.ar / worldsbestvineyards.com",
    reloaded: []
  },
  {
    name: "Passionate Wines",
    winemaker: "Matías Michelini",
    region: "Tupungato / Uco Valley",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Criolla Grande", "Torrontés", "Malbec"],
    approach: "Michelini's personal project with its own identity. Criolla Grande (10% ABV), Torrontés Brutal skin-contact white. Low intervention and undervalued varieties.",
    keyWines: ["Torrontés Brutal", "La Criolla Grande"],
    source: "naturalvin.com",
    reloaded: []
  },
  {
    name: "Cuvelier Los Andes",
    winemaker: "Bertrand Cuvelier",
    region: "Los Chacayes, Uco Valley",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Cab Franc", "Petit Verdot"],
    approach: "Certified organic. Bordeaux family (Léoville-Poyferré). Respectful winemaking expressing Los Chacayes terroir.",
    keyWines: ["Grand Vin", "Colección"],
    source: "vinofino.club",
    reloaded: []
  },
  {
    name: "Félix Enrique 1931",
    winemaker: "Fernando Páez Sarmiento (4th generation)",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Bonarda"],
    approach: "4th generation of organic viticulturists. Certified. Philosophy of returning more to the land than it gives. Leading voice in Argentina's organic wine movement (VIOS / Vinos Sustentables).",
    keyWines: ["Félix Enrique Malbec"],
    source: "vinetur.com / VIOS",
    reloaded: []
  },
  {
    name: "Andalhue",
    winemaker: "Andalhue team",
    region: "Neuquén",
    province: "Patagonia",
    category: "Emerging",
    grapes: ["Malbec", "Pinot Noir"],
    approach: "Biodynamic project in Patagonia. Part of the Argentine organic wine fair circuit.",
    keyWines: ["Andalhue Malbec", "Andalhue Pinot Noir"],
    source: "La Nación / vinofino.club",
    reloaded: []
  },
  {
    name: "Otronia",
    winemaker: "Juan Pablo Murgia (Grupo Avinea)",
    region: "Chubut, Atlantic Patagonia",
    province: "Patagonia",
    category: "Emerging",
    grapes: ["Pinot Noir", "Chardonnay", "Riesling"],
    approach: "50 organic hectares in southernmost Patagonia — the world's most southerly commercial vineyard. Part of the MatrizViva project. Head winemaker Juan Pablo Murgia, who described the 45th parallel latitude as 'conditions that create positive qualities in wine.' The 2025 vintage was exceptional despite 20% lower yields from strong Atlantic winds — Malbec 14.3% ABV with 11g/L total acidity and pH 3.1.",
    keyWines: ["Otronia Pinot Noir 45 Rugientes", "Otronia Chardonnay", "Otronia Malbec"],
    source: "espaciovino.com.ar / VIOS / James Suckling 2025 / Decanter",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },

  // ── ARTISAN / TERROIR-DRIVEN ─────────────────────────────────────
  {
    name: "Raquis",
    winemaker: "Andrés Vignoni (winemaker) / Facundo Impagliazzo (viticulture) / Ariel Núñez Porolli (director)",
    region: "Gualtallary / Chacayes / Altamira / San Pablo",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc"],
    approach: "Founded 2021 by three ex-Viña Cobos principals who spent a decade recalibrating their palates on Burgundy, Barolo, and Ribeira Sacra before asking: 'Are the wines we make today the ones we actually want to drink?' Four single-parcel wines (Gualtallary, Chacayes, Altamira, San Pablo) plus Raquis Monasterio from the highest Gualtallary sub-zone. Native yeasts, foudre aging, clayver vessels, minimal intervention — no certification but rigorous philosophy. 50 ha being developed on terraced slopes in Gualtallary Monasterio (respecting native flora), the next frontier after the flat valley floor. World of Fine Wine named them one of the new Gualtallary slope pioneers alongside Zuccardi and Riccitelli. Las Bases: 30% native yeasts, 35% whole cluster, 20 months foudre + tank.",
    keyWines: ["Raquis Monasterio (Gualtallary sub-zone)", "Los Parajes Gualtallary", "Los Parajes Chacayes", "Los Parajes Altamira", "Las Bases"],
    source: "vinomanos.com / infobae.com / worldoffinewine.com / wine-searcher.com",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Finca Ambrosia",
    winemaker: "Matías Macías (winemaker) / Daniel Pi (consultant) / Pedro Parra (terroir)",
    region: "Gualtallary Albo sub-zone, Tupungato",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Sauvignon", "Cabernet Franc", "Chardonnay", "Sauvignon Blanc"],
    approach: "Founded 2002 by 11 friends from 7 countries. 65 ha in Gualtallary's Albo sub-zone (named for its white calcareous limestone). Pedro Parra mapped the estate into micro-plots; Daniel Pi oversees winemaking. Fruit source for Trapiche Terroir Series (95-96 pts), Altos Las Hormigas, and Viña Cobos. Organic 'Casa' line (unwooded, from certified organic blocks). Harvest under full moon for the Luna line. Grand Cru = best-parcel selection, foudre-aged. Calcareous limestone soils regulate water and produce grapes with unique tannin/acidity profile.",
    keyWines: ["Grand Cru Malbec", "Grand Cru Blend", "Precioso", "Viña Única", "Casa Ambrosia (organic line)", "Luna (minimal intervention)"],
    source: "fincaambrosia.com / vintage82.eu / wine-searcher.com",
    reloaded: []
  },
  {
    name: "Humberto Canale",
    winemaker: "Ariel Rodríguez / 5th generation family",
    region: "Mainqué / General Roca, Alto Valle del Río Negro",
    province: "Patagonia",
    category: "Artisan / Terroir-Driven",
    grapes: ["Semillon", "Riesling", "Pinot Noir", "Malbec", "Trousseau", "Chardonnay"],
    approach: "Founded 1909 — the most historically significant winery in Río Negro. First vineyards planted 1912; five generations of continuous family ownership. 1942 Semillon vines (oldest in Patagonia); old-vine Riesling that South America Wine Guide calls 'one of Argentina's best'; Pinot Noir from the same Río Negro Valley as Chacra and Noemía. The 500 ha estate sits on the glacial alluvial plain of the Negro River, equidistant from the Andes and Atlantic. Cava Privada Semillon releases single bottles by number from specific years dating back to the 1980s. Sustainably farmed, old-school approach preserving what remains of Patagonia's viticultural heritage.",
    keyWines: ["Old Vineyard Semillon", "Old Vineyard Riesling", "Old Vineyard Malbec", "Old Vineyard Pinot Noir", "Cava Privada Semillon (library releases)"],
    source: "southamericawineguide.com / bodegahcanale.com / decanter.com",
    reloaded: []
  },
  {
    name: "Achaval Ferrer",
    winemaker: "Matías Alcalá",
    region: "Luján de Cuyo / Paraje Altamira / Vistalba",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Cabernet Sauvignon", "Merlot"],
    approach: "Founded 1998 by a group of Argentine friends obsessed with making Malbec that could stand alongside Barolo and Burgundy. Pioneered the single-vineyard Malbec concept in Argentina: Finca Bella Vista (Luján de Cuyo), Finca Mirador (Luján de Cuyo), Finca Altamira (Paraje Altamira). Works exclusively with very old vine parcels — many pre-phylloxera. Minimal winemaking intervention, no filtering. Quimera is the estate blend. 95 pts Tim Atkin (Finca Bella Vista 2022, $150); 95 pts Tim Atkin (Quimera Memento Single Vineyard 2022, $70).",
    keyWines: ["Malbec Finca Bella Vista", "Malbec Finca Altamira", "Malbec Finca Mirador", "Quimera", "Quimera Memento Single Vineyard"],
    source: "achavalferrer.com / Tim Atkin 2025",
    reloaded: []
  },
  {
    name: "Satélite (Familia Millán)",
    winemaker: "Maricel Váldez",
    region: "Valle de Uco — Los Chacayes / Los Arboles / Gualtallary",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Pinot Noir"],
    approach: "Dedicated Pinot Noir project drawing from seven carefully selected Uco Valley vineyards, ranging 1,000–1,600m altitude. Three tiers: entry (Los Arboles, 1,000–1,200m), mid (1,200–1,400m), and top (1,400–1,600m, Gualtallary). All 14 fermentation components aged separately through élévage in small unepoxy concrete vessels (200–2,000L), assembled only at bottling. Top tier earned 96 Descorchados 2023 — best Pinot Noir in their Argentina guide. Own vineyard in Los Chacayes.",
    keyWines: ["Satélite Pinot Noir (entry)", "Satélite Pinot Noir (mid)", "Satélite Pinot Noir (top — 96 Descorchados)"],
    source: "thewinetime.com.ar / familiamillan.com",
    reloaded: []
  },
  {
    name: "Altupalka",
    winemaker: "Alejandro Martorell",
    region: "Cafayate (1,750m) + Molinos (2,590m)",
    province: "Salta",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Torrontés", "Tannat", "Cabernet Sauvignon"],
    approach: "Boutique négociant project sourcing from two extreme-altitude Calchaquí Valley sites: a 9ha estate in Cafayate (1,750m) and 11ha in Molinos (2,590m). The Malbec-Malbec blend co-ferments fruit from both sites — the tension between the warmer Cafayate and the extreme cold of Molinos gives the wine its unusual profile of intensity plus balsamic precision. Featured in Decanter's Salta wines guide. No own winery — fruit processed at partner facilities.",
    keyWines: ["Altupalka Malbec-Malbec", "Altupalka Torrontés"],
    source: "southamericawineguide.com / decanter.com",
    reloaded: []
  },

  // ── NEW ADDITIONS FROM ARGENTINA RELOADED WINEMAKER CIRCUIT ──────

  // Artisan / Terroir-Driven
  {
    name: "Susana Balbo Wines",
    winemaker: "Susana Balbo & José Lovaglio Balbo",
    region: "Agrelo, Luján de Cuyo",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Torrontés", "Malbec", "Cabernet Sauvignon", "Semillon", "Cab Franc"],
    approach: "Argentina's first female winemaker (graduated 1981), founder of the winery in 1999. Credited with creating Argentina's first world-class Torrontés in the early 1980s in Cafayate. Family-run with son José (UC Davis) now leading R&D; deeply sustainability-focused with organic vineyard management. Tim Atkin Winemaking Legend 2020. Michelin Green Star for the restaurant Osadía de Crear (2024 & 2025). Confirmed at Argentina Reloaded Buenos Aires 2025 with son José.",
    keyWines: ["BenMarco Expresivo", "Susana Balbo Brioso Blend", "Susana Balbo Signature Torrontés", "Crios Torrontés"],
    source: "Argentina Reloaded Buenos Aires 2025 / Tim Atkin 2020 / enotriacoe.com",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Mendel Wines",
    winemaker: "Roberto de la Mota",
    region: "Perdriel, Luján de Cuyo + Paraje Altamira",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Sauvignon", "Semillon", "Chenin Blanc", "Petit Verdot"],
    approach: "Roberto de la Mota — widely considered the 'Godfather' of modern Argentine wine — founded Mendel in 2002 with the Sielecki family around historic 1928 estate vines in Perdriel. Son of legendary winemaker Raúl de la Mota; trained under Émile Peynaud in Montpellier; architect of the Terrazas de los Andes and Cheval des Andes programs. At Mendel: minimal intervention, no filtering, old vines only. Revival of ungrafted 70–80 year-old Semillon and Chenin Blanc — the Petit Verdot for Unus blend was massal selection from Château Margaux vines brought to Argentina in 1994. Tim Atkin Winemaking Legend 2024.",
    keyWines: ["Mendel Unus (Malbec/CS/PV)", "Finca Remota Malbec (Altamira)", "Mendel Semillon", "Lunta Malbec", "Mendel Cabernet Sauvignon"],
    source: "mendel.com.ar / worldoffinewine.com / vineconnections.com / Tim Atkin 2024",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Bodega Colomé",
    winemaker: "Thibaut Delmotte",
    region: "Calchaquí Valley, Molinos (2,300m) + Altura Máxima (3,111m)",
    province: "Salta",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Torrontés", "Tannat", "Bonarda", "Cab Sauvignon", "Syrah", "Petit Verdot"],
    approach: "Founded 1831 — Argentina's oldest winery, owned by the Hess family since 2001. French winemaker Thibaut Delmotte has been in charge since 2005, transforming it into a consistent Tim Atkin First Growth (2020–2024). Vineyards range from La Brava (1,750m in Cafayate) to Altura Máxima at 3,111m — one of the world's highest. All farmed with biodynamic and organic principles (not certified due to ant nest treatment). Minimal intervention: Auténtico aged in tank and concrete egg, zero oak. #31 James Suckling Top 100 Argentina 2025.",
    keyWines: ["Colomé Altura Máxima Malbec", "Colomé Auténtico Malbec", "Colomé Estate Malbec", "Colomé Torrontés", "Colomé Tannat"],
    source: "bodegacolome.com / libertywines.co.uk / Tim Atkin Argentina First Growth / James Suckling 2025",
    reloaded: ["Rio 2024"]
  },
  {
    name: "Zuccardi Valle de Uco",
    winemaker: "Sebastián Zuccardi",
    region: "Valle de Uco — Paraje Altamira / Gualtallary / San Pablo",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Semillon", "Bonarda", "Cabernet Franc", "Grenache"],
    approach: "Sebastián Zuccardi has led the winery into the rarefied air of 100-point Argentine Malbec (Piedra Infinita Gravascal). Obsessive terroir mapping across Altamira, Gualtallary, and beyond — working with Pedro Parra to understand Uco's limestone geology at granular scale. The Concreto Malbec is made with whole-cluster 'lasagna' layering and 100% concrete, earning #3 James Suckling Top 100 Argentina 2025. Zuccardi's classification of Altamira limestone sub-zones (caliche, gravascal) has redefined Argentine quality dialogue.",
    keyWines: ["Piedra Infinita Gravascal Malbec (100pts)", "Piedra Infinita Supercal Malbec", "Concreto Malbec (Altamira)", "Fosil Malbec", "Zuccardi Q Malbec"],
    source: "James Suckling Top 100 Argentina 2025 (100pts + #3) / Tim Atkin / worldoffinewine.com",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Bodega Lagarde",
    winemaker: "Sofía & Lucila Pescarmona",
    region: "Luján de Cuyo + Gualtallary",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Sauvignon", "Semillon", "Viognier", "Pinot Noir"],
    approach: "Founded 1897. Sofía Pescarmona took over in 2001 (with sister Lucila joining in 2011), steering an estate-wine pivot around the historic 1906 Luján de Cuyo bodega. Pioneers of Viognier and Moscato Bianco in Argentina. Two restaurant venues: Fogón and Zonda, the latter awarded a Michelin Green Star for sustainability. Old Vine Semillon from vines planted in 1906 is a reference point for the variety in Argentina.",
    keyWines: ["Lagarde Guarda Malbec", "Lagarde Old Vine Semillon 1906", "Lagarde Henry Gran Guarda Cabernet Sauvignon", "Lagarde Viognier"],
    source: "worldsbestvineyards.com / Argentina Reloaded Buenos Aires 2025",
    reloaded: ["Buenos Aires 2025"]
  },
  {
    name: "Matervini",
    winemaker: "Santiago Achával",
    region: "Gualtallary, Valle de Uco",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Cab Sauvignon"],
    approach: "Post-Achaval Ferrer project by Santiago Achával, co-founder of the winery that pioneered single-vineyard Malbec. Matervini is a precision terroir exercise focused on Gualtallary's calcareous limestone soils. The philosophy carries forward single-vineyard specificity with a tighter, more focused lens — fewer wines, more concentrated attention per parcel. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["Matervini Gualtallary Malbec", "Matervini Cabernet Franc"],
    source: "Argentina Reloaded Buenos Aires 2025 / Tim Atkin Argentina",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Casa Yagüe",
    winemaker: "Patricia Ferrari & Marcelo Yagüe",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Pinot Noir", "Chardonnay", "Semillon"],
    approach: "Patricia Ferrari and Marcelo Yagüe's family project, balancing Uco Valley terroir expression with minimal intervention. Small production, emphasis on freshness and drinkability over extraction. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["Casa Yagüe Malbec", "Casa Yagüe Pinot Noir", "Casa Yagüe Chardonnay"],
    source: "Argentina Reloaded Buenos Aires 2025",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "PerSe",
    winemaker: "Edy del Popolo & David Bonomi",
    region: "Multi-region — Mendoza / Luján de Cuyo / Uco Valley",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Semillon", "Cabernet Franc", "Torrontés"],
    approach: "PerSe was founded after Edy del Popolo and David Bonomi travelled every Argentine wine region with the specific goal of finding parcels whose character would shine through with minimal interference. Each wine expresses a single parcel exactly as it is — no oak obsession, no technological correction. Del Popolo is also General Manager at Susana Balbo (overseeing BenMarco); Bonomi is technical director at Bodega Norton. Their joint natural/low-intervention side project is among the most discussed in the new Argentine wave. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["PerSe Malbec single parcels", "PerSe Semillon"],
    source: "Argentina Reloaded Buenos Aires 2025 / argentinareloaded.com / winefolly.com",
    reloaded: ["Buenos Aires 2025"]
  },

  // Low Intervention
  {
    name: "Huichaira Vineyards",
    winemaker: "Ale Sejanovich & Jeff Mausbach",
    region: "Quebrada de Humahuaca, Jujuy",
    province: "Jujuy",
    category: "Low Intervention",
    grapes: ["Malbec", "Cabernet Franc", "Syrah", "Criolla Chica"],
    approach: "Ale Sejanovich and Jeff Mausbach source from small growers in the extreme-altitude gorge of Humahuaca in Jujuy (2,500–3,000m+). The soils are arid and stony, yields tiny. Jujuy's high UV, dramatic diurnal swings, and ancient alluvial soils produce co-fermented reds of unusual linearity: deep color, low pH, high natural acidity. Sejanovich quoted in James Suckling 2025: the altitude 'helps produce deep-colored wines with structure, low pH, and high natural acidity, creating uniquely balanced profiles.' The Cielo Arriba is a Malbec/Cab Franc/Syrah co-fermentation.",
    keyWines: ["Huichaira Cielo Arriba", "Huichaira Malbec"],
    source: "James Suckling Argentina 2025 Tasting Report / Argentina Reloaded circuit",
    reloaded: []
  },
  {
    name: "Bodega Tacuil",
    winemaker: "Raúl Yeyé Dávalos",
    region: "Calchaquí Valley, Salta",
    province: "Salta",
    category: "Low Intervention",
    grapes: ["Malbec", "Cabernet Sauvignon", "Torrontés", "Tannat"],
    approach: "One of the most storied family estates in Salta's upper Calchaquí Valley — the Dávalos family has farmed these vineyards for generations at altitude. Raúl 'Yeyé' Dávalos represents the custodian generation of a singular terroir. Bodega Colomé's 'Auténtico' is made as a homage to Raúl Dávalos Senior, who was famous for hating oak-aged wines. Old-vine, low-intervention, mountain-altitude wines. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["Tacuil Malbec", "Tacuil Torrontés"],
    source: "Argentina Reloaded Buenos Aires 2025 / Tim Atkin Argentina / libertywines.co.uk",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Canopus",
    winemaker: "Gabriel Dvoskin & María Hilen Pareja",
    region: "El Cepillo, Valle de Uco",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Pinot Noir", "Tempranillo", "Semillon"],
    approach: "Gabriel Dvoskin left a career as a journalist in Europe to work harvests in Burgundy and Friuli, then returned to Argentina to found Canopus in 2008. He found his terroir in El Cepillo — one of the coldest and most southerly corners of the Uco Valley, with calcareous soils, extreme diurnal swings, and erratic winds. 10 ha certified organic (LETIS) and biodynamic, farmed with deep ecological observation. María Hilen Pareja joined in 2020 after harvests in France, Italy, Chile, and the US. Zero additions, aging in used French barrels, amphora or ceramic spheres. The wines are defined by racy acidity, silky texture, and cool-climate tension — as far from extracted Mendoza Malbec as you can get.",
    keyWines: ["Pintom Malbec", "Pintom Rosado Subversivo (Pinot Noir rosé)", "Malbec De Sed"],
    source: "canopusvinos.com / morenaturalwine.com / Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Oír ese río",
    winemaker: "Germán Masera",
    region: "Alto Agrelo, Luján de Cuyo",
    province: "Mendoza",
    category: "Low Intervention",
    grapes: ["Malbec", "Cabernet Franc"],
    approach: "Side project from Germán Masera (Escala Humana), applying the same minimal-intervention philosophy to a stony (pedregoso) site in Alto Agrelo at 1,100m — a different register from his El Zampal work on ancient heritage varieties. Malbec/Cab Franc blend from glacial alluvial soils with a pebbly topsoil. Native yeasts, concrete. The name translates as 'listen to this river' — a nod to the water sources that define Mendoza's high-altitude terroirs.",
    keyWines: ["Oír ese río Malbec/Cab Franc"],
    source: "ozonodrinks.com.ar / Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Contracorriente",
    winemaker: "Jeff LeBard (consulting)",
    region: "Trevelín / Chubut, Atlantic Patagonia",
    province: "Patagonia",
    category: "Artisan / Terroir-Driven",
    grapes: ["Pinot Noir", "Chardonnay", "Malbec", "Syrah"],
    approach: "Founded by Montana-born friends Rance Rathie and Travis Smith, who pioneered viticulture in Chubut's extreme southern Patagonia after spending decades running Patagonia River Guides fly-fishing lodge. Glacial soils with clay and volcanic ash, maritime influence from Pacific winds channeled through the Andes via the Yelcho and Futaleufú Rivers. Cool, temperate climate with intense thermal amplitude (up to 30°C daily swing). Under 10,000 bottles/year. Consulting winemaker Jeff LeBard (20+ years at Gainey Vineyard, Santa Ynez, California). Wines are low-alcohol, fresh, and persistently long — unlike anything else in Argentina.",
    keyWines: ["Contracorriente Pinot Noir", "Contracorriente Malbec", "Contracorriente Chardonnay"],
    source: "contracorrientewinery.com / Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Bodega Weinert",
    winemaker: "Hubert Weber",
    region: "Luján de Cuyo",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
    approach: "Founded 1975 by German-Brazilian entrepreneur Bernardo Weinert. One of Argentina's most singular wineries — a deliberate anachronism committed to long cask aging and oxidative evolution in a way that predates and ignores the modern fruit-forward style. Wines spend years in large old oak vats, emerging with brick-hued color, dried fruit, leather, and secondary complexity that recalls aged Rioja or traditional Bordeaux. The historic 1977 Estrella de Weinert was made by Roberto de la Mota's father Raúl. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["Weinert Malbec", "Weinert Cavas de Weinert (blend)", "Weinert Estrella"],
    source: "Argentina Reloaded Buenos Aires 2025 / weinert.com.ar",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Bemberg Estate Wines",
    winemaker: "Santiago Mayorga",
    region: "Luján de Cuyo / Chacayes",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Cabernet Sauvignon", "Chardonnay"],
    approach: "The historic Bemberg family estate — one of Argentina's most prestigious — with deep roots in Luján de Cuyo and extended reach into Los Chacayes in the Uco Valley. Single-vineyard focus with meticulous terroir mapping; gravitational winery. Named after the Bemberg family, one of Argentina's most storied wine dynasties. Featured at Argentina Reloaded Rio de Janeiro 2024 and Buenos Aires 2025.",
    keyWines: ["Bemberg Alto Agrelo Malbec", "Bemberg Chacayes Malbec", "Bemberg Cabernet Franc"],
    source: "Argentina Reloaded Rio de Janeiro 2024 / Tim Atkin Argentina",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Casarena",
    winemaker: "Alejandro Vigil (consulting) / Casarena team",
    region: "Agrelo / Gualtallary",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Chardonnay", "Semillon"],
    approach: "Casarena is a single-vineyard specialist estate in Agrelo with additional vineyards in Gualtallary, systematically mapping the contrasts between Agrelo's warm clay-limestone soils and Gualtallary's cold calcareous terroir. Alejandro Vigil (El Enemigo) was long-term consulting winemaker. Featured at Argentina Reloaded Rio de Janeiro 2024.",
    keyWines: ["Casarena Lauren's Vineyard Malbec", "Casarena Owen's Vineyard Cabernet Franc", "Casarena Gualtallary Chardonnay"],
    source: "Argentina Reloaded Rio de Janeiro 2024 / casarena.com.ar",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Domaine Nico",
    winemaker: "Roy Urbieta",
    region: "Gualtallary, Tupungato",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Chardonnay", "Semillon", "Pinot Noir", "Malbec"],
    approach: "Alejandro Vigil's dedicated white wine and Pinot Noir project at Gualtallary, conceived as a Burgundian lens on Mendoza's highest and coldest terroir. Winemaker Roy Urbieta leads the cellar under Vigil's direction. The BenMarco Sin Límites Chardonnay — cited by World of Fine Wine as a 'striking backbone of acidity' example — helped establish Gualtallary as Argentina's preeminent white wine zone. White Bones and White Stones are landmark wines that have reset expectations for Argentine Chardonnay.",
    keyWines: ["Domaine Nico White Bones Chardonnay", "Domaine Nico White Stones Chardonnay", "Domaine Nico Pinot Noir"],
    source: "James Suckling Argentina 2025 / worldoffinewine.com / Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024"]
  },
  {
    name: "Puerta del Abra",
    winemaker: "Jorge Pérez Companc family",
    region: "Balcarce, Buenos Aires Province",
    province: "Patagonia",
    category: "Artisan / Terroir-Driven",
    grapes: ["Riesling", "Pinot Noir", "Chardonnay"],
    approach: "One of Argentina's most unusual and compelling wine projects: 12 hectares in Balcarce in the province of Buenos Aires — 115–137m altitude, Atlantic coastal influence, entirely different from the Andean model. Riesling planted 2014 from massal selection SO4 rootstock. Jorge Pérez Companc's personal project since 2013. The coastal Atlantic climate, loamy soils, and relatively low altitude produce wines with crisp natural acidity and a distinctly European sensibility. The Riesling is among Argentina's most distinctive whites — cool, mineral, and unlike anything from Mendoza.",
    keyWines: ["Puerta del Abra Riesling (Balcarce)", "Puerta del Abra Pinot Noir"],
    source: "argentinareloaded.com / Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Sophenia",
    winemaker: "Matías Garces Silva",
    region: "Gualtallary, Tupungato",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Cabernet Sauvignon", "Chardonnay"],
    approach: "Estate winery in Gualtallary with 200ha+ under vine at 1,200–1,500m. Sophenia was one of the early serious investors in high-altitude Gualtallary and has since developed a single-vineyard program. Synthesis is the premium tier, with estate Malbec and Cab Franc selected from the best parcels. Featured at Argentina Reloaded Rio de Janeiro 2024.",
    keyWines: ["Sophenia Synthesis Malbec", "Sophenia Synthesis Cab Franc", "Sophenia Altosur Malbec"],
    source: "Argentina Reloaded Rio de Janeiro 2024 / sophenia.com.ar",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Santa Julia",
    winemaker: "Zuccardi family / Laura Zuccardi",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Certified Organic + Natural",
    grapes: ["Malbec", "Torrontés", "Pinot Grigio", "Bonarda", "Cab Sauv"],
    approach: "The organic entry-level label from the Zuccardi family — certified organic across the entire range since 2008, making it one of the largest certified organic producers in Argentina. Santa Julia Orgánica was one of the first nationally distributed organic Argentine wine lines and helped define the category. Winemaking by Laura Principiano Zuccardi. Featured at Argentina Reloaded Rio de Janeiro 2024.",
    keyWines: ["Santa Julia Orgánica Malbec", "Santa Julia Magna Malbec", "Santa Julia Tardío (late harvest)"],
    source: "Argentina Reloaded Rio de Janeiro 2024 / zuccardiwines.com",
    reloaded: ["Rio 2024"]
  },

  // ── ADDITIONAL LOW INTERVENTION ───────────────────────────────────
  {
    name: "Solito",
    winemaker: "Solito team",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Criolla", "Semillon"],
    approach: "Small emerging natural/low-intervention producer selected by Paz Levinson for the Argentina Reloaded circuit. Minimal-intervention winemaking with a focus on honest site expression over extraction or oak.",
    keyWines: [],
    source: "Argentina Reloaded Rio de Janeiro 2024",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Tutú",
    winemaker: "Tutú team",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Bonarda", "Criolla"],
    approach: "Small natural wine producer featured at Argentina Reloaded Rio de Janeiro 2024 and Buenos Aires 2025. Part of Paz Levinson's curated roster of producers bringing fresh, identity-driven wines to international markets.",
    keyWines: [],
    source: "Argentina Reloaded Rio de Janeiro 2024 / Buenos Aires 2025",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Valle Arriba",
    winemaker: "Valle Arriba team",
    region: "Valle de Pucarà / Valle de Uco",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Franc", "Semillon"],
    approach: "Valle Arriba focuses on the Valle de Pucarà, one of Mendoza's newest and most promising sub-zones at extreme altitude in San Carlos. The El Pucareño Malbec was cited by James Suckling 2025 as showing 'singular character and sense of place, with darker fruit and greater intensity.' Featured at Argentina Reloaded Rio de Janeiro 2024 and Buenos Aires 2025.",
    keyWines: ["Valle Arriba El Pucareño Malbec"],
    source: "Argentina Reloaded Rio de Janeiro 2024 / James Suckling Argentina 2025",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },
  {
    name: "Ruca Malén",
    winemaker: "Lucas Nemec",
    region: "Agrelo, Luján de Cuyo",
    province: "Mendoza",
    category: "Artisan / Terroir-Driven",
    grapes: ["Malbec", "Cabernet Sauvignon", "Syrah", "Chardonnay", "Viognier"],
    approach: "Classic Agrelo estate founded 1997 by French and Argentine partners. Consistently benchmarked as one of Mendoza's most reliable single-vineyard estates, with Yauquén as the entry line and Kinien as the single-vineyard premium tier. Ruca Malén's restaurant is one of Mendoza's most respected wine lunch destinations. Featured at Argentina Reloaded Buenos Aires 2025.",
    keyWines: ["Ruca Malén Kinien Malbec", "Ruca Malén Kinien Cabernet Sauvignon", "Ruca Malén Yauquén Malbec"],
    source: "Argentina Reloaded Buenos Aires 2025 / rucamalen.com",
    reloaded: ["Rio 2024","Buenos Aires 2025"]
  },

  // Emerging
  {
    name: "Delfina Pontaroli",
    winemaker: "Delfina Pontaroli",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Semillon", "Pinot Noir"],
    approach: "Emerging winemaker from Mendoza's next generation with a focus on freshness and low-intervention technique. Paz Levinson has included her in the Argentina Reloaded circuit as a producer bringing a distinct new voice to Uco Valley terroir.",
    keyWines: ["Delfina Pontaroli Malbec"],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Emiliano Turano Ochoa",
    winemaker: "Emiliano Turano Ochoa",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Criolla", "Torrontés"],
    approach: "Emerging Argentine producer in Paz Levinson's Reloaded circle. Representative of a generation bringing hyper-local identity and minimal cellar intervention to Argentina's diverse terroirs.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Eugenia Luka",
    winemaker: "Eugenia Luka",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Criolla", "Semillon"],
    approach: "Emerging winemaker in Paz Levinson's network; part of a cohort of women leading Argentina's artisan wave. Low-intervention, small-production wines from Mendoza with an identity-focused approach.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Giuseppe Franceschini",
    winemaker: "Giuseppe Franceschini",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Bonarda", "Nebbiolo"],
    approach: "Italian-Argentine producer whose wines bridge Old World sensibility with Mendoza terroir. Part of Paz Levinson's curated Reloaded roster. Works with a low-intervention approach and Italian heritage varieties alongside Argentine classics.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Lucía Romero",
    winemaker: "Lucía Romero",
    region: "Salta / Calchaquí Valley",
    province: "Salta",
    category: "Emerging",
    grapes: ["Torrontés", "Malbec", "Tannat"],
    approach: "Emerging winemaker from northern Argentina's high-altitude Calchaquí Valley. In Paz Levinson's circle as an example of the next generation asserting Salta's distinct identity beyond Torrontés, with minimal-intervention reds from extreme altitude parcels.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Mariano Miretti & Ale González",
    winemaker: "Mariano Miretti & Ale González",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Cabernet Franc", "Semillon"],
    approach: "Collaborative winemaking project by Mariano Miretti and Ale González, focused on Uco Valley terroir expression with a fresh, low-intervention approach. Part of Paz Levinson's Argentina Reloaded winemaker roster.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Matías Prieto",
    winemaker: "Matías Prieto",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Criolla", "Pinot Noir"],
    approach: "Emerging small-producer in Mendoza. Low-intervention wines with a focus on site honesty. Selected by Paz Levinson for the Reloaded circuit based on quality and philosophy rather than scale.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Pancho Bugallo",
    winemaker: "Pancho Bugallo",
    region: "Mendoza",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Criolla", "Bonarda"],
    approach: "Francisco 'Pancho' Bugallo is among Mendoza's most talked-about emerging natural wine producers. Low-sulfite, native-yeast driven approach with a strong emphasis on heritage varieties. Featured in Paz Levinson's network.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Santiago Mayorga",
    winemaker: "Santiago Mayorga",
    region: "Valle de Uco",
    province: "Mendoza",
    category: "Emerging",
    grapes: ["Malbec", "Cabernet Franc", "Semillon"],
    approach: "Emerging Uco Valley winemaker selected by Paz Levinson for the Reloaded circuit. Low-intervention wines emphasizing terroir clarity from Mendoza's mountain-altitude zones.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  },
  {
    name: "Sofía Elena",
    winemaker: "Sofía Elena",
    region: "Salta / Jujuy",
    province: "Salta",
    category: "Emerging",
    grapes: ["Torrontés", "Malbec", "Criolla"],
    approach: "Emerging winemaker from northern Argentina. Part of Paz Levinson's Reloaded network as a voice representing the diversity and upside of high-altitude northern winemaking — both in Salta and Jujuy's extreme terroirs.",
    keyWines: [],
    source: "Argentina Reloaded winemaker circuit",
    reloaded: []
  }
];

const categories = ["All", "Radical Natural", "Low Intervention", "Certified Organic + Natural", "Biodynamic", "Artisan / Terroir-Driven", "Emerging"];
const provinces = ["All", "Mendoza", "Patagonia", "Jujuy", "San Juan", "Salta"];

const catConfig = {
  "Radical Natural":             { color: "#e05c3a", bg: "rgba(224,92,58,0.12)",  border: "rgba(224,92,58,0.4)" },
  "Low Intervention":            { color: "#8ab4a0", bg: "rgba(138,180,160,0.1)", border: "rgba(138,180,160,0.3)" },
  "Certified Organic + Natural": { color: "#c8a84b", bg: "rgba(200,168,75,0.1)",  border: "rgba(200,168,75,0.3)" },
  "Biodynamic":                  { color: "#9b7fd4", bg: "rgba(155,127,212,0.12)",border: "rgba(155,127,212,0.3)" },
  "Artisan / Terroir-Driven":    { color: "#d4935a", bg: "rgba(212,147,90,0.12)", border: "rgba(212,147,90,0.4)" },
  "Emerging":                    { color: "#6ab0d4", bg: "rgba(106,176,212,0.1)", border: "rgba(106,176,212,0.3)" },
};

export default function ArgNaturalWine() {
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("All");
  const [prov, setProv] = useState("All");
  const [sort, setSort] = useState("cat");
  const [expanded, setExpanded] = useState(null);
  const [reloadedOnly, setReloadedOnly] = useState(false);
  const [reloadedCity, setReloadedCity] = useState("All");

  const filtered = useMemo(() => {
    let list = [...producers];
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        [p.name, p.winemaker, p.region, p.approach, ...p.grapes, ...p.keyWines]
          .some(s => s.toLowerCase().includes(q))
      );
    }
    if (reloadedOnly) list = list.filter(p => p.reloaded && p.reloaded.length > 0);
    if (reloadedCity !== "All") list = list.filter(p => p.reloaded && p.reloaded.includes(reloadedCity));
    if (cat !== "All") list = list.filter(p => p.category === cat);
    if (prov !== "All") list = list.filter(p => p.province === prov);
    const catOrder = ["Radical Natural","Low Intervention","Certified Organic + Natural","Biodynamic","Artisan / Terroir-Driven","Emerging"];
    if (sort === "name") list.sort((a,b) => a.name.localeCompare(b.name));
    if (sort === "region") list.sort((a,b) => a.region.localeCompare(b.region));
    if (sort === "cat") list.sort((a,b) => catOrder.indexOf(a.category) - catOrder.indexOf(b.category));
    return list;
  }, [search, cat, prov, sort, reloadedOnly, reloadedCity]);

  const toggle = (name) => setExpanded(e => e === name ? null : name);

  return (
    <div style={{ fontFamily: "'Georgia', serif", background: "#080c0a", minHeight: "100vh", color: "#d8d0c0" }}>

      {/* HEADER */}
      <div style={{ padding: "36px 28px 20px", borderBottom: "1px solid #1e2820" }}>
        <div style={{ fontSize: 10, letterSpacing: "0.3em", color: "#4a6050", textTransform: "uppercase", marginBottom: 10 }}>
          Natural Wine · Organic · Biodynamic · Artisan Terroir · Argentina
        </div>
        <h1 style={{ margin: 0, fontSize: 26, fontWeight: 400, color: "#e8e0d0", letterSpacing: "0.04em" }}>
          Argentine Producers
        </h1>
        <p style={{ margin: "8px 0 0", fontSize: 12, color: "#506058", fontStyle: "italic" }}>
          {filtered.length} of {producers.length} producers · Mendoza · Patagonia · Jujuy · San Juan · Salta
        </p>
      </div>

      {/* LEGEND */}
      <div style={{ padding: "14px 28px", borderBottom: "1px solid #1e2820", display: "flex", gap: 10, flexWrap: "wrap" }}>
        {Object.entries(catConfig).map(([k, v]) => (
          <span key={k} style={{ fontSize: 10, padding: "3px 9px", borderRadius: 2, letterSpacing: "0.1em", textTransform: "uppercase", background: v.bg, color: v.color, border: `1px solid ${v.border}` }}>
            {k}
          </span>
        ))}
      </div>

      {/* CONTROLS */}
      <div style={{ padding: "16px 28px", borderBottom: "1px solid #1a211c", display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center", background: "#0a0f0b" }}>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search producer, variety, region…"
          style={{ background: "#131a14", border: "1px solid #2a3828", borderRadius: 3, color: "#c8c0b0", padding: "7px 13px", fontSize: 12, fontFamily: "inherit", width: 220, outline: "none" }}
        />

        {/* RELOADED FILTER */}
        <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
          <button onClick={() => { setReloadedOnly(r => !r); setReloadedCity("All"); }} style={{
            padding: "5px 13px", fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
            fontFamily: "inherit", cursor: "pointer", borderRadius: 2, transition: "all 0.15s",
            border: `1px solid ${reloadedOnly ? "#c8a84b" : "#1e2820"}`,
            background: reloadedOnly ? "rgba(200,168,75,0.15)" : "transparent",
            color: reloadedOnly ? "#c8a84b" : "#4a6050",
            display: "flex", alignItems: "center", gap: 5
          }}>
            <span style={{ fontSize: 11 }}>✦</span> Reloaded
          </button>
          {reloadedOnly && ["All","Rio 2024","Buenos Aires 2025"].map(city => (
            <button key={city} onClick={() => setReloadedCity(city)} style={{
              padding: "4px 9px", fontSize: 9, letterSpacing: "0.08em", textTransform: "uppercase",
              fontFamily: "inherit", cursor: "pointer", borderRadius: 2, transition: "all 0.15s",
              border: `1px solid ${reloadedCity === city ? "#c8a84b" : "#2a3020"}`,
              background: reloadedCity === city ? "rgba(200,168,75,0.12)" : "transparent",
              color: reloadedCity === city ? "#c8a84b" : "#3a4830",
            }}>{city}</button>
          ))}
        </div>

        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
          {categories.map(c => (
            <button key={c} onClick={() => setCat(c)} style={{
              padding: "5px 11px", fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase",
              fontFamily: "inherit", cursor: "pointer", borderRadius: 2, transition: "all 0.15s",
              border: `1px solid ${cat === c ? (catConfig[c]?.border || "#6a8070") : "#1e2820"}`,
              background: cat === c ? (catConfig[c]?.bg || "rgba(100,120,100,0.15)") : "transparent",
              color: cat === c ? (catConfig[c]?.color || "#8ab4a0") : "#4a6050",
            }}>{c}</button>
          ))}
        </div>

        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
          {provinces.map(p => (
            <button key={p} onClick={() => setProv(p)} style={{
              padding: "5px 10px", fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase",
              fontFamily: "inherit", cursor: "pointer", borderRadius: 2, transition: "all 0.15s",
              border: `1px solid ${prov === p ? "#6a8870" : "#1e2820"}`,
              background: prov === p ? "rgba(106,136,112,0.15)" : "transparent",
              color: prov === p ? "#8aaa90" : "#3a5040",
            }}>{p}</button>
          ))}
        </div>

        <div style={{ marginLeft: "auto", display: "flex", gap: 4, alignItems: "center" }}>
          <span style={{ fontSize: 9, color: "#334038", letterSpacing: "0.15em", textTransform: "uppercase" }}>Sort</span>
          {[["cat","Category"],["name","Name"],["region","Region"]].map(([v,l]) => (
            <button key={v} onClick={() => setSort(v)} style={{
              padding: "5px 10px", fontSize: 10, letterSpacing: "0.06em", fontFamily: "inherit", cursor: "pointer",
              borderRadius: 2, border: `1px solid ${sort===v?"#4a6050":"#1e2820"}`,
              background: sort===v?"rgba(74,96,80,0.2)":"transparent",
              color: sort===v?"#8aaa90":"#3a5040", transition: "all 0.15s"
            }}>{l}</button>
          ))}
        </div>
      </div>

      {/* LIST */}
      <div style={{ padding: "18px 28px", display: "flex", flexDirection: "column", gap: 8 }}>
        {filtered.length === 0 && (
          <div style={{ color: "#2a4030", fontStyle: "italic", textAlign: "center", padding: 48, fontSize: 13 }}>
            No results for this search.
          </div>
        )}
        {filtered.map(p => {
          const c = catConfig[p.category];
          const open = expanded === p.name;
          return (
            <div key={p.name} onClick={() => toggle(p.name)} style={{
              background: open ? "#0f1812" : "#0c1210",
              border: `1px solid ${open ? c.border : "#1a2218"}`,
              borderLeft: `3px solid ${c.color}`,
              borderRadius: 3, cursor: "pointer", transition: "all 0.15s"
            }}>
              <div style={{ padding: "13px 16px", display: "grid", gridTemplateColumns: "1fr auto auto", gap: 10, alignItems: "center" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 14, color: "#e0d8c8", letterSpacing: "0.02em" }}>{p.name}</span>
                    <span style={{ fontSize: 9, padding: "2px 7px", letterSpacing: "0.12em", textTransform: "uppercase", background: c.bg, color: c.color, border: `1px solid ${c.border}`, borderRadius: 2 }}>
                      {p.category}
                    </span>
                    {p.reloaded && p.reloaded.length > 0 && (
                      <span style={{ fontSize: 9, padding: "2px 7px", letterSpacing: "0.1em", textTransform: "uppercase", background: "rgba(200,168,75,0.1)", color: "#c8a84b", border: "1px solid rgba(200,168,75,0.35)", borderRadius: 2 }}>
                        ✦ Reloaded
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 11, color: "#4a6050", marginTop: 3, fontStyle: "italic" }}>
                    {p.winemaker} · {p.region}, {p.province}
                  </div>
                </div>

                <div style={{ display: "flex", gap: 4, flexWrap: "wrap", justifyContent: "flex-end" }}>
                  {p.grapes.slice(0, 3).map(g => (
                    <span key={g} style={{ fontSize: 9, padding: "2px 6px", border: "1px solid #1e2820", borderRadius: 2, color: "#4a6050", letterSpacing: "0.07em" }}>{g}</span>
                  ))}
                </div>

                <span style={{ color: "#2a4030", fontSize: 14, display: "block", transition: "transform 0.2s", transform: open ? "rotate(180deg)" : "none" }}>▾</span>
              </div>

              {open && (
                <div style={{ padding: "14px 16px 16px", borderTop: `1px solid ${c.border}`, background: "rgba(0,0,0,0.2)" }}>
                  <p style={{ margin: "0 0 10px", fontSize: 12, color: "#8aaa90", lineHeight: 1.75, fontStyle: "italic" }}>
                    {p.approach}
                  </p>
                  {p.keyWines.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
                      <span style={{ fontSize: 10, color: "#3a5040", letterSpacing: "0.1em", textTransform: "uppercase", marginRight: 4 }}>Key wines:</span>
                      {p.keyWines.map(w => (
                        <span key={w} style={{ fontSize: 10, padding: "2px 8px", border: `1px solid ${c.border}`, borderRadius: 2, color: c.color, background: c.bg }}>{w}</span>
                      ))}
                    </div>
                  )}
                  <div style={{ fontSize: 10, color: "#2a3c30", letterSpacing: "0.08em" }}>
                    Source: {p.source}
                  </div>
                  {p.reloaded && p.reloaded.length > 0 && (
                    <div style={{ marginTop: 8, display: "flex", gap: 5, flexWrap: "wrap", alignItems: "center" }}>
                      <span style={{ fontSize: 9, color: "#c8a84b", letterSpacing: "0.1em", textTransform: "uppercase" }}>✦ Argentina Reloaded:</span>
                      {p.reloaded.map(ed => (
                        <span key={ed} style={{ fontSize: 9, padding: "2px 8px", border: "1px solid rgba(200,168,75,0.3)", borderRadius: 2, color: "#c8a84b", background: "rgba(200,168,75,0.08)", letterSpacing: "0.07em" }}>{ed}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div style={{ padding: "16px 28px 24px", borderTop: "1px solid #141c16", fontSize: 9, color: "#233028", letterSpacing: "0.12em", textTransform: "uppercase", lineHeight: 1.8 }}>
        Sources: bistrosoft.com · inmendoza.com · vinofino.club · chakanawines.com · iprofesional.com · espaciovino.com.ar ·
        vinetur.com · La Nación · James Suckling 2025 · VellaTerra · Grand Cru Brasil · Wine Enthusiast · Natural Vin · bodegachacra.com
      </div>
    </div>
  );
}
