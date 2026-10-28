"""TASK 133 — the Windows branches of run-feedback (R1–R4, R7, R8.1–R8.3).

The stand-in tests (TC-RF*) run the Windows branches on POSIX: a `sitecustomize.py`, written at
run time into a temporary directory on `PYTHONPATH`, blocks `import fcntl` and provides a `msvcrt`
stand-in built on `fcntl.lockf` (the method of TASK 127 R7.2). It logs each lock call with the
process, the `(st_dev, st_ino)` of the descriptor, the offset and the time, and each `os.write` on
a descriptor that `locking` has seen. They skip where `fcntl` does not import.

The encoding tests (TC-EN*) run the CLI and the hooks with `PYTHONIOENCODING` set to a code page
of Windows. The tests of TC-WN* run on Windows only.

The module imports no module of `feedback_lib` at its top, so it collects at the base.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path, PureWindowsPath
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
CLI = SCRIPTS / "run_feedback.py"
HOOK = SCRIPTS / "hooks" / "posttooluse_filter.py"
SESSION_END = SCRIPTS / "hooks" / "session_end_marker.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402

try:
    import fcntl
except ImportError:
    fcntl = None

WINDOWS = os.name == "nt"
NEEDS_STANDIN = unittest.skipIf(
    fcntl is None, "the stand-in of msvcrt is built on fcntl.lockf, which only POSIX has")
WINDOWS_ONLY = unittest.skipUnless(WINDOWS, "runs the real Windows branch")

E_ACUTE = chr(0xE9)
ARROW = chr(0x2192)
EMOJI = chr(0x1F600)
CYRILLIC = "".join(chr(c) for c in (0x442, 0x435, 0x441, 0x442))

#: The `sitecustomize.py` of the stand-in. `MSVCRT_STANDIN=1` blocks `fcntl` and provides
#: `msvcrt`; `none` blocks `fcntl` and provides nothing. `MSVCRT_STANDIN_FAIL_FROM=N` makes the
#: N-th `LK_LOCK` call and each later one raise `OSError` with `MSVCRT_STANDIN_ERRNO` (36 by
#: default, `EDEADLOCK` of the UCRT). `MSVCRT_STANDIN_NO_NOFOLLOW=1` removes `os.O_NOFOLLOW`.
SITECUSTOMIZE = r'''
import os
import sys
import time
import types

_MODE = os.environ.get("MSVCRT_STANDIN", "")
if _MODE in ("1", "none"):
    import fcntl as _real

    class _Block:
        def find_spec(self, name, path=None, target=None):
            if name == "fcntl" or (_MODE == "none" and name == "msvcrt"):
                raise ModuleNotFoundError("No module named %r" % name, name=name)
            return None

    sys.meta_path.insert(0, _Block())
    sys.modules.pop("fcntl", None)
    if os.environ.get("MSVCRT_STANDIN_NO_NOFOLLOW") == "1" and hasattr(os, "O_NOFOLLOW"):
        del os.O_NOFOLLOW

if _MODE == "1":
    # `subprocess` takes the platform for Windows when `import msvcrt` succeeds, so it is
    # imported before the stand-in is
    import subprocess  # noqa: F401

    _LOG = os.environ["MSVCRT_STANDIN_LOG"]
    _FAIL_FROM = int(os.environ.get("MSVCRT_STANDIN_FAIL_FROM", "0"))
    _ERRNO = int(os.environ.get("MSVCRT_STANDIN_ERRNO", "36"))
    _seen = set()
    _calls = [0]
    _orig_write = os.write
    _orig_close = os.close

    def _log(fields):
        fd = os.open(_LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            _orig_write(fd, (" ".join(str(f) for f in fields) + "\n").encode("utf-8"))
        finally:
            _orig_close(fd)

    def _ident(fd):
        st = os.fstat(fd)
        return "%d:%d" % (st.st_dev, st.st_ino)

    msvcrt = types.ModuleType("msvcrt")
    msvcrt.LK_UNLCK, msvcrt.LK_LOCK, msvcrt.LK_NBLCK, msvcrt.LK_RLCK, msvcrt.LK_NBRLCK = range(5)
    _NAMES = {0: "LK_UNLCK", 1: "LK_LOCK", 2: "LK_NBLCK", 3: "LK_RLCK", 4: "LK_NBRLCK"}

    def locking(fd, mode, nbytes):
        offset = os.lseek(fd, 0, os.SEEK_CUR)
        name = _NAMES.get(mode, str(mode))
        _seen.add(fd)
        if mode == msvcrt.LK_UNLCK:
            _log((name, os.getpid(), _ident(fd), offset, "%.6f" % time.time()))
            _real.lockf(fd, _real.LOCK_UN, nbytes, offset, os.SEEK_SET)
            return
        _calls[0] += 1
        if _FAIL_FROM and _calls[0] >= _FAIL_FROM:
            _log((name + "-FAIL", os.getpid(), _ident(fd), offset, "%.6f" % time.time()))
            raise OSError(_ERRNO, "stand-in lock failure")
        for _ in range(10):
            try:
                _real.lockf(fd, _real.LOCK_EX | _real.LOCK_NB, nbytes, offset, os.SEEK_SET)
            except OSError:
                time.sleep(0.2)
                continue
            _log((name, os.getpid(), _ident(fd), offset, "%.6f" % time.time()))
            return
        raise OSError(36, "Resource deadlock avoided")

    def _write(fd, data):
        if fd in _seen:
            _log(("WRITE", os.getpid(), _ident(fd), len(data), "%.6f" % time.time()))
        return _orig_write(fd, data)

    def _close(fd):
        _seen.discard(fd)
        return _orig_close(fd)

    os.write = _write
    os.close = _close
    msvcrt.locking = locking
    sys.modules["msvcrt"] = msvcrt
'''

FAILED_BASH = {"stdout": "", "stderr": "boom\nExit code 2", "interrupted": False}


def _transcript(path):
    """A session transcript that holds one failed Bash call (the form of test_hook_filter)."""
    pair = [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "t1", "name": "Bash",
             "input": {"command": "python3 skills/html/scripts/x.py"}}]}},
        {"type": "user", "timestamp": "2026-07-13T02:00:00Z",
         "message": {"content": [
             {"type": "tool_result", "tool_use_id": "t1",
              "is_error": True, "content": "boom\nExit code 2"}]}},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(o) for o in pair) + "\n", encoding="utf-8")
    return path


class _Case(unittest.TestCase):
    """A temporary root with its own `.git`, run in isolation (PLAN 133, the isolation of a run)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name).resolve()
        self.root = fx.make_repo(self.tmp / "root")
        self.site = self.tmp / "site"
        self.site.mkdir()
        (self.site / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
        self.log = self.tmp / "lock.log"
        self.body = fx.write(self.tmp / "body.md", fx.DEFECT_BODY)

    def env(self, standin="1", **extra):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("RUN_FEEDBACK_", "MSVCRT_STANDIN", "PYTHONIOENCODING"))}
        # git stops at the temporary directory, so a root whose `.git` git refuses resolves to
        # itself, not to a work tree above `TMPDIR` (round 1 of stage 2, L5)
        env.update(CLAUDE_PROJECT_DIR=str(self.root), HOME=str(self.tmp),
                   PYTHONDONTWRITEBYTECODE="1", GIT_CEILING_DIRECTORIES=str(self.tmp))
        if standin:
            env.update(PYTHONPATH=str(self.site), MSVCRT_STANDIN=standin,
                       MSVCRT_STANDIN_LOG=str(self.log))
        else:
            env.pop("PYTHONPATH", None)
        env.update({k: str(v) for k, v in extra.items()})
        return env

    def run_script(self, script, args=(), stdin=b"", **env):
        return subprocess.run([sys.executable, "-B", str(script), *[str(a) for a in args]],
                              input=stdin, capture_output=True, cwd=str(self.root),
                              env=self.env(**env), timeout=120)

    def cli(self, *args, stdin=b"", **env):
        return self.run_script(CLI, args, stdin=stdin, **env)

    def log_rows(self):
        if not self.log.is_file():
            return []
        return [line.split() for line in self.log.read_text(encoding="utf-8").splitlines()]

    def ident(self, path):
        st = os.stat(str(path))
        return "%d:%d" % (st.st_dev, st.st_ino)

    def findings(self):
        inbox = self.root / ".agent" / "feedback" / "inbox"
        return sorted(inbox.glob("fnd-*.json")) if inbox.is_dir() else []

    def journal_text(self):
        jdir = self.root / ".agent" / "feedback" / "journal"
        return "".join(p.read_text(encoding="utf-8") for p in sorted(jdir.glob("*.md"))) \
            if jdir.is_dir() else ""

    def collect(self, message="boom", **env):
        proc = self.cli("collect", "--source", "test", "--kind", "tool-error",
                        "--component", "rf", "--message", message, "--json", **env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)["finding"]["finding_id"]

    def seed_ledger(self):
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)

    def assert_no_traceback(self, proc):
        self.assertNotIn(b"Traceback", proc.stderr, proc.stderr.decode("utf-8", "replace"))


@NEEDS_STANDIN
class TestLocksUnderTheStandIn(_Case):
    """TC-RF1 to TC-RF8 and TC-RF20 (TASK 133 R1)."""

    def _sequence(self, standin):
        """Run each subcommand and both hooks; return the exit codes, in order."""
        self.seed_ledger()
        codes = []
        empty = self.tmp / ("transcripts-%s" % (standin or "posix"))
        empty.mkdir()
        for args in (("--help",), ("claim", "--run-id", "r1"), ("release", "--run-id", "r1"),
                     ("triage", "--json"),
                     ("journal", "--event-type", "heal_run", "--subject", "s"),
                     ("issues", "--json"), ("mine", "--dry-run", "--transcripts-dir", empty),
                     ("init",), ("doctor",)):
            proc = self.cli(*args, standin=standin)
            self.assert_no_traceback(proc)
            codes.append((args[0], proc.returncode))
        finding_id = self.collect(standin=standin)
        proc = self.cli("file", "--finding", finding_id, "--as", "defect", "--title", "T",
                        "--category", "correctness", "--body-file", self.body, standin=standin)
        self.assert_no_traceback(proc)
        codes.append(("file", proc.returncode))
        hook = self.run_script(HOOK, stdin=json.dumps({
            "session_id": "s1", "cwd": str(self.root), "tool_name": "Bash",
            "tool_input": {"command": "python3 x.py"}, "tool_response": FAILED_BASH}).encode(),
            standin=standin, RUN_FEEDBACK_HOOKS="1")
        codes.append(("posttooluse", hook.returncode))
        end = self.run_script(SESSION_END, stdin=json.dumps({
            "session_id": "s1", "cwd": str(self.root), "reason": "other"}).encode(),
            standin=standin, RUN_FEEDBACK_HOOKS="1")
        codes.append(("session_end", end.returncode))
        return codes

    def test_rf1_each_subcommand_and_both_hooks_exit_as_with_fcntl(self):
        """TC-RF1: with `fcntl` blocked and the stand-in present, each exit code equals that of a
        run with `fcntl`, in a twin root."""
        windows = self._sequence("1")
        windows_root = self.root
        self.root = fx.make_repo(self.tmp / "posix-root")
        posix = self._sequence("")
        self.assertEqual(windows, posix)
        self.assertEqual({code for _name, code in windows}, {0}, windows)
        self.assertTrue(any(row[0] == "LK_LOCK" for row in self.log_rows()))
        self.root = windows_root
        self.assertIn("session_end | s1", self.journal_text())
        self.assertTrue(self.findings(), "the PostToolUse hook collected nothing")

    def test_rf2_each_lock_call_is_at_offset_0(self):
        """TC-RF2: each `LK_LOCK` and `LK_UNLCK` of the log is at offset 0, and the log holds
        at least one `LK_LOCK`."""
        for args in (("claim", "--run-id", "r2"), ("release", "--run-id", "r2")):
            self.assertEqual(self.cli(*args).returncode, 0)
        self.collect()
        rows = [r for r in self.log_rows() if r[0] in ("LK_LOCK", "LK_UNLCK")]
        self.assertTrue(any(r[0] == "LK_LOCK" for r in rows), rows)
        self.assertEqual({r[3] for r in rows}, {"0"}, rows)

    def test_rf3_no_lock_module_names_both(self):
        """TC-RF3: with neither `fcntl` nor `msvcrt`, a command that locks exits 1 and names
        both modules."""
        proc = self.cli("claim", "--run-id", "r3", standin="none")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assert_no_traceback(proc)
        err = proc.stderr.decode("utf-8", "replace")
        self.assertIn("fcntl", err)
        self.assertIn("msvcrt", err)

    def test_rf4_a_held_lock_times_out(self):
        """TC-RF4: `EDEADLOCK` (errno 36) of `LK_LOCK` is a `LockTimeout`, exit 1."""
        proc = self.cli("--json-errors", "claim", "--run-id", "r4", MSVCRT_STANDIN_FAIL_FROM=1)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        envelope = json.loads(proc.stderr.decode("ascii").strip().splitlines()[-1])
        self.assertEqual(envelope["type"], "LockTimeout")
        self.assertIn("retro", envelope["error"])

    def test_rf5_the_posttooluse_hook_stays_silent_on_a_lock_timeout(self):
        """TC-RF5: the hook exits 0, writes no finding and no journal entry, and the log holds
        the `LK_LOCK` call of the collect lock."""
        proc = self.run_script(HOOK, stdin=json.dumps({
            "session_id": "s5", "cwd": str(self.root), "tool_name": "Bash",
            "tool_input": {"command": "python3 x.py"}, "tool_response": FAILED_BASH}).encode(),
            RUN_FEEDBACK_HOOKS="1", MSVCRT_STANDIN_FAIL_FROM=1)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self.findings(), [])
        self.assertEqual(self.journal_text(), "")
        lock = self.root / ".agent" / "feedback" / "inbox" / ".collect.lock"
        rows = [r for r in self.log_rows() if r[0].startswith("LK_LOCK")]
        self.assertTrue(lock.is_file())
        self.assertEqual([r[2] for r in rows], [self.ident(lock)], rows)

    def test_rf6_file_warns_when_the_journal_lock_fails_after_the_filing(self):
        """TC-RF6: the filing lock is the first `LK_LOCK` of `file`, the journal's the second.
        With the second failing, the record is filed, a warning names `finding_filed`, exit 0."""
        self.seed_ledger()
        for errno_value in (36, 13):
            with self.subTest(errno=errno_value):
                finding_id = self.collect(message="boom %d" % errno_value)
                proc = self.cli("file", "--finding", finding_id, "--as", "defect", "--title",
                                "T%d" % errno_value, "--category", "correctness", "--body-file",
                                self.body, MSVCRT_STANDIN_FAIL_FROM=2,
                                MSVCRT_STANDIN_ERRNO=errno_value)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(b"finding_filed", proc.stderr)
        self.assertEqual(len(list((self.root / "docs" / "issues").glob("*.md"))), 2)

    def test_rf7_another_errno_is_a_lock_error(self):
        """TC-RF7: an `OSError` of another errno is a `LockError`, exit 1."""
        proc = self.cli("--json-errors", "claim", "--run-id", "r7", MSVCRT_STANDIN_FAIL_FROM=1,
                        MSVCRT_STANDIN_ERRNO=13)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        envelope = json.loads(proc.stderr.decode("ascii").strip().splitlines()[-1])
        self.assertEqual(envelope["type"], "LockError")

    def test_rf8_two_appends_at_once_keep_their_locks(self):
        """TC-RF8: two journal appends at once: each takes one `LK_LOCK` and one `LK_UNLCK`,
        writes once inside its own interval, and the two intervals do not overlap."""
        cmd = [sys.executable, "-B", str(CLI), "journal", "--event-type", "heal_run",
               "--subject", "s"]
        procs = [subprocess.Popen(cmd, cwd=str(self.root), env=self.env(),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for _ in range(2)]
        for proc in procs:
            _, err = proc.communicate(timeout=120)
            self.assertEqual(proc.returncode, 0, err)
        rows = self.log_rows()
        intervals = []
        for pid in {r[1] for r in rows}:
            mine = [r for r in rows if r[1] == pid]
            kinds = [r[0] for r in mine]
            self.assertEqual(sorted(kinds), ["LK_LOCK", "LK_UNLCK", "WRITE"], mine)
            times = {r[0]: float(r[4]) for r in mine}
            self.assertLessEqual(times["LK_LOCK"], times["WRITE"])
            self.assertLessEqual(times["WRITE"], times["LK_UNLCK"])
            intervals.append((times["LK_LOCK"], times["LK_UNLCK"]))
        self.assertEqual(len(intervals), 2, rows)
        first, second = sorted(intervals)
        self.assertLessEqual(first[1], second[0])
        self.assertEqual(self.journal_text().count("heal_run | s"), 2)

    def test_rf20_session_end_on_a_lock_timeout_writes_nothing(self):
        """TC-RF20: with the mine of the hook on and the first `LK_LOCK` failing, the hook exits
        0. It writes no finding and no `mine_state.json`, and the only `LK_LOCK` of the log is the
        journal's."""
        transcript = _transcript(self.tmp / "shard" / "s20.jsonl")
        proc = self.run_script(SESSION_END, stdin=json.dumps({
            "session_id": "s20", "cwd": str(self.root), "reason": "other",
            "transcript_path": str(transcript)}).encode(),
            RUN_FEEDBACK_HOOKS="1", RUN_FEEDBACK_MINE_ON_END="1", MSVCRT_STANDIN_FAIL_FROM=1)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self.findings(), [])
        self.assertFalse((self.root / ".agent" / "feedback" / "mine_state.json").exists())
        journals = list((self.root / ".agent" / "feedback" / "journal").glob("*.md"))
        self.assertEqual(len(journals), 1)
        rows = [r for r in self.log_rows() if r[0].startswith("LK_LOCK")]
        self.assertEqual([r[2] for r in rows], [self.ident(journals[0])], rows)


class _InProcess(_Case):
    """In-process tests of `feedback_lib`; the modules import in each test, not at the top."""

    def setUp(self):
        super().setUp()
        ceiling = mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.tmp)})
        ceiling.start()
        self.addCleanup(ceiling.stop)

    def without_nofollow(self):
        if hasattr(os, "O_NOFOLLOW"):
            value = os.O_NOFOLLOW
            del os.O_NOFOLLOW
            self.addCleanup(setattr, os, "O_NOFOLLOW", value)

    def run_cli(self, *args):
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(self.root)}):
            return fx.run_cli(["--repo-root", str(self.root), *args])

    def collect_in_process(self, message="boom"):
        code, out, err = self.run_cli("collect", "--source", "test", "--kind", "tool-error",
                                      "--component", "rf", "--message", message, "--json")
        self.assertEqual(code, 0, err)
        return json.loads(out)["finding"]["finding_id"]


def _can_symlink():
    """True where this process can make a symbolic link; Windows asks for a privilege."""
    probe = Path(tempfile.mkdtemp())
    try:
        (probe / "link").symlink_to(probe / "target")
        return True
    except OSError:
        return False
    finally:
        shutil.rmtree(probe, ignore_errors=True)


class TestCreateOnlyWrite(_InProcess):
    """TC-RF9 to TC-RF12, TC-RF18 (TASK 133 R2, R3)."""

    def test_rf9_file_creates_the_record_with_lf_without_o_nofollow(self):
        """TC-RF9: with `os.O_NOFOLLOW` removed, `file` writes the record with LF line ends."""
        self.without_nofollow()
        self.seed_ledger()
        finding_id = self.collect_in_process()
        code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                    "--title", "T", "--category", "correctness",
                                    "--body-file", str(self.body))
        self.assertEqual(code, 0, err)
        records = list((self.root / "docs" / "issues").glob("*.md"))
        self.assertEqual(len(records), 1)
        data = records[0].read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertTrue(data.endswith(b"\n"))

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    @unittest.skipIf(WINDOWS, "Windows refuses to rename a file that a descriptor holds open")
    def test_rf10_a_swapped_record_path_is_refused_and_the_link_stays(self):
        """TC-RF10: a record path swapped for a link right after the open exits 4, and the link
        at the path stays."""
        self.without_nofollow()
        self.seed_ledger()
        finding_id = self.collect_in_process()
        real_open = os.open
        moved = self.tmp / "moved.md"

        def swapping_open(path, flags, *rest):
            fd = real_open(path, flags, *rest)
            text = str(path)
            if text.endswith(".md") and os.sep + "issues" + os.sep in text:
                os.rename(text, str(moved))
                os.symlink(str(moved), text)
            return fd

        with mock.patch.object(os, "open", swapping_open):
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T", "--category", "correctness",
                                        "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        self.assertIn("changed during the write", err)
        links = [p for p in (self.root / "docs" / "issues").iterdir() if p.is_symlink()]
        self.assertEqual(len(links), 1)

    @unittest.skipIf(not hasattr(os, "O_NOFOLLOW"), "pins the branch that has O_NOFOLLOW")
    def test_rf11_the_record_bytes_equal_the_record_text(self):
        """TC-RF11: with `O_NOFOLLOW`, the record's bytes equal its text, encoded with LF."""
        from feedback_lib import ledger_issues
        self.seed_ledger()
        cfg = fx.load_cfg(self.root)
        preview = ledger_issues.file_defect(cfg, "RF-2", "rf-2-x", "X", "correctness",
                                            fx.DEFECT_BODY, dry_run=True)
        ledger_issues.file_defect(cfg, "RF-2", "rf-2-x", "X", "correctness", fx.DEFECT_BODY)
        data = (self.root / "docs" / "issues" / "rf-2-x.md").read_bytes()
        self.assertEqual(data, preview["issue_text"].encode("utf-8"))

    def test_rf12_each_os_open_passes_o_binary(self):
        """TC-RF12: a stand-in value of `os.O_BINARY` reaches each of the five calls."""
        used = 0
        for name in dir(os):
            if name.startswith("O_") and isinstance(getattr(os, name), int):
                used |= getattr(os, name)
        bit = next(1 << n for n in range(20, 31) if not used & (1 << n))
        seen = []
        real_open = os.open

        def spy(path, flags, *rest):
            seen.append((str(path), bool(flags & bit)))
            return real_open(path, flags & ~bit, *rest)

        self.seed_ledger()
        with mock.patch.object(os, "O_BINARY", bit, create=True), \
                mock.patch.object(os, "open", spy):
            for args in (("claim", "--run-id", "r12"),):
                self.assertEqual(self.run_cli(*args)[0], 0)
            finding_id = self.collect_in_process()
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T", "--category", "correctness",
                                        "--body-file", str(self.body))
            self.assertEqual(code, 0, err)
        targets = {
            "retro": lambda p: os.path.basename(p) == "retro_owner",
            "collect lock": lambda p: p.endswith(".collect.lock"),
            "journal": lambda p: os.sep + "journal" + os.sep in p,
            "filing lock": lambda p: p.endswith(".filing.lock"),
            "record": lambda p: os.sep + "issues" + os.sep in p and p.endswith(".md"),
        }
        for label, match in targets.items():
            hits = [flag for path, flag in seen if match(path)]
            self.assertTrue(hits, "%s: no os.open" % label)
            self.assertTrue(all(hits), "%s: an os.open without O_BINARY" % label)

    def test_rf18_a_failed_fdopen_closes_the_descriptor_before_the_rollback(self):
        """TC-RF18: when `os.fdopen` raises, the descriptor closes before the record is
        removed."""
        from feedback_lib import ledger_core, ledger_issues
        from feedback_lib.envelope import CliError
        self.seed_ledger()
        cfg = fx.load_cfg(self.root)
        events = []
        real_close, real_unlink = os.close, os.unlink

        def fdopen(fd, *args, **kwargs):
            events.append(("fd", fd))
            raise OSError(5, "stand-in fdopen failure")

        def close(fd):
            events.append(("close", fd))
            return real_close(fd)

        def unlink(path, *args, **kwargs):
            events.append(("unlink", str(path)))
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(ledger_core.os, "fdopen", fdopen), \
                mock.patch.object(os, "close", close), mock.patch.object(os, "unlink", unlink):
            with self.assertRaises((CliError, OSError)):
                ledger_issues.file_defect(cfg, "RF-2", "rf-2-y", "Y", "correctness",
                                          fx.DEFECT_BODY)
        fd = next(v for k, v in events if k == "fd")
        record = str(self.root / "docs" / "issues" / "rf-2-y.md")
        self.assertIn(("close", fd), events)
        self.assertIn(("unlink", record), events)
        self.assertLess(events.index(("close", fd)), events.index(("unlink", record)))
        self.assertFalse(os.path.lexists(record))


class TestStateAndRollback(_InProcess):
    """TC-RF21 to TC-RF24 (TASK 133 R2.3, R3.2): the rollback after a failed write of the index,
    and no link or second hard link at a file of the machine state."""

    def _outside(self):
        outside = self.tmp / "outside.txt"
        outside.write_text("keep\n", encoding="utf-8")
        return outside

    def test_rf21_a_failed_index_write_leaves_a_foreign_file(self):
        """TC-RF21: without `O_NOFOLLOW`, the rollback after a failed write of the index keeps a
        file that took the record path."""
        from feedback_lib import ledger_issues
        self.without_nofollow()
        self.seed_ledger()
        cfg = fx.load_cfg(self.root)
        record = self.root / "docs" / "issues" / "rf-2-z.md"
        foreign = b"foreign\n"

        def failing_index(path, text, *args, **kwargs):
            # a new file made while the record still holds its number, then moved over it: the
            # two never share an identity, whatever the file system reuses
            stand_in = record.with_name("rf-2-z.md.foreign")
            stand_in.write_bytes(foreign)
            os.replace(str(stand_in), str(record))
            raise OSError(28, "stand-in: no space left on device")

        with mock.patch("feedback_lib.atomic.write_atomic", failing_index):
            with self.assertRaises(OSError):
                ledger_issues.file_defect(cfg, "RF-2", "rf-2-z", "Z", "correctness",
                                          fx.DEFECT_BODY)
        self.assertEqual(record.read_bytes(), foreign)

    def _state_cases(self):
        """(the name of a state file, the command that opens it): each command exits 4 when a
        link or a FIFO stands at that name."""
        feedback = self.root / ".agent" / "feedback"
        self.seed_ledger()
        finding_id = self.collect_in_process()
        return [
            (feedback / "retro_owner", ("claim", "--run-id", "r22")),
            (feedback / "journal" / (time.strftime("%Y-%m") + ".md"),
             ("journal", "--event-type", "heal_run", "--subject", "s")),
            (feedback / "inbox" / ".collect.lock",
             ("collect", "--source", "test", "--kind", "tool-error", "--component", "rf",
              "--message", "m22")),
            (feedback / ".filing.lock",
             ("file", "--finding", finding_id, "--as", "noise", "--reason", "r")),
        ]

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    def test_rf22_a_link_at_a_state_file_is_refused(self):
        """TC-RF22: a symbolic link at `retro_owner`, at the journal file and at both lock files:
        each command exits 4, and the link's target keeps its bytes, with `O_NOFOLLOW` (a
        process) and, where the process can drop it, without it (in this process)."""
        outside = self._outside()
        for name, args in self._state_cases():
            with self.subTest(name=name.name):
                name.parent.mkdir(parents=True, exist_ok=True)
                if os.path.lexists(str(name)):
                    os.unlink(str(name))
                os.symlink(str(outside), str(name))
                proc = self.cli(*args, standin="")
                self.assertEqual(proc.returncode, 4, proc.stderr)
                self.assertEqual(outside.read_text(encoding="utf-8"), "keep\n")
                os.unlink(str(name))
        self.without_nofollow()
        for name, args in self._state_cases():
            with self.subTest(name=name.name, nofollow=False):
                name.parent.mkdir(parents=True, exist_ok=True)
                if os.path.lexists(str(name)):
                    os.unlink(str(name))
                os.symlink(str(outside), str(name))
                self.assertEqual(self.run_cli(*args)[0], 4)
                self.assertEqual(outside.read_text(encoding="utf-8"), "keep\n")
                os.unlink(str(name))
        # a dangling link: the open would create its target, so `os.lstat` refuses it first
        retro = self.root / ".agent" / "feedback" / "retro_owner"
        target = self.tmp / "created-by-the-open"
        os.symlink(str(target), str(retro))
        self.assertEqual(self.run_cli("claim", "--run-id", "r22")[0], 4)
        self.assertFalse(target.exists(), "the open created the target of a dangling link")
        os.unlink(str(retro))
        if WINDOWS:
            return  # Windows refuses to rename a file that a descriptor holds open
        # a swap after the open: only the identity check after it sees the link
        retro.write_text("", encoding="utf-8")
        real_open = os.open

        def swapping_open(path, flags, *rest):
            fd = real_open(path, flags, *rest)
            if str(path) == str(retro):
                os.rename(str(retro), str(self.tmp / "moved-owner"))
                os.symlink(str(outside), str(retro))
            return fd

        with mock.patch.object(os, "open", swapping_open):
            self.assertEqual(self.run_cli("claim", "--run-id", "r22")[0], 4)
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep\n")

    def test_rf25_an_error_before_the_identity_removes_nothing(self):
        """TC-RF25: without `O_NOFOLLOW`, an error of the open of a record, or of its
        `os.fstat`, leaves the file at the record path."""
        from feedback_lib import ledger_issues
        self.without_nofollow()
        self.seed_ledger()
        cfg = fx.load_cfg(self.root)
        real_open, real_fstat = os.open, os.fstat
        foreign = b"foreign\n"
        for slug, case in (("rf-2-a", "open"), ("rf-2-b", "fstat")):
            record = self.root / "docs" / "issues" / (slug + ".md")

            def failing_open(path, flags, *rest):
                if str(path) == str(record):
                    record.write_bytes(foreign)
                    raise PermissionError(13, "stand-in: access denied")
                return real_open(path, flags, *rest)

            def failing_fstat(fd, *args, **kwargs):
                if case == "fstat" and os.path.exists(str(record)):
                    raise OSError(5, "stand-in: input/output error")
                return real_fstat(fd, *args, **kwargs)

            with self.subTest(case=case):
                patches = [mock.patch.object(os, "fstat", failing_fstat)] if case == "fstat" \
                    else [mock.patch.object(os, "open", failing_open)]
                with patches[0]:
                    with self.assertRaises(Exception):
                        ledger_issues.file_defect(cfg, slug.upper()[:4], slug, "A",
                                                  "correctness", fx.DEFECT_BODY)
                self.assertTrue(record.exists(), "the rollback removed the record path")
                if case == "open":
                    self.assertEqual(record.read_bytes(), foreign)

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    def test_rf26_a_link_at_a_directory_of_the_state_is_refused(self):
        """TC-RF26: a link at `journal/`, at `inbox/` and at `dismissed/` of
        `.agent/feedback/`: `claim` warns, `collect` and `file --as noise` exit 4, and the link's
        target stays empty, with `O_NOFOLLOW` (a process) and without it (in this process)."""
        feedback = self.root / ".agent" / "feedback"
        self.seed_ledger()
        for nofollow in (True, False):
            if not nofollow:
                self.without_nofollow()
            finding_id = self.collect_in_process()
            for sub, args, code in (
                    ("journal", ("claim", "--run-id", "r26"), 0),
                    ("inbox", ("collect", "--source", "test", "--kind", "tool-error",
                               "--component", "rf", "--message", "m26"), 4),
                    ("dismissed", ("file", "--finding", finding_id, "--as", "noise",
                                   "--reason", "r"), 4)):
                with self.subTest(sub=sub, nofollow=nofollow):
                    outside = self.tmp / ("outside-%s-%s" % (sub, nofollow))
                    outside.mkdir()
                    directory = feedback / sub
                    keep = None
                    if directory.exists():
                        keep = self.tmp / ("kept-%s-%s" % (sub, nofollow))
                        os.rename(str(directory), str(keep))
                    os.symlink(str(outside), str(directory))
                    if nofollow:
                        proc = self.cli(*args, standin="")
                        result, err = proc.returncode, proc.stderr.decode("utf-8", "replace")
                    else:
                        result, _, err = self.run_cli(*args)
                    self.assertEqual(result, code, err)
                    if code == 0:
                        self.assertIn("retro_claimed", err)
                        self.run_cli("release", "--run-id", "r26")
                    self.assertEqual(list(outside.iterdir()), [])
                    os.unlink(str(directory))
                    if keep is not None:
                        os.rename(str(keep), str(directory))

    def _finding_status(self, finding_id):
        path = self.root / ".agent" / "feedback" / "inbox" / (finding_id + ".json")
        return json.loads(path.read_text(encoding="utf-8"))["status"]

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    def test_rf28_file_checks_its_directories_before_any_write(self):
        """TC-RF28: a link at `filed/`: `file --as defect` exits 4, files no record and leaves
        the finding `new`. A link at `inbox/`: `file --as noise` exits 4, and the finding outside
        stays."""
        feedback = self.root / ".agent" / "feedback"
        self.seed_ledger()
        finding_id = self.collect_in_process()
        outside = self.tmp / "outside-filed"
        outside.mkdir()
        os.symlink(str(outside), str(feedback / "filed"))
        code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                    "--title", "T", "--category", "correctness",
                                    "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        issues = self.root / "docs" / "issues"
        self.assertEqual(list(issues.glob("*.md")) if issues.is_dir() else [], [])
        self.assertEqual(self._finding_status(finding_id), "new")
        self.assertEqual(list(outside.iterdir()), [])
        os.unlink(str(feedback / "filed"))
        moved = self.tmp / "outside-inbox"
        os.rename(str(feedback / "inbox"), str(moved))
        os.symlink(str(moved), str(feedback / "inbox"))
        code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "noise",
                                    "--reason", "r")
        self.assertEqual(code, 4, err)
        self.assertTrue((moved / (finding_id + ".json")).exists())
        # `consume` keeps its own check of the directory it moves a finding to
        from feedback_lib import inbox
        from feedback_lib.envelope import CliError
        os.unlink(str(feedback / "inbox"))
        os.rename(str(moved), str(feedback / "inbox"))
        os.symlink(str(outside), str(feedback / "dismissed"))
        path = feedback / "inbox" / (finding_id + ".json")
        record = json.loads(path.read_text(encoding="utf-8"))
        with self.assertRaises(CliError):
            inbox.consume(fx.load_cfg(self.root), path, record, "dismissed")
        self.assertEqual(list(outside.iterdir()), [])
        # a dangling link there meets the check before `mkdir`
        os.unlink(str(feedback / "dismissed"))
        missing = self.tmp / "missing-dismissed"
        os.symlink(str(missing), str(feedback / "dismissed"))
        with self.assertRaises(CliError):
            inbox.consume(fx.load_cfg(self.root), path, record, "dismissed")
        self.assertFalse(missing.exists())

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    def test_rf29_a_dangling_link_at_a_state_directory_is_refused(self):
        """TC-RF29: a dangling link at `journal/`: `claim` warns and exits 0; at `inbox/`:
        `collect` exits 4. Neither ends in a traceback, and no target is made."""
        feedback = self.root / ".agent" / "feedback"
        feedback.mkdir(parents=True)
        missing = self.tmp / "missing-target"
        os.symlink(str(missing), str(feedback / "journal"))
        code, _, err = self.run_cli("claim", "--run-id", "r29")
        self.assertEqual(code, 0, err)
        self.assertIn("retro_claimed", err)
        os.symlink(str(missing), str(feedback / "inbox"))
        code, _, err = self.run_cli("collect", "--source", "test", "--kind", "tool-error",
                                    "--component", "rf", "--message", "m29")
        self.assertEqual(code, 4, err)
        self.assertFalse(missing.exists())

    def test_rf30_a_late_refusal_of_the_move_marks_the_finding_filed(self):
        """TC-RF30: a `StateRefused` of the move after the ledger write runs the recovery of V17:
        exit 4, an error that names both halves, and the finding marked `filed` in place."""
        from feedback_lib import inbox
        from feedback_lib.envelope import CliError
        self.seed_ledger()
        finding_id = self.collect_in_process()
        refusal = CliError("refusing a link", code=4, err_type="StateRefused")
        with mock.patch.object(inbox, "consume", side_effect=refusal):
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T", "--category", "correctness",
                                        "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        self.assertIn("could not be moved out", err)
        self.assertEqual(self._finding_status(finding_id), "filed")

    @unittest.skipUnless(_can_symlink(), "this process cannot make a link")
    def test_rf31_file_checks_the_file_its_move_writes(self):
        """TC-RF31: a link at `filed/<finding_id>.json`: `file --as defect` exits 4, files no
        record and leaves the finding `new`. A link at `dismissed/<finding_id>.json`: `file --as
        noise` exits 4. No target is made."""
        feedback = self.root / ".agent" / "feedback"
        self.seed_ledger()
        finding_id = self.collect_in_process()
        for directory, args in (("filed", ("--as", "defect", "--title", "T", "--category",
                                           "correctness", "--body-file", str(self.body))),
                                ("dismissed", ("--as", "noise", "--reason", "r"))):
            with self.subTest(directory=directory):
                target = self.tmp / ("outside-%s.json" % directory)
                (feedback / directory).mkdir(exist_ok=True)
                link = feedback / directory / (finding_id + ".json")
                os.symlink(str(target), str(link))
                try:
                    code, _, err = self.run_cli("file", "--finding", finding_id, *args)
                finally:
                    os.unlink(str(link))
                self.assertEqual(code, 4, err)
                self.assertIn("a link, a junction", err)
                issues = self.root / "docs" / "issues"
                self.assertEqual(list(issues.glob("*.md")) if issues.is_dir() else [], [])
                self.assertEqual(self._finding_status(finding_id), "new")
                self.assertFalse(target.exists())

    def test_rf32_each_failure_of_the_move_runs_the_recovery(self):
        """TC-RF32: a `FilingConflict` of the move after the ledger write also marks the finding
        `filed` in place. When that mark is refused too, the error still names both halves."""
        from feedback_lib import atomic, inbox
        from feedback_lib.envelope import CliError
        self.seed_ledger()
        conflict = CliError("refusing to replace a link", code=4, err_type="FilingConflict")
        finding_id = self.collect_in_process()
        with mock.patch.object(inbox, "consume", side_effect=conflict):
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T", "--category", "correctness",
                                        "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        self.assertIn("could not be moved out", err)
        self.assertEqual(self._finding_status(finding_id), "filed")
        finding_id = self.collect_in_process(message="m32")
        real_write = atomic.write_atomic

        def refusing_write(path, *args, **kwargs):
            if Path(path).parent.name == "inbox":
                raise conflict
            return real_write(path, *args, **kwargs)

        refusal = CliError("refusing a link", code=4, err_type="StateRefused")
        with mock.patch.object(inbox, "consume", side_effect=refusal), \
                mock.patch.object(atomic, "write_atomic", refusing_write):
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T2", "--category", "correctness",
                                        "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        self.assertIn("could not be moved out", err)
        self.assertIn("could NOT be marked filed", err)
        self.assertEqual(self._finding_status(finding_id), "new")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "makes a FIFO, which only POSIX has")
    def test_rf27_a_fifo_at_a_state_file_is_refused(self):
        """TC-RF27: a FIFO at `retro_owner`, at the journal file and at `.collect.lock`: each
        command exits 4 within 10 seconds."""
        for name, args in self._state_cases()[:3]:
            with self.subTest(name=name.name):
                name.parent.mkdir(parents=True, exist_ok=True)
                if os.path.lexists(str(name)):
                    os.unlink(str(name))
                os.mkfifo(str(name))
                try:
                    proc = subprocess.run([sys.executable, "-B", str(CLI), *args],
                                          cwd=str(self.root), env=self.env(standin=""),
                                          capture_output=True, timeout=10)
                except subprocess.TimeoutExpired:
                    self.fail("%s blocked on a FIFO" % args[0])
                self.assertEqual(proc.returncode, 4, proc.stderr)
                os.unlink(str(name))

    def test_rf23_a_second_hard_link_of_a_record_is_refused(self):
        """TC-RF23: without `O_NOFOLLOW`, a second hard link made right after the open of a record
        exits 4, and the other link keeps the file."""
        self.without_nofollow()
        self.seed_ledger()
        finding_id = self.collect_in_process()
        real_open = os.open
        other = self.tmp / "other-link.md"

        def linking_open(path, flags, *rest):
            fd = real_open(path, flags, *rest)
            text = str(path)
            if text.endswith(".md") and os.sep + "issues" + os.sep in text:
                os.link(text, str(other))
            return fd

        with mock.patch.object(os, "open", linking_open):
            code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                        "--title", "T", "--category", "correctness",
                                        "--body-file", str(self.body))
        self.assertEqual(code, 4, err)
        self.assertTrue(other.exists())

    def test_rf24_a_hard_link_at_retro_owner_is_refused(self):
        """TC-RF24: a hard link at `retro_owner` exits 4, and the other name keeps its bytes."""
        outside = self._outside()
        feedback = self.root / ".agent" / "feedback"
        feedback.mkdir(parents=True)
        os.link(str(outside), str(feedback / "retro_owner"))
        self.assertEqual(self.run_cli("claim", "--run-id", "r24")[0], 4)
        self.assertEqual(outside.read_text(encoding="utf-8"), "keep\n")


class TestReplaceAndUnlink(_InProcess):
    """TC-RF13 to TC-RF17, TC-RF19 (TASK 133 R4)."""

    def setUp(self):
        super().setUp()
        from feedback_lib import atomic, locks
        self.atomic = atomic
        patcher = mock.patch.object(locks, "WINDOWS", True)
        patcher.start()
        self.addCleanup(patcher.stop)
        sleeper = mock.patch.object(time, "sleep", lambda seconds: None)
        sleeper.start()
        self.addCleanup(sleeper.stop)
        self.target = self.tmp / "target.txt"

    @staticmethod
    def failing(real, times, error=PermissionError):
        calls = []

        def call(*args, **kwargs):
            calls.append(args)
            if len(calls) <= times:
                raise error(13, "stand-in sharing violation")
            return real(*args, **kwargs)
        call.calls = calls
        return call

    def test_rf13_replace_retries_a_held_target(self):
        """TC-RF13: `os.replace` that fails twice and then succeeds writes the file."""
        replace = self.failing(os.replace, 2)
        with mock.patch.object(os, "replace", replace):
            self.atomic.write_atomic(self.target, "text\n")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "text\n")
        self.assertEqual(len(replace.calls), 3)

    def test_rf14_replace_gives_up_after_ten_and_removes_the_temporary_file(self):
        """TC-RF14: after ten failures the error propagates, and no temporary file stays."""
        replace = self.failing(os.replace, 99)
        with mock.patch.object(os, "replace", replace):
            with self.assertRaises(PermissionError):
                self.atomic.write_atomic(self.target, "text\n")
        self.assertEqual(len(replace.calls), 10)
        self.assertEqual(list(self.tmp.glob("target.txt.tmp.*")), [])

    def test_rf15_consume_retries_its_unlink(self):
        """TC-RF15: `consume` succeeds after two failures, and propagates after ten."""
        from feedback_lib import inbox
        cfg = fx.load_cfg(self.root)
        for times, raises in ((2, False), (99, True)):
            path = self.tmp / ("finding-%d.json" % times)
            path.write_text("{}", encoding="utf-8")
            record = {"finding_id": "fnd-20260101-000000-0000000%d" % (times % 10),
                      "status": "new"}
            unlink = self.failing(os.unlink, times)
            with mock.patch.object(os, "unlink", unlink):
                if raises:
                    with self.assertRaises(PermissionError):
                        inbox.consume(cfg, path, record, "dismissed")
                    self.assertEqual(len(unlink.calls), 10)
                    self.assertTrue(path.exists())
                else:
                    inbox.consume(cfg, path, record, "dismissed")
                    self.assertFalse(path.exists())

    def test_rf16_write_atomic_refuses_a_junction(self):
        """TC-RF16: a target whose `lstat` gives a name-surrogate reparse point is refused."""
        from feedback_lib.envelope import CliError
        self.target.write_text("old", encoding="utf-8")
        real = os.lstat(str(self.target))

        class Junction:
            st_mode = stat.S_IFDIR | 0o755
            st_file_attributes = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
            st_reparse_tag = 0xA0000003
            st_dev, st_ino, st_nlink = real.st_dev, real.st_ino, 1

        def lstat(path, *args, **kwargs):
            if str(path) == str(self.target):
                return Junction()
            return os.stat(path, follow_symlinks=False)

        with mock.patch.object(os, "lstat", lstat):
            with self.assertRaises(CliError):
                self.atomic.write_atomic(self.target, "new")
        self.assertEqual(self.target.read_text(encoding="utf-8"), "old")

    def test_rf17_cleanup_unlinks_give_up_quietly_after_ten(self):
        """TC-RF17: the unlink of the temporary file and `_rollback` succeed after two failures;
        after ten each ignores its error, the starting exception propagates, the path stays."""
        from feedback_lib import ledger_core
        for times, stays in ((2, False), (99, True)):
            unlink = self.failing(os.unlink, times)
            with mock.patch.object(os, "replace", side_effect=ValueError("boom")), \
                    mock.patch.object(os, "unlink", unlink):
                with self.assertRaises(ValueError):
                    self.atomic.write_atomic(self.target, "text")
            self.assertEqual(bool(list(self.tmp.glob("target.txt.tmp.*"))), stays)
            for leftover in self.tmp.glob("target.txt.tmp.*"):
                leftover.unlink()
            record = self.tmp / ("record-%d.md" % times)
            record.write_text("r", encoding="utf-8")
            unlink = self.failing(os.unlink, times)
            with mock.patch.object(os, "unlink", unlink):
                ledger_core._rollback(record)
            self.assertEqual(record.exists(), stays)

    def test_rf19_a_rooted_config_path_is_refused_as_relative(self):
        """TC-RF19: with `Path` of `_contained` bound to `PureWindowsPath`, `/tmp/escaped` and
        `C:docs` raise code 3 with `RELATIVE`."""
        from feedback_lib import config
        from feedback_lib.envelope import CliError
        for raw in ("/tmp/escaped", "C:docs"):
            with mock.patch.object(config, "Path", PureWindowsPath):
                with self.assertRaises(CliError) as ctx:
                    config._contained(PureWindowsPath("C:/repo"), raw, "backlog_dir", "config")
            self.assertEqual(ctx.exception.code, 3)
            self.assertIn("RELATIVE", str(ctx.exception))


class TestStreamEncoding(_Case):
    """TC-EN1 to TC-EN5 (TASK 133 R7)."""

    def test_en1_init_escapes_the_arrow_under_cp1252(self):
        """TC-EN1: `init` exits 0, and its human output holds the escape of the arrow."""
        proc = self.cli("init", standin="", PYTHONIOENCODING="cp1252")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(b"prefix\\u2192category", proc.stdout)

    def test_en2_session_end_journals_a_cyrillic_id_with_a_bom(self):
        """TC-EN2: a payload with a byte-order mark and a Cyrillic session id is journaled."""
        payload = json.dumps({"session_id": CYRILLIC, "cwd": str(self.root), "reason": "other"},
                             ensure_ascii=False).encode("utf-8")
        proc = self.run_script(SESSION_END, stdin=b"\xef\xbb\xbf" + payload, standin="",
                               RUN_FEEDBACK_HOOKS="1", PYTHONIOENCODING="cp1252")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("session_end | " + CYRILLIC, self.journal_text())

    def test_en3_collect_reads_a_cyrillic_envelope_from_stdin(self):
        """TC-EN3: `--error-envelope -` decodes stdin as UTF-8."""
        envelope = json.dumps({"v": 1, "error": CYRILLIC}, ensure_ascii=False).encode("utf-8")
        proc = self.cli("collect", "--source", "test", "--kind", "tool-error", "--component",
                        "rf", "--message", "m " + EMOJI, "--error-envelope", "-", "--json",
                        stdin=b"\xef\xbb\xbf" + envelope, standin="",
                        PYTHONIOENCODING="cp1252")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stdout.isascii())
        record = json.loads(proc.stdout.decode("ascii"))["finding"]
        self.assertEqual(record["subject"]["error_envelope"]["error"], CYRILLIC)

    def test_en4_issues_json_is_ascii_under_cp1251(self):
        """TC-EN4: `issues --json` of a record whose category holds `e` with acute is ASCII, and
        parses to the value written."""
        fx.write_issue(self.root / "docs" / "issues", "RF-1", "rf-1-x",
                       category="caf" + E_ACUTE)
        proc = self.cli("issues", "--json", standin="", PYTHONIOENCODING="cp1251")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        records = json.loads(proc.stdout.decode("ascii"))
        self.assertEqual(records[0]["category"], "caf" + E_ACUTE)

    def test_en5_triage_and_the_error_envelope_are_ascii_under_cp1252(self):
        """TC-EN5: `triage --json` with an emoji, and the `--json-errors` envelope of a path
        with `e` with acute, are ASCII and parse."""
        self.collect(message="boom " + EMOJI, standin="")
        proc = self.cli("triage", "--json", standin="", PYTHONIOENCODING="cp1252")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = json.loads(proc.stdout.decode("ascii"))
        self.assertIn(EMOJI, json.dumps(rows, ensure_ascii=False))
        missing = self.root / ("caf" + E_ACUTE + ".json")
        proc = self.cli("--json-errors", "file", "--finding", missing, "--as", "noise",
                        "--reason", "r", standin="", PYTHONIOENCODING="cp1252")
        self.assertNotEqual(proc.returncode, 0)
        envelope = json.loads(proc.stderr.decode("ascii").strip().splitlines()[-1])
        self.assertIn("caf" + E_ACUTE, envelope["error"])


    def test_en6_a_body_file_with_a_bom_files_without_it(self):
        """TC-EN6: a `--body-file` that starts with a byte-order mark files a body without it."""
        self.seed_ledger()
        body = self.tmp / "bom-body.md"
        body.write_bytes(b"\xef\xbb\xbf" + fx.DEFECT_BODY.encode("utf-8"))
        finding_id = self.collect(standin="")
        proc = self.cli("file", "--finding", finding_id, "--as", "defect", "--title", "T",
                        "--category", "correctness", "--body-file", body, standin="")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        record = next((self.root / "docs" / "issues").glob("*.md")).read_text(encoding="utf-8")
        self.assertNotIn(chr(0xFEFF), record)

    def test_en7_the_posttooluse_hook_reads_a_payload_with_a_bom(self):
        """TC-EN7: the PostToolUse hook with a byte-order mark on stdin collects its finding."""
        payload = json.dumps({"session_id": "s7", "cwd": str(self.root), "tool_name": "Bash",
                              "tool_input": {"command": "python3 x.py"},
                              "tool_response": FAILED_BASH}).encode("utf-8")
        proc = self.run_script(HOOK, stdin=b"\xef\xbb\xbf" + payload, standin="",
                               RUN_FEEDBACK_HOOKS="1", PYTHONIOENCODING="cp1252")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(len(self.findings()), 1)


@WINDOWS_ONLY
class TestOnWindows(_InProcess):
    """TC-WN1 to TC-WN5 (TASK 133 R8.3): the real branches on Windows."""

    def test_wn1_replace_waits_for_a_held_target(self):
        """TC-WN1: a target held open by another handle is replaced once that handle closes."""
        from feedback_lib import atomic
        target = self.tmp / "held.txt"
        target.write_text("old", encoding="utf-8")
        handle = open(str(target), "rb")
        threading.Timer(0.3, handle.close).start()
        atomic.write_atomic(target, "new")
        self.assertEqual(target.read_text(encoding="utf-8"), "new")

    def test_wn2_write_atomic_refuses_a_real_junction(self):
        """TC-WN2: a junction at the target is refused."""
        import _winapi
        from feedback_lib import atomic
        from feedback_lib.envelope import CliError
        inner = self.tmp / "inner"
        inner.mkdir()
        link = self.tmp / "junction"
        _winapi.CreateJunction(str(inner), str(link))
        with self.assertRaises(CliError):
            atomic.write_atomic(link, "x")

    def test_wn3_the_journal_and_a_filed_record_hold_no_cr(self):
        """TC-WN3: the bytes of a journal entry and of a filed record hold no CR."""
        self.seed_ledger()
        finding_id = self.collect_in_process()
        code, _, err = self.run_cli("file", "--finding", finding_id, "--as", "defect",
                                    "--title", "T", "--category", "correctness",
                                    "--body-file", str(self.body))
        self.assertEqual(code, 0, err)
        for path in list((self.root / "docs" / "issues").glob("*.md")) + \
                list((self.root / ".agent" / "feedback" / "journal").glob("*.md")):
            self.assertNotIn(b"\r", path.read_bytes(), path)

    def test_wn4_the_real_lock_times_out(self):
        """TC-WN4: a second process meets the held lock and exits 1 with `LockTimeout`."""
        import msvcrt
        proc = self.cli("claim", "--run-id", "w4", standin="")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        owner = self.root / ".agent" / "feedback" / "retro_owner"
        fd = os.open(str(owner), os.O_RDWR | getattr(os, "O_BINARY", 0))
        try:
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
            proc = self.cli("--json-errors", "release", "--run-id", "w4", standin="")
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        finally:
            os.close(fd)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        envelope = json.loads(proc.stderr.decode("ascii").strip().splitlines()[-1])
        self.assertEqual(envelope["type"], "LockTimeout")

    def test_wn5_a_lower_case_drive_letter_matches(self):
        """TC-WN5: `default_transcript_dirs` matches a directory named with the other case of
        the drive letter."""
        from feedback_lib import mine
        root = str(self.root)
        flipped = root[0].swapcase() + root[1:]
        projects = self.tmp / "projects"
        (projects / mine.encode_project_dir(flipped)).mkdir(parents=True)
        self.assertEqual(len(mine.default_transcript_dirs(root, projects_dir=projects)), 1)


if __name__ == "__main__":
    unittest.main()
