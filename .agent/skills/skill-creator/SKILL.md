---
name: skill-creator
description: "Guidelines for creating new Agent Skills following Anthropic standards and Gemini/Antigravity structures."
tier: 2
version: 1.0
---
# Skill Creator Guide

This skill provides the authoritative standard for creating new Agent Skills in this project. It combines the [Anthropic Skills Standard](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) with our local architecture rules.

## 1. Anatomy of a Skill

Every skill **MUST** strictly follow this directory structure. This structure is non-negotiable for "Rich Skills".

```
skill-name/
├── SKILL.md (Required)
│   ├── YAML frontmatter (name, description, tier, version)
│   └── Markdown body (instructions)
└── Bundled Resources (Optional)
    ├── scripts/       # Executable code (Python/Bash) for the skill to use
    ├── examples/      # Reference implementations and usage examples
    └── resources/     # Templates, static assets, and data files
```

> [!WARNING]
> **Prohibited Files:** Do NOT create `README.md`, `CHANGELOG.md`, `INSTALLATION.md`, or other aux docs inside the skill folder. All instructions must be in `SKILL.md`.

## 2. Rich Skill Philosophy

A "Rich Skill" is not just a text file. It is a comprehensive toolkit.
The user expects high-quality skills that include **Examples** and **Templates**.

### When to use `examples/`?
- **User Stories**: "Show me how to use this."
- **Files**: `examples/usage_demo.py`, `examples/complex_scenario.md`.
- **Purpose**: Reduce hallucination by providing ground-truth input/output pairs.

### When to use `resources/`?
- **Templates**: `resources/boilerplate.py`, `resources/config_template.yaml`.
- **Data**: `resources/lookup_table.csv`.
- **Purpose**: Speed up execution by giving the agent ready-to-copy assets.

## 3. Frontmatter & Metadata

The YAML frontmatter is CRITICAL for the Orchestrator's loading logic.

```yaml
---
name: skill-my-new-capability
description: "One-line summary of what this skill enables the agent to do."
tier: [0|1|2]
version: 1.0
---
```

### Protocol: Tier Definitions
*   **0 (Bootstrap)**: Critical system skills loaded at session start (e.g., `core-principles`, `safe-commands`). *Rarely used for new skills.*
*   **1 (Phase-Triggered)**: Skills loaded automatically when entering a specific phase (e.g., `requirements-analysis` for Analysis Phase) or working on a specific requirement (e.g., `planning-decision-tree` for Planning Phases).
*   **2 (Extended)**: Specialized skills loaded only when explicitly needed or requested (e.g., `skill-creator`, `skill-reverse-engineering`). *Default for most new skills.*

## 4. Skills as Code Philosophy (TDD)

We treat skills as **executable code for agents**. You must test them.
We follow a **Red-Green-Refactor** workflow:

1.  **RED (Fail)**: Run a "pressure scenario" with a subagent *without* the skill.
    *   Observe the failure.
    *   Record the specific **rationalization** (excuse) the agent used (e.g., "I'll test later").
2.  **GREEN (Pass)**: Write the minimal skill instruction to close that specific loophole.
3.  **REFACTOR**: Optimize for clarity and "Claude Search Optimization" (CSO).

## 5. Claude Search Optimization (CSO)

The `description` frontmatter field is the **single most important line**. It determines if your skill is loaded.

### Rule: "Use when [TRIGGER]"
*   **BAD**: "Guide for TDD workflow." (Summarizes content - Model may skip loading)
*   **GOOD**: "Use when implementing a new feature or fixing a bug." (Triggering condition)

**Constraint**: Keep descriptions under 50 words. Focus on *symptoms* and *triggers*, not solutions.

## 6. Hardening Skills (Rationalization Management)

Agents (like humans) will find excuses to skip steps. You must explicitly forbid these "rationalizations".

### The "Red Flags" Section
Every skill MUST include a list of Red Flags - specific excuses the agent might make.

*   *Example*: "Stop if you think 'I already tested manually'. Delete code and start over."

## 7. Writing High-Quality Instructions

Use the **Template** found in `resources/SKILL_TEMPLATE.md` as your starting point.

### Section Guidelines:
1.  **Purpose**: Define the "Why".
2.  **Red Flags**: Immediate "Stop and Rethink" triggers.
3.  **Capabilities**: Bulleted list of what is possible.
4.  **Instructions**: Imperative, step-by-step algorithms.
5.  **Examples (Few-Shot)**: Input -> Output pairs.
    *   *Reference*: See `examples/SKILL_EXAMPLE_LEGACY_MIGRATOR.md` for a **Gold Standard** example of a rich skill.

## 8. Creation Process

When creating a new skill, you **MUST** strictly follow this sequence:

1.  **Check Duplicates**: Verify in `System/Docs/SKILLS.md`.
2.  **Initialize**:
    ```bash
    python3 .agent/skills/skill-creator/scripts/init_skill.py my-new-skill --tier 2
    ```
3.  **Populate**:
    *   **MANDATORY**: Edit the auto-generated `SKILL.md` (it already contains the template).
    *   **MANDATORY**: Fill in the "Red Flags" and "Use when..." description.
4.  **Validate**:
    ```bash
    python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/my-new-skill
    ```
5.  **Register**: Add to `System/Docs/SKILLS.md`.

## 9. Scripts Reference

*   **`init_skill.py`**: Generates a compliant skill skeleton (`scripts/`, `examples/`, `resources/`) using the rich template.
*   **`validate_skill.py`**: Enforces folder structure, frontmatter compliance, and CSO rules (description format).
