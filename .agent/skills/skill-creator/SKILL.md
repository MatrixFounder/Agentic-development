---
name: skill-creator
description: Guidelines for creating new Agent Skills following Gold Standard structures. Use when defining new capabilities or upgrading existing skills.
tier: 2
version: 1.2
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
    ├── examples/      # FEW-SHOT TRAINING: Input/Output pairs to teach the Agent
    ├── assets/        # USER OUTPUT: Templates/Files to be given to User or used in output
    ├── references/    # AGENT KNOWLEDGE: Compendiums, Specs, Guidelines, Schemas
    └── scripts/       # EXECUTABLE LOGIC: Python/Bash tools (if logic > 5 lines)
```

> [!WARNING]
> **Prohibited Files:** Do NOT create `README.md`, `CHANGELOG.md`, `INSTALLATION.md`, or other aux docs inside the skill folder. All instructions must be in `SKILL.md`.

## 2. Rich Skill Philosophy (Hybrid Standard)

A "Rich Skill" is comprehensive. We separate files by their **Semantic Purpose** to help the Agent understand *why* it is reading a file.

### `examples/` (The "Train" Data)
*   **Purpose**: Teach the Agent **Behavior**.
*   **Content**: "When user says X, do Y."
*   **Files**: `examples/usage_demo.py`, `examples/complex_scenario.md`.
*   **Rule**: Use these to reduce hallucination on complex flows.

### `assets/` (The "Material" Data)
*   **Purpose**: Provide materials for the **User**.
*   **Content**: "Here is the template you asked for."
*   **Files**: `assets/boilerplate.py`, `assets/logo.svg`, `assets/report_template.md`.
*   **Rule**: The Agent does not "learn" from these; it indiscriminately uses/copies them.

### `references/` (The "Knowledge" Data)
*   **Purpose**: Provide context for the **Agent**.
*   **Content**: "Here are the rules/specs you must follow."
*   **Files**: `references/api_spec.yaml`, `references/design_guidelines.md`.
*   **Rule**: Heavy context that is read only when needed.

### `scripts/` (The "Tool" Data)
*   **Purpose**: **Execute** logic reliably.
*   **Content**: Python scripts for deterministic tasks.

## 3. Script-First Methodology (Opt O6a)

**CRITICAL RULE**: Agents are terrible at executing complex algorithmic logic from text instructions.
If your skill requires logic (loops, conditions, parsing, scanning), you **MUST** write a Python script in `scripts/`.

- **❌ Bad (Text)**: "Go through every file, check if it imports X, then if it does, check Y..."
- **✅ Good (Script)**: "Run `python scripts/scanner.py`. It produces `report.json`."

> [!IMPORTANT]
> **The 5-Line Logic Limit:** If a step in `SKILL.md` requires more than 5 lines of logical "if/then/else" text to explain, **IT MUST BE A SCRIPT**.

## 4. Frontmatter & Metadata

The YAML frontmatter is CRITICAL for the Orchestrator's loading logic.

- **Frontmatter** (YAML): Contains `name` and `description` fields (required), plus optional fields like `tier`, `version`, `license`, `metadata`, and `compatibility` etc.

```yaml
---
name: skill-my-new-capability
description: "One-line summary of what this skill enables the agent to do."
tier: [0|1|2]
version: 1.0
---
```

### Protocol: Tier Definitions
Run `python3 scripts/init_skill.py --help` to see the available Tiers for your project.
> [!IMPORTANT]
> **DO NOT** attempt to guess tiers or read configuration files manually. The script handles complex merging logic (Defaults + Project Overrides). Always trust the script output.

## 5. Token Efficiency (Global Rule)

To prevent context window saturation, we strictly enforce limits on inline content:

### The 12-Line Rule
*   **PROHIBITED**: Inline code blocks, templates, or examples larger than **12 lines**.
*   **REQUIRED**: Extract large blocks to `examples/`, `assets/`, or `references/` and reference them.
    *   *Bad*: A 20-line JSON object inline.
    *   *Good*: "See `examples/payload.json`."

### Why?
*   Skills are read frequently.
*   Large inline examples multiply token costs.
*   External files are only read when needed.

## 6. Anti-Laziness & AGI-Agnostic Language

Agents are lazy by default. We must use **Imperative, Deterministic Language**.
We assume the agent will **attempt** to skip steps. Instructions must be defensive. "AGI-Agnostic" (work for Model X, Model Y, and future Model Z).

### Prohibited Words (Weak Language)
You **MUST NOT** use these weak words. They trigger lazy behavior.

| ❌ Weak / Prohibited | ✅ Strong / Required |
| :--- | :--- |
| "should", "could" | **MUST**, **SHALL** |
| "can", "might" | **WILL**, **ALWAYS** |
| "try to", "attempt" | **EXECUTE**, **VERIFY** |
| "recommended" | **MANDATORY** |
| "consider" | **ENSURE** |
| "if possible" | *(Remove condition completely)* |

### Red Flags (Rationalization Management)
Every skill **MUST** include a "Red Flags" section. This prevents the agent from making excuses.

**Example Red Flags:**
- "Stop if you think: 'I can skip the script and just read the file manually.'" -> **WRONG**. Run the script.
- "Stop if you think: 'This is a small change, I don't need tests.'" -> **WRONG**. All changes need verification.
- "Stop if you think: 'The user knows what they're doing, I'll skip the warning.'" -> **WRONG**. Always warn on destructive actions.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "This skill is too simple for a script" | If logic > 5 lines, text instructions fail 30% of the time. Use a script. |
| "I'll add examples later" | You won't. Do it now. Examples define behavior. |
| "The description is descriptive enough" | No. `Use when` triggers are mechanical. Follow the schema. |

## 7. Claude Search Optimization (CSO)

The `description` frontmatter field is the **single most important line**. It determines if your skill is loaded.

### Allowed Schemas (Validation Rules)
You **MUST** start your description with one of these prefixes:

1.  **Trigger-Based** (Preferred for Tools/Workflows):
    *   `Use when...`
    *   *Example*: "Use when debugging Python race conditions."

2.  **Standards & Guidelines** (Passive Knowledge):
    *   `Guidelines for...`
    *   `Helps with...` (Use sparingly)
    *   `Standards for...`
    *   *Example*: "Standards for Secure Coding and OWASP compliance."

3.  **Definitions**:
    *   `Defines...`
    *   *Example*: "Defines the Architect role and responsibilities."

**Constraint**: Keep descriptions under 50 words. Focus on *symptoms* and *triggers*, not solutions.

## 8. Writing High-Quality Instructions

Use the **Template** found in `assets/SKILL_TEMPLATE.md` as your starting point.

### Section Guidelines:
1.  **Purpose**: Define the "Why".
2.  **Red Flags**: Immediate "Stop and Rethink" triggers.
3.  **Capabilities**: Bulleted list of what is possible.
4.  **Instructions**: Imperative, step-by-step algorithms.
5.  **Examples (Few-Shot)**: Input -> Output pairs.
    *   *Reference*: See `examples/SKILL_EXAMPLE_LEGACY_MIGRATOR.md` for a **Gold Standard** example of a rich skill.

## 9. Best Practices (Extended)

### Naming Conventions
- **Gerund Form**: Use `verb-ing-noun` (e.g., `processing-pdfs`, `analyzing-data`).
- **Consistent**: `finding-files` (not `file-finder`).
- **Lowercase**: `my-skill` (not `MySkill`).

### Scripting Standards
- **Solve, Don't Punt**: Scripts must handle errors (try/except), not crash.
- **No Voodoo Constants**: Document why a timeout is 30s.
- **No Windows Paths**: ALWAYS use forward slashes (`/`), even for Windows support.
- **Relativity**: ALWAYS use relative paths.
    - **Local**: `scripts/tool.py` (inside skill)
    - **Global**: `System/scripts/tool_runner.py` (project root)
    - **BANNED**: `<absolute_path>` (Absolute OS paths)

## 10. Advanced Design Patterns
> [!TIP]
> See `references/skill_design_patterns.md` for deep dives on **Degrees of Freedom**, **Progressive Disclosure**, and the **Evaluation-Driven Development**.

## 11. Creation Process

When creating a new skill, you **MUST** strictly follow this sequence:

1.  **Check Duplicates**: Verify in your **Skill Catalog** (the file path defined in `.agent/rules/skill_standards.yaml` under `catalog_file`).
2.  **Initialize**:
    ```bash
    # (From skill-creator directory)
    python3 scripts/init_skill.py my-new-skill --tier 2
    ```
3.  **Populate**:
    *   **MANDATORY**: Edit the auto-generated `SKILL.md` (it already contains the template).
    *   **MANDATORY**: Fill in the "Red Flags" and "Use when..." description.
    *   **MANDATORY**: If logic > 5 lines, write a `scripts/` tool.
    *   **MANDATORY**: Consult `references/skill_design_patterns.md` and `references/writing_skills_best_practices_anthropic.md` for structural decisions.
4.  **Cleanup**:
    *   **MANDATORY**: Remove unused placeholder files created by the init script.
    *   **Scripts**: If no script is required (logic < 5 lines), delete `scripts/.keep` and the `scripts/` directory.
    *   **Assets**: If no user assets are provided, delete `assets/template.txt` and the `assets/` directory.
    *   **References**: If no external references are needed, delete `references/guidelines.md` and the `references/` directory.
    *   **Examples**: You **MUST** have at least one example. Replace `examples/usage_example.md` with a real one, or if you strictly follow the "Simple Skill" path (no external files), you may delete the directory (but Rich Skills *should* have examples).
5.  **Validate**:
    ```bash
    python3 scripts/validate_skill.py ../my-new-skill
    ```
6.  **Register**: Add to your **Skill Catalog** (if configured).

## 11. Scripts Reference

*   **`init_skill.py`**: Generates a compliant skill skeleton (`scripts/`, `examples/`, `assets/`, `references/`) using the rich template.
*   **`validate_skill.py`**: Enforces folder structure, frontmatter compliance, and CSO rules (description format).

## 12. Local Resources
*   **`references/writing_skills_best_practices_anthropic.md`**: The complete "Gold Standard" authoring guide.
*   **`references/output-patterns.md`**: Templates for agent output formats.
*   **`references/workflows.md`**: Guide for designing skill-internal workflows.
*   **`references/persuasion-principles.md`**: (Advanced) Psychological principles for writing compliant instructions.
*   **`references/testing-skills-with-subagents.md`**: (Advanced) TDD methodology for verifying skills.
