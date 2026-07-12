"""R5 — ID allocation over the real messy live namespace."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import ids  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402

MESSY_IDS = ("TF-X-7", "XLSX-10B-DEFER", "HTML2MD-11-BUG", "HTML2MD-11",
             "HTML2MD-12", "PERF-HIGH-2", "XLSX-PREVIEW-PNG-ASSERT")


class IdAllocationTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.issues_dir = Path(self._tmp.name) / "issues"

    def _seed_messy(self):
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        for n, issue_id in enumerate(MESSY_IDS):
            fx.write(self.issues_dir / ("messy-%d.md" % n),
                     "---\nid: %s\ntype: known-issue\nstatus: open\n---\n"
                     "# %s — t\n\nbody\n" % (issue_id, issue_id))


class TestNextNumber(IdAllocationTestCase):
    def test_empty_dir_next_is_1(self):
        self.issues_dir.mkdir(parents=True)
        self.assertEqual(ids.next_number(self.issues_dir, "RF"), 1)

    def test_missing_dir_next_is_1(self):
        self.assertEqual(ids.next_number(self.issues_dir / "nope", "RF"), 1)

    def test_dash_inside_prefix_tf_x(self):
        self._seed_messy()
        self.assertEqual(ids.next_number(self.issues_dir, "TF-X"), 8)

    def test_word_suffix_counts_html2md(self):
        self._seed_messy()
        # HTML2MD-11-BUG counts as 11; max(11, 11, 12) + 1 = 13
        self.assertEqual(ids.next_number(self.issues_dir, "HTML2MD"), 13)

    def test_letter_suffix_counts_xlsx(self):
        self._seed_messy()
        # XLSX-10B-DEFER contributes 10; XLSX-PREVIEW-PNG-ASSERT contributes 0
        self.assertEqual(ids.next_number(self.issues_dir, "XLSX"), 11)

    def test_multiword_prefix_perf_high(self):
        self._seed_messy()
        self.assertEqual(ids.next_number(self.issues_dir, "PERF-HIGH"), 3)

    def test_non_numeric_id_never_crashes_the_scan(self):
        self._seed_messy()
        # scanning any prefix walks past XLSX-PREVIEW-PNG-ASSERT unharmed
        self.assertEqual(ids.next_number(self.issues_dir, "XLSX-PREVIEW"), 1)
        self.assertEqual(ids.next_number(self.issues_dir,
                                         "XLSX-PREVIEW-PNG-ASSERT"), 1)

    def test_absent_prefix_starts_at_1(self):
        self._seed_messy()
        self.assertEqual(ids.next_number(self.issues_dir, "RF"), 1)


class TestSlug(IdAllocationTestCase):
    def test_cyrillic_only_title_demands_explicit_slug(self):
        self.issues_dir.mkdir(parents=True)
        with self.assertRaises(CliError) as ctx:
            ids.allocate(self.issues_dir, "RF", "Кириллица и только она")
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("--slug", str(ctx.exception))

    def test_mixed_title_slugifies_to_latin_kebab(self):
        self.assertEqual(ids.normalize_slug("Fix №5 (broken)"),
                         "fix-no5-broken")
        self.issues_dir.mkdir(parents=True)
        issue_id, slug = ids.allocate(self.issues_dir, "RF",
                                      "Fix №5 (broken)")
        self.assertEqual(issue_id, "RF-1")
        self.assertEqual(slug, "rf-1-fix-no5-broken")
        self.assertRegex(slug, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_prefix_for_uses_map_then_default(self):
        prefixes = {"html": "HTML2MD", "_default": "RF"}
        self.assertEqual(ids.prefix_for("html", prefixes), "HTML2MD")
        self.assertEqual(ids.prefix_for("unmapped", prefixes), "RF")
        with self.assertRaises(CliError) as ctx:
            ids.prefix_for("unmapped", {"html": "HTML2MD"})
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
