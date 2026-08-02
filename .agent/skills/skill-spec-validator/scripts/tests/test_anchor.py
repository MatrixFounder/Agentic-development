"""Anchor-located RTM: the gate must not depend on the document's language.

Why these exist (TASK 095, from work-item WI-30 filed by a downstream project
whose artifacts are written in Russian):

``validate.py`` located the RTM through the document's own prose, in three
independent places — the heading regex, the ``['ID','Requirement']`` column-name
check, and a second ``r['ID']`` dict lookup inside ``validate_plan``. On a
non-English document all three fail, and the third fails *even after* the second
is fixed, which is why the two modes are tested here as a pair rather than one
at a time. A gate whose verdict depends on which language the author writes in
is asserting something nobody claimed and it cannot check.

The contract these tests pin, per ``documentation-standards`` §4.3/§4.4:

  * ``<!-- contract:rtm -->`` on its own line, directly above the RTM heading,
    locates the table. It WINS over any prose matcher.
  * Under the anchor the table is read **positionally**: the first column is the
    requirement ID. Column names are prose and carry no contract.
  * The anchor is OPTIONAL. With no anchor the pre-existing heading matcher and
    column-name check run unchanged — that is what keeps every shipped artifact,
    in this repo and downstream, behaving byte-identically (``test_corpus``).
  * A duplicated anchor is an error, never "first one wins": an ambiguous
    address is a document defect and silently picking one hides it.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

validate = fx.validate

ANCHOR = "<!-- contract:rtm -->"

#: Heading, column names and cell text all non-English — the shape that made
#: the gate unrunnable for the reporting project. Column names deliberately do
#: NOT transliterate to 'ID'/'Requirement': matching them would be the same
#: defect with a longer synonym list (WI-30 option 2).
RU_TASK = """# Техническое задание — фикстура

## 1. Описание

Текст.

{anchor}

## 2. Матрица трассируемости требований

| ИД | Требование | MVP? |
|----|------------|------|
| R1 | Первое требование | Да |
| R2 | Второе требование | Нет |

## 3. Ограничения

Нет.
"""


def ru_task(anchor=ANCHOR):
    return RU_TASK.format(anchor=anchor)


class TestAnchorLocatesRtmInAnyLanguage(unittest.TestCase):
    """R2 — the reported half."""

    def test_task_mode_passes_on_a_non_english_rtm(self, ):
        path = fx.write(Path(self.tmp) / "TASK.md", ru_task())
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements", out)

    def test_plan_mode_passes_on_the_same_document(self):
        """R3 — the UNreported half.

        `validate_plan` extracts ids with `r['ID']`, a dict lookup on the
        authored header text, and exits 1 with 'No IDs found in RTM table.'
        This path is independent of the column-name check, so a fix that
        closes only the reported one ships WI-30's fix carrying WI-32's
        defect. Both modes are asserted together on purpose.
        """
        task = fx.write(Path(self.tmp) / "TASK.md", ru_task())
        plan = fx.write(Path(self.tmp) / "PLAN.md",
                        fx.plan_md("- [ ] R1 сделать\n- [ ] R2 сделать"))
        code, out = fx.run(validate.validate_plan, str(plan), str(task))
        self.assertEqual(code, 0, out)
        self.assertIn("2 requirements covered", out)

    def test_plan_mode_still_reports_a_genuinely_missing_id(self):
        """Positional reading must not become a rubber stamp."""
        task = fx.write(Path(self.tmp) / "TASK.md", ru_task())
        plan = fx.write(Path(self.tmp) / "PLAN.md", fx.plan_md("- [ ] R1 сделать"))
        code, out = fx.run(validate.validate_plan, str(plan), str(task))
        self.assertEqual(code, 1, out)
        self.assertIn("R2", out)

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)


class TestAnchorWinsOverProse(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_anchor_beats_an_earlier_english_rtm_heading(self):
        """A document may DISCUSS the RTM before tabulating it.

        The heading matcher takes the first `Requirements Traceability` /
        `RTM` heading it meets, which in a document that first explains the
        matrix and then presents it is the wrong section — the corpus already
        contains such a heading (`KNOWN_NON_RTM_SHAPES` in test_corpus).
        The anchor names the real one.
        """
        doc = (
            "# Spec\n\n"
            "## Requirements Traceability — what this section is for\n\n"
            "Prose about the RTM, deliberately containing no table.\n\n"
            + ANCHOR + "\n\n"
            "## The actual matrix\n\n"
            "| Ключ | Формулировка |\n|---|---|\n| R7 | Нечто |\n"
        )
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)
        self.assertIn("1 requirements", out)


class TestAnchorFailureModes(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_duplicate_anchor_is_an_error_not_first_wins(self):
        doc = ru_task() + "\n" + ANCHOR + "\n\n| ИД | Треб |\n|---|---|\n| R9 | x |\n"
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 1, out)
        self.assertIn("contract:rtm", out)

    def test_anchor_with_no_table_names_the_anchor_not_the_heading(self):
        doc = "# Spec\n\n" + ANCHOR + "\n\n## Матрица\n\nЗабыли таблицу.\n"
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 1, out)
        self.assertIn("contract:rtm", out)

    def test_anchored_table_with_a_single_column_is_an_error(self):
        """Positional reading needs at least an id column and one more.

        The message must name the anchor: this document HAS an anchor, so a
        fallback-flavoured complaint about a missing English heading would
        send the author to fix the wrong thing.
        """
        doc = "# Spec\n\n" + ANCHOR + "\n\n## Матрица\n\n| ИД |\n|---|\n| R1 |\n"
        path = fx.write(Path(self.tmp) / "TASK.md", doc)
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 1, out)
        self.assertIn("contract:rtm", out)


class TestAnchorlessDocumentsAreUntouched(unittest.TestCase):
    """R6 — the compatibility guarantee, asserted rather than assumed.

    Every artifact written before this change carries no anchor, so the
    fallback path is what the whole corpus runs on. `test_corpus` proves it
    over the real corpus; these two prove the two failure messages an author
    sees are still the pre-change ones.
    """

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_english_anchorless_task_still_passes(self):
        path = fx.write(Path(self.tmp) / "TASK.md", fx.task_md())
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 0, out)

    def test_non_english_anchorless_task_still_fails_the_old_way(self):
        """Without an anchor there is nothing structural to key on, so the
        document must still be rejected — the anchor is the remedy, not a
        silent widening of what counts as an RTM.

        Which of the two pre-change messages fires depends on whether the
        heading happens to contain a latin `RTM`, so the assertion accepts
        either DIAGNOSIS while requiring that it is one of the two the
        fallback path produces.

        The assertion is deliberately on the diagnosis and not on the whole
        message: both fallback errors now also SUGGEST the anchor as the
        remedy, which is the right thing for them to do — an author who hits
        this needs to be told the way out, and an assertion that forbade the
        word would be pinning the absence of help.
        """
        path = fx.write(Path(self.tmp) / "TASK.md", ru_task(anchor=""))
        code, out = fx.run(validate.validate_task, str(path))
        self.assertEqual(code, 1, out)
        diagnosis = out.splitlines()[0]
        self.assertTrue(
            "section missing" in diagnosis or "must contain columns" in diagnosis,
            "expected one of the two pre-change fallback diagnoses, got: %r" % diagnosis)


if __name__ == "__main__":
    unittest.main()
