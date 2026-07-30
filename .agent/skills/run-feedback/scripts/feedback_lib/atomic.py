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


def write_atomic(path, text, encoding="utf-8", newline=""):
    """Replace *path* with *text* via an unpredictable temp file in the same dir.

    ``newline=""`` by default: callers in this package preserve the file's own
    line endings verbatim and must not have them translated on the way out.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = None
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError:
        pass
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                    prefix=path.name + ".tmp.")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline=newline) as handle:
            handle.write(text)
            handle.flush()
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
