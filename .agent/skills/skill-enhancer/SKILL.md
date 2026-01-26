---
name: skill-enhancer
description: Use when you need to audit, fix, or improve an existing agent skill to meet Gold Standard compliance.
tier: 2
version: 1.0
---
# Skill Enhancer

**Purpose**: This meta-skill analyzes other skills for compliance with TDD and CSO standards and guides the agent through upgrading them.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll just add the sections blindly" -> **WRONG**. You must understand *why* the skill fails before fixing it.
- "The description is close enough" -> **WRONG**. It must start with "Use when".
- "Examples are optional" -> **WRONG**. "Rich Skills" mandate examples.

## 2. Capabilities
- **Audit**: Detect gaps (missing Red Flags, poor CSO, passive voice) using `analyze_gaps.py`.
- **Plan**: Propose specific content improvements using `resources/refactoring_patterns.md`.
- **Execute**: Apply refactoring patterns to upgrade the skill.

## 3. Instructions

### Phase 1: Audit
1.  **Run Analyzer**: `python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/<target-skill>`.
2.  **Review Gaps**: Read the output. If Gaps found, proceed to Phase 2.

### Phase 2: Plan
1.  **Read Target Skill**: Read the content of the target skill.
2.  **Draft Improvements**:
    *   *Red Flags*: Identify 2-3 likely agent excuses for *this specific task*.
    *   *Rat. Table*: Create counter-arguments.
    *   *CSO*: Rewrite description to "Use when [TRIGGER]...".
3.  **Confirm**: Ensure improvements align with the "Skills as Code" philosophy.

### Phase 3: Execute
1.  **Update File**: Edit the target `SKILL.md` to insert the new sections.
    *   **CRITICAL**: Use `replace_file_content` or `multi_replace_file_content`.
    *   **DO NOT** use `write_to_file` to overwrite existing content (Data Loss Risk).
    *   *Tip*: Use `resources/refactoring_patterns.md` (Coming in Iteration 2) for style guide.
2.  **Verify**: Re-run `analyze_gaps.py`. Expect output "No Gaps Found".

### Phase 4: Final VDD Check
1.  **Read Checklist**: Open `resources/vdd_checklist.md`.
2.  **Self-Correction**: Verify your work against the 5 criteria (Data Safety, Anti-Laziness, etc.).
3.  **Refine**: If any check fails (e.g., found "TODO"), fix it immediately.

## 4. Best Practices

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| **Specific Red Flags**: "Don't skip tests" | **Generic Red Flags**: "Don't be lazy" |
| **Trigger-Based Desc**: "Use when debugging race conditions" | **Summary Desc**: "Guide for debugging" |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "The skill is too simple for Red Flags" | Simple skills are skipped most often. Explicit rules prevent this. |
| "I don't have time to write examples" | Examples save time by preventing hallucinations later. |

## 5. Examples (Few-Shot)
> [!TIP]
> See `examples/usage_example.md` for a complete **Before & After** walkthrough of upgrading a legacy skill.

**Input:**
```bash
python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/target-skill
```

**Output:**
```text
⚠️  Gaps Detected...
Recommendation: Run 'Execute Improvement Plan'...
```

## 6. Resources
- `scripts/analyze_gaps.py`: The gap detection tool.
