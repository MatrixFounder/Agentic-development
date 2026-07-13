# Advanced Eval Patterns

**Load this reference when:** a skill is high-stakes (a gate, a verifier, a
fact-checker, anything where a wrong PASS is costly), its output is **structured**
(JSON / numbers / file shape), or you are about to claim a measured improvement and
want it to be *defensible* rather than a one-run headline.

The base workflow (`SKILL.md` §3–§4, `agents/grader.md`) covers the common case:
realistic prompts, an LLM-judge grader, `with_skill` vs `baseline`, a viewer. This
file collects the **production-grade** practices that go beyond that — distilled from a
real eval campaign on a 4-critic verifier skill.

> **Full tutorial (with diagrams, worked token math, glossary):**
> `docs/Manuals/skill-evals_guide.md` (EN) / `.ru.md` (RU) in this repo.

---

## When to reach for these

| Situation | Pattern(s) |
|---|---|
| Skill output is JSON / structured | Deterministic script-grader (§1) |
| Skill shares a PASS/FAIL rule with production | Call the gate, don't copy it (§2) |
| Numbers must not silently drift between commits | Reproducibility pinning (§3) |
| Behaviour/contract evolves over time | Versioned eval files (§4) |
| You only have a few hand-made cases | Diversify — beware the "mirage" (§5) |
| Skill could over-fire (false positives) | Negative checks (§6) |
| You changed one component and want its true effect | A/B single-variable isolation (§7) |
| A metric jitters run-to-run | Multi-rep + interval (§8) |
| You found a "defect" — should you fix it? | Know when NOT to fix (§9) |

---

## 1. Deterministic script-grader (for structured output)

The default grader is an LLM judge — flexible, but itself non-deterministic. **If the
skill's output is structured** (JSON, numbers, a file shape), write the grader as a
**pure function in code**: no LLM, no network, no DB, no `eval`/`exec`/shell.

Top-level shape — **3 inputs → per-case checks → aggregate**:

```
inputs:  (a) expected results (from evals.json: expected items, forbidden items, expected verdict)
         (b) the skill's raw output (structured)
         (c) the production "gate" function — IMPORTED, not reimplemented (see §2)
per case: match output→expectations  →  recall  →  exactness (e.g. severity)  →
          any structural-purity rule  →  verdict parity (CALL the gate)  →  false positives
output:  grading.json (rates + counts), fully reproducible
```

Payoff: zero grader tokens, and the same inputs always produce the same report —
which is what makes §3 (pinning) possible.

## 2. Call the production gate — never copy it

If the eval decides PASS/FAIL using the same rule as production, the grader must
**import and call the production function**, not re-implement the logic locally.
Re-implementations *drift*: production gets fixed, the eval keeps grading against the
old rule and lies green. One import line removes a whole class of false confidence.

## 3. Reproducibility pinning

Commit the **raw run outputs** alongside `evals.json`, and add a CI test asserting
`grade(evals, raw_outputs) == committed grading.json`. Now any accidental change to
the grader flips the test instead of silently moving the headline numbers.

In skill-creator this is generic: `scripts/verify_pin.py <benchmark_dir> <committed
benchmark.json>` re-aggregates the committed `grading.json` files and exits non-zero if
the computed metrics drift (volatile metadata ignored). Wire it into CI.

## 4. Versioned eval sets as separate files

When the skill's contract grows, add a **new** eval file (`evals-v2.json`,
`evals-v3.json`) rather than mutating the old one. Old files keep guarding old
behaviour byte-for-byte (their pinned baselines stay valid); new files cover the new
requirement. Record skill version + file checksums in the report for a full audit
trail.

## 5. Diversify the set — the "mirage"

**A small or homogeneous eval set gives false confidence.** An improvement measured on
a handful of similar cases routinely shrinks — and sometimes inverts — on a diverse
set, which *also* surfaces regressions the narrow set could never show.

Real example: a prompt change scored "−70%" on a 7-case toy set; on 32 diverse cases
the same change was only ≈ −26% **and** exposed two genuine regressions. Honest
reporting reframes "−70% (one toy run)" as "−58% cumulative over several validated
iterations, plus two real bugs found." Spread cases across domains and construction
types (§6) before trusting any delta.

## 6. Negative checks + construction validity

- **Negative checks**: encode what must **not** happen (a "forbidden finding" / a
  `should_trigger: false` query). Positive-only sets measure recall and are blind to
  over-firing (false positives).
- **seeded vs natural cases**: *seeded* = a defect mechanically planted, so ground-truth
  is objective by construction (zero author bias). *natural* = a realistic case whose
  ground-truth is the **consensus of two independent labelers blind to the prompt**.
  Mixing both removes author bias and doubles as a realistic false-positive guard.

## 7. A/B single-variable isolation

To measure the effect of one change, **change exactly one thing** and hold everything
else fixed — including, for multi-component skills, re-running only the component you
edited while reusing the committed outputs of the others. Then 100% of the metric delta
is attributable to your change, not to noise from untouched parts.

## 8. Multi-rep + interval for noisy metrics

LLMs are non-deterministic, so some metrics jitter. For those, a single before/after
draw proves nothing. Run **N independent samples per arm** (e.g. 5), compare **means**,
and report a **confidence interval** (bootstrap is fine). State the conclusion honestly:
"a downward shift in expectation," not "a guaranteed per-run improvement." Define a
**noise floor** (e.g. ±1) below which a movement is not attributed to the change.

In skill-creator, run the eval set multiple times per configuration, then
`aggregate_benchmark.py --bootstrap` attaches a **seeded** (deterministic, pinnable) 95%
CI on the pass-rate delta between the two configurations.

## 9. Know when NOT to fix

A measured "defect" that **by construction cannot change the verdict** (e.g. a metric on
a component that never moves the PASS/FAIL gate), or that sits inside the noise floor, is
usually not worth fixing — the fix adds work and risk (and may re-pin every committed
report) for no behavioural gain. Document the decision instead of acting on reflex. If
the measurement shows no problem, don't invent work.

---

## Effort & tokens (rough planning anchors)

- A behavioural-eval **iteration** on a small set ≈ a few million tokens (executor runs
  dominate; one full run ≈ 85k tokens). Budget **2–3 iterations**.
- A **deterministic script-grader costs ~0 tokens** to grade — the single biggest saving
  on large sets, and it buys reproducibility.
- Trigger/description optimization is **an order of magnitude cheaper** than behavioural
  evals (short runs).
- Pick the tier to the stakes: **minimal** (2–3 prompts, 1 iteration) → **standard**
  (5–10 cases, with/without, 2–3 iterations) → **rigorous** (20+ cases, seeded+natural,
  A/B, multi-rep, script-grader + pinning) for gates where a wrong PASS is expensive.

See `docs/Manuals/skill-evals_guide.md` for the full worked numbers and diagrams.
