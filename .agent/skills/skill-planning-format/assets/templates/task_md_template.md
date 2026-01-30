# Task X.Y: [Task Name]

## Use Case Connection
- UC-XX: [Use Case Name]
- UC-YY: [Use Case Name]

## Task Goal
[Brief description of what must be achieved]

## Changes Description

### New Files
- `path/to/new_file.py` — [purpose of file]
- `path/to/.AGENTS.md` — [description of module] (MANDATORY for new directories)

### Changes in Existing Files

#### File: `path/to/existing_file.py`

**Class `ClassName`:**
- Add method `method_name(param1: Type1, param2: Type2) -> ReturnType`
  - Parameters:
    - `param1` — [description]
    - `param2` — [description]
  - Returns: [description]
  - Logic: [brief description of method logic]

**Function `function_name`:**
- Add parameter `new_param: Type` — [description]
- Change logic: [description of changes]

### Component Integration
[Description of how new components integrate with existing ones]

## Test Cases

### End-to-end Tests
1. **TC-E2E-01:** [Description of E2E test]
   - Input Data: [...]
   - Expected Result: [...]
   - Note: [At stub stage, hardcoded result is expected]

### Unit Tests
1. **TC-UNIT-01:** [Description of test]
   - Tested Function/Method: [...]
   - Input Data: [...]
   - Expected Result: [...]

### Regression Tests
- Run all existing tests from `tests/` directory
- Ensure functionality is not broken: [list critical scenarios]

## Acceptance Criteria
- [ ] All new classes/methods added
- [ ] All tests pass (including regression)
- [ ] Documentation updated
- [ ] Code complies with project standards

## Notes
[Additional information, implementation details]
