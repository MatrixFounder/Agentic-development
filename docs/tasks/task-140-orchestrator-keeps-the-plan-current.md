# TASK 140 — [LIGHT] The executor of a plan's task keeps its status and checklist current (WI-62)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 140 |
| Slug | orchestrator-keeps-the-plan-current |
| Type | Light Mode (D1) |
| Source | WI-62, option 2; the operator's request of 2026-11-06 |
| Base revision | `511ec041d6280dd4ef99bf2dbbb87c94dd017c6d` |
| Closes | WI-62 |
| Archive name | `task-140-orchestrator-keeps-the-plan-current.md` |
| Revision | 4 |

**Request.** The operator chose option 2 of WI-62 on 2026-11-06. Option 2 extends the rule of
`skill-planning-format` §2.2 to every agent that starts a plan's task. The rule also ticks the
task's checklist items at the hand-back that reports them, before the review.

**Revision 2** follows the code review of cycle 1: CHANGES REQUESTED, with one MAJOR, eleven
MINOR and fourteen NIT findings, none BLOCKING. The fix pass:
- the MAJOR: the executor also covers an orchestrator that runs the task inline, with no
  subagent; §2.2 step 6 defines the hand-back (D3, R1);
- step 6 ticks at the approval each item that only the review settles (D9);
- step 7 holds for a dispatched agent that runs a develop workflow (D3);
- `vdd-03` and `vdd-05` tick at the hand-back step and untick at the rejection step, not in the
  roast that a reviewer may run alone (D10);
- `System/Docs/SKILLS.md`, `System/Docs/WORKFLOWS.md`, the developer wrapper and both READMEs
  follow (R5, R7);
- the tests pin more of R1 to R5; a pin of `tick` no longer matches `untick` (R6).

**Revision 3** follows the code review of cycle 2: CHANGES REQUESTED, with one MAJOR, three MINOR
and eight NIT findings, none BLOCKING. Cycle 2 is the last cycle of `light-02-develop-task`. The
fix pass:
- the MAJOR: the tests pin `System/Docs/SKILLS.md`, `System/Docs/WORKFLOWS.md`, the docstring of
  `plan_gantt.py`, the developer wrapper and the approval case of D9. A checklist edit in the
  roast of either VDD workflow fails when it uses the word tick or untick;
- the executor is the agent that was not dispatched to the task; each develop workflow tells a
  dispatched agent to skip its plan edits (D11);
- the cell of `docs/ARCHITECTURE.md` §10.6 is under 120 characters again (TC-5);
- item 10 of `01_orchestrator.md` ticks a review-settled item at approval.

**Revision 4** follows the narrow round 3, which the operator approved past the bound (D13):
APPROVED, with three MINOR and seven NIT findings. The fix pass:
- an agent dispatched to run a chain of tasks is the executor of each task it starts; the guard
  covers an agent dispatched to a single task (D12);
- the sentence of step 4 of the system prompts names the ways the agent runs the task;
- the row of `docs/ARCHITECTURE.md` §10.6 names the executor of each task an orchestrator starts;
- step 6 covers the single report of a subagent that ran a develop workflow;
- the tests pin the guard at the first plan edit of each workflow.

The builder's evidence of cycle 1 stated that removing the new row of `docs/ARCHITECTURE.md`
§10.6 fails the tests. The planting renamed a surface in that row; removing the row passed.
Revision 2 adds the pin.

**State at the base.**
1. `skill-planning-format` §2.2 binds "a develop workflow". An orchestrator that starts the
   developer and the reviewer as subagents is not one, so §2.2 does not bind it.
2. `System/Agents/01_orchestrator.md` names no plan status and no checklist.
3. Step 4 "Development Phase" of `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` names no plan status.
   An orchestrator in Claude Code reads `CLAUDE.md`. `CLAUDE.md` and `GEMINI.md` do not route
   step 4 to `01_orchestrator.md`.
4. No rule ticks a checklist item (`- [ ]` → `- [x]`).
5. `skill-planning-format` §2.1 step 1, the plan template, `plan-review-checklist` and
   `docs/ARCHITECTURE.md` §10.6 state that the develop workflows set the status.

## 1. Decisions

- D1, 2026-11-06, operator: `/light`. The run has the edits with their pinning tests, the test
  run, and one code reviewer with the exhaustive prompt, in at most two review cycles
  (`light-02-develop-task`). It has no meta-audit and no security audit: nothing that runs
  changes.
- D2, 2026-11-06, operator: the rule stands in every surface that an executor reads: §2.2,
  `01_orchestrator.md`, step 4 of the three system prompts, and the workflows `03`, `vdd-03` and
  `vdd-05`.
- D3, orchestrator, revised after review: the executor of a task is the agent that starts it and
  was not dispatched to it. It runs the task inline, through a develop workflow, or through
  subagents. Only the executor edits the status and the ticks. A dispatched developer or reviewer
  reports what is in place or rejected, also when it runs a develop workflow.
  **Why.** Parallel chains of subagents would edit `docs/PLAN.md` at the same time ⇒ edits are
  lost. The reviewers of this framework are read-only ⇒ a reviewer cannot untick an item.
- D4, orchestrator: the checklist of a task is the set of `- [ ]` and `- [x]` items of its record
  under `docs/tasks/` and of its entry in the sequence of `docs/PLAN.md`.
- D5, orchestrator: a tick changes no schedule entry. It runs neither `plan_gantt.py` command.
- D6, orchestrator: the new steps of §2.2 take the numbers 6 and 7. Steps 1–5 keep their numbers,
  so a citation of a step of §2.2 stays valid.
- D7, orchestrator: `05-run-full-task.md` and `light-02-develop-task.md` stay as they are. The
  loop of `05` starts each task through `03`. A light task has no plan.
- D8, orchestrator: the release v3.56.0 also takes the `[Unreleased]` entry of commit `511ec04`.
- D9, orchestrator, after review: an item that only the review settles, such as "Code complies
  with project standards" of the task template, turns `- [x]` at the approval.
- D10, orchestrator, after review: the two VDD workflows edit the checklist outside the roast.
  - `vdd-03` ticks at a new Step 2.3 (Hand-back) and unticks in the REJECTED branch of Step 4.
  - `vdd-05` ticks at Step B on a green suite and unticks in the REJECTED branch of Step D.
  - Step 3 of `vdd-03` holds no checklist edit.
  **Why.** `vdd-05` may hand Step 3 to a reviewer subagent ⇒ an edit in Step 3 contradicts
  step 7.
- D11, orchestrator, after review: each develop workflow carries one guard at its first plan
  edit. Under it, an agent dispatched to a single task skips every plan edit and reports instead.
- D12, orchestrator, after round 3: an agent dispatched to run a chain, such as `/develop-all`,
  is the executor of each task it starts. Rejected: the dispatcher as the executor of a chain —
  a background subagent returns one report, so the plan stays stale until the chain ends.
- D13, 2026-11-06, operator: a narrow round 3 past the bound of `light-02-develop-task`, then the
  commit.

## 2. Requirements

<!-- contract:requirements -->

- **R1** `skill-planning-format` §2.2 (version 1.6):
  - its subject is the executor of a plan's task (D3);
  - step 6 states the checklist (D4) and the hand-back: the moment the task goes to its review;
  - at the hand-back, before the review, the executor ticks each item reported in place;
  - the executor unticks an item whose deliverable a review rejects, and ticks it again at the
    hand-back of the fix round. An item that no review rejects stays ticked;
  - at the approval, the executor ticks each item that only the review settles (D9). It names
    each item still unticked in its report;
  - for a tick, the executor runs no command (D5);
  - step 7 states the one writer (D3);
  - §2.1 step 1 names the executor in place of the develop workflows.
- **R2** `01_orchestrator.md` §6, item 10, holds one rule that points to §2.2. The rule names the
  three moments: the start, the hand-back and the verdict of item 11. It holds for one chain of
  subagents and for several at once.
- **R3** Step 4 of `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` holds one item that points to §2.2.
- **R4** `03-develop-single-task.md`, `vdd-03-develop.md` and `vdd-05-run-full-task.md` each cite
  `skill-planning-format` §2.2 step 6 at the hand-back and at the rejection (D10).
- **R5** These name the executor in place of the develop workflows:
  - the plan template and `plan-review-checklist` (version 1.4);
  - `docs/ARCHITECTURE.md` §10.6, `System/Docs/SKILLS.md`, `System/Docs/WORKFLOWS.md`;
  - the docstring of `plan_gantt.py`.

  `.claude/agents/developer.md` tells a dispatched developer to edit no plan item.
- **R6** `tests/test_mermaid_wiring.py` pins R1 to R5.
- **R7** WI-62 closes in its record and in `docs/BACKLOG.md`. Both changelogs and both READMEs
  carry v3.56.0.

## 3. Files

- `.agent/skills/skill-planning-format/SKILL.md`, its `assets/templates/plan_md_template.md`;
- `.agent/skills/plan-review-checklist/SKILL.md`;
- `System/Agents/01_orchestrator.md`;
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`;
- `.agent/workflows/03-develop-single-task.md`, `vdd-03-develop.md`, `vdd-05-run-full-task.md`;
- `docs/ARCHITECTURE.md`; the docstring of `plan_gantt.py` of `mermaid-authoring-guidelines`;
- `System/Docs/SKILLS.md`, `System/Docs/WORKFLOWS.md`, `.claude/agents/developer.md`;
- `tests/test_mermaid_wiring.py`;
- `docs/backlog/wi-62-*.md`, `docs/BACKLOG.md`, `CHANGELOG.md`, `CHANGELOG.ru.md`;
- `README.md`, `README.ru.md`;
- `docs/TASK.md`; the archive of TASK 139.

## 4. Acceptance

<!-- contract:acceptance -->

- TC-1 — `tests/test_mermaid_wiring.py` → pass. It fails on each of these plantings:
  - step 6 or step 7 of §2.2 is removed;
  - the subject of §2.2 or §2.1 step 1 names the develop workflows again;
  - the rule of R2 or R3 is removed;
  - a workflow of R4 drops its tick or its untick;
  - Step 3 of `vdd-03` holds a checklist edit;
  - a surface of R5 names the develop workflows again.
- TC-2 — `python3 tests/run_tests.py` → pass.
- TC-3 — `validate_skill.py` on `skill-planning-format` and `plan-review-checklist` → pass.
- TC-4 — `check_prompt_references.py`, `smoke_workflows.py` and the check of positional
  references of `framework-gates.yml` → pass.
- TC-5 — `scan_register.py` on the edited text → no finding that this run adds.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. Option 3 of WI-62, a `## Progress` table in the plan.
2. A check that the ticks match the review. The rule is a step of the executor; no script reads
   the ticks.
3. The prompts `08_developer_prompt.md` and `09_code_reviewer_prompt.md`. Neither tells a
   dispatched agent to edit a plan item.
4. The workflows do not repeat the approval case of step 6; each cites §2.2.
5. `skill-phase-context` loads `skill-planning-format` in the Planning phase only. An executor
   reaches §2.2 through the pointers of R2 to R4.
6. A task entered again after `done` shows `in-progress` with its items ticked until a review
   rejects one.
7. The pins are substrings and word patterns. A negation that keeps the pinned words passes, such
   as "on a red suite, tick" in `vdd-05` Step B. A checklist edit in a roast that avoids the words
   tick and untick also passes.
8. Step 7 holds within one run. Two chain runners, or two operator sessions, on one
   `docs/PLAN.md` at once can overwrite each other's edit.
