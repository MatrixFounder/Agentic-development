# Python Developer Guidelines

## Code Quality
- **Ruff:** Use `ruff` for linting and formatting (replaces flak8/isort/black).
- **Type Hinting:** Strictly type all new code. Use `mypy` or `pyright`.
    - **Generics:** Use built-in types `list[str]` (Py3.9+) over `typing.List`.
    - **Self:** Use `typing.Self` (Py3.11+) for methods returning instance.
- **Project Structure:** Use `src/` layout. Manage dependencies with **Poetry** or **UV**.

## Data Validation
- **Pydantic v2:** Use `pydantic.BaseModel` for all data structures, API inputs, and config.
    - **Annotated:** Prefer `Annotated[str, Field(...)]` over `Field()` as default value.
    - **Settings:** Use `pydantic-settings` for environment variables.

## Async Patterns
- **Asyncio:** Use `asyncio.run()` for the entry point.
- **Task Groups:** Use `async with asyncio.TaskGroup() as tg:` (Py3.11+) for structured concurrency instead of `gather()`.
- **Blocking Calls:** Never block the event loop. Use `loop.run_in_executor()` for CPU-bound tasks.

## Testing Standards
- **Pytest:** Use `pytest` exclusively.
- **Fixtures:** Use `yield` fixtures for resource cleanup (DB transactions, file handles).
- **Parametrization:** Use `@pytest.mark.parametrize` for table-driven tests.
- **Mocking:** Use `pytest-mock` (`mocker` fixture) instead of raw `unittest.mock`.

## Performance
- **Generators:** Prefer generator expressions `(x for x in y)` over list comprehensions for large sequences.
- **Itertools:** Use `itertools` for efficient looping.

## Specific Contexts (n8n / Lambda / Embedded)
- **Dependency Constraints:** If Pydantic is unavailable:
    - Use `dataclasses` (StdLib) for structured data.
    - Use `json` module for manual schema validation with defensive `.get()`.
- **Event Loop:** in `n8n` or FaaS, the loop might already be running.
    - Avoid `asyncio.run()`. Use `await` directly if top-level supported, or check loop state.

