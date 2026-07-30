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

import os
import stat
import tempfile
from pathlib import Path

from .envelope import EXIT_FILING_CONFLICT, CliError


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
        if stat.S_ISLNK(info.st_mode):
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
        os.replace(tmp_name, str(path))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    return path


def _umask():
    """Read the process umask without permanently changing it."""
    current = os.umask(0o022)
    os.umask(current)
    return current
