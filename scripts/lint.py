"""
Lint the wine_vault/ structure against _SCHEMA.md and _TAXONOMY.md.

Checks (no auto-fix unless --fix is passed):
  1. Non-ASCII / mojibake in producer filenames → rename to folded slug (--fix)
     + update all wikilinks that referenced the old slug.
  2. Producer slug ≠ filename stem.
  3. country not in taxonomy list.
  4. region not in taxonomy list for that country (over-granular regions like
     "Barolo, Monforte" get flagged with a suggested parent).
  5. Empty region.
  6. Duplicate producers (two files with the same canonical_name after slug
     normalization and the same retailer stats — likely migration dupes).
  7. CSW surname collisions: producers whose canonical_slug ends with the
     same token as another producer's slug (e.g. bernard_baudry / matthieu_baudry
     / domaine_baudry all share "baudry" — these pages likely share CSW matches
     spuriously). High-coverage offenders only.
  8. Broken [[wikilink]] targets in producer bodies.

Output: build/lint_report.md (always) and a compact stdout summary.

Usage:
    python scripts/lint.py            # report only
    python scripts/lint.py --fix      # apply safe auto-fixes (slug renames)
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
WIKI = VAULT / "wiki"
PRODUCERS = WIKI / "producers"
TAXONOMY_FILE = WIKI / "_TAXONOMY.md"
CELLAR = VAULT / "cellar"
REGIONS_DIR = WIKI / "regions"
IMPORTERS_DIR = WIKI / "importers"
RETAILERS_DIR = WIKI / "retailers"
REPORT = VAULT / "build" / "lint_report.md"

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]+)?\]\]")


def ascii_slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s)
    s = re.sub(r"[\s-]+", "_", s).strip("_")
    return s


def split_frontmatter(text: str):
    m = FM_RE.match(text)
    return (m.group(1), m.group(2)) if m else None


def get_str(fm: str, key: str) -> str:
    m = re.search(rf'^{re.escape(key)}:\s*"?([^"\n]*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_bool_under(fm: str, block: str, key: str) -> bool:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(true|false)"
    m = re.search(pat, fm, re.MULTILINE)
    return bool(m) and m.group(1) == "true"


def get_int_under(fm: str, block: str, key: str) -> int:
    pat = rf"^  {block}:\n(?:    [^\n]*\n)*?    {re.escape(key)}:\s*(\d+)"
    m = re.search(pat, fm, re.MULTILINE)
    return int(m.group(1)) if m else 0


# --- taxonomy loader ---

@dataclass
class Taxonomy:
    countries: set[str] = field(default_factory=set)
    regions_by_country: dict[str, set[str]] = field(default_factory=dict)

    @property
    def all_regions(self) -> set[str]:
        out = set()
        for rs in self.regions_by_country.values():
            out |= rs
        return out


def load_taxonomy() -> Taxonomy:
    text = TAXONOMY_FILE.read_text(encoding="utf-8")
    t = Taxonomy()
    # countries under "## `country`"
    m = re.search(r"##\s*`country`\n(.*?)(?=\n##\s)", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                t.countries.add(line[2:].strip())
    # regions under "## `region` (indexed by country)" ... "### <Country>"
    region_block = re.search(
        r"##\s*`region`[^\n]*\n(.*?)(?=\n##\s)", text, re.DOTALL
    )
    if region_block:
        for section in re.finditer(
            r"###\s*([^\n]+)\n(.*?)(?=\n###|\Z)", region_block.group(1), re.DOTALL
        ):
            country = section.group(1).strip()
            regs = set()
            for line in section.group(2).splitlines():
                line = line.strip()
                if line.startswith("- "):
                    regs.add(line[2:].strip())
            t.regions_by_country[country] = regs
    return t


# --- region normalization hints ---

REGION_PREFIX_HINTS: list[tuple[str, str]] = [
    # (prefix of raw region value, suggested parent region)
    ("Barolo", "Piedmont"),
    ("Barbaresco", "Piedmont"),
    ("Serralunga", "Piedmont"),
    ("Mosel", "Mosel"),
    ("Saar", "Mosel"),
    ("Ruwer", "Mosel"),
    ("Chianti", "Tuscany"),
    ("Brunello", "Tuscany"),
    ("Bolgheri", "Tuscany"),
    ("Etna", "Sicily"),
    ("Vittoria", "Sicily"),
    ("Faro", "Sicily"),
    ("Alsace", "Alsace"),
    ("Bennwihr", "Alsace"),
    ("Verduno", "Piedmont"),
    ("Monforte", "Piedmont"),
    ("Castiglione", "Piedmont"),
    ("Neive", "Piedmont"),
    ("La Morra", "Piedmont"),
    ("Dhron", "Mosel"),
    ("Enkirch", "Mosel"),
    ("Graach", "Mosel"),
    ("Pünderich", "Mosel"),
    ("Winningen", "Mosel"),
    ("Wolf", "Mosel"),
    ("Konz", "Mosel"),
    ("Saarburg", "Mosel"),
    ("Colli Tortonesi", "Colli Tortonesi"),
    ("Timorasso", "Colli Tortonesi"),
    ("Liguria", "Liguria"),
    ("Riviera Ligure", "Liguria"),
    ("Irouléguy", "Basque (Irouléguy)"),
]


def suggest_parent_region(raw: str) -> str | None:
    for prefix, parent in REGION_PREFIX_HINTS:
        if prefix.lower() in raw.lower():
            return parent
    return None


# --- lint issues ---

@dataclass
class Issue:
    kind: str
    path: str
    detail: str


def find_mojibake_filenames() -> list[Path]:
    """Producer files whose stem contains non-ASCII bytes (migration artifacts)."""
    out = []
    for p in PRODUCERS.glob("*.md"):
        if not p.stem.isascii():
            out.append(p)
    return out


def rename_mojibake(paths: list[Path]) -> list[tuple[Path, Path, str]]:
    """Rename each to ascii_slug(stem). Returns list of (old, new, status)."""
    results = []
    used = {p.name for p in PRODUCERS.glob("*.md")}
    for old in paths:
        # Try to parse frontmatter name first (cleanest source)
        text = old.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        display_name = ""
        if parts:
            display_name = get_str(parts[0], "name")
        new_stem = ascii_slug(display_name) if display_name else ascii_slug(old.stem)
        if not new_stem:
            results.append((old, old, "empty_slug_derived"))
            continue
        new_name = f"{new_stem}.md"
        if new_name == old.name:
            results.append((old, old, "already_ascii"))
            continue
        if new_name in used:
            results.append((old, PRODUCERS / new_name, "collision"))
            continue
        new_path = PRODUCERS / new_name
        # Update slug: inside the file to match
        if parts:
            fm, body = parts
            fm = re.sub(r"^slug:\s*.*$", f"slug: {new_stem}", fm, count=1,
                        flags=re.MULTILINE)
            text = f"---\n{fm}\n---\n{body}"
        new_path.write_text(text, encoding="utf-8")
        old.unlink()
        used.add(new_name)
        used.discard(old.name)
        results.append((old, new_path, "renamed"))
    return results


def update_wikilinks(rename_map: dict[str, str]) -> int:
    """Rewrite [[old_slug|...]] → [[new_slug|...]] across the vault."""
    if not rename_map:
        return 0
    count = 0
    for d in (PRODUCERS, REGIONS_DIR, IMPORTERS_DIR, RETAILERS_DIR, CELLAR):
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            text = p.read_text(encoding="utf-8", errors="replace")
            new_text = text
            for old, new in rename_map.items():
                new_text = re.sub(
                    rf"\[\[{re.escape(old)}(\||\])",
                    lambda m, nn=new: f"[[{nn}{m.group(1)}",
                    new_text,
                )
            if new_text != text:
                p.write_text(new_text, encoding="utf-8")
                count += 1
    return count


# --- main ---

def run(fix: bool) -> int:
    issues: list[Issue] = []
    tax = load_taxonomy()

    producer_files = sorted(PRODUCERS.glob("*.md"))
    producer_slugs = {p.stem for p in producer_files}

    # 1. Mojibake filenames
    mojibake = find_mojibake_filenames()
    rename_summary: list[tuple[Path, Path, str]] = []
    if mojibake:
        if fix:
            rename_summary = rename_mojibake(mojibake)
            rename_map = {
                old.stem: new.stem
                for old, new, status in rename_summary
                if status == "renamed"
            }
            touched = update_wikilinks(rename_map)
            print(f"  renamed {sum(1 for _, _, s in rename_summary if s == 'renamed')} "
                  f"mojibake files, updated {touched} files with wikilinks")
            # refresh producer_files after renames
            producer_files = sorted(PRODUCERS.glob("*.md"))
            producer_slugs = {p.stem for p in producer_files}
        else:
            for p in mojibake:
                issues.append(Issue("mojibake_filename", p.name,
                                     f"Non-ASCII in filename → run with --fix"))

    # Per-producer checks
    canonical_names: dict[str, list[str]] = defaultdict(list)
    signatures: dict[tuple, list[str]] = defaultdict(list)
    broken_links: list[tuple[str, str]] = []

    for p in producer_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            issues.append(Issue("no_frontmatter", p.name, "file missing YAML frontmatter"))
            continue
        fm, body = parts
        if get_str(fm, "type") != "producer":
            continue
        slug = get_str(fm, "slug")
        name = get_str(fm, "name")
        country = get_str(fm, "country")
        region = get_str(fm, "region")

        # 2. slug vs filename
        if slug and slug != p.stem:
            issues.append(Issue("slug_mismatch", p.name,
                                 f"frontmatter slug='{slug}' does not match filename stem"))

        # 3. country
        if country and country not in tax.countries:
            issues.append(Issue("country_unknown", p.name,
                                 f"country='{country}' not in _TAXONOMY.md"))

        # 4. region
        if region:
            valid_regions = tax.regions_by_country.get(country, set())
            if country and valid_regions and region not in valid_regions:
                suggested = suggest_parent_region(region)
                issues.append(Issue(
                    "region_not_in_taxonomy", p.name,
                    f"region='{region}' not in allowed list for {country}. "
                    f"Suggested parent: {suggested or '(unknown)'}; "
                    "keep original in sub_region."
                ))
        else:
            # 5. empty region
            issues.append(Issue("region_empty", p.name,
                                 "region is empty — needed for rollup grouping"))

        # 6. dup detection: group by normalized name + identical CSW stats
        if name:
            canonical_names[ascii_slug(name)].append(p.stem)
        sig = (
            ascii_slug(name),
            get_int_under(fm, "chambers", "article_count"),
            get_int_under(fm, "chambers", "dedicated_count"),
            get_int_under(fm, "chambers", "first_year"),
            get_int_under(fm, "chambers", "last_year"),
        )
        if any(sig[1:]):  # only track if there's actual CSW data
            signatures[sig].append(p.stem)

        # 8. broken wikilinks (only ones pointing at producer slugs)
        for m in WIKILINK_RE.finditer(body):
            target = m.group(1).strip()
            # Only flag if it looks like a producer slug (lowercase_words)
            if re.fullmatch(r"[a-z0-9_\-]+", target) and target not in producer_slugs:
                broken_links.append((p.name, target))

    # 6b. Dupes: same sig and >1 file
    for sig, slugs in signatures.items():
        if len(slugs) > 1:
            issues.append(Issue("duplicate_producer", ",".join(slugs),
                                 f"same name+CSW sig ({sig[1]} articles): "
                                 f"merge candidates"))

    # 7. Surname collisions on CSW
    by_last_token: dict[str, list[str]] = defaultdict(list)
    coverage: dict[str, int] = {}
    aliases_map: dict[str, list[str]] = {}
    for p in producer_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, _ = parts
        articles = get_int_under(fm, "chambers", "article_count")
        if articles == 0:
            continue
        coverage[p.stem] = articles
        # Capture aliases for cross-page disambiguation check
        am = re.search(r'^aliases:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
        if am and am.group(1).strip():
            aliases_map[p.stem] = re.findall(r'"([^"]*)"', am.group(1))
        else:
            aliases_map[p.stem] = []
        tokens = [t for t in re.split(r"[_\-]+", p.stem) if t]
        common_prefixes = {"domaine", "chateau", "weingut", "bodegas", "ch", "clos"}
        # Use the last non-common token as the "surname"
        surname = ""
        for t in reversed(tokens):
            if t not in common_prefixes:
                surname = t
                break
        if surname and len(surname) >= 5:
            by_last_token[surname].append(p.stem)
    for surname, slugs in by_last_token.items():
        if len(slugs) > 1:
            # If both pages have non-empty aliases (manual disambiguation
            # already done), don't flag the collision again.
            if all(aliases_map.get(s) for s in slugs):
                continue
            cov = ", ".join(f"{s}({coverage[s]})" for s in slugs)
            issues.append(Issue("csw_surname_collision", ",".join(slugs),
                                 f"shared surname '{surname}' with coverage: {cov}. "
                                 "CSW matcher may double-count articles; "
                                 "populate aliases to disambiguate."))

    # Broken links (one issue per distinct target)
    broken_counts: dict[str, int] = defaultdict(int)
    for _, target in broken_links:
        broken_counts[target] += 1
    # Skip common hub-style links that aren't producer slugs
    skip_hub = {"csw article archive", "csw_article_archive"}
    for target, n in sorted(broken_counts.items(), key=lambda x: -x[1])[:40]:
        if target.lower() in skip_hub:
            continue
        issues.append(Issue("broken_wikilink", target,
                             f"[[{target}]] referenced {n}× but no such producer file"))

    # --- write report ---
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    by_kind: dict[str, list[Issue]] = defaultdict(list)
    for i in issues:
        by_kind[i.kind].append(i)

    lines = [
        "---",
        "type: lint_report",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"producer_files: {len(producer_files)}",
        f"total_issues: {len(issues)}",
        f"fix_mode: {fix}",
        "---",
        "",
        "# Lint report",
        "",
        f"Scanned **{len(producer_files)}** producer files against "
        f"`_SCHEMA.md` + `_TAXONOMY.md`.",
        "",
        f"**{len(issues)} issue(s)** surfaced across {len(by_kind)} categories.",
        "",
    ]

    if fix and rename_summary:
        lines += [
            "## Auto-fixes applied",
            "",
            "| Old | New | Status |",
            "|---|---|---|",
        ]
        for old, new, status in rename_summary:
            lines.append(f"| `{old.name}` | `{new.name}` | {status} |")
        lines.append("")

    kind_order = [
        "mojibake_filename",
        "slug_mismatch",
        "no_frontmatter",
        "country_unknown",
        "region_not_in_taxonomy",
        "region_empty",
        "duplicate_producer",
        "csw_surname_collision",
        "broken_wikilink",
    ]
    seen = set()
    for kind in kind_order + list(by_kind.keys()):
        if kind in seen or kind not in by_kind:
            continue
        seen.add(kind)
        items = by_kind[kind]
        lines += [
            f"## {kind} ({len(items)})",
            "",
        ]
        for i in items[:50]:
            lines.append(f"- `{i.path}` — {i.detail}")
        if len(items) > 50:
            lines.append(f"- _… and {len(items) - 50} more_")
        lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{len(issues)} issues across {len(by_kind)} categories")
    for k in kind_order:
        if k in by_kind:
            print(f"  {k:30s}: {len(by_kind[k])}")
    print(f"Report: {REPORT}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="Apply safe auto-fixes (rename mojibake filenames, "
                         "update wikilinks). Otherwise report only.")
    args = ap.parse_args()
    sys.exit(run(fix=args.fix))
