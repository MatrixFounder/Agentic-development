# TASK 103 — A positional reference carries its referent

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 103 |
| Slug | referent-carrying-positional-references |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-07; routed from onchain-analytics `docs/backlog/wi-43-line-anchored-citations-in-docs-decay-silently.md` |
| Depends on | TASK 095 (structural anchors and gate honesty — the tool this task extends) |
| Closes | WI-17 (filed by this task as the routed record) |
| Archive name | `task-103-referent-carrying-positional-references.md` |

<!-- contract:problem -->

## 1. Problem

A `path:line` reference in a document is a **claim about state written in the grammar of an
address**. Nothing observes it going false. `documentation-standards` §4.1 already states the
adjacent half of this — "prefer nominal over positional" — as a preference, and
`scripts/check_positional_refs.py` already resolves the address. Neither reaches the case where the
address resolves, is in range, and points at something else entirely.

**Measured in onchain-analytics at `e95b909`** (clean worktree; method: `git blame` the citing line
for the commit that authored it, `git show <sha>:<target>` for the content it then had, compared
against the content now):

| Population | Count |
| :--- | :--- |
| `path:line` references in the living corpus (`docs/PLAN.md`, `docs/TASK.md`, `docs/architectures/`) | 182 |
| of those, resolvable | 142 |
| of those, pointing at content that is not what it was when written | **26** |
| references the resolver reports today in that corpus | 40, all `AMBIGUOUS` |
| of the 26 drifted, reported by the resolver today | **0** |

The 26 are invisible because they are objectively fine on every axis the tool checks: the path
resolves, the line exists, the document was not edited by the current change.

**The mechanism is structural, not a lapse in care.** Measured over the same corpus, 85 of the 142
attributable references were written by the Analysis, Architecture and Planning phases — phases that
by construction run **before** the Development phase edits the files they cite. In task T-013,
`packages/core/src/adapters/registry.ts` went 950 → 1560 lines across four commits **after** the
analysis document had recorded 50 coordinates into it.

**§4.1's existing mitigation cannot reach this.** It prescribes that positional references are
verified LAST, "after the artifact edits are final". A PLAN is a positional-reference-dense document
that the pipeline requires to be written FIRST. The rule and the pipeline contradict each other, and
the plan loses.

**The resolver's scope cannot reach it either.** `collect_docs()` returns only changed `*.md`
files, so a commit that edits sources and no document scans nothing — which is precisely the commit
that invalidates references.

**An authoring rule alone is refuted, not untried.** `onchain-analytics/docs/architectures/open-questions.md:374@e95b909`
carries the rule in prose, written by its own author: *"re-measure them, or quote the predicate
text, whenever this file is touched."* The same paragraph records that `:740`/`:764` had already
rotted once. Its `:901` has since rotted again — the predicate now sits at `:1511`.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Verified by |
| :--- | :--- | :--- | :--- |
| R1 | `documentation-standards` §4.1 licenses a **referent** adjacent to a positional reference and names what satisfies one | Y | A1, A6 |
| R2 | A reference **without** a referent is reported as *not examined* — never an error, never a warning | Y | A2, A3 |
| R3 | The resolver reports four referent outcomes: present on the cited line · found uniquely elsewhere · found several times · absent | Y | A2 |
| R4 | `--fix` rewrites the **line number** of a uniquely-relocated referent and never rewrites a referent | Y | A2, A4 |
| R5 | Document selection reaches documents whose **targets** changed, not only documents that changed | Y | A2 |
| R6 | `--all` accepts files as well as directories, so a project can name its living corpus | Y | A2 |
| R7 | The coverage line states with a referent / without one / unresolvable counts separately | Y | A2, A3 |
| R8 | `artifact-formalizer/references/authoring-contract.md` carries one licensed-form row for the reference that carries a referent | Y | A1, A6 |
| R9 | §4.2 states what the referent layer makes gateable and what stays advisory, without contradicting its own 54-of-84 measurement | Y | A1, A6 |
| R10 | The routed record exists in `docs/BACKLOG.md` + `docs/backlog/`, and both changelogs carry the change | Y | A5, A7 |
| R11 | `System/Docs/SKILLS.md` describes the skill as it is after this change — the resolver, its referent layer and its fix mode | Y | A9 |

### 2.1 Sub-features

**R1 — the referent, defined by adjacency.** A referent is a **code span immediately following the
reference code span**, separated by nothing but whitespace and at most one comma. Two spellings,
one rule: a symbol name that appears on the cited line, or an exact substring of it. No new syntax
is introduced — the form is one authors already write, e.g.
`onchain-analytics/docs/PLAN.md:196@e95b909`: `` `registry.ts:1083@e95b909`, `if (deadlineHit \|\| …) {` ``.
Adjacency is an established mechanism in this tool: `SECTION_ORDINAL` already binds an ordinal to
the target named immediately before it.

**Comparison is normalized** by collapsing runs of whitespace and by unescaping `\|`. The first is
required because the target line carries its own indentation while the referent as written does not;
the second because a quotation inside a Markdown table cell MUST escape the pipe or the cell splits,
and plans put quotations in table cells. Without both, a correctly-written referent reports as
broken, and a gate that fails correct documents is switched off.

**103-D9 — the referent sits on the same document line as its reference.** Discovered in
implementation: `extract_refs()` scans line by line, so a code span wrapped across two document
lines is not one span. Two directions were possible and one is licensed — a referent **follows** its
reference, because a line carrying two references and one quotation is otherwise unassignable. The
cost is stated rather than hidden: a document whose quotation precedes the coordinate, or wraps, is
**not examined** — it is not reported as broken. That is R2's rule applied to a form the tool cannot
parse, which is the same guarantee, not an exception to it.

**R2 — the blast radius is zero by construction.** Measured across all 17 repositories carrying
`.agent/skills/`: 11 hold no `path:line` reference at all; the living corpora hold 324 in total
(onchain-analytics 182, obsidian-llm-wiki 99, Universal-skills 36, agentic-development 6,
n8n-lazy-loading-skills 1). An reference without a referent must therefore be **unverifiable, not wrong** —
otherwise this upgrade turns 324 references red in four repositories that did not ask for it. This
is the same discipline §4.2 already applies: a green run must not overclaim.

**R3 — four outcomes, three of which need a human and one that does not.**

| Outcome | Kind | Severity | Human needed |
| :--- | :--- | :--- | :--- |
| referent is on the cited line | — (pass) | — | no |
| referent occurs exactly once, on another line | `REFERENT_MOVED` | error | **no** — `--fix` resolves it |
| referent occurs several times | `REFERENT_AMBIGUOUS` | error | yes — pick one |
| referent occurs nowhere in the target | `REFERENT_ABSENT` | error | yes — the cited text changed, so the claim about it must be re-read |

`REFERENT_ABSENT` is the class the tool cannot decide and must not guess: the target line was edited,
which means the sentence citing it may now be false for reasons no coordinate repair addresses.

**R4 — the fix boundary, inherited from `verify-provenance.mjs`.** That script keeps `--update`
deliberately outside its gate: re-baselining must be a decision someone takes and a reviewer sees.
The boundary here falls in a different place **for a stated reason, not as a relaxation**: the
referent is the claim and is never machine-written; the line number is a value derived from it and may
be recomputed. `--fix` is therefore permitted to rewrite a number and forbidden to rewrite a
referent, and it is a separate invocation from the check — the pairing `format:check` / `format`, not
a gate that mutates the tree it is judging.

**The module docstring moves with the behaviour.** `check_positional_refs.py:17` states "Read-only.
The tool never writes to the repository" as one of three design constraints. `--fix` breaks it as
written. R4 therefore requires the constraint restated and narrowed in the same change — the check
never writes; the separately-invoked fix mode writes a line number and never a referent. Shipping the
flag against an unamended docstring would leave the file asserting an invariant its own CLI
contradicts, which is the defect class this whole task exists to close.

**R11 — the registry describes what exists.** `System/Docs/SKILLS.md:68` carries the
`documentation-standards` row and a note at `:98`; neither names the resolver, §4.1 or §4.2. A skill
that gains a normative rule, four finding kinds, two selection surfaces and a write mode must not be
described by a row written before any of them.

**R5 — selection by changed target.** The tool gains a third selection mode beside diff-scope and
`--all`: documents that reference a file the current change touched. `changed_files()` already
computes the change set; the addition is an index from target path to citing documents, which
`classify()` effectively builds already when it resolves each reference.

**R6 — `--all` accepts files.** `collect_docs()` rglobs each argument as a directory. A living
corpus is `docs/PLAN.md docs/TASK.md docs/ARCHITECTURE.md docs/architectures/` — two files and a
directory — and is not expressible today. Passing `docs` instead pulls in the archives: measured on
onchain-analytics, `--all docs` reports 223 errors of which 183 are in archived documents whose
coordinates are correct records of a past state.

**R7 — the denominator travels with the number.** The run already prints checked / skipped / never
examined for ordinals. The same treatment extends to `path:line`: how many carried a referent, how
many did not, how many could not be resolved at all. A count without its population is the second
defect the routed record measured, and this requirement applies its lesson to the tool itself.

**R8 — one contract row.** The precedent is WI-16 §5.3: a normative rule in
`documentation-standards` plus one row in the licensed-forms table of
`artifact-formalizer/references/authoring-contract.md`, because the Architecture phase loads the
formalizer contract and does not load `documentation-standards`. A row pointing at §4.1 alone would
send that author to a file they do not have.

**R9 — the old measurement is not overturned.** §4.2 rejects a repository-wide gate on evidence: 54
of 84 resolvable references point into files edited after the citing document was written, and
nearly all are correct records of their time. That measurement was taken over **archived reviews**
and stays true. R9 requires §4.2 to state the distinction — the referent layer is gateable over a
**named living corpus** and stays advisory everywhere else — so the two statements in one file do
not read as contradiction.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — a developer moves code that documents cite.**
*Actor:* Developer in the Execution phase.
*Precondition:* the living corpus carries references that carry a referent into the file being edited.
*Main:* the commit inserts lines above a cited coordinate; the pre-commit invocation of `--fix`
rewrites the affected numbers; the developer sees a one-line diff per reference in the same commit.
*Postcondition:* no document in the corpus carries a coordinate contradicted by the tree.

**UC-2 — a planner writes a coordinate before the code exists in final form.**
*Actor:* Planner in the Planning phase.
*Precondition:* the PLAN cites lines that the Development phase will shift.
*Main:* the planner writes the coordinate **with** the predicate it means; the Development phase
shifts the line; UC-1 repairs the number without the planner re-reading anything.
*Postcondition:* §4.1's "verify LAST" rule is satisfiable for a document written FIRST.

**UC-3 — the cited text is edited, not merely moved.**
*Actor:* Code Reviewer.
*Main:* the referent is absent from the target; the tool reports `REFERENT_ABSENT` with the file, the
number and what now sits there; the reviewer re-reads the sentence, because the claim — not the
coordinate — is what became doubtful.
*Postcondition:* the edit is either confirmed against the new text or corrected.

**UC-4 — a consumer repository upgrades the framework and changes nothing.**
*Actor:* any of the 16 consumer repositories.
*Precondition:* its documents carry references without a referent, or none at all.
*Main:* the upgrade lands; every existing reference is reported as *not examined*; no gate turns
red; the coverage line states how much of the corpus is unverified.
*Postcondition:* adoption is a per-project decision, taken later or never.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Fails when |
| :--- | :--- | :--- |
| A1 | §4.1 states the referent rule; §4.2 states the corpus distinction; the contract row exists | any of the three is absent · the row and §4.1 state different obligations |
| A2 | `pytest tests/test_positional_refs.py` passes with cases pinning R2–R7 | a new case is absent for any of R2, R3 (all four outcomes), R4, R5, R6, R7 |
| A3 | A corpus of references carrying no referent produces exit 0 and a coverage line naming them as not examined | a reference without a referent produces a finding of any severity |
| A4 | `--fix` on a moved referent rewrites the number only; on `REFERENT_ABSENT` and `REFERENT_AMBIGUOUS` it changes nothing; the module docstring states the narrowed constraint | the referent text is modified in any run · a non-unique match is repaired by guessing · the docstring still reads "the tool never writes to the repository" unconditionally |
| A5 | `docs/BACKLOG.md` carries WI-17 in lockstep with `docs/backlog/wi-17-*.md` | index line without record, or record without index line |
| A6 | `python3 System/scripts/validate_skills.py --root .` passes at the same count as before | the count changes · any skill fails validation |
| A7 | `CHANGELOG.md` and `CHANGELOG.ru.md` both carry the entry | one is edited and the other is not |
| A8 | The tool is run against this repository's own living corpus and its output is recorded in the plan's closing step | the change ships without being run on a real corpus |
| A9 | The `documentation-standards` row in `System/Docs/SKILLS.md` names the resolver, its referent layer and its fix mode | the row is unchanged · it describes a capability the skill does not have |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — wiring.** No workflow and no agent prompt invokes `check_positional_refs.py` today;
measured across `.agent/workflows/`, `System/Agents/` and every `SKILL.md`, the only file naming it
is `documentation-standards` itself. Binding it to phase boundaries is the mechanism WI-16 §5.1
sizes at nine workflows. **Deliberately out of scope here** (§7); this task ships the capability, not
its enforcement.

**OQ-2 — referents in source files.** A marker convention in the code (`// ANCHOR: name`) would remove
line numbers from references altogether. Rejected for this task, reasons in D3; re-openable.

<!-- contract:decisions -->

## 6. Decisions

**103-D1 — a reference without a referent is not examined, not an error.** Any other choice turns 324
references red across four repositories on upgrade. A rule whose adoption cost is paid by projects
that did not ask for it is switched off, which is the outcome §4.2 already recorded once.

**103-D2 — the referent is a code span adjacent to the reference, not new syntax.** 111 of the 182
references in the routed corpus already carry a backticked identifier or quotation on the same line.
Licensing the existing form makes the majority of the migration a binding exercise rather than a
writing exercise, and keeps the register unchanged.

**103-D3 — no edits to source files.** In-source referents were considered: they would eliminate
positional references entirely. Rejected on four grounds — they require edits across every package
of every consumer; a marker that exists for a document is deleted by refactors that do not know
about it; a second gate is then needed to assert the marker still exists; and prose citing "these
five lines" still has no name to bind to. The symbol spelling of D2 already recovers most of the
benefit, because symbols are referents the code declares for its own reasons.

**103-D4 — `--fix` may rewrite a number and never a referent.** Stated as a boundary rather than a
permission: the derived value is recomputable, the claim is not. This is why the rule does not
contradict `verify-provenance.mjs`, whose invariant *is* the recorded value.

**103-D5 — the migration of any corpus is out of scope.** This task ships the mechanism to
agentic-development. Adding referents to onchain-analytics' 182 references is that project's decision and its
own commit, per the routed record's §4.

**103-D7 — the mechanism is called a REFERENT, never an anchor.** The first draft called it an
anchor and collided with an occupied word: `documentation-standards` §4.3 and §4.4 define an anchor
as `<!-- contract:<name> -->`, a structural marker addressing a *section*, and ARCHITECTURE §7.2
builds its addressing ladder on that meaning. One file would then carry two mechanisms under one
name. "Referent" is the term WI-16 already uses for "the observation that falsifies a claim", which
is exactly this object.

**103-D8 — the rule extends §4.1 and claims no new section number.** §4.5 is reserved by the open
WI-16 for the build-state claim rule. A positional reference carrying its referent is a refinement
of §4.1's own subject, so it lands inside §4.1 and leaves the numbering free.

**103-D6 — `REFERENT_ABSENT` is an error, not a warning.** The tool can distinguish "moved" from
"changed", and a changed target is the case where the citing sentence may itself be false. Grading it
a warning would place the only judgement-requiring outcome in the class readers skip.

<!-- contract:out-of-scope -->

## 7. Out of scope

- **Wiring the tool into workflows** (OQ-1). Nine workflows and a Global Protocol; a separate item.
- **Migrating any repository's references**, including this one's six (D5).
- **Semantic verification.** A referent proves the quoted text is present, not that the sentence
  about it is true. A document calling a cache-warming comment "the narrowing of `matching` routes"
  passes the referent check if it quotes that comment. Only reading closes this.
- **Archived documents.** Their coordinates are correct records of a past state; §4.2's 54-of-84
  measurement is about exactly this population and is not overturned (R9).
- **In-source referent markers** (OQ-2, D3).
- **A gate over the rule's own two halves.** R1 writes the rule into `documentation-standards` §4.1
  and R8 writes the mirroring row into `artifact-formalizer/references/authoring-contract.md`.
  Nothing compares them after landing — `check_contract_sync.py` reaches only `known-issues-format`
  and its two seed templates. Drift between the two is uncaught, exactly as WI-16 §5.3 recorded for
  its own pair. Stated so a reader does not assume a gate exists.
- **The reporting rule for surveys** — "a survey states its search area with its count". The routed
  record measures this as a second defect; R7 applies it to this tool's own output and to nothing
  else.
