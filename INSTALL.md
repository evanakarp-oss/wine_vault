# Berserkers ingest pipeline — install + run

Drop-in for the existing `wine_vault/` Karpathy-style knowledge base. After
this lands, every WB thread you care about flows through one repeatable
pipeline: scrape → parse → compile → rollups.

## What ships

```
wine_vault_wb_pipeline/
├── INSTALL.md                          (this file)
├── CLAUDE_addendum.md                  edits to merge into CLAUDE.md
│
├── scripts/
│   ├── scrape_wb_thread.py             URL → discourse JSON dump
│   ├── parse_wb_thread.py              dump → per-thread tally JSON
│   ├── compile_wb_signals.py           tally JSON → producer page updates
│   └── build_wb_rollups.py             all thread JSONs → rollup views + gap candidates
│
├── raw/berserkers/
│   ├── README.md                       source-layer documentation
│   └── threads/
│       └── top10_in_cellar.json        seed (top 100 by mentions, era splits null)
│
└── wiki/
    ├── _SCHEMA_addendum.md             append to _SCHEMA.md
    ├── _TAXONOMY_addendum.md           append to _TAXONOMY.md
    └── _views/                         (empty — populated by build_wb_rollups.py)
```

## Step 1 — Drop into the vault

Copy each file/directory to the same path under `wine_vault/`:

| Source (this kit)                                         | Destination (vault)                                      |
|---|---|
| `scripts/scrape_wb_thread.py`                              | `wine_vault/scripts/scrape_wb_thread.py`                  |
| `scripts/parse_wb_thread.py`                               | `wine_vault/scripts/parse_wb_thread.py`                   |
| `scripts/compile_wb_signals.py`                            | `wine_vault/scripts/compile_wb_signals.py`                |
| `scripts/build_wb_rollups.py`                              | `wine_vault/scripts/build_wb_rollups.py`                  |
| `raw/berserkers/README.md`                                 | `wine_vault/raw/berserkers/README.md`                     |
| `raw/berserkers/threads/top10_in_cellar.json`              | `wine_vault/raw/berserkers/threads/top10_in_cellar.json`  |

Merge the addenda manually:
- `wiki/_SCHEMA_addendum.md` → append into `wine_vault/wiki/_SCHEMA.md`
- `wiki/_TAXONOMY_addendum.md` → append into `wine_vault/wiki/_TAXONOMY.md`
- `CLAUDE_addendum.md` → small edits to `wine_vault/CLAUDE.md` and
  `wine_vault/_project_instructions.md`

## Step 2 — Smoke-test on the seed

The seed JSON has the top 100 producers by mentions but `null` for era splits
(the spreadsheet only carries totals). That's enough to validate the pipeline
end to end on real producer pages:

```sh
cd wine_vault/

# Dry-run — see what would change
python scripts/compile_wb_signals.py raw/berserkers/threads/top10_in_cellar.json

# Inspect build/wb_signals_report.md to see matched/unmatched/ambiguous

# Apply
python scripts/compile_wb_signals.py raw/berserkers/threads/top10_in_cellar.json --apply

# Build the rollup views
python scripts/build_wb_rollups.py --apply
```

After this, you should have:
- `community.berserkers.threads.top10_in_cellar:` blocks in producer
  frontmatter (rank + total mentions; era fields show `null`).
- `## Berserkers` sections on matched producer pages.
- `wiki/_views/wb_top10_in_cellar_top_100.md` — rank table with vault/cellar
  status.
- `wiki/_views/wb_top10_in_cellar_momentum.md` — surging / new / fading.
  (Will be sparse until era splits are populated, see Step 3.)
- `wiki/_views/wb_in_cellar.md` — cellar overlap.
- `build/wb_gap_candidates.md` — top-100 WB names not in the vault.

Open `build/wb_signals_report.md` first — that's where unmatched producers
show up. Each unmatched name is either an alias gap (add to
`PRODUCER_ALIASES` in `parse_wb_thread.py`) or a genuinely missing vault
page (gap candidate).

## Step 3 — Repopulate era splits with a fresh scrape

The seed only has totals. To get real era splits + momentum scores, scrape
the live thread:

```sh
python scripts/scrape_wb_thread.py \
  https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370 \
  --slug top10_in_cellar
# → raw/berserkers/threads/top10_in_cellar.discourse.json

python scripts/parse_wb_thread.py \
  raw/berserkers/threads/top10_in_cellar.discourse.json \
  --slug top10_in_cellar \
  --title "Top 10 Producers in your cellar?" \
  --thread-url https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370 \
  --merge-with raw/berserkers/threads/top10_in_cellar.json
# → overwrites top10_in_cellar.json with full era splits + ~1,115 producers

python scripts/compile_wb_signals.py raw/berserkers/threads/top10_in_cellar.json --apply
python scripts/build_wb_rollups.py --apply
```

If the scraper hits a paywall or rate limit (Discourse instances vary), the
fallback is a manual paste: dump posts into
`raw/berserkers/threads/top10_in_cellar.raw.md` using the format documented
in `parse_wb_thread.py`'s docstring, and run the parser against that.

## Step 4 — Add a second thread

The whole point of building this generically is that thread #2 is one
command set:

```sh
# 1. scrape
python scripts/scrape_wb_thread.py \
  https://www.wineberserkers.com/t/<some-other-thread>/<id> \
  --slug aged_champagne

# 2. parse
python scripts/parse_wb_thread.py \
  raw/berserkers/threads/aged_champagne.discourse.json \
  --slug aged_champagne \
  --title "Best aged Champagne under $X?" \
  --thread-url <url>

# 3. register in _TAXONOMY.md (one line in the threads table)

# 4. compile + rebuild rollups
python scripts/compile_wb_signals.py raw/berserkers/threads/aged_champagne.json --apply
python scripts/build_wb_rollups.py --apply
```

Producer pages now carry both threads under
`community.berserkers.threads.<slug>`. The `## Berserkers` body section
auto-renders all threads a producer appears in.

## Step 5 — Iterate on aliases

The first compile run will report unmatched producer names. For example, the
seed JSON has `"d'Angerville"` as a raw name; depending on how your vault
slugs are spelled (`d_angerville`? `dangerville`? `domaine_d_angerville`?),
some names will miss. Three responses:

1. **Vault page exists under a different spelling** — add an alias mapping
   in `parse_wb_thread.py` `PRODUCER_ALIASES`, re-run parse + compile.
2. **Vault page exists, parser failed to match** — add an `aliases:` entry
   to the producer's frontmatter (same convention CSW uses).
3. **Genuinely no page** — leave it for `build/wb_gap_candidates.md` review.
   Decide whether to onboard via the standard CSW/DTE/Raeders curation flow
   per `CLAUDE.md`.

## Verification checklist

After Step 2, sanity checks:

- `python scripts/lint.py` should still pass (or only show pre-existing
  issues — the WB pipeline doesn't introduce new schema violations as long
  as `_TAXONOMY.md` was updated in Step 1).
- Open `wiki/producers/willi_schaefer.md` (rank 15, 32 mentions in the
  seed). It should have a `## Berserkers` section and `community.berserkers`
  frontmatter.
- Open `wiki/producers/bedrock.md` (rank 1) — same.
- Open `build/wb_gap_candidates.md` — names like "JJ Prum", "Patricia Green",
  "Hofgut Falkenstein" should appear if they don't have vault pages yet.
  If you expect one of them to be in the vault, check the unmatched section
  of `build/wb_signals_report.md` for the slug candidates the matcher tried,
  and either rename the file or add aliases.

## What this replaces

The previous WB workflow lived in:
- A standalone Google Sheet (`WB_Top10_Cellar_COMPLETE`) — scoreboard only,
  no link to vault state.
- A standalone JSX widget — UI view, not data.
- Spreadsheet/Drive, not the vault.

After this lands:
- The Sheet's data lives in `raw/berserkers/threads/<slug>.json`, version-
  controllable, regeneratable.
- The signals live on the producer pages alongside CSW/DTE/Raeders, so
  `/ask-cellar` and other queries can use them directly.
- Gap analysis happens against actual vault state (vs cellar bottles), not
  in your head.
- Adding a second thread is four commands, not a new spreadsheet + widget
  build.
