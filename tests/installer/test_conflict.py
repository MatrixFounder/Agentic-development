"""Unit tests for installer.conflict — pre-flight conflict classification.

Task 063-09. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import os

from _base import InstallerTestCase
from installer.conflict import (
    classify_path,
    preflight_scan,
    reclassify_before_write,
    system_link_decision,
)
from installer.managed_block import GITIGNORE_MARKERS, inject_block


class ConflictTestBase(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.proj = self.tmp / "proj"
        self.fw = self.proj / ".agentic-development"
        self.fw.mkdir(parents=True)


class TestClassifyPath(ConflictTestBase):

    def test_absent_is_safe(self) -> None:
        self.assertEqual(classify_path(self.proj / "ghost", self.fw), "safe")

    def test_our_symlink_is_our(self) -> None:
        (self.fw / "thing").mkdir()
        link = self.proj / "link"
        os.symlink(".agentic-development/thing", link)
        self.assertEqual(classify_path(link, self.fw), "our")

    def test_foreign_file_with_hard_name(self) -> None:
        (self.proj / "CLAUDE.md").write_text("user memory", encoding="utf-8")
        self.assertEqual(classify_path(self.proj / "CLAUDE.md", self.fw),
                         "hard_conflict")

    def test_foreign_file_with_soft_name(self) -> None:
        skill = self.proj / ".claude" / "skills" / "mine"
        skill.mkdir(parents=True)
        self.assertEqual(classify_path(skill, self.fw), "soft_conflict")

    def test_managed_block_file_is_our(self) -> None:
        gi = self.proj / ".gitignore"
        inject_block(gi, "/.agentic-development/", GITIGNORE_MARKERS)
        self.assertEqual(classify_path(gi, self.fw), "our")

    def test_foreign_symlink_outside_is_conflict(self) -> None:
        outside = self.tmp / "outside"
        outside.mkdir()
        link = self.proj / ".claude" / "x"
        link.parent.mkdir(parents=True)
        os.symlink(os.path.relpath(outside, link.parent), link)
        self.assertEqual(classify_path(link, self.fw), "soft_conflict")

    def test_reclassify_alias(self) -> None:
        self.assertEqual(reclassify_before_write(self.proj / "ghost", self.fw),
                         "safe")


class TestSystemLinkDecision(ConflictTestBase):

    def test_absent_links(self) -> None:
        self.assertEqual(
            system_link_decision(self.proj / "System", self.fw, False), "link")

    def test_foreign_without_flag_skips(self) -> None:
        (self.proj / "System").mkdir()
        self.assertEqual(
            system_link_decision(self.proj / "System", self.fw, False), "skip")

    def test_foreign_with_flag_forces(self) -> None:
        (self.proj / "System").mkdir()
        self.assertEqual(
            system_link_decision(self.proj / "System", self.fw, True), "force")


class TestPreflightScan(ConflictTestBase):

    COMPONENTS = [
        {"path": ".agent/skills", "action": "link_per_item", "source": ".agent/skills"},
        {"path": ".agent/sessions", "action": "mkdir"},
        {"path": ".agent/tools", "action": "link_folder", "source": ".agent/tools"},
        {"path": "System", "action": "link_folder", "source": "System"},
        {"path": ".claude/hooks", "action": "copy", "source": ".claude/hooks"},
    ]

    def test_clean_target_all_installable(self) -> None:
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, set())
        self.assertEqual(len(scan["to_install"]), 5)
        self.assertEqual(scan["hard_skips"], [])
        self.assertEqual(scan["soft_skips"], [])

    def test_skip_flag_moves_to_soft_skips(self) -> None:
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, {".agent/tools"})
        skipped = [e["component"]["path"] for e in scan["soft_skips"]]
        self.assertIn(".agent/tools", skipped)
        self.assertEqual(len(scan["to_install"]), 4)

    def test_foreign_link_folder_is_soft_skip(self) -> None:
        (self.proj / ".agent" / "tools").mkdir(parents=True)  # user-owned dir
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, set())
        skipped = [e["component"]["path"] for e in scan["soft_skips"]]
        self.assertIn(".agent/tools", skipped)
        self.assertIn(".agent/tools", scan["needs_force"])

    def test_foreign_system_is_hard_skip(self) -> None:
        (self.proj / "System").mkdir()  # user-owned
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, set())
        hard = [e["component"]["path"] for e in scan["hard_skips"]]
        self.assertIn("System", hard)

    def test_foreign_system_with_force_flag_installs(self) -> None:
        (self.proj / "System").mkdir()
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, set(),
                              force_system_link=True)
        self.assertIn("System", [c["path"] for c in scan["to_install"]])

    def test_copy_component_never_conflicts(self) -> None:
        # A pre-existing .claude/hooks dir must NOT block the copy component.
        (self.proj / ".claude" / "hooks").mkdir(parents=True)
        scan = preflight_scan(self.proj, self.fw, self.COMPONENTS, set())
        self.assertIn(".claude/hooks", [c["path"] for c in scan["to_install"]])
