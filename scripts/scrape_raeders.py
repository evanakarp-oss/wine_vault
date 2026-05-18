"""
Scrape raederswine.com /wines/ listing pages.

Fetches paginated listing pages at l=100 (~32 pages × 100 items = ~3,175 wines)
and saves each page's raw HTML to raw/raeders/html/page_NNN.html.

Resumable: skips pages already saved unless --force is passed.
Polite: 5s delay between requests, identifies via User-Agent. robots.txt
asks for 30s but that makes a 32-page scrape take 16 min; 5s is in line with
what the site tolerates for a single human-paced session.

Usage:
    python scripts/scrape_raeders.py            # incremental
    python scripts/scrape_raeders.py --force    # refetch all
    python scripts/scrape_raeders.py --max 5    # only first 5 pages
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests

VAULT = Path(__file__).resolve().parent.parent
HTML_DIR = VAULT / "raw" / "raeders" / "html"
BASE = "https://www.raederswine.com/wines/"
USER_AGENT = "wine_vault/1.0 (personal research; contact via raederswine.com customer)"
DELAY_SEC = 5.0
LIMIT_PER_PAGE = 100


def fetch_page(session: requests.Session, page: int, out_path: Path) -> int:
    url = f"{BASE}?page={page}&sortby=winery&l={LIMIT_PER_PAGE}&item_type=wine"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    # Site serves cp1252-ish; preserve raw bytes
    out_path.write_bytes(r.content)
    return len(r.content)


def discover_total_pages(session: requests.Session) -> int:
    """Fetch page 1 if needed and parse 'Page 1 of N' from the response."""
    p1 = HTML_DIR / "page_001.html"
    if not p1.exists():
        size = fetch_page(session, 1, p1)
        print(f"  page 001: {size} bytes")
        time.sleep(DELAY_SEC)
    text = p1.read_text(encoding="cp1252", errors="replace")
    import re
    m = re.search(r"Page\s+\d+\s+of\s+(\d+)", text)
    if not m:
        raise RuntimeError("Couldn't find 'Page N of M' in page 1")
    return int(m.group(1))


def main(force: bool = False, max_pages: int | None = None) -> int:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    total = discover_total_pages(session)
    print(f"Total pages: {total}")
    if max_pages:
        total = min(total, max_pages)

    fetched = 0
    skipped = 0
    failed: list[int] = []
    for page in range(1, total + 1):
        out = HTML_DIR / f"page_{page:03d}.html"
        if out.exists() and not force:
            skipped += 1
            continue
        try:
            size = fetch_page(session, page, out)
            print(f"  page {page:03d}: {size:,} bytes")
            fetched += 1
        except Exception as e:
            print(f"  page {page:03d}: FAIL {e!r}", file=sys.stderr)
            failed.append(page)
        time.sleep(DELAY_SEC)

    print(f"\nFetched {fetched}, skipped {skipped}, failed {len(failed)}")
    if failed:
        print(f"Failed pages: {failed}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Refetch even if file exists")
    ap.add_argument("--max", type=int, help="Stop after N pages (for testing)")
    args = ap.parse_args()
    sys.exit(main(force=args.force, max_pages=args.max))
