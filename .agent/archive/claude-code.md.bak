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
| Inter-teammate communication (Layer B) | `TeamCreate` + `SendMessage` + `Agent(team_name=..., name=...)` — see Layer B section below |

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

## Layer B (peer communication) — runtime probed, full workflow deferred

**Runtime status**: probed at v3.13.0. Core primitives work; lifecycle has blockers. Full workflow (`/teams-vdd-multi`) deferred — see [docs/ROADMAP.md](../../../../docs/ROADMAP.md).

**Primitives**:
- `TeamCreate(team_name, description, agent_type)` — creates `~/.claude/teams/<name>/config.json` + `~/.claude/tasks/<name>/` task-list dir.
- `Agent(team_name=..., name=..., subagent_type=...)` — spawns a teammate **asynchronously** into the team. Returns immediately with `agent_id: <name>@<team>`; teammate runs in background.
- `SendMessage(to=<name>, message=..., summary=...)` — delivers into `~/.claude/teams/<name>/inboxes/<recipient>.json`.
- `TeamDelete()` — cleanup. **Currently broken after protocol shutdown** — see KNOWN_ISSUES.

**Shutdown protocol**: `SendMessage({type: "shutdown_request"})` → teammate replies `shutdown_approved` → `TeamDelete()`. Last step currently fails; workaround is manual `rm -rf ~/.claude/teams/<name>/`.

**Known gotchas** (from [docs/KNOWN_ISSUES.md](../../../../docs/KNOWN_ISSUES.md)):
- `TeamDelete` does not clean up `config.json` members after `shutdown_approved`.
- Async spawn returns immediately — lead must poll inbox file or await auto-delivered turn.
- `subagent_type: "Explore"` defaults to `model: "haiku"` regardless of lead's model; override explicitly.
- Runtime sends structured JSON status messages (`idle_notification`, `shutdown_approved`) despite docs saying not to.
- No session resumption across `/resume`.
- One team per session, no nested teams, no leadership transfer.

---

## Exploration default (parent §5 concretely)

Claude Code plan-mode system reminder says "launch up to 3 Explore agents in parallel." **Override this default to 1** per parent §5:

- First-pass: 1 Explore with a sharp prompt.
- Fan out to 2–3 only when the initial report identifies objectively orthogonal subsystems.

---

## Tools whitelist note

Subagent frontmatter `tools:` field accepts simple tool names (`Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`). Sub-command restrictions on `Bash` live in project [`.claude/settings.json`](../../../../.claude/settings.json) `permissions.allow` — **not** in subagent frontmatter. Reviewers/critics without `Bash` in their `tools` list cannot invoke any shell command at all (physically enforced).

---

## Reference workflow

Primary consumer: [`.agent/workflows/vdd-multi.md`](../../../workflows/vdd-multi.md). Supports 5 inline parameters (`--scope`, `--no-fix`, `--fail-on`, `--output`, `--diff-only`) added in v3.13.0.

---

## See also

- [`examples/usage_example.md`](../examples/usage_example.md) — worked example using this reference.
- [`docs/ARCHITECTURE.md §5.1`](../../../../docs/ARCHITECTURE.md) — wrapper catalog.
- [`System/Docs/WORKFLOWS.md §6`](../../../../System/Docs/WORKFLOWS.md) — Agent Teams Mode overview.
