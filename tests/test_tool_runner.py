
import unittest
import json
import os
import shutil
from pathlib import Path
from System.scripts.tool_runner import execute_tool

class TestToolRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_tool_test")
        self.test_dir.mkdir(exist_ok=True)
        # Create a dummy file
        (self.test_dir / "test.txt").write_text("hello world")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "tests/temp_tool_test/test.txt"})
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "hello world")

    def test_read_file_not_found(self):
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "tests/temp_tool_test/missing.txt"})
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_path_traversal(self):
        # Attempt to read /etc/passwd via ../../../
        tool_call = {
            "name": "read_file",
            "arguments": json.dumps({"path": "../../../etc/passwd"})
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Path traversal", result["error"])

    def test_write_file(self):
        tool_call = {
            "name": "write_file",
            "arguments": json.dumps({
                "path": "tests/temp_tool_test/new.txt",
                "content": "new content"
            })
        }
        result = execute_tool(tool_call)
        self.assertTrue(result["success"])
        self.assertTrue((Path("tests/temp_tool_test/new.txt")).exists())

    def test_list_directory(self):
        tool_call = {
            "name": "list_directory",
            "arguments": {"path": "tests/temp_tool_test"} # Passing dict directly to test that logic too
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
            "arguments": {"command": "rm -rf /"}
        }
        result = execute_tool(tool_call)
        self.assertFalse(result["success"])
        self.assertIn("Command not allowed", result["error"])

if __name__ == "__main__":
    unittest.main()
