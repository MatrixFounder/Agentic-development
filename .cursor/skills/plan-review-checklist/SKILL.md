---
name: plan-review-checklist
description: Detailed checklist for verifying Development Plans.
version: 1.0
---
# Plan Review Checklist

## 1. Use Case Coverage
- [ ] **Total Coverage:** Every Use Case mapped to >= 1 Task?
- [ ] **Traceability:** Coverage table exists?

## 2. Structure & Formalism
- [ ] **Stub-First:** Every component has specific "Stub" and "Impl" phases/tasks?
- [ ] **Dependencies:** Task order respects dependencies?
- [ ] **Phasing:** Clear stages (Structure -> Logic -> Test)?

## 3. Task Descriptions
- [ ] **Existence:** File exists for every task in `plan.md`?
- [ ] **Naming:** Matches `task-{ID}-{SubID}-{slug}.md`?
- [ ] **Sections:** Contains Goal, Changes, Test Cases, Acceptance Criteria?
- [ ] **Depth:** Specific file paths and method signatures? (Without coding).

## Criticality Protocol
- 🔴 **BLOCKING:** Missing Use Case, Missing Task File, No "Stub-First" approach.
- 🟡 **MAJOR:** Missing coverage table, Vague dependencies.
- 🟢 **MINOR:** Formatting, missing "Notes".
