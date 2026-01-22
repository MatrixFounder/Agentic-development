---
name: skill-creator
description: "Guidelines for creating new Agent Skills following Anthropic standards and Gemini/Antigravity structures."
tier: 2
version: 1.0
---
# Skill Creator Guide

This skill provides the authoritative standard for creating new Agent Skills in this project. It combines the [Anthropic Skills Standard](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) with our local architecture rules.

## 1. Anatomy of a Skill

Every skill MUST strictly follow this directory structure:

```
skill-name/
├── SKILL.md (Required)
│   ├── YAML frontmatter (name, description, tier, version)
│   └── Markdown body (instructions)
└── Bundled Resources (Optional)
    ├── scripts/       # Executable code (Python/Bash)
    ├── examples/      # Reference implementations
    └── resources/     # Templates and other static assets
```

> [!WARNING]
> **Prohibited Files:** Do NOT create `README.md`, `CHANGELOG.md`, `INSTALLATION.md`, or other aux docs inside the skill folder. All instruction must be in `SKILL.md`.

## 2. Frontmatter Standard (Project Specific)

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
*   **1 (Phase-Triggered)**: Skills loaded automatically when entering a specific phase (e.g., `requirements-analysis` for Analysis Phase).
*   **2 (Extended)**: Specialized skills loaded only when explicitly needed or requested (e.g., `skill-creator`, `skill-reverse-engineering`). *Default for most new skills.*

## 3. Skill Content Guidelines

### Philosophy
Follow the **"Progressive Disclosure"** principle:
1.  **High-Level Summary**: Start with *what* and *why*.
2.  **Core Instructions**: The specific steps the agent must take.
3.  **Details/Examples**: Concrete examples of Good vs Bad output.

### Best Practices
1.  **Be Imperative**: Use "You MUST", "DO NOT". Avoid "It is suggested...".
2.  **Modular**: Do not duplicate instructions from `skill-core-principles` or `skill-safe-commands`. Reference them instead.
3.  **Atomic**: A skill should do ONE thing well. Split complex skills into smaller ones.
4.  **No Hallucinations**: Do not assume file paths. Use relative paths or ask the user.

## 4. Creation Process Compliance

When creating a new skill, you **MUST** strictly follow this sequence:

1.  **Check Duplicates**: Verify in `System/Docs/SKILLS.md`.
2.  **Initialize**: Use the automation script (Preferred) or create manually.
    ```bash
    # Usage: python3 .agent/skills/skill-creator/scripts/init_skill.py <skill-name> --tier [0|1|2]
    python3 .agent/skills/skill-creator/scripts/init_skill.py my-new-skill --tier 2
    ```
    *This creates the directory, templates, and required subfolders.*

3.  **Edit Content**: Modify `SKILL.md` with your specific instructions.
4.  **Validate**: Run the validation script to ensure compliance.
    ```bash
    python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/my-new-skill
    ```
5.  **Register**: Add the skill to `System/Docs/SKILLS.md`.

## 5. Scripts Reference

The `skill-creator` includes automation scripts located in `.agent/skills/skill-creator/scripts/`:

*   **`init_skill.py`**: Generates a compliant skill skeleton.
    *   Creates `scripts/`, `examples/`, `resources/`.
    *   Generates `SKILL.md` with valid YAML frontmatter.
*   **`validate_skill.py`**: Checks for compliance errors.
    *   Verifies folders (no `assets/` or `references/`).
    *   Verifies YAML frontmatter (`tier`, `version`, `name`).
    *   Checks for prohibited files (`README.md`).
