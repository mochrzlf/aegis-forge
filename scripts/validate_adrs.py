#!/usr/bin/env python3
"""
ADR format & STRIDE-completeness validator.

Enforces the ADR standard (docs/adr/ADR-000-template.md and ADR-001):
every numbered ADR (ADR-NNN-*.md, excluding the ADR-000 template) must have:
  - a metadata table with ID, Title, Status, and Date
  - a valid Status value (PROPOSED / ACCEPTED / DEPRECATED / SUPERSEDED)
  - a Context/Problem section and a Decision/Consequences section
  - a complete STRIDE threat-model table (all six categories)

Usage:
    python scripts/validate_adrs.py [adr_dir]
Exit code 0 = all ADRs valid; 1 = one or more violations.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VALID_STATUSES = ("PROPOSED", "ACCEPTED", "DEPRECATED", "SUPERSEDED")

# STRIDE categories written with a bolded first letter, e.g. "**S**poofing".
STRIDE_PATTERNS = {
    "Spoofing": r"\*\*S\*\*poofing|\bSpoofing\b",
    "Tampering": r"\*\*T\*\*ampering|\bTampering\b",
    "Repudiation": r"\*\*R\*\*epudiation|\bRepudiation\b",
    "Information Disclosure": r"\*\*I\*\*nformation Disclosure|\bInformation Disclosure\b",
    "Denial of Service": r"\*\*D\*\*enial of Service|\bDenial of Service\b",
    "Elevation of Privilege": r"\*\*E\*\*levation of Privilege|\bElevation of Privilege\b",
}

# Sections that indicate a considered decision (any of these headings).
CONTEXT_RE = re.compile(r"^#{1,4}\s+.*(context|problem)", re.IGNORECASE | re.MULTILINE)
DECISION_RE = re.compile(r"^#{1,4}\s+.*(decision|consequence|outcome)", re.IGNORECASE | re.MULTILINE)


def validate_adr(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    # Metadata table fields (accept "**ID** |" or "ID |" forms).
    for field in ("ID", "Title", "Status", "Date"):
        if not re.search(rf"\b{field}\b", text):
            errors.append(f"missing metadata field: {field}")

    # Status value must be one of the valid set.
    status_match = re.search(r"Status\*?\*?\s*\|\s*\**([A-Z]+)\**", text)
    if not status_match:
        errors.append("could not parse Status value from metadata table")
    elif status_match.group(1) not in VALID_STATUSES:
        errors.append(
            f"invalid Status '{status_match.group(1)}' "
            f"(expected one of {', '.join(VALID_STATUSES)})"
        )

    # Required narrative sections.
    if not CONTEXT_RE.search(text):
        errors.append("missing a Context/Problem section")
    if not DECISION_RE.search(text):
        errors.append("missing a Decision/Consequences section")

    # STRIDE completeness (all six categories present somewhere in the doc).
    missing = [name for name, pat in STRIDE_PATTERNS.items() if not re.search(pat, text)]
    if missing:
        errors.append("incomplete STRIDE table — missing: " + ", ".join(missing))

    return errors


def main() -> int:
    adr_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/adr")
    if not adr_dir.is_dir():
        print(f"❌ ADR directory not found: {adr_dir}")
        return 1

    # Numbered ADRs only; skip the ADR-000 template.
    adrs = sorted(
        p for p in adr_dir.glob("ADR-*.md")
        if not p.name.startswith("ADR-000")
    )
    if not adrs:
        print(f"ℹ️  No numbered ADRs found in {adr_dir} (nothing to validate).")
        return 0

    total_errors = 0
    for adr in adrs:
        errors = validate_adr(adr)
        if errors:
            total_errors += len(errors)
            print(f"❌ {adr.name}")
            for e in errors:
                print(f"     • {e}")
        else:
            print(f"✅ {adr.name}")

    print("─" * 60)
    if total_errors:
        print(f"❌ ADR validation failed: {total_errors} problem(s) across {len(adrs)} ADR(s).")
        return 1
    print(f"✅ All {len(adrs)} ADR(s) valid (metadata, status, sections, STRIDE).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
