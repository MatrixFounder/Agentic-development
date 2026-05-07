# Task 061-02 — Logic: fill workflow body

**Parent**: [docs/PLAN.md](../PLAN.md) — `/vdd-develop-all` epic
**Stage**: 2 — Logic (Implementation phase per `tdd-stub-first`)
**Predecessor**: Task 061-01 (stubs must exist and parse)
**Successor**: Task 061-03

## Goal

Replace every `<stub>` in `.agent/workflows/vdd-05-run-full-task.md` with concrete instructions that satisfy all 11 acceptance bullets from [TASK.md §2 Issues I1.1–I1.9](../TASK.md). Reference SOTs (skills, agent prompts, sibling workflows). DRY — do not inline the Sarcasmotron persona.

## Detailed content per step

### Step 1 — Plan parsing (TASK Issue I1.2)
- Read `docs/PLAN.md`. Extract ordered task list (`Task X.Y` enumerator) with paths to `docs/tasks/task-{ID}-{SubID}-{slug}.md`.
- Respect Stage 1 / Stage 2 sectioning and dependency order.
- Reference [`skill-spec-validator`](../../.agent/skills/skill-spec-validator/SKILL.md) for PLAN ↔ TASK conformance check before iteration.
- **`--dry-run` flag**: print planned chain (task IDs in order) and exit; no execution, no state writes.

### Step 2 — Per-task VDD cycle (TASK Issue I1.3)
- **Step A — Builder**: implement task per [System/Agents/08_developer_prompt.md](../../System/Agents/08_developer_prompt.md) and [`tdd-stub-first`](../../.agent/skills/tdd-stub-first/SKILL.md) (Stub → Logic).
- **Step B — Verification**: run `bash tests/test_e2e.sh` (or per-skill equivalent), unit-test discovery, `validate_skill.py` where the task touches `.agent/skills/`. **Red tests force a Builder loop before Sarcasmotron** (load-bearing — do not roast a broken build).
- **Step C — Sarcasmotron-roast**: **delegate to [.agent/workflows/vdd-03-develop.md](vdd-03-develop.md) Step 3** (DRY — do not inline the persona overlay).
- **Step D — Refinement loop**:
  - REJECTED → return to Step A.
  - **Max 3 iterations** (rationale: Sarcasmotron is stricter than standard reviewer; 2 escalates noisily, 4+ wastes tokens on stuck tasks).
  - 3rd consecutive REJECTED → STOP, escalate to user with digest of findings.
  - APPROVED (incl. Hallucination Convergence) → merge task, persist session-state.

### Step 3 — HITL gate between tasks (TASK Issue I1.4)
- After each merged task, emit one-page digest:
  ```
  Task X.Y merged. Verdict: APPROVED via {Hallucination Convergence | clean approval}.
  {N} {LOW/MED} findings polished. Iterations: {k}/3.
  Continue to Task X.Y+1? [yes / pause / abort]
  ```
- **Default**: explicit user input required (no timeout).
- **Optional**: `--auto-continue=<seconds>` flag → timeout-based auto-continue (off by default).
- `pause` → leave `.agent/sessions/latest.yaml` resumable, stop chain.
- `abort` → stop chain, no commit, summary report.

### Step 4 — Session-state persistence (TASK Issue I1.5)
- After every merge: `python3 .agent/skills/skill-session-state/scripts/update_state.py --mode "vdd-develop-all" --task "<TaskName>" --status "merged" --add_completed_task "<TaskName>"`.
- Critical decisions via `--add_decision` (e.g., `"Approved via Hallucination Convergence on iteration 2"`).
- Reference [`.agent/skills/skill-session-state/SKILL.md`](../../.agent/skills/skill-session-state/SKILL.md) §3–§4.

### Step 5 — Finalization (TASK Issue I1.6)
- Run full regression suite: `bash tests/test_e2e.sh` + unit-test discovery + `validate_skill.py` across changed skills.
- Final report to user:
  - Merged tasks list.
  - **Metrics**: total merged | total REJECTED iterations | Hallucination-Convergence APPROVED count vs honest APPROVED count.
  - `git status` snapshot.
- **Anti-pattern (verbatim in workflow)**: *"Auto-commit is forbidden. Commit/PR decision belongs to the user. This is the load-bearing difference from `/develop-all`."*

### `## Resumability` section (TASK Issue I1.7)
- Re-invoking `/vdd-develop-all` after `pause` reads `.agent/sessions/latest.yaml`, finds first non-merged task in `docs/PLAN.md`, resumes from Step 2 of cycle for that task.
- Cross-link to [`skill-session-state` §2 (Boot Protocol)](../../.agent/skills/skill-session-state/SKILL.md).
- **Smoke test** documented inline: invoke chain, send `pause` after task 1.1 merge, re-invoke; verify resumption at task 1.2 Step 2 (not restart from 1.1).

### `## Fallback` section (TASK Issue I1.8)
- Reference [`skill-parallel-orchestration`](../../.agent/skills/skill-parallel-orchestration/SKILL.md) Layer A / Layer B decision rule.
- Note: on Gemini CLI / Cursor, workflow degrades to sequential role-switching with the same step structure.

### `## Example invocation` section (TASK Issue I1.9)
- Two examples:
  ```text
  /vdd-develop-all                          # full chain, explicit HITL between tasks
  /vdd-develop-all --dry-run                # preview only, no execution
  /vdd-develop-all --auto-continue=300      # auto-continue after 5min if no input
  ```

## RTM (acceptance criteria)

- `[R1]` All 11 Issue acceptance bullets from TASK.md §2 satisfied — verifiable via grep against the workflow file.
- `[R2]` Sarcasmotron persona text NOT inlined — workflow contains a reference to `/vdd-develop` Step 3, not the persona overlay text.
- `[R3]` `Max 3 iterations` literal phrase present (or equivalent unambiguous limit).
- `[R4]` `Auto-commit is forbidden` (or semantic equivalent) literal phrase present in Step 5.
- `[R5]` `--dry-run` and `--auto-continue` flags both documented.
- `[R6]` All cross-links point to existing files (no broken references).
- `[R7]` Workflow file ≤ ~150 lines (soft guidance — flagged but not blocking).

## Verification

```bash
W=.agent/workflows/vdd-05-run-full-task.md

# R2 — DRY (no inlined persona)
! grep -q "You are Sarcasmotron" "$W"      # must be ABSENT
grep -q "vdd-03-develop" "$W"              # cross-link present
grep -q "Sarcasmotron" "$W"                # name referenced (OK)

# R3 — 3-iteration limit
grep -qE '3 iterations|max.{0,5}3|3rd consecutive' "$W"

# R4 — no-auto-commit
grep -qiE 'auto.commit.{0,20}(forbidden|prohibited|never)' "$W"

# R5 — flags
grep -q '\-\-dry-run' "$W"
grep -q '\-\-auto-continue' "$W"

# R6 — all referenced files exist
for f in $(grep -oE '\.agent/[^)]+|System/[^)]+|docs/[^)]+' "$W" | sort -u); do
  test -e "$f" || echo "BROKEN: $f"
done

# R7 — soft line budget
wc -l "$W"   # should be ≤ ~150
```

## Out of scope

- Updating CLAUDE.md or `vdd-03-develop.md` — that's Task 061-03.
- Implementing actual chain runtime — workflow is descriptive instructions for the orchestrator at execution time, not executable code.
