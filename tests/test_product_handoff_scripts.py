import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent))

from _scratch import repo_scratch_dir  # noqa: E402 - needs the path append above

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / ".agent" / "skills" / "skill-product-handoff" / "scripts"
SIGN_OFF = SCRIPTS_DIR / "sign_off.py"
VERIFY_GATE = SCRIPTS_DIR / "verify_gate.py"
COMPILE_BRD = SCRIPTS_DIR / "compile_brd.py"

HASH_RE = re.compile(
    r"^APPROVAL_HASH: [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-\d+-APPROVED$",
    re.MULTILINE,
)


def _run_script(script: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def _to_repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


@pytest.fixture
def handoff_workspace() -> Path:
    """Yield a workspace **inside** the repository.

    It cannot move to system temp: the scripts under test reject any path outside the
    repository root, which is the behaviour these tests exercise. `tests/_scratch.py`
    sweeps the directory at session start and end instead.
    """
    workspace = repo_scratch_dir(prefix="handoff_")
    product_dir = workspace / "docs" / "product"
    product_dir.mkdir(parents=True, exist_ok=True)

    (product_dir / "APPROVED_BACKLOG.md").write_text("# Approved Backlog\n", encoding="utf-8")
    (product_dir / "MARKET_STRATEGY.md").write_text("## Market\nMarket data\n", encoding="utf-8")
    (product_dir / "PRODUCT_VISION.md").write_text("## Vision\nVision text\n", encoding="utf-8")
    (product_dir / "SOLUTION_BLUEPRINT.md").write_text("## Blueprint\nBlueprint text\n", encoding="utf-8")

    yield workspace

    shutil.rmtree(workspace, ignore_errors=True)


@pytest.mark.parametrize("script", [SIGN_OFF, VERIFY_GATE, COMPILE_BRD])
def test_help_mode_exits_without_mutation(script: Path, handoff_workspace: Path) -> None:
    backlog_file = handoff_workspace / "docs" / "product" / "APPROVED_BACKLOG.md"
    output_file = handoff_workspace / "docs" / "BRD.md"

    before_backlog = backlog_file.read_text(encoding="utf-8")
    before_output_exists = output_file.exists()

    result = _run_script(script, ["--help"])

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert backlog_file.read_text(encoding="utf-8") == before_backlog
    assert output_file.exists() == before_output_exists


def test_sign_off_rejects_outside_repo_path(tmp_path: Path) -> None:
    outside_file = tmp_path / "product_handoff_outside.md"
    outside_file.write_text("# outside\n", encoding="utf-8")

    result = _run_script(SIGN_OFF, ["--file", str(outside_file)])

    assert result.returncode == 1
    assert "outside repository root" in result.stdout.lower()


def test_verify_gate_rejects_outside_repo_path(tmp_path: Path) -> None:
    outside_file = tmp_path / "product_handoff_outside_verify.md"
    outside_file.write_text("# outside\n", encoding="utf-8")

    result = _run_script(VERIFY_GATE, ["--file", str(outside_file)])

    assert result.returncode == 1
    assert "outside repository root" in result.stdout.lower()


def test_compile_brd_rejects_outside_output_path(
    handoff_workspace: Path, tmp_path: Path
) -> None:
    product_dir = handoff_workspace / "docs" / "product"
    outside_output = tmp_path / "product_handoff_brd.md"

    result = _run_script(
        COMPILE_BRD,
        [
            "--market-file",
            _to_repo_rel(product_dir / "MARKET_STRATEGY.md"),
            "--vision-file",
            _to_repo_rel(product_dir / "PRODUCT_VISION.md"),
            "--blueprint-file",
            _to_repo_rel(product_dir / "SOLUTION_BLUEPRINT.md"),
            "--output-file",
            str(outside_output),
        ],
    )

    assert result.returncode == 1
    assert "outside repository root" in result.stdout.lower()
    assert not outside_output.exists()


def test_sign_off_missing_file_returns_error(handoff_workspace: Path) -> None:
    missing_file = handoff_workspace / "docs" / "product" / "MISSING_BACKLOG.md"

    result = _run_script(SIGN_OFF, ["--file", _to_repo_rel(missing_file)])

    assert result.returncode == 1
    assert "file not found" in result.stdout.lower()


def test_verify_gate_missing_file_returns_error(handoff_workspace: Path) -> None:
    missing_file = handoff_workspace / "docs" / "product" / "MISSING_BACKLOG.md"

    result = _run_script(VERIFY_GATE, ["--file", _to_repo_rel(missing_file)])

    assert result.returncode == 1
    assert "file not found" in result.stdout.lower()


def test_compile_brd_missing_input_file_returns_error(handoff_workspace: Path) -> None:
    product_dir = handoff_workspace / "docs" / "product"
    output_file = handoff_workspace / "docs" / "BRD.md"

    result = _run_script(
        COMPILE_BRD,
        [
            "--market-file",
            _to_repo_rel(product_dir / "MARKET_STRATEGY.md"),
            "--vision-file",
            _to_repo_rel(product_dir / "PRODUCT_VISION.md"),
            "--blueprint-file",
            _to_repo_rel(product_dir / "MISSING_BLUEPRINT.md"),
            "--output-file",
            _to_repo_rel(output_file),
        ],
    )

    assert result.returncode == 1
    assert "file not found" in result.stdout.lower()
    assert not output_file.exists()


def test_sign_off_success_appends_hash(handoff_workspace: Path) -> None:
    backlog_file = handoff_workspace / "docs" / "product" / "APPROVED_BACKLOG.md"

    result = _run_script(SIGN_OFF, ["--file", _to_repo_rel(backlog_file)])

    assert result.returncode == 0
    content = backlog_file.read_text(encoding="utf-8")
    assert HASH_RE.search(content)


def test_verify_gate_success_with_valid_hash(handoff_workspace: Path) -> None:
    backlog_file = handoff_workspace / "docs" / "product" / "APPROVED_BACKLOG.md"
    backlog_file.write_text(
        "# Approved Backlog\nAPPROVAL_HASH: 550e8400-e29b-41d4-a716-446655440000-1735689600-APPROVED\n",
        encoding="utf-8",
    )

    result = _run_script(VERIFY_GATE, ["--file", _to_repo_rel(backlog_file)])

    assert result.returncode == 0
    assert "success" in result.stdout.lower()


def test_compile_brd_success_creates_output(handoff_workspace: Path) -> None:
    product_dir = handoff_workspace / "docs" / "product"
    output_file = handoff_workspace / "docs" / "BRD.md"

    result = _run_script(
        COMPILE_BRD,
        [
            "--market-file",
            _to_repo_rel(product_dir / "MARKET_STRATEGY.md"),
            "--vision-file",
            _to_repo_rel(product_dir / "PRODUCT_VISION.md"),
            "--blueprint-file",
            _to_repo_rel(product_dir / "SOLUTION_BLUEPRINT.md"),
            "--output-file",
            _to_repo_rel(output_file),
        ],
    )

    assert result.returncode == 0
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "Market data" in content
    assert "Vision text" in content
    assert "Blueprint text" in content
