"""Symlink engine: the ``link_per_item`` / ``link_folder`` / ``mkdir`` actions.

All symlinks are created with relative targets pointing inside
``.agentic-development/``. Every created symlink is checked for reachability
and guarded against path-traversal escapes (ARCHITECTURE §9.6): its fully
resolved target must stay inside ``framework_root`` (the target project's
``.agentic-development/`` directory).
"""
from __future__ import annotations

import os
from pathlib import Path

from installer.errors import ConflictError, IntegrityError
from installer.paths import resolves_inside


def _atomic_symlink(link_target: str, link: Path) -> None:
    """Create (or atomically replace) ``link`` pointing at ``link_target``."""
    # Unpredictable temp name (pid + random) so a hostile actor cannot
    # pre-create the path the installer is about to write.
    tmp = link.parent / f".{link.name}.tmp-{os.getpid()}-{os.urandom(4).hex()}"
    try:
        if tmp.is_symlink() or tmp.exists():
            tmp.unlink()
        os.symlink(link_target, tmp)
        os.replace(tmp, link)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def link_one(link: Path, source: Path, framework_root: Path) -> str:
    """Create a single relative symlink ``link`` → ``source``.

    Idempotent: a symlink already pointing at ``source`` is left untouched. An
    existing symlink pointing elsewhere is replaced only if it already resolves
    inside ``framework_root`` (i.e. it is one of ours); a foreign symlink or a
    real file raises ``ConflictError``. After creation the link is checked for
    reachability and confined to ``framework_root``.

    Returns:
        ``"created"`` | ``"already-linked"`` | ``"replaced"``.

    Raises:
        ConflictError: source missing, or a foreign object occupies ``link``,
            or the resolved target escapes ``framework_root``.
        IntegrityError: the created symlink is unreachable (e.g. cross-FS).
    """
    link = Path(link)
    source = Path(source)
    framework_root = Path(framework_root)

    if not source.exists() and not source.is_symlink():
        raise ConflictError(f"link source does not exist: {source}")

    relative = os.path.relpath(source, start=link.parent)

    if link.is_symlink():
        if os.readlink(link) == relative:
            return "already-linked"
        if not resolves_inside(link, framework_root):
            raise ConflictError(
                f"{link} is a symlink to foreign content "
                f"({os.readlink(link)}); refusing to replace it"
            )
        verb = "replaced"
    elif link.exists():
        raise ConflictError(
            f"{link} exists and is not a symlink; refusing to overwrite user content"
        )
    else:
        verb = "created"

    link.parent.mkdir(parents=True, exist_ok=True)
    _atomic_symlink(relative, link)

    try:
        os.stat(link)  # follows the symlink — reachability check
    except OSError as exc:
        link.unlink()
        raise IntegrityError(
            f"symlink {link} -> {relative} is unreachable: {exc}"
        ) from exc

    if not resolves_inside(link, framework_root):
        link.unlink()
        raise ConflictError(
            f"symlink {link} resolves outside the framework root "
            f"({framework_root}); refusing path-traversal escape"
        )
    return verb


def link_per_item(target_dir: Path, source_dir: Path, framework_root: Path) -> dict:
    """Symlink every non-dotfile entry of ``source_dir`` into ``target_dir``.

    Creates ``target_dir`` if absent. A per-item ``ConflictError`` (a
    user-owned file occupies the slot) is a non-fatal skip. ``IntegrityError``
    propagates — an unreachable link is a whole-filesystem problem the caller
    resolves by downgrading to copy mode.

    Returns:
        Counters: ``{created, already_linked, replaced, skipped, conflicts}``.
    """
    target_dir = Path(target_dir)
    source_dir = Path(source_dir)
    counters = {"created": 0, "already_linked": 0, "replaced": 0,
                "skipped": 0, "conflicts": 0}
    if not source_dir.is_dir():
        return counters

    target_dir.mkdir(parents=True, exist_ok=True)
    with os.scandir(source_dir) as entries:
        names = sorted(e.name for e in entries if not e.name.startswith("."))
    for name in names:
        try:
            result = link_one(target_dir / name, source_dir / name, framework_root)
        except ConflictError:
            counters["skipped"] += 1
            counters["conflicts"] += 1
            continue
        counters[result.replace("-", "_")] += 1
    return counters


def link_folder(target: Path, source: Path, framework_root: Path) -> str:
    """Create a single folder-level symlink via :func:`link_one`."""
    return link_one(Path(target), Path(source), framework_root)


def make_dir(target: Path) -> None:
    """Create an empty directory with a ``.gitkeep`` placeholder; idempotent."""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    gitkeep = target / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
