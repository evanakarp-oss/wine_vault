"""
build_home.py — generate wiki/HOME.md, the human entry point to the vault.

One screen: drink-window urgency counts, saved analyses (wiki/_views/),
browse-by-region/country links, and cellar quick stats. Everything links
onward — HOME is navigation, not content.

Idempotent; `--check` exits 1 if regenerating would change the file
(CI hook, same contract as build_wiki_index.py).

Pin HOME.md as the Obsidian homepage (vault root = wine_vault/).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CELLAR = VAULT / "cellar"
PRODUCERS = VAULT / "wiki" / "producers"
REGIONS = VAULT / "wiki" / "regions"
VIEWS = VAULT / "wiki" / "_views"
OUTPUT = VAULT / "wiki" / "HOME.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
CURRENT_YEAR = date.today().year
ENTERING_HORIZON = 2  # years ahead that count as "entering soon"


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_year(s: str) -> int | None:
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def drink_window_buckets() -> dict[str, int]:
    """Bottle counts per urgency bucket (same buckets as drink_window_due)."""
    buckets = {"past": 0, "now": 0, "entering": 0, "longhold": 0, "unknown": 0}
    for p in CELLAR.glob("*.md"):
        m = FM_RE.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        fm = m.group(1)
        if get_str(fm, "type") != "cellar_entry":
            continue
        qty = parse_year(get_str(fm, "quantity")) or 0
        start = parse_year(get_str(fm, "drink_window_start"))
        end = parse_year(get_str(fm, "drink_window_end"))
        if start is None and end is None:
            buckets["unknown"] += qty
        elif end is not None and end < CURRENT_YEAR:
            buckets["past"] += qty
        elif (start or 0) <= CURRENT_YEAR <= (end or CURRENT_YEAR):
            buckets["now"] += qty
        elif start is not None and CURRENT_YEAR < start <= CURRENT_YEAR + ENTERING_HORIZON:
            buckets["entering"] += qty
        elif start is not None:
            buckets["longhold"] += qty
        else:
            buckets["unknown"] += qty
    return buckets


def cellar_stats() -> tuple[int, int, int, list[tuple[str, int]]]:
    entries = 0
    bottles = 0
    producers: set[str] = set()
    by_region: dict[str, int] = defaultdict(int)
    for p in CELLAR.glob("*.md"):
        m = FM_RE.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        fm = m.group(1)
        if get_str(fm, "type") != "cellar_entry":
            continue
        entries += 1
        qty = parse_year(get_str(fm, "quantity")) or 0
        bottles += qty
        slug = get_str(fm, "producer_slug")
        if slug:
            producers.add(slug)
        region = get_str(fm, "region") or "Unknown"
        by_region[region] += qty
    top = sorted(by_region.items(), key=lambda kv: -kv[1])[:8]
    return entries, bottles, len(producers), top


def list_views() -> list[tuple[str, str, str]]:
    """(stem, updated, first heading or prettified stem) per view file."""
    out = []
    for p in sorted(VIEWS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        fm, body = (m.group(1), m.group(2)) if m else ("", text)
        updated = get_str(fm, "updated")
        h = re.search(r"^# (.+)$", body, re.MULTILINE)
        title = h.group(1).strip() if h else p.stem.replace("_", " ").title()
        out.append((p.stem, updated, title))
    # newest first
    out.sort(key=lambda v: v[1], reverse=True)
    return out


def list_region_pages() -> tuple[list[tuple[str, str, int]], list[tuple[str, str, int]]]:
    """(stem, display, producer_count) split into (country hubs, regions)."""
    countries, regions = [], []
    for p in sorted(REGIONS.glob("*.md")):
        m = FM_RE.match(p.read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        fm = m.group(1)
        n = parse_year(get_str(fm, "producer_count")) or 0
        if get_str(fm, "type") == "country_index":
            countries.append((p.stem, get_str(fm, "country") or p.stem, n))
        else:
            regions.append((p.stem, get_str(fm, "region") or p.stem, n))
    countries.sort(key=lambda r: -r[2])
    regions.sort(key=lambda r: -r[2])
    return countries, regions


def render() -> str:
    buckets = drink_window_buckets()
    entries, bottles, n_producers, top_regions = cellar_stats()
    views = list_views()
    countries, regions = list_region_pages()
    n_producer_pages = len(list(PRODUCERS.glob("*.md")))

    out = [
        "---",
        "type: home",
        "generator: scripts/build_home.py",
        "---",
        "",
        "# 🍷 Wine Vault — Home",
        "",
        "<!-- Generated by `scripts/build_home.py`. Do not hand-edit. -->",
        "",
        "Entry point for humans. LLMs start at [[index|the wiki index]] instead.",
        "",
        "## Drink-window urgency",
        "",
        f"- ⚠️ **{buckets['past']} bottles past window** — drink or triage",
        f"- 🍷 **{buckets['now']} bottles in window now**",
        f"- 📅 {buckets['entering']} bottles entering within {ENTERING_HORIZON} years",
        f"- 🛌 {buckets['longhold']} long-hold · ❓ {buckets['unknown']} unknown window",
        "",
        "→ Full urgency tables: [[drink_window_due|Drink-window due]]",
        "",
        "## Saved analyses",
        "",
        "| View | Updated |",
        "|---|---|",
    ]
    for stem, updated, title in views:
        title = title.replace("|", "/")
        out.append(f"| [[{stem}|{title}]] | {updated or '—'} |")
    out += [
        "",
        "## Browse",
        "",
        f"**{n_producer_pages} producer pages.** By country: "
        + " · ".join(f"[[{stem}|{disp}]] ({n})" for stem, disp, n in countries),
        "",
        "Top regions: "
        + " · ".join(f"[[{stem}|{disp}]] ({n})" for stem, disp, n in regions[:12]),
        "",
        "- [[index|Wiki index]] — every page, grouped by type (LLM entry point)",
        "- [[log|Change log]] — append-only history of vault operations",
        "- [[_SCHEMA|Schema]] · [[_TAXONOMY|Taxonomy]] — page structure & enums",
        "",
        "## Cellar at a glance",
        "",
        f"**{bottles} bottles** · {entries} cuvée-vintages · {n_producers} producers.",
        "",
        "Bottles by region: "
        + " · ".join(f"{r} ({n})" for r, n in top_regions),
        "",
        "---",
        "_Regenerate: `python scripts/build_home.py`_",
    ]
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if regenerating would change HOME.md.")
    args = parser.parse_args()

    content = render()
    existing = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
    if args.check:
        if content != existing:
            print("HOME.md is stale — run `python scripts/build_home.py`",
                  file=sys.stderr)
            return 1
        print("HOME.md is current.")
        return 0
    if content != existing:
        OUTPUT.write_text(content, encoding="utf-8")
        print(f"Wrote {OUTPUT}")
    else:
        print("HOME.md unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
