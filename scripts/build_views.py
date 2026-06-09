"""
Build cross-source gap-analysis + drink-urgency views from the vault.

Three regenerable outputs in `wiki/_views/`:

  1. gap_csw_championed.md
       Producers with CSW dedicated coverage (★) that Evan does NOT own.
       The "buy next from CSW's editorial backbone" list.

  2. gap_raeders_aged_value.md
       Aged Raeders bottles (vintage ≤ current_year - 8) on producers Evan
       doesn't own and that fit his curation taste (WK-flagged, biodynamic,
       grower-champagne, or already wiki-tracked). The "buy next from Raeders'
       overlooked aged stock" list.

  3. drink_window_due.md
       Cellar bottles bucketed by drink-window urgency:
         - PAST WINDOW (end_year < current_year)
         - DRINKING NOW (start ≤ current_year ≤ end)
         - ENTERING WINDOW (start_year in next 2 years)
         - LONG HOLD (start > current_year + 5)

Idempotent. Re-run after any ingest/compile pass.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
CELLAR = VAULT / "cellar"
VIEWS = VAULT / "wiki" / "_views"
RAEDERS_DIR = VAULT / "raw" / "raeders"

CURRENT_YEAR = date.today().year
AGED_THRESHOLD = CURRENT_YEAR - 8       # vintage ≤ this year = "aged" for our purposes
ENTERING_HORIZON = 2                    # bottles whose window starts in next N years


# --- frontmatter helpers ---

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_fm(text: str):
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', m.group(1)):
        v = next((x for x in part if x), "").strip()
        if v: out.append(v)
    return out


def get_int_under(fm: str, block: str, key: str) -> int:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(\d+)"
    m = re.search(pat, fm, re.MULTILINE)
    return int(m.group(1)) if m else 0


def get_bool_under(fm: str, block: str, key: str) -> bool:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(true|false)"
    m = re.search(pat, fm, re.MULTILINE)
    return bool(m) and m.group(1) == "true"


def parse_year_or_null(s: str) -> int | None:
    s = s.strip()
    if not s or s == "null" or s == "0":
        return None
    try:
        return int(s)
    except ValueError:
        return None


# --- producers ---

@dataclass
class Producer:
    slug: str
    name: str
    country: str = ""
    region: str = ""
    sub_region: str = ""
    farming: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    ch_articles: int = 0
    ch_dedicated: int = 0
    ch_first: int = 0
    ch_last: int = 0
    raeders_in: bool = False
    raeders_cuvees: int = 0
    raeders_max: int = 0
    dte_in: bool = False
    fass_in: bool = False


def load_producers() -> dict[str, Producer]:
    out: dict[str, Producer] = {}
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_fm(text)
        if not parts: continue
        fm, _ = parts
        if get_str(fm, "type") != "producer": continue
        slug = get_str(fm, "slug") or p.stem
        out[slug] = Producer(
            slug=slug,
            name=get_str(fm, "name") or slug,
            country=get_str(fm, "country"),
            region=get_str(fm, "region"),
            sub_region=get_str(fm, "sub_region"),
            farming=get_list(fm, "farming"),
            tags=get_list(fm, "tags"),
            ch_articles=get_int_under(fm, "chambers", "article_count"),
            ch_dedicated=get_int_under(fm, "chambers", "dedicated_count"),
            ch_first=get_int_under(fm, "chambers", "first_year"),
            ch_last=get_int_under(fm, "chambers", "last_year"),
            raeders_in=get_bool_under(fm, "raeders", "in_portfolio"),
            raeders_cuvees=get_int_under(fm, "raeders", "cuvee_count"),
            raeders_max=get_int_under(fm, "raeders", "price_max"),
            dte_in=get_bool_under(fm, "dte", "in_portfolio"),
            fass_in=get_bool_under(fm, "fass", "in_portfolio"),
        )
    return out


# --- cellar ---

@dataclass
class CellarBottle:
    stem: str
    producer_slug: str
    producer: str
    cuvee: str
    vintage: str
    qty: int
    size: str
    drink_start: int | None
    drink_end: int | None
    price: float


def load_cellar() -> tuple[set[str], list[CellarBottle]]:
    slugs: set[str] = set()
    bottles: list[CellarBottle] = []
    for p in CELLAR.glob("*.md"):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_fm(text)
        if not parts: continue
        fm, _ = parts
        if get_str(fm, "type") != "cellar_entry": continue
        slug = get_str(fm, "producer_slug")
        if slug:
            slugs.add(slug)
        try: qty = int(get_str(fm, "quantity"))
        except ValueError: qty = 0
        try: price = float(get_str(fm, "purchase_price_usd"))
        except ValueError: price = 0.0
        bottles.append(CellarBottle(
            stem=p.stem,
            producer_slug=slug,
            producer=get_str(fm, "producer"),
            cuvee=get_str(fm, "cuvee"),
            vintage=get_str(fm, "vintage"),
            qty=qty,
            size=get_str(fm, "bottle_size"),
            drink_start=parse_year_or_null(get_str(fm, "drink_window_start")),
            drink_end=parse_year_or_null(get_str(fm, "drink_window_end")),
            price=price,
        ))
    return slugs, bottles


# --- raeders ---

@dataclass
class RaedersBottle:
    producer: str
    producer_slug: str
    cuvee: str
    vintage: str
    vintage_int: int
    size: str
    region: str
    country: str
    price: float
    score_wa: int
    score_js: int
    score_we: int
    url: str
    has_score: bool


def slug(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def load_raeders() -> list[RaedersBottle]:
    csvs = sorted(RAEDERS_DIR.glob("master_*.csv"))
    if not csvs:
        return []
    bottles: list[RaedersBottle] = []
    with csvs[-1].open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            try: v = int(row.get("vintage") or "")
            except ValueError: v = 0
            try: price = float(row.get("price_usd") or 0)
            except ValueError: price = 0.0
            sw = int(row.get("score_wa") or 0) if (row.get("score_wa") or "").isdigit() else 0
            sj = int(row.get("score_js") or 0) if (row.get("score_js") or "").isdigit() else 0
            sn = int(row.get("score_we") or 0) if (row.get("score_we") or "").isdigit() else 0
            bottles.append(RaedersBottle(
                producer=row.get("producer", ""),
                producer_slug=slug(row.get("producer", "")),
                cuvee=row.get("cuvee", ""),
                vintage=row.get("vintage", ""),
                vintage_int=v,
                size=row.get("size", ""),
                region=row.get("region", ""),
                country=row.get("country", ""),
                price=price,
                score_wa=sw,
                score_js=sj,
                score_we=sn,
                url=row.get("url", ""),
                has_score=bool(sw or sj or sn),
            ))
    return bottles


# --- view builders ---

def fmt_price(p: float) -> str:
    if p == 0: return "—"
    return f"${int(p):,}" if p == int(p) else f"${p:,.2f}"


def view_csw_gap(producers: dict[str, Producer], owned: set[str]) -> str:
    """CSW dedicated-coverage producers Evan doesn't own."""
    candidates = [p for p in producers.values()
                  if p.ch_dedicated >= 1 and p.slug not in owned]
    candidates.sort(key=lambda p: (-p.ch_dedicated, -p.ch_articles, p.name.lower()))

    lines = [
        "---",
        "type: gap_view",
        f"updated: {date.today().isoformat()}",
        f"producer_count: {len(candidates)}",
        "---",
        "",
        "# Gap: CSW Champions You Don't Own",
        "",
        f"**{len(candidates)} producers** with CSW dedicated articles (★) that aren't in your cellar. ",
        "These are CSW's editorial picks — the producers Chambers thinks deserve their own essay. Sorted by ★ count.",
        "",
        "Columns: ★ dedicated · total CSW articles · year span · also at retailers · sub-region.",
        "",
        "| Producer | Region | ★ | Articles | Span | Raeders | DTE | FASS |",
        "|---|---|---:|---:|---|:-:|:-:|:-:|",
    ]
    for p in candidates[:80]:
        span = ""
        if p.ch_first or p.ch_last:
            span = f"{p.ch_first or '?'}–{p.ch_last or '?'}"
        sub = p.sub_region or p.region or "—"
        lines.append(
            f"| [[{p.slug}|{p.name}]] | {sub} ({p.country}) | "
            f"{p.ch_dedicated} | {p.ch_articles} | {span} | "
            f"{'✓' if p.raeders_in else '—'} | "
            f"{'✓' if p.dte_in else '—'} | "
            f"{'✓' if p.fass_in else '—'} |"
        )
    if len(candidates) > 80:
        lines.append("")
        lines.append(f"_… and {len(candidates) - 80} more with ★ coverage._")
    lines.append("")
    lines.append("*Compiled by `scripts/build_views.py` from `wiki/producers/*.md` × `cellar/*.md`.*")
    return "\n".join(lines) + "\n"


def view_raeders_gap(
    producers: dict[str, Producer],
    owned: set[str],
    raeders_bottles: list[RaedersBottle],
) -> str:
    """Aged Raeders bottles on producers Evan doesn't own that fit his taste."""

    # Producer-level filter: in our wiki AND not owned AND NOT clearly out-of-scope
    in_scope_slugs = {p.slug for p in producers.values() if p.slug not in owned}

    # Per-bottle: aged AND (producer is wk-flagged OR scored OR in CSW + biodynamic OR grower-champagne tagged)
    rows: list[tuple[RaedersBottle, Producer | None, str]] = []
    for b in raeders_bottles:
        if b.producer_slug not in in_scope_slugs:
            continue
        p = producers.get(b.producer_slug)
        if p is None:
            continue
        # Need an "aged" or "compelling" hook
        is_aged = b.vintage_int and b.vintage_int <= AGED_THRESHOLD
        is_wk = "wk-coverage" in p.tags
        is_biodyn = "biodynamic" in p.farming or "biodynamic" in p.tags
        is_grower = "grower-champagne" in p.tags
        is_csw_star = p.ch_dedicated >= 1
        if not (is_aged or is_wk or is_grower or (is_biodyn and is_csw_star)):
            continue
        if not is_aged and not (is_wk or is_grower):
            continue  # require either aged OR a strong taste hook
        # Reason badge
        badges = []
        if is_aged: badges.append(f"aged({b.vintage_int})")
        if is_wk: badges.append("WK")
        if is_grower: badges.append("grower")
        if is_biodyn: badges.append("biodynamic")
        if is_csw_star: badges.append(f"CSW ★{p.ch_dedicated}")
        rows.append((b, p, " · ".join(badges)))

    # Sort: WK-flagged first, then biodynamic CSW, then by score, then by age, then by price
    def sort_key(item):
        b, p, _ = item
        is_wk = "wk-coverage" in (p.tags if p else [])
        score = max(b.score_wa, b.score_js, b.score_we)
        return (
            0 if is_wk else 1,
            -score,
            b.vintage_int or 9999,  # older first
            b.price or 0,
        )
    rows.sort(key=sort_key)

    lines = [
        "---",
        "type: gap_view",
        f"updated: {date.today().isoformat()}",
        f"bottle_count: {len(rows)}",
        f"aged_threshold_year: {AGED_THRESHOLD}",
        "---",
        "",
        "# Gap: Raeders Aged & Curated Bottles You Don't Own",
        "",
        f"**{len(rows)} bottles** at Raeders that fit your taste filters and aren't in your cellar.",
        "",
        f"Filter: producer in vault, not owned, and either (a) aged ≤{AGED_THRESHOLD} vintage OR (b) WK-flagged producer / grower champagne / biodynamic CSW-champion.",
        "",
        "| Producer | Cuvée | Vintage | Size | Price | Scores | Why |",
        "|---|---|---:|---|---:|---|---|",
    ]
    for b, p, badges in rows[:120]:
        scores = []
        if b.score_wa: scores.append(f"WA {b.score_wa}")
        if b.score_js: scores.append(f"JS {b.score_js}")
        if b.score_we: scores.append(f"WE {b.score_we}")
        score_str = " · ".join(scores) if scores else "—"
        producer_link = f"[[{p.slug}|{p.name}]]" if p else b.producer
        cuvee = (b.cuvee or "—").replace("|", "/")
        lines.append(
            f"| {producer_link} | {cuvee} | {b.vintage or 'NV'} | "
            f"{b.size or '—'} | {fmt_price(b.price)} | {score_str} | {badges} |"
        )
    if len(rows) > 120:
        lines.append("")
        lines.append(f"_… and {len(rows) - 120} more matching bottles._")
    lines.append("")
    lines.append("*Compiled by `scripts/build_views.py` from `raw/raeders/master_<date>.csv` × `wiki/producers/` × `cellar/`.*")
    return "\n".join(lines) + "\n"


def view_drink_window(bottles: list[CellarBottle], producer_slugs: set[str]) -> str:
    """Bucket cellar bottles by drink-window urgency."""
    past, now, entering, longhold, unknown = [], [], [], [], []
    for b in bottles:
        if b.drink_start is None and b.drink_end is None:
            unknown.append(b)
        elif b.drink_end is not None and b.drink_end < CURRENT_YEAR:
            past.append(b)
        elif (b.drink_start or 0) <= CURRENT_YEAR <= (b.drink_end or CURRENT_YEAR):
            now.append(b)
        elif b.drink_start is not None and CURRENT_YEAR < b.drink_start <= CURRENT_YEAR + ENTERING_HORIZON:
            entering.append(b)
        elif b.drink_start is not None and b.drink_start > CURRENT_YEAR + 5:
            longhold.append(b)
        else:
            unknown.append(b)

    past.sort(key=lambda b: (b.drink_end or 0, b.producer.lower()))
    now.sort(key=lambda b: (b.drink_end or 0, b.producer.lower()))
    entering.sort(key=lambda b: (b.drink_start or 0, b.producer.lower()))
    longhold.sort(key=lambda b: (b.drink_start or 0, b.producer.lower()))

    def render_table(rows: list[CellarBottle], header: str, urgency_col: str) -> list[str]:
        if not rows:
            return [f"## {header}", "", "_None._", ""]
        out = [
            f"## {header} — {len(rows)} entries, "
            f"{sum(b.qty for b in rows)} bottles",
            "",
            f"| Producer | Cuvée | Vintage | Qty | Size | {urgency_col} | Purchase |",
            "|---|---|---:|---:|---|---:|---:|",
        ]
        for b in rows[:50]:
            link_slug = b.producer_slug or slug(b.producer)
            # only wikilink producers that have a wiki page; bottles always
            # link their cellar entry
            producer_cell = (f"[[{link_slug}|{b.producer}]]"
                             if link_slug in producer_slugs else b.producer)
            window = ""
            if urgency_col == "Drink end":
                window = str(b.drink_end) if b.drink_end else "?"
            elif urgency_col == "Drink window":
                window = f"{b.drink_start or '?'}–{b.drink_end or '?'}"
            elif urgency_col == "Drink start":
                window = str(b.drink_start) if b.drink_start else "?"
            cuvee = (b.cuvee or "—").replace("|", "/")
            out.append(
                f"| {producer_cell} | [[{b.stem}|{cuvee}]] | {b.vintage} | "
                f"{b.qty} | {b.size or '—'} | {window} | {fmt_price(b.price)} |"
            )
        if len(rows) > 50:
            out.append(f"")
            out.append(f"_… and {len(rows) - 50} more._")
        out.append("")
        return out

    lines = [
        "---",
        "type: drink_view",
        f"updated: {date.today().isoformat()}",
        f"current_year: {CURRENT_YEAR}",
        f"past: {len(past)}",
        f"now: {len(now)}",
        f"entering: {len(entering)}",
        f"longhold: {len(longhold)}",
        f"unknown: {len(unknown)}",
        "---",
        "",
        "# Drink Window — Urgency View",
        "",
        f"Cellar bottles bucketed against current year **{CURRENT_YEAR}**. ",
        f"Total: {sum(b.qty for b in bottles)} bottles across {len(bottles)} cuvée-vintages.",
        "",
    ]
    lines += render_table(past, f"⚠️ Past window (drink-end < {CURRENT_YEAR})", "Drink end")
    lines += render_table(now, f"🍷 Drinking now (in window)", "Drink window")
    lines += render_table(entering, f"⏳ Entering window in next {ENTERING_HORIZON} year(s)", "Drink start")
    lines += render_table(longhold, f"🛑 Long hold (window starts > {CURRENT_YEAR + 5})", "Drink start")
    if unknown:
        lines += [
            f"## Unknown drink window — {len(unknown)} entries",
            "",
            "_CellarTracker didn't have BeginConsume/EndConsume for these. Worth filling in._",
            "",
        ]
        for b in unknown[:30]:
            lines.append(f"- {b.producer} {b.cuvee} {b.vintage}")
        if len(unknown) > 30:
            lines.append(f"- _… and {len(unknown) - 30} more._")
        lines.append("")

    lines.append("*Compiled by `scripts/build_views.py` from `cellar/*.md`.*")
    return "\n".join(lines) + "\n"


# --- main ---

def main() -> int:
    VIEWS.mkdir(parents=True, exist_ok=True)
    print("Loading producers...")
    producers = load_producers()
    print(f"  {len(producers)} producers")
    print("Loading cellar...")
    owned, bottles = load_cellar()
    print(f"  {len(bottles)} cuvée-vintage entries; {len(owned)} distinct producers")
    print("Loading Raeders raw...")
    raeders = load_raeders()
    print(f"  {len(raeders)} Raeders bottles")

    (VIEWS / "gap_csw_championed.md").write_text(
        view_csw_gap(producers, owned), encoding="utf-8"
    )
    (VIEWS / "gap_raeders_aged_value.md").write_text(
        view_raeders_gap(producers, owned, raeders), encoding="utf-8"
    )
    (VIEWS / "drink_window_due.md").write_text(
        view_drink_window(bottles, set(producers)), encoding="utf-8"
    )
    print(f"\nWrote 3 views to {VIEWS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
