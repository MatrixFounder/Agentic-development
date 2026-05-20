"""Unit tests for installer.framework_root, installer.copy, installer.platform.

Task 063-04. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import os

from _base import FRAMEWORK_ROOT, InstallerTestCase
from installer.copy import IGNORE_NAMES, copy_tree
from installer.errors import ConfigurationError, ConflictError
from installer.framework_root import (
    ensure_agentic_dev,
    ensure_agentic_dev_copy,
    ensure_agentic_dev_symlink,
    guard_target,
    validate_framework,
)
from installer.platform import symlink_supported


def _make_fake_framework(root) -> None:
    """Build a minimal framework-shaped tree at ``root`` for fast tests."""
    (root / ".agent" / "skills" / "demo").mkdir(parents=True)
    (root / ".agent" / "skills" / "demo" / "SKILL.md").write_text("---\n", encoding="utf-8")
    (root / "System").mkdir()
    (root / "CLAUDE.md").write_text("# fw", encoding="utf-8")
    # Things that copy_tree must exclude.
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "stale.pyc").write_text("x", encoding="utf-8")
    # Runtime session state — must NOT land in the copy.
    (root / ".agent" / "sessions").mkdir(parents=True)
    (root / ".agent" / "sessions" / "latest.yaml").write_text("mode: dev\n", encoding="utf-8")
    (root / ".agent" / "sessions" / "latest.yaml.lock").write_text("", encoding="utf-8")
    # A deliberately broken symlink (mirrors the framework's own .cursor/skills).
    os.symlink("does/not/exist", root / "broken.lnk")


class TestValidateFramework(InstallerTestCase):

    def test_real_framework_validates(self) -> None:
        validate_framework(FRAMEWORK_ROOT)  # must not raise

    def test_incomplete_framework_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            validate_framework(self.tmp)


class TestGuardTarget(InstallerTestCase):

    def test_target_equals_framework_rejected(self) -> None:
        with self.assertRaises(ConflictError):
            guard_target(FRAMEWORK_ROOT, FRAMEWORK_ROOT)

    def test_target_inside_framework_rejected(self) -> None:
        with self.assertRaises(ConflictError):
            guard_target(FRAMEWORK_ROOT / "docs", FRAMEWORK_ROOT)

    def test_sibling_target_ok(self) -> None:
        guard_target(self.tmp, FRAMEWORK_ROOT)  # must not raise


class TestSymlinkMode(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.framework = self.tmp / "framework"
        self.framework.mkdir()
        _make_fake_framework(self.framework)
        self.target = self.tmp / "project"
        self.target.mkdir()

    def test_fresh_symlink_resolves_to_framework(self) -> None:
        agentic = ensure_agentic_dev_symlink(self.target, self.framework, force=False)
        self.assertTrue(agentic.is_symlink())
        self.assertEqual(agentic.resolve(), self.framework.resolve())
        # The link target must be relative, not absolute.
        self.assertFalse(os.path.isabs(os.readlink(agentic)))

    def test_rerun_is_idempotent(self) -> None:
        first = ensure_agentic_dev_symlink(self.target, self.framework, force=False)
        link_before = os.readlink(first)
        second = ensure_agentic_dev_symlink(self.target, self.framework, force=False)
        self.assertEqual(os.readlink(second), link_before)

    def test_foreign_content_rejected(self) -> None:
        (self.target / ".agentic-development").mkdir()
        with self.assertRaises(ConflictError):
            ensure_agentic_dev_symlink(self.target, self.framework, force=False)

    def test_force_backs_up_and_replaces(self) -> None:
        foreign = self.target / ".agentic-development"
        foreign.mkdir()
        (foreign / "user-file.txt").write_text("mine", encoding="utf-8")
        agentic = ensure_agentic_dev_symlink(self.target, self.framework, force=True)
        self.assertTrue(agentic.is_symlink())
        backups = list((self.target / ".agent" / "backups").iterdir())
        self.assertEqual(len(backups), 1)


class TestCopyMode(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.framework = self.tmp / "framework"
        self.framework.mkdir()
        _make_fake_framework(self.framework)
        self.target = self.tmp / "project"
        self.target.mkdir()

    def test_copy_excludes_ignore_names(self) -> None:
        agentic = ensure_agentic_dev_copy(self.target, self.framework, force=False)
        self.assertTrue(agentic.is_dir())
        self.assertFalse(agentic.is_symlink())
        self.assertTrue((agentic / ".agent" / "skills" / "demo").is_dir())
        self.assertFalse((agentic / ".git").exists())
        self.assertFalse((agentic / "__pycache__").exists())
        self.assertFalse((agentic / "stale.pyc").exists())

    def test_copy_excludes_session_runtime_state(self) -> None:
        # The framework's .agent/sessions/ runtime state must never be copied.
        agentic = ensure_agentic_dev_copy(self.target, self.framework, force=False)
        self.assertFalse((agentic / ".agent" / "sessions" / "latest.yaml").exists())
        self.assertFalse((agentic / ".agent" / "sessions" / "latest.yaml.lock").exists())

    def test_copy_tolerates_broken_symlink(self) -> None:
        # _make_fake_framework planted broken.lnk — copy must not crash.
        agentic = ensure_agentic_dev_copy(self.target, self.framework, force=False)
        self.assertTrue(agentic.is_dir())

    def test_copy_rerun_idempotent(self) -> None:
        ensure_agentic_dev_copy(self.target, self.framework, force=False)
        ensure_agentic_dev_copy(self.target, self.framework, force=False)  # no raise

    def test_copy_tree_ignore_names_constant(self) -> None:
        for required in (".git", "__pycache__", "*.pyc"):
            self.assertIn(required, IGNORE_NAMES)


class TestEnsureDispatch(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.framework = self.tmp / "framework"
        self.framework.mkdir()
        _make_fake_framework(self.framework)
        self.target = self.tmp / "project"
        self.target.mkdir()

    def test_dispatch_symlink(self) -> None:
        agentic = ensure_agentic_dev(self.target, self.framework, "symlink", force=False)
        # On a symlink-capable FS this is a symlink; otherwise a copy fallback.
        self.assertTrue(agentic.exists())

    def test_dispatch_copy(self) -> None:
        agentic = ensure_agentic_dev(self.target, self.framework, "copy", force=False)
        self.assertTrue(agentic.is_dir())
        self.assertFalse(agentic.is_symlink())

    def test_dispatch_unknown_mode_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            ensure_agentic_dev(self.target, self.framework, "telepathy", force=False)


class TestPlatform(InstallerTestCase):

    def test_symlink_supported_returns_bool(self) -> None:
        self.assertIsInstance(symlink_supported(), bool)

    def test_symlink_supported_with_probe_dir(self) -> None:
        self.assertIsInstance(symlink_supported(self.tmp), bool)
