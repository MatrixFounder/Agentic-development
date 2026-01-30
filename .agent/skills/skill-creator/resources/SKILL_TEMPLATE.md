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
- "[Common excuse 1]" -> [Why this is wrong]
- "[Common excuse 2]" -> [Why this is wrong]

## 2. Capabilities
List what this skill allows the agent to do.
- [Capability 1]
- [Capability 2]

## 3. Instructions
Provide step-by-step instructions for the agent. Use imperative mood.

### [Phase/Action 1]
1.  **Step 1**: [Instruction]
2.  **Step 2**: [Instruction]
    - *Tip*: [Sub-instruction or nuance]

### [Phase/Action 2]
...

## 4. Workflows (Optional)
For complex tasks, use a checklist:
```markdown
- [ ] Analysis
- [ ] Execution
- [ ] Verification
```

## 4. Best Practices & Anti-Patterns

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| [Best practice] | [Common mistake] |
| [Best practice] | [Common mistake] |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "[Excuse 1]" | "[Counter-argument]" |
| "[Excuse 2]" | "[Counter-argument]" |

## 5. Examples (Few-Shot)
Refer to `examples/` directory for full files, or include short snippets here.

**Input:**
```
[User Request]
```

**Output:**
```
[Ideal Agent Response/Action]
```

## 6. Resources
Describe the usage of files in `resources/` (templates, assets) and scripts in `scripts/`.
- `scripts/helpers.py`: [Description]
- `resources/template.json`: [Description]
