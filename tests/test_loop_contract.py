"""Tests for `System/scripts/check_loop_contract.py` (design spec 095, Component B).

The load-bearing tests here are the NEGATIVE ones. A validator that reports zero
findings against the live corpus is indistinguishable from a validator that checks
nothing — this repository has already shipped exactly that once
(`check_prompt_references.py` matched zero references for its entire life while
printing OK). So every rule the script claims to enforce has a fixture that trips it,
and `test_every_phase3_rule_fires` fails if any rule stops producing a finding.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPT = PROJECT_ROOT / "System" / "scripts" / "check_loop_contract.py"
FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "loop_contract"
EXPECTED_WARNINGS = PROJECT_ROOT / "docs" / "design" / "095-phase3-expected-warnings.txt"

# Every rule Phase 3 turns on. R8 and R11 belong to Phase 5 (Component C) and are
# deliberately absent — see spec §5.2.
PHASE3_RULES = {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R9", "R10", "R12", "R13", "R14"}


def run_validator(root: Path, *flags: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *flags],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def findings(root: Path, *flags: str) -> list[dict]:
    code, out = run_validator(root, "--json", *flags)
    return [json.loads(line) for line in out.splitlines() if line.startswith("{")]


class TestLiveCorpus(unittest.TestCase):
    """The real `.agent/workflows/` must satisfy the contract it declares."""

    def test_live_corpus_has_no_errors(self):
        found = findings(PROJECT_ROOT)
        errors = [f for f in found if f["severity"] == "error"]
        self.assertEqual(errors, [], f"loop contract violations in the live corpus: {errors}")

    def test_live_corpus_exit_code_is_zero_under_strict(self):
        code, out = run_validator(PROJECT_ROOT, "--strict")
        self.assertEqual(code, 0, out)

    def test_every_workflow_declares_a_contract(self):
        """R6 is what stopped `full-robust` from being invisible (spec Appendix A.5)."""
        workflows = sorted((PROJECT_ROOT / ".agent" / "workflows").glob("*.md"))
        self.assertEqual(len(workflows), 23)
        for path in workflows:
            with self.subTest(workflow=path.stem):
                self.assertIn("\ncontract:\n", path.read_text(encoding="utf-8"))

    def test_warnings_match_the_recorded_fixture(self):
        """Phase-3 exit gate: the WARN set is compared, not eyeballed."""
        found = findings(PROJECT_ROOT)
        actual = sorted(
            f"{f['rule']} {f['workflow']} {f['code']}"
            for f in found if f["severity"] == "warn"
        )
        expected = [
            line.strip() for line in EXPECTED_WARNINGS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertEqual(actual, sorted(expected))


class TestNegativeFixtures(unittest.TestCase):
    """Proof that the rules can fail. Without this the suite above is vacuous."""

    NEGATIVE = FIXTURES / "negative"
    UNREGISTERED = FIXTURES / "unregistered"

    def test_r3_negative_fixture_fails_the_validator(self):
        """The fixture the spec makes a deliverable: default_max 3 over prose Max 2.

        If this ever passes, R3 has gone vacuous again and the CI gate built on it is
        asserting that an author typed a number.
        """
        found = findings(self.NEGATIVE)
        mismatches = [
            f for f in found
            if f["rule"] == "R3" and f["code"] == "BOUND_MISMATCH" and f["workflow"] == "r3-mismatch"
        ]
        self.assertEqual(len(mismatches), 1, f"R3 did not catch the drifted bound: {found}")

    def test_negative_fixture_exits_1_under_strict(self):
        code, out = run_validator(self.NEGATIVE, "--strict")
        self.assertEqual(code, 1, out)

    def test_negative_fixture_exits_0_without_strict(self):
        """S4 — Component B ships warn-only; --strict is Phase 4's switch."""
        code, out = run_validator(self.NEGATIVE)
        self.assertEqual(code, 0, out)

    def test_every_phase3_rule_fires(self):
        found = findings(self.NEGATIVE) + findings(self.UNREGISTERED)
        fired = {f["rule"] for f in found}
        missing = PHASE3_RULES - fired
        self.assertEqual(missing, set(), f"rules with no fixture that trips them: {sorted(missing)}")

    def test_site_grammar_has_no_third_form(self):
        """§4.3.1 — prose anchors are an error, never a fallback."""
        codes = {f["code"] for f in findings(self.NEGATIVE)}
        self.assertIn("SITE_UNRESOLVABLE", codes)
        self.assertIn("BOUND_UNRESOLVABLE", codes)
        self.assertIn("BOUND_AMBIGUOUS", codes)

    def test_resolution_failures_name_the_part_that_failed(self):
        """A `window: 0` reported as SITE_UNRESOLVABLE sends the author to inspect the
        one part of the declaration that is correct. Each cause gets its own code."""
        by_code = {f["code"]: f for f in findings(self.NEGATIVE)}
        self.assertIn("WINDOW_INVALID", by_code)
        self.assertIn("the site itself resolves", by_code["WINDOW_INVALID"]["detail"])
        self.assertIn("SITE_ID_MISMATCH", by_code)

    def test_bind_across_a_fragment_delegation_warns(self):
        """§4.5 constraint 1 — the F10 shape: a caller binding a loop its delegated
        fragment never reaches. Reachability is prose, so this warns rather than
        pretending to decide it; silence here would be the defect F10 already was."""
        found = findings(self.NEGATIVE)
        warns = [f for f in found if f["code"] == "BIND_OVER_PARTIAL_EDGE"]
        self.assertEqual(len(warns), 1, f"partial-edge bind produced no finding: {found}")
        self.assertEqual(warns[0]["severity"], "warn")

    def test_partial_edge_without_binds_is_silent(self):
        """The correct case must stay quiet, or the warning is noise: `vdd-05`
        delegates a fragment of `vdd-03` and binds nothing."""
        found = findings(PROJECT_ROOT)
        self.assertEqual([f for f in found if f["code"] == "BIND_OVER_PARTIAL_EDGE"], [])

    def test_exit_bar_must_be_quotable(self):
        """R10 — `"until done"` is what 'non-empty' accepts and this rule rejects."""
        found = findings(self.NEGATIVE)
        self.assertTrue(any(f["code"] == "EXIT_BAR_NOT_QUOTED" for f in found))

    def test_unregistered_anchor_is_an_error(self):
        """R14 / D9 — documentation-standards §4.4: a gate reading an unregistered
        anchor is a defect, and this script is that gate."""
        codes = {f["code"] for f in findings(self.UNREGISTERED)}
        self.assertIn("REGISTRY_MISSING", codes)


class TestCliContract(unittest.TestCase):

    def test_missing_root_is_exit_2(self):
        code, out = run_validator(PROJECT_ROOT / "no" / "such" / "root")
        self.assertEqual(code, 2, out)

    def test_invalid_yaml_is_exit_3(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp) / ".agent" / "workflows"
            wf.mkdir(parents=True)
            (wf / "broken.md").write_text(
                "---\ndescription: broken\ncontract:\n  version: 1\n   loops: [\n---\nbody\n",
                encoding="utf-8",
            )
            code, out = run_validator(Path(tmp))
            self.assertEqual(code, 3, out)

    def test_json_output_is_one_object_per_line(self):
        code, out = run_validator(FIXTURES / "negative", "--json")
        for line in out.splitlines():
            if line.strip():
                self.assertIsInstance(json.loads(line), dict)

    def test_summary_reports_the_loop_count(self):
        """A file count is not evidence that anything was checked
        (`developer-guidelines` §6.3, rule 3)."""
        code, out = run_validator(PROJECT_ROOT)
        self.assertRegex(out, r"checked 25 loops: 0 error\(s\)")


if __name__ == "__main__":
    unittest.main()
