---
name: documentation-standards
description: Standards for code documentation, comments, and artifact updates.
tier: 1
version: 1.5
---
# Documentation Standards

**Purpose**: Defines the non-negotiable standards for code comments, docstrings, and global artifacts.

## 1. Red Flags (Anti-Rationalization)
**STOP if you are thinking:**
- "I'll add comments later" -> **WRONG**. Undocumented code is technical debt from the moment it is written.
- "The code is self-documenting" -> **WRONG**. Code explains *how*; comments explain *why*.
- "Artifacts are optional, I can skip them entirely" -> **WRONG**. Artifacts are part of delivery quality; `.AGENTS.md` must follow project memory policy.
- "I'll put the full explanation in the table cell" -> **WRONG**. A table is a scanning
  device. Prose inside a cell destroys scanning and makes every row of that table churn
  on any edit. Cell = label; explanation goes below the table.
- "It's all one topic, so it's one paragraph" -> **WRONG**. Topic is not structure.
  A reader needs entry points: paragraphs, lists, headings. A 30-line block has none.
- "Line length doesn't matter, editors soft-wrap" -> **WRONG**. `git diff` and review
  comments are line-granular. A 2000-character line means a one-word fix shows up as a
  whole-paragraph rewrite, and reviewers stop reading.

## 2. Docstrings & JSDoc
All classes and functions MUST have documentation.

### Python
Use Google-style docstrings.
> [!TIP]
> See `assets/templates/python_docstring.py` for the format.

### JavaScript / TypeScript
Use JSDoc standards.
> [!TIP]
> See `assets/templates/jsdoc_template.ts` for the format.

## 3. Comments
- **Why vs What**: Explain the *reason* for logic, not the syntax.
- **Work Tracking**: Use `# T O D O:` (Python) or `// T O D O:` (JS/TS) for future work.

## 4. Path & Reference Standards (CRITICAL)
- **Relative Paths Only**: When linking to internal files in Artifacts (PLAN.md, TASK.md), ALWAYS use relative paths.
    - ✅ `[Ref](src/main.py)`
    - ✅ `[.agent/skills/core.md](.agent/skills/core.md)`
    - ❌ `file:///Users/username/project/src/main.py`
    - ❌ `/Absolute/System/Path`

### 4.1. Positional references are verified LAST

A reference is **positional** when it points at *where* something sits rather than *what* it is
called: a line number, a byte offset, an item number in a numbered list, a section ordinal. A
reference is **nominal** when it names the thing: a symbol, a function, a heading, an anchor.

> **RULE**: If one task changes both an artifact and a document that references that artifact
> **positionally**, the positional references are checked **after the artifact edits are final** —
> never before. A quotation of the pre-edit state MUST carry an explicit revision identifier
> (commit, tag, version), otherwise it reads as a claim about the current state.

**Why this is a rule and not a tip.** The failure is silent and self-confirming: the author *did*
verify the references — just before shifting them, so the check passed. The document then asserts
"verified" while pointing at a line that has moved and quoting a sentence the same task deleted.
Nothing fails; only a later reader or an adversarial review finds it.

**Where it bites most**: decision records (ADR/RFC) that both settle a question and update the
comments which referenced that question as open. That is the ordinary shape of such a task, not an
edge case.

**Prefer nominal over positional** wherever the target has a name. A reference to a symbol survives
an inserted line; a reference to line 112 does not.

Concrete verification differs per ecosystem and does not belong in the rule:

| Context | How to check |
| :--- | :--- |
| Any VCS-tracked repo | Verify against the **working tree**, not the last commit; when quoting a prior state, name the revision |
| Scriptable toolchain | Resolve every `path:line` from the document and print the target line back for the author to compare |

## 5. Markdown Structure (CRITICAL)

Applies to every `.md` artifact: TASK, PLAN, ARCHITECTURE, task files, issues, `.AGENTS.md`.
These rules are **formatter-independent** — they hold whether or not the project runs
Prettier, `markdownlint`, or nothing at all. A formatter only makes a violation *visible*
sooner; it is not the reason the rule exists.

### 5.1. Table cells are labels, not prose

A cell holds **one short value**: an id, a status, a link, or a single clause.

- **Hard limit: ≤ 120 characters and one sentence per cell.**
- **Never** put inside a cell: `<br/>`, a bulleted list, a multi-sentence explanation,
  a code block, or a nested table.
- Need more? The cell keeps a **short marker**, and the detail moves to a section below,
  keyed by the same id:

  ```markdown
  | ID   | Requirement             | MVP? |
  | ---- | ----------------------- | ---- |
  | R-29 | Adapter `nansen` (REST) | Yes  |

  ### Details by ID

  **R-29** — Adapter `nansen` (REST)

  - Host `api.nansen.ai` in the adapter's own allowlist (per-adapter SSRF).
  - Auth header is literally `apiKey: <KEY>`, not `Authorization: Bearer`.
  ```

**Why, with a formatter**: every table formatter pads each column to its widest cell.
One 2000-character cell therefore rewrites every row of that table — a one-cell edit
lands in review as a twenty-line diff that hides the actual change.

**Why, without a formatter**: it is worse. Nothing re-aligns the pipes, so the columns
stop lining up entirely and the table is no longer a table in raw form — which is how it
is read in `git diff`, in a terminal, and in any editor without Markdown preview.

**Why, in both cases**: wide tables scroll horizontally. A reader cannot compare rows they
cannot see side by side, which is the only reason to use a table instead of a list.

> [!TIP]
> If a column's content does not fit the limit for most rows, that column should not
> be a column. Convert the table to a definition list (**ID** — value + bullets).

### 5.2. Prose is structured, never a wall

- **Paragraph ≤ 5 lines.** Longer means a missing break or a missing list.
- **≥ 3 parallel items → a list.** If you are writing "first… second… third…", or a
  sentence carrying three or more comma-separated conditions, it is a list.
- **List nesting ≤ 2 levels.** Deeper means the section needs sub-headings instead.
- **Section > 40 lines → sub-headings.** A reader must be able to jump, not scan linearly.
- A list item that grows past ~3 lines becomes its own paragraph under a bold lead-in.

### 5.3. Line length

- **Hard-wrap prose at 100 characters** (match the project's `printWidth` where one exists).
- Do not rely on editor soft-wrap: diffs, review comments and blame are line-granular.
- **Exempt**: URLs, tables, code blocks — never break those to satisfy the limit.

### 5.4. Self-check before delivering any `.md`

```bash
# widest line + how many exceed the limit
awk '{n=length($0); if(n>100)c++; if(n>m)m=n} END {print "widest="m, ">100ch="c+0}' FILE.md
# alignment padding as a share of the file — over ~15% means prose is stuck in table cells
python3 -c "import re,sys;s=open(sys.argv[1]).read();p=sum(len(m) for m in re.findall(r'  +',s));print(f'padding {100*p/len(s):.0f}%')" FILE.md
```

## 6. Artifacts (`.AGENTS.md`)
Policy: keep `.AGENTS.md` for source-code directories under memory tracking. Missing file should not fail execution; bootstrap when needed.
> [!TIP]
> Use the template at `assets/templates/agents_md_template.md`.

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "It's a throwaway script" | Scripts evolve into products. Documenting later costs 3x more time. |
| "I don't know the types yet" | Use `Any` or `unknown` but document *what* the value represents. |
| "The table is the natural place for this detail" | A table answers *which* and *how much*. It cannot answer *why* — that is a paragraph. Mixing them costs both. |
| "Reformatting the doc is cosmetic churn" | Structure is what makes a document auditable months later. An unreadable artifact is an absent one. |

## 7. Resources
- `assets/templates/`: Collections of templates.
- `examples/good_documentation.py`: Gold standard example.
