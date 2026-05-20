""".gitignore managed block + project-local ``!``-exception scanner.

Keeps framework artifacts out of the target project's git history while
leaving the project's own skills/commands/agents trackable via ``!`` rules.
"""
from __future__ import annotations

from pathlib import Path

from installer.managed_block import GITIGNORE_MARKERS, inject_block
from installer.paths import resolves_inside

#: Directories scanned (top level only) for project-local entries.
_SCAN_DIRS = (
    ".agent/skills", ".agent/workflows", ".agent/agents",
    ".claude/skills", ".claude/commands", ".claude/agents",
)


def _points_into_agentic(entry: Path, target: Path) -> bool:
    """True if symlink ``entry`` resolves to a path inside ``.agentic-development``.

    Uses path resolution (via :func:`installer.paths.resolves_inside`) rather
    than the raw ``readlink`` text: framework symlinks are written as
    ``../../.agentic-development/...``, so inspecting only the first path
    component would misclassify them.
    """
    return resolves_inside(entry, Path(target) / ".agentic-development")


def scan_local_exceptions(target: Path) -> list[str]:
    """Return sorted ``!/path`` lines for project-local (non-framework) entries.

    An entry is project-local when it is not a symlink, or is a symlink that
    does not resolve into ``.agentic-development/``. Dotfiles are skipped.
    A broken framework symlink is reported as a warning and not emitted.
    """
    target = Path(target)
    exceptions: list[str] = []
    for rel in _SCAN_DIRS:
        directory = target / rel
        if not directory.is_dir():
            continue
        for entry in sorted(directory.iterdir()):
            if entry.name.startswith("."):
                continue
            if entry.is_symlink() and _points_into_agentic(entry, target):
                if not entry.exists():
                    print(
                        f"warning: broken framework symlink {entry} — "
                        f"re-run install to repair it",
                        flush=True,
                    )
                continue  # framework symlink — never a project-local exception
            exceptions.append(f"!/{rel}/{entry.name}")
    return sorted(exceptions)


def build_block_body(profile: dict, exceptions: list[str]) -> str:
    """Assemble the ``.gitignore`` managed-block body for a resolved profile.

    ``profile`` must be a *resolved* profile (defaults merged into
    ``components``). Each component contributes an ignore rule; ``link_per_item``
    directories ignore their contents (``/path/*``) while folder/copy/mkdir
    components ignore the path itself. ``mkdir`` directories outside ``.agent/``
    (vendor config dirs such as ``.codex/``) are left trackable.
    """
    lines = [
        "# Managed by the agentic-development installer. Do not edit between the markers.",
        "",
        "# Framework content (symlink or local copy) and installer state.",
        "/.agentic-development/",
        "/.agentic-installer-state.json",
        "",
        "# Framework components.",
    ]
    for component in profile.get("components", []):
        path = component["path"]
        action = component["action"]
        if action == "link_per_item":
            lines.append(f"/{path}/*")
        elif action == "mkdir":
            # Runtime-state dirs under .agent/ are ignored; a vendor config dir
            # (e.g. .codex/) stays trackable so the user can commit its config.
            if path.startswith(".agent/"):
                lines.append(f"/{path}")
        else:  # link_folder, copy
            lines.append(f"/{path}")

    if profile.get("bootstrap_strategy") == "at_import":
        lines += [
            "",
            "# Claude bridge files (gitignored — they import the framework).",
            "/CLAUDE.agentic.md",
            "/CLAUDE.local.md",
        ]

    vendor_dir = profile.get("vendor_dir")
    if vendor_dir:
        lines += ["", f"# {vendor_dir} runtime locks.", f"/{vendor_dir}/*.lock"]

    if exceptions:
        lines += ["", "# Project-local entries (kept in version control)."]
        lines += exceptions

    return "\n".join(lines)


def update_gitignore(
    target: Path,
    profile: dict,
    state: dict,
    *,
    force: bool = False,
    backup_dir: Path | None = None,
) -> str:
    """Inject/update the ``.gitignore`` managed block; return the new hash.

    Delegates hash-protected writing to :func:`managed_block.inject_block`.
    """
    target = Path(target)
    exceptions = scan_local_exceptions(target)
    body = build_block_body(profile, exceptions)
    return inject_block(
        target / ".gitignore", body, GITIGNORE_MARKERS,
        state_hash=state.get("gitignore_block_hash"), force=force, backup_dir=backup_dir,
    )
