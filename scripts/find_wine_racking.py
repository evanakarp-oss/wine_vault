"""
Find wine racking for sale across NYC restaurant-liquidation operators.

When a NYC restaurant closes, its fit-out — including wine racking / wine
storage cubes — gets resold through a small set of channels:

  1. Online auction aggregators that host restaurant-closeout sales
     (BidSpotter, Proxibid, HiBid, AuctionZip). Most NYC restaurant
     liquidators run their gavels through one of these.
  2. Used-equipment liquidator storefronts (Tiger Group, Maynards, Rabin,
     Hilco / Heritage Global, TAGeX Brands, Bowery Restaurant Supply, ...).
  3. Classifieds — Craigslist NYC (business/commercial section) and Facebook
     Marketplace, where closing operators and their buyers flip racking fast.

This script searches those channels for "wine rack" (and synonyms), dedupes,
and writes a ranked report to `build/`. It mirrors the politeness and caching
conventions of `scrape_blogs.py` / `scrape_csw_articles.py`:

  - identifying User-Agent, polite delay between requests, timeout + backoff
  - each source isolated in a try/except so one block doesn't sink the run
  - idempotent: re-running overwrites the report; raw HTML cached under
    raw/liquidation/html/ for re-parsing without re-fetching

Reality check
-------------
Craigslist exposes a static (JS-free) search fallback that this script parses
directly. The auction aggregators are increasingly client-rendered and rate
-limited; their adapters are best-effort and clearly flagged — when an adapter
can't parse, the script still emits the live search URL so you can click
through. The liquidator storefronts are a curated directory (they rarely have
keyword search) — the script prints where to look.

NOTE on the Claude Code *web* sandbox: its network policy uses a host
allowlist that returns `403 Host not in allowlist` for these consumer sites,
so live fetching only works when you run this on your own machine. Use
`--list-sources` (offline) to just print every search URL to click.

Usage
-----
  # Print every source + its live "wine rack" search URL (no network needed)
  python scripts/find_wine_racking.py --list-sources

  # Full search across all fetchable sources, write build/ report
  python scripts/find_wine_racking.py

  # Limit to specific sources / change the query
  python scripts/find_wine_racking.py --source craigslist_nyc --source hibid
  python scripts/find_wine_racking.py --query "wine cellar racking"

  # Re-parse cached HTML without re-fetching (after editing an adapter)
  python scripts/find_wine_racking.py --reparse

Deps: requests, beautifulsoup4, lxml
  uv pip install requests beautifulsoup4 lxml
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Iterable

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover - dependency guard
    sys.exit(
        f"missing dependency ({exc.name}); install with:\n"
        "  uv pip install requests beautifulsoup4 lxml"
    )

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "raw" / "liquidation" / "html"
REPORT_MD = ROOT / "build" / "wine_racking_listings.md"
REPORT_CSV = ROOT / "build" / "wine_racking_listings.csv"

UA = "wine-vault/find_wine_racking (personal cellar research; contact evanakarp@gmail.com)"
DEFAULT_QUERIES = ["wine rack", "wine racking", "wine storage rack", "wine cube"]
DELAY_SECONDS = 1.5
TIMEOUT = 20
RETRIES = 3


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Listing:
    source: str
    title: str
    url: str
    price: str = ""
    location: str = ""
    note: str = ""

    def key(self) -> str:
        return self.url.split("?")[0].rstrip("/").lower()


@dataclass
class Source:
    """One channel to search. `parse` may be None for manual/directory entries."""

    id: str
    name: str
    kind: str  # classifieds | auction-aggregator | liquidator | manual
    search_url: Callable[[str], str]
    parse: Callable[[str, str], list[Listing]] | None = None
    notes: str = ""

    def fetchable(self) -> bool:
        return self.parse is not None


# --------------------------------------------------------------------------- #
# HTTP helper (polite, with backoff — mirrors the CSW/blog scrapers)
# --------------------------------------------------------------------------- #
def fetch(url: str, session: requests.Session) -> str | None:
    backoff = 2
    for attempt in range(1, RETRIES + 1):
        try:
            resp = session.get(url, timeout=TIMEOUT)
        except requests.RequestException as exc:
            print(f"    ! network error ({exc.__class__.__name__}); retry {attempt}/{RETRIES}")
            time.sleep(backoff)
            backoff *= 2
            continue
        if resp.status_code == 200:
            return resp.text
        if resp.status_code == 403 and "allowlist" in resp.text.lower():
            print("    ! blocked by network allowlist — run this on your own machine "
                  "(see https://code.claude.com/docs/en/claude-code-on-the-web).")
            return None
        if resp.status_code == 429:
            print("    ! 429 rate-limited; backing off and stopping this source.")
            return None
        if 500 <= resp.status_code < 600:
            print(f"    ! HTTP {resp.status_code}; retry {attempt}/{RETRIES}")
            time.sleep(backoff)
            backoff *= 2
            continue
        print(f"    ! HTTP {resp.status_code}; giving up on this URL.")
        return None
    return None


def cache_path(source_id: str, query: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")
    return CACHE_DIR / f"{source_id}__{slug}.html"


# --------------------------------------------------------------------------- #
# Parsers
# --------------------------------------------------------------------------- #
def parse_craigslist(html: str, base: str) -> list[Listing]:
    """Craigslist serves a JS-free static fallback we can parse directly."""
    soup = BeautifulSoup(html, "lxml")
    out: list[Listing] = []
    for li in soup.select("li.cl-static-search-result"):
        a = li.find("a", href=True)
        if not a:
            continue
        title = (li.get("title") or a.get_text(" ", strip=True)).strip()
        price = li.select_one(".price")
        loc = li.select_one(".location")
        out.append(
            Listing(
                source="craigslist_nyc",
                title=title,
                url=a["href"],
                price=price.get_text(strip=True) if price else "",
                location=loc.get_text(strip=True) if loc else "",
            )
        )
    return out


def parse_generic(source_id: str):
    """Best-effort parser for client-rendered auction sites.

    Tries, in order: JSON-LD blocks, then anchors whose text mentions wine
    racking. These sites change often and may be fully JS — treat hits as a
    bonus and always fall back to the printed search URL. Flagged unverified.
    """

    def _parse(html: str, base: str) -> list[Listing]:
        soup = BeautifulSoup(html, "lxml")
        out: list[Listing] = []
        seen: set[str] = set()
        for a in soup.find_all("a", href=True):
            text = a.get_text(" ", strip=True)
            if not text or len(text) < 4:
                continue
            if not re.search(r"wine\s*(rack|cube|cellar|storage)", text, re.I):
                continue
            href = urllib.parse.urljoin(base, a["href"])
            if href in seen:
                continue
            seen.add(href)
            out.append(Listing(source=source_id, title=text, url=href,
                               note="unverified auto-parse"))
        return out

    return _parse


# --------------------------------------------------------------------------- #
# Source registry — NYC restaurant-liquidation channels
# --------------------------------------------------------------------------- #
def _q(s: str) -> str:
    return urllib.parse.quote_plus(s)


SOURCES: list[Source] = [
    # --- Classifieds (most reliably scrapeable) -------------------------- #
    Source(
        id="craigslist_nyc",
        name="Craigslist NYC — business/commercial",
        kind="classifieds",
        # bfa = business/commercial-for-sale; searchNearby pulls LI/NJ too
        search_url=lambda q: f"https://newyork.craigslist.org/search/bfa?query={_q(q)}&searchNearby=1",
        parse=parse_craigslist,
        notes="Where closing operators dump fixtures fast. Also try /search/sss (all for-sale).",
    ),
    Source(
        id="facebook_marketplace",
        name="Facebook Marketplace — NYC",
        kind="manual",
        search_url=lambda q: f"https://www.facebook.com/marketplace/nyc/search/?query={_q(q)}",
        parse=None,  # login-walled; URL only
        notes="Login-walled, not scrapeable. Open the URL; sort by Date Listed.",
    ),
    # --- Auction aggregators (host most NYC restaurant closeouts) -------- #
    Source(
        id="bidspotter",
        name="BidSpotter (industrial/restaurant auctions)",
        kind="auction-aggregator",
        search_url=lambda q: f"https://www.bidspotter.com/en-us/search?searchText={_q(q)}",
        parse=parse_generic("bidspotter"),
        notes="Most NYC restaurant liquidators gavel here. Filter by NY after opening.",
    ),
    Source(
        id="proxibid",
        name="Proxibid (industrial/restaurant auctions)",
        kind="auction-aggregator",
        search_url=lambda q: f"https://www.proxibid.com/asp/Search.asp?keyword={_q(q)}",
        parse=parse_generic("proxibid"),
        notes="Sister channel to BidSpotter; overlapping seller base.",
    ),
    Source(
        id="hibid",
        name="HiBid (auction marketplace)",
        kind="auction-aggregator",
        search_url=lambda q: f"https://hibid.com/lots?q={_q(q)}&status=OPEN",
        parse=parse_generic("hibid"),
        notes="Large open-auction marketplace; filter to NY/NJ/CT.",
    ),
    Source(
        id="auctionzip",
        name="AuctionZip (live + online)",
        kind="auction-aggregator",
        search_url=lambda q: f"https://www.auctionzip.com/Listings/lot-search.html?keyword={_q(q)}&zip=10001&miles=50",
        parse=parse_generic("auctionzip"),
        notes="Pre-scoped to a 50-mile radius of 10001 (Manhattan).",
    ),
    # --- NYC restaurant-specialist auctioneers (the real targets) -------- #
    # Surfaced by web search 2026-06; these run NYC indie restaurant/bar/
    # wine-bar closeouts directly. Most 403 bot user-agents and have no keyword
    # search, so they're directory entries pointing at their live-auction page.
    Source(
        id="metro_auctions",
        name="Metro Auctions LLC (NYC metro restaurant specialist)",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://www.metroauctionsllc.com/upcoming-auctions",
        parse=None,
        notes="Manhattan/Brooklyn/Queens/Bronx/SI restaurants, bars, wine bars. Best single NYC bet.",
    ),
    Source(
        id="atlas_auctioneers",
        name="Atlas Auctioneers (NYC/NJ/CT restaurant liquidations)",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://www.atlasauctioneers.com/",
        parse=None,
        notes="Full facility sell-offs; see /nycbar for bar/wine-bar lots.",
    ),
    Source(
        id="bestbuy_auctioneers",
        name="BestBuy Auctioneers (NJ/NYC/CT, 30+ yrs)",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://www.bestbuyauctioneers.com/upcomingauctions",
        parse=None,
        notes="Check /upcomingauctions and /pastauctions to gauge what comes through.",
    ),
    Source(
        id="pci_auctions_nynj",
        name="PCI Auctions New York & New Jersey",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://www.pciauctions.com/new-york-and-new-jersey/",
        parse=None,
        notes="Online timed auctions; has per-auction lot search once an auction is open.",
    ),
    Source(
        id="bandh_auctioneers",
        name="B&H Auctioneers (NY metro food-service)",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://bandhauctioneers.com/",
        parse=None,
        notes="Brooklyn/Queens/LI/Bronx/Westchester/SI coverage.",
    ),
    Source(
        id="auctionbidny",
        name="AuctionBidNY (NYC restaurant auctions)",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://auctionbidny.com/nycrestaurantauction.htm",
        parse=None,
        notes="All NYC + LI + N.NJ + E.CT.",
    ),
    Source(
        id="tagex",
        name="TAGeX Brands — restaurant liquidations",
        kind="nyc-auctioneer",
        search_url=lambda q: "https://tagexbrands.com/auctions/",
        parse=None,
        notes="National restaurant-specialist liquidator; wine racking shows up regularly.",
    ),
    Source(
        id="bowery_restaurant_supply",
        name="Bowery Restaurant Supply (used equipment)",
        kind="liquidator",
        search_url=lambda q: "https://www.boweryrestaurantsupply.com/",
        parse=None,
        notes="NYC storefront that buys/sells used restaurant fixtures — call for racking.",
    ),
]

SOURCE_BY_ID = {s.id: s for s in SOURCES}


# --------------------------------------------------------------------------- #
# Run
# --------------------------------------------------------------------------- #
def search_source(src: Source, queries: list[str], session: requests.Session,
                  reparse: bool) -> list[Listing]:
    found: list[Listing] = []
    for q in queries:
        url = src.search_url(q)
        cpath = cache_path(src.id, q)
        html: str | None = None
        if reparse and cpath.exists():
            html = cpath.read_text(encoding="utf-8", errors="replace")
        elif not reparse:
            print(f"    GET {url}")
            html = fetch(url, session)
            if html:
                cpath.parent.mkdir(parents=True, exist_ok=True)
                cpath.write_text(html, encoding="utf-8")
            time.sleep(DELAY_SECONDS)
        if html and src.parse:
            try:
                found.extend(src.parse(html, url))
            except Exception as exc:  # adapter brittleness shouldn't sink the run
                print(f"    ! parse error: {exc.__class__.__name__}: {exc}")
        # query variants for the same source collapse later via dedupe
    return found


def dedupe(listings: Iterable[Listing]) -> list[Listing]:
    seen: dict[str, Listing] = {}
    for lst in listings:
        seen.setdefault(lst.key(), lst)
    return list(seen.values())


def write_reports(listings: list[Listing], queries: list[str]) -> None:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by_source: dict[str, list[Listing]] = {}
    for lst in listings:
        by_source.setdefault(lst.source, []).append(lst)

    lines = [
        "# Wine racking — NYC restaurant-liquidation scan",
        "",
        f"_Generated {now} · queries: {', '.join(queries)}_",
        "",
        f"**{len(listings)} live listing(s)** auto-parsed across "
        f"{len(by_source)} source(s).",
        "",
    ]
    if listings:
        lines.append("## Listings found")
        lines.append("")
        for sid, group in sorted(by_source.items()):
            lines.append(f"### {SOURCE_BY_ID.get(sid).name if sid in SOURCE_BY_ID else sid}")
            for lst in group:
                bits = [f"**[{lst.title}]({lst.url})**"]
                if lst.price:
                    bits.append(lst.price)
                if lst.location:
                    bits.append(lst.location)
                if lst.note:
                    bits.append(f"_{lst.note}_")
                lines.append("- " + " · ".join(bits))
            lines.append("")

    lines.append("## Every source — click to search by hand")
    lines.append("")
    lines.append("Auction aggregators and liquidator storefronts are often "
                 "client-rendered or login-walled; open these directly:")
    lines.append("")
    for src in SOURCES:
        tag = "" if src.fetchable() else " *(manual — not auto-scraped)*"
        lines.append(f"- **{src.name}** ({src.kind}){tag}  ")
        lines.append(f"  <{src.search_url(queries[0])}>  ")
        if src.notes:
            lines.append(f"  {src.notes}")
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    with REPORT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source", "title", "price",
                                                "location", "url", "note"])
        writer.writeheader()
        for lst in listings:
            writer.writerow(asdict(lst))


def list_sources(queries: list[str]) -> None:
    print(f"\nNYC restaurant-liquidation sources (query: {queries[0]!r})\n")
    for kind in ["classifieds", "auction-aggregator", "nyc-auctioneer", "liquidator", "manual"]:
        group = [s for s in SOURCES if s.kind == kind]
        if not group:
            continue
        print(f"== {kind} ==")
        for src in group:
            auto = "auto-scraped" if src.fetchable() else "manual"
            print(f"  [{auto}] {src.name}")
            print(f"      {src.search_url(queries[0])}")
            if src.notes:
                print(f"      {src.notes}")
        print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", action="append", dest="queries",
                    help="search term (repeatable; defaults to wine-rack synonyms)")
    ap.add_argument("--source", action="append", dest="sources",
                    help="limit to source id(s); see --list-sources")
    ap.add_argument("--list-sources", action="store_true",
                    help="print sources + search URLs and exit (no network)")
    ap.add_argument("--reparse", action="store_true",
                    help="re-parse cached HTML instead of fetching")
    args = ap.parse_args(argv)

    queries = args.queries or DEFAULT_QUERIES

    if args.list_sources:
        list_sources(queries)
        return 0

    selected = SOURCES
    if args.sources:
        unknown = [s for s in args.sources if s not in SOURCE_BY_ID]
        if unknown:
            ap.error(f"unknown source(s): {', '.join(unknown)} "
                     f"(known: {', '.join(SOURCE_BY_ID)})")
        selected = [SOURCE_BY_ID[s] for s in args.sources]

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

    all_found: list[Listing] = []
    for src in selected:
        if not src.fetchable():
            print(f"\n[{src.id}] manual source — open: {src.search_url(queries[0])}")
            continue
        print(f"\n[{src.id}] searching {src.name} ...")
        all_found.extend(search_source(src, queries, session, args.reparse))

    listings = dedupe(all_found)
    write_reports(listings, queries)
    print(f"\nDone. {len(listings)} auto-parsed listing(s).")
    print(f"  report : {REPORT_MD.relative_to(ROOT)}")
    print(f"  csv    : {REPORT_CSV.relative_to(ROOT)}")
    print("  (auction/liquidator channels also listed in the report to click by hand)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
