"""Unit tests for installer.bootstrap — vendor-aware bootstrap strategies.

Task 063-07. Run: ``python3 -m unittest discover -s tests/installer -v``
"""
from __future__ import annotations

from _base import InstallerTestCase
from installer.bootstrap import apply_bootstrap, is_protected
from installer.errors import ConfigurationError
from installer.managed_block import MARKDOWN_MARKERS, extract_block

# Real vendor profiles (mirrors System/scripts/vendors.yaml).
_CLAUDE = {"bootstrap_strategy": "at_import", "bootstrap_file": "CLAUDE.md",
           "bootstrap_aliases": [], "bootstrap_source": None}
_ANTIGRAVITY = {"bootstrap_strategy": "marker_block", "bootstrap_file": "GEMINI.md",
                "bootstrap_aliases": [], "bootstrap_source": "GEMINI.md"}
_CURSOR = {"bootstrap_strategy": "marker_block", "bootstrap_file": "AGENTS.md",
           "bootstrap_aliases": [], "bootstrap_source": "AGENTS.md"}
# Synthetic profiles exercising code paths no shipped vendor currently uses.
_ALIASED = {"bootstrap_strategy": "marker_block", "bootstrap_file": "GEMINI.md",
            "bootstrap_aliases": ["AGENTS.md"], "bootstrap_source": "AGENTS.md"}
_NONE = {"bootstrap_strategy": "none", "bootstrap_file": None,
         "bootstrap_aliases": [], "bootstrap_source": None}


class BootstrapTestBase(InstallerTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.target = self.tmp / "project"
        self.target.mkdir()
        # framework == the target's .agentic-development directory.
        self.framework = self.target / ".agentic-development"
        self.framework.mkdir()
        (self.framework / "CLAUDE.md").write_text("# framework claude rules\n", encoding="utf-8")
        (self.framework / "AGENTS.md").write_text("# framework agents rules\n", encoding="utf-8")
        (self.framework / "GEMINI.md").write_text("# framework gemini rules\n", encoding="utf-8")
        self.state: dict = {"bootstrap_blocks_hash": {}}


class TestAtImport(BootstrapTestBase):

    def test_clean_target_builds_three_files(self) -> None:
        result = apply_bootstrap(self.target, self.framework, _CLAUDE, self.state)
        self.assertTrue((self.target / "CLAUDE.md").is_file())
        local = self.target / "CLAUDE.local.md"
        self.assertIn("@CLAUDE.agentic.md", local.read_text())
        agentic = self.target / "CLAUDE.agentic.md"
        self.assertTrue(agentic.is_symlink())
        self.assertEqual(agentic.resolve(), (self.framework / "CLAUDE.md").resolve())
        self.assertIn("CLAUDE.md", result["created"])

    def test_existing_claude_md_not_overwritten(self) -> None:
        (self.target / "CLAUDE.md").write_text("# MY project memory\n", encoding="utf-8")
        apply_bootstrap(self.target, self.framework, _CLAUDE, self.state)
        self.assertEqual((self.target / "CLAUDE.md").read_text(), "# MY project memory\n")

    def test_existing_local_md_user_content_preserved(self) -> None:
        local = self.target / "CLAUDE.local.md"
        local.write_text("# my private notes\nsome notes here\n", encoding="utf-8")
        apply_bootstrap(self.target, self.framework, _CLAUDE, self.state)
        text = local.read_text()
        self.assertIn("my private notes", text)
        self.assertIn("@CLAUDE.agentic.md", text)

    def test_idempotent_rerun(self) -> None:
        apply_bootstrap(self.target, self.framework, _CLAUDE, self.state)
        apply_bootstrap(self.target, self.framework, _CLAUDE, self.state)  # no raise
        self.assertTrue((self.target / "CLAUDE.agentic.md").is_symlink())


class TestMarkerBlock(BootstrapTestBase):

    def test_antigravity_injects_into_gemini_only(self) -> None:
        result = apply_bootstrap(self.target, self.framework, _ANTIGRAVITY, self.state)
        gemini = self.target / "GEMINI.md"
        self.assertTrue(gemini.is_file())
        block = extract_block(gemini.read_text(), MARKDOWN_MARKERS)
        self.assertIn("framework gemini rules", block)
        # Antigravity uses GEMINI.md ONLY — no AGENTS.md, no Claude bridge files.
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / "CLAUDE.local.md").exists())
        self.assertFalse((self.target / "CLAUDE.agentic.md").exists())
        self.assertEqual(set(result["blocks"]), {"GEMINI.md"})

    def test_cursor_injects_into_agents_md(self) -> None:
        result = apply_bootstrap(self.target, self.framework, _CURSOR, self.state)
        agents = self.target / "AGENTS.md"
        self.assertTrue(agents.is_file())
        block = extract_block(agents.read_text(), MARKDOWN_MARKERS)
        self.assertIn("framework agents rules", block)
        self.assertFalse((self.target / "GEMINI.md").exists())
        self.assertEqual(set(result["blocks"]), {"AGENTS.md"})

    def test_existing_agents_md_preserved(self) -> None:
        agents = self.target / "AGENTS.md"
        agents.write_text("# user's own AGENTS\nrule one\n", encoding="utf-8")
        apply_bootstrap(self.target, self.framework, _CURSOR, self.state)
        text = agents.read_text()
        self.assertIn("user's own AGENTS", text)
        self.assertIn("framework agents rules", text)

    def test_aliases_inject_into_every_file(self) -> None:
        # bootstrap_aliases — a profile may target several bootstrap files.
        result = apply_bootstrap(self.target, self.framework, _ALIASED, self.state)
        for name in ("GEMINI.md", "AGENTS.md"):
            block = extract_block((self.target / name).read_text(), MARKDOWN_MARKERS)
            self.assertIsNotNone(block)
        self.assertEqual(set(result["blocks"]), {"GEMINI.md", "AGENTS.md"})

    def test_idempotent_rerun(self) -> None:
        apply_bootstrap(self.target, self.framework, _ANTIGRAVITY, self.state)
        first = (self.target / "GEMINI.md").read_text()
        apply_bootstrap(self.target, self.framework, _ANTIGRAVITY, self.state)
        self.assertEqual((self.target / "GEMINI.md").read_text(), first)

    def test_missing_bootstrap_source_rejected(self) -> None:
        bad = dict(_ANTIGRAVITY, bootstrap_source="NONEXISTENT.md")
        with self.assertRaises(ConfigurationError):
            apply_bootstrap(self.target, self.framework, bad, self.state)


class TestNoneStrategy(BootstrapTestBase):

    def test_none_strategy_creates_nothing(self) -> None:
        result = apply_bootstrap(self.target, self.framework, _NONE, self.state)
        self.assertEqual(result["created"], [])
        self.assertEqual(result["blocks"], {})
        self.assertEqual(list(self.target.iterdir()), [self.framework])


class TestIsProtected(InstallerTestCase):

    def test_protected_names(self) -> None:
        for name in ("CLAUDE.md", "AGENTS.md", "GEMINI.md"):
            self.assertTrue(is_protected(name))

    def test_protected_with_path_prefix(self) -> None:
        self.assertTrue(is_protected("some/dir/AGENTS.md"))

    def test_unprotected_names(self) -> None:
        for name in ("README.md", "CLAUDE.local.md", "settings.json"):
            self.assertFalse(is_protected(name))
