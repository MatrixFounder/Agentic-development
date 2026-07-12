"""Finding record (schema v1) — the canonical intermediate between capture
and filing. One JSON file per finding in the inbox.

Lifecycle: ``new`` -> ``filed`` | ``dismissed`` (moved to the sibling
``filed/`` / ``dismissed/`` dirs, never deleted — audit trail).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from . import fingerprint as fp
from .envelope import EXIT_NOT_FOUND, CliError

SCHEMA_VERSION = 1

SOURCES = ("workflow", "skill", "command", "test", "ci", "hook", "transcript")
KINDS = ("tool-error", "gate-failure", "test-failure", "review-finding",
         "blocker", "repeated-failure", "user-friction", "session-end")
CLASSIFICATIONS = ("defect", "work-item", "noise", "unknown")


def _now_iso(ts=None):
    ts = ts if ts is not None else time.time()
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def new_finding(source, kind, component, message, command=None, exit_code=None,
                error_envelope=None, run=None, evidence=None, proposed=None,
                ts=None):
    if source not in SOURCES:
        raise ValueError("unknown source: %r (expected one of %s)"
                         % (source, ", ".join(SOURCES)))
    if kind not in KINDS:
        raise ValueError("unknown kind: %r (expected one of %s)"
                         % (kind, ", ".join(KINDS)))
    error_type = (error_envelope or {}).get("type")
    fprint = fp.compute(component, error_type=error_type,
                        exit_code=exit_code, message=message)
    stamp = _now_iso(ts)
    compact = time.strftime("%Y%m%d-%H%M%S",
                            time.localtime(ts if ts is not None else time.time()))
    return {
        "v": SCHEMA_VERSION,
        "finding_id": "fnd-%s-%s" % (compact, fprint[:8]),
        "fingerprint": fprint,
        "status": "new",
        "captured_at": stamp,
        "first_seen": stamp,
        "last_seen": stamp,
        "occurrences": 1,
        "sources": [source],
        "kind": kind,
        "run": dict(run or {}),
        "subject": {
            "component": component,
            "command": command,
            "exit_code": exit_code,
            "error_envelope": error_envelope,
            "message": message,
        },
        "evidence": {
            "paths": list((evidence or {}).get("paths") or []),
            "excerpts": list((evidence or {}).get("excerpts") or []),
        },
        "proposed": dict(proposed or {}),
        "filed_as": None,
    }


def merge_duplicate(existing, incoming):
    """Fold *incoming* (same fingerprint) into *existing*; returns existing."""
    existing["occurrences"] = int(existing.get("occurrences", 1)) + 1
    existing["last_seen"] = incoming.get("last_seen") or _now_iso()
    for source in incoming.get("sources", ()):
        if source not in existing.setdefault("sources", []):
            existing["sources"].append(source)
    known_paths = set(existing["evidence"].setdefault("paths", []))
    for path in incoming.get("evidence", {}).get("paths", ()):
        if path not in known_paths:
            existing["evidence"]["paths"].append(path)
            known_paths.add(path)
    # keep run context of the FIRST capture; later contexts go to extra
    extra = existing.setdefault("run", {}).setdefault("extra", {})
    later = {k: v for k, v in (incoming.get("run") or {}).items()
             if v and k != "extra"}
    if later:
        extra.setdefault("later_runs", []).append(later)
    return existing


def save(directory, record):
    """Atomic write (tmp + os.replace); returns the target path."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (record["finding_id"] + ".json")
    tmp = target.with_suffix(".json.tmp.%d" % os.getpid())
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(str(tmp), str(target))
    return target


def load(path):
    path = Path(path)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CliError("finding not found: %s" % path, code=EXIT_NOT_FOUND,
                       err_type="NotFound")
    except (OSError, json.JSONDecodeError) as exc:
        raise CliError("finding unreadable: %s (%s)" % (path, exc),
                       code=EXIT_NOT_FOUND, err_type="NotFound")
    return record
