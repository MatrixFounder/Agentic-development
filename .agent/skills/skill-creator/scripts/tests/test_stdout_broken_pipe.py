"""A reader that closes early must not rewrite these scripts' exit status.

CPython flushes `sys.stdout` again while shutting down. If that flush hits a dead
pipe it prints `Exception ignored while flushing sys.stdout` on stderr and
**replaces the exit status with 120** — so the process contradicts the result it
just reported, and `run_loop.py` never reaches the line that writes
`results.json`. Measured on this machine (pipe capacity 65,536 bytes): a payload
of ~90-130 KB exits 120, a larger one escapes as a raw traceback and exits 1.

Both bands are covered on purpose. `print()` alone does **not** raise for a
~110 KB payload — the EPIPE only surfaces at flush — so a `try/except
BrokenPipeError` around a bare `print()` is green in the large band and still
broken in the 120 band. That is what `test_*_mid_band` kills.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHILD = HERE / "_stdout_pipe_child.py"

# Chosen against a measured 65,536-byte pipe capacity.
MID_BAND = 95_000    # renders to ~105-125 KB — the exit-120 band
LARGE = 400_000      # renders to >400 KB — the raw-traceback band


def run_with_dead_reader(module, target_bytes, workdir, env=None):
    """Run the child, consume 20 bytes, close the pipe. Returns (rc, stderr).

    `bufsize=0` is load-bearing. The default BufferedReader drains 8 KiB of the
    child's payload per `read()`, and how much the reader consumed before it
    disappeared decides *which* failure the child gets: consume little and the
    EPIPE lands inside `print()` (catchable by a bare try/except), consume a lot
    and the child finishes before we close. Reading exactly 20 raw bytes is what
    `... | head -c 20` does, and it is the case where `print()` returns normally
    and only the shutdown flush fails — the exit-120 mode this file exists for.
    """
    child_env = dict(os.environ)
    child_env.update(env or {})
    proc = subprocess.Popen(
        [sys.executable, str(CHILD), module, str(target_bytes), str(workdir)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env, bufsize=0,
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
    return proc.wait(), stderr.decode("utf-8", "replace")


class StdoutBrokenPipeMixin:
    module = None
    expected_rc = 0

    def _assert_clean(self, target_bytes):
        with tempfile.TemporaryDirectory() as tmp:
            rc, err = run_with_dead_reader(self.module, target_bytes, tmp)
        self.assertNotEqual(rc, 120, f"{self.module}: shutdown flush overrode the exit status")
        self.assertEqual(rc, self.expected_rc, f"{self.module}: stderr was:\n{err}")
        self.assertNotIn("Exception ignored", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(err, "", f"{self.module}: unexpected stderr:\n{err}")

    def test_a_dead_reader_mid_band_keeps_the_scripts_own_exit_code(self):
        self._assert_clean(MID_BAND)

    def test_a_dead_reader_large_payload_keeps_the_scripts_own_exit_code(self):
        self._assert_clean(LARGE)


class TestRunEvalStdout(StdoutBrokenPipeMixin, unittest.TestCase):
    module = "run_eval"


class TestRunLoopStdout(StdoutBrokenPipeMixin, unittest.TestCase):
    module = "run_loop"

    def test_a_dead_reader_does_not_lose_results_json(self):
        """`results.json` is written *after* the print. Before the fix the large
        band raised out of `main()` there and the file was never written."""
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "out"
            rc, err = run_with_dead_reader(
                "run_loop", LARGE, tmp, env={"CHILD_RESULTS_DIR": str(results_dir)})
            self.assertEqual(rc, 0, err)
            written = list(results_dir.rglob("results.json"))
            self.assertEqual(len(written), 1, "run_loop lost results.json on a dead reader")
            self.assertGreater(written[0].stat().st_size, LARGE)


class TestImproveDescriptionStdout(StdoutBrokenPipeMixin, unittest.TestCase):
    module = "improve_description"


if __name__ == "__main__":
    unittest.main()
