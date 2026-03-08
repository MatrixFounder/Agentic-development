"""External security tool integration."""

from pathlib import Path
from typing import List
import sys

from .helpers import run_command


def run_external_tools(project_path: str, types: List[str]):
    """Run external security tools based on project type."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"External Tools Scan: {', '.join(types)}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    cwd = project_path

    if "solidity" in types:
        run_command(["slither", "."], cwd=cwd)

    if "python" in types:
        run_command(["bandit", "-r", ".", "-q"], cwd=cwd)
        # pip-audit replaces safety (Safety DB went commercial in 2024)
        run_command(["pip-audit"], cwd=cwd)

    if "javascript" in types:
        if (Path(cwd) / "yarn.lock").exists():
            run_command(["yarn", "audit"], cwd=cwd)
        else:
            run_command(["npm", "audit"], cwd=cwd)

    if "rust" in types:
        run_command(["cargo", "audit"], cwd=cwd)
        run_command(["cargo", "clippy"], cwd=cwd)

    if "go" in types:
        run_command(["govulncheck", "./..."], cwd=cwd)
        run_command(["gosec", "./..."], cwd=cwd)

    if "iac" in types:
        run_command(["checkov", "-d", "."], cwd=cwd)
        run_command(["trivy", "fs", "--scanners", "misconfig", "."], cwd=cwd)
