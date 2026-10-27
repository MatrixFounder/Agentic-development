# Architecture Review: 129 — test-paths-and-dependency-advisories

- **Date:** 2026-10-26
- **Reviewer:** `architecture-reviewer` (read-only subagent), `01-start-feature` step 5.
- **Status:** APPROVED. 0 BLOCKING, 0 MAJOR, 5 MINOR.
- **Reviewed:** `docs/ARCHITECTURE.md`, sha256 prefix `461606da39eb`, 787 lines, at tree fingerprint
  `de5398ca8f07`. The reviewer quoted the fingerprint; the orchestrator recomputed the same value
  at the return.
- **Evidence in the brief:**
  - the diff of the three places against the base `2a7d11c`;
  - `scan_register.py`: `1 warn / 17 info`, as at the base; the added lines `0 warn and 0 info`;
  - TC-C7 of `tests/test_session_state_contract.py`: `8 passed`;
  - every `run:` step of `framework-gates.yml`, run locally: `20 of 20 steps pass`;
  - the probe of §10.7 on copies of the three manifests outside the repository: `npm audit`
    reported no advisory for the regenerated lockfiles, and the smoke render with
    chrome-headless-shell 150.0.7871.24 passed for each install;
  - the render comparison of R3.5 and the security review of R7: NOT RUN, development work.
- **Kept by:** the orchestrator, from the reviewer's hand-back.

## General Assessment

The change edits three statements and no other line. No data model changes. The install path
stays `npm ci --ignore-scripts` from the committed lockfiles, and the acceptance of a browser does
not change.

- Lines 120 and 215 match `update_state.py:383@2a7d11c` `lock_path = fpath + ".lock"`. The read
  and the write run between `_lock` and `_unlock`. The markers of TC-C7 stay.
- The versions match TASK R3.1 and R3.2. Only v10 overrides puppeteer.
- The audit claim matches the probe: `"total": 0` for each of the three lockfiles.
- No other line of the document goes stale. Outside it, R3.6, R6.2 and R6.3 cover the four places
  that still name puppeteer 25.12.0.

## Comments

### BLOCKING

None.

### MAJOR

None.

### MINOR

| ID | Finding | Resolution |
| :--- | :--- | :--- |
| 1 | §10.7 named the lockfile as the place of the overrides; they live in `package.json` | applied: the `overrides` of each `package.json` set the versions, and each lockfile pins puppeteer |
| 2 | The browser sentence held on mac_arm only, and "vouches" named no checkable act | applied: three sentences name `MERMAID_RENDER_BROWSER_SHA256` and the platform of the recorded build |
| 3 | The fallback of TASK R3.7 changes two sentences of §10.7 | PLAN 129, Failure paths: both sentences named; every branch runs `npm audit` on the committed lockfiles and dates §10.7 by that run |
| 4 | Line 120 made the state the actor of "takes a lock" | applied: `update_state.py` takes the lock |
| 5 | TC-C7 does not pin `latest.yaml.lock` | PLAN 129, Task 129.4: TC-C7 asserts the lock file on both lines |

**Before the task:** the register `warn` at `docs/ARCHITECTURE.md:269@2a7d11c`, a sentence of 45
words.

**Observation of the reviewer, not a finding.** Before this task, the setup already ran a browser
older than the build that puppeteer pins: 25.12.0 pins 154.0.8037.57, and the setup ran 150. TASK
129 widens the gap. A protocol mismatch fails the smoke render with exit 1, and R3.5 checks the
renders.

## Final Recommendation

Proceed to Planning. The fixes of MINOR 1, 2 and 4 landed after the round, within the lines that R4
allows; MINOR 3 and 5 go to the plan.
`{"review_file": "docs/reviews/architecture-129-review.md", "has_critical_issues": false}`
