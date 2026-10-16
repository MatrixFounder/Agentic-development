# TASK 125 — [LIGHT] `svg_geometry.py` stays a thin file, and its sections move to `svg_geometry_parts/`

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 125 |
| Slug | svg-geometry-package |
| Type | Refactoring, Light Mode (an auxiliary skill) |
| Source | TASK 124 D1, and the operator's answers of 2026-10-16 |
| Base revision | `15408c4f37e76d15db3a40ed7070b41927d4c607` |
| Archive name | `task-125-svg-geometry-package.md` |

**Request.** The operator split the three large scripts of the figure skill one per task (TASK 124
D1). This task takes `svg_geometry.py`. Before it started, the operator chose the layout, the
package's name and the cut (D1 to D3), and the light process (D4).

In this document `S/` stands for `.agent/skills/mermaid-authoring-guidelines/`.

<!-- contract:problem -->

## 1. Problem

`S/scripts/svg_geometry.py` is one module of 2,275 lines. It binds 120 top-level names: 73
functions, 2 classes and 45 assigned names. A header and 11 sections, each opened by a comment
line, divide it. The last section, the public API, ends with the debug command line `main`.

- 9 files import it: `render_check.py`, `S/evals/grade_figures.py`, `S/evals/render_corpus.py`,
  `S/evals/selftest_figure_evals.py` and 5 test modules. They read 6 private names, such as
  `_Svg` and `_extract_graph`.
- The grader is pinned by its SHA-256 (TC-ME-22), so it stays unedited.
- `test_printed_output.py` patches `analyze_svg`, `evaluate` and `passes` on the module, and the
  debug command line `main` calls them.
- `render_check.INSTRUMENT_FILES` and `render_corpus.INSTRUMENT_FILES` name the file. The two
  geometry fixtures record the SHA-256 of `render_check.INSTRUMENT_FILES`.

<!-- contract:rtm -->

## 2. Requirements

- **R1 — the package.** `S/scripts/svg_geometry_parts/` holds `__init__.py`, a docstring only,
  and these 12 modules, one per section, in this order:

  | Module | Section | Names |
  | :--- | :--- | :--- |
  | `base.py` | the header's names | 5 |
  | `tolerances.py` | instrument tolerances | 17 |
  | `transforms.py` | affine transforms | 6 |
  | `flattening.py` | path flattening | 6 |
  | `plane.py` | plane geometry | 20 |
  | `text_estimate.py` | text estimate | 2 |
  | `svg_model.py` | SVG model | 6 |
  | `graph.py` | graph figures | 11 |
  | `sequence.py` | sequence figures | 3 |
  | `gantt.py` | gantt figures | 1 |
  | `contrast.py` | text contrast | 27 |
  | `api.py` | public API, `main` aside | 15 |

  Each module holds a docstring that names its section, `from __future__ import annotations`, the
  imports that its code uses, and the lines of its section byte for byte, without the comment line
  that opens the section. A module imports only the standard library, `mermaid_model` and modules
  above it in the table, so the package holds no import cycle.
- **R2 — the thin file.** `S/scripts/svg_geometry.py` keeps its docstring, with one added paragraph
  that names the package. It keeps the imports and the `sys.path` line that the command line
  needs. One `from svg_geometry_parts.<module> import …` statement per module binds all 119 names
  of the package, private ones included, and `__all__` lists them with `main`. Then come `main`
  and the `__main__` block, byte for byte.
  Callers keep `import svg_geometry`, and `python3 svg_geometry.py FIG.svg` works as before.
- **R3 — the instruments.** `render_check.INSTRUMENT_FILES` and `render_corpus.INSTRUMENT_FILES`
  name the thin file and the 13 files of the package. The two geometry fixtures are rendered
  again with `render_check.py --fixture`. The comment of `render_check.py` that names
  `mermaid_model.py` names the package (TASK 124 §9).
- **R4 — a test module.** `S/scripts/tests/test_svg_geometry_package.py` checks the package's
  files and order, the imports of each module, exactly the names that its code reads, and each
  of the 120 names: bound on `svg_geometry` to the object of the module that defines it. It also
  checks that both `INSTRUMENT_FILES` name every file of the package.
- **R5 — records.** The row of `docs/ARCHITECTURE.md` §10.1 names the package. `CHANGELOG.md` and
  `CHANGELOG.ru.md` gain an entry v3.45.0.

<!-- contract:acceptance -->

## 3. Acceptance criteria

- **A1** — a move check: each module's body after its imports equals its section, and the thin
  file's `main` and `__main__` block equal the base lines.
- **A2** — the skill's suite, `tests/run_tests.py`, `tests/test_python_floor.py` and the eval
  selftest pass. One existing test changes: the guard of `test_printed_output.py` that keeps
  the geometry's code out of the lint names the package too (D6).
- **A3** — a behaviour check: `analyze_svg` and `evaluate` give the same output before and after
  for every committed SVG of the skill.
- **A4** — the steps of `.github/workflows/framework-gates.yml` pass.
- **A5** — one code review approves the change.

## 4. Decisions

- **D1**, 2026-10-16, operator: a thin `svg_geometry.py` beside a package of another name, over a
  package of the same name. The command line and the patches of the tests keep working, and this
  is the operator's usual form.
- **D2**, 2026-10-16, operator: the package is `svg_geometry_parts/`. TASK 126 takes
  `lint_mermaid_parts/`.
- **D3**, 2026-10-16, operator: one module per section, as the rule of `docs/ARCHITECTURE.md`
  §10.1 states.
- **D4**, 2026-10-16, operator: the light process. The Self-Improvement Mode of the system prompts
  names a split of a script as a case for `/light`. The limits of the `light-mode` skill on new
  files and on 30 minutes do not fit a split.
- **D5**, 2026-10-16, orchestrator: `main` stays in the thin file. It reads `analyze_svg`,
  `evaluate` and `passes` from the namespace that the tests patch.
- **D6**, 2026-10-16, orchestrator: the fix pass of the code review, which approved the change.
  - The guard of `test_printed_output.py` that keeps the geometry's code out of the lint names
    `svg_geometry_parts` too (MINOR-1).
  - TC-02 checks that each module imports exactly the names that its code reads, and that
    `__init__.py` holds a docstring only (MINOR-2).
  - The thin file's paragraph says where a name that the package looks up is replaced. Each
    module keeps two blank lines after its imports, and the two fixtures were rendered again
    (INFO-1, INFO-5).
  - `docs/reviews/framework-audit-103.md` pins its reference to the §7 of TASK 103 (INFO-2).
  - After the review, the operator saw Pylance mark the thin file in VS Code. Its imports showed
    as unresolved because the language server held a stale index: it still listed files that
    TASK 124 removed. Its re-exported names showed as not accessed, so `__all__` now lists them,
    and the fixtures were rendered once more.

  Not taken: one helper shared by the two package tests (INFO-6), which TASK 126 can raise.
- **D7**, 2026-10-16, operator: at the retro, "Поправить light-mode". The `light-mode` skill, now
  version 1.1, admits a behaviour-preserving split of a script of an auxiliary skill. Its own
  limits on new files and on 30 minutes contradicted the system prompts (D4). The gaps that
  `skill-enhancer`'s `analyze_gaps.py` reports for the skill predate this edit and stay.

## 5. Out of scope

- `S/scripts/lint_mermaid.py` (TASK 126), its comment that `svg_geometry.py` holds `_escaped`
  among it; `S/evals/grade_figures.py`, pinned by its SHA-256.
- The committed corpus renders keep their instrument hash, as in TASK 124 D8.
- Any work for Python 3.9. The floor test runs as it is.
