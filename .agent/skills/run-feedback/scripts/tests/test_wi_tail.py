"""Regression tests for TASK 093 — the WI-2…WI-7 tail.

Every test names the work-item or finding it pins. The organizing rule of this
file, from WI-7: **a fix that lands on one of two symmetric code paths is half a
fix**, so where a guard exists in both ledgers it is tested against both by
parameterization, not by two hand-copied tests that can drift apart.

  WI-2  record bodies were neither size-capped nor screened for credentials
  WI-3  ledger bodies were unmarked agent-trusted context
  WI-4  `Config.__init__` spawned `git` for a value most paths never read
  WI-5  `find_by_fingerprint` opened every file in the inbox
  WI-6  `--finding <path>` accepted any path and `consume` unlinked it
  V7    the placeholder strip probed fixed offsets
  V8    naive fence toggling mis-detected fenced regions
  V9    `doctor` aborted on the misconfiguration it exists to report
  V11   CONTRACT_KEYS was asserted against a literal that restated it
  V12   the newline-fidelity fix landed in only one ledger
  V13   `backlog_anchor` / `id_prefixes` / `*_max_chars` reached behaviour raw
  V17   a failed `consume` after a good ledger write stranded the finding
  V21   `"true"` / `"2026"` round-tripped as bool / int
  V08   `doctor`'s `.doctor-probe` write followed a planted symlink
  V10   `provisional_id` was JSON-only, and absent from the defect path
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import (atomic, body as body_mod, config as config_mod,  # noqa: E402
                          frontmatter, inbox, ledger_backlog, ledger_issues)
from feedback_lib.envelope import CliError  # noqa: E402

ANCHOR = "<!-- feedback:discovered-issues -->"


# --- WI-2: the body policy ---------------------------------------------------

class TestBodyPolicy(unittest.TestCase):
    """WI-2. Cap and screen, never rewrite (TASK 093 §1.1)."""

    def test_a_body_at_the_cap_passes_and_one_byte_over_is_refused(self):
        self.assertEqual(body_mod.guard_body("x" * 100, 100), "x" * 100)
        with self.assertRaises(CliError) as ctx:
            body_mod.guard_body("x" * 101, 100)
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("100-character ceiling", str(ctx.exception))

    def test_over_cap_body_is_refused_not_truncated(self):
        """Truncating evidence silently is how a record ends mid-sentence."""
        with self.assertRaises(CliError):
            body_mod.guard_body("y" * 10, 5)

    def test_each_credential_class_is_refused(self):
        cases = {
            "AWS access key id": "leak AKIA" + "A" * 16 + " here",
            "OpenAI-style secret key": "key sk-abcd1234efgh5678",
            "GitHub token": "ghp_" + "a" * 20,
            "Slack token": "xoxb-1234567890abc",
            "HTTP bearer token": "Authorization: Bearer abcdefgh12345678",
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(CliError) as ctx:
                    body_mod.guard_body("line one\n" + text, 64000)
                message = str(ctx.exception)
                self.assertIn(label, message)
                self.assertIn("line 2", message)

    def test_the_error_never_echoes_the_secret(self):
        """The message is printed AND journaled, so echoing the match would leak
        the secret through the check that caught it."""
        secret = "sk-supersecretvalue999"
        with self.assertRaises(CliError) as ctx:
            body_mod.guard_body("oops %s" % secret, 64000)
        rendered = str(ctx.exception) + json.dumps(
            ctx.exception.details, ensure_ascii=False)
        self.assertNotIn(secret, rendered)
        self.assertNotIn("supersecret", rendered)

    def test_prose_that_the_loose_redact_rules_would_hit_still_files(self):
        """The `k: v` and email rules of `filters.redact` are deliberately NOT in
        the screen: a work-item about the spec-validator gate legitimately writes
        "the bypass token: …", and refusing prose blocks real filing."""
        for text in ("the bypass token: [PLACEHOLDER] disables the gate",
                     "reported by someone@example.com",
                     "password: see the vault entry",
                     "Authorization: Bearer <token>"):
            with self.subTest(text=text):
                self.assertEqual(body_mod.guard_body(text, 64000), text)

    def test_an_already_redacted_secret_shape_still_files(self):
        """audit 093 Risk 7 — a record describing this very screen contains these
        shapes, and a screen that refuses its own documentation gets disabled."""
        for text in ("we found sk-[REDACTED] in the log",
                     "AKIA[REDACTED] appeared twice",
                     "ghp_REDACTEDREDACTEDREDACTED was rotated",
                     "Bearer YOUR_TOKEN_HERE in the example"):
            with self.subTest(text=text):
                self.assertEqual(body_mod.guard_body(text, 64000), text)

    def test_the_body_is_returned_byte_identical(self):
        """Nothing is rewritten — that is the whole point of refusing instead."""
        text = "  leading\n\ttabbed\r\nCRLF line\n\n"
        self.assertEqual(body_mod.guard_body(text, 64000), text)


class TestBodyPolicyReachesBothLedgers(unittest.TestCase):
    """WI-2 — the gate sits at the single CLI read, so neither ledger can be
    reached around it. Asserted through the CLI, not the library."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "BACKLOG.md", fx.BACKLOG_INDEX_FIXTURE)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md",
                             "body_max_chars": 200}))
        code, out, err = fx.run_cli(
            ["--repo-root", str(self.root), "collect", "--source", "workflow",
             "--kind", "gate-failure", "--component", "demo",
             "--message", "boom", "--json"])
        self.assertEqual(code, 0, err)
        self.fid = json.loads(out)["finding"]["finding_id"]

    def _file(self, classification, body_text, extra=()):
        body_path = fx.write(self.root / "body.md", body_text)
        argv = ["--repo-root", str(self.root), "file", "--finding", self.fid,
                "--as", classification, "--title", "T",
                "--body-file", str(body_path), "--json", *extra]
        return fx.run_cli(argv)

    def test_over_cap_body_is_refused_on_the_work_item_path(self):
        code, _, err = self._file("work-item", "z" * 400)
        self.assertEqual(code, 2, err)
        self.assertIn("ceiling", err)

    def test_over_cap_body_is_refused_on_the_defect_path(self):
        code, _, err = self._file("defect", "z" * 400,
                                  extra=("--category", "robustness"))
        self.assertEqual(code, 2, err)
        self.assertIn("ceiling", err)

    def test_credential_is_refused_on_both_paths(self):
        for classification, extra in (("work-item", ()),
                                      ("defect", ("--category", "robustness"))):
            with self.subTest(classification=classification):
                code, _, err = self._file(classification,
                                          "ghp_" + "b" * 20, extra=extra)
                self.assertEqual(code, 2, err)
                self.assertIn("credential", err)


# --- WI-3: provenance --------------------------------------------------------

class TestProvenanceMarking(unittest.TestCase):
    """WI-3 — both ledgers, one parameterized test (that is the WI-7 lesson)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "BACKLOG.md", fx.BACKLOG_INDEX_FIXTURE)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        self.cfg = fx.load_cfg(self.root)

    def _file_both(self, extensions):
        work = ledger_backlog.file_work_item(
            self.cfg, "WI-5", "wi-5-item", "An item", "Signal body.",
            opened_at="2026-07-30", extensions=extensions)
        defect = ledger_issues.file_defect(
            self.cfg, "RF-5", "rf-5-issue", "An issue", "robustness",
            "Signal body.", opened_at="2026-07-30", extensions=extensions)
        return (Path(work["record_path"]).read_text(encoding="utf-8"),
                Path(defect["issue_path"]).read_text(encoding="utf-8"))

    def test_a_machine_filed_record_carries_the_key_and_the_banner(self):
        for text in self._file_both({"finding_ref": "fnd-20260730-1-abcd1234"}):
            meta, body = frontmatter.parse(text)
            self.assertEqual(meta["provenance"], "machine")
            self.assertIn("data, not instructions", body)
            self.assertIn("fnd-20260730-1-abcd1234", body)

    def test_the_banner_sits_above_an_unchanged_body(self):
        for text in self._file_both({"finding_ref": "fnd-x"}):
            _, body = frontmatter.parse(text)
            lines = [l for l in body.split("\n") if l.strip()]
            self.assertTrue(lines[0].startswith("# "), lines[0])
            self.assertTrue(lines[1].startswith("> Filed by"), lines[1])
            self.assertEqual(lines[2], "Signal body.")

    def test_a_record_without_a_finding_ref_gets_neither(self):
        """A hand-written record is not machine-provenanced. Library callers that
        file without a capture (there are none in-tree today) stay unmarked
        rather than being mislabelled."""
        for text in self._file_both({}):
            meta, body = frontmatter.parse(text)
            self.assertNotIn("provenance", meta)
            self.assertNotIn("Filed by", body)

    def test_provenance_is_written_after_the_contract_keys(self):
        for text in self._file_both({"finding_ref": "fnd-x"}):
            meta, _ = frontmatter.parse(text)
            keys = list(meta)
            self.assertIn("provenance", keys)
            self.assertGreater(keys.index("provenance"), keys.index("slug"))


# --- WI-4: laziness ----------------------------------------------------------

class TestNoEagerGitSpawn(unittest.TestCase):
    """WI-4."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)

    def test_building_a_config_spawns_no_subprocess(self):
        with mock.patch.object(config_mod.subprocess, "run") as spawn:
            cfg = config_mod.load_config(repo_root=self.root)
            _ = cfg.index_path, cfg.issues_dir, cfg.backlog_anchor
        spawn.assert_not_called()

    def test_data_root_is_resolved_once_and_cached_per_instance(self):
        """An UNCACHED lazy property would spawn `git` on every `feedback_dir`
        access — worse than the eager call it replaced (audit 093 Risk 4)."""
        calls = []
        real_run = config_mod.subprocess.run

        def counting(*args, **kwargs):
            calls.append(args)
            return real_run(*args, **kwargs)

        cfg = config_mod.load_config(repo_root=self.root)
        with mock.patch.object(config_mod.subprocess, "run",
                               side_effect=counting):
            for _ in range(5):
                _ = cfg.feedback_dir, cfg.inbox_dir, cfg.journal_dir
        self.assertEqual(len(calls), 1, "data_root recomputed per access")

    def test_the_git_timeout_is_short_enough_not_to_stall_a_hook(self):
        captured = {}
        real_run = config_mod.subprocess.run

        def spy(*args, **kwargs):
            captured.update(kwargs)
            return real_run(*args, **kwargs)

        cfg = config_mod.load_config(repo_root=self.root)
        with mock.patch.object(config_mod.subprocess, "run", side_effect=spy):
            _ = cfg.feedback_dir
        self.assertLessEqual(captured.get("timeout", 99), 2)

    def test_data_root_still_falls_back_to_repo_root(self):
        cfg = config_mod.load_config(repo_root=self.root)
        self.assertEqual(cfg.data_root, self.root)


class TestHookLoadsConfigOnlyWhenCapturing(unittest.TestCase):
    """WI-4 — the expensive load must sit BELOW the cheap discard filters."""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)

    def _run_hook(self, payload, env=None):
        import posttooluse_filter as hook
        loads = []
        real_load = hook.load_config if hasattr(hook, "load_config") else None
        with mock.patch("feedback_lib.config.load_config",
                        side_effect=lambda **kw: loads.append(kw)) as _:
            with mock.patch.object(hook.sys, "stdin",
                                   new=StringIOish(json.dumps(payload))):
                with mock.patch.dict(os.environ, env or {}, clear=False):
                    code = hook.main()
        self.assertEqual(code, 0, "the hook contract is ALWAYS exit 0")
        return loads

    def test_a_non_bash_payload_loads_no_config(self):
        loads = self._run_hook({"tool_name": "Read", "cwd": str(self.root)})
        self.assertEqual(loads, [],
                         "config (and its git spawn) loaded for an event the "
                         "cheap filter discards")

    def test_a_passing_bash_command_loads_no_config(self):
        loads = self._run_hook({
            "tool_name": "Bash", "cwd": str(self.root),
            "tool_input": {"command": "ls"},
            "tool_response": {"exit_code": 0, "stdout": "ok"}})
        self.assertEqual(loads, [])

    def test_debug_mode_still_sees_a_discarded_payload(self):
        """The dump exists to diagnose why the filters discarded something, so it
        stays ABOVE them and pays for its own load."""
        loads = self._run_hook({"tool_name": "Read", "cwd": str(self.root)},
                               env={"RUN_FEEDBACK_HOOK_DEBUG": "1"})
        self.assertEqual(len(loads), 1)


class StringIOish:
    """Minimal stdin stand-in: `json.load` only needs `.read()`."""

    def __init__(self, text):
        self._text = text

    def read(self, *_):
        return self._text


# --- WI-5 / WI-6: the inbox --------------------------------------------------

class TestInboxLookup(unittest.TestCase):
    """WI-5, WI-6."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.cfg = fx.load_cfg(self.root)
        self.inbox = Path(self.cfg.inbox_dir)
        self.inbox.mkdir(parents=True, exist_ok=True)

    def _plant(self, finding_id, fingerprint):
        path = self.inbox / (finding_id + ".json")
        fx.write(path, json.dumps({"v": 1, "finding_id": finding_id,
                                   "fingerprint": fingerprint,
                                   "status": "new"}))
        return path

    def test_lookup_reads_only_the_candidates_not_the_whole_inbox(self):
        wanted = "a" * 16
        self._plant("fnd-20260730-000001-" + wanted[:8], wanted)
        for i in range(30):
            other = "%016x" % i
            self._plant("fnd-20260730-0000%02d-%s" % (i + 10, other[:8]), other)
        opened = []
        real_read = Path.read_text

        def counting(self_path, *args, **kwargs):
            opened.append(str(self_path))
            return real_read(self_path, *args, **kwargs)

        with mock.patch.object(Path, "read_text", counting):
            path, record = inbox.find_by_fingerprint(self.inbox, wanted)
        self.assertIsNotNone(record)
        self.assertEqual(record["fingerprint"], wanted)
        self.assertEqual(
            len(opened), 1,
            "opened %d files to answer one lookup — the O(k^2) capture path is "
            "back (WI-5)" % len(opened))

    def test_a_colliding_eight_char_prefix_still_resolves_correctly(self):
        """The prefix is not unique, so the FULL fingerprint is verified."""
        shared = "deadbeef"
        first = shared + "1" * 8
        second = shared + "2" * 8
        self._plant("fnd-20260730-000001-" + shared, first)
        self._plant("fnd-20260730-000002-" + shared, second)
        for fingerprint in (first, second):
            with self.subTest(fingerprint=fingerprint):
                _, record = inbox.find_by_fingerprint(self.inbox, fingerprint)
                self.assertEqual(record["fingerprint"], fingerprint)

    def test_a_filename_whose_prefix_lies_is_not_a_false_match(self):
        self._plant("fnd-20260730-000001-cafebabe", "0" * 16)
        _, record = inbox.find_by_fingerprint(self.inbox, "cafebabe" + "0" * 8)
        self.assertIsNone(record)

    def test_the_filename_invariant_the_glob_depends_on_still_holds(self):
        """WI-5 narrows dedup to "the id encodes the fingerprint prefix". If
        `finding.save` ever stops deriving the name from `finding_id`, dedup goes
        silently blind — so the invariant is pinned here, not just documented."""
        from feedback_lib import finding as finding_mod
        record = finding_mod.new_finding("workflow", "gate-failure", "demo",
                                         "boom")
        target = finding_mod.save(self.inbox, record)
        self.assertEqual(target.name, record["finding_id"] + ".json")
        self.assertTrue(target.stem.endswith(record["fingerprint"][:8]))

    def test_a_path_outside_the_feedback_dirs_is_refused_and_not_deleted(self):
        """WI-6 — `consume` unlinks what `resolve` returns."""
        outsider = fx.write(self.root / "somebody" / "state.json",
                            json.dumps({"finding_id": "fnd-x",
                                        "status": "new"}))
        with self.assertRaises(CliError) as ctx:
            inbox.resolve(self.cfg, str(outsider))
        self.assertEqual(ctx.exception.code, 2)
        self.assertTrue(outsider.exists(), "the file was deleted anyway")

    def test_a_path_inside_the_inbox_still_resolves(self):
        planted = self._plant("fnd-20260730-000001-abcdefab", "abcdefab" * 2)
        path, record = inbox.resolve(self.cfg, str(planted))
        self.assertEqual(Path(path).name, planted.name)
        self.assertEqual(record["finding_id"], "fnd-20260730-000001-abcdefab")

    def test_id_resolution_is_unaffected(self):
        self._plant("fnd-20260730-000001-abcdefab", "abcdefab" * 2)
        _, record = inbox.resolve(self.cfg, "fnd-20260730-000001-abcdefab")
        self.assertEqual(record["status"], "new")

    def test_a_nul_byte_in_the_reference_does_not_traceback(self):
        """`Path.resolve()` raises ValueError, not OSError, on an embedded NUL."""
        with self.assertRaises(CliError) as ctx:
            inbox.resolve(self.cfg, "fnd-\x00-nope")
        self.assertIn(ctx.exception.code, (2, 5))


# --- V7 / V8: anchor resolution ---------------------------------------------

class TestPlaceholderStrip(unittest.TestCase):
    """V7 — walk forward, do not probe fixed offsets."""

    def _insert(self, text):
        return ledger_backlog.insert_after_anchor(text, ANCHOR, "- **WI-1** x")

    def test_one_blank_line_before_the_placeholder(self):
        out = self._insert("%s\n\n_No work-items recorded yet._\n" % ANCHOR)
        self.assertNotIn("_No work-items", out)

    def test_two_blank_lines_before_the_placeholder(self):
        """The offset probe checked positions 2 and 3 only."""
        out = self._insert("%s\n\n\n_No work-items recorded yet._\n" % ANCHOR)
        self.assertNotIn("_No work-items", out)

    def test_a_later_sections_placeholder_is_never_deleted(self):
        """The offset probe could reach past a heading and delete a DIFFERENT
        section's placeholder, leaving that section looking populated."""
        text = ("%s\n\n## Closed\n\n_No work-items recorded yet._\n" % ANCHOR)
        out = self._insert(text)
        self.assertIn("_No work-items recorded yet._", out)
        self.assertIn("- **WI-1** x", out)

    def test_an_existing_entry_is_not_mistaken_for_a_placeholder(self):
        text = "%s\n- **WI-9** existing\n" % ANCHOR
        out = self._insert(text)
        self.assertIn("- **WI-9** existing", out)


class TestFenceDetection(unittest.TestCase):
    """V8 — CommonMark fence tracking, still fail-closed.

    Every test asserts WHICH line resolved, never just how many. Asserting
    `len(positions) == 1` passes when the WRONG anchor is found — a naive-toggle
    regression finds exactly one anchor too, just the one inside the fence. That is
    the same "passes for the wrong reason" defect V-22 is about, and a mutation
    run is what exposed it in the first draft of this class.
    """

    def _resolve(self, lines):
        """`lines` marks the anchor that must resolve with a trailing '<<'."""
        expected = [i for i, l in enumerate(lines) if l.endswith("<<")]
        self.assertEqual(len(expected), 1, "fixture must mark exactly one anchor")
        text = "\n".join(l[:-2] if l.endswith("<<") else l for l in lines)
        positions = ledger_backlog.anchor_positions(text, ANCHOR)
        self.assertEqual(
            positions, expected,
            "resolved lines %s, expected %s — a fence was mis-tracked, so the "
            "index line would land in the wrong place" % (positions, expected))

    def test_a_three_backtick_line_does_not_close_a_four_backtick_fence(self):
        self._resolve(["````", "```", ANCHOR, "````", "", ANCHOR + "<<"])

    def test_tildes_do_not_close_a_backtick_fence(self):
        self._resolve(["```", "~~~", ANCHOR, "```", "", ANCHOR + "<<"])

    def test_backticks_do_not_close_a_tilde_fence(self):
        self._resolve(["~~~", "```", ANCHOR, "~~~", "", ANCHOR + "<<"])

    def test_a_four_space_indented_line_is_not_a_fence(self):
        """Indented code, not a fence — the old toggle flipped on it and inverted
        every fence state below it."""
        self._resolve(["    ```", ANCHOR + "<<"])

    def test_an_info_string_does_not_make_a_closing_fence(self):
        self._resolve(["```", "```yaml", ANCHOR, "```", "", ANCHOR + "<<"])

    def test_a_longer_run_closes_a_shorter_fence(self):
        self._resolve(["```", "content", "`````", ANCHOR + "<<"])

    def test_a_fence_indented_up_to_three_spaces_still_counts(self):
        self._resolve(["   ```", ANCHOR, "   ```", "", ANCHOR + "<<"])

    def test_the_documented_anchor_in_a_fence_is_still_ignored(self):
        """F3 must not regress: this is the defect the guard exists for, and a
        fence rewrite that fails OPEN is strictly worse than the nuisance it
        fixes (TASK 093 §4)."""
        self._resolve(["```", ANCHOR, "```", "", ANCHOR + "<<"])

    def test_an_unclosed_fence_still_exits_4_but_says_why(self):
        """V8 called this a fail-closed DoS. Per CommonMark an unclosed fence runs
        to EOF, so the anchor really IS inside a code block — the fix is a message
        that names the fence, not permission to write."""
        text = "# B\n\n```\nstuff\n\n%s\n" % ANCHOR
        with self.assertRaises(CliError) as ctx:
            ledger_backlog.insert_after_anchor(text, ANCHOR, "- x")
        self.assertEqual(ctx.exception.code, 4)
        remediation = ctx.exception.details.get("remediation", "")
        self.assertIn("line 3", remediation)
        self.assertIn("never closed", remediation)


# --- V12: newline fidelity on BOTH ledgers ----------------------------------

class TestNewlineFidelityBothLedgers(unittest.TestCase):
    """V12 — the fix landed in the backlog module only. One test, both paths."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))

    def _write_crlf(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        return path

    def test_both_ledgers_read_through_the_same_primitive(self):
        """Not a style point: the asymmetry IS the defect class (WI-7)."""
        self.assertIs(ledger_backlog._read_verbatim.__wrapped__
                      if hasattr(ledger_backlog._read_verbatim, "__wrapped__")
                      else atomic.read_verbatim, atomic.read_verbatim)
        source = Path(ledger_issues.__file__).read_text(encoding="utf-8")
        self.assertIn("atomic.read_verbatim", source,
                      "the defect ledger still reads with newline translation")

    def test_a_crlf_backlog_keeps_crlf(self):
        index = self._write_crlf("docs/BACKLOG.md", fx.BACKLOG_INDEX_FIXTURE)
        cfg = fx.load_cfg(self.root)
        (self.root / "docs" / "backlog").mkdir(parents=True, exist_ok=True)
        ledger_backlog.file_work_item(cfg, "WI-5", "wi-5-x", "T", "Body.",
                                      opened_at="2026-07-30")
        raw = index.read_bytes()
        self.assertEqual(
            raw.count(b"\r\n"), raw.count(b"\n"),
            "a bare LF was introduced into a CRLF ledger: %d CRLF vs %d LF"
            % (raw.count(b"\r\n"), raw.count(b"\n")))
        self.assertIn(b"- **WI-5**", raw)

    def test_a_crlf_known_issues_index_keeps_crlf(self):
        index = self._write_crlf("docs/KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        cfg = fx.load_cfg(self.root)
        ledger_issues.file_defect(cfg, "RF-5", "rf-5-x", "T", "robustness",
                                  "Body.", opened_at="2026-07-30")
        raw = index.read_bytes()
        self.assertEqual(raw.count(b"\r\n"), raw.count(b"\n"),
                         "the defect index still normalizes CRLF to LF — V12")

    def test_a_reader_break_in_an_index_line_does_not_split_it(self):
        """`splitlines()` breaks on U+2028; `split("\\n")` does not."""
        for module, fixture, relative in (
                (ledger_backlog, fx.BACKLOG_INDEX_FIXTURE, "docs/BACKLOG.md"),
                (ledger_issues, fx.INDEX_FIXTURE, "docs/KNOWN_ISSUES.md")):
            with self.subTest(module=module.__name__):
                path = fx.write(self.root / relative,
                                fixture.replace("# ", "#  odd ", 1))
                before = path.read_text(encoding="utf-8").count(" ")
                cfg = fx.load_cfg(self.root)
                if module is ledger_backlog:
                    (self.root / "docs" / "backlog").mkdir(parents=True,
                                                           exist_ok=True)
                    module.file_work_item(cfg, "WI-6", "wi-6-x", "T", "B.",
                                          opened_at="2026-07-30")
                else:
                    module.file_defect(cfg, "RF-6", "rf-6-x", "T", "robustness",
                                       "B.", opened_at="2026-07-30")
                after = path.read_text(encoding="utf-8")
                self.assertEqual(after.count(" "), before,
                                 "U+2028 was consumed as a line break")


# --- V11: the contract tuples ------------------------------------------------

class TestContractKeysArePinned(unittest.TestCase):
    """V11 — the tuples must be pinned to the SKILL.md authority, and the
    assembly must USE them rather than restate them."""

    def _extractor(self):
        # tests -> scripts -> run-feedback -> skills
        skill_dir = (Path(__file__).resolve().parents[3]
                     / "known-issues-format")
        script = skill_dir / "scripts" / "check_contract_sync.py"
        skill = skill_dir / "SKILL.md"
        if not script.is_file() or not skill.is_file():
            self.skipTest("known-issues-format not installed beside run-feedback")
        sys.path.insert(0, str(script.parent))
        import check_contract_sync as gate
        return gate, skill.read_text(encoding="utf-8")

    def test_both_tuples_match_the_skill_md_contract(self):
        gate, skill_text = self._extractor()
        for registry, module in (("work-items", ledger_backlog),
                                 ("defects", ledger_issues)):
            with self.subTest(registry=registry):
                documented = gate._frontmatter_keys(
                    gate._slice(skill_text, registry))
                self.assertEqual(
                    list(module.CONTRACT_KEYS), documented,
                    "%s.CONTRACT_KEYS diverged from the known-issues-format "
                    "authority for registry %r" % (module.__name__, registry))

    def test_a_contract_key_with_no_source_value_raises_immediately(self):
        """This is the property the old `list(meta)[:5] != CONTRACT_KEYS[:5]`
        assertion could not have: it compared a literal to a tuple restating it."""
        with mock.patch.object(ledger_backlog, "CONTRACT_KEYS",
                               ledger_backlog.CONTRACT_KEYS + ("invented",)):
            with self.assertRaises(KeyError):
                ledger_backlog._build_meta("WI-1", "s", "open", "2026-07-30",
                                           None, None, None, {})
        with mock.patch.object(ledger_issues, "CONTRACT_KEYS",
                               ledger_issues.CONTRACT_KEYS + ("invented",)):
            with self.assertRaises(KeyError):
                ledger_issues._build_meta("RF-1", "s", "open", "2026-07-30",
                                          "robustness", None, {})

    def test_an_empty_required_contract_key_is_refused(self):
        with self.assertRaises(CliError):
            ledger_backlog._build_meta("WI-1", "", "open", "2026-07-30",
                                       None, None, None, {})
        with self.assertRaises(CliError):
            ledger_issues._build_meta("RF-1", "s", "open", "2026-07-30",
                                      "", None, {})

    def test_severity_is_the_one_optional_defect_contract_key(self):
        meta = ledger_issues._build_meta("RF-1", "s", "open", "2026-07-30",
                                         "robustness", None, {})
        self.assertNotIn("severity", meta)
        self.assertEqual(list(meta)[:4],
                         ["id", "type", "status", "opened_at"])


# --- V13: config validation --------------------------------------------------

class TestConfigValidation(unittest.TestCase):
    """V13."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)

    def _cfg(self, values):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps(dict({"v": 1}, **values)))
        return fx.load_cfg(self.root)

    def test_an_empty_anchor_is_refused_before_it_matches_every_blank_line(self):
        cfg = self._cfg({"backlog_anchor": ""})
        with self.assertRaises(CliError) as ctx:
            cfg.backlog_anchor
        self.assertEqual(ctx.exception.code, 3)

    def test_a_padded_anchor_is_refused(self):
        cfg = self._cfg({"backlog_anchor": "  <!-- x -->  "})
        with self.assertRaises(CliError):
            cfg.backlog_anchor

    def test_a_multiline_anchor_is_refused(self):
        cfg = self._cfg({"backlog_anchor": "<!-- a -->\n<!-- b -->"})
        with self.assertRaises(CliError):
            cfg.backlog_anchor

    def test_an_unusable_id_prefix_is_refused(self):
        for bad in ("../x", "a b", "", "1abc", "x" * 40, None, 7):
            with self.subTest(bad=bad):
                cfg = self._cfg({"id_prefixes": {"_default": bad}})
                with self.assertRaises(CliError):
                    cfg.id_prefixes

    def test_the_prefixes_live_consumers_actually_ship_are_accepted(self):
        """audit 093 Risk 1 — `TF-X` broke the first regex I wrote. These are
        real values from Universal-skills; a future tightening must not drop them."""
        cfg = self._cfg({"id_prefixes": {
            "_default": "RF", "transcript-fetcher": "TF-X",
            "wiki-ingest": "WIKI-INGEST", "html": "HTML2MD", "xlsx": "XLSX"}})
        self.assertEqual(cfg.id_prefixes["transcript-fetcher"], "TF-X")

    def test_non_positive_char_limits_are_refused(self):
        for key in ("excerpt_max_chars", "body_max_chars"):
            for bad in (0, -1, "lots", None):
                with self.subTest(key=key, bad=bad):
                    cfg = self._cfg({key: bad})
                    with self.assertRaises(CliError) as ctx:
                        getattr(cfg, key)
                    self.assertEqual(ctx.exception.code, 3)

    def test_this_repos_own_config_passes_every_validation(self):
        """Run the guards against the framework's real config, not a fixture."""
        # tests -> scripts -> run-feedback -> skills -> .agent -> repo root
        here = Path(__file__).resolve().parents[5]
        live = here / "docs" / "feedback" / "config.json"
        if not live.is_file():
            self.skipTest("not running inside the framework repo")
        cfg = config_mod.load_config(config_arg=str(live), repo_root=here)
        _ = (cfg.backlog_anchor, cfg.id_prefixes, cfg.excerpt_max_chars,
             cfg.body_max_chars, cfg.issues_dir, cfg.index_path,
             cfg.backlog_path, cfg.backlog_dir)


# --- V21: YAML coercion ------------------------------------------------------

class TestSerializerCoercionGuard(unittest.TestCase):
    """V21."""

    def test_boolish_text_is_quoted(self):
        for text in ("true", "False", "yes", "NO", "on", "off", "null", "~"):
            with self.subTest(text=text):
                out = frontmatter.scalar(text, "value")
                self.assertTrue(out.startswith("'"),
                                "%r emitted bare as %s" % (text, out))

    def test_numeric_text_is_quoted(self):
        for text in ("2026", "0", "-3", "1.5", "1e6", "0x10", "0o17", "010"):
            with self.subTest(text=text):
                self.assertTrue(frontmatter.scalar(text, "value").startswith("'"))

    def test_a_real_bool_is_still_emitted_bare(self):
        self.assertEqual(frontmatter.scalar(True, "auto_fixable"), "true")
        self.assertEqual(frontmatter.scalar(False, "auto_fixable"), "false")

    def test_iso_dates_stay_bare(self):
        """Quoting these would rewrite every record in every corpus."""
        for text in ("2026-07-30", "WI-7", "SEV-2",
                     "docs/backlog/x.md", "614ee37f7fb28554"):
            with self.subTest(text=text):
                self.assertEqual(frontmatter.scalar(text, "value"), text)

    def test_quoted_values_still_round_trip_through_our_reader(self):
        for text in ("true", "2026", "0x10"):
            with self.subTest(text=text):
                doc = frontmatter.serialize({"value": text}) + "\nbody\n"
                meta, _ = frontmatter.parse(doc)
                self.assertEqual(meta["value"], text)

    def test_the_apostrophe_rewrite_is_announced(self):
        stderr = StringWriter()
        with mock.patch.object(frontmatter.sys, "stderr", stderr):
            out = frontmatter.scalar("it's a thing, really", "value")
        self.assertIn("’", out)
        self.assertIn("apostrophe in value", stderr.text)

    def test_no_warning_when_nothing_is_rewritten(self):
        stderr = StringWriter()
        with mock.patch.object(frontmatter.sys, "stderr", stderr):
            frontmatter.scalar("plain prose, no quotes", "value")
        self.assertEqual(stderr.text, "")


class StringWriter:
    def __init__(self):
        self.text = ""

    def write(self, chunk):
        self.text += chunk


# --- V9 / V08 / V10 / WI-5 depth: doctor and dry-run ------------------------

class TestDoctorRobustness(unittest.TestCase):
    """V9, V-08, and the inbox-depth signal from WI-5."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)

    def _doctor(self, values=None):
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps(dict({"v": 1}, **(values or {}))))
        code, out, err = fx.run_cli(["--repo-root", str(self.root), "doctor",
                                     "--json"])
        return code, json.loads(out), err

    def test_a_bad_issues_dir_is_reported_not_crashed_on(self):
        """`doctor` exists to report a broken config; reading `cfg.issues_dir`
        outside the try meant it aborted on one instead (V9)."""
        code, payload, err = self._doctor({"issues_dir": "../../etc"})
        self.assertEqual(code, 3, err)
        self.assertFalse(payload["ready"])
        self.assertIn("issues_config_error", payload["checks"])

    def test_an_undecodable_backlog_is_reported_not_crashed_on(self):
        path = self.root / "docs" / "BACKLOG.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"# B\n\xff\xfe not utf-8\n")
        code, payload, err = self._doctor({"backlog_path": "docs/BACKLOG.md"})
        self.assertEqual(code, 3, err)
        self.assertIn("backlog_config_error", payload["checks"])

    def test_an_over_cap_backlog_reports_unchecked_and_stays_ready(self):
        """`False` there read as "your ledger is broken" for a ledger nobody
        looked at, and made a healthy repo not-ready (V9)."""
        path = self.root / "docs" / "BACKLOG.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        fx.write(path, "%s\n%s\n" % (ANCHOR, "x" * 3_000_000))
        code, payload, err = self._doctor({"backlog_path": "docs/BACKLOG.md"})
        self.assertEqual(payload["checks"]["backlog_anchor_present"],
                         "unchecked")
        self.assertTrue(payload["ready"], err)
        self.assertEqual(code, 0)

    def test_the_writability_probe_does_not_follow_a_planted_symlink(self):
        """V-08 — the last predictable-name write in the engine."""
        cfg = fx.load_cfg(self.root)
        feedback = Path(cfg.feedback_dir)
        feedback.mkdir(parents=True, exist_ok=True)
        victim = self.root / "VICTIM"
        os.symlink(str(victim), str(feedback / ".doctor-probe"))
        code, payload, _ = self._doctor()
        self.assertTrue(payload["checks"]["feedback_dir_writable"])
        self.assertFalse(victim.exists(),
                         "doctor wrote through a planted symlink")

    def test_inbox_depth_is_reported(self):
        cfg = fx.load_cfg(self.root)
        inbox_dir = Path(cfg.inbox_dir)
        inbox_dir.mkdir(parents=True, exist_ok=True)
        for i in range(3):
            fx.write(inbox_dir / ("fnd-20260730-00000%d-abcdefab.json" % i),
                     json.dumps({"v": 1, "finding_id": "fnd-%d" % i,
                                 "fingerprint": "abcdefab" * 2,
                                 "status": "new"}))
        _, payload, _ = self._doctor()
        self.assertEqual(payload["checks"]["inbox_depth"], 3)


class TestProvisionalIdOnBothPaths(unittest.TestCase):
    """V10 — JSON-only, and absent from the defect path entirely."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "BACKLOG.md", fx.BACKLOG_INDEX_FIXTURE)
        fx.write(self.root / "docs" / "KNOWN_ISSUES.md", fx.INDEX_FIXTURE)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        code, out, err = fx.run_cli(
            ["--repo-root", str(self.root), "collect", "--source", "workflow",
             "--kind", "gate-failure", "--component", "demo",
             "--message", "boom", "--json"])
        self.assertEqual(code, 0, err)
        self.fid = json.loads(out)["finding"]["finding_id"]
        self.body = fx.write(self.root / "body.md", "Signal.\n")

    def _dry_run(self, classification, extra=()):
        return fx.run_cli(["--repo-root", str(self.root), "file", "--finding",
                           self.fid, "--as", classification, "--title", "T",
                           "--body-file", str(self.body), "--dry-run", *extra])

    def test_json_and_human_both_mark_the_id_provisional(self):
        for classification, extra in (("work-item", ()),
                                      ("defect", ("--category", "robustness"))):
            with self.subTest(classification=classification):
                code, human, err = self._dry_run(classification, extra)
                self.assertEqual(code, 0, err)
                self.assertIn("PROVISIONAL", human)
                code, out, err = self._dry_run(classification,
                                               extra + ("--json",))
                self.assertEqual(code, 0, err)
                self.assertTrue(json.loads(out)["result"]["provisional_id"])


# --- V17: the stranded finding ----------------------------------------------

class TestConsumeFailureIsRecoverable(unittest.TestCase):
    """V17 — a failed move after a good ledger write exited 4 forever."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        fx.write(self.root / "docs" / "BACKLOG.md", fx.BACKLOG_INDEX_FIXTURE)
        fx.write(self.root / "docs" / "feedback" / "config.json",
                 json.dumps({"v": 1, "backlog_path": "docs/BACKLOG.md"}))
        self.body = fx.write(self.root / "body.md", "Signal.\n")

    def _collect(self):
        code, out, err = fx.run_cli(
            ["--repo-root", str(self.root), "collect", "--source", "workflow",
             "--kind", "gate-failure", "--component", "demo",
             "--message", "boom", "--json"])
        self.assertEqual(code, 0, err)
        return json.loads(out)["finding"]["finding_id"]

    def test_the_error_names_the_written_record_and_the_recovery(self):
        fid = self._collect()
        import run_feedback

        with mock.patch.object(run_feedback.inbox, "consume",
                              side_effect=OSError("read-only filesystem")):
            code, _, err = fx.run_cli(
                ["--repo-root", str(self.root), "file", "--finding", fid,
                 "--as", "work-item", "--title", "T",
                 "--body-file", str(self.body)])
        self.assertEqual(code, 4)
        self.assertIn("could not be moved out", err)
        self.assertIn("docs/backlog", err)
        self.assertIn("marked filed in place", err)

    def test_a_retry_reports_already_filed_instead_of_exiting_4_forever(self):
        fid = self._collect()
        import run_feedback

        with mock.patch.object(run_feedback.inbox, "consume",
                              side_effect=OSError("read-only filesystem")):
            fx.run_cli(["--repo-root", str(self.root), "file", "--finding", fid,
                        "--as", "work-item", "--title", "T",
                        "--body-file", str(self.body)])
        code, _, err = fx.run_cli(
            ["--repo-root", str(self.root), "file", "--finding", fid,
             "--as", "work-item", "--title", "T",
             "--body-file", str(self.body)])
        self.assertEqual(code, 2, err)
        self.assertIn("already filed", err)


if __name__ == "__main__":
    unittest.main()
