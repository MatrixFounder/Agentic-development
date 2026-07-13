"""SS-1 regression: update_state.py must anchor .agent/sessions at the repo
root regardless of the invocation CWD (docs/issues/ss-1-*.md)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "update_state.py"
ARGS = ["--mode", "Test", "--task", "t", "--status", "s", "--summary", "x"]


class UpdateStateAnchorTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def _run(self, cwd, env_extra=None):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        env.update(env_extra or {})
        return subprocess.run([sys.executable, str(SCRIPT)] + ARGS,
                              cwd=str(cwd), env=env, text=True,
                              capture_output=True, timeout=60)

    def _state(self, base):
        return Path(base) / ".agent" / "sessions" / "latest.yaml"

    def test_subdir_invocation_writes_to_repo_root(self):
        (self.root / ".git").mkdir()
        sub = self.root / "skills" / "some-skill"
        sub.mkdir(parents=True)
        proc = self._run(sub)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file(),
                        "state must land at the repo root")
        self.assertFalse((sub / ".agent").exists(),
                         "no stray .agent/ inside the subdir (SS-1)")

    def test_worktree_git_file_is_a_root_marker(self):
        (self.root / ".git").write_text("gitdir: /elsewhere\n",
                                        encoding="utf-8")
        sub = self.root / "sub"
        sub.mkdir()
        proc = self._run(sub)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file())
        self.assertFalse((sub / ".agent").exists())

    def test_repo_root_invocation_unchanged(self):
        (self.root / ".git").mkdir()
        proc = self._run(self.root)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file())

    def test_no_git_falls_back_to_claude_project_dir(self):
        target = self.root / "proj"
        (target / ".agent").mkdir(parents=True)
        lone = self.root / "lone"
        lone.mkdir()
        proc = self._run(lone,
                         {"CLAUDE_PROJECT_DIR": str(target)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(target).is_file())
        self.assertFalse((lone / ".agent").exists())

    def test_no_git_no_env_keeps_legacy_cwd_behavior(self):
        lone = self.root / "lone"
        lone.mkdir()
        proc = self._run(lone)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(lone).is_file(),
                        "zero-setup legacy fallback must keep working")

    def test_existing_state_at_root_is_merged_not_forked(self):
        (self.root / ".git").mkdir()
        first = self._run(self.root)
        self.assertEqual(first.returncode, 0, first.stderr)
        sid = self._state(self.root).read_text(encoding="utf-8")
        sub = self.root / "deep" / "er"
        sub.mkdir(parents=True)
        second = self._run(sub)
        self.assertEqual(second.returncode, 0, second.stderr)
        sid2 = self._state(self.root).read_text(encoding="utf-8")
        line = [l for l in sid.splitlines() if l.startswith("session_id:")]
        line2 = [l for l in sid2.splitlines() if l.startswith("session_id:")]
        self.assertEqual(line, line2,
                         "same session_id — subdir run updates, not forks")


if __name__ == "__main__":
    unittest.main()
