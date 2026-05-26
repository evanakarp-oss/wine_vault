---
type: workflow_doc
updated: 2026-05-26
---

# Wine Vault — Workflow

How edits flow through the vault, where to make them, and what auto-syncs
where. **Git is the single source of truth.** Drive is a read-only
mirror auto-updated on every push.

## TL;DR

| Action | Where to do it |
|---|---|
| Read on phone (Obsidian) | iCloud-synced git clone (via Working Copy iOS) |
| Read on phone (just browsing) | Google Drive mirror — open `wine_vault/` in the Drive app |
| Q&A on phone | claude.ai Project with the Drive connector |
| Edit / commit on phone | Claude Code on web/mobile (this session) |
| Edit on desktop (Obsidian) | iCloud-synced git clone |
| Edit on desktop (anything else) | Local git clone, push when done |
| Drop a scrape / external data | Commit to `raw/<source>/` in git, never upload to Drive |

**Anti-pattern**: editing files directly in Drive web UI, in Obsidian
pointed at a Drive-synced folder, or by drag-uploading to Drive from
claude.ai chat. Any of these creates the drift we just spent two days
cleaning up.

## Why git is canonical

The 2026-05-26 architecture-failure audit found three parallel vault
copies on Drive (`wiki/wiki/`, `wine_vault_fromdocuments/`,
`_drive_sync/wine_wiki_v2/`) with content that never made it back to
canonical. The Roscioli scrape (2026-05-19) added 7 more orphan files.
None of this was visible to git, the index, the lint, or any other CI
check.

Git solves this:
- Single linear history of every change
- CI runs lint + log validation + index check on every push — drift
  caught at write time, not weeks later
- The `drive_mirror` workflow pushes git → Drive every minute or so,
  so Drive is always fresh
- The `drive_audit` workflow runs weekly and opens an issue if anything
  on Drive isn't in git

## The two workflows

### `drive_mirror.yml`

Triggered on every push to `main` (or manual dispatch). Uses `rclone
sync` with the service-account credentials to overwrite the Drive
`wine_vault/` folder with the current repo. Excludes `.git/`,
`.github/`, `build/`, legacy folders.

Latency: usually 30–90 seconds after push.

To dry-run: Actions tab → drive_mirror → Run workflow → check
"Dry-run". The workflow runs but doesn't write to Drive.

### `drive_audit.yml`

Runs weekly (Sundays 18:00 UTC) and on manual dispatch. Lists Drive
files via `rclone lsjson`, diffs against `git ls-files`, opens an
issue if anything is unique to Drive.

The report lives at `build/drive_audit.md` and is uploaded as a
workflow artifact (30-day retention).

## One-time setup: Google service account

Both workflows need a Google service account with Drive API access.
Five-minute setup:

1. Go to https://console.cloud.google.com → create a new project
   (or pick an existing one). Note the project ID.

2. Enable the Google Drive API for the project:
   https://console.cloud.google.com/apis/library/drive.googleapis.com

3. Create a service account:
   - IAM & Admin → Service Accounts → Create service account
   - Name: `wine-vault-mirror`
   - Skip role grants (Drive permissions are folder-scoped, not
     project-scoped)
   - Click Done

4. Download the JSON key:
   - Open the service account → Keys tab → Add key → Create new key
   - Type: JSON → Create
   - Save the downloaded file

5. Share the Drive folder with the service account:
   - Open https://drive.google.com/drive/folders/1lqMRm9PiLel19kGC7FAZgd-2cHu2CZBB
   - Click Share
   - Paste the service account email (looks like
     `wine-vault-mirror@<project>.iam.gserviceaccount.com`)
   - Set role: **Editor** (the mirror needs write access)
   - Click Send (uncheck "Notify people")

6. Add the JSON as a GitHub repo secret:
   - GitHub → repo Settings → Secrets and variables → Actions → New
     repository secret
   - Name: `GDRIVE_SERVICE_ACCOUNT_JSON`
   - Value: paste the entire JSON file contents (one big blob)
   - Click Add

7. Test:
   - Actions tab → drive_mirror → Run workflow → check "Dry-run" → Run
   - Should complete green. If it fails, the log shows what's wrong
     (usually a missing share or the wrong folder ID).

After this, every push to `main` mirrors automatically.

## Mobile setup (one-time)

To edit on iPhone, you need a git client. The easiest stack:

1. **Working Copy** on iOS (paid app, $20-ish). Best git client on iOS
   by a wide margin.
2. Clone the repo into Working Copy from GitHub.
3. Move the local clone into iCloud Drive (Working Copy → repo
   settings → Move to Files → iCloud Drive).
4. Obsidian Mobile → Open folder as vault → pick the iCloud-synced
   clone.
5. Now Obsidian on iPhone reads/edits the git working tree directly.
   Commits happen via Working Copy (a few taps).

Alternative (no app purchases): just use Claude Code on the web/mobile.
You're already there. Commit + push from this session and the mirror
takes care of Drive within ~1 minute.

## The audit script (local)

If you're at a desktop and want to check drift right now without
waiting for the weekly cron:

```sh
# Configure rclone once (uses your personal Google login, not the
# service account):
rclone config
# → New remote → name: gdrive → type: drive → leave most defaults
# → scope: drive.readonly → root_folder_id: 1lqMRm9PiLel19kGC7FAZgd-2cHu2CZBB
# → auto-config in browser → done

# Then any time:
python scripts/drive_audit.py
# → exit 0 if clean, 1 if drift; report at build/drive_audit.md
```

## What CI now enforces

Every push to `main` triggers four checks (in `.github/workflows/check.yml`)
plus the mirror:

1. `lint.py` — schema/taxonomy/dedup must be at 0 issues
2. `build_wiki_index.py --check` — index must match current vault
3. `build_wiki_log.py --check` — log entries must match `## [date] op | title`
4. `drive_mirror` — push to Drive (separate workflow, not part of check)

Weekly:

5. `drive_audit` — flag anything on Drive that isn't in git

If any of 1-3 fail, the push is rejected (the merge to main blocks).
If 4 fails, Drive lags but git is still canonical and consistent. If
5 finds drift, an issue is opened automatically.
