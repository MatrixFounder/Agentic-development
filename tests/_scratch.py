"""Scratch-space helpers for the test suite.

Two kinds of scratch space exist here, and the difference is not stylistic:

* **System temp** is the default. Anything that does not have to live inside the
  repository is written under the OS temp directory, so an interrupted run leaves the
  working tree untouched.
* **In-repo scratch** is `tests/.scratch/`. A few scripts under test deliberately refuse
  any path outside the repository root — `sign_off.py`, `verify_gate.py` and
  `compile_brd.py` all call `Path.relative_to(repo_root)` and fail otherwise. Exercising
  their happy path therefore *requires* a workspace inside the tree.

**Why each session gets its own subdirectory.** An earlier version swept the whole shared
root at session start. That corrupted concurrent runs: two plain `pytest` shells against
one checkout failed 25 of 60 times, where the same load before the change failed 0 of 60 —
and three of the failures were *silent passes*, tests whose premise ("this file is
missing") was satisfied for the wrong reason. So a session now owns `s<pid>_<token>/` and
touches nothing else.

**Why the start-up sweep still exists, narrowed.** A run stopped by SIGKILL or a CI
timeout cannot execute its own teardown. The next session therefore removes subdirectories
whose owning process is **gone**, which recovers the debris without ever reaching into a
live session. Keeping the tree out of `git status` is not this sweep's job — `.gitignore`
already covers `tests/.scratch/`.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Single, dot-prefixed root for in-repo scratch, so one `.gitignore` line covers it and
#: a stray directory is obviously debris rather than a fixture someone meant to keep.
REPO_SCRATCH = REPO_ROOT / "tests" / ".scratch"

#: Prefix for a per-session subdirectory. The pid is embedded so a later session can ask
#: whether the owner is still running before deleting anything.
SESSION_PREFIX = "s"

#: Scratch directories used before the layout above existed. Sweeping them keeps a tree
#: that predates this change from staying dirty forever.
LEGACY_SCRATCH = (
    REPO_ROOT / "tests" / "tmp_product_handoff",
    REPO_ROOT / "tests" / "tmp_output",
)

_session_dir: Path | None = None


def _pid_alive(pid: int) -> bool:
    """Return whether a process is running.

    Unknown answers count as **alive**: deleting a live session's workspace is far worse
    than leaving one stale directory behind for the next run to collect.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _ensure_root() -> Path:
    """Return the scratch root, replacing it if it is not a usable directory.

    A symlink here would make every sweep a silent no-op and place workspaces outside the
    repository; a regular file would make directory creation raise. Both are repaired
    rather than tolerated, because both defeat the containment this module exists for.
    """
    if REPO_SCRATCH.is_symlink() or (REPO_SCRATCH.exists() and not REPO_SCRATCH.is_dir()):
        REPO_SCRATCH.unlink()
    REPO_SCRATCH.mkdir(parents=True, exist_ok=True)
    return REPO_SCRATCH


def _remove(path: Path) -> None:
    """Delete a file, symlink or directory, tolerating only its absence.

    Deliberately not `ignore_errors=True`: a cleanup that cannot clean up must not report
    success, or the mechanism silently becomes a no-op.
    """
    try:
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except FileNotFoundError:
        pass


def session_scratch() -> Path:
    """Return this session's private scratch directory, creating it on first use."""
    global _session_dir
    if _session_dir is None or not _session_dir.is_dir():
        _ensure_root()
        _session_dir = Path(
            tempfile.mkdtemp(prefix=f"{SESSION_PREFIX}{os.getpid()}_", dir=REPO_SCRATCH)
        )
    return _session_dir


def repo_scratch_dir(prefix: str = "run_") -> Path:
    """Create a unique scratch directory **inside** the repository.

    Use this only when the code under test requires an in-repo path. Everything else
    belongs in system temp — `tempfile.mkdtemp()` or pytest's `tmp_path`.

    Args:
        prefix: Prefix for the generated directory name.

    Returns:
        Path to a fresh directory inside this session's scratch directory.
    """
    return Path(tempfile.mkdtemp(prefix=prefix, dir=session_scratch()))


def sweep_stale_sessions() -> int:
    """Remove scratch left by sessions that are no longer running, and legacy directories.

    Never touches a live session's directory, including this one.

    Returns:
        How many stale directories were removed.
    """
    removed = 0
    for path in LEGACY_SCRATCH:
        if path.exists() or path.is_symlink():
            _remove(path)
            removed += 1

    if not REPO_SCRATCH.is_dir() or REPO_SCRATCH.is_symlink():
        return removed

    for child in REPO_SCRATCH.iterdir():
        if not child.name.startswith(SESSION_PREFIX):
            _remove(child)  # not ours and not a session dir: debris from an older layout
            removed += 1
            continue
        pid_text = child.name[len(SESSION_PREFIX) :].split("_", 1)[0]
        if not pid_text.isdigit() or not _pid_alive(int(pid_text)):
            _remove(child)
            removed += 1
    return removed


def sweep_session() -> None:
    """Remove only this session's scratch directory, and the root if it is now empty."""
    global _session_dir
    if _session_dir is not None:
        _remove(_session_dir)
        _session_dir = None
    try:
        if REPO_SCRATCH.is_dir() and not any(REPO_SCRATCH.iterdir()):
            REPO_SCRATCH.rmdir()
    except OSError:
        pass
