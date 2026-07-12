"""R11 — transcript miner: extraction, noise policy, dedup, incremental."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import mine  # noqa: E402

SECRET = "abc123SECRET"
ENVELOPE = {"v": 1, "error": "explosion", "code": 3, "type": "ConfigError"}


def _pair(tid, command, result_text):
    """One assistant tool_use + the matching user tool_result."""
    return [
        {"type": "assistant",
         "message": {"content": [
             {"type": "tool_use", "id": tid, "name": "Bash",
              "input": {"command": command}}]}},
        {"type": "user", "timestamp": "2026-07-12T10:00:00Z",
         "gitBranch": "main",
         "message": {"content": [
             {"type": "tool_result", "tool_use_id": tid,
              "content": [{"type": "text", "text": result_text}]}]}},
    ]


def _write_jsonl(path, objs):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(o) + "\n" for o in objs),
                    encoding="utf-8")
    return path


class MineTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.cfg = fx.load_cfg(self.root)
        self.tdir = Path(self._tmp.name) / "transcripts"
        self._build_transcripts()

    def _build_transcripts(self):
        s1 = (
            _pair("t1", "python3 skills/html/scripts/x.py",
                  "boom token=%s\nExit code 2" % SECRET)
            + _pair("t2", "grep -r needle .", "Exit code 1")
            + _pair("t3", "python3 skills/pdf/scripts/y.py --json-errors",
                    "Exit code 3\n" + json.dumps(ENVELOPE))
        )
        s2 = []
        for i in range(3):
            s2 += _pair("r%d" % i, "python3 skills/xlsx/scripts/z.py",
                        "kaboom\nExit code 2")
        self.s1 = _write_jsonl(self.tdir / "s1.jsonl", s1)
        self.s2 = _write_jsonl(self.tdir / "s2.jsonl", s2)

    def _mine(self, **kwargs):
        kwargs.setdefault("transcript_dirs", [self.tdir])
        kwargs.setdefault("include_active", True)
        return mine.mine(self.cfg, **kwargs)


class TestExtraction(MineTestCase):
    def test_candidates_kinds_components_and_noise_policy(self):
        emitted, stats = self._mine(dry_run=True)
        by_component = {r["subject"]["component"]: r for r in emitted}
        # grep exit-1 dropped; html + pdf + xlsx kept
        self.assertEqual(set(by_component), {"html", "pdf", "xlsx"})
        self.assertEqual(stats["candidates"], 3)
        self.assertEqual(stats["files_scanned"], 2)

        # component inferred from the skills/ path
        html = by_component["html"]
        self.assertEqual(html["kind"], "tool-error")
        self.assertEqual(html["subject"]["exit_code"], 2)
        self.assertEqual(html["sources"], ["transcript"])

        # three same-fingerprint failures -> ONE repeated-failure, count 3
        xlsx = by_component["xlsx"]
        self.assertEqual(xlsx["kind"], "repeated-failure")
        self.assertEqual(xlsx["run"]["extra"]["count"], 3)

    def test_json_envelope_kept_and_captured(self):
        emitted, _ = self._mine(dry_run=True)
        pdf = next(r for r in emitted
                   if r["subject"]["component"] == "pdf")
        self.assertEqual(pdf["subject"]["error_envelope"], ENVELOPE)
        self.assertEqual(pdf["subject"]["message"], "explosion")

    def test_secret_redacted_in_excerpt(self):
        emitted, _ = self._mine(dry_run=True)
        html = next(r for r in emitted
                    if r["subject"]["component"] == "html")
        excerpt = html["evidence"]["excerpts"][0]["text"]
        self.assertNotIn(SECRET, excerpt)
        self.assertIn("[REDACTED]", excerpt)

    def test_secret_in_last_line_redacted_in_message(self):
        tdir = Path(self._tmp.name) / "transcripts-leak"
        _write_jsonl(tdir / "leak.jsonl",
                     _pair("t9", "python3 skills/html/scripts/x.py",
                           "Exit code 2\ntoken=%s fatal" % SECRET))
        emitted, _ = self._mine(transcript_dirs=[tdir], dry_run=True)
        self.assertEqual(len(emitted), 1)
        self.assertNotIn(SECRET, emitted[0]["subject"]["message"])

    def test_excerpt_capped_at_400_chars(self):
        tdir = Path(self._tmp.name) / "transcripts-long"
        _write_jsonl(tdir / "long.jsonl",
                     _pair("t8", "python3 skills/html/scripts/x.py",
                           ("x" * 1000) + "\nExit code 2"))
        emitted, _ = self._mine(transcript_dirs=[tdir], dry_run=True)
        excerpt = emitted[0]["evidence"]["excerpts"][0]["text"]
        self.assertLessEqual(len(excerpt), mine.EXCERPT_LIMIT)


class TestIncremental(MineTestCase):
    def test_second_run_scans_zero_new_bytes(self):
        emitted, stats = self._mine(dry_run=False)
        self.assertEqual(stats["candidates"], 3)
        self.assertTrue(Path(self.cfg.mine_state_path).is_file())

        emitted, stats = self._mine(dry_run=False)
        self.assertEqual(stats["bytes_read"], 0)
        self.assertEqual(stats["files_scanned"], 0)
        self.assertEqual(emitted, [])

    def test_truncated_file_triggers_full_rescan(self):
        self._mine(dry_run=False)
        # rewrite s1 SHORTER than the recorded offset -> size < offset
        _write_jsonl(self.s1,
                     _pair("t1", "python3 skills/html/scripts/x.py",
                           "boom\nExit code 2"))
        emitted, stats = self._mine(dry_run=False)
        self.assertEqual(stats["files_scanned"], 1)  # s2 untouched
        self.assertEqual(stats["bytes_read"], self.s1.stat().st_size)
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0]["subject"]["component"], "html")

    def test_dry_run_writes_no_state(self):
        emitted, stats = self._mine(dry_run=True)
        self.assertGreater(stats["candidates"], 0)
        self.assertFalse(Path(self.cfg.mine_state_path).exists(),
                         "--dry-run must not persist mine state")
        # and nothing was queued anywhere
        self.assertEqual(list(Path(self.cfg.inbox_dir).glob("fnd-*.json")),
                         [])


class TestActiveSessionSkip(MineTestCase):
    def test_fresh_files_skipped_without_include_active(self):
        emitted, stats = self._mine(include_active=False, dry_run=True)
        self.assertEqual(stats["files_skipped_active"], 2)
        self.assertEqual(stats["files_scanned"], 0)
        self.assertEqual(emitted, [])


if __name__ == "__main__":
    unittest.main()
