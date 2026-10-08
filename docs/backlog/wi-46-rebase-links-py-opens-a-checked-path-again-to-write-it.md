---
id: WI-46
type: work-item
status: done
opened_at: 2026-10-08
slug: wi-46-rebase-links-py-opens-a-checked-path-again-to-write-it
effort: M
value: 'no directory swapped after the write guard of rebase_links.py can carry its write elsewhere'
source: 'TASK 116 D8'
component: '.agent/tools/rebase_links.py'
resolved_at: 2026-10-08
resolved_by: 'TASK 116'
---

# WI-46 — rebase_links.py opens a checked path again to write it

> **Done 2026-10-08 (TASK 116, R7; operator decisions D13, D14 and D16).** Both modes write
> through the descriptor they checked. This is option 2 of this record, with the directory
> checked by the descriptor's own path. Option 1, which TASK 116 D5 calls WI-40 option 2, was
> rejected: it refuses the links inside the root that TASK 116 R1.2 keeps.
>
> - The file mode opens every operand read-only with `O_NOFOLLOW` before it reads any. The
>   descriptor must be the regular file at the operand's real path, with one hard link. The
>   directory of the descriptor's own path, as the kernel gives it, must lie inside the working
>   directory. A second descriptor writes only a changed text, and only when it names the same
>   inode and passes the same check.
> - The inbound mode's `_write_file` makes the same check after its open.
> - TC-G16 to TC-G22 pin the three changes of this record, a file replaced after the read and a
>   platform with no `O_NOFOLLOW`. TC-G23 to TC-G27 pin a directory moved out and linked back,
>   a failed write, a FIFO, the closes and three swaps around the identity check. A rename out
>   of the root between the last check and the write stays a residual (TASK 116 §11).

> Origin: TASK 116 D8, which closed WI-40 with its option 1. `rebase_links.py` is installed into
> other repositories: a behaviour change for the framework owner's review, not a landed fix.

**Signal.** Both modes of `rebase_links.py` check an operand, then open it again by path to write
it:

- the file mode: `_refuse_operand` checks the operand and its directory by real path, then
  `rebase_file` opens the path with `open(path, "w")`;
- the inbound mode: `slot_links._write_file` checks the directory by real path, then opens the
  path. Its device, inode, byte and link-count checks pin the write to the inode it read.

Between the checks and the open of the file mode, three changes move or widen its write:

- a directory on the path swapped for a link;
- the file itself swapped for a link, after the check of `os.path.islink`;
- a second hard link made to the file, after the check of its link count.

TASK 112 §7 accepted this window for the file mode; TASK 115 D10 recorded "the directory-swap race
of R5.2" of the inbound mode as a work-item.

**Why it matters.** The script runs with no prompt under
`Bash(python3 .agent/tools/rebase_links.py *)`. Using the window needs a process that writes the
working tree during the archive step.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Both modes open each directory by descriptor with no link followed, as `archive_move.py` does | M | needs `dir_fd` support, which `archive_move.py` already checks |
| 2 | The file mode opens with `O_NOFOLLOW` and pins its write to the inode it read, as the inbound mode does | S | the window for the directory stays |
| 3 | do nothing, document the constraint | — | the window stays as TASK 112 §7 accepted it |

**Recommendation.** Option 1; the minimum is option 2.

**Acceptance.** A test makes each of the three changes between the check and the write, and
neither mode writes through it.

**Related.** [WI-40](wi-40-rebase-links-py-writes-through-a-linked-parent-directory.md), closed by
TASK 116 with option 1; TASK 112 §7; TASK 115 D10.
