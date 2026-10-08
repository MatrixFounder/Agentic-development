# Task 050: Framework Maintenance & Tool Cleanup

## 0. Meta Information
- **ID:** 050
- **Slug:** framework-maintenance-tools
- **Base revision:** `9f1c2ab`
- **Context:** Maintenance task to fix inconsistencies in tool definitions.

## 1. Executive Summary
**Objective:** The user reported errors in `.agent/tools/schemas.py`. Tools should be defined within skills, and the central schema file might contain outdated entries.

## 2. Use Cases

### UC-01: Cleanup Tool Schemas
**Actors:** Developer
**Preconditions:** `schemas.py` contains incorrect definitions.
**Main Scenario:**
1. Analyze `.agent/tools/schemas.py`.
2. Identify "extra" or "legacy" tools.
3. Remove or refactor incorrect entries to align with "Tools in Skills" architecture.

### UC-02: Fix Documentation
**Main Scenario:**
1. Analyze `System/Docs/ORCHESTRATOR.md`.
2. Update tool usage sections to match `schemas.py` changes.

## 3. Changes Description

### Changes in Existing Files

#### File: `.agent/tools/schemas.py`
**Variable `ALL_TOOLS`:**
- Remove `legacy_tool_definition`.
- Ensure all other tools reference their correct schema classes.

## 4. Acceptance Criteria
- [ ] `.agent/tools/schemas.py` contains only valid tool schemas.
- [ ] Documentation (`ORCHESTRATOR.md`) references the correct tool system.
- [ ] No regression in native tool availability (`run_tests`, `git_ops`).

## 5. Test Cases
### End-to-end Tests
1. **TC-E2E-01:** List Tools
   - Action: Run agent and request tool list.
   - Expected Result: No crashes, no keys for legacy tools.
