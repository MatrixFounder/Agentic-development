# Framework Audit: TASK 097 — Register scanner masking

**Date:** 2026-08-04
**Auditor:** Self-Improvement Verificator (Mode A — SPECIFICATION AUDIT)
**Target:** `docs/TASK.md` (TASK 097)
**Status:** **APPROVED** after round 2

## 0. Emergency Bypass

- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

No flag is set. No bypass was used.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | Task ID `097`, slug `scanner-masking-classification-inversion`, archive name present |
| **Tier Protection** | Pass | No TIER 0 skill is edited; see §1.1 |
| **Documentation** | Pass after F2 | R9, R13 and R15 name every document the change touches |
| **Atomicity** | Pass | 15 requirements, each with a test obligation in T1–T13 |
| **Rollback Plan** | Deferred | Backup and rollback are Mode B checks against `docs/PLAN.md` |

### 1.1 Blocking conditions (skill §4)

| Condition | Result |
| :--- | :--- |
| `core-principles` or `skill-safe-commands` removed from an agent | Not triggered; neither skill is edited |
| `GEMINI.md` modified without a `System/Docs` update | Not triggered; `GEMINI.md` is not edited |
| New workflow without a trigger declared | Not triggered; no workflow is added |

## 2. Findings

### F1 — R12 contradicted §1.1 (round 1, fixed)

§1.1 stated that the reproducing input is valid Markdown and needs no repair. R12 then required
editing the shipped templates. Read together, the two made the remedy ambiguous.

**Resolution.** §1.2 now separates two inputs. Case A is a marker cited in a code span, valid, and
present in 20 files that stay unedited (R12a). Case B is an HTML comment whose body contains
`-->`, malformed, and present in the two templates (R12).

**Evidence added.** `markdown-it` in `commonmark` mode closes the Case-B comment at the inner
`-->` and renders the remainder as a paragraph. The Case-B remedy therefore rests on rendering, not
on the scanner.

### F2 — No requirement covered `CHANGELOG` or `System/Docs` (round 1, fixed)

The skill checklist requires the task to carry its own documentation updates. R9 covered
`SKILL.md` §2 and R13 covered `measurement-baseline.md`. Neither reached `CHANGELOG.md`,
`CHANGELOG.ru.md`, or `System/Docs/SKILLS.md`.

**Resolution.** R15 added, with test obligation T14.

### F3 — Migration check does not apply (round 1, no action)

The skill asks how existing sessions migrate. This change alters one script's internal masking and
its output text. No session state, artifact schema, or anchor is affected, so no migration path is
required. Recorded rather than left silent.

## 3. Risk Analysis

| ID | Risk | Detected by |
| :--- | :--- | :--- |
| RA-1 | The corrected masking restores 61,889 letters to the rules, so documents that scanned clean may report findings. | OQ-1; the advisory CI step runs before and after |
| RA-2 | A single-pass tokenizer masks less than the sequential loop and may leave code scanned as prose. | T3 and the 128 existing selftest cases |
| RA-3 | The paragraph bound raises odd-parity documents from 14 to 17 by refusing to pair backticks across paragraphs. | R6 names each one; T6 pins the behaviour |
| RA-4 | Naming a malformed input could be read as a gate and fail CI. | R7 and T7 fix exit 0 for every input case |

## 4. Verdict & Actions

**APPROVED.**

Round 1 raised F1 and F2. Both were applied to `docs/TASK.md` before this verdict. Round 2
re-checked the document:

- `scan_register.py docs/TASK.md --terms docs/ARCHITECTURE.md` → `0 warn / 0 info`, exit 0
- `validate.py --mode task docs/TASK.md` → 15 requirements found, exit 0

Audit rounds used: 2 of the 3 the workflow allows.

**Carried into Mode B.** The rollback and backup checks apply to `docs/PLAN.md` and are audited
there, against risks RA-1 through RA-4.

---

# Mode B — PLAN AUDIT

**Date:** 2026-08-04
**Target:** `docs/PLAN.md` (TASK 097)
**Status:** **APPROVED** round 1

## 5. Compliance Checklist (skill §2 Mode B)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | Pass | §0.3 captures a baseline; every stage carries a pass condition; Stage 6 runs the whole `framework-gates.yml` set |
| **Rollback** | Pass | §0.1 backs up 9 files to gitignored `.agent/archive/`; §0.2 names two restore routes |
| **Atomic Updates** | Pass | 8 stages, each with its own verification and a stop condition in §0.4 |
| **Test Coverage** | Pass | F1–F6 fixtures, a corpus sweep, and mutation pins for stages 4b and 4c |

## 6. Scope change since Mode A

The operator folded two review findings into the task. TASK 097 §1.3 records them as D2 and D3,
and both were reproduced before being written down. Requirements grew from 16 to 21; the plan gained
stages 4b and 4c. `validate.py --mode plan` reports all 21 covered.

## 7. Risk register, updated

| ID | Risk | State |
| :--- | :--- | :--- |
| RA-1 | Restored prose surfaces findings in documents that scanned clean | Open; OQ-1 measures it in Stage 6 |
| RA-2 | The tokenizer masks differently and breaks the 128 existing cases | **Retired by measurement.** A patched copy of the skill reports 128/128 and 18/18 |
| RA-3 | The paragraph bound raises odd-parity documents from 14 to 17 | Open; R6 names each, T6 pins the behaviour |
| RA-4 | A named input defect is read as a gate and fails CI | Closed by R7 and T7 |
| RA-5 | `--allow-missing` hides a mistyped path in CI | Bounded: the flag is passed for two files, and absence without it exits 3 |
| RA-6 | Per-pattern rule-3 probing lengthens `--probe` | 24 additional scans of a one-line string; measured in Stage 4c |

## 8. Verdict & Actions

**APPROVED.** No blocking condition from skill §4 is triggered. No bypass flag is set.

Round 1 raised no finding requiring a redraft. Evidence:

- `scan_register.py docs/PLAN.md --terms docs/ARCHITECTURE.md` → `0 warn / 0 info`, exit 0
- `validate.py --mode plan docs/PLAN.md docs/TASK.md` → all 21 requirements covered

Plan audit rounds used: 1 of the 3 the workflow allows. Execution may begin at §3 of the workflow.
