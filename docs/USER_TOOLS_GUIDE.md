# User Guide: Troubleshooting Tools

If the Agent seems "stuck" or tools are failing, check this guide.

## Common Issues

### 1. "Path traversal detected"
- **Cause:** The agent tried to access a file outside the project folder (e.g., `/etc/hosts` or `../other_project`).
- **Fix:** Instruct the agent to only work within the current directory.

### 2. "Command not allowed"
- **Cause:** The agent tried to run a shell command via `run_tests` that isn't on the allowlist (e.g., `rm -rf`, `ls -la`).
- **Fix:** The `run_tests` tool is ONLY for running tests. Use `list_directory` to see files.

### 3. Tool Loop (Agent keeps calling same tool)
- **Cause:** The tool returns an error that the agent doesn't understand, so it tries again.
- **Fix:** Check the `tool` role message in the logs. If it says `FileNotFound`, tell the agent to check the path.

## How to Verify Tools
You can run the tool dispatcher manually to verify logic:

```bash
# Example: Read README.md
python3 -c 'from scripts.tool_runner import execute_tool; import json; print(execute_tool({"name": "read_file", "arguments": json.dumps({"path": "README.md"})}))'
```
