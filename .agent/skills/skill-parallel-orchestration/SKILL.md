---
name: skill-parallel-orchestration
description: "Use when decomposing tasks into parallel sub-tasks or spawning sub-agents."
tier: 2
version: 2.0
---

# Parallel Orchestration Skill

**Purpose**: Defines the protocol for the **Orchestrator Role** to decompose large tasks into independent sub-tasks and execute them in parallel via native sub-agent spawning.

**Two layers** (pick by scenario):

- **Layer A — Framework-Agent (Wave 1, implemented)**: parallel calls to the built-in `Agent` tool in a single message. Short, isolated tasks that return an artifact. No inter-teammate communication. Used by `/vdd-multi`.
- **Layer B — Native Teams (Wave 4, stub)**: `TeamCreate` + `SendMessage` + `Agent(team_name=...)`. Long-lived multi-session scenarios with peer-to-peer communication (e.g., critics debating a security-vs-performance trade-off). **NOT IMPLEMENTED in Wave 1** — see `Layer B` section below for the decision criterion.

## 1. Red Flags (Anti-Rationalization)

**STOP and READ THIS if you are thinking:**

- "I'll spawn agents sequentially, waiting for each one." → **WRONG**. For independent tasks this is slower and loses context-isolation. Issue all `Agent` calls in **one message** so the harness runs them in parallel.
- "I'll pass the first critic's output to the second to save tokens." → **WRONG**. Cross-pollination defeats parallel critique. Merge happens AFTER all returns, in the orchestrator.
- "I don't need shared state if agents are independent." → **WRONG**. If any teammate writes to `.agent/sessions/latest.yaml`, `fcntl`-locking is mandatory (already enforced by `skill-session-state`).
- "One big Agent call covering everything is simpler." → **WRONG**. Separate teammates get separate context windows, stricter tool-whitelists, and clearer failure modes.

## 2. Capabilities

- **Decompose**: split complex tasks into independent units with clear artifact contracts.
- **Spawn (Layer A)**: launch parallel `Agent` tool-uses in one message, each targeting a defined `subagent_type` from `.claude/agents/`.
- **Synchronize**: merge returned artifacts into a single coherent result.

## 3. Instructions

### Phase 1: Task Decomposition

1. Analyze the user request.
2. Identify independent units (no shared mutable state, no ordering constraints beyond "all-done → merge").
3. For each unit, pick an existing subagent from `.claude/agents/` or note that a new wrapper is needed.

### Phase 2: Parallel Spawn (Layer A)

1. **Single message, multiple `Agent` tool-uses.** Example pattern:
   ```
   Message with three tool-use blocks, all Agent:
     - Agent(subagent_type="critic-logic",       prompt="...", description="...")
     - Agent(subagent_type="critic-security",    prompt="...", description="...")
     - Agent(subagent_type="critic-performance", prompt="...", description="...")
   ```
2. Give each subagent an **independent prompt** (no references to sibling teammates' outputs — those don't exist yet).
3. Respect each subagent's tools-whitelist (declared in `.claude/agents/<name>.md` frontmatter). Do not try to bypass via prompt.
4. Await all three tool results before proceeding to merge.

### Phase 3: Merge

1. Collect structured reports from each subagent's tool result.
2. Apply merge rules defined by the calling workflow (e.g., `.agent/workflows/vdd-multi.md` Phase 2 for critics).
3. Emit the merged artifact to the user or to the next phase of the workflow.

## 4. Layer B (Native Teams) — stub

**NOT IMPLEMENTED in Wave 1.** Document only; do not invoke `TeamCreate`/`SendMessage` from this skill yet.

**When to use Layer B** (criterion):

> Layer B is required **iff** teammates need to exchange messages with each other (not just with the lead) during their work. Equivalently: if the set of artifacts produced by teammate A depends on inspecting teammate B's in-progress output, use Layer B.

Examples:
- ✅ Layer B: security and performance critics debating whether an input-validation weakness is a DoS vector or a correctness bug.
- ✅ Layer B: parallel feature implementation where backend-team needs to negotiate API schema with frontend-team mid-flight.
- ❌ Layer A (sufficient): three orthogonal code critics each producing an independent report, merged by the orchestrator after all return.

Full Layer B implementation is scheduled for **Wave 4** and will add `.agent/workflows/teams-vdd-multi.md`.

## 5. Best Practices & Anti-Patterns

| DO | DO NOT |
| :--- | :--- |
| One message, N parallel `Agent` tool-uses | Sequential `Agent` calls for independent work |
| Reference existing `.claude/agents/*` by `subagent_type` | Inline a full system prompt when a wrapper exists |
| Give each teammate a clear return-format contract | Expect unstructured prose and post-hoc parsing |
| Merge in the orchestrator after all returns | Stream partial results between teammates (use Layer B if you need that) |

## 6. Scripts and Resources

- `scripts/spawn_agent_mock.py` — **DEPRECATED** (Wave 1, 2026-04-17). Superseded by native `Agent` tool. Retained for historical `fcntl`-locking regression tests via `tests/test_mock_agent.py`. Do not use in new workflows.

## 7. History

- **v2.0 (Wave 1, 2026-04-17)**: replaced mock-spawn with native `Agent` tool (Layer A); added Layer B stub.
- **v1.0 (POC)**: mock-agent via `spawn_agent_mock.py &`. See `docs/archives/POC_PARALLEL_AGENTS.md`.
