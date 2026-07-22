#!/usr/bin/env python3
"""
parse_raeders_ratings.py — landing layer for critic RATINGS carried in the
Raeder's inventory snapshot.

The Raeders master CSV (`raw/raeders/master_<date>.csv`) has four score columns
— `score_wa` (Wine Advocate), `score_js` (James Suckling), `score_we` (Wine
Enthusiast), `score_w_s` (Wine Spectator) — plus a `tasting_note`. This lands
every non-zero score as a record in the shared ratings schema under
`raw/ratings/raeders/`, so `compile_auction_ratings.py` folds them into the same
`## Critic Ratings` section it builds from auction catalogs.

Producer resolution is deferred to the compile step: each record carries
`producer_slug` (= ascii_slug(producer), matching the Raeders ingest) and
`producer_raw`, and the compiler prefers the page-backed slug, else fuzzy-matches
the name (stripping Domaine/Château prefixes).

Usage:
    python scripts/parse_raeders_ratings.py            # dry-run summary
    python scripts/parse_raeders_ratings.py --apply    # write raw/ratings/raeders/ratings_<date>.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
RAEDERS = VAULT / "raw" / "raeders"
RATINGS = VAULT / "raw" / "ratings"

# CSV score column -> publication label. Priority order = note-attachment order.
SCORE_COLS = [
    ("score_wa", "Wine Advocate"),
    ("score_js", "James Suckling"),
    ("score_w_s", "Wine Spectator"),
    ("score_we", "Wine Enthusiast"),
]

# Strip a leading inline critic tag from a note, e.g. "WE 92 The 2018..." .
NOTE_TAG = re.compile(r"^\s*(?:WA|WS|JS|WE|VM|BH|RP|JD|AG)\s*\d{2,3}\+?\s*[-:]?\s*", re.IGNORECASE)


def ascii_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    return re.sub(r"[\s-]+", "_", s).strip("_")


def to_score(v) -> int:
    try:
        f = float(v)
        return int(f) if f > 0 else 0
    except (TypeError, ValueError):
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="master CSV (default: newest raw/raeders/master_*.csv)")
    ap.add_argument("--apply", action="store_true", help="Write JSON. Default dry-run.")
    args = ap.parse_args()

    if args.file:
        csv_path = Path(args.file)
        if not csv_path.is_absolute():
            csv_path = VAULT / csv_path
    else:
        cands = sorted(RAEDERS.glob("master_*.csv"), reverse=True)
        if not cands:
            sys.exit("no raw/raeders/master_*.csv")
        csv_path = cands[0]

    m = re.search(r"(\d{4}-\d{2}-\d{2})", csv_path.stem)
    snap = m.group(1) if m else "unknown"

    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    ratings = []
    for row in rows:
        scored = [(col, label, to_score(row.get(col))) for col, label in SCORE_COLS]
        scored = [(col, label, s) for col, label, s in scored if s > 0]
        if not scored:
            continue
        producer = (row.get("producer") or "").strip()
        cuvee = (row.get("cuvee") or "").strip()
        vintage = str(row.get("vintage") or "").strip()
        note = NOTE_TAG.sub("", (row.get("tasting_note") or "").strip())
        note = re.sub(r"\s+", " ", note).replace("|", "/")
        # Highest score gets the (single) note; ties resolved by SCORE_COLS order.
        primary_idx = max(range(len(scored)), key=lambda i: (scored[i][2], -i))
        for i, (col, label, s) in enumerate(scored):
            ratings.append({
                "source": f"Raeders {snap}",
                "producer_slug": ascii_slug(producer),
                "producer_raw": producer,
                "wine": cuvee,
                "designation": "",
                "vintage": vintage,
                "region": (row.get("region") or "").strip(),
                "critic": label,
                "critic_raw": col.replace("score_", "").upper(),
                "score": str(s),
                "note": (note[:500] if i == primary_idx else ""),
            })

    crit = Counter(r["critic"] for r in ratings)
    print(f"{csv_path.name}: {len(rows)} rows → {len(ratings)} score records "
          f"({sum(1 for r in rows if any(to_score(r.get(c))>0 for c,_ in SCORE_COLS))} scored wines)")
    for k, v in crit.most_common():
        print(f"  {v:4d}  {k}")

    payload = {
        "sale": "Raeders",
        "week": "",
        "source_file": str(csv_path.relative_to(VAULT)),
        "captured": snap,
        "count": len(ratings),
        "ratings": ratings,
    }
    out_path = RATINGS / "raeders" / f"ratings_{snap}.json"
    if args.apply:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {out_path.relative_to(VAULT)}")
    else:
        print(f"\n(dry-run) would write {out_path.relative_to(VAULT)} — pass --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
