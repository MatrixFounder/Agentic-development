# PLAN 104 — The reference resolver is invoked by the runs that break references

**TASK:** [docs/TASK.md](../tasks/task-104-resolver-wiring.md) · **Covers:** R1–R8 · **Acceptance:** A1–A6

## Sequencing rule

Four clusters. Cluster A writes the wiring test first and leaves it **red** — it is the executable
form of the eleven-file decision, and writing it first is Stub-First applied to a task whose product
is text rather than code: the structure that will hold the edits exists and fails before an edit is
made. Cluster B does the four checklists, which carry the larger population and reach five consumer
repositories by symlink. Cluster C does the seven workflows, which reach none. Cluster D closes the
ledger, both changelogs, and runs every gate.

| Order | Cluster | Files | Covers |
| :--- | :--- | :--- | :--- |
| A | The wiring test, red | `tests/test_resolver_wiring.py` | R6 |
| B | Four review checklists | `{task,plan,architecture,code}-review-checklist/SKILL.md` | R1, R2, R3, R5 |
| C | Seven workflow steps | 7 files under `.agent/workflows/` | R4, R7 |
| D | Ledger, changelogs, gates | `docs/BACKLOG.md`, `docs/backlog/wi-18-*.md`, `CHANGELOG*.md` | R8, A1–A6 |

**Baselines, measured before Cluster A:**

| Gate | Value now |
| :--- | :--- |
| `python3 -m pytest tests/ -q` | 413 passed, 74 subtests |
| `python3 System/scripts/validate_skills.py --root .` | 46/46 passed |
| workflow files in `.agent/workflows/` | 23 |

**Backup.** `mkdir -p .agent/archive`, then copy the four `SKILL.md` files and the seven workflow
files to `.agent/archive/<name>.bak`. Bootstrap files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) are
copied for the workflow's fallback step and are expected to stay byte-identical — this task edits
none of them.

**Rollback.** Thirteen tracked files plus two untracked creations. `git checkout --` on the four
checklists, the seven workflows and the two changelogs; `rm` on `tests/test_resolver_wiring.py` and
`docs/backlog/wi-18-*.md`; `git checkout -- docs/BACKLOG.md`. Reverting the checklists alone leaves
the test red and the ledger claiming work that was undone.

**One property is load-bearing.** R2's clause — a coordinate carrying no referent is **not** a
defect — is the single item preventing this task from becoming a fleet-wide migration demand. The
four checklists are live in five consumer repositories at commit time (104-D6), and a reviewer who
reads `348 without (not examined)` as a failure will demand referents nobody asked for. It is
asserted in Cluster A before any checklist is edited, and re-read in Cluster D.

## Cluster A — the wiring test, deliberately red (R6)

- [x] A1. Create `tests/test_resolver_wiring.py`. Enumerate `.agent/workflows/*.md` **from disk**,
      not from a literal list.
- [x] A2. Declare two sets in the test: `WIRED` (the seven of TASK §2.1) and `EXCLUDED`, a mapping
      from workflow name to a **reason string**. Every excluded workflow carries one; the reasons
      are the four classes TASK §2.1 and R5/R7 name — covered by the code reviewer, delegates to a
      wired workflow, authoring-only (covered by a checklist), or product (measured at zero).
- [x] A3. **The exhaustiveness assertion.** `set(disk) == WIRED | EXCLUDED.keys()`, with the failure
      message naming the workflows in neither. This is the assertion that survives a workflow being
      added; everything else in this file re-states a decision.
- [x] A4. **The delegation assertion.** For every workflow excluded as "delegates to a wired
      workflow", parse its `calls:` frontmatter and assert at least one `kind: invoke` edge to a
      member of `WIRED`. An exclusion of that class is checked, not believed.
- [x] A5. **The wired assertion.** Each of `WIRED` names `check_positional_refs.py`.
- [x] A6. **The no-double-run assertion.** Each of `EXCLUDED` does **not** name it. Written as a
      prohibition over a named set rather than as an absence, because an absence is not checkable.
- [x] A7. **The checklist assertion.** Each of the four `*-review-checklist/SKILL.md` names
      `check_positional_refs.py` **and** contains the literal marker `not a defect`, under a heading
      matching `^## \d+\. References`. Both tokens are named here because this assertion is the
      blast-radius mitigation for five consumer repositories and must not be approximate: a loose
      substring passes on a checklist saying the opposite, and a whole-sentence match breaks on a
      harmless rewording, after which someone relaxes it and the guarantee is gone. Cluster B writes
      exactly these two tokens.
- [x] A8. Run `python3 -m pytest tests/test_resolver_wiring.py -q`. **Expected: red** on A5 and A7
      (nothing is wired yet), green on A3, A4 and A6. Record which assertions fail here at execution
      time; that list is the specification Clusters B and C discharge.

**Why the test precedes the edits.** The eleven-file decision was derived twice and corrected twice
during analysis — once on which workflows invoke the code reviewer, once on how much of the
criterion is machine-derivable. A decision revised that often should be executable before it is
duplicated into eleven files.

## Cluster B — the four review checklists (R1, R2, R3, R5)

- [x] B1. `task-review-checklist` — add `## 7. References (documentation-standards §4.1)` after the
      existing `## 6. Register` section, with the four items of the design note §3.1. Scope
      `docs/TASK.md`.
- [x] B2. `plan-review-checklist` — the same section, scope
      `docs/PLAN.md docs/tasks/task-<ID>-*.md`, **carrying the archive caveat its own Script
      Contract already states**: `docs/tasks/` is the permanent archive sink, so a bare
      `docs/tasks/*.md` would put every task ever written under a gate no review can pass.
- [x] B3. `architecture-review-checklist` — the same section, scope
      `docs/ARCHITECTURE.md docs/architectures/`.
- [x] B4. `code-review-checklist` — the T1 item instead: `--targets-changed` was run and `--fix`
      landed in **this** commit. A coordinate corrected later was false in a commit someone can
      check out.
- [x] B5. Each of B1–B4 states the resolution bar identically to the `Register` section beside it:
      zero `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS`, or each survivor carries a written reason.
- [x] B6. Run `python3 System/scripts/validate_skills.py --root .`. **Expected: 46/46** — no skill is
      added, so a changed count is a defect.
- [x] B7. Run the wiring test. Expected: A7 green, A5 still red.

## Cluster C — the seven workflow steps (R4, R7)

- [x] C1. `vdd-03-develop`, `vdd-05-run-full-task`, `vdd-multi`, `vdd-adversarial`, `security-audit`,
      `framework-upgrade`, `heal-issues` — one numbered step each, running
      `check_positional_refs.py --targets-changed`, plus `--fix` where the workflow commits.
- [x] C2. **Site rule — the step RESERVES WI-16's position, it does not follow it.** WI-16 is
      **open**: none of its sites exists in any workflow file today, so "after the sweep" cannot be
      followed. The rule instead: place the resolver step at exactly the position WI-16's §5.1 table
      specifies for its own site, so that when WI-16 lands it inserts **above** this step without
      moving it. Six of the seven are in that table; `vdd-03-develop` is the seventh and takes the
      same position its table row names. Ordering the two this way is what keeps WI-16's acceptance —
      which fails on a displaced site — from failing because of this task.
- [x] C3. **Genre.** The step names the command, in the shape `framework-upgrade` §3.3 already uses
      for `skill-spec-validator`. No blockquote, no two-part reference: the resolver is a gate, not a
      Global Protocol (104-D1).
- [x] C4. Run the wiring test. **Expected: all green.**

## Cluster D — ledger, changelogs, gates (R8, A1–A6)

- [x] D1. File `WI-18` — `docs/backlog/wi-18-<slug>.md` plus its index line, and close it in the same
      commit with `status: done`, `resolved_at`, `resolved_by: TASK 104`, a resolution blockquote,
      and the index line under `## Closed`. Four elements, not three.
- [x] D2. `CHANGELOG.md` and `CHANGELOG.ru.md` — one entry each, same commit. Version `v3.28.0`,
      with `README.md` / `README.ru.md` badges moved in the same edit.
- [x] D3. Full gates: `python3 -m pytest tests/ -q` (expect 413 + the new file's cases) and
      `python3 System/scripts/validate_skills.py --root .` (expect 46/46).
- [x] D4. **A6's second half — read the shipped checklist text once as a reviewer would**, checking
      that R2's clause reads as a prohibition on the reviewer and not as a task for the author. The
      difference is not machine-checkable and is the whole blast-radius mitigation.
- [x] D5. Update `.agent/sessions/latest.yaml` via `update_state.py`.

### D3 result

```
python3 -m pytest tests/ -q                      → 422 passed, 114 subtests passed   (was 413 + 74)
python3 System/scripts/validate_skills.py --root . → 46/46 passed                     (unchanged)
```

The nine new cases are exactly `tests/test_resolver_wiring.py`; no skill was added, so an unchanged
46/46 is the expected result rather than a coincidence.

**A8's recorded red list**, for the record the plan asked for: at Cluster A the four wiring
assertions failed — `test_each_wired_workflow_names_the_resolver`,
`test_each_checklist_names_the_resolver`, `test_each_checklist_has_a_references_section`,
`test_each_checklist_states_that_a_bare_coordinate_is_not_a_defect` — while all three structural
assertions were green from the start (exhaustive partition, transitive delegation, no-double-run).
That split is the point: the structure was verifiable before a single file was wired.

### D4 result — the reviewer reading

The shipped clause reads as a prohibition on the reviewer, not as work for the author: *"This review
never demands a migration: most corpora carry no referents at all, and adoption is the project's
decision, not the reviewer's."* This is the sentence that keeps four symlinked checklists from
becoming a fleet-wide migration demand, and it is not machine-checkable beyond the `not a defect`
token the test pins.
