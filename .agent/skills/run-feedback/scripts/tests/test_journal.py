"""R3 — append-only journal: format, sanitization, multiprocess atomicity.

This module is imported by multiprocessing spawn children, so the hammer
worker must live at module level and the module must import cleanly.
"""
import multiprocessing
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from feedback_lib import journal  # noqa: E402

HEADER_RE = re.compile(
    r"^## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] [a-z_\-]+ \| ")
BULLET_RE = re.compile(r"^- \S.*: ")

# fixed timestamp so every hammer append lands in ONE monthly file
FIXED_TS = time.mktime((2026, 7, 12, 12, 0, 0, 0, 0, -1))


def _hammer_worker(journal_dir, count):
    for i in range(count):
        journal.append_event(journal_dir, "finding_collected",
                             "hammer entry", {"pid": os.getpid(), "seq": i},
                             ts=FIXED_TS)


class JournalTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.jdir = Path(self._tmp.name) / "journal"


class TestEntryFormat(JournalTestCase):
    def test_header_matches_contract_regex(self):
        journal.append_event(self.jdir, "finding_collected", "subject text",
                             ts=FIXED_TS)
        text = journal.journal_path(self.jdir, FIXED_TS).read_text(
            encoding="utf-8")
        first = text.splitlines()[0]
        self.assertRegex(first, HEADER_RE)
        self.assertIn("finding_collected | subject text", first)

    def test_monthly_file_name(self):
        ts = time.mktime((2026, 3, 15, 12, 0, 0, 0, 0, -1))
        self.assertEqual(journal.journal_path(self.jdir, ts).name,
                         "2026-03.md")
        journal.append_event(self.jdir, "mine_run", "x", ts=ts)
        self.assertTrue((self.jdir / "2026-03.md").is_file())

    def test_details_render_as_dash_key_value(self):
        journal.append_event(self.jdir, "finding_filed", "s",
                             {"kind": "tool-error", "ledger": "issues"},
                             ts=FIXED_TS)
        text = journal.journal_path(self.jdir, FIXED_TS).read_text(
            encoding="utf-8")
        self.assertIn("- kind: tool-error\n", text)
        self.assertIn("- ledger: issues\n", text)

    def test_injection_in_subject_is_sanitized(self):
        journal.append_event(
            self.jdir, "finding_collected",
            "# fake heading\n## another | with pipes\r\nand newlines",
            {"note": "\n# detail heading attempt"}, ts=FIXED_TS)
        text = journal.journal_path(self.jdir, FIXED_TS).read_text(
            encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("#"):
                self.assertRegex(
                    line, HEADER_RE,
                    "non-header hash line leaked into journal: %r" % line)
        # the payload survived, flattened into the single header line
        self.assertIn("fake heading", text)

    def test_invalid_event_type_raises_value_error(self):
        for bad in ("", "Bad Type", "UPPER", "9starts-with-digit",
                    "space here", None):
            with self.assertRaises(ValueError, msg=repr(bad)):
                journal.append_event(self.jdir, bad, "subject")

    def test_append_returns_growing_byte_offset(self):
        first = journal.append_event(self.jdir, "mine_run", "a", ts=FIXED_TS)
        second = journal.append_event(self.jdir, "mine_run", "b", ts=FIXED_TS)
        self.assertEqual(first, 0)
        self.assertGreater(second, first)


class TestMultiprocessHammer(JournalTestCase):
    def test_hammer_4x25_no_torn_lines(self):
        ctx = multiprocessing.get_context("spawn")
        procs = [ctx.Process(target=_hammer_worker,
                             args=(str(self.jdir), 25)) for _ in range(4)]
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=120)
        for p in procs:
            self.assertEqual(p.exitcode, 0)

        text = journal.journal_path(self.jdir, FIXED_TS).read_text(
            encoding="utf-8")
        lines = text.splitlines()
        headers = [l for l in lines if l.startswith("## ")]
        self.assertEqual(len(headers), 100)
        for header in headers:
            self.assertRegex(header, HEADER_RE)
        # every line is a header, a detail bullet, or blank — nothing torn
        for line in lines:
            if line == "":
                continue
            self.assertTrue(
                HEADER_RE.match(line) or BULLET_RE.match(line),
                "torn/interleaved line: %r" % line)
        # 2 detail bullets per entry
        bullets = [l for l in lines if l.startswith("- ")]
        self.assertEqual(len(bullets), 200)


if __name__ == "__main__":
    unittest.main()
