#!/usr/bin/env bash
# Hook: validate_skill_hook.sh
# Event: PostToolUse (Write, Edit)
# Purpose: Auto-validate skills when files in .agent/skills/ are modified.
#
# Claude Code hooks receive tool input via stdin as JSON.
# Exit codes:
#   0 = allow (stdout is shown to Claude as feedback)
#   2 = block

# --- Parse Input ---
input=$(cat)

# Extract file path from the tool input JSON
# Write tool uses "file_path", Edit tool uses "file_path"
file_path=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Try common field names
    path = data.get('file_path') or data.get('path') or data.get('TargetFile') or data.get('target_file') or ''
    print(path)
except:
    print('')
" 2>/dev/null)

if [ -z "$file_path" ]; then
  # No file path found — allow silently
  exit 0
fi

# --- Check if file is inside .agent/skills/ ---
if [[ "$file_path" != *".agent/skills/"* ]]; then
  # Not a skill file — allow silently
  exit 0
fi

# --- Extract skill directory name ---
# Pattern: .../.agent/skills/<skill-name>/...
skill_name=$(echo "$file_path" | sed -n 's|.*\.agent/skills/\([^/]*\)/.*|\1|p')

if [ -z "$skill_name" ]; then
  exit 0
fi

# --- Locate validator ---
script_dir="$(cd "$(dirname "$0")/../.." && pwd)"
skill_dir="${script_dir}/.agent/skills/${skill_name}"
validator="${script_dir}/.agent/skills/skill-creator/scripts/validate_skill.py"

if [ ! -f "$validator" ]; then
  echo "Skill validator not found at ${validator}. Skipping validation."
  exit 0
fi

# --- Run Validation ---
validation_output=$(python3 "$validator" "$skill_dir" 2>&1)
validation_exit=$?

if [ $validation_exit -eq 0 ]; then
  echo "Skill \"${skill_name}\" passed validation."
  exit 0
else
  echo "BLOCKED: Skill \"${skill_name}\" FAILED validation."
  echo "Output: ${validation_output}"
  echo "Fix and retry, or run: python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/${skill_name}"
  exit 2
fi
