---
review: design-spec-095
subject: docs/design/095_workflow_loop_contract.md (rev 5)
date: 2026-08-03
method: adversarial pass (`vdd-adversarial`) — every claim in the spec re-derived from the repo;
        every count re-added from the spec's own inventory; every phase reference re-checked against D7
counts: 18 findings · 6 HIGH · 7 MED · 5 LOW
---

# VDD Critique: Design Spec 095 rev 5 — Workflow Loop Contract

## 1. Executive Summary

- **Verdict**: **FAIL** — rev 5 does not meet its own objective bar. It is not ready to enter Phase 2.
- **Confidence**: **High**. Every finding below was verified mechanically against files in this
  repository; no finding rests on a judgment call about design taste.
- **Summary**: rev 5 closed the five blocking findings of `review-095-independent.md`, but the
  three mechanisms it introduced to do so (`site` grammar, `exit_bar` grammar, D7 ship-order
  reversal) are each violated by the spec's own data. The inventory is one workflow short — the
  same defect D2 was written to fix — the schema forbids a combination its own Appendix A
  declares, and D7's phase renumbering was applied to §5/§7 but not to §3's safety invariants,
  which now document a rollback that restores the wrong artifact.

**The governing pattern, stated once:** rev 4 and rev 5 both tightened a *rule* and left the
*data the rule governs* untouched. Rev 5's own changelog names this ("the rule was tightened and
the data it governs was not") and then repeats it three times.

## 2. Risk Analysis

| # | Severity | Category | Issue | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C-01** | **HIGH** | Inventory | **`full-robust` has no Appendix-A category** — it is the only 1 of 23 workflows with none, which is verbatim the defect D2 exists to fix for `framework-upgrade`. It owns **two** bounded retry loops: `full-robust.md:42-43` ("re-run the coverage gate **once**") and `:58-59` ("**one** retry of the failed sub-step"). Distinct workflows enumerated across A.1–A.6 = **22**, against a header that says 23. | R6 (Phase 3, error) forces a knowingly false `loops: []` on the one workflow whose header asserts *"Every retry loop is bounded"*. §4.7's keyword heuristic then fires on its `until clean` (`:49`) — a warning whose real cause is a missing declaration, entered into the expected-warnings fixture as noise. | Add both loops to A.5 (`coverage_fix_retry`, `docs_update_retry`, `default_max: 1`, `forbidden`, `escalate_user`). A.5 becomes 14 loops across **9** workflows — which is what its header already claims. Add the §2 wrapper to §1 property 2's table. |
| **C-02** | **HIGH** | Inventory / traceability | **F10 of the cited review was never applied.** A.2 still records `vdd-03-develop.dev_review_loop` as having caller bind *"`vdd-05` step 2D: Max 3"*. But `vdd-05-run-full-task.md:15` delegates to *"`vdd-03-develop.md` **Step 3**"* only — the persona overlay — and never enters vdd-03's step-4 loop (`vdd-03-develop.md:24`). §1.2 and §4.5's `partial` field both state this. The "Max 3" at `vdd-05:17` is vdd-05's own loop, **already** recorded in A.5 as `dev_delegate_loop`. | The same bound is counted twice — a 4th instance of the class rev 5's changelog declares closed *"**3 of 3 now**"*. `override: allowed` on that loop has no binder to justify it, and §7.1 item 4 ("only two genuine rebindings exist") contradicts an A.2 that lists three. | Move `dev_review_loop` to Category 1 (no binder → needs its own bound). A.2 drops to exactly the 2 rows §1 property 2 names. Correct the changelog claim to "3 of 4; the 4th is F10, closed in rev 6". |
| **C-03** | **HIGH** | Schema self-contradiction | **A.2's `adversarial_cycle` is invalid under §4.3.** It declares `default_max: 3` **and** `judgment_terminated: true`; §4.3 says `default_max` *"Must be `null` if … `judgment_terminated: true`"*. It also omits `exit_bar`, which §4.3 marks required and **R10 makes an error**. | A Phase-3 author copying Appendix A authors a declaration the validator must reject. Worse, the rule is wrong in substance: `vdd-adversarial` genuinely has both a judgment bar (Objective Convergence) *and* a caller cap of 3 — a numeric backstop under a judgment bar is the normal case, not an illegal one. | Relax §4.3: `null` is *permitted* under `judgment_terminated`/`gated_by` (R1's direction), *required* only under `override: required`. Give the row its `exit_bar` — the quotable one already exists at `.agent/workflows/vdd-adversarial.md:64`. |
| **C-04** | **HIGH** | Rule vs. data | **A.3's own `exit_bar` fails the grammar rev 5 introduced in the same revision.** §4.3.2 requires a verbatim substring quoted from the body at `site`; A.3 declares `exit_bar: "clean pass \| bikeshedding-only"`, and `grep -F` on `vdd-multi.md` returns **zero** matches for that string (the body says *"**Clean pass**: no real issues found"* at `:187` and *"**Bikeshedding-only**: no legitimate findings remain"* at `:188`). | The single worked example of "a bar the author cannot quote from the body" is the spec's own value. R10 errors on the inventory the spec ships. | Replace with a substring that exists, e.g. `"no legitimate findings remain — only style/nits"` (`.agent/workflows/vdd-multi.md:188`). |
| **C-05** | **HIGH** | Unverifiable claim | **The status line's readiness claim cannot be resolved against its own citation.** It reads *"rev 4 closed 6 of the 9 blocking review findings; rev 5 closes the remaining 3 (review-095-independent.md)"*. That review has **5** blocking findings, numbered 1–5; its CRITICAL is **#1** (R3 vacuity). The rev-5 changelog then cites "Finding 6", "Finding 8" and "Finding 9 — the CRITICAL one", none of which exist in the cited file under those numbers. | The first line a reader uses to decide whether the spec is ready is a claim with no gate behind it — E1's own thesis ("a gate that never ran is indistinguishable from a gate that passed") applied to the spec's own status field. | State the counts the cited review actually has (5 blocking + F1–F24 + Themes A–D + Scope challenge) and re-point every changelog driver at a resolvable anchor. |
| **C-06** | **HIGH** | D7 regression | **The D7 phase reversal was applied to §5 and §7 but not to §3, §4.3.1, R6, §7.2 or §7.3.** Stale, and now inverted: **S1** ("Phase **3** edits prose only where a bound is added"), **S8** ("Reverting Phase **3** restores prose; reverting Phase **2** removes frontmatter"), **S10** ("Phase **3** only *adds* bounds"), **R6**'s "(Phase 2)" parenthetical against a Phase column of 3, **§4.3.1** ("marker insertion part of the same phase that writes the contract" — markers are Phase 2, the contract is Phase 3), **§7.2** (WORKFLOWS.md lockstep "during Phase 3"), **§7.3/E4** ("§7's **Phase-2** exit gate cites `check_prompt_references.py`" — that citation now lives in the Phase-3 gate). | S8 is a *safety invariant* that now documents the wrong rollback: reverting Phase 3 would remove frontmatter, not restore prose. An operator following S8 during an incident reverts the wrong commit. | Renumber all six against D7. S8 becomes: reverting Phase 3 removes frontmatter + validator; reverting Phase 2 removes the prose bounds and markers. |
| **M-01** | **MED** | Arithmetic | **Four counts disagree with the inventory they summarize.** "Twelve loops have no bound" (§1.1, §2, §7 Phase 2, D7) vs **11** enumerated (A.1 6 + A.2 3 + A.3 1 + A.4 1). "~fifteen lines across **five** files" (§2, D7) — imported verbatim from the review's *pre-D2* count of 6 loops in 5 files — vs **9** bounds across **7** files after D2 and F12 added three loops. "the **13** already-bounded ones" (§7 Phase 2) vs A.5's **12**. A.5's header "12 loops across **9** workflows" vs **8** enumerated. | D7 — the decision that reversed the ship order — rests on a measured comparison (~15 lines vs ~700–850). If the numerator is wrong the argument still holds, but the spec's central quantitative claim is not reproducible from its own appendix. | Recompute from Appendix A and state the two different numbers separately: **11** loops lack a numeric bound; **9** of them receive one in Phase 2 (D1 leaves Cat 3/4 `null`), across **7** files, ~20 lines. |
| **M-02** | **MED** | Rule gap | **R3's second half has no grammar.** §4.3.1 defines exactly how `site` resolves and then leaves *"must match prose bound"* undefined. The corpus writes bounds in at least seven idioms, two of which spell the number as a **word**: `full-robust.md:43` ("re-run … **once**") and `:58` ("**one** retry"). | A digit matcher errors on two correctly-bounded loops (false positive); a matcher loose enough to accept them is on the road back to rev 3's "the digit appears anywhere" vacuity. R3 is the only thing holding A+B up. | Define the canonical prose form (`max <digits>`, case-insensitive, inside the window) and make Phase 2 *append* it where the prose spells the bound in words — an addition, so S1 holds. |
| **M-03** | **MED** | Schema gap | **`default_max` cannot express a two-level counter, and Appendix A already contains an illegal value.** A.5's `heal-issues` cell reads `3 (+ cross-run max_attempts_per_issue: 2)` — not an `int ≥ 1 \| null`. A.3 collapses `vdd-multi`'s three independent per-category counters (`.agent/workflows/vdd-multi.md:186`, reported separately at `:207` as `L=<Nl>, S=<Ns>, P=<Np>`) into one declaration. | A Phase-3 author copying the table writes invalid YAML; the validator's own inventory cannot round-trip. | Declare `default_max: 3`, `scope: per_run` for heal-issues and record the cross-run counter as **not expressible in v1** with a §7.1 question. Declare `scope: per_item` for `multi_fix_loop`, defining *item* = critic category. |
| **M-04** | **MED** | Dead rule | **R5's recursion exception applies to nothing.** `recursive` is a `loops[]` key; R5 excepts cycles in the `calls[]` graph. No workflow declares a `calls[]` self-edge — `.agent/workflows/vdd-adversarial.md:44`'s "Repeat this workflow" is prose, and A.2 marks the *loop* `recursive: true`. | The validator has no defined mapping from a recursive loop to the edge it should tolerate; the first author to declare a self-edge gets a false R5 error. | Require the self-edge when a loop declares `recursive: true`, and key the exception on that pairing — or drop the exception and state acyclicity is unconditional. |
| **M-05** | **MED** | Incoherent rule | **R4 and R5 contradict.** R4 requires `calls[].workflow` entries to resolve *"across all 3 call syntax spellings"*; entries are **basenames**, and R5 states the graph is *"built from authored `calls` lists only"*. Nothing in the rule set ever reads the prose spellings. | An implementer reads R4 as mandating a prose scan that R5 forbids — the ambiguity lands in a gate that Phase 4 makes blocking. | Split it: R4 = the authored basename resolves to a file. Record the three spellings as authoring guidance (a §1.2 note), not as a rule input. |
| **M-06** | **MED** | Unfireable rule | **R8 has no machine-readable input after D6.** It fires on *"loops inside list-iterating workflows"*, but D6 removed `for-each` from `loops[]`, so nothing declares that a workflow iterates a list — leaving prose detection, which the spec refuses everywhere else. | A permanent no-op in a rule table whose stated standard is *"A rule that cannot fail is not a rule"*. | Move R8 to Phase 5 with Component C, which has the runtime scope data — the same treatment §4.6 gives `gates[]`. |
| **M-07** | **MED** | Locator error | **Two Appendix-A `site` cells point at the wrong place.** `framework-upgrade.spec_audit_retry` says "step 2" — that is the GOTO **target**; the gate is §1.3 (`.agent/workflows/framework-upgrade.md:19`). `plan_audit_retry` says "step 4" — `## 4.` is *Documentation & Finalization*, which contains no loop; the gate is §2.3 (`:27`). | A Phase-2 author following the table inserts one marker in the wrong section — the precise failure rev 5's Appendix-A rewrite was written to end. | `site` cells → §1.3 and §2.3. |
| **L-01** | **LOW** | Stale text | §7.3 says *"see the independent review **below**, which concludes **rev 3** is not ready to build from"*. It is not below (separate file), and the verdict is about rev 3 in a rev-5 document claiming to close it. | A reader looks for a section that does not exist and takes a superseded verdict as current. | Cite the path; mark the verdict as addressed. |
| **L-02** | **LOW** | Stale citation | Appendix B cites `check_prompt_references.py:21` for "regex fixed". `:21` is the first line of the explanatory comment; the fixed regex is at **`:30`**. | An evidence index that does not resolve — in the row about a gate that did not resolve. | Cite `:21-30`. |
| **L-03** | **LOW** | Inconsistency | §7.1 item 6 says §6 *"assumes exit codes 7 and 8 are free"*. §6.2 uses 6 and **7** only; 8 appears nowhere. | The Phase-5 gate asks the author to re-check a claim the spec does not make. | Say "exit code 7". |
| **L-04** | **LOW** | Ambiguous citation | §7.3 attributes the field evidence to "work-items WI-30 / WI-31 / WI-32" of an unnamed *"downstream project"*. This repo's backlog uses the same flat `WI-<n>` namespace (currently max **WI-10**), so the ids will collide. `docs/TASK.md:12` names the project (`onchain-analytics`). | A future reader resolves WI-30 against the wrong ledger, or against none. | Name the project in §7.3, as TASK.md does. |
| **L-05** | **LOW** | Upstream defect | `01-start-feature.md` numbers **two** items "4." (`:7` and `:14`), so A.5's site "at step 4" is ambiguous for marker insertion. | Marker lands under the architecture step; R3 then compares `default_max: 2` against the wrong window. | Note in Appendix A that the `task_review` marker goes at `:7-8` (the TASK-review verification loop). The duplicate numbering is a separate `/light` fix. |

## 3. Objective-bar assessment (exit criteria)

| Condition | Status |
| :--- | :--- |
| Full test run executed | **N/A** — subject is a design document; no code changes. `smoke_workflows.py`, `check_prompt_references.py` and the workflow corpus were read directly and are unmodified by this review. |
| Zero CRITICAL findings | **Met** — nothing here breaks a running system today; the spec is not yet implemented. |
| Zero legitimate logic findings | **NOT met** — 6 HIGH, 7 MED, all reproducible. |
| Only bikeshedding remains | **NOT met.** |

**Verdict: FAIL.** Approval is bound to the objective bar, not to the finding count.

## 4. Hallucination check

- [x] **Files**: every cited file opened in this session — all 23 `.agent/workflows/*.md`,
      `System/scripts/check_prompt_references.py`, `System/scripts/smoke_workflows.py`,
      `.github/workflows/framework-gates.yml`, `requirements-dev.txt`,
      `.agent/skills/run-feedback/scripts/feedback_lib/{claims,envelope}.py`,
      `System/Docs/WORKFLOWS.md`, `docs/reviews/review-095-independent.md`, `docs/BACKLOG.md`.
- [x] **Line numbers**: every `file:line` above re-read at the cited line; the four Appendix-B
      citations that *do* hold (`claims.py:56`, `WORKFLOWS.md:220`, `.agent/workflows/vdd-multi.md:190`,
      `.agent/workflows/vdd-adversarial.md:62`, `vdd-enhanced.md:56-58`) are recorded here as verified so rev 6
      does not re-litigate them. **Caveat, and it is the spec's own thesis:** `vdd-adversarial.md`
      gained 19 lines from an unrelated edit *during* this review, moving two anchors (`:43`→`:62`,
      `:45`→`:64`). Every citation here was re-resolved against the working tree afterwards.
- [x] **Counts**: workflow count (`ls .agent/workflows/*.md | wc -l` = 23), frontmatter presence
      (23/23), slash-command coverage (23 command files = 22 aliases + `run-feedback`), and every
      Appendix-A row total were re-added by hand, not carried over.
- [x] **Negative checks**: `grep -F 'clean pass | bikeshedding-only' vdd-multi.md` → 0 hits (C-04);
      `grep -nE 'Repeat|GOTO|Go to Step|until clean'` over the six A.6 workflows → 0 hits, so the
      §4.7 heuristic produces no false warnings there; `grep 'WI-3[012]' docs/BACKLOG.md` → 0 hits
      (L-04).

## 5. What this review did NOT cover

- **Loops outside `.agent/workflows/`** — `System/Agents/*.md`, `.agent/skills/*/SKILL.md`.
  The spec scopes itself to workflows; the retry idiom exists in skills too.
- **Whether `max = 3` is the right number** for the VDD twins when their non-VDD counterparts use
  2 and `WORKFLOWS.md:220` states a framework-wide 2. That is the operator's call (D1), and it is
  unchanged by this review — but §7.2's "update WORKFLOWS.md in lockstep" is in tension with S10
  ("no existing bound value is changed") and rev 6 should say which governs.
- **Empirical inertness of the frontmatter block** for non-Claude vendors — still the largest
  untested assumption in the spec, as `review-095-independent.md` also recorded.
- **Component C's design** — §6 is PROVISIONAL by construction and re-derived at §7.1.
  Reviewing it now would be reviewing a draft the spec already promises to rewrite.
