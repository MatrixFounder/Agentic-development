"""Re-target the links into the TASK and PLAN slots that a task wrote (TASK 115, WI-38).

`skill-archive-task` Step 8 runs this module as `rebase_links.py --inbound ...`. An allow rule
names `rebase_links.py`, and it passes every argument after `--inbound` to `main(argv)` here, so
archiving stays automatic (TASK 111 D13, TASK 115 D6).

Steps 5.5 and 7.6.5 rebase the links inside the moved documents. A link in another document whose
target resolves to `docs/TASK.md` or `docs/PLAN.md` still names the slot, and the next task's TASK
and PLAN fill it. This module rewrites the slot links the task wrote to the archive paths and lists
every other one:

* own links: every slot link in a sub-task file of the task, and, with `--since <rev>`, every slot
  link on a line added since that revision, except in a ledger record (TASK 115 R3);
* every other slot link of the scan set is recorded as `INBOUND` and left as written;
* the slots, the archived documents and the symbolic links are not rewritten.

Added lines are computed here, from `git cat-file blob`, with `difflib`. No `git diff` runs, so no
diff driver, textconv driver or clean filter runs (TASK 115 D3).

Exit codes of `main`: 0 nothing listed; 1 a rewritten link does not resolve, a write failed after
its first byte, or an unexpected error; 2 an operand, git, `<rev>` or the platform; 3 completed with
`INBOUND`, `REFUSED`, `UNREADABLE` or `SKIPPED` records.
"""
from __future__ import annotations

import argparse
import bisect
import difflib
import errno
import json
import os
import posixpath
import re
import stat
import subprocess
import unicodedata
from typing import NamedTuple, Optional

import rebase_links as _rl
from archive_move import SLUG
from task_id_tool import classify_task_file

#: Slot -> the kind of archive that replaces it, which also names the link text (`task-033`).
SLOTS = {"docs/TASK.md": "task", "docs/PLAN.md": "plan"}
TASK_ARCHIVE_RE = re.compile(rf"docs/tasks/(task-([0-9]{{3,}})-({SLUG})\.md)")
PLAN_ARCHIVE_RE = re.compile(rf"plan-[0-9]{{3,}}-{SLUG}\.md")
#: Ledger records keep their bodies byte for byte (`known-issues-format` §8).
LEDGER_DIRS = ("docs/issues/", "docs/backlog/")
WALK_SKIPS = {".git", "node_modules"}
#: Environment variables that would point a git call at another repository, index or object store.
DROPPED_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                   "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE",
                   "GIT_PREFIX")
GIT_TIMEOUT = 60
#: The largest file read, and the longest text attributed by `difflib` (TASK 115 D12).
MAX_BYTES = 4 << 20
MAX_LINES = 20000
CHUNK = 1 << 16
#: Control and bidirectional formatting characters, escaped in the text output (R7.5).
_UNSAFE = re.compile("[\x00-\x1f\x7f-\x9f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]")
#: Actions that the report lists and that make the exit code 3.
LISTED = ("INBOUND", "REFUSED", "UNREADABLE", "SKIPPED")


class InboundError(Exception):
    """An operand, git, `<rev>` or the platform: nothing was written (exit 2)."""


class InboundRecord(NamedTuple):
    file: str
    line: Optional[int]
    action: str            # RETARGETED | INBOUND | REFUSED | UNREADABLE | SKIPPED
    authored: str          # the target as written
    new_target: str        # the target after the rewrite; empty unless RETARGETED
    reason: str


class InboundResult(NamedTuple):
    records: list
    archived_slot_links: int
    scan: str              # "git" | "walk"
    since: Optional[str]   # the full hash `--since` resolved to
    exit_code: int


class _Link(NamedTuple):
    start: int
    end: int
    line: int
    raw: str               # target text as written, with `<...>` brackets if any
    bare: str              # target without brackets
    path: str              # path part of `bare`
    suffix: str            # `#fragment` or `?query`, kept verbatim
    slot: str              # the slot the path resolves to
    bracket: Optional[int]  # index of the `]` of an inline link, else None


class _Unreadable(Exception):
    pass


class _Refusal(NamedTuple):
    reason: str
    partial: bool          # bytes were written before the failure (R5.3): the run exits 1


def _git_env():
    """The environment of every git call: no redirection, no prompt, no fetch (R6.6)."""
    env = {key: value for key, value in os.environ.items() if key not in DROPPED_GIT_ENV}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    # GIT_NO_LAZY_FETCH needs git 2.44; on an older git this stops the lazy fetch (R6.6).
    env["GIT_ALLOW_PROTOCOL"] = "none"
    return env


def _git(root, *args):
    """stdout of `git -C <root> ...` as bytes; raises InboundError on any failure."""
    command = ["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
               *args]
    try:
        proc = subprocess.run(command, capture_output=True, env=_git_env(), timeout=GIT_TIMEOUT,
                              stdin=subprocess.DEVNULL, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InboundError(f"git {args[0]}: {exc}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        raise InboundError(f"git {args[0]} exited {proc.returncode}"
                           + (f": {detail[-1]}" if detail else ""))
    return proc.stdout


def _toplevel(root):
    """The work tree's top level, or None when `root` is not inside one (walk mode)."""
    try:
        out = _git(root, "rev-parse", "--show-toplevel")
    except InboundError:
        return None
    return os.fsdecode(out.rstrip(b"\n"))


def _resolve(root, since):
    """The full hash of `since`, a commit that is an ancestor of HEAD, or InboundError (R6.2)."""
    if since.startswith("-"):
        raise InboundError(f"--since must not start with '-': {since!r}")
    try:
        out = _git(root, "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}")
    except InboundError as exc:
        raise InboundError(f"--since {since!r} names no commit") from exc
    base = out.decode("ascii", "replace").strip()
    try:
        _git(root, "merge-base", "--is-ancestor", base, "HEAD")
    except InboundError as exc:
        raise InboundError(f"--since {since!r} is not an ancestor of HEAD") from exc
    return base


def _ls_files(root):
    """The tracked and the untracked, not ignored, paths of the work tree (R2.1)."""
    out = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return sorted({os.fsdecode(p) for p in out.split(b"\0") if p})


def _walk(root, unreadable):
    """Every file under `root`, repo-relative; a directory it cannot read goes to `unreadable`."""
    def failed(exc):
        rel = os.path.relpath(exc.filename or root, root).replace(os.sep, "/")
        unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "", exc.strerror or str(exc)))

    found = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=failed):
        dirnames[:] = sorted(d for d in dirnames if d not in WALK_SKIPS
                             and not os.path.isfile(os.path.join(dirpath, d, "pyvenv.cfg")))
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def _read(path):
    """`(bytes, (st_dev, st_ino))` of a regular file, through a descriptor that follows no link."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
    except OSError as exc:
        raise _Unreadable(exc.strerror or str(exc)) from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise _Unreadable("not a regular file")
        if st.st_size > MAX_BYTES:
            raise _Unreadable(f"larger than {MAX_BYTES} bytes")
        chunks, size = [], 0
        while size <= MAX_BYTES and (chunk := os.read(fd, min(CHUNK, MAX_BYTES + 1 - size))):
            chunks.append(chunk)
            size += len(chunk)
        if size > MAX_BYTES:
            raise _Unreadable(f"larger than {MAX_BYTES} bytes")
        return b"".join(chunks), (st.st_dev, st.st_ino)
    except OSError as exc:
        raise _Unreadable(exc.strerror or str(exc)) from exc
    finally:
        os.close(fd)


def _slot_links(text, rel):
    """Every slot link of `text`, a file at repo-relative `rel`, outside fences and code spans."""
    masked = _rl._mask(text)
    brackets = {m.start(1): m.start(0) for m in _rl._INLINE.finditer(masked)}
    newlines = [i for i, ch in enumerate(text) if ch == "\n"]
    base_dir = posixpath.dirname(rel)
    links, seen = [], set()
    for start, end, raw in _rl._targets(masked):
        if (start, end) in seen:
            continue
        seen.add((start, end))
        bare = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        if not bare or _rl._ABSOLUTE.match(bare):
            continue
        path, suffix = _rl._split_fragment(bare)
        if not path:
            continue
        slot = posixpath.normpath(posixpath.join(base_dir, path))
        if slot in SLOTS:
            links.append(_Link(start, end, bisect.bisect_left(newlines, start) + 1, raw, bare,
                               path, suffix, slot, brackets.get(start)))
    return links, masked


def _escaped(text, i):
    """True when `text[i]` follows an odd number of backslashes."""
    count = 0
    while i - 1 - count >= 0 and text[i - 1 - count] == "\\":
        count += 1
    return count % 2 == 1


def _text_span(masked, close):
    """`(open, close)` of the link text ending at `masked[close] == ']'`, or None."""
    depth, i = 0, close - 1
    while i >= 0:
        ch = masked[i]
        if ch == "\n":
            previous = masked.rfind("\n", 0, i)
            if not masked[previous + 1:i].strip():
                return None                      # a blank line ends the paragraph
        elif ch in "[]" and not _escaped(masked, i):
            if ch == "]":
                depth += 1
            elif depth:
                depth -= 1
            else:
                return i, close
        i -= 1
    return None


def _new_text(text, link, digits):
    """The replacement link text, or None when the text is not the slot's name (R4.3)."""
    inner, ticks = text, ""
    if len(text) >= 2 and text[0] == "`" and text[-1] == "`" and not text.startswith("``"):
        inner, ticks = text[1:-1], "`"
    if inner in {link.slot, posixpath.basename(link.slot), link.bare, link.path, link.raw}:
        return f"{ticks}{SLOTS[link.slot]}-{digits}{ticks}"
    return None


def _added_lines(base_text, text):
    """1-based numbers of the lines of `text` that `base_text` lacks (TASK 115 R3)."""
    def lines(value):
        return [part[:-1] if part.endswith("\r") else part for part in value.split("\n")]
    base, work = lines(base_text), lines(text)
    if len(base) > MAX_LINES or len(work) > MAX_LINES:
        return None                              # not attributed (R3.3.6)
    matcher = difflib.SequenceMatcher(None, base, work, autojunk=False)
    added = set()
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag in ("insert", "replace"):
            added.update(range(j1 + 1, j2 + 1))
    return added


def _target(rel, link, archives):
    """The link's new target: the archive's path relative to the linking file's directory."""
    new_path = posixpath.relpath("/" + archives[link.slot], "/" + (posixpath.dirname(rel) or "."))
    new_target = new_path + link.suffix
    return f"<{new_target}>" if link.raw.startswith("<") else new_target


def _rewrite_text(text, masked, rel, links, archives, digits):
    """`text` with each link of `links` re-targeted, and its text renamed where R4.3 applies."""
    edits = []
    for link in links:
        edits.append((link.start, link.end, _target(rel, link, archives)))
        if link.bracket is None:
            continue
        span = _text_span(masked, link.bracket)
        if span is None:
            continue
        if span[0] > 0 and text[span[0] - 1] == "!" and not _escaped(text, span[0] - 1):
            continue                             # an image keeps its alt text
        replacement = _new_text(text[span[0] + 1:span[1]], link, digits)
        if replacement is not None:
            edits.append((span[0] + 1, span[1], replacement))
    out, cursor = [], 0
    for start, end, replacement in sorted(edits):
        if start < cursor:
            return None                          # overlapping links (R4.7)
        out.append(text[cursor:start])
        out.append(replacement)
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def _resolves(root, record):
    """True when a RETARGETED record's new target names an existing archive (R5.5)."""
    target = record.new_target[1:-1] if record.new_target.startswith("<") else record.new_target
    path, _suffix = _rl._split_fragment(target)
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(record.file), path))
    return os.path.isfile(os.path.join(root, resolved))


def _descriptor_path(fd):
    """The path the kernel holds for `fd`, or None where the platform gives none (TASK 116 R7.4).

    `fcntl.F_GETPATH` gives it on darwin, and the link `/proc/self/fd/<fd>` on Linux. It is one
    lookup, so no swap of a directory between two lookups by name can change it, as one can
    between `realpath` and `stat`. A failed lookup raises `OSError`. The same lookup as
    `rebase_links._descriptor_path`, held here since a copy of one module may run beside
    the base of the other.
    """
    try:
        import fcntl
    except ImportError:
        fcntl = None
    if hasattr(fcntl, "F_GETPATH"):
        return os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, bytes(1024)).split(b"\0", 1)[0])
    if os.path.isdir("/proc/self/fd"):
        return os.readlink(f"/proc/self/fd/{fd}")
    return None


def _write_file(root, rel, original, ident, data, dry_run=False):
    """Write `data` over `rel` through a descriptor that follows no link (R5.2, R5.3).

    After the open, the descriptor must be the file at the real path of `rel`, and the directory
    of its own path must lie inside `root` (TASK 116 R7.4). Returns None when the file was
    written, or, in a dry run, would be; else a `_Refusal`. A dry run makes every check of a real
    run and writes nothing (R5.4).
    """
    path = os.path.join(root, rel)
    real_root = os.path.realpath(root)
    parent = os.path.realpath(os.path.dirname(path))
    if os.path.commonpath([parent, real_root]) != real_root:
        return _Refusal("its directory resolves outside the working directory", False)
    if _rl._under_git(rel, root):
        return _Refusal("lies under .git/", False)
    try:
        fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0))
    except OSError as exc:
        return _Refusal(f"cannot open it: {exc.strerror or exc}", False)
    written = 0
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            return _Refusal("is not a regular file", False)
        if st.st_nlink != 1:
            return _Refusal(f"has {st.st_nlink} hard links", False)
        # TASK 116 R7.4: the descriptor is the file at the real path of `rel`, inside the root.
        try:
            real = os.path.realpath(path)
            now = os.stat(real)
            where = _descriptor_path(fd) or real
        except (OSError, ValueError):
            return _Refusal("is not the file at its real path", False)
        if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
            return _Refusal("is not the file at its real path", False)
        if os.path.commonpath([os.path.dirname(where), real_root]) != real_root:
            return _Refusal("its directory resolves outside the working directory", False)
        if (st.st_dev, st.st_ino) != ident:
            return _Refusal("changed during the run", False)
        chunks, size = [], 0
        while size <= len(original) and (chunk := os.read(fd, CHUNK)):
            chunks.append(chunk)
            size += len(chunk)
        if b"".join(chunks) != original:
            return _Refusal("changed during the run", False)
        if dry_run:
            return None
        os.lseek(fd, 0, os.SEEK_SET)
        view = memoryview(data)
        while written < len(data):
            written += os.write(fd, view[written:])
        os.ftruncate(fd, len(data))
        os.fsync(fd)
        now = os.stat(path, follow_symlinks=False)
        if (now.st_dev, now.st_ino) != (st.st_dev, st.st_ino):
            return _Refusal("changed during the run", False)   # an editor saved over it (R5.3)
    except OSError as exc:
        if written:
            return _Refusal(f"partly written: {exc.strerror or exc}", True)
        return _Refusal(f"cannot write it: {exc.strerror or exc}", False)
    finally:
        os.close(fd)
    return None


def _check_archives(root, task_archive, plan_archive):
    """`(digits, {slot: archive})` for the operands of R1.4 and R1.5, or InboundError."""
    match = TASK_ARCHIVE_RE.fullmatch(task_archive or "")
    if not match:
        raise InboundError(f"--task must be docs/tasks/task-<ID>-<slug>.md, not {task_archive!r}")
    name, digits, slug = match.groups()
    _check_regular(root, task_archive)
    kind = classify_task_file(os.path.join(root, "docs", "tasks"), name)
    if kind is None or kind[1]:
        raise InboundError(f"{task_archive} is a sub-task, not a task archive")
    archives = {"docs/TASK.md": task_archive}
    if plan_archive is not None:
        expected = f"docs/plans/plan-{digits}-{slug}.md"
        if plan_archive != expected:
            raise InboundError(f"--plan must be {expected}, not {plan_archive!r}")
        _check_regular(root, plan_archive)
        archives["docs/PLAN.md"] = plan_archive
    return digits, archives


def _check_regular(root, rel):
    """InboundError unless `rel` is a regular file and not a link."""
    try:
        st = os.lstat(os.path.join(root, rel))
    except OSError as exc:
        raise InboundError(f"{rel}: {exc.strerror or exc}") from exc
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise InboundError(f"{rel} is a symbolic link or not a regular file")


def _archived(root, rel, task_id):
    """`(archived, own_subtask)` for a repo-relative path."""
    head, name = posixpath.split(rel)
    if head == "docs/plans":
        return bool(PLAN_ARCHIVE_RE.fullmatch(name)), False
    if head == "docs/tasks":
        kind = classify_task_file(os.path.join(root, "docs", "tasks"), name)
        if kind is not None:
            if not kind[1]:
                return True, False
            return False, kind[0] == task_id
    return False, False


def _scan_set(root, unreadable):
    """`(scan, paths, prefix)`: the `*.md` paths of R2.1 or R2.2, repo-relative and sorted."""
    toplevel = _toplevel(root)
    if toplevel is None:
        return "walk", [p for p in _walk(root, unreadable) if p.endswith(".md")], ""
    real_root, real_top = os.path.realpath(root), os.path.realpath(toplevel)
    if os.path.commonpath([real_root, real_top]) != real_top:
        raise InboundError(f"{root} does not lie inside its git top level {toplevel}")
    paths = {unicodedata.normalize("NFC", p): p for p in _ls_files(root) if p.endswith(".md")}
    try:
        with os.scandir(os.path.join(root, "docs", "tasks")) as entries:
            for entry in entries:
                if entry.name.endswith(".md") and (entry.is_symlink()
                                                  or entry.is_file(follow_symlinks=False)):
                    rel = f"docs/tasks/{entry.name}"
                    paths.setdefault(unicodedata.normalize("NFC", rel), rel)
    except OSError as exc:
        if exc.errno not in (errno.ENOENT, errno.ENOTDIR):
            unreadable.append(InboundRecord("docs/tasks", None, "UNREADABLE", "", "",
                                            exc.strerror or str(exc)))
    prefix = os.fsdecode(_git(root, "rev-parse", "--show-prefix").rstrip(b"\n"))
    return "git", sorted(paths.values()), prefix


def retarget_inbound(repo_root, task_archive, plan_archive=None, since=None, dry_run=False):
    """Re-target the task's own slot links and list the others (TASK 115 R1-R7).

    Args:
        repo_root: the project root; `task_archive` and `plan_archive` are relative to it.
        task_archive: `docs/tasks/task-<ID>-<slug>.md`, an existing parent archive.
        plan_archive: `docs/plans/plan-<ID>-<slug>.md` when Step 7 archived the plan, else None.
        since: the task's base revision; lines added since it are own (R3.2). None: none are.
        dry_run: make every check and write nothing (R5.4).

    Returns:
        InboundResult(records, archived_slot_links, scan, since, exit_code).

    Raises:
        InboundError: an operand, git, `<rev>` or the platform (exit 2); nothing was written.
    """
    if not hasattr(os, "O_NOFOLLOW"):
        raise InboundError("this platform has no O_NOFOLLOW")
    root = os.path.abspath(repo_root)
    digits, archives = _check_archives(root, task_archive, plan_archive)
    task_id = int(digits)
    records = []
    scan, paths, prefix = _scan_set(root, records)
    if since is not None and scan == "walk":
        raise InboundError("--since needs a git work tree")
    base = _resolve(root, since) if since is not None else None
    base_paths = None

    archived_count, writes = 0, []
    for rel in paths:
        if rel in SLOTS:
            continue
        path = os.path.join(root, rel)
        if not os.path.lexists(path):
            continue
        if os.path.islink(path):
            records.append(InboundRecord(rel, None, "SKIPPED", "", "", "symbolic link"))
            continue
        archived, own_file = _archived(root, rel, task_id)
        try:
            data, ident = _read(path)
            text = data.decode("utf-8")
        except (_Unreadable, UnicodeDecodeError) as exc:
            if not archived:
                reason = "not UTF-8" if isinstance(exc, UnicodeDecodeError) else str(exc)
                records.append(InboundRecord(rel, None, "UNREADABLE", "", "", reason))
            continue
        if "TASK.md" not in text and "PLAN.md" not in text:
            continue                             # no slot name: no slot link, no mask cost (L3)
        links, masked = _slot_links(text, rel)
        if not links:
            continue
        if archived:
            archived_count += len(links)
            continue
        added, inbound_reason = None, ""
        if base is not None and not own_file and not rel.lower().startswith(LEDGER_DIRS):
            if base_paths is None:
                listing = _git(root, "ls-tree", "-r", "-z", "--name-only", "--full-tree", base)
                base_paths = {os.fsdecode(p) for p in listing.split(b"\0") if p}
            top_rel = prefix + rel
            if top_rel in base_paths:
                blob = _git(root, "cat-file", "blob", f"{base}:{top_rel}")
                added = _added_lines(blob.decode("utf-8", "replace"), text)
            elif text.count("\n") < MAX_LINES:
                added = range(1, text.count("\n") + 2)
            if added is None:
                added, inbound_reason = set(), f"not attributed: more than {MAX_LINES} lines"
        own = [link for link in links if link.slot in archives
               and (own_file or (added is not None and link.line in added))]
        own_starts = {link.start for link in own}
        for link in links:
            if link.start not in own_starts:
                records.append(InboundRecord(rel, link.line, "INBOUND", link.raw, "",
                                             inbound_reason))
        if own:
            writes.append((rel, data, ident, text, masked, own))

    partial = False
    for rel, data, ident, text, masked, own in writes:
        new_text = _rewrite_text(text, masked, rel, own, archives, digits)
        if new_text is None:
            refusal = _Refusal("overlapping links", False)
        else:
            refusal = _write_file(root, rel, data, ident, new_text.encode("utf-8"), dry_run)
        partial = partial or bool(refusal and refusal.partial)
        for link in own:
            if refusal is None:
                records.append(InboundRecord(rel, link.line, "RETARGETED", link.raw,
                                             _target(rel, link, archives), ""))
            else:
                records.append(InboundRecord(rel, link.line, "REFUSED", link.raw, "",
                                             refusal.reason))

    unresolved = any(r.action == "RETARGETED" and not _resolves(root, r) for r in records)
    records.sort(key=lambda r: (r.file, r.line or 0, r.action))
    if unresolved or partial:
        code = 1
    elif any(r.action in LISTED for r in records):
        code = 3
    else:
        code = 0
    return InboundResult(records, archived_count, scan, base, code)


class _Parser(argparse.ArgumentParser):
    """An argument error is an `InboundError`, so it exits 2 with the stderr object of R7.4."""

    def error(self, message):
        raise InboundError(message)


def _escape(value):
    """`value` with control and bidirectional formatting characters as `\\uXXXX` (R7.5)."""
    return _UNSAFE.sub(lambda m: f"\\u{ord(m.group()):04x}", value)


def _emit(stream, line):
    """Write `line` and a newline; text the stream cannot encode becomes backslash escapes."""
    encoding = getattr(stream, "encoding", None) or "utf-8"
    stream.write(line.encode(encoding, "backslashreplace").decode(encoding, "replace") + "\n")


def _summary(result, dry_run):
    """The last line of the text output (R7.4)."""
    counts = {}
    for record in result.records:
        counts[record.action] = counts.get(record.action, 0) + 1
    listed = sum(counts.get(action, 0) for action in LISTED)
    attributed = (f"lines attributed since {result.since}" if result.since
                  else "lines not attributed")
    return (f"{counts.get('RETARGETED', 0)} retargeted / {listed} listed / "
            f"{result.archived_slot_links} slot links in archived documents (not listed); "
            f"scan {result.scan}; {attributed}" + (" (dry run)" if dry_run else ""))


def main(argv=None):
    """`rebase_links.py --inbound` passes the arguments after `--inbound` here."""
    import sys
    parser = _Parser(prog="rebase_links.py --inbound", allow_abbrev=False,
                     description="Re-target the slot links a task wrote (TASK 115, WI-38).")
    parser.add_argument("--task", required=True, help="docs/tasks/task-<ID>-<slug>.md")
    parser.add_argument("--plan", help="docs/plans/plan-<ID>-<slug>.md, when Step 7 archived it")
    parser.add_argument("--since", help="the task's base revision; lines added since it are own")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else list(argv))
        result = retarget_inbound(os.getcwd(), args.task, args.plan, args.since, args.dry_run)
    except InboundError as exc:
        _emit(sys.stderr, json.dumps({"ok": False, "error": str(exc)}))
        return 2
    except Exception as exc:                      # R7.4: an unexpected error is exit 1
        _emit(sys.stderr, json.dumps({"ok": False,
                                      "error": f"unexpected: {type(exc).__name__}: {exc}"}))
        return 1
    try:
        _report(sys.stdout, result, args.json, args.dry_run)
        sys.stdout.flush()
    except OSError as exc:                        # a closed stdout, after the writes (R7.4)
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except (AttributeError, OSError, ValueError):
            pass                                  # no descriptor: nothing flushes at exit
        try:
            _emit(sys.stderr, json.dumps({"ok": False, "error": f"report not written: {exc}"}))
        except OSError:
            pass
        return 1
    return result.exit_code


def _report(stream, result, as_json, dry_run):
    """The records and the summary line, or the `--json` object (R7.4, R7.5)."""
    if as_json:
        _emit(stream, json.dumps({"ok": result.exit_code in (0, 3),
                                  "exit_code": result.exit_code, "scan": result.scan,
                                  "since": result.since,
                                  "archived_slot_links": result.archived_slot_links,
                                  "records": [r._asdict() for r in result.records]},
                                 ensure_ascii=True, indent=1))
        return
    for r in result.records:
        where = r.file if r.line is None else f"{r.file}:{r.line}"
        line = f"[{r.action}] {_escape(where)}"
        if r.authored:
            line += f"  {_escape(r.authored)}"
        if r.action == "RETARGETED":
            line += f"  ->  {_escape(r.new_target)}"
        if r.reason:
            line += f"  ({_escape(r.reason)})"
        _emit(stream, line)
    _emit(stream, _summary(result, dry_run))
