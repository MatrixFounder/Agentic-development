# Proposal: Framework Improvements for "One-Shot" Quality (Revised)

## 0. Meta Information
- **ID:** SPEC-002
- **Title:** Requirements Hardening & Atomic Planning
- **Status:** Draft
- **Related:** `Backlog/development-enhancement-20260207.md` (Superseded)

## 1. The Core Problem
The "Task Manager" retrospective proved that **implicit simplification** is the enemy of one-shot quality.
- **Ambiguity**: "Polished UI" became "Basic CSS".
- **Lossiness**: `idea.md` had "Recuring tasks" -> `TASK.md` missed it -> `PLAN.md` ignored it.
- **Simplification**: Developer assumed "Complex = Defer".

**Critique Response**: The previous proposal (SPEC-001) was correct in *intent* but over-engineered in *execution* (complexity creep, fragile parsing).

## 2. The Solution: "Hardened" Pipeline

Instead of adding 3 complex skills and "smart modes", we will implement **Structured Constraints** at 3 key points:

### 2.1 Analysis Phase: The "Traceability Matrix"
We will update the `Analyst` prompt to require a **Requirements Traceability Matrix (RTM)** in `TASK.md`. This forces specific line-items for every feature.

**Change**: Update `System/Agents/02_analyst_prompt.md`.
**Output**: `TASK.md` MUST contain:
```markdown
## Requirements Traceability
| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | Task List | Yes | Title, Priority, Date |
| R2 | Subtasks | Yes | Nested list, Toggle |
| R3 | Recurring | Yes | Daily/Weekly logic |
```

### 2.2 Planning Phase: Atomic Checklists
We will update the `Planner` prompt to strictly forbid "feature grouping". Every item in the RTM must have a corresponding **Checklist Item** in `PLAN.md`.

**Change**: Update `System/Agents/06_agent_planner.md`.
**Constraint**: "Feature grouping is PROHIBITED. Do not write '- Implement Task Features'. Write '- Implement Subtasks', '- Implement Tags', '- Implement Recurring'."

### 2.3 One New Skill: `skill-spec-validator`
Instead of multiple overlapping skills, we create ONE stateless skill that validates the artifacts against each other.

**Skill**: `spec-validator`
**Function**:
1. Reads `TASK.md`.
2. Checks if `RTM` coverage is 100%.
3. Reads `PLAN.md`.
4. Checks if every RTM item has a checklist item.
5. **fails** if there is a gap.



### 2.4 Workflow: Upgrade `/vdd-enhanced`
Instead of creating a new file, we **upgrade** the existing `vdd-enhanced` workflow. It currently just wraps `base-stub-first`. We will *unroll* it to inject the **Gatekeeper** checks.

**File**: `.agent/workflows/vdd-enhanced.md` (Updated)
```markdown
# Workflow: VDD-Enhanced (Hardened)

1. **Analysis & Validation**:
   - Call `/01-start-feature`
   - **Validator**: `spec-validator --mode=task`
   - **Self-Correction**: If validator fails, instruct Analyst to fix gaps (Max 3 retries).

2. **Planning & Validation**:
   - Call `/02-plan-implementation`
   - **Validator**: `spec-validator --mode=plan`
   - **Self-Correction**: If validator fails, instruct Planner to fix gaps (Max 3 retries).

3. **Development**:
   - Call `/05-run-full-task` (Stub-First)

4. **Adversarial Review**:
   - Call `/vdd-adversarial`
```
This makes VDD truly "Verification Driven" from the start, via autonomous loops.

## 3. Implementation Plan

### Step 1: Update Prompts (with Light Mode Protection)
We must ensure we don't slow down `/light-*` workflows.

1. **`02_analyst_prompt.md`**:
   - Add: "IF `skill-light-mode` is active OR title contains `[LIGHT]`: **SKIP** RTM generation."
   - Else: "You **MUST** generate a Requirements Traceability Matrix (RTM)."

2. **`06_agent_planner.md`**:
   - (Light mode skips planner, so this is safe).
   - Add: "Feature grouping is PROHIBITED. One RTM item = One Checklist item."
   - **MUST**: "Checklist items MUST start with the RTM ID (e.g., `[R1] Implement...`)."

3. **`08_agent_developer.md`**:
   - Add: "IF `skill-light-mode` is active: Fix directly. Do not overengineer."
   - Else: "You **MUST** use Stub-First Development for EVERY feature. No skipping."

4. **`03_task_reviewer_prompt.md`**:
   - Add Check: "Does `TASK.md` contain strict Requirements Traceability Matrix?"
   - **Light Mode Protection**: "Skip this check if task is `[LIGHT]`."

5. **`07_plan_reviewer_prompt.md`**:
   - Add Check: "Does every RTM item have a corresponding Atomic Checklist item in `PLAN.md`?"
   - **Light Mode Protection**: "Skip this check if task is `[LIGHT]`."

### Step 2: Create `skill-spec-validator` using `skill-creator`
- **Use**: This skill will be called by the `Orchestrator` during `/vdd-enhanced`.
- **Logic**:
    - `python3 scripts/validate.py --mode task task.md`: Checks for `## Requirements Traceability` table.
    - `python3 scripts/validate.py --mode plan plan.md task.md`: Checks that every ID in `task.md` (e.g., `R1`) appears in `plan.md` (e.g., `[R1]`).
- **Risk Mitigation**:
    - **Looping**: If validation fails, script returns exit code 1. Workflow catches this and triggers a **Self-Correction Loop** (returns to Analyst/Planner). It does NOT crash the Orchestrator.
    - **Bypass**: To bypass validation (e.g., bug in validator), user can add `[BYPASS_VALIDATION]` to `TASK.md` title.
    - **Garbage In**: Analyst Prompt will require *at least 3 sub-features* per requirement to prevent vague RTMs.

### Step 3: Upgrade `/vdd-enhanced` workflow
- Unroll the current implementation.
- Inject `spec-validator` checkpoints at Step 1 (Analysis) and Step 2 (Planning).
- **Result**: The workflow effectively becomes a "Quality Gate". if `TASK.md` is bad, you cannot proceed to `PLAN.md`.

## 4. Addressing Risks (VDD Critique)
| Risk | Mitigation |
|:---|:---|
| **Validator Infinite Loop** | Added "Max 3 Retries" limit. |
| **Garbage In** | Analyst Prompt requires "Granularity: >3 sub-items". |
| **ID Linking** | Planner Prompt requires strict `[ID]` prefix. |

## 5. Impact on "Classic" Workflow
The user key question: "What happens if I just say 'Do X'?"

- **Behavior**: The Orchestrator follows `01_orchestrator.md` -> calls `02_analyst` -> calls `03_task_reviewer`.
- **Improvement**: Since we upgraded the **Prompts**:
    - Analyst **WILL** generate RTM.
    - Reviewer **WILL** check RTM.
    - Planner **WILL** use Atomic Checklists.
- **Difference**: The `Classic` flow relies on **LLM Verification** (Reviewer Agent). The `VDD-Enhanced` flow adds **Programmatic Verification** (`spec-validator`).
- **Conclusion**: The "Hardening" applies globally. The "Strictest Gatekeeping" is available via workflow.

## 6. Framework Self-Improvement System (New)
To prevent regression when editing the Agents themselves.

### 6.1 `skill-self-improvement-verificator` (Tier 3) (create via skill-creator)
A Meta-Skill for **Auditing Specifications** before framework changes. It does NOT write code.
- **Purpose**: Ensure `docs/TASK.md` for a framework upgrade is complete and safe.
- **Checklist**:
    - [ ] `GEMINI.md`: Does the Task plan to update the root prompt?
    - [ ] `System/Agents/*.md`: Do proposed changes respect TIER 0 / 1 / 2 skills?
    - [ ] `System/Docs/*.md`: Does the Task include updating documentation?
    - [ ] `.agent/workflows/*.md`: Does the Task account for workflow compatibility?
- **Action**: "Read `TASK.md` and `PLAN.md`. Output a Critique. Block if unsafe."

### 6.2 Workflow: `/framework-upgrade`
```markdown
1. Analysis -> `docs/TASK.md` (Update Framework)
2. **Audit**: Call `skill-self-improvement-verificator` to Validate the Spec.
3. Architect -> `docs/ARCHITECTURE.md`
4. Planner -> `docs/PLAN.md`
5. **Audit**: Call `skill-self-improvement-verificator` to Validate the Plan.
6. Execution -> Developer (Standard Flow).
```

## 7. Comparison with Previous Proposal
| Feature | Old Proposal (Critized) | New Proposal (Revised) |
|:---|:---|:---|
| **Mode** | Implicit "Smart Parsing" | Explicit Workflow Upgrade |
| **Skills** | 3 (`parser`, `completeness`, `refinement`) | 1 (`spec-validator`) + Prompt Eng |
| **Complexity** | Blocking / User Intervention | **Self-Correcting Agentic Loop** |
| **Integration** | New Modes / Files | **Direct Upgrade of `vdd-enhanced`** |

## 8. Action Items
1. [ ] Update Analyst Prompt (Standardize RTM).
2. [ ] Update Planner Prompt (Atomic checklists).
3. [ ] Create `skill-spec-validator`.
4. [ ] **Update** `.agent/workflows/vdd-enhanced.md`.
5. [ ] **Create** `skill-self-improvement-verificator` (Tier 3).

---

## 9. Execution Checklist
- [x] Analyze Reference Project `Reference` <!-- id: 0 -->
    - [x] Check `TASK.md` for ambiguity <!-- id: 1 -->
    - [x] Check `PLAN.md` for granularity <!-- id: 2 -->
    - [x] Check key source files for simplification <!-- id: 3 -->
- [x] Synthesize Retrospective & Critique <!-- id: 4 -->
- [x] Draft Revised Proposal `Backlog/development-enhancement-revised.md` <!-- id: 5 -->
    - [x] Address complexity concerns (Smart Modes) <!-- id: 6 -->
    - [x] Address skill overlap <!-- id: 7 -->
    - [x] Focus on "Hardening" requirements <!-- id: 8 -->
    - [x] Integrate "Self-Improvement" Meta-Skill <!-- id: 17 -->
- [x] Create `skill-self-improvement-verificator` (Tier 3) <!-- id: 18 -->
    - [x] Initialize via `skill-creator` <!-- id: 20 -->
    - [x] Implement Verification Logic (Script) <!-- id: 21 -->
    - [x] Implement VDD Instructions <!-- id: 22 -->
    - [x] Refine Assets (Templates/Examples) <!-- id: 30 -->
    - [x] Add Bypass Mechanism <!-- id: 34 -->
- [x] Create `.agent/workflows/framework-upgrade.md` <!-- id: 23 -->
- [x] Create `skill-spec-validator` <!-- id: 10 -->
    - [x] Create Spec for the skill <!-- id: 11 -->
    - [x] Generate Skill using `skill-creator` patterns <!-- id: 12 -->
- [x] Implement Workflow changes <!-- id: 13 -->
    - [x] Update `vdd-enhanced.md` <!-- id: 14 -->
    - [x] Update Core Prompts (`Analyst`, `Planner`, `Developer`) <!-- id: 15 -->
    - [x] Verify Light Mode compatibility <!-- id: 16 -->
- [x] Update `Backlog/development-enhancement-20260207.md` with final decisions <!-- id: 9 -->
- [x] Update Documentation <!-- id: 24 -->
    - [x] Update `CHANGELOG.md` (v3.9.11) <!-- id: 25 -->
    - [x] Update `CHANGELOG.ru.md` (v3.9.11) <!-- id: 26 -->
    - [x] Update `System/Docs/SKILLS.md` and `WORKFLOWS.md` <!-- id: 27 -->
    - [x] Update `GEMINI.md` <!-- id: 28 -->
