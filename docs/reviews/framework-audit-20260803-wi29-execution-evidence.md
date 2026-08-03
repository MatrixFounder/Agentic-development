# Framework Audit — 2026-08-03 — the execution-evidence contract was declared universal and lived in one workflow

**Auditor:** `skill-self-improvement-verificator`, **Mode B (Plan Audit)**
**Requested by:** owner, closing WI-29 during a backlog closeout in the `onchain-analytics` project
**Verdict:** ⚠️ **WARNING** — no blocking condition triggered, but two adversarial cycles each
returned `issues-found`, every fix in this change set was applied by the orchestrator outside the
dev→review loop, and three findings are open rather than closed (§3a Cycle 2). `vdd-enhanced` §4.5:
a cap reached with orchestrator-applied fixes still carrying open findings is WARNING, never PASS.

*(This line read "✅ PASS" when the audit was written, before either cycle ran.)*

## 1. What was reported, and why the reported fix was not the fix

WI-29 (`onchain-analytics/docs/backlog/wi-29-600-bash.md`) records two subagents stalling for 600 s
in one `/vdd` run of TASK-011: `task-reviewer` (cycle 1) and `critic-security` (cycle 3). The
truncated output of the second shows the turn spent trying to launch `run_audit.py`, which its role
has no `Bash` to execute. Both recovered on a relaunch that said only "do not run the scanner,
report `scan: NOT RUN`, continue manually".

The record's own hypothesis was: *"if so, the fix is cheap — put the branch «if Bash is unavailable,
record `scan: NOT RUN` and go to manual review» in SKILL.md, not only in the orchestrator's brief."*

**That branch was already there, and had been since 2026-06-10** — `git blame` puts it at commit
`e9a2360`, `skill-adversarial-security` §3, seven weeks before the stall. Applying the proposed fix
would have re-applied an existing one and closed the record on a change that changed nothing. What
follows is what was found instead by tracing the actual path `/vdd` takes.

## 2. The actual defect

`skill-parallel-orchestration` §7 states that "all universal concepts (§2–§6) — **including merge
rules and the evidence contract** — apply on every path". §2 defines roles, layers and the
three-phase protocol. **It never defines an evidence contract.** The only place that contract is
written down is `vdd-multi.md` Step 1.0.

`/vdd` phase 4 does not run `vdd-multi`. It runs `vdd-adversarial.md`, which — after the WI-32 fix
of 2026-08-02 — carries a Cycle Brief input block and *mentions* the evidence block by analogy
("same shape as `vdd-multi`'s execution-evidence block") without ever requiring one. So on that path
a read-only teammate is spawned with:

- no evidence block, and no instruction about what to do without one;
- a skill (`security-audit` §1) whose Red Flags say **"EXECUTE the script"** with no branch for a
  role that cannot;
- a wrapper (`.claude/agents/critic-security.md`) that never mentions being read-only.

The escape hatch existed one document away, as an italic footnote *after* the fenced command. The
agent followed the instruction it met first.

**Denominator: six sites here — ten after cycle 1, and a floor rather than a total after cycle 2**
(see §3a). Found by searching before editing, per `vdd-enhanced` §4.6; the table below is the
original six:

| # | Site | Change |
| :-- | :--- | :--- |
| 1 | `skill-parallel-orchestration` §2.4 (new) | The contract itself — both halves — where §7 already claimed it lived |
| 2 | `vdd-adversarial.md` step 2a | `Execution evidence` block on **every** entry, first cycle included |
| 3 | `vdd-enhanced.md` §4.8 (new item) | The caller's obligation to gather it before spawning |
| 4 | `security-audit` §1 + §2 | A `NOT RUN` branch ahead of the command; a third Red Flag against inventing output |
| 5 | `skill-adversarial-security` §3 | Branch table moved **before** the command; the four situations enumerated |
| 6 | `.claude/agents/critic-{security,logic,performance}.md` | The read-only line **their own generated scaffolds already carry** |

Site 6 is the sharpest finding. `wrappers_manifest.json` calls Claude Code "the validated
reference/donor … INTENTIONALLY NOT generated here (it stays hand-maintained)". The generated
`.gemini` / `.codex` / `.cursor` critic wrappers each state "You are read-only: you cannot run
run_audit.py … never fabricate scanner output". The hand-maintained donor states none of it. The
copies were correct and the original was not — and the original is the only one that runs.

**Corrected in passing (site 4b):** `.claude/agents/security-auditor.md` instructed "mock results if
the environment restricts execution". That is an instruction to fabricate a security gate, and it
contradicts the same repository's "never fabricate scanner output" in three other files. Replaced
with the `NOT RUN (<reason>)` line.

## 3. What is NOT fixed, stated rather than implied

> **Superseded by the adversarial pass, and left in place because being wrong here is the point.**
> The paragraph below reported a true search of the **wrong space**. It grepped role *definitions*;
> the sibling defect lives in a **loaded skill** — exactly where `critic-security`'s did. TIER-0
> `skill-session-state` §3 tells every role, `task-reviewer` included, that it **MUST** run
> `python3 …/update_state.py`, and `skill-safe-commands` lists that command as safe to fire. So the
> mechanism §2.4 names is live for `task-reviewer`, `plan-reviewer` and `architecture-reviewer`, and
> it is now closed for all three (a "can you execute at all" branch at the head of §3, plus a
> read-only line in each wrapper). A negative result is only as strong as the space it searched, and
> this one published its conclusion in two languages before checking the space.
>
> One half of that finding did **not** hold: the reviewer prompts do say "Write the file
> `docs/reviews/…`" to roles with no Write tool, but each `.claude/agents/*-reviewer.md` wrapper
> already overrides it with "Do NOT write … yourself — the orchestrator persists". No change needed.
>
> The `task-reviewer` stall therefore now has a **plausible, verified mechanism** rather than none.
> It is still not a *reproduction*, so the downstream work-item stays open with its hypothesis
> upgraded from "not checked" to "confirmed present in the instructions".

The `task-reviewer` stall (cycle 1) is **not** explained by this. Its prompt
(`System/Agents/03_task_reviewer_prompt.md`) and both its TIER-1 skills mandate no script; a grep
for `python3` across all eleven Bash-less role definitions finds nothing addressed to it. The
mechanism proven here covers the `critic-security` case only. Recording the second case as fixed
because its sibling was would be the same error WI-29 itself objects to when it refuses to file
these under the already-closed WI-7.

## 3a. Adversarial pass (cycle 1) — what it changed

Two fresh-context reviewers were run over this change set with a full execution-evidence block. Both
returned `issues-found`; the verdict on cycle 1 was FAIL. Seventeen findings on this module, of which
the ones that changed the shipped text are listed in `CHANGELOG.md` v3.22.1 under "Corrections after
review". The two that matter most:

1. **`NOT RUN` satisfied every exit bar and was refused by none** — the contract made a *missing*
   block a finding while an all-`NOT RUN` block passed, so the cheapest compliant behaviour in every
   role became "write `NOT RUN` and converge". A loud stall traded for a silent unverified pass.
   Closed in six places.
2. **Item 8 was inserted above item 7**, while this audit, `CHANGELOG.md` and `CHANGELOG.ru.md` all
   claimed it was appended — the exact defect the append-don't-insert rule exists to prevent, in the
   change that cites that rule. §4 line 92 of this file said "appended … preserving the ordinals";
   it is true now, and was not when it was written.

### Cycle 2

A second pass over the cycle-1 corrections. Both critics returned `issues-found` again; the verdict
on cycle 2 is FAIL. What it changed:

- The `NOT RUN` clause had landed in 2 of the 3 critic SOTs — `skill-adversarial-performance` still
  blessed it while its own five wrappers said the opposite and told the agent to follow that skill
  strictly. **The fix was reported as complete one bullet after being incomplete.**
- `vdd-multi` Step 1.0 — §2.4's own instance #1, and the template the parallel path injects — had
  not been updated at all.
- `System/Agents/10_security_auditor.md` still specified the two-field footer, so the SOT and the
  fixed wrapper contradicted each other on a field the fix had just made required.
- The generator's `if evidence / elif readonly_clause` meant filling `critic-logic`'s manifest field
  **deleted** the vendor read-only line from the two adapters that enforce nothing.
- `NOT RUN` had no honest escape; `NOT APPLICABLE (<what was checked>)` is now the orchestrator's
  positive, attackable claim for a module with genuinely nothing to run.
- §9 of the skill still carried the numbers this audit had already retracted.
- Version denominator was 5 of 6 (`System/Docs/VDD.md`); §2's anti-fabrication cross-reference
  pointed at the wrong bullet, because the new Red Flag was inserted second and cited as third.

**Still open after cycle 2, named rather than closed** (this is why the verdict is WARNING, not
PASS, per `vdd-enhanced` §4.5):

1. `vdd-multi`'s merged verdict enum is `PASS | FAIL at <severity>` — there is no state for
   "unverifiable", so three critics all reporting it still aggregate to `PASS`, and `full-robust`
   §2 gates on exactly that.
2. The same "a role cannot run what its skill mandates" defect is live for `product-analyst` and
   `solution-architect` (`skill-product-analysis`, `skill-product-solution-blueprint`). The correct
   search space is **every skill loaded by a Bash-less role**; cycle 1 widened it from role
   definitions to one TIER-0 skill and stopped there. It has not been swept exhaustively, so the
   "ten sites" denominator below is a floor, not a total.
3. Nothing detects donor↔manifest content divergence; `--check` compares generated↔manifest only.

**Denominator, corrected.** "Six sites, all fixed" counted the sites of the *critic* mechanism. With
the reviewer roles included the contract was missing at **ten**: the six above plus
`skill-session-state` §3 and the three reviewer wrappers. Five further files changed for the `NOT
RUN` bar and the scan-status footer (`vdd-adversarial` SKILL, `full-robust`, `security-audit.md`,
`security-auditor`, the wrappers manifest + 12 regenerated scaffolds).

## 4. Mode B checklist

1. **[x] Verification step.** `doctor.py` → preflight passed. Full gate set, CI list **∪** local
   suites (`developer-guidelines` §6.3 rule 1 — CI is a floor, take the union):
   `pytest tests/ .agent/skills/skill-spec-validator/scripts/tests/` → **390 passed, 35 subtests**;
   `tests/run_tests.py` → **275 tests, OK**; `validate_skills.py` → **45/45**;
   `check_prompt_references.py` → 41 references across 42 files resolve; `security_lint.py` → passed;
   `smoke_workflows.py` → passed. `validate_skill.py` on all three edited skills → PASS (warnings are
   pre-existing "Execution Policy section missing" notices that an untouched control skill,
   `vdd-adversarial`, emits identically).

   > **Corrected after the first pass.** This line originally read `pytest tests/ -q` → 343 passed,
   > which is **narrower than the invocation CI runs** — CI's list adds the spec-validator tests, and
   > `run_tests.py` is in neither. That is rule 1 of the §6.3 this framework shipped one release ago,
   > and it was missed while auditing the next one. The numbers above are the union.
2. **[x] Rollback.** Clean worktree at `8571284` before starting; rollback is
   `git restore <path>`, which is why no `.bak` is made.
3. **[x] Atomic updates.** Independent insertions; any one can be reverted alone. Item 3 is item 8
   of `vdd-enhanced.md` §4 and now genuinely **follows** item 7, preserving the ordinals spec 095
   references — the same constraint the WI-32 fix observed. **It did not, when this line was first
   written:** it sat above item 7, and this checkbox asserted otherwise. Caught by the adversarial
   pass; see §3a.
4. **[x] Test coverage.** No new script, workflow, or skill file — this is guidance text consumed by
   agents, so there is no executable behaviour to test. Stated rather than silently skipped; it
   would become blocking the moment one of these edits grew a script.

## 5. Blocking conditions (§4 of the skill)

| Condition | Status |
| :--- | :--- |
| Removing `skill-core-principles` / `skill-safe-commands` from any agent | ❌ not triggered |
| Modifying `GEMINI.md` without a `System/Docs` update | ❌ not triggered — `GEMINI.md` untouched |
| Creating a new workflow without a trigger in `GEMINI.md` | ❌ not triggered — no new workflow |

No bypass flag used or needed.

## 6. Residual risk

- **One behaviour change, not pure guidance.** Site 4b flips `security-auditor` from "mock results"
  to "report `NOT RUN`". A role that previously produced a (fabricated) scan section will now produce
  an honest gap. That is the intent, and it is the one change here that could alter a downstream
  verdict — in the direction of refusing to certify what was never measured.
- **Cross-project blast radius.** Four repositories consume this framework. Five of six sites are
  additive; the sixth is the correction above.
- **Version numbers bumped and, on the owner's instruction, released as v3.22.1.**
  `skill-parallel-orchestration` 3.7→3.8, `security-audit` 3.6→3.7 (H1 heading too — the repo's own
  L10 "version sprawl" lesson), `skill-adversarial-security` 1.4→1.5. The first version of this audit
  said the release note was deferred because cutting a version is the owner's call; the owner then
  asked for it, so `CHANGELOG.md` and `CHANGELOG.ru.md` carry a v3.22.1 entry. Noted while writing
  it: **`CHANGELOG.ru.md` has no v3.22.0 entry at all** — a pre-existing translation gap, left
  unfilled (translating someone else's release text is not this change's business) but stated in the
  file itself, so v3.22.1 landing directly above v3.21.11 does not read as continuity.
- **Left uncommitted** for owner review before it reaches the other three projects.
