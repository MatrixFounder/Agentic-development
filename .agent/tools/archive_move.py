#!/usr/bin/env python3
"""Move `docs/TASK.md` or `docs/PLAN.md` into its archive directory, and nothing else.

`skill-archive-task` Steps 5 and 7.6 call this script, and one committed allow rule names it:
`Bash(python3 .agent/tools/archive_move.py *)`. The rule's `*` matches any text, so the script is
the guard (TASK 112 R1). It replaced two `mv` rules whose wildcard also approved a destination
outside the archive directories and extra source operands (WI-35).

It accepts exactly two operand pairs, compared as text:

    docs/TASK.md  docs/tasks/task-<ID>-<slug>.md
    docs/PLAN.md  docs/plans/plan-<ID>-<slug>.md

`<ID>` is three or more digits and `<slug>` is lowercase words joined by `-`, the shapes
`task_id_tool.py` produces. Run it from the project root.

It works through directory descriptors: `docs` and the destination directory are opened with
`O_DIRECTORY | O_NOFOLLOW`, and every file is named relative to them, so a link swapped in for
either directory is refused. It refuses a source that is a link or has a second hard link, and a
destination that exists. It holds the source open from its open to the end of the move, so a file
swapped in under its name meanwhile cannot take its inode number. It moves by a hard link and an
unlink, and copies into an exclusively created file where the file system refuses the hard link.
Any failure after the destination exists removes the destination; the source stays.

Exit codes: 0 moved; 1 refused, nothing changed on disk, except when the error says the archive
was kept; 2 usage error or a platform without `dir_fd` support. Any `OSError`, such as an overlong
name, is a refusal. One JSON object goes to stdout on success, to stderr otherwise.
"""
import os
import sys

# Run as a script, its own directory leaves the import path before any other import, so a module
# planted beside the script is never imported under the allow rule. A test that loads the module
# keeps its own path (TASK 112 R1.8).
if __name__ == "__main__":
    _HERE = os.path.dirname(os.path.realpath(__file__))
    sys.path[:] = [entry for entry in sys.path if os.path.realpath(entry or os.curdir) != _HERE]

import errno  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import stat  # noqa: E402

USAGE = ("usage: archive_move.py docs/TASK.md docs/tasks/task-<ID>-<slug>.md\n"
         "       archive_move.py docs/PLAN.md docs/plans/plan-<ID>-<slug>.md")
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
#: source operand -> (destination directory under docs/, archive file name)
PAIRS = {
    "docs/TASK.md": ("tasks", re.compile(rf"task-[0-9]{{3,}}-{SLUG}\.md")),
    "docs/PLAN.md": ("plans", re.compile(rf"plan-[0-9]{{3,}}-{SLUG}\.md")),
}
#: errno values of a file system that has no hard links for this file; the copy path takes over.
NO_HARD_LINK = {errno.EPERM, errno.EXDEV, errno.EMLINK, errno.ENOSYS,
                getattr(errno, "ENOTSUP", errno.EPERM), getattr(errno, "EOPNOTSUPP", errno.EPERM)}
CHUNK = 1 << 16


class Refused(Exception):
    """An operand, a link or an existing file the script will not move or write through."""


def _fail(code, message):
    print(json.dumps({"ok": False, "error": message}), file=sys.stderr)
    return code


def _supported():
    """`dir_fd` support for every call `_move` makes, read by name from `os.supports_*`."""
    dir_fd = {call.__name__ for call in os.supports_dir_fd}
    no_follow = {call.__name__ for call in os.supports_follow_symlinks}
    return ({"open", "mkdir", "rmdir", "link", "unlink", "stat"} <= dir_fd
            and "link" in no_follow
            and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"))


def _parse(source, destination):
    """The source name in `docs`, the destination directory and the archive name, or Refused."""
    if source not in PAIRS:
        raise Refused(f"source must be docs/TASK.md or docs/PLAN.md, not {source!r}")
    subdir, pattern = PAIRS[source]
    prefix = f"docs/{subdir}/"
    name = destination[len(prefix):] if destination.startswith(prefix) else None
    if name is None or not pattern.fullmatch(name):
        raise Refused(f"destination for {source} must be {prefix}{pattern.pattern}, "
                      f"not {destination!r}")
    return source[len("docs/"):], subdir, name


def _open_dir(name, parent_fd=None):
    """A descriptor of directory `name`, never through a link."""
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except FileNotFoundError:
        raise
    except OSError as exc:
        if exc.errno in (errno.ELOOP, errno.ENOTDIR):
            raise Refused(f"{name!r} is a symbolic link or not a directory") from exc
        raise Refused(f"cannot open {name!r}: {exc.strerror}") from exc


def _same_file(st, ref):
    return st.st_ino == ref.st_ino and st.st_dev == ref.st_dev


def _check_source(docs_fd, name):
    """`(descriptor, fstat of it)` of the source; the caller closes the descriptor after the move.

    The `lstat` checks come first, so nothing but a regular file is opened. The open descriptor
    keeps the source's inode allocated, so no file swapped in under the same name afterwards can
    receive its inode number, and `_same_file` stays sound (ext4 can give a freed number to the
    next new file).
    """
    try:
        st = os.stat(name, dir_fd=docs_fd, follow_symlinks=False)
    except FileNotFoundError as exc:
        raise Refused(f"docs/{name} does not exist") from exc
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISREG(st.st_mode):
        raise Refused(f"docs/{name} is a symbolic link or not a regular file")
    if st.st_nlink != 1:
        raise Refused(f"docs/{name} has {st.st_nlink} hard links")
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=docs_fd)
    except OSError as exc:
        raise Refused(f"cannot open docs/{name}: {exc.strerror}") from exc
    try:
        held = os.fstat(fd)
        if not (stat.S_ISREG(held.st_mode) and _same_file(held, st) and held.st_nlink == 1):
            raise Refused("the source changed during the move")
    except BaseException:
        _close(fd)
        raise
    return fd, held


def _exists(name, dir_fd):
    try:
        os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def _remove(name, dir_fd):
    try:
        os.unlink(name, dir_fd=dir_fd)
    except FileNotFoundError:
        pass


def _close(fd):
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass


def _link(docs_fd, src, sub_fd, dst, ref):
    """Hard-link `dst` to `src`; None when the file system has no hard link for it."""
    try:
        os.link(src, dst, src_dir_fd=docs_fd, dst_dir_fd=sub_fd, follow_symlinks=False)
    except FileExistsError as exc:
        raise Refused("the destination exists") from exc
    except OSError as exc:
        if exc.errno in NO_HARD_LINK:
            return None
        raise Refused(f"cannot link the destination: {exc.strerror}") from exc
    try:
        st = os.stat(dst, dir_fd=sub_fd, follow_symlinks=False)
    except OSError as exc:
        _remove(dst, sub_fd)
        raise Refused(f"cannot check the destination: {exc.strerror}") from exc
    if not (stat.S_ISREG(st.st_mode) and _same_file(st, ref) and st.st_nlink == 2):
        _remove(dst, sub_fd)
        raise Refused("the source changed during the move")
    return "link"


def _copy(docs_fd, src, sub_fd, dst, ref):
    """Copy `src` into an exclusively created `dst`."""
    try:
        src_fd = os.open(src, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=docs_fd)
    except OSError as exc:
        raise Refused(f"cannot open docs/{src}: {exc.strerror}") from exc
    try:
        st = os.fstat(src_fd)
        if not (stat.S_ISREG(st.st_mode) and _same_file(st, ref) and st.st_nlink == 1):
            raise Refused("the source changed during the move")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        try:
            dst_fd = os.open(dst, flags, stat.S_IMODE(st.st_mode), dir_fd=sub_fd)
        except FileExistsError as exc:
            raise Refused("the destination exists") from exc
        except OSError as exc:
            raise Refused(f"cannot create the destination: {exc.strerror}") from exc
        try:
            while chunk := os.read(src_fd, CHUNK):
                view = memoryview(chunk)
                while view:
                    view = view[os.write(dst_fd, view):]
            os.fsync(dst_fd)
            os.close(dst_fd)
        except OSError as exc:
            _close(dst_fd)
            _remove(dst, sub_fd)
            raise Refused(f"cannot copy the source: {exc.strerror}") from exc
    finally:
        _close(src_fd)
    return "copy"


def _undo_after_failed_unlink(docs_fd, src, sub_fd, subdir, dst, ref, exc):
    """The error text after the source's unlink failed; removes the archive only when it is a copy.

    While `docs/<src>` still holds the moved file, the archive is a second name or a copy of it,
    and it is removed. When the source is gone or holds another file, the archive is the content's
    last name, and it stays.
    """
    where = f"docs/{subdir}/{dst}"
    try:
        still = _same_file(os.stat(src, dir_fd=docs_fd, follow_symlinks=False), ref)
    except FileNotFoundError:
        return f"cannot remove docs/{src} ({exc.strerror}); it is gone, so {where} is kept"
    except OSError as check:
        return (f"cannot remove docs/{src} ({exc.strerror}) or confirm what it holds "
                f"({check.strerror}); both it and {where} are kept")
    if not still:
        return (f"cannot remove docs/{src} ({exc.strerror}); it no longer holds the moved file, "
                f"so {where} is kept")
    try:
        _remove(dst, sub_fd)
    except OSError as cleanup:
        return (f"cannot remove docs/{src} ({exc.strerror}), and {where} remains "
                f"({cleanup.strerror})")
    return f"cannot remove docs/{src}: {exc.strerror}"


def _move(src, subdir, dst):
    """Move `docs/<src>` to `docs/<subdir>/<dst>`; on any failure, undo what this run made.

    The source is unlinked only after the destination holds its content, and a failure after the
    destination exists removes it (`_link`, `_copy`, the unlink below). Every `OSError` becomes a
    refusal, and a directory this run created is removed again.
    """
    try:
        docs_fd = _open_dir("docs")
    except FileNotFoundError as exc:
        raise Refused("docs does not exist") from exc
    src_fd, sub_fd, created = None, None, False
    try:
        src_fd, ref = _check_source(docs_fd, src)
        try:
            sub_fd = _open_dir(subdir, docs_fd)
        except FileNotFoundError:
            os.mkdir(subdir, dir_fd=docs_fd)
            created = True
            sub_fd = _open_dir(subdir, docs_fd)
        if _exists(dst, sub_fd):
            raise Refused("the destination exists")
        method = _link(docs_fd, src, sub_fd, dst, ref) or _copy(docs_fd, src, sub_fd, dst, ref)
        try:
            os.unlink(src, dir_fd=docs_fd)
        except OSError as exc:
            raise Refused(_undo_after_failed_unlink(docs_fd, src, sub_fd, subdir, dst, ref,
                                                    exc)) from exc
    except (Refused, OSError) as exc:
        if created:
            try:
                os.rmdir(subdir, dir_fd=docs_fd)
            except OSError:
                pass
        if isinstance(exc, Refused):
            raise
        raise Refused(f"{exc.strerror or exc}: {exc.filename or ''}".rstrip(": ")) from exc
    finally:
        _close(src_fd)
        _close(sub_fd)
        _close(docs_fd)
    return {"method": method, "created_directory": created}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if len(argv) != 2 or any(arg.startswith("-") for arg in argv):
        return _fail(2, USAGE)
    if not _supported():
        return _fail(2, "this platform has no dir_fd support for open, mkdir, link and unlink")
    source, destination = argv
    try:
        result = _move(*_parse(source, destination))
    except Refused as exc:
        return _fail(1, str(exc))
    print(json.dumps({"ok": True, "source": source, "destination": destination, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
