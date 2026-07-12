"""R4 — file_defect lockstep: placement, preamble safety, rollback, vocab."""
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import frontmatter, ledger_issues  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402


class LockstepTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.index_path = fx.write(self.root / "docs" / "KNOWN_ISSUES.md",
                                   fx.INDEX_FIXTURE)
        self.cfg = fx.load_cfg(self.root)

    def _index_text(self):
        return self.index_path.read_text(encoding="utf-8")

    def _preamble(self, text):
        return text.split("## correctness", 1)[0]


class TestPlacement(LockstepTestCase):
    def test_inserts_into_right_section_in_id_order(self):
        before = self._index_text()
        ledger_issues.file_defect(self.cfg, "RF-2", "rf-2-second-issue",
                                  "Second issue", "correctness", "Body.")
        after = self._index_text()
        lines = after.splitlines()
        i_rf1 = next(i for i, l in enumerate(lines) if l.startswith("- **RF-1**"))
        i_rf2 = next(i for i, l in enumerate(lines) if l.startswith("- **RF-2**"))
        i_rf3 = next(i for i, l in enumerate(lines) if l.startswith("- **RF-3**"))
        i_rob = next(i for i, l in enumerate(lines) if l == "## robustness")
        self.assertLess(i_rf1, i_rf2)
        self.assertLess(i_rf2, i_rf3)
        self.assertLess(i_rf3, i_rob)  # stayed inside ## correctness
        # preamble byte-identical
        self.assertEqual(self._preamble(before), self._preamble(after))
        # issue file written alongside
        self.assertTrue((self.cfg.issues_dir / "rf-2-second-issue.md").is_file())

    def test_new_category_created_in_alphabetical_position(self):
        before = self._index_text()
        ledger_issues.file_defect(self.cfg, "DF-1", "df-1-dogfood-find",
                                  "Dogfood find", "dogfood", "Body.")
        after = self._index_text()
        i_cor = after.index("## correctness")
        i_dog = after.index("## dogfood")
        i_rob = after.index("## robustness")
        self.assertLess(i_cor, i_dog)
        self.assertLess(i_dog, i_rob)
        self.assertIn("- **DF-1** [Dogfood find](issues/df-1-dogfood-find.md)",
                      after)
        self.assertEqual(self._preamble(before), self._preamble(after))

    def test_rules_preamble_never_touched(self):
        before = self._index_text()
        ledger_issues.file_defect(self.cfg, "RF-2", "rf-2-a", "A",
                                  "correctness", "b")
        ledger_issues.file_defect(self.cfg, "DF-1", "df-1-b", "B",
                                  "dogfood", "b")
        ledger_issues.file_defect(self.cfg, "RF-5", "rf-5-c", "C",
                                  "robustness", "b")
        after = self._index_text()
        self.assertEqual(self._preamble(before), self._preamble(after))
        self.assertIn("## Rules / Conventions", after)


class TestIndexLineFormat(LockstepTestCase):
    def test_exact_contract_format_with_severity(self):
        line = ledger_issues.format_index_line(
            "RF-9", "Boom happens", "rf-9-boom-happens", "open",
            "2026-07-12", "SEV-3")
        self.assertEqual(
            line,
            "- **RF-9** [Boom happens](issues/rf-9-boom-happens.md) — "
            "severity `SEV-3`, status `open`, opened 2026-07-12")

    def test_severity_clause_omitted_when_none(self):
        today = time.strftime("%Y-%m-%d")
        result = ledger_issues.file_defect(
            self.cfg, "RF-6", "rf-6-no-sev", "No sev", "correctness",
            "Body.", severity=None)
        self.assertEqual(
            result["index_line"],
            "- **RF-6** [No sev](issues/rf-6-no-sev.md) — "
            "status `open`, opened %s" % today)
        self.assertNotIn("severity", result["index_line"])


class TestRollback(LockstepTestCase):
    def test_index_write_failure_removes_issue_file(self):
        before = self._index_text()
        original = ledger_issues._write_atomic

        def explode(path, text):
            raise RuntimeError("simulated index write failure")

        ledger_issues._write_atomic = explode
        try:
            with self.assertRaises(RuntimeError):
                ledger_issues.file_defect(self.cfg, "RF-7", "rf-7-rollback",
                                          "Rollback", "correctness", "Body.")
        finally:
            ledger_issues._write_atomic = original
        self.assertFalse((self.cfg.issues_dir / "rf-7-rollback.md").exists(),
                         "issue file must be rolled back on index failure")
        self.assertEqual(self._index_text(), before)


class TestWriteVocab(LockstepTestCase):
    def test_existing_slug_conflict_code_4(self):
        fx.write_issue(self.cfg.issues_dir, "RF-8", "rf-8-taken")
        with self.assertRaises(CliError) as ctx:
            ledger_issues.file_defect(self.cfg, "RF-9", "rf-8-taken", "Dup",
                                      "correctness", "b")
        self.assertEqual(ctx.exception.code, 4)

    def test_status_outside_write_vocab_code_4(self):
        with self.assertRaises(CliError) as ctx:
            ledger_issues.file_defect(self.cfg, "RF-9", "rf-9-x", "X",
                                      "correctness", "b", status="handled")
        self.assertEqual(ctx.exception.code, 4)

    def test_severity_outside_write_vocab_code_4(self):
        with self.assertRaises(CliError) as ctx:
            ledger_issues.file_defect(self.cfg, "RF-9", "rf-9-x", "X",
                                      "correctness", "b", severity="MED")
        self.assertEqual(ctx.exception.code, 4)


class TestCreateIfAbsent(unittest.TestCase):
    def test_seeds_index_from_known_issues_format_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.make_repo(tmp)
            cfg = fx.load_cfg(root)
            self.assertFalse(Path(cfg.index_path).exists())
            result = ledger_issues.file_defect(
                cfg, "RF-1", "rf-1-first", "First", "logic", "Body.")
            self.assertTrue(result["seeded_index"])
            text = Path(cfg.index_path).read_text(encoding="utf-8")
            self.assertIn("Rules / Conventions", text)
            self.assertNotIn("_No issues recorded yet._", text)
            self.assertNotIn("<!--", text)
            self.assertIn("## logic", text)
            self.assertIn("- **RF-1** [First](issues/rf-1-first.md)", text)


class TestExtensionKeys(LockstepTestCase):
    def test_extension_keys_appear_after_slug(self):
        ledger_issues.file_defect(
            self.cfg, "RF-2", "rf-2-ext", "Ext", "correctness", "Body.",
            severity="SEV-3",
            extensions={"component": "html",
                        "fingerprint": "abcd1234abcd1234",
                        "evidence_paths": ["logs/a.log"],
                        "auto_fixable": True,
                        "finding_ref": "fnd-1"})
        meta, _ = frontmatter.parse_file(self.cfg.issues_dir / "rf-2-ext.md")
        keys = list(meta)
        slug_at = keys.index("slug")
        for ext in ("component", "fingerprint", "evidence_paths",
                    "auto_fixable", "finding_ref"):
            self.assertGreater(keys.index(ext), slug_at,
                               "%s must come after slug" % ext)
        # contract keys are all present and in front
        self.assertEqual(keys[:7], ["id", "type", "status", "opened_at",
                                    "category", "severity", "slug"])

    def test_empty_extensions_are_omitted(self):
        ledger_issues.file_defect(
            self.cfg, "RF-2", "rf-2-lean", "Lean", "correctness", "Body.",
            extensions={"component": None, "fingerprint": "",
                        "evidence_paths": [], "auto_fixable": None,
                        "finding_ref": None})
        meta, _ = frontmatter.parse_file(self.cfg.issues_dir / "rf-2-lean.md")
        for ext in ("component", "fingerprint", "evidence_paths",
                    "auto_fixable", "finding_ref"):
            self.assertNotIn(ext, meta)


if __name__ == "__main__":
    unittest.main()
