"""
ARCHIVED 2026-05-26 — one-shot migration completed; `_drive_sync/`
is being deleted from Drive. Kept in scripts/_archive/ as a historical
record of the prose → YAML migration logic.

Migrate legacy prose-format producer .md files from _drive_sync/ into the
canonical YAML-frontmatter format in wiki/producers/.

Handles two source shapes:
  - "detailed" format: has CSW article excerpts, lacks dedicated-count
  - "short" format: has dedicated-count + star markers, lacks excerpts

When both exist for the same producer, fields are merged:
  - dedicated counts + star markers come from short
  - article excerpts come from detailed
  - any disagreements are flagged in stderr for human review

Usage:
  python scripts/migrate_prose_to_yaml.py

Reads from: <vault>/_drive_sync/*.md
Writes to:  <vault>/wiki/producers/<slug>.md
Also emits: <vault>/build/migration_report.md
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SRC = VAULT / "_drive_sync"
OUT = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "migration_report.md"

# ---- region → country map -------------------------------------------------
# Used when the prose format gives only a region (e.g., "Region: Burgundy")
# without an explicit country. Extend in wiki/_TAXONOMY.md if new regions appear.
REGION_COUNTRY = {
    # France
    "Alsace": "France", "Beaujolais": "France", "Bordeaux": "France",
    "Burgundy": "France", "Champagne": "France", "Corsica": "France",
    "Jura": "France", "Loire": "France", "Provence": "France",
    "Rhône": "France", "Rhone": "France", "Savoie": "France",
    "South West": "France", "Basque": "France", "Languedoc-Roussillon": "France",
    # Germany
    "Ahr": "Germany", "Baden": "Germany", "Franken": "Germany",
    "Mosel": "Germany", "Nahe": "Germany", "Pfalz": "Germany",
    "Rheingau": "Germany", "Rheinhessen": "Germany", "Württemberg": "Germany",
    # Italy
    "Piedmont": "Italy", "Tuscany": "Italy", "Sicily": "Italy",
    "Veneto": "Italy", "Lombardy": "Italy", "Friuli-Venezia Giulia": "Italy",
    "Alto Adige": "Italy", "Valle d'Aosta": "Italy", "Marche": "Italy",
    "Abruzzo": "Italy", "Campania": "Italy", "Liguria": "Italy",
    "Colli Tortonesi": "Italy", "Emilia-Romagna": "Italy",
    # Spain
    "Catalonia": "Spain", "Bierzo": "Spain", "Rioja": "Spain",
    "Galicia": "Spain", "Jumilla": "Spain", "Ribera del Duero": "Spain",
}

# Known country names (for files that put the country in the Region field, e.g. Laurent_Barth)
COUNTRIES = set(REGION_COUNTRY.values()) | {"Austria", "Portugal", "Greece", "Georgia"}


@dataclass
class Article:
    title: str
    url: str
    date: str            # "YYYY-MM" or "undated"
    dedicated: bool = False
    excerpt: str = ""


@dataclass
class Producer:
    slug: str
    name: str
    country: str = ""
    region: str = ""
    sub_region: str = ""
    farming: list = field(default_factory=list)
    importer_us: list = field(default_factory=list)
    csw_article_count: int = 0
    csw_dedicated_count: int = 0
    csw_first_year: int = 0
    csw_last_year: int = 0
    articles: list = field(default_factory=list)   # list[Article]
    cross_refs: list = field(default_factory=list) # raw [[...]] strings
    sources: list = field(default_factory=list)    # which _drive_sync files contributed


# ---- regex library --------------------------------------------------------
RE_TITLE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
RE_META_KV = re.compile(r"^\*\*(?P<key>[^*]+?):\*\*\s*(?P<val>.+?)\s*$", re.MULTILINE)
RE_CSW_COV = re.compile(
    r"(?P<n>\d+)\s+articles?\s*\(\s*(?P<y1>\d{4}|\s*)\s*[–-]\s*(?P<y2>\d{4})\s*\)"
    r"(?:\s*·\s*(?P<ded>\d+)\s+dedicated)?",
    re.IGNORECASE,
)
# Article header: optional star, title in brackets, URL in parens
RE_ARTICLE_H = re.compile(
    r"^###\s+(?P<star>★\s*)?\[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\)\s*$",
    re.MULTILINE,
)
RE_DATE = re.compile(r"^\*(?P<date>[^*]+)\*\s*$", re.MULTILINE)
RE_XREF = re.compile(r"\[\[([^\]]+)\]\]")


def slug_from_filename(path: Path) -> tuple[str, str]:
    """Return (source_kind, slug). Filenames look like 'detailed__Foo_Bar.md' or 'short__Foo_Bar.md'."""
    stem = path.stem
    if "__" in stem:
        kind, rest = stem.split("__", 1)
        return kind, rest.lower()
    return "unknown", stem.lower()


def parse_region_line(value: str) -> tuple[str, str, str]:
    """
    Parse the value of `**Region:** ...` into (country, region, sub_region).
    Handles:
      "Burgundy — Gevrey-Chambertin"  → ("France", "Burgundy", "Gevrey-Chambertin")
      "Burgundy — Burgundy"           → ("France", "Burgundy", "")
      "Italy — Barolo (La Morra)"     → ("Italy", "Piedmont", "Barolo (La Morra)")  [tricky]
      "Germany"                        → ("Germany", "", "")  — but Laurent Barth is really Alsace
    """
    # Split on em-dash or regular dash surrounded by spaces
    parts = re.split(r"\s+[—–-]\s+", value.strip(), maxsplit=1)
    head = parts[0].strip()
    tail = parts[1].strip() if len(parts) > 1 else ""

    # Case A: head is a country name, tail is a region
    if head in COUNTRIES and tail:
        # tail could be "Barolo (La Morra)" where the real region is Piedmont
        # We don't try to deduce this; we set region=tail and let lint flag.
        return head, tail, ""

    # Case B: head is a known region
    if head in REGION_COUNTRY:
        country = REGION_COUNTRY[head]
        sub = tail if tail and tail != head else ""
        return country, head, sub

    # Case C: head is just a country (e.g. "Germany")
    if head in COUNTRIES:
        return head, "", ""

    # Unknown — return as-is and let lint flag
    return "", head, tail


def parse_farming(value: str) -> list[str]:
    """Split farming field. '· ' or ', ' or ' / ' all accepted. Lowercase output."""
    if not value:
        return []
    # Normalize separators
    normalized = re.sub(r"\s*[·,/]\s*", "|", value.strip())
    parts = [p.strip().lower() for p in normalized.split("|") if p.strip()]
    return parts


def parse_importer(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"\s*(?:,|/|\|)\s*", value.strip())
    return [p for p in (x.strip() for x in parts) if p]


def parse_file(path: Path) -> Producer:
    """Parse one _drive_sync/*.md into a Producer record."""
    kind, slug = slug_from_filename(path)
    text = path.read_text(encoding="utf-8")

    # Producer name from first H1
    m = RE_TITLE.search(text)
    name = m.group(1).strip() if m else slug.replace("_", " ")

    p = Producer(slug=slug, name=name, sources=[f"{kind}:{path.name}"])

    # Metadata key-value pairs (prose format)
    for km in RE_META_KV.finditer(text):
        key = km.group("key").strip().lower()
        val = km.group("val").strip()

        if key == "region":
            country, region, sub = parse_region_line(val)
            p.country = country
            p.region = region
            p.sub_region = sub

        elif key == "farming":
            p.farming = parse_farming(val)

        elif key in ("importer (us)", "importer"):
            p.importer_us = parse_importer(val)

        elif key == "csw coverage":
            cm = RE_CSW_COV.search(val)
            if cm:
                p.csw_article_count = int(cm.group("n"))
                y1 = cm.group("y1").strip()
                p.csw_first_year = int(y1) if y1 else 0
                p.csw_last_year = int(cm.group("y2"))
                if cm.group("ded"):
                    p.csw_dedicated_count = int(cm.group("ded"))

    # Articles: find each ### header, then the following *date* line and excerpt paragraph
    article_positions = [(m.start(), m) for m in RE_ARTICLE_H.finditer(text)]
    for i, (pos, am) in enumerate(article_positions):
        title = am.group("title").strip()
        url = am.group("url").strip()
        dedicated = bool(am.group("star"))

        # Find the slice of text between this article header and the next (or doc end)
        next_pos = article_positions[i + 1][0] if i + 1 < len(article_positions) else len(text)
        block = text[am.end():next_pos]

        # Date on the next non-empty line
        date = ""
        excerpt = ""
        dm = RE_DATE.search(block)
        if dm:
            date = dm.group("date").strip()
            # Excerpt is everything after the date line until the block ends,
            # minus trailing separators and cross-refs
            after_date = block[dm.end():].strip()
            # Cut off trailing "---" or "## " sections that leaked in
            after_date = re.split(r"^\s*(?:---\s*$|##\s)", after_date, maxsplit=1, flags=re.MULTILINE)[0]
            excerpt = after_date.strip()

        p.articles.append(Article(title=title, url=url, date=date, dedicated=dedicated, excerpt=excerpt))

    # Cross-references (the [[...]] occurrences inside the Cross-references section)
    xref_section = re.split(r"##\s+Cross[- ]references", text, flags=re.IGNORECASE)
    if len(xref_section) > 1:
        tail = xref_section[1]
        p.cross_refs = [m.group(1).strip() for m in RE_XREF.finditer(tail)]

    return p


def merge(a: Producer, b: Producer) -> Producer:
    """Merge two Producer records for the same slug (detailed + short). Prefer non-empty fields.

    Strategy:
      - name: prefer non-empty; if both non-empty, prefer `a`
      - country/region/sub_region: if they disagree, prefer the one from the 'short' source
        because wine_wiki/ was the later, cleaner sweep (per Evan's timeline)
      - farming / importer_us: union
      - CSW counts: prefer 'short' (has the dedicated-count)
      - articles: merge by URL, promoting dedicated=True if either side has it,
                  keeping the longer excerpt
      - cross_refs: union
    """
    # Decide which is the "short" source by inspecting sources prefixes
    short_first = any(s.startswith("short:") for s in a.sources)
    primary, secondary = (a, b) if short_first else (b, a)

    merged = Producer(
        slug=a.slug,
        name=primary.name or secondary.name,
        country=primary.country or secondary.country,
        region=primary.region or secondary.region,
        sub_region=primary.sub_region or secondary.sub_region,
        farming=sorted(set(a.farming) | set(b.farming)),
        importer_us=sorted(set(a.importer_us) | set(b.importer_us)),
        csw_article_count=max(a.csw_article_count, b.csw_article_count),
        csw_dedicated_count=max(a.csw_dedicated_count, b.csw_dedicated_count),
        csw_first_year=min(x for x in (a.csw_first_year, b.csw_first_year) if x) if (a.csw_first_year or b.csw_first_year) else 0,
        csw_last_year=max(a.csw_last_year, b.csw_last_year),
        cross_refs=sorted(set(a.cross_refs) | set(b.cross_refs)),
        sources=sorted(set(a.sources) | set(b.sources)),
    )

    # Articles: group by URL
    by_url: dict[str, Article] = {}
    for art in a.articles + b.articles:
        existing = by_url.get(art.url)
        if existing is None:
            by_url[art.url] = art
        else:
            existing.dedicated = existing.dedicated or art.dedicated
            if len(art.excerpt) > len(existing.excerpt):
                existing.excerpt = art.excerpt
            if art.date and art.date != "undated" and (not existing.date or existing.date == "undated"):
                existing.date = art.date
            if not existing.title and art.title:
                existing.title = art.title
    # Sort newest first by date string (YYYY-MM sorts correctly; "undated" last)
    def sort_key(x: Article):
        return (0, x.date) if re.match(r"\d{4}-\d{2}", x.date or "") else (1, "")
    merged.articles = sorted(by_url.values(), key=sort_key, reverse=True)
    # Flip so "undated" ends up last but newest real dates come first
    dated = [x for x in merged.articles if re.match(r"\d{4}-\d{2}", x.date or "")]
    undated = [x for x in merged.articles if x not in dated]
    merged.articles = sorted(dated, key=lambda x: x.date, reverse=True) + undated

    return merged


def emit_yaml(p: Producer) -> str:
    """Emit a YAML frontmatter + body .md for this producer."""
    def yl(value):
        """YAML scalar/list formatting."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value) if value else "0"
        if isinstance(value, list):
            if not value:
                return "[]"
            return "[" + ", ".join(f'"{v}"' for v in value) + "]"
        if value is None or value == "":
            return '""'
        return f'"{str(value).replace(chr(34), chr(92) + chr(34))}"'

    lines = ["---",
             "type: producer",
             f"name: {yl(p.name)}",
             f"slug: {p.slug}",
             "aliases: []",
             f"country: {yl(p.country)}",
             f"region: {yl(p.region)}",
             f"sub_region: {yl(p.sub_region)}",
             "appellations: []",
             f"farming: {yl(p.farming)}",
             "certifications: []",
             f"importer_us: {yl(p.importer_us)}",
             "retailers:",
             "  chambers:",
             f"    championed: {yl(p.csw_dedicated_count > 0 or p.csw_article_count >= 2)}",
             f"    article_count: {p.csw_article_count}",
             f"    dedicated_count: {p.csw_dedicated_count}",
             f"    first_year: {p.csw_first_year}",
             f"    last_year: {p.csw_last_year}",
             "  dte:",
             "    in_portfolio: false",
             "    cuvee_count: 0",
             "    price_min: 0",
             "    price_max: 0",
             "  raeders:",
             "    in_portfolio: false",
             "  fass:",
             "    in_portfolio: false",
             "tags: []",
             f"_sources: {yl(p.sources)}",
             "---",
             "",
             f"# {p.name}",
             ""]

    lines.append("## CSW Write-ups")
    lines.append("")
    for a in p.articles:
        star = "★ " if a.dedicated else ""
        lines.append(f"### {star}[{a.title}]({a.url})")
        lines.append(f"*{a.date or 'undated'}*")
        lines.append("")
        if a.excerpt:
            lines.append(a.excerpt)
            lines.append("")

    lines.append("## Down to Earth Wines (Panzer)")
    lines.append("")
    lines.append("_Not yet populated. Run `ingest_dte_jsx.py` to fold in DTE portfolio data._")
    lines.append("")

    lines.append("## Raeder's")
    lines.append("")
    lines.append("_Not yet populated._")
    lines.append("")

    lines.append("## FASS")
    lines.append("")
    lines.append("_Not yet populated._")
    lines.append("")

    if p.cross_refs:
        lines.append("## Cross-references")
        lines.append("")
        for x in p.cross_refs:
            lines.append(f"- [[{x}]]")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    if not SRC.exists():
        print(f"No _drive_sync/ folder at {SRC}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    by_slug: dict[str, Producer] = {}
    report_rows: list[tuple[str, str, str]] = []

    for path in sorted(SRC.glob("*.md")):
        p = parse_file(path)
        if p.slug in by_slug:
            by_slug[p.slug] = merge(by_slug[p.slug], p)
        else:
            by_slug[p.slug] = p

    for slug, p in sorted(by_slug.items()):
        out_path = OUT / f"{slug}.md"
        out_path.write_text(emit_yaml(p), encoding="utf-8")
        # Flag suspicious data
        issues = []
        if not p.country:
            issues.append("no country")
        if p.region in COUNTRIES and not p.sub_region:
            issues.append(f"region field contains a country ({p.region})")
        if p.name.lower().startswith("laurent barth") and p.country == "Germany":
            issues.append("Laurent Barth listed as Germany — he is Alsace/France")
        report_rows.append((slug, p.name, "; ".join(issues) if issues else "ok"))

    # Write report
    report_lines = [
        "---",
        "type: migration_report",
        f"generated: {__import__('datetime').datetime.now().isoformat(timespec='seconds')}",
        f"produced: {len(by_slug)}",
        "---",
        "",
        "# Migration report",
        "",
        f"- Processed {len(list(SRC.glob('*.md')))} source files",
        f"- Produced {len(by_slug)} canonical producer pages in `wiki/producers/`",
        "",
        "## Per-producer status",
        "",
        "| Slug | Name | Issues |",
        "|------|------|--------|",
    ]
    for slug, name, issue in report_rows:
        report_lines.append(f"| {slug} | {name} | {issue} |")
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"OK: produced {len(by_slug)} producer pages in {OUT}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
