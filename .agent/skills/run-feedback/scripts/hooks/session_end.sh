#!/bin/sh
# Claude Code SessionEnd marker for run-feedback (opt-in, fail-silent).
# Journals a session-end event so the transcript miner knows the session's
# jsonl is complete and safe to mine.
[ "${RUN_FEEDBACK_HOOKS:-0}" = "1" ] || exit 0
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$DIR/session_end_marker.py" 2>/dev/null || true
exit 0
