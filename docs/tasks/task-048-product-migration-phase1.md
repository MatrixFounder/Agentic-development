# Task: Phase 1 - Migration & Foundation (Week 1)

> **Status:** Done
> **Parent Initiative:** [Product Development Vision v3.2](../Backlog/product_development_vision_v3_2.md)

---

## 1. Executive Summary
**Objective:** Establish the v3 "Venture Builder" architecture by creating the `docs/product/` air-gapped directory and migrating the agent fleet from 2 agents (p01, p02) to the "Lean Five" (p00-p04), strictly following the v3.2 specification.

---

## 4. Implementation Steps

1.  **Structure Setup**:
    - [x] Create `docs/product/` directory (The Air Gap).

2.  **Agent Migration (Renaming)**:
    - [x] Rename `System/Agents/p01_product_analyst_prompt.md` -> `p02_product_analyst_prompt.md`.
    - [x] Rename `System/Agents/p02_product_reviewer_prompt.md` -> `p03_product_director_prompt.md`.

3.  **Agent Creation & Updates (The Lean Five)**:
    - [x] **Create** `p00_product_orchestrator` (New Dispatcher).
    - [x] **Create** `p01_strategic_analyst` (New Researcher).
    - [x] **Update** `p02_product_analyst` (Focus: Vision Synthesis only).
    - [x] **Update** `p03_product_director` (Focus: Adversarial VDD + Approval Hash).
    - [x] **Create** `p04_solution_architect` (New Solution Designer).

4.  **Verification**:
    - [x] Verify file existence and location.
    - [x] Verify prompts match v3.2 specs (roles, tools, io).

---

## 5. Definition of Done (DoD)

**Artifact Verification**
- [x] `docs/product/` exists.
- [x] System/Agents/ contains exactly: p00, p01, p02, p03, p04 (plus standard agents).

**Functional Verification**
- [x] `p00` prompt correctly lists dispatch logic.
- [x] `p03` prompt includes "Approval Hash" instruction.
