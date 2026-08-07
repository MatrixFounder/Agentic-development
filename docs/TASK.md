# TASK 104 — The reference resolver is invoked by the runs that break references

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 104 |
| Slug | resolver-wiring |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | TASK 103 OQ-1, deferred there deliberately; design note `docs/design/104_resolver_wiring.md` |
| Depends on | TASK 103 (`ed2af74`) — ships the capability this task invokes |
| Closes | WI-18 (filed by this task) |
| Archive name | `task-104-resolver-wiring.md` |

<!-- contract:problem -->

## 1. Problem

TASK 103 shipped a resolver nobody calls. Measured across `.agent/workflows/`, `System/Agents/` and
every `SKILL.md` at `ed2af74`: the only file naming `check_positional_refs.py` is
`documentation-standards` itself. A capability no run exercises is indistinguishable from an absent
one — and the framework has recorded that equivalence before: `ARCHITECTURE` §7.2 states that a step
the author stopped running is indistinguishable from a step that passed.

**The two events that falsify a coordinate are not the same event, and only one of them was ever
considered.** WI-16 §5.1 derived its wiring from a single trigger — code lands. For a coordinate
there are two:

| Trigger | Event | How it falsifies |
| :--- | :--- | :--- |
| **T1** | code lands | lines shift under coordinates pointing into the file |
| **T2** | a document carrying coordinates is written | the coordinate can be false at birth |

T2 is the larger population. Measured in onchain-analytics at `e95b909`: **85 of 142** attributable
references were written by the Analysis, Architecture and Planning phases.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | The four review checklists carry a `References` section keyed on `documentation-standards` §4.1, in the form the existing `Register` section already uses | Y | A1, A4 |
| R2 | That section states that a coordinate carrying no referent is **not** a defect and that the review never demands a migration | Y | A1 |
| R3 | The section demands the coverage line be **quoted**, not asserted to have been produced | Y | A1 |
| R4 | Seven workflows run the resolver at a named site; the site of the open WI-16's sweep is not displaced | Y | A2, A4 |
| R5 | The two workflows invoking `09_code_reviewer_prompt` gain **no** step — the checklist already covers them | Y | A4 |
| R6 | A test partitions **every** workflow file into wired or excluded-with-a-reason, so a workflow authored later fails it rather than being silently uncovered | Y | A3 |
| R7 | No product workflow is wired | Y | A4 |
| R8 | `docs/BACKLOG.md` + record in lockstep; both changelogs carry the change | Y | A5, A6 |

### 2.1 Sub-features

**R1 — the form is copied, not invented.** `task-review-checklist` §6 and `plan-review-checklist` §4
already put a deterministic script inside a judgement checklist under a
`Register (documentation-standards §5.5)` heading, with a `Script Contract` naming the command and
its scoping caveat. The new section is that section's sibling. No new mechanism, no new skill load:
all four reviewer prompts already declare `documentation-standards` alongside their checklist.

**R2 — the item that prevents this task from becoming a migration mandate.** A reviewer reading
`348 without (not examined)` without this clause demands referents, which is the forced adoption
103-D1 forbids and which would land in four consumer repositories through a symlink. The clause is
addressed to the reviewer as a prohibition, not to the author as work.

**R3 — the strongest thing a checklist can do.** A checklist cannot prove a command ran. Demanding
the coverage line be pasted into the review makes the absence visible; demanding "was run" does not.

**R4 — seven, and why not nine.** T1's criterion — code lands in the workflow **and** no
`calls[] kind: invoke` edge hands that code to an already-wired workflow — returns nine, reproducing
WI-16 §5.1 exactly. Two of the nine drop out under R5. The remaining seven:
`vdd-03-develop`, `vdd-05-run-full-task`, `vdd-multi`, `vdd-adversarial`, `security-audit`,
`framework-upgrade`, `heal-issues`.

**Site rule against the open WI-16.** Its acceptance fails if a reference sits at a site other than
the one its table names. Six of the seven are in that table, so the resolver step goes **after** the
State-Claim Sweep site and **before** the Retro. Nothing WI-16 pins moves.

**R5 — measured, and it corrected an earlier draft.** Only `03-develop-single-task` and
`light-02-develop-task` name `09_code_reviewer_prompt`. `vdd-03-develop` does **not**, and keeps its
own step. An earlier version of this reasoning named `vdd-03-develop` as covered; it was wrong.

**R6 — the gap WI-16 leaves open, closed here for this protocol.** WI-16 §7 states of its own nine:
"Nothing verifies the wiring."

**Only half the criterion is machine-derivable, and the requirement says which half.** The
delegation half comes out of `calls[]` frontmatter exactly. The "code lands here" half does not:
measured over all 23 workflows, a grep for commit or staging steps finds them in **two**
(`light-02-develop-task`, `heal-issues`) — the rest commit implicitly or phrase it differently, so
any text-derived signal would be wrong for 21 of 23. A first draft of this requirement claimed the
whole criterion was recomputable; it is not.

**What makes the test a verification rather than a restatement is exhaustiveness, not derivation.**
The test enumerates `.agent/workflows/*.md` from disk and asserts every file appears in **exactly
one** of two sets: wired, or excluded **with a reason string**. A workflow added tomorrow is in
neither and fails. The delegation half is additionally recomputed from `calls[]`, so an exclusion
justified as "delegates to a wired workflow" is checked rather than believed.

**R7 — excluded on measurement.** `docs/product/` holds **0** `path:line` references across
onchain-analytics, obsidian-llm-wiki and Universal-skills.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a planner writes a coordinate that is wrong at birth.**
*Actor:* Plan Reviewer.
*Main:* the PLAN cites `registry.ts:944`; the reviewer runs the resolver over `docs/PLAN.md` and the
task files, quotes the coverage line, and resolves the one `REFERENT_ABSENT` before the phase
boundary.
*Postcondition:* the coordinate driving a future mutation protocol was read before it was executed.

**UC-2 — a developer shifts lines under documents nobody opened.**
*Actor:* Developer in `vdd-03-develop`.
*Main:* the step runs `--targets-changed --fix`; documents citing the edited sources are re-checked
and their numbers repaired in the same commit.
*Postcondition:* no commit lands with a coordinate the tree contradicts.

**UC-3 — a reviewer meets a corpus that adopted nothing.**
*Actor:* any reviewer in a consumer repository.
*Main:* the coverage line reports most references as not examined; per R2 the reviewer records the
number and demands nothing.
*Postcondition:* the review passes, and the corpus's unverified share is on record.

**UC-4 — a workflow is authored after this task.**
*Actor:* whoever adds it.
*Main:* it lands code, declares `calls: []`, and names no resolver step; R6's test fails and names
it.
*Postcondition:* the set cannot silently rot, which is the failure WI-16 §7 declares for its own.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Fails when |
| :--- | :--- | :--- |
| A1 | All four checklists carry the section with its four items, including R2's and R3's | any checklist lacks it · the not-a-defect clause is absent · an item says "was run" instead of demanding the quoted line |
| A2 | The seven workflows each name the resolver at the site §2.1 states | any of the seven lacks it · any site displaces a WI-16 sweep site |
| A3 | `pytest tests/test_resolver_wiring.py` passes; it enumerates `.agent/workflows/*.md` from disk and partitions every file into wired or excluded-with-a-reason, and recomputes the delegation half from `calls[]` | a workflow file belongs to neither set and the suite stays green · an exclusion carries no reason · a delegation exclusion is believed rather than checked against `calls[]` |
| A4 | `03-develop-single-task`, `light-02-develop-task`, the four orchestrators and the three product workflows name no resolver step | any of the nine gains one |
| A5 | `docs/BACKLOG.md` carries WI-18 in lockstep with its record | index line without record, or the reverse |
| A6 | Both changelogs carry the entry; `pytest tests/ -q` and `validate_skills.py` at their baselines | one changelog edited and not the other · a gate regresses |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — a CI job for both deterministic sections.** Neither the `Register (§5.5)` section nor this
task's `References (§4.1)` section can prove its command ran. Turning either into a CI job is one
decision for both. Out of scope here; a checklist that demands quoted output is what this task
ships.

<!-- contract:decisions -->

## 6. Decisions

**104-D1 — the resolver is wired as a GATE, not as a Global Protocol.** A Global Protocol takes a
two-part reference — prose blockquote plus step — in every workflow it binds; the Retro carries it in
17 of 23. A gate is named in the step that runs it, the way `framework-upgrade` §3.3 names
`skill-spec-validator`. The second genre needs no protocol-registry entry and no blockquote.

**104-D2 — T2 is discharged by four checklists, not by seven more workflow edits.** Every authoring
workflow passes its artifact to a reviewer, and all four reviewer prompts already load
`documentation-standards`. Rejected: adding a step to `01-start-feature`, `02-plan-implementation`,
`vdd-01-start-feature`, `vdd-02-plan`, `04-update-docs`, `light-01-start-feature` and
`iterative-design` — seven edits for coverage four already give.

**104-D3 — no git hook.** One `--targets-changed --fix` at pre-commit would cover T1 and T2 with a
single edit. Rejected: `.git/hooks/` holds no installed hook, is not versioned, and installation
would fall to the installer (ARCHITECTURE §9) — a new subsystem, which is the inconsistency this
task exists to avoid.

**104-D5 — no `System/Docs/` edit, recorded rather than assumed.** `framework-upgrade` §4.2 names
`SKILLS.md` and `WORKFLOWS.md` as a finalization step, so the absence needs a reason. Measured:
`WORKFLOWS.md` describes workflows at summary granularity — a mermaid graph plus one table row per
workflow — and `SKILLS.md`'s rows describe what a skill is for, not which sections it contains. A
step added inside seven workflows and a section added inside four checklists change neither
statement. TASK 103 edited `SKILLS.md` because the skill gained a CLI surface and a normative rule;
this task gives no skill a new capability.

**104-D6 — the two halves reach consumers by different routes, and that is accepted.** Measured in
onchain-analytics: `.agent/skills/` holds 47 per-skill symlinks into this repository —
`task-review-checklist` and `code-review-checklist` among them — while `.agent/workflows/` is a real
per-repo directory. So the **four checklist edits are live in five consumer repositories at commit
time**, and the **seven workflow steps reach none of them**. T2 coverage is fleet-wide, T1 coverage
is local to this repository until each project edits its own workflows. Accepted rather than fixed:
the checklist half is advisory and, by R2, demands nothing of a corpus that adopted nothing; making
the workflow half propagate would mean owning per-repo workflow files, which this framework
deliberately does not.

**104-D4 — the test derives the set; it does not list it.** A literal list passes forever and
answers nothing about a workflow added tomorrow. Recomputing from `calls[]` is what makes A3 a
verification rather than a restatement.

<!-- contract:out-of-scope -->

## 7. Out of scope

- **Migrating any corpus**, including this repository's six references. Unchanged from 103 D5.
- **A protocol registry with a validator over every terminal workflow** — WI-16 §8 sizes it at L and
  it answers the wiring question for *all* protocols. R6's test covers this one and does not
  substitute for that item.
- **`--strict` anywhere.** The resolver stays advisory; a project wanting a hard gate names its own
  living corpus and adds the flag itself.
- **Product workflows** (R7) and **a git hook** (104-D3).
- **Propagating the workflow half to consumers** (104-D6). Five repositories receive the four
  checklist edits by symlink and none of the seven workflow steps. Wiring a consumer's own workflows
  is that project's commit, not this task's.
- **A CI job for the two deterministic checklist sections** (OQ-1).
