"""DEPRECATED (Wave 1, 2026-04-17): regression test for the legacy mock-agent runner.

Retained to verify `fcntl`-locking in `skill-session-state/scripts/update_state.py`
under concurrent writes. The mock agent it exercises is itself DEPRECATED — see
`.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py`.

Do not add new test coverage here; write new concurrent-state tests directly
against `update_state.py`.

Output goes to a temporary directory (`TemporaryDirectory`),
NOT into `docs/tasks/` — a previous version wrote `docs/tasks/mock_results/` and
dirtied the working tree on every run (task 084 R9).

The mock runs in a sandbox of a temporary directory: an empty `.git`, so
`update_state.py` anchors there, and a copy of `update_state.py` at the relative path the mock calls.
The allow rule `python3 -m pytest` runs this test without a prompt, and before the
sandbox each run rewrote the live `.agent/sessions/latest.yaml` (TASK 122 R3.4).
"""

import shutil
import subprocess
import time
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPAWN_SCRIPT = REPO / ".agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py"
UPDATE_STATE = ".agent/skills/skill-session-state/scripts/update_state.py"
LIVE_STATE = REPO / ".agent" / "sessions" / "latest.yaml"


def _sandbox(root):
    """*root* as the mock's repository: its own `.git`, and `update_state.py` where the mock
    calls it."""
    (root / ".git").mkdir()
    target = root / UPDATE_STATE
    target.parent.mkdir(parents=True)
    shutil.copy2(REPO / UPDATE_STATE, target)


def _live_state():
    return LIVE_STATE.read_bytes() if LIVE_STATE.is_file() else None


def _run_spawn(output_dir, root):
    cmd = [
        sys.executable, str(SPAWN_SCRIPT),
        "--task_name", "test-task-123",
        "--goal", "Verify infrastructure",
        "--output_dir", output_dir,
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}

    start_time = time.time()
    subprocess.run(cmd, check=True, cwd=str(root), env=env)
    duration = time.time() - start_time
    print(f"Agent finished in {duration:.2f}s")

    result_file = os.path.join(output_dir, "test-task-123.result.md")
    assert os.path.exists(result_file), f"Result file missing: {result_file}"

    with open(result_file, "r") as f:
        assert "Execution Log" in f.read(), "Content invalid"


def test_spawn():
    # TemporaryDirectory removes the sandbox and its copy of update_state.py on exit, where a
    # base temp of pytest would keep them (TASK 122, review round 2)
    before = _live_state()
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        _sandbox(root)
        _run_spawn(str(root / "mock_results"), root)
        record = (root / ".agent" / "sessions" / "latest.yaml").read_text(encoding="utf-8")
        assert "test-task-123" in record, "the mock's record is not in its sandbox"
    assert _live_state() == before, "the mock rewrote the live session state"


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp_dir:
        _sandbox(Path(tmp_dir))
        _run_spawn(os.path.join(tmp_dir, "mock_results"), Path(tmp_dir))
        print("SUCCESS")
