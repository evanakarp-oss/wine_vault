#!/usr/bin/env python3
"""
parse_auction_ratings.py — landing layer for critic RATINGS embedded in
auction catalogs.

Acker 261W catalogs carry, in the `WineNote` column, a critic tasting note
plus a score tag like `(93pts BH)`, `(96-98+pts VM)`, or a bare `(95pts)`.
This script extracts those into a structured, greppable JSON under
`raw/ratings/<sale>/` — the source-of-truth landing layer. The compile pass
(`compile_auction_ratings.py`) matches them to producer pages and writes a
`## Critic Ratings` section. Landing is deterministic; matching/curation is
the compile step's job (same split as scrape/parse vs compile elsewhere).

Critic initials → publication (auction convention). Unknown initials are kept
verbatim in `critic` so nothing is silently mis-attributed.

Usage:
    python scripts/parse_auction_ratings.py                       # newest 261W catalog → dry-run summary
    python scripts/parse_auction_ratings.py --apply               # write raw/ratings/<sale>/ratings_<week>.json
    python scripts/parse_auction_ratings.py --file raw/auctions/Catalog_261W_30.xlsx --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl required: pip install openpyxl")

VAULT = Path(__file__).resolve().parent.parent
AUCTIONS = VAULT / "raw" / "auctions"
RATINGS = VAULT / "raw" / "ratings"

# Critic initials as they appear in Acker WineNotes → publication label.
CRITIC_MAP = {
    "VM": "Vinous",
    "BH": "Burghound",
    "WS": "Wine Spectator",
    "WA": "Wine Advocate",
    "JS": "James Suckling",
    "JD": "Jeb Dunnuck",
    "IWC": "International Wine Cellar",
    "WE": "Wine Enthusiast",
    "D": "Decanter",
}

# ( <score>[-<hi>][+] pts|points [INITIALS] )
SCORE_TAG = re.compile(
    r"\(\s*(\d{2,3})\s*(?:[-–]\s*(\d{1,3}))?\s*(\+?)\s*(?:pts?|points?)\.?\s*([A-Za-z]{1,4})?\s*\)",
    re.IGNORECASE,
)

COLS = ["LotNo", "Quantity", "BottleName", "Vintage", "WineName", "Designation",
        "Producer", "Levels", "Low", "High", "WineType", "RegionDescription",
        "ItemLocation", "ItemWineScore", "WineNote", "AddlLots"]


def load_rows(path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    hdr = [str(x) for x in rows[0]]
    return [dict(zip(hdr, r)) for r in rows[1:]]


def sale_ident(path: Path) -> tuple[str, str]:
    """('261W', '30') from Catalog_261W_30.xlsx; ('261W','') fallback."""
    m = re.search(r"Catalog_([0-9]+[A-Za-z]*)_([0-9]+)", path.stem, re.IGNORECASE)
    if m:
        return m.group(1).upper(), m.group(2)
    m = re.search(r"([0-9]+[A-Za-z]+)", path.stem)
    return (m.group(1).upper() if m else path.stem), ""


def clean_note(note: str) -> str:
    """Prefer the critic prose (text inside the outermost double-quotes);
    else the whole note with the score tag(s) removed. Collapse whitespace,
    drop table-hostile characters."""
    note = note.strip()
    q = re.search(r'"(.+)"', note, re.DOTALL)
    prose = q.group(1) if q else SCORE_TAG.sub("", note)
    prose = prose.replace("|", "/").replace("\n", " ")
    prose = re.sub(r"\s+", " ", prose).strip(' "')
    return prose


def score_str(lo: str, hi: str, plus: str) -> str:
    s = lo
    if hi:
        s = f"{lo}-{hi}"
    if plus:
        s += "+"
    return s


def extract(rows: list[dict], sale: str, week: str, source_file: str) -> list[dict]:
    out = []
    for d in rows:
        note = (d.get("WineNote") or "").strip()
        if not note:
            continue
        tags = list(SCORE_TAG.finditer(note))
        if not tags:
            continue
        # Primary score = the first tag; keep others in `all_scores`.
        prose = clean_note(note)
        all_scores = []
        for m in tags:
            initials = (m.group(4) or "").upper()
            all_scores.append({
                "critic_raw": initials or "",
                "critic": CRITIC_MAP.get(initials, initials) if initials else "",
                "score": score_str(m.group(1), m.group(2), m.group(3)),
            })
        primary = all_scores[0]
        out.append({
            "lot": d.get("LotNo"),
            "producer_raw": (d.get("Producer") or "").strip(),
            "wine": (d.get("WineName") or "").strip(),
            "designation": (d.get("Designation") or "").strip(),
            "vintage": str(d.get("Vintage") or "").strip(),
            "region": (d.get("RegionDescription") or "").strip(),
            "location": (d.get("ItemLocation") or "").strip(),
            "critic": primary["critic"],
            "critic_raw": primary["critic_raw"],
            "score": primary["score"],
            "all_scores": all_scores,
            "note": prose[:500],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Catalog xlsx to parse (default: newest 261W in raw/auctions/)")
    ap.add_argument("--apply", action="store_true", help="Write JSON. Default is dry-run summary.")
    args = ap.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = VAULT / path
    else:
        cands = sorted(AUCTIONS.glob("Catalog_261W_*.xlsx"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if not cands:
            sys.exit("no Catalog_261W_*.xlsx in raw/auctions/")
        path = cands[0]

    sale, week = sale_ident(path)
    rel = str(path.relative_to(VAULT)) if path.is_relative_to(VAULT) else str(path)
    rows = load_rows(path)
    ratings = extract(rows, sale, week, rel)

    from collections import Counter
    crit = Counter(r["critic"] or "(unattributed)" for r in ratings)
    print(f"{path.name}: {len(rows)} lots → {len(ratings)} scored ratings")
    for k, v in crit.most_common():
        print(f"  {v:4d}  {k}")

    payload = {
        "sale": sale,
        "week": week,
        "source_file": rel,
        "captured": date.today().isoformat(),
        "count": len(ratings),
        "ratings": ratings,
    }
    out_dir = RATINGS / sale
    out_name = f"ratings_week{week}.json" if week else "ratings.json"
    out_path = out_dir / out_name
    if args.apply:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {out_path.relative_to(VAULT)}")
    else:
        print(f"\n(dry-run) would write {out_path.relative_to(VAULT)} — pass --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
