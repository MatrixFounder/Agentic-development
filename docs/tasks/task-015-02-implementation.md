# Task 015.2: Tool Dispatcher & Schema Implementation

## Use Case Connection
- UC-1: Agent Tool Execution
- UC-2: Error Handling
- UC-3: Fallback

## Task Goal
Implement the core logic for Structured Tool Calling: populate the schemas and implement the `execute_tool` dispatcher function and the orchestration loop.

## Changes Description

### New Files
- `src/utils/tool_dispatcher.py` (Proposed location for the Python dispatcher if the Orchestrator has a Python backend).
  - **Note:** If the Orchestrator is purely prompt-based (Markdown), we need to clarify WHERE `execute_tool` runs.
  - *Assumption:* The `execute_tool` logic provided in TASK is Python code. It must run *somewhere*. If the user (me) is the Orchestrator, I must run it. If there is a script `main.py` driving this, I modify it.
  - *Safety:* I will create `scripts/tool_runner.py` as a standalone utility for now, to be integrated by whatever driver exists.

### Changes in Existing Files

#### File: `.agent/tools/schemas.py`
- **Variable `TOOLS_SCHEMAS`:**
  - Populate with full JSON schemas for: `run_tests`, `git_status`, `git_add`, `git_commit`, `read_file`, `write_file`, `list_directory`.

#### File: `scripts/tool_runner.py` (NEW)
- **Function `execute_tool(tool_call)`:**
  - Implement logic for all tools defined in schemas.
  - Implement error handling (try/except).
  - Implement Path Traversal protection (check `path` is within `repo_root`).

## Test Cases

### End-to-end Tests
1. **TC-E2E-01:** Execute `read_file` via `tool_runner`.
   - Input: `{"name": "read_file", "arguments": "{\"path\": \"README.md\"}"}`
   - Expected Result: Content of README.md in JSON wrapper.

2. **TC-E2E-02:** Execute `run_tests` (mocked).
   - Input: `{"name": "run_tests"}`
   - Expected Result: Subprocess output.

### Unit Tests
1. **TC-UNIT-01:** `execute_tool` throws error on invalid tool name.
2. **TC-UNIT-02:** Path traversal check blocks `../../etc/passwd`.

## Acceptance Criteria
- [ ] `schemas.py` fully populated.
- [ ] `execute_tool` implemented and tested.
- [ ] Security checks (Path Traversal) active.
