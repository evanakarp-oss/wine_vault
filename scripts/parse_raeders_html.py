"""
Parse saved Raeders listing HTML from raw/raeders/html/page_NNN.html into:

  raw/raeders/master_<YYYY-MM-DD>.csv      — one row per bottle
  raw/raeders/markdown/<slug>.md           — one .md per bottle (LLM compile input)

Each card text on a Raeders listing page follows the pattern:

  <Title> | (<size>) | Country: X | Region: Y |
    [Subregion: Z |] Varietal: W |
    Current price: | $N.NN | In Mixed Case: | $M.MM | Qty: | …

Title is "Producer - Cuvée [Vintage]" with vintage at the end (or "NV").
"""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

VAULT = Path(__file__).resolve().parent.parent
HTML_DIR = VAULT / "raw" / "raeders" / "html"
OUT_DIR = VAULT / "raw" / "raeders"
OUT_CSV = OUT_DIR / f"master_{date.today().isoformat()}.csv"
MD_DIR = OUT_DIR / "markdown"


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


@dataclass
class Bottle:
    title: str
    producer: str
    cuvee: str
    vintage: str
    size: str
    country: str
    region: str
    subregion: str
    varietal: str
    wine_type: str          # Red Wine / White Wine / Sparkling / Rosé / Dessert
    score_wa: int           # Wine Advocate
    score_js: int           # James Suckling
    score_we: int           # Wine Enthusiast
    score_w_s: int          # Wine Spectator
    tasting_note: str       # retailer-curated review excerpt, when present
    price_usd: float
    mixed_case_usd: float
    url: str
    product_id: str


def split_title(title: str) -> tuple[str, str, str]:
    """Title looks like 'Producer - Cuvée … 2019' or '… NV'.
    Returns (producer, cuvee, vintage)."""
    # Strip parenthetical size if present
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
    # Trailing vintage
    m = re.search(r"\s+(NV|\d{4})\s*$", title)
    if m:
        vintage = m.group(1)
        title = title[: m.start()].rstrip()
    else:
        vintage = ""
    # Producer / cuvée split on first " - "
    if " - " in title:
        producer, cuvee = title.split(" - ", 1)
    else:
        producer, cuvee = title, ""
    return producer.strip(), cuvee.strip(), vintage


def field(text: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}:\s*([^|]+?)(?=\s*\||\s*$)", text)
    return m.group(1).strip() if m else ""


def money(text: str, label: str) -> float:
    m = re.search(rf"{re.escape(label)}:\s*\|\s*\$([\d,]+\.\d{{2}})", text)
    if not m:
        return 0.0
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return 0.0


def size_of(title: str) -> str:
    m = re.search(r"\(([^)]+)\)\s*$", title)
    return m.group(1) if m else ""


SCORE_LABELS = {
    "WA": "score_wa",
    "WS": "score_w_s",
    "JS": "score_js",
    "WE": "score_we",
}


def extract_scores(text: str) -> dict[str, int]:
    """Parse 'WA | 94 | …' style score callouts."""
    out = {v: 0 for v in SCORE_LABELS.values()}
    for label, key in SCORE_LABELS.items():
        m = re.search(rf"\b{label}\s*\|\s*(\d{{2,3}})\b", text)
        if m:
            try:
                out[key] = int(m.group(1))
            except ValueError:
                pass
    return out


def extract_tasting_note(text: str) -> str:
    """Cards with a review usually look like:
       '… | WA | 94 | <tasting note text> | Read More | Current price: …'
       Pull the chunk between the last score and 'Read More' / 'Current price:'.
    """
    m = re.search(r"\|\s*\d{2,3}\s*\|\s*(.+?)\s*\|\s*(?:Read More|Current price)\s*:", text)
    if not m:
        return ""
    note = m.group(1).strip()
    note = re.sub(r"\s+\|\s+", " ", note).strip()
    return note


def extract_wine_type(card) -> str:
    """Wine type is encoded as an <img alt='Red Wine' …>."""
    img = card.find("img", alt=re.compile(r"\bWine\b"))
    return img.get("alt", "") if img else ""


def parse_card(card) -> Bottle | None:
    a = card.select_one("a.rebl15") or card.select_one("a[href*='/wines/'][href*='-w']")
    if not a:
        return None
    href = a.get("href", "")
    if not href:
        return None
    title_html = a.get_text(" ", strip=True)
    size = size_of(title_html)
    text = card.get_text(" | ", strip=True)
    title_clean = re.sub(r"\s*\|.*$", "", text).strip()
    producer, cuvee, vintage = split_title(title_clean)

    pid_m = re.search(r"-w(\w+)$", href)
    pid = pid_m.group(1) if pid_m else ""

    scores = extract_scores(text)

    return Bottle(
        title=title_clean,
        producer=producer,
        cuvee=cuvee,
        vintage=vintage,
        size=size,
        country=field(text, "Country"),
        region=field(text, "Region"),
        subregion=field(text, "Subregion"),
        varietal=field(text, "Varietal"),
        wine_type=extract_wine_type(card),
        score_wa=scores["score_wa"],
        score_js=scores["score_js"],
        score_we=scores["score_we"],
        score_w_s=scores["score_w_s"],
        tasting_note=extract_tasting_note(text),
        price_usd=money(text, "Current price"),
        mixed_case_usd=money(text, "In Mixed Case"),
        url=f"https://www.raederswine.com{href}",
        product_id=pid,
    )


def render_md(b: Bottle) -> str:
    front = [
        "---",
        "type: raeders_inventory",
        f"product_id: {b.product_id}",
        f'producer: "{b.producer.replace(chr(34), chr(39))}"',
        f"producer_slug: {slug(b.producer)}",
        f'cuvee: "{b.cuvee.replace(chr(34), chr(39))}"',
        f'vintage: "{b.vintage or "NV"}"',
        f'size: "{b.size}"',
        f'country: "{b.country}"',
        f'region: "{b.region}"',
        f'subregion: "{b.subregion}"',
        f'varietal: "{b.varietal}"',
        f'wine_type: "{b.wine_type}"',
        f"score_wa: {b.score_wa}",
        f"score_js: {b.score_js}",
        f"score_we: {b.score_we}",
        f"score_ws: {b.score_w_s}",
        f"price_usd: {b.price_usd:g}",
        f"mixed_case_usd: {b.mixed_case_usd:g}",
        f"url: {b.url}",
        f'fetched: "{date.today().isoformat()}"',
        "---",
        "",
        f"# {b.title}",
        "",
        f"- **Producer:** {b.producer}",
        f"- **Cuvée:** {b.cuvee or '—'}",
        f"- **Vintage:** {b.vintage or 'NV'}",
        f"- **Size:** {b.size}",
    ]
    if b.country or b.region:
        front.append(
            f"- **Origin:** {b.country or '—'}"
            f"{(', ' + b.region) if b.region else ''}"
            f"{(' / ' + b.subregion) if b.subregion else ''}"
        )
    if b.varietal:
        front.append(f"- **Varietal:** {b.varietal}")
    if b.wine_type:
        front.append(f"- **Type:** {b.wine_type}")
    score_parts = []
    for label, val in (("WA", b.score_wa), ("JS", b.score_js),
                       ("WE", b.score_we), ("WS", b.score_w_s)):
        if val:
            score_parts.append(f"{label} {val}")
    if score_parts:
        front.append(f"- **Scores:** {' · '.join(score_parts)}")
    front.append(
        f"- **Price:** ${b.price_usd:g}"
        f"{f' (mixed case ${b.mixed_case_usd:g})' if b.mixed_case_usd else ''}"
    )
    front.append(f"- **Source:** [{b.url}]({b.url})")
    if b.tasting_note:
        front += ["", "## Tasting note (Raeders)", "", f"> {b.tasting_note}", ""]
    else:
        front.append("")
    return "\n".join(front)


def main() -> int:
    if not HTML_DIR.exists() or not list(HTML_DIR.glob("page_*.html")):
        print(f"No HTML found in {HTML_DIR}; run scrape_raeders.py first.")
        return 1
    MD_DIR.mkdir(parents=True, exist_ok=True)

    bottles: list[Bottle] = []
    seen_pids: set[str] = set()
    for p in sorted(HTML_DIR.glob("page_*.html")):
        html = p.read_bytes().decode("cp1252", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".product-list > div")
        for card in cards:
            b = parse_card(card)
            if not b or not b.product_id:
                continue
            if b.product_id in seen_pids:
                continue
            seen_pids.add(b.product_id)
            bottles.append(b)
        print(f"  {p.name}: {len(cards)} cards parsed (running total: {len(bottles)})")

    # CSV
    fields = list(asdict(bottles[0]).keys()) if bottles else []
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for b in bottles:
            w.writerow(asdict(b))

    # Markdown per bottle (slug from product_id, deterministic)
    written_md = 0
    for b in bottles:
        producer_slug = slug(b.producer) or "unknown"
        cuvee_slug = slug(b.cuvee) or "cuvee"
        vintage = b.vintage or "NV"
        fname = f"{producer_slug}__{cuvee_slug}__{vintage}__{b.product_id}.md"
        # Cap filename length to avoid Windows MAX_PATH issues
        if len(fname) > 180:
            fname = fname[:170] + f"__{b.product_id}.md"
        (MD_DIR / fname).write_text(render_md(b), encoding="utf-8")
        written_md += 1

    print(f"\nParsed {len(bottles)} bottles")
    print(f"CSV:  {OUT_CSV}")
    print(f"MD :  {written_md} files in {MD_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
