# Orchestrator: Tool Execution Subsystem

**Version:** 3.2.2
**Status:** Active

## Overview
The Orchestrator v3.2 introduces **Structured Tool Calling**, allowing agents to perform deterministic actions on the file system and git repository. This replaces the legacy regex-based command parsing with native LLM Function Calling.

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

## 📘 User Guide

### How to Enable Tools
Tools are enabled automatically if the Orchestrator prompt (`01_orchestrator.md`) includes the `Execute Tools` capability.

### Configuration
1. **Adding Allowed Commands:**
   Edit `scripts/tool_runner.py` -> `ALLOWED_TEST_COMMANDS` list.
   ```python
   ALLOWED_TEST_COMMANDS = [
       "pytest",
       "npm test",
       "cargo test" # Added
   ]
   ```

## 🛠 Developer Guide: Adding a New Tool

To add a new tool (e.g., `web_search`), follow these 3 steps:

### Step 1: Define Schema
Add the tool definition to `.agent/tools/schemas.py`:

```python
{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Searches the internet for documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
}
```

### Step 2: Implement Logic
Add the function to `scripts/tool_runner.py`:

```python
def web_search(query):
    # Implementation (e.g., calling DuckDuckGo API)
    return {"result": f"Search results for {query}..."}
```

### Step 3: Register in Dispatcher
Update the `execute_tool` function in `scripts/tool_runner.py`:

```python
# ... inside execute_tool
elif tool_name == "web_search":
    return web_search(**arguments)
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

## ❓ Troubleshooting

### Error: "Function definition not found"
- **Cause:** The schema is defined, but the function is not registered in `tool_runner.py`.
- **Fix:** Check Step 3 in Developer Guide.

### Error: "Path traversal detected"
- **Cause:** Tool tried to access a file outside the project root (e.g., `/tmp` or `../`).
- **Fix:** Use only relative paths or paths inside the project.

### Error: "Command not allowed"
- **Cause:** `run_tests` tried to run a command not in the whitelist.
- **Fix:** Update `ALLOWED_TEST_COMMANDS` in `tool_runner.py`.
