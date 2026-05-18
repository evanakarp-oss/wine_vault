"""
Scrape Wine Berserkers (Discourse) posts by a given user into raw/berserkers/<user>/.

Wine Berserkers runs Discourse, which has a clean JSON API. For each user we
want to track (William_Kelley first), we:

  1. Page through /user_actions.json?username=<U>&filter=5&offset=N to list every
     post the user has authored. Filter=5 means "Posts" (replies + topic OPs).
  2. For each unique topic_id we encountered, fetch /t/<id>.json which gives the
     full topic with all posts and metadata. Cache the raw JSON.
  3. Emit one .md per (topic, our-user-post) at:
        raw/berserkers/<username>/<topic_id>__<post_number>.md
     with YAML frontmatter capturing topic context + post metadata, and the
     post's cooked HTML converted to markdown as the body.

Politeness mirrors the blog scrapers: 1.5s between requests, exponential backoff
on 5xx, hard-stop on 429, polite identifying User-Agent. The Discourse JSON
endpoints are documented public APIs and don't require auth for public topics.

Why per-post .md and not per-topic
----------------------------------
Most Berserkers threads are long with many participants. We only care about
WK's own contributions plus the ~1 paragraph of context immediately around them
(the post he replied to). Per-post files keep the matching pass against
producer pages clean — one file = one signal — without dragging in 200 unrelated
posts from a thread.

We DO record the question/post that WK was replying to (`reply_to_excerpt:` in
frontmatter, ≤300 chars), because his answers often reference "this producer"
without naming them, and the context is needed for matching.

Output
------
  raw/berserkers/<user>/_topic_index.json          # {topic_id: {title, slug, last_post_id, last_seen}}
  raw/berserkers/<user>/_post_index.csv            # one row per scraped post
  raw/berserkers/<user>/topics/<topic_id>.json     # cached full topic JSON
  raw/berserkers/<user>/markdown/<topic_id>__<post_number>.md
  raw/berserkers/<user>/_errors.log

Frontmatter shape
-----------------
  type: berserkers_post
  user: William_Kelley
  topic_id: 172171
  topic_slug: help-me-understand-a-wine-critic-william-kelley-the-wine-advocate
  topic_title: "Help Me Understand A Wine Critic: William Kelley (The Wine Advocate)"
  topic_url: https://www.wineberserkers.com/t/.../172171
  post_id: 2299847
  post_number: 16
  post_url: https://www.wineberserkers.com/t/.../172171/16
  date: "2021-07-20"
  category: "WINE TALK"
  reply_to_user: "Glen_Gold"
  reply_to_excerpt: "Also also he understand how to use Instagram. His photo essays..."
  word_count: 187
  fetched_at: "..."

Usage
-----
  # First pass: build inventory (~few minutes for thousands of posts)
  python scripts/scrape_berserkers_user.py --user William_Kelley --build-index

  # Dry run: fetch first 5 topics
  python scripts/scrape_berserkers_user.py --user William_Kelley --limit 5

  # Full run
  python scripts/scrape_berserkers_user.py --user William_Kelley --all

  # Incremental: only new posts since last run (uses _post_index.csv high-water mark)
  python scripts/scrape_berserkers_user.py --user William_Kelley --since-last

  # Reparse cached topic JSON without re-fetching
  python scripts/scrape_berserkers_user.py --user William_Kelley --reparse

Deps: requests, beautifulsoup4
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
from typing import Iterable
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup, Tag
except ImportError as e:
    print(f"Missing dep: {e}. Run: python -m pip install --user requests beautifulsoup4", file=sys.stderr)
    sys.exit(2)


VAULT = Path(__file__).resolve().parent.parent
BASE = "https://www.wineberserkers.com"

UA = "Mozilla/5.0 (compatible; wine-research/1.0; personal archive; +local-only)"
HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
}
DELAY_SECONDS = 1.5
MAX_RETRIES = 4
BACKOFF_BASE = 2.0

# Discourse user_actions filter codes:
#   1 = likes given       4 = topics created
#   2 = likes received    5 = posts (replies + own topic OPs)  <-- what we want
USER_ACTIONS_FILTER = 5
USER_ACTIONS_PAGE_SIZE = 30  # Discourse default; documented as max ~60

REPLY_EXCERPT_CHARS = 300


# --------------------------------------------------------------------------- #
# HTTP                                                                         #
# --------------------------------------------------------------------------- #

def _fetch(url: str, *, expect_json: bool = True, timeout: int = 30) -> tuple[int, str]:
    """GET with retries + backoff. Hard stop on 429 (Discourse rate-limits aggressively)."""
    for attempt in range(MAX_RETRIES):
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 429:
            ra = r.headers.get("Retry-After", "?")
            raise RuntimeError(f"429 on {url} (Retry-After={ra}); stopping to respect rate-limit")
        if r.status_code >= 500 and attempt < MAX_RETRIES - 1:
            wait = BACKOFF_BASE ** attempt
            print(f"  {r.status_code}; retry in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r.status_code, r.text
    return r.status_code, r.text


def robots_check() -> tuple[bool, str]:
    rp = urllib.robotparser.RobotFileParser()
    try:
        r = requests.get(f"{BASE}/robots.txt", headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return True, f"no robots.txt ({r.status_code}); proceeding"
        rp.parse(r.text.splitlines())
    except Exception as e:
        return True, f"robots.txt unreachable ({e!r}); proceeding"
    # Test the canonical Discourse JSON path
    if rp.can_fetch(UA, f"{BASE}/u/Some_User/activity.json"):
        return True, "robots.txt allows /u/<user>/ JSON"
    return False, "robots.txt disallows user activity endpoint"


# --------------------------------------------------------------------------- #
# Phase 1: build post inventory via /user_actions.json                         #
# --------------------------------------------------------------------------- #

@dataclass
class PostRef:
    topic_id: int
    topic_slug: str
    topic_title: str
    post_id: int                  # Discourse global post id
    post_number: int              # 1-indexed within the topic
    created_at: str               # ISO 8601


def list_user_posts(username: str, *, max_pages: int = 1000) -> list[PostRef]:
    """Page through /user_actions.json until exhausted. Returns every (topic_id, post_number)
    the user has authored. Posts may be deleted/private (skipped silently)."""
    out: list[PostRef] = []
    seen: set[tuple[int, int]] = set()
    offset = 0
    page = 0
    while page < max_pages:
        url = (f"{BASE}/user_actions.json?offset={offset}"
               f"&username={username}&filter={USER_ACTIONS_FILTER}")
        status, text = _fetch(url)
        if status == 404:
            print(f"  user '{username}' not found", file=sys.stderr)
            return out
        if status != 200:
            print(f"  user_actions HTTP {status} at offset {offset}; stopping", file=sys.stderr)
            break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"  malformed JSON at offset {offset}; stopping", file=sys.stderr)
            break
        actions = data.get("user_actions") or []
        if not actions:
            break
        new_this_page = 0
        for a in actions:
            tid = a.get("topic_id")
            pn = a.get("post_number")
            if tid is None or pn is None:
                continue
            key = (int(tid), int(pn))
            if key in seen:
                continue
            seen.add(key)
            out.append(PostRef(
                topic_id=int(tid),
                topic_slug=a.get("slug") or "",
                topic_title=a.get("title") or "",
                post_id=int(a.get("post_id") or 0),
                post_number=int(pn),
                created_at=a.get("created_at") or "",
            ))
            new_this_page += 1
        page += 1
        print(f"  page {page}: +{new_this_page} (total {len(out)})")
        if len(actions) < USER_ACTIONS_PAGE_SIZE:
            break
        offset += len(actions)
        time.sleep(DELAY_SECONDS / 2)  # gentler: structured API
    return out


def cmd_build_index(username: str) -> int:
    user_dir = VAULT / "raw" / "berserkers" / username
    user_dir.mkdir(parents=True, exist_ok=True)

    ok, msg = robots_check()
    print(f"[robots] {msg}")
    if not ok:
        print("[robots] aborting; pass --ignore-robots to override (not impl, edit code)", file=sys.stderr)
        return 2

    print(f"Listing posts by {username}...")
    refs = list_user_posts(username)
    print(f"Found {len(refs)} unique posts")

    # Group by topic for efficient fetching downstream
    by_topic: dict[int, dict] = {}
    for r in refs:
        t = by_topic.setdefault(r.topic_id, {
            "topic_id": r.topic_id,
            "topic_slug": r.topic_slug,
            "topic_title": r.topic_title,
            "post_numbers": [],
            "first_post_at": r.created_at,
            "last_post_at": r.created_at,
        })
        t["post_numbers"].append(r.post_number)
        if r.created_at and (not t["first_post_at"] or r.created_at < t["first_post_at"]):
            t["first_post_at"] = r.created_at
        if r.created_at and (not t["last_post_at"] or r.created_at > t["last_post_at"]):
            t["last_post_at"] = r.created_at

    for t in by_topic.values():
        t["post_numbers"] = sorted(set(t["post_numbers"]))

    inv = user_dir / "_topic_index.json"
    inv.write_text(json.dumps(by_topic, indent=2, sort_keys=True), encoding="utf-8")
    print(f"  topics:  {len(by_topic)}")
    print(f"  posts:   {len(refs)}")
    print(f"  -> {inv}")
    return 0


# --------------------------------------------------------------------------- #
# Phase 2: fetch each topic, extract our user's posts                          #
# --------------------------------------------------------------------------- #

@dataclass
class TopicMeta:
    topic_id: int
    slug: str
    title: str
    category_id: int | None
    category_name: str
    posts: list[dict]                 # Discourse post objects (subset of fields we use)


def _topic_url(meta: TopicMeta) -> str:
    return f"{BASE}/t/{meta.slug}/{meta.topic_id}" if meta.slug else f"{BASE}/t/{meta.topic_id}"


def fetch_topic(topic_id: int, slug: str, cache_dir: Path) -> TopicMeta | None:
    """Fetch /t/<slug>/<id>.json. Caches raw JSON. Some topics have many pages of posts;
    we follow `post_stream.stream` and pull additional posts via /t/<id>/posts.json
    when only a partial slice was returned."""
    cache = cache_dir / f"{topic_id}.json"
    if cache.exists():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
        except Exception:
            data = None
        if data:
            return _topic_meta_from_data(data)

    url = f"{BASE}/t/{slug}/{topic_id}.json" if slug else f"{BASE}/t/{topic_id}.json"
    status, text = _fetch(url)
    if status == 404:
        return None
    if status != 200:
        print(f"  topic {topic_id}: HTTP {status}", file=sys.stderr)
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"  topic {topic_id}: malformed JSON", file=sys.stderr)
        return None

    cache.write_text(json.dumps(data, indent=2), encoding="utf-8")
    time.sleep(DELAY_SECONDS)
    return _topic_meta_from_data(data)


def _topic_meta_from_data(data: dict) -> TopicMeta:
    return TopicMeta(
        topic_id=int(data.get("id", 0)),
        slug=data.get("slug") or "",
        title=data.get("title") or "",
        category_id=data.get("category_id"),
        category_name="",  # filled by caller from category cache
        posts=(data.get("post_stream") or {}).get("posts") or [],
    )


def hydrate_topic_posts(meta: TopicMeta, wanted_post_numbers: list[int], cache_dir: Path) -> int:
    """Bulk-fetch every stream post we don't already have, in chunks of 20.

    The first /t/<id>.json request only returns a slice of post_stream.posts (~20).
    For long topics we used to walk the stream per-target-post; that re-paginates
    from the start for each WK post and never persists intermediate chunks. Now
    we fetch every missing stream id once and persist the merged cache once.

    Returns count of newly-fetched posts.
    """
    # Already have all wanted post_numbers? Nothing to do.
    have_pn = {p.get("post_number") for p in meta.posts}
    if all(pn in have_pn for pn in wanted_post_numbers):
        return 0

    cache = cache_dir / f"{meta.topic_id}.json"
    if not cache.exists():
        return 0
    try:
        raw = json.loads(cache.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0
    stream = (raw.get("post_stream") or {}).get("stream") or []
    have_ids = {p.get("id") for p in meta.posts}
    missing_ids = [pid for pid in stream if pid not in have_ids]
    if not missing_ids:
        return 0

    # We can stop once every wanted post_number is present. But Discourse
    # doesn't tell us (post_number -> post_id), so we have to fetch chunks
    # and check post_number on the returned objects. After each chunk, if all
    # wanted are satisfied, bail out — no point hydrating the rest of the topic.
    #
    # Use a deque with per-chunk attempt counts so a transient failure (DNS
    # blip, ConnectionError, non-200) doesn't permanently drop those 20 IDs.
    # Failed chunks go to the back of the queue; give up after MAX_CHUNK_ATTEMPTS.
    from collections import deque
    MAX_CHUNK_ATTEMPTS = 3
    chunk_size = 20
    chunks: deque[tuple[list[int], int]] = deque()
    buf = list(missing_ids)
    while buf:
        chunks.append((buf[:chunk_size], 0))
        buf = buf[chunk_size:]

    fetched: list[dict] = []
    while chunks:
        chunk, attempt = chunks.popleft()
        params = "&".join(f"post_ids%5B%5D={pid}" for pid in chunk)
        url = f"{BASE}/t/{meta.topic_id}/posts.json?{params}"
        try:
            status, text = _fetch(url)
        except Exception as e:
            status, text = 0, ""
            print(f"  topic {meta.topic_id}: posts.json error {e!r} (attempt {attempt+1})", file=sys.stderr)

        if status != 200:
            if status and status not in (0,):
                print(f"  topic {meta.topic_id}: posts.json HTTP {status} (attempt {attempt+1})", file=sys.stderr)
            if attempt + 1 < MAX_CHUNK_ATTEMPTS:
                chunks.append((chunk, attempt + 1))
            time.sleep(DELAY_SECONDS)
            continue
        try:
            extra = (json.loads(text).get("post_stream") or {}).get("posts") or []
        except json.JSONDecodeError:
            if attempt + 1 < MAX_CHUNK_ATTEMPTS:
                chunks.append((chunk, attempt + 1))
            time.sleep(DELAY_SECONDS)
            continue
        fetched.extend(extra)
        meta.posts.extend(extra)
        have_pn.update(p.get("post_number") for p in extra)
        time.sleep(DELAY_SECONDS)
        if all(pn in have_pn for pn in wanted_post_numbers):
            break

    if fetched:
        raw_posts = (raw.get("post_stream") or {}).get("posts") or []
        raw_posts.extend(fetched)
        cache.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    return len(fetched)


def find_post(meta: TopicMeta, post_number: int) -> dict | None:
    for p in meta.posts:
        if p.get("post_number") == post_number:
            return p
    return None


# --------------------------------------------------------------------------- #
# HTML -> Markdown (Discourse `cooked` field)                                  #
# --------------------------------------------------------------------------- #

def cooked_to_markdown(cooked_html: str) -> str:
    """Discourse's `cooked` field is sanitized HTML. Strip aside.quote (the
    inline reply blockquote — we capture that separately as reply_to_excerpt),
    images, and convert what remains to lightweight markdown."""
    soup = BeautifulSoup(cooked_html or "", "html.parser")
    for tag in soup.select("aside.quote, .meta, .quote-controls"):
        tag.decompose()

    out: list[str] = []

    def inline(node) -> str:
        parts: list[str] = []
        for c in node.children:
            nm = getattr(c, "name", None)
            if nm == "a":
                txt = c.get_text(" ", strip=True)
                href = c.get("href", "")
                if href and txt:
                    parts.append(f"[{txt}]({href})")
                else:
                    parts.append(txt)
            elif nm in ("strong", "b"):
                parts.append(f"**{c.get_text(' ', strip=True)}**")
            elif nm in ("em", "i"):
                parts.append(f"*{c.get_text(' ', strip=True)}*")
            elif nm == "br":
                parts.append("  \n")
            elif nm == "img":
                continue  # skip emoji/avatars
            elif nm is None:
                parts.append(str(c))
            else:
                parts.append(c.get_text(" ", strip=True))
        return " ".join(s for s in (p.strip() for p in parts) if s)

    def walk(node) -> None:
        for el in node.children:
            name = getattr(el, "name", None)
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                lvl = int(name[1])
                out.append("\n" + "#" * lvl + " " + el.get_text(" ", strip=True) + "\n")
            elif name == "p":
                t = inline(el)
                if t.strip():
                    out.append("\n" + t + "\n")
            elif name == "blockquote":
                t = el.get_text("\n", strip=True)
                if t:
                    for line in t.splitlines():
                        out.append("> " + line)
                    out.append("")
            elif name in ("ul", "ol"):
                out.append("\n")
                for li in el.find_all("li", recursive=False):
                    bullet = "-" if name == "ul" else "1."
                    out.append(bullet + " " + inline(li) + "\n")
                out.append("\n")
            elif name == "pre":
                code = el.get_text("\n", strip=False)
                out.append("\n```\n" + code.rstrip() + "\n```\n")
            elif name is None:
                t = str(el).strip()
                if t:
                    out.append(t)
            else:
                walk(el)

    walk(soup)
    md = "".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def extract_reply_excerpt(cooked_html: str) -> tuple[str, str]:
    """Pull the `aside.quote` block that Discourse renders for an in-line reply.
    Returns (quoted_username, excerpt). If multiple quotes (rare), takes the first."""
    soup = BeautifulSoup(cooked_html or "", "html.parser")
    aside = soup.select_one("aside.quote")
    if not aside:
        return "", ""
    user = ""
    title_div = aside.select_one(".title")
    if title_div:
        a = title_div.find("a")
        if a:
            href = a.get("href", "")
            m = re.search(r"/u/([^/]+)", href)
            if m:
                user = m.group(1)
    blockquote = aside.find("blockquote")
    text = blockquote.get_text(" ", strip=True) if blockquote else ""
    text = re.sub(r"\s+", " ", text)
    if len(text) > REPLY_EXCERPT_CHARS:
        cut = text[:REPLY_EXCERPT_CHARS]
        if " " in cut:
            cut = cut[: cut.rfind(" ")]
        text = cut + "…"
    return user, text


# --------------------------------------------------------------------------- #
# Persistence                                                                  #
# --------------------------------------------------------------------------- #

def _date_only(iso: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", iso or "")
    return m.group(0) if m else ""


def write_post_md(user: str, meta: TopicMeta, post: dict, out_dir: Path) -> Path:
    cooked = post.get("cooked") or ""
    body_md = cooked_to_markdown(cooked)
    reply_user, reply_excerpt = extract_reply_excerpt(cooked)
    word_count = len(re.findall(r"\w+", body_md))

    pn = int(post.get("post_number", 0))
    topic_url = _topic_url(meta)
    post_url = f"{topic_url}/{pn}"
    safe_title = (meta.title or "").replace('"', '\\"')
    safe_excerpt = reply_excerpt.replace('"', '\\"')

    fm = [
        "---",
        "type: berserkers_post",
        f"user: {user}",
        f"topic_id: {meta.topic_id}",
        f"topic_slug: {meta.slug}",
        f'topic_title: "{safe_title}"',
        f"topic_url: {topic_url}",
        f"post_id: {int(post.get('id', 0))}",
        f"post_number: {pn}",
        f"post_url: {post_url}",
        f'date: "{_date_only(post.get("created_at", ""))}"',
        f'category: "{meta.category_name}"',
        f'reply_to_user: "{reply_user}"',
        f'reply_to_excerpt: "{safe_excerpt}"',
        f"word_count: {word_count}",
        f'fetched_at: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        "---",
        "",
    ]
    if reply_excerpt:
        fm += [
            f"> *Replying to {reply_user}:*  ",
            f"> {reply_excerpt}",
            "",
        ]
    fm += [body_md, ""]

    path = out_dir / f"{meta.topic_id}__{pn:04d}.md"
    path.write_text("\n".join(fm), encoding="utf-8")
    return path


def upsert_post_index(user_dir: Path, rows: list[dict]) -> None:
    if not rows:
        return
    csv_path = user_dir / "_post_index.csv"
    fields = ["topic_id", "post_number", "post_id", "date", "topic_title",
              "category", "reply_to_user", "word_count", "post_url", "fetched_at"]
    existing: dict[tuple[str, str], dict] = {}
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                existing[(r["topic_id"], r["post_number"])] = r
    for r in rows:
        existing[(str(r["topic_id"]), str(r["post_number"]))] = r
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(existing.values(), key=lambda x: (x.get("date") or "", str(x.get("topic_id") or ""))):
            w.writerow({k: r.get(k, "") for k in fields})


def log_error(user: str, msg: str) -> None:
    log = VAULT / "raw" / "berserkers" / user / "_errors.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


# --------------------------------------------------------------------------- #
# Category resolution (one fetch, cached)                                      #
# --------------------------------------------------------------------------- #

_CATEGORY_CACHE: dict[int, str] = {}


def load_categories() -> None:
    """One-shot: fetch /categories.json, build {id: name}. Cheap; cached in memory."""
    if _CATEGORY_CACHE:
        return
    try:
        status, text = _fetch(f"{BASE}/categories.json")
        if status != 200:
            return
        data = json.loads(text)
        for c in (data.get("category_list") or {}).get("categories") or []:
            cid = c.get("id")
            name = c.get("name") or ""
            if cid is not None:
                _CATEGORY_CACHE[int(cid)] = name
            for sub in c.get("subcategory_list") or []:
                sid = sub.get("id")
                sname = sub.get("name") or ""
                if sid is not None:
                    _CATEGORY_CACHE[int(sid)] = sname
        time.sleep(DELAY_SECONDS / 2)
    except Exception as e:
        print(f"  categories load failed: {e!r}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# Orchestration                                                                #
# --------------------------------------------------------------------------- #

def load_topic_index(user_dir: Path) -> dict[int, dict]:
    inv = user_dir / "_topic_index.json"
    if not inv.exists():
        print(f"No topic index at {inv}. Run --build-index first.", file=sys.stderr)
        sys.exit(1)
    raw = json.loads(inv.read_text(encoding="utf-8"))
    return {int(k): v for k, v in raw.items()}


def latest_seen_iso(user_dir: Path) -> str:
    csv_path = user_dir / "_post_index.csv"
    if not csv_path.exists():
        return ""
    latest = ""
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            d = r.get("date") or ""
            if d > latest:
                latest = d
    return latest


def run(user: str, *, limit: int, all_: bool, since_last: bool, reparse_only: bool) -> int:
    user_dir = VAULT / "raw" / "berserkers" / user
    md_dir = user_dir / "markdown"
    cache_dir = user_dir / "topics"
    md_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    by_topic = load_topic_index(user_dir)

    if since_last:
        cutoff = latest_seen_iso(user_dir)
        if cutoff:
            print(f"[since-last] cutoff = {cutoff}")
            by_topic = {tid: t for tid, t in by_topic.items()
                        if (t.get("last_post_at") or "")[:10] >= cutoff}
            print(f"[since-last] {len(by_topic)} topics have activity at/after cutoff")

    topic_ids = sorted(by_topic.keys(), key=lambda tid: by_topic[tid].get("last_post_at", ""), reverse=True)
    if limit and not all_:
        topic_ids = topic_ids[:limit]
    elif not all_ and not reparse_only:
        print("Specify --all, --limit N, --since-last, or --reparse", file=sys.stderr)
        return 2

    if not reparse_only:
        load_categories()

    rows: list[dict] = []
    written = errors = skipped = 0

    for i, tid in enumerate(topic_ids, 1):
        info = by_topic[tid]
        slug = info.get("topic_slug") or ""
        wanted = info.get("post_numbers") or []
        try:
            if reparse_only:
                cache_path = cache_dir / f"{tid}.json"
                if not cache_path.exists():
                    skipped += 1
                    print(f"[{i}/{len(topic_ids)}] {tid}  SKIP (no cached topic)")
                    continue
                meta = _topic_meta_from_data(json.loads(cache_path.read_text(encoding="utf-8")))
            else:
                meta = fetch_topic(tid, slug, cache_dir)
                if meta is None:
                    log_error(user, f"topic {tid}: fetch failed")
                    errors += 1
                    continue

            meta.category_name = _CATEGORY_CACHE.get(meta.category_id or -1, "")

            if not reparse_only:
                hydrate_topic_posts(meta, wanted, cache_dir)

            for pn in wanted:
                post = find_post(meta, pn)
                if not post:
                    log_error(user, f"topic {tid} post {pn}: not found in stream")
                    errors += 1
                    continue
                if (post.get("username") or "").lower() != user.lower():
                    # Sanity: user_actions should only return our user's posts, but skip if a topic was edited
                    continue
                path = write_post_md(user, meta, post, md_dir)
                written += 1
                rows.append({
                    "topic_id": tid,
                    "post_number": pn,
                    "post_id": int(post.get("id", 0)),
                    "date": _date_only(post.get("created_at", "")),
                    "topic_title": meta.title,
                    "category": meta.category_name,
                    "reply_to_user": extract_reply_excerpt(post.get("cooked", ""))[0],
                    "word_count": len(re.findall(r"\w+", cooked_to_markdown(post.get("cooked", "")))),
                    "post_url": f"{_topic_url(meta)}/{pn}",
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                })

            print(f"[{i}/{len(topic_ids)}] {tid}  posts={len(wanted)}  '{meta.title[:60]}'")

        except KeyboardInterrupt:
            print("\ninterrupted — writing partial index")
            break
        except Exception as e:
            log_error(user, f"EXCEPTION topic {tid} :: {e!r}")
            errors += 1
            print(f"[{i}/{len(topic_ids)}] {tid}  EXCEPTION: {e}", file=sys.stderr)

    upsert_post_index(user_dir, rows)
    print()
    print(f"posts written: {written}")
    print(f"topics seen:   {len(topic_ids)}")
    print(f"skipped:       {skipped}")
    print(f"errors:        {errors}")
    print(f"index:         {user_dir / '_post_index.csv'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--user", required=True, help="Discourse username (case-sensitive)")
    ap.add_argument("--build-index", action="store_true",
                    help="Page user_actions.json to enumerate every post by --user")
    ap.add_argument("--all", action="store_true", help="Fetch every topic in the index")
    ap.add_argument("--limit", type=int, default=0, help="Fetch only the most-recent N topics (dry-run)")
    ap.add_argument("--since-last", action="store_true",
                    help="Only topics with last_post_at >= newest date in _post_index.csv")
    ap.add_argument("--reparse", action="store_true",
                    help="Re-emit markdown from cached topic JSON; no network")
    args = ap.parse_args()

    # Line-buffer stdout so progress is visible when redirected to a log file.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    if args.build_index:
        return cmd_build_index(args.user)

    if not args.reparse:
        ok, msg = robots_check()
        print(f"[robots] {msg}")
        if not ok:
            return 2

    return run(
        args.user,
        limit=args.limit,
        all_=args.all,
        since_last=args.since_last,
        reparse_only=args.reparse,
    )


if __name__ == "__main__":
    sys.exit(main())
