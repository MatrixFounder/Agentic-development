"""R7 — tolerant ledger reads + triage duplicate candidates."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import ledger_issues  # noqa: E402


class TriageTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.issues_dir = self.root / "docs" / "issues"

    def _collect(self, message):
        code, out, err = fx.run_cli(
            ["--repo-root", self.root, "collect", "--source", "workflow",
             "--kind", "tool-error", "--component", "xlsx",
             "--message", message, "--exit-code", "2", "--json"])
        self.assertEqual(code, 0, err)
        return json.loads(out)["finding"]

    def _triage_rows(self):
        code, out, err = fx.run_cli(["--repo-root", self.root, "triage",
                                     "--json"])
        self.assertEqual(code, 0, err)
        return json.loads(out)


class TestTolerantRead(TriageTestCase):
    def test_local_vocab_parses_and_ranks(self):
        fx.write_issue(self.issues_dir, "RF-1", "rf-1-handled",
                       status="handled", severity="MED")
        fx.write_issue(self.issues_dir, "RF-2", "rf-2-no-severity",
                       status="open", severity=None)
        cfg = fx.load_cfg(self.root)
        records = {r["id"]: r for r in ledger_issues.list_issues(cfg)}
        self.assertEqual(set(records), {"RF-1", "RF-2"})
        self.assertEqual(records["RF-1"]["status"], "handled")
        self.assertEqual(records["RF-1"]["severity"], "MED")
        self.assertEqual(records["RF-1"]["severity_rank"], 30)
        self.assertIsNone(records["RF-2"]["severity"])
        self.assertEqual(records["RF-2"]["severity_rank"], 0)

    def test_severity_rank_map(self):
        self.assertEqual(ledger_issues.severity_rank("MED"), 30)
        self.assertEqual(ledger_issues.severity_rank("MEDIUM"), 30)
        self.assertEqual(ledger_issues.severity_rank(None), 0)
        self.assertEqual(ledger_issues.severity_rank("WAT"), 0)
        self.assertEqual(ledger_issues.severity_rank("SEV-2"), 50)


class TestDupCandidates(TriageTestCase):
    def test_fingerprint_dup_candidate(self):
        rec = self._collect("recalc produced stale cached values")
        fx.write_issue(self.issues_dir, "RF-5", "rf-5-same-fp",
                       extra_lines=["fingerprint: %s" % rec["fingerprint"]])
        rows = self._triage_rows()
        self.assertEqual(len(rows), 1)
        dups = rows[0]["dup_candidates"]
        self.assertTrue(any("RF-5" in d and "fingerprint" in d
                            for d in dups), dups)

    def test_title_token_overlap_candidate(self):
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md",
                 "# Known Issues\n\n## correctness\n\n"
                 "- **RF-7** [Recalc verify cached values]"
                 "(issues/rf-7-recalc-verify.md) — status `open`, "
                 "opened 2026-01-01\n")
        self._collect("recalc could not verify cached values")
        rows = self._triage_rows()
        self.assertEqual(len(rows), 1)
        dups = rows[0]["dup_candidates"]
        self.assertTrue(any("RF-7" in d and "title overlap" in d
                            for d in dups), dups)

    def test_no_candidates_for_unrelated_finding(self):
        self._collect("completely unrelated failure signature")
        rows = self._triage_rows()
        self.assertEqual(rows[0]["dup_candidates"], [])


if __name__ == "__main__":
    unittest.main()
