"""Timestamped backup snapshots with retention.

Destructive operations (``--force`` overwrite, ``switch``) snapshot the
affected paths into ``target/.agent/backups/`` first. Backups always live
under the target's ``.agent/`` — never inside ``.agentic-development/``,
which may be a read-only symlink.
"""
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

#: Backups directory, relative to the target project root.
BACKUPS_SUBDIR = ".agent/backups"


def _timestamp() -> str:
    """UTC timestamp, microsecond precision, lexicographically sortable."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _within(child: Path, parent: Path) -> bool:
    """True if ``child`` is ``parent`` itself or lies inside it."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def create_snapshot(paths: list[Path], target: Path, label: str) -> Path:
    """Copy each existing path in ``paths`` into a fresh snapshot directory.

    The snapshot dir is ``target/.agent/backups/<UTC-timestamp>-<label>/`` and
    the relative layout of each path under ``target`` is preserved. Missing
    paths are skipped silently. Symlinks are copied as symlinks. Overlapping
    inputs are handled: a directory is copied before its children, and any
    path already inside a snapshotted directory is skipped. Returns the
    snapshot directory.
    """
    target = Path(target)
    snapshot = target / BACKUPS_SUBDIR / f"{_timestamp()}-{label}"
    snapshot.mkdir(parents=True, exist_ok=True)

    # Shallowest paths first so a directory copy subsumes its descendants.
    ordered = sorted({Path(p) for p in paths}, key=lambda p: len(p.parts))
    captured: list[Path] = []
    for path in ordered:
        if not path.exists() and not path.is_symlink():
            continue  # nothing to back up
        if any(_within(path, directory) for directory in captured):
            continue  # already captured by a snapshotted ancestor directory
        try:
            relative = path.relative_to(target)
        except ValueError:
            relative = Path(path.name)
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            os.symlink(os.readlink(path), destination)
        elif path.is_dir():
            shutil.copytree(path, destination, symlinks=True)
            captured.append(path)
        else:
            shutil.copy2(path, destination)
    return snapshot


def apply_retention(target: Path, max_backups: int = 5) -> None:
    """Keep the ``max_backups`` newest snapshot directories; delete the rest.

    Snapshot directories sort chronologically by their timestamp-prefixed name.
    ``max_backups`` is floored at 1 — retention never deletes the most recent
    snapshot, which is typically the backup of the operation currently running.
    """
    max_backups = max(1, max_backups)  # never evict the newest snapshot
    backups_dir = Path(target) / BACKUPS_SUBDIR
    if not backups_dir.is_dir():
        return
    snapshots = sorted(d for d in backups_dir.iterdir() if d.is_dir())
    for snapshot in snapshots[:-max_backups]:
        shutil.rmtree(snapshot, ignore_errors=True)
