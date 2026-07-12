---
description: "Iterative design loop: Brainstorm -> Spec Draft -> VDD -> Human Review -> Refine"
---

# Iterative Concept Design Workflow

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "iterative-design-<task-slug>"` (non-blocking; exit 6 = an outer workflow owns this run's retro — fine, continue).

## Phase 1: Context & Brainstorming
1. **Context Loading**: Read all user-provided reference files (e.g., `@idea.md`, `@refs/`).
2. **Brainstorming Session**:
   - Activate skill `brainstorming`.
   - Ask clarifying questions to refine the visible & hidden requirements.
   - Output a brief "Concept Summary" in chat for confirmation.
   - **User Checkpoint**: Wait for user confirmation to proceed to drafting.

## Phase 2: First Draft Generation
3. **Drafting**:
   - create `docs/drafts/spec_[feature_name]_v1.md`.
   - Apply `architecture-format-extended` to ensure structure.
   - **Constraint**: Do NOT aim for perfection yet, aim for completeness of structure.

## Phase 3: Automated VDD Critique (The "Self-Check")
4. **Adversarial Audit**:
   - Activate skill `vdd-adversarial`.
   - Crucially: **Do not edit the spec yet.**
   - Generate a critique report: `docs/drafts/spec_[feature_name]_v1_critique.md`.
   - List High/Medium risks, ambiguities, and missing edge cases.

## Phase 4: Human-in-the-Loop Review
5. **Presentation**:
   - Present both the **Draft Spec** and the **Critique Report** to the user via `notify_user`.
   - Ask: "What points in the Spec or Critique should be accepted, rejected, or modified?"
   - **STOP**: Execution pauses here until you (the User) provide feedback.

## Phase 5: Refinement Loop (Repeatable)
6. **Integration**:
   - Read User Feedback.
   - Read VDD Critique (only the points accepted by user).
   - Create/Update `docs/spec_[feature_name]_v2.md` (or update existing).
7. **Final Verification**:
   - Verify the new spec covers the feedback.
   - If complexity is high, trigger Phase 3 again.
   - Otherwise, ask for Final Approval.

## Phase 6: Retro (Global Protocol)
8. **Retro (Global Protocol)** — apply `run-feedback` SKILL.md §7 "Retro protocol":
   `claim --run-id "iterative-design-<task-slug>"` → exit 6 = nested, SKIP this step;
   exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
   from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
   collect → triage → file per the skill, and `release`. **Non-blocking**: failures
   here are reported in one line and never change this workflow's outcome.
