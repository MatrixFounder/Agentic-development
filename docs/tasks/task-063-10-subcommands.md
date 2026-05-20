# Task 063-10 — Subcommands `switch` / `uninstall` / `update` / `doctor`

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-09
**Successor**: Task 063-11

## Goal

Implement the four remaining subcommands in `cli.py`. `install` (063-09) already provides every building block; these commands compose them plus `backup` and `managed_block.strip_block`.

## Files to edit / create

### `System/scripts/installer/cli.py`

**`_cmd_switch` (Issue I8.1 — FR-10)**
1. `load_state`; no state → require `--force` + `heuristic_state` (063-03).
2. Resolve OLD vendor; `create_snapshot` of OLD artifacts (unless `--no-backup`) → `.agent/backups/`; `apply_retention(max_backups)`.
3. Remove OLD artifacts: OLD `vendor_dir`; for `at_import` delete `*.local.md` + `*.agentic.md`; for `marker_block` `strip_block` the managed block from OLD bootstrap files. **`CLAUDE.md`/`AGENTS.md`/`GEMINI.md` kept** (`is_protected`). `.agent/sessions/` kept.
4. `.agentic-development/` is **not** recreated (assert inode/symlink target unchanged).
5. Call `_cmd_install` for the NEW vendor (`force=True`).

**`_cmd_uninstall` (Issue I8.2 — FR-11)**
- With state → delete exactly `state["managed_paths"]` + Claude bridge files; `strip_block` from `.gitignore` and bootstrap files.
- No state → `heuristic_state`; `--all-vendors` → sweep every known vendor profile.
- `--purge` → also remove `.agentic-development/`.
- `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` kept. State file deleted last.

**`_cmd_update` (Issue I8.3)**
- Re-run `link_per_item` for every per-item component (picks up new framework items).
- `--prune` → remove symlinks whose source vanished from the framework.
- Does **not** touch `settings.json`, bootstrap files, or `state["vendor"]`.

**`_cmd_doctor` (Issue I8.4 — FR-12)** — read-only, returns the [ARCHITECTURE §9.3 `doctor --json` schema](../ARCHITECTURE.md#9-framework-installer-subsystem):
- Every `state["managed_paths"]` symlink exists and resolves inside `.agentic-development/` (else `BROKEN_SYMLINK`).
- `.gitignore` + bootstrap block hashes match `state` (else `HASH_MISMATCH`).
- State file is valid JSON matching the schema (else `STATE_CORRUPT`).
- Codex: `target/.git/` exists when `git_root_required` (warning).
- `skipped_components` / foreign project-local files → `warnings`.
- `--json` → emit `{ok, vendor, errors[], warnings[]}`; exit `0` if `ok` else `1`.

### `tests/installer/test_subcommands.py` (create — Issue I10.1)

- `switch` claude→antigravity: `.claude/` gone, `CLAUDE.agentic.md` gone, `CLAUDE.md` preserved, `AGENTS.md`+`GEMINI.md` blocks present, `.agentic-development/` symlink target unchanged, snapshot created.
- `switch` without state + no `--force` → `ConflictError`; with `--force` → heuristic path runs.
- `uninstall` with state → only `managed_paths` removed; `CLAUDE.md` kept; `.gitignore` block stripped; state file gone.
- `uninstall --purge` → `.agentic-development/` removed.
- `uninstall` without state + `--all-vendors` → heuristic sweep.
- `update` → a newly-added framework skill gets linked; `--prune` removes a stale link; `settings.json` untouched.
- `doctor` on a healthy tree → `ok: true`, exit 0; on a broken symlink → `BROKEN_SYMLINK` error, exit 1; on a tampered `.gitignore` → `HASH_MISMATCH`.

## RTM (acceptance criteria)

- `[FR-10.1]` `switch` snapshots OLD, removes OLD artifacts, keeps protected files + `.agent/sessions/`, leaves `.agentic-development/` intact, installs NEW.
- `[FR-10.2]` `switch` without state requires `--force` + heuristic.
- `[FR-11.1]` `uninstall` removes `managed_paths`, strips `.gitignore`/bootstrap blocks, deletes state file.
- `[FR-11.2]` `--purge` additionally removes `.agentic-development/`; `--all-vendors` heuristic sweep.
- `[FR-11.3]` Protected bootstrap files survive `uninstall`.
- `[FR-1.2]` `update` re-syncs per-item symlinks; `--prune` drops orphans; leaves settings/bootstrap/vendor alone.
- `[FR-12.1]` `doctor` is read-only, emits the §9.3 JSON schema, exit 0/1 on health.

## Verification

```bash
python3 -m pytest tests/installer/test_subcommands.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- The full multi-step integration recipe (copy mode, switch chains, anti-clobber round-trip) — Task 063-11.
