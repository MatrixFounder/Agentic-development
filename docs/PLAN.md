# Development Plan: Workflow Refactoring

## Goal
Streamline the Workflow system, ensuring consistency, removing legacy terms, and clearly defining the purpose of each workflow.

## User Review Required
> [!IMPORTANT]
> This plan proposes renaming and consolidating some workflows.
> - **Question**: Should we merge `01-start-feature` and `base-stub-first`?
> - **Recommendation**: Keep `01-05` as "Atomic Actions" and `base-stub-first` as a "Composite Workflow".

## Proposed Changes

### 1. Workflow Definitions Refactor (.agent/workflows/)
- **Standardize Naming**: ensure all use `TASK` terminology.
- **Clarify `05-run-full-task.md`**: Ensure it acts as the primary "Loop" workflow.
- **Audit `base-stub-first.md`**: Ensure it calls the correct atomic workflows.

### 2. Documentation Update (System/Docs/WORKFLOWS.md)
- **Rewrite**: Create a clear hierarchy of workflows.
  - **Category A: Atomic Actions** (01-05) - Run *one* phase.
  - **Category B: Automation Loops** (05, base-*, vdd-*) - Run *multiple* phases.
- **Add "Full Auto" Guide**: Explicitly explain how to use `05-run-full-task`.

## Verification Plan

### Manual Verification
1. **Dry Run**: Execute `05-run-full-task` on a dummy task.
2. **Link Check**: Verify all links in `System/Docs/WORKFLOWS.md` correspond to real files.
3. **Term Check**: `grep` for "tz" again to be 100% sure.
