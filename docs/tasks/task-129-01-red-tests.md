# Task 129-01: The tests of the target state, red against the base

## Use Case Connection

- UC-1: A developer runs pytest from `tests/`
- UC-2: The operator installs the renderers
- UC-3: A test run on Windows sweeps stale scratch

<!-- contract:goal -->

## Task Goal

Write the tests of TASK R3.6, A4 and A7 so that each fails against the base for the reason it
states.

<!-- contract:changes -->

## Changes Description

`M/` stands for `.agent/skills/mermaid-authoring-guidelines/`.

### Changes in Existing Files

#### File: `tests/test_scratch_hygiene.py`

**Class `TestWindowsLiveness(unittest.TestCase)`** (new, after `TestSessionIsolation`):

- Add method `test_s1_windows_answers_alive_without_a_signal(self)` (TC-S1):
  1. `pid = _a_dead_pid()` runs first, outside the patches. With a dead pid, a call of `os.kill`
     that escapes the patch answers `False`.
  2. `kill = mock.Mock()` records each call.
  3. `mock.patch.object(scratch.os, "kill", kill)` and `mock.patch.object(scratch.os, "name", "nt")`
     enclose the call `scratch._pid_alive(pid)` and nothing else.
  4. The test asserts that the call returned `True` and that `kill.call_args_list` is empty.

**Why.** `pathlib` reads `os.name` when it makes a `Path`, so the patch of `os.name` encloses the
one call (task review N2).

#### File: `M/scripts/tests/test_setup_renderers.py`

- `PUPPETEER` names `25.16.0` for each tag (R3.6). The line at the base:
  `.agent/skills/mermaid-authoring-guidelines/scripts/tests/test_setup_renderers.py:39@2a7d11c` `PUPPETEER = {"v10": "25.12.0", "v11": "25.12.0", "v12": "25.12.0"}`
- The comment above `PUPPETEER` names the version of v11 and v12.
- Add the constants `DOMPURIFY = "3.4.17"` and `KATEX = "0.18.10"`, with a comment that names
  TASK 129 R3.1.
- **Class `TestLockfileOverrides(unittest.TestCase)`** (new, after `TestRecordedBrowsers`):
  - Add method `test_l1_each_lockfile_holds_the_overridden_versions(self)` (TC-L1). For each tag
    of `NOTATION["renderers"]["installs"]`, under `self.subTest(tag=tag)`:
    1. `overrides` of the manifest maps `dompurify` to `DOMPURIFY` and `katex` to `KATEX`. The
       test reads each with `.get`, so an absent key fails as an assertion;
    2. the `packages` entries `node_modules/dompurify`, `node_modules/katex` and
       `node_modules/puppeteer` of the lockfile hold `DOMPURIFY`, `KATEX` and `PUPPETEER[tag]`;
    3. `node_modules/mermaid` and `node_modules/@mermaid-js/mermaid-cli` hold the `mermaid` and the
       `cli` of `NOTATION["renderers"]["installs"][tag]`;
    4. no other entry of `packages` is a package `dompurify`, `katex` or `puppeteer`. The package
       of an entry is the name of an alias, else the path after the last `node_modules/`.

### The red run of R1

No file changes. From `tests/`, `python3 -B -m pytest -p no:cacheprovider -q` runs once. It stops
at the collection error. The same command with `--continue-on-collection-errors` runs past it.

<!-- contract:tests -->

## Test Cases

### Unit Tests

1. **TC-S1** — `os.name` set to `"nt"` and `os.kill` a recorder, around the call only →
   `_pid_alive` returns `True`, and the recorder holds no call; fails when R5.1 is removed.
   - Expected failure at the base: an `AssertionError` that shows the one recorded call
     `call(<pid>, 0)`.
2. **TC-L1** — the three manifests and lockfiles → each holds `dompurify` 3.4.17, `katex` 0.18.10,
   puppeteer 25.16.0, and the pinned mermaid and mermaid-cli. No second copy of the three exists.
   - Fails when an override is dropped, or when a lockfile is not written again.
   - Expected failure at the base: an `AssertionError` of item 1, `None` against `3.4.17`, in each
     of the three subtests.
3. **R3.6** — `test_v10_overrides_puppeteer_and_holds_no_extract_zip` with `PUPPETEER["v10"]` set
   to 25.16.0.
   - Expected failure at the base: an `AssertionError`, `25.12.0` against `25.16.0`.
4. **The red run of R1** — from `tests/`.
   - Expected at the base, without the flag: exit 2 at the collection error.
   - Expected failures at the base, with the flag:
     - the collection error of `tests/test_tool_runner.py`, a `ModuleNotFoundError` for `System`;
     - a `FileNotFoundError` in each of the four tests of
       `tests/test_tool_runner_security_contract.py`;
     - a `FileNotFoundError` in the test of `tests/test_schemas_stub.py`;
     - the failure of TC-S1.

### Regression Tests

- `PYTHONPATH=. python3 -B -m pytest -p no:cacheprovider tests/test_scratch_hygiene.py` → TC-S1
  fails, and every other test passes.
- `python3 -B -m pytest -p no:cacheprovider M/scripts/tests/test_setup_renderers.py` → TC-L1 and
  the v10 test fail, and every other test passes.

<!-- contract:acceptance -->

## Acceptance Criteria

- [ ] TC-S1, TC-L1 and the R3.6 pin exist.
- [ ] Each red test fails at the base with its expected failure.
- [ ] Every other test of the two modules passes.
- [ ] The review brief holds the output of each red run.
- [ ] The code review approves.

## Notes

- TC-S1 passes after Task 129.2. TC-L1 and the v10 test pass after Task 129.3.
- The lines of `PUPPETEER`, `DOMPURIFY` and `KATEX` are the only pins of the versions in the test.
- The new methods carry no return annotation, as no test method of the two modules does (code
  review of Task 129.1, M2).
- On the katex branch of R3.7 (PLAN, Failure paths), `KATEX` leaves the module, and TC-L1 asserts
  that no manifest overrides `katex`.
- TC-L1 reads JSON only. `setUpModule` of the module skips every test when `bash` or `node` is
  missing, TC-L1 included, as it skips `TestRecordedBrowsers`.
