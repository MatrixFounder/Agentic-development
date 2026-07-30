# Framework Audit: unit tests for `skill-spec-validator` (TASK 092)

**Date:** 2026-07-30
**Auditor:** Self-Improvement Verificator (Mode A + Mode B)
**Target:** `docs/TASK.md` **and** `docs/PLAN.md` for TASK 092
**Status:** **BLOCKED** — on one finding in PLAN Step 4 (details in §3)

> [!IMPORTANT]
> **This audit is retroactive and gated nothing.** Self-Improvement Mode requires the meta-audit
> on the PLAN *before* execution. For TASK 091 it ran ([`framework-audit-091.md`](framework-audit-091.md));
> for TASK 092 it was skipped, and the work was executed, reviewed twice and committed
> (`4b2a65e`) without it. It is written now so the gap is recorded rather than forgotten, and so
> the one blocking finding is stated in the artifact that was supposed to carry it.
>
> The blocking finding below was **independently caught during execution** by the adversarial
> review, and is fixed in the shipped code. So the defect did not reach `main` — but it reached
> *implementation* and had to be found by a critic reading the code, which is precisely the cost
> of skipping a plan-time gate. Read the verdict as "what this audit would have returned on
> 2026-07-30 before Step 4", not as a live block on committed work.

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** none — no flag set. No TIER 0 skill is touched by TASK 092 at all. Note that a
*post-hoc* audit is **not** a bypass: `[OVERRIDE_VERIFICATION]` force-approves despite failures,
which is the opposite of what is happening here. The protocol violation is the missing pre-execution
run, and it is recorded as such above rather than laundered through a flag.

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | TASK ID `092`, slug `spec-validator-unit-tests`; `docs/tasks/task-092-*` free at authoring time. TASK 091's artifacts were still live, and the plan states that as the rollback baseline instead of assuming a clean tree. |
| **Tier Protection** | ✅ Pass | TASK 092 touches one TIER 3 skill (`skill-spec-validator`) plus a new `scripts/tests/` tree. `core-principles`, `skill-safe-commands`, `artifact-management`, `skill-session-state` untouched — verified against the diff, not the plan's intent. |
| **Skill Compatibility** | ✅ Pass | No new agent or prompt, so no TIER 0 load list to declare. The suite is stdlib-`unittest` and mirrors `run-feedback`'s layout, so one `discover` idiom covers both skills — a compatibility choice the plan makes explicit (NFR: no pytest dependency). |
| **Documentation** | ✅ Pass | Step 5 adds the four Execution-Policy sections the skill validator warns about; Step 6 covers CHANGELOG (EN + RU) and the ledger close. `System/Docs/` needs no edit: TASK 092 changes no framework contract, only adds tests. `GEMINI.md` untouched, so §4's "GEMINI.md without System/Docs" blocker does not apply. |
| **Migration** | ✅ Pass | Nothing to migrate — additive tests, no config key, no session-state shape change, no `validate.py` behavior change. The one migration-shaped concern is portability: the corpus tests must **skip** rather than fail once the skill is installed in another repo, which R11 requires. |
| **Verification Step** | ✅ Pass | Every step carries an executable verify line; Step 4's is the strongest in either plan — *re-inject the historical regression and confirm the suite goes red*, which verifies the **guard**, not merely the code. |
| **Rollback Plan** | ✅ Pass | Additive files + one SKILL.md edit; `git checkout -- <path>` per step, stated with the TASK-091 caveat. The template's `cp X X.bak` is again declined, consistently with audit 091. |
| **Atomic Updates** | ✅ Pass | 6 steps grouped by requirement cluster, each independently runnable and independently green. |
| **Test Coverage** | ✅ Pass | This task **is** test coverage; R1–R11 map onto Steps 1–4 with no orphan requirement, and R12 is gated by `validate_skills.py`. |
| **Root Integrity (Stub-First)** | ⚠️ Pass, by exemption | Stub-First does not apply literally: the production code (`validate.py`) already exists and is explicitly **not** being changed, so there is no stub to write first. The spirit is honored inversely — the tests are RED against the *historical* matcher (Step 4's re-injection check) rather than against a stub. Worth stating, because "no stub step" would otherwise read as an omission. |

## 2. Risk Analysis

- **Risk 1 — the anti-drift probe is satisfiable by construction (BLOCKING, see §3).** Step 4's
  probe is specified as `^#{2,4} … (requirements traceability|\(rtm\))`, while the matcher under
  test requires `Requirements\s+Traceability|\bRTM\b`. The probe's condition is a **subset** of the
  matcher's, so "every probed heading matches `RTM_HEADER`" is a tautology: it holds for any
  matcher at least as loose as the probe, including a matcher that has drifted into uselessness on
  every other shape. The test would have been green on the exact defect WI-1 was filed for.
  *Required fix:* the probe must be **strictly wider** than the matcher.
- **Risk 2 — a wider probe over-matches real prose.** The unavoidable consequence of fixing Risk 1:
  widening surfaces headings that name traceability without being RTM headings. *Mitigation:* an
  explicit, **staleness-checked** exclusion set — an allow-list that outlives its entries silently
  widens itself back, so the audit requires a companion test asserting every declared exclusion
  still exists in the corpus.
- **Risk 3 — corpus counts hardcoded into prose go stale on the next archive.** The TASK's baseline
  table and the planned `## Validation Evidence` section quote live measurements (21 / 20 / 26 / 13).
  Archiving TASK 092's own artifacts changes those numbers **as a side effect of finishing the
  task**. *Mitigation:* the floors (R10) must be named constants below today's counts and the prose
  must be worded as "measured at TASK 092", never as a standing invariant.
- **Risk 4 — liveness floors set too high turn artifact churn into red builds.** A floor at today's
  count fails the day someone adds a task without an RTM. *Mitigation:* R10's canary framing, with
  the reasoning in a comment beside the constants so the next author does not "helpfully" raise them.
- **Risk 5 — the test suite writes the bypass token into a file the gate then reads.** The bypass is
  a bare substring anywhere in `TASK.md`; a test fixture, a docstring, or this very audit containing
  the literal token can switch off a real gate. *(TASK 092's own first-draft spec tripped this.)*
  *Mitigation:* R4 pins the semantics as current behavior, and any file discussing the token must
  assemble it rather than spell it — which the shipped `tests/_fixtures.py` and `test_corpus.py` do.
- **Risk 6 — zero-test discovery reports green.** `unittest discover` exits 0 when it finds nothing,
  so a broken test path is indistinguishable from a passing suite. R11 requires a guard;
  the audit adds that it must also assert the corpus tests *ran* rather than skipped inside this
  repo, since Risk 2's skip mechanism is exactly what would hide them.
- **Risk 7 — scope creep into `validate.py`.** The task sits on a live `/vdd-enhanced` gate and the
  temptation is to "just fix" the two things it documents (the `ID`/`Requirement` column contract,
  the substring bypass). *Mitigation:* both are recorded in TASK §5 as owner decisions and pinned by
  tests as-is. The plan's own rule — *a gate loosened to fit a nonconforming artifact is the
  original defect running backwards* — is the correct one and is respected in the diff.

## 3. Verdict & Actions

**BLOCKED** on Risk 1. One finding, and it is the load-bearing one: the deliverable of TASK 092 is a
guard against matcher drift, and as specified in PLAN Step 4 that guard could not detect matcher
drift. Everything else in this plan is sound — the block is not a request to re-plan.

**Required actions:**
1. **Rewrite Step 4's probe to be strictly wider than `RTM_HEADER`** (e.g. keyed on the `trace*` /
   `rtm` stems, not on the matcher's required phrase), and state the invariant in the test's failure
   message: *matchers are widened toward the corpus, never the corpus narrowed toward the matchers.*
2. Pair the wider probe with a **staleness-checked exclusion set** for legitimate non-RTM
   traceability headings (Risk 2).
3. Keep the R10 floors **below** current counts, with the canary reasoning in a comment (Risk 4),
   and word every quoted corpus number as a TASK-092 measurement (Risk 3).
4. Never spell the bypass token literally in any file the gate reads — assemble it (Risk 5).
5. Assert in the runner that the corpus tests **ran**, not merely that discovery exited 0 (Risk 6).
6. Leave `validate.py` alone; record disagreements as observations (Risk 7).

**Disposition (post-hoc, verified against the committed diff at `4b2a65e`):** all six actions are
satisfied in the shipped work — the probe is `\b(?:trace\w*|rtm)\b`, `KNOWN_NON_RTM_SHAPES` has its
own staleness test, the floors are 15 / 10 against measurements of 20 / 14, the token is assembled
in both test modules, `run_tests.sh` checks the corpus tests did not skip, and `validate.py` is
unchanged. Action 1 was reached through the adversarial review rather than through this gate, which
is the finding that matters about the process, not about the code.

## 4. Process finding (recorded for the retro)

Skipping this audit cost nothing in shipped quality **this time**, because a parallel critic
independently found the tautology. That is luck, not a control: the critics were reading
implementation, and a plan-time reader had a strictly easier job — the subset relation between two
regexes is visible in the plan text, before any code exists. The generalizable rule is the one
this framework already writes down and this run did not follow: *a gate that is skipped when the
work looks routine is a gate that only ever runs on work nobody was worried about.* Filed here
rather than in `docs/backlog/` because the defect is in the operator's adherence, not in the
framework's contracts.
