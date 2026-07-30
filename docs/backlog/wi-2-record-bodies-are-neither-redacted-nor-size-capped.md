---
id: WI-2
type: work-item
status: done
opened_at: 2026-07-30
slug: wi-2-record-bodies-are-neither-redacted-nor-size-capped
effort: S
value: 'closes a secrets-into-git path and stops SKILL.md overclaiming'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: 3f52bd920ad4e705
finding_ref: fnd-20260730-105028-3f52bd92
resolved_at: 2026-07-30
resolved_by: TASK 093
---

# WI-2 — Record bodies are neither redacted nor size-capped

> **✅ DONE 2026-07-30 (TASK 093) — with a documented DEVIATION from this WI's own
> recommendation.** Bodies are now **capped and screened, but never rewritten**:
> `feedback_lib/body.py::guard_body` runs at the single CLI read (`_read_body`), so **both**
> ledgers pass through it and neither can be reached around it. Over `body_max_chars` (new config
> key, default 64000) → refused. Carrying a high-confidence credential shape (`AKIA…`, `sk-…`,
> `gh[pousr]_…`, `xox[baprs]-…`, `Bearer <token>`) → refused, naming the class and the 1-based line
> but **never echoing the match** (the message is printed and journaled, so echoing it would leak
> the secret through the check that caught it).
>
> **Option 1 (redact the body) was deliberately NOT implemented.** Two reasons, both load-bearing:
> ① WI-3's premise — and `known-issues-format`'s contract — is that a record body is preserved
> **verbatim**, because it is the evidence someone re-reads to decide what happened. Redaction is a
> silent rewrite of evidence; refusal is not. ② `filters.redact`'s two loosest rules over-match
> prose: `\b(token|secret|passw\w*|…)\s*[=:]\s*(\S+)` rewrites *"the bypass token: …"* in a
> work-item about the spec-validator gate, and the email rule rewrites any address in any body. A
> false refusal blocks real filing, so those two rules are **excluded** from the screen and only the
> structurally distinctive prefixed shapes are used. For preventing secrets-in-git, refusal is
> strictly **stronger** than masking: the operator must fix the body before anything is written.
>
> An already-masked shape (`sk-[REDACTED]`, `Bearer YOUR_TOKEN_HERE`) still files — a record
> describing this screen contains exactly those, and a screen that refuses its own documentation is
> one nobody keeps enabled (audit 093 Risk 7).
>
> **The doc no longer overclaims either way**: `SKILL.md` §5 now states the two policies separately
> (excerpts rewritten; bodies capped, screened, never rewritten) and names the excluded rules, and
> the same paragraph is in `System/Docs/QUALITY_FEEDBACK_LOOP.md`, `cli_reference.md` and
> `finding_schema.md`. Pinned by 14 tests in `tests/test_wi_tail.py::TestBodyPolicy` +
> `TestBodyPolicyReachesBothLedgers` (both classifications, through the CLI).

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
