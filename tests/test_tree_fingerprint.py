"""The tree fingerprint covers every file under review (TASK 111 R4).

`skill-parallel-orchestration` §2.4.1 gives the formula a caller computes before a review round and
recomputes at its return. Before TASK 111 an edit inside an untracked file, or a second edit of a
tracked binary file, left the value unchanged. This file runs the formula as §2.4.1 prints it:

* an edit inside an untracked file changes the value (``TC-F1``);
* a second edit of a tracked binary file changes it (``TC-F2``);
* a tree with no untracked file yields one value on two runs (``TC-F3``);
* `vdd-multi.md` and the security-auditor wrapper quote the formula verbatim (``TC-F4``);
* §2.4.1 states where the formula runs, what it does not cover, and where the caller writes
  during a round, and no longer excuses untracked edits (``TC-F5``).
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL = PROJECT_ROOT / ".agent" / "skills" / "skill-parallel-orchestration" / "SKILL.md"
QUOTING = (".agent/workflows/vdd-multi.md", ".claude/agents/security-auditor.md")
DROPPED = "An untracked file moves the value by appearing or disappearing"
#: Git without the operator's configuration: no signing, no diff driver (PLAN D1).
ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")


def section_241():
    text = SKILL.read_text(encoding="utf-8")
    start = text.index("#### 2.4.1")
    end = re.compile(r"^#{2,4} ", re.M).search(text, start + 10)
    return text[start:end.start() if end else len(text)]


def formula():
    """The command of the first `sh` block of §2.4.1."""
    m = re.search(r"```sh\n(.+?)\n```", section_241(), re.S)
    if not m:
        raise AssertionError("§2.4.1 holds no sh block")
    return m.group(1).strip()


class Repo:
    """A temporary git repository with one tracked text file and one tracked binary file."""

    def __init__(self):
        self.path = Path(tempfile.mkdtemp())
        self.git("init", "-q")
        (self.path / "a.txt").write_text("a\n")
        (self.path / "b.bin").write_bytes(b"\x00\x01binary\x00")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.path, check=True, capture_output=True, env=ENV)

    def value(self):
        env = ENV
        proc = subprocess.run(["bash", "-c", formula()], cwd=self.path, capture_output=True,
                              text=True, env=env, timeout=60)
        out = proc.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{12}", out):
            raise AssertionError(f"the formula printed {out!r}; stderr {proc.stderr!r}")
        return out

    def remove(self):
        shutil.rmtree(self.path)


class TestFormula(unittest.TestCase):

    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.remove)

    def test_f1_edit_inside_an_untracked_file_changes_the_value(self):
        # base-fail: the base formula hashes no untracked content.
        (self.repo.path / "new.md").write_text("one\n")
        before = self.repo.value()
        (self.repo.path / "new.md").write_text("two\n")
        self.assertNotEqual(self.repo.value(), before)

    def test_f2_second_edit_of_a_tracked_binary_changes_the_value(self):
        (self.repo.path / "b.bin").write_bytes(b"\x00\x02first\x00")
        before = self.repo.value()
        (self.repo.path / "b.bin").write_bytes(b"\x00\x03second\x00")
        self.assertNotEqual(self.repo.value(), before)

    def test_f3_no_untracked_file_yields_a_stable_value(self):
        self.assertEqual(self.repo.value(), self.repo.value())


class TestText(unittest.TestCase):

    def test_f4_quoting_sites_hold_the_formula_verbatim(self):
        command = formula()
        for rel in QUOTING:
            with self.subTest(file=rel):
                self.assertIn(command, (PROJECT_ROOT / rel).read_text(encoding="utf-8"))

    def test_f5_section_states_scope_and_drops_the_excuse(self):
        flat = " ".join(section_241().split())
        for phrase in ("top level of the work tree", "ignored files",
                       "the content of a nested repository",
                       "outside the work tree or to an ignored path"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, flat)
        self.assertNotIn(DROPPED, flat)


if __name__ == "__main__":
    unittest.main()
