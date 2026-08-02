# Task 095.5 — Gate-verification rules

<!--
  Anchors below (`<!-- contract:* -->`) are how a MACHINE addresses a section:
  a gate must never key on the heading's words, because those are prose and
  prose has a language. Rule + registry: `documentation-standards` §4.3/§4.4.
-->

## Use Case Connection
- UC-3 (adjacent)
- Covers `R8` — WI-31

<!-- contract:goal -->

## Task Goal
State the boundary between narrowing a command that WRITES and reproducing the invocation of a
command that VERDICTS, plus the two shell facts that make a green verdict unreliable — at a cost
the always-loaded tier does not pay.

<!-- contract:changes -->

## Changes Description
### Changes in Existing Files
- **`developer-guidelines/SKILL.md` §5.1 item 1** — one clause: it governs the WRITING form only.
- **`developer-guidelines/SKILL.md` §6.3 (new)** — three rules: CI-identical invocation for
  verdicts; a pipeline's exit code belongs to its last command; exit 0 is not evidence of work,
  so name the sign of work and quote it. Plus: state the expected sign BEFORE running.
- Two rationalization rows; `version` 1.3 → 1.4.
- **`core-principles`: NOT edited.**

<!-- contract:tests -->

## Test Cases
No unit test — this is prose that binds a role. Its verification is behavioural and appears in
this task's own record: the §0 backup step used `install -D`, which BSD `install` lacks; every
copy failed, `&&` swallowed it, the loop exited 0, and the printed count `0 files` is what caught
it. Rule 3, demonstrated on the first command this plan ran.

<!-- contract:acceptance -->

## Acceptance Criteria
- [ ] `core-principles` line count unchanged at 43 (TASK A5)
- [ ] the three rules live in TIER 1 only
- [ ] §5.1 and §6.3 cross-reference each other rather than restating
- [ ] `validate_skills.py` 45/45

## Notes
**Why the filed options were not taken.** Option 1 put the rules in `core-principles`: 43 lines,
TIER 0, +7% for the minimum form and +23% for the honest one, charged to every session including
roles that never invoke a gate — and shell mechanics are not a principle. Option 2 added
`developer-guidelines` ON TOP, writing one assertion in two skills, which is the WI-32 defect
filed from the same run. Option 3's mechanical form is the one thing here that does not reduce
to discipline, and it belongs to spec 095 Component C — see T-095-08.

**Honest scope limit:** only rule 2 is mechanically enforceable and portable. Rules 1 and 3 stay
discipline wherever the CI command list is not machine-readable — which, downstream, is
everywhere: `System/scripts/installer/*` ships `.agent/` and `System/`, never `.github/`.
