"""R6 — `file --as work-item` through the CLI: ID allocation from the record
dir, journal/inbox bookkeeping, and the flat layout's refusal.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import frontmatter  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"

STRUCTURED_BODY = """**Signal.** The retro had to file three items by hand.

| Option | Cost |
|---|---|
| lockstep | S |

**Recommendation:** option 1.
"""


class WorkItemCliTestCase(unittest.TestCase):
    LAYOUT = "index+files"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.index = fx.write(self.root / "docs" / "BACKLOG.md",
                              fx.BACKLOG_INDEX_FIXTURE)
        self.records = self.root / "docs" / "backlog"
        # the two records the index fixture points at — allocation scans the
        # record dir, not the index
        fx.write_work_item(self.records, "WI-1", "wi-1-first-item",
                           title="First item", status="done", effort="M")
        fx.write_work_item(self.records, "WI-2", "wi-2-second-item",
                           title="Second item", effort="S")
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md",
                             "backlog_layout": self.LAYOUT}))
        self.body = fx.write(self.root / "docs" / "feedback" / "body.md",
                             STRUCTURED_BODY)
        code, out, err = fx.run_cli(
            ["--repo-root", self.root, "collect", "--source", "workflow",
             "--kind", "user-friction", "--component", "run-feedback",
             "--message", "work-item had to be filed by hand",
             "--workflow", "vdd-multi", "--task-id", "task-009",
             "--json"])
        self.assertEqual(code, 0, err)
        self.fid = json.loads(out)["finding"]["finding_id"]

    def file_work_item(self, *extra):
        return fx.run_cli(["--repo-root", self.root, "file",
                           "--finding", self.fid, "--as", "work-item",
                           "--title", "Work-item path flattens the backlog",
                           "--body-file", str(self.body), *extra])


class TestTwoLevelCli(WorkItemCliTestCase):
    def test_allocates_next_id_over_the_record_dir(self):
        # messy neighbours must not break the max+1 scan
        fx.write_work_item(self.records, "WI-7", "wi-7-seven", effort="S")
        fx.write_work_item(self.records, "WI-8X", "wi-8x-messy", effort="S")
        code, out, err = self.file_work_item("--effort", "M", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["filed_as"]["id"], "WI-9")
        self.assertEqual(payload["filed_as"]["ledger"], "backlog")
        self.assertTrue(payload["filed_as"]["path"].endswith(
            "docs/backlog/wi-9-work-item-path-flattens-the-backlog.md"))

    def test_record_carries_context_and_index_gets_one_line(self):
        code, out, err = self.file_work_item("--effort", "S", "--json")
        self.assertEqual(code, 0, err)
        record_path = Path(json.loads(out)["filed_as"]["path"])
        meta, body = frontmatter.parse_file(record_path)
        self.assertEqual(meta["id"], "WI-3")
        self.assertEqual(meta["type"], "work-item")
        self.assertEqual(meta["source"], "vdd-multi task-009")  # run context
        self.assertEqual(meta["component"], "run-feedback")
        self.assertEqual(meta["finding_ref"], self.fid)
        self.assertNotIn("auto_fixable", meta)
        self.assertIn("| Option | Cost |", body)

        lines = self.index.read_text(encoding="utf-8").splitlines()
        anchor_idx = lines.index(ANCHOR)
        self.assertEqual(
            lines[anchor_idx + 1],
            "- **WI-3** [Work-item path flattens the backlog]"
            "(backlog/wi-3-work-item-path-flattens-the-backlog.md) — "
            "effort `S`, status `open`, opened %s" % meta["opened_at"])
        self.assertEqual(len(lines),
                         len(fx.BACKLOG_INDEX_FIXTURE.splitlines()) + 1)

    def test_finding_is_consumed_and_journaled_with_the_id(self):
        code, _, err = self.file_work_item("--effort", "S")
        self.assertEqual(code, 0, err)
        feedback = self.root / ".agent" / "feedback"
        self.assertEqual(list((feedback / "inbox").glob("fnd-*.json")), [])
        filed = list((feedback / "filed").glob("fnd-*.json"))
        self.assertEqual(len(filed), 1)
        record = json.loads(filed[0].read_text(encoding="utf-8"))
        self.assertEqual(record["filed_as"]["id"], "WI-3")
        journal = "\n".join(
            p.read_text(encoding="utf-8")
            for p in (feedback / "journal").glob("*.md"))
        self.assertIn("WI-3", journal)

    def test_junk_identity_is_refused_before_anything_is_written(self):
        """A hand-maintained ledger must not receive `<prefix>-n-none.md` or a
        record whose slug normalized to nothing."""
        index_before = self.index.read_bytes()
        for extra, expected in (((), 2), (("--slug", "…"), 2)):
            args = ["--repo-root", self.root, "file", "--finding", self.fid,
                    "--as", "work-item", "--body-file", str(self.body)]
            if extra:  # title present, slug unusable
                args += ["--title", "Has a title", *extra]
            code, out, err = fx.run_cli(args)
            self.assertEqual(code, expected, out + err)
        self.assertEqual(self.index.read_bytes(), index_before)
        self.assertEqual(
            sorted(p.name for p in self.records.glob("*.md")),
            ["wi-1-first-item.md", "wi-2-second-item.md"])

    def test_path_traversal_in_slug_cannot_escape_the_record_dir(self):
        code, out, err = self.file_work_item(
            "--slug", "../../../../etc/pwned", "--json")
        self.assertEqual(code, 0, err)
        record = Path(json.loads(out)["filed_as"]["path"])
        self.assertEqual(record.parent.resolve(), self.records.resolve())
        self.assertEqual(record.name, "etc-pwned.md")

    def test_flags_that_would_be_silently_dropped_are_refused(self):
        """F15 / S-16 — a silently ignored flag is how "we marked it
        auto-fixable" survives as a belief into a heal run."""
        for extra in (("--auto-fixable",), ("--severity", "SEV-2"),
                      ("--category", "logic")):
            with self.subTest(extra=extra):
                code, out, err = self.file_work_item(*extra)
                self.assertEqual(code, 2, out)
                self.assertIn("do not apply", err)
        self.assertEqual(self.index.read_text(encoding="utf-8"),
                         fx.BACKLOG_INDEX_FIXTURE)

    def test_defect_requires_a_category(self):
        """F5 — a missing category produced a `## None` section or a traceback."""
        code, out, err = fx.run_cli(
            ["--repo-root", self.root, "file", "--finding", self.fid,
             "--as", "defect", "--title", "T", "--body-file", str(self.body)])
        self.assertEqual(code, 2, out)
        self.assertIn("--category", err)

    def test_over_long_and_control_char_titles_are_refused(self):
        for title in ("x" * 200, "line\nbreak", "bell\x07"):
            with self.subTest(title=title[:20]):
                code, out, err = fx.run_cli(
                    ["--repo-root", self.root, "file", "--finding", self.fid,
                     "--as", "work-item", "--title", title,
                     "--body-file", str(self.body)])
                self.assertEqual(code, 2, out)

    def test_explicit_source_overrides_the_run_context(self):
        code, out, err = self.file_work_item("--source", "hand-written",
                                             "--json")
        self.assertEqual(code, 0, err)
        meta, _ = frontmatter.parse_file(
            Path(json.loads(out)["filed_as"]["path"]))
        self.assertEqual(meta["source"], "hand-written")


class TestFlatLayoutCli(WorkItemCliTestCase):
    LAYOUT = "flat"

    def test_structured_body_is_refused_not_flattened(self):
        # tree_hash is not usable here: taking the filing lock legitimately
        # creates .agent/feedback/.filing.lock. The LEDGERS must be untouched.
        index_before = self.index.read_bytes()
        records_before = sorted(p.name for p in self.records.glob("*.md"))
        code, out, err = self.file_work_item()
        self.assertEqual(code, 4, out)
        self.assertIn("flat backlog layout", err)
        self.assertEqual(self.index.read_bytes(), index_before)
        self.assertEqual(sorted(p.name for p in self.records.glob("*.md")),
                         records_before)
        # the refused finding stays in the inbox, re-filable after a fix
        inbox = self.root / ".agent" / "feedback" / "inbox"
        self.assertEqual(len(list(inbox.glob("fnd-*.json"))), 1)

    def test_one_liner_still_appends_a_bullet(self):
        fx.write(self.body, "Pin typescript until tsup ships TS7 dts.\n")
        code, out, err = self.file_work_item("--effort", "S", "--json")
        self.assertEqual(code, 0, err)
        self.assertIsNone(json.loads(out)["filed_as"]["id"])
        lines = self.index.read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[lines.index(ANCHOR) + 1].startswith(
            "- **Work-item path flattens the backlog ("))
        # flat layout writes no record file
        self.assertEqual(
            sorted(p.name for p in self.records.glob("*.md")),
            ["wi-1-first-item.md", "wi-2-second-item.md"])


if __name__ == "__main__":
    unittest.main()
