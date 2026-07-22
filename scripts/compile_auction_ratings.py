#!/usr/bin/env python3
"""
compile_auction_ratings.py — attach landed critic RATINGS to producer pages.

Reads every ratings landing JSON under `raw/ratings/**/ratings*.json` — from
`parse_auction_ratings.py` (auction catalogs) and `parse_raeders_ratings.py`
(Raeders inventory), and any future source in the same record shape — matches
each rating to a `wiki/producers/` page, and writes a single auto-generated
`## Critic Ratings` section (a table of wine / vintage / critic / score / note /
source) merging all sources per producer.

Each record may carry an explicit `producer_slug` (preferred, page-backed) and a
preformatted `source` string; auction records without a slug fall back to
conservative name matching.

Matching is conservative — exact normalized name, alias, slug-words, or an
`<Initial>. Surname` expansion — and anything not confidently matched is
listed in `build/auction_ratings_report.md` for review (same curation
discipline as CSW / Raeders / clippings; a retailer/auction source does not
auto-create producer pages).

Idempotent: re-running rewrites the section in place; other sections are
untouched. Section placement + replace logic mirror `compile_clippings.py`.

Usage:
    python scripts/compile_auction_ratings.py            # dry-run summary
    python scripts/compile_auction_ratings.py --apply    # write sections + report
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RATINGS = VAULT / "raw" / "ratings"
REPORT = VAULT / "build" / "auction_ratings_report.md"

SECTION_HEADER = "## Critic Ratings"
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
NOTE_MAX = 160

PREFIXES = ("domaine ", "chateau ", "ch. ", "weingut ", "maison ", "tenuta ",
            "azienda agricola ", "az. agr. ", "cantina ", "podere ", "castello ")

# Placement: keep ratings in the critic cluster (after CSW/community/critic
# sections, before the retailer/cross-ref/notes tail).
INSERT_BEFORE = ("## Down to Earth Wines (Panzer)", "## Raeder's", "## FASS",
                 "## Cross-references", "## Notes", "## Cellar")


def norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()
    for pre in PREFIXES:
        if s.startswith(pre):
            s = s[len(pre):]
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def fm_get(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip().strip("'") if m else ""


def load_index():
    """Return (exact, surname, token_owners).

    - exact:        normalized name/alias/slug-words -> slug
    - surname:      last-token -> list[(slug, first_token)]  (for "X. Surname")
    - token_owners: any name token -> set(slug)  (ambiguity guard)
    """
    exact: dict[str, str] = {}
    surname: dict[str, list[tuple[str, str]]] = defaultdict(list)
    token_owners: dict[str, set] = defaultdict(set)
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = FM_RE.match(text)
        if not m:
            continue
        fm = m.group(1)
        slug = p.stem
        name = fm_get(fm, "name") or slug
        keys = {norm(name), norm(slug.replace("_", " "))}
        am = re.search(r"^aliases:\s*\[(.*?)\]", fm, re.MULTILINE)
        if am:
            for a in re.findall(r'"([^"]+)"', am.group(1)):
                keys.add(norm(a))
        for k in keys:
            if k:
                exact.setdefault(k, slug)
                toks = k.split()
                for t in toks:
                    if len(t) >= 3:
                        token_owners[t].add(slug)
                if len(toks) >= 2:
                    surname[toks[-1]].append((slug, toks[0]))
    return exact, surname, token_owners


def match(producer_raw: str, wine: str, exact, surname, token_owners) -> str | None:
    if producer_raw:
        # Producer field is populated → match on it only. Do NOT fall back to
        # the wine name, which for Burgundy/Piedmont is the appellation/cuvée
        # (e.g. "Barbaresco") and would mis-attribute to a same-named house.
        c = norm(producer_raw)
        if c in exact:
            return exact[c]
        toks = c.split()
        # "<initial>. Surname" (e.g. "G. Conterno", "R. Chevillon")
        if len(toks) >= 2 and len(toks[0]) <= 2:
            hits = surname.get(toks[-1], [])
            if len(hits) == 1:
                return hits[0][0]
            if len(hits) > 1:
                narrowed = [s for s, first in hits if first.startswith(toks[0][0])]
                if len(narrowed) == 1:
                    return narrowed[0]
        # Single distinctive token unique across the vault (e.g. "Cavallotto")
        if len(toks) == 1 and len(toks[0]) >= 5 and len(token_owners.get(toks[0], ())) == 1:
            return exact.get(toks[0]) or next(iter(token_owners[toks[0]]))
        return None

    # Producer embedded in the wine name (Napa/Bordeaux/Champagne). Match on the
    # longest exact leading-word prefix. A 1-word prefix is accepted only when it
    # is unambiguous across the vault — a bare "Latour" maps to several houses, so
    # it is left unmatched rather than guessed.
    parts = norm(wine).split()
    for k in (3, 2, 1):
        if len(parts) < k:
            continue
        pk = " ".join(parts[:k])
        if pk in exact:
            if k >= 2 or len(token_owners.get(pk, ())) == 1:
                return exact[pk]
    return None


def wine_label(r: dict) -> str:
    parts = [r.get("wine", ""), r.get("designation", "")]
    label = " ".join(p for p in parts if p).strip()
    return re.sub(r"\s+", " ", label) or "(unnamed)"


def render_section(ratings: list[dict]) -> str:
    # Dedup by (wine, vintage, critic, score); sort by wine then vintage.
    seen = set()
    rows = []
    for r in ratings:
        label = wine_label(r)
        key = (label.lower(), r.get("vintage", ""), r.get("critic", ""), r.get("score", ""))
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
    rows.sort(key=lambda r: (wine_label(r).lower(), str(r.get("vintage", ""))))

    lines = [
        SECTION_HEADER,
        "",
        "_Auto-generated from landed critic ratings (auction catalogs + Raeders) "
        "by `compile_auction_ratings.py`. Don't hand-edit — see `wiki/_SCHEMA.md`._",
        "",
        "| Wine | Vintage | Critic | Score | Note | Source |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        note = (r.get("note") or "").replace("|", "/")
        if len(note) > NOTE_MAX:
            note = note[:NOTE_MAX].rstrip() + "…"
        critic = r.get("critic") or "—"
        src = r.get("_source_tag", "")
        lines.append(
            f"| {wine_label(r)} | {r.get('vintage','')} | {critic} | "
            f"{r.get('score','')} | {note} | {src} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_section(path: Path, body: str) -> bool:
    text = path.read_text(encoding="utf-8")
    section_re = re.compile(
        rf"({re.escape(SECTION_HEADER)}\n.*?)(?=^## |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    if section_re.search(text):
        new_text = section_re.sub(body + "\n", text)
    else:
        anchor_m = None
        for anchor in INSERT_BEFORE:
            m = re.search(rf"^{re.escape(anchor)}\s*$", text, re.MULTILINE)
            if m:
                anchor_m = m
                break
        if anchor_m:
            new_text = text[:anchor_m.start()] + body + "\n" + text[anchor_m.start():]
        else:
            new_text = text.rstrip() + "\n\n" + body + "\n"
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write sections + report. Default dry-run.")
    args = ap.parse_args()

    files = sorted(RATINGS.glob("*/ratings*.json"))
    if not files:
        sys.exit("no raw/ratings/*/ratings*.json — run parse_auction_ratings.py --apply first")

    exact, surname, token_owners = load_index()

    by_slug: dict[str, list[dict]] = defaultdict(list)
    unmatched: list[dict] = []
    for f in files:
        payload = json.loads(f.read_text(encoding="utf-8"))
        sale, week = payload.get("sale", "?"), payload.get("week", "")
        fallback = f"{sale}·W{week} lot {{lot}}" if week else f"{sale} lot {{lot}}"
        for r in payload["ratings"]:
            r["_source_tag"] = r.get("source") or fallback.format(lot=r.get("lot"))
            # Prefer an explicit, page-backed producer_slug (Raeders carries one);
            # otherwise fall back to conservative name matching (auction catalogs).
            slug = r.get("producer_slug")
            if not (slug and (PRODUCERS / f"{slug}.md").exists()):
                slug = match(r.get("producer_raw", ""), r.get("wine", ""),
                             exact, surname, token_owners)
            if slug:
                by_slug[slug].append(r)
            else:
                unmatched.append(r)

    changed = 0
    for slug, ratings in sorted(by_slug.items()):
        path = PRODUCERS / f"{slug}.md"
        if not path.exists():
            unmatched.extend(ratings)
            continue
        body = render_section(ratings)
        if args.apply:
            if write_section(path, body):
                changed += 1
        else:
            changed += 1

    print(f"ratings files: {len(files)} | producers matched: {len(by_slug)} | "
          f"pages {'updated' if args.apply else 'to update'}: {changed}")
    print(f"unmatched ratings (no confident producer page): {len(unmatched)}")

    if args.apply:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Auction ratings — unmatched producers",
                 "",
                 f"{len(unmatched)} scored ratings could not be confidently matched to a "
                 "`wiki/producers/` page (mostly off-taste producers with no page, or "
                 "abbreviated names). Review + alias into a page, or leave.",
                 "",
                 "| Producer (raw) | Wine | Vintage | Critic | Score | Source |",
                 "|---|---|---|---|---|---|"]
        for r in sorted(unmatched, key=lambda r: (r.get("producer_raw", "") or r.get("wine", ""))):
            lines.append(
                f"| {r.get('producer_raw','') or '—'} | {wine_label(r)} | "
                f"{r.get('vintage','')} | {r.get('critic') or '—'} | {r.get('score','')} | "
                f"{r.get('_source_tag','')} |")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {REPORT.relative_to(VAULT)}")

    # Top matched producers (helps eyeball quality)
    top = sorted(by_slug.items(), key=lambda kv: -len(kv[1]))[:12]
    print("\ntop matched producers:")
    for slug, rs in top:
        print(f"  {len(rs):3d}  {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
