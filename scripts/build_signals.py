#!/usr/bin/env python3
"""
build_signals.py — the vault's join layer.

Wine knowledge is fragmented across many namespaces (region/sub_region,
appellations, farming, importer_us, retailers.*, community.berserkers, the
`## Critic Ratings`/`## Cellar` body sections, taste filters in CLAUDE.md).
Every gap analysis and /ask-cellar answer currently re-derives the join by
opening dozens of pages. This script does it once: one record per producer,
joining land + style + trust + availability + critic + community + ownership,
and two derived judgments that encode Evan's curation —

  * trust_tier  — how much to weight the source (curated importer book /
                  retailer). Tier 1 = Evan's most-trusted grower curators.
  * taste_fit   — core / adjacent / off / skip, from the CLAUDE.md taste rules.
  * conviction  — composite rank used to shortlist (fit × trust × signal).

Outputs:
  build/producer_signals.json                   — machine-readable graph (for /ask-cellar)
  wiki/_views/producer_signals_board_2026_07.md — human read surface
Also reports link-integrity (broken wikilinks = broken graph edges) and
frontmatter coverage (where the curation backfill should go next).

Idempotent. `--check` exits 1 if regenerating either output would change it.
The trust map + taste rules are curated decision tables — tune them here.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from datetime import date

VAULT = Path(__file__).resolve().parent.parent
PROD = VAULT / "wiki" / "producers"
JSON_OUT = VAULT / "build" / "producer_signals.json"
BOARD = VAULT / "wiki" / "_views" / "producer_signals_board_2026_07.md"

# ─────────────────────────────────────────────────────────────────────────────
# CURATED DECISION TABLES  (tune these — this is the taste + trust judgment)
# ─────────────────────────────────────────────────────────────────────────────

# Trust in a source = trust in the producers it curates. Keys are importer_us /
# retailer names (lowercased, prefix-matched).
# Tier 1 set by Evan (2026-07-22): DTE, CSW, Polaner, Bowler, Grand Cru, WK
# comments, Rosenthal, Skurnik. (DTE + CSW are retailers → RETAILER_TRUST; WK
# comments = a Kelley Berserkers-post signal → compute_trust; the rest are here.)
IMPORTER_TIER = {
    1: ["polaner", "bowler", "david bowler", "grand cru", "neal rosenthal",
        "rosenthal", "skurnik"],
    2: ["kermit lynch", "louis/dressner", "louis dressner", "dressner", "theise",
        "terry theise", "zev rovine", "rovine", "selection massale", "jenny & francois",
        "de maison", "wilson daniels", "vineyard brands", "wasserman", "becky wasserman",
        "wildman", "a.i. select", "henderson", "bnp", "banville", "vom boden", "schatzi",
        "jose pastor", "the source", "wine source", "kysela", "veritas", "dns"],
}
# Retailers/books Evan buys from (retailers.* frontmatter). DTE + CSW-championed
# are Tier 1 per Evan; Fass + Raeders are trusted Tier 2.
RETAILER_TRUST = {"dte": 1, "chambers_championed": 1, "fass": 2, "raeders": 2}

# "WK comments" is a graded volume signal, not binary (Evan, 2026-07-22): a ton of
# William Kelley Berserkers posts = Tier 1, one or two ≠ trust. Cutoffs are tunable.
WK_TIER1_MIN = 10   # "a ton" → Tier 1  (12 producers: Ramonet 99 … Clos Rougeard 14)
WK_TIER2_MIN = 4    # repeated signal → Tier 2; 1–3 posts confer no trust on their own

# taste_fit — regions that are the on-taste heartland (grower / terroir).
REGION_CORE = {
    "Burgundy", "Loire", "Champagne", "Mosel", "Nahe", "Piedmont", "Beaujolais",
    "Jura", "Friuli-Venezia Giulia", "Alsace", "Savoie",
}
# Northern-Rhône communes are core; southern Rhône is adjacent by default.
NRHONE_SUBS = {"cornas", "cote-rotie", "côte-rôtie", "saint-joseph", "st-joseph",
               "hermitage", "crozes-hermitage", "condrieu", "saint-peray", "st-peray"}
# Napa/California — two accepted tracks (name-matched; CLAUDE.md 2026-07-21).
NAPA_CORE = {
    "dunn", "corison", "la jota", "ridge", "dalla valle", "beta", "beringer",
    "robert mondavi", "mondavi", "sterling", "flora springs", "philip togni", "togni",
    "spottswoode", "groth", "phelps", "bond", "harlan", "araujo", "eisele",
    "kapcsandy", "abreu",
}
# California Syrah/Rhône opulent — the explicit skip (CLAUDE.md).
CA_SKIP = {"sine qua non", "sqn", "saxum", "next of kyn", "law estate", "law "}
ARG_REGIONS = {"Mendoza", "Patagonia", "Salta", "Jujuy"}

# ─────────────────────────────────────────────────────────────────────────────

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def scalar(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*?)[ \t]*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def yaml_list(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.MULTILINE)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline and inline not in ("[]", '""', "''"):
        return [x.strip().strip('"') for x in inline.strip("[]").split(",") if x.strip()]
    out, tail = [], fm[m.end():]
    for ln in tail.split("\n"):
        s = ln.strip()
        if s.startswith("- "):
            out.append(s[2:].strip().strip('"').strip("'"))
        elif s:                       # first non-empty, non-item line ends the list
            break
    return out


def retailer_true(fm, r):
    return bool(re.search(rf"\n  {r}:\n(?:    [^\n]*\n)*?    in_portfolio:\s*true", fm))


def chambers_championed(fm):
    return bool(re.search(r"championed:\s*true", fm))


def best_critic(body):
    m = re.search(r"## Critic Ratings\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if not m:
        return None
    best = None
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        nums = re.findall(r"\d+", cells[4])  # Score column
        if nums:
            v = float(nums[-1]) + (0.5 if cells[4].strip().endswith("+") else 0)
            if 50 <= v <= 100:
                best = v if best is None else max(best, v)
    return best


def wb_rank(fm):
    m = re.search(r"rank:\s*(\d+)", fm)
    return int(m.group(1)) if m else None


def wk_posts(fm):
    """'WK comments' = William Kelley's Berserkers posts about the producer
    (retailers.berserkers_kelley.post_count). A Tier-1 trust signal per Evan."""
    m = re.search(r"berserkers_kelley:\n(?:\s+[a-z_]+:.*\n)*?\s+post_count:\s*(\d+)", fm)
    return int(m.group(1)) if m else 0


def importer_tier(importers):
    best = None
    for imp in importers:
        il = imp.lower()
        for tier, names in IMPORTER_TIER.items():
            if any(il.startswith(n) or n in il for n in names):
                best = tier if best is None else min(best, tier)
    return best


def compute_trust(fm, importers):
    tiers = []
    t = importer_tier(importers)
    if t:
        tiers.append(t)
    wk = wk_posts(fm)             # WK comments: graded, not binary (Evan, 2026-07-22)
    if wk >= WK_TIER1_MIN:
        tiers.append(1)
    elif wk >= WK_TIER2_MIN:
        tiers.append(2)
    for r, tier in RETAILER_TRUST.items():
        if r == "chambers_championed":
            if chambers_championed(fm):
                tiers.append(tier)
        elif retailer_true(fm, r):
            tiers.append(tier)
    return min(tiers) if tiers else None


def compute_taste_fit(name, region, sub_region, farming):
    nl = name.lower()
    if any(s in nl for s in CA_SKIP):
        return "skip"
    if any(n in nl for n in NAPA_CORE):
        return "core"
    bio = any(f in ("biodynamic", "organic") for f in farming)
    if region in REGION_CORE:
        return "core"
    if region == "Rhône":
        return "core" if (sub_region or "").lower() in NRHONE_SUBS else "adjacent"
    if region in ("California", "Napa Valley", "Oregon"):
        return "adjacent"          # generic mid-tier unless name-matched above
    if region in ARG_REGIONS:
        return "core" if bio else "adjacent"
    if region == "Bordeaux":
        return "adjacent"          # WK-value / aged classed-growth needs a flag
    if region == "Tuscany":
        return "adjacent"
    return "adjacent" if region else "off"


FIT_SCORE = {"core": 3, "adjacent": 1, "off": 0, "skip": -3}
TRUST_SCORE = {1: 3, 2: 2, 3: 1, None: 0}


def conviction(fit, trust, critic, wb):
    s = FIT_SCORE.get(fit, 0) + TRUST_SCORE.get(trust, 0)
    if critic and critic >= 97:
        s += 2
    elif critic and critic >= 95:
        s += 1
    if wb and wb <= 200:
        s += 1
    return s


def main() -> int:
    records, all_slugs, link_targets = [], set(), []
    for p in sorted(PROD.glob("*.md")):
        all_slugs.add(p.stem)
    # gather links across wiki + _views + cellar for integrity check. Skip this
    # script's own generated board so the output isn't a function of itself
    # (keeps the run a single-pass fixed point for --check).
    for base in (VAULT / "wiki", VAULT / "cellar"):
        for f in base.rglob("*.md"):
            if f == BOARD:
                continue
            for m in WIKILINK_RE.finditer(f.read_text(encoding="utf-8", errors="replace")):
                link_targets.append(m.group(1).strip())

    for p in sorted(PROD.glob("*.md")):
        t = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        m = FM_RE.match(t)
        if not m:
            continue
        fm, body = m.group(1), m.group(2)
        name = scalar(fm, "name") or p.stem
        region = scalar(fm, "region")
        sub = scalar(fm, "sub_region")
        farming = yaml_list(fm, "farming")
        importers = yaml_list(fm, "importer_us")
        avail = [r for r in ("raeders", "dte", "fass") if retailer_true(fm, r)]
        if chambers_championed(fm):
            avail.append("chambers")
        trust = compute_trust(fm, importers)
        fit = compute_taste_fit(name, region, sub, farming)
        critic = best_critic(body)
        wb = wb_rank(fm)
        wk = wk_posts(fm)
        owned = "## Cellar" in body
        rec = {
            "slug": p.stem, "name": name, "region": region, "sub_region": sub,
            "appellations": yaml_list(fm, "appellations"), "farming": farming,
            "importer_us": importers, "available_at": avail,
            "trust_tier": trust, "taste_fit": fit, "wk_posts": wk,
            "best_critic": critic, "wb_rank": wb, "owned": owned,
            "conviction": conviction(fit, trust, critic, wb),
        }
        records.append(rec)

    records.sort(key=lambda r: (-r["conviction"], r["region"], r["name"]))

    # link integrity: a target resolves if it's any md stem under wiki/ (producers,
    # regions, importers, retailers, _views) — otherwise the edge points at nothing.
    md_stems = {f.stem for f in (VAULT / "wiki").rglob("*.md")} | all_slugs
    broken_set = {tg for tg in link_targets if tg not in md_stems}
    broken_count = sum(1 for tg in link_targets if tg not in md_stems)

    # coverage
    N = len(records)
    cov = {
        "importer_us": sum(1 for r in records if r["importer_us"]),
        "appellations": sum(1 for r in records if r["appellations"]),
        "farming": sum(1 for r in records if r["farming"]),
        "trust_tier": sum(1 for r in records if r["trust_tier"]),
    }

    payload = {
        "generated": date.today().isoformat(),
        "producers": N,
        "coverage": cov,
        "link_integrity": {"broken_targets": len(broken_set), "broken_occurrences": broken_count},
        "records": records,
    }
    json_text = json.dumps(payload, ensure_ascii=False, indent=1)

    # ---- board ----
    def link(r):
        return f"[[{r['slug']}\\|{r['name']}]]"
    core_buy = [r for r in records if r["taste_fit"] == "core" and r["available_at"]
                and not r["owned"]]
    tier1 = [r for r in records if r["trust_tier"] == 1]

    L = ["---", "type: view", f"updated: {date.today().isoformat()}",
         'question: "Joined per-producer signal graph — land + style + trust + availability + critic + ownership — ranked by conviction."',
         "source: scripts/build_signals.py (joins producer frontmatter + `## Critic Ratings`/`## Cellar` bodies + community.berserkers). Machine copy: build/producer_signals.json",
         "snapshot_date: 2026-04-25  # Raeders availability + critic rows; see per-source dates",
         "---", "",
         "# Producer Signals Board (2026-07)",
         "",
         f"The vault's **join layer**: {N} producers, one row each, unifying signals that "
         "otherwise live in separate frontmatter namespaces and body sections. Generated by "
         "`scripts/build_signals.py`; the machine-readable copy `build/producer_signals.json` is "
         "the first thing `/ask-cellar` should load for any question that spans producers, land, "
         "style, or source. Don't hand-edit.",
         "",
         "**Derived judgments (curated decision tables in the script — tune there):**",
         "",
         "- **taste_fit** — `core` (on-taste heartland: grower Burgundy/Loire/Champagne/German "
         "Riesling/Piedmont/Beaujolais/Jura/Friuli/N-Rhône + the two accepted Napa-Cab tracks) · "
         "`adjacent` (plausible, needs a flag: generic Napa, Bordeaux, S-Rhône, Argentina non-bio) · "
         "`skip` (opulent CA Syrah/Rhône — SQN/Saxum/Law/Next of Kyn).",
         "- **trust_tier** — set by Evan (2026-07-22). **Tier 1:** Down to Earth (Panzer), "
         "Chambers/CSW (championed), Polaner, David Bowler, Grand Cru, **WK comments — ≥10 posts** "
         "(a graded William Kelley Berserkers signal, `retailers.berserkers_kelley.post_count`), "
         "Neal Rosenthal, Skurnik. **Tier 2:** Fass, Raeders, **WK comments 4–9 posts** + broader "
         "trusted books (Kermit Lynch, Louis/Dressner, Theise, Zev Rovine, Wilson Daniels, Vineyard "
         "Brands, …). A lone WK mention (1–3) confers no trust on its own.",
         "- **conviction** — `taste_fit + trust_tier + critic + WB-momentum`, the shortlist rank.",
         "",
         f"## High-conviction buy list — on-taste, from a trusted source, not owned ({len(core_buy)})",
         "",
         "The money query, resolved once. `core` taste-fit × currently available at a vault "
         "retailer × not in the cellar, best conviction first.",
         "",
         "| Conv | Producer | Region / land | Trust | At | Best critic |",
         "|---:|---|---|:---:|---|---:|"]
    for r in core_buy[:50]:
        land = f"{r['region']}" + (f" · {r['sub_region']}" if r['sub_region'] else "")
        t = f"T{r['trust_tier']}" if r["trust_tier"] else "—"
        crit = f"{int(r['best_critic'])}" if r["best_critic"] else "—"
        L.append(f"| {r['conviction']} | {link(r)} | {land} | {t} | {', '.join(r['available_at'])} | {crit} |")
    L += ["",
          f"## Tier-1 trusted-source producers ({len(tier1)})",
          "",
          "Everyone who reaches Evan through a most-trusted curated book. This is the bias he asked "
          "for made queryable — start here when shortlisting.",
          "",
          "| Producer | Region / land | Fit | Source | Owned? |",
          "|---|---|:---:|---|:---:|"]
    for r in sorted(tier1, key=lambda r: (-r["wk_posts"], r["region"], r["name"]))[:90]:
        land = f"{r['region']}" + (f" · {r['sub_region']}" if r['sub_region'] else "")
        srcs = r["importer_us"][:1] + [a for a in r["available_at"] if a in ("dte", "chambers")][:1]
        if r["wk_posts"]:
            srcs.append(f"WK×{r['wk_posts']}")
        src = ", ".join(srcs) or "—"
        L.append(f"| {link(r)} | {land} | {r['taste_fit']} | {src} | {'🍷' if r['owned'] else '—'} |")
    L += ["",
          "## Curation backfill — where the graph is thin",
          "",
          "The join is only as good as the fields it reads. Coverage across "
          f"{N} producers (raise these to sharpen every future answer):",
          "",
          f"- **importer_us (trust source): {cov['importer_us']} ({100*cov['importer_us']//N}%)** — "
          "the single highest-leverage backfill; every unfilled one is a producer whose trust "
          "signal is invisible.",
          f"- **appellations (cru / vineyard 'land'): {cov['appellations']} ({100*cov['appellations']//N}%)** — "
          "the gap blocking cru-level 'producer × land' reasoning (who else works Les Chaignots / "
          "Howell Mtn). Backfill from the cuvée names already sitting in `## Critic Ratings` + the "
          "DTE cuvée tables.",
          f"- **farming (style): {cov['farming']} ({100*cov['farming']//N}%)**.",
          f"- **trust_tier resolved: {cov['trust_tier']} ({100*cov['trust_tier']//N}%)**.",
          "",
          "## Link integrity (graph edges)",
          "",
          f"**{payload['link_integrity']['broken_targets']} distinct broken `[[wikilink]]` targets** "
          f"({payload['link_integrity']['broken_occurrences']} occurrences) across wiki + _views + "
          "cellar — edges that point at nothing, so multi-hop traversal dead-ends. Top offenders and "
          "the fix plan are in [[data_quality_integration_review_2026_07]] (rec #2). Making `lint.py` "
          "validate every target turns this into a build-time gate.",
          ""]
    board_text = "\n".join(L)

    if "--check" in sys.argv:
        # Gate only the committed read surface (the board). build/producer_signals.json
        # is gitignored + regenerable, so it isn't present in a fresh CI checkout.
        cur = BOARD.read_text(encoding="utf-8") if BOARD.exists() else ""
        if cur != board_text:
            print(f"DRIFT: {BOARD.name} would change — re-run build_signals.py")
            return 1
        print(f"OK: signals board current ({N} producers, {len(core_buy)} high-conviction buys)")
        return 0

    JSON_OUT.parent.mkdir(exist_ok=True)
    JSON_OUT.write_text(json_text, encoding="utf-8")
    BOARD.write_text(board_text, encoding="utf-8")
    print(f"Wrote {JSON_OUT.name} + {BOARD.name}: {N} producers, "
          f"{len(core_buy)} on-taste buyable-not-owned, {len(tier1)} tier-1, "
          f"{payload['link_integrity']['broken_targets']} broken link targets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
