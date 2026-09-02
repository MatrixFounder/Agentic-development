"""`analyze_gaps.py --json | head` must not rewrite the documented exit code.

`analyze_skill` ends its `--json` branch with `sys.exit(1 if gaps else 0)`, and
callers rely on that: non-zero means "this skill has gaps". CPython flushes
`sys.stdout` again while shutting down, and if that flush hits a dead pipe it
prints `Exception ignored while flushing sys.stdout` on stderr and **replaces the
exit status with 120** — the `sys.exit` above never gets to mean anything, so a
run with gaps and a run without gaps report the same thing.

Measured on this machine (pipe capacity 65,536 bytes): a report of ~90-130 KB
exits 120, a larger one escapes as a raw traceback and exits 1. Both bands are
covered on purpose — `print()` alone does not raise in the first one, so a
`try/except BrokenPipeError` around a bare `print()` is green in the large band
and still broken in the 120 band.

Fixtures are generated, not committed: the defect only appears once the report
outgrows the pipe buffer, so a small checked-in skill would be green against
broken code.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ANALYZE = Path(__file__).resolve().parent.parent / "analyze_gaps.py"

# One `[Anti-Pattern] Machine-specific absolute path` gap per body line.
# Measured: 860 lines -> ~145 KB (the exit-120 band); 1500 -> ~253 KB
# (traceback band).
#
# The path root is load-bearing and must stay under `/home` (or another root in
# `analyze_gaps._MACHINE_PATH_ROOTS`). Before WI-033 this fixture used
# `/usr/local/lib/...`; that rule now flags only paths that name one machine or
# one user's account, because `/usr/...` and `/tmp/...` in a documented command
# are correct content. Under the old path the fixture produced zero gaps and a
# 632-byte report — too small to reach the pipe buffer, so this test would have
# been green against broken code.
MID_BAND_LINES = 860
LARGE_LINES = 1500


def make_skill(root, n_lines, name):
    root = Path(root) / name
    root.mkdir(parents=True)
    body = ["---", f"name: {name}",
            "description: Use when generating an oversized gap report for "
            "broken-pipe measurement.",
            "version: 1.0.0", "---", "", f"# {name}", ""]
    for i in range(n_lines):
        body.append(f"Refer to /home/builder/{name}/module_{i:05d}/entry.py "
                    f"for the details of step {i}.")
    (root / "SKILL.md").write_text("\n".join(body) + "\n")
    return root


def run_with_dead_reader(skill_dir):
    """Run `analyze_gaps.py --json`, consume 20 bytes, close the pipe.

    `bufsize=0` is load-bearing: the default BufferedReader drains 8 KiB per
    `read()`, and consuming that much moves the EPIPE inside `print()`, where a
    bare try/except already catches it. Twenty raw bytes is what
    `... | head -c 20` does and is the case where only the shutdown flush fails.
    """
    proc = subprocess.Popen(
        [sys.executable, str(ANALYZE), str(skill_dir), "--json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
    )
    got = b""
    while len(got) < 20:
        chunk = proc.stdout.read(20 - len(got))
        if not chunk:
            break
        got += chunk
    proc.stdout.close()
    stderr = proc.stderr.read()
    proc.stderr.close()
    return proc.wait(), stderr.decode("utf-8", "replace"), got


class TestAnalyzeGapsStdoutBrokenPipe(unittest.TestCase):
    def _assert_clean(self, n_lines, name, min_bytes):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(tmp, n_lines, name)
            whole = subprocess.run(
                [sys.executable, str(ANALYZE), str(skill), "--json"],
                capture_output=True)
            self.assertGreater(
                len(whole.stdout), min_bytes,
                "fixture too small to outgrow the pipe buffer; the test would be "
                "green against broken code")
            self.assertTrue(json.loads(whole.stdout)["gaps"], "fixture produced no gaps")
            self.assertEqual(whole.returncode, 1, "a skill with gaps must exit 1")
            rc, err, head = run_with_dead_reader(skill)
        self.assertEqual(head, whole.stdout[:20])
        self.assertNotEqual(rc, 120, "the shutdown flush overrode the exit status")
        self.assertEqual(
            rc, 1,
            "a dead reader must not erase the documented 'gaps exist' exit code; "
            f"stderr was:\n{err}")
        self.assertNotIn("Exception ignored", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(err, "", f"unexpected stderr:\n{err}")

    def test_a_dead_reader_mid_band_keeps_the_gaps_exit_code(self):
        self._assert_clean(MID_BAND_LINES, "midskill", 90_000)

    def test_a_dead_reader_large_report_keeps_the_gaps_exit_code(self):
        self._assert_clean(LARGE_LINES, "bigskill", 150_000)


if __name__ == "__main__":
    unittest.main()
