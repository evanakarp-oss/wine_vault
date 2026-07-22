---
type: view
updated: 2026-07-22
scope: vault_architecture
question: "How should the vault link producers × land × vintage × style × trusted source so multi-hop questions pull from multiple places?"
---

# Linkage Architecture — the vault as a queryable graph (2026-07)

Evan's ask (2026-07-22): *questions that require reasoning across producers, land,
vintages and style should pull from multiple places; wine info is fragmented, so
curate carefully toward the styles I'm drawn to, biased to sources I trust
(carefully-curated importer books).* This is the design for that — the entity
model, the join layer, the two curation judgments (trust + taste), the query
patterns it unlocks, and the ranked backfill. Companion to
[[data_quality_integration_review_2026_07]] (which found the gap) and
[[producer_signals_board_2026_07]] (the first built layer).

## The problem: six disconnected namespaces

A single producer's signal is scattered across `region`/`sub_region`,
`appellations`, `farming`, `importer_us`, `retailers.*`, `community.berserkers.*`,
and the `## Critic Ratings` / `## Cellar` body sections — plus the taste + trust
rules that only lived as prose in CLAUDE.md. Nothing joined them, so every
cross-entity answer re-opened dozens of pages and the reasoning never compounded.
Measured coverage (473 producers) shows *where* the graph is thin:

| Layer | Field | Coverage | State |
|---|---|---:|---|
| Land — commune | `sub_region` | 76% | good |
| Land — **cru / vineyard** | `appellations` | **17%** | **the gap** for cru-level joins |
| Style | `farming` | 39% | partial |
| **Trust — source** | `importer_us` | **27%** | under-filled; names are right |
| Community | `community.berserkers` | 20% | one thread ingested |
| Critic | `## Critic Ratings` | 15% | [[critic_ratings_board_2026_07\|now rolled up]] |
| Ownership | `## Cellar` link | 15% | **broken** (0/294 cellar files link back) |

## The entity model

Producer is the hub; everything else is a dimension it links to.

```
                 ┌── LAND ──────────────┐        ┌── SOURCE / TRUST ───┐
   region ──► sub_region ──► appellation │        │ importer_us         │
   (Burgundy)  (Vosne)     (Les Chaignots)│       │ retailers.{dte,fass,│
                 ▲                        │        │  chambers,raeders}  │
                 │                        ▼        └─────────┬───────────┘
   VINTAGE ◄── cuvée-rows ◄──────────  PRODUCER  ◄───────────┘
   (2019 vs 2021) in ## Critic Ratings,    │
   cellar files, DTE cuvée tables          ├──► STYLE  (farming, tags, grower-vs-house)
                                           ├──► CRITIC (## Critic Ratings → best/│depth)
                                           ├──► COMMUNITY (berserkers rank/momentum)
                                           └──► OWNERSHIP (cellar/*.md)
```

Two dimensions are still weak as *structured* data even though the information
exists in prose: **cru/vineyard** (inside cuvée names) and **vintage** (inside
cuvée rows). Lifting those into structured fields is the main backfill.

## The join layer — `build_signals.py`

One record per producer joining every dimension → `build/producer_signals.json`
(machine copy for `/ask-cellar`) + [[producer_signals_board_2026_07]] (human read
surface). It computes two curated judgments — the encoded version of Evan's taste
and trust — so ranking is a value, not a vibe:

### trust_tier (the "bias toward sources I trust")

Trust in a producer = trust in the book that curated it. Decision table in the
script (`IMPORTER_TIER` / `RETAILER_TRUST`), tunable:

- **Tier 1 (set by Evan, 2026-07-22)** — Down to Earth (Panzer), Chambers/CSW
  (championed), Polaner, David Bowler, Grand Cru, **WK comments**, Neal Rosenthal,
  Skurnik. "WK comments" is a first-class trust signal, not an importer: it's
  William Kelley's Berserkers posts about the producer
  (`retailers.berserkers_kelley.post_count > 0` — 93 producers, e.g. Ramonet ×99,
  Leflaive ×44, Duroché ×15, Clos Rougeard ×14).
- **Tier 2** — Fass, Raeders + broader trusted books: Kermit Lynch, Louis/Dressner,
  Terry Theise, Zev Rovine, Wilson Daniels, Vineyard Brands, Wasserman, Wildman,
  Henderson, BNP, Banville.
- **unresolved** (30%) — no importer + not in a trusted book/signal → invisible
  trust, the #1 backfill target.

Result: **293 Tier-1, 39 Tier-2, 70% resolved.** Tier 1 is broad because CSW and
DTE are large curated books — which is exactly the intended bias. Reorder the
`IMPORTER_TIER` / `RETAILER_TRUST` tables + the WK hook in `build_signals.py` to tune.

### taste_fit (the "styles I'm drawn to")

`core` / `adjacent` / `off` / `skip`, from the CLAUDE.md taste rules as code:
core = grower/terroir Burgundy·Loire·Champagne·German-Riesling·Piedmont·
Beaujolais·Jura·Friuli·N-Rhône + the two accepted Napa-Cab tracks; `skip` =
opulent CA Syrah/Rhône (SQN/Saxum/Law/Next of Kyn); Bordeaux/S-Rhône/generic-Napa/
non-bio-Argentina = `adjacent` pending a flag. Verified against spot cases: SQN→skip,
Bond→core, Marie Courtin/Gonon/J-M Stéphan→core+T1, Lafite→adjacent.

### conviction

`taste_fit + trust_tier + critic + WB-momentum` → the shortlist rank. The
board's lead table ("on-taste × trusted source × available × not owned") is the
buy question resolved once.

## What multi-hop questions this now answers from one place

- *"Northern-Rhône I don't own, from a trusted importer, that's actually available"*
  → filter signals: `region=Rhône & sub∈N-Rhône & trust_tier≤2 & available & !owned`.
- *"Who else works this ground?"* (land join) → group by `sub_region` (commune
  today; `appellations` once backfilled → true cru neighbours).
- *"Highest-conviction grower Champagne to buy"* → `region=Champagne & taste_fit=core
  & trust_tier=1`, then the [[critic_ratings_board_2026_07\|ratings board]] for scores.
- *"Trusted-source producers with no cellar bottle"* → tier-1 table, `owned=—`.

Vintage-level joins (*2019 vs 2021 in a given cru*) still route through the
[[critic_ratings_board_2026_07|ratings board]] + cellar files — structured vintage
is the next layer.

## Backfill roadmap (ranked — each sharpens every future answer)

1. **`importer_us` (27%→).** Highest leverage: it's the trust signal. Backfill
   from the importer rollups + `_at_raeders` xref views already in the vault, and
   from each retailer's known book. Turns 30% of producers from "trust-invisible"
   to rankable.
2. **`appellations` / cru (17%→).** Lift vineyard names out of the cuvée strings
   already sitting in `## Critic Ratings` + DTE cuvée tables into structured
   `appellations`. Unlocks cru-level "producer × land" — the join Evan named first.
3. **Repair link integrity.** ~770 broken `[[wikilink]]` targets = dead graph
   edges (cellar↔producer is 0%). Fix + extend `lint.py` to validate every target
   ([[data_quality_integration_review_2026_07]] rec #2) so it can't regress.
4. **Vintage layer.** A structured cuvée×vintage table (from ratings + cellar +
   DTE `WK` scores) for real vintage reasoning.
5. **Grower-vs-house Champagne flag.** Region=Champagne is too coarse — Dom
   Pérignon and Marie Courtin both read `core` today. A house/grower tag (or lean
   on Theise/Rovine importer signal) sharpens it.

## How `/ask-cellar` uses it

Read order is now: `build/producer_signals.json` (or
[[producer_signals_board_2026_07]] if reading via the GitHub connector) **first**
for any cross-entity question, then drill into the producer / ratings / region
pages it points to, applying `taste_fit` + `trust_tier` to rank. Regenerate with
`python scripts/build_signals.py` after ingests; `--check` gates it in CI.
