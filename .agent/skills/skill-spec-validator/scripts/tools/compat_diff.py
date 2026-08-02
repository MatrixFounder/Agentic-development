#!/usr/bin/env python3
"""Differential compatibility check: old validate.py vs new, over real corpora.

Answers exactly one question — **did any already-written artifact change verdict?**
That is the claim an additive change to a live gate has to support, and it is not
what `tests/test_corpus.py` checks: those are liveness FLOORS ("the gate is not
dead"), deliberately set below the measured counts so ordinary churn never turns
the suite red. A floor cannot detect that file X flipped while file Y flipped back.

Every number this prints is COUNTED here. None is typed into a format string —
the first version of this measurement was reported with a hand-written denominator
that was wrong by 3, which is the defect `developer-guidelines` §6.3 rule 4 now
names.

Usage:
    python3 compat_diff.py --old <path/to/old/validate.py> [--root DIR] [PROJECT ...]

Exit: 0 = no artifact changed verdict · 1 = at least one did · 2 = usage error.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NEW_DEFAULT = HERE.parents[1] / "validate.py"


def passes(validator: Path, artifact: Path) -> bool:
    return subprocess.run(
        [sys.executable, str(validator), "--mode", "task", str(artifact)],
        capture_output=True,
    ).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--old", required=True, help="pre-change validate.py")
    ap.add_argument("--new", default=str(NEW_DEFAULT))
    ap.add_argument("--root", default=str(Path.home() / "dev-projects"))
    ap.add_argument("projects", nargs="*", help="project dir names (default: all with docs/tasks)")
    args = ap.parse_args()

    old, new, root = Path(args.old), Path(args.new), Path(args.root)
    for p in (old, new):
        if not p.is_file():
            print(f"Error: validator not found: {p}", file=sys.stderr)
            return 2
    if not root.is_dir():
        print(f"Error: root not found: {root}", file=sys.stderr)
        return 2

    names = args.projects or sorted(
        d.name for d in root.iterdir() if (d / "docs" / "tasks").is_dir()
    )

    total_files = 0
    changed: list[tuple[str, str, bool, bool]] = []
    for name in names:
        files = sorted((root / name / "docs" / "tasks").glob("*.md"))
        for f in files:
            total_files += 1
            a, b = passes(old, f), passes(new, f)
            if a != b:
                changed.append((name, f.name, a, b))
        print(f"  {name}: {len(files)} artifacts")

    for proj, fname, a, b in changed:
        print(f"CHANGED {proj}/{fname}: {'pass' if a else 'fail'} -> {'pass' if b else 'fail'}")

    print(
        f"\n{len(changed)} of {total_files} artifacts changed verdict "
        f"across {len(names)} project(s)."
    )
    if total_files == 0:
        print("Error: examined 0 artifacts — nothing was measured.", file=sys.stderr)
        return 2
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
