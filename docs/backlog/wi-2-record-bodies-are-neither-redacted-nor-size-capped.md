---
id: WI-2
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-2-record-bodies-are-neither-redacted-nor-size-capped
effort: S
value: 'closes a secrets-into-git path and stops SKILL.md overclaiming'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: 3f52bd920ad4e705
finding_ref: fnd-20260730-105028-3f52bd92
---

# WI-2 — Record bodies are neither redacted nor size-capped

> Origin: vdd-multi adversarial review of TASK 091/092 (2026-07-30), `critic-security` S-06.
> **Behaviour change for the owner's review, not a landed fix.**

**Signal.** `file --body-file` content is embedded into a record verbatim with **no redaction and no
size cap**. The sibling capture path does redact and clip (`collect --excerpt-file` runs
`filters.redact` + `clip(excerpt_max_chars)`), so the inconsistency is inside one skill. `--body-file
./.env`, a CI log, or a credentials file copies secrets into a repo-visible record the operator then
commits, and `SKILL.md` §5's "no secrets: excerpts are redacted" does not cover the body.

**Why it matters.** TASK 091 *widened* this: the flat layout capped an inlined body at 300 chars,
while the new default `index+files` layout has no cap at all — an unbounded verbatim sink is now the
normal path. A leaked secret in git history is not fixable by a later edit.

**Generalized.** Any writer that copies operator-supplied file content into a version-controlled
artifact must apply the same redaction and size ceiling as its sibling capture paths; a body being
"the whole point of the record" is not a reason for the ceiling to be absent, only for it to be high.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Run `filters.redact` over the body + configurable cap (e.g. 20 KB), refuse above it | S | a legitimately huge body needs an explicit flag |
| 2 | Redact only, no cap | XS | unbounded records still possible |
| 3 | Warn on likely secrets, write anyway | XS | a warning nobody reads is not a control |
| 4 | Nothing; document that bodies are operator-trusted | — | contradicts §5 as written |

**Recommendation.** Option 1, with the cap generous enough that no honest work-item hits it. Minimum
acceptable: option 2 plus an explicit §5 sentence saying bodies are NOT redacted, so the doc stops
overclaiming.

**Acceptance.** A body containing a token-shaped string lands redacted in the record file, and a body
above the cap is refused with a remediation line naming the cap.

**Related.** `run-feedback` SKILL.md §5 · `filters.redact` · sibling `--excerpt-file` path ·
`docs/reviews/vdd-multi-091-092.md`.
