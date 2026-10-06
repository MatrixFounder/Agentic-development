"""CI actions are pinned to commits and kept current (TASK 111 R3).

A version tag such as `actions/checkout@v4` moves; a commit does not. This file pins:

* every `uses:` of `.github/workflows/*.yml` names a 40-hex commit and its release tag (``TC-P1``);
* `.github/dependabot.yml` updates the `github-actions` ecosystem monthly (``TC-P2``);
* the release checklist states how a pin changes (``TC-P3``).
"""
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = PROJECT_ROOT / ".github" / "workflows"
#: `uses: <owner>/<repo>[/<path>]@<40 hex> # v<version>`; a local action (`./`) is exempt.
PINNED = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40} # v\d+(?:\.\d+)*$")
USES = re.compile(r"^\s*(?:-\s+)?uses:\s*(.+?)\s*$")


def uses_lines():
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = USES.match(line)
            if m:
                yield f"{path.name}:{number}", m.group(1)


class TestPins(unittest.TestCase):

    def test_p1_every_action_is_pinned_to_a_commit_with_its_tag(self):
        # base-fail: the base names `@v4` and `@v5`.
        found = list(uses_lines())
        self.assertTrue(found, "no uses: line found")
        for where, ref in found:
            if ref.startswith("./"):
                continue
            with self.subTest(where=where):
                self.assertRegex(ref, PINNED)

    def test_p2_dependabot_updates_actions_monthly(self):
        text = (PROJECT_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        flat = " ".join(text.split())
        self.assertRegex(flat, r'package-ecosystem: "?github-actions"?')
        self.assertRegex(flat, r'interval: "?monthly"?')

    def test_p3_release_checklist_names_the_pin_update(self):
        text = (PROJECT_ROOT / "System" / "Docs" / "RELEASE_CHECKLIST.md").read_text(
            encoding="utf-8")
        self.assertIn("dependabot.yml", text)


if __name__ == "__main__":
    unittest.main()
