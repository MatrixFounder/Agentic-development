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
from .envelope import EXIT_NOT_FOUND, EXIT_USAGE, CliError


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
    """Locate an inbox record by fingerprint via the filename, not a full scan.

    **Invariant this relies on:** ``finding.save`` names every file
    ``<finding_id>.json`` and ``finding_id`` is ``fnd-<stamp>-<fingerprint[:8]>``
    — so the lookup key is already in the name and the lookup is a glob. It used
    to open and ``json.loads`` *every* file in the inbox to answer one yes/no
    question, under an exclusive lock, inside the fire-and-forget capture path.
    The inbox only drains when a human triages, so *k* captures without triage
    did 1+2+…+k reads — O(k²), roughly 20 100 parses at 200 stale findings (WI-5).

    The 8-char prefix is not unique, so the FULL fingerprint is still verified on
    every candidate. There is deliberately no full-scan fallback on a miss: a miss
    is the *common* case (a genuinely new finding), so falling back would restore
    the O(k²) this removes. The cost is that a hand-renamed inbox file no longer
    dedups — a trade recorded in TASK 093 §4 rather than discovered later.
    """
    inbox_dir = Path(inbox_dir)
    if not inbox_dir.is_dir():
        return None, None
    for path in sorted(inbox_dir.glob("fnd-*-%s.json" % str(fprint)[:8])):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue  # torn/foreign file: never let one bad file kill capture
        if record.get("fingerprint") == fprint:
            return path, record
    return None, None


def _within(path, directories):
    """True when *path* resolves inside one of *directories*."""
    try:
        resolved = path.resolve()
    except (OSError, ValueError):
        # ValueError: an embedded NUL byte reaches resolve() as a traceback
        return False
    for directory in directories:
        try:
            root = Path(directory).resolve()
        except (OSError, ValueError):
            continue
        if resolved == root or root in resolved.parents:
            return True
    return False


def resolve(config, ref):
    """Resolve a finding reference (id, filename, or path) to (path, record).

    A bare path is accepted only when it lands inside the feedback dirs. It used
    to accept ANY readable JSON file with a ``finding_id``, and ``consume`` then
    **unlinked the original** — so ``file --finding ./somebody/state.json --as
    noise --reason x`` deleted a file outside every configured ledger path, while
    SKILL.md §5 says those paths are the entire write scope (WI-6). The operator
    supplies the path, so this was a footgun rather than an exploit; a tool that
    documents "writes only inside X" still has to enforce containment on the paths
    it *deletes*, not only the ones it creates.
    """
    directories = (config.inbox_dir, config.filed_dir, config.dismissed_dir)

    def contained(path):
        if _within(path, directories):
            return path
        raise CliError(
            "finding reference %r resolves outside the feedback directories" % ref,
            code=EXIT_USAGE, err_type="UsageError",
            remediation="pass a bare finding id, or copy the record into %s "
                        "first — filing MOVES the record, and run-feedback must "
                        "not delete files outside its own state dir"
                        % config.inbox_dir)

    candidate = Path(ref)
    if candidate.is_file():
        return contained(candidate), finding_mod.load(candidate)
    name = ref if ref.endswith(".json") else ref + ".json"
    for directory in directories:
        # `contained` on THIS branch too. Guarding only the branch above was a fix
        # that covered one of two paths — and the unguarded one is the path a ref
        # without a `.json` suffix *necessarily* takes, so `--finding
        # ../../../victim` read a foreign JSON and `consume` then UNLINKED it
        # (verified exploit, iteration 3 H-04: the WI-6 exploit surviving on the
        # sibling code path, which is the third instance of this class in as many
        # iterations).
        path = Path(directory) / name
        if path.is_file():
            return contained(path), finding_mod.load(path)
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
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
                durable=False)
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
