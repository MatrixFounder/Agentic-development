# Technical Specification: Harden loop semantics & cross-harness/LLM portability of `full-robust` and `vdd-enhanced`

### 0. Meta Information
- **Task ID:** 084
- **Slug:** `workflow-loops-portability`
- **Mode:** Framework Upgrade (workflow-file edits only; no code, no skill changes)
- **Type:** Hardening / consistency. Scope = exactly two files named by the operator:
  `.agent/workflows/full-robust.md`, `.agent/workflows/vdd-enhanced.md` (+ registry/docs sync).
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).

### 1. Problem Description
Operator request: verify that `full-robust.md` and `vdd-enhanced.md` use **highly effective
loops** and can run on **different harnesses** (Claude Code / Codex / Cursor / Gemini CLI /
Antigravity) with **different LLMs**.

The framework already has a canonical "effective loop" pattern (established by
`skill-orchestrator-patterns` Stage Cycle, workflows `01/02/03`, `vdd-multi`, and
`vdd-adversarial` objective convergence):

1. **Deterministic gate** — a script exit code / structured verdict, not model self-assessment
   → the loop works with any LLM.
2. **Error feedback** — the gate's error output is fed verbatim into the retry prompt.
3. **Bounded iterations** — explicit max-retry count.
4. **Explicit escalation** — on exhaustion: STOP and ask the user; never silently proceed.
5. **Objective convergence bar** for adversarial loops — terminate on "0 critical, only
   bikeshedding remains", never because the critic was forced to invent nitpicks.
6. **Checkpoint at phase boundaries** — `update_state.py` persists state so a loop survives
   context resets (critical for smaller-context models and harness restarts).
7. **Vendor dispatch** — invocation via workflow *file paths* (portable), slash commands as
   Claude-Code-only aliases; role calls via native subagent spawn OR sequential role-switch
   fallback (`skill-parallel-orchestration` §1, §7).

**Audit findings (evidence, per file):**

`full-robust.md` — fails the pattern almost entirely:
- **F1 (loops):** three linear steps; no gates, no verdict propagation, no failure branches.
  If `/vdd-enhanced` escalates or the security audit finds CRITICAL blockers, behavior is
  undefined.
- **F2 (stale):** description says "(future) Security audit" while Step 2 already calls the
  existing `/security-audit` workflow.
- **F3 (invocation drift):** "Call /vdd-enhanced" — no such command exists; the Claude Code
  command is `/vdd` (`.claude/commands/vdd.md`), and `/full` maps to this very file. On
  non-Claude harnesses slash commands don't exist at all — steps must reference
  `.agent/workflows/*.md` file paths.
- **F4 (portability):** no vendor-dispatch/fallback section, no statement of how steps run on
  harnesses without subagent primitives.
- **F5 (resilience):** no phase-boundary checkpoint reminder.
- **F6 (cross-link drift):** `vdd-multi.md` §Integration says it "can be called from
  `/full-robust` — after base implementation", but `full-robust.md` never mentions it (the
  ab-experiment-075 positioning makes it the coverage/CI-gating tool for exactly this
  "maximum reliability" pipeline — as an opt-in step, not a default).

`vdd-enhanced.md` — Phases 1–2 already implement the pattern well (mechanical
`skill-spec-validator` gates + bounded retries); gaps:
- **F7 (incomplete loop):** Phase 2 loop lacks the escalation clause (Phase 1 has
  "Escalation: … stop and ask User"; Phase 2 ends at "Max 3 retries" with no terminal action).
- **F8 (missing gate):** Phase 3 delegates to `/05-run-full-task` with no stated exit
  criteria. (The sub-workflow's own regression step also lacks an If-Fail branch — out of
  scope here, compensated by a caller-side gate; see Non-Goals.)
- **F9 (unbounded loop):** Phase 4 calls `/vdd-adversarial`, which may recurse indefinitely;
  no outer iteration cap and no reference to the objective-convergence termination bar.
- **F10 (invocation drift):** references `/01-start-feature`, `/02-plan-implementation`,
  `/05-run-full-task` — these are workflow file basenames, not commands (actual commands:
  `/start-feature`, `/plan`, `/develop-all`); role calls ("Call `02_analyst` again") don't
  state the mechanism (subagent spawn vs role-switch).
- **F11 (portability):** no vendor-dispatch section; the workflow's strongest cross-LLM
  property — gates are deterministic scripts, so any model can drive the loop — is
  undocumented.
- **F12 (resilience):** no phase-boundary checkpoint reminder.

### 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features / mapping |
|----|-------------|------|------------------------|
| R1 | `full-robust.md`: explicit gated pipeline | Yes | (a) per-step gate + failure branch (vdd-enhanced escalation → STOP; security CRITICAL/HIGH → bounded remediation loop, max 3, then escalate) [F1]; (b) remove "(future)" staleness, name `/04-update-docs` for the docs step [F2] |
| R2 | `full-robust.md`: cross-harness & cross-LLM portability | Yes | (a) portable invocation (file path + Claude Code alias in parentheses) [F3]; (b) `## Vendor dispatch & model portability` section referencing `skill-parallel-orchestration` §1/§7 — no duplication of its tables [F4]; (c) phase-boundary checkpoint note (`update_state.py`) [F5] |
| R3 | `full-robust.md`: optional `/vdd-multi` coverage gate | Yes | one opt-in step (e.g. `--no-fix --fail-on=high`) restoring the cross-link that `vdd-multi.md` §Integration already declares; marked optional per 075 positioning [F6] |
| R4 | `vdd-enhanced.md`: complete the loops | Yes | (a) Phase 2 escalation clause, parity with Phase 1 [F7]; (b) Phase 3 caller-side gate: full regression must pass; on fail re-enter dev loop (max 2) then escalate [F8]; (c) Phase 4 outer cap (max 3 adversarial cycles) + objective-convergence bar reference [F9] |
| R5 | `vdd-enhanced.md`: cross-harness & cross-LLM portability | Yes | (a) portable invocation names (file paths + real command aliases) [F10]; (b) `## Vendor dispatch & model portability` section + explicit "gates are mechanical ⇒ model-agnostic" statement [F11]; (c) phase-boundary checkpoint note [F12] |
| R6 | Registry & docs sync | Yes | (a) `System/Docs/WORKFLOWS.md` rows for Full Robust / VDD Enhanced updated if wording changes; (b) CHANGELOG (EN+RU) entry; (c) audit artifact `docs/reviews/framework-audit-084.md` |
| R7 | Safety invariants | Yes | (a) backups of both workflow files to `.agent/archive/` before edit; (b) no changes to any other workflow/skill/prompt/bootstrap file **except the R8 scope expansion**; (c) gates green: `validate_skill.py` suite, `pytest`; (d) no archiving of living docs |
| R8 | **Scope expansion (operator, mid-execution: "fix follow ups that you've marked")** — fix the three follow-ups recorded during verification | Yes | (a) `tests/test_product_scripts.py`: stale `System/scripts` import path → `load_module_from_path` from the skills' script paths (repo pattern from `test_product_skills.py`); (b) `tests/test_product_skills.py::test_wsjf_calculation_logic`: old 3-tuple row shape → the script's actual `(line, cells)` contract; (c) `.agent/workflows/05-run-full-task.md` Finalization: add the missing If-Fail branch (bounded fix loop max 2 → escalate; never commit on red) + WORKFLOWS.md row sync |
| R9 | **Scope expansion 2 (operator: "почини их")** — fix the second-round follow-ups recorded in the execution-verify audit | Yes | (a) phantom slash-commands → portable file-path + real-alias form in `base-stub-first.md`, `light-01-start-feature.md` (incl. the nonexistent `/light-02-develop-task`), `light-02-develop-task.md`; (b) `tests/test_mock_agent.py` → pytest `tmp_path` output (no more writes into `docs/tasks/`), tracked test artifact `docs/tasks/mock_results/` removed from git; (c) `calculate_wsjf` docstring aligned with the actual signature/return (list of dicts, exit-1 behavior) |
| R10 | **Scope expansion 3 (operator: "это тоже исправь")** — bound the light-mode loops (audit §5 observation) | Yes | `light-02-develop-task.md`: (a) dev test-fix loop → **max 3 fix-and-rerun attempts** (validator-retry convention); (b) review loop → **max 2 review cycles** (reviewer convention); (c) Escalation trigger extended to cover bound exhaustion (repeated failures ⇒ task not trivial ⇒ standard pipeline); (d) WORKFLOWS.md Light Mode row sync |

### 3. Use Cases
- **UC1 (Claude Code user):** runs `/full` → each step states its gate, failure branch, and
  bound; a failed security remediation loop escalates instead of looping forever or silently
  finishing.
- **UC2 (Codex/Cursor/Gemini/Antigravity orchestrator):** reads the workflow file (no slash
  commands available) → every "Call X" resolves to a readable `.agent/workflows/*.md` path,
  and the vendor-dispatch section says how role calls map on that runtime.
- **UC3 (any LLM, incl. smaller-context models):** the loops' pass/fail decisions come from
  script exit codes and structured verdicts, not model self-grading; phase-boundary
  checkpoints let a fresh session resume mid-pipeline.

### 4. Acceptance Criteria
- [ ] AC1: Every step in both workflows has: gate condition, bounded retry (where a loop
  exists), and explicit escalation path. No loop is unbounded; no failure path is undefined.
- [ ] AC2: No references to non-existent slash commands remain; every sub-workflow reference
  includes its `.agent/workflows/*.md` path; Claude Code aliases shown as parenthetical.
- [ ] AC3: Both files contain a vendor-dispatch/model-portability section that references
  `skill-parallel-orchestration` (no duplicated vendor tables — SOT preserved).
- [ ] AC4: `full-robust.md` no longer says "(future)"; optional `/vdd-multi` gate present and
  marked opt-in with 075 rationale.
- [ ] AC5: `vdd-enhanced.md` Phase 2 has an escalation clause; Phase 3 has an explicit gate;
  Phase 4 has an outer cap + objective-convergence reference.
- [ ] AC6: `System/Docs/WORKFLOWS.md` + CHANGELOG updated; audit artifact exists;
  `validate_skill.py` and `pytest` suites green; `git diff --stat` touches only the declared
  files.

### 5. Non-Goals / Out of Scope
- Editing sub-workflows (`01/02/03`, `vdd-adversarial`, `security-audit`, `vdd-multi`).
  ~~The missing If-Fail branch in `05-run-full-task.md` Finalization is recorded as a
  follow-up recommendation, compensated by the caller-side gate (R4b).~~ **Superseded by
  R8c**: the operator requested the marked follow-ups be fixed in this task.
- Any change to `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `System/Agents/*`, skills, or code.
- Parallel-execution redesign (`/vdd-multi` internals) — only the opt-in cross-link (R3).

### 6. Open Questions
- None blocking. (Scope was explicitly fixed by the operator to the two named files.)

### 7. Migration
- None required: workflows are read fresh at each invocation; no session state format
  changes; no wrapper regeneration (no SOT paths renamed).
