"""
Parse arg-natural-wine_3.jsx (Argentine natural-wine producers championed by
Paz Levinson via the Argentina Reloaded series) and fold it into wiki/producers/.

The JSX file encodes producers as a JS array of object literals:
    const producers = [
      {
        name: "Finca Suarez",
        winemaker: "Juanfa Suárez",
        region: "Paraje Altamira",
        province: "Mendoza",
        category: "Radical Natural",
        grapes: [...],
        approach: "...",
        keyWines: [...],
        source: "...",
        reloaded: ["Rio 2024","Buenos Aires 2025"]
      },
      ...
    ];

For each producer:
  - province → wiki frontmatter `region` (matches taxonomy: Mendoza, Patagonia, etc.)
  - JSX `region` → wiki `sub_region`
  - category → farming + tags hybrid (see CATEGORY_MAP)
  - reloaded[] → events[] frontmatter slugs
  - approach + keyWines + source → body sections

Idempotence: if a producer file already has `_sources` containing this jsx,
re-emit from scratch (we own the file). Otherwise, abort and warn — to avoid
clobbering hand-written content from another source.

Report: build/arg_jsx_ingest_report.md.

No external deps — JSX is parsed via stripped-comments + bare-key quoting +
trailing-comma cleanup, then json.loads().
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
JSX_PATH = VAULT / "raw" / "argentina_reloaded" / "source" / "arg-natural-wine_3.jsx"
WIKI_DIR = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "arg_jsx_ingest_report.md"
SOURCE_TAG = f"arg_jsx:{JSX_PATH.name}"

CATEGORY_MAP: dict[str, dict[str, list[str]]] = {
    "Radical Natural":             {"farming": ["natural"],              "tags": ["radical-natural"]},
    "Low Intervention":            {"farming": [],                       "tags": ["low-intervention"]},
    "Certified Organic + Natural": {"farming": ["organic", "natural"],   "tags": ["organic"]},
    "Biodynamic":                  {"farming": ["biodynamic"],           "tags": ["biodynamic"]},
    "Artisan / Terroir-Driven":    {"farming": [],                       "tags": ["artisan-terroir"]},
    "Emerging":                    {"farming": [],                       "tags": ["emerging", "low-intervention"]},
}

EVENT_MAP: dict[str, str] = {
    "Rio 2024":          "argentina_reloaded_rio_2024",
    "Buenos Aires 2025": "argentina_reloaded_buenos_aires_2025",
    "London 2022":       "argentina_reloaded_london_2022",
}

ALLOWED_PROVINCES = {"Mendoza", "Patagonia", "Salta", "Jujuy", "San Juan", "Buenos Aires Province"}


def ascii_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def strip_js_comments(text: str) -> str:
    """Remove `// ...` line comments while preserving content inside double-quoted strings."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


KEY_RE = re.compile(r'([\{,]\s*)([A-Za-z_]\w*)(\s*:)')
TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")


def jsx_array_to_python(jsx_text: str) -> list[dict]:
    """Extract the `const producers = [...]` array and parse it."""
    m = re.search(r"const\s+producers\s*=\s*(\[.*?\])\s*;", jsx_text, re.DOTALL)
    if not m:
        raise ValueError("`const producers = [...]` not found in JSX")
    body = m.group(1)
    body = strip_js_comments(body)
    body = KEY_RE.sub(r'\1"\2"\3', body)
    body = TRAILING_COMMA_RE.sub(r"\1", body)
    return json.loads(body)


@dataclass
class Producer:
    name: str
    slug: str
    winemaker: str
    province: str
    sub_region: str
    category: str
    grapes: list[str]
    approach: str
    key_wines: list[str]
    source: str
    events: list[str]


def normalize(p: dict) -> Producer:
    name = p["name"].strip()
    slug = ascii_slug(name)
    province = p["province"].strip()
    if province not in ALLOWED_PROVINCES:
        # Patagonia is in JSX for some producers actually located in Buenos Aires Province
        # (e.g. Puerta del Abra at Balcarce). Lint pass will flag.
        pass
    events = [EVENT_MAP[r] for r in p.get("reloaded", []) if r in EVENT_MAP]
    return Producer(
        name=name,
        slug=slug,
        winemaker=p.get("winemaker", "").strip(),
        province=province,
        sub_region=p.get("region", "").strip(),
        category=p.get("category", "").strip(),
        grapes=[g.strip() for g in p.get("grapes", []) if g.strip()],
        approach=p.get("approach", "").strip(),
        key_wines=[w.strip() for w in p.get("keyWines", []) if w.strip()],
        source=p.get("source", "").strip(),
        events=events,
    )


def yaml_str_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def render_producer_md(p: Producer) -> str:
    cat_map = CATEGORY_MAP.get(p.category, {"farming": [], "tags": []})
    farming = cat_map["farming"]
    tags = list(cat_map["tags"])

    region_tag = ascii_slug(p.province).replace("_", "-")
    if region_tag and region_tag not in tags:
        tags.append(region_tag)
    tags.append("argentina")

    lines: list[str] = [
        "---",
        "type: producer",
        f'name: "{p.name}"',
        f"slug: {p.slug}",
        "aliases: []",
        'country: "Argentina"',
        f'region: "{p.province}"',
        f'sub_region: "{p.sub_region}"',
        "appellations: []",
        f"farming: {yaml_str_list(farming)}",
        "certifications: []",
        "importer_us: []",
        "retailers:",
        "  chambers:",
        "    championed: false",
        "    article_count: 0",
        "    dedicated_count: 0",
        "    first_year: 0",
        "    last_year: 0",
        "  dte:",
        "    in_portfolio: false",
        "  raeders:",
        "    in_portfolio: false",
        "  fass:",
        "    in_portfolio: false",
        f"events: {yaml_str_list(p.events)}",
        f"tags: {yaml_str_list(tags)}",
        f'_sources: ["{SOURCE_TAG}"]',
        "---",
        "",
        f"# {p.name}",
        "",
    ]

    summary_bits = []
    if p.winemaker:
        summary_bits.append(f"Winemaker: **{p.winemaker}**.")
    if p.sub_region:
        summary_bits.append(f"{p.sub_region} ({p.province}).")
    elif p.province:
        summary_bits.append(f"{p.province}.")
    if p.category:
        summary_bits.append(f"Category: **{p.category}**.")
    if summary_bits:
        lines.append(" ".join(summary_bits))
        lines.append("")

    if p.approach:
        lines.extend(["## Approach", "", p.approach, ""])

    if p.grapes:
        lines.extend(["## Grapes", "", ", ".join(p.grapes), ""])

    if p.key_wines:
        lines.extend(["## Key Wines", ""])
        for w in p.key_wines:
            lines.append(f"- {w}")
        lines.append("")

    if p.events:
        lines.extend(["## Argentina Reloaded", ""])
        labels = {v: k for k, v in EVENT_MAP.items()}
        for ev in p.events:
            label = labels.get(ev, ev)
            lines.append(f"- ✦ [[Argentina_Reloaded_{label.replace(' ', '_')}|{label}]]")
        lines.append("")

    if p.source:
        lines.extend(["## Source", "", p.source, ""])

    lines.extend([
        "## Cross-references",
        "",
        f"- [[{p.province.replace(' ', '_')}_Producers|{p.province}]]",
        "- [[Argentina_Producers|Argentina]]",
        "",
    ])

    return "\n".join(lines).rstrip() + "\n"


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def is_owned_by_arg_jsx(path: Path) -> bool:
    """Return True if the file's _sources includes this JSX (i.e. we wrote it)."""
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(txt)
    if not m:
        return False
    return SOURCE_TAG in m.group(1)


def main() -> int:
    if not JSX_PATH.exists():
        print(f"JSX not found: {JSX_PATH}", file=sys.stderr)
        return 1
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    jsx_text = JSX_PATH.read_text(encoding="utf-8")
    raw_producers = jsx_array_to_python(jsx_text)
    print(f"Parsed {len(raw_producers)} producers from {JSX_PATH.name}")

    producers = [normalize(p) for p in raw_producers]

    seen_slugs: dict[str, str] = {}
    duplicates: list[tuple[str, str, str]] = []
    for p in producers:
        if p.slug in seen_slugs and seen_slugs[p.slug] != p.name:
            duplicates.append((p.slug, seen_slugs[p.slug], p.name))
        seen_slugs[p.slug] = p.name

    created: list[str] = []
    updated: list[str] = []
    skipped_collision: list[tuple[str, str]] = []

    for p in producers:
        path = WIKI_DIR / f"{p.slug}.md"
        if path.exists() and not is_owned_by_arg_jsx(path):
            skipped_collision.append((p.slug, p.name))
            continue
        action = "updated" if path.exists() else "created"
        path.write_text(render_producer_md(p), encoding="utf-8")
        (updated if action == "updated" else created).append(p.slug)

    bad_provinces = [(p.slug, p.province) for p in producers if p.province not in ALLOWED_PROVINCES]

    report = [
        "---",
        "type: ingest_report",
        "source: arg_jsx",
        f'generated: "{datetime.now().isoformat(timespec="seconds")}"',
        f"total_producers: {len(producers)}",
        f"created: {len(created)}",
        f"updated: {len(updated)}",
        f"skipped_collision: {len(skipped_collision)}",
        f"province_warnings: {len(bad_provinces)}",
        f"duplicate_slugs: {len(duplicates)}",
        "---",
        "",
        "# Argentina Reloaded JSX ingest",
        "",
        f"Source: `{JSX_PATH.relative_to(VAULT)}`",
        "",
        f"## Created ({len(created)})",
        "",
    ]
    for s in sorted(created):
        report.append(f"- `{s}.md`")
    report.append("")
    report.append(f"## Updated ({len(updated)})")
    report.append("")
    for s in sorted(updated):
        report.append(f"- `{s}.md`")
    if skipped_collision:
        report.append("")
        report.append(f"## Skipped — pre-existing file not owned by this ingest ({len(skipped_collision)})")
        report.append("")
        for slug, name in skipped_collision:
            report.append(f"- `{slug}.md` — **{name}** (manual merge needed)")
    if bad_provinces:
        report.append("")
        report.append(f"## Province warnings ({len(bad_provinces)})")
        report.append("")
        for slug, prov in bad_provinces:
            report.append(f"- `{slug}` — province `{prov}` not in taxonomy")
    if duplicates:
        report.append("")
        report.append(f"## Duplicate slugs ({len(duplicates)})")
        report.append("")
        for slug, first, second in duplicates:
            report.append(f"- `{slug}` collides between `{first}` and `{second}`")

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"OK: {len(created)} created, {len(updated)} updated, "
          f"{len(skipped_collision)} skipped, {len(bad_provinces)} province warnings")
    print(f"Report: {REPORT.relative_to(VAULT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
