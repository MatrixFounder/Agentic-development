# TASK 105 — A read-only round runs against a frozen tree, and the brief carries its fingerprint

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 105 |
| Slug | frozen-tree-fingerprint |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | RF-7, filed in onchain-analytics: `docs/issues/rf-7-mutation-protocol-and-read-only-roast-run-concurrently-so-the-reviewer-measures-a-tree-that-never-shipped.md` |
| Operator decision | Option 1 (ordering) and Option 3 (fingerprint) of the four the record lists |
| Depends on | TASK 074 (`skill-parallel-orchestration` §2.4, the contract this extends) |
| Closes | RF-7 |
| Archive name | `task-105-frozen-tree-fingerprint.md` |

<!-- contract:problem -->

## 1. Problem

`skill-parallel-orchestration` §2.4 obliges the caller to run what a Bash-less role cannot. It
bounds what the caller runs and when the running starts — "before spawning". It bounds nothing
after the spawn.

Two mandatory obligations therefore share one resource with no order between them.

| Obligation | Assumption about the working tree |
| :--- | :--- |
| A read-only round (`critic-*`, `code-reviewer`, the three phase reviewers) | it does not move while the round reads |
| The evidence half of §2.4, and any fix the caller applies | it moves |

**Measured, onchain-analytics task 013-3, 2026-08-06.** `code-reviewer` read a suite run of
`1 failed | 336 passed` and a `git diff --stat` of `35 ++++` where 90 seconds earlier the same
command printed `38 +`. Both readings came from one uncommitted mutation of the caller's own
(`MUT-A`, a deleted `missingSources` pass-through). The reviewer filed a HIGH finding against the
measurement chain and spent seven additional full suite runs establishing determinism.

**The cost of the catch is not the defect.** Had the reviewer not noticed the discrepancy, it would
have returned a verdict on a tree that was never committed — inside the mutation window, 013-3 had
no `missingSources` pass-through.

**Why §2.4 is the site.** §2.4 is what put the caller at the keyboard during the round: the critic
marked the commands `NOT RUN (no Bash)`, so running them fell to the caller. The section creates the
conflict and states no order for it.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | §2.4 states the freeze rule (defined in §2.1 below) | Y | A1, A3 |
| R2 | §2.4 states where the writes go instead: before the spawn, or after the last return of the round | Y | A1 |
| R3 | §2.4 defines the fingerprint (defined in §2.1 below) | Y | A1, A3 |
| R4 | §2.4 assigns the comparison to the caller and never instructs a role without an execution tool to compute a fingerprint | Y | A1, A2 |
| R5 | A read-only role quotes the fingerprint it was given in its report, and reports an absent one without signalling `clean-pass` | Y | A1, A2, A3 |
| R6 | §2.4 states what a mismatch invalidates (§2.1 below) | Y | A1 |
| R7 | Every caller-side brief in the framework carries a `Tree fingerprint` line beside the existing evidence lines | Y | A3 |
| R8 | The sequential role-switch path states why the freeze rule is vacuous there rather than omitting it | Y | A1, A3 |
| R9 | A test enumerates the site set from disk and fails on a site added later without the clause | Y | A3, A4 |
| R10 | Both changelogs carry the change; RF-7 is closed in its own repository with the four-edit closure | Y | A5, A6 |

### 2.1 Sub-features

**R1 — the freeze rule.** Between the spawn of a round and the return of its last role, the caller
performs no write to the artifacts under review.

Scope of "under review": the files the round was pointed at, plus any file the roles were told to
read. The caller's own scratch output is outside it — writing the round's report, the session-state
file, or a findings file is not a violation. Without this bound the rule forbids the caller from
recording anything while a round runs.

**R3 — the fingerprint is defined by its property, not by one command.** The property: a value that
changes when any artifact under review changes. The caller computes it before the spawn and
recomputes it at the round's return. `git` supplies one instance; a repository-free target supplies
another. The contract states the property and gives the `git` form as an example.

**R6 — what a mismatch invalidates.** Two differing values mean the round measured a state that no
longer exists. Its findings are re-taken against the frozen tree, or the report names the mismatch
and the round does not signal a pass.

**R4 — the comparison sits with the caller because the role cannot execute.** Instructing a role
whose `tools:` line carries no Bash to hash a tree is the exact defect §2.4 already forbids. The
role carries the value; the caller compares. See decision 105-D1.

**R7 — line form.** `Tree fingerprint: <value> (<how it was computed>)`, in the same block as
`Tests:` and `Scan:`, with `NOT COMPUTED (<reason>)` as its honest absence — the same third state
the block already uses.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a roast with no mutation.** The caller computes the fingerprint, spawns the round, waits,
recomputes. The values match, the round's findings stand, and the report carries the value.

**UC-2 — a mutation lands mid-round.** The caller must run a mutation whose result the round needs.
It runs it before the spawn. If it runs one anyway, the recomputation at return differs from the
value the roles quoted, and the round is re-taken.

**UC-3 — a role receives no fingerprint.** The role reports
`tree fingerprint absent — findings are not pinned to a tree state` and does not signal
`clean-pass`. This mirrors the existing treatment of a missing evidence block.

**UC-4 — the sequential role-switch path.** One session runs the personas in order, so no write can
be outstanding while a persona reads. The freeze rule holds by construction; the fingerprint line is
still written, because the persona's report is still a claim about one tree state.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | How it is checked |
| :--- | :--- | :--- |
| A1 | `skill-parallel-orchestration` §2.4 carries the freeze rule, the fingerprint definition, the caller-side comparison, and the sequential exemption | Read the section |
| A2 | No read-only role definition instructs computing a fingerprint; each instructs quoting the supplied one | `tests/test_frozen_tree_contract.py` |
| A3 | Every declared site carries the clause, and an undeclared carrier fails | `tests/test_frozen_tree_contract.py` |
| A4 | Deleting the fingerprint line from any one site turns the test red | Executed mutation, recorded in the plan |
| A5 | `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed --fix` exits clean | Run before staging |
| A6 | The full suite is green and `generate_wrappers.py --check` reports no drift | Run before staging |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — untracked file contents.** The `git` example fingerprint covers `HEAD`, the porcelain
status listing and the tracked diff. An untracked file changes the fingerprint when it appears or
disappears, and not when its contents change. Blocks: nothing — the caveat is written beside the
example. Owner: the operator, if a run ever depends on untracked content.

<!-- contract:decisions -->

## 6. Decisions

**105-D1, 2026-08-11, orchestrator: the role carries the fingerprint, the caller compares it.**
RF-7 option 3 says the critic verifies the fingerprint on entry and on exit. A critic's `tools:`
line has no Bash, so it can compute nothing. The only verification available to it is comparing a
value in its brief against the same value in its brief.

The obligation is therefore split. The caller computes before the spawn and recomputes at the
round's return. The role quotes the value it was given, so the comparison is anchored to what the
role saw.
Rejected: instructing the role to run the hash — it is the instruction §2.4 exists to forbid, and
its measured cost is a 600-second turn.

**105-D2, 2026-08-11, orchestrator: the freeze covers the artifacts under review, not the
repository.** A rule covering every file forbids the caller from writing the round's own report
while the round runs, and would be violated on every conforming run.

**105-D3, 2026-08-11, orchestrator: the sequential path states the exemption rather than
inheriting silence.** The hazard is concurrency, and the sequential path has none. A reader finding
no mention cannot tell an exemption from an omission.

**105-D4, 2026-08-11, orchestrator: the fingerprint line goes in the evidence block, not beside
it.** The block is the one structure every caller already writes and every role already reads, and
§2.4 already defines its absence semantics. A second block would need its own absence rule.

<!-- contract:out-of-scope -->

## 7. Out of scope

- Option 2 of RF-7, isolation in a separate worktree — the record proposes it only if serialization
  becomes expensive, and the cost is not yet measured.
- Option 4, no change.
- A script that computes the fingerprint. The value is one shell pipeline in the example, and
  `skill-safe-commands` already permits its parts.
- Any change to what the evidence block reports about tests or scans.
