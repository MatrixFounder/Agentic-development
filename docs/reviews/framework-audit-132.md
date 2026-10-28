# Framework Audit 132 — The inbound walk and the file mode of `rebase_links.py` end without a traceback on a path that names a device

- **Task:** 132 `arc-14-walk-relpath`. It archives to `docs/tasks/task-132-arc-14-walk-relpath.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator`.
- **Date:** 2026-10-28. **Base revision:** `6aedb2203c26e6f6c745a362f950008e63e5a291`, clean tree
  at start (the record of ARC-14, committed by the operator as `6aedb22` after TASK 131's
  `30616d2`).
- **Source:** ARC-14, CI run 40637795256, and the operator's answer of 2026-10-28 (TASK D1).

## 0. Emergency Bypass

None. `skill-archive-task` is a TIER 1 skill; the change edits two scripts it runs and leaves its
text as it is (TASK R5.3). It touches no TIER 0 skill and removes no load of one.

## Archive (§1)

TASK 131 and PLAN 131 archived under ID 131:
- `task_id_tool.py "archive-chain-windows" --proposed-id "131" --no-correction`: `generated`,
  `task-131-archive-chain-windows.md`;
- both moves `"ok": true`, method `link`;
- Step 5.5: `0 rewritten / 0 needing review`, exit 0;
- Step 7.6.5: one `SLOT_RESOLVED`, exit 0;
- Step 8 with `--since 6f3d65c8d085c48ae36e2e63a7f47fc9ac2b8dce`: exit 3. It lists the two
  `INBOUND` records of old changelog entries, `CHANGELOG.md:3670@6aedb22` and
  `CHANGELOG.ru.md:3700@6aedb22`, which carry no reason and stay. Step 8 rewrote no file.

## Research (§1)

The facts of TASK §8 come from the log of CI run 40637795256, from the source of `ntpath.relpath`,
and from an emulation in a temporary root under the session's scratchpad. The retro claim
`framework-upgrade-task-132-arc-14-walk-relpath` was taken at the start of the run, and the base was
recorded in the session state before §1. The operator chose the scope before the TASK was written
(TASK D1).

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

The reviewer, a `task-reviewer` agent with no shell, read the TASK at SHA-256 `bd6d4ee6ce38…` and
wrote nothing. The fingerprint of the tree was `3721b6123380` before and after the round. No
failure condition of the verificator's §4 applies, and root integrity holds. The four pairs of R6.1
are the files of the change that an allow rule reaches. The reviewer read the three settings files
and quoted no rule. Its findings:
- M1: `--to nul` passes `_leaves_tree`, and each rewrite then calls `relpath` from a start that
  names a device. The orchestrator reproduced it with the stand-in: `_main` raises `ValueError`
  for `--to nul` and `--to docs/nul`;
- M2: TC-D4 passes at the base, and no test pins that the walk calls no `relpath`;
- M3: on Windows a plain path makes no entry `nul`, so TC-D1 to TC-D3 cannot run there as written;
- m1: on Windows `relpath` drops the dots and spaces that end a name, and the text keeps them;
- m2: `slot_links._write_file` also calls `_under_git`;
- m3: TC-D6 cannot be red at the base on macOS;
- m4: §1 claimed a measurement of the operand that §8 lacked. The orchestrator measured it: the
  operand `docs/tasks/nul` raises `ValueError` under the stand-in;
- m5: §1 item 3 cited TASK 131 R3 for a claim of its title;
- N1: the site of §1 item 2 is an inference;
- N2: TC-D6 on 3.11 rests on reading;
- N3: no test asserted exit 3 for a link to a device;
- N4: A6 and A7 named neither R5.3 nor R6.5.

Before the task, LOW: on Windows a walk entry under a directory whose name ends in a dot is read and
written at the normalised path. TASK §9 names it.

TASK revision 2 applies M1 to M3, m1 to m5, N1, N3 and N4 (TASK D8 to D10).

### Round 2 — TASK revision 2: PASS

The same reviewer read the TASK at SHA-256 `4f05329ce991…` and wrote nothing. The fingerprint of
the tree was `e260b98b82a8` before and after the round. It found each fix of round 1 in place, no
failure condition of §4, and no contradiction in the TASK as a whole. Its findings, none blocking:
- m1: `relpath` on Windows also drops the single dot that ends an inner part of a path, so R1.3
  claimed the base's path for `x./y.md`;
- m2: `archive_protocol._rebase_moved_document` calls `rebase_file` without `_main`. Its `to_dir`
  is fixed, and it catches `ValueError`;
- N1: one sentence of §1 item 2 still stated the inference as fact;
- N2: the check of R2.4 belongs in `_main`: TC-W18 binds the `os` of `_leaves_tree` to a namespace
  with no `getcwd`;
- N3: the first sentence of R2.5 stood at the limit of 35 words.

TASK revision 3 applies m1, m2 and N1 to N3, with no further round (TASK D11). It also adds to
TC-D2 the case of the root, which R1.1 states.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

The reviewer, a `plan-reviewer` agent with no shell, read the PLAN at SHA-256 `5e7d2e7d354d…` and
wrote nothing. The fingerprint of the tree was `cdf131e53939` before and after the round. No
failure condition of the verificator's §4 applies. The reviewer read the settings files and quoted
no rule. Its findings:
- M1: no mutation names TC-D6, and F1 had no rule for a mutation that only a test on Windows kills;
- M2: J3 named exit 2 for `--to nul`, which on macOS exits 0: `posixpath.relpath` raises no
  `ValueError` for these paths. A correct change would then have taken the Failure path;
- m1: A2 named none of the rules that can reach any code, and the PLAN did not state why the check
  of what runs comes at J3 only;
- m2: K1 declared no retro record;
- m3: no path for an `INCOMPLETE` audit of stage 4 alone;
- m4: no run checked the stub of `_relative`;
- m5: no single helper for the text of R1.1, so the edits of mutations 4 and 5 could occur three
  times;
- m6: the last bullet of H2 named no stand-in and no exit code per run;
- m7: no step checked R2.5, R2.6, R3.2 or the second sentence of TASK A3;
- m8: two referents named steps of PLAN 131 as TASK 131, and the cluster table disagreed with the
  coverage;
- N1 to N7, notes:
  - no `W` row for the `os.sep` clause, and E1 did not describe `wt132.sh gen`;
  - the read of each added call against Python 3.11;
  - the resolution blockquote of a `fixed` record, and the register;
  - two postconditions of PLAN 131, and where this review is kept.

The orchestrator ran `plan_gantt.py --check`: the chart is current. PLAN revision 2 applies M1, M2,
m1 to m8 and N1 to N7. N7 needs no change: this record holds the review.

### Round 2 — PLAN revision 2: PASS

The same reviewer read the PLAN at SHA-256 `1ab64d75316a…` and wrote nothing. The fingerprint of
the tree was `75b3f1ad4ef9` before and after the round. The orchestrator supplied the outputs of
`plan_gantt.py --check`, the register scan and the resolver. The reviewer found each fix of round 1
in place, each item of the verificator's checklist passed, and no failure condition of §4. Its notes,
none blocking:
- N1: the three rules of A2 can reach a staged copy, and `rebase_links.py` loads three siblings;
- N2: the rollback point named three trees of `wt132.sh` of five;
- N3: "raises for no path" was ambiguous: `posixpath.relpath` raises for an empty path;
- N4: the dev tree of C1 step 1 also fails TC-D1 to TC-D4;
- N5: a skip added under a condition of Windows shows only in the source;
- N6: J3 abbreviated the commands of the rule.

PLAN revision 3 applies N1 to N6, with no further round. N5 takes the form of a `git diff` of each
staged test module in B2.

## Execution (§3)

### A1, A2 — the base check and the settings

- A1: `HEAD` equals the base. Each edited path is tracked, each created path is neither ignored nor
  present, and each path passes the checks of form. `git worktree list` names the main worktree
  and two prunable registrations of earlier sessions, a finding before the task.
- A2: `rules_check.py compare` with `rules_132.json`: the local and the user settings are unchanged
  since §2.2. The local rule `ca2c33383ded` runs the modules of `tests/`, among them
  `tests/test_script_guards.py`, and through it both scripts. No rule of either file names
  `rebase_links.py` or `slot_links.py`. Three rules can reach any code, each a finding before the
  task: the local rule `881e39b164a5`, and the user rules `89216e2cf097` and `aa8ebef8166f`.

### B1, B2 — the tests first

`cp -p` made `tests/staged_script_guards.py` and `.agent/tools/staged_test_slot_links.py`. They
gained TC-D1 to TC-D4 and TC-D5 and TC-D6, with the stand-in of TASK R3.1 as one helper per
module. `git diff` against each base module shows additions only, and one line of the docstring of
`tests/test_script_guards.py` that the new bullet continues. In the red tree, under the guard:
TC-D1 to TC-D4 and the three tests of TC-D5 failed, with both subtests of the last; TC-D6 skipped;
130 tests of the base passed.

### C1, C2 — the staged scripts

- C1 step 1, the stub: `_relative` returned `os.path.relpath` and caught nothing, and the calls of
  the sites of R2.2 and R2.3 went through it. R2.4 holds no call at the base, so the stub step
  added none. In a dev tree, under the guard: 187 tests of the base passed, and TC-D1 to TC-D5
  failed; `staged_slot_links.py` was still the base.
- C1 step 2: the catch of R2.1, and the checks of R2.2 to R2.4, the last in `_main` after
  `_leaves_tree`.
- C1 step 3, each call of `os.path.relpath` in the staged `rebase_links.py`, by its two arguments
  (TASK R2.5):
  - `identity` and `new_base`: a slot archive, and `--to` that R2.4 checked;
  - `identity` and `root`;
  - `denote_old` and `new_base`: checked by R2.2 and R2.4;
  - `absolute` and `cwd` in `_under_git`: checked by R2.3 before the call;
  - `_relative(absolute, cwd)` of the check of `docs/`: never `None` after R2.3.

  The callers of TASK R2.6 at the base: `slot_links.py:434@6aedb22` `if _rl._under_git(rel, root):`
  and `archive_protocol.py:324@6aedb22` `except (OSError, ValueError):`, whose `rebase_file` takes
  the `to_dir` of the tasks or the plans directory.
- C2: `_walk` derives the text of R1.1 in one nested helper, `relative`, which the three sites
  call. In a dev tree, under the guard: the two staged modules, 140 passed and 7 skipped. In a new
  dev tree, the step of TASK 131 R7.1: 395 passed and 11 skipped, against 388 and 10 at the base.
- Each call that the change adds exists in Python 3.11: `os.path.join`, `os.getcwd`, slicing and
  `str.replace`. Each changed file parses with `feature_version=(3, 11)`.

### D1 — the changelogs and the record

v3.50.1 in `CHANGELOG.md` and `CHANGELOG.ru.md`. The record of ARC-14 takes `status: fixed`,
`resolved_at`, `resolved_by: TASK 132` and the resolution blockquote, and its index line takes the
status and the summary. `regcheck.py`: 0 warn on each.

### E1 — the patch

`wt132.sh gen` wrote `docs/reviews/framework-audit-132-stage3.diff`: four files, no other path,
no mode line and no staged copy. `git apply --check` passes on the live tree, and `git worktree
list` names no worktree of the run.

The patch: SHA-256 `567e746a3689ea23e9f0f0bb958307cca458d790c0b905692245e90643c71184`. Each file
that it edits, before the edit and after it, the second value the SHA-256 of its staged copy; each
file and each copy has the mode `644`:

| File | Before | After |
| :--- | :--- | :--- |
| `.agent/tools/rebase_links.py` | `fb1f9bdc3c10b5e2…` | `ca63a5d21117ee70…` |
| `.agent/tools/slot_links.py` | `2bcd61a06aa1178a…` | `8f26808fe90c98b7…` |
| `.agent/tools/test_slot_links.py` | `be5c85d7fc46bd2b…` | `7640d1a36c59755d…` |
| `tests/test_script_guards.py` | `19917f9ed80d7f0d…` | `a998bfa903311658…` |

### H1, H2 — the live and the patched tree

Each run below ran under the guard; `.agent/sessions/` was unchanged each time.
- H1, the live tree:
  - `gates.py`, 22 of 22 steps pass. The step of TASK 131 R7.1 runs the base: 388 passed and 10
    skipped;
  - the four final files and the texts of TASK R5.3 equal the base;
  - `list_tests131.py`: no listing names a staged file, and each exits as at PLAN 131 H1, with the
    21 errors from `.agent/`;
  - `regcheck.py`: 0 warn on each changed document. `bytescan.py`: each of the 14 paths of
    `git status` is clean, and each is declared.
- H2, the patched tree:
  - `gates.py`, 22 of 22 steps pass. The step of TASK 131 R7.1: 395 passed and 11 skipped, TC-D6
    among the skipped. The tooling step: 610 passed;
  - each final file equals its staged copy;
  - the file mode on the archive of TASK 131 exits 0, and the inbound mode exits 3 with the two
    records of §1, with no stand-in and with the platform stand-ins of TASK 131 R6.2;
  - under the stand-in of TASK R3.1, in a temporary root, since removed: a link to `nul` exits 3
    with `[ESCAPES_ROOT]`, and the document keeps its bytes. The operand `docs/tasks/nul`,
    `--to nul` and `--from nul` each exit 2. The walk, with `os.lstat` also failing for `nul`,
    exits 3 with an `UNREADABLE` record. No run ends in a traceback;
  - the source of TC-W16 equals the base, and the live and the patched tree skip the same 6 tests
    of the base.

### F1 — the mutations

`mutations132.json` holds the 12 mutations of the PLAN, each edit an exact text that occurs once.
In a new patched tree: 11 killed. Mutation 12, marked `W`, is not killed on macOS: it drops the
`/` of the text of R1.1, which only Windows reads, and TC-D4 kills it there after the push (TASK
A5). The fingerprint of the live tree, `86a700326bb2`, is the same before and after.

## Stage 2 (PLAN I1)

### Round 1, at the fingerprint `2fe2100f1a27`: code review APPROVED, security audit PASS

Both reviewers read their briefs, computed `2fe2100f1a27` at their start and at their end, and ran
the new code in the patched tree `wt-132/i1`, which the orchestrator removed after the round. The
listing of the guard was unchanged. The security auditor left `scratchpad/sec132-i1/`: its scan
summary and five probe scripts of its own. No file there hashes as a file of the repository, and
the orchestrator removed it.

The `code-reviewer`: APPROVED. It confirmed each hash of E1, R1 to R6 against the staged code, and
the step of TASK 131 R7.1, 395 passed and 11 skipped. The walk of the base and the staged walk gave
the same files and records over a tree of odd names, skipped directories, links, and directories
that cannot be read or listed. The staged walk called `relpath` 0 times, and the base 33. Its
findings, each LOW:
- no test pins that R2.4 refuses before any operand is read. A mutation that moves the check into
  `_file_mode` survived the tests of TC-D5 and TC-D6;
- the stand-in raises for `nul` alone, and with a fixed message;
- the place of the stand-in's helper among the constants, and a second marker of the condition of
  `posix_premise`;
- the module docstring of `rebase_links.py` and the docstring of `_refuse_operand` name no device;
- on Windows an operand such as `docs/tasks/nul:x` may meet R2.3 before the check of TASK 131
  R5.5.

The `security-auditor`: PASS. Its scan ran, `scan_status: findings`, with none in the change but
false positives of a path pattern and of `assert`. On POSIX the patched file mode equals the base
over 924 combinations of operands, `--from`, `--to` and options, and the walk equals the base over
odd names and roots. Under a stand-in for each device name of Windows, no run raises, and no file
but the operand is written. It found no refusal of the base weakened and no new window of a race.
Its findings, each LOW:
- C1: on Windows, a record of the walk names `x./y.md` where the read opens `x\y.md`;
- C2: a device-named `.md` file of the walk is probed before it is refused;
- C3: `relative` slices with no check of the prefix;
- C4: ARC-14 is `fixed` before the Windows jobs confirm the fix.

Before the task, each LOW:
- a junction named after a device on Python 3.11 for Windows, which the walk follows;
- the probe of `denote_new`, and the control characters of the text report;
- the names that end in a space. The scan's findings at CRITICAL and HIGH lie outside the change.

Stage 2 closes with this round (TASK D12). TASK revision 4 names each LOW finding that stays, and
TASK §9 names the findings before the task.

## §4.5, stage 3 and stage 4 (PLAN J)

### J1 — §4.5 and the settings

- `check_positional_refs.py --targets-changed`: 0 errors, 13 warnings across 472 references in 15
  documents. With `--fix`: the same counts, and `git status` and the diff unchanged, so no repair
  touched a file.
- `rules_check.py compare` against the reading of §2.2: the local and the user settings files are
  unchanged, with no new rule, exit 0.

### J2 — stage 3

Step 1: the patch hashes to `567e746a3689ea23e9f0f0bb958307cca458d790c0b905692245e90643c71184`, and each staged copy to the value of
round 1. Step 3, before the apply: each file that the patch edits hashes to its value before the
edit in E1. Each file that the patch edits, before the edit, and its staged copy, with the SHA-256
and the mode of each:

| File | SHA-256 before | Mode | Staged copy | SHA-256 | Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `.agent/tools/rebase_links.py` | `fb1f9bdc3c10b5e263f8ea5a60f9445aa73a40ce3d96ebbc276b4eca4946c925` | `644` | `.agent/tools/staged_rebase_links.py` | `ca63a5d21117ee70768df346d662783ef47dcddfd0f67cbfdd66d5107e2f08f3` | `644` |
| `.agent/tools/slot_links.py` | `2bcd61a06aa1178ae2ee6f79c8e93397099bcc6acefea8b204eae527fd18a146` | `644` | `.agent/tools/staged_slot_links.py` | `8f26808fe90c98b76c2827a879325e519e54faa78cb31589bb8edb25c90cc332` | `644` |
| `.agent/tools/test_slot_links.py` | `be5c85d7fc46bd2bc087a51b94df90e68f05c83af2f7ae930c604c0526cae88e` | `644` | `.agent/tools/staged_test_slot_links.py` | `7640d1a36c59755d3c0fe3b62996f880e7b805c0fa00dfa0e97f7c502064b593` | `644` |
| `tests/test_script_guards.py` | `19917f9ed80d7f0d13723c60e8a1ca5755867e3298567848c7011ada0c2a1757` | `644` | `tests/staged_script_guards.py` | `a998bfa903311658b067a45db48484ef2817c01c627fae00bfcade1d8b1e057d` | `644` |

The patch:

~~~~diff
diff --git a/.agent/tools/rebase_links.py b/.agent/tools/rebase_links.py
index 35393f2..4101da5 100644
--- a/.agent/tools/rebase_links.py
+++ b/.agent/tools/rebase_links.py
@@ -272,6 +272,11 @@ def rebase_document_links(text: str, from_dir: str, to_dir: str,
             records.append(LinkRecord(line, authored, denote_old,
                                       "ESCAPES_ROOT", authored))
             continue
+        rel = _relative(denote_old, root)
+        if rel is None:                             # TASK 132 R2.2: a device, as another drive
+            records.append(LinkRecord(line, authored, denote_old,
+                                      "ESCAPES_ROOT", authored))
+            continue
 
         # A MUTABLE SLOT is checked first, and without touching the filesystem.
         #
@@ -297,15 +302,14 @@ def rebase_document_links(text: str, from_dir: str, to_dir: str,
 
         # A known slot with no identity supplied is NEVER rewritten. Rebasing
         # the path here is what converts "dead" into "silently wrong".
-        if os.path.relpath(denote_old, root) in known_slots:
-            records.append(LinkRecord(line, authored,
-                                      os.path.relpath(denote_old, root).replace(os.sep, "/"),
+        if rel in known_slots:
+            records.append(LinkRecord(line, authored, rel.replace(os.sep, "/"),
                                       "UNMAPPED_SLOT", authored))
             continue
 
         resolved_old = os.path.exists(denote_old)
         resolved_new = os.path.exists(denote_new)
-        rel_old = os.path.relpath(denote_old, root).replace(os.sep, "/")  # TASK 131 R5.3
+        rel_old = rel.replace(os.sep, "/")  # TASK 131 R5.3
 
         if not resolved_old:
             action = "ACCIDENTAL_RESOLVE" if resolved_new else "PRE_BROKEN"
@@ -502,7 +506,8 @@ def _refuse_operand(path):
     """
     cwd = os.getcwd()
     absolute = os.path.normpath(os.path.join(cwd, path))
-    if not _inside(absolute, cwd) or absolute == cwd:
+    if (not _inside(absolute, cwd) or absolute == cwd
+            or _relative(absolute, cwd) is None):   # TASK 132 R2.3: a device
         return "lies outside the working directory"
     if _names_stream(path):
         return "names an alternate stream of a file"
@@ -516,7 +521,7 @@ def _refuse_operand(path):
     directory = os.path.realpath(os.path.dirname(os.path.join(cwd, path)))
     if not _inside(directory, real_cwd):
         return "its directory resolves outside the working directory"
-    if os.path.relpath(absolute, cwd).split(os.sep)[0] != "docs":
+    if _relative(absolute, cwd).split(os.sep)[0] != "docs":
         return "does not lie under docs/"
     if not path.endswith(".md"):
         return "is not a markdown file"
@@ -579,6 +584,19 @@ def _inside(path, root):
         return False
 
 
+def _relative(path, start):
+    """`os.path.relpath(path, start)`, or None where it raises `ValueError` (TASK 132 R2.1).
+
+    On Windows `relpath` resolves both paths first, and a last part that names a device, such as
+    `nul`, resolves to `\\\\.\\nul`, on another drive (ARC-14). Each caller counts such a path
+    as one outside, as a `ValueError` of `commonpath` counts (TASK 131 R5.1).
+    """
+    try:
+        return os.path.relpath(path, start)
+    except ValueError:
+        return None
+
+
 def _leaves_tree(value):
     """True when `--from` or `--to` leaves the working directory (TASK 116 R8.6, TASK 131 R5.2).
 
@@ -777,6 +795,7 @@ def _main(argv=None):
 
     # TASK 116 R8.6: a rewritten link is built from these paths, so each stays in the tree.
     # TASK 131 R12: a UNC path is refused before any call reaches the file system.
+    # TASK 132 R2.4: so is a `--from` or `--to` that names a device, before any operand is read.
     if _unc(args.repo_root):
         problem = "--repo-root is a UNC or device path"
     elif os.path.realpath(args.repo_root) != os.path.realpath(os.getcwd()):
@@ -784,7 +803,9 @@ def _main(argv=None):
     else:
         problem = next((f"{name} does not lie inside the working directory"
                         for name, value in (("--from", args.from_dir), ("--to", args.to_dir))
-                        if _leaves_tree(value)), None)
+                        if _leaves_tree(value)
+                        or _relative(os.path.join(os.getcwd(), value), os.getcwd()) is None),
+                       None)
     if problem:
         _emit(sys.stderr, json.dumps({"ok": False, "error": problem}))
         return 2
diff --git a/.agent/tools/slot_links.py b/.agent/tools/slot_links.py
index a0e9e37..4e90ab7 100644
--- a/.agent/tools/slot_links.py
+++ b/.agent/tools/slot_links.py
@@ -166,9 +166,21 @@ def _ls_files(root):
 
 
 def _walk(root, unreadable):
-    """Every file under `root`, repo-relative; a directory it cannot read goes to `unreadable`."""
+    """Every file under `root`, repo-relative; a directory it cannot read goes to `unreadable`.
+
+    Each path is read from its text after `root` (TASK 132 R1.1): `os.walk` joins each path onto
+    `root`, and so does each error that it passes to `onerror`. On Windows `os.path.relpath`
+    resolves a last part that names a device, such as `nul`, to `\\\\.\\nul`, and raises
+    `ValueError` (ARC-14).
+    """
+    head = os.path.join(root, "")
+
+    def relative(path):
+        """`path`, which is `root` or a path joined onto it, relative to `root`, with `/`."""
+        return "." if path == root else path[len(head):].replace(os.sep, "/")
+
     def failed(exc):
-        rel = os.path.relpath(exc.filename or root, root).replace(os.sep, "/")
+        rel = relative(exc.filename or root)
         unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "", exc.strerror or str(exc)))
 
     def entered(dirpath, name):
@@ -178,8 +190,7 @@ def _walk(root, unreadable):
         try:
             return not _is_link(os.lstat(path))
         except OSError as exc:
-            rel = os.path.relpath(path, root).replace(os.sep, "/")
-            unreadable.append(InboundRecord(rel, None, "UNREADABLE", "", "",
+            unreadable.append(InboundRecord(relative(path), None, "UNREADABLE", "", "",
                                             exc.strerror or str(exc)))
             return False
 
@@ -189,8 +200,7 @@ def _walk(root, unreadable):
                              and entered(dirpath, d)
                              and not os.path.isfile(os.path.join(dirpath, d, "pyvenv.cfg")))
         for name in filenames:
-            rel = os.path.relpath(os.path.join(dirpath, name), root)
-            found.append(rel.replace(os.sep, "/"))
+            found.append(relative(os.path.join(dirpath, name)))
     return sorted(found)
 
 
diff --git a/.agent/tools/test_slot_links.py b/.agent/tools/test_slot_links.py
index 24af90e..b926c81 100644
--- a/.agent/tools/test_slot_links.py
+++ b/.agent/tools/test_slot_links.py
@@ -18,6 +18,9 @@ set for the test process so that the module's own git calls read no operator con
 TC-W13, TC-W17, TC-W19, TC-W20 and TC-W24 (TASK 131) pin the inbound mode on a platform without
 `O_NOFOLLOW`, Windows among them. A test that makes a symbolic link or a FIFO skips where the
 platform cannot, and a test whose premise is a behaviour of POSIX skips on Windows (TASK 131 R6.5).
+TC-D1 to TC-D4 (TASK 132) pin the paths of the walk, read as text: on Windows `os.path.relpath`
+raises for a path that names a device, such as `nul` (ARC-14). TC-D1 to TC-D3 skip on Windows,
+where a plain path names that device.
 """
 
 import contextlib
@@ -1139,3 +1142,88 @@ def test_w41_a_crlf_subtask_with_a_fence(project):
                                     b"[" + label + b"](task-033-admission-core-v1.md)")
     assert path.read_bytes() == expected
 
+
+# --- TASK 132: the walk reads each path as text (ARC-14) ------------------------------------------
+
+NOT_ON_WINDOWS = pytest.mark.skipif(
+    os.name == "nt", reason="a plain path names the device nul on Windows (TASK 132 R3.3)")
+
+
+def device_relpath(always=False):
+    """TASK 132 R3.1: `os.path.relpath` as Windows runs it for a path that names a device.
+
+    It raises the `ValueError` of `ntpath.relpath` when the last part of its path or of its start
+    is `nul`, or on every call when `always` is true. It calls the real function otherwise.
+    """
+    real = os.path.relpath
+
+    def relpath(path, start=os.curdir):
+        if always or any(os.path.basename(os.path.normpath(part)) == "nul"
+                         for part in (path, start)):
+            raise ValueError("path is on mount '\\\\.\\nul', start on mount 'C:'")
+        return real(path, start)
+    return mock.patch("os.path.relpath", side_effect=relpath)
+
+
+@NOT_ON_WINDOWS
+def test_d1_a_directory_nul_whose_lstat_fails(project):
+    # base-fail: the record of the failed `os.lstat` calls `relpath`, which raises (ARC-14).
+    write(project, "nul/x.md", "[x](../docs/TASK.md)\n")
+    real_lstat = os.lstat
+
+    def lstat(path, *args, **kwargs):
+        if os.path.basename(os.fspath(path)) == "nul":
+            raise OSError(errno.EINVAL, "Invalid argument")
+        return real_lstat(path, *args, **kwargs)
+    unreadable = []
+    with device_relpath(), mock.patch("os.lstat", side_effect=lstat):
+        found = slot_links._walk(str(project), unreadable)
+    assert TASK in found and "nul/x.md" not in found
+    assert [(r.file, r.action) for r in unreadable] == [("nul", "UNREADABLE")]
+
+
+@NOT_ON_WINDOWS
+def test_d2_a_directory_nul_whose_scandir_fails(project):
+    # base-fail: the record of the error of `os.walk` calls `relpath`, which raises (ARC-14).
+    write(project, "nul/x.md", "[x](../docs/TASK.md)\n")
+    real_scandir, failing = os.scandir, {str(project / "nul")}
+
+    def scandir(path=".", *args, **kwargs):
+        if os.fspath(path) in failing:
+            raise PermissionError(errno.EACCES, "Permission denied", os.fspath(path))
+        return real_scandir(path, *args, **kwargs)
+    unreadable = []
+    with device_relpath(), mock.patch("os.scandir", side_effect=scandir):
+        found = slot_links._walk(str(project), unreadable)
+    assert TASK in found and "nul/x.md" not in found
+    assert [(r.file, r.action) for r in unreadable] == [("nul", "UNREADABLE")]
+    # TASK 132 R1.1: the root itself is `.`.
+    failing.add(str(project))
+    unreadable.clear()
+    with mock.patch("os.scandir", side_effect=scandir):
+        assert slot_links._walk(str(project), unreadable) == []
+    assert [(r.file, r.action) for r in unreadable] == [(".", "UNREADABLE")]
+
+
+@NOT_ON_WINDOWS
+def test_d3_a_file_named_nul_is_listed(project):
+    # base-fail: the list of files calls `relpath`, which raises for `nul` (ARC-14).
+    write(project, "docs/nul", "x\n")
+    unreadable = []
+    with device_relpath():
+        found = slot_links._walk(str(project), unreadable)
+    assert "docs/nul" in found and TASK in found
+    assert unreadable == []
+
+
+def test_d4_the_walk_calls_no_relpath(project):
+    # base-fail: the base derives each path with `relpath`.
+    write(project, "docs/a/b/c.md", "c\n")
+    write(project, "notes/d.txt", "d\n")
+    root = str(project)
+    expected = sorted(os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
+                      for dirpath, _dirnames, filenames in os.walk(root) for name in filenames)
+    unreadable = []
+    with device_relpath(always=True):
+        assert slot_links._walk(root, unreadable) == expected
+    assert unreadable == []
diff --git a/tests/test_script_guards.py b/tests/test_script_guards.py
index 2450770..e8efb11 100644
--- a/tests/test_script_guards.py
+++ b/tests/test_script_guards.py
@@ -32,7 +32,9 @@ skill directory at any `--path` or path-shaped name. This file pins:
   and after the open, refuses a junction, keeps every byte, writes any text in any stream
   encoding, refuses an operand that is not UTF-8, finds no `.pyc` under a relative null device,
   treats paths on two drives as outside, and keeps its own helpers (``TC-W11`` to ``TC-W18``,
-  ``TC-W24``, ``TC-W26``, ``TC-W27``, TASK 131).
+  ``TC-W24``, ``TC-W26``, ``TC-W27``, TASK 131);
+* a link, an operand, `--from` or `--to` that names a device, such as `nul`, ends in a record or
+  a refusal, not in a traceback (``TC-D5``, ``TC-D6``, TASK 132, ARC-14).
 
 A test that makes a symbolic link skips where this process cannot make one, and a test whose
 premise is a behaviour of POSIX skips on Windows (TASK 131 R6.5, D22).
@@ -154,6 +156,21 @@ def _can_symlink():
 
 NEEDS_SYMLINK = unittest.skipUnless(_can_symlink(), "this process cannot make a symbolic link")
 WINDOWS_ONLY = unittest.skipUnless(os.name == "nt", "a behaviour of Windows")
+
+
+def _device_relpath():
+    """TASK 132 R3.1: `os.path.relpath` as Windows runs it for a path that names a device.
+
+    It raises the `ValueError` of `ntpath.relpath` when the last part of its path or of its start
+    is `nul`. It calls the real function otherwise.
+    """
+    real = os.path.relpath
+
+    def relpath(path, start=os.curdir):
+        if any(os.path.basename(os.path.normpath(part)) == "nul" for part in (path, start)):
+            raise ValueError("path is on mount '\\\\.\\nul', start on mount 'C:'")
+        return real(path, start)
+    return mock.patch("os.path.relpath", side_effect=relpath)
 #: TASK 131 R6.5: a premise of POSIX that Windows does not hold.
 POSIX_PREMISE = os.name == "nt"
 #: The characters that a name on NTFS cannot hold.
@@ -1124,6 +1141,78 @@ class TestRebaseLinksGuard(unittest.TestCase):
         self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
         self.assertIn("--repo-root is a UNC or device path", result.stderr)
 
+    # --- TASK 132: a path that names a device (ARC-14) ------------------------------------------
+
+    def main_in_root(self, module, args):
+        """Exit code and stderr of `module._main(args)` in the root, under the stand-in."""
+        out, err = io.StringIO(), io.StringIO()
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        try:
+            with _device_relpath(), contextlib.redirect_stdout(out), \
+                    contextlib.redirect_stderr(err):
+                code = module._main(args)
+        finally:
+            os.chdir(cwd)
+        return code, err.getvalue()
+
+    def test_d5_a_link_to_a_device(self):
+        # base-fail: `relpath` raises for the link to `nul`, and the file mode ends in a traceback.
+        module = _module(REBASE, "rebase_links_under_test")
+        with _device_relpath():
+            _text, records = module.rebase_document_links(
+                "[a](ARCHITECTURE.md) [n](nul)\n", "docs", "docs/tasks", str(self.root))
+        self.assertEqual([r.action for r in records], ["REWRITTEN", "ESCAPES_ROOT"])
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text("[a](ARCHITECTURE.md) [n](nul)\n", encoding="utf-8")
+        code, err = self.main_in_root(module, ["docs/tasks/t.md", "--from", "docs",
+                                               "--to", "docs/tasks"])
+        self.assertEqual(code, 3, err)
+        self.assertEqual(moved.read_text(encoding="utf-8"), "[a](../ARCHITECTURE.md) [n](nul)\n")
+
+    def test_d5_an_operand_that_names_a_device(self):
+        # base-fail: `_under_git` calls `relpath`, which raises for `docs/tasks/nul`.
+        module = _module(REBASE, "rebase_links_under_test")
+        cwd = os.getcwd()
+        os.chdir(self.root)
+        self.addCleanup(os.chdir, cwd)
+        with _device_relpath():
+            self.assertEqual(module._refuse_operand("docs/tasks/nul"),
+                             "lies outside the working directory")
+        code, err = self.main_in_root(module, ["docs/tasks/nul", "--from", "docs",
+                                               "--to", "docs/tasks"])
+        self.assertEqual(code, 2, err)
+        self.assertIn("docs/tasks/nul: lies outside the working directory", err)
+
+    def test_d5_a_from_or_to_that_names_a_device(self):
+        # base-fail: each rewrite calls `relpath` from `--to`, which raises for `nul`; `--from nul`
+        # exits 3 at the base.
+        module = _module(REBASE, "rebase_links_under_test")
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text(LINKED, encoding="utf-8")
+        for option, args in (("--to", ["--from", "docs", "--to", "nul"]),
+                             ("--from", ["--from", "nul", "--to", "docs/tasks"])):
+            with self.subTest(option=option):
+                code, err = self.main_in_root(module, ["docs/tasks/t.md", *args])
+                self.assertEqual(code, 2, err)
+                self.assertIn(f"{option} does not lie inside the working directory", err)
+                self.assertEqual(moved.read_text(encoding="utf-8"), LINKED)
+
+    @WINDOWS_ONLY
+    def test_d6_a_device_on_windows(self):
+        moved = self.root / "docs" / "tasks" / "t.md"
+        moved.write_text("[n](nul)\n", encoding="utf-8")
+        result = self.rebase("docs/tasks/t.md")
+        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
+        self.assertIn("[ESCAPES_ROOT]", result.stdout)
+        self.assertEqual(moved.read_text(encoding="utf-8"), "[n](nul)\n")
+        result = self.rebase("docs/tasks/nul")
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("lies outside the working directory", result.stderr)
+        result = _run(REBASE, ["docs/tasks/t.md", "--from", "docs", "--to", "nul"], self.root)
+        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
+        self.assertIn("--to does not lie inside the working directory", result.stderr)
+
 
 class TestInboundGuard(unittest.TestCase):
     """TC-G8 to TC-G12 (TASK 115) and TC-G19 (TASK 116 R7.4): `--inbound` writes only regular
~~~~

`git apply --whitespace=nowarn` of the patch exited 0. Step 4: each final file hashes to its staged
copy and keeps the mode `644`, and `git apply --check -R` passes. Step 5: `rm --` of each staged
copy, each exit 0: `.agent/tools/staged_rebase_links.py`, `.agent/tools/staged_slot_links.py`,
`.agent/tools/staged_test_slot_links.py` and `tests/staged_script_guards.py`.

### J3 — the gates after stage 3

Each run below ran under the guard, with `.agent/sessions/` unchanged:
- `gates.py` from the repository root: 22 of 22 steps pass. The step of TASK 131 R7.1 in both
  Windows jobs: 395 passed and 11 skipped. The tooling step: 610 passed and 4 skipped;
- `check.py` for each command of PLAN J3, each exit code the one the PLAN names:
  - `68c87931dedb` and `e97c6d7e4fe6` from the root and from `tests/`: exit 0, 805 passed and 9
    skipped; from `.agent/tools/`: exit 0, 278 passed and 2 skipped; from `.agent/`: exit 2, the 21
    errors of the base. `ca2c33383ded` and `a8ddacaa1aa9`: exit 0;
  - `ce6cfae3843d`: `--help`, exit 0. The archive of TASK 131 with `--to docs/tasks`, exit 0, and
    with `--to nul`, exit 0. The operand `docs/tasks/nul`, exit 2. The inbound mode of §1, exit 3;
  - each pair of listings is equal, but one. During `e97c6d7e4fe6` from `tests/`, `.git` gained
    the remote-tracking refs of three branches `origin/dependabot/github_actions/…`, and
    `.git/FETCH_HEAD` and `.git/info/refs` changed. That is the mark of a `git fetch`, which no
    code of the change runs. The operator confirmed a fetch: answer "Это fetch, продолжай
    (Recommended)". It is a finding before the task, and the run put nothing back under `.git`;
  - the stop rule ends a step at such a difference. The script of the run did not stop there: it
    ran the remaining 11 commands, whose git calls only read (`rev-parse` and `ls-files`). Each
    gave its exit code and equal listings. After the operator's answer, `e97c6d7e4fe6` from
    `tests/` ran again: exit 0, 805 passed and 9 skipped, and equal listings;
- `rules_check.py compare`: the local and the user settings files are unchanged, with no new rule;
- `regcheck.py`: 0 warn on each changed document. `bytescan.py`: each of the 14 paths of
  `git status` is clean, and each is declared.

### J4 — stage 4, at the fingerprint `41ccfb8e02c4`: code review APPROVED, security audit PASS

Both reviewers read the brief of stage 4, computed `41ccfb8e02c4` at their start and at their end,
and ran the tests in the repository with `-B` and `-p no:cacheprovider`. Each first computed the
fingerprint with a plain `git status`; `.git/index` kept its time, so neither wrote it. The
scratchpad held no file of a reviewer afterwards, and the fingerprint was unchanged. Each confirmed:
- the four final files hash to the staged copies of round 1 with the mode `644`;
- `git diff` of them from the base equals the patch, and so does the fence of this record;
- no staged module is named by a file of code, test, workflow or settings;
- the step of TASK 131 R7.1 gives 395 passed and 11 skipped;
- the committed rule `ce6cfae3843d` runs the final file, and its commands of J3 give their exit
  codes.

The security scan ran, `scan_status: findings`, with none in the change but the false positives of
round 1. The auditor read the fetch of J3 in the remote reflog at 12:00:43.

Their findings, each LOW, on the records only:
- three wordings of TASK D12: which docstrings name no device, the place of a marker, and when
  `ntpath.relpath` raises;
- D12 cited the operator's rule of TASK 124 without its earlier rounds, and two of its findings
  are fixes rather than narrow routes. The operator answered "Закрыть как есть (Recommended)";
- S1: TASK §9 stated as measured the junction named after a device, which round 1 inferred;
- S2: TASK §9 said that a walk entry under a directory `x.` is written after the change; only the
  base writes it;
- S3: the ticks of J1 to J3;
- J3 ran 11 commands after the difference under `.git`, as recorded above.

TASK revision 4 takes each wording in place, D12 the operator's answer, and PLAN revision 6 the
ticks. Stage 4 passed.

## Retro (§6, PLAN K1)

The run id `framework-upgrade-task-132-arc-14-walk-relpath` was claimed at the start of the run.
The retro question listed four observed candidates:
- the regression of TASK 131, found only after the push;
- the script of J3, which did not stop at the difference under `.git`;
- exit codes that differ by platform;
- the closing on LOW findings. The operator answered "ничего". The
retro filed no record, and the claim was released, exit 0.
