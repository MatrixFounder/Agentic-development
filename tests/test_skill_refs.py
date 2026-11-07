"""Tests for `check_skill_refs.py` — every `skill-<name>` reference must resolve.

Most assertions drive `scan_text` with literals rather than this repository's content,
for the reason `test_positional_refs.py` builds a throwaway git repo: the content
changes every task, and a gate whose test depends on it fails for the wrong reasons.

Two assertions DO read the real tree, and they are the point of the file: the repository
is clean today (`test_repository_is_clean`), and the scan actually walked something
(`files_scanned`), so a run that matched nothing because it walked nothing cannot pass
for a clean run.

`TestStandaloneBundle` (TASK 141) pins the other side of reference resolution: a skill in
`STANDALONE_SKILLS`, which `Universal-skills` publishes as a byte-identical copy, names nothing
that resolves only inside this framework. A standalone consumer of that copy has no framework to
resolve it in.
"""

import importlib.util
import re
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


#: Skills that `Universal-skills` publishes as byte-identical copies of canonical and that this
#: class holds to the standalone rule (TASK 141). `vdd-sarcastic` is published too, but it keeps
#: framework references (TASK 141, residual 1), so it is not listed here.
STANDALONE_SKILLS = ("vdd-adversarial",)

#: Backticked names a standalone bundle may cite: itself and its published sibling.
PUBLISHED_NAMES = {"vdd-adversarial", "vdd-sarcastic"}

#: Fixed framework-only forms: its paths and files, its agent wrappers, its audit IDs, its roles,
#: and the tool names of one vendor. Workflow commands and skill names are derived below.
FRAMEWORK_ONLY = re.compile(
    r"docs/(?:reviews|tasks|plans|issues|backlog)/|\bdocs/[A-Z_]+\.md\b|\.agent/|\.claude/agents/|"
    r"\bSystem/(?:Agents|Docs|scripts)/|\baudit-\d{3}\b|(?i:\borchestrators?\b|\bthe\s+brief\b)|"
    r"\bview_file\b|\blist_dir\b"
)

#: The one allowed URL: the A/B report at a fixed commit. It resolves anywhere and needs no upkeep.
ALLOWED_URL = re.compile(
    r"https://github\.com/MatrixFounder/Agentic-development/blob/[0-9a-f]{40}/[^)\s]+"
)

#: The slash commands of this framework, one per `.claude/commands/*.md`; derived, so a new
#: command needs no edit here.
COMMANDS = sorted(p.stem for p in (PROJECT_ROOT / ".claude/commands").glob("*.md"))
SLASH_COMMAND = re.compile(r"(?<![\w./])/(?:%s)\b" % "|".join(map(re.escape, COMMANDS)))

#: Backticked names that resolve only here: a framework skill or a command, minus PUBLISHED_NAMES.
FRAMEWORK_NAMES = (
    {p.name for p in (PROJECT_ROOT / ".agent/skills").iterdir() if p.is_dir()} | set(COMMANDS)
) - PUBLISHED_NAMES
BACKTICKED_NAME = re.compile(r"`([a-z0-9][a-z0-9-]*)`")


def framework_refs(text):
    """Each framework-only reference in ``text``.

    The allowed URL is removed first, and whitespace is collapsed, so a form wrapped across two
    lines is still found.
    """
    flat = " ".join(ALLOWED_URL.sub("<url>", text).split())
    found = [m.group(0) for m in FRAMEWORK_ONLY.finditer(flat)]
    found += [m.group(0) for m in SLASH_COMMAND.finditer(flat)]
    found += [m.group(0) for m in BACKTICKED_NAME.finditer(flat) if m.group(1) in FRAMEWORK_NAMES]
    return found


class TestStandaloneBundle(unittest.TestCase):
    """A published copy carries no reference a standalone consumer cannot resolve.

    Known limit: the forms are words, so ordinary prose that spells one ("the brief window")
    fails too. The author then rephrases; the test does not judge intent.
    """

    def _files(self, name):
        root = PROJECT_ROOT / ".agent/skills" / name
        return sorted(p for p in root.rglob("*") if p.is_file() and p.name != ".DS_Store")

    def test_bundle_walked_something(self):
        for name in STANDALONE_SKILLS:
            self.assertGreaterEqual(len(self._files(name)), 4, f"{name}: the walk found no bundle")
        self.assertIn("vdd-multi", COMMANDS, "the command list was derived from nothing")

    def test_bundle_names_no_framework_only_reference(self):
        found = []
        for name in STANDALONE_SKILLS:
            for path in self._files(name):
                for ref in framework_refs(path.read_text(encoding="utf-8")):
                    found.append(f"{path.relative_to(PROJECT_ROOT)}: {ref}")
        self.assertEqual(found, [], "a published copy names what only this framework resolves")

    def test_each_form_is_detected(self):
        """The mutation side: each alternative planted in a literal is reported."""
        for planted in ("see `docs/reviews/x.md`", "docs/tasks/task-1.md", "docs/plans/plan-1.md",
                        "docs/issues/arc-1.md", "docs/backlog/wi-1.md", "edit docs/TASK.md",
                        "docs/KNOWN_ISSUES.md", "read .agent/skills/x", ".claude/agents/critic-logic.md",
                        "System/Agents/a.md", "run /vdd-multi", "run /vdd-adversarial",
                        "the `vdd-multi` workflow", "per `skill-parallel-orchestration` §2.4",
                        "audit-067 C-02", "audit-112", "the Orchestrator supplies it",
                        "two orchestrators", "The brief names it", "the\nbrief", "the  brief",
                        "use `view_file`", "in `list_dir` output"):
            self.assertNotEqual(framework_refs(planted), [], planted)

    def test_only_the_pinned_url_is_allowed(self):
        pinned = ("[report](https://github.com/MatrixFounder/Agentic-development/blob/"
                  "1918af6795540c00cbe812ad4c57be5f85e6fa33/docs/reviews/ab-experiment-075.md)")
        self.assertEqual(framework_refs(pinned), [])
        moving = ("[report](https://github.com/MatrixFounder/Agentic-development/blob/main/"
                  "docs/reviews/ab-experiment-075.md)")
        self.assertEqual(framework_refs(moving), ["docs/reviews/"])

    def test_ordinary_words_pass(self):
        for text in ("multi-model orchestration", "an operating system", "a brief summary",
                     "IBM System/360", "src/develop.py", "and/or", "the `vdd-sarcastic` skill",
                     "the `vdd-adversarial` skill", "`prompt-first`", "`requires-python`"):
            self.assertEqual(framework_refs(text), [], text)

if __name__ == "__main__":
    unittest.main()
