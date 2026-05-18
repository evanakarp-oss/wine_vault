"""
Second LLM-curated decision pass for Raeders, narrowed by Evan's filters:

  1. Bordeaux: WK-style undercovered/value with great farming (no first-growth
     unless aged & a benchmark vintage)
  2. Champagne: only aged vintage cuvees / late-disgorged / grower
  3. Napa: true cult tier only (Harlan/Hundred Acre/Ridge MB/Bond/Colgin/SQN/Schrader/
     Screaming Eagle), not generic $250 Cab

Run AFTER scripts/compile_raeders.py + compile_raeders_creates.py.
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


def fmt_price(p: float) -> str:
    if p == 0: return "—"
    return f"${int(p):,}" if p == int(p) else f"${p:,.2f}"


# Decisions: each entry = the canonical name + region/farming hints.
# `match_keys` lets us include multiple Raeders spelling variants under one slug.
CURATED: list[dict] = [
    # ---- Bordeaux WK-style value / great farming ----
    {"name": "Château Phélan-Ségur", "match": ["chateau_phelan_segur"],
     "country": "France", "region": "Bordeaux", "sub_region": "Saint-Estèphe",
     "farming": ["sustainable"], "tags": ["bordeaux", "saint-estephe", "value", "wk-coverage"],
     "summary": "Saint-Estèphe value benchmark; Daniel Gardère consulted, Berrouet legacy. WK pick for terroir-driven Médoc at non-classed prices."},
    {"name": "Château Calon-Ségur", "match": ["chateau_calon_segur"],
     "country": "France", "region": "Bordeaux", "sub_region": "Saint-Estèphe",
     "farming": ["sustainable"], "tags": ["bordeaux", "saint-estephe", "wk-coverage"],
     "summary": "Saint-Estèphe 3rd-growth, Suravenir-owned since 2012, sustainable farming. Strong recent vintages and aged value."},
    {"name": "Château Cantemerle", "match": ["chateau_cantemerle"],
     "country": "France", "region": "Bordeaux", "sub_region": "Haut-Médoc",
     "farming": [], "tags": ["bordeaux", "haut-medoc", "value", "wk-coverage"],
     "summary": "Haut-Médoc 5th-growth; classic WK 'undercovered Bordeaux' shoutout. Value claret with aging chops."},
    {"name": "Château Smith-Haut-Lafitte", "match": ["chateau_smith_haut_lafitte", "chateau_smith-haut-lafitte"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pessac-Léognan",
     "farming": ["organic", "biodynamic"], "tags": ["bordeaux", "pessac-leognan", "biodynamic", "wk-coverage"],
     "summary": "Cathiard-owned Pessac estate; certified biodynamic, especially celebrated for the white. WK biodynamic-Bordeaux flag-bearer."},
    {"name": "Château Pibran", "match": ["chateau_pibran"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pauillac",
     "farming": ["sustainable"], "tags": ["bordeaux", "pauillac", "value", "wk-coverage"],
     "summary": "AXA-owned Pauillac in Pichon Baron's stable. WK value pick for entry-level Pauillac with classed pedigree."},
    {"name": "Château Haut-Bailly", "match": ["chateau_haut_bailly", "chateau_haut-bailly"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pessac-Léognan",
     "farming": ["sustainable"], "tags": ["bordeaux", "pessac-leognan", "wk-coverage"],
     "summary": "Pessac-Léognan classed-growth; Wilmers family, since 2021 Robert Vifian as winemaker. Quietly excellent."},
    {"name": "Château Rauzan-Ségla", "match": ["chateau_rauzan_segla", "chateau_rauzan-segla"],
     "country": "France", "region": "Bordeaux", "sub_region": "Margaux",
     "farming": ["organic"], "tags": ["bordeaux", "margaux", "wk-coverage"],
     "summary": "Margaux 2nd-growth, Wertheimer (Chanel) ownership. Organic conversion; reputation rising under recent administration."},
    {"name": "Château Léoville Barton", "match": ["chateau_leoville_barton"],
     "country": "France", "region": "Bordeaux", "sub_region": "Saint-Julien",
     "farming": ["sustainable"], "tags": ["bordeaux", "saint-julien", "value", "wk-coverage"],
     "summary": "Saint-Julien 2nd-growth; Anthony Barton legacy, traditional vinification. WK long-running 'best-value classed-growth' pick."},
    {"name": "Château Pape Clément", "match": ["chateau_pape_clement"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pessac-Léognan",
     "farming": ["organic"], "tags": ["bordeaux", "pessac-leognan", "organic"],
     "summary": "Bernard Magrez-owned Pessac estate, certified organic. Both colors; reds carry well, whites are textured."},
    {"name": "Château Lynch-Bages", "match": ["chateau_lynch_bages"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pauillac",
     "farming": ["sustainable"], "tags": ["bordeaux", "pauillac"],
     "summary": "5th-growth Pauillac; Cazes family. Reliable across vintages, often best-value Pauillac aged."},
    {"name": "Château Gruaud-Larose", "match": ["chateau_gruaud_larose", "chateau_gruaud-larose"],
     "country": "France", "region": "Bordeaux", "sub_region": "Saint-Julien",
     "farming": [], "tags": ["bordeaux", "saint-julien", "aged"],
     "summary": "Saint-Julien 2nd-growth. 1980s-90s vintages drink beautifully today; modern era inconsistent but the older stuff is benchmark."},
    {"name": "Château Ducru-Beaucaillou", "match": ["chateau_ducru-beaucaillou", "chateau_ducru_beaucaillou"],
     "country": "France", "region": "Bordeaux", "sub_region": "Saint-Julien",
     "farming": [], "tags": ["bordeaux", "saint-julien"],
     "summary": "Saint-Julien 2nd-growth, Borie family. Renowned for elegance and aging trajectory."},

    # Aged classed-growth icons (drink-window only)
    {"name": "Château Lafite Rothschild", "match": ["chateau_lafite_rothschild"],
     "country": "France", "region": "Bordeaux", "sub_region": "Pauillac",
     "farming": [], "tags": ["bordeaux", "pauillac", "first-growth", "aged-only"],
     "summary": "Pauillac 1st-growth. Tracked here for aged drink-now bottles only — current vintages out of scope for this wiki's focus."},
    {"name": "Château Palmer", "match": ["chateau_palmer"],
     "country": "France", "region": "Bordeaux", "sub_region": "Margaux",
     "farming": ["biodynamic"], "tags": ["bordeaux", "margaux", "biodynamic"],
     "summary": "Margaux 3rd-growth (drinks at 1st-growth level). Certified biodynamic since 2013 — major signal in classed-growth Bordeaux."},

    # ---- Aged Champagne ----
    {"name": "Louis Roederer", "match": ["louis_roederer"],
     "country": "France", "region": "Champagne", "sub_region": "",
     "farming": ["biodynamic"], "tags": ["champagne", "biodynamic", "aged"],
     "summary": "Family-owned grande maison, certified biodynamic across estate vineyards. Cristal vintage and the regular Brut Vintage are the entries to track."},
    {"name": "Dom Pérignon", "match": ["dom_perignon"],
     "country": "France", "region": "Champagne", "sub_region": "",
     "farming": [], "tags": ["champagne", "vintage-only", "aged", "p2"],
     "summary": "LVMH prestige; only ever vintage. P2 (15+ years on lees) and P3 (40+) are the aged plays. Skip the standard Brut releases."},
    {"name": "Bollinger", "match": ["bollinger"],
     "country": "France", "region": "Champagne", "sub_region": "",
     "farming": [], "tags": ["champagne", "vintage", "rd"],
     "summary": "Pinot-driven Aÿ house. Grande Année (vintage) and R.D. (late-disgorged) are the aged cuvees worth seeking."},
    {"name": "Taittinger", "match": ["taittinger"],
     "country": "France", "region": "Champagne", "sub_region": "",
     "farming": [], "tags": ["champagne", "blanc-de-blancs", "aged"],
     "summary": "Reims house; Comtes de Champagne (vintage Blanc de Blancs) is the only cuvée to track here."},
    {"name": "Pierre Peters", "match": ["pierre_peters"],
     "country": "France", "region": "Champagne", "sub_region": "Le Mesnil-sur-Oger",
     "farming": ["sustainable"], "tags": ["champagne", "grower-champagne", "blanc-de-blancs", "wk-coverage"],
     "summary": "Le Mesnil-sur-Oger grower, all Chardonnay. WK-celebrated grower champagne; Les Chétillons single-vineyard is the masterpiece."},

    # ---- Napa cult tier ----
    {"name": "Sine Qua Non", "match": ["sine_qua_non"],
     "country": "United States", "region": "California", "sub_region": "Ventura / Central Coast",
     "farming": ["organic"], "tags": ["california", "cult", "rhone-style", "syrah", "grenache"],
     "summary": "Manfred Krankl's allocation-only cult; Rhône-style Syrah/Grenache + Patine white. Each bottling has its own name and label."},
    {"name": "Hundred Acre", "match": ["hundred_acre"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley",
     "farming": [], "tags": ["napa", "cult", "cabernet-sauvignon"],
     "summary": "Jayson Woodbridge's Napa Cab cult. Tightly allocated; Fortunate Son and the dreamer/warrior labels here."},
    {"name": "Schrader Cellars", "match": ["schrader", "schrader_cellars"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley (Beckstoffer To Kalon)",
     "farming": [], "tags": ["napa", "to-kalon", "cult", "cabernet-sauvignon"],
     "summary": "Fred Schrader's Napa Cab program. Beckstoffer To Kalon-bottlings are the cult tier; Double Diamond is the entry-level (skip for cult focus)."},
    {"name": "Screaming Eagle", "match": ["screaming_eagle"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley (Oakville)",
     "farming": [], "tags": ["napa", "oakville", "cult", "cabernet-sauvignon"],
     "summary": "The original Napa cult Cab. Allocation only. The Flight (second wine) and Sauv Blanc occasionally surface at retail."},
    {"name": "Bryant Family Vineyard", "match": ["bryant_family", "bryant_family_vineyard"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley (Pritchard Hill)",
     "farming": [], "tags": ["napa", "pritchard-hill", "cult", "cabernet-sauvignon"],
     "summary": "Pritchard Hill cult; small production, allocation-driven. Aged bottles offer the best value for non-list buyers."},
    {"name": "Colgin", "match": ["colgin"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley (Pritchard Hill)",
     "farming": [], "tags": ["napa", "pritchard-hill", "cult"],
     "summary": "Ann Colgin's Pritchard Hill cult; LVMH partnership. IX Estate Red and Cariad are the prestige cuvees."},
    {"name": "Futo Estate", "match": ["futo_estate", "futo"],
     "country": "United States", "region": "California", "sub_region": "Napa Valley (Stags Leap District / Oakville)",
     "farming": ["sustainable"], "tags": ["napa", "stags-leap", "cult"],
     "summary": "Tom & Kyle Futo's small-production Napa Cab. Cohn-Diamond Mountain and Stags Leap blocks. Quiet cult."},
]


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

    # vintages list for header context
    vints = sorted({r["vintage"] for r in rows if r.get("vintage")})

    fm = [
        "---",
        "type: producer",
        f'name: "{name}"',
        f"slug: {sl}",
        f"aliases: {[r['producer'] for r in rows if r['producer'] != name][:3] or '[]'}".replace("'[]'", "[]"),
        f'country: "{spec["country"]}"',
        f'region: "{spec["region"]}"',
        f'sub_region: "{spec.get("sub_region", "")}"',
        "appellations: []",
        f"farming: {spec.get('farming', [])}",
        "certifications: []",
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
        '_sources: ["raeders_compile_curated_v2:2026-04-25"]',
        "---",
        "",
        f"# {name}",
        "",
        f"_{spec.get('summary', 'LLM-curated entry from Raeders compile pass.')}_",
        "",
        "## CSW Write-ups",
        "",
        "_Pending — re-run `ingest_csw.py` after creation to pick up Chambers articles._",
        "",
        "## Down to Earth Wines (Panzer)",
        "",
        "_Not yet populated._",
        "",
        "## Raeder's",
        "",
        f"Currently tracked at Raeders: **{len(rows)} cuvée/vintage entries**; "
        f"prices {fmt_price(pmin)}–{fmt_price(pmax)}.",
        "",
        f"Vintages on offer: {', '.join(vints)}.",
        "",
        "| Cuvée | Vintage | Size | Price | Scores |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda x: -(float(x.get("price_usd") or 0))):
        scores = []
        for k, lab in (("score_wa", "WA"), ("score_js", "JS"),
                        ("score_we", "WE"), ("score_ws", "WS")):
            try:
                v = int(r.get(k) or 0)
                if v: scores.append(f"{lab} {v}")
            except (ValueError, TypeError): pass
        score_str = " · ".join(scores) if scores else "—"
        fm.append(
            f"| {(r.get('cuvee') or '—').replace('|', '/')} | "
            f"{r.get('vintage') or 'NV'} | {r.get('size') or '—'} | "
            f"{fmt_price(float(r.get('price_usd') or 0))} | {score_str} |"
        )
    fm.append("")

    # Tasting notes section
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
                except (ValueError, TypeError): pass
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
    grouped = defaultdict(list)
    with RAW_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            grouped[slug(row["producer"] or "")].append(row)

    created, skipped = [], []
    for spec in CURATED:
        target_slug = slug(spec["name"])
        path = PRODUCERS / f"{target_slug}.md"
        if path.exists():
            skipped.append((target_slug, "exists"))
            continue
        # Combine bottles from all match keys
        rows = []
        for k in spec.get("match", [target_slug]):
            rows.extend(grouped.get(k, []))
        # Also include exact-slug match
        if target_slug not in spec.get("match", []):
            rows.extend(grouped.get(target_slug, []))
        # Dedupe on product_id
        seen = set()
        unique_rows = []
        for r in rows:
            pid = r.get("product_id", "")
            if pid in seen: continue
            seen.add(pid)
            unique_rows.append(r)
        if not unique_rows:
            skipped.append((target_slug, "no_raw_match"))
            continue
        path.write_text(render_page(spec, unique_rows), encoding="utf-8")
        created.append((target_slug, len(unique_rows)))
    print(f"Created: {len(created)}")
    for s, n in created: print(f"  + {s}  ({n} bottles)")
    print(f"Skipped: {len(skipped)}")
    for s, why in skipped: print(f"  - {s}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
