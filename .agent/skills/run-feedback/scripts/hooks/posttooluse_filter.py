#!/usr/bin/env python3
"""PostToolUse(Bash) filter: stdin JSON -> maybe one inbox finding.

Contract with the session: ALWAYS exit 0, never write to stdout (a hook's
stdout can reach the model), finish fast (single stdlib interpreter, no
venv). Inbox-only — this never touches ledgers.

The Bash `tool_response` shape is not formally documented, so extraction
is a ladder (structured fields -> "Exit code N" text -> JSON error
envelope). Set RUN_FEEDBACK_HOOK_DEBUG=1 to dump raw payloads (max 5) to
the feedback dir and verify the live shape — the mandatory step before
trusting this surface.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MAX_DEBUG_DUMPS = 5


#: Each response part is truncated to its last TAIL_CHARS before anything else
#: touches it. Everything downstream only ever inspects the tail: `_exit_code`
#: greps for a trailing `Exit code: N`, `find_envelope` reads the last 5 non-empty
#: lines, `filters.clip` keeps the tail. Without this, a Bash call that printed a
#: 5 MB log cost a 5 MB copy plus ~100k transient strings in `find_envelope` —
#: ABOVE the exit-0 discard filter, i.e. on every successful command, synchronously
#: in the user's session. WI-4 removed a bounded ~5-30ms `git` spawn from this path
#: and left an unbounded allocation cost three lines higher (iteration 3, perf-High).
TAIL_CHARS = 65536


def _tail(text):
    return text if len(text) <= TAIL_CHARS else text[-TAIL_CHARS:]


def _response_text(resp):
    if resp is None:
        return ""
    if isinstance(resp, str):
        return _tail(resp)
    if isinstance(resp, dict):
        parts = []
        for key in ("stdout", "stderr", "output", "content", "text", "error"):
            value = resp.get(key)
            if isinstance(value, str):
                parts.append(_tail(value))
            elif isinstance(value, list):
                parts.extend(_tail(p.get("text", "")) for p in value
                             if isinstance(p, dict))
        return _tail("\n".join(parts))
    return _tail(str(resp))


def _exit_code(resp, text):
    if isinstance(resp, dict):
        for key in ("exit_code", "exitCode", "returncode", "code"):
            value = resp.get(key)
            if isinstance(value, int):
                return value
    import re
    match = re.search(r"^Exit code[: ]+(\d+)", text, re.MULTILINE)
    if match:
        return int(match.group(1))
    return None


def _interrupted(resp):
    if isinstance(resp, dict):
        return bool(resp.get("interrupted") or resp.get("cancelled")
                    or resp.get("aborted"))
    return False


def _maybe_debug_dump(payload):
    """Persist the raw payload when RUN_FEEDBACK_HOOK_DEBUG=1. Always returns 0.

    Loads config lazily and by itself so the normal path pays nothing, and is
    reachable from the earliest discard so a dropped event can still be inspected —
    diagnosing the filters is the whole point of the facility.
    """
    if os.environ.get("RUN_FEEDBACK_HOOK_DEBUG") != "1":
        return 0
    try:
        from feedback_lib.config import load_config
        cfg = load_config(repo_root=(os.environ.get("CLAUDE_PROJECT_DIR")
                                     or payload.get("cwd") or os.getcwd()))
        cfg.feedback_dir.mkdir(parents=True, exist_ok=True)
        dumps = sorted(cfg.feedback_dir.glob("hook_debug-*.json"))
        if len(dumps) < MAX_DEBUG_DUMPS:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            # REDACTED before it is persisted (iteration 3, sec-L-06): this was
            # the only place unredacted tool output was durably stored. The dump
            # exists to verify the tool_response *shape*, and redaction preserves
            # structure while removing the value — so the facility keeps its whole
            # purpose and stops being a plaintext secret sink.
            from feedback_lib import filters
            (cfg.feedback_dir / ("hook_debug-%s-%d.json"
                                 % (stamp, os.getpid()))).write_text(
                filters.redact(json.dumps(payload, ensure_ascii=False, indent=2)),
                encoding="utf-8")
    except Exception:  # noqa: BLE001 - a debug facility never breaks the hook
        pass
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0

    # The cheapest possible discard comes FIRST — before the feedback_lib imports,
    # which pull in re, shlex, json, fcntl, tempfile, subprocess and unicodedata
    # (~5-15ms of a ~40ms process) for an event that is about to be dropped. Same
    # defect class as WI-4, one layer up (iteration 3, perf-High secondary).
    if payload.get("tool_name") != "Bash":
        return _maybe_debug_dump(payload)

    from feedback_lib import filters, finding, inbox, journal
    from feedback_lib.config import load_config

    repo_hint = (os.environ.get("CLAUDE_PROJECT_DIR")
                 or payload.get("cwd") or os.getcwd())
    # The debug dump stays ABOVE the remaining filters and pays for its own config
    # load: it exists to diagnose WHY the filters discarded something, so moving it
    # below them would destroy its only purpose (WI-4 / audit 093 Step 3).
    _maybe_debug_dump(payload)
    cfg = None

    # --- cheap discard filters, before any config load --------------------
    # This hook runs synchronously on EVERY Bash tool call and most events are
    # discarded here. Loading config above these filters meant a config read plus
    # a `git rev-parse` for every discarded event, with the git timeout as the
    # worst-case stall of a hooked tool call (WI-4).
    command = (payload.get("tool_input") or {}).get("command", "")
    resp = payload.get("tool_response")
    text = _response_text(resp)
    exit_code = _exit_code(resp, text)
    envelope = filters.find_envelope(text)
    if _interrupted(resp):
        return 0
    if exit_code is None and isinstance(resp, dict) and resp.get("is_error"):
        exit_code = 1
    if not filters.should_capture(command, exit_code, stderr_text=text,
                                  has_envelope=envelope is not None):
        return 0

    # --- only now is a capture actually going to happen -------------------
    if cfg is None:
        try:
            cfg = load_config(repo_root=repo_hint)
        except Exception:
            return 0

    component = filters.component_of(command, fallback="session")
    tail = [l for l in text.strip().splitlines() if l.strip()]
    message = ((envelope or {}).get("error") or (tail[-1] if tail else command))
    record = finding.new_finding(
        "hook", "tool-error", component, filters.redact(message)[:400],
        command=command[:500], exit_code=exit_code, error_envelope=envelope,
        run={"session_id": payload.get("session_id"),
             "cwd": payload.get("cwd")},
        evidence={"excerpts": [{"text": filters.clip(text, 400),
                                "source": "hook"}]})
    try:
        record, deduped = inbox.collect(cfg, record)
        journal.append_event(
            cfg.journal_dir,
            "finding_deduped" if deduped else "finding_collected",
            "%s %s" % (component, record["fingerprint"]),
            {"kind": "tool-error", "via": "hook",
             "occurrences": record["occurrences"]})
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
