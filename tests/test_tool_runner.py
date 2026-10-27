import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
# `System.scripts` imports from any working directory (TASK 129 R1.1)
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from System.scripts import tool_runner  # noqa: E402 - needs the path append above
from System.scripts.tool_runner import execute_tool  # noqa: E402 - needs the path append above

sys.path.append(str(Path(__file__).resolve().parent))
from _scratch import repo_scratch_dir  # noqa: E402 - needs the path append above


class TestToolRunner(unittest.TestCase):
    def setUp(self):
        # execute_tool takes the working directory as the repository root (TASK 129 R1.2)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(REPO_ROOT)
        self.repo_root = Path.cwd().resolve()
        # an in-repo directory that git ignores: the tool runner reads only repository paths,
        # and an interrupted run then leaves no untracked path (TASK 122 R3.4)
        self.test_dir = repo_scratch_dir("tool_").resolve()
        self.rel = self.test_dir.relative_to(self.repo_root).as_posix()
        (self.test_dir / "test.txt").write_text("hello world")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @unittest.skipIf(shutil.which("git") is None, "git is not on PATH")
    def test_the_scratch_directory_is_ignored(self):
        # TASK 122 R3.4: the allowed bare pytest runs this test, so its files stay where git
        # ignores them, and an interrupted run leaves no untracked path
        done = subprocess.run(["git", "check-ignore", "-q", str(self.test_dir)],
                              cwd=str(self.repo_root))
        self.assertEqual(done.returncode, 0)

    def test_read_file_success(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": f"{self.rel}/test.txt"}),
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "hello world")

    def test_read_file_not_found(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": f"{self.rel}/missing.txt"}),
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_path_traversal(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "../../../etc/passwd"}),
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Path traversal", result["error"])

    def test_absolute_prefix_bypass_is_blocked(self):
        fake_path = f"{self.repo_root}-evil/test.txt"
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": fake_path}),
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Path traversal", result["error"])

    def test_write_file(self):
        tool_call = {
            "name": "write_file",
            "arguments": json.dumps({
                "path": f"{self.rel}/new.txt",
                "content": "new content",
            }),
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertTrue((self.test_dir / "new.txt").exists())

    def test_list_directory(self):
        tool_call = {
            "name": "list_directory",
            "arguments": {"path": self.rel},
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertIn(f"{self.rel}/test.txt", result["files"])

    def test_unknown_tool(self):
        tool_call = {"name": "fake_tool", "arguments": {}}
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Unknown tool", result["error"])

    def test_run_tests_blocked_command(self):
        tool_call = {
            "name": "run_tests",
            "arguments": {"command": "rm -rf /"},
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Command not allowed", result["error"])

    def test_run_tests_blocks_shell_metacharacters(self):
        tool_call = {
            "name": "run_tests",
            "arguments": {"command": "pytest -q; echo injected"},
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("metacharacters", result["error"])

    def test_run_tests_invalid_cwd_is_blocked(self):
        tool_call = {
            "name": "run_tests",
            "arguments": {"command": "pytest -q", "cwd": "../../../"},
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Invalid working directory", result["error"])

    def test_run_tests_invalid_timeout(self):
        tool_call = {
            "name": "run_tests",
            "arguments": {"command": "pytest -q", "timeout_seconds": 0},
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("timeout_seconds", result["error"])


    #: TASK 112 R5.3: the whole commands `run_tests` accepts; any other option or operand asks.
    ALLOWED = ("pytest", "pytest -q", "pytest -q --tb=short", "python -m pytest",
               "python3 -m pytest", "npm test", "cargo test")
    REFUSED = ("npx jest", "pytest -p x", "pytest --basetemp=/tmp/x", "python3 -m pytest -x",
               "npm test -- -u", "cargo test x", "pytest tests", "python -m pytest -q")

    def test_t1_run_tests_refuses_options_and_npx_jest(self):
        """TC-T1 (TASK 112 R5.3): an option can run a program, delete a directory or overwrite a
        file, and `npx jest` downloads jest. Base-fail: the base accepts every one of them."""
        for command in self.REFUSED:
            with self.subTest(command=command):
                self.assertFalse(tool_runner._is_allowed_test_command(shlex.split(command)))
        # Tokens, not text: a quoted `"pytest -q"` is one token, a program of that name.
        for parts in (["pytest -q"], ["python", "-m pytest"], ["npm test"]):
            with self.subTest(parts=parts):
                self.assertFalse(tool_runner._is_allowed_test_command(parts))
        with mock.patch.object(tool_runner.subprocess, "run",
                               side_effect=AssertionError("a refused command ran")):
            result = execute_tool({"name": "run_tests", "arguments": {"command": "npx jest"}})
        self.assertFalse(result["success"])
        self.assertIn("Command not allowed", result["error"])
        for command in self.ALLOWED:
            self.assertIn(command, result["error"])

    def test_t2_policy_accepts_the_whole_commands(self):
        """TC-T2 (TASK 112 R5.3), the default command among them."""
        self.assertIn(tool_runner.DEFAULT_TEST_COMMAND, self.ALLOWED)
        for command in self.ALLOWED:
            with self.subTest(command=command):
                self.assertTrue(tool_runner._is_allowed_test_command(shlex.split(command)))


class TestWorkingDirectory(unittest.TestCase):
    """TC-W1 (TASK 129 R1.2): `TestToolRunner.setUp` runs at the repository root.

    Its cleanup changes back to the directory that the test started in.
    """

    def test_w1_setup_changes_into_the_root_and_back(self):
        start = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, start, ignore_errors=True)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(start)
        case = TestToolRunner("test_unknown_tool")
        case.setUp()
        try:
            self.assertEqual(Path.cwd().resolve(), REPO_ROOT)
        finally:
            case.tearDown()
            case.doCleanups()
        self.assertEqual(Path.cwd().resolve(), start)


if __name__ == "__main__":
    unittest.main()
