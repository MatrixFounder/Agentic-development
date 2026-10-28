"""R11 — transcript miner: extraction, noise policy, dedup, incremental."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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



class TestProjectDirectoryNaming(unittest.TestCase):
    """TASK 133 R5: the name Claude Code 2.1.306 gives a project's transcript directory, the cut
    at 200 characters, the case fold on Windows and the `cwd` filter (TC-MN1 to TC-MN5). No test
    reads the real `~/.claude/projects` (R5.6): each passes a temporary `projects_dir`, and HOME
    points at the temporary root."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name).resolve()
        home = mock.patch.dict(os.environ, {"HOME": str(self.tmp),
                                            "GIT_CEILING_DIRECTORIES": str(self.tmp)})
        home.start()
        self.addCleanup(home.stop)
        self.projects = self.tmp / "projects"
        self.projects.mkdir()

    def test_mn1_the_naming_rule_of_claude_code(self):
        """TC-MN1: each code unit outside [A-Za-z0-9] becomes `-`."""
        cyrillic = "".join(chr(0x430 + i) for i in range(12))
        cases = {
            "C:\\Users\\dev\\loyalty-api-java": "C--Users-dev-loyalty-api-java",
            "/home/u/My Project_1": "-home-u-My-Project-1",
            "/Users/sergey/Documents/Work/data/" + cyrillic:
                "-Users-sergey-Documents-Work-data-------------",
            "/a/x" + chr(0x1F600): "-a-x--",
            "/home/u/app": "-home-u-app",
        }
        for path, name in cases.items():
            self.assertEqual(mine.encode_project_dir(path), name, path)

    def test_mn2_a_long_root_matches_the_cut_name(self):
        """TC-MN2: a root of 210 characters matches its first 200, with `-` and a hash."""
        root = "/" + "a" * 209
        name = mine.encode_project_dir(root)[:200] + "-1k3x9"
        (self.projects / name).mkdir()
        self.assertEqual([d.name for d in mine.match_transcript_dirs(root, self.projects)],
                         [name])

    def test_mn3_a_drive_letter_in_other_case_matches_on_windows(self):
        """TC-MN3: with `locks.WINDOWS` set, `c:\\Users\\dev\\app` matches `C--Users-dev-app`."""
        from feedback_lib import locks
        (self.projects / "C--Users-dev-app").mkdir()
        with mock.patch.object(locks, "WINDOWS", True):
            found = mine.match_transcript_dirs("c:\\Users\\dev\\app", self.projects)
        self.assertEqual([d.name for d in found], ["C--Users-dev-app"])

    def _session(self, directory, name, cwd):
        line = {"type": "user", "message": {"content": "hi"}}
        if cwd is not None:
            line["cwd"] = cwd
        _write_jsonl(directory / name, [{"type": "summary"}, line])

    def _mine(self, root):
        cfg = fx.load_cfg(root)
        return mine.mine(cfg, projects_dir=self.projects, include_active=True, dry_run=True)

    def test_mn4_a_session_of_a_sibling_is_skipped(self):
        """TC-MN4: a session whose first `cwd` is `<r>-old` is skipped and counted; one whose
        first `cwd` is `<r>/sub` is read."""
        root = fx.make_repo(self.tmp / "r")
        own = self.projects / mine.encode_project_dir(root)
        sibling = self.projects / (mine.encode_project_dir(root) + "-old")
        self._session(own, "a.jsonl", str(root / "sub"))
        self._session(sibling, "b.jsonl", str(root) + "-old")
        _, stats = self._mine(root)
        self.assertEqual(stats["files_scanned"], 1)
        self.assertEqual(stats["files_skipped_foreign"], 1)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "makes a FIFO, which only POSIX has")
    def test_mn6_a_fifo_among_the_sessions_is_skipped(self):
        """TC-MN6: a FIFO and a directory named `*.jsonl` among the session files: a process that
        runs `mine` returns within 10 seconds, and counts neither (round 1 of stage 2, L1)."""
        import subprocess
        root = fx.make_repo(self.tmp / "r")
        own = self.projects / mine.encode_project_dir(root)
        own.mkdir()
        fifo = own / "f.jsonl"
        os.mkfifo(str(fifo))
        os.utime(str(fifo), (1, 1))
        (own / "d.jsonl").mkdir()
        script = ("import sys; sys.path.insert(0, %r); sys.path.insert(0, %r)\n"
                  "import _fixtures as fx\nfrom feedback_lib import mine\n"
                  "import json\nprint(json.dumps(mine.mine(fx.load_cfg(%r), projects_dir=%r, "
                  "include_active=True, dry_run=True)[1]))\n"
                  % (str(Path(__file__).resolve().parents[1]),
                     str(Path(__file__).resolve().parent), str(root), str(self.projects)))
        try:
            proc = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True,
                                  timeout=10, env=dict(os.environ))
        except subprocess.TimeoutExpired:
            self.fail("mine blocked on a FIFO")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        stats = json.loads(proc.stdout)
        self.assertEqual((stats["files_scanned"], stats["files_skipped_foreign"]), (0, 0))

    def test_mn7_a_cwd_in_other_case_is_read_on_windows(self):
        """TC-MN7: with `locks.WINDOWS` set, a session whose first `cwd` differs from the root in
        letter case is read."""
        from feedback_lib import locks
        root = fx.make_repo(self.tmp / "r")
        own = self.projects / mine.encode_project_dir(root)
        self._session(own, "a.jsonl", str(root).upper())
        with mock.patch.object(locks, "WINDOWS", True):
            _, stats = self._mine(root)
        self.assertEqual(stats["files_scanned"], 1)

    def test_mn8_a_session_with_no_new_bytes_is_not_counted(self):
        """TC-MN8: a session file of another root whose saved offset equals its size is skipped
        before its `cwd` is read, and is not counted."""
        root = fx.make_repo(self.tmp / "r")
        sibling = self.projects / (mine.encode_project_dir(root) + "-old")
        self._session(sibling, "old.jsonl", str(root) + "-old")
        size = (sibling / "old.jsonl").stat().st_size
        cfg = fx.load_cfg(root)
        mine.save_state(cfg.mine_state_path, {"v": mine.MINE_STATE_VERSION,
                                              "sessions": {"old": {"offset": size}}})
        _, stats = self._mine(root)
        self.assertEqual(stats["files_skipped_foreign"], 0)

    def test_mn5_a_session_with_no_cwd_is_skipped(self):
        """TC-MN5: a session file of the root's directory with no line that carries `cwd` is
        skipped and counted."""
        root = fx.make_repo(self.tmp / "r")
        own = self.projects / mine.encode_project_dir(root)
        self._session(own, "c.jsonl", None)
        _, stats = self._mine(root)
        self.assertEqual(stats["files_scanned"], 0)
        self.assertEqual(stats["files_skipped_foreign"], 1)


if __name__ == "__main__":
    unittest.main()
