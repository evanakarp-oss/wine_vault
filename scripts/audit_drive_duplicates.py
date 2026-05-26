"""
audit_drive_duplicates.py — diff producer slug sets between the canonical
git vault and a Drive-mounted copy of `wiki/wiki/`.

Run before deleting `wiki/wiki/` from Drive to confirm nothing unique is
hiding there. Reports producer files present in the Drive copy but not
in the git canonical wiki/producers/, so you can either:
  - copy them into the canonical vault first, OR
  - confirm they're legitimately obsolete and proceed with the delete.

The script does NOT modify anything. Output is `build/drive_dup_audit.md`.

Usage (from anywhere with the git repo cloned):
    # Mount Drive locally (rclone, Drive for desktop, manual download).
    # Pass the path to the Drive copy of `wiki/wiki/`:
    python scripts/audit_drive_duplicates.py /path/to/Drive/wiki/wiki

Or, if the Drive copy is rooted elsewhere:
    python scripts/audit_drive_duplicates.py /path/to/Drive/wine_vault_fromdocuments
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CANONICAL_PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "drive_dup_audit.md"

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def slug_set(producers_dir: Path) -> set[str]:
    return {p.stem for p in producers_dir.glob("*.md")
            if not p.stem.startswith("_")}


def name_for(p: Path) -> str:
    text = p.read_text(encoding="utf-8", errors="replace")
    m = FM_RE.match(text)
    if not m:
        return ""
    fm = m.group(1)
    nm = re.search(r'^name:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return nm.group(1).strip() if nm else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("drive_root", type=Path,
                    help="Path to the Drive duplicate vault root "
                         "(e.g. .../Drive/wine_vault/wiki/wiki).")
    args = ap.parse_args()

    if not args.drive_root.is_dir():
        sys.exit(f"ERROR: {args.drive_root} is not a directory.")

    # Locate the producers/ subdir inside the Drive root
    drive_producers = args.drive_root / "producers"
    if not drive_producers.is_dir():
        drive_producers = args.drive_root / "wiki" / "producers"
    if not drive_producers.is_dir():
        sys.exit(f"ERROR: no producers/ subdirectory under {args.drive_root}")

    canon = slug_set(CANONICAL_PRODUCERS)
    drive = slug_set(drive_producers)

    only_in_drive = sorted(drive - canon)
    only_in_canon = sorted(canon - drive)
    in_both = canon & drive

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "type: drive_dup_audit",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"canonical_root: {CANONICAL_PRODUCERS}",
        f"drive_root: {drive_producers}",
        f"canonical_count: {len(canon)}",
        f"drive_count: {len(drive)}",
        f"only_in_drive: {len(only_in_drive)}",
        f"only_in_canonical: {len(only_in_canon)}",
        f"in_both: {len(in_both)}",
        "---",
        "",
        "# Drive duplicate audit",
        "",
        f"**Canonical**: `{CANONICAL_PRODUCERS}` — {len(canon)} producers",
        f"**Drive**:     `{drive_producers}` — {len(drive)} producers",
        f"**In both**:   {len(in_both)}",
        "",
    ]

    if only_in_drive:
        lines += [
            "## ⚠️ Only in Drive copy (would be lost on delete)",
            "",
            "Each of these is a producer page that lives in the Drive duplicate but not "
            "in the git canonical vault. Before deleting the Drive copy, either:",
            "1. Copy the .md into `wiki/producers/` and commit, OR",
            "2. Confirm the producer is obsolete / stale and accept the delete.",
            "",
            "| Slug | Name (from frontmatter) |",
            "|---|---|",
        ]
        for slug in only_in_drive:
            name = name_for(drive_producers / f"{slug}.md")
            lines.append(f"| `{slug}` | {name or '_(no name)_'} |")
        lines.append("")
    else:
        lines += [
            "## ✅ No producers unique to Drive copy",
            "",
            "Every producer slug in the Drive copy already exists in the git canonical "
            "vault. **Safe to delete the Drive copy.**",
            "",
        ]

    if only_in_canon:
        lines += [
            f"## Only in canonical (new since Drive copy diverged) — {len(only_in_canon)}",
            "",
            "Informational: these producers exist in git but not in the Drive copy "
            "(expected — Drive copy is stale).",
            "",
        ]
        for slug in only_in_canon[:50]:
            lines.append(f"- `{slug}`")
        if len(only_in_canon) > 50:
            lines.append(f"- _… and {len(only_in_canon) - 50} more_")
        lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nCanonical: {len(canon)} producers")
    print(f"Drive:     {len(drive)} producers")
    print(f"In both:         {len(in_both)}")
    print(f"Only in Drive:   {len(only_in_drive)}")
    print(f"Only in canon:   {len(only_in_canon)}")
    print(f"Report:          {REPORT}")
    if only_in_drive:
        print(f"\n⚠️  {len(only_in_drive)} producer(s) unique to Drive — review before delete.")
        return 1
    print("\n✅ Safe to delete the Drive copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
