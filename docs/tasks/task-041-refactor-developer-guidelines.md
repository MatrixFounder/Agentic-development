# Task 041: Refactor developer-guidelines

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 041
- **Slug:** `refactor-developer-guidelines`

## 1. Goal
Refactor `developer-guidelines` skill to expand language support and declutter core guidelines, adhering to the `skill-creator` V2 standard.

## 2. Scope
- **Target Skill:** `.agent/skills/developer-guidelines`
- **New Directory:** `.agent/skills/developer-guidelines/resources/languages/`
- **New Files:**
  - `resources/languages/rust.md`
  - `resources/languages/solidity.md`
  - `resources/languages/python.md`
  - `resources/languages/javascript.md`
- **Modified File:** `SKILL.md` (Update to strictly universal principles and dynamic loading).

## 3. Deliverables
1. [ ] Decomposed `SKILL.md` retaining only universal principles.
2. [ ] Created language-specific guide files (Rust, Solidity, Python, JS).
3. [ ] Updated `SKILL.md` references.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
