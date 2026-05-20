"""Vendor-aware bootstrap-file handling.

Two strategies: ``at_import`` (Claude's native 3-file ``@import`` pattern) and
``marker_block`` (Antigravity / Codex / Gemini-CLI — a managed block injected
into the project's ``AGENTS.md`` / ``GEMINI.md``). ``none`` (Cursor) is a no-op.

The ``framework`` argument is the target project's ``.agentic-development/``
directory — framework files are read through it, and ``CLAUDE.agentic.md``
symlinks into it.
"""
from __future__ import annotations

from pathlib import Path

from installer.errors import ConfigurationError
from installer.managed_block import MARKDOWN_MARKERS, inject_block
from installer.symlinks import link_one

#: Project-owned bootstrap files. NEVER overwritten, even with ``--force`` —
#: the installer only touches managed blocks *inside* them.
PROTECTED = frozenset({"CLAUDE.md", "AGENTS.md", "GEMINI.md"})

_CLAUDE_MD_SKELETON = (
    "# Project\n\n"
    "Project-specific agent instructions live in this file.\n\n"
    "The agentic-development framework is imported via `CLAUDE.local.md`.\n"
)


def is_protected(filename: str) -> bool:
    """Return ``True`` if ``filename`` is a never-overwrite bootstrap file."""
    return Path(filename).name in PROTECTED


def _marker_skeleton(name: str) -> str:
    """Header for a freshly created ``marker_block`` bootstrap file."""
    return (
        f"# {name}\n\n"
        f"Project-owned bootstrap file. The agentic-development framework block "
        f"below is managed by the installer — edit outside the markers only.\n"
    )


def _apply_at_import(target: Path, framework: Path, state: dict, result: dict,
                     *, force: bool, backup_dir: Path | None) -> None:
    """Claude 3-file pattern: CLAUDE.md + CLAUDE.local.md + CLAUDE.agentic.md."""
    hashes = state.setdefault("bootstrap_blocks_hash", {})

    claude_md = target / "CLAUDE.md"
    if not claude_md.exists():
        claude_md.write_text(_CLAUDE_MD_SKELETON, encoding="utf-8")
        result["created"].append("CLAUDE.md")

    claude_local = target / "CLAUDE.local.md"
    created_local = not claude_local.exists()
    new_hash = inject_block(
        claude_local, "@CLAUDE.agentic.md", MARKDOWN_MARKERS,
        state_hash=hashes.get("CLAUDE.local.md"), force=force, backup_dir=backup_dir,
    )
    hashes["CLAUDE.local.md"] = new_hash
    result["blocks"]["CLAUDE.local.md"] = new_hash
    if created_local:
        result["created"].append("CLAUDE.local.md")

    agentic_link = target / "CLAUDE.agentic.md"
    verb = link_one(agentic_link, framework / "CLAUDE.md", framework)
    if verb == "created":
        result["created"].append("CLAUDE.agentic.md")


def _apply_marker_block(target: Path, framework: Path, profile: dict, state: dict,
                        result: dict, *, force: bool, backup_dir: Path | None) -> None:
    """Inject the framework block into each of the vendor's bootstrap files."""
    source_name = profile.get("bootstrap_source")
    source_file = framework / source_name
    if not source_file.is_file():
        raise ConfigurationError(
            f"bootstrap_source '{source_name}' not found in framework ({source_file})"
        )
    block = source_file.read_text(encoding="utf-8")

    names = [profile.get("bootstrap_file")] + list(profile.get("bootstrap_aliases", []))
    names = [n for n in dict.fromkeys(names) if n]  # de-dupe, drop None
    hashes = state.setdefault("bootstrap_blocks_hash", {})

    for name in names:
        path = target / name
        if not path.exists():
            path.write_text(_marker_skeleton(name), encoding="utf-8")
            result["created"].append(name)
        new_hash = inject_block(
            path, block, MARKDOWN_MARKERS,
            state_hash=hashes.get(name), force=force, backup_dir=backup_dir,
        )
        hashes[name] = new_hash
        result["blocks"][name] = new_hash


def apply_bootstrap(target: Path, framework: Path, profile: dict, state: dict,
                    *, force: bool = False, backup_dir: Path | None = None) -> dict:
    """Apply the vendor profile's ``bootstrap_strategy`` to ``target``.

    Side effect:
        Updates ``state["bootstrap_blocks_hash"]`` in place with the new block
        hashes (the same hashes are also returned under ``"blocks"``).

    Returns:
        ``{"created": [filenames], "blocks": {filename: hash}}``.

    Raises:
        ConfigurationError: the strategy is unrecognized, or a ``marker_block``
            ``bootstrap_source`` is missing from the framework.
    """
    target = Path(target)
    framework = Path(framework)
    strategy = profile.get("bootstrap_strategy", "none")
    result: dict = {"created": [], "blocks": {}}

    if strategy == "none":
        return result
    if strategy == "at_import":
        _apply_at_import(target, framework, state, result,
                         force=force, backup_dir=backup_dir)
    elif strategy == "marker_block":
        _apply_marker_block(target, framework, profile, state, result,
                            force=force, backup_dir=backup_dir)
    else:
        raise ConfigurationError(f"unknown bootstrap_strategy: {strategy!r}")
    return result
