# Code Review: Task 129.1 — the tests of the target state, red against the base

- **Date:** 2026-10-26
- **Reviewer:** `code-reviewer` (subagent), `03-develop-single-task` step 4.
- **Status:** APPROVED, MERGE. 0 BLOCKING, 0 MAJOR, 6 MINOR.
- **Reviewed:** the diff of `tests/test_scratch_hygiene.py` and
  `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_setup_renderers.py`, at tree
  fingerprint `a3fab8e7cd61`. The reviewer quoted it; the orchestrator recomputed the same value at
  the return. The reviewer planted in copies outside the repository and removed them.
- **Kept by:** the orchestrator, from the reviewer's hand-back.

## Assessment

The diff matches the task file. Each red test fails at the base with its expected failure:

- TC-S1: `AssertionError: [call(<pid>, 0)] != []`;
- the v10 test: `AssertionError: '25.12.0' != '25.16.0'`;
- TC-L1: `AssertionError: None != '3.4.17'` in each subtest.

TC-L1 and the v10 test pass against the probe lockfiles of the Architecture phase. TC-S1 passes
against a copy of `tests/_scratch.py` with the change of Task 129.2.

## Comments

### BLOCKING

None.

### MAJOR

None.

### MINOR

| ID | Pillar | Finding | Resolution |
| :--- | :--- | :--- | :--- |
| M1 | Compliance | The named R1 command stops at the collection error; the predicted list needs `--continue-on-collection-errors` | the task file names both commands; TASK revision 3 corrects §1 and §8, which named the plain command |
| M2 | Compliance | The task file named `-> None`, which no test method of the two modules carries | kept as the modules write it; the task file follows |
| M3 | Quality | The dead pid of TC-S1 matters and had no comment | a comment states it |
| M4 | Quality | The docstring of TC-L1 named the overrides only | the docstring names the pinned versions too |
| M5 | Testing | TC-L1 looped over a fixed tuple, not the inventory | it loops over `NOTATION["renderers"]["installs"]` |
| M6 | Testing | Item 4 matched by key suffix: `@types/katex` read as a copy, an alias did not | `_package_name` reads the name of an alias, else the path after the last `node_modules/` |

**Measured after the fixes:**

- the two modules fail as before: `1 failed, 15 passed` and `4 failed, 32 passed`;
- the probe lockfiles pass TC-L1 and the v10 test;
- plantings on copies of the probe lockfiles:
  - an entry `node_modules/@types/katex` passes;
  - an alias `node_modules/dompurify-legacy` named `dompurify` fails, and the message names it;
  - a nested `node_modules/x/node_modules/dompurify` fails, and the message names it.

**Before the task:** `tests/test_scratch_hygiene.py:8@2a7d11c` says that every test redirects the
module's paths, which `TestRunnerDoesNotSweep` already contradicted.

## Verified (clean pass)

- **Requirements checked:** R3.6, A4 items 1 to 4, A7, and the expected failures of the task file.
- **Edge cases considered:**
  - TC-S1: the pid taken outside the patches; plantings that return `False`, check after the call,
    bind at import, or read `sys.platform` all fail;
  - TC-L1: an absent key fails as an assertion; each subtest isolates its tag; 14 plantings each
    fail at the intended assertion.
- **Tests observed:** the skill's CI invocation gives `4 failed, 742 passed, 1 skipped`, the four
  planned failures; the R1 runs give exit 2, and `6 failed, 719 passed, 1 error` with the flag.

`{"review_status": "APPROVED", "has_critical_issues": false, "e2e_tests_pass": false, "stubs_replaced": false}`
— the suites are red by design until Task 129.2 and Task 129.3.
