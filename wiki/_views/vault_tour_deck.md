---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    background: #1a1410;
    color: #e8dccc;
    font-family: 'Helvetica Neue', sans-serif;
    padding: 45px 70px;
  }
  h1 { color: #c9a961; font-size: 2em; border-bottom: 2px solid #c9a961; padding-bottom: 0.2em; margin: 0 0 0.5em 0; }
  h2 { color: #c9a961; font-size: 1.4em; }
  h3 { color: #b08968; margin-top: 0.3em; font-size: 1.1em; }
  strong { color: #e8dccc; }
  p, li { color: #e8dccc; }
  table, tbody, thead, tr, td, th {
    background: #1a1410 !important;
    background-color: #1a1410 !important;
  }
  table {
    font-size: 0.8em;
    border-collapse: collapse;
    width: 100%;
    margin-top: 0.3em;
  }
  th, td {
    padding: 7px 14px;
    border: none;
    border-bottom: 1px solid #3a2f28;
    color: #e8dccc;
    text-align: left;
  }
  th {
    color: #c9a961;
    font-weight: bold;
    border-bottom: 2px solid #c9a961;
  }
  ul li { margin: 0.4em 0; }
  blockquote {
    border-left: 3px solid #c9a961;
    color: #b08968;
    font-style: italic;
    padding-left: 1em;
    margin-left: 0;
  }
  section.lead { text-align: center; }
  section.lead h1 { border: none; font-size: 3em; }
  section.lead p { font-size: 1.25em; color: #b08968; }
  .stat-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 25px 55px;
    margin-top: 0.6em;
  }
  .stat { min-width: 240px; }
  .stat .num { font-size: 3.2em; color: #c9a961; font-weight: bold; line-height: 1; }
  .stat .lbl { font-size: 0.85em; color: #b08968; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2em; }
  .stat .num.warn { color: #d9534f; }
  section::after { color: #6b5a48; }
---

<!-- _class: lead -->

# Wine Vault

A markdown-as-database for studying, querying, and planning a cellar.

State of the vault — 2026-05-26

---

# By the numbers

<div class="stat-grid">
<div class="stat"><div class="num">746</div><div class="lbl">wiki pages indexed</div></div>
<div class="stat"><div class="num">378</div><div class="lbl">producers tracked</div></div>
<div class="stat"><div class="num">294</div><div class="lbl">cuvée-vintages in cellar</div></div>
<div class="stat"><div class="num">631</div><div class="lbl">bottles owned</div></div>
<div class="stat"><div class="num">4,797</div><div class="lbl">raw retailer records</div></div>
<div class="stat"><div class="num">57</div><div class="lbl">region rollups</div></div>
</div>

---

# What it's for

### Three jobs the vault does

1. **Study** — browse `wiki/` in Obsidian; producer + region pages teach
2. **Q&A** — `/ask-cellar` (or plain Claude) against the markdown
3. **Cellar planning** — drink-window urgency, gap analysis, owned vs. targeted

> Markdown is the source of truth. Code only lands data and renders views.

---

# The cellar — by region

| Region | Cuvées | Region | Cuvées |
|---|---:|---|---:|
| **California** | 77 | Bordeaux | 8 |
| **Burgundy** | 48 | Oregon | 8 |
| Piedmont | 19 | Rheinhessen | 7 |
| Rhône | 18 | Lombardia | 6 |
| Friuli-Venezia Giulia | 13 | Tuscany | 6 |
| Mosel Saar Ruwer | 11 | Sicily | 6 |

Plus 30+ smaller regions — Champagne, Loire, Jura, Douro, Pfalz, Niederösterreich…

---

# The cellar — by color

<div class="stat-grid">
<div class="stat"><div class="num">198</div><div class="lbl">Red</div></div>
<div class="stat"><div class="num">86</div><div class="lbl">White</div></div>
<div class="stat"><div class="num">7</div><div class="lbl">Rosé</div></div>
<div class="stat"><div class="num">3</div><div class="lbl">Orange</div></div>
</div>

---

# Most-collected producers

| Producer | Cuvées | Producer | Cuvées |
|---|---:|---|---:|
| **Ceritas** | 14 | Beta | 6 |
| Daniel & Julien Barraud | 7 | Goisot | 6 |
| Maison Pierre Brisset | 7 | Santa Cruz Mountain Vineyard | 5 |
| AR.PE.PE. | 6 | de Négoce | 5 |
| Renaissance | 6 | Stein | 5 |

---

# Drink-window urgency

### 631 bottles, bucketed against 2026

<div class="stat-grid">
<div class="stat"><div class="num warn">45</div><div class="lbl">past — drink now</div></div>
<div class="stat"><div class="num">174</div><div class="lbl">in window</div></div>
<div class="stat"><div class="num">33</div><div class="lbl">entering</div></div>
<div class="stat"><div class="num">4</div><div class="lbl">long hold</div></div>
<div class="stat"><div class="num">38</div><div class="lbl">unknown</div></div>
</div>

→ `wiki/_views/drink_window_due.md`

---

# Wiki coverage — producers by region

| Region | Producers | Region | Producers |
|---|---:|---|---:|
| **Burgundy** | 92 | Champagne | 14 |
| **Mendoza** | 62 | Mosel (all) | 14 |
| Rhône | 35 | California | 10 |
| Bordeaux | 24 | Patagonia | 9 |
| Jura | 16 | Loire | 6 |

378 producer pages · 57 region rollups · global coverage skewed Old World

---

# Sources & their roles

| Source | Records | Role |
|---|---:|---|
| **Chambers Street Wines** | 1,623 articles | editorial teacher · drives page creation |
| **Raeders** | 3,174 bottles | inventory & price snapshot |
| **Cellar** (CT export) | 294 / 631 | what's owned |
| Berserkers | wired | community pulse, momentum signals |
| Vinous, Wine Advocate (Kelley) | *pending* | critic depth — Web Clipper |

---

# Importers & retailers tracked

### Importers — 9
Dressner · Kermit Lynch · Polaner · Skurnik · Theise · Kysela · Neal Rosenthal · Louis · Wilson Daniels

### Retailers — 4
Chambers Street Wines (NYC) · Down to Earth Wines / Panzer (NYC) · Raeder's · FASS Selections

---

# Live analytical views

Three living markdown views regenerated from vault state:

- **`drink_window_due.md`** — 45 past, 174 now, 33 entering
- **`gap_csw_championed.md`** — **143 producers** with CSW dedicated articles you don't own
- **`gap_raeders_aged_value.md`** — **126 bottles** at Raeders fitting curated taste, not owned

> New analyses get filed here — they don't disappear into chat.

---

# Gap — CSW champions you don't own

| Producer | Region | ★ articles |
|---|---|---:|
| Domaine Baudry | Chinon | 20 |
| Pierre Gonon | Saint-Joseph | 9 |
| Stéphane Guion | Bourgueil | 9 |
| Produttori del Barbaresco | Piedmont | 9 |
| Weiser-Künstler | Mosel | 6 |
| Brovia | Barolo | 6 |
| Hofgut Falkenstein | Saar | 6 |
| Willi Schaefer | Mosel | 5 |

143 producers total — sorted by editorial conviction

---

# Gap — Raeders aged & curated, not owned

| Bottle | Vintage | Price |
|---|---:|---:|
| Château Lafite Rothschild Pauillac | 2018 | — |
| Château Smith-Haut-Lafitte | 2015 | $199.99 |
| Château Calon-Ségur (Saint-Estèphe) | 1995 | $199.99 |
| Biondi-Santi Brunello Riserva | 2016 | $899.99 |
| Dal Forno Romano Amarone | 2009 | $499.99 |
| Ceretto Barolo Bricco Rocche | 1997 | $399.99 |

126 bottles total — aged ≤2018 or WK-flagged / grower champagne

---

# Pipeline

### Three workflows against the vault

- **Ingest** — drop source in `raw/` → discuss → write producer pages → propagate to rollups → reindex → log
- **Query** — read `wiki/index.md` first → drill into producer / region pages → apply taste filters → file the answer back as a view
- **Lint** — `scripts/lint.py` (schema, taxonomy, dedup) · CI runs index + log validation

---

# Open follow-ups

- `/ask-cellar` skill points at OLD Drive `wine_wiki/` — needs repoint
- Vinous + Wine Advocate (Kelley) ingest not yet wired
- 60 lint issues outstanding (taxonomy, empty regions, surname collisions)
- 387 unselected Raeders new-candidate producers parked in `raw/`
- Widget rewire: `dte_wines_1.jsx` still reads hardcoded arrays
- **Mobile access** — Obsidian via iCloud OR claude.ai Project + Drive connector

---

<!-- _class: lead -->

# How to use it

**Read** `wiki/index.md` first → drill in via wikilinks
**Ask** any question to Claude with the vault loaded
**File** worthwhile answers back into `wiki/_views/`

The vault grows by use.
