"""
Scrape Chambers Street Wines blog articles into raw/csw/.

Polite-by-default: 1.5s between requests, User-Agent identifying this as a
personal research crawler, exponential backoff on 5xx, hard-stop on 429.
Idempotent: re-runs skip URLs already on disk (override with --force).

Data flow
---------
  URL inventory -> raw/csw/_url_inventory.txt  (sitemap ∪ wiki-referenced URLs)
  raw HTML     -> raw/csw/html/<slug>.html
  extracted MD -> raw/csw/markdown/<slug>.md   (YAML frontmatter + body)
  index        -> raw/csw/articles.csv         (url, slug, title, date, word_count, fetched_at, http_status)
  errors       -> raw/csw/_errors.log

Usage
-----
  # Build the URL inventory (sitemap + wiki back-references, deduped)
  python scripts/scrape_csw_articles.py --build-index

  # Dry run: fetch N URLs, verify extractor shape
  python scripts/scrape_csw_articles.py --limit 3

  # Full run
  python scripts/scrape_csw_articles.py --all

  # Re-parse cached HTML into markdown without re-fetching
  python scripts/scrape_csw_articles.py --reparse

Deps: requests, beautifulsoup4, lxml
  uv pip install requests beautifulsoup4 lxml
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing dep: {e}. Run: python -m pip install --user requests beautifulsoup4", file=sys.stderr)
    sys.exit(2)

import xml.etree.ElementTree as ET


VAULT = Path(__file__).resolve().parent.parent
RAW_CSW = VAULT / "raw" / "csw"
HTML_DIR = RAW_CSW / "html"
MD_DIR = RAW_CSW / "markdown"
INVENTORY = RAW_CSW / "_url_inventory.txt"
INDEX_CSV = RAW_CSW / "articles.csv"
ERRORS_LOG = RAW_CSW / "_errors.log"

BASE = "https://chambersstwines.com"
SITEMAP_URL = f"{BASE}/sitemap_blogs_1.xml"
ARTICLE_PREFIX = f"{BASE}/blogs/articles/"

# Identify ourselves clearly. Keep a plausible UA string — Shopify sometimes
# 403s obvious bots, but we aren't pretending to be a browser.
UA = "Mozilla/5.0 (compatible; wine-research/1.0; personal archive; +local-only)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

DELAY_SECONDS = 1.5
MAX_RETRIES = 4
BACKOFF_BASE = 2.0


# --------------------------------------------------------------------------- #
# URL inventory
# --------------------------------------------------------------------------- #

def slug_from_url(url: str) -> str:
    """Last path segment. 'https://chambersstwines.com/blogs/articles/foo-bar' -> 'foo-bar'."""
    path = urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1]


def urls_from_sitemap() -> list[tuple[str, str]]:
    """Fetch blogs sitemap, return [(url, lastmod)] for /blogs/articles/* only."""
    r = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    # Sitemap is XML with a default namespace — strip it for simpler access.
    xml_text = re.sub(r'\sxmlns="[^"]+"', "", r.text, count=1)
    root = ET.fromstring(xml_text)
    out = []
    for url_el in root.findall("url"):
        loc = (url_el.findtext("loc") or "").strip()
        lastmod = (url_el.findtext("lastmod") or "").strip()
        if loc.startswith(ARTICLE_PREFIX):
            out.append((loc, lastmod))
    return out


def urls_from_wiki() -> list[str]:
    """Scrape /blogs/articles/<slug> links from existing wiki/producers/*.md + _drive_sync/*.md."""
    out: set[str] = set()
    url_re = re.compile(r"\(https://chambersstwines\.com/blogs/articles/([^)\s]+)\)")
    for d in (VAULT / "wiki" / "producers", VAULT / "_drive_sync"):
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            for m in url_re.finditer(f.read_text(encoding="utf-8", errors="ignore")):
                slug = m.group(1).rstrip("!.,;:)")
                out.add(f"{ARTICLE_PREFIX}{slug}")
    return sorted(out)


def cmd_build_index() -> int:
    RAW_CSW.mkdir(parents=True, exist_ok=True)
    sitemap = urls_from_sitemap()
    wiki = urls_from_wiki()

    all_urls = {u for u, _ in sitemap} | set(wiki)
    INVENTORY.write_text("\n".join(sorted(all_urls)) + "\n", encoding="utf-8")
    print(f"sitemap: {len(sitemap)} articles")
    print(f"wiki refs: {len(wiki)} articles")
    print(f"union:    {len(all_urls)} unique URLs -> {INVENTORY}")
    return 0


# --------------------------------------------------------------------------- #
# Fetch + extract
# --------------------------------------------------------------------------- #

@dataclass
class Extracted:
    url: str
    slug: str
    title: str
    date: str
    body_markdown: str
    word_count: int


def fetch(url: str) -> tuple[int, str]:
    """GET with retries and backoff. Returns (status_code, text)."""
    for attempt in range(MAX_RETRIES):
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429:
            # Hard stop — they're asking us to back off. Don't try to outsmart them.
            raise RuntimeError(f"429 on {url}; stopping to respect rate-limit")
        if r.status_code >= 500 and attempt < MAX_RETRIES - 1:
            wait = BACKOFF_BASE ** attempt
            print(f"  {r.status_code}; retry in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r.status_code, r.text
    return r.status_code, r.text  # last attempt


def extract(url: str, html: str) -> Extracted:
    """Parse Shopify blog article HTML with several fallback selectors."""
    soup = BeautifulSoup(html, "html.parser")

    # --- title: og:title -> article h1 -> page h1 -> <title>
    title = ""
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        title = og["content"].strip()
    if not title:
        art = soup.find("article")
        if art:
            h1 = art.find("h1")
            if h1:
                title = h1.get_text(strip=True)
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    # --- date: article:published_time -> <time datetime> -> inline byline "M/D/YYYY -"
    date = ""
    meta_date = soup.find("meta", property="article:published_time")
    if meta_date and meta_date.get("content"):
        date = meta_date["content"][:10]  # YYYY-MM-DD
    if not date:
        t = soup.find("time")
        if t and t.get("datetime"):
            date = t["datetime"][:10]
    if not date:
        # Chambers puts the date as the first inline text in the article body, e.g. "3/19/2007 -"
        body_text = soup.get_text("\n")
        m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", body_text[:500])
        if m:
            mm, dd, yy = m.groups()
            y = int(yy)
            if y < 100:
                y = 2000 + y if y < 50 else 1900 + y
            date = f"{y:04d}-{int(mm):02d}-{int(dd):02d}"

    # --- body: try common Shopify classes, then fall back to <article> minus header
    body_el = None
    for sel in [
        ("div", {"class": "article__content"}),
        ("div", {"class": "article-body"}),
        ("div", {"class": "rte"}),
        ("section", {"class": "article__body"}),
        ("article", {}),
    ]:
        tag, attrs = sel
        body_el = soup.find(tag, attrs=attrs) if attrs else soup.find(tag)
        if body_el:
            break

    # Convert body to minimal markdown
    if body_el:
        # Remove scripts, styles, embedded share-buttons, newsletter widgets
        for bad in body_el.select("script, style, noscript, iframe, .share, .social, form, .newsletter"):
            bad.decompose()
        body_md = html_to_markdown(body_el)
    else:
        body_md = ""

    word_count = len(re.findall(r"\w+", body_md))
    return Extracted(url=url, slug=slug_from_url(url), title=title, date=date,
                     body_markdown=body_md, word_count=word_count)


def html_to_markdown(el) -> str:
    """Minimal HTML -> Markdown converter tuned for Shopify blog prose.
    We don't need perfect fidelity — the point is readable body text that preserves
    paragraph breaks, headings, lists, emphasis, and links."""
    out_parts: list[str] = []

    def walk(node, depth=0):
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
                for li in node.find_all("li", recursive=False):
                    bullet = "-" if name == "ul" else "1."
                    out_parts.append(bullet + " " + inline_md(li))
                out_parts.append("")
                return
            if name == "blockquote":
                out_parts.append("\n> " + node.get_text(" ", strip=True) + "\n")
                return
            if name == "br":
                out_parts.append("  \n")
                return
            if name in ("img",):
                src = node.get("src", "")
                alt = node.get("alt", "")
                if src:
                    out_parts.append(f"\n![{alt}]({src})\n")
                return
            # default: recurse children
            for child in node.children:
                walk(child, depth + 1)
        else:
            text = str(node).strip()
            if text:
                out_parts.append(text)

    def inline_md(n) -> str:
        parts: list[str] = []
        for c in n.children:
            nm = getattr(c, "name", None)
            if nm == "a":
                href = c.get("href", "")
                if href and not href.startswith("#"):
                    href = urljoin(BASE, href)
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

    walk(el)
    md = "".join(out_parts)
    # Collapse 3+ blank lines
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def write_markdown(ex: Extracted) -> None:
    lines = [
        "---",
        "type: csw_article",
        f"slug: {ex.slug}",
        f'title: "{ex.title.replace(chr(34), chr(92) + chr(34))}"',
        f"url: {ex.url}",
        f'date: "{ex.date}"',
        f"word_count: {ex.word_count}",
        f'fetched_at: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        "---",
        "",
        f"# {ex.title}",
        "",
        ex.body_markdown,
        "",
    ]
    out = MD_DIR / f"{ex.slug}.md"
    out.write_text("\n".join(lines), encoding="utf-8")


def write_index(rows: list[dict]) -> None:
    new_file = not INDEX_CSV.exists()
    with INDEX_CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "slug", "title", "date", "word_count", "http_status", "fetched_at"])
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def log_error(msg: str) -> None:
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def load_inventory() -> list[str]:
    if not INVENTORY.exists():
        print(f"No inventory at {INVENTORY}. Run --build-index first.", file=sys.stderr)
        sys.exit(1)
    urls = [u.strip() for u in INVENTORY.read_text(encoding="utf-8").splitlines() if u.strip()]
    # Only real article URLs
    return [u for u in urls if u.startswith(ARTICLE_PREFIX)]


def run(urls: list[str], *, force: bool, reparse_only: bool) -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    fetched = 0
    skipped = 0
    errors = 0

    for i, url in enumerate(urls, 1):
        slug = slug_from_url(url)
        html_path = HTML_DIR / f"{slug}.html"

        try:
            if reparse_only:
                if not html_path.exists():
                    print(f"[{i}/{len(urls)}] {slug}  SKIP (no cached html)")
                    skipped += 1
                    continue
                html = html_path.read_text(encoding="utf-8")
                status = 200
            else:
                if html_path.exists() and not force:
                    html = html_path.read_text(encoding="utf-8")
                    status = 200
                    action = "cached"
                else:
                    status, html = fetch(url)
                    if status != 200:
                        log_error(f"{status} {url}")
                        rows.append({"url": url, "slug": slug, "title": "", "date": "",
                                     "word_count": 0, "http_status": status,
                                     "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
                        errors += 1
                        print(f"[{i}/{len(urls)}] {slug}  HTTP {status}")
                        time.sleep(DELAY_SECONDS)
                        continue
                    html_path.write_text(html, encoding="utf-8")
                    fetched += 1
                    action = "FETCH"
                    time.sleep(DELAY_SECONDS)
                print(f"[{i}/{len(urls)}] {slug}  {action if not reparse_only else 'reparse'}")

            ex = extract(url, html)
            write_markdown(ex)
            rows.append({"url": url, "slug": slug, "title": ex.title, "date": ex.date,
                         "word_count": ex.word_count, "http_status": status,
                         "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})

        except KeyboardInterrupt:
            print("\ninterrupted — writing partial index")
            break
        except Exception as e:
            log_error(f"EXCEPTION {url} :: {e!r}")
            errors += 1
            print(f"[{i}/{len(urls)}] {slug}  EXCEPTION: {e}", file=sys.stderr)

    # Rewrite index (deduping on slug, last write wins)
    if rows:
        existing: dict[str, dict] = {}
        if INDEX_CSV.exists():
            with INDEX_CSV.open("r", encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    existing[r["slug"]] = r
        for r in rows:
            existing[r["slug"]] = r
        with INDEX_CSV.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["url", "slug", "title", "date", "word_count", "http_status", "fetched_at"])
            w.writeheader()
            for r in sorted(existing.values(), key=lambda x: x.get("date") or ""):
                w.writerow(r)

    print()
    print(f"fetched: {fetched}  (network)")
    print(f"cached:  {len(urls) - fetched - errors - skipped}")
    print(f"skipped: {skipped}")
    print(f"errors:  {errors}")
    print(f"index:   {INDEX_CSV}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-index", action="store_true", help="Build URL inventory from sitemap ∪ wiki refs")
    ap.add_argument("--all", action="store_true", help="Fetch every URL in the inventory")
    ap.add_argument("--limit", type=int, default=0, help="Fetch only the first N URLs (useful for dry-run)")
    ap.add_argument("--force", action="store_true", help="Re-fetch even if HTML is cached")
    ap.add_argument("--reparse", action="store_true", help="Re-extract markdown from cached HTML; no network")
    args = ap.parse_args()

    if args.build_index:
        return cmd_build_index()

    urls = load_inventory()
    if args.limit and not args.all:
        urls = urls[: args.limit]
    elif not args.all and not args.reparse:
        ap.error("Specify --all or --limit N or --reparse")

    run(urls, force=args.force, reparse_only=args.reparse)
    return 0


if __name__ == "__main__":
    sys.exit(main())
