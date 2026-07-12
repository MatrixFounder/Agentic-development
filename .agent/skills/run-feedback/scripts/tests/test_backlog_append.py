"""R6 — backlog work-item append: anchor discipline, dry-run, bullet format."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import ledger_backlog  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"


class BacklogTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.backlog = fx.write(Path(self._tmp.name) / "BACKLOG.md",
                                fx.BACKLOG_FIXTURE)


class TestAppend(BacklogTestCase):
    def test_bullet_inserted_immediately_after_anchor(self):
        bullet = "- **New find (2026-07-12)** — fresh bullet"
        result = ledger_backlog.append_work_item(self.backlog, ANCHOR, bullet)
        self.assertFalse(result["dry_run"])
        lines = self.backlog.read_text(encoding="utf-8").splitlines()
        anchor_idx = lines.index(ANCHOR)
        self.assertEqual(lines[anchor_idx + 1], bullet)
        # pre-existing bullet pushed down, not clobbered (newest first)
        self.assertTrue(lines[anchor_idx + 2].startswith("- **Old item"))

    def test_missing_anchor_raises_code_4(self):
        no_anchor = fx.write(Path(self._tmp.name) / "no-anchor.md",
                             "# Backlog\n\n## Discovered Issues\n\n- old\n")
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.append_work_item(no_anchor, ANCHOR, "- bullet")
        self.assertEqual(ctx.exception.code, 4)
        # never a blind EOF append
        self.assertNotIn("- bullet",
                         no_anchor.read_text(encoding="utf-8"))

    def test_missing_file_raises_code_4(self):
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.append_work_item(
                Path(self._tmp.name) / "absent.md", ANCHOR, "- bullet")
        self.assertEqual(ctx.exception.code, 4)

    def test_dry_run_leaves_file_byte_identical(self):
        before = self.backlog.read_bytes()
        result = ledger_backlog.append_work_item(
            self.backlog, ANCHOR, "- **X (2026-07-12)** — y", dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertEqual(self.backlog.read_bytes(), before)


class TestFormatBullet(unittest.TestCase):
    def test_without_effort_or_value(self):
        self.assertEqual(
            ledger_backlog.format_bullet("Title", "body  text\nwrapped",
                                         "2026-07-12"),
            "- **Title (2026-07-12)** — body text wrapped")

    def test_with_effort_and_value(self):
        self.assertEqual(
            ledger_backlog.format_bullet("Title", "body", "2026-07-12",
                                         effort="M", value="high"),
            "- **Title (2026-07-12)** — body · Effort: M · Value: high")

    def test_with_effort_only(self):
        self.assertEqual(
            ledger_backlog.format_bullet("Title", "body", "2026-07-12",
                                         effort="S"),
            "- **Title (2026-07-12)** — body · Effort: S")


if __name__ == "__main__":
    unittest.main()
