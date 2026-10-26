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

Exit codes: 0 the state was written; 1 no lock module, a lock that stayed held, a state file that
is not UTF-8, or another error; 2 a usage error. In the first three cases of exit 1 the script
writes nothing.
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

# Constants
SESSION_DIR = ".agent/sessions"
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

def ensure_session_dir():
    """Create the session dir; a second run that creates it at the same time is no error."""
    os.makedirs(get_session_dir(), exist_ok=True)

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
    """The items of the list `key`, each decoded by `_decode`."""
    section = re.search(r'^' + key + r':\s*\n((?:\s+-\s+.*(?:\n|$))*)', content, re.MULTILINE)
    if not section:
        return []
    return [_decode(raw, version)
            for raw in re.findall(r'^\s+-\s+(.*?)\s*$', section.group(1), re.MULTILINE)]


def parse_simple_yaml(content):
    """
    Robustly extract specific fields from our generated YAML.
    Does NOT aim to be a full YAML parser.
    """
    match = _VERSION_LINE.fullmatch(content.split("\n", 1)[0])
    version = int(match.group(1)) if match else 1
    data = {
        "session_id": None,
        "active_blockers": _list_items(content, "active_blockers", version),
        "recent_decisions": _list_items(content, "recent_decisions", version),
        "completed_tasks": _list_items(content, "completed_tasks", version),
    }
    if version >= SCHEMA_VERSION:
        sid = re.search(r'^session_id:\s*(.*?)\s*$', content, re.MULTILINE)
        if sid:
            data["session_id"] = _decode(sid.group(1), version) or None
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
        with open(fpath, "r", encoding="utf-8-sig") as f:
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

    try:
        ensure_session_dir()
        fpath = get_session_path()
        # A separate lock file, opened with no truncation and at position 0 (TASK 127 R1.6).
        lock_path = fpath + ".lock"
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            try:
                _lock(fd)
            except OSError as exc:
                raise StateError(f"could not lock {lock_path}: {exc}") from None
            try:
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

                with open(fpath, "w", encoding="utf-8", newline="\n") as f:
                    f.write(yaml_content)

                print(f"Session state updated: {fpath} (Locked)")
            finally:
                _unlock(fd)
        finally:
            os.close(fd)
    except Exception as e:
        print(f"Error updating session state: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
