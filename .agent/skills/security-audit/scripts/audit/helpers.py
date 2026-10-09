"""Utility functions for the security audit scanner."""

import math
import os
import unicodedata
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


#: Seconds one external tool may run before its record says `timed_out` (TASK 118 R1.1).
#: `run_tool` reads it at each call. External SAST tools like semgrep can exceed 120 s on a
#: non-trivial repository; a shorter limit killed them mid-scan.
TOOL_TIMEOUT = 600


def run_tool(cmd: List[str], cwd: str, slot: str, where: str = ".") -> Dict:
    """Run one external tool and return its tool record (TASK 118 R1.1).

    The record's `status` is `ran` with the tool's `exit_code`, `not_installed` when the executable
    is not found, or `timed_out` past `TOOL_TIMEOUT`. The tool's stdout goes to file descriptor 2,
    beside its stderr, so the scanner's stdout holds its report alone (R1.9).
    """
    record = {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where,
              "status": "ran", "exit_code": None, "reason": None}
    cmd_str = " ".join(cmd)
    print(f"[*] Running: {cmd_str}", file=sys.stderr)
    sys.stderr.flush()
    try:
        result = subprocess.run(cmd, cwd=cwd, check=False, timeout=TOOL_TIMEOUT, stdout=2)
    except FileNotFoundError:
        print(f"[!] Tool not found: {cmd[0]}", file=sys.stderr)
        record["status"] = "not_installed"
        return record
    except subprocess.TimeoutExpired:
        print(f"[!] Timeout: {cmd_str} exceeded {TOOL_TIMEOUT}s limit", file=sys.stderr)
        record["status"] = "timed_out"
        return record
    record["exit_code"] = result.returncode
    if result.returncode < 0:
        # A signal ended the process: the tool did not finish its scan (TASK 118 D13).
        record["status"] = "killed"
        print(f"[!] {cmd_str} was killed by signal {-result.returncode}", file=sys.stderr)
    elif result.returncode != 0:
        print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
    return record


#: The Unicode categories `printable` escapes: control, format, line and paragraph separator.
ESCAPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")


def printable(text) -> str:
    """`text` with each control, format or separator character escaped (TASK 118 R1.10).

    A path or a message from the scanned tree can hold a newline, an ANSI escape, a bidirectional
    override or a line separator, and with it forge a line of the scanner's output. The categories
    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`.
    """
    out = []
    for char in str(text):
        if unicodedata.category(char) in ESCAPED_CATEGORIES:
            code = ord(char)
            if code <= 0xFF:
                out.append(f"\\x{code:02x}")
            elif code <= 0xFFFF:
                out.append(f"\\u{code:04x}")
            else:
                out.append(f"\\U{code:08x}")
        else:
            out.append(char)
    return "".join(out)


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


class LockfileCopyError(Exception):
    """The lockfile or its `package.json` could not be copied, such as a FIFO (TASK 118 D16)."""


@contextmanager
def npm_audit_dir(lockfile: Path) -> Iterator[Optional[Path]]:
    """A temporary directory holding copies of `lockfile` and its `package.json` (TASK 111 R5.2).

    npm reads `.npmrc` from the directory it runs in, and an audited subdirectory may be vendored
    code: its `.npmrc` could redirect the registry or the cache. A copy leaves it behind; the
    operator's own npm configuration still applies. Yields `None` when no regular `package.json`
    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead. Raises
    `LockfileCopyError` when a copy raises `OSError`; `shutil` refuses a FIFO before it opens one.
    """
    package = lockfile.parent / "package.json"
    if not package.is_file() or package.is_symlink():
        yield None
        return
    with tempfile.TemporaryDirectory(prefix="npm-audit-") as tmp:
        try:
            shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
            shutil.copyfile(package, Path(tmp) / "package.json")
        except OSError as exc:
            raise LockfileCopyError(str(exc)) from exc
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
