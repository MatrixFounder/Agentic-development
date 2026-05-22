"""Regression tests for the two-tier inline code-block policy (Task 064).

Covers `check_inline_efficiency` in skill-creator/validate_skill.py and the
verbatim copy in skill-enhancer/analyze_gaps.py:
  - warn band / fail ceiling are config-driven (not hard-coded);
  - mermaid fences are exempt, text/console/output fences can only warn;
  - an unclosed fence is reported as an error;
  - the two copies stay behaviourally identical (drift guard).
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
