"""Frontmatter round-trip, tolerant parsing, and serialize stability."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import frontmatter, ledger_issues  # noqa: E402

CONTRACT_META = {
    "id": "RF-1",
    "type": "known-issue",
    "status": "open",
    "opened_at": "2026-07-12",
    "category": "correctness",
    "severity": "SEV-3",
    "slug": "rf-1-fixture-issue",
    "component": "html",
    "fingerprint": "abcd1234abcd1234",
    "evidence_paths": ["logs/a.log", "tmp/out b.txt"],
    "auto_fixable": True,
    "finding_ref": "fnd-20260712-101500-abcd1234",
}


class TestRoundTrip(unittest.TestCase):
    def test_contract_key_order_bool_and_block_list_round_trip(self):
        text = frontmatter.serialize(CONTRACT_META) + "\n# RF-1 — t\n\nbody\n"
        meta, body = frontmatter.parse(text)
        self.assertEqual(meta, CONTRACT_META)
        self.assertEqual(list(meta), list(CONTRACT_META))  # order preserved
        self.assertIs(meta["auto_fixable"], True)
        self.assertEqual(meta["evidence_paths"],
                         ["logs/a.log", "tmp/out b.txt"])
        self.assertIn("body", body)

    def test_serialize_parse_serialize_is_stable(self):
        once = frontmatter.serialize(CONTRACT_META)
        again = frontmatter.serialize(frontmatter.parse(once)[0])
        self.assertEqual(once, again)


class TestTolerantParse(unittest.TestCase):
    def test_inline_comment_stripped(self):
        meta, _ = frontmatter.parse(
            "---\nstatus: open   # note to self\n---\nbody")
        self.assertEqual(meta["status"], "open")

    def test_unknown_keys_kept(self):
        meta, _ = frontmatter.parse(
            "---\nid: X-1\nlocal_extension: kept\n---\n")
        self.assertEqual(meta["local_extension"], "kept")

    def test_no_frontmatter_returns_empty_meta_and_full_text(self):
        meta, body = frontmatter.parse("just a plain file\nno delimiters\n")
        self.assertEqual(meta, {})
        self.assertIn("just a plain file", body)

    def test_booleans_parsed(self):
        meta, _ = frontmatter.parse(
            "---\nauto_fixable: true\nother: false\n---\n")
        self.assertIs(meta["auto_fixable"], True)
        self.assertIs(meta["other"], False)


class TestGeneratedIssueFileStability(unittest.TestCase):
    def test_file_defect_output_reserializes_identically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fx.make_repo(tmp)
            fx.write(root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
            cfg = fx.load_cfg(root)
            ledger_issues.file_defect(
                cfg, "RF-9", "rf-9-generated", "Generated", "correctness",
                "Body.", severity="SEV-4",
                extensions={"component": "html",
                            "fingerprint": "abcd1234abcd1234",
                            "evidence_paths": ["logs/a.log"],
                            "auto_fixable": True,
                            "finding_ref": "fnd-1"})
            raw = (Path(cfg.issues_dir) / "rf-9-generated.md").read_text(
                encoding="utf-8")
            meta, _ = frontmatter.parse(raw)
            # the file starts with exactly what serialize(meta) produces
            self.assertTrue(raw.startswith(frontmatter.serialize(meta)))


if __name__ == "__main__":
    unittest.main()
