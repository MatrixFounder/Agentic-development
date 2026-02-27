---
name: skill-[name]
description: Use when [TRIGGER: specific symptoms or situations]...
tier: [TIER_VALUE] # See .agent/rules/skill_standards.yaml
version: 1.0
---
# [Skill Name]

**Purpose**: [Detailed explanation of WHY this skill exists and WHAT problem it solves]

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "[Common excuse 1]" -> [Why this is wrong — explain the consequence]
- "[Common excuse 2]" -> [Why this is wrong — explain the consequence]

## 2. Capabilities
List what this skill allows the agent to do.
- [Capability 1]
- [Capability 2]

## 3. Execution Mode
- **Mode**: [prompt-first | script-first | hybrid]
- **Why this mode**: [Short rationale for this skill]

## 4. Script Contract
Use this section when mode is `script-first` or `hybrid`.
- **Command(s)**:
  - `python3 scripts/[tool].py --arg value`
- **Inputs**: [required args/files/config]
- **Outputs**: [artifacts/logs/exit behavior]
- **Failure semantics**: [non-zero exit, error schema]
- **Idempotency**: [how repeated runs behave]
- **Dry-run support**: [yes/no and flag]

## 5. Safety Boundaries
- **Allowed scope**: [path/module/target constraints]
- **Default exclusions**: [system/non-target areas]
- **Destructive actions**: [must be explicit opt-in, never default]
- **Optional artifacts**: [whether absence is blocking or non-blocking]

## 6. Validation Evidence
- **Local verification**: [commands/checks]
- **Expected evidence**: [files, logs, structured output]
- **CI signal**: [job/check name if available]

## 7. Instructions
Provide step-by-step instructions. Use graduated language:
- **Safety-critical** steps: `MUST` + explain why
- **Behavioral** steps: Explain why + imperative verb

### [Phase/Action 1]
1.  **Step 1**: [Instruction]
2.  **Step 2**: [Instruction]
    - *Tip*: [Sub-instruction or nuance]

### [Phase/Action 2]
...

## 8. Workflows (Optional)
For complex tasks, use a checklist:
```markdown
- [ ] Analysis
- [ ] Execution
- [ ] Verification
```

## 9. Best Practices & Anti-Patterns

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| [Best practice] | [Common mistake] |
| [Best practice] | [Common mistake] |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "[Excuse 1]" | "[Counter-argument]" |
| "[Excuse 2]" | "[Counter-argument]" |

## 10. Examples (Few-Shot)
Refer to `examples/` directory for full files, or include short snippets here.

**Input:**
```
[User Request]
```

**Output:**
```
[Ideal Agent Response/Action]
```

## 11. Resources
Describe the usage of files in `assets/`, `references/`, and scripts in `scripts/`.
- `scripts/helpers.py`: [Description]
- `assets/template.json`: [Description]
- `references/guidelines.md`: [Description]

## 12. Evals (Optional but Recommended)
Define 2-3 test prompts in `evals/evals.json` — see skill-creator §14 for format.
