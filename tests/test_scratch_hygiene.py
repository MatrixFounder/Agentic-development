"""Tests for `tests/_scratch.py` — the in-repo scratch lifecycle.

This mechanism deletes directories, so the thing worth constraining is not that it cleans
up but that it cleans up **only what it owns**. An earlier design swept the shared root at
session start and corrupted concurrent runs; these tests exist so that cannot return
unnoticed.

Every test redirects the module's paths at a temporary location — nothing here touches the
real `tests/.scratch`. A process removes its own session directory at exit, by a handler bound to
that directory and its root, so a unittest run leaves no scratch behind (TS-1, TASK 128).
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRATCH = PROJECT_ROOT / "tests" / "_scratch.py"

spec = importlib.util.spec_from_file_location("_scratch_uut", SCRATCH)
scratch = importlib.util.module_from_spec(spec)
sys.modules["_scratch_uut"] = scratch
spec.loader.exec_module(scratch)


class _Redirected(unittest.TestCase):
    """Point the module at a throwaway root for the duration of one test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / ".scratch"
        self._saved = (scratch.REPO_SCRATCH, scratch.LEGACY_SCRATCH, scratch._session_dir)
        scratch.REPO_SCRATCH = self.root
        scratch.LEGACY_SCRATCH = (Path(self._tmp.name) / "legacy",)
        scratch._session_dir = None

    def tearDown(self):
        scratch.REPO_SCRATCH, scratch.LEGACY_SCRATCH, scratch._session_dir = self._saved
        self._tmp.cleanup()


class TestSessionIsolation(_Redirected):
    """A session must never reach into another session's directory."""

    def test_workspace_lives_under_a_pid_named_session_dir(self):
        workspace = scratch.repo_scratch_dir("handoff_")
        self.assertTrue(workspace.is_dir())
        self.assertEqual(workspace.parent.parent, self.root)
        self.assertTrue(workspace.parent.name.startswith(f"s{os.getpid()}_"))

    def test_stale_sweep_spares_a_live_session(self):
        # The regression that made two concurrent pytest shells fail 25 of 60 times.
        live = self.root / f"s{os.getpid()}_live"
        live.mkdir(parents=True)
        (live / "in-use.md").write_text("held open\n")

        scratch.sweep_stale_sessions()

        self.assertTrue((live / "in-use.md").exists(), "swept a live session's workspace")

    def test_stale_sweep_removes_a_dead_session(self):
        dead_pid = _a_dead_pid()
        dead = self.root / f"s{dead_pid}_old"
        dead.mkdir(parents=True)
        (dead / "left.md").write_text("from a killed run\n")

        removed = scratch.sweep_stale_sessions()

        self.assertFalse(dead.exists())
        self.assertGreaterEqual(removed, 1)

    def test_unparsable_session_name_is_removed(self):
        junk = self.root / "s-not-a-pid"
        junk.mkdir(parents=True)
        scratch.sweep_stale_sessions()
        self.assertFalse(junk.exists())

    def test_session_sweep_removes_only_this_session(self):
        mine = scratch.repo_scratch_dir("mine_")
        other = self.root / f"s{os.getpid()}_other"
        other.mkdir(parents=True)

        scratch.sweep_session()

        self.assertFalse(mine.exists())
        self.assertTrue(other.exists())


class TestHostileRootStates(_Redirected):
    """`tests/.scratch` may already exist as something other than a directory."""

    def test_symlink_root_is_replaced_not_followed(self):
        # A symlink would make every sweep a silent no-op and place workspaces outside
        # the repository, defeating the containment this module exists for.
        outside = Path(self._tmp.name) / "outside"
        outside.mkdir()
        self.root.symlink_to(outside)

        workspace = scratch.repo_scratch_dir("x_")

        self.assertFalse(self.root.is_symlink())
        self.assertNotIn("outside", str(workspace.resolve()))

    def test_regular_file_root_is_replaced(self):
        self.root.parent.mkdir(parents=True, exist_ok=True)
        self.root.write_text("not a directory\n")

        workspace = scratch.repo_scratch_dir("x_")

        self.assertTrue(workspace.is_dir())
        self.assertTrue(self.root.is_dir())


class TestLegacyAndFailures(_Redirected):
    """Legacy directories, and the refusal to hide a failed cleanup."""

    def test_legacy_directories_are_collected(self):
        legacy = scratch.LEGACY_SCRATCH[0]
        (legacy / "run_old").mkdir(parents=True)
        scratch.sweep_stale_sessions()
        self.assertFalse(legacy.exists())

    def test_remove_reports_a_real_failure(self):
        # ignore_errors=True would turn a broken cleanup into a green run.
        target = self.root / "guarded"
        target.mkdir(parents=True)
        (target / "f.md").write_text("x\n")
        self.root.chmod(0o500)  # deny writes to the parent, so removal cannot succeed
        try:
            with self.assertRaises(PermissionError):
                scratch._remove(target)
        finally:
            self.root.chmod(0o700)

    def test_removing_an_absent_path_is_not_an_error(self):
        scratch._remove(self.root / "never-existed")


class TestExitSweep(_Redirected):
    """TC-H1 and TC-H2 (TASK 128 R6): a process sweeps its own session at exit, and a root that
    another process swept meanwhile is made again."""

    def test_h1_a_process_removes_its_session_at_exit(self):
        # In a child process: `atexit` runs at its exit, and this process never calls
        # `atexit._run_exitfuncs()`. The child names a second root before it exits; the handler
        # of the first session must leave that root alone (R6.1).
        base = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, base, True)
        first, second = base / "first", base / "second"
        second.mkdir()
        code = "\n".join([
            "import importlib.util",
            "from pathlib import Path",
            f"spec = importlib.util.spec_from_file_location('scratch_child', {str(SCRATCH)!r})",
            "mod = importlib.util.module_from_spec(spec)",
            "spec.loader.exec_module(mod)",
            f"mod.REPO_SCRATCH = Path({str(first)!r})",
            "mod.LEGACY_SCRATCH = ()",
            "mod.session_scratch()",
            f"mod.REPO_SCRATCH = Path({str(second)!r})",
        ])
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True,
                              text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(first.exists(), "the session directory or its root stayed")
        self.assertTrue(second.is_dir(), "the handler removed the root named at exit")

    def test_h2_a_root_swept_meanwhile_is_made_again(self):
        # Another process removed the empty root between `_ensure_root` and `mkdtemp` (R6.4).
        real, calls = tempfile.mkdtemp, []

        def mkdtemp(*args, **kwargs):
            calls.append(kwargs.get("dir"))
            if len(calls) == 1:
                scratch.REPO_SCRATCH.rmdir()
            return real(*args, **kwargs)

        with mock.patch.object(scratch.tempfile, "mkdtemp", side_effect=mkdtemp):
            workspace = scratch.session_scratch()
        self.assertTrue(workspace.is_dir())
        self.assertEqual(len(calls), 2)

    def test_h2_a_root_swept_inside_ensure_root_is_made_again(self):
        # The sweep of another process can also land inside `_ensure_root`, which then raises
        # `FileNotFoundError`, or `FileExistsError` from its `mkdir(exist_ok=True)` (R6.4).
        for error in (FileNotFoundError(2, "No such file or directory"),
                      FileExistsError(17, "File exists")):
            with self.subTest(error=type(error).__name__):
                scratch._session_dir = None
                real, calls = scratch._ensure_root, []

                def ensure_root():
                    calls.append(True)
                    if len(calls) == 1:
                        raise error
                    return real()

                with mock.patch.object(scratch, "_ensure_root", side_effect=ensure_root):
                    workspace = scratch.session_scratch()
                self.assertTrue(workspace.is_dir())
                self.assertEqual(len(calls), 2)


class TestRunnerDoesNotSweep(unittest.TestCase):
    """The unittest runner must not touch in-repo scratch — it never creates any."""

    def test_run_tests_module_has_no_sweep_hook(self):
        source = (PROJECT_ROOT / "tests" / "run_tests.py").read_text()
        self.assertNotIn("sweep_repo_scratch", source)
        self.assertNotIn("sweep_stale_sessions", source)

    def test_curated_module_absence_is_loud(self):
        # The .is_file() guard it replaced turned drift into a silent 249 -> 179 drop.
        source = (PROJECT_ROOT / "tests" / "run_tests.py").read_text()
        self.assertIn("raise FileNotFoundError", source)


def _a_dead_pid() -> int:
    """Return the pid of a process that has certainly exited."""
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid


if __name__ == "__main__":
    unittest.main()
