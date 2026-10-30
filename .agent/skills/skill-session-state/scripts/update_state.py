#!/usr/bin/env python3
"""Persist the session state of `skill-session-state` in `.agent/sessions/latest.yaml`.

The bootstrap files run this script at each phase boundary. It takes an exclusive lock on
`latest.yaml.lock`, reads the state once, merges the arguments into it and writes it back
(TASK 127):

- the lock is `fcntl.flock` on POSIX and `msvcrt.locking` on Windows, chosen by which of the two
  imports;
- the file is UTF-8 with LF line ends. Its first line is `schema_version: 2`, and each string is
  a JSON string, which is also a YAML double-quoted scalar;
- a file without `schema_version: 2` is read as the script before TASK 127 wrote it, and the
  next write stores the same strings in the new form.

The script refuses a link, or an entry of another kind, at `.agent/sessions`, at the lock file
and at `latest.yaml` (SS-3, TASK 128); a link above them, at `.agent` or a parent directory, is
followed (TASK 128 D14). It writes a temporary file beside the state and moves it onto
`latest.yaml` with `os.replace`, which replaces a link there and writes nothing through it.

Exit codes: 0 the state was written; 1 no lock module, a lock that stayed held, a state file that
is not UTF-8, a link or an entry of another kind, a failed write, or another error; 2 a usage
error. In each case of exit 1 the script writes no state.
"""
import os
import sys

# Run as a script, its own directory leaves the import path before any other import, so a module
# planted beside the script is never imported under the allow rule (WI-39, TASK 127 R6). An entry
# is that directory when its real path, or its device and inode, match the directory of the path
# as called or of the real path. A case-insensitive volume, a linked directory and a linked file
# reach the directory under other spellings. A test that loads the module keeps its own path.
if __name__ == "__main__":
    def _identity(path):
        """`(st_dev, st_ino)` of `path`, or None where it cannot be read or has no inode."""
        try:
            st = os.stat(path)
        except OSError:
            return None
        return (st.st_dev, st.st_ino) if st.st_ino else None

    _DIRS = {os.path.dirname(os.path.abspath(__file__)),
             os.path.dirname(os.path.realpath(__file__))}
    _NAMES = {os.path.normcase(os.path.realpath(path)) for path in _DIRS}
    _IDS = {_identity(path) for path in _DIRS} - {None}
    sys.path[:] = [entry for entry in sys.path
                   if os.path.normcase(os.path.realpath(entry or os.curdir)) not in _NAMES
                   and _identity(entry or os.curdir) not in _IDS]

import argparse  # noqa: E402
import datetime  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import stat  # noqa: E402
import time  # noqa: E402
import uuid  # noqa: E402

# The lock module: `fcntl` where it imports, else `msvcrt` (TASK 127 D10).
try:
    import fcntl  # noqa: E402
except ImportError:
    fcntl = None
    try:
        import msvcrt  # noqa: E402
    except ImportError:
        msvcrt = None
else:
    msvcrt = None

# Constants. The session directory is joined by the platform, so each path that the script
# prints has one form of separator on Windows (TASK 128 R7.3).
SESSION_DIR = os.path.join(".agent", "sessions")
SESSION_FILE = "latest.yaml"
SCHEMA_VERSION = 2
#: Characters that `json.dumps(ensure_ascii=False)` leaves raw and a YAML double-quoted scalar
#: must not hold raw: those outside the YAML 1.2 printable set, and the line breaks U+0085,
#: U+2028 and U+2029 (TASK 127 R3.1).
_YAML_UNSAFE = re.compile("[%s]" % "".join(
    "%s-%s" % (chr(low), chr(high))
    for low, high in ((0x7F, 0x9F), (0x2028, 0x2029), (0xD800, 0xDFFF), (0xFFFE, 0xFFFF))))
#: The version line; the reader takes it from the first line only (TASK 127 R3.3).
_VERSION_LINE = re.compile(r"schema_version:\s*(\d+)\s*")
#: The top-level keys that `generate_yaml` writes; a run drops any other (TASK 138, WI-60).
SCHEMA_KEYS = frozenset({"schema_version", "session_id", "last_updated", "mode", "current_task",
                         "context_summary", "active_blockers", "recent_decisions",
                         "completed_tasks"})
#: A top-level key: a name of word characters, `.` and `-` at column 0, then a colon and a space
#: or the end of the line. A word character is a letter, a digit or `_` of any script, never a
#: control or format character, so a message that quotes it prints no escape sequence (TASK 138
#: D3).
_TOP_KEY = re.compile(r"^(\w[\w.-]*)[ \t]*:(?=[ \t]|$)", re.MULTILINE)
#: The stderr line names at most this many dropped keys, each cut to KEY_NAME_CHARS characters.
DROPPED_NAMES_SHOWN = 20
KEY_NAME_CHARS = 64
#: `os.O_NOFOLLOW` where the platform has it; Windows has none (TASK 128 R2.3).
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction
#: (TASK 128 R2.2).
_NAME_SURROGATE = 0x20000000
#: A move or a removal that fails with `PermissionError` is tried this often, this many seconds
#: apart (TASK 128 R2.5).
_TRIES = 10
_PAUSE = 0.1


class StateError(Exception):
    """A state that the script will not read or lock; the message names the file."""


def find_repo_root():
    """Anchor for SESSION_DIR (SS-1): the state file must land at the repo
    root no matter which subdirectory the protocol is invoked from.

    Resolution order:
    1. Walk up from CWD to the first directory containing `.git`
       (a directory, or a file — linked worktrees).
    2. `CLAUDE_PROJECT_DIR` when set and valid (harness-provided hint).
    3. CWD — legacy behavior for non-git scratch dirs, zero-setup.
    """
    cur = os.path.abspath(os.getcwd())
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir and os.path.isdir(project_dir):
        return os.path.abspath(project_dir)
    return os.path.abspath(os.getcwd())

def get_session_dir():
    """Absolute session dir anchored at the repo root, not CWD."""
    return os.path.join(find_repo_root(), SESSION_DIR)

def get_session_path():
    """Get absolute path to session file."""
    return os.path.join(get_session_dir(), SESSION_FILE)

def ensure_session_dir(session_dir=None):
    """Create the session dir; a second run that creates it at the same time is no error.

    `main` passes the directory that it found once (TASK 128 R2.1)."""
    os.makedirs(session_dir or get_session_dir(), exist_ok=True)

# --- Minimal YAML reader (specific to our schema) ---
# We ONLY need to preserve: session_id, active_blockers, recent_decisions, completed_tasks.
# Everything else (task, mode, summary) is overwritten by the Agent's update.

def _decode(raw, version):
    """One preserved value from its text in the file.

    A version 2 file holds a JSON string, which `json.loads` decodes. A version 1 file, or an item
    that is not a JSON string, is read as the script before TASK 127 read it: one optional quote
    is stripped from each end, then the outer whitespace.
    """
    if version >= SCHEMA_VERSION:
        try:
            value = json.loads(raw)
        except ValueError:
            value = None
        if isinstance(value, str):
            return value
    return re.fullmatch(r"""['"]?(.*?)['"]?""", raw, re.DOTALL).group(1).strip()


def _list_items(content, key, version):
    """The items of the list `key`, each decoded by `_decode`.

    An item is taken to the end of its line, and its trailing whitespace is stripped. A lazy
    capture before a pattern of trailing whitespace backtracks over a run of spaces in a quadratic
    number of steps (SS-6, TASK 128 R3.1).
    """
    section = re.search(r'^' + key + r':\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
    if not section:
        return []
    return [_decode(raw.rstrip(), version)
            for raw in re.findall(r'^\s+-\s+(.*)$', section.group(1), re.MULTILINE)]


def dropped_keys(content):
    """The top-level keys of `content` that the next write drops, in their order, each once.
    Linear in the size of `content`: the run holds the lock while it reads (SS-6)."""
    return list(dict.fromkeys(match.group(1) for match in _TOP_KEY.finditer(content)
                              if match.group(1) not in SCHEMA_KEYS))


def dropped_message(keys):
    """The stderr line that names `keys`, or None for none (TASK 138 R1). Apart from the names
    it is ASCII, for a console or a pipe in any code page."""
    if not keys:
        return None
    shown = [key if len(key) <= KEY_NAME_CHARS else key[:KEY_NAME_CHARS] + "..."
             for key in keys[:DROPPED_NAMES_SHOWN]]
    more = len(keys) - len(shown)
    names = ", ".join(shown) + (" and %d more" % more if more else "")
    return ("update_state.py: dropped keys that it does not write: %s; tell the operator "
            "(skill-session-state SKILL.md section 1, Owner)" % names)


def _warn(message):
    """`message` on stderr. A stderr that cannot take it changes nothing: the state is written
    and the exit stays 0. A closed pipe leaves stderr on the null device, so the flush at exit
    fails no more (TASK 138)."""
    stream = sys.stderr
    if stream is None:
        return
    try:
        print(message, file=stream, flush=True)
    except (OSError, ValueError):
        try:
            null = os.open(os.devnull, os.O_WRONLY)
            os.dup2(null, stream.fileno())
            os.close(null)
        except (OSError, ValueError):
            pass


def parse_simple_yaml(content):
    """
    Robustly extract specific fields from our generated YAML.
    Does NOT aim to be a full YAML parser. `dropped_keys` holds the top-level keys outside the
    schema, which the next write drops.
    """
    match = _VERSION_LINE.fullmatch(content.split("\n", 1)[0])
    version = int(match.group(1)) if match else 1
    data = {
        "session_id": None,
        "active_blockers": _list_items(content, "active_blockers", version),
        "recent_decisions": _list_items(content, "recent_decisions", version),
        "completed_tasks": _list_items(content, "completed_tasks", version),
        "dropped_keys": dropped_keys(content),
    }
    if version >= SCHEMA_VERSION:
        sid = re.search(r'^session_id:\s*(.*)$', content, re.MULTILINE)
        if sid:
            data["session_id"] = _decode(sid.group(1).rstrip(), version) or None
    else:
        sid = re.search(r'^session_id:\s*[\'"]?([^\'"\n]+)[\'"]?', content, re.MULTILINE)
        if sid:
            data["session_id"] = sid.group(1).strip()
    return data


def _scalar(value):
    """`value` as a YAML double-quoted scalar: a JSON string with `_YAML_UNSAFE` escaped."""
    text = json.dumps(str(value), ensure_ascii=False)
    return _YAML_UNSAFE.sub(lambda m: "\\u%04x" % ord(m.group()), text)


def generate_yaml(data):
    """
    Generate clean, valid YAML string.
    """
    lines = [
        f"schema_version: {SCHEMA_VERSION}",
        f"session_id: {_scalar(data.get('session_id'))}",
        f"last_updated: {_scalar(datetime.datetime.now().isoformat())}",
        f"mode: {_scalar(data.get('mode', 'UNKNOWN'))}",
        "",
        "current_task:",
        f"  name: {_scalar(data.get('task_name', 'Unknown Task'))}",
        f"  status: {_scalar(data.get('task_status', 'Initializing'))}",
        f"  predicted_steps: {int(data.get('predicted_steps', 0))}",
        "",
        f"context_summary: {_scalar(data.get('context_summary', '').strip())}",
    ]
    for key in ("active_blockers", "recent_decisions", "completed_tasks"):
        items = data.get(key) or []
        lines += ["", f"{key}:"]
        lines += [f"  - {_scalar(item)}" for item in items] or ["  []"]
    return "\n".join(lines) + "\n"


def read_state(fpath):
    """The preserved fields of the state file `fpath`, or `{}` when it does not exist.

    The read drops a leading byte-order mark (TASK 127 D14).

    Raises:
        StateError: the file is not UTF-8 (TASK 127 R2.3).
    """
    if not os.path.exists(fpath):
        return {}
    try:
        with open(fpath, "r", encoding="utf-8-sig", opener=_opener) as f:
            content = f.read()
    except UnicodeDecodeError as exc:
        raise StateError(f"{fpath} is not UTF-8 (byte {exc.start}: {exc.reason}); "
                         f"save it as UTF-8 or delete it") from None
    return parse_simple_yaml(content)


def _lock(fd):
    """Take the exclusive lock of the state on the lock file `fd`.

    `msvcrt.LK_LOCK` tries 10 times, 1 second apart, and then raises `OSError`; `fcntl.flock`
    waits with no time limit.
    """
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_EX)
    else:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)


def _unlock(fd):
    """Release the lock that `_lock` took."""
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_UN)
    else:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)


def _check_entry(path, directory):
    """Refuse `path` when it is a link, or when it exists and is not a directory (`directory`) or
    a regular file (TASK 128 R2.1, R2.2).

    A link is a symbolic link, or a reparse point whose tag is a name surrogate: a symbolic link
    or a junction of Windows. A cloud or deduplication placeholder is no link. The attributes of
    Windows are read with `getattr` on every platform; only Windows sets them.

    Raises:
        StateError: the message names the path.
    """
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(st.st_mode) or (
            getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
            and getattr(st, "st_reparse_tag", 0) & _NAME_SURROGATE):
        raise StateError(f"{path} is a link; remove it, or replace it with a directory or a "
                         f"regular file of your own")
    if directory and not stat.S_ISDIR(st.st_mode):
        raise StateError(f"{path} is not a directory")
    if not directory and not stat.S_ISREG(st.st_mode):
        raise StateError(f"{path} is not a regular file")


def _opener(path, flags):
    """The opener of the read and of the write of the state (TASK 128 R2.3): the flags that `open`
    hands it, `O_BINARY` on Windows among them, with `O_NOFOLLOW` on POSIX, and the permission
    bits `0o600` for a file that it creates, so no other user opens it before `os.fchmod`."""
    return os.open(path, flags | _NOFOLLOW, 0o600)


def _retry(call, *args):
    """`call(*args)`, tried again on `PermissionError`: at most `_TRIES` tries, `_PAUSE` seconds
    apart (TASK 128 R2.5). On Windows a reader or a scan can hold a file for a moment."""
    for attempt in range(_TRIES):
        try:
            return call(*args)
        except PermissionError:
            if attempt == _TRIES - 1:
                raise
            time.sleep(_PAUSE)


def _write_state(fpath, text):
    """Write `text` to a temporary file beside `fpath`, and move it onto `fpath` (TASK 128 R2.4 to
    R2.6).

    The temporary file is created exclusively, with the bits `0o600`. On POSIX it then takes the
    bits of `fpath` when that is a regular file, and else `0o644` under the umask; a link swapped
    in at `fpath` gives it no bits. It is synced and closed before the move. A failed write or
    move closes the temporary file, removes it, and raises `StateError`.
    """
    tmp = os.path.join(os.path.dirname(fpath), f"{SESSION_FILE}.{uuid.uuid4().hex}.tmp")
    try:
        st = os.lstat(fpath)
    except FileNotFoundError:
        st = None
    if st is not None and stat.S_ISREG(st.st_mode):
        bits = stat.S_IMODE(st.st_mode)
    else:
        umask = os.umask(0)
        os.umask(umask)
        bits = 0o644 & ~umask
    made = False
    try:
        with open(tmp, "x", encoding="utf-8", newline="\n", opener=_opener) as f:
            made = True
            if os.name == "posix":
                os.fchmod(f.fileno(), bits)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        _retry(os.replace, tmp, fpath)
    except Exception as exc:
        stays = ""
        if made:
            try:
                _retry(os.remove, tmp)
            except OSError as left:
                stays = f"; the temporary file {tmp} stays: {left}"
        raise StateError(f"could not write {fpath}: {exc}{stays}") from None


def main():
    # The script's own messages never raise an encoding error on a console or a pipe whose
    # encoding cannot hold a path or a value (TASK 127 R2.2).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    parser = argparse.ArgumentParser(description="Update Session State YAML")
    parser.add_argument("--mode", required=True, help="Current Agent Mode")
    parser.add_argument("--task", required=True, help="Current Task Name")
    parser.add_argument("--status", required=True, help="Current Task Status")
    parser.add_argument("--summary", required=True, help="Task Summary")
    parser.add_argument("--predicted_steps", type=int, default=0, help="Predicted remaining steps")
    parser.add_argument("--add_decision", help="Add a decision to recent_decisions")
    parser.add_argument("--add_blocker", help="Add a blocker item")
    parser.add_argument("--clear_blockers", action="store_true", help="Clear all blockers")
    parser.add_argument("--add_completed_task", help="Add a completed task to history")

    args = parser.parse_args()

    if fcntl is None and msvcrt is None:
        print("Error updating session state: neither fcntl nor msvcrt imports, "
              "and the state needs one of them for its lock")
        sys.exit(1)

    dropped_line = None
    try:
        # No entry of the state is a link, or of another kind (TASK 128 R2.1): the directory
        # before anything is made, the lock file before its open, the state inside the lock.
        # The directory is found once, so the one checked is the one used.
        session_dir = get_session_dir()
        _check_entry(session_dir, directory=True)
        ensure_session_dir(session_dir)
        fpath = os.path.join(session_dir, SESSION_FILE)
        # A separate lock file, opened with no truncation and at position 0 (TASK 127 R1.6).
        lock_path = fpath + ".lock"
        _check_entry(lock_path, directory=False)
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | _NOFOLLOW, 0o644)
        try:
            try:
                _lock(fd)
            except OSError as exc:
                raise StateError(f"could not lock {lock_path}: {exc}") from None
            try:
                _check_entry(fpath, directory=False)
                # The one read of the state, inside the lock (TASK 127 R1.2).
                latest_data = read_state(fpath)

                # Session ID: Persist if exists
                final_session_id = latest_data.get("session_id") or str(uuid.uuid4())

                # Active Blockers: Merge (Union)
                final_blockers = latest_data.get("active_blockers", [])
                if args.clear_blockers:
                    final_blockers = []
                elif args.add_blocker and args.add_blocker not in final_blockers:
                    final_blockers.append(args.add_blocker)

                # Recent Decisions: Append, keep the last 10
                final_decisions = latest_data.get("recent_decisions", [])
                if args.add_decision:
                    final_decisions.append(args.add_decision)
                    if len(final_decisions) > 10:
                        final_decisions = final_decisions[-10:]

                # Completed Tasks: Append
                final_completed = latest_data.get("completed_tasks", [])
                if args.add_completed_task and args.add_completed_task not in final_completed:
                    final_completed.append(args.add_completed_task)

                final_state = {
                    "session_id": final_session_id,
                    "mode": args.mode,
                    "task_name": args.task,
                    "task_status": args.status,
                    "predicted_steps": args.predicted_steps,
                    "context_summary": args.summary,
                    "active_blockers": final_blockers,
                    "recent_decisions": final_decisions,
                    "completed_tasks": final_completed,
                }
                yaml_content = generate_yaml(final_state)
                _write_state(fpath, yaml_content)

                print(f"Session state updated: {fpath} (Locked)")
                # The script owns the file; a key written by hand is gone, and the run says so
                # once the lock is released (TASK 138, WI-60).
                dropped_line = dropped_message(latest_data.get("dropped_keys"))
            finally:
                _unlock(fd)
        finally:
            os.close(fd)
    except Exception as e:
        print(f"Error updating session state: {e}")
        sys.exit(1)
    # The state is written: the line about the dropped keys changes no exit code (TASK 138 R1).
    if dropped_line:
        _warn(dropped_line)

if __name__ == "__main__":
    main()
