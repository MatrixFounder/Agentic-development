"""One atomic-write primitive for the whole engine.

Every writer in this package used to hand-roll `path.with_suffix(".tmp.<pid>")`
+ `write_text` + `os.replace`. Two problems, both real:

  * the temp name is **predictable** inside a directory the repo (or another
    local process) can pre-populate, and `write_text` **follows symlinks** — so a
    planted `<name>.tmp.<pid>` symlink turned any write into an arbitrary-file
    write (vdd-multi S-04, and V-07 for the four sites the first fix missed);
  * a failure between write and replace **leaked** the temp file, which in a
    git-tracked directory is one `git add -A` away from being committed.

`mkstemp` gives an unpredictable name and an O_EXCL|O_NOFOLLOW-equivalent
creation in one call; the temp file is removed on any failure, including
`KeyboardInterrupt`. Mode is copied from the target when it already exists, so
replacing a `0644` ledger does not silently narrow it to `0600` (V-09).

Not durability-complete: `os.replace` is atomic within a directory, but a power
loss can still lose the *directory* entry — no `fsync` of the parent dir. Stated
rather than implied, because the module it replaced claimed more than it did.
"""

from __future__ import annotations

import errno
import os
import stat
import tempfile
import time
from pathlib import Path

from . import locks
from .envelope import EXIT_FILING_CONFLICT, CliError

#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction (TASK 128
#: R2.2, TASK 131 R1.3).
_NAME_SURROGATE = 0x20000000


def is_link(st):
    """True for a symbolic link, or a reparse point whose tag is a name surrogate (a junction).

    Both attributes of Windows are read with `getattr`: only Windows sets them. A cloud
    placeholder is a reparse point with no name surrogate, and is no link.
    """
    return stat.S_ISLNK(st.st_mode) or bool(
        getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        and getattr(st, "st_reparse_tag", 0) & _NAME_SURROGATE)


def check_state_dir(directory):
    """Refuse a directory of the machine state that is a link or a junction.

    The files of the state lie in ``.agent/feedback/``, which comes resolved from the
    config, or in one directory under it, such as ``journal/`` or ``inbox/``. A link
    at such a directory made ``collect`` write outside the repository (TASK 133 R3.2,
    round 2 of stage 2, H1). A link above ``.agent/feedback/``, such as ``/var`` of
    macOS, is the system's and stays allowed.
    """
    try:
        st = os.lstat(str(directory))
    except FileNotFoundError:
        return
    if is_link(st) or not stat.S_ISDIR(st.st_mode):
        raise _state_refused(directory)


def check_state_file(path):
    """Refuse a file of the machine state that a later write would replace, when it is no
    regular file under ``os.lstat``: a link, a junction, a directory or a FIFO.

    `write_atomic` refuses a link at its target only when it runs. For the move of `file`
    that is after the ledger write, and a refusal there left a half-state (TASK 133 R3.2,
    round 4 of stage 2, R4-1).
    """
    try:
        st = os.lstat(str(path))
    except FileNotFoundError:
        return
    if not stat.S_ISREG(st.st_mode):
        raise _state_refused(path)


#: The errors of an open with `O_NOFOLLOW` that a link at the name gives: Linux and macOS
#: give ELOOP, FreeBSD EMLINK, NetBSD EFTYPE.
_LINK_ERRNOS = {errno.ELOOP, errno.EMLINK} | ({errno.EFTYPE} if hasattr(errno, "EFTYPE") else set())


def open_state(path, flags, mode=0o644):
    """Open a file of the machine state; refuse what would let a write leave it.

    The claim, the journal and the two lock files of run-feedback live under the
    gitignored ``.agent/feedback/`` of a repository the agent may not trust. A link
    planted at such a name made ``claim`` write a file outside the repository, and
    ``release`` truncate it; a link at ``inbox/`` made ``collect`` write there, and a
    FIFO made it wait (TASK 133 R3.2). The refusals, each exit 4, writing nothing:
    a directory of the path that a link reaches; a link at the name (``O_NOFOLLOW``
    where ``os`` has it, else ``os.lstat`` before and after the open, and the
    identity of the descriptor after it); a file that is no regular file
    (``O_NONBLOCK``, and ``os.fstat``); a file with a second hard link.
    """
    check_state_dir(os.path.dirname(str(path)))
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        try:
            if is_link(os.lstat(str(path))):
                raise _state_refused(path)
        except FileNotFoundError:
            pass
    try:
        fd = os.open(str(path), flags | (nofollow or 0) | getattr(os, "O_NONBLOCK", 0)
                     | getattr(os, "O_BINARY", 0), mode)
    except OSError as exc:
        if (nofollow is not None and exc.errno in _LINK_ERRNOS) or exc.errno == errno.ENXIO:
            raise _state_refused(path)
        raise
    try:
        st = os.fstat(fd)
        same = True
        if nofollow is None:
            lst = os.lstat(str(path))
            same = (lst.st_dev, lst.st_ino) == (st.st_dev, st.st_ino) and not is_link(lst)
    except BaseException:
        os.close(fd)
        raise
    if not (same and stat.S_ISREG(st.st_mode) and st.st_nlink == 1):
        os.close(fd)
        raise _state_refused(path)
    return fd


def _state_refused(path):
    return CliError("refusing %s: a link, a junction or a file that is not regular stands on "
                    "the path, or the file has a second hard link" % path,
                    code=EXIT_FILING_CONFLICT, err_type="StateRefused",
                    remediation="run-feedback keeps its own state under .agent/feedback/ and "
                                "writes nothing through a link there — remove the entry")


def retried(call, *args):
    """Run *call*; on Windows try it 10 times, 0.1 seconds apart, while it raises
    `PermissionError` (TASK 133 R4, the rule of TASK 128 for `update_state.py`).

    On Windows `os.replace` and `os.unlink` fail while another process holds the file open
    without delete sharing, such as a scanner or an editor. The last error propagates.
    """
    tries = 10 if locks.WINDOWS else 1
    for attempt in range(tries):
        try:
            return call(*args)
        except PermissionError:
            if attempt == tries - 1:
                raise
            time.sleep(0.1)


def read_verbatim(path, encoding="utf-8"):
    """Read a text file WITHOUT newline translation.

    ``Path.read_text`` applies universal newlines, so a CRLF ledger came back as
    LF and every one-line insertion rewrote the whole file's line endings — a
    whole-file diff for a one-line change, in files these writers promise only to
    insert into (vdd-multi F13). It lived in ``ledger_backlog`` only, which is
    why the defect index kept the bug the work-item index no longer had
    (iteration 2, V12). It sits next to ``write_atomic`` because they are one
    invariant read from both ends: a file's own bytes survive a round trip.

    Pair with ``split("\\n")`` on the caller's side — ``str.splitlines()`` also
    breaks on ``\\x0b \\x0c \\x1c-\\x1e \\x85 U+2028 U+2029``, which reintroduces
    the mutation from the parsing side after the read preserved it.
    """
    with open(str(path), encoding=encoding, newline="") as handle:
        return handle.read()


def write_atomic(path, text, encoding="utf-8", newline="", durable=True):
    """Replace *path* with *text* via an unpredictable temp file in the same dir.

    ``newline=""`` by default: callers in this package preserve the file's own
    line endings verbatim and must not have them translated on the way out.

    ``durable=False`` skips the ``fsync``. The ledgers are git-tracked artifacts and
    keep the barrier; the inbox and the journal are regenerable machine state under a
    gitignored dir, and their fsync sat INSIDE the collect flock, so every concurrent
    capture serialized behind an unbounded barrier — on a network or FUSE mount, with
    no timeout (iteration 3, perf). Paying for durability there was a habit, not a
    trade.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # `os.lstat`, not `path.stat()`: stat FOLLOWS a symlink, so the mode was copied
    # from the link's TARGET and a symlink pointing at a 0666 file silently widened
    # the replacement's permissions. And a symlink at the target path is refused
    # outright — `os.replace` would otherwise replace the LINK, leaving the real
    # file untouched while reporting success (iteration 3, sec-L-08).
    mode = None
    try:
        info = os.lstat(str(path))
    except OSError:
        info = None
    if info is not None:
        if is_link(info):
            raise CliError(
                "refusing to replace %s: it is a symlink" % path,
                code=EXIT_FILING_CONFLICT, err_type="FilingConflict",
                remediation="run-feedback writes files, never through links — "
                            "resolve or remove the symlink")
        mode = stat.S_IMODE(info.st_mode)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                    prefix=path.name + ".tmp.")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline=newline) as handle:
            handle.write(text)
            handle.flush()
            if durable:
                os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(tmp_name, mode)
        else:
            os.chmod(tmp_name, 0o644 & ~_umask())
        retried(os.replace, tmp_name, str(path))
    except BaseException:
        try:
            retried(os.unlink, tmp_name)
        except OSError:
            pass
        raise
    return path


def _umask():
    """Read the process umask without permanently changing it."""
    current = os.umask(0o022)
    os.umask(current)
    return current
