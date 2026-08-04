---
name: task-review-checklist
description: Detailed checklist for verifying Technical Specifications (TASK).
tier: 1
version: 1.0
---
# TASK Review Checklist

## 1. Task Compliance
- [ ] **Requirements:** All user requirements covered?
- [ ] **Scope:** No unrequested features?
- [ ] **Goal:** Solves the core user problem?

## 2. Completeness (Use Cases)
- [ ] **Structure:** Name, Actors, Preconditions, Main Scenario, Alternatives, Postconditions.
- [ ] **Main Scenario:** Step-by-step, clear system/actor actions.
- [ ] **Alternatives:** Error handling, edge cases (empty inputs, network failures).
- [ ] **Acceptance Criteria:** Specific, measurable, verifiable.

## 3. Compatibility
- [ ] **Terminology:** Uses project terms?
- [ ] **Architecture:** Respects existing constraints?
- [ ] **Integrations:** correctly describes interaction with existing components?

## 4. Consistency
- [ ] **Internal:** No contradictions between UC-01 and UC-02.
- [ ] **Naming:** Same entities named identically.

## 5. Non-Functional
- [ ] **Performance:** Metrics defined?
- [ ] **Security:** Critical checks (auth, inputs)?

## 6. Register (`documentation-standards` §5.5)
- [ ] **Scan attached:** `artifact-formalizer/scripts/scan_register.py docs/TASK.md --sections
      --terms docs/ARCHITECTURE.md` was run, and its `DETECTORS` block shows no dead detector.
- [ ] **Warns resolved:** zero `warn`, or each survivor carries a written reason.
- [ ] **Zero read correctly:** if `DIAGNOSTICS` reports `PRESSED AGAINST THE LIMIT`, the
      `sentence_near_limit` findings were judged rather than ignored.
- [ ] **Reading pass covered:** every section in the `--sections` worklist was read for rules 3, 4
      and 6, not only the sections carrying findings.

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement; the register scan named in the
  Script Contract is deterministic and is run, not recalled.

## Script Contract
- **Primary Command:** `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md`
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
- **BLOCKING:** Missing UC, contradiction with User Task, unmitigated critical risk, dead detector
  in the register scan.
- **MAJOR:** Incomplete scenarios, vague criteria, term mismatches, unresolved register `warn`.
- **MINOR:** Typos, phrasing.
