"""Transcript miner: extract failure signals from Claude Code session logs.

Claude Code shards transcripts per-cwd under ``~/.claude/projects/`` (a
session launched inside ``skills/html`` lands in a DIFFERENT dir than one
launched at the repo root), so discovery enumerates every project dir
whose decoded path sits at or under the repo root.

Deterministic, incremental (per-file byte offsets), and it shares the
noise policy + fingerprint recipe with the PostToolUse hook so the same
failure captured live and mined later collapses into one finding.
Excerpts are redacted and hard-capped; assistant text, thinking blocks and
file contents are never scanned.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from . import atomic, filters, finding
from . import fingerprint as fp

MINE_STATE_VERSION = 1
ACTIVE_SESSION_WINDOW_SEC = 600
EXCERPT_LIMIT = 400
FRUSTRATION_LIMIT = 200
REPEAT_THRESHOLD = 3

_EXIT_CODE_RE = re.compile(r"^Exit code[: ]+(\d+)", re.MULTILINE)
_FRUSTRATION_RE = re.compile(
    r"(?i)(не работает|опять|снова не|сломал|какого|still broken|"
    r"doesn'?t work|again\b|wtf|broken again)")


def encode_project_dir(path):
    return re.sub(r"[/.]", "-", str(path))


def default_transcript_dirs(repo_root, projects_dir=None):
    projects = Path(projects_dir or (Path.home() / ".claude" / "projects"))
    if not projects.is_dir():
        return []
    prefix = encode_project_dir(Path(repo_root).resolve())
    return sorted(d for d in projects.iterdir()
                  if d.is_dir() and (d.name == prefix
                                     or d.name.startswith(prefix + "-")))


# --- incremental state -------------------------------------------------------

def load_state(path):
    try:
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        if state.get("v") == MINE_STATE_VERSION:
            return state
    except (OSError, ValueError):
        pass
    return {"v": MINE_STATE_VERSION, "sessions": {}}


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic.write_atomic(path, json.dumps(state, indent=2) + "\n")


# --- per-line extraction ------------------------------------------------------

def _result_text(item):
    content = item.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content
                         if isinstance(part, dict) and part.get("type") == "text")
    return ""


_find_envelope = filters.find_envelope


def _component_of(command, tool_name):
    return filters.component_of(command, fallback=tool_name)


class SessionMiner:
    """Single-pass scanner over one session jsonl file."""

    def __init__(self, session_id, frustration=False):
        self.session_id = session_id
        self.frustration = frustration
        self.tool_index = {}
        self.buckets = {}  # fingerprint -> candidate dict
        self.frustrations = []

    def feed(self, obj):
        kind = obj.get("type")
        message = obj.get("message") or {}
        content = message.get("content")
        if kind == "assistant" and isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    self.tool_index[item.get("id")] = {
                        "name": item.get("name"),
                        "command": (item.get("input") or {}).get("command", ""),
                    }
            return
        if kind != "user":
            return
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    self._feed_tool_result(item, obj)
        elif self.frustration and isinstance(content, str):
            if _FRUSTRATION_RE.search(content):
                self.frustrations.append({
                    "excerpt": filters.clip(content, FRUSTRATION_LIMIT),
                    "ts": obj.get("timestamp"),
                })

    def _feed_tool_result(self, item, obj):
        info = self.tool_index.get(item.get("tool_use_id")) or {}
        if info.get("name") not in (None, "Bash"):
            # only command execution results carry actionable failures
            if not item.get("is_error"):
                return
        command = info.get("command", "")
        text = _result_text(item)
        top = obj.get("toolUseResult")
        if isinstance(top, str) and top.startswith("Error:"):
            text = text or top
        exit_match = _EXIT_CODE_RE.search(text or "")
        exit_code = int(exit_match.group(1)) if exit_match else None
        envelope = _find_envelope(text or "")
        is_error = bool(item.get("is_error"))
        if exit_code is None and is_error:
            exit_code = 1
        if not filters.should_capture(command, exit_code, stderr_text=text,
                                      has_envelope=envelope is not None):
            return
        component = _component_of(command, info.get("name"))
        tail_lines = (text or "").strip().splitlines()
        message = filters.redact(
            (envelope or {}).get("error")
            or (tail_lines[-1] if tail_lines else ""))
        fprint = fp.compute(component,
                            error_type=(envelope or {}).get("type"),
                            exit_code=exit_code, message=message)
        bucket = self.buckets.setdefault(fprint, {
            "component": component, "command": command,
            "exit_code": exit_code, "envelope": envelope,
            "message": message, "count": 0,
            "excerpt": filters.clip(text or "", EXCERPT_LIMIT),
            "ts": obj.get("timestamp"), "branch": obj.get("gitBranch"),
            "sidechain": bool(obj.get("isSidechain")),
        })
        bucket["count"] += 1

    def candidates(self):
        out = []
        for fprint, bucket in self.buckets.items():
            kind = ("repeated-failure" if bucket["count"] >= REPEAT_THRESHOLD
                    else "tool-error")
            out.append((fprint, kind, bucket))
        for item in self.frustrations:
            out.append((None, "user-friction", item))
        return out


def mine(config, transcript_dirs=None, since=None, session=None,
         include_active=False, frustration=False, limit=None, dry_run=False):
    """Scan transcripts, return (candidates_emitted, stats). Emission =
    building a finding dict; the CLI decides to collect or just print."""
    dirs = ([Path(d) for d in transcript_dirs] if transcript_dirs
            else default_transcript_dirs(config.repo_root))
    state = load_state(config.mine_state_path)
    now = time.time()
    emitted = []
    stats = {"files_scanned": 0, "files_skipped_active": 0,
             "bytes_read": 0, "candidates": 0}

    for directory in dirs:
        for path in sorted(directory.glob("*.jsonl")):
            session_id = path.stem
            if session and session_id != session:
                continue
            try:
                mtime = path.stat().st_mtime
                size = path.stat().st_size
            except OSError:
                continue
            if (not include_active
                    and now - mtime < ACTIVE_SESSION_WINDOW_SEC):
                stats["files_skipped_active"] += 1
                continue
            if since and mtime < since:
                continue
            entry = state["sessions"].get(session_id, {})
            offset = int(entry.get("offset", 0))
            if size < offset:
                offset = 0  # truncated/rewritten: rescan
            if size == offset:
                continue
            miner = SessionMiner(session_id, frustration=frustration)
            with open(path, "rb") as handle:
                handle.seek(offset)
                for raw in handle:
                    try:
                        obj = json.loads(raw.decode("utf-8"))
                    except (ValueError, UnicodeDecodeError):
                        continue
                    miner.feed(obj)
                end_offset = handle.tell()
            stats["files_scanned"] += 1
            stats["bytes_read"] += end_offset - offset

            for fprint, kind, bucket in miner.candidates():
                if limit and len(emitted) >= limit:
                    break
                if kind == "user-friction":
                    record = finding.new_finding(
                        "transcript", kind, "session", bucket["excerpt"],
                        run={"session_id": session_id,
                             "extra": {"ts": bucket.get("ts")}})
                else:
                    record = finding.new_finding(
                        "transcript", kind, bucket["component"],
                        bucket["message"], command=bucket["command"],
                        exit_code=bucket["exit_code"],
                        error_envelope=bucket["envelope"],
                        run={"session_id": session_id, "extra": {
                            "ts": bucket.get("ts"),
                            "branch": bucket.get("branch"),
                            "count": bucket["count"],
                            "sidechain": bucket.get("sidechain"),
                        }},
                        evidence={"excerpts": [
                            {"text": bucket["excerpt"], "source": "transcript"}
                        ]})
                emitted.append(record)
            if not dry_run:
                state["sessions"][session_id] = {
                    "offset": end_offset,
                    "mined_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }

    stats["candidates"] = len(emitted)
    if not dry_run:
        save_state(config.mine_state_path, state)
    return emitted, stats
