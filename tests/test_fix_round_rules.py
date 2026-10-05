"""Fix-round rules contract test (TASK 110, WI-27).

TASK 108 checked each fix wave with a verifier that replayed the original failures, and the
verifiers still found 23, 17 and 17 new regressions in three successive waves. A fix to shared
parsing or measuring code moves verdicts on inputs its own test does not hold. This file pins:

* `developer-guidelines` §6.4 states the differential replay: a fix to code that an instrument
  applies to a stored corpus re-runs that instrument over the corpus before hand-off, and the
  hand-off lists every verdict that moved, or states "0 of N moved". The section defines its two
  terms and the case of a project with no stored corpus (``TC-01``);
* the same section states the closed list: from the second fix round of one review on, a fix
  edits only for the findings on that round's list (``TC-02``);
* `code-review-checklist` §4 checks both (``TC-03``).
"""
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUIDELINES = ".agent/skills/developer-guidelines/SKILL.md"
CHECKLIST = ".agent/skills/code-review-checklist/SKILL.md"


def _read(rel):
    path = PROJECT_ROOT / rel
    if not path.is_file():
        raise AssertionError(f"{rel}: the file is missing")
    return path.read_text(encoding="utf-8")


def _section(text, heading_pattern):
    """The body under the first heading that matches, up to the next heading of its level or a
    higher one; None when no heading matches."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and re.search(heading_pattern, m.group(2)):
            level = len(m.group(1))
            for j in range(i + 1, len(lines)):
                n = re.match(r"^(#{1,6})\s", lines[j])
                if n and len(n.group(1)) <= level:
                    return "\n".join(lines[i + 1:j])
            return "\n".join(lines[i + 1:])
    return None


def _flat(text):
    return " ".join(text.split()).casefold()


def _missing(needles, text):
    flat = _flat(text)
    return [n for n in needles if _flat(n) not in flat]


class TestFixRoundRules(unittest.TestCase):
    def setUp(self):
        self.rounds = _section(_read(GUIDELINES), r"^6\.4\b")
        self.assertIsNotNone(self.rounds, f"{GUIDELINES}: no section 6.4")

    def test_tc01_differential_replay(self):
        missing = _missing(("differential replay", "stored corpus", "instrument", "before hand-off",
                            "every verdict that moved", "0 of N moved", "no stored corpus"),
                           self.rounds)
        self.assertEqual(missing, [], f"{GUIDELINES} §6.4: missing {missing}")

    def test_tc01_terms_are_defined(self):
        for term in ("instrument", "stored corpus"):
            with self.subTest(term=term):
                self.assertRegex(_flat(self.rounds), re.escape(f"an {term} is")
                                 if term == "instrument" else re.escape(f"a {term} is"))

    def test_tc02_closed_list(self):
        missing = _missing(("closed list", "second fix round", "only for the findings on that "
                            "round's list"), self.rounds)
        self.assertEqual(missing, [], f"{GUIDELINES} §6.4: missing {missing}")

    def test_tc03_the_review_checks_both(self):
        testing = _section(_read(CHECKLIST), r"^4\.\s*Testing")
        self.assertIsNotNone(testing, f"{CHECKLIST}: no section 4")
        missing = _missing(("**Replay:**", "differential replay", "**Closed list:**",
                            "`developer-guidelines` §6.4"), testing)
        self.assertEqual(missing, [], f"{CHECKLIST} §4: missing {missing}")


if __name__ == "__main__":
    unittest.main()
