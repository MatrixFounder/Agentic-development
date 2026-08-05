---
id: WI-16
type: work-item
status: open
opened_at: 2026-08-05
slug: wi-16-state-claims-carry-no-required-referent
effort: M
value: 'a claim that a task is not in the code names nothing that fails when the task lands'
source: 'onchain-analytics WI-38, owner-routed to this repository 2026-08-05'
provenance: human
component: 'sweep skill + artifact-management + 3 registries + 9 workflows + 2 register skills'
---

# WI-16 — A claim about code state carries no required referent

Routed here from onchain-analytics, record
`docs/backlog/wi-38-no-gate-reads-architecture-status-markers.md`, which measured the drift and
named this repository as the place the change belongs.

> **Fifth statement.** Three adversarial reviews rejected the four before it. The decision has been
> stable since the first; what failed each time was the evidence apparatus around it. §9 records
> which mechanisms were refuted, so nobody re-proposes one. Every figure below is pinned, and the
> pins are stated once in §2.

## 1. The gap

`PLANNED (T-012, not in code as of 2026-08-03)` is readable. It names its task and its date, and a
reader can say what it claimed and when. What it does not name is anything that **fails** when
T-012 lands. The claim went false the next day and nothing observed the transition.

The missing element is a referent. The consequence is silent expiry.

[`documentation-standards`](../../.agent/skills/documentation-standards/SKILL.md) §4.1 binds the
adjacent case, and only that one:

> A quotation of the pre-edit state MUST carry an explicit revision identifier (commit, tag,
> version), otherwise it reads as a claim about the current state.

Its population is **references** — positional against nominal. A status marker is neither, and a
bare date is not among the licensed revision identifiers. `artifact-formalizer` leaves the same
gap: its T1 tests whether a sentence is checkable, and this one is. The 14 licensed forms in
`references/authoring-contract.md` contain no row for a claim about build state.

## 2. Measurement

**All figures in this record are measured at these revisions**, not at a later working tree:
agentic-development `fddf209`, onchain-analytics `b1f7a7b`, Universal-skills `9a8258f`,
n8n-lazy-loading-skills `8809f54`. Re-derive with `git -C <repo> show <rev>:<path>`.

Lines matching `\b(PLANNED|LANDED|SHIPPED|BUILT)\b|not in code|not yet in code` over
`docs/ARCHITECTURE.md` plus `docs/architectures/`:

| Repository | `docs/architectures/` | Lines |
| :--- | :--- | :--- |
| agentic-development | absent | 0 |
| onchain-analytics | present | 28 |
| Universal-skills | present | 2 |
| n8n-lazy-loading-skills | present | 0 |

Word boundaries are load-bearing: without them `BUILTIN_WHITELIST` matches and Universal-skills
reads 3. The onchain-analytics figure is 28 lines and 29 occurrences: one line carries two
markers.

**The vocabulary is not a framework form.** The same pattern over `architecture-format-core`,
`architecture-format-extended`, `architecture-design` and `artifact-management` returns 0 lines.
onchain-analytics introduced it locally, so a gate keyed on it would fire only where it was
invented.

## 3. Why a vocabulary gate does not ship

WI-38 recommends a gate on the words `PLANNED`/`TBD`/`not in code`/`will be` next to a `T-0NN`
identifier, failing when `ARCHITECTURE.md` marks that task `BUILT`.

**It depends on the natural language of the document it judges**, and
`agentic-development/docs/ARCHITECTURE.md` §7.2 states invariant **L1** against exactly that.
onchain-analytics writes architecture in English and its ledger in Russian.

**It starts red on a corrected corpus.** Simulated over
`onchain-analytics/docs/architectures/system-architecture.md` with adjacency scoped to the line —
`grep -nE '(PLANNED|TBD|not in code|will be)' | grep -E 'T-0[0-9][0-9]'` — it produces four
findings and none is true. One is a quotation of a deleted banner; three are prose about the
corrections. That one file carried nine `PLANNED` lines before the fix pass. Eight were corrected
and the ninth is kept deliberately.

`documentation-standards` §4.2 measured the same outcome over 84 references and states the
consequence: a gate that fails on correct documents is switched off. Bare §4.x and §5.x ordinals
below name that skill; this record's own sections are always written as "§N" with a noun.

`documentation-standards` §4.3 is **not** an argument here; a draft used it and was wrong. §4.3
governs how a gate addresses a *section*, and a gate scanning body text addresses none.

## 4. Options

| # | Option | Catches the transition | Language-neutral | Cost |
| :--- | :--- | :--- | :--- | :--- |
| 1 | WI-38's vocabulary gate | yes | no | M |
| 2 | WI-38's marker date + task against `git log` | yes | no | L |
| 3 | **Sweep keyed on the task id, wired like the Retro** | yes | yes | M |
| 4 | **Authoring rule — the claim names what falsifies it** | no | yes | S |
| 5 | Anchor-keyed gate on a declared state-claim block | only where declared | yes | M |

Option 2 is the closest of WI-38's to the failure mode and fails on the same L1 ground: locating
"the marker" to check its date requires the vocabulary. Option 5 is graded "only where declared"
because §4.3 makes an anchor optional on read and its fallback branch is Option 1.

## 5. The change

### 5.1. Option 3 — one definition, wired by enumeration

| Artefact | What it gains |
| :--- | :--- |
| a new **TIER 2** skill | the whole sweep procedure |
| [`artifact-management`](../../.agent/skills/artifact-management/SKILL.md) | one delegation line |
| `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` | the protocol named in each Global Protocols line |
| nine workflows | the two-part reference the Retro already uses |
| `System/Docs/SKILLS.md` | one row |

**Why a TIER 2 skill.** The Retro's home, `run-feedback`, is TIER 2. `artifact-management` is TIER 0
and loads in every session; a procedure needed once at run end does not belong in that budget.
Delegation is that skill's established genre — it already delegates to `skill-archive-task`,
`known-issues-format`, `architecture-format-core` and `skill-safe-commands`.

**Why all three registries.** Each is a real file carrying exactly one Global Protocols line, and
`framework-upgrade` §3.1 names all three. Editing one leaves the protocol unbound on two vendors.

**Why enumeration is the wiring and not the definition.** No Global Protocol here has ever bound a
workflow that does not name it. Measured: 17 of 23 workflows carry the Retro's two-part reference,
and an 18th names it only to exclude a run mode. `skill-archive-task` appears in 8,
`skill-update-memory` in 1.
A draft proposed declaring the protocol and editing no workflow; that mechanism does not exist.

**Selection criterion**, stated so the set can be falsified: code lands in the workflow **and** no
`calls[]` edge hands that code to a wired workflow, directly or transitively. Two exclusions follow
from it and are named so a reader does not stop on them:

- `05-run-full-task` commits at its step 3 and is absent — it runs each task through
  `03-develop-single-task`, which sweeps before it returns. `vdd-enhanced` and `base-stub-first`
  are absent for the same reason, one edge further out.
- `04-update-docs` is absent because no code lands there, although its step 3 asks the question
  this record exists to answer. `iterative-design` is absent for the same reason — it writes
  drafts. `full-robust` is absent because it hands code to `vdd-multi`, `security-audit` and
  `03-develop-single-task`, all wired.

Two members need their edges explained, because both carry a `calls[]` edge to a wired workflow:

- `vdd-05-run-full-task`'s edge to `vdd-03-develop` carries `partial: "Step 3"`, so it borrows the
  persona overlay and not the sweep; its own Step 2A builds and 2D merges.
- `vdd-adversarial` is in the set because `vdd-enhanced` §4.4 documents orchestrator-applied fixes
  that never enter the developer loop, so its edge to `03-develop-single-task` does not hand that
  code off.

| Workflow | Sweep step site |
| :--- | :--- |
| `03-develop-single-task` | before the Retro step |
| `vdd-03-develop` | before the Retro step |
| `vdd-05-run-full-task` | inside step 2, after the 2D merge, once per task |
| `vdd-multi` | before the Retro step |
| `vdd-adversarial` | before the Retro step |
| `security-audit` | before the Retro step |
| `framework-upgrade` | a new §5, before the Fallback section |
| `light-02-develop-task` | before §3 item 1, the staging step |
| `heal-issues` | inside step 3, before its `Commit:` line |

The reference is two-part. The first part is a **prose** blockquote where the Retro's claim line
sits: directly under the frontmatter, before step 1. It names the protocol and states that an outer
run already sweeping suppresses this one. The shape is the Retro's; the content is not,
because the Retro's line executes `run_feedback.py claim` and this protocol ships no such
instrument, so the blockquote states the rule rather than enforcing it. The second part is a
numbered step at the run's last code-affecting boundary.

Three sites are not "before the Retro", each for a measured reason:

- `light-02-develop-task` stages and commits at its §3, and `heal-issues` commits inside its
  step 3. In both the sweep precedes the commit: a correction made after it lands outside
  the commit that caused it. For `heal-issues` that also matters because its own precondition is
  a clean `git status --porcelain`, which an uncommitted correction would block on the next run.
- **`heal-issues` has no Retro step.** It names the Retro only in prose, to scope one run mode, so
  its site is named against its own numbered steps. Its step-2 exhaustion path commits and exits
  without reaching step 3; that path carries no sweep, and the run reports that.
- `framework-upgrade`'s §5 is a recovery procedure rather than a run step, so the boundary is §4.

**Why not `skill-archive-task`.** Owner decision, 2026-08-05.

### 5.2. What the sweep does

1. **Identifier, by source.** The wired workflows do not all name the task the same way, so the
   rule names the source rather than one filename:

   | Source | Wired workflows | Identifier |
   | :--- | :--- | :--- |
   | `docs/tasks/task-<N>[-<M>]-<slug>.md` | `03-develop-single-task`, `vdd-03-develop`, `vdd-05-run-full-task` | the stem's numeric group `<N>` |
   | `docs/TASK.md` meta block | `framework-upgrade`, `security-audit`, `light-02-develop-task`, `vdd-adversarial` | the `Task ID` value |
   | the run's own unit | `heal-issues`, `vdd-multi` | the issue ID, the target path, or the diff |

   `vdd-05-run-full-task` iterates task files and sweeps **once per task**, which is why its site
   is inside the loop rather than before the Retro. `vdd-adversarial` runs after `vdd-enhanced`
   Phase 1 has produced and validated `docs/TASK.md`, so a task ID is available to it on the path
   §5.1 admits it for.
2. **Match.** An anchored alternation over the prefix set and over both number forms. The prefixes
   are `T-<n>`, `task-<n>` and `TASK <n>`, the three §6 item 7's detector reads. The numbers are
   the three-digit zero-padded form and the unpadded one, so `012` matches `T-012` and `T-12`,
   and neither matches `T-120` or `T-0120`.
   The prefix set is load-bearing: onchain-analytics writes `T-0NN`, and this repository writes
   `TASK 102` and `task-102-…`. A stem carrying no numeric group yields no identifier and takes
   item 3.
3. **No identifier is a result, not a skip.** A run whose unit is an issue ID, a path or a diff has
   nothing the architecture corpus keys on, because markers key on task identifiers. Such a run
   sweeps nothing and prints that it did not, naming which unit it had.
4. **Scope.** `docs/ARCHITECTURE.md`, plus `docs/architectures/` where the project runs index mode.
   That condition is owned by `architecture-format-core`.
5. **Report.** Each matched line with its file and line number. **Zero matches is a result and is
   printed.**
6. **Resolve.** Confirm or correct each line before the run closes.

**Blocking on being run, advisory on its verdict.** An absent block is a finding; a printed list the
operator confirms is a pass, and a printed list never fails the run. onchain-analytics WI-32
established the first half — the Cycle Brief in `vdd-adversarial`, whose absence is itself a
finding. §4.2 establishes the second.

**Nesting is stated, not enforced.** An outer run that owns the sweep suppresses the inner one. The
Retro's equivalent rule has an instrument, a `claim`/`release` pair; this item ships none, and §7
records the consequence.

### 5.3. Option 4 — the authoring rule

**Normative text** — a new `documentation-standards` **§4.5**:

> A sentence that asserts a task identifier is or is not in the code MUST name the observation that
> falsifies it: a symbol, a test id, or a `path:line`. A date or a commit alone does not satisfy
> this. Both stay true of their revision while the claim about the present goes false.

**Obligation surface** — one row in `artifact-formalizer/references/authoring-contract.md`'s
licensed-forms table, stating the form **in full**. The rule binds an author in the **Architecture**
phase; TIER 1 loads `artifact-formalizer` there and loads `documentation-standards` only in
Development, so a row that cross-references §4.5 sends that author to a file they do not have. All
14 existing rows are self-contained: none cross-references another file.

**Population: assertion, not quotation.** The rule binds a sentence that **asserts** build state,
not one quoting or describing it — which is why the four sites §3 calls false findings are out of
population. Nineteen lines pair a marker with a task identifier and carry no `path:line`; four are
those sites, leaving **15**. `SHIPPED` claims are included: a revert makes them false too.

**The inherited 15 are not retrofitted.** The rule binds what is written after it lands.

**A state claim in a table cell puts its referent below the table**, per `documentation-standards`
§5.1's escape hatch.
`onchain-analytics/docs/ARCHITECTURE.md:10@b1f7a7b` is a metadata cell far over that cap. It
violates the rule independently of this item, and §4.5 must not be read as licensing a referent
added inside one.

**The pair is ungated.** `check_contract_sync.py` compares `known-issues-format` against its two
seed templates and nothing else. Drift between §4.5 and the contract row is uncaught after landing.

### 5.4. Option 5 — deferred

`<!-- contract:state-claim -->` gets a row in §4.4, the marker declares itself, and the gate
resolves the declared referent. Filed only on the residue Options 3 and 4 leave, per §6 item 7.

## 6. Acceptance

1. The sweep skill exists and states all six items of §5.2, the run it fires on, and the nesting
   rule. The procedure is stated **there and nowhere else**. `validate_skills.py --root .` goes from
   N to N+1 skills, all passing.
   Fails when — a workflow restates the procedure instead of referencing it, or the skill's
   frontmatter declares a tier other than 2, which would defeat the budget argument in §5.1.
   *`init_skill.py` is the mandated creation path; its shipped template does not pass
   `validate_skill.py` unquoted, so de-templating is part of authoring.*
2. `artifact-management` names the skill in one delegation line and carries no copy of the
   procedure.
   Fails when — the delegation line is absent, or the procedure appears in both places.
3. All three of `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` name the protocol.
   Fails when — one names it and another does not.
4. All nine workflows of §5.1 carry the two-part reference at the stated site, and the skill has a
   row in `System/Docs/SKILLS.md`.
   Fails when — the reference is present in eight of the nine.
5. The sweep prints its list even when empty, states that an absent block is a finding, and states
   that a printed list never fails the run.
   Fails when — a run with zero matches produces no block.
6. §4.5 states the obligation with `MUST` and names the three satisfying observations; the
   `authoring-contract.md` row states the same form in full.
   - §4.5 states that it adds an obligation and does not relax §4.1 for quotations.
   - It names what it does not reach: an unpinned referent that resolves and is wrong, a document no
     change touches, and a pinned referent, which `check_positional_refs.py` skips entirely.
   Fails when — the row and §4.5 state different obligations.
7. **Trigger for Option 5 — a delta, and not a condition of closing this item.** Run the detector
   on the landing commit for `B0` and 60 days later for `B1`, in every repository where the detector
   returns a non-zero `B0`. Today that is **onchain-analytics** at 19 and **Universal-skills** at 1;
   agentic-development has no `docs/architectures/` and returns 0. Option 5 is filed if `B1 > B0`
   in any of them and a reading of the new lines confirms them.

   ```bash
   grep -rnE '\b(PLANNED|LANDED|SHIPPED|BUILT)\b|not in code|not yet in code' \
     docs/ARCHITECTURE.md docs/architectures/ 2>/dev/null \
     | grep -E '\b(T-[0-9]+|task-[0-9]+|TASK [0-9]+)' \
     | grep -vE '`[^`]+\.[a-z]+:[0-9]+' | wc -l
   ```

   **The detector reads one of the three satisfying observations** — it excludes a backticked
   `path:line` and nothing else, so a compliant marker referencing a test id still counts. That
   is why the trigger requires reading the new lines, not the count alone. It counts population, not
   residue: it returns **19** at `b1f7a7b`, from markers predating this item, so a level test would
   file Option 5 on day one.

   **This item closes on items 1 to 6.** Item 7 is carried by a follow-up work-item opened at
   landing.

## 7. Bound

**What can fail.** The sweep fails when it did not run, or when its list was printed and left
unresolved. No CI job is added.

**What never fails a run.** No check rejects a document for its vocabulary, and no status marker is
prohibited.

**What this does not fix.**

- **Nothing verifies the wiring.** No gate checks that a workflow authored later carries the
  reference, and none explains the 17 / 8 / 1 spread across the three existing protocols.
- **Nothing verifies discharge.** A reference in a workflow is not evidence that a run swept. The
  Retro has the same gap: `claim`/`release` is mutual exclusion, not an obligation ledger.
- **Two of the nine wired sites are inert by construction.** `heal-issues` and `vdd-multi` take
  §5.2 item 3: their unit of work is an issue ID, a path or a diff, and the architecture corpus
  keys on task identifiers. Both run the sweep and both print that they swept nothing. A run that
  lands code without a task identifier therefore leaves every marker unchecked, and the wiring says
  so rather than implying coverage.
- A build-state claim carrying **no** task identifier; both options key on one.
- A stale marker naming a task other than the one just landed.
- A referent that resolves and is wrong, and a pinned referent, which the checker never opens.
- A hand edit made outside any run.

The first two are the subject of a separate item — see §8.

## 8. Out of scope

- **The wiring gate and the discharge ledger.** A protocol registry with a validator over every
  terminal workflow, plus a journal recording discharge, is a separate work-item at cost L. It would
  answer the 17 / 8 / 1 question for all protocols rather than for this one.
- **`skill-archive-task`.** Owner decision: its job is rotation.
- **WI-38's ENFORCED/DECLARED option** — one pair of numbers in one project's source. It belongs
  to onchain-analytics and is currently held by no open record there: WI-38 is `dropped` and
  WI-37 is `done`.
- **A machine-readable task-status registry.** None exists, so WI-38's first acceptance criterion is
  not implementable as written. Option 3 does not need one.
- **Genuinely archived artifacts.** The living architecture corpus is in scope and gets corrected in
  place.
- **Propagating any of this to the three consumers.** `.agent/skills/` is a real directory in each,
  with per-skill symlinks — 47, 57 and 0, the last keeping 54 real directories. A skill that does
  not exist yet has no link, so reaching a consumer is a manual step either way. Registries and
  workflows are per-repo files.

## 9. Related and refuted

- `onchain-analytics` WI-38 — the source. **Its counts do not reconcile**: it states fifteen false
  claims and nine markers while its own per-file breakdown sums to 22, and three figures inside one
  document disagree. Re-derived at `6af4b19`: nine `PLANNED` lines in `system-architecture.md`, six
  of them stale markers inside the banner's declared scope, plus seven across three other files
  under `docs/architectures/`; `security.md` carries none
  against WI-38's one. This record uses the re-derivation, not WI-38's figures.
- `onchain-analytics` WI-32 — the precedent for the blocking rule in §5.2.
- `onchain-analytics` WI-24 and WI-28 — the two gates whose population does not reach this kind of
  sentence.
- [WI-15](wi-15-skill-md-6-has-no-rule-for-narrowing-a-rule.md) — the rule that a contract change
  ships with a measurement. §6 item 7 applies it to Option 5.

**Mechanisms refuted before this statement**, kept so none is re-proposed. No draft survives in a
commit; this list is what the reviews reported.

| Proposal | Why it failed |
| :--- | :--- |
| A rule satisfied by a pin | The population already carries dates; §4.1 exempts pins from re-checking |
| Exempting the corpus as archived | `docs/architectures/` is a living document, corrected in place |
| Arguing from §4.3 | §4.3 governs section addressing, not content matching |
| Three develop workflows, step inlined | Code lands in nine places; one step was unreachable from `/vdd-develop-all` |
| A Global Protocol binding without wiring | No such mechanism; each protocol here is named in every workflow it binds |
| The rule in `documentation-standards` alone | The Architecture phase does not load it |
