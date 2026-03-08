"""Utility functions for the security audit scanner."""

import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .config import (
    SELF_DIR,
    SEVERITY_ORDER,
    SKIP_DIRS,
    IAC_FILENAMES,
)


def run_command(cmd, cwd=None, shell=False, capture=False) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command, capture exit code, and report status."""
    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
    print(f"[*] Running: {cmd_str}", file=sys.stderr)
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=shell, check=False, timeout=120,
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
        print(f"[!] Timeout: {cmd_str} exceeded 120s limit", file=sys.stderr)
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
    return list(types)
