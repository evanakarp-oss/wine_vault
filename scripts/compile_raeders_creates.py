"""
LLM-curated decision pass: create wiki/producers/ entries for notable
terroir-driven producers that Raeders carries but the wiki doesn't yet have.

Each entry's `_sources: ["raeders_compile_curated"]` flags it as LLM-curated
during this session. Frontmatter pre-populates region/farming hints based on
known producer profile so they aren't blank when first viewed.

Run AFTER scripts/compile_raeders.py (so the auto-applies have happened).
This step *only adds* new pages — it doesn't touch existing ones.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
RAW_CSV = sorted((VAULT / "raw" / "raeders").glob("master_*.csv"))[-1]


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


# (raeders_name, target_slug, country, region, sub_region, farming, importer, tags, notes)
# This is the LLM-curated decision table. Each entry was judged for: terroir
# orientation, multi-bottle Raeders presence, fit with Evan's collector profile
# (terroir-driven, NYC retailers, German biodynamic + US boutique + Italian
# Friuli/Piedmont leaning).
CURATED_NEW: list[dict] = [
    # --- Piedmont icons ---
    {"name": "Gaja", "country": "Italy", "region": "Piedmont",
     "sub_region": "Barbaresco / Barolo", "farming": ["sustainable"],
     "tags": ["nebbiolo", "piedmont", "icon"]},
    {"name": "Elvio Cogno", "country": "Italy", "region": "Piedmont",
     "sub_region": "Barolo (Novello)", "farming": ["organic"],
     "tags": ["nebbiolo", "barolo", "old-vines"]},
    # --- Brunello / Tuscany ---
    {"name": "Biondi-Santi", "country": "Italy", "region": "Tuscany",
     "sub_region": "Brunello di Montalcino", "farming": ["sustainable"],
     "tags": ["sangiovese", "brunello", "icon", "aged-release"]},
    {"name": "Altesino", "country": "Italy", "region": "Tuscany",
     "sub_region": "Brunello di Montalcino", "farming": [],
     "tags": ["sangiovese", "brunello"]},
    # --- Veneto ---
    {"name": "Dal Forno Romano", "country": "Italy", "region": "Veneto",
     "sub_region": "Valpolicella", "farming": [],
     "tags": ["amarone", "valpolicella", "cult"]},
    # --- Burgundy ---
    {"name": "Domaine Leflaive", "country": "France", "region": "Burgundy",
     "sub_region": "Puligny-Montrachet", "farming": ["biodynamic"],
     "importer_us": ["Wilson Daniels"],
     "tags": ["chardonnay", "white-wine-focused", "biodynamic", "icon"]},
    {"name": "Méo-Camuzet", "country": "France", "region": "Burgundy",
     "sub_region": "Vosne-Romanée", "farming": ["sustainable"],
     "tags": ["pinot-noir", "burgundy"]},
    {"name": "Ramonet", "country": "France", "region": "Burgundy",
     "sub_region": "Chassagne-Montrachet", "farming": [],
     "tags": ["chardonnay", "white-wine-focused", "burgundy"]},
    {"name": "Michel Niellon", "country": "France", "region": "Burgundy",
     "sub_region": "Chassagne-Montrachet", "farming": [],
     "tags": ["chardonnay", "white-wine-focused", "burgundy"]},
    {"name": "Lucien Boillot", "country": "France", "region": "Burgundy",
     "sub_region": "Gevrey-Chambertin", "farming": [],
     "tags": ["pinot-noir", "burgundy"]},
    {"name": "Louis Latour", "country": "France", "region": "Burgundy",
     "sub_region": "Beaune", "farming": [],
     "tags": ["pinot-noir", "chardonnay", "négociant"]},
    {"name": "Domaine Laroche", "country": "France", "region": "Burgundy",
     "sub_region": "Chablis", "farming": ["sustainable"],
     "tags": ["chardonnay", "chablis"]},
    # --- Châteauneuf ---
    {"name": "Domaine de Beaurenard", "country": "France", "region": "Rhône",
     "sub_region": "Châteauneuf-du-Pape", "farming": ["biodynamic"],
     "tags": ["grenache", "chateauneuf", "biodynamic"]},
    # --- Bordeaux (yes, even though sparse — these are the iconic ones) ---
    {"name": "Domaine de Chevalier", "country": "France", "region": "Bordeaux",
     "sub_region": "Pessac-Léognan", "farming": ["sustainable"],
     "tags": ["bordeaux", "pessac-leognan", "classed-growth"]},
    # --- US boutique (matches Evan's existing cellar leanings) ---
    {"name": "Kosta Browne", "country": "United States", "region": "California",
     "sub_region": "Sonoma Coast", "farming": [],
     "tags": ["pinot-noir", "california", "cult"]},
    {"name": "Bergstrom", "country": "United States", "region": "California",
     "sub_region": "Willamette Valley (Oregon)", "farming": ["biodynamic"],
     "tags": ["pinot-noir", "oregon", "biodynamic"]},
    {"name": "Lewis Cellars", "country": "United States", "region": "California",
     "sub_region": "Napa Valley", "farming": [],
     "tags": ["napa", "cabernet-sauvignon"]},
]


def load_raw_grouped() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    with RAW_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            grouped[slug(row["producer"] or "")].append(row)
    return grouped


def fmt_price(p: float) -> str:
    if p == 0: return "—"
    return f"${int(p):,}" if p == int(p) else f"${p:,.2f}"


def render_page(spec: dict, rows: list[dict]) -> str:
    name = spec["name"]
    sl = slug(name)
    prices = []
    for r in rows:
        try:
            v = float(r.get("price_usd") or 0)
            if v > 0: prices.append(v)
        except ValueError: pass
    pmin = min(prices) if prices else 0
    pmax = max(prices) if prices else 0

    fm = [
        "---",
        "type: producer",
        f'name: "{name}"',
        f"slug: {sl}",
        f"aliases: []",
        f'country: "{spec["country"]}"',
        f'region: "{spec["region"]}"',
        f'sub_region: "{spec.get("sub_region", "")}"',
        f"appellations: []",
        f"farming: {spec.get('farming', [])}",
        f"certifications: []",
        f"importer_us: {spec.get('importer_us', [])}",
        "retailers:",
        "  chambers:",
        "    championed: false",
        "    article_count: 0",
        "    dedicated_count: 0",
        "    first_year: 0",
        "    last_year: 0",
        "  dte:",
        "    in_portfolio: false",
        "    cuvee_count: 0",
        "    price_min: 0",
        "    price_max: 0",
        "  raeders:",
        "    in_portfolio: true",
        f"    cuvee_count: {len(rows)}",
        f"    price_min: {int(pmin) if pmin == int(pmin) else pmin:g}",
        f"    price_max: {int(pmax) if pmax == int(pmax) else pmax:g}",
        "  fass:",
        "    in_portfolio: false",
        f"tags: {spec.get('tags', [])}",
        '_sources: ["raeders_compile_curated:2026-04-25"]',
        "---",
        "",
        f"# {name}",
        "",
        "_Created from Raeders compile pass — "
        "LLM-curated as a notable terroir-driven producer worth tracking. "
        "Editorial summary still to be written._",
        "",
        "## CSW Write-ups",
        "",
        "_Not yet covered in CSW archive sweep._",
        "",
        "## Down to Earth Wines (Panzer)",
        "",
        "_Not yet populated._",
        "",
    ]
    # Raeder's section
    fm.append("## Raeder's")
    fm.append("")
    fm.append(
        f"Currently tracked at Raeders: **{len(rows)} cuvée/vintage entries**; "
        f"prices {fmt_price(pmin)}–{fmt_price(pmax)}."
    )
    fm.append("")
    fm.append("| Cuvée | Vintage | Size | Price | Scores |")
    fm.append("|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: -(float(x.get("price_usd") or 0))):
        scores = []
        for k, lab in (("score_wa", "WA"), ("score_js", "JS"),
                        ("score_we", "WE"), ("score_ws", "WS")):
            try:
                v = int(r.get(k) or 0)
                if v: scores.append(f"{lab} {v}")
            except ValueError: pass
        score_str = " · ".join(scores) if scores else "—"
        fm.append(
            f"| {(r.get('cuvee') or '—').replace('|', '/')} | "
            f"{r.get('vintage') or 'NV'} | {r.get('size') or '—'} | "
            f"{fmt_price(float(r.get('price_usd') or 0))} | {score_str} |"
        )
    fm.append("")

    # Notes section if any tasting notes
    notes_rows = [r for r in rows if (r.get("tasting_note") or "").strip()]
    if notes_rows:
        notes_rows.sort(
            key=lambda x: -(int(x.get("score_wa") or 0)
                            + int(x.get("score_js") or 0)
                            + int(x.get("score_we") or 0))
        )
        fm.append("## Raeders Notes")
        fm.append("")
        for r in notes_rows[:5]:
            scores = []
            for k, lab in (("score_wa", "WA"), ("score_js", "JS"),
                            ("score_we", "WE"), ("score_ws", "WS")):
                try:
                    v = int(r.get(k) or 0)
                    if v: scores.append(f"{lab} {v}")
                except ValueError: pass
            score_str = f" ({' · '.join(scores)})" if scores else ""
            fm.append(f"### {(r.get('cuvee') or name)} {r.get('vintage') or ''}{score_str}")
            fm.append("")
            note = re.sub(r"\.{3}\s*Read More\s*$", "…",
                          (r.get("tasting_note") or "")).strip()
            fm.append(f"> {note}")
            fm.append("")
            fm.append(f"_[Raeders link]({r.get('url') or ''})_")
            fm.append("")

    fm.append("## FASS")
    fm.append("")
    fm.append("_Not yet populated._")
    fm.append("")
    return "\n".join(fm)


def main() -> int:
    grouped = load_raw_grouped()
    created, skipped = [], []
    for spec in CURATED_NEW:
        sl = slug(spec["name"])
        path = PRODUCERS / f"{sl}.md"
        if path.exists():
            skipped.append((sl, "exists"))
            continue
        rows = grouped.get(sl, [])
        if not rows:
            skipped.append((sl, "no_raw_match"))
            continue
        path.write_text(render_page(spec, rows), encoding="utf-8")
        created.append(sl)
    print(f"Created: {len(created)}")
    for s in created: print(f"  + {s}")
    print(f"Skipped: {len(skipped)}")
    for s, why in skipped: print(f"  - {s}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
