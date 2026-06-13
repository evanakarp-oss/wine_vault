---
type: view
updated: 2026-06-13
question: "Are there wines and producers at Raeders on any of the curated importer lists (Roscioli etc.)?"
source: raw/raeders/master_2026-04-25.csv (3,174 bottles, scraped 2026-04-25) × wiki/importers/*.md
method: normalized producer-name match (accent/prefix stripping) across all 66 importer pages, then manual disambiguation of fuzzy candidates against the Raeders CSV
---

# Raeders × Importer Lists — Producer Overlap (2026-06)

**Short answer: yes — and it's overwhelmingly the Roscioli list.** Raeders'
3,174-bottle inventory contains ~1,544 distinct producers. Cross-referenced
against every importer page in `wiki/importers/`, the meaningful overlap is
with **[[Roscioli_Wine_Club|Roscioli Wine Club]]** — 9 of its 146 Italian
profiles are buyable at Raeders right now. Scattered single-producer hits also
land on Polaner, Dressner/Louis, Skurnik, and Wilson Daniels.

> **Why Roscioli dominates:** it's the only importer page that carries a large
> *external* curated list (156 Italian profiles, most without vault pages). The
> other 65 importer pages are auto-generated rollups of producers *already in
> the vault* — mostly French/German growers that a Long Island retailer like
> Raeders doesn't stock. So the overlap concentrates exactly where the curated
> Italian list meets Raeders' Italian shelf.

## Roscioli Wine Club — buyable at Raeders (9 of 146)

| Roscioli producer | Region | At Raeders | Example bottle | Price |
|---|---|---|---|---:|
| **[[roagna\|Roagna]]** | Langhe · Barbaresco | Roagna | Barbaresco Pajé 2017 | $189.99 |
| **Braida** | Monferrato · Barbera | Braida | Bricco dell'Uccellone Barbera 2020 | $89.99 |
| **Cantina Sobrero** | Castiglione Falletto · Barolo | Sobrero | Ciabot Tanasio Barolo 2016 | $59.99 |
| **Castello dei Rampolla** | Panzano in Chianti | Castello dei Rampolla | Sammarco Toscana 2019 | $109.99 |
| **Lamole di Lamole** | Chianti Classico | Lamole di Lamole | Chianti Classico Maggiolo 2022 | $20.99 |
| **Le Macchiole** | Bolgheri | Le Macchiole | Toscana Paleo Red 1995 | $189.99 |
| **Christof Tiefenbrunner** | Alto Adige · Schiava | Tiefenbrunner | Pinot Grigio | $15.99 |
| **Paitin** | Langhe · Barbaresco | Sorì Paitin | Barbaresco Vecchie Vigne 2000 | $184.99 |
| **Enrico Rizzi** *(probable)* | Langhe · Barbaresco | Rizzi | Barbaresco 2016 | $41.99 |

Notes:
- **Roagna** is the strongest tie-in — it's already in the vault and the cellar
  (2020 Langhe Rosso). Raeders also lists Barolo Rocche di Castiglione 2020
  ($229.99), Barbaresco Pajé Vecchie Viti 2018 ($359.99), and Langhe Rosso 2020
  ($59.99).
- **Paitin** matches on its flagship cru name — Roscioli lists "Paitin", Raeders
  lists the wine as "Sorì Paitin" (same estate, Paitin di Pasquero-Elia).
- **Enrico Rizzi** is flagged *probable*: Roscioli lists "Enrico Rizzi" (Langhe
  Barbaresco); Raeders lists only "Rizzi — Barbaresco 2016". Barbaresco has both
  Enrico Rizzi and the Dellapiana "Rizzi" estate, so the bare "Rizzi" listing is
  ambiguous. Verify before treating as a confirmed match.

## Other importer lists — single hits

| Importer | Producer on list | At Raeders | Example bottle | Price |
|---|---|---|---|---:|
| **[[Polaner\|Polaner]]** | Ceretto | Ceretto | Barolo Bricco Rocche 1996 | $399.99 |
| **[[Polaner\|Polaner]]** | Produttori del Barbaresco | Produttori del Barbaresco | Barbaresco 2021 | $49.99 |
| **[[Dressner\|Dressner]]** / **[[Louis\|Louis]]** | Arianna Occhipinti | Arianna Occhipinti | Il Frappato 2021 | $53.99 |
| **[[Dressner\|Dressner]]** / **[[Louis\|Louis]]** | Domaine des Ardoisières | Maison Des Ardoisieres | Silice Rouge 2024 | $29.99 |
| **[[Skurnik\|Skurnik]]** | Chandon de Briailles | Domaine Chandon De Briailles | Pernand Vergelesses Les Vergelesses | — |
| **[[Wilson_Daniels\|Wilson Daniels]]** | Domaine Leflaive | Domaine Leflaive | Pouilly-Fuissé 2017 | $139.99 |

Notes:
- **Ceretto** at Raeders skews to back-vintage Barolo (Bricco Rocche / Prapò,
  1996–2011, $159–400) plus a cheap Arneis Blangé ($24.99).
- **Domaine Leflaive** has the deepest presence of any of these — Pouilly-Fuissé,
  multiple Puligny crus (Folatières, Pucelles, Clavoillon), Mâcon-Verzé. Watch
  the label: Raeders *also* carries Olivier Leflaive and Valentin Leflaive, which
  are separate négoce/Champagne ventures, **not** the Wilson Daniels Domaine.

## Method & caveats

- Match = normalized producer name (accents stripped, common prefixes like
  *Domaine/Cantina/Castello* removed, lowercased). Confirmed against the Raeders
  CSV bottle-by-bottle; fuzzy token candidates (e.g. shared "jean", "saint",
  "castello") were discarded as false positives.
- This is a **conservative** floor. Name conventions differ between Roscioli's
  Italian profiles and Raeders' titles, so a few real matches could be missed by
  the normalizer. Worth a manual re-check if onboarding Roscioli producers.
- Prices shown are the live Raeders listing; `$0.00` in the source means an
  unpriced/out-of-stock listing (omitted from the example column where possible).
- Raeders snapshot is 2026-04-25; inventory turns over, so treat the bottle-level
  detail as indicative.

## Takeaway for the vault

The Roscioli follow-up (152 missing producer pages, per CLAUDE.md) and the
Raeders candidate triage intersect on these 8–9 Piedmont/Tuscany/Alto-Adige
names. If you onboard Roscioli producers, **Roagna, Le Macchiole, Castello dei
Rampolla, Braida, Cantina Sobrero, Paitin, Lamole di Lamole, and Tiefenbrunner**
are the ones you can actually source locally — good first pages to seed because
the inventory link is real.
