# Task 043: Refactor security-audit

> **Status:** ACTIVE
> **Created:** 2026-01-23
> **Owner:** Orchestrator

## 0. Meta Information
- **Task ID:** 043
- **Slug:** `refactor-security-audit`

## 1. Goal
Refactor `security-audit` skill to automate tooling and standardize checklists with high-grade security standards (SCSVS, SWC, Fuzzing), especially for Solidity.

## 2. Scope
- **Target Skill:** `.agent/skills/security-audit`
- **New Directories:**
  - `scripts/`
  - `resources/checklists/`
- **New Files:**
  - `scripts/run_audit.py` (Unified wrapper for slither/bandit/npm/cargo)
  - `resources/checklists/owasp_top_10.md`
  - `resources/checklists/solidity_security.md` (SCSVS, DeFi, Upgradability)
  - `resources/checklists/solana_security.md` (Anchor, Account Validation, PDAs)
  - `resources/checklists/fuzzing_invariants.md`
- **Modified File:** `SKILL.md` (Mandate script usage and "Hacker Mindset").

## 3. Deliverables
1. [x] Created `scripts/run_audit.py` with multi-language detection.
2. [x] Created `owasp_top_10.md`.
3. [x] Created `solidity_security.md` with SCSVS/SWC/DeFi references.
4. [ ] Created `solana_security.md`.
5. [x] Created `fuzzing_invariants.md`.
6. [ ] Updated `SKILL.md` to include Solana references.

## 4. Implementation Plan
See `docs/PLAN.md` for detailed steps.
