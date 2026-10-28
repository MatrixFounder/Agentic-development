# TASK 131 — The archive chain runs on Windows, and the file mode of `rebase_links.py` ends without a traceback

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 131 |
| Slug | archive-chain-windows |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | the defect report of 2026-10-26 (TASK 127 §1); TASK 127 D1; the operator's answers of 2026-10-27 (D1 to D3, D8) |
| Base revision | `6f3d65c8d085c48ae36e2e63a7f47fc9ac2b8dce` |
| Closes | none; the WI-39 record gains a progress note (R8.3) |
| Archive name | `task-131-archive-chain-windows.md` |
| Revision | 10 |

**Revision 10** records round 3 of stage 2, which passed, and the LOW findings that stay (D29).
**Revision 9** applies the fix of round 2 of stage 2: R1.4 step 9, R1.5, R1.6, R12.1, RW2, RW11 and
RW12, the outcomes on Windows of TC-W30 and TC-W31, and TC-W43 to TC-W46 (D28).
**Revision 8** applies the fix of round 1 of stage 2 and the operator's answers on its two
findings that widen the scope: R11, R12 and TC-W29 to TC-W42 (D24 to D27).
**Revision 7** names in R6.6 a test of TASK 116 that R3.3 changes, which PLAN C3 met.
**Revision 6** applies m3 and N2 of round 3 of the Mode B audit to TC-W6 and TC-W28 (D23).
**Revision 5** adds what the read of PLAN B1 measured: R10, the skips and edits of R6.5 and
R6.6, and TC-W28 (D21, D22).
**Revision 4** applies m1, m2, N1 and N2 of Mode A round 3, which passed, with no further round
(D20).
**Revision 3** applies M1, m1 to m7 and N1 to N3 of Mode A round 2 (D19).
**Revision 2** applies M1 to M5, m1 to m10 and N2, N4 to N7 of Mode A round 1 (D18). It records
the operator's answer on D8.

**Request.** A team runs the framework on Windows 10 with Python 3.13, Git Bash and PowerShell.
The ANSI code page there is cp1251. Their report of 2026-10-26 names the archive chain among the
scripts that fail on Windows. TASK 127 D1 gave the chain to the second task of the Windows series.
On 2026-10-27 the operator put it after TASK 130, and chose its scope (D1 to D3, D8).

A coordinate into a file that this task edits carries the pin `@6f3d65c`, the base revision.

<!-- contract:problem -->

## 1. Problem

`skill-archive-task` runs four scripts at each new task:

- `.agent/tools/task_id_tool.py` at Step 3;
- `.agent/tools/archive_move.py` at Steps 5 and 7.6;
- the file mode of `.agent/tools/rebase_links.py` at Steps 5.5 and 7.6.5;
- its inbound mode, in `.agent/tools/slot_links.py`, at Step 8.

The runs of §8 give these defects:

1. **The move exits 2.** `.agent/tools/archive_move.py:301@6f3d65c` `if not _supported():`. The
   check needs `os.supports_dir_fd`, `os.O_NOFOLLOW` and `os.O_DIRECTORY`; Windows has none of
   them (§8, run 1).
2. **The file mode exits 2.** `.agent/tools/rebase_links.py:573@6f3d65c`
   `raise _Unsafe("this platform has no O_NOFOLLOW")` (§8, run 2).
3. **The inbound mode exits 2.** `.agent/tools/slot_links.py:494@6f3d65c`
   `raise InboundError("this platform has no O_NOFOLLOW")` (§8, run 3).
4. **No open sets `O_BINARY`.**
   - `.agent/tools/rebase_links.py:575@6f3d65c` `fd = os.open(path, flags | nofollow | getattr(os, "O_NONBLOCK", 0))`
   - `.agent/tools/slot_links.py:184@6f3d65c` `os.O_RDONLY | os.O_NOFOLLOW`
   - `.agent/tools/slot_links.py:360@6f3d65c` `os.O_RDWR | os.O_NOFOLLOW`
   - `.agent/tools/task_id_tool.py:104@6f3d65c` `fd = os.open(path, flags)`

   On Windows such a descriptor is in text mode. The C runtime reads CR LF as LF and stops at the
   byte `0x1A`, and it writes LF as CR LF. `tempfile` adds `O_BINARY` for this reason (§8).
5. **A junction is not `S_ISLNK`.** The base refuses links through `O_NOFOLLOW` and
   `O_DIRECTORY`. On Windows `os.lstat` gives `S_ISLNK` for a symbolic link only; a junction is a
   directory with a reparse tag (TASK 128 R2.2). The code of `os.walk` in Python 3.14.8 enters a
   junction (§8).
6. **The report fails after the write.** `.agent/tools/rebase_links.py:826@6f3d65c`
   `print(f"[{r['action']}] {entry['file']}:{r['line']}  "` writes each authored target with
   `print`. A stream whose encoding lacks a character of it ends the run in a traceback, exit 1,
   after the file was rewritten (§8, run 4). Under Claude Code on Windows the stream is a pipe in
   the ANSI code page: cp1251 for the reporting team, cp1252 on the CI runner.
7. **An operand that is not UTF-8 ends in a traceback.** `.agent/tools/rebase_links.py:743@6f3d65c`
   `text = _read_descriptor(fd).decode("utf-8")` lies outside the handled errors. A cp1251 file
   exits 1 (§8, run 5). Step 5.5 reads exit 1 as a link that regressed.
8. **The bytecode prefix is relative on Windows.** `.agent/tools/rebase_links.py:98@6f3d65c`
   `sys.pycache_prefix = os.path.join(os.devnull, "rebase-links-pycache")`. On Windows
   `os.devnull` is `nul`, a relative path (§8, run 6). A sibling's `.pyc` is then looked up under
   `nul\rebase-links-pycache\` in the working directory. A `\\?\` path can create a directory
   named `nul` there.
9. **Two drives end in a traceback.** `os.path.commonpath` raises `ValueError` for paths on two
   drives (§8, run 6). These seven checks call it:
   - `.agent/tools/rebase_links.py:264@6f3d65c` `if os.path.commonpath([root, denote_old]) != root:`
   - `.agent/tools/rebase_links.py:498@6f3d65c` `if os.path.commonpath([absolute, cwd]) != cwd or absolute == cwd:`
   - `.agent/tools/rebase_links.py:508@6f3d65c` `if os.path.commonpath([directory, real_cwd]) != real_cwd:`
   - `.agent/tools/rebase_links.py:546@6f3d65c` `if os.path.commonpath([os.path.dirname(where), real_cwd]) != real_cwd:`
   - `.agent/tools/slot_links.py:355@6f3d65c` `if os.path.commonpath([parent, real_root]) != real_root:`
   - `.agent/tools/slot_links.py:379@6f3d65c` `if os.path.commonpath([os.path.dirname(where), real_root]) != real_root:`
   - `.agent/tools/slot_links.py:459@6f3d65c` `if os.path.commonpath([real_root, real_top]) != real_top:`

   `.agent/tools/rebase_links.py:686@6f3d65c` `if os.path.isabs(value)` passes a value with a
   drive and no root, such as `D:x`. From Python 3.13 it also passes a root with no drive, such as
   `/x`.
10. **A slot link exits 2 on Windows.** `.agent/tools/rebase_links.py:286@6f3d65c`
    `os.path.relpath(identity, root),` writes the `denotes_old` of a `SLOT_RESOLVED` record with
    `\` on Windows. `.agent/tools/rebase_links.py:456@6f3d65c`
    `return [part for part in path.split("/") if part not in ("", ".", "..")]` splits it on `/`
    only. The check of TASK 117 R2, `_adds_parts`, then fails, and Steps 5.5 and 7.6.5 exit 2 on
    every slot link (§8, run 7).
11. **The tests run on Ubuntu only.** The chain's tests use FIFOs, permission bits, symbolic links
    and the descriptors of `archive_move._move`. Two tests assert the exit 2 of item 2 or 3:
    `test_g22_a_platform_with_no_o_nofollow` of `tests/test_script_guards.py` and
    `test_platform_without_o_nofollow_refuses` of `.agent/tools/test_slot_links.py`.
12. **Text in the locale encoding.** The read of PLAN B1 found reads and writes that pass no
    `encoding` on text that is not ASCII. On the runner the locale encoding is cp1252:
    - `.agent/tools/archive_protocol.py:400@6f3d65c` `meta = parse_task_meta(task_file.read_text())`,
      and the calls of lines 440, 487 and 491;
    - six tests of `.agent/tools/test_archive_protocol.py` write a TASK with Cyrillic labels;
    - `_write` of `TestSubTaskByH1` in `.agent/tools/test_task_id_tool.py` writes H1 lines with
      dashes;
    - `test_tc7_link_text` of `.agent/tools/test_slot_links.py` reads a sub-task with `§`.

    The same read found tests whose premise fails on Windows (D22):
    - a `..` that Windows resolves before the link;
    - a file replaced while a descriptor holds it;
    - a name that NTFS refuses, and permission bits that deny nothing.
13. **A CR LF document is masked to its end.** `.agent/tools/rebase_links.py:109@6f3d65c`
    `_FENCE = re.compile(` closes a fence on a line that ends in LF only, and `_CODE_SPAN` ends a
    span at a blank line of LF only. Git for Windows checks files out with CR LF by default. Steps
    5.5, 7.6.5 and 8 then skip each link after the first fence, with exit 0 (stage 2, round 1).
14. **A UNC path reaches the file system.** `.agent/tools/rebase_links.py:681@6f3d65c`
    `if os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):` resolves any
    `--repo-root`, and `task_id_tool.py` lists any `--tasks-dir`. On Windows a UNC path there
    sends the user's NTLM credentials to its host (stage 2, round 1).

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| R1 | `archive_move.py` without `dir_fd` | yes | a move by path; links and junctions; a read-only source; a copy; the undo; tries | A1 |
| R2 | An open with no link followed, without `O_NOFOLLOW` | yes | a check before and after the open; `O_BINARY`; both modes; the walk; `task_id_tool.py` | A2 |
| R3 | The text of the file mode | yes | any stream encoding; ASCII JSON; an operand that is not UTF-8 | A3 |
| R4 | The bytecode prefix where `os.devnull` is relative | yes | a prefix under the script's real path | A4 |
| R5 | Paths of another drive, root or separator | yes | `ValueError` as outside; `--from` and `--to`; `denotes_old` with `/` | A5 |
| R6 | Tests | yes | TC-W tests; POSIX tests of the Windows checks; skips by capability; the read; mutations | A6, A7 |
| R7 | CI on Windows | yes | a step in each Windows job; TC-C8 and TC-C9; the first run after the push | A8, A11, A12 |
| R8 | Documents and records | yes | `docs/ARCHITECTURE.md`; v3.50.0; WI-39; the stale texts | A9 |
| R9 | Staging and checks | yes | copies under new names; the check of what runs; the worktree; the settings | A10 |
| R10 | `archive_protocol.py` reads and writes UTF-8 | yes | four calls; TC-W28 | A13 |
| R11 | The masks of `rebase_links.py` read CR LF | yes | a fence closed by CR LF; a blank line of CR LF | A14 |
| R12 | No UNC path reaches the file system | yes | `--repo-root`; `--tasks-dir`; a refusal before any call | A14 |

## 3. Requirements

### R1 — `archive_move.py` on a platform without `dir_fd`

- **R1.1** Where `_supported()` returns true, `main` runs `_move`. Its calls, flags and messages
  stay as at the base.
- **R1.2** Elsewhere, `main` runs `_move_by_path`, a new function. The exit 2 for the platform is
  removed. Exit 2 then means a usage error only.
- **R1.3** A link is an entry for which `os.lstat` gives `stat.S_ISLNK`. It is also an entry whose
  `st_file_attributes` holds `stat.FILE_ATTRIBUTE_REPARSE_POINT` and whose
  `st_reparse_tag & 0x20000000` is not 0. The check reads both attributes with `getattr`. This is
  the rule of TASK 128 R2.2: a symbolic link and a junction are links, a cloud placeholder is not.
- **R1.4** `_move_by_path` runs these steps. An identity is the pair `(st_dev, st_ino)`. Each
  refusal exits 1 and runs the undo of R1.5:
  1. `docs`: `os.lstat`. Missing → `docs does not exist`. A link or not a directory →
     `'docs' is a symbolic link or not a directory`. Its identity is kept.
  2. The source: `os.lstat`. Missing, a link, not a regular file or a second hard link → the
     message of `_check_source` for that case. `stat.FILE_ATTRIBUTE_READONLY` in
     `st_file_attributes` → `docs/TASK.md is read-only`, or `docs/PLAN.md is read-only`.
     `stat.FILE_ATTRIBUTE_ENCRYPTED` → `docs/TASK.md is encrypted`, or `docs/PLAN.md is encrypted`.
  3. The source opens with `os.O_RDONLY`, and with each of `os.O_NOFOLLOW`, `os.O_NONBLOCK` and
     `os.O_BINARY` that exists. `os.fstat` gives a regular file with one hard link and the
     identity of step 2, or the run refuses with `the source changed during the move`. The
     descriptor stays open until step 9.
  4. The destination directory: `os.lstat`. Missing → `os.mkdir`, then `os.lstat` again. A link or
     not a directory → the message of step 1 with its name. Its identity is kept.
  5. The destination: an entry of any kind at its name → `the destination exists`.
  6. The destination opens with `os.O_WRONLY | os.O_CREAT | os.O_EXCL`, with each of
     `os.O_NOFOLLOW` and `os.O_BINARY` that exists, and with the permission bits of the source.
  7. `docs` and the destination directory keep their identities and are no links. The
     destination's `os.lstat` gives the identity of its descriptor. Otherwise →
     `the destination directory changed during the move`.
  8. The script copies the source into the destination, syncs it with `os.fsync`, and closes the
     destination's descriptor.
  9. With the source's descriptor open, the source's `os.lstat` gives the identity, the size and
     the `st_mtime_ns` of step 2, and one hard link. Otherwise the run refuses with the message of
     R1.5. The source's descriptor then closes.
  10. `os.unlink` removes the source.
- **R1.5** The undo:
  - a refusal at step 7 or step 8 removes the destination when its `os.lstat` gives the identity
    of its descriptor. Otherwise the file that step 6 made stays, and the message ends
    `docs/<dst> no longer holds the file this run made, so that file is kept`;
  - a refusal at step 9, or a failure of step 10, removes the archive only while the source's
    `os.lstat` gives the identity of step 2. When the source is gone or holds another file, the
    archive is the content's last name, and it stays;
  - a failure of step 10 gives the messages of `_undo_after_failed_unlink`. A refusal at step 9
    gives one of these, with `<src>` the source and `<dst>` the archive:
    - the source is gone: `docs/<src> is gone after the copy, so docs/<dst> is kept`;
    - it holds another file: `docs/<src> no longer holds the moved file, so docs/<dst> is kept`;
    - its `os.lstat` fails: `cannot confirm what docs/<src> holds (<strerror>); both it and
      docs/<dst> are kept`;
    - it holds the moved file with a second hard link, or a size or `st_mtime_ns` other than that
      of step 2: `the source changed during the move`, and the archive is removed;
  - a directory that step 4 created is removed again;
  - before each removal of the archive or of that directory, `docs` and the destination directory
    keep their identities of steps 1 and 4 and are no links. Otherwise the entry stays. For the
    archive, the message ends `the destination directory changed, so docs/<dst> is kept`;
  - when the archive's removal fails after a failed step 10, the message is that of the base:
    `cannot remove docs/<src> (<strerror>), and docs/<dst> remains (<strerror>)`.
- **R1.6** An `os.unlink` or `os.rmdir` of R1.4 or R1.5 that fails with `PermissionError` is tried
  again: at most 10 tries, 0.1 seconds apart (TASK 128 D9). Before each try of step 10, the check
  of step 9 runs again; a failed check ends the tries with the refusal of step 9. Before each try
  of the archive's removal in R1.5, each check of R1.5 runs again: the archive's identity, the two
  directories and, after step 9, the source. A failed check ends the tries, and the archive stays
  with the message of that check. For the source, the message is `<the refusal>; docs/<src>
  changed before docs/<dst> was removed, so docs/<dst> is kept`. Before each try of the removal
  of the created directory, the check of the two directories runs again.
- **R1.7** Any other `OSError` of R1.4 is a refusal with exit 1 and the undo of R1.5. Its message
  is the base's message for that call: `cannot open docs/<name>`, `cannot create the destination`,
  `cannot copy the source`, or else `<strerror>: <filename>` as the handler of `_move` builds it.
- **R1.8** A move prints `"method": "copy"` and `"created_directory"`, beside the fields of the
  base.
- **R1.9** The module docstring names both branches, the exit codes of R1.2 and the labels of the
  windows of D7. It states that the archive is a new file: it takes the access rules of the
  destination directory, and no alternate stream of the source.

### R2 — an open with no link followed, without `O_NOFOLLOW`

- **R2.1** Where `os.O_NOFOLLOW` exists, each open of both modes passes the flags of the base.
- **R2.2** Elsewhere, an open with no link followed runs three steps:
  1. `os.lstat` of the path. A link by R1.3 → refusal `is a link`. Any other entry that is not a
     regular file → refusal `is not a regular file`, before any open.
  2. `os.open` with the flags of the base, `os.O_NONBLOCK` among them, and `os.O_BINARY` where they
     exist.
  3. `os.fstat` gives the identity of step 1. Otherwise the descriptor closes, and the open
     refuses with `changed during the run`.
- **R2.3** The checks after the open stay: a regular file, one hard link, the file at its real
  path, and its directory inside the root. Where `_descriptor_path` gives no path, the real path
  serves, as at the base. Where `os.name` is not `posix`, `_descriptor_path` gives no path: it
  imports no `fcntl` and reads no `/proc` (D27).
- **R2.4** The refusal `this platform has no O_NOFOLLOW` is removed from both modes. So are the
  words `or the platform` from the exit codes of `slot_links.py`:
  - `.agent/tools/slot_links.py:21@6f3d65c` `its first byte, or an unexpected error; 2 an operand, git, `;
  - `.agent/tools/slot_links.py:66@6f3d65c` `"""An operand, git, `;
  - `.agent/tools/slot_links.py:491@6f3d65c` `InboundError: an operand, git, `.
- **R2.5** The walk of the inbound mode enters no directory that is a link by R1.3. A directory
  whose `os.lstat` fails is not entered either, and is recorded as `UNREADABLE`.
- **R2.6** Each of the three modules holds its own copy of the helpers of R1.3 and R2.2 (D12).
- **R2.7** `_first_h1` of `task_id_tool.py` adds `os.O_BINARY` to its flags where it exists (D17).

### R3 — the text of the file mode

- **R3.1** The file mode writes each line of stdout and stderr in the stream's encoding with the
  error handler `backslashreplace`, as `slot_links._emit` does.
- **R3.2** The `--json` object of the file mode is ASCII: `json.dumps` with `ensure_ascii=True`.
- **R3.3** An operand that is not UTF-8 exits 2 with `{"ok": false, "error": "<operand>: is not
  UTF-8"}` on stderr. The operand is not written (D8).

### R4 — the bytecode prefix where `os.devnull` is relative

- **R4.1** Where `os.devnull` is an absolute path, `sys.pycache_prefix` stays as at the base.
- **R4.2** Elsewhere, `sys.pycache_prefix` is `os.path.join(<the script's real path>, "pycache")`.

  **Why.** The path lies under a regular file ⇒ no directory or `.pyc` can exist at it, on any
  platform.
- **R4.3** The comment of the prefix names both cases:
  `.agent/tools/rebase_links.py:78@6f3d65c` `# - no bytecode is written, and `.

### R5 — paths of another drive, root or separator

- **R5.1** At each of the seven checks of §1 item 9, a `ValueError` of `os.path.commonpath` counts
  as a path outside. The check then gives its refusal, or its record, for a path outside.
- **R5.2** `--from` and `--to` are refused as outside the working directory when
  `os.path.splitdrive` gives a drive, or when the value starts with `/` or `os.sep`.
- **R5.3** `rebase_document_links` writes each repo-relative `denotes_old` of a record with `/` on
  every platform.
- **R5.4** On Windows, the file mode refuses a link target written with `\` that resolves from the
  old directory to a file other than a slot. It exits 2 and writes nothing (D16). A `\` link to a
  slot is rewritten. One that resolves nowhere, only from the new directory, or outside the root
  is `PRE_BROKEN`, `ACCIDENTAL_RESOLVE` or `ESCAPES_ROOT`, and stays as written.
- **R5.5** Where the paths of the platform have drives, the file mode refuses an operand that holds
  `:` after its drive: on NTFS the colon names an alternate stream of the file.

### R6 — tests

- **R6.1** New tests, `TC-W1` onward, cover R1 to R5. Each runs on every platform unless it needs a
  feature of Windows.
- **R6.2** On POSIX a test reaches each branch by removing the capability:
  - `archive_move._supported` patched to return false;
  - `os.O_NOFOLLOW` deleted;
  - `os.devnull` set to `nul`.

  A test that runs a script in a subprocess removes it with a `sitecustomize.py`. The test writes
  that file in a temporary directory (TASK 127 R7.2).
- **R6.3** On POSIX a test reaches each check of Windows with a stand-in:
  - `os.lstat` patched to report a reparse tag, or the read-only attribute, for one path;
  - `os.O_BINARY` set to an unused bit, and `os.open` wrapped by a spy that records and strips it;
  - for R5.2 and R5.3, the module's `os` bound to a namespace that holds `path=ntpath` and
    `sep="\\"`, so the global `os.path` stays.
- **R6.4** Tests on Windows only:
  - a junction at `docs`, at `docs/tasks` and at the directory of an operand;
  - a source held open by another descriptor;
  - a read-only source;
  - an operand, a link target and `--from` on another drive;
  - a link target written with `\`.

  A test makes a junction with `_winapi.CreateJunction`, and runs no `cmd.exe`.
- **R6.5** An existing test that needs a POSIX feature skips where the platform lacks it:
  - a FIFO, by `os.mkfifo`;
  - permission bits;
  - the descriptors of `archive_move._move`, by `_supported()`;
  - a symbolic link, by a probe that creates one;
  - the descriptor path, by `_descriptor_path_known()` as at the base.

  A test whose premise is a behaviour of POSIX skips on Windows, with the reason in its marker:
  - a `..` resolved after the link before it: `test_g15_a_parent_segment_after_a_directory_link`;
  - a file replaced while a descriptor holds it: `test_g21_a_file_replaced_after_the_read` and
    `test_tc27`; Windows refuses the replace;
  - a name that NTFS refuses: the cases of `test_g30` and `test_g31` that hold `:`, `"` or `>`,
    and the case of `test_tc31` with a line break in a file name;
  - permission bits that deny a read: `test_tc37` and `test_tc43`.
- **R6.6** These tests change:
  - `test_g22_a_platform_with_no_o_nofollow` and `test_platform_without_o_nofollow_refuses` assert
    that the run rewrites the file without `O_NOFOLLOW`. TC-W11 and TC-W19 assert the refusal of a
    link swapped in;
  - `test_g16_a_directory_swapped_around_the_open`, `test_g17_a_file_swapped_for_a_link` and the
    swap case of `test_g19_a_directory_swapped_around_the_inbound_open` accept the refusal of R2.2
    where `os.O_NOFOLLOW` is missing;
  - the docstring of `tests/test_script_guards.py` no longer names a refusal of the platform:
    `tests/test_script_guards.py:17@6f3d65c` `and a platform with no `;
  - each test that the read of PLAN B1 names writes or reads its text with `encoding="utf-8"`;
  - `test_tc21` writes its hooks as LF bytes, with the paths in the form of POSIX;
  - `test_g11_a_planted_module_is_not_imported` also plants `fcntl`, which the scripts import on
    POSIX and lack on Windows;
  - `test_f3_a_non_utf8_operand_raises_as_at_the_base` of `.agent/tools/test_rebase_links.py`
    pinned the traceback of the base. It becomes `test_f3_a_non_utf8_operand_is_refused`, which
    asserts the refusal of R3.3;
  - a test that compares `denotes_old` with a path of the platform compares it with `/` (R5.3):
    `.agent/tools/test_rebase_links.py:209@6f3d65c` `assert rec[0].denotes_old == os.path.join("docs", "ARCHITECTURE.md")`.
- **R6.7** Before stage 2, the run reads each test that the Windows jobs run for an assumption of
  POSIX. The read covers:
  - path separators and letter case;
  - line ends, and `core.autocrlf` of a test repository and of the checkout itself;
  - the locale encoding of `read_text`, `write_text` and `subprocess` with `text=True`;
  - links, permission bits and FIFOs;
  - the temporary directory, its drive and its short names;
  - the removal of an open file.

  The audit record lists each test, the assumption it meets, and how the change meets it.
- **R6.8** Each new test fails under a mutation that the PLAN names. The PLAN marks each mutation
  that only a test of R6.4 kills; A11 decides those.

### R7 — CI on Windows

- **R7.1** The jobs `session-state-windows-floor` and `session-state-windows-main` of
  `.github/workflows/framework-gates.yml` gain a step `Run the archive-chain tests`, after the
  step `Run the session-state tests`. It runs `python -m pytest -p no:cacheprovider -q` on:
  - `tests/test_archive_move.py`;
  - the classes `TestRebaseLinksGuard` and `TestInboundGuard` of `tests/test_script_guards.py`;
  - `.agent/tools/test_rebase_links.py`, `.agent/tools/test_slot_links.py`,
    `.agent/tools/test_archive_protocol.py` and `.agent/tools/test_task_id_tool.py`.
- **R7.2** The ids and names of both jobs stay (D9).
- **R7.3** In `tests/test_session_state_contract.py`, TC-C8 selects the step named
  `Run the session-state tests`, and TC-C9 the step of R7.1 (§5):
  `tests/test_session_state_contract.py:151@6f3d65c` `self.assertEqual(len(tests), 1, f"{name}: one pytest step")`.
- **R7.4** The first run of the step follows the operator's push, after this run. The final report
  names the step. The next task reads its result first, with `gh run list` and `gh run view`. A
  failed test is filed as a defect record and named to the operator (D15).

### R8 — documents and records

- **R8.1** The paragraph on archiving of `docs/ARCHITECTURE.md` states the branch of each script
  on a platform without `dir_fd` or `O_NOFOLLOW`:
  `docs/ARCHITECTURE.md:189@6f3d65c` `Archiving runs through`.
- **R8.2** `CHANGELOG.md` and `CHANGELOG.ru.md` hold v3.50.0.
- **R8.3** The WI-39 record gains a progress blockquote after its last one: the prefix of R4. Its
  index line in `docs/BACKLOG.md` stays.
- **R8.4** `skill-archive-task` and `skill-safe-commands` stay as they are (D10).

### R9 — staging and checks

- **R9.1** The change runs the four stages of `framework-upgrade` §3 step 4. Stage 1 writes these
  copies under new names, and the stage-3 patch gives each final file their bytes:
  - `.agent/tools/staged_archive_move.py` → `.agent/tools/archive_move.py`;
  - `.agent/tools/staged_rebase_links.py` → `.agent/tools/rebase_links.py`;
  - `.agent/tools/staged_slot_links.py` → `.agent/tools/slot_links.py`;
  - `.agent/tools/staged_task_id_tool.py` → `.agent/tools/task_id_tool.py`;
  - `tests/staged_archive_move.py` → `tests/test_archive_move.py`;
  - `tests/staged_script_guards.py` → `tests/test_script_guards.py`;
  - `.agent/tools/staged_test_rebase_links.py` → `.agent/tools/test_rebase_links.py`;
  - `.agent/tools/staged_test_slot_links.py` → `.agent/tools/test_slot_links.py`;
  - `.agent/tools/staged_test_task_id_tool.py` → `.agent/tools/test_task_id_tool.py`.

  The patch touches no other path.

  **Why.** Allow rules run `archive_move.py`, `rebase_links.py` and `task_id_tool.py`, and
  `rebase_links.py` loads `slot_links.py`. `tests/run_tests.py`, which an allow rule runs, runs the
  two modules of `tests/`. The three modules of `.agent/tools/` import the scripts by their final
  names ⇒ landed in place, their new tests fail the gates before stage 3.
- **R9.2** The documents, the changelogs, the record, the CI workflow, TC-C8 and TC-C9 land in place
  before stage 3. So do the edits of `.agent/tools/test_archive_protocol.py` and the change of R10.

  **Why.** No rule runs `.agent/tools/archive_protocol.py`. Only test modules load it, and
  `framework-upgrade` §3 step 4 exempts code that runs without a prompt only through them.
- **R9.3** The checks of TASK 128 R8.7 apply, with the commands of this change:
  - the gates: the test steps of `.github/workflows/framework-gates.yml`, run on macOS in a
    worktree that holds the stage-3 patch;
  - the mutations, and a scan of each changed file for bytes outside its encoding;
  - the listing of `.agent/sessions/` before and after each check, which shows the live session
    state unchanged;
  - the check of §3 step 4 for each allowed command that reaches the change, the bare pytest of
    `tests/test_session_state_contract.py` among them. The PLAN lists the commands.
- **R9.4** The run reads `.claude/settings.local.json` and the user's `~/.claude/settings.json` at
  §2.2, at §4.5 and after the gates of stage 3. The audit record names each file of the change
  that a rule of either file runs, and quotes no rule. Two rules of the user run `task_id_tool.py`
  through the links of a sibling checkout (§8); the check of R9.3 runs each of them.
- **R9.5** The change edits no permission rule, hook or settings key. Stage 3 adds no settings
  test.

### R10 — `archive_protocol.py` reads and writes UTF-8

- **R10.1** The four calls of §1 item 12 pass `encoding="utf-8"`. Their line ends stay as at the
  base (D21).

### R11 — the masks of `rebase_links.py` read CR LF

- **R11.1** A fence closes on a line that ends in CR LF, as on one that ends in LF.
- **R11.2** A line that holds only spaces, tabs and a CR before its LF is a blank line, and it ends
  a code span.

  **Why.** Git for Windows checks files out with CR LF by default. At the base a CR LF document
  masks everything after its first fence, so Steps 5.5, 7.6.5 and 8 skip each link there with
  exit 0 (D24).

### R12 — no UNC `--repo-root` or `--tasks-dir` reaches the file system

- **R12.1** Where the paths of the platform have drives, a path that starts with two separators,
  or with `\??\`, is a UNC or device path: `\\host\share`, `\\?\`, `\\.\` and
  `\??\UNC\host\share`. The check reads the text, with each `/` read as `\`. It reads no drive
  of the value from `os.path.splitdrive`, which gives none for `\??\UNC\host\share` (§8). It calls
  `splitdrive` only to learn whether the paths of the platform have drives.
- **R12.2** `rebase_links.py` refuses such a `--repo-root`, and `task_id_tool.py` such a
  `--tasks-dir`, before any call that reaches the file system. The file mode exits 2, and
  `task_id_tool.py` prints a status `error` and exits 1.

  **Why.** On Windows an open of a UNC path sends the user's NTLM credentials to its host, and
  allow rules run both scripts with any argument (D25).

<!-- contract:use-cases -->

## 4. Use cases

### UC-1 — An agent on Windows archives a task

- **Actors.** An agent in Claude Code on Windows 10, with Python 3.13, Git Bash and the code page
  cp1251.
- **Precondition.** `docs/TASK.md` and `docs/PLAN.md` hold the previous task.
1. Step 5 runs `archive_move.py docs/TASK.md docs/tasks/task-<ID>-<slug>.md`. The branch of R1
   copies the file and removes the source. Exit 0.
2. Step 5.5 runs the file mode on the archive. The open of R2 keeps its line ends, and a slot
   link is rewritten (R5.3). Exit 0 or 3.
3. Steps 7.6 and 7.6.5 do the same for the plan.
4. Step 8 runs the inbound mode. Exit 0 or 3.
- **Alternative 1a.** An editor holds `docs/TASK.md` open without `FILE_SHARE_DELETE`. The unlink
  fails 10 times, and the archive is removed. Exit 1 names the source, which keeps its bytes.
- **Alternative 1b.** `docs/tasks` is a junction. Exit 1; nothing is created or removed.
- **Alternative 1c.** `docs/TASK.md` is read-only. Exit 1 with `is read-only`; nothing changes.
- **Alternative 2a.** A link target holds `→`. The report shows it as `\u2192`, and the exit code
  follows the records.
- **Alternative 2b.** A link target written with `\` resolves to a file other than a slot. Exit 2
  names its line, and nothing is written. The agent stops and reports, as Step 5.5 states for
  exit 2.
- **Postcondition.** Each archive holds the bytes of its slot, apart from the links that Steps 5.5
  and 7.6.5 rebase. Neither slot exists. Step 8 changed only the slot links that the task wrote.

### UC-2 — The operator pushes, and CI runs the chain's tests on Windows

- **Actors.** The operator; GitHub Actions.
- **Precondition.** The operator committed this task and pushed it.
1. Each Windows job runs the step of R7.1, on Python 3.11 or 3.14.
2. A test that needs POSIX skips. The tests of R6.4 run.
- **Alternative 2a.** A test fails. The next task files it as a defect record and names it to the
  operator (R7.4).
- **Postcondition.** The result shows whether the branches hold on Windows. The next task reads it.

<!-- contract:acceptance -->

## 5. Acceptance criteria

Tests of `tests/test_archive_move.py`. Each runs `_move_by_path` on POSIX with `_supported`
patched, unless it says otherwise:

- **TC-W1** — the move of `docs/TASK.md`, and of `docs/PLAN.md` with no `docs/plans` → exit 0,
  `"method": "copy"`, the archive holds the source's bytes, and the source is gone.
  `"created_directory"` is true for the plan. Fails when `main` calls `_move` on this branch.
- **TC-W2** — a link at `docs`, at `docs/tasks` or at the source → exit 1, and nothing is created
  or removed. With `os.lstat` patched, the tags `0xA0000003` and `0xA000000C` at `docs` or at
  `docs/tasks` → exit 1; the tag `0x9000001A` → exit 0. On Windows also a junction at `docs` and
  at `docs/tasks` → exit 1.
- **TC-W3** — a file, a directory or a link at the destination → exit 1, and nothing changes.
- **TC-W4** — a source with a second hard link → exit 1. A source with the read-only attribute, by
  `os.lstat` patched, and on Windows by `os.chmod` → exit 1 with `is read-only`. Nothing changes.
- **TC-W5** — `docs/tasks` swapped for a link to a directory outside, between step 4 and step 6 →
  exit 1 with `the destination directory changed during the move`. The undo removes nothing
  through the link: the empty file there stays, and the message says that the archive is kept
  (R1.5, RW2). The source keeps its bytes.
- **TC-W6** — each replacement of TC-W6, TC-W7 and TC-W21 is a new file that `os.replace` moves
  over the source, so it never takes the source's inode number. The source replaced after the copy
  → exit 1 with `no longer holds the moved file`,
  and the archive and the replacement are kept. The source removed after the copy → exit 1 with
  `is gone after the copy`, and the archive is kept. A second hard link made to the source after
  the copy → exit 1 with `the source changed during the move`, and the archive is removed. On
  Windows, a swap that the open descriptor of the source refuses with `PermissionError` leaves
  the move to complete with exit 0 (D7); the test asserts that outcome for that case.
- **TC-W7** — an unlink of the source that fails with `PermissionError` 10 times → exit 1, the
  archive is removed, and the source keeps its bytes. Failing 9 times → exit 0. The source
  replaced between two tries → exit 1, and the archive and the replacement are kept. A removal of
  the archive that fails once, with the source removed before the next try → the archive is
  kept.
- **TC-W8** — on Windows only, the source held open by a second `open()` → exit 1 after the tries,
  the archive is removed, and the source keeps its bytes.
- **TC-W9** — a source with CR LF line ends and a byte `0x1A` → the archive holds the same bytes.
- **TC-W10** — where `_supported()` returns true, `main` never calls `_move_by_path`. The tests of
  the base pass unchanged on POSIX.
- **TC-W21** — another regular file swapped in at the source between step 2 and step 3 → exit 1
  with `the source changed during the move`, and nothing is created. With `os.O_NOFOLLOW` also
  deleted, a link swapped in there → the same refusal.
- **TC-W22** — an archive name past the file system's limit → exit 1, and nothing is created. A
  refusal after `docs/plans` was created → the directory is removed, also when its first
  `os.rmdir` fails with `PermissionError`.
- **TC-W23** — the module docstring names `_move_by_path`, exit 2 as a usage error only, and the
  labels `RW1` to `RW12` of D7, and the access rules of a new file.

Tests of the open and of the text, in `tests/test_script_guards.py`,
`.agent/tools/test_rebase_links.py` and `.agent/tools/test_task_id_tool.py`:

- **TC-W11** — without `os.O_NOFOLLOW`, the file mode rewrites a moved document. A link swapped in
  between the `os.lstat` and the open → exit 2 with `changed during the run`, and no write.
- **TC-W12** — on Windows only, a junction at the operand's directory that resolves outside → exit
  2, and no write.
- **TC-W13** — a document with CR LF line ends and a byte `0x1A` → both modes keep every byte but
  the rewritten links.
- **TC-W14** — a link target with `→`, and stdout and stderr in ASCII → each line holds `\u2192`,
  and the exit code follows the records. The `--json` output is ASCII, and `json.loads` reads the
  target back.
- **TC-W15** — an operand in cp1251 → exit 2 with `is not UTF-8`, and the file keeps its bytes.
- **TC-W16** — the inbound mode with `os.devnull` set to `nul`, in walk mode on POSIX →
  `sys.pycache_prefix` lies under the script's real path. A `.pyc` planted under
  `nul/rebase-links-pycache/` in the working directory is not read. On Windows the test makes `nul`
  through a `\\?\` path.
- **TC-W17** — `os.path.commonpath` made to raise `ValueError` at each of the seven checks → the
  refusal or record of a path outside. On Windows also: an operand on another drive → exit 2; a
  link target `\\server\share\x.md` → `ESCAPES_ROOT`.
- **TC-W18** — `--from` or `--to` with a root, `/x` → exit 2. The check of R5.2 with `ntpath` →
  `\x` and `D:x` are outside. On Windows also: `\x` and `D:x` → exit 2.
- **TC-W24** — `os.O_BINARY` set to an unused bit → each open of R1.4, of R2.2 and of `_first_h1`
  passes it. The opens of R2.2 run with `os.O_NOFOLLOW` deleted. Fails when any one of them drops
  it.
- **TC-W25** — `rebase_document_links` with `ntpath` and the root `C:\repo`, and a slot map →
  `denotes_old` holds `/`, and `_adds_parts` of the record is false. On Windows the kept cases of
  TC-G31, the commands of Steps 5.5 and 7.6.5, rewrite a slot link with exit 0.
- **TC-W26** — each of the three modules defines the helpers of R1.3 and R2.2, and none reads them
  from a sibling.
- **TC-W27** — on Windows only, a link target `..\x.md` → exit 2 with its line, and no write.

Tests of the inbound mode, in `.agent/tools/test_slot_links.py`:

- **TC-W19** — without `os.O_NOFOLLOW`, the inbound mode rewrites a sub-task's slot link. A file
  swapped for a link after its `os.lstat` → `REFUSED`, and no write.
- **TC-W20** — the walk mode enters no directory link. With `os.lstat` patched, a directory with
  the tag `0xA0000003` is not entered. On Windows also a junction is not entered.

Tests of the fix of round 1 of stage 2 (TASK D26). The tests of `_move_by_path` run as those of
TC-W1:

- **TC-W29** — a second hard link made between step 2 and step 3 → exit 1 with
  `the source changed during the move`, and no open of the destination.
- **TC-W30** — `docs` moved out and linked back between step 4 and step 6 → exit 1 with
  `the destination directory changed during the move`. The undo removes nothing through the
  changed directory, and the message says that the archive is kept (R1.5, RW2).
- **TC-W31** — another file put at the destination's name after step 6 → exit 1 with
  `the destination directory changed during the move`. That file and the source keep their bytes.
  The message says that the file of step 6 is kept.

  On Windows the rename of TC-W30 and of TC-W31 may fail with `PermissionError`: a descriptor of
  the run holds a file in the renamed directory, or the renamed file. The move then completes with
  exit 0, and the test asserts that outcome for that case (D28).
- **TC-W32** — a failed copy, and a removal of the archive that fails once → exit 1, and the archive
  is removed.
- **TC-W33** — a failed step 10 with the source gone, holding another file, or not readable → the
  messages of `_undo_after_failed_unlink`, and the archive stays. A removal of the archive that
  fails too → `cannot remove docs/TASK.md (<strerror>), and <archive> remains (<strerror>)`.
- **TC-W34** — `docs/tasks` swapped for a link between the undo's check of the archive and its
  removal → the file at the link's target stays, and the message ends `so <archive> is kept`.
- **TC-W35** — a source with the encrypted attribute, by `os.lstat` patched → exit 1 with
  `docs/TASK.md is encrypted`.
- **TC-W36** — a write to the source after the copy → exit 1 with
  `the source changed during the move`; the archive is removed, and the source keeps the write.
- **TC-W37** — without `os.O_NOFOLLOW`, a FIFO at the operand of either mode → a refusal with
  `is not a regular file`, and no open blocks. Skipped where there is no FIFO.
- **TC-W38** — `_descriptor_path` of both modules with `os.name` patched to `nt` → no path, and no
  import of `fcntl`.
- **TC-W39** — the check of R5.5 with `ntpath` → `docs/a.md:b.md` is refused, and
  `C:\repo\docs\a.md` is not. With `posixpath`, `docs/a.md:b.md` is not refused.
- **TC-W40** — the walk with `os.lstat` failing for one directory → an `UNREADABLE` record, and no
  record of the files in it.
- **TC-W41** — a CR LF document with a link before a fence and a link after it, and a code span
  over a CR LF blank line. Both modes rewrite each link outside the fence and the span.
- **TC-W42** — `--repo-root` and `--tasks-dir` of `\\host\share`, `//host/share`, `\\?\C:\x`,
  `\\.\pipe\x`, `\??\UNC\host\share`, `/??/UNC/host/share`, `\\host\\share`, `\\\host\share` and
  `\\host`, with `ntpath`, are refused. With `posixpath` none is refused. No call of
  `os.path.realpath`, `os.stat` or `os.listdir` runs. On Windows the command line refuses them
  too.

Tests of the fix of round 2 of stage 2 (TASK D28), in `tests/test_archive_move.py`:

- **TC-W43** — a write to the source between two tries of step 10 → exit 1 with
  `the source changed during the move`; the archive is removed, and the source keeps the write.
- **TC-W44** — another file put at the archive's name between two tries of its removal in the
  undo → that file stays, and the message ends `so that file is kept`.
- **TC-W45** — `docs/tasks` renamed after a failed copy, before the undo checks the archive → the
  archive stays in the renamed directory, and the message ends
  `docs/tasks/<dst> no longer holds the file this run made, so that file is kept`.
- **TC-W46** — a directory `docs/plans` that the run created, replaced by another empty directory
  before the undo, or between two tries of its removal → that directory stays.

A test of `.agent/tools/test_archive_protocol.py`:

- **TC-W28** — `archive_task` in a temporary root, in a subprocess under `LC_ALL=C`,
  `PYTHONUTF8=0` and `PYTHONCOERCECLOCALE=0`. Its TASK has a Cyrillic label and no ID → the
  archive holds the written-back ID, and the text keeps its letters.

Tests of `tests/test_session_state_contract.py`:

- **TC-C8** — as at the base, for the step named `Run the session-state tests`.
- **TC-C9** — each Windows job holds the step of R7.1 with each path of R7.1, after the step of
  TC-C8. The ids and names of both jobs are those of the base.

The criteria of the task:

- **A1** — R1: TC-W1 to TC-W10 and TC-W21 to TC-W23 pass, and so do the tests of the base.
- **A2** — R2: TC-W11 to TC-W13, TC-W19, TC-W20, TC-W24 and TC-W26 pass. The texts of R2.4 hold
  no `or the platform`.
- **A3** — R3: TC-W14 and TC-W15 pass.
- **A4** — R4: TC-W16 passes, and `test_g12_a_planted_pyc_is_never_read` still passes.
- **A5** — R5: TC-W17, TC-W18, TC-W25 and TC-W27 pass.
- **A6** — R6: each module of R7.1 passes on macOS in the gates. The audit record holds the read
  of R6.7.
- **A7** — each mutation of the PLAN makes its test fail on macOS, except those that R6.8 marks.
- **A8** — TC-C8 and TC-C9 pass.
- **A9** — R8: `docs/ARCHITECTURE.md`, both changelogs and the WI-39 record hold their text. The
  register scanner `scan_register.py` finds no warning on a line that the change adds.
- **A10** — R9: the gates pass on the patched worktree and, after stage 3, on the tree. The checks
  of R9.3 and R9.4 pass.
- **A11** — after the push, owned by the next task: both Windows jobs pass the step (R7.4), with
  the tests of R6.4 among them. This run cannot decide it.
- **A12** — the final report of this run names the step of R7.1, and asks the operator to push.
- **A13** — R10: TC-W28 passes, and the tests of R6.6 that write Cyrillic pass the encoding.
- **A14** — R11, R12 and the fixes of rounds 1 and 2: TC-W29 to TC-W46 pass, with TC-W23 of twelve
  labels.

<!-- contract:open-questions -->

## 6. Open questions

None. The operator chose the guards (D1), the extra defects (D2), the tests on Windows (D3) and
R3.3 (D8).

## 7. Decisions

- **D1**, 2026-10-27, operator: the Windows branches use the standard library only, and this TASK
  names the windows of a race that remain (D7). Answer "stdlib + окна в TASK (Recommended)".
  Rejected: the Win32 API through `ctypes`, which no run before the push can check.
- **D2**, 2026-10-27, operator: the task fixes the report after the write, the bytecode prefix and
  the paths on two drives (§1 items 6, 8 and 9). Answer "Все три (Recommended)".
- **D3**, 2026-10-27, operator: both Windows jobs run every test module of the chain. Answer "Все
  модули цепочки (Recommended)". Rejected: one new module, which leaves the tests of the base
  unrun on Windows.
- **D4**, 2026-10-27, orchestrator: each script chooses its branch by the capability. Rejected:
  `os.name == "nt"`. A test on POSIX could then reach a branch only by patching `os` for the whole
  interpreter (TASK 127 D10).
- **D5**, 2026-10-27, orchestrator: the move by path copies, and never makes a hard link.
  Rejected:
  - `os.link`: no run has measured it on a file held open without `FILE_SHARE_DELETE`;
  - `os.rename`: a swap before it moves the swapped entry itself, and a failure after it leaves no
    source.
- **D6**, 2026-10-27, orchestrator: the move refuses a read-only source before it writes. Windows
  removes no read-only file, so step 10 would fail after the copy, and the undo would meet a
  read-only copy.
- **D7**, 2026-10-27, orchestrator: these windows of a race remain on a platform without `dir_fd`
  or `O_NOFOLLOW`. A process that can swap entries in `docs/` during a run can already write the
  scripts of the repository (TASK 128 D6). Each step of R1.4 names its entry by path:
  - **RW1** — a link swapped in at `docs` or at the destination directory after its check of step
    1 or step 4. It is swapped back between the checks of step 7. Step 7 then passes, and steps 8 to
    10 read or write at the link's target. With a link at the destination directory, one outcome
    is exit 0, with the archive at the link's target and the source removed. With a link at
    `docs`, steps 9 and 10 may move a `TASK.md` at the link's target, and the real source stays.
    Step 6 of `skill-archive-task` then finds no archive and stops;
  - **RW2** — the same link, swapped back before step 7 or still in place at step 7. Step 7
    refuses, and the file that step 6 created stays at the link's target, empty. The message says
    that it is kept. A destination directory that step 4 created through a link at `docs` stays
    there too. The source stays;
  - **RW3** — a link swapped in at `docs` between step 9 and step 10, or between the check and a
    try of R1.6. Step 10 then removes a `TASK.md` or `PLAN.md` at the link's target, and the
    source stays;
  - **RW4** — an entry swapped in at the source between step 9 and step 10, or between the check
    and a try of R1.6. Step 10 removes it, and the archive holds the moved file;
  - **RW5** — the source removed between the check of R1.6 and a try of the archive's removal. The
    try removes the archive, and neither name holds the content;
  - **RW6** — a link swapped in at the destination's name between step 5 and step 6. Step 6 or
    step 7 refuses. Where the platform has no `O_NOFOLLOW`, the open of step 6 may create a file
    at the link's target, and that file stays. No run has measured it on Windows;
  - **RW7** — a directory swapped for a link between the open of R2.2 and the check of the real
    path. The check then reads the swapped directory, as at the base where no descriptor path
    exists;
  - **RW8** — a junction swapped in between the walk filter of R2.5 and the walk's descent. The
    walk reads the files behind it, and the check of the real path refuses a write to them;
  - **RW9** — on a volume that reports `st_ino` 0, an identity compares the device only;
  - **RW10** — a replacement that receives the source's freed inode number, as ext4 or FAT can
    give it, passes an identity check. Between step 2 and step 3 the run then moves the
    replacement. Between the check and a try of R1.6, the try removes it;
  - **RW11** — a link swapped in at `docs` or at the destination directory after the undo's checks
    of R1.5, before its removal of the archive or of the created directory. Another file put at the
    archive's name in that time is the same case. The removal then reaches the link's target, or
    that file. An archive that another process removes in that time ends the undo with the message
    `…, and docs/<dst> remains (<strerror>)`, though no file remains. One removed after a failed
    try ends it with `docs/<dst> no longer holds the file this run made, so that file is kept`;
  - **RW12** — a write to the source that keeps its size. Windows updates the time of the last write
    fully only when each handle that wrote closes, and FAT keeps that time in steps of 2 seconds. A
    process that writes and keeps its handle open then passes the checks of step 9 and R1.6, and
    the archive holds the text before the write, or a part of it. A write between the last check
    and step 10 is lost the same way.

  The source's descriptor, open from step 3 to step 9, keeps its inode number allocated there. On
  Windows no other process can rename or remove the source in that time: `os.open` grants no
  `FILE_SHARE_DELETE`. It grants the sharing of reads and writes, so step 9 and each try of R1.6
  compare the size and the time of the last write with those of step 2.
- **D8**, 2026-10-27, operator: R3.3 joins the scope. It is the input side of §1 item 6: one
  `except` in the same loop. The orchestrator proposed it; the operator answered "R3.3 оставь".
- **D9**, 2026-10-27, orchestrator: a step in each of the two Windows jobs, and no new job.
  Rejected:
  - two new jobs, which add two runners on Windows to each push;
  - renamed jobs: a check name that a branch rule names would no longer match.
- **D10**, 2026-10-27, orchestrator: `skill-archive-task` stays. Each statement of its Steps 3 to
  8 holds on Windows, and a refusal reaches the operator through the JSON error that each step
  reports.
- **D11**, 2026-10-27, orchestrator: the tries of R1.6 run on every platform, as TASK 128 D9 does.
  A test on POSIX then reaches them.
- **D12**, 2026-10-27, orchestrator: each module holds its own helpers. Stage 1 runs a copy of one
  module beside the base of another, as the duplicate `_descriptor_path` of `slot_links.py` states.
- **D13**, 2026-10-27, orchestrator: the walk filter of R2.5 applies on every platform. On POSIX
  `os.walk` already skips a directory link, so the filter changes nothing there.
- **D14**, 2026-10-27, orchestrator: the Windows jobs run two classes of
  `tests/test_script_guards.py`. Its third class tests `init_skill.py`, which is not in the chain.
- **D15**, 2026-10-27, orchestrator: the next task reads the first run of the Windows step. The
  run never pushes; the operator commits and pushes (TASK 128 D12).
- **D16**, 2026-10-27, orchestrator: a link target written with `\` that resolves to a file other
  than a slot stays a refusal on Windows.
  Windows resolves `\` as a separator, and the check of TASK 117 R2, `_adds_parts`, refuses the
  rewrite.
  The remedy is a link written with `/`. Rejected: a resolution of link targets with `posixpath`
  on Windows, which changes what the file mode reads as an existing file.
- **D17**, 2026-10-27, orchestrator: `task_id_tool.py` joins the change for one flag (R2.7). Its
  allow rule and Step 8 run `_first_h1`, and a text-mode read stops at a byte `0x1A` before the
  H1. Rejected: §9, which would leave one open of the chain in text mode.
- **D18**, 2026-10-27, orchestrator: revision 2 applies every finding of Mode A round 1. N1 needs
  no change; N3 is in D7.
- **D19**, 2026-10-27, orchestrator: revision 3 applies every finding of Mode A round 2. Its M1 is
  TC-W21: the base flag `O_NOFOLLOW` of step 3 refused a link before the identity check, so the
  test swaps in a regular file.
- **D20**, 2026-10-27, orchestrator: revision 4 applies m1, m2, N1 and N2 of Mode A round 3, which
  passed. The source's descriptor stays open through step 9, as the base holds it to the end of
  the move. N3 needs no change: no setting of the sibling checkout names a script of the chain.
- **D21**, 2026-10-27, orchestrator: R10 joins the scope. The read of PLAN B1 found that six tests
  of D3 with Cyrillic text fail on the runner. A fix of the tests alone leaves
  `archive_protocol.py` reading UTF-8 as cp1252. Line ends stay: a change there alters the archive
  on POSIX too. The operator may remove R10. Rejected: a skip of the six tests on Windows, which
  leaves the defect.
- **D22**, 2026-10-27, orchestrator: a test whose premise is a behaviour of POSIX skips on Windows
  (R6.5). Rejected: a rewrite of each premise for Windows, which tests behaviour that the task does
  not change, such as a `..` resolved by the kernel.
- **D23**, 2026-10-27, orchestrator: TC-W6 on Windows asserts the protection of D7. The source's
  descriptor grants no `FILE_SHARE_DELETE` from step 3 to step 9, so a swap there fails in the
  test, and the move completes. Rejected: a skip, which leaves that claim of D7 untested.
- **D24**, 2026-10-27, operator: R11 joins the scope. Code review round 1 found that the masks of
  `rebase_links.py` close no fence on CR LF, which Git for Windows checks out by default. Answer
  "Чинить в TASK 131 (Recommended)". Rejected: a work item, which leaves Steps 5.5, 7.6.5 and 8
  blind after the first fence on Windows.
- **D25**, 2026-10-27, operator: R12 joins the scope. The security audit of round 1 found, before
  the task, that a UNC path of `--repo-root` or `--tasks-dir` sends the user's NTLM credentials to
  its host on Windows. Answer "Чинить в TASK 131 (Recommended)". Rejected: a backlog record.
- **D26**, 2026-10-27, orchestrator: the fix of round 1 of stage 2 applies each finding of both
  reviews. It changes R1.4 steps 2 and 9, R1.5, R1.9, R2.2, R2.3, R2.5, R5.5, RW1, RW2 and RW11, and
  adds TC-W29 to TC-W42. A fixture that a test compares by its bytes is written with LF.
- **D27**, 2026-10-27, orchestrator: `_descriptor_path` gives no path where `os.name` is not
  `posix`. `fcntl` and `/proc` exist on POSIX only; on Windows the import searches every entry of
  `sys.path`, and `/proc` names a path on the current drive. Rejected: a choice by capability, as
  D4 states for a branch: this choice skips a lookup, and changes no branch.
- **D28**, 2026-10-27, orchestrator: the fix of round 2 of stage 2 applies each finding of both
  reviews:
  - R12.1 reads the text. `ntpath.splitdrive` gives no drive for `\??\UNC\host\share` (§8). By the
    security audit of round 2, the `splitdrive` of 3.11 gives none for `\\host\\share`,
    `\\\host\share` and `\\host` either;
  - step 9 compares the `os.lstat` of step 2, so each try of R1.6 repeats the check of the size
    and the time after the source's descriptor closes;
  - each try of the undo checks the archive again, and the message names a file of step 6 that
    the undo keeps (RW2, RW11);
  - TC-W30 and TC-W31 assert on Windows the outcome of a rename that a descriptor of the run
    refuses, as TC-W6 does (D23). Rejected: a skip, which leaves both tests unrun there;
  - TC-W39 and TC-W42 assert the result on POSIX with `posixpath`, since `os.path` is `ntpath` on
    the Windows jobs.
- **D29**, 2026-10-27, orchestrator: round 3 of stage 2, the last of the bound, passed: the code
  review approved, and the security audit passed. The run closes stage 2 with no fourth round, as
  the operator chose for TASK 124 once both reviews passed. Its LOW findings take these forms:
  - the wording of R12.1 on `splitdrive`, the heading of R12, and its headline in both changelogs
    are corrected in place: the check covers the two arguments;
  - RW11 names the message after an archive that another process removes;
  - §9 names Python for Cygwin and MSYS2;
  - a double blank line in the class `TestInboundGuard` of `tests/test_script_guards.py`, the staged
    copy at round 3, stays. So does TC-G20, whose hard link the reviewer expects Windows to make. A
    change of the reviewed bytes would need a fourth round.

## 8. Measurements of this run

Measured at the base revision with Python 3.14.8 on macOS, in roots under the session's scratchpad.
A `sitecustomize.py` set `os.supports_dir_fd` to an empty set and deleted `os.O_NOFOLLOW`, as
Windows lacks both.

- Run 1: `archive_move.py docs/TASK.md docs/tasks/task-900-x.md` → exit 2,
  `this platform has no dir_fd support for open, mkdir, link and unlink`.
- Run 2: the file mode on `docs/tasks/task-900-x.md` → exit 2,
  `docs/tasks/task-900-x.md: this platform has no O_NOFOLLOW`.
- Run 3: `rebase_links.py --inbound --task docs/tasks/task-900-x.md` → exit 2,
  `this platform has no O_NOFOLLOW`.
- Run 4: `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`, the file mode on a document that links to
  `notes/заметка→.md` → exit 1, `UnicodeEncodeError: 'ascii' codec can't encode characters`. The
  document was rewritten to `../notes/заметка→.md` before the traceback.
- Run 5: the file mode on a document with the cp1251 bytes `D2 C7` →
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd2`, exit 1.
- Run 6: `ntpath.devnull` is `'nul'`, and `ntpath.isabs('nul')` is false.
  `ntpath.commonpath(['C:\\repo', 'D:\\x'])` raises `ValueError: Paths don't have the same drive`.
  `ntpath.isabs('/x')` is false.
- Run 6b, at stage 2 round 2: `ntpath.splitdrive('\\??\\UNC\\host\\share')` gives
  `('', '\\??\\UNC\\host\\share')`, no drive.
- Run 7: `ntpath.relpath` of `C:\repo\docs\tasks\task-001-x.md` from `C:\repo` gives
  `docs\tasks\task-001-x.md`. The `parts` of `_adds_parts` read it as one part, and the new target
  `../tasks/task-001-x.md` as two: the check returns true.
- `tempfile` adds `_os.O_BINARY` to its flags where it exists.
- `os.walk` of 3.14.8 descends with `followlinks=False` unless `os.path.islink`, or
  `DirEntry.is_symlink`, is true. Both are false for a junction.
- The modules of R7.1 collect these tests:
  - `tests/test_archive_move.py`: 27;
  - the two classes of `tests/test_script_guards.py`: 30 of its 34;
  - `.agent/tools/test_rebase_links.py`: 52;
  - `.agent/tools/test_slot_links.py`: 71;
  - `.agent/tools/test_archive_protocol.py`: 56;
  - `.agent/tools/test_task_id_tool.py`: 78.

  The step of R7.1 runs 314 tests at the base.
- In the sibling checkout `Universal-skills`, `.agent/tools` links to
  `../.agentic-development/.agent/tools`, and `.agentic-development` links to this repository. Two
  rules of the user's settings run `task_id_tool.py` by an absolute path in that checkout.
- Step 8 of this run's archive of TASK 130 exited 3 with two `INBOUND` records, in
  `CHANGELOG.md:3618` and `CHANGELOG.ru.md:3647`. It rewrote no file.

<!-- contract:out-of-scope -->

## 9. Out of scope

- The locks and `O_NOFOLLOW` of `run-feedback` — the third task of the Windows series.
- A statement of supported platforms in `README.md` — the last task of the series (TASK 127 §9).
- The `python3` launcher on Windows — the reporter's answer is still open (TASK 127 §9).
- The search of the working directory for `git.exe` by `CreateProcess` on Windows. Every caller of
  git there meets it, Claude Code among them.
- `init_skill.py` on Windows — the WI-39 record and a later task.
- A volume whose `os.lstat` and `os.fstat` give different identities for one file. The checks of
  R1 and R2 then refuse every file; no run here can reach such a volume.
- The letter case of a slot path in `rebase_document_links` — a finding before the task (audit
  record, round 1 B1).
- The `shutil.move` of `archive_protocol.py` on Windows. Its tests run on the Windows jobs (D3),
  and a failure there goes through R7.4.
- WI-39 for the nine scripts without a filter — the WI-39 record.
- Findings before the task, from the security audits of stage 2:
  - the file mode prints the control characters of a link target unescaped (round 1);
  - `task_id_tool.py --tasks-dir` creates its directory at any path that the argument names
    (round 2);
  - on the Python of Cygwin and of the MSYS2 runtime, `os.path` is `posixpath`, so `_unc` refuses
    no `//host/share`, as at the base (round 3). The framework supports neither interpreter. The
    mingw-w64 Python of MSYS2 uses `ntpath`, and `_unc` refuses there as on Windows.
