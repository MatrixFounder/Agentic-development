"""Two rules from the TASK 111 retro (R7).

TASK 111 registered a PreToolUse hook in this repository while building it; the hook then asked
for approval on the orchestrator's and the reviewers' own commands in Auto mode. Its bypass hunt
stopped, and the operator deferred the hook to WI-34. This file pins the rules whole:

* `framework-upgrade` §3 step 4, whole: what takes effect at once, the four stages, the failure
  branch; and §3.1's fixture exception (``TC-1``);
* `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
  no unverified control, tests are not the hunt (``TC-2``);
* the wrapper's bullet and the sentences of the five other places that route an audit, and
  `full-robust` §3's gate on `audit_status: PASS` (``TC-3``).

A change to a pinned rule changes this file in the same edit, where a review sees both.
"""
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ".agent/workflows/framework-upgrade.md"
SKILL = ".agent/skills/security-audit/SKILL.md"
WRAPPER = ".claude/agents/security-auditor.md"

STEP_4 = (
    '4. **Hooks and permission rules take effect at once.** Claude Code applies a settings '
    "file to the running session as soon as it changes, the reviewers' commands included. "
    'The step covers every change that alters what runs, or what runs without a prompt. The '
    'list is not exhaustive: - a hook in a settings file, or in the frontmatter of an agent '
    'or a skill; - the script of a registered hook, or code that script calls; - a '
    "permission rule, `additionalDirectories` or the permission mode, an agent's "
    '`permissionMode` and the `allowed-tools` of a skill or a command among them; - a '
    "settings key that names a command, such as `statusLine`, or sets a command's "
    'environment, `env`; - the MCP servers of `.mcp.json` or a settings file, and '
    '`enableAllProjectMcpServers`. A change that only narrows what runs without a prompt, '
    'such as a removed allow rule, may land at once: it runs nothing new, and at worst a '
    'command asks. Before the edit, a check shows that it narrows, and the audit records '
    "the check's output: - a base entry of the same list covers each new allow rule, "
    '`additionalDirectories` entry and `allowed-tools` entry; - each base deny or ask rule '
    'and `disallowedTools` entry is still present, or a new entry of the same list covers '
    "it; - every other key equals the base's; - no file that a registered hook, a "
    '`statusLine` command or an MCP server runs changes. The run registers nothing in '
    "`.claude/settings.local.json` or the user's settings; an edit there waits for the "
    "operator's commit and their go-ahead. Every other change runs in four stages. 1. "
    '**Fixture.** The TASK states the exact registration: the event, matcher and command of '
    "a hook, or the text of a rule or key. A hook's test builds a temporary root with its "
    'own `.claude/settings.json` holding that registration, and removes it. Code that a '
    'registered hook runs is edited under a new name. 2. **Reviews.** The code review and '
    'the security audit check the code and the registration. Both must pass. An '
    '`INCOMPLETE` audit blocks the registration until the operator decides under '
    '`security-audit` §6.2. 3. **Registration.** After §4.5, the last edit of the change '
    'copies the registration verbatim into its file, or the new code over the code it '
    "replaces, and removes the copy under the new name. Only the retro's records follow "
    'this edit. The same edit adds a settings test that pins the registration, and the '
    'gates run again. 4. **Focused review.** A code reviewer and a security auditor check '
    'the registration diff on the new fingerprint. **Failure.** If the gates of stage 3 '
    'fail, or the focused review does not pass, the run restores the registered files at '
    "once to their text before stage 3's edit. The restore brings back the copy under the "
    'new name, if there is one, and the audit records the stage-3 diff. - After an '
    '`INCOMPLETE` audit, `security-audit` §6.2 governs the re-run, which reads that '
    'recorded diff. If the re-run passes, stage 3 applies the same diff again, and stage 4 '
    'checks it on the new fingerprint. - After a failed gate, a rejected code review or a '
    '`FAIL`, the operator decides what follows. A registration, or the code it runs, whose '
    'text changes returns to stage 1. **Why.** TASK 111 registered a PreToolUse hook while '
    "building it, and the hook asked for approval on the orchestrator's and the reviewers' "
    'own commands in Auto mode.'
)
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
POINTERS = {
    WRAPPER: (
        "**A part that does not run to completion makes the audit `INCOMPLETE`**, whether the scan "
        "or the adversarial review, or `FAIL` when a part found a CRITICAL or HIGH issue: name the "
        "part. The orchestrator re-runs it once, then the operator decides (`security-audit` §6.2).",
        "`NOT_RUN` forces `audit_status: \"INCOMPLETE\"`, or `\"FAIL\"` when the manual review found "
        "a CRITICAL or HIGH issue — never `PASS`.",
    ),
    "System/Agents/10_security_auditor.md": (
        "5. **Unfinished parts:** a scan or an adversarial review that did not run to completion "
        "makes the audit `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue, and the "
        "summary names it (`security-audit` §6.2).",
        "`\"NOT_RUN\"` forces `audit_status: \"INCOMPLETE\"`, or `\"FAIL\"` when the manual review "
        "found a CRITICAL or HIGH issue — never `\"PASS\"`.",
    ),
    ".agent/workflows/security-audit.md": (
        "- A review that does not run to completion makes the audit `INCOMPLETE`, or `FAIL` when a "
        "part found a CRITICAL or HIGH issue: name the part. The orchestrator re-runs it once, then "
        "the operator decides (`security-audit` §6.2).",
        "`NOT_RUN` makes the audit `INCOMPLETE`, or `FAIL` when step 3 finds a CRITICAL or HIGH "
        "issue, never `PASS`",
        "the verdict is `INCOMPLETE` or `FAIL`, not clean, and `security-audit` §6.2 governs its one "
        "re-run.",
    ),
    ".agent/workflows/full-robust.md": (
        "**Gate:** the audit footer reads `audit_status: PASS`, the automated scan exits clean, AND "
        "the manual review",
        "An `INCOMPLETE` audit never meets it.",
        "the gate is **not met** and the verdict is `INCOMPLETE`, or `FAIL` when the manual review "
        "found a CRITICAL or HIGH issue. The missing part is re-run once; if it still does not "
        "complete, the reason is escalated to the user (`security-audit` §6.2).",
    ),
    "System/Docs/SKILLS.md": (
        "private disclosure of a dependency finding (§6.1), an unfinished review reported as "
        "`INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue (§6.2).",
    ),
    "System/Docs/WORKFLOWS.md": (
        "A `scan_status: NOT_RUN` yields `INCOMPLETE`, or `FAIL` when the manual review found a "
        "CRITICAL or HIGH issue, never clean (`security-audit` §6.2).",
    ),
}


def _read(rel):
    path = PROJECT_ROOT / rel
    if not path.is_file():
        raise AssertionError(f"{rel}: the file is missing")
    return path.read_text(encoding="utf-8")


def _flat(text):
    return " ".join(text.split())


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


class TestHookRegistration(unittest.TestCase):
    """TC-1: a hook or a permission rule takes effect at once."""

    maxDiff = None

    def setUp(self):
        self.section = _section(_read(WORKFLOW), "3. Execution (Atomic Updates)")

    def test_step_4_is_the_reviewed_text(self):
        self.assertEqual(_flat(_step(self.section, 4)), STEP_4)

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
    """TC-3: every place that routes an audit states the rule."""

    def test_each_router_states_the_rule(self):
        for rel, sentences in POINTERS.items():
            text = _flat(_read(rel))
            for sentence in sentences:
                with self.subTest(file=rel, sentence=sentence[:40]):
                    self.assertIn(sentence, text)


if __name__ == "__main__":
    unittest.main()
