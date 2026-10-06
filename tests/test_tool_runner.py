import json
import shlex
import shutil
import unittest
from pathlib import Path
from unittest import mock

from System.scripts import tool_runner
from System.scripts.tool_runner import execute_tool


class TestToolRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_tool_test")
        self.test_dir.mkdir(exist_ok=True)
        (self.test_dir / "test.txt").write_text("hello world")
        self.repo_root = Path.cwd().resolve()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "tests/temp_tool_test/test.txt"}),
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "hello world")

    def test_read_file_not_found(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "tests/temp_tool_test/missing.txt"}),
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
                "path": "tests/temp_tool_test/new.txt",
                "content": "new content",
            }),
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertTrue((Path("tests/temp_tool_test/new.txt")).exists())

    def test_list_directory(self):
        tool_call = {
            "name": "list_directory",
            "arguments": {"path": "tests/temp_tool_test"},
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertIn("tests/temp_tool_test/test.txt", result["files"])

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


if __name__ == "__main__":
    unittest.main()
