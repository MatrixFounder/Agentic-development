# Orchestrator: Tool Execution Subsystem

**Version:** 3.2.5
**Status:** Active

## Overview
The Orchestrator v3.2 introduces **Structured Tool Calling**, allowing agents to perform deterministic actions on the file system and git repository. This replaces the legacy regex-based command parsing with native LLM Function Calling.

## Table of Contents
- [Components](#components)
- [Security Model](#security-model)
- [User Guide](#-user-guide)
- [Developer Guide: Adding a New Tool](#-developer-guide-adding-a-new-tool)
- [Supported Tools](#supported-tools)
- [Troubleshooting](#-troubleshooting)
- [Manual Tool Verification](#-manual-tool-verification)

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

This guide walks through the complete process of adding a new tool to the system.

### Prerequisites
- Python 3.9+
- Understanding of JSON Schema format
- Familiarity with the tool dispatcher pattern

---

### Step 1: Design the Tool Interface

Before writing code, define:

| Question | Example Answer |
|----------|----------------|
| **What does the tool do?** | Generate unique ID for task archival |
| **What inputs does it need?** | `slug` (required), `proposed_id` (optional) |
| **What does it return?** | `filename`, `used_id`, `status`, `message` |
| **Is it read-only or mutating?** | Read-only (doesn't modify files) |

> [!TIP]
> Keep tools focused on ONE responsibility. If your tool does multiple things, split it.

---

### Step 2: Implement the Core Logic

Create a new file in `.agent/tools/` (e.g., `my_tool.py`):

```python
# .agent/tools/my_tool.py
"""
My Tool - Brief description of what it does.
"""
import os
from typing import Optional

def my_tool_function(
    required_param: str,
    optional_param: Optional[str] = None
) -> dict:
    """
    Main tool function.
    
    Args:
        required_param: Description of required parameter.
        optional_param: Description of optional parameter.
    
    Returns:
        dict with keys: result, status, message
    """
    # Validate inputs
    if not required_param:
        return {"status": "error", "message": "Missing required_param"}
    
    # Core logic here
    result = f"Processed: {required_param}"
    
    return {
        "result": result,
        "status": "success",
        "message": None
    }
```

**Best Practices:**
- ✅ Return a `dict` with consistent keys (`status`, `message`)
- ✅ Handle edge cases gracefully (return errors, don't raise exceptions)
- ✅ Keep the function pure when possible (no side effects)
- ❌ Don't perform file I/O unless that's the tool's purpose

---

### Step 3: Define the Schema

Add the tool definition to `.agent/tools/schemas.py`:

```python
# In TOOLS_SCHEMAS list:
{
    "type": "function",
    "function": {
        "name": "my_tool_function",
        "description": "Brief description shown to the LLM. Be specific about when to use.",
        "parameters": {
            "type": "object",
            "properties": {
                "required_param": {
                    "type": "string",
                    "description": "What this parameter means."
                },
                "optional_param": {
                    "type": "string",
                    "description": "Optional. What this does if provided."
                }
            },
            "required": ["required_param"]
        }
    }
}
```

> [!IMPORTANT]
> The `description` field is critical — the LLM uses it to decide when to call your tool.

---

### Step 4: Register in Dispatcher

Add the tool handler to `scripts/tool_runner.py`:

```python
# At the top of execute_tool function, add import handling:
elif name == "my_tool_function":
    import sys
    tools_path = repo_root / ".agent" / "tools"
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))
    
    from my_tool import my_tool_function
    
    required_param = args.get("required_param")
    if not required_param:
        return {"error": "Missing 'required_param'", "success": False}
    
    optional_param = args.get("optional_param")
    
    result = my_tool_function(
        required_param=required_param,
        optional_param=optional_param
    )
    result["success"] = result["status"] == "success"
    return result
```

---

### Step 5: Write Tests

Create `.agent/tools/test_my_tool.py`:

```python
import pytest
from my_tool import my_tool_function

class TestMyTool:
    def test_basic_usage(self):
        result = my_tool_function(required_param="test")
        assert result["status"] == "success"
        assert "test" in result["result"]
    
    def test_missing_required_param(self):
        result = my_tool_function(required_param="")
        assert result["status"] == "error"
    
    def test_with_optional_param(self):
        result = my_tool_function(required_param="test", optional_param="extra")
        assert result["status"] == "success"
```

Run tests:
```bash
cd .agent/tools && python -m pytest test_my_tool.py -v
```

---

### Step 6: Integration Test

Test via the dispatcher to ensure end-to-end functionality:

```bash
python -c "
from scripts.tool_runner import execute_tool
result = execute_tool({
    'name': 'my_tool_function',
    'arguments': {'required_param': 'hello'}
})
print(result)
assert result['success'], f'Failed: {result}'
print('✅ Integration test passed!')
"
```

---

### Step 7: Update Documentation

1. **`docs/ORCHESTRATOR.md`**: Add to Supported Tools table
2. **`docs/SKILLS.md`**: Add to Executable Skills section (if user-facing)
3. **`docs/ARCHITECTURE.md`**: Add to Available Tools table
4. **`docs/USER_TOOLS_GUIDE.md`**: Add troubleshooting entry if needed

---

### Checklist

| Step | Done |
|------|------|
| Core logic in `.agent/tools/my_tool.py` | ☐ |
| Schema in `.agent/tools/schemas.py` | ☐ |
| Handler in `scripts/tool_runner.py` | ☐ |
| Unit tests passing | ☐ |
| Dispatcher integration test passing | ☐ |
| Documentation updated | ☐ |

---

### Real Example: `generate_task_archive_filename`

See the implementation in:
- **Logic:** `.agent/tools/task_id_tool.py`
- **Tests:** `.agent/tools/test_task_id_tool.py` (29 tests)
- **Schema:** `.agent/tools/schemas.py` (search for `generate_task_archive_filename`)

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
| `generate_task_archive_filename` | Generates unique sequential ID for task archival. |

## ❓ Troubleshooting

### Error: "Function definition not found"
- **Cause:** The schema is defined, but the function is not registered in `tool_runner.py`.
- **Fix:** Check Step 4 in Developer Guide above.

### Error: "Path traversal detected"
- **Cause:** Tool tried to access a file outside the project root (e.g., `/tmp` or `../`).
- **Fix:** Use only relative paths or paths inside the project. Instruct the agent to work within the current directory.

### Error: "Command not allowed"
- **Cause:** `run_tests` tried to run a command not in the whitelist (e.g., `rm -rf`, `ls -la`).
- **Fix:** The `run_tests` tool is ONLY for running tests. Use `list_directory` to see files. To add new commands, update `valid_starts` in `tool_runner.py`.

### Tool Loop (Agent keeps calling same tool)
- **Cause:** The tool returns an error that the agent doesn't understand, so it tries again.
- **Fix:** Check the `tool` role message in the logs. If it says `FileNotFound`, tell the agent to check the path.

### Error: "Missing 'slug' argument" (generate_task_archive_filename)
- **Cause:** The tool requires a `slug` parameter to generate the filename.
- **Fix:** Provide a slug like `generate_task_archive_filename(slug="my-feature")`.

---

## 🔧 Manual Tool Verification

You can run the tool dispatcher manually to verify logic:

```bash
# Example: Read README.md
python3 -c 'from scripts.tool_runner import execute_tool; print(execute_tool({"name": "read_file", "arguments": {"path": "README.md"}}))'

# Example: List directory
python3 -c 'from scripts.tool_runner import execute_tool; print(execute_tool({"name": "list_directory", "arguments": {"path": "."}}))'

# Example: Generate task archive filename
python3 -c 'from scripts.tool_runner import execute_tool; print(execute_tool({"name": "generate_task_archive_filename", "arguments": {"slug": "my-feature"}}))'
```
