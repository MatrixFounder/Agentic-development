#!/usr/bin/env bash

# Dependency check
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }

# Get recent git commits for context
# Suppress errors if not a git repo
context=$(git log -5 --oneline 2>/dev/null || echo "No git history")

# Return as JSON
# Use proper escaping for JSON strings if context is complex, 
# but for simple text, jq --arg is safer.
jq -n --arg ctx "Recent commits:\n$context" '{
  hookSpecificOutput: {
    hookEventName: "BeforeAgent",
    additionalContext: $ctx
  }
}'
