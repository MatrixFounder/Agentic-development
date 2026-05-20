#!/usr/bin/env python3
"""agentic-development framework installer entry-point.

Subcommands: install, switch, update, uninstall, doctor.
Plan: /Users/sergey/.claude/plans/snug-foraging-wind.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python3 System/scripts/install.py` to import the installer package.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from installer.cli import main  # noqa: E402


def _parse_argv(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="install.sh",
        description="agentic-development framework installer",
    )
    parser.add_argument(
        "--installer-script-dir",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,  # passed by bash wrapper; not for users
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")

    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="Install framework into a target project")
    p_install.add_argument("--vendor", default="claude",
                           choices=["claude", "antigravity", "codex", "cursor", "gemini-cli"])
    p_install.add_argument("--target", type=Path, default=Path.cwd())
    p_install.add_argument("--from", dest="from_path", type=Path, default=None,
                           help="Framework root path (defaults to installer's own dir)")
    p_install.add_argument("--mode", choices=["symlink", "copy"], default="symlink")
    p_install.add_argument("--force", action="store_true")
    p_install.add_argument("--dry-run", action="store_true")
    p_install.add_argument("--no-gitignore", action="store_true")
    p_install.add_argument("--force-system-link", action="store_true",
                           help="Force-overwrite existing System/ with framework symlink")
    p_install.add_argument("--skip", default="",
                           help="Comma-separated list of component paths to skip")

    p_switch = sub.add_parser("switch", help="Switch installed vendor")
    p_switch.add_argument("--vendor", required=True,
                          choices=["claude", "antigravity", "codex", "cursor", "gemini-cli"])
    p_switch.add_argument("--target", type=Path, default=Path.cwd())
    p_switch.add_argument("--no-backup", action="store_true")
    p_switch.add_argument("--max-backups", type=int, default=5)
    p_switch.add_argument("--force", action="store_true")

    p_update = sub.add_parser("update", help="Re-sync per-item symlinks")
    p_update.add_argument("--target", type=Path, default=Path.cwd())
    p_update.add_argument("--prune", action="store_true",
                          help="Remove symlinks whose source no longer exists")

    p_uninstall = sub.add_parser("uninstall", help="Remove framework artifacts")
    p_uninstall.add_argument("--target", type=Path, default=Path.cwd())
    p_uninstall.add_argument("--purge", action="store_true",
                             help="Also remove .agentic-development/ itself")
    p_uninstall.add_argument("--all-vendors", action="store_true",
                             help="Heuristic: remove artifacts of all known vendors")
    p_uninstall.add_argument("--force", action="store_true")

    p_doctor = sub.add_parser("doctor", help="Verify install integrity")
    p_doctor.add_argument("--target", type=Path, default=Path.cwd())
    p_doctor.add_argument("--json", action="store_true")

    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_argv(sys.argv[1:])
    sys.exit(main(args))
