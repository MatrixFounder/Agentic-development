# Final Full Pipeline Verification Plan

**Goal:** Ensure "Enterprise Quality" by verifying that the refactored Skills-based agents produce outputs equal to or better than the original Monolithic agents.
**Method:** Simulation of a "Secure User Login" task.

## 1. Orchestrator (01)
- [ ] **Routing:** correctly identifies "New Task" vs "Refinement".
- [ ] **Archiving:** correctly triggers `skill-artifact-management` to archive `docs/TZ.md` before starting.
- [ ] **Cycle Management:** Enforces the 2-cycle limit for Analyst/Architect.

## 2. Analysis Phase (02 Analyst + 03 TZ Reviewer)
- [ ] **Analyst:** Uses `skill-requirements-analysis` to generate verbose TZ (Use Cases, A/C).
- [ ] **TZ Reviewer:** Uses `skill-tz-review-checklist` to catch missing edge cases or undefined metrics.
- [ ] **Comparison:** Does the Reviewer still catch "Missing Password Recovery" if it's not in the TZ? (Yes, via "Completeness" check).

## 3. Architecture Phase (04 Architect + 05 Reviewer)
- [ ] **Architect:** Uses `skill-architecture-design` to define Data Model (Entities, SQL types).
- [ ] **Arch Reviewer:** Uses `skill-architecture-review-checklist`.
- [ ] **Critical Check:** Does it enforce **Security** (Salt/Hash) and **Data Model** (Indexes)?

## 4. Planning Phase (06 Planner + 07 Reviewer)
- [ ] **Planner:** Uses `skill-planning-decision-tree` to break down into **Stub** -> **Impl** tasks.
- [ ] **Plan Reviewer:** Uses `skill-plan-review-checklist` to REJECT plans (🔴 Blocking) that miss the "Stub-First" approach.

## 5. Execution Phase (08 Developer + 09 Reviewer)
- [ ] **Developer:** Uses `skill-developer-guidelines` + `skill-documentation-standards`.
- [ ] **Artifacts:** Updates `.AGENTS.md` before coding?
- [ ] **Code Reviewer:** Uses `skill-code-review-checklist`.
- [ ] **Critical Check:** Does it fail code with **LLM Mocks**? Does it fail code with missing **Docstrings**?

## 6. Regression Check
- [ ] Are any instructions lost? (e.g., "Do not nitpick style" in Code Reviewer).
- [ ] Are output formats (JSON) preserved?

## Status
- [ ] Orchestrator
- [ ] Analysis
- [ ] Architecture
- [ ] Planning
- [ ] Execution
