"""Unit tests for installer.managed_block — the anti-clobber engine.

Task 063-06. This module is safety-critical (NFR-2, no silent clobber), so the
suite is deliberately exhaustive. Run:
``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

from _base import InstallerTestCase
from installer.errors import IntegrityError
from installer.managed_block import (
    GITIGNORE_MARKERS,
    MARKDOWN_MARKERS,
    block_hash,
    extract_block,
    inject_block,
    strip_block,
)

_BODY = "/.agentic-development/\n/System"


class TestBlockHash(InstallerTestCase):

    def test_hash_prefixed_and_deterministic(self) -> None:
        self.assertTrue(block_hash("x").startswith("sha256:"))
        self.assertEqual(block_hash("abc"), block_hash("abc"))

    def test_hash_distinguishes_content(self) -> None:
        self.assertNotEqual(block_hash("abc"), block_hash("abd"))


class TestInjectCreate(InstallerTestCase):

    def test_inject_into_absent_file_creates_block(self) -> None:
        f = self.tmp / ".gitignore"
        returned = inject_block(f, _BODY, GITIGNORE_MARKERS)
        self.assertTrue(f.exists())
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS), _BODY)
        self.assertEqual(returned, block_hash(_BODY))

    def test_inject_appends_preserving_user_content(self) -> None:
        f = self.tmp / ".gitignore"
        f.write_text("# my project\n*.log\n", encoding="utf-8")
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        text = f.read_text()
        self.assertIn("# my project", text)
        self.assertIn("*.log", text)
        self.assertEqual(extract_block(text, GITIGNORE_MARKERS), _BODY)

    def test_round_trip(self) -> None:
        f = self.tmp / "AGENTS.md"
        body = "line one\nline two\nline three"
        inject_block(f, body, MARKDOWN_MARKERS)
        self.assertEqual(extract_block(f.read_text(), MARKDOWN_MARKERS), body)

    def test_inject_into_empty_existing_file(self) -> None:
        f = self.tmp / ".gitignore"
        f.write_text("", encoding="utf-8")  # exists but empty
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS), _BODY)


class TestInjectRewrite(InstallerTestCase):

    def test_rewrite_with_matching_hash(self) -> None:
        f = self.tmp / ".gitignore"
        h1 = inject_block(f, _BODY, GITIGNORE_MARKERS)
        new_body = _BODY + "\n/.agentic-installer-state.json"
        h2 = inject_block(f, new_body, GITIGNORE_MARKERS, state_hash=h1)
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS), new_body)
        self.assertEqual(h2, block_hash(new_body))

    def test_first_run_none_hash_rewrites_existing(self) -> None:
        f = self.tmp / ".gitignore"
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        # state_hash=None (lost state) → adopt/overwrite the existing block.
        inject_block(f, "/.agentic-development/", GITIGNORE_MARKERS, state_hash=None)
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS),
                         "/.agentic-development/")

    def test_hash_mismatch_aborts_without_force(self) -> None:
        f = self.tmp / ".gitignore"
        h1 = inject_block(f, _BODY, GITIGNORE_MARKERS)
        # Simulate a hand-edit inside the block.
        tampered = f.read_text().replace("/System", "/System\n/secrets")
        f.write_text(tampered, encoding="utf-8")
        with self.assertRaises(IntegrityError) as ctx:
            inject_block(f, "/new", GITIGNORE_MARKERS, state_hash=h1)
        self.assertIn("--force", str(ctx.exception))
        # The file must be left untouched.
        self.assertEqual(f.read_text(), tampered)

    def test_rejects_marker_line_in_body(self) -> None:
        # A block body containing a marker line would create a premature
        # boundary — inject_block must refuse it.
        f = self.tmp / ".gitignore"
        evil = f"safe line\n{GITIGNORE_MARKERS[1]}\nmore content"
        with self.assertRaises(IntegrityError):
            inject_block(f, evil, GITIGNORE_MARKERS)

    def test_hash_mismatch_force_overwrites_and_backs_up(self) -> None:
        f = self.tmp / ".gitignore"
        h1 = inject_block(f, _BODY, GITIGNORE_MARKERS)
        tampered = f.read_text().replace("/System", "/System\n/secrets")
        f.write_text(tampered, encoding="utf-8")
        backup_dir = self.tmp / "backups"
        inject_block(f, "/new-body", GITIGNORE_MARKERS, state_hash=h1,
                     force=True, backup_dir=backup_dir)
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS), "/new-body")
        saved = backup_dir / ".gitignore.user-edits.txt"
        self.assertTrue(saved.is_file())
        self.assertIn("/secrets", saved.read_text())


class TestExtractBlock(InstallerTestCase):

    def test_extract_none_when_no_marker(self) -> None:
        self.assertIsNone(extract_block("just some text\n", GITIGNORE_MARKERS))

    def test_extract_exact_content(self) -> None:
        f = self.tmp / ".gitignore"
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        self.assertEqual(extract_block(f.read_text(), GITIGNORE_MARKERS), _BODY)


class TestStripBlock(InstallerTestCase):

    def test_strip_removes_block_keeps_surrounding(self) -> None:
        f = self.tmp / ".gitignore"
        f.write_text("# my project\n*.log\n", encoding="utf-8")
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        strip_block(f, GITIGNORE_MARKERS)
        text = f.read_text()
        self.assertIn("# my project", text)
        self.assertIn("*.log", text)
        self.assertIsNone(extract_block(text, GITIGNORE_MARKERS))
        self.assertNotIn("agentic-development", text)

    def test_strip_absent_file_is_noop(self) -> None:
        strip_block(self.tmp / "nope.gitignore", GITIGNORE_MARKERS)  # must not raise

    def test_strip_no_block_is_noop(self) -> None:
        f = self.tmp / ".gitignore"
        f.write_text("*.log\n", encoding="utf-8")
        strip_block(f, GITIGNORE_MARKERS)
        self.assertEqual(f.read_text(), "*.log\n")

    def test_strip_block_only_file_becomes_empty(self) -> None:
        f = self.tmp / ".gitignore"
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        strip_block(f, GITIGNORE_MARKERS)
        self.assertEqual(f.read_text(), "")

    def test_strip_keeps_content_after_block(self) -> None:
        f = self.tmp / ".gitignore"
        inject_block(f, _BODY, GITIGNORE_MARKERS)
        # Append user content AFTER the managed block.
        f.write_text(f.read_text() + "\n# trailing user note\n*.tmp\n", encoding="utf-8")
        strip_block(f, GITIGNORE_MARKERS)
        text = f.read_text()
        self.assertIn("# trailing user note", text)
        self.assertIn("*.tmp", text)
        self.assertNotIn("agentic-development", text)
