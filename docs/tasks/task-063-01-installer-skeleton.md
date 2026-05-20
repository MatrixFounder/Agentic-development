# Task 063-01 — Installer package skeleton + `vendors.yaml` + test scaffold

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 1 — Structure & Stubs `[STUB CREATION]` (per [tdd-stub-first](../../.agent/skills/tdd-stub-first/SKILL.md))
**Predecessor**: none
**Successor**: Task 063-02

## Goal

Create the full `installer/` Python package with **every module's signatures stubbed** (`raise NotImplementedError` + docstrings), the **complete `vendors.yaml`** config, and a Red→Green **E2E smoke test**. After this task, `python3 System/scripts/install.py <cmd>` must not crash on import — [install.py](../../System/scripts/install.py) line 18 already does `from installer.cli import main`.

## Files to create

### Python package — `System/scripts/installer/`

Every module per [ARCHITECTURE §9.2](../ARCHITECTURE.md#9-framework-installer-subsystem). Each public function/class gets a real signature, a docstring describing future logic, and a body `raise NotImplementedError`.

- `__init__.py` — empty package marker.
- `errors.py` — declare class names only (`InstallerError`, `ConfigurationError`, `ConflictError`, `IntegrityError`); full bodies in 063-02.
- `cli.py` — `main(args) -> int`; dispatch on `args.command` to `_cmd_install/_cmd_switch/_cmd_update/_cmd_uninstall/_cmd_doctor`. **Stub handlers print `[stub] <command>` and return `0`** (so the E2E smoke goes Green).
- `vendors.py` — `load_vendors(path) -> dict`, `validate_profile(name, profile, framework_root) -> None`.
- `state.py` — `load_state(target) -> dict | None`, `save_state(target, state) -> None`.
- `framework_root.py` — `ensure_agentic_dev_symlink(target, framework, force) -> Path`, `ensure_agentic_dev_copy(target, framework, force) -> Path`, `guard_target(target, framework) -> None`.
- `symlinks.py` — `link_one(link, source) -> str`, `link_per_item(target_dir, source_dir) -> dict`, `link_folder(target, source) -> str`, `make_dir(target) -> None`.
- `copy.py` — `copy_tree(src, dst, ignore_extra=()) -> None`.
- `managed_block.py` — `inject_block(file_path, content, marker_pair, state_hash=None, force=False) -> str`, `strip_block(file_path, marker_pair) -> None`.
- `bootstrap.py` — `apply_bootstrap(target, framework, profile, state, force) -> dict`, `is_protected(filename) -> bool`.
- `gitignore.py` — `update_gitignore(target, profile, state) -> str`, `scan_local_exceptions(target) -> list[str]`.
- `backup.py` — `create_snapshot(paths, target, label) -> Path`, `apply_retention(target, max_backups=5) -> None`.
- `platform.py` — `symlink_supported(probe_dir=None) -> bool`, `is_windows() -> bool`.

### Config — `System/scripts/vendors.yaml`

**Full content** (not a stub — pure config, single task per [planning-decision-tree](../../.agent/skills/planning-decision-tree/SKILL.md) §1). Exactly the schema from [TASK.md Issue I1.3](../TASK.md) and the approved plan: `version: 1`, `defaults` (`agent_components` + `root_components`), and 5 vendor profiles `claude / antigravity / codex / cursor / gemini-cli` with `bootstrap_strategy`, `bootstrap_file`, `bootstrap_aliases`, `bootstrap_source`, `vendor_dir`, `git_root_required`, `components`.

### Test scaffold — `tests/installer/`

- `__init__.py` — empty.
- `conftest.py` — pytest fixtures: `framework_root` (path to this repo), `tmp_target` (a `tmp_path` git-init'd dir).
- `test_e2e.py` — one smoke test `test_cli_dispatches_all_subcommands`: build a minimal `argparse.Namespace` per subcommand, call `installer.cli.main()`, assert it returns `0` (the stubbed value). This is the Stub-phase E2E test — 063-09/063-11 replace it with real-behavior assertions.

## RTM (acceptance criteria)

- `[NFR-3.1]` All 12 modules under `System/scripts/installer/` exist; every public symbol has a signature + docstring + `NotImplementedError` body (except `cli.py` stub handlers, which return `0`).
- `[NFR-3.2]` `System/scripts/vendors.yaml` exists, parses as valid YAML, has `version: 1`, a `defaults` block, and exactly the 5 vendor keys.
- `[NFR-3.3]` `installer.cli.main()` routes each of `install/switch/update/uninstall/doctor` to a distinct handler.
- `[NFR-3.4]` `tests/installer/test_e2e.py` smoke test passes (Green on stubs).
- `[NFR-5.1]` No third-party imports beyond `yaml`; everything else stdlib.

## Verification

```bash
# NFR-3.1 — all modules import cleanly
python3 -c "import sys; sys.path.insert(0,'System/scripts'); \
import installer.cli, installer.vendors, installer.state, installer.framework_root, \
installer.symlinks, installer.copy, installer.managed_block, installer.bootstrap, \
installer.gitignore, installer.backup, installer.platform, installer.errors; print('imports OK')"

# NFR-3.2 — vendors.yaml shape
python3 -c "import yaml; d=yaml.safe_load(open('System/scripts/vendors.yaml')); \
assert d['version']==1; assert set(d['vendors'])=={'claude','antigravity','codex','cursor','gemini-cli'}; \
assert 'defaults' in d; print('vendors.yaml OK')"

# NFR-3.3 + entry-point — no import crash
python3 System/scripts/install.py doctor --target /tmp ; echo "exit=$?"

# NFR-3.4 — E2E smoke
python3 -m pytest tests/installer/test_e2e.py -v

# NFR-5.1 — no unexpected deps
! grep -rEn '^\s*import (requests|click|rich|pydantic)' System/scripts/installer/
```

## Out of scope

- Any real logic — every Stage-2 task replaces the stubs of its module.
- `errors.py` exception bodies — declared here, implemented in 063-02.
