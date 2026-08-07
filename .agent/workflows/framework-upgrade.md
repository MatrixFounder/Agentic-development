---
description: Pipeline for upgrading the Agentic Framework itself (Prompts, Skills, System Logic)
contract:
  version: 1
  loops:
    - id: spec-audit-retry
      what: specification meta-audit fails -> redraft TASK
      site: "<!-- loop:spec-audit-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
    - id: plan-audit-retry
      what: plan meta-audit fails -> redraft PLAN
      site: "<!-- loop:plan-audit-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---

# Workflow: Framework Upgrade

> [!CAUTION]
> **META-OPERATION**: This workflow modifies the Agent's own operating logic.
> **Strict Adherence Required**: No skipping validation steps.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "framework-upgrade-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

## 1. Analysis & Meta-Audit
1. **Analyze**: Read User Request.
2. **Draft**: Create `docs/TASK.md` (Type: Framework Upgrade).
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: SPECIFICATION AUDIT).
   - **Instruction**: "Check `docs/TASK.md` for safety violations."
   <!-- loop:spec-audit-retry -->
   - **Gate**: If Audit fails, GOTO Step 2.
   - **Target of that GOTO**: **Step 2 of THIS section** (§1.2, redraft `docs/TASK.md`) — not §2.
   - **Bound: max 3 audit rounds.** Still failing after the 3rd: **STOP** and escalate to the user
     with the verificator's outstanding safety violations. A framework upgrade never proceeds on an
     unaudited TASK.

## 2. Planning & Safety Check
1. **Architect**: Update `docs/ARCHITECTURE.md` (if System Architecture changes).
2. **Plan**: Create `docs/PLAN.md` (Implementation Steps).
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: PLAN AUDIT).
   - **Instruction**: "Check `docs/PLAN.md` for rollback and verification steps."
   <!-- loop:plan-audit-retry -->
   - **Gate**: If Audit fails, GOTO Step 2.
   - **Target of that GOTO**: **Step 2 of THIS section** (§2.2, redraft `docs/PLAN.md`).
   - **Bound: max 3 audit rounds.** Still failing after the 3rd: **STOP** and escalate to the user
     with the verificator's outstanding findings — do not enter §3 Execution.

## 3. Execution (Atomic Updates)
1. **Backup**:
   - `mkdir -p .agent/archive`
   - Back up **every present bootstrap file** (not just one vendor's — the repo uses `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex/Cursor, `GEMINI.md` for Gemini CLI):
     `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done`
   - Also back up any other files this upgrade will edit (prompts, skills, workflows) to `.agent/archive/`.
2. **Implement**: Execute `08_developer_prompt.md` with `skill-self-improvement-verificator` active.
3. **Verify**:
   - Run affected tests.
   - Run `skill-spec-validator` (if modified).

## 4. Documentation & Finalization
1. **Docs**: Update `System/Docs/` to match new reality.
2. **Registry**: Update `System/Docs/SKILLS.md` and `WORKFLOWS.md`.
3. **Restart**: Instruct User to restart session if Core Prompts changed.

## 4.5 Reference resolver (gate)

Run `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed --fix`.

It selects documents **citing** the files this change touched, which default diff scope
does not. `REFERENT_MOVED` is repaired mechanically and the repair lands in the same
commit; a coordinate carrying no referent is reported as *not examined* and is **not** a
defect (`documentation-standards` §4.1). This position is the one WI-16's §5.1 table
names for the State-Claim Sweep: when that record lands it inserts **above** this
section, so neither displaces the other.

## 5. Fallback
If the system becomes unstable during upgrade:
- **Restore every backed-up bootstrap file** (covers Claude Code / Codex·Cursor / Gemini CLI):
  `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f ".agent/archive/$f.bak" ] && cp ".agent/archive/$f.bak" "$f"; done`
- Restore any other edited file from its `.agent/archive/<file>.bak` backup the same way.

## 6. Retro (Global Protocol)
Apply `run-feedback` SKILL.md §7 "Retro protocol":
`claim --run-id "framework-upgrade-<task-slug>"` → exit 6 = nested, SKIP this step;
exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
collect → triage → file per the skill, and `release`. **Non-blocking**: failures
here are reported in one line and never change this workflow's outcome.
