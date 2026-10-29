#!/usr/bin/env python3
"""Smoke checks for workflow integrity."""

import os
import sys

# Run as a script, the script's own directory leaves `sys.path` before any other import, matched by
# real path and by device and inode, so a module planted beside the script is never imported.
if __name__ == "__main__":
    def _identity(path):
        """`(st_dev, st_ino)` of `path`, or None where it cannot be read or has no inode."""
        try:
            st = os.stat(path)
        except OSError:
            return None
        return (st.st_dev, st.st_ino) if st.st_ino else None

    _DIRS = {os.path.dirname(os.path.abspath(__file__)),
             os.path.dirname(os.path.realpath(__file__))}
    _NAMES = {os.path.normcase(os.path.realpath(path)) for path in _DIRS}
    _IDS = {_identity(path) for path in _DIRS} - {None}
    sys.path[:] = [entry for entry in sys.path
                   if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
                   and _identity(entry or os.curdir) not in _IDS]

import argparse
import re
from pathlib import Path

KEY_WORKFLOWS = [
    "base-stub-first.md",
    "vdd-enhanced.md",
    "light-01-start-feature.md",
    "light-02-develop-task.md",
]

# Intentionally validate explicit nested workflow calls only: "Call /workflow-name"
CALL_RE = re.compile(r"\b(?:Call|call)\s+`?/([a-z0-9-]+)`?")


def check_key_workflows(workflows_dir: Path) -> list[str]:
    errors: list[str] = []
    for wf_name in KEY_WORKFLOWS:
        wf_path = workflows_dir / wf_name
        if not wf_path.is_file():
            errors.append(f"Missing key workflow: .agent/workflows/{wf_name}")
    return errors


def check_internal_calls(workflows_dir: Path) -> list[str]:
    errors: list[str] = []

    for wf_path in sorted(workflows_dir.glob("*.md")):
        try:
            content = wf_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = wf_path.read_text(encoding="utf-8", errors="ignore")

        for line_num, line in enumerate(content.splitlines(), start=1):
            for match in CALL_RE.finditer(line):
                called = match.group(1)
                called_path = workflows_dir / f"{called}.md"
                if not called_path.is_file():
                    rel_wf = wf_path.as_posix().split("/.agent/")[-1]
                    errors.append(
                        f"{rel_wf}:{line_num}: missing called workflow -> .agent/workflows/{called}.md"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-check workflow files")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    workflows_dir = repo_root / ".agent/workflows"

    if not workflows_dir.is_dir():
        print("Missing .agent/workflows directory", file=sys.stderr)
        return 2

    errors = []
    errors.extend(check_key_workflows(workflows_dir))
    errors.extend(check_internal_calls(workflows_dir))

    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        print(f"Workflow smoke checks failed with {len(errors)} issue(s).", file=sys.stderr)
        return 1

    print("Workflow smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
