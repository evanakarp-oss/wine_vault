"""
One-shot ingest for the Veritas Wines (California) importer portfolio.

Source: raw/veritas/producers.csv — harvested 2026-05-28 from WebSearch
snippets against site:veritaswine.com (the live site blocks automated
fetches from the Claude Code on the web sandbox with HTTP 403). Provenance
details in raw/veritas/_README.md.

For each row:
  - If a producer page already exists in wiki/producers/<slug>.md,
    add "Veritas Wines" to importer_us in the frontmatter (idempotent).
  - Otherwise, write a minimal stub producer page with country / region /
    sub_region / importer_us set, plus a body link back to the Veritas
    producer URL. Body is intentionally sparse — a future
    compile_veritas.py pass (after a local re-scrape against the live
    site) should enrich it with hectares, farming detail, winemaker name,
    cuvée list, etc.

Idempotent: safe to re-run. Touches only wiki/producers/*.md.

This is a one-shot archived under scripts/_archive/ following the repo
convention. After running, regenerate the importer rollup page and the
top-level index:

  python scripts/build_rollups.py
  python scripts/build_wiki_index.py

Usage:
  python scripts/_archive/ingest_veritas_2026_05.py            # dry run
  python scripts/_archive/ingest_veritas_2026_05.py --apply
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("Need pyyaml: pip install pyyaml --break-system-packages")


VAULT = Path(__file__).resolve().parent.parent.parent
CSV_PATH = VAULT / "raw" / "veritas" / "producers.csv"
PRODUCERS = VAULT / "wiki" / "producers"
IMPORTER_NAME = "Veritas Wines"
SOURCE_TAG = "veritas_websearch_2026-05-28"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def stub_frontmatter(row: dict[str, str]) -> dict[str, Any]:
    return {
        "type": "producer",
        "name": row["name"],
        "slug": row["slug"],
        "aliases": [],
        "country": row["country"],
        "region": row["region"],
        "sub_region": row.get("sub_region", "") or "",
        "appellations": [],
        "farming": [],
        "certifications": [],
        "importer_us": [IMPORTER_NAME],
        "retailers": {
            "chambers": {
                "championed": False,
                "article_count": 0,
                "dedicated_count": 0,
                "first_year": 0,
                "last_year": 0,
            },
            "dte": {"in_portfolio": False},
            "raeders": {"in_portfolio": False},
            "fass": {"in_portfolio": False},
        },
        "tags": [],
        "_sources": [SOURCE_TAG],
    }


def stub_body(row: dict[str, str]) -> str:
    notes = (row.get("notes") or "").strip()
    url = (row.get("url") or "").strip()
    sub_region = (row.get("sub_region") or "").strip()

    parts: list[str] = [f"# {row['name']}", ""]
    intro_bits = []
    if sub_region:
        intro_bits.append(f"**{sub_region}**, {row['region']}, {row['country']}.")
    else:
        intro_bits.append(f"**{row['region']}, {row['country']}**.")
    if notes:
        intro_bits.append(notes + ".")
    parts.append(" ".join(intro_bits))
    parts.append("")
    parts.append(
        "_Stub seeded from the Veritas Wines (California) US importer "
        "portfolio. Body to be enriched on a future compile pass once the "
        "live site is fetchable locally._"
    )
    parts.append("")
    parts.append("## Veritas Wines (US importer)")
    parts.append("")
    if url:
        parts.append(f"Profile: <{url}>")
        parts.append("")

    parts.append("## CSW Write-ups")
    parts.append("")
    parts.append("_No Chambers Street write-ups on file._")
    parts.append("")
    parts.append("## Down to Earth Wines (Panzer)")
    parts.append("")
    parts.append("_Not in portfolio._")
    parts.append("")
    parts.append("## Raeder's")
    parts.append("")
    parts.append("_Not in portfolio._")
    parts.append("")
    parts.append("## FASS")
    parts.append("")
    parts.append("_Not in portfolio._")
    parts.append("")
    parts.append("## Cross-references")
    parts.append("")
    parts.append(f"- [[{row['region']}_Producers|{row['region']}]]")
    parts.append(f"- [[Veritas_Wines|Veritas Wines (importer)]]")
    parts.append("")
    return "\n".join(parts)


def write_stub(path: Path, row: dict[str, str]) -> None:
    fm = stub_frontmatter(row)
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    body = stub_body(row)
    path.write_text(f"---\n{fm_text}\n---\n\n{body}", encoding="utf-8")


def add_importer_to_existing(path: Path) -> bool:
    """Append 'Veritas Wines' to importer_us list if not already present.
    Returns True if file was modified."""
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        print(f"  WARN: {path.name} has no frontmatter — skipping", file=sys.stderr)
        return False
    fm_raw, body = m.group(1), m.group(2)
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError as e:
        print(f"  WARN: {path.name} YAML error {e} — skipping", file=sys.stderr)
        return False

    current = fm.get("importer_us") or []
    if not isinstance(current, list):
        current = [current] if current else []
    if IMPORTER_NAME in current:
        return False
    current.append(IMPORTER_NAME)
    fm["importer_us"] = current
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    path.write_text(f"---\n{fm_text}\n---\n{body}", encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write files")
    args = ap.parse_args()

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    print(f"Loaded {len(rows)} rows from {CSV_PATH.relative_to(VAULT)}")

    created, updated, skipped = 0, 0, 0
    for row in rows:
        slug = row["slug"].strip()
        if not slug:
            continue
        path = PRODUCERS / f"{slug}.md"
        if path.exists():
            if args.apply:
                if add_importer_to_existing(path):
                    print(f"  UPDATE {slug}")
                    updated += 1
                else:
                    skipped += 1
            else:
                # Dry-run preview
                text = path.read_text(encoding="utf-8")
                if IMPORTER_NAME in text:
                    print(f"  ALREADY OK   {slug}")
                    skipped += 1
                else:
                    print(f"  WOULD UPDATE {slug}")
                    updated += 1
        else:
            if args.apply:
                write_stub(path, row)
                print(f"  CREATE {slug}")
            else:
                print(f"  WOULD CREATE {slug}  ({row['country']} / {row['region']})")
            created += 1

    print()
    print(f"Summary: created={created} updated={updated} skipped={skipped}")
    if not args.apply:
        print("(dry-run — pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
