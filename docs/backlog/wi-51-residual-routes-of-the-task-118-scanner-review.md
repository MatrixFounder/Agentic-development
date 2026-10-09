---
id: WI-51
type: work-item
status: open
opened_at: 2026-10-09
slug: wi-51-residual-routes-of-the-task-118-scanner-review
effort: M
value: 'a security-audit scan never blocks on, or reads complete after, a part it did not scan'
source: 'TASK 118 stage 2, round 2 (D18)'
component: '.agent/skills/security-audit/scripts/'
---

# WI-51 — Residual routes of the TASK 118 scanner review

**Signal.** Stage 2 of TASK 118 left four routes outside its fix rounds. Each was found by a
reviewer of that run and is recorded in `docs/reviews/framework-audit-118.md`:

- **A FIFO under a scanned extension.** The in-process scans open each file of a matching
  extension. The stage-2 code review measured a FIFO named `package-lock.json`: it blocked the
  secrets scan until the process was killed, in the base and after TASK 118. TASK 118 fixed the
  dependency scan and the external layer only (D16).
- **A wrapper's exit code.** A tool started through a wrapper that reports its child's death as a
  positive code, such as 127, records `ran` and completes its slot. TASK 118 classifies a negative
  code only (D13); the auditor documents name an error in the tool's output as `NOT_RUN`.
- **The `mcp-scan` fallback.** It runs with no argument. Its target is then probably the operator's
  own configuration, not the scanned tree (low confidence, not measured).
- **A test helper's `PATH`.** The base helper of `tests/test_lockfile_audit.py` puts the fake `npm`
  before the real `PATH`, so an installed tool can start in a case that does not fake it.

Round 3 of that review, the last the bound allows, left three items that would have changed
reviewed files:

- `printable` does not escape the backslash, so a file name that holds the text `\x0a` prints
  as an escaped newline does (INFO);
- the module docstring of `tests/test_lockfile_audit.py` lists TC-E19 but not TC-E19b (NIT);
- the auditor bullet of `security-audit` §2, **Exit codes and summary**, lacks the routers'
  sentence that a run with no report is `NOT_RUN` (NIT).

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Check `S_ISREG` before each open of the in-process walks; measure `mcp-scan`'s target; narrow the helper's `PATH` | M | four small changes, each with a test |
| 2 | Fix the FIFO route only | S | the other three stay |

**Recommendation.** Option 1.
