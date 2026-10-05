"""Disclosure rule contract test (TASK 110, R11.2).

TASK 110 found a vulnerability with no public advisory in a dependency and drafted the report,
root cause and reproduction included, inside this public repository. The security review caught
the draft before a commit. This file pins the rule that keeps the detail out:

* `security-audit` §6.1 defines a dependency finding, states five steps, and names the four duties
  of an audit that give way to it (``TC-01``);
* `core-principles`, which every role loads at session start, points to §6.1, so the rule reaches
  a role that never loads `security-audit` (``TC-02``);
* the places that write a finding down point to §6.1: step 4 of the `security-audit` workflow,
  Step 3 of the auditor prompt, the filing rules of `run-feedback` and the output routing of
  `vdd-multi` (``TC-03``);
* the documents that quote the skill's version quote the front matter (``TC-04``);
* two paragraphs that already hold public detail of the TASK 110 finding are not extended, and
  the records of that finding point to the rule (``TC-05``). Headings and single lines hold such
  detail too; the audit of TASK 110 lists them, and these pins do not cover them.
"""
import hashlib
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL = ".agent/skills/security-audit/SKILL.md"
CORE = ".agent/skills/core-principles/SKILL.md"
WORKFLOW = ".agent/workflows/security-audit.md"
AUDITOR = "System/Agents/10_security_auditor.md"
RUN_FEEDBACK = ".agent/skills/run-feedback/SKILL.md"
POINTER = "`security-audit` §6.1"


def _read(rel):
    path = PROJECT_ROOT / rel
    if not path.is_file():
        raise AssertionError(f"{rel}: the file is missing")
    return path.read_text(encoding="utf-8")


def _flat(text):
    return " ".join(text.split())


def _section(text, heading):
    """The body under `heading` up to the next heading of the same or a higher level."""
    m = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.M)
    if not m:
        raise AssertionError(f"heading {heading!r} is missing")
    level = len(m.group(1))
    end = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, m.end())
    return text[m.end():end.start() if end else len(text)]


def _paragraph(text, start):
    """The paragraph that begins with `start`, whitespace collapsed."""
    i = text.find(start)
    if i == -1:
        raise AssertionError(f"no paragraph starts with {start!r}")
    j = text.find("\n\n", i)
    return _flat(text[i:j if j != -1 else len(text)])


class TestSkillRule(unittest.TestCase):
    """TC-01: §6.1 defines the term, states each step, and names what gives way."""

    def setUp(self):
        self.body = _flat(_section(_read(SKILL), "6.1 A finding in a dependency"))

    def test_the_term_covers_only_an_unpublished_vulnerability(self):
        self.assertIn("A **dependency finding** is a vulnerability that no public advisory "
                      "describes yet, in code the project uses but does not maintain", self.body)
        self.assertIn("A vulnerability with a public advisory is cited by its advisory identifier "
                      "(CVE or GHSA)", self.body)
        self.assertIn("Until a public advisory describes it:", self.body)

    def test_each_step_is_stated(self):
        for step in ("**Report it privately.**",
                     "**Keep the detail out of everything published with the repository**",
                     "**Hand the report to the operator.**", "**Record the status.**",
                     "**After the advisory**"):
            with self.subTest(step=step):
                self.assertIn(step, self.body)

    def test_a_record_states_only_the_status_level(self):
        self.assertIn("A record states only the dependency, the affected versions, a severity, "
                      "this project's mitigation and the status of the report; nothing on how the "
                      "defect works or what reaches it", self.body)

    def test_only_the_operator_sends(self):
        self.assertIn("An agent posts to an external service only when the operator asks for it in "
                      "their own message", self.body)

    def test_the_duties_that_give_way_are_named(self):
        for duty in ("a test pins this project's mitigation and never exercises the dependency's "
                     "defect",
                     "a patch to a vendored copy waits for the advisory",
                     "the exploit scenario a review role writes goes into the operator's draft, "
                     "not into the record",
                     "the CWE identifier that §6 asks for waits for the advisory",
                     "the finding is filed as a work-item, not as a defect"):
            with self.subTest(duty=duty):
                self.assertIn(duty, self.body)

    def test_public_detail_is_not_extended(self):
        self.assertIn("Detail that was public before a finding came under this rule is not repeated "
                      "or extended", self.body)

    def test_a_private_repository_is_no_exception(self):
        self.assertIn("The rule holds for a private repository too", self.body)


class TestPointers(unittest.TestCase):
    """TC-02 and TC-03: the rule is reachable from every role and from each place that writes."""

    def test_core_principles_holds_the_rule_in_its_own_section(self):
        body = _section(_read(CORE), "5. Disclosure")
        line = next((ln for ln in body.splitlines()
                     if ln.startswith("- **Dependency Vulnerabilities:**")), None)
        self.assertIsNotNone(line, "core-principles §5 has no Dependency Vulnerabilities line")
        self.assertIn(POINTER, line)
        self.assertIn("no file in the repository", line)

    def test_the_workflow_covers_every_output_of_its_remediation_step(self):
        step = _read(WORKFLOW).split("4. **Remediation & Reporting**", 1)[1].split("\n5. ", 1)[0]
        line = next((ln for ln in step.splitlines() if POINTER in ln), "")
        for output in ("the patches of 4a", "the tests of 4b", "the saved report",
                       "the `.AGENTS.md` notes", "the retro records"):
            with self.subTest(output=output):
                self.assertIn(output.lower(), line.lower())

    def test_the_auditor_reports_a_dependency_finding_by_the_rule(self):
        step = _section(_read(AUDITOR), "Step 3: Reporting")
        self.assertIn(POINTER, step)

    def test_run_feedback_files_it_as_a_work_item(self):
        flat = _flat(_read(RUN_FEEDBACK))
        self.assertIn("**A vulnerability with no public advisory in a dependency** is filed as a "
                      "work-item that holds only what `security-audit` §6.1 step 2 lists", flat)
        self.assertIn(f"reproduction ({POINTER})", flat)

    def test_vdd_multi_keeps_the_exploit_scenario_out_of_its_report(self):
        flat = _flat(_read(".agent/workflows/vdd-multi.md"))
        self.assertIn("a dependency finding of `security-audit` §6.1 enters the report with its "
                      "severity and the dependency's status only", flat)


class TestVersionMirrors(unittest.TestCase):
    """TC-04: `SKILLS.md` showed v3.7 for a skill at 3.8 before TASK 110."""

    def test_each_mirror_quotes_the_front_matter(self):
        version = re.search(r"^version: (\S+)$", _read(SKILL), re.M).group(1)
        for rel, quote in ((SKILL, f"# Security Audit v{version}\n"),
                           ("System/Docs/SKILLS.md", f"Vulnerability assessment v{version} "),
                           ("System/Docs/VDD.md", f"`security-audit` skill (v{version})")):
            with self.subTest(file=rel):
                self.assertIn(quote, _read(rel))


#: sha256 of each paragraph, whitespace collapsed, as at the base revision 6ae772b. The paragraphs
#: describe the TASK 110 finding as the public repository held it before §6.1. A failure here
#: means the paragraph changed: confirm that it adds no detail (§6.1), then update the digest.
#: Drop both pins once a public advisory describes the finding.
PUBLIC_PARAGRAPHS = {
    (".agent/skills/mermaid-authoring-guidelines/references/renderer-facts.md",
     "**Observed.** The request filter of mermaid-cli"):
        "38c92dc6dbdf07f8a89b43e913fce599415e53335dc8fec64dd1d8e4a60c1d37",
    ("docs/backlog/wi-30-renderer-supply-chain-v10-lockfile-mermaid-cli-request-filter-browser-"
     "hash.md", "**Signal.** Three renderer supply-chain items"):
        "67486b36c9a22d06e6bd26bbbb5070648799ec33008a9e7275dfbcb0af049fed",
}


class TestPublicDetail(unittest.TestCase):
    """TC-05: detail that was public before the rule is not extended."""

    def test_each_paragraph_is_as_at_the_base(self):
        for (rel, start), digest in PUBLIC_PARAGRAPHS.items():
            with self.subTest(file=rel):
                got = hashlib.sha256(_paragraph(_read(rel), start).encode("utf-8")).hexdigest()
                self.assertEqual(got, digest)

    def test_the_records_of_the_finding_point_to_the_rule(self):
        rf21, wi30 = (rel for rel, _start in PUBLIC_PARAGRAPHS)
        self.assertIn(f"until a public advisory describes it ({POINTER})",
                      _paragraph(_read(rf21), "**Rule.** Render a figure"))
        self.assertIn("the private report is sent and its channel and date are recorded here",
                      _paragraph(_read(wi30), "**Acceptance.**"))


if __name__ == "__main__":
    unittest.main()
