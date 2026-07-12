"""Append-only run-feedback journal.

Markdown, monthly rotation (``<journal_dir>/YYYY-MM.md``), grep-friendly
entry headers::

    ## [YYYY-MM-DD HH:MM:SS] <event_type> | <subject>
    - key: value

Atomic under concurrency: O_APPEND + flock(LOCK_EX) + full-write loop +
fsync (pattern proven by the obsidian-llm-wiki log writer; implemented
fresh here — stdlib only). Lives under the gitignored ``.agent/feedback/``
so appends never dirty the git tree (heal-issues preconditions depend on
this).
"""

from __future__ import annotations

import fcntl
import os
import re
import time
from pathlib import Path

_HEADER_SANITIZE_RE = re.compile(r"[\r\n|]+")
_EVENT_TYPE_RE = re.compile(r"^[a-z][a-z0-9_\-]*$")

KNOWN_EVENT_TYPES = frozenset({
    "finding_collected", "finding_deduped", "finding_filed",
    "finding_dismissed", "session_end", "mine_run",
    "retro_claimed", "retro_released",
    "heal_run", "heal_attempt", "heal_blocked",
})


def _sanitize(value, limit=200):
    value = _HEADER_SANITIZE_RE.sub(" ", str(value or "")).strip()
    if value.startswith("#"):
        value = value.lstrip("#").strip()
    return value[:limit]


def journal_path(journal_dir, ts=None):
    ts = ts if ts is not None else time.time()
    return Path(journal_dir) / (time.strftime("%Y-%m", time.localtime(ts)) + ".md")


def render_entry(event_type, subject, details=None, ts=None):
    ts = ts if ts is not None else time.time()
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
    lines = ["## [%s] %s | %s" % (stamp, _sanitize(event_type, 60),
                                  _sanitize(subject))]
    for key, value in (details or {}).items():
        lines.append("- %s: %s" % (_sanitize(key, 60), _sanitize(value, 500)))
    return "\n".join(lines) + "\n\n"


def append_event(journal_dir, event_type, subject, details=None, ts=None):
    """Append one entry; returns the byte offset the entry starts at."""
    event_type = str(event_type or "").strip()
    if not _EVENT_TYPE_RE.match(event_type):
        raise ValueError("invalid event_type: %r" % event_type)
    path = journal_path(journal_dir, ts)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = render_entry(event_type, subject, details, ts).encode("utf-8")

    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        offset = os.lseek(fd, 0, os.SEEK_END)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
        return offset
    finally:
        # closing releases the flock
        os.close(fd)
