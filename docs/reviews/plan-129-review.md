# Plan Review: 129 — test-paths-and-dependency-advisories

- **Date:** 2026-10-26
- **Reviewer:** `plan-reviewer` (read-only subagent), `02-plan-implementation` step 3.
- **Status:** APPROVED. 0 BLOCKING, 2 MAJOR, 10 MINOR; none needs another round.
- **Reviewed:** `docs/PLAN.md` revision 1 and the four files `docs/tasks/task-129-0*.md`, at tree
  fingerprint `91d20eddb0b7`. The reviewer quoted the fingerprint; the orchestrator recomputed the
  same value at the return.
- **Evidence in the brief:**
  - `scan_register.py docs/PLAN.md docs/tasks/task-129-*.md --sections --terms docs/ARCHITECTURE.md`:
    `0 warn / 3 info`, every detector live;
  - `plan_gantt.py docs/PLAN.md --check docs/PLAN.md`: exit 0, no chart for 4 tasks;
  - `check_positional_refs.py --all`: `0 with a referent, 0 without (not examined), 6 pinned`;
  - the pinned coordinates against `2a7d11c`: 5 of 5 referents match;
  - the local gates at the Architecture boundary: `20 of 20 steps pass`;
  - the base evidence of the plan: the probe audits, the base renders of 52 figures, and a second
    render of them with 0 differences.
- **Not supplied:** the RTM-coverage validator. The reviewer checked by hand that each of R1–R7
  opens a `[Rn]` item.
- **Kept by:** the orchestrator, from the reviewer's hand-back. PLAN revision 2 answers each
  finding.

## Use Case Coverage

- UC-1 → 129.1, 129.2
- UC-2 → 129.1, 129.3, 129.4
- UC-3 → 129.1, 129.2

## Structure Verification

**Stub-First: PASS.** The change adds no interface to stub. Stage 1 writes the tests of the target
state, red at the base: TC-S1, TC-L1, the R3.6 pin and the red run of R1. Stage 2 changes the code
and the lockfiles. Pins and lockfiles are configuration, a single task by `planning-decision-tree`
§1. The TC-C7 extension follows a fix that landed in the Architecture phase; a mutation on a copy
stands in for its red run. No two tasks own the same file.

**Technical answers.**

- TC-S1 fails at the base for its stated reason: the recorder holds one call.
- Items 1 and 2 of TC-L1 fail at the base; items 3 and 4 are guards that pass. Item 4 holds for the
  three base lockfiles and the three probe lockfiles.
- `tests/test_tool_runner.py` has one class. `addCleanup` before `chdir` is the right order.
- The closing of WI-41 matches Registry B. RF-22 counts every key of `packages`, the root included:
  135, 201 and 205 at the base; 135, 201 and 204 in the probe.
- No other current file names pytest 9.0.2 or puppeteer 25.12.0. No `.AGENTS.md` is in scope.

## Comments

### BLOCKING

None.

### MAJOR

| ID | Finding | Answer of revision 2 |
| :--- | :--- | :--- |
| 1 | The CI half of A9 had no step; that run is the first of pytest 9.1.1 on Python 3.11 | PLAN, "Closing: the CI run" |
| 2 | The katex branch of R3.7 was carried only in part: A4, `KATEX`, the setup header, the v10 description, the changelog and RF-22 | PLAN, "The katex branch of R3.7", steps 1 to 6; task files 129-01, 129-03 and 129-04 |

### MINOR

| ID | Finding | Answer of revision 2 |
| :--- | :--- | :--- |
| 1 | Task 129.3 expected every gate to pass while TC-S1 could stay red | Task 129.3 depends on Task 129.2 |
| 2 | `npm audit` lacked `npm_config_cache`; TC-E4 lacked `-B` | both commands corrected |
| 3 | The base evidence had no path and no fallback; TC-E6 did not exclude `--ignore` | PLAN, "Base evidence" and "Fallback"; TC-E6 without `--ignore` |
| 4 | The failure paths missed a setup exit for another reason and a new advisory | PLAN, "Failure paths" |
| 5 | "The setup tries the cached 150 next" misled: 156 is not cached | Task 129.3, Notes |
| 6 | The base status of the probe figure was incomplete | PLAN, "Base evidence" |
| 7 | `_a_dead_pid()` ran inside the patches of TC-S1 | Task 129.1: the pid is taken first |
| 8 | Four referents sat on the line below their coordinate | each on the line of its coordinate |
| 9 | Register: two obligations in TC-C1; a rule and its reason joined by "so"; the goal of 129.2; the purpose of the base installs | TC-C1 and TC-C2; the note split; the goal as a list; the purpose stated |
| 10 | `tdd-strict` was not named; TC-L1 skips without `bash` or `node` | PLAN, Rules of the run; Task 129.1 states each expected failure and the skip |

## Final Decision

APPROVED. Proceed to Development with PLAN revision 2.
`{"review_file": "docs/reviews/plan-129-review.md", "has_critical_issues": false}`
