# Authoring contract — the register you write in, before the first sentence

Load this **before** writing a specification, not after. Everything below is generative: it gives
the sentence forms to write *from*. The lexicon in `data/register-*.json` is a backstop that
measures whether this contract held; it is not the contract.

Applies in the document's own language. This contract constrains how a sentence reads, never which
language it is written in (`documentation-standards` §5.5, ARCHITECTURE §7.3 invariant L2).

## Why this exists as a contract and not as a review

Two measurements, both from the TASK 096 corpora.

- **A rewrite costs the document twice.** Prose carrying a rule-4 or rule-6 defect measured 5.1% of
  one corpus's words: 731 of 14,288 across ten task files. Removing it afterwards required reading
  and editing all 14,288. Writing it in register costs nothing extra. Words are quoted rather than
  tokens because tokens depend on the tokenizer, and a ratio that changes with the tool is not a
  measurement.
- **Register quality otherwise tracks the model, not the project.** The same repository received
  specifications of visibly different register from different authoring models. A contract in the
  prompt is what makes the output independent of which model is holding the pen.

A third reason has no number: a reviewer who must re-derive what a sentence claims cannot audit
conformance against it. That cost is paid once per reader, on every reading.

## The role

You write **checkable requirements**, not an argument for them.

A reader who was not in the discussion takes any sentence and states two things: what would have to
be true for it to hold, and where to look. A sentence that fails either test is an essay sentence.
Persuasion, emphasis and memorability are goals of that other genre.

## The six tests — applied per sentence, as it is written

The tests are stated as properties, not as a word list. A property reaches a phrasing the lexicon
has never seen; a word list does not. The tests are therefore the mechanism, and the word lists are
a faster detector for the phrasings already known. This is a design intent, not a guarantee — see
Handoff.

| # | Test | Fails when | Do instead |
| :--- | :--- | :--- | :--- |
| T1 | **Verifiable** | the sentence asserts a judgement the reader cannot check | state the condition and the observable outcome |
| T2 | **Real subject** | the grammatical subject performs an action it cannot perform | name the operation the artefact actually performs |
| T3 | **Resolvable referent** | a noun resolves only inside this author's documents | use the standard name (termhood test below) |
| T4 | **One claim** | one sentence carries a requirement **and** its justification | requirement stays; justification moves under `**Why.**` |
| T5 | **Named severity** | severity is carried by a glyph | use a value from the project's severity vocabulary |
| T6 | **Budget** | the sentence runs past ~15 words on a single claim | split it |

Failing surfaces, per test. Each is written here as code.

**Why code spans.** The scanner masks them, so a document *about* the register is not reported as a
document *in* it. That is the convention for citing a marker **or a glyph** as an example. A span
holds across a line break and stops at a **blank** line, so a citation that must span a paragraph
goes in a fenced block instead.

**This sentence said the opposite until 2026-08-05.** It claimed a span does not cross a line break.
`scan_register.py:526-528` records the fix that made it false, and `mask()` was run in both
directions to confirm it.

**The convention binds a document being written, and reaches no document already filed.** A ledger
record body is preserved byte-for-byte as supplied (`known-issues-format` §8), and an archived
artifact is immutable by doctrine (ARCHITECTURE §7.2). Neither can adopt the convention afterwards.
The scanner still reports their glyphs, and this paragraph is why — no exemption is added to rule 5.
Measured 2026-08-05 over the declared scope: 26 quoted glyphs, 23 in three `provenance: machine`
records and 3 in one archived task.

- **T1** — `наивный`, `неочевиден`, `elegant`, `the main risk`, `a trap`, `unfortunately`.
- **T2** — a gate `blesses`, a deadline `strikes`, a comment `outlives`, a test `goes red`.
- **T3** — `шов`, `бусина`, `плечо`, `seam`, `bead`, `leg`, `head/tail`, `in flight`.
- **T4** — `must … because`, `обязан … потому что`, `должен … иначе`.
- **T5** — `🔴`, `⚠️`, `🆕`. Replace with `warn`, `SEV-2`, `Critical`.
- **T6** — 35 words is the failure bound, not the target. It applies to what a reader reads, so a
  licensed form is not exempt from it: see the first note under Licensed forms.

**T6 is gamed by writing to 35 words.** A corpus whose longest sentence is exactly 35 words was
written for the limit, not to the rule.

Target **under 15 words**. That is the upper end of the five corpus means measured for this skill,
which run 5.8 to 15.4. The low end belongs to the oldest and tersest corpus and is not proposed as a
target. The scanner reports the band under the limit so the tail stays visible.

**The termhood test (T3), stated so it can be applied without asking anyone.** A term is established
if it appears in the project's own `ARCHITECTURE.md`, in a library's public API, or in a standard
the project cites. If its only occurrences are documents written by the same author, it is a
metaphor and the standard name for the thing already exists. Run
`scan_register.py --terms docs/ARCHITECTURE.md` to have the scanner apply this test mechanically.

## Licensed forms — write from these

Choose the form before writing the sentence. No step of the process generates prose and then
repairs it.

| Statement | Form |
| :--- | :--- |
| **Goal** | `<verb> <object> so that <observable state> holds` — one sentence, no scope, no risk |
| **Requirement** | `<subject> <modal> <observable action or state>` |
| **Prohibition** | `<subject> must not <action>` + the input on which the violation shows |
| **Scope** | `In scope: <enumeration>. Out of scope: <enumeration> (<who carries it>)`; past three items, a list |
| **Definition** | `<term> is <genus> that <differentia>` — no example inside the sentence |
| **Algorithm / procedure** | a numbered list, one operation per item, each with its own postcondition |
| **Justification** | `**Why.** <fact> ⇒ <consequence>` — its own block, never inside the requirement |
| **Risk / failure mode** | `<condition> → <observable outcome> (detected by <test or gate>)` |
| **Decision** | `<id>, <date>, <owner>: <what was decided>. Rejected: <alternative> — <measurable reason>` |
| **Open Question** | `<id> — <the question as a question>. Blocks: <what>. Owner: <who decides>` |
| **Test obligation** | `<test id> — <input> → <asserted outcome>` + `; fails when <mutation>` where executable; past the budget, the mutation gets its own line |
| **Derived number** | `<value> = <derivation>; measured <m>; applied <a>` — and which of the two is a ceiling |
| **Deviation** | `<artifact> states "<quoted text>"; this document does <what>; recorded in <ADR entry>` |
| **Table row** | a label per cell: an id, a status, a value, or one clause under 120 characters |

**Notes on four of them.**

- **A form that exceeds T6 becomes a list. The budget is not waived** (WI-12). One item per line;
  each item is then its own block and is measured on its own. Measured: a campaign where the
  contract removed every long *prose* sentence, and the whole remaining tail was this collision — 5
  Scope enumerations and 3 acceptance criteria, and no running prose at all
  ([`measurement-baseline.md`](measurement-baseline.md) §12.2). Before this note the contract
  licensed both forms and stated a budget none of them could meet.
- **Test obligation.** The mutation clause is required only where the test is executable. A
  documentation check has no mutation to name, and demanding one made the form unfollowable for the
  test cases this framework writes most.
- **Table row.** §5.1 owns cell shape. A cell that needs a sentence needs a section below the table.
- **Open Question.** Use it rather than resolving an ambiguity silently. That is the escape hatch
  the rest of the contract deliberately does not provide.

**A statement kind that is not listed** falls back to tests T1–T6 and to the nearest listed form.
The list is the common set, not a closed one; a kind you needed twice belongs in it, so amend this
table under the maintenance rule in SKILL.md §6.

## Worked conversions

Each source sentence is from a real specification and fails a numbered test.

**T1 + T2 — a risk written as a warning.**

> Главная опасность задачи — «доказательство», которое ничего не доказывает.

> **Риск R1** — фейки `makeAdapter` не объявляют `chainSupport`, поэтому после удаления фильтра
> тест краснеет по причине, не связанной с проверяемым свойством. Обнаруживается шагом 3.

Rewritten as the Risk form: condition → outcome → where it is detected. `Главная опасность` fails
T1 (a ranking with no scale); `доказательство, которое ничего не доказывает` fails T2 and stands in
for the rule instead of stating it.

**T3 — a coined metaphor.**

> Шов инъекции строится ровно затем, чтобы проверка стала возможной.

> Параметр `safeFetchImpl` выносится в зависимости эндпоинта — это **точка внедрения зависимости**,
> без которой контрактный тест H3 наблюдает только путь через лимитер.

`Шов` occurs in no `ARCHITECTURE.md`, no public API and no cited standard for this project, so T3
resolves it as a metaphor. English `seam` passes the same test — Feathers' legacy-code terminology
is a citable source — which is why the two languages carry different severities for the same idea.

**T4 — a requirement carrying its own justification.**

> Тест обязан называть адаптеры, потому что список ниоткуда не выводится.

> Тест перечисляет адаптеры поимённо.
>
> **Why.** Список не выводится из кода: он и есть решение OD-5.

**T6 — a licensed form that outgrew the budget.** Not from a specification this time: from
`evals/corpus/A1/with_contract/rep-2.md`, written by a model that had this contract in front of it.
52 words, one sentence, and it follows the Scope form as it was written. It is fenced rather than
quoted for the reason the code spans above are code spans: this document is *about* the defect and
must not be reported as a document carrying it.

```text
**Out of scope:** authentication and API-key issuance (owned by the identity service),
per-endpoint request weighting (deferred, see D-8), paid quota tiers and billing (owned by
commerce), L3/L4 volumetric filtering (owned by the edge provider), retry logic inside published
client SDKs (owned by SDK maintainers), rate limiting of internal service traffic.
```

> **Out of scope.**
>
> - authentication and API-key issuance — identity service
> - per-endpoint request weighting — deferred, D-8
> - paid quota tiers and billing — commerce
> - L3/L4 volumetric filtering — edge provider
> - retry logic inside published client SDKs — SDK maintainers
> - rate limiting of internal service traffic

Nothing is added and nothing is cut. The longest block falls from 52 words to 7, and a reader
looking for one exclusion stops at its line instead of parsing a comma chain. This is the note
above, applied.

**T6 — a 34-word sentence that is two claims.**

> Комментарий, дающий одно число, — дефект приёмки, даже если число верное, потому что R-149 делает
> эти комментарии тем источником, откуда следующая правка кода их копирует.

> Комментарий с одним числом не проходит приёмку.
>
> **Why.** R-149 делает комментарий источником, из которого следующая правка копирует значение.

## What stays verbatim

Established domain terminology, numbers, identifiers, file paths, quoted requirements, legal text,
and every sentence that already conforms. Register changes how a requirement reads, never which
requirement it is. When a sentence is ambiguous about an obligation, surface the ambiguity as an
Open Question — resolving it silently is a larger defect than the register one.

## Handoff

Authoring done → run `scan_register.py` on what you wrote. Findings there are the residue this
contract did not catch, and each one is evidence about the contract:

- a finding the six tests already forbid → the contract held in principle and the author skipped it;
- a finding no test reaches → **the contract is amended**, not just the word list.

That second rule is what stops `data/register-*.json` from growing into a list of yesterday's
phrases. Maintenance procedure: SKILL.md §6.
