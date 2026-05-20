"""Installer state file: ``<target>/.agentic-installer-state.json``.

The state file lives at the target project root (not inside ``.agent/``) so
it survives ``switch`` / ``uninstall`` operations — see ARCHITECTURE §9.5.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from installer.errors import IntegrityError
from installer.paths import resolves_inside

#: Name of the installer state file, relative to the target project root.
STATE_FILENAME = ".agentic-installer-state.json"

#: Schema version of the state document.
STATE_VERSION = 1

#: Vendor directories that unambiguously identify a vendor on disk. Antigravity
#: has no vendor_dir, so it is not heuristically detectable here.
_VENDOR_DIRS = {
    ".claude": "claude",
    ".gemini": "gemini-cli",
    ".codex": "codex",
    ".cursor": "cursor",
}

#: Paths scanned for framework symlinks during state recording and recovery.
#: Includes per-item directories (scanned entry-by-entry) and folder-level
#: symlink targets (``.agent/tools``, ``.agent/rules``, ``.agents/skills``,
#: ``System``) which are themselves symlinks.
_SCAN_DIRS = (
    ".agent/skills", ".agent/workflows", ".agent/agents", ".agent/tools", ".agent/rules",
    ".claude/skills", ".claude/commands", ".claude/agents",
    ".cursor/skills", ".agents/skills", "System",
)


def state_path(target: Path) -> Path:
    """Return the path of the state file inside ``target``."""
    return Path(target) / STATE_FILENAME


def load_state(target: Path) -> dict | None:
    """Return the parsed state dict, or ``None`` when the file is absent.

    Raises:
        IntegrityError: the file exists but is unreadable or not a JSON object.
    """
    path = state_path(target)
    if not path.exists():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise IntegrityError(f"cannot read state file {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise IntegrityError(f"state file {path} is corrupt JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise IntegrityError(f"state file {path} must contain a JSON object")
    return data


def save_state(target: Path, state: dict) -> None:
    """Atomically write ``state`` to the state file (temp file + ``os.replace``)."""
    path = state_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".state-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def new_state(vendor: str, mode: str, framework_path, is_symlink: bool) -> dict:
    """Build a schema-complete state dict per ARCHITECTURE §9.3."""
    return {
        "version": STATE_VERSION,
        "vendor": vendor,
        "mode": mode,
        "framework_path": str(framework_path),
        "agentic_development_is_symlink": bool(is_symlink),
        "installed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "gitignore_block_hash": None,
        "bootstrap_blocks_hash": {},
        "managed_paths": [],
        "skipped_components": [],
    }


def _points_into_agentic(link: Path, target: Path) -> bool:
    """True if ``link`` resolves to a path inside ``target/.agentic-development``."""
    return resolves_inside(link, Path(target) / ".agentic-development")


def collect_managed_symlinks(target: Path) -> list[str]:
    """Return repo-relative paths of every symlink pointing into the framework."""
    target = Path(target)
    found: list[str] = []
    for rel in _SCAN_DIRS:
        directory = target / rel
        if directory.is_symlink():
            if _points_into_agentic(directory, target):
                found.append(rel)
            continue
        if directory.is_dir():
            for entry in sorted(directory.iterdir()):
                if entry.is_symlink() and _points_into_agentic(entry, target):
                    found.append(str(entry.relative_to(target)))
    return sorted(found)


def heuristic_state(target: Path) -> dict:
    """Reconstruct a best-effort state dict from the current filesystem.

    Used when the state file is missing (``switch`` / ``uninstall`` recovery,
    Issue I7.2). Detects the framework mode, a best-guess vendor, and the set
    of framework symlinks. The result is a schema-pure state dict — callers
    that invoke this function already know the state was reconstructed.
    """
    target = Path(target)
    agentic = target / ".agentic-development"
    if agentic.is_symlink():
        mode, is_symlink = "symlink", True
        framework_path = os.path.realpath(agentic)
    elif agentic.is_dir():
        mode, is_symlink = "copy", False
        framework_path = str(agentic)
    else:
        mode, is_symlink, framework_path = "unknown", False, ""

    vendor = "unknown"
    for vendor_dir, vendor_name in _VENDOR_DIRS.items():
        if (target / vendor_dir).exists():
            vendor = vendor_name
            break

    state = new_state(vendor, mode, framework_path, is_symlink)
    state["managed_paths"] = collect_managed_symlinks(target)
    return state
