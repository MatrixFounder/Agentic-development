# TASK 107 — framework-upgrade rolls back through git, and writes no copy outside it

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 107 |
| Slug | framework-upgrade-git-rollback |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | [WI-20](../backlog/wi-20-framework-upgrade-keeps-bak-copies-beside-git-roll-back-through-git-instead.md), option 1 |
| Operator decision | 2026-10-02: copies outside version control are not needed in principle |
| Base revision | `687d0466e807585b994f2faa479dbbf17024dfb6` |
| Closes | WI-20 |
| Archive name | `task-107-framework-upgrade-git-rollback.md` |

<!-- contract:problem -->

## 1. Problem

`/framework-upgrade` carries two rollback mechanisms. Git holds every path an upgrade edits.
§3.1 also copies the bootstrap files and every edited file to `.agent/archive/<name>.bak`, and
§5 restores from those copies.

**What the copies cost, measured 2026-10-02.**

- 60 copies, 1.7M, accumulated in `.agent/archive/`. Each one's content was found among git's
  objects. The operator had them deleted on that basis before this task's base was taken.
- Copies are named by basename, so two skills' `SKILL.md` could collide. TASK 106 wrote
  `SKILL.md.bak` without checking whether a copy of that name existed.
- A copy keeps text the tree has since changed. A repository grep for the old T4 label found it
  in two copies after TASK 106.

**Three readers repeat the copy rule.**

- `skill-self-improvement-verificator` Mode B check 2 asks for a step such as
  `cp GEMINI.md GEMINI.bak`. A plan that rolls back through git therefore fails the audit as
  written.
- The verificator's audit template and its worked examples ask for a "backup strategy".
- `System/Docs/WORKFLOWS.md` §5 states the rollback as an automatic copy to `.agent/archive/`.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | `framework-upgrade.md` gains §0: a clean tree before the first edit, and a recorded base commit | Y | A1, A2 |
| R2 | §3.1 states the rollback point and writes no copy outside version control | Y | A1, A2 |
| R3 | §5 restores from the base commit and removes created paths by name | Y | A1, A2 |
| R4 | Verificator Mode B check 2 asks for the base commit, not a copy; version 1.0 → 1.1 | Y | A1, A3 |
| R5 | The audit template and the worked examples ask the same question | Y | A1, A3 |
| R6 | `System/Docs/WORKFLOWS.md` §5 states the git rollback | Y | A1 |
| R7 | `.gitignore` and `tests/test_frozen_tree_contract.py` comments state that no run writes copies now | Y | A6 |
| R8 | A unittest module pins R1–R6 and runs in the curated suite | Y | A1, A2, A4 |
| R9 | WI-20 is closed, and both changelogs carry the release | Y | A5, A6 |

### 2.1 Sub-features

**R1 — §0, before §1.**

1. The run happens in the framework's own repository, from its top level. §0 checks that
   `.agent/workflows/framework-upgrade.md` is tracked there; an installed project fails the check.
2. `git status --porcelain --untracked-files=all` exits 0 and prints nothing. Otherwise the run
   stops; the operator commits or runs `git stash -u`, and the run restarts at §0. The workflow
   never stashes, commits or discards the operator's work.
3. The full `git rev-parse HEAD` hash is the base. §0 persists it through `update_state.py` with
   every required argument and the task in the entry. From §1.3 on, the audit header is the
   record §5 reads.

**Why §0 and not §3.1.** §1 already edits the tree: it archives the previous TASK and writes the
new one. A rollback point taken at §3.1 would miss those edits.

**R2 — §3.1 "Rollback point".**

1. `git rev-parse HEAD` still equals the recorded base. The run commits nothing; the operator
   commits after §4.5.
2. The PLAN declares every path it edits and creates. §2.2 asks for the full repo-relative path
   of each, one per list item.
3. Each edited path passes `git ls-files --error-unmatch`; each created path is not ignored; each
   declared path matches `[A-Za-z0-9._/-]+`, has no `.git` or `..` segment, and is relative. A
   failing path stops the run. No `git add -f`.
4. No path outside this repository is edited during the run.
5. No copy of any file is written outside version control.

**R3 — §5 Fallback.** Only the operator's own message confirms it; a subagent never runs it.
The audit is kept.

1. §5 sets `top` again, since shell state does not survive between calls, and checks HEAD against
   the audit header's base. A mismatch stops the run.
2. `git status --porcelain=v1 --untracked-files=all` lists every change **before** anything moves.
   Each path is identical to a declared one: from the PLAN, from §4.5's repair list in the audit,
   or this run's TASK, PLAN, archive pair or audit. Both paths of an `R` or `C` entry count. Any
   other entry stops the run.
3. The list is recorded where the base is recorded and shown to the operator. After the reply it
   is taken again; a different list stops the run.
4. `??` entries other than the audit are removed with `rm -- "${top:?}/<path>"`, files only.
5. The other entries are restored by name from the base.
6. A final `git status` shows only the audit. Anything else stops the run.
7. `git reset --hard`, `git clean`, `git checkout` and `git stash` are not used. A committed
   upgrade is reverted by the operator; a merge needs `git revert -m 1`.

**R4 — Mode B check 2.** "Does the plan record the base commit, and does every edited or created
path return to it?" Version `1.0` → `1.1`.

**R5 — template and examples.**

1. `assets/audit_template.md`: the header carries `Base revision`; the Rollback Plan row asks
   R4's question.
2. `examples/audit_examples.md`: each header carries `Base revision`. The good example declares
   its created files. The bad example fails on an edit that predates the run; its required action
   stops the run until the operator commits or stashes.

**R6 — WORKFLOWS.md.** §5 Safety Protocol item 4 states R1–R3 in one item.

**R7 — the two comments.** The `.gitignore` entry for `.agent/archive/` stays. A clone holding
copies from before this task keeps a clean `git status`. The comment states that. The comment
above `SCAN_ROOTS` in `tests/test_frozen_tree_contract.py` changes the same way; `_is_scanned`
keeps its exclusion.

**R8 — the pin.** `tests/test_git_rollback_contract.py`, pure `unittest`:

1. `TC-01` — §0 precedes §1 and carries its commands; its clean-tree item carries its stop. The
   §2.2, §3.1 and §4.5 texts carry the declaration and its checks. The §5 body carries each
   control in the order list, confirm, remove, restore, check.
2. `TC-02` — no markdown file in the instruction roots names a copy. Roots: `.agent/workflows/`,
   `.agent/skills/` without `evals/corpus*`, `System/Docs/`, `System/Agents/`,
   `.claude/commands/`, `.claude/agents/`, the vendor agent directories, the bootstrap files.
   Tokens: `.bak`, `.orig`, `.backup`, `.old`, `.agent/archive`, `.agent/backups`. Vendor roots
   are read as markdown, TOML and JSON.
3. `TC-03` — Mode B check 2, read as a whole list item, names the base commit and no copy.
4. `TC-04` — the workflow names `git reset --hard`, `git clean`, `git stash`, `git checkout`,
   `git add -f`, `rm -r` or `-delete` only in one of three exact prohibition sentences.
5. The module is in `CURATED_UNITTEST_MODULES` in `tests/run_tests.py`, which CI runs.

**R9 — closure and release.** WI-20 takes four edits: `status: done`, `resolved_at` and
`resolved_by`, a resolution blockquote, and its index line moved to `## Closed`. Changelogs:
`v3.32.0`, since a workflow changes what it runs.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — an upgrade that completes.**
*Actor:* the orchestrator running `/framework-upgrade`.
*Precondition:* the operator's tree is committed.
*Main:* §0 records the base; §1–§4 edit tracked paths; nothing is written outside git.
*Postcondition:* `git status` shows the upgrade's changes and nothing else.

**UC-2 — an upgrade that fails mid-way.**
*Actor:* the orchestrator.
*Precondition:* §3 left the system unstable.
*Main:* the operator confirms; §5 restores from the base and removes the declared created files.
*Alternative A1 (at Main):* an entry the PLAN does not declare remains. §5 stops and asks.
*Postcondition:* HEAD equals the base; only the audit remains untracked.

**UC-3 — an upgrade started on a dirty tree.**
*Actor:* the orchestrator.
*Precondition:* `git status --porcelain` prints at least one line.
*Main:* §0 stops and asks the operator to commit or stash.
*Alternative A1 (at Main):* the operator commits. §0 records that commit as the base.
*Postcondition:* no edit happens before the tree is clean.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion |
| :--- | :--- |
| A1 | `python3 -m pytest tests/test_git_rollback_contract.py -q` passes |
| A2 | Each R8 mutation below fails that module; reverting it passes |
| A3 | `System/scripts/validate_skills.py --root . --quiet` reports every skill valid |
| A4 | `PYTHONPATH=. python3 tests/run_tests.py` runs the new module and reports OK |
| A5 | `python3 -m pytest tests/ -q` passes, and `check_loop_contract.py` reports 0 errors |
| A6 | `scan_register.py` over every edited markdown file reports no new `warn` |
| A7 | `git status --short` lists only the files `docs/PLAN.md` declares |
| A8 | The CI living-corpus reference check reports 0 errors |

**A2 mutations.** Each is applied alone and reverted. The audit's mutation table lists all 41
with their outcomes. They cover five groups:

1. a copy instruction in each scanned spelling, placed in each kind of instruction file, and in a
   `corpus*` file outside `evals/`;
2. a deleted or weakened control in §0, §2.2, §3.1, §4.5 or §5;
3. a destructive command added: `git reset --hard`, `git clean`, `rm -rf`, `rm -fr`, `rm -R`,
   `rm --recursive`, a whole-tree `git restore`, an agent-run stash, a restore hidden in a comment;
4. the §5 order changed: restore before list, or restore before remove;
5. two legitimate reflows, of check 2 and of a §0 command, which must pass.

Every mutation fails the module except the two reflows.

<!-- contract:open-questions -->

## 5. Open Questions

**OQ1 — none open.** The operator chose WI-20 option 1 on 2026-10-02.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-10-02, orchestrator: the base commit is taken at §0.** §1 edits the tree first, through
the TASK archive and the new TASK. Rejected: §3.1 — the rollback would miss every §1 and §2 edit.

**D2, 2026-10-02, orchestrator: a dirty tree stops the run.** The workflow cannot tell the
operator's uncommitted work from its own. Rejected: an automatic `git stash` — a stash the run
forgets to pop hides the operator's work with no signal.

**D3, 2026-10-02, orchestrator: created paths are removed by name.** Rejected: `git clean -fd` — it
removes every untracked path, including one the run did not create.

**D4, 2026-10-02, orchestrator: the `.gitignore` entry and the test exclusion stay.** Copies from
earlier runs may still exist in other clones. Rejected: removing both — such a clone would show its
old copies in `git status`, and `test_frozen_tree_contract.py` `TC-03` would count them as sites.

**D5, 2026-10-02, orchestrator: the pin runs in the curated suite, not a new CI line.** CI runs
`tests/run_tests.py`, which loads `CURATED_UNITTEST_MODULES`. Rejected: editing
`.github/workflows/framework-gates.yml` — a second registration for the same module.

**D6, 2026-10-02, orchestrator: the first review round, applied.** Base fingerprint
`67e0f8050084`. `code-reviewer` returned REQUEST CHANGES. Its blocking finding: §5 removed every
untracked path it listed, and that list holds paths the run never created. Causes:
`status.showUntrackedFiles=no` at §0, a run from a subdirectory, a concurrent writer, or HEAD past
the base. The `security-auditor` round **failed**: its mutation script missed its copy on a
dangling symlink and wrote into the frozen tree. It also ran `git checkout --` on one file. It
restored the files, and the caller confirmed the fingerprint and each file unchanged. Its findings
still entered this loop. Fixed:

- §0 runs from the top level, checks untracked files too, records the full hash, and persists it;
- §3.1 leaves commits to the operator, stops on an untracked path, and forbids `git add -f`;
- §5 needs the operator's confirmation, checks HEAD, restores `:/`, and removes only declared
  files with `rm --`; it keeps the audit and stops on anything else;
- `git revert -m 1` for a merge; `git stash -u` for the operator;
- the template and examples carry `Base revision`; the bad example stops the run;
- the pin reads §0 and §5 as sections, scans the prompt and wrapper roots, widens the token set,
  and gains `TC-04`.

**D7, 2026-10-02, orchestrator: findings of the first round left as they are.**

- `docs/design/104_resolver_wiring.md:152@687d046` `Back them up to` cites the old §3.1. It is a
  task's design record, not an instruction surface.
- `.claude/settings.json` lets `git restore` run without a prompt. Permissions are the operator's;
  §5 asks for the operator's confirmation instead.
- The `.cursor/skills` symlink resolves to nothing. It predates this task. The operator chose not
  to file it at Retro.

**D8, 2026-10-02, orchestrator: the second review round, applied.** Fingerprint `8c8b9095f1f3`;
both roles wrote nothing in the repository. `code-reviewer` returned REQUEST CHANGES and
`security-auditor` PASS WITH NOTES. Both found the same defect. §5 read the declared set from a
PLAN its own restore had just reverted. It also discarded an undeclared tracked edit without
showing it. Fixed:

- §5 lists every change first and stops on an undeclared one. It shows the list, waits for the
  operator, and then restores declared paths by name, not `:/`;
- `rm -- "$top/<path>"`, and declared paths match `[A-Za-z0-9._/-]+`;
- §0 checks the framework repository by a tracked path, and gives the full `update_state.py` call;
- §2.2 tells the planner to declare every path; §3.1 names the checks; §4.5 lists its repairs;
- the pin checks each §5 control and its order, strips comments, scans vendor TOML and JSON, and
  reads `TC-04` over the whole workflow against exact prohibition sentences.

Left: `check_positional_refs.py --fix` walks ignored files too, so §4.5 can rewrite one. The
operator chose not to file it at Retro.

**D9, 2026-10-02, orchestrator: the third review round, applied.** Fingerprint `af13d6aafd4d`.
`code-reviewer` checked closure only, wrote nothing in the repository, and returned APPROVE WITH
CHANGES. Both round-2 blocking findings are closed, each reproduced in a throwaway repository.
Fixed from its list:

- `$top` does not survive between shell calls, so §5 sets it again and removes with
  `rm -- "${top:?}/…"`; an unset variable stops instead of reaching `/`;
- §5 removes created files before it restores, so a path both untracked and deleted ends at the
  base; a final `git status` must show only the audit;
- an `R` or `C` entry needs both paths declared and restored;
- a declared path may not hold a `.git` or `..` segment or start with `/`;
- the confirmed list is recorded beside the base and taken again after the reply;
- §2.2 asks for full repo-relative paths, one per list item;
- the pin collapses whitespace in §0, scans `.agent/rules/`, pins the new sentences, and catches
  `rm -fr`, `rm -R`, `rm --recursive` and a whole-tree `git restore`.

Left: empty directories after a fallback (git ignores them), and spellings outside the token set,
which the pin's docstring names.

<!-- contract:out-of-scope -->

## 7. Out of scope

| Excluded | Reason |
| :--- | :--- |
| Installer snapshots under `.agent/backups/` | the target project may hold untracked files, or no git at all |
| Mutation-planting copies in `developer-guidelines` and `vdd-adversarial` | they run mid-review, on a tree that may carry uncommitted work |
| `test_frozen_tree_contract.py`, `test_resolver_wiring.py` absent from CI | found here; not filed at Retro, operator decision |
| Running this workflow inside an installed project | §0 sends it to the framework repository |
| Any edit to `docs/tasks/`, `docs/plans/` or ledger record bodies | ARCHITECTURE §7.2, immutable |
