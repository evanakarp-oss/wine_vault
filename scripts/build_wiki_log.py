#!/usr/bin/env python3
"""
build_wiki_log.py — seed wiki/log.md from git history; validate format.

Implements the chronological-log pattern from the Karpathy LLM-wiki gist:
an append-only record where each entry is prefixed
`## [YYYY-MM-DD] op | title`, which keeps the log greppable with simple
unix tools (e.g. `grep "^## \\[" wiki/log.md | tail -5`).

Two modes:

  Default (seed): read `git log` from the vault, classify each commit
  by subject keyword, and write a fresh wiki/log.md. Refuses to
  overwrite an existing log.md unless --force is given — once entries
  have been appended by the LLM or other scripts, re-seeding would
  destroy them. Seed is a one-shot bootstrap.

  --check: validate that every `## ` heading in log.md matches the
  canonical format. Exit 0 on clean, 1 on any violation. Use as a CI
  hook.

By default, the seed only includes commits whose subjects look like
high-leverage operations (ingest, compile, scrape, parse, lint,
build_*). Use --all to include every non-merge commit instead.

Usage:
    python scripts/build_wiki_log.py
    python scripts/build_wiki_log.py --all          # include every commit
    python scripts/build_wiki_log.py --force        # overwrite existing
    python scripts/build_wiki_log.py --check        # validate format only
    python scripts/build_wiki_log.py --vault-root /path/to/wine_vault

Requires: git in PATH.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


# Subject keyword → operation. First match wins. Patterns are matched
# case-insensitively against the commit subject. Ordering matters when
# multiple patterns could match the same subject.
OP_RULES: list[tuple[str, str]] = [
    ("ingest",   r"\bingest"),
    ("compile",  r"\bcompile"),
    ("scrape",   r"\bscrape"),
    ("parse",    r"\bparse\b"),
    ("lint",     r"\blint"),
    ("build",    r"\bbuild_(rollup|widget|wiki)"),
    ("merge",    r"^merge\b"),
    ("docs",     r"\b(readme|claude\.md|agents\.md|docs|schema|taxonomy|orientation)"),
    ("fix",      r"^fix\b|\bfix:"),
    ("refactor", r"^refactor"),
    ("wip",      r"\bwip\b"),
]

# Operations considered "noteworthy" for the seed. Edit/fix/refactor/docs/wip
# are filtered out by default; pass --all to include them.
DEFAULT_INTERESTING = frozenset({"ingest", "compile", "scrape", "parse", "lint", "build"})

# Match `## ` at start of line. Greedy `.+?` would still terminate at
# end-of-line; we use it to allow trailing whitespace stripping. The
# leading anchor + literal `## ` (exactly two #'s and a space) prevents
# `### ` (h3) from matching: position 2 of `###` is `#`, not space.
HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
ENTRY_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2})\] (\S+) \| (.+)$")


@dataclass
class Commit:
    sha: str
    date: str   # YYYY-MM-DD (author-local short)
    subject: str


def classify(subject: str) -> str:
    """Return an operation label derived from the commit subject."""
    for op, pat in OP_RULES:
        if re.search(pat, subject, flags=re.IGNORECASE):
            return op
    return "edit"


def git_log(vault_root: Path) -> list[Commit]:
    """Run git log and return commits oldest-first. Exit on failure."""
    SEP = "\x1f"  # ASCII unit separator — unlikely in commit subjects
    fmt = SEP.join(["%h", "%ad", "%s"])
    try:
        result = subprocess.run(
            ["git", "log", "--no-merges", "--reverse",
             f"--pretty=format:{fmt}", "--date=short"],
            cwd=str(vault_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        sys.exit("ERROR: git not found in PATH. Install git or run from "
                 "an environment that has it.")
    if result.returncode != 0:
        # Empty-repo special case: `git log` exits 128 when the repo
        # exists but has no commits yet. That's not an error for us —
        # the seed simply produces an empty log.md.
        empty_repo_markers = (
            "does not have any commits",
            "bad default revision",
            "unknown revision",
        )
        stderr_lower = (result.stderr or "").lower()
        if any(m in stderr_lower for m in empty_repo_markers):
            return []
        # Otherwise surface git's actual error (typically "not a git
        # repository").
        sys.exit(f"ERROR: git log failed ({result.returncode}): "
                 f"{result.stderr.strip() or '(no stderr)'}")
    commits: list[Commit] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split(SEP, 2)
        if len(parts) != 3:
            continue
        sha, date, subject = parts
        subject = subject.strip() or "(no message)"
        commits.append(Commit(sha=sha, date=date, subject=subject))
    return commits


def _sanitize_title(subject: str) -> str:
    """Make subject safe inside the `## [date] op | title` prefix.

    `|` would visually look like a second separator; replace with `/`.
    Newlines from --pretty=format:%s shouldn't appear (subject is one
    line by definition), but guard anyway.
    """
    title = subject.replace("|", "/").replace("\n", " ").strip()
    return title or "(no message)"


def render(commits: list[Commit]) -> str:
    out: list[str] = []
    out.append("---")
    out.append("type: log")
    out.append(f"total_entries: {len(commits)}")
    out.append("generator: scripts/build_wiki_log.py")
    out.append("---")
    out.append("")
    out.append("# Wiki Log")
    out.append("")
    out.append("<!-- Initial entries seeded from git history by "
               "`scripts/build_wiki_log.py`. After seeding, append new "
               "entries by hand or via your ingest/compile/lint "
               "scripts. Format: `## [YYYY-MM-DD] op | title`. -->")
    out.append("")
    out.append(
        "Chronological, append-only record of vault operations. Each "
        "entry's `## ` prefix makes the log greppable with simple "
        "unix tools — e.g. `grep \"^## \\[\" wiki/log.md | tail -5` "
        "for the five most recent operations."
    )
    out.append("")

    if not commits:
        out.append("_No entries yet._")
        out.append("")
        return "\n".join(out) + "\n"

    for c in commits:
        op = classify(c.subject)
        title = _sanitize_title(c.subject)
        out.append(f"## [{c.date}] {op} | {title}")
        out.append("")
        out.append(f"_commit `{c.sha}`_")
        out.append("")

    return "\n".join(out) + "\n"


def _strip_frontmatter(text: str) -> str:
    """Return body with leading YAML frontmatter removed (if present)."""
    m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    return text[m.end():] if m else text


def validate(log_path: Path) -> int:
    """Return 0 if every `## ` heading matches the canonical format,
    1 otherwise, 2 if the file is missing."""
    if not log_path.exists():
        print(f"ERROR: {log_path} not found. Run without --check to seed it.",
              file=sys.stderr)
        return 2
    text = log_path.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    headings = list(HEADING_RE.finditer(body))
    violations: list[tuple[int, str]] = []
    for m in headings:
        heading = m.group(1)
        if not ENTRY_RE.match(heading):
            line_no = body.count("\n", 0, m.start()) + 1
            violations.append((line_no, heading))
    if violations:
        print(f"FAIL: {len(violations)} of {len(headings)} heading(s) "
              "don't match `## [YYYY-MM-DD] op | title`:", file=sys.stderr)
        for ln, h in violations[:20]:
            print(f"  body-line {ln}: ## {h}", file=sys.stderr)
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more", file=sys.stderr)
        return 1
    print(f"OK: {log_path.name} has {len(headings)} entries, all valid.",
          file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault-root", type=Path,
                   default=Path(__file__).resolve().parent.parent,
                   help="Root of wine_vault. Defaults to parent of this script.")
    p.add_argument("--output", type=Path, default=None,
                   help="Output path. Defaults to <vault>/wiki/log.md")
    p.add_argument("--force", action="store_true",
                   help="Overwrite existing log.md (destroys appended entries).")
    p.add_argument("--check", action="store_true",
                   help="Validate log.md format. Exit 1 on any violation.")
    p.add_argument("--all", action="store_true",
                   help="Include every non-merge commit (default: only "
                        "ingest/compile/scrape/parse/lint/build commits).")
    p.add_argument("--quiet", action="store_true", help="Suppress info logs.")
    args = p.parse_args()

    vault = args.vault_root.resolve()
    output = args.output.resolve() if args.output else vault / "wiki" / "log.md"

    if args.check:
        return validate(output)

    if not vault.is_dir():
        sys.exit(f"ERROR: {vault} is not a directory")

    if output.exists() and not args.force:
        print(f"ERROR: {output} already exists. Use --force to overwrite "
              "(destroys any appended entries), or just keep appending "
              "to it by hand / via scripts.", file=sys.stderr)
        return 1

    all_commits = git_log(vault)
    if args.all:
        commits = all_commits
    else:
        commits = [c for c in all_commits if classify(c.subject) in DEFAULT_INTERESTING]

    if not args.quiet:
        print(f"Selected {len(commits)} of {len(all_commits)} commits "
              f"({'all non-merge' if args.all else 'interesting ops only'}).",
              file=sys.stderr)

    text = render(commits)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(text.encode("utf-8"))

    if not args.quiet:
        print(f"Wrote {output} ({len(text)} bytes, {len(commits)} entries)",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
