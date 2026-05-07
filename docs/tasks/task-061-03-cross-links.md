# Task 061-03 — Integration: cross-links and registry

**Parent**: [docs/PLAN.md](../PLAN.md) — `/vdd-develop-all` epic
**Stage**: 3 — Integration
**Predecessor**: Task 061-02 (workflow body must be complete — otherwise the cross-link in `vdd-03-develop.md` would point at a stub)
**Successor**: none (final task in chain)

## Goal

Make `/vdd-develop-all` discoverable from the existing entry points without regressing surrounding documentation.

## Files to update

### 1. `CLAUDE.md` — `## WORKSPACE WORKFLOWS` block

Locate the line listing Available Commands (currently includes `/develop-all`, `/vdd-develop`, `/vdd-multi`, etc.) and insert `/vdd-develop-all` in the natural alphabetical/grouped position next to `/develop-all` and `/vdd-develop`.

**Constraint**: edit ONLY the Available Commands list. Do NOT modify any other CLAUDE.md section.

### 2. `.agent/workflows/vdd-03-develop.md` — trailing cross-link note

Append one line at the end of the file:
```markdown

> **Для прогона всей цепочки задач — см. `/vdd-develop-all` (`.agent/workflows/vdd-05-run-full-task.md`).**
```

**Constraint**: append-only. Do NOT modify the existing 4 numbered steps or the persona overlay text.

## RTM (acceptance criteria)

- `[R1]` `/vdd-develop-all` appears in `CLAUDE.md` `## WORKSPACE WORKFLOWS` Available Commands list.
- `[R2]` Trailing cross-link note appended to `.agent/workflows/vdd-03-develop.md`.
- `[R3]` No regressions in surrounding workflows: `git diff --stat .agent/workflows/` shows changes ONLY in `vdd-03-develop.md` (and the new `vdd-05-run-full-task.md` from Task 061-02).
- `[R4]` No regressions in CLAUDE.md outside the Available Commands list: `git diff CLAUDE.md` shows a single-line addition to that list (modulo trivial reflow).

## Verification

```bash
# R1 — registered in CLAUDE.md
grep -c '/vdd-develop-all' CLAUDE.md   # ≥ 1
grep -A2 -B1 'Available Commands' CLAUDE.md | grep -q '/vdd-develop-all'

# R2 — cross-link appended
tail -3 .agent/workflows/vdd-03-develop.md | grep -q 'vdd-develop-all'

# R3 — no other workflow regressions
git diff --stat .agent/workflows/ | grep -E '^\s*\.agent/workflows/(vdd-03-develop|vdd-05-run-full-task)\.md' | wc -l  # → 2
git diff --stat .agent/workflows/ | grep -vE '(vdd-03-develop|vdd-05-run-full-task)\.md' | grep -E '^\s*\.' | wc -l   # → 0

# R4 — CLAUDE.md change minimal
git diff --stat CLAUDE.md   # 1 file changed, small line delta
```

## Out of scope

- Adding `/vdd-develop-all` to other docs (README.ru.md, ROADMAP.md, etc.) — out of scope for v1; can be a follow-up if discoverability gaps emerge.
- Updating ARCHITECTURE.md — workflow is composition of existing patterns, no architectural delta (decided in Analysis phase).
