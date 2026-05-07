# Technical Specification: VDD Chain Workflow (`/vdd-develop-all`)

### 0. Meta Information
- **Task ID:** TBD (assigned by Planner via `task_id_tool.py`)
- **Slug:** `vdd-develop-all`
- **Mode:** VDD (Verification-Driven Development)
- **Type:** Framework upgrade — new workflow composition

## 1. General Description

Compose the existing primitives `/develop-all` (chain iteration over `docs/PLAN.md`) and `/vdd-develop` (Builder → Verification → Sarcasmotron-roast loop) into a single workflow `/vdd-develop-all` that walks the entire plan, applies the **adversarial** review variant to each task, and **never** auto-commits.

Load-bearing differences from `/develop-all`:
- Adversarial Sarcasmotron review per task instead of standard `code-reviewer`.
- Inter-task HITL gate (mandatory, not optional).
- No auto-commit, ever (the chain ends with a status report; commit/PR decision belongs to the user).
- Resumable from `.agent/sessions/latest.yaml` if interrupted.
- Hard escalation after 3 consecutive REJECTED iterations (no silent retry).

Architectural impact: **none**. Workflow uses existing Layer A / Stage Cycle patterns (see [ARCHITECTURE.md §3, §5.1](ARCHITECTURE.md#3-workflow-logic-v31)). No new agents, skills, or infrastructure.

## 2. Epics & Issues (Chainlink Decomposition)

### Epic E1 — Workflow file `vdd-05-run-full-task.md`

#### Issue I1.1 — File scaffold and frontmatter
**Acceptance:**
- ✅ File created at `.agent/workflows/vdd-05-run-full-task.md`.
- ✅ Frontmatter `description:` line in same shape as sibling workflows (`05-run-full-task.md`, `vdd-03-develop.md`).
- ✅ File contains exactly **5 numbered steps** matching FR-1 … FR-5 below.

#### Issue I1.2 — Step 1: Plan parsing
**Acceptance:**
- ✅ Reads `docs/PLAN.md` and extracts ordered list of tasks (`Task X.Y`) with paths to `docs/tasks/task-{ID}-{SubID}-{slug}.md`.
- ✅ Respects PLAN.md sectioning (Stage 1 / Stage 2) and dependency order.
- ✅ References `skill-spec-validator` for PLAN ↔ TASK conformance check before iteration.
- ✅ Supports `--dry-run` flag: prints planned chain (task IDs + order) and exits without execution.

#### Issue I1.3 — Step 2: Per-task VDD cycle
**Acceptance:**
- ✅ Step A (Builder): references [System/Agents/08_developer_prompt.md](../System/Agents/08_developer_prompt.md) and `tdd-stub-first` skill (Stub → Logic).
- ✅ Step B (Verification): runs `bash tests/test_e2e.sh` (or per-skill equivalent), unit-test discovery, and `validate_skill.py` where the task touches `.agent/skills/`. Red tests force a Builder loop **before** Sarcasmotron — never roast a broken build.
- ✅ Step C (Sarcasmotron-roast): **delegates** to `/vdd-develop` Step 3 (DRY — no inline copy of persona overlay). Cross-link must point at [.agent/workflows/vdd-03-develop.md](vdd-03-develop.md).
- ✅ Step D (Refinement loop): on REJECTED → return to Step A; **max 3 iterations**; on 3rd consecutive REJECTED → STOP, escalate to user with digest of findings (rationale: Sarcasmotron is stricter than standard reviewer; 2 is too tight, 4+ wastes tokens on stuck tasks).
- ✅ APPROVED (including Hallucination Convergence) → merge task, persist session-state via `update_state.py --add_completed_task <name>`.

#### Issue I1.4 — Step 3: HITL gate between tasks
**Acceptance:**
- ✅ After each merged task, workflow emits a one-page digest in the format:
  ```
  Task X.Y merged. Verdict: APPROVED via {Hallucination Convergence | clean approval}.
  {N} {LOW/MED} findings polished. Iterations: {k}/3.
  Continue to Task X.Y+1? [yes / pause / abort]
  ```
- ✅ **Default mode**: explicit user input required (no timeout).
- ✅ **Optional mode**: `--auto-continue=<seconds>` flag activates a timeout-based auto-continue. Documented but **off by default**.
- ✅ `pause` → stop chain, leave `latest.yaml` in resumable state.
- ✅ `abort` → stop chain, no commit, summary report.

#### Issue I1.5 — Step 4: Session-state persistence
**Acceptance:**
- ✅ After every merge, calls `python3 .agent/skills/skill-session-state/scripts/update_state.py` with `--mode "vdd-develop-all" --task "<TaskName>" --status "merged" --add_completed_task "<TaskName>"`.
- ✅ Critical decisions (e.g., "approved via Hallucination Convergence on iteration 2") logged via `--add_decision`.
- ✅ References [.agent/skills/skill-session-state/SKILL.md](../.agent/skills/skill-session-state/SKILL.md) §3–§4.

#### Issue I1.6 — Step 5: Finalization (no auto-commit)
**Acceptance:**
- ✅ At chain end, runs full regression suite: `bash tests/test_e2e.sh` + unit-test discovery + `validate_skill.py` across changed skills.
- ✅ Emits final report to user with:
  - Merged tasks list.
  - **Metrics**: total merged, total REJECTED iterations across the chain, count of `Hallucination-Convergence APPROVED` vs honest APPROVED.
  - Current `git status` snapshot.
- ✅ **Auto-commit is explicitly forbidden** — must include a comment line stating: *"Anti-pattern: auto-commit. Commit/PR decision belongs to the user. This is the load-bearing difference from `/develop-all`."*

#### Issue I1.7 — Resumability section
**Acceptance:**
- ✅ Workflow includes a `## Resumability` block: re-invoking `/vdd-develop-all` after `pause` reads `.agent/sessions/latest.yaml`, identifies first non-merged task in PLAN.md, resumes from Step 2 of cycle for that task.
- ✅ Cross-link to [.agent/skills/skill-session-state/SKILL.md](../.agent/skills/skill-session-state/SKILL.md) §2 (Boot Protocol).
- ✅ **Behavioral smoke test** (documented in workflow's `## Resumability` block): invoke `/vdd-develop-all`, send `pause` after task 1.1 merge, re-invoke; chain must resume at task 1.2 Step 2 — not restart from task 1.1.

#### Issue I1.8 — Vendor-agnostic note
**Acceptance:**
- ✅ Workflow includes a `## Fallback` section noting Layer A / Layer B decision per `skill-parallel-orchestration`. On Gemini CLI / Cursor, the workflow degrades to sequential role-switching with the same step structure.

#### Issue I1.9 — Example invocation
**Acceptance:**
- ✅ File ends with `## Example invocation` showing one runnable example (e.g., `/vdd-develop-all` with no args; second example with `--dry-run`).

### Epic E2 — Slash command registration

#### Issue I2.1 — `.claude/commands/vdd-develop-all.md`
**Acceptance:**
- ✅ Created using the same template as [.claude/commands/vdd-develop.md](../.claude/commands/vdd-develop.md) and [.claude/commands/develop-all.md](../.claude/commands/develop-all.md).
- ✅ Body: `Read and execute the workflow defined in '.agent/workflows/vdd-05-run-full-task.md'. … User's task context: $ARGUMENTS`.

### Epic E3 — Documentation cross-links

#### Issue I3.1 — `CLAUDE.md` registry update
**Acceptance:**
- ✅ `## WORKSPACE WORKFLOWS` block in [CLAUDE.md](../CLAUDE.md) "Available Commands" list updated to include `/vdd-develop-all`.

#### Issue I3.2 — Cross-link from `vdd-03-develop.md`
**Acceptance:**
- ✅ A trailing note appended: *"Для прогона всей цепочки задач — см. /vdd-develop-all (`.agent/workflows/vdd-05-run-full-task.md`)."*

## 3. Non-functional Requirements

- **Anti-pattern enforcement** (must be explicit in workflow text, not just implicit):
  - ❌ No auto-commit — anywhere, including intermediate steps.
  - ❌ No silent retry past 3 REJECTED iterations.
  - ❌ No skipping Step B (Verification) before Sarcasmotron.
  - ❌ No editing `docs/tasks/*.md` from inside the workflow — chain only **executes** tasks.
- **Vendor-agnostic**: works under Claude Code, Gemini CLI, Cursor. Per `skill-parallel-orchestration` Layer A/B selection.
- **Resumability**: interrupted chain restorable from `.agent/sessions/latest.yaml` — no re-derivation of state.
- **DRY**: Sarcasmotron persona overlay must NOT be inlined; reference `/vdd-develop` Step 3.
- **Token budget**: workflow file ≤ ~150 lines (sibling workflows are 20–60 lines; this is more complex but should not bloat).

## 4. Constraints and Assumptions

- **Assumes** `docs/PLAN.md` exists and follows the convention of sibling plans (Stage 1 / Stage 2 sections, `Task X.Y` enumerator, links to `docs/tasks/task-{ID}-{SubID}-{slug}.md`).
- **Assumes** the existing `/vdd-develop` workflow remains the source of truth for the Sarcasmotron persona overlay. If `/vdd-develop` is renamed or refactored, this workflow must be updated.
- **Verified** `update_state.py` supports `--add_completed_task` and `--add_decision` flags (`grep` against [.agent/skills/skill-session-state/scripts/update_state.py](../.agent/skills/skill-session-state/scripts/update_state.py) on 2026-05-07).
- **No architecture changes** — see ARCHITECTURE.md §3 / §5.1 — workflow is a composition of existing patterns.

## 5. Open Questions

All locked via HITL on 2026-05-07:
- **Q1 (Reject limit) → 3 iterations.** Sarcasmotron is stricter than standard reviewer; 2 escalates noisily, 4+ wastes tokens on stuck tasks.
- **Q2 (Pause semantics) → Default explicit user input `[yes/pause/abort]`; opt-in `--auto-continue=<seconds>` flag for timeout mode.**
- **Q3 (Final regression suite) → Workflow runs it automatically.** End-of-chain consistency check is part of the validation contract; commit decision still belongs to user.
- **Bonus) → Both metrics in final report AND `--dry-run` flag.** Both are low-cost and add retrospective signal / preview value.
