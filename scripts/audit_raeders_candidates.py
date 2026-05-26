"""
audit_raeders_candidates.py — surface Raeders producers that are NOT yet
in the vault, so they can be triaged through the curation flow.

Reads `raw/raeders/master_<latest>.csv`, groups by producer, joins
against `wiki/producers/*.md` (slug match + alias match), and writes
`build/raeders_candidates.md` — sorted by "vault-readiness" signal.
Highest signal first:

  - producer has ≥3 SKUs in Raeders inventory
  - producer name matches Evan's curation taste (Bordeaux/Champagne/
    Burgundy/Loire/Mosel/Piedmont/Napa cult tier)
  - producer appears in CSW article archive (lookup-only, by surname)

The output is a triage table. The actual onboarding still goes through
`compile_raeders_creates_v2.py` with the curated decision table —
that's deliberately human-in-the-loop per
`CLAUDE.md` → "Don't bulk-create producer pages from a single retailer
source without LLM curation."

Usage:
    python scripts/audit_raeders_candidates.py
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
RAW_DIR = VAULT / "raw" / "raeders"
PRODUCERS = VAULT / "wiki" / "producers"
OUTPUT = VAULT / "build" / "raeders_candidates.md"

CURATION_HINTS: list[tuple[str, str]] = [
    # (substring of region/category, taste-tier label)
    ("Bordeaux",       "BDX (verify WK-style farming + value tier)"),
    ("Champagne",      "Champagne (must be vintage / late-disgorged / grower)"),
    ("Burgundy",       "Burgundy (terroir-driven; check farming)"),
    ("Loire",          "Loire (terroir-driven; check biodynamic-lean)"),
    ("Mosel",          "Mosel (German biodynamic favored)"),
    ("Piedmont",       "Piedmont (grower-scale Barolo/Barbaresco)"),
    ("Barolo",         "Piedmont — Barolo"),
    ("Barbaresco",     "Piedmont — Barbaresco"),
    ("Napa",           "Napa (cult tier only)"),
]

CULT_NAPA = {
    "harlan", "hundred acre", "ridge", "monte bello", "bond", "colgin",
    "sine qua non", "sqn", "schrader", "screaming eagle",
}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def strip_common_prefix(s: str) -> str:
    return re.sub(
        r"^(domaine|chateau|weingut|bodegas|ch\.|clos)_",
        "",
        s.lower(),
    )


def load_producer_slugs() -> tuple[set[str], dict[str, set[str]]]:
    """Return (set of producer file stems, alias→stem map)."""
    stems: set[str] = set()
    aliases: dict[str, set[str]] = defaultdict(set)
    fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
    for p in PRODUCERS.glob("*.md"):
        stems.add(p.stem)
        text = p.read_text(encoding="utf-8", errors="replace")
        m = fm_re.match(text)
        if not m:
            continue
        fm = m.group(1)
        am = re.search(r'^aliases:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
        if am:
            for a in re.findall(r'"([^"]*)"', am.group(1)):
                aliases[slugify(a)].add(p.stem)
    return stems, aliases


def latest_master_csv() -> Path:
    csvs = sorted(RAW_DIR.glob("master_*.csv"))
    if not csvs:
        sys.exit(f"ERROR: no master_*.csv in {RAW_DIR}")
    return csvs[-1]


def main() -> int:
    csv_path = latest_master_csv()
    producer_stems, aliases = load_producer_slugs()

    by_producer: dict[str, list[dict]] = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prod = (row.get("producer") or row.get("Producer") or "").strip()
            if not prod:
                continue
            by_producer[prod].append(row)

    # Decide vault-presence per producer
    matched: list[str] = []
    candidates: list[tuple[int, str, list[dict]]] = []
    for prod, skus in sorted(by_producer.items()):
        s = slugify(prod)
        s_stripped = strip_common_prefix(s)
        if s in producer_stems or s_stripped in producer_stems:
            matched.append(prod)
            continue
        if aliases.get(s) or aliases.get(s_stripped):
            matched.append(prod)
            continue
        candidates.append((len(skus), prod, skus))

    candidates.sort(key=lambda x: -x[0])

    # Render
    lines = [
        "---",
        "type: raeders_candidates_report",
        f"source: {csv_path.name}",
        f"raeders_total_producers: {len(by_producer)}",
        f"already_in_vault: {len(matched)}",
        f"candidates: {len(candidates)}",
        "---",
        "",
        "# Raeders candidates — producers NOT yet in the vault",
        "",
        "Ordered by SKU count (descending). Apply Evan's curation taste "
        "before onboarding (see CLAUDE.md → Curation taste).",
        "",
        "**Onboarding flow:** add a decision row to "
        "`scripts/compile_raeders_creates_v2.py`, then re-run that script.",
        "",
        f"## Top candidates ({min(100, len(candidates))} of {len(candidates)})",
        "",
        "| # | Producer | SKUs | Sample wine | Hint |",
        "|---|---|---:|---|---|",
    ]
    for rank, (n_skus, prod, skus) in enumerate(candidates[:100], start=1):
        sample = skus[0]
        wine = (sample.get("wine") or sample.get("Wine")
                or sample.get("cuvee") or "").strip()
        region = (sample.get("region") or sample.get("Region") or "").strip()
        category = (sample.get("category") or sample.get("Category") or "").strip()
        hint = ""
        for kw, label in CURATION_HINTS:
            if kw.lower() in region.lower() or kw.lower() in category.lower():
                hint = label
                break
        if not hint and any(c in prod.lower() for c in CULT_NAPA):
            hint = "Napa (cult tier — check)"
        if not hint:
            hint = f"{region or category or '(no region tag)'}"
        wine_short = (wine[:50] + "…") if len(wine) > 50 else wine
        lines.append(f"| {rank} | {prod} | {n_skus} | {wine_short} | {hint} |")
    if len(candidates) > 100:
        lines.append("")
        lines.append(f"_… and {len(candidates) - 100} more — see CSV for full list._")
    lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRaeders producers: {len(by_producer)}")
    print(f"  already in vault: {len(matched)}")
    print(f"  candidates:       {len(candidates)}")
    print(f"  report:           {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
