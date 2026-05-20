"""Unit tests for installer.symlinks — the link/mkdir actions.

Task 063-05. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import os

from _base import InstallerTestCase
from installer.errors import ConflictError, IntegrityError
from installer.symlinks import link_folder, link_one, link_per_item, make_dir


class SymlinkTestBase(InstallerTestCase):
    """Builds a framework_root + project layout under self.tmp."""

    def setUp(self) -> None:
        super().setUp()
        # framework_root = the in-target .agentic-development directory.
        self.fw = self.tmp / "project" / ".agentic-development"
        (self.fw / ".agent" / "skills").mkdir(parents=True)
        self.project = self.tmp / "project"

    def _make_source(self, rel: str, *, is_dir: bool = True) -> "os.PathLike":
        src = self.fw / rel
        if is_dir:
            src.mkdir(parents=True)
            (src / "marker").write_text("x", encoding="utf-8")
        else:
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text("x", encoding="utf-8")
        return src


class TestLinkOne(SymlinkTestBase):

    def test_fresh_link_is_relative_and_resolves(self) -> None:
        src = self._make_source(".agent/skills/demo")
        link = self.project / ".agent" / "skills" / "demo"
        self.assertEqual(link_one(link, src, self.fw), "created")
        self.assertTrue(link.is_symlink())
        self.assertFalse(os.path.isabs(os.readlink(link)))
        self.assertEqual(link.resolve(), src.resolve())

    def test_rerun_is_already_linked(self) -> None:
        src = self._make_source(".agent/skills/demo")
        link = self.project / ".agent" / "skills" / "demo"
        link_one(link, src, self.fw)
        self.assertEqual(link_one(link, src, self.fw), "already-linked")

    def test_foreign_file_rejected(self) -> None:
        src = self._make_source(".agent/skills/demo")
        link = self.project / ".agent" / "skills" / "demo"
        link.parent.mkdir(parents=True)
        link.write_text("user content", encoding="utf-8")
        with self.assertRaises(ConflictError):
            link_one(link, src, self.fw)

    def test_stale_but_ours_symlink_replaced(self) -> None:
        src1 = self._make_source(".agent/skills/one")
        src2 = self._make_source(".agent/skills/two")
        link = self.project / ".agent" / "skills" / "item"
        link_one(link, src1, self.fw)
        self.assertEqual(link_one(link, src2, self.fw), "replaced")
        self.assertEqual(link.resolve(), src2.resolve())

    def test_foreign_symlink_rejected(self) -> None:
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "target").write_text("x", encoding="utf-8")
        link = self.project / ".agent" / "skills" / "item"
        link.parent.mkdir(parents=True)
        os.symlink(os.path.relpath(outside / "target", link.parent), link)
        src = self._make_source(".agent/skills/demo")
        with self.assertRaises(ConflictError):
            link_one(link, src, self.fw)

    def test_missing_source_rejected(self) -> None:
        link = self.project / ".agent" / "skills" / "ghost"
        with self.assertRaises(ConflictError):
            link_one(link, self.fw / ".agent/skills/ghost", self.fw)

    def test_unreachable_source_raises_integrity(self) -> None:
        # A source that is itself a broken symlink → created link is unreachable.
        broken = self.fw / ".agent" / "skills" / "broken"
        os.symlink("nonexistent-target-xyz", broken)
        link = self.project / ".agent" / "skills" / "broken"
        with self.assertRaises(IntegrityError):
            link_one(link, broken, self.fw)
        self.assertFalse(link.is_symlink())  # rolled back

    def test_traversal_escape_rejected(self) -> None:
        # Source is a real file OUTSIDE the framework root.
        outside = self.tmp / "outside"
        outside.mkdir()
        escape = outside / "passwd"
        escape.write_text("x", encoding="utf-8")
        link = self.project / ".agent" / "skills" / "escape"
        with self.assertRaises(ConflictError):
            link_one(link, escape, self.fw)
        self.assertFalse(link.is_symlink())  # rolled back


class TestLinkPerItem(SymlinkTestBase):

    def test_links_all_entries_skips_dotfiles(self) -> None:
        source = self.fw / ".agent" / "skills"
        for name in ("alpha", "beta"):
            (source / name).mkdir()
        (source / ".DS_Store").write_text("junk", encoding="utf-8")
        target = self.project / ".agent" / "skills"
        counters = link_per_item(target, source, self.fw)
        self.assertEqual(counters["created"], 2)
        self.assertTrue((target / "alpha").is_symlink())
        self.assertFalse((target / ".DS_Store").exists())

    def test_user_file_is_skipped_not_fatal(self) -> None:
        source = self.fw / ".agent" / "skills"
        (source / "alpha").mkdir()
        (source / "beta").mkdir()
        target = self.project / ".agent" / "skills"
        target.mkdir(parents=True)
        (target / "alpha").write_text("user's own skill", encoding="utf-8")
        counters = link_per_item(target, source, self.fw)
        self.assertEqual(counters["created"], 1)   # beta
        self.assertEqual(counters["skipped"], 1)   # alpha (user file)
        self.assertEqual((target / "alpha").read_text(), "user's own skill")

    def test_missing_source_dir_returns_zero_counters(self) -> None:
        counters = link_per_item(self.project / "x", self.fw / "nope", self.fw)
        self.assertEqual(sum(counters.values()), 0)

    def test_rerun_reports_already_linked(self) -> None:
        source = self.fw / ".agent" / "skills"
        for name in ("alpha", "beta"):
            (source / name).mkdir()
        target = self.project / ".agent" / "skills"
        link_per_item(target, source, self.fw)
        counters = link_per_item(target, source, self.fw)  # second run
        self.assertEqual(counters["already_linked"], 2)
        self.assertEqual(counters["created"], 0)

    def test_integrity_error_propagates_not_skipped(self) -> None:
        # An unreachable item is a filesystem-level problem — it must NOT be
        # swallowed as a per-item skip; it propagates for the caller to handle.
        source = self.fw / ".agent" / "skills"
        (source / "good").mkdir()
        os.symlink("nonexistent-target-xyz", source / "bad")
        target = self.project / ".agent" / "skills"
        with self.assertRaises(IntegrityError):
            link_per_item(target, source, self.fw)


class TestLinkFolderAndMkdir(SymlinkTestBase):

    def test_link_folder(self) -> None:
        src = self._make_source(".agent/tools")
        link = self.project / ".agent" / "tools"
        self.assertEqual(link_folder(link, src, self.fw), "created")
        self.assertTrue(link.is_symlink())

    def test_make_dir_creates_gitkeep(self) -> None:
        d = self.project / ".agent" / "sessions"
        make_dir(d)
        self.assertTrue(d.is_dir())
        self.assertTrue((d / ".gitkeep").is_file())

    def test_make_dir_idempotent(self) -> None:
        d = self.project / ".agent" / "sessions"
        make_dir(d)
        make_dir(d)  # must not raise
        self.assertTrue((d / ".gitkeep").is_file())
