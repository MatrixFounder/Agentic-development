# Framework Audit 107 — framework-upgrade rolls back through git

- **Task:** 107 `framework-upgrade-git-rollback`. It archives to
  `docs/tasks/task-107-framework-upgrade-git-rollback.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.0,
  Modes A and B.
- **Date:** 2026-10-02. **Base revision:** `687d0466e807585b994f2faa479dbbf17024dfb6`, clean tree
  at start.
- **Source:** WI-20, option 1, chosen by the operator.

## 0. Emergency Bypass

None set.

**This run follows the substance of the rule it ships, not its final form.** §3.1 of the base
workflow still asks for copies in `.agent/archive/`. The operator ruled them out on 2026-10-02,
before this run. The run took its rollback point from a clean tree at the base above and wrote no
copy. It recorded the base short at first, and not in session state; the final §0 asks for both.
Mode B check 2 below is judged on that substance; this task rewrites the check's wording.

## Mode A — SPECIFICATION AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R9 each name an acceptance id; R8's pin is written before the edits |
| 2 | Skill Compatibility | PASS — no new agent, prompt or workflow; TIER 0 skills untouched |
| 3 | Documentation | PASS — R6 edits `System/Docs/WORKFLOWS.md`; R9 covers both changelogs |
| 4 | Migration | PASS — copies from earlier runs stay ignored (D4); nothing reads them |
| — | Blocking conditions | None triggered |

**Blocking conditions.** `core-principles` and `skill-safe-commands` are unmodified. `CLAUDE.md`,
`AGENTS.md` and `GEMINI.md` are unmodified. No workflow is added.

**Check 4.** This clone's copies were deleted before the base. Another clone may still hold
copies from an earlier run; the `.gitignore` entry stays, so they stay out of `git status`. A run
started after this task writes none and restores from git.

## Mode B — PLAN AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — every cluster ends in a run; Cluster E runs every CI gate locally |
| 2 | Rollback | PASS — base `687d046` recorded at a clean tree; restore and removal steps stated |
| 3 | Atomic updates | PASS — five clusters, one requirement group each |
| 4 | Test coverage | PASS — a new unittest module, written first; executed mutations per round |

**Check 2.** The base check text asks for a copy step. The plan has none, by the operator's
decision and by this task's own requirement. The check is judged on whether every edited path
returns to a known state, and it does.

**RTM coverage.** R1–R3 → B · R4–R6 → C · R7 → D · R8 → A · R9 → E.

## Review round 1

Tree fingerprint `67e0f8050084`, computed with
`{ git rev-parse HEAD; git status --porcelain; git diff HEAD; } | shasum -a 256 | cut -c1-12`.

| Reviewer | Verdict | Round |
|---|---|---|
| `code-reviewer` | REQUEST CHANGES | valid; fingerprint quoted and unchanged |
| `security-auditor` | PASS WITH NOTES | **failed** — the role wrote to the frozen tree |

**The failed round.** The auditor's `rsync … && cd <copy>` stopped on the dangling symlink
`.cursor/skills`. The `cd` never ran, so its mutations landed in the repository. It edited three
files and ran `git checkout --` on a fourth, which the brief forbade. It restored all four and
reported the incident itself. The caller then confirmed the fingerprint and each file unchanged.
Per `skill-parallel-orchestration` §2.4.1, the round records no pass. Its findings entered the fix
loop as input.

**Blocking finding.** `code-reviewer` rated it High; the auditor rated the same mechanism Medium.
§5 removed every untracked path its listing showed. That
listing can hold paths the run never created:

- `status.showUntrackedFiles=no` hid them at §0;
- §5 ran from a subdirectory;
- another writer acted during the run;
- HEAD moved past the base.

TASK D6 lists the fixes and D7 what was left.

## Review round 2

Tree fingerprint `8c8b9095f1f3`. Both roles quoted it, recomputed it at return, and wrote nothing
in the repository; the caller confirmed the value unchanged.

| Reviewer | Verdict | Round |
|---|---|---|
| `code-reviewer` | REQUEST CHANGES | valid |
| `security-auditor` | PASS WITH NOTES | valid |

**Round 1 closure.** Both roles marked every round-1 finding closed, except the blocking one,
which both marked partly closed.

**The shared finding.** §5 restored first and then read the declared set from `docs/PLAN.md`,
which the restore had just reverted. The restore also discarded a tracked edit the PLAN did not
declare, with no list shown first. TASK D8 lists the fixes. §5 now lists, checks, shows and waits
before it restores anything, and it restores by name.

### Mutations, round 2

Round 2 ran 24 mutations; each gave the outcome recorded for it in TASK D8. The final round below
supersedes them.

## Review round 3

Tree fingerprint `af13d6aafd4d`. `code-reviewer` checked closure only, quoted the fingerprint,
recomputed it at return, and wrote nothing in the repository. The caller confirmed it unchanged.

| Reviewer | Verdict | Round |
|---|---|---|
| `code-reviewer` | APPROVE WITH CHANGES | valid |

**Closure.** Both round-2 blocking findings closed, each reproduced in a throwaway repository: an
undeclared tracked edit and an undeclared staged file both stop §5 before anything moves.

**Applied from its list.** TASK D9 lists each fix. The major one: `$top` did not survive between
shell calls, so an unset variable turned `rm -- "$top/<path>"` into a path under `/`. §5 now sets
`top` again and removes with `rm -- "${top:?}/<path>"`.

### Mutations, final round

Each was applied alone to the working file, run, and reverted. The module returned to 7 of 7
after each. Names are the mutation script's labels.

| # | Mutation | Outcome |
|---|---|---|
| 1 | copy: workflow gains .bak | red, TC-02 |
| 2 | copy: SKILL.md names .agent/archive | red, TC-02 |
| 3 | copy: System/Agents prompt gains .bak | red, TC-02 |
| 4 | copy: .claude/commands wrapper | red, TC-02 |
| 5 | copy: .orig | red, TC-02 |
| 6 | copy: .old | red, TC-02 |
| 7 | copy: .backup | red, TC-02 |
| 8 | copy: .agent/backups | red, TC-02 |
| 9 | copy: codex .toml | red, TC-02 |
| 10 | copy: .agent/rules file | red, TC-02 |
| 11 | check 2 loses 'base commit' | red, TC-03 |
| 12 | check 2 reflowed | green, as required |
| 13 | §0 deleted | red, TC-04 and TC-01 |
| 14 | §0 clean item loses STOP | red, TC-01 |
| 15 | §0 agent stashes itself | red, TC-04 |
| 16 | §0 --add_decision dropped | red, TC-01 |
| 17 | §0 ls-files command reflowed | green, as required |
| 18 | §2.2 declaration sentence dropped | red, TC-01 |
| 19 | §3.1 HEAD check -> commit per cluster | red, TC-01 |
| 20 | §3.1 path-regex bullet dropped | red, TC-01 |
| 21 | §3.1 gains git reset --hard | red, TC-04 |
| 22 | §4.5 repair list dropped | red, TC-01 |
| 23 | §5 confirmation sentence dropped | red, TC-01 |
| 24 | §5 subagent sentence dropped | red, TC-01 |
| 25 | §5 step 0 dropped | red, TC-01 |
| 26 | §5 `${top:?}` becomes `$top` | red, TC-01 |
| 27 | §5 remove -> rm -rf | red, TC-04 and TC-01 |
| 28 | §5 rm -fr | red, TC-04 |
| 29 | §5 rm -R | red, TC-04 |
| 30 | §5 rm --recursive | red, TC-04 |
| 31 | §5 broad restore :/ added | red, TC-04 |
| 32 | §5 `git restore .` added | red, TC-04 |
| 33 | §5 restore -> reset --hard + clean | red, TC-04 and TC-01 |
| 34 | §5 restore hidden in a comment | red, TC-04 and TC-01 |
| 35 | §5 git clean beside the prohibition | red, TC-04 |
| 36 | §5 R/C rule dropped | red, TC-01 |
| 37 | §5 re-list after reply dropped | red, TC-01 |
| 38 | §5 Check step dropped | red, TC-01 |
| 39 | §5 order: restore before list | red, TC-01 |
| 40 | §5 order: restore before remove | red, TC-01 |
| 41 | copy: corpus-* outside evals | red, TC-02 |

## Execution evidence (gates)

Final run, after the round-3 fix loop.

| Gate | Command | Result |
|---|---|---|
| A1 | `python3 -m pytest tests/test_git_rollback_contract.py -q` | **7 passed** |
| A2 | the mutation script, 41 mutations | 39 red, 2 reflows green, as required |
| A3 | `System/scripts/validate_skills.py --root . --quiet` | **46/46** |
| A4 | `PYTHONPATH=. python3 tests/run_tests.py` | **358 tests OK**, the new module included |
| A5 | `python3 -m pytest tests/ -q`; `check_loop_contract.py` | **455 passed**, 124 subtests; 0 errors |
| A6 | `scan_register.py`, each edited instruction file against `687d046` | **0 new findings** |
| A6 | `scan_register.py` over TASK, PLAN, this audit, both v3.32.0 entries | **0 warn, 0 info** |
| A7 | `git status --short` | the declared paths and nothing else |
| A8 | CI living-corpus reference check | **0 errors** |
| §4.5 | `check_positional_refs.py --targets-changed --fix` | 9 errors, the same 9 as at the base; 0 repairs |
| CI | `check_prompt_references.py`, `security_lint.py`, `generate_wrappers.py --check` | all pass |
| CI | `smoke_workflows.py` | pass |
| — | formalizer selftest and evals; `test_frozen_tree_contract.py` | 192/192; 78/78; 7 passed |
| — | `skill-enhancer/scripts/analyze_gaps.py` on the verificator | no blocking gap; 6 advisories, as at base |

**The 6 advisories.** They are the verificator's missing Red Flags, Rationalization Table,
Execution Mode, Script Contract, Safety Boundaries and Validation Evidence sections. All six
predate this task, and WI-20 does not ask for them.

## Retro (run-feedback §7)

The operator answered the retro question on 2026-10-02: this was a service run, and nothing is
filed. Six candidates were offered:

- the reviewer that wrote into the frozen tree;
- the dangling `.cursor/skills` symlink;
- the two contract tests absent from CI;
- `--fix` touching ignored files;
- a sandbox rule for destructive steps;
- the verificator's missing sections.
