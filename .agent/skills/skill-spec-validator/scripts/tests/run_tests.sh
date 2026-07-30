#!/usr/bin/env bash
# skill-spec-validator suite runner with a ZERO-TEST GUARD.
#
# `python3 -m unittest discover` exits 0 when it discovers nothing — the same
# silent-green failure mode this skill was tested for in the first place (a gate
# that never fires looks exactly like a gate nobody tripped). So a run that
# executes zero tests is a FAILURE here, not a pass. Mirrors the discipline in
# run-feedback/scripts/tests/test_e2e.sh.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$(dirname "$HERE")"
fail=0

out="$(cd "$SCRIPTS" && python3 -m unittest discover -s tests 2>&1)" || fail=1
echo "$out" | tail -5
echo "$out" | grep -qE '^Ran [1-9][0-9]* test' || { echo "FAIL: zero-test discovery"; fail=1; }
echo "$out" | grep -qE '^OK' || { echo "FAIL: suite not OK"; fail=1; }

# The corpus tests SKIP outside the framework repo (by design). Inside it they
# must actually run, otherwise the anti-drift guard is silently absent. The
# "am I in the framework repo?" question is answered by the SAME predicate the
# tests use — a second, disagreeing shell check made a `.git`-less checkout fail
# spuriously (vdd-multi F21).
corpus_present="$(cd "$HERE" && python3 -c 'import test_corpus; print(1 if test_corpus.REPO_ROOT else 0)' 2>/dev/null || echo 0)"
if [ "$corpus_present" = "1" ]; then
  # count skips rather than grepping for the word: any future legitimate skip
  # elsewhere in the suite would otherwise fail this gate
  skipped="$(echo "$out" | grep -oE 'skipped=[0-9]+' | head -1 | cut -d= -f2)"
  [ -n "${skipped:-}" ] && { echo "FAIL: $skipped test(s) skipped inside the framework repo (corpus guard must run)"; fail=1; }
fi

if [ "$fail" = "0" ]; then echo "spec-validator tests: PASS"; else echo "spec-validator tests: FAIL"; fi
exit "$fail"
