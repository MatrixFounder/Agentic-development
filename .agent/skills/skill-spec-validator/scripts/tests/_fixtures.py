"""Shared helpers for the skill-spec-validator suite.

``validate.py`` is a CLI that exits via ``sys.exit()`` inside its two entry
points, so every behavioral assertion here is made on ``SystemExit.code`` with
stdout captured. That shape is deliberate: WI-1 asked for TESTS, and refactoring
a live gate into return-codes to make it prettier to test is a separate, riskier
change (`developer-guidelines`: no unsolicited refactoring).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
VALIDATE_PY = SCRIPTS_DIR / "validate.py"


def load_validator():
    """Import validate.py by path (it lives in a skill dir, not a package)."""
    spec = importlib.util.spec_from_file_location("spec_validator_validate",
                                                  VALIDATE_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate = load_validator()

# The bypass token is assembled rather than written literally: `validate.py`
# tests for it as a bare substring ANYWHERE in TASK.md, so a file that merely
# mentions it disables its own gate — including, if we were careless, this
# fixture module's docstring leaking into a fixture.
BYPASS_TOKEN = "[BYPASS_" + "VALIDATION]"


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run(func, *args):
    """Call a validate.py entry point; return (exit_code, stdout)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            func(*args)
        except SystemExit as exc:  # every path exits
            return (exc.code if exc.code is not None else 0), out.getvalue()
    raise AssertionError("%s returned without sys.exit()" % func.__name__)


def run_cli(argv):
    """Drive main() through argparse; returns (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    old_argv = sys.argv
    sys.argv = ["validate.py", *[str(a) for a in argv]]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                validate.main()
            except SystemExit as exc:
                return (exc.code if exc.code is not None else 0), \
                    out.getvalue(), err.getvalue()
        return 0, out.getvalue(), err.getvalue()
    finally:
        sys.argv = old_argv


# --- artifact builders -------------------------------------------------------

RTM_TABLE = """
| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | First thing  | test |
| R2 | Second thing | test |
"""


def task_md(heading="## Requirements Traceability Matrix (RTM)", table=RTM_TABLE,
            prologue="# Technical Specification: fixture\n\n## 1. Description\n\nText.\n",
            epilogue="\n## 3. Constraints\n\nNone.\n"):
    return "%s\n%s\n%s%s" % (prologue, heading, table, epilogue)


def plan_md(body):
    return "# Development Plan — fixture\n\n%s\n" % body
