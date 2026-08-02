# Task 095.3 — Templates and prompts emit anchors

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-2: Author writes a new TASK
- Covers `R4`, `R5`

<!-- contract:goal -->

## Task Goal
Make a conforming document carry its anchors without the author having read the rule. A rule that
depends on being remembered is the state this task is leaving.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`skill-planning-format/assets/templates/plan_md_template.md`** — `contract:sequence`,
  `contract:coverage`, plus the explanatory banner.
- **`skill-planning-format/assets/templates/task_md_template.md`** — `contract:goal`,
  `contract:changes`, `contract:tests`, `contract:acceptance`, plus the banner.
- **`System/Agents/02_analyst_prompt.md`** — each of the six TASK sections names its anchor; the
  RTM clause now says the first column is the id and **the column names are prose**.
- **`docs/TASK.md` / `docs/PLAN.md`** — this task's own artifacts emit them (dogfood).

<!-- contract:tests -->

## Test Cases
Verified by construction rather than by a new unit test: every emitted anchor is grepped against
the §4.4 registry. An emitted anchor with no registry row fails that check.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] 6 anchors emitted across the two templates, all registered
- [ ] the analyst prompt names an anchor for each of its six required sections
- [ ] `docs/TASK.md` and `docs/PLAN.md` pass their gates **via the anchor path**
- [ ] `check_prompt_references.py --root .` exit 0

## Notes
Emission only. Nothing is REQUIRED to read these anchors, which is what keeps `R6` true — an
anchor that a gate demanded would break the corpus it governs.
