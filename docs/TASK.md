# Technical Specification: Refactoring TZ.md to TASK.md

## 0. Meta Information
- **Task ID:** 012
- **Slug:** tz-to-task-refactor

## 1. General Description
The objective is to improve the consistency of the framework's naming conventions by transitioning from the Russian acronym "TZ" (Техническое Задание) to the English term "TASK" (Task/Requirements/Specification). This aligns with open-source standards and simplifies onboarding for international contributors.

The primary deliverables are renaming `docs/TZ.md` to `docs/TASK.md`, `03_tz_reviewer_prompt.md` to `03_task_reviewer_prompt.md`, and performing a global replacement of "TZ" with "TASK" across the codebase, documentation, and workflows, while ensuring backward compatibility.

## 2. List of Use Cases

### UC-01: Renaming Artifacts
**Actors:** Agent (Developer), Maintainer
**Preconditions:** Repository contains `docs/TZ.md` and related prompts.
**Main Scenario:**
1. System renames `docs/TZ.md` to `docs/TASK.md`.
2. System renames `.agent/roles/03_tz_reviewer_prompt.md` to `.agent/roles/03_task_reviewer_prompt.md`.
3. System updates the content of `03_task_reviewer_prompt.md` to replace mentions of "TZ" with "TASK".

### UC-02: Global Codebase Refactoring
**Actors:** Agent (Developer)
**Preconditions:** Artifacts are renamed.
**Main Scenario:**
1. System performs a search for "TZ.md" and replaces it with "TASK.md" (case-sensitive) in all files (except exclusions).
2. System performs a search for "tz" and replaces it with "task" in relevant contexts (filenames, variables, descriptions).
3. **Exclusions:**
    - `CHANGELOG.md` (historical data).
    - `docs/tasks/` (archived tasks).
4. Critical updates applied to:
    - `.agent/skills/` (especially `artifact-management`, `core-principles`).
    - `.agent/roles/` (descriptions, active skills).
    - `docs/WORKFLOWS.md` and workflow files.
    - `README.md` and documentation.

### UC-03: Archive Management Update
**Actors:** Agent (Analyst/Manager)
**Preconditions:** Task is completed.
**Main Scenario:**
1. Agent invokes `skill-artifact-management`.
2. System archives `docs/TASK.md` to `docs/tasks/archived_task_{timestamp}_{slug}.md` (or standard format).
3. System ensures no legacy `TZ.md` remains unless it's a fallback.

### UC-04: Backward Compatibility Check
**Actors:** Orchestrator, Agent
**Preconditions:** Core refactoring complete.
**Main Scenario:**
1. Orchestrator attempts to find `docs/TASK.md`.
2. If found, uses it as the source of truth.
3. If not found, Orchestrator checks for `docs/TZ.md` (Legacy Fallback).
4. System logs a warning if legacy file is used (optional).

## 3. Requirements & Acceptance Criteria

### 3.1 Content Requirements
- **Consistency:** "TZ" should not appear in active user-facing docs or prompts (except as historical reference).
- **Naming:** `docs/TASK.md` is the new standard.

### 3.2 Technical Requirements
- **Renamed Files:**
    - `docs/TZ.md` -> `docs/TASK.md`
    - `System/Agents/03_tz_reviewer_prompt.md` -> `System/Agents/03_task_reviewer_prompt.md` (Note: The user request mentioned `.agent/roles/` but the system path seems to be `System/Agents/` or `.agent/roles/` depending on the structure. Will check and update both if needed).
    - **Note:** Based on file exploration, prompts are in `System/Agents/`.
- **Global Search & Replace:**
    - `TZ.md` -> `TASK.md`
    - `tz` -> `task` (smart case, structural).

### 3.3 Acceptance Criteria
- ✅ `docs/TASK.md` exists and contains current task info.
- ✅ `System/Agents/03_task_reviewer_prompt.md` exists and is valid.
- ✅ `docs/TZ.md` does not exist (unless explicitly kept for test, but goal is renaming).
- ✅ `docs/WORKFLOWS.md` refers to `TASK.md`.
- ✅ `README.md` refers to `TASK.md` and `Task Reviewer`.
- ✅ Old projects with `TZ.md` still work (conceptual check).

## 4. Constraints and Assumptions
- **Path Structure:** Assumed `System/Agents/` is the location for prompts based on previous file reads.
- **Safety:** Backup of critical files before bulk rename.

## 5. Open Questions
- None.
