---
name: plan-review-checklist
description: Detailed checklist for verifying Development Plans.
tier: 1
version: 1.0
---
# Plan Review Checklist

## 1. Use Case Coverage
- [ ] **Total Coverage:** Every Use Case mapped to >= 1 Task?
- [ ] **Traceability:** Coverage table exists?

## 2. Structure & Formalism
- [ ] **Stub-First:** Every component has specific "Stub" and "Impl" phases/tasks?
- [ ] **Dependencies:** Task order respects dependencies?
- [ ] **Phasing:** Clear stages (Structure -> Logic -> Test)?

## 3. Task Descriptions
- [ ] **Existence:** File exists for every task in `plan.md`?
- [ ] **Naming:** Matches `task-{ID}-{SubID}-{slug}.md`?
- [ ] **Sections:** Contains Goal, Changes, Test Cases, Acceptance Criteria?
- [ ] **Depth:** Specific file paths and method signatures? (Without coding).

- [ ] **Strict Mode:** Usage of `skill-tdd-strict` specified for critical components/bugs?

## 4. Register (`documentation-standards` §5.5)
- [ ] **Scan attached:** `scan_register.py docs/PLAN.md docs/tasks/task-<ID>-*.md --sections
      --terms docs/ARCHITECTURE.md` was run over **every** task file this plan produced, not a
      sample; `DETECTORS` shows none dead. `<ID>` is the Task ID from `docs/TASK.md` section 0.
      Task files carrying an earlier ID are the archive (`skill-archive-task` moves rotated
      documents into the same directory) and are out of this review's scope.
- [ ] **Warns resolved:** zero `warn`, or each survivor carries a written reason.
- [ ] **Reading pass covered:** every section of every task file appears in the worklist and was
      read for rules 3, 4 and 6.

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement; the register scan named in the
  Script Contract is deterministic and is run, not recalled.

## Script Contract
- **Primary Command:** `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/PLAN.md docs/tasks/task-<ID>-*.md --sections --terms docs/ARCHITECTURE.md`
- **Scope:** substitute the current Task ID for `<ID>`; `docs/tasks/` is also the permanent
  archive sink, so the bare glob `docs/tasks/*.md` would put every task ever written under a gate
  that demands zero `warn` — a gate no review can pass and none can fix.
- **Outputs:** findings, a `DETECTORS` probe table, a `DIAGNOSTICS` block, and the
  per-section worklist. `--json` for the same content as a document.
- **Failure Semantics:** `0` on any number of findings (advisory); `2` on a broken rule file or a
  dead detector; `3` on unreadable or absent input. A `2` or `3` invalidates the run, not the
  artifact.

## Safety Boundaries
- **Scope:** read-only. A review reads artifacts and runs the read-only register scan; it never
  edits the artifact under review. Findings go to the review notes, and the authoring role applies
  them.

## Validation Evidence
- **Primary Evidence:** the register scan named in the Register section, attached to the review
  notes with its `DETECTORS` and `DIAGNOSTICS` blocks intact.
- **Quality Gate:** no dead detector; zero unresolved `warn`; every checklist item above ticked
  against the artifact under review rather than against the previous revision.

## Criticality Protocol
Severity is a named value, never a glyph (§5.5 rule 5).
- **BLOCKING:** Missing Use Case, Missing Task File, No "Stub-First" approach, dead detector in the
  register scan.
- **MAJOR:** Missing coverage table, Vague dependencies, unresolved register `warn`.
- **MINOR:** Formatting, missing "Notes".
