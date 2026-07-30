"""Unit tests for skill-spec-validator (TASK 092 / WI-1).

R1-R2 heading matcher · R3 table checks · R4 bypass · R5-R6 PLAN coverage and
the whole-token boundary · R7 table parser + section slicing · R8 CLI errors.

Every heading fixture in R1 is copied VERBATIM from a file in `docs/tasks/` —
invented shapes are what let the matcher drift away from the corpus in the first
place (WI-1: the gate had never once passed on a shipped artifact).
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

validate = fx.validate


# --- R1 / R2: the RTM heading matcher ----------------------------------------

class TestRtmHeadingShapes(unittest.TestCase):
    """R1 — the eight shapes `docs/tasks/` actually ships, verbatim."""

    #: Counted from `docs/tasks/` (2026-07-30). The first two are the corpus's
    #: MOST COMMON shapes and the first version of this list omitted both, so
    #: every fixture happened to contain the word "Requirements" — a narrowing
    #: that required it would have broken 24 of 46 real headings while this
    #: suite stayed green (vdd-multi iteration 2, V5).
    SHIPPED = [
        "## RTM (acceptance criteria)",                 # 16 files
        "## Requirements Traceability Matrix (RTM)",     # 15
        "## 2. RTM",                                     # 7 (bare RTM + number)
        "### 2. Requirements (RTM)",                     # 4
        "## 2. Requirements Traceability Matrix (RTM)",
        "### 3. Requirements Traceability Matrix (RTM)",
        "## Requirements Traceability",
        "## 6. Acceptance Criteria (Requirements Traceability Matrix)",
        "## 5. Acceptance Criteria (RTM)",
    ]

    def test_every_shipped_shape_matches(self):
        for heading in self.SHIPPED:
            with self.subTest(heading=heading):
                self.assertTrue(validate.RTM_HEADER.search(heading + "\n"),
                                "shipped heading no longer matched: %s" % heading)

    def test_h4_and_paren_section_numbers_match(self):
        for heading in ("#### Requirements (RTM)",
                        "## 2) Requirements Traceability Matrix",
                        "## requirements traceability matrix"):  # case-insensitive
            with self.subTest(heading=heading):
                self.assertTrue(validate.RTM_HEADER.search(heading + "\n"))

    def test_shapes_that_must_not_match(self):
        """R2 — the matcher is a gate, not a wildcard."""
        for heading in (
            "# Requirements Traceability Matrix",          # h1 is the doc title
            "##### Requirements (RTM)",                    # h5 is too deep
            "## 2. Use Cases",                             # names neither form
            "###Requirements (RTM)",                       # no space after hashes
            "the Requirements Traceability Matrix is below",   # prose, not a heading
            "| ID | Requirement | RTM |",                  # a table row, not a heading
        ):
            with self.subTest(heading=heading):
                self.assertIsNone(validate.RTM_HEADER.search(heading + "\n"))

    def test_split_on_the_heading_is_non_capturing(self):
        """The regex stays zero-width/non-capturing so split() yields exactly
        [before, after] — a capturing group here would shift RTM_HEADER.split()[1]
        onto the group text and silently parse the wrong block."""
        content = fx.task_md()
        parts = validate.RTM_HEADER.split(content)
        self.assertEqual(len(parts), 2)
        self.assertIn("| R1 |", parts[1])


# --- R3 / R4: --mode task -----------------------------------------------------

class TaskModeTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def task(self, text):
        return str(fx.write(self.tmp / "TASK.md", text))


class TestTaskMode(TaskModeTestCase):
    def test_valid_rtm_passes_and_reports_the_row_count(self):
        code, out = fx.run(validate.validate_task, self.task(fx.task_md()))
        self.assertEqual(code, 0, out)
        self.assertIn("Found 2 requirements", out)

    def test_missing_heading_fails(self):
        code, out = fx.run(validate.validate_task,
                           self.task("# Spec\n\n## 1. Description\n\nText.\n"))
        self.assertEqual(code, 1)
        self.assertIn("section missing", out)

    def test_empty_table_fails(self):
        code, out = fx.run(validate.validate_task,
                           self.task(fx.task_md(table="\nNo table here.\n")))
        self.assertEqual(code, 1)
        self.assertIn("empty or invalid", out)

    def test_wrong_columns_fail(self):
        table = ("\n| ID | Finding | Fix |\n|----|---------|-----|\n"
                 "| R1 | thing | do it |\n")
        code, out = fx.run(validate.validate_task,
                           self.task(fx.task_md(table=table)))
        self.assertEqual(code, 1)
        self.assertIn("must contain columns", out)

    def test_missing_file_fails(self):
        """R8."""
        code, out = fx.run(validate.validate_task, str(self.tmp / "absent.md"))
        self.assertEqual(code, 1)
        self.assertIn("not found", out)


class TestBypass(TaskModeTestCase):
    """R4 — the escape hatch, and the fact that it is a BARE SUBSTRING."""

    def test_bypass_short_circuits_task_mode(self):
        broken = "# Spec\n\nNo RTM at all. %s\n" % fx.BYPASS_TOKEN
        code, out = fx.run(validate.validate_task, self.task(broken))
        self.assertEqual(code, 0)
        self.assertIn("bypassed", out)

    def test_bypass_short_circuits_plan_mode(self):
        task = self.task("# Spec\n\nNo RTM. %s\n" % fx.BYPASS_TOKEN)
        plan = str(fx.write(self.tmp / "PLAN.md", fx.plan_md("- [ ] nothing")))
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0)
        self.assertIn("bypassed", out)

    def test_token_merely_mentioned_in_prose_still_bypasses(self):
        """Pinned as CURRENT behavior, not endorsed: a spec that documents the
        token disables its own gate and prints a line that reads like a pass.
        This bit the first draft of TASK 092's own spec. Tightening it is a
        behavior change to a live gate and belongs to the owner."""
        text = fx.task_md() + (
            "\n## 4. Notes\n\nUse %s only with a written justification.\n"
            % fx.BYPASS_TOKEN)
        code, out = fx.run(validate.validate_task, self.task(text))
        self.assertEqual(code, 0)
        self.assertIn("bypassed", out)
        self.assertNotIn("Found 2 requirements", out)  # never reached the table


# --- R5 / R6: --mode plan -----------------------------------------------------

class PlanModeTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def pair(self, plan_body, table=fx.RTM_TABLE):
        task = fx.write(self.tmp / "TASK.md", fx.task_md(table=table))
        plan = fx.write(self.tmp / "PLAN.md", fx.plan_md(plan_body))
        return str(plan), str(task)


class TestPlanCoverage(PlanModeTestCase):
    def test_ids_in_step_headings_count(self):
        """R5 — `## Step N — … (R1)`, the majority form in docs/plans/."""
        plan, task = self.pair("## Step 1 — do it (R1)\n\n## Step 2 — more (R2)\n")
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0, out)
        self.assertIn("All 2 requirements covered", out)

    def test_ids_in_checklist_bullets_count(self):
        plan, task = self.pair("- [ ] R1 do it\n- [x] R2 done\n")
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0, out)

    def test_uncovered_ids_are_named(self):
        plan, task = self.pair("## Step 1 — do it (R1)\n")
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 1)
        self.assertIn("['R2']", out)
        self.assertNotIn("'R1'", out)

    def test_missing_plan_file_fails(self):
        """R8."""
        _, task = self.pair("- [ ] R1\n- [ ] R2\n")
        code, out = fx.run(validate.validate_plan,
                           str(self.tmp / "absent.md"), task)
        self.assertEqual(code, 1)
        self.assertIn("not found", out)


class TestWholeTokenBoundary(PlanModeTestCase):
    """R6 — the case WI-1 names by hand."""

    ONE_ID = "\n| ID | Requirement |\n|----|-------------|\n| R1 | thing |\n"

    def test_r10_does_not_satisfy_r1(self):
        plan, task = self.pair("## Step 1 — covers (R10)\n", table=self.ONE_ID)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 1)
        self.assertIn("['R1']", out)

    def test_r1_inside_a_word_does_not_count(self):
        plan, task = self.pair("Refactor VAR1 and R1x and xR1.\n",
                               table=self.ONE_ID)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 1)

    def test_hyphenated_ids_match_whole(self):
        table = ("\n| ID | Requirement |\n|----|-------------|\n"
                 "| R-065-1 | namespaced |\n| TF-X-7 | messy live id |\n")
        plan, task = self.pair("## Step 1 (R-065-1)\n\n- [ ] TF-X-7 fix it\n",
                               table=table)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0, out)

    def test_hyphenated_id_is_not_satisfied_by_its_prefix(self):
        table = "\n| ID | Requirement |\n|----|-------------|\n| R-065-1 | x |\n"
        plan, task = self.pair("## Step 1 (R-065)\n", table=table)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 1)

    def test_markdown_noise_around_the_id_is_normalized(self):
        table = ("\n| ID | Requirement |\n|----|-------------|\n"
                 "| **R1** | bold |\n| `R2` | code |\n| [R3] | bracketed |\n")
        plan, task = self.pair("- [ ] R1\n- [ ] R2\n- [ ] R3\n", table=table)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0, out)

    def test_empty_id_cell_is_skipped_not_crashed_on(self):
        table = ("\n| ID | Requirement |\n|----|-------------|\n"
                 "|  | blank id |\n| R2 | real |\n")
        plan, task = self.pair("- [ ] R2 only\n", table=table)
        code, out = fx.run(validate.validate_plan, plan, task)
        self.assertEqual(code, 0, out)


# --- R7: the table parser and section slicing ---------------------------------

class TestParseMarkdownTable(unittest.TestCase):
    def test_separator_row_is_skipped(self):
        rows = validate.parse_markdown_table(fx.RTM_TABLE)
        self.assertEqual([r["ID"] for r in rows], ["R1", "R2"])

    def test_escaped_pipe_stays_inside_the_cell(self):
        table = ("| ID | Requirement |\n|----|----|\n"
                 "| R1 | a \\| b |\n")
        rows = validate.parse_markdown_table(table)
        self.assertEqual(rows[0]["Requirement"], "a \\| b")

    def test_row_with_wrong_column_count_is_skipped(self):
        table = ("| ID | Requirement |\n|----|----|\n"
                 "| R1 | ok |\n| R2 | too | many |\n")
        rows = validate.parse_markdown_table(table)
        self.assertEqual([r["ID"] for r in rows], ["R1"])

    def test_table_ends_at_the_first_non_pipe_line(self):
        table = ("| ID | Requirement |\n|----|----|\n| R1 | ok |\n"
                 "\nProse.\n\n| ID | Requirement |\n|----|----|\n| R9 | later |\n")
        rows = validate.parse_markdown_table(table)
        self.assertEqual([r["ID"] for r in rows], ["R1"])

    def test_no_table_yields_no_rows(self):
        self.assertEqual(validate.parse_markdown_table("Just prose.\n"), [])


class TestSectionSlicing(TaskModeTestCase):
    def test_a_later_h2_table_does_not_leak_into_the_rtm_block(self):
        """R7 — the RTM block stops at the next `## `, so an unrelated table
        further down the spec cannot inflate (or rescue) the requirement count."""
        text = fx.task_md(epilogue=(
            "\n## 3. Risk Register\n\n"
            "| ID | Requirement |\n|----|-------------|\n| R99 | not an RTM row |\n"))
        code, out = fx.run(validate.validate_task, self.task(text))
        self.assertEqual(code, 0, out)
        self.assertIn("Found 2 requirements", out)

    def test_rtm_under_an_h3_heading_still_stops_at_the_next_h2(self):
        text = fx.task_md(heading="### 2. Requirements (RTM)")
        code, out = fx.run(validate.validate_task, self.task(text))
        self.assertEqual(code, 0, out)
        self.assertIn("Found 2 requirements", out)


# --- R8: the CLI surface ------------------------------------------------------

class TestCli(PlanModeTestCase):
    def test_plan_mode_with_one_file_is_a_usage_error(self):
        plan, _ = self.pair("- [ ] R1\n- [ ] R2\n")
        code, out, _err = fx.run_cli(["--mode", "plan", plan])
        self.assertEqual(code, 1)
        self.assertIn("requires", out)

    def test_task_mode_end_to_end_through_main(self):
        _, task = self.pair("- [ ] R1\n- [ ] R2\n")
        code, out, _err = fx.run_cli(["--mode", "task", task])
        self.assertEqual(code, 0, out)
        self.assertIn("Found 2 requirements", out)

    def test_unknown_mode_is_rejected_by_argparse(self):
        code, _out, err = fx.run_cli(["--mode", "wat", "x.md"])
        self.assertEqual(code, 2)
        self.assertIn("invalid choice", err)


if __name__ == "__main__":
    unittest.main()
