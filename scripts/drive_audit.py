"""
drive_audit.py — diff the canonical Drive `wine_vault/` against the
local git working tree, emit `build/drive_audit.md`, exit non-zero if
anything is unique to Drive.

Run from CI by `.github/workflows/drive_audit.yml`. Can also run
locally if you have rclone configured with a `gdrive:` remote pointing
at the Drive `wine_vault/` folder.

The Drive listing is obtained via `rclone lsjson gdrive: --recursive`.
The git side is just `git ls-files` (tracked files only — untracked
local junk doesn't count as drift).

Files unique to Drive are real drift signals: someone edited on Drive,
bypassing git, OR a one-off Drive upload happened (Roscioli-style).

Files unique to git are NOT flagged: the mirror is push-only, so git
having more is expected mid-window (between push and mirror sync).
The mirror workflow handles that.

Excludes (must match `.github/workflows/drive_mirror.yml`):
  - .git/, .github/, build/, __pycache__/
  - _drive_sync/, wiki/wiki/, wine_vault_fromdocuments/ (legacy)
  - .DS_Store, *.pyc, Thumbs.db

Usage:
    python scripts/drive_audit.py            # default paths
    python scripts/drive_audit.py --report path/to/output.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
REPORT = VAULT / "build" / "drive_audit.md"

EXCLUDE_PREFIXES = (
    ".git/", ".github/", "build/", "__pycache__/",
    "_drive_sync/", "wiki/wiki/", "wine_vault_fromdocuments/",
)
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}


def is_excluded(path: str) -> bool:
    if path.startswith(EXCLUDE_PREFIXES):
        return True
    if path.endswith(".pyc"):
        return True
    name = path.rsplit("/", 1)[-1]
    return name in EXCLUDE_FILES


def git_tracked_paths() -> set[str]:
    """All paths tracked by git, with forward slashes, exclusions applied."""
    out = subprocess.run(
        ["git", "ls-files"],
        cwd=str(VAULT),
        capture_output=True,
        text=True,
        check=True,
    )
    return {p for p in out.stdout.splitlines() if p and not is_excluded(p)}


def drive_paths() -> set[str]:
    """All file paths in the Drive `gdrive:` remote, recursive."""
    out = subprocess.run(
        ["rclone", "lsjson", "gdrive:", "--recursive", "--files-only", "--no-mimetype"],
        capture_output=True,
        text=True,
        check=True,
    )
    items = json.loads(out.stdout)
    return {it["Path"] for it in items if not is_excluded(it["Path"])}


def render_report(git_set: set[str], drive_set: set[str]) -> str:
    only_drive = sorted(drive_set - git_set)
    only_git = sorted(git_set - drive_set)
    both = git_set & drive_set
    lines = [
        "---",
        "type: drive_audit",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"git_tracked: {len(git_set)}",
        f"drive_files:  {len(drive_set)}",
        f"in_both:      {len(both)}",
        f"drive_only:   {len(only_drive)}",
        f"git_only:     {len(only_git)}",
        "---",
        "",
        "# Drive ↔ git audit",
        "",
        f"- **git tracked files**: {len(git_set):,}",
        f"- **drive files**:       {len(drive_set):,}",
        f"- **in both**:           {len(both):,}",
        "",
    ]
    if only_drive:
        lines += [
            "## ⚠️ Unique to Drive (drift signal)",
            "",
            "These files exist in Drive but not in git. Either someone "
            "edited directly on Drive (Obsidian / web UI / chat upload) "
            "or this is an old artifact that survived a previous mirror.",
            "",
            "**Action**: review each. If real content, copy into the git "
            "repo and commit. If junk, delete from Drive.",
            "",
        ]
        for p in only_drive[:200]:
            lines.append(f"- `{p}`")
        if len(only_drive) > 200:
            lines.append(f"- _… and {len(only_drive) - 200} more_")
        lines.append("")
    else:
        lines += [
            "## ✅ No drift",
            "",
            "Every Drive file is tracked in git. The mirror is the only "
            "source of writes to Drive.",
            "",
        ]
    if only_git:
        lines += [
            "## Pending mirror (informational)",
            "",
            f"{len(only_git)} file(s) tracked in git but not yet in Drive. "
            "This is normal between a `git push` and the next mirror sync "
            "(typically <1 minute). If this is persistently non-zero, the "
            "mirror workflow is failing — check the `drive_mirror` run logs.",
            "",
        ]
        for p in only_git[:30]:
            lines.append(f"- `{p}`")
        if len(only_git) > 30:
            lines.append(f"- _… and {len(only_git) - 30} more_")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, default=REPORT,
                    help="Output report path.")
    args = ap.parse_args()

    git_set = git_tracked_paths()
    drive_set = drive_paths()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(git_set, drive_set), encoding="utf-8")
    only_drive = drive_set - git_set
    print(f"git: {len(git_set):>5}  drive: {len(drive_set):>5}  "
          f"drive-only: {len(only_drive):>5}  report: {args.report}")
    return 1 if only_drive else 0


if __name__ == "__main__":
    sys.exit(main())
