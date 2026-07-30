#!/usr/bin/env python3
"""Contract-sync gate for the thin-index ledger formats.

Asserts the format contract stays identical between the **framework-shipped**
copies: the skill authority (`SKILL.md`) and the seed template of each registry.
This closes the drift risk the VDD-adversarial review flagged (Task 088): the
contract is embedded in more than one self-contained place, so a future edit to
one copy could silently diverge.

Two registries are gated (Task 091), each sliced out of its files by an HTML
marker comment so the two contracts never bleed into each other's comparison:

  * ``defects``    — ``<!-- contract:defects -->``    / `known_issues_md_template.md`
  * ``work-items`` — ``<!-- contract:work-items -->`` / `backlog_md_template.md`

Compared per registry: the status vocabulary, the rank vocabulary (severity for
defects, effort for work-items), the record frontmatter key set, and the
index-line format string.

Exit 0 = in sync · 1 = drift (prints the registry + what diverged) · 2 =
extraction/setup error. CI-gateable, like `System/scripts/validate_skills.py`.

NOTE: the live `docs/KNOWN_ISSUES.md` / `docs/BACKLOG.md` are PER-PROJECT
instances (their records, prefixes, and local extensions differ per project), so
they are intentionally NOT gated here — only the artifacts the framework ships
are compared.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
SKILL = _ROOT / "SKILL.md"
TEMPLATES = _ROOT / "assets" / "templates"

# registry key -> (seed template, rank-vocabulary marker)
REGISTRIES = {
    "defects": ("known_issues_md_template.md", "Severity vocabulary"),
    "work-items": ("backlog_md_template.md", "Effort vocabulary"),
}

_MARKER_RE = re.compile(r"<!--\s*contract:([a-z\-]+)\s*-->")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _slice(text: str, registry: str) -> str:
    """Text from this registry's contract marker up to the next marker (or EOF).

    Scoping the comparison per registry is what lets one SKILL.md hold both
    contracts without the defect vocab being compared against the work-item one.
    """
    start = None
    for match in _MARKER_RE.finditer(text):
        if match.group(1) == registry:
            start = match.end()
            break
    if start is None:
        return ""
    nxt = _MARKER_RE.search(text, start)
    return text[start:nxt.start()] if nxt else text[start:]


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


def _contract(text: str, rank_marker: str) -> dict:
    return {
        "status_vocab": _paragraph(text, "Status vocabulary"),
        "rank_vocab": _paragraph(text, rank_marker),
        "frontmatter_keys": _frontmatter_keys(text),
        "index_line_format": _index_line_format(text),
    }


def main() -> int:
    if not SKILL.is_file():
        print(f"ERROR: missing {SKILL}", file=sys.stderr)
        return 2
    skill_text = SKILL.read_text(encoding="utf-8")

    drifted = False
    for registry, (template_name, rank_marker) in REGISTRIES.items():
        template = TEMPLATES / template_name
        if not template.is_file():
            print(f"ERROR: missing {template}", file=sys.stderr)
            return 2

        slices = {"SKILL.md": _slice(skill_text, registry),
                  template_name: _slice(template.read_text(encoding="utf-8"),
                                        registry)}
        for label, sliced in slices.items():
            if not sliced.strip():
                print(
                    f"ERROR: no <!-- contract:{registry} --> marker found in "
                    f"{label} — the layout changed; restore the marker or update "
                    f"this gate.",
                    file=sys.stderr,
                )
                return 2

        a = _contract(slices["SKILL.md"], rank_marker)
        b = _contract(slices[template_name], rank_marker)

        empty = [k for k in a if not a[k] or not b[k]]
        if empty:
            print(
                f"ERROR: [{registry}] could not extract contract field(s) "
                f"{empty} — the SKILL.md or template layout changed; update this "
                f"gate to match.",
                file=sys.stderr,
            )
            return 2

        drift = [k for k in a if a[k] != b[k]]
        if drift:
            drifted = True
            print(f"CONTRACT DRIFT [{registry}] between SKILL.md (authority) "
                  f"and {template_name}:")
            for k in drift:
                print(f"  - {k}:")
                print(f"      SKILL.md: {a[k]}")
                print(f"      template: {b[k]}")

    if drifted:
        print("Reconcile both sides — they are one contract in shipped copies.")
        return 1

    print("thin-index ledger contracts in sync (SKILL.md <-> seed templates): "
          + ", ".join(REGISTRIES) + " x status_vocab, rank_vocab, "
          "frontmatter_keys, index_line_format.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
