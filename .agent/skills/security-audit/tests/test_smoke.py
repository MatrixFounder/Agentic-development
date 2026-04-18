"""Smoke / regression tests for security-audit scanner v3.3+.

Runs offline — no internet / external-tool dependency. Exercises the behaviors
that broke historically (and have been fixed) so a future regression is caught.

Invoke:
    python3 -m pytest .agent/skills/security-audit/tests/
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit import (  # noqa: E402
    __version__,
    scan_dependencies,
    scan_code_patterns,
    scan_sbom,
    scan_secrets,
)
from audit import config as audit_config  # noqa: E402


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Empty temp project dir."""
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# --- Version ---------------------------------------------------------------

def test_version_is_exposed():
    """__version__ is a single source of truth; must be semver-ish."""
    assert isinstance(__version__, str)
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert all(p.isdigit() for p in parts)


# --- P1.1 / H4: pip lock detection ----------------------------------------

def test_pyproject_without_lock_flags_missing(tmp_project):
    _write(tmp_project / "pyproject.toml", '[project]\nname = "demo"\n')
    result = scan_dependencies(str(tmp_project))
    types = [f.get("type") for f in result["findings"]]
    assert "Missing Lock File" in types
    msgs = [f.get("message", "") for f in result["findings"]]
    assert any("python" in m for m in msgs)


def test_requirements_txt_alone_flags_missing(tmp_project):
    """requirements.txt without hashes is NOT a lock file."""
    _write(tmp_project / "requirements.txt", "requests==2.31.0\n")
    result = scan_dependencies(str(tmp_project))
    assert any(f.get("type") == "Missing Lock File" for f in result["findings"])


def test_hash_pinned_requirements_accepted_as_lock(tmp_project):
    """pip-compile output with --hash=sha256: counts as lock (R4 fix)."""
    _write(
        tmp_project / "requirements.txt",
        "# pip-compile generated\nrequests==2.31.0 \\\n    --hash=sha256:abcdef123456\n",
    )
    result = scan_dependencies(str(tmp_project))
    assert not any(
        f.get("type") == "Missing Lock File" and "python" in f.get("message", "")
        for f in result["findings"]
    ), "hash-pinned requirements.txt should satisfy pip lock requirement"


def test_poetry_lock_satisfies_pip(tmp_project):
    _write(tmp_project / "pyproject.toml", '[project]\nname = "demo"\n')
    _write(tmp_project / "poetry.lock", "# poetry lock\n")
    result = scan_dependencies(str(tmp_project))
    assert not any(
        f.get("type") == "Missing Lock File" and "python" in f.get("message", "")
        for f in result["findings"]
    )


def test_js_any_lock_satisfies(tmp_project):
    """JS ecosystem accepts any of npm/yarn/pnpm locks (R3 fix)."""
    _write(tmp_project / "package.json", '{"name":"demo"}')
    _write(tmp_project / "package-lock.json", '{"lockfileVersion":3}')
    result = scan_dependencies(str(tmp_project))
    assert not any(
        f.get("type") == "Missing Lock File" and "javascript" in f.get("message", "")
        for f in result["findings"]
    )


# --- P2.3 / H3: SBOM rglob with SKIP_DIRS ---------------------------------

def test_sbom_found_in_nested_dir(tmp_project):
    _write(tmp_project / "docs" / "sbom.json", "{}")
    result = scan_sbom(str(tmp_project))
    assert not result["findings"], "nested docs/sbom.json should be found"


def test_sbom_inside_skip_dir_not_found(tmp_project):
    """SBOM inside node_modules/vendor must NOT satisfy — it's a vendor artifact."""
    _write(tmp_project / "node_modules" / "sbom.json", "{}")
    result = scan_sbom(str(tmp_project))
    assert any(f.get("type") == "Missing SBOM" for f in result["findings"])


def test_sbom_case_insensitive(tmp_project):
    _write(tmp_project / "SBOM.json", "{}")
    result = scan_sbom(str(tmp_project))
    assert not result["findings"], "uppercase SBOM.json should be found (case-insensitive)"


# --- P2.6 / L8: Solidity view/pure + returns/payable ----------------------

def test_solidity_view_function_not_flagged(tmp_project):
    _write(
        tmp_project / "Demo.sol",
        """pragma solidity ^0.8.0;
contract Demo {
    uint256 public x;
    function getX() external view returns (uint256) {
        return x;
    }
}
""",
    )
    result = scan_code_patterns(str(tmp_project))
    unprotected = [
        f for f in result["findings"]
        if "state-mutating function without modifier" in f.get("pattern", "")
    ]
    assert not unprotected, "view function should NOT be flagged"


def test_solidity_public_mutator_flagged(tmp_project):
    _write(
        tmp_project / "Demo.sol",
        """pragma solidity ^0.8.0;
contract Demo {
    uint256 public x;
    function setX(uint256 _x) public {
        x = _x;
    }
}
""",
    )
    result = scan_code_patterns(str(tmp_project))
    unprotected = [
        f for f in result["findings"]
        if "state-mutating function without modifier" in f.get("pattern", "")
    ]
    assert unprotected, "unprotected public mutator should be flagged"


def test_solidity_public_payable_returns_flagged(tmp_project):
    """R4 L8: pattern widened to accept `payable` and `returns (...)`."""
    _write(
        tmp_project / "Demo.sol",
        """pragma solidity ^0.8.0;
contract Demo {
    function deposit() external payable returns (uint256) {
        return msg.value;
    }
}
""",
    )
    result = scan_code_patterns(str(tmp_project))
    unprotected = [
        f for f in result["findings"]
        if "state-mutating function without modifier" in f.get("pattern", "")
    ]
    assert unprotected, "public+payable+returns should flag"


def test_solidity_modifier_not_flagged(tmp_project):
    """Custom modifier (onlyOwner) must suppress the 'unprotected' finding."""
    _write(
        tmp_project / "Demo.sol",
        """pragma solidity ^0.8.0;
contract Demo {
    modifier onlyOwner { _; }
    function setX(uint256 _x) public onlyOwner {
        _x;
    }
}
""",
    )
    result = scan_code_patterns(str(tmp_project))
    unprotected = [
        f for f in result["findings"]
        if "state-mutating function without modifier" in f.get("pattern", "")
    ]
    assert not unprotected, "function with custom modifier should NOT flag"


# --- P3.7 / H1: Go rand call-site (not math/rand.*) -----------------------

def test_go_rand_call_site_flagged(tmp_project):
    _write(
        tmp_project / "main.go",
        """package main
import "math/rand"
func main() { _ = rand.Intn(10) }
""",
    )
    result = scan_code_patterns(str(tmp_project))
    patterns = [f.get("pattern", "") for f in result["findings"]]
    assert any("rand.* call" in p for p in patterns), "rand.Intn call-site must flag (R4 H1)"


def test_rust_unsafe_and_transmute(tmp_project):
    _write(
        tmp_project / "main.rs",
        """fn main() {
    unsafe {
        let _ = std::mem::transmute::<u32, f32>(42);
    }
}
""",
    )
    result = scan_code_patterns(str(tmp_project))
    patterns = [f.get("pattern", "") for f in result["findings"]]
    assert any("transmute" in p for p in patterns)
    assert any("unsafe block" in p for p in patterns)


# --- P3.10 / M5: ReDoS guard (MAX_LINE_LENGTH) ----------------------------

def test_long_line_skipped_by_redos_guard(tmp_project, monkeypatch):
    """A single 10k-char line must NOT be scanned (skipped), low-risk for ReDoS."""
    monkeypatch.setattr(audit_config, "MAX_LINE_LENGTH", 1000)
    _write(
        tmp_project / "min.js",
        "var x = " + ("a" * 10_000) + ";\neval(userInput);\n",
    )
    result = scan_code_patterns(str(tmp_project))
    # eval() on line 2 (short) MUST still be detected even though line 1 was skipped.
    patterns = [f.get("pattern", "") for f in result["findings"]]
    assert any("eval()" in p for p in patterns), "short lines must still scan normally"


# --- Self-exclusion (pre-existing behavior) -------------------------------

def test_self_exclusion_skill_dir():
    """Scanner's own directory must not flag its own regex patterns."""
    skill_dir = Path(__file__).resolve().parent.parent
    result = scan_code_patterns(str(skill_dir))
    assert not result["findings"], f"self-exclusion broken: {result['findings']}"
