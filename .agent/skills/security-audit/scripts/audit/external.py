"""External security tool integration."""

import json
import os
import stat
from pathlib import Path
from typing import List, Optional
import sys

from .helpers import LockfileCopyError, find_npm_lockfiles, npm_audit_dir, printable, run_tool


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


#: `--fail-on` → the `npm audit --audit-level` that makes npm exit non-zero at that threshold
#: (TASK 118 R2.10).
NPM_AUDIT_LEVEL = {"critical": "critical", "high": "high", "medium": "moderate"}

#: The working-tree secret scan: `--no-git` reads the files, the uncommitted ones included
#: (TASK 118 R4.1).
GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
#: The history secret scan: git mode reads the committed history (TASK 118 R4.2).
GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]


def _bare_repository(directory: str) -> Optional[str]:
    """`"bare"` for a regular `HEAD` and the directories `objects` and `refs`; `"bare-link"` when
    the three exist and one is a link (TASK 118 R4.2); `None` otherwise."""
    try:
        modes = [os.lstat(os.path.join(directory, name)).st_mode
                 for name in ("HEAD", "objects", "refs")]
    except OSError:
        return None
    if any(stat.S_ISLNK(mode) for mode in modes):
        return "bare-link"
    head, objects, refs = modes
    if stat.S_ISREG(head) and stat.S_ISDIR(objects) and stat.S_ISDIR(refs):
        return "bare"
    return None


def find_git_entry(root: str, stop: Optional[str] = None) -> Optional[str]:
    """The kind of the first repository at or above `root` (TASK 118 R4.2).

    The walk starts at the real path of `root`, as git does, and checks each parent up to the
    filesystem root, or up to `stop` included. At each directory it reads `.git` with `os.lstat`,
    so a link is reported as `"link"` and never followed, and then checks whether the directory is
    itself a bare repository. Returns `"dir"`, `"file"`, `"link"`, `"other"`, `"unreadable"`,
    `"bare"`, `"bare-link"`, or `None` when nothing matches on the path.
    """
    current = os.path.realpath(root)
    last = os.path.realpath(stop) if stop is not None else None
    while True:
        try:
            mode = os.lstat(os.path.join(current, ".git")).st_mode
        except (FileNotFoundError, NotADirectoryError):
            bare = _bare_repository(current)
            if bare:
                return bare
        except OSError:
            return "unreadable"
        else:
            if stat.S_ISLNK(mode):
                return "link"
            if stat.S_ISDIR(mode):
                return "dir"
            if stat.S_ISREG(mode):
                return "file"
            return "other"
        parent = os.path.dirname(current)
        if current == last or parent == current:
            return None
        current = parent


def incomplete_slots(records: List[dict]) -> List[tuple]:
    """`(slot, last record)` of each slot with no `ran` and no `not_applicable` record (TASK 118 §3).

    A slot is selected when it holds a record, so a slot with no record is never listed. Slots are
    listed in the order of their first record.
    """
    slots = {}
    for record in records:
        slots.setdefault(record["slot"], []).append(record)
    return [(slot, held[-1]) for slot, held in slots.items()
            if not any(r["status"] in ("ran", "not_applicable") for r in held)]


def external_section(records: List[dict]) -> dict:
    """The external section of the report: its status and its records (TASK 118 R1.7).

    The first match sets `status`: `NOT_RUN` when no record ran, `COMPLETE` when every selected
    slot has a `ran` or a `not_applicable` record, `PARTIAL` otherwise.
    """
    if not any(r["status"] == "ran" for r in records):
        status = "NOT_RUN"
    elif incomplete_slots(records):
        status = "PARTIAL"
    else:
        status = "COMPLETE"
    return {"status": status, "tools": records}


def _declined(slot: str, cmd: List[str], where: str, status: str, reason: str) -> dict:
    """The record of a tool the scanner did not start (`not_run` or `not_applicable`)."""
    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": status,
            "exit_code": None, "reason": reason}


def run_external_tools(project_path: str, types: List[str], fail_on=None) -> List[dict]:
    """Run the external tools and return one tool record per tool (TASK 118 R1).

    The slots `sast`, `secrets-tree` and `secrets-history` run for every project, also one with no
    detected type; the others run for the project types that select them. A fallback starts only
    when the first tool of its slot is `not_installed` or `timed_out`. A missing tool is non-fatal:
    its record says so, and `run_audit.py` reports the slot as a part not run.
    """
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"External Tools Scan: {', '.join(types)}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    cwd = project_path
    records = []

    def run(slot, cmd, where=".", workdir=None):
        record = run_tool(cmd, workdir or cwd, slot, where)
        records.append(record)
        return record

    def run_with_fallback(slot, first, fallback):
        if run(slot, first)["status"] in ("not_installed", "timed_out"):
            run(slot, fallback)

    # --- Cross-cutting scanners (run for any project, also with no detected type) ---

    # semgrep — de-facto SAST standard (2024+); auto-config picks rules by language.
    run("sast", ["semgrep", "--config", "auto", "--error", "--quiet", "--timeout", "60", "."])

    # Secret scanners — stronger than regex-only. The working tree first, then the history.
    # trufflehog exits 0 on a finding unless `--fail` is given (R2.10).
    run_with_fallback("secrets-tree", GITLEAKS_TREE,
                      ["trufflehog", "filesystem", "--no-update", "--fail", "."])
    # The history slot has no fallback: `trufflehog git` ran the scanned repository's
    # `core.fsmonitor` command (CVE-2025-41390), so only gitleaks reads the history (R4.3).
    entry = find_git_entry(cwd)
    if entry in ("dir", "file", "bare"):
        run("secrets-history", GITLEAKS_HISTORY)
    elif entry == "unreadable":
        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
                                 ".git could not be read"))
    elif entry == "bare-link":
        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
                                 "the bare repository holds a symbolic link"))
    elif entry == "link":
        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
                                 ".git is a symbolic link"))
    elif entry == "other":
        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
                                 ".git is not a directory or a regular file"))
    else:
        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_applicable",
                                 "no .git at or above the scanned root"))

    # --- Language/stack-specific scanners ---

    if "solidity" in types:
        run("solidity", ["slither", "."])

    if "python" in types:
        run("python-sast", ["bandit", "-r", ".", "-q"])
        # pip-audit replaces safety (Safety DB went commercial in 2024)
        run("python-deps", ["pip-audit"])

    # npm audit in each lockfile directory, whatever the detected types (TASK 111 R5.4); a project
    # without an npm lockfile runs none, since npm stops with ENOLOCK there (R5.5). Under
    # `--fail-on`, `--audit-level` makes npm exit non-zero at that threshold only (TASK 118 R2.10).
    npm = ["npm", "audit", "--package-lock-only"]
    if fail_on in NPM_AUDIT_LEVEL:
        npm.append(f"--audit-level={NPM_AUDIT_LEVEL[fail_on]}")
    for lockfile in find_npm_lockfiles(cwd):
        label = os.path.relpath(lockfile, cwd).replace(os.sep, "/")
        slot = f"npm-audit:{label}"
        try:
            with npm_audit_dir(lockfile) as workdir:
                if workdir is None:
                    reason = "no package.json beside it"
                else:
                    reason = None
                    print(f"[*] npm audit for {printable(label)}", file=sys.stderr)
                    run(slot, npm, where=label, workdir=str(workdir))
        except LockfileCopyError:
            reason = "the lockfile could not be copied"
        if reason:
            print(f"[!] npm audit skipped for {printable(label)}: {reason}", file=sys.stderr)
            records.append(_declined(slot, npm, label, "not_run", reason))
    # yarn reads `.yarnrc` and `.yarnrc.yml` where it runs, and `yarnPath` there names a script it
    # executes. It runs in a copy of the lockfile and its `package.json`, as npm does, and the copy
    # keeps the dependency fields only: a corepack `yarn` shim would fetch and run the version that
    # `packageManager` or `devEngines` names (TASK 112 R5.1).
    yarn_lock = Path(cwd) / "yarn.lock"
    if "javascript" in types and (yarn_lock.exists() or yarn_lock.is_symlink()):
        yarn = ["yarn", "audit"]
        if yarn_lock.is_symlink() or not yarn_lock.is_file():
            reason = "yarn.lock is a link or not a regular file"
        else:
            reason = None
            try:
                with npm_audit_dir(yarn_lock) as workdir:
                    if workdir is None:
                        reason = "no package.json beside yarn.lock"
                    elif not _keep_dependency_fields(workdir / "package.json"):
                        reason = "package.json is not a JSON object"
                    else:
                        run("yarn-audit", yarn, where="yarn.lock", workdir=str(workdir))
            except LockfileCopyError:
                reason = "the lockfile could not be copied"
        if reason:
            print(f"[!] yarn audit skipped: {reason}", file=sys.stderr)
            records.append(_declined("yarn-audit", yarn, "yarn.lock", "not_run", reason))

    if "rust" in types:
        run("rust-deps", ["cargo", "audit"])
        run("rust-lint", ["cargo", "clippy"])

    if "go" in types:
        run("go-deps", ["govulncheck", "./..."])
        run("go-sast", ["gosec", "./..."])

    if "iac" in types:
        run("iac", ["checkov", "-d", "."])
        # trivy exits 0 on a finding unless `--exit-code` is given (R2.10).
        run("iac-misconfig", ["trivy", "fs", "--scanners", "misconfig", "--exit-code", "1", "."])

    if "mcp" in types:
        # snyk-agent-scan (formerly Invariant mcp-scan): tool poisoning, tool
        # shadowing, toxic flows across MCP servers and agent skills.
        # SAFETY: NEVER pass --dangerously-skip-permissions-style flags here
        # (e.g. --dangerously-run-mcp-servers) — an audit must not auto-start
        # untrusted MCP servers; starting them is the operator's consent-gated call.
        run_with_fallback("mcp", ["snyk-agent-scan", "."], ["mcp-scan"])  # legacy Invariant CLI

    return records
