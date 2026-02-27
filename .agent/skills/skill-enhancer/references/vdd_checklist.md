# VDD Verification Checklist (Gold Standard)

**Rule**: After enhancing a skill, you MUST verify it against this checklist. If ANY item fails, the skill is NOT done.

## 1. Data Safety & Integrity
- [ ] **No Overwrites**: Did you use `replace_file_content` tailored to specific lines? (Banned: `write_to_file` on existing files).
- [ ] **Backup**: Did you preserve the original intent of the skill? (e.g., didn't delete "Audit" capability while adding "Red Flags").

## 2. Graduated Language Check
- [ ] **No Placeholders**: `grep -i "todo" SKILL.md` returns 0 results.
- [ ] **No Generic Excuses**: "Red Flags" are specific to the task, not generic "Don't be lazy".
    *   *Bad*: "Don't run without testing."
    *   *Good*: "Don't run `rm -rf` without dry-run first — files cannot be recovered."
- [ ] **Graduated Style**: Safety-critical steps use `MUST` + reason. Behavioral steps explain "why" + use imperative. No bare `MUST` without rationale.

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
- [ ] **Prefix Logic**: Description starts with one of:
    *   `Use when...` (Triggers)
    *   `Guidelines for...` (Context)
    *   'Helps with...` (Context)
    *   'Helps to...` (Context)
    *   `Standards for...` (Rules)
    *   `Defines...` (Concepts)
- [ ] **Concise**: Description is under 50 words.
- [ ] **Pushiness**: Description includes edge-case triggers and adjacent domains to prevent under-triggering.

## 5. Logic Hardening
- [ ] **Rationalization Table**: Does it contain at least 2 common excuses?
- [ ] **Red Flags**: Do they stop the agent from making a catastrophic mistake?

## 6. Test Coverage
- [ ] **Evals Exist**: Skill has at least 2-3 test prompts (in `evals/evals.json` or documented inline).
