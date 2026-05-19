"""
Ingest FASS Selections email offers (raw/fass/markdown/*.md) into wiki
producer pages.

Each FASS email is essentially a single-wine pitch: title has score / vintage /
cuvee hints, body has a story + tasting notes + an offer price. We extract
what we can heuristically (vintage, price, score, snippet) and match the
producer by scanning the title + body for known wiki producer names + aliases.

This is distinct from `ingest_fass.py`, which folds the FASS *portfolio* JSX
into `## FASS`. Emails land in their own `## FASS Offers` section so the two
sources never clobber each other.

Idempotent: each run rebuilds `## FASS Offers` from whatever .md files are
currently in raw/fass/markdown/. To incorporate a new email, save it as a
scraped markdown file under raw/fass/markdown/<slug>.md with frontmatter
matching the existing files (type / title / url / fetched_at), then re-run.

Unmatched emails are logged to build/fass_emails_ingest_report.md — they are
NOT auto-created as wiki pages (per the same convention as `ingest_fass.py`).
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
EMAILS_DIR = VAULT / "raw" / "fass" / "markdown"
WIKI_DIR = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "fass_emails_ingest_report.md"

# Manual disambiguations. Normalized substring → wiki slug. The substring
# match runs BEFORE the heuristic name scoring, so explicit aliases always
# win. Extend as the unmatched report surfaces clear cases.
EMAIL_ALIASES: dict[str, str] = {
    "stefan steinmetz": "steinmetz",
    "gunther steinmetz": "steinmetz",
    "gunter steinmetz": "steinmetz",
}

# Producer-side normalized search terms that are too generic to ever count as
# a match (would create false positives if a producer's `name` collapses to
# one of these).
GENERIC_TERMS = {
    "domaine", "weingut", "chateau", "estate", "winery", "the", "and",
    "fass", "fass selections", "blog",
}

# Min normalized-term length we'll accept as a search term — single tokens
# shorter than this are too prone to false positives.
MIN_TERM_LEN = 5

# Confidence threshold for producer match. Score weighting:
#   title hit: 3 × len(term),  body hit: 1 × len(term).
# So matching a 7-char name once in the title scores 21; once in the body
# scores 7. Floor of 7 means we require at least one body hit on a 7+ char
# term, OR a title hit on a 5+ char term, OR multiple shorter hits.
MIN_MATCH_SCORE = 7


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
SCORE_RE = re.compile(r"\b(\d{2,3})\s*Points?\b", re.IGNORECASE)
PRICE_RE = re.compile(r"\$(\d{1,4}(?:\.\d{2})?)")
VINTAGE_RE = re.compile(r"\b(19[7-9]\d|20[0-2]\d)\b")


def normalize(s: str) -> str:
    """Lowercase, strip accents, collapse non-alphanum runs to single space."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------------------
# Email parsing
# ---------------------------------------------------------------------------


# Footer marker that ends the pitch and begins the legacy-offers listing.
# Past wines listed after this point name-drop other producers and would
# create false-positive matches if we scored them.
PITCH_END_MARKERS = (
    "previous offers still open",
    "a word about fass selections",
)

# Char window at the start of pitch_body used for producer matching. FASS
# announces the offered wine + producer in the opening paragraphs. Later
# prose drifts into editorial comparisons that name-drop other producers.
INTRO_WINDOW_CHARS = 1500


@dataclass
class Email:
    path: Path
    slug: str
    title: str
    url: str
    fetched_at: str
    body: str

    @property
    def display_title(self) -> str:
        """Frontmatter title is 'Blog' on partial/preview scrapes — fall back
        to the first ## heading inside the body."""
        if self.title and self.title.lower() != "blog":
            return self.title
        for line in self.body.splitlines():
            if line.startswith("## "):
                return line[3:].strip()
        return self.slug

    @property
    def pitch_body(self) -> str:
        """Body trimmed to the pitch portion only — everything before the
        'Previous Offers Still Open' footer (or similar boilerplate)."""
        low = self.body.lower()
        cut = len(self.body)
        for marker in PITCH_END_MARKERS:
            i = low.find(marker)
            if i != -1 and i < cut:
                cut = i
        return self.body[:cut]

    @property
    def intro_body(self) -> str:
        """The opening of the pitch, where FASS announces the wine + producer.
        Past this window the body becomes editorial storytelling that often
        name-drops other producers as benchmarks."""
        return self.pitch_body[:INTRO_WINDOW_CHARS]

    @property
    def vintage(self) -> str:
        m = VINTAGE_RE.search(self.display_title)
        if m:
            return m.group(1)
        m = VINTAGE_RE.search(self.body[:600])
        return m.group(1) if m else ""

    @property
    def price(self) -> str:
        """Offer price. Prices in body are typically the order line at the
        bottom; a price in the title is the headline ('$54.99 for ...')."""
        m = PRICE_RE.search(self.display_title)
        if m:
            return f"${m.group(1)}"
        prices = PRICE_RE.findall(self.body)
        if not prices:
            return ""
        # Prefer the LAST price with cents — that's almost always the
        # per-bottle order line. Fall back to last price seen.
        for p in reversed(prices):
            if "." in p:
                return f"${p}"
        return f"${prices[-1]}"

    @property
    def score(self) -> str:
        m = SCORE_RE.search(self.display_title)
        if not m:
            m = SCORE_RE.search(self.body[:400])
        return f"{m.group(1)} pts" if m else ""

    @property
    def snippet(self) -> str:
        """First substantive paragraph after the title — usually the wine
        announcement line. Caps at ~220 chars."""
        title_norm = re.sub(r"\s+", " ", self.display_title).strip().lower()
        for para in self.body.split("\n\n"):
            line = para.strip()
            if not line or line.startswith("!["):
                continue
            line = re.sub(r"^#+\s*", "", line).strip()
            line = re.sub(r"\s+", " ", line)
            if not line or line.lower() == title_norm:
                continue
            if len(line) < 60:
                continue
            if len(line) > 220:
                line = line[:217].rsplit(" ", 1)[0] + "…"
            return line
        return ""


def parse_email(path: Path) -> Email | None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text, body = m.group(1), m.group(2).strip()
    fm: dict[str, str] = {}
    for line in fm_text.splitlines():
        if not line or line.startswith(" "):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return Email(
        path=path,
        slug=fm.get("slug") or path.stem,
        title=fm.get("title", ""),
        url=fm.get("url", ""),
        fetched_at=fm.get("fetched_at", ""),
        body=body,
    )


# ---------------------------------------------------------------------------
# Producer index
# ---------------------------------------------------------------------------


@dataclass
class Producer:
    slug: str
    name: str
    search_terms: list[str] = field(default_factory=list)


def _parse_aliases(fm_text: str) -> list[str]:
    m = re.search(r"^aliases:\s*(.+)$", fm_text, re.MULTILINE)
    if not m:
        return []
    rest = m.group(1).strip()
    if not rest or rest == "[]":
        return []
    if rest.startswith("[") and rest.endswith("]"):
        inner = rest[1:-1]
        return [s.strip().strip('"').strip("'")
                for s in inner.split(",") if s.strip()]
    return []


def load_producers() -> list[Producer]:
    # Invert EMAIL_ALIASES so a slug can pick up any extra terms mapped to it.
    extra_terms_by_slug: dict[str, list[str]] = defaultdict(list)
    for alias, slug in EMAIL_ALIASES.items():
        extra_terms_by_slug[slug].append(alias)

    producers: list[Producer] = []
    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    for path in sorted(WIKI_DIR.glob("*.md")):
        slug = path.stem
        text = path.read_text(encoding="utf-8")
        m = fm_re.match(text)
        name = ""
        aliases: list[str] = []
        if m:
            fm_text = m.group(1)
            name_match = re.search(r'^name:\s*"?([^"\n]+?)"?\s*$',
                                   fm_text, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
            aliases = _parse_aliases(fm_text)

        seen: set[str] = set()
        terms: list[str] = []
        candidates = [name] + aliases + extra_terms_by_slug.get(slug, [])
        if not name:
            candidates.append(slug.replace("_", " "))
        for cand in candidates:
            n = normalize(cand)
            if not n or n in GENERIC_TERMS or n in seen:
                continue
            if len(n) < MIN_TERM_LEN:
                continue
            seen.add(n)
            terms.append(n)
        if not terms:
            continue
        # Longest first — match_producer relies on this ordering.
        terms.sort(key=len, reverse=True)
        producers.append(Producer(slug=slug, name=name or slug,
                                  search_terms=terms))
    return producers


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def _count_whole_word(haystack_padded: str, needle: str) -> int:
    """Count occurrences of `needle` as a whole token run in `haystack_padded`,
    which must already be wrapped with a leading + trailing space."""
    return haystack_padded.count(" " + needle + " ")


def match_producer(email: Email, producers: list[Producer]) -> tuple[Producer | None, float]:
    title_norm = " " + normalize(email.display_title) + " "
    intro_norm = " " + normalize(email.display_title + " " + email.intro_body) + " "

    # Heuristic scoring on title + opening of the pitch body. We don't scan
    # the full body — FASS emails name-drop benchmark producers ("on par with
    # Steinmetz", "if Brisset made nebbiolo") in editorial passages well after
    # the wine being offered has been introduced. Title hits weigh 3x. Short
    # single-word terms (e.g. "paris") collide with cities/regions, so they
    # only count when they hit in the title.
    best: Producer | None = None
    best_score = 0.0
    for p in producers:
        for term in p.search_terms:
            title_hits = _count_whole_word(title_norm, term)
            intro_hits = _count_whole_word(intro_norm, term) - title_hits
            if not (title_hits or intro_hits):
                continue
            if " " not in term and len(term) <= 6 and title_hits == 0:
                break  # too risky as a body-only match
            score = (title_hits * 3 + intro_hits) * len(term)
            if score > best_score:
                best_score = score
                best = p
            break  # only score the longest hitting term per producer
    if best_score < MIN_MATCH_SCORE:
        return None, best_score
    return best, best_score


# ---------------------------------------------------------------------------
# Section rendering + page mutation
# ---------------------------------------------------------------------------


SECTION_RE = re.compile(
    r"(?ms)^## FASS Offers\n.*?(?=^## [^#]|\Z)"
)


def render_section(emails: list[Email]) -> str:
    sorted_emails = sorted(
        emails,
        key=lambda e: (e.fetched_at or "", e.slug),
        reverse=True,
    )
    out: list[str] = ["## FASS Offers", ""]
    plural = "s" if len(sorted_emails) != 1 else ""
    out.append(f"{len(sorted_emails)} email offer{plural} from FASS "
               f"Selections (raw/fass/markdown/).")
    out.append("")
    for e in sorted_emails:
        title = e.display_title.replace("\n", " ").strip()
        out.append(f"### [{title}]({e.url})")
        meta: list[str] = []
        if e.vintage:
            meta.append(e.vintage)
        if e.price:
            meta.append(e.price)
        if e.score:
            meta.append(e.score)
        if e.fetched_at:
            meta.append(f"fetched {e.fetched_at[:10]}")
        if meta:
            out.append(f"*{' · '.join(meta)}*")
        if e.snippet:
            out.append("")
            out.append(f"> {e.snippet}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _read_lf(path: Path) -> tuple[str, str]:
    """Read text normalized to LF. Returns (text, newline_style) where
    newline_style is the original ending ('\\r\\n' or '\\n') to restore on
    write. Wiki pages are CRLF; preserving that avoids whole-file diffs."""
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw[:4096] else "\n"
    return raw.replace("\r\n", "\n"), newline


def _write_lf(path: Path, text: str, newline: str) -> None:
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def upsert_section(path: Path, section: str) -> bool:
    """Insert or replace `## FASS Offers` on the producer page. Returns True
    if the file content changed.

    Placement preference, in order:
      1. Replace existing `## FASS Offers` section.
      2. Insert right after the `## FASS` portfolio section.
      3. Insert before `## Cross-references`.
      4. Append at end of file.
    """
    text, newline = _read_lf(path)

    if SECTION_RE.search(text):
        new = SECTION_RE.sub(section + "\n", text, count=1)
    else:
        # After ## FASS (portfolio block)
        m = re.search(r"(?ms)^(## FASS\n.*?)(?=^## [^#]|\Z)", text)
        if m:
            insert_at = m.end()
            new = text[:insert_at] + "\n" + section + "\n" + text[insert_at:]
        elif re.search(r"^## Cross-references\n", text, re.MULTILINE):
            new = re.sub(
                r"^(## Cross-references\n)",
                section + "\n\\1",
                text,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            new = text.rstrip() + "\n\n" + section

    # Tidy stacked blank lines.
    new = re.sub(r"\n{3,}", "\n\n", new)
    if not new.endswith("\n"):
        new += "\n"

    if new != text:
        _write_lf(path, new, newline)
        return True
    return False


def clear_section(path: Path) -> bool:
    """Remove a stale `## FASS Offers` section. Returns True if changed."""
    text, newline = _read_lf(path)
    if not SECTION_RE.search(text):
        return False
    new = SECTION_RE.sub("", text, count=1)
    new = re.sub(r"\n{3,}", "\n\n", new).rstrip() + "\n"
    if new != text:
        _write_lf(path, new, newline)
        return True
    return False


def would_change(path: Path, section: str | None) -> bool:
    """Dry-run preview: would upsert_section (section=str) or clear_section
    (section=None) change this file?"""
    text, _ = _read_lf(path)
    existing_m = SECTION_RE.search(text)
    existing = existing_m.group(0).rstrip() if existing_m else None
    if section is None:
        return existing is not None
    return (existing or "").rstrip() != section.rstrip()


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_report(
    emails: list[Email],
    by_producer: dict[str, list[Email]],
    unmatched: list[tuple[Email, float]],
) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    matched_count = sum(len(v) for v in by_producer.values())
    lines = [
        "---",
        "type: ingest_report",
        "source: fass_emails",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_emails: {len(emails)}",
        f"matched: {matched_count}",
        f"unmatched: {len(unmatched)}",
        f"producers_touched: {len(by_producer)}",
        "---",
        "",
        "# FASS emails ingest report",
        "",
        f"Parsed `{EMAILS_DIR.relative_to(VAULT)}` — {len(emails)} email files.",
        f"Matched **{matched_count}** emails to **{len(by_producer)}** wiki producers.",
        f"**{len(unmatched)}** emails could not be confidently matched (score < "
        f"{MIN_MATCH_SCORE}).",
        "",
        "Unmatched emails are NOT auto-created as wiki pages (FASS pitches",
        "many producers we do not curate). To resolve:",
        "",
        "- If the producer is already in the wiki under a different spelling,",
        "  add a mapping to `EMAIL_ALIASES` in `scripts/ingest_fass_emails.py`",
        "  and re-run.",
        "- If the producer is worth adding to the wiki, create the page",
        "  manually following the schema in `wiki/_SCHEMA.md`, then re-run.",
        "",
        f"## Touched producers ({len(by_producer)})",
        "",
    ]
    for slug, es in sorted(by_producer.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        plural = "s" if len(es) != 1 else ""
        lines.append(f"- `{slug}` — {len(es)} email{plural}")
    lines += ["", f"## Unmatched emails ({len(unmatched)})", ""]
    if unmatched:
        lines.append("| Slug | Best score | Title |")
        lines.append("|---|---:|---|")
        for e, score in sorted(unmatched, key=lambda kv: -kv[1])[:120]:
            title = e.display_title.replace("|", "\\|")[:120]
            lines.append(f"| `{e.slug}` | {score:.1f} | {title} |")
        if len(unmatched) > 120:
            lines += ["", f"_… and {len(unmatched) - 120} more_"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="Don't write — exit 1 if any producer page would change.")
    args = ap.parse_args(argv)

    if not EMAILS_DIR.exists():
        print(f"emails dir not found: {EMAILS_DIR}", file=sys.stderr)
        return 1

    email_paths = sorted(EMAILS_DIR.glob("*.md"))
    emails: list[Email] = []
    for p in email_paths:
        e = parse_email(p)
        if e:
            emails.append(e)
    if not emails:
        print(f"no emails found in {EMAILS_DIR}")
        return 0
    print(f"parsed {len(emails)} FASS emails from "
          f"{EMAILS_DIR.relative_to(VAULT)}/")

    producers = load_producers()
    print(f"loaded {len(producers)} wiki producers")

    by_producer: dict[str, list[Email]] = defaultdict(list)
    unmatched: list[tuple[Email, float]] = []
    for e in emails:
        p, score = match_producer(e, producers)
        if p:
            by_producer[p.slug].append(e)
        else:
            unmatched.append((e, score))
    print(f"matched: {sum(len(v) for v in by_producer.values())} emails → "
          f"{len(by_producer)} producers")
    print(f"unmatched: {len(unmatched)}")

    changed: list[str] = []
    matched_slugs = set(by_producer.keys())

    # Upsert sections on matched producers
    for slug in sorted(matched_slugs):
        path = WIKI_DIR / f"{slug}.md"
        if not path.exists():
            continue
        section = render_section(by_producer[slug])
        if args.check:
            if would_change(path, section):
                changed.append(slug)
        else:
            if upsert_section(path, section):
                changed.append(slug)

    # Clear stale sections on producers no longer matched
    for path in sorted(WIKI_DIR.glob("*.md")):
        slug = path.stem
        if slug in matched_slugs:
            continue
        if "## FASS Offers" not in path.read_bytes().decode("utf-8"):
            continue
        if args.check:
            if would_change(path, None):
                changed.append(f"{slug} (clear stale)")
        else:
            if clear_section(path):
                changed.append(f"{slug} (cleared)")

    if not args.check:
        write_report(emails, by_producer, unmatched)
        print(f"report: {REPORT.relative_to(VAULT)}")

    if args.check:
        if changed:
            print(f"--check: {len(changed)} pages would change:")
            for c in changed[:30]:
                print(f"  - {c}")
            if len(changed) > 30:
                print(f"  … and {len(changed) - 30} more")
            return 1
        print("--check: clean")
        return 0

    print(f"updated {len(changed)} producer pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
