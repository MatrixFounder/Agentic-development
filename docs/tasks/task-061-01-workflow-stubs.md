# Task 061-01 — Stubs: scaffold workflow file + slash command

**Parent**: [docs/PLAN.md](../PLAN.md) — `/vdd-develop-all` epic
**Stage**: 1 — Structure (Stubs phase per `tdd-stub-first`)
**Predecessor**: none
**Successor**: Task 061-02

## Goal

Create the **skeleton** of the new workflow file and its slash-command stub. No content beyond frontmatter and section headings — Stage 2 fills the body.

## Files to create

### 1. `.agent/workflows/vdd-05-run-full-task.md`

Skeleton:
```markdown
---
description: Execute all tasks in PLAN.md with adversarial Sarcasmotron review (no auto-commit)
---
> [!IMPORTANT]
> **VDD MODE ACTIVE**: Adversarial chain. No auto-commit. Resumable.

1. **Plan parsing**: <stub>
2. **Per-task VDD cycle**: <stub>
   - Step A — Builder: <stub>
   - Step B — Verification: <stub>
   - Step C — Sarcasmotron-roast: <stub>
   - Step D — Refinement loop: <stub>
3. **HITL gate (between tasks)**: <stub>
4. **Session-state persistence**: <stub>
5. **Finalization (no auto-commit)**: <stub>

## Resumability
<stub>

## Fallback (vendor-agnostic)
<stub>

## Example invocation
<stub>
```

### 2. `.claude/commands/vdd-develop-all.md`

Body — copy the template used by `vdd-develop.md` and `develop-all.md` verbatim, adjusting only the workflow path:
```markdown
Read and execute the workflow defined in `.agent/workflows/vdd-05-run-full-task.md`.

Follow all steps sequentially. Load required skills as specified in each step.
Apply all Global Protocols (skill-archive-task, skill-session-state).

User's task context:
$ARGUMENTS
```

## RTM (acceptance criteria)

- `[R1]` `.agent/workflows/vdd-05-run-full-task.md` exists.
- `[R2]` Frontmatter present (`description:` line) and parses (no missing `---` fences).
- `[R3]` Exactly **5 numbered top-level steps** present (`^[1-5]\. `).
- `[R4]` Sub-steps A/B/C/D present under step 2.
- `[R5]` Three named sections present: `## Resumability`, `## Fallback`, `## Example invocation`.
- `[R6]` `.claude/commands/vdd-develop-all.md` exists.
- `[R7]` Slash-command body matches the structure of `develop-all.md` / `vdd-develop.md` (same boilerplate sentence, same `$ARGUMENTS` token).

## Verification

```bash
# R1, R6 — file existence
test -f .agent/workflows/vdd-05-run-full-task.md
test -f .claude/commands/vdd-develop-all.md

# R2 — frontmatter
head -3 .agent/workflows/vdd-05-run-full-task.md | grep -q '^description:'

# R3 — 5 numbered steps
grep -cE '^[1-5]\. ' .agent/workflows/vdd-05-run-full-task.md   # → 5

# R4 — sub-steps
grep -cE '^   - Step [A-D]' .agent/workflows/vdd-05-run-full-task.md  # → 4

# R5 — required sections
grep -cE '^## (Resumability|Fallback|Example invocation)' .agent/workflows/vdd-05-run-full-task.md  # → 3

# R7 — slash-command boilerplate
diff <(sed 's/vdd-05-run-full-task/05-run-full-task/' .claude/commands/vdd-develop-all.md) .claude/commands/develop-all.md
# → byte-identical except the workflow path
```

## Out of scope

- Filling the `<stub>` placeholders — that's Task 061-02.
- Updating CLAUDE.md or `vdd-03-develop.md` — that's Task 061-03.
