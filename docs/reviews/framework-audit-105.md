# Framework Audit 105 — a read-only round runs against a frozen tree

- **Task:** 105 `frozen-tree-fingerprint` (`docs/TASK.md` at audit time; archives to `docs/tasks/task-105-frozen-tree-fingerprint.md`)
- **Workflow:** `/framework-upgrade` · **Meta-skill:** `skill-self-improvement-verificator` v1.0 (Modes A + B)
- **Date:** 2026-08-11 · **Release:** v3.29.0
- **Source:** RF-7 (onchain-analytics ledger). Operator selected options 1 and 3 of the four the record lists.

## Mode A — SPECIFICATION AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Root Integrity | PASS — R1–R10 each carry an acceptance id; A4 names the mutation that reddens the test; the test is written before the edits it governs (Stub-First for a text product, precedent TASK 104) |
| 2 | Skill Compatibility | PASS — no new agent, prompt or workflow. TIER 0 skills untouched; the edit lands in a TIER 2 skill and its readers |
| 3 | Documentation | PASS — R10 covers both changelogs. `System/Docs/SKILLS.md:53` carries no version field for this skill, so the registry row needs no edit; the skill's own `version:` and `## 9. History` do |
| 4 | Migration | PASS — the clause is additive. A brief written before this change lacks the line and is reported by the test, never silently accepted |
| — | Blocking conditions | None triggered — `core-principles` and `skill-safe-commands` unmodified; `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` unmodified; no new workflow needing a trigger declaration |

**Note on check 3.** The generated vendor wrappers under `.gemini/`, `.codex/`, `.cursor/` and
`.antigravity/` are outputs of `scripts/generate_wrappers.py`. Editing `wrappers_manifest.json` and
regenerating is the documented path; hand-editing a generated wrapper is forbidden by the manifest's
own comment. The plan gate runs `generate_wrappers.py --check` for drift.

## Mode B — PLAN AUDIT — **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Verification step | PASS — Cluster E runs `tests/test_frozen_tree_contract.py`, the full suite, `generate_wrappers.py --check`, `scan_register.py`, and the reference resolver |
| 2 | Rollback | PASS — Cluster A step 0 backs up every file the change touches to `.agent/archive/`; the tree is clean at start, so `git checkout --` is the second layer |
| 3 | Atomic updates | PASS — five clusters, each ending in a verification; Cluster B leaves the test red on purpose and Cluster E is the only place it may be green |
| 4 | Test coverage | PASS — one new test file with three assertions, plus the recorded mutation for each |

## Execution evidence (gates)

Recorded in `docs/PLAN.md` §Gates and filled in on execution. This section is completed at the end
of Cluster E, not at audit time.

| Gate | Command | Result |
|---|---|---|
| G1 | `python3 -m pytest tests/test_frozen_tree_contract.py` | **7 passed** |
| G2 | `python3 -m pytest tests/` | **435 passed, 114 subtests** (428 before this task) |
| G3 | `generate_wrappers.py --check` | **OK — all 12 scaffold wrappers match the manifest** |
| G4 | `scan_register.py`, each edited file against its `.bak` | **0 new warnings** across 16 files + both changelogs |
| G5 | `check_positional_refs.py --targets-changed --fix` | **exit 0**, 2 repaired; 1 pre-existing error out of scope (below) |
| G6 | three executed mutations | each turns a different assertion red (below) |
| G7 | `python3 System/scripts/check_loop_contract.py` | **checked 25 loops: 0 error(s), 0 warning(s)** |

### G6 — the mutations, executed

| # | Mutation | Assertion that reddened |
|---|---|---|
| MUT-1 | fingerprint line deleted from `vdd-adversarial.md` | `TC-01` — caller site missing the line |
| MUT-2 | `critic-security.md` told to **compute** with `shasum` | `TC-02` quote-instruction **and** the hash-command guard |
| MUT-3 | a new contract-carrying workflow added, undeclared | `TC-03` partition completeness |

Each was restored and the suite re-run green before the next.

### G5 — 7 errors, all pre-existing, none this change's

The final run reports 7 errors across 2 classes. Every one sits in text this change did not write.
`--targets-changed` selects documents *citing* an edited file, and then checks all of that
document's references — so editing a changelog pulls the whole changelog's history into scope.

| Class | Count | Where | Why it is not this change's |
|---|---|---|---|
| `UNRESOLVABLE` | 6 | `CHANGELOG.md:88-89`, `CHANGELOG.ru.md:86-87` | The **v3.28.1** entry quotes `get-token.ts:117` / `wallet-balances.ts:92` — coordinates in the `onchain-analytics` consumer repo, cited as the illustration of the defect that entry fixed. No such file exists here, and none can. The v3.29.0 entry sits above them at lines 19–81 and is untouched by the finding |
| `REFERENT_ABSENT` | 1 | `docs/reviews/review-095-independent.md:35` → `check_prompt_references.py:21` | Neither file is touched here, so the reference stands exactly as at `7056556`. It is a review artifact — a record of what a reviewer saw — so the coordinate is reported, not rewritten |

**Recorded rather than fixed, deliberately.** Editing the v3.28.1 entry to make the resolver quiet
would falsify a released changelog; editing the review would falsify a record. The
`UNRESOLVABLE`-on-a-foreign-repo-coordinate class is a genuine gap in the resolver's scoping, and it
belongs to that tool's backlog, not to this task.

**Two `REFERENT_MOVED` repairs landed that this change did not cause, and they stay.**
`--fix` rewrote `full-robust.md:47` → `:82` and `framework-gates.yml:51-64` → `:134-147` in
`docs/reviews/review-095-independent.md`. Neither target is edited here; the review entered scope
for citing an edited file, and once a document is in scope every one of its references is checked.
`framework-upgrade` §4.5 mandates `--fix` and states the repair lands in the same commit, so the two
are kept rather than reverted. The referent text is unchanged in both — only the coordinate moved.

### G7 — a regression this task caused and fixed

The freeze bullet added six lines between three `<!-- loop:* -->` markers and their canonical
`Max N` line, pushing the bound outside the 13-line resolution window.
`check_loop_contract.py` returned `BOUND_UNRESOLVABLE` for `01-start-feature.task-review`,
`01-start-feature.arch-review` and `02-plan-implementation.plan-review`. Fixed by moving the three
markers to sit directly above their loop bodies — the placement `vdd-01-start-feature` and
`vdd-02-plan` already use, which is why those two did not fail. Found by the suite, not by review.

## Versions

| Component | Before | After |
|---|---|---|
| `skill-parallel-orchestration` | 3.8 | **3.9** |
| Framework | v3.28.1 | **v3.29.0** |
