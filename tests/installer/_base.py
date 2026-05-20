"""Shared base for installer ``unittest`` tests (Task 063-01 test scaffold).

This replaces the pytest ``conftest.py`` named in the task files: the repo's
test harness is ``unittest`` (``tests/run_tests.py``), pytest is not installed,
and TASK.md NFR-5 caps dependencies at stdlib + PyYAML — so no third-party
fixture plugin is introduced. ``unittest`` needs only ``tempfile`` for the
isolated-workspace fixture.

Importing this module also puts ``System/scripts`` on ``sys.path`` so test
modules can ``import installer.*`` without ``install.py``'s bootstrap.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

#: Repo root — three levels up from tests/installer/_base.py.
FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]

_SCRIPTS = FRAMEWORK_ROOT / "System" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


class InstallerTestCase(unittest.TestCase):
    """Base TestCase providing an isolated temp workspace per test.

    ``self.tmp`` is a fresh ``Path`` cleaned up automatically. ``make_target()``
    creates a target-project directory (optionally ``git init``-ed) inside it.
    """

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="installer-test-")
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def make_target(self, *, git: bool = True) -> Path:
        """Create a fresh target-project directory inside the temp workspace."""
        target = Path(tempfile.mkdtemp(dir=self.tmp))
        if git:
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        return target
