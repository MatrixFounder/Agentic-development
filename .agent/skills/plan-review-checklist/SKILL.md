---
name: plan-review-checklist
description: Detailed checklist for verifying Development Plans.
tier: 1
version: 1.2
---
# Plan Review Checklist

## 1. Use Case Coverage
- [ ] **Total Coverage:** Every Use Case mapped to >= 1 Task?
- [ ] **Traceability:** Coverage table exists?

## 2. Structure & Formalism
- [ ] **Stub-First:** Every component has specific "Stub" and "Impl" phases/tasks?
- [ ] **Dependencies:** Task order respects dependencies?
- [ ] **Disjoint scope:** No task's "Changes" list is a subset of another task's — the same file
  and the same function or route owned twice means one of the two closes with no code. Seen
  once: a "sessions, CSRF, login limits" task duplicated the auth-logic task that preceded it in
  the dependency graph and was closed as already delivered.
- [ ] **Phasing:** Clear stages (Structure -> Logic -> Test)?

## 3. Task Descriptions
- [ ] **Existence:** File exists for every task in `plan.md`?
- [ ] **Naming:** Matches `task-{ID}-{SubID}-{slug}.md`?
- [ ] **Sections:** Contains Goal, Changes, Test Cases, Acceptance Criteria?
- [ ] **Depth:** Specific file paths and method signatures? (Without coding).

- [ ] **Strict Mode:** Usage of `tdd-strict` specified for critical components/bugs?

## 4. Register (`documentation-standards` §5.5)
- [ ] **Scan attached:** `scan_register.py docs/PLAN.md docs/tasks/task-<ID>-*.md --sections
      --terms docs/ARCHITECTURE.md` was run over **every** task file this plan produced, not a
      sample; `DETECTORS` shows none dead. `<ID>` is the Task ID from `docs/TASK.md` section 0.
      Task files carrying an earlier ID are the archive (`skill-archive-task` moves rotated
      documents into the same directory) and are out of this review's scope.
- [ ] **Warns resolved:** zero `warn`, or each survivor carries a written reason.
- [ ] **Reading pass covered:** every section of every task file appears in the worklist and was
      read for rules 3, 4 and 6.

## 5. References (`documentation-standards` §4.1)
- [ ] **Resolver run:** `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --all docs/PLAN.md docs/tasks/task-<ID>-*.md`
      was run, and its `path:line` coverage line is **quoted** in the review — not asserted to
      have been produced. A checklist cannot prove a command ran; pasted output can.
- [ ] **Verdicts resolved:** zero `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS`, or each survivor
      carries a written reason. `REFERENT_MOVED` is repaired by re-running with `--fix`, never
      argued about — the number is derived from the referent, so no judgement is involved.
- [ ] **A coordinate carrying no referent is not a defect.** It is reported as *not examined* and
      is **NOT** required to gain one. This review never demands a migration: most corpora carry
      no referents at all, and adoption is the project's decision, not the reviewer's.
- [ ] **Cross-repository coordinates pinned:** a path outside this repository resolves to nothing
      and reports `UNRESOLVABLE`. It carries `@<rev>` naming the revision measured, which is the
      form §4.1 already licenses for a claim about another state.
> **Scope caveat, the same one this checklist's Script Contract states for the register scan.**
> `docs/tasks/` is also the permanent archive sink, so the bare glob `docs/tasks/*.md` would put
> every task ever written under this section. Substitute the current Task ID for `<ID>`.

## 6. Figures (`documentation-standards` §5.6)
The standard is `mermaid-authoring-guidelines`. The caller runs the Script Contract commands of this
section, and the brief carries their output. Without the `plan_gantt.py --check` output, the items
**Schedule valid** and **Chart current** are reported *not verified*. The review then does not
return APPROVED, and `has_critical_issues` is true.
- [ ] **Schedule block:** `docs/PLAN.md` holds one `json` fence directly under
      `<!-- contract:schedule -->`. It lists every task of the sequence once, with the `id` of its
      record and the record's dependencies as `deps`.
- [ ] **Schedule valid:** the `plan_gantt.py --check` output names no cycle, unknown dependency,
      duplicate id or non-integer estimate.
- [ ] **Chart current:** a plan of 8 or more tasks holds the generated chart, or one chart per
      stage group, between `<!-- generated:plan-gantt-start -->` and
      `<!-- generated:plan-gantt-end -->`, and the check output shows exit `0`. A plan of fewer
      than 8 tasks holds no chart there (`skill-planning-format` §2.1).
- [ ] **Skill absent:** a project without `.agent/skills/mermaid-authoring-guidelines/` gets no
      plan chart, and the check cannot run. When the `figures` field of the planner's return JSON
      states `skill absent`, the absent chart is not a defect. **Schedule valid** and **Chart
      current** are then reported *not examined*.
- [ ] **Other figures:** each other figure in `docs/PLAN.md` or a task file of this plan comes with
      lint output that holds no `error`. Without it the figure is reported *not verified*. The
      review then does not return APPROVED, and `has_critical_issues` is true. Render output is
      optional; the line `not rendered: <reason>` lets the review conclude and never counts as a
      passed render.
- [ ] **No negative marker:** no figure in `docs/PLAN.md` or a task file of this plan ends with a
      `%% negative:` line. Such a line in a project document fails FIG-25 of the skill's review
      checklist. The lint reports the line as MA-NEG-03, an error. It also counts every finding of
      that fence.
- [ ] **A figure this plan does not add or edit is not a defect.** It is reported as *not
      examined*, and this review never demands a redraw of it.

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement. The commands of the Script Contract
  are deterministic and are run, not recalled.

## Script Contract
- **Primary Command:** `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/PLAN.md docs/tasks/task-<ID>-*.md --sections --terms docs/ARCHITECTURE.md`
- **Scope:** substitute the current Task ID for `<ID>`. `docs/tasks/` is also the permanent
  archive sink. The bare glob `docs/tasks/*.md` would put every task ever written under a gate
  that demands zero `warn`. No review can pass that gate, and none can fix it.
- **Outputs:** findings, a `DETECTORS` probe table, a `DIAGNOSTICS` block, and the
  per-section worklist. `--json` for the same content as a document.
- **Failure Semantics:** `0` on any number of findings (advisory); `2` on a broken rule file or a
  dead detector; `3` on unreadable or absent input. A `2` or `3` invalidates the run, not the
  artifact.
- **Plan chart check (§6):**
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/plan_gantt.py docs/PLAN.md --check docs/PLAN.md`.
  Exit `0` the schedule block is valid and the chart is current; `1` a stale chart or an invalid
  block, and the message names which; `2` a broken instrument; `3` usage. A `2` or `3` leaves the
  items that read this output *not verified*.
- **Figure lint (§6), once per file of this plan with a figure outside the generated region:**
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py <file>`. Exit `0` no
  `error`; `1` `error` findings; `2` a broken instrument or a dead rule; `3` usage. A `2` or `3`
  leaves the figure *not verified*.
- **Figure render (§6), optional:**
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/render_check.py <file>`. Exit `0`
  pass; `1` a figure fails; `2` not rendered, printed as `not rendered: <reason>`; `3` usage.
  Renders are written outside the repository.

## Safety Boundaries
- **Scope:** read-only. A review reads artifacts and runs the read-only register scan; it never
  edits the artifact under review. Findings go to the review notes, and the authoring role applies
  them. The plan chart check, figure lint and render output reach the review as caller-supplied
  evidence; renders sit outside the repository.

## Validation Evidence
- **Primary Evidence:** the register scan named in the Register section, attached to the review
  notes with its `DETECTORS` and `DIAGNOSTICS` blocks intact.
- **Figure Evidence:** the `plan_gantt.py --check` output; for a file that holds another figure,
  the lint output, and the render output or the `not rendered: <reason>` line.
- **Quality Gate:** no dead detector; zero unresolved `warn`; every checklist item above ticked
  against the artifact under review rather than against the previous revision. An item reported
  *not examined* stays unticked, and the review still concludes. An item or a figure reported
  *not verified* keeps the review from APPROVED.

## Criticality Protocol
Severity is a named value, never a glyph (§5.5 rule 5).
- **BLOCKING:** Missing Use Case, Missing Task File, No "Stub-First" approach, dead detector in the
  register scan.
- **MAJOR:** Missing coverage table, Vague dependencies, unresolved register `warn`. Figures: an
  absent, incomplete or invalid schedule block; an absent or stale plan chart, except in a project
  without the skill (§6 **Skill absent**); a figure lint `error`; a figure that contradicts its
  text.
- **MINOR:** Formatting, missing "Notes", figure layout, caption and legend form.
