---
type: workflow_doc
updated: 2026-07-22
---

# Wine Vault — Workflow

How edits flow through the vault, where to make them, and how to read and
query it. **Git is the single source of truth.** There is no second copy
of the vault anywhere — everything is read directly from the git repo.

> **History:** until 2026-07-22 a `drive_mirror` GitHub Action copied the
> repo to a Google Drive folder on every push, so that the Claude chat app
> and phone browsing could reach the vault. Claude can now read the GitHub
> repo directly (Claude Code on the web + the claude.ai GitHub connector),
> so the mirror became an obsolete, fragile layer — it also failed on every
> push once Google removed service-account storage quota, emailing a failure
> notice each time. Both the mirror and its weekly `drive_audit` were
> retired. Read and query the git repo directly instead (see below).

## TL;DR

| Action | Where to do it |
|---|---|
| Read / study the vault | **Obsidian** pointed at a git clone (renders the wiki + `[[wikilinks]]`) |
| Read a quick page anywhere | GitHub web UI (github.com/evanakarp-oss/wine_vault) |
| Q&A — deep, full-vault | **Claude Code on the web** (this session) — reads the live repo, has `/ask-cellar` |
| Q&A — quick, on phone | **claude.ai in a browser** with the GitHub connector on `wine_vault` |
| Edit / commit | Claude Code (this session), a local git clone, or Working Copy on iOS |
| Drop a scrape / external data | Commit it to `raw/<source>/` in git |

**Anti-pattern**: keeping a second copy of the vault anywhere — Google
Drive, uploaded claude.ai "project files", an Obsidian vault pointed at a
Drive-synced folder. Any of these drifts out of sync with git and recreates
the mess the 2026-05-26 audit had to clean up. One source of truth: the git
repo. Everything reads from it directly.

## Why git is the single source of truth

The 2026-05-26 architecture-failure audit found three parallel vault copies
on Google Drive with content that never made it back to canonical. Git
solves this:

- Single linear history of every change.
- CI runs lint + log validation + index check on every push, so drift is
  caught at write time, not weeks later.
- Reading and querying now point straight at the repo, so there is no copy
  to fall out of date.

## Reading the vault (Obsidian)

The vault is already an Obsidian vault — the config is checked into
`.obsidian/`, and the internal links use Obsidian's `[[slug|Display]]`
convention. To read it beautifully (rendered pages, clickable producer
links, search, graph view):

1. Install **Obsidian** (free) — desktop and/or iPhone.
2. Get a copy of the repo onto the device (a git clone; on iOS use Working
   Copy — see Mobile setup below).
3. In Obsidian: **Open folder as vault** → pick the cloned `wine_vault`
   folder.
4. Start at `wiki/index.md` (the catalog of every page) or
   `wiki/_views/_index.md` (saved analyses). Click through the wikilinks.

Edits made in Obsidian are ordinary file edits — commit them with your git
client (Working Copy on iOS, or `git` on desktop) to make them canonical.

## Asking questions (Claude, connected to git)

No Google Drive, no uploaded copies. Claude reads the repo directly:

- **Deep / full-vault questions** — use **Claude Code on the web**
  (claude.ai/code, this session). It reads the live repo, follows the
  `index.md` → producer/region/view drill-down, and has the `/ask-cellar`
  skill built for exactly this.
- **Quick questions, incl. on a phone** — use **claude.ai in a browser**
  with the **GitHub connector**. One-time: claude.ai → Settings →
  Connectors → GitHub → connect. Then in a chat: **＋ → Add from GitHub →
  `wine_vault`**, and ask. The native Claude mobile *app* has no GitHub
  connector yet, so on a phone use the browser — **Add to Home Screen**
  makes it feel like an app while keeping the connector.

## Mobile setup (one-time)

To read in Obsidian and commit from an iPhone:

1. **Working Copy** on iOS (best git client on iOS by a wide margin).
2. Clone the repo into Working Copy from GitHub.
3. Move the local clone into iCloud Drive (Working Copy → repo settings →
   Move to Files → iCloud Drive).
4. Obsidian Mobile → Open folder as vault → pick the iCloud-synced clone.
5. Obsidian now reads/edits the git working tree directly; commits happen
   in Working Copy (a few taps).

No-app-purchase alternative: just use Claude Code on the web / claude.ai in
the phone browser. Commit + push from this session; reading happens in the
browser.

## What CI enforces

Every push to `main` triggers the `check` workflow
(`.github/workflows/check.yml`):

1. `lint.py` — schema/taxonomy/dedup must be at 0 issues.
2. `build_wiki_index.py --check` — index must match current vault.
3. `build_wiki_log.py --check` — log entries must match `## [date] op | title`.

If any fail, the push is rejected. There are no longer any Drive-related
workflows.
