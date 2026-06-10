# Release Checklist (Framework Version Bump)

Use this checklist for every framework release.

## 1. Scope and Versioning

1. Confirm release scope and target version.
2. Update version references in:
   - `README.md`
   - `README.ru.md`
   - `CHANGELOG.md`
   - `CHANGELOG.ru.md`
3. Add migration notes if behavior or file contracts changed.

## 2. Documentation Sync

1. Verify prompt file names match real files in `System/Agents/`.
2. Verify workflow docs match `.agent/workflows/` names and command forms.
3. Verify skill docs match `.agent/skills/` and tool names in `.agent/tools/schemas.py`.
4. Update source map if needed: `System/Docs/SOURCE_OF_TRUTH.md`.

## 3. Mandatory Validation

Run from repository root:

```bash
python System/scripts/check_prompt_references.py --root .
python System/scripts/security_lint.py --root .
python System/scripts/smoke_workflows.py --root .
python System/scripts/validate_skills.py --root . --quiet
PYTHONPATH=. pytest -p no:cacheprovider tests/test_tool_runner.py tests/test_tool_runner_security_contract.py tests/test_spec_validator.py -q
```

If any gate is intentionally deferred, document rationale and risk in release notes.

## 4. Optional Product Handoff Safety (only when modifying `skill-product-handoff`)

1. Confirm CLI contracts for:
   - `.agent/skills/skill-product-handoff/scripts/sign_off.py`
   - `.agent/skills/skill-product-handoff/scripts/verify_gate.py`
   - `.agent/skills/skill-product-handoff/scripts/compile_brd.py`
2. Optional targeted tests:

```bash
PYTHONPATH=. pytest -p no:cacheprovider tests/test_product_handoff_scripts.py -q
```

## 5. Release Package

1. Ensure `.github/workflows/framework-gates.yml` is up to date.
2. Update backlog status in the current release/iteration backlog file under `Backlog/` (do not hardcode a dated filename).
3. Tag the release in VCS and publish notes.
4. Announce breaking changes and migration steps.
