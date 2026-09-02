#!/usr/bin/env python3
"""Child process for `test_stdout_broken_pipe.py`.

Runs a real script's `main()` with only the LLM-backed work stubbed out, so the
actual `print(json.dumps(...), flush=True)` line under test executes on a payload
of a caller-chosen size. Argv: <module> <target_bytes> <workdir>.
"""
import importlib.util
import json
import os
import pathlib
import sys
import types

MODULE, TARGET_BYTES, WORKDIR = sys.argv[1], int(sys.argv[2]), pathlib.Path(sys.argv[3])
SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
WORKDIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location("under_test", SCRIPTS / f"{MODULE}.py")
m = importlib.util.module_from_spec(spec)
sys.modules["under_test"] = m
spec.loader.exec_module(m)


def blob(n):
    """A results list whose json.dumps(indent=2) is at least n bytes."""
    out, i = [], 0
    while len(json.dumps(out, indent=2)) < n:
        out.append({"id": f"case-{i:05d}", "query": "q" * 60, "pass": bool(i % 2),
                    "triggers": 2, "runs": 3, "should_trigger": True})
        i += 1
    return out


skill = WORKDIR / "fixture-skill"
skill.mkdir(exist_ok=True)
(skill / "SKILL.md").write_text(
    "---\nname: fixture-skill\ndescription: Use when driving a tooling-skill main() "
    "for broken-pipe measurement.\nversion: 1.0.0\n---\n\n# fixture-skill\n")
evals = WORKDIR / "evals.json"
evals.write_text(json.dumps([{"id": "a", "query": "q", "should_trigger": True}]))

if MODULE == "run_eval":
    m.run_eval = lambda **kw: {"description": "d",
                               "summary": {"passed": 1, "failed": 0, "total": 1},
                               "results": blob(TARGET_BYTES)}
    sys.argv = ["run_eval.py", "--eval-set", str(evals), "--skill-path", str(skill)]
    m.main()

elif MODULE == "run_loop":
    m.run_loop = lambda **kw: {"best_description": "d", "iterations": 1,
                               "history": blob(TARGET_BYTES)}
    m.generate_html = lambda *a, **k: "<html></html>"
    sys.argv = ["run_loop.py", "--eval-set", str(evals), "--skill-path", str(skill),
                "--model", "stub", "--report", "none"]
    if os.environ.get("CHILD_RESULTS_DIR"):
        sys.argv += ["--results-dir", os.environ["CHILD_RESULTS_DIR"]]
    m.main()

elif MODULE == "improve_description":
    results = WORKDIR / "evalres.json"
    results.write_text(json.dumps({"description": "old",
                                   "summary": {"passed": 1, "failed": 0, "total": 1},
                                   "results": blob(TARGET_BYTES)}))
    m.anthropic = types.SimpleNamespace(Anthropic=lambda *a, **k: object())
    m.improve_description = lambda **kw: "a new description"
    sys.argv = ["improve_description.py", "--eval-results", str(results),
                "--skill-path", str(skill), "--model", "stub"]
    m.main()

else:
    raise SystemExit(f"unknown module {MODULE!r}")
