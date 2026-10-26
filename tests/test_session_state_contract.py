"""The session-state rules stand where the agents read them (TASK 127 R4, R5, R7.5, R8.8).

TC-C1 to TC-C7 of TASK 127 §5 pin:

* the failure rule of R4.1 in the three bootstrap files, in `skill-session-state` §3, and in the
  guide's §1 and its Risk A (``TC-C1``);
* the disagreement step of R4.2 in the three bootstrap files, in the skill's §2, and in the
  guide's §1 and its Risk A (``TC-C2``);
* the skill names no tool of one vendor and no lock that the script does not take, and §3 keeps
  its paragraph for roles that cannot run a command (``TC-C3``);
* the skill's §1 states the file format, its §6 the lock, and its version is 1.2 (``TC-C4``);
* the guide names `current_task.status`, the three platforms, UTF-8 and the dropped key
  (``TC-C5``);
* the CI pytest step runs the skill's tests and this module (``TC-C6``);
* `docs/ARCHITECTURE.md` names `msvcrt` at both statements of the session-state lock
  (``TC-C7``).
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agent" / "skills" / "skill-session-state" / "SKILL.md"
GUIDE = ROOT / "System" / "Docs" / "SESSION_CONTEXT_GUIDE.md"
WORKFLOW = ROOT / ".github" / "workflows" / "framework-gates.yml"
ARCHITECTURE = ROOT / "docs" / "ARCHITECTURE.md"

#: The words that each copy of a rule carries.
FAILURE = ("If `update_state.py` exits non-zero", "the operator in the same reply", "by hand")
DISAGREE = ("Session state and docs/TASK.md disagree",)
#: The paths of R7.5 in the pytest step of the CI workflow.
CI_PATHS = (".agent/skills/skill-session-state/scripts/tests/",
            "tests/test_session_state_contract.py")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def heading_section(text, title):
    """The lines under the first heading that starts with `title`, up to the next heading of
    its level or a higher one."""
    match = re.search(r"^(#{1,6}) " + re.escape(title) + r".*$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"no heading {title!r}")
    rest = text[match.end():]
    end = re.search(r"^#{1,%d} " % len(match.group(1)), rest, re.MULTILINE)
    return rest[:end.start()] if end else rest


def between(text, start, stop):
    """The text from `start` to `stop`, both exact substrings."""
    first = text.index(start)
    return text[first:text.index(stop, first)]


class RulesTestCase(unittest.TestCase):
    def assert_holds(self, text, words, where):
        for word in words:
            self.assertTrue(word in text, f"{where}: {word!r} is missing")

    def test_c1_the_failure_rule(self):
        claude = read(ROOT / "CLAUDE.md")
        self.assert_holds(between(claude, "**ON PHASE BOUNDARY**", "\n## "), FAILURE,
                          "CLAUDE.md ON PHASE BOUNDARY")
        for name in ("AGENTS.md", "GEMINI.md"):
            self.assert_holds(heading_section(read(ROOT / name), "Session State Persistence"),
                              FAILURE, f"{name} Session State Persistence")
        self.assert_holds(heading_section(read(SKILL), "3. Update Protocol"), FAILURE,
                          "SKILL.md §3")
        guide = read(GUIDE)
        self.assert_holds(heading_section(guide, "1. How It Works"), FAILURE, "the guide's §1")
        self.assert_holds(heading_section(guide, "Risk A"), FAILURE, "the guide's Risk A")

    def test_c2_the_disagreement_step(self):
        claude = read(ROOT / "CLAUDE.md")
        self.assert_holds(between(claude, "**ON SESSION START**", "**ON PHASE BOUNDARY**"),
                          DISAGREE, "CLAUDE.md ON SESSION START")
        for name in ("AGENTS.md", "GEMINI.md"):
            self.assert_holds(heading_section(read(ROOT / name), "SESSION RESTORATION"),
                              DISAGREE, f"{name} SESSION RESTORATION")
        self.assert_holds(heading_section(read(SKILL), "2. Boot Protocol"), DISAGREE,
                          "SKILL.md §2")
        guide = read(GUIDE)
        self.assert_holds(heading_section(guide, "1. How It Works"), DISAGREE, "the guide's §1")
        self.assert_holds(heading_section(guide, "Risk A"), DISAGREE, "the guide's Risk A")

    def test_c3_the_skill_names_no_vendor_tool_and_no_other_lock(self):
        skill = read(SKILL)
        for word in ("task_boundary", "read_file", "view_file", "lockf", "Shared Lock"):
            self.assertFalse(word in skill, f"SKILL.md holds {word!r}")
        self.assert_holds(heading_section(skill, "3. Update Protocol"),
                          ("does not apply to you",), "SKILL.md §3")

    def test_c4_the_skill_states_the_format_and_the_lock(self):
        skill = read(SKILL)
        self.assertRegex(skill.split("---", 2)[1], r"(?m)^version: 1\.2$")
        self.assert_holds(heading_section(skill, "1. The Session File"),
                          ("`schema_version: 2`", "UTF-8", "drops a key"), "SKILL.md §1")
        self.assert_holds(heading_section(skill, "6. Shared State Protocol"),
                          ("`fcntl.flock`", "`msvcrt.locking`"), "SKILL.md §6")

    def test_c5_the_guide(self):
        guide = read(GUIDE)
        self.assert_holds(guide, ("current_task.status",), "the guide")
        self.assertFalse("task_status" in guide, "the guide holds 'task_status'")
        self.assert_holds(heading_section(guide, "5. Platform Memory Integration"),
                          ("macOS", "Linux", "Windows"), "the guide's §5")
        self.assert_holds(heading_section(guide, "6. Manual Override"),
                          ("UTF-8", "drops a key"), "the guide's §6")

    def test_c6_the_ci_pytest_step(self):
        workflow = read(WORKFLOW)
        step = between(workflow, "- name: Run tooling regression tests", "\n      - name:")
        self.assert_holds(step, CI_PATHS, "the pytest step of the CI workflow")

    def test_c7_the_architecture_names_both_locks(self):
        lines = read(ARCHITECTURE).splitlines()
        for marker in ("- **Shared State**:", "- **Session state**:"):
            hits = [line for line in lines if line.startswith(marker)]
            self.assertEqual(len(hits), 1, marker)
            self.assert_holds(hits[0], ("`fcntl`", "`msvcrt`"), f"ARCHITECTURE {marker}")


if __name__ == "__main__":
    unittest.main()
