---
name: architecture-review-checklist
description: Detailed checklist for verifying System Architecture and Data Models.
tier: 1
version: 1.2
---
# Architecture Review Checklist

## 1. TASK Compliance
- [ ] **Coverage:** All Use Cases mapped to components?
- [ ] **Constraints:** All non-functional requirements met?

## 2. Data Model (CRITICAL)
- [ ] **Completeness:** All entities, attributes, relationships defined?
- [ ] **Types:** Correct data types chosen? (e.g., TIMESTAMP vs VARCHAR)
- [ ] **Indexes:** Defined for frequent queries?
- [ ] **Migrations:** Plan for existing data exists?
- [ ] **Business Rules:** Constraints enforced (UNIQUE, NOT NULL)?

## 3. System Design
- [ ] **Simplicity:** Least moving parts? (No overengineering).
- [ ] **Style:** Pattern matches problem (Monolith vs Microservices).
- [ ] **Boundaries:** Clear segregation of duties (SRP).
- [ ] **Document Size:** `docs/ARCHITECTURE.md` is ≤1500 lines, OR is an INDEX (~≤200 lines) with section chunks in `docs/architectures/` and all links resolving.
- [ ] **No Per-Task Drift:** ARCHITECTURE.md is a single living document — no `architecture-NNN-*.md` snapshots, nothing moved into `docs/archives/`.

## 4. Security
- [ ] **Auth:** Authentication & Authorization defined?
- [ ] **Protection:** OWASP Top 10 considered?
- [ ] **Secrets:** No hardcoded keys?

## 5. Scalability & Reliability
- [ ] **Scaling:** Horizontal/Vertical strategy?
- [ ] **Faults:** Error handling, retries, backups?

## 6. Register (`documentation-standards` §5.5)
- [ ] **Scan attached:** `artifact-formalizer/scripts/scan_register.py docs/ARCHITECTURE.md
      --sections` was run; `DETECTORS` shows none dead. In Index Mode append the chunk paths (see
      the Script Contract).
- [ ] **Warns resolved:** zero `warn`, or each survivor carries a written reason.
- [ ] **Terms declared, not assumed:** every noun this document introduces as a term is *defined*
      here. ARCHITECTURE.md is what `--terms` reads downstream, so a metaphor introduced here
      legitimises itself in every task file that follows.

## 7. References (`documentation-standards` §4.1)
- [ ] **Resolver run:** `python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --all docs/ARCHITECTURE.md docs/architectures/`
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
Scope: each figure in a section this change adds or edits. With none, this section is not
examined. The standard is `mermaid-authoring-guidelines`; the evidence comes from the Script
Contract, supplied by the caller.
- [ ] **Lint output read:** the brief carries the figure lint output. Without it, each figure in
      scope is reported *not verified*, and no item below is ticked for it. The review then does
      not return APPROVED, and `has_critical_issues` is true.
- [ ] **Lint clean:** the lint output shows no `error` on a figure in scope. Evidence: the lint
      output.
- [ ] **No negative marker:** no fence in scope ends with a `%% negative:` line. Such a line in a
      project document fails FIG-25 of the skill's review checklist. The lint reports the line as
      MA-NEG-03, an error. It also counts every finding of that fence.
- [ ] **Form and concern:** each figure is the form that Step 0 of the skill selects for its
      information, and it shows one concern. Evidence: the figure and its section text.
- [ ] **Fidelity:** every node, edge, label, note and number traces to a line of this document.
      The figure adds no relation, group, number or writer. Each arrow points the way the text
      states the call. Evidence: the figure and the text.
- [ ] **Rendered:** the render check output shows a pass for each figure in scope. Evidence: that
      output and the renders it names. No render output, or the line `not rendered: <reason>`,
      reports this item *not rendered*: it is not ticked, and the review concludes.
- [ ] **Caption and legend:** a caption sits directly above each fence, and a legend, where the
      skill requires one, directly below it. Each states only what the figure draws. Evidence:
      the document text and the positions the lint output reports.
- [ ] **A figure outside the scope is not a defect.** It is reported as *not examined*; this
      review never demands a redraw of it.

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement; the register scan and the figure
  checks named in the Script Contract are deterministic and are run, not recalled.

## Script Contract
- **Primary Command:** `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py docs/ARCHITECTURE.md --sections`
- **Index Mode only:** when `docs/architectures/` exists (ARCHITECTURE.md was split past 1500
  lines), append the chunks: `... docs/ARCHITECTURE.md docs/architectures/*.md --sections`. Check
  the directory first — `ls -d docs/architectures`. Do **not** pass the glob when the directory is
  absent, which is the default single-file state: bash forwards the unmatched pattern as a literal
  path (exit 3, no findings) and zsh aborts the command before the scanner runs.
- **Outputs:** findings, a `DETECTORS` probe table, a `DIAGNOSTICS` block, and the
  per-section worklist. `--json` for the same content as a document.
- **Failure Semantics:** `0` on any number of findings (advisory); `2` on a broken rule file or a
  dead detector; `3` on unreadable or absent input. A `2` or `3` invalidates the run, not the
  artifact.
- **Figure lint (required):** `python3 .agent/skills/mermaid-authoring-guidelines/scripts/lint_mermaid.py docs/ARCHITECTURE.md`.
  In Index Mode, pass the chunk paths as for the register scan. Exit `0` no `error` finding; `1`
  `error` findings; `2` a broken instrument or a dead rule; `3` usage. A `2` or `3` invalidates
  the run, not the artifact.
- **Render check (optional):** `python3 .agent/skills/mermaid-authoring-guidelines/scripts/render_check.py docs/ARCHITECTURE.md`.
  In Index Mode, pass the chunk paths as well. Exit `0` pass; `1` a figure fails or does not
  parse; `2` not rendered, printed as `not rendered: <reason>`; `3` usage. A brief without render
  output, or with the `not rendered: <reason>` line, is accepted: the review concludes, and the
  render items are not ticked.

## Safety Boundaries
- **Scope:** read-only. A review reads artifacts and runs the read-only commands of the Script
  Contract; it never edits the artifact under review. The render check writes its renders outside
  the repository. Findings go to the review notes, and the authoring role applies them.

## Validation Evidence
- **Primary Evidence:** the register scan named in the Register section, attached to the review
  notes with its `DETECTORS` and `DIAGNOSTICS` blocks intact.
- **Figure Evidence:** the figure lint output, and the render check output or its
  `not rendered: <reason>` line, attached as the caller supplied them.
- **Quality Gate:** no dead detector; zero unresolved `warn`; every checklist item above ticked
  against the artifact under review rather than against the previous revision. A figure item
  reported *not rendered* or *not examined* stays unticked, and the review still concludes. A
  figure reported *not verified* keeps the review from APPROVED.

## Criticality Protocol
Severity is a named value, never a glyph (§5.5 rule 5).
- **BLOCKING:** Data Model error, Security hole, Unmet TASK requirement, dead detector in the
  register scan.
- **MAJOR:** Missing index, Questionable tech choice, Vague interface, Single-file
  `ARCHITECTURE.md` over 1500 lines (needs Index-Mode split), unresolved register `warn`, a figure
  that contradicts its text. A figure lint `error`, a figure that does not render in a version of
  the check pair, and an edge through a node are MAJOR as well (the skill's review checklist §4).
- **MINOR:** Description clarity, typos, figure layout, caption and legend form.
