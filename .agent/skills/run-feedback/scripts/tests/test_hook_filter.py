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
        env.pop("RUN_FEEDBACK_MINE_ON_END", None)
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


SESSION_END = Path(__file__).resolve().parents[1] / "hooks" / "session_end_marker.py"


@unittest.skipUnless(SESSION_END.is_file(),
                     "session_end_marker not shipped yet: %s" % SESSION_END)
class TestSessionEndMineOnEnd(unittest.TestCase):
    """PostToolUse cannot see failing tool calls (verified live 2026-07-13),
    so mine-on-session-end is the primary automatic capture path."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.inbox = self.root / ".agent" / "feedback" / "inbox"

    def _write_transcript(self, path):
        pair = [
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "t1", "name": "Bash",
                 "input": {"command": "python3 skills/html/scripts/x.py"}}]}},
            {"type": "user", "timestamp": "2026-07-13T02:00:00Z",
             "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t1",
                 "is_error": True, "content": "boom\nExit code 2"}]}},
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(o) for o in pair) + "\n",
                        encoding="utf-8")

    def _run(self, env_extra):
        transcript = Path(self._tmp.name) / "shard" / "sess-9.jsonl"
        self._write_transcript(transcript)
        payload = {"session_id": "sess-9", "cwd": str(self.root),
                   "reason": "other", "transcript_path": str(transcript)}
        env = dict(os.environ)
        # Hermetic against the operator's session env (settings.local.json may
        # export the opt-in capture flags globally — they must not leak in).
        env.pop("RUN_FEEDBACK_CONFIG", None)
        env.pop("RUN_FEEDBACK_HOOK_DEBUG", None)
        env.pop("RUN_FEEDBACK_MINE_ON_END", None)
        env.pop("RUN_FEEDBACK_HOOKS", None)
        env["CLAUDE_PROJECT_DIR"] = str(self.root)
        env.update(env_extra)
        return subprocess.run([sys.executable, str(SESSION_END)],
                              input=json.dumps(payload), text=True,
                              capture_output=True, env=env,
                              cwd=str(self.root), timeout=120)

    def _journal_text(self):
        jdir = self.root / ".agent" / "feedback" / "journal"
        return "".join(p.read_text(encoding="utf-8")
                       for p in sorted(jdir.glob("*.md"))) \
            if jdir.is_dir() else ""

    def test_marker_only_without_mine_flag(self):
        proc = self._run({})
        self.assertEqual(proc.returncode, 0)
        self.assertIn("session_end | sess-9", self._journal_text())
        self.assertNotIn("mine_run", self._journal_text())
        self.assertFalse(self.inbox.is_dir() and any(self.inbox.iterdir()))

    def test_mine_on_end_collects_the_failure(self):
        proc = self._run({"RUN_FEEDBACK_MINE_ON_END": "1"})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        text = self._journal_text()
        self.assertIn("session_end | sess-9", text)
        self.assertIn("mine_run | session-end sess-9", text)
        findings = sorted(self.inbox.glob("fnd-*.json"))
        self.assertEqual(len(findings), 1)
        record = json.loads(findings[0].read_text(encoding="utf-8"))
        self.assertEqual(record["subject"]["component"], "html")
        self.assertEqual(record["subject"]["exit_code"], 2)
        self.assertEqual(record["sources"], ["transcript"])
