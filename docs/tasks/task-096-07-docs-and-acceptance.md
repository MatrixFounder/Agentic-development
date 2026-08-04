# Task 096.7 — `System/Docs/`, CHANGELOG, full acceptance run


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | a 38-case selftest | 128 cases | baseline §9 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R11 · **Acceptance:** A1–A11 · **Stage:** 6 of 6 · **Dependencies:** all

<!-- contract:goal -->

## Goal

Record the new reality, then run every acceptance criterion in the TASK and report the result of
each — including any that fails.

<!-- contract:changes -->

## Changes

### Documentation

| File | Change |
| :--- | :--- |
| `System/Docs/SKILLS.md` | New row for `artifact-formalizer` (TIER 2); updated row for `documentation-standards` (§5.5) |
| `CHANGELOG.md` / `CHANGELOG.ru.md` | Version entry: register doctrine, the skill, the four authoring surfaces |
| `docs/ARCHITECTURE.md` | Re-read §7.3 against what shipped — threshold, paths, skill name |

### Gates

```sh
python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/artifact-formalizer
bash .agent/skills/skill-spec-validator/scripts/tests/run_tests.sh     # 47 OK
python3 -m pytest tests/ -q                                            # 370 passed
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py
python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py
python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/TASK.md docs/PLAN.md
```

`check_positional_refs.py` runs **after** every edit is final — `documentation-standards` §4.1.
This task adds §5.5, so any reference to a later-numbered section shifts.

<!-- contract:tests -->

## Test cases

- **TC-ACC-01…11** — one case per acceptance criterion A1–A11, each reporting pass or fail with
  the command output that establishes it.
- **TC-ACC-12** — corpus re-measurement: re-run the TASK §1.1 script and confirm the baseline
  figures are reproducible. A changed baseline means the measurement, not the corpus, moved.
- **TC-REG-01** — `git diff --stat` shows no file changed outside the plan's declared scope.

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] `SKILLS.md` and both CHANGELOGs updated
- [ ] §7.3 of ARCHITECTURE matches the shipped threshold, paths and skill name
- [ ] All six gate commands run at repository root and their real output recorded
- [ ] Every A1–A11 reported with its verdict; a failure is reported, never omitted
- [ ] No file changed outside the declared scope

## Notes

**Reporting a failure is the deliverable, not the exception.** A8 requires this TASK and PLAN to
scan at zero `warn`. If either fails, the fix is the prose. Moving a threshold to obtain a green
scan is the outcome the TASK's A8 verification clause was rewritten to forbid.
