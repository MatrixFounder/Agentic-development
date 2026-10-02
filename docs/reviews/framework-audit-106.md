# Framework Audit 106 — a test-to-rule map, one name per check, and ASD-STE100 on record

- **Task:** 106 `formalizer-term-map-and-ste100`. It archives to
  `docs/tasks/task-106-formalizer-term-map-and-ste100.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.0,
  Modes A and B.
- **Date:** 2026-10-02. **Base revision:** `5b96f01`. **Release:** v3.31.2.
- **Source:** operator review of ASD-STE100 against `artifact-formalizer`. Items Р1, Р2, Р3 and Р5
  were approved; Р4 was deferred.

## 0. Emergency Bypass

None set. No TIER 0 skill, bootstrap file or workflow is edited.

## Mode A — SPECIFICATION AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R8 each name an acceptance id |
| 2 | Skill Compatibility | PASS — no new agent, prompt or workflow; TIER 0 skills untouched |
| 3 | Documentation | PASS — R1 edits `System/Docs/SKILLS.md`; R7 covers both changelogs and `version` |
| 4 | Migration | PASS — no session format changes |
| — | Blocking conditions | None triggered |

**Check 1.** R2's pin is written first and fails on the base tree, which states 59 in two sites.

**Check 4.** `run_authoring.py` hashes the contract into each run's `meta.json`. R3 and R4 change
that hash for future runs. `selftest_evals.py` asserts the hash is present, never its value. The
committed corpus stays valid as a record of the prior contract, as `evals/corpus-wi12/` did.

**Blocking conditions.** `core-principles` and `skill-safe-commands` are unmodified. `CLAUDE.md`,
`AGENTS.md` and `GEMINI.md` are unmodified.

**Risks the specification bounds.**

- **R3 adds a column every authoring phase reads.** Cell shape stays under
  `documentation-standards` §5.1, and `TC-SHIP-06` fails if it does not.
- **R6 adds text that two battery cases parse.** TASK §2.1 R6 names both constraints.
- **R4 renames a label agents may quote.** No T4 citation of `One claim` exists outside the contract
  cell. T-numbers do not change, so `reg-12` and `wi-16` still resolve.

## Mode B — PLAN AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — every cluster ends in a run; Cluster G runs every CI gate locally |
| 2 | Rollback | PASS — Cluster A backs up the bootstrap files and the eight edited files |
| 3 | Atomic updates | PASS — seven clusters, one requirement group each |
| 4 | Test coverage | PASS — `TC-EV-13b` widened in place; executed mutations name their site |

**Check 2.** The tree is clean at start, so `git checkout --` is the second rollback layer.

**Check 3.** Cluster B fails on purpose. Cluster C is the first place the pin passes.

**RTM coverage.** R1 → C · R2 → B · R3 → D1, D2 · R4 → D3 · R5 → D4 · R6 → E · R7 → F · R8 → G.

## Execution evidence (gates)

Final run, after the review fix loop.

| Gate | Command | Result |
|---|---|---|
| G1 | `scripts/selftest_scan.py` | **192/192** |
| G2 | `evals/selftest_evals.py` | **78/78**, 0 agents, 0 tokens |
| G3 | `scan_register.py --probe` | **18/18 detectors live** |
| G4 | `scan_register.py` over `SKILL.md`, `references/*.md`, `docs/TASK.md`, `docs/PLAN.md` | **0 warn**, 36 info |
| G5 | `grep -rn "One claim" .agent/skills` | 4 lines: three rule-1 sites and the §4.2 record |
| G6 | `git status --short` | the declared file set and nothing else |
| G7a | `check_positional_refs.py --all docs/*.md docs/issues docs/backlog` (CI living corpus) | **0 errors**, 5 warnings |
| G7b | `check_positional_refs.py --targets-changed --fix` | 13 errors, all pre-existing; 3 repairs |
| G8a | `System/scripts/validate_skills.py --root . --quiet` | **46/46** |
| G8b | `PYTHONPATH=. python3 tests/run_tests.py` | **351 tests OK** |
| G8c | `python3 -m pytest tests/ -q` | **448 passed**, 124 subtests |
| G9 | `check_prompt_references.py`, `security_lint.py`, `generate_wrappers.py --check` | all pass |
| G9d | `System/scripts/check_loop_contract.py` | 25 loops, 0 errors |

**G4.** The 36 info findings are pre-existing. Each edited document was scanned against its
`.agent/archive/` backup, and the new text adds none. Both v3.31.2 changelog entries scan at 0/0.

**G7a.** All 5 warnings are `DRIFT_SUSPECT` inside ledger record bodies (`wi-13`, `arc-11`, `reg-9`,
`reg-10`, `reg-13`). A record body is preserved byte-for-byte (`known-issues-format` §8), so none
is edited.

**G7b.** The 13 errors sit in five documents: both changelogs' older entries, `plan-103`,
`framework-audit-105` and `framework-audit-20260813-reference-gate-scope`. The same five report 13
errors at `5b96f01`, checked in a detached worktree. The first `--fix` run repaired three
`REFERENT_MOVED` in `docs/TASK.md`. Each pointed at a changelog line the v3.31.2 entry pushed
down. Two of the three were later pinned to `@5b96f01` instead.

### Mutations, executed

Each was applied alone to the working file, run, and reverted; every revert returned 78/78.

| # | Mutation | Outcome |
|---|---|---|
| 1 | `SKILL.md` count 78 → 59 | red, names `SKILL.md` [59] |
| 2 | `System/Docs/SKILLS.md` count 78 → 59 | red, names `SKILLS.md` [59] |
| 3 | `evals/README.md` run-command count 78 → 77 | red, names `README.md` [77, 78] |
| 4 | `SKILL.md` numeral deleted | red, names `SKILL.md` [] |
| 5 | `SKILL.md` gains a stale second count in the same sentence | red, names `SKILL.md` [78, 59] |
| 6 | `SKILL.md` count written `1,078` | red, names `SKILL.md` [] |
| 7 | `System/Docs/SKILLS.md` deleted, `System/Docs/` present | red, `missing=['System/Docs/SKILLS.md']` |
| 8 | `SKILL.md` re-wrapped between `78` and `cases` | green, as intended |

## Review round (G11)

`code-reviewer` and `security-auditor` ran in parallel over tree fingerprint `099216ac0488`. The
command was `{ git rev-parse HEAD; git status --porcelain; git diff HEAD; } | shasum -a 256`. Both
quoted the value back. The caller recomputed it at return and found it unchanged, so the round
stands.

| Reviewer | Verdict | Blocking |
|---|---|---|
| `code-reviewer` | APPROVE WITH CHANGES | none |
| `security-auditor` | PASS WITH NOTES | none; no Critical or High |

**Applied.** TASK D7 lists each fix. In short:

- the §4.2 reopen bar is a defect rate;
- the §4.2 corpus uses `detect_lang()`, 131 files instead of 135;
- the changelog says seven rules assessed, four measured;
- `TC-EV-13b` reads span-wide, spans a re-wrap, rejects aliases, and requires the registry here;
- the third-party link is pinned to `7d4a135` and marked as data;
- three new sentences that broke T2 or T4 were rewritten;
- the PLAN counts were corrected;
- this table was filled in.

**Deferred.** TASK D8 lists each one with its reason.

- `TC-SHIP-10` cannot read the §4.2 table. The operator chose not to file it.
- `System/Docs/SKILLS.md`'s `192-case` is read by no case. Filed as REG-19.
- A per-site count pin was rejected.
- `scripts/selftest_scan.py:1010` cites a contract line already stale at `5b96f01`. That file is
  outside this task's file set.

**Security notes left as they are.** No workflow declares `permissions:`, which predates this
change. External scanners (semgrep, gitleaks, bandit) are not installed. Their regex layer found
nothing in the changed files.

## Retro (run-feedback §7)

The operator answered the retro question on 2026-10-02. Filed:

| ID | Kind | Subject |
|---|---|---|
| REG-19 | defect, SEV-4 | `TC-SHIP-08` exempts a whole list item, so a `192-case` count is read by no case |
| WI-19 | work-item, M | measure term consistency before the contract gains a rule for it |
| WI-20 | work-item, M | roll back through git instead of `.bak` copies |

**Dismissed as noise.** One candidate said `selftest_scan.py` runs about two minutes. Measured, it
runs in 7.27 s. The one timeout this run saw came from a compound command, and its cause was not
identified.

**Prefix table.** `REG` has no row in the `docs/KNOWN_ISSUES.md` prefix table, although the ledger
holds REG-1 to REG-19. That gap predates this task.
