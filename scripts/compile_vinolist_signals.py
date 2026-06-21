"""
Aggregate Vinolist restaurant lists → per-producer community.vinolist frontmatter.

Reads one or more raw/vinolist/restaurants/<slug>.json files, aggregates each
producer across every restaurant, and upserts a `community.vinolist` block on
the matching wiki/producers/<slug>.md:

    community:
      vinolist:
        list_count: 7                 # distinct restaurants pouring this producer
        prestige_lists: [eleven_madison_park, le_bernardin]   # grand_cellar tiers
        price_floor: 95               # lowest bottle price across lists (USD)
        price_median: 180             # median bottle price across lists (USD)
        momentum_2026: 2              # Δ list_count vs the prior dated snapshot
        last_updated: 2026-06-21

Momentum: this script also writes a dated snapshot of per-producer list_counts
to raw/vinolist/snapshots/producers_<YYYY-MM-DD>.json, and computes
`momentum_<year>` against the most recent EARLIER snapshot (null until a second
snapshot exists).

Matching reuses the slug resolver from compile_wb_signals.py (strip
Domaine/Château/etc., compact-alphanumeric fallback). Unmatched producers are
NOT auto-created (single-source anti-pattern) — they're listed in
build/vinolist_signals_report.md as discovery/gap candidates.

Usage:
    python scripts/compile_vinolist_signals.py raw/vinolist/restaurants/*.json
    python scripts/compile_vinolist_signals.py raw/vinolist/restaurants/*.json --apply
    python scripts/compile_vinolist_signals.py ... --no-snapshot   # skip momentum write
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Reuse the validated matcher + frontmatter splitter.
from compile_wb_signals import (
    build_slug_index, match_path, split_frontmatter, slug_candidates,
)

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
SNAP_DIR = VAULT / "raw" / "vinolist" / "snapshots"
REPORT = VAULT / "build" / "vinolist_signals_report.md"


def _now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _now_seconds() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ----------------------------------------------------------- aggregation --

def aggregate(sources: list[Path]) -> tuple[dict[str, dict], list[dict]]:
    """Return (by_producer, restaurants). by_producer keyed on raw_producer."""
    restaurants: list[dict] = []
    # raw_producer -> {restaurants:set, prestige:set, prices:list}
    agg: dict[str, dict] = defaultdict(
        lambda: {"restaurants": set(), "prestige": set(), "prices": []})

    for src in sources:
        data = json.loads(src.read_text(encoding="utf-8"))
        r = data["restaurant"]
        restaurants.append(r)
        rslug = r["slug"]
        is_prestige = r.get("tier") == "grand_cellar"
        for w in data.get("wines", []):
            name = (w.get("raw_producer") or "").strip()
            if not name:
                continue
            a = agg[name]
            a["restaurants"].add(rslug)
            if is_prestige:
                a["prestige"].add(rslug)
            if w.get("price") is not None:
                a["prices"].append(int(w["price"]))

    by_producer: dict[str, dict] = {}
    for name, a in agg.items():
        prices = sorted(a["prices"])
        by_producer[name] = {
            "list_count": len(a["restaurants"]),
            "prestige_lists": sorted(a["prestige"]),
            "price_floor": prices[0] if prices else None,
            "price_median": int(statistics.median(prices)) if prices else None,
        }
    return by_producer, restaurants


# -------------------------------------------------------------- momentum --

def latest_prior_snapshot(today: str) -> dict | None:
    if not SNAP_DIR.exists():
        return None
    snaps = sorted(p for p in SNAP_DIR.glob("producers_*.json")
                   if p.stem.replace("producers_", "") < today)
    if not snaps:
        return None
    return json.loads(snaps[-1].read_text(encoding="utf-8"))


def write_snapshot(by_producer: dict[str, dict], today: str) -> Path:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "snapshot_date": today,
        "generated": _now_seconds(),
        "counts": {n: v["list_count"] for n, v in by_producer.items()},
    }
    out = SNAP_DIR / f"producers_{today}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    return out


# ------------------------------------------------ frontmatter upsert ------
# community.vinolist is a flat block (no per-thread nesting like berserkers).

def _render_vinolist_yaml(payload: dict, year: int, base_indent: int) -> list[str]:
    pad = " " * base_indent
    out = [f"{pad}vinolist:"]
    p2 = " " * (base_indent + 2)
    out.append(f"{p2}list_count: {payload['list_count']}")
    pl = payload.get("prestige_lists") or []
    out.append(f"{p2}prestige_lists: [{', '.join(pl)}]" if pl
               else f"{p2}prestige_lists: null")
    for k in ("price_floor", "price_median"):
        v = payload.get(k)
        out.append(f"{p2}{k}: {v if v is not None else 'null'}")
    mom = payload.get("momentum")
    out.append(f"{p2}momentum_{year}: {mom if mom is not None else 'null'}")
    out.append(f"{p2}last_updated: {_now_date()}")
    return out


def upsert_vinolist_block(fm: str, payload: dict, year: int) -> tuple[str, str]:
    """Insert/replace community.vinolist. Returns (new_fm, action)."""
    lines = fm.split("\n")

    def find(pat: re.Pattern) -> int:
        for i, ln in enumerate(lines):
            if pat.match(ln):
                return i
        return -1

    def block_end(idx: int, indent: int) -> int:
        end = len(lines)
        for j in range(idx + 1, len(lines)):
            if not lines[j].strip():
                continue
            if len(lines[j]) - len(lines[j].lstrip(" ")) <= indent:
                end = j
                break
        return end

    new_block = _render_vinolist_yaml(payload, year, base_indent=2)

    cidx = find(re.compile(r"^community:\s*$", re.MULTILINE))
    if cidx == -1:
        insert_at = len(lines)
        for i, ln in enumerate(lines):
            if ln.startswith("_sources:") or ln.startswith("tags:"):
                insert_at = i
                break
        block = ["community:"] + new_block
        lines = lines[:insert_at] + block + lines[insert_at:]
        return "\n".join(lines), "added"

    cend = block_end(cidx, indent=0)
    vidx = -1
    for j in range(cidx + 1, cend):
        if re.match(r"^  vinolist:\s*$", lines[j]):
            vidx = j
            break
    if vidx == -1:
        lines = lines[:cidx + 1] + new_block + lines[cidx + 1:]
        return "\n".join(lines), "added"

    vend = block_end(vidx, indent=2)
    if lines[vidx:vend] == new_block:
        return "\n".join(lines), "no_change"
    lines = lines[:vidx] + new_block + lines[vend:]
    return "\n".join(lines), "updated"


# -------------------------------------------------------------------- main -

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+",
                    help="raw/vinolist/restaurants/<slug>.json files")
    ap.add_argument("--apply", action="store_true", help="Write changes")
    ap.add_argument("--no-snapshot", action="store_true",
                    help="Don't write a dated momentum snapshot")
    ap.add_argument("--year", type=int, default=datetime.now().year,
                    help="Year label for the momentum_<year> field")
    args = ap.parse_args()

    paths = [Path(s) for s in args.sources]
    by_producer, restaurants = aggregate(paths)
    print(f"{len(restaurants)} restaurant(s) → {len(by_producer)} distinct producers")

    today = _now_date()
    prior = latest_prior_snapshot(today)
    if prior:
        pc = prior.get("counts", {})
        for name, v in by_producer.items():
            if name in pc:
                v["momentum"] = v["list_count"] - pc[name]
        print(f"Momentum vs snapshot {prior.get('snapshot_date')}")
    else:
        print("No prior snapshot — momentum left null (need 2 snapshots).")

    exact, cidx = build_slug_index()
    matched: dict[Path, dict] = {}
    unmatched: list[tuple[str, dict]] = []
    for name, payload in by_producer.items():
        path, hits = match_path(name, exact, cidx)
        if path:
            matched[path] = payload
        else:
            unmatched.append((name, payload))
    print(f"Matched {len(matched)} to producer pages, {len(unmatched)} unmatched")

    # ---- report ----
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rep = [
        "---", "type: signals_report", "source: vinolist",
        f'generated: "{_now_seconds()}"',
        f"restaurants: {[r['slug'] for r in restaurants]}",
        f"producers_total: {len(by_producer)}",
        f"matched: {len(matched)}", f"unmatched: {len(unmatched)}",
        f"apply_mode: {args.apply}", "---", "",
        "# Vinolist signal compile report", "",
        f"Aggregated {len(restaurants)} restaurant list(s).", "",
        "## Discovery / gap candidates (unmatched producers)", "",
        "Producers on NYC lists with no `wiki/producers/<slug>.md`. Ranked by "
        "list_count (somm demand). Onboard keepers via per-producer LLM passes "
        "(verify farming + critic coverage; don't bulk-create).", "",
        "| Lists | Prestige | Floor $ | Median $ | Producer | Tried slugs |",
        "|---|---|---|---|---|---|",
    ]
    for name, p in sorted(unmatched,
                          key=lambda x: (-x[1]["list_count"],
                                         x[1].get("price_floor") or 1e9)):
        tried = ", ".join(slug_candidates(name)[:3])
        rep.append(f"| {p['list_count']} | {len(p['prestige_lists'])} | "
                   f"{p['price_floor'] or '—'} | {p['price_median'] or '—'} | "
                   f"{name} | `{tried}` |")
    REPORT.write_text("\n".join(rep) + "\n", encoding="utf-8")
    print(f"Report: {REPORT}")

    if not args.no_snapshot and args.apply:
        snap = write_snapshot(by_producer, today)
        print(f"Snapshot: {snap}")

    if not args.apply:
        print("\nDry-run. Re-run with --apply to write producer pages + snapshot.")
        return 0

    changes = 0
    for path, payload in matched.items():
        text = path.read_text(encoding="utf-8")
        split = split_frontmatter(text)
        if not split:
            print(f"  skip (no frontmatter): {path.name}")
            continue
        fm, body = split
        fm, action = upsert_vinolist_block(fm, payload, args.year)
        if action != "no_change":
            new_text = f"---\n{fm}\n---\n{body}"
            path.write_text(new_text, encoding="utf-8")
            changes += 1
    print(f"\nApplied community.vinolist to {changes} producer page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
