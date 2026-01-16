# Task 016: Workflow System Refactoring

## Rationale
The user identifies confusion in the current workflow system (`.agent/workflows/` and `docs/WORKFLOWS.md`). There are legacy naming conventions, overlapping functionalities (e.g., numbered workflows vs named ones), and a need for clear documentation on autonomous execution.

## Goals
1. **Audit & cleanup**: Verify correctness of all workflows (no legacy 'tz' terms).
2. **Consolidate**: detailed clear purpose for each workflow.
3. **Clarify Automation**: Explain `05-run-full-task` and ensure it's documented.
4. **Update Documentation**: Rewrite `docs/WORKFLOWS.md` to be the definitive guide.

## Scope

### 1. Analysis (Done)
- Review `docs/WORKFLOWS.md`.
- Review `.agent/workflows/` content.

### 2. Refactoring Proposals
- **Naming Convention**: Decide between `01-start...` vs `base-stub-first`.
  - *Decision:* Numbered workflows (`01`, `02`, `03`) are good for sequential steps. Named workflows (`base-stub-first`) are good for "Modes".
  - *Action:* Keep `01-05` as the "Standard Toolchain". Keep `base-*` or `vdd-*` as "Meta-Workflows" that might call the standard ones.
- **Clarification**:
  - `05-run-full-task.md`: This is the "Loop" workflow.

### 3. Implementation
- Update `docs/WORKFLOWS.md` with a clear table.
- Fix any remaining legacy terms in workflows.
- Ensure `05-run-full-task` is correctly referenced.

## Acceptance Criteria
- [ ] `docs/WORKFLOWS.md` accurately reflects all files in `.agent/workflows/`.
- [ ] User understands distinction between "Atomic Actions" (01-04) and "Loops" (05).
