"""Deterministic retro ownership.

The "skip if sub-workflow" rule cannot be enforced by prose (workflows
have no runtime nesting signal), so ownership is a flock-guarded claim
file: the FIRST workflow of a run claims it; nested workflows see a live
foreign claim and skip their retro step; the owner releases at the end.
Stale claims (default TTL 24h) are silently overwritable so a crashed run
never bricks future retros.
"""

from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path

DEFAULT_TTL_HOURS = 24


def _locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)


def _read(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    raw = b""
    while True:
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        raw += chunk
    if not raw.strip():
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _write(fd, payload):
    data = json.dumps(payload).encode("utf-8")
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, data)
    os.fsync(fd)


def claim(config, run_id, ttl_hours=DEFAULT_TTL_HOURS):
    """Try to claim retro ownership; returns (acquired, current_owner)."""
    path = Path(config.retro_owner_path)
    fd = _locked(path)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        current = _read(fd)
        now = time.time()
        if current:
            fresh = (now - float(current.get("claimed_at", 0))) < ttl_hours * 3600
            if fresh and current.get("run_id") != run_id:
                return False, current.get("run_id")
            if fresh and current.get("run_id") == run_id:
                return True, run_id
        _write(fd, {"run_id": run_id, "claimed_at": now})
        return True, run_id
    finally:
        os.close(fd)


def release(config, run_id, force=False):
    """Release ownership; returns True when the file was cleared."""
    path = Path(config.retro_owner_path)
    if not path.exists():
        return True
    fd = _locked(path)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        current = _read(fd)
        if current and not force and current.get("run_id") != run_id:
            return False
        os.ftruncate(fd, 0)
    finally:
        os.close(fd)
    try:
        path.unlink()
    except OSError:
        pass
    return True


def current(config):
    path = Path(config.retro_owner_path)
    if not path.exists():
        return None
    fd = _locked(path)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH)
        return _read(fd)
    finally:
        os.close(fd)
