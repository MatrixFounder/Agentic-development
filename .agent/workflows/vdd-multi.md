---
description: VDD Multi-Adversarial — parallel critics via Layer-A teammate spawn (Claude Code); sequential fallback on other vendors
---

# Workflow: VDD Multi-Adversarial

Parallel execution of three specialized adversarial critics (logic, security, performance) via Claude Code native subagent-spawn (Layer A). On vendors without `Agent` tool + `.claude/agents/`, falls back to sequential role-switching.

## Invocation

```
/vdd-multi [target] [flags]
```

- `target` — file path, directory, or omitted. If omitted, implies `--diff-only`.
- `flags` — space-separated list of the parameters below.

### Parameters (v3.13.0)

| Flag | Values | Default | Effect |
|---|---|---|---|
| `--scope=<list>` | `logic`, `security`, `performance`, `all`; comma-separated | `all` | Run only the selected critic(s). Accepts e.g. `--scope=security,performance`. Reduces cost when area is known. |
| `--no-fix` | (boolean) | off | Skip Phase 3 iterative fix loop. Report-only mode. Use for CI, smoke tests, pre-merge review bots. |
| `--fail-on=<sev>` | `critical`, `high`, `medium`, `low`, `none` | `none` | Mark the run as **FAIL** (and surface in termination line) if any finding has severity ≥ threshold. Workflow still completes; the flag controls the terminal verdict only. |
| `--output=<path>` | relative or absolute file path | none | Write the merged Phase 2 report to the given path instead of inline. Orchestrator creates the file and returns a short pointer instead of the full markdown. Typical: `--output=docs/reviews/pr-42.md`. |
| `--diff-only` | (boolean) | auto-on if `target` is omitted | Bound the review to files present in `git diff` vs `main` branch. Implied when no target given. Critics receive the changed file paths + per-file diff context, not the entire files. |

### Parameter examples

```
/vdd-multi docs/tasks/task-dummy.md
  → full all-critic run on one file, inline merged report, fix-loop on issues

/vdd-multi src/auth.py --scope=security --fail-on=critical
  → security critic only; CI-style (non-zero verdict on any critical finding)

/vdd-multi --diff-only --no-fix --output=docs/reviews/pr-42.md
  → PR-review mode: all changed files, three critics, report-only, persist to file

/vdd-multi src/ --scope=logic,performance --no-fix
  → skip security (assume already audited), just logic + perf, no fix cycle
```

---

## Pipeline

```
vdd-multi
 ├── Phase 0: Parse invocation (target + flags)
 ├── Phase 1: PARALLEL SPAWN (one tool-use, N subagents per --scope)
 │    ├── critic-logic        → report  (if in scope)
 │    ├── critic-security     → report  (if in scope)
 │    └── critic-performance  → report  (if in scope)
 ├── Phase 2: MERGE & DEDUPLICATE (main orchestrator)
 ├── Phase 3: ITERATIVE FIX LOOP (per-category; skipped if --no-fix)
 └── Termination: verdict (PASS|FAIL per --fail-on); emit report inline or to --output
```

## Prerequisites

- Code must be implemented and functional before running this workflow.
- Claude Code runtime with `.claude/agents/critic-{logic,security,performance}.md` present.
- If subagents unavailable → execute **Fallback (Sequential)** section below.

---

## Phase 0 — Parse invocation

1. Extract `target` (first non-flag token) and all `--flag[=value]` tokens from the invocation string.
2. If no `target` and no `--diff-only` flag → set `--diff-only` implicitly.
3. Validate:
   - `--scope` values must be subset of `{logic, security, performance, all}`; default `all`.
   - `--fail-on` must be one of `{critical, high, medium, low, none}`; default `none`.
   - `--output` parent directory must exist or be creatable (`mkdir -p`).
4. If `--diff-only` active, derive file list via `git diff --name-only main...HEAD` (or `git diff --name-only` for uncommitted). Report the list to the user before spawning.

## Phase 1 — Parallel critic spawn (Layer A)

In a **single assistant message**, invoke `Agent` N times in parallel (N = critics in `--scope`):
- `subagent_type: critic-logic` (if `logic` in scope)
- `subagent_type: critic-security` (if `security` in scope)
- `subagent_type: critic-performance` (if `performance` in scope)

**Prompt skeleton** for each (substitute `{target}` and bounding context):

```
Review the following code for <your-domain> issues and return a structured report per the contract in your teammate definition.

Target: {target}  (plus diff context if --diff-only)
Context: {short description — what this code does, entry points, dependencies}
Focus areas: {optional — narrow the scope}
```

**Constraints**:
- ONE message with N parallel Agent tool-uses, not N sequential messages (Layer A invariant).
- Each critic receives **independent context**; no pre-filter or cross-pollination.
- Do NOT pass critic outputs between critics during Phase 1 — merge happens in Phase 2.

## Phase 2 — Merge & deduplicate

Merge the reports from critics that ran. Apply:

1. **Location dedup**: issues at the same `(file, line ± 3)` with overlapping category → merge, keep highest severity, union descriptions and recommendations.
2. **Cross-category re-attribution**: if a critic flagged something belonging to a sibling's domain, re-section into the correct critic's block.
3. **Severity escalation**: two critics independently flagging the same location → escalate severity by one level.
4. **Hallucination filter**: any critic reporting `convergence: hallucinating` → drop its low-severity items from this iteration.
5. **`--severity` filter** (if present): drop items below the threshold from the merged report (but still count for `--fail-on`).

### Merged report structure

```markdown
# VDD Multi-Adversarial Report — iteration <N>

## Summary
- Critics run: <list, per --scope>
- Total issues (post-dedup): <N>  (critical: <C>, high: <H>, medium: <M>, low: <L>)
- Convergence: <logic=state> · <security=state> · <performance=state>
- Verdict (per --fail-on): PASS | FAIL at <severity>

## Logic issues
<items, post-dedup>

## Security findings
<items, post-dedup>

## Performance findings
<items, post-dedup>

## Overlaps (same location, multiple critics)
<cross-category items with escalated severity>
```

**Output routing**:
- If `--output=<path>` → write the merged report to that file; emit a short pointer inline (`"Merged report written to <path> (verdict: <V>)"`).
- Else → emit the full merged report inline.

## Phase 3 — Iterative fix loop

**Skip entirely if `--no-fix` is set.**

Otherwise, for each non-clean category, apply fixes and re-spawn **only that critic** until:
1. **Clean pass**: no real issues found → category ✓.
2. **Hallucinating**: critic inventing problems → category ✓.
3. **Diminishing returns**: only micro-optimizations remain → category ✓.
4. **Iteration cap** (`--max-iterations` if provided, default unbounded): force-stop and flag in termination.

Re-spawns are single-critic, not full parallel triples.

## Termination

Emit the final line:

> `VDD Multi-Adversarial complete: Logic ✓ Security ✓ Performance ✓ (iterations: L=<Nl>, S=<Ns>, P=<Np>; verdict: <PASS|FAIL>)`

**Verdict** = FAIL iff any finding in the final merged report has severity ≥ `--fail-on` threshold. Default `--fail-on=none` → verdict always PASS.

If `--output` was set, mention the path in the termination line as well.

---

## Fallback (Sequential) — non-Claude-Code vendors

If `Agent` tool or `.claude/agents/` is unavailable, fall back to sequential role-switching:

1. Apply `skill-vdd-adversarial` (role-switch) → fix loop (unless `--no-fix`).
2. Apply `skill-adversarial-security` (role-switch) → fix loop.
3. Apply `skill-adversarial-performance` (role-switch) → fix loop.

Functionally equivalent to Phase 1–3 above but slower (3× wall-clock) and without parallel-context-isolation benefits. All flags (`--scope`, `--no-fix`, `--fail-on`, `--output`, `--diff-only`) honored by the role-switching path.

---

## Integration

This workflow can be called from:
- `/full-robust` — after base implementation.
- Directly via `/vdd-multi` — for existing code review.
- PR/CI bots via `/vdd-multi --diff-only --no-fix --fail-on=high --output=docs/reviews/pr-<N>.md`.
