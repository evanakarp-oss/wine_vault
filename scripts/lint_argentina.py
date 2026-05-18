"""
ARG-specific lint pass over wiki/producers/*.md (country == Argentina).

Checks:
  1. region in {Mendoza, Patagonia, Salta, Jujuy, San Juan, Buenos Aires Province}
  2. every events[] slug is in the known set (matches wiki/_TAXONOMY.md events)
  3. province sanity: if approach text mentions "Buenos Aires Province" but
     frontmatter region != "Buenos Aires Province", flag it (catches the
     Puerta del Abra case where JSX says province=Patagonia but the body
     describes Balcarce in Buenos Aires Province)
  4. category/farming consistency: producers tagged radical-natural should
     have farming include "natural"; biodynamic tag implies farming includes
     "biodynamic"; etc.

Output: build/lint_argentina.md (always) + compact stdout summary.
Exit code: 0 always — this is advisory, not gating.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "lint_argentina.md"

ALLOWED_REGIONS = {"Mendoza", "Patagonia", "Salta", "Jujuy", "San Juan", "Buenos Aires Province"}
KNOWN_EVENTS = {
    "argentina_reloaded_rio_2024",
    "argentina_reloaded_buenos_aires_2025",
    "argentina_reloaded_london_2022",
}

TAG_FARMING_RULES: list[tuple[str, str]] = [
    ("radical-natural", "natural"),
    ("biodynamic", "biodynamic"),
    ("organic", "organic"),
]

PROVINCE_HINTS: dict[str, list[str]] = {
    "Buenos Aires Province": ["Balcarce", "Buenos Aires Province", "province of Buenos Aires"],
    "Patagonia": ["Río Negro", "Rio Negro", "Chubut", "Neuquén", "Neuquen"],
    "Salta": ["Calchaquí", "Calchaqui", "Cafayate", "Molinos"],
    "Jujuy": ["Quebrada de Humahuaca", "Maimará", "Tilcara"],
    "San Juan": ["Calingasta"],
    "Mendoza": ["Uco Valley", "Valle de Uco", "Luján de Cuyo", "Lujan de Cuyo", "Gualtallary",
                "Tupungato", "Maipú", "Maipu", "Agrelo", "Perdriel"],
}

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_str_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m or not m.group(1).strip():
        return []
    return re.findall(r'"([^"]*)"', m.group(1))


def main() -> int:
    issues: list[tuple[str, str, str]] = []  # (slug, kind, detail)
    arg_count = 0

    for path in sorted(PRODUCERS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        if get_str(fm, "country") != "Argentina":
            continue

        slug = get_str(fm, "slug") or path.stem
        arg_count += 1
        region = get_str(fm, "region")
        events = get_str_list(fm, "events")
        farming = set(get_str_list(fm, "farming"))
        tags = set(get_str_list(fm, "tags"))

        if region not in ALLOWED_REGIONS:
            issues.append((slug, "region", f"region '{region}' not in taxonomy"))

        for ev in events:
            if ev not in KNOWN_EVENTS:
                issues.append((slug, "event", f"unknown event slug '{ev}'"))

        for tag, required_farming in TAG_FARMING_RULES:
            if tag in tags and required_farming not in farming:
                issues.append((slug, "farming-tag",
                               f"tag '{tag}' but farming missing '{required_farming}'"))

        for province, hints in PROVINCE_HINTS.items():
            if province == region:
                continue
            for hint in hints:
                if hint in body:
                    issues.append((slug, "province-hint",
                                   f"region='{region}' but body mentions '{hint}' (likely '{province}')"))
                    break

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    by_kind: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for slug, kind, detail in issues:
        by_kind[kind].append((slug, detail))

    lines = [
        "---",
        "type: lint_report",
        "scope: argentina",
        f'generated: "{datetime.now().isoformat(timespec="seconds")}"',
        f"argentina_producers: {arg_count}",
        f"issues_total: {len(issues)}",
        "---",
        "",
        "# Argentina lint report",
        "",
        f"Scanned **{arg_count}** producers with `country: Argentina`. Found **{len(issues)}** issue(s).",
        "",
    ]
    if not issues:
        lines.append("All clean.")
    else:
        for kind, entries in sorted(by_kind.items()):
            lines.append(f"## {kind} ({len(entries)})")
            lines.append("")
            for slug, detail in entries:
                lines.append(f"- `{slug}` — {detail}")
            lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Argentina producers: {arg_count} | issues: {len(issues)}")
    print(f"Report: {REPORT.relative_to(VAULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
