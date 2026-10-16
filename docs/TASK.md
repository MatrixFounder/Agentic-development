# TASK 124 — `mermaid_model.py` becomes the package `mermaid_model/`, one module per section

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 124 |
| Slug | mermaid-model-package |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | the operator's requests of 2026-10-15: during TASK 123, at its retro, and the scope answer of TASK 124 |
| Base revision | `44520ba6197264c744b105ecf428b93496ba428f` |
| Closes | none: no backlog record holds this item |
| Archive name | `task-124-mermaid-model-package.md` |
| Revision | 9 |

**Request.** During TASK 123 the operator wrote: "если финальные скрипты будут огромными, то
по-правильному их надо отрефакторить и разбить на модули для дальнейшего развития и поддержки".
They named `lint_mermaid.py` and `svg_geometry.py`, and added "mermaid_model.py тоже надо". At the
retro of TASK 123 they chose "TASK 124 следом". Asked how to cut the work, they answered "По одному
модулю". TASK 124 splits `mermaid_model.py` and sets the layout that TASK 125 (`svg_geometry.py`)
and TASK 126 (`lint_mermaid.py`) follow.

**Revision 2** applies M1 to M5, m1 to m16 and N2, N3, N4, N6 and N7 of Mode A round 1.
**Revision 3** applies m17 to m21 and N10 to N18 of round 2, which passed, with no further round,
on the precedent of TASK 122 and TASK 123. **Revision 4** adds the operator's requirement that the
skill stays self-contained: D12, R1.8, TC-07 and the last point of R5.2. It also adds a lint run of
a `.mmd` file to R6.7 (Mode B round 1, N7). **Revision 5** records fix round 1 of stage 2 (D13),
**revision 6** fix round 2 (D14), **revision 7** fix round 3 (D15), and **revision 8** fix round 4
(D16). **Revision 9** records the close of stage 2 at round 5 (D17) and the operator's answer on
the layout (D18).

In this document `S/` stands for `.agent/skills/mermaid-authoring-guidelines/`. A coordinate into
a file that this task moves or edits carries the pin `@44520ba`, the base revision. A top-level
name of a module is a name that a top-level `def`, `class` or assignment binds, each name of a
tuple target included and imported names excluded.

<!-- contract:problem -->

## 1. Problem

`S/scripts/mermaid_model.py` is one module of 3,708 lines. It defines 230 top-level names: 97
functions, 33 classes and 100 assigned names. Comment lines divide it into 16 sections, from the
module header to the entry points (§8).

- To edit one diagram kind's parser, an agent opens a file that holds 15 other sections.
- 16 files import it as `mermaid_model`: 8 scripts and 8 test modules. They read 36 of its names,
  9 of them private. The grader reads 4 names through `getattr`. A missing private one stops it
  with exit 2, and a missing `NEGATIVE_MARKER` changes its result without an error (§8).
- A committed allow rule runs `S/scripts/lint_mermaid.py`, and two run `S/scripts/plan_gantt.py`.
  Both import the module, so `framework-upgrade` §3 step 4 stages each edit of it.

Seven couplings constrain a split:
1. Tests assign three names on the module object: `NEGATIVE_ROOTS`, `negative_markers` and
   `_parse_er`. After a split, an assignment takes effect only when it lands on the module whose
   code looks the name up. `test_markers_are_read_once_per_fence` then counts no call and passes.
2. `SKILL_DIR` is `Path(__file__).resolve().parent.parent`. One directory deeper, it names
   `S/scripts/`.
3. `tests/test_python_floor.py` finds a local module only as a `<name>.py` file. A package fails
   TC-03, and TC-04 does not stub it. `tests/run_tests.py` runs that module, so its edit is staged.
4. `render_corpus.INSTRUMENT_FILES` names `scripts/mermaid_model.py`, and `instrument_sha256`
   records `absent` for a file that does not exist.
5. The grader records the SHA-256 of `grade_figures.py` and of `fidelity.py` in every report, and
   the eval selftest compares each committed report with a new one (TC-ME-22).
6. TC-12 of `tests/test_mermaid_wiring.py` requires each path of the `docs/ARCHITECTURE.md` §10.1
   table to exist. The row of the module changes with the package, at stage 3.
7. `test_every_anchor_a_script_reads_is_registered` of `tests/test_mermaid_wiring.py` reads anchor
   literals from `S/scripts/*.py` and `S/evals/*.py`, and from no package's modules. The base
   module holds no anchor literal.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The package `S/scripts/mermaid_model/` | yes | one module per section; verbatim text; full re-export; no cycle; old file removed; self-contained | A1, A2, A3 |
| R2 | Callers and tests | yes | no import line of a caller changes; patches land where names are looked up; the floor test reads packages | A3, A4 |
| R3 | The instruments of a corpus render | yes | the package files in `INSTRUMENT_FILES`; a test ties the list to the package; the corpus renders kept | A3, A8 |
| R4 | A test module of the package | yes | modules and order; import graph; names; `SKILL_DIR`; the instrument list | A3 |
| R5 | The layout rule and the records | yes | `docs/ARCHITECTURE.md` §10; the changelogs; `System/Docs` unedited; migration | A7, A8 |
| R6 | Staging, evidence and records | yes | stage-1 copies; the stage-3 patch; the move check; the behaviour check; the gates and the check; the settings | A2, A5, A6, A9, A10 |

## 3. Requirements

### R1 — the package `S/scripts/mermaid_model/`

- **R1.1** `S/scripts/mermaid_model/` holds `__init__.py` and these 15 modules, one per section of
  the base file, in this order:

  | Module | Section of the base file | Lines at the base |
  | :--- | :--- | :--- |
  | `base.py` | the header's names: paths, constants, `negative_allowed`, `load_notation` | 44–93 |
  | `document.py` | document level | 94–724 |
  | `figure.py` | figure level | 725–989 |
  | `hazards.py` | hazard codes | 990–1069 |
  | `labels.py` | labels | 1070–1148 |
  | `kinds.py` | kinds | 1149–1197 |
  | `settings.py` | settings | 1198–1524 |
  | `preprocessing.py` | preprocessing | 1525–1667 |
  | `flowchart.py` | flowchart | 1668–2318 |
  | `sequence.py` | sequence | 2319–2494 |
  | `state.py` | state | 2495–2707 |
  | `gantt.py` | gantt | 2708–2782 |
  | `er.py` | er | 2783–2875 |
  | `other_kinds.py` | other kinds | 2876–3174 |
  | `ascii_figures.py` | ascii | 3175–3624 |

  `__init__.py` holds the entry points, lines 3625–3708. Base line 1, the shebang, goes to no
  module. The docstring of lines 2–28 goes to `__init__.py` (R1.3), and each module writes its own
  imports in place of lines 29–43.
- **R1.2** Each of the 15 modules holds, in this order:
  1. a module docstring of one paragraph that names its section;
  2. `from __future__ import annotations`;
  3. the imports that its code uses, annotations included: standard-library names, and names of
     modules above it in R1.1;
  4. the lines of its section, byte for byte, without the comment line that opens the section.

  One line differs from the base: `base.py` sets `SKILL_DIR = Path(__file__).resolve().parents[2]`.
- **R1.3** `__init__.py` holds, in this order:
  1. the docstring of base lines 2–28, with one added paragraph that names the 15 modules;
  2. `from __future__ import annotations` and the standard-library imports of the entry points;
  3. one `from .<module> import …` statement per module of R1.1, in that order. Together they bind
     every top-level name of the 15 modules;
  4. the lines of the entry-points section, byte for byte, without its opening comment line.
- **R1.4** A module of R1.1 imports only from modules above it in R1.1. No module of the package
  imports `__init__.py`.
- **R1.5** Each of the 230 top-level names of the base module is bound on `mermaid_model`, to the
  object of the module that defines it. R6.5 shows that each definition keeps its text.
- **R1.6** `S/scripts/mermaid_model.py` is removed.
- **R1.7** Every module of the package parses under the Python 3.9 grammar. At import time it
  imports only modules of the package and modules that `STDLIB_3_9` of `tests/test_python_floor.py`
  lists. From a standard-library module it imports only the names that `FROM_3_9` lists.
- **R1.8** The skill stays self-contained. Every file that the change adds to the skill lies under
  `S/`, and the package lies in `S/scripts/`, where `mermaid_model.py` was. Each script of
  `S/scripts/` and each module of the package imports only standard-library modules and modules of
  `S/scripts/`. No file of the skill moves out of `S/`.

### R2 — callers and tests

- **R2.1** No import statement of a caller changes. The 8 scripts and 8 test modules of §8 import
  `mermaid_model` as at the base.
- **R2.2** A test that assigns a name of the package reads and assigns it through one expression,
  which names the module that looks the name up:
  - `NEGATIVE_ROOTS` through `sys.modules[mm.negative_allowed.__module__]`, at the 11 lines of §8;
  - `negative_markers` through `sys.modules[mm.Fence.__module__]`, at the 3 lines of §8.

  The 6 lines of §8 that read and assign `_parse_er` stay as they are (D5).

  **Why.** At the base both expressions name `mermaid_model` itself, so the edited tests pass
  before stage 3 and after it.
- **R2.3** `test_markers_are_read_once_per_fence` also asserts that the counting function ran at
  least once. Fails when: the assignment lands on a module that the code does not read.
- **R2.4** In `tests/test_python_floor.py`, `_grader_local_imports()` and TC-03 resolve a local
  name as Python does: first `<dir>/<name>/__init__.py`, then `<dir>/<name>.py`, for each
  directory of `GRADER_PATH`. TC-03 parses every `*.py` module of a package that it reaches, under
  the 3.9 grammar. It walks in turn the imports at the module's top level and in its `try` and
  `if` blocks. An entry counts when an import statement can spell its name and each directory on
  its way. TC-03 fails on these static forms, by which Python would run code that it never parsed
  (D14 to D16):
  - a package directory that is a symbolic link, or a link in the package;
  - a compiled or extension module, or a Windows `*.pyw` source, in the package or by a local
    name. A cache in `__pycache__/` is no module;
  - a module that spells `__path__` or `submodule_search_locations`: as a name, an attribute, a
    keyword, an imported name or a string;
  - a local module named after a standard-library module that the walked code or a guarded
    script imports, in `GRADER_PATH` or beside that script.

  It also fails on a `*.py` entry that is no regular file, which it does not open. §9 states what
  lies out of its reach (D17). The edit is staged (R6.1).
- **R2.5** The docstring of `S/scripts/tests/test_lint_mermaid.py` names the package in place of
  `mermaid_model.py`.

### R3 — the instruments of a corpus render

- **R3.1** `INSTRUMENT_FILES` of `S/evals/render_corpus.py` takes the text of this fence. The other
  lines of the file stay as they are.

```text
INSTRUMENT_FILES = ("scripts/render_check.py", "scripts/svg_geometry.py",
                    "scripts/measure_text.mjs", "scripts/mermaid_model/__init__.py",
                    "scripts/mermaid_model/base.py", "scripts/mermaid_model/document.py",
                    "scripts/mermaid_model/figure.py", "scripts/mermaid_model/hazards.py",
                    "scripts/mermaid_model/labels.py", "scripts/mermaid_model/kinds.py",
                    "scripts/mermaid_model/settings.py", "scripts/mermaid_model/preprocessing.py",
                    "scripts/mermaid_model/flowchart.py", "scripts/mermaid_model/sequence.py",
                    "scripts/mermaid_model/state.py", "scripts/mermaid_model/gantt.py",
                    "scripts/mermaid_model/er.py", "scripts/mermaid_model/other_kinds.py",
                    "scripts/mermaid_model/ascii_figures.py", "assets/notation.json")
```

- **R3.2** The 66 committed `geometry.json` files of `S/evals/corpus/` stay as they are. Their
  `instrument_sha256` then differs from the current one, so the next corpus run renders their
  figures again (D8).

### R4 — a test module of the package

- **R4.1** `S/scripts/tests/test_mermaid_model_package.py` holds these tests:
  - TC-01 — the files of the package → `__init__.py` and the 15 modules of R1.1; fails when a
    module is added, removed or renamed without an edit of the test;
  - TC-02 — the relative imports of each module → only modules above it in R1.1, and none of
    `__init__`; fails when a module imports one below it;
  - TC-03 — the 230 names of §8, listed by module in the test → each defined in its module and
    bound on `mermaid_model` to the same object. Fails when a name moves or is dropped;
  - TC-04 — `SKILL_DIR` → the skill directory, and `NOTATION_PATH` → an existing file; fails when
    `SKILL_DIR` keeps `.parent.parent`;
  - TC-05 — `INSTRUMENT_FILES`, read from the source of `render_corpus.py` by AST → each of the 16
    files of TC-01 once, and no `scripts/mermaid_model.py`. Fails when a module of the package is
    missing from the list;
  - TC-06 — `NEGATIVE_ROOTS` assigned through the expression of R2.2 → `negative_allowed` reads
    it; fails when that expression names a module that `negative_allowed` does not read;
  - TC-07 — each absolute import of each script of `S/scripts/` and of each module of the package,
    read by AST → a module of `sys.stdlib_module_names` or a module of `S/scripts/` (R1.8). Fails
    when a module imports a name from outside the skill and the standard library.
- **R4.2** Against the base layout, TC-01, TC-02, TC-03 and TC-05 fail or raise an error, and
  TC-04, TC-06 and TC-07 pass. The audit record holds that run. A mutation in the throwaway
  worktree of R6.6 makes each of TC-04, TC-06 and TC-07 fail, and the audit record holds those
  runs.
- **R4.3** The test module imports no module of `S/evals/` and runs on Python 3.11 and 3.14, the
  versions of the CI matrix. This machine has no Python 3.11, so CI checks 3.11 after the commit.

### R5 — the layout rule and the records

- **R5.1** In `docs/ARCHITECTURE.md` §10.1, the row of `scripts/mermaid_model.py` takes the text of
  this fence, at stage 3 (D11). §10.3 names `mermaid_model` where it names `mermaid_model.py`.

```text
| `scripts/mermaid_model/` | library | fence extraction; parsers for flowchart, sequence, state, gantt, ASCII; one module per section | unit tests |
```

- **R5.2** `docs/ARCHITECTURE.md` §10.1 gains, below its table, the layout rule that TASK 125 and
  TASK 126 follow:
  - a script of `S/scripts/` that holds several sections becomes a package, one module per section;
  - a script that a command runs by its path keeps that file, and its package takes another name.
    A command runs a script by its path when an allow rule, a document of the framework or a test
    names the file in a command line. A package and a module of one name in one directory import
    as the package;
  - the name that callers import binds every top-level name of the script, and callers keep their
    imports. That name is the package's `__init__.py`, or the file that the script keeps;
  - a module imports only from modules above it, so the package has no import cycle;
  - a test reads and assigns a name on the module whose code looks it up;
  - a test that reads a property of the scripts from `S/scripts/*.py`, such as an anchor literal,
    reads the package's modules too once a package holds that property;
  - the skill stays self-contained: the package lies in `S/scripts/`, and its modules import only
    the standard library and modules of `S/scripts/` (D12).
- **R5.3** `CHANGELOG.md` and `CHANGELOG.ru.md` gain an entry v3.44.0 under **Changed**.
- **R5.4** `System/Docs/` names no file that this task moves or edits, and stays unedited.
- **R5.5** Migration. No session state, command, setting or notation value changes. An install by
  the default per-item symlinks reads the package at once. The installer copies a file only where
  the target lacks it, and keeps an existing framework copy whole, with `--force` too. A copy
  install made before this task therefore runs the old `mermaid_model.py` until that copy is
  removed and made again.

### R6 — staging, evidence and records

- **R6.1** Stage 1 writes these copies under new names. Nothing imports them, and no test runner
  collects them:
  - the 16 files of R1 under `S/scripts/staged_mermaid_model/`;
  - `tests/staged_python_floor.py`, a copy of `tests/test_python_floor.py` with R2.4;
  - `S/scripts/tests/staged_test_mermaid_model_package.py`, the module of R4.
- **R6.2** The change runs the four stages of `framework-upgrade` §3 step 4. The stage-3 patch:
  1. creates the 16 files of R1 and the module of R4, with the bytes of their staged copies;
  2. gives `tests/test_python_floor.py` the bytes of its staged copy;
  3. removes `S/scripts/mermaid_model.py`;
  4. applies R3.1 to `S/evals/render_corpus.py` and the row of R5.1 to `docs/ARCHITECTURE.md`.

  It touches no other path, and it holds no staged copy. Stage 3 removes each copy once its file
  hashes to it, and then the empty `S/scripts/staged_mermaid_model/`. Stage 3 adds no settings
  test.

  **Why.** No registration changes.
- **R6.3** On a failure of stage 3 or stage 4, the run recreates `S/scripts/staged_mermaid_model/`.
  It writes back each removed copy from its file, when that file still hashes to the copy, and
  then runs `git apply -R` of the patch. A file that hashes otherwise, or a failed
  `git apply -R`, stops the run for the operator. After the restore an ignored `__pycache__/` can
  keep `S/scripts/mermaid_model/` on disk; Python then imports `mermaid_model.py`.
- **R6.4** The edits of R2.2, R2.3, R2.5, the §10.3 wording of R5.1, R5.2, R5.3 and the records
  land in place before stage 3.
- **R6.5** The move check compares the base file with the staged package:
  - the body of each module of R1.1, after its imports, equals the lines of its section without
    the opening comment line. `SKILL_DIR`'s line is the one exception;
  - the docstring of `__init__.py` begins with base lines 2–27, and its body after the imports
    equals the entry-points lines without the opening comment line.
- **R6.6** The behaviour check compares the live tree before stage 3 with the patched tree. The
  patched tree is a throwaway worktree outside the repository that holds the live tree's files
  and the stage-3 patch. Each run starts in its tree's root and names files by paths relative to
  it. The run writes nothing in the tree from the creation of the worktree to the end of the
  check. It compares:
  - the bytes of `S/scripts/lint_mermaid.py --json` and `--inventory --json` for each Markdown file
    of the list of §8;
  - the output and exit of `S/scripts/plan_gantt.py --check docs/PLAN.md docs/PLAN.md`;
  - the eval selftest, 226 of 226 on both.
- **R6.7** The gates of `.github/workflows/framework-gates.yml` pass on the patched tree in that
  worktree. The check of `framework-upgrade` §3 step 4 runs for these commands, from the
  repository root unless a directory is named:
  - before stage 3: `python3 -m pytest` from the root and from `S/`; `python3 tests/run_tests.py`;
    `python3 -m unittest discover -s tests -v`; and `python3 -m unittest discover -s scripts/tests`
    from `S/`;
  - after stage 3: those commands, `python3 S/scripts/lint_mermaid.py` with the text output,
    `--json`, `--inventory` and `--inventory --json` of `S/references/paired-examples.md`, the
    text output of `S/scripts/tests/fixtures/fx-k33.mmd`, `--probe` alone, and
    `python3 S/scripts/plan_gantt.py --check docs/PLAN.md docs/PLAN.md`.
- **R6.8** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3. The audit record names each file of the change
  that a rule of either file runs, and quotes no rule (`framework-upgrade` §3 step 4).

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent edits the flowchart parser after this task

- **Precondition.** TASK 124 has landed.
1. The agent opens `S/scripts/mermaid_model/flowchart.py`, the 650 lines of one section.
2. It edits the parser. The callers still import `mermaid_model`, and the package binds the name.
3. If the edit imports a module below `flowchart.py`, TC-02 fails.
- **Postcondition.** The edit touches one module of the package, and the callers stay unedited.

### UC-2 — A test replaces the roots of negative fences

- **Precondition.** A test needs a temporary directory to count as a teaching file.
1. The test reads and assigns `NEGATIVE_ROOTS` through `sys.modules[mm.negative_allowed.__module__]`.
2. `negative_allowed` reads the new roots.
- **Postcondition.** The test's document counts, and the test restores the roots through the same
  expression.

### UC-3 — The floor test runs the grader under a faked Python 3.9

- **Precondition.** TASK 124 has landed.
1. TC-03 finds `mermaid_model/__init__.py` and parses each module that it imports.
2. TC-04 stubs `mermaid_model`, so no module body of the package runs.
- **Postcondition.** The grader exits 2 and names both versions, as at the base.

### UC-4 — TASK 125 splits `svg_geometry.py`

- **Precondition.** TASK 124 has landed, and its rule stands in `docs/ARCHITECTURE.md` §10.1.
1. TASK 125 reads the rule.
2. If a command runs `svg_geometry.py` by its path, TASK 125 keeps that file, which binds every
   top-level name, and gives the package another name.
3. Otherwise `svg_geometry` becomes a package of the same name, whose `__init__.py` binds every
   top-level name.
- **Postcondition.** TASK 125's package follows the points of R5.2.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — `S/scripts/mermaid_model/` holds the 16 files of R1.1, and `S/scripts/mermaid_model.py`
  does not exist.
- **A2** — the move check of R6.5 passes, with `SKILL_DIR`'s line as the only difference.
- **A3** — `S/scripts/tests/test_mermaid_model_package.py` passes on the patched tree. Against the
  base layout its tests fail and pass as R4.2 states.
- **A4** — the skill's test suite, `tests/run_tests.py`, `tests/test_python_floor.py` and the eval
  selftest pass on the patched tree. Before stage 3, the base `tests/test_python_floor.py`, placed
  in the worktree's `tests/`, fails TC-03 and TC-04 on the patched tree. Its staged copy passes on
  both trees.
- **A5** — the behaviour check of R6.6 finds no difference.
- **A6** — the gates and the check of R6.7 pass, and after stage 3 they pass on the tree.
- **A7** — `docs/ARCHITECTURE.md` §10.1 holds the row of R5.1 and the rule of R5.2, and the
  changelogs hold v3.44.0.
- **A8** — `git diff --quiet <base> --` exits 0 for `S/evals/grade_figures.py`, `S/evals/fidelity.py`,
  `S/scripts/render_check.py`, `S/evals/corpus` and `System/Docs`.
- **A9** — before stage 3, `python3 -m pytest --co` from the root and from `S/`, and both unittest
  discoveries of R6.7, list no staged file.
- **A10** — the audit record holds the three readings of R6.8 and names the files of the change
  that a rule of either settings file runs.

<!-- contract:open-questions -->

## 6. Open questions

None. The operator answered the scope (D1).

## 7. Decisions

- **D1**, 2026-10-15, operator: one module per task, `mermaid_model.py` first. Answer "По одному
  модулю". Rejected: the three scripts in one task, about 8,400 moved lines with three kinds of risk
  in one review.
- **D2**, 2026-10-15, orchestrator: `mermaid_model` becomes a package of the same name. No command
  runs the file by its path, so callers keep `import mermaid_model` and need no edit. Rejected: the
  file kept as a facade beside a package of another name, which adds a second name for one module.
- **D3**, 2026-10-15, orchestrator: one module per section of the base file, in a flat package.
  Each section reads only names of sections above it (§8), so the order of R1.1 holds no cycle.
  The ASCII section becomes `ascii_figures.py`: an `ascii.py` would bind `ascii` in `__init__.py`
  and hide the built-in function there. Rejected: a subpackage for the diagram parsers, which adds
  an import level and no boundary that the sections lack.
- **D4**, 2026-10-15, orchestrator: `__init__.py` binds every top-level name of the base module,
  private ones included. 6 callers read 9 private names. Rejected: a public subset, which would
  edit those 6 callers; the grader would stop with exit 2 at each private name that it reads
  through `getattr`.
- **D5**, 2026-10-15, orchestrator: the entry points stay in `__init__.py`. No section uses them,
  and `parse_figure` then looks `_parse_er` up in the package's own namespace. The two tests that
  assign `mm._parse_er` keep working unedited.
- **D6**, 2026-10-15, orchestrator: a test names the module that looks a name up as
  `sys.modules[<function>.__module__]`. The expression names `mermaid_model` at the base and the
  defining module after the split, so the edits land before stage 3. Rejected: test copies staged
  beside the package, about 4,000 more staged lines.
- **D7**, 2026-10-15, orchestrator: `S/evals/grade_figures.py`, `S/evals/fidelity.py` and
  `S/scripts/render_check.py` stay unedited. Every committed campaign report records the SHA-256
  of the first two (TC-ME-22). `render_check.INSTRUMENT_FILES` binds the two geometry fixtures,
  and `render_check.py` is one of those files. Their texts that name `mermaid_model.py` stay (§9).
- **D8**, 2026-10-15, orchestrator: the corpus instrument hash changes with the file list, and the
  committed corpus renders keep the old hash as their record. Rejected: a hash that ignores a move,
  which would also ignore an edit of the moved text.
- **D9**, 2026-10-15, orchestrator: the staged files are checked in a throwaway worktree with the
  patch applied. The floor test and the callers read the files at their final paths, which no
  module loader of the run can stand in for. TASK 123 D19 added that worktree for the gates.
- **D10**, 2026-10-15, orchestrator: the edit of `tests/test_python_floor.py` is staged.
  `tests/run_tests.py`, which an allow rule names, runs it, so it is no exempt test module
  (`framework-upgrade` §3 step 4). TASK 123 staged the same file.
- **D11**, 2026-10-15, orchestrator: the row of R5.1 lands in the stage-3 patch. TC-12 of
  `tests/test_mermaid_wiring.py` fails before stage 3 if the row names the package, and after it if
  the row names the file. The rule of R5.2 sits below the table, which TC-12 does not read, and
  lands in place.
- **D12**, 2026-10-15, operator: the skill stays self-contained, and its scripts stay inside it.
  The operator's words: "скилл должен быть самодостаточным и его скрипты должны оставаться внутри
  скила". R1.8, TC-07 and the last point of R5.2 state it. Every script of `S/scripts/` imports only
  the standard library and modules of `S/scripts/` at the base (§8).
- **D13**, 2026-10-16, orchestrator: fix round 1 of stage 2. Both reviews of round 1 passed, and
  the run applies their LOW findings before round 2, on the precedent of TASK 123 D18:
  - TC-03 of the floor test walks every module file of a package that it reaches. An absolute
    import of a module of a package names only the package to `_top`, so such a module escaped it
    (security LOW-1). A test of `_package_modules` ran red first;
  - TC-03 of the package test requires each name to be bound by a top-level `def`, `class` or
    assignment of its module, not by an import (code review L1);
  - a comment of `test_render_check.py`, the changelogs and R5.5 state what the code does (L2 to
    L4); §9 names the reach of TC-07 and the eval scripts that import from another skill.

  Rejected: the round's LOW findings left as residuals. TC-03 of the floor test would then pass a
  module that it never parsed (LOW-1), and TC-03 of the package test a name that a module imports
  (L1).
- **D14**, 2026-10-16, operator: fix round 2 of stage 2, then round 3, the last of the bound. Both
  reviews of round 2 passed, and every finding was a LOW route of a class that round 1 fixed. The
  operator chose one more round over a residual with a backlog record: "Ещё один раунд".
  - `_package_modules` fails on a symbolic link anywhere in a package that TC-03 walks, and on a
    module entry that is no regular file. Python imports through a link that `rglob` does not
    follow (security R2-LOW-1), and a device or a FIFO would be opened (R2-INFO-1);
  - two tests drive the walk itself: a module reached only by `import pkg.hidden`, and a
    subpackage behind a link, each fail it (code review N1, R2-INFO-2). The walker's subtests name
    a path outside the project as it is;
  - §9 names the subprocesses of `render_check.py` (N2); the PLAN cites this revision (N3); two
    changelog lines are rewrapped (N4); R2.4 and the floor test's docstring state the walk (I1).

  Rejected: the routes left as a residual of §9 with one backlog record. Round 3 then found two
  narrower routes of the class, a compiled module and a change of `__path__`. D15 closes the first
  and the plain spelling of the second, and D16 the other static spellings.
- **D15**, 2026-10-16, operator: round 3 of stage 2, the last of the bound, passed, and its
  findings were again LOW routes of the class of LOW-1. The operator's answer: "закрой рефакторинг
  без work items. ты же всегда рефакторил сразу". The run fixes the routes in fix round 3, and a
  fourth round reviews the fix; no backlog record is filed.
  - `_package_modules` also fails on a package directory that is a link and on a compiled or
    extension module, and leaves `__pycache__/` aside. The walk fails on an `__init__.py` that names
    `__path__` (security R3-LOW-1, R3-INFO-1; code review R3-2);
  - one test plants each of these forms, a directory and a FIFO named `*.py` among them, which pin
    the check of regular files (R3-1, R3-INFO-2). Each new case ran red first, but those two, which
    the check of round 2 already refused;
  - D14's last sentence, R2.4 and the floor test's docstring state what the walk refuses (R3-2).

  Rejected: a residual of §9 with one backlog record, which the operator declined.
- **D16**, 2026-10-16, orchestrator: fix round 4 of stage 2, under D15. Both reviews of round 4
  passed. The run fixes their findings and closes two static forms of the class that no review
  had named yet:
  - TC-03 counts only an entry whose name an import statement can spell. An editor's lock file
    or an AppleDouble file no longer fails it (code review R4-1, security R4-INFO-2);
  - every module that TC-03 walks fails on each static spelling of `__path__` and
    `submodule_search_locations` (R4-2, R4-LOW-1);
  - `__pycache__/` counts as the subpackage that Python imports there, and its caches stay aside.
    A link of that name now fails TC-03 (R4-INFO-1);
  - the suffixes are fixed sets for Linux, macOS and Windows, and a `*.pyw` source fails TC-03
    (R4-INFO-3, I2);
  - a compiled or extension module by a local name fails TC-03. Python may import it in place of
    the source: an extension module first in its directory, a compiled one from an earlier
    directory. A local module named after a standard-library module that the walked code imports
    fails too, in `GRADER_PATH` or beside a guarded script;
  - R2.4, the floor test's docstring and §9 state TC-03's reach (R4-2). PLAN line 7 is
    rewrapped (I1).

  Rejected: a check of every dynamic spelling, which no static check can make (both reviews of
  round 4). Rejected again: a residual with a backlog record, which the operator declined (D15).
- **D17**, 2026-10-16, operator: stage 2 closes at round 5, and both reviews of that round passed.
  The operator's words: "не надо оптимизировать ничего под Python 3.9 - он старый", and then
  "давай закрывать задачу уже. Кажется, что делается лишняя работа".
  - Security R5-LOW-1, code review R5-1 and its I1 name routes by which only an interpreter below
    the minimum stops before its guard. R5-2 asks for one more case of TC-03. None is fixed. §9
    states the limits, and no backlog record is filed;
  - R5-3, R5-INFO-1 and R5-INFO-2 correct wording. R2.4, D16, §9 and the audit record change in
    place. The floor test's docstring keeps its sentence on compiled modules: a change there would
    alter a staged copy after its review.

  Rejected: a fifth fix round and a sixth review round, which the operator declined.
- **D18**, 2026-10-16, operator: the layout of D2 stays. After stage 3 the operator wrote: "ты же
  обычно рефакторил так: делал папку с модулями и исходный модуль упрощал - делал тонкий
  менеджер/оркестратор". Offered a thin `mermaid_model.py` beside a package of another name, they
  answered "Оставить как есть". `mermaid_model/__init__.py` holds that role: the imports of the 15
  modules and the four entry points. The rule of R5.2 gives TASK 125 and TASK 126 the thin file for
  a script that a command runs by its path.

## 8. Measurements of this run

- The base module, by section; the line of each section's opening comment starts its range:

  | Section | Lines | Top-level names |
  | :--- | :--- | :--- |
  | header | 1–93 | 8 |
  | document level | 94–724 | 40 |
  | figure level | 725–989 | 22 |
  | hazard codes | 990–1069 | 8 |
  | labels | 1070–1148 | 10 |
  | kinds | 1149–1197 | 4 |
  | settings | 1198–1524 | 15 |
  | preprocessing | 1525–1667 | 5 |
  | flowchart | 1668–2318 | 17 |
  | sequence | 2319–2494 | 12 |
  | state | 2495–2707 | 10 |
  | gantt | 2708–2782 | 3 |
  | er | 2783–2875 | 6 |
  | other kinds | 2876–3174 | 23 |
  | ascii | 3175–3624 | 43 |
  | entry points | 3625–3708 | 4 |

- No name is bound in two sections. `S/scripts/mermaid_model.py:3224@44520ba`
  `_UP_STROKE, _DOWN_STROKE = _box_strokes()` binds two names through one tuple target, and lines
  3225–3226 rebind them in place.
- A name of one section that another section reads, annotations included, always belongs to a
  section above the reader. The module has no `global` statement, no import inside a function, no
  `__main__` block and no anchor literal.
- The 8 scripts that import the module: `lint_mermaid.py`, `render_check.py`, `plan_gantt.py` and
  `svg_geometry.py` of `S/scripts/`; `grade_figures.py`, `fidelity.py`, `render_corpus.py` and
  `selftest_figure_evals.py` of `S/evals/`.
- The 8 test modules that import it, all of `S/scripts/tests/`: `test_lint_mermaid.py`,
  `test_render_check.py`, `test_commonmark_scan.py`, `test_notation_consistency.py`,
  `test_paired_examples.py`, `test_plan_gantt.py`, `test_setup_renderers.py` and
  `test_svg_geometry.py`.
- The 9 private names that callers read:
  - `_Line`, `_fence_spans`, `_list_item`, `_parse_er`, `_parse_props`, `_quote_strip`, `_scan`;
  - `_paragraph_before` and `_paragraph_after`, through `getattr` in `grade_figures.py` only.

  6 callers read them: `lint_mermaid.py`,
  `grade_figures.py`, `fidelity.py`, `test_commonmark_scan.py`, `test_notation_consistency.py` and
  `test_lint_mermaid.py`.
- The grader reads 4 names through `getattr`: `_paragraph_before`, `_paragraph_after`,
  `_parse_props` and `NEGATIVE_MARKER`. A missing private one raises `InstrumentError`, exit 2. A
  missing `NEGATIVE_MARKER` leaves the text as it is.
- The lines that read or assign a name of the module, at `@44520ba`:
  - `NEGATIVE_ROOTS`: lines 1150, 1152, 1156, 1160, 1202, 1203 and 1206 of
    `S/scripts/tests/test_lint_mermaid.py`, and lines 379, 383, 387 and 669 of
    `S/scripts/tests/test_render_check.py`;
  - `negative_markers`: lines 1168, 1173 and 1179 of `S/scripts/tests/test_lint_mermaid.py`;
  - `_parse_er`: lines 1300, 1301, 1305, 2781, 2790 and 2798 of
    `S/scripts/tests/test_lint_mermaid.py`, in two tests.
- `S/scripts/mermaid_model.py:44@44520ba` `SKILL_DIR = Path(__file__).resolve().parent.parent`.
- The rules that run the module, named by the first 16 hex digits of their SHA-256: the committed
  rule `f594e5c59bc4365f` runs the lint, and the committed rules `de5f1e917179bf0e` and
  `cc744c1d56d6c74f` run `plan_gantt.py`. The reading of the local and the user's settings follows
  at §2.2.
- `S/evals/corpus/` holds 66 committed `geometry.json` files, each with an `instrument_sha256`.
- Each of the 6 scripts of `S/scripts/` imports only standard-library modules and modules of
  `S/scripts/`. The skill holds committed `.mmd` fixtures, `fx-k33.mmd` among them; the lint reads a
  `.mmd` file through `figure_from_mmd`.
- `System/scripts/install.py` installs by per-item symlinks by default, and by copies with
  `--mode copy`.
- The list of the behaviour check: every `.md` file of `S/references/`, `S/evals/corpus/`, `docs/`
  and `System/`, and `S/SKILL.md`.

<!-- contract:out-of-scope -->

## 9. Out of scope

- `S/scripts/svg_geometry.py` (TASK 125) and `S/scripts/lint_mermaid.py` (TASK 126).
- The texts that name `mermaid_model.py` in the three files of D7: the docstring of
  `grade_figures.py`, `S/evals/fidelity.py` line 20 in its docstring, and a comment of
  `render_check.py`. TASK 125 edits `render_check.py` and renders the fixtures again; it takes the
  comment.
- The record of `S/evals/AMENDMENTS.md` that names `mermaid_model.py`; a record keeps its text.
- The re-render of the committed corpus renders (D8).
- The glob of `test_every_anchor_a_script_reads_is_registered` of `tests/test_mermaid_wiring.py`,
  while no package holds an anchor literal (R5.2).
- WI-54, the residual routes of the put-back of `framework-upgrade` §3 step 4.
- TC-07 reads the static absolute imports of the scripts and of the package. A dynamic import or a
  `sys.path` entry outside the skill would pass it; neither exists today (D13). `render_check.py`
  runs `mmdc` and node as subprocesses in the renderers' install directory outside the skill,
  which TC-07 does not read (D14).
- TC-03 of the floor test reads files and runs none of their code. Code that runs to import is out
  of its reach, such as `exec`, `eval`, `__import__`, `importlib`, a loader called directly, a
  computed `getattr`, a module-level `__getattr__`, or a change of `sys.path`, `sys.meta_path` or
  `sys.path_hooks`. So are the interpreter's environment, such as `PYTHONPATH` or a `.pth` file,
  and Python's bytecode cache. TC-03 reads no import in a class or a function body. It refuses a
  local module of a standard-library name only for a name that the walked code or a guarded script
  imports, not for one that the standard library imports in turn, such as `gettext` (D17).
  Of the modules that TC-03 walks today, `lint_mermaid.py`, `svg_geometry.py` and
  `S/evals/fidelity.py` change `sys.path`, each to add `S/scripts/`, a directory of `GRADER_PATH`.
  None of them uses the other forms, and each `getattr` call there names its attribute literally
  (D16).
- The skill's eval scripts import from another skill: `S/evals/grade_figures.py` imports
  `aggregate_benchmark`, and `S/evals/selftest_figure_evals.py` puts `skill-creator/scripts` on
  `sys.path`. R1.8 covers `S/scripts/`. At the retro the operator kept the rest of the skill as it
  is (D13).
