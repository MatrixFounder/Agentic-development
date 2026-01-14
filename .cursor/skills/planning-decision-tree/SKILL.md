---
name: planning-decision-tree
description: Decision tree for breaking down tasks and prioritizing work.
version: 1.1
---
# Planning Decision Tree

## 1. Task Breakdown Strategy

### Core Logic: Stub-First & E2E
**CRITICALLY IMPORTANT:** You must split every functional requirement into two distinct task types:

1. **Phase 1: Structure & Stubs**
   - **Goal:** Create file structure, class definitions, method signatures, and **STUBS**.
   - **Action:** `return None` or hardcoded values.
   - **Verification:** Write E2E test that passes on these stubs (asserting hardcoded values).
   - **Task Tag:** `[STUB CREATION]`

2. **Phase 2: Logic Implementation**
   - **Goal:** Replace stubs with real logic.
   - **Action:** Implement algorithms, DB queries, API calls.
   - **Verification:** Update E2E test to assert real values. Add Unit Tests.
   - **Task Tag:** `[LOGIC IMPLEMENTATION]`

**Decision Rule:**
- IF task involves writing code -> Split into Stub + Impl.
- IF task is configuration/setup -> Single task.

## 2. Decomposition Levels
- **Too Complex?** (e.g., "Implement Auth") -> Break into "User Model", "Registration Service", "Login Service".
- **Too Simple?** (e.g., "Add one field") -> Combine with related tasks if safe.
- **Dependency?** -> Plan dependencies (Models, DB) BEFORE dependent services.

## 3. Concreteness Rules
- **For New Projects:** Define directory structure, class names, method signatures.
- **For Modifications:** Specify **exact file paths** and **methods** to change.

## 4. Prioritization
1. **Critical:** Core Architecture, Blockers, Database Schemas.
2. **High:** Main Business Logic (Stub -> Impl).
3. **Medium:** Edge cases, Error handling.
