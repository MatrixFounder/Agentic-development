---
name: task-review-checklist
description: Detailed checklist for verifying Technical Specifications (TASK).
tier: 1
version: 1.1
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

## 7. References (`documentation-standards` §4.1)
- [ ] **Resolver run:** `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --all docs/TASK.md`
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

## 8. Figures (`documentation-standards` §5.6)
- [ ] **Fidelity:** a figure in `docs/TASK.md` states only what the TASK text states. Each node,
      edge, label and number has a line of the text that states it.
- [ ] **Lint output read:** the brief carries the output of the figure lint in the Script
      Contract, and it holds no `error`. Without it the figure is reported *not verified*: the
      review then approves nothing, and `has_critical_issues` is true. Render output is
      optional; the line `not rendered: <reason>` lets the review conclude and never counts as a
      passed render.
- [ ] **No negative marker:** no figure ends with a `%% negative:` line. Such a line in a project
      document fails FIG-25 of the skill's review checklist. The lint reports the line as
      MA-NEG-03, an error. It also counts every finding of that fence.

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement; the register scan and the figure lint
  named in the Script Contract are deterministic and are run, not recalled.

## Script Contract
- **Primary Command:** `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/TASK.md --sections --terms docs/ARCHITECTURE.md`
- **Outputs:** findings, a `DETECTORS` probe table, a `DIAGNOSTICS` block, and the
  per-section worklist. `--json` for the same content as a document.
- **Failure Semantics:** `0` on any number of findings (advisory); `2` on a broken rule file or a
  dead detector; `3` on unreadable or absent input. A `2` or `3` invalidates the run, not the
  artifact.
- **Figure lint (§8), when `docs/TASK.md` holds a figure:**
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py docs/TASK.md`. Exit
  `0` no `error`; `1` `error` findings; `2` a broken instrument or a dead rule; `3` usage. A `2`
  or `3` leaves the figure *not verified*.
- **Figure render (§8), optional:**
  `python3 .agent/skills/mermaid-authoring-guidelines/scripts/render_check.py docs/TASK.md`. Exit
  `0` pass; `1` a figure fails; `2` not rendered, printed as `not rendered: <reason>`; `3` usage.
  Renders are written outside the repository.

## Safety Boundaries
- **Scope:** read-only. A review reads artifacts and runs the read-only register scan; it never
  edits the artifact under review. Findings go to the review notes, and the authoring role applies
  them. Figure lint and render output reach the review as caller-supplied evidence; renders sit
  outside the repository.

## Validation Evidence
- **Primary Evidence:** the register scan named in the Register section, attached to the review
  notes with its `DETECTORS` and `DIAGNOSTICS` blocks intact.
- **Figure Evidence:** for a TASK that holds a figure, the lint output, and the render output or
  the `not rendered: <reason>` line.
- **Quality Gate:** no dead detector; zero unresolved `warn`; every checklist item above ticked
  against the artifact under review rather than against the previous revision.

## Criticality Protocol
Severity is a named value, never a glyph (§5.5 rule 5).
- **BLOCKING:** Missing UC, contradiction with User Task, unmitigated critical risk, dead detector
  in the register scan.
- **MAJOR:** Incomplete scenarios, vague criteria, term mismatches, unresolved register `warn`, a
  figure lint `error`, a figure that states what the TASK text does not.
- **MINOR:** Typos, phrasing.
