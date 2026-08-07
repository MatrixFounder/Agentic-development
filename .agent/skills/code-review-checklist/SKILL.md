---
name: code-review-checklist
description: "Structured checklist for code review: bugs, style, performance, security, docs."
tier: 1
version: 1.3
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
- [ ] **Dead Code:** Before proposing a deletion — symbol grepped repo-wide? (callout below)

> ### Before acting on a "remove dead code" finding
> 1. **Grep the symbol repo-wide — never scope the search to a test directory.** Tests are not
>    always in one: Go keeps `*_test.go` beside the source, Rust puts unit tests inline under
>    `#[cfg(test)]`, JS/TS co-locates `*.spec.ts` / `__tests__/`, Python uses `tests/`, Foundry
>    uses `test/*.t.sol`. A directory-scoped grep returns "nothing depends on it" precisely where
>    that answer is wrong.
> 2. **If a test drives it, the fix is not deletion** — make production reach the branch (wire the
>    flag, pass the parameter) so code and requirement agree.
> 3. **Report it as "unreachable *and* covered by test X"**, not "dead, delete". A finding can be
>    right about the smell and wrong about the fix.

## 3. Documentation "First"
- [ ] **Directory Docs:** `.AGENTS.md` updated for touched source directories under memory tracking policy (or bootstrap step recorded)?
- [ ] **Docstrings:** Present for new classes/methods? (Google/JSDoc)
- [ ] **Project Docs:** README updated if architecture changed?
- [ ] **Positional references:** If this change touches BOTH an artifact and a document citing it by
      line/offset/ordinal — were those references re-checked **against the final state** of the
      change, and is any pre-edit quotation tagged with its revision? (`documentation-standards` §4.1)
      **The reviewer owns this one**: the author's own check passes even when it ran too early.

## 4. Testing
- [ ] **E2E:** Passed? Checks main scenario?
- [ ] **Regression:** All passed?
- [ ] **Unit:** Edge cases covered?
- [ ] **No Mocking:** Real LLM/DB used in integration tests?

## 5. Consistency
- [ ] **Backward Compatibility:** Existing consumers not broken?
- [ ] **Architecture:** Follows layers (Service -> Repo)?
- [ ] **Style:** Matches project conventions?

## 6. High Assurance (If Tier 3 Active)
- [ ] **Fail Reason Verified?** Did the tests fail exactly as predicted?
- [ ] **Pass Reason Rational?** Does `EXPLAIN_PASS_REASON` match the code?
- [ ] **Law of Minimalism:** No dead code? No speculation? (deletion guard: §2)
- [ ] **Mutation Check:** If you delete a line, does it fail?

## 7. References (`documentation-standards` §4.1)
- [ ] **Coordinates repaired in THIS commit:** `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed`
      was run — it selects documents *citing* the files this change touched, which default diff
      scope does not — and `--fix` landed in the same commit. A coordinate corrected later was
      false in a commit someone can check out.
- [ ] **Verdicts resolved:** zero `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS`, or each survivor
      carries a written reason. `REFERENT_ABSENT` means the cited text was edited, so the sentence
      citing it needs re-reading — not a new number.
- [ ] **A coordinate carrying no referent is not a defect.** Reported as *not examined*, and this
      review never demands one be added.

## Criticality Protocol
Severity is a named value, never a glyph (`documentation-standards` §5.5 rule 5).
- **BLOCKING:** Task not done, Test failure, Broken compat, Stub violation (Logic in stub task).
- **MAJOR:** Documentation missing, Duplication, Poor names.
- **MINOR:** Style nits.
