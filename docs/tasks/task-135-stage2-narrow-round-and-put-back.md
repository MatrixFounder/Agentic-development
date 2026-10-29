# TASK 135 — [LIGHT] Stage 2 of `framework-upgrade` gains a narrow round and a site list, and its put-back removes nothing

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 135 |
| Slug | stage2-narrow-round-and-put-back |
| Type | Framework Upgrade, Light Mode (D1) |
| Source | WI-54, WI-56, WI-58; the operator's request of 2026-10-28 |
| Base revision | `88d21619ce14ec7fb6dc1c37eb5b7032b2885d98` |
| Closes | WI-54, WI-56, WI-58 |
| Archive name | `task-135-stage2-narrow-round-and-put-back.md` |
| Revision | 2 |

**Request.** The operator took WI-56 and WI-54 as one task, and WI-58 with its option 1. All three
edit `framework-upgrade` §3 step 4. The bound of stage 2 names no narrow round, though the operator
chose one in TASK 130 (D17) and in TASK 133 (D10, D11).

**Revision 2** follows the code review of commit `13ba348`, which ran after the commit (D7): CHANGES
REQUESTED, with two MAJOR, ten MINOR and thirteen NIT findings. The fix pass:
- M1: a created path stops the run for the operator (R4);
- M2, m3, m4: the site list is part of the finding, by `developer-guidelines` §6.4, and names the
  state or the input of the finding (R3);
- m1, m2: the narrow round is the operator's choice, and its briefs set its scope (R1);
- m5, m6: the rule on a fix of prose, which the fixer's brief states (R2); D4 names the half of
  option 2 that is not taken;
- m7, m8, m9, n6: the wording of the put-back and of the user's files (R4 to R6);
- n1, n2: the pins of §2 and the method of TC-3; n3: one sentence split; n4: the test's docstring;
  n7: `System/Docs/WORKFLOWS.md`; n5, n12, n13: step 4 keeps no bare reference (D8).

Not taken:
- m10, the process of D1, which the operator chose;
- n8, the second half of the acceptance of WI-58, which the record names as pending;
- n9 and n10, which the hash stop and the operator's reading cover;
- the three findings before the task.

Step 4 holds 1616 words.

## 1. Decisions

- D1, 2026-10-28, operator: Light Mode. The run has a `[LIGHT]` TASK, the edit and its pinning
  test, the test run, one code reviewer with the exhaustive prompt and one fix pass. Rejected: the
  full `/framework-upgrade` and a reduced one — the cost of a run, which the operator named. The
  change alters nothing that runs, so stages 1 to 4 of step 4 do not apply to it.
- D2, 2026-10-28, operator: the scope is the three records. Step 4 does not grow: its word count
  after the edit is at most 1623, the count at the base.
- D3, 2026-10-28, operator: WI-54 option 1. The put-back removes nothing.
- D4, 2026-10-28, operator: WI-56 options 1 and 2, both in `framework-upgrade.md`.
  `developer-guidelines` is not edited. The test-first half of option 2 is not taken: a fix of
  prose has no scenario that a test runs, and the pin of step 4 fails on any change of its words.
- D5, 2026-10-28, operator: WI-58 option 1. A site list is due only for a finding that the fix
  classes as one site of a class.
- D6, 2026-10-28, orchestrator: the ID is 135. TASK 133 D1 holds 134 for WI-39.
- D7, 2026-10-28, operator: the commit precedes the code review, and the fixes land in a commit of
  their own.
- D8, 2026-10-28, operator: step 4 keeps no bare reference to a task or a record. A consumer of
  the workflow numbers its own tasks and records.

## 2. Requirements

<!-- contract:requirements -->

- R1 (WI-56 option 1) — past the bound of stage 2, the operator may choose a narrow round. Its
  briefs limit it to the last fix and the lines that the fix touches.
- R2 (WI-56 option 2) — the fixer's brief states that a fix of prose adds a clause only where
  narrowing one cannot answer the finding.
- R3 (WI-58 option 1) — the fix can class a finding as one site of a class. The audit record then
  lists each such site in the change, as part of that finding (`developer-guidelines` §6.4). A site
  is each write, removal, creation and open of the finding's state, or each route of its input, on
  each code path. Each site has a fix and a test, or the reason the class cannot occur there. The
  brief of the next round cites the list.
- R4 (WI-54 option 1, S3-1, S3-2) — the put-back removes no file and no directory. A path that the
  command created stops the run for the operator.
- R5 (WI-54, R3-2) — the check hashes what the user's three files hold, following a link, or their
  absence.
- R6 (WI-54, R3-4, I-2) — the restore command of the put-back carries `-c core.fsmonitor=false`. A
  restored file that hashes otherwise than in the first listing stops the run.
- R7 (D2) — the word count of step 4 is at most 1623. No rule of step 4 changes for it:
  - three history sentences become references: (WI-48), (WI-52), (TASK 122). Revision 2 removes
    them, and the other references of step 4 (D8);
  - four reasons leave the text: the sentence on where Claude Code adds an allow rule, "which holds
    every stash", the purpose of `-c core.fsmonitor=false`, and "it runs nothing new, and at worst
    a command asks".
- R8 — WI-54, WI-56 and WI-58 are closed in their records and in `docs/BACKLOG.md`; both
  changelogs carry the release.

**Out of scope.**

- `developer-guidelines` (D4);
- a lighter `framework-upgrade` as a whole, which the operator discusses separately (D2);
- the two `INBOUND` records of the archive of TASK 133: `CHANGELOG.md:3773@88d2161`,
  `CHANGELOG.ru.md:3806@88d2161`, slot links that TASK 133 did not write.

## 3. Files

- `.agent/workflows/framework-upgrade.md`
- `tests/test_run_safety_rules.py`
- `docs/backlog/wi-54-residual-routes-of-the-task-123-put-back.md`
- `docs/backlog/wi-56-a-fix-of-rule-text-in-stage-2-gives-the-next-round-new-text-to-review.md`
- `docs/backlog/wi-58-a-fix-round-of-stage-2-fixes-the-instance-of-a-class-and-the-next-round-finds-the-next-site.md`
- `docs/BACKLOG.md`
- `CHANGELOG.md`, `CHANGELOG.ru.md`
- `System/Docs/WORKFLOWS.md` (revision 2)
- `docs/TASK.md`; the archive pair of TASK 133

## 4. Acceptance

- TC-1 — `tests/test_run_safety_rules.py`: `STEP_4` equals step 4 of the edited workflow → pass;
  fails when a word of step 4 differs from the pinned text.
- TC-2 — the full suite, `python3 tests/run_tests.py` → the same result as at the base.
- TC-3 — a word count of step 4, from `4. **Hooks` up to the line `## 4. Documentation`, which it
  excludes → at most 1623.
- TC-4 — `scan_register.py` on the edited lines → no new finding.
