---
id: WI-17
type: work-item
status: done
opened_at: 2026-08-07
slug: wi-17-positional-references-carry-no-referent
effort: M
value: 'a path:line coordinate is a claim about state that nothing observes going false; 26 of 142 in one consumer corpus were already wrong and no gate reported one'
source: 'onchain-analytics WI-43, owner-routed to this repository 2026-08-07'
provenance: human
component: 'documentation-standards §4.1/§4.2 + check_positional_refs.py + artifact-formalizer authoring contract + System/Docs/SKILLS.md'
resolved_at: 2026-08-07
resolved_by: 'TASK 103 — referent layer in check_positional_refs.py, §4.1 rule, §4.2 corpus split, one licensed-form row, registry row; 115 tests pass (89 before), 46/46 skills validate'
---

# WI-17 — A positional reference carries no referent

> ## Closed 2026-08-07 by TASK 103
>
> The mechanism shipped: a `path:line` reference may carry a **referent** — a symbol or an exact
> substring of the cited line, written as a code span immediately after the coordinate — and
> `check_positional_refs.py` resolves it to one of three verdicts, one of which `--fix` repairs
> without a human. A reference carrying no referent is reported as **not examined**.
>
> **What did NOT ship, deliberately:** no corpus was migrated, including this repository's six
> references, and no workflow invokes the tool. Both are recorded in TASK 103 §7 and OQ-1.

Routed here from onchain-analytics, record
`docs/backlog/wi-43-line-anchored-citations-in-docs-decay-silently.md`, which measured the drift and
named this repository as the place the change belongs — the resolver is a shared artifact reached by
symlink from five consumer repositories.

## 1. The gap

`documentation-standards` §4.1 said "prefer nominal over positional" and
`check_positional_refs.py` resolved the address. Neither reached the case where the address
resolves, is in range, and points at something else entirely.

**Measured in onchain-analytics at `e95b909`** — `git blame` the citing line for the commit that
authored it, `git show <sha>:<target>` for the content it then had, compared against the content now:

| Population | Count |
| :--- | :--- |
| references in the living corpus | 182 |
| of those, resolvable | 142 |
| pointing at content that is not what it was when written | **26** |
| of those 26, reported by the resolver before this change | **0** |

## 2. Why an authoring rule alone was not the answer

`onchain-analytics/docs/architectures/open-questions.md:374@e95b909` carries the rule in prose,
written by its own author: *"re-measure them, or quote the predicate text, whenever this file is
touched."* The same paragraph records that two coordinates had already rotted once. A third has
rotted since — the cited predicate now sits 610 lines further down.

The cause is structural. 85 of the 142 attributable references were written by the Analysis,
Architecture and Planning phases, which run **before** the Development phase edits the files they
cite. §4.1's own mitigation — "positional references are verified LAST" — is unfollowable for a PLAN,
which the pipeline requires to be written FIRST.

## 3. What shipped

| Artefact | Change |
| :--- | :--- |
| `documentation-standards` §4.1 | the referent rule, its two spellings, and why an absent referent is not an error |
| `documentation-standards` §4.2 | three finding kinds; the corpus split — gateable over a **named** living corpus, advisory elsewhere |
| `check_positional_refs.py` | referent detection, `--fix`, `--targets-changed`, `--all` accepting files, the `path:line` coverage line |
| `artifact-formalizer/references/authoring-contract.md` | one licensed-form row, because the Architecture phase does not load `documentation-standards` |
| `System/Docs/SKILLS.md` | the row and note describe the resolver as it now is |
| `docs/ARCHITECTURE.md` §7.2 | the addressing ladder gains the **Positional + referent** rung |

**Adoption costs nothing.** Measured across the 17 repositories carrying `.agent/skills/`: 11 hold
no `path:line` reference at all, and the living corpora hold 324 in total. An unreferenced
coordinate is *not examined*, so no existing document turns red on upgrade.

## 4. What this does not fix

- **Semantics.** A referent proves the quoted text is present, not that the sentence about it is
  true.
- **Wiring.** No workflow invokes the resolver; measured, the only file naming it is
  `documentation-standards`. Binding it to phase boundaries is a separate item, sized at nine
  workflows by [WI-16](wi-16-state-claims-carry-no-required-referent.md) §5.1.
- **The rule's own two halves are ungated.** §4.1 and the authoring-contract row are compared by
  nothing; `check_contract_sync.py` reaches neither. Same situation WI-16 §5.3 recorded.
- **A referent written before its coordinate, or wrapped across two document lines, is not
  examined** (TASK 103 D9). One direction is licensed because a line carrying two references and one
  quotation is otherwise unassignable.
- **Archived documents.** Pointing the tool at them reports true drift that is not a defect: their
  coordinates are correct records of a past state. Sampled in Universal-skills — 2 of 3 referent
  findings sit in archived documents. This is why the gateable scope is a **named** corpus.

## 5. Related

- [WI-16](wi-16-state-claims-carry-no-required-referent.md) — the sibling: a claim about build state
  carrying no required referent. Same word, same defect shape, different population (status markers
  rather than coordinates). Its §4.5 reservation is why this rule extends §4.1 instead of claiming a
  new section number (TASK 103 D8).
- onchain-analytics WI-43 — the source. Its recommendation named Option 1, a shape heuristic;
  measured over the four coordinates the record itself lists, that option catches one. This record
  ships the referent instead, and does not use WI-43's option table.
