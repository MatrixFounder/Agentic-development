# PLAN 101 — artifact-formalizer: behavioural evals for Mode A and the §5 recall gaps

**TASK:** [docs/TASK.md](../tasks/task-101-formalizer-behavioural-evals-mode-a-and-recall-gaps.md) · **Covers:** R1–R7 · **Acceptance:** A1–A9

## Sequencing rule

Seven clusters in order. Cluster A creates every file as a stub and leaves the selftest red.
Clusters B to D turn one stub each into an implementation. Cluster E makes the selftest green.
Cluster F spends tokens; every cluster before it spends none. Cluster G writes what F measured.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | Scaffold and stubs | `evals/` tree | R7 |
| B | Grader | `evals/grade_run.py` | R2, R6 |
| C | Fixtures and answer keys | `evals/fixtures/` | R3 |
| D | Executor | `evals/run_authoring.py` | R1 |
| E | Instrument selftest | `evals/selftest_evals.py` | R4, A1–A8 |
| F | Campaign | `evals/corpus/`, `evals/report.json` | R5, A9 |
| G | Documents and CI | `README.md`, `SKILL.md`, baseline, workflow | R5, R6 |

**Rollback.** The working tree is clean at HEAD `7708e2f`. Cluster A onward adds one new directory,
`.agent/skills/artifact-formalizer/evals/`. Reverting is `rm -rf` on that directory plus
`git checkout --` on the four tracked files clusters G touches. No cluster deletes or moves an
existing file.

## Cluster A — scaffold and stubs

- [x] A1. Create `.agent/skills/artifact-formalizer/evals/` with `fixtures/`, `corpus/`, `prompts/`.
- [x] A2. Write `evals/evals.json`: 6 Axis A cases, 4 Axis B cases, schema `formalizer-evals/v1`.
      Each Axis A case declares `id`, `axis`, `lang`, `artifact_kind`, `prompt_file`. Each Axis B
      case declares `id`, `axis`, `fixture`, `key`.
- [x] A3. Write the six Axis A prompt files under `evals/prompts/`. A prompt states the artifact to
      write and its subject. It names no register rule and no marker.
- [x] A4. Create `evals/grade_run.py`, `evals/run_authoring.py`, `evals/selftest_evals.py` as
      importable stubs. Each function carries its signature and returns a declared empty value.
- [x] A5. Verify the stubs import and the selftest exits non-zero:
      `python3 evals/selftest_evals.py; echo $?` reports a non-zero code.

**Why the prompt names no rule.** A prompt naming a rule teaches both arms the contract, and the
arms would then differ in nothing.

## Cluster B — grader

- [x] B1. `grade_run.py` imports `scan_register` from the sibling `scripts/` directory and calls its
      scan entry point on a path. It reads `warn`, `diagnostics` and `counts` from the result.
- [x] B2. Implement `score_document(path) -> dict` returning the five values of TASK R2, each keyed
      by the name TASK R2 states.
- [x] B3. Implement `score_axis_b(reported, key) -> dict` returning `recall`, `precision`,
      `matched`, `missed`, `spurious`. A reported line matches a planted defect when it falls in
      that defect's declared line set and names its rule.
- [x] B4. Implement `grade(evals, run_dir) -> dict` writing `grading.json`. A case whose
      `prose_share_of_nonblank` falls below `PROSE_FLOOR` is recorded with `measured: false` and a
      stated reason.
- [x] B5. Declare `PROSE_FLOOR = 25`, with the derivation in a comment. `measurement-baseline.md`
      §10.1 E5 measured `task_md_template.md` at 27% prose reaching rule 1 under the masking defect,
      and at 50% after the fix. A floor of 25 therefore sits under both figures. It reports only a
      document measured less than the worst case that defect produced.
- [x] B6. The summary printer names cases run, repetitions, empty outputs and unmeasured cases.

**Why the grader never declares a threshold of the scanner's.** L4 and TASK R2. A copied threshold
drifts from `data/register-*.json` and grades against the previous value.

## Cluster C — fixtures and answer keys

- [x] C1. Write `fixtures/recall-gap-rule3.md`: a specification-shaped document whose obligation and
      justification sit in two consecutive sentences.
- [x] C2. Write `fixtures/recall-gap-rule4.md`: an aphorism composed for this fixture, matching no
      template in either `data/register-*.json` maxim set.
- [x] C3. Write `fixtures/recall-gap-rule6.md`: a metaphor composed for this fixture, absent from
      both rule-6 candidate lists and from `docs/ARCHITECTURE.md`.
- [x] C4. Write `fixtures/control-conforming.md`: a document with no planted defect.
- [x] C5. Write one `fixtures/<name>.key.json` per fixture: `planted` holds `id`, `lines`, `rule`
      and `quote`. The control declares `planted: []`.
- [x] C6. Verify the fixture invariant by hand before it is asserted:
      `scan_register.py fixtures/*.md --json` reports no `warn` on any planted line.

**Why one rule per fixture.** A fixture carrying three planted rules cannot separate a pass that
found rule 4 from one that found rule 6.

**Why a quote in the key.** The line number moves when the fixture is edited. The quote is what a
later reader compares against.

## Cluster D — executor

- [x] D1. `run_authoring.py` builds the working directory under `tempfile.mkdtemp()` and asserts it
      holds no `CLAUDE.md`, no `.agent/` and no `.claude/`. A failed assertion exits 2.
- [x] D2. Build the command: `claude -p <prompt> --output-format json --model <model>` plus
      `--disallowed-tools` naming the file, command and network tools. `CLAUDECODE` is removed from
      the child environment.
- [x] D3. The `with_contract` arm prepends the text of `references/authoring-contract.md` under a
      fixed header. The `baseline` arm prepends nothing. No other input differs.
- [x] D4. Capture `result` from the envelope. Strip one enclosing fenced block when the whole output
      is one, and record `unwrapped` in the metadata.
- [x] D5. Write `corpus/<case>/<arm>/rep-<n>.md` and a sibling `rep-<n>.meta.json` holding model,
      arm, prompt SHA-256, contract SHA-256, `permission_denials`, `is_error` and duration. One
      metadata file per repetition, so a rerun of one repetition cannot overwrite another's record.
- [x] D6. `--reps` accepts an odd integer and defaults to 1. `--dry-run` prints the command and
      spawns nothing.

**Why the contract hash.** TASK R5. A corpus whose inputs are unrecorded cannot support a threshold
move.

**Why `--dry-run`.** Cluster E asserts the command shape without spending a token.

## Cluster E — instrument selftest

- [x] E1. Case `TC-EV-01` — set size: `evals.json` holds 10 cases, 6 on Axis A and 4 on Axis B (A8).
- [x] E2. Case `TC-EV-02` — grader direction: a golden conforming document and a violator document
      are scored, and the violator is higher on `warn_per_100_lines`, `marker_per_100_lines` and
      `sentence_mean` (A3).
- [x] E3. Case `TC-EV-03` — Axis B scorer: a golden answer scores recall 1.0 and precision 1.0; an
      answer missing one planted defect and inventing one scores below 1.0 on both.
- [x] E4. Case `TC-EV-04` — **fixture invariant**: for every fixture, the scanner reports no `warn`
      on any planted line, and the control fixture reports no `warn` at all (A4).
- [x] E5. Case `TC-EV-05` — key integrity: every `quote` in every key occurs on its declared line.
- [x] E6. Case `TC-EV-06` — prompt identity: for one case, the two arm prompts differ exactly by the
      contract block, verified by removing that block and comparing bytes (A1).
- [x] E7. Case `TC-EV-07` — isolation: the executor exits 2 on a directory holding `CLAUDE.md`, and
      on one holding `.agent/`, and on one holding `.claude/` (A2).
- [x] E8. Case `TC-EV-08` — command shape: `--dry-run` names `--disallowed-tools`, `--model` and
      `--output-format json`, and the tool list holds each tool the task names (A2.1).
- [x] E9. Case `TC-EV-09` — no reimplementation: `grade_run.py` declares no threshold name that
      `scan_register.DEFAULTS` also declares, and it imports `scan_register` (A3).
- [x] E10. Case `TC-EV-10` — report shape: a synthetic run with one empty output and one below the
      prose floor produces a summary naming both (A7).
- [x] E11. Case `TC-EV-11` — corpus shape: every directory under `corpus/` holds a `meta.json` beside
      each `rep-*.md` (A6). An empty `corpus/` passes and prints that it was empty.
- [x] E12. Case `TC-EV-12` — zero tokens: the selftest asserts that `run_authoring.spawn` is not
      reached, by running the whole battery with a sentinel that raises when called (A5).
- [x] E13. Case `TC-EV-13` — count pin: the battery asserts its own case count, and a second case
      reads that number out of `README.md`.
- [x] E14. `python3 evals/selftest_evals.py` exits 0.

**Why TC-EV-12 uses a sentinel.** An assertion that no subprocess ran is checkable only by making
the call site fail. Counting processes after the fact measures the machine, not the battery.

## Cluster F — campaign

- [x] F1. Run Axis A: `python3 evals/run_authoring.py --reps 1 --model claude-opus-5`. Record the
      wall time and the summed `total_cost_usd`.
- [x] F2. Run Axis B: one `claude -p` per fixture, prompted with `SKILL.md` §5, step B4 and the
      `--sections` worklist, returning JSON findings only.
- [x] F3. `python3 evals/grade_run.py --out evals/report.json`. Read the per-arm means.
- [x] F4. Record any case reported `measured: false`, and state it in the report rather than
      dropping it.
- [x] F5. Commit `corpus/` with its `meta.json` files and `report.json`.

**Why one repetition.** TASK OQ1. The report states that a single draw carries no interval.

## Cluster G — documents and CI

- [x] G1. Write `evals/README.md`: what each instrument measures, how it fails, how to run it, and
      what none of it proves. State the case count TC-EV-13 reads.
- [x] G2. Add §12 to `references/measurement-baseline.md` holding the campaign's figures, the
      command that reproduces them, and the corpus path. State that §11's requirement is now met for
      this corpus and for no other.
- [x] G3. Add the eval instrument to `SKILL.md` §8 Validation Evidence and to §9 Quick Reference.
      State that Mode A now carries a measurement, and name its size. Extend the
      `artifact-formalizer` entry in `System/Docs/SKILLS.md`, which states the skill's modes
      (audit 101, finding F1).
- [x] G4. Add `python3 .agent/skills/artifact-formalizer/evals/selftest_evals.py` to
      `.github/workflows/framework-gates.yml` in the `tooling-tests` job, with a comment stating
      that it spawns no agent.
- [x] G5. Add `scan_register.py`'s sibling script paths to `skill-safe-commands` if the new scripts
      are to auto-run. Decide against it when the executor spawns an agent.
- [x] G6. Run the full local gate set: the formalizer battery, `--probe`, the new selftest,
      `validate_skills.py`, `check_prompt_references.py`, `security_lint.py`.
- [x] G7. Scan the three authored documents of this task:
      `scan_register.py docs/TASK.md docs/PLAN.md docs/ARCHITECTURE.md --sections --terms
      docs/ARCHITECTURE.md`.

## Verification checkpoints

| After cluster | Command | Expected |
| :--- | :--- | :--- |
| A | `python3 evals/selftest_evals.py` | non-zero; the stubs are not an implementation |
| C | `scan_register.py evals/fixtures/*.md` | no `warn` on any planted line |
| E | `python3 evals/selftest_evals.py` | exit 0, every case named |
| F | `python3 evals/grade_run.py` | `grading.json` written, per-arm means printed |
| G | `python3 scripts/selftest_scan.py` and `--probe` | 191 cases exit 0; 18 detectors exit 0 |
| G | `python System/scripts/validate_skills.py --root . --quiet` | exit 0 |
| G | `python System/scripts/security_lint.py --root .` | exit 0 |

## Out of plan

No cluster edits `scripts/scan_register.py`, `data/register-*.json` or any threshold. TASK §7 states
why: this task measures the skill and does not move it. A finding that argues for a threshold change
is recorded in the report and filed, not applied here.
