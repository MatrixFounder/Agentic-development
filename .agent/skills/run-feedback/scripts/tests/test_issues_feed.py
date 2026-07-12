"""R7 — `issues --json` feed: severity sorting and filters."""
import json
import sys
import tempfile
import unittest

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402


class IssuesFeedTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        issues = self.root / "docs" / "issues"
        fx.write_issue(issues, "RF-1", "rf-1-sev2", severity="SEV-2",
                       status="open", opened_at="2026-01-01",
                       extra_lines=["auto_fixable: true"])
        fx.write_issue(issues, "RF-2", "rf-2-sev3", severity="SEV-3",
                       status="fixed", opened_at="2026-01-02")
        fx.write_issue(issues, "RF-3", "rf-3-low", severity="LOW",
                       status="open", opened_at="2026-01-03")
        fx.write_issue(issues, "RF-4", "rf-4-unknown-sev", severity="WAT",
                       status="open", opened_at="2026-01-04")
        fx.write_issue(issues, "RF-5", "rf-5-no-sev", severity=None,
                       status="handled", opened_at="2026-01-05",
                       extra_lines=["auto_fixable: sure"])

    def _issues(self, *extra):
        code, out, err = fx.run_cli(["--repo-root", self.root, "issues",
                                     *extra, "--json"])
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_sorted_by_severity_rank_desc(self):
        rows = self._issues()
        self.assertEqual([r["id"] for r in rows],
                         ["RF-1", "RF-2", "RF-3", "RF-4", "RF-5"])
        ranks = [r["severity_rank"] for r in rows]
        self.assertEqual(ranks, sorted(ranks, reverse=True))
        self.assertEqual(ranks, [50, 40, 10, 0, 0])

    def test_status_open_filter(self):
        rows = self._issues("--status", "open")
        self.assertEqual({r["id"] for r in rows}, {"RF-1", "RF-3", "RF-4"})

    def test_auto_fixable_filters_on_boolean_true_only(self):
        rows = self._issues("--auto-fixable")
        # RF-5 carries `auto_fixable: sure` (a string) — must be excluded
        self.assertEqual([r["id"] for r in rows], ["RF-1"])
        self.assertIs(rows[0]["auto_fixable"], True)

    def test_unknown_severity_string_does_not_crash(self):
        rows = self._issues()
        rf4 = next(r for r in rows if r["id"] == "RF-4")
        self.assertEqual(rf4["severity"], "WAT")
        self.assertEqual(rf4["severity_rank"], 0)


if __name__ == "__main__":
    unittest.main()
