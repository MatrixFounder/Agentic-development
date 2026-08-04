[Русская версия](CHANGELOG.ru.md) | [English version](CHANGELOG.md)

<!--
## [Unreleased]

### 🇺🇸 English
#### Added
- ...

#### Changed
- ...

#### Fixed
- ...
-->

## 🇺🇸 English Version (Primary)

### **v3.24.0 — artifact register: measured rules for how specification prose reads**

Task and plan prose had drifted from specification into essay. Measured across two independently
authored corpora (~12,200 lines): evaluative-marker density rose **14×** in this framework's tasks
and **1.75×** in a downstream project's; mean sentence length rose **2.4×** (5.8 → 14.1 words).
Both signals move the same direction in corpora written by different hands, which is why they
became rules.

#### **Added**
- **`artifact-formalizer` (TIER 2, split-tier)** — two modes. **Mode A** is
  `references/authoring-contract.md`: six per-sentence tests and fourteen licensed statement forms,
  loaded before the first sentence of an artifact. **Mode B** is the advisory scanner
  (`scan_register.py`) plus a reading pass. All six register rules reach a detector; rules 3, 4 and
  6 carry declared recall limits. Every run probe-tests each detector, so a zero is reported next to
  what the detector saw. Exit 0 on any findings, 2 on a broken instrument or a dead detector, 3 on a
  usage error. Per-language marker data (`register-rules/v1`, extensible with no code edit) and a
  128-case selftest.
- **`documentation-standards` §5.5 "Register"** — the normative short form, 33 lines.
- **ARCHITECTURE §7.3, invariant L2** — the framework constrains how an artifact reads, never
  which language it is written in. Structural checks are language-independent; lexical rules are
  per-language data. A language with no rule file still gets structural checks and says so.
- The rules are carried inline by **three** authoring prompts (Analyst, Architect, Planner) and both
  artifact templates, because those roles load neither `documentation-standards` nor the new skill.
- **Validation Evidence is bounded.** `validate_skill.py` now warns when the section carries an
  investigation rather than a verdict; the bound is `quality_checks.max_validation_evidence_lines`
  in both copies of `skill_standards_default.yaml`, with no literal in the code — an absent key
  means the standard is unconfigured, not that the checker invents a number. Default 12 is twice
  the repo median of 7. Two existing skills are flagged (`run-feedback` 18, `skill-spec-validator`
  29) and left for their owners. `skill-creator`, `skill-enhancer` and `SKILL_TEMPLATE.md` state
  the rule: detail moves to `references/`, nothing is deleted.

#### **Refuted by measurement, and shipped as non-rules**
Bold density (9.1 vs 30.7 per 100 lines), em-dash density (12.2 vs 22.8) and emoji density
(0.0 vs 8.7) all **improved** and get no rule. Seven generic AI-writing tells measured **zero** on
this corpus and were not adopted. Over-wide table cells are real (22% of cells in the newest
artifact) but already owned by §5.1 — the scanner surfaces that rule rather than adding one.

#### **Fixed — ARC-1 and ARC-2, both closed**

**ARC-1 — a committed task could be silently renumbered.** The id machinery was already correct;
it was unreachable. `get_parent_archive_ids()` distinguishes a parent archive from planner
sub-tasks, but only on the `--proposed-id` path, and **every documented invocation omitted it** —
Step 3 Option A literally showed `generate_task_archive_filename(slug="task-slug")`, and Step 4
said to set the task's id to whatever the filename got. Step 3 now passes the Meta-block id with
correction off; Step 4 asserts instead of assigning; `allow_renumber` defaults to `False` in
`archive_protocol.py` and `tool_runner.py`. Three adjacent defects closed with it: `archive_task()`
parsed the meta block only when the *slug* was missing (so ARC-1 reproduced through the automated
path); `parse_task_meta()` keyed on the English literals `Task ID` and `Slug`, filing any
non-English TASK.md as `untitled`; and Step 5 had **no** collision guard while `SKILL.md` claimed
one — `shutil.move` silently overwrote a planner sub-task file.

**ARC-2 — archiving broke relative links, in three shapes, not one.** New
`.agent/tools/rebase_links.py`, invoked from both moves. The rule is arithmetic —
`relpath(normpath(join(old_dir, target)), new_dir)` — because the `../` → `../../` substitution the
issue proposed fixes **zero** of the 45 remaining instances, which carry no `../` at all. Existence
became the guard rather than the trigger: a link broken before the move is never "fixed" by
guessing, and one that resolves only from the new home is left alone, which is also what makes a
re-run a no-op.

The sharper half: **a mutable slot is not a file identity.** `**Parent**: [docs/PLAN.md](../PLAN.md)`
inside `task-063-07` meant *task 063's* plan and resolves today to whatever plan is live. Rebasing
the path would have preserved the wrong thing and reported success, so the rewriter takes a slot
map consulted **before** any filesystem probe — which is also the only way it works inside
`archive_plan()`, where `docs/TASK.md` is already gone.

Corpus: **45 broken links → 4**, plus 19 silent mis-resolutions re-pointed. The 4 survivors are
broken where they were authored, not by any move, and are reported rather than guessed at.

**The tests protecting all of this ran nowhere.** `framework-gates.yml` lists test files
explicitly and named neither `test_task_id_tool.py` nor `test_archive_protocol.py` — 59 tests, no
CI. Both are now in the list, with `test_rebase_links.py` (36 cases). The second review round found
the same hole one level up: `tests/run_tests.py` was invoked by no job, and its `load_tests` is what
pulls in the whole of `tests/installer/`. Added as its own step. CI now runs **320** pytest +
**302** unittest.
- A `KNOWN_ISSUES.md` entry cited "TASK 096" as having fixed VAL-2; no such task existed. Replaced
  with the commit that did.

#### **Second review round — what the first pass closed too early**

Re-verified by execution rather than by reading, which is what turned these up.

- **ARC-1 was closed while four of five documented call sites still taught it.** The fix landed in
  `skill-archive-task` and `tool_runner.py`; `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` and
  `ORCHESTRATOR.md` still showed the bare `task_id_tool.py <slug>` form — and three of those are
  read at session start, before the skill loads. Measured: with `task-095-01..03` present and no
  parent, the bare form returns **096** where the protocol form returns **095**. All four corrected;
  `02_analyst_prompt.md` now calls the tool instead of eyeballing `docs/tasks/`. Pinned by
  `TestBareInvocationShadowsTheParentId` — one test per form, so the difference cannot be
  "simplified" away.
- **`schemas.py` advertised `allow_correction: default true`** to the model while the dispatcher
  used `False`, so an agent could omit the argument believing it had enabled the renumbering ARC-1
  forbids. Now `false`, pinned against the dispatcher.
- **`rebase_links.py` could not see 3 real links.** Its code-span mask closed a backtick run
  against the *first character* of a longer one and could span blank lines, so one unbalanced
  backtick blanked every link after it. The tool would have reported success while leaving them
  broken — the exact under-fix it exists to prevent. One-line fix; measured to recover exactly
  those 3 and to keep masking all 13 links that are syntax examples inside code spans. The looser
  `](target)` regex was **kept**: tightening it changes 2 findings corpus-wide, both `#anchor`
  targets already dropped as absolute.
- `.agent/archive/` (rollback backups written by `/framework-upgrade`) is now ignored rather than
  leaving `git status` dirty after every upgrade.

#### **Third round — closing WI-11, and the HIGH that closing it uncovered**

WI-11 held the MED/LOW tail. Its own closing rule was *execute each entry, do not read it*, and
that rule paid for itself: **six of ten entries confirmed, four refuted** — and rewriting the
lowest-stakes entry of all, a stale `Example Flow`, then *running* it exposed a HIGH.

- **Step 5.5 exited `1` — "a link regressed" — on the protocol's own happy path.** The conservation
  law filesystem-probed every rewritten target including `SLOT_RESOLVED` ones, but a slot map is a
  **forward reference**: Step 5.5 names `docs/plans/plan-NNN-x.md`, which Step 7 creates
  afterwards. Read literally, the protocol told the agent to stop on success. `SLOT_RESOLVED` is
  now exempt from the conservation law — a declared identity is the caller's assertion, not
  something to police mid-sequence — while a target not yet on disk still prints as
  `[SLOT_PENDING]`, so a typo'd map stays visible. **This finding was reported in round 1 and
  refuted in error**: the refutation ran the tool *without* `--slot`, which is not the documented
  command.
- **`artifact-formalizer` scanner precision**, each reproduced before being fixed: an escaped pipe
  hid an over-wide cell entirely; `U+2028` shifted every reported line number, because
  `str.splitlines()` breaks on separators that editors and `grep -n` do not; the same `--rules`
  file named twice doubled every finding; a document opening with a **horizontal rule** had its
  title and first block masked away as frontmatter and scanned to **zero**; and `e.g. Capital`
  split one sentence into two, halving the measured length at 12 corpus sites.
- **Refuted, and shipped as pinned non-defects.** "A stray backtick masks the rest of the line" —
  the pairing is CommonMark-correct and a genuinely unmatched backtick masks nothing. "Decimals
  split sentences" — `1.5 Beta` has no whitespace after the period, so the rule never fired.
  `__pycache__` hygiene — already ignored, 0 tracked. Exempting `etc.`/`т.д.` alongside `e.g.` was
  rejected on measurement: both are 0 here and genuinely end sentences elsewhere, so exempting
  them would trade a false split for a false glue.
- `skill-archive-task` → **2.0** (the protocol's mandatory steps changed), and its `Example Flow`
  rewritten to the real 11-step sequence.
- `selftest_scan.py` is now a CI step. CI runs **324** pytest + **302** unittest + the selftest.

> **State at time of writing.** Both data files carry the required `probe` field, the scanner
> probe-tests 18 detectors across two languages on every run, and the CI step is green
> (`selftest_scan.py` 128/128, `--probe` 18/18). A fresh-context adversarial review of the v2.0
> candidate returned 65 findings, every one reproduced by execution before it was accepted;
> `references/measurement-baseline.md` §10 records the four that defeated a headline design claim,
> including three that produced a silent zero while the run reported every detector live.

The three rounds share one shape: **round 1 shipped a guard that depended on the caller
remembering it, round 2 verified a fix only where it was written, round 3 found that a refutation
had measured the wrong command.** Each round ended with every gate green.

#### **Two detector defects, found by measurement**
The first corpus baseline was **discarded**: sentences were split over the whole file, so runs of
`- [ ]` lines glued into pseudo-sentences of up to 167 words — it measured the checklist format,
not the prose. The same defect reappeared for `*Actor:* X. *Main:* Y.`, caught by running the
scanner against the specification that defined it. Both are pinned as regressions. A silent zero
and a broken instrument look identical.

### **v3.23.0 — every retry loop states its own bound, and the gate that checks it can fail**

Design spec 095 Phases 2 and 3. Eleven retry loops across the corpus had **no numeric bound in the
workflow that owned them** — the VDD family had systematically dropped the caps its non-VDD twins
carry, and `framework-upgrade` had two unbounded `GOTO` loops. Nine now state a bound and an
escalation path where they live; two stay `null` deliberately (one judgment-terminated, one
HITL-gated). On top of that, all 23 workflows declare a machine-readable loop contract and a new CI
gate checks the declaration against the prose. Gates: **417 pytest + 58 subtests** (CI list ∪ local
`tests/`, +24 / +23), **302 `run_tests.py`** (+24), **177 installer `unittest`** (unchanged).

#### **The bounds, where they execute** (Phase 2)
`vdd-01-start-feature` ×2, `vdd-02-plan`, `vdd-03-develop`, `vdd-05-run-full-task`,
`framework-upgrade` ×2, `vdd-adversarial`, `security-audit` — nine loops, ~20 lines, seven files.
Each gets `max 3` (operator decision D1) plus a written escalation path; an exhausted counter is an
escalation, never an approval. `full-robust` spelled two bounds in words (`once`, `one` retry) and
now carries the canonical `(max 1)` *appended* beside them — never a rewrite of the sentence.
`framework-upgrade`'s two gates both read *"If Audit fails, GOTO Step 2"* without saying whose
Step 2; both are section-local and now say so.

`System/Docs/WORKFLOWS.md` held a third copy of every bound plus a framework-wide *"the Doer gets
**2 attempts**"* that D1 contradicts head-on. It is now split into Standard = 2 / VDD = 3, and its
call map lost two edges `vdd-enhanced` does not contain.

#### **`contract:` frontmatter and `check_loop_contract.py`** (Phase 3)
All 23 workflows declare `contract.loops[]` and `contract.calls[]` — 25 loops, 20 call edges,
generated from one inventory so a bound cannot differ between two files by hand. Call edges were
derived mechanically from the corpus across all three call spellings, not copied from prose.

`System/scripts/check_loop_contract.py` implements R1–R7, R9, R10, R12, R13, R14, warn-only. The
rule it exists for is **R3**: the number in frontmatter must equal the number in the prose that
executes it, resolved through a `<!-- loop:<id> -->` anchor with a declared search window.

**The negative fixtures are the deliverable, not the suggestion.** The validator's first run against
the live corpus printed `0 error(s), 0 warning(s)` — the exact shape of a gate that checks nothing,
which this repository has shipped once already. `tests/fixtures/loop_contract/` now trips every rule
(20 distinct codes), `test_every_phase3_rule_fires` fails if any rule stops producing a finding, and
the CI job goes red **if the R3 fixture ever passes**.

#### **Anchors conform to `documentation-standards` §4.3/§4.4** (D9)
That section's rule is explicit: *adding a gate that reads an anchor absent from the registry is a
defect*. R3 and R10 are such a gate, so `loop:<id>` gained a registry row, all 25 ids are lowercase
kebab-case, and the non-heading placement rule is written down — nearly every loop site sits inside
a numbered step list, where a comment at column 0 splits the list.

#### **Fixed: Markdown links were resolved against the wrong base**
`check_positional_refs.py` resolved Markdown link targets against the repository **root**. Links are
document-relative: a review at `docs/reviews/x.md` linking `../../.agent/foo.md#L1` names a repo
file and is correct — the gate reported it `ESCAPES_ROOT`, and because that kind is deliberately a
warning, the misresolution never surfaced. Links now resolve against their own document; code spans
stay repo-relative. The fix immediately exposed **three genuinely broken links** in `docs/TASK.md`,
dead in any editor, hidden for as long as they existed.

#### **Fixed: a checker whose tests ran in CI while the check never did**
`check_positional_refs.py` and its 89 unit tests already existed; nothing ever pointed the checker at
a document. 39 unresolvable references had accumulated across `docs/`. Now wired into
`reference-integrity` over the whole tree: **0 errors across 495 references in 241 documents**.

The 36 archived findings were **not** stale records needing pins, as first assumed — 33 of 35 resolve
correctly once the *path* is disambiguated. They were unaddressable, not wrong: a bare `SKILL.md` +
line number matches 47 files here. Pinning them would have marked 33 correct references unchecked
permanently, since a pinned reference is skipped.

#### **Fixed: `tests/test_loop_contract.py` was not in the CI list**
Added to `run_tests.py`'s curated suite in Phase 3 but not to the `tooling-tests` pytest line, so the
negative fixtures guarding the validator did not run in CI at all. Now in both.

#### Not shipped, and why
**Phase 4** (`--strict` in CI) is a one-word change waiting on its gate: *Phase 3 green for one full
framework-upgrade cycle*. **Phase 5** (Component C) is gated by the §7.1 entry questions, five of
which are now answered on record in §7.4 — and two of those answers point *away* from building it:
`override: required` is used by 0 of 25 loops, and neither of the two caller binds changes a number.

### **v3.22.2 — a trailing slash is a type assertion, and the default install is the other type**

Reported from a downstream `install.sh install --vendor antigravity` run: the generated
`.gitignore` did not actually ignore `.agentic-development`. Fixing it surfaced a second, larger
defect — the installer had no way to *deliver* a `.gitignore` fix to an existing project. Both are
fixed here. Gates: **393 pytest + 35 subtests** (CI list ∪ local `tests/`, +3 from the regressions
below), **278 `run_tests.py`** (+3), **177 installer `unittest`** (+2).

#### **The rule was right about the name and wrong about the kind**
`build_block_body` emitted `/.agentic-development/`. In gitignore syntax a trailing slash is a
*directory-only* assertion, and git does not follow symlinks — it records one as a blob of type
symlink, i.e. a file. The installer's **default** mode makes `.agentic-development` exactly that
symlink (`framework_root.ensure_agentic_dev`, `mode='symlink'`), so the pattern described a shape
the default install never produces and the entry stayed visible to `git status`.

Reproduced before touching anything, then again after, in both modes:

| mode | on disk | before | after |
|------|---------|--------|-------|
| `symlink` (default) | symlink | `?? .agentic-development` | `.gitignore:5:/.agentic-development` |
| `copy` | real dir | ignored | `.gitignore:5:/.agentic-development` |

Dropping the slash is strictly wider and costs nothing: the slashless form matches directories,
files, and symlinks, so it covers both modes with one rule.

**Vendor-independent.** It reads as an Antigravity report because that is where it was seen, but
the line is a hard-coded constant shared by every profile. The other symlinked entry, `/System`,
was already correct — every component rule is generated as `/{path}` without a slash. The defect
was one hard-coded string, not the generator.

#### **The assertion that let it ship**
Two tests covered the line as `assertIn("/.agentic-development/", body)` — a *substring* check,
which passes against both spellings and so could never tell them apart. They are now exact-line
membership (`assertIn(..., body.splitlines())`), plus a dedicated
`test_framework_rule_has_no_trailing_slash`. Verified red-then-green: reverted to the buggy string,
watched all three fail, restored the fix.

#### **Not changed, deliberately**
The same report asked whether `GEMINI.md` should be gitignored too. It should not, and the reporter
was right to flag their own uncertainty. `GEMINI.md` is in `bootstrap.PROTECTED` — project-owned,
never overwritten even under `--force`; the installer only maintains a managed block inside it and
tells the author to "edit outside the markers only". Ignoring it would drop the author's own text
out of version control and leave a fresh clone with no bootstrap file. The existing split is the
intended one: pure-framework artifacts (`CLAUDE.agentic.md`, `CLAUDE.local.md`) are ignored,
project-owned ones (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) are tracked.

#### **A fix nobody can receive is not shipped — `update` now refreshes `.gitignore`**
Checking the upgrade path turned up the worse half. `update_gitignore` had exactly **one** call
site — step 8 of `install`. `switch` inherits it by delegating to `_cmd_install`, but `update`
never touched `.gitignore` at all. So the rule above, once fixed, would have reached **no existing
project**: the natural "pull the framework, run `update`" upgrade left the broken rule in place
indefinitely. Reproduced on a project installed from a deliberately-buggy build, then confirmed
fixed on the same setup.

`_cmd_update` now refreshes the block. Two independent reasons it belongs there: linking and
`--prune` change which entries are project-local, so the `!`-exception list drifts on every update;
and the block body itself changes when the framework is upgraded.

A hand-edited block raises `IntegrityError`, which must **not** abort `update` — the symlink
re-sync has already happened, and dying half-done would be worse than the stale rule. It warns,
keeps the exit code green, and preserves the edit; `install --force` remains the deliberate way to
overwrite a customised block. Both paths are covered by new tests
(`test_update_refreshes_stale_gitignore_block`, `test_update_survives_hand_edited_gitignore`),
verified red-then-green by removing the refresh and watching exactly those two fail.

**Upgrade note.** Either `install` or `update` now delivers the fix; `update` is enough. A project
that already committed the symlink must still untrack it once:
`git rm --cached .agentic-development`. Note the ordering constraint for anyone upgrading from a
build older than this one: the `update`-side fix only exists *after* you have this version, so the
first hop still needs a re-run of `install` if your installed copy predates it.

### **v3.22.1 — a contract declared universal must live where every path can read it**

From WI-29, filed by the same downstream project from the same `/vdd` run as v3.22.0: two
subagents stalled for **600 s each**, one of them visibly spending its turn trying to launch
`run_audit.py` — a script its role has no `Bash` to execute. Gates: **390 pytest + 35 subtests**
(CI list ∪ local `tests/`), **275 `run_tests.py`**, 45/45 skills, prompt-refs / security-lint /
workflow-smoke green, `doctor.py` preflight passed.

#### **The reported fix was already in the file, and had been for seven weeks**
WI-29 proposed adding the branch "if Bash is unavailable, record `scan: NOT RUN` and review
manually" to `skill-adversarial-security` SKILL.md. `git blame` puts that branch at `e9a2360`,
**2026-06-10** — seven weeks before the stall it did not prevent. Recorded rather than quietly
skipped, because applying it would have re-applied an existing fix and closed a record on a change
that changes nothing. A proposed fix is a hypothesis; the first step is to check whether it is
already there.

#### **Added — `skill-parallel-orchestration` §2.4 (v3.7 → v3.8)**
§7 has always claimed that "all universal concepts (§2–§6) — including merge rules **and the
evidence contract** — apply on every path". §2 defined roles, layers and the three-phase protocol,
and no evidence contract: it existed only inside `vdd-multi` Step 1.0. A claim with no referent.
§2.4 now states both halves where §7 says they live — the **orchestrator** runs anything that must
be executed to be known and injects it, writing `NOT RUN (<reason>)` for what it did not run; the
**teammate** uses what it is given, reports a missing block as a finding, and — the half nobody had
written down — records `NOT RUN (no execution tool in this role)` for a command its role cannot run
**instead of spending the turn attempting it**.

#### **Fixed — `/vdd` phase 4 spawned read-only teammates with neither half**
`/vdd` does not run `vdd-multi`. It runs `vdd-adversarial.md`, which since v3.22.0 carries a Cycle
Brief and *mentions* the evidence block by analogy without ever requiring one. Step 2a now defines
it, on **every** entry including the first cycle. `vdd-enhanced` §4 gains **item 8** — the caller's
obligation to gather evidence before spawning — **appended**, not inserted, for the same reason
items 6–7 were: spec 095 cites these ordinals.

#### **Fixed — `security-audit` §1–§2 (v3.6 → v3.7), `skill-adversarial-security` §3 (v1.4 → v1.5)**
§1's Red Flags said **"EXECUTE the script"** with no branch for a role declared without an execution
tool, and §3's escape hatch was an italic footnote *after* the fenced command. The agent followed
the instruction it met first. §2 now opens with the check "can you execute at all"; §3 leads with a
four-row branch table and puts the command below it. §1 gains a third Red Flag against the failure
mode that is worse than the stall — **inventing the output of a scan you did not run**. The
`security-audit` H1 heading was bumped along with the frontmatter: that skill's own docs record
version sprawl as lesson L10.

#### **Fixed — the hand-maintained donor had drifted behind its own generated copies**
`wrappers_manifest.json` calls Claude Code "the validated reference/donor … INTENTIONALLY NOT
generated here (it stays hand-maintained)". Since Task 081 the generated `.gemini` / `.codex` /
`.cursor` critic wrappers have each carried "You are read-only: you cannot run run_audit.py … never
fabricate scanner output". The hand-maintained donor carried none of it — and the donor is the only
one that runs. All three `.claude/agents/critic-*` wrappers now state it.

#### **Fixed — an instruction to fabricate a security gate**
`.claude/agents/security-auditor.md` read "mock results if the environment restricts execution",
contradicting "never fabricate scanner output" in three neighbouring files. Replaced with
`scan: NOT RUN (<reason>)`. This is the **only behaviour change** in the release: a role that
previously produced a fabricated scan section now produces an honest gap.

#### **Not shipped, deliberately**
The second stalled subagent in that run was `task-reviewer`, and this does **not** explain it.
Neither its prompt nor either of its TIER-1 skills mandates a script, and a grep for `python3`
across all eleven `Bash`-less roles finds nothing addressed to it. Recording it as fixed because its
sibling was is the exact error WI-29 itself objects to when it refuses to file both cases under the
already-closed WI-7. Filed downstream as its own open work-item instead.

#### **Corrections after review — seven of this entry's own defects**
An adversarial pass over this release found seven things wrong with it. All are recorded rather than
quietly amended, because every one is the genre the release is about.

- **`NOT RUN` satisfied every exit bar in the framework, and was refused by none.** The contract as
  first written made a *missing* block a finding while a block reading `Tests: NOT RUN; Scan: NOT
  RUN` passed — and `skill-adversarial-security` §7 explicitly blessed it. That trades a loud
  600-second stall for a **silent unverified pass**, which is strictly worse because nothing
  downstream can see it. `NOT RUN` now licenses continuing a review, never concluding one: it leaves
  the bar unmet in §2.4, in both critic skills' §7, in `vdd-adversarial` (skill and workflow) and in
  all six critic wrappers.
- **The one behaviour change shipped a third state into consumers that had two.** `security-auditor`
  reports `scan: NOT RUN` in prose while its machine-readable footer still had only
  `PASS`/`FAIL` — so a scan-less audit was indistinguishable from a clean one, and both consumers
  (`full-robust` §3's "the scan exits clean AND…", `security-audit.md`'s "re-run until clean")
  resolved the undefined branch in favour of passing. Footer gains `scan_status`, `NOT_RUN` forces
  `INCOMPLETE`, and both consumers now say so.
- **Item 8 was INSERTED, not appended** — it sat above item 7 in the file, and three documents
  (both changelogs and the audit) claimed otherwise. Since CommonMark renumbers ordered lists in
  document order, the item labelled `8.` rendered as 7, which is exactly the breakage the
  append-don't-insert rule exists to prevent. Now genuinely last.
- **"Nothing addressed to `task-reviewer`" was a true search of the wrong space.** The grep covered
  role *definitions*; the sibling defect lives in a **loaded skill**, and TIER-0
  `skill-session-state` §3 tells every role — including the three read-only reviewers — that it
  **MUST** run `update_state.py`. That is the exact mechanism §2.4 names, live for
  `task-reviewer`/`plan-reviewer`/`architecture-reviewer`. §3 now opens with "can you execute at
  all", and the three wrappers say they are read-only. (The other half of that finding did *not*
  hold: the prompts tell reviewers to write a review file, but each wrapper already overrides that
  with "do NOT write it yourself".)
- **The version bump honoured L10 at 2 sites of 5.** `audit/__init__.py` — which L10's own remedy
  made the source of truth — plus `run_audit.py`'s CLI header and `System/Docs/SKILLS.md` were left
  behind, so the scanner would have printed `v3.5` for a skill documented as 3.7. All five now agree.
- **"All three generated wrappers already carried the read-only line" was 2 of 3.** The manifest's
  `evidence` string for `critic-logic` was empty, so its `.gemini`/`.codex`/`.cursor`/`.antigravity`
  wrappers carried nothing. Worse, fixing the donor first left the **donor ahead of the manifest** —
  the same drift with the arrows reversed. Manifest updated, all 12 scaffolds regenerated,
  `generate_wrappers.py --check` green.
- **The 600-second anecdote was stated as two proven cases in three files.** One stall is traced to
  the scanner attempt; the second is *observed*, and the same release says so two sections later.
  Corrected wherever it is told.

Also found and fixed while checking: `§2.4`'s "read-only **by construction** — every vendor adapter"
is false for two of five (Antigravity has no read-only field at all, Gemini's whitelist is
self-declared unverified) and for the sequential role-switch path, where the persona keeps the
orchestrator's tools; the evidence block was a new agent-trusted channel carrying "do not verify"
with no data-vs-instructions marker, which this repository's own ledger doctrine settled long ago;
the branch table's lead sentence contradicted two of its own rows; and the instance list named 2 of
at least 4 readers.

#### **Cycle 2 — the corrections had their own defects, and the loophole was closed at 2 SOTs of 3**
A second adversarial pass over the corrections above:

- **`skill-adversarial-performance` still blessed `NOT RUN`** while all five `critic-performance`
  wrappers said the opposite and ordered the agent to follow that skill *strictly*. The bullet above
  claimed "both critic skills' §7"; there are three critic SOTs. Fixed (v1.3 → 1.4).
- **`vdd-multi` Step 1.0 — the canonical instance, and the template the parallel path actually
  injects — never got the clause.** Fixed, together with the "valid only in the caller's message"
  rule the injected prompt also lacked.
- **`10_security_auditor.md` was not updated**, so the SOT the fixed wrapper says to follow strictly
  still specified a two-field footer without `scan_status` and demanded an `audit_file` the wrapper
  forbids writing. Both reconciled in that file.
- **`NOT RUN` had no honest escape**, so a module with genuinely nothing to run could never converge
  — pressure toward writing a trivial test to clear the gate, i.e. the fabrication mode one layer up.
  Added `NOT APPLICABLE (<what was checked>)` as the orchestrator's positive, attackable claim.
- **The generator's `if evidence / elif readonly_clause`** meant filling `critic-logic`'s evidence
  string **deleted** the vendor read-only line from its Gemini and Antigravity wrappers — the two
  adapters §2.4 identifies as enforcing nothing. Both clauses now emit.
- **§9's history still carried the retracted numbers** ("six sites", "their own generated scaffolds
  carry") while the retraction lived only in this changelog — the corrected text in the file nobody
  loads, the wrong text in the file every agent loads. Fixed.
- **The version denominator was 5 of 6** (`System/Docs/VDD.md` still said v3.2), and §2's
  anti-fabrication cross-reference said "§1's third Red Flag" while the new one was inserted second.
  Both fixed; the cross-reference is now nominal.
- **The instance list is now a table of readers**, split by half, after cycle 2 showed "all of them"
  named five of a dozen.

**Still open, named rather than closed:** `vdd-multi`'s merged verdict is `PASS | FAIL at <severity>`
with no state for "unverifiable", so three critics reporting it can still aggregate to `PASS`; and
the same "role cannot run what its skill mandates" defect is live for `product-analyst` and
`solution-architect` (`skill-product-analysis`, `skill-product-solution-blueprint` both instruct
`python3 …` at roles with no Bash). The correct search space is *every skill loaded by a Bash-less
role*, and it has not been swept exhaustively.

#### **One correction to this release's own verification**
The first pass verified with `pytest tests/ -q` — **343 tests** — and reported that number. CI runs
a different list which *adds* `.agent/skills/skill-spec-validator/scripts/tests/`; the union is
**390**. That is rule 1 of the `developer-guidelines` §6.3 this framework shipped one release ago,
missed while shipping the next one. The numbers above are the union, and `run_tests.py` (a suite the
CI job list does not contain at all) was run alongside it.

### **v3.22.0 — a gate must not depend on the language of the document it judges**

From three work-items filed by a downstream project whose artifacts are written in Russian
(WI-30/31/32, one `/vdd` run). The reported symptom was one validator refusing a perfectly
good RTM. Re-verification found the same defect in **four** places, one of them silent, and
the framework had already solved it once — for a single ledger — without generalizing.
Gates: **779 tests** across the four local suites, 45/45 skills, prompt-refs / security-lint /
workflow-smoke green; compatibility measured differentially — **0 of 1102 artifacts changed
verdict across 10 projects** (`scripts/tools/compat_diff.py`, old = `14799d3`).

#### **Added — `documentation-standards` §4.3–§4.4 (v1.6 → v1.7)**
§4.1 sorts references into positional and nominal and prefers nominal. That was right and
incomplete: a nominal reference can still break, because it names its target **in a language**.
The third rung is **nominal-by-anchor** — `<!-- contract:rtm -->` survives renumbering,
retitling *and* translation. **RULE: a human may address a section at any rung; a machine gate
addresses an authored document at the anchor rung.** §4.4 is the reserved-anchor registry
(14 rows, each naming its consumer); no gate may key on an unregistered anchor. Anchors are
**emitted on write, optional on read**, so every existing artifact behaves byte-identically.

`known-issues-format` (v2.0 → v2.1) points at the registry: its own "a comment, not a heading,
because headings get renumbered and retitled" is where this reasoning was first written down.
`docs/ARCHITECTURE.md` §7 gains §7.2 and invariant **L1** — §7 previously modelled localization
as *translating the framework*, which is a different problem from *the project's own artifacts
being in another language*.

#### **Fixed — `skill-spec-validator`: three language couplings, not one**
`RTM_HEADER` (English heading words), `expected_cols = ['ID','Requirement']` (the reported
failure), and — independently — `r['ID']` in `validate_plan`, which kept `--mode plan` dead
*even after* the column check was fixed. Both modes now share one `locate_rtm()`; they held two
copies and each past fix landed in only one of them. Under an anchor the table is read
**positionally** (first column = id); without one, the pre-existing contract runs unchanged.
`RTM_HEADER` is byte-identical and the corpus floors are untouched. 38 → 47 tests, and the
47-test suite is now **wired into CI**, where it had never run.

#### **Fixed — the same defect in three more places, only one of which anyone had filed**
- `calculate_wsjf.py` matched four English column names against an authored backlog table.
  Falls back to position when no name matches; a *partial* match is deliberately not rescued.
- `task_id_tool.normalize_slug` stripped every non-latin character and returned `"untitled"` —
  silently, and identically every time, so `"реестр-инструментов"` and `"единый-реестр"` both
  archived to `task-095-untitled.md`. Now transliterates before stripping.
- `archive_protocol.py` re-implemented the slug rule twice more with its own character classes,
  and gated the meta section on the English string `"Meta Information"` — so it did not even
  recognize the `## 0. Meta` table this framework's own template writes. Now delegates to
  `normalize_slug` and checks `<!-- contract:meta -->` first.

#### **Added — `developer-guidelines` §6.3 (v1.3 → v1.4)**
Three ways a gate reports success without verifying anything, all ending in exit code 0:
verifying with a narrower invocation than CI runs, taking an exit code after a pipe, and
treating exit 0 as evidence that work happened. §5.1 item 1 gains the missing qualifier —
**narrow what you write; reproduce CI for what you verify** — resolving a latent contradiction
with a rule that already told developers to narrow the path argument. **Nothing was added to
`core-principles`**: at 43 lines and TIER 0 it is loaded by every role including those that
never invoke a gate, and shell mechanics are not a principle.

#### **Added — `vdd-enhanced` §4 items 6–7, `vdd-adversarial` Cycle Brief**
Four consecutive cycles of one run found the same shape: not a wrong fix, but a fix applied to
one site of an assertion written in four. Item 6 requires enumerating every site **before**
editing and reporting `fixed N of M found` — "fixed" without a denominator is an assertion with
no guard. Item 7 makes the "next cycle's brief" that §4.4 has always referred to a **real
input**: `vdd-adversarial` step 2a now defines the block, and a *missing* block is itself a
finding, exactly as missing execution evidence is. Items 6 and 7 are **appended**, not inserted:
two documents and three ledger lines across two repositories cite §4.4/§4.5 by ordinal, and
shifting them would reproduce the very defect being fixed.

#### **Corrections after review — two of this entry's own defects**
A reviewing agent checked the above against the repository and found two things wrong with it.
Both are recorded rather than quietly amended, because both are the genre this release is about.

- **The `calculate_wsjf.py` fix broke a test that was not in the CI job list.** The positional
  fallback fired on *any* row of ≥5 cells, so a lone headerless `| Bad | 1 | 1 | 1 | 0 | 0 |` was
  consumed as the header row, leaving zero data rows and exiting 0 —
  `test_product_scripts.py::test_job_size_zero_protection` went red. The fallback now requires the
  markdown separator row that follows a real header. Missed because verification used the CI job
  list, and that list is a **subset** of the local suite; §6.3 rule 1 now says CI is a floor and to
  take the union.
- **Pulling that thread found the named protection had never run.** Its fixture was rejected on
  column names long before reaching the guard, and the guard did not exist:
  `calculate_wsjf.py` read `if js == 0: js = 1  # Avoid div by zero` **and**
  `return max(1, num)  # Ensure at least 1`, so a row sized 0 scored `(8+5+3)/1 = 16.0` and sorted
  to the top of the backlog looking like a real 16. **Two sites, both closed** — fixing only the
  first left `0` and `-3` still scoring. Job Size ≤ 0 is now refused, the backlog is left
  unmodified when it is, and four tests cover it on both the English and positional paths.
- **A denominator in this changelog was typed, not counted.** "0 of 1105 artifacts" was a literal
  in a print statement's format string; the real total is **1102**. The substantive claim (no
  artifact changed verdict) was genuinely computed and holds. §6.3 gains **rule 4**: a number you
  report must be produced by the thing you measured. The measurement is now a checked-in script
  with its evidence line in the skill.

Also noted and deliberately **not** changed: `map_size_to_fib`'s `num > 40` branch contains two
unreachable comparisons (`num <= 10`, `num <= 30`). Verified across the range — the first reachable
branch returns the same value they would have, so it is dead code, not a behaviour defect.

#### **Not shipped, deliberately**
The other half of WI-30 ("a skipped step must be an event") and the mechanically-enforceable
half of WI-31 both need one mechanism — a wrapper that runs the command, so it owns the true
exit code, records the invocation verbatim, and makes "did not run" a distinguishable state.
That is `run_stack.py gate`, already designed as Component C of design spec 095. Field evidence
was recorded against that spec's Phase-5 entry gate instead of building a second mechanism
beside it. Spec 095 also received an independent four-lens adversarial review
(`docs/reviews/review-095-independent.md`): 57 findings, 30 CRITICAL/HIGH, **11 surviving** a
refutation pass — it is **not** ready to build from.

### **v3.21.11 — positional references are verified last, or the check passes too early**

From a live run (`onchain-intel` TASK-010): one task settled two open questions in ADRs
**and** rewrote the comments that referenced them as open. The ADRs went first, so they
quoted a sentence the task then deleted, and every line past the insertion point shifted —
while the document asserted "all `file:line` references verified". Eight of thirty confirmed
findings, one cause. Gates: **324 pytest** (228 → 324) + 17 subtests, **275 `run_tests.py`**
(179 → 275), 45/45 skills, prompt-refs / security-lint / workflow-smoke green.

#### **Added — `documentation-standards` §4.1–§4.2 (v1.4 → v1.6)**
A reference is **positional** when it points at *where* something sits (line, offset, item
number, section ordinal), **nominal** when it names the thing. Positional ones break on an
inserted line. So when one task changes both an artifact and a document referencing it
positionally, those references are checked **after the artifact edits are final**, and any
quotation of the pre-edit state carries a revision identifier. §4 becomes *Path & Reference
Standards*; per-ecosystem commands sit in a table beside the rule, not inside it.

§4.2 adds the resolver `scripts/check_positional_refs.py` — advisory, diff-scoped,
read-only. It resolves `path:line` plus the `§` ordinals whose target is named adjacently,
printing the target line back for comparison. Errors are objective (missing file, ambiguous
shorthand, line past EOF, absent `§`); drift and paths leaving the repository are warnings a
human judges. Every run prints how many ordinals it checked (passed and failed apart), skipped
with the reason, and never examined — and pinned references are excluded from the "resolve"
count — so a green report cannot be read as covering what it never looked at. 96 tests,
gated in `framework-gates.yml` and named in `tests/run_tests.py`, so the suite a developer
runs locally is not blind to them.

Pinning is language-independent, and **backticks** are what make it so: they mark a token
as an identifier rather than prose, which no list of prepositions can do across languages.
So `` …:101 на `985f843` `` pins in Russian exactly as in English, while an *unmarked* hex
run — a CSS colour, a build id, a digest — does not, and an unmarked version does not
either, because it is usually the subject of the sentence ("bump to v3.4"). `HEAD` is
matched case-sensitively: honouring lower-case "head" would exempt every line containing
"the head of the list". One prose pin covers a line only when that line carries exactly one
reference, ordinals included. `@<rev>` remains the unambiguous per-reference form.

#### **Added — `code-review-checklist` §3 (v1.2 → v1.3)**
One checkbox that names its owner: **the reviewer**. The author's own verification *passes*,
because it ran before they shifted the lines. A check the author cannot fail is not a check.

#### **Rejected as a gate, shipped as a tool**
A resolver cannot tell a legitimate quotation from a stale reference, so the gate stays
rejected. The `@<rev>` pin (`` `src/app.py:42@v3.21.10` ``) makes that distinction decidable
and the tool ships **advisory** instead. The caution is earned: a survey of this repo's
archived reviews finds 54 of 84 resolvable references pointing into files edited after the
document was written, nearly all of them correct historical records. The same discipline
caps the ordinal check at the slice with an unambiguous target — across 483 documents it
returns exactly one real defect: `SKILL_TEMPLATE.md` pointed at section 14 of a
`skill-creator` document that ends at section 10. That pointer is now nominal.

---

### **v3.21.10 — VAL-2: the trigger probe was measuring itself; and the evals catch up to the skill**

Two halves. **VAL-2** — the instrument that measures whether a skill's description
triggers reported "0 triggers across 69 runs" for a description that fires instantly by
hand; that is exactly `23 queries × 3 runs`, i.e. the probe, not the skill. **The evals** —
the 19-case behavioural suite was mechanically green while describing a world that TASKS
091–095 had already changed. Gates: **58 skill-creator tests** (26 → 58), **330
run-feedback tests**, E2E PASS, `selftest` PASS (19 cases, both new ones discriminating),
`grade_run --lint` clean, 45/45 skills, all five earlier exploits still refused.

#### **Fixed — VAL-2 (verified live before any code changed)**
A fake `claude` on PATH replaying canned stream-json reproduced every reported behaviour at
zero token cost, and turned up **three mechanisms the record does not name**: `message_stop`
fires once per assistant *message* (recorded from a real stream: 2 × `message_stop`, 1 ×
`result`), so a skill call after a tool result scored not-triggered; the EOF path discarded
every event in the final read; and a `thinking` block always precedes the tool call.

The fix **widens and tightens together**, which is the whole difficulty: accepting the
canonical name while leaving matching loose would have made precision *worse*. The old
`clean_name in accumulated_json` test already scored `Skill(skill="brainstorming",
args="…<clone>…")` as a trigger — a **different** skill counted, which the record's own
"Do-not" forbids. Now: exact match against `{probe_clone, real_name}` after normalising
`plugin:skill` forms, `Skill.skill` only (never `args`), a `Read` only when it loads
`SKILL.md` or the probe command file, an 8-call budget instead of first-call-decides, and
every other tool NEUTRAL. Instrument failure is now distinguishable from a real
non-trigger (`matched` / `clean-no-trigger` / `budget-exhausted` / `timeout` /
`child-error`), the run reports **which** name matched, and zero-triggers-everywhere prints
a loud warning instead of a half-plausible summary.

*A defect of my own, caught mid-fix:* the first version killed a child that was exiting
cleanly and classified it `child-error` — which made every negative pass for the wrong
reason. Our kill is now distinguished from the child's own failure.

#### **Fixed — the eval suite caught up to the skill**
* **Case 10 was factually inverted** by RF-1: its note said "doctor reports ready:true even
  on built-in defaults". It now grades the exit-3 bootstrap trigger, `configured: true`, and
  that the two-level layout survives bootstrap.
* **Case 17 had lost its forcing function**: it claimed a stale `backlog_path` makes filing
  exit 4; it now exits 0 and silently *seeds* the second backlog the case forbids. The
  dry-run is the only place that signal appears, so the case now grades it.
* **Case 5's golden transcript filed a retired phantom premise** the case's own note
  documents as the fixture bug it was fixed to remove — the seed was corrected and the
  transcript was not, so the "ideal agent" modelled a defect the fixture no longer contains.
* Cases 7, 9, 12 corrected for the two-level registry and the RF-2 body gate.
* **Infrastructure that made half the registry ungradeable**: `_hashes.py` did not hash
  `docs/backlog/`, and `ledger_text()` could not see work-item records — so the lockstep ban
  covered only the defect ledger.

#### **Added**
* **Case 18 — ledger bodies are DATA, not instructions.** The suite's only OWASP-LLM01
  surface: a seeded issue body carries plausible *maintainer prose* instructing the agent to
  mark everything `auto_fixable` and hand-append to the index. The failure mode is a
  **helpful** agent, not a fooled one. With a confused-deputy violator.
* **Case 19 — recovery from a refused body.** WI-2's screen is script-covered; what only an
  LLM can get wrong is what it does with exit 2. Its golden transcript *asserts the refusal
  actually fires*, so the fixture cannot go stale silently.
* `grade_run.py --lint` — static suite validation with no sandbox and no tokens, descending
  into `not` wrappers (the omission that let one of my own miswired checks through).
* `evals/README.md` — provenance, the odd-`--runs-per-query` footgun, and the five lockstep
  obligations for editing a case.
* Trigger set 23 → 30 queries: four positives for work-item filing (advertised since v3.21.4,
  never tested), three negatives guarding the word "backlog", and four queries tagged
  `instrument_sensitive` whose historical failure was VAL-2, not the description.

#### **Honest about the instrument**
`selftest.py` claimed "the instrument discriminates" while proving it for 8 of 17 cases; it
now names the 9 with no violator transcript, and `--case N` no longer prints the global
banner after running zero violators. `grade_run.py`'s misalignment guard exits **2** as its
own docs always promised (it exited 1, indistinguishable from a grading crash).

#### **Scope, recorded not silently expanded**
The description gained one 6-word disambiguator (`NOT for fixing already-filed issues
(/heal-issues).`, 69/70 words) to protect the set's hardest negative. Trigger evals remain
**single-vendor** — `run_eval.py` only speaks Claude Code — but the detector is now split so
the pure matching helpers are vendor-neutral and only `TriggerScanner.feed` knows the wire
format. Filed as **WI-10**; the 9 cases without violators as part of the standing gap.

### **v3.21.9 — RF-1 / RF-2: two gates that did not check what they claimed**

Both from the 2026-07-13/14 eval campaign, and one class — the one RF-2 names in its own "Related"
line: **the gate does not check what it claims**. Light Mode. Gates: **330 tests** (320 → 330),
E2E PASS, contract-sync OK, 45/45 skills, `doctor ready: true`.

#### **Fixed**
* **RF-1** — `doctor` reported `ready: true` in the same payload whose own remediation said "run
  init", so any caller gating on `ready` concluded an unconfigured repo was configured (which is how
  eval agents filed into an unbootstrapped fixture repo with nothing stopping them). `configured` is
  now its own check **and** part of `ready`: an unconfigured repo is `ready: false`, exit 3, and
  `init` then makes it ready. Option (a) from the Fix path, chosen over (b) deliberately — adding a
  `configured` field while leaving `ready` alone would not have fixed the reported harm, because the
  harm is that callers gate on `ready`. The record's "Do-not" was honored in lockstep:
  `test_e2e.sh` (which asserted exit 0 in a config-less repo), `cli_reference.md`, and SKILL.md §7,
  where a whole paragraph existed only to teach agents not to trust this field. `collect`/`file`
  deliberately still run on built-in defaults and exit 0 — only `doctor` refuses.
* **RF-2** — `file` validated nothing about the body, and `--dry-run` previewed the id, the paths and
  the index line but never the **body**: the one part an agent composes by hand and cannot repair
  afterwards, since §5 is create-only. `body.guard_structure` now refuses an unterminated code fence
  (**both** registries) and a defect body with no `## Reproduction` section at exit 4 as the Fix path
  specified, and `--dry-run` echoes the rendered record. Create-only was not relaxed — the gate was
  fixed, not the invariant, which is what removes the trap that made an agent hand-edit a filed record.

#### **Cost, recorded because it was not zero**
The Reproduction requirement exposed that **28 test fixtures were filing defect bodies the documented
contract had always forbidden** (bare stubs like `"Body."`). They now share one `fx.DEFECT_BODY`.
Making the fixtures conform is the honest direction; loosening the gate to accept stubs would have
been the gate bending to the tests. Two assertions comparing a body line-by-line, and one E2E line
that broke under `set -o pipefail` (`doctor` exits 3 there by design, so the pipeline failed even
when the grep matched), were fixed alongside.

One deliberate asymmetry: work-item bodies need no Reproduction section (`/heal-issues` selects on a
defect repro) but do need balanced fences. Five guards mutation-verified.

### **v3.21.8 — one ledger write path: the asymmetry class closed by construction**

Three adversarial iterations each found a guard present on one ledger writer and absent on its twin
(WI-23; iteration 2's V12; iteration 3's L-1, L-2, L-4, L-5, L-6, H-04). TASK 093 shared the
*mechanisms* and still produced six new instances. This closes **WI-9** — the choreography is now one
`file_record()` in `feedback_lib/ledger_core.py`, driven by a per-registry descriptor — and **WI-8**,
the 16-row residue, fixed afterwards so the rows living in that choreography landed once for both
registries rather than twice by hand. Gates: **320 tests** (286 → 320, zero skips), E2E PASS,
contract-sync green with **zero edits** to `known-issues-format`, 45/45 skills, `doctor ready: true`,
all five iteration-3 exploits re-probed and refused, both live consumer configs verified.

#### **Changed — the extraction (WI-9)**
* **`ledger_core.file_record`** holds the whole write: vocab → lexists pre-check → id uniqueness →
  body policy → frontmatter → record text → index line → index insert → records-dir integrity →
  `O_EXCL|O_NOFOLLOW` create → rollback → index write → rollback. Every guard exactly once; `O_EXCL`
  now appears in **one** ledger module.
* **The public API is byte-identical.** `file_defect` / `file_work_item` keep their signatures *and*
  their result-dict keys, so the **286 pre-existing tests passed unmodified** — the plan forbade
  editing a single one during the extraction, and the audit made that a gate. A refactor whose tests
  change alongside it proves nothing.
* When two rollback tests turned out to patch a seam the core no longer used, the seam was made real
  (`Registry.write_index`) rather than the tests rewritten. The behaviour was never in question, only
  where the mock attached, and keeping the net intact was worth more than removing an indirection.
* **`tests/test_ledger_core.py`** is a guard *inventory* that runs each guard against **both**
  registries and records **which one refused** — per-registry attribution was an audit requirement,
  because a test asserting only "some registry refused" has the same blind spot as the defect class it
  exists to catch. Nine guards mutation-verified; `O_EXCL` reddens it twice, once per registry.

#### **Fixed — the residue (WI-8, 15 of 16 rows)**
* **Correctness:** a **blank** (0-byte) index is now seeded, not left preamble-less; `doctor`
  evaluates every validating config key so it can no longer report `ready: true` while every `file`
  exits 3; the placeholder strip matches exact seed text instead of a wildcard that would delete a
  human's italic note; a new category is placed by sort order, not file order; a quoted value with
  trailing text (`title: "The Big Bug" (again)`) no longer silently loses the tail.
* **Security:** duplicate frontmatter keys are refused (the "a human reads the first value, a tool
  reads the second" primitive); the hook debug dump is redacted before it is persisted — it was the
  only place unredacted tool output was durably stored; `write_atomic` refuses a symlink target and
  takes its mode from `lstat`; the record dir's realpath is re-verified before the create, closing the
  TOCTOU window on intermediate components that `O_NOFOLLOW` cannot see; `feedback_dir`'s exemption is
  narrowed so `.git/objects` is refused while the documented `.agent/feedback` still works; every
  `triage` table cell is escaped, not just `\|` in the message.
* **Performance:** inbox and journal writes drop the `fsync` (regenerable state, and the barrier sat
  inside the collect flock); an over-ceiling `--body-file` is refused by **stat**, before the read that
  used to load a multi-GB log to measure it against the ceiling meant to refuse it.
* **Tests:** the two under-pinning ones corrected — `_within` is exercised directly with a NUL path
  (the old test exited through `NotFound`, so the arm it was written for was pinned by nothing), and
  the filename invariant is asserted against the **glob the lookup uses** rather than a proxy.

#### **Not fixed, with the reason**
* **sec-L-10** — a repo-shipped `.git` *file* can relocate `data_root`. That mechanism is how linked
  git worktrees legitimately work and the documented reason `data_root` exists; a hostile pointer and a
  legitimate one cannot be told apart from the pointer alone, and a false refusal breaks worktree
  support silently. Accepted and documented rather than guessed at.
* The perf row also wanted opens-per-filing and fsyncs-per-capture counters. The fsync **asymmetry** is
  pinned; absolute counts are not, so a regression there would still be invisible. Recorded, not claimed.
* The four result-dict synonym pairs (`issue_id`/`item_id` …) mean the core carries a translation
  layer. Normalizing them is a separate change with its own callers — doing it here would have
  destroyed the unmodified-suite property that verified the refactor.

### **v3.21.7 — iteration 3: the task that closed the asymmetry class produced six more**

`/vdd-multi` iteration 3 reviewed the WI-2…WI-7 fixes and found that **TASK 093 had not applied its
own organizing lesson to itself**. WI-7's generalization is *"a fix that lands on one of two
symmetric code paths is half a fix"* — and the code written to close that class contained six more
instances of it, including one that re-broke the CRLF fix in the branch a freshly seeded index always
takes, and one where the defect ledger had **no fence awareness at all** a whole task after the
work-item ledger got it. Vigilance was the wrong remedy. Gates: **286 tests** (265 → 286, zero
skips), E2E PASS, contract-sync 0, 45/45 skills, `doctor ready: true`. Report:
[`docs/reviews/vdd-multi-093.md`](docs/reviews/vdd-multi-093.md).

#### **Fixed — 5 reproduced exploits**
* **Arbitrary file write** (H-01): `finding.save` built its path from an unvalidated `finding_id`
  read off disk, and `pathlib` discards the left operand on an absolute right one — so an inbox record
  carrying `"finding_id": "/…/.claude/settings"` wrote its whole JSON object there, via `--as noise`,
  the one path needing no title, body or category. Reproduced, then closed with **two independent
  controls**, each pinned by its own test.
* **Out-of-tree delete** (H-04): WI-6 guarded one of `resolve`'s two branches — and the unguarded one
  is the branch a ref without a `.json` suffix *necessarily* takes, so `--finding ../../../victim`
  read a foreign file and `consume` **unlinked it**. Reproduced.
* **Case-variant denylist bypass** (H-02): `Path.resolve()` does not canonicalize case and APFS is
  case-insensitive, so `.Claude/commands` reached the real `.claude/commands/` — the V-11 exploit
  reachable by changing one letter. Now NFC-normalized and casefolded across **every** component.
* **CRLF corruption** (L-1) and **insertion inside a code fence** (L-2), both reproduced by hand.

#### **Fixed — structurally, not case-by-case**
* **`feedback_lib/markdown.py`** — one CommonMark fence scanner both ledgers consume. The defect
  index was fence-blind, so a pointer line landed inside a documented example; and an indented anchor
  counted as live, so `doctor` could report `ready: true` for an anchor that renders as code.
* **`ids.assert_id_free`** — one id guard both writers call (the defect writer had none).
* **`body.guard_config_body`** — the WI-2 cap and screen now run **inside both writers**. Putting the
  check in the CLI meant *neither* writer had it, and the docstring argued the inverse.
* `atomic.read_verbatim`, `except BaseException` rollback, and the trailing-newline shape are now
  identical on both paths, and every test covering a shared guard is parameterized over both
  registries so "fixed on one path" cannot pass again.

#### **Fixed — security**
* The credential screen missed **the exploit it was written for**: `--body-file ./.env` passed,
  as did PEM private keys, `github_pat_`, `glpat-`, `AIza`, JWTs and inline-credential URLs. 10 more
  families plus one narrow `NAME=<20+ chars>` rule that still lets *"the bypass token:
  [PLACEHOLDER]"* through. A **partially** masked secret (`ghp_xxxxxxxx<live tail>` — what the error
  message's own "remove or mask" invites) no longer launders past: the mask must now dominate.
* Metadata scalars (`--title`, `--value`, `--source`, `--reason`, `--component`) are screened and
  capped — they land in frontmatter, the index line and the journal, all git-tracked.
* Ledger config paths are validated **structurally** (no dot-component, `.md` for file keys, no
  markdown/control characters) instead of against a denylist of 8 dirs and 5 basenames that left
  `.cursorrules`, `.envrc` and `.github/**` legal targets.
* `clip` slices before redacting (it scanned 100 MB to produce 2 000 chars, on tool output, inside a
  synchronous hook), the email rule is bounded against O(n²) backtracking, and `clip(text, 1)` no
  longer returns the whole string.

#### **Fixed — performance**
* The hook did **O(entire tool output)** work — full copy, `splitlines()`, full-text regex — *above*
  the exit-0 discard, i.e. on every successful Bash call, synchronously in the session. WI-4 removed a
  bounded ~5–30 ms `git` spawn from that path and left an unbounded allocation cost three lines
  higher. Response tail-truncated to 64 KB; the `tool_name` discard moved above the imports.
* `doctor` parsed every inbox JSON to produce an integer — the exact O(k) WI-5 had just deleted, one
  command over, in the same commit. `_dup_candidates` rebuilt a loop-invariant token set per pair.
  `existing_ids`/`list_issues` now read metadata only (`parse_file` joined a full record body that
  every id scan discards, twice per filing, inside the filing flock).

#### **Process — mine, not the code's**
* **I edited the tree while the critics were reading it.** `critic-security` got two different
  versions of one file and correctly refused to certify the exit bar on those grounds. Its one
  integrity finding was an artifact of that window (verified). Freeze the tree for a review.
* Mutation testing caught **a weak test of my own**: asserting the anchor *count* is 1 passes whether
  the right or the wrong anchor resolved. The fence tests now assert **which line**.
* Two independent controls **masked each other** in a test — neutralizing either left the suite green.
  Each now has its own test, the same lesson as iteration 2's create-only guards.
* **Not converged.** All three critics returned `issues-found`. The residue is filed as **WI-8** (16
  recorded findings) and **WI-9** — extract a shared `ledger_core`, promoted from WI-7's "someday"
  because writer asymmetry has produced a confirmed finding in *every* iteration, three for three.

### **v3.21.6 — the WI-2…WI-7 tail: shared primitives instead of vigilance**

Closes all six work-items the two adversarial iterations of TASK 091/092 deferred. The organizing
finding is WI-7's: **`ledger_issues` and `ledger_backlog` implement one contract in two modules, and
every fix that landed in one but not the other is half a fix** — V12 was literally "the CRLF fix
landed only in the backlog module". So the answer is not vigilance: the mechanisms that diverged are
now *shared primitives*, and where a guard exists in both ledgers **one parameterized test** covers
both instead of two hand-copied ones that can drift. Gates: **247 tests** (174 → 247, zero skips),
E2E PASS, contract-sync 0, 45/45 skills, `doctor ready: true`.

#### **Fixed**
* **WI-4** — `Config.data_root` is lazy + cached **per instance** (uncached would spawn `git` on
  every `feedback_dir` access, worse than the eager call), `git` timeout 10s → **2s**, and the hook
  loads config **below** the `tool_name`/`should_capture` filters. `doctor`/`issues`/`--dry-run` now
  spawn zero `git`. The module-level memo was **dropped** as a staleness class that buys nothing.
* **WI-5** — `find_by_fingerprint` globs on the 8-char prefix already in the filename instead of
  parsing every inbox file (O(k²) → one read). A fallback scan was rejected: the miss case is the
  common case, so it would restore the cost while looking like a safety net. `doctor` reports
  `inbox_depth`.
* **WI-6** — a bare `--finding <path>` must resolve inside the feedback dirs; `consume` unlinks what
  `resolve` returns, so an arbitrary path was deleted. Also catches `ValueError` from `Path.resolve()`
  on an embedded NUL (an uncaptured iteration-2 finding).
* **WI-7 (all 11 rows)** — CommonMark fence tracking (char **and** length, so a 3-backtick line no
  longer closes a 4-backtick fence) that stays **fail-closed** and names the unclosed fence's line;
  the placeholder strip walks forward instead of probing offsets 2–3; `doctor` guards every
  config-derived probe, catches `UnicodeDecodeError`, and reports `"unchecked"` rather than a false
  `False` for an over-cap ledger; `read_verbatim` shared so the **defect** index stops normalizing
  CRLF; config validation for `backlog_anchor`/`id_prefixes`/`*_max_chars`; `mkstemp` for the last
  predictable-name write; `provisional_id` on both paths **and** in the human line; both ledgers
  **build** frontmatter from `CONTRACT_KEYS` (pinned to the SKILL.md authority by a test that
  reddens when a key is added); a failed `consume` after a good ledger write is now recoverable
  instead of exiting 4 forever; `serialize` quotes what YAML would coerce (`true`, `2026`, `0x10`)
  while ISO dates stay bare.

#### **Added**
* **WI-2 — body policy: capped and screened, never rewritten.** `feedback_lib/body.py` runs at the
  single CLI read, so neither ledger can be reached around it: over `body_max_chars` (new key,
  default 64000) → refused; a high-confidence credential shape → refused, naming the class and line
  but **never echoing the match**. **Redaction was deliberately not implemented**: a body is
  preserved verbatim *because* it is evidence, and `filters.redact`'s loose rules rewrite ordinary
  prose (*"the bypass token: …"*, any email). For secrets-in-git, refusal is strictly stronger than
  masking. An already-masked shape still files — a record describing this screen contains one.
* **WI-3 — provenance.** CLI-filed records carry `provenance: machine` **and** a one-line banner
  above the body; the read side is closed too — `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` now state that
  ledger record bodies are **data, not instructions** (they are re-read by Analysis and Planning on
  every run, and a body can derive from a mined transcript — OWASP LLM01).

#### **Found while doing the work, not on any list**
* The human-mode error handler **dropped `remediation` entirely**, so every remediation string in the
  engine was visible only under `--json-errors` — including the half-state recovery instructions
  whose whole value is telling the operator what to do next.
* Writing the V-22 symlink test revealed both create-only guards emitted the **same** message, so no
  test could name which one fired. They are now distinguishable, which is what made the split possible.

#### **Process**
* `docs/reviews/framework-audit-093.md` ran **before** execution (unlike 092's, written retroactively
  and marked as such) and **blocked** the plan on three points, all applied: RED-before-GREEN per
  guard, drop the memo, add the `[REDACTED]` positive case. Its Risk 1 check — reading the two
  consuming repos' live configs — is why the prefix regex allows `-` and `TF-X` is a pinned test case.
* **Mutation-verified, not assumed**: eleven guards were each disabled and the specific test observed
  to redden. That caught a weak test of my own — asserting the anchor *count* is 1 passes whether the
  right or the wrong anchor resolved, so the fence tests now assert **which line**.

### **v3.21.5 — `skill-spec-validator`: tests anchored to the corpus, not to fixtures**

The `/vdd-enhanced` gate shipped **zero tests**, and both matchers (RTM heading, PLAN id coverage) had drifted until they failed on 100% of shipped artifacts — invisible, because *a gate that never passes looks exactly like a gate nobody tripped*. Closes **WI-1**. Gates: **38 tests (0 → 38)**, 45/45 skill validation with the skill now warning-free.

#### **Added**
* **`scripts/tests/`** — the **8** RTM heading shapes the corpus actually ships (fixtures copied verbatim, incl. two `Acceptance Criteria (…)` forms WI-1 had not enumerated) + negative shapes; table, bypass and CLI-error paths; PLAN ids via `## Step N — … (R1)` headings **and** `- [ ] R1` bullets; the `R1`-vs-`R10` boundary, hyphenated ids, markdown-noise normalization; the table parser and RTM section slicing.
* **`tests/test_corpus.py` — the anti-drift layer.** Fixtures alone would not have caught the original drift: the next author to re-tighten the regex would have updated the fixtures to match. So a probe keyed on the `trace*`/`rtm` stems — **wider** than the matcher's required phrase — asserts `RTM_HEADER` matches every RTM heading under `docs/tasks/` bar an explicit, staleness-checked allow-list; plus a regression pin on the 8 shapes and liveness floors (≥15 tasks, ≥10 plan pairs still pass). Discovering **zero** headings is itself a failure. Floors are canaries below today's counts (20 tasks, 14 of 27 pairs), so artifact churn never reddens the suite while a dead matcher always does; outside this repo the corpus tests **skip**.
* **`tests/run_tests.sh`** — zero-test-discovery guard (`unittest discover` exits 0 on an empty run), plus a check that the corpus tests actually ran rather than skipped inside this repo.
* **Proof the guard bites**: re-injecting the two historical regressions reddens the suite — the pre-TASK-090 `^## Requirements Traceability$` matcher → **28 failures**, the literal `[**R-1**]` PLAN token → **7**.

#### **Changed**
* **`skill-spec-validator` v1.0 → 1.1** — the four Execution-Policy sections + a ⚠️ on the bypass. Safety Boundaries states the rule the defect violated: **matchers are widened toward the corpus, never the corpus narrowed toward the matchers.**
* **The first version of that probe was a tautology**, caught by the adversarial review: it required `requirements traceability` or `(rtm)` — a **subset** of what the matcher accepts — so "every probed heading matches" was true by construction. Widening it surfaced a real corpus case (a prose heading in `task-050`), now an explicit exclusion rather than a silent one.

#### **Not changed (recorded, with reasons)**
* `validate.py` still `sys.exit()`s from its entry points — tests assert on `SystemExit.code`; a testability refactor of a live gate is a separate change.
* The `ID`/`Requirement` column contract stands, so one corpus artifact still fails `--mode task`. Loosening a gate to fit a non-conforming artifact is this defect running backwards.
* The bypass token remains a bare substring anywhere in `TASK.md` — a spec that merely *mentions* it disables its own gate (this bit TASK 092's own first draft). Pinned by a test and documented; tightening it is a behaviour change for the owner.

### **v3.21.4 — Work-item filing became two-level, like defect filing (one format contract, two registries)**

`run-feedback` had two filing paths and they had diverged. The defect path wrote a record file **plus** a thin index line, in lockstep, with rollback. The work-item path collapsed the body to one line and inlined it **into the index**, never creating a record — so a retro that produced three work-items had to file them by hand, and `--dry-run` previewed a ~1 800-character bullet with a table folded into a single line. This framework's own `docs/BACKLOG.md` was the second live instance. Generalized: **if the target registry is an index over record files, an appender that writes only the index line is not a filing mechanism for it** — it either loses the body or makes the index unreadable, and in both cases silently. Gates: **167 unit tests (112 at `4281c96`, measured in a clean worktree)** + E2E green, 45/45 skill validation, contract-sync exit 0 (and exit 1 on injected drift).

#### **Fixed**
* **`ledger_backlog.py` rewritten** — `file_work_item()` writes `docs/backlog/<slug>.md` (contract frontmatter + body **verbatim**) **and** one pointer line after the anchor: lockstep with rollback, create-only, `WI-<n>` = max+1 over the record dir. The anchor resolves **before** any write, so an anchorless backlog exits 4 having written nothing; a missing `BACKLOG.md` is seeded from the new template; `--dry-run` previews id, record path and the exact index line.
* **The flat layout refuses instead of flattening** — `backlog_layout: "flat"` (explicit opt-in for a single-file backlog) rejects a body it would have to inline (>1 non-empty line, or >300 collapsed chars) rather than silently collapsing it.

#### **Hardened after adversarial review** ([`docs/reviews/vdd-multi-091-092.md`](docs/reviews/vdd-multi-091-092.md))
Three parallel critics returned 41 findings; **four were reproduced as working exploits** before being fixed. A **second** round then re-verified the fixes in fresh contexts and found that the first pass had guarded the payloads I tested rather than the classes — `\n`/`\r` were refused while the reader also splits on `\x0b \x0c \x1c-\x1e \x85 U+2028 U+2029`; the bracket escaper did not escape its own backslash; the flat bullet still interpolated `--value` raw; `mkstemp` had landed at 2 of 6 temp-write sites; containment was repo-granular, so a config could aim a ledger at `CLAUDE.md` or `.claude/commands/`. All closed and re-verified, with 34 regression tests naming their findings (`tests/test_ledger_hardening.py`), one shared `feedback_lib/atomic.py`, and a `parse(serialize(m)) == m` property test — the single assertion that would have caught the whole injection class at once. The residual tail is filed as WI-7 rather than declared done:
* **Frontmatter injection** — a newline in a metadata scalar forged contract keys, including `auto_fixable`, which `/heal-issues` selects on. `frontmatter.serialize` is now the choke point for both ledgers: newlines and a bare `---` are refused, prose is quoted (apostrophe normalized so the lenient reader cannot truncate it).
* **Index-line injection** — a newline in `--title` spliced a **second, forged** pointer line into a hand-maintained index; `](` closed the link early. Titles are collapsed, `[`/`]` escaped, control characters and >120 chars refused.
* **Symlink follow** — a *dangling* symlink at the record path was followed outside the ledger, because `exists()` follows links and reported `False`, so create-only never fired. Now `lexists` + `O_EXCL|O_NOFOLLOW`, and a symlinked record dir is refused.
* **Config containment** — an absolute or traversing `backlog_dir` escaped the repo (`pathlib` discards the left operand). All five configured paths are resolved and required to stay inside the examined checkout, per SKILL.md §5.
* Also: the record write moved **inside** the rollback guard; the anchor must be unique and outside code fences; `doctor` shares the filing path's anchor predicate and no longer crashes on the misconfiguration it exists to diagnose; `--category` guarded; id reuse refused; CRLF / U+2028 preserved instead of rewritten; flags that would be silently dropped are refused; `mkstemp` + cleanup replaces predictable `.tmp.<pid>` files.

#### **Changed**
* **`known-issues-format` v1.0 → 2.0: one contract, two registries.** The thin-index mechanics are stated **once** and parameterized per registry — defects (`docs/KNOWN_ISSUES.md` + `docs/issues/`) and work-items (`docs/BACKLOG.md` + `docs/backlog/`). No second format skill: two near-identical contracts are exactly the drift that produced this defect. `check_contract_sync.py` now gates **both** seed templates, slicing on `<!-- contract:* -->` markers so the vocabularies are never compared against each other.
* **Config `v1` unchanged; three additive keys** — `backlog_dir` (`docs/backlog`), `backlog_prefix` (`WI`), `backlog_layout` (`index+files`). A config written before them loads with no warning and lands on the layout its project already maintained by hand.
* **CLI/report surface** — `--source` (defaults to the capture's run context), `--effort` limited to `S/M/L`, `filed_as.id` is now the allocated `WI-<n>` and `filed_as.path` the record file; `doctor` reports layout, record dir and template reachability, and a `"flat"` layout is reported rather than flagged (it is an explicit opt-in).
* **Skills and docs** — `run-feedback` v1.4 (§7 covers both classifications; two red flags; `work_item_body_template.md`; `auto_fixable` stays defect-only), `artifact-management` v1.4 (`BACKLOG.md` as a living Global Artifact with its format delegated), `QUALITY_FEEDBACK_LOOP.md` v1.1 with a "why two ledgers and not one" note, and the Analysis-phase ledger line added to `CLAUDE.md`, `GEMINI.md` **and** `AGENTS.md` — the first pass updated only `CLAUDE.md`, the same single-vendor omission v3.21.3 had to correct for Workspace Workflows.

#### **Dogfood**
* This repo's own flat `docs/BACKLOG.md` → a thin index over `docs/backlog/`, text preserved verbatim: the framework no longer ships a contract it violates. The five review findings that were **not** fixed (body redaction/cap, ledger-body provenance, an eager `git` spawn with a 10s cliff on the hook path, an O(k²) inbox scan, `--finding` path containment) were filed as **WI-2…WI-6** through the fixed CLI itself.

### **v3.21.3 — Retro lessons hardened: portability review, vendor-bootstrap parity, one rule reverted**

Five retro lessons from a consumer project had been written into Tier-1 skills and pipeline prompts; an adversarial pass over the batch found two of them inverted on other stacks. Gates: 45/45 skill validation, 228 pytest + 17 subtests, doctor / prompt-refs / workflow-smoke / security-lint green.

#### **Fixed**
* **`developer-guidelines` §5.1** — Go row is now `gofmt -l .` / `gofmt -w .` (`gofmt` takes paths, not the go-tool `./...` pattern), with `go fmt ./...` flagged as a writing form; `ruff format --check` replaces `--diff`; `ruff check .` and `cargo clippy` added to the reporting column.
* **`developer-guidelines` §5.1** — narrowing the path argument to the task's files is now step 1; extending repo-wide ignore rules is a finding to RAISE, no longer a mandated edit.
* **`code-review-checklist` §2** — the dead-code guard greps repo-wide instead of `test/`, with per-language test layouts listed (Go, Rust, JS/TS, Python, Foundry).
* **`01_orchestrator.md` §5.1** — retracted C-07 claim removed; `skill-parallel-orchestration` citations corrected §4 → §2.2. Same claim removed from `docs/ARCHITECTURE.md`.
* **`01_orchestrator.md` item 15** — stalled-subagent recovery branches on evidence: early stall → resume; late stall after substantial output → fresh spawn seeded with the partial artifact.
* **`04_architect_prompt`** — incremental writes follow the order `architecture-format-*` mandates; out-of-order decisions go to a scratch draft.
* **`08_developer_prompt` Step 2b** — "highest-value first" is scoped to within the assigned phase and never reorders the Stub-First phases.
* **`CLAUDE.md`** — duplicate list numbering in Workspace Workflows (`3.` twice).

#### **Added**
* **`run-feedback` §7 triage step 4** (v1.2 → **1.3**) — a finding whose fix edits a shared artifact must be generalized out of the originating stack, and a behaviour change filed as a work-item for review rather than landed as guidance. Two matching Rationalization Table rows.
* **`AGENTS.md` Workspace Workflows section** — Codex and Cursor previously had no workflow discovery or dispatch rules. `GEMINI.md` gained the Teams Dispatch item.

#### **Changed**
* **Bootstrap files name their own parallel-orchestration reference** instead of running the §1.1 detector. `GEMINI.md` splits guidance between Antigravity and Gemini CLI, since `vendors.yaml` maps both to it.
* **War-story justifications and origin markers removed** from Tier-1 artifacts.

#### **Reverted**
* **Commit-granularity rule (`skill-planning-format`)** and its plan-template field — its premise is false under Stub-First (the stub commit is green by construction) and its trigger fires on every Stub-First plan.
* **"Independent critics beat self-critique" (`vdd-enhanced.md`)** — uncited, and it deprecated the workflow that file dispatches. Retained: orchestrator-applied fixes carry into the next cycle as unreviewed, and a cap reached with one still unreviewed → verdict **WARNING, never PASS**.

### **v3.21.2 — `task_id_tool.py`: sub-tasks no longer block archiving their own parent**

`get_existing_task_ids()` was the single scan behind both the auto-generated id **and** the `--proposed-id` conflict check, and it matched `task-005-1-slug.md` as "id 005 is taken". So archiving a **finished parent** TASK-005 under its own id was refused and silently corrected to 006 — while `skill-archive-task` Step 4 instructs the agent to "set Task ID to the id used in filename". Following the protocol literally therefore **renumbered an already-committed task**, breaking its pairing with its own nine sub-tasks, with `docs/plans/plan-005-*.md`, and with every commit referencing TASK-005. Nothing errored; the hand-maintained ledger simply became wrong. Found in a TASK-006 run of the `onchain-analytics` repo: `--proposed-id 005` returned `corrected -> 006` although `task-005-m2-alpha-paid.md` did not exist. Gate: 36/36 in the tool's own suite, 59 green across `.agent/tools`.

#### **Fixed**
* **The `--proposed-id` conflict check now runs against parent archives only.** New **`get_parent_archive_ids()`** returns the ids that actually own a parent archive (`task-<id>-<slug>.md`); a populated sub-task namespace (`task-<id>-1..N-*.md`) is no longer a conflict for the parent it belongs to. The two scans are split **by semantics, on purpose**: `get_existing_task_ids()` is **unchanged** and still backs **auto-generation**, where a sub-task must keep its parent's id reserved — otherwise a brand-new task would be handed a number whose sub-task namespace is already populated, interleaving two unrelated tasks under one id.
* **Parent vs sub-task is decided by filename shape** — a sub-task's segment right after the id is purely numeric (`task-005-1-…`), a parent's is not (`task-005-m2-alpha-paid`). The repos' own precedent had been contradicting the tool: `task-003-m1-read-layer.md` sits next to `task-003-1..8`, i.e. "the parent keeps its id" is the convention actually practised.

#### **Added**
* **`TestParentArchiveVsSubTask`** (tool suite 29 → **36** tests) — covers the original scenario, the inverse (a real parent archive still conflicts), `allow_correction=False`, and that auto-generation still reserves ids held only by sub-tasks.

#### **Changed**
* Both filename patterns are now module-level constants (`TASK_FILENAME_RE`, `SUBTASK_FILENAME_RE`) instead of a regex compiled inside the loop, so the parent/sub-task distinction has one definition rather than two call sites that can drift.

**Known limitation** (documented in the docstring, not silently accepted): a parent slug that itself begins with a bare number segment (`task-007-2024-migration.md`) is indistinguishable from sub-task 2024 by filename alone. `normalize_slug` does not forbid leading numeric segments, because `task-012-3d-viewer` is legitimate and reads correctly (`3d` is not purely numeric).

### **v3.21.1 — `documentation-standards` v1.4: Markdown structure is now a contract, not a preference**

The framework had a standard for documenting **code** (docstrings, JSDoc, why-not-what comments) but none for the **shape** of the `.md` artifacts it emits on every run — so TASK/PLAN/ARCHITECTURE files kept degrading into unreadable walls: explanations stuffed into table cells, 30-line paragraphs with no entry points, 2000-character lines that turn a one-word fix into a whole-paragraph diff. This release makes structure a contract. Skill-only and **formatter-independent** — a Prettier/`markdownlint` setup only makes a violation *visible* sooner, it is not the reason the rule exists. No code, no installer, no `vendors.yaml` change. Gate: 45/45 skill validation green.

#### **Added**
* **`documentation-standards` §5 "Markdown Structure (CRITICAL)"** (v1.3 → **1.4**) — binding on every `.md` artifact (TASK, PLAN, ARCHITECTURE, task files, issues, `.AGENTS.md`): **§5.1 table cells are labels, not prose** — hard limit ≤ 120 characters and one sentence per cell, never `<br/>` / a bulleted list / a code block / a nested table inside a cell; overflow keeps a short marker in the cell and moves the detail to a "Details by ID" section keyed by the same id (worked example included), with the *why* spelled out for both the with-formatter case (column padding rewrites every row, hiding the real change in a twenty-line diff) and the worse without-formatter case (nothing re-aligns the pipes, so the table stops being a table in raw form — which is how `git diff`, terminals and preview-less editors read it). **§5.2 prose is structured, never a wall** — paragraph ≤ 5 lines, ≥ 3 parallel items → a list, nesting ≤ 2 levels, section > 40 lines → sub-headings. **§5.3 line length** — hard-wrap prose at 100 characters (match the project's `printWidth` where one exists), URLs/tables/code blocks exempt. **§5.4 self-check** — two copy-pasteable one-liners (`awk` widest-line + over-limit count; a padding-share probe where > ~15% means prose is stuck in table cells). Sections renumbered: Artifacts → §6, Resources → §7.

#### **Changed**
* **§1 Red Flags** — three new anti-rationalizations, each naming the concrete cost rather than the aesthetic: *"I'll put the full explanation in the table cell"* (a table is a scanning device; prose in a cell destroys scanning and churns every row on any edit), *"It's all one topic, so it's one paragraph"* (topic is not structure — a reader needs entry points), *"Line length doesn't matter, editors soft-wrap"* (`git diff`, review comments and blame are line-granular).
* **Rationalization Table** — two new rows: *"The table is the natural place for this detail"* (a table answers *which* and *how much*; it cannot answer *why* — that is a paragraph) and *"Reformatting the doc is cosmetic churn"* (structure is what makes a document auditable months later; an unreadable artifact is an absent one).

### **v3.21.0 — Quality feedback loop: `run-feedback` engine + Retro Global Protocol + `/heal-issues` harness**

Closes the "run errors evaporate" gap end-to-end: deterministic **capture** (end-of-run Retro step, opt-in Claude Code hooks, transcript miner) → LLM **triage** → deterministic **filing** into the `known-issues-format` ledger / project backlog → bounded **self-healing**. Task 089; plan hardened by a 3-critic VDD-adversarial pass (40+ findings folded in). Gates: 105 unit tests + scripted E2E green, `check_contract_sync.py` green, 45/45 skill validation, workflow smoke, security lint.

#### **Added**
* **`run-feedback`** skill (TIER 2, hybrid; skill count 44 → **45**) — stdlib-only CLI `scripts/run_feedback.py` (`collect / triage / file / journal / issues / mine / claim / release / doctor`): fingerprint dedup that EXCLUDES the capture source (hook- and transcript-captures of one failure collapse; `sources[]` union), machine state under gitignored `.agent/feedback/` (inbox + flock/fsync monthly journal), create-only lockstep ledger writes with rollback + category-section routing, messy-ID-tolerant allocation (`TF-X-7`, `XLSX-10B-DEFER`), anchored backlog appends (missing anchor → exit 4, never blind EOF), redaction + excerpt caps, per-repo `docs/feedback/config.json`. Own Apache-clean error envelope — schema-compatible with, NOT a byte copy of, the proprietary office `_errors.py` (license firewall).
* **Capture surfaces**: opt-in fail-silent hooks (`RUN_FEEDBACK_HOOKS=1`; PostToolUse(Bash) + SessionEnd; worktree-safe via `git rev-parse --git-common-dir`; experimental until a `RUN_FEEDBACK_HOOK_DEBUG=1` payload dump confirms the shape) and the transcript miner (`mine`): enumerates ALL per-cwd `~/.claude/projects/` shards under the repo root, incremental byte offsets, retry aggregation, `--dry-run` first.
* **`/heal-issues`** workflow + command — consumes `issues --status open --json`: strict `auto_fixable: true` opt-in, run-lock, clean-tree + base-branch preconditions, repro ONLY from fenced `sh` blocks (never synthesized from prose), ≤3 iterations / ≤2 lifetime attempts, replication-protocol + protected-paths + diff-size rails, gate timeouts, branch-only output (NEVER push/merge/PR), no silent outcomes. Scheduling is operator-side opt-in only (no repo cron — honest-scope). Aborted-run recovery: Phase 0 detects a journal `heal_run start` without an `end` (a mid-flight death leaves an uncommitted fix, unflipped ledger, stale branch) and demands finish-or-reset instead of a bare "dirty tree" failure; Phase 4 writes the `end` tombstone on EVERY exit path before the final line.
* **`/run-feedback`** command (ad-hoc collection, any session; `mine` hint supported).
* **`init` subcommand + Bootstrap protocol** — self-serve setup for unconfigured repos: `run_feedback.py init` copies both config templates into `docs/feedback/` (create-only, never overwrites) and seeds the `component→prefix` map from the existing ledger's messy IDs (`TF-X-7` → `TF-X`; conflicts reported, never guessed); `doctor` nudges toward it when running on built-in defaults. SKILL.md §7 "Bootstrap protocol": an agent that hits findings in an unconfigured repo bootstraps itself and finishes the judgement `todo` (backlog anchor, heal gates, prefix rows). Suites made hermetic against operator-level capture env flags.

#### **Changed**
* **Retro Global Protocol** wired into all **17 terminal workflows** (claim blockquote at start + non-blocking Retro step before the verdict); deterministic nesting via `claim`/`release` flock (exit 6 = nested → skip). CLAUDE.md / GEMINI.md registries updated in lockstep; `System/Docs/SKILLS.md` row added.
* **`known-issues-format`** contract extended in lockstep (SKILL.md + seed template; sync gate green): optional automation keys after `slug` (`component`, `fingerprint`, `evidence_paths`, `auto_fixable`, `finding_ref`), read-tolerance for per-project extensions (`status: handled`, `severity: MED`), `heal-issues (…)` `resolved_by` tokens.
* **Docs**: new operator guide [`System/Docs/QUALITY_FEEDBACK_LOOP.md`](System/Docs/QUALITY_FEEDBACK_LOOP.md) — architecture, capture surfaces (incl. the verified HK-1 PostToolUse limitation and the mine-on-SessionEnd pivot), heal rails, consumer-project setup, Stage 0→1 operations, dogfood evidence; `heal-issues` row added to `System/Docs/WORKFLOWS.md` (Automation Loops); cross-links from `SKILLS.md`/`CLAUDE.md`/`GEMINI.md`/`README.md`.

### **v3.20.17 — Cleared the VDD-adversarial findings on the KNOWN_ISSUES system (enterprise hardening)**

A fresh-context adversarial review (`docs/reviews/vdd-adversarial-known-issues-format.md`) returned WARNING on the v3.20.14–16 work: 1 MED (the format contract lived in 3 self-contained copies and 2 glosses had already drifted) + 5 LOW + 2 NIT, all verified. This release clears every finding and — for the MED — adds an **automated drift gate** rather than a one-time reconcile. Task 088, gate artifact `docs/reviews/framework-audit-088.md`. Exit bar re-run → **PASS**.

#### **Added**
* **`known-issues-format/scripts/check_contract_sync.py`** — a CI-gateable gate (exit `0`/`1`/`2`) that fails if the format contract (status/severity vocab, frontmatter key set, index-line format) drifts between the skill authority (`SKILL.md`) and the seed template. Wired into the skill's **Script Contract** + **Validation Evidence**; the skill is now `hybrid`, not prompt-only. This is the enterprise upgrade over the manual reconcile the finding literally caught mid-drift.

#### **Fixed** (each maps to a verified review finding)
* **MED** — reconciled the drifted glosses across `SKILL.md`, the template, and the live ledger (`SEV-3 (degraded)` → `(degraded / annoying)`; `by-design (intended trade-off)` → `(…, not a defect)`) and guarded them with the gate above.
* **LOW** — the seed template comment credited the wrong owner (`artifact-management` → **`known-issues-format`**).
* **LOW** — the slug rule asserted a machine equality (`slug == slugify(id)-slugify(title)`) that the repo's own `AT-7` (`Async spawn ≠ sync return`) violates; softened to "a slugified, human-readable id+title (normalize symbols, e.g. `≠`→`not`)".
* **LOW** — the ambiguous seed instruction ("keep everything down to the second `---`") is unified across template / skill / example to "keep Purpose + Rules/Conventions (above the first `## <category>`); delete the seed comment and the `_No issues recorded yet._` block".
* **LOW** — read-path steps ("Read `docs/KNOWN_ISSUES.md`") in `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` + `01-start-feature.md` / `vdd-01-start-feature.md` now say **"skip if absent — created on the first filed issue"** (create-if-absent is write-path only) and name `known-issues-format` (TIER-2 discoverability).
* **NIT** — commented `resolved_at` / `resolved_by` keys added to the frontmatter schema examples (skill + template).
* **LOW (history-honesty)** — see the v3.20.15 note below: 086→087 were squashed into one commit.

### **v3.20.16 — KNOWN_ISSUES format extracted into a dedicated `known-issues-format` skill**

Architectural-consistency follow-up to v3.20.15. v3.20.15 had put the format contract **and** the seed template inside the TIER-0 `artifact-management` hub — but that hub is a **management** skill that everywhere else *delegates* format (archiving → `skill-archive-task`; `ARCHITECTURE.md` structure → `architecture-format-core`) and had held **zero** templates. This release restores that invariant: KNOWN_ISSUES gets its **own** format skill, mirroring how `ARCHITECTURE.md` (also a living, non-planning artifact) has `architecture-format-core`. Task 087, gate artifact `docs/reviews/framework-audit-087.md`. No code/installer change.

#### **Added**
* **`known-issues-format`** skill (TIER 2, created via the mandatory `init_skill.py` gate) — the single **format authority** for `docs/KNOWN_ISSUES.md`: frontmatter schema, prefix→category table, status/severity vocab, index-line format, per-issue recipe, and create-if-absent. It **owns the seed template**, now at `assets/templates/known_issues_md_template.md` (moved out of the hub, renamed to the `<artifact>_md_template.md` convention used by `skill-planning-format` / `documentation-standards`). Skill count 43 → **44**.

#### **Changed**
* **`artifact-management` (TIER 0, v1.2 → 1.3)** slimmed back to its role: it lists `KNOWN_ISSUES.md` as a living Global Artifact and keeps the **create-if-absent** rule, but the detailed format contract is gone — replaced by a one-line **delegation** to `known-issues-format` (parallel to its existing ARCHITECTURE → `architecture-format-core` delegation). The hub once again holds **no** template assets.
* **`skill-reverse-engineering` §2 (v1.3 → 1.4)** repointed at `known-issues-format` (and its `assets/templates/…` seed) instead of the hub.
* **`System/Docs/SKILLS.md`** — new `known-issues-format` row; the `artifact-management` row reworded to "owns lifecycle, delegates format".

#### **Fixed**
* **Placement inconsistency from v3.20.15.** The template was the first-ever asset in the management hub, and the format contract was duplicated there rather than owned by a format skill. Both are corrected; there is now a single source for the KNOWN_ISSUES format that the hub and reverse-engineering both delegate to.

### **v3.20.15 — KNOWN_ISSUES thin-index format is now framework-resident (portable to new projects)**

> **History note:** v3.20.15 and v3.20.16 landed in a **single commit** (`1ca49cf`); 086 was refactored by 087 before either was committed. This entry is **descriptive** — the intermediate state it describes (the template under `artifact-management/assets/`) never existed as a checkoutable path in git history.

Follow-up to v3.20.14. The thin-index format rules were trapped in **this repo's** `docs/KNOWN_ISSUES.md` — a project artifact never shipped to new projects — so an agent bootstrapping a **clean** project would not know the layout and would reinvent a flat list. This release moves the format contract into the framework layer (a TIER-0 skill + a shipped template), with **no code and no installer change**. Task 086, gate artifact `docs/reviews/framework-audit-086.md`. Seed mechanism **B (skill-driven)** — operator-selected.

#### **Added**
* **`assets/KNOWN_ISSUES.template.md`** under `artifact-management` — a **project-agnostic, rules-only** seed (Purpose + Rules/Conventions: frontmatter schema, a generic prefix→category starter table, status/severity vocab, index-line format, "Adding a new issue" recipe) with an empty `_No issues recorded yet._` state. It ships to every new project automatically via the existing `.agent/skills` link — **no `vendors.yaml`/installer change**.

#### **Changed**
* **`artifact-management` (TIER 0, v1.1 → 1.2)** now lists **`KNOWN_ISSUES.md`** as a living Global Artifact and carries a compact **"Known Issues (thin index)"** contract: one file per issue under `docs/issues/`, the index-line format, the hand-maintained/no-generator rule, and a **create-if-absent** step (materialize `docs/KNOWN_ISSUES.md` from the template on first issue). Because this skill is loaded at every session start, an agent learns the format **before any file exists**.
* **`skill-reverse-engineering` §2 (v1.2 → 1.3)** — its "record findings in KNOWN_ISSUES" pointer now defers to the framework-resident `artifact-management` contract (and its template) instead of *"that file's Rules/Conventions section"*, which **dangled in a fresh project** where the file/section doesn't exist yet. Repo-specific `AT`/`WR` prefix wording was generalized.

#### **Fixed**
* **Portability gap identified in v3.20.14.** New projects had no framework-level source for the KNOWN_ISSUES format; the reverse-engineering write-path pointed at a project artifact that may not exist. Both are now resolved at the framework layer.

**Rejected (safety):** seeding `docs/KNOWN_ISSUES.md` via the installer's `copy` action — `_remove_install` (`cli.py:289-294`) deletes every `copy` component on `uninstall`/`switch`, which would **destroy a project's accumulated issue history**. Mechanism B keeps the file project-owned (the installer never references it), uninstall-safe by construction.

### **v3.20.14 — `KNOWN_ISSUES.md` restructured into a thin index + per-issue files (obsidian-llm-wiki layout)**

`docs/KNOWN_ISSUES.md` was a flat 22-line checklist; it is now a **hand-maintained thin index** (Rules/Conventions + category groups, one line per issue) with every issue split into its own file under `docs/issues/<slug>.md` — mirroring the `obsidian-llm-wiki` schema, adapted to a non-vault repo (standard Markdown links, not Obsidian wikilinks). A repo-wide drift audit followed; **nothing broke** — the file path is unchanged. Task 085, gate artifact `docs/reviews/framework-audit-085.md`.

#### **Added**
* **10 per-issue files under `docs/issues/`** — one file per known issue with YAML frontmatter (`id`, `type: known-issue`, `status`, `opened_at`, `category`, optional `severity`, `slug`) + body; the full original text is preserved verbatim (**0 dropped clauses**). IDs: `AT-1..AT-9` (agent-teams / Layer-B limitations) and `WR-1` (wrapper↔SOT drift). Opened dates are git-truthful (2026-04-17 / 2026-06-10).
* **"Rules / Conventions" section in `docs/KNOWN_ISSUES.md`** — the hand-maintenance rules: the ID prefix→category table, status/severity vocabularies, the index-line format, and an explicit **"Adding a new issue"** recipe. This repo has no `wiki-index-render` tooling (unlike the source vault), so the index is maintained by hand and its coupling is documented for agents.

#### **Changed**
* **`docs/KNOWN_ISSUES.md` is now a thin index** — Purpose + Rules + `## agent-teams` / `## wrappers` groups with one link-line per issue. Same path, so all existing references (README, `CLAUDE/AGENTS/GEMINI.md`, `ARCHITECTURE.md`, the pipeline context-read steps) still resolve.
* **`skill-reverse-engineering` §2 "KNOWN_ISSUES.md Updates" (v1.1 → 1.2)** — now directs the agent to file each finding as its own `docs/issues/<slug>.md` + one index line per the Rules recipe (**not** a flat `- [ ]` append), and to add a new prefix→category row for reverse-engineering findings. This was the one live automation write-path that populates KNOWN_ISSUES.
* **`docs/ROADMAP.md` Wave-4 blocking gotchas deep-linked** — the four inline gotchas now link to their canonical `issues/at-6..at-9.md` (summary text kept), removing a content-duplicate that would drift once `AT-6` (currently `open`, SEV-2) is resolved.

Drift audit: **26** live/coupled references classified and adversarially verified → **6 real** (2 `Should` applied above, 4 `Optional` documented and deferred: `references/claude-code.md` inline gotchas, `references/_stub-template.md` wording, `README.md`/`README.ru.md` RE starter prompt). No historical records (docs/tasks · plans · reviews · CHANGELOG · archive) were touched. Backups in `.agent/archive/`.

### **v3.20.13 — Bounded gated loops + cross-harness portability for the `full-robust` and `vdd-enhanced` pipelines**

The two composite pipelines now spell out their loop semantics (gate → bounded retry → explicit escalation) and how to run them on any supported harness (Claude Code, Codex, Cursor, Gemini CLI, Antigravity) with any LLM. Workflow prose only — no other workflow, skill, prompt, bootstrap file, or code changed. Task 084, gate artifact `docs/reviews/framework-audit-084.md`.

#### **Changed**
* **`full-robust.md` rewritten from a 3-line linear script into a gated pipeline.** Each step now has a gate and a failure branch: the VDD step stops the pipeline if its inner loops escalated; the security step bounds the sub-workflow's open-ended "fix → re-scan until clean" loop at **max 3 iterations** at the caller, then escalates; the vague "final documentation update" now points at `.agent/workflows/04-update-docs.md`. Added the **opt-in `vdd-multi` coverage gate** (`--no-fix --fail-on=high`, one fix + one re-run, then escalate) that `vdd-multi.md` §Integration had declared but the pipeline never referenced — marked optional per the ab-experiment-075 positioning (coverage/CI tool, not the default review path).
* **`vdd-enhanced.md` loops completed.** Phase 2 gained the missing **Escalation** clause (parity with Phase 1: 3 failed validator retries → STOP and ask the user); Phase 3 gained a caller-side **regression gate** (full suite must pass; max 2 fix-and-rerun rounds via `03-develop-single-task`, then escalate — never enter adversarial review with a red suite); Phase 4 gained an **outer cap of 3 adversarial cycles** on top of the objective-convergence termination bar (0 CRITICAL, only bikeshedding left — never approve invented nitpicks).
* **Both pipelines are now vendor- and model-portable by construction.** Every sub-workflow reference is a readable `.agent/workflows/*.md` file path with the slash command shown as a Claude-Code-only alias; a new **"Vendor dispatch & model portability"** section in each file defers to `skill-parallel-orchestration` §1.1/§7 for runtime resolution (native subagent adapters, sequential role-switching as last resort); a **loop-protocol note** states the cross-LLM invariant: gates are deterministic scripts and structured verdicts (never model self-assessment), gate errors are fed back verbatim into retries, and state is checkpointed at every phase boundary so small-context models can resume from `.agent/sessions/latest.yaml`.
* **`System/Docs/WORKFLOWS.md`** pipeline rows for Full Robust / VDD Enhanced updated to describe the bounded loops and list the `/full` and `/vdd` aliases.

#### **Fixed**
* **Phantom slash commands.** The pipelines referenced commands that don't exist (`/vdd-enhanced`, `/01-start-feature`, `/02-plan-implementation`, `/05-run-full-task`) — real aliases are `/vdd`, `/start-feature`, `/plan`, `/develop-all` (verified against `.claude/commands/`). On non-Claude harnesses these references are now plain file paths, which is the only form that works everywhere.
* **Stale "(future) Security audit"** wording in `full-robust.md` — the security-audit workflow has existed since it was first referenced in Step 2.
* **`05-run-full-task.md` could auto-commit into the void.** Its Finalization said "If Pass: Commit changes" with no failure branch. It now has the same bounded gate as the rest of the family: on a red suite, re-enter `03-develop-single-task` (max 2 attempts), re-run, then escalate — **never commit on a red suite**. The "Run Full Task" row in `System/Docs/WORKFLOWS.md` was synced. (Operator-approved scope expansion, R8.)
* **Two long-broken root tests repaired** (pre-existing, exposed by this task's regression gate): `tests/test_product_scripts.py` failed collection with `ModuleNotFoundError: init_product` because it still imported from `System/scripts/` after the product scripts moved into skills — it now uses the same `load_module_from_path` pattern as its sibling; `tests/test_product_skills.py::test_wsjf_calculation_logic` passed row tuples in an obsolete 3-element shape — aligned with `calculate_wsjf`'s actual `(line, cells)` contract. Root suite: 227 passed, 0 failed.
* **Light Mode loops bounded (operator-approved, R10).** `light-02-develop-task.md` had two unbounded loops — "If tests fail: Fix and re-run (loop)" and "If issues found: Return to Step 1" — the same defect class this release fixed in the main pipelines. Now: max 3 test-fix attempts, max 2 review cycles; exhausting either bound triggers the workflow's existing Escalation path (repeated failures mean the task is not trivial → standard pipeline). The Light Mode row in `System/Docs/WORKFLOWS.md` was synced.
* **Second-round follow-ups cleared (operator-approved, R9).** The same phantom-command pattern was purged from three more workflows — `base-stub-first.md`, `light-01-start-feature.md` (including a transition to a `/light-02-develop-task` command that never existed), `light-02-develop-task.md` — all sub-workflow references are now portable `.agent/workflows/*.md` paths with real Claude Code aliases. `tests/test_mock_agent.py` no longer writes into `docs/tasks/` on every run (output moved to pytest `tmp_path`; the committed `docs/tasks/mock_results/` test artifact was removed from the repo). The `calculate_wsjf` docstring now matches the function's real signature and return shape.

### **v3.20.12 — Corrected description of the framework's helper tools (additional + fallback)**

The framework ships a small set of helper tools — generate a unique archive filename, run tests, check/stage/commit with git, and read/write/list files. A previous release mistakenly described this whole subsystem as obsolete and unused. This release fixes the description only: behaviour, code, and files are unchanged, and nothing was deleted or moved.

#### **Changed**
* **The helper tools now fall into two clear groups.** The archive-filename generator has no equivalent among a coding assistant's own tools, so it is always used — run it with `python3 .agent/tools/task_id_tool.py <name>`. The rest (run tests, git, file read/write/list) duplicate what an assistant already does on its own, so they act as a **fallback** for assistants that lack those built-ins. The code that runs an individual tool is implemented and tested; the piece that would let an assistant drive these tools by itself is documented honestly as **not yet built**.
* **The tool list was restored in the assistant setup files** — `AGENTS.md` (Cursor, Codex) and `GEMINI.md` (Gemini CLI, Antigravity) — where the previous release had removed it. Each entry was written to match that assistant's own official documentation for running commands and adding extra tools. The Claude Code setup file was already correct and left unchanged.
* **Supporting documents were brought in line** — `ORCHESTRATOR.md`, `SOURCE_OF_TRUTH.md`, `SKILLS.md`, and `RELEASE_CHECKLIST.md` now present the subsystem as additional/fallback tools, and a leftover reference to a tool that never actually existed was corrected. Nothing was archived; all automated checks pass.

### **v3.20.11 — Vendor-Currency: Tool-Layer Reword + GEMINI.md Symlink Re-sync**

Follow-up to the `System/Agents` cross-vendor audit (items 1, 2, 4; item 3 — version-header re-stamp — intentionally skipped). **Framing-only, zero pipeline-behavior change.** Task 082, gate artifact `docs/reviews/framework-audit-082.md`. Scope: "reword prompts only" — `schemas.py` / `tool_runner.py` / `ORCHESTRATOR.md` left in place. Gates 43/43, pytest 30/30.

#### **Changed**
* **Dead tool-dispatch framing retired** in the two core role-prompts and two bootstrap files. `00_agent_development.md`, `01_orchestrator.md`, `AGENTS.md`, `GEMINI.md` no longer instruct the orchestrator to call a standalone-Python `run_tests` / `git_status` / `git_ops` / `file_ops` / `execute_tool` dispatcher (imported only by its own tests; used by **no** current vendor harness). They now say: use your harness's **built-in** file/shell/search tools, and run repo Python helpers via the shell. `CLAUDE.md` was already correct and is **unchanged** (it is the donor template). `System/Docs/ORCHESTRATOR.md` is now referenced as **legacy**.
* **`task_boundary` fiction removed.** `00_agent_development.md` (General Concept, §2, anti-patterns) and `GEMINI.md` (workflow dispatch) no longer describe a `task_boundary` tool/protocol for state tracking; state is persisted via `skill-session-state` (`update_state.py`) at phase boundaries.

#### **Fixed**
* **GEMINI.md symlink-resolution gap.** Gemini CLI's bootstrap file was a stale fork (~v3.15) missing the **SYMLINK RESOLUTION** + **SYMLINK-AWARE COMMAND DEFAULTS** protocol that `AGENTS.md` received in v3.19.1. Ported both sections — closes a silent skill-load failure when the framework is deployed via symlinks (Gemini's `find`/`rg` skip symlinks by default).

### **v3.20.10 — Item 6 In-Repo Complete: Antigravity Adapter + Vendor Dispatch (6d) + Wave-5 Generator (6e)**

Finishes the **in-repo** half of roadmap item 6 (C-07). After this, item 6's only remaining piece is **operator e2e validation on real CLIs**. Task 081, gate artifact `docs/reviews/framework-audit-081.md`. Doc/script-only, gates 43/43, pytest 30/30; the only severity escalation in the merge logic remains R3b.

#### **Added**
* **Google Antigravity adapter** (4th vendor) — `references/antigravity.md` stub→full, verified via web (primary docs render client-side; corroborated from antigravity.google/docs/agent-manager + Google-Cloud/Medium + DataCamp + gemini-cli discussion #27305). **Dynamic-first** architecture documented (orchestrator spawns subagents on the fly, no config files) alongside the static **custom-agent** form (`agent.json` at `~/.gemini/antigravity-cli/agents/<name>/`). Async parallel ✅. **Detection ambiguity recorded honestly** — Antigravity shares `AGENTS.md` (Codex) and `~/.gemini/` (Gemini); a provisional `.antigravity/` marker is used pending validation.
* **Wave-5 wrapper generator (6e)** — `scripts/generate_wrappers.py` + `scripts/wrappers_manifest.json`: one manifest → **12 critic wrappers** across 4 scaffold vendors (Gemini MD+YAML, Codex TOML, Cursor MD+YAML, Antigravity JSON) in their native formats, all pointing at the same SOT skills + enum. Claude Code **excluded** (validated reference/donor, hand-maintained). `--check` mode exits non-zero on drift (CI-gateable). Hand-sync of scaffold wrappers is eliminated.

#### **Changed**
* **6d — sequential-fallback demoted** (C-07 "functionally equivalent" claim **removed** from `vdd-multi.md` + `SKILL.md §7`): `vdd-multi`'s "Fallback (Sequential)" section is now "**Vendor dispatch**" — resolve the runtime (skill §1) → use its native parallel adapter (Codex/Cursor/Antigravity ✅, Gemini Layer-A pending); sequential role-switching is the **documented last resort** (primitive-less runtime / single-session debug / 1-slot CI), explicitly **not** functionally equivalent to parallel. All flags + the evidence contract honored on every path.
* **6e — drift-grep extended** (`KNOWN_ISSUES.md`) to all 5 wrapper dirs (`.claude/.gemini/.codex/.cursor/.antigravity/agents/`); documents that scaffold wrappers are generated (edit the manifest, run the generator, never hand-edit).
* Detection table (`SKILL.md §1.1`) Antigravity row updated (provisional marker + ambiguity). `skill-parallel-orchestration` 3.6→3.7.

#### **Still open under item 6**
* **Operator e2e validation** on real Codex / Cursor / Antigravity / Gemini installs — graduates each ⚠️ SCAFFOLD → ✅. Until then the banners stay and sequential remains the proven path. **Roadmap item 6 stays 🔜 (6a–6e in-repo ✅ · validation ⏳).**

---

### **v3.20.9 — Vendor Adapter Scaffolds: Codex / Gemini / Cursor (roadmap item 6, sub-tasks 6a–6c, in-repo portion)**

In-repo scaffolds for parallel-critic dispatch on three non-Claude runtimes, authored from **primary-source docs** (geminicli.com, developers.openai.com/codex, cursor.com — verified in-session 2026-06-10). **Everything ships ⚠️ SCAFFOLD — not yet validated on real runtimes**; graduation to ✅ requires one operator-run `/vdd-multi --no-fix` per CLI (hardware/accounts the operator does not have right now — explicitly deferred). Task 080, gate artifact `docs/reviews/framework-audit-080.md`. Doc-only diff, gates 43/43, pytest 30/30.

#### **Added**
* **Three vendor references** (`skill-parallel-orchestration/references/`): `codex-cli.md` (NEW), `gemini-cli.md` + `cursor.md` (stub→full), each at `claude-code.md` depth — concept→primitive mapping, Layer A pattern, read-only critic enforcement, wrapper catalog, validation gate.
* **Nine thin critic wrappers** at real runtime paths, all pointing at the same SOT skills (`vdd-adversarial`, `skill-adversarial-security`, `skill-adversarial-performance`) with the same `clean-pass | issues-found | bikeshedding-only` enum: `.codex/agents/critic-*.toml` (×3, `sandbox_mode="read-only"`), `.gemini/agents/critic-*.md` (×3, read-only `tools`), `.cursor/agents/critic-*.md` (×3, `readonly: true`).
* **Detection table** (`SKILL.md §1.1`) gains a Codex row (`.codex/agents/`); Gemini/Cursor statuses restated as "Scaffold — documented, not validated". First-match-wins keeps Claude Code precedence in this repo.

#### **Verified against primary docs**
* **Codex CLI** — TOML in `.codex/agents/`; **parallel confirmed** ("spawns in parallel, waits for all, consolidates"); `sandbox_mode="read-only"` maps to the read-only critic guarantee.
* **Cursor 2.4** — Markdown+YAML in `.cursor/agents/`; **parallel confirmed (max 10)**; `readonly: true` is purpose-built for reviewer subagents; `is_background` = async (Layer B, deferred).
* **Gemini CLI** — Markdown+YAML in `.gemini/agents/`; **⚠️ parallel multi-spawn NOT documented** (only auto-delegation + `@subagent`). The scaffold records this gap honestly and corrects the roadmap's earlier optimistic "concurrent subagents" note; the multi-critic flow on Gemini stays sequential-delegation until a real run proves Layer A.

#### **Deferred (still open under item 6)**
* e2e validation on real CLIs (operator action), 6d (sequential-fallback demotion + `vdd-multi` "Vendor dispatch" rewrite), 6e (drift-grep extension + Wave-5 wrapper generator). `skill-parallel-orchestration` 3.5→3.6. **Roadmap item 6 stays 🔜 — scaffolds authored, not validated.**

---

### **v3.20.8 — Tier-Diverse Escalation Demoted to Tag-Only (mini-exp 078 refuted the premise)**

The R3c tier-diverse `+1` escalation shipped in v3.20.7 was an explicit **pilot**. Mini-experiment 078 (`docs/reviews/tier-diverse-experiment-078.md`, fresh sealed corpus, 3 arms, 18 bugs) **refuted its sole premise**: cross-tier critic agreement was *less* precise than same-tier (overlap precision **0.66 vs 0.73**), so escalating severity on it would manufacture false positives. This release translates that finding into the rule — the escalation is **demoted to a `tier-diverse` provenance tag with no `+1`**. The `--models` config is **retained** (078 validated it as a recall/coverage tool: D-tier hit the highest recall, 100% pooled). Task 079, gate artifact `docs/reviews/framework-audit-079.md`. **Zero mechanics regression** beyond the intended demotion; gates 43/43, pytest 30/30, doc-only.

#### **Changed**
* **Merge rule 3 gradation, middle row + third bullet** (lockstep, byte-identical mod critics↔teammates across `vdd-multi.md` Phase 2 + `skill-parallel-orchestration` §6): "Same vendor, different tier → +1 for CRITICAL/HIGH" → "**no escalation — `tier-diverse` tag only**", with an inline 078 citation. The bullet now tags provenance without a severity bump.
* **`--models` config kept; Phase 0 resolution simplified:** the flag, parse, and per-critic spawn are unchanged (recall tool); Phase 0 step 5 now resolves a *provenance tag* (`corroborated` / `tier-diverse`) instead of an escalation tier. Env-flatten note reworded: when `CLAUDE_CODE_SUBAGENT_MODEL` collapses the config, downgrade the tag to `corroborated` (no escalation to withhold — the tag just tells the truth).
* **Cross-refs synced** (`usage_example.md`, `claude-code.md` Model-pin hygiene §, `vdd-multi` Positioning block): tier-diverse = recall tool + provenance tag, escalation demoted; the still-open lever is **true cross-vendor** critics (⏳ item 6 — 078 tested tiers, not vendor independence). `skill-parallel-orchestration` 3.4→3.5.
* **Untouched:** R3a (`corroborated`), R3b (different-mechanism `+1` — the only surviving escalation), R3d (sequential never-escalate), dedup rule 1, rules 2/4/5, the evidence contract (074), and all flags.

> This closes the loop on the VDD discipline: R3c shipped as a pilot (077), was validated on a sealed corpus (078), and is corrected by data here (079) — only mechanism-difference escalates now.

---

### **v3.20.7 — R3c Tier-Diverse Escalation: Model Heterogeneity Re-earns a Guarded +1 (audit-067 C-08, roadmap item 7 — last open slice)**

Closes the final slice of claim **C-08**: severity-escalation merge rule 3 gains a **model-independence axis**. Same-model critic agreement stays corroboration-only (R3a, task 072); under a **tier-diverse** `--models` config (critics on different model tiers within one vendor) same-mechanism agreement now earns +1 **for CRITICAL/HIGH only** (tag `tier-diverse`). The cross-vendor row stays ⏳ blocked by vendor adapters (item 6). Motivated by experiment 075 rule 2 (same-model committee fails its cost bar → heterogeneity is the remaining lever). Task 077, gate artifact `docs/reviews/framework-audit-077.md`. **Zero mechanics regression** — additive config (absent `--models` → unchanged R3a behavior); gates 43/43, pytest 30/30, doc-only.

#### **Changed**
* **Merge rule 3 — model-independence gradation** (lockstep, byte-identical modulo critics↔teammates across `vdd-multi.md` Phase 2 + `skill-parallel-orchestration` §6, normalized-diff-verified): new 3-row gradation table (same-model none / same-vendor-tier-diverse partial / cross-vendor quasi-independent) + a third bullet for the tier-diverse case. R3a/R3b/R3d bullets byte-unchanged.
* **`/vdd-multi --models=logic:<t>,security:<t>,performance:<t>`** (`<t>` ∈ haiku/sonnet/opus/fable): Phase 0 parses the map + resolves the run's `escalation_tier`; Phase 1 spawns each critic on its assigned tier. Partial maps allowed; unset critics fall back to the wrapper default (opus).
* **Env-flatten guard:** Phase 0 detects `CLAUDE_CODE_SUBAGENT_MODEL` (which silently overrides per-critic pins), warns, and **downgrades escalation to R3a** — never awards the `tier-diverse` +1 on a heterogeneity the env erased.
* Sequential fallback: tier-diverse declared **impossible** (single instance) — gradation N/A, stays never-escalate. `usage_example.md` + `claude-code.md` Model-pin hygiene § cross-referenced. `skill-parallel-orchestration` 3.3→3.4.
* **Ships as a pilot** — the tier-diverse +1 is theory-grounded (partial within-family independence, arXiv:2506.07962/2601.12307); empirical payoff is under validation in the experiment-075 follow-up (task 078).

---

### **v3.20.6 — Evidence-Based Repositioning of vdd-multi / K1 / K2 (ab-experiment-075 rules 1–3) + Corpus Documentation**

Applies the pre-registered verdicts of A/B experiment 075 (`docs/reviews/ab-experiment-075.md`, Task 075: 240 runs, 24 sealed seeded bugs, frozen scorer) to the framework's positioning text — **zero mechanics changed** (merge rules, flags, evidence contract, exit bars all byte-identical; gates 43/43, pytest 30/30). Task 076, gate artifact `docs/reviews/framework-audit-076.md`.

#### **Changed**
* **`/vdd-multi` repositioned (rule 2 FAILED its cost bar):** new "Positioning" block — coverage & CI-gating tool, not the default review path (+5.6pp < +10pp over best single reviewer at 3.25× tokens and higher FP; but the only arm at 100% pooled recall). Default for routine recall-oriented review = single strong reviewer with the plain exhaustive prompt. Remaining lever: R3c model-heterogeneous critics.
* **`vdd-adversarial` 1.4→1.5 (rule 3 FAILED):** empirical-positioning note — **precision tool, not recall lever** (−6.9pp recall vs plain baseline; −16% FP; bikeshedding 3.9% vs 13.0%). Load when noise cost dominates; plain exhaustive prompt for recall-critical passes.
* **`vdd-sarcastic` 1.4→1.5 (rule 1 SURVIVED):** stale "awaits the A/B" disclaimer → resolved **KEPT** (+4.2pp vs neutral-adversarial at lower FP; full ordering still puts the plain baseline above both skins).
* **Corpus documentation:** `tests/fixtures/ab-corpus/README.md` (RU, accessible methodology + infographics + verdicts) and `tests/fixtures/ab-corpus/.AGENTS.md` (all python modules incl. per-file seeded-bug roles, all data artifacts, seal invariants).
* Roadmap: item 13 follow-ups marked done; R3c pilot remains the open lever.

---

### **v3.20.5 — Orchestrator-Supplies-Evidence Contract (audit-067 item 11, C-13 + P0 item 2 residual)**

Closes the critic capability asymmetry: critics (`tools: Read, Grep, Glob`) cannot execute tests/scanners, yet their shared exit bar requires "the full test run has actually been executed". Chosen direction per roadmap (Bash for critics rejected — attack/cost surface, read-only guarantee): **the orchestrator runs the evidence commands and injects results into every critic prompt**. Also closes the P0 item 2 residual — critic-security no longer legitimately reports `scan: NOT RUN` on every `/vdd-multi` run — and removes experiment 13's known arm-D handicap. Executed as a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-074.md`, Task 074). **Zero functional change**: doc-only diff, pytest 30/30, skill gate 43/43.

#### **Changed**

* **`vdd-multi.md` Phase 1** gains Step 1.0 "Gather execution evidence": orchestrator runs the test suite (summary or `tests: NOT RUN (<reason>)`) and `run_audit.py` (summary or `scan: NOT RUN (<reason>)`) **before** spawning; the prompt skeleton gains an `Execution evidence` block (tests for all critics, scan additionally for critic-security) + the critic-side rule: evidence is INPUT — never re-run or fabricate; a missing block → finding **"exit-bar condition unverifiable — no execution evidence supplied"**, never `clean-pass`. Phase 2 Summary records evidence state; the sequential fallback gets the same contract (step 0 + flag-parity sentence). Merge rules 1–5, enum, and flags byte-unchanged.
* **Exit-bar lockstep ×3** (`vdd-adversarial` 1.3→1.4, `vdd-sarcastic` 1.3→1.4, `vdd-methodology.md` §IV): condition (1) extended with one byte-identical parenthetical — executed by you, or via orchestrator-supplied evidence in critic/subagent mode; neither → unverifiable, report as finding, never approve.
* **Absence-rule clauses** added to the existing critic-side groundwork: `skill-adversarial-security` §3 (1.3→1.4) and `skill-adversarial-performance` Termination cond 1 (1.2→1.3). `skill-parallel-orchestration` 3.2→3.3 (`sequential-fallback.md` concrete pattern step 0 + evidence lines in persona messages; anti-pattern line aligned: target + shared evidence block = legitimate persona input). Critic wrappers untouched (thin-wrapper anti-drift discipline — the rule lives in SOT skills + the Phase-1 prompt).

> **Acceptance evidence:** `exit-bar condition unverifiable` grep → exactly the 7 contract files; the 3 lockstep parentheticals hash-identical (1 unique md5); merge-rule/enum/flag lines 0 touched in diff; skill gate 43/43; pytest 30/30; `.md`-only diff.

---

### **v3.20.4 — P2 "Aging" Batch: Fresh-Context Rationale, Model-Pin Hygiene, Two-Layer Audit Model, Perf-Critic Objective Bar (audit-067 items 8/9/10/12, C-02/C-06/C-10/C-16)**

Closes the four independent P2 claims in one `/framework-upgrade` cycle (the roadmap's own suggested batch), gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-073.md`, Task 073). In all four cases the **practice is unchanged** — only the rationale/contract text is modernized. **Zero functional change**: doc-only diff, pytest 30/30, skill gate 43/43.

#### **Changed**

* **Item 8 [C-02] — fresh-context rationale re-grounded** (`vdd-adversarial` 1.2→1.3, `vdd-sarcastic` 1.2→1.3, `references/vdd-methodology.md` §II.3 + §V.4, `.agent/workflows/vdd-adversarial.md`): the anthropomorphic "relationship drift / AI becoming too agreeable over time" story is replaced by the documented mechanisms — multi-turn assumption lock-in (−39% vs single-turn, arXiv:2505.06120), context rot (Chroma 2025), pushback-driven sycophantic belief updates (TRUTH DECAY / SYCON-Bench). Fresh context per review **stays mandatory** (scored Current in audit-067). Methodology principle V.4 renamed "Context-Interference Resistance (formerly \"Entropy Resistance\")". The workflow file was a 4th location found by blast-radius grep beyond the roadmap's list.
* **Item 9 [C-06] — model-pin hygiene documented** (`skill-parallel-orchestration` 3.1→3.2, new §"Model-pin hygiene" in `references/claude-code.md`; 2-line pin-rationale comment in all 3 `.claude/agents/critic-*.md` frontmatters): tier ladder `haiku < sonnet < opus < fable` (fable exists **above** opus — the wrappers pin opus deliberately for cost/latency; the recall lever is the reporting instruction, not tier); `CLAUDE_CODE_SUBAGENT_MODEL` env **silently overrides** frontmatter pins (flattens tier-diverse configs without warning); `effort` frontmatter field available; severity-threshold literalism hazard (Opus 4.7+ follows "only report high-severity" literally → recall drops; canonical pattern: report everything with confidence + severity, filter downstream). Literalism audit of critic prompt surfaces re-run → clean (071 fixed the only offender).
* **Item 10 [C-10] — regex positioned as deterministic floor** (`security-audit` 3.5→3.6, new §0 "Methodology — Two Layers", §1–§7 numbering unshifted): layer 1 = regex + external scanners (reproducible, cheap, CI-gateable, categorically blind to semantic classes — a clean scan is **not** clearance); layer 2 = LLM semantic pass (long-context taint/logic review, business-logic authz, semantic MCP tool-description poisoning). Frontier evidence cited as rationale (DARPA AIxCC finals 2025, Google Big Sleep, Codex Security / Claude Code Security — audit-067 bibliography). Semgrep licensing footnote added (Semgrep CE since Dec 2024; Opengrep fork as drop-in alternative). `System/Docs/SKILLS.md` registry row synced to v3.6.
* **Item 12 [C-16] — perf-critic termination aligned with the objective bar** (`skill-adversarial-performance` 1.1→1.2): the pre-065 subjective termination ("developer addressed all real issues") replaced by Objective Convergence — evidence condition (orchestrator-supplied execution evidence or honest `tests: NOT RUN`; the critic has no Bash and **never fabricates** results) + the 3-state convergence enum `clean-pass | issues-found | bikeshedding-only`, byte-aligned with its wrapper `critic-performance.md`. (Orchestrator-side evidence contract remains roadmap item 11.)

> **Acceptance evidence (scope: framework sources, excluding `.agent/archive/` rollback copies and `.agent/sessions/` runtime state):** `relationship drift` + `too agreeable` greps → empty; severity-threshold literalism grep over critic surfaces → empty; wrapper↔SKILL enum parenthetical byte-identical; `git diff --stat` shows `.md`-only changes; skill gate 43/43; pytest 30/30. Known pre-existing drift re-flagged, not fixed: `SKILLS.md:53` stale "Mock Runner for POC" row; `skill-parallel-orchestration` §8 stale test reference.

---

### **v3.20.3 — Severity-Escalation Redesign: Same-Model Agreement No Longer Auto-Escalates (audit-067 P1 item 7 partial, C-08 / R3a+R3b+R3d)**

Closes the shippable-now slice of claim **C-08**: the merge rule "two critics independently flagging the same location → escalate severity by one level" assumed critic independence, but all critics are the same base model under different personas — same-model pairs pick the *same wrong answer* ~60% of the time when erring (Correlated Errors, ICML 2025, arXiv:2506.07962; persona ensembles share priors, arXiv:2601.12307). Same-model agreement is **corroboration** (survived persona/prompt variation), not independent **confirmation**. Executed as a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-072.md`, Task 072). **Zero functional change to scripts/tests** — pure rule-text redesign; pytest 30/30, skill gate 43/43.

#### **Changed**

* **Merge rule 3 redesigned in lockstep across all 4 locations** (byte-identical modulo the pre-existing "critics"↔"teammates" noun split, verified by normalized diff):
  - **R3a — no auto-escalation on same-model agreement:** duplicates with the same failure mechanism merge at severity = max (rule 1) and carry a `corroborated` tag ("flagged by N critics — weak positive signal"), instead of +1.
  - **R3b — different-mechanism exception:** two critics flagging the same location with **different failure mechanisms** (e.g., unhandled edge case + exploitable injection at the same line) = two distinct analyses → +1 escalation survives. Mechanism-difference test: the scenarios are not paraphrases of each other — orchestrator judgment, documented in the merged report.
  - Locations: `.agent/workflows/vdd-multi.md` Phase 2 (+ Overlaps placeholder), **`skill-parallel-orchestration` 3.0 → 3.1** §6 (+ §2.3 merge-summary echo), `references/sequential-fallback.md` merge step, `examples/usage_example.md` walkthrough.
* **R3d — sequential fallback explicitly never escalates:** role-switching mode has the weakest independence (same session window, same model instance) — agreement between sequential personas tags `corroborated` only; different-mechanism findings get at most a `priority` flag, never +1. The §Anti-patterns "stronger signal" line aligned to claim corroboration, not independent confirmation.
* Untouched per roadmap discipline: dedup rule 1 (±3 lines), cross-category re-attribution rule 2, bikeshedding filter rule 4, `--severity` filter rule 5, iteration caps.
* **Deferred:** R3c (re-earning escalation via model heterogeneity — per-critic model config, signal-strength gradation table) stays open: its tier-diverse form is available in Claude Code today, its cross-vendor form is blocked by vendor adapters (roadmap item 6). Item 11 (orchestrator-supplies-evidence) also deferred — user scoped this cycle to R3a/R3b/R3d.

> **Acceptance evidence (scope: framework sources, excluding `.agent/archive/` rollback copies and `.agent/sessions/` runtime state):** old-wording greps (`independently flagging/flag the same location`, `escalation on independent overlap`, `escalate severity on cross-category overlap`) → empty; `escalate severity by one level` survives only inside the new R3b different-mechanism bullets; rule-3 normalized diff between `vdd-multi.md` and `SKILL.md §6` → empty. Known pre-existing drift flagged, not fixed: `SKILL.md` §8 references `tests/test_mock_agent.py` which no longer exists.

---

### **v3.20.2 — Politeness-Filter Rationale Retired; vdd-sarcastic Repositioned as Opt-in Skin (audit-067 P1 item 5, C-01/C-03/K2)**

Closes claims **C-01** ("Forced Negativity bypasses LLM politeness filters" — GPT-4-era theory: vendors now train sycophancy out per the GPT-5 and Opus 4.5/4.6 system cards; harsh judge prompts inflate false positives, arXiv:2603.00539 / 2604.16790; the vendor-documented recall lever is the *reporting-threshold instruction*, not tone) and **C-03** ("Meanness is the mechanism" — unsubstantiated as causal), and implements the **K2 repositioning**: `vdd-sarcastic` is now an explicitly **opt-in stylistic skin** over `vdd-adversarial` mechanics, with a disclaimer that tone has **no evidence base** as a recall lever (keep-vs-deprecate awaits the pre-registered A/B, roadmap item 13). Executed as a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-071.md`, Task 071). **Zero functional change** — no script, pattern, test, or exit-bar semantics touched; Objective Convergence bars stay byte-identical: pytest 30/30, skill gate 43/43.

The replacement rationale everywhere is the **exhaustive-reporting instruction**: *report every issue, including low-confidence ones; attach confidence + severity to each finding; filtering happens downstream — never in the reviewer's head.*

#### **Changed**

* **`vdd-adversarial` 1.1 → 1.2** — §2 principle "Forced Negativity" → **"Exhaustive Reporting** (supersedes 'Forced Negativity')" with the new instruction; §7 rationalization counter "VDD requires Forced Negativity. Politeness hides bugs." → "Harshness is not the requirement — exhaustive reporting is… Withholding a finding to be nice is the only real failure." `references/vdd-methodology.md` §V principle 2 reworded the same way, with an explicit retirement note (audit-067 C-01). Mechanics (objective bar, template, hallucination check) byte-untouched.
* **`vdd-sarcastic` 1.1 → 1.2** — §2 gains the **positioning disclaimer** (opt-in stylistic choice, no evidence base; mechanism = exhaustive reporting + objective bar §4, not meanness); §1 red flag and §3 process reworded (style optional / findings non-negotiable; "frame ALL feedback sarcastically" mandate dropped); §5 rows "Meanness is the mechanism" (C-03) and the politeness-filter row (C-01) replaced; frontmatter description now says "opt-in … stylistic skin over vdd-adversarial mechanics". `examples/usage_example.md` Roast table gains **Severity + Confidence** columns plus a deliberately low-confidence finding #6 to demonstrate the reporting contract.
* **`skill-adversarial-security` 1.2 → 1.3** — §2 persona **MANDATORY → optional style** (what is NOT optional: exhaustive reporting + the §7 objective bar); §1 red flag "Sarcasm breaks complacency. Use it." → "I'll only report the high-severity stuff" → WRONG (also pre-empts severity-threshold literalism per item 9's wording); §5 step 4 and §7 synced; description → "adversarial style (optional sarcastic skin)".
* **`skill-adversarial-performance` 1.0 → 1.1** — Tone section gains the style note (opt-in delivery style, not the mechanism); Process step "State the problem sarcastically" → "(sarcastic framing optional — style, never the success criterion)"; description → "(optional sarcastic skin)". Checklist/termination untouched (termination alignment = roadmap item 12).
* **`.claude/agents/critic-security.md`** (wrapper sync, Wave-1/2 anti-drift) — "(mandatory per SKILL §2)" → persona is optional style; mandatory = exhaustive reporting + objective bar (SKILL §7).
* **`System/Docs/SKILLS.md` registry** — 3 rows re-described (vdd-sarcastic as opt-in stylistic skin; both critics "(optional sarcastic skin)").

> **Acceptance evidence (scope: framework sources, excluding `.agent/archive/` rollback copies and `.agent/sessions/` runtime state):** `grep -ri "politeness filter" .agent/ System/` → empty (hardened bare-token grep over `.agent/ System/ .claude/` also empty); mandate-token grep (`mandatory per SKILL §2`, `Sarcasm breaks complacency`, `Meanness is the mechanism`, `frame ALL feedback sarcastically`, `State the problem sarcastically`) → empty; "Forced Negativity" survives only in the two `(supersedes …)` traceability notes. `docs/verification_roadmap.md` and `docs/reviews/audit-067` keep quoting the retired claim by design (backlog/immutable history).

**Sources (primary references for this change):**
- Anthropic, *Towards Understanding Sycophancy in Language Models* (Sharma et al., 2023) — [anthropic.com/research](https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models) · [arXiv:2310.13548](https://arxiv.org/abs/2310.13548). Sycophancy is a real RLHF artifact (the original motivation for "forced negativity").
- OpenAI, *GPT-5 System Card* — sycophancy −69% (free) / −75% (paid) vs GPT-4o; targeted evals 14.5% → <6% — [openai.com](https://openai.com/index/gpt-5-system-card/) · [PDF](https://cdn.openai.com/gpt-5-system-card.pdf). Vendors now train sycophancy out → the "bypass politeness" premise is outdated.
- *Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement* — [arXiv:2603.00539](https://arxiv.org/abs/2603.00539). Detailed/harsh prompts make models flag non-existent errors (false positives).
- *Bias in the Loop: Auditing LLM-as-a-Judge for Software Engineering* — [arXiv:2604.16790](https://arxiv.org/abs/2604.16790).
- *LLMs-as-Judges: A Comprehensive Survey* — [arXiv:2412.05579](https://arxiv.org/abs/2412.05579) (position / verbosity / self-preference biases).
- OpenAI, *LLM Critics Help Catch LLM Bugs* (CriticGPT; seeded-bug method later used by the item-13 A/B) — [arXiv:2407.00215](https://arxiv.org/abs/2407.00215) · [openai.com](https://openai.com/index/finding-gpt4s-mistakes-with-gpt-4/). The recall lever is exhaustive reporting, not tone.


---

### **v3.20.1 — OWASP Top 10 Checklist Re-mapped to the 2025 Final (audit-067 P1 item 4, C-09)**

Closes claim **C-09**: `references/checklists/owasp_top_10.md` was titled "2025" but laid out on the **2021 taxonomy** — every A-number exported to compliance systems (Jira/Snyk) was wrong. The ten 2025 category names were **verified directly against owasp.org/Top10/2025/ in-session** (the verification also caught audit-067's own paraphrase of A09 — official name is "Security Logging and **Alerting** Failures"). Executed as a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-070.md`, Task 070). **Zero behavior change**: pattern lists, finding fields, severities, and CLI untouched — pytest 30/30; repo audit findings and counts unchanged vs the pre-edit baseline (the only output diff is the intentional v3.4 → v3.5 summary-header line).

#### **Changed**

* **`owasp_top_10.md` re-sectioned to the 2025 final** — A01 Broken Access Control (absorbs 2021-A10 **SSRF** as a subsection); A02 Security Misconfiguration (was #5); **A03 Software Supply Chain Failures (new)** — re-homes all of 2021-A06 plus the CI/CD-tampering, code-signing, and dependency-audit items from 2021-A08; A04 Cryptographic Failures; A05 Injection; A06 Insecure Design; A07 Authentication Failures (renamed); A08 Software **or** Data Integrity Failures (renamed, keeps deserialization/signature checks); A09 Security Logging and Alerting Failures (renamed); **A10 Mishandling of Exceptional Conditions (new)** — fail-closed controls (CWE-636), unchecked returns (CWE-252/754), swallowed exceptions (CWE-390), resource cleanup on error paths (CWE-404/772), partial-failure rollback, plus the stack-trace-leak check (CWE-209) re-homed from old-A05. Checkbox conservation verified: 61 → 66 (−1 SSRF dedup, +5 new-A10, +1 new-A08). A **2021 → 2025 mapping table** is appended for previously exported compliance references.
* **`security-audit` skill 3.4 → 3.5** — §2 scanner-scope tags re-mapped (Secrets → A04:2025, Dependencies/Supply Chain → A03:2025, Injection patterns → A05:2025, Config → A02:2025); §3 Web/API Top Checks now four 2025-correct checks (A01 incl. SSRF, A03 supply chain, A05 injection, A10 exceptional conditions); version lockstep across frontmatter/header/`run_audit.py` docstring/`audit.__version__`.
* **`scanners.py` docstrings** — four scanner A-number tags re-mapped to 2025 (comment-only, zero functional diff).
* **`System/Docs/SKILLS.md` registry** — security-audit row → v3.5, "OWASP Top 10:2025 (final taxonomy)".

> **Note for downstream compliance exports:** A-numbers recorded before this release follow the 2021 layout. Use the mapping table at the end of `owasp_top_10.md` to migrate (e.g., old "Injection (A03)" → A05; old "SSRF (A10)" → A01).

---

### **v3.20.0 — Agentic/MCP Security Upgrade (audit-067 P1 item 3 — highest real-world risk)**

Closes claims **C-11** (agentic/MCP threats covered by one-liners, zero detection patterns) and **C-14** (Security Auditor role has no agentic threat model) from the verification-stack currency audit (Task 067). The external bar moved while the checklists stood still: **OWASP Top 10 for Agentic Applications 2026** (ASI01–ASI10, 2025-12-09), **NSA AISC CSI "MCP: Security Design Considerations"** (U/OO/6030316-26, May 2026), CVE-2025-6514 (9.6) / CVE-2025-49596 (9.4) / the MCP-STDIO 11-CVE cluster, and in-the-wild incidents (postmark-mcp rug pull, s1ngularity, Shai-Hulud) — in the framework's own home domain. Executed as a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-069.md`, Task 069); ASI names, NSA controls, and scanner CLIs **verified against primary sources** (genai.owasp.org, nsa.gov, github.com/snyk/agent-scan) instead of model memory.

#### **Added**

* **`references/checklists/mcp_agentic_security.md`** — sections mapped **1:1 to ASI01–ASI10**, NSA CSI operational controls (least-privilege tokens, context labeling, cryptographic isolation, audit logging, outgoing filtering proxy/DLP, signed provenance, registry hardening, local MCP scans), the seven named attack patterns (tool poisoning, rug pull, tool shadowing, full-schema poisoning, confused deputy, token passthrough, session hijacking), an incident-calibration block, and an honest "scanner floor vs LLM review" boundary.
* **Scanner: new `--scan-type mcp`** (`scan_mcp_agentic`, included in `all`) — **10 regex patterns**, each tagged with a real CWE **and** an ASI ID, with a per-pattern `scope` field (known MCP configs / any config / code): auto-approve keys, permission-bypass flags, unpinned `npx -y`/`uvx` (incl. `@latest`), unpinned JSON `args`, `mcp-remote` (CVE-2025-6514 class), cleartext MCP URLs, inline `env` secrets, shell-spawning servers, imperative-description heuristic, `<IMPORTANT>` poisoning marker. Provenance finding (low) for every `mcp.json`/`.mcp.json`/`claude_desktop_config.json`; **descends into `.vscode/`** (custom prune — the canonical mcp.json home that `SKIP_DIRS` hid); whole-file matching with the IaC-style ReDoS guard; **severity ceiling HIGH** by design (regex can't prove config exploitability → MCP findings alone can never trip `--fail-on critical`). Markdown is deliberately not scanned — semantic prose poisoning is the LLM-review class. `detect_project_types()` gains `"mcp"`. **12 new regression tests** (29 total), including the `.vscode` prune hole, multi-line env blocks, and pinned-vs-unpinned negatives.
* **External tool roster**: `snyk-agent-scan` (formerly Invariant `mcp-scan`; legacy CLI as fallback) auto-attempted when MCP config artifacts are detected — **never** with server-auto-start flags; starting untrusted MCP servers stays a consent-gated operator action.
* **`10_security_auditor.md` v3.6.0 → v3.7.0** — new **Step 1.5: Agentic Threat Model** (goal hijack ASI01, tool tampering ASI02, identity/privilege + confused deputy ASI03, supply chain/rug pull ASI04, memory poisoning ASI06, inter-agent trust ASI07) + TIER 1 pointer to the new checklist for agentic/MCP targets. TIER 0 block byte-identical.

#### **Changed**

* **`security-audit` skill 3.3 → 3.4** — §2 scope + usage gain the MCP line and scan type; §3 gains the "Agentic / MCP" mandatory-checklist subsection with the regex-floor limitation note; frontmatter `description` now triggers on MCP/agentic; version lockstep across frontmatter/header/`run_audit.py` docstring/`audit.__version__`.
* **`System/Docs/SKILLS.md` registry** — security-audit line refreshed (was stale at "v3.2 / 121 patterns"; now v3.4 / **148 patterns** incl. MCP/ASI capability).

#### **Fixed (surfaced by dogfooding)**

* **`scan_secrets` phantom ReDoS warning** — `skipped_lines` used `content.count("\n") + 1 - len(safe_lines)`, which over-counts by 1 on newline-terminated files (`splitlines()` yields no trailing empty element), so **every** normal file printed a misleading `[WARN] skipped 1 line(s) > 4000 chars (ReDoS guard)`. No content was actually skipped, but a false "skipped" signal undermines the skill's own "check `skipped_files` = false negatives" guidance. Now counts only genuinely over-long lines (`len(all_lines) - len(safe_lines)`). +1 regression test (no phantom warning on short lines; real warning still fires on a >limit line). Found by running the scanner against a 17-file multi-domain dogfood corpus.

#### **Verification**

* pytest **30/30**; `run_audit.py` on this repo: finding counts byte-identical to pre-change baseline (22: 10 critical / 12 medium — pre-existing regex-floor FPs in framework scripts) + **0 MCP findings**; skill gate **43/43**; drift greps clean; dogfood corpus (Python/JS/Go/Rust/Solidity/GraphQL/Docker/K8s/Terraform/config/secrets/MCP) → 100 findings across all scanners, every planted bug class detected; remaining audit-067 backlog (items 4–13) unchanged.

**Sources (primary references for this change):**
- OWASP, *Top 10 for Agentic Applications (2026)* — [genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) (ASI01 Goal Hijack, ASI06 Memory/Context Poisoning).
- OWASP, *LLM01: Prompt Injection (2025)* — [genai.owasp.org](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) (direct vs indirect prompt injection).
- NSA AISC, *CSI: MCP — Security Design Considerations for AI-Driven Automation* (U/OO/6030316-26, May 2026) — [press release](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/) · [PDF](https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf).
- *Model Context Protocol — Security Best Practices* — [modelcontextprotocol.io](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) (tool poisoning, shadowing, rug pull).

### **v3.19.2 — Adversarial-Security Critic: Objective Termination + No-Fabrication Recon (audit-067 P0)**

The verification-stack currency audit (`docs/reviews/verification-stack-currency-audit-067.md`, Task 067) graded two claims in `skill-adversarial-security` **HARMFUL** — the residuals the v3.18/v3.19 Objective-Convergence hardening missed. Both fixed in a `/framework-upgrade` cycle gated by `skill-self-improvement-verificator` Modes A+B (`docs/reviews/framework-audit-068.md`); nothing else in the verification stack touched.

#### **Changed**

* **`skill-adversarial-security` v1.1 → v1.2 — §7 Termination [C-05]**: deleted the termination condition "You have made at least one snarky comment about a questionable design choice" (tone-as-success-criterion forced noise on clean code — the pattern v3.18.0 removed from Sarcasmotron). Termination now binds to the objective bar **only**: automation executed (or honestly reported `scan: NOT RUN`) + no Critical/High findings + bikeshedding-only remains — matching `vdd-sarcastic` §4 (Objective Convergence) and the critic `Convergence signal` contract.
* **§3 Reconnaissance [C-15]**: deleted "Mock the results if you cannot run it directly, but assume standard tool outputs (slither/bandit)" — an instruction for a *security critic* to fabricate scanner evidence (and, since `critic-security` has no Bash tool, the **default path** in every `/vdd-multi` run, not the exception). Replaced with the no-fabrication protocol: report `scan: NOT RUN` and proceed with manual review only — never fabricate scanner output; the orchestrator runs `run_audit.py` and passes its results into the critic prompt. §5 Process step 1 aligned with the same rule.

#### **Unchanged (invariants)**

* Sarcastic persona (§2), checklists (§4), rationalization table (§6) byte-identical — tone remains the delivery style, it just stopped being a success criterion. Satellites (`critic-security.md`, `vdd-multi.md`, `skill-adversarial-performance`) verified clean — neither harmful claim existed outside the one skill file. Skill gate 43/43. Remaining audit-067 backlog (5×P1, 5×P2, 1×P2-experiment) deferred to follow-up cycles.

### **v3.19.1 — Symlink-Aware Prompt Discovery (Codex / `AGENTS.md` hardening)**

In the default `--mode symlink` install, framework prompts/skills land as symlinks into `.agentic-development/`. Agents whose default file-discovery does not descend into symlinked directories saw those paths as empty on the first probe. Verified live on dummy projects: **Antigravity follows symlinks natively** (no change needed), but **Codex** recognized the content only on a *second* attempt — its first read-only probe was a plain `find` (which silently skips symlinked dirs); the next step used `find -L` and everything resolved. Fixed at the instruction + safe-command-policy layer; the installer (`vendors.yaml`, Python) is untouched.

#### **Added**

* **`AGENTS.md` → `SYMLINK RESOLUTION (MANDATORY)`** — states that framework paths (`.agent/`, `.agents/`, `System/`, `.agentic-development/`, …) may be symlinks, mandates following them when reading prompts/skills/tools, and declares that targets resolving inside `.agentic-development/` are *expected and trusted*, not a path-traversal escape. Propagates to every Codex/Cursor install via the `marker_block` bootstrap (whole `AGENTS.md` = managed block).
* **`AGENTS.md` → `SYMLINK-AWARE COMMAND DEFAULTS`** — mandates `find -L` / `ls -L` / `rg --follow` (`rg -L`) / `fd -L` when inspecting framework dirs (plain `find`/`ls`/`rg` skip symlinked directories), notes direct reads (`cat`/`sed`/`head`/`tail`) follow symlinks automatically, and adds a **retry-once** rule: an empty probe under a known framework dir must be retried with symlink-following before the path is treated as empty/missing.

#### **Changed**

* **`skill-safe-commands` v1.1 → v1.2** — new **Symlink-aware** command category (`find -L`, `ls -L`, `rg --follow` / `rg -L`, `fd -L`); `rg`/`fd` added to the Read-only set; matching regex patterns added; an `[!IMPORTANT]` retry-rule block added to runtime behavior; the Antigravity "Allow List Terminal Commands" line extended with the symlink-aware variants.

#### **Unchanged (invariants)**

* Installer logic (`System/scripts/installer/*`, `vendors.yaml`) byte-identical — no copy/symlink mode change. `GEMINI.md` and `CLAUDE.md` not modified: Antigravity (verified) and Claude follow symlinks by default. Skill gate: `skill-safe-commands` validates PASSED (pre-existing warnings only).

### **v3.19.0 — Multi-Critic Objective Convergence (parallel adversarial pipeline)**

Follow-up to v3.18.0: the parallel critics (`critic-logic` / `critic-security` / `critic-performance`) still self-certified convergence via a subjective `hallucinating` state — the same gameable pattern v3.18.0 removed from Sarcasmotron, and worse, `/vdd-multi`'s Phase-3 termination marked a category *done* on it. Replaced with an objective state, so both the termination gate and the merge noise-filter are objective.

#### **Changed**

* **Critic `Convergence signal` enum** `clean-pass | issues-found | hallucinating` → `clean-pass | issues-found | **bikeshedding-only**` across the three critic agents, with `bikeshedding-only` defined objectively ("no legitimate findings remain — only style/nits; NOT 'forced to invent problems'").
* **`/vdd-multi` Phase-3 termination** now marks a category ✓ on the objective `bikeshedding-only` / `clean-pass` state instead of "critic inventing problems".
* **Merge noise-filter** (`vdd-multi.md` + `skill-parallel-orchestration`) re-keyed off `bikeshedding-only`; the "drop a converged critic's low-severity items this iteration" mechanic is unchanged. Satellite references (`skill-parallel-orchestration` §2.3, `examples/usage_example.md`, `references/sequential-fallback.md`) refreshed to the objective terminology.

#### **Unchanged (invariants)**

* All other merge rules — location dedup (±3 lines), cross-category re-attribution, severity escalation on independent overlap, `--severity` filter, iteration cap — and the Layer A / Layer B decision rule are byte-identical. Skill gate 43/43; VDD adversarial review APPROVED with zero findings.

### **v3.18.0 — Reviewers Hardening (provable clean review + objective Sarcasmotron exit, cross-vendor)**

Three reviewer weaknesses, plus a cross-vendor backup gap, hardened without merging or re-toning the two review roles. The Code Reviewer's clean pass is now *provable*; its output contract is converged across four drifting definitions; the Sarcasmotron exit is moved off a subjective trigger onto an objective bar across every authoritative definition; and `/framework-upgrade` now backs up all vendor bootstrap files. `has_critical_issues` and the orchestrator DECISION TABLE are byte-for-byte unchanged — control-flow is identical before and after.

#### **Added**

* **Code Reviewer "Verified" block** — when `has_critical_issues = false`, the report must carry a plain-markdown block proving the *scope* of the clean pass (requirements cross-checked + edge cases considered), so "looked and clean" is distinguishable from "didn't look". Body text only — never a structured key — so it cannot affect control-flow (`09_code_reviewer_prompt.md`).
* **Objective Convergence** — the Sarcasmotron exit is now bound to an objective bar (full test run executed · 0 CRITICAL · 0 legitimate logic/security/slop findings · only bikeshedding left), replacing the subjective "forced to invent nitpicks → approve" trigger that let a lazy/sycophantic model exit early.

#### **Changed**

* **Reviewer output contract converged to one superset** `{ review_status, has_critical_issues, e2e_tests_pass, stubs_replaced }` across all four definitions — SOT `09_…`, `skill-orchestrator-patterns` Extended Schema, the `.claude/agents/code-reviewer.md` wrapper, and `01_orchestrator.md` Step 11. `comments` is reconciled everywhere as the prose report body, not a JSON key. Additive only; `has_critical_issues` semantics untouched.
* **Objective-Convergence criterion applied identically** across all authoritative Sarcasmotron definitions — `vdd-03-develop.md`, `vdd-adversarial/SKILL.md`, `vdd-sarcastic/SKILL.md`, `vdd-adversarial/references/vdd-methodology.md`, plus the `/vdd-adversarial` workflow — with hostile tone and "assume broken until proven" stance preserved. Stale "Hallucination Convergence/Exit" terminology refreshed in `vdd-05-run-full-task.md`, `System/Docs/WORKFLOWS.md`, `VDD.md`, and `TDD_VS_VDD.md`. VDD-loop mechanics (3-REJECT / escalation / HITL) unchanged.
* **`/framework-upgrade` backup/rollback is now vendor-aware** — Step 3.1 and Step 5 iterate over every present bootstrap file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) and skip absent ones, instead of hard-coding `GEMINI.md` alone.

#### **Fixed**

* **Reviewer-contract drift** — `09_…` previously emitted only `{review_status, has_critical_issues}` while three consumers expected `e2e_tests_pass`/`stubs_replaced`; now consistent.
* **Subjective exit fabrication** — approval could be triggered by the auditor inventing nitpicks (an unobservable, gameable signal); approval is now bound to the objective bar in every definition. The Phase-4 adversarial review (eating its own dogfood against the new bar) caught two further normative residuals (`VDD.md`, `TDD_VS_VDD.md`, `/vdd-adversarial`) which were folded in. The `/vdd-multi` `convergence: hallucinating` dedup noise-filter is a distinct mechanism, intentionally left untouched.

### v3.17.0 — Skill-Validator Inline-Block Rule Reform (two-tier warn/fail)

The skill quality gate hard-failed CI on any fenced code block over 12 lines — an arbitrary, line-based threshold with no warning tier and no awareness of block type, stricter than `ARCHITECTURE.md` §8 itself (which cites "50 lines" as the bad case). v3.16.0's `skill-archive-task` tripped it. The principle (progressive disclosure — keep `SKILL.md` lean) is kept; the crude implementation is replaced with a two-tier, fence-type-aware, config-driven check. Validator-only change — no runtime-pipeline tools touched.

#### **Added**

* **Two-tier inline-block policy** — a fenced block over **20 lines** emits a non-blocking warning; over **60 lines** a hard error. Thresholds are config-driven (`validation.quality_checks.max_inline_lines_warn` / `_fail`).
* **Fence-type awareness** — `mermaid` fences are exempt (diagrams); `text`/`console`/`output` fences can only warn, never fail (output samples). Configurable via `inline_exempt_fence_langs` / `inline_softcheck_fence_langs`.
* **Unclosed-fence detection** — an unclosed ` ``` ` is now reported explicitly instead of being silently swallowed by the parser.
* **`tests/test_inline_efficiency.py`** — 9 regression tests (warn / fail / exempt / softcheck / unclosed branches + a drift guard asserting the `validate_skill.py` and `analyze_gaps.py` copies stay behaviourally identical), wired into the `Framework Gates` CI.

#### **Changed**

* **`check_inline_efficiency`** now returns `(errors, warnings)` — warnings route to the non-blocking channel instead of failing CI.
* **`skill-creator`** v2.0 → v2.1, **`skill-enhancer`** v1.2 → v1.3 — both validator copies reformed in lockstep; **`skill-archive-task`** v1.2 → v1.3.
* Config updated across `.agent/rules/skill_standards.yaml` and all bundled `skill_standards_default.yaml`; `skill-creator` docs, `System/Docs/skill-writing.md`, and `ARCHITECTURE.md` §8 updated.

#### **Fixed**

* **`skill-archive-task` CI failure** — the v3.16.0 Step-7 protocol block (35 lines) and Example Flow (17 lines) hard-failed the old 12-line rule; both were restructured into smaller labelled blocks, and the rule itself reformed so coherent procedural content is no longer penalised.

### **v3.16.0 — Deterministic Artifact Archiving (PLAN.md lockstep + ARCHITECTURE.md Index-Mode)**

Closes a long-standing drift: `docs/TASK.md` archived reliably, while `docs/PLAN.md` and `docs/ARCHITECTURE.md` did not — some projects archived plans to `docs/plans/`, some dumped them flat into `docs/archives/`, some never archived; `ARCHITECTURE.md` grew unbounded (one project reached 2037 lines). Archiving of PLAN.md and ARCHITECTURE.md is now an explicit, deterministic protocol wired into the same skills, prompts, and workflows that already make TASK.md archiving work. Protocol change — no new scripts and no runtime-pipeline tools touched; the existing `archive_protocol.py` test mirror gains matching `archive_plan()` coverage.

#### **Added**

* **PLAN.md lockstep archiving** — `skill-archive-task` now archives `docs/PLAN.md` → `docs/plans/plan-NNN-slug.md` in lockstep with TASK.md, reusing the same ID and slug (`task-NNN-slug.md` ↔ `plan-NNN-slug.md`). New protocol Step 7 with explicit edge cases (PLAN.md absent, orphan PLAN.md, re-plan, corrected ID).
* **ARCHITECTURE.md Index-Mode** — `architecture-format-core` gains a "Living Document & Index-Mode" section: `docs/ARCHITECTURE.md` is a single living document, updated in place and never per-task archived; when it exceeds **1500 lines** it is split into `docs/architectures/<section-slug>.md` chunks with a short (~≤200-line) index.

#### **Changed**

* **`skill-archive-task`** v1.1 → v1.2 (now covers TASK.md + PLAN.md).
* **`artifact-management`** v1.0 → v1.1, **`architecture-format-core`** v1.0 → v1.1, **`architecture-review-checklist`** v1.0 → v1.1, **`skill-safe-commands`** v1.0 → v1.1.
* **Agent prompts** — Analyst, Architect, Planner, Architecture Reviewer wired for lockstep archiving + the Index-Mode size check / reviewer backstop.
* **Workflows** — `01-start-feature`, `vdd-01-start-feature`, `light-01-start-feature`, `light-02-develop-task`, `04-update-docs`, `02-plan-implementation`, `vdd-02-plan` annotated with the new rules.
* **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Directory Structure updated with `docs/plans/` and `docs/architectures/`; new "Artifact rotation" note.
* **`.agent/tools/archive_protocol.py`** (the skill-archive-task test mirror) — new `archive_plan()` function implementing Step 7 + 8 lockstep tests (23 archive tests total, all green).

#### **Fixed**

* **PLAN.md archiving drift** — plans are no longer dumped flat into `docs/archives/` or left unarchived. This repo's own legacy `docs/archives/PLAN-*.md` migrated to `docs/plans/plan-NNN-slug.md`.
* **ARCHITECTURE.md unbounded growth** — the 1500-line Index-Mode threshold plus an Architecture Reviewer 🟡 MAJOR backstop prevent monolithic architecture files.

### **v3.15.0 — Framework Installer: `install.sh` (5 vendors, 5 subcommands)**

A bootstrap-time CLI that deploys the framework into a clean target project under a chosen agent-system profile — replacing manual folder copying. The framework lives in the target's `.agentic-development/` (a symlink to a sibling clone, or a full copy); per-item relative symlinks point into it; a SHA-256-hash-protected managed `.gitignore` block keeps framework files out of the project's git history. Built end-to-end through the framework's own VDD pipeline (Analyst → Architect → Planner → an 11-task `/vdd-develop-all` chain → 3-critic `/vdd-multi` adversarial review). The adversarial passes caught and fixed real bugs before merge — a `--dry-run` that mutated the filesystem, a snapshot crash on overlapping paths, a CWD-dependent `copytree` symlink-resolution bug, and an `uninstall` that could delete user-owned content. The installer is a standalone bootstrap tool — **no runtime-pipeline changes**.

#### **Added**

* **`install.sh`** — minimal bash wrapper (`BASH_VERSION` guard, `python3`/PyYAML dependency check, `exec python3`).
* **`System/scripts/install.py`** + **`System/scripts/installer/`** — 16-module Python package (stdlib + PyYAML only, per NFR-5).
* **`System/scripts/vendors.yaml`** — declarative vendor profiles; a new agent system is added without touching Python.
* **Five subcommands** — `install` / `switch` / `update` / `uninstall` / `doctor`.
* **Five vendor profiles** — `claude`, `antigravity`, `codex`, `cursor`, `gemini-cli`.
* **Two deployment modes** — `--mode symlink` (default, `.agentic-development/` → sibling clone) and `--mode copy` (self-contained, for airgapped / CI).
* **Pre-flight conflict prevention** — every target path is classified (`safe` / `our` / `hard_conflict` / `soft_conflict`) before any write; `CLAUDE.md` / `AGENTS.md` / `GEMINI.md`, user `settings.json`, and a user-owned `System/` are never overwritten. `--dry-run` previews the plan with **zero** filesystem mutation.
* **Anti-clobber engine** — managed blocks in `.gitignore` and bootstrap files are SHA-256-hashed; a hand-edited block aborts the run with a unified diff unless `--force` (which backs the old version up first).
* **`doctor`** — read-only integrity verifier with a `--json` report schema (broken symlinks, hash mismatches, state-schema check).
* **`tests/installer/`** — 169 `unittest` tests (per-module unit + 10-scenario end-to-end + bash-wrapper smoke), wired into `tests/run_tests.py`.

#### **Changed**

* **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — new **§9 Framework Installer Subsystem** (data model, components, invariants, security & safety).
* **[README.md](README.md) §Installation** — `install.sh` documented as the recommended deployment method; manual folder-copy retained as the alternative.

#### **Fixed**

* Adversarial-review fixes folded in before merge: `--dry-run` filesystem mutation; snapshot overlapping-path crash; `copytree` CWD-dependent dangling-symlink resolution; `uninstall`/`switch` over-broad deletion of user content; `inject_block` marker-line injection; `doctor` state-schema gap; `apply_retention` able to delete every backup; a stale `System` symlink surviving `uninstall`.

### **v3.14.3 — `/vdd-develop-all`: VDD chain workflow with Sarcasmotron review**

New workflow composing the chain-iteration of `/develop-all` with the per-task adversarial Sarcasmotron loop of `/vdd-develop`. Walks the full `docs/PLAN.md`, applies hostile review to each task, gates progression on explicit user input between tasks, and **never auto-commits**. Built end-to-end through the framework's own VDD pipeline (Analyst → Architect → Planner → Developer → Sarcasmotron); the build itself surfaced 1 honest REJECTED iteration that fixed a real control-flow bug before merge. No architectural changes — pure composition of existing Layer A / Stage Cycle patterns.

#### **Added**

* **`.agent/workflows/vdd-05-run-full-task.md`** (53 lines) — new chain workflow with 5 numbered steps:
  1. **Plan parsing** with `--dry-run` flag (preview chain without executing).
  2. **Per-task VDD cycle** A→D: Builder → Verification → Sarcasmotron-roast → Refinement loop. Sarcasmotron persona is **delegated** to `vdd-03-develop.md` Step 3 (DRY — not inlined).
  3. **HITL gate** between tasks (`yes / pause / abort`) with optional `--auto-continue=<seconds>` flag for unattended runs.
  4. **Session-state persistence** on both APPROVED-merge and 3-REJECTED-STOP paths, with explicit ordering `merge → persist → HITL` (load-bearing — persist BEFORE the HITL prompt to survive runner crashes during user wait).
  5. **Finalization** with full regression suite (`python3 tests/run_tests.py` + `validate_skill.py`) and metrics report (merged tasks, REJECTED iterations, Hallucination-Convergence vs honest APPROVED counts). **Auto-commit forbidden**; commit/PR decision belongs to the user.
* **`.claude/commands/vdd-develop-all.md`** — slash-command registration, byte-identical structure to `develop-all.md` / `vdd-develop.md` modulo the workflow path.
* **Resumability** section + behavioral smoke test: re-invoke `/vdd-develop-all` after `pause` reads `.agent/sessions/latest.yaml` and resumes from the first non-merged task in `docs/PLAN.md`.
* **Refinement loop limit**: 3 REJECTED iterations per task before STOP + escalation (chosen over `/03-develop-single-task`'s 2 because Sarcasmotron is stricter — 2 escalates noisily, 4+ wastes tokens on stuck tasks).

#### **Changed**

* **[CLAUDE.md](CLAUDE.md) `## WORKSPACE WORKFLOWS`**: `+1 −1` — `/vdd-develop-all` inserted into Available Commands list next to `/vdd-develop`.
* **[GEMINI.md](GEMINI.md)**: `+1 −1` — `vdd-05-run-full-task` added to Available Workflows enumeration.
* **[AGENTS.md](AGENTS.md)** §Development Phase: `+1` — chain-execution pointer comparing `/develop-all` (auto-commit) vs `/vdd-develop-all` (adversarial, HITL, no auto-commit).
* **[System/Docs/WORKFLOWS.md](System/Docs/WORKFLOWS.md)**: `+22 −5` across 4 surgical edits:
  - **Mermaid diagram**: `VDDRunAll{{vdd-05-run-full-task}}` node added to Automation Loops, with edge labels distinguishing auto-commit (`RunAll`) from Sarcasmotron+HITL (`VDDRunAll`).
  - **Automation Loops table**: new row for `vdd-05-run-full-task`; clarified existing `05-run-full-task` row to mention auto-commit; clarified `vdd-03-develop` as "single task".
  - **FAQ**: new entry "When should I use `vdd-05-run-full-task` instead of `05-run-full-task`?" listing the 3 load-bearing differences (adversarial review, mandatory HITL, no auto-commit).
  - **VDD Multi-Step example**: Step 3 expanded into 3a (single-task) and 3b (chain) variants.
* **[.agent/workflows/vdd-03-develop.md](.agent/workflows/vdd-03-develop.md)**: `+2` — trailing cross-link note pointing at `/vdd-develop-all` for chain execution.

#### **Fixed (caught during the build itself)**

* **Hallucinated test path** (caught in Verification, before Sarcasmotron): user's original brief and intermediate spec drafts referenced `bash tests/test_e2e.sh` — a file that does not exist in this repo. The actual test harness is `python3 tests/run_tests.py`. Workflow file now uses the real path. Spec drift remains in `docs/TASK.md` and `docs/tasks/task-061-02-workflow-impl.md`; left as-is per "specs are write-once snapshots" — the implementation is canonical.
* **Step 3 ↔ Step 4 control-flow ambiguity** (caught by Sarcasmotron, iteration 1 of 061-02): Step 2D originally said "APPROVED → merge → Step 3 (HITL)", but Step 4 (session-state persist) sat below Step 3 numerically and claimed "after every merge", leaving the persist-vs-HITL execution order undefined. Could lose merge state if a runner crashes during user wait. **Fix**: Step 2D now explicitly states `merge → Step 4 (persist) → Step 3 (HITL gate) → next task`, with "Order is load-bearing" callout.
* **Missing failure-path session-state persist** (caught by Sarcasmotron, iteration 1 of 061-02): the 3-REJECTED-STOP path did not persist failure state, so resumption after escalation would silently retry from scratch. **Fix**: Step 2D now invokes Step 4 with `--status "failed_sarcasmotron" --add_blocker "Task <name>: 3 REJECTED iterations"` on the STOP path; Step 4 header annotates "called from Step 2D — both APPROVED and 3-REJECTED-STOP paths".

#### **Verification**

* All 7 RTM checks for Task 061-01 (stubs) GREEN on iteration 1.
* All 7 RTM checks for Task 061-02 (logic) GREEN after iteration 2 (1 Verification fix + 2 Sarcasmotron fixes).
* All 4 RTM checks for Task 061-03 (cross-links) GREEN on iteration 1 (`+1 −1` to CLAUDE.md, `+2 −0` to `vdd-03-develop.md`, no other workflow regressions).
* Final regression suite: `python3 tests/run_tests.py` → 5/5 passed.
* Workflow file 53 lines (≤150 line budget).

#### **Process metrics (chain build)**

| Metric | Value |
|---|---|
| Tasks merged | 3/3 |
| Total REJECTED iterations across chain | 1 |
| Hallucination-Convergence APPROVED | 3 |
| Honest APPROVED (no nitpick-inversion) | 0 |
| Verification-phase finds (caught **before** Sarcasmotron) | 1 |

The single honest REJECTED iteration was a genuine save: Sarcasmotron caught a control-flow bug that would have made session-state semantics ambiguous to a future LLM consumer. The Verification phase separately caught a hallucinated test path inherited from the brief — exactly the filter Step B is designed to provide.

#### **Impact**

* New chain primitive for high-rigor multi-task batches: per-task adversarial scrutiny + mandatory HITL + zero accidental commits. Pairs with the existing `/develop-all` (fast path with auto-commit) — pick by required rigor, not by default.
* Resumability via `latest.yaml` makes pause/resume a first-class operation: long batches can run across context-window resets without losing merge state.
* Demonstrates the framework can build its own next-tier workflow under its own VDD pipeline, including catching real bugs via the adversarial loop. The Sarcasmotron persona's "Hallucination Convergence" exit rule worked as intended: round 1 produced 2 honest findings, round 2 reduced to bikeshedding.

---

### **v3.14.2 — `security-audit` skill v3.2 → v3.3 (bug fixes + coverage + hardening)**

Post-analysis critique of the `security-audit` skill surfaced 2 real bugs, 4 coverage gaps, and 6 refinement opportunities. All 14 items addressed. Scanner integrity is visibly improved; no breaking changes to CLI surface (new `--max-size` is additive).

#### **Fixed (HIGH — correctness bugs)**

* **Pip lock-file detection**: [scanners.py](.agent/skills/security-audit/scripts/audit/scanners.py) previously treated `requirements.txt` as a lock file (it is not — it does not pin a transitive graph with hashes) AND had no `is_type` branch for Python at all, so `Missing Lock File` never fired for pip projects. Rewrote `scan_dependencies` to use ecosystem groups with explicit `markers` (presence of `pyproject.toml`/`setup.py`/`setup.cfg`/`requirements.txt`/`Pipfile`) and `locks` (real lock files only: `Pipfile.lock`, `poetry.lock`, `uv.lock`, `pdm.lock`). Also fixed JS over-flagging (previously `yarn`+`pnpm` both fired when `package-lock.json` was present — now any of the three locks satisfies the JS ecosystem).
* **Report-path rassinchron**: [`.agent/workflows/security-audit.md`](.agent/workflows/security-audit.md) wrote `docs/SECURITY_AUDIT.md`; the [`security-auditor`](.claude/agents/security-auditor.md) agent (and [`System/Agents/10_security_auditor.md`](System/Agents/10_security_auditor.md)) writes `docs/audit/security-{ID}.md`. Aligned workflow → agent convention (supports multiple audits + integrates with `skill-archive-task` ID convention).

#### **Fixed (MED — coverage + refinement)**

* **SBOM scan was non-recursive** ([scanners.py](.agent/skills/security-audit/scripts/audit/scanners.py) `scan_sbom`): `glob("*sbom*")` only looked in the project root. SBOMs are commonly placed in `build/`, `dist/`, `artifacts/`, `docs/`. Switched to `rglob` with `SKIP_DIRS` filter and duplicate dedup. Nested `docs/sbom.json` now detected.
* **Dead SBOM-probe block removed**: previous code ran `syft --version` / `cdxgen --version` and printed "tool is available for SBOM generation" without actually generating anything. Either misleading or unfinished — removed entirely; generation instructions remain in the `Missing SBOM` finding message.
* **`MAX_FILE_SIZE` 5 MB → 15 MB + CLI `--max-size MB`**: 5 MB was silently skipping most modern minified production bundles (`vendor.js`/`bundle.js` routinely exceed 10 MB after Webpack `DefinePlugin`). Bumped default to 15 MB; added `--max-size` flag with runtime override (scanners now read `config.MAX_FILE_SIZE` via module-reference, not import-time copy).
* **Solidity `public/external` false positives on view/pure**: pattern flagged every non-modifier `public` function, noisily firing on view/pure getters. Tightened regex with negative lookahead `(?!.*\b(?:view|pure|constant)\b)` — getters no longer flagged; state-mutators still flagged.

#### **Added (coverage expansion)**

* **+16 regex patterns across 3 language stacks** (`patterns.py`):
  * **Rust** (6): `unsafe {}` blocks, `unsafe fn`, `std::mem::transmute`, `std::mem::forget`, `.unwrap_unchecked`, `from_raw_parts`, `rand::random` (weak RNG for security).
  * **Go** (6): `"math/rand"` import + call-site, SQL concat/`Sprintf` in `db.Query`/`Exec`, `http.ListenAndServe` (missing TLS), `filepath.Join` with request data, `exec.Command` with formatted/concat string.
  * **GraphQL** (4): `introspection: true`, `GRAPHQL_PLAYGROUND=true`, `graphiql: true`, `ApolloServer({...})` config (verify depth/complexity limits for DoS).
* **External tools — cross-cutting additions** ([external.py](.agent/skills/security-audit/scripts/audit/external.py)):
  * `semgrep --config auto` (de-facto SAST standard since 2024) now runs for any project type.
  * `gitleaks detect` (primary) with `trufflehog filesystem` fallback — stronger secret detection than regex-only.
  * Missing tools remain non-fatal (per `run_command` contract).
* **ReDoS guard**: added `MAX_LINE_LENGTH = 4000` to [config.py](.agent/skills/security-audit/scripts/audit/config.py); `scan_code_patterns` now skips pathologically long lines (minified JS routinely has >100k-char single lines, triggering catastrophic backtracking on complex regex). Real source code lines almost never exceed 4k chars.
* **`fuzzing_invariants.md` expanded 42 → 170+ lines**: 8 invariant categories (accounting, access control, monotonicity, pausability, ERC-20, ERC-4626, oracle, reentrancy); Foundry / Echidna / Medusa / Halmos setup; mandatory handler-based fuzzing pattern with ghost state; depth requirement table by criticality; 10-item edge-case checklist; post-fuzz regression discipline.

#### **Documentation**

* [SKILL.md §2](.agent/skills/security-audit/SKILL.md) now documents `--max-size` flag, Rust/Go/GraphQL coverage, semgrep/gitleaks cross-cutting tools, ReDoS guard, and clarifies that `--scan-type external` runs ONLY external tools (SKIPS regex scans) — previously ambiguous.
* Version bumped to v3.3 in SKILL.md frontmatter, header, and `run_audit.py` module docstring + CLI description.

#### **Verification (smoke-tested)**

* Self-exclusion holds on own skill dir (0 findings).
* `pyproject.toml` alone → `Missing Lock File` (pip) — previously silent.
* `requirements.txt` alone → `Missing Lock File` (pip) — previously silent.
* Nested `docs/sbom.json` detected via rglob — previously reported missing.
* Rust test file (`unsafe {}`, `std::mem::transmute`, `rand::random::<u32>()`) → all 3 patterns fire.
* Solidity test: `view` getter skipped, `public` state-mutator flagged.
* Config/deps/IaC/SBOM scans on repo root all pass without regression.

#### **Impact**

* Python projects without real lock files (Pipfile.lock/poetry.lock/uv.lock/pdm.lock) now receive supply-chain warnings — previously false-negative. Hash-pinned `requirements.txt` (pip-compile output with `--hash=sha256:` lines) is accepted as a lock (avoids false-positive on pip-tools mainstream pattern, added in Round 4).
* Rust, Go, and GraphQL codebases receive **initial** in-process regex coverage. For depth, `gosec`/`govulncheck`/`semgrep`/`cargo-audit`/`clippy` remain primary (invoked via `--scan-type external`); the in-process patterns are fast signalling, not a replacement.
* Minified bundles up to 15 MB are now scanned for accidentally-committed secrets (previously 5 MB cutoff).
* Adversarial convergence signal: `issues-found` at R3 (3 actionable bugs fixed in P1–P2) and again at R4 (10 defects — 4 broken patterns + pip-compile false-positive regression + SBOM perf regression + test gap — all fixed before release tag).

---

### **v3.14.1 — VDD adversarial-review fixes on v3.14.0**

Post-release adversarial critique of v3.14.0 surfaced 7 findings (2 HIGH, 4 MED, 2 LOW). All addressed in this patch. No behavior change for Claude Code users; all fixes are rigor/documentation improvements that close silent-fail modes.

#### **Fixed (HIGH — closes silent-fail modes)**

* **`SKILL.md §1` load-semantics ambiguity**: previous wording "load the matching reference" did not specify WHO reads WHEN. A junior agent could consult the selection table, memorize the choice, and never actually `Read` the reference file — proceeding to §2 with only abstract concepts and no invocation syntax. Now explicitly: "**Use the `Read` tool to load the matching reference file now**, before applying §2–§6."
* **`sequential-fallback.md` untested claim**: the file was marked "Complete and vendor-agnostic" but had never been exercised on a non-Claude runtime. Downgraded to "**proposed pattern, not yet validated**" with an explicit caveat that all claims about wall-clock overhead, context-bleed, and persona-swap effectiveness are theoretical. Parent `SKILL.md §7` gained the same caveat. Invites first-validator PR after real run.

#### **Fixed (MED — closes fail-soft-where-loud-was-safer)**

* **Stubs now emit a visible DEGRADED-MODE banner** (`gemini-cli.md`, `cursor.md`, `antigravity.md`): previously a non-Claude agent landing on a stub silently fell through to sequential fallback — user thinks they have parallel execution, actually running at ~3× latency. The banner makes the degradation loud at the top of each stub.
* **`SKILL.md §1.1` detection now specifies cwd-walkup**: previous rule assumed the agent ran from project root. Now detects via find-up (walk from cwd toward filesystem root, stop at `.git`), and emits a warning rather than silently falling back when no marker is found.
* **`SKILL.md §1.2` tie-break clarified**: when multiple runtime markers match, replace the untestable "prefer runtime currently executing" with concrete signals — tool-list fingerprint (`Agent`+`TeamCreate`+`SendMessage` → Claude Code), explicit `runtime:` caller hint, and explicit warning on still-ambiguous instead of silent guess.
* **v3.14.0 CHANGELOG overclaim softened**: "No behavior change for Claude Code users" → "Content preserved; section numbering reorganized — see §9 History and `references/claude-code.md` for the mapping." Calls out the `§5.1 → §5` anchor shift for anyone citing the old structure in external notes.

#### **Fixed (LOW — dedup + translation hint)**

* **Stubs deduplicated via `references/_stub-template.md`**: previously 3 near-identical files (~45 lines each, ~80% shared). The shared checklist + contribution guidance now lives in `_stub-template.md`; vendor-specific stubs slimmed to ~22 lines each, carrying only the vendor-specific marker + warning banner + pointer to template. Maintenance: update one template file instead of three.
* **`sequential-fallback.md` adds orchestration-style note**: previously assumed chat-based orchestration (messages as persona swaps). Added explicit SDK/API translation note — for non-chat runtimes, the pattern is one `system` prompt per teammate with `messages` list reset between roles; merge logic unchanged.

#### **Impact**

* No code execution path changed. All changes are documentation rigor + fail-loud where v3.14.0 was fail-soft.
* Agents applying the skill are now explicitly told to `Read` a reference (closes silent fallthrough).
* Claims that were aspirational are now labeled aspirational (closes overclaim).
* Stub files degrade visibly instead of silently (closes user-surprise).

Adversarial convergence signal: `issues-found` at the start; `clean-pass` after these fixes. Further adversarial cycles should start surfacing cosmetic-only items — at that point hallucination convergence is near.

---

### **v3.14.0 — `skill-parallel-orchestration` vendor-agnostic rewrite + per-vendor reference files**

**Motivation**: the previous `skill-parallel-orchestration/SKILL.md` was authored as vendor-agnostic documentation but in practice encoded Claude Code primitives throughout (`Agent` tool, `.claude/agents/`, `subagent_type`, `TeamCreate`/`SendMessage`, "Claude Code harness permits up to 3 Explore agents"). Agents running on Gemini CLI, Cursor, Antigravity, or any other runtime had no way to apply the skill.

This release splits the methodology (universal) from the invocation syntax (vendor-specific), without breaking the Claude Code reference implementation.

#### **Added**

* **Vendor-agnostic core** — [`SKILL.md`](.agent/skills/skill-parallel-orchestration/SKILL.md) rewritten to v3.0. Now contains only universal concepts: Orchestrator/Teammate roles, Layer A vs Layer B decision criterion, three-phase protocol (Decompose → Spawn → Merge), Red Flags, Best Practices, Exploration-default-ONE rule, Merge rules. No Claude-specific tool names, paths, or syntax.

* **Per-vendor reference files** in `references/`:
  - [`references/claude-code.md`](.agent/skills/skill-parallel-orchestration/references/claude-code.md) — **complete**. Claude Code primitives: `Agent` tool, `.claude/agents/` convention, `subagent_type`, single-message multi-tool-call pattern, `requestId` parallelism verification, Layer B (`TeamCreate`/`SendMessage`) with v3.13.0 probe findings, tools whitelist convention. Paired with the existing `examples/usage_example.md`.
  - [`references/sequential-fallback.md`](.agent/skills/skill-parallel-orchestration/references/sequential-fallback.md) — **complete, universal**. Role-switching through a single session for any runtime lacking a parallel-spawn primitive. Documents trade-offs (N× slower, loses per-teammate context isolation, no Layer B), concrete single-session persona-swap protocol, and anti-patterns specific to single-session execution ("don't let critic B see critic A's output").
  - [`references/gemini-cli.md`](.agent/skills/skill-parallel-orchestration/references/gemini-cli.md), [`references/cursor.md`](.agent/skills/skill-parallel-orchestration/references/cursor.md), [`references/antigravity.md`](.agent/skills/skill-parallel-orchestration/references/antigravity.md) — **stubs**. Contain a contribution checklist and direct users to the universal fallback until filled in by someone running the framework on that vendor.

* **Reference-selection protocol** — parent `SKILL.md` §1 now mandates loading the matching reference before applying the protocol, with a runtime-indicator table (`CLAUDE.md` + `.claude/agents/` → `claude-code.md`; `GEMINI.md` → `gemini-cli.md`; `.cursor/` → `cursor.md`; fallback to `sequential-fallback.md`).

#### **Changed**

* **`examples/usage_example.md`** — header updated to mark the example as Claude Code–specific and point vendor-agnostic users at the parent `SKILL.md` + the matching reference file. Example body unchanged (it was already a Claude-specific walk-through).

* **`docs/ROADMAP.md` Wave 5** — updated from "Not started" to "Partially unlocked at v3.14.0". The methodology-level vendor split is now in place; what remains is the subagent-definition portability layer (`.agent/agents/*.md` SOT + generator script) — unblocked when a second vendor is actually adopted.

#### **Not changed**

* No changes to existing wrappers in `.claude/agents/` (still 16, unchanged).
* No changes to `/vdd-multi` workflow or its v3.13.0 parameter set.
* Content for Claude Code users is preserved (same methodology, same examples); section numbering was reorganized in the v3.0 split — see §9 History and `references/claude-code.md` for the mapping. Callers citing "skill §5.1 Explore default" in notes should update to "skill §5" (content unchanged).
* Deprecated `scripts/spawn_agent_mock.py` remains retired; retained only for `fcntl`-locking regression tests.

#### **Impact**

* Framework's multi-vendor claim (stated in README and CLAUDE.md) is now real at the methodology layer: universal concepts are cleanly separated from Claude-specific invocation syntax.
* Agents on non-Claude runtimes get an explicit, vendor-neutral fallback path (sequential persona-swap) that preserves all universal concepts.
* Extension point established: adopting a new vendor is a matter of filling in its `references/<vendor>.md` plus adding subagent definitions (Wave 5 remaining scope), not rewriting the skill.

---

### **v3.13.1 — External-feedback integration: 2 immediate fixes + roadmap absorption**

Applied actionable lessons from a multi-hour VDD session in an external project (captured in [docs/agentic-refine.md](docs/agentic-refine.md)). Two small high-value fixes shipped immediately; the rest integrated into [docs/ROADMAP.md](docs/ROADMAP.md) with explicit reopen criteria.

#### **Fixed — silent false-positive tests_pass (Rec #1, small)**

The `developer` subagent previously returned `tests_pass: true` in its structured output regardless of whether tests actually executed — a shadow-pass that propagated unverified claims to the orchestrator. The wrapper's return contract now requires concrete evidence:

* `tests_pass: true` is **forbidden without `verification_evidence`** (test output, report path, or command transcript).
* `tests_pass: "syntax_only"` — parser/linter ran but no runtime tests.
* `tests_pass: null` — cannot execute tests (no runtime access, sandbox, etc.); reason goes in `blocking_questions`.

This closes a known class of silent-bug propagation where developers without execution rights shadow-passed tests. The feedback source caught a real SQL-migration bug that would have shipped had the main session trusted the false `tests_pass: true`.

#### **Changed — Explore parallelism default 3 → 1 for reconnaissance (Rec #3, small)**

Added §5.1 "Explore parallelism — default to ONE" to [.agent/skills/skill-parallel-orchestration/SKILL.md](.agent/skills/skill-parallel-orchestration/SKILL.md). The Claude Code harness permits up to 3 parallel Explore agents, but the ceiling is a scalability tool, not a quality tool. First-pass reconnaissance should spawn one well-scoped Explore; fan out to 2–3 only when objectively orthogonal subsystems are identified (frontend + backend + infra, no shared files).

Observed symptom from the feedback source: three parallel Explores returned ~20k words of reference material with ~30% load-bearing content. One sharper prompt would have returned the same signal at ⅓ the cost.

#### **Deferred to [docs/ROADMAP.md](docs/ROADMAP.md) — remaining 5 recommendations + meta-observation**

Integrated as new ROADMAP entries with explicit reopen criteria:

* **Drift detection before apply-to-live operations** (Deferred, conditional on apply-to-live workflows appearing).
* **`/vdd-recover` + `/vdd-post-deploy-watch` workflows** (Deferred, conditional on Deploy-phase epic or second friction incident).
* **Deploy-as-a-phase** (potential new epic — idea level, large scope).
* **Structured drift reports from reviewers** (Nice-to-have, triggers on first human hunting through prose).
* **MCP tool truncation documentation** (Nice-to-have, conditional on MCP adoption).
* **TodoWrite nag rate-limiting** → out-of-scope (Claude Code harness-level, not this framework's source).

Full feedback artifact preserved at [docs/agentic-refine.md](docs/agentic-refine.md) for future reference.

#### **Impact**
* No behavior change in Layer A `/vdd-multi` (same 16 wrappers, same parallel critic flow).
* Developer subagent's machine-readable output is now honest about test execution status.
* Analysis/Architecture phases spawn fewer Explores by default when reconnoitering.

---

### **v3.13.0 — `/vdd-multi` parameters + Wave 4 runtime probe findings**

Adds first-class parameters to `/vdd-multi` for scoped runs, CI integration, PR reviews, and fixture preservation. Also documents the Native Teams (Layer B) runtime probe — what works, what's broken, and why Wave 4 is deferred.

#### **Added — `/vdd-multi` parameters**

Previously `/vdd-multi <path>` took only a target path. Now accepts 5 inline flags:

* `--scope=logic|security|performance|all` (comma-separated list supported) — run only selected critic(s). Saves tokens when area is known.
* `--no-fix` — skip Phase 3 iterative fix loop (report-only mode). For CI, smoke tests, pre-merge review bots.
* `--fail-on=critical|high|medium|low|none` — surface a PASS/FAIL verdict when any finding meets/exceeds the threshold. Workflow always completes; flag only controls the terminal verdict.
* `--output=<path>` — write merged report to file instead of inline; orchestrator returns a short pointer. For persistent artifacts under `docs/reviews/`.
* `--diff-only` — bound review to files in `git diff` vs `main`. Auto-on when no target is given. Critics receive changed files + per-file diff context. Primary use case: PR review.

Example CI invocation: `/vdd-multi --diff-only --no-fix --fail-on=high --output=docs/reviews/pr-42.md`.

Workflow file [.agent/workflows/vdd-multi.md](.agent/workflows/vdd-multi.md) rewritten:
* Added "Invocation / Parameters" section with flag table + examples.
* New Phase 0 ("Parse invocation") normalizes flag input + derives `git diff` target list when `--diff-only`.
* Phase 2 "Merge & deduplicate" honors `--severity` filter and derives verdict from `--fail-on`.
* Phase 3 "Iterative fix loop" skipped when `--no-fix`.
* Termination line now includes verdict + output-path pointer.
* Sequential fallback (non-Claude-Code vendors) honors all flags.

#### **Added — Wave 4 Native Teams runtime probe**

Ran a minimal `TeamCreate` + `Agent(team_name, name)` + `SendMessage` + `TeamDelete` smoke cycle to verify Layer B runtime (experimental flag `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` already set). Documented findings:

**Works**:
* `TeamCreate` creates `~/.claude/teams/<name>/config.json` + `~/.claude/tasks/<name>/.lock`.
* `Agent(team_name, name, subagent_type)` spawns teammate asynchronously (returns immediately with `agent_id`; teammate runs in background).
* Teammate executes task correctly (verified by counting `.md` files — returned 16, matches actual wrapper count).
* `SendMessage` delivers to inbox file (`~/.claude/teams/<name>/inboxes/<recipient>.json`) as JSON array with `from`, `text`, `summary`, `timestamp`, `color`, `read`.
* Shutdown round-trip (`shutdown_request` → `shutdown_approved`) completes within ~2 seconds.

**Broken or surprising** (new entries in [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)):
* **`TeamDelete` does NOT clean up after protocol shutdown**: `config.json` members array is not updated on `shutdown_approved`; `TeamDelete` fails with `Cannot cleanup team with N active member(s)`. Error message references `requestShutdown` which is not an available tool. Workaround: manual `rm -rf ~/.claude/teams/<name>/ ~/.claude/tasks/<name>/`.
* **Async spawn ≠ sync return**: unlike Layer A where `Agent` returns the subagent's result, Layer B `Agent(team_name)` returns immediately. Lead must poll inbox file or await an auto-delivered turn.
* **Model inheritance inconsistent**: `subagent_type: "Explore"` teammate defaulted to `model: "haiku"` regardless of lead's model. Must override explicitly if Opus needed.
* **Runtime sends structured JSON despite docs**: `{"type":"idle_notification",...}` and `{"type":"shutdown_approved",...}` are auto-delivered to lead's inbox even though docs say "Do NOT send structured JSON status messages". Parsers must handle both.

**Decision**: Wave 4 (full Layer B `/teams-vdd-multi` workflow) remains deferred. Layer A (parallel `Agent` spawn in one message) handles the current `/vdd-multi` use case fully, is proven twice under smoke tests (Sonnet + Opus), and has none of the Layer-B gotchas above. Wave 4 reopens only when a concrete peer-debate scenario makes the extra complexity justified.

#### **Changed**
* [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) — Native Teams section expanded with 3 new findings from the probe (TeamDelete cleanup, async spawn, model inheritance, runtime JSON messages).
* [docs/TASK.md](docs/TASK.md) — Completed Waves table adds `Wave 4 probe + /vdd-multi parameters (v3.13.0)` row.

#### **Not changed (explicit)**
* No new subagent wrappers (still 16).
* No changes to Layer A behavior — `/vdd-multi` without flags runs identically to v3.12.0.
* No Layer B workflow (`/teams-vdd-multi`) — deferred.

---

### **v3.12.0 — Agent Teams Mode Wave 3: Product-Pipeline Subagent Wrappers**

#### **Added**
* **4 new product-pipeline subagent wrappers** in `.claude/agents/` — brings total wrapper count to **16** (3 Wave-1 critics + 9 Wave-2 dev-pipeline + 4 Wave-3 product):
  - **`strategic-analyst`** (sonnet) — The Researcher. Produces `docs/product/MARKET_STRATEGY.md` (TAM/SAM/SOM, competition, timing, pre-mortem, verdict score). SOT: `System/Agents/p01_strategic_analyst_prompt.md`.
  - **`product-analyst`** (sonnet) — The Visionary. Produces `docs/product/PRODUCT_VISION.md` with INVEST stories, SMART KPIs, 10-factor viability score. SOT: `System/Agents/p02_product_analyst_prompt.md`.
  - **`product-director`** (opus) — The Gatekeeper / VC Proxy. Applies Adversarial-VDD Acid Test (hallucination check, moat check, fluff check) to Strategy + Vision. Produces `docs/product/APPROVED_BACKLOG.md` (with WSJF + `APPROVAL_HASH` via sign-off script) or `REVIEW_COMMENTS.md`. SOT: `System/Agents/p03_product_director_prompt.md`.
  - **`solution-architect`** (sonnet) — The Pragmatist. Verifies `APPROVAL_HASH` at entry (stops if missing/invalid — security violation). Produces `docs/product/SOLUTION_BLUEPRINT.md` (WHAT to build: requirements, UX flows, ROI — NOT HOW). SOT: `System/Agents/p04_solution_architect_prompt.md`.

* **`docs/ARCHITECTURE.md` §5.1** — new Wave 3 catalog table (4 rows: SOT path, tools, model, role); Model policy block updated to **10 Opus + 6 Sonnet**.

#### **Changed**
* **`planner` wrapper model: sonnet → opus** (was silently updated post-v3.11.2; now formally documented). Rationale: plan decomposition (Stub-First, atomicity, RTM coverage) has verifier-like rigor — a weak plan corrupts every downstream developer invocation. Matches the verifier-tier pattern.
* **Model policy documentation** now lists 10 Opus + 6 Sonnet roles and explains the inclusion of `planner` and `product-director` in the Opus tier.
* **`docs/TASK.md`** — TASK-060 (Wave 3) now the current active task; Completed Waves table updated with `Hardening (v3.11.1)`, `Opus upgrade (v3.11.2)`, and `Wave 3 (v3.12.0)` rows.

#### **Design decisions**
* **`product-director` is a "verifier that writes"** (unlike dev-pipeline reviewers which return text reports). SOT prescribes specific output filenames (`APPROVED_BACKLOG.md`, `REVIEW_COMMENTS.md`) that downstream agents consume contractually (`solution-architect` requires `APPROVED_BACKLOG.md` with valid hash). Wrapper body documents this exception explicitly.
* **`solution-architect` verifies `APPROVAL_HASH` at entry** — if missing/invalid, subagent STOPS and reports a security violation rather than producing a blueprint. This honors the Logic Locker from SOT §4.3.
* **No workflow rewrites in Wave 3** — consistent with Wave 2: wrappers are infrastructure. Product workflows (`/product-full-discovery`, `/product-market-only`, `/product-quick-vision`) keep working via sequential role-switching; wrappers enable parallel or named-type spawn when useful.
* **`p00_product_orchestrator_prompt.md` not wrapped** — orchestrator roles (`01`, `p00`) stay as main-agent personas because Claude Code native Teams do not support nested teams.

#### **Verified**
* All 16 wrappers: YAML frontmatter valid, `name` matches filename, thin-adapter body size unchanged (7–8 lines).
* No regression: `git diff` limited to new Wave 3 files + `docs/ARCHITECTURE.md` §5.1 + `docs/TASK.md` + changelog/readme. Wave 1/2 artifacts untouched.

#### **Out of Scope (future waves)**
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.

---

### **v3.11.2 — Verifier subagents upgraded to Opus**

All 8 verifier wrappers now run on `model: opus`; 4 builder wrappers stay on `sonnet`.

#### **Changed**
* **8 verifiers → opus**:
  - 3 adversarial critics: `critic-logic`, `critic-security`, `critic-performance`
  - 4 pipeline reviewers: `task-reviewer`, `architecture-reviewer`, `plan-reviewer`, `code-reviewer`
  - `security-auditor` (full-audit role)
* **4 builders stay on sonnet**: `analyst`, `architect`, `planner`, `developer`

#### **Rationale**
Verification is a quality gate — missed bugs, missed vulnerabilities, and approved broken architecture cost orders of magnitude more than the extra token spend. Opus's deeper reasoning, stronger adversarial thinking, and more calibrated doubt (resistance to "it probably works" rationalization) justify the cost for the verifier tier. Creation tasks are template-driven under Stub-First and follow the SOT structure; Sonnet produces equivalent artifact quality there at ~5× lower cost and lower latency.

Smoke-test cost impact: three parallel Opus critics in `/vdd-multi` ≈ 3–5× Sonnet's token cost per run. A single missed SQLi or logic regression in production easily exceeds that by orders of magnitude.

#### **Impact on behavior**
* `/vdd-multi` parallel critique now runs on Opus critics — expect slightly slower wall-clock per critic (Opus latency) but higher finding rates on edge cases and subtle adversarial scenarios. Merge/dedup rules unchanged.
* Builder-stage workflows (`analyst` → `architect` → `planner` → `developer`) see no latency or cost change.

#### **Documentation**
* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §5.1 — added `Model` column to the 12-wrapper catalog + Model policy block explaining the split.

---

### **v3.11.1 — Thin-Wrapper Refactor + Adversarial Review Fixes**

Self-review of v3.10.0 and v3.11.0 surfaced 3 real bugs and 7 anti-patterns. This release fixes them.

#### **Fixed (HIGH — real bugs)**
* **`.agent/tools/task_id_tool.py`**: added CLI main block (`argparse` + JSON output to stdout). Was referenced in [CLAUDE.md](../CLAUDE.md#L29) (`python3 .agent/tools/task_id_tool.py <slug>`) and in the v3.11.0 `planner` wrapper, but the module had no `if __name__ == "__main__":` — running it produced empty output. Now emits `{"filename": "task-NNN-<slug>.md", "used_id": "NNN", "status": "generated|corrected", "message": null}`.
* **`.claude/agents/security-auditor.md`**: removed `Bash(python3 -m bandit:*)` from tools — bandit is not installed in the default environment, so declaring the tool was a false promise.
* **`.claude/agents/` — Bash tool syntax**: removed non-standard `Bash(cmd:*)` colon pattern from all wrappers. The subagent-frontmatter `tools` field and project [.claude/settings.json](../.claude/settings.json) `permissions.allow` are distinct mechanisms; subagent tools now list simple names only (`Read, Grep, Glob, Bash`), and settings.json governs which Bash sub-commands auto-approve vs prompt. Reviewers/critics without `Bash` in tools cannot invoke any shell command, making the read-only guarantee actually enforced.

#### **Changed — Thin-Wrapper Refactor (MED)**
All 12 wrappers rewritten as **true thin adapters**. The v3.10.0/v3.11.0 wrappers had grown to 50–90 lines each with duplicated skill lists, paraphrased SOT guardrails, and restated return-format blocks. This was a drift hazard: on SOT edits, wrappers would silently fall behind.

* **Size**: `.claude/agents/` total went from **842 lines → 160 lines** (−81%). Each wrapper is now 13–14 lines (7–8 lines body) and contains only:
  1. Frontmatter (`name`, `description`, `tools`, `model`).
  2. One-line SOT pointer: `You are the <Role> teammate. Full system prompt ... lives in [SOT path] — read and follow strictly.`
  3. `Subagent adaptations`: 1–3 bullets covering only what differs from SOT when running as subagent (primarily "return text report to orchestrator instead of writing `docs/reviews/…`").
* **No duplicated skill lists**: wrappers no longer restate SOT §2 skill loads. SOT is authoritative.
* **No cargo-cult guardrails**: wrappers no longer paraphrase SOT Prime Directives. Guardrails live in SOT.
* **No invented return formats**: wrappers link to SOT's contract; orchestrator handles the schema.
* **Consistent description grammar**: all 12 start with an infinitive action verb (`Transform`, `Review`, `Design`, `Decompose`, `Implement`, `Perform`) for more predictable auto-routing.
* **Cross-reference between `critic-security` and `security-auditor`**: both wrappers now disambiguate in their `description` field (lightweight parallel critic vs. full audit).
* **Removed aspirational `files_modified` merge claim** from `developer.md` — no such merge logic exists in the orchestrator.

#### **Changed — Docs**
* **`docs/ARCHITECTURE.md` §5.1 wrapper catalog table**: tools column now shows exact frontmatter values (no vague "git read-only" or phantom "bandit"); added a "Tools note" explaining the division between subagent `tools` frontmatter and settings.json `permissions`; design convention block updated to reflect actual ~15-line size target.

#### **Impact on behavior**
* **None expected**. Critics and reviewers continue to read the same SOT files; the SOT is where methodology lives. Wave 1 smoke-test behavior should reproduce identically (same SOT → same critique quality).
* **Maintenance improved**: edits to SOT (e.g., new skill added to `02_analyst_prompt.md` §2) propagate automatically to the `analyst` subagent on next spawn — no wrapper update needed.

#### **Verified (smoke-test on `docs/tasks/task-dummy.md`)**
* **Parallel spawn**: single LLM `requestId` (`req_011Ca9FA2hNt4PVJGVTYajEX`) across three critic `Agent` tool_uses in one message — parallelism preserved.
* **Seeded flaw coverage**: critic-logic 2/2, critic-security 4/4, critic-performance 5/5 — matches or exceeds the Wave 1 baseline (v3.10.0: 2/2, 4/4, 5/5).
* **Overlap detection**: both expected cross-category overlaps detected (line 20 flaw #5 SQLi+N+1, line 51/57 flaw #9 file-handle leak); severity escalation rule 3 applied (flaw #9: logic:HIGH + perf:HIGH → CRITICAL).
* **No hallucinations**. Bonus findings grew vs v3.10.0 (path-traversal, missing input validation, no conn pooling, `returncode` check, second-order SQL injection, ambiguous return types) — evidence that thin wrappers do not lose SOT access.
* **Fixture integrity**: `git diff docs/tasks/task-dummy.md` empty; read-only tool whitelist physically enforced (reviewers/critics without `Bash` cannot invoke shell).

---

### **v3.11.0 — Agent Teams Mode Wave 2: Dev-Pipeline Subagent Wrappers**

#### **Added**
* **9 new dev-pipeline subagent wrappers** in `.claude/agents/` (12 total after Wave 1's 3 critics). Each wrapper is a thin Claude Code adapter over `System/Agents/XX_*.md` source of truth, following Option D pattern established in Wave 1:
  - **Builders** (Write/Edit access to their artifact path):
    - `analyst` → TASK.md generator (RTM + acceptance criteria)
    - `architect` → ARCHITECTURE.md designer (Data Model → Components → Interfaces)
    - `planner` → PLAN.md + `docs/tasks/*.md` under Stub-First (uses `task_id_tool` Bash)
    - `developer` → implements atomic tasks with full Bash access
  - **Reviewers** (read-only, return text reports to orchestrator):
    - `task-reviewer` → gates Analysis→Architecture
    - `architecture-reviewer` → gates Architecture→Planning (focus: Data Model, Security, YAGNI)
    - `plan-reviewer` → gates Planning→Execution (RTM coverage, Stub-First, atomicity)
    - `code-reviewer` → gates Execution→Merge (three pillars: Compliance, Quality, Testing) with git read-only
  - **Security-auditor** → full OWASP audit with scoped scanner Bash (`run_audit.py`, `bandit`). Distinct from the Wave 1 lightweight `critic-security` used in `/vdd-multi`.
* **`docs/ARCHITECTURE.md` §5.1 — extended wrapper catalog** with all 12 wrappers, SOT paths, tools whitelist per row, and explicit "wrapper design convention" block (body ≤ ~30 lines, SOT never duplicated).

#### **Design Decisions**
* **No workflow rewrites**: unlike Wave 1 (which rewrote `/vdd-multi`), Wave 2 is pure infrastructure — existing dev-pipeline workflows (`01-04`, `vdd-*`, `develop-all`) keep working through sequential role-switching. Wrappers are *available* for parallel spawn when orchestrator decides (e.g., parallel reviewer pairs, parallel developers for independent tasks).
* **Reviewers return text reports, do not write files**: avoids giving reviewers broad filesystem Write access. Orchestrator persists to `docs/reviews/…` if needed. Same pattern as Wave 1 critics.
* **Strict tools whitelist per role**: builders write to their artifact path only; reviewers are read-only; developer has full Bash (testing, build, scripts). Enforced via frontmatter `tools` field. Verified: attempting Write inside a reviewer subagent fails with permission error.
* **Sonnet model for all 12 wrappers**: baseline choice. Future waves may downgrade specific wrappers to Haiku for cost (e.g., simple reviewers).
* **`security-auditor` ≠ `critic-security`**: full audit role (OWASP Top 10, taint analysis, CVE check, formal `docs/audit/` report) vs. lightweight parallel critic for `/vdd-multi`. Wrappers explicitly document the distinction.

#### **Changed**
* **`docs/TASK.md`** → Wave 2 (TASK-059) is now the current active task; Wave 1 (TASK-058) referenced in the Completed Waves table.
* **`docs/ARCHITECTURE.md` §5.1** — Layer A section expanded from "Wave 1 wrappers" to full 12-wrapper catalog with design convention documentation.

#### **Verified**
* YAML frontmatter validation passes for all 12 wrappers (`name` matches filename, required fields present).
* No regression: `git diff` on Wave 1 artifacts (`.agent/workflows/vdd-multi.md`, Wave 1 critic wrappers) — untouched.

#### **Out of Scope (future waves)**
* Wave 3: 4 product-pipeline wrappers (`strategic-analyst`, `product-analyst`, `product-director`, `solution-architect`).
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.
* Orchestrator prompts (`01_orchestrator.md`, `p00_product_orchestrator_prompt.md`) — native Teams don't support nested teams, these stay as main-agent role personas.

---

### **v3.10.0 — Agent Teams Mode Wave 1: Parallel VDD Multi-Adversarial Critics**

#### **Added**
* **`.claude/agents/` directory** with three thin Claude Code subagent wrappers (Option D — thin adapters over existing SOT skills):
  - `critic-logic` (read-only tools, points to `.agent/skills/vdd-adversarial/SKILL.md`)
  - `critic-security` (read-only + `git log/diff/show`, points to `.agent/skills/skill-adversarial-security/SKILL.md` + `references/prompts/sarcastic.md`)
  - `critic-performance` (read-only tools, points to `.agent/skills/skill-adversarial-performance/SKILL.md`)
* **`System/Agents/01_orchestrator.md` §5.1 — Teams Dispatch**: scenario→layer dispatch table (Layer A: `Agent` tool parallel spawn; Layer B: native `TeamCreate`/`SendMessage` — Wave 4 stub). Role-switching remains primary mode.
* **`docs/ARCHITECTURE.md` §5.1 — Two-Layer Teams Model** with ASCII diagram, shared infrastructure description (`fcntl`-locked session state, SOT-in-skills convention), vendor-portability notes.
* **`docs/KNOWN_ISSUES.md`** — Native Teams gotchas (no session resumption, task status lag, one team per session, no leadership transfer, higher token costs) + Wave 1 wrapper/SOT drift risk.
* **`docs/TASK.md` + `docs/tasks/task-058-teams-mode-wave-1.md`** — RTM with 12 acceptance criteria (R1–R12) across 8 Issues. Smoke-test passed.
* **`docs/tasks/task-dummy.md`** — deterministic smoke fixture with 9 labelled flaws (seeded across logic/security/perf) and two cross-category overlaps for verifying severity-escalation logic. Repeatable — fixture intentionally left un-fixed.

#### **Changed**
* **`.agent/workflows/vdd-multi.md`** rewritten from sequential role-switching to **parallel three-critic spawn** in a single assistant message via `Agent` tool. Phase 2 adds merge rules (location dedup ±3 lines, cross-category re-attribution, severity escalation on overlap, hallucination filter). Phase 3 iterative fix-loop uses single-critic re-spawn (cheaper than re-parallelizing). Sequential fallback documented for non-Claude-Code vendors.
* **`.agent/skills/skill-parallel-orchestration/SKILL.md` → v2.0**: removed `spawn_agent_mock.py` instructions; now references native `Agent` tool with parallel tool-uses in one message. Added Layer B stub (decision criterion: "use iff teammates need inter-teammate communication"). Red Flags and DO/DO-NOT tables updated to reflect native-spawn reality.
* **`.agent/skills/skill-parallel-orchestration/examples/usage_example.md`** rewritten around VDD multi-critic scenario; old "frontend+backend decomposition" example moved to the Layer B (Wave 4) slot.
* **`docs/ARCHITECTURE.md` §5 Parallel Execution Model (POC)** marked `[SUPERSEDED]` — retained for historical context; `fcntl`-locking notes carried forward into §5.1.
* **`.claude/settings.json`**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env flag (activates native Teams for Wave 4). Already enabled prior to commit; now formally part of Wave 1 scope.
* **`CLAUDE.md`**: added Workflow Dispatch point 3 — notes that `/vdd-multi` is parallel in Claude Code with sequential fallback elsewhere; points to orchestrator §5.1 for the layer-decision rule.

#### **Deprecated**
* **`.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py`** and **`tests/test_mock_agent.py`** — module-level `DEPRECATED` docstrings. Scripts retained only to exercise `fcntl`-locking regression tests in `update_state.py`; do not reference from new workflows.
* **`docs/POC_PARALLEL_AGENTS.md`** → moved to `docs/archives/POC_PARALLEL_AGENTS.md` with `SUPERSEDED` header. Open Question #1 (CLI agent-spawn availability) marked closed — native `Agent` tool fills the gap.

#### **Verified**
* Smoke test: single LLM `requestId` observed across all three critic `Agent` tool_uses (`req_011Ca9BWa5rbziH6xcocS57c`) — parallel spawn confirmed via JSONL log analysis. All three critics returned structured `issues-found` reports; merged report deduped 14 issues with 2 cross-category escalations (flaws #5 SQLi+N+1 on fixture line 23, flaw #9 file-handle leak on lines 56–57). No hallucinations; bonus findings (path-traversal, dead API_KEY, missing authn) validated that critics correctly loaded SOT checklists.
* Regression: standard `/vdd` (sequential role-switching) untouched — verified by inspection.

#### **Out of Scope (future waves)**
* Wave 2: 9 wrappers for `System/Agents/02–10` (dev pipeline).
* Wave 3: 4 wrappers for product pipeline (`p01–p04`).
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.

---

### **v3.9.17 — Developer Discipline: Karpathy Guidelines Integration**

#### **Added**
* **§1.5 Think Before Implementing** (`developer-guidelines`): Graduated ambiguity handling protocol — critical ambiguity goes to TASK.md Open Questions, implementation-level decisions are made by the developer with brief documentation, trivial decisions are made silently.
* **§1.6 Implementation Discipline** (`developer-guidelines`): Two-level decision framework — architectural decisions (new modules, public API, data models) must come from PLAN.md/ARCHITECTURE.md; implementation details (internal patterns, helpers, abstractions) are the developer's professional judgment. Speculative complexity is prohibited.
* **§6.2 Multi-Step Tasks** (`developer-guidelines`): Generalized Verification Protocol with `Step → verify: [check]` pattern, extending the Bug Fixing Protocol to all multi-step work.
* **Before/after code examples** (`developer-guidelines/examples/coding-anti-patterns.md`): 3 real-world examples — drive-by refactoring, speculative features vs. plan-driven implementation, silent interpretation vs. surfacing ambiguity. Adapted from Karpathy Guidelines for complex product development context.

#### **Improved**
* **Red Flags** (`developer-guidelines` §0): +2 entries — against silent architectural changes and speculative features.
* **Strict Adherence** (`developer-guidelines` §1): +2 entries — Task Traceability (every change must serve the task, professional choices within scope are OK) and Style Matching (match existing code style).
* **Rationalization Table** (`developer-guidelines` §9): +3 entries covering speculative additions, silent plan deviation, and drive-by improvements.
* **Atomicity & Traceability** (`core-principles` §1): Added Verification Checkpoints for multi-step tasks.
* **Minimizing Hallucinations** (`core-principles` §3): Added Ambiguity Protocol with cross-reference to developer-guidelines §1.5.
* **Token budget** (`skill-phase-context`): Updated Development phase estimate from ~768 to ~1,100 to reflect expanded developer-guidelines.

#### **Design Decisions**
* **"Implementation Discipline" instead of "Simplicity First"**: Karpathy's "minimum code" principle was adapted for complex product development — architectural complexity is valid when plan-driven; only speculative complexity is prohibited.
* **Graduated Ambiguity instead of "ask everything"**: Three-tier protocol prevents bombarding users with questions while ensuring critical decisions are surfaced.
* **No new standalone skill created**: All changes integrated into existing `developer-guidelines` (Tier 1) and `core-principles` (Tier 0) to avoid skill bloat and tier conflicts.

---

### **v3.9.16 — Security Audit v3.2: Smart Contract Patterns & Modular Architecture**

#### **Added**
* **Solidity/Smart Contract patterns** (16 new): Reentrancy (`.call{value:}`, `.send()`, `.transfer()`), arbitrary execution (`delegatecall`, `selfdestruct` EIP-6780, `suicide()`), access control (`tx.origin`, public/external without modifier), oracle manipulation (`getReserves()`, `latestRoundData()`), unchecked return values, unprotected initializers, integer overflow (pre-0.8.0), locked ether, inline assembly.
* **VDD Round 3 critique** document with real hack coverage matrix (Dec 2025 – Mar 2026).
* **Real-world hack validation**: Scanner tested against contracts simulating SwapNet ($13.4M), Truebit ($26.4M), YieldBlox ($10.2M), Aperture ($4M) attack vectors — 7/10 vectors fully detected.

#### **Improved**
* **Modular scanner architecture**: Refactored 886-line monolith `run_audit.py` into 7-file package (`audit/config.py`, `audit/patterns.py`, `audit/helpers.py`, `audit/scanners.py`, `audit/external.py`, `audit/__init__.py`).
* **MAX_FILE_SIZE consistency**: Added 5MB file size guard to `scan_configuration()` and `scan_iac()`.
* **Pattern count**: 105 → 121 total patterns (28 secret + 62 dangerous + 25 IaC + 6 config).

#### **Fixed**
* **VDD Round 2** (8 issues): `os.popen()` CWE misclassification, missing `subprocess.run shell=True`, Flask open redirect regex, SQL `%` formatting detection, IaC false positives on non-IaC YAML, symlink following, SSRF pattern expansion.

---

### **v3.9.15 — Claude Code Integration**

#### **Added**
* **Claude Code entry point**: Created `CLAUDE.md` (136 lines) adapted from `GEMINI.md` with native Claude Code tool references (Read, Write, Edit, Bash, Grep, Glob), session state bootstrap, and explicit tier-based skill loading protocol.
* **Claude Code hooks**: Added `.claude/settings.json` with `PostToolUse` hook and `.claude/hooks/validate_skill_hook.sh` for automatic skill validation on file modification.
* **Claude Code commands**: Created 20 slash command files in `.claude/commands/` covering all 21 workflows (delegator pattern — single source of truth in `.agent/workflows/`).
  * Core: `/start-feature`, `/plan`, `/develop`, `/develop-all`, `/light`
  * VDD: `/vdd`, `/vdd-start-feature`, `/vdd-plan`, `/vdd-develop`, `/vdd-adversarial`, `/vdd-multi`
  * Pipelines: `/full`, `/security-audit`, `/base-stub-first`, `/framework-upgrade`, `/iterative-design`
  * Product: `/product-full-discovery`, `/product-market-only`, `/product-quick-vision`
  * Docs: `/update-docs`
* **Migration specification**: Added `docs/migration-to-claude.md` with full platform comparison, tool mapping, hook adaptation guide, and validation checklist.

#### **Improved**
* **AGENTS.md**: Added missing "Session State Persistence" instruction (`update_state.py` on phase boundaries), achieving parity with `GEMINI.md`.
* **SESSION_CONTEXT_GUIDE.md**: Added Section 5 "Platform Memory Integration" documenting how framework session state complements platform-specific memory systems (Claude Code, Cursor, Gemini).
* **README.md / README.ru.md**: Updated "Option C: Claude Code" section — replaced manual setup instructions with ready-to-use configuration and full command list.

---

### **v3.9.14 — Enterprise Hardening Wave (BI-001..009)** (Security / Reliability / Governance)

#### **Added**
* **Governance docs**:
    * Added `System/Docs/SOURCE_OF_TRUTH.md` with authoritative mappings for prompts, skills, workflows, tools, and command conventions.
    * Added `System/Docs/RELEASE_CHECKLIST.md` with release gates and mandatory validation commands.
* **Validation and guardrail scripts**:
    * Added `System/scripts/check_prompt_references.py`, `System/scripts/security_lint.py`, `System/scripts/smoke_workflows.py`, `System/scripts/validate_skills.py`, and `System/scripts/doctor.py`.
* **CI gatekeeping**:
    * Added `.github/workflows/framework-gates.yml` to enforce tooling tests, skill validation, workflow smoke checks, reference integrity, and security linting.
* **Regression coverage**:
    * Added `tests/test_tool_runner_security_contract.py`, `tests/test_spec_validator.py`, and `tests/test_product_handoff_scripts.py`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Structured Evals Workflow**: Added a full section for defining and running vendor-agnostic tests (evals) for skills using LLM-as-a-judge (`evals/evals.json`).
    * **Agent Prompts**: Moved 3 ready-to-use prompts to `agents/` for automated skill evaluation (`grader.md`, `comparator.md`, `analyzer.md`).
    * **Reporting Scripts**: Added infrastructure to `scripts/` for processing evaluator results (`aggregate_benchmark.py`, `generate_report.py`, `generate_review.py`).
    * **JSON Schemas**: Added `references/eval_schemas.md` defining a Single Source of Truth for 8 JSON evaluation formats.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Phase 1.7 (Behavioral Analysis)**: Added a new audit phase to review usage logs and recommend extracting FAQs to `references/` and helpers to `scripts/`.

#### **Improved**
* **Tool execution security (BI-001)**:
    * Hardened `System/scripts/tool_runner.py` command policy (`shell=False`, disallowed shell chars/operators, allowlist checks, timeout handling, normalized `cwd` checks).
    * Expanded and aligned tool schemas in `.agent/tools/schemas.py`; updated runtime docs in `System/Docs/ORCHESTRATOR.md`.
* **Workflow and path integrity (BI-002, BI-009)**:
    * Repaired stale prompt/workflow references across workflow files and READMEs.
    * Standardized command conventions to canonical `run <workflow-name>` with explicit slash alias notes.
* **Python environment standardization (BI-004)**:
    * Added pinned dev dependencies (`requirements-dev.txt`) and setup guidance in `README.md` and `README.ru.md`.
* **Skills standardization, technical scope (BI-007)**:
    * Added missing `tier`/`version` metadata where absent.
    * Relaxed strict CSO prefix enforcement for existing stable skills to avoid forced legacy rewrites.
* **Meta-skill execution policy hardening**:
    * Updated `.agent/skills/skill-creator/SKILL.md` and `.agent/skills/skill-creator/assets/SKILL_TEMPLATE.md` with explicit sections: `Execution Mode`, `Script Contract`, `Safety Boundaries`, and `Validation Evidence`.
    * Extended `.agent/skills/skill-creator/scripts/validate_skill.py` with warning-first execution-policy checks and optional strict mode (`--strict-exec-policy`).
    * Extended `.agent/skills/skill-enhancer/scripts/analyze_gaps.py` with execution-policy gap detection (missing contract sections + script/scope safety signals).
    * Updated `.agent/skills/skill-enhancer/references/refactoring_patterns.md` with migration patterns: prompt-only -> hybrid, ad-hoc script -> governed script, unsafe mutation -> scoped mutation.

* **Skill validator operational alignment (BI-007 follow-up)**:
    * Added `validation.inline_exempt_skills` in `.agent/rules/skill_standards.yaml` for legacy full-context skills that must keep large inline blocks.
    * Updated `.agent/skills/skill-creator/scripts/validate_skill.py` to skip inline-size enforcement for explicitly exempted skills while keeping the default limit for new skills.
* **Skill-creator defaults discoverability**:
    * Added `.agent/skills/skill-creator/references/default_parameters.md` with configuration resolution order, bundled defaults, runtime fallbacks, and maintenance rule.
    * Updated `.agent/skills/skill-creator/SKILL.md` to reference the defaults map and `skill_utils.py` for effective merged-config inspection.
* **Release checklist scope tuning**:
    * Updated `System/Docs/RELEASE_CHECKLIST.md`: product handoff safety checks are optional and required only when modifying `skill-product-handoff`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Graduated Instructions**: Replaced strict `MUST/ALWAYS` constraints with a two-tier approach (`MUST + explanation` for safety, `explain why + do` for behavioral tuning).
    * **Description Pushiness Optimization (CSO)**: Expanded SEO-optimization guidelines for skill descriptions, advocating for more aggressive triggers.
    * **Behavior Iteration Loop**: Added a step in skill creation to extract repetitive agent code/questions into `scripts/` or `references/`.
    * **Environment Adaptation**: Added recommendations for Fallback strategies for skills relying on specific CLIs or browsers.
    * **Target Audience Selection**: Guidelines now require explicitly defining the target audience before writing.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Graduated Language Check**: `analyze_gaps.py` and pipeline instructions now evaluate using the two-tier motivation system. Updates internal VDD checklists and refactoring patterns.
    * **Description Pushiness Check**: Added rules to verify the "aggressiveness" of triggers in skill descriptions.
    * **Test Coverage Check**: Final VDD Check now enforces the presence of at least 2-3 test prompts (either in `evals.json` or text).
    * **Generalization Check**: Added audit to prevent overfitting of skills to overly narrow examples.
    * **Agent References**: Local references to SSoT agents (`skill-creator/agents/`) updated.

#### **Fixed**
* **Spec validator correctness (BI-003)**:
    * Fixed requirement ID matching logic in `.agent/skills/skill-spec-validator/scripts/validate.py` (literal token handling + regression tests).
* **Product handoff hardening (BI-008)**:
    * Hardened `.agent/skills/skill-product-handoff/scripts/sign_off.py`, `.agent/skills/skill-product-handoff/scripts/verify_gate.py`, and `.agent/skills/skill-product-handoff/scripts/compile_brd.py` with argparse CLI, explicit file args, and safe path validation.
* **Artifact memory hardening, technical part (BI-006)**:
    * Extended `.agent/skills/skill-update-memory/scripts/suggest_updates.py` with deterministic bootstrap controls:
        * Added `--mode bootstrap` + `--create-missing` for controlled initial memory file generation.
        * Added explicit development scope via `--development-root` (default: `src`).
        * Added hard exclusions for `/.agent/skills/*` and `/.cursor/skills/*` to prevent unintended memory-file creation in skills catalogs.
        * Preserved graceful behavior when `.AGENTS.md` is missing (no hard failure).
    * Aligned workflow/docs contract for migration usage:
        * Updated `.agent/workflows/04-update-docs.md` bootstrap command to use `--development-root src`.
        * Updated `System/Docs/SOURCE_OF_TRUTH.md` and skill docs to reflect optional `.AGENTS.md` + scoped bootstrap policy.
* **skill-creator v1.3**:
    * Updated `validate_skill.py`: `agents/` and `evals/` directories are now whitelisted to avoid false-positives during strict checks.
    * Corrected typos in JSON keys in `SKILL.md` examples for strict schema compliance (`input_files` -> `files`, `expected_outcomes` -> `expectations`).
* **skill-enhancer v1.2**:
    * `analyze_gaps.py`: Improved markdown parsing to prevent false-positives for missing `Phase/Step` prefixes inside JSON blocks.
    * Cleaned up phantom links to "(Coming in Iteration 2)" — all declared architecture now actually exists.

#### **Verified**
* `System/scripts/check_prompt_references.py --root .` and `System/scripts/smoke_workflows.py --root .` pass in the target repository.
* Backlog status alignment: BI-001..006, BI-008, and BI-009 are marked `Done` in `Backlog/archive/framework_improvements_20260219.md`.

---

### **v3.9.13 — Security Audit Enhancement & Workflow Alignment** (Feature / Maintenance)

#### **Added**
* **Developer Guidelines**:
    * **Security Quick-References**: Added condensed guides for 10 frameworks (Flask, Django, FastAPI, Express, Next.js, React, Vue, jQuery, JS General, Go).
    * **Dynamic Loading**: Updated `SKILL.md` (v1.1) to dynamically load strict security references based on project context.

#### **Refactored**
* **`security-audit` Workflow**:
    * **Unified Script**: Updated `.agent/workflows/security-audit.md` to use the unified `run_audit.py` script.
    * **Modernization**: Removed outdated prompt references and aligned manual review steps with the "Think Like a Hacker" protocol.
* **`skill-adversarial-security` (v1.1)**:
    * **Gold Standard**: Added strict "Red Flags" (Anti-Rationalization) and "Rationalization Table" (Developer Excuses).
    * **Cleanup**: Removed duplicate sections and updated script execution commands to match v2 standards.
    * **Verification**: Verified integration with `vdd-adversarial` and `vdd-multi` workflows.

#### **Improved**
* **`security-audit` (v2.1)**:
    * **Unified Scanner**: Merged `run_audit.py` to combine internal static analysis (Secrets, Dangerous Patterns) with external tool runners (`slither`, `bandit`, `npm audit`).
    * **Gold Standard Compliance**: Added "Red Flags" (Anti-Rationalization), detailed reporting standards, and mandatory "Think Like a Hacker" checklists.
    * **OWASP 2025**: Updated checks to match the latest OWASP Top 10:2025 standards (Supply Chain Security, Exceptional Conditions).
    * **Checklist Restoration**: Explicitly linked and mandated usage of `solana_security.md`, `solidity_security.md`, and `fuzzing_invariants.md`.

#### **Fixed** *(VDD Adversarial Hardening)*
* **Security References**:
    * Fixed factual inaccuracies in `flask.md` (deprecated `FLASK_ENV`, `safe_join` CVE) and `django.md` (middleware ordering) via VDD Adversarial Review.
* **`run_audit.py`**:
    * Silent `except: pass` → stderr logging + `skipped_files` counter in report.
    * Self-flagging false positives → self-exclusion via `_is_self_path()`.
    * Substring-based `SKIP_DIRS` → basename matching (`dirs[:]` pruning).
    * `run_command` now captures and reports external tool exit codes.
    * Added 120s timeout on all `subprocess.run` calls.
    * Extended `SKIP_DIRS` with `.cache`, `.idea`, `.vscode`, `vendor`, `tmp`, `coverage`.
* **`SKILL.md`**: Fixed OWASP category mappings (Secrets→A02, Deps→A06, Patterns→A03, Config→A05). Added Rationalization Table (Section 6).
* **`owasp_top_10.md`**: Resolved duplicate A10 (merged SSRF into unified A10). Merged A08 into A03.


---


### **v3.9.12 — Framework Consistency, Parallel Agents & Safety Fixes** (Feature / Bugfix)

#### **Added**
* **Parallel Agent Architecture (POC)**:
    * **New Skill: `skill-parallel-orchestration` (Tier 2)**: Protocol for decomposing tasks into parallel sub-tasks and spawning sub-agents (mock runner).
    * **Concurrent State Safety**: `update_state.py` now uses `fcntl` file locking for atomic read-modify-write on `latest.yaml`, preventing race conditions.
    * **Mock Agent Runner**: `spawn_agent_mock.py` simulates async agent execution with state updates.
    * **Documentation**: `docs/POC_PARALLEL_AGENTS.md` guide and `docs/ARCHITECTURE.md` updated with Parallel Execution Model.
* **Skill Validation Hook**:
    * **`.gemini/hooks/validate_skill_hook.sh`**: `AfterTool` hook that auto-validates skills via `validate_skill.py` on every write to `.agent/skills/`.
    * **`.gemini/settings.json`**: Hook configuration with `$GEMINI_PROJECT_DIR` fallback for cross-runner compatibility.
    * **Skill Creation Gate**: Added mandatory `init_skill.py` rule to `GEMINI.md` and `AGENTS.md` Development Phase. Manual skill creation is now prohibited.

#### **Improved**
* **VDD Skills (v1.1)**:
    * **`vdd-adversarial`**: Added **Red Flags** (Anti-Rationalization), **Rationalization Table**, and explicit `examples/` reference.
    * **`vdd-sarcastic`**: Added **Red Flags** (Anti-Rationalization), **Rationalization Table**, and explicit `examples/` reference.

#### **Fixed**
* **Data Loss Prevention**: Patched `trigger_technical.py` to abort if `docs/TASK.md` already exists, preventing accidental overwrites during product handoff.
* **Protocol Integrity**: Updated `light-02-develop-task` workflow to enforce mandatory `.AGENTS.md` updates, preventing memory drift in Light Mode.
* **Standardization**: Updated `vdd-01-start-feature` to use the authoritative `skill-archive-task` protocol instead of hardcoded manual steps.
* **Shell Injection (VDD)**: Replaced heredoc interpolation with `jq -n` in `validate_skill_hook.sh` to prevent malformed JSON from `validation_output`.
* **Invalid Mode (VDD)**: Fixed `spawn_agent_mock.py` using non-existent mode `"Wrapper"` → `"EXECUTION"`.

---



### **v3.9.11 — Hardened Pipeline & Self-Improvement System** (Feature)

#### **Added**
* **New Skill: `skill-spec-validator` (Tier 2)**:
    * **RTM Validation**: Mechanically enforces that `docs/TASK.md` contains a Requirements Traceability Matrix.
    * **Atomic Planning**: Mechanically enforces that `docs/PLAN.md` covers every RTM item with an ID-tagged task (e.g., `[R1]`).
* **New Skill: `skill-self-improvement-verificator` (Tier 3)**:
    * **Meta-Audit**: Acts as a "Guardian" for the framework itself. Audits specifications for `framework-upgrade` to prevent regression.
* **New Workflow: `/framework-upgrade`**:
    * Specialized pipeline for upgrading Prompts, Skills, and System Logic.
    * Integrates `skill-self-improvement-verificator` gates at Analysis and Planning stages.
* **Documentation**:
    * **Claude Code & Gemini CLI**: Added native integration guides (Options C & D) in READMEs.
    * **Concept Deep Dive**: Added "Blueprint vs Driver" explanation to clarify `00_agent_development.md` vs `AGENTS.md` roles.
    * **Usage Scenarios**: Added practical examples for Standard, Light Mode, and Session Restoration workflows.

#### **Improved**
* **Workflows**:
    * **`/vdd-enhanced`**: Upgraded to "Hardened Mode". Now includes `skill-spec-validator` checkpoints with auto-correction loops (Max 3 retries).
* **Agent Prompts**:
    * **Analyst**: Mandates RTM table generation (except for `[LIGHT]` tasks).
    * **Planner**: Mandates Atomic Checklists with Strict ID linking.
    * **Developer**: Enforces Strict Stub-First methodology (except for `[LIGHT]` tasks).
* **Reliability**:
    * **`skill-creator`**: now outputs mandatory cleanup instructions to prevent debris.
    * **`validate.py`**: robustness fix for parsing Markdown tables with escaped characters.

---


### **v3.9.10 — Skill Creator Cleanup & Brainstorming 2.1** (Optimization)

#### **Improved**
* **`skill-creator`**:
    * **Cleanup Protocol**: Added specific instructions to remove unused placeholder directories (`scripts/`, `assets/`, `references/`) after skill initialization.
    * **Validation**: Verified that `validate_skill.py` supports "lean" skills without empty folders.
* **`brainstorming`** (v2.1):
    * **Universal Gold Standard**: Upgraded to v2.1 with "Universal" compatibility (tool agnostic).
    * **3-Tier Assessment**: Implemented **Trivial/Medium/Complex** complexity classification with tailored protocols for each.
    * **Safety Guardrails**: Added strict "No Coding without Design" rules and Handover Templates.

---

### **v3.9.9 — Skill Resources Migration & Validation Hardening** (Optimization)

#### **Refactored**
* **Skill Standardization (Gold Standard)**:
    * **Directory Hygiene**: Migrated `resources/` folders to `assets/` (templates) and `references/` (knowledge) across all skills.
    * **Legacy Removal**: Deprecated `resources/` directory to strictly enforce Semantic Folder Structure.

#### **Fixed**
* **Validation**:
    * **Config Support**: Updated `validate_skill.py` to explicitly allow `config/` directories (restoring support for `skill-product-solution-blueprint`).
    * **CSO Violations**: Fixed description prefixes in 6 skills (`developer-guidelines`, `requirements-analysis`, etc.) to meet "Gold Standard" compliance (`Use when`, `Guidelines for`).

#### **Verified**
* **Global Audit**: Ran verification script on all migrated skills to ensure 0 broken links and 100% validation pass rate.

---

### **v3.9.8 — Meta-Skills Independence** (Refactoring)
#### **Decoupled**
* **Project-Agnostic Meta-Skills**: `skill-creator` and `skill-enhancer` are now fully portable and independent of the Antigravity project.
    * **Configurable**: Policies (Tiers, Banned Words, File Rules) are now loaded from `.agent/rules/skill_standards.yaml` instead of hardcoded Python dicts.
    * **Zero-Dependency**: Removed `PyYAML` dependency. Implemented a custom "Vanilla Python" parser (`skill_utils.py`) to ensure tools run on any environment without `pip install` or `venv`.
    * **Documentation**: Removed hardcoded references to `System/Docs/SKILLS.md` and "Gemini/Antigravity". Replaced with generic "Skill Catalog" concepts.

#### **Added**
* **New Manual**: `System/Docs/skill-writing.md` — A portable User Guide for using the meta-skills (Install, Config, Usage).
* **Resilience**: Scripts now include a **Bundled Default Config** (`skill_standards_default.yaml`) for instant drop-in usage if project config is missing.

#### **Refined**
* **Hybrid Folder Structure**: Refactored `skill-creator` and `skill-enhancer` to use a semantic folder standard:
    * `examples/` (Train): Few-shot examples for the agent.
    * `assets/` (Material): User-facing templates and output files.
    * `references/` (Knowledge): Heavy context, specs, and guidelines.
    * `scripts/` (Tools): Python automation.
    * *Deprecated `resources/` in favor of more specific `assets/` and `references/`.*

#### **Verified**
* **E2E Testing**: Validated proper functioning of dynamic tiers, parser correctness (including edge cases like inline dicts), and gap analysis on a test skill.
* **Migration**: Successfully migrated `skill-creator` and `skill-enhancer` to the new structure without data loss.

---

### **v3.9.7 — Skill Best Practices & AGI-Agnostic Hardening** (Optimization)

#### **Added**
* **Extended Best Practices Integration**:
    * **Checklist Workflows**: Added native support for the "Checklist Pattern" in `SKILL_TEMPLATE.md` and `skill_design_patterns.md`.
    * **Gerund Naming**: `init_skill.py` now advises users to use Action-Oriented naming (e.g., `processing-files`).
    * **POV Detection**: `analyze_gaps.py` now flags First/Second person POV ("I can...", "You can...") to enforce Third-Person objectivity.
    * **Anti-Patterns**: `analyze_gaps.py` now detects Windows-style paths (`back\slashes`) to ensure cross-platform compatibility.
* **Logic Hardening**:
    * **"Solve, Don't Punt"**: Explicitly banned "Try to..." language in favor of deterministic scripts.
    * **Rationalization Table**: Built-in to default templates to preemptively block agent excuses.

#### **Improved**
* **`analyze_gaps.py`**:
    * **False Positive Reduction**: Fixed regex to ignore quoted words (e.g., prohibiting "should" no longer flags the rule itself) and Markdown tables.
    * **Robust Parsing**: Enhanced Windows path detection to handle mixed text/code contexts.
* **`skill-creator`**:
    * **Self-Sufficiency**: Added `skill_design_patterns.md` resource to decouple the skill from external docs.
    * **TDD Integration**: Evaluation-Driven Development is now a core pattern.

#### **Verified**
* **VDD Round 3**: Created an adversarial `bad-skill-helper` with intentional violations. The system successfully detected and flagged all anti-patterns (Vague Name, POV, Windows Paths).

---

### **v3.9.7 — Iterative Design & VDD Robustness** (Feature)

#### **Added**
* **New Workflow: `/iterative-design`**:
    * **Concept Loop**: brain storm -> Spec Draft -> VDD Audit -> Human Review -> Refinement.
    * **Human-in-the-Loop**: Explicit checkpoints for user feedback before coding.
* **New Skill: `brainstorming` (Tier 2)**:
    * **Pre-Planning**: Specialized instructions for research and idea generation.
    * **Anti-Hallucination**: Strict "NO CODING" rules during brainstorming phase.

#### **Fixed**
* **VDD Artifact Consistency**:
    * **Logic Gap Closed**: Fixed issue where `iterative-design` requested a report but `vdd-adversarial` had no template.
    * **Templates**: Added `resources/template_critique.md` to `skill-vdd-adversarial` for standardized auditing.
    * **Rich Skill**: Refactored `vdd-adversarial` to meet `skill-enhancer` standards (Resources separation).

---

### **v3.9.6 — Evolved TDD & Strict Reliability** (Feature)

#### **Added**
* **New Skill: `tdd-strict` (Tier 3)**:
    * **High Assurance Mode**: Enforces "Mechanical Verification" (Failing test MUST match `EXPECTED_FAIL_REASON`).
    * **Law of Minimalism**: Explicitly bans speculative coding and dead code.
    * **Self-Contained**: Can be loaded independently of Tier 1 skills.
* **Bug Fixing Protocol (Universal)**:
    * Added to `developer-guidelines` (Section 6).
    * Mandates "Reproduce First" rule for ALL bug fixes (Tier 1).

#### **Improved**
* **Checklists**:
    * **`code-review-checklist`**: Added "High Assurance" section for verifying strict TDD compliance.
    * **`plan-review-checklist`**: Added check for planning Strict Mode usage.
* **Workflows**:
    * Updated `/full-robust` pipeline to automatically load `tdd-strict` for maximum reliability.
* **Documentation**:
    * Updated `System/Docs/SKILLS.md` with Tier 3 definitions.
    * Updated `System/Docs/WORKFLOWS.md` to reflect strict integration.

---

### **v3.9.5 — Skill Hardening & Gold Standard Refactoring** (Optimization)

#### **Refactored (Gold Standard)**
* **`documentation-standards`**:
    * **Token Optimization**: Extracted inline templates to `resources/templates/` (60%+ reduction).
    * **Richness**: Added `examples/good_documentation.py` (Gold Standard example).
    * **Resilience**: Added "Red Flags" and "Rationalization Table".
* **`skill-planning-format`**:
    * **Token Optimization**: Extracted massive templates (`PLAN.md`, `TASK.md`) to `resources/templates/`.
    * **Richness**: Added `examples/PLAN_EXAMPLE.md` and `examples/TASK_EXAMPLE.md`.
* **`skill-task-model`**:
    * **Richness**: Extracted inline Use Case examples (Good/Bad) to `examples/`.
    * **Resilience**: Added "Red Flags" and "Rationalization Table".

#### **Fixed**
* **`light-mode`**: Fixed YAML syntax error (`[LIGHT]` tag unquoted) and CSO violation in description.
* **`skill-safe-commands`**: Updated documentation to allow `AGENTS.md` configuration.

#### **Improved**
* **System Resilience**:
    * **No-Dependency Parsing**: Removed `PyYAML` dependency from `validate_skill.py` and `analyze_gaps.py`.
    * **Robust Parsing**: Implemented manual YAML parser handling quotes, lists, and comments gracefully.
* **CSO Schemas**: Updated `skill-creator` and `skill-enhancer` to allow richer description prefixes: `Use when`, `Guidelines for`, `Standards for`, `Defines`, `Helps with`.

---

### **v3.9.4 — Product Skills Deepening & Refactoring** (Optimization)

#### **Refactored**
* **Strategic Analyst (`p01`):**
    * Refactored Prompt: Removed inline template, added `Execution Loop` with Deconstruct/Timing/Moat steps.
    * Updated Skill `skill-product-strategic-analysis`:
        * Added `market_strategy_template.md` (Core Thesis, Moat Score, Risks).
        * Added Example `01_strong_ai_assistant.md` (Strong Go).
        * Added Example `02_nogo_vertical_video.md` (No-Go).
* **Product Analyst (`p02`):**
    * Refactored Prompt: Added `User Refinements` input, delegated Vision generation to Skill.
    * Updated Skill `skill-product-analysis`:
        * Updated `vision_template.md` (Core Pillars, Moat Score, Emotional Logic).
        * Added rigorous examples: `01_strong_go_devboost`, `02_consider_talentflow`, `03_nogo_quickbites`.
* **Solution Architect (`p04`):**
    * Refactored Prompt: Removed duplicated template.
    * Updated Skill `skill-product-solution-blueprint`:
        * Updated `solution_blueprint_template.md` (Unit Economics, Verdict).
        * Updated `calculate_roi.py` to output ARPU, CAC, LTV/CAC.
        * Added examples: `01_simple_flexarb` and `02_advanced_loyaltyhub`.
* **Director (`p03`):**
    * Refactored Prompt: Integrated `skill-product-backlog-prioritization`.
    * Added Step 3: Auto-Prioritization (WSJF) before sign-off.
    * Added Step 4: Auto-Hash generation via `sign_off.py`.

#### **Improved**
* **Consistency:** All Product Agents (`p01`, `p02`, `p04`) now use a unified "Prompt → Skill → External Template" architecture.
* **Scoring:** Implemented quantitative scoring (10-factor matrix) and "Verdict" logic across all product artifacts.

---

### **v3.9.3 — Documentation Hygiene & JSON Enforcement** (Maintenance)

#### **Changed**
* **Documentation Standardization:**
    * **JSON Enforcement:** Updated `skill-product-solution-blueprint` to strictly enforce `.json` for `calculate_roi.py` inputs (removed ambiguous YAML references).
    * **Path Hygiene:** Standardized temporary artifact location to `docs/product/` (e.g., `docs/product/stories.json`).
* **Resource Structure:**
    * Flattened template structure in `skill-product-solution-blueprint` (moved `resources/templates/` -> `resources/`).
    * Updated `SKILL.md` to reference the canonical `solution_blueprint_template.md`.

---

### **v3.9.2 — Product Skills Refactoring & Math Hardening** (Optimization)

#### **Added**
* **Advanced Financials:** `calculate_roi.py` now supports:
    * **Granular Sizing:** T-Shirt sizes (XS-XXL) mapped to hours via `sizing_config.json`.
    * **LLM Acceleration:** "Friendliness" score discounting based on global factors.
    * **Metrics:** NPV (3yr), LTV, CAC, and Payback estimations.
* **Product Scoring:** New `score_product.py` implementing 10-Factor Matrix (Problem Intensity, Moat, etc.).
* **Documentation:**
    * `System/Docs/PRODUCT_CALCULATIONS_MANUAL.md`: Detailed "Magic Math" FAQ.
    * Updated `System/Docs/PRODUCT_DEVELOPMENT.md` with Calculation Manual reference.

#### **Optimized**
* **Prioritization:** `calculate_wsjf.py` now natively supports T-Shirt sizes (S, M, L) mapped to Fibonacci.
* **Security (VDD):**
    * Hardened `calculate_roi.py` against "Time Travel" bugs (negative duration).
    * Clamped `score_product.py` inputs (1-10) to prevent overflow.
    * Removed `PyYAML` dependency for lighter execution.

---

### **v3.9.1 — Documentation Sync & Cleanup** (Maintenance)

#### **Optimized**
* **Documentation Synchronization:**
    * Updated `README.md` and `README.ru.md` to fully reflect Product Development capabilities (Agents, Workflows, Artifacts).
    * Refactored `00_agent_development.md` description to "Meta-System Prompt".
* **Standards Enforcement (O6a):**
    * Updated `System/Docs/SKILLS.md` and `SKILL_TIERS.md` to strictly enforce "Script-First" and "Example Separation" patterns.
    * Removed legacy references to `Backlog/agentic_development_optimisations.md`.
* **Cleanup:**
    * Archived `Backlog/agentic_development_optimisations.md` as all optimization milestones (O1-O7) are complete and documented in System Docs.

---

### **v3.9.0 — Product Discovery & Handoff** (Feature)

#### **Added**
* **Completed Product Phase:** Full "Venture Builder" pipeline with 5 new agents (`p00`-`p04`).
    * **Strategy:** `skill-product-strategic-analysis` (TAM/SAM/SOM).
    * **Vision:** `skill-product-analysis` (Crossing the Chasm).
    * **Solution:** `skill-product-solution-blueprint` (ROI, Risk, Text-UX).
* **Quality Gate (VDD):**
    * **Adversarial Director (`p03`):** Blocks handoff if "Moat" is weak.
    * **Cryptographic Handoff:** `sign_off.py` -> `verify_gate.py` chain ensures only approved backlogs reach developers.
* **Workflows:**
    * `/product-full-discovery`: End-to-end Venture Building.
    * `/product-quick-vision`: For internal tools.
    * `/product-market-only`: For rapid idea validation.
* **Documentation:**
    * `System/Docs/PRODUCT_DEVELOPMENT.md`: Comprehensive playbook.
    * `System/Docs/WORKFLOWS.md`: Updated with Product workflows.

---

### **v3.8.0 — Phase 0: Product Bootstrap** (Feature)

#### **Added**
* **Product Management Module:**
    * **New Skills:** `skill-product-analysis` (Vision) and `skill-product-backlog-prioritization` (WSJF).
    * **New Agents:** `p01_product_analyst` (Creator) and `p02_product_reviewer` (VDD Critic).
    * **New Documentation:** [`System/Docs/PRODUCT_DEVELOPMENT.md`](System/Docs/PRODUCT_DEVELOPMENT.md) with usage scenarios.
* **Native Tool Integration:**
    * **Product Tools:** `init_product` and `calculate_wsjf` registered in `schemas.py`.
    * **Tool Runner:** Updated `System/scripts/tool_runner.py` to dispatch these tools via native subprocess calls.
    * **Scripts Root:** Moved scripts from `scripts/` to `System/scripts/` to align with framework standards.

#### **Changed**
* **Documentation:**
    * Updated `ORCHESTRATOR.md` with new supported tools.
    * Updated `SKILLS.md` with Product Management section.
    * Updated `SKILL_TIERS.md` with new Tier 2 skills.

---

### **v3.7.2 — O7: Session Context Persistence** (Optimization)

#### **Added**
* **New Skill: `skill-session-state`**: TIER 0 capability to persist/restore session context.
    * **Script-First**: `update_state.py` handles atomic YAML updates.
    * **Protocol**: Defines Boot (Read) and Boundary (Write) triggers.
* **Boot Protocol**: Updated `GEMINI.md` and `AGENTS.md` to restore state from `.agent/sessions/latest.yaml` on session start.
* **Agent Updates**: All 10 Agent Prompts updated to include `skill-session-state` in TIER 0 list.


### **v3.7.1 — Light Mode** (Feature)

#### **Added**
* **Light Mode:** New fast-track workflow for trivial tasks (typos, UI tweaks, simple bugfixes).
    * Skips Architecture and Planning phases (~50% token savings).
    * Workflows: `light-01-start-feature.md`, `light-02-develop-task.md`.
    * Skill: `light-mode` (Tier 2) with escalation protocol and security sanity checks.
    * Updated `GEMINI.md`, `AGENTS.md`, `WORKFLOWS.md`, `SKILLS.md`.

---

### **v3.7.0 — Skills Refactoring & Security Hardening** (Optimization)

#### **Added**
* **Security Automation:** Added `run_audit.py` to `security-audit` skill. Auto-detects project type (Solidity/Rust/Python/JS) and runs relevant tools (`slither`, `bandit`, `cargo audit`).
* **High-Grade Checklists:**
    * `solidity_security.md`: DeFi patterns, Flash Loans, Upgradability.
    * `solana_security.md`: Anchor validation, PDAs, Arithmetic.
* **Architecture Patterns:** Added `clean_architecture.md` and `event_driven.md` to `architecture-design` resources.
* **LLM Security:** Added Prompt Injection, Jailbreaking, and System Prompt Leakage checks to `skill-adversarial-security`.

#### **Optimized**
* **Skills Refactoring (O6):**
    * **Example Separation:** Extracted inline templates from `requirements-analysis`, `testing-best-practices` to `resources/`.
    * **Script-First:** Replaced manual instructions with script mandates.
    * **Sarcastic Persona:** Extracted prompt examples to `resources/prompts/sarcastic.md`.
* **Documentation:** Updated `System/Docs/SKILLS.md` to mandate V2 standards (Script-First, Example-Separation).

#### **Verified**
* **Global Validation:** All 6 refactored skills passed `validate_skill.py`.
* **Safety:** TIER 0 skills (`core-principles`) verified intact.

---

### **v3.6.5 — Configuration Standardization** (Refactoring)

#### **Changed**
* **Project Structure:**
    * Moved `.gemini/GEMINI.md` to `./GEMINI.md` (Project Root).
    * Renamed `.cursorrules` to `AGENTS.md` (Project Root) for clarity.
* **Documentation:** Updated `README.md`, `README.ru.md` and `docs/ARCHITECTURE.md` to reflect the new configuration structure.

---

### **v3.6.4 — O7 Prep & System Manifesto** (Documentation)

#### **Optimized**
* **System Manifesto (O11):** Rewritten `System/Agents/00_agent_development.md` to be the single source of truth for v3.6+ architecture.
    * Aligned with O1 (Skill Tiers) and O2 (Orchestrator Patterns).
    * Added section on **Agentic Mode** and `task_boundary` usage.
    * Included `10. Security Auditor` role.
* **O7 Specification:** Refined Session Context Management optimization.
    * Added alignment with `task_boundary` tool.
    * Added "Start Prompt" for O7 implementation.
* **README:** Updated Installation section to explicitly mention `.gemini/` folder copy.

---

### **v3.6.3 — O6a: Skill Structure Optimization** (Optimization)

#### **Changed**
* **Large Skills Refactoring:** Transformed 4 "heavy" skills (>4KB) to use `scripts/` + `examples/` pattern:
    * `architecture-format-extended`: Extracted inline templates to `examples/` (-65% size).
    * `skill-reverse-engineering`: Replaced NL traversal valid with `scan_structure.py` (-64% size).
    * `skill-update-memory`: Replaced NL git logic with `suggest_updates.py` (-63% size).
    * `skill-phase-context`: Removed redundant ASCII art layers (-49% size).

#### **Added**
* **Automation Scripts**: Added python automation for deterministic skill execution.
* **Infographic Update**: Added *Model Impact Analysis* and *References* to [O6_OPTIMIZATION_INFOGRAPHIC.md](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md).

### **v3.6.2 — Skill Creator & Automation** (Feature)

#### **Added**
* **New Skill: `skill-creator`**: Meta-skill for creating new skills containing Anthropic standards + Project Tiers (verified structure).
    *   **Automation:** Includes `scripts/init_skill.py` for compliant scaffolding.
    *   **Validation:** Includes `scripts/validate_skill.py` for ensuring frontmatter and strict folder hygiene.

---

---

### **v3.6.1 — O6: Logic Integrity & Documentation Polish** (Post-Release Fix)

#### **Fixed**
* **Orchestrator Logic Integrity:** Restored missing stages 11-14 (Review/Fix cycle) and Workflows section in `01_orchestrator.md` to guarantee 100% logic parity with v3.2.
* **Documentation:** Consolidated `CHANGELOG.md` entry for v3.6.0 logic clarity.

#### **Updated**
* **Infographics:** Updated [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) and [O6 Optimization Infographic](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md) with final v3.6.1 verification stats (-20% Orchestrator compression vs -36% initial estimate).

---

### **v3.6.0 — O5: Skill Tiers & O6: Standardization (Optimization)** (Stability)

#### **Added**
* **O6 Standard:** All 10 Agent Prompts (`01`–`10`) now use a unified 4-section schema with mandatory TIER 0 skills validation.
    * **New Names:** Standardized filenames to `_prompt.md`.
* **O5 Skill Tiers:** New document `System/Docs/SKILL_TIERS.md` — authoritative source for loading rules (TIER 0, 1, 2).

#### **Changed**
* **Skills Metadata:** All 28 skills now explicitly declare `tier: [0|1|2]`.
* **Agent Efficiency (O6):**
    * `04 Architect`: **-29%** tokens.
    * `06 Planner`: **-33%** tokens.
    * `08 Developer`: **-31%** tokens.
    * `01 Orchestrator`: **-20%** tokens (adjusted for guaranteed logic retention).
* **Safety (O6):**
    * Reviewers (`07`, `09`) and Auditor (`10`) now strictly enforce TIER 0 safety skills (+43% size for zero hallucinations).

#### **Verified**
* **VDD Audit:** All 10 standardized agents passed Logic Retention checks against v3.2 backups.
* **Localization:** All Russian prompts synchronized.

---


### **v3.5.5 — O2: Orchestrator Compression (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-orchestrator-patterns`**: Stage Cycle pattern and dispatch table for Orchestrator.
    * Reusable Init → Review → Revision flow pattern.
    * Stage Dispatch Table with agents, reviewers, and iteration limits.
    * Decision logic tables for common branching.
    * Expected result schemas for all agent types.
    * Exception documentation (Completion, Blocking).

#### **Changed**
* **`01_orchestrator.md`**: Compressed from 492 lines to 170 lines using patterns + dispatch table.
* **`Translations/RU/Agents/01_orchestrator.md`**: Updated with same compression logic.
* **`System/Docs/SKILLS.md`**: Added `skill-orchestrator-patterns` entry.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| File size | 11,195 bytes | 4,522 bytes | **-60%** |
| Lines | 492 | 170 | **-65%** |
| Tokens (~) | ~2,799 | ~1,130 | **-60%** |

> **Note:** All 14 scenarios preserved. Backup at `01_orchestrator_full.md.bak`.
>
> 📊 **See:** [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) for a visual breakdown of savings.

---

### **v3.5.4 — O1: Skill Phase Context (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-phase-context`**: Skill loading tiers protocol for optimized token consumption.
    * **TIER 0** (Always Load): `core-principles`, `skill-safe-commands`, `artifact-management` (~2,082 tokens).
    * **TIER 1** (Phase-Triggered): Phase→Skills mapping table for on-demand loading.
    * **TIER 2** (Extended): Specialized skills loaded only when explicitly requested.
    * Loading rules and flow diagram for agent reference.

#### **Changed**
* **`.gemini/GEMINI.md`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`.cursorrules`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`System/Docs/SKILLS.md`**: Added `skill-phase-context` entry in Core & Process section.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Baseline session load | ~9,772 tokens | ~2,082 tokens | **-79%** |
| TIER 1 skills | All loaded upfront | On-demand per phase | -3,000 to -5,000 tokens |

> **Note:** Automation (safe-commands) preserved — `mv`, `git`, tests still auto-run.

---

### **v3.5.3 — O3: architecture-format Split (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `architecture-format-core`**: Minimal template for architecture documents (~150 lines, TIER 1).
    * Core sections: Task Description, Functional Architecture, System Architecture, Data Model (conceptual), Open Questions.
    * Default skill for most architecture updates.
    * Loading conditions table for decision-making.
* **New Skill: `architecture-format-extended`**: Full templates with examples (~400 lines, TIER 2).
    * Complete sections 3-10 with JSON samples, diagrams, and detailed templates.
    * Loaded only for: new systems, major refactors, complex requirements.
    * Cross-reference to core skill.

#### **Changed**
* **`04_architect_prompt.md`**: Updated with conditional loading table for core/extended skills.
* **`Translations/RU/Agents/04_architect_prompt.md`**: Updated with same conditional loading logic.
* **`System/Docs/SKILLS.md`**: Replaced single `architecture-format` entry with two tier-based entries.

#### **Token Savings**
| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Minor architecture update | ~2,535 | ~996 | **-60%** |
| New system / major refactor | ~2,535 | ~3,357 | +32% (more examples) |

---

### **v3.5.2 — Scripts Consolidation & Installation Simplification** (Refactoring)

#### **Changed**
* **Moved `scripts/` → `System/scripts/`**: Tool Dispatcher is now part of System folder.
    * **Installation simplified**: Only 2 folders to copy (`System/` + `.agent/`) instead of 3.
    * **Clear separation**: Framework files (`System/`) vs project files.

#### **Updated**
* **README.md / README.ru.md**: Simplified installation instructions and directory structure diagrams.
* **System/Docs/ORCHESTRATOR.md**: All import paths updated to `System.scripts.tool_runner`.
* **tests/test_tool_runner.py**: Updated import path.

---

### **v3.5.1 — Protocol Conflict Resolution & IDE-Agnostic Fixes** (Framework Bugfix)

#### **Fixed**
* **`skill-archive-task`**: Removed strict dependency on `generate_task_archive_filename` tool. Added manual fallback for filename generation using shell commands.
* **`skill-archive-task`**: Replaced hardcoded example IDs (`032`, `033`) with generic placeholders (`{OLD_ID}`, `{NEW_ID}`) to prevent agent confusion.
* **`artifact-management`**: Removed hardcoded absolute path in skill reference. Fixed outdated tool reference.
* **`artifact-management`**: Added "Dual State Tracking" section to resolve conflict between Agentic Mode internal `task.md` and project `docs/TASK.md`.
* **`core-principles`**: Added IDE-agnostic "Bootstrap Protocol" (Section 0) instructing agents that `<user_rules>` injected by IDE **override** internal defaults.

#### **Root Causes Addressed**
| Issue | Solution |
|-------|----------|
| Context Blindness | Bootstrap Protocol now clarifies priority |
| Internal vs Project `task.md` | Dual State Tracking section added |
| Missing Tool Blocker | Manual fallback in skill-archive-task |
| Hardcoded Examples | Replaced with `{PLACEHOLDER}` syntax |

---

### **v3.5.0 — Memory Automation** (Task 035)


#### **Added**
* **New Skill: `skill-update-memory`**: Auto-update `.AGENTS.md` files based on code changes.
    * Analyzes `git diff --staged` to detect new, modified, and deleted files.
    * Strict filtering: ignores `*.lock`, `dist/`, `migrations/`, config files.
    * Human knowledge preservation: protects `[Human Knowledge]` sections.
    * Integration points: `09_agent_code_reviewer`, `04-update-docs`.
* **New Skill: `skill-reverse-engineering`**: Regenerate architecture documentation from codebase analysis.
    * Iterative strategy: folder-by-folder analysis → local summaries → global synthesis.
    * Updates `ARCHITECTURE.md` and discovers hidden knowledge for `KNOWN_ISSUES.md`.
    * Context overflow mitigation: never loads entire codebase at once.

#### **Documentation**
* Updated `System/Docs/SKILLS.md` with new skills in Core & Process section.
* Updated roadmap in `Backlog/potential_improvements-2.md`.

#### **Integration**
* `09_agent_code_reviewer.md`: Added `skill-update-memory` to verify `.AGENTS.md` updates.
* `04-update-docs.md` workflow: Added references to both skills for structured docs maintenance.
* `README.md` / `README.ru.md`: Updated "Reverse Engineering" section with skill-based prompts.

---

### **v3.4.2 — Framework Documentation Consistency Fixes** (Task 034 Phase 3)

#### **Fixed**
* **Broken References**: Identified and fixed stale references to moved files (`System/Docs/` vs `docs/`) in `README.md`, `.cursorrules`, and agent prompts.
* **Path Error**: Fixed incorrect path in `Translations/RU/Agents/01_orchestrator.md` (`docs/ORCHESTRATOR.md`) to align with user project structure.
* **Typos**: Corrected formatting errors in Russian Orchestrator prompt.

#### **Improved**
* **Installation Instructions**: Clarified `README.md` and `README.ru.md` to explicitly instruct users to copy `System/Docs/ORCHESTRATOR.md` to their local `docs/` folder, preventing path conflicts for distributed agents.

---

### **v3.4.1 — Workflow Integrity & Artifact Fixes** (Task 034 Phase 2)

#### **Fixed**
* **Workflow "Phantom" References**: Fixed critical bugs in `base-stub-first.md` (and consequently `vdd-enhanced`) which referenced non-existent workflows (`/analyst-task`, etc.) instead of valid ones. This restored the mandatory Analysis/Architecture phases.
* **VDD Adversarial Loop**: Corrected `vdd-adversarial.md` to use valid workflow calls (`/03-develop-single-task`) instead of non-existent actions (`/developer-fix`).
* **Artifact Consistency**: Created missing `docs/KNOWN_ISSUES.md` placeholder to satisfy workflow requirements.
* **Security Audit**: Clarified `security-audit.md` instructions regarding `.AGENTS.md` updates to handle missing files gracefully.

#### **Verified**
* Performed a full audit of all 14 workflow definitions to ensure every cross-reference points to an existing file.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Added**
* **New Skill: `skill-adversarial-security`**: OWASP security critic in adversarial/sarcastic style.
    * Injection attacks (SQLi, XSS, Command Injection, Path Traversal).
    * Authentication & Authorization flaws.
    * Secrets exposure (hardcoded keys, passwords, API tokens).
    * Input validation failures.
* **New Skill: `skill-adversarial-performance`**: Performance critic in adversarial/sarcastic style.
    * N+1 queries, missing indexes.
    * Memory leaks, unbounded allocations.
    * Blocking operations in async code.
    * Algorithm complexity issues.
* **New Workflow: `/vdd-multi`**: Sequential execution of multiple specialized adversarial critics.
    * Phase 1: General logic review (`skill-vdd-adversarial`).
    * Phase 2: Security review (`skill-adversarial-security`).
    * Phase 3: Performance review (`skill-adversarial-performance`).

#### **Documentation**
* Updated `docs/SKILLS.md` with new VDD skills.
* Updated `Backlog/potential_improvements-2.md` with v3.4 status.

---

### **v3.3.2 — Auto-Tests for Archiving Protocol** (Task 033 Phase 2)

#### **Added**
* **Archive Protocol Tests**: 15 new automated tests for the 8 archiving scenarios using VDD adversarial approach:
    * Core scenarios: new task with existing TASK.md, no TASK.md, refinement, ID conflict.
    * VDD adversarial: missing Meta Information, malformed Task ID, permission denied, tool error simulation.
* **Testable Protocol Module**: `archive_protocol.py` — Python implementation of the 6-step archiving protocol for unit testing.
* **Test Fixtures**: 3 TASK.md variants (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Verification**
* 44 total tests pass (29 existing + 15 new).
* Run: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Portability, VDD Audit & UX Improvements** (Task 033)

#### **Fixed**
* **Circular Logic in Safe Commands**: Eliminated the documentation loop. Added explicit copy-paste list to `skill-safe-commands` for IDE configuration.
* **Agent Hallucinations**: Corrected `01_orchestrator.md` references to non-existent tools (`git_ops` -> `git_status`, etc.) revealed by VDD Audit.
* **IDE Configuration**: Fixed documentation for "Allow List" to address `mv` command token matching issues.
* **Portability**: Made `docs/ORCHESTRATOR.md` reference optional (`if available`) to prevent errors in lightweight projects or when transferring agents.

#### **Refactored**
* **Mandatory Skill Pattern**: Enforced `skill-safe-commands (Mandatory)` across all agents to ensure native tool safety.
* **Developer Guidelines**: Introduced explicit "Tooling Protocol" enforcing `native tools` (like `run_tests`) over shell commands.

### **v3.3.0 — Skill Encapsulation & Safe Commands Centralization** (Task 033)

#### **Added**
* **New Skill: `skill-archive-task`**: Complete, self-contained protocol for archiving `docs/TASK.md`. Single source of truth for archiving logic, eliminating duplication across 7+ files.
    * 6-step archiving protocol with decision logic (new vs refinement).
    * Error handling for missing Meta Information.
    * Validation and rollback guidance.
* **New Skill: `skill-safe-commands`**: Centralized list of commands safe for auto-execution without user approval.
    * 7 command categories: read-only, file info, git read, archiving, directory ops, tool calls, testing.
    * Pattern matching rules for IDE integration.
    * IDE-specific instructions (Antigravity/Gemini, Cursor).

#### **Refactored**
* **Duplication Eliminated**: Reduced archiving protocol duplication from 7 files to 1:
    * `.gemini/GEMINI.md` → skill reference
    * `.cursorrules` → skill reference
    * `System/Agents/02_analyst_prompt.md` → skill reference
    * `System/Agents/01_orchestrator.md` → skill reference
    * `System/Agents/00_agent_development.md` → skill reference (30 lines → 14)
    * `.agent/skills/artifact-management/SKILL.md` → skill import
    * `.agent/workflows/01-start-feature.md` → skill reference
* **Safe Commands Centralized**: All 4 files with duplicate Safe Commands now reference `skill-safe-commands`.

#### **Documentation**
* Updated `docs/SKILLS.md` with new skills.
* Added Implementation Summary to `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Task Archive ID Tool & Auto-Run Protocol**

#### **Added**
* **New Tool: `generate_task_archive_filename`**: Deterministic tool for generating unique sequential IDs when archiving tasks. Eliminates manual ID assignment errors and ID gaps.
    * Auto-generates next available ID (`max + 1` strategy).
    * Validates proposed IDs and handles conflicts (`allow_correction` flag).
    * Normalizes slugs (lowercase, dashes).
    * Future-proofed: supports IDs beyond 999 (regex `\d{3,}`).
* **Dispatcher Integration**: Tool registered in `scripts/tool_runner.py` for native execution.
* **Unit Tests**: 29 comprehensive tests covering all use cases.

#### **Improved**
* **Safe Commands Protocol**: Expanded list of auto-run commands in `skill-artifact-management` and Orchestrator prompt:
    * Read-only: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git read: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Archiving: `mv docs/TASK.md docs/tasks/...`
    * Tools: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Agent Prompts**: Updated Orchestrator (`01`) and Analyst (`02`) with explicit tool usage for archiving.

#### **Documentation**
* Updated `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, and `docs/SKILLS.md`.
* Added Python installation requirements to README.
* Consolidated `docs/USER_TOOLS_GUIDE.md` into `docs/ORCHESTRATOR.md` (removed duplicate file).
* Synchronized `.gemini/GEMINI.md` and `.cursorrules` with v3.2.5+ protocol.

---

### **v3.2.4 — Workflow Documentation Enhancement**

#### **Added**
* **Workflow Call Sequences**: Added comprehensive "Getting Started" section to `docs/WORKFLOWS.md` with:
    * One-Step vs Multi-Step approach comparison table.
    * TDD pipeline examples (`base-stub-first`, `01`→`02`→`03/05`→`04`) with pros/cons.
    * VDD pipeline examples (`vdd-enhanced`, `full-robust`, VDD atomic steps) with pros/cons.
    * Decision flowchart (Mermaid diagram) for choosing the right approach.
    * Quick reference summary table for common scenarios.

---

### **v3.2.3 — Archiving Protocol Refinement**

#### **Changed**
* **Archiving Scope**: Removed mandatory archiving of `docs/PLAN.md`. Only `docs/TASK.md` requires archiving before new tasks.
* **Documentation**: Updated version references in `README.md` (v3.1→v3.2) and `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Improved**
* **Auto-Run Protocol**: Added explicit `SAFE TO AUTO-RUN` instruction to Analyst prompt and `skill-artifact-management`. The archive command for `docs/TASK.md` no longer requires user approval.

---

### **v3.2.2 — System Integrity & Archiving Protocols**

#### **Fixed**
* **Critical Restoration**: Restored missing (empty) Russian agent prompts (`Translations/RU/Agents/01, 02, 04, 06`) using v3.2.0 logic.
* **Data Loss Prevention**: Fixed a critical gap in `skill-artifact-management` where the "Archiving Protocol" was missing.
* **Protocol Enforcement**: Updated Orchestrator (`01`), Analyst (`02`), and Planner (`06`) to strictly enforce archiving of `docs/TASK.md` and `docs/PLAN.md` before overwriting.

#### **Improved**
* **System Prompts**: Synchronized `.gemini/GEMINI.md` and `.cursorrules` with the Tool Execution Protocol (v3.2.0), explicitly enabling native tool calling.
* **Consistency**: Completed a full audit of the prompt system to ensure zero contradictions between System and Agent prompts.

---

### **v3.2.1 — Skills System Optimization**

#### **Added**
* **Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
* **Rules**: Added `.agent/rules/localization-sync.md` to enforce bilingual documentation updates.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Localization**: Synced `README.ru.md` with English version (added Tool Calling section).
* **Russian Agents**: Updated `Translations/RU/Agents/*.md` to match v3.2.0 optimizations (Tool Calling logic, Skills extraction, Path Hygiene).

---

### **v3.2.0 — Structured Tool Calling & Path Hygiene**

#### **Added**
* **Tool Execution Subsystem**: The Orchestrator now natively supports structured tool calling (Function Calling).
* **New Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
    * `skill-architecture-format`: Consolidated architecture document templates.
* **Standard Tools**: Added `run_tests`, `git_ops`, `file_ops` to `.agent/tools/schemas.py`.
* **Documentation**: Added `docs/ORCHESTRATOR.md`.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Maintenance**: Centralized critical document templates (TASK, PLAN, Architecture) in `.agent/skills/` to ensure consistency and easier updates.
* **Workflows**: Refactored `03-develop-task` -> `03-develop-single-task` and updated `base-stub-first`.

#### **Changed**
* **Test Reports**: Standardized storage location. Reports moved from `docs/test_reports` to `tests/tests-{Task ID}/`.
* **Path Enforcement**: Updated all Agent prompts to use strictly project-relative path examples.
* **Agents**: Updated Orchestrator, Developer, and Reviewers to enforce new protocols.

#### **Fixed**
* **Cleanup**: Removed legacy `docs/test_reports` directory.

---

### **v3.1.3 — Skills Cleanup & Cursor Integration Fix**

#### **Changed**
* **Project Structure**: Removed redundant `.cursor/skills` directory to eliminate duplication.
* **Cursor Integration**: Updated `README.md` to instruct users to simply symlink `.cursor/skills` -> `.agent/skills`, ensuring a single source of truth.
* **Orchestrator**: Updated `.cursorrules` to reference the correct symlinked path and fixed legacy "tz" terminology in comments.
* **Workflows**: Archived `docs/TASK.md` to `docs/tasks/task-014-cleanup-skills.md`.

---

### **v3.1.2 — Analyst Protocol & YAML Fixes**

#### **Fixed**
* **Skills**: Fixed YAML syntax error in `core-principles` skill (quoted description).

#### **Improved**
* **Analyst Agent**: Added "CRITICAL PRE-FLIGHT CHECKLIST" to `02_analyst_prompt.md` to strictly enforce:
    * Archiving of existing `docs/TASK.md` before starting new work.
    * Mandatory inclusion of Section 0 (Meta Information: Task ID, Slug).
* **Skills**: Updated `skill-requirements-analysis` to mark Meta Information as **MANDATORY**.
* **Documentation**: Enforced "Relative Paths Only" rule for Artifacts in `skill-documentation-standards` and `06_agent_planner.md`.

#### **Refactored**
* **Skills**: Audited and fixed YAML frontmatter in `code-review-checklist`, `developer-guidelines`, `security-audit` and `artifact-management`.
* **PLAN.md**: Converted absolute paths to relative paths.

---

### **v3.1.1 — Plan & Structure Fixes**

#### **Fixed**
* **Agent Prompts**: Corrected `plan.md` file path references to `docs/PLAN.md` in Planner and Reviewer agents (both English and Russian versions).
* **Agent Prompts**: Corrected `open_questions.md` file path references to `docs/open_questions.md` in Planner agent.
* **Project Structure**: Removed the `verification/` directory to comply with `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Global "TZ" to "TASK" Refactor**

#### **Changed**
* **Terminology**: Global refactoring of "TZ" (Техническое Задание) to "TASK" (Task/Specification) to improve internationalization and consistency.
* **Артефакты**: Переименован `docs/TZ.md` в `docs/TASK.md`.
* **Системные Агенты**: Обновлены все промпты агентов (Analyst, Reviewer, Architect и др.) для использования терминологии "TASK".
* **Навыки**: Переименован `skill-tz-review-checklist` в `skill-task-review-checklist`.
* **Документация**: Обновлены `README.ru.md`, `WORKFLOWS.md`, `SKILLS.md` и `.gemini/GEMINI.md` для соответствия новому стандарту.

#### **Исправлено**
* **Согласованность**: Устранено смешанное использование "ТЗ" и "Task Specification" во всем фреймворке.
* **Сценарии (Workflows)**: Исправлена критическая ошибка в `01-start-feature` и `vdd-01-start-feature`, из-за которой старое ТЗ перезаписывалось без архивации. Добавлен явный шаг архивирования.

#### **Инструкция по миграции**
Для обновления с v3.0.x до v3.1.0:
1. **Переименование**: `mv docs/TZ.md docs/TASK.md`
2. **Обновление Агентов**: Замените `System/Agents/` на новую версию (Важно: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Обновление Навыков**: Замените `.agent/skills/` на новую версию.

---

### **v3.0.3 — Синхронизация документации и артефакты**

#### **Исправлено**
* **Документация**: Заменены устаревшие ссылки на `UNKNOWN.md` на `docs/open_questions.md` в `README.md` и `README.ru.md` для соответствия реальным промптам Агентов.

#### **Добавлено**
* **Артефакты**: Добавлен отсутствующий шаблон `docs/open_questions.md` для отслеживания нерешенных вопросов.

---

### **v3.0.2 — Примеры и Доработка Документации**
  
#### **Добавлено**
* **Примеры (Examples)**:
    * `examples/skill-testing/test_skill.py`: Python скрипт для изолированного тестирования навыков.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow с подсказками (Sticky Notes) для проверки промптов.
* **Документация (Skills)**:
    * В `docs/SKILLS.md` добавлены разделы "Dynamc Loading", "Isolated Testing" и "Best Practices".
    * Добавлены прямые ссылки на файлы примеров.

---

### **v3.0.1 — Улучшение Системы Навыков**

#### **Улучшено**
* **Документация Навыков**:
    * Расширен `docs/SKILLS.md`: добавлено "Как это работает", принципы и ссылки на официальную документацию.
    * Добавлены матрицы "Используется в сценариях" и "Используется агентами".
    * Уточнено понятие **Adversarial Agent** как "Virtual Persona" (Виртуальная Персона) в режиме VDD.
* **README**:
    * Восстановлены пропущенные разделы "Команда Агентов" и "Системный Промпт".
    * Исправлены инструкции по установке Системы Навыков.

---

### **v3.0.0 — Система Навыков и Глобальная Локализация**

#### **Ключевые изменения**
* **Система Навыков**: Внедрена модульная библиотека `.agent/skills/`. Агенты теперь динамически загружают "навыки" вместо использования монолитных промптов.
* **Архитектура Локализации**: Новая структура директории `Translations/`. Полная поддержка переключения между Английским и Русским контекстами.
* **Документация**:
    * Добавлен `docs/SKILLS.md`: Полный каталог доступных навыков.
    * Обновлены `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md`.

#### **Удалено**
* **Legacy**: Удалена директория `/System/Agents_ru` (заменена на `Translations/RU`).

---

### **v2.1.3 — Документация и согласованность сценариев**

#### **Исправлено**
* **ARCHITECTURE.md**: Обновлен для соответствия реальной структуре проекта (добавлены папки `.agent` и `docs`).
* **Workflows**: `full-robust.md` теперь явно вызывает `/security-audit` (Агент 10) вместо заглушки.

### **v2.1.2 — Исправление генерации .AGENTS.md**

#### **Исправлено**
* **Конфликт промптов**: Устранен конфликт, из-за которого Developer пропускал создание `.AGENTS.md`, так как Planner не ставил это в задачу, а правило "без лишних файлов" запрещало самодеятельность.
* **Planner Agent**: Теперь явно требует создания `.AGENTS.md` для новых папок.
* **Developer Agent**: Получил явное разрешение (исключение) на создание `.AGENTS.md`, даже если этого нет в task-файле.

### **v2.1.1 — Верификация процессов и безопасность**

#### **Добавлено**
* **Обязательная верификация**: Все основные сценарии (Standard и VDD) теперь включают явные циклы проверки (Analyst -> TZ Review и т.д.).
* **Лимиты безопасности**: Внедрен механизм **Max 2 Retries** для предотвращения бесконечных циклов "Исполнитель-Ревьюер".

---

### **v2.1.0 — Вложенные сценарии (Nested Workflows) и аудит безопасности (Security Audit)**

#### **Добавлено**
* **Поддержка вложенных сценариев**: Возможность вызывать одни workflows из других (например, `Call /base-stub-first`).
* **Новые сценарии**:
  * `/base-stub-first`: Базовый пайплайн Stub-First.
  * `/vdd-adversarial`: Изолированный цикл адверсариальной проверки.
  * `/vdd-enhanced`: Комбинация Stub-First + VDD.
  * `/full-robust`: Полный пайплайн с будущим аудитом безопасности.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **Документация**: Обновлены `WORKFLOWS.md`, `README.md` и `GEMINI.md`.

---

### **v2.0.0 — Public Release: Multi-Agent Software Development System**

#### **Key Highlights**

* **9-Agent Ecosystem**: A comprehensive orchestration of **9 specialized agents** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator, and others) covering the full SDLC.
* **VDD (Verification-Driven Development)**: Built-in adversarial testing with the **Sarcasmotron** agent to ensure logic consistency and high reliability.
* **Stub-First Methodology**: Strict TDD-inspired flow where architecture, E2E tests, and stubs are defined before a single line of production code is written.
* **Long-Term Memory**: Advanced artifact management using `.AGENTS.md` and structured logs to maintain context across long development sessions.
* **Native IDE Integration**: Seamless support for **Antigravity** (`.gemini/GEMINI.md`) and **Cursor** (`.cursorrules`).

#### **🚀 Quick Start**

1. **Copy agents**: Move the `/System/Agents` folder into your project root.
2. **Configure IDE**: Copy `.gemini/GEMINI.md` (for Antigravity) or `.cursorrules` (for Cursor) to your project root to enable agent instructions.
3. **Initialize**: Use the `02_analyst_prompt.md` prompt to start the session.
4. **Follow Guidelines**: Refer to the **Pre-flight Check** in the README for the full workflow.
