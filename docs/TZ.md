## 0. Meta Information
- **Task ID:** 009
- **Slug:** verification-workflow

## 1. General Description
The goal is to improve the development process quality by introducing mandatory verification steps (Review) and feedback loops into the agentic workflows. We need to modify existing workflow files to ensure that every "Doer" (Analyst, Architect, Planner) is followed by a "Reviewer" (TZ Reviewer, Architecture Reviewer, Plan Reviewer).

## 2. List of Use Cases

### UC-01: Analyst Workflow with Verification
**Actors:** User, Analyst, TZ Reviewer
**Preconditions:** User initiates a new feature or task.
**Main Scenario:**
1. **Analyst** creates/updates `docs/TZ.md`.
2. **TZ Reviewer** checks the TZ.
3. If issues found -> Analyst fixes -> Go to step 2.
4. If approved -> Workflow proceeds.

### UC-02: Architect Workflow with Verification
**Actors:** Architect, Architecture Reviewer
**Preconditions:** TZ is approved.
**Main Scenario:**
1. **Architect** updates `docs/ARCHITECTURE.md`.
2. **Architecture Reviewer** checks the architecture.
3. If issues found -> Architect fixes -> Go to step 2.
4. If approved -> Workflow proceeds.

### UC-03: Planner Workflow with Verification
**Actors:** Planner, Plan Reviewer
**Preconditions:** Architecture is approved.
**Main Scenario:**
1. **Planner** creates `docs/PLAN.md` and task breakdowns.
2. **Plan Reviewer** checks the plan.
3. If issues found -> Planner fixes -> Go to step 2.
4. If approved -> Workflow proceeds.

## 3. Non-functional Requirements
- **Consistency:** All specified workflows must follow the same Doer-Reviewer-Loop pattern.
- **Robustness:** The loop must ensure quality before moving forward.

## 4. Constraints and Assumptions
- We are modifying markdown workflow files in `.agent/workflows`.
- The agents (Analyst, etc.) are already defined in `System/Agents`.
- We assume the Orchestrator/User will execute these steps manually or via an interpreter that understands these prompts.

## 5. Open Questions
- None.
