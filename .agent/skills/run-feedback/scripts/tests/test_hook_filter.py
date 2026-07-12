"""R12 — PostToolUse hook filter, driven as a real subprocess."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "posttooluse_filter.py"
SECRET = "abc123SECRET"


@unittest.skipUnless(HOOK.is_file(),
                     "hook script not shipped yet: %s" % HOOK)
class HookFilterTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.inbox = self.root / ".agent" / "feedback" / "inbox"

    def _run(self, payload=None, raw=None):
        env = dict(os.environ)
        env.pop("RUN_FEEDBACK_CONFIG", None)
        env.pop("RUN_FEEDBACK_HOOK_DEBUG", None)
        env["RUN_FEEDBACK_HOOKS"] = "1"
        env["CLAUDE_PROJECT_DIR"] = str(self.root)
        data = raw if raw is not None else json.dumps(payload)
        return subprocess.run([sys.executable, str(HOOK)], input=data,
                              text=True, capture_output=True, env=env,
                              cwd=str(self.root), timeout=120)

    def _payload(self, command, response, tool_name="Bash"):
        return {"session_id": "sess-1", "cwd": str(self.root),
                "tool_name": tool_name,
                "tool_input": {"command": command},
                "tool_response": response}

    def _findings(self):
        return sorted(self.inbox.glob("fnd-*.json")) \
            if self.inbox.is_dir() else []


class TestHookFilter(HookFilterTestCase):
    def test_bash_failure_with_exit_code_text_collects_one_finding(self):
        proc = self._run(self._payload(
            "python3 skills/html/scripts/x.py",
            {"stdout": "boom\nExit code 2", "stderr": ""}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "",
                         "hook stdout can reach the model — must stay empty")
        files = self._findings()
        self.assertEqual(len(files), 1)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(record["sources"], ["hook"])
        self.assertEqual(record["subject"]["component"], "html")
        self.assertEqual(record["subject"]["exit_code"], 2)

    def test_grep_exit_1_is_dropped(self):
        proc = self._run(self._payload(
            "grep -r needle .",
            {"stdout": "", "stderr": "", "exit_code": 1}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._findings(), [])

    def test_non_bash_tool_is_dropped(self):
        proc = self._run(self._payload(
            "irrelevant",
            {"stdout": "boom\nExit code 2", "stderr": ""},
            tool_name="Read"))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._findings(), [])

    def test_interrupted_command_is_dropped(self):
        proc = self._run(self._payload(
            "python3 skills/html/scripts/x.py",
            {"stdout": "partial\nExit code 2", "stderr": "",
             "interrupted": True}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._findings(), [])

    def test_secret_in_stderr_is_redacted_in_stored_finding(self):
        proc = self._run(self._payload(
            "python3 skills/pdf/scripts/y.py",
            {"stdout": "",
             "stderr": "fatal: token=%s\nExit code 2" % SECRET}))
        self.assertEqual(proc.returncode, 0)
        files = self._findings()
        self.assertEqual(len(files), 1)
        raw = files[0].read_text(encoding="utf-8")
        self.assertNotIn(SECRET, raw)
        self.assertIn("[REDACTED]", raw)

    def test_malformed_stdin_json_exits_0_silently(self):
        proc = self._run(raw="this is {not json at all")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")
        self.assertEqual(self._findings(), [])

    def test_exit_0_even_on_success_payload(self):
        proc = self._run(self._payload(
            "python3 skills/html/scripts/x.py",
            {"stdout": "all good\nExit code 0", "stderr": ""}))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self._findings(), [])


if __name__ == "__main__":
    unittest.main()
