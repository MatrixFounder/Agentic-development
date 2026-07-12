#!/usr/bin/env python3
"""SessionEnd hook body: append a session_end journal marker (never inbox)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}
    from feedback_lib import inbox, journal
    from feedback_lib import mine as mine_mod
    from feedback_lib.config import load_config
    repo_hint = (os.environ.get("CLAUDE_PROJECT_DIR")
                 or payload.get("cwd") or os.getcwd())
    session_id = payload.get("session_id") or "unknown-session"
    try:
        cfg = load_config(repo_root=repo_hint)
        journal.append_event(
            cfg.journal_dir, "session_end", session_id,
            {"reason": payload.get("reason"),
             "transcript": payload.get("transcript_path")})
    except Exception:
        return 0

    # Auto-mine the just-ended session (opt-in). This is the PRIMARY live
    # capture path: PostToolUse does NOT fire on failing tool calls
    # (verified 2026-07-13 on Claude Code 2.1.207), so per-command hooks
    # cannot see errors — the transcript can. --include-active semantics:
    # the transcript is complete once SessionEnd fires.
    if os.environ.get("RUN_FEEDBACK_MINE_ON_END") == "1":
        try:
            transcript = payload.get("transcript_path")
            tdirs = ([Path(transcript).parent] if transcript else None)
            emitted, stats = mine_mod.mine(
                cfg, transcript_dirs=tdirs, session=session_id,
                include_active=True)
            collected = 0
            for record in emitted:
                _, was_dup = inbox.collect(cfg, record)
                collected += 0 if was_dup else 1
            journal.append_event(
                cfg.journal_dir, "mine_run",
                "session-end %s" % session_id,
                {**stats, "collected": collected})
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
