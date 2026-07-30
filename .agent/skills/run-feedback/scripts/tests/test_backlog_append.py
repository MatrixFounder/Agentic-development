"""R6 — work-item ledger: two-level lockstep filing (index + record file),
ID allocation, rollback, dry-run, and the legacy flat layout's refusal guard.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import frontmatter, ledger_backlog  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"

TABLE_BODY = """**Signal.** The appender never created a record file.

| Option | Cost |
|---|---|
| teach it lockstep | S |
| refuse instead | XS |

**Recommendation:** option 1.
"""


# --- two-level layout (the contract) -----------------------------------------

class TwoLevelTestCase(unittest.TestCase):
    """A fixture repo whose backlog is a thin index over docs/backlog/*.md."""

    LAYOUT = "index+files"
    BACKLOG_DIR = "docs/backlog"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.index = fx.write(self.root / "docs" / "BACKLOG.md",
                              fx.BACKLOG_INDEX_FIXTURE)
        self.records = self.root / self.BACKLOG_DIR
        fx.write_work_item(self.records, "WI-1", "wi-1-first-item",
                           title="First item", status="done", effort="M")
        fx.write_work_item(self.records, "WI-2", "wi-2-second-item",
                           title="Second item", effort="S")
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md",
                             "backlog_dir": self.BACKLOG_DIR,
                             "backlog_layout": self.LAYOUT}))
        self.cfg = fx.load_cfg(self.root)

    def file_item(self, item_id="WI-3", slug="wi-3-new-item", title="New item",
                  body=TABLE_BODY, **kwargs):
        return ledger_backlog.file_work_item(
            self.cfg, item_id, slug, title, body, opened_at="2026-07-29",
            **kwargs)

    def index_lines(self):
        return self.index.read_text(encoding="utf-8").splitlines()


class TestTwoLevelFiling(TwoLevelTestCase):
    def test_body_lands_in_a_record_file_not_in_the_index(self):
        result = self.file_item(effort="S", value="closes the flattening hole",
                               source="TASK-009 retro")
        record = Path(result["record_path"])
        self.assertEqual(record, self.records / "wi-3-new-item.md")
        meta, body = frontmatter.parse_file(record)
        self.assertEqual(
            list(meta),
            ["id", "type", "status", "opened_at", "slug", "effort", "value",
             "source"])
        self.assertEqual(meta["type"], "work-item")
        self.assertEqual(meta["status"], "open")
        # every structural line of the body survives, unflattened
        self.assertIn("| Option | Cost |", body)
        self.assertIn("**Recommendation:** option 1.", body)
        self.assertEqual(body.count("\n| teach it lockstep | S |"), 1)
        # …and the index got exactly ONE short pointer line
        lines = self.index_lines()
        anchor_idx = lines.index(ANCHOR)
        self.assertEqual(
            lines[anchor_idx + 1],
            "- **WI-3** [New item](backlog/wi-3-new-item.md) — effort `S`, "
            "status `open`, opened 2026-07-29")
        self.assertLess(len(lines[anchor_idx + 1]), 200)
        self.assertNotIn("| Option | Cost |",
                         self.index.read_text(encoding="utf-8"))
        # newest first: the pre-existing entry is pushed down, not clobbered
        self.assertTrue(lines[anchor_idx + 2].startswith("- **WI-2**"))
        self.assertIn("## Closed", lines)

    def test_effort_clause_omitted_without_effort(self):
        result = self.file_item()
        self.assertEqual(
            result["index_line"],
            "- **WI-3** [New item](backlog/wi-3-new-item.md) — status `open`, "
            "opened 2026-07-29")

    def test_free_text_keys_are_quoted_and_round_trip(self):
        result = self.file_item(
            value="two things: the body, and the index line",
            source="TASK-009 retro\nsecond line")
        meta, _ = frontmatter.parse_file(Path(result["record_path"]))
        self.assertEqual(meta["value"],
                         "two things: the body, and the index line")
        self.assertEqual(meta["source"], "TASK-009 retro second line")

    def test_apostrophe_in_free_text_does_not_truncate_the_value(self):
        result = self.file_item(value="it's the index line that suffers")
        meta, _ = frontmatter.parse_file(Path(result["record_path"]))
        self.assertEqual(meta["value"], "it’s the index line that suffers")

    def test_extension_keys_land_after_source_and_exclude_auto_fixable(self):
        result = self.file_item(
            source="retro",
            extensions={"component": "run-feedback", "fingerprint": "abc123",
                        "evidence_paths": ["docs/reviews/x.md"],
                        "finding_ref": "fnd-1", "auto_fixable": True})
        meta, _ = frontmatter.parse_file(Path(result["record_path"]))
        self.assertEqual(list(meta)[-4:],
                         ["component", "fingerprint", "evidence_paths",
                          "finding_ref"])
        self.assertNotIn("auto_fixable", meta)  # /heal-issues is defect-only

    def test_vocab_violations_are_contract_errors(self):
        for kwargs in ({"status": "handled"}, {"effort": "HUGE"}):
            with self.assertRaises(CliError) as ctx:
                self.file_item(**kwargs)
            self.assertEqual(ctx.exception.code, 4)

    def test_dry_run_leaves_the_tree_identical_and_previews_everything(self):
        before = fx.tree_hash(self.root)
        result = self.file_item(effort="M", dry_run=True)
        self.assertEqual(fx.tree_hash(self.root), before)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["item_id"], "WI-3")
        self.assertTrue(result["record_path"].endswith(
            "docs/backlog/wi-3-new-item.md"))
        self.assertIn("effort `M`", result["index_line"])
        self.assertIn("| Option | Cost |", result["record_text"])

    def test_create_only_never_overwrites_a_record(self):
        self.file_item()
        stamp = (self.records / "wi-3-new-item.md").read_bytes()
        index_before = self.index.read_bytes()
        with self.assertRaises(CliError) as ctx:
            self.file_item(item_id="WI-4", body="different body")
        self.assertEqual(ctx.exception.code, 4)
        self.assertEqual((self.records / "wi-3-new-item.md").read_bytes(),
                         stamp)
        self.assertEqual(self.index.read_bytes(), index_before)

    def test_missing_anchor_fails_before_any_write(self):
        fx.write(self.index, "# Backlog\n\n## Discovered\n\n- old\n")
        with self.assertRaises(CliError) as ctx:
            self.file_item()
        self.assertEqual(ctx.exception.code, 4)
        # zero writes: no record file, and never a blind EOF append
        self.assertFalse((self.records / "wi-3-new-item.md").exists())
        self.assertNotIn("WI-3", self.index.read_text(encoding="utf-8"))

    def test_index_write_failure_rolls_the_record_back(self):
        boom = OSError("index write exploded")
        with mock.patch.object(ledger_backlog, "_write_atomic",
                               side_effect=boom):
            with self.assertRaises(OSError):
                self.file_item()
        self.assertFalse((self.records / "wi-3-new-item.md").exists())
        self.assertNotIn("WI-3", self.index.read_text(encoding="utf-8"))

    def test_backlog_is_seeded_from_the_template_when_absent(self):
        self.index.unlink()
        result = self.file_item(effort="S")
        self.assertTrue(result["seeded_backlog"])
        text = self.index.read_text(encoding="utf-8")
        self.assertIn(ANCHOR, text)                    # anchor survives seeding
        self.assertIn("Rules / Conventions", text)     # preamble kept
        self.assertNotIn("SEED TEMPLATE", text)        # seed comment dropped
        self.assertNotIn("_No work-items recorded yet._", text)
        self.assertIn(result["index_line"], text)


class TestNestedRecordDir(TwoLevelTestCase):
    """A non-default backlog_dir must still produce a correct relative link."""

    BACKLOG_DIR = "docs/wi/items"

    def test_link_is_relative_to_the_index_file(self):
        result = self.file_item()
        self.assertEqual(
            result["index_line"],
            "- **WI-3** [New item](wi/items/wi-3-new-item.md) — status `open`, "
            "opened 2026-07-29")


# --- the pure helpers --------------------------------------------------------

class TestFormatIndexLine(unittest.TestCase):
    def test_grammar_matches_the_known_issues_format_contract(self):
        self.assertEqual(
            ledger_backlog.format_index_line(
                "WI-9", "Title", "backlog/wi-9-title.md", "done",
                "2026-07-29", effort="L"),
            "- **WI-9** [Title](backlog/wi-9-title.md) — effort `L`, "
            "status `done`, opened 2026-07-29")

    def test_record_link_is_posix(self):
        self.assertEqual(
            ledger_backlog.record_link("/repo/docs/BACKLOG.md",
                                       "/repo/docs/backlog/wi-1-x.md"),
            "backlog/wi-1-x.md")


# --- legacy flat layout ------------------------------------------------------

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


class TestFlatBodyGuard(unittest.TestCase):
    """The flat layout inlines the body, so it must REFUSE what it would
    flatten rather than silently produce an unreadable index line."""

    def test_structured_body_is_refused(self):
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.guard_flat_body(TABLE_BODY)
        self.assertEqual(ctx.exception.code, 4)
        self.assertIn("index+files", ctx.exception.details["remediation"])

    def test_long_single_line_body_is_refused(self):
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.guard_flat_body("word " * 200)
        self.assertEqual(ctx.exception.code, 4)

    def test_genuine_one_liner_passes(self):
        body = "Pin typescript until tsup ships TS7 dts support."
        self.assertEqual(ledger_backlog.guard_flat_body(body), body)


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
