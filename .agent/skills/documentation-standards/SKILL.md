---
name: documentation-standards
description: Standards for code documentation, comments, and artifact updates.
tier: 1
version: 1.7
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

**Pinning a deliberate quotation.** A pinned reference is a claim about *that* revision and is
exempt from re-checking; an unpinned one claims the current state, which is what makes the
check decidable at all. Two forms:

| Form | Example | Works in |
| :--- | :--- | :--- |
| `@<rev>` suffix | `` `src/app.py:42@v3.21.10` `` | any language, any revision kind |
| **Backticked** hash | `` …:101 на `985f843` `` | any language |
| `HEAD`, `HEAD~2` | "…`a.py:1` wie in HEAD~2" | any language, case-sensitive |
| Bare hash or version | "verified at 4f2a91c", "at v3.19.1" | needs an English cue |

**The backticks are what make it language-independent**, not the surrounding words: they
mark the token as an identifier rather than prose, which no list of prepositions can do
across languages. An *unmarked* hex run is a CSS colour, a build id or a digest far more
often than a revision, and an unmarked version is usually the subject of the sentence
("bump to v3.4") — so those pin only after an English cue.

`HEAD` is matched **case-sensitively** on purpose. Lower-case "head" is an ordinary English
word, and honouring it would exempt every line containing "the head of the list".

A prose pin applies only when the line carries **exactly one** reference — `path:line` and
`§` ordinals counted together — because prose cannot say which reference it qualifies.
Prefer `@<rev>`: it is per-reference, unambiguous, and language-neutral.

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
>    three quarters of all ordinals.
> 3. A target that numbers no headings at all — an ADR whose headings read `## D1 — Decision`
>    — makes its inbound ordinals *unverifiable*, not wrong; they are skipped.
>
> Limits 2 and 3 are not left to this document. Every run that meets a `§` at all prints how
> many ordinals it **checked** (passed and failed separately), how many it skipped **with the
> reason**, and how many it **never examined** — so a green report cannot be read as covering
> references it never looked at. Pinned `path:line` references are excluded from the
> "resolve" count for the same reason.
>
> **Prefer the nominal form** where a document offers one: `[Section 5](#5-claudemd-specification)`
> survives renumbering because the anchor, not the number, carries the meaning.

### 4.3. Structural anchors — a machine addresses a section by anchor, never by prose

§4.1 sorts references into **positional** (where a thing sits) and **nominal** (what it is called),
and prefers nominal. That is right and incomplete: a nominal reference can still break, because it
names its target **in a language**. Three rungs, not two:

| Rung | Form | Survives renumbering | Survives retitling | Survives translation |
| :--- | :--- | :--- | :--- | :--- |
| Positional | `§4.5`, `line 112` | ✗ | ✗ | ✗ |
| Nominal-by-prose | `## Requirements Traceability`, a `\| Requirement \|` column | ✓ | ✗ | ✗ |
| **Nominal-by-anchor** | `<!-- contract:rtm -->` | ✓ | ✓ | ✓ |

> **RULE**: A **human** may address a section at any rung. A **machine gate** addresses an authored
> document at the **anchor** rung. A gate that matches a heading's words, or a table's column names,
> is asserting that the document is written in a particular language — an assertion nobody made and
> the gate cannot check.

**Why this is a rule and not a tip.** Both failure modes are silent in the way that matters. The
loud one — the gate exits non-zero on a perfectly good document — pushes the author to write in a
language they do not use, or to stop running the step; and a step that can be quietly skipped is
distinguishable from a passed one only by someone eventually looking. The quiet one is worse: a
non-latin slug that normalizes to `"untitled"` makes two different documents resolve to one
filename, and reports nothing.

This framework had already reached the conclusion once, for one file — `known-issues-format` inserts
at a comment anchor *"because headings get renumbered and retitled"* — and did not generalize it. By
the time it was generalized there were three independent instances of the same defect, only one of
which anyone had filed.

**Syntax.** An HTML comment alone on its line, directly above the section heading or block it names,
followed by a blank line:

```markdown
<!-- contract:rtm -->

## 1. Requirements Traceability Matrix (RTM)
```

`<name>` is lowercase ASCII kebab-case. The comment is invisible in every Markdown renderer, so the
prose heading stays exactly as the author wrote it — the two audiences stop competing for one string.

**Lookup semantics** (binding on every gate that reads an anchor):

| Situation | Behaviour |
| :--- | :--- |
| Anchor present | Line-exact match after stripping whitespace. It wins over any prose matcher. |
| Anchor absent | Fall back to the gate's pre-existing prose matcher, unchanged. |
| Anchor present more than once | **Error**, never "first wins" — an ambiguous anchor is a document defect. |
| Anchor present, expected content absent | Error naming the anchor, not the heading. |

**Compatibility.** Anchors are **emitted on write, optional on read**. Every gate keeps its old
matcher as the fallback branch, so documents written before the anchor existed — archived artifacts,
which doctrine forbids editing, and every downstream project's corpus — behave byte-identically.
An anchor is never *required* by a gate; requiring one would break the corpus it governs, which is
the failure `skill-spec-validator` already survived once.

**Registry.** Reserved anchors live in §4.4. **No gate may key on an unregistered anchor.** The
converse is deliberately permitted: an anchor may be registered and emitted before any reader
exists, for the required sections of pipeline artifacts (§4.4), so that the *next* gate is
language-independent by construction instead of by remembering this rule.

### 4.4. Reserved anchor registry

`—` in **Consumer** means: emitted by the template, no reader yet, reserved so a future gate has a
structural target. Adding a row is how a new anchor is introduced; adding a *gate* that reads an
anchor absent from this table is a defect.

| Anchor | Document | Names | Consumer |
| :--- | :--- | :--- | :--- |
| `contract:defects` | `known-issues-format` SKILL + `known_issues_md_template.md` | Registry A schema block | `check_contract_sync.py` |
| `contract:work-items` | `known-issues-format` SKILL + `backlog_md_template.md` | Registry B schema block | `check_contract_sync.py` |
| `feedback:discovered-issues` | `docs/BACKLOG.md` | Index-line insertion point | `feedback_lib/ledger_backlog.py` |
| `contract:rtm` | `docs/TASK.md` | The RTM table | `skill-spec-validator` (`--mode task` **and** `--mode plan`) |
| `contract:meta` | `docs/TASK.md` | Meta table (ID, slug, type) | — |
| `contract:problem` | `docs/TASK.md` | Problem statement | — |
| `contract:use-cases` | `docs/TASK.md` | Use cases | — |
| `contract:acceptance` | `docs/TASK.md`, `docs/tasks/*.md` | Acceptance criteria | — |
| `contract:open-questions` | `docs/TASK.md` | Open questions | — |
| `contract:sequence` | `docs/PLAN.md` | Task execution sequence | — |
| `contract:coverage` | `docs/PLAN.md` | Use-case coverage table | — |
| `contract:goal` | `docs/tasks/*.md` | Task goal | — |
| `contract:changes` | `docs/tasks/*.md` | Changes description | — |
| `contract:tests` | `docs/tasks/*.md` | Test cases | — |
| `loop:<id>` | `.agent/workflows/*.md` | A retry loop's site (`<id>` = the loop's `contract.loops[].id`) | `check_loop_contract.py` (R3, R10) — design spec 095 |

> [!NOTE]
> `feedback:discovered-issues` keeps its own namespace: it marks an **insertion point** for a writer,
> not a contract block for a reader, and it predates this registry. Renaming it would rewrite live
> ledgers in every consumer project to no benefit.

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

### 5.5. Register — how the prose reads

Applies to authored prose **in whatever language the project writes**. This section constrains how
a sentence reads, never which language it is written in (ARCHITECTURE §7.3, invariant L2).

**Register is decided while writing, not after.** Load
`artifact-formalizer/references/authoring-contract.md` **before** the first sentence of any TASK,
ARCHITECTURE, PLAN or task file. It carries the six per-sentence tests and the licensed statement
forms. The scanner below measures whether that contract held; it is not the contract.

| # | Rule | Detector | What the detector does NOT reach |
| :--- | :--- | :--- | :--- |
| 1 | One claim per sentence | full | counts words, not claims |
| 2 | No evaluative markers | word list | judgement phrased in unlisted words |
| 3 | Reasoning separated from requirement | partial | reasoning split across two sentences |
| 4 | A rule is stated as a rule | partial | a novel aphorism |
| 5 | Severity is a named value | full | — |
| 6 | A private metaphor is not a term | partial | a metaphor coined today |

- **1** — over 35 words is the failure bound, not the target; every corpus mean is 5.8–15.4 words.
- **2** — a word asserting a judgment the reader cannot check: `obviously`, `robust`, `наивный`.
- **3** — the requirement states what must hold; justification goes under `**Why.**` or into Notes.
- **4** — no maxim or personification standing in for a norm.
- **5** — `🔴` is not a severity. `warn`, `SEV-2`, `Critical` are.
- **6** — established terminology stays verbatim; a metaphor coined for one document does not.

**A partial detector is not a pass.** Rules 3, 4 and 6 ship with declared recall limits, and the
reading pass owns the remainder — a coined metaphor is indistinguishable from a term until you check
where else it occurs. `--terms docs/ARCHITECTURE.md` runs the string half of that check. Read the
scanner's `DETECTORS` and `DIAGNOSTICS` blocks before its findings: a zero from a dead detector is
not a measurement, and a corpus whose longest sentence equals the limit was written for the gate.

**Thresholds are measured, not chosen.** 35 words sits far above every corpus mean (5.8 oldest,
14.1–15.4 newest) and catches the ~3.7% tail both newest corpora grew. A failing scan is resolved
in the prose; moving a threshold to obtain a green scan inverts the rule.

**Advisory by construction.** The scanner reports and never fails a phase, for the reason §4 gives:
a gate that fails on correct documents is how gates get switched off. Its non-advisory exits are a
**dead detector** (`2`) and a **usage error** (`3`) — a broken instrument and a mistyped command,
neither a verdict on the document.

**This section owns register only.** Cell width and cells-as-prose → §5.1 (the scanner surfaces both
as `cell_width` and `cell_sentences`). Paragraph and list shape → §5.2. Line length → §5.3.

> [!TIP]
> Authoring contract, rewrite guide, per-language marker data and the scanner:
> **`artifact-formalizer`**.

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
- **Primary Evidence**: `tests/test_positional_refs.py` — 84 tests over throwaway git repositories
  covering extraction, shorthand ambiguity, each finding class, language-independent pinning and
  its false-pin guards, ordinal parsing and denylisting, scope honesty, path containment, and
  every exit code. Gated in `framework-gates.yml` and named in `tests/run_tests.py`, so the
  suite a developer runs locally is not blind to it.
- **Secondary Evidence**: a diff-scoped run on the change under review, quoted in the review notes.
- **Quality Gate**: no `error`-severity findings; every `DRIFT_SUSPECT` explicitly confirmed.

## 8. Resources
- `assets/templates/`: Collections of templates.
- `examples/good_documentation.py`: Gold standard example.
