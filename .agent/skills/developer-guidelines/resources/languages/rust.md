# Rust Developer Guidelines

## Core Principles
- **Borrow Checker:** Work *with* the borrow checker, not against it. Avoid `clone()` unless necessary for ownership transfer.
- **Safety:** STRICTLY prefer safe Rust. Use `unsafe` blocks ONLY when absolutely necessary and document WHY.
- **Error Handling:**
  - Use `Result<T, E>` for recoverable errors.
  - Avoid `.unwrap()`. Use `?`, `.expect("context")`, or match for proper handling.
- **Clippy:** Ensure code passes `cargo clippy` without warnings.
- **Formatting:** Adhere to `cargo fmt`.

## Testing
- Use `#[test]` for unit tests within the same file (usually in a `tests` module).
- Use `tests/` directory for integration tests.
