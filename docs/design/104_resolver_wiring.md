# Design 104 — wiring the reference resolver

**Status:** proposal · **Opens:** TASK 103 OQ-1 · **Precondition:** TASK 103 committed
**Filed as a design note, not as `docs/TASK.md`:** TASK 103 is complete and uncommitted. Rotating
`docs/TASK.md` now would archive 103 before it lands, so this becomes TASK 104 after that commit.

## 1. What is missing

TASK 103 shipped a resolver nobody calls. Measured across `.agent/workflows/`, `System/Agents/` and
every `SKILL.md`: the only file naming `check_positional_refs.py` is `documentation-standards`
itself. The capability exists and no run exercises it.

## 2. The set, derived rather than borrowed

**Criterion.** Wire `W` when T1 or T2 occurs in `W`'s own steps **and** no `calls[] kind: invoke`
edge hands that same work to an already-wired workflow.

| Trigger | Event | Why it invalidates a coordinate |
| :--- | :--- | :--- |
| **T1** | code lands | lines shift under coordinates pointing into the file |
| **T2** | a document carrying coordinates is written | the coordinate can be false at birth |

The `calls[]` graph was read from the frontmatter of all 23 workflows.

**T1 yields nine:** `03-develop-single-task`, `vdd-03-develop`, `vdd-05-run-full-task`, `vdd-multi`,
`vdd-adversarial`, `security-audit`, `framework-upgrade`, `light-02-develop-task`, `heal-issues`.

This set **reproduces WI-16 §5.1 exactly**. That is a check, not a borrowing: the same criterion run
for a different protocol returns the same nine, and the four excluded orchestrators
(`05-run-full-task`, `base-stub-first`, `full-robust`, `vdd-enhanced`) are excluded for the same
transitive reason.

**T2 yields seven more** — `01-start-feature`, `02-plan-implementation`, `vdd-01-start-feature`,
`vdd-02-plan`, `04-update-docs`, `light-01-start-feature`, `iterative-design` — and **none of them
gets a workflow edit.** Every authoring workflow passes its artifact through a reviewer, and all
four reviewer prompts already load `documentation-standards`:

| Prompt | Active skills |
| :--- | :--- |
| `03_task_reviewer_prompt` | `task-review-checklist` + `documentation-standards` |
| `05_architecture_reviewer_prompt` | `architecture-review-checklist` + `documentation-standards` |
| `07_plan_reviewer_prompt` | `plan-review-checklist` + `documentation-standards` |
| `09_code_reviewer_prompt` | `code-review-checklist` + `documentation-standards` |

T2 therefore costs four checklist edits and zero new skill loads.

**Two of T1's nine drop out**, because they already invoke the code reviewer that now carries the
item: `03-develop-single-task` and `light-02-develop-task` (both name `09_code_reviewer_prompt`).
`vdd-03-develop` does **not** invoke it and keeps its own step.

**Exclusions on measurement, not on reasoning.** `product-full-discovery`,
`product-market-only`, `product-quick-vision`: `docs/product/` holds **0** `path:line` references
across onchain-analytics, obsidian-llm-wiki and Universal-skills.

**A git hook was rejected on consistency.** One `--targets-changed --fix` at pre-commit would cover
T1 and T2 at once, but `.git/hooks/` in this repository holds no installed hook, is not versioned,
and installation would fall to the installer (ARCHITECTURE §9). That is a new subsystem — the
inconsistency this plan exists to avoid.

## 3. The eleven files

| # | File | Gets |
| :--- | :--- | :--- |
| 1 | `.agent/skills/task-review-checklist/SKILL.md` | `## 7. References (§4.1)`, scope `docs/TASK.md` |
| 2 | `.agent/skills/plan-review-checklist/SKILL.md` | same, scope `docs/PLAN.md docs/tasks/task-<ID>-*.md` |
| 3 | `.agent/skills/architecture-review-checklist/SKILL.md` | same, scope `docs/ARCHITECTURE.md docs/architectures/` |
| 4 | `.agent/skills/code-review-checklist/SKILL.md` | the T1 item: `--targets-changed`, repaired in THIS commit |
| 5–11 | `vdd-03-develop`, `vdd-05-run-full-task`, `vdd-multi`, `vdd-adversarial`, `security-audit`, `framework-upgrade`, `heal-issues` | one step running `--targets-changed`, `--fix` where the workflow commits |

### 3.1 The checklist item (files 1–3)

```
## 7. References (`documentation-standards` §4.1)
- [ ] **Resolver run:** `check_positional_refs.py --all <scope>` was run and its `path:line`
      coverage line is QUOTED in the review — not asserted to have been run.
- [ ] **Verdicts resolved:** zero `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS`, or each survivor
      carries a written reason. `REFERENT_MOVED` is repaired with `--fix`, never argued.
- [ ] **Not-examined is not a defect:** a coordinate carrying no referent is reported and is NOT
      required to gain one. This review never demands a migration.
- [ ] **Cross-repository coordinates pinned:** a path outside this repository resolves to nothing
      and reports `UNRESOLVABLE`; it carries `@<rev>` naming the revision measured.
```

**The form is copied from the existing `Register (§5.5)` section**, which already puts a
deterministic script inside a judgement checklist and resolves the same way ("zero `warn`, or each
survivor carries a written reason"). No new mechanism is introduced.

**Item 3 is load-bearing.** Without it a reviewer reads `348 without (not examined)` as a failure
and demands referents — the forced migration 103-D1 forbids. It is written as a prohibition on the
reviewer, not a task for the author.

**Item 4 comes from evidence.** All four defects TASK 103's own G5 run found in its own artifacts
were exactly this class.

**File 2 inherits the archive caveat already stated in its Script Contract:** `docs/tasks/` is also
the permanent archive sink, so the bare glob `docs/tasks/*.md` would put every task ever written
under a gate no review can pass.

### 3.2 The workflow step (files 5–11)

One numbered step, at the site named per workflow, running:

```bash
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --targets-changed
```

plus `--fix` in the workflows that commit. **Genre matters:** the resolver is a *gate*, not a Global
Protocol. A Global Protocol takes a two-part reference (prose blockquote + step) in every workflow it
binds; a gate is named in the step that runs it, the way `framework-upgrade` §3.3 names
`skill-spec-validator`. This plan uses the second genre, so it needs no protocol registry entry and
no blockquote.

### 3.3 Site rule against the open WI-16

WI-16 pins its own sites and **fails** if a reference sits elsewhere. Six of files 5–11 are in its
table. The rule: **WI-16's site does not move**; the resolver step goes *after* the State-Claim
Sweep and *before* the Retro. Files 1–4 are checklists WI-16 does not touch — no collision.

## 4. Order

1. **Files 1–4, the checklists.** They cover the largest population (85 of 142 references in the
   measured corpus were written by authoring phases) and touch no workflow.
2. **Files 5–11, the workflow steps.**
3. **The wiring test** (§5).
4. `CHANGELOG.md` + `CHANGELOG.ru.md`, and the ledger record.

Checklists first because they are revertible in isolation and prove the item's wording before it is
duplicated into seven workflows.

## 5. Verification — and one gap this plan closes that WI-16 leaves open

**WI-16 §7 states, of its own nine: "Nothing verifies the wiring."** A workflow authored later is
absent from the set and nothing reports it. That gap is cheap to close here and this plan closes it:

```
tests/test_resolver_wiring.py
  - the eleven files each name check_positional_refs.py
  - the four excluded orchestrators do NOT (they would double-run it)
  - every workflow whose frontmatter has `calls: []` AND which commits is in the set,
    computed from the frontmatter rather than from a literal list
```

The third assertion is the one that matters: it recomputes the criterion instead of restating the
answer, so a workflow added later fails the test rather than being silently uncovered.

**Gates:** `python3 -m pytest tests/ -q` (413 passed today) and
`python3 System/scripts/validate_skills.py --root .` (46/46 today, unchanged — no skill is added).

## 6. Rollback

Eleven tracked files plus one new test, no moves and no deletions: `git checkout --` on the eleven,
`rm` on the test. Back them up to `.agent/archive/` before starting, per `framework-upgrade` §3.1.

## 7. Out of scope

- **Migrating any corpus**, including this repository's six references. Unchanged from 103 D5.
- **A protocol registry with a validator over every terminal workflow.** WI-16 §8 sizes it at L and
  it answers the wiring question for *all* protocols. §5's test covers this one; it does not
  substitute for that item.
- **Product workflows** — excluded on the measurement in §2.
- **A git hook** — §2.
- **`--strict` anywhere.** No consumer opts into gating by this plan; the resolver stays advisory,
  and a project that wants a hard gate names its own living corpus and adds `--strict` itself.

## 8. The honest residual

A checklist item is reviewer judgement, and nothing proves the reviewer ran the command — the same
gap the `Register (§5.5)` section carries today. §3.1's first item mitigates it by demanding the
coverage line be **quoted** rather than claimed, which is the strongest thing a checklist can do
without becoming a CI job. Turning either section into a CI job is one decision for both, not two.
