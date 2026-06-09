"""
link_cellar.py — connect cellar/*.md and wiki/producers/*.md into one graph.

Three idempotent passes:

  1. Slug repair. CellarTracker producer names slugify differently than the
     wiki slugs (e.g. "Anne et Jean-François Ganevat" → wiki page
     jean_francois_ganevat). SLUG_OVERRIDES below is the curated decision
     table (verified by hand 2026-06-09, see wiki/log.md). Rewrites
     `producer_slug:` in cellar frontmatter and renames the cellar file to
     keep the {vintage}_{producer_slug}_{cuvee} convention.

  2. Cellar → producer wikilink. Rewrites the `- **Producer:** Name` body
     line to `- **Producer:** [[slug|Name]]` when the producer page exists.
     Producers without a wiki page stay plain text (no broken links).

  3. Producer → cellar wikilinks. Regenerates the `## Cellar` section on
     every producer page that has cellar entries, with each bottle line
     wikilinked to its cellar/*.md file. Section content is derived from
     cellar/*.md (canonical for owned bottles), NOT from My Cellar.csv.

Run after `ingest_cellar.py` (which regenerates cellar files from the CT
export and would drop the body wikilinks).
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
CELLAR = VAULT / "cellar"
PRODUCERS = VAULT / "wiki" / "producers"

# Curated mapping: CellarTracker-derived slug → canonical wiki slug.
# Verified one-by-one against producer page name/region (2026-06-09).
# Fuzzy candidates that were REJECTED as different producers:
#   vincent (Oregon) ≠ vincent_paris (Rhône)
#   our_wines (Oregon) ≠ zorzal_wines (Argentina)
#   chateau_guiraud, domaine_chapel, domaine_des_croix, domaine_diochon,
#   domaine_rougeot, domaine_berlancourt, domaine_de_la_terre_rouge —
#   no wiki page yet (see build/cellar_link_report.md).
SLUG_OVERRIDES: dict[str, str] = {
    "anne_et_jean_francois_ganevat": "jean_francois_ganevat",
    "arnot_roberts": "arnot-roberts",
    "christophe_billon": "billon",
    "comm_g_b_burlotto": "burlotto",
    "daniel_julien_barraud": "barraud",
    "enderle_moll": "enderle__moll",
    "guilhem_et_jean_hugues_goisot": "goisot",
    "hundred_acre_vineyard": "hundred_acre",
    "patrick_jasmin": "jasmin",
    "peter_lauer": "peter_lauer__weingut_lauer",
    "stein": "ulli_stein",
    "weingut_gunther_steinmetz": "steinmetz",
    "weingut_knebel": "knebel",
}

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
SLUG_LINE_RE = re.compile(r"^producer_slug:\s*(\S+)\s*$", re.MULTILINE)
PRODUCER_LINE_RE = re.compile(r"^- \*\*Producer:\*\* (?!\[\[)(.+)$", re.MULTILINE)
CELLAR_SECTION_RE = re.compile(r"## Cellar\n.*?(?=\n## [^#]|\Z)", re.DOTALL)


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


@dataclass
class Entry:
    stem: str
    slug: str
    producer: str
    cuvee: str
    vintage: str
    size: str
    qty: int
    price: float
    drink_start: str
    drink_end: str


def pass1_fix_slugs() -> int:
    renamed = 0
    for p in sorted(CELLAR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        m = SLUG_LINE_RE.search(text)
        if not m:
            continue
        old = m.group(1)
        new = SLUG_OVERRIDES.get(old)
        if not new:
            continue
        text = SLUG_LINE_RE.sub(f"producer_slug: {new}", text, count=1)
        new_name = p.name.replace(f"_{old}_", f"_{new}_", 1)
        target = p.with_name(new_name)
        p.write_text(text, encoding="utf-8")
        if new_name != p.name:
            if target.exists():
                print(f"WARN: rename target exists, keeping {p.name}", file=sys.stderr)
            else:
                p.rename(target)
        renamed += 1
        print(f"  slug: {old} → {new}  ({new_name})")
    return renamed


def pass2_link_cellar_bodies(producer_slugs: set[str]) -> int:
    linked = 0
    for p in sorted(CELLAR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        parts = FM_RE.match(text)
        if not parts:
            continue
        slug = get_str(parts.group(1), "producer_slug")
        if slug not in producer_slugs:
            continue
        new_text, n = PRODUCER_LINE_RE.subn(
            lambda m: f"- **Producer:** [[{slug}|{m.group(1).strip()}]]",
            text, count=1)
        if n:
            p.write_text(new_text, encoding="utf-8")
            linked += 1
    return linked


def load_entries() -> dict[str, list[Entry]]:
    by_slug: dict[str, list[Entry]] = defaultdict(list)
    for p in sorted(CELLAR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        parts = FM_RE.match(text)
        if not parts:
            continue
        fm = parts.group(1)
        if get_str(fm, "type") != "cellar_entry":
            continue
        slug = get_str(fm, "producer_slug")
        if not slug:
            continue
        try:
            qty = int(get_str(fm, "quantity"))
        except ValueError:
            qty = 0
        try:
            price = float(get_str(fm, "purchase_price_usd"))
        except ValueError:
            price = 0.0
        by_slug[slug].append(Entry(
            stem=p.stem,
            slug=slug,
            producer=get_str(fm, "producer"),
            cuvee=get_str(fm, "cuvee"),
            vintage=get_str(fm, "vintage"),
            size=get_str(fm, "bottle_size"),
            qty=qty,
            price=price,
            drink_start=get_str(fm, "drink_window_start"),
            drink_end=get_str(fm, "drink_window_end"),
        ))
    return by_slug


def build_cellar_section(entries: list[Entry]) -> str:
    lines = ["## Cellar", ""]
    total_q = sum(e.qty for e in entries)
    lines.append(f"Own **{total_q} bottle(s)** across {len(entries)} cuvée-vintage(s):")
    lines.append("")
    for e in sorted(entries, key=lambda x: (x.vintage, x.cuvee)):
        window = ""
        ds = e.drink_start if e.drink_start not in ("", "null") else ""
        de = e.drink_end if e.drink_end not in ("", "null") else ""
        if ds or de:
            window = f" — drink {ds or '?'}–{de or '?'}"
        price = f" @ ${e.price:g}" if e.price else ""
        label = f"{e.cuvee} {e.vintage}".replace("|", "/").replace("]", ")")
        lines.append(
            f"- {e.qty} × [[{e.stem}|{label}]]"
            f" ({e.size}){price}{window}"
        )
    lines.append("")
    return "\n".join(lines)


def pass3_producer_sections(by_slug: dict[str, list[Entry]]) -> int:
    updated = 0
    for slug, entries in sorted(by_slug.items()):
        path = PRODUCERS / f"{slug}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        new_section = build_cellar_section(entries)
        if CELLAR_SECTION_RE.search(body):
            new_body = CELLAR_SECTION_RE.sub(new_section.rstrip() + "\n", body, count=1)
        elif "## Cross-references" in body:
            new_body = body.replace(
                "## Cross-references",
                new_section.rstrip() + "\n\n## Cross-references", 1)
        else:
            new_body = body.rstrip() + "\n\n" + new_section
        if new_body != body:
            path.write_text(f"---\n{fm}\n---\n{new_body}", encoding="utf-8")
            updated += 1
    return updated


def main() -> int:
    producer_slugs = {p.stem for p in PRODUCERS.glob("*.md")}

    print("Pass 1 — cellar slug repair:")
    fixed = pass1_fix_slugs()
    print(f"  {fixed} cellar files re-slugged")

    linked = pass2_link_cellar_bodies(producer_slugs)
    print(f"Pass 2 — {linked} cellar bodies now wikilink their producer")

    by_slug = load_entries()
    with_page = {s: e for s, e in by_slug.items() if s in producer_slugs}
    updated = pass3_producer_sections(with_page)
    missing = sorted(set(by_slug) - producer_slugs)
    print(f"Pass 3 — {updated} producer pages got a refreshed ## Cellar section")
    print(f"Cellar producers still without a wiki page: {len(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
