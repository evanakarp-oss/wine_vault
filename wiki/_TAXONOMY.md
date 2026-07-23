---
type: taxonomy
updated: 2026-04-21
---

# Wine Wiki Taxonomy

Allowed values for the enumerated frontmatter fields. The lint script rejects values not in this list (to prevent e.g. "Bourgogne" vs. "Burgundy" vs. "Burgundie" drift).

Add new values here FIRST, then use them in producer files.

## `country`

- France
- Germany
- Italy
- Spain
- Austria
- Portugal
- Greece
- Georgia
- United States
- Argentina
- Chile
- Uruguay
- Slovenia
- Switzerland

## `region` (indexed by country)

### France
- Alsace
- Beaujolais
- Bordeaux
- Burgundy
- Champagne
- Corsica
- Jura
- Loire
- Provence
- Rhône
- Savoie
- South West
- Languedoc-Roussillon
- Basque (Irouléguy)

### Germany
- Ahr
- Baden
- Franken
- Mosel
- Nahe
- Pfalz
- Rheingau
- Rheinhessen
- Württemberg

### Italy
- Piedmont
- Tuscany
- Sicily
- Sardinia
- Veneto
- Lombardy
- Friuli-Venezia Giulia
- Alto Adige / Südtirol
- Valle d'Aosta
- Marche
- Abruzzo
- Basilicata
- Calabria
- Campania
- Liguria
- Colli Tortonesi
- Emilia-Romagna
- Umbria
- Lazio
- Molise
- Apulia

### Spain
- Catalonia
- Bierzo
- Rioja
- Galicia
- Jumilla
- Ribera del Duero
- Basque Country

### Argentina
- Mendoza
- Patagonia
- Salta
- Jujuy
- San Juan
- Buenos Aires Province

### Switzerland
- Valais
- Vaud
- Geneva
- Neuchâtel
- Ticino

### Slovenia
- Goriška Brda
- Vipava Valley
- Kras (Karst)

## `farming`

- conventional
- sustainable
- organic
- biodynamic
- natural

(These are additive — a producer can be both organic and biodynamic, or biodynamic and natural.)

## `certifications`

- Demeter (biodynamic)
- Ecocert (organic, EU)
- USDA Organic
- Vignerons Indépendants
- HVE (Haute Valeur Environnementale)
- Biodyvin
- Triple A (Velier)

## `retailers` (keys in the retailers frontmatter block)

- `chambers` → Chambers Street Wines (NYC)
- `dte` → Down to Earth Wines / Robert Panzer (NYC importer)
- `raeders` → Raeder's
- `fass` → FASS

(Add more here as new retailers are modeled — each gets its own key and its own section in the producer body.)

## `source` (top-level source-role enum, parallel to `retailers:`)

- `roscioli_wine_club` → Roscioli Wine Club (Rome-based Italian importer-curator). Producer pages with Roscioli coverage carry a top-level `roscioli:` frontmatter block and a `## Roscioli Wine Club` body section. 156 producer profiles indexed at `wiki/importers/Roscioli_Wine_Club.md`.

## `events` (curatorial / festival series)

Producer-frontmatter `events: []` accepts these slugs. Each event has its own rollup page in `wiki/events/`.

- `argentina_reloaded_rio_2024` — Argentina Reloaded, Rio de Janeiro 2024 (curator: Paz Levinson)
- `argentina_reloaded_buenos_aires_2025` — Argentina Reloaded, Buenos Aires 2025 (curator: Paz Levinson)
- `argentina_reloaded_london_2022` — Argentina Reloaded, London 2022 (curator: Paz Levinson)

Add new events here first, then reference them in producer files.

## `tags`

Free-form, but lowercase, hyphenated. Some encouraged conventions:

- Region slug: `alsace`, `burgundy`, `mosel`, `piedmont`
- Farming: `organic`, `biodynamic`, `natural`
- Style: `grower-champagne`, `kabinett`, `old-vines`, `white-wine-focused`, `nebbiolo-specialist`
- Scale: `micro-production`, `négociant`
- Status: `cult`, `widely-available`, `allocation-only`

## `community` (sources keyed under the `community:` frontmatter block)

- `berserkers` → Wine Berserkers community forum (https://www.wineberserkers.com)
- `lpv` → La Passion du Vin, French amateur forum (https://www.lapassionduvin.com)

### `community.berserkers.threads` (registered thread slugs)

Each entry is a thread that has been ingested via `scripts/scrape_wb_thread.py`
+ `parse_wb_thread.py`. Producer pages reference the slug; the canonical
metadata (URL, title, post count) lives in
`raw/berserkers/threads/<slug>.json`.

| Slug | Title | URL |
|---|---|---|
| `top10_in_cellar` | Top 10 Producers in your cellar? | https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370 |

(Add a row when ingesting a new thread.)

### `community.lpv.threads` (registered thread slugs)

Each entry is an LPV thread ingested into `raw/lpv/threads/<slug>.json`.
Threads come in three kinds — `producer_fil`, `blind_panel`, `best_of_poll`
(see `raw/lpv/README.md`). **None ingested yet**; candidate anchor threads to
ingest are listed in `raw/lpv/threads/index.md`.

| Slug | Kind | Title | URL |
|---|---|---|---|
| _(none yet)_ | | | |

(Add a row when ingesting a thread; the slug must match the JSON filename.)

### `community.vinolist.restaurants` (registered restaurant slugs)

Each entry is an NYC restaurant whose wine list has been ingested from
[Vinolist NYC](https://vinolistnyc.com/) into
`raw/vinolist/restaurants/<slug>.json`. The slug is referenced when aggregating
per-producer `community.vinolist.*` signals. **None ingested yet** (scraper blocked —
403 + egress); candidate restaurants are listed in `raw/vinolist/restaurants/index.md`.
`tier` ∈ `grand_cellar`, `grower_champagne`, `grower_french`, `italian_deepcut`,
`natural_bar`.

| Slug | Restaurant | Tier | URL |
|---|---|---|---|
| _(none yet)_ | | | |

(Add a row when ingesting a restaurant; the slug must match the JSON filename.)
