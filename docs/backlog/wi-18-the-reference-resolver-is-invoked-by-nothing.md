---
id: WI-18
type: work-item
status: done
opened_at: 2026-08-07
slug: wi-18-the-reference-resolver-is-invoked-by-nothing
effort: M
value: 'TASK 103 shipped a resolver no run exercises; a capability nothing invokes is indistinguishable from an absent one'
source: 'TASK 103 OQ-1, deferred there deliberately'
provenance: human
component: '4 review checklists + 7 workflows + tests/test_resolver_wiring.py'
resolved_at: 2026-08-07
resolved_by: 'TASK 104 — four checklist sections, seven workflow steps, and a wiring test that partitions every workflow file'
---

# WI-18 — The reference resolver is invoked by nothing

> ## Closed 2026-08-07 by TASK 104
>
> Eleven files: four review checklists carry a `References (§4.1)` section, seven workflows run
> `--targets-changed`, and `tests/test_resolver_wiring.py` partitions **every** workflow file on
> disk into wired or excluded-with-a-reason.
>
> **Not shipped, deliberately:** no corpus migrated, no `--strict` anywhere, no git hook, and the
> seven workflow steps do **not** reach consumer repositories — see §4.

## 1. The gap

TASK 103 shipped the referent layer and OQ-1 recorded that nothing called it. Measured at `ed2af74`
across `.agent/workflows/`, `System/Agents/` and every `SKILL.md`: the only file naming
`check_positional_refs.py` was `documentation-standards` itself.

`ARCHITECTURE` §7.2 already states the equivalence this creates — a step the author stopped running
is indistinguishable from a step that passed. A step nobody starts is the same thing earlier.

## 2. Two triggers, where the prior derivation had one

WI-16 §5.1 derived its wiring from a single trigger: code lands. A coordinate has two.

| Trigger | Event | How it falsifies |
| :--- | :--- | :--- |
| T1 | code lands | lines shift under coordinates pointing into the file |
| T2 | a document carrying coordinates is written | the coordinate can be false at birth |

T2 is the larger population: **85 of 142** attributable references in the measured corpus were
written by the Analysis, Architecture and Planning phases.

T1's criterion — code lands **and** no `calls[] kind: invoke` edge hands it to a covered workflow —
returns nine, reproducing WI-16 §5.1 exactly. That was a check on the criterion, not a borrowing.
Two of the nine drop out because they invoke `09_code_reviewer_prompt`, whose checklist now carries
the item: `03-develop-single-task` and `light-02-develop-task`. `vdd-03-develop` does **not** invoke
it and keeps its own step; an earlier draft said otherwise and was wrong.

T2 costs no workflow edit at all. Every authoring workflow passes its artifact to a reviewer, and
all four reviewer prompts already declare `documentation-standards`.

## 3. What the wiring test does that WI-16's does not

WI-16 §7 states of its own nine: "Nothing verifies the wiring."

Only half the criterion is machine-derivable. The delegation half comes out of `calls:` frontmatter
exactly; "code lands here" does not — measured over all 23 workflows, a grep for commit or staging
steps finds them in **two**. A first draft of the requirement claimed the whole criterion was
recomputable; it is not.

What makes the test a verification is **exhaustiveness**, not derivation: it enumerates
`.agent/workflows/*.md` from disk and asserts every file is in exactly one of two sets, one carrying
a reason per member. A workflow added tomorrow is in neither and fails. Exclusions claiming
delegation are additionally checked against `calls:` transitively, so that class is verified rather
than believed.

## 4. What this does not fix

- **The seven workflow steps do not reach consumers.** Measured in onchain-analytics:
  `.agent/skills/` holds 47 per-skill symlinks into this repository, so the **four checklist edits
  are live in five repositories at commit time**; `.agent/workflows/` is a real per-repo directory,
  so the **seven steps reach none**. T2 coverage is fleet-wide, T1 coverage is local until each
  project edits its own workflows. Accepted: the checklist half is advisory and demands nothing of a
  corpus that adopted nothing.
- **A checklist cannot prove its command ran.** The section demands the coverage line be **quoted**,
  which is the strongest thing a checklist can do without becoming a CI job. The
  `Register (§5.5)` section beside it carries the same gap, and turning either into CI is one
  decision for both.
- **The protocol registry with a validator over every terminal workflow** —
  [WI-16](wi-16-state-claims-carry-no-required-referent.md) §8 sizes it at L and it answers the
  wiring question for *all* protocols. This item's test covers one.
- **Semantics**, unchanged from [WI-17](wi-17-positional-references-carry-no-referent.md): a
  referent proves the quoted text is present, not that the sentence about it is true.

## 5. Related

- [WI-17](wi-17-positional-references-carry-no-referent.md) — the capability this item invokes.
- [WI-16](wi-16-state-claims-carry-no-required-referent.md) — **open**, and its sites are not in any
  file yet. The seven steps take the positions its §5.1 table names, placed so WI-16 inserts
  **above** them on landing. Ordering against an absent line was caught in the plan audit; nothing
  WI-16 pins is displaced.
