# PLAN 107 — framework-upgrade rolls back through git, and writes no copy outside it

**TASK:** [docs/TASK.md](TASK.md) · **Covers:** R1–R9 · **Acceptance:** A1–A8

## Sequencing rule

Five clusters in order. Cluster A writes the pin and leaves it **failing** on the base tree, which
still instructs copies. Cluster B edits the workflow, Cluster C its three readers, and Cluster D the
two comments. Cluster D is the first point where the pin passes. Cluster E closes WI-20, writes
the release and runs every gate.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | The pin, failing | `tests/test_git_rollback_contract.py`, `tests/run_tests.py` | R8 |
| B | The workflow | `.agent/workflows/framework-upgrade.md` | R1, R2, R3 |
| C | Its readers | verificator `SKILL.md`, `assets/audit_template.md`, `examples/audit_examples.md`, `System/Docs/WORKFLOWS.md` | R4, R5, R6 |
| D | Two comments | `.gitignore`, `tests/test_frozen_tree_contract.py` | R7 |
| E | Closure, release, gates | WI-20, `docs/BACKLOG.md`, both changelogs, `docs/reviews/framework-audit-107.md` | R9, A1–A8 |

The verificator lives at `.agent/skills/skill-self-improvement-verificator/`.

**Declared paths (A7, `framework-upgrade` §2.2).** Edited:

- `.agent/workflows/framework-upgrade.md`
- `.agent/skills/skill-self-improvement-verificator/SKILL.md`
- `.agent/skills/skill-self-improvement-verificator/assets/audit_template.md`
- `.agent/skills/skill-self-improvement-verificator/examples/audit_examples.md`
- `System/Docs/WORKFLOWS.md`
- `.gitignore`
- `tests/test_frozen_tree_contract.py`
- `tests/run_tests.py`
- `docs/backlog/wi-20-framework-upgrade-keeps-bak-copies-beside-git-roll-back-through-git-instead.md`
- `docs/BACKLOG.md`
- `CHANGELOG.md`
- `CHANGELOG.ru.md`

Created:

- `tests/test_git_rollback_contract.py`
- `docs/reviews/framework-audit-107.md`

The run's own `docs/TASK.md`, `docs/PLAN.md` and the TASK 106 archive pair are declared by §5.

**Rollback point.** Base `687d0466e807585b994f2faa479dbbf17024dfb6`, clean at the start of the
run. No copy is written. Fallback follows `framework-upgrade` §5 over the paths above.

## Cluster A — the pin, failing (R8)

- [x] A1. Write `tests/test_git_rollback_contract.py`, pure `unittest`. The first version held
      three cases; the review rounds grew it to four (TASK R8, D6, D8, D9).
      1. `TC-01` — §0, §2.2, §3.1, §4.5 and §5 carry their controls; §5 keeps its order.
      2. `TC-02` — no instruction file names a copy. The failure names each file and line.
      3. `TC-03` — the verificator's Mode B check 2 names the base commit.
      4. `TC-04` — commands that act on unnamed paths appear only in prohibitions.
- [x] A2. Add `"test_git_rollback_contract"` to `CURATED_UNITTEST_MODULES` in `tests/run_tests.py`.
- [x] A3. Run the module. Expected: `TC-01`, `TC-02` and `TC-03` fail on the base tree.

**Why `TC-02` reads instruction files only.** It reads markdown, the YAML rule files, and the
vendor TOML and JSON agent files. Scripts such as the installer write their own snapshots under
`.agent/backups/`, which TASK §7 leaves out of scope.

## Cluster B — the workflow (R1, R2, R3)

- [x] B1. `framework-upgrade.md`: insert `## 0. Rollback point (before any edit)` above §1, per TASK
      R1. It names the audit header as where the base is recorded.
- [x] B2. Replace §3.1 "Backup" with "Rollback point", per TASK R2.
- [x] B3. Replace §5 "Fallback", per TASK R3.
- [x] B4. Keep both `<!-- loop:… -->` sites and the frontmatter unchanged; run
      `System/scripts/check_loop_contract.py`. Expected: 0 errors.
- [x] B5. Run the pin. Expected: `TC-01` passes; `TC-02` still fails on the verificator files and
      `WORKFLOWS.md`.

## Cluster C — the readers (R4, R5, R6)

- [x] C1. Verificator `SKILL.md` Mode B check 2: TASK R4's question. Frontmatter `version: 1.1`.
- [x] C2. `assets/audit_template.md`: the Rollback Plan row asks the same question.
- [x] C3. `examples/audit_examples.md`: each header carries `Base revision`; the good row declares
      its created files; the bad row's required action stops the run (final text: TASK D6, D8).
- [x] C4. `System/Docs/WORKFLOWS.md` §5 Safety Protocol item 4: TASK R6.
- [x] C5. Run the pin. Expected: every case passes.

## Cluster D — the two comments (R7)

- [x] D1. `.gitignore`: the comment above `.agent/archive/` states that no run writes copies now,
      and that the entry stays for clones holding older ones.
- [x] D2. `tests/test_frozen_tree_contract.py`: the comment above `SCAN_ROOTS`, the same way.
      `_is_scanned` is not edited.
- [x] D3. Run `python3 -m pytest tests/test_frozen_tree_contract.py -q`. Expected: pass.

## Cluster E — closure, release, gates (R9, A1–A8)

- [x] E1. Execute the A2 mutations from TASK §4, one at a time; the audit records each outcome.
- [x] E2. Close WI-20: `status: done`, `resolved_at`, `resolved_by: TASK 107`, a resolution
      blockquote, and the index line moved to `## Closed` in `docs/BACKLOG.md`.
- [x] E3. `CHANGELOG.md` and `CHANGELOG.ru.md`: a `v3.32.0` entry above `v3.31.2`.
- [x] E4. `scan_register.py` over every edited markdown file → no new `warn` (A6).
- [x] E5. `validate_skills.py`, `tests/run_tests.py`, `pytest tests/`, `check_loop_contract.py`,
      `check_prompt_references.py`, `security_lint.py`, `generate_wrappers.py --check` (A3–A5).
- [x] E6. CI living-corpus reference check, then `--targets-changed --fix` (A8, workflow §4.5).
- [x] E7. `git status --short` → the declared file set (A7).
- [ ] E8. Review per the Self-Improvement Mode rule: `code-reviewer` and `security-auditor` in
      parallel, over a frozen tree with its fingerprint.
- [ ] E9. Fill the audit's evidence table.

## Review fix loop (round 1 → round 2)

Run after round 1 returned. TASK D6 lists what was fixed and D7 what was left.

- [x] F1. Workflow §0, §3.1 and §5 rewritten per TASK R1–R3 as amended.
- [x] F2. Verificator check 2, template and examples: `Base revision` field; the bad example
      stops the run.
- [x] F3. `WORKFLOWS.md` item 4: the operator confirms; only declared files are removed.
- [x] F4. The pin: sections read separately, prompt and wrapper roots scanned, tokens widened,
      `TC-04` added. Eleven mutations executed (TASK A2).
- [x] F5. TASK, both changelogs and the WI-20 resolution re-stated; all scan at 0 warn.
- [x] F6. Every gate re-run, then round 2 over a new fingerprint.

## Review fix loop (round 2 → round 3)

TASK D8 lists what was fixed.

- [x] G1. §5 lists, checks, shows and waits before it restores; it restores by name.
- [x] G2. §0, §2.2, §3.1 and §4.5 carry the checks the declared set needs.
- [x] G3. The pin checks each §5 control and its order; `TC-04` reads the whole workflow.
- [x] G4. 24 mutations executed; the audit lists each outcome.
- [x] G5. Every gate re-run; round 3 checks that the round-2 findings are closed.

## Review fix loop (round 3)

TASK D9 lists what was fixed.

- [x] H1. §5 sets `top` again, removes before it restores, handles `R` and `C`, and ends on a
      status check; the confirmed list is recorded and taken again.
- [x] H2. §2.2 asks for full paths; §3.1 rejects `.git`, `..` and absolute paths.
- [x] H3. The pin pins the new sentences and catches more destructive spellings; 41 mutations.
- [x] H4. Every gate re-run; Retro.
