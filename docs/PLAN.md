# PLAN 120 — Stage 2 of framework-upgrade holds its reviews to the TASK and the lines the change touches

**TASK:** [docs/TASK.md](TASK.md) (revision 5) · **Covers:** R1–R4 · **Acceptance:** A1–A4.

**Revision:** 4: stage-2 fix round 2 (TASK D4); revision 3 per fix round 1 (TASK D3); revision 2
per the plan audit.

<!-- contract:sequence -->

## Sequencing rule

A small run on TASK 118's staging mechanics, with the differences of TASK R4.3. No
`docs/tasks/task-120-*.md` file is written, on the precedent of PLAN 111 to PLAN 119.

| Order | Cluster | Covers |
| :--- | :--- | :--- |
| A | Base check and the staged copy | R4.1 |
| B | The pin first (Red), then the patched text (Green) | R1, R2, A2 |
| C | Documents and records | R3, A3 |
| D | The stage-3 patch and the gates | R1, R4.2, A4 |
| E | Stage 2 | R4.3 |
| F | §4.5, stage 3 and stage 4 | R1, R4.2, R4.3, A1, A4 |

<!-- contract:coverage -->

### Coverage

| Requirement | Steps |
| :--- | :--- |
| R1 | B1, D1, F1 |
| R2 | B1, B2 (TC-B1) |
| R3 | C1, C2, C3 |
| R4 | A1, A2, D1, D2, E1, F1, F2 |

## Declared paths

Edited:

- `.agent/workflows/framework-upgrade.md` (by the patch in F)
- `tests/test_run_safety_rules.py` (by the patch in F)
- `System/Docs/WORKFLOWS.md`
- `CHANGELOG.md`
- `CHANGELOG.ru.md`
- `docs/BACKLOG.md`
- `docs/backlog/wi-52-stage-2-reviews-can-widen-a-framework-upgrade-task-beyond-its-changed-lines.md`

Created:

- `tests/staged_run_safety_rules.py` (removed by the patch in F)
- `docs/reviews/framework-audit-120-stage3.diff`

The run's `docs/TASK.md`, `docs/PLAN.md`, the audit record `docs/reviews/framework-audit-120.md`
and the TASK 119 archive pair are declared by `framework-upgrade` §5.

**Rollback point.** Base `da91d2fefa33242a47356e1b740055e645db5e1e`. No file outside the repository
is edited except the scratchpad. The scratchpad holds no copy of a repository file. Its files are
`staging.py`, `stage_driver.py`, `gen_stage3_patch.py`, `run_gates.sh`, `regcheck.py`, the gate
logs that `run_gates.sh` writes under `RUNNER_TEMP`, and the audit text that waits during a review
round. Each is deleted after F, or when the run stops. Every Python run in the
repository sets `PYTHONDONTWRITEBYTECODE=1`, and every pytest run passes `-p no:cacheprovider`, so
no ignored cache appears in the tree. While a review round runs, the audit record is not written;
its text waits in the scratchpad (`skill-parallel-orchestration` §2.4.1).

## Cluster A — base check and the staged copy

- [x] A1 Every check of `framework-upgrade` §3.1: `HEAD` equals the base; each edited path is
      tracked; each created path gives `git check-ignore` exit 1; each path matches
      `[A-Za-z0-9._/-]+`, has no `.git` or `..` segment, and does not start with `/`.
- [x] A2 `tests/staged_run_safety_rules.py` is a byte copy of `tests/test_run_safety_rules.py`.
      `stage_driver.py`, mode `base`, loads it by file path and runs it: every case passes.

## Cluster B — the pin, then the patched text

`staging.py` reads the bullet from the R1.1 fence of `docs/TASK.md` and indents it as R1.1 states,
so no second copy of the text exists. Its `patched(text)` inserts the bullet after the **LOW routes
of a fixed class** bullet. It fails unless the anchor occurs once and the bullet is absent.

`stage_driver.py` loads a test module by its file path, under a module name that is not `test_*`.
It replaces the module's `_read` so that `WORKFLOW` returns the given text and every other path is
read from disk. Then it runs the module's cases and prints the result of each case.

- [x] B1 Tests first: the staged module's `STEP_4` takes the bullet of R1.1 at its place. The
      bullet in `STEP_4` equals the R1.1 fence, whitespace collapsed. Mode `base` (the base text of
      `framework-upgrade.md`): `test_step_4_is_the_reviewed_text_to_the_end_of_section_3` fails,
      and every other case passes, `test_base_check_allows_the_fixture` among them.
- [x] B2 Mode `patched` (`patched(base text)`, in memory): every case passes. Mode `old-pin`
      (the base test module against the patched text): the same case fails, and every other case
      passes. TC-B1 holds when the three results hold.

## Cluster C — documents and records

- [x] C1 `System/Docs/WORKFLOWS.md`: item 5 of the §5 Safety Protocol list (R3.1).
- [x] C2 The changelogs (R3.2); WI-52 closed, and its index line moved under `## Closed` (R3.3).
- [x] C3 The register check of each file of C1 and C2: `regcheck.py` finds no `WARN` on an added
      line. Item 5 and the English changelog entry equal the fences of R3.1 and R3.2, whitespace
      collapsed.

## Cluster D — the stage-3 patch and the gates

- [x] D1 `gen_stage3_patch.py` writes `docs/reviews/framework-audit-120-stage3.diff`:
      `framework-upgrade.md` takes `patched(base text)`, `tests/test_run_safety_rules.py` takes the
      staged text, the staged file is deleted, and no other path changes. `git apply --check`
      passes.
- [x] D2 `run_gates.sh`, the CI steps of `.github/workflows/framework-gates.yml`: every step
      passes. The register check of C3 passes. Every path of `git status` is declared.

## Cluster E — stage 2

- [x] E1 A `code-reviewer` and a `security-auditor` at one fingerprint, with the SHA-256 of the
      patch, of the staged file and of `patched(base text)`. Each brief states the boundary of TASK
      R1.1. The external tools are installed, so the security auditor runs the scan in full. The
      bound is 3 rounds. A fix round that changes the bullet changes the pin first; every fix round
      runs B1, B2, C3, D1 and D2 again.

## Cluster F — §4.5, stage 3 and stage 4

- [x] F1 Stage 3, as PLAN 119 G1:
  1. §4.5: `check_positional_refs.py --targets-changed`, then with `--fix`; the audit record lists
     every file a repair touched;
  2. the patch and the staged file hash to the values E1 quoted; the audit record holds the patch
     text in a `~~~~diff` fence;
  3. the audit record holds the SHA-256 and mode of every file the patch touches;
  4. `git diff --quiet <base> -- .agent/workflows/framework-upgrade.md tests/test_run_safety_rules.py`
     exits 0, unless the audit lists a step-1 repair of that file; then
     `git apply --whitespace=nowarn` of the patch;
  5. postcondition: `tests/test_run_safety_rules.py` hashes to the value step 2 recorded for the
     staged file, `framework-upgrade.md` hashes to the value E1 quoted for `patched(base text)`,
     the staged file is gone, and `git apply --check -R` passes.

  A mismatch at step 2 means STOP: the patch returns to E1, unless a repair of step 1 changed it
  and E1's reviewers saw it. A non-zero exit at step 4 means STOP and report; `git apply` is
  atomic, so nothing was applied and nothing is restored.

  Then the gates of D2 run again, and A1 is checked: the bullet is the third bullet of stage 2.
- [x] F2 Stage 4: a `code-reviewer` and a `security-auditor` on the applied patch. Each brief
      states the boundary of TASK R1.1.

**Failure** (TASK 118 R7.8):

- A failed postcondition or gate of F1, or an F2 review that is rejected or `FAIL`:
  `git apply -R --whitespace=nowarn` of the same patch. Each file's SHA-256 and mode then equal
  those of F1 step 3; a mismatch, or a non-zero exit, means STOP. The audit record lists R3.1 to
  R3.3 under `Pending after restore`, and the operator decides. The same list is written when the
  run stops before F1 step 4 succeeds.
- An `INCOMPLETE` F2 security audit as the only failure: the same restore, then `security-audit`
  §6.2 re-runs the unfinished part with the recorded patch. On a pass, F1 is applied again with
  every step, and F2 runs again; otherwise the operator decides.

## Retro

`framework-upgrade` §6 with the run id `framework-upgrade-wi-52-stage2-boundary`.

## Schedule

<!-- contract:schedule -->

```json
{
  "schema": "plan-schedule/v1",
  "tasks": [
    {"id": "120.A", "title": "Staged copy", "stage": "Build", "est": 1, "deps": [], "status": "done"},
    {"id": "120.B", "title": "Pin and patched text", "stage": "Build", "est": 1, "deps": ["120.A"], "status": "done"},
    {"id": "120.C", "title": "Documents and records", "stage": "Build", "est": 1, "deps": ["120.A"], "status": "done"},
    {"id": "120.D", "title": "Patch and gates", "stage": "Closure", "est": 1, "deps": ["120.B", "120.C"], "status": "done"},
    {"id": "120.E", "title": "Stage 2", "stage": "Closure", "est": 1, "deps": ["120.D"], "status": "done"},
    {"id": "120.F", "title": "Stage 3 and 4", "stage": "Closure", "est": 1, "deps": ["120.E"], "status": "done"}
  ]
}
```

<!-- generated:plan-gantt-start -->
<!-- generated:plan-gantt-end -->
