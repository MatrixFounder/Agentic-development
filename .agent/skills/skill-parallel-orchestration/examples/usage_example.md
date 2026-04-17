# Example: Parallel Orchestration (Layer A — Claude Code reference)

> **Vendor scope**: this example uses Claude Code primitives (`Agent` tool, `.claude/agents/*` wrappers, `subagent_type` parameter). For the vendor-agnostic protocol see the parent [`SKILL.md`](../SKILL.md); for the Claude-specific reference this example illustrates, see [`references/claude-code.md`](../references/claude-code.md); for other vendors see the matching file in `references/`. Users on a non-Claude runtime or in environments without a parallel-spawn primitive should follow [`references/sequential-fallback.md`](../references/sequential-fallback.md) and adapt Step 2 below to a sequential persona-swap.
>
> **History**: this example reflects the v2.0+ protocol (native `Agent` tool). The pre-v2.0 example used `spawn_agent_mock.py`; see `docs/archives/POC_PARALLEL_AGENTS.md` for the historical POC.

## Input (User Request)
```
Review this PR for logic, security, and performance issues.
```

## Expected Orchestrator Actions

### Step 1: Decompose
Identify three orthogonal critiques (logic, security, performance) — each with its own subagent definition in `.claude/agents/critic-*`. No file decomposition needed; each teammate reviews the same target from its own perspective.

### Step 2: Parallel Spawn (single message, three Agent tool-uses)
In one assistant message, issue three parallel `Agent` calls:

```
Agent(
  subagent_type="critic-logic",
  description="Logic review of target",
  prompt="Review <target> for edge cases, input validation, state consistency, error handling. Return a structured critique per your teammate contract."
)

Agent(
  subagent_type="critic-security",
  description="OWASP/security review of target",
  prompt="Review <target> for injection, authn/authz, secrets, LLM-specific vulns. Return a structured security report per your teammate contract."
)

Agent(
  subagent_type="critic-performance",
  description="Performance review of target",
  prompt="Review <target> for N+1, memory, async, complexity, resource leaks. Return a structured perf report per your teammate contract."
)
```

All three execute concurrently; results return as three tool results in the same turn.

### Step 3: Merge
Collect the three structured reports. Apply merge rules (see `.agent/workflows/vdd-multi.md` Phase 2):
- Deduplicate issues at the same `(file, line ± 3)` across critics.
- Escalate severity by one level when two critics independently flag the same location.
- Produce a single `VDD Multi-Adversarial Report` with sections per category plus an "Overlaps" section.

### Step 4: Iterative fix (per category)
For any category that returned issues, apply fixes and re-spawn **only that critic** until clean-pass or hallucinating (not a full parallel triple — single-critic re-spawn is cheaper).

## Alternative scenario — decomposed feature development (use Layer B in Wave 4)

For "Build Login Page (Frontend) + Auth API (Backend) simultaneously" where teammates need to negotiate API schema mid-flight:
- **Wave 1**: not the right use case for Layer A (needs inter-teammate communication).
- **Wave 4 (planned)**: `TeamCreate` + teammates with `SendMessage` mailbox. Stub criterion in `SKILL.md` §4.
