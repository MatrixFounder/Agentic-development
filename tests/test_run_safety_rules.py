"""Two rules from the TASK 111 retro (R7), as TASK 112 R7 rewrote them.

TASK 111 registered a PreToolUse hook in this repository while building it; the hook then asked
for approval on the orchestrator's and the reviewers' own commands in Auto mode. Its bypass hunt
stopped, and the operator deferred the hook to WI-34. This file pins the rules whole:

* `framework-upgrade` §3 step 4, whole and up to the end of §3: what takes effect at once, the
  scripts that allow rules run, the test-module exemption, the four stages, the failure branch;
  and §3.1's fixture exception (``TC-1``);
* `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
  no unverified control, tests are not the hunt (``TC-2``);
* each place that routes an audit, as the whole paragraph, list item or table row that holds its
  pointer, and `full-robust` §3's gate on `audit_status: PASS` and a scan that ran (``TC-3``);
* each place that turns the scanner's exit code and summary into `scan_status`, as a block of its
  own: exit 3 or `summary.not_run` gives `NOT_RUN`, and `summary.tool_exits` gives at least
  `findings` (``TC-3b``, TASK 118 R5.5).

The pinned texts below are written as they stand in their files, wrapped; the tests compare them
with whitespace collapsed. A change to a pinned rule changes this file in the same edit, where a
review sees both.
"""
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ".agent/workflows/framework-upgrade.md"
SKILL = ".agent/skills/security-audit/SKILL.md"
WRAPPER = ".claude/agents/security-auditor.md"


def _flat(text):
    return " ".join(text.split())


STEP_4 = _flat("""
4. **Hooks and permission rules take effect at once.** Claude Code applies a settings file to the
   running session as soon as it changes, the reviewers' commands included. The step covers every
   change that alters what runs, or what runs without a prompt. The list is not exhaustive:
   - a hook in a settings file, or in the frontmatter of an agent or a skill;
   - the script of a registered hook, code that script calls, and a new module it would import;
   - a script that a committed allow rule names, code that script calls, and a new module it
     would import;
   - a permission rule, `additionalDirectories` or the permission mode, an agent's
     `permissionMode` and the `allowed-tools` of a skill or a command among them;
   - a settings key that names a command, such as `statusLine`, or sets a command's environment,
     `env`;
   - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.

   Test modules and fixtures that no rule names by path are exempt, and so is code that runs
   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
   hook or listed script runs or imports; a fixture is a data file that a test reads.
   `tests/run_tests.py` is named by a rule and is not exempt.

   A change that only narrows what runs without a prompt, such as a removed allow rule, may land
   at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
   it narrows, and the audit record holds the check's output:
   - a base entry of the same list covers each new allow rule, `additionalDirectories` entry and
     `allowed-tools` entry;
   - each base deny or ask rule and `disallowedTools` entry is still present, or a new entry of the
     same list covers it;
   - every other key equals the base's;
   - no code of the list above changes, and no new module appears that it would import.

   The run registers nothing in `.claude/settings.local.json` or the user's settings; an edit
   there waits for the operator's commit and their go-ahead.

   Every other change runs in four stages. The audit record is
   `docs/reviews/framework-audit-<ID>.md`; the security audit is the review of stage 2.
   1. **Fixture.** The TASK states the exact registration: the event, matcher and command of a
      hook, or the text of a rule or key. A hook's test builds a temporary root with its own
      `.claude/settings.json` holding that registration, and removes it. Code of the list above
      is edited under a new name.
   2. **Reviews.** The code review and the security audit check the code and the registration.
      Both must pass. An `INCOMPLETE` security audit blocks the registration: `security-audit`
      §6.2 re-runs the unfinished part once, and then the operator decides.
      <!-- loop:stage2-review-retry -->
      - **Bound: max 3 review rounds.** A round is one code review and one security audit of the
        same fingerprint. A round that does not pass returns the run to the fix of its findings.
        The §6.2 re-run of an `INCOMPLETE` audit is not a round. Still failing after the 3rd
        round: **STOP** and escalate to the operator with the open findings; the operator
        decides what follows.
      - **LOW routes of a fixed class.** A round whose findings are all LOW, each a route of a
        class that an earlier round of this run fixed, proposes to the operator before the next
        round: the scope of each route as a residual in the TASK, and one backlog record that
        holds them. The operator chooses between that record and one more round. TASK 116 ran
        seven rounds; from round 4 on, each found a narrower route of one class (WI-48).
      - **Boundary.** A review round checks the change against its TASK and the lines it touches.
        Code that the change makes run, or run without a prompt, is among those lines. Any other
        finding, unless the change causes it as a regression, is one line in the audit record, with
        its severity, marked as before the task. Such a finding does not set the round's verdict;
        one of CRITICAL or HIGH severity is named to the operator when the round ends. A new backlog
        record needs the operator's decision. Each reviewer's brief states this boundary. TASK 119
        filed two records from such findings, and the operator removed them. WI-52 records this
        rule.
   3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
      into its file, or the new code over the code it replaces, and removes the copy under the new
      name. Only the retro's records follow this edit. The same edit adds a settings test that
      pins the registration, and the gates run again.
   4. **Focused review.** A code reviewer and a security auditor check the stage-3 diff on the new
      fingerprint.

   **Failure.** If the gates of stage 3 fail, or the focused review does not pass, the run
   restores every file of stage 3's edit at once to its text before that edit. The restore brings
   back the copy under the new name, if there is one, and the audit record holds the stage-3 diff.
   - When an `INCOMPLETE` security audit is the only failure, `security-audit` §6.2 governs the
     re-run, which reads that recorded diff. If the re-run passes, stage 3 applies the same diff
     again, and stage 4 checks it on the new fingerprint.
   - In every other case, a failed gate, a rejected code review or a `FAIL` among them, the
     operator decides what follows. A registration, or the code it runs, whose text changes
     returns to stage 1.

   **Why.** TASK 111 registered a PreToolUse hook while building it, and the hook asked for
   approval on the orchestrator's and the reviewers' own commands in Auto mode.
""")
SECTION_6_2 = (
    'An audit has two parts: the scan and the manual adversarial review. Its verdict is one '
    'of three: - `PASS`: both parts ran to completion and found no CRITICAL or HIGH issue; '
    '- `FAIL`: a part found a CRITICAL or HIGH issue, whether or not the other part '
    'completed; - `INCOMPLETE`: a part did not run to completion, and neither part found a '
    'CRITICAL or HIGH issue. When either part does not run to completion, the audit is '
    'never `PASS`, and the report names that part. The causes include a refused tool, a '
    'stopped turn, a missing environment and a scan with `scan_status: NOT_RUN`. An auditor '
    'whose turn stops returns no report, so the orchestrator records the audit as '
    '`INCOMPLETE` itself. 1. **Re-run once.** The orchestrator re-runs that part once, in a '
    "fresh agent or session, on the round's frozen tree. A fix round does not reset the "
    'count: each part gets one re-run in a run. 2. **Then the operator decides.** If the '
    're-run does not complete either, the operator chooses in their own message, and the '
    'record quotes it. The choices are to ship the control with the gap recorded, to defer '
    'it to a work-item, or to remove it. 3. **No unverified security claim.** A security '
    'control whose bypass hunt never finished does not ship as protection. Its changelog '
    'and documents say it is unverified, or it moves to a work-item. 4. **Tests are not the '
    'hunt.** Tests and a mutation run with a passing baseline show that the tests pin the '
    "specification. They do not show that the specification closes the threat. (TASK 111's "
    'retro wrote this rule. The bypass hunt on its anchor hook had stopped, and the '
    'operator had deferred the hook to a work-item.)'
)
#: Each router's pointers, as the whole block that holds each: a paragraph, a list item or a
#: table row. A sentence appended inside the block changes it (TASK 112 R6.3).
POINTERS = {
    WRAPPER: (
        """- **An unfinished part makes the audit `INCOMPLETE`.** A part is the scan or the
        adversarial review. When a part found a CRITICAL or HIGH issue, the audit is `FAIL`. Name
        the unfinished part. The orchestrator re-runs it once, then the operator decides
        (`security-audit` §6.2).""",
        """- **`scan_status` is a required field and it is not decoration.** `NOT_RUN` forces
        `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or HIGH
        issue — never `PASS`. Without that, a scan-less audit reported the same machine-readable
        verdict as a clean one, and every consumer that gates on the footer (`full-robust` §3,
        `security-audit.md` step 4) treated "we did not look" as "we looked and it was fine".
        Reporting the gap in prose while the footer says `PASS` is the fabrication this replaced,
        one layer down.""",
    ),
    "System/Agents/10_security_auditor.md": (
        """5. **Unfinished parts:** a scan or an adversarial review that did not run to completion
        makes the audit `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue, and the
        summary names it (`security-audit` §6.2).""",
        """- `scan_status` is `"clean" | "findings" | "NOT_RUN"` and is **required**. `"NOT_RUN"`
        forces `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or
        HIGH issue — never `"PASS"`. Without it a scan-less audit is machine- indistinguishable
        from a clean one, and every consumer that branches on this footer treats "we did not look"
        as "we looked and it was fine".""",
    ),
    ".agent/workflows/security-audit.md": (
        """- A review that does not run to completion makes the audit `INCOMPLETE`, or `FAIL` when a
        part found a CRITICAL or HIGH issue: name the part. The orchestrator re-runs it once, then
        the operator decides (`security-audit` §6.2).""",
        """- **If you cannot execute it** (no execution tool in your role, or the environment
        refuses): record `scan_status: NOT_RUN (<reason>)`, continue to step 3, and carry that
        status into the report. **Never invent the output** (`security-audit` §1). `NOT_RUN` makes
        the audit `INCOMPLETE`, or `FAIL` when step 3 finds a CRITICAL or HIGH issue, never `PASS`
        — step 4's "until clean" loop cannot be satisfied by a scan that never ran.""",
        """- If findings exist: a. Fix implementation (apply patches, rotate secrets). b. Add
        regression tests (security-focused). <!-- loop:audit-remediation --> c. Re-run audit
        script until clean. **Bound: max 3 iterations** when this workflow is entered directly; a
        caller may re-scope both the cap and the definition of "clean" (`full-robust` §3 does
        exactly that). On exhaustion with findings still open → **STOP** and escalate the open
        findings to the user. Per step 2, a `scan_status: NOT_RUN` never satisfies this loop: the
        verdict is `INCOMPLETE` or `FAIL`, not clean, and `security-audit` §6.2 governs its one
        re-run.""",
    ),
    ".agent/workflows/full-robust.md": (
        """- **Gate:** the audit footer reads `audit_status: PASS`, the automated scan ran to
        completion (`scan_status` is `clean` or `findings`), AND the manual review (per the
        `security-audit` skill §3 checklists) emits a severity-labelled findings table with **no
        CRITICAL/HIGH findings**. The table rules on each CRITICAL or HIGH hit of the scan: a
        confirmed hit is a finding, and a rejected one is listed as a false positive. An
        `INCOMPLETE` audit never meets it.""",
        """- **A scan that did not run is not a scan that passed.** `scan_status: NOT_RUN`
        (equivalently a `scan: NOT RUN (<reason>)` line) fails the scan conjunct: the gate is **not
        met** and the verdict is `INCOMPLETE`, or `FAIL` when the manual review found a CRITICAL or
        HIGH issue. The missing part is re-run once; if it still does not complete, the reason is
        escalated to the user (`security-audit` §6.2). Left unstated, `NOT RUN` is neither clean
        nor unclean and the undefined branch resolves in practice to "the other conjunct
        passed".""",
    ),
    "System/Docs/SKILLS.md": (
        """| **`security-audit`** | Vulnerability assessment v3.12 (two-layer model: deterministic
        regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping
        table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance,
        auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity
        reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC
        (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool
        integrations (incl. `snyk-agent-scan`), a status for each external tool and exit 3 for a
        scan part that did not run, private disclosure of a dependency finding (§6.1), an
        unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH
        issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |""",
    ),
    "System/Docs/WORKFLOWS.md": (
        """| **Security Audit** | Runs the security auditor agent. Remediation loop bounded at **max
        3 iterations** when invoked directly; `full-robust` §3 re-scopes both the cap and the
        definition of "clean". A `scan_status: NOT_RUN` yields `INCOMPLETE`, or `FAIL` when the
        manual review found a CRITICAL or HIGH issue, never clean (`security-audit` §6.2). | `run
        security-audit` |""",
    ),
}

#: TC-3b (TASK 118 R5.5): each router that reads the scanner states how its exit code and summary
#: set `scan_status`, in a block outside the blocks of `POINTERS`.
SCAN_STATUS_POINTERS = {
    WRAPPER: (
        """- **The scanner's exit code and summary set the floor of `scan_status`.** Exit 3, or a
        `summary.not_run` list that is not empty, means a part of the scan did not run:
        `scan_status: "NOT_RUN"`. A `summary.tool_exits` list that is not empty means an external
        tool reported a finding or failed: `scan_status` is at least `"findings"`, and
        `"NOT_RUN"` when the tool's output shows an error (`security-audit` §2). A run that prints
        no report, such as exit 1 with a JSON `error` or exit 2, is `"NOT_RUN"`.""",
    ),
    "System/Agents/10_security_auditor.md": (
        """- The scanner sets the floor of `scan_status`. Exit 3, or a `summary.not_run` list that
        is not empty, gives `"NOT_RUN"`. A `summary.tool_exits` list that is not empty gives at
        least `"findings"`, and `"NOT_RUN"` when the tool's output shows an error
        (`security-audit` §2). A run that prints no report, such as exit 1 with a JSON `error` or
        exit 2, gives `"NOT_RUN"`.""",
    ),
    ".agent/workflows/security-audit.md": (
        """- **A partial scan is `NOT_RUN`.** Exit 3, or a `summary.not_run` list that is not
        empty, records `scan_status: NOT_RUN (<the parts it names>)`. A `summary.tool_exits` list
        that is not empty records at least `scan_status: findings`, and `scan_status: NOT_RUN`
        when the tool's output shows an error (`security-audit` §2). A run that prints no report,
        such as exit 1 with a JSON `error` or exit 2, records `scan_status: NOT_RUN`.""",
    ),
}


def _read(rel):
    path = PROJECT_ROOT / rel
    if not path.is_file():
        raise AssertionError(f"{rel}: the file is missing")
    return path.read_text(encoding="utf-8")


def _section(text, heading):
    m = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.M)
    if not m:
        raise AssertionError(f"heading {heading!r} is missing")
    level = len(m.group(1))
    end = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, m.end())
    return text[m.end():end.start() if end else len(text)]


def _step(section, number):
    """The text of a top-level numbered step, up to the next one."""
    m = re.search(rf"^{number}\. .*?(?=^\d+\. |\Z)", section, re.M | re.S)
    if not m:
        raise AssertionError(f"step {number} is missing")
    return m.group(0)


def _step_to_end(section, number):
    """The text of a top-level numbered step, up to the end of the section (TASK 112 R6.3)."""
    m = re.search(rf"^{number}\. ", section, re.M)
    if not m:
        raise AssertionError(f"step {number} is missing")
    return section[m.start():]


def _blocks(text):
    """Each paragraph, list item and table row of `text`, whitespace collapsed."""
    item = re.compile(r"^\s*(?:[-*+]|\d+\.)\s|^\s*\|")
    blocks, current = [], []
    for line in text.splitlines():
        if not line.strip() or (item.match(line) and current):
            if current:
                blocks.append(_flat(" ".join(current)))
            current = [line] if line.strip() else []
            continue
        current.append(line)
    if current:
        blocks.append(_flat(" ".join(current)))
    return blocks


class TestHookRegistration(unittest.TestCase):
    """TC-1: a hook or a permission rule takes effect at once."""

    maxDiff = None

    def setUp(self):
        self.section = _section(_read(WORKFLOW), "3. Execution (Atomic Updates)")

    def test_step_4_is_the_reviewed_text_to_the_end_of_section_3(self):
        self.assertEqual(_flat(_step_to_end(self.section, 4)), STEP_4)

    def test_base_check_allows_the_fixture(self):
        self.assertIn("A test fixture that the test itself creates in a temporary directory and "
                      "removes is no such copy (step 4).", _flat(_step(self.section, 1)))


class TestIncompleteReview(unittest.TestCase):
    """TC-2: a review that cannot finish."""

    maxDiff = None

    def test_section_6_2_is_the_reviewed_text(self):
        self.assertEqual(_flat(_section(_read(SKILL), "6.2 A review that cannot finish")),
                         SECTION_6_2)


class TestPointers(unittest.TestCase):
    """TC-3: every place that routes an audit states the rule, in a block of its own."""

    maxDiff = None

    def test_each_router_states_the_rule_whole(self):
        for rel, expected in POINTERS.items():
            blocks = _blocks(_read(rel))
            for block in expected:
                block = _flat(block)
                with self.subTest(file=rel, block=block[:50]):
                    self.assertIn(block, blocks)

    def test_each_router_maps_the_scanner_status(self):
        """TC-3b (TASK 118 R5.5)."""
        for rel, expected in SCAN_STATUS_POINTERS.items():
            blocks = _blocks(_read(rel))
            for block in expected:
                block = _flat(block)
                with self.subTest(file=rel, block=block[:50]):
                    self.assertIn(block, blocks)

    def test_blocks_split_at_items_rows_and_blank_lines(self):
        text = "- one\n  two\n- three\n\npara\nline\n| a | b |\n| c | d |\n"
        self.assertEqual(_blocks(text), ["- one two", "- three", "para line", "| a | b |",
                                         "| c | d |"])


if __name__ == "__main__":
    unittest.main()
