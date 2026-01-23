# Task 042: Refactor testing-best-practices

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 042
- **Slug:** `refactor-testing-best-practices`

## 1. Goal
Refactor `testing-best-practices` skill to provide concrete, runnable examples and standard boilerplate by moving inline examples to `examples/` and creating templates in `resources/`.

## 2. Scope
- **Target Skill:** `.agent/skills/testing-best-practices`
- **New Directories:** 
  - `.agent/skills/testing-best-practices/examples/`
  - `.agent/skills/testing-best-practices/resources/templates/`
- **New Files:**
  - `examples/pytest_structure.py`
  - `examples/jest_structure.js`
  - `resources/templates/test_boilerplate.py`
- **Modified File:** `SKILL.md` (Update references).

## 3. Deliverables
1. [ ] Extracted Python/Pytest examples to `examples/pytest_structure.py`.
2. [ ] Extracted JavaScript/Jest examples to `examples/jest_structure.js`.
3. [ ] Created `resources/templates/test_boilerplate.py` template.
4. [ ] Updated `SKILL.md` to reference the new files.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
