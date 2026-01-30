# Skill Writing Manual

**Tools for Agentic Development**

This manual describes how to use the **Skill Creator** and **Skill Enhancer** tools to build authoritative, high-quality agent skills. These tools are designed to be project-agnostic and configurable.

---

## 1. Overview

The Meta-Skill system consists of two primary components:

1.  **Skill Creator**: Bootstraps new skills with a standardized structure (`scripts/`, `examples/`, `resources/`) and validates them against compliance rules.
    *   *Scripts*: `init_skill.py`, `validate_skill.py`
2.  **Skill Enhancer**: Analyzes existing skills for "gaps" (weak language, missing sections, poor examples) and guides refactoring.
    *   *Scripts*: `analyze_gaps.py`

---

## 2. Configuration

The tools are driven by a configuration file. This allows you to define your own project policies (e.g., specific Tiers, banned words).

### Locations
The scripts look for configuration in the following order:
1.  **Project Overlay**: `.agent/rules/skill_standards.yaml` (Recommended)
2.  **Bundled Defaults**: `scripts/skill_standards_default.yaml` (Fallback)

### Configuration Format
The configuration file uses a JSON-compatible subset of YAML.

```yaml
# .agent/rules/skill_standards.yaml

project_config:
  # Optional: Path to a master documentation file to list skills
  catalog_file: "docs/SKILLS_CATALOG.md"
  skills_root: "skills" # Default output dir

taxonomy:
  # Define your own Tier system
  tiers:
    - value: 0
      name: "Core"
      description: "Always loaded."
    - value: 1
      name: "Standard"
      description: "Loaded on demand."

validation:
  allowed_cso_prefixes: 
    - "Use when"
    - "Guidelines for"
  
  quality_checks:
    max_inline_lines: 12
    max_description_words: 50
    banned_words:
      - "should"
      - "can"
```

---

## 3. Usage Guide

### Creating a New Skill
Use `init_skill.py` to generate a compliant skeleton.

```bash
# Basic Usage
python3 .agent/skills/skill-creator/scripts/init_skill.py my-new-skill

# Specific Tier
python3 .agent/skills/skill-creator/scripts/init_skill.py my-new-skill --tier 1
```

**What it does:**
- Creates directories: `scripts/`, `examples/`, `resources/`.
- Generates `SKILL.md` from the template.
- Checks if you need to update your Catalog File.

### Validating a Skill
Use `validate_skill.py` to check structural compliance (Metadata, Folders).

```bash
python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/my-new-skill
```

**Checks:**
- `SKILL.md` exists.
- Frontmatter (YAML) is valid and matches config (Tiers).
- No prohibited files (e.g., README.md).
- Description starts with allowed prefixes.

### Enhancing a Skill
Use `analyze_gaps.py` to check for quality issues and "Antigravity" compliance.

```bash
python3 .agent/skills/skill-enhancer/scripts/analyze_gaps.py .agent/skills/my-new-skill
```

**Checks:**
- **Weak Language**: Detects "passive" words like "should", "can".
- **Structure**: Checks for required sections ("Red Flags").
- **Token Efficiency**: Warns if inline code blocks > 12 lines.
- **Richness**: Warns if `examples/` folder is empty.

---

## 4. Best Practices (The "Gold Standard")

To write effective skills that work across different LLMs (Anthropic, OpenAI, etc.):

1.  **Script-First**: If logic requires > 5 lines of text explanation, write a Python script instead. Agents follow code better than text.
2.  **Imperative Language**: Use "MUST", "EXECUTE", "VERIFY". Avoid "should", "try".
3.  **Examples**: Provide real file examples in `examples/`. Do not force the agent to hallucinate content.
4.  **Zero-Dependency**: Keep your skill scripts standard (Vanilla Python) so they run everywhere without setup.
