# Orchestrator: Tool Execution Subsystem

**Version:** 3.1.2
**Status:** Active

## Overview
The Orchestrator v3.1 introduces **Structured Tool Calling**, allowing agents to perform deterministic actions on the file system and git repository. This replaces the legacy regex-based command parsing.

## Components

### 1. Tool Schemas
- **Location:** `.agent/tools/schemas.py`
- **Format:** OpenAI-compatible JSON Schema (`tools` array).
- **Import:** Dynamic loading via `importlib` (due to hidden directory).

### 2. Dispatcher (`execute_tool`)
- **Location:** `scripts/tool_runner.py`
- **Function:** `execute_tool(tool_call)`
- **Input:** `tool_call` object (or dict) with `function.name` and `function.arguments`.
- **Output:** Dict (JSON-serializable) with fields like `output`, `error`, `success`.

## Security Model

### Path Traversal Protection
All file operations (`read_file`, `write_file`, `list_directory`) are restricted to the **Project Root**.
- **Mechanism:** `is_safe_path()` checks if the resolved path starts with `repo_root`.
- **Failure:** Returns `{"error": "Path traversal detected", "success": False}`.

### Command Whitelisting
The `run_tests` tool prevents arbitrary shell execution.
- **Allowed commands must start with:** `pytest`, `python -m pytest`, `npm test`.

## Usage in System Prompts

The Orchestrator injects the tools into the API call:
```python
response = client.chat.completions.create(
    model="grok-beta",
    messages=...,
    tools=TOOLS_SCHEMAS, # Loaded dynamically
    tool_choice="auto"
)
```

## Supported Tools

| Tool | Description |
|------|-------------|
| `run_tests` | Runs project tests (pytest). |
| `read_file` | Reads file content. |
| `write_file` | Writes file content. |
| `list_directory` | Lists directory contents. |
| `git_status` | Checks repo status. |
| `git_add` | Stages files. |
| `git_commit` | Commits changes. |
