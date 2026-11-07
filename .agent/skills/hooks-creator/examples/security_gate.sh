#!/usr/bin/env bash

# Dependency check (MANDATORY, SKILL.md Phase 2): exit 2 blocks with a system error.
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 2; }

# Use `jq` to parse JSON input. DO NOT use grep/regex on raw input.
input=$(cat)

# Extract content safely
if ! content=$(echo "$input" | jq -r '.tool_input.content // empty'); then
  echo "Error parsing input" >&2
  exit 2
fi

# Check for secrets (example pattern)
if echo "$content" | grep -qE "SECRET_KEY|API_TOKEN"; then
  echo "Blocked secret commitment" >&2
  # Allow exit 0 for structured denial
  cat <<EOF
{
  "decision": "deny",
  "reason": "Security Policy: Potential secret detected.",
  "systemMessage": "🔒 Security scanner blocked operation"
}
EOF
  exit 0
fi

# Allow by default
echo '{"decision": "allow"}'
