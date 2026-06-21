---
type: view
updated: 2026-06-21
question: "Which NYC restaurants have the best wine lists for Evan's taste, and how do I use Vinolist NYC to track producers (popularity / price / prestige) and discover new ones?"
scope: New York City restaurant wine lists, via vinolistnyc.com (aggregator) + editorial cross-refs
source: vinolist
caveat: "vinolistnyc.com 403s the fetcher (bot protection) and the host is egress-blocked from this environment. Bottle counts / price ranges below are real where they carry a Vinolist link (search-surfaced from indexed pages); the editorial roster and producer sightings are from Resy / Star Wine List / Wine Spectator / Decanter / VinePair snippets and should be verified in-browser before quoting."
---

# NYC Restaurant Wine Lists — destination guide + Vinolist tracking recipe (2026-06)

[Vinolist NYC](https://vinolistnyc.com/) is **not a shop, importer, or bar** — it's a
search engine that aggregates NYC **restaurant** wine lists into one place
("65 Restaurants, 37,878 Bottles" as of this snapshot; the count drifts as lists
re-scrape). You search **across every list at once by restaurant, producer, or
cuvée**, and each restaurant gets a page with bottle count, color split, and
min/avg/max price. Founder (lower-confidence): **Etesh Mangray**, who holds the
older `vinolist.com — "The Wine Database"` trademark — reads as a data/tech product,
not a somm's curated portfolio.

This page does three jobs Evan asked of the source:
1. **Restaurant picks** — top NYC lists, filtered to his taste (below).
2. **Producer tracking** — how to use Vinolist as a popularity / price / prestige
   gauge (the "recipe" + seed snapshot below; full pipeline scaffolded in
   `raw/vinolist/`).
3. **Discovery** — producers spotted across top lists that aren't yet in the vault.

---

## 1 · Restaurant picks — best NYC lists for Evan's taste

Grouped by character. **★ = confirmed indexed on Vinolist** (linked); the rest are
editorial top-lists worth searching Vinolist for. Bottle counts/prices are
point-in-time.

### Grand cellars (depth, verticals, aged classed-growth for drink-now)
- ★ **[Eleven Madison Park](https://www.vinolistnyc.com/restaurant/eleven-madison-park)** — ~3,306 bottles, $35–$28,000. Cathedral list; deep Burgundy/Bordeaux/Champagne verticals. The place to find aged classed-growth by the bottle.
- ★ **[Chambers](https://www.vinolistnyc.com/restaurant/chambers)** — ~2,017 bottles, $20–$3,950.
- **Le Bernardin** — Aldo Sohm's ~1,635-label list; strong Champagne incl. grower **Agrapart & Fils**.

### Grower Champagne / Riesling specialists (his Champagne + Mosel lanes)
- **Terroir (Tribeca)** — Paul Grieco; 80+ BTG at all times incl. **30 Rieslings**; grower Champagne (**Dhondt-Grellet, La Rogerie, Suenen**). Maps almost perfectly to the Champagne + Mosel filters.
- **Compagnie (Flatiron)** — list opens with otherwise-unattainable **Anselme Selosse**; serious grower-Champagne depth.
- **Aldo Sohm Wine Bar**, **Maison Premiere** — Champagne-forward.

### Minimalist / grower-French (Burgundy · Loire · Beaujolais · Alsace · Jura)
- **Le Veau d'Or** — Jorge Riera; ~100 biodynamic/organic French + seasonal Champagne list. (Frenchette team.)
- **Frenchette** — Riera again; the past decade's grower/minimalist French zeitgeist.
- **Winona's (Bklyn)** — Henry Mermer's ~400-label natural-French list (**Julien Meyer** Alsace, **Tarlant** Champagne, **Nicolas Joly** Loire).
- **Ops (East Village)** — natural-minded (**Vouette & Sorbée**, **Jean-Marc Dreyer**, **Domaine Valette** Mâcon, **Yvon Métras** Beaujolais, **Christian Tschida** Austria).
- **Lei (Chinatown)** — Annie Shi; natural list to pair with Chinese food (**Salima et Alain Cordeuil** Champ., **Maison Skyaasen** Burgundy, **Clos des Plantes** Loire).
- **The Four Horsemen (Bklyn)**, **Wildair / Contra**, **Borgo** (Lee Campbell; low-intervention FR/PT/ES/IT) — natural-leaning, grower-scale.

### Italian deep-cuts (Friuli / Piedmont lane)
- **Peasant** — Michael Laudenslager; ~150 selections, **all-Italian, deep cuts**.
- ★ **[Red Hook Tavern (Bklyn)](https://www.vinolistnyc.com/restaurant/red-hook-tavern)** — ~408 bottles, $40–$7,425; bistro front, collector depth behind it.
- ★ **[Place des Fêtes (Bklyn)](https://www.vinolistnyc.com/restaurant/place-des-fetes)** — ~143, $60–$600; France-leaning natural wine bar.
- ★ **[Vinegar Hill House (Bklyn)](https://www.vinolistnyc.com/restaurant/vinegar-hill-house)** — ~78; small, focused.

**Top 5 to actually book for wine, his taste:** Terroir (Riesling/grower Champ), Compagnie
(Selosse), Le Veau d'Or / Frenchette (grower-French), Le Bernardin (Agrapart + aged depth),
Eleven Madison Park (verticals / aged classed-growth drink-now).

---

## 2 · Producer tracking recipe — popularity · price · prestige

Vinolist's structure makes it a clean **somm-demand gauge**. Because it aggregates
~65 lists, three derived signals fall out (no scraping needed to *understand* them;
scraping needed to *track* them over time — see `raw/vinolist/`):

| Signal | How to read it on Vinolist | Vault analogue |
|---|---|---|
| **Popularity / prestige** | # of restaurant lists a producer appears on (search the producer → count lists). Appearing on many *grand* lists (EMP, Le Bernardin) = prestige; on many *natural-bar* lists = momentum. | Berserkers `mentions` / `rank` |
| **Price** | min / avg / max bottle price for that producer across lists; track the floor over snapshots | retailer price frontmatter |
| **Momentum** | change in list-count between dated snapshots (new entrant vs. fading) | Berserkers `momentum_score_2023` |

The pipeline that turns this into per-producer `community.vinolist.*` frontmatter +
`_views/` rollups is scaffolded in **`raw/vinolist/`** (data contract + restaurant
registry). Like LPV, the **scraper is the blocker** (403 + egress); ingest is
manual-paste / local-scraper until that's built.

### Seed snapshot v0 — producers spotted across top lists (2026-06, manual, partial)
Not the systematic list-count yet — just what surfaced while researching the rosters
above. Treat as a discovery seed, not a tally.

| Producer | Region | Lane | Spotted at | In vault? |
|---|---|---|---|---|
| Anselme Selosse | Champagne | grower (prestige) | Compagnie | check |
| Agrapart & Fils | Champagne | grower | Le Bernardin | check |
| Suenen | Champagne | grower | Terroir | check |
| Dhondt-Grellet | Champagne | grower | Terroir | check |
| La Rogerie | Champagne | grower (new) | Terroir | check |
| Vouette & Sorbée | Champagne | grower/bio | Ops | check |
| Tarlant | Champagne | grower | Winona's | check |
| Salima et Alain Cordeuil | Champagne | grower (new) | Lei | check |
| Julien Meyer | Alsace | bio/natural | Winona's | check |
| Jean-Marc Dreyer | Alsace | natural | Ops | check |
| Nicolas Joly | Loire (Savennières) | biodynamic founder | Winona's | check |
| Clos des Plantes | Loire (Anjou) | natural | Lei | check |
| Yvon Métras | Beaujolais (Fleurie) | natural icon | Ops | check |
| Domaine Valette | Mâconnais | bio | Ops | check |
| Maison Skyaasen | Burgundy | négoce/natural (new) | Lei | check |
| Christian Tschida | Austria (Burgenland) | natural | Ops | check |

---

## 3 · Discovery — onboarding candidates

The v0 table above is the discovery feed: producers the best NYC somms pour, biased
hard toward Evan's filters (grower Champagne, biodynamic Loire/Alsace, natural
Beaujolais). Next step is the triage many other sources use — cross-reference each
against the vault and onboard the keepers via per-producer LLM passes (verify farming
+ critic coverage; don't bulk-create from a single source). The richest discovery
vein here is **grower Champagne** (Selosse / Agrapart / Suenen / Dhondt-Grellet /
La Rogerie / Vouette & Sorbée / Tarlant / Cordeuil) — exactly the "aged vintage /
late-disgorged / grower" filter.

---

## How to use Vinolist (query cheat-sheet)
- **"Where can I drink an aged Selosse / a Clape Cornas / a Mosel grower tonight?"** → search the producer; it returns every list carrying it, with prices.
- **"Best by-the-bottle value on a grand list"** → open a restaurant page, sort by price; EMP/Chambers have $20–$40 floors hiding under five-figure ceilings.
- **"What's a natural bar pouring right now"** → Ops / Four Horsemen / Place des Fêtes pages = current grower zeitgeist.

## Sources
- [Vinolist NYC](https://vinolistnyc.com/) + indexed restaurant pages (EMP, Chambers, Red Hook Tavern, Place des Fêtes, Vinegar Hill House)
- [Resy — NYC Wine Hit List, Spring 2026](https://blog.resy.com/2026/03/nyc-wine-hit-list/) · [French wine in NY](https://blog.resy.com/2023/01/french-wine-new-york/) · [Le Veau d'Or](https://blog.resy.com/2024/07/le-veau-dor-nyc/)
- [Star Wine List — top wine restaurants NYC 2026](https://starwinelist.com/wine-guide/top-wine-restaurants-in-new-york-city) · [Wine Spectator — top NYC restaurant wine lists](https://www.winespectator.com/articles/new-york-city-top-restaurant-wine-lists) · [Decanter — NY wine bars](https://www.decanter.com/wine-travel/restaurant-and-bar-recommendations/new-york-wine-bars-320462/)
