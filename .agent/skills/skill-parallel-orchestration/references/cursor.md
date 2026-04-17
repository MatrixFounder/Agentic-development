# Parallel Orchestration — Cursor reference (STUB)

> ⚠️ **DEGRADED MODE**: this vendor's reference is a **stub** — not yet validated on a real runtime. If you're here because `SKILL.md §1.1` matched this vendor, the skill will fall back to [`sequential-fallback.md`](sequential-fallback.md) for concrete invocation patterns. **The fallback is slower (~N× wall-clock) and loses per-teammate context isolation.** If you wanted parallel execution on this vendor, the reference is not yet implemented — contribute a PR after validating one end-to-end run.

**Loads with**: parent `SKILL.md` when a `.cursor/` directory is present and no Claude Code markers are active (parent `SKILL.md §1.1`).

## Vendor-specific notes

- **Runtime detection marker**: presence of `.cursor/` directory at project root.
- **Known parallel primitive**: unknown — Composer / agent-mode may or may not support single-invocation multi-agent spawn. Contribute after verifying.
- **Known teammate definition convention**: Cursor has `.cursor/rules/*.mdc` for related concepts, but whether rules-as-teammates is the right analog is unverified. Contribute after verifying.
- **Layer B support**: unknown — contribute after verifying.

## What this file should become

See the shared checklist and contribution guidance in [`_stub-template.md`](_stub-template.md). A complete reference matches the depth of [`claude-code.md`](claude-code.md).

## Until then

Use [`sequential-fallback.md`](sequential-fallback.md) — universal concepts from parent `SKILL.md §2–§6` apply unchanged; only the spawn mechanism degrades to sequential persona-swap.
