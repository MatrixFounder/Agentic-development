# Task 063-09 — Conflict prevention + `install` end-to-end

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-08
**Successor**: Task 063-10

## Goal

Implement the pre-flight conflict classifier and wire the full `install` subcommand end-to-end in `cli.py` — the 10-step algorithm from [TASK.md §Алгоритм install](../TASK.md) / the approved plan. This task makes the installer actually *do something*.

## Files to edit / create

### `System/scripts/installer/conflict.py` (create — Issues I6.1–I6.4)

- `HARD_CONFLICT_NAMES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md"}`; settings files (`*/settings.json`), `System/`, `.codex/config.toml` are also hard.
- `classify_path(target_path, framework_root, state) -> str` (I6.1) → one of:
  - `safe` — does not exist.
  - `our` — symlink resolving inside `.agentic-development/`, **or** a file carrying a managed block whose hash is in `state`.
  - `hard_conflict` — foreign and in the hard list.
  - `soft_conflict` — foreign per-item path under `.claude/skills/` `.agent/skills/` etc.
- `preflight_scan(target, framework_root, components, profile, state, skip_set) -> dict` (I6.3) — classify every component path; return `{to_install, hard_skips, soft_skips, needs_force}`. Honors `--skip` (I6.4 — those paths recorded with reason `"--skip flag"`).
- `reclassify_before_write(path, framework_root, state) -> str` — TOCTOU re-check (ARCHITECTURE §9.6): re-run `classify_path` immediately before each write; a path that became `hard_conflict` since the scan is skipped + warned.
- `system_link_decision(target, force_system_link) -> str` (I6.2) — `"link" | "skip" | "force"`; foreign `System/` defaults to `skip` with the plan's warning message unless `--force-system-link`.

### `System/scripts/installer/cli.py` — implement `_cmd_install` (FR-1, FR-8)

The 10-step algorithm:
1. Resolve framework (`--from` → `$AGENTIC_DEV_ROOT` → `--installer-script-dir`); `validate_framework`.
2. Resolve target; `guard_target`; if `profile.git_root_required` and no `target/.git/` → warning, require `--force` (**FR-14 runtime check**).
3. `load_vendors` + `validate_profile` (063-02) — crash early on bad config.
4. `ensure_agentic_dev` (063-04) — symlink|copy.
5. `preflight_scan` (063-09) — classify; `--dry-run` stops here and prints `N to install / M skipped / K need --force`.
6. `apply_bootstrap` (063-07).
7. Execute components via `symlinks` / `copy` (063-05/063-04), each preceded by `reclassify_before_write`; `IntegrityError` (cross-FS) → downgrade that component to copy + warn.
8. `update_gitignore` (063-08) unless `--no-gitignore`.
9. `save_state` (063-03) — vendor, mode, hashes, `managed_paths`, `skipped_components`.
10. Print summary (`created/linked/copied/skipped`).

Stub→logic transition for the E2E test from 063-01: `_cmd_install` now returns `0` on success, non-zero `InstallerError.exit_code` on failure.

### `tests/installer/test_conflict.py` (create — Issue I10.1)

- `classify_path`: absent → `safe`; our symlink → `our`; foreign `CLAUDE.md` → `hard_conflict`; foreign `.claude/skills/x` → `soft_conflict`.
- `preflight_scan` over a mixed tree → correct bucket counts; `--skip` entries land in `hard_skips`/recorded.
- `reclassify_before_write`: a path that flips to foreign between scan and write → returns `hard_conflict`.
- `system_link_decision`: absent → `link`; foreign + no flag → `skip`; foreign + `--force-system-link` → `force`.

### Extend `tests/installer/test_e2e.py`

Replace the 063-01 stub assertion: a real `install` into a `tmp_target` produces `.agentic-development` symlink, `.agent/skills/*` symlinks, `CLAUDE.agentic.md`, a `.gitignore` block, and a state file; exit `0`. Re-run → `0 created, N already linked` (NFR-1 idempotency).

## RTM (acceptance criteria)

- `[FR-1.1]` `install` runs the 10-step algorithm end-to-end and returns proper exit codes.
- `[FR-8.1]` `classify_path` produces the 4 categories per the policy table.
- `[FR-8.2]` Hard conflicts → skip + warning + recorded in `state["skipped_components"]`; `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` never overwritten even with `--force`.
- `[FR-8.3]` Soft conflicts → item skipped, surfaces in `.gitignore` `!`-exceptions.
- `[FR-8.4]` `--dry-run` stops after the scan with the summary report; zero FS mutations.
- `[FR-8.5]` `--skip COMPONENT,...` excludes paths, recorded with reason.
- `[FR-8.6]` TOCTOU re-check before every write (`reclassify_before_write`).
- `[FR-14.2]` `git_root_required` runtime check warns + requires `--force` when `target/.git/` is absent.
- `[NFR-1.1]` Re-running `install` with no source changes → `0 created`.

## Verification

```bash
python3 -m pytest tests/installer/test_conflict.py tests/installer/test_e2e.py -v
# Live smoke into a temp project:
T=$(mktemp -d); (cd "$T" && git init -q)
python3 System/scripts/install.py install --vendor claude --target "$T" --from "$PWD" --dry-run
python3 System/scripts/install.py install --vendor claude --target "$T" --from "$PWD"
test -L "$T/.agentic-development" && test -L "$T/.agent/skills/brainstorming" && test -f "$T/.agentic-installer-state.json"
python3 System/scripts/install.py install --vendor claude --target "$T" --from "$PWD" | grep -qi 'already'
rm -rf "$T"
python3 -m pytest tests/installer/ -q
```

## Out of scope

- `switch` / `uninstall` / `update` / `doctor` — Task 063-10.
- Full integration recipe (copy mode, anti-clobber, switch chains) — Task 063-11.
