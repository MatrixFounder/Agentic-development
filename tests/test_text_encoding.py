"""Scripts read and write text in UTF-8 (TASK 139, PT-1).

With no `encoding=`, `open`, `read_text` and `write_text` take the codec of the locale: `cp1251`
or `cp1252` on native Windows. Before TASK 139 seven calls of four scripts had none, and under
`cp1251` `generate_wrappers.py --check` reported each of its 12 wrappers as drift. This file pins:

* each script under `.agent/` and `System/`, tracked or new and not ignored, passes an encoding to
  each call that opens a file as text: `open`, `io.open`, `os.fdopen`, `Path.open`, `read_text`
  and `write_text`. A file under a `tests/` or `evals/` directory, and a file named `test_*.py`,
  are out of scope (``TC-E1``);
* the check reports each such call with no encoding, with `encoding=None` or with a mode it cannot
  read. It passes a binary mode, an encoding given by keyword or by position, and an `X.open`
  that takes a path, a file or a member name, as in `gzip.open(p)` or `tarfile.open(fileobj=f)`
  (``TC-E2``);
* `generate_wrappers.py --check` exits 0 under a locale whose codec is not UTF-8, with UTF-8 mode
  off and the streams of that locale (``TC-E3``);
* `calculate_roi.py` writes its report to a `cp1252` stream and exits 0 (``TC-E5``);
* both Windows jobs of `framework-gates.yml` run this file (``TC-E6``, TASK 139 D6);
* the listing takes a new file, and no test, eval, virtualenv, ignored file or tracked file gone
  from the work tree (``TC-E7``).

The check is static and reads that an encoding is given, not its value. A call with `**kwargs`
passes it, and so do an `X.open` whose mode is a variable and the text modes of `gzip.open`;
`subprocess` is not read (TASK 139 §5).
"""
import ast
import codecs
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCOPE = (".agent", "System")
#: Directories whose files are tests or evals: out of scope (TASK 139 D3).
OUT_OF_SCOPE_DIRS = frozenset({"tests", "evals"})
#: Directories of code that this repository does not author, such as a virtualenv of a skill.
THIRD_PARTY_DIRS = frozenset({".venv", "venv", "site-packages", "node_modules"})
#: Position of the mode and of the encoding in each call; `None` is a call that opens text only.
POSITIONS = {"open": (1, 3), "Path.open": (0, 2), "read_text": (None, 0), "write_text": (None, 1)}
#: Receivers of `.open` that open no text file: `os.open` returns a descriptor, the other a URL.
NOT_A_FILE = frozenset({"os", "webbrowser"})
#: Receivers whose `.open` is the built-in `open`.
BUILTIN_OPEN = frozenset({"io", "builtins"})
#: The characters of a mode; a first argument of other text is a path or a member name.
MODE_CHARS = frozenset("rwaxbt+")
#: The keywords of `Path.open`; a call with another keyword is a call of another module.
PATH_OPEN_KEYWORDS = frozenset({"mode", "buffering", "encoding", "errors", "newline"})
SKILLS = ROOT / ".agent" / "skills"
WRAPPERS = SKILLS / "skill-parallel-orchestration" / "scripts" / "generate_wrappers.py"
ROI = SKILLS / "skill-product-solution-blueprint" / "scripts" / "calculate_roi.py"


def _is_mode(node):
    """Whether *node* is a string literal of mode characters only."""
    return (isinstance(node, ast.Constant) and isinstance(node.value, str) and bool(node.value)
            and set(node.value) <= MODE_CHARS)


def _call_kind(node):
    """The key of POSITIONS for the call *node*, or None for a call that opens no text file.

    `X.open` is `Path.open` when its first positional argument is a mode literal, or when it has
    none and each keyword is one of `Path.open`, with a mode literal for `mode`. `gzip.open(p)`,
    `tarfile.open(fileobj=f)` and `ZipFile(p).open(name)` take a path, a file or a name there.
    """
    func = node.func
    if isinstance(func, ast.Name):
        return "open" if func.id == "open" else None
    if not isinstance(func, ast.Attribute):
        return None
    receiver = func.value.id if isinstance(func.value, ast.Name) else None
    if func.attr == "open":
        if receiver in BUILTIN_OPEN:
            return "open"
        if receiver in NOT_A_FILE:
            return None
        if node.args:
            return "Path.open" if _is_mode(node.args[0]) else None
        if any(kw.arg not in PATH_OPEN_KEYWORDS for kw in node.keywords):
            return None
        mode = _argument(node, None, "mode")
        return "Path.open" if mode is None or _is_mode(mode) else None
    if func.attr == "fdopen" and receiver == "os":
        return "open"
    if func.attr in ("read_text", "write_text"):
        return func.attr
    return None


def _argument(node, position, keyword):
    """The node given for *keyword*, by keyword or at *position*; None when the call gives none."""
    for kw in node.keywords:
        if kw.arg == keyword:
            return kw.value
    if position is not None and position < len(node.args):
        return node.args[position]
    return None


def _is_none(value):
    """Whether *value* is the literal `None`."""
    return isinstance(value, ast.Constant) and value.value is None


def text_opens_without_encoding(source, name="<source>"):
    """Sorted (line, kind) of each call in *source* that opens a file as text with no encoding."""
    found = []
    for node in ast.walk(ast.parse(source, name)):
        if not isinstance(node, ast.Call):
            continue
        kind = _call_kind(node)
        if kind is None or any(kw.arg is None for kw in node.keywords):
            continue
        mode_at, encoding_at = POSITIONS[kind]
        encoding = _argument(node, encoding_at, "encoding")
        if encoding is not None and not _is_none(encoding):
            continue
        if mode_at is not None:
            mode = _argument(node, mode_at, "mode")
            if mode is None:
                mode = ast.Constant("r")
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and "b" in mode.value:
                continue
        found.append((node.lineno, kind))
    return sorted(found)


def scripts_in_scope(root=ROOT):
    """The `*.py` files under SCOPE that git tracks or would add, less tests, evals and third-party
    code (TASK 139 D3). A tracked file gone from the work tree is not listed."""
    listed = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
                             "--", *SCOPE], cwd=str(root), capture_output=True,
                            check=True).stdout.decode("utf-8")
    paths = []
    for rel in dict.fromkeys(filter(None, listed.split("\0"))):
        parts = Path(rel).parts
        skipped = (OUT_OF_SCOPE_DIRS | THIRD_PARTY_DIRS).intersection(parts[:-1])
        if (rel.endswith(".py") and not skipped and not parts[-1].startswith("test_")
                and (Path(root) / rel).is_file()):
            paths.append(rel)
    return paths


class TestTextEncoding(unittest.TestCase):
    def test_e1_each_script_in_scope_passes_an_encoding(self):
        try:
            paths = scripts_in_scope()
        except (OSError, subprocess.CalledProcessError) as exc:
            self.skipTest(f"git ls-files is not available here: {exc}")
        self.assertGreater(len(paths), 50, "the scope lists too few scripts to be the tree")
        found = []
        for rel in paths:
            source = (ROOT / rel).read_text(encoding="utf-8")
            found += [f"{rel}:{line} {kind}"
                      for line, kind in text_opens_without_encoding(source, rel)]
        self.assertEqual(found, [], "text opened with no encoding (ARCHITECTURE §8, Rule 5)")

    def test_e2_the_check_reports_each_form(self):
        reported = (
            'open(p)\n'
            'open(p, "w")\n'
            'open(p, mode="a")\n'
            'open(p, "r", -1, None)\n'
            'io.open(p, "rt")\n'
            'os.fdopen(fd, "w")\n'
            'p.open("w")\n'
            'p.open()\n'
            'p.read_text()\n'
            'p.write_text(s)\n'
            'p.read_text(encoding=None)\n'
            'open(p, m)\n'
            'p.open(mode="w")\n'
            'builtins.open(p)\n'
            'p.open("r")\n'
            'p.open("a")\n'
            'p.open("r+")\n'
            'p.open("xt")\n'
        )
        self.assertEqual([line for line, _ in text_opens_without_encoding(reported)],
                         list(range(1, reported.count("\n") + 1)))
        passed = (
            'open(p, "rb")\n'
            'open(p, mode="wb")\n'
            'open(p, encoding="utf-8")\n'
            'open(p, "w", -1, "utf-8")\n'
            'os.fdopen(fd, "wb")\n'
            'p.open("rb")\n'
            'p.open("w", -1, "utf-8")\n'
            'p.read_text("utf-8")\n'
            'p.write_text(s, "utf-8")\n'
            'p.read_text(encoding=enc)\n'
            'p.read_bytes()\n'
            'os.open(p, os.O_RDONLY)\n'
            'webbrowser.open(url)\n'
            'open(p, **kw)\n'
            'io.open(p, "rb")\n'
            'io.open(p, "w", -1, "utf-8")\n'
            'builtins.open(p, "rb")\n'
            'gzip.open(p, "rb")\n'
            'tarfile.open(archive)\n'
            'zipfile.ZipFile(p).open("x.json")\n'
            'zf.open("build.json")\n'
            'webbrowser.get().open(url)\n'
            'os.open("x", os.O_RDONLY)\n'
            'tarfile.open(fileobj=buf, mode="r:gz")\n'
            'gzip.open(filename=p)\n'
            'zf.open(name="x.json")\n'
            'p.open(mode="rb")\n'
        )
        self.assertEqual(text_opens_without_encoding(passed), [])

    def test_e3_generate_wrappers_check_under_a_locale_that_is_not_utf_8(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("LC_", "PYTHON"))}
        env.update(LC_ALL="C", LANG="C", PYTHONDONTWRITEBYTECODE="1")
        child = [sys.executable, "-s", "-X", "utf8=0"]
        probe = subprocess.run(
            child + ["-c", "import locale; print(locale.getpreferredencoding(False))"],
            env=env, capture_output=True, text=True, errors="replace", timeout=60)
        codec = probe.stdout.strip()
        if probe.returncode or codecs.lookup(codec).name == "utf-8":
            self.skipTest(f"the child's locale codec is {codec or probe.stderr.strip()!r}")
        # The child writes in the codec of its locale; its text is read for `OK` and a message.
        run = subprocess.run(child + [str(WRAPPERS), "--check"], cwd=str(ROOT), env=env,
                             capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=60)
        self.assertEqual(run.returncode, 0, f"codec {codec}: {run.stdout}{run.stderr}")
        self.assertIn("OK", run.stdout)

    def test_e5_calculate_roi_writes_to_a_cp1252_stream(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(PYTHONIOENCODING="cp1252", PYTHONDONTWRITEBYTECODE="1")
        run = subprocess.run([sys.executable, "-s", str(ROI), "--users", "10", "--price", "5",
                              "--small", "1"], cwd=str(ROOT), env=env, capture_output=True,
                             text=True, encoding="cp1252", errors="replace", timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("Business Case Analysis", run.stdout)

    def test_e6_the_windows_jobs_run_this_check(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML does not import: TC-E6 reads the workflow as YAML")
        workflow = ROOT / ".github" / "workflows" / "framework-gates.yml"
        jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
        windows = [job for job in jobs.values() if job.get("runs-on") == "windows-latest"]
        self.assertTrue(windows, "the Windows jobs")
        for job in windows:
            runs = [step.get("run", "") for step in job.get("steps", [])
                    if step.get("name") == "Run the text-encoding check"]
            self.assertEqual(len(runs), 1, job.get("name"))
            self.assertIn("tests/test_text_encoding.py", runs[0], job.get("name"))

    def test_e7_the_listing(self):
        """A new file is listed; a test, an eval, a virtualenv, an ignored file and a tracked file
        gone from the work tree are not."""
        import shutil
        import tempfile
        if shutil.which("git") is None:
            self.skipTest("git is not available here")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = ("tracked.py", "new.py", "gone.py", "tests/helper.py", "evals/grade.py",
                     "skill/test_x.py", "skill/.venv/lib/site.py", "ignored.py", "notes.md")
            for rel in files:
                path = root / ".agent" / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x = 1\n", encoding="utf-8")
            (root / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
            env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
            for command in (["init", "-q"], ["add", ".agent/tracked.py", ".agent/gone.py"]):
                subprocess.run(["git", *command], cwd=tmp, env=env, check=True,
                               capture_output=True)
            (root / ".agent" / "gone.py").unlink()
            self.assertEqual(sorted(scripts_in_scope(root)), [".agent/new.py", ".agent/tracked.py"])


if __name__ == "__main__":
    unittest.main()
