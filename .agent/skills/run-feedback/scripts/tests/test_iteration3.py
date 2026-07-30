"""Regression tests for vdd-multi iteration 3 (TASK 093 review).

Iteration 3 reviewed the fixes that closed WI-2…WI-7 and found that **the task's
own organizing lesson had not been applied to itself**: five of the confirmed
findings were further instances of "a fix that landed on one of two symmetric
paths," on the very code that was supposed to close that class.

  L-1  the CRLF fix was re-broken in `insert_index_line`'s new-category branch —
       the branch the FIRST defect ever filed into a fresh index always takes
  L-2  `ledger_issues.insert_index_line` had NO fence awareness, so a pointer
       line could be written inside a documented code example (F3, one registry
       over, a whole task later)
  L-3  the test asserting "both ledgers share the read primitive" was vacuous in
       both of its assertions (fixed in test_wi_tail.py, mutation-verified)
  L-4  `file_defect` rolled back only on `OSError` while `file_work_item` used
       `BaseException` (V1, unapplied on the twin)
  L-5  the WI-2 body gate sat at the CLI, so NEITHER writer enforced it
  L-6  `file_defect` had no id-uniqueness guard at all (F10, unapplied on the twin)
  L-8  a ≥4-space-indented anchor counted as live, so `doctor` could report
       `ready: true` for an anchor that renders inside an indented code block
  L-15 `_rejoin` collapsed a human's trailing blank lines on every insertion

The structural answer — and the reason `feedback_lib/markdown.py` exists — is that
the fence state machine and the id guard are now **one implementation each**,
consumed by both ledgers. Tests that cover a shared guard are parameterized over
both registries here, so "fixed on one path only" cannot pass again.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import (body as body_mod, ids as ids_mod,  # noqa: E402
                          ledger_backlog, ledger_issues, markdown)
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"


class LedgerCase(unittest.TestCase):
    """A repo with both ledgers seeded, so either writer can be exercised."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.backlog = fx.write(self.root / "docs" / "BACKLOG.md",
                                fx.BACKLOG_INDEX_FIXTURE)
        self.index = fx.write(self.root / "docs" / "KNOWN_ISSUES.md",
                              fx.INDEX_FIXTURE)
        self.records = self.root / "docs" / "backlog"
        self.records.mkdir(parents=True, exist_ok=True)
        self.issues = self.root / "docs" / "issues"
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        self.cfg = fx.load_cfg(self.root)

    def file_work_item(self, **kw):
        kw.setdefault("item_id", "WI-9")
        kw.setdefault("slug", "wi-9-item")
        kw.setdefault("title", "An item")
        kw.setdefault("body", "Signal.")
        kw.setdefault("opened_at", "2026-07-30")
        return ledger_backlog.file_work_item(self.cfg, **kw)

    def file_defect(self, **kw):
        kw.setdefault("issue_id", "RF-9")
        kw.setdefault("slug", "rf-9-issue")
        kw.setdefault("title", "An issue")
        kw.setdefault("category", "robustness")
        kw.setdefault("body", "Signal.")
        kw.setdefault("opened_at", "2026-07-30")
        return ledger_issues.file_defect(self.cfg, **kw)


# --- L-1 / L-15: newline and trailing-shape fidelity -------------------------

class TestIndexInsertionFidelity(unittest.TestCase):
    """L-1, L-15 — direct unit tests on `insert_index_line`.

    Iteration 3 noted there were NO direct tests for this function, `_eol_of` or
    `_rejoin`: all coverage went through `file_defect` on two well-formed
    fixtures, which is why the new-category branch could be broken and green.
    """

    LINE = "- **RF-9** [y](issues/y.md) — status `open`, opened 2026-07-30"

    def _crlf(self, text):
        return text.replace("\n", "\r\n")

    def test_new_category_in_a_crlf_index_stays_crlf(self):
        """L-1: `insert_at == len(lines)` sampled the empty tail element, so this
        branch always concluded LF. A freshly seeded index has no category
        sections, so the FIRST defect ever filed takes exactly this path."""
        text = self._crlf("# Known Issues\n\n## correctness\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01\n")
        out = ledger_issues.insert_index_line(text, "zzz", self.LINE).encode()
        self.assertEqual(out.count(b"\r\n"), out.count(b"\n"),
                         "bare LF introduced into a CRLF ledger: %d CRLF vs %d LF"
                         % (out.count(b"\r\n"), out.count(b"\n")))

    def test_new_category_before_an_existing_one_stays_crlf(self):
        text = self._crlf("# K\n\n## zzz\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01\n")
        out = ledger_issues.insert_index_line(text, "aaa", self.LINE).encode()
        self.assertEqual(out.count(b"\r\n"), out.count(b"\n"))

    def test_existing_category_in_a_crlf_index_stays_crlf(self):
        text = self._crlf("# K\n\n## logic\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01\n")
        out = ledger_issues.insert_index_line(text, "logic", self.LINE).encode()
        self.assertEqual(out.count(b"\r\n"), out.count(b"\n"))

    def test_trailing_blank_lines_a_human_left_are_preserved(self):
        """L-15: `rstrip("\\r\\n") + eol` collapsed them, turning a one-line
        insertion into a multi-line diff in a hand-maintained file."""
        text = "# K\n\n## logic\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01\n\n\n"
        out = ledger_issues.insert_index_line(text, "logic", self.LINE)
        self.assertTrue(out.endswith("\n\n\n"), repr(out[-8:]))

    def test_a_file_with_no_trailing_newline_gains_exactly_one(self):
        text = "# K\n\n## logic\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01"
        out = ledger_issues.insert_index_line(text, "logic", self.LINE)
        self.assertTrue(out.endswith("\n"))
        self.assertFalse(out.endswith("\n\n"))

    def test_a_malformed_pointer_line_is_refused_not_a_traceback(self):
        """L-25: `_INDEX_ENTRY_RE.match(line).group(1)` was unguarded."""
        text = "# K\n\n## logic\n- **RF-1** [x](issues/x.md) — status `open`, opened 2026-01-01\n"
        with self.assertRaises(CliError) as ctx:
            ledger_issues.insert_index_line(text, "logic", "not a pointer line")
        self.assertEqual(ctx.exception.code, 4)


# --- L-2 / L-8: fence and indent awareness on BOTH ledgers -------------------

class TestFenceAwarenessIsShared(unittest.TestCase):
    """L-2, L-8 — one scanner, both registries."""

    def test_the_defect_index_does_not_insert_inside_a_fenced_example(self):
        """L-2, reproduced before the fix: the pointer landed at the line after a
        fenced example, i.e. INSIDE the code block — F3 on Registry A."""
        text = ("# Known Issues\n\n## logic\n\nExample:\n\n```\n"
                "- **L-99** [example](issues/l-99-example.md) — status `open`, opened 2026-01-01\n"
                "```\n\n"
                "- **L-1** [real](issues/l-1-real.md) — status `open`, opened 2026-01-01\n")
        out = ledger_issues.insert_index_line(
            text, "logic",
            "- **L-0** [new](issues/l-0-new.md) — status `open`, opened 2026-07-30")
        lines = out.split("\n")
        fenced = markdown.fenced_mask(out)
        placed = next(i for i, l in enumerate(lines)
                      if l.startswith("- **L-0**"))
        self.assertFalse(
            fenced[placed],
            "the new pointer line landed inside a code fence (line %d) — it "
            "renders as code, outside the real list, and exits 0" % placed)

    def test_a_fenced_category_heading_is_not_mistaken_for_the_real_one(self):
        text = ("# K\n\n```\n## logic\n```\n\n## logic\n"
                "- **L-1** [real](issues/l-1-real.md) — status `open`, opened 2026-01-01\n")
        out = ledger_issues.insert_index_line(
            text, "logic",
            "- **L-0** [new](issues/l-0-new.md) — status `open`, opened 2026-07-30")
        lines = out.split("\n")
        fenced = markdown.fenced_mask(out)
        placed = next(i for i, l in enumerate(lines) if l.startswith("- **L-0**"))
        self.assertFalse(fenced[placed])

    def test_an_indented_anchor_is_not_live(self):
        """L-8: `line.strip() == anchor` discarded indentation, so an anchor
        documented as an indented code block counted — and `doctor` then reported
        `ready: true` while filing would insert into the code block."""
        self.assertEqual(
            ledger_backlog.anchor_positions("Seed it:\n\n    %s\n" % ANCHOR,
                                            ANCHOR), [])

    def test_an_indented_copy_does_not_make_the_real_anchor_ambiguous(self):
        """Before the fix this returned two positions, so EVERY filing exited 4."""
        positions = ledger_backlog.anchor_positions(
            "    %s\n\n%s\n" % (ANCHOR, ANCHOR), ANCHOR)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0], 2)

    def test_a_three_space_indented_anchor_still_counts(self):
        """≤3 spaces is not a code block, so it is still structure."""
        self.assertEqual(
            ledger_backlog.anchor_positions("   %s\n" % ANCHOR, ANCHOR), [0])

    def test_both_ledgers_use_the_shared_scanner(self):
        """Behavioural, not a grep: patch the shared module and assert both
        writers' locators go through it (L-3's lesson about vacuous assertions)."""
        calls = []
        real = markdown.scan

        def spy(text):
            calls.append(len(text))
            return real(text)

        with mock.patch.object(markdown, "scan", spy):
            ledger_backlog.anchor_positions("%s\n" % ANCHOR, ANCHOR)
        self.assertTrue(calls, "the work-item anchor scan bypassed markdown.scan")

        calls.clear()
        real_mask = markdown.fenced_mask

        def spy_mask(text):
            calls.append(len(text))
            return real_mask(text)

        with mock.patch.object(markdown, "fenced_mask", spy_mask):
            ledger_issues.insert_index_line(
                "# K\n\n## logic\n", "logic",
                "- **L-1** [x](issues/x.md) — status `open`, opened 2026-07-30")
        self.assertTrue(calls,
                        "the defect index insertion is still fence-blind (L-2)")


# --- L-4 / L-5 / L-6: guards applied to BOTH writers ------------------------

class TestGuardsAreSymmetric(LedgerCase):
    """L-4, L-5, L-6 — each of these existed on one writer only."""

    def test_a_non_oserror_mid_write_rolls_back_on_both_ledgers(self):
        """L-4: `file_defect` caught only `OSError`, so a KeyboardInterrupt left a
        truncated orphan record — while its own docstring promised no half-state."""
        cases = (
            ("backlog", self.file_work_item, self.records / "wi-9-item.md"),
            ("issues", self.file_defect, self.issues / "rf-9-issue.md"),
        )
        for label, filer, record in cases:
            with self.subTest(ledger=label):
                real_fdopen = os.fdopen

                def boom(fd, *args, **kwargs):
                    # close the fd we were handed before raising: leaking it makes
                    # the suite emit a ResourceWarning that has nothing to do with
                    # the production path under test
                    real_fdopen(fd, *args, **kwargs).close()
                    raise KeyboardInterrupt("interrupted mid-write")

                with mock.patch.object(os, "fdopen", side_effect=boom):
                    with self.assertRaises(KeyboardInterrupt):
                        filer()
                self.assertFalse(
                    record.exists(),
                    "%s ledger left an orphan record after a non-OSError "
                    "failure" % label)

    def test_the_body_guard_binds_at_the_writers_not_only_the_cli(self):
        """L-5: with the check only in `_read_body`, any library caller wrote an
        uncapped, unscreened body straight into a git-tracked ledger."""
        huge = "z" * (self.cfg.body_max_chars + 1)
        secret = "ghp_" + "c" * 20
        for label, filer in (("backlog", self.file_work_item),
                             ("issues", self.file_defect)):
            for kind, payload in (("over-cap", huge), ("credential", secret)):
                with self.subTest(ledger=label, kind=kind):
                    with self.assertRaises(CliError) as ctx:
                        filer(body=payload)
                    self.assertEqual(ctx.exception.code, 2)

    def test_an_honest_body_still_files_through_both_writers(self):
        self.file_work_item(body="A normal signal paragraph.")
        self.file_defect(body="A normal signal paragraph.")

    def test_id_reuse_is_refused_on_both_ledgers(self):
        """L-6: only the work-item writer had this guard; the defect writer
        checked the SLUG path only, so a differing slug let a duplicate id in."""
        fx.write_work_item(self.records, "WI-9", "wi-9-taken", title="Taken")
        with self.assertRaises(CliError) as ctx:
            self.file_work_item(slug="wi-9-different")
        self.assertEqual(ctx.exception.code, 4)

        fx.write_issue(self.issues, "RF-9", "rf-9-taken", title="Taken",
                       category="robustness")
        with self.assertRaises(CliError) as ctx:
            self.file_defect(slug="rf-9-different")
        self.assertEqual(ctx.exception.code, 4)

    def test_case_and_archive_evasion_are_refused_on_both_ledgers(self):
        """The two evasions F10/V2 named: a differing case, and a record archived
        into a subdirectory that a flat scan cannot see."""
        archive = self.records / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        fx.write_work_item(archive, "WI-9", "wi-9-archived", title="Archived")
        with self.assertRaises(CliError):
            self.file_work_item(item_id="wi-9", slug="wi-9-lowercase")

        issue_archive = self.issues / "archive"
        issue_archive.mkdir(parents=True, exist_ok=True)
        fx.write_issue(issue_archive, "RF-9", "rf-9-archived", title="Archived",
                       category="robustness")
        with self.assertRaises(CliError):
            self.file_defect(issue_id="rf-9", slug="rf-9-lowercase")

    def test_an_id_with_stray_whitespace_cannot_evade_the_guard(self):
        """L-13: the guard compared the raw id while the writer stored a collapsed
        one, so it could not recognize its own previous output."""
        fx.write_work_item(self.records, "WI-9", "wi-9-taken", title="Taken")
        with self.assertRaises(CliError):
            self.file_work_item(item_id=" WI-9 ", slug="wi-9-padded")


if __name__ == "__main__":
    unittest.main()


# --- H-01 / H-04 / H-02 / H-03: the reproduced exploits ----------------------

class TestReproducedExploits(unittest.TestCase):
    """Each of these was reproduced as a working exploit before the fix.

    All four are the same shape as the work-items they follow: a guard that was
    reasoned about carefully on one path and absent on its twin.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.inbox = self.root / ".agent" / "feedback" / "inbox"
        self.inbox.mkdir(parents=True, exist_ok=True)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)

    def _config(self, **values):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps(dict({"v": 1}, **values)))

    def test_h01_an_absolute_finding_id_cannot_write_outside_the_inbox(self):
        """H-01: `directory / record["finding_id"]` — pathlib discards the left
        operand on an absolute right one, so `save()` wrote the attacker's whole
        JSON object to any path. `write_atomic` creates parents and REPLACES."""
        self._config()
        victim = self.root / "PWNED"
        fx.write(self.inbox / "fnd-20260730-000000-deadbeef.json",
                 json.dumps({"v": 1, "status": "new",
                             "fingerprint": "deadbeefdeadbeef",
                             "finding_id": str(victim)}))
        code, _, err = fx.run_cli(
            ["--repo-root", str(self.root), "file", "--finding",
             "fnd-20260730-000000-deadbeef", "--as", "noise", "--reason", "x"])
        self.assertNotEqual(code, 0, err)
        self.assertIn("not a valid generated id", err,
                      "expected the id-grammar guard to be the one that fired; a "
                      "different message means this test is now attributing to "
                      "the wrong control (the V-22 lesson)")
        self.assertFalse(Path(str(victim) + ".json").exists(),
                         "wrote a finding outside the feedback dir")

    def test_h01_containment_holds_even_if_the_id_grammar_guard_is_bypassed(self):
        """Two independent controls stop H-01: the id grammar, and a containment
        assert on the computed path. A single test cannot tell which one fired, so
        this one neutralizes the first to pin the second — otherwise removing
        either leaves the suite green (V-22)."""
        from feedback_lib import finding as finding_mod
        victim = self.root / "PWNED2"
        with mock.patch.object(finding_mod, "validate_id",
                               side_effect=lambda value: str(value)):
            with self.assertRaises(CliError) as ctx:
                finding_mod.save(self.inbox,
                                 {"finding_id": str(victim), "status": "new"})
        self.assertIn("outside", str(ctx.exception))
        self.assertFalse(Path(str(victim) + ".json").exists())

    def test_h01_a_traversing_finding_id_is_refused(self):
        self._config()
        fx.write(self.inbox / "fnd-20260730-000001-cafebabe.json",
                 json.dumps({"v": 1, "status": "new",
                             "fingerprint": "cafebabecafebabe",
                             "finding_id": "../../../../escaped"}))
        code, _, _ = fx.run_cli(
            ["--repo-root", str(self.root), "file", "--finding",
             "fnd-20260730-000001-cafebabe", "--as", "noise", "--reason", "x"])
        self.assertNotEqual(code, 0)
        self.assertFalse((Path(self._tmp.name).parent / "escaped.json").exists())

    def test_h04_traversal_through_the_suffix_branch_deletes_nothing(self):
        """H-04: `_within` guarded only the branch that tests the ref verbatim. A
        ref WITHOUT a `.json` suffix necessarily takes the other branch — which had
        no containment — so `consume` unlinked a file outside the feedback dir."""
        self._config()
        victim = fx.write(
            self.root / "victim.json",
            json.dumps({"finding_id": "fnd-20260730-000002-aaaabbbb",
                        "status": "new", "fingerprint": "aaaabbbbccccdddd"}))
        code, _, err = fx.run_cli(
            ["--repo-root", str(self.root), "file", "--finding",
             "../../../victim", "--as", "noise", "--reason", "x"])
        self.assertEqual(code, 2, err)
        self.assertTrue(victim.exists(),
                        "a file outside the feedback dirs was DELETED")

    def test_h02_a_case_variant_of_a_forbidden_root_is_refused(self):
        """H-02: `Path.resolve()` does not canonicalize case and macOS/APFS is
        case-insensitive, so `.Claude/commands` reached the real `.claude/commands`
        — writing an attacker-influenced record body as a new slash command."""
        # `system/Docs` and `SYSTEM/x` are the isolating cases: they are NOT
        # dotfiles, so ONLY the casefolded root check can refuse them. Without
        # them the dotfile rule (H-03) absorbs every `.Claude`-style variant and
        # this test would pass with the casefolding removed (V-22).
        for variant in ("system/Docs", "SYSTEM/x", ".Claude/commands",
                        ".AGENT/skills", ".GIT/hooks"):
            with self.subTest(variant=variant):
                self._config(issues_dir=variant)
                cfg = fx.load_cfg(self.root)
                with self.assertRaises(CliError) as ctx:
                    cfg.issues_dir
                self.assertEqual(ctx.exception.code, 3)
                if not variant.startswith("."):
                    self.assertIn("executable agent surface", str(ctx.exception))

    def test_h02_a_case_variant_of_a_forbidden_basename_is_refused(self):
        for variant in ("docs/claude.md", "docs/Readme.md", "docs/Skill.md"):
            with self.subTest(variant=variant):
                self._config(index_path=variant)
                cfg = fx.load_cfg(self.root)
                with self.assertRaises(CliError):
                    cfg.index_path

    def test_h03_a_dotfile_target_is_refused_structurally(self):
        """H-03: the denylist covered 8 dirs and 5 basenames; everything else in
        the repo was a legal target, incl. `.cursorrules`, `.envrc` (where the
        index line's backticks are command substitution to bash) and
        `.github/copilot-instructions.md`. Refusing dot-components kills the class."""
        for target in (".cursorrules", ".envrc", ".windsurfrules",
                       ".github/copilot-instructions.md"):
            with self.subTest(target=target):
                self._config(index_path=target)
                cfg = fx.load_cfg(self.root)
                with self.assertRaises(CliError) as ctx:
                    cfg.index_path
                self.assertEqual(ctx.exception.code, 3)

    def test_h03_a_ledger_file_must_be_markdown(self):
        for target in ("package.json", "docs/conftest.py", "docs/data.yml"):
            with self.subTest(target=target):
                self._config(index_path=target)
                cfg = fx.load_cfg(self.root)
                with self.assertRaises(CliError):
                    cfg.index_path

    def test_the_live_consumer_configs_still_pass_every_rule(self):
        """The rules above are only acceptable if real configs satisfy them."""
        self._config(issues_dir="docs/issues", index_path="docs/KNOWN_ISSUES.md",
                     backlog_path="docs/office-skills-backlog.md",
                     backlog_dir="docs/backlog")
        cfg = fx.load_cfg(self.root)
        for attr in ("issues_dir", "index_path", "backlog_path", "backlog_dir",
                     "feedback_dir"):
            getattr(cfg, attr)


# --- M-01 / M-02: the credential screen -------------------------------------

class TestCredentialScreenCoverage(unittest.TestCase):
    """M-01, M-02 — the screen missed the exploit `body.py` was written for."""

    def test_the_env_file_scenario_the_module_was_written_for_is_caught(self):
        """`--body-file ./.env` is the docstring's own motivating example, and the
        first version excluded every `key=value` rule, so it passed."""
        for line in ("AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEX",
                     "GITHUB_TOKEN=github_pat_11ABCDEFG0abcdefghijklmnop",
                     "DATABASE_PASSWORD=s3cretVal0eWith20PlusChars"):
            with self.subTest(line=line):
                with self.assertRaises(CliError):
                    body_mod.guard_body("env dump:\n" + line, 64000)

    def test_a_pem_private_key_is_caught(self):
        """`--body-file ~/.ssh/id_rsa`: a 2 KB key is nowhere near the ceiling."""
        for header in ("-----BEGIN OPENSSH PRIVATE KEY-----",
                       "-----BEGIN RSA PRIVATE KEY-----",
                       "-----BEGIN PRIVATE KEY-----"):
            with self.subTest(header=header):
                with self.assertRaises(CliError):
                    body_mod.guard_body(header + "\nMIIEow...\n", 64000)

    def test_the_added_token_families_are_caught(self):
        cases = ("github_pat_" + "a" * 24, "glpat-" + "b" * 20,
                 "AIza" + "c" * 35, "xapp-1-A02-abcdefgh",
                 "npm_" + "d" * 36, "sk_live_" + "e" * 20,
                 "whsec_" + "f" * 20,
                 "SG.abcdefghijklmnopqrst.uvwxyzabcdefghijklmn",
                 "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkw",
                 "postgres://user:supersecret@db.internal/app")
        for value in cases:
            with self.subTest(value=value[:16]):
                with self.assertRaises(CliError):
                    body_mod.guard_body("found %s in the log" % value, 64000)

    def test_a_partially_masked_secret_is_still_refused(self):
        """M-02: `_MASKED_RE.search` over the whole span meant an operator masking
        only the MIDDLE — the likely habit, since the error says "remove or mask" —
        laundered a token with a live tail past the screen."""
        for value in ("ghp_xxxxxxxx0123456789abcdefgh",
                      "Bearer ...eyJhbGciOiJIUzI1NiJ9.LIVETAILabcdefgh"):
            with self.subTest(value=value[:20]):
                with self.assertRaises(CliError):
                    body_mod.guard_body("token: %s" % value, 64000)

    def test_fully_masked_documentation_still_files(self):
        """The other side of the dominance rule: a record describing this screen
        must not refuse itself (audit 093 Risk 7)."""
        for value in ("sk-[REDACTED]", "AKIA[REDACTED]",
                      "ghp_REDACTEDREDACTEDREDACTED",
                      "Bearer YOUR_TOKEN_HERE"):
            with self.subTest(value=value):
                text = "we found %s in the log" % value
                self.assertEqual(body_mod.guard_body(text, 64000), text)

    def test_prose_that_would_false_positive_still_files(self):
        """The narrow env rule must not fire on prose: lowercase, a colon rather
        than `=`, a bracketed placeholder, or a short/spaced value."""
        for text in ("the bypass token: [PLACEHOLDER] disables the gate",
                     "password: see the vault entry",
                     "set TOKEN=abc for the test",
                     "reported by someone@example.com"):
            with self.subTest(text=text):
                self.assertEqual(body_mod.guard_body(text, 64000), text)

    def test_all_credentials_on_a_line_are_reported_not_just_the_first(self):
        """L-21: an early `break` meant an operator masked one and got refused
        again, one secret at a time."""
        found = body_mod.find_credentials(
            "a ghp_%s here\nb glpat-%s there\n" % ("a" * 20, "b" * 20))
        self.assertEqual([lineno for _, lineno in found], [1, 2])

    def test_a_cr_only_body_is_numbered_by_real_lines(self):
        """L-21: `split("\\n")` made a `\\r`-progress-bar body ONE line."""
        found = body_mod.find_credentials("progress\rdone ghp_%s" % ("c" * 20))
        self.assertEqual(found[0][1], 2)


# --- perf: the DoS-shaped findings ------------------------------------------

class TestBoundedWork(unittest.TestCase):
    """perf-High and M-04 — cost proportional to the limit, not to the input."""

    def test_clip_does_not_scan_the_whole_input(self):
        """`clip` redacted BEFORE slicing, so `excerpt_max_chars` bounded the
        output but not the work: 100 MB scanned to produce 2 000 chars — on tool
        output, inside a synchronous hook (M-04)."""
        from feedback_lib import filters
        huge = ("no-at-signs-here " * 60000) + "tail"
        out = filters.clip(huge, 100)
        self.assertLessEqual(len(out), 100)
        self.assertTrue(out.endswith("tail"))

    def test_a_cap_of_one_still_caps(self):
        """sec-L-02: `text[-(limit - 1):]` is `text[-0:]` — the WHOLE string."""
        from feedback_lib import filters
        self.assertLessEqual(len(filters.clip("x" * 5000, 1)), 1)

    def test_the_hook_truncates_the_response_before_any_scan(self):
        """perf-High: `_response_text` + `find_envelope` + `_exit_code` all ran
        over the FULL tool output, above the exit-0 discard."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
        import posttooluse_filter as hook
        text = hook._response_text({"stdout": "y" * (hook.TAIL_CHARS * 3)})
        self.assertLessEqual(len(text), hook.TAIL_CHARS)

    def test_doctor_counts_the_inbox_without_parsing_it(self):
        """perf Med-low: `len(inbox.scan(...))` opened and json.loads'd every file
        to produce an integer — the O(k) WI-5 had just deleted, one command over."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = fx.make_repo(tmp.name)
        fx.write(root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write(root / "docs" / "feedback" / "config.json", json.dumps({"v": 1}))
        cfg = fx.load_cfg(root)
        inbox_dir = Path(cfg.inbox_dir)
        inbox_dir.mkdir(parents=True, exist_ok=True)
        for i in range(4):
            fx.write(inbox_dir / ("fnd-20260730-00000%d-abcdefab.json" % i),
                     "not even valid json {{{")
        opened = []
        real_read = Path.read_text

        def counting(self_path, *a, **kw):
            if str(self_path).endswith(".json") and "inbox" in str(self_path):
                opened.append(str(self_path))
            return real_read(self_path, *a, **kw)

        with mock.patch.object(Path, "read_text", counting):
            code, out, err = fx.run_cli(["--repo-root", str(root), "doctor",
                                         "--json"])
        payload = json.loads(out)
        self.assertEqual(payload["checks"]["inbox_depth"], 4)
        self.assertEqual(opened, [],
                         "doctor parsed %d inbox files to produce a count"
                         % len(opened))
