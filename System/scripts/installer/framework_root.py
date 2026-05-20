"""Creates and validates ``target/.agentic-development/``.

The framework root inside the target project is either a relative symlink to
a sibling framework clone (``--mode symlink``, default) or a deep copy
(``--mode copy``). All vendor symlinks point inside this directory.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from installer import backup
from installer.copy import copy_tree
from installer.errors import ConfigurationError, ConflictError
from installer.platform import symlink_supported

#: Directory created inside the target project that holds the framework.
AGENTIC_DIR = ".agentic-development"


def validate_framework(framework: Path) -> None:
    """Assert ``framework`` is a usable framework root.

    Raises:
        ConfigurationError: ``.agent/skills/`` or ``System/`` is missing.
    """
    framework = Path(framework)
    missing = []
    if not (framework / ".agent" / "skills").is_dir():
        missing.append(".agent/skills/")
    if not (framework / "System").is_dir():
        missing.append("System/")
    if missing:
        raise ConfigurationError(
            f"{framework} is not a valid framework root — missing: {', '.join(missing)}"
        )


def guard_target(target: Path, framework: Path) -> None:
    """Refuse to operate when ``target`` *is* the framework or lies inside it.

    Raises:
        ConflictError: naming both paths.
    """
    resolved_target = Path(target).resolve()
    resolved_framework = Path(framework).resolve()
    if resolved_target == resolved_framework:
        raise ConflictError(
            f"target and framework are the same directory ({resolved_target}); "
            f"install into a separate project"
        )
    if resolved_target.is_relative_to(resolved_framework):
        raise ConflictError(
            f"target {resolved_target} is inside the framework {resolved_framework}; "
            f"install into a separate project"
        )


def _agentic_path(target: Path) -> Path:
    return Path(target) / AGENTIC_DIR


def _remove(path: Path) -> None:
    """Remove a file, symlink, or directory tree."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _is_our_symlink(path: Path, framework: Path) -> bool:
    """True if ``path`` is a symlink resolving to ``framework``."""
    if not path.is_symlink():
        return False
    try:
        return path.resolve() == Path(framework).resolve()
    except OSError:
        return False


def _looks_like_framework_copy(path: Path) -> bool:
    """True if ``path`` is a real directory shaped like a framework copy."""
    return (
        path.is_dir()
        and not path.is_symlink()
        and (path / ".agent" / "skills").is_dir()
    )


def ensure_agentic_dev_symlink(target: Path, framework: Path, force: bool) -> Path:
    """Create/validate ``target/.agentic-development`` as a relative symlink.

    Idempotent when the symlink already points at ``framework``. Foreign
    content raises ``ConflictError`` unless ``force`` (which snapshots the old
    content to ``.agent/backups/`` before replacing).
    """
    target, framework = Path(target), Path(framework)
    agentic = _agentic_path(target)
    if agentic.is_symlink() or agentic.exists():
        if _is_our_symlink(agentic, framework):
            return agentic  # idempotent — already correct
        if not force:
            raise ConflictError(
                f"{agentic} already exists and is not a symlink to {framework}; "
                f"re-run with --force to back it up and replace it"
            )
        backup.create_snapshot([agentic], target, "agentic-development")
        _remove(agentic)
    target.mkdir(parents=True, exist_ok=True)
    try:
        link_target = os.path.relpath(framework.resolve(), target.resolve())
    except ValueError:
        # Different Windows drives have no relative path — use an absolute one.
        link_target = str(framework.resolve())
    os.symlink(link_target, agentic)
    if not agentic.exists():  # reachability check
        agentic.unlink()
        raise ConflictError(
            f"created symlink {agentic} -> {link_target} is unreachable; "
            f"use --mode copy instead"
        )
    return agentic


def ensure_agentic_dev_copy(target: Path, framework: Path, force: bool) -> Path:
    """Create/validate ``target/.agentic-development`` as a deep copy.

    Idempotent when an existing framework-shaped copy is present. Foreign
    content raises ``ConflictError`` unless ``force`` (snapshot then replace).
    """
    target, framework = Path(target), Path(framework)
    agentic = _agentic_path(target)
    if agentic.is_symlink() or agentic.exists():
        if _looks_like_framework_copy(agentic):
            return agentic  # idempotent — already a framework copy
        if not force:
            raise ConflictError(
                f"{agentic} already exists and is not a framework copy; "
                f"re-run with --force to back it up and replace it"
            )
        backup.create_snapshot([agentic], target, "agentic-development")
        _remove(agentic)
    target.mkdir(parents=True, exist_ok=True)
    copy_tree(framework, agentic)
    return agentic


def ensure_agentic_dev(target: Path, framework: Path, mode: str, force: bool) -> Path:
    """Create/validate ``.agentic-development/`` per ``mode``.

    ``mode='symlink'`` downgrades to copy with a warning when the platform
    cannot create symlinks.

    Raises:
        ConfigurationError: ``mode`` is neither ``symlink`` nor ``copy``.
    """
    if mode == "symlink":
        # Probe the *target's* filesystem, not a temp dir that may sit on a
        # different mount with different symlink support.
        Path(target).mkdir(parents=True, exist_ok=True)
        if not symlink_supported(probe_dir=target):
            print(
                "warning: symlinks are not supported on the target filesystem; "
                "falling back to --mode copy",
                flush=True,
            )
            return ensure_agentic_dev_copy(target, framework, force)
        return ensure_agentic_dev_symlink(target, framework, force)
    if mode == "copy":
        return ensure_agentic_dev_copy(target, framework, force)
    raise ConfigurationError(f"unknown mode: {mode!r} (expected 'symlink' or 'copy')")
