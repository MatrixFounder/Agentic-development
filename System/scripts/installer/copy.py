"""Deep-copy helper for ``--mode copy`` and the copy variant of framework_root."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

#: Names/globs excluded when copying the framework into ``.agentic-development/``.
IGNORE_NAMES = (
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "node_modules",
    ".hypothesis",
    ".ruff_cache",
    "*.pyc",
    "*.lock",
)


def _is_sessions_dir(directory: str) -> bool:
    """True if ``directory`` is the framework's ``.agent/sessions`` runtime dir."""
    path = Path(directory)
    return path.name == "sessions" and path.parent.name == ".agent"


def _ignore_factory():
    """Build a ``copytree`` ignore callable: :data:`IGNORE_NAMES` + broken
    symlinks + the contents of ``.agent/sessions/`` (runtime session state).

    ``shutil.copytree``'s own ``ignore_dangling_symlinks`` resolves a symlink's
    raw (often relative) target against the *process CWD*, which misidentifies
    relative dangling symlinks (e.g. the framework's own ``.cursor/skills``).
    Excluding broken symlinks here — where the correct full path is known — is
    CWD-independent and reliable.

    ``.agent/sessions/`` holds the framework's own runtime session state
    (``latest.yaml`` and locks); it is never copied into an installed
    framework — the target gets a fresh empty ``.agent/sessions/`` via the
    ``mkdir`` component instead.
    """
    pattern_ignore = shutil.ignore_patterns(*IGNORE_NAMES)

    def ignore(directory, names):
        if _is_sessions_dir(directory):
            return set(names)  # drop all runtime session state from the copy
        ignored = set(pattern_ignore(directory, names))
        for name in names:
            full = os.path.join(directory, name)
            if os.path.islink(full) and not os.path.exists(full):
                ignored.add(name)  # broken symlink — skip it
        return ignored

    return ignore


def copy_tree(src: Path, dst: Path) -> None:
    """Recursively copy ``src`` to ``dst`` with :data:`IGNORE_NAMES` and broken
    symlinks excluded.

    ``symlinks=True`` preserves the framework's internal *relative* symlinks
    (e.g. ``.claude/skills`` → ``../.agent/skills``) AS symlinks — they remain
    self-consistent inside the copy, which stays fully self-contained.

    Dereferencing them with ``symlinks=False`` is unsafe: ``shutil.copytree``
    resolves a symlink's raw relative target against the *process CWD*, so a
    valid framework symlink is silently skipped whenever the installer runs
    from outside the framework root. Broken symlinks are still dropped by
    :func:`_ignore_factory` (CWD-independent — it uses the full path).
    """
    shutil.copytree(
        Path(src),
        Path(dst),
        symlinks=True,
        ignore=_ignore_factory(),
    )
