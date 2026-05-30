"""
Scrape Fass Selections and Down to Earth Wines (Panzer) blog posts into
`raw/<site>/`, mirroring the conventions of `scrape_csw_articles.py`.

Both sites are WordPress, so URL discovery prefers the wp-json REST API and
falls back to sitemap → paginated index crawling. Politeness is identical to
the CSW scraper: 1.5s between requests, exponential backoff on 5xx, hard-stop
on 429, idempotent caching of raw HTML.

Sites
-----
  fass  -> https://www.fassselections.com/blog/   (single offers, often 1-3 wines, 1 producer)
  dtew  -> https://downtoearthwines.net/          (long-form producer profiles by Robert Panzer)

  Note: dtew's robots.txt disallows /read-their-stories/. By default this script
  honors robots.txt for any URL it intends to fetch. Pass --ignore-robots to
  override (acknowledging this is personal-archive use only). The 1.5s delay and
  identifying User-Agent stand either way.

Data flow (mirrors raw/csw/)
----------------------------
  raw/<site>/_url_inventory.txt      — deduped URL list (sitemap ∪ wp-json ∪ wiki refs)
  raw/<site>/html/<slug>.html        — cached raw HTML
  raw/<site>/markdown/<slug>.md      — extracted YAML-frontmatter + body
  raw/<site>/articles.csv            — index (url, slug, title, date, producer, word_count, ...)
  raw/<site>/_errors.log             — append-only error log

Frontmatter shape
-----------------
  type: <site>_article          # fass_article | dtew_article
  slug: <stable-slug>
  title: "<post title>"
  url: <canonical url>
  date: "YYYY-MM-DD"
  producer: "<best-effort producer name>"   # often empty for fass; common for dtew
  categories: [...]              # WP categories that aren't generic ("Blog" filtered out)
  word_count: <int>
  fetched_at: "<iso-8601 utc>"

Usage
-----
  # Build URL inventory for one site (wp-json + sitemap + wiki back-refs, deduped)
  python scripts/scrape_blogs.py --site fass --build-index
  python scripts/scrape_blogs.py --site dtew --build-index --ignore-robots

  # Dry run: fetch N URLs, eyeball extractor shape
  python scripts/scrape_blogs.py --site fass --limit 3

  # Full run
  python scripts/scrape_blogs.py --site fass --all
  python scripts/scrape_blogs.py --site dtew --all --ignore-robots

  # Re-parse cached HTML into markdown without re-fetching (after extractor edits)
  python scripts/scrape_blogs.py --site fass --reparse

Deps: requests, beautifulsoup4, lxml
  uv pip install requests beautifulsoup4 lxml
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup, Tag
except ImportError as e:
    print(f"Missing dep: {e}. Run: python -m pip install --user requests beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(2)

import xml.etree.ElementTree as ET


# Resolve VAULT root assuming this file lives in <vault>/scripts/
VAULT = Path(__file__).resolve().parent.parent

UA = "Mozilla/5.0 (compatible; wine-research/1.0; personal archive; +local-only)"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
DELAY_SECONDS = 1.5
MAX_RETRIES = 4
BACKOFF_BASE = 2.0


# --------------------------------------------------------------------------- #
# Site configuration                                                          #
# --------------------------------------------------------------------------- #

@dataclass
class SiteConfig:
    name: str                          # short id used as folder + frontmatter type prefix
    base: str                          # https://example.com
    article_url_filter: Callable[[str], bool]  # is this URL a single-post article on this site?
    sitemap_candidates: list[str]      # sitemap URLs to try (in order)
    wp_json_endpoint: str              # absolute or relative; "" disables
    blog_index_url: str                # paginated index entry point (fallback)
    blog_pagination_template: str      # "{base}/blog/page/{n}/" or similar
    body_selectors: list[tuple[str, dict]]  # bs4 (tag, attrs) tuples to try in order
    drop_categories: set[str] = field(default_factory=set)  # generic categories to filter from frontmatter

    def slug_from_url(self, url: str) -> str:
        path = urlparse(url).path.rstrip("/")
        return path.rsplit("/", 1)[-1]


def _fass_is_article(url: str) -> bool:
    p = urlparse(url)
    if p.netloc not in ("www.fassselections.com", "fassselections.com"):
        return False
    if not p.path.startswith("/blog/"):
        return False
    # Index pages: /blog/, /blog/page/2/, /blog/page/3/...
    if p.path == "/blog/" or re.match(r"^/blog/page/\d+/?$", p.path):
        return False
    # Category/author/feed routes
    if any(seg in p.path for seg in ("/category/", "/author/", "/feed/", "/tag/")):
        return False
    return True


def _dtew_is_article(url: str) -> bool:
    p = urlparse(url)
    if p.netloc not in ("downtoearthwines.net", "www.downtoearthwines.net"):
        return False
    # DTEW posts live at root level, e.g. /from-the-heart-of-the-mittelhaardt-jurgen-and-sabine-mosbacher/
    path = p.path.strip("/")
    if not path:
        return False
    # Filter known non-article routes
    skip_prefixes = ("wp-", "category", "author", "tag", "feed", "page", "read-their-stories",
                     "about", "contact", "subscribe", "shop", "cart", "checkout", "comments")
    first = path.split("/", 1)[0]
    if first in skip_prefixes or first.startswith("wp-"):
        return False
    # File extensions (images, etc.)
    if "." in first:
        return False
    return True


SITES: dict[str, SiteConfig] = {
    "fass": SiteConfig(
        name="fass",
        base="https://www.fassselections.com",
        article_url_filter=_fass_is_article,
        sitemap_candidates=[
            "https://www.fassselections.com/wp-sitemap.xml",
            "https://www.fassselections.com/sitemap_index.xml",
            "https://www.fassselections.com/sitemap.xml",
        ],
        wp_json_endpoint="https://www.fassselections.com/wp-json/wp/v2/posts",
        blog_index_url="https://www.fassselections.com/blog/",
        blog_pagination_template="https://www.fassselections.com/blog/page/{n}/",
        body_selectors=[
            ("div", {"class": "entry-content"}),
            ("article", {}),
            ("main", {}),
        ],
        drop_categories={"blog", "uncategorized"},
    ),
    "dtew": SiteConfig(
        name="dtew",
        base="https://downtoearthwines.net",
        article_url_filter=_dtew_is_article,
        sitemap_candidates=[
            "https://downtoearthwines.net/wp-sitemap.xml",
            "https://downtoearthwines.net/sitemap_index.xml",
            "https://downtoearthwines.net/sitemap.xml",
        ],
        wp_json_endpoint="https://downtoearthwines.net/wp-json/wp/v2/posts",
        blog_index_url="https://downtoearthwines.net/read-their-stories/",
        blog_pagination_template="https://downtoearthwines.net/read-their-stories/page/{n}/",
        body_selectors=[
            ("div", {"class": "entry-content"}),
            ("article", {}),
            ("main", {}),
        ],
        drop_categories={"blog", "uncategorized", "read their stories", "stories"},
    ),
}


# --------------------------------------------------------------------------- #
# Robots.txt                                                                  #
# --------------------------------------------------------------------------- #

def robots_check(site: SiteConfig, ignore: bool) -> tuple[bool, str]:
    """Return (ok_to_proceed, message). When ignore=True we still fetch + report."""
    rp = urllib.robotparser.RobotFileParser()
    robots_url = f"{site.base}/robots.txt"
    try:
        r = requests.get(robots_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return True, f"no robots.txt ({r.status_code}); proceeding"
        rp.parse(r.text.splitlines())
    except Exception as e:
        return True, f"robots.txt unreachable ({e!r}); proceeding"

    # Test the index URL specifically
    allowed = rp.can_fetch(UA, site.blog_index_url)
    if allowed:
        return True, "robots.txt allows blog index"
    msg = f"robots.txt DISALLOWS {site.blog_index_url} for our UA"
    if ignore:
        return True, msg + " — proceeding due to --ignore-robots"
    return False, msg


# --------------------------------------------------------------------------- #
# URL inventory                                                               #
# --------------------------------------------------------------------------- #

def _fetch(url: str, *, timeout: int = 30) -> tuple[int, str]:
    """GET with retries + backoff. Hard stop on 429."""
    for attempt in range(MAX_RETRIES):
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 429:
            raise RuntimeError(f"429 on {url}; stopping to respect rate-limit")
        if r.status_code >= 500 and attempt < MAX_RETRIES - 1:
            wait = BACKOFF_BASE ** attempt
            print(f"  {r.status_code}; retry in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r.status_code, r.text
    return r.status_code, r.text


def urls_from_sitemap(site: SiteConfig) -> list[str]:
    """Try each sitemap candidate; recurse into sitemap-index if needed."""
    out: set[str] = set()
    seen: set[str] = set()

    def parse_sitemap(url: str, depth: int = 0) -> None:
        if url in seen or depth > 3:
            return
        seen.add(url)
        try:
            status, text = _fetch(url, timeout=20)
            if status != 200:
                return
            xml_text = re.sub(r'\sxmlns="[^"]+"', "", text, count=1)
            root = ET.fromstring(xml_text)
        except Exception as e:
            print(f"  sitemap parse failed for {url}: {e!r}", file=sys.stderr)
            return

        if root.tag.endswith("sitemapindex"):
            for sm in root.findall("sitemap"):
                loc = (sm.findtext("loc") or "").strip()
                if loc:
                    parse_sitemap(loc, depth + 1)
        else:  # urlset
            for u in root.findall("url"):
                loc = (u.findtext("loc") or "").strip()
                if loc and site.article_url_filter(loc):
                    out.add(loc)

    for sm in site.sitemap_candidates:
        parse_sitemap(sm)
        if out:
            break
    return sorted(out)


def urls_from_wp_json(site: SiteConfig) -> list[str]:
    """Page through wp-json/wp/v2/posts. Returns canonical post URLs."""
    if not site.wp_json_endpoint:
        return []
    out: set[str] = set()
    page = 1
    per_page = 50
    while True:
        url = f"{site.wp_json_endpoint}?per_page={per_page}&page={page}&_fields=link,slug,date"
        try:
            status, text = _fetch(url, timeout=20)
        except RuntimeError:
            raise
        if status == 400 and page > 1:
            # WordPress returns 400 ("rest_post_invalid_page_number") past last page
            break
        if status != 200:
            print(f"  wp-json {status} on page {page}; aborting wp-json discovery", file=sys.stderr)
            break
        try:
            posts = json.loads(text)
        except Exception:
            break
        if not posts:
            break
        for p in posts:
            link = (p.get("link") or "").strip()
            if link and site.article_url_filter(link):
                out.add(link)
        if len(posts) < per_page:
            break
        page += 1
        time.sleep(DELAY_SECONDS / 2)  # gentler with structured API
        if page > 200:  # paranoia bound
            break
    return sorted(out)


def urls_from_pagination(site: SiteConfig, max_pages: int = 200) -> list[str]:
    """Crawl /blog/, /blog/page/2/, ... harvesting article hrefs. Used as a fallback."""
    out: set[str] = set()
    for n in range(1, max_pages + 1):
        url = site.blog_index_url if n == 1 else site.blog_pagination_template.format(base=site.base, n=n)
        try:
            status, html = _fetch(url, timeout=20)
        except RuntimeError:
            raise
        if status == 404:
            break
        if status != 200:
            print(f"  pagination {status} at page {n}; stopping", file=sys.stderr)
            break
        soup = BeautifulSoup(html, "html.parser")
        new = 0
        for a in soup.find_all("a", href=True):
            href = urljoin(site.base, a["href"])
            if site.article_url_filter(href):
                if href not in out:
                    out.add(href)
                    new += 1
        print(f"  page {n}: +{new} (total {len(out)})")
        if new == 0:
            break
        time.sleep(DELAY_SECONDS)
    return sorted(out)


def urls_from_wiki(site: SiteConfig) -> list[str]:
    """Pull article URLs already cited inside wiki/producers/."""
    netloc = urlparse(site.base).netloc.replace("www.", "")
    pat = re.compile(rf"https?://(?:www\.)?{re.escape(netloc)}/[^\s)\"'<>]+")
    out: set[str] = set()
    d = VAULT / "wiki" / "producers"
    if d.exists():
        for f in d.glob("*.md"):
            for m in pat.finditer(f.read_text(encoding="utf-8", errors="ignore")):
                href = m.group(0).rstrip("!.,;:)")
                if site.article_url_filter(href):
                    out.add(href)
    return sorted(out)


def cmd_build_index(site: SiteConfig, ignore_robots: bool) -> int:
    raw_dir = VAULT / "raw" / site.name
    raw_dir.mkdir(parents=True, exist_ok=True)

    ok, msg = robots_check(site, ignore_robots)
    print(f"[robots] {msg}")
    if not ok:
        print("[robots] aborting. Pass --ignore-robots to override (personal-archive use).", file=sys.stderr)
        return 2

    print(f"[{site.name}] discovery: wp-json...")
    wp = urls_from_wp_json(site)
    print(f"  wp-json: {len(wp)} URLs")

    print(f"[{site.name}] discovery: sitemap...")
    sm = urls_from_sitemap(site)
    print(f"  sitemap: {len(sm)} URLs")

    pagi: list[str] = []
    if not wp and not sm:
        print(f"[{site.name}] discovery: pagination crawl (fallback)...")
        pagi = urls_from_pagination(site)
        print(f"  pagination: {len(pagi)} URLs")

    wiki = urls_from_wiki(site)
    print(f"  wiki refs: {len(wiki)} URLs")

    all_urls = sorted(set(wp) | set(sm) | set(pagi) | set(wiki))
    inventory = raw_dir / "_url_inventory.txt"
    inventory.write_text("\n".join(all_urls) + ("\n" if all_urls else ""), encoding="utf-8")
    print(f"  union:   {len(all_urls)} -> {inventory}")
    return 0


# --------------------------------------------------------------------------- #
# Extraction                                                                  #
# --------------------------------------------------------------------------- #

@dataclass
class Extracted:
    url: str
    slug: str
    title: str
    date: str
    producer: str
    categories: list[str]
    body_markdown: str
    word_count: int


def _meta(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str:
    if name:
        el = soup.find("meta", attrs={"name": name})
    elif prop:
        el = soup.find("meta", property=prop)
    else:
        return ""
    if el and el.get("content"):
        return el["content"].strip()
    return ""


_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_date(text: str) -> str:
    """Parse a few likely date formats. Returns YYYY-MM-DD or ''."""
    text = text.strip()
    # ISO 2024-01-19T... or 2024-01-19
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # WordPress byline: "Jan 19, 2024" / "January 19, 2024"
    m = re.search(r"\b([A-Za-z]+)\.?\s+(\d{1,2}),\s+(\d{4})\b", text)
    if m:
        mon = _MONTHS.get(m.group(1).lower()[:4]) or _MONTHS.get(m.group(1).lower()[:3])
        if mon:
            return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"
    # M/D/YYYY
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", text)
    if m:
        mm, dd, yy = m.groups()
        y = int(yy)
        if y < 100:
            y = 2000 + y if y < 50 else 1900 + y
        return f"{y:04d}-{int(mm):02d}-{int(dd):02d}"
    return ""


def _extract_categories(soup: BeautifulSoup) -> list[str]:
    """Pull WordPress category names from rel='category tag' links + body class."""
    out: set[str] = set()
    for a in soup.find_all("a", attrs={"rel": True}):
        rels = a.get("rel") or []
        if isinstance(rels, str):
            rels = [rels]
        if any("category" in r or "tag" in r for r in rels):
            txt = a.get_text(" ", strip=True)
            if txt:
                out.add(txt)
    # WP body class often contains: category-blog, category-remi-poisot, etc.
    body = soup.find("body")
    if body and body.get("class"):
        for c in body.get("class"):
            if c.startswith("category-"):
                slug = c[len("category-"):]
                # leave slug-form for the body-class route; it's a useful signal
                out.add(slug.replace("-", " ").title())
    return sorted(out)


def _strip_chrome(body_el: Tag) -> None:
    """Remove navigation/widget noise inside the body container before MD conversion."""
    selectors = [
        "script", "style", "noscript", "iframe", "form",
        ".share", ".social", ".sharedaddy", ".jp-relatedposts",
        ".newsletter", ".comments", "#comments", ".entry-meta",
        ".post-navigation", ".nav-links", ".widget", "aside",
    ]
    for sel in selectors:
        for bad in body_el.select(sel):
            bad.decompose()


def extract(site: SiteConfig, url: str, html: str) -> Extracted:
    soup = BeautifulSoup(html, "html.parser")

    # --- title ---
    title = _meta(soup, prop="og:title")
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(" ", strip=True)
    if not title and soup.title:
        title = soup.title.get_text(" ", strip=True)
    # Strip site suffix " | Fass Selections" / " - Down to Earth Wines"
    title = re.sub(r"\s*[\|\-–—]\s*(Fass Selections|Down to Earth Wines)\s*$", "", title or "").strip()

    # --- date ---
    date = ""
    for prop in ("article:published_time", "og:article:published_time"):
        v = _meta(soup, prop=prop)
        if v:
            date = _parse_date(v)
            if date:
                break
    if not date:
        t = soup.find("time")
        if t:
            date = _parse_date(t.get("datetime", "") or t.get_text(" ", strip=True))
    if not date:
        # Divi/WP byline: <span class="published">Nov 6, 2023</span>
        pub = soup.find("span", class_="published")
        if pub:
            date = _parse_date(pub.get_text(" ", strip=True))
    if not date:
        # WP byline pattern: "by admin | Jan 19, 2024 | Blog"
        byline = soup.find(string=re.compile(r"\bby\s+\S+\s*\|"))
        if byline:
            date = _parse_date(str(byline))

    # --- categories ---
    categories = [c for c in _extract_categories(soup) if c.lower() not in site.drop_categories]

    # --- body ---
    body_el = None
    for tag, attrs in site.body_selectors:
        body_el = soup.find(tag, attrs=attrs) if attrs else soup.find(tag)
        if body_el:
            break
    if body_el:
        _strip_chrome(body_el)
        body_md = html_to_markdown(body_el, base=site.base)
    else:
        body_md = ""

    word_count = len(re.findall(r"\w+", body_md))

    # --- producer (best-effort) ---
    # Heuristic order: a non-generic category > body class category > leave empty
    producer = ""
    for c in categories:
        if c.lower() not in {"blog", "uncategorized", "stories", "read their stories"}:
            producer = c
            break

    return Extracted(
        url=url,
        slug=site.slug_from_url(url),
        title=title,
        date=date,
        producer=producer,
        categories=categories,
        body_markdown=body_md,
        word_count=word_count,
    )


# --------------------------------------------------------------------------- #
# HTML -> Markdown (lifted + lightly extended from scrape_csw_articles.py)    #
# --------------------------------------------------------------------------- #

def html_to_markdown(el: Tag, *, base: str) -> str:
    out_parts: list[str] = []

    def inline_md(n: Tag) -> str:
        parts: list[str] = []
        for c in n.children:
            nm = getattr(c, "name", None)
            if nm == "a":
                href = c.get("href", "")
                if href and not href.startswith("#"):
                    href = urljoin(base, href)
                    parts.append(f"[{c.get_text(' ', strip=True)}]({href})")
                else:
                    parts.append(c.get_text(" ", strip=True))
            elif nm in ("strong", "b"):
                parts.append(f"**{c.get_text(' ', strip=True)}**")
            elif nm in ("em", "i"):
                parts.append(f"*{c.get_text(' ', strip=True)}*")
            elif nm == "br":
                parts.append("  \n")
            elif nm == "img":
                src = c.get("src", "")
                alt = c.get("alt", "")
                if src:
                    parts.append(f"![{alt}]({src})")
            elif nm is None:
                parts.append(str(c))
            else:
                parts.append(c.get_text(" ", strip=True))
        return " ".join(s for s in (p.strip() for p in parts) if s)

    def walk(node, depth: int = 0) -> None:
        if hasattr(node, "children"):
            name = getattr(node, "name", None)
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(name[1])
                out_parts.append("\n" + "#" * level + " " + node.get_text(" ", strip=True) + "\n")
                return
            if name == "p":
                txt = inline_md(node)
                if txt.strip():
                    out_parts.append("\n" + txt + "\n")
                return
            if name in ("ul", "ol"):
                out_parts.append("\n")
                for li in node.find_all("li", recursive=False):
                    bullet = "-" if name == "ul" else "1."
                    out_parts.append(bullet + " " + inline_md(li) + "\n")
                out_parts.append("\n")
                return
            if name == "blockquote":
                out_parts.append("\n> " + node.get_text(" ", strip=True) + "\n")
                return
            if name == "br":
                out_parts.append("  \n")
                return
            if name == "img":
                src = node.get("src", "")
                alt = node.get("alt", "")
                if src:
                    out_parts.append(f"\n![{alt}]({src})\n")
                return
            for child in node.children:
                walk(child, depth + 1)
        else:
            text = str(node).strip()
            if text:
                out_parts.append(text)

    walk(el)
    md = "".join(out_parts)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


# --------------------------------------------------------------------------- #
# Persistence                                                                 #
# --------------------------------------------------------------------------- #

def write_markdown(site: SiteConfig, ex: Extracted) -> None:
    md_dir = VAULT / "raw" / site.name / "markdown"
    md_dir.mkdir(parents=True, exist_ok=True)

    safe_title = ex.title.replace('"', '\\"')
    cats_yaml = "[" + ", ".join(f'"{c}"' for c in ex.categories) + "]"

    lines = [
        "---",
        f"type: {site.name}_article",
        f"slug: {ex.slug}",
        f'title: "{safe_title}"',
        f"url: {ex.url}",
        f'date: "{ex.date}"',
        f'producer: "{ex.producer}"',
        f"categories: {cats_yaml}",
        f"word_count: {ex.word_count}",
        f'fetched_at: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        "---",
        "",
        f"# {ex.title}",
        "",
        ex.body_markdown,
        "",
    ]
    (md_dir / f"{ex.slug}.md").write_text("\n".join(lines), encoding="utf-8")


def log_error(site: SiteConfig, msg: str) -> None:
    log = VAULT / "raw" / site.name / "_errors.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


def upsert_index(site: SiteConfig, rows: list[dict]) -> None:
    if not rows:
        return
    csv_path = VAULT / "raw" / site.name / "articles.csv"
    fields = ["url", "slug", "title", "date", "producer", "word_count", "http_status", "fetched_at"]
    existing: dict[str, dict] = {}
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                existing[r["slug"]] = r
    for r in rows:
        existing[r["slug"]] = r
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(existing.values(), key=lambda x: x.get("date") or ""):
            # Project to known fields only (defensive against schema drift)
            w.writerow({k: r.get(k, "") for k in fields})


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #

def load_inventory(site: SiteConfig) -> list[str]:
    inv = VAULT / "raw" / site.name / "_url_inventory.txt"
    if not inv.exists():
        print(f"No inventory at {inv}. Run --build-index first.", file=sys.stderr)
        sys.exit(1)
    urls = [u.strip() for u in inv.read_text(encoding="utf-8").splitlines() if u.strip()]
    return [u for u in urls if site.article_url_filter(u)]


def run(site: SiteConfig, urls: list[str], *, force: bool, reparse_only: bool) -> None:
    html_dir = VAULT / "raw" / site.name / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    fetched = errors = skipped = 0

    for i, url in enumerate(urls, 1):
        slug = site.slug_from_url(url)
        html_path = html_dir / f"{slug}.html"

        try:
            if reparse_only:
                if not html_path.exists():
                    print(f"[{i}/{len(urls)}] {slug}  SKIP (no cached html)")
                    skipped += 1
                    continue
                html = html_path.read_text(encoding="utf-8")
                status = 200
                action = "reparse"
            else:
                if html_path.exists() and not force:
                    html = html_path.read_text(encoding="utf-8")
                    status = 200
                    action = "cached"
                else:
                    status, html = _fetch(url)
                    if status != 200:
                        log_error(site, f"{status} {url}")
                        rows.append({
                            "url": url, "slug": slug, "title": "", "date": "",
                            "producer": "", "word_count": 0, "http_status": status,
                            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        })
                        errors += 1
                        print(f"[{i}/{len(urls)}] {slug}  HTTP {status}")
                        time.sleep(DELAY_SECONDS)
                        continue
                    html_path.write_text(html, encoding="utf-8")
                    fetched += 1
                    action = "FETCH"
                    time.sleep(DELAY_SECONDS)
            print(f"[{i}/{len(urls)}] {slug}  {action}")

            ex = extract(site, url, html)
            write_markdown(site, ex)
            rows.append({
                "url": url, "slug": slug, "title": ex.title, "date": ex.date,
                "producer": ex.producer, "word_count": ex.word_count, "http_status": status,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })

        except KeyboardInterrupt:
            print("\ninterrupted — writing partial index")
            break
        except Exception as e:
            log_error(site, f"EXCEPTION {url} :: {e!r}")
            errors += 1
            print(f"[{i}/{len(urls)}] {slug}  EXCEPTION: {e}", file=sys.stderr)

    upsert_index(site, rows)
    print()
    print(f"fetched: {fetched}  (network)")
    print(f"cached/reparsed: {len(urls) - fetched - errors - skipped}")
    print(f"skipped: {skipped}")
    print(f"errors:  {errors}")
    print(f"index:   {VAULT / 'raw' / site.name / 'articles.csv'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--site", required=True, choices=sorted(SITES.keys()),
                    help="Which retailer's blog to scrape")
    ap.add_argument("--build-index", action="store_true",
                    help="Build URL inventory from wp-json + sitemap + wiki refs (+ pagination fallback)")
    ap.add_argument("--all", action="store_true", help="Fetch every URL in the inventory")
    ap.add_argument("--limit", type=int, default=0, help="Fetch only the first N URLs (dry-run)")
    ap.add_argument("--force", action="store_true", help="Re-fetch even if HTML is cached")
    ap.add_argument("--reparse", action="store_true",
                    help="Re-extract markdown from cached HTML; no network")
    ap.add_argument("--ignore-robots", action="store_true",
                    help="Proceed even if robots.txt disallows the blog index (personal-archive use)")
    args = ap.parse_args()

    site = SITES[args.site]

    if args.build_index:
        return cmd_build_index(site, ignore_robots=args.ignore_robots)

    if not args.reparse:
        ok, msg = robots_check(site, args.ignore_robots)
        print(f"[robots] {msg}")
        if not ok:
            return 2

    urls = load_inventory(site)
    if args.limit and not args.all:
        urls = urls[: args.limit]
    elif not args.all and not args.reparse:
        ap.error("Specify --all, --limit N, or --reparse")

    run(site, urls, force=args.force, reparse_only=args.reparse)
    return 0


if __name__ == "__main__":
    sys.exit(main())
