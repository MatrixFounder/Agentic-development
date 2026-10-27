# Code Review: Task 129.2 — the test paths, pytest 9.1.1 and `_pid_alive`

- **Date:** 2026-10-26
- **Reviewer:** `code-reviewer` (subagent), `03-develop-single-task` step 4.
- **Status:** APPROVED, MERGE. 0 BLOCKING, 0 MAJOR, 3 MINOR.
- **Reviewed:** the diff of `tests/test_tool_runner.py`, `tests/test_tool_runner_security_contract.py`,
  `tests/test_schemas_stub.py`, `tests/_scratch.py` and `requirements-dev.txt`, at tree fingerprint
  `ea273c11da9e`. The reviewer quoted it; the orchestrator recomputed the same value at the return.
  The reviewer planted in a detached worktree outside the repository and removed it.
- **Kept by:** the orchestrator, from the reviewer's hand-back.

## Assessment

The change does what the task file asks, in its five files only. A11 holds: no file of
`System/scripts/` or `.agent/tools/` changed. Plantings in the worktree:

| Planting | Measured |
| :--- | :--- |
| revert R1.1 | exit 2, `ModuleNotFoundError: No module named 'System'`, from `tests/` and from outside |
| revert R1.2 | green from `tests/`; `14 failed` from outside the repository only (M1) |
| revert R1.3 | `5 failed, 734 passed`, each a `FileNotFoundError` |
| revert R5.1 | TC-S1 fails: `[call(<pid>, 0)] != []` |
| the Windows branch forced on POSIX | `test_stale_sweep_removes_a_dead_session` fails (R5.2) |

## Comments

### BLOCKING

None.

### MAJOR

None.

### MINOR

| ID | Pillar | Finding | Resolution |
| :--- | :--- | :--- | :--- |
| M1 | Testing | No test guarded R1.2 or its restore of the working directory | TC-W1, class `TestWorkingDirectory`; the task file names it |
| M2 | Quality | The docstring of `_pid_alive` left a stale directory "for the next run", which on Windows never collects it | "for a later run on POSIX to collect" |
| M3 | Quality | One `# noqa: E402` carried no reason, unlike its neighbours | the reason added |

**TC-W1, measured after the fix.** It passes. Three plantings in the live tree, each restored and
checked byte-identical by sha256:

- R1.2 removed: fails, `ValueError` of `relative_to` in `setUp`;
- the cleanup of `setUp` dropped: fails, the working directory stays at the root;
- the two lines swapped: fails, the cleanup returns to the root.

The runs after the fixes: from `tests/` with pytest 9.0.2 and with the venv's 9.1.1, and from a
directory outside the repository, each `740 passed`; the three modules of R1 from the root,
`20 passed`.

**Before the task:**

- `tests/test_schemas_stub.py:13@2a7d11c` puts `schemas` into `sys.modules` and never removes it;
  line 15 holds trailing whitespace.
- `git worktree list` names two prunable worktrees of other sessions. The run did not touch them.

## Verified (clean pass)

- **Requirements checked:** R1.1–R1.4, R2.1–R2.2, R5.1–R5.3; A1, A2, A7, A11.
- **Edge cases considered:**
  - the root on `sys.path` in another spelling: `PYTHONPATH=.`, and a path through a symbolic link;
  - a bare `.venv/bin/pytest` from the root, and `python -m unittest` from `tests/`;
  - the order of `addCleanup` and `chdir`, and a `setUp` that fails after the `chdir`;
  - on Windows the sweep still removes legacy directories and names without a pid, and no
    `s<pid>_` directory.
- **Tests observed:** the evidence of the brief, reproduced: TC-E1 to TC-E4, the run from outside
  the repository, and the local gates, where step 05 fails only on the four planned red tests of
  Task 129.1.
- **R2:** `requirements-dev.txt` is the only pin; the five CI install steps and the README install
  from it.

`{"review_status": "APPROVED", "has_critical_issues": false, "e2e_tests_pass": true, "stubs_replaced": true}`
