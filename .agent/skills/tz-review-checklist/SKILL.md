---
name: tz-review-checklist
description: Detailed checklist for verifying Technical Specifications (TZ).
version: 1.0
---
# TZ Review Checklist

## 1. Task Compliance
- [ ] **Requirements:** All user requirements covered?
- [ ] **Scope:** No unrequested features?
- [ ] **Goal:** Solves the core user problem?

## 2. Completeness (Use Cases)
- [ ] **Structure:** Name, Actors, Preconditions, Main Scenario, Alternatives, Postconditions.
- [ ] **Main Scenario:** Step-by-step, clear system/actor actions.
- [ ] **Alternatives:** Error handling, edge cases (empty inputs, network failures).
- [ ] **Acceptance Criteria:** Specific, measurable, verifiable.

## 3. Compatibility
- [ ] **Terminology:** Uses project terms?
- [ ] **Architecture:** Respects existing constraints?
- [ ] **Integrations:** correctly describes interaction with existing components?

## 4. Consistency
- [ ] **Internal:** No contradictions between UC-01 and UC-02.
- [ ] **Naming:** Same entities named identically.

## 5. Non-Functional
- [ ] **Performance:** Metrics defined?
- [ ] **Security:** Critical checks (auth, inputs)?

## Criticality Protocol
- 🔴 **BLOCKING:** Missing UC, contradiction with User Task, unmitigated critical risk.
- 🟡 **MAJOR:** Incomplete scenarios, vague criteria, term mismatches.
- 🟢 **MINOR:** Typos, phrasing.
