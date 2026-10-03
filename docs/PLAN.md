# PLAN 109 — Python 3.11 is the floor and 3.14 the main version, stated once and enforced at the entry points

**TASK:** [docs/TASK.md](TASK.md) (revision 2) · **Covers:** R1–R7 · **Acceptance:** A1–A6

## Sequencing rule

Five clusters in order. Cluster A writes the pin and leaves it **failing** on the base tree, which
still states 3.9. Cluster B writes the statement, Cluster C the enforcement points, and Cluster D
the CI matrix and the last claim. Cluster D is the first point where the pin passes. Cluster E
closes WI-33, writes the release, runs every gate and takes the review. Review round 1 added the
items marked "(r1)".

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | The pin, failing | `tests/test_python_floor.py`, `tests/run_tests.py` | R6 |
| B | The statement | `README.md`, `README.ru.md`, `System/Docs/ORCHESTRATOR.md`, `docs/ARCHITECTURE.md` | R1 |
| C | The enforcement points | `install.sh`, `install.py`, `doctor.py`, five guarded scripts, the wrapper test | R2, R3 |
| D | CI and the last claim | `framework-gates.yml`, `plan_gantt.py` | R4, R5 |
| E | Closure, release, gates, review | WI-33, `docs/BACKLOG.md`, both changelogs, `skill-creator` `SKILL.md`, `AMENDMENTS.md`, the audit | R7, A1–A6 |

**Declared paths (A6, `framework-upgrade` §2.2).** Edited:

- `README.md`
- `README.ru.md`
- `System/Docs/ORCHESTRATOR.md`
- `docs/ARCHITECTURE.md`
- `install.sh`
- `System/scripts/install.py`
- `System/scripts/doctor.py`
- `.agent/skills/skill-creator/scripts/aggregate_benchmark.py`
- `.agent/skills/skill-creator/scripts/verify_pin.py`
- `.agent/skills/skill-creator/SKILL.md`
- `.agent/skills/mermaid-authoring-guidelines/evals/run_evals.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/render_corpus.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/selftest_figure_evals.py`
- `.agent/skills/mermaid-authoring-guidelines/evals/AMENDMENTS.md`
- `.agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py`
- `.github/workflows/framework-gates.yml`
- `tests/run_tests.py`
- `tests/installer/test_wrapper.sh`
- `docs/backlog/wi-33-skill-creator-scripts-target-python-3-14-not-3-9.md`
- `docs/BACKLOG.md`
- `CHANGELOG.md`
- `CHANGELOG.ru.md`

Created:

- `tests/test_python_floor.py`
- `docs/reviews/framework-audit-109.md`

The run's own `docs/TASK.md`, `docs/PLAN.md` and the TASK 108 archive pair are declared by §5.
`grade_figures.py` stays unchanged (TASK D6).

**Rollback point.** Base `cd9a45547f69460b7630e5966a54c9ec6b94a6de`, clean at the start of the
run. No copy is written. Fallback follows `framework-upgrade` §5 over the paths above.

## Cluster A — the pin, failing (R6)

- [x] A1. Write `tests/test_python_floor.py`, pure `unittest`, TC-01 to TC-07 (TASK R6.1–R6.3).
- [x] A2. Add `"test_python_floor"` to `CURATED_UNITTEST_MODULES` in `tests/run_tests.py`.
- [x] A3. Run the module on the base tree. Result: it fails.

## Cluster B — the statement (R1)

- [x] B1. `README.md` §3 "Supported Python": minimum 3.11, main version 3.14, CI tests both.
- [x] B2. `README.ru.md` §3: the same in Russian, line for line.
- [x] B3. `System/Docs/ORCHESTRATOR.md` Prerequisites: the pair and README §3 (r1, TASK D2).
- [x] B4. `docs/ARCHITECTURE.md` §9.2: the wrapper's checks (r1).

## Cluster C — the enforcement points (R2, R3)

- [x] C1. `install.sh`: check 3.11 after it finds `python3`, exit 2 naming 3.11 and 3.14; the PyYAML
      probe runs with `-P` (r1, TASK D8).
- [x] C2. `System/scripts/doctor.py`: `REQUIRED_PYTHON = (3, 11)`, `RECOMMENDED_PYTHON = (3, 14)`;
      both messages name both versions (r1).
- [x] C3. The guard, after the standard-library imports and before any local import or write,
      ending in `sys.exit(2)` (r1, TASK D7), in `aggregate_benchmark.py`, `verify_pin.py`,
      `run_evals.py`, `selftest_figure_evals.py`, `render_corpus.py` (r1) and `install.py` (r1).
      Their exit-code descriptions name the case. `grade_figures.py` stops through its import of
      `run_evals` (TASK D6).
- [x] C4. `tests/installer/test_wrapper.sh`: the stub recognises the probe with `-P` (r1).

## Cluster D — CI and the last claim (R4, R5)

- [x] D1. `framework-gates.yml`: the tooling matrix `["3.11", "3.14"]`, and the comment above it.
- [x] D2. `plan_gantt.py` docstring: the framework's minimum.
- [x] D3. Run the module. Result: it passes.

## Cluster E — closure, release, gates, review (R7, A1–A6)

- [x] E1. Run each A2 mutation of the TASK alone, then revert it; the audit records the outcomes.
- [x] E2. A3 under `/usr/bin/python3` 3.9.6: `install.sh --help`, the six scripts and the grader.
- [x] E3. `skill-creator` `SKILL.md` 2.2 → 2.3. `AMENDMENTS.md` notes the check in three eval
      scripts and that the grader is unchanged.
- [x] E4. WI-33 closes as `done`, with its resolution; its index line moves to `## Closed`.
- [x] E5. Both changelogs: v3.34.0 (TASK D10).
- [x] E6. Every step of `framework-gates.yml` locally; `scan_register.py` on the edited markdown;
      `check_positional_refs.py --targets-changed --fix` (`framework-upgrade` §4.5).
- [x] E7. Review: one code reviewer and one security auditor read the diff against the base.
- [ ] E8. `git status` against the declared paths. The operator commits.
