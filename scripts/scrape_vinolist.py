"""
Scrape a Vinolist NYC restaurant wine list into raw HTML + (best-effort) JSON.

Vinolist NYC (https://vinolistnyc.com/) aggregates NYC *restaurant* wine lists.
Each restaurant has a page at /restaurant/<slug>. The site 403s naive fetchers
and is egress-blocked from the Claude-Code-on-web sandbox, so THIS SCRIPT IS
MEANT TO RUN LOCALLY ON EVAN'S MACHINE, not in a web session.

It does three things, in order, and is deliberately defensive because the live
page structure hasn't been validated against this code yet:

  1. Fetch the page with a real browser User-Agent + Accept headers (+ retries
     with exponential backoff). Always save the raw HTML to
     raw/vinolist/restaurants/<slug>.raw.html  (durable provenance).
  2. Try to auto-extract structured wine rows from the HTML using several
     strategies (Next.js __NEXT_DATA__, JSON-LD, a generic embedded JSON blob,
     then an HTML <table> fallback). If any strategy yields rows, write
     raw/vinolist/restaurants/<slug>.json in the data-contract shape.
  3. If auto-extraction finds nothing, leave only the .raw.html and tell the
     user to run parse_vinolist.py against it (or hand-tune the selectors).

⚠️ First-run reality: the extraction selectors below are best-guesses. After the
first successful HTML fetch, inspect <slug>.raw.html, then either (a) adjust
`extract_wines()` here, or (b) parse via parse_vinolist.py. The .raw.html is the
source of truth either way — re-parsing never re-hits the network.

Usage (local):
    python scripts/scrape_vinolist.py \\
        https://www.vinolistnyc.com/restaurant/eleven-madison-park \\
        --tier grand_cellar
    python scripts/scrape_vinolist.py --slug terroir_tribeca \\
        https://www.vinolistnyc.com/restaurant/terroir ... --tier grower_champagne

Pass --tier (grand_cellar|grower_champagne|grower_french|italian_deepcut|
natural_bar) so the compiler can flag prestige lists. --throttle to be polite.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
OUT_DIR = VAULT / "raw" / "vinolist" / "restaurants"

# A real browser UA is required — the site 403s tool/library UAs.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
}

VALID_TIERS = ("grand_cellar", "grower_champagne", "grower_french",
               "italian_deepcut", "natural_bar")
COLORS = {"red", "white", "rose", "rosé", "sparkling", "orange",
          "fortified", "dessert"}


def _now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def slug_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    leaf = path.rsplit("/", 1)[-1]
    return re.sub(r"[^a-z0-9]+", "_", leaf.lower()).strip("_")


def fetch_html(url: str, throttle: float = 1.0, retries: int = 4) -> str:
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            last_err = e
            wait = throttle * (2 ** attempt)
            print(f"  attempt {attempt+1}/{retries} failed ({e}); "
                  f"sleeping {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Could not fetch {url}: {last_err}")


# ------------------------------------------------------------- extraction --
# Several strategies, tried in order. Each returns a list of wine dicts or [].

def _coerce_price(val) -> int | None:
    if val is None:
        return None
    m = re.search(r"\d[\d,]*", str(val))
    return int(m.group(0).replace(",", "")) if m else None


def _coerce_color(val) -> str | None:
    if not val:
        return None
    v = str(val).strip().lower()
    if v in ("rosé",):
        return "rose"
    return v if v in COLORS else None


def _wine_from_obj(o: dict) -> dict | None:
    """Map a loosely-shaped dict (from embedded JSON) to a contract wine row."""
    if not isinstance(o, dict):
        return None
    producer = (o.get("producer") or o.get("winery") or o.get("domaine")
                or o.get("maker") or o.get("brand"))
    name = o.get("name") or o.get("wine") or o.get("title") or o.get("cuvee")
    if not producer and not name:
        return None
    return {
        "raw_producer": (producer or name or "").strip(),
        "slug": None,
        "cuvee": (o.get("cuvee") or (name if producer else None)),
        "region": o.get("region") or o.get("appellation") or None,
        "vintage": _coerce_price(o.get("vintage")) if o.get("vintage") else None,
        "price": _coerce_price(o.get("price") or o.get("bottlePrice")
                               or o.get("price_bottle")),
        "color": _coerce_color(o.get("color") or o.get("type")),
    }


def _walk_for_wines(node, found: list[dict]) -> None:
    """Recursively scan parsed JSON for objects that look like wine rows."""
    if isinstance(node, dict):
        w = _wine_from_obj(node)
        if w and (w["price"] is not None or w["cuvee"] or w["region"]):
            found.append(w)
        for v in node.values():
            _walk_for_wines(v, found)
    elif isinstance(node, list):
        for v in node:
            _walk_for_wines(v, found)


def _try_embedded_json(html: str) -> list[dict]:
    rows: list[dict] = []
    # Next.js
    for m in re.finditer(
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            _walk_for_wines(json.loads(m.group(1)), rows)
        except json.JSONDecodeError:
            pass
    # JSON-LD blocks
    for m in re.finditer(
            r'<script[^>]*type="application/(?:ld\+json|json)"[^>]*>(.*?)</script>',
            html, re.DOTALL):
        try:
            _walk_for_wines(json.loads(m.group(1)), rows)
        except json.JSONDecodeError:
            pass
    return rows


def _try_table(html: str) -> list[dict]:
    """Fallback: parse the first plausible <table> of wines."""
    rows: list[dict] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE):
        cells = [re.sub(r"<[^>]+>", "", c).strip()
                 for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",
                                     tr, re.DOTALL | re.IGNORECASE)]
        cells = [c for c in cells if c]
        if not cells:
            continue
        price = next((_coerce_price(c) for c in cells
                      if re.search(r"\$\s?\d", c)), None)
        producer = cells[0]
        if producer and (price is not None or len(cells) >= 2):
            rows.append({
                "raw_producer": producer, "slug": None,
                "cuvee": cells[1] if len(cells) > 1 else None,
                "region": None, "vintage": None, "price": price, "color": None,
            })
    return rows


def extract_wines(html: str) -> tuple[list[dict], str]:
    for strategy, fn in (("embedded_json", _try_embedded_json),
                         ("html_table", _try_table)):
        rows = fn(html)
        # de-dup on (producer, cuvee, vintage, price)
        seen, uniq = set(), []
        for r in rows:
            key = (r["raw_producer"], r.get("cuvee"), r.get("vintage"),
                   r.get("price"))
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        if len(uniq) >= 5:
            return uniq, strategy
    return [], "none"


def extract_meta(html: str) -> dict:
    out: dict = {}
    mt = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if mt:
        out["page_title"] = re.sub(r"\s+", " ", mt.group(1)).strip()
    mb = re.search(r"(\d[\d,]*)\s*bottles", html, re.IGNORECASE)
    if mb:
        out["bottle_count"] = int(mb.group(1).replace(",", ""))
    prices = [int(p.replace(",", ""))
              for p in re.findall(r"\$\s?(\d[\d,]*)", html)]
    if prices:
        out["price_min"], out["price_max"] = min(prices), max(prices)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="Vinolist restaurant URL (/restaurant/<slug>)")
    ap.add_argument("--slug", help="Override output filename slug")
    ap.add_argument("--name", help="Restaurant display name")
    ap.add_argument("--tier", choices=VALID_TIERS, default="grower_french")
    ap.add_argument("--borough", default="Manhattan")
    ap.add_argument("--wine-director", default=None)
    ap.add_argument("--throttle", type=float, default=1.0)
    args = ap.parse_args()

    slug = args.slug or slug_from_url(args.url)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        html = fetch_html(args.url, throttle=args.throttle)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nFallback: open the page in a browser, save the HTML to "
              f"{OUT_DIR / (slug + '.raw.html')}, or paste the list into "
              f"{OUT_DIR / (slug + '.raw.md')} (see parse_vinolist.py), "
              "then run parse_vinolist.py.", file=sys.stderr)
        return 2

    raw_path = OUT_DIR / f"{slug}.raw.html"
    raw_path.write_text(html, encoding="utf-8")
    print(f"Saved raw HTML → {raw_path} ({len(html):,} bytes)")

    meta = extract_meta(html)
    wines, strategy = extract_wines(html)
    print(f"Extraction strategy: {strategy} → {len(wines)} wine rows")

    if not wines:
        print("\nNo rows auto-extracted. Inspect the raw HTML and either tune "
              "extract_wines() here or run:\n"
              f"  python scripts/parse_vinolist.py {raw_path} --tier {args.tier}")
        return 0

    payload = {
        "restaurant": {
            "slug": slug,
            "name": args.name or meta.get("page_title", slug),
            "url": args.url,
            "borough": args.borough,
            "tier": args.tier,
            "bottle_count": meta.get("bottle_count"),
            "price_min": meta.get("price_min"),
            "price_max": meta.get("price_max"),
            "wine_director": args.wine_director,
            "scraped_at": _now_date(),
            "scrape_method": f"html_v1:{strategy}",
        },
        "wines": wines,
    }
    out = OUT_DIR / f"{slug}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"Wrote {out}  ({len(wines)} wines)")
    print(f"\nNext: python scripts/compile_vinolist_signals.py {out}  "
          "# add --apply to write producer pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
