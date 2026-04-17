# Roadmap

**Purpose**: Track deferred work, conditional follow-ups, and nice-to-have polish items for future releases. Living document — update as work gets picked up or priorities change.

**Last updated**: 2026-04-17 (Teams Mode Epic closed at v3.13.0).

---

## Closed epics (historical)

| Epic | Versions | Archive |
|---|---|---|
| Teams Mode Integration (Waves 1–3 + Wave-4 probe + /vdd-multi params) | v3.10.0 – v3.13.0 | [docs/archives/teams-mode-epic-v3.10-to-v3.13.md](archives/teams-mode-epic-v3.10-to-v3.13.md) |

---

## Deferred (conditional — reopen on concrete trigger)

### Wave 4 — Layer B: Native `TeamCreate` workflow (`/teams-vdd-multi`)

**Status**: Runtime probed in v3.13.0, **full workflow deferred**. Layer A (parallel `Agent` spawn in one message) fully covers current `/vdd-multi` use cases.

**Reopen when**: a concrete peer-debate scenario surfaces where critics or teammates must message each other **during** their work (not post-hoc merge). Current examples that do NOT qualify:
- Orthogonal parallel critique (Layer A already solves this).
- Independent parallel development of atomic tasks (Layer A with N `developer` subagents).

Hypothetical qualifying scenarios (speculative):
- `critic-security` finds a ReDoS and wants to check with `critic-performance` whether the algorithmic complexity is exploitable DoS vs. just slow, **before** finalizing severity.
- Two `developer` teammates implementing frontend and backend of the same feature, negotiating API schema mid-flight.

**Blocking gotchas** to address before shipping (documented in [docs/KNOWN_ISSUES.md](KNOWN_ISSUES.md)):
- `TeamDelete` does not clean up `config.json` members array after `shutdown_approved` protocol round-trip — currently requires manual `rm -rf`. This is a hard blocker for any idempotent workflow.
- Async spawn contract (no sync return) differs from Layer A — requires workflow-level inbox polling or wait-for-idle semantics.
- Model inheritance is inconsistent across subagent types — must override explicitly when Opus required.
- Runtime sends structured JSON status messages despite docs saying otherwise — workflow parsers must handle both plain text and JSON.

**Estimated scope** if reopened: 4–8 hours. Includes workflow design, lifecycle management, error recovery, observability of inter-teammate messages, smoke test.

### Wave 5 — Portable subagent generator

**Status**: Not started. **Conditional on second vendor adoption.**

**Reopen when**: a second CLI vendor (Codex, Antigravity, or similar) is adopted by the project and needs its own subagent definitions.

**Scope** if reopened:
- Introduce `.agent/agents/*.md` as vendor-portable source of truth (superset frontmatter).
- Generator script `.agent/tools/generate_vendor_agents.py` reading `.agent/agents/` and emitting per-vendor directories (`.claude/agents/`, `.codex/agents/`, etc.).
- Frontmatter mapping layer (Claude Code ↔ Codex tool-naming).
- Pre-commit hook to regenerate on change.

**YAGNI note**: as long as Claude Code is the only vendor, the current manual `.claude/agents/` wrappers are sufficient and simpler.

---

## Nice-to-have polish (no blockers; do when idle)

### `/vdd-multi` parameter smoke tests

**Status**: Parameters (`--scope`, `--no-fix`, `--fail-on`, `--output`, `--diff-only`) added in v3.13.0 and documented, but **not exercised** by a dedicated smoke run. Parsing and merge-filter behavior is unverified against real usage.

**Trigger**: first time someone uses a non-default flag and hits unexpected behavior.

**Scope**: run 3–5 parameterized invocations on `docs/tasks/task-dummy.md`:
- `/vdd-multi task-dummy.md --scope=security` — verify only critic-security spawns.
- `/vdd-multi task-dummy.md --no-fix` — verify Phase 3 skipped; report-only.
- `/vdd-multi task-dummy.md --fail-on=high --output=/tmp/report.md` — verify verdict + file write.
- `/vdd-multi --diff-only` (no target) — verify auto-derivation of target list from `git diff`.

### `/agents` UI discovery check

**Status**: All 16 wrappers have valid YAML frontmatter and pass structural validation, but have **never been browsed via the `/agents` Claude Code command** in the UI. Auto-routing by `description` field is untested.

**Scope**: manual 30-second check in IDE:
- Run `/agents` — confirm 16 entries visible.
- Verify descriptions start with infinitive verbs (Transform / Review / Design / …).
- Spot-check one entry for auto-routing accuracy (natural prompt → correct wrapper).

### Token cost measurement

**Status**: CHANGELOG v3.11.2 and ARCHITECTURE.md §5.1 claim "Opus ≈ 3–5× Sonnet token cost" — **hypothesis, not measurement**. Actual per-run cost for `/vdd-multi` has not been logged.

**Scope**: instrument one `/vdd-multi` smoke run (Sonnet baseline + Opus upgrade) and record actual token usage per critic from JSONL logs. Update docs with real numbers.

### Real-usage dogfood

**Status**: The framework has been exercised exclusively on `docs/tasks/task-dummy.md` (synthetic 9-flaw fixture). No real feature has been reviewed by the parallel `/vdd-multi` pipeline.

**Value**: real code surfaces what synthetic fixtures don't — noisy bonus findings, context-sensitivity, wrapper routing in unfamiliar codebases.

**Scope**: apply `/vdd-multi --diff-only` to any real PR in this repo (e.g., the next meaningful code change). Compare findings to what a manual reviewer would catch.

### `/full-robust` integration with `/vdd-multi` parameters

**Status**: `/full-robust` calls `/vdd-enhanced` and `/security-audit`, but does not pass `/vdd-multi` flags through. If a user invokes `/full-robust` with intent for CI-style `--fail-on=critical`, there's currently no way to plumb the flag.

**Scope**: minor workflow edit in `.agent/workflows/full-robust.md` to accept and forward flags. One commit, ~10 lines.

### CHANGELOG length discipline

**Status**: Recent CHANGELOG entries (v3.11.0, v3.11.1, v3.11.2, v3.13.0) are long — dense explanations, bulleted subsections, design decisions. Readability vs. thoroughness tradeoff.

**Scope**: consider a section-length cap (say 150 lines per version) for future entries; move long "Design decisions" rationale to a companion ADR file if it exceeds the cap.

---

## Out of scope (won't do without explicit ask)

- Wrapping `01_orchestrator.md` or `p00_product_orchestrator_prompt.md` as subagents — native Teams does not support nested teams; these roles must remain main-agent personas.
- Wrapping `00_agent_development.md` — it's a meta-doc, not an agent prompt.
- Porting the framework to a different agent runtime (non-CLI orchestrator) — architecture is tied to Claude Code / native subagent convention.

---

## How to use this roadmap

When picking up an item:
1. Read the full context (linked archive + KNOWN_ISSUES references).
2. Create a new `docs/TASK.md` via `/start-feature` or `/vdd-start-feature`.
3. Reference the roadmap item in the new TASK header ("Resolves: ROADMAP §<item>").
4. On completion, update this file to move the item to a "Done" table (or remove if trivial polish shipped in a patch release).

When adding a new item:
- Categorize into Deferred (conditional), Polish (nice-to-have), or Out of scope.
- Include a "Reopen when" / "Trigger" condition — avoid indefinite vague entries.
- Estimate scope roughly (hours or "small/medium/large").
