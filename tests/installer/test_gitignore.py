"""Unit tests for installer.gitignore — managed block + !-exception scanner.

Task 063-08. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

import io
import os
from contextlib import redirect_stdout
from pathlib import Path

from _base import FRAMEWORK_ROOT, InstallerTestCase
from installer.errors import IntegrityError
from installer.gitignore import (
    build_block_body,
    scan_local_exceptions,
    update_gitignore,
)
from installer.managed_block import GITIGNORE_MARKERS, extract_block
from installer.vendors import load_vendors, resolve_profile

_VENDORS = load_vendors(FRAMEWORK_ROOT / "System" / "scripts" / "vendors.yaml")
_CLAUDE = resolve_profile(_VENDORS, "claude")
_CODEX = resolve_profile(_VENDORS, "codex")


class TestBuildBlockBody(InstallerTestCase):

    def test_body_has_framework_and_state(self) -> None:
        body = build_block_body(_CLAUDE, [])
        # Exact-line membership, not assertIn on the raw text: a substring check
        # passes just as happily against "/.agentic-development/" and so cannot
        # tell the two apart. See test_framework_rule_has_no_trailing_slash.
        self.assertIn("/.agentic-development", body.splitlines())
        self.assertIn("/.agentic-installer-state.json", body.splitlines())

    def test_framework_rule_has_no_trailing_slash(self) -> None:
        # Regression: a `dir/` pattern matches directories only, and git does not
        # follow symlinks. In the default symlink mode `.agentic-development` is a
        # symlink, so a trailing slash left it visible to `git status`.
        body = build_block_body(_CLAUDE, [])
        self.assertNotIn("/.agentic-development/", body.splitlines())

    def test_per_item_dirs_ignore_contents(self) -> None:
        body = build_block_body(_CLAUDE, [])
        self.assertIn("/.agent/skills/*", body)
        self.assertIn("/.claude/skills/*", body)

    def test_claude_bridge_files_ignored(self) -> None:
        body = build_block_body(_CLAUDE, [])
        self.assertIn("/CLAUDE.agentic.md", body)
        self.assertIn("/CLAUDE.local.md", body)

    def test_codex_config_dir_stays_trackable(self) -> None:
        # .codex is a mkdir component outside .agent/ — must NOT be ignored.
        body = build_block_body(_CODEX, [])
        self.assertNotIn("/.codex\n", body + "\n")
        # but .agent/sessions (mkdir under .agent/) IS ignored.
        self.assertIn("/.agent/sessions", body)

    def test_feedback_machine_state_ignored(self) -> None:
        # run-feedback machine state (.agent/feedback: inbox/journal/locks/
        # heal-state) is a mkdir component under .agent/ — must be ignored so
        # downstream projects never commit it (QUALITY_FEEDBACK_LOOP §setup).
        body = build_block_body(_CLAUDE, [])
        self.assertIn("/.agent/feedback", body)

    def test_exceptions_appended(self) -> None:
        body = build_block_body(_CLAUDE, ["!/.agent/skills/mine"])
        self.assertIn("!/.agent/skills/mine", body)


class TestScanLocalExceptions(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.target = self.tmp / "project"
        # framework content the symlinks point into.
        agentic = self.target / ".agentic-development" / ".agent" / "skills"
        (agentic / "fw-skill").mkdir(parents=True)
        self.skills = self.target / ".agent" / "skills"
        self.skills.mkdir(parents=True)

    def _framework_symlink(self, name: str, dest_rel: str) -> None:
        os.symlink(dest_rel, self.skills / name)

    def test_framework_symlinks_not_exceptions(self) -> None:
        self._framework_symlink("fw-skill",
                                "../../.agentic-development/.agent/skills/fw-skill")
        result = scan_local_exceptions(self.target)
        self.assertEqual(result, [])

    def test_user_directory_is_exception(self) -> None:
        (self.skills / "my-skill").mkdir()
        self._framework_symlink("fw-skill",
                                "../../.agentic-development/.agent/skills/fw-skill")
        result = scan_local_exceptions(self.target)
        self.assertEqual(result, ["!/.agent/skills/my-skill"])

    def test_dotfiles_skipped(self) -> None:
        (self.skills / ".DS_Store").write_text("junk", encoding="utf-8")
        self.assertEqual(scan_local_exceptions(self.target), [])

    def test_broken_framework_symlink_warned_not_added(self) -> None:
        self._framework_symlink("gone",
                                "../../.agentic-development/.agent/skills/gone")
        result = scan_local_exceptions(self.target)
        self.assertEqual(result, [])  # broken framework link is not an exception

    # -- symlinks leaving the project ------------------------------------
    # A `!` on one of these invites `git add -A` to commit a path that exists on
    # the author's machine only. Measured on a real project: one `update` added
    # 15 such lines for skills symlinked out of ~/ExternalTools.

    def _outbound_symlink(self, name: str) -> Path:
        """Symlink ``name`` at a real directory outside the target project."""
        outside = self.tmp / "outside" / name
        outside.mkdir(parents=True)
        os.symlink(outside, self.skills / name)
        return outside

    def test_outbound_symlink_not_exception(self) -> None:
        self._outbound_symlink("external-skill")
        self.assertEqual(scan_local_exceptions(self.target), [])

    def test_outbound_symlink_warned(self) -> None:
        self._outbound_symlink("external-skill")
        with redirect_stdout(io.StringIO()) as out:
            scan_local_exceptions(self.target)
        self.assertIn("external-skill", out.getvalue())
        self.assertIn("resolves outside the project", out.getvalue())

    def test_inbound_symlink_is_exception(self) -> None:
        # `.claude/skills/x` -> `.agent/skills/x` is relative and in-repo, so a
        # clone resolves it; it stays trackable.
        (self.skills / "owned").mkdir()
        claude_skills = self.target / ".claude" / "skills"
        claude_skills.mkdir(parents=True)
        os.symlink("../../.agent/skills/owned", claude_skills / "owned")
        self.assertEqual(
            scan_local_exceptions(self.target),
            ["!/.agent/skills/owned", "!/.claude/skills/owned"],
        )

    def test_outbound_symlink_stays_out_across_repeated_updates(self) -> None:
        # The block is regenerated on every `update`, so a one-off correct run
        # proves nothing: the defect must not come back on the second pass.
        self._outbound_symlink("external-skill")
        state: dict = {}
        with redirect_stdout(io.StringIO()):
            state["gitignore_block_hash"] = update_gitignore(
                self.target, _CLAUDE, state)
            update_gitignore(self.target, _CLAUDE, state)
        body = extract_block(
            (self.target / ".gitignore").read_text(encoding="utf-8"),
            GITIGNORE_MARKERS)
        self.assertNotIn("external-skill", body)


class TestUpdateGitignore(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.target = self.tmp / "project"
        self.target.mkdir()
        self.state: dict = {}

    def test_creates_gitignore_with_single_block(self) -> None:
        update_gitignore(self.target, _CLAUDE, self.state)
        text = (self.target / ".gitignore").read_text()
        self.assertEqual(text.count(GITIGNORE_MARKERS[0]), 1)
        self.assertEqual(text.count(GITIGNORE_MARKERS[1]), 1)

    def test_preserves_existing_user_rules(self) -> None:
        gi = self.target / ".gitignore"
        gi.write_text("# user rules\n*.log\nbuild/\n", encoding="utf-8")
        update_gitignore(self.target, _CLAUDE, self.state)
        text = gi.read_text()
        self.assertIn("*.log", text)
        self.assertIn("build/", text)
        self.assertIn("/.agentic-development", text.splitlines())

    def test_idempotent_rerun(self) -> None:
        h1 = update_gitignore(self.target, _CLAUDE, self.state)
        self.state["gitignore_block_hash"] = h1
        h2 = update_gitignore(self.target, _CLAUDE, self.state)
        self.assertEqual(h1, h2)

    def test_manual_edit_aborts_without_force(self) -> None:
        h1 = update_gitignore(self.target, _CLAUDE, self.state)
        self.state["gitignore_block_hash"] = h1
        gi = self.target / ".gitignore"
        gi.write_text(gi.read_text().replace("/System", "/System\n/tampered"),
                      encoding="utf-8")
        with self.assertRaises(IntegrityError):
            update_gitignore(self.target, _CLAUDE, self.state)

    def test_manual_edit_force_restores(self) -> None:
        h1 = update_gitignore(self.target, _CLAUDE, self.state)
        self.state["gitignore_block_hash"] = h1
        gi = self.target / ".gitignore"
        gi.write_text(gi.read_text().replace("/System", "/System\n/tampered"),
                      encoding="utf-8")
        backup_dir = self.target / ".agent" / "backups" / "snap"
        update_gitignore(self.target, _CLAUDE, self.state,
                         force=True, backup_dir=backup_dir)
        self.assertNotIn("/tampered",
                         extract_block((gi).read_text(), GITIGNORE_MARKERS))
