---
type: canonical_ids
updated: 2026-05-26
purpose: |
  Pinned Drive folder/file IDs for wine_vault. Scripts and Claude must
  resolve folders by ID (not by name) to avoid the duplicate-name
  ambiguity that caused the wiki/wiki/ divergence in May 2026.
---

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
wiki/producers/:            1jNoplT8Fir2PHAZU17p1CePdRJtZf-4o
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

## Remaining clutter on Drive (safe to delete, outside canonical tree)

These are gitignored and don't affect the canonical vault. Drive-only
cleanup, do via web UI when convenient. See
`build/drive_duplicates_audit.md` for the full enumeration.

```yaml
# _drive_sync/ graveyards. Pre-migration content, kept around as archive.
wine_vault/_drive_sync/:           1aAl0ic2l7tXBpb1ftwvmX9ovVRnQnBwb
_drive_sync/ (Drive root, dup):    1CtZo6znKy239-zxloRk1su2-XD22VQTp
_drive_sync/wine_wiki_v2/:         1uBIr27zcIqMljdKcKHSgk3KyeCxlCcmP

# Four ~125 KB zip copies of the old wine_wiki_v2 content.
wine_wiki_v2.zip (in vault dsync): 1Jq3pYkMukyiZfc5TKhJlURnQQnzO86k8
wine_wiki_v2.zip (in root dsync):  1Y7c7XgoRqQIiCu3DOBXPP5vEmJCJ9lTD
wine wiki v2.zip (Drive root):     1NrV8ghs3p4WaBIBsYzqs7ufcbRmYo29a
wine_wiki:.zip (Drive root):       1Fvvq2EFGXMyTKgsNNdun9NmmqEyNFewt

# May 10 cleanup-session scaffolding. Historical context, no longer needed.
wine_vault_cleanup_bundle/:        1nM83t_-3SaH2eBGnnOb5dqEZcsi-_aiF
wine_vault_cleanup_bundle.zip:     1-hEdGpaPhbEYRQpssLS1GEhrWCdqFwcE
```

## Cleanup history (already executed — IDs are trashed/superseded)

These IDs are now inaccessible via the Drive MCP ("ineligible for
generative AI"), which is Drive's signal for trashed items. Kept here
for traceability; do not write to them. Audited 2026-05-26.

```yaml
# The wiki/wiki/ parallel branch — merged into canonical 2026-05-10
# per wine_vault_cleanup_bundle/CLEANUP_RUNBOOK.md. 104 producer pages
# received their Berserkers/Kelley body sections via merge_wiki_producers.py.
wiki/wiki/                  (was 1GKlN2KtDVYFtoYG_-BZQZmRoE4XnWpOs) — TRASHED
wiki/wiki/producers/        (was 18X5-67eHq649S_RE2RGFy6oLM8YK-y1a) — TRASHED

# Third copy auto-created from a chat-attached zip upload.
wine_vault_fromdocuments/   (was 1mYgoJfyDF3VrFN_r9i8KVLtcdKHSsn_k) — TRASHED

# Original canonical wiki/producers/ folder — replaced 2026-05-14 by
# `1jNoplT8Fir2PHAZU17p1CePdRJtZf-4o` (likely a re-upload during cleanup).
wiki/producers/             (was 1v1YRi3cxRO2EWjrL5QwVdnaEgAAzmD9v) — SUPERSEDED
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
