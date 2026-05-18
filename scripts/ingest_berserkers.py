"""
Scan `raw/berserkers/<user>/markdown/*.md` posts produced by
`scrape_berserkers_user.py` and fold matching posts into each
`wiki/producers/*.md` file's `## Berserkers (<DisplayName>)` section.

Currently focused on William Kelley (--user William_Kelley), but designed to
generalize to other high-signal critics/posters once the pattern works.

Why the section header includes the user name
---------------------------------------------
Different posters have different signal levels. WK's word on a producer is
near-critic-grade; another forum regular's might be tasting-impression-grade.
Keep them in separate sections so we can present them with different weight in
producer pages and so future ingest of other users doesn't overwrite WK's data.

Frontmatter contract
--------------------
Adds (or updates) a `berserkers_<userkey>:` block on each producer page:

  retailers:
    berserkers_kelley:
      post_count: 4
      first_year: 2019
      last_year: 2024
      latest_post: https://www.wineberserkers.com/t/.../172171/16

The block is INSERTED if missing (most pages won't have it yet); existing
fields are UPDATED in place. Same logic as the FASS/DTEW ingest. The
`retailers:` parent must already exist on the producer page (it does for all
~294 today; lint enforces).

Matching
--------
Identical algorithm to ingest_blog_articles.py: ASCII-fold + alias expansion +
prefix/suffix stripping + whole-word match with hyphen/space tolerance. We
match the post body against producer name forms. Reply context (the
`reply_to_excerpt` block, captured separately by the scraper) is INCLUDED in
the matching corpus — WK often answers "yes that producer is great" without
naming who; the question contains the name.

Per-post excerpt rendering
--------------------------
For each matched post we render:
  ### [<topic title>](<post_url>)  *(post #N · YYYY-MM-DD)*
  > <reply context if present, ≤200 chars>
  > <first ~250 chars of WK's reply>

We do NOT mark posts as "dedicated" the way blog articles are (no equivalent
of an article whose title is solely about a single producer). All posts are
weighted equally; the post_count is the primary signal.

Usage
-----
  python scripts/ingest_berserkers.py --user William_Kelley --dry-run
  python scripts/ingest_berserkers.py --user William_Kelley
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"
BUILD = VAULT / "build"

MIN_MATCH_LEN = 5
EXCERPT_CHARS = 250
REPLY_CTX_CHARS = 180


# --------------------------------------------------------------------------- #
# User configuration                                                           #
# --------------------------------------------------------------------------- #

@dataclass
class UserConfig:
    discourse_user: str       # exact case from Discourse
    fm_key: str               # frontmatter sub-key under retailers:, e.g. "berserkers_kelley"
    section_header: str       # "## Berserkers (William Kelley)"
    display_label: str        # "William Kelley"


USERS: dict[str, UserConfig] = {
    "William_Kelley": UserConfig(
        discourse_user="William_Kelley",
        fm_key="berserkers_kelley",
        section_header="## Berserkers (William Kelley)",
        display_label="William Kelley",
    ),
}


# --------------------------------------------------------------------------- #
# Frontmatter primitives (copied from ingest_blog_articles.py)                 #
# --------------------------------------------------------------------------- #

FM_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    m = FM_RE.match(text)
    if not m:
        return None
    return m.group(1), m.group(2)


def get_fm_field(fm: str, key: str) -> str | None:
    m = re.search(rf'^{re.escape(key)}:\s*"?(.*?)"?\s*$', fm, re.MULTILINE)
    return m.group(1) if m else None


def get_fm_list(fm: str, key: str) -> list[str]:
    m = re.search(rf'^{re.escape(key)}:\s*\[(.*?)\]\s*$', fm, re.MULTILINE)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    out = []
    for part in re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', inner):
        v = next((x for x in part if x), "").strip()
        if v:
            out.append(v)
    return out


# --- Block insert/update (copied + adapted) --- #

INDENT_BLOCK = "    "


def _find_retailer_block(fm_lines: list[str], key: str) -> tuple[int, int] | None:
    header_re = re.compile(rf"^  {re.escape(key)}:\s*$")
    start = -1
    for i, line in enumerate(fm_lines):
        if header_re.match(line):
            start = i
            break
    if start < 0:
        return None
    end = start + 1
    while end < len(fm_lines):
        line = fm_lines[end]
        if line.strip() == "":
            if end + 1 < len(fm_lines) and fm_lines[end + 1].startswith(INDENT_BLOCK):
                end += 1
                continue
            break
        if line.startswith(INDENT_BLOCK):
            end += 1
            continue
        break
    return start, end


def _find_retailers_root(fm_lines: list[str]) -> int | None:
    """Locate the `retailers:` top-level key (no indent). Returns line index or None."""
    for i, line in enumerate(fm_lines):
        if re.match(r"^retailers:\s*$", line):
            return i
    return None


def _retailers_block_end(fm_lines: list[str], start: int) -> int:
    """Walk past `retailers:` and return the first line index that is no longer
    inside the block (i.e., not a 2-space-indented child or its 4-space children)."""
    end = start + 1
    while end < len(fm_lines):
        line = fm_lines[end]
        if line.strip() == "":
            if end + 1 < len(fm_lines) and (fm_lines[end + 1].startswith("  ") or fm_lines[end + 1].strip() == ""):
                end += 1
                continue
            break
        if line.startswith("  "):  # any 2+ space indent is still inside retailers:
            end += 1
            continue
        break
    return end


def upsert_subblock(fm: str, key: str, values: dict[str, str]) -> tuple[str, bool]:
    """Insert-or-update `<key>:` sub-block under `retailers:`. Returns (new_fm, retailers_existed)."""
    lines = fm.splitlines()
    retailers_at = _find_retailers_root(lines)
    if retailers_at is None:
        return fm, False  # caller will skip frontmatter mutation; the prose section can still write

    block = _find_retailer_block(lines, key)
    if block is None:
        # Insert a fresh sub-block at the end of `retailers:`
        end = _retailers_block_end(lines, retailers_at)
        # Walk back past trailing blank lines inside the block
        insert_at = end
        while insert_at > retailers_at + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        new_block = [f"  {key}:"] + [f"{INDENT_BLOCK}{f}: {v}" for f, v in values.items()]
        lines = lines[:insert_at] + new_block + lines[insert_at:]
        return "\n".join(lines), True

    # Update existing sub-block
    start, end = block
    field_re = {f: re.compile(rf"^{INDENT_BLOCK}{re.escape(f)}:\s*(.*)$") for f in values}
    found: dict[str, int] = {}
    for i in range(start + 1, end):
        for f, rx in field_re.items():
            if rx.match(lines[i]):
                found[f] = i
                break
    for f, idx in found.items():
        lines[idx] = f"{INDENT_BLOCK}{f}: {values[f]}"
    missing = [f for f in values if f not in found]
    if missing:
        insert_at = end
        while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        new_lines = [f"{INDENT_BLOCK}{f}: {values[f]}" for f in missing]
        lines = lines[:insert_at] + new_lines + lines[insert_at:]
    return "\n".join(lines), True


# --------------------------------------------------------------------------- #
# Matching (copied verbatim from ingest_blog_articles.py)                     #
# --------------------------------------------------------------------------- #

def ascii_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


GENERIC_SUFFIXES = (
    " Père et Fils", " Père & Fils", " Pere et Fils", " Pere & Fils",
    " et Fils", " & Fils", " et Fille", " et Filles",
    " Family", " Vignerons", " Frères", " Freres", " & Sons",
)


def build_match_names(name: str, aliases: list[str]) -> list[str]:
    out = {name}
    for a in aliases:
        out.add(a)
    for n in list(out):
        if " / " in n:
            for part in n.split(" / "):
                part = part.strip()
                if " " in part and len(part) >= MIN_MATCH_LEN:
                    out.add(part)
    for n in list(out):
        for suf in GENERIC_SUFFIXES:
            if n.endswith(suf):
                short = n[: -len(suf)].strip()
                if len(short) >= MIN_MATCH_LEN:
                    out.add(short)
    for n in list(out):
        for prefix in ("Domaine ", "Château ", "Chateau ", "Weingut ", "Bodegas "):
            if n.startswith(prefix):
                short = n[len(prefix):].strip()
                if len(short) >= MIN_MATCH_LEN:
                    out.add(short)
    return sorted({ascii_lower(n) for n in out if len(n) >= MIN_MATCH_LEN})


def _name_pattern(n: str) -> str:
    tokens = [t for t in re.split(r"[\s\-]+", n.strip()) if t]
    if not tokens:
        return ""
    joined = r"[\s\-]+".join(re.escape(t) for t in tokens)
    return r"\b" + joined + r"\b"


# --------------------------------------------------------------------------- #
# Post model                                                                   #
# --------------------------------------------------------------------------- #

@dataclass
class Post:
    topic_id: int
    topic_title: str
    post_number: int
    post_url: str
    date: str                        # YYYY-MM-DD or ""
    body_raw: str                    # the WK reply prose (no reply blockquote)
    reply_excerpt: str               # the post being replied to (may name the producer)
    body_norm: str                   # ascii-lower of body + reply for matching
    word_count: int

    @property
    def year(self) -> int:
        m = re.match(r"^(\d{4})", self.date or "")
        return int(m.group(1)) if m else 0

    @property
    def sort_key(self) -> tuple:
        if self.date:
            y, mo, d = self.date.split("-")
            return (0, -(int(y) * 10000 + int(mo) * 100 + int(d)))
        return (1, 0)


def _strip_reply_block(body: str) -> tuple[str, str]:
    """The scraper prepends a `> *Replying to X:*` blockquote to the body.
    Split it out so we can render reply context separately."""
    lines = body.splitlines()
    # Skip leading blank lines that come right after the frontmatter `---`
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    reply_lines: list[str] = []
    if i < len(lines) and lines[i].startswith("> *Replying to "):
        while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ""):
            if lines[i].startswith(">"):
                # Strip leading `> ` (or `>` if no space) and any trailing whitespace
                stripped = re.sub(r"^>\s?", "", lines[i]).rstrip()
                reply_lines.append(stripped)
            else:
                # Hit a blank line — end of reply block
                i += 1
                break
            i += 1
        # Consume any further trailing blanks before the prose
        while i < len(lines) and lines[i].strip() == "":
            i += 1
    rest = "\n".join(lines[i:]).strip()
    reply_text = " ".join(s for s in reply_lines if not s.startswith("*Replying to")).strip()
    return reply_text, rest


def load_posts(user_dir: Path) -> list[Post]:
    out: list[Post] = []
    md_dir = user_dir / "markdown"
    if not md_dir.exists():
        return out
    for p in sorted(md_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, body = parts
        if get_fm_field(fm, "type") != "berserkers_post":
            continue
        topic_title = get_fm_field(fm, "topic_title") or ""
        topic_id = int(get_fm_field(fm, "topic_id") or 0)
        pn = int(get_fm_field(fm, "post_number") or 0)
        post_url = get_fm_field(fm, "post_url") or ""
        date = (get_fm_field(fm, "date") or "").strip()
        reply_excerpt_fm = get_fm_field(fm, "reply_to_excerpt") or ""
        reply_text, body_clean = _strip_reply_block(body)
        # Prefer the in-FM excerpt (cleaner, never split mid-tag); fall back to extracted
        reply_excerpt = reply_excerpt_fm or reply_text
        full_corpus = f"{reply_excerpt} {body_clean}"
        out.append(Post(
            topic_id=topic_id,
            topic_title=topic_title,
            post_number=pn,
            post_url=post_url,
            date=date,
            body_raw=body_clean,
            reply_excerpt=reply_excerpt,
            body_norm=ascii_lower(full_corpus),
            word_count=len(re.findall(r"\w+", body_clean)),
        ))
    return out


def post_matches(post: Post, names: list[str]) -> bool:
    pats = [p for p in (_name_pattern(n) for n in names) if p]
    for pat in pats:
        if re.search(pat, post.body_norm):
            return True
    return False


def truncate(text: str, n: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return ""
    if len(text) <= n:
        return text
    cut = text[:n]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut + "…"


# --------------------------------------------------------------------------- #
# Section render + replace                                                     #
# --------------------------------------------------------------------------- #

def render_section(uc: UserConfig, matches: list[Post]) -> str:
    lines = [uc.section_header, ""]
    for post in matches:
        date = post.date or "undated"
        lines.append(f"### [{post.topic_title}]({post.post_url})")
        lines.append(f"*post #{post.post_number} · {date}*")
        lines.append("")
        if post.reply_excerpt:
            lines.append(f"> *Reply to:* {truncate(post.reply_excerpt, REPLY_CTX_CHARS)}")
            lines.append("")
        lines.append(f"> {truncate(post.body_raw, EXCERPT_CHARS)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _section_re(header: str) -> re.Pattern[str]:
    return re.compile(rf"{re.escape(header)}\n.*?(?=\n## [^#]|\Z)", re.DOTALL)


def replace_section(body: str, header: str, new_section: str) -> str:
    new_section = new_section.rstrip()
    rx = _section_re(header)
    if rx.search(body):
        new_body = rx.sub(new_section, body, count=1)
    else:
        new_body = body.rstrip() + "\n\n" + new_section
    return new_body.rstrip() + "\n"


# --------------------------------------------------------------------------- #
# Process                                                                      #
# --------------------------------------------------------------------------- #

@dataclass
class ProducerResult:
    slug: str
    name: str
    matched: int = 0
    first_year: int = 0
    last_year: int = 0
    latest_url: str = ""
    retailers_block_missing: bool = False
    skipped_reason: str = ""


def process(uc: UserConfig, *, dry_run: bool) -> int:
    user_dir = VAULT / "raw" / "berserkers" / uc.discourse_user
    print(f"Loading posts from {user_dir / 'markdown'}...")
    posts = load_posts(user_dir)
    print(f"Loaded {len(posts)} posts")

    if not posts:
        print(f"No posts found. Run scrape_berserkers_user.py --user {uc.discourse_user} first.", file=sys.stderr)
        return 1

    if not PRODUCERS.exists():
        print(f"No producers directory at {PRODUCERS}", file=sys.stderr)
        return 1

    producer_files = sorted(PRODUCERS.glob("*.md"))
    print(f"Scanning {len(producer_files)} producers...")

    results: list[ProducerResult] = []
    files_written = 0

    for p in producer_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = split_frontmatter(text)
        if not parts:
            continue
        fm, body = parts
        if get_fm_field(fm, "type") != "producer":
            continue
        name = get_fm_field(fm, "name") or ""
        slug = get_fm_field(fm, "slug") or p.stem
        aliases = get_fm_list(fm, "aliases")

        result = ProducerResult(slug=slug, name=name)
        names = build_match_names(name, aliases)
        if not names:
            result.skipped_reason = "no match names"
            results.append(result)
            continue

        matches = [post for post in posts if post_matches(post, names)]
        # Dedupe by post_url (a post could match multiple times via aliases — collapse)
        seen: set[str] = set()
        unique: list[Post] = []
        for post in matches:
            if post.post_url in seen:
                continue
            seen.add(post.post_url)
            unique.append(post)
        unique.sort(key=lambda x: x.sort_key)

        post_count = len(unique)
        years = [post.year for post in unique if post.year > 0]
        first_year = min(years) if years else 0
        last_year = max(years) if years else 0
        latest_url = unique[0].post_url if unique else ""

        new_fm, retailers_existed = upsert_subblock(
            fm,
            uc.fm_key,
            {
                "post_count": str(post_count),
                "first_year": str(first_year),
                "last_year": str(last_year),
                "latest_post": latest_url or '""',
            },
        )
        result.retailers_block_missing = not retailers_existed

        if unique:
            new_body = replace_section(body, uc.section_header, render_section(uc, unique))
        else:
            new_body = body if body.endswith("\n") else body + "\n"

        if not dry_run and (new_fm != fm or new_body != body):
            p.write_text(f"---\n{new_fm}\n---\n{new_body}", encoding="utf-8")
            files_written += 1

        result.matched = post_count
        result.first_year = first_year
        result.last_year = last_year
        result.latest_url = latest_url
        results.append(result)

    # ----- report -----
    BUILD.mkdir(parents=True, exist_ok=True)
    matched = [r for r in results if r.matched > 0]
    no_match = [r for r in results if r.matched == 0 and not r.skipped_reason]
    skipped = [r for r in results if r.skipped_reason]
    block_missing = [r for r in results if r.retailers_block_missing and r.matched > 0]
    matched.sort(key=lambda r: (-r.matched, r.name))

    report_path = BUILD / f"berserkers_{uc.fm_key}_ingest_report.md"
    lines = [
        "---",
        "type: ingest_report",
        f"source: berserkers/{uc.discourse_user}",
        f'generated: "{datetime.now(timezone.utc).isoformat(timespec="seconds")}"',
        f"total_producers: {len(results)}",
        f"matched_producers: {len(matched)}",
        f"no_match_producers: {len(no_match)}",
        f"skipped: {len(skipped)}",
        f"retailers_block_missing: {len(block_missing)}",
        f"total_posts: {len(posts)}",
        f"dry_run: {str(dry_run).lower()}",
        "---",
        "",
        f"# Berserkers ingest — {uc.display_label}",
        "",
        f"Scanned {len(posts)} posts by **{uc.display_label}** against {len(results)} producer pages. "
        f"Updated **{len(matched)}** producer files.",
        "",
        "## Top 30 by post count",
        "",
        "| Slug | Name | Posts | First | Last | Latest |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in matched[:30]:
        latest_link = f"[link]({r.latest_url})" if r.latest_url else "—"
        lines.append(f"| `{r.slug}` | {r.name} | {r.matched} | "
                     f"{r.first_year or '—'} | {r.last_year or '—'} | {latest_link} |")

    if block_missing:
        lines += [
            "",
            f"## ⚠ Producers missing `retailers:` block ({len(block_missing)})",
            "",
            "These pages had matches but no `retailers:` parent block, so the prose "
            "section was written but the frontmatter sub-block was not. Lint should "
            "flag these as schema violations independently.",
            "",
        ]
        for r in sorted(block_missing, key=lambda r: r.name):
            lines.append(f"- `{r.slug}` — {r.name}")

    lines += [
        "",
        f"## No matches ({len(no_match)})",
        "",
        f"These producers had zero matching posts by {uc.display_label}.",
        "",
    ]
    for r in sorted(no_match, key=lambda r: r.name)[:80]:
        lines.append(f"- `{r.slug}` — {r.name}")
    if len(no_match) > 80:
        lines.append(f"- … and {len(no_match) - 80} more")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"{'DRY-RUN: would update' if dry_run else 'Updated'}: {files_written} producer files")
    print(f"matched producers: {len(matched)}")
    print(f"no-match producers: {len(no_match)}")
    print(f"missing retailers block: {len(block_missing)}")
    print(f"report: {report_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--user", required=True, choices=sorted(USERS.keys()),
                    help="Configured user to ingest (Discourse username, exact case)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Compute matches and write report; do NOT modify producer files")
    args = ap.parse_args()
    return process(USERS[args.user], dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
