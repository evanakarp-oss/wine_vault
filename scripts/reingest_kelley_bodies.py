#!/usr/bin/env python3
"""
reingest_kelley_bodies.py — body-text re-pass for William Kelley Berserkers posts.

The original ingest (scripts/ingest_blog_articles.py or equivalent) matched producers
only on topic titles / OPs, missing inline mentions in post bodies. Kelley name-checks
small bio Bordeaux producers, secondary references in long threads, and personal-cellar
buy lists all over body text. This pass re-scans ALL post bodies against ALL producer
names + aliases and produces a delta report.

DEFAULT BEHAVIOR: dry-run, writes only build/kelley_body_repass_report.md.
Pass --apply to write `berserkers_kelley_body` block into producer frontmatter.
The original `berserkers_kelley` block (title-OP matches) is left untouched —
this is additive so the two signals stay distinguishable.

Match philosophy:
- Strongly prefer multi-token producer names. "Clos Puy Arnaud", "Château Le Puy",
  "Bachelet-Ramonet" are nearly unambiguous.
- Single-token surnames are only matched if the slug is in SAFE_SINGLE_TOKEN.
  (Ramonet, Leflaive, Donnhoff are safe; Paris, Bachelet, Audoin, Moreau are not.)
- Word-boundary regex with Unicode + accent-insensitive folding.
- Per-post: at most one match per producer (no double-counting if name appears twice).
- Per-producer: posts are deduped by (topic_id, post_number).

Usage:
    python scripts/reingest_kelley_bodies.py
    python scripts/reingest_kelley_bodies.py --apply
    python scripts/reingest_kelley_bodies.py --producer-filter chateau_le_puy

"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# --- Paths (override via env if your layout differs) -------------------------
VAULT_ROOT = Path(os.environ.get("WINE_VAULT_ROOT", "."))
PRODUCERS_DIR = VAULT_ROOT / "wiki" / "producers"
BERSERKERS_DIR = VAULT_ROOT / "raw" / "berserkers" / "William_Kelley"
POSTS_DIR = BERSERKERS_DIR / "markdown"
POST_INDEX_CSV = BERSERKERS_DIR / "_post_index.csv"
BUILD_DIR = VAULT_ROOT / "build"
REPORT_PATH = BUILD_DIR / "kelley_body_repass_report.md"

# --- Match safety lists ------------------------------------------------------
# Slugs whose single-token name is distinctive enough to safely match alone.
# Add to this list only after confirming false-positive rate is near zero.
SAFE_SINGLE_TOKEN = {
    "ramonet", "leflaive", "donnhoff", "raveneau", "coche-dury", "roulot",
    "selosse", "krug", "bollinger", "taittinger", "salon", "egly-ouriet",
    "clemens_busch", "willi_schaefer", "schaefer-frohlich", "donnhoff",
    "keller", "emrich_schonleber", "ziereisen", "huet", "raveneau",
    "dauvissat", "fourrier", "rousseau", "barthod", "mugnier",
    "dujac", "ponsot", "chave", "rayas", "beaucastel",
    "valentini", "pepe", "occhipinti", "bonavita", "biondi_santi",
    "gravner", "radikon",
    # add others as evidence accrues
}

# Slugs known to be ambiguous — NEVER match on single token, even if listed
# in name. These need full multi-token form to count.
ALWAYS_MULTITOKEN = {
    "paris",       # city false-matches
    "bachelet",    # multiple Bachelet families (Denis, JC, Ramonet, Monnot)
    "moreau",      # generic
    "audoin",      # ambiguous
    "rousset",     # multiple Roussets
    "noellat",     # Hudelot/Michel/Georges
    "guyon",       # multiple
    "tissot",      # Stéphane vs others
    "lorenzon",    # vs Bruno Lorenzon
    "mallard",     # vs Michel Mallard
    "magnien",     # Frédéric vs Stéphane vs others
    "tawse",       # vs Marchand-Tawse
    "rings",       # generic word
    "chateau_brandeau",  # "brandeau" too generic alone
}

# Common stopword-like single tokens to never match even if a name reduces to them
TOKEN_BLACKLIST = {
    "domaine", "chateau", "weingut", "clos", "domaines", "fils",
    "et", "de", "la", "le", "les", "du", "des", "von", "the",
    "wine", "wines", "vineyard", "estate",
}

# --- Frontmatter parsing -----------------------------------------------------
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

def parse_frontmatter(text: str) -> dict:
    """Crude YAML-ish frontmatter parser; sufficient for our schema."""
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    current_key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # top-level key: value
        if not line.startswith(" "):
            if ":" in line:
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip().strip('"').strip("'")
                current_key = k.strip()
        # nested handled crudely; we don't need nested for this script
    return out

def extract_aliases(text: str) -> list[str]:
    m = re.search(r"^aliases:\s*\[(.*?)\]", text, re.MULTILINE)
    if not m:
        return []
    raw = m.group(1)
    return [a.strip().strip("'").strip('"') for a in raw.split(",") if a.strip()]

# --- Producer index ----------------------------------------------------------
@dataclass
class Producer:
    slug: str
    name: str
    aliases: list[str] = field(default_factory=list)
    path: Path = None

    def display_names(self) -> list[str]:
        names = [self.name] + self.aliases
        # Add slug-derived form ("chateau_le_puy" -> "Chateau Le Puy")
        slug_form = " ".join(w.capitalize() for w in self.slug.split("_"))
        if slug_form not in names:
            names.append(slug_form)
        return [n for n in names if n]

def fold(s: str) -> str:
    """Lowercase + strip diacritics for matching."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def build_match_patterns(producers: list[Producer]) -> dict[str, re.Pattern]:
    """For each slug, compile a regex that matches any plausible mention."""
    patterns = {}
    for p in producers:
        terms: set[str] = set()
        for name in p.display_names():
            n = fold(name)
            if not n:
                continue
            # Strip leading common prefixes
            for prefix in ("chateau ", "domaine ", "weingut ", "domaines "):
                if n.startswith(prefix):
                    n_stripped = n[len(prefix):].strip()
                    if n_stripped and n_stripped not in TOKEN_BLACKLIST:
                        terms.add(n_stripped)
            terms.add(n)
        # Single-token policy
        if p.slug in ALWAYS_MULTITOKEN:
            terms = {t for t in terms if " " in t or "-" in t}
        elif p.slug not in SAFE_SINGLE_TOKEN:
            # Default for unlisted: require multi-token unless the single
            # token is also the full name and it's at least 7 chars
            multi = {t for t in terms if " " in t or "-" in t}
            singles_kept = {t for t in terms if " " not in t and "-" not in t and len(t) >= 9}
            terms = multi | singles_kept
        if not terms:
            continue
        # Word-boundary regex
        escaped = sorted({re.escape(t) for t in terms}, key=len, reverse=True)
        patterns[p.slug] = re.compile(r"(?<![\w-])(" + "|".join(escaped) + r")(?![\w-])")
    return patterns

def load_producers(producers_dir: Path) -> list[Producer]:
    out = []
    for path in sorted(producers_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        slug = fm.get("slug") or path.stem
        name = fm.get("name") or slug.replace("_", " ").title()
        aliases = extract_aliases(text)
        out.append(Producer(slug=slug, name=name, aliases=aliases, path=path))
    return out

# --- Post scanning -----------------------------------------------------------
POST_FILE_RE = re.compile(r"^(\d+)__(\d+)\.md$")

@dataclass
class Hit:
    topic_id: int
    post_number: int
    excerpt: str  # ~200 char window around the match

def scan_posts(posts_dir: Path, patterns: dict[str, re.Pattern], producer_filter: set[str] | None = None):
    hits: dict[str, list[Hit]] = defaultdict(list)
    n_scanned = 0
    for path in posts_dir.iterdir():
        m = POST_FILE_RE.match(path.name)
        if not m:
            continue
        topic_id = int(m.group(1))
        post_num = int(m.group(2))
        body = path.read_text(encoding="utf-8", errors="replace")
        folded = fold(body)
        n_scanned += 1
        for slug, pat in patterns.items():
            if producer_filter and slug not in producer_filter:
                continue
            mh = pat.search(folded)
            if mh:
                start = max(0, mh.start() - 80)
                end = min(len(body), mh.end() + 120)
                hits[slug].append(Hit(topic_id=topic_id, post_number=post_num, excerpt=body[start:end].replace("\n", " ")))
        if n_scanned % 500 == 0:
            print(f"  scanned {n_scanned} posts, {sum(len(v) for v in hits.values())} cumulative hits", file=sys.stderr)
    return hits, n_scanned

# --- Existing post counts (from frontmatter) ---------------------------------
def get_existing_post_count(text: str) -> int:
    m = re.search(r"berserkers_kelley:\s*\n(?:\s+\w+:.*\n)*?\s+post_count:\s*(\d+)", text)
    return int(m.group(1)) if m else 0

# --- Main --------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write berserkers_kelley_body block to producer frontmatter")
    ap.add_argument("--producer-filter", action="append", help="Only process these slugs (repeatable)")
    ap.add_argument("--posts-dir", type=Path, default=POSTS_DIR)
    ap.add_argument("--producers-dir", type=Path, default=PRODUCERS_DIR)
    args = ap.parse_args()

    print(f"Loading producers from {args.producers_dir}...", file=sys.stderr)
    producers = load_producers(args.producers_dir)
    print(f"  loaded {len(producers)} producers", file=sys.stderr)

    pf = set(args.producer_filter) if args.producer_filter else None

    print("Building match patterns...", file=sys.stderr)
    patterns = build_match_patterns(producers)
    print(f"  {len(patterns)} producers have matchable patterns", file=sys.stderr)

    print(f"Scanning {args.posts_dir}...", file=sys.stderr)
    hits, n_scanned = scan_posts(args.posts_dir, patterns, pf)
    print(f"  scanned {n_scanned} posts", file=sys.stderr)

    # Build report
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    by_slug = {p.slug: p for p in producers}

    lines = []
    lines.append("# Kelley body-text re-pass — delta report\n")
    lines.append(f"Scanned **{n_scanned}** posts against **{len(patterns)}** producer patterns.\n")
    lines.append(f"Producers with at least one body-text hit: **{len(hits)}**\n\n")

    # Movers: producers with body hits but title-OP post_count was 0
    new_finds = []
    movers = []
    for slug, h in hits.items():
        prod = by_slug.get(slug)
        if not prod:
            continue
        existing = get_existing_post_count(prod.path.read_text(encoding="utf-8", errors="replace"))
        if existing == 0:
            new_finds.append((slug, prod.name, len(h)))
        elif len(h) > existing:
            movers.append((slug, prod.name, existing, len(h)))

    new_finds.sort(key=lambda x: -x[2])
    movers.sort(key=lambda x: -(x[3] - x[2]))

    lines.append("## NEW finds (zero title-OP matches → ≥1 body hit)\n")
    lines.append("| Slug | Name | Body hits |")
    lines.append("|---|---|---:|")
    for slug, name, n in new_finds:
        lines.append(f"| `{slug}` | {name} | {n} |")
    lines.append("")

    lines.append("\n## Movers (body hits exceed title-OP count)\n")
    lines.append("| Slug | Name | Title-OP | Body | Δ |")
    lines.append("|---|---|---:|---:|---:|")
    for slug, name, old, new in movers:
        lines.append(f"| `{slug}` | {name} | {old} | {new} | +{new - old} |")
    lines.append("")

    # Sample excerpts for spot-checking
    lines.append("\n## Sample excerpts (first 2 hits per new find, for false-positive review)\n")
    for slug, name, _ in new_finds[:50]:
        lines.append(f"\n### {name} (`{slug}`)")
        for h in hits[slug][:2]:
            lines.append(f"- _{h.topic_id}/#{h.post_number}_: …{h.excerpt}…")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report → {REPORT_PATH}", file=sys.stderr)

    if args.apply:
        print("Writing berserkers_kelley_body blocks to producer pages...", file=sys.stderr)
        n_updated = 0
        for slug, h in hits.items():
            prod = by_slug.get(slug)
            if not prod:
                continue
            text = prod.path.read_text(encoding="utf-8", errors="replace")
            if "berserkers_kelley_body:" in text:
                # idempotent: replace existing block
                text = re.sub(
                    r"\n\s*berserkers_kelley_body:\s*\n(?:\s{2,}\w+:.*\n)+",
                    "\n",
                    text,
                )
            block = (
                f"\n  berserkers_kelley_body:\n"
                f"    body_hit_count: {len(h)}\n"
                f"    distinct_topics: {len({x.topic_id for x in h})}\n"
                f"    note: \"derived from body-text re-pass; additive to berserkers_kelley\"\n"
            )
            # insert just before the closing --- of frontmatter
            new_text, n = re.subn(r"(\n)(---\s*\n)", block + r"\1\2", text, count=1)
            if n:
                prod.path.write_text(new_text, encoding="utf-8")
                n_updated += 1
        print(f"  updated {n_updated} producer pages", file=sys.stderr)

if __name__ == "__main__":
    main()
