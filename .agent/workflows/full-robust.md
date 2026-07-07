---
description: Run the full robust pipeline (Stub-First + VDD + Security) with bounded, gated loops
---
# Workflow: Full Robust Development

**Description:**
Maximum reliability: Hardened VDD pipeline + opt-in multi-critic coverage gate + Security audit.
Every step below is a **gate**: proceed only on PASS. Every retry loop is **bounded** with an
explicit escalation path — never loop silently, never proceed past an undefined failure.

> [!IMPORTANT]
> **Loop protocol (applies to every step):**
> 1. Gates are **objective and externally checkable** — deterministic script exit codes and
>    test runs, plus structured PASS/FAIL review verdicts against written bars — never
>    free-form model self-assessment. Any LLM can drive this pipeline.
> 2. On a gate failure, feed the gate's error output **verbatim** into the retry.
> 3. After each step, persist state (global protocol):
>    `python3 .agent/skills/skill-session-state/scripts/update_state.py ...` — a fresh
>    session resumes mid-pipeline from `.agent/sessions/latest.yaml`.

**Steps:**

1. **Hardened VDD pipeline** — execute `.agent/workflows/vdd-enhanced.md` (Claude Code alias: `/vdd`).
   - Context: Load Skill `tdd-strict` (High Assurance Mode).
   - Already nested inside: analysis/planning validation loops + development + adversarial review.
   - **Gate:** all 4 phases completed without escalating to the user. If one of its bounded
     loops exhausted and escalated, this pipeline is already STOPPED — resolve with the user
     before re-entering; do NOT proceed to Step 2.

2. **Coverage gate (OPT-IN)** — execute `.agent/workflows/vdd-multi.md` with
   `--no-fix --fail-on=high` (alias: `/vdd-multi`).
   - Run only when the operator requests a coverage-critical / pre-release pass. Per
     ab-experiment-075, `/vdd-multi` is a coverage & CI-gating tool (highest pooled recall at
     ~3× tokens), **not** the default review path — Step 1 already contains the default
     adversarial review.
   - **Gate:** verdict PASS. On FAIL: persist the merged report
     (`--output=docs/reviews/coverage-<task-id>.md`), materialize the ≥threshold findings as
     one fix-task file `docs/tasks/task-<ID>-coverage-fixes.md` (one checklist item per
     finding, citing the report), execute `.agent/workflows/03-develop-single-task.md`
     (alias: `/develop`) with that task file as its input, then re-run the coverage gate
     **once**; still FAIL → STOP and escalate the remaining findings to the user.

3. **Security audit** — execute `.agent/workflows/security-audit.md` (alias: `/security-audit`).
   - **Gate:** the automated scan exits clean AND the manual review (per the
     `security-audit` skill §3 checklists) emits a severity-labelled findings table with
     **no CRITICAL/HIGH findings**.
   - **Bounded remediation:** the sub-workflow's "fix → re-run audit until clean" loop is
     re-scoped HERE at the caller: "clean" = the gate above (no CRITICAL/HIGH) — MEDIUM/LOW
     leftovers are recorded in the audit report and do **not** trigger further iterations.
     **Max 3 iterations**; on exhaustion with CRITICAL/HIGH still open → STOP and escalate
     the open findings to the user.

4. **Documentation update** — execute `.agent/workflows/04-update-docs.md` (alias: `/update-docs`).
   - **Gate:** every sub-step completes without error and with no unresolved doc/code
     mismatch (task rotation, architecture check, `.AGENTS.md` scopes current).
   - **Bounded retry:** on failure, feed the error output verbatim into **one** retry of the
     failed sub-step; still failing → STOP and escalate — do not announce `Docs ✓`.

**Completion:** announce
`Full Robust pipeline complete: VDD ✓ · Coverage ✓|skipped · Security ✓ · Docs ✓`
— or name the step and gate where the pipeline stopped, with the escalated findings.

## Vendor dispatch & model portability

- **Invocation:** on any harness, "execute a workflow" = **read the referenced
  `.agent/workflows/*.md` file and follow its steps**. Slash commands in parentheses are
  Claude-Code-only aliases (`.claude/commands/`); Codex/Cursor bootstrap via `AGENTS.md`,
  Gemini CLI / Antigravity via `GEMINI.md`.
- **Subagent/role calls** inside the sub-workflows resolve per `skill-parallel-orchestration`
  §1.1 (native adapter per runtime), with sequential role-switching (§7) as the last resort.
  Gates, bounds, and escalation paths are identical on every path — only the spawn mechanism
  changes.
- **Model-agnostic by construction:** script gates (validator, test suite, audit scanner)
  are mechanical; review gates (Step 2 coverage verdict, Step 3 manual-review table) are
  structured judgment verdicts against written bars. Either way, no step depends on a
  vendor-specific model capability. Smaller-context models rely on the per-step state
  checkpoints to resume.
