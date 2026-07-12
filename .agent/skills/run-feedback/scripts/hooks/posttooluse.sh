#!/bin/sh
# Claude Code PostToolUse(Bash) capture wrapper for run-feedback.
# OPT-IN: does nothing unless RUN_FEEDBACK_HOOKS=1 (set it in your personal
# settings.local.json "env" or shell profile). Fail-silent by design: a
# broken feedback path must never break the hooked command or the session.
[ "${RUN_FEEDBACK_HOOKS:-0}" = "1" ] || exit 0
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$DIR/posttooluse_filter.py" 2>/dev/null || true
exit 0
