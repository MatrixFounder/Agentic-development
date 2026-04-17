# Vendor-reference stub template

**This file is a template**, not itself loaded by the skill. Per-vendor stub files (`gemini-cli.md`, `cursor.md`, `antigravity.md`) each contain only the vendor-specific detection marker + a pointer to this template for the shared checklist.

Shared across all non-complete vendor references:

---

## Fallback warning (include verbatim at top of each stub)

> ⚠️ **DEGRADED MODE**: this vendor's reference is a **stub** — not yet validated on a real runtime. If you're here because `SKILL.md §1.1` matched this vendor, the skill will fall back to [`sequential-fallback.md`](sequential-fallback.md) for concrete invocation patterns. **The fallback is slower (~N× wall-clock) and loses per-teammate context isolation.** If you wanted parallel execution on this vendor, the reference is not yet implemented — contribute a PR after validating one end-to-end run.

---

## What the full reference must provide (contribution checklist)

A complete vendor reference (matching [`claude-code.md`](claude-code.md) depth) should document:

- [ ] **Runtime identification**: what file/env var/directory signals "this vendor" (so parent `SKILL.md §1.1` detection can match).
- [ ] **Parallel-spawn primitive**: does the vendor expose a single-invocation multi-agent spawn? If yes, its name + syntax. If no, state so and direct users to `sequential-fallback.md`.
- [ ] **Teammate definition convention**: vendor's equivalent of `.claude/agents/<name>.md` — directory layout, frontmatter schema, body conventions.
- [ ] **Teammate type selector**: equivalent of the `subagent_type` parameter.
- [ ] **Tools whitelist mechanism**: how per-teammate tool restrictions are declared and enforced.
- [ ] **Layer B support** (peer messaging): whether the vendor has native teams/messaging. If no, explicitly note Layer B unavailability.
- [ ] **Verification pattern**: how to confirm parallel execution actually occurred (Claude uses same-`requestId` check in JSONL — what's the equivalent here?).
- [ ] **Known gotchas**: anything that would become an entry in [`docs/KNOWN_ISSUES.md`](../../../../docs/KNOWN_ISSUES.md).
- [ ] **Reference consumer**: link to a workflow that uses this reference (analogous to `.agent/workflows/vdd-multi.md` for the Claude Code case).

## Minimum viable content to unblock

If a full reference is not yet feasible, at minimum state:

1. Runtime identification marker (detection signal for parent `SKILL.md §1.1`).
2. Whether **any** parallel primitive exists. If not, explicit pointer to [`sequential-fallback.md`](sequential-fallback.md).
3. One-line summary of how teammate definitions are authored (file path + format), so `.claude/agents/*` wrappers can be ported or generated (Wave 5 remaining scope in [`docs/ROADMAP.md`](../../../../docs/ROADMAP.md)).

## Contribution guidance

Propose a PR to the vendor-specific stub file after running at least one concrete end-to-end task on that runtime (analogous to the Claude Code smoke tests on `docs/tasks/task-dummy.md`). Include:

- Evidence of parallel execution (or explicit statement it's sequential-only).
- Token-cost comparison vs. the Claude Code reference implementation.
- Any new entries for `docs/KNOWN_ISSUES.md`.
