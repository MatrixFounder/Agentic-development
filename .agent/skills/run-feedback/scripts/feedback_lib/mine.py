"""Transcript miner: extract failure signals from Claude Code session logs.

Claude Code shards transcripts per-cwd under ``~/.claude/projects/`` (a
session launched inside ``skills/html`` lands in a DIFFERENT dir than one
launched at the repo root). Claude Code 2.1.306 names that dir after the path:
each UTF-16 code unit outside ``[A-Za-z0-9]`` becomes ``-``, and a name longer
than 200 characters keeps its first 200, with ``-`` and a hash appended. The
name cannot be decoded, so discovery takes each dir named as the root, or
starting with that name and ``-``, comparing the first 200 characters, without
letter case on Windows. A sibling such as ``<root>-old`` matches by name too, so
each session file is read only when the first line of it that carries ``cwd``
names the root or a path under it (TASK 133 R5).

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
import stat
import time
from pathlib import Path

from . import atomic, filters, finding, locks
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


_ALNUM = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
#: Claude Code cuts a longer name to this many characters and appends `-` and a hash.
NAME_LIMIT = 200


def encode_project_dir(path):
    """The name Claude Code 2.1.306 gives the transcript dir of *path* (TASK 133 R5.1).

    Its rule is ``replace(/[^a-zA-Z0-9]/g, "-")`` over UTF-16 code units, so a character
    outside the Basic Multilingual Plane, two code units, gives two ``-``.
    """
    return "".join(c if c in _ALNUM else ("--" if ord(c) > 0xFFFF else "-")
                   for c in str(path))


def default_transcript_dirs(repo_root, projects_dir=None):
    return match_transcript_dirs(str(Path(repo_root).resolve()), projects_dir)


def match_transcript_dirs(root_text, projects_dir=None):
    """Each dir of *projects_dir* named as the root *root_text*, or starting with that
    name and ``-`` (TASK 133 R5.2, R5.3).

    A name longer than ``NAME_LIMIT`` is compared on its first ``NAME_LIMIT``
    characters. On Windows the names are compared after ``str.casefold``: NTFS ignores
    letter case, and the drive letter of the root may differ in case from the one that
    Claude Code read.
    """
    projects = Path(projects_dir or (Path.home() / ".claude" / "projects"))
    if not projects.is_dir():
        return []
    fold = str.casefold if locks.WINDOWS else (lambda text: text)
    prefix = fold(encode_project_dir(root_text)[:NAME_LIMIT])
    return sorted(d for d in projects.iterdir()
                  if d.is_dir() and (fold(d.name) == prefix
                                     or fold(d.name).startswith(prefix + "-")))


def _open_regular(path):
    """*path* open for reading, or None when it is no regular file (TASK 133 R5.4).

    ``O_NONBLOCK`` keeps a FIFO, swapped in after the ``stat`` of the caller, from
    blocking the open; ``os.fstat`` then decides on the descriptor itself.
    """
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
                 | getattr(os, "O_BINARY", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            return None
        return os.fdopen(fd, "rb")
    except BaseException:
        os.close(fd)
        raise


def _first_cwd(path):
    """The ``cwd`` of the first line of *path* that carries one, or None."""
    try:
        handle = _open_regular(path)
        if handle is None:
            return None
        with handle:
            for raw in handle:
                try:
                    obj = json.loads(raw)
                except ValueError:
                    continue
                if isinstance(obj, dict) and isinstance(obj.get("cwd"), str):
                    return obj["cwd"]
    except OSError:
        return None
    return None


def _session_of_root(path, root_text):
    """True when the first ``cwd`` of the session file *path* is the root or under it
    (TASK 133 R5.4)."""
    cwd = _first_cwd(path)
    if cwd is None:
        return False
    # text only: a link is not resolved, so a `cwd` such as a UNC path opens no connection
    here = os.path.normcase(os.path.normpath(cwd))
    root = os.path.normcase(os.path.normpath(root_text))
    if locks.WINDOWS:
        here, root = here.casefold(), root.casefold()
    return here == root or here.startswith(root.rstrip(os.sep) + os.sep)


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
         include_active=False, frustration=False, limit=None, dry_run=False,
         projects_dir=None):
    """Scan transcripts, return (candidates_emitted, stats). Emission =
    building a finding dict; the CLI decides to collect or just print.

    *projects_dir* replaces ``~/.claude/projects`` for the default dirs (TASK 133
    R5.6). With explicit *transcript_dirs* each file is read, as before; with the
    default dirs a session file of another root is skipped (R5.4)."""
    root_text = None
    if transcript_dirs:
        dirs = [Path(d) for d in transcript_dirs]
    else:
        root_text = str(Path(config.repo_root).resolve())
        dirs = default_transcript_dirs(config.repo_root, projects_dir)
    state = load_state(config.mine_state_path)
    now = time.time()
    emitted = []
    stats = {"files_scanned": 0, "files_skipped_active": 0,
             "files_skipped_foreign": 0, "bytes_read": 0, "candidates": 0}

    for directory in dirs:
        for path in sorted(directory.glob("*.jsonl")):
            session_id = path.stem
            if session and session_id != session:
                continue
            try:
                st = path.stat()
            except OSError:
                continue
            if not stat.S_ISREG(st.st_mode):
                continue  # a FIFO or a device would block the read (round 1 of stage 2, L1)
            mtime, size = st.st_mtime, st.st_size
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
            if root_text is not None and not _session_of_root(path, root_text):
                stats["files_skipped_foreign"] += 1
                continue
            miner = SessionMiner(session_id, frustration=frustration)
            try:
                handle = _open_regular(path)
            except OSError:
                continue
            if handle is None:
                continue
            with handle:
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
