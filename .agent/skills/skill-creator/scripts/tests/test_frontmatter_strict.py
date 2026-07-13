"""Regression tests for VAL-1 — validate_skill.py must reject frontmatter that strict
YAML parsers reject (an unquoted colon-bearing scalar renders the skill card as a parse
error in Obsidian/VSCode preview), while keeping PyYAML soft-optional.

See docs/issues/val-1-validate-skill-py-passes-frontmatter-that-strict-yaml-parsers-reject-unquoted-colon-in-description.md
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validate_skill  # noqa: E402

BAD_DESCRIPTION = 'Use when previewing breaks: strict YAML parsers reject this "unquoted" colon scalar.'
GOOD_DESCRIPTION = '"Use when previewing breaks: strict YAML parsers accept this quoted colon scalar."'

CONFIG = {
    "validation": {"enforce_cso_prefix": True, "allowed_cso_prefixes": ["Use when"]},
    "taxonomy": {"tiers": [{"value": 0}, {"value": 1}, {"value": 2}]},
}


def _frontmatter(description):
    return f"name: demo-skill\ndescription: {description}\ntier: 2\nversion: 1.0"


class TestCheckFrontmatterStrict(unittest.TestCase):
    def test_unquoted_colon_scalar_is_an_error(self):
        errors, warnings = validate_skill.check_frontmatter_strict(_frontmatter(BAD_DESCRIPTION))
        self.assertTrue(errors, "strict check must reject an unquoted colon-bearing scalar")
        self.assertIn("Strict YAML Parse Error", errors[0])
        self.assertFalse(warnings)

    def test_quoted_colon_scalar_is_clean(self):
        errors, warnings = validate_skill.check_frontmatter_strict(_frontmatter(GOOD_DESCRIPTION))
        self.assertEqual(([], []), (errors, warnings))

    def test_heuristic_floor_warns_without_pyyaml(self):
        """PyYAML stays soft-optional: the stdlib fallback warns, it never fails."""
        warnings = validate_skill._heuristic_unquoted_colon_warnings(_frontmatter(BAD_DESCRIPTION))
        self.assertEqual(1, len(warnings))
        self.assertIn("'description'", warnings[0])
        self.assertIn("line 3", warnings[0])
        self.assertFalse(
            validate_skill._heuristic_unquoted_colon_warnings(_frontmatter(GOOD_DESCRIPTION))
        )


class TestValidateSkillEndToEnd(unittest.TestCase):
    """The VAL-1 reproduction itself, at unit scope: the gate must go red."""

    def _validate_with_description(self, description):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = os.path.join(tmp, "demo-skill")
            os.makedirs(skill_dir)
            with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
                f.write(f"---\n{_frontmatter(description)}\n---\n\n# Demo Skill\n\nBody.\n")
            with redirect_stdout(io.StringIO()) as out:
                passed = validate_skill.validate_skill(skill_dir, CONFIG)
            return passed, out.getvalue()

    def test_skill_with_unquoted_colon_description_fails_validation(self):
        passed, output = self._validate_with_description(BAD_DESCRIPTION)
        self.assertFalse(passed, "VAL-1: validator must not pass strict-YAML-broken frontmatter")
        self.assertIn("Strict YAML Parse Error", output)

    def test_skill_with_quoted_colon_description_passes_validation(self):
        passed, _ = self._validate_with_description(GOOD_DESCRIPTION)
        self.assertTrue(passed)


if __name__ == "__main__":
    unittest.main()
