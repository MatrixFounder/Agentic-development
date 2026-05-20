"""Installer exception hierarchy.

Each error carries an ``exit_code`` the CLI maps onto the process exit status.
See docs/ARCHITECTURE.md §9.2.
"""
from __future__ import annotations


class InstallerError(Exception):
    """Base installer error.

    Attributes:
        exit_code: process exit status the CLI returns for this error. The
            class default may be overridden per-instance via the keyword arg.
    """

    exit_code = 1

    def __init__(self, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class ConfigurationError(InstallerError):
    """Invalid vendors.yaml, vendor profile, or framework layout."""

    exit_code = 2


class ConflictError(InstallerError):
    """A target path collides with user-owned content."""

    exit_code = 3


class IntegrityError(InstallerError):
    """Hash mismatch, broken/unreachable symlink, or corrupt state file."""

    exit_code = 4
