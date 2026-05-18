"""
Scrape argentinareloaded.com — Paz Levinson's curated Argentine winemaker
showcase. Polite-by-default: 1.5s delay between requests, identifying UA,
exponential backoff on 5xx, hard-stop on 429. Idempotent: cached HTML is
reused unless --force is passed.

Data flow
---------
  homepage  -> raw/argentina_reloaded/html/index.html
  talents   -> raw/argentina_reloaded/html/talent_<slug>.html
  index     -> raw/argentina_reloaded/talents.csv  (slug,name,url,wineries,fetched_at)
  errors    -> raw/argentina_reloaded/_errors.log

Cross-validation report (build/argentina_reloaded_validation.md):
  - AR talents matched to wiki producers (via winemaker field fuzzy match)
  - AR talents NOT matched in wiki (gaps to investigate)
  - Wiki producers tagged with an argentina_reloaded event but not found on AR site

Usage
-----
  python scripts/scrape_argentina_reloaded.py --build-index   # fetch homepage, list talents
  python scripts/scrape_argentina_reloaded.py --all           # fetch every talent page
  python scripts/scrape_argentina_reloaded.py --validate      # wiki cross-check (no fetch)

Deps: requests, beautifulsoup4
  python -m pip install --user requests beautifulsoup4
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing dep: {e}. Run: python -m pip install --user requests beautifulsoup4", file=sys.stderr)
    sys.exit(2)


VAULT = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT / "raw" / "argentina_reloaded"
HTML_DIR = RAW_DIR / "html"
TALENTS_CSV = RAW_DIR / "talents.csv"
ERRORS_LOG = RAW_DIR / "_errors.log"
VALIDATION_REPORT = VAULT / "build" / "argentina_reloaded_validation.md"
PRODUCERS_DIR = VAULT / "wiki" / "producers"

BASE = "https://argentinareloaded.com"
UA = "Mozilla/5.0 (compatible; wine-research/1.0; personal archive; +local-only)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"}
DELAY_SECONDS = 1.5
MAX_RETRIES = 4
BACKOFF_BASE = 2.0


def log_error(msg: str) -> None:
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")


def polite_get(url: str, cache_path: Path | None = None, force: bool = False) -> str | None:
    """GET with caching, backoff, and friendly UA. Returns body or None on hard fail."""
    if cache_path and cache_path.exists() and not force:
        return cache_path.read_text(encoding="utf-8", errors="replace")
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 429:
                log_error(f"429 hard-stop on {url}")
                return None
            if 500 <= r.status_code < 600:
                wait = BACKOFF_BASE ** attempt
                log_error(f"{r.status_code} retry {attempt + 1} on {url} (wait {wait:.1f}s)")
                time.sleep(wait)
                continue
            r.raise_for_status()
            time.sleep(DELAY_SECONDS)
            if cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(r.text, encoding="utf-8")
            return r.text
        except requests.RequestException as e:
            log_error(f"{type(e).__name__} on {url}: {e}")
            time.sleep(BACKOFF_BASE ** attempt)
    return None


@dataclass
class Talent:
    slug: str
    name: str
    url: str
    wineries: list[str] = field(default_factory=list)
    bio_excerpt: str = ""


def parse_talents(html: str) -> list[Talent]:
    """Extract /talents/<slug>/ links from the homepage."""
    soup = BeautifulSoup(html, "html.parser")
    seen: dict[str, Talent] = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/talents/([^/?#]+)/?", href)
        if not m:
            continue
        slug = m.group(1)
        name = a.get_text(strip=True) or slug.replace("-", " ").title()
        url = urljoin(BASE, href)
        if slug in seen and len(seen[slug].name) >= len(name):
            continue
        seen[slug] = Talent(slug=slug, name=name, url=url)
    return sorted(seen.values(), key=lambda t: t.name.lower())


def parse_talent_detail(html: str) -> tuple[list[str], str]:
    """Best-effort extraction of winery names and bio excerpt from a /talents/X/ page."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    paragraphs = [line for line in text.splitlines() if len(line) > 60][:3]
    bio = " ".join(paragraphs)[:600]
    wineries: list[str] = []
    for cap in re.findall(r"\b((?:Bodega|Finca|Domaine|Casa|Familia|Altos)\s+[A-Z][\w\sÁÉÍÓÚÑáéíóúñ&\.\-]+?)(?=[\.,\n;])", text):
        cap = cap.strip()
        if cap and cap not in wineries:
            wineries.append(cap)
    return wineries[:6], bio


def cmd_build_index(force: bool) -> int:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    home_path = HTML_DIR / "index.html"
    html = polite_get(BASE + "/", home_path, force=force)
    if not html:
        print("Failed to fetch homepage", file=sys.stderr)
        return 1
    talents = parse_talents(html)
    if not talents:
        print("No talents found on homepage", file=sys.stderr)
        return 1

    with TALENTS_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["slug", "name", "url", "wineries", "fetched_at"])
        for t in talents:
            w.writerow([t.slug, t.name, t.url, "", datetime.now(timezone.utc).isoformat()])

    print(f"OK: {len(talents)} talents -> {TALENTS_CSV.relative_to(VAULT)}")
    return 0


def cmd_all(force: bool, limit: int | None) -> int:
    if not TALENTS_CSV.exists():
        print("Run --build-index first", file=sys.stderr)
        return 1
    rows = list(csv.DictReader(TALENTS_CSV.open(encoding="utf-8")))
    if limit:
        rows = rows[:limit]

    enriched: list[Talent] = []
    for i, row in enumerate(rows, 1):
        slug = row["slug"]
        cache_path = HTML_DIR / f"talent_{slug}.html"
        print(f"[{i}/{len(rows)}] {row['name']}")
        html = polite_get(row["url"], cache_path, force=force)
        wineries: list[str] = []
        bio = ""
        if html:
            wineries, bio = parse_talent_detail(html)
        enriched.append(Talent(slug=slug, name=row["name"], url=row["url"], wineries=wineries, bio_excerpt=bio))

    with TALENTS_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["slug", "name", "url", "wineries", "fetched_at"])
        for t in enriched:
            w.writerow([t.slug, t.name, t.url, " | ".join(t.wineries),
                        datetime.now(timezone.utc).isoformat()])

    print(f"OK: enriched {len(enriched)} talents")
    return 0


# --- cross-validation against wiki ---

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def normalize_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9\s]", " ", s).lower()
    return re.sub(r"\s+", " ", s).strip()


def name_tokens(s: str) -> set[str]:
    base = {"the", "and", "&", "i", "y"}
    return {tok for tok in normalize_name(s).split() if tok and tok not in base and len(tok) > 2}


def load_wiki_argentina_producers() -> list[dict]:
    out = []
    for path in sorted(PRODUCERS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        if not m:
            continue
        fm = m.group(1)
        country_m = re.search(r'^country:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
        if not country_m or country_m.group(1).strip() != "Argentina":
            continue
        slug_m = re.search(r"^slug:\s*(\S+)", fm, re.MULTILINE)
        name_m = re.search(r'^name:\s*"([^"]*)"', fm, re.MULTILINE)
        events_m = re.search(r'^events:\s*\[(.*?)\]', fm, re.MULTILINE)
        events = []
        if events_m and events_m.group(1).strip():
            events = re.findall(r'"([^"]*)"', events_m.group(1))
        body = text[m.end():]
        winemaker_m = re.search(r"Winemaker:\s*\*\*([^*]+)\*\*", body)
        winemaker = winemaker_m.group(1).strip() if winemaker_m else ""
        out.append({
            "slug": slug_m.group(1) if slug_m else path.stem,
            "name": name_m.group(1) if name_m else "",
            "winemaker": winemaker,
            "events": events,
        })
    return out


def cmd_validate() -> int:
    if not TALENTS_CSV.exists():
        print("Run --build-index first", file=sys.stderr)
        return 1
    talents = list(csv.DictReader(TALENTS_CSV.open(encoding="utf-8")))
    producers = load_wiki_argentina_producers()
    print(f"AR talents: {len(talents)} · Wiki Argentina producers: {len(producers)}")

    matched: list[tuple[dict, dict]] = []
    talent_unmatched: list[dict] = []
    for t in talents:
        t_tokens = name_tokens(t["name"])
        best, best_score = None, 0
        for p in producers:
            for field_val in (p["winemaker"], p["name"]):
                if not field_val:
                    continue
                p_tokens = name_tokens(field_val)
                if not p_tokens:
                    continue
                score = len(t_tokens & p_tokens)
                if score > best_score:
                    best, best_score = p, score
        if best and best_score >= 1:
            matched.append((t, best))
        else:
            talent_unmatched.append(t)

    matched_slugs = {p["slug"] for _, p in matched}
    wiki_event_orphans = [
        p for p in producers
        if p["events"] and p["slug"] not in matched_slugs
    ]

    VALIDATION_REPORT.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.now().isoformat(timespec="seconds")
    lines = [
        "---",
        "type: validation_report",
        "source: argentina_reloaded_scrape",
        f'generated: "{today}"',
        f"talents_total: {len(talents)}",
        f"matched: {len(matched)}",
        f"talent_unmatched: {len(talent_unmatched)}",
        f"wiki_event_orphans: {len(wiki_event_orphans)}",
        "---",
        "",
        "# Argentina Reloaded × Wiki cross-validation",
        "",
        f"## Matched ({len(matched)})",
        "",
        "| AR Talent | Wiki Producer | Winemaker (wiki) | Events (wiki) |",
        "|---|---|---|---|",
    ]
    for t, p in matched:
        evs = ", ".join(p["events"]) or "—"
        lines.append(f"| {t['name']} ({t['slug']}) | [[{p['slug']}|{p['name']}]] | {p['winemaker'] or '—'} | {evs} |")

    lines += [
        "",
        f"## AR talents NOT matched in wiki ({len(talent_unmatched)})",
        "",
        "_These winemakers appear on argentinareloaded.com but no wiki Argentina producer was found by token-overlap match. Could be (a) a wiki gap, (b) a name-mismatch needing an alias, or (c) the talent maps to a producer not currently in our JSX list._",
        "",
    ]
    for t in talent_unmatched:
        lines.append(f"- **{t['name']}** — {t['url']}")

    lines += [
        "",
        f"## Wiki producers with `events: []` but no AR talent match ({len(wiki_event_orphans)})",
        "",
        "_These wiki producers claim Argentina Reloaded participation but no scraped talent matched. Verify the JSX `reloaded` field is correct, or the talent's name on the AR site differs from our winemaker field._",
        "",
    ]
    for p in wiki_event_orphans:
        evs = ", ".join(p["events"])
        lines.append(f"- **{p['name']}** ({p['slug']}) — winemaker: {p['winemaker'] or '—'} — events: {evs}")

    VALIDATION_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: matched {len(matched)}, unmatched {len(talent_unmatched)}, orphans {len(wiki_event_orphans)}")
    print(f"Report: {VALIDATION_REPORT.relative_to(VAULT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    ap.add_argument("--build-index", action="store_true", help="Fetch homepage and list talents")
    ap.add_argument("--all", action="store_true", help="Fetch every talent detail page")
    ap.add_argument("--validate", action="store_true", help="Cross-check talents.csv against wiki/producers/")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true", help="Bypass HTML cache")
    args = ap.parse_args()

    if args.build_index:
        return cmd_build_index(args.force)
    if args.all:
        return cmd_all(args.force, args.limit)
    if args.validate:
        return cmd_validate()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
