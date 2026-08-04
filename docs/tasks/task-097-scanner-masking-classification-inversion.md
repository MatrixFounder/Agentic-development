# TASK 097 — Register scanner: masking must not invert code/prose classification

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 097 |
| Slug | scanner-masking-classification-inversion |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator report, 2026-08-04; reproduced and re-measured before drafting |
| Depends on | TASK 096 (`docs/tasks/task-096-artifact-register-formalization.md`) |
| Archive name | `task-097-scanner-masking-classification-inversion.md` |

<!-- contract:problem -->

## 1. Problem

`mask()` in `.agent/skills/artifact-formalizer/scripts/scan_register.py` applies four regular
expressions in sequence, each over the whole text. `HTML_COMMENT` runs before `CODE_SPAN`. Both
carry `re.S`.

A comment boundary that falls inside a code span removes an odd number of backticks. The surviving
backtick then pairs with a later one. From that offset the classification inverts: prose is masked
as code, and code is scanned as prose. `re.S` carries the inversion to the end of the file.

The scan then reports `0 warn / 0 info` and exits 0. The output states `18/18 detectors live`.
Nothing in it distinguishes this from a document that is clean.

**Why this ranks above an ordinary defect.** The skill exists to report whether a document holds a
register. This false negative prints an answer no reader can distinguish from a true zero.

### 1.1 Evidence

All figures below were produced by execution against this repository at commit `992b3ef`.

| # | Measurement | Value |
| :--- | :--- | :--- |
| E1 | Fixture of valid Markdown: Cyrillic letters surviving `mask()` | 28 of 167 |
| E2 | Same fixture, finding reported | none; `0 warn`, exit 0 |
| E3 | Same fixture with the trigger removed, finding reported | 1 (`§5.5 r2, marker`) |
| E4 | Documents with odd backtick parity after `mask()` | 14 of 598 |
| E5 | `task_md_template.md`: prose reaching rule 1 | 27%, against 50% without the trigger |
| E6 | `task_md_template.md`: lines masked away | 42, against 17 without the trigger |
| E7 | Prose a corrected `mask()` restores to the rules | +61,889 letters across 169 documents |
| E8 | Masked-letter fraction across the corpus | p50 22.1%, p95 63.1%, max 97.3% |

**E1–E3, the reproducing fixture.** The trigger is a marker cited in a code span, followed by a
correct HTML comment:

```markdown
Маркер `<!--` открывает HTML-комментарий.

<!-- обычный, корректный комментарий -->

Дальше идёт обычная проза, которую сканер обязан читать. Наивный подход здесь неверен.
```

The input is valid Markdown. The document needs no repair; the instrument does.

**E4–E6, the reach inside this repository.** Two of the 14 documents are shipped templates:
`.agent/skills/skill-planning-format/assets/templates/task_md_template.md` and its plan sibling.
Every task file authored from those templates inherits the construct.

### 1.2 Two inputs, only one of which is malformed

The task separates them, because the remedy differs.

| Case | Example | Verdict | Remedy |
| :--- | :--- | :--- | :--- |
| A | A marker cited in a code span, as in E1 | Valid Markdown | R1–R4: the instrument |
| B | An HTML comment whose body contains `-->` | Malformed | R12: the document |

**Case A occurs in 20 files under `.agent/`, `System/` and `docs/`.** Citing a marker in a code
span is how this repository documents its own anchors. Editing 20 correct documents to accommodate
one instrument is the wrong direction.

**Case B is a defect a reader sees, and the scanner is not the reason.** `markdown-it` in
`commonmark` mode closes the comment at the inner `-->`. The remainder — one sentence plus a
literal `--&gt;` — renders as a visible paragraph. Both shipped templates hold this construct; no
other file in the corpus does.

**Scope note.** The templates carried Case B before commit `992b3ef`, which added one blank line to
each. The scanner is what is new. `docs/TASK.md`, `docs/PLAN.md` and `docs/ARCHITECTURE.md` are
unaffected today: parity is even and 8–35% of letters are masked.

### 1.3 Two further defects of the same class

Both were found by the review of commit `992b3ef` and reproduced here before being folded in. Each
one is the instrument reporting green while a check is dead, which is the defect §1 describes.

**D2 — an unreadable path claims the instrument is broken.** `scan_register.py:1194` returns 2 when
a file cannot be read. Code 2 means a dead detector. The CI advisory step carries no `|| true`, so
a push fails whenever `docs/TASK.md` is absent. That absence is the framework's own state between
`skill-archive-task` and the next analysis phase. Reproduced: exit 2, with `No such file or
directory` as the only output.

**D3 — the rule-3 probe exercises 1 regex of 23.** `scan_register.py:917` runs one declared probe
string for the whole modal-by-causal cross-product. Reproduced by mutation: replacing `\bshall\b`
in `register-en.json` leaves `--probe` at `18/18 detectors live` and the selftest at `128/128`,
while the sentence `The installer shall abort because the target exists.` loses its finding.

**Out of scope.** The review confirmed 32 further findings. They are filed in the ledger, not fixed
here. In scope: D2, D3, and the masking defect. Out of scope: everything else the review confirmed
(carried by `docs/KNOWN_ISSUES.md`).

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | Masking must not change the code/prose classification of any text that follows a masked construct. | Yes | UC-1, T1, T2 |
| R2 | A masked construct must not begin inside another masked construct. | Yes | T3 |
| R3 | A code span must not cross a blank line. | Yes | T4 |
| R4 | Valid Markdown carrying the E1 trigger must be masked correctly and raise no diagnostic. | Yes | UC-1, T1 |
| R5 | An unterminated HTML comment must be named in the output. | Yes | UC-2, T5 |
| R6 | An unpaired backtick surviving masking must be named in the output. | Yes | UC-2, T6 |
| R7 | Exit 2 must stay reserved for a dead detector. | Yes | T7 |
| R8 | `DIAGNOSTICS` must report the masked-letter fraction. | Yes | UC-3, T8 |
| R9 | `SKILL.md` §2 must name which `DIAGNOSTICS` value invalidates a scan. | Yes | UC-3 |
| R10 | The 128 existing selftest cases must pass unchanged. | Yes | T9 |
| R11 | `--probe` must report 18 of 18 detectors live. | Yes | T10 |
| R12 | The two shipped templates must render no comment body as page text (Case B). | Yes | T11 |
| R12a | A marker cited in a code span (Case A) must stay unedited in all 20 files that hold it. | Yes | T11a |
| R13 | `references/measurement-baseline.md` must record this defect and its measurement. | Yes | T12 |
| R14 | The register scan must raise no exit-2 across the 598-document corpus. | Yes | T13 |
| R15 | `CHANGELOG.md`, `CHANGELOG.ru.md` and `System/Docs/SKILLS.md` must state the new behaviour. | Yes | T14 |
| R16 | A path the scanner cannot read must exit 3 and must be named in the output. | Yes | T15 |
| R17 | `--allow-missing` must let a named absent file exit 0; without it, absence exits 3. | Yes | T16 |
| R18 | The CI advisory step must pass in the archived state, where `docs/TASK.md` is absent. | Yes | T17 |
| R19 | `--probe` must exercise every rule-3 modal and every rule-3 causal. | Yes | T18 |
| R20 | The `--probe` detail must state what it exercised, not what the data declares. | Yes | T19 |

<!-- contract:use-cases -->

## 3. Use Cases

### UC-1 — An author scans a document that cites a marker

**Actors.** Author; `scan_register.py`.

**Preconditions.** The document is valid Markdown. It cites `<!--` inside a code span, and it also
contains an HTML comment.

**Main scenario.**
1. The author runs the scanner on the document.
2. The scanner masks each construct without letting one begin inside another.
3. The scanner reports every finding in the prose that follows the comment.
4. The scanner exits 0.

**Postcondition.** The finding set equals the set for the same document without the citation.

**Alternative A1.** The document contains a stray backtick. The scanner bounds the mispairing at
the next blank line and names the unpaired backtick.

### UC-2 — A malformed document reaches the scanner

**Actors.** Author; `scan_register.py`.

**Preconditions.** The document contains an HTML comment with no terminator, or an unpaired
backtick.

**Main scenario.**
1. The author runs the scanner.
2. The scanner names the construct and the line it starts on.
3. The scanner reports findings for the prose it could classify.
4. The scanner exits 0.

**Postcondition.** The operator can tell a named-input case from a clean document by reading the
output.

**Why exit 0.** Exit 2 means the instrument is broken. A malformed document is an input, and
`documentation-standards` §4 forbids a gate that fails on documents the project may legitimately
hold.

### UC-3 — An operator judges whether a scan is a measurement

**Actors.** Operator; CI.

**Preconditions.** A scan reported zero findings.

**Main scenario.**
1. The operator reads `DIAGNOSTICS`.
2. `DIAGNOSTICS` states the masked-letter fraction and the count of named input defects.
3. The operator compares that fraction against the band `SKILL.md` §2 states.

**Postcondition.** A zero finding count is accompanied by the evidence that the document was read.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Test obligation |
| :--- | :--- |
| T1 | E1 fixture → the `§5.5 r2` finding is reported; fails when the tokenizer is replaced by the sequential `re.sub` loop |
| T2 | E1 fixture → Cyrillic letters surviving masking ≥ 160 of 167; fails when construct order is restored |
| T3 | Both fixtures → no masked region overlaps another; fails when two constructs are allowed to nest |
| T4 | A code span opened before a blank line → the span is not masked past that blank line; fails when `re.S` is applied without the paragraph bound |
| T5 | Document with `<!--` and no terminator → the output names it; fails when the unterminated branch is removed |
| T6 | Document with one stray backtick → the output names it; fails when the parity check is removed |
| T7 | Every input in T1–T6 → exit 0; a killed detector → exit 2 |
| T8 | Any scan → `DIAGNOSTICS` carries the masked-letter fraction |
| T9 | `python3 .agent/skills/artifact-formalizer/scripts/selftest_scan.py` → 128 existing cases plus the new ones pass |
| T10 | `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py --probe` → `18/18 detectors live` |
| T11 | Each shipped template rendered by `markdown-it` in `commonmark` mode → no text from inside a comment appears in the output |
| T11a | `git diff` over the 20 Case-A files → empty |
| T12 | `references/measurement-baseline.md` contains E1–E8 |
| T13 | The scanner over all 598 corpus documents → no exit 2 |
| T14 | Both changelogs and `System/Docs/SKILLS.md` name the input-defect diagnostics |
| T15 | An unreadable path → exit 3, and the path appears in the output; fails when the read branch returns 2 |
| T16 | An absent file with `--allow-missing` → exit 0; the same file without the flag → exit 3 |
| T17 | The CI advisory command run with `docs/TASK.md` absent → exit 0 |
| T18 | Each rule-3 modal and each rule-3 causal replaced by a non-matching pattern → `--probe` exits 2; fails when one declared pair stands in for the cross-product |
| T19 | `--probe` detail for `reasoning` states the count it exercised, and that count equals the vocabulary size |

Beyond the per-test obligations: the full gate set of `.github/workflows/framework-gates.yml`
passes, and `git status` is clean after the run.

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — Do the recovered 61,889 letters change the advisory CI scan?** The three living artifacts
show even parity today, so the expected change is zero. Blocks: nothing. Owner: implementer,
answered by running the advisory step before and after.

**OQ-2 — Should the 12 affected `docs/tasks/task-095-*.md` archives be repaired?** They are
archived documents, and repairing them edits history. Blocks: nothing in this task. Owner:
operator.

## 6. Rejected candidates

| Candidate | Measurement that rejected it |
| :--- | :--- |
| Masked-letter fraction above a fixed threshold exits 2 | E8; fires on 26 correct documents |
| Reorder `CODE_SPAN` before `HTML_COMMENT` | Moves the inversion; a cited `-->` then breaks the comment |
| Treat odd backtick parity as an instrument failure | E4; parity also goes odd on a stray backtick |

**Threshold candidate.** 8 of those 26 documents are fenced by construction, so a high fraction is
their correct state. `documentation-standards` §4 forbids a gate that fails on correct documents.

**Parity candidate.** A stray backtick is an input defect. R6 names it; R7 keeps exit 2 for the
instrument.

## 7. Decisions

**D-097-1, 2026-08-04, implementer:** masking becomes one left-to-right pass that consumes a
construct whole. Rejected: keeping four independent `re.sub` calls and fixing their order — the
ordering argument already stated in the `mask()` docstring for fences does not extend to comments.

**D-097-2, 2026-08-04, implementer:** a code span is bounded by a blank line, per CommonMark.
Rejected: unbounded `re.S` — it lets one mispairing reach the end of the file.

**D-097-3, 2026-08-04, implementer:** a named input defect exits 0. Rejected: exit 2 for malformed
input — it conflates the document with the instrument and would fail CI on documents the project
may hold.
