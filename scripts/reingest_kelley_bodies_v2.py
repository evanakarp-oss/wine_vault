#!/usr/bin/env python3
"""
reingest_kelley_bodies_v2.py — body-text re-pass for William Kelley Berserkers
posts, with PER-POST DATES captured.

What changed vs v1 (reingest_kelley_bodies.py):
  - Loads raw/berserkers/William_Kelley/_post_index.csv to look up the post
    date for every (topic_id, post_number).
  - Hit dataclass now carries `date` (ISO YYYY-MM-DD).
  - Frontmatter `berserkers_kelley_body` block now also writes:
        first_year:    earliest YYYY across hits
        last_year:     most recent YYYY across hits
        recent_posts:  YAML list of up to 5 most-recent {date, url} pairs
  - Replacement regex generalised to also tolerate YAML list items
    (`- {...}`), so re-runs are still idempotent.
  - Report sorts new finds and movers by `last_year DESC` so "what is Kelley
    championing now" answers fall out of the top of the table.

DEFAULT BEHAVIOR: dry-run, writes only build/kelley_body_repass_report_v2.md.
Pass --apply to write `berserkers_kelley_body` block into producer frontmatter.
The original `berserkers_kelley` block (title-OP matches) is left untouched.

Usage:
    python scripts/reingest_kelley_bodies_v2.py
    python scripts/reingest_kelley_bodies_v2.py --apply
    python scripts/reingest_kelley_bodies_v2.py --producer-filter henri_magnien
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# --- Paths -----------------------------------------------------------------
VAULT_ROOT = Path(os.environ.get("WINE_VAULT_ROOT", "."))
PRODUCERS_DIR = VAULT_ROOT / "wiki" / "producers"
BERSERKERS_DIR = VAULT_ROOT / "raw" / "berserkers" / "William_Kelley"
POSTS_DIR = BERSERKERS_DIR / "markdown"
POST_INDEX_CSV = BERSERKERS_DIR / "_post_index.csv"
BUILD_DIR = VAULT_ROOT / "build"
REPORT_PATH = BUILD_DIR / "kelley_body_repass_report_v2.md"

# --- Match safety lists (unchanged from v1) --------------------------------
SAFE_SINGLE_TOKEN = {
    "ramonet", "leflaive", "donnhoff", "raveneau", "coche-dury", "roulot",
    "selosse", "krug", "bollinger", "taittinger", "salon", "egly-ouriet",
    "clemens_busch", "willi_schaefer", "schaefer-frohlich",
    "keller", "emrich_schonleber", "ziereisen", "huet",
    "dauvissat", "fourrier", "rousseau", "barthod", "mugnier",
    "dujac", "ponsot", "chave", "rayas", "beaucastel",
    "valentini", "pepe", "occhipinti", "bonavita", "biondi_santi",
    "gravner", "radikon",
}

ALWAYS_MULTITOKEN = {
    "paris", "bachelet", "moreau", "audoin", "rousset", "noellat",
    "guyon", "tissot", "lorenzon", "mallard", "magnien", "tawse",
    "rings", "chateau_brandeau",
}

TOKEN_BLACKLIST = {
    "domaine", "chateau", "weingut", "clos", "domaines", "fils",
    "et", "de", "la", "le", "les", "du", "des", "von", "the",
    "wine", "wines", "vineyard", "estate",
}

# --- Frontmatter parsing ---------------------------------------------------
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            if ":" in line:
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def extract_aliases(text: str) -> list[str]:
    m = re.search(r"^aliases:\s*\[(.*?)\]", text, re.MULTILINE)
    if not m:
        return []
    return [a.strip().strip("'").strip('"') for a in m.group(1).split(",") if a.strip()]

# --- Post index ------------------------------------------------------------
def load_post_index(path: Path) -> dict[tuple[int, int], dict]:
    """Returns {(topic_id, post_number): {date, post_url, topic_title}}."""
    if not path.exists():
        print(f"WARNING: post index {path} not found; dates will be empty", file=sys.stderr)
        return {}
    out = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tid = int(row["topic_id"])
                pn = int(row["post_number"])
            except (KeyError, ValueError, TypeError):
                continue
            out[(tid, pn)] = {
                "date": (row.get("date") or "").strip(),
                "post_url": (row.get("post_url") or "").strip(),
                "topic_title": (row.get("topic_title") or "").strip(),
            }
    print(f"  loaded {len(out)} entries from post index", file=sys.stderr)
    return out

# --- Producer index --------------------------------------------------------
@dataclass
class Producer:
    slug: str
    name: str
    aliases: list[str] = field(default_factory=list)
    path: Path = None

    def display_names(self) -> list[str]:
        names = [self.name] + self.aliases
        slug_form = " ".join(w.capitalize() for w in self.slug.split("_"))
        if slug_form not in names:
            names.append(slug_form)
        return [n for n in names if n]

def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def build_match_patterns(producers: list[Producer]) -> dict[str, re.Pattern]:
    patterns = {}
    for p in producers:
        terms: set[str] = set()
        for name in p.display_names():
            n = fold(name)
            if not n:
                continue
            for prefix in ("chateau ", "domaine ", "weingut ", "domaines "):
                if n.startswith(prefix):
                    n_stripped = n[len(prefix):].strip()
                    if n_stripped and n_stripped not in TOKEN_BLACKLIST:
                        terms.add(n_stripped)
            terms.add(n)
        if p.slug in ALWAYS_MULTITOKEN:
            terms = {t for t in terms if " " in t or "-" in t}
        elif p.slug not in SAFE_SINGLE_TOKEN:
            multi = {t for t in terms if " " in t or "-" in t}
            singles_kept = {t for t in terms if " " not in t and "-" not in t and len(t) >= 9}
            terms = multi | singles_kept
        if not terms:
            continue
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

# --- Post scanning ---------------------------------------------------------
POST_FILE_RE = re.compile(r"^(\d+)__(\d+)\.md$")

@dataclass
class Hit:
    topic_id: int
    post_number: int
    date: str        # ISO YYYY-MM-DD or "" if unknown
    post_url: str    # canonical URL or "" if unknown
    excerpt: str

def scan_posts(
    posts_dir: Path,
    patterns: dict[str, re.Pattern],
    post_index: dict[tuple[int, int], dict],
    producer_filter: set[str] | None = None,
):
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
        idx_entry = post_index.get((topic_id, post_num), {})
        date = idx_entry.get("date", "")
        post_url = idx_entry.get("post_url", "")
        for slug, pat in patterns.items():
            if producer_filter and slug not in producer_filter:
                continue
            mh = pat.search(folded)
            if mh:
                start = max(0, mh.start() - 80)
                end = min(len(body), mh.end() + 120)
                hits[slug].append(Hit(
                    topic_id=topic_id,
                    post_number=post_num,
                    date=date,
                    post_url=post_url,
                    excerpt=body[start:end].replace("\n", " "),
                ))
        if n_scanned % 500 == 0:
            print(f"  scanned {n_scanned} posts, {sum(len(v) for v in hits.values())} cumulative hits",
                  file=sys.stderr)
    return hits, n_scanned

def get_existing_post_count(text: str) -> int:
    m = re.search(r"berserkers_kelley:\s*\n(?:\s+\w+:.*\n)*?\s+post_count:\s*(\d+)", text)
    return int(m.group(1)) if m else 0

# --- Aggregation helpers ---------------------------------------------------
def year_of(iso_date: str) -> int | None:
    if not iso_date or len(iso_date) < 4:
        return None
    try:
        return int(iso_date[:4])
    except ValueError:
        return None

def aggregate_dates(hit_list: list[Hit]) -> dict:
    years = sorted({y for h in hit_list if (y := year_of(h.date)) is not None})
    sorted_by_date = sorted(
        (h for h in hit_list if h.date),
        key=lambda h: h.date,
        reverse=True,
    )
    recent = sorted_by_date[:5]
    return {
        "first_year": years[0] if years else 0,
        "last_year": years[-1] if years else 0,
        "recent_posts": [
            {"date": h.date, "url": h.post_url or f"topic/{h.topic_id}/{h.post_number}"}
            for h in recent
        ],
    }

# --- Frontmatter writing ---------------------------------------------------
# Match the body block plus all indented continuation lines (covers both
# `key: value` and `- {...}` list items).
EXISTING_BLOCK_RE = re.compile(
    r"\n\s*berserkers_kelley_body:[^\n]*\n(?:[ \t]+[^\n]*\n)*"
)

def render_block(slug_hits: list[Hit]) -> str:
    agg = aggregate_dates(slug_hits)
    lines = [
        "berserkers_kelley_body:",
        f"  body_hit_count: {len(slug_hits)}",
        f"  distinct_topics: {len({x.topic_id for x in slug_hits})}",
        f"  first_year: {agg['first_year']}",
        f"  last_year: {agg['last_year']}",
    ]
    if agg["recent_posts"]:
        lines.append("  recent_posts:")
        for p in agg["recent_posts"]:
            url_escaped = p["url"].replace('"', '\\"')
            lines.append(f'    - {{date: "{p["date"]}", url: "{url_escaped}"}}')
    lines.append('  note: "derived from body-text re-pass v2; additive to berserkers_kelley"')
    return "\n" + "\n".join(lines) + "\n"

# --- Main ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Write berserkers_kelley_body block to producer frontmatter")
    ap.add_argument("--producer-filter", action="append",
                    help="Only process these slugs (repeatable)")
    ap.add_argument("--posts-dir", type=Path, default=POSTS_DIR)
    ap.add_argument("--producers-dir", type=Path, default=PRODUCERS_DIR)
    ap.add_argument("--post-index", type=Path, default=POST_INDEX_CSV)
    args = ap.parse_args()

    print(f"Loading post index from {args.post_index}...", file=sys.stderr)
    post_index = load_post_index(args.post_index)

    print(f"Loading producers from {args.producers_dir}...", file=sys.stderr)
    producers = load_producers(args.producers_dir)
    print(f"  loaded {len(producers)} producers", file=sys.stderr)

    pf = set(args.producer_filter) if args.producer_filter else None

    print("Building match patterns...", file=sys.stderr)
    patterns = build_match_patterns(producers)
    print(f"  {len(patterns)} producers have matchable patterns", file=sys.stderr)

    print(f"Scanning {args.posts_dir}...", file=sys.stderr)
    hits, n_scanned = scan_posts(args.posts_dir, patterns, post_index, pf)
    print(f"  scanned {n_scanned} posts", file=sys.stderr)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    by_slug = {p.slug: p for p in producers}

    # Build report ----------------------------------------------------------
    lines: list[str] = []
    lines.append("# Kelley body-text re-pass v2 (with dates) — delta report\n")
    lines.append(f"Scanned **{n_scanned}** posts against **{len(patterns)}** producer patterns.")
    lines.append(f"Producers with at least one body-text hit: **{len(hits)}**\n")

    n_with_dates = sum(1 for hl in hits.values() for h in hl if h.date)
    n_total_hits = sum(len(v) for v in hits.values())
    coverage = (n_with_dates / n_total_hits * 100) if n_total_hits else 0
    lines.append(f"Date coverage: {n_with_dates}/{n_total_hits} hits ({coverage:.1f}%)\n")

    # Group A: producers Kelley has body-mentioned with last_year >= 2024.
    # This is the headline finding for "what is he championing now".
    recent_finds: list[tuple[str, str, int, int, int]] = []
    all_movers: list[tuple[str, str, int, int, int, int]] = []
    for slug, hl in hits.items():
        prod = by_slug.get(slug)
        if not prod:
            continue
        agg = aggregate_dates(hl)
        existing_op = get_existing_post_count(
            prod.path.read_text(encoding="utf-8", errors="replace")
        )
        if agg["last_year"] >= 2024:
            recent_finds.append((slug, prod.name, len(hl), agg["first_year"], agg["last_year"]))
        if len(hl) > existing_op:
            all_movers.append((slug, prod.name, existing_op, len(hl),
                               agg["first_year"], agg["last_year"]))

    recent_finds.sort(key=lambda r: (-r[4], -r[2]))   # last_year desc, then hits desc
    all_movers.sort(key=lambda r: (-r[5], -(r[3] - r[2])))

    lines.append("\n## Kelley body-mentions in 2024+ (headline finding)\n")
    lines.append("| Slug | Name | Body hits | First | Last |")
    lines.append("|---|---|---:|---:|---:|")
    for slug, name, n, fy, ly in recent_finds:
        lines.append(f"| `{slug}` | {name} | {n} | {fy} | {ly} |")
    lines.append("")

    lines.append("\n## Movers (body hits exceed title-OP count), sorted by recency\n")
    lines.append("| Slug | Name | Title-OP | Body | Δ | Last |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for slug, name, old, new, _, ly in all_movers:
        lines.append(f"| `{slug}` | {name} | {old} | {new} | +{new - old} | {ly} |")
    lines.append("")

    # Sample excerpts — most recent post per recent find
    lines.append("\n## Most-recent excerpt per 2024+ producer (for spot-check)\n")
    for slug, name, _, _, _ in recent_finds[:60]:
        prod = by_slug.get(slug)
        if not prod:
            continue
        sorted_hits = sorted(hits[slug], key=lambda h: h.date or "", reverse=True)
        if not sorted_hits:
            continue
        h = sorted_hits[0]
        lines.append(f"\n### {name} (`{slug}`) — most recent {h.date or '(undated)'}")
        lines.append(f"- _{h.post_url or f'topic {h.topic_id}/#{h.post_number}'}_")
        lines.append(f"- …{h.excerpt}…")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report → {REPORT_PATH}", file=sys.stderr)

    # Apply -----------------------------------------------------------------
    if args.apply:
        print("Writing berserkers_kelley_body blocks to producer pages...", file=sys.stderr)
        n_updated = 0
        for slug, hl in hits.items():
            prod = by_slug.get(slug)
            if not prod:
                continue
            text = prod.path.read_text(encoding="utf-8", errors="replace")
            # Idempotent: strip any existing block (v1 or v2 layout) before inserting
            text = EXISTING_BLOCK_RE.sub("\n", text)
            block = render_block(hl)
            # Insert just before the closing --- of the frontmatter
            new_text, n = re.subn(r"(\n)(---\s*\n)", block + r"\1\2", text, count=1)
            if n:
                prod.path.write_text(new_text, encoding="utf-8")
                n_updated += 1
        print(f"  updated {n_updated} producer pages", file=sys.stderr)

if __name__ == "__main__":
    main()
