# Task 044: Refactor requirements-analysis

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 044
- **Slug:** `refactor-requirements-analysis`

## 1. Goal
Refactor `requirements-analysis` skill to streamline the main prompt by moving the verbose "Technical Specification (TASK) Structure" section to a separate template file.

## 2. Scope
- **Target Skill:** `.agent/skills/requirements-analysis`
- **New Directory:** `.agent/skills/requirements-analysis/resources/templates/`
- **New File:** `resources/templates/task_template.md`
- **Modified File:** `SKILL.md` (Replace inline template with reference).

## 3. Deliverables
1. [ ] Created `resources/templates/task_template.md` containing the extracted TASK structure.
2. [ ] Updated `SKILL.md` to remove the inline text and reference the new template.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
