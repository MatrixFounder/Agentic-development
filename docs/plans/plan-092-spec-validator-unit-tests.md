# Development Plan — TASK 092: unit tests for `skill-spec-validator`

**Scope:** a stdlib test suite for `.agent/skills/skill-spec-validator/scripts/validate.py` +
the four Execution-Policy sections its SKILL.md is missing. **No behavior change to `validate.py`.**

**Rollback:** clean tree at start apart from TASK 091's uncommitted work; every step is additive
(new `scripts/tests/` files) except the SKILL.md sections. `git checkout -- <path>` per step.

---

## Step 1 (R1, R2, R7) — matcher + parser unit tests (`tests/test_validate.py`)

- [ ] **R1** one test per shipped heading shape, fixtures copied verbatim from `docs/tasks/`:
      `## Requirements Traceability Matrix (RTM)`, `## 2. …`, `### 2. …`, `### 3. …`,
      `### 2. Requirements (RTM)`, `## Requirements Traceability`,
      `## 6. Acceptance Criteria (Requirements Traceability Matrix)`, `## 5. Acceptance Criteria (RTM)`.
- [ ] **R2** negative shapes: `# …` (h1), `##### …` (h5), `## 2. Use Cases` (names neither form),
      and a prose line "the Requirements Traceability Matrix lives below" outside a heading.
- [ ] **R7** `parse_markdown_table`: separator row skipped · escaped `\|` kept inside a cell ·
      row with the wrong column count skipped · table terminated by the first non-pipe line ·
      a second table under a LATER `## Section` does not leak into the RTM block (slicing test).

**Verify:** `python3 -m unittest discover -s tests` from the skill's `scripts/` dir — new tests green.

## Step 2 (R3, R4, R8) — `--mode task` behavior tests

- [ ] **R3** missing table → exit 1 + "table is empty or invalid"; wrong columns → exit 1 +
      "must contain columns"; valid table → exit 0 + "Found N requirements".
- [ ] **R4** bypass token → exit 0 + "bypassed" in both modes, on content that would otherwise
      fail, **and** when the token appears only inside prose (pins the bare-substring semantics
      that silently disabled this task's own first-draft spec).
- [ ] **R8** absent TASK path → exit 1; absent PLAN path → exit 1; `--mode plan` with a single
      file → argparse/usage failure.

**Verify:** same discover run; assertions cover exit code AND message, so a message reworded
without thought fails loudly.

## Step 3 (R5, R6) — `--mode plan` coverage tests

- [ ] **R5** id referenced only in `## Step 2 — thing (R2)` → pass; id referenced only in
      `- [ ] R1 do the thing` → pass; uncovered id → exit 1 naming exactly the missing ids.
- [ ] **R6** `R10` present but `R1` absent → `R1` reported missing (the WI-1 case);
      hyphenated ids `R-065-1` / `TF-X-7` matched whole; `**R1**`, `` `R1` ``, `[R1]` in the RTM
      cell normalize to `R1`; an id row with an empty `ID` cell is skipped, not crashed on.

**Verify:** same discover run.

## Step 4 (R9, R10, R11) — corpus anti-drift tests (`tests/test_corpus.py`)

- [ ] **R9** loose independent probe (`^#{2,4} … (requirements traceability|\(rtm\))`, case-insensitive)
      over `docs/tasks/*.md`; assert `RTM_HEADER` matches **every** probed heading, and assert the
      probe found ≥6 distinct shapes — zero discovery is a failure, not a green run.
- [ ] **R10** liveness floors as named constants with a comment stating they are canaries below
      today's measurements (20 tasks / 13 pairs): `MIN_TASKS_PASSING = 15`,
      `MIN_PLAN_PAIRS_PASSING = 10`. Pairing is exact-slug (`plan-X.md` ↔ `task-X.md`) so
      sub-task files are never mispaired.
- [ ] **R11** the corpus tests skip cleanly (not fail) when run outside the framework repo, so the
      suite stays portable once the skill is installed elsewhere; a zero-test discovery run fails.

**Verify:** run the suite; then temporarily tighten `RTM_HEADER` to the old
`^## Requirements Traceability$` literal and confirm R9/R10 tests go red — the drift the WI
describes must be mechanically detectable. Restore.

## Step 5 (R12) — SKILL.md v1.0 → 1.1

- [ ] Add `## Execution Mode` (script-first), `## Script Contract` (command, exit codes 0/1,
      bypass semantics, idempotent read-only), `## Safety Boundaries` (read-only; never edits the
      artifacts it judges; bypass is an escape hatch that must be justified), and
      `## Validation Evidence` (the test command + the corpus counts measured in TASK 092).

**Verify:** `python3 System/scripts/validate_skills.py` — skill warning-free, 45/45 overall.

## Step 6 — close the ledger entry + release notes

- [ ] Flip `docs/backlog/wi-1-skill-spec-validator-unit-tests.md` to `status: done` +
      `resolved_at` / `resolved_by: TASK 092`, add the resolution blockquote (what is covered, what
      was deliberately NOT changed), and move its index line to a `## Closed` group in
      `docs/BACKLOG.md` — the first close under the two-level contract from TASK 091.
- [ ] CHANGELOG (EN + RU) entry with real gate numbers.
- [ ] Session-state update; archive TASK/PLAN in lockstep at completion.

**Verify:** `git diff` shows the ledger edited in lockstep; full gate sweep green
(unittest ×2 suites, E2E, contract-sync, validate_skills, prompt-refs, security-lint).
