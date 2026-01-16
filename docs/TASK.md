# Task: Correct Cursor Installation Instructions

### 0. Meta Information
- **Task ID:** 014-B
- **Slug:** fix-cursor-instructions
- **Status:** Active

## 1. General Description
The user pointed out that Cursor does not automatically index `.agent/skills`. We need to explicitly instruct users to trigger this indexing, likely via a symbolic link from `.agent/skills` to `.cursor/skills`. We also need to correct `.cursorrules` to reflect this reality.

## 2. List of Use Cases

### UC-01: Update README Installation Instructions
- **Actor:** System
- **Action:** Update `README.md` and `README.ru.md`.
- **Change:**
    - Replace "Automatically indexes" with "Requires Symlink".
    - Provide exact command: `ln -s ../.agent/skills .cursor/skills` (or similar relative path).

### UC-02: Corrections in .cursorrules
- **Actor:** System
- **Action:** Update `.cursorrules`.
- **Change:**
    - Clarify that Skills are physically in `.agent/skills` but should be linked for Cursor visibility.
    - Ensure paths are robust.

## 3. Impact Analysis
- **User UX:** Users must run one Setup command (`ln -s`) for the IDE to work fully. This is better than maintaining duplicate files.

## 4. Verification Plan
- **Docs:** Read `README.md` to ensure clarity.
