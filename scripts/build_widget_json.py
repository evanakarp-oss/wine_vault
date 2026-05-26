"""
build_widget_json.py — emit `build/widget_data.json` from the vault.

Single source of truth for the React widget that currently reads
hardcoded arrays in `dte_wines_1.jsx`. After this lands, the JSX
fetches widget_data.json instead.

Output shape (see `wiki/_SCHEMA.md` → "## Derived JSON"):

  {
    "generated": "2026-05-26T11:45:00Z",
    "producer_count": 368,
    "cellar_bottle_count": 631,
    "producers": [
      {
        "slug": "laurent_barth",
        "name": "Laurent Barth",
        "country": "France",
        "region": "Alsace",
        "sub_region": "Bennwihr",
        "farming": ["biodynamic", "natural"],
        "importer_us": ["Jenny & François"],
        "retailers": {
          "chambers":   {"championed": true, "article_count": 4, ...},
          "dte":        {"in_portfolio": true, "cuvee_count": 3, ...},
          "raeders":    {"in_portfolio": false, ...},
          "fass":       {"in_portfolio": false, ...}
        },
        "cellar_bottles": 2,
        "cellar_cuvees":  1
      },
      ...
    ],
    "wines": [
      {
        "producer_slug": "laurent_barth",
        "cuvee": "Gewurztraminer Kitterlé Grand Cru",
        "vintage": "2019",
        "quantity": 2,
        "purchase_price_usd": 35,
        "source_retailer": "dte",
        "drink_window_start": 2028,
        "drink_window_end":   2035,
        "location": "NYC closet"
      },
      ...
    ]
  }

Pure stdlib. Idempotent. Run after `lint.py` is clean.

Usage:
    python scripts/build_widget_json.py
    python scripts/build_widget_json.py --check    # exit 1 if regen differs
    python scripts/build_widget_json.py --pretty   # indent for readability
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
CELLAR = VAULT / "cellar"
OUTPUT = VAULT / "build" / "widget_data.json"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
LIST_INLINE_RE = re.compile(r'^([a-z_]+):\s*\[(.*?)\]\s*$', re.MULTILINE)
LIST_MULTI_RE = re.compile(r'^([a-z_]+):\s*$\n((?:- [^\n]*\n)+)', re.MULTILINE)


def split_fm(text: str):
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def fm_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip().strip("'") if m else ""


def fm_list(fm: str, key: str) -> list[str]:
    """Handle both `key: [a, b]` and multi-line `key:\\n- a\\n- b`."""
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return []
        out = []
        for part in re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', inner):
            v = next((x for x in part if x), "").strip()
            if v:
                out.append(v)
        return out
    m = re.search(rf'^{re.escape(key)}:\s*$\n((?:- [^\n]*\n)+)', fm, re.MULTILINE)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        v = line.lstrip("- ").strip().strip('"\'')
        if v:
            out.append(v)
    return out


def fm_block_bool(fm: str, block: str, key: str) -> bool:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(true|false)"
    m = re.search(pat, fm, re.MULTILINE)
    return bool(m) and m.group(1) == "true"


def fm_block_int(fm: str, block: str, key: str) -> int:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(\d+)"
    m = re.search(pat, fm, re.MULTILINE)
    return int(m.group(1)) if m else 0


def producer_to_dict(p: Path) -> dict | None:
    text = p.read_text(encoding="utf-8", errors="replace")
    parts = split_fm(text)
    if not parts:
        return None
    fm, _ = parts
    if fm_str(fm, "type") != "producer":
        return None
    return {
        "slug":         fm_str(fm, "slug") or p.stem,
        "name":         fm_str(fm, "name"),
        "country":      fm_str(fm, "country"),
        "region":       fm_str(fm, "region"),
        "sub_region":   fm_str(fm, "sub_region"),
        "farming":      fm_list(fm, "farming"),
        "importer_us":  fm_list(fm, "importer_us"),
        "retailers": {
            "chambers": {
                "championed":      fm_block_bool(fm, "chambers", "championed"),
                "article_count":   fm_block_int(fm, "chambers", "article_count"),
                "dedicated_count": fm_block_int(fm, "chambers", "dedicated_count"),
                "first_year":      fm_block_int(fm, "chambers", "first_year"),
                "last_year":       fm_block_int(fm, "chambers", "last_year"),
            },
            "dte": {
                "in_portfolio":  fm_block_bool(fm, "dte", "in_portfolio"),
                "cuvee_count":   fm_block_int(fm, "dte", "cuvee_count"),
                "price_min":     fm_block_int(fm, "dte", "price_min"),
                "price_max":     fm_block_int(fm, "dte", "price_max"),
            },
            "raeders": {
                "in_portfolio":  fm_block_bool(fm, "raeders", "in_portfolio"),
                "cuvee_count":   fm_block_int(fm, "raeders", "cuvee_count"),
            },
            "fass": {
                "in_portfolio":  fm_block_bool(fm, "fass", "in_portfolio"),
                "cuvee_count":   fm_block_int(fm, "fass", "cuvee_count"),
            },
        },
    }


def cellar_to_dict(p: Path) -> dict | None:
    text = p.read_text(encoding="utf-8", errors="replace")
    parts = split_fm(text)
    if not parts:
        return None
    fm, _ = parts
    if fm_str(fm, "type") != "cellar_entry":
        return None
    qty_m = re.search(r"^quantity:\s*(\d+)", fm, re.MULTILINE)
    price_m = re.search(r"^purchase_price_usd:\s*(\d+(?:\.\d+)?)", fm, re.MULTILINE)
    dws_m = re.search(r"^drink_window_start:\s*(\d+)", fm, re.MULTILINE)
    dwe_m = re.search(r"^drink_window_end:\s*(\d+)", fm, re.MULTILINE)
    return {
        "producer_slug":      fm_str(fm, "producer_slug"),
        "cuvee":              fm_str(fm, "cuvee"),
        "vintage":            fm_str(fm, "vintage"),
        "bottle_size":        fm_str(fm, "bottle_size") or "750ml",
        "quantity":           int(qty_m.group(1)) if qty_m else 0,
        "purchase_price_usd": float(price_m.group(1)) if price_m else 0.0,
        "source_retailer":    fm_str(fm, "source_retailer"),
        "drink_window_start": int(dws_m.group(1)) if dws_m else 0,
        "drink_window_end":   int(dwe_m.group(1)) if dwe_m else 0,
        "location":           fm_str(fm, "location"),
    }


def build() -> dict:
    producers: list[dict] = []
    for p in sorted(PRODUCERS.glob("*.md")):
        d = producer_to_dict(p)
        if d:
            producers.append(d)

    wines: list[dict] = []
    bottles_by_slug: dict[str, int] = {}
    cuvees_by_slug: dict[str, int] = {}
    for p in sorted(CELLAR.glob("*.md")):
        d = cellar_to_dict(p)
        if d and d["producer_slug"]:
            wines.append(d)
            bottles_by_slug[d["producer_slug"]] = (
                bottles_by_slug.get(d["producer_slug"], 0) + d["quantity"]
            )
            cuvees_by_slug[d["producer_slug"]] = (
                cuvees_by_slug.get(d["producer_slug"], 0) + 1
            )

    for prod in producers:
        prod["cellar_bottles"] = bottles_by_slug.get(prod["slug"], 0)
        prod["cellar_cuvees"] = cuvees_by_slug.get(prod["slug"], 0)

    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "producer_count": len(producers),
        "cellar_bottle_count": sum(w["quantity"] for w in wines),
        "cellar_cuvee_count": len(wines),
        "producers": producers,
        "wines": wines,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="Exit 1 if regen differs from existing widget_data.json.")
    ap.add_argument("--pretty", action="store_true",
                    help="Indent JSON for readability (larger file).")
    args = ap.parse_args()

    data = build()
    # `generated` flips every run — exclude from --check diff
    if args.check:
        if not OUTPUT.exists():
            print(f"ERROR: {OUTPUT} not found. Run without --check to build.",
                  file=sys.stderr)
            return 1
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        for d in (data, existing):
            d.pop("generated", None)
        if existing != data:
            print(f"FAIL: {OUTPUT} is stale. Run scripts/build_widget_json.py.",
                  file=sys.stderr)
            return 1
        print(f"OK: {OUTPUT.name} matches current vault state.", file=sys.stderr)
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if args.pretty else None
    text = json.dumps(data, ensure_ascii=False, indent=indent, sort_keys=False)
    OUTPUT.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(text):,} chars, "
          f"{data['producer_count']} producers, "
          f"{data['cellar_bottle_count']} cellar bottles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
