"""Scripts that a committed allow rule runs write inside the working directory only (TASK 112 R4).

`Bash(python3 .agent/tools/rebase_links.py *)` and
`Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)` approve any operands. Before
TASK 112, `rebase_links.py` rewrote a file operand wherever it lay, and `init_skill.py` created a
skill directory at any `--path` or path-shaped name. This file pins:

* `rebase_links.py` refuses a file outside the working directory, a linked file, a file with a
  second hard link and a file under `.git/` in any letter case or through a link, with exit 2 and
  no write (``TC-G1``, ``TC-G2``); a file inside is rewritten as before (``TC-G3``); one refused
  operand stops every write (``TC-G7``);
* `rebase_links.py` refuses a file whose directory resolves outside the working directory, with
  exit 2 and no write, also through a `..` after a link; a file whose directory link resolves
  inside is rewritten (``TC-G13`` to ``TC-G15``, TASK 116 R1.1);
* both modes write through the descriptor they checked: a directory swapped around the open or
  moved out, a file swapped for a link, a second hard link, a file replaced after the read, a FIFO
  and a platform with no `O_NOFOLLOW` are refused with no write, and so are three swaps around the
  identity check; a failed write leaves a prefix of the new text, and no descriptor stays open
  (``TC-G16`` to ``TC-G27``, TASK 116 R7);
* `rebase_links.py` takes a slot map only for `docs/TASK.md` and `docs/PLAN.md`, each with an
  archive of its form, and only a markdown operand under `docs/`. Its `--repo-root`, `--from` and
  `--to` stay in the tree. A rewrite adds to a link no character outside letters, digits and
  `._~/%-` and no path part that its author did not write, and the text gains no such character
  (``TC-G28`` to ``TC-G30``, TASK 116 R8);
* `rebase_links.py --inbound` refuses a file with a second hard link and skips a symbolic link,
  with exit 3 and no write; it rewrites a sub-task inside; neither a module nor a `.pyc`
  planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115);
* `init_skill.py` refuses a skill directory outside the working directory or under `.git/`, with
  exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``).

The working directory is the `realpath` of a temporary root: `os.getcwd()` returns the resolved
path on darwin, where `tempfile` returns `/var/...`.
"""
import builtins
import contextlib
import errno
import gc
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
#: The scripts under test, which committed allow rules name.
REBASE = PROJECT_ROOT / ".agent" / "tools" / "rebase_links.py"
INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill.py"
#: The inbound module; TC-G19 loads it in this process (TASK 116 R7.4).
SLOT = PROJECT_ROOT / ".agent" / "tools" / "slot_links.py"
#: TC-G28 pins the slug grammar of `rebase_links.py` to this module's (TASK 116 R8.3).
ARCHIVE_MOVE = PROJECT_ROOT / ".agent" / "tools" / "archive_move.py"
LINKED = "[a](ARCHITECTURE.md)\n"
REBASED = "[a](../ARCHITECTURE.md)\n"
SUBTASK = "# Task 112-01: a\n\n[docs/TASK.md](../TASK.md)\n"
RETARGETED = "# Task 112-01: a\n\n[task-112](task-112-x.md)\n"


def _tmp(case):
    path = Path(os.path.realpath(tempfile.mkdtemp()))
    case.addCleanup(shutil.rmtree, path)
    return path


def _run(script, args, cwd):
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=60)


def _module(path, name):
    """A fresh module of `path`, loaded in this process; its siblings come from its directory."""
    sys.path.insert(0, str(Path(path).parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(Path(path).parent))


def _swap(directory, outside):
    """Swap `directory` for a link to `outside`; return the function that swaps it back."""
    aside = directory.with_name(directory.name + ".aside")
    directory.rename(aside)
    directory.symlink_to(outside, target_is_directory=True)

    def back():
        directory.unlink()
        aside.rename(directory)
    return back


def _writes(args, kwargs):
    """True when a call of `os.open` (its flags) or of the built-in `open` (its mode) writes."""
    spec = args[0] if args else kwargs.get("mode", kwargs.get("flags", "r"))
    if isinstance(spec, str):
        return any(c in spec for c in "wax+")
    return bool(spec & (os.O_WRONLY | os.O_RDWR))


def _move_out(directory, outside):
    """Rename `directory` into `outside` and put a link to its new place in its stead."""
    moved = outside / directory.name
    directory.rename(moved)
    directory.symlink_to(moved, target_is_directory=True)
    return moved


def _descriptor_path_known():
    """True where the platform gives the path of a descriptor (TASK 116 R7.2)."""
    try:
        import fcntl
    except ImportError:
        fcntl = None
    return hasattr(fcntl, "F_GETPATH") or os.path.isdir("/proc/self/fd")


class TestRebaseLinksGuard(unittest.TestCase):
    """TC-G1 to TC-G3, TC-G7, TC-G13 to TC-G18, TC-G20 to TC-G30 (TASK 116), TC-G31 (TASK 117)."""

    def setUp(self):
        self.root = _tmp(self)
        (self.root / "docs" / "tasks").mkdir(parents=True)
        (self.root / "docs" / "ARCHITECTURE.md").write_text("# a\n", encoding="utf-8")
        self.outside = _tmp(self)

    def rebase(self, operand):
        return _run(REBASE, [str(operand), "--from", "docs", "--to", "docs/tasks"], self.root)

    def test_g1_a_file_outside_the_working_directory(self):
        # base-fail: the base rewrites it.
        victim = self.outside / "victim.md"
        victim.write_text(LINKED, encoding="utf-8")
        result = self.rebase(victim)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        # TASK 116 R1.1 and R8.2 run after the checks of TASK 112, so the first one names the
        # refusal on every platform.
        self.assertIn("lies outside the working directory", result.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)

    def test_g2_a_link_a_second_hard_link_or_git(self):
        victim = self.outside / "victim.md"
        victim.write_text(LINKED, encoding="utf-8")
        (self.root / "docs" / "tasks" / "linked.md").symlink_to(victim)
        hard = self.root / "docs" / "tasks" / "hard.md"
        hard.write_text(LINKED, encoding="utf-8")
        os.link(hard, self.root / "alias.md")
        git = self.root / ".git" / "x.md"
        git.parent.mkdir()
        git.write_text(LINKED, encoding="utf-8")
        (self.root / "gl").symlink_to(self.root / ".git", target_is_directory=True)
        (self.root / ".git" / "hooks").mkdir()
        hook = self.root / ".git" / "hooks" / "y.md"
        hook.write_text(LINKED, encoding="utf-8")
        (self.root / "hl").symlink_to(self.root / ".git" / "hooks", target_is_directory=True)
        for operand in ("docs/tasks/linked.md", "docs/tasks/hard.md", ".git/x.md", ".GIT/x.md",
                        "gl/x.md", "hl/y.md", "hl/../x.md"):
            with self.subTest(operand=operand):
                result = self.rebase(operand)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
        self.assertEqual(hard.read_text(encoding="utf-8"), LINKED)
        self.assertEqual(git.read_text(encoding="utf-8"), LINKED)
        self.assertEqual(hook.read_text(encoding="utf-8"), LINKED)

    def test_g2_from_a_subdirectory_and_through_a_firmlink(self):
        (self.root / ".git" / "hooks").mkdir(parents=True)
        hook = self.root / ".git" / "hooks" / "y.md"
        hook.write_text(LINKED, encoding="utf-8")
        sub = self.root / "sub"
        sub.mkdir()
        (sub / "gl").symlink_to(self.root / ".git", target_is_directory=True)
        result = _run(REBASE, ["gl/hooks/y.md", "--from", "docs", "--to", "docs/tasks"], sub)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        firm = Path("/System/Volumes/Data" + str(self.root / ".git" / "hooks"))
        if sys.platform == "darwin" and firm.is_dir():
            (self.root / "fl").symlink_to(firm, target_is_directory=True)
            result = self.rebase("fl/y.md")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            # TASK 116 R1.1 runs after the check of `.git`, so that check names the refusal.
            self.assertIn("lies under .git/", result.stderr)
        self.assertEqual(hook.read_text(encoding="utf-8"), LINKED)

    def test_g7_one_refused_operand_stops_every_write(self):
        good = self.root / "docs" / "tasks" / "t.md"
        good.write_text(LINKED, encoding="utf-8")
        victim = self.outside / "victim.md"
        victim.write_text(LINKED, encoding="utf-8")
        result = _run(REBASE, ["docs/tasks/t.md", str(victim), "--from", "docs", "--to",
                               "docs/tasks"], self.root)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(good.read_text(encoding="utf-8"), LINKED)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)

    def test_g3_a_file_inside_is_rewritten(self):
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        result = self.rebase("docs/tasks/t.md")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)

    def test_g13_a_directory_that_resolves_outside(self):
        # base-fail: the base writes through the directory link.
        victim = self.outside / "victim.md"
        victim.write_text(LINKED, encoding="utf-8")
        (self.root / "docs" / "out").symlink_to(self.outside, target_is_directory=True)
        result = self.rebase("docs/out/victim.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("resolves outside", result.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)

    def test_g14_a_directory_link_that_resolves_inside(self):
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        (self.root / "docs" / "in").symlink_to(self.root / "docs" / "tasks",
                                               target_is_directory=True)
        result = self.rebase("docs/in/t.md")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(moved.read_text(encoding="utf-8"), REBASED)

    def test_g15_a_parent_segment_after_a_directory_link(self):
        # base-fail: the kernel resolves the link before the `..`; a lexical check does not.
        victim = self.outside / "victim.md"
        victim.write_text(LINKED, encoding="utf-8")
        (self.outside / "sub").mkdir()
        (self.root / "docs" / "up").symlink_to(self.outside / "sub", target_is_directory=True)
        result = self.rebase("docs/up/../victim.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("resolves outside", result.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)

    def inprocess(self, operand, hooks, before=None):
        """`_main` of `REBASE` in this process, with `hooks(real)` wrapping each kind of open.

        `operand` is one operand or a list of them. The script is loaded fresh before `before`
        runs, so a case can change `os` for the run alone. Returns the exit code and the text of
        stderr.
        """
        module = _module(REBASE, "rebase_links_under_test")
        err, cwd = io.StringIO(), os.getcwd()
        os.chdir(self.root)
        try:
            with contextlib.ExitStack() as stack:
                if before:
                    stack.enter_context(before())
                stack.enter_context(mock.patch("os.open", hooks(os.open)))
                stack.enter_context(mock.patch("builtins.open", hooks(builtins.open)))
                stack.enter_context(contextlib.redirect_stderr(err))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                operands = [operand] if isinstance(operand, str) else list(operand)
                code = module._main([*operands, "--from", "docs", "--to", "docs/tasks"])
        finally:
            os.chdir(cwd)
        return code, err.getvalue()

    def test_g16_a_directory_swapped_around_the_open(self):
        # base-fail: the base reads and writes the outside file through the swapped directory.
        inside = self.root / "docs" / "x"
        inside.mkdir()
        (inside / "t.md").write_text(LINKED, encoding="utf-8")
        victim = self.outside / "t.md"
        victim.write_text(LINKED, encoding="utf-8")
        target = str(inside / "t.md")

        def hooks(real):
            def opener(path, *args, **kwargs):
                if os.path.abspath(path) != target:
                    return real(path, *args, **kwargs)
                back = _swap(inside, self.outside)
                try:
                    return real(path, *args, **kwargs)
                finally:
                    back()
            return opener
        code, err = self.inprocess("docs/x/t.md", hooks)
        self.assertEqual(code, 2, err)
        self.assertIn("is not the file at its real path", err)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
        self.assertEqual((inside / "t.md").read_text(encoding="utf-8"), LINKED)

    def test_g17_a_file_swapped_for_a_link(self):
        # base-fail: the base follows the planted link. The inside link needs O_NOFOLLOW itself.
        other = self.root / "docs" / "other.md"
        for name, target in (("outside", self.outside / "v.md"), ("inside", other)):
            with self.subTest(link=name):
                target.write_text(LINKED, encoding="utf-8")
                operand = self.root / "docs" / "tasks" / f"{name}.md"
                operand.write_text(LINKED, encoding="utf-8")

                def hooks(real, operand=operand, target=target):
                    def opener(path, *args, **kwargs):
                        if os.path.abspath(path) == str(operand) and not operand.is_symlink():
                            operand.unlink()
                            operand.symlink_to(target)
                        return real(path, *args, **kwargs)
                    return opener
                code, err = self.inprocess(f"docs/tasks/{name}.md", hooks)
                self.assertEqual(code, 2, err)
                self.assertIn("cannot open it", err)
                self.assertEqual(target.read_text(encoding="utf-8"), LINKED)

    def test_g18_a_second_hard_link_before_the_open(self):
        # base-fail: the base writes through the shared inode.
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        alias = self.outside / "alias.md"

        def hooks(real):
            def opener(path, *args, **kwargs):
                if os.path.abspath(path) == str(moved) and not alias.exists():
                    os.link(moved, alias)
                return real(path, *args, **kwargs)
            return opener
        code, err = self.inprocess("docs/tasks/t.md", hooks)
        self.assertEqual(code, 2, err)
        self.assertIn("has 2 hard links", err)
        self.assertEqual(alias.read_text(encoding="utf-8"), LINKED)

    def test_g20_a_second_hard_link_before_the_write(self):
        # base-fail: the base writes through the shared inode; R7.3 re-checks the link count.
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        alias = self.outside / "alias.md"

        def hooks(real):
            def opener(path, *args, **kwargs):
                if (os.path.abspath(path) == str(moved) and _writes(args, kwargs)
                        and not alias.exists()):
                    os.link(moved, alias)
                return real(path, *args, **kwargs)
            return opener
        code, err = self.inprocess("docs/tasks/t.md", hooks)
        self.assertEqual(code, 2, err)
        self.assertIn("has 2 hard links", err)
        self.assertEqual(alias.read_text(encoding="utf-8"), LINKED)
        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)

    def test_g21_a_file_replaced_after_the_read(self):
        # base-fail: the base writes the rebased old text over the new file.
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        fresh = "# fresh\n"
        replaced = []

        def hooks(real):
            def opener(path, *args, **kwargs):
                if (os.path.abspath(path) == str(moved) and _writes(args, kwargs)
                        and not replaced):
                    replaced.append(True)
                    new = moved.with_name("t.md.new")
                    new.write_text(fresh, encoding="utf-8")
                    os.replace(new, moved)
                return real(path, *args, **kwargs)
            return opener
        code, err = self.inprocess("docs/tasks/t.md", hooks)
        self.assertEqual(code, 2, err)
        self.assertIn("changed during the run", err)
        self.assertEqual(moved.read_text(encoding="utf-8"), fresh)

    def test_g22_a_platform_with_no_o_nofollow(self):
        # base-fail: the base file mode needs no O_NOFOLLOW, so it rewrites the file.
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")

        @contextlib.contextmanager
        def no_o_nofollow():
            saved = os.O_NOFOLLOW
            del os.O_NOFOLLOW
            try:
                yield
            finally:
                os.O_NOFOLLOW = saved
        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=no_o_nofollow)
        self.assertEqual(code, 2, err)
        self.assertIn("this platform has no O_NOFOLLOW", err)
        self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)

    def test_g23_a_directory_moved_out_and_linked_back(self):
        # base-fail: the file keeps its inode, so only the directory check refuses it.
        inside = self.root / "docs" / "x"
        inside.mkdir()
        (inside / "t.md").write_text(LINKED, encoding="utf-8")
        target, moved = str(inside / "t.md"), []

        def hooks(real):
            def opener(path, *args, **kwargs):
                if os.path.abspath(path) == target and not moved:
                    moved.append(_move_out(inside, self.outside))
                return real(path, *args, **kwargs)
            return opener
        code, err = self.inprocess("docs/x/t.md", hooks)
        self.assertEqual(code, 2, err)
        self.assertIn("its directory resolves outside the working directory", err)
        self.assertEqual((moved[0] / "t.md").read_text(encoding="utf-8"), LINKED)

    def test_g24_a_failed_write_leaves_a_prefix_of_the_new_text(self):
        # base-fail: the base writes through a file object, so the hook never fires: exit 0.
        moved = self.root / "docs" / "tasks" / "t.md"
        moved.write_text(LINKED, encoding="utf-8")
        real_write = os.write

        def full_disk(fd, data):
            real_write(fd, bytes(data[:5]))
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC))

        @contextlib.contextmanager
        def failing_write():
            with mock.patch("os.write", full_disk):
                yield
        code, err = self.inprocess("docs/tasks/t.md", lambda real: real, before=failing_write)
        self.assertEqual(code, 2, err)
        self.assertEqual(moved.read_bytes(), REBASED.encode("utf-8")[:5])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "no os.mkfifo")
    def test_g25_a_fifo_operand(self):
        # base-fail: the base rewrites the first operand, then blocks on the open of the FIFO.
        first = self.root / "docs" / "tasks" / "t.md"
        first.write_text(LINKED, encoding="utf-8")
        os.mkfifo(self.root / "docs" / "tasks" / "f.md")
        try:
            result = subprocess.run([sys.executable, str(REBASE), "docs/tasks/t.md",
                                     "docs/tasks/f.md", "--from", "docs", "--to", "docs/tasks"],
                                    cwd=self.root, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            self.fail("the open of the FIFO blocked")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("is not a regular file", result.stderr)
        # TASK 116 R7.1: every operand is opened before any is read or written.
        self.assertEqual(first.read_text(encoding="utf-8"), LINKED)

    @unittest.skipUnless(os.path.isdir("/dev/fd"), "no /dev/fd")
    def test_g26_no_descriptor_stays_open(self):
        # Passes at the base, which closes each file it opens.
        moved = self.root / "docs" / "tasks" / "t.md"
        second = self.root / "docs" / "tasks" / "u.md"
        alias = self.outside / "alias.md"

        def hooks(real):
            def opener(path, *args, **kwargs):
                if os.path.abspath(path) == str(second) and not alias.exists():
                    os.link(second, alias)
                return real(path, *args, **kwargs)
            return opener
        for operands in (["docs/tasks/t.md"], ["docs/tasks/t.md", "docs/tasks/u.md"]):
            with self.subTest(operands=operands):
                moved.write_text(LINKED, encoding="utf-8")
                second.write_text(LINKED, encoding="utf-8")
                gc.collect()
                before = sorted(os.listdir("/dev/fd"))
                code, err = self.inprocess(operands, hooks)
                self.assertIn(code, (0, 2), err)
                self.assertEqual(sorted(os.listdir("/dev/fd")), before)
        self.assertTrue(alias.exists(), "the hook made no second link")

    @unittest.skipUnless(_descriptor_path_known(), "no descriptor path on this platform")
    def test_g27_three_swaps_around_the_identity_check(self):
        # base-fail: the base reads and writes the outside file through the swapped directory.
        inside = self.root / "docs" / "x"
        inside.mkdir()
        (inside / "t.md").write_text(LINKED, encoding="utf-8")
        victim = self.outside / "t.md"
        victim.write_text(LINKED, encoding="utf-8")
        target, state = str(inside / "t.md"), {"swaps": 0}

        def hooks(real):
            def opener(path, *args, **kwargs):
                if os.path.abspath(path) == target and "opened" not in state:
                    state["opened"], state["back"] = True, _swap(inside, self.outside)
                return real(path, *args, **kwargs)
            return opener

        @contextlib.contextmanager
        def swaps_around_realpath():
            real_realpath = os.path.realpath

            def realpath(path, *args, **kwargs):
                if "back" not in state or os.path.abspath(path) != target:
                    return real_realpath(path, *args, **kwargs)
                state.pop("back")()
                state["swaps"] += 1
                try:
                    return real_realpath(path, *args, **kwargs)
                finally:
                    state["back"] = _swap(inside, self.outside)
            try:
                with mock.patch("os.path.realpath", realpath):
                    yield
            finally:
                if "back" in state:
                    state.pop("back")()
        code, err = self.inprocess("docs/x/t.md", hooks, before=swaps_around_realpath)
        self.assertEqual(code, 2, err)
        self.assertIn("its directory resolves outside the working directory", err)
        self.assertEqual(victim.read_text(encoding="utf-8"), LINKED)
        self.assertGreaterEqual(state["swaps"], 1, "the realpath hook never swapped")

    def test_g28_a_slot_map_of_another_form(self):
        # base-fail: the base writes any archive text over the slot link.
        # TASK 117 R1: the operand carries the slot archives' `<ID>-<slug>`.
        moved = self.root / "docs" / "tasks" / "task-116-x.md"
        text = LINKED + "[t](TASK.md)\n[p](PLAN.md)\n"
        refused = (("docs/NOTES.md=docs/tasks/task-116-x.md", "its slot is not"),
                   ("docs/TASK.md=.agent/tools/x.py", "its archive is not"),
                   ("docs/TASK.md=docs/plans/plan-116-x.md", "its archive is not"),
                   ("docs/PLAN.md=docs/tasks/task-116-x.md", "its archive is not"),
                   ("docs/TASK.md=docs/tasks/task-16-x.md", "its archive is not"),
                   ("docs/TASK.md=docs/tasks/task-116-x.md\nevil", "its archive is not"),
                   # a slug outside the grammar of `archive_move.SLUG`
                   ("docs/TASK.md=docs/tasks/task-116-a b.md", "its archive is not"),
                   ("docs/TASK.md=docs/tasks/task-116-A:b.md", "its archive is not"))
        for pair, reason in refused:
            with self.subTest(pair=pair):
                moved.write_text(text, encoding="utf-8")
                result = _run(REBASE, ["docs/tasks/task-116-x.md", "--from", "docs",
                                       "--to", "docs/tasks", "--slot", pair], self.root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                error = json.loads(result.stderr.strip().splitlines()[-1])["error"]
                self.assertIn(reason, error)
                self.assertIn(repr(pair), error)
                self.assertEqual(moved.read_text(encoding="utf-8"), text)
        for pair in ("docs/TASK.md=docs/tasks/task-116-x.md",
                     "docs/PLAN.md=docs/plans/plan-116-x.md"):
            with self.subTest(pair=pair):
                moved.write_text(text, encoding="utf-8")
                result = _run(REBASE, ["docs/tasks/task-116-x.md", "--from", "docs",
                                       "--to", "docs/tasks", "--slot", pair], self.root)
                self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
                self.assertIn("../ARCHITECTURE.md", moved.read_text(encoding="utf-8"))
        grammar = re.compile(r'^_?SLUG = (r".*")$', re.M)
        ours = grammar.search(Path(REBASE).read_text(encoding="utf-8"))
        self.assertIsNotNone(ours, "rebase_links.py holds no slug grammar")
        self.assertEqual(ours.group(1),
                         grammar.search(ARCHIVE_MOVE.read_text(encoding="utf-8")).group(1))

    def test_g29_an_operand_that_is_not_markdown_under_docs(self):
        # base-fail: the base rewrites a link-shaped token in a file of any kind, anywhere.
        for operand, reason in (("docs/tasks/t.py", "is not a markdown file"),
                                ("CLAUDE.md", "does not lie under docs/"),
                                # the normalised operand, not the operand as written
                                ("docs/../CLAUDE.md", "does not lie under docs/"),
                                # fails both checks: the check of `docs/` comes first
                                ("notes.txt", "does not lie under docs/")):
            with self.subTest(operand=operand):
                path = self.root / operand
                path.write_text(LINKED, encoding="utf-8")
                result = self.rebase(operand)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(reason, result.stderr)
                self.assertEqual(path.read_text(encoding="utf-8"), LINKED)

    def test_g30_options_and_rewritten_links_stay_in_the_tree(self):
        # base-fail: the base builds the link from any --repo-root, --from and --to.
        docs = self.root / "docs"
        moved = docs / "tasks" / "t.md"
        slot = ["--slot", "docs/TASK.md=docs/tasks/task-116-x.md"]
        with_slot = LINKED + "[t](TASK.md)\n"
        for name in ("x y", "a:b", "a)b", "plain-words"):
            (docs / name).mkdir()
            (docs / name / "ARCHITECTURE.md").write_text("# a\n", encoding="utf-8")
        for name in ("a b/x y.md", "m n/a.md", 'href="x.md"', "x.md"):
            (docs / name).parent.mkdir(exist_ok=True)
            (docs / name).write_text("# a\n", encoding="utf-8")
        text_held = "holds text that its authored link does not"
        part_held = "the path of a rewritten link is not a tail of its authored link's"
        refused = (
            # (--from, --to, other options, the operand's text, the reason)
            ("docs", "docs/tasks", ["--repo-root", str(self.root / "nowhere")] + slot, with_slot,
             "--repo-root is not the working directory"),
            ("docs", "docs/tasks", ["--repo-root", str(self.outside)] + slot, with_slot,
             "--repo-root is not the working directory"),
            ("docs", "../w", slot, with_slot, "--to does not lie inside the working directory"),
            # R8.6 compares the normalised form
            ("docs", "docs/../../w", slot, with_slot,
             "--to does not lie inside the working directory"),
            (str(self.outside), "docs/tasks", slot, with_slot,
             "--from does not lie inside the working directory"),
            # TASK 116 R8.7: the space of `docs/x y` would enter the link
            ("docs/x y", "docs/tasks", [], LINKED, text_held),
            # a colon and a bracket too: R8.7 counts every character outside its safe set
            ("docs/a:b", "docs/tasks", [], LINKED, text_held),
            ("docs/a)b", "docs/tasks", [], LINKED, text_held),
            # a dry run makes the check too
            ("docs/x y", "docs/tasks", ["--dry-run"], LINKED, text_held),
            # each character is counted: a second space is one too many
            ("docs/a b", "docs/tasks", [], "[a](<x y.md>)\n", text_held),
            # a path part that the author did not write, of safe characters or of others
            ("docs/plain-words", "docs/tasks", [], LINKED, part_held),
            ("docs/m n", "docs/tasks", [], "[a](<q r/../a.md>)\n", part_held),
            ("docs/plain-words", "docs/tasks", ["--dry-run"], LINKED, part_held),
            # two links spliced one into the other: the text gains a quote
            ("docs", "docs/tasks", [], '[a](href="x.md")\n',
             "the rewritten text holds a character that the text did not"),
            ("docs", "docs/tasks", ["--dry-run"], '[a](href="x.md")\n',
             "the rewritten text holds a character that the text did not"))
        for from_dir, to_dir, extra, text, reason in refused:
            with self.subTest(from_dir=from_dir, to_dir=to_dir, extra=extra, text=text):
                moved.write_text(text, encoding="utf-8")
                result = _run(REBASE, ["docs/tasks/t.md", "--from", from_dir, "--to", to_dir,
                                       *extra], self.root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(reason, result.stderr)
                self.assertEqual(moved.read_text(encoding="utf-8"), text)
        other = docs / "tasks" / "ARCHITECTURE.md"
        other.write_text("# b\n", encoding="utf-8")
        for from_dir, reason in (("docs/x y", text_held), ("docs/plain-words", part_held)):
            # an ambiguous rebase: the target exists under --to as well
            with self.subTest(ambiguous=from_dir):
                moved.write_text(LINKED, encoding="utf-8")
                result = _run(REBASE, ["docs/tasks/t.md", "--from", from_dir, "--to",
                                       "docs/tasks"], self.root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(reason, result.stderr)
                self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
        other.unlink()
        with self.subTest(kept="a link authored with a space"):
            # passes at the base: R8.7 refuses only what the rewrite adds
            (docs / "sp ace.md").write_text("# a\n", encoding="utf-8")
            moved.write_text("[a](<sp ace.md>)\n", encoding="utf-8")
            result = self.rebase("docs/tasks/t.md")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(moved.read_text(encoding="utf-8"), "[a](<../sp ace.md>)\n")

    def test_g31_a_chosen_slug_reordered_parts_and_a_splice(self):
        # base-fail: the base of TASK 117 writes each refused shape (WI-47).
        docs = self.root / "docs"
        (docs / "plans").mkdir()
        (docs / "tasks" / "task-116-x.md").write_text("# Task 116: x\n", encoding="utf-8")
        for name in ("two/one/one/two/three.md", "one/one/a.md", "](x", "x", 'x">', "a/c.md"):
            (docs / name).parent.mkdir(parents=True, exist_ok=True)
            (docs / name).write_text("# a\n", encoding="utf-8")
        other = "names another <ID>-<slug> than its name"
        tail = "the path of a rewritten link is not a tail of its authored link's"
        splice = "the rewritten text is not the text with each rewritten link replaced"
        refused = (
            # (operand, --from, --to, other options, the operand's text, the reason)
            # R1: a slug, or an ID, that is not the operand's own
            ("plans/plan-116-x.md", "docs", "docs/plans",
             ["--slot", "docs/TASK.md=docs/tasks/task-116-marker-chosen-words-here.md"],
             "[t](TASK.md)\n", other),
            ("plans/plan-116-x.md", "docs", "docs/plans",
             ["--slot", "docs/TASK.md=docs/tasks/task-117-x.md"], "[t](TASK.md)\n", other),
            ("tasks/task-116-y.md", "docs", "docs/tasks",
             ["--slot", "docs/PLAN.md=docs/plans/plan-116-x.md"], "[p](PLAN.md)\n", other),
            ("plans/notes.md", "docs", "docs/plans",
             ["--slot", "docs/TASK.md=docs/tasks/task-116-x.md"], "[t](TASK.md)\n",
             "its name is not task-<ID>-<slug>.md or plan-<ID>-<slug>.md"),
            # R2: parts reordered, and a part repeated
            ("tasks/t.md", "docs/two/one", "docs/tasks", [], "[a](one/two/three.md)\n", tail),
            ("tasks/t.md", "docs/one", "docs/tasks", [], "[a](one/a.md)\n", tail),
            # R3: two overlapping links spliced into one, with no new character
            ("tasks/t.md", "docs", "docs/tasks", [], "[r]: ](x\n", splice),
            ("tasks/t.md", "docs", "docs/tasks", [], '<a href="](x">\n', splice),
            ("tasks/t.md", "docs", "docs/tasks", ["--dry-run"], "[r]: ](x\n", splice))
        for operand, from_dir, to_dir, extra, text, reason in refused:
            with self.subTest(operand=operand, from_dir=from_dir, extra=extra, text=text):
                moved = docs / operand
                moved.write_text(text, encoding="utf-8")
                result = _run(REBASE, [f"docs/{operand}", "--from", from_dir, "--to", to_dir,
                                       *extra], self.root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(reason, result.stderr)
                self.assertEqual(moved.read_text(encoding="utf-8"), text)
                moved.unlink()
        # R4: the commands of `skill-archive-task` Steps 5.5 and 7.6.5, and R2's normalised parts
        kept = (("tasks/task-116-x.md", "docs/tasks",
                 ["--slot", "docs/PLAN.md=docs/plans/plan-116-x.md"],
                 LINKED + "[p](PLAN.md)\n", REBASED + "[p](../plans/plan-116-x.md)\n"),
                ("plans/plan-116-x.md", "docs/plans",
                 ["--slot-must-exist", "--slot", "docs/TASK.md=docs/tasks/task-116-x.md"],
                 LINKED + "[t](TASK.md)\n", REBASED + "[t](../tasks/task-116-x.md)\n"),
                # a `..` inside the authored path: its parts are normalised first
                ("tasks/t.md", "docs/tasks", [], "[c](a/b/../c.md)\n", "[c](../a/c.md)\n"))
        for operand, to_dir, extra, text, rebased in kept:
            with self.subTest(kept=operand):
                moved = docs / operand
                moved.write_text(text, encoding="utf-8")
                result = _run(REBASE, [f"docs/{operand}", "--from", "docs", "--to", to_dir,
                                       *extra], self.root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(moved.read_text(encoding="utf-8"), rebased)


class TestInboundGuard(unittest.TestCase):
    """TC-G8 to TC-G12 (TASK 115) and TC-G19 (TASK 116 R7.4): `--inbound` writes only regular
    files with one hard link, through the descriptor it checked.

    The root holds no git repository, so the script walks it. An own link is a slot link in a
    sub-task file of task 112.
    """

    def setUp(self):
        self.root = _tmp(self)
        self.tasks = self.root / "docs" / "tasks"
        self.tasks.mkdir(parents=True)
        (self.tasks / "task-112-x.md").write_text("# Task 112: x\n", encoding="utf-8")
        self.outside = _tmp(self)

    def inbound(self, script=None):
        return _run(script or REBASE, ["--inbound", "--task", "docs/tasks/task-112-x.md"],
                    self.root)

    def test_g8_a_second_hard_link(self):
        # base-fail: the base rejects --inbound with exit 2.
        sub = self.tasks / "task-112-01-a.md"
        sub.write_text(SUBTASK, encoding="utf-8")
        os.link(sub, self.root / "alias.md")
        result = self.inbound()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("[REFUSED] docs/tasks/task-112-01-a.md", result.stdout)
        self.assertEqual(sub.read_text(encoding="utf-8"), SUBTASK)
        self.assertEqual((self.root / "alias.md").read_text(encoding="utf-8"), SUBTASK)

    def test_g9_a_symbolic_link_to_a_file_outside(self):
        victim = self.outside / "victim.md"
        victim.write_text(SUBTASK, encoding="utf-8")
        (self.tasks / "task-112-02-b.md").symlink_to(victim)
        result = self.inbound()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("[SKIPPED] docs/tasks/task-112-02-b.md", result.stdout)
        self.assertEqual(victim.read_text(encoding="utf-8"), SUBTASK)

    def test_g10_a_subtask_inside_is_rewritten(self):
        sub = self.tasks / "task-112-03-c.md"
        sub.write_text(SUBTASK, encoding="utf-8")
        result = self.inbound()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(sub.read_text(encoding="utf-8"), RETARGETED)

    def _tools_copy(self):
        tools = self.outside / "tools"
        tools.mkdir()
        names = {REBASE.name, "rebase_links.py", "slot_links.py", "task_id_tool.py",
                 "archive_move.py"}
        for name in names:
            shutil.copy2(REBASE.parent / name, tools / name)
        (self.tasks / "task-112-04-d.md").write_text(SUBTASK, encoding="utf-8")
        return tools

    def test_g11_a_planted_module_is_not_imported(self):
        # No module planted beside the script runs (TASK 115 R1.2): a standard-library name, one the
        # standard library lacks on this platform (`subprocess` imports `msvcrt` on POSIX), a
        # package or an extension module in a sibling's name.
        import importlib.machinery
        tools = self._tools_copy()
        planted = ("__future__", "re", "typing", "argparse", "json", "difflib", "subprocess",
                   "msvcrt", "_winapi")
        for name in planted:
            sentinel = self.outside / f"sentinel-{name}"
            (tools / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
                                              encoding="utf-8")
        siblings = ("slot_links", "rebase_links", "archive_move", "task_id_tool")
        for name in siblings:
            package = tools / name
            package.mkdir()
            sentinel = self.outside / f"sentinel-package-{name}"
            (package / "__init__.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
                                                 encoding="utf-8")
        suffix = importlib.machinery.EXTENSION_SUFFIXES[0]
        (tools / f"slot_links{suffix}").write_bytes(b"not a shared object")
        result = self.inbound(tools / REBASE.name)
        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
        ran = [name for name in planted if (self.outside / f"sentinel-{name}").exists()]
        ran += [name for name in siblings
                if (self.outside / f"sentinel-package-{name}").exists()]
        self.assertEqual(ran, [], "a module planted beside the script was imported")

    def test_g12_a_planted_pyc_is_never_read(self):
        import py_compile
        tools = self._tools_copy()
        sentinel = self.outside / "sentinel-pyc"
        evil = self.outside / "evil.py"
        evil.write_text(f"open({str(sentinel)!r}, 'w').close()\n", encoding="utf-8")
        cache = tools / "__pycache__"
        cached = cache / f"slot_links.{sys.implementation.cache_tag}.pyc"
        cache.mkdir()
        py_compile.compile(str(evil), cfile=str(cached),
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
        result = self.inbound(tools / REBASE.name)
        self.assertIn(result.returncode, (0, 3), result.stdout + result.stderr)
        self.assertFalse(sentinel.exists(), "a .pyc planted in __pycache__/ was read")
        self.assertEqual(os.listdir(cache), [cached.name])

    def write_through(self, module, case):
        """`_write_file` of `docs/<case>/t.md` given the identity and bytes of the file the hooks
        of `case` put in its place. Returns the refusal, that file, its bytes before the call, and
        the count of swaps around `os.path.realpath`.

        `swap`: the directory is swapped for a link to `outside/<case>` around the open. `move`:
        the directory is moved into `outside` and linked back. `three`: the swaps of TC-G27.
        """
        inside, away = self.root / "docs" / case, self.outside / case
        inside.mkdir()
        (inside / "t.md").write_text(SUBTASK, encoding="utf-8")
        if case != "move":
            away.mkdir()
            (away / "t.md").write_text(SUBTASK, encoding="utf-8")
        source = (inside if case == "move" else away) / "t.md"
        original, st = source.read_bytes(), source.stat()
        target, state = str(inside / "t.md"), {"swaps": 0}
        real_open, real_realpath = os.open, os.path.realpath

        def opener(path, *args, **kwargs):
            if os.path.abspath(path) != target or "opened" in state:
                return real_open(path, *args, **kwargs)
            state["opened"] = True
            if case == "move":
                _move_out(inside, self.outside)
                return real_open(path, *args, **kwargs)
            state["back"] = _swap(inside, away)
            try:
                return real_open(path, *args, **kwargs)
            finally:
                if case == "swap":
                    state.pop("back")()

        def realpath(path, *args, **kwargs):
            if case != "three" or "back" not in state or path != target:
                return real_realpath(path, *args, **kwargs)
            state.pop("back")()
            state["swaps"] += 1
            try:
                return real_realpath(path, *args, **kwargs)
            finally:
                state["back"] = _swap(inside, away)
        try:
            with mock.patch("os.open", opener), mock.patch("os.path.realpath", realpath):
                refusal = module._write_file(str(self.root), f"docs/{case}/t.md", original,
                                             (st.st_dev, st.st_ino), RETARGETED.encode("utf-8"))
        finally:
            if "back" in state:
                state.pop("back")()
        return refusal, away / "t.md", original, state["swaps"]

    def test_g19_a_directory_swapped_around_the_inbound_open(self):
        # base-fail: the base writes the outside file; its post-write check refuses only a swap.
        module = _module(SLOT, "slot_links_under_test")
        reasons = {"swap": "is not the file at its real path",
                   "move": "its directory resolves outside the working directory",
                   "three": "its directory resolves outside the working directory"}
        for case, reason in reasons.items():
            with self.subTest(case=case):
                if case == "three" and not _descriptor_path_known():
                    self.skipTest("no descriptor path on this platform")
                refusal, victim, original, swaps = self.write_through(module, case)
                self.assertIsNotNone(refusal)
                self.assertEqual(refusal.reason, reason)
                self.assertEqual(victim.read_bytes(), original)
                if case == "three":
                    self.assertGreaterEqual(swaps, 1, "the realpath hook never swapped")


class TestInitSkillGuard(unittest.TestCase):
    """TC-G4 to TC-G6."""

    def setUp(self):
        self.root = _tmp(self)
        self.work = self.root / "work"
        (self.work / ".git" / "hooks").mkdir(parents=True)
        (self.work / "gl").symlink_to(self.work / ".git", target_is_directory=True)
        (self.work / "hl").symlink_to(self.work / ".git" / "hooks", target_is_directory=True)

    def init(self, *args):
        return _run(INIT, list(args), self.work)

    def test_g4_a_path_outside_the_working_directory(self):
        # base-fail: the base creates the skill there.
        result = self.init("x", "--path", str(self.root / "elsewhere"))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse((self.root / "elsewhere").exists())

    def test_g5_a_path_shaped_name_or_git(self):
        for args, absent in ((("../x",), self.root / "x"),
                             ((str(self.root / "abs-x"),), self.root / "abs-x"),
                             (("x", "--path", ".git"), self.work / ".git" / "x"),
                             (("y", "--path", ".GIT"), self.work / ".git" / "y"),
                             (("z", "--path", "gl"), self.work / ".git" / "z"),
                             (("pre-commit", "--path", "hl"),
                              self.work / ".git" / "hooks" / "pre-commit")):
            with self.subTest(args=args):
                result = self.init(*args)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse(absent.exists())

    def test_g5_a_worktree_gitfile_and_a_link_to_the_main_git(self):
        main = self.root / "main.git"
        (main / "worktrees" / "w").mkdir(parents=True)
        (main / "worktrees" / "w" / "commondir").write_text("../..\n", encoding="utf-8")
        tree = self.root / "tree"
        tree.mkdir()
        (tree / ".git").write_text(f"gitdir: {main / 'worktrees' / 'w'}\n", encoding="utf-8")
        (tree / "ml").symlink_to(main, target_is_directory=True)
        result = _run(INIT, ["q6", "--path", "ml"], tree)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse((main / "q6").exists())

    def test_g6_a_path_inside_is_created(self):
        result = self.init("x", "--path", "skills")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.work / "skills" / "x" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
