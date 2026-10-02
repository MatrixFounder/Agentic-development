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
2. **Draft**: Create `docs/TASK.md` (Type: Framework Upgrade).
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
1. **Rollback point**:
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
     `.agent/sessions/` and `.agent/feedback/` is ignored by design and is not rolled back.
2. **Implement**: Execute `08_developer_prompt.md` with `skill-self-improvement-verificator` active.
3. **Verify**:
   - Run affected tests.
   - Run `skill-spec-validator` (if modified).

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
   - this run's `docs/TASK.md`, `docs/PLAN.md`, archive pair or audit.

   An `R` or `C` entry names two paths, and both must be declared. Before §2.2 has written the
   PLAN, only the last kind applies. Any other entry means **STOP** and ask the operator.
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
   paths no step named.
7. Once the operator has committed the upgrade, the rollback is the operator's
   `git revert <commit>`; for a merge commit, `git revert -m 1 <merge>`.

## 6. Retro (Global Protocol)
Apply `run-feedback` SKILL.md §7 "Retro protocol":
`claim --run-id "framework-upgrade-<task-slug>"` → exit 6 = nested, SKIP this step (unless the owner is another task's run — a stale claim, run-feedback §7 Retro step 1);
exit 0 = gather what did NOT go smoothly this run (failed/retried gates, blockers
from `.agent/sessions/latest.yaml`), ask the user the one retro question, then
collect → triage → file per the skill, and `release`. **Non-blocking**: failures
here are reported in one line and never change this workflow's outcome.
