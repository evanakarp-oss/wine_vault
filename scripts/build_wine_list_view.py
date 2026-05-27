"""
Render wiki/_views/wine_list_arrivals.md from the latest diff JSON.

Reads build/wine_list_arrivals_<YYYY-WW>.json (latest by default; pick one
with --week) and writes:

  - wiki/_views/wine_list_arrivals.md                 ← "latest week" pointer
  - wiki/_views/wine_list_arrivals_<YYYY-WW>.md       ← archived weekly view

Both files have the same content; the first is overwritten each week, the
second is preserved as a historical record.

The view groups by restaurant. Each new arrival is shown with:
  - producer (as a wikilink if a vault page exists; otherwise raw + ❓ flag)
  - cuvée, vintage, region, price
  - whether it's by-the-glass
  - section it appeared in on the list

Wines whose producer doesn't match an existing vault page are surfaced at
the bottom as "candidate new producers" — feeds the same triage workflow
as build/raeders_candidates.md.

Usage:
    python scripts/build_wine_list_view.py            # dry-run latest week
    python scripts/build_wine_list_view.py --apply
    python scripts/build_wine_list_view.py --week 2026-W21 --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
BUILD_DIR = VAULT / "build"
VIEWS_DIR = VAULT / "wiki" / "_views"

WEEK_RE = re.compile(r"^wine_list_arrivals_(\d{4}-W\d{2})\.json$")


def _latest_week_file() -> Path | None:
    files = []
    for p in BUILD_DIR.glob("wine_list_arrivals_*.json"):
        m = WEEK_RE.match(p.name)
        if m:
            files.append((m.group(1), p))
    if not files:
        return None
    files.sort(key=lambda t: t[0])
    return files[-1][1]


def _wine_row(wine: dict) -> str:
    """One row of the additions table."""
    if wine["producer_slug_confidence"] == "high" and wine["producer_slug"]:
        producer_md = f"[[{wine['producer_slug']}|{wine['producer_raw']}]]"
    else:
        producer_md = f"{wine['producer_raw']} ❓"
    vintage = wine["vintage"] or "NV"
    price = f"${wine['price_usd']:g}" if wine.get("price_usd") else "—"
    glass = "🍷" if wine.get("by_the_glass") else ""
    cuvee = wine.get("cuvee", "") or "—"
    section = wine.get("section", "") or "—"
    return (f"| {producer_md} | {cuvee} | {vintage} | "
            f"{wine.get('region', '') or '—'} | {price} | {glass} | {section} |")


def _render(payload: dict) -> str:
    week = payload["week"]
    totals = payload["totals"]
    per_source = payload["by_source"]
    generated = payload["generated_at"]

    parts: list[str] = []
    parts.append("---")
    parts.append("type: view")
    parts.append(f"slug: wine_list_arrivals_{week}")
    parts.append(f"week: {week}")
    parts.append(f"generated: {generated}")
    parts.append("source: scripts/build_wine_list_view.py")
    parts.append("---")
    parts.append("")
    parts.append(f"# Wine List Arrivals — {week}")
    parts.append("")
    parts.append(
        f"Producers, cuvées, and vintages that appeared on monitored NYC wine "
        f"lists this week and weren't on the prior week's list. "
        f"**{totals['added']} additions** across {sum(1 for s in per_source if s['status'] == 'diffed')} "
        f"diffed sources."
    )
    parts.append("")
    parts.append(
        "Producer names rendered as `[[slug|Name]]` already have a vault page. "
        "Names suffixed `❓` don't match any existing producer — candidates "
        "for triage and potential new pages.")
    parts.append("")

    # Per-restaurant sections
    candidates: list[tuple[str, dict]] = []  # (restaurant_name, wine)
    for src in per_source:
        slug = src["slug"]
        restaurant = src.get("restaurant", {})
        name = restaurant.get("name", slug)
        address = restaurant.get("address", "")

        parts.append(f"## {name}" + (f" — *{address}*" if address else ""))
        parts.append("")
        if src["status"] == "no_snapshots":
            parts.append("_No snapshots yet — run `scripts/scrape_wine_lists.py "
                         f"{slug}` then `scripts/parse_wine_list.py {slug}`._")
            parts.append("")
            continue
        if src["status"] == "first_snapshot":
            parts.append(f"_First snapshot on {src['latest_date']} "
                         f"({src['latest_count']} wines). Next week's diff "
                         f"will surface arrivals._")
            parts.append("")
            continue

        added = src["added"]
        removed = src["removed"]
        parts.append(
            f"_{src['previous_date']} → {src['latest_date']}: "
            f"**+{len(added)}** added, −{len(removed)} removed_  "
            f"(_{src['previous_count']} → {src['latest_count']} total_)"
        )
        parts.append("")

        if not added:
            parts.append("No new arrivals this week.")
            parts.append("")
            continue

        parts.append("| Producer | Cuvée | Vintage | Region | Price | BTG | Section |")
        parts.append("|---|---|---|---|---|---|---|")
        for wine in added:
            parts.append(_wine_row(wine))
            if wine["producer_slug_confidence"] != "high" and wine.get("producer_raw"):
                candidates.append((name, wine))
        parts.append("")

    # Candidate new producers (rolled up across restaurants)
    if candidates:
        by_producer: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        for r, w in candidates:
            by_producer[w["producer_raw"]].append((r, w))

        parts.append("## Candidate new producers")
        parts.append("")
        parts.append(
            f"Producers that appeared as new arrivals but don't match any "
            f"existing vault page. **{len(by_producer)} unique candidates.** "
            f"Triage with Evan's curation filters (see CLAUDE.md) and onboard "
            f"keepers with a new `wiki/producers/<slug>.md`.")
        parts.append("")
        parts.append("| Producer | Suggested slug | Seen at | Sample cuvée |")
        parts.append("|---|---|---|---|")
        for producer in sorted(by_producer):
            sightings = by_producer[producer]
            venues = ", ".join(sorted({r for r, _ in sightings}))
            sample = sightings[0][1]
            cuvee = sample.get("cuvee") or sample.get("raw_text", "")[:60]
            slug = sample.get("producer_slug", "")
            parts.append(f"| {producer} | `{slug}` | {venues} | {cuvee} |")
        parts.append("")

    # Footer
    parts.append("---")
    parts.append("")
    parts.append("Generated by `scripts/build_wine_list_view.py`. "
                 "Source data: `build/wine_list_arrivals_" + week + ".json`. "
                 "Sources: `raw/wine_lists/*/snapshot_*.json`.")
    parts.append("")

    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--week", help="Week tag YYYY-WW (default: latest).")
    ap.add_argument("--apply", action="store_true",
                    help="Write the .md files (default: dry-run, print only).")
    args = ap.parse_args()

    if args.week:
        path = BUILD_DIR / f"wine_list_arrivals_{args.week}.json"
        if not path.exists():
            print(f"ERROR: {path.relative_to(VAULT)} doesn't exist. "
                  f"Run scripts/diff_wine_lists.py --apply first.",
                  file=sys.stderr)
            return 1
    else:
        path = _latest_week_file()
        if not path:
            print("ERROR: no build/wine_list_arrivals_*.json found. "
                  "Run scripts/diff_wine_lists.py --apply first.", file=sys.stderr)
            return 1

    payload = json.loads(path.read_text(encoding="utf-8"))
    md = _render(payload)
    week = payload["week"]

    print(f"Rendered {len(md):,} bytes for week {week}")
    archive_path = VIEWS_DIR / f"wine_list_arrivals_{week}.md"
    latest_path = VIEWS_DIR / "wine_list_arrivals.md"

    if args.apply:
        VIEWS_DIR.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(md, encoding="utf-8")
        latest_path.write_text(md, encoding="utf-8")
        print(f"  wrote {archive_path.relative_to(VAULT)}")
        print(f"  wrote {latest_path.relative_to(VAULT)}")
    else:
        print(f"  (dry-run; pass --apply to write "
              f"{archive_path.relative_to(VAULT)} + "
              f"{latest_path.relative_to(VAULT)})")
        print()
        print(md[:2000] + ("…" if len(md) > 2000 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
