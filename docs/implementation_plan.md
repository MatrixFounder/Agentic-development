# Implementation Plan - Task 016: Workflow System Refactoring

## Goal
Clean up the workflow system to remove ambiguity, eliminate duplication (DRY), and clarify the distinction between "Atomic Tools" and "Automation Pipelines".

## User Review Required
> [!IMPORTANT]
> **Breaking Change**: Renaming `03-develop-task.md` to `03-develop-single-task.md` to avoid confusion with the loop.
> **Logic Change**: `base-stub-first.md` will now explicitly CALL `05-run-full-task` instead of describing the loop manually.

## Proposed Changes

### 1. Refactor Workflow Files
- **Rename**: `.agent/workflows/03-develop-task.md` -> `03-develop-single-task.md`.
- **Refactor**: `.agent/workflows/base-stub-first.md`:
  - Replace "Step 4: Development Loop" manual instructions with `Call /05-run-full-task`.
- **Update**: `.agent/workflows/05-run-full-task.md`:
  - Ensure it references `03-develop-single-task` for the actual work (Composition).
- **Cleanup**: Delete any unused/duplicate files if found (None found so far, just overlapping logic).

### 2. Update Documentation (`docs/WORKFLOWS.md`)
- **Structure**:
  - **Level 1: Pipelines** (Run these for features) -> `base-stub-first`, `full-robust`.
  - **Level 2: Atomic Actions** (Run these for specific steps) -> `01`, `02`, `03`, `04`.
  - **Level 3: Automation** (Run these to loop) -> `05`.
- **FAQ Section**: Add "Why did 01-04 not loop?" explanation.
- **Reference**: Update all links to renamed files.

## Verification Plan

### Automated Verification
- None possible (these are text instructions for Agents).

### Manual Verification
1. **Dependency Check**: `grep` for `03-develop-task` to ensure no broken links.
2. **Logic Check**: Read `base-stub-first.md` to ensure the flow is `Analysis` -> `Arch` -> `Plan` -> `Call 05`.
