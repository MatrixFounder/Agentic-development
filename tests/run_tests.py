import os
import sys

# Run as a script, the script's own directory leaves `sys.path` before any other import, matched by
# real path and by device and inode, so a module planted beside the script is never imported. No
# `.pyc` is written or read from a `__pycache__/`. The test modules that it runs are not guarded.
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
    sys.dont_write_bytecode = True
    if os.path.isabs(os.devnull):
        sys.pycache_prefix = os.path.join(os.devnull, "run_tests-pycache")
    else:
        sys.pycache_prefix = os.path.join(os.path.realpath(__file__), "pycache")

import unittest
import json
import re
# Imported before the discovery, where `tests/` is on the path: each probes on import for a module
# that some platforms lack, `subprocess` for `msvcrt` or `fcntl` and `platform` for `_wmi`.
import platform  # noqa: F401
import subprocess  # noqa: F401
from pathlib import Path
from unittest.mock import MagicMock, patch

# --- Dynamic Import Helper ---
import importlib.util

def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Load Scripts
roi_script = load_module_from_path("calculate_roi", 
    PROJECT_ROOT / ".agent/skills/skill-product-solution-blueprint/scripts/calculate_roi.py")

score_script = load_module_from_path("score_product",
    PROJECT_ROOT / ".agent/skills/skill-product-analysis/scripts/score_product.py")

wsjf_script = load_module_from_path("calculate_wsjf",
    PROJECT_ROOT / ".agent/skills/skill-product-backlog-prioritization/scripts/calculate_wsjf.py")

class TestProductSkills(unittest.TestCase):

    # --- ROI Tests ---
    def test_roi_effort_calculation(self):
        config = {
            "sizing": {"S": 10},
            "financials": {"llm_global_accel": 0.5}
        }
        # Friendliness 1.0 -> Factor 0.5 -> 5 hours
        stories = [{"size": "S", "llm_friendly": 1.0}]
        base, effective = roi_script.calculate_granular_effort(stories, config)
        self.assertEqual(base, 10)
        self.assertEqual(effective, 5.0)

    def test_roi_time_travel_clamping(self):
        """Ensure time travel bug is fixed."""
        config = {
            "sizing": {"S": 10},
            "financials": {"llm_global_accel": 0.5}
        }
        # Friendliness 3.0 -> Should clamp to 1.0 -> Factor 0.5 -> 5 hours
        stories = [{"size": "S", "llm_friendly": 3.0}] 
        base, effective = roi_script.calculate_granular_effort(stories, config)
        self.assertGreater(effective, 0)
        self.assertEqual(effective, 5.0) 

    # --- Score Tests ---
    def test_score_product_clamping(self):
        scores = {
            "problem_intensity": 100, # Should clamp to 10
            "market_size": 0          # Should clamp to 1
        }
        # Capture stdout to avoid clutter
        with patch('sys.stdout', new=MagicMock()):
             final_score, risk = score_script.score_product(scores)
        
        # Total weight = 12.0 (sum of weights)
        # Score calculation: 
        # problem: 10 * 2.0 = 20
        # market: 1 * 1.5 = 1.5
        # others: 5 * weight...
        
        # Just ensure range is valid
        self.assertTrue(0 <= final_score <= 100)

    # --- WSJF Tests ---
    def test_wsjf_mapping(self):
        self.assertEqual(wsjf_script.map_size_to_fib("XS"), 1)
        self.assertEqual(wsjf_script.map_size_to_fib("medium"), 5) # Case insensitive check
        self.assertEqual(wsjf_script.map_size_to_fib("Small"), 2)

    def test_wsjf_logic(self):
        # Expected input: list of (line_content, cells)
        rows = [("| A | 3 | 3 | 2 | S | |", ["A", "3", "3", "2", "S", ""])]
        indices = {"User Value": 1, "Time Criticality": 2, "Risk Reduction": 3, "Job Size": 4, "WSJF": 5}
        processed = wsjf_script.calculate_wsjf(rows, indices)
        self.assertEqual(processed[0]['score'], 4.0)

#: Pure-unittest modules in `tests/` that the curated suite pulls in by name. Blanket
#: discovery is deliberately avoided: several `tests/test_*.py` files use pytest fixtures
#: and would error under the unittest loader.
#:
#: CI runs this runner (`.github/workflows/framework-gates.yml`, the curated unittest step), so
#: a module listed here is a CI gate. The workflow's pytest step names a separate, larger set.
CURATED_UNITTEST_MODULES = (
    "test_positional_refs",
    "test_scratch_hygiene",
    "test_loop_contract",
    # WI-39 — a role prompt that declares an Active Skill by a name resolving to nothing
    # fails silently: the role loads nothing and continues. 108 such references existed
    # across 25 files before this gate.
    "test_skill_refs",
    # TASK 107 — /framework-upgrade rolls back through git; no instruction asks for a copy.
    "test_git_rollback_contract",
    # TASK 108 — every R10 surface keeps its pointer to mermaid-authoring-guidelines.
    "test_mermaid_wiring",
    # TASK 109 — one Python floor, stated in README §3 and enforced at the entry points.
    "test_python_floor",
    # TASK 110 — a fix round replays the stored corpus and keeps a closed list (WI-27).
    "test_fix_round_rules",
    # TASK 110 — a dependency finding is reported privately and stays out of the repo (R11.2).
    "test_disclosure_rule",
    # TASK 111 — checks that cover what they claim (WI-31): the committed settings, pinned
    # actions, the full fingerprint and the audit of every npm lockfile. The anchor hook is
    # deferred to WI-34.
    "test_committed_settings",
    "test_ci_action_pins",
    "test_tree_fingerprint",
    "test_lockfile_audit",
    # TASK 111 retro (R7) — a hook is registered last; an unfinished review is INCOMPLETE.
    "test_run_safety_rules",
    # TASK 112 — the archive script and the guards of the scripts that allow rules run (WI-35).
    "test_archive_move",
    "test_script_guards",
)


def load_tests(loader, standard_tests, pattern):
    """Augment the curated suite with the installer package and named unittest modules.

    `tests/installer/` is a flat (non-package) directory of unittest modules;
    discovering it with its own `top_level_dir` lets the test modules import
    their sibling `_base` helper.

    A missing curated module is a hard error, not a skip. Guarding the load with
    `.is_file()` would turn the drift this list exists to prevent into a silent one: rename
    the file and the runner quietly returns to its old count while still printing OK.

    Each discovered directory is appended to the end of `sys.path` first, so `unittest` does not
    insert it at the front: the standard library and the installed packages stay ahead of a module
    planted in `tests/` (TASK 134 R5).

    Raises:
        FileNotFoundError: If a module named in :data:`CURATED_UNITTEST_MODULES` is gone.
    """
    installer_dir = PROJECT_ROOT / "tests" / "installer"
    for directory in (PROJECT_ROOT / "tests", installer_dir):
        if str(directory) not in sys.path:
            sys.path.append(str(directory))
    if installer_dir.is_dir():
        # the installer tests' helper, by its path: `tests/` stands before `tests/installer/`
        if (installer_dir / "_base.py").is_file() and "_base" not in sys.modules:
            load_module_from_path("_base", installer_dir / "_base.py")
        standard_tests.addTests(
            loader.discover(start_dir=str(installer_dir),
                            top_level_dir=str(installer_dir))
        )

    tests_dir = PROJECT_ROOT / "tests"
    for module_name in CURATED_UNITTEST_MODULES:
        if not (tests_dir / f"{module_name}.py").is_file():
            raise FileNotFoundError(
                f"curated test module {module_name!r} is missing from {tests_dir}; "
                "update CURATED_UNITTEST_MODULES in tests/run_tests.py"
            )
        standard_tests.addTests(
            loader.discover(start_dir=str(tests_dir),
                            pattern=f"{module_name}.py",
                            top_level_dir=str(tests_dir))
        )
    return standard_tests


if __name__ == '__main__':
    unittest.main()
