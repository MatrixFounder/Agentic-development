#!/usr/bin/env python3
"""Resolve ``skill-<name>`` references in prompts and skills to real skill directories.

A role prompt declares its Active Skills by NAME. If that name does not resolve, the
role either loads nothing or falls back to whatever it can infer — quietly, because
nothing fails. Measured 2026-08-05: **108 references across 25 files** named a skill
with a ``skill-`` prefix its directory does not have, including every one of the ten
role prompts under ``System/Agents/``. ``CLAUDE.md`` contradicted itself inside forty
lines: its TIER-0 block loads ``.agent/skills/core-principles/SKILL.md`` by path while
its pipeline prose calls the same skill ``skill-core-principles``.

The defect surfaced from a run, not a review: ``plan-reviewer`` reported that
``skill-plan-review-checklist`` did not exist and completed using the checklist inlined
in its own prompt instead.

**The rule is deliberately narrow, so it has no judgement in it.** A reference is a
mis-spelling if and only if:

    .agent/skills/skill-<name>/   does NOT exist   AND
    .agent/skills/<name>/         DOES exist

That is provable from the filesystem — the reference names a real skill by a name it
does not have. Nothing else is reported.

**Declared limit: a reference to a skill that exists under NEITHER spelling is
invisible to this tool, and that is correct rather than a gap.** Measured on the same
day, six such references exist and all six are legitimate:

* ``skill-mcp-tools-overview``, ``skill-drift-detection``, ``skill-deploy-checklist`` —
  ROADMAP proposals for skills that do not exist yet ("create a new ``skill-…``");
* ``skill-validate`` — a CI job name, not a skill;
* ``skill-magic-wand`` — a deliberately fictional skill inside an audit EXAMPLE;
* ``skill-validator`` — a real skill that lives outside ``.agent/skills/``.

Reporting those would mean deciding which prose is a reference and which is a proposal,
which no filesystem check can do. A tool that fires on a ROADMAP entry gets muted, and a
muted gate protects nothing.

Archived material is excluded for the same reason ``check_positional_refs.py`` is
diff-scoped: an archived spec was correct when written and is not retrofitted.

Exit codes:
    0: every ``skill-<name>`` reference resolves (or is out of this rule's scope)
    1: at least one reference names a real skill by a name it does not have
    2: the check could not be performed — no ``.agent/skills`` directory found. Never 0,
       so a failed query cannot pass for a clean run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

#: A backticked or bare ``skill-<name>`` token. ``\b`` on both ends so ``xskill-foo``
#: and ``skill-foo-bar`` are not clipped into a false match.
_REF = re.compile(r"\bskill-([a-z0-9][a-z0-9-]*)\b")

#: Paths whose contents are history rather than instruction. ``archives``/``archive``
#: cover both spellings in use; ``docs/tasks|plans|reviews`` are per-task artifacts that
#: this framework explicitly does not retrofit.
_SKIP = re.compile(
    r"(^|/)(archives|archive|node_modules|\.git|__pycache__)/"
    r"|(^|/)CHANGELOG[^/]*$"
    r"|(^|/)docs/(tasks|plans|reviews)/"
)


@dataclass(frozen=True)
class Finding:
    """One reference that names a real skill by a name it does not have."""

    path: str
    line: int
    reference: str
    correct: str

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}: `{self.reference}` does not resolve — "
            f"the skill exists as `{self.correct}` (no `skill-` prefix)"
        )


def skill_names(skills_dir: Path) -> set[str]:
    """Directory names under ``.agent/skills`` — the authoritative set of skill names."""
    return {entry.name for entry in skills_dir.iterdir() if entry.is_dir()}


def scan_text(text: str, names: set[str], path: str = "<text>") -> list[Finding]:
    """Findings for one document. Split out from disk access so the tests can drive it
    with literals instead of depending on this repository's evolving content."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _REF.finditer(line):
            name = match.group(1)
            if f"skill-{name}" in names:
                continue  # correctly prefixed skill — this is its real name
            if name in names:
                findings.append(Finding(path, lineno, match.group(0), name))
            # else: names no known skill under either spelling — out of scope, see the
            # module docstring for the six measured cases and why they are legitimate.
    return findings


def scan_repo(root: Path) -> tuple[list[Finding], int]:
    """Returns (findings, files_scanned). ``files_scanned`` is the sign of work: a run
    that matched nothing because it walked nothing must not read as a clean run."""
    skills_dir = root / ".agent" / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"no skills directory at {skills_dir}")
    names = skill_names(skills_dir)

    findings: list[Finding] = []
    scanned = 0
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if _SKIP.search(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        findings.extend(scan_text(text, names, rel))
    return findings, scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every `skill-<name>` reference resolves to a real skill.",
    )
    parser.add_argument("--root", default=".", help="Repository root (default: cwd).")
    parser.add_argument("--json", action="store_true", help="Emit findings as JSON.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        findings, scanned = scan_repo(root)
    except FileNotFoundError as error:
        print(f"check_skill_refs: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "files_scanned": scanned,
                    "findings": [f.__dict__ for f in findings],
                },
                indent=2,
            )
        )
    else:
        for finding in findings:
            print(finding.render())
        print(
            f"check_skill_refs: {len(findings)} unresolvable reference(s) "
            f"in {scanned} scanned file(s)",
            file=sys.stderr,
        )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
