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
  interpreter reaches the guard and prints its message (``TC-03``). A local name resolves as
  Python resolves it, a package's ``__init__.py`` first, and no local module stands in for a
  standard-library one. TC-03 parses every ``*.py`` module of a package that it reaches. It fails
  on each static form by which Python would run code that it never parsed: a link, a compiled or
  extension module, a Windows ``*.pyw`` source, and a module that spells ``__path__`` or
  ``submodule_search_locations`` (TASK 124 R2.4, D14 to D16). TC-03 is static: code that runs to
  import, such as ``importlib`` or a change of ``sys.path``, is out of its reach. So is a feature
  that fails only when it runs, such as ``dataclass(slots=True)`` in an imported module;
* each guarded script and the grader, run under a faked 3.9.6 in an empty directory, exit 2, name
  the script that was run and both versions, and write nothing, in that directory or in the
  skills; the grader runs with a stub for each local module it imports before ``run_evals``, and
  holds none of their files at its exit; the preflight reports FAIL and names both versions
  (``TC-04``);
* the installer, given a ``python3`` that reports 3.9.6, exits 2 and names both versions
  (``TC-05``);
* no living document or script claims support for Python 3.10 or older (``TC-06``);
* the installer imports no module from the current directory, which is the target project
  (``TC-07``).

The grader carries no guard of its own. Every committed campaign report records the sha256 of
``grade_figures.py``, and the eval selftest re-derives each report from its corpus (TC-ME-22), so an
edit to the grader would turn every stored report stale. It imports ``run_evals`` at its top,
before it reads an argument or writes a file, and that guard stops it (TASK D6).

TC-04 stubs the local modules that the grader imports before ``run_evals``, so the allowed runs
of this file execute none of their bodies (TASK 123 R2). Under the fake those bodies would run on
the current interpreter and prove nothing about 3.9, and TC-03 parses them. The residual: TC-04
no longer checks them for a write at import, which a real 3.9 would run before the guard. None
of them writes or reads ``sys.version_info`` today.

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


def _run_under_old(path, cwd, prelude=""):
    """*path* run as `__main__` under the faked 3.9.6, after the child code *prelude*."""
    code = (f"{FAKE_VERSION}\n{prelude}import runpy\n"
            f"runpy.run_path({str(path)!r}, run_name='__main__')\n")
    return subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True,
                          text=True, timeout=120)


#: What the grader's child writes at its exit: the files of `GRADER_PATH` that `sys.modules`
#: holds then, the grader aside (TASK 123 R2.2).
LOADED = "held from GRADER_PATH: "


def _local_module(name, dirs=GRADER_PATH):
    """The file that `import <name>` loads from *dirs*, the directories of `GRADER_PATH` unless
    given, as Python resolves it: in each directory, a package's `__init__.py` before a module of
    that name (TASK 124 R2.4). None for a name that no directory holds."""
    for d in dirs:
        for path in (d / name / "__init__.py", d / f"{name}.py"):
            if path.is_file():
                return path
    return None


#: A statement that parses on Python 3.10 and later only.
MATCH_3_10 = "match 1:\n    case 1:\n        pass\n"
#: The suffixes of the modules that Python imports on Linux, macOS or Windows without a source
#: that TC-03 parses: a Windows source, a compiled module and two kinds of extension module. Only
#: an extension module's name carries a platform tag before its suffix. The sets are fixed, so
#: that the walk does not depend on the interpreter that runs it (TASK 124 D15, D16).
UNPARSED_SUFFIXES = (".pyw", ".pyc", ".pyd", ".so")
TAGGED_SUFFIXES = (".pyd", ".so")
#: The names by which a module changes where a package finds its modules (TASK 124 D15, D16).
SEARCH_PATH_NAMES = frozenset({"__path__", "submodule_search_locations"})


def _module_kind(name):
    """How Python can import a file of this *name*: "source" for a `*.py` module, which TC-03
    parses, "unparsed" for a module of `UNPARSED_SUFFIXES`, and None for no module. The module name,
    up to the first dot, is one that an import statement can spell. A cache in `__pycache__/`
    carries a cache tag before `.pyc`, so it is no module (TASK 124 D16)."""
    stem, dot, rest = name.partition(".")
    if not (stem.isidentifier() and dot):
        return None
    if rest == "py":
        return "source"
    if "." + rest in UNPARSED_SUFFIXES or name.endswith(TAGGED_SUFFIXES):
        return "unparsed"
    return None


def _module_files(name, dirs):
    """`(path, kind)` for each file by which Python on Linux, macOS or Windows can import `<name>`
    from *dirs*: a package's `__init__` or a module of that name (TASK 124 D16)."""
    found = []
    for d in dirs:
        for path in sorted(d.glob(f"{name}/__init__.*")) + sorted(d.glob(f"{name}.*")):
            kind = _module_kind(path.name)
            if kind:
                found.append((path, kind))
    return found


def _package_modules(init):
    """Every `*.py` module of the package whose `__init__.py` is *init*, subpackages included, in a
    fixed order with *init* first. TC-03 parses each one, whatever import reaches it: an absolute
    import of a module of the package names only the package to `_top` (TASK 124 R2.4).

    An entry counts when an import statement can spell it: each directory on its way, and its
    module name (`_module_kind`). `__pycache__/` counts, since Python imports it as a subpackage.
    Raises ValueError on each entry that counts and by which Python would run code that TC-03
    never parsed: a package directory that is a symbolic link, a link in it, and a module of
    `UNPARSED_SUFFIXES`. Python imports through a link that `rglob` does not follow. Also raises
    on a `*.py` entry that is no regular file, which Python skips and TC-03 would open: a FIFO
    would hang the read (TASK 124 D14 to D16)."""
    if init.parent.is_symlink():
        raise ValueError(f"{_label(init.parent)}: a package that TC-03 walks is a symbolic link")
    found = []
    for entry in sorted(init.parent.rglob("*")):
        if not all(part.isidentifier() for part in entry.relative_to(init.parent).parts[:-1]):
            continue
        kind = _module_kind(entry.name)
        if entry.is_symlink():
            if kind or entry.name.isidentifier():
                raise ValueError(f"{_label(entry)}: a symbolic link in a package that TC-03 walks")
        elif kind == "unparsed":
            raise ValueError(f"{_label(entry)}: a module that TC-03 cannot parse: compiled, an "
                             "extension or a Windows source")
        elif kind == "source" and entry != init:
            if not entry.is_file():
                raise ValueError(f"{_label(entry)}: a module entry that is no regular file")
            found.append(entry)
    return [init] + found


def _search_path_spellings(tree):
    """`<line>:<name>` for each place where *tree* spells a name of `SEARCH_PATH_NAMES`: as a name,
    an attribute, a keyword, an imported name or a string. A computed spelling is out of reach
    (TASK 124 D16)."""
    found = []
    for node in ast.walk(tree):
        for _field, value in ast.iter_fields(node):
            for item in value if isinstance(value, list) else [value]:
                if isinstance(item, str) and item in SEARCH_PATH_NAMES:
                    found.append(f"{getattr(node, 'lineno', '?')}:{item}")
    return found


def _label(path):
    """*path* relative to the project root when it lies inside it, else as it is."""
    try:
        return str(Path(path).relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _grader_local_imports():
    """The modules that the grader imports at module level before `run_evals`, from a directory of
    `GRADER_PATH`, found in its source as TC-03 finds them. TC-04 stubs each one (TASK 123 R2.1)."""
    tree = ast.parse(GRADER.read_text(encoding="utf-8"))
    names = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            if any(a.name == GRADER_GUARD for a in node.names):
                break
            names.extend(_top(a.name) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names.append(_top(node.module))
    return tuple(n for n in dict.fromkeys(names) if _local_module(n) is not None)


def _stubs_and_report(stubs):
    """Child code: an empty module in `sys.modules` for each name of *stubs*, and a report at exit
    of each module whose file lies in a directory of `GRADER_PATH`, the grader aside."""
    dirs = tuple(str(d) + os.sep for d in GRADER_PATH)
    return ("import atexit, types\n"
            f"for _name in {tuple(stubs)!r}:\n"
            "    sys.modules[_name] = types.ModuleType(_name)\n"
            "def _report():\n"
            "    held = sorted(m.__file__ for m in list(sys.modules.values())\n"
            "                  if isinstance(getattr(m, '__file__', None), str)\n"
            f"                  and m.__file__.startswith({dirs!r})\n"
            f"                  and m.__file__ != {str(GRADER)!r})\n"
            f"    sys.stderr.write({LOADED!r} + repr(held) + '\\n')\n"
            "atexit.register(_report)\n")


def _minimal_env(first_dir):
    """PATH with `first_dir` in front, HOME, and no bytecode written into the repository."""
    return {"PATH": str(first_dir) + os.pathsep + os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", str(first_dir)), "PYTHONDONTWRITEBYTECODE": "1"}


def _executable(path, body):
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _put(path, data=b""):
    """Write *data* at *path*, its directories first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


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
                self._check_before_guard(path)

    def _check_before_guard(self, path):
        """Only the docstring, `__future__` and imports of `STDLIB_3_9` precede the guard of
        *path*, and no module beside *path* stands in for one of them: Python looks in a script's
        own directory first (TASK 124 D16)."""
        index, _floor, tree = guard(path)
        for pos, node in enumerate(tree.body[:index]):
            if (pos == 0 and isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                continue
            if isinstance(node, ast.Import) and all(
                    _top(a.name) in STDLIB_3_9 for a in node.names):
                names = [_top(a.name) for a in node.names]
            elif (isinstance(node, ast.ImportFrom) and node.level == 0
                    and all((node.module, a.name) in FROM_3_9 for a in node.names)):
                names = [_top(node.module)]
            else:
                self.fail(f"{path.name}:{node.lineno} runs before the version guard and "
                          f"may be missing on 3.9: {ast.unparse(node)[:80]}")
            for name in names:
                self.assertEqual([_label(p) for p, _kind in _module_files(name, (path.parent,))],
                                 [], f"{path.name}:{node.lineno}: a module beside the script "
                                     f"stands in for the standard library's {name!r}")

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
        self._walk_names(pending)

    def _walk_names(self, pending, dirs=GRADER_PATH):
        """Walk each module name of *pending*, and the names that its modules import in turn, as
        `import` resolves them from *dirs*. A name of `STDLIB_3_9` has no file in *dirs*, which
        Python would import in its place. A local name has no module there of
        `UNPARSED_SUFFIXES`, which Python may try before the source (TASK 124 D16)."""
        seen = set()
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            files = _module_files(name, dirs)
            if name in STDLIB_3_9:
                self.assertEqual([_label(p) for p, _kind in files], [],
                                 f"a local module stands in for the standard library's {name!r}")
                continue
            self.assertEqual([_label(p) for p, kind in files if kind != "source"], [],
                             f"Python can import {name!r} from a module that TC-03 cannot parse")
            path = _local_module(name, dirs)
            self.assertIsNotNone(path, f"the grader imports {name!r} before run_evals: neither a "
                                       f"3.9 standard-library module nor a local one")
            self._walk_local(path, pending, set())

    def test_every_module_of_a_package_is_walked(self):
        """TC-03 walks every module file of a package it reaches, a module that the package reaches
        only by an absolute import or one of a subpackage among them (TASK 124 R2.4)."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp, "pkg")
            (pkg / "sub").mkdir(parents=True)
            for rel in ("__init__.py", "hidden.py", "sub/__init__.py", "sub/deep.py"):
                (pkg / rel).write_text("import pkg.hidden\n", encoding="utf-8")
            walked = [p.relative_to(pkg).as_posix() for p in _package_modules(pkg / "__init__.py")]
            self.assertEqual(walked, ["__init__.py", "hidden.py", "sub/__init__.py", "sub/deep.py"])
            (pkg / "link.py").symlink_to(pkg / "hidden.py")
            with self.assertRaises(ValueError):
                _package_modules(pkg / "__init__.py")

    def test_a_package_that_python_imports_otherwise_fails_the_walk(self):
        """Each form that Python imports from a package but TC-03 cannot parse fails
        `_package_modules`; Python's own `__pycache__/` and a data file do not (TASK 124 D15)."""
        def package(tmp):
            pkg = Path(tmp, "pkg")
            pkg.mkdir()
            (pkg / "__init__.py").write_text("import pkg.hidden\n", encoding="utf-8")
            return pkg
        cases = {
            "a compiled module beside the sources":
                lambda pkg: (pkg / "hidden.pyc").write_bytes(b""),
            "an extension module": lambda pkg: (pkg / "hidden.so").write_bytes(b""),
            "an extension module of Linux":
                lambda pkg: _put(pkg / "hidden.cpython-311-x86_64-linux-gnu.so"),
            "an extension module of Windows": lambda pkg: _put(pkg / "hidden.cp311-win_amd64.pyd"),
            "a source module of Windows": lambda pkg: _put(pkg / "hidden.pyw"),
            "a compiled module in __pycache__/":
                lambda pkg: _put(pkg / "__pycache__" / "hidden.pyc"),
            "a __pycache__/ that is a link":
                lambda pkg: (pkg / "__pycache__").symlink_to(pkg.parent, target_is_directory=True),
            "a module entry that is a directory": lambda pkg: (pkg / "hidden.py").mkdir(),
        }
        if hasattr(os, "mkfifo"):
            cases["a module entry that is a FIFO"] = lambda pkg: os.mkfifo(pkg / "hidden.py")
        for name, plant in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                pkg = package(tmp)
                plant(pkg)
                with self.assertRaises(ValueError):
                    _package_modules(pkg / "__init__.py")
        with tempfile.TemporaryDirectory() as tmp:
            pkg = package(tmp)
            linked = Path(tmp, "linked")
            linked.symlink_to(pkg, target_is_directory=True)
            with self.assertRaises(ValueError):
                _package_modules(linked / "__init__.py")
            (pkg / "__pycache__").mkdir()
            (pkg / "__pycache__" / "hidden.cpython-39.pyc").write_bytes(b"")
            (pkg / "README.md").write_text("data\n", encoding="utf-8")
            self.assertEqual(_package_modules(pkg / "__init__.py"), [pkg / "__init__.py"])

    def test_the_walk_lists_each_module_that_an_import_statement_can_name(self):
        """The walk lists each `*.py` module whose name and directories an import statement can
        spell, in `__pycache__/` too, which Python imports as a subpackage. It leaves aside each
        entry that no import statement names (TASK 124 D16)."""
        def package(tmp):
            pkg = Path(tmp, "pkg")
            pkg.mkdir()
            (pkg / "__init__.py").write_text("import pkg.hidden\n", encoding="utf-8")
            return pkg
        aside = {
            "an editor's lock, a dangling link":
                lambda pkg: (pkg / ".#hidden.py").symlink_to("user@host.1234"),
            "an AppleDouble file": lambda pkg: _put(pkg / "._hidden.py", b"\x00\x05\x16\x07"),
            "an editor's copy": lambda pkg: _put(pkg / "hidden.orig.py", MATCH_3_10.encode()),
            "a module below a directory that no import names":
                lambda pkg: _put(pkg / ".venv" / "lib" / "hidden.py", MATCH_3_10.encode()),
            "a cache in __pycache__/":
                lambda pkg: _put(pkg / "__pycache__" / "hidden.cpython-39.pyc"),
            "data": lambda pkg: _put(pkg / ".DS_Store"),
        }
        for name, plant in aside.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                pkg = package(tmp)
                plant(pkg)
                self.assertEqual(_package_modules(pkg / "__init__.py"), [pkg / "__init__.py"])
        with tempfile.TemporaryDirectory() as tmp:
            pkg = package(tmp)
            for rel in ("__pycache__/__init__.py", "__pycache__/cached.py"):
                _put(pkg / rel, b"import pkg.hidden\n")
            walked = [p.relative_to(pkg).as_posix() for p in _package_modules(pkg / "__init__.py")]
            self.assertEqual(walked, ["__init__.py", "__pycache__/__init__.py",
                                      "__pycache__/cached.py"])

    def test_the_walk_fails_on_each_static_spelling_of_a_search_path_change(self):
        """A module that changes where a package finds its modules can import one that TC-03 never
        lists. Each static spelling fails the walk, in any module that it walks. The plain name in
        an `__init__.py` is the case of `test_the_walk_fails_on_an_init_that_changes_its_path`
        (TASK 124 D16)."""
        cases = {
            "an attribute of the module object":
                ("__init__.py", "import sys\nsys.modules[__name__].__path__.append('elsewhere')\n"),
            "the search locations of the spec":
                ("__init__.py", "__spec__.submodule_search_locations.append('elsewhere')\n"),
            "a string": ("__init__.py", "globals()['__path__'].append('elsewhere')\n"),
            "a keyword": ("__init__.py", "import importlib.util\nimportlib.util."
                                         "spec_from_file_location('x', 'y', "
                                         "submodule_search_locations=[])\n"),
            "another module of the package":
                ("hidden.py", "import pkg\npkg.__path__.append('elsewhere')\n"),
        }
        walker = TC03GuardsAreReached("test_the_grader_reaches_the_run_evals_guard")
        for name, (rel, text) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                pkg = Path(tmp, "pkg")
                pkg.mkdir()
                (pkg / "__init__.py").write_text("import pkg.hidden\n", encoding="utf-8")
                (pkg / rel).write_text(text, encoding="utf-8")
                with self.assertRaises(AssertionError):
                    walker._walk_local(pkg / "__init__.py", [], set())
        with self.subTest(case="a module outside the package"), \
                tempfile.TemporaryDirectory() as tmp:
            module = Path(tmp, "mod.py")
            module.write_text("import pkg\npkg.__path__.append('elsewhere')\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                walker._walk_local(module, [], set())

    def test_a_module_that_python_finds_before_the_source_fails_the_walk(self):
        """Python tries a compiled or extension module before a source of the same name, and the
        directories of `GRADER_PATH` before the standard library. Either form of a name that the
        walk reaches fails it (TASK 124 D16)."""
        cases = {
            "an extension module beside the source":
                ("second", "mod.cpython-311-x86_64-linux-gnu.so", "mod"),
            "a compiled module in an earlier directory": ("first", "mod.pyc", "mod"),
            "a local module of a standard-library name": ("second", "json.py", "json"),
            "a local package of a standard-library name": ("first", "json/__init__.py", "json"),
        }
        walker = TC03GuardsAreReached("test_the_grader_reaches_the_run_evals_guard")
        for name, (where, rel, imported) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as tmp:
                dirs = (Path(tmp, "first"), Path(tmp, "second"))
                _put(dirs[1] / "mod.py", b"import json\n")
                dirs[0].mkdir()
                _put(Path(tmp, where, rel))
                with self.assertRaises(AssertionError):
                    walker._walk_names([imported], dirs)
        with self.subTest(case="the source alone"), tempfile.TemporaryDirectory() as tmp:
            dirs = (Path(tmp, "first"), Path(tmp, "second"))
            _put(dirs[1] / "mod.py", b"import json\n")
            dirs[0].mkdir()
            walker._walk_names(["mod"], dirs)

    def test_a_module_beside_a_guarded_script_cannot_stand_in_for_the_standard_library(self):
        """A guarded script imports the standard library before its guard, and Python looks in the
        script's own directory first. A module of such a name there fails TC-03 (TASK 124 D16)."""
        checker = TC03GuardsAreReached(
            "test_only_docstring_future_and_3_9_stdlib_imports_precede_each_guard")
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp, "script.py")
            script.write_text("import argparse\nimport sys\nif sys.version_info < (3, 11):\n"
                              "    sys.exit(2)\n", encoding="utf-8")
            checker._check_before_guard(script)
            _put(Path(tmp, "argparse.py"))
            with self.assertRaises(AssertionError):
                checker._check_before_guard(script)

    def test_the_walk_fails_on_an_init_that_changes_its_path(self):
        """An `__init__.py` that names `__path__` can import a module that TC-03 never lists, and
        fails the walk of TC-03 (TASK 124 D15)."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp, "pkg")
            pkg.mkdir()
            (pkg / "__init__.py").write_text("__path__.append('elsewhere')\n", encoding="utf-8")
            walker = TC03GuardsAreReached("test_the_grader_reaches_the_run_evals_guard")
            with self.assertRaises(AssertionError):
                walker._walk_local(pkg / "__init__.py", [], set())

    def test_the_walk_parses_a_module_reached_only_by_an_absolute_import(self):
        """A module that its package reaches only through `import pkg.hidden`, and that does not
        parse under the 3.9 grammar, fails the walk of TC-03 (TASK 124 D14)."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp, "pkg")
            pkg.mkdir()
            (pkg / "__init__.py").write_text("import pkg.hidden\n", encoding="utf-8")
            (pkg / "hidden.py").write_text(MATCH_3_10, encoding="utf-8")
            walker = TC03GuardsAreReached("test_the_grader_reaches_the_run_evals_guard")
            with self.assertRaises(SyntaxError):
                walker._walk_local(pkg / "__init__.py", [], set())

    def test_the_walk_fails_on_a_link_in_a_package(self):
        """A subpackage that its package reaches through a symbolic link fails the walk of TC-03:
        Python imports through the link, which `rglob` does not follow (TASK 124 D14)."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg, real = Path(tmp, "pkg"), Path(tmp, "real")
            pkg.mkdir()
            real.mkdir()
            (real / "__init__.py").write_text(MATCH_3_10, encoding="utf-8")
            (pkg / "__init__.py").write_text("import pkg.sub\n", encoding="utf-8")
            (pkg / "sub").symlink_to(real, target_is_directory=True)
            walker = TC03GuardsAreReached("test_the_grader_reaches_the_run_evals_guard")
            with self.assertRaises(AssertionError):
                walker._walk_local(pkg / "__init__.py", [], set())

    def _walk_local(self, path, pending, walked):
        """Parse *path* under the 3.9 grammar and queue its imports. A module of a package also
        walks each module of the package that it imports relatively, and a package's `__init__.py`
        walks every module of its package. An entry of that package that `_package_modules`
        refuses, or a module that spells a name of `SEARCH_PATH_NAMES`, fails the walk (TASK 124
        R2.4, D14 to D16)."""
        if path in walked:
            return
        walked.add(path)
        if path.name == "__init__.py":
            try:
                modules = _package_modules(path)[1:]
            except ValueError as exc:
                self.fail(str(exc))
            for module in modules:
                self._walk_local(module, pending, walked)
        with self.subTest(module=_label(path)):
            sub = ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))
            self.assertEqual(_search_path_spellings(sub), [],
                             f"{_label(path)} changes where a package finds its modules, so it can "
                             "import a module that TC-03 does not list (TASK 124 D15, D16)")
            for node in _import_time_imports(sub):
                if isinstance(node, ast.Import):
                    pending.extend(_top(a.name) for a in node.names)
                elif node.level == 0:
                    self._names_exist_in_3_9(node, path.name)
                    pending.append(_top(node.module))
                else:
                    self.assertTrue(node.level == 1 and (path.parent / "__init__.py").is_file(),
                                    f"{path.name}:{node.lineno} imports relatively outside a "
                                    "package")
                    targets = [node.module] if node.module else [a.name for a in node.names]
                    for target in targets:
                        module = path.parent / f"{_top(target)}.py"
                        self.assertTrue(module.is_file(),
                                        f"{path.name}:{node.lineno}: the package lacks {target!r}")
                        self._walk_local(module, pending, walked)

    def _names_exist_in_3_9(self, node, where):
        if _top(node.module) not in STDLIB_3_9:
            return  # a local module: its own imports are walked in turn
        missing = [a.name for a in node.names if (node.module, a.name) not in FROM_3_9]
        self.assertEqual(missing, [], f"{where}:{node.lineno} imports names FROM_3_9 does not "
                                      f"list from {node.module}")


class TC04GuardedScriptsStopAndWriteNothing(unittest.TestCase):
    def test_each_script_and_the_grader_under_a_faked_3_9(self):
        minimum, main = stated()
        stubs = _grader_local_imports()
        for path in GUARDED + (GRADER,):
            with self.subTest(script=path.name), tempfile.TemporaryDirectory() as tmp:
                before = _snapshot(WATCHED)
                prelude = _stubs_and_report(stubs) if path == GRADER else ""
                proc = _run_under_old(path, tmp, prelude)
                self.assertEqual(proc.returncode, 2, proc.stderr[-400:])
                for needle in (f"{path.name} needs Python", _version(minimum), _version(main),
                               "this is Python 3.9"):
                    self.assertIn(needle, proc.stderr)
                self.assertEqual(os.listdir(tmp), [])
                self.assertEqual(_snapshot(WATCHED), before, "a guarded run wrote into the skills")
                if path == GRADER:
                    # TASK 123 R2.2: no module body of the grader's local imports ran
                    self.assertIn(LOADED + "[]", proc.stderr, proc.stderr[-800:])

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
