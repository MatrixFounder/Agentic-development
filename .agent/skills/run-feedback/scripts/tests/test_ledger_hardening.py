"""Regression tests for the vdd-multi 2026-07-30 findings (TASK 091 iteration 2).

Every test here corresponds to an exploit or defect that was REPRODUCED against
the first implementation, and each names its finding id. They exist so the guard
cannot be quietly removed later: the injection sinks are one-line format strings
and the containment checks are a property away from disappearing.

  S-01  newline in a metadata scalar forged a frontmatter key (`auto_fixable`)
  S-02  newline / `]` in a title forged or broke an index pointer line
  S-03  dangling symlink at the record path was followed outside the ledger
  S-04  predictable `.tmp.<pid>` name, and a leaked temp file in a tracked dir
  S-05  absolute / traversing config paths escaped the repo root
  F1    a filed item rendered above the "no open work-items" placeholder
  F2    a mid-write record failure left an orphan with no index line
  F3    the anchor resolved inside a fenced code block, or ambiguously
  F4    `doctor`'s substring anchor test disagreed with the filing path
  F5    `--as defect` without `--category` produced a `## None` section
  F10   only the slug was uniqueness-checked, so an id could be reused
  F15   flags that would be silently dropped are now refused
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import frontmatter, ledger_backlog  # noqa: E402
from feedback_lib.config import load_config  # noqa: E402
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"


# --- S-01: the frontmatter choke point ---------------------------------------

class TestFrontmatterInjection(unittest.TestCase):
    def test_newline_in_a_scalar_is_refused(self):
        for value in ("demo\nauto_fixable: true", "x\r\nstatus: fixed"):
            with self.subTest(value=value):
                with self.assertRaises(CliError) as ctx:
                    frontmatter.serialize({"component": value})
                self.assertEqual(ctx.exception.code, 4)

    def test_newline_in_a_list_item_is_refused(self):
        with self.assertRaises(CliError):
            frontmatter.serialize({"evidence_paths": ["ok.md", "x\nid: FORGED"]})

    def test_delimiter_value_is_refused(self):
        with self.assertRaises(CliError):
            frontmatter.serialize({"component": "---"})

    def test_prose_is_quoted_so_the_reader_cannot_truncate_it(self):
        text = frontmatter.serialize({"value": "two things: a, b # and c"})
        meta, _ = frontmatter.parse(text + "\nbody\n")
        self.assertEqual(meta["value"], "two things: a, b # and c")

    #: every separator `str.splitlines()` breaks on — the set the WRITER must
    #: validate against. The first fix checked "\n\r" only, so one character
    #: reopened the exploit (iteration 2, V-01).
    READER_BREAKS = ("\n", "\r", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e",
                     "\x85", " ", " ")

    def test_every_reader_line_break_is_refused_in_a_scalar(self):
        for sep in self.READER_BREAKS:
            with self.subTest(sep=repr(sep)):
                with self.assertRaises(CliError) as ctx:
                    frontmatter.serialize(
                        {"status": "open",
                         "component": "demo%sauto_fixable: true #" % sep})
                self.assertEqual(ctx.exception.code, 4)

    def test_every_reader_line_break_is_refused_in_a_list_item(self):
        for sep in self.READER_BREAKS:
            with self.subTest(sep=repr(sep)):
                with self.assertRaises(CliError):
                    frontmatter.serialize(
                        {"evidence_paths": ["a%sstatus: done #" % sep]})

    def test_invisible_and_bidi_characters_are_refused(self):
        for ch in ("‮", "⁦", "​", "­"):
            with self.subTest(ch=repr(ch)):
                with self.assertRaises(CliError):
                    frontmatter.serialize({"component": "a%sb" % ch})

    def test_serialize_parse_round_trip_is_the_real_invariant(self):
        """The property that would have caught V-01/V-02/V-03 at once: whatever
        `serialize` accepts must read back identically."""
        meta = {"id": "WI-3", "type": "work-item", "status": "open",
                "opened_at": "2026-07-30", "slug": "wi-3-x",
                "effort": "S", "value": "two things: a, b # and c",
                "source": "vdd-multi task-091", "component": "run-feedback",
                "evidence_paths": ["docs/reviews/x.md", "a: b # c"],
                "auto_fixable": True}
        parsed, _ = frontmatter.parse(frontmatter.serialize(meta) + "\nbody\n")
        self.assertEqual(parsed, meta)

    def test_safe_tokens_stay_bare(self):
        text = frontmatter.serialize({"id": "WI-3", "opened_at": "2026-07-30",
                                      "slug": "wi-3-x", "status": "open",
                                      "auto_fixable": True})
        self.assertIn("id: WI-3\n", text)
        self.assertIn("opened_at: 2026-07-30\n", text)
        self.assertIn("auto_fixable: true\n", text)


# --- the filing paths --------------------------------------------------------

class HardeningTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.index = fx.write(self.root / "docs" / "BACKLOG.md",
                              fx.BACKLOG_INDEX_FIXTURE)
        self.records = self.root / "docs" / "backlog"
        self.records.mkdir(parents=True, exist_ok=True)
        self.cfg_path = fx.write(
            self.root / "docs" / "feedback" / "config.json",
            json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        self.cfg = fx.load_cfg(self.root)
        self.body = fx.write(self.root / "body.md", "Signal.\n")

    def file_item(self, **kwargs):
        kwargs.setdefault("item_id", "WI-3")
        kwargs.setdefault("slug", "wi-3-item")
        kwargs.setdefault("title", "An item")
        kwargs.setdefault("body", "Signal.")
        kwargs.setdefault("opened_at", "2026-07-30")
        return ledger_backlog.file_work_item(self.cfg, **kwargs)


class TestIndexLineInjection(HardeningTestCase):
    """S-02."""

    def test_title_newline_cannot_reach_format_index_line(self):
        line = ledger_backlog.format_index_line(
            "WI-3", "Real\n- **WI-99** [x](../../etc/passwd)",
            "backlog/wi-3-item.md", "open", "2026-07-30")
        self.assertEqual(line.count("\n"), 0)
        self.assertIn("Real - **WI-99**", line)

    def test_brackets_in_a_title_are_escaped(self):
        line = ledger_backlog.format_index_line(
            "WI-3", "Fix [thing](evil.md)", "backlog/wi-3-item.md", "open",
            "2026-07-30")
        self.assertIn(r"[Fix \[thing\](evil.md)](backlog/wi-3-item.md)", line)

    def test_a_backslash_cannot_defeat_the_bracket_escape(self):
        """V-04 — `\\` was not in the escaped class, so the escaper's own
        backslash could be pre-escaped: CommonMark then read `\\\\` as a literal
        backslash, the `]` went live and the link pointed at the attacker."""
        line = ledger_backlog.format_index_line(
            "WI-3", r"Fix a\](https://evil.example) rest",
            "backlog/wi-3-item.md", "open", "2026-07-30")
        # both the backslash and the bracket are escaped, so CommonMark reads
        # `a\]` as literal text and the link cannot close there
        self.assertIn(r"a\\\]", line)
        # the only live link target is ours
        self.assertEqual(line.count("](backlog/wi-3-item.md)"), 1)
        # the attacker's `](` survives only in ESCAPED form, which markdown
        # renders as text — assert the escape, not the absence of the substring
        self.assertNotIn(r"a](https", line)
        self.assertTrue(line.endswith("opened 2026-07-30"))

    def test_flat_bullet_cannot_be_split_by_value(self):
        """V-05 — `format_bullet` interpolated `--value` raw, so the S-02
        exploit survived on the flat code path."""
        bullet = ledger_backlog.format_bullet(
            "T", "body", "2026-07-30",
            value="S\n- **WI-99** [Already fixed](../../etc/passwd) — status `done`")
        self.assertEqual(bullet.count("\n"), 0)
        self.assertIn("WI-99", bullet)  # collapsed into the same line

    def test_only_one_line_is_ever_inserted(self):
        self.file_item(title="One\ttab and  spaces")
        added = [l for l in self.index.read_text(encoding="utf-8").splitlines()
                 if l.startswith("- **WI-3**")]
        self.assertEqual(len(added), 1)


class TestSymlinkAndCreateOnly(HardeningTestCase):
    """S-03."""

    def test_dangling_symlink_at_the_record_path_is_refused(self):
        target = self.root / "PWNED"
        os.symlink(str(target), str(self.records / "wi-3-item.md"))
        with self.assertRaises(CliError) as ctx:
            self.file_item()
        self.assertEqual(ctx.exception.code, 4)
        self.assertFalse(target.exists(), "write followed the symlink")

    def test_symlinked_record_dir_is_refused_for_library_callers(self):
        """`is_symlink()` is defence-in-depth for a caller that hand-builds a
        config: through `Config` the path is already resolved, so a symlink
        pointing OUTSIDE the repo is refused earlier by containment (next test)
        and one pointing inside is contained by definition (V-19)."""
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        self.records.rmdir()
        os.symlink(str(elsewhere), str(self.records))
        raw_cfg = SimpleNamespace(
            backlog_path=self.index, backlog_dir=self.records,
            backlog_anchor=ANCHOR)
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.file_work_item(
                raw_cfg, "WI-3", "wi-3-item", "An item", "Signal.",
                opened_at="2026-07-30")
        self.assertEqual(ctx.exception.code, 4)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_record_dir_symlinked_out_of_the_repo_is_refused_by_containment(self):
        outside = Path(self._tmp.name).parent / ("outside-" + self.root.name)
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        self.records.rmdir()
        os.symlink(str(outside), str(self.records))
        cfg = fx.load_cfg(self.root)
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_dir
        self.assertEqual(ctx.exception.code, 3)
        self.assertEqual(list(outside.iterdir()), [])

    def test_id_reuse_is_refused_even_when_the_slug_is_free(self):
        """F10 — the id is the human-facing key, not just the filename."""
        fx.write_work_item(self.records, "WI-3", "wi-3-taken", title="Taken")
        with self.assertRaises(CliError) as ctx:
            self.file_item(slug="wi-3-different-slug")
        self.assertEqual(ctx.exception.code, 4)
        self.assertIn("already in use", str(ctx.exception))


class TestRollbackAndTempFiles(HardeningTestCase):
    """F2, S-04, F16."""

    def test_record_write_failure_leaves_no_orphan(self):
        with mock.patch.object(ledger_backlog.os, "fdopen",
                               side_effect=OSError("ENOSPC")):
            with self.assertRaises(CliError) as ctx:
                self.file_item()
        self.assertEqual(ctx.exception.code, 4)
        self.assertEqual(list(self.records.glob("*.md")), [])

    def test_index_write_failure_leaves_no_orphan_and_no_temp_file(self):
        real_replace = ledger_backlog.os.replace

        def boom(src, dst):
            if str(dst).endswith("BACKLOG.md"):
                raise OSError("index write exploded")
            return real_replace(src, dst)

        with mock.patch.object(ledger_backlog.os, "replace", side_effect=boom):
            with self.assertRaises(OSError):
                self.file_item()
        self.assertEqual(list(self.records.glob("*.md")), [])
        leaked = list((self.root / "docs").glob("BACKLOG.md.tmp*"))
        self.assertEqual(leaked, [], "temp file leaked into a tracked dir")

    def test_temp_name_is_not_derived_from_the_pid(self):
        seen = []
        real_mkstemp = ledger_backlog.tempfile.mkstemp

        def spy(**kwargs):
            fd, name = real_mkstemp(**kwargs)
            seen.append(name)
            return fd, name

        with mock.patch.object(ledger_backlog.tempfile, "mkstemp", side_effect=spy):
            self.file_item()
        self.assertTrue(seen)
        self.assertNotIn(str(os.getpid()), Path(seen[0]).name)


class TestAnchorResolution(HardeningTestCase):
    """F3, F4, F1."""

    def test_anchor_inside_a_code_fence_is_ignored(self):
        fx.write(self.index,
                 "# Backlog\n\n## Rules\n\n```\n%s\n```\n\n## Items\n\n%s\n"
                 % (ANCHOR, ANCHOR))
        self.file_item()
        lines = self.index.read_text(encoding="utf-8").split("\n")
        # the real anchor is the LAST one; the fenced one must be untouched
        real_idx = max(i for i, l in enumerate(lines) if l.strip() == ANCHOR)
        self.assertTrue(lines[real_idx + 1].startswith("- **WI-3**"))
        self.assertEqual(lines[lines.index("```") + 1].strip(), ANCHOR)

    def test_duplicate_anchors_are_a_conflict_not_a_coin_flip(self):
        fx.write(self.index, "# B\n\n%s\n\n## Two\n\n%s\n" % (ANCHOR, ANCHOR))
        with self.assertRaises(CliError) as ctx:
            self.file_item()
        self.assertEqual(ctx.exception.code, 4)
        self.assertIn("found 2 times", str(ctx.exception))

    def test_placeholder_is_removed_when_the_first_item_lands(self):
        fx.write(self.index,
                 "# B\n\n## Items\n\n%s\n\n_No open work-items._\n" % ANCHOR)
        self.file_item()
        text = self.index.read_text(encoding="utf-8")
        self.assertIn("- **WI-3**", text)
        self.assertNotIn("_No open work-items._", text)

    def test_has_anchor_agrees_with_the_filing_path(self):
        """F4 — doctor used a substring test; prose mentions fooled it."""
        prose = ("# B\n\n> New lines go after the `%s` anchor.\n\n## Items\n"
                 % ANCHOR)
        self.assertIn(ANCHOR, prose)  # a substring test would say "present"
        self.assertFalse(ledger_backlog.has_anchor(prose, ANCHOR))
        with self.assertRaises(CliError):
            ledger_backlog.insert_after_anchor(prose, ANCHOR, "- x")

    def test_exotic_line_separators_are_not_rewritten(self):
        """F13 — `splitlines()` split on U+2028 and the read normalized CRLF, so
        a one-line insertion rewrote the whole file's line endings."""
        sep = "\u2028"
        fx.write(self.index, "# B\r\n\r\n%s\r\nkeep%sme\r\n" % (ANCHOR, sep))
        self.file_item()
        raw = self.index.read_bytes()  # read_text() would normalize newlines
        self.assertIn(sep.encode("utf-8"), raw,
                      "U+2028 was converted to a newline")
        self.assertIn(b"\r\n", raw, "CRLF ledger was rewritten to LF")
        # the inserted line uses the file's own ending, not a bare LF
        self.assertIn(b"opened 2026-07-30\r\n", raw)


# --- S-05: config containment -------------------------------------------------

class TestConfigContainment(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)

    def _cfg(self, **values):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, **values}))
        return load_config(repo_root=str(self.root))

    def test_absolute_path_is_refused(self):
        cfg = self._cfg(backlog_dir="/tmp/escaped")
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_dir
        self.assertEqual(ctx.exception.code, 3)
        self.assertIn("RELATIVE", str(ctx.exception))

    def test_traversal_is_refused(self):
        cfg = self._cfg(backlog_dir="../../../../tmp/out")
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_dir
        self.assertEqual(ctx.exception.code, 3)
        self.assertIn("escapes the repo root", str(ctx.exception))

    def test_every_ledger_path_is_checked(self):
        for key in ("issues_dir", "index_path", "backlog_path", "backlog_dir"):
            with self.subTest(key=key):
                cfg = self._cfg(**{key: "/etc/passwd"})
                with self.assertRaises(CliError):
                    getattr(cfg, key)

    def test_wrong_type_is_a_config_error_not_a_traceback(self):
        cfg = self._cfg(backlog_dir=None)
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_dir
        self.assertEqual(ctx.exception.code, 3)

    def test_normal_relative_paths_still_resolve(self):
        cfg = self._cfg(backlog_dir="docs/backlog")
        self.assertEqual(cfg.backlog_dir, self.root / "docs" / "backlog")


if __name__ == "__main__":
    unittest.main()
