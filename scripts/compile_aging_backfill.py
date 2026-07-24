"""
Backfill retailers.chambers.aging_score for CSW-covered producers that the
original CSW context primer never scored.

PROVENANCE NOTE — read before trusting these numbers.
The original aging_score values (87 producers) came from a one-time CSW context
primer (csw_context.txt) landed via compile_csw_cellar_signal.py — an LLM reading
actual Chambers Street article text. That primer no longer exists in the repo and
covered only ~121 of 829 producers, leaving 115 CSW-covered producers with no
score (or an explicit 0 placeholder). A 0/absent score therefore meant "not in
the primer," not "no aging potential" — a low-recall gap.

This pass EXTENDS recall. The scores below are curated judgment (Opus, 2026-07-23):
aging-CAPACITY by region/grape archetype, adjusted for producer tier and CSW
championing, calibrated to the 22 existing anchors (Olga Raffault/Breton 14 →
Chinon/Bourgueil benchmark; Baudry 13; Guion 12; Chevalerie 10; Éric Texier 8;
Gonon 7; 15-20yr agers 5-6; moderate 4). They are a heuristic, NOT Chambers'
literal verdict — so this is a mixed-provenance field from 2026-07-23 onward.

Rules:
  - GAP-FILL ONLY. Never overwrites an existing positive aging_score.
    Replaces an explicit 0; inserts where the key is absent.
  - Touches aging_score only. cellar_pick (a specific CSW editorial flag) is left
    exactly as found — not fabricated here.

Usage:
    python scripts/compile_aging_backfill.py            # dry-run + report
    python scripts/compile_aging_backfill.py --apply    # write
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "aging_backfill_report.md"

# slug -> curated aging_score (0-14). See module docstring for the rubric.
DECISION = {
    # --- Bordeaux / SW / Provence (structural, long-aging classed growths) ---
    "chateau_lafite_rothschild": 14,
    "chateau_leoville_barton": 13,
    "chateau_palmer": 13,
    "chateau_calon_segur": 12,
    "chateau_gruaud_larose": 12,
    "domaine_de_chevalier": 12,
    "chateau_smith_haut_lafitte": 11,
    "chateau_le_puy": 11,
    "chateau_cantemerle": 9,
    "chateau_fonroque": 8,
    "clos_puy_arnaud": 6,
    "elian_da_ros": 5,
    "clos_cibonne": 5,
    "chateau_brandeau": 4,
    "domaine_uchida": 3,
    # --- California cult (age-worthy Napa/Sonoma) ---
    "screaming_eagle": 12,
    "kosta_browne": 4,
    # --- Piedmont + Italy reds/whites ---
    "lorenzo_accomasso": 12,
    "cavallotto": 12,
    "gravner": 12,
    "biondi_santi": 14,
    "domenico_clerico": 9,
    "ceretto": 9,
    "ferdinando_principiano": 9,
    "mastroberardino": 9,
    "borgo_del_tiglio": 7,
    "trediberri": 7,
    "doro_princic": 6,
    "ronchi_di_cialla": 6,
    "zidarich": 6,
    "masseria_del_pino": 5,
    "feudo_montoni": 5,
    "bonavita": 4,
    "montenidoli": 4,
    "i_fabbri": 4,
    # --- Champagne (prestige + grower) ---
    "dom_perignon": 12,
    "bollinger": 11,
    "pierre_peters": 7,
    "agrapart": 6,
    "larmandier_bernier": 6,
    "jacques_lassaigne": 6,
    "laherte": 5,
    "marguet": 5,
    "champagne_ponson": 4,
    "champagne_les_freres_mignon": 3,
    # --- Germany / Alsace / Baden / Bierzo ---
    "schafer-frohlich": 8,
    "heymann_lowenstein": 8,
    "diel": 6,
    "bernhard_huber": 6,
    "rudolf_furst": 6,
    "wasenhaus": 6,
    "rings": 5,
    "sven_enderle": 5,
    "steinmetz": 4,
    "melsheimer": 4,
    "laurent_barth": 4,
    "beck_hartweg": 4,
    "castro_ventosa": 4,
    # --- Burgundy (by level: GC/benchmark high, village mid) ---
    "domaine_leflaive": 10,
    "meo_camuzet": 10,
    "ramonet": 9,
    "cecile_tremblay": 8,
    "domaine_joseph_roty": 7,
    "lignier-michelot": 6,
    "domaine_duroche": 6,
    "heresztyn-mazzini": 6,
    "domaine_jean_chauvenet": 6,
    "michel_noellat": 6,
    "domaine_simon_bize": 5,
    "stephane_magnien": 5,
    "domaine_bart": 5,
    "berthaut-gerbet": 5,
    "amelie_berthaut": 5,
    "domaine_chantal_lescure": 5,
    "domaine_armand_heitz": 5,
    "domaine_pavelot": 5,
    "domaine_rossignol-fevrier": 5,
    "michel_mallard": 5,
    "sirugue": 5,
    "georges_glantenay": 5,
    "domaine_de_chassorney": 5,
    "domaine_laroche": 5,
    "domaine_celine_perrin": 4,
    "domaine_boisson": 4,
    "domaine_david_moreau": 4,
    "fanny_sabre": 4,
    "simon_colin": 4,
    "guillot_broux": 4,
    "domaine_chantereves": 4,
    "goisot": 4,
    "domaine_cheveau": 3,
    "dujardin": 3,
    "messager-germain": 3,
    # --- Beaujolais (cru gamay) ---
    "clos_de_la_roilette": 7,
    "desvignes": 6,
    "anthony_thevenet": 5,
    # --- Jura ---
    "domaine_marnes_blanches": 5,
    "domaine_de_saint_pierre": 5,
    "domaine_ratte": 4,
    "domaine_lulu_vigneron": 4,
    "domaine_pont_de_breux": 4,
    "les_granges_paquenesses": 4,
    "les_capriades": 2,
    # --- Rhône (N. Syrah long agers; CdP; Savoie) ---
    "jamet": 9,
    "jasmin": 7,
    "clos_du_mont_olivet": 7,
    "chapelle_st_theodoric": 7,
    "domaine_garon": 6,
    "vincent_paris": 6,
    "langlore": 5,
    "domaine_des_ardoisieres": 5,
    "dard__ribo": 4,
    # --- Basque ---
    "ilarria": 5,
    # --- Loire ---
    # bernard_baudry merged into domaine_baudry (2026-07-23) — domaine_baudry keeps its primer score 13
    "boulay": 5,
}

CHAMBERS_RE = re.compile(r"^  chambers:\s*$")
AGING_RE = re.compile(r"^    aging_score:\s*(\d+)\s*$")


def apply_one(path: Path, score: int) -> tuple[str, int | None]:
    """Return (action, old_value). action in skip_positive/updated_zero/inserted/no_chambers."""
    text = path.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split("\n")
    lines = [ln.rstrip("\r") for ln in lines]

    ch_idx = next((i for i, ln in enumerate(lines) if CHAMBERS_RE.match(ln)), None)
    if ch_idx is None:
        return "no_chambers", None

    end_idx = len(lines)
    for j in range(ch_idx + 1, len(lines)):
        if lines[j] and not lines[j].startswith("    "):
            end_idx = j
            break

    block = lines[ch_idx + 1:end_idx]
    pos = next((k for k, bl in enumerate(block) if AGING_RE.match(bl)), None)
    new_line = f"    aging_score: {score}"

    if pos is not None:
        old = int(AGING_RE.match(block[pos]).group(1))
        if old > 0:
            return "skip_positive", old
        block[pos] = new_line
        action = "updated_zero"
    else:
        block.append(new_line)
        old = None
        action = "inserted"

    new_lines = lines[:ch_idx + 1] + block + lines[end_idx:]
    path.write_text(nl.join(new_lines), encoding="utf-8")
    return action, old


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    results = []
    for slug, score in sorted(DECISION.items()):
        path = PRODUCERS / f"{slug}.md"
        if not path.exists():
            results.append((slug, score, "MISSING_FILE", None))
            continue
        if not args.apply:
            # dry-run: report intended action without writing
            text = path.read_text(encoding="utf-8")
            m = re.search(r"^\s*aging_score:\s*(\d+)\s*$", text, re.M)
            cur = int(m.group(1)) if m else None
            if cur and cur > 0:
                act = "skip_positive"
            elif cur == 0:
                act = "updated_zero"
            else:
                act = "inserted"
            results.append((slug, score, act, cur))
        else:
            act, old = apply_one(path, score)
            results.append((slug, score, act, old))

    from collections import Counter
    tally = Counter(r[2] for r in results)
    lines_out = ["# Aging-score backfill report", ""]
    lines_out.append(f"- decision-table size: {len(DECISION)}")
    for k, v in sorted(tally.items()):
        lines_out.append(f"- {k}: {v}")
    lines_out.append("")
    lines_out.append("| slug | score | action | old |")
    lines_out.append("|---|---|---|---|")
    for slug, score, act, old in sorted(results, key=lambda r: (-r[1], r[0])):
        lines_out.append(f"| {slug} | {score} | {act} | {old if old is not None else ''} |")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    print(("APPLIED" if args.apply else "DRY-RUN") + f" — {len(DECISION)} in table")
    for k, v in sorted(tally.items()):
        print(f"  {k}: {v}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
