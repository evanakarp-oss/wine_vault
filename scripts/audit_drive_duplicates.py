#!/usr/bin/env python3
"""
audit_drive_duplicates.py — diff a stale Drive `wiki/wiki/` tree against the
canonical local `wiki/`, so we know what's safe to delete and what still needs
to be merged back.

Background (see _canonical_ids.md):
    The stale Drive folder `wiki/wiki/` (ID 1GKlN2KtDVYFtoYG_-BZQZmRoE4XnWpOs)
    is a parallel duplicate of `wiki/`. It has Berserkers/Kelley ingest content
    that never made it to the canonical tree, but lacks the Argentina ingest.
    Pending cleanup. Before deleting we need to know:
      1. Files only in the stale tree (would be lost).
      2. Files in both but with divergent content (need merge).
      3. Files identical in both (safe to delete from stale).

The script walks both trees, hashes every file, and writes a markdown report
to `build/drive_duplicates_audit.md` (or `--output`). Idempotent.

Usage:
    python scripts/audit_drive_duplicates.py /path/to/Drive/wine_vault/wiki/wiki
    python scripts/audit_drive_duplicates.py /path/to/stale --local-wiki wiki
    python scripts/audit_drive_duplicates.py /path/to/stale --output report.md
    python scripts/audit_drive_duplicates.py /path/to/stale --quiet

Exit codes:
    0 — report written
    1 — input path invalid
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SKIP_NAMES = {".DS_Store", "Thumbs.db", ".obsidian"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class FileEntry:
    rel: Path
    size: int
    mtime: float
    sha: str
    lines: int


def walk_tree(root: Path) -> dict[Path, FileEntry]:
    """Return {relative_path: FileEntry} for every regular file under root."""
    out: dict[Path, FileEntry] = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name in SKIP_NAMES or p.suffix in SKIP_SUFFIXES:
            continue
        # Skip anything inside a SKIP_NAMES directory.
        if any(part in SKIP_NAMES for part in p.relative_to(root).parts[:-1]):
            continue
        try:
            data = p.read_bytes()
        except OSError as e:
            print(f"WARN: could not read {p}: {e}", file=sys.stderr)
            continue
        sha = hashlib.sha256(data).hexdigest()
        lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        st = p.stat()
        out[p.relative_to(root)] = FileEntry(
            rel=p.relative_to(root),
            size=st.st_size,
            mtime=st.st_mtime,
            sha=sha,
            lines=lines,
        )
    return out


def fmt_size(n: int) -> str:
    for unit in ("B", "K", "M"):
        if n < 1024:
            return f"{n}{unit}"
        n //= 1024
    return f"{n}G"


def fmt_mtime(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def write_report(
    stale_root: Path,
    local_root: Path,
    stale: dict[Path, FileEntry],
    local: dict[Path, FileEntry],
    out_path: Path,
) -> None:
    stale_keys = set(stale)
    local_keys = set(local)

    only_stale = sorted(stale_keys - local_keys)
    only_local = sorted(local_keys - stale_keys)
    in_both = sorted(stale_keys & local_keys)

    identical = [k for k in in_both if stale[k].sha == local[k].sha]
    differing = [k for k in in_both if stale[k].sha != local[k].sha]

    lines: list[str] = []
    lines.append("# Drive duplicates audit — stale `wiki/wiki/` vs canonical `wiki/`")
    lines.append("")
    lines.append(f"- Stale tree:      `{stale_root}`")
    lines.append(f"- Canonical tree:  `{local_root}`")
    lines.append(f"- Generated:       {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Bucket | Count |")
    lines.append("|---|---:|")
    lines.append(f"| Files only in stale (would be lost) | {len(only_stale)} |")
    lines.append(f"| Files only in canonical | {len(only_local)} |")
    lines.append(f"| Files in both, identical (safe to drop from stale) | {len(identical)} |")
    lines.append(f"| Files in both, **differing** (need merge review) | {len(differing)} |")
    lines.append(f"| Total in stale | {len(stale)} |")
    lines.append(f"| Total in canonical | {len(local)} |")
    lines.append("")

    lines.append("## Files only in stale (would be lost on cleanup)")
    lines.append("")
    if not only_stale:
        lines.append("_None — nothing unique in the stale tree._")
    else:
        lines.append("| Path | Size | Lines | Mtime |")
        lines.append("|---|---:|---:|---|")
        for rel in only_stale:
            e = stale[rel]
            lines.append(f"| `{rel}` | {fmt_size(e.size)} | {e.lines} | {fmt_mtime(e.mtime)} |")
    lines.append("")

    lines.append("## Files in both but differing (need merge review)")
    lines.append("")
    lines.append("`Δsize` is stale minus canonical. Positive = stale has more bytes")
    lines.append("(often the Berserkers/Kelley ingest content not yet merged back).")
    lines.append("")
    if not differing:
        lines.append("_None — every shared file matches byte-for-byte._")
    else:
        # Sort by absolute byte delta desc so the biggest divergences float up.
        differing_sorted = sorted(
            differing,
            key=lambda r: abs(stale[r].size - local[r].size),
            reverse=True,
        )
        lines.append("| Path | Stale size | Canon size | Δsize | Stale mtime | Canon mtime |")
        lines.append("|---|---:|---:|---:|---|---|")
        for rel in differing_sorted:
            s, c = stale[rel], local[rel]
            delta = s.size - c.size
            sign = "+" if delta > 0 else ""
            lines.append(
                f"| `{rel}` | {fmt_size(s.size)} | {fmt_size(c.size)} | "
                f"{sign}{delta} | {fmt_mtime(s.mtime)} | {fmt_mtime(c.mtime)} |"
            )
    lines.append("")

    lines.append("## Files only in canonical (expected — e.g. Argentina ingest)")
    lines.append("")
    lines.append(f"_{len(only_local)} files — list elided unless `--verbose`._")
    lines.append("")

    lines.append("## Next steps")
    lines.append("")
    lines.append("1. For each row in **only in stale**: decide port-or-drop. If port,")
    lines.append("   copy into the matching canonical location and re-run this audit.")
    lines.append("2. For each row in **differing**: diff the two files. If stale has")
    lines.append("   net-new content (positive Δsize, newer mtime), merge into canonical")
    lines.append("   via `scripts/merge_wiki_producers.py` (TODO) or a hand pass.")
    lines.append("3. Once both top tables are empty, the stale Drive folder")
    lines.append("   `wiki/wiki/` (ID `1GKlN2KtDVYFtoYG_-BZQZmRoE4XnWpOs`) is safe")
    lines.append("   to delete. Remove its row from `_canonical_ids.md`.")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "stale_path",
        type=Path,
        help="Path to the stale Drive `wiki/wiki/` folder (mounted locally).",
    )
    ap.add_argument(
        "--local-wiki",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "wiki",
        help="Path to the canonical local wiki (default: <repo>/wiki).",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "build" / "drive_duplicates_audit.md",
        help="Where to write the report (default: build/drive_duplicates_audit.md).",
    )
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    stale_root: Path = args.stale_path
    local_root: Path = args.local_wiki

    if not stale_root.is_dir():
        print(f"ERROR: stale path is not a directory: {stale_root}", file=sys.stderr)
        return 1
    if not local_root.is_dir():
        print(f"ERROR: local wiki is not a directory: {local_root}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Walking stale tree: {stale_root}", file=sys.stderr)
    stale = walk_tree(stale_root)
    if not args.quiet:
        print(f"  {len(stale)} files", file=sys.stderr)
        print(f"Walking canonical tree: {local_root}", file=sys.stderr)
    local = walk_tree(local_root)
    if not args.quiet:
        print(f"  {len(local)} files", file=sys.stderr)

    write_report(stale_root, local_root, stale, local, args.output)
    if not args.quiet:
        print(f"Wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
