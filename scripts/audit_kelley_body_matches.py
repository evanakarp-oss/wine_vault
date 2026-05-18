#!/usr/bin/env python3
"""
audit_kelley_body_matches.py — sanity-check the body re-pass.

Question: how many of the 694 hits in build/kelley_body_repass_report_v2.md
are matching on actual reply prose vs. matching on the post-file frontmatter
(topic_title / topic_slug / topic_url)?

The main scanner folds the whole .md file, so if a producer's name appears in
the topic_slug but not in the body prose, it still counts as a hit. This audit
runs the same matcher on (a) full file, (b) frontmatter only, (c) body only,
and reports which producers have inflated counts.

Usage:
    python scripts/audit_kelley_body_matches.py
"""
from __future__ import annotations
import os, re, sys
from collections import defaultdict
from pathlib import Path

# Reuse the main script's matching code by importing it
sys.path.insert(0, str(Path(__file__).parent))
from reingest_kelley_bodies_v2 import (  # type: ignore
    load_producers, build_match_patterns, fold, POST_FILE_RE,
)

VAULT_ROOT = Path(os.environ.get("WINE_VAULT_ROOT", "."))
PRODUCERS_DIR = VAULT_ROOT / "wiki" / "producers"
POSTS_DIR = VAULT_ROOT / "raw" / "berserkers" / "William_Kelley" / "markdown"

FM_SPLIT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def split_post(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body_text). Empty strings if no frontmatter."""
    m = FM_SPLIT_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def main() -> None:
    print("Loading producers...", file=sys.stderr)
    producers = load_producers(PRODUCERS_DIR)
    patterns = build_match_patterns(producers)
    print(f"  {len(patterns)} producers with patterns", file=sys.stderr)

    # Counters keyed by slug
    full_hits: dict[str, int] = defaultdict(int)
    fm_hits: dict[str, int] = defaultdict(int)
    body_hits: dict[str, int] = defaultdict(int)
    n_scanned = 0

    print(f"Scanning {POSTS_DIR}...", file=sys.stderr)
    for path in POSTS_DIR.iterdir():
        if not POST_FILE_RE.match(path.name):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = split_post(text)
        full_folded = fold(text)
        fm_folded = fold(fm)
        body_folded = fold(body)
        n_scanned += 1
        for slug, pat in patterns.items():
            full_match = bool(pat.search(full_folded))
            if not full_match:
                continue
            full_hits[slug] += 1
            if pat.search(fm_folded):
                fm_hits[slug] += 1
            if pat.search(body_folded):
                body_hits[slug] += 1
        if n_scanned % 1000 == 0:
            print(f"  scanned {n_scanned}", file=sys.stderr)
    print(f"  scanned {n_scanned} posts total", file=sys.stderr)

    # Aggregate
    total_full = sum(full_hits.values())
    total_fm = sum(fm_hits.values())
    total_body = sum(body_hits.values())
    body_only = sum(1 for s in full_hits if body_hits[s] and not fm_hits.get(s))
    fm_only = sum(1 for s in full_hits if fm_hits.get(s) and not body_hits.get(s))
    both = sum(1 for s in full_hits if fm_hits.get(s) and body_hits.get(s))

    print()
    print("# Audit summary")
    print(f"- Full-file hits (current scanner): {total_full}")
    print(f"- Hits where FM matches:            {total_fm}")
    print(f"- Hits where BODY matches:          {total_body}")
    print()
    print(f"- Producers with body-only matches: {body_only}")
    print(f"- Producers with FM-only matches:   {fm_only}  (potentially over-credited)")
    print(f"- Producers matching in both:       {both}")
    print()

    # Per-producer breakdown of suspect cases (FM>0, body=0)
    print("# Producers where ALL hits are frontmatter-only (no body prose)")
    print("| Slug | Full | FM | Body |")
    print("|---|---:|---:|---:|")
    suspect = sorted(
        ((s, full_hits[s], fm_hits.get(s, 0), body_hits.get(s, 0))
         for s in full_hits if body_hits.get(s, 0) == 0),
        key=lambda r: -r[1],
    )
    for slug, full, fm, body in suspect[:40]:
        print(f"| `{slug}` | {full} | {fm} | {body} |")
    print()

    print("# Producers with PARTIAL body coverage (FM > body > 0) — top 20")
    print("| Slug | Full | FM | Body | Body % |")
    print("|---|---:|---:|---:|---:|")
    partial = []
    for s, full in full_hits.items():
        b = body_hits.get(s, 0)
        f = fm_hits.get(s, 0)
        if b > 0 and f > b:
            partial.append((s, full, f, b, 100.0 * b / full))
    partial.sort(key=lambda r: r[1], reverse=True)
    for slug, full, fm, body, pct in partial[:20]:
        print(f"| `{slug}` | {full} | {fm} | {body} | {pct:.0f}% |")


if __name__ == "__main__":
    main()
