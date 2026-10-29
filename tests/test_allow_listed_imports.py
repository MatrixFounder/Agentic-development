"""TASK 134 (WI-39): a Python script that an allow rule runs imports no module planted beside it.

Each test copies a script, and the files it loads, into a temporary root, plants modules beside
the copy and runs it as the rule runs it: ``python3 <path> <arguments>``. A planted module creates
a sentinel file when it runs. The planted names are each top-level module that the script and its
siblings import, ``__future__``, and ``msvcrt``, ``_winapi``, ``fcntl`` and ``_wmi``, for which the
standard library probes on the platforms that lack them.

* ``TC-AL1``: each of the 14 scripts, with arguments that reach its work: its exit code equals that
  of a run with nothing planted, which ends with the exit code of `SCRIPTS` and without a
  traceback, and no sentinel exists.
* ``TC-AL2``: each script that loads siblings, with a package and an extension module planted
  under the name of each sibling module, and a ``.pyc`` planted in ``__pycache__/`` for each
  sibling module and for a submodule of each sibling package: its exit code equals that of a run
  with nothing planted, and no sentinel exists.
* ``TC-AL3``: TC-AL1 through a path in other letter case, where the volume ignores letter case,
  for one script of each group.
* ``TC-AL4``: ``tests/run_tests.py`` with stub test modules: a module planted in ``tests/`` or
  ``tests/installer/`` under a standard-library name is not chosen during the discovery; ``_wmi``,
  ``msvcrt`` and ``_winapi`` planted there answer no probe; a ``_base.py`` planted in ``tests/``
  does not stand in for the installer tests' helper.
* ``TC-AL5``: none of the 14 scripts holds ``from __future__`` or inserts a directory into
  ``sys.path`` at module level, and each runs the guard before any import but ``os`` and ``sys``.
  The guard is one code in every copy, the three older ones of ``update_state.py``,
  ``archive_move.py`` and ``rebase_links.py`` among them; the comment above it and ``_load`` are
  one text in each group. A fix of one copy fails until each copy has it.
"""
import ast
import importlib.machinery
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ".agent/skills"
EXTRA = ("__future__", "msvcrt", "_winapi", "fcntl", "_wmi")
MERMAID_DOC = "# Doc\n\n```mermaid\nflowchart TD\n  A[Start] --> B[End]\n```\n"
PLAN = ("# PLAN 1 — A plan\n\n## Schedule\n\n<!-- contract:schedule -->\n\n```json\n"
        '{"schema": "plan-schedule/v1", "tasks": [{"id": "1.A", "title": "A", "stage": "Build", '
        '"est": 1, "deps": [], "status": "done"}]}\n```\n')


def _write(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


#: Each script: its exit code with nothing planted, its path, the trees the run copies, its siblings
#: (modules and packages beside it, which TC-AL2 shadows), the inputs it reads and its arguments.
#: `doctor` and `security_lint` report the empty root with exit 1, after their checks ran.
SCRIPTS = {
    "scan_register": dict(
        exit=0,
        path=f"{S}/artifact-formalizer/scripts/scan_register.py",
        copy=[f"{S}/artifact-formalizer"], siblings=(),
        files={"doc.md": "# Doc\n\nThe tool reads this line.\n"}, args=["doc.md"]),
    "task_id_tool": dict(
        exit=0,
        path=".agent/tools/task_id_tool.py", copy=[".agent/tools/task_id_tool.py"], siblings=(),
        files={"docs/tasks/.keep": ""}, args=["demo", "--proposed-id", "1", "--no-correction"]),
    "check_prompt_references": dict(
        exit=0,
        path="System/scripts/check_prompt_references.py",
        copy=["System/scripts/check_prompt_references.py"], siblings=(),
        files={"AGENTS.md": "See System/Agents/01_a.md.\n", "System/Agents/01_a.md": "# A\n"},
        args=["--root", "."]),
    "doctor": dict(
        exit=1,
        path="System/scripts/doctor.py", copy=["System/scripts/doctor.py"], siblings=(),
        files={}, args=[]),
    "security_lint": dict(
        exit=1,
        path="System/scripts/security_lint.py", copy=["System/scripts/security_lint.py"],
        siblings=(), files={}, args=["--root", "."]),
    "smoke_workflows": dict(
        exit=0,
        path="System/scripts/smoke_workflows.py",
        copy=["System/scripts/smoke_workflows.py", ".agent/workflows"], siblings=(), files={},
        args=["--root", "."]),
    "validate_skills": dict(
        exit=0,
        path="System/scripts/validate_skills.py",
        copy=["System/scripts/validate_skills.py", f"{S}/skill-creator"], siblings=(),
        files={}, args=["--root", "."]),
    "selftest_scan": dict(
        exit=0,
        path=f"{S}/artifact-formalizer/scripts/selftest_scan.py",
        copy=[f"{S}/artifact-formalizer"], siblings=("scan_register",), files={}, args=[]),
    "lint_mermaid": dict(
        exit=0,
        path=f"{S}/mermaid-authoring-guidelines/scripts/lint_mermaid.py",
        copy=[f"{S}/mermaid-authoring-guidelines"],
        siblings=("mermaid_model", "planarity", "lint_mermaid_parts"),
        files={"doc.md": MERMAID_DOC}, args=["doc.md"]),
    "plan_gantt": dict(
        exit=0,
        path=f"{S}/mermaid-authoring-guidelines/scripts/plan_gantt.py",
        copy=[f"{S}/mermaid-authoring-guidelines"], siblings=("mermaid_model",),
        files={"PLAN.md": PLAN}, args=["PLAN.md"]),
    "init_skill": dict(
        exit=0,
        path=f"{S}/skill-creator/scripts/init_skill.py", copy=[f"{S}/skill-creator"],
        siblings=("skill_utils",), files={"out/.keep": ""},
        args=["demo-skill", "--path", "out"]),
    "validate_skill": dict(
        exit=0,
        path=f"{S}/skill-creator/scripts/validate_skill.py", copy=[f"{S}/skill-creator"],
        siblings=("skill_utils",), files={}, args=[f"{S}/skill-creator"]),
    "run_audit": dict(
        exit=0,
        path=f"{S}/security-audit/scripts/run_audit.py", copy=[f"{S}/security-audit"],
        siblings=("audit",), files={"project/app.py": "print('hello')\n"},
        args=["project", "--scan-type", "patterns", "--output", "json"]),
}

#: The tree of `tests/run_tests.py`: the three product scripts it loads by path, copied, and stub
#: curated modules. Each imports a helper of `tests/`, `subprocess`, and `colorsys`, which nothing
#: imports before the discovery, so its search shows where `tests/` stands on `sys.path`.
RUN_TESTS = "tests/run_tests.py"
PRODUCT = (f"{S}/skill-product-solution-blueprint/scripts/calculate_roi.py",
           f"{S}/skill-product-analysis/scripts/score_product.py",
           f"{S}/skill-product-backlog-prioritization/scripts/calculate_wsjf.py")
STUB_TEST = ("import colorsys\nimport platform\nimport subprocess\nimport unittest\n\n"
             "import _stub_helper\n\n\n"
             "class StubTest(unittest.TestCase):\n    def test_ok(self):\n"
             "        self.assertEqual(_stub_helper.VALUE, 1)\n")


def _curated():
    tree = ast.parse((ROOT / RUN_TESTS).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "CURATED_UNITTEST_MODULES":
            return ast.literal_eval(node.value)
    raise AssertionError("tests/run_tests.py names no CURATED_UNITTEST_MODULES")


def _imported(paths):
    """Each top-level name that the files at `paths` import, relative imports left out."""
    names = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
    return names


def _sibling_files(script, siblings):
    here = script.parent
    files = [script]
    for name in siblings:
        if (here / name).is_dir():
            files += sorted((here / name).rglob("*.py"))
        else:
            files.append(here / f"{name}.py")
    return files


class _Harness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="allow-listed-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.sentinels = self.tmp / "sentinels"
        self.sentinels.mkdir()

    def make_root(self, label, spec):
        root = self.tmp / label
        for rel in spec["copy"]:
            source, target = ROOT / rel, root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(source, target)
        _write(root, spec["files"])
        return root

    def plant(self, directory, names, tag):
        for name in names:
            sentinel = self.sentinels / f"{tag}-{name}"
            (directory / f"{name}.py").write_text(f"open({str(sentinel)!r}, 'w').close()\n",
                                                  encoding="utf-8")

    def ran(self):
        return sorted(p.name for p in self.sentinels.iterdir())

    def run_script(self, root, script, args):
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.tmp), HOME=str(self.tmp))
        env.pop("PYTHONPATH", None)
        return subprocess.run([sys.executable, str(script), *args], cwd=str(root), env=env,
                              capture_output=True, text=True, timeout=300)

    def run_clean(self, label, spec):
        """A run of a copy with nothing planted, which must end without a traceback."""
        root = self.make_root(label, spec)
        result = self.run_script(root, root / spec["path"], spec["args"])
        self.assertNotIn("Traceback (most recent call last)", result.stderr,
                         "%s fails with nothing planted: %s" % (label, result.stderr[-2000:]))
        self.assertEqual(result.returncode, spec["exit"],
                         "%s stops before its work: %s%s" % (label, result.stdout[-1500:],
                                                            result.stderr[-1500:]))
        return result

    def planted_names(self, spec):
        script = ROOT / spec["path"]
        names = _imported(_sibling_files(script, spec["siblings"]))
        return sorted((names | set(EXTRA)) - set(spec["siblings"]) - {script.stem})


class TestPlantedModules(_Harness):
    """TC-AL1 and TC-AL3."""

    def check(self, name, through=None):
        spec = SCRIPTS[name]
        expected = self.run_clean(f"{name}-clean", spec)
        root = self.make_root(f"{name}-planted", spec)
        script = root / spec["path"]
        self.plant(script.parent, self.planted_names(spec), name)
        if through:
            script = through(script)
            if script is None:
                self.skipTest("the volume tells letter case apart")
        result = self.run_script(root, script, spec["args"])
        self.assertEqual(self.ran(), [], "a module planted beside %s ran" % name)
        self.assertEqual(result.returncode, expected.returncode,
                         "%s: %s%s" % (name, result.stdout[-2000:], result.stderr[-2000:]))

    def test_al1_each_script_imports_no_planted_module(self):
        for name in SCRIPTS:
            with self.subTest(script=name):
                for path in self.sentinels.iterdir():
                    path.unlink()
                self.check(name)

    def test_al3_through_a_path_in_other_letter_case(self):
        def swapped(script):
            variant = script.parent.parent / script.parent.name.swapcase() / script.name
            return variant if variant.exists() else None
        for name in ("task_id_tool", "init_skill"):
            with self.subTest(script=name):
                for path in self.sentinels.iterdir():
                    path.unlink()
                self.check(name, through=swapped)


class TestPlantedSiblings(_Harness):
    """TC-AL2."""

    def test_al2_a_sibling_is_loaded_by_its_path_only(self):
        suffix = importlib.machinery.EXTENSION_SUFFIXES[0]
        tag = sys.implementation.cache_tag
        for name, spec in SCRIPTS.items():
            if not spec["siblings"]:
                continue
            with self.subTest(script=name):
                for path in self.sentinels.iterdir():
                    path.unlink()
                expected = self.run_clean(f"{name}-siblings-clean", spec)
                root = self.make_root(f"{name}-siblings", spec)
                script = root / spec["path"]
                here = script.parent
                evil = self.tmp / f"evil-{name}.py"
                for sibling in spec["siblings"]:
                    if (here / sibling).is_dir():
                        submodule = sorted(p.stem for p in (here / sibling).glob("*.py")
                                           if p.stem != "__init__")[0]
                        cached = [(here / sibling / "__pycache__" / f"__init__.{tag}.pyc"),
                                  (here / sibling / "__pycache__" / f"{submodule}.{tag}.pyc")]
                    else:
                        package = here / sibling
                        package.mkdir()
                        sentinel = self.sentinels / f"package-{sibling}"
                        (package / "__init__.py").write_text(
                            f"open({str(sentinel)!r}, 'w').close()\n", encoding="utf-8")
                        cached = [here / "__pycache__" / f"{sibling}.{tag}.pyc"]
                    (here / f"{sibling}{suffix}").write_bytes(b"not a shared object")
                    for target in cached:
                        sentinel = self.sentinels / f"pyc-{sibling}-{target.stem}"
                        evil.write_text(f"open({str(sentinel)!r}, 'w').close()\n",
                                        encoding="utf-8")
                        target.parent.mkdir(exist_ok=True)
                        py_compile.compile(
                            str(evil), cfile=str(target),
                            invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
                result = self.run_script(root, script, spec["args"])
                self.assertEqual(self.ran(), [], "%s: %s%s" % (name, result.stdout[-1500:],
                                                               result.stderr[-1500:]))
                self.assertEqual(result.returncode, expected.returncode,
                                 "%s: %s%s" % (name, result.stdout[-1500:], result.stderr[-1500:]))


class TestRunTestsDiscovery(_Harness):
    """TC-AL1 for `tests/run_tests.py`, and TC-AL4."""

    def make_tree(self):
        root = self.tmp / "runner"
        (root / "tests" / "installer").mkdir(parents=True)
        shutil.copy2(ROOT / RUN_TESTS, root / RUN_TESTS)
        for rel in PRODUCT:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, root / rel)
        files = {}
        for module in _curated():
            files[f"tests/{module}.py"] = STUB_TEST
        files["tests/_stub_helper.py"] = "VALUE = 1\n"
        files["tests/installer/_base.py"] = "VALUE = 1\n"
        files["tests/installer/test_stub_installer.py"] = STUB_TEST.replace("_stub_helper", "_base")
        _write(root, files)
        return root

    def test_al4_the_discovery_keeps_tests_behind_the_standard_library(self):
        root = self.make_tree()
        expected = self.run_script(root, root / RUN_TESTS, [])
        self.assertEqual(expected.returncode, 0, expected.stdout + expected.stderr)
        names = _imported([ROOT / RUN_TESTS]) | {"colorsys", "json", "subprocess", "msvcrt",
                                                 "_winapi", "_wmi", "selectors", "signal",
                                                 "threading", "fcntl", "__future__"}
        self.plant(root / "tests", sorted(names | {"_base"}), "runner")
        self.plant(root / "tests" / "installer", sorted(names), "installer")
        result = self.run_script(root, root / RUN_TESTS, [])
        self.assertEqual(self.ran(), [], result.stdout[-2000:] + result.stderr[-2000:])
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])

    def test_al3_the_runner_through_a_path_in_other_letter_case(self):
        root = self.make_tree()
        self.plant(root / "tests", ["json", "re", "unittest", "__future__"], "runner")
        variant = root / RUN_TESTS.replace("tests/", "TESTS/")
        if not variant.exists():
            self.skipTest("the volume tells letter case apart")
        result = self.run_script(root, variant, [])
        self.assertEqual(self.ran(), [], result.stdout[-2000:] + result.stderr[-2000:])
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])


#: The guarded scripts by the form of their guard: A removes the directory only; B also turns off
#: bytecode and loads its siblings by path; C, the test runner, has the code of B and its own
#: comment. The older copies of TASK 112, 115 and 127 join them, by code only.
GUARD_A = [SCRIPTS[n]["path"] for n in ("scan_register", "task_id_tool", "check_prompt_references",
                                        "doctor", "security_lint", "smoke_workflows",
                                        "validate_skills")]
GUARD_B = [SCRIPTS[n]["path"] for n in ("selftest_scan", "lint_mermaid", "plan_gantt", "init_skill",
                                        "validate_skill", "run_audit")]
OLDER_A = [f"{S}/skill-session-state/scripts/update_state.py", ".agent/tools/archive_move.py"]
OLDER_B = [".agent/tools/rebase_links.py"]


def _guard(path):
    """The guard of *path*: its code, with the name of its `.pyc` prefix normalised, and the comment
    lines right above it."""
    text = (ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.If)
                and ast.unparse(n.test) == "__name__ == '__main__'")
    lines = text.splitlines()
    comment = []
    index = node.lineno - 2
    while index >= 0 and lines[index].startswith("#"):
        comment.insert(0, lines[index])
        index -= 1
    code = re.sub(r"'[\w-]+-pycache'", "'<script>-pycache'", ast.unparse(node))
    return code, "\n".join(comment)


def _path_changes(body):
    """Each statement of *body*, outside a function, a class and the guard, that changes
    `sys.path`: a call of one of its methods, or an assignment to it or to a part of it."""
    found = []
    for statement in body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(statement, ast.If) and ast.unparse(statement.test) == "__name__ == '__main__'" \
                and "sys.path[:]" in ast.unparse(statement):
            continue
        for node in ast.walk(statement):
            if isinstance(node, ast.Call) and ast.unparse(node.func).startswith("sys.path."):
                found.append(ast.unparse(node))
            targets = node.targets if isinstance(node, ast.Assign) else \
                [node.target] if isinstance(node, (ast.AugAssign, ast.AnnAssign)) else []
            found += [ast.unparse(t) for t in targets if ast.unparse(t).startswith("sys.path")]
    return found


def _loader(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "_load")
    return ast.get_source_segment(text, node)


class TestGuardShape(unittest.TestCase):
    """TC-AL5."""

    def test_al5_the_runner_imports_each_prober_before_its_discovery(self):
        tree = ast.parse((ROOT / RUN_TESTS).read_text(encoding="utf-8"))
        top = {alias.name for node in tree.body if isinstance(node, ast.Import)
               for alias in node.names}
        self.assertTrue({"platform", "subprocess"} <= top, sorted(top))

    def test_al5_every_copy_of_the_guard_is_the_same(self):
        code_a, comment_a = _guard(GUARD_A[0])
        code_b, comment_b = _guard(GUARD_B[0])
        self.assertTrue(code_b.startswith(code_a), "group B extends the guard of group A")
        for group, code, comment, older in ((GUARD_A, code_a, comment_a, OLDER_A),
                                            (GUARD_B, code_b, comment_b, OLDER_B),
                                            ([RUN_TESTS], code_b, _guard(RUN_TESTS)[1], [])):
            for path in group + older:
                with self.subTest(script=path):
                    other_code, other_comment = _guard(path)
                    self.assertEqual(other_code, code, "the guard of %s differs" % path)
                    if path in group:
                        self.assertEqual(other_comment, comment, "the comment of %s differs" % path)
        loader = _loader(GUARD_B[0])
        for path in GUARD_B[1:]:
            with self.subTest(loader=path):
                self.assertEqual(_loader(path), loader, "_load of %s differs" % path)

    def test_al5_no_future_statement_no_path_insert_and_the_guard_first(self):
        for name, spec in {**SCRIPTS, "run_tests": dict(path=RUN_TESTS)}.items():
            with self.subTest(script=name):
                tree = ast.parse((ROOT / spec["path"]).read_text(encoding="utf-8"))
                body = tree.body[1:] if (tree.body and isinstance(tree.body[0], ast.Expr)
                                         and isinstance(tree.body[0].value, ast.Constant)) \
                    else tree.body
                self.assertFalse(any(isinstance(n, ast.ImportFrom) and n.module == "__future__"
                                     for n in body), "from __future__ in %s" % name)
                self.assertEqual(_path_changes(body), [], "%s changes sys.path" % name)
                index = next(i for i, n in enumerate(body) if isinstance(n, ast.If)
                             and ast.unparse(n.test) == "__name__ == '__main__'")
                for node in body[:index]:
                    self.assertIsInstance(node, ast.Import, name)
                    self.assertTrue({a.name for a in node.names} <= {"os", "sys"}, name)
                self.assertIn("sys.path[:]", ast.unparse(body[index]), name)


if __name__ == "__main__":
    unittest.main()
