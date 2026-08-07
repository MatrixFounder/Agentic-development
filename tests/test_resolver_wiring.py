"""Wiring test for the positional-reference resolver (TASK 104).

WI-16 §7 states, of its own nine wired workflows: "Nothing verifies the wiring." A workflow
authored later is absent from the set and nothing reports it. This file closes that gap for
this one protocol.

**What makes it a verification rather than a restatement is exhaustiveness.** Only half the
selection criterion is machine-derivable: the delegation half comes out of ``calls:``
frontmatter exactly, while "code lands here" does not — measured over all 23 workflows, a grep
for commit or staging steps finds them in two. So the test enumerates the workflow directory
**from disk** and asserts every file is in exactly one of two sets, one of which carries a
reason per member. A workflow added tomorrow is in neither and fails here.
"""

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
WORKFLOWS = PROJECT_ROOT / ".agent/workflows"
SKILLS = PROJECT_ROOT / ".agent/skills"
RESOLVER = "check_positional_refs.py"

#: Workflows running the resolver themselves: code lands in their own steps and no `calls:`
#: edge hands that code to a workflow already covered.
WIRED = {
    "vdd-03-develop",
    "vdd-05-run-full-task",
    "vdd-multi",
    "vdd-adversarial",
    "security-audit",
    "framework-upgrade",
    "heal-issues",
}

#: Every other workflow, with the reason it runs no resolver step. A reason is required: an
#: exclusion nobody can read is how a set rots.
EXCLUDED = {
    # Covered by `code-review-checklist` — these invoke 09_code_reviewer_prompt, so a step
    # here would run the resolver twice on the same change.
    "03-develop-single-task": "code-reviewer",
    "light-02-develop-task": "code-reviewer",
    # Orchestrators: they hand the code to a covered workflow. Asserted, not believed.
    "05-run-full-task": "delegates",
    "base-stub-first": "delegates",
    "full-robust": "delegates",
    "vdd-enhanced": "delegates",
    "light-01-start-feature": "delegates",
    # Authoring-only: no code lands, and the artifact passes a reviewer whose checklist
    # carries the References section.
    "01-start-feature": "authoring",
    "02-plan-implementation": "authoring",
    "04-update-docs": "authoring",
    "iterative-design": "authoring",
    "vdd-01-start-feature": "authoring",
    "vdd-02-plan": "authoring",
    # Measured at zero: docs/product/ holds no path:line reference in onchain-analytics,
    # obsidian-llm-wiki or Universal-skills.
    "product-full-discovery": "product",
    "product-market-only": "product",
    "product-quick-vision": "product",
}

CHECKLISTS = (
    "task-review-checklist",
    "plan-review-checklist",
    "architecture-review-checklist",
    "code-review-checklist",
)

#: The two tokens the checklist section is asserted on. Named rather than approximated: this
#: assertion is the blast-radius mitigation for five consumer repositories reached by symlink.
#: A loose substring would pass on a checklist saying the opposite; a whole-sentence match
#: would break on a harmless rewording, after which someone relaxes it and the guarantee is
#: gone. A heading plus a short marker phrase is stable under rewording and specific enough
#: to be wrong loudly.
REFERENCES_HEADING = re.compile(r"^## \d+\. References", re.MULTILINE)
NOT_A_DEFECT = "not a defect"

CALLS_BLOCK = re.compile(r"^  calls:\s*$(.*?)^---$", re.MULTILINE | re.DOTALL)
INVOKE_EDGE = re.compile(r"-\s+workflow:\s*(?P<name>[\w-]+)\s*\n\s+kind:\s*invoke")


def workflow_names():
    """Return every workflow name on disk. The set is read, never declared."""
    return {p.stem for p in WORKFLOWS.glob("*.md")}


def text_of(name):
    return (WORKFLOWS / f"{name}.md").read_text(encoding="utf-8")


def invoke_targets(name):
    """Return the workflows ``name`` invokes, from its `calls:` frontmatter."""
    block = CALLS_BLOCK.search(text_of(name))
    if not block:
        return set()
    return {m.group("name") for m in INVOKE_EDGE.finditer(block.group(1))}


class TestSetIsExhaustive(unittest.TestCase):
    """The assertion that survives a workflow being added. Everything else re-states a decision."""

    def test_every_workflow_is_wired_or_excluded_with_a_reason(self):
        on_disk = workflow_names()
        classified = WIRED | set(EXCLUDED)
        unclassified = on_disk - classified
        self.assertEqual(
            unclassified,
            set(),
            "workflow(s) in neither set — decide whether the resolver runs there, and record "
            f"the reason if it does not: {sorted(unclassified)}",
        )

    def test_no_set_member_is_missing_from_disk(self):
        """A renamed or deleted workflow leaves a stale member that would silently pass."""
        stale = (WIRED | set(EXCLUDED)) - workflow_names()
        self.assertEqual(stale, set(), f"named but absent from disk: {sorted(stale)}")

    def test_the_two_sets_are_disjoint(self):
        self.assertEqual(WIRED & set(EXCLUDED), set())


class TestDelegationIsChecked(unittest.TestCase):
    """An exclusion claiming delegation is verified against `calls:`, not taken on trust."""

    def _covered(self):
        """WIRED plus the workflows a reviewer's checklist covers directly."""
        return WIRED | {n for n, why in EXCLUDED.items() if why == "code-reviewer"}

    def test_every_delegating_workflow_reaches_a_covered_one(self):
        covered = self._covered()
        for name, why in sorted(EXCLUDED.items()):
            if why != "delegates":
                continue
            with self.subTest(workflow=name):
                seen, frontier = set(), list(invoke_targets(name))
                while frontier:
                    current = frontier.pop()
                    if current in covered:
                        break
                    if current in seen:
                        continue
                    seen.add(current)
                    frontier.extend(invoke_targets(current))
                else:
                    self.fail(
                        f"{name} is excluded as delegating, but no invoke edge reaches a "
                        f"covered workflow (transitively). Reached: {sorted(seen)}"
                    )


class TestWiredWorkflowsRunIt(unittest.TestCase):
    def test_each_wired_workflow_names_the_resolver(self):
        for name in sorted(WIRED):
            with self.subTest(workflow=name):
                self.assertIn(RESOLVER, text_of(name))


class TestExcludedWorkflowsDoNot(unittest.TestCase):
    """Written as a prohibition over a named set: an absence is not otherwise checkable."""

    def test_no_excluded_workflow_names_the_resolver(self):
        for name in sorted(EXCLUDED):
            with self.subTest(workflow=name):
                self.assertNotIn(
                    RESOLVER,
                    text_of(name),
                    f"{name} is excluded as '{EXCLUDED[name]}' — a step here double-runs it",
                )


class TestChecklistsCarryTheSection(unittest.TestCase):
    """T2's whole coverage, and the one item that keeps this task from being a migration demand."""

    def _skill(self, name):
        return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

    def test_each_checklist_names_the_resolver(self):
        for name in CHECKLISTS:
            with self.subTest(checklist=name):
                self.assertIn(RESOLVER, self._skill(name))

    def test_each_checklist_has_a_references_section(self):
        for name in CHECKLISTS:
            with self.subTest(checklist=name):
                self.assertRegex(self._skill(name), REFERENCES_HEADING)

    def test_each_checklist_states_that_a_bare_coordinate_is_not_a_defect(self):
        """The command WITHOUT this clause is a fleet-wide migration demand: the four
        checklists are live in five consumer repositories by symlink at commit time, and a
        reviewer reading '348 without (not examined)' as a failure will demand referents
        nobody asked for. 103-D1 forbids exactly that."""
        for name in CHECKLISTS:
            with self.subTest(checklist=name):
                self.assertIn(NOT_A_DEFECT, self._skill(name))


if __name__ == "__main__":
    unittest.main()
