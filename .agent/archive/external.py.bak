"""External security tool integration."""

from pathlib import Path
from typing import List
import sys

from .helpers import run_command


def run_external_tools(project_path: str, types: List[str]):
    """Run external security tools based on project type.

    Tool availability is checked by `run_command` (prints [!] Tool not found and returns None).
    Missing tools are non-fatal — run_audit.py always continues.
    """
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"External Tools Scan: {', '.join(types)}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    cwd = project_path

    # --- Cross-cutting scanners (run for any project type) ---

    # semgrep — de-facto SAST standard (2024+); auto-config picks rules by language.
    run_command(["semgrep", "--config", "auto", "--error", "--quiet", "--timeout", "60", "."], cwd=cwd)

    # Secret scanners — stronger than regex-only; run at least one.
    # gitleaks is the more common; trufflehog is a fallback.
    if not run_command(["gitleaks", "detect", "--no-banner", "--redact", "-s", "."], cwd=cwd):
        run_command(["trufflehog", "filesystem", "--no-update", "."], cwd=cwd)

    # --- Language/stack-specific scanners ---

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
