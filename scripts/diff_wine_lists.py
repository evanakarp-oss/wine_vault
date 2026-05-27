"""
Diff each restaurant's latest snapshot against its previous snapshot.

For each registered source under raw/wine_lists/<slug>/snapshot_*.json:
  1. Find the two most recent snapshots (by snapshot_date in filename).
  2. Compute additions / removals keyed on (producer_slug, cuvée_norm, vintage).
  3. Emit a combined report to build/wine_list_arrivals_<YYYY-WW>.json.

The week tag (`YYYY-WW`) comes from the *latest* snapshot date across all
sources — usually they're all from the same Monday fetch, but if they're
out-of-sync the report uses the freshest week.

We surface BOTH additions and removals in the JSON (good for forensics)
but the wiki view (build_wine_list_view.py) only shows additions. New
arrivals are the actionable signal; bottle disappearing usually means it
sold through, which is interesting but noisier.

Usage:
    python scripts/diff_wine_lists.py                       # dry-run, all sources
    python scripts/diff_wine_lists.py --apply               # write build/...json
    python scripts/diff_wine_lists.py --slug estela         # one source
    python scripts/diff_wine_lists.py --since 2026-05-20    # diff vs. last snapshot before this date
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

VAULT = Path(__file__).resolve().parent.parent
RAW_ROOT = VAULT / "raw" / "wine_lists"
BUILD_DIR = VAULT / "build"

SNAPSHOT_RE = re.compile(r"^snapshot_(\d{4}-\d{2}-\d{2})\.json$")


# ─── Diff key ────────────────────────────────────────────────────────────────

def _norm_cuvee(s: str) -> str:
    """Cuvée normalization for diff keying — lowercase, collapse whitespace,
    strip parens, drop common decorations."""
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9'\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def wine_key(w: dict) -> tuple[str, str, int | None]:
    return (w.get("producer_slug", ""),
            _norm_cuvee(w.get("cuvee", "")),
            w.get("vintage"))


# ─── Snapshot discovery ──────────────────────────────────────────────────────

def _list_snapshots(slug_dir: Path) -> list[tuple[date, Path]]:
    out: list[tuple[date, Path]] = []
    for p in slug_dir.glob("snapshot_*.json"):
        m = SNAPSHOT_RE.match(p.name)
        if not m:
            continue
        try:
            d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        out.append((d, p))
    out.sort(key=lambda t: t[0])
    return out


def _pick_pair(snapshots: list[tuple[date, Path]],
               since: date | None) -> tuple[Path | None, Path | None]:
    """Return (previous, latest) — latest is the newest, previous is the
    newest strictly before latest (or before `since` if given)."""
    if not snapshots:
        return None, None
    latest_d, latest_p = snapshots[-1]
    prev_p: Path | None = None
    cutoff = since or latest_d
    for d, p in reversed(snapshots[:-1]):
        if d < cutoff:
            prev_p = p
            break
    return prev_p, latest_p


# ─── Diff one source ─────────────────────────────────────────────────────────

def diff_source(slug: str, since: date | None) -> dict:
    slug_dir = RAW_ROOT / slug
    snapshots = _list_snapshots(slug_dir)
    prev_p, latest_p = _pick_pair(snapshots, since)

    if not latest_p:
        return {"slug": slug, "status": "no_snapshots"}

    latest = json.loads(latest_p.read_text(encoding="utf-8"))

    if not prev_p:
        return {
            "slug": slug,
            "status": "first_snapshot",
            "latest_date": latest["snapshot_date"],
            "latest_count": latest.get("wine_count", len(latest.get("wines", []))),
            "added": [],
            "removed": [],
        }

    prev = json.loads(prev_p.read_text(encoding="utf-8"))
    prev_wines = {wine_key(w): w for w in prev.get("wines", [])}
    latest_wines = {wine_key(w): w for w in latest.get("wines", [])}

    added_keys = set(latest_wines) - set(prev_wines)
    removed_keys = set(prev_wines) - set(latest_wines)

    def _format(w: dict) -> dict:
        return {
            "producer_raw": w.get("producer_raw", ""),
            "producer_slug": w.get("producer_slug", ""),
            "producer_slug_confidence": w.get("producer_slug_confidence", "low"),
            "cuvee": w.get("cuvee", ""),
            "vintage": w.get("vintage"),
            "region": w.get("region", ""),
            "price_usd": w.get("price_usd"),
            "by_the_glass": w.get("by_the_glass", False),
            "section": w.get("section", ""),
            "raw_text": w.get("raw_text", ""),
        }

    return {
        "slug": slug,
        "restaurant": latest.get("restaurant", {}),
        "status": "diffed",
        "previous_date": prev["snapshot_date"],
        "latest_date": latest["snapshot_date"],
        "previous_count": len(prev_wines),
        "latest_count": len(latest_wines),
        "added": [_format(latest_wines[k]) for k in sorted(added_keys)],
        "removed": [_format(prev_wines[k]) for k in sorted(removed_keys)],
    }


# ─── Driver ──────────────────────────────────────────────────────────────────

def _registered_sources() -> list[str]:
    return sorted(p.name for p in RAW_ROOT.iterdir()
                  if p.is_dir() and (p / "source.md").exists())


def _week_tag(per_source: Iterable[dict]) -> str:
    """ISO YYYY-WW of the newest latest_date across sources, fallback today."""
    dates = [datetime.strptime(s["latest_date"], "%Y-%m-%d").date()
             for s in per_source if "latest_date" in s]
    d = max(dates) if dates else date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--slug", help="Diff only this source.")
    ap.add_argument("--since",
                    help="Compare latest against the newest snapshot strictly "
                         "before this date (YYYY-MM-DD). Default: pairs the "
                         "two most recent snapshots per source.")
    ap.add_argument("--apply", action="store_true",
                    help="Write build/wine_list_arrivals_<YYYY-WW>.json "
                         "(default: dry-run, print summary only).")
    args = ap.parse_args()

    since = (datetime.strptime(args.since, "%Y-%m-%d").date()
             if args.since else None)
    targets = [args.slug] if args.slug else _registered_sources()

    per_source = [diff_source(s, since) for s in targets]
    week = _week_tag(per_source)

    total_added = sum(len(s.get("added", [])) for s in per_source)
    total_removed = sum(len(s.get("removed", [])) for s in per_source)
    print(f"Week {week}: {total_added} additions, {total_removed} removals "
          f"across {len(per_source)} sources")
    for s in per_source:
        if s["status"] == "no_snapshots":
            print(f"  [{s['slug']}] no snapshots yet")
        elif s["status"] == "first_snapshot":
            print(f"  [{s['slug']}] first snapshot "
                  f"({s['latest_date']}, {s['latest_count']} wines) — "
                  f"no prior to diff")
        else:
            print(f"  [{s['slug']}] {s['previous_date']} → {s['latest_date']}: "
                  f"+{len(s['added'])} / -{len(s['removed'])} "
                  f"({s['previous_count']} → {s['latest_count']})")

    out = BUILD_DIR / f"wine_list_arrivals_{week}.json"
    payload = {
        "week": week,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "totals": {"added": total_added, "removed": total_removed},
        "by_source": per_source,
    }
    if args.apply:
        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        print(f"\nWrote {out.relative_to(VAULT)}")
    else:
        print(f"\n(dry-run; pass --apply to write {out.relative_to(VAULT)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
