# Framework Audit — 2026-07-28 — encoding five retro lessons from onchain-intel

**Auditor:** `skill-self-improvement-verificator`, **Mode B (Plan Audit)**
**Requested by:** owner, during a backlog closeout in the `onchain-analytics` project
**Verdict:** ✅ **PASS** — no blocking condition triggered; proceed.

## 1. What is being changed and why

Five work-items in `onchain-analytics/docs/BACKLOG.md` (WI-1, WI-5, WI-6, WI-7, WI-9) are process
lessons whose stated resolution is an edit to this framework. A grep over `System/` and
`.agent/` confirmed **none of the five is currently encoded anywhere** — they existed only as raw
`.agent/feedback/filed/*.json` findings and backlog prose, i.e. in the two places an agent never
reads while working. That is the defect being fixed: a lesson stored where it cannot fire is
indistinguishable from a lesson nobody learned.

| Item | Lesson | Target |
| :--- | :--- | :--- |
| WI-1 | Widening a repo-wide formatter/linter gate needs a blast-radius check BEFORE the write | `developer-guidelines` §5.1 (new) |
| WI-5 | "Remove dead code" findings must be checked against test dependencies first | `code-review-checklist` §2 |
| WI-6 | Fixes applied outside the dev→review loop still need their own review pass | `vdd-enhanced.md` §4 |
| WI-7 | Long agent tasks need incremental-write + priority-order + resume-not-respawn | `04_architect_prompt`, `08_developer_prompt`, `01_orchestrator` §7 item 15 |
| WI-9 | "One commit per task" only applies when tasks are file-independent | **REVERTED** — see note below |

Every one is **additive guidance**. No rule is deleted, no skill is removed from any agent, no
tier assignment changes.

> **Post-review correction (adversarial pass, same day).** WI-9 was **reverted in full** and
> `skill-planning-format` restored to its prior state. Its stated justification — that splitting
> file-coupled tasks yields intermediate commits which fail tests — is false under this framework's
> own Stub-First method: `tdd-stub-first` requires the E2E suite to pass on stubs, so the stub
> commit is green by construction. Worse, the rule's trigger ("any file touched by more than one
> task") fires on *every* Stub-First plan, since a stub task and its implementation task always
> write the same files. As written it would have collapsed the framework's default two-commit
> granularity into one commit per module. A rule that touches commit policy is a behavioural
> change, not guidance, and this one was justified by a scenario the framework cannot produce.
>
> Also reverted: the `vdd-enhanced.md` claim that independent critics categorically beat
> role-switched self-critique. It was uncited, and it deprecated the very workflow that file
> invokes at step 4.1 — while the one recorded experiment in `vdd-adversarial` SKILL.md points the
> other way on recall and prices `/vdd-multi` at ~3×.

## 2. Mode B checklist

1. **[x] Verification step.** These are prompt/skill documents; the framework's own mechanical gate
   for them is `python3 System/scripts/doctor.py`, run after the edits. Additionally, the five
   changed files are re-read after writing to confirm the surrounding structure is intact.
2. **[x] Rollback.** The repository is a clean git worktree at `e69fa1a` with **0 modified files**
   (verified before starting). Rollback is `git checkout -- <path>` or `git restore .` — strictly
   better than a `.bak` copy, and the reason no `.bak` is created here.
3. **[x] Atomic updates.** One file per lesson (WI-7 touches three, being addressed to three
   different roles). Each edit is a self-contained section insertion that does not depend on any
   other edit in this batch, so any subset can be reverted independently.
4. **[x] Test coverage.** No new framework *feature* is introduced — no script, no workflow, no
   skill file — so there is nothing with executable behaviour to test. The changes are guidance
   text consumed by agents. Recorded explicitly rather than silently skipped: **this checklist item
   is not applicable to this change**, and would become blocking the moment any of these edits grew
   a script.

## 3. Blocking conditions (§4 of the skill)

| Condition | Status |
| :--- | :--- |
| Removing `skill-core-principles` / `skill-safe-commands` from any agent | ❌ not triggered — nothing removed |
| Modifying `GEMINI.md` without a `System/Docs` update | ❌ not triggered — `GEMINI.md` untouched |
| Creating a new workflow without a trigger in `GEMINI.md` | ❌ not triggered — no new workflow |

No bypass flag is used or needed.

## 4. Residual risk

- **Prompt-length creep.** Five insertions across six files add roughly 60 lines of guidance to
  documents that are loaded as system prompts. Each insertion is deliberately short and placed in
  an existing section rather than opening a new top-level one. Worth revisiting if these prompts
  approach their own size limits — the architect prompt already carries a Step 4b size check for
  its *output*, and the prompts themselves deserve the same discipline eventually.
- **Cross-project blast radius.** This repository is consumed by four projects
  (`dynamic-test`, `obsidian-llm-wiki`, `onchain-analytics`, `travel-bootstrap`). The changes are
  additive guidance, so the failure mode is "an agent reads one more paragraph", not a behaviour
  break. Left **uncommitted** at the owner's explicit instruction so the diff is reviewed before it
  reaches the other three.
