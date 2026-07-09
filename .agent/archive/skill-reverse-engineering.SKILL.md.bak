---
name: skill-reverse-engineering
description: "Regenerate architecture documentation from codebase analysis."
tier: 2
version: 1.1
---
# Reverse Engineering Skill

## Purpose
Recover the mental model of a project from its codebase when documentation is outdated or missing.

## When to Use
- Documentation-code mismatch detected
- New team member onboarding
- Post-"quick fix" cleanup

## Strategy: Automated Scan + Iterative Analysis

### Phase 1: Automated Directory Scan
**Tool:** `scripts/scan_structure.py`

**Usage:**
```bash
python3 .agent/skills/skill-reverse-engineering/scripts/scan_structure.py . --depth 2
```

**Goal:**
- Get high-level overview of project structure.
- Identify dominant languages and components.
- Avoid context overflow by NOT reading all files.

### Phase 2: Local Analysis (Per-Directory)
For each key component identified in Phase 1:
1. List files.
2. Sample 2-3 representative files (read content).
3. Generate **Local Summary**:
   - Purpose
   - Key Classes
   - Dependencies

### Phase 3: Global Synthesis
Combine local summaries to update `docs/ARCHITECTURE.md`:
- Update **Directory Structure**
- Update **Component Map**
- Identify **Architecture Drift** (Code != Docs)

## Output Artifacts

### 1. ARCHITECTURE.md Update
Generate diffs for:
- Directory Structure
- Component Map
- Data Flow

### 2. KNOWN_ISSUES.md Updates
Identify:
- `TODO`/`HACK` comments indicating tech debt.
- Discrepancies between implementation and docs.

## Human Knowledge Preservation

> [!CAUTION]
> **Never overwrite architectural rationale written by humans.**

**Protected patterns:**
- `<!-- HUMAN KNOWLEDGE -->`
- `> **Design Decision:**`

**Strategy:** Append new findings, do not delete existing rationale.

## Integration
- **With `skill-update-memory`**: After analysis, run bootstrap mode to create missing `.AGENTS.md` files where needed.
- **Workflow `04-update-docs`**: Run this skill if docs drift is detected.
