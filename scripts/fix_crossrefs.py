"""
fix_crossrefs.py — repair broken wikilinks in wiki/producers/*.md.

Idempotent. Three rules, applied in order:

  1. `[[CSW Article Archive]]` → `[[Chambers_Street_Wines|CSW article archive]]`
     (the archive hub page never existed; the retailer page is the real hub).
  2. Accent-folded target repair: a link whose target doesn't exist but whose
     accent-stripped form does is rewritten (e.g. `[[Rhône_Producers|Rhône]]`
     → `[[Rhone_Producers|Rhône]]`).
  3. Remaining broken targets are unwrapped to plain text (`[[X|Y]]` → `Y`).
     These are mostly sub-region/appellation names (Savigny-lès-Beaune,
     Chassagne-Montrachet, …) that have no pages. Policy: locations stay
     plain text until a page exists — re-linking later is a grep away.

Run AFTER `build_rollups.py` so country hubs (France_Producers, …) exist
and don't get unwrapped.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PRODUCERS = VAULT / "wiki" / "producers"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def main() -> int:
    stems = {f.stem for root in (VAULT / "wiki", VAULT / "cellar")
             for f in root.rglob("*.md")}
    folded = {fold(s): s for s in stems}

    touched = 0
    rewrites = unwrapped = 0
    for p in sorted(PRODUCERS.glob("*.md")):
        text = p.read_text(encoding="utf-8")

        def repl(m: re.Match) -> str:
            nonlocal rewrites, unwrapped
            target = m.group(1).strip()
            display = (m.group(2) or "").strip()
            if target in stems:
                return m.group(0)
            if target == "CSW Article Archive":
                rewrites += 1
                return f"[[Chambers_Street_Wines|{display or 'CSW article archive'}]]"
            ft = folded.get(fold(target))
            if ft:
                rewrites += 1
                return f"[[{ft}|{display or target}]]"
            unwrapped += 1
            return display or target

        new_text = WIKILINK_RE.sub(repl, text)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            touched += 1

    print(f"{touched} producer pages touched: "
          f"{rewrites} links re-targeted, {unwrapped} unwrapped to plain text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
