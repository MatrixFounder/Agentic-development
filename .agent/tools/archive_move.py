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

Where the platform has `dir_fd`, `_move` works through directory descriptors: `docs` and the
destination directory are opened with `O_DIRECTORY | O_NOFOLLOW`, and every file is named relative
to them, so a link swapped in for either directory is refused. It refuses a source that is a link
or has a second hard link, and a destination that exists. It holds the source open from its open
to the end of the move, so a file swapped in under its name meanwhile cannot take its inode
number. It moves by a hard link and an unlink, and copies into an exclusively created file where
the file system refuses the hard link. Any failure after the destination exists removes the
destination; the source stays.

Where it has none, Windows among them, `_move_by_path` moves by path (TASK 131 R1). A link is a
symbolic link or a junction: a reparse point whose tag is a name surrogate. It refuses each case
of `_move`, a read-only source and an encrypted one, checks each entry before and after its open,
copies into an exclusively created file with `O_BINARY`, and holds the source open through the
check of its step 9. An unlink or a removal that fails with `PermissionError` is tried 10 times.
The archive is a new file: it takes the access rules of the destination directory, and no
alternate stream of the source. These windows of a race remain, as TASK 131 D7 states:

- RW1: a link swapped in at `docs` or at the destination directory after its check, and swapped
  back between the checks of step 7; the copy, or the move of a file at the link's target, is
  then made there;
- RW2: the same link swapped back before step 7, or still in place at it; an empty file stays at
  the link's target, and the error says that it is kept; a directory that step 4 made through the
  link stays there too;
- RW3: a link swapped in at `docs` between step 9 and step 10 or a try; step 10 removes a file at
  the link's target;
- RW4: an entry swapped in at the source between step 9 and step 10 or a try; step 10 removes it;
- RW5: the source removed between its check and a try of the archive's removal;
- RW6: a link swapped in at the destination's name between steps 5 and 6;
- RW7: a directory swapped for a link between an open and the check of its real path;
- RW8: a junction swapped in between the walk filter and the walk's descent;
- RW9: a volume that reports `st_ino` 0, where an identity compares the device only;
- RW10: a replacement that receives the source's freed inode number;
- RW11: a link swapped in at a directory, or another file put at the archive's name, between the
  undo's checks and its removal of an entry;
- RW12: a write to the source that keeps its size, which Windows may not date until the writer's
  handle closes, or which falls within the 2-second steps of FAT; the archive misses it.

Exit codes: 0 moved; 1 refused, nothing changed on disk, except when the error says the archive
was kept; 2 usage error. Any `OSError`, such as an overlong name, is a refusal. One JSON object
goes to stdout on success, to stderr otherwise.
"""
import os
import sys

# Run as a script, its own directory leaves the import path before any other import, so a module
# planted beside the script is never imported under the allow rule. A test that loads the module
# keeps its own path (TASK 112 R1.8). An entry is that directory when its real path, or its device
# and inode, match the directory of the path as called or of the real path: a case-insensitive
# volume reaches the directory in other letter case (ARC-13, the rule of TASK 127 R6.1).
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

import errno  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import stat  # noqa: E402
import time  # noqa: E402

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
#: The bit of a reparse tag that marks a name surrogate: a symbolic link or a junction (TASK 128
#: R2.2).
NAME_SURROGATE = 0x20000000
#: An unlink or a removal that fails with `PermissionError` is tried this often, this many seconds
#: apart (TASK 128 D9, TASK 131 R1.6).
TRIES = 10
PAUSE = 0.1


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


def _is_link(st):
    """True for a symbolic link, or a reparse point whose tag is a name surrogate (TASK 131 R1.3).

    Both attributes of Windows are read with `getattr`: only Windows sets them. A junction is a
    link; a cloud placeholder is not.
    """
    return stat.S_ISLNK(st.st_mode) or bool(
        getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        and getattr(st, "st_reparse_tag", 0) & NAME_SURROGATE)


def _flags(*names):
    """The union of each `os.O_*` flag of `names` that this platform has."""
    value = 0
    for name in names:
        value |= getattr(os, name, 0)
    return value


def _tried(call, path, check=None):
    """`call(path)`, tried again on `PermissionError` (TASK 131 R1.6).

    At most `TRIES` tries, `PAUSE` seconds apart. `check`, when given, runs before each try after
    the first, and a check that raises ends the tries with its error.
    """
    for attempt in range(TRIES):
        if attempt and check is not None:
            check()
        try:
            return call(path)
        except PermissionError:
            if attempt == TRIES - 1:
                raise
            time.sleep(PAUSE)


def _dir_lstat(path, label):
    """The `lstat` of directory `path`; `label` names it in a refusal. A missing one raises
    `FileNotFoundError`."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise Refused(f"cannot open {label!r}: {exc.strerror}") from exc
    return st


def _same_dir(path, ref):
    """True while `path` is a directory, no link, of the identity of `ref`."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISDIR(st.st_mode) and not _is_link(st) and _same_file(st, ref)


def _holds(path, ref):
    """True while `path` is the file of `ref`, no link."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return not _is_link(st) and _same_file(st, ref)


class _Kept(Refused):
    """A refusal after which the archive stays: it may be the content's last name."""


def _source_check(source, ref, target):
    """Step 9: the source still holds the moved file, one hard link, with the size and the time of
    the last write of step 2 (TASK 131 R1.4, R1.5).

    Raises `_Kept` when the source is gone, holds another file or cannot be checked, and
    `Refused` when it holds the moved file with a second hard link or a write since step 2.
    """
    try:
        st = os.lstat(source)
    except FileNotFoundError as exc:
        raise _Kept(f"{source} is gone after the copy, so {target} is kept") from exc
    except OSError as exc:
        raise _Kept(f"cannot confirm what {source} holds ({exc.strerror}); both it and "
                    f"{target} are kept") from exc
    if _is_link(st) or not _same_file(st, ref):
        raise _Kept(f"{source} no longer holds the moved file, so {target} is kept")
    if st.st_nlink != 1 or (st.st_size, st.st_mtime_ns) != (ref.st_size, ref.st_mtime_ns):
        raise Refused("the source changed during the move")


class _UnlinkFailed(Refused):
    """Step 10 failed while the source still holds the moved file; `strerror` is its error."""

    def __init__(self, source, strerror):
        super().__init__(f"cannot remove {source}: {strerror}")
        self.strerror = strerror


def _unlink_source(source, ref, target):
    """Step 10, with the tries of R1.6; the message of `_undo_after_failed_unlink` on a failure."""
    try:
        _tried(os.unlink, source, lambda: _source_check(source, ref, target))
    except Refused:
        raise
    except OSError as exc:
        try:
            st = os.lstat(source)
        except FileNotFoundError:
            raise _Kept(f"cannot remove {source} ({exc.strerror}); it is gone, so {target} is "
                        "kept") from exc
        except OSError as check:
            raise _Kept(f"cannot remove {source} ({exc.strerror}) or confirm what it holds "
                        f"({check.strerror}); both it and {target} are kept") from exc
        if _is_link(st) or not _same_file(st, ref):
            raise _Kept(f"cannot remove {source} ({exc.strerror}); it no longer holds the moved "
                        f"file, so {target} is kept") from exc
        raise _UnlinkFailed(source, exc.strerror) from exc


class _DirsChanged(Exception):
    """A directory of the undo is no longer the one that steps 1 and 4 checked."""


class _NotOurs(Exception):
    """The archive's name no longer holds the file that step 6 made."""


def _remove_ours(target, made, dirs, check=None):
    """Remove this run's archive, with the tries of R1.6, through unchanged directories (R1.5).

    Before the first try and before each later one, the archive is checked and raises `_NotOurs`
    unless it holds the file of `made`; then `dirs()` raises `_DirsChanged` unless `docs` and the
    destination directory keep their identities; then `check` runs.
    """
    if made is None:
        return

    def checks():
        if not _holds(target, made):
            raise _NotOurs()
        dirs()
        if check is not None:
            check()
    checks()
    _tried(os.unlink, target, checks)


def _undo(exc, message, target, made, dirs, source, ref, checked):
    """The message of a refusal after the undo of R1.5 removed what it may remove."""
    def source_holds():
        if not _holds(source, ref):
            raise _Kept("")
    try:
        _remove_ours(target, made, dirs, source_holds if checked else None)
    except _NotOurs:
        return f"{message}; {target} no longer holds the file this run made, so that file is kept"
    except _DirsChanged:
        return f"{message}; the destination directory changed, so {target} is kept"
    except _Kept:
        return f"{message}; {source} changed before {target} was removed, so {target} is kept"
    except OSError as cleanup:
        if isinstance(exc, _UnlinkFailed):
            return (f"cannot remove {source} ({exc.strerror}), and {target} remains "
                    f"({cleanup.strerror})")
        return f"{message}, and {target} remains ({cleanup.strerror})"
    return message


def _move_by_path(src, subdir, dst):
    """Move `docs/<src>` to `docs/<subdir>/<dst>` by path, where `dir_fd` is missing (R1.4).

    The steps are those of TASK 131 R1.4, and the undo that of R1.5: an archive made before step 9
    is removed while it is this run's; one checked at step 9 or 10 stays when the source is gone
    or holds another file. A directory this run created is removed again.
    """
    source, directory = f"docs/{src}", f"docs/{subdir}"
    target = f"{directory}/{dst}"
    try:                                                    # step 1
        docs = _dir_lstat("docs", "docs")
    except FileNotFoundError as exc:
        raise Refused("docs does not exist") from exc
    if _is_link(docs) or not stat.S_ISDIR(docs.st_mode):
        raise Refused("'docs' is a symbolic link or not a directory")
    src_fd = dst_fd = made = sub = ref = None
    created, checked = False, False
    try:
        try:                                                # step 2
            ref = os.lstat(source)
        except FileNotFoundError as exc:
            raise Refused(f"{source} does not exist") from exc
        if _is_link(ref) or not stat.S_ISREG(ref.st_mode):
            raise Refused(f"{source} is a symbolic link or not a regular file")
        if ref.st_nlink != 1:
            raise Refused(f"{source} has {ref.st_nlink} hard links")
        if getattr(ref, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_READONLY:
            raise Refused(f"{source} is read-only")
        if getattr(ref, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_ENCRYPTED:
            raise Refused(f"{source} is encrypted")
        try:                                                # step 3
            src_fd = os.open(source, _flags("O_RDONLY", "O_NOFOLLOW", "O_NONBLOCK", "O_BINARY"))
        except OSError as exc:
            raise Refused(f"cannot open {source}: {exc.strerror}") from exc
        held = os.fstat(src_fd)
        if not (stat.S_ISREG(held.st_mode) and _same_file(held, ref) and held.st_nlink == 1):
            raise Refused("the source changed during the move")
        try:                                                # step 4
            sub = _dir_lstat(directory, subdir)
        except FileNotFoundError:
            os.mkdir(directory)
            created = True
            sub = _dir_lstat(directory, subdir)
        if _is_link(sub) or not stat.S_ISDIR(sub.st_mode):
            raise Refused(f"{subdir!r} is a symbolic link or not a directory")
        try:                                                # step 5
            os.lstat(target)
        except FileNotFoundError:
            pass
        else:
            raise Refused("the destination exists")
        flags = _flags("O_WRONLY", "O_CREAT", "O_EXCL", "O_NOFOLLOW", "O_BINARY")
        try:                                                # step 6
            dst_fd = os.open(target, flags, stat.S_IMODE(ref.st_mode))
        except FileExistsError as exc:
            raise Refused("the destination exists") from exc
        except OSError as exc:
            raise Refused(f"cannot create the destination: {exc.strerror}") from exc
        made = os.fstat(dst_fd)
        if not (_same_dir("docs", docs) and _same_dir(directory, sub)       # step 7
                and _holds(target, made)):
            raise Refused("the destination directory changed during the move")
        try:                                                # step 8
            while chunk := os.read(src_fd, CHUNK):
                view = memoryview(chunk)
                while view:
                    view = view[os.write(dst_fd, view):]
            os.fsync(dst_fd)
        except OSError as exc:
            raise Refused(f"cannot copy the source: {exc.strerror}") from exc
        _close(dst_fd)
        dst_fd = None
        checked = True                                      # step 9
        _source_check(source, ref, target)
        _close(src_fd)
        src_fd = None
        _unlink_source(source, ref, target)                 # step 10
    except _Kept:
        raise
    except (Refused, OSError) as exc:
        _close(dst_fd)
        dst_fd = None
        if isinstance(exc, Refused):
            message = str(exc)
        else:
            message = f"{exc.strerror or exc}: {exc.filename or ''}".rstrip(": ")

        def dirs():
            if not (_same_dir("docs", docs) and (sub is None or _same_dir(directory, sub))):
                raise _DirsChanged()
        message = _undo(exc, message, target, made, dirs, source, ref, checked)
        if created:
            try:
                dirs()
                _tried(os.rmdir, directory, dirs)
            except (_DirsChanged, OSError):
                pass
        raise Refused(message) from exc
    finally:
        _close(src_fd)
        _close(dst_fd)
    return {"method": "copy", "created_directory": created}


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
    source, destination = argv
    try:
        parsed = _parse(source, destination)
        result = _move(*parsed) if _supported() else _move_by_path(*parsed)
    except Refused as exc:
        return _fail(1, str(exc))
    print(json.dumps({"ok": True, "source": source, "destination": destination, **result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
