# Task 008.1: Update WORKFLOWS.md

## Use Case Connection
- UC-01: View available workflows
- UC-02: Add new workflow

## Task Goal
Update `docs/WORKFLOWS.md` to include a comprehensive, beautiful table of all workflow variants and usage examples.

## Changes Description

### Changes in Existing Files

#### File: `docs/WORKFLOWS.md`
- **Structure Refactoring:**
    - Replace the simple list/table with a comprehensive "Master Registry" table.
    - Columns to include: `Variant`, `Workflow File`, `Description`, `Key Features`, `Command Example`.
- **Content Updates:**
    - Add detailed descriptions for "Standard", "VDD", and "Nested" workflows.
    - Ensure `security-audit` is included.

## Test Cases

### Manual Verification
1. **TC-MAN-01:** Render Markdown
   - Open `docs/WORKFLOWS.md` in a Markdown viewer.
   - Verify table formatting is correct.
   - Verify links to workflow files are valid.

## Acceptance Criteria
- [ ] Table covers all workflows found in `.agent/workflows`.
- [ ] Command examples are copy-pasteable.
- [ ] Descriptions are clear and helpful.
