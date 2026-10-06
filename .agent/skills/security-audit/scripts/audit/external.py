"""External security tool integration."""

import json
import os
from pathlib import Path
from typing import List
import sys

from .helpers import find_npm_lockfiles, npm_audit_dir, run_command


#: The `package.json` fields the yarn copy keeps (TASK 112 R5.1). `packageManager` and
#: `devEngines.packageManager` are left out: a corepack `yarn` shim fetches the version they name.
YARN_KEPT_FIELDS = ("name", "version", "private", "workspaces", "resolutions", "dependencies",
                    "devDependencies", "optionalDependencies", "peerDependencies")


def _keep_dependency_fields(package: Path) -> bool:
    """Rewrite the copied `package.json` with `YARN_KEPT_FIELDS` only; False when no JSON object."""
    try:
        data = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    kept = {key: data[key] for key in YARN_KEPT_FIELDS if key in data}
    package.write_text(json.dumps(kept), encoding="utf-8")
    return True


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
    # yarn reads `.yarnrc` and `.yarnrc.yml` where it runs, and `yarnPath` there names a script it
    # executes. It runs in a copy of the lockfile and its `package.json`, as npm does, and the copy
    # keeps the dependency fields only: a corepack `yarn` shim would fetch and run the version that
    # `packageManager` or `devEngines` names (TASK 112 R5.1).
    yarn_lock = Path(cwd) / "yarn.lock"
    if "javascript" in types and (yarn_lock.exists() or yarn_lock.is_symlink()):
        if yarn_lock.is_symlink() or not yarn_lock.is_file():
            print("[!] yarn audit skipped: yarn.lock is a link or not a regular file", file=sys.stderr)
        else:
            with npm_audit_dir(yarn_lock) as workdir:
                if workdir is None:
                    print("[!] yarn audit skipped: no package.json beside yarn.lock", file=sys.stderr)
                elif not _keep_dependency_fields(workdir / "package.json"):
                    print("[!] yarn audit skipped: package.json is not a JSON object", file=sys.stderr)
                else:
                    run_command(["yarn", "audit"], cwd=str(workdir))

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
