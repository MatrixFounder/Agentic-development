#!/usr/bin/env bash
# Read hook input from stdin
input=$(cat)

# Dependency check
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }

# Extract tool name safely
tool_name=$(echo "$input" | jq -r '.tool_name')

# Log to stderr (visible in terminal if hook fails, or captured in logs)
echo "Logging tool: $tool_name" >&2

# Log to file (ensure directory exists in real usage)
# In production, use absolute paths for logs
echo "[$(date)] Tool executed: $tool_name" >> .gemini/tool-log.txt

# Return success (exit 0) with empty JSON
echo "{}"
exit 0
