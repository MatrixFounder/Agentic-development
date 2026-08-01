"""Tests for `check_positional_refs.py` (documentation-standards §4.1).

The fixture builds a throwaway git repository so no assertion depends on the
content of this repository, which changes every task.
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPT = PROJECT_ROOT / ".agent/skills/documentation-standards/scripts/check_positional_refs.py"

spec = importlib.util.spec_from_file_location("check_positional_refs", SCRIPT)
cpr = importlib.util.module_from_spec(spec)
sys.modules["check_positional_refs"] = cpr
spec.loader.exec_module(cpr)


def _git(root, *args):
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )


class TestExtractRefs(unittest.TestCase):
    """Reference extraction: what counts as a positional reference."""

    def test_code_span_reference(self):
        refs = cpr.extract_refs("d.md", "see `src/app.py:42` for detail")
        self.assertEqual(len(refs), 1)
        self.assertEqual((refs[0].path, refs[0].line, refs[0].pin), ("src/app.py", 42, None))

    def test_range_reference(self):
        refs = cpr.extract_refs("d.md", "`src/app.py:10-25`")
        self.assertEqual((refs[0].line, refs[0].end), (10, 25))

    def test_markdown_link_anchor(self):
        refs = cpr.extract_refs("d.md", "[app](src/app.py#L42-L51)")
        self.assertEqual((refs[0].path, refs[0].line, refs[0].end), ("src/app.py", 42, 51))

    def test_explicit_revision_pin(self):
        refs = cpr.extract_refs("d.md", "`src/app.py:42@v3.21.10`")
        self.assertEqual(refs[0].pin, "v3.21.10")

    def test_prose_revision_pin_on_same_line(self):
        refs = cpr.extract_refs("d.md", "verified at v3.19.1: `src/app.py:42`")
        self.assertEqual(refs[0].pin, "v3.19.1")

    def test_prose_pin_accepts_sha(self):
        refs = cpr.extract_refs("d.md", "as of 4f2a91c the line `src/app.py:42` held")
        self.assertEqual(refs[0].pin, "4f2a91c")

    def test_prose_pin_works_in_a_non_english_document(self):
        # The pin matches the revision token, not an English preposition: anchoring on
        # "at / as of" made the documented escape hatch inert in every other language.
        refs = cpr.extract_refs("d.md", "`src/types.ts:101-106` на `985f843`")
        self.assertEqual(refs[0].pin, "985f843")

    def test_bare_version_is_not_a_pin(self):
        # Version strings are ordinary subject matter ("bump to v3.4"); pinning on them
        # would silently exempt live references. Versions need a cue or the @rev suffix.
        self.assertIsNone(cpr.extract_refs("d.md", "bump to v3.4 in `SKILLS.md:87`")[0].pin)
        self.assertIsNone(cpr.extract_refs("d.md", "`a.py:1` по состоянию на v3.21.11")[0].pin)

    def test_explicit_suffix_is_the_language_neutral_form_for_versions(self):
        refs = cpr.extract_refs("d.md", "по состоянию на `a.py:1@v3.21.11`")
        self.assertEqual(refs[0].pin, "v3.21.11")

    def test_head_pin_works_in_any_language(self):
        self.assertEqual(cpr.extract_refs("d.md", "`a.py:1` wie in HEAD~2")[0].pin, "HEAD~2")

    def test_prose_pin_rejects_hex_legal_words(self):
        # "deadbeef" is hex-legal but has no digit, so it is a word, not a revision.
        refs = cpr.extract_refs("d.md", "`src/app.py:101` returns deadbeef")
        self.assertIsNone(refs[0].pin)

    def test_the_english_word_head_is_not_a_pin(self):
        # Matching HEAD case-insensitively exempted every line containing "head" — a
        # silent miss, and the worst outcome this tool can produce.
        for line in ("the head of the list is `a.py:1`",
                     "Head over to `a.py:1` for details",
                     "the header in `a.py:1`"):
            self.assertIsNone(cpr.extract_refs("d.md", line)[0].pin, line)

    def test_uppercase_head_still_pins(self):
        self.assertEqual(cpr.extract_refs("d.md", "`a.py:1` at HEAD")[0].pin, "HEAD")

    def test_unmarked_hex_is_not_a_pin(self):
        # CSS colours, build ids and digests are hex-shaped and are not revisions.
        for line in ("`a.py:1` colour #deadb33f in the theme",
                     "`a.py:1` id 1234567890abcdef",
                     "`a.py:1` build cafe1234",
                     "`a.py:1` see https://host/x/commit/985f843abc"):
            self.assertIsNone(cpr.extract_refs("d.md", line)[0].pin, line)

    def test_backticks_are_what_make_a_bare_hash_a_pin(self):
        self.assertIsNone(cpr.extract_refs("d.md", "`a.py:1` rolled back to 985f843")[0].pin)
        self.assertEqual(cpr.extract_refs("d.md", "`a.py:1` откат на `985f843`")[0].pin, "985f843")

    def test_pin_survives_a_sentence_ending_period(self):
        # A sentence that ends with the hash is ordinary writing; rejecting it made the
        # documented mechanism fail in the most natural phrasing.
        self.assertEqual(cpr.extract_refs("d.md", "`a.py:1` as of 985f843.")[0].pin, "985f843")

    def test_prose_pin_rejects_plain_quantity(self):
        # A quantity is not a commit hash; treating it as one silently skips the check.
        refs = cpr.extract_refs("d.md", "measured per 1000000 requests `src/app.py:42`")
        self.assertIsNone(refs[0].pin)

    def test_prose_pin_rejects_bare_date(self):
        refs = cpr.extract_refs("d.md", "at 20260731 the file `src/app.py:42` was fine")
        self.assertIsNone(refs[0].pin)

    def test_prose_pin_ignored_when_line_has_several_refs(self):
        # Prose cannot say WHICH reference it pins, so it must pin none of them.
        refs = cpr.extract_refs("d.md", "at v1.0 `a.py:1` differed from `b.py:2`")
        self.assertEqual([r.pin for r in refs], [None, None])

    def test_explicit_pin_still_applies_among_several_refs(self):
        refs = cpr.extract_refs("d.md", "`a.py:1@v1.0` and `b.py:2`")
        self.assertEqual([r.pin for r in refs], ["v1.0", None])

    def test_the_single_reference_guard_covers_ordinals_too(self):
        # The guard existed for path:line references but not for ordinals, so one hash
        # exempted every ordinal on the line.
        line = "на `985f843` `demo` §1 и `demo` §2"
        self.assertEqual([r.pin for r in cpr.extract_ordinal_refs("d.md", line)], [None, None])

    def test_the_guard_counts_both_kinds_of_reference_together(self):
        line = "на `985f843` `a.py:1` и `demo` §2"
        self.assertIsNone(cpr.extract_refs("d.md", line)[0].pin)
        self.assertIsNone(cpr.extract_ordinal_refs("d.md", line)[0].pin)

    def test_a_lone_ordinal_still_accepts_a_prose_pin(self):
        line = "на `985f843` `demo` §2"
        self.assertEqual(cpr.extract_ordinal_refs("d.md", line)[0].pin, "985f843")

    def test_descending_range_keeps_both_endpoints(self):
        # range(6, 4) is empty, so "§5-§3" used to collapse to a single ordinal.
        got = [r.ordinal for r in cpr.extract_ordinal_refs("d.md", "`demo` §5-§3")]
        self.assertEqual(got, ["5", "3"])

    def test_refs_are_returned_in_column_order(self):
        refs = cpr.extract_refs("d.md", "[x](z.py#L9) then `a.py:1`")
        self.assertEqual([r.path for r in refs], ["z.py", "a.py"])

    def test_host_port_is_not_a_reference(self):
        self.assertEqual(cpr.extract_refs("d.md", "connect to `example.com:8080`"), [])

    def test_plain_prose_colon_number_is_not_a_reference(self):
        self.assertEqual(cpr.extract_refs("d.md", "see section 4.1:42 below"), [])


class TestSuffixIndex(unittest.TestCase):
    """Shorthand resolution and ambiguity detection."""

    def test_indexes_every_suffix(self):
        index = cpr.build_suffix_index(["docs/reviews/audit.md"])
        self.assertIn("audit.md", index)
        self.assertIn("reviews/audit.md", index)
        self.assertIn("docs/reviews/audit.md", index)

    def test_collision_keeps_all_candidates(self):
        index = cpr.build_suffix_index(["a/notes.md", "b/notes.md"])
        self.assertEqual(len(index["notes.md"]), 2)


class TestClassificationOnRepo(unittest.TestCase):
    """End-to-end classification against a real throwaway repository."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls._tmp.name)
        root = cls.root

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@example.com")
        _git(root, "config", "user.name", "Test")

        (root / "src").mkdir()
        (root / "a").mkdir()
        (root / "b").mkdir()
        (root / "docs").mkdir()
        (root / "src/app.py").write_text("\n".join(f"line {i}" for i in range(1, 6)) + "\n")
        (root / "a/notes.md").write_text("a\n")
        (root / "b/notes.md").write_text("b\n")
        (root / "docs/stable.md").write_text("untouched\n")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "init")

        # The current "change": src/app.py is edited and a new document is added.
        (root / "src/app.py").write_text(
            "inserted\n" + "\n".join(f"line {i}" for i in range(1, 6)) + "\n"
        )
        (root / "docs/new.md").write_text(
            "drift: `src/app.py:3`\n"
            "range past eof: `src/app.py:99`\n"
            "missing: `src/gone.py:1`\n"
            "ambiguous: `notes.md:1`\n"
            "pinned: `src/app.py:99@v1.0`\n"
            "stable target: `docs/stable.md:1`\n"
            "zero line: `src/app.py:0`\n"
            "descending range: `src/app.py:4-2`\n"
            "escape: `../../../etc/passwd.py:1`\n"
        )
        cls.report = cpr.run(root, "HEAD", None)
        cls.findings = cls.report.findings
        cls.by_kind = {}
        for f in cls.findings:
            cls.by_kind.setdefault(f.kind, []).append(f)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_drift_suspect_reported_with_target_line(self):
        drift = self.by_kind["DRIFT_SUSPECT"]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0].ref.line, 3)
        # The insertion shifted content: line 3 now holds what used to be line 2.
        self.assertEqual(drift[0].target_text, "line 2")
        self.assertEqual(drift[0].severity, "warning")

    def test_line_past_end_of_file_is_an_error(self):
        oor = [f for f in self.by_kind["OUT_OF_RANGE"] if f.ref.line == 99]
        self.assertEqual(len(oor), 1)
        self.assertEqual(oor[0].severity, "error")

    def test_line_zero_is_an_error_not_the_last_line(self):
        # lines[0 - 1] would silently resolve to the FINAL line of the file.
        zero = [f for f in self.by_kind["OUT_OF_RANGE"] if f.ref.line == 0]
        self.assertEqual(len(zero), 1)
        self.assertIsNone(zero[0].target_text)

    def test_descending_range_is_an_error(self):
        desc = [f for f in self.by_kind["OUT_OF_RANGE"] if f.ref.end == 2]
        self.assertEqual(len(desc), 1)

    def test_path_escaping_the_root_is_refused_but_only_warned_about(self):
        # Refused a read (the security boundary) yet reported as a warning: cross-repository
        # references are real here, so an error would fail correct documents.
        esc = self.by_kind["ESCAPES_ROOT"]
        self.assertEqual(len(esc), 1)
        self.assertEqual(esc[0].severity, "warning")
        self.assertIsNone(esc[0].target)

    def test_unresolvable_path_is_an_error(self):
        unres = self.by_kind["UNRESOLVABLE"]
        self.assertEqual(len(unres), 1)
        self.assertEqual(unres[0].ref.path, "src/gone.py")
        self.assertEqual(unres[0].severity, "error")

    def test_ambiguous_shorthand_is_an_error_listing_candidates(self):
        amb = self.by_kind["AMBIGUOUS"]
        self.assertEqual(len(amb), 1)
        self.assertEqual(amb[0].candidates, ["a/notes.md", "b/notes.md"])
        self.assertEqual(amb[0].severity, "error")

    def test_pinned_reference_is_skipped(self):
        # `src/app.py:99@v1.0` is past EOF but pinned, so it is a claim about v1.0.
        pinned = [f for f in self.findings if f.ref.pin]
        self.assertEqual(pinned, [])

    def test_unchanged_target_produces_no_finding(self):
        stable = [f for f in self.findings if f.ref.path == "docs/stable.md"]
        self.assertEqual(stable, [])

    def test_unchanged_document_is_out_of_diff_scope(self):
        scanned = {f.ref.doc for f in self.findings}
        self.assertEqual(scanned, {"docs/new.md"})


class TestExitCodes(unittest.TestCase):
    """CLI contract: advisory by default, strict on request."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@example.com")
        _git(self.root, "config", "user.name", "Test")
        (self.root / "src").mkdir()
        (self.root / "src/app.py").write_text("a\nb\nc\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "init")

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, *extra):
        # Swallow the CLI's own stdout: unittest does not capture it, and the report
        # would otherwise interleave with the local runner's progress output.
        with contextlib.redirect_stdout(io.StringIO()):
            return cpr.main(["--root", str(self.root), *extra])

    def test_clean_change_exits_zero(self):
        (self.root / "note.md").write_text("nominal ref to `src/app.py` only\n")
        self.assertEqual(self._run(), 0)

    def test_warning_only_exits_zero_by_default(self):
        (self.root / "src/app.py").write_text("inserted\na\nb\nc\n")
        (self.root / "note.md").write_text("`src/app.py:2`\n")
        self.assertEqual(self._run(), 0)

    def test_warning_only_exits_one_under_strict(self):
        (self.root / "src/app.py").write_text("inserted\na\nb\nc\n")
        (self.root / "note.md").write_text("`src/app.py:2`\n")
        self.assertEqual(self._run("--strict"), 1)

    def test_error_exits_one(self):
        (self.root / "note.md").write_text("`src/app.py:900`\n")
        self.assertEqual(self._run(), 1)

    def test_non_repository_exits_two(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertEqual(cpr.main(["--root", plain]), 2)

    def test_unknown_base_exits_two_not_zero(self):
        # A mistyped --base must never be indistinguishable from a clean review.
        (self.root / "src/app.py").write_text("inserted\na\nb\nc\n")
        (self.root / "note.md").write_text("`src/app.py:2`\n")
        self.assertEqual(self._run("--base", "no-such-ref"), 2)

    def test_missing_git_executable_exits_two(self):
        with unittest.mock.patch(
            "check_positional_refs.subprocess.run", side_effect=FileNotFoundError
        ):
            self.assertEqual(self._run(), 2)

    def test_json_mode_reports_scope_alongside_findings(self):
        (self.root / "src/app.py").write_text("inserted\na\nb\nc\n")
        (self.root / "note.md").write_text("`src/app.py:2`\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cpr.main(["--root", str(self.root), "--json"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["doc_count"], 1)
        self.assertEqual(payload["ref_count"], 1)
        self.assertEqual(payload["findings"][0]["kind"], "DRIFT_SUSPECT")

    def test_summary_counts_ordinals_as_references(self):
        # An ordinal finding used to be reported "across 0 reference(s)".
        (self.root / ".agent/skills/demo").mkdir(parents=True)
        (self.root / ".agent/skills/demo/SKILL.md").write_text("# D\n## 1. One\n")
        (self.root / "note.md").write_text("`demo` §9\n")
        report = cpr.run(self.root, "HEAD", None)
        self.assertEqual((report.ref_count, report.ordinal_count), (0, 1))
        self.assertEqual(report.total_refs, 1)
        self.assertIn("0 path:line + 1 ordinal", cpr.format_text(report))


class TestScopeHonesty(unittest.TestCase):
    """An empty or unqueryable scope must never read as a pass."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@example.com")
        _git(self.root, "config", "user.name", "Test")

    def tearDown(self):
        self._tmp.cleanup()

    def test_empty_scope_does_not_claim_verification(self):
        (self.root / "a.py").write_text("x\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "init")
        report = cpr.run(self.root, "HEAD", None)
        text = cpr.format_text(report)
        self.assertEqual(report.doc_count, 0)
        self.assertIn("NOTHING CHECKED", text)
        self.assertNotIn("OK:", text)

    def test_repository_without_commits_is_scanned_and_noted(self):
        (self.root / "d.md").write_text("`a.py:1`\n")
        report = cpr.run(self.root, "HEAD", None)
        self.assertEqual(report.doc_count, 1)
        self.assertTrue(any("no tracked files" in n for n in report.notes))
        self.assertEqual(report.findings[0].kind, "UNRESOLVABLE")
        self.assertIn("nothing is tracked", report.findings[0].detail)

    def test_all_mode_scans_outside_the_diff(self):
        (self.root / "docs").mkdir()
        (self.root / "src").mkdir()
        (self.root / "src/app.py").write_text("a\nb\n")
        (self.root / "docs/old.md").write_text("`src/app.py:99`\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "init")
        self.assertEqual(cpr.run(self.root, "HEAD", None).doc_count, 0)
        report = cpr.run(self.root, "HEAD", ["docs"])
        self.assertEqual(report.doc_count, 1)
        self.assertEqual(report.findings[0].kind, "OUT_OF_RANGE")


class TestOrdinalParsing(unittest.TestCase):
    """What a document declares as a section ordinal."""

    def test_numbered_headings_are_declared(self):
        got = cpr.parse_ordinals(["## 4. Paths", "### 4.1. Positional", "text"])
        self.assertEqual(got, {"4", "4.1"})

    def test_range_heading_declares_every_ordinal_in_it(self):
        got = cpr.parse_ordinals(["## 5-10. Extended Sections"])
        self.assertEqual(got, {"5", "6", "7", "8", "9", "10"})

    def test_list_items_declare_sub_ordinals(self):
        # `run-feedback` §7.1 addresses a list item under an UNNUMBERED sub-heading.
        got = cpr.parse_ordinals(["## 7. Instructions", "### Triage", "1. one", "2. two"])
        self.assertEqual(got, {"7", "7.1", "7.2"})

    def test_blockquoted_list_items_count(self):
        # The orchestrator's prime directives are a quoted list; §1.3 addresses item 3.
        got = cpr.parse_ordinals(["## 1. PRIME DIRECTIVE", "> 1. a", "> 2. b", "> 3. c"])
        self.assertEqual(got, {"1", "1.1", "1.2", "1.3"})

    def test_nested_list_items_do_not_declare_ordinals(self):
        got = cpr.parse_ordinals(["## 2. X", "1. top", "    1. nested"])
        self.assertEqual(got, {"2", "2.1"})


class TestOrdinalExtraction(unittest.TestCase):
    """Which ordinals are in scope: only those naming their target adjacently."""

    def _paths(self, line):
        return [(r.path, r.ordinal) for r in cpr.extract_ordinal_refs("d.md", line)]

    def test_skill_name_antecedent(self):
        self.assertEqual(self._paths("see `developer-guidelines` §1.5"),
                         [("developer-guidelines", "1.5")])

    def test_bare_skill_name_antecedent(self):
        self.assertEqual(self._paths("per skill-safe-commands §2"), [("skill-safe-commands", "2")])

    def test_repo_path_antecedent(self):
        self.assertEqual(self._paths("`System/Agents/01_orchestrator.md` §5.1"),
                         [("System/Agents/01_orchestrator.md", "5.1")])

    def test_markdown_link_antecedent(self):
        self.assertEqual(self._paths("[x](docs/ARCHITECTURE.md) §9.2"),
                         [("docs/ARCHITECTURE.md", "9.2")])

    def test_skill_md_suffix_is_absorbed(self):
        self.assertEqual(self._paths("`run-feedback` SKILL.md §7"), [("run-feedback", "7")])

    def test_bare_ordinal_is_out_of_scope(self):
        self.assertEqual(self._paths("see §4.2 for the resolver"), [])

    def test_external_specification_is_denylisted(self):
        self.assertEqual(self._paths("CommonMark §4.5 defines this"), [])

    def test_cross_repository_reference_is_denylisted(self):
        self.assertEqual(self._paths("Universal-skills CLAUDE.md §2 covers it"), [])

    def test_range_chain_is_expanded(self):
        self.assertEqual(self._paths("`skill-creator` §1-§3"),
                         [("skill-creator", "1"), ("skill-creator", "2"), ("skill-creator", "3")])

    def test_separated_chain_inherits_the_target(self):
        self.assertEqual(self._paths("`skill-creator` §2 and §5"),
                         [("skill-creator", "2"), ("skill-creator", "5")])


class TestOrdinalClassification(unittest.TestCase):
    """An ordinal is a finding only when the target provably does not declare it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".agent/skills/demo").mkdir(parents=True)
        (self.root / ".agent/skills/demo/SKILL.md").write_text(
            "# Demo\n## 1. One\n## 2. Two\n### 2.1. Sub\n"
        )
        (self.root / ".agent/skills/unnumbered").mkdir(parents=True)
        (self.root / ".agent/skills/unnumbered/SKILL.md").write_text("# U\n## Overview\n")
        self.caches = ({}, {})

    def tearDown(self):
        self._tmp.cleanup()

    def _check(self, line):
        refs = cpr.extract_ordinal_refs("d.md", line)
        return [cpr.classify_ordinal(r, self.root, *self.caches) for r in refs]

    def test_existing_ordinal_passes(self):
        self.assertEqual(self._check("`demo` §2.1"), [(None, "checked")])

    def test_missing_ordinal_is_an_error(self):
        [(finding, outcome)] = self._check("`demo` §9")
        self.assertEqual(finding.kind, "ORDINAL_MISSING")
        self.assertEqual(finding.severity, "error")
        self.assertEqual(outcome, "checked")

    def test_target_numbering_nothing_is_unverifiable_not_wrong(self):
        # An ADR heading like "## D1 — Decision" declares no ordinal; §3 into it is
        # unverifiable, and the report must say so rather than imply a pass.
        self.assertEqual(self._check("`unnumbered` §3"), [(None, "unnumbered-target")])

    def test_unknown_antecedent_is_skipped(self):
        self.assertEqual(self._check("`no-such-skill` §1"), [(None, "unknown-target")])

    def test_pinned_ordinal_is_skipped(self):
        self.assertEqual(self._check("at v1.0 `demo` §9"), [(None, "pinned")])

    def test_markdown_link_target_is_actually_checked(self):
        # All three antecedent forms must reach classification, not just skill names.
        (self.root / "docs").mkdir()
        (self.root / "docs/adr.md").write_text("# A\n## 1. One\n")
        [(finding, outcome)] = self._check("[ADR](docs/adr.md) §9")
        self.assertEqual(outcome, "checked")
        self.assertEqual(finding.kind, "ORDINAL_MISSING")

    def test_backticked_path_target_is_actually_checked(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/adr.md").write_text("# A\n## 1. One\n")
        [(finding, outcome)] = self._check("`docs/adr.md` §9")
        self.assertEqual(outcome, "checked")
        self.assertEqual(finding.kind, "ORDINAL_MISSING")


class TestOrdinalScopeReporting(unittest.TestCase):
    """The report must distinguish what it checked, what failed, and what it never saw."""

    def test_scope_line_names_each_skip_reason(self):
        note = cpr.describe_ordinal_scope(
            {"checked": 3, "unknown-target": 2, "unnumbered-target": 1, "pinned": 1}, 0, 5
        )
        self.assertIn("3 checked (3 passed, 0 failed)", note)
        self.assertIn("2 skipped (target is not a document in this repository)", note)
        self.assertIn("1 skipped (target declares no numbered sections)", note)
        self.assertIn("1 skipped (pinned to a revision)", note)
        self.assertIn("5 NOT examined", note)

    def test_failed_ordinals_are_not_reported_as_passed(self):
        # "3 verified" while one of them is an error is the overclaim this line exists
        # to prevent.
        note = cpr.describe_ordinal_scope({"checked": 3}, 1, 0)
        self.assertIn("3 checked (2 passed, 1 failed)", note)

    def test_scope_line_omits_absent_reasons(self):
        note = cpr.describe_ordinal_scope({"checked": 2}, 0, 0)
        self.assertIn("2 checked", note)
        self.assertNotIn("skipped", note)
        self.assertNotIn("NOT examined", note)

    def test_unknown_outcome_names_are_not_dropped(self):
        # A new outcome must widen the tally, not silently shrink it.
        note = cpr.describe_ordinal_scope({"checked": 1, "brand-new-outcome": 4}, 0, 0)
        self.assertIn("4 brand-new-outcome", note)


class TestScopeHonestyInOutput(unittest.TestCase):
    """The headline must not claim verification it did not perform."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@example.com")
        _git(self.root, "config", "user.name", "Test")
        (self.root / "src").mkdir()
        (self.root / "src/app.py").write_text("a\nb\nc\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "init")

    def tearDown(self):
        self._tmp.cleanup()

    def test_pinned_references_are_excluded_from_the_resolve_claim(self):
        (self.root / "d.md").write_text("`src/app.py:99@v1.0`\n")
        report = cpr.run(self.root, "HEAD", None)
        self.assertEqual((report.total_refs, report.pinned_count), (1, 1))
        self.assertEqual(report.examined_refs, 0)
        text = cpr.format_text(report)
        self.assertIn("0 of 1", text)
        self.assertIn("1 pinned, not checked", text)

    def test_a_document_of_only_bare_ordinals_still_reports_its_scope(self):
        # Reporting a clean OK with no mention of the ordinals it ignored is the exact
        # overclaim the scope note exists to prevent.
        (self.root / "d.md").write_text("see §4.2 and TASK §4 for the rule\n")
        report = cpr.run(self.root, "HEAD", None)
        self.assertEqual(report.ordinal_count, 0)
        self.assertEqual(report.ordinal_out_of_scope, 2)
        self.assertIn("2 NOT examined", cpr.format_text(report))

    def test_external_specification_ordinals_count_as_not_examined(self):
        (self.root / "d.md").write_text("CommonMark §4.5 defines this\n")
        report = cpr.run(self.root, "HEAD", None)
        self.assertEqual(report.ordinal_out_of_scope, 1)


class TestSafeJoin(unittest.TestCase):
    """Path containment: a document must not steer the tool outside the repository."""

    def setUp(self):
        self.root = Path("/repo")

    def test_plain_relative_path_is_joined(self):
        self.assertEqual(cpr.safe_join(self.root, "src/app.py"), Path("/repo/src/app.py"))

    def test_interior_dotdot_is_normalised(self):
        self.assertEqual(cpr.safe_join(self.root, "src/../a.py"), Path("/repo/a.py"))

    def test_traversal_is_refused(self):
        self.assertIsNone(cpr.safe_join(self.root, "../../../etc/passwd.py"))

    def test_absolute_path_is_refused(self):
        self.assertIsNone(cpr.safe_join(self.root, "/etc/passwd.py"))


if __name__ == "__main__":
    unittest.main()
