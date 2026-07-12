"""R4 — `file --dry-run` never writes: whole-tree hash before == after."""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402


class DryRunTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write_issue(self.root / "docs" / "issues", "RF-1",
                       "rf-1-first-issue", title="First issue")
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        fx.write(self.root / "docs" / "BACKLOG.md", fx.BACKLOG_FIXTURE)
        self.body = fx.write(self.root / "docs" / "feedback" / "body.md",
                             "Symptom: it exploded.\n")

        code, out, err = fx.run_cli(
            ["--repo-root", self.root, "collect", "--source", "workflow",
             "--kind", "tool-error", "--component", "html",
             "--message", "conversion exploded", "--exit-code", "2",
             "--json"])
        self.assertEqual(code, 0, err)
        self.fid = json.loads(out)["finding"]["finding_id"]
        self.before = fx.tree_hash(self.root)

    def _file(self, *extra):
        return fx.run_cli(["--repo-root", self.root, "file",
                           "--finding", self.fid, *extra, "--dry-run"])

    def test_defect_dry_run_tree_identical_and_previews_index_line(self):
        code, out, err = self._file(
            "--as", "defect", "--title", "Boom happens",
            "--category", "correctness", "--severity", "SEV-3",
            "--body-file", str(self.body))
        self.assertEqual(code, 0, err)
        # allocated ID (RF-1 exists on disk -> next is RF-2) + exact line
        self.assertIn("RF-2", out)
        expected_line = (
            "- **RF-2** [Boom happens](issues/rf-2-boom-happens.md) — "
            "severity `SEV-3`, status `open`, opened %s"
            % time.strftime("%Y-%m-%d"))
        self.assertIn(expected_line, out)
        self.assertEqual(fx.tree_hash(self.root), self.before,
                         "defect --dry-run must not touch the repo tree")

    def test_work_item_dry_run_tree_identical(self):
        code, out, err = self._file("--as", "work-item",
                                    "--title", "Follow up on boom",
                                    "--body-file", str(self.body))
        self.assertEqual(code, 0, err)
        self.assertIn("DRY-RUN", out)
        self.assertEqual(fx.tree_hash(self.root), self.before,
                         "work-item --dry-run must not touch the repo tree")

    def test_noise_dry_run_tree_identical_and_finding_stays_in_inbox(self):
        code, out, err = self._file("--as", "noise", "--reason", "flaky env")
        self.assertEqual(code, 0, err)
        self.assertEqual(fx.tree_hash(self.root), self.before,
                         "noise --dry-run must not touch the repo tree")
        inbox = self.root / ".agent" / "feedback" / "inbox"
        files = list(inbox.glob("fnd-*.json"))
        self.assertEqual(len(files), 1, "finding must stay in the inbox")
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(record["status"], "new")


if __name__ == "__main__":
    unittest.main()
