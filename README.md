---
type: vault_readme
updated: 2026-04-21
---

# Wine Vault

Karpathy-style LLM knowledge base for wine collecting. The markdown here is the source of truth; everything else is either source material (`raw/`) or a derived artifact (`build/`).

## Directory map

```
wine_vault/
├── raw/                        # source documents — never hand-edited wiki content
│   ├── csw/                    # Chambers Street blog posts, email offers
│   ├── dte/                    # Down to Earth (Panzer) offer emails
│   ├── raeders/                # Raeder's xlsx + emails
│   └── fass/                   # FASS xlsx + emails
│
├── wiki/                       # compiled knowledge base — LLM-maintained
│   ├── _SCHEMA.md              # frontmatter schema (read first)
│   ├── _TAXONOMY.md            # allowed enum values
│   ├── producers/              # one .md per producer
│   ├── regions/                # auto-generated per-region rollups
│   ├── importers/              # importer profiles
│   └── retailers/              # retailer profiles
│
├── cellar/                     # my actual bottles — one .md per cuvée-vintage
│
├── scripts/                    # Python tools (migration, compile, lint, build)
│   ├── migrate_prose_to_yaml.py # one-shot: convert old prose format to YAML frontmatter
│   ├── ingest_dte_jsx.py       # parse dte_wines_1.jsx, add DTE sections to producer .md
│   ├── ingest_raeders.py       # parse raeders*.xlsx → add Raeder's sections
│   ├── ingest_fass.py          # parse fass*.xlsx → add FASS sections
│   ├── lint.py                 # schema + taxonomy + broken-backlink checks
│   ├── build_rollups.py        # regenerate wiki/regions/*, wiki/importers/*
│   └── build_widget_json.py    # emit build/widget_data.json for the React widget
│
└── build/                      # derived outputs — regenerable, never hand-edit
    └── widget_data.json
```

## The loop

1. **Ingest** — drop new source material into `raw/<retailer>/`. Anything: HTML dumps, PDFs, pasted emails, Excel files.
2. **Compile** — run Claude (or a targeted `scripts/ingest_*.py`) to update `wiki/producers/*.md` from new raw content.
3. **Lint** — `python scripts/lint.py` flags schema violations, taxonomy drift, broken backlinks, likely errors (e.g. a producer's country disagreeing with CSW's tagging).
4. **Build** — `python scripts/build_rollups.py && python scripts/build_widget_json.py`.
5. **View** — open in Obsidian (`.obsidian/` config checked in), or load the widget which reads `build/widget_data.json`.

The widget is ONE output. Other valid outputs: a Marp slide deck of "2026 Q2 cellaring candidates", a matplotlib chart of retailer overlap by region, a Q&A answer that files itself back into `wiki/notes/`.

## Where to edit (git is canonical)

See `WORKFLOW.md` for the full edit-and-sync rules. The short version: git is the single source of truth. Edit in git (Claude Code, local clone, or Working Copy iOS). Read it in Obsidian (config checked in under `.obsidian/`) or on the GitHub web UI. Ask questions by pointing Claude at the repo — Claude Code on the web reads it live, or connect the claude.ai GitHub connector. There is no second copy anywhere; the old Google Drive mirror was retired 2026-07-22.
