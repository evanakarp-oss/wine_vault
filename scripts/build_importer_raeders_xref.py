"""
build_importer_raeders_xref.py — cross-reference an importer's portfolio
against the Raeders inventory.

For each producer in wiki/producers/ tagged with the given importer in
importer_us, fuzzy-match against the latest raw/raeders/master_*.csv and
list every Raeders cuvée. Producers not at Raeders are listed as gaps.

Output: wiki/_views/<importer_slug>_raeders_xref_<YYYY-MM>.md

Usage:
  python scripts/build_importer_raeders_xref.py "Skurnik"
  python scripts/build_importer_raeders_xref.py "Veritas Wines" --apply
  python scripts/build_importer_raeders_xref.py "Skurnik" --out /tmp/x.md

  --apply         actually write the file (default = stdout preview)
  --out PATH      override output path
  --min-score N   fuzzy threshold (default 0.86)
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Need pyyaml: pip install pyyaml --break-system-packages")


VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RAEDERS_DIR = VAULT / "raw" / "raeders"
VIEWS = VAULT / "wiki" / "_views"

PREFIXES = (
    "Domaine ", "Château ", "Chateau ", "Ch. ", "Ch ",
    "Weingut ", "Maison ", "Bodega ", "Bodegas ",
    "Tenuta ", "Cantina ", "Azienda Agricola ", "Agricola ",
    "Le ", "La ", "Les ", "El ",
)

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def canonical(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.strip()
    for p in PREFIXES:
        if s.startswith(p):
            s = s[len(p):].strip()
            break
    s = re.sub(r"[^\w\s]", " ", s).lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def safe_filename(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s\-]", "", s).strip().lower()
    s = re.sub(r"\s+", "_", s)
    return s or "importer"


@dataclass
class WikiProducer:
    slug: str
    name: str
    country: str
    region: str
    sub_region: str
    importer_us: list[str]
    aliases: list[str]
    raeders_in_portfolio: bool


def load_wiki_producers() -> list[WikiProducer]:
    out: list[WikiProducer] = []
    for path in sorted(PRODUCERS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if (fm.get("type") or "") != "producer":
            continue
        retailers = fm.get("retailers") or {}
        raeders = retailers.get("raeders") or {}
        out.append(WikiProducer(
            slug=fm.get("slug") or path.stem,
            name=fm.get("name") or path.stem,
            country=fm.get("country") or "",
            region=fm.get("region") or "",
            sub_region=fm.get("sub_region") or "",
            importer_us=fm.get("importer_us") or [],
            aliases=fm.get("aliases") or [],
            raeders_in_portfolio=bool(raeders.get("in_portfolio")),
        ))
    return out


@dataclass
class RaedersCuvee:
    producer: str
    cuvee: str
    vintage: str
    size: str
    price: float
    mc_price: float
    score_wa: int
    score_js: int
    score_we: int
    score_ws: int
    url: str
    country: str
    region: str


@dataclass
class RaedersProducer:
    name: str
    canon: str
    cuvees: list[RaedersCuvee] = field(default_factory=list)
    countries: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)


def latest_master_csv() -> Path:
    cands = sorted(RAEDERS_DIR.glob("master_*.csv"))
    if not cands:
        sys.exit(f"No master_*.csv in {RAEDERS_DIR}")
    return cands[-1]


def load_raeders() -> tuple[dict[str, RaedersProducer], Path]:
    csv_path = latest_master_csv()
    out: dict[str, RaedersProducer] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pname = (row.get("producer") or "").strip()
            if not pname:
                continue
            canon = canonical(pname)
            p = out.get(canon)
            if p is None:
                p = RaedersProducer(name=pname, canon=canon)
                out[canon] = p
            p.countries.add((row.get("country") or "").strip())
            p.regions.add((row.get("region") or "").strip())

            def fnum(k: str) -> float:
                try:
                    return float(row.get(k) or 0)
                except ValueError:
                    return 0.0

            def inum(k: str) -> int:
                try:
                    return int(row.get(k) or 0)
                except ValueError:
                    return 0

            p.cuvees.append(RaedersCuvee(
                producer=pname,
                cuvee=(row.get("cuvee") or "").strip(),
                vintage=(row.get("vintage") or "").strip() or "NV",
                size=(row.get("size") or "").strip(),
                price=fnum("price_usd"),
                mc_price=fnum("mixed_case_usd"),
                score_wa=inum("score_wa"),
                score_js=inum("score_js"),
                score_we=inum("score_we"),
                score_ws=inum("score_w_s"),
                url=(row.get("url") or "").strip(),
                country=(row.get("country") or "").strip(),
                region=(row.get("region") or "").strip(),
            ))
    return out, csv_path


def match_in_raeders(wp: WikiProducer, raeders: dict[str, RaedersProducer],
                     min_score: float) -> tuple[RaedersProducer | None, float, str]:
    candidates = [canonical(wp.name)] + [canonical(a) for a in wp.aliases]
    candidates = [c for c in candidates if c]
    for c in candidates:
        if c in raeders:
            return raeders[c], 1.0, "exact"
    best, best_score = None, 0.0
    for rp in raeders.values():
        for c in candidates:
            s = SequenceMatcher(None, c, rp.canon).ratio()
            if s > best_score:
                best_score = s
                best = rp
    if best and best_score >= min_score:
        return best, best_score, f"fuzzy({best_score:.2f})"
    return None, best_score, f"no_match(best={best_score:.2f})"


def fmt_scores(c: RaedersCuvee) -> str:
    parts = []
    if c.score_wa: parts.append(f"WA {c.score_wa}")
    if c.score_js: parts.append(f"JS {c.score_js}")
    if c.score_we: parts.append(f"WE {c.score_we}")
    if c.score_ws: parts.append(f"W&S {c.score_ws}")
    return " · ".join(parts) if parts else "—"


def fmt_price(c: RaedersCuvee) -> str:
    if c.price:
        return f"${c.price:.2f}".rstrip("0").rstrip(".")
    return "—"


def build_view(importer: str, min_score: float) -> tuple[str, str]:
    producers = load_wiki_producers()
    book = [p for p in producers if importer in p.importer_us]
    if not book:
        body = (
            f"# {importer} × Raeder's — Cross-Reference\n\n"
            f"_No producers tagged with `importer_us: ['{importer}']` in the "
            f"vault. Harvest the importer's portfolio first (see "
            f"`raw/veritas/_README.md` for the pattern), then re-run._\n"
        )
        fname = f"{safe_filename(importer)}_raeders_xref_{date.today().strftime('%Y-%m')}.md"
        return body, fname

    raeders, csv_path = load_raeders()

    overlap: list[tuple[WikiProducer, RaedersProducer, float, str]] = []
    gaps: list[WikiProducer] = []

    for wp in sorted(book, key=lambda x: x.name.lower()):
        rp, score, reason = match_in_raeders(wp, raeders, min_score)
        if rp is not None:
            overlap.append((wp, rp, score, reason))
        else:
            gaps.append(wp)

    total_cuvees = sum(len(rp.cuvees) for _, rp, _, _ in overlap)

    today = date.today().isoformat()
    month_stamp = date.today().strftime("%Y-%m")
    importer_slug = safe_filename(importer)
    fname = f"{importer_slug}_raeders_xref_{month_stamp}.md"

    lines: list[str] = [
        "---",
        "type: xref_view",
        f'importer: "{importer}"',
        f'source_raeders_csv: "{csv_path.relative_to(VAULT)}"',
        f"book_producer_count: {len(book)}",
        f"overlap_producer_count: {len(overlap)}",
        f"overlap_cuvee_count: {total_cuvees}",
        f"gap_producer_count: {len(gaps)}",
        f"min_fuzzy_score: {min_score}",
        f"updated: {today}",
        "---",
        "",
        f"# {importer} × Raeder's — Cross-Reference",
        "",
        (f"**{len(book)}** producers in the {importer} book tracked in the "
         f"vault. **{len(overlap)}** ({len(overlap)*100//max(len(book),1)}%) "
         f"have a current presence at Raeder's, covering "
         f"**{total_cuvees}** cuvée/vintage listings."),
        "",
        f"_Source: `{csv_path.relative_to(VAULT)}` (matched by canonical "
        f"name; min fuzzy score = {min_score}). Cross-references are by "
        f"`importer_us` on the vault producer pages, not a direct lookup "
        f"of the live importer book._",
        "",
        f"## Overlap — at Raeder's ({len(overlap)} producers, {total_cuvees} cuvées)",
        "",
    ]

    if not overlap:
        lines.append(f"_No {importer} producers currently at Raeder's._")
        lines.append("")
    else:
        lines += [
            "| Producer | Region | Cuvées | Price range | Top vintages | Match |",
            "|---|---|---:|---|---|---|",
        ]
        for wp, rp, score, reason in sorted(
            overlap, key=lambda t: (-len(t[1].cuvees), t[0].name.lower())
        ):
            prices = [c.price for c in rp.cuvees if c.price > 0]
            price_range = (
                f"${min(prices):.0f}–${max(prices):.0f}"
                if prices else "—"
            )
            vintages = sorted({c.vintage for c in rp.cuvees if c.vintage != "NV"})
            top_vint = ", ".join(vintages[-4:]) if vintages else "NV"
            region = wp.region or (next(iter(rp.regions), "") if rp.regions else "—")
            lines.append(
                f"| [[{wp.slug}|{wp.name}]] | {region} | "
                f"{len(rp.cuvees)} | {price_range} | {top_vint} | {reason} |"
            )
        lines += [""]

        lines += [
            f"## Cuvée-level detail",
            "",
        ]
        for wp, rp, score, _ in sorted(
            overlap, key=lambda t: t[0].name.lower()
        ):
            lines.append(f"### [[{wp.slug}|{wp.name}]] — {wp.region or '—'}")
            lines.append("")
            lines.append("| Cuvée | Vintage | Size | Price | Scores |")
            lines.append("|---|---:|---|---:|---|")
            for c in sorted(rp.cuvees, key=lambda c: (
                -(c.score_wa or c.score_js or c.score_we or 0),
                c.cuvee, c.vintage,
            )):
                cuvee_text = c.cuvee or "—"
                link = f"[{cuvee_text}]({c.url})" if c.url else cuvee_text
                lines.append(
                    f"| {link} | {c.vintage} | {c.size} | "
                    f"{fmt_price(c)} | {fmt_scores(c)} |"
                )
            lines.append("")

    lines += [
        f"## Gaps — in book, not at Raeder's ({len(gaps)} producers)",
        "",
    ]
    if not gaps:
        lines.append(f"_Every {importer} producer in the vault is currently at Raeder's._")
        lines.append("")
    else:
        lines += [
            "| Producer | Country | Region |",
            "|---|---|---|",
        ]
        for wp in sorted(gaps, key=lambda x: (x.country, x.region, x.name.lower())):
            lines.append(
                f"| [[{wp.slug}|{wp.name}]] | {wp.country or '—'} | "
                f"{wp.region or '—'} |"
            )
        lines += [""]

    lines += [
        "## Method",
        "",
        f"1. Filter `wiki/producers/*.md` by `importer_us` ∋ `{importer}`.",
        f"2. For each producer, fuzzy-match the canonical name (NFKD ASCII-fold, "
        f"strip `Domaine`/`Château`/`Weingut` prefixes, lowercase) against the "
        f"producer column of `{csv_path.relative_to(VAULT)}`.",
        f"3. Matches with score ≥ {min_score} are treated as a single producer.",
        f"4. Regenerate with `python scripts/build_importer_raeders_xref.py "
        f'"{importer}" --apply`.',
        "",
        "_This view is a snapshot — Raeders inventory rotates. Re-scrape via "
        "`scripts/scrape_raeders.py` + `scripts/parse_raeders_html.py` and "
        "re-run to refresh._",
    ]

    return "\n".join(lines) + "\n", fname


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("importer", help='Importer name as it appears in importer_us, e.g. "Skurnik"')
    ap.add_argument("--apply", action="store_true", help="write to wiki/_views/")
    ap.add_argument("--out", type=Path, help="override output path")
    ap.add_argument("--min-score", type=float, default=0.86)
    args = ap.parse_args()

    body, fname = build_view(args.importer, args.min_score)

    if args.out:
        out_path = args.out
    elif args.apply:
        VIEWS.mkdir(parents=True, exist_ok=True)
        out_path = VIEWS / fname
    else:
        sys.stdout.write(body)
        print(f"\n(preview — would write to wiki/_views/{fname}; pass --apply)",
              file=sys.stderr)
        return 0

    out_path.write_text(body, encoding="utf-8")
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
