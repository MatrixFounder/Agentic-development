---
description: Execute all tasks in PLAN.md with adversarial Sarcasmotron review (no auto-commit)
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: Adversarial chain. **Auto-commit is forbidden.** Resumable via session-state.

This workflow composes `/develop-all` (chain iteration) with `/vdd-develop` (Sarcasmotron adversarial loop). Load-bearing differences from `/develop-all`: per-task adversarial review, mandatory inter-task HITL gate, **no auto-commit ever**, hard escalation after 3 consecutive REJECTED iterations, and resumability from `.agent/sessions/latest.yaml`.

1. **Plan parsing**: Read `docs/PLAN.md`. Extract the ordered task list (`Task X.Y`) with paths to `docs/tasks/task-{ID}-{SubID}-{slug}.md`. Respect Stage 1 / Stage 2 sectioning and dependency order. Apply `skill-spec-validator` for PLAN ↔ TASK conformance before iteration. **Flag `--dry-run`**: if present, print the planned chain (task IDs in dependency order) and exit; no execution, no state writes.
2. **Per-task VDD cycle** (apply for each task in dependency order):
   - Step A — Builder: implement per `System/Agents/08_developer_prompt.md` + `tdd-stub-first` (Stub → Logic). Strict adherence to the task file; no creative reinterpretation.
   - Step B — Verification: run `python3 tests/run_tests.py` (the project test harness; or `pytest tests/` if available) and `validate_skill.py` where the task touches `.agent/skills/`. **Red tests force a Builder loop before Sarcasmotron** — never roast a broken build.
   - Step C — Sarcasmotron-roast: **delegate to `.agent/workflows/vdd-03-develop.md` Step 3** (DRY — do not inline the persona overlay here). Adopt the persona exactly as defined there, then return a verdict: REJECTED or APPROVED (incl. Objective Convergence).
   - Step D — Refinement loop:
     - REJECTED → return to Step A. **Max 3 iterations.**
     - On the 3rd consecutive REJECTED → STOP. **Persist failure to session-state** via Step 4 with `--status "failed_sarcasmotron" --add_blocker "Task <name>: 3 REJECTED iterations"`, then escalate to user with a digest of findings (no silent retry — escalation is a feature).
     - APPROVED (incl. Objective Convergence) → merge task, **then call Step 4 (persist) → then Step 3 (HITL gate) → then loop to next task**. Order is load-bearing: persist BEFORE the HITL prompt so a runner crash during user wait does not lose merge state.
3. **HITL gate (between tasks)**: After each merged task, emit a one-page digest:
   ```
   Task X.Y merged. Verdict: APPROVED via {Objective Convergence | clean approval}.
   {N} {LOW/MED} findings polished. Iterations: {k}/3.
   Continue to Task X.Y+1? [yes / pause / abort]
   ```
   **Default mode**: explicit user input required (no timeout). **Optional**: `--auto-continue=<seconds>` flag enables timeout-based auto-continue (off by default). `pause` → stop chain, leave state resumable. `abort` → stop chain, no commit, jump to Step 5 summary report.
4. **Session-state persistence** (called from Step 2D — both APPROVED and 3-REJECTED-STOP paths). After each merge:
   ```bash
   python3 .agent/skills/skill-session-state/scripts/update_state.py \
     --mode "vdd-develop-all" --task "<TaskName>" --status "merged" \
     --add_completed_task "<TaskName>" \
     --add_decision "<verdict-detail>"
   ```
   See `.agent/skills/skill-session-state/SKILL.md` §3–§4. This is load-bearing for resumability — do not skip.
5. **Finalization (no auto-commit)**: At chain end (all tasks merged, or chain aborted/paused), run the full regression suite: `python3 tests/run_tests.py` + `validate_skill.py` across changed skills. Emit a final report containing:
   - Merged tasks list (in order).
   - **Metrics**: total tasks merged | total REJECTED iterations across the chain | count of post-refinement APPROVED (`Objective Convergence` reached after ≥1 REJECT) vs first-pass clean APPROVED.
   - Current `git status` snapshot.

   **Auto-commit is forbidden.** Commit/PR decision belongs to the user. This is the load-bearing difference from `/develop-all`.

## Resumability
Re-invoking `/vdd-develop-all` after `pause` reads `.agent/sessions/latest.yaml` (see `.agent/skills/skill-session-state/SKILL.md` §2 Boot Protocol), identifies the first non-merged task in `docs/PLAN.md` by checking `completed_tasks`, and resumes from Step 2 (Step A) for that task.

**Behavioral smoke test**: invoke `/vdd-develop-all`, send `pause` after Task 1.1 merges, then re-invoke `/vdd-develop-all`. Chain must resume at Task 1.2 Step A — not restart from Task 1.1.

## Fallback (vendor-agnostic)
Per `.agent/skills/skill-parallel-orchestration/SKILL.md` §4 (Layer A vs Layer B decision rule). On Claude Code, Step C's Sarcasmotron persona may be dispatched via the `Agent` tool (Layer A) for context isolation, or executed inline as role-switching (Stage Cycle). On Gemini CLI / Cursor, the workflow degrades to sequential role-switching with the same step structure — same artifacts, same gate semantics.

## Example invocation
```text
/vdd-develop-all                          # full chain, explicit HITL between tasks
/vdd-develop-all --dry-run                # preview the planned chain only, no execution
/vdd-develop-all --auto-continue=300      # auto-continue after 5min if no input at HITL gate
```
