"""Platform detection and symlink-capability probing.

Drives the automatic ``--mode symlink`` → ``--mode copy`` fallback on
platforms where symlink creation is unavailable (e.g. Windows without
Developer Mode).
"""
from __future__ import annotations

import os
import platform as _platform
import tempfile
from pathlib import Path


def is_windows() -> bool:
    """Return ``True`` on Windows."""
    return _platform.system() == "Windows"


def _probe(directory: Path) -> bool:
    """Attempt a real symlink inside ``directory``; clean up afterwards."""
    target = directory / ".agentic-symlink-probe.tmp"
    link = directory / ".agentic-symlink-probe.lnk"
    target.write_text("", encoding="utf-8")
    try:
        os.symlink(target.name, link)
        return link.is_symlink()
    finally:
        for path in (link, target):
            try:
                path.unlink()
            except OSError:
                pass


def symlink_supported(probe_dir: Path | None = None) -> bool:
    """Return whether symlinks can be created on the relevant filesystem.

    Probes by creating a real symlink in ``probe_dir`` (or a fresh temp
    directory). Never raises — returns ``False`` on ``OSError`` /
    ``NotImplementedError``.
    """
    try:
        if probe_dir is not None:
            return _probe(Path(probe_dir))
        with tempfile.TemporaryDirectory() as tmp:
            return _probe(Path(tmp))
    except (OSError, NotImplementedError):
        return False
