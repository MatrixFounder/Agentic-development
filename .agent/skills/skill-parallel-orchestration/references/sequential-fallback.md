# Parallel Orchestration — Sequential fallback (universal-by-design)

> **Validation status**: **proposed pattern, not yet validated on a non-Claude runtime.** The protocol below is designed to be vendor-agnostic (requires only "Read a file" + "swap the active system prompt"), but all documented claims about wall-clock overhead, context-bleed, and persona-swap effectiveness have only been exercised on Claude Code itself (the native Layer A is used in practice; the fallback has been desk-checked, not end-to-end smoke-tested on a non-Claude runtime). Until the first real run on Gemini CLI / Cursor / Antigravity / etc., treat this as a design sketch rather than a proven code path. Report discrepancies via PR.

**Loads with**: `SKILL.md` (parent skill) when no vendor-specific parallel primitive is available, or when debugging with maximum observability. See §1 and §7 of parent SKILL.md.

---

## When to use

- The runtime has no parallel-spawn primitive (no `Agent` tool, no multi-tool-call).
- The runtime has one, but you want deterministic single-session behavior for debugging.
- You need a diagnostic run where the entire teammate trajectory is visible in one log.
- CI/script environments that don't provision multiple agent slots.

---

## What you gain vs lose vs Layer A

**Gain**:
- Zero vendor-specific dependency — works anywhere a single agent runs.
- Full linear log — easy to reproduce issues.
- No inbox/task-list/shutdown-protocol gotchas.
- No per-teammate tool-whitelist infrastructure required.

**Lose**:
- **Wall-clock**: ~N× slower (each teammate runs in sequence, not parallel).
- **Context isolation**: every teammate's work lands in the same session window. Context bleeds across personas. Prompts must be rigorous about "forget the previous persona" at each swap.
- **Token cost** per run can be higher: no per-teammate context pruning; accumulated history carries forward.
- **Layer B impossible**: no inter-teammate messaging — there's only one agent. If you need peer communication, fallback is insufficient.

---

## Protocol

For each teammate role in the decomposition:

1. **Context reset** (explicit, in the prompt): "Forget prior personas. You are now <ROLE>. Your sole task is described below."
2. **Load persona**: read the role's definition file (`System/Agents/<role>.md` or equivalent) and adopt its methodology.
3. **Execute**: perform the unit of work with strictly the persona's scope — do not mix concerns from earlier personas.
4. **Emit artifact**: write the structured report to the agreed output location (or return it to the orchestrator as text).
5. **State clear**: explicitly close the persona ("Persona <ROLE> complete. Returning to orchestrator mode.") before the next swap.

After all teammates have run sequentially, the orchestrator performs the same merge as in parent §6:
1. Location dedup (±3 lines).
2. Cross-category re-attribution.
3. Severity escalation on independent overlap.
4. Hallucination filter.
5. Optional severity filter.

---

## Orchestration style assumption

The concrete pattern below assumes **chat-based orchestration** (most LLM CLIs — Claude Code, Gemini CLI, Cursor Composer) where the lead agent speaks in natural-language turns that the teammate persona consumes.

For **SDK/API-based orchestration** (no chat loop; you're calling `messages.create` or equivalent directly), the equivalent implementation is:

- One `system` message per teammate role (swap between calls instead of "persona swap via prompt").
- `messages` list reset between roles (or: one `user` message per role, `assistant` response captured per role).
- Merge logic unchanged — runs in your orchestrator code after the last persona completes.

The teaching below uses the chat idiom for readability; translate to SDK calls mentally if that's your runtime.

## Concrete pattern (chat-based)

```
## Sequential fallback for a 3-critic VDD run

1. Orchestrator message: "You are now critic-logic. Read
   .agent/skills/vdd-adversarial/SKILL.md. Review <target> for logic
   issues. Emit structured report. Do NOT fix."

2. Orchestrator captures report #1 to scratch.

3. Orchestrator message: "Forget the critic-logic persona. You are now
   critic-security. Read .agent/skills/skill-adversarial-security/SKILL.md.
   Review <target> for security issues. Emit structured report. Do NOT fix."

4. Orchestrator captures report #2.

5. Orchestrator message: "Forget the critic-security persona. You are
   now critic-performance. Read .agent/skills/skill-adversarial-performance/SKILL.md.
   Review <target> for performance issues. Emit structured report. Do NOT fix."

6. Orchestrator captures report #3.

7. Orchestrator merges (parent SKILL.md §6 rules).
```

---

## Anti-patterns specific to sequential fallback

- **"Since it's all one session, let the second critic look at the first one's output."** → **WRONG**. That's cross-pollination (parent §3 Red Flags). Each persona must start fresh with only the target as input.
- **"Keep accumulated context between personas; it's cheaper."** → **WRONG**. Persona bleed = each next critic inherits the prior's biases. Explicit context reset is non-negotiable.
- **"Skip the persona swap if two roles share the same checklist area."** → **WRONG**. The separation is methodological, not just content. Two critics finding the same issue independently is a stronger signal than one critic finding it twice.

---

## When to prefer this over vendor-specific Layer A

Even when a parallel primitive exists:

| Prefer sequential fallback when | Prefer vendor Layer A when |
|---|---|
| You need single-pane debugging of the full trajectory | Parallel wall-clock matters |
| The runtime has known Layer B/A bugs you're avoiding | Context-isolation per teammate matters (token hygiene, tool whitelist) |
| CI environment with one agent slot | Interactive IDE with full harness |

---

## Relationship to parent skill

All universal concepts (parent §2–§6) apply verbatim. This file only replaces the **spawn mechanism** (§2.3 step 2) with a sequential persona-swap loop, and adds the anti-patterns specific to single-session execution.
