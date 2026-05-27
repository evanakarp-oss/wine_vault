"""
Fetch a restaurant's published wine list and save the raw file under
raw/wine_lists/<slug>/raw/<YYYY-MM-DD>.{pdf,html}.

This is the landing layer. The downstream pipeline:

  scrape_wine_lists.py    <slug>   → raw/wine_lists/<slug>/raw/<date>.{pdf,html}
  parse_wine_list.py      <slug>   → raw/wine_lists/<slug>/snapshot_<date>.json
  diff_wine_lists.py               → build/wine_list_arrivals_<YYYY-WW>.json
  build_wine_list_view.py          → wiki/_views/wine_list_arrivals.md

stdlib only — same constraint as scrape_wb_thread.py. If the host blocks
the request (or you're running in a sandbox without internet) drop the file
manually at raw/wine_lists/<slug>/raw/<YYYY-MM-DD>.{pdf,html} and skip
straight to parse_wine_list.py.

Per-source URLs and any special discovery logic (e.g. Chambers' weekly PDF
URL changes — discovered by scraping the homepage) live in the SOURCES
registry below.

Usage:
    python scripts/scrape_wine_lists.py estela
    python scripts/scrape_wine_lists.py chambers_pours
    python scripts/scrape_wine_lists.py --all              # fetch every source
    python scripts/scrape_wine_lists.py estela --date 2026-05-27
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable

VAULT = Path(__file__).resolve().parent.parent
RAW_ROOT = VAULT / "raw" / "wine_lists"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _http_get(url: str, accept: str = "*/*", timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_static(url: str, ext: str) -> tuple[bytes, str]:
    """Fetcher for sources at a fixed URL. Returns (bytes, extension)."""
    return _http_get(url), ext


def fetch_chambers_pours() -> tuple[bytes, str]:
    """
    Chambers Street Wines hosts the weekly pour list as a PDF on a Squarespace
    CDN URL that rotates whenever the file is replaced. The stable entry point
    is chambersstwines.com — we scrape it for the current PDF URL.
    """
    home = _http_get("https://www.chambersstwines.com/", accept="text/html").decode(
        "utf-8", errors="replace"
    )
    # Squarespace asset URLs look like:
    #   https://static1.squarespace.com/static/<...>/<...>/<...>/WINE+LIST+....pdf
    matches = re.findall(
        r"https?://static1\.squarespace\.com/static/[^\"'<>\s]+?WINE[^\"'<>\s]*?\.pdf",
        home,
        flags=re.IGNORECASE,
    )
    if not matches:
        raise RuntimeError(
            "Couldn't find a WINE LIST PDF URL on chambersstwines.com. "
            "The page structure may have changed. Open the site, find the "
            "current PDF link, and either (a) update fetch_chambers_pours() "
            "in this script or (b) download the PDF manually to "
            "raw/wine_lists/chambers_pours/raw/<YYYY-MM-DD>.pdf and skip "
            "straight to parse_wine_list.py."
        )
    pdf_url = matches[0]
    print(f"  discovered PDF: {pdf_url}")
    return _http_get(pdf_url, accept="application/pdf"), "pdf"


@dataclass(frozen=True)
class Source:
    slug: str
    fetch: Callable[[], tuple[bytes, str]]


SOURCES: dict[str, Source] = {
    "chambers_pours": Source(
        "chambers_pours",
        fetch_chambers_pours,
    ),
    "estela": Source(
        "estela",
        lambda: fetch_static(
            "https://hub.binwise.com/restaurant/estela/list/estela-wine-list.pdf",
            "pdf",
        ),
    ),
    "peasant": Source(
        "peasant",
        lambda: fetch_static("https://www.peasantnyc.com/menu/wine-list/", "html"),
    ),
    "claud": Source(
        "claud",
        lambda: fetch_static("https://www.claudnyc.com/wine/", "html"),
    ),
    "noreetuh": Source(
        "noreetuh",
        lambda: fetch_static("https://www.noreetuh.com/menu", "html"),
    ),
}


def fetch_one(slug: str, snapshot_date: str, force: bool, apply: bool) -> int:
    if slug not in SOURCES:
        print(f"ERROR: unknown source '{slug}'. "
              f"Known: {', '.join(sorted(SOURCES))}", file=sys.stderr)
        return 2

    src = SOURCES[slug]
    out_dir = RAW_ROOT / slug / "raw"
    print(f"[{slug}] fetching…")
    try:
        body, ext = src.fetch()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
        print(f"  FAILED: {e}", file=sys.stderr)
        print(
            f"\n  Fallback: drop the raw file at "
            f"{out_dir.relative_to(VAULT)}/{snapshot_date}.<ext> "
            f"and skip to parse_wine_list.py.",
            file=sys.stderr,
        )
        return 1

    out_path = out_dir / f"{snapshot_date}.{ext}"
    if out_path.exists() and not force:
        print(f"  exists, skipping: {out_path.relative_to(VAULT)} "
              f"(use --force to overwrite)")
        return 0

    print(f"  {len(body):,} bytes  →  {out_path.relative_to(VAULT)}")
    if apply:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(body)
    else:
        print("  (dry-run; pass --apply to write)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("slug", nargs="?", help="Source slug (e.g. 'estela'). "
                    "Omit with --all to fetch every source.")
    ap.add_argument("--all", action="store_true",
                    help="Fetch every registered source.")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="Snapshot date (default: today, YYYY-MM-DD).")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing raw/<date>.<ext> file.")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write to disk (default: dry-run).")
    args = ap.parse_args()

    if args.all:
        targets = list(SOURCES.keys())
    elif args.slug:
        targets = [args.slug]
    else:
        ap.error("provide a slug or pass --all")

    rc = 0
    for slug in targets:
        rc |= fetch_one(slug, args.date, args.force, args.apply)
    return rc


if __name__ == "__main__":
    sys.exit(main())
