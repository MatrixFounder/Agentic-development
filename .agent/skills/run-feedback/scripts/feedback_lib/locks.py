"""File locks of run-feedback on POSIX and Windows (TASK 133 R1).

POSIX takes `fcntl.flock` on the descriptor, with no time limit, and the close of the descriptor
releases it, as before TASK 133. Windows has no `fcntl`: there `acquire` locks byte 0 of the same
file with `msvcrt.locking`, which tries 10 times, 1 second apart, and `release` unlocks that byte
before the close. A lock of `msvcrt` is mandatory and has no shared form, so a shared lock is
exclusive there.

`WINDOWS` is true exactly when `fcntl` does not import. The modules that act otherwise on Windows
read it when they run, so a test sets it.
"""

from __future__ import annotations

import os

from .envelope import EXIT_UNEXPECTED, CliError

try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    msvcrt = None

WINDOWS = fcntl is None

#: The errno of `msvcrt.locking` after its 10 tries: `EDEADLOCK` of the Universal C Runtime.
#: `errno.EDEADLOCK` is 35 on Linux and absent on macOS, so the value is held here.
EDEADLOCK = 36


def acquire(fd, path, shared=False):
    """Take the lock of *fd*, the descriptor of *path*; raise `CliError` when it cannot."""
    if fcntl is not None:
        fcntl.flock(fd, fcntl.LOCK_SH if shared else fcntl.LOCK_EX)
        return
    if msvcrt is None:
        raise CliError("cannot lock %s: neither fcntl nor msvcrt imports on this platform"
                       % path, code=EXIT_UNEXPECTED, err_type="LockError")
    os.lseek(fd, 0, os.SEEK_SET)
    try:
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
    except OSError as exc:
        if exc.errno == EDEADLOCK:
            raise CliError("timed out waiting for the lock of %s: another run-feedback process "
                           "holds it" % path, code=EXIT_UNEXPECTED, err_type="LockTimeout")
        raise CliError("cannot lock %s: %s" % (path, exc.strerror or exc),
                       code=EXIT_UNEXPECTED, err_type="LockError")


def release(fd):
    """Release the lock of *fd* before its close; on POSIX the close releases it."""
    if fcntl is not None or msvcrt is None:
        return
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        pass  # the close of the descriptor releases the lock
