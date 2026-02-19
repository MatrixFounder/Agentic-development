# Skill Creator Default Parameters Map

This file is the quick-reference for all default parameters used by `skill-creator` scripts.

## 1. Configuration Resolution Order

Parameters are resolved in this order:

1. Bundled defaults: `scripts/skill_standards_default.yaml`
2. Project overlay: `.agent/rules/skill_standards.yaml`
3. Script-level runtime fallbacks (hardcoded in Python scripts)

## 2. Bundled Defaults (`scripts/skill_standards_default.yaml`)

```yaml
project_config:
  catalog_file: null
  skills_root: "."

taxonomy:
  tiers:
    - value: 0
      name: "Bootstrap"
    - value: 1
      name: "Phase-Triggered"
    - value: 2
      name: "Extended"

validation:
  allowed_cso_prefixes:
    - "Use when"
    - "Guidelines for"
    - "Standards for"
  required_sections:
    - "Red Flags"
    - "Rationalization Table"
  prohibited_files: []
  quality_checks:
    max_inline_lines: 12
    max_description_words: 50
    banned_words:
      - "should"
      - "can"
```

## 3. Runtime Fallbacks (When Keys Are Missing)

### `scripts/init_skill.py`
- `--path` default: `project_config.skills_root` (fallback: `.agent/skills`)
- `--tier` choices: `taxonomy.tiers[*].value` (fallback: `0, 1, 2`)
- `--tier` default value: `2`

### `scripts/validate_skill.py`
- `validation.enforce_cso_prefix` fallback: `true`
- `validation.allowed_cso_prefixes` fallback (only if enforcement is enabled and list is empty): `["Use when"]`
- `taxonomy.tiers` fallback for validation: `[0, 1, 2]`
- `validation.quality_checks.max_inline_lines` fallback: `12`
- `validation.quality_checks.max_description_words` fallback: `50`

## 4. Project-Level Extensions (Overlay-Dependent)

Project overlays may add or override fields. This file must not be treated as repository-specific policy.

Typical override patterns:
- `validation.enforce_cso_prefix` (`true`/`false`)
- `validation.inline_exempt_skills` (legacy exceptions)
- additional entries in `validation.allowed_cso_prefixes`
- extended `taxonomy.tiers` (for example, custom Tier `3+`)
- `validation.prohibited_files` adjustments

To determine active behavior in the current repository, inspect the merged config output instead of assuming values from examples.

## 5. How To Inspect Effective Config

From `skill-creator` directory:

```bash
python3 scripts/skill_utils.py
```

This prints merged effective configuration (defaults + project overlay).

## 6. Maintenance Rule

When a new config parameter is introduced in `skill-creator` scripts or standards, update this file in the same change.
