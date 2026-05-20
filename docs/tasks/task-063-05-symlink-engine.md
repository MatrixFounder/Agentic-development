# Task 063-05 — Symlink engine

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-04
**Successor**: Task 063-06

## Goal

Implement the four component actions (`link_one`, `link_per_item`, `link_folder`, `mkdir`) with relative-path computation, idempotency, reachability checks, and the canonical-path traversal guard (ARCHITECTURE §9.6).

## Files to edit / create

### `System/scripts/installer/symlinks.py` (implement — Issues I3.1–I3.4)

- `link_one(link: Path, source: Path, framework_root: Path) -> str` (I3.1):
  - `source` missing → raise `ConflictError`.
  - Create relative symlink via `os.path.relpath(source, start=link.parent)`.
  - `link` already a correct symlink to `source` → no-op, return `"already-linked"`.
  - `link` exists pointing elsewhere → if it's ours (resolves inside `.agentic-development/`) atomic-replace via `os.replace`; else `ConflictError`.
  - **Reachability**: after creation `os.stat(link, follow_symlinks=True)`; on failure delete the link and raise `IntegrityError` (caller may downgrade to copy).
  - **Canonical-path guard** (§9.6): assert `link.resolve().is_relative_to(framework_root.resolve())`; if the resolved target escapes `framework_root`, delete the link and raise `ConflictError`. Defends against crafted `../../../` source names.
  - Return one of `"created" | "already-linked" | "replaced"`.
- `link_per_item(target_dir: Path, source_dir: Path, framework_root: Path) -> dict` (I3.2):
  - `mkdir -p target_dir`; iterate `os.scandir(source_dir)` skipping dotfiles (`.DS_Store`, `.git*`).
  - Call `link_one` per entry; collect counters `{created, already_linked, replaced, skipped, conflicts}`.
  - A per-item `ConflictError` is caught → counted as `skipped` (soft-conflict — user file wins), not fatal.
- `link_folder(target: Path, source: Path, framework_root: Path) -> str` (I3.3) — single `link_one` call.
- `make_dir(target: Path) -> None` (I3.4) — `mkdir -p`; drop a `.gitkeep`; idempotent.

### `tests/installer/test_symlinks.py` (create — Issue I10.1)

- `link_one` fresh → relative symlink, `readlink` starts with `../`, resolves to source.
- `link_one` re-run → `"already-linked"`, no FS change.
- `link_one` over a foreign file → `ConflictError`.
- `link_one` over a stale-but-ours symlink → `"replaced"`.
- Reachability: source on a path made unreachable → `IntegrityError`, link removed.
- Canonical guard: a source crafted to resolve outside `framework_root` → `ConflictError`, link removed.
- `link_per_item`: mixed dir (framework items + one pre-existing user file) → user file `skipped`, rest `created`; counters correct; dotfiles ignored.
- `make_dir` idempotent; `.gitkeep` present.

## RTM (acceptance criteria)

- `[FR-4.1]` `link_one` creates **relative** symlinks via `os.path.relpath`.
- `[FR-4.2]` Idempotent — correct existing symlink is a no-op.
- `[FR-4.3]` Reachability check (`os.stat(follow_symlinks=True)`) after every creation; failure removes the link.
- `[FR-4.4]` Canonical-path guard rejects symlinks resolving outside `framework_root`.
- `[FR-4.5]` `link_per_item` returns counters and treats per-item conflicts as non-fatal skips.
- `[FR-4.6]` `link_folder` and `mkdir` actions implemented and idempotent.

## Verification

```bash
python3 -m pytest tests/installer/test_symlinks.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- Cross-FS downgrade *policy* (catch `IntegrityError` → copy) — decided by the `install` orchestration in Task 063-09.
- Driving these actions from a vendor profile — Task 063-09.
