# Task 063-06 — Managed-block engine

**Parent**: [docs/PLAN.md](../PLAN.md) — Framework Installer (Task 063)
**Stage**: 2 — Core Logic `[LOGIC IMPLEMENTATION]`
**Predecessor**: Task 063-05
**Successor**: Task 063-07

## Goal

Implement the shared marker-block engine used by both `.gitignore` (063-08) and bootstrap files (063-07). SHA-256 hashing of the block content is the anti-clobber guarantee (ARCHITECTURE §9.5 — *no silent clobber*).

## Files to edit / create

### `System/scripts/installer/managed_block.py` (implement — Issues I4.1–I4.3)

- Marker pairs (I4.2):
  - `GITIGNORE_MARKERS = ("# >>> agentic-development framework >>>", "# <<< end agentic-development framework <<<")`.
  - `MARKDOWN_MARKERS = ("<!-- >>> agentic-development >>> -->", "<!-- <<< agentic-development <<< -->")`.
- `block_hash(content: str) -> str` — `"sha256:" + hashlib.sha256(content.encode()).hexdigest()`.
- `extract_block(text: str, marker_pair) -> str | None` — return the current inner block content, or `None` if no opening marker.
- `inject_block(file_path: Path, content: str, marker_pair, *, state_hash: str | None = None, force: bool = False, backup_dir: Path | None = None) -> str` (I4.1, I4.3):
  - File absent → create it containing exactly the marker-wrapped block; return new hash.
  - Opening marker present → compute hash of the **current** block:
    - matches `state_hash` (or `state_hash is None`, i.e. first run) → atomic rewrite (temp + `os.replace`); return new hash.
    - mismatch → if `not force` raise `IntegrityError` with a `difflib.unified_diff` (expected-vs-current); if `force`, write the current block to `backup_dir/<filename>.user-edits.txt` first, then rewrite.
  - No marker → append the marker-wrapped block at EOF.
- `strip_block(file_path: Path, marker_pair) -> None` — remove the marker block (and its trailing blank line) from the file, leaving the rest intact; no-op if absent. Used by `uninstall`/`switch`.

### `tests/installer/test_managed_block.py` (create — Issue I10.1)

- Inject into a non-existent file → file created, content marker-wrapped, hash returned.
- Inject into a file with prior user content → user content preserved, block appended.
- Re-inject with matching `state_hash` → atomic rewrite, new hash returned.
- Re-inject after a manual edit (hash mismatch) + `force=False` → `IntegrityError`, diff in the message, **file untouched**.
- Same, `force=True` → block rewritten, old block saved to `<file>.user-edits.txt` in `backup_dir`.
- `strip_block` removes only the block, leaves surrounding content + is a no-op when absent.
- `extract_block` returns `None` when no marker, exact inner content otherwise.

## RTM (acceptance criteria)

- `[FR-5.1]` `inject_block` creates / appends / rewrites per the marker state.
- `[FR-5.2]` SHA-256 hash returned and used for mismatch detection.
- `[FR-5.3]` Hash mismatch without `--force` → `IntegrityError` carrying a unified diff; file is **not** modified.
- `[FR-5.4]` `--force` saves the user version to `.user-edits.txt` before overwrite.
- `[FR-5.5]` Atomic write (temp + `os.replace`).
- `[FR-5.6]` Both marker formats (`.gitignore` `#`-comment, markdown `<!-- -->`) supported via the `marker_pair` parameter.
- `[NFR-2.1]` No code path overwrites a managed block whose hash diverged from state without explicit `--force`.

## Verification

```bash
python3 -m pytest tests/installer/test_managed_block.py -v
python3 -m pytest tests/installer/ -q
```

## Out of scope

- The actual `.gitignore` block *content* — Task 063-08.
- Bootstrap-file *content* — Task 063-07.
