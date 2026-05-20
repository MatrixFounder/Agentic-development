"""Shared path-safety helpers for the installer.

Single source of truth for the symlink-confinement check used by the symlink
engine (path-traversal guard), state recovery, and the gitignore scanner.
"""
from __future__ import annotations

from pathlib import Path


def resolves_inside(path: Path, root: Path) -> bool:
    """Return ``True`` if ``path`` fully resolves to a location inside ``root``.

    Used to confirm a symlink stays within the framework and to guard against
    path-traversal escapes. Never raises — a resolution failure yields ``False``.
    """
    try:
        resolved = Path(path).resolve()
        resolved_root = Path(root).resolve()
    except OSError:
        return False
    try:
        return resolved.is_relative_to(resolved_root)
    except ValueError:
        return False
