# Task 063-11 — Integration E2E suite + bash wrapper smoke test

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 3 — Integration & Verification
**Predecessor**: Task 063-10
**Successor**: none (chain end)

## Goal

Codify the full verification recipe from the approved plan as an automated integration suite, and add a bash-wrapper smoke test. This is the chain-end gate proving the installer behaves end-to-end across vendors and modes.

## Files to edit / create

### `tests/installer/test_e2e.py` (extend — Issue I10.2)

Each scenario uses a fresh `tmp_target` (git-init'd) and runs `installer.cli.main()` directly with built `Namespace` objects. The framework source is the live repo (`framework_root` fixture).

1. **Fresh install — symlink mode**: `.agentic-development` is a symlink; `.agent/skills/*` are relative symlinks resolving into it; `CLAUDE.agentic.md` symlink present; `.gitignore` has the marker block (open + close); state file vendor = `claude`.
2. **Fresh install — copy mode**: `.agentic-development` is a real dir (not symlink); contains no `IGNORE_NAMES` entries; per-item symlinks inside the target still exist and resolve into the local copy.
3. **Conflict prevention**: pre-seed `System/my-code/`, a user `CLAUDE.md`, `.claude/skills/my-skill/`, a user `.claude/settings.json`; after install all four are byte-preserved; `System` not symlinked; `state["skipped_components"]` contains `"System"`; `.gitignore` has `!/.claude/skills/my-skill`.
4. **`--force-system-link`**: foreign `System/` → backed up and replaced by the symlink.
5. **Idempotency** (NFR-1): second `install` reports `0 created`; FS unchanged (compare a path→inode map).
6. **Switch claude→antigravity**: `.agentic-development` symlink target unchanged; `.claude/` removed; `CLAUDE.md` preserved; `AGENTS.md`+`GEMINI.md` managed blocks present; snapshot dir created.
7. **Switch antigravity→codex**: `AGENTS.md` preserved; `.agents/skills` symlink present; `.codex/` dir present.
8. **Anti-clobber** (NFR-2): manually edit inside the `.gitignore` block → `install` raises `IntegrityError` with a diff, file untouched; `install --force` → block rewritten, user version saved under `.agent/backups/<ts>/.gitignore.user-edits.txt`.
9. **Uninstall without `--purge`**: `.agent/`, `.claude/` gone; `.agentic-development/` remains; state file gone; `.gitignore` block removed.
10. **Uninstall `--purge`**: `.agentic-development/` also gone; user `CLAUDE.md` still present.

### `tests/installer/test_wrapper.sh` (create — Issue I10.3)

- Run `install.sh doctor --target <tmp>` under `bash` → exit reflects doctor result (not an interpreter error).
- Run under `sh`/`dash` → exits `2` with the `BASH_VERSION` guard message.
- Simulate missing PyYAML (`PYTHONPATH` trick or a stub `python3`) → wrapper prints the `pip3 install --user pyyaml` hint and exits `2`.
- Script is self-contained, uses `mktemp -d`, cleans up with `trap`.

### `tests/run_tests.py` (extend if a registry exists)

Ensure `tests/installer/` is discovered by the repo's existing runner so `python3 tests/run_tests.py` includes it.

## RTM (acceptance criteria)

- `[NFR-4.1]` All 10 integration scenarios pass via `pytest tests/installer/test_e2e.py`.
- `[NFR-4.2]` Every test uses `tmp_path`/`tmp_target` — zero mutation of the real repo or `$HOME`.
- `[NFR-1.2]` Idempotency scenario proves a no-change re-install mutates nothing.
- `[NFR-2.2]` Anti-clobber scenario proves a tampered block aborts without `--force` and round-trips with it.
- `[I10.3]` `test_wrapper.sh` passes under `bash`, fails cleanly under `sh`, and surfaces the PyYAML hint.
- Full regression: `python3 -m pytest tests/ -q` shows no pre-existing test broken.

## Verification

```bash
python3 -m pytest tests/installer/test_e2e.py -v
bash tests/installer/test_wrapper.sh
python3 -m pytest tests/installer/ -v        # whole installer suite
python3 -m pytest tests/ -q                  # full regression
python3 tests/run_tests.py                   # repo runner picks up installer tests
```

## Out of scope

- Real Antigravity/Codex IDE behavioral testing — the suite verifies file-layout correctness, not third-party IDE consumption.
- Windows CI — `platform.symlink_supported()` fallback is unit-tested in 063-04; a Windows runner is post-MVP.
