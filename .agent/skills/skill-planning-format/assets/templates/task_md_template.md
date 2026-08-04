<!--
  REGISTER. Write in whichever language the project uses; nothing in this pipeline changes that
  choice. In that language, apply the authoring contract BEFORE the first sentence:
  `.agent/skills/artifact-formalizer/references/authoring-contract.md` — six per-sentence tests and
  the licensed statement forms. It is the single source for them, so this template does not restate
  the rules. Audit with `artifact-formalizer/scripts/scan_register.py`.
-->

# Task X.Y: [Task Name]

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
  Keep them; translate the headings freely. Never invent an unregistered one.
-->

## Use Case Connection
- UC-XX: [Use Case Name]
- UC-YY: [Use Case Name]

<!-- contract:goal -->

## Task Goal
[Brief description of what must be achieved]

<!-- contract:changes -->

## Changes Description

### New Files
- `path/to/new_file.py` — [purpose of file]
- `path/to/.AGENTS.md` — [description of module] (for new source directories under memory tracking policy)

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

<!-- contract:tests -->

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

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] All new classes/methods added
- [ ] All tests pass (including regression)
- [ ] Documentation updated
- [ ] Code complies with project standards

## Notes
[Additional information, implementation details]
