#!/usr/bin/env python3
"""Validate that System/Agents markdown references resolve to existing files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_PATTERNS = [
    "AGENTS.md",
    "GEMINI.md",
    "README.md",
    "README.ru.md",
    ".agent/workflows/**/*.md",
    "System/Docs/**/*.md",
]

# `\.` — ONE backslash. The previous `\\.` was written inside an r-string, where it
# means a literal backslash followed by any character, so it required the text
# `System/Agents/name\Xmd` and matched nothing in the corpus. The gate still printed
# "OK: checked 42 files; all System/Agents references resolve" and exited 0 — a green
# verdict over zero references, for as long as it has existed.
#
# That is why the summary below now reports the reference COUNT, and why a run that
# resolves nothing is a FAILURE rather than a pass: a file count is not evidence that
# any reference was checked (`developer-guidelines` §6.3, rule 3).
AGENT_REF_RE = re.compile(r"System/Agents/([A-Za-z0-9_.-]+\.md)")


def iter_files(repo_root: Path, patterns: list[str]) -> Iterable[Path]:
    seen: set[Path] = set()

    for pattern in patterns:
        matched = False
        for path in repo_root.glob(pattern):
            matched = True
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path

        if matched:
            continue

        direct = repo_root / pattern
        if direct.is_file():
            resolved = direct.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield direct


def scan_file(repo_root: Path, file_path: Path) -> tuple[list[tuple[int, str]], int]:
    """Return (missing_references, references_examined).

    The second value is the point: without it a run that examined nothing is
    indistinguishable from a run in which everything resolved.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

    missing: list[tuple[int, str]] = []
    examined = 0
    for line_num, line in enumerate(content.splitlines(), start=1):
        for match in AGENT_REF_RE.finditer(line):
            examined += 1
            rel_path = Path("System/Agents") / match.group(1)
            if not (repo_root / rel_path).is_file():
                missing.append((line_num, rel_path.as_posix()))
    return missing, examined


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that System/Agents/*.md references in docs/workflows resolve.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root (default: current directory)",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=DEFAULT_PATTERNS,
        help="File/glob patterns relative to project root.",
    )
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    files = list(iter_files(repo_root, args.paths))

    if not files:
        print("No files matched the provided patterns.", file=sys.stderr)
        return 2

    failures = 0
    examined = 0
    for file_path in files:
        missing, seen_here = scan_file(repo_root, file_path)
        examined += seen_here
        for line_num, missing_ref in missing:
            failures += 1
            rel_file = file_path.resolve().relative_to(repo_root)
            print(f"{rel_file}:{line_num}: missing reference -> {missing_ref}")

    if failures:
        print(
            f"Found {failures} missing System/Agents references "
            f"({examined} examined across {len(files)} files).",
            file=sys.stderr,
        )
        return 1

    # A scan that examined nothing is not a pass. The corpus always contains
    # System/Agents references — the workflows and prompts are built on them — so
    # zero means the matcher is broken, which is exactly how this gate spent its
    # whole life reporting green.
    if examined == 0:
        print(
            f"Error: matched {len(files)} files but examined 0 System/Agents "
            "references — the matcher is broken, not the corpus.",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: {examined} System/Agents references across {len(files)} files all resolve."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
