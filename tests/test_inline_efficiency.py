"""Regression tests for the two-tier inline code-block policy (Task 064).

Covers `check_inline_efficiency` in skill-creator/validate_skill.py and the
verbatim copy in skill-enhancer/analyze_gaps.py:
  - warn band / fail ceiling are config-driven (not hard-coded);
  - mermaid fences are exempt, text/console/output fences can only warn;
  - an unclosed fence is reported as an error;
  - the two copies stay behaviourally identical (drift guard);
  - and, since WI-033, every function the two files share is byte-identical.
"""

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CREATOR = REPO / ".agent/skills/skill-creator/scripts/validate_skill.py"
ENHANCER = REPO / ".agent/skills/skill-enhancer/scripts/analyze_gaps.py"


def _load(path: Path, modname: str):
    """Load a validator script as a module (each appends its own scripts/ dir)."""
    sys.modules.pop("skill_utils", None)
    spec = importlib.util.spec_from_file_location(modname, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cie_creator = _load(CREATOR, "vs_validate_skill").check_inline_efficiency
cie_enhancer = _load(ENHANCER, "ve_analyze_gaps").check_inline_efficiency
check_inline_efficiency = cie_creator


def _block(n: int, lang: str = "") -> str:
    """A fenced block with exactly `n` content lines."""
    body = "\n".join(f"line {i}" for i in range(n))
    return f"```{lang}\n{body}\n```"


# --- behavioural coverage (defaults: warn 20 / fail 60) ---

def test_small_block_passes():
    errors, warnings = check_inline_efficiency(_block(15, "python"))
    assert errors == [] and warnings == []


def test_mid_block_warns_only():
    errors, warnings = check_inline_efficiency(_block(25, "python"))
    assert errors == [] and len(warnings) == 1


def test_large_block_fails():
    errors, warnings = check_inline_efficiency(_block(65, "python"))
    assert len(errors) == 1 and warnings == []


def test_untagged_block_is_checked():
    errors, warnings = check_inline_efficiency(_block(40))
    assert errors == [] and len(warnings) == 1


def test_mermaid_fence_exempt():
    errors, warnings = check_inline_efficiency(_block(65, "mermaid"))
    assert errors == [] and warnings == []


def test_text_fence_softcheck_warns_never_fails():
    errors, warnings = check_inline_efficiency(_block(65, "text"))
    assert errors == [] and len(warnings) == 1


def test_unclosed_fence_is_an_error():
    content = "```python\n" + "\n".join(f"x{i}" for i in range(5))
    errors, warnings = check_inline_efficiency(content)
    assert len(errors) == 1 and "Unclosed" in errors[0]


def test_thresholds_are_config_driven_not_hard_coded():
    # The same 25-line block: default warn=20 -> warns; raised warn=30 -> silent.
    assert check_inline_efficiency(_block(25, "python"))[1]
    assert not check_inline_efficiency(_block(25, "python"), warn_lines=30, fail_lines=100)[1]
    # A 65-line block hard-fails by default but only warns with a raised ceiling.
    assert check_inline_efficiency(_block(65, "python"))[0]
    assert not check_inline_efficiency(_block(65, "python"), warn_lines=20, fail_lines=80)[0]


# --- drift guard: the two verbatim copies must agree ---

def test_creator_and_enhancer_copies_agree():
    fixtures = [
        _block(15, "python"), _block(25, "python"), _block(65, "python"),
        _block(40), _block(65, "mermaid"), _block(65, "text"),
        "```python\n" + "\n".join(f"x{i}" for i in range(5)),
        "no fences here at all",
    ]
    for content in fixtures:
        assert cie_creator(content) == cie_enhancer(content), content[:40]


# --- drift guard, widened: nine functions are now duplicated, not one -------
#
# `check_inline_efficiency` was the first function the two gates carried
# verbatim. WI-033 (Universal-skills) added eight more — code masking, the
# section helpers, the execution-policy rule — because the two gates must not
# reach different verdicts about the same SKILL.md, and neither may import from
# the other (a skill has to run in isolation, including as a packaged archive).
#
# Behavioural sampling cannot see a divergence outside the fixtures it happens
# to try. Byte-identity can.

import ast

SHARED_FUNCTIONS = [
    "check_inline_efficiency",
    "mask_code",
    "collect_execution_policy_findings",
    "_normalize_section_title",
    "_collect_markdown_headings",
    "_has_section",
    "_has_real_files",
    "_section_body_lines",
    "check_validation_evidence_size",
]

# `extract_frontmatter` differs ON PURPOSE: analyze_gaps.py returns a fourth
# value, the body's line offset, because its findings name a line and
# validate_skill.py's do not.
DELIBERATELY_DIFFERENT = {"extract_frontmatter", "main"}


def _function_source(path: Path, name: str):
    source = path.read_text(encoding="utf-8")
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    return None


def _top_level_functions(path: Path):
    return {n.name for n in ast.parse(path.read_text(encoding="utf-8")).body
            if isinstance(n, ast.FunctionDef)}


def test_every_shared_function_is_byte_identical():
    for name in SHARED_FUNCTIONS:
        a = _function_source(CREATOR, name)
        b = _function_source(ENHANCER, name)
        assert a is not None, f"{name} missing from validate_skill.py"
        assert b is not None, f"{name} missing from analyze_gaps.py"
        assert a == b, (
            f"the two copies of {name}() have drifted. Make them identical "
            f"again rather than relaxing this test — a check that differs "
            f"between the two gates is how WI-033 started.")


def test_the_shared_inventory_is_not_quietly_incomplete():
    """A function duplicated but unlisted is a function nobody guards."""
    shared = _top_level_functions(CREATOR) & _top_level_functions(ENHANCER)
    unlisted = shared - set(SHARED_FUNCTIONS) - DELIBERATELY_DIFFERENT
    assert not unlisted, (
        f"duplicated but unguarded: {sorted(unlisted)} — add them to "
        f"SHARED_FUNCTIONS, or to DELIBERATELY_DIFFERENT with a reason.")


def test_a_rule_in_both_gates_carries_the_same_severity():
    """`required_sections` is reported by both, and blocks in neither.

    Measured 2026-09-02: making it an error in validate_skill.py flipped 34 of
    this repository's 46 skills from passing to failing and took the CI gate
    from 46/46 to 12/46, without a single skill changing. Red Flags and a
    Rationalization Table are a house convention, not a structural requirement.
    """
    import json
    import subprocess
    import tempfile

    body = (
        "---\nname: nosectionskill\n"
        "description: Use when a skill carries no house-convention sections.\n"
        "tier: 2\nversion: 1.0\n---\n# nosectionskill\n\n"
        "A body with none of the house-convention headings.\n")
    with tempfile.TemporaryDirectory() as tmp:
        skill = Path(tmp) / "nosectionskill"
        (skill / "examples").mkdir(parents=True)
        (skill / "examples" / "e.md").write_text(
            "# Example\n\nLong enough to clear the size floor.\n", encoding="utf-8")
        (skill / "SKILL.md").write_text(body, encoding="utf-8")
        for tool, blocking, advisory in ((CREATOR, "errors", "warnings"),
                                         (ENHANCER, "gaps", "advisories")):
            out = subprocess.run(
                [sys.executable, str(tool), str(skill), "--json"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", cwd=str(REPO)).stdout
            doc = json.loads(out)
            assert not [x for x in doc[blocking] if "Red Flags" in x], (
                f"{tool.name} blocks on a house-convention section")
            assert [x for x in doc[advisory] if "Red Flags" in x], (
                f"{tool.name} stopped reporting the missing section at all")
