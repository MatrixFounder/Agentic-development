"""Inbox operations: scan, fingerprint dedup-merge, consume moves.

Only this module (via the CLI) mutates inbox state; capture surfaces are
told to treat ``collect`` as the sole entry point.
"""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path

from . import atomic, finding as finding_mod
from .envelope import EXIT_NOT_FOUND, CliError


def scan(inbox_dir):
    """Yield (path, record) for every parseable finding JSON in the inbox."""
    inbox_dir = Path(inbox_dir)
    if not inbox_dir.is_dir():
        return []
    out = []
    for path in sorted(inbox_dir.glob("fnd-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue  # torn/foreign file: never let one bad file kill capture
        out.append((path, record))
    return out


def find_by_fingerprint(inbox_dir, fprint):
    for path, record in scan(inbox_dir):
        if record.get("fingerprint") == fprint:
            return path, record
    return None, None


def resolve(config, ref):
    """Resolve a finding reference (id, filename, or path) to (path, record)."""
    candidate = Path(ref)
    if candidate.is_file():
        return candidate, finding_mod.load(candidate)
    name = ref if ref.endswith(".json") else ref + ".json"
    for directory in (config.inbox_dir, config.filed_dir, config.dismissed_dir):
        path = Path(directory) / name
        if path.is_file():
            return path, finding_mod.load(path)
    raise CliError("finding not found: %s" % ref, code=EXIT_NOT_FOUND,
                   err_type="NotFound")


def collect(config, record):
    """Idempotent intake: dedup-merge against the inbox by fingerprint.

    Returns (record, deduped). Serialized by a collect-scoped flock so two
    concurrent captures of the same failure cannot race the merge.
    """
    inbox = Path(config.inbox_dir)
    inbox.mkdir(parents=True, exist_ok=True)
    lock_path = inbox / ".collect.lock"
    fd = os.open(str(lock_path), os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        existing_path, existing = find_by_fingerprint(inbox,
                                                      record["fingerprint"])
        if existing is not None:
            merged = finding_mod.merge_duplicate(existing, record)
            atomic.write_atomic(
                existing_path,
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
            return merged, True
        finding_mod.save(inbox, record)
        return record, False
    finally:
        os.close(fd)


def consume(config, path, record, new_status):
    """Move a finding out of the inbox to filed/ or dismissed/."""
    dest_dir = {"filed": Path(config.filed_dir),
                "dismissed": Path(config.dismissed_dir)}[new_status]
    dest_dir.mkdir(parents=True, exist_ok=True)
    record["status"] = new_status
    finding_mod.save(dest_dir, record)
    try:
        os.unlink(str(path))
    except FileNotFoundError:
        pass
    return dest_dir / (record["finding_id"] + ".json")
