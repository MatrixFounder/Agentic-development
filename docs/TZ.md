## 0. Meta Information
- **Task ID:** 008
- **Slug:** workflow-manual

## 1. General Description
The goal is to improve `docs/WORKFLOWS.md` to make it a comprehensive manual for users. This involves creating a detailed, visually appealing table of all available workflow variants, including descriptions and usage examples. The document should serve as a single point of truth for automation workflows.

## 2. List of Use Cases

### UC-01: View available workflows
**Actors:** User
**Preconditions:** User opens `docs/WORKFLOWS.md`
**Main Scenario:**
1. User sees a clear summary table of capabilities.
2. User can quickly find the right workflow for their task (Standard vs VDD vs Nested).
3. User sees copy-pasteable examples for running workflows.
**Postconditions:** User understands how to start work.

### UC-02: Add new workflow
**Actors:** Developer/Architect
**Preconditions:** New workflow file created.
**Main Scenario:**
1. Developer adds new entry to the Registry table.
2. Developer follows the defined schema.
**Postconditions:** `docs/WORKFLOWS.md` remains up to date.

## 3. Non-functional Requirements
- **Readability:** High, with clear formatting and examples.
- **Completeness:** Must cover all existing workflows found in `.agent/workflows`.
- **Maintainability:** Easy to update when new workflows are added.

## 4. Constraints and Assumptions
- Modifications are limited to `docs/WORKFLOWS.md`.
- No new workflows are created, only documentation is improved.

## 5. Open Questions
- None.
