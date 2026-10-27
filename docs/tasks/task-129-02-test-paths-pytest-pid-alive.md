# Task 129-02: The test paths, pytest 9.1.1 and `_pid_alive`

## Use Case Connection

- UC-1: A developer runs pytest from `tests/`
- UC-3: A test run on Windows sweeps stale scratch

<!-- contract:goal -->

## Task Goal

Change the three test modules, the pytest pin and `_pid_alive` so that:

- every test under `tests/` passes from any working directory;
- the project venv runs pytest 9.1.1;
- `_pid_alive` sends no signal on Windows.

<!-- contract:changes -->

## Changes Description

### Changes in Existing Files

#### File: `tests/test_tool_runner.py`

- Add `import os`, and the constant `REPO_ROOT = Path(__file__).resolve().parents[1]`.
- When `str(REPO_ROOT)` is absent from `sys.path`, append it (R1.1). This runs before the line
  `tests/test_tool_runner.py:10@2a7d11c` `from System.scripts import tool_runner`.
- **Class `TestToolRunner`, method `setUp`** (R1.2), before its first line:
  1. `self.addCleanup(os.chdir, os.getcwd())`;
  2. `os.chdir(REPO_ROOT)`.

  The rest of `setUp` stays as it is.

**Why.** `tool_runner.execute_tool` takes `Path.cwd()` as the repository root (TASK R1.2).

#### File: `tests/test_tool_runner_security_contract.py`

- Add the constant
  `TOOL_RUNNER = Path(__file__).resolve().parents[1] / "System" / "scripts" / "tool_runner.py"`.
- The four tests read `TOOL_RUNNER` in place of `Path("System/scripts/tool_runner.py")` (R1.3).

#### File: `tests/test_schemas_stub.py`

- Add `from pathlib import Path`.
- `spec_from_file_location` takes
  `str(Path(__file__).resolve().parents[1] / ".agent" / "tools" / "schemas.py")` in place of
  `".agent/tools/schemas.py"` (R1.3).

#### File: `requirements-dev.txt`

- `pytest==9.0.2` becomes `pytest==9.1.1` (R2.1).
- `.venv/bin/python -m pip install -r requirements-dev.txt` runs after the edit (R2.2).

#### File: `tests/_scratch.py`

- **Function `_pid_alive(pid: int) -> bool`:** when `os.name == "nt"`, it returns `True` before the
  call of `os.kill` (R5.1). The POSIX branch stays as it is (R5.2). The docstring states the
  answer on Windows.
- **Module docstring**, the paragraph `**Why the start-up sweep still exists, narrowed.**`: it
  states that on Windows the sweep removes no session directory (R5.3).
- **Module docstring**, the paragraph `**Why a session is also swept at exit.**`: it states that
  the `atexit` handler removes the directory of each normal exit, on Windows too (R5.3).

No file of `System/scripts/` or `.agent/tools/` changes (R1.4).

<!-- contract:tests -->

## Test Cases

### Unit Tests

1. **TC-S1** of Task 129.1 → passes (A7).
2. `test_stale_sweep_spares_a_live_session` and `test_stale_sweep_removes_a_dead_session` → pass
   (R5.2).
3. **TC-W1** of `tests/test_tool_runner.py`, class `TestWorkingDirectory` (code review of Task 129.2,
   M1). `TestToolRunner.setUp` runs from a temporary directory → the working directory is the
   repository root. After the cleanups of the case it is the temporary directory again.
   - Fails when R1.2 is removed, when the cleanup is dropped, or when the two lines swap.

### End-to-end Tests

1. **TC-E1** — from `tests/`, `python3 -B -m pytest -p no:cacheprovider -q` → exit 0 (A1).
2. **TC-E2** — from `tests/`, `../.venv/bin/python -B -m pytest -p no:cacheprovider -q` → exit 0
   (A1).
3. **TC-E3** — from the root, `PYTHONPATH=. python3 -B -m pytest -p no:cacheprovider` over the
   three modules of R1 → exit 0 (UC-1 alternative 1a).
4. **TC-E4** — `.venv/bin/python -B -m pytest --version` → `pytest 9.1.1` (A2).

### Regression Tests

- Every `run:` step of `.github/workflows/framework-gates.yml`, run locally → each passes. The
  exceptions are TC-L1 and the v10 test of the mermaid skill, which pass after Task 129.3.
- `git diff 2a7d11c -- System/scripts .agent/tools` → no output (A11).

<!-- contract:acceptance -->

## Acceptance Criteria

- [ ] A1, A2, A7 and A11 hold.
- [ ] The code review approves.

## Notes

- An allow rule of `.claude/settings.local.json` names `tests/test_tool_runner.py` (TASK 123 §1).
  This task is not a framework upgrade. It writes no staged copy.
- The pytest of the global interpreter stays 9.0.2 (TASK §9).
