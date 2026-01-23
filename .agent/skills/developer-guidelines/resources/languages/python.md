# Python Developer Guidelines

## Code Quality
- **Type Hinting:** USE type hints for all function arguments and return values.
- **Docstrings:** Use Google-style docstrings for all functions and classes.
- **Formatting:** Follow PEP 8. Use `black` and `isort` if available.

## Testing
- **Pytest:** Use `pytest` as the standard runner.
- **Structure:** Mirror package structure in `tests/`.
- **Fixtures:** Use `conftest.py` for shared fixtures.

## Performance
- **Vectorization:** Use NumPy/Pandas for heavy data processing instead of loops.
- **Generators:** Use generators/iterators for large datasets.
