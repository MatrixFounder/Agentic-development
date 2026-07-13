"""`init` — bootstrap docs/feedback/ configs from templates (Bootstrap protocol).

Create-only, prefix seeding from the existing ledger's messy IDs, idempotency,
and schema conformance (the created config must load WITHOUT unknown-key
warnings — that is the drift the templates exist to prevent)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CLI = Path(__file__).resolve().parents[1] / "run_feedback.py"

_ISSUE = """---
id: {id}
type: known-issue
status: open
opened_at: 2026-06-01
category: robustness
component: {component}
slug: {slug}
---
# {id} — fixture
"""


class InitBootstrapTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        (self.root / ".git").mkdir()
        self.issues = self.root / "docs" / "issues"
        self.issues.mkdir(parents=True)

    def _seed_issue(self, issue_id, component, slug):
        (self.issues / ("%s.md" % slug)).write_text(
            _ISSUE.format(id=issue_id, component=component, slug=slug),
            encoding="utf-8")

    def _init(self, *extra):
        return subprocess.run(
            [sys.executable, str(CLI), "--repo-root", str(self.root),
             "init", "--json", *extra],
            capture_output=True, text=True, timeout=120)

    def test_creates_both_configs_and_seeds_prefixes(self):
        self._seed_issue("TF-X-7", "transcript-fetcher", "tf-x-7-a")
        self._seed_issue("HTML2MD-3", "html", "html2md-3-b")
        self._seed_issue("XLSX-10B-DEFER", "xlsx", "xlsx-10b-c")
        proc = self._init()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(len(payload["created"]), 2)
        self.assertEqual(payload["seeded_prefixes"], {
            "transcript-fetcher": "TF-X", "html": "HTML2MD", "xlsx": "XLSX"})
        cfg = json.loads((self.root / "docs/feedback/config.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(cfg["id_prefixes"]["transcript-fetcher"], "TF-X")
        self.assertEqual(cfg["id_prefixes"]["_default"], "RF")
        heal = json.loads((self.root / "docs/feedback/heal-config.json")
                          .read_text(encoding="utf-8"))
        self.assertFalse(heal["scheduling"]["enabled"],
                         "template must ship with scheduling disabled")

    def test_created_config_loads_without_unknown_key_warnings(self):
        # Schema-drift guard: the template's keys must ALL be known to the
        # engine (this is exactly the bug class init exists to prevent).
        self._init()
        proc = subprocess.run(
            [sys.executable, str(CLI), "--repo-root", str(self.root),
             "doctor", "--json"],
            capture_output=True, text=True, timeout=120)
        self.assertNotIn("unknown config key", proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["checks"]["config_source"].endswith(
            "config.json"))

    def test_second_run_is_create_only(self):
        self._init()
        marker = '"_default": "CUSTOM"'
        cfg_path = self.root / "docs/feedback/config.json"
        cfg_path.write_text(cfg_path.read_text(encoding="utf-8")
                            .replace('"_default": "RF"', marker),
                            encoding="utf-8")
        proc = self._init()
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["created"], [])
        self.assertEqual(len(payload["skipped"]), 2)
        self.assertIn(marker, cfg_path.read_text(encoding="utf-8"),
                      "existing config must never be overwritten")

    def test_conflicting_prefixes_reported_not_guessed(self):
        self._seed_issue("TF-X-7", "transcript-fetcher", "tf-x-7-a")
        self._seed_issue("TF-9", "transcript-fetcher", "tf-9-b")
        proc = self._init()
        payload = json.loads(proc.stdout)
        self.assertNotIn("transcript-fetcher", payload["seeded_prefixes"])
        self.assertEqual(sorted(payload["conflicts"]["transcript-fetcher"]),
                         ["TF", "TF-X"])
        self.assertTrue(any("conflicting" in t for t in payload["todo"]))

    def test_doctor_nudges_init_when_unconfigured(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "--repo-root", str(self.root),
             "doctor", "--json"],
            capture_output=True, text=True, timeout=120)
        payload = json.loads(proc.stdout)
        self.assertTrue(any("run_feedback.py init" in r
                            for r in payload["remediation"]))


if __name__ == "__main__":
    unittest.main()
