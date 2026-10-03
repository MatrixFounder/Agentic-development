---
id: WI-21
type: work-item
status: open
opened_at: 2026-10-02
slug: wi-21-redraw-the-framework-figures-under-mermaid-authoring-guidelines
effort: M
value: 'the framework's own documents show the figure standard it ships'
source: 'TASK 108 (mermaid-authoring-guidelines)'
---

# WI-21 — Redraw the framework figures under mermaid-authoring-guidelines

**Signal.** TASK 108 §1 lists seven Mermaid figures in the framework's living documents:
`README.md:240`, `README.ru.md:240`, `System/Docs/PRODUCT_DEVELOPMENT.md:27`,
`System/Docs/WORKFLOWS.md:37`, `:383`, `:406`, and
`.agent/skills/brainstorming/examples/demo_complex.md:68`. Measured on 2026-10-02 in mermaid
10.9.8 and 12.1.0:

- 3 of the 7 draw an edge through a subgraph title;
- `WORKFLOWS.md:37` holds 26 nodes and renders 5:1 wide in 10.9;
- `demo_complex.md:68` has 8 participants, over the sequence budget.

TASK 108 left them unchanged (§9). Its UC-6 redraws a figure only when its section is edited.

The advisory lint sweep of PLAN 108 B5, run on 2026-10-03 with the 87 rules of the shipped lint:

| File | Errors | Warnings | Most frequent |
| :--- | ---: | ---: | :--- |
| `README.md`, `README.ru.md` | 0 each | 9 each | capitalised edge labels (6) |
| `System/Docs/PRODUCT_DEVELOPMENT.md` | 0 | 18 | capitalised edge labels (12) |
| `System/Docs/WORKFLOWS.md` | 2 | 64 | capitalised edge labels (35); 2 figures over the hard budget |
| `brainstorming/examples/demo_complex.md` | 0 | 15 | messages over 24 characters (10) |

**Option.** Run the skill's lint and render check over the seven, redraw each failing figure, and
keep the README pair identical. Effort: one task; no code change.

Later lint changes of TASK 108 move these figures as follows (2026-10-03):

- `brainstorming/examples/demo_complex.md:68` has 8 participants. The hard budget is now 6, so the
  lint reports the error MA-BUDGET-02; 8 participants measure 1650 px, 8.7 px text in the column.
- `docs/presentation/FRAMEWORK_EVOLUTION.md:88` draws `xychart-beta`, now a kind to avoid
  (MA-SYN-04, a warning).
- `System/Docs/WORKFLOWS.md` has 4 subgraph titles over 32 characters (MA-LABEL-01).
