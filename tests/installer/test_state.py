"""Unit tests for installer.state and installer.backup.

Task 063-03. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import os
from datetime import datetime

from _base import InstallerTestCase
from installer.backup import apply_retention, create_snapshot
from installer.errors import IntegrityError
from installer.state import (
    STATE_FILENAME,
    heuristic_state,
    load_state,
    new_state,
    save_state,
    state_path,
)


class TestState(InstallerTestCase):

    def test_load_missing_returns_none(self) -> None:
        self.assertIsNone(load_state(self.tmp))

    def test_load_corrupt_json_raises(self) -> None:
        (self.tmp / STATE_FILENAME).write_text("{not json", encoding="utf-8")
        with self.assertRaises(IntegrityError):
            load_state(self.tmp)

    def test_load_non_object_json_raises(self) -> None:
        (self.tmp / STATE_FILENAME).write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(IntegrityError):
            load_state(self.tmp)

    def test_save_load_round_trip(self) -> None:
        state = new_state("claude", "symlink", "/some/framework", True)
        state["managed_paths"] = [".agent/skills/foo", ".claude/agents/bar.md"]
        save_state(self.tmp, state)
        loaded = load_state(self.tmp)
        self.assertEqual(loaded, state)

    def test_save_leaves_no_temp_file(self) -> None:
        save_state(self.tmp, new_state("cursor", "copy", "/fw", False))
        leftovers = [p.name for p in self.tmp.iterdir() if p.name != STATE_FILENAME]
        self.assertEqual(leftovers, [])

    def test_new_state_schema_complete(self) -> None:
        state = new_state("codex", "symlink", "/fw", True)
        for key in ("version", "vendor", "mode", "framework_path",
                    "agentic_development_is_symlink", "installed_at",
                    "gitignore_block_hash", "bootstrap_blocks_hash",
                    "managed_paths", "skipped_components"):
            self.assertIn(key, state)
        self.assertEqual(state["vendor"], "codex")
        self.assertIs(state["agentic_development_is_symlink"], True)

    def test_new_state_installed_at_is_iso8601(self) -> None:
        state = new_state("claude", "symlink", "/fw", True)
        parsed = datetime.fromisoformat(state["installed_at"])  # raises if invalid
        self.assertIsNotNone(parsed)

    def test_state_path(self) -> None:
        self.assertEqual(state_path(self.tmp).name, STATE_FILENAME)


class TestHeuristicState(InstallerTestCase):

    def _build_install(self) -> None:
        """Hand-build a minimal claude-style install under self.tmp."""
        agentic = self.tmp / ".agentic-development"
        (agentic / ".agent" / "skills" / "foo").mkdir(parents=True)
        (self.tmp / ".claude").mkdir()
        skills = self.tmp / ".agent" / "skills"
        skills.mkdir(parents=True)
        os.symlink("../../.agentic-development/.agent/skills/foo", skills / "foo")

    def test_detects_vendor_and_symlinks(self) -> None:
        self._build_install()
        state = heuristic_state(self.tmp)
        self.assertEqual(state["vendor"], "claude")
        self.assertIn(".agent/skills/foo", state["managed_paths"])
        # Result must be schema-pure — no off-schema keys.
        self.assertEqual(set(state), set(new_state("x", "y", "z", False)))

    def test_unknown_when_empty(self) -> None:
        state = heuristic_state(self.tmp)
        self.assertEqual(state["vendor"], "unknown")
        self.assertEqual(state["mode"], "unknown")
        self.assertEqual(state["managed_paths"], [])

    def test_copy_mode_detected(self) -> None:
        (self.tmp / ".agentic-development").mkdir()
        self.assertEqual(heuristic_state(self.tmp)["mode"], "copy")


class TestBackup(InstallerTestCase):

    def test_create_snapshot_copies_existing_skips_missing(self) -> None:
        (self.tmp / ".claude").mkdir()
        (self.tmp / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
        (self.tmp / "CLAUDE.md").write_text("# memory", encoding="utf-8")
        snap = create_snapshot(
            [self.tmp / ".claude", self.tmp / "CLAUDE.md", self.tmp / "missing.txt"],
            self.tmp, "test",
        )
        self.assertTrue((snap / ".claude" / "settings.json").is_file())
        self.assertTrue((snap / "CLAUDE.md").is_file())
        self.assertFalse((snap / "missing.txt").exists())
        self.assertEqual(snap.parent, self.tmp / ".agent" / "backups")

    def test_create_snapshot_preserves_symlink(self) -> None:
        (self.tmp / "real.txt").write_text("x", encoding="utf-8")
        link = self.tmp / "link.txt"
        os.symlink("real.txt", link)
        snap = create_snapshot([link], self.tmp, "test")
        self.assertTrue((snap / "link.txt").is_symlink())

    def test_retention_keeps_newest(self) -> None:
        names = []
        for i in range(5):
            snap = create_snapshot([], self.tmp, f"snap{i}")
            names.append(snap.name)
        apply_retention(self.tmp, max_backups=2)
        remaining = sorted(d.name for d in (self.tmp / ".agent" / "backups").iterdir())
        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining, sorted(names)[-2:])

    def test_retention_floors_at_one(self) -> None:
        # max_backups<=0 must NOT delete everything — the newest snapshot
        # (typically the current operation's backup) is always kept.
        for i in range(3):
            create_snapshot([], self.tmp, f"snap{i}")
        apply_retention(self.tmp, max_backups=0)
        remaining = list((self.tmp / ".agent" / "backups").iterdir())
        self.assertEqual(len(remaining), 1)

    def test_retention_no_backups_dir_is_noop(self) -> None:
        apply_retention(self.tmp, max_backups=5)  # must not raise
