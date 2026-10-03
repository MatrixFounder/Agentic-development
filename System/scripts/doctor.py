#!/usr/bin/env python3
"""Local preflight checks for Python-based framework tooling."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

# README §3 states both versions; tests/test_python_floor.py holds these equal to it.
REQUIRED_PYTHON = (3, 11)
RECOMMENDED_PYTHON = (3, 14)
REQUIRED_MODULES = [
    ("pytest", "pytest"),
    ("yaml", "PyYAML"),
]
REQUIRED_FILES = [
    Path("System/scripts/tool_runner.py"),
    Path(".agent/skills/skill-creator/scripts/init_skill.py"),
    Path(".agent/skills/skill-creator/scripts/validate_skill.py"),
]


def _status(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def _check_python_version() -> int:
    current = sys.version_info[:3]

    if current < REQUIRED_PYTHON:
        _status(
            "FAIL",
            f"Python {current[0]}.{current[1]}.{current[2]} is below the minimum {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}; "
            f"{RECOMMENDED_PYTHON[0]}.{RECOMMENDED_PYTHON[1]} is the main version",
        )
        return 1

    if current < RECOMMENDED_PYTHON:
        _status(
            "WARN",
            f"Python {current[0]}.{current[1]}.{current[2]} meets the minimum {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}; "
            f"{RECOMMENDED_PYTHON[0]}.{RECOMMENDED_PYTHON[1]} is the main version",
        )
        return 0

    _status("OK", f"Python {current[0]}.{current[1]}.{current[2]}")
    return 0


def _check_modules() -> int:
    failures = 0
    for module_name, package_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception:
            failures += 1
            _status("FAIL", f"Missing module '{module_name}' (install package: {package_name})")
            continue
        _status("OK", f"Module '{module_name}' available")
    return failures


def _check_files(repo_root: Path) -> int:
    failures = 0
    for rel_path in REQUIRED_FILES:
        abs_path = repo_root / rel_path
        if abs_path.is_file():
            _status("OK", f"Found {rel_path.as_posix()}")
        else:
            failures += 1
            _status("FAIL", f"Missing required file: {rel_path.as_posix()}")
    return failures


def _check_pytest_command() -> int:
    try:
        result = subprocess.run(
            # -P (3.11+): import nothing from the current directory, which may be a project.
            [sys.executable, *(["-P"] if sys.version_info >= (3, 11) else []), "-m", "pytest",
             "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        _status("FAIL", f"Could not execute pytest version check: {exc}")
        return 1

    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        _status("FAIL", f"pytest invocation failed: {output}")
        return 1

    _status("OK", f"{output}")
    return 0


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    failures = 0

    failures += _check_python_version()
    failures += _check_modules()
    failures += _check_files(repo_root)
    failures += _check_pytest_command()

    if failures:
        _status("SUMMARY", f"Preflight failed with {failures} issue(s).")
        _status("HINT", "Run: pip install -r requirements-dev.txt")
        return 1

    _status("SUMMARY", "Preflight checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
