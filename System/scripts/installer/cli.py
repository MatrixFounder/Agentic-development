"""Installer subcommand dispatch.

``main()`` routes parsed argparse results to a per-subcommand handler and
returns a process exit code. All five subcommands — install / switch / update
/ uninstall / doctor — are implemented here.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from installer import backup
from installer import state as state_mod
from installer.bootstrap import apply_bootstrap
from installer.conflict import preflight_scan, reclassify_before_write
from installer.copy import copy_tree
from installer.errors import (
    ConfigurationError, ConflictError, IntegrityError, InstallerError,
)
from installer.framework_root import ensure_agentic_dev, guard_target, validate_framework
from installer.gitignore import update_gitignore
from installer.managed_block import (
    GITIGNORE_MARKERS, MARKDOWN_MARKERS, block_hash, extract_block, strip_block,
)
from installer.paths import resolves_inside
from installer.symlinks import link_folder, link_per_item, make_dir
from installer.vendors import load_vendors, resolve_profile, validate_profile

#: Vendor directories used for a heuristic sweep when the profile is unknown.
_ALL_VENDOR_DIRS = (".claude", ".gemini", ".codex", ".cursor")
#: Claude bridge files (the only gitignored bootstrap artifacts).
_BRIDGE_FILES = ("CLAUDE.local.md", "CLAUDE.agentic.md")
#: Bootstrap files that may carry a managed block.
_BOOTSTRAP_FILES = ("AGENTS.md", "GEMINI.md")


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

def _resolve_framework(args) -> Path:
    """Resolve the framework root: --from, then $AGENTIC_DEV_ROOT, then the
    installer's own directory."""
    if getattr(args, "from_path", None):
        return Path(args.from_path).resolve()
    env = os.environ.get("AGENTIC_DEV_ROOT")
    if env:
        return Path(env).resolve()
    if getattr(args, "installer_script_dir", None):
        return Path(args.installer_script_dir).resolve()
    return Path(__file__).resolve().parents[3]


def _resolve_framework_from_state(state: dict, target: Path) -> Path:
    """Locate the framework for a post-install command (switch/update)."""
    framework_path = state.get("framework_path")
    if framework_path and Path(framework_path).is_dir():
        return Path(framework_path).resolve()
    agentic = Path(target) / ".agentic-development"
    if agentic.exists():
        return agentic.resolve()
    raise ConfigurationError(
        "cannot locate the framework — .agentic-development/ is missing and "
        "the state file has no usable framework_path"
    )


def _remove(path: Path) -> None:
    """Remove a file, symlink, or directory tree."""
    path = Path(path)
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _vendors_yaml(framework: Path) -> Path:
    return Path(framework) / "System" / "scripts" / "vendors.yaml"


def _prune_empty_dirs(target: Path) -> None:
    """Remove now-empty framework directories (children before parents)."""
    for rel in (".agent/skills", ".agent/workflows", ".agent/agents",
                ".agents/skills", ".agents", ".cursor/skills",
                ".claude/skills", ".claude/commands", ".claude/agents",
                ".gemini", ".cursor", ".claude", ".codex", ".agent"):
        directory = Path(target) / rel
        if directory.is_dir() and not directory.is_symlink():
            try:
                if not any(directory.iterdir()):
                    directory.rmdir()
            except OSError:
                pass


# --------------------------------------------------------------------------
# install
# --------------------------------------------------------------------------

def _install_component(comp: dict, target: Path, agentic: Path, *,
                       force: bool, force_system_link: bool) -> str:
    """Install a single component; return a short status string."""
    action = comp["action"]
    path = comp["path"]
    target_path = Path(target) / path
    source = (Path(agentic) / comp["source"]) if comp.get("source") else None

    if action == "mkdir":
        make_dir(target_path)
        return "ok"

    if action == "copy":
        # copy-if-absent / keep-if-present — a copied dir cannot be told apart
        # from a user dir, so it is never clobbered by `install`.
        if target_path.exists() or target_path.is_symlink():
            return "kept"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            copy_tree(source, target_path)
        else:
            shutil.copy2(source, target_path)
        return "copied"

    if action == "link_per_item":
        try:
            counters = link_per_item(target_path, source, agentic)
        except IntegrityError:
            _remove(target_path)
            copy_tree(source, target_path)
            return "copied (cross-FS fallback)"
        return (f"{counters['created']} linked, "
                f"{counters['already_linked']} existing, "
                f"{counters['skipped']} skipped")

    if action == "link_folder":
        cls = reclassify_before_write(target_path, agentic)  # TOCTOU re-check
        if cls in ("hard_conflict", "soft_conflict"):
            allowed = force or (path == "System" and force_system_link)
            if not allowed:
                return "skipped (user content)"
            backup.create_snapshot([target_path], target, "install")
            _remove(target_path)
        try:
            return link_folder(target_path, source, agentic)
        except IntegrityError:
            if target_path.exists() or target_path.is_symlink():
                _remove(target_path)
            copy_tree(source, target_path)
            return "copied (cross-FS fallback)"

    return "skipped (unknown action)"


def _cmd_install(args) -> int:
    """Install the framework into a target project (10-step algorithm)."""
    quiet = getattr(args, "quiet", False)

    def say(msg: str) -> None:
        if not quiet:
            print(msg)

    # 1. Resolve + validate the framework.
    framework = _resolve_framework(args)
    validate_framework(framework)

    # 2. Resolve the target; guard against installing into the framework.
    target = Path(args.target).resolve()
    guard_target(target, framework)

    # 3. Load + validate the vendor profile.
    vendors = load_vendors(_vendors_yaml(framework))
    vendor = args.vendor
    if vendor not in vendors.get("vendors", {}):
        raise ConfigurationError(f"unknown vendor: {vendor!r}")
    validate_profile(vendor, vendors["vendors"][vendor], framework)
    profile = resolve_profile(vendors, vendor)

    # 3b. Codex git-root requirement (FR-14 runtime check).
    if profile.get("git_root_required") and not (target / ".git").is_dir():
        if not args.force:
            raise ConflictError(
                f"vendor '{vendor}' expects the target to be a git repository "
                f"root, but {target / '.git'} does not exist — re-run with "
                f"--force to override."
            )
        say(f"warning: {target} is not a git root — proceeding (--force).")

    # 4. Pre-flight conflict scan. Read-only — runs BEFORE any filesystem
    #    mutation, using the *intended* .agentic-development path so that
    #    --dry-run makes zero changes.
    agentic_path = target / ".agentic-development"
    skip_set = {s.strip() for s in (args.skip or "").split(",") if s.strip()}
    scan = preflight_scan(target, agentic_path, profile["components"], skip_set,
                          force_system_link=args.force_system_link)
    say(f"pre-flight: {len(scan['to_install'])} to install, "
        f"{len(scan['hard_skips']) + len(scan['soft_skips'])} skipped "
        f"(user conflict), {len(scan['needs_force'])} would need --force.")
    for entry in scan["hard_skips"] + scan["soft_skips"]:
        say(f"  skip: {entry['component']['path']} — {entry['reason']}")
    if args.dry_run:
        say("dry-run: no changes made.")
        return 0

    # 5. Create/validate .agentic-development/ (first filesystem mutation).
    agentic = ensure_agentic_dev(target, framework, args.mode, args.force)

    # State document + a per-run backup directory for --force overwrites.
    state = state_mod.load_state(target) or state_mod.new_state(
        vendor, args.mode, framework, Path(agentic).is_symlink())
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = target / ".agent" / "backups" / f"{timestamp}-install"

    # 6. Bootstrap files.
    apply_bootstrap(target, agentic, profile, state,
                    force=args.force, backup_dir=backup_dir)

    # 7. Install components.
    statuses: dict = {}
    for comp in scan["to_install"]:
        statuses[comp["path"]] = _install_component(
            comp, target, agentic,
            force=args.force, force_system_link=args.force_system_link)

    # 8. Patch .gitignore.
    if not args.no_gitignore:
        state["gitignore_block_hash"] = update_gitignore(
            target, profile, state, force=args.force, backup_dir=backup_dir)

    # 9. Persist state.
    state["vendor"] = vendor
    state["mode"] = args.mode
    state["framework_path"] = str(framework)
    state["agentic_development_is_symlink"] = Path(agentic).is_symlink()
    state["managed_paths"] = state_mod.collect_managed_symlinks(target)
    state["skipped_components"] = sorted(
        {e["component"]["path"] for e in scan["hard_skips"] + scan["soft_skips"]})
    state_mod.save_state(target, state)
    backup.apply_retention(target, max_backups=getattr(args, "max_backups", 5))

    # 10. Summary.
    say(f"\ninstalled vendor '{vendor}' ({args.mode} mode) into {target}")
    for path, status in statuses.items():
        say(f"  {path}: {status}")
    if state["skipped_components"]:
        say(f"skipped (user content): {', '.join(state['skipped_components'])}")
    return 0


# --------------------------------------------------------------------------
# removal — shared by switch and uninstall
# --------------------------------------------------------------------------

def _remove_install(target: Path, state: dict, vendors: dict | None, *,
                    keep_sessions: bool, purge: bool, sweep_all: bool = False) -> list:
    """Remove framework artifacts. Returns the list of paths actually removed.

    Project-owned files (``CLAUDE.md`` / ``AGENTS.md`` / ``GEMINI.md`` and any
    non-symlink user content) are preserved. ``.agent/sessions/`` is kept when
    ``keep_sessions`` is set (switch). ``purge`` additionally removes
    ``.agentic-development/``. ``sweep_all`` removes every known vendor's dir.
    """
    target = Path(target)
    removed: list = []
    vendor = state.get("vendor")
    profile = (vendors or {}).get("vendors", {}).get(vendor, {}) if vendors else {}

    # 1. Framework symlinks — the union of the state's recorded set and a
    #    fresh filesystem scan. The scan catches links created after the state
    #    was last saved, and any link a stale or heuristic state failed to
    #    record, so no broken framework symlink survives an uninstall.
    recorded = set(state.get("managed_paths", []))
    on_disk = set(state_mod.collect_managed_symlinks(target))
    for rel in sorted(recorded | on_disk):
        path = target / rel
        if path.is_symlink():
            path.unlink()
            removed.append(rel)

    # 2. Vendor copy-components (hooks, settings files) and mkdir .gitkeep
    #    placeholders. These are framework artifacts — safe to remove. For a
    #    heuristic / --all-vendors sweep, every vendor's components are covered.
    profiles = (list((vendors or {}).get("vendors", {}).values())
                if sweep_all else [profile])
    for prof in profiles:
        for comp in prof.get("components", []):
            action, cpath = comp.get("action"), target / comp["path"]
            if action == "copy" and (cpath.exists() or cpath.is_symlink()):
                _remove(cpath)
                removed.append(comp["path"])
            elif action == "mkdir" and comp["path"] != ".agent/sessions":
                gitkeep = cpath / ".gitkeep"
                if gitkeep.is_file():
                    gitkeep.unlink()
                    removed.append(f"{comp['path']}/.gitkeep")
    if sweep_all and not vendors:  # degraded mode — no vendors.yaml
        for vdir in _ALL_VENDOR_DIRS:
            for leaf in ("hooks", "settings.json", "settings.local.json",
                         ".gitkeep"):
                cpath = target / vdir / leaf
                if cpath.exists() or cpath.is_symlink():
                    _remove(cpath)
                    removed.append(f"{vdir}/{leaf}")

    # 3. Vendor directories are NOT removed wholesale — that would destroy
    #    user-owned content inside them. The framework artifacts (managed
    #    symlinks from step 1, copy-components from step 2) are gone; an empty
    #    vendor dir is pruned in step 8, a non-empty one (user files) is kept.

    # 4. Claude bridge files.
    for name in _BRIDGE_FILES:
        path = target / name
        if path.exists() or path.is_symlink():
            path.unlink()
            removed.append(name)

    # 5. Strip managed blocks from bootstrap files (the files themselves stay).
    for name in _BOOTSTRAP_FILES:
        strip_block(target / name, MARKDOWN_MARKERS)

    # 6. Strip the .gitignore managed block.
    strip_block(target / ".gitignore", GITIGNORE_MARKERS)

    # 7. Runtime-state directory.
    sessions = target / ".agent" / "sessions"
    if not keep_sessions and sessions.is_dir() and not sessions.is_symlink():
        _remove(sessions)
        removed.append(".agent/sessions")

    # 8. Prune now-empty framework directories (user content keeps them alive).
    _prune_empty_dirs(target)

    # 9. Purge the framework root.
    if purge:
        agentic = target / ".agentic-development"
        if agentic.exists() or agentic.is_symlink():
            _remove(agentic)
            removed.append(".agentic-development")
    return removed


# --------------------------------------------------------------------------
# switch
# --------------------------------------------------------------------------

def _cmd_switch(args) -> int:
    """Switch the installed vendor — remove the old, install the new."""
    target = Path(args.target).resolve()
    new_vendor = args.vendor

    state = state_mod.load_state(target)
    heuristic = state is None
    if heuristic:
        if not args.force:
            raise ConflictError(
                "no installer state found — cannot determine the current "
                "vendor. Re-run with --force to switch using heuristic detection."
            )
        state = state_mod.heuristic_state(target)

    old_vendor = state.get("vendor")
    if old_vendor == new_vendor:
        print(f"vendor is already '{new_vendor}' — nothing to switch.")
        return 0

    framework = _resolve_framework_from_state(state, target)
    vendors = load_vendors(_vendors_yaml(framework))
    if new_vendor not in vendors.get("vendors", {}):
        raise ConfigurationError(f"unknown vendor: {new_vendor!r}")

    # Snapshot the old vendor's artifacts before removing them. Every vendor
    # dir is snapshotted (a heuristic switch may not know the exact old vendor).
    if not args.no_backup:
        snapshot_paths = [target / rel for rel in state.get("managed_paths", [])]
        for extra in (*_BRIDGE_FILES, *_BOOTSTRAP_FILES, ".gitignore"):
            snapshot_paths.append(target / extra)
        for vdir in _ALL_VENDOR_DIRS:
            snapshot_paths.append(target / vdir)
        backup.create_snapshot(snapshot_paths, target, f"switch-from-{old_vendor}")
        backup.apply_retention(target, max_backups=args.max_backups)

    # Remove the old vendor's artifacts (.agentic-development/ is NOT touched).
    # A heuristic switch sweeps every vendor's components — the exact old
    # vendor cannot be trusted when there was no state file.
    _remove_install(target, state, vendors, keep_sessions=True, purge=False,
                    sweep_all=heuristic)

    # Replace the old state with a clean one for the new vendor so the install
    # half does not inherit the old vendor's block hashes (which would make a
    # later `doctor` run flag stale, already-removed files). Writing — rather
    # than deleting — keeps a valid state file on disk throughout the switch,
    # so a crash mid-switch stays recoverable.
    agentic_dir = target / ".agentic-development"
    state_mod.save_state(target, state_mod.new_state(
        new_vendor, state.get("mode", "symlink"), framework,
        agentic_dir.is_symlink()))

    # Install the new vendor. force=True replaces what is left over.
    install_args = argparse.Namespace(
        command="install", vendor=new_vendor, target=target, from_path=framework,
        mode=state.get("mode", "symlink"), force=True, dry_run=False,
        no_gitignore=False, force_system_link=False, skip="", verbose=False,
        quiet=getattr(args, "quiet", False), installer_script_dir=None,
        max_backups=args.max_backups,
    )
    result = _cmd_install(install_args)
    if result == 0:
        print(f"switched vendor: {old_vendor} -> {new_vendor}")
    return result


# --------------------------------------------------------------------------
# uninstall
# --------------------------------------------------------------------------

def _cmd_uninstall(args) -> int:
    """Remove framework artifacts from a target project."""
    target = Path(args.target).resolve()
    state = state_mod.load_state(target)
    heuristic = state is None
    if heuristic:
        state = state_mod.heuristic_state(target)

    vendors = None
    try:
        framework = _resolve_framework_from_state(state, target)
        vendors = load_vendors(_vendors_yaml(framework))
    except (ConfigurationError, InstallerError):
        vendors = None  # degraded mode — framework already gone

    # Snapshot before destroying (ARCHITECTURE §9.6).
    snapshot_paths = [target / rel for rel in state.get("managed_paths", [])]
    for extra in (*_BRIDGE_FILES, *_BOOTSTRAP_FILES, ".gitignore"):
        snapshot_paths.append(target / extra)
    for vdir in _ALL_VENDOR_DIRS:
        snapshot_paths.append(target / vdir)
    backup.create_snapshot(snapshot_paths, target, "uninstall")

    sweep_all = heuristic or args.all_vendors
    removed = _remove_install(target, state, vendors, keep_sessions=False,
                              purge=args.purge, sweep_all=sweep_all)

    # The state file is removed last so a crash mid-uninstall stays recoverable.
    state_file = state_mod.state_path(target)
    if state_file.exists():
        state_file.unlink()

    print(f"uninstalled — removed {len(removed)} framework artifact(s).")
    if not args.purge and (target / ".agentic-development").exists():
        print("  .agentic-development/ kept (pass --purge to remove it).")
    return 0


# --------------------------------------------------------------------------
# update
# --------------------------------------------------------------------------

def _prune_stale_symlinks(directory: Path, agentic: Path) -> int:
    """Remove framework symlinks in ``directory`` whose source no longer exists."""
    pruned = 0
    if not directory.is_dir():
        return 0
    for entry in directory.iterdir():
        if (entry.is_symlink() and resolves_inside(entry, agentic)
                and not entry.exists()):
            entry.unlink()
            pruned += 1
    return pruned


def _cmd_update(args) -> int:
    """Re-sync per-item symlinks so new framework items are picked up."""
    target = Path(args.target).resolve()
    state = state_mod.load_state(target)
    if state is None:
        raise ConflictError("no installer state found — run `install` first.")

    framework = _resolve_framework_from_state(state, target)
    vendors = load_vendors(_vendors_yaml(framework))
    vendor = state.get("vendor")
    if vendor not in vendors.get("vendors", {}):
        raise ConfigurationError(f"state references unknown vendor: {vendor!r}")
    profile = resolve_profile(vendors, vendor)
    agentic = target / ".agentic-development"

    linked = pruned = 0
    for comp in profile["components"]:
        if comp["action"] != "link_per_item":
            continue
        target_dir = target / comp["path"]
        source_dir = agentic / comp["source"]
        if source_dir.is_dir():
            try:
                counters = link_per_item(target_dir, source_dir, agentic)
                linked += counters["created"]
            except IntegrityError:
                # Cross-FS — the per-item symlink is unreachable; copy instead.
                if target_dir.exists() or target_dir.is_symlink():
                    _remove(target_dir)
                copy_tree(source_dir, target_dir)
        if args.prune:
            pruned += _prune_stale_symlinks(target_dir, agentic)

    state["managed_paths"] = state_mod.collect_managed_symlinks(target)
    state_mod.save_state(target, state)
    print(f"update complete — {linked} new link(s), {pruned} stale link(s) pruned.")
    return 0


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------

def _check_block_hash(file_path: Path, markers, expected: str) -> bool:
    """True if the managed block in ``file_path`` matches ``expected`` hash."""
    if not file_path.exists():
        return False
    body = extract_block(file_path.read_text(encoding="utf-8"), markers)
    return body is not None and block_hash(body) == expected


def _cmd_doctor(args) -> int:
    """Verify install integrity (read-only)."""
    target = Path(args.target).resolve()
    report: dict = {"ok": True, "vendor": None, "errors": [], "warnings": []}

    def error(code: str, path: str, detail: str) -> None:
        report["ok"] = False
        report["errors"].append({"code": code, "path": path, "detail": detail})

    def warn(code: str, path: str, reason: str) -> None:
        report["warnings"].append({"code": code, "path": path, "reason": reason})

    try:
        state = state_mod.load_state(target)
    except IntegrityError as exc:
        error("STATE_CORRUPT", state_mod.STATE_FILENAME, str(exc))
        state = None

    if state is None and report["ok"]:
        warn("NO_STATE", str(target),
             "no installer state file — nothing installed here, or state lost")

    if state is not None:
        report["vendor"] = state.get("vendor")
        agentic = target / ".agentic-development"

        # State-schema check (FR-12) — a valid-JSON file with the wrong shape
        # must not pass as a healthy install.
        _required_keys = {
            "version", "vendor", "mode", "framework_path",
            "agentic_development_is_symlink", "installed_at",
            "gitignore_block_hash", "bootstrap_blocks_hash",
            "managed_paths", "skipped_components",
        }
        missing_keys = _required_keys - set(state)
        if missing_keys:
            error("STATE_SCHEMA", state_mod.STATE_FILENAME,
                  f"state file is missing required keys: {sorted(missing_keys)}")

        for rel in state.get("managed_paths", []):
            path = target / rel
            if not path.exists():
                error("BROKEN_SYMLINK", rel, "managed symlink is missing or unreachable")
            elif path.is_symlink() and not resolves_inside(path, agentic):
                error("BROKEN_SYMLINK", rel, "symlink resolves outside the framework")

        gi_hash = state.get("gitignore_block_hash")
        if gi_hash and not _check_block_hash(target / ".gitignore",
                                             GITIGNORE_MARKERS, gi_hash):
            error("HASH_MISMATCH", ".gitignore",
                  "the .gitignore managed block was modified outside the installer")

        for name, expected in state.get("bootstrap_blocks_hash", {}).items():
            if not _check_block_hash(target / name, MARKDOWN_MARKERS, expected):
                error("HASH_MISMATCH", name,
                      "the managed block was modified outside the installer")

        if state.get("vendor") == "codex" and not (target / ".git").is_dir():
            warn("GIT_ROOT_MISSING", str(target),
                 "Codex expects the target to be a git repository root")

        for component in state.get("skipped_components", []):
            warn("SKIPPED_COMPONENT", component, "user-owned at install time")

    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        status = "ok" if report["ok"] else "PROBLEMS FOUND"
        print(f"doctor: {status} (vendor: {report['vendor']})")
        for item in report["errors"]:
            print(f"  ERROR  {item['code']} {item['path']}: {item['detail']}")
        for item in report["warnings"]:
            print(f"  warn   {item['code']} {item['path']}: {item['reason']}")
    return 0 if report["ok"] else 1


# --------------------------------------------------------------------------
# dispatch
# --------------------------------------------------------------------------

_HANDLERS = {
    "install": _cmd_install,
    "switch": _cmd_switch,
    "update": _cmd_update,
    "uninstall": _cmd_uninstall,
    "doctor": _cmd_doctor,
}


def main(args) -> int:
    """Dispatch ``args.command`` to its handler; return a process exit code.

    Any ``InstallerError`` raised by a handler is caught, its message printed
    to stderr, and its ``exit_code`` returned as the process status.
    """
    command = getattr(args, "command", None)
    handler = _HANDLERS.get(command)
    if handler is None:
        print(f"Unknown command: {command!r}", file=sys.stderr)
        return 2
    try:
        return handler(args)
    except InstallerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
