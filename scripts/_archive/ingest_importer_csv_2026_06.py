"""
Generic one-shot: ingest a producer CSV from raw/<importer>/producers.csv
into wiki/producers/, tagging each row with the given importer in
importer_us. Generalization of scripts/_archive/ingest_veritas_2026_05.py
to support the multi-importer wave kicked off in 2026-06 (Veritas, Zev
Rovine, David Bowler, DNS).

CSV schema: slug,name,country,region,sub_region,url,notes
  - country / region must conform to wiki/_TAXONOMY.md
  - rows whose slug already exists in wiki/producers/ get their
    importer_us list extended (idempotent)

Usage:
  python scripts/_archive/ingest_importer_csv_2026_06.py \\
      --importer "Zev Rovine Selections" --csv raw/zev_rovine/producers.csv
  ...with --apply to actually write.
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
PRODUCERS = VAULT / "wiki" / "producers"

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def stub_frontmatter(row: dict[str, str], importer: str,
                     source_tag: str) -> dict[str, Any]:
    return {
        "type": "producer",
        "name": row["name"],
        "slug": row["slug"],
        "aliases": [],
        "country": row["country"],
        "region": row["region"],
        "sub_region": (row.get("sub_region") or "").strip(),
        "appellations": [],
        "farming": [],
        "certifications": [],
        "importer_us": [importer],
        "retailers": {
            "chambers": {
                "championed": False, "article_count": 0,
                "dedicated_count": 0, "first_year": 0, "last_year": 0,
            },
            "dte": {"in_portfolio": False},
            "raeders": {"in_portfolio": False},
            "fass": {"in_portfolio": False},
        },
        "tags": [],
        "_sources": [source_tag],
    }


def stub_body(row: dict[str, str], importer: str) -> str:
    notes = (row.get("notes") or "").strip()
    url = (row.get("url") or "").strip()
    sub_region = (row.get("sub_region") or "").strip()
    parts = [f"# {row['name']}", ""]
    if sub_region:
        intro = f"**{sub_region}**, {row['region']}, {row['country']}."
    else:
        intro = f"**{row['region']}, {row['country']}**."
    if notes:
        intro += f" {notes}."
    parts.append(intro)
    parts.append("")
    parts.append(
        f"_Stub seeded from the {importer} US importer portfolio. Body to be "
        f"enriched on a future compile pass once the live importer site is "
        f"fetchable locally._"
    )
    parts.append("")
    parts.append(f"## {importer} (US importer)")
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
    parts.append("")
    return "\n".join(parts)


def write_stub(path: Path, row: dict[str, str], importer: str,
               source_tag: str) -> None:
    fm = stub_frontmatter(row, importer, source_tag)
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    path.write_text(f"---\n{fm_text}\n---\n\n{stub_body(row, importer)}",
                    encoding="utf-8")


def add_importer_to_existing(path: Path, importer: str) -> bool:
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return False
    fm_raw, body = m.group(1), m.group(2)
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError:
        return False
    current = fm.get("importer_us") or []
    if not isinstance(current, list):
        current = [current] if current else []
    if importer in current:
        return False
    current.append(importer)
    fm["importer_us"] = current
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    path.write_text(f"---\n{fm_text}\n---\n{body}", encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--importer", required=True, help='Name as in importer_us, e.g. "Zev Rovine Selections"')
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--source-tag", default=None,
                    help="value for _sources; default derived from CSV path")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    csv_path = args.csv if args.csv.is_absolute() else VAULT / args.csv
    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")
    source_tag = args.source_tag or (
        f"{csv_path.parent.name}_websearch_2026-06-13"
    )

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    print(f"Loaded {len(rows)} rows from {csv_path.relative_to(VAULT)} → importer={args.importer!r}")

    created, updated, skipped = 0, 0, 0
    for row in rows:
        slug = row["slug"].strip()
        if not slug:
            continue
        path = PRODUCERS / f"{slug}.md"
        if path.exists():
            if args.apply:
                if add_importer_to_existing(path, args.importer):
                    print(f"  UPDATE {slug}")
                    updated += 1
                else:
                    skipped += 1
            else:
                text = path.read_text(encoding="utf-8")
                if args.importer in text:
                    print(f"  ALREADY OK   {slug}")
                    skipped += 1
                else:
                    print(f"  WOULD UPDATE {slug}")
                    updated += 1
        else:
            if args.apply:
                write_stub(path, row, args.importer, source_tag)
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
