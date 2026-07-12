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
    from feedback_lib import journal
    from feedback_lib.config import load_config
    repo_hint = (os.environ.get("CLAUDE_PROJECT_DIR")
                 or payload.get("cwd") or os.getcwd())
    try:
        cfg = load_config(repo_root=repo_hint)
        journal.append_event(
            cfg.journal_dir, "session_end",
            payload.get("session_id") or "unknown-session",
            {"reason": payload.get("reason"),
             "transcript": payload.get("transcript_path")})
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
