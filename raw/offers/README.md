---
type: source_readme
source: offers
updated: 2026-05-25
---

# Retailer email offers — ingest workflow

Weekly roundup of inbound offer emails from the retailers Evan follows, with
producer mentions cross-referenced against `wiki/producers/`, `cellar/`, and
the Berserkers community signals. Output lands in
`wiki/_views/offers_<YYYY-MM-DD>.md`.

## Retailers tracked

| Slug | Sender(s) | Cadence |
|---|---|---|
| `chambers` | `office@chambersstwines.com` | ~daily |
| `flatiron` | `offers@flatiron-wines.com`, `<rep>@flatiron-wines.com` (Jeff Patten, John Truax, Dan Weber, …) | ~daily |
| `leon` | `info@leonandsonwine.com` | ~2–3/week |
| `rsquared` | `info@rsquaredselections.com` | weekly (Tue) |
| `fass` | `lyle@fassselections.com` | ~2–3/week (bonus — already wired into wiki) |

## Directory layout

```
raw/offers/
  README.md                   # this file
  <YYYY-MM-DD>/               # roundup window (date = run day, covering past 7 days)
    <retailer>_<thread_id>.md # one file per email
```

Each `<retailer>_<thread_id>.md` has frontmatter + a short body excerpt.

```yaml
---
type: offer
retailer: chambers              # one of the slugs above
sender: office@chambersstwines.com
date: 2026-05-23                # date of the email
gmail_thread_id: 19e557a0fd3a1c85
subject: "An Array of New Arrivals From Spain and Portugal..."
landing_page_url: ""            # "View the Wines" target — recorded even if unfetched
landing_page_fetched: false     # true if producer list below came from the live page
producers_in_vault: []          # slugs that match wiki/producers/<slug>.md
producers_not_in_vault: []      # raw producer names that don't (yet) have a page
themes: [spain, portugal]       # free-form tags
kind: feature                   # feature | meta | flash_sale | private_collection | new_arrivals | auction
---

One-paragraph excerpt or summary of the offer body. Producers mentioned
inline so the page is greppable.
```

## Workflow (weekly)

1. **Capture** — In a Claude Code session, search Gmail for the past 7 days
   from each retailer's sender (via the Gmail MCP). For each email, fetch
   the full thread (`get_thread` with `FULL_CONTENT`) and read the
   `plaintextBody` field — this is where the producer detail usually lives
   (e.g. Flatiron's Northern Rhône offer named Marcel Juge / Jamet / Levet
   in the prose; Leon's Muscadet auction listed every lot inline). Write a
   raw offer file with subject, body excerpt, landing-page URL, and the
   LLM-extracted `producers_in_vault` + `producers_not_in_vault` lists.
   This is the LLM-judgment step: map "Bruno Clair" → `bruno_clair` (slug
   exists) or note it as `not_in_vault`.

   **Network caveat.** This vault's remote execution container blocks
   outbound HTTP to retailer hostnames (chambersstwines.com,
   nyc.flatiron-wines.com, etc.) — landing pages cannot be fetched
   directly. Record the URL in `landing_page_url` with
   `landing_page_fetched: false` so the output view surfaces a ⚠︎ marker
   and the user can open it manually. If the container's egress policy is
   relaxed, try the Shopify JSON endpoint
   (`/collections/<slug>/products.json?limit=250`) for a complete product
   list.

2. **Overlay** — Run `python scripts/compile_offers_roundup.py
   --date 2026-05-25`. The script:
     - Builds a `{slug → producer-page metadata}` index from
       `wiki/producers/*.md`.
     - Builds a `{producer_slug → cellar entries}` index from `cellar/*.md`.
     - For every `producers_in_vault` slug in this week's offers, looks
       up: CSW championed flag, cellar holdings (vintages + count),
       Berserkers rank + momentum.
     - Writes `wiki/_views/offers_<YYYY-MM-DD>.md` grouped by retailer.

3. **Log** — Append a line to `wiki/log.md`:
   `## [YYYY-MM-DD] offers | weekly roundup (<N> emails, <M> vault hits)`

4. **Review** — Read the view. Surface candidates to buy. Note new
   producers worth a page (`producers_not_in_vault` with multiple
   retailer hits over time).

## Anti-patterns

- Don't auto-create producer pages from a single offer mention — same
  rule as Raeders ingest. Curate.
- Don't hand-edit `wiki/_views/offers_*.md`. Regenerate.
- Don't fetch full HTML bodies into the raw file — a short excerpt is
  enough. Producer extraction happens in-session.
