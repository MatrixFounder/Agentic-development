# VDD Critique: [Feature Name]

## 1. Executive Summary
- **Verdict**: [PASS / WARNING / FAIL]
  - PASS: the exit bar of SKILL.md §2 is met.
  - WARNING: no CRITICAL finding, but the bar is not met (legitimate findings remain, or the test run is unverifiable). WARNING is not an approval.
  - FAIL: at least one CRITICAL finding.
- **Confidence**: [High/Medium/Low]
- **Summary**: [1-2 sentences]

## 2. Test Evidence (Exit Bar)
- **Command**: [the full test run, as executed] or `none`
- **Result**: [captured output, or a summary: exit code, pass/fail counts, failures] or `NOT RUN (<reason>)`
- **Source**: [run by the reviewer / handed over with the review / none: nothing handed over, nothing run]
- **Tree state** (optional): [the fingerprint handed over, or the commit plus a hash over the working-tree diff and every untracked file], `NOT COMPUTED (<reason>)`, or `absent`

A test run that is `NOT RUN` or has no evidence goes into the Risk Analysis table as the finding 'exit-bar condition unverifiable — <thing> NOT RUN (<reason>)', with severity HIGH.

## 3. Risk Analysis
Severity: CRITICAL / HIGH / MEDIUM / LOW. Confidence per finding: High / Medium / Low.

| Severity | Confidence | Category | Issue | Impact | Recommendation | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HIGH** | High | Security | [Description, `file:line`] | [Exploit/Crash] | [Specific fix] | [test or check that proves the fix] |
| **MEDIUM** | Low | Logic | [Description, `file:line`] | [Bug] | [Specific fix] | [test or check that proves the fix] |

## 4. Hallucination Check
- [ ] **Files**: Confirmed all cited files exist in a directory listing.
- [ ] **Line Numbers**: Confirmed code actually exists at these lines.
