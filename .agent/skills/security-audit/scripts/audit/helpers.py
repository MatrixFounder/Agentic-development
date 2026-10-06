"""Utility functions for the security audit scanner."""

import math
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from .config import (
    MCP_CONFIG_FILENAMES,
    SELF_DIR,
    SEVERITY_ORDER,
    SKIP_DIRS,
    IAC_FILENAMES,
)


def run_command(cmd, cwd=None, shell=False, capture=False, timeout=600) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command, capture exit code, and report status.

    timeout: seconds (default 600s / 10min). External SAST tools like semgrep can easily
    exceed 120s on non-trivial repos; earlier default silently killed them mid-scan.
    """
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    print(f"[*] Running: {cmd_str}", file=sys.stderr)
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=shell, check=False, timeout=timeout,
            capture_output=capture, text=capture
        )
        if result.returncode != 0:
            print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
        return result
    except FileNotFoundError:
        tool_name = cmd[0] if isinstance(cmd, list) else cmd.split()[0]
        print(f"[!] Tool not found: {tool_name}", file=sys.stderr)
        print(f"    Install: see project docs or run via Docker", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"[!] Timeout: {cmd_str} exceeded {timeout}s limit", file=sys.stderr)
        return None


def is_self_path(filepath: str) -> bool:
    """Check if file is within the scanner's own directory (false positive prevention)."""
    try:
        return str(Path(filepath).resolve()).startswith(SELF_DIR)
    except (OSError, ValueError):
        return False


def sort_findings_by_severity(findings: List[Dict]) -> List[Dict]:
    """Sort findings by severity (critical first) to ensure important items are not truncated."""
    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "low"), 99))


def shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob if p > 0)


#: npm lockfiles in the order npm reads them: `npm-shrinkwrap.json` wins over `package-lock.json`.
NPM_LOCKFILES = ("npm-shrinkwrap.json", "package-lock.json")


def find_npm_lockfiles(root_dir: str) -> List[Path]:
    """One npm lockfile per directory under `root_dir` (TASK 111 R5.1).

    The audit of a lockfile below the root was missing: `npm audit` ran at the root only. Skips the
    directories of `SKIP_DIRS`, `node_modules` among them, and follows no symbolic link, to a
    directory or to a lockfile. A directory holding both lockfiles yields `npm-shrinkwrap.json`.
    """
    found = []
    for root, dirs, files in os.walk(root_dir, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in NPM_LOCKFILES:
            path = Path(root) / name
            if name in files and not path.is_symlink():
                found.append(path)
                break
    return found


@contextmanager
def npm_audit_dir(lockfile: Path) -> Iterator[Optional[Path]]:
    """A temporary directory holding copies of `lockfile` and its `package.json` (TASK 111 R5.2).

    npm reads `.npmrc` from the directory it runs in, and an audited subdirectory may be vendored
    code: its `.npmrc` could redirect the registry or the cache. A copy leaves it behind; the
    operator's own npm configuration still applies. Yields `None` when no regular `package.json`
    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead.
    """
    package = lockfile.parent / "package.json"
    if not package.is_file() or package.is_symlink():
        yield None
        return
    with tempfile.TemporaryDirectory(prefix="npm-audit-") as tmp:
        shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
        shutil.copyfile(package, Path(tmp) / "package.json")
        yield Path(tmp)


def detect_project_types(root_dir: str) -> List[str]:
    """Detect project types based on file extensions and config files."""
    types = set()
    for root, dirs, files in os.walk(root_dir, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if any(f.endswith(".sol") for f in files):
            types.add("solidity")
        if any(f.endswith(".py") for f in files):
            types.add("python")
        if any(f.endswith(".js") or f.endswith(".ts") for f in files):
            types.add("javascript")
        if any(f.endswith(".rs") for f in files) or "Cargo.toml" in files:
            types.add("rust")
        if any(f.endswith(".go") for f in files) or "go.mod" in files:
            types.add("go")
        if any(f in IAC_FILENAMES for f in files) or any(f.endswith(".tf") for f in files):
            types.add("iac")
        if any(f in MCP_CONFIG_FILENAMES for f in files):
            types.add("mcp")
    # .vscode is in SKIP_DIRS (pruned above) but is the canonical mcp.json home —
    # probe the project root explicitly so detection still triggers.
    if (Path(root_dir) / ".vscode" / "mcp.json").exists():
        types.add("mcp")
    return list(types)
