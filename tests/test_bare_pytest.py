"""A bare pytest run from the repository root collects (TASK 122 R3).

The allow rules `python3 -m pytest` and `python -m pytest` run pytest with no path, so it collects
every `test_*.py` file it finds from the root. Before TASK 122 the skill-testing example called
`exit(1)` at import when `openai` was absent, and the run stopped with INTERNALERROR. Each check
runs in a subprocess in which `import openai` fails, whether or not the package is installed.

TASK 123 R6 adds two checks of the example: it runs as a script, and an xAI key alone reaches no
server, since `query_model` reads `OPENAI_API_KEY` only.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "skill-testing" / "test_skill.py"
#: Makes `import openai` fail in the child, as on a machine without the package.
NO_OPENAI = "import sys\nsys.modules['openai'] = None\n"
#: The variables of an API key and a server, `XAI_API_KEY` among them, which `query_model` read
#: before TASK 123 R6.2; a child gets none of them.
KEYS = ("OPENAI_API_KEY", "XAI_API_KEY", "OPENAI_BASE_URL")
LOAD = ("import importlib.util\n"
        "spec = importlib.util.spec_from_file_location('skill_example', %r)\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        "print('imported')\n" % str(EXAMPLE))


def run(code, env=None):
    """*code* in a child interpreter at the repository root, with `import openai` failing."""
    child = {k: v for k, v in os.environ.items() if k not in KEYS}
    child.update(PYTHONDONTWRITEBYTECODE="1", **(env or {}))
    return subprocess.run([sys.executable, "-c", NO_OPENAI + code], cwd=str(ROOT), env=child,
                          capture_output=True, text=True, timeout=300)


class TestBarePytest(unittest.TestCase):
    def test_collection_from_the_root_succeeds(self):
        done = run("import pytest\n"
                   "raise SystemExit(pytest.main(['--co', '-q', '-p', 'no:cacheprovider']))\n")
        out = done.stdout + done.stderr
        self.assertEqual(done.returncode, 0, out[-3000:])
        self.assertNotIn("INTERNALERROR", out)

    def test_the_example_imports_without_openai(self):
        done = run(LOAD)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("imported", done.stdout)

    def test_query_model_without_a_key_needs_no_openai(self):
        done = run(LOAD + "print(mod.query_model('prompt text'))\n")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("imported", done.stdout)
        self.assertIn("Dry run complete.", done.stdout)

    def test_query_model_with_a_key_and_no_openai_exits_1(self):
        done = run(LOAD + "mod.query_model('prompt text')\n", env={"OPENAI_API_KEY": "test-key"})
        # the marker shows that the exit comes from query_model, not from the import
        self.assertIn("imported", done.stdout)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("pip install openai", done.stdout)

    def test_only_an_xai_key_gives_the_dry_run(self):
        # TASK 123 R6.2: no line reads XAI_API_KEY, so that key reaches no server
        done = run(LOAD + "print(mod.query_model('prompt text'))\n", env={"XAI_API_KEY": "test-key"})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("Dry run complete.", done.stdout)
        self.assertNotIn("pip install openai", done.stdout)

    def test_the_example_runs_as_a_script(self):
        # TASK 123 R6.1: the role file and the two skills that __main__ names exist
        done = run("import runpy\nrunpy.run_path(%r, run_name='__main__')\n" % str(EXAMPLE))
        out = done.stdout + done.stderr
        self.assertEqual(done.returncode, 0, out[-2000:])
        for rel in ("System/Agents/08_developer_prompt.md", ".agent/skills/tdd-stub-first/SKILL.md",
                    ".agent/skills/documentation-standards/SKILL.md"):
            self.assertIn(str(ROOT / rel), out)
        self.assertNotIn("File not found", out)
        self.assertNotIn("Warning: Skill", out)


if __name__ == "__main__":
    unittest.main()
