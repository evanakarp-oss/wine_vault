"""
Scrape a Wine Berserkers (Discourse) thread into a JSON post array.

Wine Berserkers runs on Discourse, which exposes thread data as JSON:

  GET /t/<slug>/<id>.json              first page + the full post-id stream
  GET /t/<id>/posts.json?post_ids[]=N  batch fetch posts (up to ~30 per call)

This script walks the full stream in batches and writes a flat JSON array of
posts to raw/berserkers/threads/<slug>.discourse.json. The shape is what
parse_wb_thread.py consumes directly.

Output post shape (each entry):
  {
    "id":         <int>,
    "username":   <str>,
    "name":       <str|null>,
    "post_number":<int>,
    "created_at": "2013-08-12T14:23:00Z",
    "updated_at": "...",
    "raw":        "<original markdown if requested>",
    "cooked":     "<rendered HTML>"
  }

`raw` is only included if the forum exposes it (some Discourse instances
require auth for raw markdown — `cooked` HTML is always available, and
parse_wb_thread.py strips tags from it as a fallback).

Usage:
    python scripts/scrape_wb_thread.py \\
        https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370

Pass `--slug <s>` to override the output filename. Pass `--throttle 1.5`
to be more polite (default 1s between batches).

If the script fails to fetch (network, rate limit, etc.), nothing is
written. The fallback path is to manually paste posts into a markdown file
(`raw/berserkers/threads/<slug>.raw.md`) using the format documented in
parse_wb_thread.py — and run parse_wb_thread.py against that.
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
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
OUT_DIR = VAULT / "raw" / "berserkers" / "threads"

USER_AGENT = "wine_vault scraper (personal knowledge base, contact: evanakarp@gmail.com)"
BATCH_SIZE = 20   # Discourse caps post_ids[] arrays around 20–30 per call


def parse_thread_url(url: str) -> tuple[str, str, int]:
    """https://www.wineberserkers.com/t/top-10-.../74370 → (origin, slug, id)."""
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Bad URL: {url}")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    m = re.match(r"^/t/([^/]+)/(\d+)/?$", parsed.path)
    if not m:
        raise ValueError(f"Not a Discourse /t/<slug>/<id> URL: {url}")
    return origin, m.group(1), int(m.group(2))


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def scrape(thread_url: str, throttle: float = 1.0,
           include_raw: bool = True) -> tuple[dict, list[dict]]:
    origin, slug, tid = parse_thread_url(thread_url)
    main_url = f"{origin}/t/{slug}/{tid}.json"
    if include_raw:
        main_url += "?include_raw=true"

    print(f"GET {main_url}")
    main = fetch_json(main_url)

    posts_seed = main.get("post_stream", {}).get("posts", [])
    stream = main.get("post_stream", {}).get("stream", [])
    title = main.get("title") or main.get("fancy_title") or slug
    posts_count = main.get("posts_count") or len(stream)
    print(f"Title: {title}")
    print(f"Stream length: {len(stream)} posts (posts_count metadata: {posts_count})")

    have: dict[int, dict] = {p["id"]: p for p in posts_seed}
    missing = [pid for pid in stream if pid not in have]
    print(f"Already have {len(have)} from seed; need {len(missing)} more")

    for batch_start in range(0, len(missing), BATCH_SIZE):
        batch = missing[batch_start:batch_start + BATCH_SIZE]
        params = "&".join(f"post_ids[]={pid}" for pid in batch)
        batch_url = f"{origin}/t/{tid}/posts.json?{params}"
        if include_raw:
            batch_url += "&include_raw=true"
        try:
            data = fetch_json(batch_url)
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} on batch {batch_start}-{batch_start+len(batch)}: {e}",
                  file=sys.stderr)
            time.sleep(throttle * 2)
            continue
        for p in data.get("post_stream", {}).get("posts", []):
            have[p["id"]] = p
        print(f"  fetched batch {batch_start//BATCH_SIZE + 1}/"
              f"{(len(missing) + BATCH_SIZE - 1)//BATCH_SIZE} "
              f"({len(have)}/{len(stream)} total)")
        time.sleep(throttle)

    posts = [have[pid] for pid in stream if pid in have]
    print(f"Final: {len(posts)} posts")

    keep_keys = ("id", "username", "name", "post_number",
                 "created_at", "updated_at", "raw", "cooked")
    posts_min = [{k: p.get(k) for k in keep_keys if k in p} for p in posts]

    thread_meta = {
        "title": title,
        "url": thread_url,
        "thread_id": tid,
        "slug": slug,
        "post_count": len(posts_min),
    }
    return thread_meta, posts_min


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="Wine Berserkers thread URL")
    ap.add_argument("--slug", help="Override output filename slug")
    ap.add_argument("--throttle", type=float, default=1.0,
                    help="Seconds between batch requests (default 1.0)")
    ap.add_argument("--no-raw", action="store_true",
                    help="Skip include_raw=true (use only cooked HTML)")
    args = ap.parse_args()

    try:
        thread_meta, posts = scrape(args.url, throttle=args.throttle,
                                    include_raw=not args.no_raw)
    except (ValueError, urllib.error.URLError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nFallback: paste posts into raw/berserkers/threads/<slug>.raw.md "
              "using the format documented in parse_wb_thread.py, then run that "
              "script directly.", file=sys.stderr)
        return 2

    slug = args.slug or thread_meta["slug"]
    out = OUT_DIR / f"{slug}.discourse.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"thread": thread_meta, "posts": posts}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"\nWrote {out}")
    print(f"\nNext: python scripts/parse_wb_thread.py {out} \\")
    print(f'        --slug {slug} \\')
    print(f'        --title "{thread_meta["title"]}" \\')
    print(f'        --thread-url {thread_meta["url"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
