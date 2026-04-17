# Parallel Orchestration — Antigravity reference (STUB)

> ⚠️ **DEGRADED MODE**: this vendor's reference is a **stub** — not yet validated on a real runtime. If you're here because `SKILL.md §1.1` matched this vendor, the skill will fall back to [`sequential-fallback.md`](sequential-fallback.md) for concrete invocation patterns. **The fallback is slower (~N× wall-clock) and loses per-teammate context isolation.** If you wanted parallel execution on this vendor, the reference is not yet implemented — contribute a PR after validating one end-to-end run.

**Loads with**: parent `SKILL.md` when an Antigravity runtime marker is detected and no other vendor markers are active (parent `SKILL.md §1.1`).

## Vendor-specific notes

- **Runtime detection marker**: TBD — contributor must identify which file/env var/directory reliably signals Antigravity so parent `SKILL.md §1.1` detection can match.
- **Known parallel primitive**: unknown — contribute after verifying.
- **Known teammate definition convention**: unknown — contribute after verifying.
- **Layer B support**: unknown — contribute after verifying.

## What this file should become

See the shared checklist and contribution guidance in [`_stub-template.md`](_stub-template.md). A complete reference matches the depth of [`claude-code.md`](claude-code.md).

## Until then

Use [`sequential-fallback.md`](sequential-fallback.md) — universal concepts from parent `SKILL.md §2–§6` apply unchanged; only the spawn mechanism degrades to sequential persona-swap.
