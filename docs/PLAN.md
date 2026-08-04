# Development Plan: TASK 097 — Register scanner masking

**Target:** `docs/TASK.md` (TASK 097), 16 requirements, audit `docs/reviews/framework-audit-097.md`.
**Mode:** Framework Upgrade (Self-Improvement). Stub-First per `tdd-stub-first`.
**Primary file:** `.agent/skills/artifact-formalizer/scripts/scan_register.py`.

## 0. Safety

**0.1 Backup** (before the first edit in Stage 2):

```sh
mkdir -p .agent/archive
for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done
for f in .agent/skills/artifact-formalizer/scripts/scan_register.py \
         .agent/skills/artifact-formalizer/scripts/selftest_scan.py \
         .agent/skills/artifact-formalizer/SKILL.md \
         .agent/skills/artifact-formalizer/references/measurement-baseline.md \
         .agent/skills/skill-planning-format/assets/templates/task_md_template.md \
         .agent/skills/skill-planning-format/assets/templates/plan_md_template.md; do
  cp "$f" ".agent/archive/$(basename $f).bak"
done
```

`.agent/archive/` is gitignored, so the backups leave `git status` clean.

**0.2 Rollback.** Restore any file from `.agent/archive/<basename>.bak`. The tracked copy is also
in git history at `992b3ef`, so `git checkout 992b3ef -- <path>` is the second route.

**0.3 Baseline capture** (Stage 1, before any edit). Recorded so every later claim is a delta:

```sh
python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py          # expect 128/128
python3 .agent/skills/artifact-formalizer/scripts/scan_register.py --probe  # expect 18/18
python3 .agent/skills/artifact-formalizer/scripts/scan_register.py \
  docs/TASK.md docs/PLAN.md docs/ARCHITECTURE.md --sections --terms docs/ARCHITECTURE.md
```

**0.4 Stop condition.** A stage whose verification fails is not carried forward. Restore from 0.1
and report.

<!-- contract:sequence -->

## Task Execution Sequence

### Stage 1: Baseline and corpus harness (Red)

1. Run 0.3 and record the three outputs under `docs/reviews/`.
2. Add `corpus_sweep()` to `selftest_scan.py`: for every `*.md` in the repository, report masked
   letter fraction, surviving backtick parity, and exit code.
3. Assert the current numbers: 14 odd-parity documents, 598 documents scanned.

**Verification.** The sweep reproduces E4 and E8 from TASK 097 §1.1.
**Stub-First note.** The harness measures before any behaviour changes, so Stage 3 has a baseline
to be a delta against.

### Stage 2: Tokenizer stub and its failing pins (Red)

1. Add `_scan_constructs(text)` to `scan_register.py`, returning a list of `(start, end)` spans.
   Stub body raises `NotImplementedError`, with the docstring stating the invariant.
2. Add fixtures F1–F6 to `selftest_scan.py`, one per test obligation T1–T6.
3. Run the selftest. F1–F6 fail; the 128 existing cases pass.

**Verification.** Selftest reports 128 passed, 6 failed. A pin that passes here is asserting
nothing and is rewritten before Stage 3.

### Stage 3: Tokenizer and paragraph bound (Green)

1. Implement `_scan_constructs` as one left-to-right pass. At each position try fence, HTML
   comment, link target, code span, in that order; consume the match whole; advance past it.
2. Bound the code span at a blank line, per CommonMark.
3. Rewrite `mask()` to blank the spans `_scan_constructs` returns. Keep the frontmatter step ahead
   of it, unchanged.
4. Run the selftest.

**Verification.** 128 existing cases plus F1–F6 pass. `--probe` reports 18/18.
**Rollback trigger.** Any of the 128 failing means the tokenizer masks differently from the
sequential loop on a case the corpus already covers. Restore and re-derive.

### Stage 4: Named input defects (Green)

1. Return input defects from `_scan_constructs`: an unterminated HTML comment, and a backtick left
   unpaired after the pass.
2. Print them above `DIAGNOSTICS`, each with its line number.
3. Add the masked-letter fraction to `DIAGNOSTICS`.
4. Hold exit 0 for every input defect. Exit 2 stays bound to `--probe`.

**Verification.** F5 and F6 pass. T7 asserts exit 0 on F1–F6 and exit 2 on a killed detector.

### Stage 4b: Exit-code contract (D2)

1. Route an unreadable path and an unreadable stdin to exit 3, and name the path in the output.
   Leave rule-file and term-file failures at 2: those are the instrument.
2. Add `--allow-missing`. A named absent file is reported and skipped; the run exits 0 when at
   least one file was scanned.
3. Add `--allow-missing` to the CI advisory step for `docs/TASK.md` and `docs/PLAN.md` only.

**Verification.** T15, T16, T17.
**Why the flag rather than tolerating absence by default.** A typo'd path would otherwise pass CI
while nothing was scanned. The flag names the one state the framework legitimately produces.

### Stage 4c: Rule-3 probe covers its vocabulary (D3)

1. Replace the single declared probe with one synthesised probe per modal and per causal.
2. Report the count exercised, not the count declared.
3. Add a mutation pin: each rule-3 pattern replaced in turn by a non-matching one → exit 2.

**Verification.** T18, T19. The mutation pin is what makes this stage falsifiable.

### Stage 5: Case-B template repair

1. Rewrite the Case-B comment in both templates so no comment body contains `-->`.
2. Assert with `markdown-it` that no comment text renders as page text.
3. Assert `git diff` is empty over the 20 Case-A files.

**Verification.** T11 and T11a. Templates keep their meaning; only the citation form changes.

### Stage 6: Documentation and acceptance

1. `SKILL.md` §2: name which `DIAGNOSTICS` value invalidates a scan.
2. `references/measurement-baseline.md`: record E1–E8.
3. `System/Docs/SKILLS.md`, `CHANGELOG.md`, `CHANGELOG.ru.md`: state the new behaviour.
4. Run the full gate set of `.github/workflows/framework-gates.yml`.
5. Re-run the corpus sweep and record the delta against Stage 1.

**Verification.** T8–T14. `git status` clean.

<!-- contract:coverage -->

## Use Case Coverage

| Use Case | Stages | Verified by |
| :--- | :--- | :--- |
| UC-1 — author scans a document citing a marker | 2, 3 | T1, T2, T3, T4 |
| UC-2 — malformed document reaches the scanner | 2, 4 | T5, T6, T7 |
| UC-3 — operator judges whether a scan is a measurement | 4, 6 | T8, T9 |

## Requirements Coverage (RTM)

| Requirement | Stage | Verified by |
| :--- | :--- | :--- |
| R1 classification never inverts | 3 | T1, T2 |
| R2 no construct begins inside another | 3 | T3 |
| R3 code span does not cross a blank line | 3 | T4 |
| R4 valid Markdown raises no diagnostic | 3 | T1 |
| R5 unterminated comment is named | 4 | T5 |
| R6 unpaired backtick is named | 4 | T6 |
| R7 exit 2 reserved for a dead detector | 4 | T7 |
| R8 `DIAGNOSTICS` carries the masked fraction | 4 | T8 |
| R9 `SKILL.md` §2 names the invalidating value | 6 | T8 |
| R10 128 existing cases pass | 3 | T9 |
| R11 `--probe` reports 18/18 | 3 | T10 |
| R12 templates render no comment body | 5 | T11 |
| R12a Case-A files stay unedited | 5 | T11a |
| R13 baseline records the defect | 6 | T12 |
| R14 no exit 2 across the corpus | 6 | T13 |
| R15 changelogs and `System/Docs` updated | 6 | T14 |
| R16 unreadable path exits 3 | 4b | T15 |
| R17 `--allow-missing` exits 0 | 4b | T16 |
| R18 CI advisory passes in the archived state | 4b | T17 |
| R19 probe exercises every rule-3 pattern | 4c | T18 |
| R20 probe detail states what it exercised | 4c | T19 |

## Ordering constraints

| Before | After | Reason |
| :--- | :--- | :--- |
| Stage 1 | Stage 3 | A delta needs a baseline captured first |
| Stage 2 | Stage 3 | A pin written after the fix cannot be seen to fail |
| Stage 3 | Stage 4 | Input defects are a product of the tokenizer pass |
| Stage 3 | Stage 5 | Template repair must not be what makes Stage 3 pass |
| Stage 5 | Stage 6 | The corpus delta is recorded once the corpus is final |

**Stage 5 is deliberately after Stage 3.** Repairing the templates first would remove the Case-B
trigger, and Stage 3 would then pass without proving anything about Case A.

## Verification per stage

| Stage | Command | Pass condition |
| :--- | :--- | :--- |
| 1 | `selftest_scan.py`, `--probe`, corpus sweep | 128/128, 18/18, 14 odd-parity |
| 2 | `selftest_scan.py` | 128 pass, F1–F6 fail |
| 3 | `selftest_scan.py`, `--probe` | 134 pass, 18/18 |
| 4 | `selftest_scan.py` | 134 pass, exit codes per T7 |
| 4b | scan with a missing path, with and without the flag | exit 3, then exit 0 |
| 4c | each rule-3 pattern mutated in turn | `--probe` exits 2 every time |
| 5 | `markdown-it` render, `git diff` | no comment text rendered, Case-A diff empty |
| 6 | full `framework-gates.yml` set | every job exits 0, `git status` clean |
