---
name: skill-spec-validator
description: Validates conformance between TASK.md (RTM) and PLAN.md (Atomic Checklists).
tier: 2
version: 1.1
---

# Skill: Spec Validator

> [!IMPORTANT]
> **TIER 2 (High Integrity)**: This skill acts as a mechanical gatekeeper for the `/vdd-enhanced` workflow.

## 1. Purpose
To strictly enforce "Requirements Hardening" by mechanically verifying that:
1.  `TASK.md` contains a Requirements Traceability Matrix (RTM).
2.  `PLAN.md` explicitly covers every item in the RTM using Atomic Checklists.

## 2. Usage

### Mode A: TASK Validation
**Trigger**: After Analysis Phase.
**Command**:
```bash
python3 scripts/validate.py --mode task /absolute/path/to/docs/TASK.md
```
**Checks**:
- Presence of an RTM heading (h2–h4), matched flexibly: `## Requirements Traceability [Matrix]`,
  `## N. ... (RTM)`, and the bare `### N. Requirements (RTM)` form are all accepted.
- Columns `ID`, `Requirement`.

### Mode B: PLAN Validation
**Trigger**: After Planning Phase.
**Command**:
```bash
python3 scripts/validate.py --mode plan /absolute/path/to/docs/PLAN.md /absolute/path/to/docs/TASK.md
```
**Checks**:
- Every RTM `ID` in TASK appears as a whole token somewhere in PLAN — in a step heading
  (`## Step 1 — ... (R1)`) or a `- [ ] R1 ...` bullet. `R1` does not satisfy `R10`.

## 3. Failure Handling
- **Exit Code 1**: Issues found. Orchestrator should trigger a **Correction Loop** (instruct Analyst/Planner to fix).
- **Bypass**: If validation is buggy, add the bypass token — `BYPASS_VALIDATION` in square brackets —
  to `TASK.md`.
  > [!WARNING]
  > The bypass is a **bare substring test anywhere in `TASK.md`**, so a spec that merely *mentions*
  > the token switches its own gate off and prints `Validation bypassed …` with exit 0 — which reads
  > like a pass. Write it only when you mean it (that is why this section spells the token out
  > instead of quoting it). Pinned by a test, deliberately not "fixed": tightening it is a behavior
  > change to a live gate.

## 4. Dependencies
- Python 3 (stdlib only)
- `validate.py` (in `scripts/`)

## Execution Mode
- **Mode:** script-first. The whole judgement is mechanical — two regex matchers and a table
  parser. Nothing here is prompt-side; if a matcher disagrees with an artifact, that is a finding
  for a human, not something to reason around.

## Script Contract
- **Command:** `python3 scripts/validate.py --mode task <TASK.md>` ·
  `python3 scripts/validate.py --mode plan <PLAN.md> <TASK.md>`
- **Exit codes:** `0` conforming (or bypassed) · `1` non-conforming / file missing / usage error
  inside a mode · `2` argparse rejection (unknown `--mode`).
- **Outputs:** one verdict line on stdout — `Success: Found N requirements…`,
  `Success: All N requirements covered…`, `Error: …` naming the uncovered IDs — preceded by a
  `Note: …` line whenever the RTM section held more than one table (RF-6): how many tables were
  read as one RTM, and which tables were **not** read, named by their columns. The verdict may
  cover part of a section; it may not do so quietly.
- **Idempotent and read-only**; no dry-run needed because it never writes.

## Safety Boundaries
- **Read-only.** The validator never edits the artifacts it judges — corrections belong to the
  Analyst/Planner correction loop, so a gate can never "fix" itself green.
- **No network, no writes**; the test suite writes only inside `tempfile`.
- **Matchers are widened toward the corpus, never the corpus narrowed toward the matchers.** A gate
  that cannot pass on the artifacts it governs is not a gate (TASK 090 found it in exactly that
  state); the corpus tests below exist to make that failure loud.

## Validation Evidence
- **Local verification:** `bash scripts/tests/run_tests.sh` — 57 tests, stdlib `unittest`, with a
  **zero-test-discovery guard** (a run that executes nothing is a FAILURE, not a green gate) and a
  guard that the corpus tests actually RAN rather than skipped inside this repo.
- **Coverage:** the 8 RTM heading shapes `docs/tasks/` actually ships (fixtures copied verbatim) +
  negative shapes; table checks; bypass semantics; PLAN ID coverage via step headings and checklist
  bullets; the `R1`-vs-`R10` whole-token boundary and hyphenated ids; the table parser and RTM
  section slicing; multi-table RTM sections (`tests/test_multitable.py`); CLI errors.
- **Multi-table RTM sections** (`tests/test_multitable.py`, RF-6): the first table fixes the RTM's
  shape; later tables with an **identical header row** are the same RTM continued and are read;
  a table with different columns is skipped and named. The rule was chosen **by measurement, not by
  preference** — "read every table" invents ids like `Bold density` out of `task-096`'s
  `### N.N Details by ID` subsection, and "refuse on more than one table" fails three shipped tasks;
  each is a gate broken on the artifacts it governs. Scanning skips a foreign table rather than
  stopping at it, so an interleaved subsection cannot truncate the RTM.
- **Anti-drift, corpus-anchored** (`tests/test_corpus.py`): a probe keyed on the `trace*`/`rtm` stems
  — deliberately **wider** than the matcher's required phrase, so a new corpus shape like
  `## Traceability Matrix` fails the test instead of slipping through — finds the RTM-ish headings
  under `docs/tasks/` and asserts `RTM_HEADER` matches every one that is not a declared non-RTM
  mention (`KNOWN_NON_RTM_SHAPES`, currently one prose heading in `task-050`, itself checked for
  staleness). Plus a regression pin on the 8 shapes that must never stop matching, and liveness
  floors (≥15 tasks pass `--mode task`, ≥10 exact-slug plan/task pairs pass `--mode plan`).
  **Measured 2026-07-30 (recount after archiving TASK 092's own artifacts): 46 probed headings,
  8 normalized shapes, 20 tasks and 14 of 27 pairs passing** — the floors are canaries below those
  numbers, not targets. Outside the framework repo these tests **skip** rather than fail.
- **Differential compatibility check** (`scripts/tools/compat_diff.py`): runs the PRE-change
  validator and the current one over every `docs/tasks/*.md` in every sibling project and reports
  how many artifacts **changed verdict**. This answers a question the corpus floors cannot: those
  are liveness canaries ("the gate is not dead"), set below the measured counts so ordinary churn
  never turns them red, and a floor cannot see one file flip while another flips back.
  **Measured for the anchor change (TASK 095), old = `14799d3`: `0 of 1102 artifacts changed
  verdict across 10 projects`.** Every number in that line is counted by the script; the first
  time this was reported the denominator had been typed by hand into the output string and was
  wrong by 3 (`developer-guidelines` §6.3 rule 4 now names that defect).
  **Measured for the multi-table change (RF-6), old = `fddf209`: `0 of 1127 artifacts changed
  verdict across 10 projects`** — and, on the question the verdict cannot answer, **24 of 1127
  changed their requirement COUNT, every one of them upward**, across 5 projects (e.g.
  `onchain-analytics/task-012` 3 → 26, `n8n-lazy-loading-skills/task-003` 12 → 24). Those 24 are
  not a regression, they are the defect's extent: each is an epic-split RTM of which the gate had
  been reading the first epic and reporting `Success`. Each was checked to be a real requirements
  table rather than a foreign one. `compat_diff.py` compares **verdicts** and would have called
  this change clean while it silently altered a quarter-hundred counts — so a count sweep belongs
  beside it whenever what changes is how much of a document is read, not whether it passes.
- **Proof the guard bites:** re-injecting each historical regression makes the suite red —
  the pre-TASK-090 `^## Requirements Traceability$` matcher → 28 failures (incl. every corpus test);
  the literal `[**R-1**]` PLAN token → 7 failures. Re-verify with those two edits, not by reading.
