"""Scope contract for the positional-reference CI gate (documentation-standards §4.2).

§4.2 splits the resolver's verdict by corpus: a **named living corpus** is gateable, and
"everything else, archives included" stays advisory, because a coordinate in an archived
document is a true statement about a past state. The CI step predates that split and scanned
the whole tree, so CI ran red for six days on six references that are all correct — three
cross-repository coordinates no local file can satisfy, and three referents whose target was
edited after the review citing it was written.

**What makes this a verification rather than a restatement of the YAML is exhaustiveness.**
The living/archived boundary is not a list somebody keeps in their head: archiving MOVES a
document from the top level of ``docs/`` into a subdirectory, so the boundary is that move.
This file enumerates ``docs/`` **from disk** and asserts every subdirectory is in exactly one
of two sets, the archived one carrying a reason per member. A directory added tomorrow is in
neither and fails here — which is the assertion that survives, where "the gate names these
eight paths" would not.

Mutations checked when this file was written, each reddening a different assertion:
adding an undeclared ``docs/audit/``; dropping ``docs/issues`` from the gate command;
naming ``docs/reviews`` in it; removing ``continue-on-error`` from the advisory step.
"""

import unittest
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DOCS = PROJECT_ROOT / "docs"
WORKFLOW = PROJECT_ROOT / ".github/workflows/framework-gates.yml"

RESOLVER = "check_positional_refs.py"
GATE_STEP = "Check positional references (living corpus)"
ADVISORY_STEP = "Check positional references (archives, advisory)"

#: Subdirectories inside the gate. Everything at the TOP LEVEL of `docs/` is living by
#: construction — archiving is the act of moving a document down into a subdirectory — so
#: only the exceptions to that rule need naming, and these two are the ledger record bodies
#: whose coordinates `heal-issues` follows to reach a defect.
GATED_DIRS = {
    "issues",
    "backlog",
}

#: Every other `docs/` subdirectory, with the reason the gate does not fail on it. A reason
#: is required: an exclusion nobody can read is how a set rots. All of these are reported by
#: the advisory step, so none of them is dropped silently.
ARCHIVED_DIRS = {
    # Rotated here by `skill-archive-task` in lockstep. A coordinate in an archived TASK or
    # PLAN describes the tree as it stood when the task ran.
    "tasks": "archive",
    "plans": "archive",
    "archives": "archive",
    # A record of what a reviewer or a report saw, at the revision they saw it. Editing one
    # to quiet the resolver would falsify the record — the ground the audit-105 round
    # already declined to stand on.
    "reviews": "record",
    "reports": "record",
    # Per-task design notes, numbered by the task that produced them and not revised after.
    "design": "record",
    # Machine-written inbox and configs for `run-feedback` / `heal-issues`.
    "feedback": "machine",
    # Narrative material about past releases.
    "presentation": "record",
}


def steps():
    """Return every step of every job in the workflow, as dicts."""
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return [s for job in workflow["jobs"].values() for s in job.get("steps", [])]


def step_named(name):
    for step in steps():
        if step.get("name") == name:
            return step
    raise AssertionError(f"no step named {name!r} in {WORKFLOW.name}")


def docs_subdirectories():
    """Return the name of every subdirectory of `docs/`. The set is read, never declared."""
    return {p.name for p in DOCS.iterdir() if p.is_dir()}


class TestSetIsExhaustive(unittest.TestCase):
    """The anti-rot assertion. Everything below it re-states a decision already made."""

    def test_every_docs_subdirectory_is_gated_or_archived_with_a_reason(self):
        unclassified = docs_subdirectories() - GATED_DIRS - set(ARCHIVED_DIRS)
        self.assertEqual(
            unclassified,
            set(),
            "docs/ subdirectory in neither set — decide whether the reference gate fails on "
            f"it, and record the reason if it does not: {sorted(unclassified)}",
        )

    def test_no_set_member_is_missing_from_disk(self):
        """A renamed or removed directory leaves a stale member that would silently pass."""
        stale = (GATED_DIRS | set(ARCHIVED_DIRS)) - docs_subdirectories()
        self.assertEqual(stale, set(), f"named but absent from disk: {sorted(stale)}")

    def test_the_two_sets_are_disjoint(self):
        self.assertEqual(GATED_DIRS & set(ARCHIVED_DIRS), set())


class TestGateScope(unittest.TestCase):
    """What the failing step scans, asserted from both sides."""

    def setUp(self):
        self.run = step_named(GATE_STEP)["run"]

    def test_the_gate_runs_the_resolver(self):
        self.assertIn(RESOLVER, self.run)

    def test_the_gate_covers_the_top_level_of_docs(self):
        """The living corpus is the top level, so the glob is the rule, not a shorthand:
        a document added to `docs/` tomorrow is gated without anyone editing this list."""
        self.assertIn("docs/*.md", self.run)

    def test_the_gate_names_every_gated_directory(self):
        for name in sorted(GATED_DIRS):
            with self.subTest(directory=name):
                self.assertIn(f"docs/{name}", self.run)

    def test_the_gate_names_no_archived_directory(self):
        """Written as a prohibition over a named set: an absence is not otherwise checkable,
        and re-widening the scope is exactly how the six correct-document errors come back."""
        for name, why in sorted(ARCHIVED_DIRS.items()):
            with self.subTest(directory=name):
                self.assertNotIn(
                    f"docs/{name}",
                    self.run,
                    f"docs/{name} is excluded as '{why}' — gating it fails correct documents",
                )

    def test_the_gate_refuses_an_empty_scan(self):
        """An explicit path list can be mistyped, and the resolver answers a path matching
        nothing with NOTHING CHECKED and exit 0. Without this guard the narrowing could
        silently become a gate over no document at all."""
        self.assertIn("NOTHING CHECKED", self.run)


class TestArchivesAreReportedNotDropped(unittest.TestCase):
    """§4.2's second row. Coverage removed from the gate stays visible in the log."""

    def setUp(self):
        self.step = step_named(ADVISORY_STEP)

    def test_the_advisory_step_scans_the_whole_tree(self):
        self.assertIn("--all docs", self.step["run"])

    def test_the_advisory_step_never_fails_the_run(self):
        self.assertTrue(
            self.step.get("continue-on-error"),
            "an advisory step that fails the run is the gate this change just narrowed",
        )


if __name__ == "__main__":
    unittest.main()
