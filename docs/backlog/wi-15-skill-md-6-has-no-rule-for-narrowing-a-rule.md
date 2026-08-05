---
id: WI-15
type: work-item
status: open
opened_at: 2026-08-05
slug: wi-15-skill-md-6-has-no-rule-for-narrowing-a-rule
effort: S
value: 'the maintenance triage covers adding coverage and not removing it, so a narrowing proposal has no stated bar to clear'
source: 'WI-13 §7.5, carried out of that record when it was dropped'
provenance: human
component: artifact-formalizer
---

# WI-15 — `SKILL.md` §6 has no rule for narrowing a rule

Carried out of [WI-13](wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot.md) §7.5. The gap is
independent of the narrowing WI-13 proposed, and outlived it.

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
