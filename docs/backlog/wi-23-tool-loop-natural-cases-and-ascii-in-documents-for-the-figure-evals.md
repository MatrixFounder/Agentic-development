---
id: WI-23
type: work-item
status: open
opened_at: 2026-10-02
slug: wi-23-tool-loop-natural-cases-and-ascii-in-documents-for-the-figure-evals
effort: L
value: 'a measurement of the render-look-fix loop and of figure requests nobody seeded'
source: 'TASK 108 (mermaid-authoring-guidelines)'
---

# WI-23 — Tool-loop variant, natural cases and ASCII in documents for the figure evals

**Signal.** The TASK 108 campaign measures the skill's guidance in tool-less runs, on eleven
seeded cases. Three things stay unmeasured:

- the render-look-fix loop the skill teaches, which needs the render tools in both arms;
- figure requests taken from real documents, keyed by two labellers blind to the arms;
- ASCII figures inside a Markdown document (F1 measures a terminal reply only).

**Option.** `evals/evals-v2.json` with a tool-loop arm pair (same toolkit in both arms, only the
guidance differs), natural cases, and an F3 case for ASCII in a document.
