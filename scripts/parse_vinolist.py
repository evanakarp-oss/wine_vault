"""
Parse a saved Vinolist restaurant page (or a manual paste) → contract JSON.

Two inputs supported:

  1. <slug>.raw.html  — saved by scrape_vinolist.py. Re-runs the same HTML
     extraction strategies (no network), so you can iterate on selectors
     without re-fetching.

  2. <slug>.raw.md    — a MANUAL PASTE, one wine per line. This is the
     today-workflow while the live scraper is unvalidated / the host is
     egress-blocked. Accepted line formats (whitespace-tolerant):

        Producer | Cuvée | Region | Vintage | $Price | color
        Producer — Cuvée, Region 2018 .... $125
        Producer, Cuvée .... 125

     Only the producer is required; everything else is best-effort. Lines
     beginning with '#' are treated as comments. A line of the form
     `@key: value` sets restaurant metadata (name, tier, borough,
     wine_director, bottle_count, price_min, price_max).

Output: raw/vinolist/restaurants/<slug>.json in the data-contract shape
(see raw/vinolist/README.md). slug resolution to vault producers happens
later, in compile_vinolist_signals.py — this step leaves `slug: null`.

Usage:
    python scripts/parse_vinolist.py raw/vinolist/restaurants/terroir.raw.md \\
        --name "Terroir Tribeca" --tier grower_champagne \\
        --wine-director "Paul Grieco"
    python scripts/parse_vinolist.py raw/vinolist/restaurants/emp.raw.html \\
        --name "Eleven Madison Park" --tier grand_cellar
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Reuse the HTML strategies + helpers from the scraper (same directory).
import scrape_vinolist as sv

VAULT = Path(__file__).resolve().parent.parent
OUT_DIR = VAULT / "raw" / "vinolist" / "restaurants"
VALID_TIERS = sv.VALID_TIERS
COLORS = sv.COLORS


def _now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def parse_paste_line(line: str) -> dict | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # price (last $-amount, or a trailing bare number)
    price = None
    pm = re.findall(r"\$\s?(\d[\d,]*)", line)
    if pm:
        price = int(pm[-1].replace(",", ""))
        line = re.sub(r"\$\s?\d[\d,]*\s*$", "", line).strip(" .\t")
    else:
        bm = re.search(r"(?:\.{2,}|\s{2,}|\t)\s*(\d{2,4})\s*$", line)
        if bm:
            price = int(bm.group(1))
            line = line[:bm.start()].strip(" .\t")

    # vintage (a 19xx/20xx token)
    vintage = None
    vm = re.search(r"\b(19\d{2}|20\d{2})\b", line)
    if vm:
        vintage = int(vm.group(1))

    # color (trailing keyword)
    color = None
    cm = re.search(r"\b(red|white|rose|rosé|sparkling|orange|fortified|dessert)\b\s*$",
                   line, re.IGNORECASE)
    if cm:
        color = sv._coerce_color(cm.group(1))
        line = line[:cm.start()].strip(" ,—-|")

    if "|" in line:
        parts = [p.strip() for p in line.split("|")]
        producer = parts[0]
        cuvee = parts[1] if len(parts) > 1 and parts[1] else None
        region = parts[2] if len(parts) > 2 and parts[2] else None
    else:
        # split producer from the rest on the first em/en dash or comma
        m = re.split(r"\s+[—–-]\s+|,\s+", line, maxsplit=1)
        producer = m[0].strip()
        cuvee = m[1].strip(" ,") if len(m) > 1 and m[1].strip() else None
        region = None

    if not producer:
        return None
    return {
        "raw_producer": producer, "slug": None, "cuvee": cuvee or None,
        "region": region, "vintage": vintage, "price": price, "color": color,
    }


def parse_paste(text: str) -> tuple[list[dict], dict]:
    wines, meta = [], {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("@"):
            mk = re.match(r"@(\w+)\s*:\s*(.+)", s)
            if mk:
                meta[mk.group(1)] = mk.group(2).strip()
            continue
        w = parse_paste_line(line)
        if w:
            wines.append(w)
    return wines, meta


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="<slug>.raw.html or <slug>.raw.md")
    ap.add_argument("--slug", help="Override output slug (default: from filename)")
    ap.add_argument("--name")
    ap.add_argument("--tier", choices=VALID_TIERS, default="grower_french")
    ap.add_argument("--borough", default="Manhattan")
    ap.add_argument("--wine-director", default=None)
    ap.add_argument("--url", default=None)
    args = ap.parse_args()

    src = Path(args.input)
    text = src.read_text(encoding="utf-8")
    slug = args.slug or re.sub(r"\.(raw\.html|raw\.md|html|md)$", "", src.name)

    file_meta: dict = {}
    if src.suffix == ".html" or src.name.endswith(".raw.html"):
        wines, strategy = sv.extract_wines(text)
        file_meta = sv.extract_meta(text)
        method = f"html_reparse:{strategy}"
    else:
        wines, paste_meta = parse_paste(text)
        file_meta = paste_meta
        method = "manual_paste_v1"

    if not wines:
        print(f"No wines parsed from {src.name}. "
              "If HTML, tune extract_wines() in scrape_vinolist.py; "
              "if paste, check the line format in the module docstring.")
        return 1

    def mi(key):
        v = file_meta.get(key)
        return int(v) if v is not None and str(v).strip().isdigit() else None

    payload = {
        "restaurant": {
            "slug": slug,
            "name": args.name or file_meta.get("name")
            or file_meta.get("page_title", slug),
            "url": args.url or file_meta.get("url"),
            "borough": file_meta.get("borough", args.borough),
            "tier": file_meta.get("tier", args.tier),
            "bottle_count": mi("bottle_count"),
            "price_min": mi("price_min"),
            "price_max": mi("price_max"),
            "wine_director": file_meta.get("wine_director") or args.wine_director,
            "scraped_at": _now_date(),
            "scrape_method": method,
        },
        "wines": wines,
    }
    out = OUT_DIR / f"{slug}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"Wrote {out}  ({len(wines)} wines, method={method})")
    print(f"\nNext: python scripts/compile_vinolist_signals.py {out}  "
          "# add --apply to write producer pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
