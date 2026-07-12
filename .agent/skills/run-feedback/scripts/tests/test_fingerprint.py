"""R2 — fingerprint stability and discrimination."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from feedback_lib import fingerprint as fp  # noqa: E402

# The same logical failure, captured twice with different volatile
# fragments: different absolute paths, numbers, hex ids, and timestamps.
MSG_A = ("cannot open /var/tmp/run-11/out.log at 2026-07-12 10:15:22 "
         "id deadbeefcafe attempt 3")
MSG_B = ("cannot open /Users/alice/work/out2.log at 2025-01-01T00:00:01Z "
         "id 0123456789ab attempt 42")


class TestNormalizeMessage(unittest.TestCase):
    def test_lowercases_and_collapses_whitespace(self):
        self.assertEqual(fp.normalize_message("Hello   BIG\t\n WORLD  "),
                         "hello big world")

    def test_volatile_fragments_replaced_with_placeholders(self):
        norm = fp.normalize_message(MSG_A)
        self.assertIn("<path>", norm)
        self.assertIn("<ts>", norm)
        self.assertIn("<hex>", norm)
        self.assertIn("<n>", norm)
        self.assertNotIn("deadbeefcafe", norm)
        self.assertNotIn("/var/tmp", norm)

    def test_none_and_empty_are_safe(self):
        self.assertEqual(fp.normalize_message(None), "")
        self.assertEqual(fp.normalize_message(""), "")


class TestCompute(unittest.TestCase):
    def test_same_failure_different_volatile_fragments_same_fingerprint(self):
        self.assertEqual(fp.compute("html", exit_code=2, message=MSG_A),
                         fp.compute("html", exit_code=2, message=MSG_B))

    def test_different_component_differs(self):
        self.assertNotEqual(fp.compute("html", exit_code=2, message="boom"),
                            fp.compute("pdf", exit_code=2, message="boom"))

    def test_different_error_type_differs(self):
        self.assertNotEqual(
            fp.compute("html", error_type="ConfigError", message="boom"),
            fp.compute("html", error_type="UsageError", message="boom"))

    def test_different_exit_code_differs(self):
        self.assertNotEqual(fp.compute("html", exit_code=2, message="boom"),
                            fp.compute("html", exit_code=3, message="boom"))

    def test_envelope_type_wins_over_exit_code(self):
        with_type_a = fp.compute("html", error_type="ConfigError",
                                 exit_code=2, message="boom")
        with_type_b = fp.compute("html", error_type="ConfigError",
                                 exit_code=7, message="boom")
        self.assertEqual(with_type_a, with_type_b)
        # ... but exit code still matters when there is no envelope type
        self.assertNotEqual(with_type_a,
                            fp.compute("html", exit_code=2, message="boom"))

    def test_fingerprint_is_16_hex_chars(self):
        self.assertRegex(fp.compute("html", exit_code=2, message="x"),
                         r"^[0-9a-f]{16}$")

    def test_component_normalized(self):
        self.assertEqual(fp.compute(" HTML ", exit_code=2, message="boom"),
                         fp.compute("html", exit_code=2, message="boom"))

    def test_failure_kind_fallbacks(self):
        self.assertEqual(fp.failure_kind("ConfigError", 2), "ConfigError")
        self.assertEqual(fp.failure_kind(None, 2), "exit:2")
        self.assertEqual(fp.failure_kind(None, None), "unknown")


if __name__ == "__main__":
    unittest.main()
