# Meta-Skills Independence Proposal

**Date**: 2026-01-30
**Status**: DRAFT (Rev 6)
**Context**: `skill-creator` and `skill-enhancer` currently contain hardcoded "Antigravity/Gemini" standards. To make these meta-skills portable (project-agnostic), we need to extract these policies into a configuration file and remove fragile dependencies.

---

## 1. Analysis Report: Current Project Specificities & Universality

### A. Compliance & Taxonomy (Tiers)
*   **Correction**: The project uses **4 tiers** (0, 1, 2, 3).
*   **Resolution**: The `taxonomy.tiers` config must support a flexible list.

### B. "Golden Standard" & Universality
*   **Self-Sufficiency Policy**: `SKILL.md` must be self-contained.
*   **Prohibited Files**: Banning `README.md` is an *Antigravity* opinion. It will be configurable but disabled by default.
*   **Catalog File**: `System/Docs/SKILLS.md` is unique to this project. Generic skills should **NOT** crash or error if this file is missing.

### C. Technical Constraints (Zero-Dependency)
*   **Constraint**: The scripts must run on any environment with Python 3 **without** `pip install` (no `PyYAML` or `requests`).
*   **Resolution**: We will use the **Zero-Dependency "Vanilla" Parser** (already implemented in `validate_skill.py`) to read the YAML config.
*   **Effect on Config**: The `skill_standards.yaml` must use a **Strict Subset of YAML** (Basic Key-Values, Lists, no complex Nesting/Anchors) to be parseable by our simple custom parser.

---

## 2. Implementation Proposal

We will separate the **Mechanism** (Python scripts) from the **Policy** (YAML configuration).

### Proposed Configuration File
**`.agent/rules/skill_standards.yaml`** (Project Overlay).
**`scripts/skill_standards_default.yaml`** (Bundled Default).

```yaml
# .agent/rules/skill_standards.yaml
# NOTE: Must be compatible with Simple "Vanilla Python" Parser.
# No advanced YAML features (anchors, complex mapping keys).

project_config:
  # Optional: Path to a documentation file listing all skills.
  # If defined, scripts will remind the user to update this file.
  catalog_file: "System/Docs/SKILLS.md" 

  skills_root: ".agent/skills" 

taxonomy:
  tiers:
    - value: 0
      name: "Bootstrap"
      description: "Critical system skills loaded at session start."
    - value: 1
      name: "Phase-Triggered"
      description: "Loaded automatically when entering specific phases."
    - value: 2
      name: "Extended"
      description: "Specialized skills loaded only when requested."
    - value: 3
      name: "High Assurance"
      description: "Strict, rigorous protocols for critical stability."

validation:
  allowed_cso_prefixes: 
    - "Use when"
    - "Guidelines for"
    - "Standards for"
    - "Defines"
  
  # Default is EMPTY []. Antigravity project will override this.
  prohibited_files:
    - "README.md"
    - "CHANGELOG.md"
    
  quality_checks:
    max_inline_lines: 12
    max_description_words: 50
    banned_words:
      - "should"
      - "can"
      - "try to"
```

---

## 3. Detailed Action Plan

### Phase 1: Policy Configuration (The "Rules")
1.  **Create Config**: Create `.agent/rules/skill_standards.yaml`.

### Phase 2: Refactoring `skill-creator` (The "Mechanism")
1.  **Modify `scripts/init_skill.py`**:
    *   **Resilience Strategy**: Load Bundled Default -> Merge Project Overlay.
    *   **YAML Parsing**: Use the **Vanilla Parser** (Zero-Dependency). Warn if the user's YAML is too complex for the parser.
    *   **Catalog Logic**: Optional check (Reminder only).
2.  **Modify `scripts/validate_skill.py`**:
    *   Validate `tier` against the configured list.

### Phase 3: Refactoring `skill-enhancer` (The "Mechanism")
1.  **Modify `scripts/analyze_gaps.py`**:
    *   Load config via Vanilla Parser.

### Phase 4: Documentation (User Request)
1.  **Create Manual**: Create `System/Docs/skill-writing.md` as a detailed manual for using `skill-creator` and `skill-enhancer`.
    *   This file will be the portable "User Guide" for specific vendors or teams adopting these meta-skills.

## 4. Resilience & Architecture Summary

| Component | Strategy |
| :--- | :--- |
| **Missing Config** | Fallback to bundled defaults. |
| **Parsing** | **Zero-Dependency Vanilla Parser**. No `pip install` required. |
| **Compatibility** | Fully project-agnostic. Works in any repo structure. |

## 5. Next Steps
1.  Approve this plan.
2.  Create `.agent/rules/skill_standards.yaml`.
3.  Begin refactoring `init_skill.py` (Phase 2).
4.  Write `System/Docs/skill-writing.md` (Phase 4).
