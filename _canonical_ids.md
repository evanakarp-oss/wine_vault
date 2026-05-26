---
type: canonical_ids
updated: 2026-05-26
status: legacy_reference
canonical_source_of_truth: this git repository
purpose: |
  Pinned Drive folder/file IDs for wine_vault. As of 2026-05-26 this
  git repository is the canonical source of truth (see CLAUDE.md →
  Architecture-fix history). The IDs below are kept as a historical
  reference and as targets for the Drive-side cleanup checklist below.
  Drive is treated as a read-only mirror; no scripts write to Drive.
---

## Drive cleanup checklist (2026-05-26)

The three Drive folders below are duplicates / stale. Recommended
delete order, safest first:

1. **`_drive_sync/wine_wiki_v2/`** — pre-migration legacy. Safe to delete.
2. **`wine_vault_fromdocuments/`** — 2026-04-24 ZIP-derived snapshot,
   strictly older than the current canonical. Safe to delete.
3. **`wiki/wiki/`** — partial parallel tree inside the canonical
   `wiki/` folder. Before deleting, run:

   ```sh
   python scripts/audit_drive_duplicates.py /path/to/Drive/wine_vault/wiki/wiki
   ```

   The audit reports any producer slugs unique to the Drive copy. If
   the report says "Safe to delete," proceed. Otherwise copy the
   unique pages into `wiki/producers/`, commit, then delete.


# Wine Vault — Canonical Drive IDs

If a Drive search returns two folders with the same name, the one whose ID is
listed below is canonical. The other is a sync artifact and should be flagged
for cleanup, never written to.

## Vault root

```yaml
wine_vault:                 1lqMRm9PiLel19kGC7FAZgd-2cHu2CZBB
```

## Wiki

```yaml
wiki/:                      11pj3GsO9yVhsWzhDEpdAzdakaq0xWKit
wiki/producers/:            1v1YRi3cxRO2EWjrL5QwVdnaEgAAzmD9v
wiki/regions/:              1_5HLIxTUWmrv1muspDgpVNiJitCpo_bw
wiki/importers/:            1OUbur4qTdLEHKNRmjQlH__B8n5Ag9Wct
wiki/retailers/:            18SYgqJ3MtorxXSnpX7SdtQb5ns6b3YUh
wiki/_views/:               1YNOWKYbN3NniLdYVk5QfPONrst6oqOtc
wiki/events/:               1LEzJmCMyF9K4XZnKQKWGGH3bibgB4MVe
```

## Cellar, scripts, build

```yaml
cellar/:                    1pa3QUtI3DwSvru7jB3jB5BbHbC2BbGE9
scripts/:                   1ykP2-vPeWNnKMWoCa-vxSonUqAyVJgy8
build/:                     1qvpx7_8edeocaDzuzlgimxiqrpIep6Wm
```

## Raw source data

```yaml
raw/:                       1V2PXUyasQGW4NJWeDJw9DJDaq9LiXkvs
raw/csw/:                   1kyJvDvah0slAQxM4OVHF6tH1i761GV5N
raw/raeders/:               1ExsuxY7pW7OjiYEyyH07cE8oxKGRl9el
raw/dte/:                   1_qz3nGWcbbTqZi0ugLAM41ai1ACaDo2s
raw/fass/:                  13qqZK18Lpfz5BG4zLgghFD38ANdLwiGV
raw/berserkers/:            1-9fcxh-k9esiKUICnOtWlT9GNLbHw5Gh
raw/argentina_reloaded/:    13sdPZofEj7LJ19AtmQnHu2wwdBC38rAo
```

## Key data files

```yaml
wiki/_SCHEMA.md:            1M6G9s4UYC21nzTM0YtBTDaY2-3y4Xnou
wiki/_TAXONOMY.md:          1SwvCst8GFqlka4qDy_mK7l1QxyMyf6Hd
wiki/_resources.md:         1BxPXP4DGDfnJbglXKgxk9kunxPbWTDQX
wiki/My Cellar.csv:         1AWW-w9itTWl0beC-zDqq_itpykI9jVP_
CLAUDE.md (root):           1oyZrOpxPMhSiITbiASq1YsLVEptbNsVt
README.md (root):           1-GX6IaKQXLUYh3VFAigmX4ugYhRqlz6z
_project_instructions.md:   113EFDgKjMfj84A6m1gbuugecxmoyfJ9R
```

## Known stale / pending-cleanup IDs (do NOT write to these)

```yaml
# Parallel duplicate tree of wiki/ — has the Berserkers/Kelley ingest content,
# but lacks the Argentina ingest. Pending merge via scripts/merge_wiki_producers.py.
wiki/wiki/:                 1GKlN2KtDVYFtoYG_-BZQZmRoE4XnWpOs
wiki/wiki/producers/:       18X5-67eHq649S_RE2RGFy6oLM8YK-y1a

# Third copy of the entire vault (auto-created from a chat-attached zip upload).
# Stale (mostly 2026-04-24). Pending review then deletion.
wine_vault_fromdocuments/:  1mYgoJfyDF3VrFN_r9i8KVLtcdKHSsn_k

# Old vault pre-migration. Lives inside _drive_sync/. Pending deletion.
_drive_sync/wine_wiki_v2/:  1uBIr27zcIqMljdKcKHSgk3KyeCxlCcmP
```

## How to use this file

**Scripts:** load this file at startup, parse the YAML blocks, look up IDs by
key. Refuse to write to any folder ID not listed above (or warn loudly).

**Claude:** at session start, read this file before any Drive write operation.
When a Drive search returns multiple folders with the same name, prefer the ID
listed here. If a write target's parent ID is not in this file, ask the user
before proceeding.

**Humans:** keep this file in sync if you create new top-level folders. Run
`lint.py --check-canonical-ids` (TODO) to verify all IDs still exist and have
the expected names.
