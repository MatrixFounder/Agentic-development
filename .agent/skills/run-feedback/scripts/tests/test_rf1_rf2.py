"""Regression tests for RF-1 and RF-2 — both from the 2026-07-13/14 eval campaign.

Same class, named in RF-2's own "Related" line: **the gate does not check what it
claims**. RF-1's `doctor` reported `ready: true` in the same payload whose
remediation said "run init"; RF-2's `file` accepted a body it could never let you
repair afterwards, and `--dry-run` previewed everything except the fallible part.

Each test runs the record's own reproduction, not a paraphrase of it.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import body as body_mod  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402


class RepoCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        (self.root / "docs" / "issues").mkdir(parents=True, exist_ok=True)


class TestRF1DoctorReadiness(RepoCase):
    """RF-1 — `ready` must not contradict the remediation beside it."""

    def test_an_unconfigured_repo_is_not_ready(self):
        """The record's exact reproduction: a repo with .git and docs/issues and
        no config.json. It used to print ready:true with a non-empty remediation."""
        code, out, err = fx.run_cli(["--repo-root", str(self.root), "doctor",
                                     "--json"])
        payload = json.loads(out)
        self.assertFalse(payload["ready"])
        self.assertFalse(payload["checks"]["configured"])
        self.assertTrue(payload["remediation"], "expected the init remediation")
        self.assertEqual(code, 3)

    def test_ready_and_a_nonempty_remediation_are_never_both_true(self):
        """The invariant behind the record, stated directly: a caller gating on
        `ready` must not be able to disagree with the remediation list."""
        for values in ({}, {"body_max_chars": 0}, {"issues_dir": "../../etc"}):
            with self.subTest(values=values):
                if values:
                    fx.write(self.root / "docs" / "feedback" / "config.json",
                             json.dumps(dict({"v": 1}, **values)))
                _, out, _ = fx.run_cli(["--repo-root", str(self.root), "doctor",
                                        "--json"])
                payload = json.loads(out)
                self.assertFalse(
                    payload["ready"] and payload["remediation"],
                    "ready:true alongside remediation %r — the contradiction RF-1 "
                    "was filed for" % payload["remediation"])

    def test_init_makes_it_ready(self):
        """The bootstrap flow the fix is supposed to enable, end to end."""
        code, _, err = fx.run_cli(["--repo-root", str(self.root), "init"])
        self.assertEqual(code, 0, err)
        code, out, err = fx.run_cli(["--repo-root", str(self.root), "doctor",
                                     "--json"])
        payload = json.loads(out)
        self.assertTrue(payload["checks"]["configured"])
        self.assertTrue(payload["ready"], payload["remediation"])
        self.assertEqual(code, 0, err)


class TestRF2BodyGate(RepoCase):
    """RF-2 — a body that cannot be repaired after filing must be refused before."""

    def setUp(self):
        super().setUp()
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1}))
        code, out, err = fx.run_cli(
            ["--repo-root", str(self.root), "collect", "--source", "test",
             "--kind", "test-failure", "--component", "demo",
             "--message", "boom", "--json"])
        self.assertEqual(code, 0, err)
        self.fid = json.loads(out)["finding"]["finding_id"]

    def _file(self, body_text, extra=()):
        path = fx.write(self.root / "bad.md", body_text)
        return fx.run_cli(["--repo-root", str(self.root), "file", "--finding",
                           self.fid, "--as", "defect", "--title", "demo",
                           "--category", "robustness", "--severity", "SEV-3",
                           "--body-file", str(path), *extra])

    def test_an_unterminated_fence_is_refused(self):
        """The record's reproduction verbatim: an unterminated ```sh fence used to
        be accepted at exit 0, leaving an unbalanced fence in the ledger — and
        create-only then forbade repairing it."""
        code, _, err = self._file(
            "**Symptom.** x\n\n**Reproduction.**\n\n```sh\necho broken\n")
        self.assertEqual(code, 4, err)
        self.assertIn("unterminated code fence", err)
        self.assertEqual(list((self.root / "docs" / "issues").glob("*.md")), [],
                         "a record was written despite the refusal")

    def test_a_defect_without_a_reproduction_section_is_refused(self):
        code, _, err = self._file("**Symptom.** just prose, no repro\n")
        self.assertEqual(code, 4, err)
        self.assertIn("no Reproduction section", err)

    def test_both_reproduction_heading_forms_are_accepted(self):
        for repro in ("**Reproduction.**", "## Reproduction",
                      "### Reproduction"):
            with self.subTest(repro=repro):
                self.assertEqual(
                    body_mod.guard_structure(
                        "**Symptom.** x\n\n%s\n\n```sh\nexit 1\n```\n" % repro,
                        "issue", require_repro=True).count("Reproduction"), 1)

    def test_a_work_item_body_needs_no_reproduction_section(self):
        """The asymmetry is deliberate: `/heal-issues` selects on a defect repro,
        and a work-item has nothing to reproduce."""
        body_mod.guard_structure("Just a signal paragraph.\n", "work-item",
                                 require_repro=False)

    def test_a_work_item_body_still_needs_balanced_fences(self):
        with self.assertRaises(CliError):
            body_mod.guard_structure("a\n\n```sh\nunclosed\n", "work-item")

    def test_dry_run_previews_the_body(self):
        """The other half of RF-2: `--dry-run` echoed the id, the paths and the
        index line but never the BODY — the one part composed by hand and
        unrepairable after filing."""
        code, out, err = self._file(fx.DEFECT_BODY, extra=("--dry-run",))
        self.assertEqual(code, 0, err)
        self.assertIn("record as it would be written", out)
        self.assertIn("**Reproduction.**", out)
        self.assertIn("exit 1", out)

    def test_a_conforming_body_files_cleanly(self):
        code, _, err = self._file(fx.DEFECT_BODY)
        self.assertEqual(code, 0, err)
        filed = list((self.root / "docs" / "issues").glob("*.md"))
        self.assertEqual(len(filed), 1)
        text = filed[0].read_text(encoding="utf-8")
        self.assertEqual(text.count("```"), 2, "fences must balance in the record")


if __name__ == "__main__":
    unittest.main()
