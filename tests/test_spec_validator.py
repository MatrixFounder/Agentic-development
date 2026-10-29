import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / ".agent/skills/skill-spec-validator/scripts/validate.py"


def _run_validator(mode: str, *files: Path) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(VALIDATOR), "--mode", mode, *[str(f) for f in files]]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_plan_validation_accepts_simple_id(tmp_path: Path):
    task = _write(
        tmp_path / "TASK.md",
        """
## Requirements Traceability
| ID | Requirement |
|---|---|
| R1 | Sample requirement |
""".strip()
        + "\n",
    )
    plan = _write(tmp_path / "PLAN.md", "- [R1] Implement sample requirement\n")

    result = _run_validator("plan", plan, task)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Success" in result.stdout


def test_plan_validation_accepts_dotted_id(tmp_path: Path):
    task = _write(
        tmp_path / "TASK.md",
        """
## Requirements Traceability
| ID | Requirement |
|---|---|
| R1.1 | Dotted requirement |
""".strip()
        + "\n",
    )
    plan = _write(tmp_path / "PLAN.md", "- [R1.1] Implement dotted requirement\n")

    result = _run_validator("plan", plan, task)
    assert result.returncode == 0, result.stdout + result.stderr


def test_plan_validation_reports_missing_ids(tmp_path: Path):
    task = _write(
        tmp_path / "TASK.md",
        """
## Requirements Traceability
| ID | Requirement |
|---|---|
| R1 | Requirement one |
| R2 | Requirement two |
""".strip()
        + "\n",
    )
    plan = _write(tmp_path / "PLAN.md", "- [R1] Implement requirement one\n")

    result = _run_validator("plan", plan, task)
    assert result.returncode != 0
    assert "R2" in result.stdout


def test_plan_validation_honors_bypass_flag(tmp_path: Path):
    task = _write(
        tmp_path / "TASK.md",
        """
# Spec [BYPASS_VALIDATION]
## Requirements Traceability
| ID | Requirement |
|---|---|
| R1 | Requirement one |
""".strip()
        + "\n",
    )
    plan = _write(tmp_path / "PLAN.md", "(intentionally empty)\n")

    result = _run_validator("plan", plan, task)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Validation bypassed" in result.stdout
