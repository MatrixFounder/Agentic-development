# Framework Audit 120 — Stage 2 of framework-upgrade holds its reviews to the TASK and the lines the change touches

- **Task:** 120 `stage2-review-boundary`. It archives to
  `docs/tasks/task-120-stage2-review-boundary.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1.
- **Date:** 2026-10-09. **Base revision:** `da91d2fefa33242a47356e1b740055e645db5e1e`, clean tree
  at start (TASK 119 committed by the operator as `da91d2f`).
- **Source:** WI-52; the operator's request "сразу же поправь wi-52", and the answer "Реализовать
  правило сейчас".

## 0. Emergency Bypass

None.

## Archive (§1)

TASK 119 and PLAN 119 archived under ID 119:
- both moves `"ok": true`;
- Step 5.5 and Step 7.6.5: one rewrite each, exit 0;
- Step 8 with `--since 5d0c83f…`: exit 3. It reports the two `INBOUND` records of the v3.13.0
  changelog entries, which carry no reason and stay. Step 8 rewrote no file.

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent at fingerprint `74499056f4a6`. No §4 failure condition and no
safety violation. Two MAJOR:
- A3 could not pass for R3.1, since both Framework Upgrade rows of `WORKFLOWS.md` carry register
  `WARN`s at the base.
- R1.1 kept only half of D5 of TASK 119, so a review could pass a change that leaves its own TASK
  unmet.

Seven MINOR:
- which row R3.1 means;
- "(WI-52)" read as a removed record;
- the bullet's indent;
- no severity on the line;
- R4.3's staging terms;
- no changelog text;
- D1's quote.

Revision 2 applies all nine: R3.1 adds item 5 to the §5 Safety Protocol list, and no table cell
changes. R1.1 checks the change against its TASK and the lines it touches, with the finding's
severity.

Before the task, per the reviewer:
- the two Framework Upgrade rows of `WORKFLOWS.md` differ and break §5.1;
- the workflow states no review boundary outside stage 2;
- `skill-self-improvement-verificator` §4 names `GEMINI.md`.

### Round 2 — TASK revision 2: PASS

The same agent at `d6fe2cd4f69d`. Findings 1 to 9 RESOLVED. One MINOR: item 5 of R3.1 and the
entry of R3.2 dropped R1.1's exception for a regression, and the H1 left out the TASK. Revision 3
applies it.

While round 1 ran, the orchestrator wrote this record, an untracked file, against
`skill-parallel-orchestration` §2.4.1. It moved the text to the scratchpad and restored the record
before round 2. The tree then hashed to `d6fe2cd4f69d` again, the value round 2 was given.

**Mode A verdict:** APPROVED, TASK revision 3.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: PASS

A read-only `plan-reviewer` at `4a390335aeaf`. No CRITICAL or MAJOR finding. `plan_gantt.py
--check`, run before the round: exit 0, the region empty for six tasks. Nine MINOR:
- A2, A3 and R1 missing from the cluster table;
- the stated texts checked only by review;
- "TC-1 fails" names a class of two cases;
- no check of the final paths before the apply, and no hash of `framework-upgrade.md` after it;
- no pending list on a stop before stage 3;
- the external tools' status;
- the boundary in the stage-4 briefs, and the fix-round wording;
- the scratchpad list;
- A1 restating §3.1 in part.

PLAN revision 2 applies all nine. `staging.py` reads the bullet from the TASK's R1.1 fence, so no
second copy of the text exists. `plan_gantt.py --check`: exit 0; the register scan: no `WARN`.

Before the task, per the reviewer: §4.5 runs before the stage-3 apply, so `--targets-changed`
never sees the stage-3 targets as changed.

**Mode B verdict:** APPROVED, PLAN revision 2.

## §3 — Execution

- A1: `HEAD` equals the base. The seven edited paths are tracked. The two created paths give
  `git check-ignore` exit 1. All nine pass the path checks of §3.1.
- A2: `tests/staged_run_safety_rules.py` is a byte copy. The driver, mode `base`: 6 cases, 0
  failures.
- B1, the pin first: `staging.patched` puts the bullet into the staged `STEP_4`. The bullet equals
  the R1.1 fence, whitespace collapsed, and it follows the LOW-routes bullet. Mode `base`:
  `test_step_4_is_the_reviewed_text_to_the_end_of_section_3` fails; the other 5 cases pass.
- B2: mode `patched`, 6 cases, 0 failures. Mode `old-pin`, the base module against the patched
  text: the same case fails, the other 5 pass. TC-B1 holds.
- C1 to C3: item 5 of the §5 Safety Protocol; v3.41.0 in both changelogs; WI-52 done, its index
  line under `## Closed`. Item 5 and the English entry equal their fences. Register: 0 `WARN` on
  added lines of the five files, after the closed index line of WI-52 was shortened from 38 words.
  `check_contract_sync.py`: exit 0.
- D1: the patch, three sections; `git apply --check` passes. SHA-256: patch `3cf3d6320d34…`,
  staged file `926a451ab61e…`, `patched(base text)` `298a0513770d…`.
- D2: `run_gates.sh` 18 PASS. Since staging began, only declared paths changed in the tree.

### Stage 2, round 1 — fingerprint `0cffdff015c1`

Both agents quoted the fingerprint and the three prefixes at their start and end; equal on return.
Neither wrote in the tree.

**Code review: APPROVED.** The reviewer applied the patch in a scratch export and ran the CI steps
there: all pass. It reproduced TC-B1 with its own driver; a planted word change in the bullet
fails the pin. Two LOW findings:
- the WI-52 closure reads as a quote of the bullet but drops "marked as before the task";
- "Stage-2" in item 5 has no referent in `WORKFLOWS.md`.

**Security audit: PASS**, `scan_status: findings`. The scan: exit 0, `external.status` COMPLETE,
`not_run` empty. Each tool exit is a finding, and none is in a changed file. The staged file is
outside the runner, pytest's discovery and every allow rule. Three LOW findings:
- the boundary can be read to leave out unchanged code that a registration makes run;
- the bullet does not say whether a CRITICAL or HIGH from before the task sets the verdict that
  `security-audit` §6.2 gives;
- item 5 drops the severity.

Before the task, per the reviewers:
- LOW: `STEP_4` compares with whitespace collapsed, so it does not pin the indent; a bullet moved
  out of stage 2's list still passes.
- LOW: `python3 -m pytest` with no path stops at collection on `examples/skill-testing`, which
  needs `openai`.
- CRITICAL and HIGH, scanner severity, untriaged: 25 CRITICAL and 9 HIGH in-process hits, three
  semgrep ERROR results, bandit's 14 High, and gitleaks' 747 redacted hits, none in a changed
  file.
- LOW: katex GHSA-238p-pmpm-9mq7 in the three renderer lockfiles. MEDIUM: no SBOM.

### Fix round 1

TASK revision 4 (D3) and PLAN revision 3 apply all five LOW findings. The bullet gains two
sentences. The code that the change makes run is among its lines. A finding before the task does
not set the verdict, and a CRITICAL or HIGH one is named to the operator. Item 5 names
`framework-upgrade` §3 step 4 and the severity. The changelogs carry both sentences. The WI-52
closure reads as a summary.

- The pin first: the round-1 pin fails against the new patched text. The new staged pin: mode
  `base` fails one case, mode `patched` passes 6 of 6, and `old-pin` fails one case.
- C3: 0 `WARN` on added lines; item 5 and the English entry equal their fences.
- D1: patch `a1655bc9510c…`, staged file `a258ee29a228…`, `patched(base text)` `2e263ae8a8f1…`;
  `git apply --check` passes. D2: 18 PASS.

### Stage 2, round 2 — fingerprint `b18c75f457e7`

Both agents, resumed, quoted the fingerprint and the three prefixes at their start and end; equal.
Neither wrote in the tree.

**Code review: APPROVED.** The five round-1 findings are RESOLVED. Six planted changes in the new
sentences each fail the pin. The CI steps pass on the applied tree.

**Security audit: PASS**, `scan_status: findings`. The round-1 scan stands; a scan of the changed
and patched files is clean. The new sentences do not conflict with `security-audit` §6.2 or with
the `INCOMPLETE` rule of stage 2: an unfinished part is not a finding.

Three LOW findings, one class: a summary drops a clause of the bullet.
- Item 5 states that a finding before the task does not set the verdict, without naming a
  CRITICAL or HIGH one to the operator.
- The changelogs and the WI-52 closure drop "or run without a prompt".

Round 1 fixed this class (LOW-3), so stage 2's rule for LOW routes of a fixed class applies before
a round 3. The bullet and its pin are correct.

### Fix round 2

The operator chose to write in the clauses and run round 3 (TASK D4: "Дописать и раунд 3").
- TASK revision 5 changes the fences of R3.1 and R3.2 only; R1.1 and the bullet are unchanged.
- Item 5 gains the code that the change makes run, or run without a prompt, and the naming of a
  CRITICAL or HIGH finding to the operator.
- The changelogs and the WI-52 closure gain "or run without a prompt".
- C3: 0 `WARN` on added lines; item 5 and the English entry equal their fences.
- D1: the patch and the staged file hash as in round 2. D2: 18 PASS.

### Stage 2, round 3 — fingerprint `2bf27963b202`

Both agents, resumed, quoted the fingerprint and the three prefixes at their start and end; equal.
Neither wrote in the tree.

- **Code review: APPROVED.** Both round-2 findings RESOLVED; no new finding. Item 5 and the English
  entry equal their fences; every summary carries the bullet's clauses that its fence holds. The
  pin, `run_tests.py` and the loop contract pass on the applied tree.
- **Security audit: PASS**, `scan_status: findings` (round 1's scan; no scanned code changed). LOW
  N1 RESOLVED; no new finding.

**Stage 2 verdict:** passed at round 3 of 3, patch `a1655bc9510c…`.

## Stage 3

### F1 — before the apply

1. §4.5: `check_positional_refs.py --targets-changed`, then with `--fix`. No `REFERENT_MOVED`, and
   the fingerprint `8b50c356a6ba` is the same before and after `--fix`, so no file was repaired.
   The 9 errors were there before the task, as in TASK 118 and 119:
   - links in old changelog entries to `get-token.ts` and `wallet-balances.ts` of another
     repository;
   - `docs/reviews/review-095-independent.md`, whose cited text was edited later.
2. The patch and the staged file hash to the values round 3 quoted. The patch text:

~~~~diff
diff --git a/.agent/workflows/framework-upgrade.md b/.agent/workflows/framework-upgrade.md
--- a/.agent/workflows/framework-upgrade.md
+++ b/.agent/workflows/framework-upgrade.md
@@ -154,6 +154,14 @@
         round: the scope of each route as a residual in the TASK, and one backlog record that
         holds them. The operator chooses between that record and one more round. TASK 116 ran
         seven rounds; from round 4 on, each found a narrower route of one class (WI-48).
+      - **Boundary.** A review round checks the change against its TASK and the lines it touches.
+        Code that the change makes run, or run without a prompt, is among those lines. Any other
+        finding, unless the change causes it as a regression, is one line in the audit record, with
+        its severity, marked as before the task. Such a finding does not set the round's verdict;
+        one of CRITICAL or HIGH severity is named to the operator when the round ends. A new backlog
+        record needs the operator's decision. Each reviewer's brief states this boundary. TASK 119
+        filed two records from such findings, and the operator removed them. WI-52 records this
+        rule.
    3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
       into its file, or the new code over the code it replaces, and removes the copy under the new
       name. Only the retro's records follow this edit. The same edit adds a settings test that
diff --git a/tests/test_run_safety_rules.py b/tests/test_run_safety_rules.py
--- a/tests/test_run_safety_rules.py
+++ b/tests/test_run_safety_rules.py
@@ -85,6 +85,14 @@
         round: the scope of each route as a residual in the TASK, and one backlog record that
         holds them. The operator chooses between that record and one more round. TASK 116 ran
         seven rounds; from round 4 on, each found a narrower route of one class (WI-48).
+      - **Boundary.** A review round checks the change against its TASK and the lines it touches.
+        Code that the change makes run, or run without a prompt, is among those lines. Any other
+        finding, unless the change causes it as a regression, is one line in the audit record, with
+        its severity, marked as before the task. Such a finding does not set the round's verdict;
+        one of CRITICAL or HIGH severity is named to the operator when the round ends. A new backlog
+        record needs the operator's decision. Each reviewer's brief states this boundary. TASK 119
+        filed two records from such findings, and the operator removed them. WI-52 records this
+        rule.
    3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
       into its file, or the new code over the code it replaces, and removes the copy under the new
       name. Only the retro's records follow this edit. The same edit adds a settings test that
diff --git a/tests/staged_run_safety_rules.py b/tests/staged_run_safety_rules.py
deleted file mode 100644
--- a/tests/staged_run_safety_rules.py
+++ /dev/null
@@ -1,349 +0,0 @@
-"""Two rules from the TASK 111 retro (R7), as TASK 112 R7 rewrote them.
-
-TASK 111 registered a PreToolUse hook in this repository while building it; the hook then asked
-for approval on the orchestrator's and the reviewers' own commands in Auto mode. Its bypass hunt
-stopped, and the operator deferred the hook to WI-34. This file pins the rules whole:
-
-* `framework-upgrade` §3 step 4, whole and up to the end of §3: what takes effect at once, the
-  scripts that allow rules run, the test-module exemption, the four stages, the failure branch;
-  and §3.1's fixture exception (``TC-1``);
-* `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
-  no unverified control, tests are not the hunt (``TC-2``);
-* each place that routes an audit, as the whole paragraph, list item or table row that holds its
-  pointer, and `full-robust` §3's gate on `audit_status: PASS` and a scan that ran (``TC-3``);
-* each place that turns the scanner's exit code and summary into `scan_status`, as a block of its
-  own: exit 3 or `summary.not_run` gives `NOT_RUN`, and `summary.tool_exits` gives at least
-  `findings` (``TC-3b``, TASK 118 R5.5).
-
-The pinned texts below are written as they stand in their files, wrapped; the tests compare them
-with whitespace collapsed. A change to a pinned rule changes this file in the same edit, where a
-review sees both.
-"""
-import re
-import unittest
-from pathlib import Path
-
-PROJECT_ROOT = Path(__file__).resolve().parent.parent
-WORKFLOW = ".agent/workflows/framework-upgrade.md"
-SKILL = ".agent/skills/security-audit/SKILL.md"
-WRAPPER = ".claude/agents/security-auditor.md"
-
-
-def _flat(text):
-    return " ".join(text.split())
-
-
-STEP_4 = _flat("""
-4. **Hooks and permission rules take effect at once.** Claude Code applies a settings file to the
-   running session as soon as it changes, the reviewers' commands included. The step covers every
-   change that alters what runs, or what runs without a prompt. The list is not exhaustive:
-   - a hook in a settings file, or in the frontmatter of an agent or a skill;
-   - the script of a registered hook, code that script calls, and a new module it would import;
-   - a script that a committed allow rule names, code that script calls, and a new module it
-     would import;
-   - a permission rule, `additionalDirectories` or the permission mode, an agent's
-     `permissionMode` and the `allowed-tools` of a skill or a command among them;
-   - a settings key that names a command, such as `statusLine`, or sets a command's environment,
-     `env`;
-   - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.
-
-   Test modules and fixtures that no rule names by path are exempt, and so is code that runs
-   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
-   hook or listed script runs or imports; a fixture is a data file that a test reads.
-   `tests/run_tests.py` is named by a rule and is not exempt.
-
-   A change that only narrows what runs without a prompt, such as a removed allow rule, may land
-   at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
-   it narrows, and the audit record holds the check's output:
-   - a base entry of the same list covers each new allow rule, `additionalDirectories` entry and
-     `allowed-tools` entry;
-   - each base deny or ask rule and `disallowedTools` entry is still present, or a new entry of the
-     same list covers it;
-   - every other key equals the base's;
-   - no code of the list above changes, and no new module appears that it would import.
-
-   The run registers nothing in `.claude/settings.local.json` or the user's settings; an edit
-   there waits for the operator's commit and their go-ahead.
-
-   Every other change runs in four stages. The audit record is
-   `docs/reviews/framework-audit-<ID>.md`; the security audit is the review of stage 2.
-   1. **Fixture.** The TASK states the exact registration: the event, matcher and command of a
-      hook, or the text of a rule or key. A hook's test builds a temporary root with its own
-      `.claude/settings.json` holding that registration, and removes it. Code of the list above
-      is edited under a new name.
-   2. **Reviews.** The code review and the security audit check the code and the registration.
-      Both must pass. An `INCOMPLETE` security audit blocks the registration: `security-audit`
-      §6.2 re-runs the unfinished part once, and then the operator decides.
-      <!-- loop:stage2-review-retry -->
-      - **Bound: max 3 review rounds.** A round is one code review and one security audit of the
-        same fingerprint. A round that does not pass returns the run to the fix of its findings.
-        The §6.2 re-run of an `INCOMPLETE` audit is not a round. Still failing after the 3rd
-        round: **STOP** and escalate to the operator with the open findings; the operator
-        decides what follows.
-      - **LOW routes of a fixed class.** A round whose findings are all LOW, each a route of a
-        class that an earlier round of this run fixed, proposes to the operator before the next
-        round: the scope of each route as a residual in the TASK, and one backlog record that
-        holds them. The operator chooses between that record and one more round. TASK 116 ran
-        seven rounds; from round 4 on, each found a narrower route of one class (WI-48).
-      - **Boundary.** A review round checks the change against its TASK and the lines it touches.
-        Code that the change makes run, or run without a prompt, is among those lines. Any other
-        finding, unless the change causes it as a regression, is one line in the audit record, with
-        its severity, marked as before the task. Such a finding does not set the round's verdict;
-        one of CRITICAL or HIGH severity is named to the operator when the round ends. A new backlog
-        record needs the operator's decision. Each reviewer's brief states this boundary. TASK 119
-        filed two records from such findings, and the operator removed them. WI-52 records this
-        rule.
-   3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
-      into its file, or the new code over the code it replaces, and removes the copy under the new
-      name. Only the retro's records follow this edit. The same edit adds a settings test that
-      pins the registration, and the gates run again.
-   4. **Focused review.** A code reviewer and a security auditor check the stage-3 diff on the new
-      fingerprint.
-
-   **Failure.** If the gates of stage 3 fail, or the focused review does not pass, the run
-   restores every file of stage 3's edit at once to its text before that edit. The restore brings
-   back the copy under the new name, if there is one, and the audit record holds the stage-3 diff.
-   - When an `INCOMPLETE` security audit is the only failure, `security-audit` §6.2 governs the
-     re-run, which reads that recorded diff. If the re-run passes, stage 3 applies the same diff
-     again, and stage 4 checks it on the new fingerprint.
-   - In every other case, a failed gate, a rejected code review or a `FAIL` among them, the
-     operator decides what follows. A registration, or the code it runs, whose text changes
-     returns to stage 1.
-
-   **Why.** TASK 111 registered a PreToolUse hook while building it, and the hook asked for
-   approval on the orchestrator's and the reviewers' own commands in Auto mode.
-""")
-SECTION_6_2 = (
-    'An audit has two parts: the scan and the manual adversarial review. Its verdict is one '
-    'of three: - `PASS`: both parts ran to completion and found no CRITICAL or HIGH issue; '
-    '- `FAIL`: a part found a CRITICAL or HIGH issue, whether or not the other part '
-    'completed; - `INCOMPLETE`: a part did not run to completion, and neither part found a '
-    'CRITICAL or HIGH issue. When either part does not run to completion, the audit is '
-    'never `PASS`, and the report names that part. The causes include a refused tool, a '
-    'stopped turn, a missing environment and a scan with `scan_status: NOT_RUN`. An auditor '
-    'whose turn stops returns no report, so the orchestrator records the audit as '
-    '`INCOMPLETE` itself. 1. **Re-run once.** The orchestrator re-runs that part once, in a '
-    "fresh agent or session, on the round's frozen tree. A fix round does not reset the "
-    'count: each part gets one re-run in a run. 2. **Then the operator decides.** If the '
-    're-run does not complete either, the operator chooses in their own message, and the '
-    'record quotes it. The choices are to ship the control with the gap recorded, to defer '
-    'it to a work-item, or to remove it. 3. **No unverified security claim.** A security '
-    'control whose bypass hunt never finished does not ship as protection. Its changelog '
-    'and documents say it is unverified, or it moves to a work-item. 4. **Tests are not the '
-    'hunt.** Tests and a mutation run with a passing baseline show that the tests pin the '
-    "specification. They do not show that the specification closes the threat. (TASK 111's "
-    'retro wrote this rule. The bypass hunt on its anchor hook had stopped, and the '
-    'operator had deferred the hook to a work-item.)'
-)
-#: Each router's pointers, as the whole block that holds each: a paragraph, a list item or a
-#: table row. A sentence appended inside the block changes it (TASK 112 R6.3).
-POINTERS = {
-    WRAPPER: (
-        """- **An unfinished part makes the audit `INCOMPLETE`.** A part is the scan or the
-        adversarial review. When a part found a CRITICAL or HIGH issue, the audit is `FAIL`. Name
-        the unfinished part. The orchestrator re-runs it once, then the operator decides
-        (`security-audit` §6.2).""",
-        """- **`scan_status` is a required field and it is not decoration.** `NOT_RUN` forces
-        `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or HIGH
-        issue — never `PASS`. Without that, a scan-less audit reported the same machine-readable
-        verdict as a clean one, and every consumer that gates on the footer (`full-robust` §3,
-        `security-audit.md` step 4) treated "we did not look" as "we looked and it was fine".
-        Reporting the gap in prose while the footer says `PASS` is the fabrication this replaced,
-        one layer down.""",
-    ),
-    "System/Agents/10_security_auditor.md": (
-        """5. **Unfinished parts:** a scan or an adversarial review that did not run to completion
-        makes the audit `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue, and the
-        summary names it (`security-audit` §6.2).""",
-        """- `scan_status` is `"clean" | "findings" | "NOT_RUN"` and is **required**. `"NOT_RUN"`
-        forces `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or
-        HIGH issue — never `"PASS"`. Without it a scan-less audit is machine- indistinguishable
-        from a clean one, and every consumer that branches on this footer treats "we did not look"
-        as "we looked and it was fine".""",
-    ),
-    ".agent/workflows/security-audit.md": (
-        """- A review that does not run to completion makes the audit `INCOMPLETE`, or `FAIL` when a
-        part found a CRITICAL or HIGH issue: name the part. The orchestrator re-runs it once, then
-        the operator decides (`security-audit` §6.2).""",
-        """- **If you cannot execute it** (no execution tool in your role, or the environment
-        refuses): record `scan_status: NOT_RUN (<reason>)`, continue to step 3, and carry that
-        status into the report. **Never invent the output** (`security-audit` §1). `NOT_RUN` makes
-        the audit `INCOMPLETE`, or `FAIL` when step 3 finds a CRITICAL or HIGH issue, never `PASS`
-        — step 4's "until clean" loop cannot be satisfied by a scan that never ran.""",
-        """- If findings exist: a. Fix implementation (apply patches, rotate secrets). b. Add
-        regression tests (security-focused). <!-- loop:audit-remediation --> c. Re-run audit
-        script until clean. **Bound: max 3 iterations** when this workflow is entered directly; a
-        caller may re-scope both the cap and the definition of "clean" (`full-robust` §3 does
-        exactly that). On exhaustion with findings still open → **STOP** and escalate the open
-        findings to the user. Per step 2, a `scan_status: NOT_RUN` never satisfies this loop: the
-        verdict is `INCOMPLETE` or `FAIL`, not clean, and `security-audit` §6.2 governs its one
-        re-run.""",
-    ),
-    ".agent/workflows/full-robust.md": (
-        """- **Gate:** the audit footer reads `audit_status: PASS`, the automated scan ran to
-        completion (`scan_status` is `clean` or `findings`), AND the manual review (per the
-        `security-audit` skill §3 checklists) emits a severity-labelled findings table with **no
-        CRITICAL/HIGH findings**. The table rules on each CRITICAL or HIGH hit of the scan: a
-        confirmed hit is a finding, and a rejected one is listed as a false positive. An
-        `INCOMPLETE` audit never meets it.""",
-        """- **A scan that did not run is not a scan that passed.** `scan_status: NOT_RUN`
-        (equivalently a `scan: NOT RUN (<reason>)` line) fails the scan conjunct: the gate is **not
-        met** and the verdict is `INCOMPLETE`, or `FAIL` when the manual review found a CRITICAL or
-        HIGH issue. The missing part is re-run once; if it still does not complete, the reason is
-        escalated to the user (`security-audit` §6.2). Left unstated, `NOT RUN` is neither clean
-        nor unclean and the undefined branch resolves in practice to "the other conjunct
-        passed".""",
-    ),
-    "System/Docs/SKILLS.md": (
-        """| **`security-audit`** | Vulnerability assessment v3.12 (two-layer model: deterministic
-        regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping
-        table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance,
-        auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity
-        reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC
-        (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool
-        integrations (incl. `snyk-agent-scan`), a status for each external tool and exit 3 for a
-        scan part that did not run, private disclosure of a dependency finding (§6.1), an
-        unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH
-        issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |""",
-    ),
-    "System/Docs/WORKFLOWS.md": (
-        """| **Security Audit** | Runs the security auditor agent. Remediation loop bounded at **max
-        3 iterations** when invoked directly; `full-robust` §3 re-scopes both the cap and the
-        definition of "clean". A `scan_status: NOT_RUN` yields `INCOMPLETE`, or `FAIL` when the
-        manual review found a CRITICAL or HIGH issue, never clean (`security-audit` §6.2). | `run
-        security-audit` |""",
-    ),
-}
-
-#: TC-3b (TASK 118 R5.5): each router that reads the scanner states how its exit code and summary
-#: set `scan_status`, in a block outside the blocks of `POINTERS`.
-SCAN_STATUS_POINTERS = {
-    WRAPPER: (
-        """- **The scanner's exit code and summary set the floor of `scan_status`.** Exit 3, or a
-        `summary.not_run` list that is not empty, means a part of the scan did not run:
-        `scan_status: "NOT_RUN"`. A `summary.tool_exits` list that is not empty means an external
-        tool reported a finding or failed: `scan_status` is at least `"findings"`, and
-        `"NOT_RUN"` when the tool's output shows an error (`security-audit` §2). A run that prints
-        no report, such as exit 1 with a JSON `error` or exit 2, is `"NOT_RUN"`.""",
-    ),
-    "System/Agents/10_security_auditor.md": (
-        """- The scanner sets the floor of `scan_status`. Exit 3, or a `summary.not_run` list that
-        is not empty, gives `"NOT_RUN"`. A `summary.tool_exits` list that is not empty gives at
-        least `"findings"`, and `"NOT_RUN"` when the tool's output shows an error
-        (`security-audit` §2). A run that prints no report, such as exit 1 with a JSON `error` or
-        exit 2, gives `"NOT_RUN"`.""",
-    ),
-    ".agent/workflows/security-audit.md": (
-        """- **A partial scan is `NOT_RUN`.** Exit 3, or a `summary.not_run` list that is not
-        empty, records `scan_status: NOT_RUN (<the parts it names>)`. A `summary.tool_exits` list
-        that is not empty records at least `scan_status: findings`, and `scan_status: NOT_RUN`
-        when the tool's output shows an error (`security-audit` §2). A run that prints no report,
-        such as exit 1 with a JSON `error` or exit 2, records `scan_status: NOT_RUN`.""",
-    ),
-}
-
-
-def _read(rel):
-    path = PROJECT_ROOT / rel
-    if not path.is_file():
-        raise AssertionError(f"{rel}: the file is missing")
-    return path.read_text(encoding="utf-8")
-
-
-def _section(text, heading):
-    m = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.M)
-    if not m:
-        raise AssertionError(f"heading {heading!r} is missing")
-    level = len(m.group(1))
-    end = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, m.end())
-    return text[m.end():end.start() if end else len(text)]
-
-
-def _step(section, number):
-    """The text of a top-level numbered step, up to the next one."""
-    m = re.search(rf"^{number}\. .*?(?=^\d+\. |\Z)", section, re.M | re.S)
-    if not m:
-        raise AssertionError(f"step {number} is missing")
-    return m.group(0)
-
-
-def _step_to_end(section, number):
-    """The text of a top-level numbered step, up to the end of the section (TASK 112 R6.3)."""
-    m = re.search(rf"^{number}\. ", section, re.M)
-    if not m:
-        raise AssertionError(f"step {number} is missing")
-    return section[m.start():]
-
-
-def _blocks(text):
-    """Each paragraph, list item and table row of `text`, whitespace collapsed."""
-    item = re.compile(r"^\s*(?:[-*+]|\d+\.)\s|^\s*\|")
-    blocks, current = [], []
-    for line in text.splitlines():
-        if not line.strip() or (item.match(line) and current):
-            if current:
-                blocks.append(_flat(" ".join(current)))
-            current = [line] if line.strip() else []
-            continue
-        current.append(line)
-    if current:
-        blocks.append(_flat(" ".join(current)))
-    return blocks
-
-
-class TestHookRegistration(unittest.TestCase):
-    """TC-1: a hook or a permission rule takes effect at once."""
-
-    maxDiff = None
-
-    def setUp(self):
-        self.section = _section(_read(WORKFLOW), "3. Execution (Atomic Updates)")
-
-    def test_step_4_is_the_reviewed_text_to_the_end_of_section_3(self):
-        self.assertEqual(_flat(_step_to_end(self.section, 4)), STEP_4)
-
-    def test_base_check_allows_the_fixture(self):
-        self.assertIn("A test fixture that the test itself creates in a temporary directory and "
-                      "removes is no such copy (step 4).", _flat(_step(self.section, 1)))
-
-
-class TestIncompleteReview(unittest.TestCase):
-    """TC-2: a review that cannot finish."""
-
-    maxDiff = None
-
-    def test_section_6_2_is_the_reviewed_text(self):
-        self.assertEqual(_flat(_section(_read(SKILL), "6.2 A review that cannot finish")),
-                         SECTION_6_2)
-
-
-class TestPointers(unittest.TestCase):
-    """TC-3: every place that routes an audit states the rule, in a block of its own."""
-
-    maxDiff = None
-
-    def test_each_router_states_the_rule_whole(self):
-        for rel, expected in POINTERS.items():
-            blocks = _blocks(_read(rel))
-            for block in expected:
-                block = _flat(block)
-                with self.subTest(file=rel, block=block[:50]):
-                    self.assertIn(block, blocks)
-
-    def test_each_router_maps_the_scanner_status(self):
-        """TC-3b (TASK 118 R5.5)."""
-        for rel, expected in SCAN_STATUS_POINTERS.items():
-            blocks = _blocks(_read(rel))
-            for block in expected:
-                block = _flat(block)
-                with self.subTest(file=rel, block=block[:50]):
-                    self.assertIn(block, blocks)
-
-    def test_blocks_split_at_items_rows_and_blank_lines(self):
-        text = "- one\n  two\n- three\n\npara\nline\n| a | b |\n| c | d |\n"
-        self.assertEqual(_blocks(text), ["- one two", "- three", "para line", "| a | b |",
-                                         "| c | d |"])
-
-
-if __name__ == "__main__":
-    unittest.main()
~~~~

3. SHA-256 and mode of each file the patch touches, before the apply:

   - `.agent/workflows/framework-upgrade.md`: `a50f248e00c5101ff7a74926c336ad3d0d834911c598d99880db35edf0b881f5`, mode `644`
   - `tests/test_run_safety_rules.py`: `e18dd6a674ecd9ffcc68405447711591d18469557a7739839b174ad6c1c8084a`, mode `644`
   - `tests/staged_run_safety_rules.py`: `a258ee29a22891ba726e03cb301d872ed5f2e7dfb62a5a16173cda994c493064`, mode `644`

### F1 — the apply and the gates

4. `git diff --quiet <base>` of the two final paths: exit 0; no step-1 repair touched them. Then
   `git apply --whitespace=nowarn` of the patch: exit 0.
5. Postcondition: `tests/test_run_safety_rules.py` hashes to the staged file's `a258ee29a228…`;
   `framework-upgrade.md` hashes to `2e263ae8a8f1…`, the value round 3 quoted for
   `patched(base text)`; the staged file is gone; `git apply --check -R` passes.

The gates of D2 again: 18 PASS. `tests/test_run_safety_rules.py`: 6 passed. A1: **Boundary.** is
the third bullet of stage 2, at indent 6 with continuation lines at 8. No cache file in the tree
is newer than the run's staging.

## Stage 4 — fingerprint `2612f225cdcb`

Both agents, resumed, quoted the fingerprint, the patch hash and the two final hashes at their
start and end; equal. Neither wrote in the tree, and neither reversed the patch.

- **Code review: APPROVED**, no finding. It reproduced F1 steps 1 to 5 in a scratch tree. The
  `~~~~diff` fence equals the patch byte for byte. A1 holds, and the CI steps pass.
- **Security audit: PASS**, `scan_status: findings` (round 1's scan; the applied change adds text
  only). No finding. The ASTs of the test at HEAD and after the apply are equal with `STEP_4`
  masked: no new import, call or I/O.

**Stage 4 verdict:** passed. The upgrade is ready for the operator's commit.

## Retro (§6)

The run held the claim `framework-upgrade-wi-52-stage2-boundary` from its start. Observed
candidates were put to the operator:
- the summaries dropped clauses of the bullet twice, so stage 2 took three rounds;
- the audit record was written while spec round 1 ran, and the record was restored before round 2;
- spec round 1 failed on two MAJOR findings.

The operator answered "Всё прошло нормально": nothing is collected or filed. The claim is
released.
