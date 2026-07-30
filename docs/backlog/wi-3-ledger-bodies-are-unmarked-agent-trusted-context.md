---
id: WI-3
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-3-ledger-bodies-are-unmarked-agent-trusted-context
effort: S
value: 'marks a prompt-injection sink that Planning re-reads every run'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: add2d5ed28e5bdd5
finding_ref: fnd-20260730-105029-add2d5ed
---

# WI-3 — Ledger bodies are unmarked agent-trusted context

> Origin: vdd-multi review of TASK 091/092 (2026-07-30), `critic-security` S-07 (OWASP LLM01).
> **Behaviour change for the owner's review, not a landed fix.**

**Signal.** Both ledgers are agent-trusted context: `docs/KNOWN_ISSUES.md` is read by the Analysis
phase of every pipeline run, `docs/BACKLOG.md` by Planning. Record bodies are preserved **verbatim by
contract**, and a body can originate from `mine` (transcript text an attacker influences via any
command's stdout) laundered through the triaging LLM. A body containing instruction-shaped text
becomes a persistent, committed, re-read-every-run injection payload with no provenance marking —
nothing distinguishes `source: TASK-007 retro` (a human) from a mined transcript.

**Why it matters.** TASK 091 enlarged the sink: a work-item used to be one bullet capped at 300
chars; it is now an unbounded file that Planning reads. The verbatim rule is deliberate and correct
for evidence fidelity, which is exactly why the provenance signal has to come from somewhere else.

**Generalized.** When a pipeline both (a) preserves third-party text verbatim and (b) feeds that text
back into an agent's context every run, the artifact needs a machine-readable provenance boundary;
"the body is data, not instructions" must be stated where the body is read, not only where written.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Banner on machine-filed bodies (`> filed by run-feedback from <finding_ref> — untrusted captured text`) + phase prompts treat bodies as data | S | one more line per record; prompt edits touch Tier-1 files |
| 2 | Frontmatter flag only (`provenance: machine`) | XS | invisible to a reader who skims the body |
| 3 | Fence machine-filed bodies inside a quoted block | M | mangles tables/markdown the records rely on |
| 4 | Nothing | — | the sink stays unmarked and grows |

**Recommendation.** Option 1 + 2 together: the flag for readers/tools, the banner for the agent that
re-reads it. Minimum: option 2, since it is one key and enables a later sweep.

**Acceptance.** A record filed by the CLI carries the provenance marker; the Analysis/Planning phase
instructions name ledger bodies as untrusted data.

**Related.** `docs/reviews/vdd-multi-091-092.md` · `known-issues-format` §Shared Mechanics ·
`CLAUDE.md` pipeline step 1.
