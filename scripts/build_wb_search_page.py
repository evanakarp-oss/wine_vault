"""
Build a self-contained, offline searchable HTML page for a Wine Berserkers
thread tally. One row per producer with mentions, per-era counts, 2023+
momentum, and vault/cellar status — searchable + sortable client-side, no
network or build step needed to view (just open the .html).

Reuses the slug-matching + cellar join from build_wb_rollups so the vault/
cellar flags match the _views rollups exactly.

Usage:
    python scripts/build_wb_search_page.py                 # dry-run (prints path)
    python scripts/build_wb_search_page.py --apply         # write the .html
    python scripts/build_wb_search_page.py --thread top10_in_cellar --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_wb_rollups import (  # noqa: E402
    build_indices, find_path, cellar_counts, producer_info, _now_iso_date,
)
from parse_wb_thread import normalize_for_alias  # noqa: E402

VAULT = Path(__file__).resolve().parent.parent
THREADS = VAULT / "raw" / "berserkers" / "threads"
VIEWS = VAULT / "wiki" / "_views"
REGION_TSV = VAULT / "raw" / "berserkers" / "producer_regions.tsv"


def load_region_map() -> dict[str, tuple[str, str]]:
    """Curated fallback country/region for producers with no vault page.
    Returns a dict keyed by BOTH the exact raw_name and its normalized form
    (accent/prefix/paren-insensitive) so lookups are forgiving. Vault-page
    region always wins over this."""
    out: dict[str, tuple[str, str]] = {}
    if not REGION_TSV.exists():
        return out
    for line in REGION_TSV.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            name, val = parts[0].strip(), (parts[1].strip(), parts[2].strip())
            out[name] = val
            out.setdefault(normalize_for_alias(name), val)
    return out


def build_rows(producers, exact, cidx, cellar, region_map):
    rows = []
    for p in producers:
        path = find_path(p["raw_name"], exact, cidx)
        slug = path.stem if path else None
        info = producer_info(path) if path else {}
        region = info.get("region", "")
        country = info.get("country", "")
        if not region:  # fall back to the curated map (exact, then normalized)
            hit = region_map.get(p["raw_name"]) or region_map.get(normalize_for_alias(p["raw_name"]))
            if hit:
                country, region = hit
        bottles = cellar.get(slug, 0) if slug else 0
        score = p.get("momentum_score_2023")
        # Sort key for momentum: null -> -1, new entrant (inf) -> 999.
        if score is None:
            mom_val, mom_disp = -1.0, "—"
        elif score == float("inf") or score == "inf":
            mom_val, mom_disp = 999.0, "new"
        else:
            mom_val, mom_disp = float(score), f"{float(score):g}×"
        rows.append({
            "rank": p.get("rank"),
            "name": p["raw_name"],
            "slug": slug or "",
            "mentions": p.get("mentions", 0),
            "e1": p.get("mentions_2013_2014"),
            "e2": p.get("mentions_2021_2022"),
            "e3": p.get("mentions_2023_2026"),
            "mom": mom_val,
            "momd": mom_disp,
            "vault": bool(path),
            "cellar": bottles,
            "region": region,
            "country": country,
        })
    return rows


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Berserkers search</title>
<style>
  :root {{ --bg:#faf8f5; --fg:#2a2320; --mut:#8a7f76; --line:#e7ddd2;
          --accent:#7b2d26; --chip:#efe7db; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
          font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
  header {{ position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line);
           padding:14px 18px 10px; z-index:5; }}
  h1 {{ margin:0 0 2px; font-size:19px; }}
  .sub {{ color:var(--mut); font-size:13px; margin-bottom:10px; }}
  .controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
  #q {{ flex:1 1 240px; min-width:180px; padding:9px 12px; font-size:15px;
        border:1px solid var(--line); border-radius:8px; background:#fff; }}
  .chip {{ padding:7px 11px; border:1px solid var(--line); border-radius:999px;
          background:#fff; cursor:pointer; font-size:13px; user-select:none; white-space:nowrap; }}
  .chip.on {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  #count {{ color:var(--mut); font-size:13px; margin-left:auto; }}
  .wrap {{ padding:0 8px 40px; }}
  table {{ border-collapse:collapse; width:100%; }}
  th,td {{ text-align:left; padding:7px 9px; border-bottom:1px solid var(--line); font-size:14px; }}
  th {{ position:sticky; top:0; background:var(--chip); cursor:pointer; white-space:nowrap;
       font-size:12px; text-transform:uppercase; letter-spacing:.03em; color:#5c534b; }}
  th.sorted::after {{ content:" ▾"; }}
  th.sorted.asc::after {{ content:" ▴"; }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  tr:hover td {{ background:#fff; }}
  .name {{ font-weight:600; }}
  .tag {{ font-size:11px; padding:1px 6px; border-radius:4px; margin-left:6px; vertical-align:1px; }}
  .tag.v {{ background:#e3efe0; color:#2f6d2a; }}
  .tag.c {{ background:#f3e2df; color:var(--accent); }}
  .mut {{ color:var(--mut); }}
  .surge {{ color:#2f6d2a; font-weight:600; }}
  .fade {{ color:#a05; }}
  .new {{ color:#2166a5; font-weight:600; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  @media (max-width:640px) {{ .hide-sm {{ display:none; }} }}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class="sub">{sub}</div>
  <div class="controls">
    <input id="q" type="search" placeholder="Search producer… (e.g. burlotto, keller, champagne)" autofocus>
    <label class="chip" style="cursor:default">min mentions
      <input id="minm" type="number" min="0" value="{minm}" style="width:48px;margin-left:6px;border:0;background:transparent;font:inherit"></label>
    <span class="chip" data-f="cellar">🍷 In my cellar</span>
    <span class="chip" data-f="vault">✅ Has page</span>
    <span class="chip" data-f="surge">↗ Surging</span>
    <span class="chip" data-f="fade">↘ Fading</span>
    <span class="chip" data-f="new">🆕 New</span>
    <span id="count"></span>
  </div>
  <div class="sub" style="margin:8px 0 0">{legend}</div>
</header>
<div class="wrap">
<table id="t">
<thead><tr>
  <th class="num" data-k="rank">#</th>
  <th data-k="name">Producer</th>
  <th class="num" data-k="mentions">Mentions</th>
  <th class="num hide-sm" data-k="e1">’13–14</th>
  <th class="num hide-sm" data-k="e2">’21–22</th>
  <th class="num hide-sm" data-k="e3">’23–26</th>
  <th class="num" data-k="mom">Momentum</th>
  <th class="hide-sm" data-k="country">Country</th>
  <th class="hide-sm" data-k="region">Region</th>
</tr></thead>
<tbody id="tb"></tbody>
</table>
</div>
<script>
const DATA = {data};
const REPO_PRODUCER = "../producers/"; // relative link to a page if it exists
let sortK = "{sortk}", sortAsc = {sortasc};
const filters = {{ cellar:false, vault:false, surge:false, fade:false, new:false }};
const tb = document.getElementById("tb"), q = document.getElementById("q"), count = document.getElementById("count");
const minm = document.getElementById("minm");

function momCell(r) {{
  if (r.momd === "—") return '<span class="mut">—</span>';
  if (r.momd === "new") return '<span class="new">🆕 new</span>';
  const cls = r.mom >= 1.2 ? "surge" : (r.mom < 0.5 ? "fade" : "");
  const arrow = r.mom >= 1.2 ? "↗ " : (r.mom < 0.5 ? "↘ " : "");
  return '<span class="'+cls+'">'+arrow+r.momd+'</span>';
}}
function n(v) {{ return (v===null||v===undefined) ? '<span class="mut">—</span>' : v; }}

function render() {{
  const term = q.value.trim().toLowerCase();
  let rows = DATA.filter(r => {{
    if (term && !(r.name.toLowerCase().includes(term) ||
                  (r.region||"").toLowerCase().includes(term) ||
                  (r.country||"").toLowerCase().includes(term))) return false;
    if (filters.cellar && !r.cellar) return false;
    if (filters.vault && !r.vault) return false;
    if (filters.surge && !(r.mom >= 1.2 && r.mom < 900)) return false;
    if (filters.fade && !(r.mom >= 0 && r.mom < 0.5)) return false;
    if (filters.new && r.momd !== "new") return false;
    const mm = parseInt(minm.value||"0", 10);
    if (mm && r.mentions < mm) return false;
    return true;
  }});
  rows.sort((a,b) => {{
    let x=a[sortK], y=b[sortK];
    if (typeof x === "string") {{ x=x.toLowerCase(); y=(y||"").toLowerCase(); }}
    if (x===null||x===undefined) x = -Infinity;
    if (y===null||y===undefined) y = -Infinity;
    return (x<y?-1:x>y?1:0) * (sortAsc?1:-1);
  }});
  count.textContent = rows.length + " of " + DATA.length + " producers";
  tb.innerHTML = rows.map(r => {{
    const name = r.vault
      ? '<a href="'+REPO_PRODUCER+r.slug+'.md">'+r.name+'</a>'
      : r.name;
    const tags = (r.vault?'<span class="tag v">page</span>':'') +
                 (r.cellar?'<span class="tag c">🍷 '+r.cellar+'</span>':'');
    return '<tr>'+
      '<td class="num mut">'+(r.rank??"")+'</td>'+
      '<td class="name">'+name+tags+'</td>'+
      '<td class="num">'+r.mentions+'</td>'+
      '<td class="num hide-sm">'+n(r.e1)+'</td>'+
      '<td class="num hide-sm">'+n(r.e2)+'</td>'+
      '<td class="num hide-sm">'+n(r.e3)+'</td>'+
      '<td class="num">'+momCell(r)+'</td>'+
      '<td class="hide-sm mut">'+(r.country||"")+'</td>'+
      '<td class="hide-sm mut">'+(r.region||"")+'</td>'+
    '</tr>';
  }}).join("");
  document.querySelectorAll("th").forEach(th => {{
    th.classList.toggle("sorted", th.dataset.k===sortK);
    th.classList.toggle("asc", th.dataset.k===sortK && sortAsc);
  }});
}}
q.addEventListener("input", render);
minm.addEventListener("input", render);
document.querySelectorAll("th").forEach(th => th.addEventListener("click", () => {{
  const k = th.dataset.k;
  if (sortK===k) sortAsc = !sortAsc;
  else {{ sortK=k; sortAsc = (k==="name"||k==="region"); }}
  render();
}}));
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {{
  const f = c.dataset.f; filters[f]=!filters[f]; c.classList.toggle("on", filters[f]); render();
}}));
render();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thread", default="top10_in_cellar",
                    help="Thread slug (default: top10_in_cellar)")
    ap.add_argument("--apply", action="store_true", help="Write the .html (default: dry-run)")
    args = ap.parse_args()

    src = THREADS / f"{args.thread}.json"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    thread, producers = data["thread"], data["producers"]

    exact, cidx = build_indices()
    cellar = cellar_counts()
    region_map = load_region_map()
    rows = build_rows(producers, exact, cidx, cellar, region_map)
    data_json = json.dumps(rows, ensure_ascii=False)
    n_region = sum(1 for r in rows if r["region"])

    n_vault = sum(1 for r in rows if r["vault"])
    n_cellar = sum(1 for r in rows if r["cellar"])
    sub = (f'{thread.get("title","")} · '
           f'{thread.get("post_count","?")} posts · {len(rows)} producers · '
           f'{thread.get("total_mentions","?")} mentions · '
           f'{thread.get("first_post_date","")}–{thread.get("last_post_date","")} · '
           f'{n_vault} in vault · {n_cellar} owned · '
           f'<a href="{thread.get("url","")}">thread</a> · built {_now_iso_date()}')
    mom_legend = ("<b>Momentum</b> = mentions/era in <b>2023+</b> ÷ mentions in the producer's "
                  "earliest active era. ↗ ≥1.2 rising · ↘ &lt;0.5 fading · 🆕 no earlier baseline. "
                  "Bump <b>min mentions</b> to cut single-mention noise.")

    # (mode label, filename suffix, initial sort key, sort ascending?, default min-mentions, legend)
    variants = [
        ("search",   "search",        "mentions", False, 0, "Click a column to sort · tap a producer with a page to open it."),
        ("Momentum scan", "momentum_scan", "mom", False, 3, mom_legend),
    ]
    wrote = []
    for label, suffix, sortk, asc, minm, legend in variants:
        title = thread.get("title", "Wine Berserkers")
        if suffix != "search":
            title = f"{title} — {label}"
        html = HTML.format(
            title=title, sub=sub, data=data_json, legend=legend,
            minm=minm, sortk=sortk, sortasc="true" if asc else "false",
        )
        out = VIEWS / f"wb_{args.thread}_{suffix}.html"
        wrote.append(out)
        if args.apply:
            out.write_text(html, encoding="utf-8")

    print(f"{len(rows)} rows · {n_vault} vault · {n_cellar} cellar")
    for o in wrote:
        print(("Wrote " if args.apply else "would write ") + str(o) +
              (f" ({o.stat().st_size // 1024} KB)" if args.apply else ""))
    if not args.apply:
        print("Dry-run. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
