"""Marker-delimited managed-block engine, shared by gitignore and bootstrap.

The block body is SHA-256-hashed; the hash is stored in installer state. On
re-run, a hash mismatch (the user hand-edited the block) aborts with a diff
unless ``--force`` is given — the *no silent clobber* guarantee (NFR-2,
ARCHITECTURE §9.5).
"""
from __future__ import annotations

import difflib
import hashlib
import os
import tempfile
from pathlib import Path

from installer.errors import IntegrityError

#: Open/close markers for the ``.gitignore`` managed block.
GITIGNORE_MARKERS = (
    "# >>> agentic-development framework >>>",
    "# <<< end agentic-development framework <<<",
)

#: Open/close markers for managed blocks inside Markdown bootstrap files.
MARKDOWN_MARKERS = (
    "<!-- >>> agentic-development >>> -->",
    "<!-- <<< agentic-development <<< -->",
)


def block_hash(content: str) -> str:
    """Return ``"sha256:<hexdigest>"`` of the block ``content``."""
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _find_markers(lines: list[str], marker_pair: tuple[str, str]) -> tuple[int, int] | None:
    """Return ``(open_index, close_index)`` of a complete block, or ``None``."""
    open_marker, close_marker = marker_pair
    open_index = None
    for i, line in enumerate(lines):
        if line.strip() == open_marker:
            open_index = i
            break
    if open_index is None:
        return None
    for j in range(open_index + 1, len(lines)):
        if lines[j].strip() == close_marker:
            return (open_index, j)
    return None


def _atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (temp file + ``os.replace``)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _save_user_edits(file_path: Path, body: str, backup_dir: Path) -> None:
    """Save a user-modified block body to ``<backup_dir>/<name>.user-edits.txt``."""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / f"{file_path.name}.user-edits.txt").write_text(
        body + "\n", encoding="utf-8"
    )


def extract_block(text: str, marker_pair: tuple[str, str]) -> str | None:
    """Return the inner content of the managed block in ``text``, or ``None``."""
    lines = text.splitlines()
    found = _find_markers(lines, marker_pair)
    if found is None:
        return None
    open_index, close_index = found
    return "\n".join(lines[open_index + 1:close_index])


def inject_block(
    file_path: Path,
    content: str,
    marker_pair: tuple[str, str],
    *,
    state_hash: str | None = None,
    force: bool = False,
    backup_dir: Path | None = None,
) -> str:
    """Create, append, or rewrite the managed block in ``file_path``.

    - Absent file → create it containing only the marker-wrapped block.
    - No marker in an existing file → append the block at EOF (after a blank
      separator line).
    - Marker present → compare the on-disk block hash to ``state_hash``: on
      match (or ``state_hash is None``, a first run) atomically rewrite; on
      mismatch raise ``IntegrityError`` with a unified diff unless ``force``
      (which first saves the user version to ``backup_dir``).

    Returns:
        The SHA-256 hash of the newly written block body.

    Raises:
        IntegrityError: the on-disk block diverged from ``state_hash`` and
            ``force`` is not set.
    """
    file_path = Path(file_path)
    open_marker, close_marker = marker_pair
    body = content.rstrip("\n")
    # Reject a body that contains a marker line — it would create a premature
    # block boundary, corrupting the block and defeating the hash guard.
    for line in body.split("\n"):
        if line.strip() in (open_marker, close_marker):
            raise IntegrityError(
                f"block content contains a line identical to a managed-block "
                f"marker ({line.strip()!r}); refusing to write a self-corrupting "
                f"block into {file_path}"
            )
    new_hash = block_hash(body)
    block_lines = [open_marker, *body.split("\n"), close_marker] if body else \
        [open_marker, close_marker]

    if not file_path.exists():
        _atomic_write(file_path, "\n".join(block_lines) + "\n")
        return new_hash

    original = file_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    found = _find_markers(lines, marker_pair)

    if found is None:
        separator = "\n" if original.strip() else ""
        prefix = original if (original == "" or original.endswith("\n")) else original + "\n"
        _atomic_write(file_path, prefix + separator + "\n".join(block_lines) + "\n")
        return new_hash

    open_index, close_index = found
    current_body = "\n".join(lines[open_index + 1:close_index])

    if state_hash is not None and block_hash(current_body) != state_hash:
        if not force:
            diff = "\n".join(difflib.unified_diff(
                current_body.splitlines(),
                body.splitlines(),
                fromfile="on-disk block (modified outside the installer)",
                tofile="installer block",
                lineterm="",
            ))
            raise IntegrityError(
                f"the managed block in {file_path} was modified outside the "
                f"installer; re-run with --force to overwrite it "
                f"(the old version is saved to a backup).\n{diff}"
            )
        if backup_dir is not None:
            _save_user_edits(file_path, current_body, backup_dir)

    new_lines = lines[:open_index] + block_lines + lines[close_index + 1:]
    _atomic_write(file_path, "\n".join(new_lines) + "\n")
    return new_hash


def strip_block(file_path: Path, marker_pair: tuple[str, str]) -> None:
    """Remove the managed block from ``file_path``; no-op if absent.

    A blank separator line immediately before or after the block is removed
    too, so repeated install/uninstall cycles do not accrete blank lines.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return
    lines = file_path.read_text(encoding="utf-8").splitlines()
    found = _find_markers(lines, marker_pair)
    if found is None:
        return
    open_index, close_index = found
    before = lines[:open_index]
    after = lines[close_index + 1:]
    if before and before[-1].strip() == "":
        before = before[:-1]
    elif after and after[0].strip() == "":
        after = after[1:]
    remaining = before + after
    _atomic_write(file_path, "\n".join(remaining) + "\n" if remaining else "")
