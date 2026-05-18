"""
Compile event rollup pages from wiki/producers/*.md frontmatter `events: [...]`.

Outputs:
  wiki/events/<Event>.md — one per event slug, listing participating producers.

Event metadata (display name, curator, year, location) lives in EVENT_META below.
Add new events here when adding to wiki/_TAXONOMY.md.

All output is regenerable — overwrites on each run.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
EVENTS = VAULT / "wiki" / "events"

EVENT_META: dict[str, dict[str, str]] = {
    "argentina_reloaded_rio_2024": {
        "display": "Argentina Reloaded — Rio de Janeiro 2024",
        "curator": "Paz Levinson",
        "year": "2024",
        "location": "Rio de Janeiro, Brazil",
        "filename": "Argentina_Reloaded_Rio_2024",
    },
    "argentina_reloaded_buenos_aires_2025": {
        "display": "Argentina Reloaded — Buenos Aires 2025",
        "curator": "Paz Levinson",
        "year": "2025",
        "location": "Buenos Aires, Argentina",
        "filename": "Argentina_Reloaded_Buenos_Aires_2025",
    },
    "argentina_reloaded_london_2022": {
        "display": "Argentina Reloaded — London 2022",
        "curator": "Paz Levinson",
        "year": "2022",
        "location": "London, UK",
        "filename": "Argentina_Reloaded_London_2022",
    },
}

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'', inner):
        v = next((x for x in part if x), "").strip()
        if v:
            out.append(v)
    return out


@dataclass
class ProducerSummary:
    slug: str
    name: str
    province: str
    sub_region: str
    category_tag: str


def category_tag(tags: list[str]) -> str:
    for t in ("radical-natural", "biodynamic", "organic", "low-intervention", "artisan-terroir", "emerging"):
        if t in tags:
            return t
    return ""


def load_producers_with_events() -> dict[str, list[ProducerSummary]]:
    by_event: dict[str, list[ProducerSummary]] = defaultdict(list)
    for path in sorted(PRODUCERS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        if not m:
            continue
        fm = m.group(1)
        if get_str(fm, "type") != "producer":
            continue
        events = get_list(fm, "events")
        if not events:
            continue
        ps = ProducerSummary(
            slug=get_str(fm, "slug") or path.stem,
            name=get_str(fm, "name"),
            province=get_str(fm, "region"),
            sub_region=get_str(fm, "sub_region"),
            category_tag=category_tag(get_list(fm, "tags")),
        )
        for ev in events:
            by_event[ev].append(ps)
    return by_event


def render_event_page(event_slug: str, producers: list[ProducerSummary]) -> str:
    meta = EVENT_META.get(event_slug, {
        "display": event_slug.replace("_", " ").title(),
        "curator": "",
        "year": "",
        "location": "",
        "filename": event_slug,
    })
    producers = sorted(producers, key=lambda p: p.name.lower())
    today = date.today().isoformat()
    lines = [
        "---",
        "type: event",
        f"slug: {event_slug}",
        f'name: "{meta["display"]}"',
        f'curator: "{meta["curator"]}"',
        f'year: "{meta["year"]}"',
        f'location: "{meta["location"]}"',
        f"producer_count: {len(producers)}",
        f"updated: {today}",
        "---",
        "",
        f"# {meta['display']}",
        "",
    ]
    if meta["curator"]:
        lines.append(f"**Curator:** {meta['curator']}.")
    if meta["location"]:
        lines.append(f"**Location:** {meta['location']}.")
    lines.append(f"**Participating producers tracked in vault:** {len(producers)}.")
    lines.append("")
    lines.append("| Producer | Province | Sub-region | Category |")
    lines.append("|---|---|---|---|")
    for p in producers:
        lines.append(
            f"| [[{p.slug}|{p.name}]] | {p.province or '—'} | "
            f"{p.sub_region or '—'} | {p.category_tag or '—'} |"
        )
    lines += ["", "*Compiled by `scripts/build_event_rollups.py` from `wiki/producers/*.md` frontmatter `events: []`.*"]
    return "\n".join(lines) + "\n"


def main() -> int:
    EVENTS.mkdir(parents=True, exist_ok=True)
    by_event = load_producers_with_events()
    if not by_event:
        print("No producers with events[] found.")
        return 0
    written = 0
    for event_slug, producers in sorted(by_event.items()):
        meta = EVENT_META.get(event_slug)
        if not meta:
            print(f"WARN: event slug '{event_slug}' has {len(producers)} producers "
                  "but no metadata in EVENT_META — skipping page (but keeping data).")
            continue
        path = EVENTS / f"{meta['filename']}.md"
        path.write_text(render_event_page(event_slug, producers), encoding="utf-8")
        written += 1
        print(f"  {path.relative_to(VAULT)} — {len(producers)} producers")
    print(f"OK: {written} event page(s) written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
