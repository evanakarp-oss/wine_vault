"""
One-shot cleanup: the DTE JSX uses R index 0 ("Alsace") as a default when region
is unspecified, which causes Italian producers to appear as Alsace in the
migrated wiki. Blank region when country and region disagree geographically.

Rules applied:
  - Italy + Alsace → region=""
  - Italy + Basque → region=""
  - Spain + Alsace → region=""
  - Germany + Alsace → region=""
  - France + Bierzo → region=""

We only touch producer files that were seeded by DTE (_sources contains dte_jsx).
Files that originated from CSW wiki are left alone; the migrator's country
derivation for those is independent and correct.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
WIKI_DIR = VAULT / "wiki" / "producers"

# (country_pattern, region_pattern) pairs that are suspicious and should be blanked
SUSPICIOUS = [
    ("Italy", "Alsace"),
    ("Italy", "Basque"),
    ("Italy", "Burgundy"),   # a Piedmont or Tuscan producer tagged Burgundy is wrong
    ("Italy", "Rhône"),
    ("Italy", "Champagne"),
    ("Spain", "Alsace"),
    ("Spain", "Burgundy"),
    ("Germany", "Alsace"),   # German regions are distinct; Alsace-proximity not enough
    ("France", "Bierzo"),
    ("France", "Piedmont"),
]


def iter_producer_files():
    for p in sorted(WIKI_DIR.glob("*.md")):
        yield p


def main() -> int:
    changed = 0
    total = 0
    for path in iter_producer_files():
        text = path.read_text(encoding="utf-8")
        total += 1

        # Only touch DTE-seeded files (so we don't clobber CSW data we trust)
        if "dte_jsx" not in text:
            continue

        for country, region in SUSPICIOUS:
            pattern = re.compile(
                rf'(country:\s*"){re.escape(country)}("\s*\n\s*region:\s*"){re.escape(region)}(")'
            )
            if pattern.search(text):
                new_text = pattern.sub(rf'\1{country}\2\3', text)
                # Replace the region with empty string
                new_text = re.sub(
                    rf'(country:\s*"{re.escape(country)}"\s*\n\s*region:\s*")'
                    rf'{re.escape(region)}(")',
                    r'\1\2',
                    new_text,
                )
                if new_text != text:
                    text = new_text
                    print(f"  {path.name}: {country}/{region} -> {country}/(blank)")

        # Write back if anything changed vs. original
        original = path.read_text(encoding="utf-8")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1

    print(f"\nScanned {total} files, modified {changed}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
