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
import atexit
import codecs
import json
import os
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
    install_human_channel()
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


# --------------------------------------------------------------------- #
# The HUMAN channel — reports, progress, --help
# --------------------------------------------------------------------- #
#
# The machine helpers above must ignore the caller's locale: JSON is UTF-8 by
# RFC 8259 §8.1. Prose is the opposite — it must OBEY the caller's codec,
# because UTF-8 written into a terminal that declared cp1252 is mojibake, not
# robustness.
#
# Until this existed it obeyed by dying. stderr is opened
# errors="backslashreplace" and survives; stdout gets "surrogateescape" (or
# "strict" under an explicit PYTHONIOENCODING), and NEITHER can represent an
# em dash — surrogateescape rescues lone surrogates and nothing else. So one
# `—` or `✓` in a report, or in an argparse `help=` string, took the whole
# command down.
#
# The fix belongs to the STREAM, not to the call sites. `codecs.register_error`
# is the documented extension point for exactly this question — "what should
# happen to a character this codec cannot represent?" — and once the handler
# is on stdout it covers `print`, argparse's own `file.write`, a bare
# `sys.stdout.write` deep inside a renderer, and any third-party write in the
# same process. Nothing to remember at the call site, because there is no call
# site to remember.
#
# The first version of this fix did the opposite: a `say()` wrapper, a
# `HumanArgumentParser` subclass and a stream shim, ~157 lines copied into
# every skill, with every `print` rewritten to match. It worked, and it was
# the wrong shape — mutation testing showed a forgotten `print` still slipped
# through, and the duplicated block was mechanism rather than data. What is
# left below is data (the table) plus fifteen lines that hand it to CPython.
#
# Issue: docs/issues/human-cli-output-locale-class.md.

#: Name under which the handler is registered process-wide. Also usable as an
#: `errors=` argument anywhere: `text.encode("ascii", HUMAN_ERRORS)` gives
#: exactly what a report would look like under that codec, which is how the
#: tests state their expectations without restating the table.
HUMAN_ERRORS = "human_channel.asciify"

#: ASCII spellings for the decoration these reports print. A FALLBACK table,
#: not a transliterator: consulted only for characters the caller's codec has
#: already rejected, and anything missing from it degrades to a
#: `backslashreplace` escape rather than being dropped.
_ASCII_FALLBACK = {
    "—": "--", "–": "-", "…": "...", "→": "->", "←": "<-",
    "✓": "+", "✔": "+", "✗": "x", "✘": "x", "×": "x",
    "⚠": "!", "❌": "x", "✅": "+", "❗": "!", "•": "*", "§": "S",
    "±": "+/-", "≥": ">=", "≤": "<=", "≠": "!=", "°": " deg",
    "‘": "'", "’": "'", "“": '"', "”": '"', " ": " ",
    # U+FE0F / U+FE0E only select an emoji's presentation; they carry no
    # meaning of their own. `⚠️` is U+26A0 U+FE0F, so mapping just the base
    # glyph left the selector behind and the report read `!️`. Dropping
    # them is the whole fix — the base character already says it.
    "️": "", "︎": "",
}


def _asciify(exc):
    """Spell an unencodable run in ASCII instead of letting it kill the write.

    The codec calls this once per unencodable RUN, not once per character:
    `exc.object[exc.start:exc.end]` can be several characters long, hence the
    loop. Degradation stays per character so a codec keeps everything it can
    carry — under cp1251 `доклад — ✓` keeps the Cyrillic AND the em dash and
    only the check mark moves.

    Anything the table does not know falls back to `backslashreplace`, which
    is what stderr has always done and precisely why stderr never crashed.

    Re-raises anything that is not an encode error. A decode error reaching
    here would mean the handler was installed on a readable stream, where
    guessing would corrupt input rather than tidy output.
    """
    if not isinstance(exc, UnicodeEncodeError):
        raise exc
    spelled = []
    for ch in exc.object[exc.start:exc.end]:
        replacement = _ASCII_FALLBACK.get(ch)
        if replacement is None:
            # Escaped against ASCII, NOT against `exc.encoding`. For every
            # charmap codec -- cp1251, cp1252, latin-1, cp850, cp932 -- the
            # exception reports `exc.encoding == "charmap"`, the literal
            # string, not the codec's name. Re-encoding through *that* does
            # not raise: the bare `charmap` codec falls back to Latin-1 and
            # hands back the RAW BYTE, so `é` came out of cp1251 as b"\xe9"
            # and the following decode blew up. ASCII escapes are also the
            # only universally safe answer -- the character is here precisely
            # because the caller's codec rejected it.
            replacement = ch.encode("ascii", "backslashreplace").decode("ascii")
        spelled.append(replacement)
    return "".join(spelled), exc.end


codecs.register_error(HUMAN_ERRORS, _asciify)


def _quiet_a_dead_stdout():
    """Drain stdout at exit, and if it is already gone, point fd 1 at devnull.

    Registered by `install_human_channel`, and the second half of the exit-code
    contract. `line_buffering` makes the CLI's own `except BrokenPipeError`
    handler see the failure and return its verdict — but the interpreter then
    flushes the SAME dead fd again during finalization, prints "Exception
    ignored while flushing sys.stdout" on stderr, and replaces that verdict
    with 120. Measured: `install_components.py` with no reader at all printed
    its own broken-pipe line, returned 1, and exited 120.

    atexit callbacks run before that final flush, so draining here leaves it
    nothing to fail on. A stream with no real fd (a test's StringIO) has
    nothing to redirect and needs nothing, hence the swallowed exceptions.
    """
    try:
        sys.stdout.flush()
    except (BrokenPipeError, ValueError, OSError):
        try:
            fd = sys.stdout.fileno()
        except (OSError, ValueError, AttributeError):
            return
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
        except OSError:
            return
        try:
            os.dup2(devnull, fd)
        finally:
            os.close(devnull)
    except AttributeError:
        pass


def install_human_channel(*streams):
    """Point stdout's and stderr's error handler at `_asciify`.

    Call once, early in `main()` — NOT at import. Registering the handler
    above is inert, but `reconfigure` mutates a process-wide stream, and a
    module that does that on import imposes it on everything that merely
    imports the module.

    stderr is included even though it never crashed: its `backslashreplace`
    turns an em dash into the six characters `\\u2014`, and `--` is strictly
    better for the same cost.

    `line_buffering` is set for a second, unrelated reason, and it matters:
    piped stdout is BLOCK-buffered, so `report | head` surfaces the dead reader
    during interpreter shutdown, where CPython prints "Exception ignored while
    flushing sys.stdout" and **replaces the exit status with 120** — a command
    contradicting the verdict it just gave. Line-buffered, the write itself
    raises BrokenPipeError inside `main()`, where the CLI's own handler sees
    it. This also just restores the behaviour stdout already has on a terminal;
    only redirection took it away.

    Failure is silent by design. A replaced stdout — a test's `StringIO`, a
    capture proxy, `prog >&-` leaving `sys.stdout` as None — has no
    `reconfigure` to call, and none of that is a reason to fail a report.
    """
    if not streams:
        atexit.register(_quiet_a_dead_stdout)
    for stream in streams or (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors=HUMAN_ERRORS, line_buffering=True)
        except (AttributeError, ValueError, OSError):
            pass


if __name__ == "__main__":
    sys.exit(main())
