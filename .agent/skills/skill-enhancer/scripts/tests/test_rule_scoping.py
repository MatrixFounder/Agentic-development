#!/usr/bin/env python3
"""Rule scoping for `analyze_gaps.py` (WI-033).

Three rules used to fire on documentation that is correct as written:

* `[Lazy]` read `[--page-size letter|a4|legal]` as an unfilled template slot.
  It is CLI usage notation where the brackets mean "optional argument"; filling
  it in makes every documented command wrong.
* `[Anti-Pattern]` read `/tmp/invoice.pdf` in Validation Evidence as a path to
  be made relative. It is a reproducible scratch path, and relative is wrong
  there. It also read the markdown escape `x\\_1` as a Windows path.
* `[Language]` read "weasyprint **can** find its native libraries" — a
  statement about a tool's capability — as a weak instruction.

Measured 2026-09-02 across the 22 skills carrying a `SKILL.md`: 34
`Anti-Pattern` occurrences, of which 0 named a machine; 221 bracket
placeholders, of which 199 were CLI usage notation and 19 were mermaid node
labels.

Every test below pins BOTH halves: what the narrowed rule now ignores, and the
defect it must still catch. A narrowing with no `must_still_catch` case is a
rule deletion wearing a rule's name.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import analyze_gaps  # noqa: E402

ANALYZE = SCRIPTS / "analyze_gaps.py"


def write_skill(root, name, body, *, description=None, examples=True,
                extra_dirs=()):
    """A minimal skill that is otherwise clean, so a test sees only its own rule."""
    skill = Path(root) / name
    skill.mkdir(parents=True)
    if examples:
        (skill / "examples").mkdir()
        (skill / "examples" / "usage.md").write_text(
            "# Example\n\nA worked example long enough to pass the size floor.\n",
            encoding="utf-8")
    for extra in extra_dirs:
        (skill / extra).mkdir()
    description = description or "Use when exercising one analyze_gaps rule."
    head = textwrap.dedent(f"""\
        ---
        name: {name}
        description: {description}
        tier: 2
        version: 1.0
        ---
        # {name}

        ## Red Flags
        - "I'll skip this" -> **WRONG**. Read the rule first.

        ## Rationalization Table
        | Agent Excuse | Reality |
        | :--- | :--- |
        | "Close enough" | It is not. |
        """)
    (skill / "SKILL.md").write_text(head + "\n" + body + "\n", encoding="utf-8")
    return skill


def run_json(skill_dir, *args, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(ANALYZE), str(skill_dir), "--json", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd or Path(skill_dir).parent),
    )
    return proc.returncode, json.loads(proc.stdout)


def gaps_matching(report, label):
    return [g for g in report["gaps"] if g.startswith(f"[{label}]")]


def advisories_matching(report, label):
    return [a for a in report["advisories"] if a.startswith(f"[{label}]")]


class TestMaskCode(unittest.TestCase):
    """Code is not prose. Masking must not move anything."""

    def test_a_fenced_block_is_blanked_and_the_line_count_is_kept(self):
        body = "before\n```bash\nrm -rf [everything here]\n```\nafter"
        masked = analyze_gaps.mask_code(body)
        self.assertEqual(len(masked.splitlines()), len(body.splitlines()))
        self.assertNotIn("everything here", masked)
        self.assertIn("before", masked)
        self.assertIn("after", masked)

    def test_a_tilde_fence_closes_on_its_own_marker(self):
        body = "~~~text\n[a placeholder]\n~~~\n[a real one]"
        masked = analyze_gaps.mask_code(body)
        self.assertNotIn("a placeholder", masked)
        self.assertIn("a real one", masked)

    def test_an_inline_span_is_blanked_in_place(self):
        body = "Pass `--page-size [letter|a4]` to the script."
        masked = analyze_gaps.mask_code(body)
        self.assertEqual(len(masked), len(body))
        self.assertNotIn("letter", masked)
        self.assertTrue(masked.startswith("Pass "))
        self.assertTrue(masked.rstrip().endswith("to the script."))

    def test_an_unopened_fence_does_not_swallow_the_rest_of_the_file(self):
        body = "```\ncode\n```\nprose [with a slot in it]"
        masked = analyze_gaps.mask_code(body)
        self.assertIn("with a slot in it", masked)


class TestAbsolutePathScoping(unittest.TestCase):
    """Flag a path that names one machine; leave a portable one alone."""

    MACHINE = ["/Users/alice/dev/out.docx", "/home/builder/skills/x.py",
               "/Volumes/Backup/report.pdf", "/mnt/data/fixture.xlsx",
               "/root/.config/tool.json", "/srv/www/customer-x/in.docx",
               "/export/home/bob/deck.pptx", "/cygdrive/c/Users/me/out.docx"]
    PORTABLE = ["/tmp/invoice.pdf", "/dev/null", "/usr/local/lib/thing.so",
                "/etc/hosts", "/var/log/run.log"]
    # Stated false negatives of the first-segment denylist. Pinned so the cost
    # stays visible: if a later change makes one of these fire, that is a
    # deliberate widening and this list moves, it does not quietly disagree.
    KNOWN_FALSE_NEGATIVES = [
        "/opt/homebrew/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/var/folders/xy/abc/T/build.pdf",
        "/private/tmp/claude-501/session/out.pdf",
    ]

    def test_the_denylist_s_false_negatives_are_the_documented_ones(self):
        for hit in self.KNOWN_FALSE_NEGATIVES:
            with self.subTest(hit=hit):
                self.assertFalse(analyze_gaps.is_machine_specific_path(hit))

    def test_every_machine_path_on_a_line_is_reported_not_just_the_first(self):
        line = "`pdf_merge.py /Users/alice/a.pdf /tmp/b.pdf /home/bob/c.pdf`"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "multipathskill", f"## Notes\n- {line}\n")
            _, report = run_json(skill)
        hits = gaps_matching(report, "Anti-Pattern")
        self.assertEqual(len(hits), 2, hits)
        self.assertTrue(any("/Users/alice/a.pdf" in h for h in hits))
        self.assertTrue(any("/home/bob/c.pdf" in h for h in hits))

    def test_a_url_on_the_line_does_not_suppress_a_machine_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "urlpathskill", textwrap.dedent("""\
                ## Notes
                Run `fetch.py "https://youtu.be/x" --out /Users/alice/talk.txt`.
                See https://example.com/a/b/c for the format.
                """))
            _, report = run_json(skill)
        hits = gaps_matching(report, "Anti-Pattern")
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("/Users/alice/talk.txt", hits[0])

    def test_a_machine_specific_root_is_still_caught(self):
        for hit in self.MACHINE:
            with self.subTest(hit=hit):
                self.assertTrue(analyze_gaps.is_machine_specific_path(hit))

    def test_a_portable_root_is_not_an_anti_pattern(self):
        for hit in self.PORTABLE:
            with self.subTest(hit=hit):
                self.assertFalse(analyze_gaps.is_machine_specific_path(hit))

    def test_end_to_end_both_halves(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "pathskill", textwrap.dedent("""\
                ## Validation Evidence
                - `python3 scripts/md2pdf.py examples/fixture.md /tmp/out.pdf`
                - the dump lands in /dev/null when discarded

                ## Anti-example
                Read /Users/alice/dev/notes.md before starting.
                """))
            _, report = run_json(skill)
        hits = gaps_matching(report, "Anti-Pattern")
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("/Users/alice/dev/notes.md", hits[0])


class TestWindowsPathScoping(unittest.TestCase):
    """A backslash between two word characters is usually an escape."""

    PATHS = [r"C:\Users\me\out.docx", r"\\server\share\deck.pptx",
             r"scripts\lib\helper.py"]
    NOT_PATHS = [r"write `x\_1`, not x_1", r"use \(x\) for inline math",
                 r"emits `wiki-ingest 1.1.0\n` and exits 0",
                 r"a single a\b separator"]

    def test_a_real_windows_path_is_still_caught(self):
        for line in self.PATHS:
            with self.subTest(line=line):
                self.assertIsNotNone(analyze_gaps._WINDOWS_PATH_RE.search(line))

    def test_an_escape_sequence_is_not_a_path(self):
        for line in self.NOT_PATHS:
            with self.subTest(line=line):
                self.assertIsNone(analyze_gaps._WINDOWS_PATH_RE.search(line))


class TestPlaceholderScoping(unittest.TestCase):
    """`[--flag VALUE]` is usage notation, not an unfilled slot."""

    def test_cli_notation_and_footnotes_are_not_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "notationskill", textwrap.dedent("""\
                ## Script Contract
                - `python3 scripts/md2pdf.py IN.md OUT.pdf [--page-size letter|a4|legal]`
                - Bare notation outside code: [--layout] and [-o OUT.json]

                ## Notes
                The body gets pandoc-style [^fn-1] markers appended.
                """))
            _, report = run_json(skill)
        self.assertEqual(gaps_matching(report, "Lazy"), [])

    def test_an_unfilled_template_slot_is_still_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "slotskill", textwrap.dedent("""\
                ## Instructions
                1. Explain [Why this is wrong] to the user.
                """))
            _, report = run_json(skill)
        hits = gaps_matching(report, "Lazy")
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("Why this is wrong", hits[0])

    def test_a_mermaid_node_label_is_not_a_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "mermaidskill", textwrap.dedent("""\
                ## Flow
                ```mermaid
                graph TD
                    A[Phase 1: Automated Scan] --> B[Generate Report]
                ```
                """))
            _, report = run_json(skill)
        self.assertEqual(gaps_matching(report, "Lazy"), [])


class TestTodoScoping(unittest.TestCase):
    """A TODO marker is a note to self, not the word appearing in a sentence."""

    def test_a_marker_is_still_caught(self):
        for line in ["TODO: write this section", "- TODO", "<!-- TODO -->"]:
            with self.subTest(line=line), tempfile.TemporaryDirectory() as tmp:
                skill = write_skill(tmp, "todoskill", f"## Notes\n{line}\n")
                _, report = run_json(skill)
                hits = gaps_matching(report, "Lazy")
                self.assertTrue(any("TODO" in h for h in hits), report["gaps"])

    def test_prose_about_something_else_s_todo_is_not_a_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "prosetodoskill", textwrap.dedent("""\
                ## Capabilities
                `##` becomes a content slide with TODO placeholder.
                The outline converter emits titles plus TODO bullets.
                Run `obsidian tasks todo format=json` to list open tasks.
                """))
            _, report = run_json(skill)
        self.assertEqual(gaps_matching(report, "Lazy"), [])


class TestLanguageScoping(unittest.TestCase):
    """Weak wording is an instruction problem; the rule must read instructions."""

    def test_questions_negations_and_compounds_are_not_weak_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "prosekill", textwrap.dedent("""\
                ## Interview
                1. What should this skill enable the agent to do?

                ## Notes
                Client-side KaTeX can't be used, so formulas pre-render.
                Mix should-trigger and should-not-trigger trigger queries.
                Pass `--can-fail` to keep going after the first error.
                """))
            _, report = run_json(skill)
        self.assertEqual(advisories_matching(report, "Language"), [])
        self.assertEqual(gaps_matching(report, "Language"), [])

    def test_a_weak_instruction_is_still_reported_as_an_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "weakskill", textwrap.dedent("""\
                ## Instructions
                1. The helper script should be bundled in scripts/.
                """))
            code, report = run_json(skill)
        self.assertEqual(len(advisories_matching(report, "Language")), 1,
                         report["advisories"])
        self.assertEqual(gaps_matching(report, "Language"), [])
        self.assertEqual(code, 0, "an advisory alone must not fail the gate")
        self.assertEqual(report["status"], "passed")

    def test_strict_promotes_an_advisory_to_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "weakstrictskill", textwrap.dedent("""\
                ## Instructions
                1. The helper script should be bundled in scripts/.
                """))
            code, report = run_json(skill, "--strict")
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["advisories"])


class TestReportedLineNumbers(unittest.TestCase):
    """A finding whose line does not resolve is a finding nobody checks."""

    def test_the_reported_line_is_the_file_line_not_the_body_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "lineskill",
                                "## Anti-example\nRead /Users/alice/notes.md first.\n")
            _, report = run_json(skill)
            lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
        hit = gaps_matching(report, "Anti-Pattern")[0]
        reported = int(hit.split(" at line ")[1].split(".")[0])
        self.assertIn("/Users/alice/notes.md", lines[reported - 1])


class TestGateAgreement(unittest.TestCase):
    """Config keys validate_skill.py honours, analyze_gaps.py must honour too."""

    OVERLAY = textwrap.dedent("""\
        validation:
          enforce_cso_prefix: false
          allowed_cso_prefixes:
            - "Use when"
        """)

    def _with_overlay(self, tmp, text):
        rules = Path(tmp) / ".agent" / "rules"
        rules.mkdir(parents=True)
        (rules / "skill_standards.yaml").write_text(text, encoding="utf-8")

    def test_enforce_cso_prefix_false_silences_the_prefix_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._with_overlay(tmp, self.OVERLAY)
            skill = write_skill(tmp, "csoskill", "## Notes\nNothing here.\n",
                                description="DRIVE the running app from the shell.")
            code, report = run_json(skill, cwd=tmp)
        self.assertEqual(gaps_matching(report, "CSO"), [], report["gaps"])
        self.assertEqual(code, 0)

    def test_the_prefix_rule_still_fires_when_enforcement_is_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "csoskill2", "## Notes\nNothing here.\n",
                                description="DRIVE the running app from the shell.")
            code, report = run_json(skill, cwd=tmp)
        self.assertEqual(len(gaps_matching(report, "CSO")), 1, report["gaps"])
        self.assertEqual(code, 1)

    def test_the_two_gates_agree_on_skills_pdf(self):
        """WI-033's trigger: validate_skill.py exited 0 while analyze_gaps.py exited 1."""
        repo = SCRIPTS.parents[2]
        pdf = repo / "skills" / "pdf"
        if not pdf.is_dir():
            self.skipTest("skills/pdf is not in this checkout")
        validate = repo / "skills" / "skill-creator" / "scripts" / "validate_skill.py"
        env = dict(os.environ)
        analyze_rc = subprocess.run(
            [sys.executable, str(ANALYZE), str(pdf)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(repo), env=env).returncode
        validate_rc = subprocess.run(
            [sys.executable, str(validate), str(pdf)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(repo), env=env).returncode
        self.assertEqual(analyze_rc, validate_rc,
                         "the two gates disagree about skills/pdf again")


class TestStructureScoping(unittest.TestCase):
    """A gitignored scratch directory is not part of the skill."""

    def test_a_tracked_non_standard_directory_is_still_caught(self):
        """Reported, at the warning severity validate_skill.py uses."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "dirskill", "## Notes\nNothing.\n",
                                extra_dirs=("workbench",))
            _, report = run_json(skill)
        hits = advisories_matching(report, "Structure")
        self.assertEqual(len(hits), 1, report["advisories"])
        self.assertIn("workbench", hits[0])
        self.assertEqual(gaps_matching(report, "Structure"), [])

    def test_a_gitignored_directory_is_not_a_structure_deviation(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
            (Path(tmp) / ".gitignore").write_text("scratch/\n", encoding="utf-8")
            skill = write_skill(tmp, "ignoredirskill", "## Notes\nNothing.\n",
                                extra_dirs=("scratch",))
            _, report = run_json(skill)
        self.assertEqual(advisories_matching(report, "Structure"), [],
                         report["advisories"])

    def test_a_skill_under_an_ignored_path_still_gets_structure_findings(self):
        """`git check-ignore` says yes to anything under an ignored parent.

        This repo ignores `/.agent/skills/*`, so without the extra check every
        structure finding vanished for the framework skills that live there.
        """
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
            (Path(tmp) / ".gitignore").write_text("hidden/\n", encoding="utf-8")
            (Path(tmp) / "hidden").mkdir()
            skill = write_skill(tmp, "hidden/buriedskill", "## Notes\nNothing.\n",
                                extra_dirs=("workbench",))
            _, report = run_json(skill, cwd=Path(tmp) / "hidden")
        self.assertTrue(advisories_matching(report, "Structure"),
                        "an ignored parent silenced the whole skill")


class TestExecutionPolicyScoping(unittest.TestCase):
    """One finding per missing section, and triggers that mean what they say."""

    def _findings(self, tmp, body, *, with_scripts):
        skill = Path(tmp) / "epskill"
        (skill / "scripts").mkdir(parents=True) if with_scripts else skill.mkdir()
        if with_scripts:
            (skill / "scripts" / "run.py").write_text("print(1)\n", encoding="utf-8")
        return analyze_gaps.collect_execution_policy_findings(str(skill), body, {})

    def test_a_trigger_annotates_the_finding_instead_of_adding_a_second(self):
        body = ("# s\n\nThis skill will delete stale files and overwrite the index.\n"
                "Run `python3 scripts/run.py`.\n")
        with tempfile.TemporaryDirectory() as tmp:
            found = self._findings(tmp, body, with_scripts=True)
        self.assertEqual(len(found), 4, found)
        joined = "\n".join(found)
        self.assertIn("'scripts/' has executable content", joined)
        self.assertIn("mutation wording found (delete, overwrite)", joined)
        self.assertIn("the skill ships scripts/", joined)
        for section in ("Execution Mode", "Script Contract", "Safety Boundaries",
                        "Validation Evidence"):
            self.assertEqual(sum(section in f for f in found), 1,
                             f"{section} reported more than once")

    def test_a_mutation_word_inside_code_is_not_mutation_wording(self):
        body = ("# p\n\n- **Mode**: `prompt-first`\n\n"
                "```bash\nrm -rf out && delete overwrite\n```\n")
        with tempfile.TemporaryDirectory() as tmp:
            found = self._findings(tmp, body, with_scripts=False)
        self.assertNotIn("mutation wording", "\n".join(found))

    def test_prose_about_removing_patterns_is_not_a_file_mutation(self):
        """text-humanizer's `remove` applies to AI patterns in prose."""
        body = "# p\n\n- **Mode**: `prompt-first`\n\nRewrites text to remove AI patterns.\n"
        with tempfile.TemporaryDirectory() as tmp:
            found = self._findings(tmp, body, with_scripts=False)
        # `remove` is still matched as a word -- the heuristic reads prose -- but
        # it can no longer produce a finding of its own, only annotate one.
        self.assertEqual(sum("Safety Boundaries" in f for f in found), 1, found)

    def test_prompt_first_with_no_scripts_is_exempt_from_script_contract(self):
        body = "# p\n\n- **Mode**: `prompt-first`\n\nJust prose.\n"
        with tempfile.TemporaryDirectory() as tmp:
            found = self._findings(tmp, body, with_scripts=False)
        self.assertNotIn("Script Contract", "\n".join(found))

    def test_citing_another_skill_s_scripts_is_not_shipping_scripts(self):
        """obsidian-cli's only `scripts/` match was a path to wiki-ingest's."""
        body = ("# p\n\n- **Mode**: `prompt-first`\n\n"
                "See `skills/wiki-ingest/scripts/wiki_ops.py`.\n")
        with tempfile.TemporaryDirectory() as tmp:
            found = self._findings(tmp, body, with_scripts=False)
        self.assertNotIn("ships scripts/", "\n".join(found))


class TestQuoteStrippingStaysOnOneLine(unittest.TestCase):
    """A quoted span never crosses a line.

    Without the `\\n` exclusion one ordinary apostrophe opened a span that ran to
    the next apostrophe several lines down and blanked everything between.
    Measured before the fix: 14.6% of this repo's body lines went blank, and a
    fixture carrying BOTH an unfilled slot and a TODO reported neither.
    """

    BODY = textwrap.dedent("""\
        ## Instructions
        1. Don't skip the review step.
        2. Explain [Why this is wrong] to the user.
        3. TODO: finish this section.
        4. Record the reviewer's verdict.
        """)

    def test_an_apostrophe_does_not_blind_the_lines_after_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "apostropheskill", self.BODY)
            code, report = run_json(skill)
        hits = gaps_matching(report, "Lazy")
        self.assertEqual(len(hits), 2, report["gaps"])
        self.assertTrue(any("Why this is wrong" in h for h in hits))
        self.assertTrue(any("TODO" in h for h in hits))
        self.assertEqual(code, 1)

    def test_a_quoted_excuse_on_one_line_is_still_stripped(self):
        """The behaviour the stripper exists for must survive the fix."""
        body = '## Red Flags 2\n- "I can just read the files manually" -> **WRONG**.\n'
        self.assertEqual(
            analyze_gaps.strip_quoted(body).count("read the files manually"), 0)

    def test_stripping_preserves_length_and_line_count(self):
        out = analyze_gaps.strip_quoted(self.BODY)
        self.assertEqual(len(out.splitlines()), len(self.BODY.splitlines()))
        for a, b in zip(self.BODY.splitlines(), out.splitlines()):
            self.assertEqual(len(a), len(b))


class TestUnclosedFenceDoesNotBlindTheRest(unittest.TestCase):
    """Masking an unterminated fence would blank every line after it."""

    def test_content_after_an_unclosed_fence_is_still_read(self):
        for opener in ("```bash", "~~~text", "~~~~~~~~~~~~"):
            with self.subTest(opener=opener), tempfile.TemporaryDirectory() as tmp:
                body = f"## Notes\n{opener}\nsome code\n\n1. Explain [Why this is wrong].\n"
                skill = write_skill(tmp, "unclosedskill", body)
                _, report = run_json(skill)
                self.assertTrue(gaps_matching(report, "Lazy"),
                                f"{opener} swallowed the rest of the body")

    def test_a_closed_fence_is_still_masked(self):
        body = "## Notes\n```bash\nrun --flag [a slot in code]\n```\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "closedfenceskill", body)
            _, report = run_json(skill)
        self.assertEqual(gaps_matching(report, "Lazy"), [])

    def test_an_unclosed_backtick_fence_is_reported_by_the_size_check(self):
        errors, _ = analyze_gaps.check_inline_efficiency("a\n```\ncode\nmore\n")
        self.assertTrue(any("Unclosed code fence" in e for e in errors))

    def test_an_unclosed_tilde_fence_is_deliberately_not_an_error(self):
        """`check_inline_efficiency` tracks backtick fences only, on purpose.

        Teaching it `~~~` would make a decorative rule line — `~~~~~~~~~~~~` —
        read as an unterminated fence and fail a skill that passed before. The
        swallow this was guarding against is already gone: `mask_code` does not
        mask an unclosed fence, so the rules still see the rest of the body
        (the test above this pair). Reporting it is not worth a gate that is
        stricter than it was.
        """
        errors, _ = analyze_gaps.check_inline_efficiency("a\n~~~\ncode\nmore\n")
        self.assertEqual(errors, [])


class TestTodoMarkerForms(unittest.TestCase):
    """Every form the docstring names must actually be caught."""

    MARKERS = ["TODO: write this section", "TODO(sergey): write it", "- TODO",
               "- TODO fix the examples", "<!-- TODO -->",
               "<!-- TODO write this -->", "TODO write the examples",
               "1. TODO add tests", "> TODO revisit"]
    PROSE = ["a content slide with TODO placeholder",
             "titles + TODO bullets",
             "run `obsidian tasks todo format=json` to list open tasks"]

    def test_every_marker_form_is_caught(self):
        for line in self.MARKERS:
            with self.subTest(line=line):
                self.assertTrue(analyze_gaps.has_todo_marker(line))

    def test_prose_about_someone_else_s_todo_is_not(self):
        for line in self.PROSE:
            with self.subTest(line=line):
                self.assertFalse(analyze_gaps.has_todo_marker(line))


class TestWindowsPathImplementsItsDocstring(unittest.TestCase):
    PATHS = [r"C:\Users\me\out.docx", r"\\server\share\deck.pptx",
             r"scripts\lib\helper.py", r".\scripts\run.bat",
             r"%USERPROFILE%\Documents\out.docx"]
    NOT_PATHS = [r"Inline math uses \alpha\beta\gamma for the constants",
                 r"write `x\_1`, not x_1", r"emits `wiki-ingest 1.1.0\n` and exits 0",
                 r"use \(x\) for inline math"]
    # Stated cost of requiring a filename extension.
    KNOWN_FALSE_NEGATIVES = [r"x\y\z"]

    def test_a_real_windows_path_is_caught(self):
        for line in self.PATHS:
            with self.subTest(line=line):
                self.assertIsNotNone(analyze_gaps._WINDOWS_PATH_RE.search(line))

    def test_chained_escapes_are_not_paths(self):
        for line in self.NOT_PATHS:
            with self.subTest(line=line):
                self.assertIsNone(analyze_gaps._WINDOWS_PATH_RE.search(line))

    def test_the_stated_false_negatives_are_the_documented_ones(self):
        for line in self.KNOWN_FALSE_NEGATIVES:
            with self.subTest(line=line):
                self.assertIsNone(analyze_gaps._WINDOWS_PATH_RE.search(line))


class TestEveryFindingReportsAFileRelativeLine(unittest.TestCase):
    """One report must not mix two line-number conventions."""

    def test_token_efficiency_and_anti_pattern_agree_with_the_file(self):
        big = "\n".join(f"line {i}" for i in range(70))
        body = (f"## Notes\nRead /Users/alice/n.md first.\n\n```python\n{big}\n```\n")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "mixedlineskill", body)
            _, report = run_json(skill)
            lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
        for label, needle in (("Anti-Pattern", "/Users/alice/n.md"),
                              ("Token Efficiency", "```python")):
            found = gaps_matching(report, label) + advisories_matching(report, label)
            self.assertTrue(found, f"no {label} finding")
            n = int(re.search(r"at line (\d+)|block at line (\d+)",
                              found[0]).group(1) or 0
                    or re.search(r"block at line (\d+)", found[0]).group(1))
            self.assertIn(needle, lines[n - 1],
                          f"{label} line {n} does not resolve to its own finding")

    def test_the_language_advisory_line_resolves(self):
        body = "## Instructions\n1. The helper script should be bundled here.\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "langlineskill", body)
            _, report = run_json(skill)
            lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
        adv = advisories_matching(report, "Language")[0]
        n = int(re.search(r"Line (\d+):", adv).group(1))
        self.assertIn("should be bundled", lines[n - 1])


class TestStructureSeverityMatchesTheOtherGate(unittest.TestCase):
    """validate_skill.py warns about a non-standard directory and passes."""

    def test_a_non_standard_directory_is_advisory_not_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "dirsevskill", "## Notes\nNothing.\n",
                                extra_dirs=("workbench",))
            code, report = run_json(skill)
        self.assertEqual(gaps_matching(report, "Structure"), [], report["gaps"])
        self.assertTrue(advisories_matching(report, "Structure"))
        self.assertEqual(code, 0, "a warning-class finding must not fail the gate")

    def test_the_gates_agree_without_git_on_PATH(self):
        """`_is_git_ignored` shells out; agreement must not depend on it."""
        repo = SCRIPTS.parents[2]
        html = repo / "skills" / "html"
        if not html.is_dir():
            self.skipTest("skills/html is not in this checkout")
        with tempfile.TemporaryDirectory() as empty:
            env = dict(os.environ, PATH=empty)
            a = subprocess.run([sys.executable, str(ANALYZE), str(html)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=str(repo), env=env).returncode
            v = subprocess.run(
                [sys.executable,
                 str(repo / "skills/skill-creator/scripts/validate_skill.py"),
                 str(html)],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", cwd=str(repo), env=env).returncode
        self.assertEqual(a, v, "the gates disagree when git is off PATH")


if __name__ == "__main__":
    unittest.main()
