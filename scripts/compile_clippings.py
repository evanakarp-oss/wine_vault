"""
compile_clippings.py — ingest Obsidian Web Clipper markdown from
`raw/clippings/<source>/` into producer-page body sections.

Each clipping is a single `.md` with YAML frontmatter naming the
producer; the compile pass extracts critic, score, drinking window,
and a short excerpt, and writes them to a `## <Source> Reviews`
section on the matching producer page.

Two sources currently wired:

  - vinous            → `## Vinous Reviews` section
  - wine_advocate     → `## Wine Advocate (Kelley)` section

Producer matching:

  1. Clipping frontmatter `producer_slug:` (preferred — explicit)
  2. Fallback: ascii_slug(producer_name) from the clipping title

Unmatched clippings get listed in `build/clippings_report.md` so they
can be reviewed and either aliased into an existing page or proposed
as a new producer (subject to the same curation rule as CSW/Raeders).

Usage:
    python scripts/compile_clippings.py vinous            # dry-run
    python scripts/compile_clippings.py vinous --apply    # write to pages
    python scripts/compile_clippings.py wine_advocate --apply
    python scripts/compile_clippings.py all --apply       # both sources

Idempotent: re-running rewrites the section in place; the producer
page's other sections are untouched.
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
PRODUCERS = VAULT / "wiki" / "producers"
CLIPPINGS = VAULT / "raw" / "clippings"
REPORT = VAULT / "build" / "clippings_report.md"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

SOURCES = {
    "vinous": {
        "section_header": "## Vinous Reviews",
        "default_critic": "Vinous",
    },
    "wine_advocate": {
        "section_header": "## Wine Advocate (Kelley)",
        "default_critic": "William Kelley",
    },
}


def ascii_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def split_fm(text: str):
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def fm_get(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip().strip("'") if m else ""


def first_two_sentences(body: str) -> str:
    """Pull the first ~2 sentences of free-text body, skipping markdown
    chrome (headings, code fences, link-only lines)."""
    lines = []
    in_code = False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not s:
            if lines:
                break
            continue
        if s.startswith("#") or s.startswith("---"):
            continue
        lines.append(s)
        if sum(l.count(".") for l in lines) >= 2:
            break
    txt = " ".join(lines)
    # Cut after second sentence
    m = re.match(r"^(.+?\.\s+.+?\.)(?=\s|$)", txt)
    return (m.group(1) if m else txt[:300]).strip()


@dataclass
class Clipping:
    path: Path
    source: str
    producer_slug: str
    critic: str
    url: str
    published: str
    title: str
    excerpt: str


def load_clippings(source: str) -> list[Clipping]:
    src_dir = CLIPPINGS / source
    if not src_dir.is_dir():
        return []
    out: list[Clipping] = []
    for p in sorted(src_dir.glob("*.md")):
        if p.name.startswith("_") or p.name == "README.md":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_fm(text)
        if not parts:
            print(f"  skip (no frontmatter): {p.name}", file=sys.stderr)
            continue
        fm, body = parts
        slug = fm_get(fm, "producer_slug")
        if not slug:
            # Try to infer from filename: `<date>__<slug>__<title>.md`
            m = re.match(r"^\d{4}-\d{2}-\d{2}__([a-z0-9_]+)__", p.stem)
            if m:
                slug = m.group(1)
        # Title: from H1 in body, else from filename tail
        title_m = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else p.stem
        out.append(Clipping(
            path=p,
            source=source,
            producer_slug=slug,
            critic=fm_get(fm, "critic") or SOURCES[source]["default_critic"],
            url=fm_get(fm, "url"),
            published=fm_get(fm, "published"),
            title=title,
            excerpt=first_two_sentences(body),
        ))
    return out


def render_section(source: str, clippings: list[Clipping]) -> str:
    """Build the `## <Source> Reviews` section body."""
    header = SOURCES[source]["section_header"]
    lines = [header, ""]
    # Group by clipping, newest first
    clippings = sorted(clippings,
                       key=lambda c: c.published or "0000-00-00",
                       reverse=True)
    for c in clippings:
        link = f"[{c.title}]({c.url})" if c.url else c.title
        date = c.published or "undated"
        lines.append(f"### {link}")
        lines.append(f"*{date}* — {c.critic}")
        lines.append("")
        if c.excerpt:
            lines.append(f"> {c.excerpt}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


SECTION_END_RE_TEMPLATE = (
    r"({header}\n.*?)(?=^## |\Z)"
)
INSERT_BEFORE = ("## Cross-references", "## Notes", "## Cellar",
                 "## Down to Earth Wines (Panzer)", "## Raeder's", "## FASS")


def write_section(producer_path: Path, source: str, section_body: str) -> bool:
    """Write/replace the section on the producer page. Returns True if
    the file was changed."""
    if not producer_path.exists():
        return False
    text = producer_path.read_text(encoding="utf-8")
    header = SOURCES[source]["section_header"]
    section_re = re.compile(
        SECTION_END_RE_TEMPLATE.format(header=re.escape(header)),
        re.DOTALL | re.MULTILINE,
    )
    if section_re.search(text):
        new_text = section_re.sub(section_body + "\n", text)
    else:
        # Insert before the first known anchor section
        insert_pat = None
        for anchor in INSERT_BEFORE:
            pat = re.compile(rf"^{re.escape(anchor)}\b", re.MULTILINE)
            m = pat.search(text)
            if m:
                insert_pat = m
                break
        if insert_pat:
            new_text = (text[:insert_pat.start()]
                        + section_body + "\n"
                        + text[insert_pat.start():])
        else:
            # Append to end
            new_text = text.rstrip() + "\n\n" + section_body + "\n"
    if new_text == text:
        return False
    producer_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=list(SOURCES) + ["all"],
                    help="Which clipping source to compile.")
    ap.add_argument("--apply", action="store_true",
                    help="Write changes. Default is dry-run.")
    args = ap.parse_args()

    sources = list(SOURCES) if args.source == "all" else [args.source]
    all_clippings: list[Clipping] = []
    for src in sources:
        all_clippings.extend(load_clippings(src))

    # Group by (source, producer_slug)
    by_target: dict[tuple[str, str], list[Clipping]] = defaultdict(list)
    unmatched: list[Clipping] = []
    for c in all_clippings:
        if not c.producer_slug:
            unmatched.append(c)
            continue
        target = PRODUCERS / f"{c.producer_slug}.md"
        if not target.exists():
            unmatched.append(c)
            continue
        by_target[(c.source, c.producer_slug)].append(c)

    written = 0
    for (src, slug), clippings in by_target.items():
        body = render_section(src, clippings)
        target = PRODUCERS / f"{slug}.md"
        if args.apply:
            if write_section(target, src, body):
                written += 1
        else:
            written += 1  # would write

    # Report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "type: clippings_report",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"sources: {sources}",
        f"clippings_total: {len(all_clippings)}",
        f"matched: {sum(len(v) for v in by_target.values())}",
        f"unmatched: {len(unmatched)}",
        f"producers_touched: {len(by_target)}",
        f"apply_mode: {args.apply}",
        "---",
        "",
        "# Clippings compile report",
        "",
    ]
    if unmatched:
        lines += [
            f"## Unmatched ({len(unmatched)})",
            "",
            "Add a `producer_slug:` to the clipping frontmatter, create the producer page, or update `aliases:` on an existing producer.",
            "",
        ]
        for c in unmatched[:50]:
            slug_note = f"slug='{c.producer_slug}'" if c.producer_slug else "no slug"
            lines.append(f"- `{c.path.name}` — {slug_note} ({c.source})")
        if len(unmatched) > 50:
            lines.append(f"- _… and {len(unmatched) - 50} more_")
        lines.append("")
    if by_target:
        lines += [
            f"## Producers touched ({len(by_target)})",
            "",
        ]
        for (src, slug), cs in sorted(by_target.items()):
            lines.append(f"- `{slug}` ({src}, {len(cs)} clipping(s))")
        lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n=== {mode} ===")
    print(f"  clippings:         {len(all_clippings)}")
    print(f"  producers touched: {len(by_target)}")
    print(f"  unmatched:         {len(unmatched)}")
    print(f"  report:            {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
