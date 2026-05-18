"""
Multi-channel web search for ember-cooking baskets reachable from the US.

Sibai (https://sibai.es/menaje-para-brasas/) is a small Spanish maker
of brasa hardware with no US distribution. Mibrasa Home USA carries the
same product family but prices it punitively. The real supply lives in
small workshops scattered across Argentina, Uruguay, Brazil, the Basque
Country and the UK, plus white-label OEMs in China. This script asks
each of those channels: "can I get one of these to the US, and from whom?"

Framework
---------
1. DIRECT_BRAND — is Sibai itself reachable from the US?
   USPTO trademark, ImportYeti/Panjiva, backlinks to sibai.es.

2. US_RETAIL — substitutes already landed in the US
   Heritage Backyard, Gaucho Life, Pampa Direct, Wildwood Ovens,
   Urban Asado, MTC Kitchen, plus Amazon/eBay/Etsy aggregators.

3. ARG_URY — workshops in Argentina/Uruguay (herrería + parrilla)
   MercadoLibre, Etsy ship-from-AR, Instagram herrerías, NIC Store BBQ.

4. SPAIN_UK — Pira / Josper / Basque besuguera + UK asador builders
   Hostelería Uno, hostelería10, Parrilla Gaucha UK, Wildpyre, Metartal.

5. BRAZIL — grelha aramada / churrasco (Tramontina, Prana, Mor)
   Empório do Lazer, Alves Grill, achurrasqueira, Wildwood Ovens (US re-seller).

6. CHINA_OEM — Alibaba / AliExpress / DHgate white-label wire baskets.

7. FORWARDERS — package consolidators for shops that won't ship US.

8. INSTAGRAM_DM — small workshops only reachable via DM/WhatsApp.

Output
------
Per prong: top N results (title, URL, snippet) and a "[new]" tag the
first time a domain appears across the run, so fresh channels pop out.

Stdlib only (urllib + html.parser). No API key.

Usage
-----
  python scripts/search_sibai_us.py
  python scripts/search_sibai_us.py --only arg_ury
  python scripts/search_sibai_us.py --only spain_uk --top 5
  python scripts/search_sibai_us.py --query "besuguera ship US"
"""
from __future__ import annotations

import argparse
import re
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
    # 1. DIRECT_BRAND — Sibai itself
    ("direct_brand", "brand + US retail",   'sibai basket buy US OR USA OR "United States"'),
    ("direct_brand", "brand + distributor", '"sibai" "menaje" distributor OR importer US'),
    ("direct_brand", "USPTO trademark",     'site:tmsearch.uspto.gov OR site:tsdr.uspto.gov "sibai"'),
    ("direct_brand", "customs records",     'site:importyeti.com OR site:panjiva.com sibai'),
    ("direct_brand", "backlinks to sibai",  '"sibai.es" -site:sibai.es'),

    # 2. US_RETAIL — already landed
    ("us_retail", "Heritage Backyard",  'site:heritagebackyard.com brasero OR parrilla OR asado'),
    ("us_retail", "Gaucho Life",        'site:gaucholife.com brasero OR basket OR besuguera'),
    ("us_retail", "Pampa Direct",       'site:pampadirect.com brasero OR parrilla'),
    ("us_retail", "Wildwood Ovens",     'site:wildwoodovens.com burn basket OR brasero OR braseiro'),
    ("us_retail", "Urban Asado",        'site:urbanasado.com brasero OR basket'),
    ("us_retail", "MTC Kitchen",        'site:mtckitchen.com grill basket OR yakiami'),
    ("us_retail", "Norcal Oven Works",  'site:norcalovenworks.com brasero OR uruguayan'),
    ("us_retail", "Mibrasa USA",        'site:mibrasahomeusa.com basket OR cesto OR besuguera'),
    ("us_retail", "Amazon besuguera",   'site:amazon.com besuguera OR rodaballera OR "fish grill basket"'),
    ("us_retail", "Etsy from AR",       'site:etsy.com brasero argentina ships US'),
    ("us_retail", "eBay besuguera",     'site:ebay.com besuguera OR rodaballera OR "asador basket"'),

    # 3. ARG_URY — workshops at source
    ("arg_ury", "MercadoLibre AR",      'site:listado.mercadolibre.com.ar brasero OR canasto parrilla'),
    ("arg_ury", "MercadoLibre UY",      'site:listado.mercadolibre.com.uy brasero OR canasto'),
    ("arg_ury", "NIC Store BBQ",        'site:nicstorebbq.com brasero OR canasto OR international'),
    ("arg_ury", "Etsy ships from AR",   '"ships from Argentina" brasero OR parrilla site:etsy.com'),
    ("arg_ury", "herrería Instagram",   'instagram herreria brasero parrilla "envio" OR "whatsapp" argentina'),
    ("arg_ury", "Barraca de Fuegos UY", 'site:barracadefuegos.com.uy brasero OR parrilla'),

    # 4. SPAIN_UK — restaurant-grade + UK builders
    ("spain_uk", "Hostelería Uno",      'site:hosteleriauno.es besuguera OR rodaballera'),
    ("spain_uk", "Hostelería 10",       'site:hosteleria10.com pescado parrilla'),
    ("spain_uk", "Pira charcoal ovens", 'site:piracharcoalovens.com fish OR besuguera'),
    ("spain_uk", "Josper besuguera",    'josper besuguera buy international'),
    ("spain_uk", "Parrilla Gaucha UK",  'site:parrillagauchauk.com brasero OR basket'),
    ("spain_uk", "Wildpyre UK",         'site:wildpyre.co.uk brasero OR basket'),
    ("spain_uk", "Metartal UK",         'site:metartal.com asador OR brasero'),
    ("spain_uk", "Black Box BBQ UK",    'site:blackboxbbq.co.uk parrilla OR brasero'),
    ("spain_uk", "TopBrasa",            'site:topbrasa.com parrilla vasca OR besuguera'),
    ("spain_uk", "grandgourmet.se",     'site:grandgourmet.se halster OR besugero OR rodaballera'),

    # 5. BRAZIL — grelha aramada / churrasco
    ("brazil", "Empório do Lazer",    'site:emporiodolazervirtual.com.br grelha aramada'),
    ("brazil", "Alves Grill",         'site:alvesgrill.com.br grelha aramada inox'),
    ("brazil", "achurrasqueira",      'site:achurrasqueira.com.br grelha aramada uruguaia'),
    ("brazil", "Leroy Merlin BR",     'site:leroymerlin.com.br grelha aramada churrasco'),
    ("brazil", "Amazon BR",           'site:amazon.com.br grelha aramada inox 304'),
    ("brazil", "Tramontina BR",       'tramontina grelha aramada churrasco inox'),

    # 6. CHINA_OEM — white-label wire baskets
    ("china_oem", "Alibaba besuguera",  'site:alibaba.com "fish grill basket" stainless wire 304'),
    ("china_oem", "Alibaba bulk",       'site:alibaba.com MOQ "wire fish basket" OEM stainless'),
    ("china_oem", "AliExpress",         'site:aliexpress.com fish grill basket stainless wire'),
    ("china_oem", "DHgate",             'site:dhgate.com fish grill basket stainless'),

    # 7. FORWARDERS — when the shop won't ship US
    ("forwarders", "MyUS Argentina",    'myus shop ship from Argentina forwarder'),
    ("forwarders", "Aeropost AR/UY",    'aeropost argentina uruguay forwarder mercadolibre'),
    ("forwarders", "Planet Express",    'planet express shop argentina forward to US'),
    ("forwarders", "Stackry Europe",    'stackry ship from Spain UK to US forwarder'),
    ("forwarders", "Tienda Aeropost",   'tienda aeropost argentina envio EEUU'),

    # 8. INSTAGRAM_DM — DM-only herrerías
    ("instagram_dm", "herreria parrilla",  'site:instagram.com herreria parrilla brasero argentina'),
    ("instagram_dm", "herreria Olavarría", 'site:instagram.com herreria sur Olavarria brasero'),
    ("instagram_dm", "Basque halster",     'site:instagram.com halster besugero kokotxera rodaballera'),
    ("instagram_dm", "churrasco artesanal", 'site:instagram.com grelha churrasco artesanal aramada'),

    # 9. JAPAN — yakiami / konro / robatayaki / sumibiyaki
    ("japan", "Korin yakiami",  'site:korin.com yakiami OR konro OR "grill net" OR basket'),
    ("japan", "MTC Kitchen",    'site:mtckitchen.com konro OR yakiami OR robata OR "grill basket"'),
    ("japan", "Hitachiya USA",  'site:hitachiyausa.com yaki-ami OR yakiami OR grill'),
    ("japan", "Minimaru",       'site:minimaru.com yakiami OR konro'),
    ("japan", "Kasai Grills",   'site:kasaigrills.com konro OR robata'),
    ("japan", "Amazon yakiami", 'site:amazon.com yakiami OR konro "made in Japan"'),
    ("japan", "eBay Japan",     'site:ebay.com yakiami OR yaki-ami OR konro Japan'),
    ("japan", "Snow Peak grill",'snow peak yakiami pro grill net buy US'),
    ("japan", "Toiro Kitchen",  'site:toirokitchen.com grill OR konro OR yakiami'),
    ("japan", "Bernal Cutlery", 'site:bernalcutlery.com grill OR konro'),

    # 10. AFRICA — South African braai
    ("africa", "NorCal SA imports", 'site:norcalovenworks.com braai jetmaster basket'),
    ("africa", "OZ Braai US",       'site:dasmule.com OR site:ozbraai.com.au travel braai basket'),
    ("africa", "Cadac skottel",     'cadac skottel braai US ship'),
    ("africa", "Braaiplank",        'site:braaiplank.co.za rolling braai basket international'),
    ("africa", "ShopSouthAfrica",   'site:shopsouthafrica.com.au OR site:southafricanshop.uk braai basket'),

    # 11. PORTUGAL — sardinha + grelhador
    ("portugal", "Seabra Foods US",   'site:seabrafoods.com grelha sardinha OR fish'),
    ("portugal", "JVP",               'site:jvp-churrasqueiras.com grelhador inox export'),
    ("portugal", "Portugalia US",     'site:portugaliamarketplace.com grelha OR sardinha OR grelhador'),

    # 12. MIDDLE EAST — mangal / manqal
    ("middle_east", "MangalGrills",   'site:mangalgrills.com fish OR basket OR cage OR shashlik'),
    ("middle_east", "Timeless Steel", 'site:timelessteel.com mangal fish OR basket OR cage'),
    ("middle_east", "Josper mangal",  'site:jospergrill.com mangal kebab'),

    # 13. US_CRAFT — domestic forges and makers
    ("us_craft", "Crafted Fire",    'site:craftedfire.com basket OR brasero OR ember'),
    ("us_craft", "Forged by Thor",  'site:forgedbythor.com grill OR basket OR ember'),
    ("us_craft", "Wicks Forge",     'site:wicksforge.com grill basket OR ember OR roaster'),
    ("us_craft", "Hansen Wheel",    'site:hansenwheel.com hand-forged cooking basket OR grill'),
    ("us_craft", "Etsy US-made",    'site:etsy.com hand forged grill basket "ships from united states"'),
    ("us_craft", "Crafted Fire AR", 'site:craftedfire.com argentinian asado OR brasero'),
]


# Stock heuristics. Probe a candidate URL's HTML for availability hints.
# Out-of-stock signals beat in-stock — "add to cart" often appears in CSS
# templates even on sold-out pages.
STOCK_OUT = [
    r'"availability"\s*:\s*"[^"]*OutOfStock',
    r'"availability"\s*:\s*"[^"]*SoldOut',
    r'\bout\s*of\s*stock\b',
    r'\bsold\s*out\b',
    r'\bcurrently unavailable\b',
    r'\bno longer available\b',
    r'\btemporarily unavailable\b',
    r'\bagotado\b',
    r'\bsin\s*stock\b',
    r'\bsin\s*existencias\b',
    r'\bno\s*disponible\b',
    r'\besgotado\b',
    r'\bindispon[íi]vel\b',
    r'\brupture de stock\b',
    r'\bindisponible\b',
    r'\bvergriffen\b',
    r'\bnicht\s*verf[üu]gbar\b',
    r'\besaurito\b',
    r'\bnon\s*disponibile\b',
    r'在庫切れ',
    r'品切れ',
    r'完売',
]
STOCK_IN = [
    r'"availability"\s*:\s*"[^"]*InStock',
    r'"availability"\s*:\s*"[^"]*PreOrder',
    r'\badd\s*to\s*(cart|bag|basket)\b',
    r'\bbuy\s*it\s*now\b',
    r'\bagregar al carrito\b',
    r'\ba[ñn]adir al carrito\b',
    r'\bcomprar ahora\b',
    r'\badicionar ao carrinho\b',
    r'\bcomprar agora\b',
    r'\bajouter au panier\b',
    r'\bin den warenkorb\b',
    r'\baggiungi al carrello\b',
    r'カートに入れる',
    r'在庫あり',
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


_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_OUT_RE = re.compile("|".join(STOCK_OUT), re.IGNORECASE)
_IN_RE = re.compile("|".join(STOCK_IN), re.IGNORECASE)


def probe_stock(url: str, timeout: float = 12.0) -> str:
    """Return 'in', 'out', 'unknown', or 'error:<short>'.

    Cheap-and-dirty: fetch HTML, run two regex unions. Out-of-stock wins
    if both match (templates often render 'add to cart' even when sold).
    Search-results / category pages will mostly land on 'unknown'.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _BROWSER_UA, "Accept-Language": "en-US,en;q=0.8"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(400_000).decode("utf-8", errors="replace")
    except Exception as e:
        return f"error:{type(e).__name__}"
    if _OUT_RE.search(body):
        return "out"
    if _IN_RE.search(body):
        return "in"
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser(description="Multi-prong search for Sibai baskets or substitutes in the US.")
    ap.add_argument(
        "--only",
        choices=[
            "direct_brand", "us_retail", "arg_ury", "spain_uk", "brazil",
            "china_oem", "forwarders", "instagram_dm", "japan", "africa",
            "portugal", "middle_east", "us_craft",
        ],
        help="Run only one prong group.",
    )
    ap.add_argument("--query", action="append", help="Bypass prongs; run this query instead (repeatable).")
    ap.add_argument("--top", type=int, default=6, help="Results per query (default 6).")
    ap.add_argument("--delay", type=float, default=1.5, help="Seconds between queries.")
    ap.add_argument(
        "--check-stock",
        action="store_true",
        help="Fetch each candidate URL and probe for in-stock/out-of-stock signals.",
    )
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
            stock_tag = ""
            if args.check_stock:
                status = probe_stock(r["url"])
                marker = {"in": "✓ IN", "out": "✗ OUT", "unknown": "? UNK"}.get(status, f"! {status}")
                stock_tag = f"  [{marker}]"
            print(f"  - {r.get('title', '(no title)')}{tag}{stock_tag}")
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
