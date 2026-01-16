# Task 015.1: Executable Skills & Schema Stubs

## Use Case Connection
- UC-1: Support Native Tool Use (Structure Preparation)

## Task Goal
Prepare the file structure and stubs for the new Tool Execution Subsystem. This involves defining where tools live (`.agent/tools`) and registering the "Executable Skills" category.

## Changes Description

### New Files
- `.agent/tools/schemas.py` — Stub file for defining JSON schemas.
  - Variable `TOOLS_SCHEMAS = []`

### Changes in Existing Files

#### File: `docs/SKILLS.md`
- **Section "Skills Catalog":**
  - Add new category "Executable Skills".
  - Mention `run_tests`, `git_ops` as future executable capabilities.

#### File: `System/Agents/01_orchestrator.md`
- **Note:** This is a textual prompt file.
- **Action:** Add a placeholder comment or section indicating where `execute_tool` logic description will eventually reside (if we are simulating logic in prompts) or just acknowledge this file needs review for the Logic phase.
- *Decision:* For Stubs, we will just verify the file exists and maybe add a comment.

## Test Cases

### End-to-end Tests
1. **TC-E2E-01:** Verify `schemas.py` is importable.
   - Input: Python script `import importlib.util...`
   - Expected Result: No `ImportError`, `TOOLS_SCHEMAS` is empty list.

### Regression Tests
- Check that existing skills still function (manual verification via `ls`).

## Acceptance Criteria
- [ ] `.agent/tools/schemas.py` exists with empty list.
- [ ] `docs/SKILLS.md` updated.
