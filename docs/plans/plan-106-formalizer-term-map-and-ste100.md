# PLAN 106 — artifact-formalizer: a test-to-rule map, one name per check, and ASD-STE100 on record

**TASK:** [docs/TASK.md](../tasks/task-106-formalizer-term-map-and-ste100.md) · **Covers:** R1–R8 · **Acceptance:** A1–A9

## Sequencing rule

Seven clusters in order. Cluster A backs up. Cluster B rewrites the pin and leaves it **failing** on
the base tree, which states 59 in two sites. That is Stub-First for a task whose product is text:
the test is the executable form of R1. Cluster C corrects the counts and is the first point where
the pin passes. Clusters D and E edit the contract and the baseline. Cluster F writes the release,
and Cluster G runs every gate.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | Backup | `.agent/archive/` | rollback |
| B | The pin, failing | `evals/selftest_evals.py`, `evals/README.md` | R2 |
| C | The counts | `SKILL.md`, `System/Docs/SKILLS.md` | R1 |
| D | Map, label, pointer | `references/authoring-contract.md`, `SKILL.md` | R3, R4, R5 |
| E | ASD-STE100 record | `references/measurement-baseline.md` | R6 |
| F | Release | `SKILL.md`, `CHANGELOG.md`, `CHANGELOG.ru.md` | R7 |
| G | Gates | `docs/reviews/framework-audit-106.md` | R8, A1–A9 |

Paths under `evals/`, `references/` and the bare `SKILL.md` are relative to
`.agent/skills/artifact-formalizer/`.

**Declared file set (A7).** Nine edited files: the eight in the table above that sit outside
`docs/`, plus `docs/reviews/framework-audit-106.md`. Also present in the diff: `docs/TASK.md`,
`docs/PLAN.md`, and the TASK 105 pair archived to `docs/tasks/` and `docs/plans/`. Cluster G may add
`REFERENT_MOVED` repairs from the resolver's `--fix`. Each repair is listed in the audit.

**Architecture.** `docs/ARCHITECTURE.md:319` `the six per-sentence tests and the licensed statement
forms` stays true. No architecture edit.

**Rollback.** Every edited path is tracked, and no cluster creates or deletes a skill file.
Reverting is `git checkout --` on the nine edited paths, or a copy back from `.agent/archive/`.
The TASK 105 archive move reverts with `git mv` back to `docs/TASK.md` and `docs/PLAN.md`.

## Cluster A — backup

- [x] A1. `mkdir -p .agent/archive`.
- [x] A2. Copy the bootstrap files present: `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ]
      && cp "$f" ".agent/archive/$f.bak"; done`. None is edited; the copies serve the fallback.
- [x] A3. Copy each of the eight non-`docs/` files to `.agent/archive/<basename>.bak`.
      `SKILL.md` and `System/Docs/SKILLS.md` share no basename, so no copy overwrites another.

## Cluster B — the pin, failing (R2)

- [x] B1. Rewrite `t_count_pin()` in `evals/selftest_evals.py`. Keep one `check()` call per run,
      named `TC-EV-13b`.
      1. Sites: `evals/README.md`, `SKILL.md`, `System/Docs/SKILLS.md`.
      2. Pattern: every `<n> case(s)` in the span from a `selftest_evals.py` mention to the next
         full stop. Final form after review: TASK D7.
      3. A missing `System/Docs/SKILLS.md` is skipped only where `System/Docs/` is absent.
      4. Fails when a present site states no count, or any count differs from `EXPECTED_CASES`.
      5. The detail names each site with the counts it found.
- [x] B2. Update the `EXPECTED_CASES` comment: the same number is read from three files.
- [x] B3. `evals/README.md`, the sentence on `TC-EV-13b`: it reads the number from this file,
      `SKILL.md` and `System/Docs/SKILLS.md`.
- [x] B4. Run `python3 evals/selftest_evals.py`. Expected: 77 of 78, exit 1. `TC-EV-13b` names
      `SKILL.md` [59] and `SKILLS.md` [59].

**Why the full stop bounds the pattern.** `SKILLS.md` states `192-case battery` and the eval count
in one list item. The `192-case` claim precedes the `selftest_evals.py` mention, so the anchored
pattern cannot reach it. Every eval count in the three sites follows its mention within one
sentence.

## Cluster C — the counts (R1)

- [x] C1. `SKILL.md` §8 "Behavioural evals": `59 cases` → `78 cases`.
- [x] C2. `System/Docs/SKILLS.md` "Mode C" item: `runs 59 cases` → `runs 78 cases`.
- [x] C3. Run `python3 evals/selftest_evals.py`. Expected: 78 of 78, exit 0.
- [x] C4. Execute the A5 mutations from TASK §4, one at a time. Each one: apply, run, record
      the `TC-EV-13b` detail, revert with the `.bak` or `git checkout --`, re-run green.

## Cluster D — map, label, pointer (R3, R4, R5)

- [x] D1. `references/authoring-contract.md`, the six-test table: add a `§5.5 rule` column after
      `Test`. Values for T1–T6: 2, 4, 6, 3, 5, 1.
- [x] D2. Same file, directly under the table: one paragraph. A finding names its §5.5 rule; the
      column maps it to the test. `cell_width` and `cell_sentences` carry §5.1 and have no row.
- [x] D3. Same table, T4 row: `**One claim**` → `**Reasoning separated**`.
- [x] D4. `SKILL.md` §6 rule 1: add one sentence naming the column D1 adds.
- [x] D5. Run `grep -rn "One claim" .agent/skills`. Expected: three lines, all rule 1 —
      `SKILL.md`, `references/formalization-guide.md`, `documentation-standards/SKILL.md`.
      Cluster E adds a fourth: the §4.2 record of the rename, which is history and not a label.
- [x] D6. Run `scan_register.py` over `SKILL.md` and `references/*.md`. Expected: 0 `warn`.

## Cluster E — the ASD-STE100 record (R6)

- [x] E1. Re-run the measurement over `docs/tasks/` with the scanner's `mask()`, `prose_blocks()`
      and `sentences()`. Record the figures and the base revision.
- [x] E2. Write `### 4.2` in `references/measurement-baseline.md`, after §4.1 and before `## 5.`.
      Content per TASK §2.1 R6, items 1–5.
- [x] E3. Table cells stay one clause under 120 characters; reasons go below the table.
- [x] E4. The text states no `<n> cases`, and no verdict cell begins with `adopted`.
- [x] E5. Run `python3 scripts/selftest_scan.py`. Expected: 192 of 192 — `TC-SHIP-06`, `TC-SHIP-08`,
      `TC-SHIP-10` and `TC-SHIP-11` read this file.

## Cluster F — release (R7)

- [x] F1. `SKILL.md` frontmatter: `version: 2.1` → `version: 2.2`.
- [x] F2. `CHANGELOG.md`: a `v3.31.2` entry above `v3.31.1`, sections Fixed and Changed.
- [x] F3. `CHANGELOG.ru.md`: the same entry in Russian, at the same position.
- [x] F4. Run `scan_register.py` over both changelogs, compared against their `.bak`. Expected: no
      new `warn` in the new entry.

## Cluster G — gates (R8, A1–A9)

- [x] G1. `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py` → 192 of 192 (A1).
- [x] G2. `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py` → 78 of 78 (A2).
- [x] G3. `scan_register.py --probe` → 18 of 18 live (A3).
- [x] G4. `scan_register.py` over `SKILL.md`, `references/*.md`, `docs/TASK.md` → 0 `warn` (A4).
- [x] G5. `grep -rn "One claim" .agent/skills` → the three rule-1 lines and the §4.2 record (A6).
- [x] G6. `git status --short` and `git diff --stat` → only the declared file set (A7).
- [x] G7. `check_positional_refs.py --targets-changed --fix` → every repair listed in the audit
      (A8).
- [x] G8. `validate_skills.py --root . --quiet`, `PYTHONPATH=. python3 tests/run_tests.py`,
      `python3 -m pytest tests/ -q` → all pass (A9).
- [x] G9. CI parity: `check_prompt_references.py --root .`, `security_lint.py --root .`,
      `.agent/skills/skill-parallel-orchestration/scripts/generate_wrappers.py --check`.
- [x] G10. Fill the audit's execution-evidence table with each command's printed result.
- [x] G11. Review per the Self-Improvement Mode rule: `code-reviewer` and `security-auditor` over
      the diff, in parallel.

## Review fix loop

Run after G11 returned, with the tree no longer frozen. TASK D7 lists what was fixed and D8 what
was deferred.

- [x] R1. `TC-EV-13b`: span-wide counts, `(?:\s+|-)` between numeral and `cases`, no `1,078` alias,
      registry required where `System/Docs/` exists. Eight mutations re-executed (TASK A5).
- [x] R2. `measurement-baseline.md` §4.2: re-measured with `detect_lang()`; reopen bar rewritten as
      a defect rate; source link pinned to `7d4a135`; sub-headings 4.2.1 and 4.2.2.
- [x] R3. Contract paragraph and CHANGELOG entries corrected; both changelogs re-scanned.
- [x] R4. Every gate in Cluster G re-run; the audit records the final figures.
