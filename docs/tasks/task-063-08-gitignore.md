# Task 063-08 — `.gitignore` patch + `!`-exception scanner

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-07
**Successor**: Task 063-09

## Goal

Implement the mandatory `.gitignore` managed block (hash-protected via the 063-06 engine) and the `!`-exception scanner that keeps project-local skills/commands trackable.

## Files to edit / create

### `System/scripts/installer/gitignore.py` (implement — Issues I9.1, I9.2)

- `build_block_body(profile: dict, exceptions: list[str]) -> str` — assemble the static block body from the approved plan: framework dirs (`/.agentic-development/`, `/System`, `.agent/*` sub-paths), `/.agentic-installer-state.json`, Claude bridge files, the chosen vendor's paths, then the `!`-exception lines.
- `scan_local_exceptions(target: Path) -> list[str]` (I9.2):
  - Scan top level of `.agent/skills/`, `.agent/workflows/`, `.agent/agents/`, `.claude/skills/`, `.claude/commands/`, `.claude/agents/` (no recursion).
  - "project-local" predicate: `not entry.is_symlink()` **OR** (`entry.is_symlink()` and `Path(os.readlink(entry)).parts[0] != ".agentic-development"`).
  - Skip dotfiles (`.DS_Store`, `.git*`, `.gitkeep`).
  - Broken framework symlink (points into `.agentic-development/` but target missing) → emit a warning, **do not** add an exception.
  - Return sorted `!/relative/path` lines.
- `update_gitignore(target: Path, profile: dict, state: dict, *, force: bool = False, backup_dir: Path | None = None) -> str` (I9.1):
  - `exceptions = scan_local_exceptions(target)`; `body = build_block_body(profile, exceptions)`.
  - Delegate to `managed_block.inject_block(target/".gitignore", body, GITIGNORE_MARKERS, state_hash=state.get("gitignore_block_hash"), force=force, backup_dir=backup_dir)`.
  - Return the new hash (caller stores it in `state["gitignore_block_hash"]`).

### `tests/installer/test_gitignore.py` (create — Issue I10.1)

- No `.gitignore` → created with exactly one marker block; `version`-stable body.
- Existing `.gitignore` with user rules → user rules preserved, block appended.
- `scan_local_exceptions`: a tree with framework symlinks + one real user skill dir → only the user dir returned as `!/...`.
- Dotfiles never appear in exceptions.
- Broken framework symlink → warning emitted, not added as exception.
- Re-run with matching `state_hash` → idempotent rewrite.
- Manual edit inside the block → `update_gitignore` raises `IntegrityError` (via the 063-06 engine); `--force` restores.

## RTM (acceptance criteria)

- `[FR-7.1]` `.gitignore` always gets a marker-delimited managed block.
- `[FR-7.2]` Block hash stored in `state["gitignore_block_hash"]`; anti-clobber enforced (delegated to 063-06).
- `[FR-7.3]` `scan_local_exceptions` adds `!`-lines for project-local items only (predicate above).
- `[FR-7.4]` Dotfiles filtered; broken framework symlinks skipped with a warning.
- `[FR-7.5]` No recursion — only top-level entries of the six scanned dirs.

## Verification

```bash
python3 -m pytest tests/installer/test_gitignore.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- `--no-gitignore` flag handling — that branch lives in the `install` orchestration, Task 063-09.
- Stripping the block on `uninstall` — Task 063-10.
