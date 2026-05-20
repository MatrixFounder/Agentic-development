# Task 063-07 — Vendor-aware bootstrap

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-06
**Successor**: Task 063-08

## Goal

Implement the two bootstrap strategies — Claude's `@import` 3-file pattern and the `marker_block` injection for Antigravity/Codex/Gemini-CLI — plus the `none` strategy (Cursor) and the don't-overwrite enforcement.

## Files to edit / create

### `System/scripts/installer/bootstrap.py` (implement — Issues I5.1–I5.4)

- `PROTECTED = {"CLAUDE.md", "AGENTS.md", "GEMINI.md"}`.
- `is_protected(filename: str) -> bool` (I5.4) — `Path(filename).name in PROTECTED`. Used everywhere a write to a project-owned bootstrap file is attempted; **no path, even with `--force`, overwrites these files** — only managed blocks inside them.
- `apply_bootstrap(target, framework, profile, state, *, force, backup_dir) -> dict` — dispatch on `profile["bootstrap_strategy"]`; return `{created: [...], blocks: {filename: hash}}`.
- Strategy `at_import` (I5.1 — Claude):
  - `CLAUDE.md` — write a skeleton **only if absent** (`# Project\n\nSee CLAUDE.local.md for framework tooling.\n`); never touch an existing one.
  - `CLAUDE.local.md` — if absent, create containing the single line `@CLAUDE.agentic.md`; if present without that import, append a `MARKDOWN_MARKERS` block holding `@CLAUDE.agentic.md` via `managed_block.inject_block`.
  - `CLAUDE.agentic.md` — relative symlink → `.agentic-development/CLAUDE.md` (via `symlinks.link_one`).
- Strategy `marker_block` (I5.2 — Antigravity/Codex/Gemini-CLI):
  - Target files = `[bootstrap_file] + bootstrap_aliases` (Antigravity ⇒ `GEMINI.md` + `AGENTS.md`; FR-15).
  - Block content read fresh each run from `framework/<bootstrap_source>`.
  - For each target file: skeleton if absent (`# Project\n\n<block>\n`), else `managed_block.inject_block(..., MARKDOWN_MARKERS, state_hash=state["bootstrap_blocks_hash"].get(name), force=force, backup_dir=backup_dir)`.
  - Record each returned hash into `state["bootstrap_blocks_hash"][name]`.
  - **Do not** create `*.local.md` / `*.agentic.md` for this strategy.
- Strategy `none` (I5.3 — Cursor) — return `{created: [], blocks: {}}` immediately.

### `tests/installer/test_bootstrap.py` (create — Issue I10.1)

- `at_import` on a clean target → `CLAUDE.md` skeleton, `CLAUDE.local.md` with `@CLAUDE.agentic.md`, `CLAUDE.agentic.md` symlink resolving to `.agentic-development/CLAUDE.md`.
- `at_import` with a pre-existing `CLAUDE.md` → file content **unchanged** (don't-overwrite).
- `at_import` with a pre-existing `CLAUDE.local.md` (user notes, no import) → user notes preserved, import added under a marker block.
- `marker_block` (antigravity) → block injected into **both** `GEMINI.md` and `AGENTS.md` from one source; both hashes recorded in state.
- `marker_block` with a pre-existing `AGENTS.md` → file kept, only the managed block touched.
- `marker_block` re-run with matching state hash → idempotent.
- `none` (cursor) → no bootstrap files created.
- `is_protected("CLAUDE.md") / ("AGENTS.md") / ("GEMINI.md")` → `True`; `("README.md")` → `False`.

## RTM (acceptance criteria)

- `[FR-6.1]` `at_import` builds the 3-file Claude pattern; `CLAUDE.md` never overwritten.
- `[FR-6.2]` `marker_block` injects a managed block into the project's `AGENTS.md`/`GEMINI.md`, content sourced from `framework/<bootstrap_source>`.
- `[FR-6.3]` `marker_block` does **not** create `*.local.md`/`*.agentic.md`.
- `[FR-6.4]` `none` strategy is a clean no-op.
- `[FR-6.5]` `is_protected()` covers `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`; these are never overwritten even with `--force`.
- `[FR-15.1]` Antigravity injects the same block into both `GEMINI.md` and `AGENTS.md`; both hashes stored under `state["bootstrap_blocks_hash"]`.

## Verification

```bash
python3 -m pytest tests/installer/test_bootstrap.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- `.gitignore` handling — Task 063-08.
- Stripping bootstrap blocks on `switch`/`uninstall` — Task 063-10.
