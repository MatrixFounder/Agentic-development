---
description: Pipeline for upgrading the Agentic Framework itself (Prompts, Skills, System Logic)
---

# Workflow: Framework Upgrade

> [!CAUTION]
> **META-OPERATION**: This workflow modifies the Agent's own operating logic.
> **Strict Adherence Required**: No skipping validation steps.

## 1. Analysis & Meta-Audit
1. **Analyze**: Read User Request.
2. **Draft**: Create `docs/TASK.md` (Type: Framework Upgrade).
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: SPECIFICATION AUDIT).
   - **Instruction**: "Check `docs/TASK.md` for safety violations."
   - **Gate**: If Audit fails, GOTO Step 2.

## 2. Planning & Safety Check
1. **Architect**: Update `docs/ARCHITECTURE.md` (if System Architecture changes).
2. **Plan**: Create `docs/PLAN.md` (Implementation Steps).
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: PLAN AUDIT).
   - **Instruction**: "Check `docs/PLAN.md` for rollback and verification steps."
   - **Gate**: If Audit fails, GOTO Step 2.

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

## 5. Fallback
If the system becomes unstable during upgrade:
- **Restore every backed-up bootstrap file** (covers Claude Code / Codex·Cursor / Gemini CLI):
  `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f ".agent/archive/$f.bak" ] && cp ".agent/archive/$f.bak" "$f"; done`
- Restore any other edited file from its `.agent/archive/<file>.bak` backup the same way.
