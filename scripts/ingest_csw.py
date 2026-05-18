"""
Scan raw/csw/markdown/*.md (1,623 Chambers Street articles) and fold matching
articles into each wiki/producers/*.md file's `## CSW Write-ups` section.

For each producer:
  - Build match names: canonical `name` + `aliases` + a short form (strip
    `Domaine `/`Château `/`Chateau ` prefix).
  - Scan every article title + body for word-boundary matches of those names
    (ASCII-normalized, case-insensitive). Minimum length 5 chars to avoid
    noise. Dedicated if the match is in the title.
  - Extract the article date from a leading `M/D/YY -` pattern in the body
    (Chambers email convention), fall back to the article slug.
  - Update `retailers.chambers.{championed,article_count,dedicated_count,
    first_year,last_year}` in the frontmatter.
  - Replace the `## CSW Write-ups` section body with a list of matches,
    newest first, `★` prefix on dedicated, excerpt below.

No-match producers are left alone.

A summary report lands in build/csw_ingest_report.md.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RAW_CSW = VAULT / "raw" / "csw" / "markdown"
REPORT = VAULT / "build" / "csw_ingest_report.md"

MIN_MATCH_LEN = 5
EXCERPT_CHARS = 260


# --------- frontmatter parsing ---------

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


def repair_frontmatter(fm: str) -> str:
    """Repair corruption from a previous buggy run: `last_year: N  dte:` on
    a single line (newline eaten). Idempotent."""
    # Exactly 2 spaces between last_year's value and the next top-level key.
    fm = re.sub(
        r"(    last_year:\s*\d+)  (dte|raeders|fass):",
        r"\g<1>\n  \g<2>:",
        fm,
    )
    return fm


def set_chambers_fields(
    fm: str,
    championed: bool,
    article_count: int,
    dedicated_count: int,
    first_year: int,
    last_year: int,
) -> str:
    """Update each chambers.* field by targeted line-level substitution.
    Preserves surrounding newlines/indentation."""
    fm = re.sub(
        r"(    championed: )(?:true|false)",
        lambda m: f"{m.group(1)}{'true' if championed else 'false'}",
        fm, count=1,
    )
    fm = re.sub(r"(    article_count: )\d+",
                lambda m: f"{m.group(1)}{article_count}", fm, count=1)
    fm = re.sub(r"(    dedicated_count: )\d+",
                lambda m: f"{m.group(1)}{dedicated_count}", fm, count=1)
    fm = re.sub(r"(    first_year: )\d+",
                lambda m: f"{m.group(1)}{first_year}", fm, count=1)
    fm = re.sub(r"(    last_year: )\d+",
                lambda m: f"{m.group(1)}{last_year}", fm, count=1)
    return fm


# --------- matching ---------

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
    # Split slash-separated multi-name forms ("Peter Lauer / Weingut Lauer",
    # "Gilles / Jean / Maxime Lafouge") and emit each multi-word part. Skip
    # single-word parts to avoid first-name false positives ("Gilles", "Jean").
    for n in list(out):
        if " / " in n:
            for part in n.split(" / "):
                part = part.strip()
                if " " in part and len(part) >= MIN_MATCH_LEN:
                    out.add(part)
    # Strip generic family suffixes ("Rapet Père et Fils" → "Rapet").
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
    """Tolerant whole-word pattern: matches space/hyphen variants between tokens.
    e.g. 'schafer frohlich' matches 'Schafer Frohlich', 'Schäfer-Fröhlich'."""
    tokens = [t for t in re.split(r"[\s\-]+", n.strip()) if t]
    if not tokens:
        return ""
    joined = r"[\s\-]+".join(re.escape(t) for t in tokens)
    return r"\b" + joined + r"\b"


# --------- date extraction ---------

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
    "june": 6, "july": 7, "august": 8, "september": 9,
    "october": 10, "november": 11, "december": 12,
}

LEADING_SLASH_DATE = re.compile(
    r"^\s*(?:\*|﻿|_|\s)*?"            # optional leading emphasis/BOM
    r"(\d{1,2})/(\d{1,2})/(\d{2,4})"  # M/D/YY or M/D/YYYY
)

INLINE_MONTH_DATE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(\d{1,2}),?\s+(\d{4})",
    re.IGNORECASE,
)


def _normalize_year(yy: int) -> int:
    if yy < 100:
        # Chambers started 2001. 06..26 → 2006..2026; 99 → 1999.
        return 2000 + yy if yy <= 40 else 1900 + yy
    return yy


def extract_date(body: str, slug: str, fm_date: str) -> str:
    """Return YYYY-MM if parseable, else ''.

    Priority: explicit fm date > leading M/D/Y in body > inline 'Month DD, YYYY' near top > slug year.
    """
    if fm_date:
        m = re.match(r"^(\d{4})-(\d{2})", fm_date)
        if m:
            return f"{m.group(1)}-{m.group(2)}"

    head = body[:400]
    m = LEADING_SLASH_DATE.match(head)
    if m:
        mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = _normalize_year(y)
        if 1 <= mo <= 12 and 2000 <= y <= 2030:
            return f"{y:04d}-{mo:02d}"

    m = INLINE_MONTH_DATE.search(body[:1200])
    if m:
        mo = MONTH_MAP.get(m.group(1).lower(), 0)
        y = int(m.group(3))
        if mo and 2000 <= y <= 2030:
            return f"{y:04d}-{mo:02d}"

    # Slug-based fallback: some slugs are YYYY-MM-DD or YYYY-slug-rest
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", slug)
    if m and 2000 <= int(m.group(1)) <= 2030:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.match(r"^(\d{4})-", slug)
    if m and 2000 <= int(m.group(1)) <= 2030:
        return f"{m.group(1)}"

    return ""


# --------- article model ---------

@dataclass
class Article:
    slug: str
    title: str
    url: str
    date: str          # "YYYY-MM" or "YYYY" or ""
    body_raw: str
    title_norm: str
    body_norm: str

    @property
    def year(self) -> int:
        m = re.match(r"^(\d{4})", self.date)
        return int(m.group(1)) if m else 0

    @property
    def sort_key(self) -> tuple:
        if re.match(r"^\d{4}-\d{2}$", self.date):
            y, mo = self.date.split("-")
            return (0, -(int(y) * 100 + int(mo)))
        if re.match(r"^\d{4}$", self.date):
            return (0, -int(self.date) * 100)
        return (1, 0)


def load_articles() -> list[Article]:
    articles = []
    for p in RAW_CSW.glob("*.md"):
        txt = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(txt)
        if not parts:
            continue
        fm, body = parts
        title = get_fm_field(fm, "title") or ""
        url = get_fm_field(fm, "url") or ""
        fm_date = (get_fm_field(fm, "date") or "").strip()
        slug = get_fm_field(fm, "slug") or p.stem
        body = re.sub(r"^\s*#\s+[^\n]*\n+", "", body, count=1)
        articles.append(
            Article(
                slug=slug,
                title=title,
                url=url,
                date=extract_date(body, slug, fm_date),
                body_raw=body,
                title_norm=ascii_lower(title),
                body_norm=ascii_lower(body),
            )
        )
    return articles


def match_article(art: Article, names: list[str]) -> tuple[bool, bool]:
    pats = [p for p in (_name_pattern(n) for n in names) if p]
    for pat in pats:
        if re.search(pat, art.title_norm):
            return True, True
    for pat in pats:
        if re.search(pat, art.body_norm):
            return True, False
    return False, False


def extract_excerpt(body_raw: str, chars: int = EXCERPT_CHARS) -> str:
    text = re.sub(r"\n+", " ", body_raw.strip())
    text = re.sub(r"\s+", " ", text).strip()
    # Strip embedded markdown images that bloat excerpts
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


def render_writeups(matches: list[tuple[Article, bool]]) -> str:
    lines = ["## CSW Write-ups", ""]
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
    return "\n".join(lines).rstrip() + "\n\n"


CSW_SECTION_RE = re.compile(
    r"## CSW Write-ups\n.*?(?=\n## [^#]|\Z)", re.DOTALL
)


def replace_csw_section(body: str, new_section: str) -> str:
    if CSW_SECTION_RE.search(body):
        return CSW_SECTION_RE.sub(new_section.rstrip() + "\n", body, count=1)
    return body.rstrip() + "\n\n" + new_section


# --------- main ---------

@dataclass
class ProducerResult:
    slug: str
    name: str
    matched: int = 0
    dedicated: int = 0
    first_year: int = 0
    last_year: int = 0
    skipped_reason: str = ""


def process():
    print(f"Loading articles from {RAW_CSW}...")
    articles = load_articles()
    dated = sum(1 for a in articles if a.date)
    print(f"Loaded {len(articles)} articles ({dated} dated)")

    results: list[ProducerResult] = []
    producer_files = sorted(PRODUCERS.glob("*.md"))
    print(f"Scanning {len(producer_files)} producers...")

    for p in producer_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        text = repair_frontmatter(text)  # heal any prior corruption
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
            # Still write the repaired file even if we skip matching
            p.write_text(f"---\n{fm}\n---\n{body}", encoding="utf-8")
            continue

        matches: list[tuple[Article, bool]] = []
        seen: set[str] = set()
        for art in articles:
            if art.url in seen:
                continue
            ok, dedicated = match_article(art, names)
            if ok:
                matches.append((art, dedicated))
                seen.add(art.url)

        matches.sort(key=lambda x: x[0].sort_key)
        article_count = len(matches)
        dedicated_count = sum(1 for _, d in matches if d)
        years = [art.year for art, _ in matches if art.year > 0]
        first_year = min(years) if years else 0
        last_year = max(years) if years else 0
        championed = dedicated_count > 0

        new_fm = set_chambers_fields(
            fm, championed, article_count, dedicated_count, first_year, last_year
        )
        if matches:
            new_body = replace_csw_section(body, render_writeups(matches))
        else:
            new_body = body

        p.write_text(f"---\n{new_fm}\n---\n{new_body}", encoding="utf-8")

        result.matched = article_count
        result.dedicated = dedicated_count
        result.first_year = first_year
        result.last_year = last_year
        results.append(result)

    # --- report ---
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    matched_results = [r for r in results if r.matched > 0]
    no_match = [r for r in results if r.matched == 0 and not r.skipped_reason]
    skipped = [r for r in results if r.skipped_reason]
    matched_results.sort(key=lambda r: (-r.matched, r.name))

    lines = [
        "---",
        "type: ingest_report",
        "source: csw_markdown",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_producers: {len(results)}",
        f"matched_producers: {len(matched_results)}",
        f"no_match_producers: {len(no_match)}",
        f"skipped: {len(skipped)}",
        f"total_articles: {len(articles)}",
        f"dated_articles: {dated}",
        "---",
        "",
        "# CSW ingest report",
        "",
        f"Scanned {len(articles)} Chambers Street articles against {len(results)} producer pages.",
        f"Updated **{len(matched_results)}** producer files with matching CSW Write-ups.",
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
        f"## No CSW matches ({len(no_match)})",
        "",
        "These producers in `wiki/producers/` had zero article matches.",
        "Most are DTE/Raeder's/FASS-only or have aliases not yet recorded.",
        "",
    ]
    for r in sorted(no_match, key=lambda r: r.name)[:80]:
        lines.append(f"- `{r.slug}` — {r.name}")
    if len(no_match) > 80:
        lines.append(f"- … and {len(no_match) - 80} more")

    if skipped:
        lines += ["", f"## Skipped ({len(skipped)})", ""]
        for r in skipped:
            lines.append(f"- `{r.slug}` — {r.skipped_reason}")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nUpdated {len(matched_results)} producer files")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    process()
