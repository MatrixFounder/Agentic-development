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

## 4. Content Guidelines

### Philosophy
Follow the **"Progressive Disclosure"** principle:
1.  **High-Level Summary**: Start with *what* and *why*.
2.  **Core Instructions**: The specific steps the agent must take.
3.  **Details/Examples**: Concrete examples of Good vs Bad output.

### Best Practices
1.  **Be Imperative**: Use "You MUST", "DO NOT". Avoid "It is suggested...".
    *   *Bad*: "You could check the file..."
    *   *Good*: "1. Read the file. 2. If X, do Y."
2.  **Modular**: Do not duplicate instructions from `skill-core-principles` or `skill-safe-commands`. Reference them instead.
3.  **Atomic**: A skill should do ONE thing well. Split complex skills into smaller ones.
4.  **No Hallucinations**: Do not assume file paths. Use relative paths or ask the user.
5.  **Use Examples**: Include "Input -> Output" blocks (Few-Shot) to ground the model.

## 5. Writing High-Quality Instructions (`SKILL.md`)

Use the **Template** found in `resources/SKILL_TEMPLATE.md` as your starting point.

### Section Guidelines:
1.  **Purpose**: Define the "Why".
2.  **Capabilities**: Bulleted list of what is possible.
3.  **Instructions**: Imperative, step-by-step algorithms.
4.  **Examples (Few-Shot)**:
    *   Include "Input -> Output" blocks directly in markdown or reference files in `examples/`.
    *   Contrast **Good vs Bad** patterns.

## 6. Creation Process

When creating a new skill, you **MUST** strictly follow this sequence:

1.  **Check Duplicates**: Verify in `System/Docs/SKILLS.md`.
2.  **Initialize**:
    ```bash
    python3 .agent/skills/skill-creator/scripts/init_skill.py my-new-skill --tier 2
    ```
    *This creates the directory, templates, and required subdirectories.*
3.  **Populate**:
    *   **MANDATORY**: Copy content from `.agent/skills/skill-creator/resources/SKILL_TEMPLATE.md` into your new `SKILL.md`.
    *   **MANDATORY**: Create at least one example file in `examples/` or an example block in `SKILL.md`.
4.  **Validate**:
    ```bash
    python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/my-new-skill
    ```
5.  **Register**: Add the skill to `System/Docs/SKILLS.md`.

## 7. Scripts Reference

The `skill-creator` includes automation scripts located in `.agent/skills/skill-creator/scripts/`:

*   **`init_skill.py`**: Generates a compliant skill skeleton.
    *   Creates `scripts/`, `examples/`, `resources/`.
    *   Generates `SKILL.md` with valid YAML frontmatter.
*   **`validate_skill.py`**: Checks for compliance errors.
    *   Verifies folders (no `assets/` or `references/`).
    *   Verifies YAML frontmatter (`tier`, `version`, `name`).
    *   Checks for prohibited files (`README.md`).
