# Task 046: Refactor skill-adversarial-security

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 046
- **Slug:** `refactor-adversarial-security`

## 1. Goal
Refactor `skill-adversarial-security` to leverage the new `security-audit` tools (de-duplication), extract sarcasm resources (decomposition), and add LLM-specific security checks (prompt injection).

## 2. Scope
- **Target Skill:** `.agent/skills/skill-adversarial-security`
- **New Directory:** `.agent/skills/skill-adversarial-security/resources/prompts/`
- **New File:** `resources/prompts/sarcastic.md`
- **Modified File:** `SKILL.md`
    - Remove inline OWASP checklist (link to `security-audit` instead).
    - Add instruction to run `security-audit/scripts/run_audit.py`.
    - Add Prompt Injection checks.

## 3. Deliverables
1. [ ] Created `resources/prompts/sarcastic.md` with persona and example prompts.
2. [ ] Updated `SKILL.md`:
    - Linked to `security-audit/resources/checklists/`.
    - Removed inline checklists.
    - Added Prompt Injection / Jailbreak checks.
    - Added mandate for `run_audit.py` reconnaissance.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
