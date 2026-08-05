---
id: WI-15
type: work-item
status: done
opened_at: 2026-08-05
slug: wi-15-skill-md-6-has-no-rule-for-narrowing-a-rule
effort: S
value: 'the maintenance triage covers adding coverage and not removing it, so a narrowing proposal has no stated bar to clear'
source: 'WI-13 §7.5, carried out of that record when it was dropped'
provenance: human
component: artifact-formalizer
resolved_at: 2026-08-05
resolved_by: TASK 102
---

# WI-15 — `SKILL.md` §6 has no rule for narrowing a rule

> **Done 2026-08-05 (TASK 102).** `SKILL.md` §6 carries rule 5 with the three items §3 named. The
> section intro now states that rules 1 to 4 govern under-coverage and rule 5 the other direction.
>
> **The record the rule requires is in `measurement-baseline.md` §6.** A third proposal reads it
> there. It holds `task-099` D2 and WI-13 P2 as two rounds of one widening, each with its figures.
> §4 keeps non-rules on record; §6 now keeps this narrowing decision the same way.
>
> **§7.5's second finding shipped too.** §6 now carries a table of which surface narrows which
> register rule, and states that rule 5 alone has no data-file surface. That is the impossible step
> WI-13 §5 named.
>
> **A first draft of that paragraph generalised §7.5 from rule 5 to "rules 1 and 5" and was false.**
> Rule 1's bound is `thresholds.sentence_max_words`, declared in both shipped data files and merged
> over the code default. Measured on two throwaway copies: the data-file edit moves the limit from
> 35 to 100 and the rule-1 finding disappears; the code-`DEFAULTS` edit changes nothing.

Carried out of [WI-13](wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md) §7.5. The gap is
independent of the narrowing WI-13 proposed. It remained open after that record was dropped.

## 1. The gap

`SKILL.md` §6 triages a **new defective phrase found in the wild**. Its four numbered rules all
answer one direction:

| Rule | Answers |
| :--- | :--- |
| 1 | a test already forbids it — add a faster detector |
| 2 | no test reaches it — amend the contract first |
| 3 | every entry ships with a `probe` |
| 4 | a rule ships only when a measurement supports it |

Rules 1 and 2 route **under**-coverage: a defect no test forbids. Rule 4 gates what a rule needs to
**ship**. Nothing states what a proposal to **remove** coverage must show.

## 2. What the missing rule costs

Two events in this repository, both recorded:

- WI-13 §7.5 identified the gap while proposing a narrowing, then routed itself through rule 2 —
  the rule for the opposite direction.
- WI-13 §7.2 records P2 as the same widening `task-099` D2 had already rejected, re-proposed with a
  sample three times smaller than the true blast radius. Verified: 584 findings erased, battery
  `188/191`.

A re-proposal is cheap when nothing states the bar. `measurement-baseline.md` already keeps
non-rules on record so nobody re-proposes them from impression; the narrowing direction has no
equivalent.

## 3. The change

Add a fifth rule to `SKILL.md` §6, stating what a narrowing must produce before it ships:

1. the population it removes, measured over the **declared** scope, with the scope and the commit
   named;
2. the battery result after the change, since a narrowing that turns a case red is a rule the
   battery still wants;
3. the class the narrowed rule keeps, with one occurrence that the narrowed rule still reports.

Point 3 is what WI-13 could not supply: its §8 measured zero occurrences of the keep-class, and
§7.3 showed the class is unreachable where its vocabulary lives.

## 4. Bound

This adds a bar to clear, not a prohibition. `measurement-baseline.md` §4 already drops a rule that
never fires, and a narrowing that meets the three points above is how that gets carried out.
