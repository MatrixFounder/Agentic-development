"""Pre-flight conflict classification — protects user-owned project files.

Every target path is classified BEFORE any filesystem mutation. Hard conflicts
(protected bootstrap files, settings, ``System/``) are skipped with a warning;
soft conflicts (per-item user files) are skipped individually. The classifier
is re-run at write time as a TOCTOU guard (ARCHITECTURE §9.6).
"""
from __future__ import annotations

from pathlib import Path

from installer.managed_block import GITIGNORE_MARKERS, MARKDOWN_MARKERS, extract_block
from installer.paths import resolves_inside

#: Basenames that are HARD conflicts when foreign — never auto-overwritten.
HARD_NAMES = frozenset({
    "CLAUDE.md", "AGENTS.md", "GEMINI.md",
    "settings.json", "settings.local.json", "config.toml", "System",
})


def _is_hard_name(path: Path) -> bool:
    return Path(path).name in HARD_NAMES


def _has_managed_block(path: Path) -> bool:
    """True if ``path`` is a file already carrying one of our managed blocks."""
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return (extract_block(text, GITIGNORE_MARKERS) is not None
            or extract_block(text, MARKDOWN_MARKERS) is not None)


def classify_path(path: Path, framework_root: Path) -> str:
    """Classify a target path: ``safe`` | ``our`` | ``hard_conflict`` | ``soft_conflict``.

    - ``safe`` — does not exist.
    - ``our`` — a symlink resolving inside the framework, or a file carrying
      one of our managed blocks.
    - ``hard_conflict`` — foreign content whose basename is in :data:`HARD_NAMES`.
    - ``soft_conflict`` — any other foreign content.

    (The task spec's ``state`` parameter is intentionally omitted: ownership is
    fully determined by symlink resolution and managed-marker presence.)
    """
    path = Path(path)
    if not path.exists() and not path.is_symlink():
        return "safe"
    if path.is_symlink() and resolves_inside(path, framework_root):
        return "our"
    if not path.is_symlink() and _has_managed_block(path):
        return "our"
    return "hard_conflict" if _is_hard_name(path) else "soft_conflict"


def reclassify_before_write(path: Path, framework_root: Path) -> str:
    """TOCTOU re-check: re-classify ``path`` immediately before mutating it.

    A thin, intention-revealing alias of :func:`classify_path` — call sites use
    this name to make the time-of-write re-verification explicit.
    """
    return classify_path(path, framework_root)


def system_link_decision(system_path: Path, framework_root: Path,
                          force_system_link: bool) -> str:
    """Decide what to do with the ``System/`` link: ``link`` | ``skip`` | ``force``."""
    cls = classify_path(system_path, framework_root)
    if cls in ("safe", "our"):
        return "link"
    return "force" if force_system_link else "skip"


def preflight_scan(target: Path, framework_root: Path, components: list,
                   skip_set: set, force_system_link: bool = False) -> dict:
    """Classify every component before any filesystem mutation.

    Returns a dict with ``to_install`` (list of components) and ``hard_skips`` /
    ``soft_skips`` (lists of ``{"component", "reason"}``) and ``needs_force``
    (list of component paths a ``--force`` run would install).

    (Deviates from the task spec signature: the unused ``profile`` / ``state``
    params are dropped; ``force_system_link`` is added for the ``System/``
    special case.)
    """
    target = Path(target)
    result: dict = {"to_install": [], "hard_skips": [], "soft_skips": [],
                    "needs_force": []}
    for comp in components:
        path = comp["path"]
        action = comp["action"]

        if path in skip_set:
            result["soft_skips"].append({"component": comp, "reason": "--skip flag"})
            continue

        if path == "System":
            decision = system_link_decision(target / "System", framework_root,
                                            force_system_link)
            if decision in ("link", "force"):
                result["to_install"].append(comp)
            else:
                result["hard_skips"].append({
                    "component": comp,
                    "reason": "System/ is user-owned — pass --force-system-link to replace it",
                })
                result["needs_force"].append(path)
            continue

        # These actions never conflict at the component level:
        #  - link_per_item — per-item conflicts handled at symlink-creation time;
        #  - mkdir — idempotent;
        #  - copy — copy-if-absent / keep-if-present (a copied directory is
        #    indistinguishable from a user directory, so it is never clobbered).
        if action in ("link_per_item", "mkdir", "copy"):
            result["to_install"].append(comp)
            continue

        # Only link_folder (a single symlink whose ownership is verifiable)
        # reaches here — classify the target path.
        cls = classify_path(target / path, framework_root)
        if cls in ("safe", "our"):
            result["to_install"].append(comp)
        else:
            bucket = "hard_skips" if cls == "hard_conflict" else "soft_skips"
            result[bucket].append({
                "component": comp,
                "reason": f"user-owned content at {path}",
            })
            result["needs_force"].append(path)
    return result
