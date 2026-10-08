---
description: Pipeline for upgrading the Agentic Framework itself (Prompts, Skills, System Logic)
contract:
  version: 1
  loops:
    - id: spec-audit-retry
      what: specification meta-audit fails -> redraft TASK
      site: "<!-- loop:spec-audit-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
    - id: plan-audit-retry
      what: plan meta-audit fails -> redraft PLAN
      site: "<!-- loop:plan-audit-retry -->"
      default_max: 3
      override: forbidden
      on_exhaust: escalate_user
  calls: []
---

# Workflow: Framework Upgrade

> [!CAUTION]
> **META-OPERATION**: This workflow modifies the Agent's own operating logic.
> **Strict Adherence Required**: No skipping validation steps.

> **Retro claim (Global Protocol):** run `python3 .agent/skills/run-feedback/scripts/run_feedback.py claim --run-id "framework-upgrade-<task-slug>"` (non-blocking; exit 6 = an outer workflow of this task owns this run's retro — fine, continue; an owner from another task is a stale claim — run-feedback §7 Retro step 1).

## 0. Rollback point (before any edit)

This workflow edits the framework's own repository. Where the framework is installed into a
project as a symlink or a copy, run it in the framework repository, not in that project.

§1 edits the tree: it archives the previous TASK and writes the new one. The rollback point is
therefore taken here, before §1. Git holds every state this run can return to.

1. **Top level.** `top=$(git rev-parse --show-toplevel)` exits 0; then `cd "$top"`. Then
   `git ls-files --error-unmatch -- .agent/workflows/framework-upgrade.md` exits 0. A non-zero exit
   from either means this is not the framework repository: **STOP**.
2. **Clean tree.** `git status --porcelain --untracked-files=all` exits 0 and prints nothing.
   Otherwise **STOP** and ask the operator to commit, or to run `git stash -u`. The run then
   restarts at §0. The workflow never stashes, commits or discards the operator's work.
3. **Record the base.** `git rev-parse HEAD` prints the full 40-character hash. Persist it at once:
   `python3 .agent/skills/skill-session-state/scripts/update_state.py --mode "FRAMEWORK-UPGRADE"
   --task "<task>" --status "base recorded" --summary "base <hash>"
   --add_decision "framework-upgrade <task> base <hash>"`. When §1.3 creates
   `docs/reviews/framework-audit-<ID>.md`, its header carries the hash as `Base revision`. From then
   on the audit header is the record §5 reads.

## 1. Analysis & Meta-Audit
1. **Analyze**: Read User Request.
2. **Draft**: Create `docs/TASK.md` (Type: Framework Upgrade). `skill-archive-task` archives the
   previous TASK and PLAN first. When its Step 8 rewrites a file, the run records the list at once
   in the session state, as §0 records the base, and §1.3 copies it into the audit with Step 8's
   records.
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: SPECIFICATION AUDIT).
   - **Instruction**: "Check `docs/TASK.md` for safety violations."
   <!-- loop:spec-audit-retry -->
   - **Gate**: If Audit fails, GOTO Step 2.
   - **Target of that GOTO**: **Step 2 of THIS section** (§1.2, redraft `docs/TASK.md`) — not §2.
   - **Bound: max 3 audit rounds.** Still failing after the 3rd: **STOP** and escalate to the user
     with the verificator's outstanding safety violations. A framework upgrade never proceeds on an
     unaudited TASK.

## 2. Planning & Safety Check
1. **Architect**: Update `docs/ARCHITECTURE.md` (if System Architecture changes).
2. **Plan**: Create `docs/PLAN.md` (Implementation Steps). It declares the full repo-relative
   path of every file the run edits and every file it creates, one per list item. Then §3.1
   checks that declaration, and §5 requires an identical path.
3. **Meta-Audit**:
   - **Call**: `skill-self-improvement-verificator` (Mode: PLAN AUDIT).
   - **Instruction**: "Check `docs/PLAN.md` for rollback and verification steps."
   <!-- loop:plan-audit-retry -->
   - **Gate**: If Audit fails, GOTO Step 2.
   - **Target of that GOTO**: **Step 2 of THIS section** (§2.2, redraft `docs/PLAN.md`).
   - **Bound: max 3 audit rounds.** Still failing after the 3rd: **STOP** and escalate to the user
     with the verificator's outstanding findings — do not enter §3 Execution.

## 3. Execution (Atomic Updates)
1. **Base check**:
   - `git rev-parse HEAD` still equals the base recorded in §0. The run commits nothing; the
     operator commits the upgrade after §4.5.
   - Every path the PLAN edits passes `git ls-files --error-unmatch -- <path>`. For every path the
     PLAN creates, `git check-ignore -q -- <path>` exits 1.
   - Every declared path matches `[A-Za-z0-9._/-]+`, has no `.git` or `..` segment, and does not
     start with `/`.
   - A path that fails any of these checks is not touched: **STOP** and ask the operator. The run
     never uses `git add -f`.
   - No path outside this repository is edited during the run. A mirror is synced after the
     operator's commit.
   - No copy of any file is written outside version control. The run's own state under
     `.agent/sessions/` and `.agent/feedback/` is ignored by design and is not rolled back. A test
     fixture that the test itself creates in a temporary directory and removes is no such copy
     (step 4).
2. **Implement**: Execute `08_developer_prompt.md` with `skill-self-improvement-verificator` active.
3. **Verify**:
   - Run affected tests.
   - Run `skill-spec-validator` (if modified).
4. **Hooks and permission rules take effect at once.** Claude Code applies a settings file to the
   running session as soon as it changes, the reviewers' commands included. The step covers every
   change that alters what runs, or what runs without a prompt. The list is not exhaustive:
   - a hook in a settings file, or in the frontmatter of an agent or a skill;
   - the script of a registered hook, code that script calls, and a new module it would import;
   - a script that a committed allow rule names, code that script calls, and a new module it
     would import;
   - a permission rule, `additionalDirectories` or the permission mode, an agent's
     `permissionMode` and the `allowed-tools` of a skill or a command among them;
   - a settings key that names a command, such as `statusLine`, or sets a command's environment,
     `env`;
   - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.

   Test modules and fixtures that no rule names by path are exempt, and so is code that runs
   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
   hook or listed script runs or imports; a fixture is a data file that a test reads.
   `tests/run_tests.py` is named by a rule and is not exempt.

   A change that only narrows what runs without a prompt, such as a removed allow rule, may land
   at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
   it narrows, and the audit record holds the check's output:
   - a base entry of the same list covers each new allow rule, `additionalDirectories` entry and
     `allowed-tools` entry;
   - each base deny or ask rule and `disallowedTools` entry is still present, or a new entry of the
     same list covers it;
   - every other key equals the base's;
   - no code of the list above changes, and no new module appears that it would import.

   The run registers nothing in `.claude/settings.local.json` or the user's settings; an edit
   there waits for the operator's commit and their go-ahead.

   Every other change runs in four stages. The audit record is
   `docs/reviews/framework-audit-<ID>.md`; the security audit is the review of stage 2.
   1. **Fixture.** The TASK states the exact registration: the event, matcher and command of a
      hook, or the text of a rule or key. A hook's test builds a temporary root with its own
      `.claude/settings.json` holding that registration, and removes it. Code of the list above
      is edited under a new name.
   2. **Reviews.** The code review and the security audit check the code and the registration.
      Both must pass. An `INCOMPLETE` security audit blocks the registration: `security-audit`
      §6.2 re-runs the unfinished part once, and then the operator decides.
   3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
      into its file, or the new code over the code it replaces, and removes the copy under the new
      name. Only the retro's records follow this edit. The same edit adds a settings test that
      pins the registration, and the gates run again.
   4. **Focused review.** A code reviewer and a security auditor check the stage-3 diff on the new
      fingerprint.

   **Failure.** If the gates of stage 3 fail, or the focused review does not pass, the run
   restores every file of stage 3's edit at once to its text before that edit. The restore brings
   back the copy under the new name, if there is one, and the audit record holds the stage-3 diff.
   - When an `INCOMPLETE` security audit is the only failure, `security-audit` §6.2 governs the
     re-run, which reads that recorded diff. If the re-run passes, stage 3 applies the same diff
     again, and stage 4 checks it on the new fingerprint.
   - In every other case, a failed gate, a rejected code review or a `FAIL` among them, the
     operator decides what follows. A registration, or the code it runs, whose text changes
     returns to stage 1.

   **Why.** TASK 111 registered a PreToolUse hook while building it, and the hook asked for
   approval on the orchestrator's and the reviewers' own commands in Auto mode.

## 4. Documentation & Finalization
1. **Docs**: Update `System/Docs/` to match new reality.
2. **Registry**: Update `System/Docs/SKILLS.md` and `WORKFLOWS.md`.
3. **Restart**: Instruct User to restart session if Core Prompts changed.

## 4.5 Reference resolver (gate)

Run `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed --fix`.

It selects documents **citing** the files this change touched, which default diff scope
does not. `REFERENT_MOVED` is repaired mechanically and the repair lands in the same
commit; a coordinate carrying no referent is reported as *not examined* and is **not** a
defect (`documentation-standards` §4.1). This position is the one WI-16's §5.1 table
names for the State-Claim Sweep: when that record lands it inserts **above** this
section, so neither displaces the other.

The audit lists every file a `--fix` repair touched. §5 treats those files as declared.

## 5. Fallback
Fallback discards every change this run made since the base, except the audit, which it keeps.
Only the operator's own message confirms a fallback. A subagent never runs §5; it reports and
stops.

0. **Top level and base.** `top=$(git rev-parse --show-toplevel)` exits 0; then `cd "$top"`. Shell
   state does not survive between calls, so §5 sets `top` again rather than reading §0's. Then
   `git rev-parse HEAD` equals the `Base revision` in the audit header. Before §1.3 has written
   the audit, the session-state entry from §0 holds it. Otherwise **STOP**: a commit exists, and
   the operator decides how to revert it.
1. **List before restoring.** `git status --porcelain=v1 --untracked-files=all` lists every
   change. Every path on every entry must be identical to a declared path:
   - a path the PLAN declares;
   - a file a §4.5 repair touched, as the audit lists it;
   - a file that Step 8 of `skill-archive-task` rewrote in §1, as the audit lists it, or as the
     session state lists it before §1.3 has written the audit;
   - this run's `docs/TASK.md`, `docs/PLAN.md`, archive pair or audit.

   An `R` or `C` entry names two paths, and both must be declared. Before §2.2 has written the
   PLAN, only the last two kinds apply. Any other entry means **STOP** and ask the operator.
2. **Confirm.** Record the list where the base is recorded, show it to the operator, and wait for
   the operator's reply. Then list again; a different list means **STOP**. Steps 3 and 4 act on
   the recorded list.
3. **Remove created files.** For every `??` entry except the audit,
   `rm -- "${top:?}/<path>"`. Files only, never `-r`. A non-zero exit means **STOP**.
4. **Restore by name.** For every other entry, both paths of an `R` or `C` entry included:
   `git restore --source=<base> --staged --worktree -- <path>…`. A non-zero exit means **STOP**.
5. **Check.** `git status --porcelain=v1 --untracked-files=all` prints only the audit. Otherwise
   **STOP** and ask the operator. The operator commits or removes the audit before the next run.
6. Do not use `git reset --hard`, `git clean`, `git checkout` or `git stash` here. Each acts on
   paths no step named. The committed `.claude/settings.json` denies the first, second and fourth
   of them to Claude Code (TASK 116). A deny rule matches only the spellings it names, so this
   rule still applies.
7. Once the operator has committed the upgrade, the rollback is the operator's
   `git revert <commit>`; for a merge commit, `git revert -m 1 <merge>`.

## 6. Retro (Global Protocol)
Apply `run-feedback` SKILL.md §7 "Retro protocol":
`claim --run-id "framework-upgrade-<task-slug>"` → exit 6 = nested, SKIP this step (unless the owner is another task's run — a stale claim, run-feedback §7 Retro step 1);
exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
collect → triage → file per the skill, and `release`. **Non-blocking**: failures
here are reported in one line and never change this workflow's outcome.
