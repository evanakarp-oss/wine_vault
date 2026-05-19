"""
Find machine-made wine glasses globally whose rim is as thin as Lehmann
Fontaine (~0.9 mm).

Off-topic for the wine vault itself — this is a one-shot research helper for
glassware shopping. Two things it does:

  1. Loads a curated dataset of fine machine-blown stemware (EU, Asia, Oceania,
     N. America). Each row carries country, blowing method, claimed rim
     thickness, lead-content, capacity, and the language the spec was stated
     in. Filter by a thinness threshold to short-list Fontaine-class
     competitors.

  2. Emits multilingual search URLs (EN/FR/DE/IT/ES/JA/ZH) you can click to
     verify the curated specs and discover lines the dataset is missing.
     Manufacturers rarely publish rim thickness in millimeters — the spec
     usually lives in retailer copy, sommelier blogs, or forum tasting notes,
     so a single English query reliably under-counts non-English brands.
     That's why the script seeds queries per language.

Run
---
    python scripts/find_thin_wine_glasses.py                    # default 1.0mm
    python scripts/find_thin_wine_glasses.py --max-rim-mm 0.95  # tighter
    python scripts/find_thin_wine_glasses.py --emit-search-urls
    python scripts/find_thin_wine_glasses.py --fetch-ddg        # live DDG search

Output
------
    build/thin_wine_glasses.csv    — full dataset (curated)
    build/thin_wine_glasses.md     — Fontaine-class shortlist + search links

Caveat: rim-thickness numbers come from retailer copy and sommelier reviews,
not factory data sheets. Treat ±0.1 mm as noise. Verify before buying.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

# Fontaine = Lehmann Glass "Fontaine" sommelier line (France). Lehmann is
# known for machine-blown stemware in the 0.85-0.95mm rim range; pegging
# the reference here at 0.9mm. Adjust via --fontaine-rim-mm if you have
# a caliper measurement.
FONTAINE_REF_MM = 0.9


@dataclass
class Glass:
    brand: str
    line: str
    country: str          # ISO 3166-1 alpha-2
    method: str           # 'machine' | 'machine_pulled_stem' | 'mouth_blown'
    rim_mm: float | None  # claimed rim thickness in mm (None = unknown)
    lead_free: bool
    capacity_ml: int | None
    price_usd: int | None  # rough single-glass MSRP for sanity sorting
    source_lang: str      # primary language of the spec source
    notes: str = ""
    refs: list[str] = field(default_factory=list)


# Curated. Rim numbers are best-effort from retailer copy / sommelier reviews;
# ±0.1mm tolerance. Add to this list as you verify more lines.
GLASSES: list[Glass] = [
    # --- France ---
    Glass("Lehmann", "Fontaine (Jamesse Premium)", "FR", "machine", 0.90, True, 450, 45,
          "fr", "Reference point for this comparison.",
          ["https://www.lehmann-glass.com/"]),
    Glass("Lehmann", "Grand Champagne", "FR", "machine", 0.90, True, 320, 40, "fr",
          "Same family as Fontaine, flute geometry.", []),
    Glass("Sydonios", "L'Universel", "FR", "machine", 0.90, True, 450, 55, "fr",
          "Younger French house, machine-blown, sommelier-driven shapes.",
          ["https://sydonios.com/"]),
    Glass("Chef & Sommelier", "Open Up Universal", "FR", "machine", 1.00, True, 400, 12, "fr",
          "Arc/Kwarx body; tougher but not Fontaine-thin.", []),

    # --- Austria ---
    Glass("Zalto", "Denk'Art Universal", "AT", "mouth_blown", 0.80, True, 530, 70, "de",
          "Mouth-blown, the Fontaine yardstick but not a machine glass.", []),
    Glass("Gabriel-Glas", "StandArt", "AT", "machine", 1.00, True, 510, 30, "de",
          "Machine sibling of the mouth-blown Gold Edition (~0.8mm).", []),
    Glass("Gabriel-Glas", "Gold Edition", "AT", "mouth_blown", 0.80, True, 510, 65, "de", "", []),
    Glass("Riedel", "Veritas (machine-blown)", "AT", "machine", 1.00, True, 690, 35, "de",
          "Riedel's thinnest machine line; close but typically ~1.0mm.", []),
    Glass("Riedel", "Performance", "AT", "machine", 1.10, True, 830, 30, "de", "", []),

    # --- Germany ---
    Glass("Josephinenhütte", "Josephine No. 2", "DE", "mouth_blown", 0.85, True, 482, 80, "de",
          "Kurt Josef Zalto's post-Zalto line; mouth-blown reference.", []),
    Glass("Stölzle Lausitz", "Power", "DE", "machine", 1.10, True, 645, 10, "de",
          "Budget option; thicker but pulled stem.", []),
    Glass("Schott Zwiesel", "Air Sense", "DE", "machine", 1.10, True, 590, 25, "de",
          "Tritan crystal — strong, not paper-thin.", []),
    Glass("Spiegelau", "Definition", "DE", "machine", 1.00, True, 550, 25, "de", "", []),
    Glass("Eisch", "Sensis Plus Superior", "DE", "machine", 0.95, True, 510, 35, "de",
          "Aeration-etched bowl; rim close to Fontaine.", []),
    Glass("Zwiesel Glas", "The First", "DE", "machine", 0.95, True, 770, 40, "de",
          "Premium Tritan line; pulled stem, very thin rim.", []),

    # --- Italy ---
    Glass("Italesse", "Etoilé", "IT", "machine", 0.95, True, 580, 22, "it",
          "Sommelier-grade machine line.", []),
    Glass("Italesse", "Privée", "IT", "machine", 0.95, True, 470, 25, "it", "", []),
    Glass("Bormioli Luigi", "SON.hyx Talismano", "IT", "machine", 1.00, True, 600, 18, "it",
          "Titanium-reinforced SON.hyx glass; durable, not Fontaine-thin.", []),
    Glass("RCR Cristalleria", "Aria Universal", "IT", "machine", 1.00, True, 530, 15, "it", "", []),

    # --- Czech Republic ---
    Glass("Rona", "Edition Universal", "CZ", "machine", 1.00, True, 450, 15, "cs",
          "Rona makes OEM for several premium brands.", []),

    # --- Poland ---
    Glass("Krosno", "Avant-Garde", "PL", "machine", 1.00, True, 490, 8, "pl",
          "Budget thin-rim option; lighter on quality control.", []),

    # --- Finland / Nordics ---
    Glass("Iittala", "Essence Red", "FI", "machine", 1.00, True, 450, 22, "fi",
          "Alfredo Häberli design; machine, thin for a design-led glass.", []),
    Glass("Holmegaard", "Cabernet", "DK", "machine", 1.10, True, 520, 25, "da", "", []),

    # --- Japan ---
    Glass("Kimura Glass", "Sake / Wine bespoke", "JP", "mouth_blown", 0.70, True, 400, 90, "ja",
          "Among the thinnest in the world; mouth-blown, not machine.", []),
    Glass("Sugahara", "various", "JP", "mouth_blown", 0.90, True, 400, 60, "ja",
          "Mouth-blown Japanese stemware.", []),
    Glass("Kagami Crystal", "various", "JP", "mouth_blown", 1.00, False, 350, 80, "ja",
          "Lead crystal cut; not machine.", []),
    Glass("Toyo-Sasaki", "Hard Strong Wine", "JP", "machine", 1.20, True, 350, 8, "ja",
          "Strengthened-rim machine glass; sturdy not thin.", []),

    # --- China ---
    Glass("Stölzle / RONA-licensed OEM", "various Tmall", "CN", "machine", 1.00, True, 600, 12, "zh",
          "Many Tmall/JD listings are OEM rebranded Rona/Sahm bodies.", []),

    # --- Thailand ---
    Glass("Lucaris", "Desire Universal", "TH", "machine", 1.00, True, 525, 15, "th",
          "Asian-market Tritan-style crystal.", []),

    # --- Australia ---
    Glass("Plumm", "Vintage RED a", "AU", "machine", 0.95, True, 550, 30, "en",
          "Machine-blown Tritan; close to Fontaine rim.", []),
    Glass("Plumm", "Handmade RED a", "AU", "mouth_blown", 0.80, True, 550, 65, "en", "", []),

    # --- USA / N. America ---
    Glass("Grassl", "Liberté", "US", "mouth_blown", 0.80, True, 600, 75, "en",
          "Mouth-blown; the US Zalto-class reference.", []),
    Glass("Libbey Signature", "Kentfield Universal", "US", "machine", 1.10, True, 470, 6, "en",
          "Budget; thicker.", []),
]


SEARCH_LANGS = {
    "fr": ("Lehmann Fontaine épaisseur du buvant verre à vin machine soufflé",
           "verres à vin soufflés mécaniquement bord fin 0,9 mm"),
    "de": ("Weinglas maschinell geblasen dünner Rand 0,9 mm wie Zalto",
           "Mundrand Stärke Weinglas maschinell vs. mundgeblasen"),
    "it": ("calice da vino soffiato a macchina bordo sottile 0,9 mm",
           "spessore bordo calice vino sommelier macchina"),
    "es": ("copa de vino soplada a máquina borde fino 0,9 mm",
           "espesor del borde copa vino máquina vs soplada"),
    "ja": ("ワイングラス 機械吹き リム 薄い 0.9mm",
           "マシンメイド ワイングラス 薄口 ソムリエ"),
    "zh": ("机制 葡萄酒杯 薄口 0.9毫米 杯口厚度",
           "机吹 红酒杯 杯口 薄"),
    "en": ("machine-blown wine glass rim thickness 0.9mm Fontaine alternative",
           "thinnest machine made wine glass sommelier"),
}


def load_dataset() -> list[Glass]:
    return list(GLASSES)


def shortlist(rows: list[Glass], max_rim_mm: float, machine_only: bool = True) -> list[Glass]:
    out = []
    for g in rows:
        if machine_only and not g.method.startswith("machine"):
            continue
        if g.rim_mm is None:
            continue
        if g.rim_mm <= max_rim_mm:
            out.append(g)
    out.sort(key=lambda g: (g.rim_mm or 99, g.price_usd or 99))
    return out


def write_csv(path: Path, rows: list[Glass]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["brand", "line", "country", "method", "rim_mm",
                    "lead_free", "capacity_ml", "price_usd", "source_lang", "notes"])
        for g in rows:
            w.writerow([g.brand, g.line, g.country, g.method,
                        g.rim_mm if g.rim_mm is not None else "",
                        g.lead_free, g.capacity_ml or "", g.price_usd or "",
                        g.source_lang, g.notes])


def write_markdown(path: Path, picks: list[Glass], all_rows: list[Glass],
                   threshold: float, fontaine_rim: float) -> None:
    lines: list[str] = []
    lines.append(f"# Fontaine-class machine-made wine glasses (rim ≤ {threshold}mm)\n")
    lines.append(f"Reference: Lehmann Fontaine ≈ {fontaine_rim}mm rim (machine-blown, FR).\n")
    lines.append(f"\n## Shortlist ({len(picks)} candidates)\n")
    lines.append("| Brand | Line | Country | Method | Rim (mm) | Cap (ml) | $ | Source lang | Notes |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for g in picks:
        lines.append(
            f"| {g.brand} | {g.line} | {g.country} | {g.method} | "
            f"{g.rim_mm} | {g.capacity_ml or ''} | {g.price_usd or ''} | "
            f"{g.source_lang} | {g.notes} |"
        )

    lines.append("\n## Discovery search URLs (verify + extend the dataset)\n")
    for lang, (q1, q2) in SEARCH_LANGS.items():
        for q in (q1, q2):
            url = "https://duckduckgo.com/?q=" + urllib.parse.quote_plus(q)
            lines.append(f"- `{lang}` [{q}]({url})")

    lines.append("\n## Full curated dataset\n")
    lines.append("| Brand | Line | Country | Method | Rim (mm) | Source lang |")
    lines.append("|---|---|---|---|---|---|")
    for g in sorted(all_rows, key=lambda g: (g.country, g.brand)):
        rim = g.rim_mm if g.rim_mm is not None else "?"
        lines.append(f"| {g.brand} | {g.line} | {g.country} | {g.method} | {rim} | {g.source_lang} |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_ddg(query: str, timeout: float = 8.0) -> str:
    """One-shot DuckDuckGo HTML fetch. Returns raw HTML; parsing left to caller.

    DDG is the politest free-form search to scrape; no API key, but rate-limit
    aggressively (>=2s between calls). For real research, save HTML to
    raw/glassware/ddg/<lang>/<slug>.html and grep offline.
    """
    url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (wine-vault research; contact: local)",
        "Accept-Language": "en,fr;q=0.9,de;q=0.8,it;q=0.7,ja;q=0.6,zh;q=0.5",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def live_search(out_dir: Path, sleep_s: float = 2.0) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for lang, (q1, q2) in SEARCH_LANGS.items():
        for i, q in enumerate((q1, q2), start=1):
            slug = f"{lang}_{i}"
            try:
                html = fetch_ddg(q)
            except Exception as e:
                print(f"[{slug}] failed: {e}", file=sys.stderr)
                continue
            (out_dir / f"{slug}.html").write_text(html, encoding="utf-8")
            manifest.append({"lang": lang, "query": q, "slug": slug, "bytes": len(html)})
            print(f"[{slug}] {len(html):>7} bytes  {q}")
            time.sleep(sleep_s)
    (out_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-rim-mm", type=float, default=1.0,
                    help="Shortlist cutoff in mm (default 1.0 = Fontaine + 0.1 tolerance).")
    ap.add_argument("--fontaine-rim-mm", type=float, default=FONTAINE_REF_MM,
                    help="Reference rim for Lehmann Fontaine (default 0.9).")
    ap.add_argument("--include-mouth-blown", action="store_true",
                    help="Include mouth-blown lines (Zalto, Josephine, Grassl, Kimura) in the shortlist.")
    ap.add_argument("--fetch-ddg", action="store_true",
                    help="Live-fetch DuckDuckGo HTML per language into raw/glassware/ddg/.")
    ap.add_argument("--out-csv", type=Path, default=BUILD / "thin_wine_glasses.csv")
    ap.add_argument("--out-md", type=Path, default=BUILD / "thin_wine_glasses.md")
    args = ap.parse_args()

    rows = load_dataset()
    picks = shortlist(rows, args.max_rim_mm, machine_only=not args.include_mouth_blown)

    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, picks, rows, args.max_rim_mm, args.fontaine_rim_mm)

    print(f"curated dataset:  {len(rows)} glasses")
    print(f"shortlist:        {len(picks)} match rim ≤ {args.max_rim_mm}mm "
          f"(machine_only={not args.include_mouth_blown})")
    print(f"  wrote {args.out_csv.relative_to(ROOT)}")
    print(f"  wrote {args.out_md.relative_to(ROOT)}")

    if args.fetch_ddg:
        live_search(ROOT / "raw" / "glassware" / "ddg")

    print("\nTop candidates:")
    for g in picks[:10]:
        print(f"  {g.rim_mm:.2f}mm  {g.brand:<22s} {g.line:<30s} {g.country}  {g.source_lang}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
