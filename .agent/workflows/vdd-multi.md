---
description: VDD Multi-Adversarial — parallel critics via Layer-A teammate spawn (Claude Code); sequential fallback on other vendors
---

# Workflow: VDD Multi-Adversarial (Wave 1: parallel)

**Description**:
Parallel execution of three specialized adversarial critics (logic, security, performance) via Claude Code native subagent-spawn (Layer A). On vendors without `Agent` tool + `.claude/agents/`, falls back to sequential role-switching.

**Pipeline**:
```
vdd-multi
 ├── Phase 1: PARALLEL SPAWN (one tool-use, three subagents)
 │    ├── critic-logic        → report
 │    ├── critic-security     → report
 │    └── critic-performance  → report
 ├── Phase 2: MERGE & DEDUPLICATE (main orchestrator)
 └── Phase 3: ITERATIVE FIX LOOP (per-category until clean/hallucinating)
```

---

## Prerequisites

- Code must be implemented and functional before running this workflow.
- Claude Code runtime with `.claude/agents/critic-{logic,security,performance}.md` present.
- If subagents unavailable → execute **Fallback (Sequential)** section below.

---

## Phase 1 — Parallel critic spawn (Layer A)

**Action**: in a **single assistant message**, invoke the `Agent` tool **three times in parallel** with these subagent types:
- `subagent_type: critic-logic`
- `subagent_type: critic-security`
- `subagent_type: critic-performance`

**Prompt skeleton** for each (substitute `{target}` with the file/dir/diff under review):

```
Review the following code for <your-domain> issues and return a structured report per the contract in your teammate definition.

Target: {target}
Context: {short description — what this code does, entry points, dependencies}
Focus areas: {optional — narrow the scope}
```

**Constraints**:
- MUST be one message with three parallel Agent tool-uses, not three sequential messages. Sequential spawn defeats the purpose and loses context-isolation benefits.
- Each critic receives **independent context**; do not pre-filter or pre-summarize — the whole point is orthogonal perspectives.
- Do NOT pass critic outputs between critics during Phase 1. Cross-pollination happens in Phase 2 (merge).

**Expected outputs**: three structured reports (markdown per each teammate's contract) returned to the orchestrator in tool results.

---

## Phase 2 — Merge & deduplicate

**Action**: the main orchestrator merges the three reports.

**Dedup rules**:
1. **Location-based**: issues at the same `(file, line ± 3)` with overlapping category are merged. Keep the highest severity; union the descriptions and recommendations.
2. **Cross-category attribution**: if `critic-logic` flagged something that is really a security or perf issue, re-attribute to the correct critic's section in the merged report.
3. **Severity escalation**: if two critics independently flagged the same location (e.g., perf + security on ReDoS), escalate severity by one level.
4. **Hallucination filter**: if any critic returned `convergence: hallucinating`, drop its low-severity items from this iteration.

**Merged report structure**:
```markdown
# VDD Multi-Adversarial Report — iteration <N>

## Summary
- Total issues: <N>  (critical: <C>, high: <H>, medium: <M>, low: <L>)
- Convergence: logic=<state>  security=<state>  perf=<state>

## Logic issues
<items from critic-logic, post-dedup>

## Security findings
<items from critic-security, post-dedup>

## Performance findings
<items from critic-performance, post-dedup>

## Overlaps (same location, multiple critics)
<cross-category items with escalated severity>
```

---

## Phase 3 — Iterative fix loop

**Action**: for each non-clean category, apply fixes and re-spawn **only that critic** until:
1. **Clean pass**: no real issues found → category ✓.
2. **Hallucinating**: critic inventing problems → category ✓ (convergence signal from SKILL.md methodology).
3. **Diminishing returns**: only micro-optimizations remain → category ✓.

**Important**: re-spawns are single-critic, not full parallel triples (cheaper and faster). Phase 1 parallel-triple is only for the initial scan.

---

## Termination

Workflow terminates when all three categories are ✓. Emit final announcement:

> "VDD Multi-Adversarial complete: Logic ✓ Security ✓ Performance ✓ (iterations: L=<Nl>, S=<Ns>, P=<Np>)"

---

## Fallback (Sequential) — non-Claude-Code vendors

If `Agent` tool or `.claude/agents/` is unavailable, fall back to sequential role-switching:

1. Apply `skill-vdd-adversarial` (role-switch) → fix loop.
2. Apply `skill-adversarial-security` (role-switch) → fix loop.
3. Apply `skill-adversarial-performance` (role-switch) → fix loop.

This is the legacy pre-Wave-1 behavior. Functionally equivalent but slower (3× wall-clock) and without parallel-context-isolation benefits.

---

## Integration

This workflow can be called from:
- `/full-robust` — after base implementation.
- Directly via `/vdd-multi` — for existing code review.
