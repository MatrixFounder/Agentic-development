"""R10 — deterministic retro ownership: claim/release/stale semantics."""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _fixtures as fx  # noqa: E402
from feedback_lib import claims  # noqa: E402


class ClaimTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = fx.make_repo(self._tmp.name)
        self.cfg = fx.load_cfg(self.root)

    def _claim(self, run_id):
        return fx.run_cli(["--repo-root", self.root, "claim",
                           "--run-id", run_id])

    def _release(self, run_id, *extra):
        return fx.run_cli(["--repo-root", self.root, "release",
                           "--run-id", run_id, *extra])


class TestClaimCli(ClaimTestCase):
    def test_full_ownership_lifecycle(self):
        # first claim acquires
        code, out, _ = self._claim("run-1")
        self.assertEqual(code, 0)
        self.assertIn("claimed", out)

        # a different run is denied (exit 6)
        code, out, _ = self._claim("run-2")
        self.assertEqual(code, 6)
        self.assertIn("DENIED", out)
        self.assertIn("run-1", out)  # reports the live owner

        # same run-id re-claim is ok (idempotent)
        code, _, _ = self._claim("run-1")
        self.assertEqual(code, 0)

        # release by non-owner without --force is refused (exit 6)
        code, out, _ = self._release("run-2")
        self.assertEqual(code, 6)
        self.assertIn("NOT released", out)
        self.assertTrue(Path(self.cfg.retro_owner_path).exists())

        # release by the owner clears the claim file
        code, _, _ = self._release("run-1")
        self.assertEqual(code, 0)
        self.assertFalse(Path(self.cfg.retro_owner_path).exists())

        # ...and the next run can claim again
        code, _, _ = self._claim("run-2")
        self.assertEqual(code, 0)

    def test_force_release_by_non_owner(self):
        self.assertEqual(self._claim("owner-run")[0], 0)
        code, _, _ = self._release("intruder-run", "--force")
        self.assertEqual(code, 0)
        self.assertFalse(Path(self.cfg.retro_owner_path).exists())


class TestStaleClaim(ClaimTestCase):
    def test_stale_claim_is_overwritable(self):
        path = Path(self.cfg.retro_owner_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # a claim from 25 hours ago (TTL is 24h)
        path.write_text(json.dumps({"run_id": "ghost-run",
                                    "claimed_at": time.time() - 25 * 3600}),
                        encoding="utf-8")
        acquired, owner = claims.claim(self.cfg, "fresh-run")
        self.assertTrue(acquired)
        self.assertEqual(owner, "fresh-run")
        current = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(current["run_id"], "fresh-run")

    def test_fresh_foreign_claim_not_overwritable(self):
        path = Path(self.cfg.retro_owner_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"run_id": "live-run",
                                    "claimed_at": time.time()}),
                        encoding="utf-8")
        acquired, owner = claims.claim(self.cfg, "late-run")
        self.assertFalse(acquired)
        self.assertEqual(owner, "live-run")


if __name__ == "__main__":
    unittest.main()
