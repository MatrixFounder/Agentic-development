# TASK 120 — Stage 2 of framework-upgrade holds its reviews to the TASK and the lines the change touches

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 120 |
| Slug | stage2-review-boundary |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-52 (below); the operator's request of 2026-10-09: "сразу же поправь wi-52" |
| Base revision | `da91d2fefa33242a47356e1b740055e645db5e1e` |
| Closes | WI-52 |
| Archive name | `task-120-stage2-review-boundary.md` |
| Revision | 5 |

**Record.** [WI-52](backlog/wi-52-stage-2-reviews-can-widen-a-framework-upgrade-task-beyond-its-changed-lines.md)

<!-- contract:problem -->

## 1. Problem

Stage 2 of `/framework-upgrade` (§3 step 4) bounds its review rounds, but not their scope. In TASK
119 the reviewers reported findings in code the task did not change, and the run filed two new
backlog records from them. The operator removed both and set the boundary D5 of TASK 119 mid-run.
The workflow does not state that boundary, so the next run starts without it.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Acceptance |
| :--- | :--- | :--- | :--- |
| R1 | Stage 2 states the review boundary | Y | A1 |
| R2 | The pin of §3 step 4 holds the new text | Y | A1, A2 |
| R3 | Documents and records | Y | A3 |
| R4 | Staging | Y | A2, A4 |

<!-- contract:requirements -->

## 3. Requirements

- **R1.1** Stage 2 of `framework-upgrade` §3 step 4 gains one bullet, after **LOW routes of a fixed
  class**, with this text:

  ```text
  - **Boundary.** A review round checks the change against its TASK and the lines it touches. Code
    that the change makes run, or run without a prompt, is among those lines. Any other finding,
    unless the change causes it as a regression, is one line in the audit record, with its
    severity, marked as before the task. Such a finding does not set the round's verdict; one of
    CRITICAL or HIGH severity is named to the operator when the round ends. A new backlog record
    needs the operator's decision. Each reviewer's brief states this boundary. TASK 119 filed two
    records from such findings, and the operator removed them. WI-52 records this rule.
  ```

  The bullet is indented as the two bullets above it: 6 spaces, and 8 on a continuation line.

- **R2.1** `tests/test_run_safety_rules.py` pins §3 step 4 whole (`STEP_4`). The pin takes the
  bullet of R1.1.
- **R3.1** `System/Docs/WORKFLOWS.md`, the **Safety Protocol** list of §5, gains item 5. No table
  cell changes:

  ```text
  5. **Review Boundary:** Stage-2 reviews (`framework-upgrade` §3 step 4) check the change against
     its TASK and the lines it touches. Code that the change makes run, or run without a prompt,
     is among those lines. Any other finding, unless the change causes it as a regression, is one
     line in the audit record, with its severity, and does not set the round's verdict. A CRITICAL
     or HIGH finding of that kind is named to the operator. A new backlog record needs the
     operator's decision.
  ```

- **R3.2** `CHANGELOG.md` and `CHANGELOG.ru.md` get v3.41.0, titled "stage 2 of framework-upgrade
  holds its reviews to the TASK and the lines the change touches (TASK 120)". One `#### Changed`
  entry, and `#### Изменено` in Russian:

  ```text
  - **Stage 2 of `/framework-upgrade` holds its reviews to the TASK and the lines the change
    touches** (WI-52). Code that the change makes run, or run without a prompt, counts among
    those lines. Any other finding, unless the change causes it as a regression, is one line in
    the audit record, with its severity, marked as before the task. It does not set the round's
    verdict, and a CRITICAL or HIGH one is named to the operator. A new backlog record needs the
    operator's decision. Each reviewer's brief states the boundary.
  ```

- **R3.3** WI-52 gets `status: done`, `resolved_at`, `resolved_by: 'TASK 120'` and a resolution
  blockquote; its index line moves under `## Closed`.
- **R4.1** `tests/test_run_safety_rules.py` is code that `tests/run_tests.py` imports. Its new text
  is written under the staged name `tests/staged_run_safety_rules.py`.
- **R4.2** The base test pins the current text of §3 step 4. The edit of R1.1 therefore lands with
  the test, in one stage-3 patch: `framework-upgrade.md` takes the bullet, the test takes the staged
  text, and the staged file is deleted.
- **R4.3** Stages 2 to 4 and the Failure rule follow TASK 118 R7.2 to R7.11, except:
  - the test module of R4.1 is the only staged file;
  - a scratchpad driver loads it and gives its `_read` either the base text of
    `framework-upgrade.md` or the patched text built in memory (A2);
  - no mutation run applies: the pin itself is the check;
  - `Pending after restore` lists R3.1 to R3.3.

<!-- contract:tests -->

## 4. Test obligations

- **TC-B1** — the staged pin `STEP_4` holds the bullet of R1.1.
  - Against the base text of `framework-upgrade.md`, the staged module's TC-1 fails.
  - Against the patched text, built in memory, it passes.
  - It fails when the bullet is missing from the workflow or from the pin.

<!-- contract:acceptance -->

## 5. Acceptance criteria

- **A1** — after stage 3, the bullet is the third bullet of stage 2 in §3 step 4, and
  `tests/test_run_safety_rules.py` passes.
- **A2** — before stage 3, the staged TC-1 fails on the base text and passes on the patched text.
- **A3** — R3's documents and records hold the stated text; the register check reports no `WARN` on
  an added line.
- **A4** — after stage 3, `python3 tests/run_tests.py`, the CI steps and the skill validators pass.

<!-- contract:decisions -->

## 6. Decisions

- **D1**, 2026-10-09, operator: implement WI-52 now, answer "Реализовать правило сейчас".
  Rejected: correcting the record only, since the next run would start without the rule.
- **D2**, 2026-10-09, orchestrator: the boundary of this run is R1 to R4 (D5 of TASK 119 applies to
  this run's own reviews).
- **D4**, 2026-10-09, operator: round 2 passed with three LOW findings of the class that round 1
  fixed. The summaries of R3.1 and R3.2 and the WI-52 closure take the missing clauses. Round 3
  reviews that edit. Answer "Дописать и раунд 3". Rejected: shipping with the residual in the audit
  record, and a backlog record for it.
- **D3**, 2026-10-09, orchestrator: stage-2 round 1 passed with five LOW findings, all in the
  touched lines; fix round 1 applies them. Without it, the bullet leaves open whether a CRITICAL
  from before the task sets the verdict that `security-audit` §6.2 gives. Rejected: shipping on
  round 1, which leaves that reading to each auditor.

<!-- contract:out-of-scope -->

## 7. Out of scope

- The agent definitions of the reviewers: the brief carries the boundary (R1.1).
- Any other text of `framework-upgrade`.
