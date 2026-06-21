"""
Build Vinolist _views rollups from all restaurant JSONs (+ momentum snapshots).

Generates one keeper view, wiki/_views/vinolist_rollup_<YYYY_MM>.md, with:
  - Top producers by list_count (somm-demand popularity / prestige)
  - Price-floor table (cheapest NYC by-the-bottle entry per producer)
  - Momentum (risers / new entrants vs. the prior snapshot, if one exists)
  - Discovery / gap candidates (producers not in the vault), taste-flagged

Reads the same raw/vinolist/restaurants/*.json the compiler reads, and the
raw/vinolist/snapshots/ for momentum. Marks each producer ✓ (in vault) or ·
(gap) using the shared matcher.

Idempotent. Dry-run by default; --apply writes the view. After --apply, re-run
scripts/build_views_index.py to refresh the catalog.

Usage:
    python scripts/build_vinolist_rollups.py raw/vinolist/restaurants/*.json
    python scripts/build_vinolist_rollups.py raw/vinolist/restaurants/*.json --apply
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from compile_vinolist_signals import (
    aggregate, latest_prior_snapshot,
)
from compile_wb_signals import build_slug_index, match_path

VAULT = Path(__file__).resolve().parent.parent
VIEWS = VAULT / "wiki" / "_views"


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def build(sources: list[Path], top_n: int = 50) -> str:
    by_producer, restaurants = aggregate(sources)
    today = _today()

    prior = latest_prior_snapshot(today)
    pc = (prior or {}).get("counts", {})
    for name, v in by_producer.items():
        if name in pc:
            v["momentum"] = v["list_count"] - pc[name]

    exact, cidx = build_slug_index()
    in_vault: dict[str, bool] = {}
    for name in by_producer:
        path, _ = match_path(name, exact, cidx)
        in_vault[name] = path is not None

    ranked = sorted(by_producer.items(),
                    key=lambda x: (-x[1]["list_count"],
                                   x[1].get("price_floor") or 1e9))

    L: list[str] = [
        "---", "type: view", f"updated: {today}",
        'question: "Across the ingested NYC restaurant lists (Vinolist), which '
        'producers carry the most somm demand, at what price floor, and which '
        'are rising — and which are vault gaps?"',
        f"scope: {len(restaurants)} NYC restaurant list(s) via vinolistnyc.com",
        "source: vinolist",
        "generator: scripts/build_vinolist_rollups.py",
        "---", "",
        f"# Vinolist rollup — NYC restaurant demand ({today})", "",
        f"Aggregated **{len(restaurants)} list(s)** → **{len(by_producer)} "
        "distinct producers**. `list_count` = # of NYC lists pouring the producer "
        "(popularity / prestige proxy); **floor** = cheapest by-the-bottle entry "
        "across those lists. ✓ = in vault · · = gap candidate. "
        "Regenerate with `build_vinolist_rollups.py --apply`.", "",
        "## Restaurants ingested", "",
        "| Restaurant | Tier | Bottles | Wines indexed |", "|---|---|---|---|",
    ]
    counts_by_r = {r["slug"]: 0 for r in restaurants}
    for src in sources:
        d = json.loads(Path(src).read_text(encoding="utf-8"))
        counts_by_r[d["restaurant"]["slug"]] = len(d.get("wines", []))
    for r in restaurants:
        L.append(f"| {r.get('name', r['slug'])} | {r.get('tier', '—')} | "
                 f"{r.get('bottle_count') or '—'} | {counts_by_r[r['slug']]} |")
    L += ["",
          f"## Top {top_n} by list-count (somm demand)", "",
          "| # | Lists | Prestige | Floor $ | Median $ | Producer | In vault |",
          "|---|---|---|---|---|---|---|"]
    for i, (name, p) in enumerate(ranked[:top_n], 1):
        mark = "✓" if in_vault[name] else "·"
        L.append(f"| {i} | {p['list_count']} | {len(p['prestige_lists'])} | "
                 f"{p['price_floor'] or '—'} | {p['price_median'] or '—'} | "
                 f"{name} | {mark} |")

    risers = sorted(((n, v) for n, v in by_producer.items()
                     if v.get("momentum")),
                    key=lambda x: -x[1]["momentum"])
    if risers:
        L += ["", "## Momentum (Δ list-count vs prior snapshot)", "",
              f"Versus snapshot **{prior.get('snapshot_date')}**.", "",
              "| Δ | Lists now | Producer | In vault |", "|---|---|---|---|"]
        for name, v in risers[:30]:
            if v["momentum"] == 0:
                continue
            sign = f"+{v['momentum']}" if v["momentum"] > 0 else str(v["momentum"])
            mark = "✓" if in_vault[name] else "·"
            L.append(f"| {sign} | {v['list_count']} | {name} | {mark} |")

    gaps = [(n, p) for n, p in ranked if not in_vault[n]]
    L += ["", f"## Discovery / gap candidates ({len(gaps)})", "",
          "Producers poured across NYC lists but not yet in the vault — ranked by "
          "demand. Onboard keepers via per-producer LLM passes (verify farming + "
          "critic coverage; don't bulk-create from a single source).", "",
          "| Lists | Prestige | Floor $ | Producer |", "|---|---|---|---|"]
    for name, p in gaps[:80]:
        L.append(f"| {p['list_count']} | {len(p['prestige_lists'])} | "
                 f"{p['price_floor'] or '—'} | {name} |")

    L += ["", "## Sources", "",
          "- [Vinolist NYC](https://vinolistnyc.com/) restaurant lists "
          f"(ingested JSON under `raw/vinolist/restaurants/`).", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--top-n", type=int, default=50)
    args = ap.parse_args()

    md = build([Path(s) for s in args.sources], top_n=args.top_n)
    today = _today()
    out = VIEWS / f"vinolist_rollup_{today[:7].replace('-', '_')}.md"
    if not args.apply:
        print(md[:2000])
        print(f"\n... dry-run. --apply writes {out} "
              "(then run build_views_index.py).")
        return 0
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out}")
    print("Next: python scripts/build_views_index.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
