# TASK 143 — [LIGHT] The anchor registry names the sections of a Light TASK (WI-63)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 143 |
| Slug | light-task-anchors |
| Type | Light Mode (D1) |
| Source | WI-63, option 1; the operator's request of 2026-11-07 |
| Base revision | `7d7746669ad5ee7c453afdba44bf0749abb2808d` |
| Closes | WI-63, MR-2 |
| Archive name | `task-143-light-task-anchors.md` |
| Revision | 7 |

**Request.** The operator chose option 1 of WI-63 and `/light`.

**Finding.** A Light TASK has the sections Decisions, Requirements, Files and Out of scope.
The registry of `documentation-standards` §4.4 names no anchor for them, and
`02_analyst_prompt.md` says to never invent one. 28 archived tasks of `docs/tasks/` carry
`contract:requirements` or `contract:out-of-scope`. TASK 141 removed four invented anchors by
hand.

**Revision 2** follows the code review of cycle 1: CHANGES REQUESTED, with two MAJOR, four
MINOR and eight NIT findings, none BLOCKING. The fix pass:
- the MAJOR M1: the living-TASK test no longer requires an anchor, since §4.3 keeps anchors
  optional on read; a literal test proves its detector;
- the MAJOR M2: the index line of WI-63 moves to `## Closed`;
- the detector follows the lookup rule of §4.3, a whole line after stripping whitespace; it also
  skips fenced blocks, by this task's choice;
- the rows name `docs/TASK.md` with no qualifier; the analyst prompt names the section of each
  anchor, and says that a standard TASK with such a section uses the same anchor.

**Revision 3** follows cycle 2: APPROVED, with five MINOR and eleven NIT findings. They are fixed
in place with no review round 3, under the operator's standing rule of 2026-10-16. Two NITs stay:
a no-space spelling of an anchor, and the `—` consumer that no test pins.
- a fence closes only on its own character and length, with nothing after it (CommonMark);
- the test reuses `ANCHOR_LITERAL` and fails on a repeated anchor;
- §4.3 licenses an anchor for a section that a template or a prompt emits; the analyst prompt
  allows no anchor outside the list, and its standard-mode block names the Light anchors.

**Revision 4.** The retro of this task filed MR-2: `plan_gantt.py` ends with
`UnicodeEncodeError` on a `cp1252` stream when its report holds the `→` of a critical path. The
operator asked to fix it at once (D5, R5).

**Revision 5** follows the narrow review of the MR-2 fix: CHANGES REQUESTED, with one MAJOR, one
MINOR and nine NIT findings. The MAJOR: residual 4 was half wrong. `lint_mermaid.py` crashed on a
`cp1252` stream before a finding's hint, the class of MR-2, also on native Windows. It is fixed
here the same way, with TC-E9; residual 4 is gone. The MR-2 resolution corrects its body: only
the preview of `plan_gantt.py` crashed.

**Revision 6** follows a second narrow review, on the operator's request: APPROVED, with three
MINOR and six NIT findings, fixed in place:
- the same defect in `evals/grade_figures.py` and `evals/selftest_figure_evals.py`: both print a
  `Δ_H`. Both escape now, with TC-E10 for the grader; the committed report of campaign
  `2026-10-opus55-xhigh-r1` takes the new SHA-256 of `grade_figures.py`, as commit `3a6e07e` did;
- the scope text of the lint defect covers any character outside the codec, in every output mode;
- three tests decode the output of their child explicitly; a docstring gives the new counts.

**Revision 7.** On the operator's request of 2026-11-08, `docs/ARCHITECTURE.md` §8 Rule 6 states
the stream convention; residual 4 is gone (D6, R6).

<!-- contract:decisions -->

## 1. Decisions

- D1, 2026-11-07, operator: `/light`. The run has the edit, its pinning tests, the test run and
  one code reviewer in at most two cycles. It has no meta-audit and no security audit: the
  anchor change runs nothing, and D5 covers the scripts that it changes.
- D2, 2026-11-07, operator: option 1 of WI-63. §4.4 registers `contract:decisions`,
  `contract:requirements`, `contract:files` and `contract:out-of-scope` for `docs/TASK.md`, with
  no consumer.
- D3, orchestrator: the archived tasks stay as they are; an archive is not rewritten.
- D4, orchestrator: the framework release is v3.56.3. The commit waits for the operator.
- D5, 2026-11-07, operator: MR-2 is fixed in this task, and with it the same defect of
  `lint_mermaid.py`, `grade_figures.py` and `selftest_figure_evals.py`. The fix changes four
  scripts; it adds no input and no dependency, so the run has no security audit. Two narrow
  review rounds check it; the operator asked for the second.
- D6, 2026-11-08, operator: ARCHITECTURE §8 states the convention that the scripts of TASK 139
  and of D5 follow, as Rule 6.

<!-- contract:requirements -->

## 2. Requirements

- **R1** `documentation-standards` §4.4 (v1.8 → v1.9) has one row per anchor of D2. Each row
  names `docs/TASK.md` as the document, the section, and the consumer `—`.
- **R2** The Light Mode Bypass of `02_analyst_prompt.md` names the anchor of each section of a
  Light TASK: `contract:meta`, `contract:decisions`, `contract:requirements`, `contract:files`,
  `contract:acceptance` and `contract:out-of-scope`. A standard TASK with such a section uses
  the same anchor.
- **R3** `tests/test_mermaid_wiring.py::TestDocumentationStandards` fails:
  - when §4.4 lacks a row of D2;
  - when `02_analyst_prompt.md` names an unregistered anchor;
  - when `docs/TASK.md` carries an unregistered or a repeated anchor, by the lookup rule of
    §4.3, outside fenced blocks. A TASK with no anchor passes.
- **R4** WI-63 is `done` in its record, and its index line stands under `## Closed` of
  `docs/BACKLOG.md`. `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md` and `README.ru.md` carry
  v3.56.3.
- **R5** `plan_gantt.py` escapes on stdout and stderr what the codec of the stream cannot
  encode, as TASK 139 did for `generate_wrappers.py`:
  - `tests/test_text_encoding.py` TC-E8 runs it on `PLAN_EXAMPLE.md` with a `cp1252` stream and
    expects exit 0 and the critical path `1.1 \u2192 1.2`;
  - `tests/test_mermaid_wiring.py` decodes the output of the `plan_gantt.py` child explicitly;
  - MR-2 is `fixed` in its record and in `docs/KNOWN_ISSUES.md`;
  - `lint_mermaid.py` escapes the same way: TC-E9 runs it on a `cp1252` stream, and
    `test_lint_mermaid.py` decodes the output of its child explicitly;
  - `evals/grade_figures.py` and `evals/selftest_figure_evals.py` escape the same way: TC-E10
    runs the grader on a `cp1252` stream, and the selftest passes under `cp1252`. The committed
    report of campaign `2026-10-opus55-xhigh-r1` records the new SHA-256 of the grader;
    `selftest_figure_evals.py` TC-ME-22 passes.
- **R6** `docs/ARCHITECTURE.md` §8 Rule 6: a script that writes to stdout or stderr text it does
  not fully control calls `reconfigure(errors="backslashreplace")` on both streams, first in
  `main()`, with no `encoding=`. A test that starts a script decodes its output explicitly. The
  rule names its enforcement and the gap: no check finds a script that lacks the call.

<!-- contract:files -->

## 3. Files

- `.agent/skills/documentation-standards/SKILL.md`;
- `System/Agents/02_analyst_prompt.md`;
- `tests/test_mermaid_wiring.py`, `tests/test_text_encoding.py`;
- `.agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py`, `lint_mermaid.py`,
  `tests/test_lint_mermaid.py`, `tests/test_lint_mermaid_package.py`;
- `.agent/skills/mermaid-authoring-guidelines/evals/grade_figures.py`,
  `selftest_figure_evals.py`, `corpus/2026-10-opus55-xhigh-r1/report.json`;
- `tests/test_allow_listed_imports.py`;
- `docs/ARCHITECTURE.md`;
- `docs/issues/mr-2-*.md`, `docs/KNOWN_ISSUES.md`;
- `docs/backlog/wi-63-*.md`, `docs/BACKLOG.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`, `README.ru.md`;
- `docs/TASK.md`; the archive of TASK 142.

<!-- contract:acceptance -->

## 4. Acceptance

- TC-1 — `tests/test_mermaid_wiring.py` → pass. It fails on each of these plantings:
  - a row of D2 is removed from §4.4;
  - `02_analyst_prompt.md` names `<!-- contract:invented -->`;
  - `docs/TASK.md` carries `<!-- contract:invented -->`, also indented.

  A `docs/TASK.md` with no anchor, or with that anchor inside a fenced block, passes.
- TC-2 — `python3 tests/run_tests.py` → pass.
- TC-3 — `validate_skill.py` on `documentation-standards`, `check_prompt_references.py` and
  `smoke_workflows.py` → pass.
- TC-4 — `scan_register.py` on the edited text → no warn-level finding that this run adds.
- TC-5 — the reproduction of MR-2 → pass; `tests/test_text_encoding.py` → pass, also under
  `PYTHONIOENCODING=cp1252`. TC-E8, TC-E9 and TC-E10 fail on the scripts without the escape.
  The tests of `mermaid-authoring-guidelines` and `selftest_figure_evals.py` pass under
  `PYTHONIOENCODING=cp1252`.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. The 28 archived tasks keep their anchors (D3). Each carries some of the four, now registered:
   `contract:out-of-scope` 27 of them, `contract:decisions` 13, `contract:requirements` 9.
   Two other anchors stay unregistered: `contract:constraints` in the archive of TASK 118 and
   `contract:measurements` in that of TASK 133.
2. No gate keys on the four anchors; their consumer is `—`. `archive_protocol.py` ends the Meta
   region at the next `<!-- contract:` comment, so `contract:decisions` now ends it earlier;
   `parse_task_meta` returns the same values.
3. The `—` of the `contract:meta` row predates this task: `archive_protocol.py` reads that
   anchor.
4. No check finds a script that lacks the call of Rule 6; the TC-E tests cover four scripts.
5. Under a simulated `PYTHONIOENCODING=cp1252`, `test_allow_listed_imports.py` fails in
   `artifact-formalizer/scripts/selftest_scan.py`: it decodes the output of its child with the
   codec of the locale, UTF-8 there. On native Windows both sides take `cp1252`. That skill is
   outside this diff, and no Windows job runs the file.
