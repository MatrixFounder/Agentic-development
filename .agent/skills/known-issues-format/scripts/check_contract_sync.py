#!/usr/bin/env python3
"""Contract-sync gate for the KNOWN_ISSUES thin-index format.

Asserts the format contract stays identical between the two **framework-shipped**
copies: the skill authority (`SKILL.md`) and the seed template
(`assets/templates/known_issues_md_template.md`). This closes the drift risk the
VDD-adversarial review flagged (Task 088): the contract is embedded in more than
one self-contained place, so a future edit to one copy could silently diverge.

Compared fields: the status vocabulary, the severity vocabulary, the per-issue
frontmatter key set, and the index-line format string.

Exit 0 = in sync · 1 = drift (prints what diverged) · 2 = extraction/setup error.
CI-gateable, like `System/scripts/validate_skills.py`.

NOTE: the live `docs/KNOWN_ISSUES.md` is a PER-PROJECT instance (its issues and
prefixes differ per project), so it is intentionally NOT gated here — only the two
artifacts the framework ships are compared.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
SKILL = _ROOT / "SKILL.md"
TEMPLATE = _ROOT / "assets" / "templates" / "known_issues_md_template.md"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _paragraph(text: str, marker: str) -> str:
    """Whitespace-normalized paragraph starting at the line containing `marker`,
    up to the next blank line. Robust to soft line wraps."""
    out: list[str] = []
    capturing = False
    for line in text.splitlines():
        if marker in line:
            capturing = True
        if capturing:
            if line.strip() == "" and out:
                break
            out.append(line)
    return _norm(" ".join(out))


def _frontmatter_keys(text: str) -> list[str]:
    """Active (non-commented) keys, in order, from the first ```yaml fence."""
    m = re.search(r"```yaml\s*\n(.*?)\n```", text, re.S)
    if not m:
        return []
    keys: list[str] = []
    for line in m.group(1).splitlines():
        km = re.match(r"([a-z_]+):", line.strip())
        if km:
            keys.append(km.group(1))
    return keys


def _index_line_format(text: str) -> str:
    for line in text.splitlines():
        if line.lstrip().startswith("- **<ID>**"):
            return _norm(line)
    return ""


def _contract(text: str) -> dict:
    return {
        "status_vocab": _paragraph(text, "Status vocabulary"),
        "severity_vocab": _paragraph(text, "Severity vocabulary"),
        "frontmatter_keys": _frontmatter_keys(text),
        "index_line_format": _index_line_format(text),
    }


def main() -> int:
    for path in (SKILL, TEMPLATE):
        if not path.is_file():
            print(f"ERROR: missing {path}", file=sys.stderr)
            return 2
    a = _contract(SKILL.read_text(encoding="utf-8"))
    b = _contract(TEMPLATE.read_text(encoding="utf-8"))

    empty = [k for k in a if not a[k] or not b[k]]
    if empty:
        print(
            f"ERROR: could not extract contract field(s) {empty} — the SKILL.md or "
            f"template layout changed; update this gate to match.",
            file=sys.stderr,
        )
        return 2

    drift = [k for k in a if a[k] != b[k]]
    if drift:
        print("CONTRACT DRIFT between SKILL.md (authority) and the seed template:")
        for k in drift:
            print(f"  - {k}:")
            print(f"      SKILL.md: {a[k]}")
            print(f"      template: {b[k]}")
        print("Reconcile both — they are one contract in two shipped copies.")
        return 1

    print("known-issues-format contract in sync (SKILL.md ↔ template): "
          + ", ".join(a) + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
