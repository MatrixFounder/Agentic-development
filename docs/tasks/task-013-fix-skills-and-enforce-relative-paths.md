# Task: SKILL Audit & Artifact Standards

### 0. Meta Information
- **Task ID:** 013
- **Slug:** fix-skills-and-enforce-relative-paths

## 1. General Description
The user reported a YAML syntax error in `core-principles`, which has been fixed. Now, the scope is expanded to:
1.  **Audit all SKILL files** for similar YAML issues.
2.  **Standardize Artifact Paths:** Enforce the use of relative paths (instead of absolute) in `docs/PLAN.md` and other artifacts for portability.
3.  **Systemic Enforcement:** Update System Prompts and Skills (Documentation Standards) to require relative paths.
4.  **Localization Sync Rule:** Create a formal rule to ensure `System/Agents` and `Translations` are kept in sync.

## 2. List of Use Cases

### UC-01: Fix YAML Syntax (Completed)
- Fixed `core-principles`.

### UC-02: Enforce Analyst Protocol (Completed)
- Hardened `02_analyst_prompt.md`.

### UC-03: Audit and Fix All Skills (Completed)
- Audited and fixed YAML in 5 files.

### UC-04: Refactor PLAN.md to Relative Paths (Completed)
- Refactored `docs/PLAN.md`.

### UC-05: Enforce Relative Path Standard (Completed)
- Updated `skill-documentation-standards` and `06_agent_planner.md`.

### UC-06: Create Localization Sync Rule
**Actors:** System
**Main Scenario:**
1.  Create `.agent/rules/localization-sync.md` (or similar).
2.  Define rule: "If `System/Agents` changes -> Update `Translations/RU/Agents`".
3.  (Optional) Add this rule to `docs/rules.md` if it exists, or just ensure the agent reads it.
**Note:** The user specified creating a rule in `.agent/rules`.

## 3. Impact Analysis
- **Consistency:** Prevents English and Russian prompts from drifting apart in logic/rules.

## 4. Verification Plan
- **Rule Existence:** Verify file `.agent/rules/localization-sync.md` exists.
- **Content:** Verify it explicitly mentions the sync requirement.

## 5. Open Questions
- None.
