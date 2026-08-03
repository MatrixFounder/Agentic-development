# VDD Critique — Design Spec 095 rev 6 (Workflow Loop Contract)

**Target:** [095_workflow_loop_contract.md](../design/095_workflow_loop_contract.md) rev 6
**Date:** 2026-08-03
**Reviewer:** Adversary (fresh context, `vdd-adversarial` §2 Objective Convergence)
**Corpus state:** `75f624b` (v3.22.1) — HEAD at review time. Every `file:line` below is
pinned to that revision: Phase 2 and Phase 3 have since shifted all of them, which is the
finding H-01 is about, applied to this document.
**Prior pass:** [review-095-rev5-adversarial.md](review-095-rev5-adversarial.md) (18 findings, all claimed closed by rev 6)

---

## 1. Executive Summary

- **Verdict:** **FAIL** (reject — 4 HIGH, 8 MED, 7 LOW; M-07 / M-08 surfaced while applying fixes)
- **Confidence:** High. Every finding below was resolved against the corpus with `grep -n` /
  `awk` at HEAD; no claim rests on the document's own assertions.
- **Summary:** rev 6's 18 substantive closures hold — C-01…C-06, M-01…M-07 and L-01…L-05 were
  each re-checked and each is genuinely fixed. What rev 6 did **not** survive is its own commit:
  `75f624b` shipped the rev-6 spec **and** +57 lines across five of the workflow files it cites,
  in one commit, invalidating nine line citations — including the two `exit_bar` provenance
  anchors that §4.3.2's grammar exists to keep resolvable. Appendix B's claim *"Every row above
  was re-resolved on 2026-08-03"* was false at the moment it was written. Separately, the two
  commits immediately preceding rev 6 (`14799d3`, `a20670d`) introduced
  `documentation-standards` §4.3/§4.4 — a **reserved anchor registry** with an explicit rule that
  the spec's own `<!-- loop:<id> -->` gate violates in three ways.

**The pattern, third revision running.** Rev 5's changelog diagnosed revs 3–4 as *"the rule was
tightened and the data it governs was not."* Rev 6's changelog diagnosed rev 5 as *"the pattern rev
5 named, rev 5 repeated."* Rev 6 repeats it once more, at one remove: the rule is now sound, the
data is now correct **against a corpus that the same commit moved**. Positional citation is the
mechanism, and the framework fixed that class two commits earlier
(`documentation-standards` §4.3, `14799d3`) — the spec cites that section and does not apply it
to itself.

---

## 2. Risk Analysis

| # | Severity | Category | Issue | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H-01** | **HIGH** | Stale citation / unverifiable claim | **Nine positional citations were invalidated by the commit that shipped rev 6.** `75f624b` edited `vdd-adversarial.md` (+31), `vdd-enhanced.md` (+10), `vdd-multi.md` (+7), `security-audit.md` (+5), `full-robust.md` (+4) alongside the spec. Verified stale at HEAD: `vdd-adversarial.md:62@75f624b`→**74** (§1.2 ×2, App. B), `:64`→**76** (A.2 `exit_bar`), `vdd-multi.md:188@75f624b`→**195** (A.3 `exit_bar`), `:207`→**214** (§4.3 `scope`), `:190`→**197** (App. B), `:187-189`→**194-197** (App. B), `full-robust.md:58-59@75f624b`→**62-63** (§4.5, A.5, App. B), `:52`→**56** (§4.3.1), `vdd-enhanced.md:49@75f624b`→**62** (§1.2 spelling 2). | The two `exit_bar` anchors are the provenance for §4.3.2's *"quoted verbatim from the body at `site`"* — the grammar rev 6 added to stop exactly this drift. Appendix B carries the assertion *"Every row above was **re-resolved on 2026-08-03**"*, which is E1's own thesis (a verification claim with no gate behind it) applied to the spec for the third revision running. | Re-resolve all nine. Then stop asserting freshness: replace the note with the **rule** — every positional citation in this document is a Phase-2 re-check item, and the anchors that matter (`exit_bar`, `site`) are quoted **by content**, not by line. |
| **H-02** | **HIGH** | Schema vs. data | **A.5 declares `optional: true` on a *loop*.** §4.3's `loops[]` key table has no `optional`; §4.5 defines `optional` on **`calls[]`**. The `coverage-fix-retry` row reads *"`optional: true` — the coverage gate is opt-in"*. | Structurally identical to C-03, the class rev 6's changelog declares closed: a Phase-3 author copying Appendix A authors a key the validator must reject. The inventory is again the half that is wrong about the schema — this time the *schema* is right. | Delete the key from the loop row. The opt-in fact belongs on the `full-robust` → `vdd-multi` **call edge** (`optional: true`, legal there) and, for a human, in the loop's `what:`. |
| **H-03** | **HIGH** | Framework conflict (new, from `14799d3`) | **The `<!-- loop:<id> -->` anchor violates `documentation-standards` §4.3/§4.4 in three ways.** (a) §4.4: *"adding a **gate** that reads an anchor absent from this table is a defect"* — Component B (R3, R10) is such a gate and `loop:<id>` has **no registry row**. (b) §4.3: *"`<name>` is lowercase ASCII **kebab-case**"* — §4.3 of the spec mandates `id` be **`snake_case`**, so all 25 markers (`loop:audit_remediation`, `loop:dev_review_loop`, …) are mis-cased against the grammar the spec cites as its own precedent. (c) §4.3's syntax is *"directly above the section **heading** or block it names, followed by a blank line"*; ~20 of the 25 sites are **inside numbered lists** (`01-start-feature.md:8@75f624b`, `vdd-01:15`, `security-audit.md:38@75f624b`, `full-robust.md:42@75f624b`), where a comment-plus-blank-line insertion is unspecified and can split the list. | Phase 3 ships a gate that the framework's own TIER-1 standard classifies as a defect, and Phase 2 writes 25 anchors in a casing the standard forbids — a rename across 23 files to undo. (c) also puts S1 at risk: restructuring a list is not *"appending a marker"*. | Switch `id` to lowercase kebab-case (one spelling for the YAML key, the anchor and `binds`); add a `loop:<id>` row to §4.4's registry as a **Phase-2** deliverable; state the non-heading placement rule explicitly (own line, at the content indentation of the item it names, no blank line required inside a list). |
| **H-04** | **HIGH** | Coverage gap | **Nothing detects a *missing* `calls[]` edge.** R4 checks authored edges resolve; R5 builds the graph *"from authored `calls` lists only"*; R2 requires binds *"on all non-optional caller edges"*. All three are only as complete as `calls[]`, and no rule — nor any §4.7-style heuristic — fires when a call exists in prose but not in frontmatter. | R2 and R5 silently weaken to whatever the author remembered to declare, and the failure is invisible: a workflow that omits an edge passes every rule. §4.7 gives `loops: []` a keyword heuristic for precisely this failure mode; `calls[]` gets none, though `smoke_workflows.py:19`'s `CALL_RE` already extracts one spelling mechanically. | Add **R13** (warn, Phase 3): a prose call spelling with no matching `calls[]` entry warns — the same standing §4.7's heuristic has, and for the same reason. |
| **M-01** | **MED** | Stale evidence | **§4.3.1's site-by-site window walk no longer reproduces.** It justifies `window: 4` on `coverage-fix-retry` with *"the default reaches §3's `Max 3 iterations` at `:52`"*. That bound is at **`:56`** at HEAD; from a marker at `:42` the 12-line default ends at `:54` and no longer reaches it. The companion sentence — *"Every other site was checked and clears the default"* — rests on the same walk, run before the +31/+10/+7/+5/+4-line insertions. | The narrowing is still *safe*, but its stated evidence is false, and the reader cannot tell which of the two claims (this one, or the 23-site clearance) is still true. | Re-cite `:56`; keep `window: 4` and say why in terms that survive (a 13-line gap that one inserted paragraph re-closes — which is what just happened in the other direction); mark the clearance walk as a Phase-2 re-run, not a result. |
| **M-02** | **MED** | Stale field evidence | **§7.3/E3 is one release out of date, in the direction that matters.** E3 asserts *"the prose half of E2 landed as `developer-guidelines` §6.3. **No wrapper was built**"* and concludes there is *"no **portable** mechanism other than C"*. Since then `75f624b` (v3.22.1) shipped a portable **prose** NOT-RUN contract across five workflows and three skills — `full-robust.md:49-52@75f624b`, `security-audit.md:23-27@75f624b`, `vdd-adversarial.md:45-48@75f624b`, `vdd-multi.md:96,237`, `skill-parallel-orchestration` §2.4 — plus a dedicated audit (`docs/reviews/framework-audit-20260803-wi29-execution-evidence.md`). | It cuts **both ways** and the spec records neither: a second independent instance of the E1 class (raising C's value) *and* a portable non-C mechanism whose non-existence E3 asserts (lowering it). §7.1 item 7 is explicitly designed to answer *from the record*; the record stops one commit short. | Add **E5** stating both directions, and re-point §7.1 item 7 at it. |
| **M-03** | **MED** | Vocabulary gap | **`gate --outcome pass\|fail\|skipped` (§6.2) cannot express the state the framework just named.** v3.22.1 distinguishes *ran-and-passed*, *ran-and-failed*, and *never ran* (`scan_status: NOT_RUN` → verdict `INCOMPLETE`). `skipped` is not `not_run`: skipped is a decision, NOT_RUN is a missing capability, and E1's entire thesis is that these must be distinguishable. | Component C would record the exact conflation it was designed to expose. | Add `not_run` to the outcome enum in §6.2 and to `gates[]`' description in §4.6. |
| **M-04** | **MED** | Inventory gap | **A.2's `audit-remediation` row does not record the termination precondition added in `75f624b`.** `security-audit.md:25-27@75f624b` now states the *"until clean"* loop *"cannot be satisfied by a scan that never ran"* — a written condition on loop entry/exit. | Phase 2's job at that site is larger than *"append `max 3`"*, and A.2 is the instruction Phase 2 follows. | Note the precondition in the row and in Phase 2's scope. |
| **M-05** | **MED** | Under-specified | **`id` uniqueness has no stated scope, and the corpus already collides.** §4.3: *"`id` \| string, `snake_case`, **unique**"*. `task_review`, `arch_review`, `plan_review` each appear in **two** workflows (A.1's `vdd-01`/`vdd-02` vs A.5's `01`/`02`). | Per-workflow uniqueness is clearly intended (R12 resolves `binds` against the *callee's* `loops[]`), but with a **global** anchor registry now in play (§4.4, H-03) the unqualified word reads as a global constraint the inventory violates 3 times. | *"unique within the workflow"*, and say that the marker's uniqueness is per-file for the same reason. |
| **M-06** | **MED** | Incomplete enumeration | **§7.2 under-enumerates the doc it puts in lockstep.** It names `WORKFLOWS.md:148, :152, :161, :163` as *"a third copy of **every** bound"*. `:350` carries a fifth (*"Max 3 REJECTED iterations per task"*). | A lockstep instruction that under-enumerates its targets leaves a copy behind — which is the drift class the whole spec exists to close. | Add `:350`; state that the list is re-derived by `grep`, not carried. |
| **M-07** | **MED** | Inventory gap (found while applying the fixes) | **Both Category-2 loops declare `default_max: 3` while their body contains no bound at all.** The cap for `adversarial-cycle` lives only in the caller (`vdd-enhanced.md:67@75f624b`); `grep -i '\bmax\b' vdd-adversarial.md` returns **nothing**. Same for `security-audit.md` — its only loop text is `:38` *"Re-run audit script until clean."* | R3 would report `BOUND_UNRESOLVABLE` on both the moment Phase 3 authors `default_max: 3`. §7's Phase 2 does cover them (*"the 9 loops of A.1/**A.2**"*), but Appendix A — the table Phase 2 is executed from — says only *"marker inserted at step 2b / step 4c"*, and a `default` a callee never states is exactly the Category-2 shape a reader would assume needs no prose edit. | Say it in both A.2 rows: Phase 2 writes the `max 3` into the **callee** body, not only the marker. |
| **M-08** | **MED** | Broken structure | **Appendix B's evidence table is split in two by a blockquote inserted mid-table.** Five rows (`vdd-enhanced calls non-VDD 01/02` … `Framework retry limit in docs`) sit *after* the note and render as a second, header-less table. | The rows most likely to be skimmed past are the ones a renderer mangles — and `documentation-standards` §5 governs exactly this. | One table, note after it. |
| **L-01** | LOW | Stale citation | App. B's *"Reader scripts scan frontmatter"* cites `check_prompt_references.py:17,50-61`. `:50-61` is `iter_files`' direct-file branch plus a docstring; the line that scans every line (frontmatter included) is **`:72`**. | An evidence row that does not evidence its claim. | Cite `:17` + `:72`. |
| **L-02** | LOW | Wrong spelling | §1.2 gives spelling 1 as `Call /<name>`. The corpus and `CALL_RE` (`smoke_workflows.py:19`, `` r"\b(?:Call\|call)\s+`?/([a-z0-9-]+)`?" ``) both use the **backticked** form — `` Call `/03-develop-single-task` `` (`05-run-full-task.md:19@75f624b`). | §1.2 is authoring guidance (R4), so the cost is a reader's, not a validator's. | Fix the form; add that only spelling 1 is machine-detected today. |
| **L-03** | LOW | Declared-unused | `on_exhaust` declares four values; the 25-row inventory uses **two** (`escalate_user`, `needs_human`). | `stop_success` / `warn_continue` are declared data with no reader — the test §4.6 applies to `gates[]` and §2 applies to Component A. | Keep with a one-line justification, or cut to the two in use. |
| **L-04** | LOW | Wrong anchor | §7.1 item 9 cites `skill-parallel-orchestration` §1.1 (*Detection* — vendor primitive resolution). The frame/evidence semantics the question is about are §2.2 and §2.4. | The Phase-5 author reads the wrong section. | Cite §2.2 + §2.4. |
| **L-05** | LOW | Undefined surface | §5.3 declares `--json` with no output schema and no rule that references it. | A flag nobody can implement to spec. | Define it or drop it until B has a consumer. |
| **L-06** | LOW | Forward inconsistency | §1.2's callee table will contradict §4.5 the moment `adversarial-cycle`'s **required** self-edge is authored: the table lists `vdd-adversarial \| vdd-enhanced`, and R5's exception needs `vdd-adversarial` to also call itself. | A table that the spec's own rule invalidates at Phase 3. | Add the self-edge to §1.2 with a note that it is the R5 pairing, not a new call path. |
| **L-07** | LOW | Release hygiene (repo, not spec) | HEAD (`75f624b`) is **v3.22.1**; its parent (`a9e179b`) is **v3.22.2**. The versions were committed out of order. | Not a 095 defect; noted because §7.1 item 6 asks the Phase-5 author to detect drift *by version*. | Out of scope for this spec — raise separately. |

---

## 3. Objective-bar assessment (exit criteria)

| Bar | State |
| :--- | :--- |
| Full test run **executed** | ✅ `python3 tests/run_tests.py` → `Ran 278 tests … OK`, exit 0. Run by the reviewer in-session, not claimed. |
| 0 CRITICAL | ✅ None. No finding makes the framework unsafe; all are spec-internal. |
| 0 legitimate logic / security / slop findings | ❌ **4 HIGH + 6 MED.** |
| Only bikeshedding remains | ❌ |

**Verdict: REJECT.** Not converged.

---

## 4. What rev 6 got right (checked, not assumed)

Each of the 18 prior findings was re-verified at HEAD:

- **C-01** — `full-robust` now has A.5 rows for both wrapper retries; A.1–A.6 tile all 23 workflows
  exactly once (A.1 5 + A.2 2 + A.3 1 + A.4 1 + A.5 9 + A.6 6 = 24, minus `vdd-05-run-full-task`
  counted in both A.1 and A.5). Totals verified: 7+2+1+1+14 = **25** ✅
- **C-02** — `dev_review_loop` is in A.1; A.2 holds exactly the two rebindings §1 property 2 names ✅
- **C-03 / D8** — R1 is one-directional; A.2's `adversarial_cycle` is legal ✅
- **C-04** — A.3's `exit_bar` (`"no legitimate findings remain — only style/nits"`) is a **verbatim**
  substring of `vdd-multi.md` (now `:195`) ✅; A.2's is verbatim at `vdd-adversarial.md` (now `:76`) ✅
- **C-05** — the cited review does have 5 blocking findings, CRITICAL = #1 ✅
- **C-06** — S1 / S8 / S10 / R6 / §4.3.1 / §7.2 / §7.3 all read Phase 2/3 consistently with D7 ✅
- **M-01…M-07** — counts (11 / 9 / 7 files / 14 already-bounded), R3's `max <N>` grammar, §4.3.3,
  R5's self-edge pairing, R4's scoping, R8's deferral, and the `framework-upgrade` §1.3/§2.3
  locators are each correct against the corpus ✅ (`framework-upgrade.md:19@75f624b` and `:27` both read
  *"If Audit fails, GOTO Step 2"*, in §1 and §2 respectively)
- **L-01…L-05** ✅

Also independently confirmed: 23 workflows, all with `description:` frontmatter; A.6's six
workflows are genuinely retry-free; `.gitignore:9` covers `.agent/sessions/` (S7); `PyYAML==6.0.3`
is already pinned in `requirements-dev.txt` (S3); the five CI job names in §5.3 match
`framework-gates.yml`; exit codes 0–5 (`envelope.py:20-25`) + 6 (`run_feedback.py:45`) leave **7**
free (§6.2); `claims.py:3-6` quotes verbatim; `light-02-develop-task` is the only workflow without
a slash command (§1.2); `WORKFLOWS.md:98-99` do name call edges `vdd-enhanced.md` does not contain.

---

## 5. Hallucination check

- [x] **Files** — every path cited in this critique was opened or `ls`-confirmed at HEAD.
- [x] **Line numbers** — every `:N` above was resolved with `grep -n` / `awk` at HEAD
      (`75f624b`), not carried from the spec.
- [x] **Quotes** — every quoted string was `grep`-matched in its source file.
- [x] **Execution** — the test run in §3 was executed in-session; its summary is copied from
      `tests/run_tests.py` output, not reconstructed.

## 6. What this review did NOT cover

- Component C's runtime design (§6) — PROVISIONAL by construction; re-derived at §7.1.
- Whether `max = 3` (D1) is the right number — an operator judgment, out of an adversary's remit.
- The downstream `onchain-analytics` work-items themselves (WI-30/31/32) — read as reports.
- Any check of `.antigravity/`, `.codex/`, `.cursor/`, `.gemini/` agent mirrors against the spec.
