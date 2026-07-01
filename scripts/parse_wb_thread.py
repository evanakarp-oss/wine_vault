"""
Parse a Wine Berserkers thread dump into a per-producer tally JSON.

Input is whatever scrape_wb_thread.py produced:
  - Discourse JSON (preferred): a JSON array of posts with `username`,
    `created_at`, and `cooked` (HTML) or `raw` (markdown) text fields.
  - Raw markdown dump: a flat .md file where each post is separated by a
    `---` line and starts with `## <Username> — YYYY-MM` style header. Less
    reliable; used as fallback when scraping isn't possible.

Output: raw/berserkers/threads/<slug>.json (shape: see raw/berserkers/README.md).

What it does:
  1. Walk each post.
  2. Detect "producer list" posts: ≥3 short lines that look like producer
     names (no full sentences, optional %/bottle-count suffix).
  3. Normalize each line through PRODUCER_ALIASES to a canonical name.
  4. Bucket post date into era_breakpoints (configurable in the input JSON
     metadata, defaults to 2013–2014 / 2021–2022 / 2023–2026).
  5. Compute totals + per-era counts + 2023+ momentum score per producer.

The momentum score answers "is interest accelerating recently?":
    momentum_2023 = (mentions_per_post in 2023+ era) / (mentions_per_post in
                    earliest active era for that producer)
Score = 1.0 means steady. >1 means surging. 0.0 means dropped off entirely.
For producers with zero mentions in earlier eras, score is reported as
`null` and they are flagged as "new entrants".

Usage:
    python scripts/parse_wb_thread.py raw/berserkers/threads/top10_in_cellar.discourse.json
    python scripts/parse_wb_thread.py raw/berserkers/threads/top10_in_cellar.raw.md \\
        --slug top10_in_cellar --title "Top 10 Producers in your cellar?" \\
        --thread-url https://www.wineberserkers.com/t/top-10-producers-in-your-cellar/74370

Outputs to threads/<slug>.json. Pass --merge-with to keep curated alias
overrides + notable_quotes from a prior version of the JSON.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


def _now_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()

VAULT = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT / "raw" / "berserkers" / "threads"

# ---------------------------------------------------------------- aliases ---
#
# Curated decision table mapping raw forum spellings → canonical name.
# The canonical name is also what appears in the JSON's `raw_name` field
# and what the compiler then matches to wiki/producers/<slug>.md.
#
# Add new aliases here when the parser reports unmatched producers.

PRODUCER_ALIASES: dict[str, str] = {
    # Form: lower("normalized stripped name") -> canonical display name.
    # Normalization (see normalize_for_alias) folds accents, lowercases,
    # collapses whitespace, strips common prefixes (domaine/chateau/weingut).
    "jj prum": "JJ Prum",
    "joh jos prum": "JJ Prum",
    "prum": "JJ Prum",
    "donnhoff": "Donnhoff",
    "pegau": "Pegau",
    "du pegau": "Pegau",
    "produttori": "Produttori",
    "produttori del barbaresco": "Produttori",
    "produttori di barbaresco": "Produttori",
    "rivers marie": "Rivers-Marie",
    "rivers-marie": "Rivers-Marie",
    "rm": "Rivers-Marie",
    "lopez de heredia": "Lopez de Heredia",
    "r lopez de heredia": "Lopez de Heredia",
    "ldh": "Lopez de Heredia",
    "hudelot noellat": "Hudelot-Noellat",
    "hudelot-noellat": "Hudelot-Noellat",
    "alain hudelot noellat": "Hudelot-Noellat",
    "willi schaefer": "Willi Schaefer",
    "schaefer": "Willi Schaefer",
    "bedrock wine co": "Bedrock",
    "bedrock": "Bedrock",
    "rhys": "Rhys",
    "ridge": "Ridge",
    "carlisle": "Carlisle",
    "huet": "Huet",
    "domaine huet": "Huet",
    "saxum": "Saxum",
    "dujac": "Dujac",
    "domaine dujac": "Dujac",
    "bruno giacosa": "Bruno Giacosa",
    "giacosa": "Bruno Giacosa",
    "hofgut falkenstein": "Hofgut Falkenstein",
    "falkenstein": "Hofgut Falkenstein",
    "goodfellow": "Goodfellow",
    "goodfellow family cellars": "Goodfellow",
    "patricia green": "Patricia Green",
    "patricia green cellars": "Patricia Green",
    "kelley fox": "Kelley Fox",
    "kelley fox wines": "Kelley Fox",
    "walter scott": "Walter Scott",
    "di costanzo": "Di Costanzo",
    "beta": "Beta",
    "extradimensional": "Extradimensional",
    "extradimensional wine co yeah": "Extradimensional",
    "dirty and rowdy": "Dirty and Rowdy",
    "dnr": "Dirty and Rowdy",
    "sqn": "SQN",
    "sine qua non": "SQN",
    "drc": "DRC",
    "domaine de la romanee conti": "DRC",
    "domaine de la romanee-conti": "DRC",
    "krug": "Krug",
    "dom perignon": "Dom Perignon",
    "moet et chandon": "Dom Perignon",
    "moet chandon": "Dom Perignon",
    "cedric bouchard": "Cedric Bouchard",
    "roses de jeanne": "Cedric Bouchard",
    "roses de jeanne cedric bouchard": "Cedric Bouchard",
    "g rinaldi": "G. Rinaldi",
    "giuseppe rinaldi": "G. Rinaldi",
    "g mascarello": "G. Mascarello",
    "giuseppe mascarello": "G. Mascarello",
    "giuseppe e figlio mascarello": "G. Mascarello",
    "b mascarello": "B. Mascarello",
    "bartolo mascarello": "B. Mascarello",
    "rousseau": "Rousseau",
    "armand rousseau": "Rousseau",
    "domaine armand rousseau": "Rousseau",
    "fourrier": "Fourrier",
    "domaine fourrier": "Fourrier",
    "mugneret gibourg": "Mugneret-Gibourg",
    "mugneret-gibourg": "Mugneret-Gibourg",
    "georges mugneret": "Mugneret-Gibourg",
    "barthod": "Barthod",
    "ghislaine barthod": "Barthod",
    "lafarge": "Lafarge",
    "michel lafarge": "Lafarge",
    "d angerville": "d'Angerville",
    "marquis d angerville": "d'Angerville",
    "marquis d'angerville": "d'Angerville",
    "chevillon": "Chevillon",
    "robert chevillon": "Chevillon",
    "mugnier": "Mugnier",
    "jacques frederic mugnier": "Mugnier",
    "roumier": "Roumier",
    "g roumier": "Roumier",
    "bouchard": "Bouchard",
    "bouchard pere et fils": "Bouchard",
    "raveneau": "Raveneau",
    "francois raveneau": "Raveneau",
    "dauvissat": "Dauvissat",
    "vincent dauvissat": "Dauvissat",
    "drouhin": "Drouhin",
    "joseph drouhin": "Drouhin",
    "jadot": "Jadot",
    "louis jadot": "Jadot",
    "leflaive": "Leflaive",
    "domaine leflaive": "Leflaive",
    "lapierre": "Lapierre",
    "marcel lapierre": "Lapierre",
    "foillard": "Foillard",
    "jean foillard": "Foillard",
    "coudert": "Coudert",
    "clos rougeard": "Clos Rougeard",
    "rougeard": "Clos Rougeard",
    "baudry": "Baudry",
    "bernard baudry": "Baudry",
    "domaine bernard baudry": "Baudry",
    "chave": "Chave",
    "jean louis chave": "Chave",
    "j l chave": "Chave",
    "chidaine": "Chidaine",
    "francois chidaine": "Chidaine",
    "pepiere": "Pepiere",
    "domaine de la pepiere": "Pepiere",
    "marc ollivier": "Pepiere",
    "gonon": "Gonon",
    "pierre gonon": "Gonon",
    "allemand": "Allemand",
    "thierry allemand": "Allemand",
    "clape": "Clape",
    "auguste clape": "Clape",
    "levet": "Levet",
    "bernard levet": "Levet",
    "rayas": "Rayas",
    "ch des tours": "Rayas",
    "chateau des tours": "Rayas",
    "beaucastel": "Beaucastel",
    "chateau de beaucastel": "Beaucastel",
    "vajra": "Vajra",
    "g d vajra": "Vajra",
    "gd vajra": "Vajra",
    "burlotto": "Burlotto",
    "comm g b burlotto": "Burlotto",
    "g b burlotto": "Burlotto",
    "cappellano": "Cappellano",
    "augusto cappellano": "Cappellano",
    "giacomo conterno": "Giacomo Conterno",
    "monfortino": "Giacomo Conterno",
    "brovia": "Brovia",
    "fratelli brovia": "Brovia",
    "montrose": "Montrose",
    "chateau montrose": "Montrose",
    "pichon lalande": "Pichon Lalande",
    "pichon longueville comtesse de lalande": "Pichon Lalande",
    "pichon comtesse": "Pichon Lalande",
    "pichon baron": "Pichon Baron",
    "pichon longueville baron": "Pichon Baron",
    "pontet canet": "Pontet Canet",
    "pontet-canet": "Pontet Canet",
    "leoville barton": "Leoville-Barton",
    "leoville-barton": "Leoville-Barton",
    "leoville las cases": "Leoville Las Cases",
    "leoville poyferre": "Leoville Poyferre",
    "cos d estournel": "Cos d'Estournel",
    "cos destournel": "Cos d'Estournel",
    "kosta browne": "Kosta Browne",
    "williams selyem": "Williams Selyem",
    "selyem": "Williams Selyem",
    "kistler": "Kistler",
    "kutch": "Kutch",
    "myriad": "Myriad",
    "myriad cellars": "Myriad",
    "andremily": "Andremily",
    "macdonald": "MacDonald",
    "alban": "Alban",
    "halcon": "Halcon",
    "halcon vineyards": "Halcon",
    "halcon estate": "Halcon",
    "ultramarine": "Ultramarine",
    "kinsman eades": "Kinsman Eades",
    "kobayashi": "Kobayashi",
    "fingers crossed": "Fingers Crossed",
    "ceritas": "Ceritas",
    "sandlands": "Sandlands",
    "thomas": "Thomas",
    "thomas winery": "Thomas",
    "scherrer": "Scherrer",
    "scherrer winery": "Scherrer",
    "rochioli": "Rochioli",
    "littorai": "Littorai",
    "peay": "Peay",
    "peay vineyards": "Peay",
    "mount eden": "Mount Eden",
    "domaine eden": "Mount Eden",
    "cameron": "Cameron",
    "evesham wood": "Evesham Wood",
    "arcadian": "Arcadian",
    "maison ilan": "Maison Ilan",
    "lauer": "Lauer",
    "peter lauer": "Lauer",
    "weingut peter lauer": "Lauer",
    "keller": "Keller",
    "weingut keller": "Keller",
    "klaus peter keller": "Keller",
    "schafer frohlich": "Schafer-Frohlich",
    "schafer-frohlich": "Schafer-Frohlich",
    "emrich schonleber": "Emrich-Schonleber",
    "emrich-schonleber": "Emrich-Schonleber",
    "richter": "Richter",
    "max ferd richter": "Richter",
    "weingut max ferd richter": "Richter",
    "selbach oster": "Selbach-Oster",
    "selbach-oster": "Selbach-Oster",
    "von schubert": "Von Schubert",
    "maximin grunhaus": "Von Schubert",
    "von schubert maximin grunhaus": "Von Schubert",
    "musar": "Musar",
    "chateau musar": "Musar",
    "cayuse": "Cayuse",
    "quilceda creek": "Quilceda Creek",
    "felsina": "Felsina",
    "fattoria di felsina": "Felsina",
    "fattoria di felsina berardenga": "Felsina",
    "taittinger": "Taittinger",
    "comtes": "Taittinger",  # only in Champagne context — risky
    "realm": "Realm",
    "realm cellars": "Realm",
    "saxum james berry": "Saxum",
    "patricia green cellars 5 2 percent": "Patricia Green",
    # — additive: when the parser reports an unmatched name, add the
    #   normalized form here pointing at the canonical name and re-run.
}

# Lines to *exclude* even though they look like producer names.
EXCLUDE_TOKENS = {
    "edit", "tied", "tie", "and", "or", "etc", "the rest", "next 10",
    "honorable mention", "in no particular order", "spots", "btls",
    "bottles", "by region", "by producer", "by appellation",
}


def fold_ascii(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


PREFIX_RE = re.compile(
    r"^(domaine|chateau|château|weingut|bodegas|maison|fattoria|cantina|"
    r"tenuta|comm|comm\.|signor|sig\.|m|mr|mme|le|la)\s+",
    re.IGNORECASE,
)


def normalize_for_alias(s: str) -> str:
    """Used as the lookup key into PRODUCER_ALIASES."""
    s = fold_ascii(s).lower().strip()
    # strip percentages, bottle counts, parens, quotation marks
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"\d+\.\d+%?", "", s)
    s = re.sub(r"\d+%", "", s)
    s = re.sub(r"\s*[-–—]\s*\d+%?", "", s)
    s = re.sub(r"\s*\d+\s*(bottles?|btls?|bot)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^\w\s'-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # strip common prefixes
    while True:
        new = PREFIX_RE.sub("", s)
        if new == s:
            break
        s = new
    return s


# ----------------------------------------------------------- post extract ---

POST_LINE_MAX_WORDS = 8  # producer-name lines are short
LIST_MIN_LINES = 3


@dataclass
class Post:
    username: str
    created_at: str  # ISO date or YYYY-MM
    text: str

    @property
    def year(self) -> int | None:
        m = re.search(r"\b(19|20)\d{2}\b", self.created_at)
        return int(m.group(0)) if m else None


def parse_discourse_json(path: Path) -> list[Post]:
    data = json.loads(path.read_text(encoding="utf-8"))
    posts = []
    items = data if isinstance(data, list) else data.get("posts", [])
    for it in items:
        username = it.get("username") or it.get("name") or ""
        created = it.get("created_at") or it.get("date") or ""
        # Prefer raw markdown if present, else strip HTML tags from cooked
        text = it.get("raw") or strip_html(it.get("cooked", ""))
        if username and text:
            posts.append(Post(username=username, created_at=str(created), text=text))
    return posts


HTML_TAG_RE = re.compile(r"<[^>]+>")
# Tags that imply a line break — Discourse `cooked` HTML packs list items and
# paragraphs onto one line with no newline, so converting these to `\n` before
# stripping is what turns an <li>…</li><li>…</li> run into one-name-per-line.
BLOCK_TAG_RE = re.compile(r"(?i)</(?:li|p|div|tr|h[1-6]|blockquote)>|<br\s*/?>")


def strip_html(html: str) -> str:
    html = BLOCK_TAG_RE.sub("\n", html)
    return re.sub(r"\n{3,}", "\n\n", HTML_TAG_RE.sub("", html))


POST_HEADER_RE = re.compile(
    r"^##\s+(?P<user>[A-Za-z0-9_.-]+)\s*[—\-–]\s*(?P<date>[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2})\s*$",
    re.MULTILINE,
)


def parse_raw_markdown(path: Path) -> list[Post]:
    """Fallback: posts separated by `## <user> — <date>` headers."""
    text = path.read_text(encoding="utf-8")
    posts = []
    matches = list(POST_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        posts.append(Post(
            username=m.group("user"),
            created_at=m.group("date"),
            text=body,
        ))
    return posts


# ---------------------------------------------------------- list detection -

PCT_LINE_RE = re.compile(r"\d+(?:\.\d+)?\s*%")
SENTENCE_END_RE = re.compile(r"[.!?]\s+[A-Z]")
LEAD_ENUM_RE = re.compile(r"^\s*[\d\)\.\-\*•#]+[\.\)]?\s*")
TRAIL_COUNT_RE = re.compile(
    r"\s*[-–—:]?\s*\d+(?:\.\d+)?\s*(?:%|bottles?|btls?|bot|x)?\s*$",
    re.IGNORECASE,
)


def _clean_line(line: str) -> str:
    """Strip the leading enumerator/bullet and any trailing %/bottle-count so
    the line is just the candidate producer name. Applied *before* the prose
    check so `1. Bedrock` is not mistaken for a sentence."""
    line = LEAD_ENUM_RE.sub("", line)
    line = TRAIL_COUNT_RE.sub("", line)
    line = line.strip(" -*•\t")
    if line.endswith(":"):  # section header / label ("Champagne:", "My ten:")
        return ""
    return line


def looks_like_list_post(text: str) -> bool:
    """A post is a producer-list post if it has ≥3 short lines that don't
    look like prose."""
    candidates = 0
    for line in text.splitlines():
        line = _clean_line(line)
        if not line:
            continue
        if SENTENCE_END_RE.search(line):
            continue
        words = line.split()
        if len(words) > POST_LINE_MAX_WORDS:
            continue
        if any(t in line.lower() for t in EXCLUDE_TOKENS):
            continue
        # Must contain at least one alpha character
        if not re.search(r"[A-Za-z]{3}", line):
            continue
        candidates += 1
    return candidates >= LIST_MIN_LINES


def extract_producers(text: str) -> list[str]:
    """Pull candidate producer names from a list post's lines."""
    out = []
    for line in text.splitlines():
        line = _clean_line(line)
        if not line:
            continue
        if SENTENCE_END_RE.search(line):
            continue
        words = line.split()
        if len(words) == 0 or len(words) > POST_LINE_MAX_WORDS:
            continue
        if any(t in line.lower() for t in EXCLUDE_TOKENS):
            continue
        if not re.search(r"[A-Za-z]{3}", line):
            continue
        out.append(line)
    return out


# ----------------------------------------------------------- era bucketing -

DEFAULT_ERA_BUCKETS = [
    ("2013-2014", 2013, 2014),
    ("2021-2022", 2021, 2022),
    ("2023-2026", 2023, 2099),
]


def era_for_year(year: int | None, buckets) -> str | None:
    if year is None:
        return None
    for label, lo, hi in buckets:
        if lo <= year <= hi:
            return label
    return None


# ---------------------------------------------------------- tally building -

@dataclass
class ProducerTally:
    canonical_name: str
    mentions: int = 0
    by_era: dict[str, int] = field(default_factory=dict)
    first_seen: str = ""
    last_seen: str = ""
    raw_forms_seen: set = field(default_factory=set)


def normalize_post_dates(post: Post) -> tuple[str, int | None]:
    """Return (display_date, year)."""
    s = post.created_at
    # Discourse: 2024-03-19T12:34:56Z
    m = re.match(r"(\d{4})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}", int(m.group(1))
    # "Aug 2013" style
    m = re.match(r"([A-Za-z]{3})\s+(\d{4})", s)
    if m:
        try:
            dt = datetime.strptime(s, "%b %Y")
            return dt.strftime("%Y-%m"), dt.year
        except ValueError:
            pass
    m = re.search(r"(\d{4})", s)
    if m:
        return s, int(m.group(1))
    return s, None


def canonical_for(raw_line: str) -> str | None:
    key = normalize_for_alias(raw_line)
    if not key:
        return None
    if key in PRODUCER_ALIASES:
        return PRODUCER_ALIASES[key]
    # No alias known: use the title-cased normalized form as canonical.
    # The compiler will still try to slug-match it; if no match, it's
    # reported as unmatched and the user adds an alias entry.
    return raw_line.strip().rstrip(".,;:")


def build_tally(posts: list[Post], buckets) -> dict[str, ProducerTally]:
    tally: dict[str, ProducerTally] = {}
    for post in posts:
        if not looks_like_list_post(post.text):
            continue
        date_str, year = normalize_post_dates(post)
        era = era_for_year(year, buckets)
        # one mention per producer per post (dedupe within a post)
        in_post = set()
        for raw in extract_producers(post.text):
            canon = canonical_for(raw)
            if not canon or canon.lower() in in_post:
                continue
            in_post.add(canon.lower())
            t = tally.setdefault(canon, ProducerTally(canonical_name=canon))
            t.mentions += 1
            t.raw_forms_seen.add(raw.strip())
            if era:
                t.by_era[era] = t.by_era.get(era, 0) + 1
            if not t.first_seen or date_str < t.first_seen:
                t.first_seen = date_str
            if not t.last_seen or date_str > t.last_seen:
                t.last_seen = date_str
    return tally


def momentum_2023(t: ProducerTally) -> float | None:
    """(mentions/post in 2023+) / (mentions/post in earliest active era).

    We don't have post counts per era here; using mention counts as a proxy
    is fine for relative comparison since post counts are roughly constant
    across the WB top10 thread's bursts. Returns None for new entrants
    (zero in earlier eras → no baseline)."""
    recent = t.by_era.get("2023-2026", 0)
    early = t.by_era.get("2013-2014", 0)
    mid = t.by_era.get("2021-2022", 0)
    baseline = early or mid
    if baseline == 0:
        return None if recent == 0 else float("inf")
    return round(recent / baseline, 2)


# ------------------------------------------------------------ JSON writing -

def write_thread_json(
    out_path: Path,
    thread_meta: dict,
    tally: dict[str, ProducerTally],
    buckets,
    merge_with: dict | None = None,
) -> None:
    """Emit the canonical thread JSON. Preserves notable_quotes if present
    in merge_with."""
    ranked = sorted(tally.values(), key=lambda t: -t.mentions)

    prior_quotes: dict[str, list] = {}
    if merge_with:
        for p in merge_with.get("producers", []):
            if p.get("notable_quotes"):
                prior_quotes[p["raw_name"]] = p["notable_quotes"]

    producers = []
    for rank, t in enumerate(ranked, start=1):
        e = t.by_era
        producers.append({
            "rank": rank,
            "raw_name": t.canonical_name,
            "mentions": t.mentions,
            "mentions_2013_2014": e.get("2013-2014", 0) if e else None,
            "mentions_2021_2022": e.get("2021-2022", 0) if e else None,
            "mentions_2023_2026": e.get("2023-2026", 0) if e else None,
            "momentum_score_2023": momentum_2023(t),
            "first_seen": t.first_seen,
            "last_seen": t.last_seen,
            "notable_quotes": prior_quotes.get(t.canonical_name, []),
        })

    thread_meta = dict(thread_meta)
    thread_meta["unique_producers"] = len(producers)
    thread_meta["total_mentions"] = sum(t.mentions for t in ranked)
    thread_meta["scraped_at"] = _now_iso_date()
    thread_meta.setdefault("era_breakpoints", [b[0] for b in buckets])

    payload = {"thread": thread_meta, "producers": producers}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")


# -------------------------------------------------------------------- main -

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="Path to scraped thread (.discourse.json or .raw.md)")
    ap.add_argument("--slug", help="Thread slug (filename of output JSON). "
                                   "Default: derived from source filename.")
    ap.add_argument("--title", default="", help="Thread title for metadata")
    ap.add_argument("--thread-url", default="", help="Thread URL for metadata")
    ap.add_argument("--thread-id", type=int, default=0)
    ap.add_argument("--merge-with", help="Existing <slug>.json to preserve curated fields")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 2

    if src.suffix == ".json":
        posts = parse_discourse_json(src)
    else:
        posts = parse_raw_markdown(src)
    print(f"Parsed {len(posts)} posts from {src.name}")

    list_posts = [p for p in posts if looks_like_list_post(p.text)]
    print(f"  {len(list_posts)} look like producer-list posts")

    buckets = DEFAULT_ERA_BUCKETS
    tally = build_tally(posts, buckets)
    print(f"  {len(tally)} unique producers, "
          f"{sum(t.mentions for t in tally.values())} total mentions")

    slug = args.slug or src.stem.replace(".discourse", "").replace(".raw", "")
    out = RAW_DIR / f"{slug}.json"

    merge_with = None
    if args.merge_with:
        merge_with = json.loads(Path(args.merge_with).read_text(encoding="utf-8"))

    thread_meta = {
        "slug": slug,
        "title": args.title or (merge_with.get("thread", {}).get("title", "") if merge_with else ""),
        "url": args.thread_url or (merge_with.get("thread", {}).get("url", "") if merge_with else ""),
        "thread_id": args.thread_id or (merge_with.get("thread", {}).get("thread_id", 0) if merge_with else 0),
        "forum": "wineberserkers",
        "post_count": len(posts),
        "scrape_method": "discourse_json_v1" if src.suffix == ".json" else "manual_paste_v1",
    }
    if list_posts:
        first = min(p.created_at for p in list_posts)
        last = max(p.created_at for p in list_posts)
        thread_meta["first_post_date"] = first[:7]
        thread_meta["last_post_date"] = last[:7]

    write_thread_json(out, thread_meta, tally, buckets, merge_with=merge_with)
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
