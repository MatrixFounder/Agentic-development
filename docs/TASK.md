# TASK 122 — The render check prints no raw control character, a bare pytest run collects, and the quick-reference figure is redrawn

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 122 |
| Slug | render-output-pytest-figure |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Findings of TASK 121 marked as before the task; the operator's request of 2026-10-15 |
| Base revision | `b6362e3444eaa1b9109a104a445b100f7e4e964d` |
| Closes | none: no backlog record holds these findings |
| Archive name | `task-122-render-output-pytest-figure.md` |
| Revision | 7 |

**Request.** The operator listed five findings of TASK 121 and asked which need a fix. The answer
named four: the two outputs of `render_check.py`, the bare pytest run and the legacy figure. It
called the nine positional-reference errors optional. The operator then wrote "Я сделал коммит,
выполни доработки".

**Revision 2** applies the findings of Mode A round 1: M1, M2 and m1 to m7, and the notes.
**Revision 3** applies r2-1 and the notes N1 to N8 of round 2. **Revision 4** follows M1 of Mode B
round 1: `svg_geometry.py` stays unedited (D10). **Revision 5** applies r3-1 of Mode A round 3, r2-3
of Mode B round 2, and the notes of both. **Revision 6** applies review round 1 (D11), and
**revision 7** review round 2 (D12) and the wording of round 3.

<!-- contract:problem -->

## 1. Problem

1. **The render check prints control characters raw.** Its JSON is `json.dumps(…,
   ensure_ascii=False)`. That form leaves U+0085, U+009B, U+007F, U+00A0, U+2028 and U+202E raw
   (§8). Label text and font names come from the page, so a figure can put a terminal control
   sequence into the output. The text report prints the clean font name and the error lines of
   mmdc raw as well.
2. **A long label can stop the whole run.** `measure_text.mjs` cuts label text with
   `.slice(0, 120)`, which counts UTF-16 units. A cut through an emoji leaves a lone surrogate.
   `render_check.py` then writes the measurement as UTF-8 and raises `UnicodeEncodeError`. The
   render catches only `OSError`, so the run ends at that render with one traceback and prints no
   figure's report.
3. **A bare pytest run collects nothing.** Two allow rules run `python3 -m pytest` and `python -m
   pytest` without a prompt. From the repository root, the run stops with `INTERNALERROR` and exit
   3. `examples/skill-testing/test_skill.py` calls `exit(1)` at import when `openai` is absent, and
   pytest collects the file by its name.
4. **The quick-reference figure of `System/Docs/WORKFLOWS.md` is cut on GitHub.** The `graph TD`
   figure under "Quick Reference: Choosing Your Approach" has no settings line. In GitHub's font,
   15 of its labels are hidden (TASK 121, F8). The lint reports 18 warnings on it, and one more on
   the next figure, whose settings line differs from it (§8). The figure also draws a cycle: `run
   base-stub-first` leads to the criticality question, whose `Standard` answer leads back to it.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | The JSON files and printed lines of the render check hold no raw non-printable character | Y | R1.1–R1.5 | A1, A2 |
| R2 | A cut never splits a surrogate pair | Y | R2.1–R2.2 | A2 |
| R3 | A bare pytest run collects, and writes no live state | Y | R3.1–R3.4 | A3 |
| R4 | The quick-reference figures pass | Y | R4.1–R4.5 | A4 |
| R5 | Evidence, tests and records | Y | R5.1–R5.7 | A1–A6 |

## 3. Requirements

A character is **non-printable** when `str.isprintable()` returns false for it.

### R1 — the output of the render check

- **R1.1** `scripts/render_check.py` gains `json_text(value, **kw)`. It returns
  `json.dumps(value, ensure_ascii=False, **kw)` with each non-printable character other than a
  newline written as a JSON `\u` escape.
  - A non-printable code point above U+FFFF, such as U+E0001, becomes its pair of surrogate
    escapes. A printable one, such as U+1F4E6, stays as it is.
  - `json.loads` of the result equals *value*. The one exception is a high surrogate followed
    directly by a low surrogate as two code points: `json.loads` joins their escapes into one.
- **R1.2** Each JSON file that `scripts/render_check.py` writes, and each JSON it prints, comes
  from `json_text`:
  - the measurement file of each render;
  - `mermaid-config.json` of each render;
  - `evidence.json`;
  - the report of `--json`, at both of its print sites;
  - the keys and values of `dump_json`, which writes a fixture.

  `browser_stat_digest` keeps `json.dumps(row, ensure_ascii=False, …)`. It hashes the rows that
  `setup_renderers.sh` hashes with `JSON.stringify`, and it writes and prints nothing.
- **R1.3** Withdrawn in revision 4 (D10): `svg_geometry.py` is not edited, its command line among
  its parts.
- **R1.4** Each `print` call of `render_check.py` passes its text through `_shown` of that file,
  which writes each non-printable character, a newline among them, as its Python escape,
  `ascii(ch)[1:-1]`. A backslash stays single (D5).
  - The text report prints its lines one by one, so a newline inside a field cannot start a line.
  - A JSON print keeps the newlines that lay out its JSON; `json_text` escapes any other.
  - The only `print` call of the file is the one inside `_say`.

  The calls print:
  - the text report, its notes and the `fixture:` line;
  - each `not rendered` reason;
  - each command-line error, the error of reading `notation.json` among them.

  argparse prints its usage and its errors itself, and stays as it is (D8).
- **R1.5** A measurement that holds a lone surrogate leaves its render `ok`, and the run writes the
  measurement file. Three files keep the figure's text as written: the `.mmd` copy of a fence, the
  SVG that mmdc writes and the PNG that `measure_text.mjs` writes. They are the renderer's input
  and output.

### R2 — the cut of `measure_text.mjs`

- **R2.1** Both cuts of label text count code points: the clean measurement's text of each element,
  and the text of each swapped `foreignObject`. Each keeps the first 120 code points of the
  collapsed text, as `_line_anchor` of `svg_geometry.py` does with `[:120]`.
- **R2.2** The header comment of `measure_text.mjs` states the cut in code points.

### R3 — the bare pytest run

- **R3.1** `examples/skill-testing/test_skill.py` imports `openai` inside `query_model`, after its
  dry-run branch. Importing the module without `openai` neither exits nor raises.
- **R3.2** `query_model` without an API key returns the dry-run text and imports nothing. No key
  means that neither `OPENAI_API_KEY` nor `XAI_API_KEY` is set. With a key set and without
  `openai`, it prints the install message and exits 1.
- **R3.3** A new test module `tests/test_bare_pytest.py`:
  - runs pytest's collection from the repository root in a subprocess, with `import openai`
    failing, and asserts exit 0 and no `INTERNALERROR` in the output;
  - checks R3.1 and both branches of R3.2 in subprocesses, with `import openai` failing. Each
    subprocess prints a marker after the import, so an exit at import fails the check. The branch
    without a key clears both variables of R3.2, and the branch with a placeholder key clears
    `OPENAI_BASE_URL`.

  The tooling step of `.github/workflows/framework-gates.yml` lists the module.
- **R3.4** The bare run writes no live state, and leaves no path that git does not ignore (D11):
  - `tests/test_mock_agent.py` runs its mock in a sandbox of a temporary directory, with an empty
    `.git` and a copy of `update_state.py`, and removes the sandbox. It asserts that the bytes of
    the live `.agent/sessions/latest.yaml` stay as they were;
  - `tests/test_tool_runner.py` writes under `tests/.scratch`, which git ignores, and asserts that
    `git check-ignore` accepts its directory.

### R4 — the quick-reference figures of `System/Docs/WORKFLOWS.md`

- **R4.1** The figure under "Quick Reference: Choosing Your Approach" becomes two figures (D3):
  - "choosing your approach": 9 nodes and 8 edges. Four questions lead to `run light`,
    `run iterative-design`, a one-step pipeline, VDD Multi-Step or TDD Multi-Step;
  - "choosing the one-step pipeline": 5 nodes and 4 edges. The scenario question leads to
    `run base-stub-first`, `run vdd-enhanced`, `run full-robust` or `run vdd-multi`.
- **R4.2** Each figure opens with the flowchart settings line of `assets/notation.json`. It holds
  `accTitle` and `accDescr`, and the document's class `wf` with its `classDef` as written.
- **R4.3** A caption paragraph sits directly above each fence, in the form of the document's
  product-approach caption.
- **R4.4** Each node and edge label has a supporting line in `WORKFLOWS.md` (§8, fidelity table).
- **R4.5** No figure of the document draws a cycle that the text does not state.

### R5 — evidence, tests and records

- **R5.1** `render_check.py --fixture` writes `scripts/tests/fixtures/references-geometry.json` and
  `scripts/tests/fixtures/paired-examples-geometry.json` anew. The instrument hash changes with R1
  and R2.
- **R5.2** Tests, each run red against its base code first (R5.6):
  - `test_render_check.py`: `json_text` escapes C1 controls, DEL, U+2028, U+202E, NBSP, a lone
    surrogate and U+E0001. It keeps Cyrillic and U+1F4E6. `json.loads` reads each result back.
  - `test_render_check.py`, stubbed runs. The clean font name, a finding, a note, a render's
    error line and a `not rendered` reason hold control characters and a lone surrogate. The
    text output, the `--json` output, `evidence.json` and `dump_json` then hold no non-printable
    character but newlines. Three more cases hold none either:
    - a command-line error that names a path with a control character;
    - a run with no renderer, whose install home holds ESC and U+009B in its name: the `home` and
      `missing` of its `--json` report, and its `not rendered` lines;
    - a run with `--fixture` at a path that holds ESC and U+009B: the `fixture.path` of its
      `--json` report, the `fixture:` line and the written fixture.
  - `test_render_check.py`, a stand-in measurement whose font name holds C1 controls, U+202E and a
    lone surrogate: the render is `ok`. The measurement file holds no non-printable character but
    newlines, and reads back.
  - `test_render_check.py`, installed renderers: a label of 119 letters and an emoji is measured
    as those 120 code points, in `labels` and in `font_swap.labels`, with no lone surrogate.
  - `tests/test_bare_pytest.py` of R3.3.
  - `test_render_check.py`, for D11:
    - a finding that holds a newline prints as one line;
    - a command-line error whose path holds a newline prints as one line too;
    - a forward render whose log holds control characters prints its `note:` line escaped;
    - an AST check finds one `print` call, inside `_say`;
    - an AST check finds `lines` passed at two `_say` calls, each printing `json_text(…)`.
  - the two tests of R3.4.
- **R5.3** `docs/ARCHITECTURE.md` §10.7 states R1: the JSON files and printed lines of the render
  check hold no raw non-printable character.
- **R5.4** `CHANGELOG.md` and `CHANGELOG.ru.md` get v3.42.1, titled "the render check prints no raw
  control character, a bare pytest run collects, and the quick-reference figure is redrawn
  (TASK 122)".
- **R5.5** No code that a committed allow rule names changes (D12), and no listed script runs or
  imports the edited code:
  - no committed rule names `render_check.py`, `measure_text.mjs` or the example;
  - no guarded script imports `render_check.py` before its guard, and no listed script runs
    `measure_text.mjs`;
  - `tests/test_bare_pytest.py`, `tests/test_mock_agent.py` and `tests/test_tool_runner.py` are
    test modules that `tests/run_tests.py` does not run.

  `svg_geometry.py` runs without a prompt: `tests/run_tests.py` runs `test_python_floor`, whose
  TC-04 runs `evals/grade_figures.py`. The grader imports `svg_geometry` before the guard of the
  `run_evals` it imports next (§8).
  The run therefore leaves `svg_geometry.py` unedited (D10).

  The rules `python3 -m pytest` and `python -m pytest` name no path. After R3.1 they run the test
  modules of `tests/`, which no committed rule names by path; `framework-upgrade` §3 step 4
  exempts those (D12).
  A3 requires the bare run to collect. §8 records that the suite passes with `--ignore=examples`;
  the gates of the PLAN run the bare run after R3.1.
- **R5.6** Stub first: each new test fails against the base text of the code it tests before that
  code is edited. The audit record holds each red run, or names why a test passes on the base.
- **R5.7** `System/Docs/SKILLS.md` changes only where it states a fact this task changes. Its
  `mermaid-authoring-guidelines` row and note state none of R1 or R2.

**Migration.** No session state, notation key or command changes. The instrument hash of the render
check changes with R1 and R2, so render evidence written before this task reads as stale and is
written anew (R5.1).

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent renders a figure whose label holds an emoji at the cut

**Precondition.** The pinned renderers are installed. A label holds 119 letters and then an emoji.

1. `measure_text.mjs` keeps the 120 code points, the emoji whole.
2. `render_check.py` writes the measurement file and reports the figure.

**Postcondition.** The measurement file holds no lone surrogate, and the run reports every figure.

**Alternative A.** A measurement holds a lone surrogate from another source. `json_text` writes it
as an escape, and the run continues.

### UC-2 — A figure puts control characters into a label or a font name

**Precondition.** A render completes; its label text or font name holds ESC or C1 characters.

1. The run prints its report and writes `evidence.json`.
2. Each control character prints as an escape: `\x1b` in the text output, a `\u` escape in the
   JSON.

**Postcondition.** The terminal shows the escape and runs no control sequence.

### UC-3 — An agent runs the allowed bare pytest

**Precondition.** The repository root is the working directory; `openai` is not installed.

1. `python3 -m pytest` collects from the root, and the import of the example does not exit.
2. The run executes the tests of `tests/`.

**Postcondition.** The run reports its results; no `INTERNALERROR` occurs.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — the tests of R5.2 for R1 pass. In a stubbed run with control characters, the text
  output, the `--json` output, `evidence.json` and a fixture hold no non-printable character but
  newlines. In the stand-in run of R1.5, the measurement file holds none either.
- **A2** — the stand-in test of R1.5 and the installed-renderer test of R2.1 pass. The full suite
  of the skill passes: `python3 -m pytest -p no:cacheprovider scripts/tests -q` from the skill's
  directory.
- **A3** — `python3 -m pytest --co -q -p no:cacheprovider` from the repository root exits 0 with
  `openai` absent, and `tests/test_bare_pytest.py` passes. A bare run from the root leaves the
  sha256 of `.agent/sessions/latest.yaml` as it was.
- **A4** — `lint_mermaid.py System/Docs/WORKFLOWS.md` reports 0 errors and 0 warnings.
  `render_check.py System/Docs/WORKFLOWS.md` exits 0, every figure `pass`.
- **A5** — every step of `.github/workflows/framework-gates.yml` passes as CI runs it.
- **A6** — each red run of R5.6 is in the audit record, and every path of `git status` is a
  declared path of the PLAN.

<!-- contract:open-questions -->

## 6. Open questions

None.

## 7. Decisions

- **D1**, 2026-10-15, orchestrator: one `/framework-upgrade` run carries the four fixes.
  `framework-upgrade` §0 needs a clean tree. A `/light` run first would leave its edits for the
  operator's commit before this run could start. Rejected: `/light` for the figure and pytest, then
  `/framework-upgrade` for the render check.
- **D2**, 2026-10-15, orchestrator: the nine positional-reference errors stay out of scope. The
  answer to the operator called them optional, and the request asked for the fixes that answer
  named. Rejected: fixing them in this run. Eight are references in old changelog entries to files
  of another repository, one is in a review record, and no gate reads them. The end-of-run report
  names them as open.
- **D3**, 2026-10-15, orchestrator: the legacy figure becomes two figures, split by concern. It has
  15 nodes and 16 edges, over the soft budget of 12. The scenario question follows the one-step
  answer, so the cycle goes. Each label takes the words of a line of the document (§8). Rejected:
  one figure of 13 nodes, which stays over the budget.
- **D4**, 2026-10-15, orchestrator: the JSON keeps printable non-ASCII text as it is. Rejected:
  `ensure_ascii=True`, which writes every Cyrillic letter of a label as an escape in `evidence.json`
  and in the fixtures.
- **D5**, 2026-10-15, orchestrator: `_shown` writes no doubled backslash. Paths and the `%r` quotes
  of the findings keep their form. The fields that TASK 121 escaped keep their doubled backslash.
  Rejected: doubling at the print boundary, which would double each backslash of a quoted label
  again.
  - Residual: in a line `_shown` escapes, the literal text `\x1b` prints as an escaped ESC does.
    No control character reaches the terminal.
- **D6**, 2026-10-15, orchestrator: the cut counts code points. Rejected: dropping a trailing high
  surrogate after a cut of 120 units, which keeps a cut shorter than the Python side's for text with
  emoji.
- **D7**, 2026-10-15, orchestrator: the example imports `openai` where it uses it. Rejected:
  renaming the file, which the changelogs name, and a `collect_ignore` in a new root `conftest.py`,
  which hides the example and leaves its exit at import.
- **D8**, 2026-10-15, orchestrator: argparse's own usage and errors stay as they are. Python 3.14
  colours them with escape sequences of its own, which `_shown` would print as text. Rejected:
  routing them through `_shown`.
  - Residual: an option-like argument that holds a control character prints raw in argparse's
    error. It comes from the caller's command line, or from a glob over a file whose name starts
    with `-`. Low risk.
- **D9**, 2026-10-15, orchestrator: the nested collection of R3.3 runs under both Python versions of
  the CI matrix, 3.11 and 3.14. It is measured on 3.14.8, and under the 3.11 grammar statically
  (§8). Rejected: skipping the test below 3.12, which would hide a failure of the bare run on the
  framework's minimum Python.
  - Residual: no 3.11 interpreter is installed here, and `ast.parse(feature_version=…)` is best
    effort. The 3.11 run of A5 happens first in CI.
- **D10**, 2026-10-15, orchestrator: `json_text` lives in `render_check.py`, and `svg_geometry.py`
  stays unedited. Its module body runs without a prompt (R5.5), so an edit would need the four
  stages of `framework-upgrade` §3 step 4. Rejected: staging it, since the fixtures bind its
  hash and stage 3 would leave them stale. Rejected as well: an operator's exception for an edit
  that adds one function. Once R1.3 is withdrawn, `render_check.py` is the only caller of
  `json_text`.
- **D11**, 2026-10-15, orchestrator: review round 1 found that the bare run, which this task
  unblocks, rewrites the live session state through `tests/test_mock_agent.py` (F1). Fix round 1
  isolates that test and moves the scratch of `tests/test_tool_runner.py` (R3.4). It also escapes
  a newline inside a printed field (LOW-1) and pins each `_say` site. The orchestrator restores the
  live state and drops its test records. Rejected: a residual with a backlog record, which would
  leave each allowed bare run rewriting the state that the next session restores.
- **D12**, 2026-10-15, orchestrator: the edit of `tests/test_tool_runner.py` stays unstaged (R2-1
  of review round 2). An allow rule of `.claude/settings.local.json`, which git ignores, names
  that test.
  - `framework-upgrade` §3 step 4 lists "a script that a committed allow rule names", and exempts
    only "test modules and fixtures that no rule names by path". The two sentences disagree on a
    local rule. Their reading is the operator's call, and the end-of-run report names it.
  - The edit moves the test's scratch into `tests/.scratch` and adds a `git check-ignore`. Review
    rounds 2 and 3 checked it.
  - Rejected: the four stages for a test module that no committed rule names.

- **D13**, 2026-10-15, operator: the allow rules that `framework-upgrade` §3 step 4 counts include
  those of `.claude/settings.local.json`. Two items of the retro become TASK 123, after the
  operator's commit of this task:
  - the text of §3 step 4 on local rules;
  - a check of what a change newly makes run without a prompt.

  A curated test pins that text, so TASK 123 stages it.
  Answers "И settings.local.json" and "TASK 123 после коммита". Rejected: extending this task,
  which had passed its reviews, and counting committed rules only.
  - Under this reading, the edit of `tests/test_tool_runner.py` (D12) would have taken the four
    stages. It stays as review rounds 2 and 3 checked it.

## 8. Measurements of this run

- From the repository root, `python3 -m pytest --co -q -p no:cacheprovider` exits 3 with
  `INTERNALERROR` and "no tests collected". With `--ignore=examples` it collects 709 tests and exits
  0, and a run with `--ignore=examples` gives "709 passed".
- The 39 test files of that collection parse under `ast.parse(…, feature_version=(3, 11))`, and
  none imports a name added after 3.11 at module level. CI's tooling job runs 3.11 and 3.14.
- `json.dumps(…, ensure_ascii=False)` leaves U+0085, U+009B, U+007F, U+00A0, U+2028 and U+202E raw.
  `ensure_ascii=True` leaves none, and writes Cyrillic as escapes.
- Writing `json.dumps(…, ensure_ascii=False)` of a lone surrogate to a UTF-8 file raises
  `UnicodeEncodeError`.
- In node, `.slice(0, 120)` of 119 letters and U+1F4E6 ends on U+D83D, a lone surrogate.
  `Array.from` keeps the emoji whole.
- The lint of `WORKFLOWS.md`: "0 error / 19 warn". The legacy figure holds 18:
  - `MA-SET-06` once;
  - `MA-BUDGET-01` twice (15 nodes, 16 edges);
  - `MA-DOC-01` once;
  - `MA-LABEL-03` once;
  - `MA-LABEL-07` thirteen times.

  The 19th is `MA-SET-07` on the product-approach figure: its settings differ from the legacy one.
- The two new figures, written to a scratch file first: lint "0 error / 0 warn". Both pass the
  render check in 11.17.2, dark and 10.9.8. The swap font is `.SF NS`. Widths and heights:
  - "choosing your approach": 653×1085 px (11.17.2) and 618×1025 px (10.9.8);
  - "choosing the one-step pipeline": 746×317 px and 694×287 px.
- No allow rule names `render_check.py`, `svg_geometry.py`, `measure_text.mjs` or the example.
  `tests/test_mermaid_wiring.py`, a curated module, names `render_check.py` and never runs or
  imports it.
- `evals/grade_figures.py` imports `mermaid_model`, `lint_mermaid`, `svg_geometry`, `fidelity`
  and `stats` before `run_evals`, whose guard stops an old Python. TC-04 of
  `tests/test_python_floor.py` runs the grader under a faked 3.9.

**Fidelity table of R4.4.** Each label, and the line of `WORKFLOWS.md` that supports it:

| Label | Supporting line |
| :--- | :--- |
| Trivial task, `yes: typo, bugfix`, `run light` | Summary Table, "Trivial task (typo, bugfix)" |
| Concept to refine, `run iterative-design` | §1 Pipelines, "Iterative Design … Concept Refinement Loop" |
| Trust automation, One-Step pipeline | Approaches Overview, "One-Step (Pipeline) … trusted automation" |
| `no: learning, debugging` | Approaches Overview, "Multi-Step (Manual) … Learning, debugging" |
| Adversarial review, VDD Multi-Step | FAQ, "adversarial review per task"; VDD Examples, "Multi-Step Approach" |
| TDD Multi-Step | TDD Examples, "Multi-Step Approach (Manual Control)" |
| Which scenario | Summary Table, its column "Scenario" |
| `quick feature`, `run base-stub-first` | Summary Table, "Quick feature, trusted automation" |
| `high-quality code`, `run vdd-enhanced` | Summary Table, "High-quality production code" |
| `security-critical`, `run full-robust` | Summary Table, "Security-critical feature" |
| `max quality: 3 critics`, `run vdd-multi` | Summary Table, "Maximum code quality (3 parallel critics)" |

The second line "chosen in the next figure" and the `yes` and `no` answers are the figure's own
navigation and state no fact.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The nine positional-reference errors in old changelog entries and in
  `docs/reviews/review-095-independent.md` (D2), and two more of the same coordinates in
  `docs/reviews/framework-audit-105.md`.
- The example sends `XAI_API_KEY` to the default OpenAI URL when only that key is set. Its
  `__main__` fails before `query_model`.
- Raw invisible characters in the string literals of `test_ledger_hardening.py` of `run-feedback`.
- The mock of `tests/test_mock_agent.py` runs `python3` from PATH, and it sleeps 5 s.
- The `__main__` block of the example names `08_agent_developer.md` and two skills with a
  `skill-` prefix, none of which exists. Run as a script, it ends in `FileNotFoundError`. Before the
  task; the operator did not ask for it.
- The quoting rules of `lint_mermaid.py` that print label text raw, and its `--json` output, which
  is `json.dumps(…, ensure_ascii=False)`. Before TASK 121; the lint is code that an allow rule
  names.
- The join of a label's lines with no separator in `measure_text.mjs`.
- The debug command line of `svg_geometry.py`, which prints its JSON with `ensure_ascii=False`
  (D10).
- `evals/render_corpus.py`, which writes the metrics of each render, `geometry.json`, with
  `ensure_ascii=False`, so a lone surrogate still stops a corpus render. Before the task.
