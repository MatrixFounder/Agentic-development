"""An RTM split across several tables must be read whole, or said to be partial.

Why these exist (RF-6, filed by a downstream project from a measured run):

``parse_markdown_table`` stops at the first non-table line, so the located RTM
block could only ever yield its FIRST table — and ``validate.py`` printed
``Success`` about it. A TASK carrying 23 requirements in five per-epic tables
reported ``Found 9 requirements``, exit 0, with no line saying that 61% of the
section had not been read. ``validate_plan`` shares the same locator, so the
planning gate would have reported full coverage of the nine it could see. The
exit code of a gate is read as its reach; a gate that succeeds over part of its
subject is worse than an absent one.

The contract pinned here:

  * The FIRST table fixes the RTM's shape. Every later table in the block with
    an IDENTICAL header row is the same RTM continued and is read.
  * A later table with a DIFFERENT header is not a requirements table. It is
    skipped and **named** — the corpus puts real ones there (`task-096` files a
    corpus measurement and a rejected-candidates table under `### N.N Details by
    ID`, which stays inside the block because `_SECTION_END` cuts at the next
    h2). Reading those as requirements invents ids like `Bold density`; refusing
    on "more than one table" fails three shipped tasks. Both are gates broken on
    the artifacts they govern, which is the defect this suite already exists for.
  * Skipping is never silent, and neither is continuing: both modes print what
    they read before they print a verdict.
  * Scanning does not STOP at a foreign table. `RTM-E1 / Details / RTM-E2` must
    not lose E2 to a subsection someone filed in the middle.

Every assertion below fails on the pre-fix behaviour: first-table-only turns the
three-requirement fixtures into one, and drops the notes entirely.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

validate = fx.validate

ANCHOR = "<!-- contract:rtm -->"

#: The reproduction from the record, verbatim in shape: one RTM, two epics,
#: identical columns. Non-English on purpose — the multi-table split and the
#: language-independence of the anchor path are separate properties, and a
#: fixture that exercised only the first would let a "fix" re-couple them.
EPIC_TASK = """# Техническое задание — фикстура

## 1. Описание

Текст.

{anchor}

## 2. Требования

### Эпик E-1

| ИД | Требование | MVP? |
| --- | --- | --- |
| **R-1** | первое | Да |

### Эпик E-2

| ИД | Требование | MVP? |
| --- | --- | --- |
| **R-2** | второе | Да |
| **R-3** | третье | Да |

## 3. Дальше
"""

#: `task-096`'s shape, reduced: the RTM, then a subsection tabulating something
#: else. Both tables live in the block; only the first is requirements.
DETAILS_TASK = """# Spec

{anchor}

## 1. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? |
| --- | --- | --- |
| R1 | First thing | Yes |
| R2 | Second thing | Yes |

### 1.1 Details by ID

| Corpus | Files | Mean words/sentence |
| --- | ---: | ---: |
| oldest | 21 | 5.8 |
| newest | 9 | 14.1 |

## 2. Problem
"""


class _Tmp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def task(self, text, anchor=ANCHOR):
        return fx.write(Path(self.tmp) / "TASK.md", text.format(anchor=anchor))


class TestContinuationTablesAreRead(_Tmp):
    """The reported defect."""

    def test_task_mode_counts_every_epic_table(self):
        code, out = fx.run(validate.validate_task, str(self.task(EPIC_TASK)))
        self.assertEqual(code, 0, out)
        self.assertIn("3 requirements", out)

    def test_the_split_is_stated_not_assumed(self):
        """`Found 3` alone cannot be told apart from a single 3-row table.

        The count is the answer; how much was read is what makes the count
        checkable without opening the document.
        """
        _code, out = fx.run(validate.validate_task, str(self.task(EPIC_TASK)))
        self.assertIn("2 tables", out)

    def test_plan_mode_sees_ids_from_the_later_tables(self):
        """The half that would have shipped a false coverage verdict.

        `validate_plan` builds its id set from the same locator, so before the
        fix a plan covering only the first epic printed `All 1 requirements
        covered` and the rest were never asked about.
        """
        task = self.task(EPIC_TASK)
        plan = fx.write(Path(self.tmp) / "PLAN.md", fx.plan_md("- [ ] R-1 сделать"))
        code, out = fx.run(validate.validate_plan, str(plan), str(task))
        self.assertEqual(code, 1, out)
        self.assertIn("R-2", out)
        self.assertIn("R-3", out)

    def test_plan_mode_passes_when_every_table_is_covered(self):
        task = self.task(EPIC_TASK)
        plan = fx.write(Path(self.tmp) / "PLAN.md",
                        fx.plan_md("- [ ] R-1\n- [ ] R-2\n- [ ] R-3"))
        code, out = fx.run(validate.validate_plan, str(plan), str(task))
        self.assertEqual(code, 0, out)
        self.assertIn("3 requirements covered", out)

    def test_the_anchorless_heading_path_behaves_the_same(self):
        """The fallback path shares the locator and had the identical defect.

        Fixing only the anchor path would leave the whole pre-anchor corpus —
        i.e. every artifact written before `contract:rtm` existed — on the old
        behaviour, which is the half-applied-fix shape this module's siblings
        were written for.
        """
        doc = (
            "# Spec\n\n## Requirements Traceability Matrix (RTM)\n\n"
            "### Epic A\n\n"
            "| ID | Requirement |\n| --- | --- |\n| R1 | first |\n\n"
            "### Epic B\n\n"
            "| ID | Requirement |\n| --- | --- |\n| R2 | second |\n\n"
            "## Next\n")
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements", out)


class TestForeignTablesAreSkippedAndNamed(_Tmp):
    """The corpus counter-example that rules out "parse every table"."""

    def test_a_details_subsection_is_not_counted_as_requirements(self):
        code, out = fx.run(validate.validate_task, str(self.task(DETAILS_TASK)))
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements", out)

    def test_the_skipped_table_is_named(self):
        """Silence here is the defect restated, not its remedy.

        An author who DID mean the second table as requirements gets the reason
        it was not read and the exact remedy; an author who did not loses
        nothing. This is the line whose absence let `Found 9` pass for 23.
        """
        _code, out = fx.run(validate.validate_task, str(self.task(DETAILS_TASK)))
        self.assertIn("NOT read as requirements", out)
        self.assertIn("Corpus", out)

    def test_plan_mode_does_not_demand_coverage_of_a_foreign_table(self):
        """The consequence of getting this wrong is a gate nobody can pass:
        `oldest` and `newest` would become required plan references."""
        task = self.task(DETAILS_TASK)
        plan = fx.write(Path(self.tmp) / "PLAN.md", fx.plan_md("- [ ] R1\n- [ ] R2"))
        code, out = fx.run(validate.validate_plan, str(plan), str(task))
        self.assertEqual(code, 0, out)

    def test_a_foreign_table_does_not_stop_the_scan(self):
        """Skip, not stop: an interleaved subsection must not truncate the RTM."""
        doc = (
            "# Spec\n\n" + ANCHOR + "\n\n## RTM\n\n"
            "| ID | Requirement |\n| --- | --- |\n| R1 | first |\n\n"
            "### Notes\n\n"
            "| Note | Text |\n| --- | --- |\n| n1 | whatever |\n\n"
            "### Epic B\n\n"
            "| ID | Requirement |\n| --- | --- |\n| R2 | second |\n\n"
            "## Next\n")
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements", out)
        self.assertIn("NOT read as requirements", out)


class TestSingleTableDocumentsSayNothingExtra(_Tmp):
    """A note printed on every run is a note nobody reads.

    The corpus is overwhelmingly single-table, so the ordinary case must stay
    byte-identical to before the fix — otherwise the signal that something was
    skipped is buried under the runs where nothing was.
    """

    def test_no_note_on_an_ordinary_task(self):
        path = fx.write(Path(self.tmp) / "TASK.md", fx.task_md())
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)
        self.assertNotIn("Note:", out)


if __name__ == "__main__":
    unittest.main()
