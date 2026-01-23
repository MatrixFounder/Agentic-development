# Task 047: Implement Light Mode (Workflow-Based)

> **Status:** COMPLETE ✅
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 047
- **Slug:** `implement-light-mode`
- **Source:** `Backlog/task-light_mode.md`

## 1. Goal
Implement **Light Mode** for fast, low-risk tasks (typos, UI tweaks), reducing development cycle time by ~50% by skipping Architecture and Planning phases using standard Workflows and Skill Tiers.

## 2. Scope
### Core Components
- **Workflows:**
    - `.agent/workflows/light-01-start-feature.md` (Analysis Only, sets [LIGHT] tag).
    - `.agent/workflows/light-02-develop-task.md` (Dev -> Review Loop).
- **Skill:** `.agent/skills/light-mode/SKILL.md` (Tier 2, instructions for Dev/Reviewer).
- **Documentation:** Updates to `GEMINI.md`, `AGENTS.md`, `docs/WORKFLOWS.md`.

### Critical Logic
- **Escalation Protocol:** Dev must STOP if complexity increases.
- **Security:** Code Reviewer performs sanity security checks (SPoF mitigation).
- **Dispatch:** `GEMINI.md` must proactively suggest `/light`.

## 3. Deliverables
1. [x] **Docs:** `GEMINI.md` (Critical Rule Exception, Dispatch), `AGENTS.md`, `WORKFLOWS.md`.
2. [x] **Workflows:** `light-01-start-feature.md`, `light-02-develop-task.md`.
3. [x] **Skill:** `light-mode` (Tier 2).
4. [ ] **Verification:** Successful execution of a dummy task via `/light`.

## 4. Implementation Summary
- **Configuration:** Updated `GEMINI.md` CRITICAL RULE to allow Light Mode exception. Added dispatch logic to propose `/light` for trivial tasks.
- **Workflows:** Created 2 new workflows with `// turbo` annotations for auto-run.
- **Skill:** Created `light-mode` skill with Low Risk definition, role-specific instructions, escalation protocol, and safety rules.
- **Documentation:** Updated `WORKFLOWS.md` (diagram, tables), `SKILLS.md` (catalog), `CHANGELOG.md` (EN/RU).
