---
description: Develop a specific task
contract:
  version: 1
  loops:
    - id: dev-review
      what: code reviewer rejects -> update and re-review
      site: "<!-- loop:dev-review -->"
      default_max: 2
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---
> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "03-develop-single-task-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

1. Read `System/Agents/08_developer_prompt.md` to understand the Development phase.
2. Pick a task from `docs/tasks/`.
3. Implement the task using the Stub-First approach:
    - Create stubs/interfaces first.
    - Verify rendering/compilation.
    - Implement logic.
4. Initiate Code Review.
    <!-- loop:dev-review -->
    - **Verification Loop**: Read `System/Agents/09_code_reviewer_prompt.md`. 
    - If the Reviewer requests changes:
        - Update code/stubs.
        - **Retry (Max 2 attempts)**: Repeat the review.
        - If after 2 retries the review still fails: **STOP** and ask the user for help.
    - If approved: Proceed or Finish.
5. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "03-develop-single-task-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
