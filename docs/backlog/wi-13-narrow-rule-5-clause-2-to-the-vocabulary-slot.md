---
id: WI-13
type: work-item
status: open
opened_at: 2026-08-05
slug: wi-13-narrow-rule-5-clause-2-to-the-vocabulary-slot
effort: M
value: 'removes a false-positive class that is 218 of 223 findings in living framework instructions'
source: 'TASK 101 follow-up: operator question "what is wrong with glyphs"'
provenance: human
component: artifact-formalizer
---

# WI-13 — narrow rule 5 clause 2 to the vocabulary slot

> **Deferred by the operator, 2026-08-05: YAGNI.** Recorded so the measurement is not repeated and
> so the concept is settled before anyone acts on it. Nothing in this record is applied.

> **Adversarially reviewed 2026-08-05, fresh context, and the review changed the record.** Two of
> the four proposals are now marked **not adopted** with their figures, and the measurement in §2 is
> marked **invalid for the purpose it was taken**. §7 records what was verified. Read §7 before §2.

Every glyph in this record sits in a code span. That is the convention the record proposes for
citing one, applied to itself.

## 1. The rule as it ships

`formalization-guide.md` rule 5, two clauses:

1. Severity is a named value. `` `🔴` `` is not a severity; `warn`, `SEV-2`, `Critical` are.
2. A glyph that carries no severity at all — `` `🆕` `` for "new since the last revision" — is diff
   metadata and does not belong in the specification either.

Clause 1 is not in question. This record is about clause 2.

## 2. What clause 2 actually reports

Measured 2026-08-05 over the tracked `.md` files, `emoji_severity` findings only.

| Population | Living framework instructions | Ledgers |
| :--- | ---: | ---: |
| `` `✅` `` / `` `❌` `` as a two-valued opposition (`DO` / `DO NOT`) | 170 | 25 |
| Heading decoration (`` `🌐` `` `Web/API`, `` `🛡` `` `Smart Contracts`) | 25 | 0 |
| A glyph quoted inside a record reporting glyph severities | 0 | 23 |
| A glyph beside a severity that is already named (`` `🔴` `` `CRITICAL:`) | 2 | 0 |
| A glyph standing **in place of** a named severity | **0** | **0** |
| **Total** | **223** | **49** |

`` `🆕` ``, the example clause 2 states, occurs in exactly two files: the two that define the rule.
It has no occurrence in the wild.

**The clause fires 218 times in living instructions and 48 times in the ledgers on populations its
own text does not describe.** Its stated target has no instance in this corpus.

## 3. The settled concept

Decided by the operator, 2026-08-05.

| Population | Verdict |
| :--- | :--- |
| A glyph in place of a value from an ordered, declared vocabulary | **defect** — keep detecting |
| A glyph beside a severity already named | **not a defect** — no rule, and no detector |
| A glyph quoted inside a record about glyphs | **not a defect** |
| `` `✅` `` `DO` / `` `❌` `` `DO NOT` — a two-valued local opposition | **not a defect** — legibility, and long-standing in several skills |
| Heading decoration | **not a defect** — legibility |

**Why the ordered vocabulary is the property.** Severity is ordered, project-wide and consumed by
tooling: the ledgers key on it and `/heal-issues` selects on it. A glyph is absent from every
declared vocabulary, so nothing can rank two of them and no gate can check one. `DO` against
`DO NOT` is unordered, local to its section, and read by nobody's tooling.

## 4. Proposed changes, none applied

**P1 — the detector needs a vocabulary to compare against, and has none.** This is the crux and it
is unsolved. The narrowed rule reports a glyph that occupies a **vocabulary slot**, and
`scan_register.py` cannot see a slot: it matches pictographic code points. Rule 6 already faced this
and answered it with `--terms`, which hands the scanner the project's established terminology.

*Proposal:* `--severities <file>`, mirroring `--terms`. A glyph within N characters of a word
declared there is reported; a glyph elsewhere is not. `known-issues-format` already declares the
severity and status vocabularies, so the file exists.

*Unresolved:* the operator's concept in §3 rules that a glyph **beside** a named severity is not a
defect, and that is the case `--severities` detects most easily. What `--severities` must detect is
a glyph where the word is **absent** — the harder direction, and one a proximity test cannot express.
This record does not resolve it.

**P2 — widen the unconditional exclusion set.** `` `✅` ``, `` `❌` ``, `` `☑` ``, `` `☒` `` move from
"excluded inside a table cell" to excluded everywhere, joining `` `✓` `` and `` `✗` ``. Evidence: 195
occurrences, none in a severity position. `measurement-baseline.md` §6 already records the identical
argument for `` `✓` `` and `` `✗` ``.

*Cost, stated:* a project where `` `❌` `` means "blocker" loses detection. This is a judgement about
this corpus, and another project needs its own measurement.

**P3 — heading decoration leaves rule 5.** A glyph in a heading carries neither severity nor
revision state. If a project wants it gone, that is `documentation-standards`, not register.

**P4 — the citation convention, no code change.** A record citing a glyph puts it in a code span.
The masker already blanks those, so the 23 ledger findings disappear with no rule change at all.
`authoring-contract.md` states the same convention for markers and does not state it for glyphs.

**P5 — clause 2 keeps only revision state.** `` `🆕` `` for "new since the last revision" belongs to
version control. That is the one part of clause 2 the measurement leaves standing, and it has zero
occurrences, so it is a rule against a defect nobody has committed here.

*Open question:* a rule with no corpus occurrence is what `measurement-baseline.md` §4 declines to
adopt ("a rule that never fires is prose read for nothing"). Whether clause 2 survives at all is
therefore open.

## 5. Order of work, when it is taken up

`SKILL.md` §6 rule 2 governs: this is a finding about what rule 5 **means**, not about a missing
pattern. Therefore:

1. amend `formalization-guide.md` and `authoring-contract.md`;
2. record the §2 figures in `measurement-baseline.md`;
3. change `data/register-*.json` and `scan_register.py`;
4. add a battery case per changed behaviour, and a false-positive control for each population §3
   rules out.

TASK 101 §7 excludes every one of those files, so this is not that task's work.

## 7. Review outcome, 2026-08-05

Reviewed by `critic-logic` in a fresh context. The critic had no execution tool; every finding below
was re-verified here by running the command shown. Findings the review raised and this verification
could not sustain are omitted.

### 7.1 The §2 measurement is invalid for the purpose it was taken

**The zero is survivorship bias.** §2 reports "a glyph standing in place of a named severity: 0" and
§1 concludes the rule's target does not occur. The class existed and was removed by the commit
immediately before this work began.

```sh
git show 7708e2f^:System/Agents/03_task_reviewer_prompt.md | grep -n '🔴\|🟡\|🟢'
```

```text
44:- **🔴 CRITICAL (BLOCKING):** Missing use cases, contradictions, ...
45:- **🟡 MAJOR:** Incomplete descriptions, missing scenarios, vague criteria.
46:- **🟢 MINOR:** Typos, formatting, style.
```

Three glyphs constituting a severity taxonomy with no severity word on the line — the class §2
measures at zero. It stood in five prompts and three subagent wrappers until `7708e2f` closed WIR-2
and WIR-11 on 2026-08-04. The zero is evidence the rule **worked**, recorded as evidence the rule is
pointless.

**The corpus is largely outside the rule's declared scope.** `documentation-standards` §5.5 scopes
the contract to "any TASK, ARCHITECTURE, PLAN or task file". No review checklist scans
`.agent/skills/**`, `System/**` or `.claude/**`. 218 of the 223 findings §2 leans on therefore come
from documents no gate reaches.

### 7.2 P2 is a decision that was already taken, the other way, with larger figures

`docs/tasks/task-099-...md:230-234`:

> **D2, 2026-08-04, orchestrator: rule 5 exempts `✓`/`✗` everywhere and keeps `✅`/`❌` in-table-only.**
> Rejected: exempt every status glyph everywhere — erases 704 of 1050 rule-5 findings and turns
> `TC-ADV-13` red.

P2 is that rejected option, re-proposed with a smaller sample, citing `measurement-baseline.md` §6 —
the record of the rejection — as if it endorsed the widening. Verified by execution on a throwaway
copy with `TICK_GLYPHS` widened to `✓✗✅❌☑☒`:

| Measured | Value |
| :--- | ---: |
| `emoji_severity` findings, shipped scanner, 577 files | 757 |
| Same, with P2 applied | 173 |
| **Erased** | **584** |
| Battery | `188/191`, red on `TC-ADV-13`, `TC-ADV-13a`, `TC-100-07` |

P2's stated evidence was "195 occurrences". The true blast radius is three times that, and REG-18
exists because this precise widening erases findings while every gate reports green.

**P2: not adopted.** Figures recorded so it is not re-proposed a third time.

### 7.3 The class §3 keeps is undetectable where it lives

`known-issues-format` writes severity as a **frontmatter key** (`severity: SEV-2`). `mask()` blanks
frontmatter before any rule runs.

```python
>>> scan_register.mask("---\nid: X-1\nseverity: 🔴\nstatus: open\n---\n\nProse.\n")
# the glyph does not survive
```

Verified: `False` — the glyph is gone before rule 5 sees the document. A narrowed rule 5 would
detect the keep-class in prose, where nobody writes it, and be blind to it in frontmatter, where the
vocabulary actually is. **This blocks §3 until it is solved, and §4 did not name it.**

### 7.4 P1 is not implementable as stated

`--terms` tests the finding's own surface against a blob (`apply_terms`). A proximity test needs the
opposite direction: the document's neighbouring words against a *vocabulary*, and `load_terms`
returns an undifferentiated blob. Handing it `known-issues-format/SKILL.md` would declare every word
of a prose document a severity term. There is no machine-readable vocabulary file in the skill.

It also breaks invariant L2: the vocabulary source is English, so a Russian document would never
match, and rule 5 would fire differently by language.

**P1: not adopted**, for the reason §4 already gave — the detectable direction is the non-defect
direction.

### 7.5 §5's order of work names an impossible step

Step 3 says "change `data/register-*.json`". Rule 5 has no data-file surface:
`RULE_KIND = {2: "marker", 4: "maxim", 6: "metaphor"}` (`scan_register.py:59`), and `_validate_entry`
rejects any other rule number. A rule-5 change is a code change only.

`SKILL.md` §6 rule 2 governs **under**-coverage — a defect no test forbids. This record is
**over**-coverage. §6 has no rule for narrowing, which is a gap worth closing on its own.

### 7.6 A defect outside this record, found by the review

`authoring-contract.md:54` stated "a code span does not cross a line break". The scanner masks
across a line break and stops at a **blank** line. Verified both directions; corrected in place,
since a shipped document asserting a falsehood about its own tool is worse than the scope boundary.

### 7.7 What survived the attack

The **property** in §3 — ordered, declared, machine-consumed — is sound and its mechanism is
verified: an unknown severity string ranks 0 (`severity_rank("WAT") == 0`), so a glyph in that slot
degrades silently rather than failing. That sentence is the part of this record worth keeping.

### 7.8 Disposition

1. §3's property statement stands.
2. P1 and P2 are **not adopted**, with the figures above.
3. Before anything is scheduled, re-measure over the **declared** scope (`docs/TASK.md`,
   `docs/ARCHITECTURE.md`, `docs/PLAN.md`, `docs/tasks/`, `docs/issues/`, `docs/backlog/`) at a
   commit **before** `7708e2f`, and state both scope and commit.
4. §7.3 is the blocker. A narrowing that leaves the keep-class undetectable replaces 218 out-of-scope
   firings with zero firings, which `measurement-baseline.md` §4 calls prose read for nothing.

## 6. Reproduction

```sh
git ls-files -z '*.md' > /tmp/md.z
python3 - <<'EOF'
import io, json, contextlib, sys, collections
sys.path.insert(0, '.agent/skills/artifact-formalizer/scripts')
import scan_register
files = [f for f in open('/tmp/md.z','rb').read().decode().split('\0') if f]
live = [f for f in files if f.startswith(('.agent/skills/', '.agent/workflows/',
                                          'System/', '.claude/'))]
out = io.StringIO()
with contextlib.redirect_stdout(out):
    scan_register.main(live + ['--json'])
hits = [w for w in json.loads(out.getvalue())['warn']
        if w['kind'] == 'emoji_severity']
print(len(hits), collections.Counter(w['match'] for w in hits).most_common())
EOF
```
