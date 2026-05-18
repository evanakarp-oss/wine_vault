"""
Compile rollup index pages from wiki/producers/*.md frontmatter.

Outputs:
  wiki/regions/<Region>_Producers.md    — one per top-level region, grouped
                                           table with retailer coverage.
  wiki/importers/<Name>.md               — one per US importer_us entry,
                                           listing producers they bring in.
  wiki/retailers/<Name>.md               — one per retailer (chambers/dte/
                                           raeders/fass), with leaderboard.

Cellar counts are joined in from cellar/*.md (producer_slug + quantity).

All outputs are regenerable — overwrite on each run.
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
REGIONS = VAULT / "wiki" / "regions"
IMPORTERS = VAULT / "wiki" / "importers"
RETAILERS = VAULT / "wiki" / "retailers"
CELLAR = VAULT / "cellar"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_int_under(fm: str, block: str, key: str) -> int:
    """Get integer value of `key` inside a 2-space-indented `block:` section."""
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(\d+)"
    m = re.search(pat, fm, re.MULTILINE)
    return int(m.group(1)) if m else 0


def get_bool_under(fm: str, block: str, key: str) -> bool:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(true|false)"
    m = re.search(pat, fm, re.MULTILINE)
    return bool(m) and m.group(1) == "true"


def get_list(fm: str, key: str) -> list[str]:
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


def safe_filename(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s\-&]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "unnamed"


@dataclass
class Producer:
    slug: str
    name: str
    country: str
    region: str
    sub_region: str
    importer_us: list[str]
    # chambers
    champ: bool = False
    ch_articles: int = 0
    ch_dedicated: int = 0
    ch_first: int = 0
    ch_last: int = 0
    # dte / raeders / fass
    dte: bool = False
    dte_cuvees: int = 0
    dte_price_max: int = 0
    raeders: bool = False
    raeders_cuvees: int = 0
    fass: bool = False
    fass_cuvees: int = 0
    # cellar (joined later)
    cellar_bottles: int = 0
    cellar_cuvees: int = 0


def load_producers() -> list[Producer]:
    out = []
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, _ = parts
        if get_str(fm, "type") != "producer":
            continue
        pr = Producer(
            slug=get_str(fm, "slug") or p.stem,
            name=get_str(fm, "name"),
            country=get_str(fm, "country"),
            region=get_str(fm, "region"),
            sub_region=get_str(fm, "sub_region"),
            importer_us=get_list(fm, "importer_us"),
            champ=get_bool_under(fm, "chambers", "championed"),
            ch_articles=get_int_under(fm, "chambers", "article_count"),
            ch_dedicated=get_int_under(fm, "chambers", "dedicated_count"),
            ch_first=get_int_under(fm, "chambers", "first_year"),
            ch_last=get_int_under(fm, "chambers", "last_year"),
            dte=get_bool_under(fm, "dte", "in_portfolio"),
            dte_cuvees=get_int_under(fm, "dte", "cuvee_count"),
            dte_price_max=get_int_under(fm, "dte", "price_max"),
            raeders=get_bool_under(fm, "raeders", "in_portfolio"),
            raeders_cuvees=get_int_under(fm, "raeders", "cuvee_count"),
            fass=get_bool_under(fm, "fass", "in_portfolio"),
            fass_cuvees=get_int_under(fm, "fass", "cuvee_count"),
        )
        out.append(pr)
    return out


def join_cellar(producers: list[Producer]) -> None:
    cellar_bottles: dict[str, int] = defaultdict(int)
    cellar_cuvees: dict[str, int] = defaultdict(int)
    for c in CELLAR.glob("*.md"):
        text = c.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, _ = parts
        if get_str(fm, "type") != "cellar_entry":
            continue
        slug = get_str(fm, "producer_slug")
        if not slug:
            continue
        m = re.search(r"^quantity:\s*(\d+)", fm, re.MULTILINE)
        q = int(m.group(1)) if m else 0
        cellar_bottles[slug] += q
        cellar_cuvees[slug] += 1
    for p in producers:
        p.cellar_bottles = cellar_bottles.get(p.slug, 0)
        p.cellar_cuvees = cellar_cuvees.get(p.slug, 0)


# --- region rollup ---

def yn(flag: bool) -> str:
    return "✓" if flag else "—"


def region_table_row(p: Producer) -> str:
    ch = str(p.ch_articles) if p.ch_articles else "—"
    dte = f"{p.dte_cuvees}" if p.dte else "—"
    rae = f"{p.raeders_cuvees}" if p.raeders else "—"
    fass = f"{p.fass_cuvees}" if p.fass else "—"
    cel = f"{p.cellar_bottles} btl" if p.cellar_bottles else "—"
    title_slug = p.slug  # Obsidian wikilink stem
    display = p.name or p.slug
    return (
        f"| [[{title_slug}|{display}]] | {p.country or '—'} | "
        f"{p.sub_region or '—'} | {ch} | {dte} | {rae} | {fass} | {cel} |"
    )


def build_region_pages(producers: list[Producer]) -> int:
    REGIONS.mkdir(parents=True, exist_ok=True)
    by_region: dict[str, list[Producer]] = defaultdict(list)
    for p in producers:
        key = p.region or "Unknown"
        by_region[key].append(p)

    today = date.today().isoformat()
    written = 0
    for region, plist in sorted(by_region.items()):
        plist.sort(key=lambda x: (-(x.ch_articles + x.cellar_bottles), x.name.lower()))
        safe = safe_filename(region)
        path = REGIONS / f"{safe}_Producers.md"
        lines = [
            "---",
            "type: region_index",
            f'region: "{region}"',
            f"updated: {today}",
            f"producer_count: {len(plist)}",
            "---",
            "",
            f"# {region} — Producer Index",
            "",
            f"**{len(plist)} producers** tracked.",
            "",
            "| Producer | Country | Sub-region | CSW | DTE | Raeder's | FASS | Cellar |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for p in plist:
            lines.append(region_table_row(p))
        lines += ["", "*Compiled by `scripts/build_rollups.py` from `wiki/producers/*.md`.*"]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    return written


# --- importer rollup ---

def build_importer_pages(producers: list[Producer]) -> int:
    IMPORTERS.mkdir(parents=True, exist_ok=True)
    by_importer: dict[str, list[Producer]] = defaultdict(list)
    for p in producers:
        for imp in p.importer_us or []:
            by_importer[imp].append(p)

    today = date.today().isoformat()
    written = 0
    for imp, plist in sorted(by_importer.items()):
        if not imp.strip():
            continue
        plist.sort(key=lambda x: (-x.ch_articles, x.name.lower()))
        safe = safe_filename(imp)
        path = IMPORTERS / f"{safe}.md"
        focus_regions = sorted({p.region for p in plist if p.region})
        top_producers = [p.name for p in plist[:8] if p.name]
        lines = [
            "---",
            "type: importer",
            f'name: "{imp}"',
            f"slug: {safe.lower()}",
            f"producer_count: {len(plist)}",
            f"focus: {focus_regions}",
            f"notable_producers: {top_producers[:5]}",
            f"updated: {today}",
            "---",
            "",
            f"# {imp}",
            "",
            f"**{len(plist)} producer(s)** in the vault imported by {imp} (US).",
            "",
            "| Producer | Country | Region | CSW | Cellar |",
            "|---|---|---|---:|---:|",
        ]
        for p in plist:
            ch = str(p.ch_articles) if p.ch_articles else "—"
            cel = f"{p.cellar_bottles}" if p.cellar_bottles else "—"
            lines.append(
                f"| [[{p.slug}|{p.name}]] | {p.country or '—'} | "
                f"{p.region or '—'} | {ch} | {cel} |"
            )
        lines += ["", "*Compiled by `scripts/build_rollups.py`.*"]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    return written


# --- retailer rollup ---

RETAILER_META = {
    "chambers": {
        "display": "Chambers Street Wines",
        "url": "https://chambersstwines.com",
        "location": "NYC",
    },
    "dte": {
        "display": "Down to Earth Wines (Panzer)",
        "url": "",
        "location": "NYC (import portfolio)",
    },
    "raeders": {
        "display": "Raeder's",
        "url": "",
        "location": "",
    },
    "fass": {
        "display": "FASS Selections",
        "url": "",
        "location": "",
    },
}


def build_retailer_pages(producers: list[Producer]) -> int:
    RETAILERS.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    def producers_for(key: str) -> list[Producer]:
        if key == "chambers":
            return [p for p in producers if p.ch_articles > 0]
        if key == "dte":
            return [p for p in producers if p.dte]
        if key == "raeders":
            return [p for p in producers if p.raeders]
        if key == "fass":
            return [p for p in producers if p.fass]
        return []

    written = 0
    for key, meta in RETAILER_META.items():
        plist = producers_for(key)
        if key == "chambers":
            plist.sort(key=lambda x: (-x.ch_dedicated, -x.ch_articles))
        else:
            metric = {
                "dte": lambda x: x.dte_cuvees,
                "raeders": lambda x: x.raeders_cuvees,
                "fass": lambda x: x.fass_cuvees,
            }[key]
            plist.sort(key=lambda x, m=metric: (-m(x), x.name.lower()))
        path = RETAILERS / f"{safe_filename(meta['display'])}.md"
        lines = [
            "---",
            "type: retailer",
            f'name: "{meta["display"]}"',
            f"slug: {key}",
            f'url: "{meta["url"]}"',
            f'location: "{meta["location"]}"',
            f"producer_count: {len(plist)}",
            f"updated: {today}",
            "---",
            "",
            f"# {meta['display']}",
            "",
            f"**{len(plist)} producers** from this retailer are tracked in the wiki.",
            "",
        ]
        if key == "chambers":
            lines += [
                "## Most-championed producers",
                "",
                "| Producer | ★ Dedicated | Total articles | First | Last |",
                "|---|---:|---:|---:|---:|",
            ]
            for p in plist[:50]:
                lines.append(
                    f"| [[{p.slug}|{p.name}]] | {p.ch_dedicated} | "
                    f"{p.ch_articles} | {p.ch_first or '—'} | {p.ch_last or '—'} |"
                )
        else:
            cuvee_getter = {
                "dte": lambda x: x.dte_cuvees,
                "raeders": lambda x: x.raeders_cuvees,
                "fass": lambda x: x.fass_cuvees,
            }[key]
            lines += [
                "## Producers in portfolio",
                "",
                "| Producer | Country | Region | Cuvées | CSW articles |",
                "|---|---|---|---:|---:|",
            ]
            for p in plist:
                lines.append(
                    f"| [[{p.slug}|{p.name}]] | {p.country or '—'} | "
                    f"{p.region or '—'} | {cuvee_getter(p)} | {p.ch_articles or '—'} |"
                )
        lines += ["", "*Compiled by `scripts/build_rollups.py`.*"]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += 1
    return written


def main() -> int:
    print("Loading producers...")
    producers = load_producers()
    print(f"  {len(producers)} producer pages")
    print("Joining cellar counts...")
    join_cellar(producers)
    owned = sum(1 for p in producers if p.cellar_bottles > 0)
    print(f"  {owned} producers with cellar bottles")

    r_count = build_region_pages(producers)
    i_count = build_importer_pages(producers)
    s_count = build_retailer_pages(producers)
    print(f"Wrote {r_count} region pages, {i_count} importer pages, {s_count} retailer pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
