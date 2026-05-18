"""
Find US (or similar) sellers of Sibai brasa baskets — or substitutes.

Sibai (https://sibai.es/menaje-para-brasas/) is a small Spanish maker of
ember-cooking baskets and brasa hardware. They have no obvious US dealer,
so a single keyword search rarely answers the real question. This script
runs a structured multi-prong search and groups hits by *intent* so a
human can scan and act.

Framework
---------
1. DIRECT — is Sibai itself reachable from the US?
   a) Brand-name + US-retail/import language
   b) USPTO trademark presence (TESS dorks)
   c) Customs / bill-of-lading aggregators (importyeti, panjiva)
   d) Backlink discovery — pages that mention sibai.es

2. SIMILAR — what's a category substitute already in the US?
   a) Category vocabulary: asador / parrilla / brasa / ember basket
   b) Style cousins: Argentine parrilla, Basque txuleton, Japanese yakiami
   c) Spanish-goods + BBQ-specialty retailers via site: dorks

Output
------
Per prong: top N results (title, URL, snippet) and a "[new]" tag the first
time a domain shows up across the whole run, so substitute leads pop out.

Stdlib only (urllib + html.parser). No API key.

Usage
-----
  python scripts/search_sibai_us.py
  python scripts/search_sibai_us.py --only direct
  python scripts/search_sibai_us.py --only similar --top 5
  python scripts/search_sibai_us.py --query "asador basket buy usa"
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = (
    "Mozilla/5.0 (compatible; sibai-search/0.2; "
    "personal-research; +https://sibai.es/menaje-para-brasas/)"
)

# (prong, label, query)
PRONGS: list[tuple[str, str, str]] = [
    # 1. DIRECT — Sibai itself
    ("direct", "brand + US retail",   'sibai basket buy US OR USA OR "United States"'),
    ("direct", "brand + distributor", '"sibai" "menaje" distributor OR importer US'),
    ("direct", "trademark (USPTO)",   'site:tmsearch.uspto.gov "sibai"'),
    ("direct", "trademark (TSDR)",    'site:tsdr.uspto.gov "sibai"'),
    ("direct", "customs: ImportYeti", 'site:importyeti.com sibai'),
    ("direct", "customs: Panjiva",    'site:panjiva.com sibai'),
    ("direct", "backlinks to sibai",  '"sibai.es" -site:sibai.es'),

    # 2. SIMILAR — category substitutes
    ("similar", "asador basket",      '"asador basket" buy US'),
    ("similar", "parrilla basket",    '"parrilla basket" buy US'),
    ("similar", "brasa / ember",      'brasa OR ember "grill basket" US retailer'),
    ("similar", "Argentine parrilla", 'argentine parrilla grilling basket buy US'),
    ("similar", "Basque txuleton",    'basque txuleton grill basket buy US'),
    ("similar", "Spanish goods US",   'site:tienda.com OR site:latienda.com brasa OR parrilla basket'),
    ("similar", "BBQ specialists",    'site:bbqguys.com OR site:surlatable.com OR site:williams-sonoma.com brasa OR asador basket'),
    ("similar", "boutique grills",    '"hand-forged" OR "handmade" grilling basket spain OR argentina US'),
]


class DDGResultParser(HTMLParser):
    """Parse rows from html.duckduckgo.com.

    Each result is `<a class="result__a" href="...">title</a>` and later
    `<a class="result__snippet">snippet</a>`. The href is wrapped in a
    DDG redirect (`//duckduckgo.com/l/?uddg=<encoded>`) which we unwrap.
    """

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._capture: str | None = None
        self._buf: list[str] = []
        self._current: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attr = dict(attrs)
        cls = attr.get("class") or ""
        if "result__a" in cls:
            self._current = {"url": _unwrap_ddg(attr.get("href") or "")}
            self._capture, self._buf = "title", []
        elif "result__snippet" in cls and self._current:
            self._capture, self._buf = "snippet", []

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._capture is None:
            return
        text = " ".join("".join(self._buf).split())
        if self._capture == "title":
            self._current["title"] = text
        elif self._capture == "snippet":
            self._current["snippet"] = text
            if self._current.get("url"):
                self.results.append(self._current)
            self._current = {}
        self._capture, self._buf = None, []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buf.append(data)


def _unwrap_ddg(href: str) -> str:
    if not href:
        return ""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        target = urllib.parse.parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return urllib.parse.unquote(target)
    return href


def search(query: str, top: int) -> list[dict[str, str]]:
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    parser = DDGResultParser()
    parser.feed(body)
    return parser.results[:top]


def _domain(url: str) -> str:
    netloc = urllib.parse.urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def main() -> int:
    ap = argparse.ArgumentParser(description="Multi-prong search for Sibai baskets or substitutes in the US.")
    ap.add_argument("--only", choices=["direct", "similar"], help="Run only one prong group.")
    ap.add_argument("--query", action="append", help="Bypass prongs; run this query instead (repeatable).")
    ap.add_argument("--top", type=int, default=6, help="Results per query (default 6).")
    ap.add_argument("--delay", type=float, default=1.5, help="Seconds between queries.")
    args = ap.parse_args()

    if args.query:
        prongs = [("custom", f"q{i+1}", q) for i, q in enumerate(args.query)]
    else:
        prongs = [p for p in PRONGS if not args.only or p[0] == args.only]

    seen: dict[str, int] = {}  # domain -> first-seen prong index

    for i, (group, label, q) in enumerate(prongs):
        if i:
            time.sleep(args.delay)
        print(f"\n=== [{group}] {label} :: {q} ===")
        try:
            results = search(q, args.top)
        except Exception as e:
            print(f"  ! error: {e}", file=sys.stderr)
            continue
        if not results:
            print("  (no results)")
            continue
        for r in results:
            d = _domain(r["url"])
            tag = " [new]" if d and d not in seen else ""
            if d:
                seen.setdefault(d, i)
            print(f"  - {r.get('title', '(no title)')}{tag}")
            print(f"    {r['url']}")
            snip = r.get("snippet", "")
            if snip:
                print(f"    {snip[:200]}")

    # Quick recap of unique domains, ordered by first appearance — the most
    # interesting leads are usually the ones that surface in `similar` prongs
    # but didn't show up earlier under `direct`.
    print(f"\n--- {len(seen)} unique domains across {len(prongs)} queries ---")
    for d, _ in sorted(seen.items(), key=lambda kv: kv[1]):
        print(f"  {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
