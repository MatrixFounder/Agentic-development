# Parallel Orchestration — Claude Code reference implementation

**Status**: Complete. This is the framework's primary runtime.

**Loads with**: `SKILL.md` (parent skill) when `CLAUDE.md` is present and `.claude/agents/` is populated. See §1 of parent SKILL.md.

---

## Runtime primitives

| Concept (from parent §2) | Claude Code primitive |
|---|---|
| Parallel-spawn primitive | Built-in `Agent` tool — multiple `tool_use` blocks inside one assistant message |
| Teammate definition | `.claude/agents/<name>.md` — YAML frontmatter (`name`, `description`, `tools`, `model`) + thin body |
| Teammate type selector | `subagent_type: "<wrapper-name>"` parameter on the `Agent` tool |
| Single-invocation multi-spawn | Claude's multi-tool-call feature (one LLM turn, multiple tool-uses, same `requestId`) |
| Inter-teammate communication (Layer B) | `Agent(name=...)` + `SendMessage`, in the session's one implicit team — see Layer B section below |

---

## Layer A (parallel, no peer communication) — implemented

**Protocol step 2 (Spawn) concretely**: in a **single assistant message**, issue N `Agent` tool-uses. Each must set `subagent_type` to an existing wrapper name from `.claude/agents/`.

Pattern:

```
Message with three parallel tool-uses:
  - Agent(subagent_type="critic-logic",       prompt="...", description="...")
  - Agent(subagent_type="critic-security",    prompt="...", description="...")
  - Agent(subagent_type="critic-performance", prompt="...", description="...")
```

**Invariants**:
- ONE message with N tool-uses. Sequential messages = not parallel.
- Each `prompt` is independent — no references to sibling outputs (they don't exist yet).
- Respect each wrapper's `tools` whitelist (declared in frontmatter); don't try to bypass via prompt.
- Await all N `tool_result` blocks before merging.

**Verification the harness ran them in parallel**: JSONL log records all N `Agent` tool-uses under the **same `requestId`** (one LLM inference returning N tool-calls). Verified in production on `docs/tasks/task-dummy.md` smoke runs (v3.10.0 baseline, v3.11.1 post-refactor, v3.13.0 post-Opus).

---

## Layer B (peer communication) — full workflow deferred

**Runtime status**: Claude Code 2.1.306, with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in [.claude/settings.json](../../../../.claude/settings.json). A session has one implicit team. `TeamCreate` and `TeamDelete` are retired: the binary lists both among retired tool names, and neither is offered as a tool. `Agent` ignores its `team_name` parameter. The full workflow (`/teams-vdd-multi`) stays deferred — see [docs/ROADMAP.md](../../../../docs/ROADMAP.md).

**Primitives** (from the tool schemas of 2.1.306; no Layer B workflow ran on them):
- `Agent(name=..., subagent_type=..., prompt=...)` — spawns a teammate that runs in the background. `name` makes it addressable while it runs; the lead is notified when it completes.
- `SendMessage(to=<name>, message=...)` — sends a message to a running teammate, or resumes a finished one from its transcript. Messages from teammates arrive in the lead's turn; there is no inbox file to read. `shutdown_request` and `plan_approval_request` remain as legacy protocol messages.
- `ListAgents()` — lists the teammates and subagents that the session can message.
- `TaskStop(task_id=<name>)` — stops a running teammate.

**Probe history**: the probe of v3.13.0 (2026-04-17) ran on `TeamCreate`, `TeamDelete` and team directories under `~/.claude/teams/<name>/`. Its records AT-1 to AT-9 in [docs/KNOWN_ISSUES.md](../../../../docs/KNOWN_ISSUES.md) are closed: AT-6 (`TeamDelete` cleanup) is `fixed` by the retirement, and the other eight are `wontfix`, not probed again. A Layer B workflow starts with a new probe on the current runtime, and files each constraint that still holds as a new record.

---

## Exploration default (parent §5 concretely)

Claude Code plan-mode system reminder says "launch up to 3 Explore agents in parallel." **Override this default to 1** per parent §5:

- First-pass: 1 Explore with a sharp prompt.
- Fan out to 2–3 only when the initial report identifies objectively orthogonal subsystems.

---

## Tools whitelist note

Subagent frontmatter `tools:` field accepts simple tool names (`Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`). Sub-command restrictions on `Bash` live in project [`.claude/settings.json`](../../../../.claude/settings.json) `permissions.allow` — **not** in subagent frontmatter. Reviewers/critics without `Bash` in their `tools` list cannot invoke any shell command at all (physically enforced).

---

## Model-pin hygiene (audit-067 C-06)

- **Tier ladder**: the Agent-tool `model` enum is `haiku < sonnet < opus < fable` — a `fable` tier exists **above** `opus`. The critic wrappers pin `model: opus` deliberately: routine critic passes are cost/latency-bound, and the documented recall lever is the exhaustive-reporting instruction, not raw model tier. Revisit when item 7/R3c (tier-diverse critics) lands.
- **Silent env override**: `CLAUDE_CODE_SUBAGENT_MODEL`, when set, **silently overrides** every wrapper's frontmatter `model:` pin. Before reasoning about critic behavior or cost, check that env var — it flattens an intentionally heterogeneous (tier-diverse) config without any warning.
- **`effort` field**: subagent frontmatter also accepts an `effort` field (audit-067) — becomes relevant once tier-diverse critic configs are adopted.
- **Tier-diverse consumer (R3c)**: `/vdd-multi --models=logic:<t>,security:<t>,performance:<t>` passes each critic a distinct `model` on its `Agent` call, spreading the committee across tiers **for recall/coverage** (mini-exp 078: highest recall, 100% pooled). The resulting overlaps carry a `tier-diverse` provenance tag but **no severity escalation** — 078 found cross-tier agreement *less* precise than same-tier (0.66 vs 0.73), so the original +1 was demoted to tag-only. The `CLAUDE_CODE_SUBAGENT_MODEL` override above flattens the config back to same-model; the workflow warns and uses the plain `corroborated` tag when it detects the env var.
- **Severity-threshold literalism (recall hazard)**: Opus 4.7+ follows instructions like "only report high-severity issues" *literally* — recall drops. The canonical pattern (used by all critic SOT skills since 071): **"report everything with confidence + severity attached; filter downstream."** Never put a severity floor in a critic prompt; filtering belongs to the merge step (`--severity`, merge rule 5).

---

## Reference workflow

Primary consumer: [`.agent/workflows/vdd-multi.md`](../../../workflows/vdd-multi.md). Supports 5 inline parameters (`--scope`, `--no-fix`, `--fail-on`, `--output`, `--diff-only`) added in v3.13.0.

---

## See also

- [`examples/usage_example.md`](../examples/usage_example.md) — worked example using this reference.
- [`docs/ARCHITECTURE.md §5.1`](../../../../docs/ARCHITECTURE.md) — wrapper catalog.
- [`System/Docs/WORKFLOWS.md §6`](../../../../System/Docs/WORKFLOWS.md) — Agent Teams Mode overview.
