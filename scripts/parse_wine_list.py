"""
Parse a raw wine list file into a normalized snapshot JSON.

Input:  raw/wine_lists/<slug>/raw/<YYYY-MM-DD>.{pdf,html,txt}
Output: raw/wine_lists/<slug>/snapshot_<YYYY-MM-DD>.json

The output shape is documented in raw/wine_lists/README.md. The key invariant
is that diff_wine_lists.py keys on `(producer_slug, cuvee_norm, vintage)` —
so producer_slug normalization is the load-bearing step.

For PDFs the script tries `pdftotext` (poppler-utils) first; if absent, it
looks for a sibling `<date>.txt` (pre-extracted) and uses that. If neither
exists, it errors with instructions for manual extraction.

Per-source parsers live in PARSERS. Each takes raw text (PDF→text or HTML)
and returns a list of WineEntry dicts. The shared `normalize_entry` pass
then fills in producer_slug + slug confidence against the vault index.

Usage:
    python scripts/parse_wine_list.py estela
    python scripts/parse_wine_list.py estela --date 2026-05-27
    python scripts/parse_wine_list.py estela --from-file path/to/file.pdf
    python scripts/parse_wine_list.py --all                  # parse every source's latest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

VAULT = Path(__file__).resolve().parent.parent
RAW_ROOT = VAULT / "raw" / "wine_lists"
PRODUCER_DIR = VAULT / "wiki" / "producers"


# ─── Producer slug normalization ─────────────────────────────────────────────
#
# Vault rules (CLAUDE.md):
#   - slug = lowercase, ASCII-folded, underscored
#   - strip common producer prefixes ("Domaine ", "Château ", "Weingut ", ...)

PREFIX_STRIPS = (
    r"^domaine\s+", r"^dom\.?\s+",
    r"^château\s+", r"^chateau\s+", r"^ch\.?\s+",
    r"^weingut\s+",
    r"^cantina\s+", r"^azienda\s+(agricola\s+)?", r"^tenuta\s+",
    r"^bodega\s+", r"^bodegas\s+",
    r"^maison\s+",
    r"^clos\s+",  # debatable — "Clos Rougeard" is canonically "rougeard" in some vaults; keep configurable
)


def _ascii_fold(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def slugify(producer_raw: str) -> str:
    """
    Normalize a raw producer string to a canonical (underscored) slug.

    The vault uses a mixed convention — most producers are underscored
    (`arnoux_lachaux`) but some keep hyphens (`arnot-roberts`,
    `beck-hartweg`). slugify always emits the underscored form;
    `_resolve_vault_slug` checks both variants against the actual vault
    index and returns whichever exists.

    Examples:
        "Domaine Roulot"             → "roulot"
        "Château Pichon Lalande"     → "pichon_lalande"
        "Weingut Dönnhoff"           → "donnhoff"
        "Arnoux-Lachaux"             → "arnoux_lachaux"
        "A.J. Adam"                  → "aj_adam"
    """
    s = producer_raw.strip()
    s = _ascii_fold(s)
    s = s.lower()
    for pat in PREFIX_STRIPS:
        s = re.sub(pat, "", s, count=1)
    s = re.sub(r"[.,'’]+", "", s)         # drop apostrophes/commas/periods
    s = re.sub(r"[^a-z0-9\s-]+", " ", s)  # other punctuation → space
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"-+", "_", s)             # canonical form uses underscores
    return s


_PRODUCER_INDEX: set[str] | None = None


def vault_producer_slugs() -> set[str]:
    """Cached set of existing wiki/producers/<slug>.md slugs."""
    global _PRODUCER_INDEX
    if _PRODUCER_INDEX is None:
        _PRODUCER_INDEX = {
            p.stem for p in PRODUCER_DIR.glob("*.md")
            if not p.stem.startswith("_")
        }
    return _PRODUCER_INDEX


def _resolve_vault_slug(canonical: str) -> str | None:
    """Given the canonical (underscored) slug, return the actual vault slug
    if a producer page exists in either underscore or hyphen form."""
    if not canonical:
        return None
    vault = vault_producer_slugs()
    if canonical in vault:
        return canonical
    hyphenated = canonical.replace("_", "-")
    if hyphenated in vault:
        return hyphenated
    return None


# ─── Wine entry data model ───────────────────────────────────────────────────

@dataclass
class WineEntry:
    raw_text: str
    producer_raw: str = ""
    producer_slug: str = ""
    producer_slug_confidence: str = "low"  # "high" if matches a vault page
    cuvee: str = ""
    vintage: int | None = None
    region: str = ""
    sub_region: str = ""
    price_usd: float | None = None
    by_the_glass: bool = False
    section: str = ""


def normalize_entry(e: WineEntry) -> WineEntry:
    if e.producer_raw and not e.producer_slug:
        e.producer_slug = slugify(e.producer_raw)
    resolved = _resolve_vault_slug(e.producer_slug)
    if resolved:
        e.producer_slug = resolved
        e.producer_slug_confidence = "high"
    else:
        e.producer_slug_confidence = "low"
    return e


# ─── Generic line-level extractors ───────────────────────────────────────────

VINTAGE_RE = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
NV_RE = re.compile(r"\b(NV|N\.V\.|MV|Multi\s*Vintage)\b", re.IGNORECASE)
PRICE_RE = re.compile(r"\$?\s*(\d{2,4})(?:\.\d{2})?\s*$")  # trailing $NNN
BTG_RE = re.compile(r"\b(glass|by\s*the\s*glass|btg|/\s*gl)\b", re.IGNORECASE)


def extract_vintage(line: str) -> tuple[int | None, str]:
    """Pull a 4-digit vintage out of a line. Returns (vintage, line_without_vintage)."""
    if NV_RE.search(line):
        return None, NV_RE.sub("", line, count=1).strip()
    m = VINTAGE_RE.search(line)
    if not m:
        return None, line
    return int(m.group(1)), (line[: m.start()] + line[m.end():]).strip()


def extract_price(line: str) -> tuple[float | None, str]:
    m = PRICE_RE.search(line)
    if not m:
        return None, line
    return float(m.group(1)), line[: m.start()].rstrip(" .—–-")


_TRIM_PUNCT = " ,;:—–-"


def split_producer_cuvee(line: str) -> tuple[str, str]:
    """
    Best-effort producer/cuvée split. Tries the obvious heuristics:
        "Producer, Cuvée"      → comma split
        "Producer — Cuvée"     → em-dash split
        "Producer "            → no cuvée
    Per-source parsers should override when they have better structure.
    """
    for sep in (", ", " — ", " – ", " - "):
        if sep in line:
            head, rest = line.split(sep, 1)
            return head.strip(_TRIM_PUNCT), rest.strip(_TRIM_PUNCT)
    return line.strip(_TRIM_PUNCT), ""


def parse_generic_line(raw: str, section: str = "") -> WineEntry | None:
    """
    Last-resort line-level parser. Used by per-source parsers when they've
    already split text into wine-shaped lines but don't have structural
    metadata. Returns None if the line doesn't look like a wine.
    """
    line = raw.strip()
    if len(line) < 8:
        return None
    if not re.search(r"[A-Za-z]{3}", line):
        return None

    btg = bool(BTG_RE.search(line))
    line = BTG_RE.sub("", line).strip()

    price, line = extract_price(line)
    vintage, line = extract_vintage(line)
    producer, cuvee = split_producer_cuvee(line)

    if not producer:
        return None

    return WineEntry(
        raw_text=raw.strip(),
        producer_raw=producer,
        cuvee=cuvee,
        vintage=vintage,
        price_usd=price,
        by_the_glass=btg,
        section=section,
    )


# ─── HTML helpers ────────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    """Walk HTML, emit (tag, text) tuples respecting block-level breaks."""
    BLOCK_TAGS = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5",
                  "h6", "section", "article"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs):
        if tag in ("script", "style"):
            self._skip_depth += 1
        elif tag == "br":
            self.parts.append("\n")
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str):
        if not self._skip_depth:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    out = "".join(parser.parts)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\n[ \t]+", "\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


# ─── PDF helpers ─────────────────────────────────────────────────────────────

def pdf_to_text(pdf_path: Path) -> str:
    """
    Try `pdftotext` (poppler-utils) → fall back to sibling `.txt` →
    error with extraction instructions.
    """
    txt_sibling = pdf_path.with_suffix(".txt")
    if txt_sibling.exists():
        return txt_sibling.read_text(encoding="utf-8", errors="replace")

    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode == 0:
            return proc.stdout
        print(f"  pdftotext failed: {proc.stderr.strip()}", file=sys.stderr)

    raise RuntimeError(
        f"Can't extract text from {pdf_path.name}.\n"
        f"  Either:\n"
        f"    1. Install poppler-utils so `pdftotext` is on PATH, or\n"
        f"    2. Extract the PDF text yourself and save to "
        f"{txt_sibling.relative_to(VAULT)}.\n"
        f"       (macOS: Preview → File → Export As Text. Or use any "
        f"online PDF→text tool.)"
    )


# ─── Per-source parsers ──────────────────────────────────────────────────────
#
# Each parser takes the raw text (already PDF→text-extracted or HTML→text)
# and returns a list of WineEntry. The shared `normalize_entry` pass fills in
# producer_slug + confidence.
#
# These are STARTER IMPLEMENTATIONS. Each one needs calibration against the
# first real fetch — the format-specific section headers, line shapes, and
# price columns vary. Update the section_re / line filtering as needed.

SECTION_HEADER_HINTS = (
    "champagne", "burgundy", "bourgogne", "loire", "rhône", "rhone", "bordeaux",
    "jura", "savoie", "alsace", "languedoc", "provence", "beaujolais",
    "piedmont", "piemonte", "tuscany", "toscana", "veneto", "friuli", "sicily",
    "rioja", "ribera", "priorat", "germany", "mosel", "rheingau", "pfalz",
    "austria", "wachau", "kamptal",
    "california", "oregon", "washington",
    "sparkling", "white", "red", "rosé", "rose", "orange", "dessert",
    "by the glass",
)


def _looks_like_section_header(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 80:
        return False
    low = s.lower()
    # all-caps short lines are usually section headers
    if s == s.upper() and len(s) < 50 and re.search(r"[A-Z]{3,}", s):
        return True
    return any(hint in low for hint in SECTION_HEADER_HINTS) and len(s.split()) <= 6


def _parse_text_with_sections(text: str) -> list[WineEntry]:
    """
    Generic line-by-line parser: detects section headers, runs each non-header
    line through parse_generic_line. Works decently for both restaurant PDFs
    and Squarespace HTML once converted to text.
    """
    entries: list[WineEntry] = []
    section = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _looks_like_section_header(line):
            section = line
            continue
        entry = parse_generic_line(line, section=section)
        if entry:
            entries.append(entry)
    return entries


def parse_chambers_pours(text: str) -> list[WineEntry]:
    """Chambers Street weekly pour PDF (poppler-extracted text)."""
    # TODO: calibrate against first real fetch. The list groups by region
    # and has a "Special Pours" callout that we may want to tag separately.
    return _parse_text_with_sections(text)


def parse_estela(text: str) -> list[WineEntry]:
    """Estela binwise PDF (poppler-extracted text)."""
    # TODO: calibrate. binwise output is usually a clean two-column layout
    # (wine description on the left, price on the right) — `pdftotext -layout`
    # preserves the columns, so generic parsing should largely work.
    return _parse_text_with_sections(text)


def parse_peasant(text: str) -> list[WineEntry]:
    """Peasant wine-list HTML → text."""
    # TODO: calibrate against first real fetch. Italian-only list — the
    # section headers are likely regions (Piedmont, Veneto, etc.).
    return _parse_text_with_sections(text)


def parse_claud(text: str) -> list[WineEntry]:
    """Claud wine page HTML → text."""
    # TODO: calibrate. May be an inline list, may be a PDF embed (in which case
    # update scrape_wine_lists.py to download the embedded PDF and change
    # source.md to source_format: pdf).
    return _parse_text_with_sections(text)


def parse_noreetuh(text: str) -> list[WineEntry]:
    """Noreetuh menu HTML → text (Squarespace)."""
    # TODO: calibrate. The page may show only "representative" selections; if
    # parsed count << 300, source.md notes the discrepancy.
    return _parse_text_with_sections(text)


PARSERS: dict[str, Callable[[str], list[WineEntry]]] = {
    "chambers_pours": parse_chambers_pours,
    "estela": parse_estela,
    "peasant": parse_peasant,
    "claud": parse_claud,
    "noreetuh": parse_noreetuh,
}


# ─── Pipeline glue ───────────────────────────────────────────────────────────

def _resolve_input(slug: str, snapshot_date: str | None,
                   from_file: Path | None) -> Path:
    if from_file:
        return from_file
    raw_dir = RAW_ROOT / slug / "raw"
    if not raw_dir.exists():
        raise FileNotFoundError(
            f"No raw/ dir for {slug}. Run scrape_wine_lists.py first or "
            f"drop a file at {raw_dir.relative_to(VAULT)}/<YYYY-MM-DD>.<ext>.")
    if snapshot_date:
        candidates = list(raw_dir.glob(f"{snapshot_date}.*"))
    else:
        candidates = sorted(raw_dir.iterdir(), key=lambda p: p.stat().st_mtime,
                            reverse=True)
        candidates = [p for p in candidates
                      if p.suffix.lower() in (".pdf", ".html", ".htm", ".txt")]
    if not candidates:
        raise FileNotFoundError(
            f"No raw file found for {slug}"
            + (f" on {snapshot_date}" if snapshot_date else "")
            + f" under {raw_dir.relative_to(VAULT)}/")
    return candidates[0]


def parse_one(slug: str, snapshot_date: str | None, from_file: Path | None,
              apply: bool) -> int:
    if slug not in PARSERS:
        print(f"ERROR: no parser registered for '{slug}'.", file=sys.stderr)
        return 2

    try:
        raw_path = _resolve_input(slug, snapshot_date, from_file)
    except FileNotFoundError as e:
        print(f"[{slug}] {e}", file=sys.stderr)
        return 1

    suffix = raw_path.suffix.lower()
    snapshot_date = snapshot_date or raw_path.stem

    raw_bytes = raw_path.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()

    print(f"[{slug}] parsing {raw_path.relative_to(VAULT)} "
          f"({len(raw_bytes):,} bytes, sha256:{sha[:12]})")

    if suffix == ".pdf":
        text = pdf_to_text(raw_path)
    elif suffix in (".html", ".htm"):
        text = html_to_text(raw_bytes.decode("utf-8", errors="replace"))
    else:  # .txt
        text = raw_bytes.decode("utf-8", errors="replace")

    entries = PARSERS[slug](text)
    entries = [normalize_entry(e) for e in entries]

    high = sum(1 for e in entries if e.producer_slug_confidence == "high")
    print(f"  parsed {len(entries)} wines — "
          f"{high} match existing vault producers, {len(entries) - high} new/unknown")

    out_path = RAW_ROOT / slug / f"snapshot_{snapshot_date}.json"
    payload = {
        "restaurant": _restaurant_block(slug),
        "snapshot_date": snapshot_date,
        "source_file": str(raw_path.relative_to(VAULT)),
        "source_format": suffix.lstrip("."),
        "source_sha256": sha,
        "parsed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wine_count": len(entries),
        "wines": [asdict(e) for e in entries],
    }

    if apply:
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  wrote {out_path.relative_to(VAULT)}")
    else:
        print(f"  (dry-run; pass --apply to write {out_path.relative_to(VAULT)})")
    return 0


def _restaurant_block(slug: str) -> dict:
    """Pull restaurant name + address from raw/wine_lists/<slug>/source.md frontmatter."""
    src = RAW_ROOT / slug / "source.md"
    out = {"slug": slug, "name": slug, "address": ""}
    if not src.exists():
        return out
    text = src.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.DOTALL)
    if not m:
        return out
    for line in m.group(1).splitlines():
        kv = re.match(r"^(name|address):\s*\"?([^\"]+)\"?\s*$", line)
        if kv:
            out[kv.group(1)] = kv.group(2).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("slug", nargs="?", help="Source slug (e.g. 'estela').")
    ap.add_argument("--all", action="store_true",
                    help="Parse every source's latest raw file.")
    ap.add_argument("--date", default=None,
                    help="Snapshot date to parse (default: most recent).")
    ap.add_argument("--from-file", type=Path, default=None,
                    help="Bypass the raw/ lookup and parse this file directly.")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write to disk (default: dry-run).")
    args = ap.parse_args()

    if args.all:
        targets = list(PARSERS.keys())
    elif args.slug:
        targets = [args.slug]
    else:
        ap.error("provide a slug or pass --all")

    rc = 0
    for slug in targets:
        rc |= parse_one(slug, args.date, args.from_file, args.apply)
    return rc


if __name__ == "__main__":
    sys.exit(main())
