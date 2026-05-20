# Task 063-04 — `.agentic-development/` root management + platform

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-03
**Successor**: Task 063-05

## Goal

Implement creation/validation of the `target/.agentic-development/` root (symlink or copy mode), the pre-flight target guards, the deep-copy helper, and Windows platform detection/fallback.

## Files to edit / create

### `System/scripts/installer/platform.py` (implement — FR-13)

- `is_windows() -> bool` — `platform.system() == "Windows"`.
- `symlink_supported(probe_dir: Path | None = None) -> bool` — attempt a real symlink inside a `tempfile.TemporaryDirectory()` (or `probe_dir`); return `False` on `OSError`/`NotImplementedError`. Result drives the auto-fallback to `--mode copy`.

### `System/scripts/installer/copy.py` (implement — Issue I2.2)

- `IGNORE_NAMES = {".git", ".venv", "__pycache__", ".pytest_cache", ".DS_Store", "node_modules", ".hypothesis", ".ruff_cache"}` + glob `*.pyc`.
- `copy_tree(src: Path, dst: Path) -> None` — `shutil.copytree(src, dst, symlinks=False, ignore=shutil.ignore_patterns(...))`. `symlinks=False` resolves the framework's internal symlinks (e.g. `.claude/skills → .agent/skills`) into real files.

### `System/scripts/installer/framework_root.py` (implement — Issues I2.1, I2.2, I2.3)

- `guard_target(target: Path, framework: Path) -> None` (I2.3):
  - `target.resolve() == framework.resolve()` → `ConflictError` (names both paths).
  - `target.resolve().is_relative_to(framework.resolve())` → `ConflictError`.
- `ensure_agentic_dev_symlink(target, framework, force) -> Path` (I2.1):
  - Absent → create relative symlink via `os.path.relpath(framework, target)`; if `relpath` escapes upward beyond a sane depth use the absolute path.
  - Present + correct (symlink resolving to `framework`) → no-op + log.
  - Present + foreign → `ConflictError` unless `force` (then snapshot via `backup.create_snapshot` + replace).
  - Reachability check after creation (`os.stat(follow_symlinks=True)`).
- `ensure_agentic_dev_copy(target, framework, force) -> Path` (I2.2):
  - Absent → `copy.copy_tree(framework, target/".agentic-development")`.
  - Present + our copy → no-op.
  - Present + foreign → `ConflictError` unless `force` (snapshot + replace).
- `ensure_agentic_dev(target, framework, mode, force) -> Path` — dispatch on `mode`; if `mode == "symlink"` and `not symlink_supported()` → warn + downgrade to copy.
- `validate_framework(framework: Path) -> None` — assert `.agent/skills/` and `System/` exist; else `ConfigurationError` listing what's missing.

### `tests/installer/test_framework_root.py` (create — Issue I10.1)

- `guard_target`: target == framework → `ConflictError`; target inside framework → `ConflictError`; sibling dir → OK.
- `ensure_agentic_dev_symlink`: fresh create → relative symlink resolves to framework; re-run → no-op; foreign dir present → `ConflictError`; `force=True` → snapshot taken + symlink created.
- `ensure_agentic_dev_copy`: fresh copy excludes every `IGNORE_NAMES` entry and `*.pyc`.
- `symlink_supported` returns a bool and never raises.
- `validate_framework` on an incomplete tree → `ConfigurationError`.

## RTM (acceptance criteria)

- `[FR-3.1]` Symlink mode creates a relative symlink; idempotent on re-run.
- `[FR-3.2]` Copy mode uses `shutil.copytree(symlinks=False)` with the ignore-list.
- `[FR-3.3]` Foreign `.agentic-development/` → `ConflictError` unless `--force` (then backup first).
- `[FR-3.4]` `guard_target` rejects target == framework and target ⊂ framework.
- `[FR-13.1]` `symlink_supported()` probes via temp dir; never raises.
- `[FR-13.2]` `mode=symlink` auto-downgrades to copy when symlinks unsupported.

## Verification

```bash
python3 -m pytest tests/installer/test_framework_root.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- Component installation into the root — Tasks 063-05+.
- Calling `ensure_agentic_dev` from the `install` flow — Task 063-09.
