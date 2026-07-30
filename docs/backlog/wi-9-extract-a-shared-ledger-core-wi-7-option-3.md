---
id: WI-9
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-9-extract-a-shared-ledger-core-wi-7-option-3
effort: L
value: 'removes the writer-asymmetry class by construction'
source: 'vdd-multi iteration 3'
provenance: machine
component: run-feedback
fingerprint: 2a2dca572340d70c
finding_ref: fnd-20260730-140047-2a2dca57
---

# WI-9 — Extract a shared ledger_core (WI-7 option 3)

> Filed by `run-feedback` from capture `fnd-20260730-140047-2a2dca57`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

> Origin: vdd-multi iteration 3 (2026-07-30). This is WI-7's **option 3**, promoted from "when a
> third registry appears" to "the evidence is now overwhelming".

**Signal.** `ledger_issues` and `ledger_backlog` implement ONE contract in two modules. Every
adversarial iteration over this code has found at least one guard present on one writer and absent
on its twin — three for three:

| iteration | the asymmetry it found |
|---|---|
| WI-23 (origin) | the work-item path wrote only an index line; the defect path wrote record + pointer in lockstep |
| 2 | V12 — the CRLF/reader-break fix landed only in `ledger_backlog` |
| 3 | L-1 CRLF in the new-category branch · L-2 **no fence awareness at all** in `ledger_issues` · L-4 `OSError`-only rollback · L-5 the body gate in neither writer · L-6 no id-uniqueness guard · H-04 containment on one of two `resolve` branches |

**Why it matters.** TASK 093 was *specifically about* this class and produced six more instances of
it while fixing it. The remedy applied so far is the right one but partial: `markdown.py`,
`ids.assert_id_free`, `atomic.read_verbatim` and `body.guard_config_body` are now single
implementations both writers consume. What remains duplicated is the **write choreography** —
lexists pre-check, id allocation, `O_EXCL|O_NOFOLLOW` create, rollback semantics, dry-run payload
shape, seeding-when-absent, index insertion — roughly 120 near-parallel lines per module that a
reader must diff by eye to notice a divergence.

**Generalized.** Two implementations of one contract diverge at the rate someone edits them. Sharing
the *mechanisms* (done) lowers that rate; sharing the *choreography* is what removes the class. Three
iterations of evidence is enough to stop treating each instance as a separate bug.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Extract `feedback_lib/ledger_core.py`: one `file_record()` taking a registry descriptor (contract keys, vocab, record dir, index inserter, link builder); both modules become thin descriptors | L | biggest blast radius in the skill; touches two live registries consumed by symlink in three repos, so it needs its own TASK and a full gate sweep |
| 2 | Keep extracting mechanism-by-mechanism as each divergence is found | S each | what is happening now; converges slowly and only where someone looks |
| 3 | Accept the duplication and add a review checklist item "diff the two ledgers" | XS | a human check against a class that has already defeated three reviews |

**Recommendation.** Option 1, as its own TASK with `skill-self-improvement-verificator` run **before**
execution. The precondition is now met: after iteration 3 the shared primitives exist, so the
extraction is mostly moving choreography rather than inventing abstractions.

**Acceptance.** One write path, exercised by the existing both-ledgers parameterized tests with no
per-registry duplication left in the test file either; `check_contract_sync.py` still green; every
guard from iterations 1-3 provably present for both registries by construction rather than by review.
