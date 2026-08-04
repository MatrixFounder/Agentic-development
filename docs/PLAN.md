# Development Plan: TASK 096 — Artifact register formalization

**Target:** `docs/TASK.md` (TASK 096), 12 requirements, audit `docs/reviews/framework-audit-096.md`.
**Mode:** Framework Upgrade (Self-Improvement). Stub-First per `tdd-stub-first`.

## 0. Safety

**0.1 Backup** (before the first edit in Stage 2):

```sh
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
cp .agent/skills/documentation-standards/SKILL.md .agent/archive/documentation-standards.SKILL.md.bak
cp System/Agents/02_analyst_prompt.md .agent/archive/02_analyst_prompt.md.bak
cp System/Agents/06_planner_prompt.md .agent/archive/06_planner_prompt.md.bak
cp .agent/skills/skill-planning-format/assets/templates/task_md_template.md .agent/archive/task_md_template.md.bak
cp .agent/skills/skill-planning-format/assets/templates/plan_md_template.md .agent/archive/plan_md_template.md.bak
cp .agent/skills/requirements-analysis/assets/task_template.md .agent/archive/task_template.md.bak
```

**0.2 Rollback.** Restore any edited file from `.agent/archive/<file>.bak`. The new skill directory
is removed with `rm -rf .agent/skills/artifact-formalizer`. No existing file is deleted by this
plan, so rollback is restore-and-remove only.

**0.3 Regression baseline** (recorded before Stage 1, re-run at Stage 6):

```sh
bash .agent/skills/skill-spec-validator/scripts/tests/run_tests.sh   # expect 47 tests OK
python3 -m pytest tests/ -q                                          # expect 370 passed
wc -l .agent/skills/documentation-standards/SKILL.md                 # expect 361
```

**0.4 Gate discipline.** Every verification command below is run at repository root with the same
invocation CI uses. A narrower invocation does not count as a green verdict
(`developer-guidelines` §6.3).

<!-- contract:sequence -->

## Task Execution Sequence

### Stage 1: Decisions and doctrine

- **Task 096.1** — Close Q1 and write the normative short form
  - Requirements: R1, R2, R3, R5, A10, A11
  - Description File: `docs/tasks/task-096-01-thresholds-and-doctrine.md`
  - Priority: Critical
  - Dependencies: none
  - **Blocks every later stage.** Q1 (sentence-length bound) is closed here, with the number and
    its justification recorded. A scanner written before this produces a hard-coded guess.

### Stage 2: Skill scaffold and stubs (Red)

- **Task 096.2** — Scaffold `artifact-formalizer`, define the schema, stub the scanner
  - Requirements: R6, R7, R10
  - Description File: `docs/tasks/task-096-02-skill-scaffold-stubs.md`
  - Priority: Critical
  - Dependencies: Task 096.1
  - **Scaffold command (mandatory, not by hand):**
    `python3 .agent/skills/skill-creator/scripts/init_skill.py artifact-formalizer --tier 2`
  - Stub-First: `scan_register.py` exposes its full CLI and returns hardcoded empty findings.
    `selftest_scan.py` carries the complete case battery and is **expected to fail**. A selftest
    that passes against stubs is a defective selftest, not a finished step.
  - **Red state must name its reason.** `python3 -c "import scan_register"` succeeds, and the
    selftest output lists the failing case names. A failure from a syntax or import error is not a
    Red state; it is a broken file.

### Stage 3: Scanner logic (Green)

- **Task 096.3** — Masking pass and structural checks
  - Requirements: R12, R4, R8
  - Description File: `docs/tasks/task-096-03-masking-and-structural.md`
  - Priority: Critical
  - Dependencies: Task 096.2

- **Task 096.4** — Lexical rules, per-language data, language resolution
  - Requirements: R4, R7, R8
  - Description File: `docs/tasks/task-096-04-lexical-and-languages.md`
  - Priority: High
  - Dependencies: Task 096.3

### Stage 4: Guide

- **Task 096.5** — Formalization guide, worked example, rejected-candidates table
  - Requirements: R2, R6
  - Description File: `docs/tasks/task-096-05-guide-and-rejected.md`
  - Priority: High
  - Dependencies: Task 096.1, Task 096.4

### Stage 5: Authoring surfaces

- **Task 096.6** — Prompts and templates carry the short form
  - Requirements: R9, A7
  - Description File: `docs/tasks/task-096-06-authoring-surfaces.md`
  - Priority: Critical
  - Dependencies: Task 096.1

### Stage 6: Documentation and verification

- **Task 096.7** — `System/Docs/`, CHANGELOG, full acceptance run
  - Requirements: R11, A1–A11
  - Description File: `docs/tasks/task-096-07-docs-and-acceptance.md`
  - Priority: Critical
  - Dependencies: all above
  - Includes the skill-validation gate and a re-read of `docs/ARCHITECTURE.md` §7.3 against what
    actually shipped: the threshold, the file locations, and the skill name.

<!-- contract:coverage -->

## Use Case Coverage

| Use Case | Covered by |
| :--- | :--- |
| UC-1 Analyst drafts a TASK | Task 096.6 |
| UC-2 Author checks a finished artifact | Task 096.3, Task 096.4 |
| UC-2 Alt A — language with no rule file | Task 096.4 |
| UC-2 Alt B — malformed rule file | Task 096.2, Task 096.4 |
| UC-3 Author formalizes a drifted artifact | Task 096.5 |
| UC-4 Team adds a rule | Task 096.4 (fixture-data selftest case) |

## Requirements Coverage (RTM)

| Req | Tasks |
| :--- | :--- |
| R1 measurement-derived rules | 096.1 |
| R2 refuted candidates recorded | 096.1, 096.5 |
| R3 no language mandate | 096.1, verified 096.7 |
| R4 applies to any language | 096.3, 096.4 |
| R5 normative form in `documentation-standards` | 096.1 |
| R6 TIER 2 skill carries guide, example, scanner | 096.2, 096.5 |
| R7 rules are data | 096.2, 096.4 |
| R8 advisory, exit 0 | 096.3, 096.4 |
| R9 authoring surfaces | 096.6 |
| R10 acceptance battery | 096.2, 096.4 |
| R11 System/Docs | 096.7 |
| R12 masking | 096.3 |

## Ordering constraints

1. **096.1 before everything.** It fixes the thresholds. A later step that needs a different
   threshold changes the data file and records why — it does not change the number to make a scan
   pass (TASK A8).
2. **096.2 before 096.3.** The selftest battery is written against the stub and observed failing.
   A battery written after the logic proves the battery, not the logic.
3. **096.3 before 096.4.** Masking is what makes lexical matching honest. Six of the six evaluative
   hits in `docs/TASK.md` sit inside backticks (TASK §1.1 R12); lexical rules landing first would
   be measured against a known-wrong baseline.
4. **096.6 independent of 096.2–096.5.** The authoring surfaces need the rules from 096.1, not the
   scanner. It may run in parallel with Stage 2–4.
5. **096.7 last.** It runs the acceptance criteria, and A8 scans this PLAN and the TASK.

## Verification per stage

| Stage | Command | Expected |
| :--- | :--- | :--- |
| 1 | `wc -l .agent/skills/documentation-standards/SKILL.md` | ≤ 401 (baseline 361 + 40, A10) |
| 2 | `init_skill.py artifact-formalizer --tier 2`; then `python3 -c "import scan_register"` | Skill dir scaffolded by the tool; module imports |
| 2 | `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py` | **Fails**, listing failing case names (not an import error) |
| 3 | same | Structural and masking cases pass; lexical still fail |
| 4 | same | All cases pass |
| 5 | Read each of the 4 authoring surfaces against the §5.5 rule list | Every rule reachable from the surface (A7); grep is secondary, never the proof |
| 6 | `python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/artifact-formalizer` | Passes the skill-structure gate |
| 6 | `bash .agent/skills/skill-spec-validator/scripts/tests/run_tests.sh`; `python3 -m pytest tests/ -q` | 47 OK; 370 passed (A9) |
| 6 | `scan_register.py docs/TASK.md docs/PLAN.md` | exit 0, zero `warn` (A8) |
| 6 | Read `docs/ARCHITECTURE.md` §7.3 against the shipped skill | Threshold, paths and skill name all match reality |
