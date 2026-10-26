"""Tests of `update_state.py`.

SS-1 regression: update_state.py must anchor .agent/sessions at the repo root regardless of the
invocation CWD (docs/issues/ss-1-*.md). TASK 127: the lock on POSIX and on Windows, UTF-8, the
escaped scalars and their round trip, and the import path (WI-39); TC-01 to TC-18 of its §5.

Each test runs the script in a temporary root that holds its own `.git`, and no test writes
under the repository. The Windows branch runs on POSIX: a test writes, into a temporary
directory, a `sitecustomize.py` that blocks `import fcntl` and provides a `msvcrt` stand-in on
`fcntl.lockf`, and puts that directory on `PYTHONPATH`. PyYAML checks each written file as a
second reader; where it does not import, each test that reaches such a check reports a skip.
"""
import ast
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path

try:
    import fcntl
except ImportError:  # Windows: the tests that hold a POSIX lock skip
    fcntl = None
try:
    import yaml
except ImportError:  # PyYAML is a second reader only
    yaml = None

SCRIPT = Path(__file__).resolve().parents[1] / "update_state.py"
ARGS = ["--mode", "Test", "--task", "t", "--status", "s", "--summary", "x"]

#: The `sitecustomize.py` of the Windows branch (TASK 127 R7.2). `MSVCRT_STANDIN=1` blocks
#: `import fcntl` and provides `msvcrt`, whose `locking` logs `<mode> <offset> <nbytes>` to
#: `MSVCRT_STANDIN_LOG` and takes `fcntl.lockf` on the same bytes. `LK_LOCK` tries
#: `MSVCRT_STANDIN_TRIES` times, like the 10 tries of the real one, and then raises `OSError`.
#: `MSVCRT_STANDIN_BLOCK` names more modules to block.
SITECUSTOMIZE = r'''
import errno
import os
import sys
import time
import types

_BLOCKED = {"fcntl"} | set(filter(None, os.environ.get("MSVCRT_STANDIN_BLOCK", "").split(",")))
for _name in _BLOCKED - {"fcntl"}:
    sys.modules.pop(_name, None)

if os.environ.get("MSVCRT_STANDIN") == "1":
    import fcntl as _real
    del sys.modules["fcntl"]
    _LOG = os.environ.get("MSVCRT_STANDIN_LOG")
    _TRIES = int(os.environ.get("MSVCRT_STANDIN_TRIES", "10"))
    msvcrt = types.ModuleType("msvcrt")
    msvcrt.LK_UNLCK, msvcrt.LK_LOCK, msvcrt.LK_NBLCK, msvcrt.LK_RLCK, msvcrt.LK_NBRLCK = range(5)

    def locking(fd, mode, nbytes):
        offset = os.lseek(fd, 0, os.SEEK_CUR)
        if _LOG:
            with open(_LOG, "a", encoding="utf-8") as fh:
                fh.write(f"{mode} {offset} {nbytes}\n")
        if mode == msvcrt.LK_UNLCK:
            _real.lockf(fd, _real.LOCK_UN, nbytes, offset, os.SEEK_SET)
            return
        for _ in range(_TRIES):
            try:
                _real.lockf(fd, _real.LOCK_EX | _real.LOCK_NB, nbytes, offset, os.SEEK_SET)
                return
            except OSError:
                time.sleep(0.05)
        raise OSError(errno.EDEADLK, "Resource deadlock avoided")

    msvcrt.locking = locking
    sys.modules["msvcrt"] = msvcrt
else:
    sys.modules.pop("fcntl", None)


class _Block:
    def find_spec(self, name, path=None, target=None):
        if name in _BLOCKED:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return None


sys.meta_path.insert(0, _Block())
'''

#: TC-09: one value per run, each a case of TASK 127 §5.
ROUND_TRIP_VALUES = [
    'q"q', "b\\b", "n\\nn",
    "l\nl", "c\rc", "t\tt", "d\x7fd", "x\x85x", "y\x93y", "z\u2028z",
    "Тест", "e\U0001F600e",
    "k: v", "# h", " lead",
    "s\udcffs",
]

#: A version 2 state file whose decision holds Cyrillic and an arrow (TC-06), and one whose
#: decision holds escaped quotes (TC-15).
V2_STATE = """schema_version: 2
session_id: "sid-127"
last_updated: "2026-10-26T00:00:00"
mode: "M"

current_task:
  name: "t"
  status: "s"
  predicted_steps: 0

context_summary: "x"

active_blockers:
  []

recent_decisions:
  - {decision}

completed_tasks:
  []
"""

#: A state file as the script before TASK 127 wrote it, with a key that a hand edit added
#: (TC-10, UC-5).
V1_STATE = r"""session_id: "old-sid"
last_updated: "2026-09-17T00:00:00"
mode: "M"

current_task:
  name: "t"
  status: "s"
  predicted_steps: 0

context_summary: "x"

current_task_2026_09_17:
  name: "TASK-029 by hand"

active_blockers:
  []

recent_decisions:
  - "say "hi""
  - "C:\new\dir"
  - "C:\new\tab"

schema_version: 2

completed_tasks:
  - "done one"
"""


def clean_env():
    """The environment of a run: no `CLAUDE_PROJECT_DIR`, which could point the script at a live
    repository, no `PYTHONPATH`, and no bytecode written."""
    env = dict(os.environ)
    for key in ("CLAUDE_PROJECT_DIR", "PYTHONPATH"):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_script(cwd, args, env_extra=None, script=SCRIPT, pythonpath=None):
    """Run the script with `args` in `cwd`; bytes out."""
    env = clean_env()
    if pythonpath is not None:
        env["PYTHONPATH"] = str(pythonpath)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(script)] + list(args), cwd=str(cwd), env=env,
                          capture_output=True, timeout=120)


def output(proc):
    """stdout and stderr of `proc` as text, for messages and assertions."""
    return (proc.stdout + proc.stderr).decode("utf-8", "backslashreplace")


def load_script(name):
    """The script as a module named `name`, compiled from its source in memory.

    `importlib`'s loader reads and writes `__pycache__/` beside the script; this neither reads
    nor writes bytecode there.
    """
    module = types.ModuleType(name)
    module.__file__ = str(SCRIPT)
    exec(compile(SCRIPT.read_bytes(), str(SCRIPT), "exec"), module.__dict__)
    return module


def json_lists(text):
    """Each list of the state file and the scalars of `current_task`, read as JSON lines.

    A reader of its own, independent of the script's parser: a list item is `  - <JSON string>`.
    """
    lists, key = {}, None
    scalars = {}
    for line in text.split("\n"):
        head = re.match(r"^(\w+):\s*$", line)
        if head:
            key = head.group(1)
            lists.setdefault(key, [])
            continue
        item = re.match(r"^  - (.*)$", line)
        if item and key:
            lists[key].append(json.loads(item.group(1)))
            continue
        field = re.match(r"^  (name|status): (.*)$", line)
        if field and key == "current_task":
            scalars[field.group(1)] = json.loads(field.group(2))
    return lists, scalars


class _RootCase(unittest.TestCase):
    """A temporary root that holds its own `.git`; the script writes its state there."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve() / "root"
        (self.root / ".git").mkdir(parents=True)
        self.sessions = self.root / ".agent" / "sessions"
        self.state = self.sessions / "latest.yaml"
        self.lock = self.sessions / "latest.yaml.lock"

    def run_ok(self, args, **kwargs):
        proc = run_script(self.root, args, **kwargs)
        self.assertEqual(proc.returncode, 0, output(proc))
        return proc

    def text(self):
        return self.state.read_bytes().decode("utf-8")

    def write_state(self, text, prefix=b""):
        self.sessions.mkdir(parents=True, exist_ok=True)
        self.state.write_bytes(prefix + text.encode("utf-8"))

    def standin(self, **env):
        """The `PYTHONPATH` directory and the environment of the Windows branch."""
        site = Path(self._tmp.name) / "site"
        site.mkdir(exist_ok=True)
        (site / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
        values = {"MSVCRT_STANDIN": "1",
                  "MSVCRT_STANDIN_LOG": str(Path(self._tmp.name) / "msvcrt.log")}
        values.update(env)
        return site, values

    def assert_yaml_equal(self, text, key, expected):
        """PyYAML yields `expected` for `key`, a dotted path. Each test calls this after its own
        checks; without PyYAML the test reports a skip, so R3.7 is not shown as checked."""
        if yaml is None:
            self.skipTest("PyYAML does not import: TASK 127 R3.7 is not checked")
        node = yaml.safe_load(text)
        for part in key.split("."):
            node = node[part]
        self.assertEqual(node, expected)


class UpdateStateAnchorTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()

    def _run(self, cwd, env_extra=None):
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        env.update(env_extra or {})
        return subprocess.run([sys.executable, str(SCRIPT)] + ARGS,
                              cwd=str(cwd), env=env, text=True,
                              capture_output=True, timeout=60)

    def _state(self, base):
        return Path(base) / ".agent" / "sessions" / "latest.yaml"

    def test_subdir_invocation_writes_to_repo_root(self):
        (self.root / ".git").mkdir()
        sub = self.root / "skills" / "some-skill"
        sub.mkdir(parents=True)
        proc = self._run(sub)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file(),
                        "state must land at the repo root")
        self.assertFalse((sub / ".agent").exists(),
                         "no stray .agent/ inside the subdir (SS-1)")

    def test_worktree_git_file_is_a_root_marker(self):
        (self.root / ".git").write_text("gitdir: /elsewhere\n",
                                        encoding="utf-8")
        sub = self.root / "sub"
        sub.mkdir()
        proc = self._run(sub)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file())
        self.assertFalse((sub / ".agent").exists())

    def test_repo_root_invocation_unchanged(self):
        (self.root / ".git").mkdir()
        proc = self._run(self.root)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(self.root).is_file())

    def test_no_git_falls_back_to_claude_project_dir(self):
        target = self.root / "proj"
        (target / ".agent").mkdir(parents=True)
        lone = self.root / "lone"
        lone.mkdir()
        proc = self._run(lone,
                         {"CLAUDE_PROJECT_DIR": str(target)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(target).is_file())
        self.assertFalse((lone / ".agent").exists())

    def test_no_git_no_env_keeps_legacy_cwd_behavior(self):
        lone = self.root / "lone"
        lone.mkdir()
        proc = self._run(lone)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self._state(lone).is_file(),
                        "zero-setup legacy fallback must keep working")

    def test_existing_state_at_root_is_merged_not_forked(self):
        (self.root / ".git").mkdir()
        first = self._run(self.root)
        self.assertEqual(first.returncode, 0, first.stderr)
        sid = self._state(self.root).read_text(encoding="utf-8")
        sub = self.root / "deep" / "er"
        sub.mkdir(parents=True)
        second = self._run(sub)
        self.assertEqual(second.returncode, 0, second.stderr)
        sid2 = self._state(self.root).read_text(encoding="utf-8")
        line = [l for l in sid.splitlines() if l.startswith("session_id:")]
        line2 = [l for l in sid2.splitlines() if l.startswith("session_id:")]
        self.assertEqual(line, line2,
                         "same session_id — subdir run updates, not forks")


@unittest.skipIf(fcntl is None, "holds a POSIX lock, or runs the Windows branch on POSIX")
class LockTestCase(_RootCase):
    """TASK 127 R1: the lock on POSIX and on Windows (TC-01 to TC-05)."""

    def test_tc01_two_runs_at_once_keep_both_tasks(self):
        procs = [subprocess.Popen([sys.executable, str(SCRIPT)] + ARGS
                                  + ["--add_completed_task", name], cwd=str(self.root),
                                  env=clean_env(), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
                 for name in ("Task A", "Task B")]
        for proc in procs:
            out, err = proc.communicate(timeout=120)
            self.assertEqual(proc.returncode, 0, (out + err).decode("utf-8", "replace"))
        lists, _ = json_lists(self.text())
        self.assertEqual(sorted(lists["completed_tasks"]), ["Task A", "Task B"])

    def test_tc02_a_held_flock_makes_the_run_wait(self):
        self.sessions.mkdir(parents=True)
        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            proc = subprocess.Popen([sys.executable, str(SCRIPT)] + ARGS, cwd=str(self.root),
                                    env=clean_env(), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            time.sleep(2)
            waiting = proc.poll() is None
            # A state that another run wrote while this one waited: the read must come after it.
            self.write_state(V2_STATE.format(decision='"kept"').replace(
                "completed_tasks:\n  []", 'completed_tasks:\n  - "written while waiting"'))
            fcntl.flock(fd, fcntl.LOCK_UN)
            out, err = proc.communicate(timeout=120)
        finally:
            os.close(fd)
        self.assertTrue(waiting, "the run did not wait for the held lock")
        self.assertEqual(proc.returncode, 0, (out + err).decode("utf-8", "replace"))
        lists, _ = json_lists(self.text())
        self.assertEqual(lists["completed_tasks"], ["written while waiting"],
                         "the run read the state before it took the lock")

    def test_tc03_windows_branch_locks_and_unlocks_byte_zero(self):
        site, env = self.standin()
        self.run_ok(ARGS, env_extra=env, pythonpath=site)
        log = Path(env["MSVCRT_STANDIN_LOG"]).read_text(encoding="utf-8").split()
        self.assertEqual(log, ["1", "0", "1", "0", "0", "1"],
                         "LK_LOCK, then LK_UNLCK, each on 1 byte at offset 0")
        self.assertTrue(self.text().startswith("schema_version: 2\n"))

    def test_tc04_windows_branch_exits_1_when_the_lock_stays_held(self):
        self.write_state(V2_STATE.format(decision='"kept"'))
        before = self.state.read_bytes()
        fd = os.open(self.lock, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.lockf(fd, fcntl.LOCK_EX, 1, 0, os.SEEK_SET)
            site, env = self.standin()
            proc = run_script(self.root, ARGS, env_extra=env, pythonpath=site)
        finally:
            os.close(fd)
        self.assertEqual(proc.returncode, 1, output(proc))
        self.assertIn("latest.yaml.lock", output(proc))
        self.assertEqual(self.state.read_bytes(), before)

    def test_tc05_no_lock_module_exits_1_and_writes_nothing(self):
        site, env = self.standin(MSVCRT_STANDIN="0", MSVCRT_STANDIN_BLOCK="msvcrt")
        proc = run_script(self.root, ARGS, env_extra=env, pythonpath=site)
        self.assertEqual(proc.returncode, 1, output(proc))
        self.assertIn("fcntl", output(proc))
        self.assertIn("msvcrt", output(proc))
        self.assertFalse((self.root / ".agent").exists(), "a file was written")
        proc = run_script(self.root, ["--help"], env_extra=env, pythonpath=site)
        self.assertEqual(proc.returncode, 0, output(proc))


class DirectoryTestCase(_RootCase):
    """TASK 127 R1.9: a session directory that another run made meanwhile (TC-18)."""

    def test_tc18_a_directory_made_meanwhile_is_no_error(self):
        # The race of R1.9 every time: the directory exists, and `os.path.exists` says it does
        # not, as when a second run creates it between the check and the creation.
        from unittest import mock
        module = load_script("update_state_tc18")
        self.sessions.mkdir(parents=True)
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            with mock.patch.dict(os.environ), mock.patch("os.path.exists", return_value=False):
                os.environ.pop("CLAUDE_PROJECT_DIR", None)
                module.ensure_session_dir()
        finally:
            os.chdir(cwd)
        self.assertTrue(self.sessions.is_dir())


class EncodingTestCase(_RootCase):
    """TASK 127 R2: UTF-8 on every platform (TC-06 to TC-08, TC-11, TC-15)."""

    #: A locale whose encoding is ASCII on Linux and macOS (TASK 127 R7.3).
    ASCII_LOCALE = {"LC_ALL": "C", "LANG": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}

    def test_tc06_cyrillic_state_survives_an_ascii_locale(self):
        self.write_state(V2_STATE.format(decision='"решение → ok"'))
        self.run_ok(ARGS, env_extra=self.ASCII_LOCALE)
        lists, _ = json_lists(self.text())
        self.assertEqual(lists["recent_decisions"], ["решение → ok"])
        self.assert_yaml_equal(self.text(), "recent_decisions", ["решение → ok"])

    def test_tc07_each_open_names_its_encoding(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == "open"]
        self.assertTrue(calls)
        for call in calls:
            keywords = {kw.arg: kw.value for kw in call.keywords}
            mode = call.args[1] if len(call.args) > 1 else keywords.get("mode")
            mode = mode.value if isinstance(mode, ast.Constant) else "r"
            encoding = keywords.get("encoding")
            self.assertIsInstance(encoding, ast.Constant, f"line {call.lineno}: no encoding")
            if "w" in mode:
                self.assertEqual(encoding.value, "utf-8", f"line {call.lineno}")
                newline = keywords.get("newline")
                self.assertIsInstance(newline, ast.Constant, f"line {call.lineno}: no newline")
                self.assertEqual(newline.value, "\n", f"line {call.lineno}")
            else:
                self.assertEqual(encoding.value, "utf-8-sig", f"line {call.lineno}")

    def test_tc08_messages_survive_an_ascii_pipe(self):
        root = Path(self._tmp.name).resolve() / "корень"
        (root / ".git").mkdir(parents=True)
        proc = run_script(root, ARGS, env_extra={"PYTHONIOENCODING": "ascii"})
        self.assertEqual(proc.returncode, 0, output(proc))
        self.assertNotIn("Traceback", output(proc))

    def test_tc11_a_state_file_that_is_not_utf8_stops_the_run(self):
        self.sessions.mkdir(parents=True)
        before = b'session_id: "x"\nmode: "\xff\xfe"\n'
        self.state.write_bytes(before)
        proc = run_script(self.root, ARGS)
        self.assertEqual(proc.returncode, 1, output(proc))
        self.assertIn(str(self.state), output(proc))
        self.assertIn("UTF-8", output(proc))
        self.assertEqual(self.state.read_bytes(), before)

    def test_tc15_a_byte_order_mark_does_not_hide_version_2(self):
        # An ASCII-only JSON string escapes `é` and `→`. A version 2 read decodes the
        # escapes, and the write stores the characters; a version 1 read keeps them as text.
        self.write_state(V2_STATE.format(decision=json.dumps("café → ok")),
                         prefix=b"\xef\xbb\xbf")
        self.run_ok(ARGS)
        raw = self.state.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertIn('  - "café → ok"\n', raw.decode("utf-8"))


class ScalarTestCase(_RootCase):
    """TASK 127 R3: escaped scalars and a stable round trip (TC-09, TC-10, TC-14, TC-16)."""

    def test_tc09_sixteen_runs_keep_every_value(self):
        for value in ROUND_TRIP_VALUES:
            self.run_ok(["--mode", "M", "--task", value, "--status", value, "--summary", "x",
                         "--add_blocker", value, "--add_decision", value,
                         "--add_completed_task", value])
        text = self.text()
        lists, scalars = json_lists(text)
        self.assertEqual(lists["active_blockers"], ROUND_TRIP_VALUES)
        self.assertEqual(lists["completed_tasks"], ROUND_TRIP_VALUES)
        self.assertEqual(lists["recent_decisions"], ROUND_TRIP_VALUES[-10:])
        self.assertEqual(scalars, {"name": ROUND_TRIP_VALUES[-1],
                                   "status": ROUND_TRIP_VALUES[-1]})
        self.assert_yaml_equal(text, "active_blockers", ROUND_TRIP_VALUES)
        self.assert_yaml_equal(text, "completed_tasks", ROUND_TRIP_VALUES)
        self.assert_yaml_equal(text, "recent_decisions", ROUND_TRIP_VALUES[-10:])
        self.assert_yaml_equal(text, "current_task.name", ROUND_TRIP_VALUES[-1])
        self.assert_yaml_equal(text, "current_task.status", ROUND_TRIP_VALUES[-1])

    def test_tc10_an_old_file_keeps_its_strings(self):
        self.write_state(V1_STATE)
        self.run_ok(ARGS)
        text = self.text()
        self.assertTrue(text.startswith("schema_version: 2\n"))
        lists, _ = json_lists(text)
        self.assertEqual(lists["recent_decisions"],
                         ['say "hi"', "C:\\new\\dir", "C:\\new\\tab"])
        self.assertEqual(lists["completed_tasks"], ["done one"])
        self.assertIn('session_id: "old-sid"', text)
        self.assertNotIn("current_task_2026_09_17", text)
        self.assert_yaml_equal(text, "recent_decisions",
                               ['say "hi"', "C:\\new\\dir", "C:\\new\\tab"])

    def test_tc14_a_summary_of_two_lines_is_one_scalar(self):
        self.run_ok(["--mode", "M", "--task", "t", "--status", "s",
                     "--summary", "line one\nline two"])
        text = self.text()
        line = [l for l in text.split("\n") if l.startswith("context_summary: ")]
        self.assertEqual(len(line), 1)
        self.assertEqual(json.loads(line[0][len("context_summary: "):]), "line one\nline two")
        self.run_ok(["--mode", "M", "--task", "t", "--status", "s", "--summary", "  padded  "])
        self.assertIn('context_summary: "padded"\n', self.text())
        self.assert_yaml_equal(text, "context_summary", "line one\nline two")

    def test_tc17_the_merge_rules(self):
        self.run_ok(ARGS + ["--add_blocker", "", "--add_decision", ""])
        lists, _ = json_lists(self.text())
        self.assertEqual((lists["active_blockers"], lists["recent_decisions"]), ([], []))
        for _ in range(2):
            self.run_ok(ARGS + ["--add_blocker", "B", "--add_completed_task", "T"])
        lists, _ = json_lists(self.text())
        self.assertEqual(lists["active_blockers"], ["B"])
        self.assertEqual(lists["completed_tasks"], ["T"])

    def test_tc16_an_empty_task_name(self):
        self.run_ok(["--mode", "M", "--task", "", "--status", "s", "--summary", "x"])
        _, scalars = json_lists(self.text())
        self.assertEqual(scalars["name"], "")
        self.assert_yaml_equal(self.text(), "current_task.name", "")


class ImportPathTestCase(_RootCase):
    """TASK 127 R6, WI-39: no module planted beside the script runs (TC-12, TC-13)."""

    #: Modules that a planted file cannot shadow: built into the interpreter, or imported
    #: before the script runs.
    PRELOADED = ("os", "sys")

    def planted_names(self):
        """Each module that the script imports, by its AST, and `msvcrt` and `_winapi`."""
        names = {"msvcrt", "_winapi"}
        for node in ast.walk(ast.parse(SCRIPT.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names.add(node.module.split(".")[0])
        return sorted(names - set(self.PRELOADED))

    def test_tc12_a_planted_module_is_not_imported(self):
        base = Path(self._tmp.name).resolve()
        scripts = base / "copy" / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "update_state.py").write_bytes(SCRIPT.read_bytes())
        markers = base / "markers"
        markers.mkdir()
        planted = self.planted_names()
        self.assertIn("datetime", planted)
        self.assertIn("json", planted)
        for name in planted:
            if name == "datetime":
                continue
            (scripts / f"{name}.py").write_text(
                f"open({str(markers / name)!r}, 'w').close()\n", encoding="utf-8")
        source = base / "datetime_source.py"
        source.write_text(f"open({str(markers / 'datetime')!r}, 'w').close()\n",
                          encoding="utf-8")
        py_compile.compile(str(source), cfile=str(scripts / "datetime.pyc"), doraise=True)
        source.unlink()
        runs = [scripts / "update_state.py"]
        link = base / "link"
        try:
            os.symlink(scripts, link, target_is_directory=True)
            runs.append(link / "update_state.py")
        except (OSError, NotImplementedError):  # no symbolic link on this host
            pass
        # A case-insensitive volume reaches the copy through other letter case, and the path as
        # called then differs from the real one (security audit S-1).
        variant = base / "COPY" / "scripts" / "update_state.py"
        if variant.exists():
            runs.append(variant)
        # A linked file leaves the link's own directory on `sys.path` on Windows; the modules
        # planted there must not run either.
        linked = base / "linked"
        linked.mkdir()
        for name in planted:
            if name != "datetime":
                (linked / f"{name}.py").write_text(
                    f"open({str(markers / name)!r}, 'w').close()\n", encoding="utf-8")
        try:
            os.symlink(scripts / "update_state.py", linked / "update_state.py")
            runs.append(linked / "update_state.py")
        except (OSError, NotImplementedError):
            pass
        for script in runs:
            proc = run_script(self.root, ARGS, script=script)
            self.assertEqual(proc.returncode, 0, output(proc))
            self.assertEqual(sorted(p.name for p in markers.iterdir()), [],
                             f"a module planted beside {script} was imported")

    def test_tc13_a_module_import_keeps_sys_path(self):
        before = list(sys.path)
        module = load_script("update_state_under_test")
        self.assertEqual(sys.path, before)
        self.assertTrue(callable(module.parse_simple_yaml))


if __name__ == "__main__":
    unittest.main()
