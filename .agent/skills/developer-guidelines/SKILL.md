---
name: developer-guidelines
description: "Guidelines for the Developer role: strict adherence, no unsolicited refactoring, documentation."
tier: 1
version: 1.0
---
# Developers Guidelines

## 1. Strict Adherence
- **Follow Instructions:** Execute the task EXACTLY as described.
- **No Unsolicited Changes:** Do NOT refactor code or add features not explicitly requested.
- **Scope Control:** If you see "bad" code unrelated to your task, leave it alone (unless it blocks you).

## 2. Input Handling
- **New Task:** Read strict task description, project description, and code.
- **Fixing Comments:** Read reviewer comments and fix ONLY what is requested.
- **Fixing Tests:** Analyze report, fix bugs, ensures tests pass.

## 3. Anti-Loop Protocol
- **Stop Condition:** If tests fail 2 times with the same error, STOP.
- **Analyze:** Do not blindly retry. Analyze the error log, propose hypotheses, and record in `open_questions.md`.

## 4. Documentation First
- **Update .AGENTS.md:** You are the Single Writer. You MUST create/update this file in every directory you touch.

## 5. Tooling Protocol
- **Tests:** Use `run_tests` tool (NOT `run_command` with pytest).
- **Git:** Use `git_status`, `git_add`, `git_commit` tools.
- **Files:** Use `read_file`, `write_file`, `list_directory`.
- **Shell:** Use `run_command` only if no native tool exists for the operation.

## 6. Bug Fixing Protocol (Universal)
1.  **Reproduce First:** Never fix a bug without a failing test case that reproduces it.
2.  **Verify Fail:** Run the test to confirm it fails.
3.  **Fix:** Implement the fix.
4.  **Verify Pass:** Run the test to confirm it passes.
5.  **Regression:** Run the full suite to ensure no regressions.

## 7. Language Specific Guidelines
- **Dynamic Loading:** If you are working in a specific language, you MUST read the corresponding guideline file from `references/languages/` if it exists.
  - Rust: `references/languages/rust.md`
  - Solidity: `references/languages/solidity.md`
  - Python: `references/languages/python.md`
  - JavaScript/TypeScript: `references/languages/javascript.md`
- **Application:** Apply the specific rules in addition to the core guidelines above.
