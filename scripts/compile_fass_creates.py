#!/usr/bin/env python3
"""Create producer pages for Fass Selections inventory not yet in the vault.

Source: Fass File.xlsx -> /tmp/fass/parsed.json (producer, wine, vintage,
country, region, subregion, price). Deduplicates producers (lookup table +
manual merges), drops obvious name-fragments, resolves country/region against
_TAXONOMY.md, dedupes cuvees, pulls editorial from raw/fass/markdown when a
matching article exists, and writes wiki/producers/<slug>.md.

LLM-judgment pass (decision tables below), per CLAUDE.md compile_*.py pattern.
Idempotent: never overwrites an existing producer file. Run with --apply.
"""
from __future__ import annotations
import json, os, re, sys, glob, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRODUCERS = ROOT / "wiki" / "producers"
TAXONOMY = ROOT / "wiki" / "_TAXONOMY.md"
PARSED = Path("/tmp/fass/parsed.json")
ARTICLES_DIR = ROOT / "raw" / "fass" / "markdown"
ARTICLES_CSV = ROOT / "raw" / "fass" / "articles.csv"

# ---- decision tables ----------------------------------------------------
MERGE = {  # raw/standardized -> canonical
    "Maison Brisset": "Maison Pierre Brisset", "Pierre Brisset": "Maison Pierre Brisset",
    "Thorle": "Thörle", "Thörle": "Thörle",
    "Thorle Blanc": "Thörle", "Thörle Blanc": "Thörle",
    "Arpepe": "ArPePe", "ArPePe Stella": "ArPePe", "ArPePe": "ArPePe",
    "Achim": "Achim Dürr", "Achim Durr": "Achim Dürr", "Achim Duerr": "Achim Dürr",
    "Bernard and Fabrice Gripa": "Bernard Gripa", "Bernard Gripa": "Bernard Gripa",
    "Caves Jean": "Caves Jean Bourdy", "Caves Jean Bourdy": "Caves Jean Bourdy",
    "Cesare": "Cesare Bussolo", "Cesare Bussolo": "Cesare Bussolo",
    "Caillez-Lemaire \"Pur": "Caillez-Lemaire", "Caillez-Lemaire": "Caillez-Lemaire",
    "Calafe": "CaLaFe", "CaLaFe Ariavecchia": "CaLaFe",
    "Enderle &amp; Moll": "Enderle & Moll",
    # residual corrupt-split merges (producer name split across producer+wine cols)
    "Thörle Saulheimer": "Thörle", "Thorle Saulheimer": "Thörle",
    "Domaine de Cote Epine": "Domaine de la Côte Saint-Épine",
    "Domaine de la Cote St Epine": "Domaine de la Côte Saint-Épine",
    "Sprecher von": "Sprecher von Bernegg",
    "Max Geitlinger Wein": "Max Geitlinger",
    "Vigneti Valle": "Vigneti Valle Roncati",
    "Vini Marino": "Vini Marino Proclamo Cilento",
    "Philippe Nadeff": "Philippe Naddef", "Phillippe Naddef": "Philippe Naddef",
    "Domaine Philippe Naddef": "Philippe Naddef", "Domaine Philippe": "Philippe Naddef",
    "Laurent &": "Laurent Boussey",
    "Domaine de la Côte": "Domaine de la Côte Saint-Épine",
}
# names too generic/truncated to be a producer -> drop
FRAG = {"Domaine", "Domaine des", "Domaine de", "Bel", "Bel Air", "Cantina",
        "Cantina Del", "Cave", "Chateau", "Caves", "Cascina", "Cecllia Monte",
        "Caves Jean", "Cesare", "Achim", "Cantina Menegola",  # Menegola: 0 real wines
        # tangled importer-collab mis-parses (Lyle Fass = the Fass buyer, not a producer)
        "Lyle Fass Charalambos Lelektsoglou", "Lyle Fass/Charalambos",
        "Lyle Fass/Charalambos Lelektsoglou",
        "Hector Adrien Charalambos Lelektsoglou"}

COUNTRY_MAP = {"France": "France", "Germany": "Germany", "Italy": "Italy",
               "Switzerland": "Switzerland", "USA": "United States",
               "Southwest France": "France", "Spain": "Spain"}

REGION_MAP = {  # raw region -> (taxonomy region, sub_region or None)
    "Burgundy": ("Burgundy", None), "Rhône": ("Rhône", None),
    "Southern Rhône": ("Rhône", "Southern Rhône"), "Champagne": ("Champagne", None),
    "Loire": ("Loire", None), "Bordeaux": ("Bordeaux", None),
    "Beaujolais": ("Beaujolais", None), "Jura": ("Jura", None),
    "Savoie": ("Savoie", None), "Provence": ("Provence", None),
    "Cahors": ("South West", "Cahors"), "Southwest France": ("South West", None),
    "Mosel": ("Mosel", None), "Rheinhessen": ("Rheinhessen", None),
    "Baden": ("Baden", None), "Franken": ("Franken", None),
    "Franconia": ("Franken", None), "Nahe": ("Nahe", None),
    "Pfalz": ("Pfalz", None), "Rheingau": ("Rheingau", None),
    "Wurttemberg": ("Württemberg", None),
    "Piedmont": ("Piedmont", None), "Lombardy": ("Lombardy", None),
    "Campania": ("Campania", None), "Tuscany": ("Tuscany", None),
    "Trentino-Alto Adige": ("Alto Adige / Südtirol", None),
    "Molise": ("Molise", None), "Sicily": ("Sicily", None), "Umbria": ("Umbria", None),
    "Bierzo": ("Bierzo", None),
    "Graubunden": ("Graubünden", None), "Basel-Land": ("Basel-Land", None),
    "Eastern Switzerland": ("Eastern Switzerland", None), "Vully": ("Vully", None),
    "Willamette Valley": ("Oregon", "Willamette Valley"),
}
REGION_TAG = {  # region -> tag slug
    "Burgundy": "burgundy", "Rhône": "rhone", "Champagne": "champagne",
    "Mosel": "mosel", "Rheinhessen": "rheinhessen", "Baden": "baden",
    "Piedmont": "piedmont", "Loire": "loire", "Bordeaux": "bordeaux",
    "Beaujolais": "beaujolais", "Pfalz": "pfalz", "Nahe": "nahe",
    "Franken": "franken", "Lombardy": "lombardy",
}

def deacc(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c))

PREFIX = re.compile(r'^(domaine|chateau|weingut|maison|cantina|cave|caves|tenuta|azienda agricola|fattoria|podere)\s+', re.I)

def slugify(name):
    s = deacc(name).lower().strip()
    s = re.sub(r'[\'"`.]', '', s)
    stripped = PREFIX.sub('', s)
    if len(re.sub(r'[^a-z0-9]', '', stripped)) >= 3:  # don't over-truncate (e.g. "Podere Ai")
        s = stripped
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')

def load_taxonomy_regions():
    text = TAXONOMY.read_text(encoding="utf-8")
    block = re.search(r"##\s*`region`[^\n]*\n(.*?)(?=\n##\s)", text, re.DOTALL).group(1)
    out = {}
    for m in re.finditer(r"###\s*([^\n]+)\n(.*?)(?=\n###|\Z)", block, re.DOTALL):
        country = m.group(1).strip()
        regs = set(re.findall(r"^-\s*(.+)$", m.group(2), re.M))
        out[country] = {r.strip() for r in regs}
    return out

def is_year(s):
    return bool(re.match(r'^\d{4}$', str(s).strip()))

GROUP_STOP = {'de', 'du', 'des', 'la', 'le', 'les', "l", 'el', 'il', 'di', 'e', 'and',
              'the', 'et', 'da', 'dei', 'della', 'von', 'der', 'of', 'und',
              # producer-form prefixes & suffixes that fragment one estate into many keys
              'domaine', 'weingut', 'familie', 'maison', 'chateau', 'tenuta',
              'cantina', 'cave', 'caves', 'sarl', 'az', 'azienda', 'agricola',
              'fattoria', 'podere', 'vigneti', 'vini', 'caveau',
              'fils', 'pere', 'peres', 'freres', 'frere', 'amp', 'and', 'gmbh'}

KEYFIX = {'gunter': 'gunther', 'josef': 'joseph', 'rochhe': 'rocche',
          'phillippe': 'philippe', 'nadeff': 'naddef', 'st': 'saint', 'ste': 'sainte'}

def group_key(name):
    s = deacc(name).lower().replace('&amp;', ' and ').replace('&', ' and ')
    s = re.sub(r"['`.\-]", " ", s)
    toks = [KEYFIX.get(t, t) for t in re.findall(r'[a-z0-9]+', s) if t not in GROUP_STOP]
    return " ".join(toks)

JUNK = {"", "none", "#num!", "#ref!", "nan", "n/a"}

def clean_cuvee(wine, producer):
    if wine is None or str(wine).strip().lower() in JUNK:
        return None
    if re.fullmatch(r'[\d.\s]+', str(wine).strip()):  # numeric (a shifted vintage)
        return None
    w = str(wine)
    w = w.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    w = w.replace('´', "'")
    w = re.sub(r'\s+', ' ', w).strip()
    # strip duplicated leading producer name ("Pierre Brisset Vosne...")
    for tok in [producer, producer.split()[-1]]:
        if tok and w.lower().startswith(tok.lower() + ' '):
            w = w[len(tok)+1:].strip()
    # strip a parenthetical numeric id like "(5167)"
    w = re.sub(r'\s*\(\d{3,}\)\s*$', '', w).strip()
    return w

def vint(v):
    s = str(v).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

# ---- article matching ---------------------------------------------------
STOP = {"domaine", "maison", "weingut", "cantina", "cave", "caves", "tenuta",
        "azienda", "agricola", "fattoria", "podere", "the", "and", "fils",
        "pere", "et", "di", "de", "del", "della", "family", "familie"}

def load_articles():
    arts = []
    for p in sorted(ARTICLES_DIR.glob("*.md")):
        head = p.read_text(encoding="utf-8", errors="replace")
        tm = re.search(r'^title:\s*"?(.+?)"?\s*$', head, re.M)
        um = re.search(r'^url:\s*(\S+)', head, re.M)
        title = tm.group(1) if tm else p.stem
        url = um.group(1) if um else ""
        arts.append({"stem": p.stem, "title": title, "url": url, "path": p,
                     "hay": deacc(p.stem + " " + title).lower()})
    return arts

def match_article(canon, arts):
    toks = [t for t in re.findall(r'[a-z]+', deacc(canon).lower()) if len(t) >= 4 and t not in STOP]
    if not toks:
        return None
    best, best_score = None, 0
    for a in arts:
        score = sum(1 for t in toks if re.search(r'\b' + re.escape(t), a["hay"]))
        if score > best_score:
            best, best_score = a, score
    # require the most distinctive token (longest) to be present
    if best and best_score >= 1:
        longest = max(toks, key=len)
        if re.search(r'\b' + re.escape(longest), best["hay"]):
            return best
    return None

def article_excerpt(path):
    body = path.read_text(encoding="utf-8", errors="replace")
    body = body.split('---', 2)[-1]  # drop frontmatter
    paras = []
    for line in body.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('!['):
            continue
        line = line.replace('“', '"').replace('”', '"').replace('’', "'")
        if len(line) > 140:
            paras.append(line)
        if len(paras) >= 1:
            break
    if not paras:
        return None
    ex = paras[0]
    if len(ex) > 600:
        ex = ex[:600].rsplit(' ', 1)[0] + '…'
    return ex

# ---- main ---------------------------------------------------------------
def canon_name(p):
    return MERGE.get(p, p)

def main(apply):
    d = json.loads(PARSED.read_text())
    lookup, data = d["lookup"], d["data"]
    tax_regions = load_taxonomy_regions()
    arts = load_articles()

    # existing vault index for skip
    existing_slugs = {p.stem for p in PRODUCERS.glob("*.md")}
    existing_keys = set(existing_slugs)
    for p in PRODUCERS.glob("*.md"):
        existing_keys.add(slugify(p.stem.replace('_', ' ')))
        txt = p.read_text(encoding="utf-8", errors="replace")[:1200]
        nm = re.search(r'^name:\s*"?([^"\n]+)', txt, re.M)
        if nm:
            existing_keys.add(slugify(nm.group(1)))
        for m in re.findall(r'aliases:\s*\[(.*?)\]', txt):
            for a in re.findall(r'"([^"]+)"', m):
                existing_keys.add(slugify(a))

    # existing surname-only stubs (e.g. "steinmetz", "billon", "jasmin")
    existing_single = {s for s in existing_slugs if '_' not in s and len(s) >= 5}

    def in_vault(canon):
        sl = slugify(canon)
        if sl in existing_keys:
            return True
        # full Fass name (e.g. "gunther_steinmetz") vs existing surname stub
        if existing_single & set(sl.split('_')):
            return True
        return any(len(sl) > 4 and (sl == e or ((sl in e or e in sl) and abs(len(sl)-len(e)) <= 2))
                   for e in existing_keys)

    # global prefilter: drop corrupt "shifted" rows (year misread into price col)
    def price_of(r):
        try:
            return float(r['price'])
        except (TypeError, ValueError):
            return None
    data = [r for r in data if not (price_of(r) is not None and price_of(r) >= 1000)]

    # group rows by stopword-stripped key (merges "de l'Hermitage" spelling drift)
    groups = defaultdict(list)
    raw_variants = defaultdict(set)
    display = defaultdict(set)
    for r in data:
        std = lookup.get(str(r['producer']).strip(), str(r['producer']).strip())
        canon = canon_name(std)
        if canon in FRAG:
            continue
        key = group_key(canon)
        if not key:
            continue
        groups[key].append(r)
        raw_variants[key].add(str(r['producer']).strip())
        display[key].add(canon)

    # single-token bare-surname fragments: drop if subsumed by a fuller name
    # (another multi-token group, or an existing producer's last token)
    existing_last = set()
    for p in PRODUCERS.glob("*.md"):
        existing_last.add(p.stem.split('_')[-1])
        existing_last.add(slugify(p.stem.replace('_', ' ')).split('_')[-1])
    multi_last = {k.split()[-1] for k in groups if len(k.split()) > 1}
    fragment_tokens = (existing_last | multi_last) - {''}

    created, skipped, held = [], [], []
    for key, rows in sorted(groups.items()):
        # canonical display = the most complete (longest) variant seen
        canon = max(display[key], key=lambda s: (len(s), s))
        if len(key.split()) == 1 and key in fragment_tokens:
            skipped.append((canon, "fragment"))
            continue
        if in_vault(canon):
            skipped.append((canon, "in-vault"))
            continue
        slug = slugify(canon)
        path = PRODUCERS / f"{slug}.md"
        if path.exists():
            skipped.append((canon, "file-exists"))
            continue
        # country
        cc = Counter(COUNTRY_MAP[str(r['country'])] for r in rows if str(r['country']) in COUNTRY_MAP)
        if not cc:
            held.append((canon, "no-country"))
            continue
        country = cc.most_common(1)[0][0]
        valid = tax_regions.get(country, set())
        # region: most common mappable region valid for chosen country
        rc = Counter()
        for r in rows:
            raw = str(r['region'])
            if raw in REGION_MAP and REGION_MAP[raw][0] in valid:
                rc[raw] += 1
        if not rc:
            # fall back to any mappable region (country mismatch tolerated -> re-pick country)
            for r in rows:
                raw = str(r['region'])
                if raw in REGION_MAP:
                    reg = REGION_MAP[raw][0]
                    for c2, regs in tax_regions.items():
                        if reg in regs:
                            rc[raw] += 1
            if rc:
                raw_top = rc.most_common(1)[0][0]
                reg = REGION_MAP[raw_top][0]
                country = next(c2 for c2, regs in tax_regions.items() if reg in regs)
            else:
                held.append((canon, "no-region"))
                continue
        raw_top = rc.most_common(1)[0][0]
        region, sub_region = REGION_MAP[raw_top]
        # finer subregion from data if present and different
        all_regions = {r for regs in tax_regions.values() for r in regs}
        subs = Counter(str(r['subregion']) for r in rows
                       if r['subregion'] and str(r['subregion']) not in (region, country, 'None', raw_top))
        if not sub_region and subs:
            cand = subs.most_common(1)[0][0]
            # reject region-bleed (a real region elsewhere) and junk
            if (cand and cand not in valid and cand not in all_regions
                    and cand.lower() not in JUNK and not cand.isdigit()
                    and cand not in COUNTRY_MAP and cand not in COUNTRY_MAP.values()):
                sub_region = cand
        # dedupe cuvees
        cuvees = {}
        for r in rows:
            cv = clean_cuvee(r['wine'], canon)
            if not cv:
                continue
            key = re.sub(r'[^a-z0-9]', '', deacc(cv).lower())
            e = cuvees.setdefault(key, {"name": cv, "vints": set(), "prices": []})
            if len(cv) > len(e["name"]):
                e["name"] = cv
            v = vint(r['vintage'])
            e["vints"].add(v if is_year(v) else "NV")
            try:
                pr = float(r['price'])
                if 3 < pr < 1000:  # drop $1.99 errors and year-as-price misparses
                    e["prices"].append(pr)
            except (TypeError, ValueError):
                pass
        allprices = [p for e in cuvees.values() for p in e["prices"]]
        if not allprices:
            held.append((canon, "no-price"))
            continue
        pmin, pmax = min(allprices), max(allprices)
        vints_all = sorted({v for e in cuvees.values() for v in e["vints"] if re.match(r'\d{4}$', v)})
        span = f"{vints_all[0]}–{vints_all[-1]}" if len(vints_all) > 1 else (vints_all[0] if vints_all else "NV")

        art = match_article(canon, arts)
        page = render(canon, slug, sorted(raw_variants[key] - {canon}), country,
                      region, sub_region, cuvees, pmin, pmax, span, region_tag(region), art)
        if apply:
            path.write_text(page, encoding="utf-8")
        created.append((canon, slug, country, region, len(cuvees), "art" if art else ""))

    # report
    print(f"created: {len(created)}  skipped: {len(skipped)}  held: {len(held)}")
    if held:
        print("\nHELD (need manual region/country/price):")
        for h in held:
            print("  ", h[0], "—", h[1])
    print(f"\nwith editorial article: {sum(1 for c in created if c[5]=='art')}")
    Path("build").mkdir(exist_ok=True)
    rep = ["# Fass producer creation report", "",
           f"created **{len(created)}**, skipped {len(skipped)}, held {len(held)}", "",
           "| Producer | Slug | Country | Region | Cuvées | Article |", "|---|---|---|---|---|---|"]
    for c in sorted(created):
        rep.append(f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {'✓' if c[5] else ''} |")
    if held:
        rep += ["", "## Held back", ""] + [f"- {h[0]} — {h[1]}" for h in held]
    (ROOT / "build" / "fass_creates_report.md").write_text("\n".join(rep) + "\n")
    print("wrote build/fass_creates_report.md")

def region_tag(region):
    return REGION_TAG.get(region, deacc(region).lower().replace(' ', '-').replace('/', '-'))

def render(canon, slug, aliases, country, region, sub_region, cuvees, pmin, pmax, span, rtag, art):
    al = ", ".join(f'"{a}"' for a in sorted(aliases))
    rows = sorted(cuvees.values(), key=lambda e: (min(e["prices"]) if e["prices"] else 0))
    table = []
    for e in rows:
        yrs = sorted(v for v in e["vints"] if is_year(v))
        vs = ", ".join(yrs) if yrs else "NV"
        if e["prices"]:
            lo, hi = min(e["prices"]), max(e["prices"])
            price = f"${lo:.0f}" if abs(lo-hi) < 0.5 else f"${lo:.0f}–{hi:.0f}"
        else:
            price = "—"
        table.append(f"| {e['name']} | {vs} | {price} |")
    sub_disp = f"{region} / {sub_region}" if sub_region else region
    tags = f'["{rtag}", "fass"]'
    fm = [
        "---", "type: producer", f'name: "{canon}"', f"slug: {slug}",
        f"aliases: [{al}]", "", f'country: "{country}"', f'region: "{region}"',
        f'sub_region: "{sub_region or ""}"', "appellations: []", "",
        "farming: []", "certifications: []", "", 'importer_us: ["Fass Selections"]', "",
        "retailers:", "  chambers:", "    championed: false", "    article_count: 0",
        "  dte:", "    in_portfolio: false", "  raeders:", "    in_portfolio: false",
        "  fass:", "    in_portfolio: true", f"    cuvee_count: {len(cuvees)}",
        f"    price_min: {pmin:.0f}", f"    price_max: {pmax:.0f}",
        f"tags: {tags}", '_sources: ["fass:Fass File.xlsx (Cleaned Inventory, Spring 2025 offers)"]',
        "---", "",
    ]
    body = [
        f"# {canon}", "",
        f"_{sub_disp} producer offered through [[FASS_Selections|Fass Selections]]. "
        f"Seeded from the Fass Spring 2025 inventory; not yet covered in the CSW archive._", "",
        "## FASS", "",
        f"In portfolio: **{len(cuvees)} cuvée(s)** ({span}); prices **${pmin:.0f}–${pmax:.0f}**. "
        "_Source: Fass Selections offers (Spring 2025), deduplicated from the master inventory._", "",
        "| Cuvée | Vintage(s) | Price (USD) |", "|---|---|---|",
        *table, "",
    ]
    if art:
        ex = article_excerpt(art["path"])
        if ex:
            body += [f"## Fass Notes — {art['title']}", "", f"> {ex}", "",
                     f"_Source: [{art['title']}]({art['url']}), Fass Selections._", ""]
    body += ["## CSW Write-ups", "", "_Not yet covered in the CSW archive sweep._", "",
             "## Raeder's", "", "_Not yet populated._", ""]
    return "\n".join(fm + body)

if __name__ == "__main__":
    main("--apply" in sys.argv)
