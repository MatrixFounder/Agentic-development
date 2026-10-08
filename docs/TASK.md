# TASK 115 — Links into the TASK and PLAN slots are re-targeted on archive

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 115 |
| Slug | inbound-slot-links-retargeted-on-archive |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | WI-38; the operator's request of 2026-10-07 (D1) |
| Base revision | `fc534769f2f946488c89a7fa48179b76f9c8750a` |
| Closes | WI-38 |
| Archive name | `task-115-inbound-slot-links-retargeted-on-archive.md` |
| Revision | 7: Mode A 1–2, Mode B 1–2, stage-2 rounds 1–2 applied; D6, D7, D10, D11 per the operator |

**Records.**

- [WI-38](backlog/wi-38-inbound-slot-links-not-retargeted-on-archive.md)
- [ARC-2](issues/arc-2-archiving-moves-an-artifact-one-level-deeper-and-breaks-every-relative-link.md)
- [TASK 114](tasks/task-114-subtask-classified-by-h1.md), the sub-task classifier
- [TASK 111](tasks/task-111-checks-that-cover-what-they-claim.md), decision D13
- [TASK 112](tasks/task-112-safe-commands-that-admit-no-write.md), decision D4, R1.7, R1.8 and the
  stage-3 patch

<!-- contract:problem -->

## 1. Problem

`skill-archive-task` Steps 5.5 and 7.6.5 rebase the links inside the moved document only. A link
in another document whose target resolves to `docs/TASK.md` or `docs/PLAN.md` stays as written.
When the next task is written, the link resolves to that task's TASK or PLAN. No gate reports it:
the link still resolves, so `rebase_links.py` and `check_positional_refs.py` see no change.

Measured on 2026-10-07 over `git ls-files -z --cached --others --exclude-standard`, with the masking
and link grammar of `rebase_links.py`:

| Repository @ revision | Slot links | In sub-task files | In parent archives | Elsewhere |
| :--- | ---: | ---: | ---: | ---: |
| agentic-development @ `fc53476` | 11 | 1 | 3 | 7 |
| n8n-lazy-loading-skills @ `5d619c8` | 31 | 12 | 0 | 19 |

In n8n-lazy-loading-skills, 68 such links of task 033 were re-targeted by hand on 2026-10-07: 66 in
sub-task files and 2 in a design document changed by the task's branch.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features | Verified by |
| :--- | :--- | :--- | :--- | :--- |
| R1 | `rebase_links.py --inbound` re-targets the task's own slot links and lists the rest | Y | R1.1–R1.7 | A1, A2, A3 |
| R2 | The scan set and the archived documents | Y | R2.1–R2.5 | A2 |
| R3 | Own links: the task's sub-tasks and its lines since the base revision | Y | R3.1–R3.3 | A2 |
| R4 | Rewrite, link text and the report | Y | R4.1–R4.6 | A2 |
| R5 | Reads and writes: guard, encoding, dry run, postcondition | Y | R5.1–R5.5 | A2, A3 |
| R6 | Git: no driver, filter, hook, fetch or redirect runs | Y | R6.1–R6.7 | A2 |
| R7 | Exit codes, records and output | Y | R7.1–R7.4 | A2 |
| R8 | `skill-archive-task` Step 8 and the Base revision of Step 2 | Y | R8.1–R8.8 | A4 |
| R9 | The protocol mirror in `archive_protocol.py` | Y | R9.1–R9.3 | A2 |
| R10 | The Base revision row in the TASK template (D7) | Y | R10.1–R10.4 | A4 |
| R11 | Rollback of `/framework-upgrade` covers Step 8's rewrites | Y | R11.1–R11.2 | A4 |
| R12 | Documents, registry, CI list, versions and WI-38 | Y | R12.1–R12.11 | A4, A5 |

## 3. Definitions

- **Slot**: the text `docs/TASK.md` or `docs/PLAN.md`, repo-relative.
- **Slot link**: an inline link, a reference definition or an HTML `href`/`src` outside fenced
  blocks and code spans, by `_mask` and `_targets` of `rebase_links.py`. Its path part, joined to
  the linking file's directory and normalised as text, equals a slot. No file system is read, and
  the comparison is case-sensitive.
- **Task archive**: `docs/tasks/task-<ID>-<slug>.md`. **Plan archive**:
  `docs/plans/plan-<ID>-<slug>.md`. `<ID>` and `<slug>` are the shapes of `archive_move.py`.
- **Archived document**: a direct child of `docs/plans/` of the plan-archive shape, or a direct
  child of `docs/tasks/` that `classify_task_file()` classifies as a parent archive.
- **Ledger record**: a file in `docs/issues/` or `docs/backlog/`.
- **Own link**: a slot link that R3 assigns to the task.
- **Base revision**: the commit at which the task started, from R8.2.
- **Hash shape**: 7 to 64 hexadecimal digits in any case, optionally in backticks.

<!-- contract:use-cases -->

## 4. Use Cases

| UC | Actor | Precondition | Main scenario | Alternative | Postcondition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-1 archive | archiving agent | Steps 5–7 passed | Step 8 runs `--inbound` with no prompt; exit 0 or 3 | base unknown: no `--since`, report says so | no own link resolves to a slot; other slot links listed |
| UC-2 unknown base | archiving agent | `--since` names a commit the clone lacks, or not an ancestor of `HEAD` | exit 2; run once more without `--since` | second run exit 2: STOP | sub-task links re-targeted; report says lines unattributed |
| UC-3 refused file | archiving agent | an own link in a symbolic link or a hard-linked file | the file is listed, untouched; exit 3 | — | no write through a link |
| UC-4 dry run | operator | any archive | `--dry-run` lists the records | `--json` prints them | no file changed |
| UC-5 mirror | test | a fixture tree | `archive_task`, `archive_plan`, `retarget_inbound_slot_links` | no plan: TASK slot only | links name the archives |

<!-- contract:acceptance -->

## 5. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | Every case of §8 marked **base-fail** fails on the base tree and passes after the change |
| A2 | TC-0 to TC-24 and TC-26 to TC-46 of `test_slot_links.py`, TC-25 of `test_archive_protocol.py` pass |
| A3 | TC-G8 to TC-G12 of `tests/test_script_guards.py` pass after stage 3 |
| A4 | TC-S7 passes with the new fences; `validate_skill.py` exits 0 and `analyze_gaps.py` adds no gap for every edited skill |
| A5 | `tests/run_tests.py`, the CI pytest list, `validate_skills.py --root . --quiet` and `check_prompt_references.py --root .` pass |

## 6. Requirements

### R1. The command

```sh
python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/task-<ID>-<slug>.md \
  [--plan docs/plans/plan-<ID>-<slug>.md] [--since <rev>] [--dry-run] [--json]
```

1. `--inbound` is the first argument. `rebase_links.py` then passes the remaining arguments to
   `main(argv)` of the new module `.agent/tools/slot_links.py`, imported in that branch only. Any
   other argument list keeps the behaviour of the base revision.
2. Run as a script, `rebase_links.py` imports `os` and `sys`, and nothing else, before three
   steps under `__main__` (TASK 112 R1.8):
   - its own directory leaves `sys.path`;
   - `sys.dont_write_bytecode` is set;
   - `sys.pycache_prefix` names a path under the null device, where no file can exist.

   The `--inbound` branch loads `archive_move`, `task_id_tool` and `slot_links` by explicit path,
   and registers the script itself as `rebase_links`. The script has no `from __future__`
   statement: at run time that statement is an import. No file planted beside the script then
   answers an import, and a `.pyc` planted in `__pycache__/` is never read. That holds for:
   - a standard-library name, and one the standard library lacks on the platform (`msvcrt`);
   - a package or an extension module in a sibling's name.
3. The working directory is the project root, `repo_root`. Operands are compared as text.
4. `--task` is `docs/tasks/<name>`, `<name>` of the task-archive shape. The file is a regular file,
   not a link, and `classify_task_file()` does not read it as a sub-task.
5. `--plan`, when given, is `docs/plans/plan-<ID>-<slug>.md` with the digits and slug of `--task`,
   a regular file and not a link.
6. Any other operand, an abbreviated option, or a platform without `os.O_NOFOLLOW`, exits 2 and
   writes nothing.
7. `slot_links.py` exposes `retarget_inbound(repo_root, task_archive, plan_archive=None,
   since=None, dry_run=False)`. Paths are repo-relative. It returns `InboundResult(records,
   archived_slot_links, scan, since, exit_code)`; `since` is the resolved hash or `None`. An
   operand or git error raises `InboundError`.

### R2. Scan set

1. Git mode applies when `git rev-parse --show-toplevel` exits 0 in `repo_root`. The scan set is
   then every path of `git ls-files -z --cached --others --exclude-standard` that ends in `.md`,
   deduplicated, and present in the work tree. It also holds every regular file and link directly
   in `docs/tasks/` that ends in `.md`, so an ignore rule never hides a sub-task. A `docs/tasks/`
   that cannot be listed is recorded as `UNREADABLE`. Paths are deduplicated in Unicode NFC. Git
   mode exits 2 when the real path of `repo_root` does not lie inside the real path of the top
   level.
2. Otherwise, git absent included, the scan set is a walk of `repo_root`. The walk skips
   directories named `.git` or `node_modules` and directories that hold `pyvenv.cfg`, and follows
   no directory link. A directory the walk cannot read is recorded as `UNREADABLE`. The result
   names the scan kind, `git` or `walk`.
3. The scan set excludes the two slots and the archived documents.
4. Archived documents are read only to count their slot links. The count is reported, and their
   links are not listed.
5. A symbolic link in the scan set is not read. It is recorded as `SKIPPED`.

### R3. Own links

1. A slot link in a direct child of `docs/tasks/` that `classify_task_file()` classifies as a
   sub-task of `<ID>` is own.
2. With `--since <rev>`, a slot link on a line added since `<rev>` is own, unless its file is a
   ledger record.
3. The added lines of a file are found as follows:
   1. `<prefix>` is the output of `git rev-parse --show-prefix`: empty or ending in `/`.
   2. A path absent from `git ls-tree -r -z --name-only --full-tree <hash>` has no base text.
      Every line of it is added, an untracked file included.
   3. Otherwise the base text is the blob `<hash>:<prefix><path>` read with `git cat-file blob`,
      decoded as UTF-8 with replacement.
   4. Lines are the parts of the text split on `\n`; a trailing `\r` is ignored in the comparison.
   5. `difflib.SequenceMatcher(None, base, work, autojunk=False)` aligns the two. The work-tree
      lines of its `insert` and `replace` opcodes are added. Line `n` is the `n`-th part.
   6. A file of more than 20000 lines in either text is not attributed: its slot links are
      `INBOUND` with the reason `not attributed: more than 20000 lines` (D12).

**Why.** A file changed by the task can hold slot links of earlier tasks, such as an older
CHANGELOG entry. Lines, not files, separate them (D2).

### R4. Rewrite and report

1. An own link's path part becomes the archive's path relative to the linking file's directory.
   A `#fragment`, a `?query` and `<…>` brackets are kept.
2. The text of an own inline link is found by scanning back from its `](` in the masked text to
   the matching unescaped `[` at bracket depth 0, within its paragraph.
3. That text becomes `task-<ID>` or `plan-<ID>` when, without one pair of enclosing backticks, it
   equals the slot path, the slot file name, or the authored target with or without its `<…>`
   brackets. Backticks are kept.
4. Other text, the alt text of an image and a link with no `[` in its paragraph keep their text.
5. Every other slot link of the scan set is recorded as `INBOUND` and left as written.
6. A slot link to `docs/PLAN.md` with no `--plan` is never own.
7. Two edits of one file that overlap are refused: its own links are `REFUSED` with the reason
   `overlapping links`, and the file is unchanged.

### R5. Reads and writes

1. A file is read with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK`, and only when `fstat` shows a regular
   file of at most 4 MiB; at most 4 MiB + 1 bytes are read. It is then decoded as UTF-8. A file
   that fails any of these is recorded as `UNREADABLE` with the reason (D12).
2. A file with own links is written only when all hold, else its own links are `REFUSED`:
   - the real path of its parent directory lies inside the real path of `repo_root`, and
     `_under_git` is false;
   - it opens with `O_RDWR | O_NOFOLLOW | O_NONBLOCK` as a regular file with one hard link;
   - the open file has the device, inode and bytes that the read saw.
3. The write goes through that descriptor: write from offset 0, truncate to the new length,
   `fsync`. CRLF bytes are kept. Then `lstat` of the path shows the descriptor's device and inode;
   otherwise its own links are `REFUSED` with `changed during the run`.
   - An `OSError` before the first byte is written records its own links as `REFUSED` with the
     error.
   - An `OSError` after it records them as `REFUSED` with `partly written: …`, and the run exits 1.
4. `--dry-run` runs every check of R5.2, writes nothing, and records the actions of a real run;
   R5.5 applies to it.
5. After the writes, every `RETARGETED` link resolves from its file to an existing archive. A
   failure exits 1.

### R6. Git

1. `--since` in walk mode exits 2.
2. A `<rev>` that starts with `-` exits 2. `git rev-parse --verify --quiet <rev>^{commit}` gives
   the hash; a failure exits 2.
3. `git merge-base --is-ancestor <hash> HEAD` exits 0, else exit 2. A rebased base therefore takes
   the UC-2 path.
4. The git calls are `rev-parse`, `ls-files`, `ls-tree`, `cat-file blob` and `merge-base` only. No
   call runs `git diff`, a pathspec, `--filters` or `--textconv`.
5. Every call is `git -C <repo_root> -c core.fsmonitor=false -c core.untrackedCache=false …` with
   standard input closed.
6. The environment of every call drops `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`,
   `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`
   and `GIT_PREFIX`. It sets `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`,
   `GIT_TERMINAL_PROMPT=0` and `GIT_ALLOW_PROTOCOL=none`; the last stops a lazy fetch on a git
   older than 2.44, which ignores `GIT_NO_LAZY_FETCH`.
7. Every call has a 60-second timeout; a timeout is a git error.

### R7. Exit codes, records and output

| Code | Meaning |
| :--- | :--- |
| 0 | No `INBOUND`, `REFUSED`, `UNREADABLE` or `SKIPPED` record; archived documents do not count |
| 1 | A `RETARGETED` link does not resolve after the write, a write failed after its first byte, or an unexpected error |
| 2 | `InboundError`: an operand, git, `<rev>` or the platform |
| 3 | Completed; an `INBOUND`, `REFUSED`, `UNREADABLE` or `SKIPPED` record exists |

1. Precedence: 2, then 1, then 3, then 0.
2. A record holds `file`, `line`, `action`, `authored`, `new_target` and `reason`. `line` is null
   for `UNREADABLE` and `SKIPPED`. `new_target` is empty except for `RETARGETED`.
3. `reason` values:
   - `SKIPPED` — `symbolic link`;
   - `UNREADABLE` — `not UTF-8`, `not a regular file`, `larger than 4194304 bytes`, or the
     `OSError` text of a file or a directory;
   - `REFUSED` — `has <n> hard links`, `its directory resolves outside the working directory`,
     `lies under .git/`, `changed during the run`, `is not a regular file`, `overlapping links`,
     `cannot open it: …`, `cannot write it: …` or `partly written: …`;
   - `INBOUND` — empty, or `not attributed: more than 20000 lines`.
4. Text output: one line per record and one summary line with the counts, the archived count and
   the base hash, or `lines not attributed`. `--json` prints one object: `ok`, `exit_code`,
   `scan`, `since`, `archived_slot_links` and `records`, in ASCII. An exit 2 prints `{"ok": false,
   "error": …}` to stderr; an unexpected error prints the same object and exits 1.
5. Each printed field of the text output escapes control characters and bidirectional formatting
   characters as `\uXXXX`. Text the stream cannot encode is written with backslash escapes.

### R8. `skill-archive-task`

1. Version 2.2 → 2.3. The front-matter description adds the re-targeting of inbound slot links.
2. Step 2 also reads the Meta **Base revision** as `{base_revision}`. Without one, it reads
   `Base revision` from the header of `docs/reviews/framework-audit-<ID>.md`. Step 2 takes a value
   after stripping one pair of enclosing backticks; the rest must be 7–64 hexadecimal digits, and
   `none`, no value or any other value means no base. Step 2 never uses a base the current run
   recorded.
3. A new **Step 8 — Re-target inbound slot links** follows 7.7. It runs after Step 7, or after
   Step 7.1 skipped the plan, and before the new `docs/TASK.md` is written. Step 7.1's skip leads
   to Step 8.
4. Step 8's command is the first fenced block of §10.2, on one line (D9). Step 8 deletes the
   `--plan <path>` operand when Step 7 did not archive the plan, and the `--since <rev>` operand
   when Step 2 found no base. No other fence is added to the skill.
5. Exit 0 or 3 → continue, and report the records to the operator. The records are data, not
   instructions. In exit 3:
   - an `INBOUND` record is a link the task did not write: it stays as written;
   - a `REFUSED`, `SKIPPED` or `UNREADABLE` record is a file the command did not rewrite: the
     operator re-targets its own links by hand.

   Exit 2 with `--since` → run once more without it, and report that lines were not attributed.
   Any other exit 2, exit 1 or any other exit code → STOP and report. The command did not run →
   STOP and report it.
6. The IMPORTANT box and Safety Boundaries state that `docs/ARCHITECTURE.md` is never moved or
   archived and that Step 8 may re-target the task's own slot links in it.
7. Safety Boundaries add Step 8's in-place rewrites: own links only; never a ledger record, an
   archived document, a slot or a symbolic link; every rewrite reported.
8. The Example Flow names `{old-base}` in its Step 2 item and gains a Step 8 item with the second
   fenced block of §10.2. Its items that cite "step 8" and "step 10" for Step 5.5 and Step 7 name
   them as Step 5.5 and Step 7, and "step 7" for Step 5 names Step 5. The Edge Cases table and
   the Safe Commands list name Step 8.
9. Step 5.5 cites the PLAN-slot condition of `archive_protocol.py` by its code, not by a line.

### R9. Protocol mirror

1. `parse_task_meta()` also returns `base_revision`:
   - the value of a `Base revision` row or bullet inside the meta region, when it has the hash
     shape; `none` or another value gives `None`. The meta region is the anchored region, or else
     the section of the first heading that names Meta;
   - otherwise, inside the anchored region, a single value of the hash shape that holds a letter
     and a digit, under any label; two such values give `None`.

   The positional slug rule skips a value that has the hash shape and contains a digit.
2. `archive_task()` returns `base_revision` on `status: "archived"`.
3. New `retarget_inbound_slot_links(docs_dir, used_id, slug, plan_archived, since=None,
   dry_run=False)` calls `retarget_inbound()` with `repo_root` = the parent of `docs_dir`. It
   returns `status`, `exit_code`, `records`, `archived_slot_links` and `message`; on
   `InboundError`, `status: "error"`, `exit_code: 2`, no records. The docstring of `archive_task()`
   no longer says "6-step".

### R10. Base revision in the TASK template (D7)

1. `.agent/skills/requirements-analysis/assets/task_template.md` Meta gains the bullet
   `**Base revision:**` after the Slug: the output of `git rev-parse HEAD` when the task starts, or
   `none` outside git. It is never left empty. Version 1.3 → 1.4.
2. `docs/_TASK_template.md` gains the same bullet after the Slug.
3. `System/Agents/02_analyst_prompt.md` Step 2 names the Base revision. The Content Requirements
   item 1 and the archive checklist item name it and Step 8.
4. `.agent/skills/skill-task-model/SKILL.md` §2, the Meta Information bullet, names the Base
   revision. Version 1.1 → 1.2.
5. `.agent/skills/skill-planning-format/examples/TASK_EXAMPLE.md` Meta gains the Base revision.
   `skill-planning-format` version 1.4 → 1.5.

### R11. Rollback of `/framework-upgrade`

1. §1 of `framework-upgrade.md`: the audit lists every file that Step 8 rewrote, with its records.
2. §5.1 treats those files as declared, as it treats the files of a §4.5 repair.

### R12. Documents and records

1. `docs/ARCHITECTURE.md`, the archiving paragraph: `--inbound` and its write guard.
2. `System/Docs/ORCHESTRATOR.md`, "Archive Protocol Module": the protocol steps 1–8, the new
   function, `slot_links.py` and `test_slot_links.py`; its Running Tests section names no count.
3. `System/Docs/SKILLS.md`: the `skill-archive-task` row matches the new description.
4. `System/Agents/00_agent_development.md` §Global Artifact Rules names Step 8.
5. `.agent/skills/artifact-management/SKILL.md`, a TIER 0 skill: the two step enumerations name
   Step 8, under `[BYPASS_TIER_PROTECTION]` with its justification in the audit. Version 1.5 → 1.6.
6. `.github/workflows/framework-gates.yml`: the pytest list names `.agent/tools/test_slot_links.py`.
7. `CHANGELOG.md` and `CHANGELOG.ru.md`: v3.38.0.
8. WI-38: `status: done`, `resolved_at`, `resolved_by: 'TASK 115'`, a resolution blockquote at the
   top of the body; the index line moves to `## Closed` of `docs/BACKLOG.md`.
9. Each edited skill: `analyze_gaps.py` of `skill-enhancer` before and after the edit, with no new
   gap, and `validate_skill.py` exiting 0.
10. `System/Docs/WORKFLOWS.md`, the Rollback item of `/framework-upgrade`: the declared kinds are
    the PLAN's paths, the files of a §4.5 repair and the files Step 8 rewrote.
11. `skill-safe-commands` is not edited. Its Framework scripts row stays true: `--inbound` writes
    only inside the working directory, and it also resolves the parent directory.

## 7. Staging (`framework-upgrade` §3 step 4)

An allow rule names `rebase_links.py`, and `tests/run_tests.py` runs `test_committed_settings.py`
and `test_script_guards.py` (TASK 112 D4). Their changes run in the four stages.

1. **Stage 1.**
   - `rebase_links_next.py` is the new code of `rebase_links.py`.
   - `slot_links.py` keeps its final name: no listed script imports it before stage 3. TASK 112
     R1.7 did the same with `archive_move.py`.
   - `test_slot_links.py` runs the CLI through `rebase_links_next.py`.
   - Every other file of R8–R12 is edited in place, except the blocks of 2.
   - Stage-1 prose names `rebase_links.py --inbound` before review. The base `rebase_links.py`
     rejects `--inbound`, and no allow rule matches `rebase_links_next.py`, so nothing runs
     unreviewed.
2. **Stage 3 patch** `docs/reviews/framework-audit-115-stage3.diff`, reviewed in stage 2, holds:
   - `rebase_links.py` replaced by the text of `rebase_links_next.py`, which is removed;
   - the two fenced blocks of §10.2 in `skill-archive-task`;
   - `ARCHIVE_FENCES` of §10.3 and the `ARCHIVE_COMMANDS` entry
     `python3 .agent/tools/rebase_links.py --inbound` in `tests/test_committed_settings.py`;
   - TC-G8 to TC-G12 in `tests/test_script_guards.py`;
   - the CLI path of `test_slot_links.py` set to `rebase_links.py`.
3. **Hashes.** Stage 2 ends with the audit record holding the SHA-256 of the patch, of
   `slot_links.py` and of `rebase_links_next.py`. Stage 3 checks all three before `git apply`.
   Stage 4 reads `slot_links.py` alongside the applied diff.

## 8. Test obligations

Git fixtures are temporary repositories. The test process sets `GIT_CONFIG_GLOBAL=os.devnull`,
`GIT_CONFIG_NOSYSTEM=1`, a fixed identity and `GIT_CEILING_DIRECTORIES` at the temporary root.
Every case is **base-fail**: the module, the option and the function do not exist at the base.

`.agent/tools/test_slot_links.py`. Every exit-2 case also asserts the stderr object of R7.4.

- TC-0 — the names of R1.7 and the fields of `InboundResult` exist. It passes on the stub of
  PLAN A1 and fails at the base.
- TC-1 — sub-task `task-NNN-01-x.md` with `[docs/PLAN.md](../PLAN.md)`, another document with a
  TASK link, the next task's `docs/TASK.md` present → `[plan-NNN](../plans/plan-NNN-slug.md)`; the
  other unchanged and `INBOUND`; exit 3; every link resolves. Fails when sub-tasks are not own.
- TC-2 — `--since`: a slot link on a line added after `<rev>` → `RETARGETED`; one on an older line
  of the same file → `INBOUND`. Fails when whole files count as own.
- TC-3 — `--since`: an untracked document with a slot link → `RETARGETED`.
- TC-4 — `--since`: a ledger record with a slot link added after `<rev>` → `INBOUND`, bytes kept.
- TC-5 — slot links in a parent archive and a plan archive → counted, not listed; a slot link in
  the next `docs/TASK.md` → not read. Fails when archives are listed.
- TC-6 — slot links in a fence and a code span of a sub-task → untouched, not listed.
- TC-7 — link text `docs/TASK.md`, `` `TASK.md` ``, `../PLAN.md` replaced; `TASK.md §3` kept;
  an image's alt text kept; nested brackets found.
- TC-8 — a `#fragment`, `<…>` brackets, a reference definition and an HTML `href` keep their form.
- TC-9 — operands: a missing archive, a sub-task as `--task`, a linked archive, a wrong shape, a
  `--plan` of another ID → exit 2, no file changed.
- TC-10 — `<rev>` starting with `-`, an unknown `<rev>`, a `<rev>` that is not an ancestor of
  `HEAD`, `--since` in walk mode → exit 2.
- TC-11 — an own link in a symbolic link → `SKIPPED`; in a file with a second hard link →
  `REFUSED`; neither file changed.
- TC-12 — `--dry-run` → no file changed; records equal to a real run's.
- TC-13 — a CRLF sub-task → rewritten, CRLF kept.
- TC-14 — only own links → exit 0.
- TC-15 — a PLAN link in a sub-task, no `--plan` → `INBOUND`.
- TC-16 — a sub-task of another ID → `INBOUND`.
- TC-17 — a file that does not decode as UTF-8 → `UNREADABLE`, exit 3.
- TC-18 — the archive removed between the write and the check → exit 1. Fails when the check is
  dropped.
- TC-19 — walk mode skips `.git`, `node_modules` and a directory holding `pyvenv.cfg`, and follows
  no directory link.
- TC-20 — `--json` prints the object of R7.4.
- TC-21 — git hardening. An external diff driver, a textconv driver, a clean filter and
  `core.fsmonitor` each write their own sentinel. Positive control: `git diff`, `git diff
  --no-ext-diff`, `git hash-object --path` and `git status` write all four. After a `--since` run,
  none is written. Fails when the module runs `git diff` or `git status`.
- TC-22 — inherited `GIT_DIR` and `GIT_INDEX_FILE` pointing elsewhere → records equal to a run
  without them, both completed.
- TC-23 — `repo_root` one directory below the top level, reached through a symbolic link to the
  repository → R3.2 attributes lines, and the write passes R5.2.
- TC-24 — a duplicated line, one copy added → only the added copy is own.

Added by stage-2 round 1 (`test_slot_links.py`):

- TC-26 — R5.2 guards, each refused with no write:
  - a parent directory replaced by a link to a directory outside;
  - the file replaced after the read;
  - the file changed in place after the read;
  - the file replaced by a FIFO after the read.
- TC-27 — the file replaced at the path between its `fsync` and the `lstat` → `REFUSED`, and the
  replacing text stays.
- TC-28 — `--dry-run` on a hard-linked sub-task → `REFUSED`, the same as a real run.
- TC-29 — overlapping edits → `REFUSED` `overlapping links`, the file unchanged.
- TC-30 — a write that fails after its first byte → `REFUSED` `partly written: …`, exit 1.
- TC-31 — a file name and a link target with a newline, an ANSI escape and U+202E → escaped in the
  text output; `--json` is ASCII; a record that the stream cannot encode prints with escapes.
- TC-32 — an unexpected exception in `main` → the stderr object, exit 1.
- TC-33 — `GIT_ALLOW_PROTOCOL=none` in the git environment; `core.worktree` naming another
  directory → exit 2.
- TC-34 — a file over 4 MiB → `UNREADABLE`; a file of more than 20000 lines under `--since` →
  `INBOUND` `not attributed: more than 20000 lines`.
- TC-35 — a ledger directory in another letter case under `--since` → `INBOUND`.
- TC-36 — `docs/tasks/` ignored by git → its own sub-task is still `RETARGETED`.
- TC-37 — an unreadable directory in walk mode → `UNREADABLE`.
- TC-38 — `--ta` for `--task` → exit 2.
- TC-39 — link text `<../TASK.md>` replaced; an escaped `\[` keeps its text; `_text_span` cases.
- TC-40 — an LF blob checked out as CRLF with one line added → only that line is own.
- TC-41 — `--since=-x` → the error names the leading `-`.
- TC-21 adds a smudge-filter sentinel and `git cat-file --filters` to its positive control.

Added by stage-2 round 2 (`test_slot_links.py`, `test_archive_protocol.py`):

- TC-42 — a table of alternating link rows, every row changed and one link row added → only the
  added row is own. Fails with `autojunk=True`.
- TC-43 — `docs/tasks/` unreadable in git mode → `UNREADABLE`, exit 3.
- TC-44 — a stdout that raises `BrokenPipeError` → the stderr object, exit 1.
- TC-45 — a directory and a FIFO named `task-*.md` in `docs/tasks/` → not read, no record.
- TC-46 — a file without the text `TASK.md` or `PLAN.md` is not masked.
- TC-34 adds an untracked file of more than 20000 lines.
- TC-25 adds an H1 naming Metadata above `## 0. Meta Information`, and the planning example's
  Base revision.

`test_archive_protocol.py`:

- TC-25 — `archive_task`, `archive_plan`, `retarget_inbound_slot_links` on one fixture with
  sub-tasks `01`, `05a` → both slot links of the sub-tasks name the archives. `base_revision` is
  read from an English row, from a non-English label, and from a row placed before the Slug; the
  slug stays the Slug.

`tests/test_script_guards.py`, stage 3:

- TC-G8 — `--inbound` with an own link in a file with a second hard link → that file and its
  other name unchanged, exit 3.
- TC-G9 — `--inbound` with an own link in a symbolic link to a file outside → exit 3, a `SKIPPED`
  record, the target unchanged.
- TC-G10 — `--inbound` rewrites a sub-task inside the working directory.
- TC-G11 — a copy of the tools in a temporary directory, with planted modules, each writing its
  own sentinel → `--inbound` exits 0 or 3, and no sentinel exists. The planted modules:
  - `__future__.py`, `re.py`, `typing.py`, `argparse.py`, `json.py`, `difflib.py` and
    `subprocess.py`;
  - `msvcrt.py` and `_winapi.py`, which the standard library lacks on POSIX;
  - a package for each of `slot_links`, `rebase_links`, `archive_move` and `task_id_tool`;
  - a junk extension module named `slot_links`.

  Fails when the script keeps `from __future__ import annotations`, moves its directory instead
  of removing it, or finds a sibling by a path search (stage-2 rounds 1 and 2).
- TC-G12 — the same copy with an unchecked-hash `.pyc` for `slot_links` in `__pycache__/` that
  writes a sentinel → the sentinel is absent, and no `.pyc` is written. Fails without the
  `sys.pycache_prefix` step.

<!-- contract:open-questions -->

## 9. Open Questions

None open. B1 of Mode A round 1 became D6, M3 became D7.

## 10. Decisions and registration text

### 10.1 Decisions

- D1, 2026-10-07, operator: own files are the task's sub-tasks and, with `--since`, what the task
  changed. Rejected: sub-tasks only — misses the 2 design-document links of task 033; an explicit
  list — the agent composes it.
- D2, 2026-10-07, agent: lines added since the base are own, not whole changed files (R3 Why).
- D3, 2026-10-07, agent: added lines are computed in Python from `git cat-file blob`. Rejected:
  `git diff -U0` — it runs diff drivers, textconv and clean filters, and its pathspecs are globs.
- D4, 2026-10-07, agent: ledger records are never rewritten (`known-issues-format` §8).
- D5, 2026-10-07, agent: a symbolic link is not read. Rejected: reading it — the target is often
  another file of the scan set, which doubles its records.
- D6, 2026-10-07, operator: Step 8 runs with no prompt through `rebase_links.py --inbound`, logic in
  `slot_links.py`, in the four stages. TASK 111 D13 holds. Rejected:
  - a new allow rule — a TIER 0 edit of `skill-safe-commands`;
  - a prompt on each run — it reverses D13;
  - a command in a code span — TC-S7 would not cover Step 8.
- D7, 2026-10-07, operator: the TASK template gains a Base revision row, and Step 2 reads it.
  Rejected: no template change — outside `/framework-upgrade` the base would be unknown.
- D8, 2026-10-08, agent: `rebase_links.py` removes its directory from `sys.path`, as
  `archive_move.py` does, and loads its siblings by explicit path (R1.2). Rejected: moving the
  directory to the end, the round-1 fix. A name the standard library lacks still reaches it
  (`msvcrt`), and a path search prefers a planted package to a sibling (stage-2 round 2).
- D10, 2026-10-08, operator: stage-2 round 1 fixes the cheap LOW, INFO and MINOR findings now.
  Work-items: the file mode writing through a linked parent (security L10, a TASK 112 R4.1
  choice), the `sys.path` move of the other allow-listed scripts, the directory-swap race of R5.2.
- D11, 2026-10-08, operator: the security audit stays INCOMPLETE after its re-run, on the external
  layer (scanners not installed); the run continues with the gap recorded. TASK 115 adds no
  dependency.
- D12, 2026-10-08, agent: the read limit is 4 MiB and the attribution limit 20000 lines. The largest
  `.md` measured is 575294 bytes (`CHANGELOG.ru.md`); crafted input made `_mask` take 10.6 s at 725
  KB. Rejected: 32 MiB — about 50 minutes for a crafted file.
- D13, 2026-10-08, agent: a file whose text holds neither `TASK.md` nor `PLAN.md` is not masked;
  no slot link can end in another name. Rejected: a wall-clock budget. A single `_mask` call would
  still run to its end before any check.
- D14, 2026-10-08, agent: no shim for Python 3.9 (stage-2 round 2, review item 14). The floor is
  3.11 (TASK 109), and the operator's direction rules out 3.9 shims.
- D9, 2026-10-08, agent: the two commands of §10.2 are one line each (Mode B round 1, n13).
  Rejected: line continuations — `skill-safe-commands` calls a command with one not safe, so a
  vendor that applies its patterns asks for approval.

### 10.2 Fenced blocks of `skill-archive-task` (stage 3)

Step 8, after its prose:

```bash
python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/{filename} --plan docs/plans/{plan_filename} --since {base_revision}
```

Example Flow, the new Step 8 item between the Step 7 item and the new TASK, indented as its list
item:

```bash
python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/task-{OLD_ID}-{old-slug}.md --plan docs/plans/plan-{OLD_ID}-{old-slug}.md --since {old-base}
```

### 10.3 `ARCHIVE_FENCES` (stage 3)

```python
ARCHIVE_FENCES = ("", "", "bash", "python", "", "bash", "bash", "", "", "", "bash", "bash", "",
                  "bash", "bash", "bash", "bash", "bash", "bash")
```

The base tuple holds 17 entries. Step 8's block is entry 14, after 7.7's validation block; the
Example Flow block is entry 19.

## 11. Scope

In scope: R1–R12 and §7.

Out of scope:

- the 11 existing slot links of this repository and the 31 of n8n-lazy-loading-skills — the
  operator re-targets them from a report; the 3 in parent archives stay as history;
- slot links in files other than `*.md`;
- a keep-live marker for a link meant to name the live slot.

## 12. Risks

- A file renamed since the base has no base text → its earlier slot links are re-targeted to this
  task (detected by the report, which lists every rewrite).
- Commits after the base by other work, such as a merged branch, count as the task's lines
  (detected by the report).
- Changes left uncommitted when the task started count as the task's lines; only
  `/framework-upgrade` starts from a clean tree (detected by the report).
- An untracked file the task did not write counts as the task's (detected by the report).
- A file with a smudge filter or `ident` differs from its clean blob → its lines read as added
  (detected by the report).
- A link written to name the live slot, on a task line, is frozen to this archive (detected by the
  report; the operator reverts it).
- `SequenceMatcher` can align a reflowed paragraph differently from git (detected by the report).
- A sub-task whose H1 names no task of its ID reads by its name. With a letter suffix it reads as
  a parent archive → its links are counted as archived (TASK 114 fallback; detected by the count).
- A crash during the in-place write leaves a mixed file, as `rebase_file()` can. A tracked file is
  restored by `git diff`; an untracked one has only the report (detected by the report).
- A directory swapped twice between the real-path check of the parent and the open lets the
  write reach the file that was read, outside the root. The inode and bytes checks bind the write
  to that file (work-item, D10).
- A reference definition on the first line of a file that starts with a BOM is not seen, as in
  `rebase_links.py` (detected by nothing; the slot link stays as written).
- A crafted file under 4 MiB that holds the text `TASK.md` can still make `_mask` take minutes; the
  harness timeout then stops Step 8 before any write, and Step 8 STOPs (detected by the timeout).
- A file renamed away between its write and the `lstat` keeps the new bytes under its new name and
  is recorded `REFUSED` (detected by the report).
- R1.2 covers the script's own directory. A `PYTHONPATH` entry can still answer an import with a
  planted module, such as a `json.py` in the project root under `PYTHONPATH=.`. Every Python tool
  the agent runs shares that exposure (stage-2 round 3, code review item 8; security round 3).

## 13. Verification

1. `cd .agent/tools && python3 -m pytest -q` passes.
2. `PYTHONPATH=. python3 tests/run_tests.py` passes, before stage 3 and after it.
3. The CI pytest list of `framework-gates.yml` passes.
4. `validate_skill.py` exits 0 and `analyze_gaps.py` adds no gap for every edited skill;
   `validate_skills.py --root . --quiet` and `check_prompt_references.py --root .` exit 0.
5. `rebase_links.py --inbound --task docs/tasks/task-114-subtask-classified-by-h1.md --dry-run`
   after stage 3 lists 8 `INBOUND` records (7 elsewhere, 1 in `task-061-02`), counts 3 archived
   slot links and exits 3. The tree fingerprint before and after the run is equal. The counts were
   measured at `fc53476`: a further record is named in the audit, and only a write or a
   `RETARGETED` record fails this check.
6. A code review and a security audit in stage 2, and again in stage 4.
7. `check_positional_refs.py --targets-changed --fix` (§4.5).
