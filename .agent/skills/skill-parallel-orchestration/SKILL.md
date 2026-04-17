---
name: skill-parallel-orchestration
description: "Use when decomposing tasks into parallel sub-tasks or spawning sub-agents. Vendor-agnostic core; load a per-vendor reference for concrete tool names, directory conventions, and invocation syntax."
tier: 2
version: 3.0
---

# Parallel Orchestration Skill

**Purpose**: vendor-agnostic protocol for the Orchestrator Role to decompose large tasks into independent units and execute them via parallel sub-agent spawning. Specific tool names, directory layouts, and invocation syntax are delegated to per-vendor reference files in `references/`.

---

## 1. Load the right reference (mandatory step — Read tool, now)

Before applying any protocol below, **use the `Read` tool to load the matching reference file now**. Do not proceed to §2 with only this SKILL.md in context — the reference supplies the concrete tool names and invocation syntax that the universal concepts below need to become executable.

### 1.1 Detection

Walk upward from the current working directory toward the filesystem root (or stop at a `.git` boundary if that's closer) and check for vendor markers:

| Runtime indicator (first match wins) | `Read` | Status |
|---|---|---|
| `CLAUDE.md` + `.claude/agents/` present | [`references/claude-code.md`](references/claude-code.md) | Reference implementation (complete, smoke-tested) |
| `GEMINI.md` present, no `.claude/agents/` | [`references/gemini-cli.md`](references/gemini-cli.md) | **Stub** — not yet validated on real runtime |
| `.cursor/` directory present | [`references/cursor.md`](references/cursor.md) | **Stub** — not yet validated on real runtime |
| Antigravity runtime marker present | [`references/antigravity.md`](references/antigravity.md) | **Stub** — not yet validated on real runtime |
| None of the above, or vendor has no parallel-spawn primitive | [`references/sequential-fallback.md`](references/sequential-fallback.md) | Universal-by-design; unvalidated on non-Claude runtimes (see file for caveats) |

If `cwd` is not the project root, walk up looking for the first marker; stop at `.git/` or filesystem root. If no marker found, the skill is being invoked outside a framework-managed project — emit a warning to the caller rather than silently falling back, then load `sequential-fallback.md`.

### 1.2 Tie-break when multiple indicators match

If a repo carries both `CLAUDE.md` and `GEMINI.md` (multi-vendor support), the agent cannot reliably introspect which CLI is hosting it. Use these concrete signals, in order:

1. **Tool-list fingerprint**: if the agent has `Agent` (with `team_name` parameter) + `TeamCreate` + `SendMessage` available — load `claude-code.md`. If it has a Gemini-specific `run_shell_command` or Cursor's Composer primitives — load the matching reference. Tool availability is the most reliable signal.
2. **Explicit caller hint**: if the orchestrator passed a `runtime:` parameter in the skill invocation, honor it.
3. **Fallback**: if still ambiguous, emit a warning "ambiguous runtime; defaulting to sequential-fallback" and load `sequential-fallback.md`. Do not guess silently.

---

## 2. Universal concepts

### 2.1 Roles

- **Orchestrator**: single lead agent that decomposes the task, invokes the parallel-spawn primitive, and merges results. Does **not** execute domain work itself.
- **Teammate**: independent worker with isolated context and an explicit artifact contract. Returns a structured report to the orchestrator; does not write to shared files unless the contract says so.

### 2.2 Two layers

- **Layer A — Parallel independent spawn** (universal). N teammates working on orthogonal pieces. **No mid-work inter-teammate communication**; merge happens after all return. Covers parallel critique, parallel exploration, independent atomic tasks.
- **Layer B — Peer communication** (vendor-dependent). Teammates message each other during work. Required **iff** teammate A's output depends on inspecting teammate B's in-progress state. Examples: security-vs-performance trade-off debate; frontend/backend API-schema negotiation mid-flight. Not all vendors support this natively — see your reference file.

**Decision criterion for Layer A vs B**: use Layer B iff teammates must exchange messages *during* their work (not just in post-hoc merge). Otherwise Layer A.

### 2.3 Three-phase protocol

1. **Decompose**: split the task into independent units with clear artifact contracts. No shared mutable state. No ordering constraints beyond "all-done → merge". Each unit should fit a single teammate's context budget.
2. **Spawn**: invoke all teammates in a **single atomic step** using the vendor's parallel-spawn primitive (see your reference file for syntax). Sequential invocations defeat the purpose.
3. **Merge**: collect structured reports → deduplicate by location (±3 lines) → escalate severity on cross-category overlap → filter hallucinations → emit unified artifact.

---

## 3. Red Flags (anti-rationalization — universal)

- "Sequential for independent tasks saves complexity." → **WRONG**. Slower, and you lose per-teammate context isolation. Use the parallel primitive when the runtime supports it.
- "Cross-pollinate critics' outputs to save tokens." → **WRONG**. Defeats parallel critique — each teammate's independent perspective is the whole point. Merge strictly after all return.
- "One big combined agent call is simpler." → **WRONG**. Separate teammates get separate context windows, stricter tool restrictions, and clearer failure modes. Collapsing them erases those properties.
- "Parallelism is a quality tool." → **WRONG**. Parallelism is a **scalability** tool. More agents ≠ better analysis. Default to 1; fan out only when objectively orthogonal subsystems are identified. See §5.

---

## 4. Best Practices (universal)

| DO | DO NOT |
|---|---|
| Single-invocation parallel spawn | Sequential invocations for independent work |
| Reference an existing teammate definition (by name/type) | Inline a full system prompt when a wrapper exists |
| Clear structured-return contract per teammate | Expect unstructured prose for post-hoc parsing |
| Merge in the orchestrator after all returns | Stream partial outputs between teammates (use Layer B if you genuinely need that) |

---

## 5. Exploration default — ONE

Even if the runtime permits N parallel exploration agents, **default to 1** for first-pass reconnaissance. Fan out to 2–3 only when objectively orthogonal subsystems are identified.

| Case | Default count |
|---|---|
| First-pass reconnaissance ("understand the current state") | **1** |
| Well-scoped single-domain question | **1** |
| Independent subsystems with no shared files (frontend + backend + infra) | **2–3**, one per domain |
| Same area, larger search space | **1** (sharper prompt, not more agents) |

**Why**: three parallel Explores on overlapping scope produce ~3× noise with heavy content overlap, not 3× signal.

**Rule**: parallelism is a last-step optimization for cost/wall-clock applied after scope is understood — not a default exploration tactic.

---

## 6. Merge rules (universal)

After all teammates return, apply these in order:

1. **Location dedup**: issues at the same `(file, line ± 3)` with overlapping category → merge, keep highest severity, union descriptions and recommendations.
2. **Cross-category re-attribution**: if a teammate flagged something belonging to a sibling's domain, re-section under the correct owner's block.
3. **Severity escalation**: two teammates independently flagging the same location → escalate severity by one level (signal that two independent perspectives both see the issue).
4. **Hallucination filter**: any teammate signaling `convergence: hallucinating` → drop its low-severity items from this iteration.
5. **Optional severity filter**: drop items below a user-specified minimum severity (e.g. `--severity=high`).

---

## 7. When a runtime has no parallel primitive

If the active runtime is stub-only (no `Agent` tool, no multi-tool-call, no spawn mechanism), fall back to [`references/sequential-fallback.md`](references/sequential-fallback.md):

- Role-switching through a single session (persona-swap per teammate role).
- Slower by ~N× wall-clock.
- Loses per-teammate context isolation (everything lands in the same session window).
- Functionally equivalent for merge-at-end patterns; **cannot** do Layer B.

All universal concepts (§2–§6) still apply; only the spawn mechanism changes.

> **Caveat**: the fallback protocol is documented as universal-by-design but has only been validated on Claude Code itself (roleplay as a no-`Agent`-tool runtime). Until a real non-Claude runtime runs an end-to-end task through it, treat the fallback as a *proposed pattern* rather than a certified code path. File issues / PRs against `references/sequential-fallback.md` after your first real run.

---

## 8. Scripts and Resources

- `scripts/spawn_agent_mock.py` — **DEPRECATED** (Wave 1, 2026-04-17). POC mock runner. Retained only for `fcntl`-locking regression tests in `tests/test_mock_agent.py`. Do not reference from new workflows.
- `examples/usage_example.md` — Claude Code–specific usage walk-through paired with `references/claude-code.md`.
- `references/` — per-vendor reference implementations. See §1 for selection.

---

## 9. History

- **v3.0 (2026-04-18)**: vendor-agnostic rewrite. Universal concepts (§2–§6) stay in `SKILL.md`; Claude-specific primitives (`Agent` tool, `.claude/agents/`, `subagent_type`, `TeamCreate`/`SendMessage`) extracted to `references/claude-code.md`. Added `references/sequential-fallback.md` as universal fallback and stubs for Gemini CLI, Cursor, Antigravity. Extraction point established for Wave 5 (multi-vendor generator).
- **v2.0 (Wave 1, 2026-04-17)**: replaced mock-spawn with native Claude Code `Agent` tool (Layer A); added Layer B stub. Single-vendor assumption.
- **v1.0 (POC)**: mock-agent via `spawn_agent_mock.py &`. See `docs/archives/POC_PARALLEL_AGENTS.md`.
