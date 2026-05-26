# Vinous clippings — ingest layer

Drop one `.md` file per Vinous article here. Use the Obsidian Web
Clipper extension on the live page: it produces markdown with
frontmatter that the compile pass can read.

## Filename convention

`<YYYY-MM-DD>__<producer-slug>__<short-title>.md`

Examples:

- `2026-03-15__keller__weingut-keller-and-the-grapes-of-rheinhessen.md`
- `2026-02-08__chateau-pichon-baron__bordeaux-2022-en-primeur.md`

Producer slug must match the page stem under `wiki/producers/`
(lowercase ASCII, underscores). If the producer doesn't have a wiki
page yet, write the clipping anyway and let the compile pass surface
it as a gap candidate.

## Required frontmatter

The Web Clipper writes the basics; add `producer_slug` by hand if not
captured:

```yaml
---
type: vinous_clipping
source: vinous
producer_slug: keller
critic: "Antonio Galloni"            # optional, varies by article
url: "https://vinous.com/articles/..."
published: 2026-03-15
clipped: 2026-05-26
---
```

## How it lands

`scripts/compile_clippings.py vinous --apply` reads every clipping,
extracts critic, score, vintage, drinking window, and a 2-sentence
excerpt; writes a `## Vinous Reviews` section on the matched producer
page. Schema documented in `wiki/_SCHEMA.md`. Unmatched clippings list
in `build/clippings_report.md` for review.

## What this replaces

Was previously a "TODO: ingest Vinous" item in CLAUDE.md with no
plumbing. Now: drop a clipping, run the compile, the producer page
updates with the critic signal alongside CSW and Berserkers. The
clipping itself stays in this folder as the source of truth — never
deleted, never hand-edited.
