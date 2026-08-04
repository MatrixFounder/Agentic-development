---
name: architecture-review-checklist
description: Detailed checklist for verifying System Architecture and Data Models.
tier: 1
version: 1.1
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

## Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the checklist items are reviewer judgement; the register scan named in the
  Script Contract is deterministic and is run, not recalled.

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
- **BLOCKING:** Data Model error, Security hole, Unmet TASK requirement, dead detector in the
  register scan.
- **MAJOR:** Missing index, Questionable tech choice, Vague interface, Single-file
  `ARCHITECTURE.md` over 1500 lines (needs Index-Mode split), unresolved register `warn`.
- **MINOR:** Description clarity, typos.
