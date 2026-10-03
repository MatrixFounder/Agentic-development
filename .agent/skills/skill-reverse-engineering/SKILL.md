---
name: skill-reverse-engineering
description: "Regenerate architecture documentation from codebase analysis."
tier: 2
version: 1.5
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

**Figures.** Write the text of a section first. Then draw its figure from that text with
`mermaid-authoring-guidelines`; load the skill before the first figure. Each element of the figure
has a supporting line in that text. A relation found only in the code goes into the text first, or
stays out of the figure. A figure in a section this update leaves unchanged stays as it is.

**Why.** The skill's fidelity step (Step 6) accepts a line of the document as support. A line of
code is not one.

### 2. KNOWN_ISSUES.md Updates
Identify:
- `TODO`/`HACK` comments indicating tech debt.
- Discrepancies between implementation and docs.

**Filing format (thin index).** `docs/KNOWN_ISSUES.md` is a hand-maintained **thin index**, not a
flat checklist — do **NOT** append `- [ ]` lines to it. The authoritative format contract lives in the
**`known-issues-format`** skill (`artifact-management`, TIER 0, delegates to it) — follow it:
1. If `docs/KNOWN_ISSUES.md` does not exist yet, materialize it from
   `known-issues-format`'s `assets/templates/known_issues_md_template.md` first (create-if-absent).
2. File each finding as its own `docs/issues/<slug>.md` (frontmatter + H1 + body) **plus** one index
   line under the matching `## <category>` heading — edit both **in lockstep**.
3. If a finding needs a category/prefix the project's ledger doesn't have yet, add a new
   **prefix → category** row to that ledger's *Rules / Conventions* table before filing.

(The "Append new findings, do not delete existing rationale" protection in **Human Knowledge
Preservation** below still applies to the per-issue bodies.)

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
- **With `mermaid-authoring-guidelines`**: every figure of the update; see **Figures** above.
