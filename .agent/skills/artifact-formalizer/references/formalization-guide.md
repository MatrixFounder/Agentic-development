# Formalization guide — Mode B, rewriting a document that already exists

Mode A is [`authoring-contract.md`](authoring-contract.md), and it is the cheaper order. This guide
is for a document already written. Apply it in the document's own language: the rewrite never
translates anything.

## The six rules

1. **One claim per sentence.** Over 35 words is the failure bound. It is measured, not chosen: every
   corpus mean sits between 5.8 and 15.4 words, which is the target. A document whose longest
   sentence is exactly 35 words was written for the bound, and the scanner says so.
2. **No evaluative markers.** A word asserting a judgment the reader cannot check does not belong
   in a document of checkable requirements. `важно понимать`, `наивный`, `obviously`, `elegant`.
3. **Reasoning is separated from requirement.** The requirement states what must hold. Its
   justification goes under a `**Why.**` lead-in or into Notes. A reader auditing conformance must
   be able to read requirements without reading arguments.
4. **A rule is stated as a rule.** No maxim, no personification. A sentence in the shape of
   `the deadline strikes only what has not yet cost money` is memorable and unimplementable.
5. **Severity is a named value.** `🔴` is not a severity. `warn`, `SEV-2`, `Critical` are. A glyph
   that carries no severity at all — `🆕` for "new since the last revision" — is diff metadata and
   does not belong in the specification either.
6. **A private metaphor is not a term.** Established terminology stays verbatim — `singleflight`,
   `deadline`, `throttle`, `RTM`, `дедлайн`. A metaphor the author coined for this document has no
   shared referent, and a reader outside the conversation cannot resolve it. «Шов инъекции» →
   «точка внедрения зависимости». «Нога платного вызова» → «платный подвызов».

**Telling the two apart.** A term is established if it appears in the project's own
`ARCHITECTURE.md`, in a library's public API, or in a standard the project cites.

If its only occurrences are in documents written by the same author, it is a metaphor, and the
standard name for the thing exists. `scan_register.py --terms docs/ARCHITECTURE.md` runs the string
half of that test for you. It downgrades the findings that pass, and never suppresses them.

**Why downgrade rather than suppress.** A metaphor that spread into the architecture document also
satisfies a string test while remaining a metaphor.

**The same idea can be a term in one language and a metaphor in the other.** English `seam` has a
citable source in Feathers' legacy-code terminology; the Russian calque «шов» has none. The shipped
lexicons therefore carry different severities for it, and that asymmetry is deliberate.

## What a pass touches

**Rewrite:** over-long sentences, evaluative markers, aphorisms standing in for rules, reasoning
braided into a requirement clause, emoji used as severity, metaphors the author coined for this
document.

**Leave verbatim:** established domain terminology, numbers, identifiers, file paths, quoted
requirements, legal or contractual text, and every sentence that already conforms. Over-rewriting
introduces errors that were not there.

**Never change:** what the document requires. Register changes how a requirement reads, never which
requirement it is. If a sentence is ambiguous about an obligation, surface the ambiguity as a
question — do not resolve it silently.

## Worked example

A goal section from a task specification. Russian in, Russian out — the rewrite never translates.

**Before:**

> Сделать проверяемым **условие корректности** D4 п.2: дедлайн бьёт только по тому, что ещё не
> стоило денег. Задача маленькая по объёму кода и самая рискованная по швам — два из трёх швов §0.3
> плана закрываются здесь.

**After:**

> **Цель.** Сделать проверяемым условие корректности D4 п.2: отмена по дедлайну не затрагивает
> подвызовы, за которые уже списаны кредиты.
>
> **Объём.** Здесь создаются две из трёх точек внедрения зависимостей, перечисленных в §0.3 плана.
>
> **Why.** Параметр `safeFetchImpl` нужно вынести в зависимости эндпоинта: пока вызов идёт через
> статический импорт, контрактный тест H3 наблюдает только путь через лимитер и не видит вторую
> половину гарантии.

What each change removes:

| Before | After | Defect removed |
| :--- | :--- | :--- |
| дедлайн бьёт только по тому, что ещё не стоило денег | отмена не затрагивает подвызовы, за которые уже списаны кредиты | Rule 4 — a maxim replaced by a testable condition |
| маленькая по объёму, самая рискованная | (deleted; scope stated as a count) | Rule 2 — judgments the reader cannot check |
| «швы», «шов инъекции» | точки внедрения зависимостей; вынести параметр в зависимости | Rule 6 — a private metaphor replaced by the standard name |
| one sentence carrying goal, size and risk | three labelled blocks | Rule 3 — reasoning moved under `**Why.**` |

The rewrite is not shorter for its own sake. Counted: 34 words before, 59 after — 31 if the
`**Why.**` block is excluded, since that block is new material rather than a rewrite of the source.
Every clause is now verifiable by a reader who was not in the discussion, which is the property
being bought.

### What this example also demonstrates about coverage

When this rewrite was first performed, it was applied to this section and to **no other section of
the same document**. The metaphor «шов» survived seventeen more times across the task set it came
from, including in section headings and acceptance criteria.

Rewriting the fragment that was quoted at you is the characteristic failure of Mode B. It is why
the scanner emits a per-section worklist (`--sections`).

## The specification test

For each rewritten sentence: **can a reader who was not in the discussion verify this claim from
the document alone?** If it needs context that lives in the team's heads, it is not done.

## Order of work

1. `scan_register.py <file> --sections --terms docs/ARCHITECTURE.md`.
2. Read `DETECTORS` and `DIAGNOSTICS` **first**. A zero from a dead detector is not a measurement,
   and a clean scan flagged `PRESSED AGAINST THE LIMIT` is a document written for the gate.
3. Fix every `warn`. Judge each `info`.
4. Walk **every** section in the worklist for the recall gaps in SKILL.md §5. The detectors for
   rules 3, 4 and 6 are partial by construction, and a section with zero findings is not a section
   that was read.
5. Re-scan. A remaining `warn` is fixed in the prose. Moving a threshold to obtain a green scan
   inverts the rule the threshold exists to enforce.
6. Feed the residue back: SKILL.md §6 says when a finding obliges a new lexicon entry and when it
   obliges an amendment to the authoring contract.
