# TASK 096 — Artifact register: formalize how TASK/PLAN prose is written

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 096 |
| Slug | artifact-register-formalization |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator report, 2026-08-03 |
| Reference skill | `enterprise-project-calc-bootstrap/skills/text-formalizer` (construction only) |
| Archive name | `task-096-artifact-register-formalization.md` |

**Operator statement.** Task and plan descriptions have become hard to read: jargon-heavy and
padded with reasoning that distracts the reader. Two clarifications followed. First, jargon is
mostly appropriate — the requirement is relaxed. Second, the language of an artifact stays the
author's choice; the subject is formalization, not English.

<!-- contract:rtm -->

## 1. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
| :--- | :--- | :--- | :--- |
| R1 | Register rules MUST be derived from measurement of the artifact corpus, not from impression. | Yes | Baseline script; per-era counts; §1.1 evidence |
| R2 | Candidate rules the measurement refutes MUST be recorded as rejected, not silently dropped. | Yes | Rejected-candidates table in the skill |
| R3 | The framework MUST NOT mandate the language of any artifact. | Yes | No language rule added; §5.5 states language-independence |
| R4 | Rules MUST apply to any language the artifact is written in. | Yes | Per-language data files; language-independent structural checks |
| R5 | The normative short form MUST live in `documentation-standards`. | Yes | New §5.5, under 40 lines; cross-references §5.1/§5.2, restates neither |
| R6 | A TIER 2 skill MUST carry the full guide, the worked example, and the scanner. | Yes | `artifact-formalizer`, built via `skill-creator` |
| R7 | Rules MUST be data, extensible without editing the scanner. | Yes | Schema `register-rules/v1`; `data/register-{ru,en}.json` |
| R8 | The scanner MUST be advisory: it reports and never fails a phase. | Yes | Exit 0 on findings; 2 broken instrument; 3 usage error |
| R9 | Authoring surfaces MUST route the author to the rules before the first sentence. | Yes | Three prompts + three templates, each a pointer (see §6, D-1) |
| R10 | The scanner MUST have an acceptance battery covering schema and detection. | Yes | `selftest_scan.py`, 128 cases, run in CI |
| R11 | `System/Docs/` MUST record the new skill and the changed skills. | Yes | `SKILLS.md` rows; `CHANGELOG.md` entry |
| R12 | The scanner MUST NOT match inside code spans, fenced blocks, or link targets. | Yes | Masking pass before matching; selftest case per construct |

### 1.1 Details by ID

**R1 — baseline measurement.** Prose was segmented per block (a list item is its own block) and
sentences split inside blocks. Counts below are from that pass.

| Corpus | Files | Mean words/sentence | >35 words | Evaluative markers /100 lines |
| :--- | ---: | ---: | ---: | ---: |
| agentic `task-03x/04x` (oldest) | 21 | 5.8 | 0.0% | 0.1 |
| agentic `task-06x/07x` | 33 | 12.1 | 2.6% | 0.6 |
| agentic `task-095` (newest) | 9 | 14.1 | 3.8% | 1.4 |
| onchain `task-00x` (oldest) | 48 | 13.6 | 2.9% | 1.2 |
| onchain `task-012` (newest) | 10 | 15.4 | 3.6% | 2.1 |

Evaluative-marker density rises monotonically in both repositories: 14× across the agentic corpus
and 1.75× across the onchain corpus. Mean sentence length rises 2.4× in the agentic corpus. Both
signals move the same direction in two independently authored repositories, which is why they
become rules.

**R1 — a first measurement was wrong and was discarded.** The initial pass split sentences over the
whole file. Consecutive `- [ ]` checklist lines carry no terminal punctuation, so they glued into
single pseudo-sentences of 101 to 167 words. Those figures measured the checklist format, not the
prose. The block-aware pass above replaced them.

**R2 — refuted candidates.** Four properties were expected to show degradation and did not.

| Candidate | Measured | Verdict |
| :--- | :--- | :--- |
| Bold density | agentic 9.1 vs 30.7 /100 lines (newest vs older) | Improved. No rule. |
| Em-dash density | agentic 12.2 vs 22.8 /100 lines | Improved. No rule. |
| Emoji density | agentic 0.0 vs 8.7 /100 lines | Improved. No rule for agentic. |
| Long table cells | agentic newest 22% of cells over 120 chars | Real, but already covered by §5.1 |

Emoji rose in the onchain corpus (2.8 vs 1.6 per 100 lines) on a small base. It is recorded as
`info` severity, not `warn`.

**R2 — §5.1 is an enforcement gap, not a missing rule.** `documentation-standards` §5.1 already caps
a table cell at 120 characters and one sentence. The newest agentic artifact violates it in 21 of
95 cells. No new rule is written for this; the scanner reports the existing one.

**R6 — skill name.** `artifact-formalizer`, not `text-formalizer`. The reference skill keeps its
name in its own repository. Two skills sharing a name with different rule sets would eventually be
synchronized into each other and one rule set would be lost.

**R7 — what is taken from the reference skill.** Its construction: data-driven rules, a validate-
then-scan script, severity `warn`/`info`, a guide holding a worked before/after example, and a
selftest. Its content is not taken. The reference dictionaries translate engineering slang into
business vocabulary for customer-facing documents, which the operator has ruled out of scope here.

**R8 — why advisory.** `documentation-standards` §4 already records the mechanism it measured: a
gate that fails on correct documents is how gates get switched off. Register rules are heuristic and
will produce false positives, so they report.

The second mechanism — an author writing *to* a bound rather than to the rule — is this skill's own
measurement and is recorded in `artifact-formalizer/references/measurement-baseline.md` §8. An
earlier revision of this paragraph attributed it to §4, which never said it.

**R5 — reachability.** `documentation-standards` is loaded in the Development phase by the tier
table. TASK and PLAN are authored by the Analyst and the Planner, which load neither it nor the new
skill. R9 is therefore the only path by which these rules reach their audience, and §5.5 alone
would leave them unread.

**R12 — measured, not assumed.** This TASK was scanned against its own proposed rules. It returned
six evaluative-marker hits. All six sit inside backticks, where the markers are cited as examples
rather than used. The reference scanner matches raw lines and would report all six. Masking code
spans, fences and link targets before matching is therefore a requirement, not a refinement.

<!-- contract:problem -->

## 2. Problem

Artifact prose has drifted from specification into essay. Two properties carry the drift, and both
were measured in two repositories that were authored independently.

Sentences have lengthened. Evaluative and rhetorical markers have multiplied: `ровно`, `именно`,
`precisely`, `exactly`, `waste`, `honest`. These words assert a judgment the reader cannot check,
in a document whose purpose is to state checkable requirements.

Two further habits are visible in the samples but are not yet counted: a rule stated as an aphorism
rather than as a rule, and argumentation braided into the sentence that carries a requirement. The
scanner cannot detect either. They belong to the reading pass.

No authoring surface currently states a register rule. The Analyst prompt, the Planner prompt and
both templates are silent on how prose should read.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — Analyst drafts a TASK.**
*Actor:* Analyst. *Precondition:* the prompt and template carry the register rules.
*Main:* the author writes short declarative requirements in the language of their choice; the
artifact conforms without the author having loaded `artifact-formalizer`.
*Postcondition:* register no longer depends on the author remembering a skill exists.

**UC-2 — Author checks a finished artifact.**
*Actor:* any pipeline role. *Main:* `scan_register.py docs/TASK.md` lists sentences over the length
bound, evaluative markers, and cells that breach §5.1. Exit code is 0.
*Alternative A:* the artifact is in a language with no rule file — structural checks still run,
marker checks report zero, and the script says so.
*Alternative B:* a rule file is malformed — exit 2, naming the fault, without scanning.

**UC-3 — Author formalizes a drifted artifact.**
*Actor:* any pipeline role. *Main:* scan, replace every `warn` hit, judge `info` hits, then read the
whole text once against the guide for the two defects no pattern detects.

**UC-4 — Team adds a rule.**
*Actor:* operator. *Main:* a new entry is added to `data/register-<lang>.json`. The scanner is not
edited. A new language is a new data file.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| # | Criterion | Verification |
| :--- | :--- | :--- |
| A1 | Every rule shipped traces to a row in the §1.1 measurement. | Review each rule against the table. |
| A2 | The four refuted candidates appear in the skill as rejected, with their figures. | Grep the skill. |
| A3 | No artifact-language rule exists anywhere in the framework. | Read every rule statement this task adds (grep is secondary, see below) |
| A4 | Scanner exits 0 on an artifact full of findings. | Selftest case. |
| A5 | Scanner exits 2 on a malformed rule file and names the fault. | Selftest case. |
| A6 | A new rule requires no edit to the scanner. | Selftest adds an entry via a fixture data file. |
| A7 | Every authoring surface routes the author to the contract before writing | Read the three prompts and the three templates |
| A8 | This TASK and its PLAN pass their own scanner at zero `warn` | Thresholds fixed from §1.1 before the run (see below) |
| A11 | §5.5 states no rule already stated by §5.1 or §5.2. | Read the three sections together; each property has one owner. |
| A9 | All existing skill and root tests stay green. | `bash scripts/tests/run_tests.sh`; `pytest`. |
| A10 | `documentation-standards` §5.5 stays a short form, not a second copy of the skill | `wc -l` before and after; deviation recorded below |


**Notes on four criteria.**

- **A3** — grep is a secondary check, never the proof. A rule constraining language can be written
  without any of the words a grep would look for.
- **A8** — a failure is resolved by editing the prose, never by moving a threshold. Moving a
  threshold to obtain a green scan inverts the rule the threshold exists to enforce.
- **A10 — deviation, recorded 2026-08-04.** The criterion said "under 40 lines"; §5.5 grew by
  **47**. The extra content is the detector-coverage table with its per-rule recall limits, which
  did not exist when A10 was written.

  The adversarial review showed that table to be load-bearing. A reader who does not know a detector
  is partial reads its zero as a pass. Trimming it to meet a line budget would be writing for the
  gate, which §5.5 itself forbids, so the criterion is amended rather than met.
- **R9 — deviation, recorded 2026-08-04.** R9 originally required every surface to carry the rules
  inline "so a conforming artifact needs no skill load". Execution produced five inline copies of
  one rule set, which is five places for it to drift; the adversarial review found the copies had
  already begun to. The surfaces now point at
  `artifact-formalizer/references/authoring-contract.md`, which is loaded in every authoring phase
  (`skill-phase-context`). The cost is one file read per authoring phase; the benefit is a single
  source. ARCHITECTURE §7.3 records the placement.
## 5. Out of Scope

- Rewriting archived artifacts. Rules apply on write.
- Any jargon or terminology dictionary. The operator relaxed this requirement.
- Any rule about which language an artifact uses.
- `task_id_tool.py` parent-versus-sub-task ID collision. Found while archiving TASK 095: the tool
  read `task-095-01…09` as occupying ID 095 and returned 096 for the parent. Filed to the ledger,
  fixed separately.
- Bold, em-dash and emoji density rules. Refuted by measurement (§1.1 R2).

<!-- contract:open-questions -->

## 6. Open Questions

**Q1 — sentence-length bound (blocking the scanner step).** The measurement gives a distribution,
not a threshold. The oldest agentic corpus averaged 5.8 words per sentence, which is terser than
these documents need. A bound of 35 words for `warn` is proposed as the starting value, tunable in
the data file. The PLAN MUST close this before the scanner is implemented; a step that starts with
the bound open will hard-code a guess.

**Q2 — scope of the evaluative marker list.** `именно` and `exactly` are sometimes load-bearing, as
in "read in exactly one place". The proposed treatment is `info` severity for those two and `warn`
for markers that carry no such use.
