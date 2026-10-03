"""Python floor contract test (TASK 109, WI-33).

The framework states one minimum Python and one main version, in README §3: 3.11 and 3.14 when
this file was written. Before TASK 109 six places claimed 3.9, while CI tested only 3.11 and 3.13
and five ``skill-creator`` scripts failed at import on 3.9. On 3.9.6 the figure-eval grader wrote
``report.json``, skipped ``benchmark.json`` with a note about a ``TypeError``, and exited 0.

The code now carries the minimum where a user starts the framework's Python: the installer, the
preflight, and the benchmark scripts of ``skill-creator`` and of the figure evals. This file pins:

* README §3 states the pair, the Russian README and ``ORCHESTRATOR.md`` state the same pair
  (``TC-01``);
* the preflight, the installer, the six guards and the CI matrix carry that minimum, and no CI job
  runs below it (``TC-02``);
* each guard runs before anything but the docstring, ``__future__`` and standard-library imports
  of modules and names that Python 3.9 has; each guarded file, the grader and the modules the
  grader imports first parse under the 3.9 grammar and import only such names, so an old
  interpreter reaches the guard and prints its message (``TC-03``). A feature that fails only when
  it runs, such as ``dataclass(slots=True)`` in an imported module, is out of its reach;
* each guarded script and the grader, run under a faked 3.9.6 in an empty directory, exit 2, name
  the script that was run and both versions, and write nothing, in that directory or in the
  skills; the preflight reports FAIL and names both versions (``TC-04``);
* the installer, given a ``python3`` that reports 3.9.6, exits 2 and names both versions
  (``TC-05``);
* no living document or script claims support for Python 3.10 or older (``TC-06``);
* the installer imports no module from the current directory, which is the target project
  (``TC-07``).

The grader carries no guard of its own. Every committed campaign report records the sha256 of
``grade_figures.py``, and the eval selftest re-derives each report from its corpus (TC-ME-22), so an
edit to the grader would turn every stored report stale. It imports ``run_evals`` at its top,
before it reads an argument or writes a file, and that guard stops it (TASK D6).

``TC-06`` is a tripwire for the known spellings of a claim, not a parser of intent.
"""

import ast
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

README_EN = PROJECT_ROOT / "README.md"
README_RU = PROJECT_ROOT / "README.ru.md"
ORCHESTRATOR = PROJECT_ROOT / "System" / "Docs" / "ORCHESTRATOR.md"
DOCTOR = PROJECT_ROOT / "System" / "scripts" / "doctor.py"
INSTALL_SH = PROJECT_ROOT / "install.sh"
CI_WORKFLOW = PROJECT_ROOT / ".github" / "workflows" / "framework-gates.yml"
EVALS = PROJECT_ROOT / ".agent" / "skills" / "mermaid-authoring-guidelines" / "evals"
SKILL_SCRIPTS = PROJECT_ROOT / ".agent" / "skills" / "mermaid-authoring-guidelines" / "scripts"
CREATOR_SCRIPTS = PROJECT_ROOT / ".agent" / "skills" / "skill-creator" / "scripts"

#: The scripts that stop below the minimum before they write anything (TASK R2, R3).
GUARDED = (
    CREATOR_SCRIPTS / "aggregate_benchmark.py",
    CREATOR_SCRIPTS / "verify_pin.py",
    EVALS / "run_evals.py",
    EVALS / "render_corpus.py",
    EVALS / "selftest_figure_evals.py",
    PROJECT_ROOT / "System" / "scripts" / "install.py",
)
#: The figure-eval grader, stopped by the guard of the `run_evals` it imports (TASK D6).
GRADER = EVALS / "grade_figures.py"
GRADER_GUARD = "run_evals"
#: Where the grader resolves its local imports: `sys.path` gets the evals and the scripts.
GRADER_PATH = (EVALS, SKILL_SCRIPTS)
#: Directories a guarded run must leave as they were (TC-04).
WATCHED = (EVALS, SKILL_SCRIPTS, CREATOR_SCRIPTS, PROJECT_ROOT / "System" / "scripts")

#: Standard-library modules Python 3.9 has. A guard may follow imports of these only, so that an
#: old interpreter reaches it. A module added in 3.10 or later (`tomllib`, ...) is absent on
#: purpose; the running interpreter's `sys.stdlib_module_names` would accept it.
STDLIB_3_9 = frozenset("""
    __future__ abc argparse ast base64 bisect collections concurrent contextlib copy csv
    dataclasses datetime decimal difflib enum errno fnmatch fractions functools glob gzip hashlib
    heapq hmac html importlib inspect io itertools json locale logging math operator os pathlib
    pickle platform pprint queue random re select shlex shutil signal socket stat statistics
    string struct subprocess sys tempfile textwrap threading time traceback types typing
    unicodedata unittest urllib uuid warnings weakref webbrowser xml zipfile zlib
""".split())
#: Names a `from <module> import <name>` may take before a guard, or in a module the grader imports
#: first. Each exists in Python 3.9. Add a pair only after checking that; `typing.Self`,
#: `datetime.UTC` and `enum.StrEnum` are 3.11 names and stay out.
FROM_3_9 = frozenset({
    ("__future__", "annotations"), ("bisect", "bisect_left"), ("bisect", "bisect_right"),
    ("collections", "defaultdict"), ("dataclasses", "dataclass"), ("dataclasses", "field"),
    ("datetime", "datetime"), ("datetime", "timezone"), ("pathlib", "Path"),
    ("typing", "Callable"), ("typing", "Iterable"), ("typing", "Optional"),
})

#: What an old interpreter reports in TC-04 and TC-05: a namedtuple, so that indexing, slicing,
#: attribute access and tuple comparison all behave as on the real `sys.version_info`.
FAKE_VERSION = ("import collections, sys; "
                "sys.version_info = collections.namedtuple('version_info', "
                "'major minor micro releaselevel serial')(3, 9, 6, 'final', 0)")

EN_MIN = re.compile(r"^- \*\*Minimum:\*\* Python `(\d+)\.(\d+)`", re.M)
EN_MAIN = re.compile(r"^- \*\*Main:\*\* Python `(\d+)\.(\d+)`", re.M)
RU_MIN = re.compile(r"^- \*\*Минимум:\*\* Python `(\d+)\.(\d+)`", re.M)
RU_MAIN = re.compile(r"^- \*\*Основная:\*\* Python `(\d+)\.(\d+)`", re.M)
ORCH_PAIR = re.compile(r"^- Python (\d+)\.(\d+) or newer; (\d+)\.(\d+) is the main version", re.M)

#: TC-06 — the spellings of a claim to support Python 3.0–3.10, case-insensitive, matched across
#: a line break.
OLD = r"3\.(?:[0-9]|10)(?![0-9])"
CLAIM = re.compile(
    rf"python\s*`?{OLD}`?\s*\+"
    rf"|python\s*`?{OLD}`?\s+(?:or|and)\s+(?:newer|later|higher|greater|above|up)\b"
    rf"|python\s*`?{OLD}`?\s+(?:и|или)\s+(?:выше|новее|старше|позже)"
    rf"|python\s*(?:>=|=>|≥)\s*`?{OLD}"
    rf"|(?:requires-python|python_requires)\s*=\s*[\"']\s*>=\s*{OLD}"
    r"|REQUIRED_PYTHON\s*=\s*\(\s*3\s*,\s*(?:[0-9]|10)\s*\)",
    re.I)

#: TC-06 — where a claim would be read as current: the top level of docs/, except the current
#: task's own TASK and PLAN, which quote the old claims as the problem. Archived records and the
#: changelogs quote them as history; fixtures and corpora hold captured text; a skill's
#: `examples/` hold sample content about the user's code.
CLAIM_FILES = ("README.md", "README.ru.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "install.sh",
               "pyproject.toml", "setup.cfg")
CLAIM_DOCS_SKIP = {"docs/TASK.md", "docs/PLAN.md"}
CLAIM_DIRS = ("System", ".agent/skills", ".agent/workflows", ".agent/tools", ".agent/rules",
              ".claude/commands", ".claude/agents", ".github")
CLAIM_SUFFIXES = {".md", ".py", ".sh", ".yml", ".yaml", ".toml", ".cfg"}
CLAIM_SKIP_PARTS = {"corpus", "fixtures", "examples", "__pycache__", "node_modules"}
#: Files that state since which version a Python feature exists. A fact about Python, not a
#: version the framework supports (TASK §7).
FACT_FILES = {".agent/skills/developer-guidelines/references/languages/python.md"}


def _version(pair):
    return "%d.%d" % pair


def _one(rx, text, what):
    found = rx.findall(text)
    if len(found) != 1:
        raise AssertionError(f"{what}: expected one statement, found {len(found)}")
    return tuple(int(x) for x in found[0])


def stated():
    """(minimum, main version) as README §3 states them."""
    text = README_EN.read_text(encoding="utf-8")
    return (_one(EN_MIN, text, "README.md §3 minimum"),
            _one(EN_MAIN, text, "README.md §3 main version"))


def _is_version_test(test):
    return (isinstance(test, ast.Compare) and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Lt)
            and ast.unparse(test.left) == "sys.version_info"
            and isinstance(test.comparators[0], ast.Tuple))


def guard(path):
    """(index of the guard among top-level statements, the floor it checks, the module tree)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.If) and _is_version_test(node.test):
            exits = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                     and ast.unparse(n.func) == "sys.exit"
                     and [ast.unparse(a) for a in n.args] == ["2"]]
            if exits:
                return i, tuple(ast.literal_eval(node.test.comparators[0])), tree
    raise AssertionError(f"{path.relative_to(PROJECT_ROOT)}: no top-level guard ending in "
                         f"sys.exit(2)")


def _import_time_imports(tree):
    """Import nodes that run at import time: top level and inside `try`/`if`, not in a def."""
    found, stack = [], list(tree.body)
    while stack:
        node = stack.pop(0)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            found.append(node)
        stack.extend(child for child in ast.iter_child_nodes(node) if isinstance(child, ast.stmt))
    return found


def _top(name):
    return (name or "").split(".")[0]


def _snapshot(dirs):
    state = {}
    for root in dirs:
        for path in root.rglob("*"):
            if "__pycache__" in path.parts or not path.is_file():
                continue
            st = path.stat()
            state[str(path)] = (st.st_size, st.st_mtime_ns)
    return state


def _run_under_old(path, cwd):
    code = f"{FAKE_VERSION}; import runpy; runpy.run_path({str(path)!r}, run_name='__main__')"
    return subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True,
                          text=True, timeout=120)


def _minimal_env(first_dir):
    """PATH with `first_dir` in front, HOME, and no bytecode written into the repository."""
    return {"PATH": str(first_dir) + os.pathsep + os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", str(first_dir)), "PYTHONDONTWRITEBYTECODE": "1"}


def _executable(path, body):
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


class TC01ThePairIsStated(unittest.TestCase):
    def test_readme_pair_and_orchestrator_state_the_same_pair(self):
        minimum, main = stated()
        text = README_RU.read_text(encoding="utf-8")
        self.assertEqual(_one(RU_MIN, text, "README.ru.md §3 minimum"), minimum)
        self.assertEqual(_one(RU_MAIN, text, "README.ru.md §3 main version"), main)
        pairs = ORCH_PAIR.findall(ORCHESTRATOR.read_text(encoding="utf-8"))
        self.assertEqual(len(pairs), 1, "ORCHESTRATOR.md states the pair once")
        self.assertEqual((tuple(map(int, pairs[0][:2])), tuple(map(int, pairs[0][2:]))),
                         (minimum, main))
        self.assertLess(minimum, main)


class TC02EveryPointCarriesTheFloor(unittest.TestCase):
    def setUp(self):
        self.minimum, self.main = stated()

    def test_preflight(self):
        values = {}
        for node in ast.parse(DOCTOR.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                name = getattr(node.targets[0], "id", "")
                if name in ("REQUIRED_PYTHON", "RECOMMENDED_PYTHON"):
                    values[name] = tuple(ast.literal_eval(node.value))
        self.assertEqual(values.get("REQUIRED_PYTHON"), self.minimum)
        self.assertEqual(values.get("RECOMMENDED_PYTHON"), self.main)

    def test_installer(self):
        text = INSTALL_SH.read_text(encoding="utf-8")
        checks = re.findall(r"sys\.version_info < \((\d+), (\d+)\)", text)
        self.assertEqual([tuple(int(x) for x in c) for c in checks], [self.minimum],
                         "install.sh checks the minimum exactly once")
        missing = [line for line in text.splitlines() if "python3 not found" in line]
        self.assertEqual(len(missing), 1)
        for version in (self.minimum, self.main):
            self.assertIn(_version(version), missing[0])
        for line in text.splitlines():
            if re.search(r"\bpython3\b.*\s-c\s", line):
                self.assertRegex(line, r"\bpython3\s+-[IP]\s", f"install.sh: {line.strip()}")

    def test_guards(self):
        for path in GUARDED:
            with self.subTest(script=path.name):
                self.assertEqual(guard(path)[1], self.minimum)

    def test_ci_runs_nothing_below_the_minimum(self):
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        matrix = re.findall(r"python-version:\s*\[([^\]]*)\]", text)
        self.assertEqual(len(matrix), 1, "one version matrix in framework-gates.yml")
        versions = [tuple(map(int, v.split("."))) for v in re.findall(r'"(\d+\.\d+)"', matrix[0])]
        for version in (self.minimum, self.main):
            self.assertIn(version, versions)
        singles = [tuple(map(int, v.split(".")))
                   for v in re.findall(r"python-version:\s*[\"']?(\d+\.\d+)[\"']?\s*$", text,
                                       re.M)]
        self.assertTrue(singles, "the single-version jobs name their Python")
        below = [v for v in versions + singles if v < self.minimum]
        self.assertEqual(below, [], "a CI job runs below the minimum")


class TC03GuardsAreReached(unittest.TestCase):
    def test_only_docstring_future_and_3_9_stdlib_imports_precede_each_guard(self):
        for path in GUARDED:
            with self.subTest(script=path.name):
                index, _floor, tree = guard(path)
                for pos, node in enumerate(tree.body[:index]):
                    if (pos == 0 and isinstance(node, ast.Expr)
                            and isinstance(node.value, ast.Constant)
                            and isinstance(node.value.value, str)):
                        continue
                    if isinstance(node, ast.Import) and all(
                            _top(a.name) in STDLIB_3_9 for a in node.names):
                        continue
                    if (isinstance(node, ast.ImportFrom) and node.level == 0
                            and all((node.module, a.name) in FROM_3_9 for a in node.names)):
                        continue
                    self.fail(f"{path.name}:{node.lineno} runs before the version guard and "
                              f"may be missing on 3.9: {ast.unparse(node)[:80]}")

    def test_guarded_files_parse_under_the_3_9_grammar(self):
        for path in GUARDED:
            with self.subTest(script=path.name):
                ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))

    def test_the_grader_reaches_the_run_evals_guard(self):
        tree = ast.parse(GRADER.read_text(encoding="utf-8"), feature_version=(3, 9))
        names = [a.name for node in tree.body if isinstance(node, ast.Import) for a in node.names]
        self.assertIn(GRADER_GUARD, names, "grade_figures.py imports run_evals at module level")
        self.assertIn(EVALS / f"{GRADER_GUARD}.py", GUARDED)
        # Every local module the grader imports before run_evals, and what those import in turn,
        # must parse under 3.9 and import only what 3.9 has; otherwise an old interpreter stops
        # with a traceback before the guard.
        index = next(i for i, node in enumerate(tree.body) if isinstance(node, ast.Import)
                     and any(a.name == GRADER_GUARD for a in node.names))
        pending = []
        for node in tree.body[:index]:
            if isinstance(node, ast.Import):
                pending.extend(_top(a.name) for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                self._names_exist_in_3_9(node, "grade_figures.py")
                pending.append(_top(node.module))
        seen = set()
        while pending:
            name = pending.pop()
            if name in seen or name in STDLIB_3_9:
                continue
            seen.add(name)
            files = [d / f"{name}.py" for d in GRADER_PATH if (d / f"{name}.py").is_file()]
            self.assertTrue(files, f"the grader imports {name!r} before run_evals: neither a "
                                   f"3.9 standard-library module nor a local one")
            with self.subTest(module=name):
                sub = ast.parse(files[0].read_text(encoding="utf-8"), feature_version=(3, 9))
                for node in _import_time_imports(sub):
                    if isinstance(node, ast.Import):
                        pending.extend(_top(a.name) for a in node.names)
                    elif node.level == 0:
                        self._names_exist_in_3_9(node, files[0].name)
                        pending.append(_top(node.module))

    def _names_exist_in_3_9(self, node, where):
        if _top(node.module) not in STDLIB_3_9:
            return  # a local module: its own imports are walked in turn
        missing = [a.name for a in node.names if (node.module, a.name) not in FROM_3_9]
        self.assertEqual(missing, [], f"{where}:{node.lineno} imports names FROM_3_9 does not "
                                      f"list from {node.module}")


class TC04GuardedScriptsStopAndWriteNothing(unittest.TestCase):
    def test_each_script_and_the_grader_under_a_faked_3_9(self):
        minimum, main = stated()
        for path in GUARDED + (GRADER,):
            with self.subTest(script=path.name), tempfile.TemporaryDirectory() as tmp:
                before = _snapshot(WATCHED)
                proc = _run_under_old(path, tmp)
                self.assertEqual(proc.returncode, 2, proc.stderr[-400:])
                for needle in (f"{path.name} needs Python", _version(minimum), _version(main),
                               "this is Python 3.9"):
                    self.assertIn(needle, proc.stderr)
                self.assertEqual(os.listdir(tmp), [])
                self.assertEqual(_snapshot(WATCHED), before, "a guarded run wrote into the skills")

    def test_under_python_m_each_guard_names_its_own_module(self):
        # `python -m <package>` leaves `__main__.py` in argv[0]; that name would tell nothing.
        for path in GUARDED:
            with self.subTest(script=path.name), tempfile.TemporaryDirectory() as tmp:
                code = (f"{FAKE_VERSION}; import importlib.util; "
                        f"sys.argv[0] = {str(Path(tmp) / '__main__.py')!r}; "
                        f"spec = importlib.util.spec_from_file_location('guarded', {str(path)!r}); "
                        "spec.loader.exec_module(importlib.util.module_from_spec(spec))")
                proc = subprocess.run([sys.executable, "-B", "-c", code], cwd=tmp,
                                      capture_output=True, text=True, timeout=120)
                self.assertEqual(proc.returncode, 2, proc.stderr[-400:])
                self.assertIn(f"{path.name} needs Python", proc.stderr)

    def test_the_preflight_reports_both_versions(self):
        minimum, main = stated()
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_under_old(DOCTOR, tmp)
        fail = [line for line in proc.stdout.splitlines() if line.startswith("[FAIL] Python")]
        self.assertEqual(len(fail), 1, proc.stdout[-400:])
        for version in (minimum, main):
            self.assertIn(_version(version), fail[0])
        self.assertNotEqual(proc.returncode, 0)


class TC05InstallerStopsOnAnOldInterpreter(unittest.TestCase):
    def test_install_sh_with_a_python3_that_reports_3_9(self):
        minimum, main = stated()
        with tempfile.TemporaryDirectory() as tmp:
            fake_py = Path(tmp) / "fake_python3.py"
            fake_py.write_text(
                f"{FAKE_VERSION}\n"
                "args = sys.argv[1:]\n"
                "if args[:1] == ['-c']:\n"
                "    code = args[1]\n"
                "elif args[:1] in (['-'], []):\n"
                "    code = sys.stdin.read()\n"
                "else:\n"
                "    sys.exit('fake python3: unsupported arguments %r' % (args,))\n"
                "exec(compile(code, '<fake>', 'exec'), {'__name__': '__main__'})\n",
                encoding="utf-8")
            fake = Path(tmp) / "python3"
            _executable(fake, "#!/bin/sh\nexec "
                              f"{shlex.quote(sys.executable)} {shlex.quote(str(fake_py))} \"$@\"\n")
            env = _minimal_env(tmp)
            try:
                probe = subprocess.run([str(fake), "-c", "print('ok')"], env=env,
                                       capture_output=True, text=True, timeout=30)
            except PermissionError as exc:
                self.skipTest(f"the temporary directory does not run executables: {exc}")
            self.assertEqual(probe.stdout.strip(), "ok", probe.stderr)
            proc = subprocess.run(["bash", str(INSTALL_SH), "--help"], cwd=tmp, env=env,
                                  capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 2, proc.stdout[-300:] + proc.stderr[-300:])
        for needle in (_version(minimum), _version(main), "Python 3.9 found"):
            self.assertIn(needle, proc.stderr)


class TC06NoOlderPythonIsClaimed(unittest.TestCase):
    def test_living_documents_and_scripts(self):
        paths = [PROJECT_ROOT / name for name in CLAIM_FILES if (PROJECT_ROOT / name).is_file()]
        paths += [path for path in sorted((PROJECT_ROOT / "docs").glob("*.md"))
                  if path.relative_to(PROJECT_ROOT).as_posix() not in CLAIM_DOCS_SKIP]
        for root in CLAIM_DIRS:
            if not (PROJECT_ROOT / root).is_dir():
                continue
            for path in sorted((PROJECT_ROOT / root).rglob("*")):
                rel = path.relative_to(PROJECT_ROOT)
                if (path.is_file() and path.suffix in CLAIM_SUFFIXES
                        and not CLAIM_SKIP_PARTS & set(rel.parts)
                        and rel.as_posix() not in FACT_FILES):
                    paths.append(path)
        hits = []
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in CLAIM.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                hits.append(f"{path.relative_to(PROJECT_ROOT)}:{line}: "
                            f"{' '.join(match.group(0).split())}")
        self.assertEqual(hits, [], "\n".join(hits))


class TC07InstallerImportsNothingFromTheTarget(unittest.TestCase):
    def test_decoy_modules_in_the_current_directory_stay_unread(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "decoy-ran"
            for name in ("yaml", "linecache"):
                (Path(tmp) / f"{name}.py").write_text(
                    f"open({str(marker)!r}, 'a').write({name!r})\n", encoding="utf-8")
            shim = Path(tmp) / "bin"
            shim.mkdir()
            _executable(shim / "python3", f"#!/bin/sh\nexec {shlex.quote(sys.executable)} \"$@\"\n")
            env = _minimal_env(shim)
            try:
                subprocess.run([str(shim / "python3"), "-c", "pass"], env=env, timeout=30)
            except PermissionError as exc:
                self.skipTest(f"the temporary directory does not run executables: {exc}")
            proc = subprocess.run(["bash", str(INSTALL_SH), "--help"], cwd=tmp, env=env,
                                  capture_output=True, text=True, timeout=60)
            ran = marker.read_text() if marker.exists() else ""
        self.assertEqual(ran, "", "install.sh imported a module from the target project")
        self.assertTrue(proc.returncode == 0 or "PyYAML" in proc.stderr,
                        proc.stdout[-300:] + proc.stderr[-300:])


if __name__ == "__main__":
    unittest.main()
