#!/usr/bin/env python3
"""
compile_offers_roundup.py — overlay weekly retailer offer emails against the vault.

Reads `raw/offers/<YYYY-MM-DD>/*.md` (LLM-captured offer emails with
frontmatter listing producer slugs), then for each producer mentioned looks
up:
  - wiki/producers/<slug>.md frontmatter — region, farming, CSW championed
    status, Berserkers rank/momentum
  - cellar/*.md — do we own this producer? Which vintages, how many bottles?

Writes `wiki/_views/offers_<YYYY-MM-DD>.md` grouped by retailer.

Usage:
    python scripts/compile_offers_roundup.py --date 2026-05-25
    python scripts/compile_offers_roundup.py            # defaults to today

Requires PyYAML.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML required. pip install pyyaml --break-system-packages")


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)

RETAILER_DISPLAY = {
    "chambers": "Chambers Street Wines",
    "flatiron": "Flatiron Wines",
    "leon": "Leon & Son",
    "rsquared": "R Squared Selections",
    "fass": "FASS Selections",
}

RETAILER_ORDER = ["chambers", "flatiron", "leon", "rsquared", "fass"]


@dataclass
class Producer:
    slug: str
    name: str
    region: str = ""
    sub_region: str = ""
    country: str = ""
    farming: list = field(default_factory=list)
    csw_championed: bool = False
    csw_articles: int = 0
    berserkers_rank: int | None = None
    berserkers_mentions: int | None = None
    berserkers_momentum: float | None = None


@dataclass
class CellarEntry:
    producer_slug: str
    cuvee: str
    vintage: str
    quantity: int
    drink_window_start: int | None = None
    drink_window_end: int | None = None


@dataclass
class Offer:
    path: Path
    retailer: str
    sender: str
    date: str
    subject: str
    gmail_thread_id: str
    producers_in_vault: list
    producers_not_in_vault: list
    themes: list
    kind: str
    body_excerpt: str


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2)


def load_producers(vault_root: Path) -> dict[str, Producer]:
    out: dict[str, Producer] = {}
    for p in (vault_root / "wiki" / "producers").glob("*.md"):
        fm, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        if not fm:
            continue
        slug = fm.get("slug") or p.stem
        # CSW + Berserkers signals
        retailers = fm.get("retailers") or {}
        csw = retailers.get("chambers") or {}
        community = fm.get("community") or {}
        berserkers = (community.get("berserkers") or {}).get("threads") or {}
        # Pick the top10_in_cellar thread if present; else first thread
        b_thread = berserkers.get("top10_in_cellar") or (next(iter(berserkers.values()), {}) if berserkers else {})
        out[slug] = Producer(
            slug=slug,
            name=fm.get("name") or slug,
            region=fm.get("region") or "",
            sub_region=fm.get("sub_region") or "",
            country=fm.get("country") or "",
            farming=fm.get("farming") or [],
            csw_championed=bool(csw.get("championed")),
            csw_articles=int(csw.get("article_count") or 0),
            berserkers_rank=b_thread.get("rank"),
            berserkers_mentions=b_thread.get("mentions"),
            berserkers_momentum=b_thread.get("momentum_score_2023"),
        )
    return out


def load_cellar(vault_root: Path) -> dict[str, list[CellarEntry]]:
    out: dict[str, list[CellarEntry]] = {}
    for p in (vault_root / "cellar").glob("*.md"):
        fm, _ = split_frontmatter(p.read_text(encoding="utf-8"))
        if not fm:
            continue
        slug = fm.get("producer_slug")
        if not slug:
            continue
        out.setdefault(slug, []).append(
            CellarEntry(
                producer_slug=slug,
                cuvee=fm.get("cuvee") or "",
                vintage=str(fm.get("vintage") or ""),
                quantity=int(fm.get("quantity") or 0),
                drink_window_start=fm.get("drink_window_start"),
                drink_window_end=fm.get("drink_window_end"),
            )
        )
    return out


def load_offers(vault_root: Path, date: str) -> list[Offer]:
    offer_dir = vault_root / "raw" / "offers" / date
    if not offer_dir.is_dir():
        sys.exit(f"ERROR: {offer_dir} not found.")
    out: list[Offer] = []
    for p in sorted(offer_dir.glob("*.md")):
        if p.name == "README.md":
            continue
        fm, body = split_frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") != "offer":
            continue
        out.append(Offer(
            path=p,
            retailer=fm.get("retailer") or "",
            sender=fm.get("sender") or "",
            date=str(fm.get("date") or ""),
            subject=fm.get("subject") or "",
            gmail_thread_id=fm.get("gmail_thread_id") or "",
            producers_in_vault=list(fm.get("producers_in_vault") or []),
            producers_not_in_vault=list(fm.get("producers_not_in_vault") or []),
            themes=list(fm.get("themes") or []),
            kind=fm.get("kind") or "feature",
            body_excerpt=body.strip(),
        ))
    return out


def producer_annotation(prod: Producer, cellar: list[CellarEntry]) -> str:
    bits = []
    loc = ", ".join(x for x in (prod.region, prod.country) if x)
    if prod.sub_region:
        loc = f"{prod.sub_region} ({loc})" if loc else prod.sub_region
    if loc:
        bits.append(loc)
    if prod.farming:
        bits.append("/".join(prod.farming))
    art = "article" if prod.csw_articles == 1 else "articles"
    if prod.csw_championed:
        bits.append(f"★ CSW championed ({prod.csw_articles} {art})")
    elif prod.csw_articles:
        bits.append(f"CSW: {prod.csw_articles} {art}")
    if prod.berserkers_rank:
        mom = ""
        if prod.berserkers_momentum is not None:
            try:
                mom = f", momentum {float(prod.berserkers_momentum):.1f}×"
            except (TypeError, ValueError):
                mom = ""
        bits.append(f"WB rank {prod.berserkers_rank} ({prod.berserkers_mentions} mentions{mom})")
    if cellar:
        total = sum(c.quantity for c in cellar)
        vintages = sorted({c.vintage for c in cellar if c.vintage})
        bits.append(f"**OWN {total} btl** ({', '.join(vintages)})")
    return " · ".join(bits)


def render_offer(offer: Offer, producers: dict[str, Producer], cellar_idx: dict[str, list[CellarEntry]]) -> str:
    lines: list[str] = []
    date = offer.date
    kind_tag = f" `{offer.kind}`" if offer.kind and offer.kind != "feature" else ""
    lines.append(f"### {date} — {offer.subject}{kind_tag}")
    lines.append(f"*from {offer.sender}* · [Gmail thread](https://mail.google.com/mail/u/0/#all/{offer.gmail_thread_id})")
    lines.append("")
    if offer.body_excerpt:
        lines.append(f"> {offer.body_excerpt.replace(chr(10), ' ').strip()}")
        lines.append("")

    hits = []
    for slug in offer.producers_in_vault:
        prod = producers.get(slug)
        if not prod:
            hits.append((slug, f"`{slug}` (slug listed but no producer page — fix the offer file or create the page)"))
            continue
        cellar = cellar_idx.get(slug, [])
        ann = producer_annotation(prod, cellar)
        link = f"[[{slug}|{prod.name}]]"
        hits.append((slug, f"{link} — {ann}" if ann else link))

    if hits:
        lines.append("**Vault hits:**")
        for _, line in hits:
            lines.append(f"- {line}")
        lines.append("")
    if offer.producers_not_in_vault:
        lines.append("**Not in vault:** " + ", ".join(offer.producers_not_in_vault))
        lines.append("")
    if not hits and not offer.producers_not_in_vault:
        lines.append("_No specific producers extracted (meta/admin or theme-only)._")
        lines.append("")
    return "\n".join(lines)


def render_summary(offers: list[Offer], producers: dict[str, Producer], cellar_idx: dict[str, list[CellarEntry]]) -> str:
    # Total counts; cellar hits across all offers; producers without a page
    total = len(offers)
    by_retailer: dict[str, int] = {}
    vault_hits: dict[str, list[str]] = {}     # slug → list of retailer slugs
    cellar_hits: dict[str, list[str]] = {}    # slug → list of retailer slugs
    missing: dict[str, int] = {}              # raw name → count

    for o in offers:
        by_retailer[o.retailer] = by_retailer.get(o.retailer, 0) + 1
        for slug in o.producers_in_vault:
            vault_hits.setdefault(slug, []).append(o.retailer)
            if slug in cellar_idx:
                cellar_hits.setdefault(slug, []).append(o.retailer)
        for name in o.producers_not_in_vault:
            missing[name] = missing.get(name, 0) + 1

    lines: list[str] = []
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **{total} emails** across {len(by_retailer)} retailers.")
    for r in RETAILER_ORDER:
        if r in by_retailer:
            lines.append(f"  - {RETAILER_DISPLAY.get(r, r)}: {by_retailer[r]}")
    lines.append(f"- **{len(vault_hits)} unique producers** matched to vault pages.")
    lines.append(f"- **{len(cellar_hits)} of those are in the cellar** — flash-points for top-ups.")
    lines.append(f"- **{len(missing)} unique producers** with no vault page (candidates for new pages if recurring).")
    lines.append("")

    if cellar_hits:
        lines.append("### Already in cellar (review for top-ups / drink-now)")
        lines.append("")
        for slug, retailers in sorted(cellar_hits.items()):
            prod = producers.get(slug)
            if not prod:
                continue
            cellar = cellar_idx.get(slug, [])
            total_btl = sum(c.quantity for c in cellar)
            vintages = sorted({c.vintage for c in cellar if c.vintage})
            tags = ", ".join(sorted(set(retailers)))
            lines.append(f"- [[{slug}|{prod.name}]] — own {total_btl} btl ({', '.join(vintages)}); offered by {tags}")
        lines.append("")

    cross_retailer = {s: r for s, r in vault_hits.items() if len(set(r)) > 1}
    if cross_retailer:
        lines.append("### Multi-retailer producers this week")
        lines.append("")
        for slug, retailers in sorted(cross_retailer.items()):
            prod = producers.get(slug)
            if not prod:
                continue
            tags = ", ".join(sorted(set(retailers)))
            lines.append(f"- [[{slug}|{prod.name}]] — {tags}")
        lines.append("")

    if missing:
        lines.append("### Producers mentioned but not in vault")
        lines.append("")
        lines.append("Sorted by mention count. Curate candidates for new producer pages — same rule as Raeders: don't auto-create from a single source.")
        lines.append("")
        for name, count in sorted(missing.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {name} ({count}×)")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="Roundup date (YYYY-MM-DD) — must match raw/offers/<date>/.")
    ap.add_argument("--vault-root", default=str(Path(__file__).resolve().parent.parent), help="Path to vault root.")
    ap.add_argument("--output", default=None, help="Output file (default: wiki/_views/offers_<date>.md).")
    args = ap.parse_args()

    vault_root = Path(args.vault_root)
    producers = load_producers(vault_root)
    cellar_idx = load_cellar(vault_root)
    offers = load_offers(vault_root, args.date)

    out_path = Path(args.output) if args.output else vault_root / "wiki" / "_views" / f"offers_{args.date}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("---")
    lines.append("type: view")
    lines.append("view: offers_weekly")
    lines.append(f"date: {args.date}")
    lines.append(f"offer_count: {len(offers)}")
    lines.append(f"generator: scripts/compile_offers_roundup.py")
    lines.append("---")
    lines.append("")
    lines.append(f"# Weekly Offers Roundup — {args.date}")
    lines.append("")
    lines.append(f"Past-7-day inbox sweep across CSW, Flatiron, Leon & Son, R Squared (+ FASS). Generated by `scripts/compile_offers_roundup.py`. Raw email captures under `raw/offers/{args.date}/`.")
    lines.append("")
    lines.append(render_summary(offers, producers, cellar_idx))
    lines.append("")

    by_retailer: dict[str, list[Offer]] = {}
    for o in offers:
        by_retailer.setdefault(o.retailer, []).append(o)

    for r in RETAILER_ORDER:
        if r not in by_retailer:
            continue
        lines.append(f"## {RETAILER_DISPLAY.get(r, r)}")
        lines.append("")
        for o in sorted(by_retailer[r], key=lambda x: x.date, reverse=True):
            lines.append(render_offer(o, producers, cellar_idx))
            lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(offers)} offers, {sum(1 for o in offers for s in o.producers_in_vault)} vault hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
