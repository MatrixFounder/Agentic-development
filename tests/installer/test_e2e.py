"""End-to-end tests for the installer CLI.

Task 063-09 replaces the Stub-phase smoke test with real ``install`` behavior
assertions (Task 063-11 adds the remaining vendor/mode scenarios). The
still-stubbed subcommands keep a lightweight dispatch smoke.

Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import argparse

from _base import FRAMEWORK_ROOT, InstallerTestCase
from installer.cli import main


def install_args(target, **overrides) -> argparse.Namespace:
    """Build a complete argparse.Namespace for the ``install`` subcommand."""
    ns = dict(
        command="install", vendor="claude", target=target,
        from_path=FRAMEWORK_ROOT, mode="symlink", force=False, dry_run=False,
        no_gitignore=False, force_system_link=False, skip="",
        verbose=False, quiet=True, installer_script_dir=FRAMEWORK_ROOT,
        max_backups=5,
    )
    ns.update(overrides)
    return argparse.Namespace(**ns)


def switch_args(target, vendor, **overrides) -> argparse.Namespace:
    """Build a complete argparse.Namespace for the ``switch`` subcommand."""
    ns = dict(command="switch", vendor=vendor, target=target, no_backup=False,
              max_backups=5, force=False, quiet=True)
    ns.update(overrides)
    return argparse.Namespace(**ns)


class TestDispatch(InstallerTestCase):
    """CLI dispatch behavior. (switch/update/uninstall/doctor are exercised
    end-to-end in test_subcommands.py.)"""

    def test_unknown_command_returns_exit_2(self) -> None:
        self.assertEqual(main(argparse.Namespace(command="bogus")), 2)


class TestInstallSymlinkMode(InstallerTestCase):

    def test_fresh_install(self) -> None:
        target = self.make_target()
        self.assertEqual(main(install_args(target)), 0)
        # .agentic-development is a symlink to the framework.
        agentic = target / ".agentic-development"
        self.assertTrue(agentic.is_symlink())
        self.assertEqual(agentic.resolve(), FRAMEWORK_ROOT.resolve())
        # .agent/skills holds per-item symlinks into the framework.
        skills = target / ".agent" / "skills"
        self.assertTrue(skills.is_dir())
        self.assertTrue(any(p.is_symlink() for p in skills.iterdir()))
        # Claude bridge files.
        self.assertTrue((target / "CLAUDE.agentic.md").is_symlink())
        self.assertIn("@CLAUDE.agentic.md",
                      (target / "CLAUDE.local.md").read_text())
        # .gitignore managed block + state file.
        self.assertIn("agentic-development framework",
                      (target / ".gitignore").read_text())
        self.assertTrue((target / ".agentic-installer-state.json").is_file())

    def test_reinstall_is_idempotent(self) -> None:
        target = self.make_target()
        main(install_args(target))
        before = sorted(p.name for p in (target / ".agent" / "skills").iterdir())
        self.assertEqual(main(install_args(target)), 0)  # second run
        after = sorted(p.name for p in (target / ".agent" / "skills").iterdir())
        self.assertEqual(before, after)
        self.assertTrue((target / ".agentic-development").is_symlink())

    def test_dry_run_makes_no_changes(self) -> None:
        target = self.make_target()
        self.assertEqual(main(install_args(target, dry_run=True)), 0)
        self.assertFalse((target / ".agentic-development").exists())
        self.assertFalse((target / ".agent").exists())
        self.assertFalse((target / ".agentic-installer-state.json").exists())

    def test_install_preserves_user_claude_md(self) -> None:
        target = self.make_target()
        (target / "CLAUDE.md").write_text("# MY memory\n", encoding="utf-8")
        main(install_args(target))
        self.assertEqual((target / "CLAUDE.md").read_text(), "# MY memory\n")

    def test_target_is_framework_rejected(self) -> None:
        # Installing into the framework itself must fail (exit code 3).
        self.assertEqual(main(install_args(FRAMEWORK_ROOT)), 3)


class TestCodexGitRoot(InstallerTestCase):
    """FR-14: Codex requires the target to be a git repository root."""

    def test_codex_rejects_non_git_target(self) -> None:
        target = self.make_target(git=False)
        self.assertEqual(main(install_args(target, vendor="codex")), 3)

    def test_codex_force_overrides_git_requirement(self) -> None:
        target = self.make_target(git=False)
        self.assertEqual(
            main(install_args(target, vendor="codex", force=True)), 0)
        self.assertTrue((target / ".agentic-development").is_symlink())


# ==========================================================================
# Task 063-11 — integration scenarios from the approved plan's verification
# recipe. (Scenarios already covered by TestInstallSymlinkMode and
# test_subcommands.py are not duplicated here.)
# ==========================================================================

class TestInstallCopyMode(InstallerTestCase):
    """Scenario 2 — fresh install in copy mode."""

    def test_copy_mode_produces_real_directory(self) -> None:
        target = self.make_target()
        self.assertEqual(main(install_args(target, mode="copy")), 0)
        agentic = target / ".agentic-development"
        self.assertTrue(agentic.is_dir())
        self.assertFalse(agentic.is_symlink())
        # The ignore-list kept VCS / cache cruft out of the copy.
        self.assertFalse((agentic / ".git").exists())
        # Per-item symlinks inside the target still exist and resolve into
        # the local copy.
        skills = target / ".agent" / "skills"
        linked = [p for p in skills.iterdir() if p.is_symlink()]
        self.assertTrue(linked)
        self.assertTrue(linked[0].resolve().is_relative_to(agentic.resolve()))

    def test_copy_mode_populates_symlink_sourced_component(self) -> None:
        # .claude/skills is a SYMLINK in the framework (-> ../.agent/skills).
        # Copy mode must still populate it — copytree(symlinks=True) preserves
        # the framework's internal relative symlinks self-consistently.
        target = self.make_target()
        self.assertEqual(main(install_args(target, mode="copy")), 0)
        claude_skills = target / ".claude" / "skills"
        self.assertTrue(claude_skills.is_dir())
        linked = [p for p in claude_skills.iterdir() if p.is_symlink()]
        self.assertTrue(linked, ".claude/skills must be populated in copy mode")


class TestConflictPrevention(InstallerTestCase):
    """Scenario 3 — install over a non-empty project preserves user content."""

    def test_user_content_preserved(self) -> None:
        target = self.make_target()
        (target / "System" / "my-code").mkdir(parents=True)
        (target / "System" / "my-code" / "x.py").write_text("user", encoding="utf-8")
        (target / "CLAUDE.md").write_text("# USER memory\n", encoding="utf-8")
        my_skill = target / ".claude" / "skills" / "my-skill"
        my_skill.mkdir(parents=True)
        (my_skill / "SKILL.md").write_text("user skill", encoding="utf-8")
        settings = target / ".claude" / "settings.json"
        settings.write_text('{"mine": true}', encoding="utf-8")

        self.assertEqual(main(install_args(target)), 0)

        # Don't-overwrite files are byte-preserved.
        self.assertEqual((target / "CLAUDE.md").read_text(), "# USER memory\n")
        self.assertEqual(settings.read_text(), '{"mine": true}')
        # System/ stays user-owned (not replaced by a symlink).
        self.assertFalse((target / "System").is_symlink())
        self.assertTrue((target / "System" / "my-code" / "x.py").exists())
        # The skipped System/ is recorded in state.
        import json
        state = json.loads((target / ".agentic-installer-state.json").read_text())
        self.assertIn("System", state["skipped_components"])
        # The project-local skill is preserved and git-tracked via a ! rule.
        self.assertTrue((my_skill / "SKILL.md").exists())
        self.assertIn("!/.claude/skills/my-skill",
                      (target / ".gitignore").read_text())


class TestForceSystemLink(InstallerTestCase):
    """Scenario 4 — --force-system-link replaces a user-owned System/."""

    def test_force_system_link(self) -> None:
        target = self.make_target()
        (target / "System" / "my-code").mkdir(parents=True)
        (target / "System" / "my-code" / "x.py").write_text("user", encoding="utf-8")
        self.assertEqual(
            main(install_args(target, force_system_link=True)), 0)
        self.assertTrue((target / "System").is_symlink())
        backups = list((target / ".agent" / "backups").iterdir())
        self.assertTrue(any((b / "System").exists() for b in backups))


class TestSwitchChain(InstallerTestCase):
    """Scenario 7 — switch antigravity -> codex."""

    def test_switch_antigravity_to_codex(self) -> None:
        target = self.make_target()  # git-init'd — Codex needs a git root
        main(install_args(target, vendor="antigravity"))
        self.assertEqual(main(switch_args(target, vendor="codex")), 0)
        # Codex's bootstrap file is AGENTS.md (antigravity used GEMINI.md only).
        self.assertTrue((target / "AGENTS.md").is_file())
        # Codex-specific artifacts are in place.
        self.assertTrue((target / ".agents" / "skills").is_symlink())
        self.assertTrue((target / ".codex").is_dir())


class TestAntiClobber(InstallerTestCase):
    """Scenario 8 — a hand-edited .gitignore block aborts; --force restores."""

    def test_tampered_gitignore_aborts_then_force_restores(self) -> None:
        target = self.make_target()
        main(install_args(target))
        gitignore = target / ".gitignore"
        gitignore.write_text(
            gitignore.read_text().replace("/System", "/System\n/tampered"),
            encoding="utf-8")
        # Re-install must abort with IntegrityError (exit 4); file untouched.
        self.assertEqual(main(install_args(target)), 4)
        self.assertIn("/tampered", gitignore.read_text())
        # --force overwrites and saves the user version to a backup.
        self.assertEqual(main(install_args(target, force=True)), 0)
        self.assertNotIn("/tampered", gitignore.read_text())
        edits = list((target / ".agent" / "backups").rglob("*.user-edits.txt"))
        self.assertTrue(edits)
