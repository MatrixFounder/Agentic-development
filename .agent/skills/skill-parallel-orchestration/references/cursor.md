# Parallel Orchestration — Cursor reference (SCAFFOLD)

> ⚠️ **SCAFFOLD — documented from primary + secondary sources (cursor.com/docs/subagents + changelog/2-4, fetched 2026-06-10), NOT yet validated on a real runtime.** The primitives below are transcribed from Cursor 2.4's published docs; no end-to-end `/vdd-multi` run has been executed on Cursor from this repo. Ready-to-validate: run one `--no-fix` task on a real Cursor install, then graduate the banner.

**Loads with**: parent `SKILL.md` when a `.cursor/` directory is present and no Claude Code markers are active (parent `SKILL.md §1.1`).

---

## Runtime primitives

| Concept (from parent §2) | Cursor 2.4 primitive |
|---|---|
| Parallel-spawn primitive | main agent orchestrates; subagents **run in parallel, max 10** (cursor.com/docs/subagents, changelog 2.4) |
| Teammate definition | **Markdown + YAML frontmatter** — `.cursor/agents/<name>.md` (project, committed) or `~/.cursor/agents/<name>.md` (global) |
| Teammate type selector | the agent file (one file = one subagent); the `description` drives delegation |
| Single-invocation multi-spawn | the orchestrating agent delegates to N subagents that execute concurrently (Layer A); merge after |
| Inter-teammate communication (Layer B) | `is_background: true` makes a subagent **async** (cloud background agent) — closer to Layer B semantics; **defer like Claude's Layer B** (out of scope for the synchronous critic merge) |

### Teammate definition fields (verified)

- `description` — **critical**; the main agent reads it to decide when to delegate (write it like a job description, specific about when to use).
- `model` — `"inherit"` (use the main agent's model), `"fast"` (cheaper/faster), or a hardcoded model id.
- `readonly` — `true` ⇒ the agent only reads/analyzes, never writes; **ideal for critics/auditors/reviewers**.
- `is_background` — `true` ⇒ async (parent doesn't wait). For the synchronous critic merge keep this **false**.

---

## Layer A (parallel, no peer communication) — documented, unvalidated

**Protocol step 2 (Spawn) concretely**: the orchestrating agent delegates to the three critic subagents; Cursor runs them in parallel (up to 10 concurrent). Use **in-session** subagents (`is_background: false`) so the merge happens in one pass.

**Invariants**:
- Delegate all three at once; do not chain (Layer A invariant).
- Independent context per subagent; no cross-pollination except the shared execution-evidence block (`vdd-multi` Phase 1).
- **Read-only critic guarantee**: `readonly: true` on every critic subagent — the runtime-enforced analogue of withholding `Bash`/`Write` from a Claude critic wrapper.

**In-session vs background**: in-session subagents (interactive, `is_background:false`) are the Layer A path here. Background agents (cloud, async) are closer to Layer B — **deferred**, like Claude's `TeamCreate` Layer B.

---

## Critic wrapper catalog (scaffold)

| Wrapper | File | SOT skill | Scope |
|---|---|---|---|
| `critic-logic` | `.cursor/agents/critic-logic.md` | `.agent/skills/vdd-adversarial/SKILL.md` | logic only |
| `critic-security` | `.cursor/agents/critic-security.md` | `.agent/skills/skill-adversarial-security/SKILL.md` | security only |
| `critic-performance` | `.cursor/agents/critic-performance.md` | `.agent/skills/skill-adversarial-performance/SKILL.md` | performance only |

All `readonly: true`, `is_background: false`, same convergence enum `clean-pass | issues-found | bikeshedding-only`.

---

## Validation gate (graduate SCAFFOLD → ✅)

Graduates **only after one end-to-end `/vdd-multi --no-fix` run on a real Cursor 2.4+ install**. Record run date + Cursor version + parallel-execution evidence (and confirm the max-10 concurrency vs the framework's default-to-1 exploration guidance). Operator action — not in-repo work.

## See also
- Parent [`SKILL.md §1.1`](../SKILL.md) detection table (Cursor row: `.cursor/`).
- [`claude-code.md`](claude-code.md) — the complete reference this scaffold mirrors.
- [`sequential-fallback.md`](sequential-fallback.md) — last resort if parallel delegation proves unavailable.
