# VDD Verification Checklist (Gold Standard)

**Rule**: After enhancing a skill, you MUST verify it against this checklist. If ANY item fails, the skill is NOT done.

## 1. Data Safety & Integrity
- [ ] **No Overwrites**: Did you use `replace_file_content` tailored to specific lines? (Banned: `write_to_file` on existing files).
- [ ] **Backup**: Did you preserve the original intent of the skill? (e.g., didn't delete "Audit" capability while adding "Red Flags").

## 2. Anti-Laziness (The "TODO" Ban)
- [ ] **No Placeholders**: `grep -i "todo" SKILL.md` returns 0 results.
- [ ] **No Generic Excuses**: "Red Flags" are specific to the task, not generic "Don't be lazy".
    *   *Bad*: "Don't run without testing."
    *   *Good*: "Don't run `rm -rf` without dry-run first."

## 3. "Rich Skill" Compliance & Integrity
- [ ] **Examples Exist**: `examples/` directory is not empty.
- [ ] **Ref/File Match**: Every file referenced in `SKILL.md` (e.g., "See `examples/demo.py`") MUST exist on disk.
- [ ] **Token Efficiency**: Embed only critical Interaction Patterns (< 8 lines). Offload implementation details to `examples/`.
- [ ] **Path Consistency**:
    *   **Execution**: Commands use Repo-Relative paths (e.g., `python3 .agent/skills/...`).
    *   **References**: Docs use Skill-Relative paths (e.g., `See resources/template.md`).
    *   **NO Absolute Paths**: `/Users/...` is strictly forbidden.
- [ ] **Imperative Instructions**: Checked for passive words ("should", "can") and removed them.

## 4. Search Optimization (CSO)
- [ ] **Trigger-Based**: Description starts with "Use when [symptom/situation]...", NOT "This skill does...".
- [ ] **Concise**: Description is under 50 words.

## 5. Logic Hardening
- [ ] **Rationalization Table**: Does it contain at least 2 common excuses?
- [ ] **Red Flags**: Do they stop the agent from making a catastrophic mistake?
