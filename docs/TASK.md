# TASK 126 — [LIGHT] `lint_mermaid.py` keeps its command line, and its sections move to `lint_mermaid_parts/`

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 126 |
| Slug | lint-mermaid-package |
| Type | Refactoring, Light Mode (an auxiliary skill) |
| Source | TASK 124 D1, TASK 125 D2, and the operator's answers of 2026-10-16 |
| Base revision | `ee278ca0b1340af8e53a09d6e9534a8fc1a42328` |
| Archive name | `task-126-lint-mermaid-package.md` |

**Request.** This task takes the last of the three large scripts of the figure skill (TASK 124 D1).
TASK 125 D2 named the package. Before the work started, the operator chose what the thin file
keeps, the cut and a shared module for the package tests (D1 to D3).

In this document `S/` stands for `.agent/skills/mermaid-authoring-guidelines/`.

<!-- contract:problem -->

## 1. Problem

`S/scripts/lint_mermaid.py` is one module of 2,404 lines. It binds 169 top-level names: 144
functions, 4 classes and 21 assigned names. A header and 16 sections, each opened by a comment
line, divide it: one section per family of rules, and the engine. The engine ends with the
command line.

- A committed allow rule and the CI gates run the file by its path, so the file stays.
- 5 files import it: `S/evals/grade_figures.py`, `S/evals/selftest_figure_evals.py` and 3 test
  modules. They read 13 private names. The grader is pinned by its SHA-256 (TC-ME-22).
- `test_printed_output.py` patches `run_probes`, `lint_text` and `_shown` on the module. `main`
  calls the first two, and `_say` calls `_shown`.
- `TestOnlySayPrints` of `test_printed_output.py` reads the lint's source. It pins that only `_say`
  prints and that the lint imports no geometry code.
- The rules register themselves into `RULES` as their module runs, in the order of the file.
- The helpers of `test_mermaid_model_package.py` and `test_svg_geometry_package.py` are copies of
  one another (TASK 125 D6, review INFO-6).

<!-- contract:rtm -->

## 2. Requirements

- **R1 — the package.** `S/scripts/lint_mermaid_parts/` holds `__init__.py`, a docstring only,
  and these 17 modules, one per section, in this order:

  | Module | Section | Names |
  | :--- | :--- | :--- |
  | `base.py` | the header's names | 16 |
  | `parse.py` | PARSE | 1 |
  | `syntax.py` | SYN | 6 |
  | `settings.py` | SET | 15 |
  | `ids.py` | ID | 3 |
  | `budget.py` | BUDGET | 7 |
  | `flowchart.py` | FLOW | 12 |
  | `state.py` | STATE | 3 |
  | `sequence.py` | SEQ | 3 |
  | `labels.py` | LABEL | 24 |
  | `classes.py` | CLASS | 18 |
  | `gantt.py` | GANTT | 7 |
  | `ascii_figures.py` | ASCII | 10 |
  | `doc.py` | DOC | 10 |
  | `model.py` | MODEL | 1 |
  | `negatives.py` | NEG | 11 |
  | `engine.py` | engine, up to the command line | 11 |

  Each module holds a docstring that names its section, `from __future__ import annotations`, the
  imports that its code reads, and the lines of its section byte for byte, without the comment
  line that opens it. Two texts change. The docstring of `_escaped` in `labels.py` says that
  `svg_geometry.py` binds its twin, which `svg_geometry_parts/api.py` holds. The comment of
  `RULES` in `base.py` says that the modules fill it in the order of the thin file's imports. A
  module imports only the standard library, `mermaid_model`, `planarity` and modules above it in
  the table.
- **R2 — the thin file.** `S/scripts/lint_mermaid.py` keeps its docstring, with one added paragraph
  that names the package. It keeps the imports and the `sys.path` line that its code needs. One
  `from lint_mermaid_parts.<module> import …` statement per module binds all 158 names of the
  package, private ones included, and `__all__` lists the 169 names. Then come the 11 names of the
  command line, from `_summary` to `main`, and the `__main__` block, byte for byte. The thin file
  imports the modules in the order of R1, so `RULES` holds the rules in the order of the base file.
- **R3 — tests.**
  - `S/scripts/tests/package_checks.py` holds the helpers that the package tests share.
    `test_mermaid_model_package.py` and `test_svg_geometry_package.py` use it, and the former
    gains the check that each module imports exactly the names that its code reads.
  - `S/scripts/tests/test_lint_mermaid_package.py` checks the package's files and order and the
    imports of each module. It checks that each of the 169 names is bound on `lint_mermaid` to the
    object of the module that defines it. It also checks that `RULES` lists the rules in the order
    of the modules and of their sources.
  - `TestOnlySayPrints` reads the thin file and every module of the package.
- **R4 — records.** `docs/ARCHITECTURE.md` §10.1 lists the thin file and the package. `CHANGELOG.md`
  and `CHANGELOG.ru.md` gain an entry v3.46.0.

<!-- contract:acceptance -->

## 3. Acceptance criteria

- **A1** — a move check: each module's body after its imports equals its section, but the two
  texts of R1, and the thin file's command line equals the base lines.
- **A2** — the skill's suite, `tests/run_tests.py`, `tests/test_python_floor.py` and the eval
  selftest pass.
- **A3** — a behaviour check: the base file and the thin file give the same output and exit. The
  runs are the text, `--json`, `--inventory` and `--inventory --json` runs over the Markdown files
  of the behaviour check of TASK 124, a run per `.mmd` fixture, and `--probe`.
- **A4** — the steps of `.github/workflows/framework-gates.yml` pass.
- **A5** — one code review approves the change.

## 4. Decisions

- **D1**, 2026-10-16, operator: the thin file keeps the command line, the tail of the engine
  section from `_summary` to `main`. The patches of `test_printed_output.py` keep working, and the
  file that commands run holds the command line. Rejected: `main` alone, which moves the patch of
  `_shown` to another module.
- **D2**, 2026-10-16, operator: one module per section, 17 modules, as the rule of
  `docs/ARCHITECTURE.md` §10.1 states. Rejected: MODEL merged into PARSE.
- **D3**, 2026-10-16, operator: the package tests share `package_checks.py`. Rejected: a third
  copy of the helpers.
- **D4**, 2026-10-16, orchestrator: the light process, as TASK 125 D4 and `light-mode` 1.1 state.
  `INSTRUMENT_FILES` names no file of the lint, so no fixture is rendered again.
- **D5**, 2026-10-16, orchestrator: the fix pass of the code review. The review found no
  blocking issue and confirmed the behaviour.
  - TC-04 compares `RULES` with every rule that the modules register, in order, the 35 rules that
    a plain `rule(...)(check)` call registers among them. Each rule lies in the module of its
    family (MAJOR-1).
  - TC-03 checks that the thin file imports each name from the module that defines it, in the
    order of R1 (MINOR-1).
  - The docstrings of `__init__.py` and `engine.py` say that a module imported alone sees only
    the rules of the modules imported so far (MINOR-2).
  - `reads()` of `package_checks.py` adds the names that the compiled code loads. A read of an
    imported name inside a comprehension at the top level then counts on Python 3.12 and later.
    Only the module attributes stay aside, where all dunder names did (MINOR-3).
  - The changelogs and §10.1 name the header module, and the changelogs name the two changed
    texts. The comment of `RULES` is the second text of R1 (MINOR-4, MINOR-5).

## 5. Out of scope

- `S/evals/grade_figures.py`, pinned by its SHA-256.
- Any work for Python 3.9. The floor test runs as it is.
