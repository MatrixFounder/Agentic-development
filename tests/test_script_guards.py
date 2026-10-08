"""Scripts that a committed allow rule runs write inside the working directory only (TASK 112 R4).

`Bash(python3 .agent/tools/rebase_links.py *)` and
`Bash(python3 .agent/skills/skill-creator/scripts/init_skill.py *)` approve any operands. Before
TASK 112, `rebase_links.py` rewrote a file operand wherever it lay, and `init_skill.py` created a
skill directory at any `--path` or path-shaped name. This file pins:

* `rebase_links.py` refuses a file outside the working directory, a linked file, a file with a
  second hard link and a file under `.git/` in any letter case or through a link, with exit 2 and
  no write (``TC-G1``, ``TC-G2``); a file inside is rewritten as before (``TC-G3``); one refused
  operand stops every write (``TC-G7``);
* `rebase_links.py --inbound` refuses a file with a second hard link and skips a symbolic link,
  with exit 3 and no write; it rewrites a sub-task inside; neither a module nor a `.pyc`
  planted beside the script runs (``TC-G8`` to ``TC-G12``, TASK 115);
* `init_skill.py` refuses a skill directory outside the working directory or under `.git/`, with
  exit 1 and nothing created (``TC-G4``, ``TC-G5``); a directory inside is created (``TC-G6``).

The working directory is the `realpath` of a temporary root: `os.getcwd()` returns the resolved
path on darwin, where `tempfile` returns `/var/...`.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
#: The scripts under test, which committed allow rules name.
REBASE = PROJECT_ROOT / ".agent" / "tools" / "rebase_links.py"
INIT = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts" / "init_skill.py"
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


class TestRebaseLinksGuard(unittest.TestCase):
    """TC-G1 to TC-G3."""

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


class TestInboundGuard(unittest.TestCase):
    """TC-G8 to TC-G12: `--inbound` writes only regular files with one hard link (TASK 115).

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
