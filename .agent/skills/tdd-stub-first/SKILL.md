---
name: tdd-stub-first
description: Test-Driven Development with Stub-First approach.
version: 1.0
---
# TDD & Stub-First Strategy

## 1. Stubbing Phase
1. **Create Structure:** Files, classes, methods.
2. **Implement Stubs:** Use `NotImplementedError`, `return None`, or hardcoded values.
3. **Docstrings:** Add detailed docstrings describing future logic.
4. **E2E Test (Stub):** Write an E2E test that asserts the hardcoded behavior.
   - *Example:* asserting `discount == 100.0` (stubbed value).

## 2. Implementation Phase
1. **Verify Stubs:** Ensure E2E test passes on stubs.
2. **Replace Stubs:** Implement real logic.
3. **Unit Tests:** Add unit tests for specific methods and edge cases.
4. **Update E2E:** Update E2E test to assert real behavior.
   - *Example:* asserting `discount == 150.0` (calculated value).

## 3. Testing Rules
- **No Mocking LLMs:** Use recorded responses or separate integration environments.
- **Regression:** Always run full regression suite.
