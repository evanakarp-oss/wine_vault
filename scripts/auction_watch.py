#!/usr/bin/env python3
"""Weekly auction scour: fetch current catalogs from the major wine-auction
platforms, screen every lot against scripts/auction_watchlist.yaml (seeded
from Evan's curation taste), and write a markdown hit report.

Run by .github/workflows/auction_watch.yml every Monday; the workflow opens
a GitHub issue when there are hits. Also usable by hand:

    python scripts/auction_watch.py                     # fetch + screen all platforms
    python scripts/auction_watch.py --xlsx path.xlsx    # screen a local Acker-format catalog

Outputs (regenerable, never hand-edit):
    build/auction_watch/report.md   — the hit report
    build/auction_watch/hits.json   — machine-readable hits (workflow gate)

Platform adapters are best-effort: auction sites change markup and some
(WineBid, K&L) wall their catalogs behind login. Every run reports which
platforms were fetched, which failed, and which need a manual look, so a
silent miss is impossible. Acker's weekly xlsx (the Catalog_<sale>W_<week>
CDN pattern, verified 2026-06 against sale 261W week 24) is the one fully
automated source; the rest degrade to manual-check links until tuned
against live markup.
"""

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "scripts" / "auction_watchlist.yaml"
OUT_DIR = ROOT / "build" / "auction_watch"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Acker weekly catalog CDN bucket + sale/week anchor (sale 261W = ISO week 24
# of 2026). Sale number and ISO week advance in lockstep, so future URLs are
# computable without scraping; probe +/-1 to absorb skipped weeks.
ACKER_CDN = "https://605d53e62efa100bb729-56ef94ef6e45e295aeb858c8b79ff7f4.ssl.cf1.rackcdn.com"
ACKER_ANCHOR = (dt.date(2026, 6, 8), 261, 24)  # (monday, sale_no, week_label)

# Platforms with no working adapter yet — surfaced in every report so the
# human (or a Claude session) can sweep them manually.
MANUAL_CHECK = {
    "WineBid (weekly, Sun close)": "https://www.winebid.com/BrowseWine",
    "Zachys": "https://auction.zachys.com",
    "Hart Davis Hart": "https://www.hdhwine.com/auctions",
    "K&L auctions": "https://www.klwines.com/Auctions",
    "Sotheby's Wine": "https://www.sothebys.com/en/departments/wine-spirits",
    "Christie's Wine": "https://www.christies.com/en/departments/wine-and-spirits",
    "Spectrum Wine": "https://www.spectrumwine.com/auctions/",
}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- xlsx parse

XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def parse_acker_xlsx(blob, sale_label):
    """Acker weekly catalog → normalized lot dicts. Columns verified 2026-06:
    LotNo, Quantity, BottleName, Vintage, WineName, Designation, Producer,
    Levels, Low, High, WineType, RegionDescription, ItemLocation,
    ItemWineScore, WineNote, AddlLots."""
    z = zipfile.ZipFile(BytesIO(blob))
    shared = [
        "".join(t.text or "" for t in si.iter(XLSX_NS + "t"))
        for si in ET.fromstring(z.read("xl/sharedStrings.xml"))
    ]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.iter(XLSX_NS + "row"):
        vals = {}
        for c in row:
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v = c.find(XLSX_NS + "v")
            if v is None:
                continue
            vals[col] = shared[int(v.text)] if c.get("t") == "s" else v.text
        rows.append(vals)
    if not rows:
        return []
    header = {v: k for k, v in rows[0].items()}

    def g(r, name):
        return r.get(header.get(name, ""), "")

    lots = []
    for r in rows[1:]:
        try:
            qty = int(float(g(r, "Quantity") or 0))
            low = float(g(r, "Low") or 0)
            high = float(g(r, "High") or 0)
        except ValueError:
            qty, low, high = 0, 0.0, 0.0
        lots.append({
            "platform": "Acker",
            "sale": sale_label,
            "lot": g(r, "LotNo"),
            "wine": g(r, "WineName"),
            "designation": g(r, "Designation"),
            "producer": g(r, "Producer"),
            "vintage": g(r, "Vintage"),
            "qty": qty,
            "size": g(r, "BottleName"),
            "low": low,
            "high": high,
            "score": g(r, "ItemWineScore"),
            "location": g(r, "ItemLocation"),
            "levels": g(r, "Levels"),
        })
    return lots


# ----------------------------------------------------------------- adapters


def adapter_acker(status):
    """Probe the Acker CDN for this week's catalog (sale/week advance with
    the ISO calendar from the verified anchor)."""
    anchor_day, anchor_sale, anchor_week = ACKER_ANCHOR
    weeks = (dt.date.today() - anchor_day).days // 7
    lots = []
    for delta in (0, -1, 1):
        sale = anchor_sale + weeks + delta
        week = anchor_week + weeks + delta
        year_off, week_lbl = divmod(week - 1, 52)
        week_lbl += 1
        url = f"{ACKER_CDN}/Catalog_{sale}W_{week_lbl}.xlsx"
        try:
            blob = fetch(url)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            continue
        lots.extend(parse_acker_xlsx(blob, f"{sale}W week {week_lbl}"))
        status.append(("Acker", f"OK — sale {sale}W ({len(lots)} lots) {url}"))
    if not lots:
        status.append(("Acker", "FAILED — no catalog found at probed CDN URLs"))
    return lots


ADAPTERS = [adapter_acker]


# ------------------------------------------------------------------- screen


def load_watchlist():
    cfg = yaml.safe_load(WATCHLIST.read_text())
    tiers = [
        (t["name"], t.get("note", ""), [re.compile(p, re.I) for p in t["patterns"]])
        for t in cfg["tiers"]
    ]
    excl = [re.compile(p, re.I) for p in cfg.get("exclusions", [])]
    return tiers, excl


def screen(lots, tiers, excl):
    hits = {name: [] for name, _, _ in tiers}
    for lot in lots:
        hay = " ".join((lot["wine"], lot["designation"], lot["producer"]))
        if any(p.search(hay) for p in excl):
            continue
        for name, _, pats in tiers:
            if any(p.search(hay) for p in pats):
                hits[name].append(lot)
                break
    return hits


def fmt_lot(l):
    per = ""
    if l["qty"] and l["size"] == "bottle" and l["low"]:
        per = f" (~${l['low'] / l['qty']:.0f}-{l['high'] / l['qty']:.0f}/btl)"
    size = "" if l["size"] == "bottle" else f" {l['size']}"
    score = f" {l['score']}" if l["score"] else ""
    levels = f" — condition: {l['levels']}" if l["levels"] else ""
    return (
        f"| {l['platform']} {l['sale']} | {l['lot']} | {l['vintage']} | "
        f"{l['wine']}{' — ' + l['designation'] if l['designation'] else ''} | "
        f"{l['qty']}{size} | ${l['low']:.0f}-{l['high']:.0f}{per} |{score}{levels} |"
    )


def write_report(hits, tiers, status, total_lots):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    n_hits = sum(len(v) for v in hits.values())
    lines = [
        f"# Auction watch — {today}",
        "",
        f"Screened **{total_lots} lots** against `scripts/auction_watchlist.yaml`; "
        f"**{n_hits} hits**.",
        "",
        "## Platform status",
        "",
    ]
    for platform, msg in status:
        lines.append(f"- **{platform}**: {msg}")
    lines += ["", "## Manual-check platforms (no adapter yet)", ""]
    for name, url in MANUAL_CHECK.items():
        lines.append(f"- [{name}]({url})")
    for name, note, _ in tiers:
        lots = hits[name]
        if not lots:
            continue
        lines += ["", f"## {name} ({len(lots)})", ""]
        if note:
            lines += [f"_{note}_", ""]
        lines += ["| Sale | Lot | Vtg | Wine | Qty | Estimate | Score / condition |",
                  "|---|---|---|---|---|---|---|"]
        lines += [fmt_lot(l) for l in sorted(lots, key=lambda x: (x["wine"], x["vintage"]))]
    lines += [
        "",
        "---",
        "_Generated by `scripts/auction_watch.py`. Deep-screen hits against the_",
        "_cellar via `/ask-cellar` before bidding; check bottle condition on_",
        "_anything pre-1995._",
        "",
    ]
    (OUT_DIR / "report.md").write_text("\n".join(lines))
    flat = [l for v in hits.values() for l in v]
    (OUT_DIR / "hits.json").write_text(json.dumps(flat, indent=1))
    return n_hits


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--xlsx", help="screen a local Acker-format xlsx instead of fetching")
    args = ap.parse_args()

    status, lots = [], []
    if args.xlsx:
        lots = parse_acker_xlsx(Path(args.xlsx).read_bytes(), Path(args.xlsx).stem)
        status.append(("local file", f"OK — {len(lots)} lots from {args.xlsx}"))
    else:
        for adapter in ADAPTERS:
            try:
                lots.extend(adapter(status))
            except Exception as e:  # one bad adapter must not sink the run
                status.append((adapter.__name__, f"ERROR — {e}"))

    tiers, excl = load_watchlist()
    hits = screen(lots, tiers, excl)
    n = write_report(hits, tiers, status, len(lots))
    print(f"{len(lots)} lots screened, {n} hits → {OUT_DIR / 'report.md'}")


if __name__ == "__main__":
    main()
