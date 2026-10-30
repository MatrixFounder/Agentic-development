# TASK 139 — [LIGHT] Four scripts read and write text in UTF-8, and the Windows tests run under cp1252 (PT-1)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 139 |
| Slug | scripts-read-and-write-utf-8 |
| Type | Light Mode (D1) |
| Source | PT-1; the Windows report of loyalty-api-java (2026-10-28); the operator's requests of 2026-10-29 and 2026-10-30 |
| Base revision | `36ca054d2cd7dbdf6c46cb297651907fe2efee50` |
| Closes | PT-1 |
| Archive name | `task-139-scripts-read-and-write-utf-8.md` |
| Revision | 3 |

**Request.** The operator set the order of the open items of the Windows report: MR-1 (TASK 137),
WI-60 and WI-61 (TASK 138), then PT-1. On 2026-10-30 the operator added a rule to PT-1: the tests
of a script that runs on Windows also run on the local machine under `PYTHONIOENCODING=cp1252`.
The retro of TASK 138 proposed the rule: there the review found a `§` on stderr that the Windows
jobs would have decoded as `cp1252`, and the tests on macOS passed.

**Revision 2** follows the code review of cycle 1: CHANGES REQUESTED, with one MAJOR, six MINOR
and fifteen NIT findings, none BLOCKING. The fix pass:
- the MAJOR: `X.open` counts as `Path.open` only with no positional argument or a mode literal
  first, so `gzip.open(p, "rb")` and `ZipFile(p).open(name)` pass (D7);
- R3 reaches the scripts of PT-1: the check joins both Windows jobs (D6, R6);
- `calculate_roi.py` and `generate_wrappers.py` escape on their streams what the codec cannot
  encode (R5); before, a `cp1252` pipe ended the first in `UnicodeEncodeError`;
- TC-E3 probes the codec that `open` takes and runs with the streams of the locale; TC-E2 pins
  `io.open`, `builtins.open` and the forms of D7; TC-E5 and TC-E6 are new;
- the check lists a new file that git would add, and skips a tracked file gone from the work tree;
- Rule 5, the counts of §0, §5 and both changelogs state what the code does.

**Revision 3** follows cycle 2: APPROVED, with two MINOR and nine NIT findings. The fix pass (D8):
- an `X.open` with no positional argument is `Path.open` only when each keyword is one of
  `Path.open` and `mode` is a mode literal, so `tarfile.open(fileobj=f)` passes (D7);
- TC-E2 reports `p.open("r")`, `"a"`, `"r+"` and `"xt"`, and passes three keyword forms;
- TC-E7 pins the listing, which now skips a virtualenv; TC-E6 reads each Windows job;
- D6 names its areas; TC-E3 and §5 state what each platform and D7 let through; the changelogs
  name `builtins.open`.

**Measured at the base** (`36ca054`):
1. The check of R2 finds 7 calls that open a file as text with no `encoding=` in the scripts under
   `.agent/` and `System/`, outside tests and evals. They are the seven calls of PT-1:

   | Script | Lines |
   | :--- | :--- |
   | `.agent/skills/skill-parallel-orchestration/scripts/generate_wrappers.py` | 26, 136, 140 |
   | `.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py` | 64 |
   | `.agent/skills/skill-product-handoff/scripts/trigger_technical.py` | 48 |
   | `.agent/skills/skill-product-solution-blueprint/scripts/calculate_roi.py` | 19, 141 |

2. The same check finds 58 such calls in evals: 57 under `run-feedback/evals/` and 1 in
   `mermaid-authoring-guidelines/evals/run_evals.py`. It finds 99 in the tests under `.agent/`
   and `System/`, and 188 in `tests/`.
3. `LC_ALL=ru_RU.CP1251 python3 -I generate_wrappers.py --check` exits 1. Under `LC_ALL=C` with
   `-X utf8=0`, the locale's codec is `US-ASCII`, and the script ends in `UnicodeDecodeError` on
   the manifest.
4. Under `PYTHONIOENCODING=cp1252`, `calculate_roi.py` exits 1 with `UnicodeEncodeError` on the
   emoji of its first line of output.

## 1. Decisions

- D1, 2026-10-30, operator: `/light`. The run has the edits with their tests, the test run, and
  one code reviewer with the exhaustive prompt, in at most two review cycles
  (`light-02-develop-task`).
- D2, orchestrator: the run adds one test file, `tests/test_text_encoding.py`. The light-mode
  condition "no new files" is not met for it. The file holds the check that the fix path of PT-1
  names; no other file of the run is new.
- D3, orchestrator: the check covers the scripts under `.agent/` and `System/`. A file under a
  `tests/` or `evals/` directory, and a file named `test_*.py`, are out of its scope (§5).
- D4, orchestrator: the rule of the operator stands in `docs/ARCHITECTURE.md` §8, Rule 5, beside
  the other rules of the scripts of a skill. A comment beside the Windows jobs of
  `framework-gates.yml` points to it.
- D5, orchestrator: the behaviour test takes the locale `C` with UTF-8 mode off, whose codec is
  ASCII. That locale exists on Linux and macOS; `ru_RU.CP1251` is absent on the Linux runners. On
  Windows the test takes the code page of the runner.
- D6, orchestrator, after review: R3 names the tests of the Windows jobs. Those jobs run the
  tests of the areas ported to native Windows: the session state, the archive chain and
  run-feedback (TASK 127 to 133), and the Mermaid renderers (TASK 137).
  `tests/test_text_encoding.py` joins both Windows jobs of `framework-gates.yml`. So the rule
  reaches the scripts of PT-1, and CI runs D5 on Windows.
- D7, orchestrator, after review: no type is known to a static check. An `X.open` is a call of
  another module when its first argument is a path or a member name, as in `gzip.open(p)`. So is
  one with a keyword that `Path.open` does not take, as in `tarfile.open(fileobj=f)`. The check
  reads such a call as no text call.
- D8, orchestrator: cycle 2 approved the change, and `light-02-develop-task` allows two cycles.
  The findings of cycle 2 are fixed with no third cycle; the tests of §4 and the gates verify the
  pass.

## 2. Requirements

<!-- contract:requirements -->

- **R1** The seven calls of §0 pass `encoding="utf-8"`.
- **R2** `tests/test_text_encoding.py` fails when a script in the scope of D3 opens a file as text
  with no encoding. The calls it reads are `open`, `io.open`, `builtins.open`, `os.fdopen`,
  `Path.open` (D7), `read_text` and `write_text`. A call opens text when its mode has no `b`. It
  gives no encoding when it passes none or passes `encoding=None`. The failure names the file and
  the line. The curated suite of `tests/run_tests.py` lists the file.
- **R3** `docs/ARCHITECTURE.md` §8 states Rule 5:
  - a script outside tests and evals passes `encoding="utf-8"` to each call that reads or writes
    a text file; R2 checks that an encoding is given, not its value;
  - before a push, the tests that the Windows jobs of `framework-gates.yml` and
    `mermaid-render-windows.yml` run also run on the local machine under
    `PYTHONIOENCODING=cp1252`.
- **R4** PT-1 closes in its record and in `docs/KNOWN_ISSUES.md`; both changelogs carry the
  release v3.55.1.
- **R5** `generate_wrappers.py` and `calculate_roi.py` reconfigure stdout and stderr with
  `errors="backslashreplace"` at the start of `main`, as `run_feedback.py` does.
- **R6** Both Windows jobs of `framework-gates.yml` run `tests/test_text_encoding.py` (D6).

## 3. Files

- the four scripts of §0;
- `tests/test_text_encoding.py` (new), `tests/run_tests.py`;
- `docs/ARCHITECTURE.md`, `.github/workflows/framework-gates.yml`;
- `docs/issues/pt-1-*.md`, `docs/KNOWN_ISSUES.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`;
- `docs/TASK.md`; the archive of TASK 138.

## 4. Acceptance

<!-- contract:acceptance -->

- TC-E1 — the scripts in the scope of D3 → no call is reported. On the base the check names the
  seven calls of §0 and no other.
- TC-E2 — a sample source → the check reports each text call with no encoding, `encoding=None`
  and a mode in a variable. It passes:
  - a binary mode, and an encoding by keyword or by position;
  - `os.open`, `webbrowser.open` and a call with `**kwargs`;
  - an `X.open` with a path or a member name first, such as `gzip.open(p, "rb")`;
  - an `X.open` with a keyword of another module, such as `tarfile.open(fileobj=f)`.
- TC-E3 — `generate_wrappers.py --check` under the locale of D5, with the streams of that locale →
  exit 0 and `OK`. On the base it exits 1 with `UnicodeDecodeError`. Without R5 it exits 1 with
  `UnicodeEncodeError` on Linux and macOS; `cp1252` of the Windows runners encodes the dash.
- TC-E4 — the tests of the Windows jobs of R3 pass under `PYTHONIOENCODING=cp1252` on this
  machine, and the gates of `framework-gates.yml` that run here pass.
- TC-E5 — `calculate_roi.py` with a `cp1252` stream → exit 0 and the report. On the base it exits
  1.
- TC-E6 — each Windows job of `framework-gates.yml` has the step of R6.
- TC-E7 — a git tree in a temporary directory → the listing of R2 takes a new file. It takes no
  test, eval, file of a virtualenv, ignored file or tracked file gone from the work tree.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. The 58 calls of evals and the 287 calls of tests (§0, item 2). The installer copies `evals/`
   and `tests/` into a project, so a consumer can run them on Windows.
2. The check is static and does not resolve names.
   - It passes a mode or an encoding inside `**kwargs`, an `X.open` whose mode is a variable,
     `Path.read_text(p)` called on the class, `fdopen` imported by name, and `_io.open(p, "w")`
     through an alias of `io`.
   - Under D7 it passes the text modes of other modules: `gzip.open(p, "rt")`,
     `bz2.open(p, "wt")` and `codecs.open(p, "r")` take the codec of the locale.
   - It reports `self.open()` and any other `X.open` with no argument as `Path.open`.
3. Text that a subprocess returns with `text=True` and no `encoding=` is decoded in the codec of
   the locale; R2 does not read `subprocess` calls.
4. The rule of R3 is a step of the developer. The Windows jobs of CI run the same tests under the
   code page of the runner.
5. On Windows, `generate_wrappers.py` without `--check` writes its wrappers with CR LF line ends;
   `--check` reads them with universal newlines and reports no drift.
