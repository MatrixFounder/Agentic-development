# TASK 109 — Python 3.11 is the floor and 3.14 the main version, stated once and enforced at the entry points

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 109 |
| Slug | python-floor-3-11-main-3-14 |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | [WI-33](../backlog/wi-33-skill-creator-scripts-target-python-3-14-not-3-9.md), operator direction of 2026-10-03 |
| Operator decision | 2026-10-03: minimum Python 3.11, main Python 3.14; CI tests both |
| Base revision | `cd9a45547f69460b7630e5966a54c9ec6b94a6de` |
| Closes | WI-33 |
| Archive name | `task-109-python-floor-3-11-main-3-14.md` |
| Revision | 3: review rounds 1 and 2 applied (`docs/reviews/framework-audit-109.md`) |

<!-- contract:problem -->

## 1. Problem

The framework states Python 3.9 as its minimum. CI does not test 3.9, and part of the code does not
run on it.

**Measured on 2026-10-03.**

- Five `skill-creator` scripts evaluate `X | None` annotations at import, and Python 3.9 stops
  them with `TypeError`: `aggregate_benchmark.py`, `improve_description.py`, `run_eval.py`,
  `run_loop.py` and `eval-viewer/generate_review.py`. `verify_pin.py` imports
  `aggregate_benchmark` and stops the same way under `/usr/bin/python3` 3.9.6.
- Under 3.9.6 the figure-eval grader writes `report.json`, skips `benchmark.json` with a note
  about a `TypeError`, and exits 0. The note does not name the interpreter version. Its selftest
  skips one row and fails another.
- CI tests 3.11 and 3.13. No version below 3.11 is tested, and neither is 3.14, the version the
  maintainer runs.

**Six places carry the 3.9 claim.**

| Place | Text today |
| :--- | :--- |
| `README.md` §3 | "Minimum: Python `3.9+` (legacy compatibility)" |
| `README.ru.md` §3 | the same, in Russian |
| `System/Docs/ORCHESTRATOR.md` | "Python 3.9+" under Prerequisites |
| `install.sh` | "Install Python >= 3.9 and retry." |
| `System/scripts/doctor.py` | `REQUIRED_PYTHON = (3, 9)`: under 3.9.6 it reports "meets minimum" |
| `mermaid-authoring-guidelines/scripts/plan_gantt.py` | "Python 3.9 or newer" in its docstring |

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The README pair states the supported versions, and the documents that name them agree | Y | R1.1–R1.4 | A1, A2 |
| R2 | The installer and the preflight enforce the floor | Y | R2.1–R2.6 | A1, A2, A3 |
| R3 | The benchmark stops below the floor before it writes anything | Y | R3.1–R3.3 | A1, A2, A3 |
| R4 | CI tests the floor and the main version, and runs nothing below the floor | Y | R4.1–R4.3 | A1, A2 |
| R5 | No living file claims support for Python 3.10 or older | Y | R5.1–R5.3 | A1, A2 |
| R6 | One unittest module pins R1–R5 and runs in the curated suite | Y | R6.1–R6.3 | A1, A2, A4 |
| R7 | WI-33 is closed, and the release is recorded | Y | R7.1–R7.3 | A5, A6 |

### 2.1 Sub-features

- **R1.1** `README.md` §3 "Supported Python": minimum 3.11, main version 3.14, and CI tests both.
- **R1.2** `README.ru.md` §3 states the same in Russian.
- **R1.3** `System/Docs/ORCHESTRATOR.md` Prerequisites states the same pair and names README §3 as
  the policy (D2).
- **R1.4** `docs/ARCHITECTURE.md` §9.2 lists the checks the wrapper makes.
- **R2.1** `install.sh` checks `python3` against 3.11 after it finds it, and exits 2 below it.
- **R2.2** Its messages name 3.11 as the minimum and 3.14 as the main version.
- **R2.3** `System/scripts/doctor.py`: `REQUIRED_PYTHON = (3, 11)`, `RECOMMENDED_PYTHON = (3, 14)`.
  Its FAIL and WARN messages name both versions.
- **R2.4** `System/scripts/install.py`, the second entry point, exits 2 below 3.11.
- **R2.5** The PyYAML probe of `install.sh` runs with `-P`, so it imports no module from the target
  project (D8).
- **R2.6** The stub of `tests/installer/test_wrapper.sh` recognises the probe with `-P`.
- **R3.1** `skill-creator/scripts/aggregate_benchmark.py` and `verify_pin.py` exit 2 below 3.11.
- **R3.2** `mermaid-authoring-guidelines/evals/run_evals.py`, `render_corpus.py` and
  `selftest_figure_evals.py` exit 2 below 3.11, before their local imports and before any write.
  `grade_figures.py` stops through the guard of the `run_evals` it imports at its top (D6).
- **R3.3** Each message names the script that was run, the minimum, the main version and the
  running version. Exit 2 is the code each script documents for an environment that cannot run
  it (D7).
- **R4.1** The tooling-tests matrix of `framework-gates.yml` holds `"3.11"` and `"3.14"`.
- **R4.2** The comment above the matrix names the two versions and why.
- **R4.3** No CI job runs below 3.11. The single-version jobs stay on 3.11.
- **R5.1** The docstring of `plan_gantt.py` names the framework's minimum.
- **R5.2** R1, R2 and R5.1 remove the six 3.9 claims of §1.
- **R5.3** A check fails when a living document or script claims 3.10 or older again.
- **R6.1** `tests/test_python_floor.py`, TC-01 and TC-02: README §3 is the source. The Russian
  README, `ORCHESTRATOR.md`, `doctor.py`, `install.sh`, the six guards and the CI jobs agree
  with it.
- **R6.2** TC-03 to TC-05 and TC-07: every guard is reachable on 3.9, as far as syntax and
  imported names show. Each guarded script, the grader and the installer stop under a faked 3.9.6
  with exit 2, both versions named and nothing written; under `python -m` a guard names its own
  module. The installer reads no module from the target project.
- **R6.3** TC-06 scans for a claim. The module is listed in `CURATED_UNITTEST_MODULES` of
  `tests/run_tests.py`.
- **R7.1** WI-33 closes as `done`, and its index line moves to `## Closed`.
- **R7.2** Both changelogs carry v3.34.0 (D10). `skill-creator` goes from 2.2 to 2.3.
- **R7.3** `mermaid-authoring-guidelines/evals/AMENDMENTS.md` records the check in three eval
  scripts and that the grader is unchanged.

<!-- contract:use-cases -->

## 3. Use Cases

| UC | Actor | Precondition | Main scenario | Alternative | Postcondition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-1 install | user | `python3` is 3.9 | `bash install.sh install` stops with exit 2 and names 3.11 and 3.14 | `python3 System/scripts/install.py` directly: exit 2, the same names | nothing written into the target |
| UC-2 selftest | maintainer | `/usr/bin/python3` is 3.9.6 | `selftest_figure_evals.py` stops with exit 2 and names 3.11 | 3.11 or newer: all 223 rows run | no row ran, so none is skipped |
| UC-3 grading | maintainer | an old interpreter | `grade_figures.py` stops at its import of `run_evals` with exit 2 and names itself | 3.11 or newer: grading as before | the campaign directory is unchanged |
| UC-4 CI | pull request | a change to the framework | the tooling tests run on 3.11 and on 3.14 | one version fails: the other still reports | both results visible |

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `python3 -m pytest tests/test_python_floor.py -q` passes |
| A2 | Each mutation below fails that module, and reverting it passes |
| A3 | Under `/usr/bin/python3` 3.9.6, `install.sh --help` exits 2; the six guarded scripts and the grader exit 2, naming 3.11 |
| A4 | `PYTHONPATH=. python3 tests/run_tests.py` runs the new module and reports OK |
| A5 | Every step of `framework-gates.yml` passes locally; the advisory archive step reports no new error |
| A6 | `scan_register.py` reports no new `warn` on the edited markdown, and `git status` lists only declared paths |

**A2 mutations.** Each is applied alone and reverted:

1. README §3 names another minimum, or `ORCHESTRATOR.md` another pair;
2. `doctor.py` requires another version, or its FAIL message drops the main version;
3. `install.sh` checks another version, loses its check, or runs the PyYAML probe without `-P`;
4. one guard checks another version, exits 1, or is deleted, in a script or in `install.py`;
5. one guard moves below a statement or names `__main__.py`; a 3.11 module or name (`tomllib`,
   `typing.Self`, `datetime.UTC`, `enum.StrEnum`) or 3.10 syntax enters a guarded file or a module
   the grader imports first;
6. the CI matrix loses `"3.14"` or gains `"3.10"`, or a single-version job runs 3.10, quoted or not;
7. a living document claims 3.9 or 3.10: as "3.9+", in lower case with "or higher", as "or
   greater", across a line break, in Russian, in a top-level `docs/` file or in `.claude/agents`;
8. the grader stops importing `run_evals` at its top.

<!-- contract:open-questions -->

## 5. Open Questions

**None open.** The operator chose the minimum and the main version on 2026-10-03.

## 6. Decisions

**D1, 2026-10-03, operator: minimum 3.11, main version 3.14, and CI tests both.** Rejected: 3.14
only, because projects on 3.11–3.13 would have to upgrade.

**D2, 2026-10-03, orchestrator: the README pair is the one statement.** `ORCHESTRATOR.md`
repeats the pair and names README §3 as the policy. In an installed project its relative link
would resolve to the project's own README, so it states the numbers itself. The enforcement
points carry the minimum in code. R6.1 holds all of them equal to README §3.

**D3, 2026-10-03, orchestrator: guards at the entry points only.** They cover the installer, the
preflight and the benchmark scripts of `skill-creator` and of the figure evals. There a run on an
old interpreter wrote partial output or writes into a campaign. Rejected: a guard in every script.
It touches every skill for a version range nothing tests, while the entry points are where a user
starts. The other eval scripts of `artifact-formalizer` and `run-feedback` and the description
loop of `skill-creator` stay without one; README §3 names only the guarded group.

**D4, 2026-10-03, orchestrator: the matrix replaces 3.13 with 3.14.** The floor and the main
version bracket the 3.11/3.12 behaviour boundary named in the matrix comment. Rejected: three
versions, which adds a CI run without a case only 3.13 would catch.

**D5, 2026-10-03, orchestrator: `mermaid-authoring-guidelines` stays at 1.0.** Its lint, render
check and plan chart do not change. The eval guards and the docstring do not change what the skill
does for a user.

**D6, 2026-10-03, orchestrator: the grader carries no guard of its own.** Every committed
campaign report records the sha256 of `grade_figures.py`. The eval selftest re-derives each report
from its corpus (TC-ME-22), and a guard in the grader turned the stored report stale in this run.
The grader imports `run_evals` at its top, before it reads an argument or writes a file, so that
guard stops it. The guard names the script that was run. Rejected: regrading the campaign corpus
for a version check.

**D7, 2026-10-03, orchestrator (review round 1): the guards exit 2.** `run_evals.py`,
`selftest_figure_evals.py` and `render_corpus.py` document 2 as an instrument or environment
error. `verify_pin.py` documents 1 as "drift detected", and `install.sh` uses 2 for its
environment checks. Exit 1 would read as a verdict. Rejected: exit 1 with a new row in each table,
because the registered `evals/README.md` table is frozen.

**D8, 2026-10-03, orchestrator (review round 1): the PyYAML probe runs with `-P`.** `python3 -c`
puts the current directory, the target project, first on the import path. A `yaml.py` there ran
during the probe, and on 3.14 a `linecache.py` did too. `-P` exists from 3.11, which the check
above it now guarantees. `-P` keeps the entries a user puts on `PYTHONPATH`: with
`PYTHONPATH=.` the target project's modules are importable by that user's own setting. Rejected:
clearing `PYTHONPATH` in the wrapper, which would break a PyYAML supplied that way.

**D9, 2026-10-03, orchestrator (review round 1): below 3.11 every installer subcommand stops,
`uninstall` included.** A user on 3.9 or 3.10 runs `uninstall` with Python 3.11 or newer. The
Migration note of the changelogs says so. Rejected: an exemption per subcommand in two entry
points, for a version range the framework no longer supports.

**D10, 2026-10-03, orchestrator (review round 1): the release is v3.34.0.** A raised minimum is a
changed requirement for a user on 3.9 or 3.10, not a patch.

## 7. Out of scope

- A guard in every framework script (D3).
- The `skill-creator` mirror in Universal-skills. It is synced after the operator's commit
  (`framework-upgrade` §3.1).
- Consumer projects. Their next `install.sh update` brings the change.
- `developer-guidelines/references/languages/python.md`, which says since which version a Python
  feature exists. It states a fact about Python, not a version the framework supports.
- A feature that fails on 3.9 or 3.10 only when it runs, such as `dataclass(slots=True)` in a module
  the grader imports first. TC-03 sees syntax and imported names, not runtime behaviour.
- The `except (ImportError, SyntaxError, TypeError)` branch at the benchmark import of
  `grade_figures.py`. It no longer sees an old interpreter, and D6 keeps the grader unchanged; the
  next grader revision removes it.
