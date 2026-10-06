"""External security tool integration."""

import os
from pathlib import Path
from typing import List
import sys

from .helpers import find_npm_lockfiles, npm_audit_dir, run_command


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

    # npm audit in each lockfile directory, whatever the detected types (TASK 111 R5.4); a project
    # without an npm lockfile runs none, since npm stops with ENOLOCK there (R5.5).
    for lockfile in find_npm_lockfiles(cwd):
        label = os.path.relpath(lockfile, cwd)
        with npm_audit_dir(lockfile) as workdir:
            if workdir is None:
                print(f"[!] npm audit skipped for {label}: no package.json beside it", file=sys.stderr)
                continue
            print(f"[*] npm audit for {label}", file=sys.stderr)
            run_command(["npm", "audit", "--package-lock-only"], cwd=str(workdir))
    if "javascript" in types and (Path(cwd) / "yarn.lock").exists():
        run_command(["yarn", "audit"], cwd=cwd)

    if "rust" in types:
        run_command(["cargo", "audit"], cwd=cwd)
        run_command(["cargo", "clippy"], cwd=cwd)

    if "go" in types:
        run_command(["govulncheck", "./..."], cwd=cwd)
        run_command(["gosec", "./..."], cwd=cwd)

    if "iac" in types:
        run_command(["checkov", "-d", "."], cwd=cwd)
        run_command(["trivy", "fs", "--scanners", "misconfig", "."], cwd=cwd)

    if "mcp" in types:
        # snyk-agent-scan (formerly Invariant mcp-scan): tool poisoning, tool
        # shadowing, toxic flows across MCP servers and agent skills.
        # SAFETY: NEVER pass --dangerously-skip-permissions-style flags here
        # (e.g. --dangerously-run-mcp-servers) — an audit must not auto-start
        # untrusted MCP servers; starting them is the operator's consent-gated call.
        if not run_command(["snyk-agent-scan", "."], cwd=cwd):
            run_command(["mcp-scan"], cwd=cwd)  # legacy Invariant CLI fallback
