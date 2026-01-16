---
name: code-review-checklist
description: "Structured checklist for code review: bugs, style, performance, security, docs."
version: 1.1
---
# Code Review Checklist

## 1. Task Compliance
- [ ] **Requirements:** Fulfills all "Changes Description" items?
- [ ] **Acceptance Criteria:** Met?
- [ ] **Use Cases:** Main scenario works?

## 2. Implementation Quality
- [ ] **Top-Down/Stubs:**
    - *Stub Task:* Returns hardcoded values? NO logic? E2E checks hardcode?
    - *Impl Task:* Real logic replaces stub? E2E updated?
- [ ] **No Duplication:** used existing methods/helpers?
- [ ] **Error Handling:** Exceptions caught and logged?
- [ ] **Code Smells:** No magic numbers, understandable names?

## 3. Documentation "First"
- [ ] **Directory Docs:** `.AGENTS.md` updated in *every* touched directory?
- [ ] **Docstrings:** Present for new classes/methods? (Google/JSDoc)
- [ ] **Project Docs:** README updated if architecture changed?

## 4. Testing
- [ ] **E2E:** Passed? Checks main scenario?
- [ ] **Regression:** All passed?
- [ ] **Unit:** Edge cases covered?
- [ ] **No Mocking:** Real LLM/DB used in integration tests?

## 5. Consistency
- [ ] **Backward Compatibility:** Existing consumers not broken?
- [ ] **Architecture:** Follows layers (Service -> Repo)?
- [ ] **Style:** Matches project conventions?

## Criticality Protocol
- 🔴 **BLOCKING:** Task not done, Test failure, Broken compat, Stub violation (Logic in stub task).
- 🟡 **MAJOR:** Documentation missing, Duplication, Poor names.
- 🟢 **MINOR:** Style nits.
