"""Tests for `check_skill_refs.py` — every `skill-<name>` reference must resolve.

Most assertions drive `scan_text` with literals rather than this repository's content,
for the reason `test_positional_refs.py` builds a throwaway git repo: the content
changes every task, and a gate whose test depends on it fails for the wrong reasons.

Two assertions DO read the real tree, and they are the point of the file: the repository
is clean today (`test_repository_is_clean`), and the scan actually walked something
(`files_scanned`), so a run that matched nothing because it walked nothing cannot pass
for a clean run.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPT = PROJECT_ROOT / ".agent/skills/documentation-standards/scripts/check_skill_refs.py"

spec = importlib.util.spec_from_file_location("check_skill_refs", SCRIPT)
csr = importlib.util.module_from_spec(spec)
sys.modules["check_skill_refs"] = csr
spec.loader.exec_module(csr)

# A synthetic skill set: one skill whose real name carries the prefix, three that do not.
NAMES = {"skill-session-state", "core-principles", "plan-review-checklist", "light-mode"}


class TestDetects(unittest.TestCase):
    """The forms the rule is meant to catch."""

    def test_prefixed_reference_to_an_unprefixed_skill(self):
        findings = csr.scan_text("Apply `skill-core-principles` now.", NAMES)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].reference, "skill-core-principles")
        self.assertEqual(findings[0].correct, "core-principles")

    def test_bare_reference_without_backticks(self):
        """The role prompts write these both ways, so backticks must not be the key."""
        findings = csr.scan_text("- skill-plan-review-checklist (Your checklist)", NAMES)
        self.assertEqual(len(findings), 1)

    def test_reports_every_occurrence_with_its_line(self):
        text = "`skill-core-principles`\nfiller\n`skill-light-mode`"
        findings = csr.scan_text(text, NAMES, path="d.md")
        self.assertEqual([(f.line, f.correct) for f in findings],
                         [(1, "core-principles"), (3, "light-mode")])

    def test_message_names_the_correct_spelling(self):
        """A diagnostic that says only 'unresolvable' sends the reader to a 47-entry
        directory listing."""
        finding = csr.scan_text("`skill-light-mode`", NAMES, path="d.md")[0]
        self.assertIn("light-mode", finding.render())
        self.assertIn("d.md:1", finding.render())


class TestDoesNotFire(unittest.TestCase):
    """The forms that must stay silent — each one measured in the real repo."""

    def test_correctly_prefixed_skill(self):
        """`skill-session-state` IS the directory name. 176 such references exist."""
        self.assertEqual(csr.scan_text("`skill-session-state`", NAMES), [])

    def test_unprefixed_reference_is_already_correct(self):
        self.assertEqual(csr.scan_text("`core-principles`", NAMES), [])

    def test_reference_to_a_skill_that_exists_under_neither_spelling(self):
        """DECLARED LIMIT. `skill-drift-detection` is a ROADMAP proposal for a skill that
        does not exist yet; `skill-validate` is a CI job name; `skill-magic-wand` is a
        deliberately fictional skill inside an audit example. Six such references exist
        and all six are legitimate — firing on them would mean deciding which prose is a
        reference and which is a proposal, and a gate that fires on a ROADMAP entry gets
        muted."""
        text = "create `skill-drift-detection`, the `skill-validate` job, `skill-magic-wand`"
        self.assertEqual(csr.scan_text(text, NAMES), [])

    def test_longer_token_is_not_clipped_into_a_match(self):
        """`skill-core-principles-v2` names no skill; reporting it as `core-principles`
        would be inventing a correction."""
        self.assertEqual(csr.scan_text("`skill-core-principles-v2`", NAMES), [])


class TestRealRepository(unittest.TestCase):
    """The two assertions that read the tree."""

    def test_scan_walked_something(self):
        _, scanned = csr.scan_repo(PROJECT_ROOT)
        self.assertGreater(scanned, 20, "the scan matched no files — everything else is vacuous")

    def test_repository_is_clean(self):
        findings, _ = csr.scan_repo(PROJECT_ROOT)
        self.assertEqual(
            [f.render() for f in findings],
            [],
            "a role prompt declares an Active Skill whose name resolves to nothing; the "
            "role then loads nothing and says so only if it happens to notice",
        )

    def test_archived_material_is_out_of_scope(self):
        """Archived specs were correct when written and this framework does not retrofit
        them — the same reason `check_positional_refs.py` is diff-scoped."""
        for path in ("archives/x.md", "docs/tasks/task-001.md", "CHANGELOG.md",
                     "Backlog/archive/old.md"):
            self.assertRegex(path, csr._SKIP, f"{path} should be skipped")
        for path in ("System/Agents/03_task_reviewer_prompt.md", "CLAUDE.md"):
            self.assertNotRegex(path, csr._SKIP, f"{path} must be scanned")


if __name__ == "__main__":
    unittest.main()
