# Parallel Orchestration — OpenAI Codex CLI reference (SCAFFOLD)

> ⚠️ **SCAFFOLD — documented from primary sources (developers.openai.com/codex, fetched 2026-06-10), NOT yet validated on a real runtime.** The primitives below are transcribed from Codex's published docs, but no end-to-end `/vdd-multi` run has been executed on Codex CLI from this repo. Treat this as a *ready-to-validate* adapter: run one `--no-fix` task on a real Codex install, then graduate the banner to ✅ and record the date+version here.

**Loads with**: parent `SKILL.md` when a `.codex/agents/` directory is present (parent `SKILL.md §1.1`). Note: `AGENTS.md` alone is **not** a Codex marker — it is cross-vendor; tie-break via §1.2.

---

## Runtime primitives

| Concept (from parent §2) | Codex CLI primitive |
|---|---|
| Parallel-spawn primitive | Codex spawns specialized agents in parallel on explicit request, **waits for all, returns a consolidated response** (developers.openai.com/codex/subagents) |
| Teammate definition | **TOML** file in `.codex/agents/<name>.toml` (project) or `~/.codex/agents/<name>.toml` (user) |
| Teammate type selector | the agent's `name` field (the identifier Codex uses when spawning) |
| Single-invocation multi-spawn | request multiple agents in one turn → Codex runs them concurrently and consolidates (the Layer-A analogue of Claude's multi-tool-call) |
| Inter-teammate communication (Layer B) | not documented as peer messaging — treat as **Layer A only**; defer Layer B like Claude's |

### Teammate definition fields (verified)

Required: `name`, `description`, `developer_instructions` (the agent's behavior — the wrapper body).
Optional (inherit from session when omitted): `model` (e.g. `"gpt-5.4"`), `model_reasoning_effort`, `sandbox_mode` (`"read-only"` | `"workspace-write"`), `mcp_servers`, `skills.config`, `nickname_candidates` (array).

---

## Layer A (parallel, no peer communication) — documented, unvalidated

**Protocol step 2 (Spawn) concretely**: ask Codex to run the three critic agents on the target; Codex dispatches them in parallel and returns one consolidated result. Each critic agent is a TOML file under `.codex/agents/`.

**Invariants** (mirror parent §2.3 / §3):
- One request fans out to N agents — do not chain them sequentially.
- Each agent gets independent context; no cross-pollination (the shared execution-evidence block from `vdd-multi` Phase 1 is the only exception — it is ground truth).
- **Read-only critic guarantee**: set `sandbox_mode = "read-only"` in every critic agent — the physical analogue of withholding `Bash`/`Write` from a Claude critic wrapper. Critics report findings; the orchestrator applies fixes.

**Verification that they ran in parallel**: Codex's consolidated response should reflect all three agents in one turn. Record the concrete signal (log line / response structure) here after the first real run.

---

## Read-only enforcement

Codex critics declare `sandbox_mode = "read-only"`. This is enforced by the runtime, not by prompt — equivalent to a Claude critic wrapper omitting `Bash`/`Write` from `tools`. Do not grant `workspace-write` to a critic; the orchestrator owns mutations.

---

## Critic wrapper catalog (scaffold)

Three thin wrappers, one per domain, each pointing at the same SOT skill as the Claude wrappers:

| Wrapper | File | SOT skill | Scope |
|---|---|---|---|
| `critic-logic` | `.codex/agents/critic-logic.toml` | `.agent/skills/vdd-adversarial/SKILL.md` | logic only |
| `critic-security` | `.codex/agents/critic-security.toml` | `.agent/skills/skill-adversarial-security/SKILL.md` | security only |
| `critic-performance` | `.codex/agents/critic-performance.toml` | `.agent/skills/skill-adversarial-performance/SKILL.md` | performance only |

All three emit the same convergence enum `clean-pass | issues-found | bikeshedding-only`. Mind v3.19.1's symlink-aware prompt-discovery work (commit `6caf8ad`) — Codex path resolution must survive symlinked framework dirs; verify during the e2e run.

---

## Validation gate (graduate SCAFFOLD → ✅)

Graduates **only after one end-to-end `/vdd-multi --no-fix` run on a real Codex CLI install**. Record run date + Codex version + parallel-execution evidence in this header. Until then the ⚠️ banner stays. These runs require an operator machine with Codex CLI installed — **not in-repo work**.

## See also
- Parent [`SKILL.md §1.1`](../SKILL.md) detection table (Codex row: `.codex/agents/`).
- [`claude-code.md`](claude-code.md) — the complete, smoke-tested reference this scaffold mirrors.
- [`sequential-fallback.md`](sequential-fallback.md) — last resort if a runtime exposes no parallel primitive.
