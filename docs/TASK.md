### 0. Meta Information
- **Task ID:** 031
- **Slug:** verify-docs-v3.2.2
- **Status:** Completed

# TASK: Verify and Update Documentation for v3.2.2

## Goal
Verify that all project documentation (`README.md`, `README.ru.md`, `docs/`) accurately reflects the changes introduced in v3.2.2 (System Integrity & Archiving Protocols) and previous recent versions if missed.

## Requirements
1.  **Analyze Documentation Coverage:**
    -   Check `README.md` & `README.ru.md` for mentions of Archiving Protocols or updated Agent capabilities.
    -   Check `docs/SKILLS.md` for updates to `skill-artifact-management`.
    -   Check `docs/WORKFLOWS.md` for correct referencing of updated workflows.
2.  **Verify Consistency:**
    -   Ensure "Task" vs "TZ" terminology is consistent (should have been done in v3.1.0, but worth a double-check).
    -   Ensure symlink instructions for Cursor are clear.
3.  **Update Missing Information:**
    -   If any documentation is outdated regarding the new strict archiving rules, update it.

## Acceptance Criteria
-   [x] `README.md` and `README.ru.md` are up to date.
-   [x] `docs/SKILLS.md` accurately describes `skill-artifact-management` updates.
-   [x] `docs/WORKFLOWS.md` is consistent with current agent behavior.
