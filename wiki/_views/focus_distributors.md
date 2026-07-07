---
type: view
question: "Focus distributors — importers Evan tracks closely and buys from deliberately"
updated: 2026-07-07
---

# Focus Distributors

The **focus distributor** is a curation concept (introduced 2026-07-07): an
importer whose book Evan trusts enough to track closely, mine for discovery, and
buy from deliberately — not just a name that happens to appear on a back label.
A focus distributor's producers are onboarding priorities, and seeing its
importer strip on a shelf is itself a positive signal.

**Mechanism.** Each focus distributor's importer page carries
`focus_distributor: true` in frontmatter (preserved through `build_rollups.py`
regeneration) plus a `focus-distributor` tag. This page is the read surface.

## Current focus distributors

| Distributor | Regions | Why | Page |
|---|---|---|---|
| **Benvenu** (benvenusa.com) | Etna, Friuli, Slovenia (Brda/Vipava), Tuscany, Sardinia, Piedmont | Small book of hand-farmed (<10 ha) micro-producers — terroir-transparent, border-Friuli/Slovenia whites, volcanic Etna, biodynamic Cortona Syrah. "I really like the wines I've had from this portfolio." | [[Benvenu\|Benvenu]] |

## How to add one

1. Ensure the importer page exists under `wiki/importers/` (create it if the
   distributor isn't modeled yet — mirror the Benvenu / Henderson pattern).
2. Add `focus_distributor: true` to its frontmatter and `focus-distributor` to
   its `tags`.
3. Add a row to the table above.
4. Re-run `python scripts/build_views_index.py` (catalogs this page) and
   `python scripts/build_wiki_index.py`.

## Related

- [[Benvenu|Benvenu]] — full 16-producer roster + curated onboarding tiers.
- Contrast with **Henderson Selections** ([[Henderson_Selections|page]]) — also
  a curated, on-taste US book, but not (yet) flagged a focus distributor.
