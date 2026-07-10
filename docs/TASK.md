# Technical Specification: Extract KNOWN_ISSUES format into a dedicated `known-issues-format` skill

### 0. Meta Information
- **Task ID:** 087
- **Slug:** `known-issues-format-skill`
- **Mode:** Framework Upgrade (skill creation + refactor; **no code, no installer change**)
- **Type:** Architectural consistency. Follow-up to Task 086.
- **Workflow:** `/framework-upgrade` (verificator Modes A + B). **SKILL CREATION GATE:** new skill via `init_skill.py`.

### 1. Problem Description
Task 086 placed `KNOWN_ISSUES.template.md` **and** the full format contract inside the TIER-0
`artifact-management` skill. That violates the framework's established artifact pattern:

- `artifact-management` is a **management hub** — it owns lifecycle/ownership/dual-state and **delegates
  format**: archiving → `skill-archive-task`; ARCHITECTURE format/split → `architecture-format-core`
  (*"defined in architecture-format-core, not here"*).
- **Reusable templates live in per-artifact format skills**, never in the hub:
  `skill-planning-format/assets/templates/{task,plan}_md_template.md`,
  `documentation-standards/assets/templates/agents_md_template.md`.
- Until Task 086, `artifact-management` held **zero** assets. `KNOWN_ISSUES.template.md` was the first —
  an anomaly.

KNOWN_ISSUES is a **living, non-planning artifact** — the direct analog of `ARCHITECTURE.md`, which has its
**own** format skill (`architecture-format-core`) rather than being folded into planning-format. So it
warrants its own format skill.

### 2. Requirements (RTM)

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | Create a dedicated **`known-issues-format`** skill (tier 2) via `init_skill.py` (gate-compliant). | Skill dir exists; `validate_skills` passes (44/44). |
| R2 | The new skill **owns the format contract** (frontmatter schema, prefix→category table, status/severity vocab, index-line format, "Adding a new issue" recipe) + the **template** at `assets/templates/known_issues_md_template.md`. | Contract + template present; template schema == live `docs/KNOWN_ISSUES.md`. |
| R3 | **Move** the template out of `artifact-management/assets/`; remove the now-empty dir. | `artifact-management/assets/` gone; no orphan. |
| R4 | **Slim `artifact-management`** to lifecycle only: list KNOWN_ISSUES.md as a living Global Artifact + create-if-absent + **delegate format** to `known-issues-format` (mirrors the ARCHITECTURE delegation). | Detailed format contract removed from the hub; one-line delegation added. |
| R5 | Repoint `skill-reverse-engineering §2` to the format authority (`known-issues-format`). | §2 references `known-issues-format`. |
| R6 | No `core-principles`/`skill-safe-commands` change; docs + registry synced. | Meta-audit; SKILLS.md + CHANGELOG + README updated. |

### 3. Non-Goals
- No change to the committed `docs/KNOWN_ISSUES.md` ledger or the per-issue files.
- No installer/vendors.yaml/Python/test change (the template still auto-ships via the `.agent/skills` link).
- Not folding KNOWN_ISSUES into planning-format/documentation-standards (a living non-planning artifact
  gets its own format skill, per the ARCHITECTURE precedent).

### 4. Acceptance Criteria
- `known-issues-format` is the single source of the KNOWN_ISSUES format + template; `artifact-management`
  and `skill-reverse-engineering` both **delegate** to it (no duplicated contract).
- Fresh-project trace still holds (create-if-absent references the new skill's template).
- `validate_skills` 44/44; template schema consistent; no orphan assets.
