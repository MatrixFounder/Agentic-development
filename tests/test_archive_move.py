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
  imported, and loading the script keeps the caller's `sys.path`; a source that vanishes before
  its unlink, holds another file then, or cannot be checked, leaves the archive in place
  (``TC-A19`` to ``TC-A23``);
* an existing letter-suffixed sub-task file in the destination's place is refused (``TC-A24``,
  TASK 114).

Each case runs the script with the `realpath` of a temporary root as its working directory;
TC-A11, TC-A13 and TC-A15 to TC-A18 call `main(argv)` in-process to replace `os.link`, `os.unlink`
or `os.write`.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
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
        path.write_text(text, encoding="utf-8")
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

    def test_a5_a_linked_tasks_directory(self):
        outside = Path(os.path.realpath(tempfile.mkdtemp()))
        self.addCleanup(shutil.rmtree, outside)
        (self.root / "docs" / "tasks").symlink_to(outside, target_is_directory=True)
        self.assertRefused((TASK, TASK_DEST))
        self.assertEqual(os.listdir(outside), [])

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

    def test_a16_copy_path_refuses_a_swapped_regular_file(self):
        def swap_then_fail(*_args, **_kwargs):
            self.swap("file")
            raise PermissionError(1, "no hard links here")

        with mock.patch("os.link", side_effect=swap_then_fail):
            code, report = self.run_in_process(TASK, TASK_DEST)
        self.assertEqual(code, 1)
        self.assertIn("changed", report["error"])
        self.assertFalse((self.root / TASK_DEST).exists())

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

    def test_a20_loading_the_script_keeps_the_callers_path(self):
        before = list(sys.path)
        sys.path.insert(0, str(SCRIPT.parent))
        try:
            _load()
            self.assertEqual(sys.path, [str(SCRIPT.parent)] + before)
        finally:
            sys.path[:] = before

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


if __name__ == "__main__":
    unittest.main()
