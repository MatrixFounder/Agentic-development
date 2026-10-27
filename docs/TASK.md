# TASK 129 — The tests run from any directory, and the dependency advisories of the TASK 128 retro close

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 129 |
| Slug | test-paths-and-dependency-advisories |
| Type | Standard pipeline (the operator's choice, 2026-10-26) |
| Source | the retro of TASK 128: three findings to fix at once, with no ledger record (D1) |
| Base revision | `2a7d11cbf0a4f82153259dfcae9344239d9e9064` |
| Archive name | `task-129-test-paths-and-dependency-advisories.md` |
| Revision | 6 |

**Revision 2** applies m1 to m8 and N1 to N8 of the task review, which approved revision 1.
**Revision 3** corrects the command of the measurement in §1 and §8 (code review of Task 129.1).
**Revision 4** records D9 and changes R6.4, R6.5, §8 and the R6 row (Task 129.3).
**Revision 5** answers the code review and the security audit of Task 129.3. D4 moves to `katex`
0.18.10, with R3.1 and A4; D9, R6.4 and R6.5 name every copy that the page runs; §8 states the
advisories of each copy.
**Revision 6** answers round 2 of the code review of Task 129.3: the closing condition of R6.4 per
copy, and the wording of D9 on the sanitizer.

**Request.** At the retro of TASK 128 the operator chose three findings before that task and
answered "это можно все сразу починить". Asked how, they chose one task for all of them, npm
included (D2). The Windows port of the archive chain follows as TASK 130.

A coordinate into a file that this task edits carries the pin `@2a7d11c`, the base revision.

<!-- contract:problem -->

## 1. Problem

1. **pytest from `tests/`.** `python3 -m pytest` run from `tests/` stops at a collection error.
   With `--continue-on-collection-errors` it gives `5 failed, 719 passed, 1 error`:
   - `tests/test_tool_runner.py:10@2a7d11c` `from System.scripts import tool_runner` finds no
     package;
   - the four tests of `tests/test_tool_runner_security_contract.py` read
     `Path("System/scripts/tool_runner.py")`;
   - `tests/test_schemas_stub.py` loads `.agent/tools/schemas.py` by a relative path.
2. **pytest 9.0.2.** `requirements-dev.txt` pins `pytest==9.0.2`, which CVE-2025-71176
   (GHSA-6w46-j5rx-g56g) covers.
3. **The renderer lockfiles.** `npm audit --package-lock-only` of each lockfile under
   `.agent/skills/mermaid-authoring-guidelines/assets/renderers/` reports:
   - critical GHSA-cg2g-xh64-v4q7, high GHSA-mrv2-3pqr-j5jr and low GHSA-c6gr-qvv4-5v3f in
     `dompurify` 3.4.16;
   - high GHSA-mrhx-c7xc-m3w5 in `zod` 3.25.76, through `chromium-bidi` 17.0.2 of puppeteer 25.12.0;
   - low GHSA-238p-pmpm-9mq7 in `katex` 0.16.47 through mermaid, open as WI-41. The low entries
     of the mermaid plugins of v11 and v12 come through mermaid and `katex` too.
4. **Statements of the old state.** `references/renderer-facts.md` RF-22 and §10.7 of
   `docs/ARCHITECTURE.md` say that `npm audit` reports no advisory, or no high one.
5. **Two small defects.**
   - `docs/ARCHITECTURE.md:120@2a7d11c` `Uses file locking on` and line 215 name the state, not
     its lock file `latest.yaml.lock`.
   - `tests/_scratch.py:69@2a7d11c` `os.kill(pid, 0)` sends `CTRL_C_EVENT` on Windows, where the
     signal number 0 is that event. The docstring of the module says that the next sweep removes
     the directory of a killed run, which on Windows does not happen.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | Tests independent of the working directory | yes | the import; the directory of `tool_runner`; two paths; no source change | A1, A11 |
| R2 | pytest 9.1.1 | yes | the pin; the project venv; CI | A2, A9 |
| R3 | No critical or high advisory in the renderer lockfiles | yes | `dompurify`; `katex`; puppeteer; renders compared; the pins | A3, A4, A5, A9 |
| R4 | The lock file and the audit result in the architecture | yes | lines 120 and 215; §10.7; TC-C7 | A6 |
| R5 | No signal from the stale sweep on Windows | yes | no `os.kill`; alive by default; the docstring; a test | A7 |
| R6 | Records | yes | the changelogs; RF-22; the setup header; WI-41; the bundled copies | A8 |
| R7 | A security review of the lockfile diff | yes | new packages; install scripts; sources | A10 |

## 3. Requirements

### R1 — tests independent of the working directory

- **R1.1** `tests/test_tool_runner.py` appends the repository root to `sys.path` when it is absent,
  before it imports `System.scripts`. The root is `Path(__file__).resolve().parents[1]`.
- **R1.2** `TestToolRunner.setUp` registers a cleanup that changes back to the current directory,
  then changes into that root.

  **Why.** `tool_runner.execute_tool` takes `Path.cwd()` as the repository root by design.
- **R1.3** `tests/test_tool_runner_security_contract.py` and `tests/test_schemas_stub.py` read
  their files under that root.
- **R1.4** No file of `System/scripts/` or `.agent/tools/` changes.

### R2 — pytest 9.1.1

- **R2.1** `requirements-dev.txt` pins `pytest==9.1.1`, the current release on 2026-10-26 (D7).
- **R2.2** The project's `.venv` installs `requirements-dev.txt` again.

### R3 — the renderer lockfiles

- **R3.1** The `overrides` of each renderer's `package.json` set `dompurify` to `3.4.17` and
  `katex` to `0.18.10` (D4).
- **R3.2** Each renderer runs puppeteer `25.16.0`: a dependency of v11 and v12, the override of
  v10.
- **R3.3** `npm install --package-lock-only --ignore-scripts` writes each lockfile. The versions
  of `mermaid` and `@mermaid-js/mermaid-cli` stay as pinned: 10.9.8 and 10.9.1, 11.17.2 and
  11.17.0, 12.1.0 and 12.0.0.
- **R3.4** `scripts/setup_renderers.sh --forward` installs the new lockfiles into a temporary
  `MERMAID_RENDER_HOME`, and the smoke render of each install passes. The browser is the cached
  chrome-headless-shell 150.0.7871.24, whose tree hash `assets/renderers/browsers.json` records.
  `browsers.json` and `BROWSER_MIN_BUILD` stay unchanged.
- **R3.5** The renders are compared (D8):
  1. before any lockfile change, a fresh install of the base lockfiles in a temporary home renders
     the figures with `render_check.py --forward --json`;
  2. the figures are those of the nine `references/*.md` that hold a mermaid fence, and one
     probe figure with a KaTeX label, written outside the repository;
  3. after the change, a fresh install of the new lockfiles in a second temporary home renders
     the same figures;
  4. each figure keeps its status, and each render of it keeps its status and its metrics.
- **R3.6** `PUPPETEER` of `scripts/tests/test_setup_renderers.py` names `25.16.0` for each tag.
- **R3.7** A difference of R3.5 in a figure with a KaTeX label drops the override of `katex`;
  WI-41 then stays open. Any other difference, or a failed smoke render, stops the run for the
  operator.

### R4 — the lock file and the audit result in the architecture

- **R4.1** `docs/ARCHITECTURE.md:120@2a7d11c` and line 215 name `.agent/sessions/latest.yaml.lock`
  as the file that the lock is taken on. Both keep `fcntl` and `msvcrt`, which TC-C7 of
  `tests/test_session_state_contract.py` reads.
- **R4.2** §10.7 names the overrides of each lockfile and the result of `npm audit` measured in this
  task.
- **R4.3** No other line of `docs/ARCHITECTURE.md` changes.

### R5 — no signal from the stale sweep on Windows

- **R5.1** `_pid_alive` of `tests/_scratch.py` returns `True` on Windows (`os.name == "nt"`)
  without a call of `os.kill`.
- **R5.2** On POSIX it keeps its behaviour.
- **R5.3** The docstring of the module states that on Windows the stale sweep removes no session
  directory, and that the `atexit` handler removes the directory of each normal exit.

### R6 — records

- **R6.1** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.48.1. It tells the operator to run
  `setup_renderers.sh` again: `render_check.py` refuses an install whose lockfile stamp is stale.
- **R6.2** RF-22 of `references/renderer-facts.md` states the new overrides, the entry counts and
  the result of `npm audit`, with the date of the measurement. RF-21 and the record of WI-30 stay
  as they are: TC-05 of `tests/test_disclosure_rule.py` pins a paragraph of each.
- **R6.3** The header of `scripts/setup_renderers.sh` and the description of
  `assets/renderers/v10/package.json` name puppeteer 25.16.0 and the overrides.
- **R6.4** WI-41 stays open (D9). A progress blockquote at the top of its body names:
  - the overrides of this task and the audit result;
  - each copy of DOMPurify and KaTeX that the render page runs, by tag and package, with its
    version and the advisories that cover it;
  - the condition of its closing: each DOMPurify copy that the page runs is 3.4.17 or newer, each
    KaTeX copy is 0.18.2 or newer, and the figure renders pass.

  Its index line in `docs/BACKLOG.md` names the progress.
- **R6.5** The changelog entry, RF-22, the setup header and §10.7 of `docs/ARCHITECTURE.md` state
  each copy of DOMPurify and KaTeX that the render page runs, by tag and package, with its version
  (D9).

### R7 — a security review of the lockfile diff

- **R7.1** A security auditor reviews the diff of the three lockfiles: each added or removed
  package, each `hasInstallScript`, each `resolved` host, and each `integrity`.
- **R7.2** The review checks again the claim of `setup_renderers.sh:13@2a7d11c` `The only install
  script in the three lockfiles is puppeteer's`.

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — A developer runs pytest from `tests/`

- **Actors.** A developer, or an agent under the committed rule `python3 -m pytest`.
- **Precondition.** The interpreter holds pytest; the working directory is `tests/`.
1. The developer runs `python3 -m pytest`.
2. pytest collects every module of `tests/`.
3. `TestToolRunner` changes into the repository root for each test, and back.
- **Alternative 1a.** The run starts at the root with `PYTHONPATH=.`, as CI runs it: the same tests
  pass.
- **Postcondition.** Every collected test passes.

### UC-2 — The operator installs the renderers

- **Actors.** The operator; `setup_renderers.sh`; the npm registry.
- **Precondition.** The puppeteer cache holds chrome-headless-shell 150.0.7871.24.
1. The operator runs `setup_renderers.sh`, with `--forward` for v12.
2. `npm ci --ignore-scripts` installs each lockfile.
3. The script accepts the cached browser by its tree hash, and runs a smoke render.
- **Alternative 2a.** The registry does not answer: the script exits 1 and names the step.
- **Alternative 3a.** No accepted browser is cached: the script exits 1 and names the step.
- **Alternative 3b.** The smoke render fails with build 150: the script exits 1. A browser of
  build 156.0.8078.47, which puppeteer 25.16.0 pins, needs a tree hash that the operator vouches
  for.
- **Postcondition.** `render_check.py` renders with each install.

### UC-3 — A test run on Windows sweeps stale scratch

- **Actors.** pytest on Windows; the hook of `tests/conftest.py`.
- **Precondition.** `tests/.scratch/` holds a session directory of another process.
1. `sweep_stale_sessions` asks `_pid_alive` about its pid.
2. `_pid_alive` answers `True` and sends no event.
- **Alternative 1a.** On POSIX `_pid_alive` sends signal 0 as before, and a dead process's directory
  goes.
- **Postcondition.** On Windows the directory stays, and no process gets `CTRL_C_EVENT`.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — from `tests/`, `python3 -m pytest` and `.venv/bin/python -m pytest` exit 0. The pytest
  step of CI exits 0 from the root.
- **A2** — `requirements-dev.txt` holds `pytest==9.1.1`, and `.venv/bin/python -m pytest
  --version` prints 9.1.1.
- **A3** — `npm audit --package-lock-only` of each lockfile reports no critical and no high
  advisory, and no GHSA-238p-pmpm-9mq7 while the override of `katex` stands.
- **A4** — each lockfile keeps the `mermaid` and `@mermaid-js/mermaid-cli` of R3.3, and holds
  `dompurify` 3.4.17, `katex` 0.18.10 and puppeteer 25.16.0.
- **A5** — `setup_renderers.sh --forward` exits 0 in a temporary home. The comparison of R3.5 finds
  no difference in a status or a metric, the probe figure included.
- **A6** — lines 120 and 215 name `latest.yaml.lock`, §10.7 states the measured audit, and TC-C7
  passes.
- **A7** — TC-S1 of `tests/test_scratch_hygiene.py`: `os.name` set to `"nt"` around the call
  only, and `os.kill` replaced by a recorder → `_pid_alive` returns `True`, and the recorder holds
  no call; fails when R5.1 is removed. The tests `test_stale_sweep_*` pass (R5.2).
- **A8** — v3.48.1 in both changelogs, RF-22, the setup header and the v10 description as R6
  states; WI-41 as R6.4 states. `scan_register.py` finds no warning on an added line, and
  `tests/test_disclosure_rule.py` passes.
- **A9** — the tests of the skill, `scripts/tests/test_setup_renderers.py` among them, pass. The CI
  run after the operator's push passes every job.
- **A10** — the review of R7 finds no finding of MEDIUM or above.
- **A11** — `git diff 2a7d11c -- System/scripts .agent/tools` prints nothing.

<!-- contract:open-questions -->

## 6. Open questions

None. The operator chose the findings and one task for them (D1, D2).

## 7. Decisions

- **D1**, 2026-10-26, operator, at the retro of TASK 128: three findings are fixed at once, with no
  ledger record. The fourth, the boot read of `latest.yaml` through a committed link, is not in
  this task. The Windows port of the archive chain, which `task-128` named TASK 129, becomes
  TASK 130.
- **D2**, 2026-10-26, operator: one task for all of them, npm included, through the standard
  pipeline. Rejected: `/light` for the small fixes and a second task for npm.
- **D3**, 2026-10-26, orchestrator: puppeteer goes to 25.16.0, the current release. Rejected: an
  override of `zod` to 4.6.7, a major version over the `^3.24.1` that `chromium-bidi` 17.0.2
  requires.
- **D4**, 2026-10-26, orchestrator; 2026-10-27, operator: `katex` goes to 0.18.10 through
  `overrides`, option 1 of WI-41, under the check of R3.5. The release 0.18.10 is the newest of 0.18
  that its publisher does not deprecate. The fix came with 0.18.2. Rejected:
  - 0.18.11, the first choice. Its publisher deprecates it: "Accidentally published with breaking
    changes. Use 0.19.0 instead." (code review of Task 129.3);
  - 0.19.1, a line further from the `^0.16` of the pinned mermaid versions;
  - 0.18.2, an older release of the same line;
  - a move of the mermaid pins, which the render evidence was measured with.
- **D5**, 2026-10-26, orchestrator: on Windows `_pid_alive` answers `True`. Rejected: a probe of the
  process through the Windows API, which no CI run reaches. `tests/.scratch/` is absent after a
  checkout, so the sweep of the Windows jobs meets no session, and `tests/test_scratch_hygiene.py`
  runs on Ubuntu only.
- **D6**, 2026-10-26, orchestrator: R1 changes the three test modules. Rejected: `pythonpath` in a
  new root `pytest.ini`, which changes the import path of every pytest run; a path insert in
  `tests/conftest.py`, which fixes the import only and leaves the working directory of R1.2.
- **D7**, 2026-10-26, orchestrator: pytest goes to 9.1.1, the current release. Measured under 9.1.1
  and Python 3.14: the pytest step of the tooling job gave `582 passed, 2 skipped`, the tests of the
  figure skill `742 passed, 1 skipped`, and a bare run from the root `738 passed`. Rejected: 9.0.3,
  the patch of an older line.
- **D8**, 2026-10-26, orchestrator: R3.5 compares the status and the metrics of each render, the bar
  of RF-22. Rejected: the verdicts alone, which hide a change of size or of a crossing count.
- **D9**, 2026-10-26, operator, after Task 129.3; confirmed on 2026-10-27 with every copy: the
  overrides stay, and WI-41 stays open for the copies of DOMPurify and KaTeX that the render page
  runs. The page takes no script from the packages `dompurify` and `katex`. The copies, measured in
  Task 129.3:

  | Tag | Package that carries the copy | DOMPurify | KaTeX |
  | :--- | :--- | :--- | :--- |
  | v10 | mermaid 10.9.8 | 3.4.2 | 0.16.45 |
  | v11 | mermaid 11.17.2 | 3.4.12 | 0.16.47 |
  | v11 | `@mermaid-js/layout-elk` 0.2.3 | 3.4.12 | 0.16.47 |
  | v11 | `@mermaid-js/mermaid-zenuml` 0.2.3 | 3.3.1 | none |
  | v12 | mermaid 12.1.0 | 3.4.12 | 0.16.47 |
  | v12 | `@mermaid-js/mermaid-zenuml` 1.0.1 | 3.3.1 | none |

  §8 names the advisories of each copy. No release of these packages bundles DOMPurify 3.4.17:
  mermaid 12.2.0, the newest, bundles DOMPurify 3.4.12 and KaTeX 0.18.11. The security audit of
  Task 129.3 rates the exposure LOW:
  - mermaid calls the sanitizer with default options or with `FORBID_TAGS`;
  - the page resolves no host, uses no proxy, and keeps its sandbox;
  - the figures come from the operator and from agents.

  Rejected:
  - closing WI-41 by the letter of its acceptance, which reads the lockfile: the copies that run
    stay;
  - a second record for the copies in the plugins: one record keeps one closing condition per copy;
  - raising v12 to mermaid 12.2.0, which leaves DOMPurify 3.4.12 and moves the render evidence (D4).

## 8. Measurements of this run

- `python3 -m pytest` from `tests/`: exit 2 at the collection error of `tests/test_tool_runner.py`.
  With `--continue-on-collection-errors`: `5 failed, 719 passed, 1 error`, the modules of R1 only.
- `npm audit --package-lock-only` at the base: v10 1 critical, 5 high, 2 low; v11 1 critical,
  4 high, 6 low; v12 1 critical, 4 high, 5 low. The ranges of the three `dompurify` advisories end
  at 3.4.16, so 3.4.17 lies outside each; the critical one starts at 3.4.4. GHSA-238p-pmpm-9mq7
  covers `katex` 0.11.0 to 0.18.1.
- `npm view`, 2026-10-26:
  - `dompurify` 3.4.17 and puppeteer 25.16.0 are the current releases;
  - `katex` 0.18.11 is the newest release of 0.18, and 0.19.1 the current one;
  - puppeteer 25.16.0 pins chrome-headless-shell 156.0.8078.47, and needs node 22.12.0 or newer;
  - its `chromium-bidi` 157.0.8090-0 requires `zod ^4.6.5` and node 22.12.0 or newer.
- The puppeteer cache holds chrome-headless-shell 131, 146, 148 and 150.0.7871.24, and
  `browsers.json` records the tree hash of 150.0.7871.24 only.
- The base renders, a fresh install of the base lockfiles in a temporary home, `--forward`:
  51 figures, `21 pass, 7 unchecked, 23 expected, 0 fail`, in v10, v11 and v12.
- Task 129.3, the bundles: mermaid-cli 10.9.1 loads `mermaid/dist/mermaid.js`, and mermaid-cli
  11.17.0 and 12.0.0 load `mermaid/dist/mermaid.esm.mjs` with its chunks. The version strings in them:
  DOMPurify 3.4.2 and KaTeX 0.16.45 in mermaid 10.9.8; DOMPurify 3.4.12 and KaTeX 0.16.47 in mermaid
  11.17.2 and 12.1.0. mermaid-cli 11 and 12 serve the page `katex/dist/katex.css` and its fonts from
  the package `katex`.
- Task 129.3, the plugins: mermaid-cli 11 and 12 register `@mermaid-js/mermaid-zenuml`, whose
  `zenuml-definition` chunk carries DOMPurify 3.3.1 and loads with a `zenuml` figure. mermaid-cli 11
  loads `@mermaid-js/layout-elk` 0.2.3, whose chunks carry DOMPurify 3.4.12 and KaTeX 0.16.47. The
  page of mermaid-cli 10.9.1 holds no DOMPurify of its own.
- `npm audit` of each copy's version through npm aliases, 2026-10-27:
  - DOMPurify 3.4.2: 13 advisories, among them high GHSA-mrv2-3pqr-j5jr; no critical one;
  - DOMPurify 3.4.12: 5 advisories, among them critical GHSA-cg2g-xh64-v4q7 and high
    GHSA-mrv2-3pqr-j5jr;
  - DOMPurify 3.3.1: 21 advisories, among them high GHSA-mrv2-3pqr-j5jr; no critical one;
  - KaTeX 0.16.45 and 0.16.47: low GHSA-238p-pmpm-9mq7.
- `npm view`, 2026-10-27: the publisher of `katex` deprecates 0.18.11, "Accidentally published with
  breaking changes. Use 0.19.0 instead."; 0.18.10 carries no deprecation.
- `npm view`, 2026-10-26: DOMPurify 3.4.17 was published on 2026-10-12. No mermaid 10 or 11 release
  followed the pinned 10.9.8 and 11.17.2; mermaid 12.2.0 (2026-10-13) bundles DOMPurify 3.4.12 and
  KaTeX 0.18.11.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The boot read of `latest.yaml` through a committed link (D1).
- A browser of build 156.0.8078.47: only Alternative 3b of UC-2 brings it to the operator.
- The pytest of the global interpreter, which the operator's rule keeps out of reach of `pip`.
- A probe of a process on Windows in `tests/_scratch.py` (D5).
- The Windows port of the archive chain — TASK 130.
