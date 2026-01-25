# Task 050: Framework Maintenance: Tools & Orchestrator Correction

## 0. Meta Information
- **ID:** 050
- **Slug:** framework-maintenance-tools
- **Context:** Maintenance task to fix inconsistencies in tool definitions (`schemas.py`) and documentation (`ORCHESTRATOR.md`).

## 1. Executive Summary
**Objective:** The user reported errors and inconsistencies regarding "tools" in `.agent/tools/schemas.py` and `System/Docs/ORCHESTRATOR.md`. Specifically, tools should be defined within skills, and `schemas.py` might contain outdated or incorrect entries. The documentation must also be updated to reflect the current architecture.

## 2. Use Cases

### UC-01: Cleanup .agent/tools/schemas.py
**Actors:** System, Developer
**Preconditions:** `schemas.py` exists and contains potentially incorrect definitions.
**Main Scenario:**
1. Analyze `.agent/tools/schemas.py`.
2. Identify tools that are "extra" or "incorrect" (e.g., legacy tools, implementation code mixed with schemas).
3. Align `schemas.py` with the "tools inside skills" paradigm.
4. Remove or refactor incorrect entries.

### UC-02: Fix System/Docs/ORCHESTRATOR.md
**Actors:** System, Developer
**Preconditions:** `ORCHESTRATOR.md` contains errors regarding tools.
**Main Scenario:**
1. Analyze `System/Docs/ORCHESTRATOR.md`.
2. Identify sections describing tool usage or definitions that are outdated.
3. Update specific sections to match the actual system behavior (Tools embedded in Skills).

## 3. Acceptance Criteria
- [x] `.agent/tools/schemas.py` contains only valid, necessary tool schemas/definitions.
- [x] `System/Docs/ORCHESTRATOR.md` correctly describes the tool system and references `schemas.py` or skills appropriately.
- [x] No regression in tool availability (native tools like `run_tests`, `git_ops`, etc. should remain if they are valid).

## 4. Open Questions
- What specifically defines an "extra" script in `schemas.py`? (Assumption: Scripts that should be in `skills/` or are unused).
