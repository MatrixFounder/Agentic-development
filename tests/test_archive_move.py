"""The archive script moves TASK and PLAN into their archive directories only (TASK 112 R1).

Before TASK 112 two allow rules, `Bash(mv docs/TASK.md docs/tasks/*)` and
`Bash(mv docs/PLAN.md docs/plans/*)`, approved any text after their prefix:
`mv docs/TASK.md docs/tasks/../../x` and extra source operands among it. One rule now names
`.agent/tools/archive_move.py`, and the script is the guard. This file pins:

* each of the two pairs moves its file, and the destination directory is created when absent
  (``TC-A1``, ``TC-A2``);
* an existing destination, a link in its place, a linked directory, a linked source, a linked
  `docs` and an absent source are refused with no change on disk (``TC-A3`` to ``TC-A6``,
  ``TC-A9``, ``TC-A10``);
* a destination of any other shape is refused (``TC-A7``); a wrong operand count or an option
  exits 2 (``TC-A8``);
* the copy path used where the file system refuses a hard link moves the file, and refuses a
  destination that appears meanwhile (``TC-A11``);
* a source with a second hard link is refused (``TC-A12``), and a source that cannot be removed
  leaves no destination behind (``TC-A13``);
* an overlong name is a refusal with a JSON error, not a traceback (``TC-A14``);
* a source swapped during the move is refused on the link path and on the copy path, and a failed
  copy leaves no destination (``TC-A15`` to ``TC-A18``);
* a failed check after the link leaves no destination; a module planted beside the script is not
  imported, through a path in other letter case either (ARC-13, TASK 128), and loading the script
  keeps the caller's `sys.path`; a source that vanishes before
  its unlink, holds another file then, or cannot be checked, leaves the archive in place
  (``TC-A19`` to ``TC-A23``);
* an existing letter-suffixed sub-task file in the destination's place is refused (``TC-A24``,
  TASK 114);
* on a platform without `dir_fd`, Windows among them, the move copies by path: it refuses a link,
  a junction, a read-only source and a source with a second hard link; it keeps the archive when
  the source changed after the copy; it tries an unlink 10 times; it keeps every byte; and each of
  its opens passes `O_BINARY` (``TC-W1`` to ``TC-W10``, ``TC-W21`` to ``TC-W24``, TASK 131 R1).

A test that patches the descriptors of `_move` skips where `_supported()` is false, and a test
that makes a symbolic link skips where this process cannot make one (TASK 131 R6.5).

Each case runs the script with the `realpath` of a temporary root as its working directory;
TC-A11, TC-A13 and TC-A15 to TC-A18 call `main(argv)` in-process to replace `os.link`, `os.unlink`
or `os.write`; the TC-W tests call it in-process with `_supported` patched to return false.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
TASK = "docs/TASK.md"
PLAN = "docs/PLAN.md"
TASK_DEST = "docs/tasks/task-112-x.md"
PLAN_DEST = "docs/plans/plan-112-x.md"


def _load():
    spec = importlib.util.spec_from_file_location("archive_move_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


NEEDS_SYMLINK = unittest.skipUnless(_can_symlink(), "this process cannot make a symbolic link")
NEEDS_DIR_FD = unittest.skipUnless(_load()._supported(),
                                   "it patches the descriptors of `_move`, which need `dir_fd`")
WINDOWS_ONLY = unittest.skipUnless(os.name == "nt", "a behaviour of Windows")
#: The reparse tags of a junction, of a symbolic link and of a cloud placeholder (TASK 128 R2.2).
JUNCTION, SYMLINK, CLOUD = 0xA0000003, 0xA000000C, 0x9000001A


def _fake_stat(real, **extra):
    """The fields of `real`, with the attributes of Windows that `extra` names."""
    fields = {name: getattr(real, name) for name in dir(real) if name.startswith("st_")}
    fields.setdefault("st_file_attributes", 0)
    fields.setdefault("st_reparse_tag", 0)
    fields.update(extra)
    return types.SimpleNamespace(**fields)


def _lstat_reporting(paths, **extra):
    """A patch of `os.lstat` that reports `extra` for each path of `paths`."""
    real = os.lstat

    def lstat(path, *args, **kwargs):
        st = real(path, *args, **kwargs)
        return _fake_stat(st, **extra) if os.fspath(path) in paths else st
    return mock.patch("os.lstat", side_effect=lstat)


def _unused_open_bit():
    """A bit that no `os.O_*` flag of this platform uses."""
    used = 0
    for name in dir(os):
        if name.startswith("O_"):
            used |= getattr(os, name)
    return next(1 << bit for bit in range(30, 15, -1) if not used & (1 << bit))


@contextlib.contextmanager
def _no_o_nofollow():
    """`os.O_NOFOLLOW` deleted, as on Windows, for the time of the block."""
    saved = getattr(os, "O_NOFOLLOW", None)
    if saved is not None:
        del os.O_NOFOLLOW
    try:
        yield
    finally:
        if saved is not None:
            os.O_NOFOLLOW = saved


def _junction(link, target):
    """A junction at `link` to the directory `target` (Windows only), as CPython's tests make it."""
    import _winapi
    _winapi.CreateJunction(str(target), str(link))


class ArchiveTestCase(unittest.TestCase):

    def setUp(self):
        self.root = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "docs").mkdir()
        self.write(TASK, "# task\n")
        self.write(PLAN, "# plan\n")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        # TASK 131 D26: LF on every platform, so a test may compare the bytes.
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=60)

    def run_in_process(self, *args):
        """`(exit code, the JSON object printed)`."""
        module = _load()
        out, err = io.StringIO(), io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = module.main(list(args))
        finally:
            os.chdir(cwd)
        return code, json.loads(out.getvalue() or err.getvalue())

    def tree(self):
        """Every path under the root, links shown by their target."""
        entries = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            for name in sorted(dirnames + filenames):
                path = Path(dirpath) / name
                rel = path.relative_to(self.root).as_posix()
                if path.is_symlink():
                    entries.append((rel, "->" + os.readlink(path)))
                elif path.is_file():
                    entries.append((rel, path.read_text(encoding="utf-8")))
                else:
                    entries.append((rel, "/"))
        return sorted(entries)

    def assertRefused(self, args, code=1):
        before = self.tree()
        result = self.run_script(*args)
        self.assertEqual(result.returncode, code, result.stderr)
        report = json.loads(result.stderr)
        self.assertFalse(report["ok"])
        self.assertEqual(self.tree(), before, "a refusal changed the disk")
        return report


class TestMoves(ArchiveTestCase):
    """TC-A1, TC-A2."""

    def test_a1_task_moves_into_a_new_tasks_directory(self):
        # base-fail: the script is absent at the base.
        result = self.run_script(TASK, TASK_DEST)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / TASK).exists())
        self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual((report["source"], report["destination"]), (TASK, TASK_DEST))
        self.assertTrue(report["created_directory"])
        self.assertEqual(os.stat(self.root / TASK_DEST).st_nlink, 1)

    def test_a2_plan_moves_into_an_existing_plans_directory(self):
        (self.root / "docs" / "plans").mkdir()
        result = self.run_script(PLAN, PLAN_DEST)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / PLAN).exists())
        self.assertEqual((self.root / PLAN_DEST).read_text(encoding="utf-8"), "# plan\n")
        self.assertFalse(json.loads(result.stdout)["created_directory"])


class TestRefusals(ArchiveTestCase):
    """TC-A3 to TC-A10, TC-A12, TC-A24."""

    def test_a3_an_existing_destination_is_kept(self):
        self.write(TASK_DEST, "# older\n")
        self.assertRefused((TASK, TASK_DEST))

    @NEEDS_SYMLINK
    def test_a4_a_link_in_place_of_the_destination(self):
        outside = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, outside)
        target = outside / "victim.md"
        target.write_text("victim\n", encoding="utf-8")
        (self.root / "docs" / "tasks").mkdir()
        for name, points_to in (("dangling", outside / "absent.md"), ("to-file", target)):
            with self.subTest(link=name):
                link = self.root / TASK_DEST
                if link.is_symlink():
                    link.unlink()
                link.symlink_to(points_to)
                self.assertRefused((TASK, TASK_DEST))
                self.assertEqual(target.read_text(encoding="utf-8"), "victim\n")
                self.assertFalse((outside / "absent.md").exists())

    @NEEDS_SYMLINK
    def test_a5_a_linked_tasks_directory(self):
        outside = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, outside)
        (self.root / "docs" / "tasks").symlink_to(outside, target_is_directory=True)
        self.assertRefused((TASK, TASK_DEST))
        self.assertEqual(os.listdir(outside), [])

    @NEEDS_SYMLINK
    def test_a6_a_linked_source(self):
        real = self.write("elsewhere.md", "# elsewhere\n")
        (self.root / TASK).unlink()
        (self.root / TASK).symlink_to(real)
        self.assertRefused((TASK, TASK_DEST))

    def test_a7_a_destination_of_another_shape(self):
        for source, destination in (
            (TASK, "docs/tasks/../x.md"),
            (TASK, str(self.root / TASK_DEST)),
            (TASK, "docs/tasks/sub/task-112-x.md"),
            (TASK, PLAN_DEST),
            (TASK, "docs/tasks/x.md"),
            (TASK, "docs/tasks/task-12-x.md"),
            (TASK, "./" + TASK_DEST),
            (TASK, "docs/tasks/task-112-X.md"),
            (TASK, "docs/tasks/task-112-x.md.bak"),
            (TASK, "docs/plans/task-112-x.md"),
            (PLAN, TASK_DEST),
            (PLAN, "docs/plans/plan-112-.md"),
            ("./" + TASK, TASK_DEST),
            ("docs/ARCHITECTURE.md", TASK_DEST),
        ):
            with self.subTest(source=source, destination=destination):
                self.assertRefused((source, destination))

    def test_a8_usage_errors_exit_2(self):
        for args in ((TASK,), (TASK, TASK_DEST, PLAN), ("-f", TASK_DEST), (TASK, "--help"), ()):
            with self.subTest(args=args):
                self.assertRefused(args, code=2)

    @NEEDS_SYMLINK
    def test_a9_a_linked_docs_directory(self):
        real = self.root / "real-docs"
        (self.root / "docs").rename(real)
        (self.root / "docs").symlink_to(real, target_is_directory=True)
        self.assertRefused((TASK, TASK_DEST))

    def test_a10_an_absent_source_creates_no_directory(self):
        (self.root / TASK).unlink()
        self.assertRefused((TASK, TASK_DEST))
        self.assertFalse((self.root / "docs" / "tasks").exists())

    def test_a12_a_source_with_a_second_hard_link(self):
        os.link(self.root / TASK, self.root / "alias.md")
        report = self.assertRefused((TASK, TASK_DEST))
        self.assertIn("hard links", report["error"], "refused before the link, by the source check")

    def test_a24_an_existing_letter_suffixed_subtask_is_kept(self):
        # TASK 114 R4: the guard is the destination's existence, not its name; a name rule would
        # also refuse the new parent archive `task-012-3d-viewer.md`.
        self.write("docs/tasks/task-112-05a-x.md", "# Task 112-05a: a planner sub-task\n")
        self.assertRefused((TASK, "docs/tasks/task-112-05a-x.md"))

    def test_a14_an_overlong_name_is_a_refusal(self):
        report = self.assertRefused((TASK, "docs/tasks/task-112-" + "a" * 300 + ".md"))
        self.assertIn("error", report)
        self.assertFalse((self.root / "docs" / "tasks").exists())


class TestFallbacks(ArchiveTestCase):
    """TC-A11, TC-A13: in-process, with `os.link` or `os.unlink` replaced."""

    def test_a11_copy_path_moves_the_file(self):
        with mock.patch("os.link", side_effect=PermissionError(1, "no hard links here")):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 0)
        self.assertEqual(report["method"], "copy")
        self.assertFalse((self.root / TASK).exists())
        self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")

    @NEEDS_DIR_FD
    def test_a11_copy_path_refuses_a_destination_that_appeared(self):
        racer = self.root / TASK_DEST

        def link_then_fail(*_args, **_kwargs):
            racer.write_text("# racer\n", encoding="utf-8")
            raise PermissionError(1, "no hard links here")

        (self.root / "docs" / "tasks").mkdir()
        with mock.patch("os.link", side_effect=link_then_fail):
            code, _ = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")
        self.assertEqual(racer.read_text(encoding="utf-8"), "# racer\n")

    @NEEDS_DIR_FD
    def test_a13_a_source_that_cannot_be_removed_leaves_no_destination(self):
        real_unlink = os.unlink

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == "TASK.md":
                raise PermissionError(1, "read-only")
            return real_unlink(name, *args, **kwargs)

        with mock.patch("os.unlink", side_effect=unlink):
            code, _ = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertFalse((self.root / "docs" / "tasks").exists(),
                         "the directory the run created stays behind")


class TestSwappedSource(ArchiveTestCase):
    """TC-A15 to TC-A18: the checks that hold when the source changes during the move (R1.3)."""

    def swap(self, kind):
        """Replace `docs/TASK.md` by another regular file or by a link to one outside the root."""
        source = self.root / TASK
        source.unlink()
        if kind == "file":
            source.write_text("# swapped\n", encoding="utf-8")
        else:
            outside = Path(os.path.realpath(tempfile.mkdtemp()))
            self.addCleanup(shutil.rmtree, outside)
            (outside / "secret.md").write_text("secret\n", encoding="utf-8")
            source.symlink_to(outside / "secret.md")

    @NEEDS_DIR_FD
    def test_a15_link_path_refuses_a_swapped_source(self):
        real_link = os.link

        def swap_then_link(*args, **kwargs):
            self.swap("file")
            return real_link(*args, **kwargs)

        with mock.patch("os.link", side_effect=swap_then_link):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("changed", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# swapped\n")

    @NEEDS_DIR_FD
    def test_a16_copy_path_refuses_a_swapped_regular_file(self):
        def swap_then_fail(*_args, **_kwargs):
            self.swap("file")
            raise PermissionError(1, "no hard links here")

        with mock.patch("os.link", side_effect=swap_then_fail):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("changed", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())

    @NEEDS_DIR_FD
    def test_a17_copy_path_never_opens_a_link(self):
        def swap_then_fail(*_args, **_kwargs):
            self.swap("link")
            raise PermissionError(1, "no hard links here")

        with mock.patch("os.link", side_effect=swap_then_fail):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("cannot open docs/TASK.md", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())

    def test_a18_a_failed_copy_leaves_no_destination(self):
        with mock.patch("os.link", side_effect=PermissionError(1, "no hard links here")), \
                mock.patch("os.write", side_effect=OSError(28, "No space left on device")):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("cannot copy", report["error"])
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertFalse((self.root / "docs" / "tasks").exists())


class TestLastSteps(ArchiveTestCase):
    """TC-A19 to TC-A21 (TASK 112 fix round 2)."""

    @NEEDS_DIR_FD
    def test_a19_a_failed_check_after_the_link_leaves_no_destination(self):
        real_link, real_stat, linked = os.link, os.stat, []

        def link(*args, **kwargs):
            linked.append(True)
            return real_link(*args, **kwargs)

        def stat(name, *args, **kwargs):
            if linked and os.fspath(name) == "task-112-x.md":
                raise OSError(5, "Input/output error")
            return real_stat(name, *args, **kwargs)

        with mock.patch("os.link", side_effect=link), mock.patch("os.stat", side_effect=stat):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("cannot check the destination", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")

    def test_a20_a_module_beside_the_script_is_not_imported(self):
        tools = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, tools)
        shutil.copyfile(SCRIPT, tools / "archive_move.py")
        marker = self.root / "planted-module-ran"
        (tools / "json.py").write_text(f"open({str(marker)!r}, 'w').close()\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(tools / "archive_move.py"), TASK, TASK_DEST],
                                cwd=self.root, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists(), "the planted json.py ran")

    def test_a20_a_module_beside_the_script_through_other_letter_case(self):
        # ARC-13: a volume that ignores letter case reaches the copy through a path in other case,
        # and the path as called then differs from the real one (TASK 128 R1.3).
        tools = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, tools)
        shutil.copyfile(SCRIPT, tools / "archive_move.py")
        marker = self.root / "planted-module-ran"
        (tools / "json.py").write_text(f"open({str(marker)!r}, 'w').close()\n", encoding="utf-8")
        variant = tools.parent / tools.name.swapcase() / "archive_move.py"
        if not variant.exists():
            self.skipTest("the volume tells letter case apart")
        result = subprocess.run([sys.executable, str(variant), TASK, TASK_DEST],
                                cwd=self.root, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists(), "the planted json.py ran through other letter case")

    def test_a20_loading_the_script_keeps_the_callers_path(self):
        before = list(sys.path)
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            _load()
            self.assertEqual(sys.path, [str(SCRIPT.parent)] + before)
        finally:
            sys.path[:] = before

    @NEEDS_DIR_FD
    def test_a21_a_vanished_source_keeps_the_archive(self):
        real_unlink = os.unlink

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == "TASK.md":
                real_unlink(name, *args, **kwargs)  # another process removed it first
                raise FileNotFoundError(2, "No such file or directory")
            return real_unlink(name, *args, **kwargs)

        with mock.patch("os.unlink", side_effect=unlink):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("kept", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")

    @NEEDS_DIR_FD
    def test_a22_a_source_swapped_before_its_unlink_keeps_the_archive(self):
        real_unlink = os.unlink

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == "TASK.md":
                source = self.root / TASK
                real_unlink(source)
                source.write_text("# another\n", encoding="utf-8")
                raise PermissionError(1, "Operation not permitted")
            return real_unlink(name, *args, **kwargs)

        with mock.patch("os.unlink", side_effect=unlink):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("kept", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# another\n")

    @NEEDS_DIR_FD
    def test_a23_an_unconfirmed_source_keeps_both_names(self):
        real_unlink, real_stat, failed = os.unlink, os.stat, []

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == "TASK.md":
                failed.append(True)
                raise PermissionError(1, "Operation not permitted")
            return real_unlink(name, *args, **kwargs)

        def stat(name, *args, **kwargs):
            if failed and os.fspath(name) == "TASK.md":
                raise OSError(5, "Input/output error")
            return real_stat(name, *args, **kwargs)

        with mock.patch("os.unlink", side_effect=unlink), mock.patch("os.stat", side_effect=stat):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("both it and", report["error"])
        self.assertEqual((self.root / TASK).read_text(encoding="utf-8"), "# task\n")
        self.assertEqual((self.root / TASK_DEST).read_text(encoding="utf-8"), "# task\n")


class TestMoveByPath(ArchiveTestCase):
    """TC-W1 to TC-W10, TC-W21 to TC-W24 (TASK 131 R1): the move on a platform without `dir_fd`.

    Each test calls `main` in the test process with `_supported` patched to return false, the
    branch that Windows takes (TASK 131 R6.2), and with `time.sleep` patched out of the tries.
    """

    def by_path(self, *args, patches=(), module=None):
        """`(exit code, the JSON object printed)` of `main` with `_supported` false."""
        module = module or _load()
        out, err = io.StringIO(), io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(module, "_supported", return_value=False))
                stack.enter_context(mock.patch("time.sleep"))
                for patch in patches:
                    stack.enter_context(patch)
                stack.enter_context(contextlib.redirect_stdout(out))
                stack.enter_context(contextlib.redirect_stderr(err))
                code = module.main(list(args))
        finally:
            os.chdir(cwd)
        return code, json.loads(out.getvalue() or err.getvalue())

    def refused_by_path(self, args, message, patches=()):
        before = self.tree()
        code, report = self.by_path(*args, patches=patches)
        self.assertEqual(code, 1, report)
        self.assertFalse(report["ok"])
        self.assertIn(message, report["error"])
        self.assertEqual(self.tree(), before, "a refusal changed the disk")
        return report

    def outside(self):
        path = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, path)
        return path

    def test_w1_the_move_by_path_copies(self):
        for source, destination, text in ((TASK, TASK_DEST, b"# task\n"),
                                          (PLAN, PLAN_DEST, b"# plan\n")):
            with self.subTest(source=source):
                code, report = self.by_path(source, destination)
                self.assertEqual(code, 0, report)
                self.assertEqual(report["method"], "copy")
                self.assertTrue(report["created_directory"])
                self.assertFalse((self.root / source).exists())
                self.assertEqual((self.root / destination).read_bytes(), text)

    def test_w1_the_script_moves_by_path_where_dir_fd_is_missing(self):
        site = self.outside()
        (site / "sitecustomize.py").write_text("import os\nos.supports_dir_fd = set()\n",
                                               encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(site))
        result = subprocess.run([sys.executable, str(SCRIPT), TASK, TASK_DEST], cwd=self.root,
                                env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["method"], "copy")
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    @NEEDS_SYMLINK
    def test_w2_a_link_at_docs(self):
        real = self.root / "real-docs"
        (self.root / "docs").rename(real)
        (self.root / "docs").symlink_to(real, target_is_directory=True)
        self.refused_by_path((TASK, TASK_DEST), "'docs' is a symbolic link or not a directory")

    @NEEDS_SYMLINK
    def test_w2_a_link_at_the_destination_directory(self):
        (self.root / "docs" / "tasks").symlink_to(self.outside(), target_is_directory=True)
        self.refused_by_path((TASK, TASK_DEST), "'tasks' is a symbolic link or not a directory")

    @NEEDS_SYMLINK
    def test_w2_a_link_at_the_source(self):
        real = self.write("elsewhere.md", "# elsewhere\n")
        (self.root / TASK).unlink()
        (self.root / TASK).symlink_to(real)
        self.refused_by_path((TASK, TASK_DEST),
                             "docs/TASK.md is a symbolic link or not a regular file")

    def test_w2_a_reparse_tag_of_a_name_surrogate_is_a_link(self):
        (self.root / "docs" / "tasks").mkdir()
        for path, label in (("docs", "'docs'"), ("docs/tasks", "'tasks'")):
            for tag in (JUNCTION, SYMLINK):
                with self.subTest(path=path, tag=hex(tag)):
                    patch = _lstat_reporting(
                        {path}, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
                        st_reparse_tag=tag)
                    self.refused_by_path((TASK, TASK_DEST),
                                         f"{label} is a symbolic link or not a directory",
                                         patches=(patch,))

    def test_w2_a_reparse_tag_that_is_no_name_surrogate_is_no_link(self):
        patch = _lstat_reporting({"docs"}, st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT,
                                 st_reparse_tag=CLOUD)
        code, report = self.by_path(TASK, TASK_DEST, patches=(patch,))
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    @WINDOWS_ONLY
    def test_w2_a_junction_at_docs_or_at_the_destination_directory(self):
        outside = self.outside()
        tasks = self.root / "docs" / "tasks"
        _junction(tasks, outside)
        try:
            self.refused_by_path((TASK, TASK_DEST),
                                 "'tasks' is a symbolic link or not a directory")
        finally:
            os.rmdir(tasks)                     # removes the junction, not its target
        real = self.root / "real-docs"
        (self.root / "docs").rename(real)
        _junction(self.root / "docs", real)
        self.addCleanup(os.rmdir, self.root / "docs")
        self.refused_by_path((TASK, TASK_DEST), "'docs' is a symbolic link or not a directory")

    def test_w3_an_entry_at_the_destination(self):
        tasks = self.root / "docs" / "tasks"
        tasks.mkdir()
        target = self.root / TASK_DEST
        target.write_text("# older\n", encoding="utf-8")
        self.refused_by_path((TASK, TASK_DEST), "the destination exists")
        target.unlink()
        target.mkdir()
        self.refused_by_path((TASK, TASK_DEST), "the destination exists")
        target.rmdir()
        if _can_symlink():
            target.symlink_to(self.outside() / "absent.md")
            self.refused_by_path((TASK, TASK_DEST), "the destination exists")

    def test_w4_a_second_hard_link_is_refused_at_its_lstat(self):
        os.link(self.root / TASK, self.root / "alias.md")
        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md has 2 hard links")

    def test_w4_a_read_only_source_is_refused(self):
        patch = _lstat_reporting({TASK}, st_file_attributes=stat.FILE_ATTRIBUTE_READONLY)
        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is read-only", patches=(patch,))

    @WINDOWS_ONLY
    def test_w4_a_read_only_source_on_windows(self):
        source = self.root / TASK
        os.chmod(source, stat.S_IREAD)
        self.addCleanup(os.chmod, source, stat.S_IREAD | stat.S_IWRITE)
        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is read-only")

    @NEEDS_SYMLINK
    def test_w5_a_directory_swapped_for_a_link_before_the_create(self):
        tasks = self.root / "docs" / "tasks"
        tasks.mkdir()
        outside = self.outside()
        real_open = os.open

        def open_(path, flags, *args, **kwargs):
            if os.fspath(path) == TASK_DEST and flags & os.O_CREAT and not tasks.is_symlink():
                tasks.rename(self.root / "docs" / "tasks-aside")
                tasks.symlink_to(outside, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.open", side_effect=open_),))
        self.assertEqual(code, 1, report)
        self.assertIn("the destination directory changed during the move", report["error"])
        # R1.5: the undo removes nothing through the link; the empty file stays there (RW2).
        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
        self.assertEqual((outside / "task-112-x.md").read_bytes(), b"")
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def changed_after_the_copy(self, change):
        """`(exit code, report, whether the change was refused)`; `change` runs after the copy."""
        real_fsync, refused = os.fsync, []

        def fsync(fd):
            real_fsync(fd)
            try:
                change(self.root / TASK)
            except PermissionError:
                refused.append(True)            # Windows: the source's descriptor is open

        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.fsync", side_effect=fsync),))
        return code, report, bool(refused)

    def assertMovedDespite(self, code, report):
        """TASK 131 D23, D28: a descriptor of the run refused the change, and the move ends."""
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
        self.assertFalse((self.root / TASK).exists())

    def test_w6_a_source_replaced_after_the_copy_keeps_the_archive(self):
        def replace(source):
            new = source.with_name("TASK.md.new")
            new.write_bytes(b"# replaced\n")
            os.replace(new, source)

        code, report, refused = self.changed_after_the_copy(replace)
        if refused:
            return self.assertMovedDespite(code, report)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["error"], "docs/TASK.md no longer holds the moved file, so "
                                          "docs/tasks/task-112-x.md is kept")
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
        self.assertEqual((self.root / TASK).read_bytes(), b"# replaced\n")

    def test_w6_a_source_removed_after_the_copy_keeps_the_archive(self):
        code, report, refused = self.changed_after_the_copy(os.unlink)
        if refused:
            return self.assertMovedDespite(code, report)
        self.assertEqual(code, 1, report)
        self.assertIn("is gone after the copy", report["error"])
        self.assertIn("is kept", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    def test_w6_a_second_hard_link_after_the_copy_removes_the_archive(self):
        code, report, refused = self.changed_after_the_copy(
            lambda source: os.link(source, self.root / "alias.md"))
        if refused:
            return self.assertMovedDespite(code, report)
        self.assertEqual(code, 1, report)
        self.assertIn("the source changed during the move", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def unlink_failing(self, times, on_failure=None):
        """A patch of `os.unlink` that fails `times` times on the source, then removes it."""
        real_unlink, failures = os.unlink, []

        def unlink(path, *args, **kwargs):
            if os.fspath(path) == TASK and len(failures) < times:
                failures.append(True)
                if on_failure is not None:
                    on_failure(len(failures))
                raise PermissionError(13, "Permission denied")
            return real_unlink(path, *args, **kwargs)
        return mock.patch("os.unlink", side_effect=unlink)

    def test_w7_the_unlink_of_the_source_is_tried_ten_times(self):
        code, report = self.by_path(TASK, TASK_DEST, patches=(self.unlink_failing(10),))
        self.assertEqual(code, 1, report)
        self.assertIn("cannot remove docs/TASK.md", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def test_w7_the_tenth_try_moves_the_file(self):
        code, report = self.by_path(TASK, TASK_DEST, patches=(self.unlink_failing(9),))
        self.assertEqual(code, 0, report)
        self.assertFalse((self.root / TASK).exists())

    def test_w7_a_source_replaced_between_two_tries_keeps_both(self):
        def replace(count):
            if count == 2:
                new = self.root / "docs" / "TASK.md.new"
                new.write_bytes(b"# replaced\n")
                os.replace(new, self.root / TASK)

        # Two failures, so that a third try with no check of step 9 removes the replacement.
        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(self.unlink_failing(2, on_failure=replace),))
        self.assertEqual(code, 1, report)
        self.assertIn("no longer holds the moved file", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
        self.assertEqual((self.root / TASK).read_bytes(), b"# replaced\n")

    def test_w7_a_source_removed_before_a_try_of_the_archives_removal(self):
        real_unlink, failed = os.unlink, []

        def unlink(path, *args, **kwargs):
            name = os.fspath(path)
            if name == TASK:
                raise PermissionError(13, "Permission denied")
            if name == TASK_DEST and not failed:
                failed.append(True)
                real_unlink(self.root / TASK)       # another process removes the source
                raise PermissionError(13, "Permission denied")
            return real_unlink(path, *args, **kwargs)

        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.unlink", side_effect=unlink),))
        self.assertEqual(code, 1, report)
        self.assertIn("was removed, so", report["error"])
        self.assertIn("is kept", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    @WINDOWS_ONLY
    def test_w8_a_source_held_open_by_another_handle(self):
        with open(self.root / TASK, "rb"):
            code, report = self.by_path(TASK, TASK_DEST)
        self.assertEqual(code, 1, report)
        self.assertIn("cannot remove docs/TASK.md", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def test_w9_the_archive_keeps_every_byte(self):
        data = b"# task\r\nline\x1a after the byte\r\nlast\n"
        (self.root / TASK).write_bytes(data)
        code, report = self.by_path(TASK, TASK_DEST)
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / TASK_DEST).read_bytes(), data)

    @NEEDS_DIR_FD
    def test_w10_a_platform_with_dir_fd_never_moves_by_path(self):
        module = _load()
        out = io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            with mock.patch.object(module, "_move_by_path",
                                   side_effect=AssertionError("moved by path")), \
                    contextlib.redirect_stdout(out):
                code = module.main([TASK, TASK_DEST])
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out.getvalue())["ok"])

    def test_w21_a_regular_file_swapped_in_before_the_open(self):
        real_open = os.open

        def open_(path, flags, *args, **kwargs):
            if os.fspath(path) == TASK and not flags & os.O_CREAT:
                new = self.root / "docs" / "TASK.md.new"
                new.write_bytes(b"# swapped\n")
                os.replace(new, self.root / TASK)
            return real_open(path, flags, *args, **kwargs)

        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.open", side_effect=open_),))
        self.assertEqual(code, 1, report)
        self.assertIn("the source changed during the move", report["error"])
        self.assertFalse((self.root / "docs" / "tasks").exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# swapped\n")

    @NEEDS_SYMLINK
    def test_w21_a_link_swapped_in_where_o_nofollow_is_missing(self):
        secret = self.outside() / "secret.md"
        secret.write_bytes(b"secret\n")
        real_open = os.open

        def open_(path, flags, *args, **kwargs):
            if os.fspath(path) == TASK and not flags & os.O_CREAT:
                link = self.root / "docs" / "TASK.md.link"
                link.symlink_to(secret)
                os.replace(link, self.root / TASK)
            return real_open(path, flags, *args, **kwargs)

        with _no_o_nofollow():
            code, report = self.by_path(TASK, TASK_DEST,
                                        patches=(mock.patch("os.open", side_effect=open_),))
        self.assertEqual(code, 1, report)
        self.assertIn("the source changed during the move", report["error"])
        self.assertFalse((self.root / "docs" / "tasks").exists())

    def test_w22_an_overlong_name_is_a_json_refusal(self):
        code, report = self.by_path(TASK, "docs/tasks/task-112-" + "a" * 300 + ".md")
        self.assertEqual(code, 1, report)
        self.assertFalse(report["ok"])
        self.assertFalse((self.root / "docs" / "tasks").exists())

    def test_w22_a_created_directory_is_removed_after_a_failed_rmdir(self):
        real_rmdir, failed = os.rmdir, []

        def rmdir(path, *args, **kwargs):
            if os.fspath(path) == "docs/plans" and not failed:
                failed.append(True)
                raise PermissionError(13, "Permission denied")
            return real_rmdir(path, *args, **kwargs)

        code, report = self.by_path(PLAN, "docs/plans/plan-112-" + "a" * 300 + ".md",
                                    patches=(mock.patch("os.rmdir", side_effect=rmdir),))
        self.assertEqual(code, 1, report)
        self.assertTrue(failed, "the refusal removed no directory")
        self.assertFalse((self.root / "docs" / "plans").exists())

    def test_w23_the_docstring_names_both_branches_and_the_windows(self):
        doc = _load().__doc__
        self.assertIn("_move_by_path", doc)
        self.assertIn("2 usage error.", doc)
        self.assertIn("access rules", doc)
        for label in range(1, 13):
            with self.subTest(label=label):
                self.assertRegex(doc, rf"\bRW{label}\b")

    def test_w24_each_open_of_the_move_passes_o_binary(self):
        bit, calls, real_open = _unused_open_bit(), [], os.open

        def spy(path, flags, *args, **kwargs):
            calls.append((os.fspath(path), flags))
            return real_open(path, flags & ~bit, *args, **kwargs)

        code, report = self.by_path(TASK, TASK_DEST, patches=(
            mock.patch.object(os, "O_BINARY", bit, create=True),
            mock.patch("os.open", side_effect=spy)))
        self.assertEqual(code, 0, report)
        self.assertEqual(sorted(path for path, _flags in calls), [TASK, TASK_DEST])
        for path, flags in calls:
            with self.subTest(path=path):
                self.assertTrue(flags & bit, f"the open of {path} drops O_BINARY")

    # --- the fix of round 1 of stage 2 (TASK 131 D26) ------------------------------------------

    def open_hook(self, path, when, change):
        """A patch of `os.open` that runs `change()` once, before the first open of `path` that
        `when(flags)` accepts; the list it returns names each open of `path`."""
        real_open, seen = os.open, []

        def opener(name, flags, *args, **kwargs):
            if os.fspath(name) == path:
                seen.append(flags)
                if when(flags) and len([f for f in seen if when(f)]) == 1:
                    change()
            return real_open(name, flags, *args, **kwargs)
        return mock.patch("os.open", side_effect=opener), seen

    def test_w29_a_second_hard_link_before_the_open_of_the_source(self):
        real_open, opened = os.open, []

        def opener(name, flags, *args, **kwargs):
            opened.append(os.fspath(name))
            if os.fspath(name) == TASK and opened.count(TASK) == 1:
                os.link(self.root / TASK, self.root / "alias.md")
            return real_open(name, flags, *args, **kwargs)
        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.open", side_effect=opener),))
        self.assertEqual(code, 1, report)
        self.assertIn("the source changed during the move", report["error"])
        self.assertNotIn(TASK_DEST, opened, "step 6 opened the destination")
        self.assertFalse((self.root / "docs" / "tasks").exists(), "step 4 ran")

    def refused_on_windows(self, change, refused):
        """`change()`; on Windows its `PermissionError` is noted in `refused` (TASK 131 D28)."""
        try:
            change()
        except PermissionError:
            if os.name != "nt":
                raise
            refused.append(True)                # a descriptor of the run holds the file

    @NEEDS_SYMLINK
    def test_w30_docs_moved_out_and_linked_back_before_the_create(self):
        (self.root / "docs" / "tasks").mkdir()
        away = self.outside() / "docs-moved"
        refused = []

        def move_docs():
            (self.root / "docs").rename(away)
            (self.root / "docs").symlink_to(away, target_is_directory=True)
        patch, _seen = self.open_hook(TASK_DEST, lambda flags: flags & os.O_CREAT,
                                      lambda: self.refused_on_windows(move_docs, refused))
        code, report = self.by_path(TASK, TASK_DEST, patches=(patch,))
        if refused:
            return self.assertMovedDespite(code, report)
        self.assertEqual(code, 1, report)
        self.assertIn("the destination directory changed during the move", report["error"])
        # R1.5: the undo removes nothing through a changed directory (RW2).
        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
        self.assertEqual((away / "tasks" / "task-112-x.md").read_bytes(), b"")
        self.assertEqual((away / "TASK.md").read_bytes(), b"# task\n")

    def test_w31_another_file_at_the_destination_after_the_create(self):
        (self.root / "docs" / "tasks").mkdir()
        target, aside = self.root / TASK_DEST, self.root / "docs" / "made-aside.md"
        real_open, refused = os.open, []

        def put_another():
            target.rename(aside)
            target.write_bytes(b"# impostor\n")

        def opener(name, flags, *args, **kwargs):
            fd = real_open(name, flags, *args, **kwargs)
            if os.fspath(name) == TASK_DEST and flags & os.O_CREAT:
                self.refused_on_windows(put_another, refused)
            return fd
        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.open", side_effect=opener),))
        if refused:
            return self.assertMovedDespite(code, report)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["error"], "the destination directory changed during the move; "
                                          "docs/tasks/task-112-x.md no longer holds the file "
                                          "this run made, so that file is kept")
        self.assertEqual(target.read_bytes(), b"# impostor\n")
        self.assertEqual(aside.read_bytes(), b"")
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def test_w32_the_undo_tries_the_removal_of_the_archive(self):
        real_unlink, failed = os.unlink, []

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == TASK_DEST and not failed:
                failed.append(True)
                raise PermissionError(13, "Permission denied")
            return real_unlink(name, *args, **kwargs)
        code, report = self.by_path(TASK, TASK_DEST, patches=(
            mock.patch("os.write", side_effect=OSError(28, "No space left on device")),
            mock.patch("os.unlink", side_effect=unlink)))
        self.assertEqual(code, 1, report)
        self.assertIn("cannot copy the source", report["error"])
        self.assertTrue(failed)
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def failed_step_10(self, error, before=None):
        """`main` with the unlink of the source failing with `error`; `before` runs first."""
        real_unlink = os.unlink

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == TASK:
                if before is not None:
                    before()
                raise error
            return real_unlink(name, *args, **kwargs)
        return self.by_path(TASK, TASK_DEST, patches=(mock.patch("os.unlink", side_effect=unlink),))

    def test_w33_a_vanished_source_keeps_the_archive(self):
        code, report = self.failed_step_10(FileNotFoundError(2, "No such file or directory"),
                                           before=lambda: os.remove(self.root / TASK))
        self.assertEqual(code, 1, report)
        self.assertIn("it is gone, so docs/tasks/task-112-x.md is kept", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    def test_w33_a_source_that_holds_another_file_keeps_the_archive(self):
        def swap():
            new = self.root / "docs" / "TASK.md.new"
            new.write_bytes(b"# another\n")
            os.replace(new, self.root / TASK)
        code, report = self.failed_step_10(OSError(5, "Input/output error"), before=swap)
        self.assertEqual(code, 1, report)
        self.assertIn("it no longer holds the moved file, so", report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")
        self.assertEqual((self.root / TASK).read_bytes(), b"# another\n")

    def test_w33_an_unconfirmed_source_keeps_both_names(self):
        real_lstat, real_unlink, failed = os.lstat, os.unlink, []

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == TASK:
                failed.append(True)
                raise OSError(5, "Input/output error")
            return real_unlink(name, *args, **kwargs)

        def lstat(name, *args, **kwargs):
            if failed and os.fspath(name) == TASK:
                raise OSError(5, "Input/output error")
            return real_lstat(name, *args, **kwargs)
        code, report = self.by_path(TASK, TASK_DEST, patches=(
            mock.patch("os.unlink", side_effect=unlink),
            mock.patch("os.lstat", side_effect=lstat)))
        self.assertEqual(code, 1, report)
        self.assertIn("or confirm what it holds", report["error"])
        self.assertIn("both it and docs/tasks/task-112-x.md are kept", report["error"])
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# task\n")

    def test_w33_a_failed_removal_of_the_archive_keeps_the_base_message(self):
        def unlink(name, *args, **kwargs):
            raise PermissionError(13, "Permission denied")
        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.unlink", side_effect=unlink),))
        self.assertEqual(code, 1, report)
        self.assertEqual(report["error"],
                         "cannot remove docs/TASK.md (Permission denied), and "
                         "docs/tasks/task-112-x.md remains (Permission denied)")

    @NEEDS_SYMLINK
    def test_w34_a_directory_swapped_before_the_removal_of_the_archive(self):
        tasks = self.root / "docs" / "tasks"
        tasks.mkdir()
        outside = self.outside()
        decoy = outside / "task-112-x.md"
        decoy.write_bytes(b"# decoy\n")
        real_lstat, swapped = os.lstat, []

        def lstat(name, *args, **kwargs):
            st = real_lstat(name, *args, **kwargs)
            if os.fspath(name) == TASK_DEST and copied and not swapped:
                swapped.append(True)                # the check of the archive passed
                tasks.rename(self.root / "docs" / "tasks-aside")
                tasks.symlink_to(outside, target_is_directory=True)
            return st
        copied = []

        def failing_write(fd, data):
            copied.append(True)
            raise OSError(28, "No space left on device")
        code, report = self.by_path(TASK, TASK_DEST, patches=(
            mock.patch("os.write", side_effect=failing_write),
            mock.patch("os.lstat", side_effect=lstat)))
        self.assertEqual(code, 1, report)
        self.assertTrue(swapped, "the hook never swapped")
        self.assertIn("so docs/tasks/task-112-x.md is kept", report["error"])
        self.assertEqual(decoy.read_bytes(), b"# decoy\n")

    def test_w35_an_encrypted_source_is_refused(self):
        patch = _lstat_reporting({TASK}, st_file_attributes=stat.FILE_ATTRIBUTE_ENCRYPTED)
        self.refused_by_path((TASK, TASK_DEST), "docs/TASK.md is encrypted", patches=(patch,))

    def test_w36_a_write_to_the_source_after_the_copy(self):
        real_fsync = os.fsync

        def fsync(fd):
            real_fsync(fd)
            with open(self.root / TASK, "ab") as handle:
                handle.write(b"written later\n")
            # a later time of the last write than that of step 3
            st = os.stat(self.root / TASK)
            os.utime(self.root / TASK, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(mock.patch("os.fsync", side_effect=fsync),))
        self.assertEqual(code, 1, report)
        self.assertIn("the source changed during the move", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\nwritten later\n")

    # --- the fix of round 2 of stage 2 (TASK 131 D28) ------------------------------------------

    def test_w43_a_write_to_the_source_between_two_tries_of_step_10(self):
        def write(_count):
            with open(self.root / TASK, "ab") as handle:
                handle.write(b"written later\n")

        code, report = self.by_path(TASK, TASK_DEST,
                                    patches=(self.unlink_failing(1, on_failure=write),))
        self.assertEqual(code, 1, report)
        self.assertEqual(report["error"], "the source changed during the move")
        self.assertFalse((self.root / TASK_DEST).exists())
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\nwritten later\n")

    def test_w44_another_file_at_the_archives_name_between_two_tries_of_the_undo(self):
        real_unlink, failed = os.unlink, []

        def unlink(name, *args, **kwargs):
            if os.fspath(name) == TASK_DEST and not failed:
                failed.append(True)
                another = self.root / "docs" / "tasks" / "another.md"
                another.write_bytes(b"# another\n")
                os.replace(another, self.root / TASK_DEST)
                raise PermissionError(13, "Permission denied")
            return real_unlink(name, *args, **kwargs)
        code, report = self.by_path(TASK, TASK_DEST, patches=(
            mock.patch("os.write", side_effect=OSError(28, "No space left on device")),
            mock.patch("os.unlink", side_effect=unlink)))
        self.assertEqual(code, 1, report)
        self.assertTrue(failed, "the undo tried no removal")
        self.assertTrue(report["error"].endswith("so that file is kept"), report["error"])
        self.assertEqual((self.root / TASK_DEST).read_bytes(), b"# another\n")
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def copy_failing(self, path, change):
        """Patches: the copy fails, and `change()` runs at the first `lstat` of `path` after it."""
        real_lstat, copied, changed = os.lstat, [], []

        def lstat(name, *args, **kwargs):
            if os.fspath(name) == path and copied and not changed:
                changed.append(True)
                change()
            return real_lstat(name, *args, **kwargs)

        def failing_write(fd, data):
            copied.append(True)
            raise OSError(28, "No space left on device")
        return (mock.patch("os.write", side_effect=failing_write),
                mock.patch("os.lstat", side_effect=lstat)), changed

    def test_w45_a_renamed_destination_directory_keeps_the_archive(self):
        tasks = self.root / "docs" / "tasks"
        tasks.mkdir()
        aside = self.root / "docs" / "tasks-aside"
        patches, changed = self.copy_failing(TASK_DEST, lambda: tasks.rename(aside))
        code, report = self.by_path(TASK, TASK_DEST, patches=patches)
        self.assertEqual(code, 1, report)
        self.assertTrue(changed, "the undo never checked the archive")
        self.assertEqual(report["error"], "cannot copy the source: No space left on device; "
                                          "docs/tasks/task-112-x.md no longer holds the file "
                                          "this run made, so that file is kept")
        self.assertEqual((aside / "task-112-x.md").read_bytes(), b"")
        self.assertEqual((self.root / TASK).read_bytes(), b"# task\n")

    def test_w46_a_created_directory_replaced_before_the_undo_stays(self):
        plans = self.root / "docs" / "plans"

        def replace():
            plans.rename(self.root / "docs" / "plans-aside")
            plans.mkdir()                       # another, empty directory at its name
        patches, changed = self.copy_failing(PLAN_DEST, replace)
        code, report = self.by_path(PLAN, PLAN_DEST, patches=patches)
        self.assertEqual(code, 1, report)
        self.assertTrue(changed, "the undo never checked the archive")
        self.assertTrue(plans.is_dir(), "the undo removed a directory that it did not create")
        self.assertEqual((self.root / "docs" / "plans-aside" / "plan-112-x.md").read_bytes(), b"")

    def test_w46_a_created_directory_replaced_between_two_tries_stays(self):
        plans = self.root / "docs" / "plans"
        real_rmdir, failed = os.rmdir, []

        def rmdir(path, *args, **kwargs):
            if os.fspath(path) == "docs/plans" and not failed:
                failed.append(True)
                plans.rename(self.root / "docs" / "plans-aside")
                plans.mkdir()                   # another, empty directory at its name
                raise PermissionError(13, "Permission denied")
            return real_rmdir(path, *args, **kwargs)

        code, report = self.by_path(PLAN, "docs/plans/plan-112-" + "a" * 300 + ".md",
                                    patches=(mock.patch("os.rmdir", side_effect=rmdir),))
        self.assertEqual(code, 1, report)
        self.assertTrue(failed, "the refusal removed no directory")
        self.assertTrue(plans.is_dir(), "the undo removed a directory that it did not create")


if __name__ == "__main__":
    unittest.main()
