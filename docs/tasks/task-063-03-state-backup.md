# Task 063-03 — State management + backup engine

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-02
**Successor**: Task 063-04

## Goal

Implement the installer state file (`<target>/.agentic-installer-state.json`) and the timestamped backup engine with retention. State lives at the target **root** (not inside `.agent/`) so it survives `switch`/`uninstall` (ARCHITECTURE §9.5 invariant).

## Files to edit / create

### `System/scripts/installer/state.py` (implement — Issues I7.1, I7.2)

- `STATE_FILENAME = ".agentic-installer-state.json"`.
- `load_state(target: Path) -> dict | None` — return parsed JSON, or `None` if absent (must **not** raise); raise `IntegrityError` only if the file exists but is corrupt JSON.
- `save_state(target: Path, state: dict) -> None` — atomic write (`tempfile.NamedTemporaryFile` in same dir → `os.replace`).
- `new_state(vendor, mode, framework_path, is_symlink) -> dict` — build the schema from [ARCHITECTURE §9.3](../ARCHITECTURE.md#9-framework-installer-subsystem): `version, vendor, mode, framework_path, agentic_development_is_symlink, installed_at` (ISO-8601 UTC), `gitignore_block_hash` (None), `bootstrap_blocks_hash` ({}), `managed_paths` ([]), `skipped_components` ([]).
- `heuristic_state(target: Path) -> dict` — reconstruct best-effort state from the current FS when no state file exists (scan for our symlinks → `managed_paths`; detect vendor by which `vendor_dir` is populated). Used by I7.2.

### `System/scripts/installer/backup.py` (implement — Issue I7.3)

- `create_snapshot(paths: list[Path], target: Path, label: str) -> Path` — copy each existing path into `target/.agent/backups/<UTC-timestamp>-<label>/`, preserving relative layout; return the snapshot dir. Backups **always** go under `target/.agent/backups/` (never inside `.agentic-development/`, which may be a read-only symlink).
- `apply_retention(target: Path, max_backups: int = 5) -> None` — keep the N newest snapshot dirs (lexicographic sort on the UTC-timestamp prefix), delete the rest.

### `tests/installer/test_state.py` (create — Issue I10.1)

- `load_state` on missing file → `None` (no raise).
- `load_state` on corrupt JSON → `IntegrityError`.
- `save_state` → `load_state` round-trip preserves all keys; write is atomic (no partial file on simulated failure).
- `new_state` produces a schema-complete dict; `installed_at` parses as ISO-8601.
- `heuristic_state` on a hand-built FS tree detects vendor + collects symlink `managed_paths`.
- `create_snapshot` copies only existing paths, skips missing ones, returns a dir under `.agent/backups/`.
- `apply_retention(max_backups=2)` over 5 snapshots leaves exactly the 2 newest.

## RTM (acceptance criteria)

- `[FR-9.1]` State file at `<target>/.agentic-installer-state.json` (target root, not `.agent/`).
- `[FR-9.2]` Schema matches ARCHITECTURE §9.3 exactly.
- `[FR-9.3]` `load_state` returns `None` (not raise) on absence; raises `IntegrityError` on corruption.
- `[FR-9.4]` Atomic write via temp + `os.replace`.
- `[FR-9.5]` `heuristic_state` reconstructs state from FS when the file is missing.
- `[FR-10.1]` `create_snapshot` writes to `target/.agent/backups/<UTC-ts>-<label>/`.
- `[FR-10.2]` `apply_retention` keeps N newest, deletes older (default N=5).

## Verification

```bash
python3 -m pytest tests/installer/test_state.py -v
python3 -m pytest tests/installer/ -q   # no regression
```

## Out of scope

- Calling `create_snapshot` from `switch`/`install --force` — that wiring is Tasks 063-09 / 063-10.
- Heuristic-mode *driving* `switch`/`uninstall` — Task 063-10.
