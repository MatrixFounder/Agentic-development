# Implementation Plan — `/vdd-develop-all` workflow (Task 061)

**Parent**: [docs/TASK.md](TASK.md) — VDD Chain Workflow
**Mode**: VDD (Verification-Driven Development)
**Architecture impact**: none (composition of existing Layer A / Stage Cycle patterns — see [ARCHITECTURE.md §3, §5.1](ARCHITECTURE.md#3-workflow-logic-v31)).

## Goal

Decompose TASK.md (3 Epics, 11 Issues) into atomic, verifiable Beads under Stub-First discipline. Each Bead is small enough to be verified by a single test case (file existence, grep pattern, structural check, or behavioral smoke).

## Stages

### Stage 1 — Structure (Stubs phase)

**Goal**: All artifact files exist with valid frontmatter and skeleton structure. No content beyond placeholders. Verifies "structure is correct before logic".

| Task | File | Beads | Test |
|------|------|-------|------|
| **Task 061-01** | [tasks/task-061-01-workflow-stubs.md](tasks/task-061-01-workflow-stubs.md) | Scaffold `.agent/workflows/vdd-05-run-full-task.md` (frontmatter + 5 numbered step headings + section placeholders); create `.claude/commands/vdd-develop-all.md` matching the `vdd-develop.md` / `develop-all.md` template. | Files exist, frontmatter parses, 5 step headings present, slash-command template body matches sibling commands verbatim. |

### Stage 2 — Logic (Implementation phase)

**Goal**: Fill workflow content per all FRs in TASK.md. Cross-links wired. Bonus features (`--dry-run`, metrics) included.

| Task | File | Beads | Test |
|------|------|-------|------|
| **Task 061-02** | [tasks/task-061-02-workflow-impl.md](tasks/task-061-02-workflow-impl.md) | Fill all 5 numbered steps (Plan parsing, Per-task VDD cycle A→D, HITL gate, Session-state persistence, Finalization); add `## Resumability`, `## Fallback`, `## Example invocation`; reference `/vdd-develop` for Sarcasmotron persona (DRY); explicit anti-pattern callouts (no auto-commit, no silent retry, no skip Step B). | All 11 Issue acceptance criteria from TASK.md satisfied (grep-verifiable for each phrase + file structure). |

### Stage 3 — Integration (Cross-links & registry)

**Goal**: New workflow discoverable from existing entry points. No regressions in surrounding workflows.

| Task | File | Beads | Test |
|------|------|-------|------|
| **Task 061-03** | [tasks/task-061-03-cross-links.md](tasks/task-061-03-cross-links.md) | Update [CLAUDE.md](../CLAUDE.md) `## WORKSPACE WORKFLOWS` → "Available Commands" list to include `/vdd-develop-all`; append cross-link note at end of [.agent/workflows/vdd-03-develop.md](../.agent/workflows/vdd-03-develop.md). | `grep -c '/vdd-develop-all' CLAUDE.md` ≥ 1; tail of `vdd-03-develop.md` contains the cross-link sentence; sibling workflows untouched (`git diff --stat .agent/workflows/` shows only the two expected files). |

## Dependency order

```
061-01 (stubs)  ──►  061-02 (logic)  ──►  061-03 (cross-links)
   │                     │                       │
   └─ test: files exist  └─ test: content        └─ test: registry
      + frontmatter         covers all 11           updated, no
      valid                 acceptance bullets      regressions
```

**Strict serial**: 061-02 cannot start until 061-01 produces a parseable skeleton; 061-03 cannot start until 061-02 lands the canonical workflow file (otherwise the cross-link in `vdd-03-develop.md` would point at a missing file).

## Verification (chain-end)

Run after Task 061-03 merges:

1. **Structural**:
   ```bash
   ls .agent/workflows/vdd-05-run-full-task.md  # exists
   ls .claude/commands/vdd-develop-all.md       # exists
   head -3 .agent/workflows/vdd-05-run-full-task.md | grep '^description:'  # frontmatter
   ```

2. **Coherence** (no broken links):
   ```bash
   grep -c '/vdd-develop-all' CLAUDE.md                        # ≥ 1
   grep -c '/vdd-develop-all' .agent/workflows/vdd-03-develop.md  # ≥ 1
   grep -c 'vdd-03-develop' .agent/workflows/vdd-05-run-full-task.md  # ≥ 1 (Sarcasmotron DRY ref)
   ```

3. **No regression**: existing `/vdd-develop`, `/develop-all`, and other workflows untouched.

## Out of scope for v1

- Implementing or testing the workflow's runtime logic against a real PLAN.md chain — that requires a live PLAN with multiple tasks and a Sarcasmotron pass to actually execute. Validation is **structural and documentary** in this epic.
- Auto-generation of metrics — workflow text describes what to count; counting itself is the orchestrator's responsibility at runtime.
- Migration of any existing tasks to use `/vdd-develop-all` — opt-in only, no auto-replacement of `/develop-all` callsites.
