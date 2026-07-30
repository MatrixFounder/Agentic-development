# Technical Specification: unit tests for `skill-spec-validator`

### 0. Meta Information
- **Task ID:** 092
- **Slug:** spec-validator-unit-tests

## 1. General Description

`skill-spec-validator` is the mechanical gate of `/vdd-enhanced`: mode `task` asserts `TASK.md`
carries an RTM, mode `plan` asserts every RTM ID is referenced in `PLAN.md`. It ships **zero tests**.
Both matchers had drifted from the convention the repo actually writes and failed on 100% of shipped
artifacts across ≥2 prior "fixes" — undetected until a manual corpus run in TASK 090, because
nothing mechanically re-checks a matcher against the corpus it governs. Filed as **WI-1**
(`docs/backlog/wi-1-skill-spec-validator-unit-tests.md`, opened 2026-07-20, effort S).

The failure mode is specific and worth naming: a regex gate is **silently satisfiable in both
directions**. Too strict, it never fires and the gate is dead (the state TASK 090 found); too loose,
it passes anything and the gate is theatre. Unit fixtures alone catch neither drift, because a
future author will re-tighten the regex and update the fixtures to match. What catches it is a test
anchored to the **shipped corpus** (`docs/tasks/`, `docs/plans/`) rather than to invented strings.

Measured baseline, taken now (2026-07-30) with the live validator:

| Probe | Count |
|---|---|
| `docs/tasks/*.md` carrying an RTM-ish heading (independent loose probe) | 21 |
| …matched by `RTM_HEADER` | 21 |
| …passing full `--mode task` (heading + non-empty table + `ID`/`Requirement` columns) | 20 |
| exact-slug `plan-<id>-<slug>.md` ↔ `task-<id>-<slug>.md` pairs | 26 |
| …passing `--mode plan` | 13 |

Scope is **tests plus the SKILL.md sections the validator warns about** — no behavior change to
`validate.py`. Where the corpus disagrees with the gate, this task records the disagreement; it does
not silently move the gate to make it green (`developer-guidelines`: no unsolicited refactoring, and
a gate loosened to fit a nonconforming artifact is the original defect running backwards).

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | Every RTM heading shape the repo actually ships is matched by `RTM_HEADER` — the 8 distinct forms found in `docs/tasks/` (h2/h3, `N.`/`N)` section numbers, trailing `(RTM)`, bare `Requirements (RTM)`, and `Acceptance Criteria (RTM)`). | Unit test per shape, fixtures copied verbatim from the corpus. |
| R2 | Shapes that must NOT match are pinned: h1, h5+, a heading naming neither "Requirements Traceability" nor `RTM`, and a prose line mentioning the RTM outside a heading. | Negative unit tests. |
| R3 | `--mode task` table checks hold: missing table → exit 1; table without `ID`/`Requirement` columns → exit 1; valid table → exit 0 reporting the row count. | Unit tests asserting exit code AND message. |
| R4 | The bypass token (`BYPASS_VALIDATION` in square brackets) short-circuits both modes to exit 0 **before** any RTM check, and it is a bare substring test anywhere in `TASK.md` — so a spec that merely *mentions* the token disables its own gate. Both facts are pinned. | Unit test per mode, using content that would otherwise fail, plus a test where the token appears only inside prose. |
| R5 | `--mode plan` accepts an ID referenced in a `## Step N — … (R1)` heading and in a `- [ ] R1 …` bullet, and reports the uncovered ones by name otherwise. | Unit tests for both reference styles + the missing-ID message. |
| R6 | Whole-token boundary: `R10` in the plan does not satisfy RTM id `R1`; hyphenated ids (`R-065-1`, `TF-X-7`) are matched whole; markdown noise around an id (`**R1**`, `` `R1` ``, `[R1]`) is normalized. | Unit tests, incl. the R1-vs-R10 case named in WI-1. |
| R7 | `parse_markdown_table` behavior is pinned: separator row skipped, escaped `\|` preserved, column-count mismatch row skipped, table ends at the first non-pipe line, and a table under a LATER `##` section does not leak into the RTM block. | Unit tests on the parser + section slicing. |
| R8 | Missing input files exit 1 in both modes; `--mode plan` with one file is a usage error. | CLI-level tests. |
| R9 | **Corpus anti-drift guard**: an independent loose probe over `docs/tasks/*.md` finds the RTM-ish headings, and `RTM_HEADER` must match every one; discovering zero headings is itself a failure. | Corpus test over real files. |
| R10 | **Corpus liveness floor**: at least 15 shipped tasks pass `--mode task` and at least 10 exact-slug plan/task pairs pass `--mode plan`. A matcher that dies again collapses these to ~0. | Corpus test with named floor constants + explanatory comment. |
| R11 | The suite runs stdlib-only, offline, from the skill dir, and a zero-test discovery run fails rather than reporting green. | `python3 -m unittest discover -s tests` + a guard assertion. |
| R12 | `SKILL.md` gains the four Execution-Policy sections the validator warns about (Execution Mode, Script Contract, Safety Boundaries, Validation Evidence) naming the test command. | `validate_skills.py` reports the skill warning-free; 45/45 overall. |

## 3. Non-functional Requirements
- **Performance:** whole suite well under a second; the corpus tests read ~140 small files.
- **Security:** tests are read-only over the repo; no network, no writes outside `tempfile`.
- **Compatibility:** stdlib `unittest` only (no pytest dependency), Python 3.9+ syntax, mirroring
  `run-feedback`'s suite so one `discover` idiom covers both skills.

## 4. Constraints and Assumptions
- `validate.py` calls `sys.exit()` inside its two entry points; tests therefore assert on
  `SystemExit.code` with stdout captured. **No refactor to return-codes** — WI-1 asks for tests, and
  a testability refactor of a live gate is a separate, riskier change.
- The corpus floors (R10) are **canaries, not targets**: they are set below today's counts (20 and
  13) so that ordinary artifact churn does not fail the suite, while a dead matcher does.
- Sub-task files (`task-NNN-MM-slug.md`) legitimately carry no RTM — the parent TASK owns it — so
  the corpus tests select by "has an RTM heading", never "every file in the directory".

## 5. Open Questions / Observations (recorded, not fixed here)
- `docs/tasks/task-088-known-issues-vdd-fixes.md` uses `| ID | Finding | Fix | Verify |` and so fails
  the `ID`/`Requirement` column check — the one corpus artifact that does. Recorded as an
  observation for the owner; **not** fixed here, and the column contract is pinned as-is by R3.
- **The bypass is a bare substring anywhere in the file.** Writing the token into a spec — as the
  first draft of *this* very spec did — silently switches the gate off; the run prints
  "Validation bypassed" and exits 0, which reads like a pass. Pinned by R4 as current behavior, not
  changed here: tightening it (e.g. to a fenced marker or a heading) is a behavior change to a live
  gate and belongs to the owner.
- 13 of 26 exact-slug plan/task pairs fail `--mode plan`, mostly with genuinely unreferenced RTM ids
  — the gate doing its job on historical artifacts, not a matcher fault. Left alone.
