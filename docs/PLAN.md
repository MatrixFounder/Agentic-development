# PLAN 105 — A read-only round runs against a frozen tree, and the brief carries its fingerprint

**TASK:** [docs/TASK.md](TASK.md) · **Covers:** R1–R10 · **Acceptance:** A1–A6

## Sequencing rule

Five clusters. Cluster A backs up and fixes the site set from disk. Cluster B writes the test and
leaves it **red** — the test is the executable form of the site set, and writing it first is
Stub-First applied to a task whose product is text. Cluster C edits the source of truth. Cluster D
edits its readers, caller side then role side. Cluster E runs every gate and is the only cluster in
which the test may be green.

## Site set

Derived from `grep -rln "NOT RUN"` over `.agent/`, `.claude/` and the four vendor agent directories,
partitioned by what the file does with the evidence block.

**Caller side — the file instructs someone to WRITE a brief (9 files).**

| # | File | Site |
| :--- | :--- | :--- |
| 1 | `.agent/skills/skill-parallel-orchestration/SKILL.md` | §2.4, source of truth |
| 2 | `.agent/skills/skill-parallel-orchestration/references/sequential-fallback.md` | concrete pattern step 0 |
| 3 | `.agent/workflows/vdd-multi.md` | Step 1.0, Step 1.1 skeleton, sequential step 0 |
| 4 | `.agent/workflows/vdd-adversarial.md` | step 2a block |
| 5 | `.agent/workflows/vdd-enhanced.md` | §4 item 8 |
| 6 | `.agent/workflows/01-start-feature.md` | steps 4 and 5 |
| 7 | `.agent/workflows/vdd-01-start-feature.md` | steps 4 and 5 |
| 8 | `.agent/workflows/02-plan-implementation.md` | step 3 |
| 9 | `.agent/workflows/vdd-02-plan.md` | step 3 |

**Role side — the file defines a role that READS a brief (19 definitions + the manifest).**

| # | File | Note |
| :--- | :--- | :--- |
| 10–12 | `.claude/agents/critic-{logic,security,performance}.md` | donors, hand-maintained |
| 13–15 | `.claude/agents/{task,plan,architecture}-reviewer.md` | phase gate reviewers |
| 16 | `.claude/agents/security-auditor.md` | holds Bash; carries the caller-side obligation instead |
| 17 | `.agent/skills/skill-parallel-orchestration/scripts/wrappers_manifest.json` | one edit regenerates 12 scaffolds |

**Excluded, with the reason recorded in the test.**

| File | Reason |
| :--- | :--- |
| `.agent/workflows/full-robust.md` | consumes a verdict; writes no brief and defines no role |
| `.agent/skills/security-audit/SKILL.md` | methodology read by a role that holds Bash |
| `.agent/skills/skill-adversarial-{security,performance}/SKILL.md` | persona methodology; the wrapper carries the block contract |
| `.agent/skills/vdd-adversarial/SKILL.md` | same |

Counted at `7056556`: 9 caller + 20 role + 5 excluded = **34** files carrying the contract token.
`.agent/archive/` is outside the scan roots — it holds `.bak` copies that would otherwise be
counted as sites.

## Cluster A — backup

- [x] **A1** [R1–R10] `mkdir -p .agent/archive` and copy every file in the site set to
      `.agent/archive/<basename>.bak`. `git status --porcelain` is empty at start, so the working
      tree is the second rollback layer.
- [x] **A2** Record the site-set greps and their counts in this plan under Gates.

**Verification:** every backed-up file exists under `.agent/archive/`.

## Cluster B — the test, red

- [x] **B1** [R9] Create `tests/test_frozen_tree_contract.py` with three assertions.
      - **TC-01** — every caller-side file carries the fingerprint clause.
        `TC-01 — the 9 caller files → each contains the fingerprint marker; fails when the marker is
        deleted from any one of them.`
      - **TC-02** — every role-side file carries the quote-it instruction and instructs no
        computation. `TC-02 — the 19 role definitions and the manifest → each contains the quote instruction and no
        hash command; fails when a wrapper is given a command.`
      - **TC-03** — partition completeness. `TC-03 — every file under the scanned roots containing
        the evidence contract → member of exactly one of caller / role / excluded-with-reason;
        fails when a file is added to none.`
- [x] **B2** [R9] Run it. It is **red** on TC-01 and TC-02 — no site carries the clause yet.

**Verification:** `python3 -m pytest tests/test_frozen_tree_contract.py` fails, and the failure
names TC-01 and TC-02.

## Cluster C — the source of truth

- [x] **C1** [R1, R2] `skill-parallel-orchestration` §2.4 — add the freeze rule to the orchestrator
      half: no write to the artifacts under review between the spawn and the last return; the writes
      go before or after.
- [x] **C2** [R3, R6] Same section — define the fingerprint by its property, give the `git` form as
      an example with the untracked-content caveat (OQ-1), and state what a mismatch invalidates.
- [x] **C3** [R4] Same section — assign the comparison to the caller and state why: a role with no
      execution tool must not be handed a command, which is the rule the section already carries.
- [x] **C4** [R5] Same section, teammate half — add the bullet: quote the supplied fingerprint,
      report an absent one, do not signal `clean-pass` without it.
- [x] **C5** [R8] Same section — state that the sequential role-switch path has no concurrency and
      the freeze rule is therefore vacuous there, while the line is still written.
- [x] **C6** [R10] Bump `version: 3.8` to `3.9` and add the `## 9. History` entry.

**Verification:** `scan_register.py` over the edited file reports no warn; TC-01 now passes for
file 1 only.

## Cluster D — the readers

- [x] **D1** [R7] Files 2–5 — add the `Tree fingerprint` line to each evidence block template and
      the freeze obligation to each caller-side step.
- [x] **D2** [R7] Files 6–9 — add the freeze obligation and the fingerprint line to the four phase
      gate spawns. The artifact under review there is a document, not a source tree; the rule is
      stated over "the artifacts under review" and needs no restatement.
- [x] **D3** [R5] Files 10–16 — add the quote-it instruction to the seven hand-maintained role
      definitions. `security-auditor` holds Bash, so it carries the caller-side form.
- [x] **D4** [R5] File 17 — add the clause to the three `evidence` fields in
      `wrappers_manifest.json`, then run `generate_wrappers.py` and confirm 12 wrappers changed.

**Verification:** TC-01 and TC-02 pass.

## Cluster E — gates and finalization

- [x] **E1** [A4] Mutation: delete the fingerprint line from `vdd-adversarial.md`, run G1, observe
      red, restore, observe green. Record both outputs under Gates.
- [x] **E2** [A6] `python3 -m pytest tests/` — full suite green.
- [x] **E3** [A6] `generate_wrappers.py --check` — no drift.
- [x] **E4** [A5] `check_positional_refs.py --targets-changed --fix` — clean.
- [x] **E5** [R10] `CHANGELOG.md` and `CHANGELOG.ru.md` — v3.29.0 entry in both.
- [x] **E6** [R10] Close RF-7 in onchain-analytics: frontmatter `status: fixed`, `resolved_at`,
      `resolved_by`, a resolution blockquote appended without editing the body, and the one index
      line in `docs/KNOWN_ISSUES.md` — four edits, not three (decision 102-D6).
- [x] **E7** Fill the Gates table in `docs/reviews/framework-audit-105.md`.

**Verification:** every gate below carries a recorded result.

## Gates

| Gate | Command | Result |
| :--- | :--- | :--- |
| G1 | `python3 -m pytest tests/test_frozen_tree_contract.py` | 7 passed |
| G2 | `python3 -m pytest tests/` | 435 passed, 114 subtests |
| G3 | `generate_wrappers.py --check` | OK, 12 wrappers match the manifest |
| G4 | `scan_register.py`, each edited file against its `.bak` | 0 new warnings |
| G5 | `check_positional_refs.py --targets-changed --fix` | exit 0, 2 repaired, 1 pre-existing error out of scope |
| G6 | three mutations, one per assertion | each reddens a different one |
| G7 | `System/scripts/check_loop_contract.py` | 25 loops, 0 errors |

Full results and the two findings that needed prose — the pre-existing G5 error and the loop-window
regression this task caused and fixed — are in
[`docs/reviews/framework-audit-105.md`](reviews/framework-audit-105.md).

## Rollback

Restore from `.agent/archive/<basename>.bak` for any file whose edit must be undone. The working
tree was clean at start, so `git checkout -- <path>` restores any file that was tracked.
`tests/test_frozen_tree_contract.py` is new and is removed with `rm`.

## Failure handling

| Failure | Action |
| :--- | :--- |
| G1 red after Cluster D | the site set and the test disagree; fix the site, never the assertion |
| G2 red | an unrelated suite broke; restore from backup and re-apply one cluster at a time |
| G3 drift | a generated wrapper was hand-edited; re-run the generator |
| G5 non-zero | a coordinate moved; the resolver repairs it and the repair lands in the same commit |
