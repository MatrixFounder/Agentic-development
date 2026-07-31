---
name: documentation-standards
description: Standards for code documentation, comments, and artifact updates.
tier: 1
version: 1.6
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

**Pinning a deliberate quotation.** Suffix the reference with `@<rev>` — as in
`` `src/app.py:42@v3.21.10` `` — or name the revision in the same line of prose
("verified at v3.19.1", "as of 4f2a91c"). A pinned
reference is a claim about *that* revision and is exempt from re-checking. An unpinned one claims
the current state, which is what makes the check decidable at all.

Concrete verification differs per ecosystem and does not belong in the rule:

| Context | How to check |
| :--- | :--- |
| Any VCS-tracked repo | Verify against the **working tree**, not the last commit |
| Quoting a prior state | Pin with `@<rev>`, or name the revision in the same line |
| Scriptable toolchain | Resolve every `path:line` and print the target line back for comparison |
| This framework | Run `scripts/check_positional_refs.py` — see §4.2 |

### 4.2. Reference resolver (advisory)

`scripts/check_positional_refs.py` implements the scriptable row above. It is **advisory and
diff-scoped**, not a gate, for a reason worth keeping: a survey of this repository's archived
reviews found 54 of 84 resolvable references pointing into files edited after the citing document
was written — and nearly all of them are correct records of the state at the time. A gate scoped
that widely would fail on correct documents, which is how gates get switched off.

```bash
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py   # current change
python3 .agent/skills/documentation-standards/scripts/check_positional_refs.py --base main
```

| Finding | Severity | Meaning |
| :--- | :--- | :--- |
| `UNRESOLVABLE` | error | No file matches the path — objectively broken |
| `AMBIGUOUS` | error | A shorthand matching several files; write a repo-relative path |
| `OUT_OF_RANGE` | error | The line number is past end-of-file, zero, or a descending range |
| `ORDINAL_MISSING` | error | The target document declares no such `§` section |
| `DRIFT_SUSPECT` | warning | The target is edited by this same change; the §4.1 case |
| `ESCAPES_ROOT` | warning | Points outside the repository: refused a read, not verifiable |

Only `DRIFT_SUSPECT` needs judgement: the tool prints the target line back, and the reviewer
confirms it still says what the document claims. Pinned references are skipped entirely.

**Section ordinals** are positional too, and the tool checks the slice it can check honestly:
an ordinal whose target is named *next to it* — a skill name, a repo path, or a markdown link
(`` `developer-guidelines` §1.5 ``). Both numbered headings and numbered list items count as
declarations, because references such as `01_orchestrator.md` §1.3 address a list item.
Ranges (`§1–§3`) expand; external specs (CommonMark, OWASP) and other repositories are excluded.

> [!NOTE]
> **Known limits, stated because a green run must not overclaim.**
> 1. Only *changed* documents are scanned. A change that edits only source, shifting lines
>    under an untouched older document, is out of scope — the archived-document case above,
>    where a warning would be noise rather than signal.
> 2. A **bare** ordinal (`see §4.2`, `TASK §4`) is never checked. Its antecedent lives in
>    prose, and guessing one manufactures false failures. In this repository that is roughly
>    three quarters of all ordinals, so the tool prints that caveat in its own output.
> 3. A target that numbers no headings at all makes its inbound ordinals *unverifiable*,
>    not wrong; they are skipped.
>
> **Prefer the nominal form** where a document offers one: `[Section 5](#5-claudemd-specification)`
> survives renumbering because the anchor, not the number, carries the meaning.

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

## 7. Execution Policy

### 7.1. Execution Mode
- **Mode**: `hybrid`
- **Rationale**: the documentation standards themselves are prompt-driven judgement, while
  positional-reference resolution (§4.2) is mechanical and therefore script-driven.

### 7.2. Script Contract
- **Primary Command**: `python3 scripts/check_positional_refs.py [--root DIR] [--base REV]`
- **Inputs**: repository root, revision defining the current change, optional `--all [DIR ...]`.
- **Outputs**: human-readable findings, or a JSON array with `--json`.
- **Failure Semantics**: `0` no errors, `1` errors present (or any finding under `--strict`),
  `2` usage or environment problem such as a non-repository root.

### 7.3. Safety Boundaries
- **Scope**: read-only. The tool opens files and runs read-only `git` queries; it never writes,
  edits, or deletes anything in the repository.
- **Default Exclusions**: documents outside the current change are not scanned unless `--all`
  is passed explicitly.
- **Destructive Actions**: none. There is no fix or rewrite mode, deliberately — deciding whether
  a reference is stale or a legitimate quotation is the reviewer's judgement, not the tool's.

### 7.4. Validation Evidence
- **Primary Evidence**: `tests/test_positional_refs.py` — 60 tests over throwaway git repositories
  covering extraction, shorthand ambiguity, each finding class, pin exemption, ordinal parsing
  and denylisting, path containment, and every exit code. Gated in `framework-gates.yml`.
- **Secondary Evidence**: a diff-scoped run on the change under review, quoted in the review notes.
- **Quality Gate**: no `error`-severity findings; every `DRIFT_SUSPECT` explicitly confirmed.

## 8. Resources
- `assets/templates/`: Collections of templates.
- `examples/good_documentation.py`: Gold standard example.
