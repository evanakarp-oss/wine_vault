---
name: email-sweep
description: Weekly sweep of Evan's Gmail for offer emails from the two grower-import retailers he buys from — Fass Selections (lyle@fassselections.com) and Down to Earth / Panzer (robertpanzer@hotmail.com). Records offers in the rolling offers view, folds a "Recent offer" note onto matching producer pages, and flags un-paged on-taste producers for onboarding. Run manually via /email-sweep or on the weekly Routine.
---

# /email-sweep

Keeps the vault current with what Evan's two grower-import retailers are
actually offering, and turns their emails into producer-page context + an
onboarding signal. Runs weekly (Routine) or on demand.

**Preconditions**
1. CWD is the `wine_vault/` repo.
2. The Gmail connector is available (tools `search_threads` / `get_thread`).
   If not, stop and tell Evan the sweep can't run without it.

## The two senders

| Sender | Retailer | Data shape |
|---|---|---|
| `lyle@fassselections.com` | Fass Selections | Producer + cuvée + vintage + price + **Lyle's /10 house score** + tasting blurb. ~4 emails/week. |
| `robertpanzer@hotmail.com` | Down to Earth (Panzer) | Producer allocation offers (mostly Burgundy/Italy), often "LAST CALL". Third-party critic scores when quoted. ~1–3/week. |

## Steps

1. **Pull new mail.** Search each sender since the last run (default window
   8 days — overlap is fine, dedup by date+producer):
   - `from:lyle@fassselections.com newer_than:8d`
   - `from:robertpanzer@hotmail.com newer_than:8d`
   Use `search_threads` for the list; only `get_thread` (FULL_CONTENT) when the
   snippet isn't enough — those newsletter bodies are large, so prefer snippets.

2. **Parse each offer** into: date, producer, wine/cuvée, vintage, price,
   Lyle score (Fass only), one-line blurb. The subject line + snippet usually
   carry all of it.

3. **Record in the rolling offers view.** Append newest-first to the current
   month's `wiki/_views/retailer_email_offers_<YYYY_MM>.md` (create it from the
   2026-07 file's structure when the month rolls over; keep the previous month's
   file as history). One row per offer, in the right sender table.

4. **Fold onto the producer page.** If the producer has a page
   (check `wiki/producers/`, respecting the alias tables in
   `scripts/ingest_fass.py` / `ingest_dte_jsx.py` and stripped prefixes),
   add or refresh a single **`**Recent offer (<date>, <sender>):** …`** line in
   its `## FASS` (Fass) or `## Down to Earth Wines (Panzer)` (DTE) section.
   Keep only the most recent 2–3 offers per page — this is context, not a log.

5. **Flag onboarding candidates.** If the producer has NO page and fits Evan's
   curation taste (CLAUDE.md — grower Champagne, terroir Loire/Burgundy/German
   Riesling/N. Rhône, biodynamic-leaning), add it to the **Onboard queue** at the
   top of the offers view with a one-line rationale. **Do NOT auto-create pages** —
   onboarding is a curated LLM pass (see the DTE/Fass onboarding pattern in
   `wiki/log.md`, 2026-07-22). Skip generic mid-tier silently.

6. **Regenerate + commit.** `python scripts/build_views_index.py`,
   `python scripts/build_wiki_index.py`, append a one-line `wiki/log.md` entry
   (`## [YYYY-MM-DD] sweep | retailer email offers (Fass + DTE)`), run the
   `--check` hooks, then commit and push. If nothing new arrived, do nothing and
   say so — don't create an empty commit.

## Notes

- Fass prices go stale fast (many are last-call) — the offers view is a
  snapshot, not a price source. Don't backfill prices onto producer frontmatter.
- Fass's `WK`-style scoring is Lyle's own palate, not a wine critic; label it
  "Lyle N/10", never as a Wine Advocate / Vinous score.
- The DTE portfolio JSX (`raw/dte/dte_portfolio_2026-*.sd.json`) also carries a
  `WK` dict of Panzer's per-cuvée scores — a separate, richer feed if you want to
  build a scored-offers view.
- First seed + design: `wiki/_views/retailer_email_offers_2026_07.md`.
