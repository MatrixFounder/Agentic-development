from pathlib import Path

# read under the repository root, whatever the working directory (TASK 129 R1.3)
TOOL_RUNNER = Path(__file__).resolve().parents[1] / "System" / "scripts" / "tool_runner.py"


def test_tool_runner_no_shell_true_for_run_tests():
    src = TOOL_RUNNER.read_text(encoding="utf-8")
    assert "shell=True" not in src


def test_tool_runner_no_prefix_path_check():
    src = TOOL_RUNNER.read_text(encoding="utf-8")
    assert "startswith(str(repo_root))" not in src


def test_tool_runner_uses_relative_to_containment():
    src = TOOL_RUNNER.read_text(encoding="utf-8")
    assert "relative_to(repo_root)" in src


def test_tool_runner_has_shell_metachar_guard():
    src = TOOL_RUNNER.read_text(encoding="utf-8")
    assert "DISALLOWED_SHELL_CHARS" in src
