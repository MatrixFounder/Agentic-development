#!/usr/bin/env bash
# Hook: validate_skill_hook.sh
# Event: AfterTool (write_file, replace_file_content, multi_replace_file_content)
# Purpose: Auto-validate skills when files in .agent/skills/ are modified.
#
# Exit codes:
#   0 + {"decision":"allow"} = pass (or file not in skills dir)
#   0 + {"decision":"deny", "reason":"..."} = validation failed, warn agent
#   2 = system error (jq missing, etc.)

# --- Dependency Check ---
command -v jq >/dev/null 2>&1 || { echo "jq is required for hooks" >&2; exit 2; }

# --- Parse Input ---
input=$(cat)

# Extract the file path from tool_input
# write_file uses "TargetFile", replace uses "TargetFile" too
file_path=$(echo "$input" | jq -r '.tool_input.TargetFile // .tool_input.target_file // empty')

if [ -z "$file_path" ]; then
  # No file path found — allow and exit
  echo '{"decision": "allow"}'
  exit 0
fi

# --- Check if file is inside .agent/skills/ ---
if [[ "$file_path" != *".agent/skills/"* ]]; then
  # Not a skill file — allow silently
  echo '{"decision": "allow"}'
  exit 0
fi

# --- Extract skill directory name ---
# Pattern: .../.agent/skills/<skill-name>/...
skill_name=$(echo "$file_path" | sed -n 's|.*\.agent/skills/\([^/]*\)/.*|\1|p')

if [ -z "$skill_name" ]; then
  echo '{"decision": "allow"}'
  exit 0
fi

# --- Locate skill directory ---
# Use $GEMINI_PROJECT_DIR if available, otherwise CWD from input
project_dir=$(echo "$input" | jq -r '.cwd // empty')
if [ -z "$project_dir" ]; then
  project_dir="."
fi

skill_dir="${project_dir}/.agent/skills/${skill_name}"
validator="${project_dir}/.agent/skills/skill-creator/scripts/validate_skill.py"

# --- Check if validator exists ---
if [ ! -f "$validator" ]; then
  echo '{"decision": "allow", "systemMessage": "⚠️ Skill validator not found. Skipping validation."}'
  exit 0
fi

# --- Run Validation ---
validation_output=$(python3 "$validator" "$skill_dir" 2>&1)
validation_exit=$?

if [ $validation_exit -eq 0 ]; then
  # Validation PASSED
  jq -n --arg skill "$skill_name" \
    '{decision: "allow", systemMessage: ("✅ Skill \"" + $skill + "\" passed validation.")}'
  exit 0
else
  # Validation FAILED — warn the agent but don't block
  # Use jq to safely construct JSON (prevents shell injection via heredoc)
  jq -n \
    --arg skill "$skill_name" \
    --arg output "$validation_output" \
    '{
      decision: "allow",
      systemMessage: ("⚠️ Skill \"" + $skill + "\" FAILED validation. Run validate_skill.py to fix."),
      hookSpecificOutput: {
        additionalContext: ("WARNING: Skill validation failed. Output: " + $output + ". Run: python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/" + $skill)
      }
    }'
  exit 0
fi
