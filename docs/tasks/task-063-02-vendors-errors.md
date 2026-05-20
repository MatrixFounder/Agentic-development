# Task 063-02 — Errors + vendor profile loader & validator

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-01
**Successor**: Task 063-03

## Goal

Implement the error hierarchy and the `vendors.yaml` loader + per-action schema validator. The validator must reject malformed profiles **before any FS operation** (TASK Issue I1.4) — this is the first real defensive layer.

## Files to edit / create

### `System/scripts/installer/errors.py` (implement — Issue I1.5)

- `class InstallerError(Exception)` — field `exit_code: int = 1`; `__init__(self, message, *, exit_code=None)`.
- `class ConfigurationError(InstallerError)` — `exit_code = 2`.
- `class ConflictError(InstallerError)` — `exit_code = 3`.
- `class IntegrityError(InstallerError)` — `exit_code = 4`.

### `System/scripts/installer/vendors.py` (implement — Issue I1.4)

- `load_vendors(path: Path) -> dict` — parse YAML, return typed dict; raise `ConfigurationError` on malformed YAML or missing `version`/`vendors`.
- `validate_profile(name: str, profile: dict, framework_root: Path) -> None` — per-action schema validation, raising `ConfigurationError` with the exact offending field path:
  - `bootstrap_strategy` ∈ `{at_import, marker_block, none}`; for `marker_block`, `bootstrap_source` is required.
  - For each component, validate per the action table in [TASK.md §I1.4](../TASK.md):
    - `link_per_item` / `link_folder` / `copy` → `source` **required** and must resolve to an existing path under `framework_root` (unless `optional: true`); `path` required.
    - `mkdir` → `source` **forbidden**; `path` required.
  - `git_root_required` (if present) must be `bool`.
- `resolve_profile(vendors: dict, name: str) -> dict` — merge `defaults.agent_components` + `defaults.root_components` + the vendor's own `components` into one ordered component list.

### `tests/installer/test_vendors.py` (create — Issue I10.1)

Unit tests on `tmp_path`:
- Valid profile (each of the 5 real vendors loaded from the repo's `vendors.yaml`) → no raise.
- `marker_block` without `bootstrap_source` → `ConfigurationError`.
- `mkdir` action with a `source` key → `ConfigurationError`.
- `link_folder` with a `source` that doesn't exist in `framework_root` and no `optional` → `ConfigurationError`.
- `link_folder` with non-existent `source` **and** `optional: true` → no raise.
- Malformed YAML / missing `version` → `ConfigurationError`.
- Each `ConfigurationError` carries `exit_code == 2`.

## RTM (acceptance criteria)

- `[FR-2.1]` `load_vendors()` parses `vendors.yaml`, returns typed structure, raises `ConfigurationError` on malformed input.
- `[FR-2.2]` `validate_profile()` enforces the per-action field table (source required/forbidden, path required).
- `[FR-2.3]` `source` paths are resolved against `framework_root`; missing non-optional source → `ConfigurationError` naming the field.
- `[FR-2.4]` `bootstrap_strategy` enum + `marker_block ⇒ bootstrap_source` enforced.
- `[FR-14.1]` `git_root_required` accepted and type-checked as a vendor-profile field.
- `[I1.5]` `InstallerError` hierarchy with exit codes 1/2/3/4 implemented; all validation failures raise `ConfigurationError` (exit 2).

## Verification

```bash
python3 -m pytest tests/installer/test_vendors.py -v
# Real config must validate against itself:
python3 -c "import sys; sys.path.insert(0,'System/scripts'); \
from pathlib import Path; from installer.vendors import load_vendors, validate_profile; \
d=load_vendors(Path('System/scripts/vendors.yaml')); fr=Path('.').resolve(); \
[validate_profile(n,p,fr) for n,p in d['vendors'].items()]; print('all 5 profiles valid')"
python3 -m pytest tests/installer/ -q   # no regression in sibling tests
```

## Out of scope

- Consuming the validated profile in `install` — that wiring is Task 063-09.
- `git_root_required` runtime *check* (FR-14 check half) — Task 063-09.
