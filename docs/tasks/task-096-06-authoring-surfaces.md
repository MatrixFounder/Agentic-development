# Task 096.6 — Prompts and templates carry the short form


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | four surfaces carry the short block inline | the surfaces POINT at the authoring contract and do not restate the rules | ARCHITECTURE §7.3 |
> | four surfaces | five: three prompts (Analyst, Architect, Planner) and two templates; a third template was added | ARCHITECTURE §7.3 |
> | five rules in each block | the contract holds the rules once; no surface restates them | ARCHITECTURE §7.3 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R9 · **Acceptance:** A7 · **Stage:** 5 of 6 · **Dependencies:** 096.1

<!-- contract:goal -->

## Goal

Put the rules where the authors are. The Analyst and the Planner load neither
`documentation-standards` nor `artifact-formalizer`, so a rule stated only there is a rule that
reaches nobody at the moment an artifact is written.

<!-- contract:changes -->

## Changes

Four surfaces, the same short block in each — five rules, no reasoning, one pointer:

| File | Placement |
| :--- | :--- |
| `System/Agents/02_analyst_prompt.md` | Beside the existing TASK-authoring instructions |
| `System/Agents/06_planner_prompt.md` | Beside the existing PLAN-authoring instructions |
| `.agent/skills/requirements-analysis/assets/task_template.md` | A comment block at the top, beside the anchor note |
| `.agent/skills/skill-planning-format/assets/templates/plan_md_template.md` | Same |

The block:

```markdown
**Register.** Write in whichever language the project uses. In that language:
one claim per sentence (over 35 words is a rewrite signal); no words asserting a
judgment the reader cannot check; justification goes under a **Why.** lead-in,
never inside the requirement clause; state a rule as a rule, not as a maxim;
severity is a named value, never an emoji.
Full guide and scanner: `artifact-formalizer`. Format rules: `documentation-standards` §5.5.
```

`task_md_template.md` already carries the anchor comment block from TASK 095; the register block
sits beside it rather than replacing it.

<!-- contract:tests -->

## Test cases

- **TC-SURF-01** — read all four files. Every one of the five rules is present and correctly
  stated. Grep is a secondary check (audit Mode B, risk 1).
- **TC-SURF-02** — no surface states a rule about which language to use. Each says the opposite.
- **TC-SURF-03** — the anchor block introduced by TASK 095 survives in both templates.
- **TC-SURF-04** — no prompt loses a TIER 0 skill load or any existing instruction.

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] Four surfaces carry the block; verified by reading, not by grep alone
- [ ] The block names the language question and leaves it to the author
- [ ] TASK 095 anchor blocks intact in both templates
- [ ] No existing instruction removed from either prompt
- [ ] The block is under 10 lines in each surface — it competes for the author's attention with
      everything else in the prompt

## Notes

**Why the same text five times rather than a reference.** A prompt that says "see
`documentation-standards` §5.5" relies on the role loading a file its tier table does not give it.
The block is short enough that duplication costs less than the indirection. It is repeated
verbatim so a future edit can find every copy with one search.
