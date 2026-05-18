"""
Merge cellaring signal from a CSW context primer into producer .md frontmatter.

Source format (one block per producer):

    Producer Name | Appellation [farming] via Importer
      CSW: N articles (YYYY-YYYY) * M dedicated * aging:K [STAR]CELLAR
      CELLAR: "<excerpt>"        # optional, only when aging > 0

Adds to each matched wiki/producers/<slug>.md:
  - frontmatter retailers.chambers.aging_score: int
  - frontmatter retailers.chambers.cellar_pick: bool   (the *CELLAR flag)
  - body "## CSW Cellar Note" section with the excerpt (when present)

Does NOT overwrite the existing article_count / dedicated_count / first_year /
last_year fields, even when csw_context.txt disagrees - the upstream
ingest_csw.py is authoritative for those. Disagreements are reported.

Usage:
    python scripts/compile_csw_cellar_signal.py <csw_context.txt>
    python scripts/compile_csw_cellar_signal.py <csw_context.txt> --apply
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
REPORT = VAULT / "build" / "csw_cellar_signal_report.md"


# ---------- parsing ----------

# Use Unicode bullet/dash classes so we work regardless of how the file encodes
# en-dash and middle-dot.
HEADER_RE = re.compile(
    r"^(?P<name>[^|]+?)\s*\|\s*"
    r"(?P<rest>.+?)\s*$"
)
CSW_RE = re.compile(
    r"^\s*CSW:\s*(?P<articles>\d+)\s+articles?\s*\("
    r"(?P<first>\d{4})\s*[-–—]\s*(?P<last>\d{4})\)\s*"
    r"[·•\*]\s*(?P<dedicated>\d+)\s+dedicated\s*"
    r"[·•\*]\s*aging:(?P<aging>\d+)"
    r"(?P<flag>\s*★?\s*CELLAR)?",
)
CELLAR_RE = re.compile(r'^\s*CELLAR:\s*"(?P<note>.+?)"\s*$')

FARMING_RE = re.compile(r"\[(?P<farming>[^\]]+)\]")
VIA_RE = re.compile(r"\bvia\s+(?P<importer>.+?)\s*$")


@dataclass
class CswEntry:
    raw_name: str
    appellation: str
    farming: list[str]
    importer: str
    articles: int
    dedicated: int
    first_year: int
    last_year: int
    aging_score: int
    cellar_pick: bool
    cellar_note: str = ""

    @property
    def slug_candidates(self) -> list[str]:
        return slug_candidates_for(self.raw_name)


def parse_context_file(path: Path) -> list[CswEntry]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    entries: list[CswEntry] = []

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Skip headers, comments, separators, region notes
        if (not line.strip()
            or line.startswith("#")
            or line.startswith("=")
            or line.startswith("-")
            or line.startswith("═")  # box-drawing horizontal
            or line.startswith("─")
            or line.startswith("REGION:")
            or line.startswith("NOTE:")
            or line.startswith("KEY INSIGHTS")
            or line.startswith("MOST CHAMPIONED")
            or line.startswith("TOP CELLAR PICKS")
            or line.startswith("BORDEAUX SELL")
            or line.startswith("CSW FARMING")
            or line.startswith("CSW IMPORTER")
            or line.startswith("END OF")
            or line.startswith("  ")  # detail line without producer header above
            ):
            i += 1
            continue

        # Try parsing a producer header: "Name | Appellation [farming] via Importer"
        if "|" not in line:
            i += 1
            continue
        name, rest = line.split("|", 1)
        name = name.strip()
        rest = rest.strip()
        if not name:
            i += 1
            continue

        farming = []
        m = FARMING_RE.search(rest)
        if m:
            farming = [f.strip() for f in m.group("farming").split("/")]
            rest_no_farming = (rest[:m.start()] + rest[m.end():]).strip()
        else:
            rest_no_farming = rest

        importer = ""
        m_via = VIA_RE.search(rest_no_farming)
        if m_via:
            importer = m_via.group("importer").strip()
            appellation = rest_no_farming[:m_via.start()].strip()
        else:
            appellation = rest_no_farming.strip()

        # Next non-blank line should be the CSW: line
        j = i + 1
        csw_line = None
        while j < n and not lines[j].strip():
            j += 1
        if j < n and "CSW:" in lines[j]:
            csw_line = lines[j]
        if csw_line is None:
            # Header without metric line - skip
            i += 1
            continue

        m_csw = CSW_RE.match(csw_line)
        if not m_csw:
            i += 1
            continue

        articles = int(m_csw.group("articles"))
        dedicated = int(m_csw.group("dedicated"))
        first = int(m_csw.group("first"))
        last = int(m_csw.group("last"))
        aging = int(m_csw.group("aging"))
        cellar_pick = m_csw.group("flag") is not None

        # Optional CELLAR: line
        note = ""
        k = j + 1
        while k < n and not lines[k].strip():
            k += 1
        if k < n:
            m_cellar = CELLAR_RE.match(lines[k])
            if m_cellar:
                note = m_cellar.group("note").strip()
                k += 1

        entries.append(CswEntry(
            raw_name=name,
            appellation=appellation,
            farming=farming,
            importer=importer,
            articles=articles,
            dedicated=dedicated,
            first_year=first,
            last_year=last,
            aging_score=aging,
            cellar_pick=cellar_pick,
            cellar_note=note,
        ))
        i = k
    return entries


# ---------- slug match ----------

PREFIXES = ["domaine ", "chateau ", "château ", "weingut ", "weiser ", "le ", "la "]


def fold_ascii(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def to_slug(s: str) -> str:
    s = fold_ascii(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def slug_candidates_for(name: str) -> list[str]:
    """Generate plausible slug candidates from a CSW name."""
    candidates: list[str] = []

    # Multi-name producers like "Julien Guillot / Vignes du Maynes" or
    # "Peter Lauer / Weingut Lauer" - try each part and the joined form.
    parts = [p.strip() for p in re.split(r"\s*/\s*", name)]
    pieces = parts + [name]

    for p in pieces:
        if not p:
            continue
        candidates.append(to_slug(p))
        # Also try without leading "Domaine "/"Chateau "/etc.
        low = p.lower()
        for pref in PREFIXES:
            if low.startswith(pref):
                candidates.append(to_slug(p[len(pref):]))
                break
        # And with "domaine_" prepended (e.g. "Forey" -> "domaine_forey")
        if not any(low.startswith(pref) for pref in PREFIXES):
            candidates.append("domaine_" + to_slug(p))

    # Joined form for slash-separated names: "gilles_jean_maxime_lafouge"
    if len(parts) > 1:
        joined = "_".join(to_slug(p) for p in parts if p)
        candidates.append(joined)
        # Also double-underscore form (existing convention)
        joined_dbl = "__".join(to_slug(p) for p in parts if p)
        candidates.append(joined_dbl)

    # Dedupe preserving order
    seen = set()
    out = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def compact(s: str) -> str:
    """Alphanumeric-only form for separator-agnostic matching."""
    return re.sub(r"[^a-z0-9]", "", fold_ascii(s).lower())


def match_entry(
    entry: CswEntry,
    slug_index: dict[str, Path],
    compact_index: dict[str, list[Path]],
) -> tuple[Path | None, list[Path]]:
    """Return (chosen_path, all_candidate_paths). chosen=None means ambiguous."""
    # Pass 1: exact slug match against any candidate
    hits: list[Path] = []
    for c in entry.slug_candidates:
        p = slug_index.get(c)
        if p and p not in hits:
            hits.append(p)

    # Pass 2: compact-form match (separator-agnostic)
    if not hits:
        cand_compacts = {compact(c) for c in entry.slug_candidates if c}
        # Also try compact of the raw name and de-prefixed forms
        cand_compacts.add(compact(entry.raw_name))
        for cc in cand_compacts:
            if cc and cc in compact_index:
                for p in compact_index[cc]:
                    if p not in hits:
                        hits.append(p)

    if len(hits) == 1:
        return hits[0], hits
    if len(hits) >= 2:
        # Prefer the slug whose first candidate matched - i.e. when CSW name
        # is "Domaine Rousset", prefer domaine_rousset.md over rousset.md.
        primary_cands = entry.slug_candidates[:2]  # first form is most specific
        for pc in primary_cands:
            for h in hits:
                if h.stem.lower() == pc:
                    return h, hits
        return None, hits
    return None, []


# ---------- frontmatter & body update ----------

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def upsert_chambers_keys(fm: str, aging_score: int, cellar_pick: bool) -> tuple[str, dict]:
    """Insert/update aging_score and cellar_pick under retailers.chambers.

    Returns (new_fm, change_dict).
    """
    changes = {}
    lines = fm.split("\n")

    # Locate the chambers: block (under retailers:)
    chambers_idx = None
    for i, ln in enumerate(lines):
        if re.match(r"^  chambers:\s*$", ln):
            chambers_idx = i
            break
    if chambers_idx is None:
        changes["error"] = "no_chambers_block"
        return fm, changes

    # Determine end of the chambers block (next line at <=2-space indent)
    end_idx = len(lines)
    for j in range(chambers_idx + 1, len(lines)):
        if lines[j] and not lines[j].startswith("    "):
            end_idx = j
            break

    block = lines[chambers_idx + 1:end_idx]
    # Find existing aging_score/cellar_pick lines
    aging_re = re.compile(r"^    aging_score:\s*(\d+)\s*$")
    pick_re = re.compile(r"^    cellar_pick:\s*(true|false)\s*$")
    aging_pos = pick_pos = None
    for k, bl in enumerate(block):
        if aging_re.match(bl):
            aging_pos = k
        if pick_re.match(bl):
            pick_pos = k

    new_aging = f"    aging_score: {aging_score}"
    new_pick = f"    cellar_pick: {'true' if cellar_pick else 'false'}"

    if aging_pos is None:
        block.append(new_aging)
        changes["aging_score"] = ("added", aging_score)
    else:
        old = block[aging_pos]
        if old != new_aging:
            changes["aging_score"] = ("updated", aging_score)
        block[aging_pos] = new_aging

    if pick_pos is None:
        block.append(new_pick)
        changes["cellar_pick"] = ("added", cellar_pick)
    else:
        old = block[pick_pos]
        if old != new_pick:
            changes["cellar_pick"] = ("updated", cellar_pick)
        block[pick_pos] = new_pick

    new_lines = lines[:chambers_idx + 1] + block + lines[end_idx:]
    return "\n".join(new_lines), changes


CELLAR_NOTE_HEADER = "## CSW Cellar Note"


def upsert_cellar_note_section(body: str, note: str) -> tuple[str, str]:
    """Insert/update '## CSW Cellar Note' section. Inserts after '## CSW Write-ups'
    block (if present) or before '## Down to Earth' / first '## ' header.

    Returns (new_body, action).
    """
    if not note:
        return body, "skip_empty"

    # Quote-escape: replace any unescaped " with smart-quote-ish equivalents
    safe_note = note.replace("\\", "\\\\")
    section_text = f"\n{CELLAR_NOTE_HEADER}\n\n> {safe_note}\n"

    # If section already exists, replace it
    existing_re = re.compile(
        rf"\n{re.escape(CELLAR_NOTE_HEADER)}\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    if existing_re.search(body):
        new_body = existing_re.sub(section_text.rstrip("\n"), body)
        return new_body, "updated"

    # Insert before next "## " header following "## CSW Write-ups"
    csw_idx = body.find("## CSW Write-ups")
    if csw_idx >= 0:
        # Find the next "## " after csw_idx
        after_idx = body.find("\n## ", csw_idx + 1)
        if after_idx >= 0:
            new_body = body[:after_idx] + section_text + body[after_idx:]
            return new_body, "inserted_after_csw"
        # CSW Write-ups is last section - append at end
        new_body = body.rstrip() + "\n" + section_text
        return new_body, "appended_after_csw"

    # No CSW Write-ups header - just append
    new_body = body.rstrip() + "\n" + section_text
    return new_body, "appended_eof"


# ---------- main ----------

def build_slug_index() -> tuple[dict[str, Path], dict[str, list[Path]]]:
    """Return (exact_index, compact_index)."""
    exact: dict[str, Path] = {}
    compact_idx: dict[str, list[Path]] = {}
    for p in sorted(PRODUCERS.glob("*.md")):
        stem = p.stem.lower()
        exact[stem] = p
        cc = compact(stem)
        compact_idx.setdefault(cc, []).append(p)
    return exact, compact_idx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Path to csw_context.txt")
    parser.add_argument("--apply", action="store_true", help="Write changes (default is dry-run)")
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        return 2

    entries = parse_context_file(src)
    print(f"Parsed {len(entries)} producer entries from {src.name}")

    slug_index, compact_index = build_slug_index()
    print(f"Vault has {len(slug_index)} producer files")

    matched: list[tuple[CswEntry, Path]] = []
    unmatched: list[CswEntry] = []
    ambiguous: list[tuple[CswEntry, list[Path]]] = []

    for e in entries:
        chosen, hits = match_entry(e, slug_index, compact_index)
        if chosen:
            matched.append((e, chosen))
        elif len(hits) >= 2:
            ambiguous.append((e, hits))
        else:
            unmatched.append(e)

    print(f"\nMatch results: {len(matched)} matched, {len(unmatched)} unmatched, "
          f"{len(ambiguous)} ambiguous (multiple candidates)")

    if unmatched:
        print("\n--- UNMATCHED (no producer file found) ---")
        for e in unmatched:
            print(f"  {e.raw_name}  [tried: {', '.join(e.slug_candidates[:5])}]")

    if ambiguous:
        print("\n--- AMBIGUOUS (multiple candidate files) ---")
        for e, hits in ambiguous:
            print(f"  {e.raw_name}")
            for h in hits:
                print(f"    -> {h.name}")

    # Disagreements between csw_context counts and existing chambers.article_count
    disagreements = []
    for e, path in matched:
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^\s*article_count:\s*(\d+)\s*$", text, re.MULTILINE)
        existing = int(m.group(1)) if m else None
        if existing is not None and existing != e.articles:
            disagreements.append((e.raw_name, path.name, existing, e.articles))
    if disagreements:
        print(f"\n--- COUNT DISAGREEMENTS ({len(disagreements)} -- not overwritten) ---")
        for name, fname, ex, new in disagreements[:20]:
            print(f"  {name}: vault={ex}, csw_context={new}  ({fname})")
        if len(disagreements) > 20:
            print(f"  ... and {len(disagreements) - 20} more")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write changes.")
        return 0

    # Apply
    write_count = 0
    for e, path in matched:
        text = path.read_text(encoding="utf-8")
        split = split_frontmatter(text)
        if split is None:
            print(f"  skip (no frontmatter): {path.name}")
            continue
        fm, body = split
        new_fm, fm_changes = upsert_chambers_keys(fm, e.aging_score, e.cellar_pick)
        new_body, body_action = upsert_cellar_note_section(body, e.cellar_note)
        new_text = f"---\n{new_fm}\n---\n{new_body}"
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            write_count += 1
    print(f"\nWrote {write_count} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
