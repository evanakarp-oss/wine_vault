---
type: source_readme
source: vinolist
updated: 2026-06-21
status: scaffolded — data contract + registry defined; scraper/compiler not yet written
---

# Vinolist NYC — source layer

[Vinolist NYC](https://vinolistnyc.com/) is a search engine that aggregates **NYC
restaurant wine lists** ("65 Restaurants, 37,878 Bottles" at last check; the count
drifts as lists re-scrape). It is **not a retailer** — nothing is for sale. It's a
**sommelier-demand / market-pulse source**: which producers the best NYC lists
actually pour, at what price, on how many lists. Different community from Berserkers
(US amateurs) or LPV (French amateurs) — this is the **trade/somm** signal.

This source layer mirrors `raw/lpv/` and `raw/berserkers/`. Each ingested restaurant
becomes a `restaurants/<slug>.json` that downstream scripts compile into producer-page
signals (`community.vinolist.*` frontmatter + an optional body mention) and `_views/`
rollups (top-N by list-count, price floors, momentum, vault-gap candidates).

Serves three jobs (see the keeper view
[`wiki/_views/nyc_restaurant_wine_lists_2026_06.md`](../../wiki/_views/nyc_restaurant_wine_lists_2026_06.md)):
1. **Restaurant database** — top NYC lists, taste-filtered.
2. **Producer tracking** — popularity (# lists) · price (min/avg/max) · prestige
   (which lists) · momentum (Δ list-count between dated snapshots).
3. **Discovery** — producers on many top lists not yet in the vault → onboarding triage.

## ⚠️ Scraper blocker (read first)

vinolistnyc.com **403s the WebFetch tool** (bot protection) **and the host is
egress-blocked** from the Claude-Code-on-web environment. Same situation as LPV. Until
a real scraper exists (browser headers/session run locally, or a manual paste
workflow), ingest is **manual paste**: copy a restaurant's list into
`restaurants/<slug>.raw.md`, then parse. The data contract below is designed so a
future automated scraper drops in without changing the JSON shape.

## Layout

```
raw/vinolist/
├── README.md                    this file
├── restaurants/
│   ├── _TEMPLATE.json           the canonical JSON shape (copy to start a restaurant)
│   ├── index.md                 registry of restaurants to ingest (taste-tagged)
│   ├── <slug>.raw.md            raw scraped/pasted list dump (one per restaurant)
│   └── <slug>.json              structured, compiler-ready (one per restaurant)
└── snapshots/                   dated producer-frequency rollups (for momentum tracking)
    └── producers_<YYYY-MM-DD>.json   (one per scrape run; diffed for momentum)
```

## Restaurant JSON shape

See `restaurants/_TEMPLATE.json` for the copy-paste skeleton. Summary:

```json
{
  "restaurant": {
    "slug": "eleven_madison_park",            // matches filename; key in registry
    "name": "Eleven Madison Park",
    "url": "https://www.vinolistnyc.com/restaurant/eleven-madison-park",
    "borough": "Manhattan",                    // Manhattan | Brooklyn | Queens | ...
    "tier": "grand_cellar",                    // grand_cellar | grower_champagne | grower_french | italian_deepcut | natural_bar
    "bottle_count": 3306,                      // int|null — as displayed
    "price_min": 35,                           // int|null — USD
    "price_max": 28000,                        // int|null
    "wine_director": null,                     // string|null
    "scraped_at": "YYYY-MM-DD",
    "scrape_method": "manual_paste_v1 | html_v1 | template"
  },
  "wines": [
    {
      "raw_producer": "Jacques Selosse",
      "slug": "selosse",                        // optional resolved vault slug (LLM curation)
      "cuvee": "Substance",                     // optional
      "region": "Champagne",                    // top-level region per _TAXONOMY.md (optional)
      "vintage": null,                          // int|null
      "price": 1200,                            // int|null — USD bottle price on this list
      "color": "sparkling"                      // red|white|rose|sparkling|orange|fortified|null
    }
  ]
}
```

`null` is allowed for any optional field — the compiler degrades gracefully (same
contract as Berserkers/LPV). `slug` is filled by LLM curation, not blind
string-matching (strip `Domaine `/`Champagne `/`Weingut ` prefixes; resolve
surname collisions per Evan's taste, as the Blachon view documents for LPV).

## Derived producer signal (`community.vinolist.*`)

The compiler aggregates `wines[]` across all `restaurants/*.json` into a per-producer
block: how many lists carry the producer, the price floor/median, and which prestige
lists (EMP / Le Bernardin) it sits on. Schema block lives in `wiki/_SCHEMA.md` →
`community.vinolist` (**scaffolded — no producer pages carry it yet**). Momentum comes
from diffing dated `snapshots/producers_<date>.json`.

## Pipeline (planned — scripts not yet written)

Mirrors the Berserkers four-script pipeline. **None of these exist yet**; this README
defines the contract they'll implement.

```
scrape_vinolist.py        URL/all            → restaurants/<slug>.raw.md   (TODO — blocked by 403/egress; manual paste for now)
parse_vinolist.py         <slug>.raw.md      → restaurants/<slug>.json     (TODO)
compile_vinolist_signals.py  restaurants/*.json → wiki/producers/*.md      (TODO — writes community.vinolist.*)
build_vinolist_rollups.py    all + snapshots → wiki/_views/*.md            (TODO — top-N, price floors, momentum, gap candidates)
```

Each will be dry-run by default; `--apply` to write — same convention as `*_wb_*`.

## Adding a restaurant (manual-paste workflow, today)

1. Copy `restaurants/_TEMPLATE.json` → `restaurants/<slug>.json`; fill `restaurant.*`.
2. Paste the list (or the Vinolist restaurant page) into `restaurants/<slug>.raw.md`.
3. Hand-fill (or LLM-fill) the `wines[]` array, resolving `slug` per Evan's curation
   taste; leave unknown fields `null`.
4. Register the slug in `wiki/_TAXONOMY.md` → `community.vinolist.restaurants` and
   flip its status in `restaurants/index.md`.
5. When `compile_vinolist_signals.py` exists, run it `--apply`; until then the JSON
   is the durable record and can be read directly during `/ask-cellar`.

## Scope (Evan's taste — which lists to mine first)

Prioritise lists dense in his lanes: grower-Champagne / Riesling (Terroir, Compagnie,
Le Bernardin), grower-French minimalist (Le Veau d'Or, Frenchette, Winona's, Ops, Lei),
Italian deep-cuts (Peasant), and the grand cellars for aged drink-now classed-growth
(EMP, Chambers). Candidate restaurants are listed in `restaurants/index.md`.
