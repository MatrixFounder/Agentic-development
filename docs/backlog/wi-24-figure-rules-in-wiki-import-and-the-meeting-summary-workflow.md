---
id: WI-24
type: work-item
status: open
opened_at: 2026-10-02
slug: wi-24-figure-rules-in-wiki-import-and-the-meeting-summary-workflow
effort: M
value: 'figures written by the wiki and meeting-summary tooling follow the same rules'
source: 'TASK 108 (mermaid-authoring-guidelines)'
---

# WI-24 — Figure rules in wiki-import and the meeting-summary workflow

**Signal.** Two Mermaid authors live outside this repository (TASK 108 research R5, 2026-10-02):

- `obsidian-llm-wiki` `wiki-import --diagrams` writes selective Mermaid figures; its search index
  drops the inside of a fence, so only a caption outside the fence is searchable;
- `Universal-skills/workflows/generate-detailed-meeting-summary.md` asks for 5 to 15 nodes, LR,
  emoji, and white text on fills that fail WCAG AA.

**Option.** Write the rules out inline in both, because a cross-repository reference cannot rely
on a sibling skill being installed: the form ladder, the budgets, top-to-bottom structure, a
caption outside the fence, no theme, contrast. Edits happen in those repositories after the
operator commits TASK 108.
