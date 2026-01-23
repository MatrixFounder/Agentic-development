# Multi-Agent Software Development System (v3.6+)

## General Concept

This system orchestrates a team of specialized agents coordinated by an Orchestrator. The system operates in **Agentic Mode**, utilizing a structured `task_boundary` protocol for state management and an authoritative **Skill System** for capabilities.

**Source of Truth:**
- **Roles & Prompts:** `System/Agents/`
- **Capabilities:** `.agent/skills/` (See `SKILL_TIERS.md`)
- **Orchestration Logic:** `.agent/skills/skill-orchestrator-patterns/SKILL.md`

## Agent Roles

### 1. Orchestrator
**Function:** Coordination of the entire development process
- Assigns tasks to other agents
- Manages strict Stage Cycles (Init → Review → Revision)
- **Tooling:** Uses `task_boundary` to track high-level progress.

### 2. Analyst
**Function:** Creating the Technical Specification (TASK)
- **Output:** `docs/TASK.md` (See `skill-task-model`)
- **Key Skill:** `requirements-analysis` (TIER 1)

### 3. TASK Reviewer
**Function:** Verifying the Technical Specification
- **Checklist:** `task-review-checklist`

### 4. Architect
**Function:** Designing system architecture
- **Output:** `docs/ARCHITECTURE.md` (Core or Extended format)
- **Key Skill:** `architecture-format-core` / `architecture-format-extended` (See O3 optimization)

### 5. Architecture Reviewer
**Function:** Verifying the architecture
- **Checklist:** `architecture-review-checklist`

### 6. Tech Lead / Planner
**Function:** Formulating development tasks
- **Output:** `docs/PLAN.md` and `docs/tasks/*.md`
- **Key Skill:** `planning-decision-tree`

### 7. Plan Reviewer
**Function:** Verifying the plan
- **Checklist:** `plan-review-checklist`

### 8. Developer
**Function:** Task implementation and test writing
- **Key Principles:** Stub-First (`tdd-stub-first`), Atomic Commits, Docs-First.
- **Output:** Code, Tests, Updated `.AGENTS.md`.

### 9. Code Reviewer
**Function:** Verifying code quality
- **Checklist:** `code-review-checklist`

### 10. Security Auditor
**Function:** Vulnerability assessment
- **Trigger:** Post-development or via `security-audit` workflow.
- **Key Skill:** `security-audit` / `adversarial-security`.

---

## System Operating Principles

### 1. Skill Tiers (Authoritative Source: `System/Docs/SKILL_TIERS.md`)
The system uses a **Phase-Specific Loading Protocol** (Optimization O1) to minimize token overhead:
- **TIER 0 (System Foundation):** ALWAYS LOADED. Includes `core-principles`, `safe-commands`, `artifact-management`.
- **TIER 0 (+):** `skill-session-state` (Session Persistence).
- **TIER 1 (Phase-Triggered):** Loaded only when entering a specific phase (e.g., Analysis, Architecture).
- **TIER 2 (Extended):** Loaded on demand (e.g., `reverse-engineering`).

### 2. Agentic Mode & Task Boundaries
The system operates within strict boundaries defined by the **`task_boundary`** tool:
- **State Tracking:** Every major step updates `TaskName`, `TaskStatus`, and `Mode`.
- **Session Persistence:** (Optimization O7) Context is saved to `.agent/sessions/latest.yaml` to survive session clears.

### 3. Core Methodologies
- **Stub-First Development:** Structure → Stubs → Tests → Implementation.
- **Documentation First:** No code without updated artifacts.
- **Verification Driven (VDD):** "Trust but Verify" using adversarial reviewers.

---

## Development Process (Orchestrator Patterns)

The strict logic of the development lifecycle is defined in **`skill-orchestrator-patterns/SKILL.md`**.
The system follows a standard **Stage Cycle**:

1. **Initialization:** Agent (Analyst/Architect/etc.) creates artifact.
2. **Review:** Reviewer checks artifact against checklist.
3. **Revision:** (If needed) Agent fixes issues. Max 2 iterations.

### Workflows (Dynamic Dispatch)
Standard flows can be overridden by Workflows (`.agent/workflows/`):
- `/vdd-adversarial`: High-integrity mode with stricter reviews.
- `/security-audit`: Focused security pass.

---

## Global Artifact Rules

### TASK.md Lifecycle
- **Active Task:** `docs/TASK.md` always describes the CURRENT active work.
- **Archiving:** (Skill: `skill-archive-task`) Old tasks are moved to `docs/tasks/task-XXX-slug.md`.
- **Never Delete:** History is preserved in `docs/tasks/`.

### ARCHITECTURE.md
- **Modular Format:** Uses `architecture-format-core` for updates and `architecture-format-extended` for new systems.

---

## Key Rules (The "Anti-Patterns")

❌ **NO** writing code without tests (Stub-First violation).
❌ **NO** refactoring without a task (Scope creep).
❌ **NO** ignoring TIER 0 skills (breaking automation).
✅ **ALWAYS** use `task_boundary` to report status.
✅ **ALWAYS** update `.AGENTS.md` when structure changes (Memory update).
