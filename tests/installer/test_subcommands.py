"""End-to-end tests for switch / uninstall / update / doctor.

Task 063-10. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import argparse
import io
import json
import os
from contextlib import redirect_stdout

from _base import FRAMEWORK_ROOT, InstallerTestCase
from installer.cli import main


def _install_ns(target, vendor="claude", **kw) -> argparse.Namespace:
    d = dict(command="install", vendor=vendor, target=target,
             from_path=FRAMEWORK_ROOT, mode="symlink", force=False, dry_run=False,
             no_gitignore=False, force_system_link=False, skip="", verbose=False,
             quiet=True, installer_script_dir=FRAMEWORK_ROOT, max_backups=5)
    d.update(kw)
    return argparse.Namespace(**d)


def _switch_ns(target, vendor, **kw) -> argparse.Namespace:
    d = dict(command="switch", vendor=vendor, target=target, no_backup=False,
             max_backups=5, force=False, quiet=True)
    d.update(kw)
    return argparse.Namespace(**d)


def _uninstall_ns(target, **kw) -> argparse.Namespace:
    d = dict(command="uninstall", target=target, purge=False, all_vendors=False,
             force=False)
    d.update(kw)
    return argparse.Namespace(**d)


def _update_ns(target, **kw) -> argparse.Namespace:
    d = dict(command="update", target=target, prune=False)
    d.update(kw)
    return argparse.Namespace(**d)


def _doctor_ns(target, **kw) -> argparse.Namespace:
    d = dict(command="doctor", target=target, json=False)
    d.update(kw)
    return argparse.Namespace(**d)


class TestSwitch(InstallerTestCase):

    def test_switch_claude_to_antigravity(self) -> None:
        target = self.make_target()
        main(_install_ns(target, vendor="claude"))
        link_before = os.readlink(target / ".agentic-development")

        self.assertEqual(main(_switch_ns(target, vendor="antigravity")), 0)

        self.assertFalse((target / ".claude").exists())            # vendor dir gone
        self.assertFalse((target / "CLAUDE.agentic.md").exists())  # bridge gone
        self.assertFalse((target / "CLAUDE.local.md").exists())
        self.assertTrue((target / "CLAUDE.md").is_file())          # project file kept
        self.assertTrue((target / "GEMINI.md").is_file())          # antigravity bootstrap
        self.assertFalse((target / "AGENTS.md").exists())          # antigravity = GEMINI.md only
        # .agentic-development/ is NOT recreated.
        self.assertEqual(os.readlink(target / ".agentic-development"), link_before)
        # A snapshot of the old vendor was taken.
        backups = list((target / ".agent" / "backups").iterdir())
        self.assertTrue(any("switch-from-claude" in b.name for b in backups))

    def test_switch_without_state_requires_force(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        (target / ".agentic-installer-state.json").unlink()
        self.assertEqual(main(_switch_ns(target, vendor="antigravity")), 3)

    def test_switch_without_state_force_uses_heuristic(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        (target / ".agentic-installer-state.json").unlink()
        self.assertEqual(
            main(_switch_ns(target, vendor="antigravity", force=True)), 0)

    def test_switch_same_vendor_is_noop(self) -> None:
        target = self.make_target()
        main(_install_ns(target, vendor="claude"))
        self.assertEqual(main(_switch_ns(target, vendor="claude")), 0)


class TestUninstall(InstallerTestCase):

    def test_uninstall_keeps_agentic_dev(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        self.assertEqual(main(_uninstall_ns(target)), 0)
        self.assertTrue((target / ".agentic-development").exists())   # kept
        self.assertFalse((target / ".agentic-installer-state.json").exists())
        self.assertFalse((target / ".claude").exists())
        # The System folder-symlink must be removed too (no stale link).
        self.assertFalse((target / "System").is_symlink())
        gitignore = target / ".gitignore"
        text = gitignore.read_text() if gitignore.exists() else ""
        self.assertNotIn("agentic-development framework", text)

    def test_uninstall_purge_removes_agentic_dev(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        self.assertEqual(main(_uninstall_ns(target, purge=True)), 0)
        self.assertFalse((target / ".agentic-development").exists())
        self.assertTrue((target / "CLAUDE.md").is_file())  # protected file survives

    def test_uninstall_without_state_all_vendors(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        (target / ".agentic-installer-state.json").unlink()
        self.assertEqual(main(_uninstall_ns(target, all_vendors=True)), 0)
        self.assertFalse((target / ".claude").exists())

    def test_uninstall_preserves_user_content_in_vendor_dir(self) -> None:
        # A user file inside .claude/ must survive uninstall — the installer
        # removes only its own artifacts, never the whole vendor directory.
        target = self.make_target()
        main(_install_ns(target))
        user_file = target / ".claude" / "my-notes.md"
        user_file.write_text("user notes", encoding="utf-8")
        self.assertEqual(main(_uninstall_ns(target)), 0)
        self.assertTrue(user_file.exists())
        self.assertEqual(user_file.read_text(), "user notes")


class TestUpdate(InstallerTestCase):

    def test_update_relinks_removed_item(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        skills = target / ".agent" / "skills"
        victim = sorted(skills.iterdir())[0]
        victim_name = victim.name
        victim.unlink()  # simulate a lost link
        self.assertEqual(main(_update_ns(target)), 0)
        self.assertTrue((skills / victim_name).is_symlink())

    def test_update_prune_removes_stale(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        skills = target / ".agent" / "skills"
        os.symlink("../../.agentic-development/.agent/skills/ghost-xyz",
                   skills / "ghost-xyz")  # stale — source does not exist
        main(_update_ns(target, prune=True))
        self.assertFalse((skills / "ghost-xyz").is_symlink())

    def test_update_without_state_rejected(self) -> None:
        target = self.make_target()
        self.assertEqual(main(_update_ns(target)), 3)

    def test_update_leaves_settings_json_untouched(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        settings = target / ".claude" / "settings.json"
        before = settings.read_text() if settings.is_file() else None
        main(_update_ns(target))
        after = settings.read_text() if settings.is_file() else None
        self.assertEqual(before, after)


class TestDoctor(InstallerTestCase):

    def test_doctor_healthy_install(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        self.assertEqual(main(_doctor_ns(target)), 0)

    def test_doctor_json_schema(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(_doctor_ns(target, json=True))
        report = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["vendor"], "claude")
        self.assertEqual(report["errors"], [])

    def test_doctor_detects_broken_symlink(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        victim = sorted((target / ".agent" / "skills").iterdir())[0]
        victim.unlink()  # a managed_paths entry now missing
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(_doctor_ns(target, json=True))
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(buf.getvalue())["ok"])

    def test_doctor_detects_tampered_gitignore(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        gitignore = target / ".gitignore"
        gitignore.write_text(
            gitignore.read_text().replace("/System", "/System\n/tampered"),
            encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(_doctor_ns(target, json=True))
        self.assertEqual(rc, 1)
        codes = [e["code"] for e in json.loads(buf.getvalue())["errors"]]
        self.assertIn("HASH_MISMATCH", codes)

    def test_doctor_no_state_is_warning(self) -> None:
        target = self.make_target()
        self.assertEqual(main(_doctor_ns(target)), 0)  # nothing installed → ok

    def test_doctor_clean_after_switch(self) -> None:
        # After a vendor switch, doctor must not false-fail on stale block
        # hashes inherited from the old vendor's state.
        target = self.make_target()
        main(_install_ns(target, vendor="claude"))
        main(_switch_ns(target, vendor="antigravity"))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(_doctor_ns(target, json=True))
        report = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["errors"], [])

    def test_doctor_detects_schema_incomplete_state(self) -> None:
        target = self.make_target()
        main(_install_ns(target))
        # Valid JSON, wrong shape — must not pass as a healthy install.
        (target / ".agentic-installer-state.json").write_text(
            '{"foo": 1}', encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(_doctor_ns(target, json=True))
        self.assertEqual(rc, 1)
        codes = [e["code"] for e in json.loads(buf.getvalue())["errors"]]
        self.assertIn("STATE_SCHEMA", codes)
