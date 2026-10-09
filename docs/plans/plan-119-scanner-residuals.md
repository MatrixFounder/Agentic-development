# PLAN 119 — The in-process scans skip a file that is not regular, the test helper's PATH holds system directories only, and printable escapes the backslash

**TASK:** [docs/TASK.md](../tasks/task-119-scanner-residuals.md) (revision 6) · **Covers:** R1–R7 · **Acceptance:** A1–A6.

**Revision:** 5: stage-2 fix round 2 (D5 to D7); revision 4 per fix round 1.

<!-- contract:sequence -->

## Sequencing rule

A small run on TASK 118's staging mechanics (TASK R7). No `docs/tasks/task-119-*.md` file is
written, on the precedent of PLAN 111 to PLAN 118.

| Order | Cluster | Covers |
| :--- | :--- | :--- |
| A | Base check and staged copies | R7.1 |
| B | Tests first (Red), then the code (Green) | R1–R4 |
| C | Base-fail and mutation runs | R7.3, R7.4 |
| D | Documents and records | R5, R6 |
| E | The stage-3 patch and the gates | R7.4, A6 |
| F | Stage 2 | R7.4 |
| G | §4.5, stage 3 and stage 4 | R7.4, A6 |

<!-- contract:coverage -->

### Coverage

| Requirement | Steps |
| :--- | :--- |
| R1 | B1, B2 (TC-F1, TC-F2, TC-F3) |
| R2 | B1, B2 (TC-F4) |
| R3 | B1, B2 (TC-F5) |
| R4 | B1 |
| R5, R6 | D1, D2 |
| R7 | A1, A2, C1, C2, E1, E2, F1, G1, G2 |

## Declared paths

Edited:

- `.agent/skills/security-audit/scripts/audit/helpers.py` (by the patch in G)
- `.agent/skills/security-audit/scripts/audit/scanners.py` (by the patch in G)
- `tests/test_lockfile_audit.py` (by the patch in G)
- `.agent/skills/security-audit/SKILL.md`
- `CHANGELOG.md`
- `CHANGELOG.ru.md`
- `docs/BACKLOG.md`
- `docs/backlog/wi-51-residual-routes-of-the-task-118-scanner-review.md`

Created:

- `.agent/skills/security-audit/scripts/audit/helpers_next.py` (removed by the patch in G)
- `.agent/skills/security-audit/scripts/audit/scanners_next.py` (removed by the patch in G)
- `tests/staged_lockfile_audit.py` (removed by the patch in G)
- `docs/reviews/framework-audit-119-stage3.diff`

The run's `docs/TASK.md`, `docs/PLAN.md`, the audit record `docs/reviews/framework-audit-119.md`
and the TASK 118 archive pair are declared by `framework-upgrade` §5.

**Rollback point.** Base `5d0c83f0832a7960d98d6c1a00a5e94288250725`. No file outside the repository
is edited except the scratchpad. The scratchpad holds no copy of a repository file. Its files are
`stage_driver.py`, `bootstrap_next.py`, `staging.py`, `mutation_driver.py`,
`gen_stage3_patch.py`, `run_gates.sh`, `regcheck.py` and the gate logs that `run_gates.sh`
writes under `RUNNER_TEMP`; each is deleted after G. Every Python run in the repository sets
`PYTHONDONTWRITEBYTECODE=1`, and every pytest run passes `-p no:cacheprovider`, so no ignored
cache appears in the tree.

## Cluster A — base check and staged copies

- [x] A1 `framework-upgrade` §3.1: `HEAD` equals the base; each edited path is tracked; each created
      path gives `git check-ignore` exit 1; each path matches `[A-Za-z0-9._/-]+`.
- [x] A2 `helpers_next.py`, `scanners_next.py` and `tests/staged_lockfile_audit.py` are byte copies
      of their base files. The driver of TASK R7.2, mode `next` and mode `base`: every case passes.
      Mode `next` loads in this order: the package with `__path__` the final `audit/`, the staged
      `.helpers`, the staged `.scanners`, then the final `__init__.py`, which loads the final
      `.external`. It asserts each staged module's `__file__`, and that `external.run_tool` and
      `external.printable` are the staged helpers' objects.

## Cluster B — tests, then code

- [x] B1 Tests first, in `tests/staged_lockfile_audit.py`: TC-F1 to TC-F5 and the docstring of
      R4.1. The driver, mode `next`: TC-F1, TC-F2, TC-F4 and TC-F5 fail; TC-F3 passes.
- [x] B2 Code: `open_regular_text` and the backslash escape in `helpers_next.py`; the six sites
      in `scanners_next.py`; `AuditTestCase`'s `PATH` of R2.1. The driver, mode `next`: every case
      passes.

## Cluster C — base-fail and mutation runs

- [x] C1 The driver, mode `base`: TC-F1, TC-F2 and TC-F5 fail, TC-F1 and TC-F2 by their timeout;
      no other case fails. TC-F3 passes, as TASK A2 states. TC-F4 passes, because the `PATH` lives
      in the staged test module; the audit record states it, and C2's `PATH` mutant shows the case
      can fail.
- [x] C2 `mutation_driver.py`: the ten mutants of TASK R7.3, each in a fresh subprocess; each is
      killed; the SHA-256 of the staged files is equal after the restore.

## Cluster D — documents and records

- [x] D1 `security-audit` §2 (R5.1, R5.2).
- [x] D2 The changelogs (R6.1); WI-51 closed (R6.2); the `mcp-scan` line of §2 (R6.3).
- [x] D3 The register check of each file of D1 and D2: no `WARN` on an added line.

## Cluster E — the stage-3 patch and the gates

- [x] E1 `gen_stage3_patch.py` writes `docs/reviews/framework-audit-119-stage3.diff`: the three
      final paths take the text of their staged files, the three staged files are deleted, and no
      other path changes. `git apply --check` passes.
- [x] E2 `run_gates.sh`, the CI steps: every step passes. The skill's tests pass. The register
      check of D3 passes. Every path of `git status` is declared.

## Cluster F — stage 2

- [x] F1 A `code-reviewer` and a `security-auditor` at one fingerprint, with the SHA-256 of the
      patch and of each staged file. The bound is 3 rounds. The external tools are installed, so
      the security auditor runs the scan in full. A fix round writes its test first and runs B2,
      C1, C2, E1 and E2 again.

## Cluster G — §4.5, stage 3 and stage 4

- [x] G1 Stage 3, as PLAN 118 I1:
  1. §4.5: `check_positional_refs.py --targets-changed`, then with `--fix`; the audit record lists
     every file a repair touched;
  2. the patch and the staged files hash to the values F1 quoted; the audit record holds the patch
     text in a `~~~~diff` fence;
  3. the audit record holds the SHA-256 and mode of every file the patch touches;
  4. `git apply --whitespace=nowarn` of the patch;
  5. postcondition: each final path hashes to the value step 2 recorded for its staged file, the
     staged files are gone, and `git apply --check -R` passes.

  A mismatch at step 2 means STOP: the patch returns to F1, unless a repair of step 1 changed it
  and F1's reviewers saw it. A non-zero exit at step 4 means STOP and report; `git apply` is
  atomic, so nothing was applied and nothing is restored.

  Then the gates of E2 and `validate_skill.py .agent/skills/security-audit` run again.
- [x] G2 Stage 4: a `code-reviewer` and a `security-auditor` on the applied patch.

**Failure** (TASK 118 R7.8):

- A failed postcondition or gate of G1, or a G2 review that is rejected or `FAIL`:
  `git apply -R --whitespace=nowarn` of the same patch. Each file's SHA-256 and mode then equal
  those of G1 step 3; a mismatch, or a non-zero exit, means STOP. The audit record lists under
  `Pending after restore` §2 of `security-audit`, the two changelogs and WI-51, and the
  operator decides.
- An `INCOMPLETE` G2 security audit as the only failure: the same restore, then `security-audit`
  §6.2 re-runs the unfinished part with the recorded patch. On a pass, G1 is applied again with
  every step, and G2 runs again; otherwise the operator decides.

## Retro

`framework-upgrade` §6 with the run id `framework-upgrade-wi-51-scanner-residuals`.

## Schedule

<!-- contract:schedule -->

```json
{
  "schema": "plan-schedule/v1",
  "tasks": [
    {"id": "119.A", "title": "Staged copies", "stage": "Build", "est": 1, "deps": [], "status": "done"},
    {"id": "119.B", "title": "Tests and code", "stage": "Build", "est": 2, "deps": ["119.A"], "status": "done"},
    {"id": "119.C", "title": "Base-fail and mutations", "stage": "Build", "est": 1, "deps": ["119.B"], "status": "done"},
    {"id": "119.D", "title": "Documents and records", "stage": "Build", "est": 1, "deps": ["119.A"], "status": "done"},
    {"id": "119.E", "title": "Patch and gates", "stage": "Closure", "est": 1, "deps": ["119.C", "119.D"], "status": "done"},
    {"id": "119.F", "title": "Stage 2", "stage": "Closure", "est": 1, "deps": ["119.E"], "status": "done"},
    {"id": "119.G", "title": "Stage 3 and 4", "stage": "Closure", "est": 1, "deps": ["119.F"], "status": "done"}
  ]
}
```

<!-- generated:plan-gantt-start -->
<!-- generated:plan-gantt-end -->
