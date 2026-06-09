#!/usr/bin/env python3
"""
build_wiki_index.py — generate wiki/index.md from the wine_vault wiki.

Implements the "indexing" pattern from the Karpathy LLM-wiki gist:
a single content-oriented catalog of every page in `wiki/` and `cellar/`,
grouped by type, so the LLM (or you) can find candidate pages in one read
before drilling into them.

Idempotent. Pure stdlib + PyYAML. Tolerant of malformed YAML, missing
keys, and Drive-sync artifacts (legacy `wiki/wiki/` nesting, `.obsidian/`,
etc.).

Usage:
    python scripts/build_wiki_index.py
    python scripts/build_wiki_index.py --check   # exit 1 if regen differs
    python scripts/build_wiki_index.py --vault-root /path/to/wine_vault
    python scripts/build_wiki_index.py --output /tmp/index.md --quiet

Requires: PyYAML.
    pip install pyyaml --break-system-packages
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. pip install pyyaml --break-system-packages")


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

# Directories never indexed even if they live under wiki/ or cellar/.
# 'wiki' is here to catch the legacy nested wiki/wiki/ from the
# 2026-05-08 ingest divergence; the depth-0 special-case in is_skipped()
# keeps the canonical wiki/ folder itself walkable.
SKIP_DIRS = {
    ".obsidian", ".git", "_drive_sync", "build", "wiki",
}
SKIP_FILES = {"My Cellar.csv", "index.md", "log.md", "HOME.md"}

SECTION_ORDER = (
    "Schema & taxonomy",
    "Views & analyses",
    "Region rollups",
    "Importers",
    "Retailers",
    "Producers",
    "Events",
    "Cellar bottles",
    "Other",
)


@dataclass
class Page:
    path: Path                              # absolute path on disk
    rel: str                                # path relative to vault, POSIX
    slug: str                               # filename stem (wikilink target)
    type_: str                              # frontmatter['type'] or 'unknown'
    name: str                               # display name
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split markdown into (frontmatter_dict, body). Tolerate malformed YAML."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(fm, dict):
        return {}, text
    return fm, m.group(2)


def is_skipped(path: Path, vault_root: Path, extra_excludes: set[Path] = frozenset()) -> bool:
    """True if the path lives inside a skipped directory, is a skip-list
    filename, or matches an extra exclusion (e.g. the script's own
    output path — without this, regenerating index.md would re-index
    itself and break idempotency)."""
    if path in extra_excludes:
        return True
    if path.name in SKIP_FILES:
        return True
    try:
        parts = path.relative_to(vault_root).parts
    except ValueError:
        return False
    for i, part in enumerate(parts[:-1]):  # only check directory components
        # Allow the canonical top-level 'wiki' directory at depth 0;
        # skip nested 'wiki' (legacy sync artifact) anywhere else.
        if part == "wiki" and i == 0:
            continue
        if part in SKIP_DIRS:
            return True
    return False


def _as_str(v: Any, default: str = "") -> str:
    return v if isinstance(v, str) else default


def _as_list(v: Any) -> list:
    return v if isinstance(v, list) else []


def _as_dict(v: Any) -> dict:
    return v if isinstance(v, dict) else {}


def pretty_stem(stem: str) -> str:
    return stem.replace("_", " ").strip().title() or stem


def collect(root: Path, vault_root: Path, extra_excludes: set[Path] = frozenset()) -> list[Page]:
    if not root.is_dir():
        return []
    pages: list[Page] = []
    for p in sorted(root.rglob("*.md")):
        if is_skipped(p, vault_root, extra_excludes):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            print(f"WARN: unreadable {p}: {exc}", file=sys.stderr)
            continue
        fm, body = parse_frontmatter(text)
        pages.append(Page(
            path=p,
            rel=p.relative_to(vault_root).as_posix(),
            slug=p.stem,
            type_=_as_str(fm.get("type"), "unknown") or "unknown",
            name=_as_str(fm.get("name")) or pretty_stem(p.stem),
            frontmatter=fm,
            body=body,
        ))
    return pages


def first_paragraph(body: str, limit: int = 140) -> str:
    """First non-empty non-heading paragraph, collapsed and truncated."""
    for chunk in re.split(r"\n\s*\n", body.strip(), maxsplit=6):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("#") or chunk.startswith("---"):
            continue
        chunk = re.sub(r"\s+", " ", chunk)
        return chunk[:limit].rstrip() + ("…" if len(chunk) > limit else "")
    return ""


def producer_retailer_flags(fm: dict[str, Any]) -> str:
    flags: list[str] = []
    rmap = _as_dict(fm.get("retailers"))
    chambers = _as_dict(rmap.get("chambers"))
    if chambers.get("championed"):
        n = chambers.get("article_count") or chambers.get("dedicated_count") or 0
        if chambers.get("dedicated_count"):
            flags.append(f"CSW ★{chambers.get('dedicated_count')}/{chambers.get('article_count') or n}")
        else:
            flags.append(f"CSW {n}")
    elif chambers.get("article_count"):
        flags.append(f"CSW {chambers['article_count']}")
    for key, label in (("dte", "DTE"), ("raeders", "Raeder"), ("fass", "FASS")):
        block = _as_dict(rmap.get(key))
        if block.get("in_portfolio"):
            cnt = block.get("cuvee_count")
            flags.append(f"{label} {cnt}" if isinstance(cnt, int) else label)
    return " · ".join(flags)


def summary_line(page: Page) -> str:
    fm = page.frontmatter
    if page.type_ == "producer":
        region = _as_str(fm.get("region")) or "?"
        sub = _as_str(fm.get("sub_region"))
        place = f"{region} / {sub}" if sub else region
        farming = ", ".join(_as_list(fm.get("farming")))
        bits = [place]
        if farming:
            bits.append(farming)
        flags = producer_retailer_flags(fm)
        if flags:
            bits.append(flags)
        return " · ".join(bits)
    if page.type_ == "region_index":
        region = _as_str(fm.get("region")) or pretty_stem(page.slug)
        return first_paragraph(page.body) or f"Producer rollup for {region}"
    if page.type_ == "importer":
        focus = ", ".join(_as_list(fm.get("focus")))
        return focus or first_paragraph(page.body)
    if page.type_ == "retailer":
        bits = [b for b in (_as_str(fm.get("location")), _as_str(fm.get("url"))) if b]
        return " · ".join(bits) or first_paragraph(page.body)
    if "/_views/" in page.rel:
        updated = _as_str(fm.get("updated")) or str(fm.get("updated") or "")
        desc = first_paragraph(page.body)
        return f"updated {updated} · {desc}" if updated else desc
    if page.type_ == "cellar_entry":
        cuv = _as_str(fm.get("cuvee"))
        vin = _as_str(fm.get("vintage"))
        qty = fm.get("quantity")
        bits = [f"{vin} {cuv}".strip()]
        if isinstance(qty, int):
            bits.append(f"{qty} btl")
        return " · ".join(b for b in bits if b)
    return first_paragraph(page.body)


def section_for(page: Page) -> str:
    type_to_section = {
        "producer": "Producers",
        "region_index": "Region rollups",
        "country_index": "Region rollups",
        "importer": "Importers",
        "retailer": "Retailers",
        "schema": "Schema & taxonomy",
        "taxonomy": "Schema & taxonomy",
        "cellar_entry": "Cellar bottles",
        "event": "Events",
    }
    sec = type_to_section.get(page.type_)
    if sec:
        return sec
    # Heuristics for un-typed pages
    if "/_views/" in page.rel:
        return "Views & analyses"
    if page.path.name.startswith("_"):
        return "Schema & taxonomy"
    if "/events/" in page.rel:
        return "Events"
    return "Other"


def wikilink(page: Page) -> str:
    # Slug = link target (Obsidian resolves by filename across vault).
    # `|` and `]` in the display name would terminate the alias / link
    # early; Obsidian doesn't honor backslash escapes inside [[...]],
    # so substitute instead of escape.
    name = page.name.replace("|", "/").replace("]", ")")
    return f"[[{page.slug}|{name}]]"


def count_bottles(pages: Iterable[Page]) -> int:
    n = 0
    for p in pages:
        q = p.frontmatter.get("quantity")
        if isinstance(q, int):
            n += q
    return n


def render(wiki_pages: list[Page], cellar_pages: list[Page]) -> str:
    all_pages = wiki_pages + cellar_pages
    total = len(all_pages)
    producer_slugs = {p.slug for p in wiki_pages if p.type_ == "producer"}

    grouped: dict[str, list[Page]] = {s: [] for s in SECTION_ORDER}
    for p in all_pages:
        grouped.setdefault(section_for(p), []).append(p)

    out: list[str] = []
    out.append("---")
    out.append("type: index")
    out.append(f"total_pages: {total}")
    out.append("generator: scripts/build_wiki_index.py")
    out.append("---")
    out.append("")
    out.append("# Wiki Index")
    out.append("")
    out.append("<!-- Generated by `scripts/build_wiki_index.py`. Do not hand-edit. -->")
    out.append("")
    out.append(
        "Catalog of every page in `wiki/` and `cellar/`, grouped by type. "
        "Per the LLM-wiki pattern, this is the LLM's first read on any query — "
        "find candidate pages here, then drill into them."
    )
    out.append("")
    out.append(f"**{total} pages indexed.**")
    out.append("")

    for section in SECTION_ORDER:
        rows = grouped.get(section) or []
        if not rows:
            continue
        out.append(f"## {section}")
        out.append("")

        if section == "Producers":
            by_region: dict[str, list[Page]] = {}
            for p in rows:
                region = _as_str(p.frontmatter.get("region")) or "Unknown"
                by_region.setdefault(region, []).append(p)
            out.append(f"_{len(rows)} producers across {len(by_region)} regions._")
            out.append("")
            for region in sorted(by_region):
                out.append(f"### {region}")
                out.append("")
                for p in sorted(by_region[region], key=lambda x: x.slug):
                    summ = summary_line(p)
                    out.append(f"- {wikilink(p)} — {summ}" if summ else f"- {wikilink(p)}")
                out.append("")
            continue

        if section == "Cellar bottles":
            bottles = count_bottles(rows)
            by_prod: dict[str, list[Page]] = {}
            for p in rows:
                key = _as_str(p.frontmatter.get("producer_slug")) or "_unknown"
                by_prod.setdefault(key, []).append(p)
            out.append(
                f"_{len(rows)} cuvée-vintage entries · ~{bottles} bottles · "
                f"{len(by_prod)} producers._"
            )
            out.append("")
            for prod in sorted(by_prod):
                entries = sorted(by_prod[prod], key=lambda x: x.slug)
                display = pretty_stem(prod) if prod != "_unknown" else "(unknown producer)"
                preview_bits = []
                for b in entries[:3]:
                    v = _as_str(b.frontmatter.get("vintage"))
                    c = _as_str(b.frontmatter.get("cuvee"))
                    item = f"{v} {c}".strip() or b.slug
                    preview_bits.append(item)
                preview = "; ".join(preview_bits)
                if len(entries) > 3:
                    preview += f"; … +{len(entries) - 3} more"
                # plain text when the producer has no wiki page (no broken links)
                link = f"[[{prod}|{display}]]" if prod in producer_slugs else display
                n = len(entries)
                word = "entry" if n == 1 else "entries"
                out.append(f"- {link} — {n} {word}: {preview}")
            out.append("")
            continue

        for p in sorted(rows, key=lambda x: x.slug):
            summ = summary_line(p)
            out.append(f"- {wikilink(p)} — {summ}" if summ else f"- {wikilink(p)}")
        out.append("")

    out.append("---")
    out.append("_Regenerate: `python scripts/build_wiki_index.py`_")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault-root", type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Root of wine_vault. Defaults to the parent of this script.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Output path. Defaults to <vault>/wiki/index.md",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if regenerated content differs from existing output.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress info logs.")
    args = parser.parse_args()

    vault = args.vault_root.resolve()
    wiki_root = vault / "wiki"
    cellar_root = vault / "cellar"
    if not wiki_root.is_dir():
        sys.exit(f"ERROR: {wiki_root} is not a directory")

    output = args.output.resolve() if args.output else wiki_root / "index.md"
    # Exclude the output file from collection so regenerating doesn't
    # re-index its own previous content (would break idempotency).
    exclude = {output}

    wiki_pages = collect(wiki_root, vault, exclude)
    cellar_pages = collect(cellar_root, vault, exclude)
    if not args.quiet:
        print(
            f"Indexed {len(wiki_pages)} wiki pages + "
            f"{len(cellar_pages)} cellar entries",
            file=sys.stderr,
        )

    rendered = render(wiki_pages, cellar_pages)
    rendered_bytes = rendered.encode("utf-8")

    if args.check:
        existing = output.read_bytes() if output.exists() else b""
        if existing != rendered_bytes:
            print(
                f"DRIFT: {output} would change. "
                f"Run without --check to update.",
                file=sys.stderr,
            )
            return 1
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(rendered_bytes)
    if not args.quiet:
        print(f"Wrote {output} ({len(rendered_bytes)} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
