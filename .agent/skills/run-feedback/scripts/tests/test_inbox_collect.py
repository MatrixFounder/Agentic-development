"""R2/R3 — inbox collect: dedup-merge, atomic writes, consume moves."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import finding, inbox  # noqa: E402


class InboxTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.cfg = fx.load_cfg(self.root)

    def _finding(self, source="hook", paths=()):
        return finding.new_finding(
            source, "tool-error", "html", "conversion exploded",
            command="python3 skills/html/scripts/x.py", exit_code=2,
            evidence={"paths": list(paths)})


class TestCollect(InboxTestCase):
    def test_collect_creates_fnd_json(self):
        record, deduped = inbox.collect(self.cfg, self._finding())
        self.assertFalse(deduped)
        files = list(Path(self.cfg.inbox_dir).glob("fnd-*.json"))
        self.assertEqual(len(files), 1)
        on_disk = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(on_disk["fingerprint"], record["fingerprint"])
        self.assertEqual(on_disk["status"], "new")

    def test_second_collect_merges_by_fingerprint(self):
        inbox.collect(self.cfg, self._finding(source="hook",
                                              paths=["logs/a.log"]))
        merged, deduped = inbox.collect(
            self.cfg, self._finding(source="transcript",
                                    paths=["logs/a.log", "logs/b.log"]))
        self.assertTrue(deduped)
        self.assertEqual(merged["occurrences"], 2)
        self.assertEqual(merged["sources"], ["hook", "transcript"])
        # evidence paths union, no duplicates
        self.assertEqual(merged["evidence"]["paths"],
                         ["logs/a.log", "logs/b.log"])
        # still exactly one file in the inbox
        self.assertEqual(len(list(Path(self.cfg.inbox_dir)
                                  .glob("fnd-*.json"))), 1)

    def test_atomic_write_leaves_no_tmp_files(self):
        inbox.collect(self.cfg, self._finding())
        inbox.collect(self.cfg, self._finding(source="transcript"))
        leftovers = list(Path(self.cfg.inbox_dir).glob("*.tmp.*"))
        self.assertEqual(leftovers, [])


class TestCollectCli(InboxTestCase):
    BASE = ("collect", "--kind", "tool-error", "--component", "html",
            "--message", "conversion exploded", "--exit-code", "2")

    def test_dedup_is_idempotent_exit_0_and_sources_union(self):
        code, out, _ = fx.run_cli(["--repo-root", self.root, *self.BASE,
                                   "--source", "hook", "--json"])
        self.assertEqual(code, 0)
        first = json.loads(out)
        self.assertFalse(first["deduped"])

        code, out, _ = fx.run_cli(["--repo-root", self.root, *self.BASE,
                                   "--source", "transcript", "--json"])
        self.assertEqual(code, 0)
        second = json.loads(out)
        self.assertTrue(second["deduped"])
        self.assertEqual(second["finding"]["occurrences"], 2)
        self.assertEqual(second["finding"]["sources"],
                         ["hook", "transcript"])
        self.assertEqual(second["finding"]["fingerprint"],
                         first["finding"]["fingerprint"])


class TestConsume(InboxTestCase):
    def _collected(self):
        record, _ = inbox.collect(self.cfg, self._finding())
        path = Path(self.cfg.inbox_dir) / (record["finding_id"] + ".json")
        self.assertTrue(path.is_file())
        return path, record

    def test_consume_moves_to_filed(self):
        path, record = self._collected()
        dest = inbox.consume(self.cfg, path, record, "filed")
        self.assertTrue(Path(dest).is_file())
        self.assertEqual(Path(dest).parent, Path(self.cfg.filed_dir))
        self.assertFalse(path.exists())
        moved = json.loads(Path(dest).read_text(encoding="utf-8"))
        self.assertEqual(moved["status"], "filed")

    def test_consume_moves_to_dismissed(self):
        path, record = self._collected()
        dest = inbox.consume(self.cfg, path, record, "dismissed")
        self.assertTrue(Path(dest).is_file())
        self.assertEqual(Path(dest).parent, Path(self.cfg.dismissed_dir))
        self.assertFalse(path.exists())
        self.assertEqual(list(Path(self.cfg.inbox_dir).glob("fnd-*.json")),
                         [])


if __name__ == "__main__":
    unittest.main()
