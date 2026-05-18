"""
Scan `raw/<source>/markdown/*.md` articles produced by `scrape_blogs.py` and fold
matching articles into each `wiki/producers/*.md` file's `## <Source> Write-ups`
section. Supports two sources: `fass` and `dtew`.

This is the FASS/DTEW analog of `ingest_csw.py`. The matching algorithm is
copied verbatim from there (proven against 1,623 CSW × 294 producers): build a
set of name forms per producer (canonical + aliases + prefix-stripped +
suffix-stripped), ASCII-normalize, scan article title + body with whole-word
matching that tolerates space/hyphen variants. Title hits = "dedicated" (★).

Source config
-------------
  fass  → reads raw/fass/markdown/   updates `fass.{championed,article_count,
                                     dedicated_count,first_year,last_year}` and
                                     replaces the `## FASS Write-ups` section.
  dtew  → reads raw/dtew/markdown/   updates `dte.{championed,article_count,
                                     dedicated_count,first_year,last_year}` —
                                     piggybacks on the existing `dte:` block
                                     (Robert Panzer's company; portfolio data
                                     lives there too) and replaces the
                                     `## DTEW Write-ups` section.

Why DTEW writes into the `dte` block
------------------------------------
The schema already has `dte:` for Down to Earth portfolio data (in_portfolio,
cuvee_count, price_min, price_max from `ingest_dte_jsx.py`). DTEW is the same
company's editorial blog. One retailer = one frontmatter key; we just add the
article-coverage fields alongside the existing portfolio fields. Sections stay
separate (`## Down to Earth Wines (Panzer)` for portfolio, `## DTEW Write-ups`
for blog articles).

Insert-or-update frontmatter
----------------------------
Unlike the CSW ingest (which assumes `chambers.{championed,...}` keys already
exist on every producer page), most pages today have `fass: { in_portfolio:
false }` and a similarly minimal `dte:` block. This script will INSERT the new
fields if absent. It still keeps unrelated fields in place.

Output
------
Updates `wiki/producers/*.md` in place. Writes a report to
`build/<source>_ingest_report.md` (matched count, top 30, no-match list).
No-match articles are not auto-created as new producer pages — that's an LLM
curation call (per CLAUDE.md anti-pattern: "don't bulk-create producer pages
from a single retailer source").

Usage
-----
  python scripts/ingest_blog_articles.py --source fass
  python scripts/ingest_blog_articles.py --source dtew
  python scripts/ingest_blog_articles.py --source fass --dry-run   # report only, no writes
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
BUILD = VAULT / "build"

MIN_MATCH_LEN = 5
EXCERPT_CHARS = 260


# --------------------------------------------------------------------------- #
# Source configuration                                                        #
# --------------------------------------------------------------------------- #

@dataclass
class SourceConfig:
    name: str               # cli flag value: "fass" | "dtew"
    raw_dir: Path           # raw/<src>/markdown/
    retailer_key: str       # frontmatter retailer block: "fass" | "dte"
    section_header: str     # "## FASS Write-ups" | "## DTEW Write-ups"
    report_path: Path

    # Display-side only (frontmatter remains in the article files themselves)
    display_label: str      # "FASS" | "DTEW" (for log output)


SOURCES: dict[str, SourceConfig] = {
    "fass": SourceConfig(
        name="fass",
        raw_dir=VAULT / "raw" / "fass" / "markdown",
        retailer_key="fass",
        section_header="## FASS Write-ups",
        report_path=BUILD / "fass_ingest_report.md",
        display_label="FASS",
    ),
    "dtew": SourceConfig(
        name="dtew",
        raw_dir=VAULT / "raw" / "dtew" / "markdown",
        retailer_key="dte",  # piggyback on the existing dte: block
        section_header="## DTEW Write-ups",
        report_path=BUILD / "dtew_ingest_report.md",
        display_label="DTEW",
    ),
}


# --------------------------------------------------------------------------- #
# Frontmatter parsing (mirrors ingest_csw.py)                                 #
# --------------------------------------------------------------------------- #

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def get_fm_field(fm: str, key: str) -> str | None:
    m = re.search(rf'^{re.escape(key)}:\s*"?(.*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1) if m else None


def get_fm_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', inner):
        v = next((x for x in part if x), "").strip()
        if v:
            out.append(v)
    return out


# --------------------------------------------------------------------------- #
# Retailer block insert-or-update                                             #
# --------------------------------------------------------------------------- #
#
# We need to mutate frontmatter blocks like:
#
#   retailers:
#     fass:
#       in_portfolio: false        <- existing
#       championed: true           <- INSERT if missing, UPDATE if present
#       article_count: 4
#       dedicated_count: 1
#       first_year: 2022
#       last_year: 2024
#
# Strategy: locate the line `  <key>:` (2-space indent), then walk subsequent
# lines while they remain indented deeper (4+ spaces). Build a dict of
# key→(line_idx, value). Update existing lines in-place; for missing keys,
# insert new lines at the end of the block. Preserve all other content.

NEW_FIELDS = ("championed", "article_count", "dedicated_count", "first_year", "last_year")
INDENT_BLOCK = "    "  # 4 spaces — children of a retailer key


def _find_retailer_block(fm_lines: list[str], key: str) -> tuple[int, int] | None:
    """Return (start_idx, end_idx) for the lines belonging to `key:` block.
    end_idx is exclusive — first line that is no longer part of the block."""
    header_re = re.compile(rf"^  {re.escape(key)}:\s*$")
    start = -1
    for i, line in enumerate(fm_lines):
        if header_re.match(line):
            start = i
            break
    if start < 0:
        return None
    end = start + 1
    while end < len(fm_lines):
        line = fm_lines[end]
        # Block continues while the line is empty OR starts with 4+ spaces
        if line.strip() == "":
            # Blank line could mean end-of-block or just spacing — peek ahead
            if end + 1 < len(fm_lines) and fm_lines[end + 1].startswith(INDENT_BLOCK):
                end += 1
                continue
            break
        if line.startswith(INDENT_BLOCK):
            end += 1
            continue
        break
    return start, end


def update_retailer_fields(fm: str, key: str, values: dict[str, str]) -> tuple[str, bool]:
    """Insert/update {field: rendered_value} pairs inside the `<key>:` block.
    Returns (new_fm, block_existed)."""
    lines = fm.splitlines()
    block = _find_retailer_block(lines, key)
    if block is None:
        return fm, False

    start, end = block
    field_re = {
        f: re.compile(rf"^{INDENT_BLOCK}{re.escape(f)}:\s*(.*)$") for f in values
    }
    found: dict[str, int] = {}
    for i in range(start + 1, end):
        for f, rx in field_re.items():
            if rx.match(lines[i]):
                found[f] = i
                break

    # Update existing fields
    for f, idx in found.items():
        lines[idx] = f"{INDENT_BLOCK}{f}: {values[f]}"

    # Insert missing fields just before the end of the block, preserving order
    missing = [f for f in values if f not in found]
    if missing:
        # Strip trailing blank lines from the block before insertion
        insert_at = end
        while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        new_lines = [f"{INDENT_BLOCK}{f}: {values[f]}" for f in missing]
        lines = lines[:insert_at] + new_lines + lines[insert_at:]

    return "\n".join(lines), True


# --------------------------------------------------------------------------- #
# Matching algorithm (copied from ingest_csw.py — same logic)                 #
# --------------------------------------------------------------------------- #

def ascii_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


GENERIC_SUFFIXES = (
    " Père et Fils", " Père & Fils", " Pere et Fils", " Pere & Fils",
    " et Fils", " & Fils", " et Fille", " et Filles",
    " Family", " Vignerons", " Frères", " Freres", " & Sons",
)


def build_match_names(name: str, aliases: list[str]) -> list[str]:
    out = {name}
    for a in aliases:
        out.add(a)
    for n in list(out):
        if " / " in n:
            for part in n.split(" / "):
                part = part.strip()
                if " " in part and len(part) >= MIN_MATCH_LEN:
                    out.add(part)
    for n in list(out):
        for suf in GENERIC_SUFFIXES:
            if n.endswith(suf):
                short = n[: -len(suf)].strip()
                if len(short) >= MIN_MATCH_LEN:
                    out.add(short)
    for n in list(out):
        for prefix in ("Domaine ", "Château ", "Chateau ", "Weingut ", "Bodegas "):
            if n.startswith(prefix):
                short = n[len(prefix):].strip()
                if len(short) >= MIN_MATCH_LEN:
                    out.add(short)
    return sorted({ascii_lower(n) for n in out if len(n) >= MIN_MATCH_LEN})


def _name_pattern(n: str) -> str:
    tokens = [t for t in re.split(r"[\s\-]+", n.strip()) if t]
    if not tokens:
        return ""
    joined = r"[\s\-]+".join(re.escape(t) for t in tokens)
    return r"\b" + joined + r"\b"


# --------------------------------------------------------------------------- #
# Article model                                                               #
# --------------------------------------------------------------------------- #

@dataclass
class Article:
    slug: str
    title: str
    url: str
    date: str               # "YYYY-MM" or "YYYY" or ""
    body_raw: str
    title_norm: str
    body_norm: str
    producer_hint: str      # value of `producer:` from frontmatter (may be "")

    @property
    def year(self) -> int:
        m = re.match(r"^(\d{4})", self.date)
        return int(m.group(1)) if m else 0

    @property
    def sort_key(self) -> tuple:
        # Newest first; undated last
        if re.match(r"^\d{4}-\d{2}$", self.date):
            y, mo = self.date.split("-")
            return (0, -(int(y) * 100 + int(mo)))
        if re.match(r"^\d{4}$", self.date):
            return (0, -int(self.date) * 100)
        return (1, 0)


def _normalize_year_month(date_field: str, slug: str) -> str:
    """Reduce a YYYY-MM-DD frontmatter date to YYYY-MM. Empty → '' (compile_csw
    falls back to slug; here the scraper always writes YYYY-MM-DD or '')."""
    m = re.match(r"^(\d{4})-(\d{2})", date_field)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    # very old/scanned slugs sometimes carry a year prefix — last-resort
    m = re.match(r"^(\d{4})", slug)
    if m and 2000 <= int(m.group(1)) <= 2030:
        return m.group(1)
    return ""


def load_articles(src: SourceConfig) -> list[Article]:
    out: list[Article] = []
    if not src.raw_dir.exists():
        return out
    for p in src.raw_dir.glob("*.md"):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, body = parts
        title = get_fm_field(fm, "title") or ""
        url = get_fm_field(fm, "url") or ""
        date = (get_fm_field(fm, "date") or "").strip()
        slug = get_fm_field(fm, "slug") or p.stem
        producer_hint = get_fm_field(fm, "producer") or ""
        # Strip the leading "# Title" the scraper writes
        body = re.sub(r"^\s*#\s+[^\n]*\n+", "", body, count=1)
        out.append(
            Article(
                slug=slug,
                title=title,
                url=url,
                date=_normalize_year_month(date, slug),
                body_raw=body,
                title_norm=ascii_lower(title),
                body_norm=ascii_lower(body),
                producer_hint=producer_hint,
            )
        )
    return out


def match_article(art: Article, names: list[str]) -> tuple[bool, bool]:
    pats = [p for p in (_name_pattern(n) for n in names) if p]
    for pat in pats:
        if re.search(pat, art.title_norm):
            return True, True       # matched + dedicated (title hit)
    for pat in pats:
        if re.search(pat, art.body_norm):
            return True, False
    return False, False


def extract_excerpt(body_raw: str, chars: int = EXCERPT_CHARS) -> str:
    text = re.sub(r"\n+", " ", body_raw.strip())
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    if len(text) > chars:
        cut = text[:chars]
        if " " in cut:
            cut = cut[: cut.rfind(" ")]
        return cut + "…"
    return text


# --------------------------------------------------------------------------- #
# Section render + replace                                                    #
# --------------------------------------------------------------------------- #

def render_writeups(section_header: str, matches: list[tuple[Article, bool]]) -> str:
    lines = [section_header, ""]
    for art, dedicated in matches:
        marker = "★ " if dedicated else ""
        date = art.date if art.date else "undated"
        lines.append(f"### {marker}[{art.title}]({art.url})")
        lines.append(f"*{date}*")
        lines.append("")
        excerpt = extract_excerpt(art.body_raw)
        if excerpt:
            lines.append(f"> {excerpt}")
            lines.append("")
    # No trailing whitespace; replace_section adds the canonical separators.
    return "\n".join(lines).rstrip()


def _section_re(header: str) -> re.Pattern[str]:
    """Match the section from `## Header` up to the next `## ` heading or EOF."""
    return re.compile(
        rf"{re.escape(header)}\n.*?(?=\n## [^#]|\Z)", re.DOTALL
    )


def replace_section(body: str, header: str, new_section: str) -> str:
    """Replace existing `## Header` section, or append. Result body always ends `\\n`."""
    new_section = new_section.rstrip()
    rx = _section_re(header)
    if rx.search(body):
        # Strip trailing newlines from the existing section before substitution
        # so the file's overall trailing-whitespace shape stays stable.
        new_body = rx.sub(new_section, body, count=1)
    else:
        new_body = body.rstrip() + "\n\n" + new_section
    return new_body.rstrip() + "\n"


# --------------------------------------------------------------------------- #
# Process                                                                     #
# --------------------------------------------------------------------------- #

@dataclass
class ProducerResult:
    slug: str
    name: str
    matched: int = 0
    dedicated: int = 0
    first_year: int = 0
    last_year: int = 0
    block_missing: bool = False
    skipped_reason: str = ""


def process(src: SourceConfig, *, dry_run: bool) -> int:
    print(f"Loading {src.display_label} articles from {src.raw_dir}...")
    articles = load_articles(src)
    dated = sum(1 for a in articles if a.date)
    print(f"Loaded {len(articles)} articles ({dated} dated)")

    if not articles:
        print(f"No articles found in {src.raw_dir}. Run scrape_blogs.py --site {src.name} first.", file=sys.stderr)
        return 1

    if not PRODUCERS.exists():
        print(f"No producers directory at {PRODUCERS}", file=sys.stderr)
        return 1

    producer_files = sorted(PRODUCERS.glob("*.md"))
    print(f"Scanning {len(producer_files)} producers...")

    results: list[ProducerResult] = []
    files_written = 0

    for p in producer_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, body = parts
        if get_fm_field(fm, "type") != "producer":
            continue
        name = get_fm_field(fm, "name") or ""
        slug = get_fm_field(fm, "slug") or p.stem
        aliases = get_fm_list(fm, "aliases")

        result = ProducerResult(slug=slug, name=name)
        names = build_match_names(name, aliases)
        if not names:
            result.skipped_reason = "no match names (name too short?)"
            results.append(result)
            continue

        matches: list[tuple[Article, bool]] = []
        seen: set[str] = set()
        for art in articles:
            key = art.url or art.slug
            if key in seen:
                continue
            ok, dedicated = match_article(art, names)
            if ok:
                matches.append((art, dedicated))
                seen.add(key)

        matches.sort(key=lambda x: x[0].sort_key)
        article_count = len(matches)
        dedicated_count = sum(1 for _, d in matches if d)
        years = [a.year for a, _ in matches if a.year > 0]
        first_year = min(years) if years else 0
        last_year = max(years) if years else 0
        championed = dedicated_count > 0

        # Update the retailer block (insert-or-update)
        new_fm, block_existed = update_retailer_fields(
            fm,
            src.retailer_key,
            {
                "championed": "true" if championed else "false",
                "article_count": str(article_count),
                "dedicated_count": str(dedicated_count),
                "first_year": str(first_year),
                "last_year": str(last_year),
            },
        )
        if not block_existed:
            result.block_missing = True

        if matches:
            new_body = replace_section(body, src.section_header, render_writeups(src.section_header, matches))
        else:
            new_body = body

        if not dry_run:
            p.write_text(f"---\n{new_fm}\n---\n{new_body}", encoding="utf-8")
            if matches or new_fm != fm:
                files_written += 1

        result.matched = article_count
        result.dedicated = dedicated_count
        result.first_year = first_year
        result.last_year = last_year
        results.append(result)

    # ----- report -----
    BUILD.mkdir(parents=True, exist_ok=True)
    matched_results = [r for r in results if r.matched > 0]
    no_match = [r for r in results if r.matched == 0 and not r.skipped_reason]
    skipped = [r for r in results if r.skipped_reason]
    block_missing = [r for r in results if r.block_missing]
    matched_results.sort(key=lambda r: (-r.matched, r.name))

    lines = [
        "---",
        "type: ingest_report",
        f"source: {src.name}_markdown",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_producers: {len(results)}",
        f"matched_producers: {len(matched_results)}",
        f"no_match_producers: {len(no_match)}",
        f"skipped: {len(skipped)}",
        f"block_missing: {len(block_missing)}",
        f"total_articles: {len(articles)}",
        f"dated_articles: {dated}",
        f"dry_run: {str(dry_run).lower()}",
        "---",
        "",
        f"# {src.display_label} ingest report",
        "",
        f"Scanned {len(articles)} {src.display_label} articles against {len(results)} producer pages.",
        f"Updated **{len(matched_results)}** producer files with matching {src.display_label} write-ups.",
    ]
    if block_missing:
        lines.append(
            f"\n**Note:** {len(block_missing)} producer pages were missing the `{src.retailer_key}:` "
            f"frontmatter block entirely (no `in_portfolio: false` skeleton). Those got the new "
            f"fields appended into the existing block where one was found, but pages with NO "
            f"`{src.retailer_key}:` block at all were skipped on the frontmatter side. "
            f"The prose section was still written in those cases."
        )
    lines += [
        "",
        "## Top 30 by article count",
        "",
        "| Slug | Name | Articles | Dedicated | First | Last |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in matched_results[:30]:
        lines.append(
            f"| `{r.slug}` | {r.name} | {r.matched} | {r.dedicated} | "
            f"{r.first_year or '—'} | {r.last_year or '—'} |"
        )
    lines += [
        "",
        f"## No {src.display_label} matches ({len(no_match)})",
        "",
        f"These wiki producers had zero matching articles in `raw/{src.name}/markdown/`.",
        "",
    ]
    for r in sorted(no_match, key=lambda r: r.name)[:80]:
        lines.append(f"- `{r.slug}` — {r.name}")
    if len(no_match) > 80:
        lines.append(f"- … and {len(no_match) - 80} more")

    # Unmatched-from-the-other-direction: articles whose producer hint didn't
    # land in any wiki producer page. These are the "candidate new producers".
    matched_urls: set[str] = set()
    for r in matched_results:
        # rebuild matches per producer to count URLs (skip — too expensive; just
        # report based on producer_hint that isn't a known wiki slug)
        pass
    known_slugs = {r.slug for r in results}

    def _slugify(s: str) -> str:
        s = ascii_lower(s)
        s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
        return s

    candidate_producers: dict[str, list[Article]] = {}
    for art in articles:
        if not art.producer_hint:
            continue
        cand_slug = _slugify(art.producer_hint)
        if cand_slug in known_slugs:
            continue
        candidate_producers.setdefault(cand_slug, []).append(art)

    if candidate_producers:
        lines += [
            "",
            f"## Candidate new producers ({len(candidate_producers)})",
            "",
            f"Articles whose `producer:` hint doesn't match any existing wiki/producers/ slug. "
            f"**Do not auto-create**; review for curation per CLAUDE.md anti-pattern.",
            "",
            "| Candidate slug | Article count | Latest article |",
            "|---|---:|---|",
        ]
        for cand, arts in sorted(candidate_producers.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:60]:
            arts.sort(key=lambda a: a.sort_key)
            latest = arts[0] if arts else None
            latest_str = f"[{latest.title[:60]}…]({latest.url})" if latest else ""
            lines.append(f"| `{cand}` | {len(arts)} | {latest_str} |")
        if len(candidate_producers) > 60:
            lines.append(f"\n_… and {len(candidate_producers) - 60} more candidates_")

    if skipped:
        lines += ["", f"## Skipped ({len(skipped)})", ""]
        for r in skipped:
            lines.append(f"- `{r.slug}` — {r.skipped_reason}")

    src.report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"{'DRY-RUN: would update' if dry_run else 'Updated'}: {files_written} producer files")
    print(f"matched producers: {len(matched_results)}")
    print(f"no-match producers: {len(no_match)}")
    print(f"candidate new producers: {len(candidate_producers)}")
    print(f"report: {src.report_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--source", required=True, choices=sorted(SOURCES.keys()),
                    help="Which raw/<source>/markdown/ to ingest")
    ap.add_argument("--dry-run", action="store_true",
                    help="Compute matches and write the report; do NOT modify producer files")
    args = ap.parse_args()
    return process(SOURCES[args.source], dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
