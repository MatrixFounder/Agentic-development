# PLAN 129 — The tests run from any directory, and the dependency advisories of the TASK 128 retro close

**TASK:** [docs/TASK.md](../tasks/task-129-test-paths-and-dependency-advisories.md) (revision 6) · **Covers:** R1–R7 · **Acceptance:** A1–A11.

**Revision:** 4, per the code review of Task 129.3 and TASK D4 and D9 of 2026-10-27: `katex` 0.18.10,
and the records name each copy of DOMPurify and KaTeX that the page runs, by tag and package.
Revision 3 followed TASK D9 (R6.4, R6.5). Revision 2 answered the plan review, which approved
revision 1.

<!-- contract:sequence -->

## Task Execution Sequence

### Rules of the run

- A coordinate into a file that this plan edits carries the pin `@2a7d11c`, the base revision.
- Every Python run passes `-B` or sets `PYTHONDONTWRITEBYTECODE=1`.
- Every pytest run passes `-p no:cacheprovider`.
- No tool input holds an escape of the form backslash, `u`, four hex digits. Code builds the text
  that needs one.
- After each write of a file of the change, a byte scan finds in it:
  - no control character but LF;
  - no U+2028 or U+2029;
  - no lone surrogate and no byte-order mark.
- Each `npm` command passes `--ignore-scripts` where it installs, and sets `npm_config_cache` to a
  directory of the session scratchpad. No `npm` command writes to `~/.npm`.
- The install homes, the renders and the evidence files lie in the session scratchpad, outside
  the repository.
- R1 and R5 are defects. Task 129.1 states the expected failure of each red test, and its red run
  compares it with the actual failure (`tdd-strict`, steps 1 and 2).
- The operator commits and pushes.

**Why.** TASK 127 measured one such escape decoded into the character it names.

### Stage 1: Tests first (Red)

- **Task 129.1** — [STUB CREATION] the tests of the target state, red against the base
  - Use Cases: UC-1, UC-2, UC-3
  - Description File: `docs/tasks/task-129-01-red-tests.md`
  - Priority: Critical
  - Dependencies: none
  - [R1] the red run of `python3 -m pytest` from `tests/`
  - [R3] `PUPPETEER` names 25.16.0 (R3.6); TC-L1 reads the three manifests and lockfiles
  - [R5] TC-S1 of `tests/test_scratch_hygiene.py`

### Stage 2: The fixes (Green)

- **Task 129.2** — [LOGIC IMPLEMENTATION] the test paths, pytest 9.1.1 and `_pid_alive`
  - Use Cases: UC-1, UC-3
  - Description File: `docs/tasks/task-129-02-test-paths-pytest-pid-alive.md`
  - Priority: High
  - Dependencies: Task 129.1
  - [R1] the three test modules read from the repository root
  - [R2] `pytest==9.1.1`, installed in the project venv
  - [R5] `_pid_alive` answers `True` on Windows without a call of `os.kill`

- **Task 129.3** — [LOGIC IMPLEMENTATION] the renderer lockfiles
  - Use Cases: UC-2
  - Description File: `docs/tasks/task-129-03-renderer-lockfiles.md`
  - Priority: High
  - Dependencies: Task 129.2
  - [R3] the overrides, the lockfiles, the setup and the render comparison
  - [R6] R6.3 and R6.5: the setup header and the v10 description
  - [R7] the security review of the lockfile diff

### Stage 3: Records

- **Task 129.4** — the records and the check of the architecture
  - Use Cases: UC-2
  - Description File: `docs/tasks/task-129-04-records.md`
  - Priority: Medium
  - Dependencies: Task 129.3
  - [R4] §10.7 against the audit of Task 129.3, and TC-C7
  - [R6] R6.1, R6.2, R6.4 and R6.5: the changelogs, RF-22, the progress of WI-41, §10.7

The edits of R4 landed in the Architecture phase. Task 129.4 checks them against the measured
audit.

### Closing: the CI run

After the operator's push, the orchestrator reads the CI run of that commit with `gh run list` and
`gh run view` (TASK A9). It is the first run of pytest 9.1.1 on Python 3.11. A failed job goes to
the operator with its log, and its fix follows in this task.

## Schedule

<!-- contract:schedule -->

```json
{
  "schema": "plan-schedule/v1",
  "tasks": [
    {"id": "129.1", "title": "Red tests", "stage": "Stage 1", "est": 1, "deps": [], "status": "done"},
    {"id": "129.2", "title": "Test paths, pytest, _pid_alive", "stage": "Stage 2", "est": 2, "deps": ["129.1"], "status": "done"},
    {"id": "129.3", "title": "Renderer lockfiles", "stage": "Stage 2", "est": 3, "deps": ["129.2"], "status": "done"},
    {"id": "129.4", "title": "Records", "stage": "Stage 3", "est": 2, "deps": ["129.3"], "status": "done"}
  ]
}
```

<!-- generated:plan-gantt-start -->
<!-- generated:plan-gantt-end -->

<!-- contract:coverage -->

## Use Case Coverage

| Use Case | Tasks |
| :--- | :--- |
| UC-1 | 129.1, 129.2 |
| UC-2 | 129.1, 129.3, 129.4 |
| UC-3 | 129.1, 129.2 |

## Requirement Coverage

| Requirement | Tasks | Acceptance |
| :--- | :--- | :--- |
| R1 | 129.1, 129.2 | A1, A11 |
| R2 | 129.2; the CI run | A2, A9 |
| R3 | 129.1, 129.3; the CI run | A3, A4, A5, A9 |
| R4 | Architecture phase; 129.4 checks it | A6 |
| R5 | 129.1, 129.2 | A7 |
| R6 | 129.3 (R6.3, R6.5), 129.4 | A8 |
| R7 | 129.3 | A10 |

## Base evidence

`<scratch>` is the session scratchpad, and `<logs>` is `<scratch>/logs-129`. The base lockfiles were
installed in the temporary home `<scratch>/render-base` before any lockfile change.

- The nine `references/*.md` that hold a mermaid fence, `render_check.py --forward --json`:
  51 figures, `21 pass, 7 unchecked, 23 expected, 0 fail` (TASK §8). File:
  `<logs>/render-base2.json`.
- The KaTeX probe figure `<scratch>/probe-katex/katex-probe.md`, a flowchart with two math labels,
  by the same command. File: `<logs>/render-base-katex.json`. One figure, status `fail`:
  - `clipped_labels` of one math label in v11, and of both in v12;
  - `font_swap` of one math label in v11.
- A second render of the same 52 figures with the same installs. Files:
  `<logs>/render-base3.json` and `<logs>/render-base3-katex.json`.
  `<scratch>/tools-128/compare_renders.py` finds no difference in a status or a metric.

The probe of the Architecture phase ran on copies of the three manifests, in `<scratch>/probe-129/`:

- `npm audit` of the three regenerated lockfiles reported no advisory;
- the smoke render with chrome-headless-shell 150.0.7871.24 passed for each install.

**Fallback.** When `<scratch>` is lost before the comparison of Task 129.3, the base is rendered
again:
1. a detached worktree at `2a7d11c` runs its `setup_renderers.sh --forward` into a new temporary
   home;
2. `render_check.py` renders the nine files and the probe figure with that home. The text of the
   probe figure stands in Task 129.3, Notes;
3. `compare_renders.py` is written again from its description in Task 129.3.

## Failure paths

- The setup of Task 129.3 exits 1 → the run stops for the operator. The causes are a failed smoke
  render (UC-2 alternative 3b), a registry that does not answer (2a) and no accepted browser (3a).
- `npm audit` of Task 129.3 reports a critical or a high advisory → the run stops for the operator.
- The comparison of Task 129.3 finds a difference in a figure with a KaTeX label only → the katex
  branch of R3.7, below.
- Any other difference of the comparison → the run stops for the operator.
- A review that rejects twice → the run stops for the operator.

On every branch, Task 129.3 runs `npm audit` on the committed lockfiles, and Task 129.4 dates §10.7
and RF-22 by that run (architecture review, MINOR 3).

### The katex branch of R3.7

1. Task 129.3 drops the override of `katex` from the three manifests. It writes the lockfiles,
   installs, renders and compares again.
2. `KATEX` leaves `test_setup_renderers.py`. TC-L1 asserts that no manifest overrides `katex`.
3. A4 holds without `katex` 0.18.10. The review record of Task 129.3 and the changelog entry name
   this deviation.
4. The setup header, the v10 description, the changelog entry and RF-22 name the override of
   `dompurify` only. Each names GHSA-238p-pmpm-9mq7 as the low advisory that stays, under WI-41.
5. Task 129.4 changes two sentences of §10.7:
   - the sentence of the overrides loses its `katex` clause;
   - the sentence of the audit names GHSA-238p-pmpm-9mq7.
6. WI-41 stays open. A progress blockquote at the top of its body states that TASK 129 measured a
   render difference with `katex` 0.18.10 (precedent: PLAN 128 C6).
