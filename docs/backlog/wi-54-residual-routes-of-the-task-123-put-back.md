---
id: WI-54
type: work-item
status: done
opened_at: 2026-10-15
slug: wi-54-residual-routes-of-the-task-123-put-back
effort: S
value: 'the put-back of framework-upgrade §3 step 4 never deletes the only copy of a file, and never acts through a link'
source: 'TASK 123 stage 2, round 3 (D20)'
component: '.agent/workflows/framework-upgrade.md'
resolved_at: 2026-10-28
resolved_by: 'TASK 135'
---

# WI-54 — Residual routes of the TASK 123 put-back

> **Done 2026-10-28 (TASK 135).** Option 1 (TASK 135 D3, R4 to R6).
>
> - The put-back of `framework-upgrade` §3 step 4 removes nothing: it names each created path to
>   the operator. S3-1 and S3-2 close by construction.
> - The check hashes what the user's three files hold, through a link (R3-2). The restore command
>   carries `-c core.fsmonitor=false`, and a file whose hash then differs stops the run (R3-4,
>   I-2).
> - `tests/test_run_safety_rules.py` pins step 4.

**Signal.** TASK 123 added a check of what a change runs to `framework-upgrade` §3 step 4, and a
put-back after it. Round 3 of its stage-2 review, the last that the bound allows, passed. Its
findings were LOW routes of classes that earlier rounds had fixed, and the operator chose this
record over a fourth round (TASK 123 D20). `docs/reviews/framework-audit-123.md` records them:

- **A created file can hold the only copy of a changed file (S3-1).** A command can copy a file and
  then overwrite it, or move it and create it again. The listing then shows a created file and a
  changed one, and nothing under `.git` or missing. The put-back removes the created file. When the
  changed file is ignored or declared, the run names it to the operator but cannot restore it.
- **A created link to a directory can read as a directory (S3-2).** `rmdir` of such a path with a
  trailing slash removes the link's empty target, and `rm -r` would remove the target's files. The
  text does not say how the put-back removes a file or a directory.
- **The user's files through a link (R3-2).** The text does not say that the check hashes what a
  linked user file holds, so a write through a dotfiles link could pass unseen.
- **Two wordings (R3-4, I-2).** The restore command of the put-back omits `-c core.fsmonitor=false`,
  which the sentence before it requires. The text does not say that a file that hashes otherwise
  after the restore stops the run.

Each round of that review found a narrower route of one class, as TASK 116 did (WI-48).

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | The put-back deletes nothing: it names each created path to the operator, who removes it | S | closes S3-1 and S3-2 by construction; the operator removes leftovers by hand |
| 2 | Patch each route of the put-back | S | keeps the automatic put-back; a later route needs its own patch |

Option 2 keeps a created file whose SHA-256 equals that of a changed or missing file. It removes
files and links with `rm --` and then directories with `rmdir --`, deepest first, and a failed
removal or hash check stops the run. Both options also state that the check hashes a user file
through a link, and add the flag and the stop of the last bullet.

**Recommendation.** Option 1.
