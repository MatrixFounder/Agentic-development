# Parallel Orchestration — Gemini CLI reference (SCAFFOLD)

> ⚠️ **SCAFFOLD — documented from primary sources (geminicli.com/docs/core/subagents, fetched 2026-06-10), NOT yet validated on a real runtime.** The subagent *definition* format below is transcribed from Gemini's published docs. **Parallel single-invocation multi-spawn is NOT confirmed by the primary docs** (see the gap note) — so until validated, Layer-A parallelism on Gemini is unproven and the skill may fall back to [`sequential-fallback.md`](sequential-fallback.md) for the multi-critic dispatch.

**Loads with**: parent `SKILL.md` when `GEMINI.md` is present and no Claude Code markers are active (parent `SKILL.md §1.1`).

---

## Runtime primitives

| Concept (from parent §2) | Gemini CLI primitive |
|---|---|
| Teammate definition | **Markdown + YAML frontmatter** — `.gemini/agents/<name>.md` (project) or `~/.gemini/agents/<name>.md` (user); the body is the agent's system prompt |
| Teammate type selector | the `name` field; explicit invocation via `@<subagent-name>` in a prompt |
| Spawn / invocation | (a) **automatic delegation** — the main agent decides based on `description`; (b) **explicit** — prefix a prompt with `@subagent-name` |
| Parallel-spawn primitive | **⚠️ NOT documented.** Primary docs describe auto-delegation + explicit `@name` invocation; they do **not** state concurrent multi-subagent execution. See gap note. |
| Inter-teammate communication (Layer B) | not documented — treat as unavailable |

### Teammate definition fields (verified)

Required: `name` (slug — lowercase, digits, `-`/`_`), `description` (helps the main agent decide when to delegate).
Optional: `tools` (array; wildcards `*`, `mcp_*`, `mcp_server_*` — omit to inherit all), `mcpServers` (inline, isolated to this agent), `model` (override; inherits session by default), `kind` (`local` default / `remote`), `temperature`, `max_turns` (default 30), `timeout_mins` (default 10).

---

## ⚠️ The Layer-A gap (honest record)

The framework's multi-critic pattern needs a **single-invocation fan-out** (spawn 3 critics at once, merge after). Claude Code does this with one multi-tool-call message; Codex does it with parallel agent spawn. **Gemini's primary docs do not document an equivalent.** What they document:
- one subagent invoked at a time, either by auto-delegation or `@name`.

Until a real run proves otherwise, do **not** claim Layer A on Gemini. Two honest options for the multi-critic flow:
1. **Sequential delegation** — invoke `@critic-logic`, then `@critic-security`, then `@critic-performance` in turn, merging after (this is `sequential-fallback.md` semantics, just using native subagents as the personas).
2. **Validate parallel** — if a real Gemini run demonstrates concurrent subagent execution (e.g. multiple `@`-invocations dispatched together), document the exact pattern here and graduate to Layer A.

The roadmap's earlier "concurrent subagents/instances" note was **optimistic and is not corroborated** by the primary docs as of 2026-06-10.

---

## Read-only enforcement

Gemini critics restrict the `tools` array to read-only tools (the project's read/grep/glob equivalents) — no write/shell tool listed. This is the analogue of withholding `Bash`/`Write` from a Claude critic wrapper.

---

## Critic wrapper catalog (scaffold)

| Wrapper | File | SOT skill | Scope |
|---|---|---|---|
| `critic-logic` | `.gemini/agents/critic-logic.md` | `.agent/skills/vdd-adversarial/SKILL.md` | logic only |
| `critic-security` | `.gemini/agents/critic-security.md` | `.agent/skills/skill-adversarial-security/SKILL.md` | security only |
| `critic-performance` | `.gemini/agents/critic-performance.md` | `.agent/skills/skill-adversarial-performance/SKILL.md` | performance only |

Same convergence enum `clean-pass | issues-found | bikeshedding-only`. The wrappers are valid subagent definitions regardless of the parallel gap — the gap is about *orchestration*, not *definition*.

---

## Validation gate (graduate SCAFFOLD → ✅)

Graduates **only after one end-to-end `/vdd-multi --no-fix` run on a real Gemini CLI install** that also resolves the Layer-A question (parallel confirmed, or documented sequential). Record run date + Gemini version + the dispatch pattern actually used. Operator action — not in-repo work.

## See also
- Parent [`SKILL.md §1.1`](../SKILL.md) detection table (Gemini row: `GEMINI.md`).
- [`claude-code.md`](claude-code.md) — the complete reference this scaffold mirrors.
- [`sequential-fallback.md`](sequential-fallback.md) — the documented dispatch until Layer A is proven on Gemini.
