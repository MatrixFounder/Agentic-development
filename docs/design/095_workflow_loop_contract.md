# Design Spec 095 — Workflow Loop Contract & Run Frame Stack

**Status:** DRAFT rev 6 — revs 4–5 closed all **five** blocking findings of
[review-095-independent.md](../reviews/review-095-independent.md) (plus its `site` / `exit_bar`
grammar gaps); rev 6 closes the 18 defects found by the rev-5 adversarial pass
([review-095-rev5-adversarial.md](../reviews/review-095-rev5-adversarial.md)).
**Author:** Orchestrator (self-improvement mode)
**Date:** 2026-08-03
**Supersedes:** DRAFT rev 5. **Blocks:** nothing.
**Prime constraint:** *do not break the current framework.* Every element below is additive,
inert-by-default, and revertible with a single `git revert`. See §3.
**Decisions applied:** D1–D8 in §8 — **decision-complete**. D7 (ship order reversed) accepted by the
operator 2026-08-02; D8 (schema correction, forced by the spec's own inventory) added in rev 6.
Changelog in Appendix C.

---

## 1. Problem statement

The framework's orchestration layer is not a flat state machine. It is a **hierarchical,
composable protocol** with five properties that no existing artifact records mechanically:

1. **A call stack up to 5 deep.**
   `full-robust` → `vdd-enhanced` → `05-run-full-task` → `03-develop-single-task` →
   developer↔reviewer loop.

2. **Caller-side rebinding of callee bounds.** A sub-workflow declares an open-ended loop; the
   caller closes it at the call site. Two genuine caller-side rebindings exist today (with **four**
   additional caller wrapper or skip mechanisms — the wrappers are loops the *caller* owns, and
   they are inventoried as such in Appendix A.5):

   | Caller | Callee | Mechanism / Rebinding |
   |---|---|---|
   | `full-robust` §3 | `security-audit` §4c | Genuine rebind: `"until clean"` → `no CRITICAL/HIGH`, **max 3 iterations** |
   | `vdd-enhanced` §4 | `vdd-adversarial` | Genuine rebind: **max 3** adversarial cycles |
   | `full-robust` §2 | `vdd-multi` | Caller flag: passes `--no-fix`, callee skips Phase 3 fix loop entirely |
   | `full-robust` §2 | *(own loop)* | Caller-owned wrapper: **one** re-run of the coverage gate after a materialized fix task (`full-robust.md:42-43`) |
   | `full-robust` §4 | `04-update-docs` | Caller-owned wrapper: **one** retry around single-pass sub-workflow (`full-robust.md:58-59`) |
   | `vdd-enhanced` §3 | `03-develop-single-task` | Caller-owned loop: **max 2** fix-and-rerun rounds *total* over single tasks |

3. **Deliberately non-composing counters.** `vdd-enhanced` §3 states the rule in prose because
   nothing enforces it: *"max 2 fix-and-rerun rounds **total** (not per task; `/develop`'s
   internal max-2 review loop counts **separately**)."*

4. **A runtime nesting signal that already exists — for exactly one concern.**
   `run_feedback.py claim` returns `EXIT_CLAIM_DENIED = 6` when an outer workflow owns the run.
   Its own source states the thesis of this spec:

   > *"The 'skip if sub-workflow' rule cannot be enforced by prose (workflows have no runtime
   > nesting signal), so ownership is a flock-guarded claim file."*
   > — `.agent/skills/run-feedback/scripts/feedback_lib/claims.py:3-6`

5. **Crash recovery that exists in one workflow only.** `heal-issues` has a flock run-lock,
   `heal_run start`/`end` journal tombstones, orphan detection, and a cross-run attempt counter
   in `.agent/feedback/heal-state.json` — which contains a real recorded incident:
   `"session died before Phase 4; tail (journal end, heal-state) completed post-hoc"`.
   No other workflow can detect or recover from the same failure.

### 1.1 The concrete defect this produces

**Eleven loops have no numeric bound in the workflow that owns them** (Appendix A.1 ×7 + A.2 ×2 +
A.3 ×1 + A.4 ×1, re-added from the inventory in rev 6). Some are bounded only when reached through
a specific caller; invoked directly they run unbounded. **Nine** of the eleven receive a bound in
Phase 2 — D1 leaves the judgment-terminated (A.3) and HITL-gated (A.4) loops at `null` deliberately.
Full inventory in Appendix A.

The most significant finding is not random scatter but a **systematic regression in the VDD
family** — the VDD variants dropped the bounds their non-VDD twins have:

| Non-VDD workflow | Bound | VDD twin | Bound |
|---|---|---|---|
| `01-start-feature` step 4 (TASK review) | Max 2 attempts → STOP | `vdd-01-start-feature` step 4 | *"repeat the review"* — **none** |
| `01-start-feature` step 5 (ARCH review) | Max 2 attempts → STOP | `vdd-01-start-feature` step 5 | *"repeat the review"* — **none** |
| `02-plan-implementation` step 3 | Max 2 attempts → STOP | `vdd-02-plan` step 3 | *"repeat the review"* — **none** |
| `03-develop-single-task` step 4 | Max 2 attempts → STOP | `vdd-03-develop` step 4 | *"Go to Step 2.1"* — **none** |

Additionally, `framework-upgrade.md` has two unbounded retry loops ("*If Audit fails, GOTO Step 2*"), and `vdd-05-run-full-task` step 2 has an unbounded Red tests Builder loop.

The invariant asserted in `full-robust`'s header — *"Every retry loop is **bounded** with an
explicit escalation path"* — holds only inside that call tree.

### 1.2 The call graph & call invocation spellings

Derived from inspecting all `.agent/workflows/<name>.md` files.

| Callee | Callers (sub-workflow invocation in-degree) |
|---|---|
| `01-start-feature` | `base-stub-first`, `vdd-enhanced` *(Note: `light-01`/`light-02` mention `01-start-feature` as an escalation handoff, not a sub-workflow call)* |
| `02-plan-implementation` | `base-stub-first`, `vdd-enhanced` |
| `03-develop-single-task` | `05-run-full-task`, `full-robust`, `vdd-enhanced`, **`vdd-adversarial`** (`.agent/workflows/vdd-adversarial.md:62`) |
| `05-run-full-task` | `base-stub-first`, `vdd-enhanced` |
| `04-update-docs` | `full-robust` |
| `security-audit` | `full-robust` |
| `vdd-multi` | `full-robust` |
| `vdd-enhanced` | `full-robust` |
| `vdd-adversarial` | `vdd-enhanced` |
| `vdd-03-develop` | `vdd-05-run-full-task` *(partial delegation to Step 3)* |
| `light-02-develop-task` | `light-01-start-feature` |
| **`vdd-01-start-feature`** | **none** |
| **`vdd-02-plan`** | **none** |
| **`iterative-design`**, **`framework-upgrade`**, **`heal-issues`**, **`product-*`** | **none** |

The codebase uses three distinct call syntax spellings:
1. `Call /<name>` (e.g. `.agent/workflows/05-run-full-task.md:19`)
2. `Execute .agent/workflows/<name>.md` (e.g. `.agent/workflows/vdd-enhanced.md:49`)
3. ``Call workflow `<name>` `` (e.g. `.agent/workflows/vdd-adversarial.md:62`)

Two structural consequences:
- **`vdd-enhanced` calls the NON-VDD `01-start-feature` / `02-plan-implementation`**, not the
  VDD variants. Therefore `vdd-01-start-feature` and `vdd-02-plan` have **no caller at all** —
  they exist only as the `/vdd-start-feature` and `/vdd-plan` entrypoints.
- Every workflow except `light-02-develop-task` has a slash command in `.claude/commands/`, so
  **every workflow is directly invocable**. A loop bounded only by its caller is therefore
  unbounded on its own entrypoint.

> **Note on call edges (`contract.calls[]`):** `contract.calls[]` represents active workflow invocations,
> never documentation pointers (e.g., the `vdd-03` ↔ `vdd-05` footer link) or escalation handoffs (`light-01` → `01`).

### 1.3 What is explicitly NOT the problem

- **Not a missing FSM diagram.** A flat state table cannot express caller-side rebinding
  or counter scoping.
- **Not an XML markup requirement.** XML instruction blocks are rejected to maintain vendor neutrality.
- **Not enforcement-by-prose.** Binding enforcement requires process exit codes (`validate.py`, `flock`, `diff -q`, `claim` → 6).

---

## 2. Design principle

> **The exit code is the vendor-agnostic interface.**

Everything specified here reduces to files that any runtime can read and scripts that any
runtime can run.

Three components, each valuable alone:

**The defect in §1.1 is closed by prose, not by any component.** Nine loops need a bound written
where they live: roughly twenty lines across seven files, in the idiom
`.agent/workflows/01-start-feature.md:11-12` already uses. That work is **Phase 2** and it stands entirely alone.
Rev 3 shipped it *after* 23 files of frontmatter and a CI gate, and justified the ordering by
calling frontmatter "the highest-value / lowest-risk step" — the independent review refuted that
by measurement (~700–850 new lines to protect ~20). See **D7**.
*(Rev 5 quoted "~15 lines across five files" — the review's figure, measured against the six A.1
loops it knew about, before D2 added `framework-upgrade` ×2 and F12 added `vdd-05`'s builder loop.
The order argument is unaffected by the correction; the number is not the review's any more, so it
is restated here as this spec's own.)*

Components exist for what remains **after** the bounds are written — drift, and claims about
runs. Each is stated by what it detects once §1.1 is already closed:

| # | Component | Kind | What it detects *after* Phase 2 |
|---|---|---|---|
| **A** | Loop Contract — machine-readable frontmatter | Declaration | Nothing on its own. It is the input B reads; alone it is a second copy of a number, which is a liability, not an asset |
| **B** | `check_loop_contract.py` — CI/dev-time validator | Gate | A bound edited in prose but not in frontmatter (or the reverse) — R3; a loop added later with no declaration — R6 + the §4.7 keyword heuristic; a caller binding a loop that does not exist — R12 |
| **C** | `run_stack.py` — frame stack, counters, gate outcomes | Enforcement | A bound *exceeded at runtime*, and a completion claim (`✓`) with no recorded gate behind it — neither of which any static check can see |

**A is explicitly not "valuable alone".** §4.6 defers `contract.gates[]` because *"declaring data
that nothing reads is the over-engineering this design otherwise avoids"*; that test applies to
`loops[]` too, and A fails it until B exists. A and B therefore ship as **one phase**, and the
table above states B's detections rather than A's, because A has none.

Ship order is **prose bounds → A+B → C**. `contract.gates[]` (§4.6) ships with C. Component C is
PROVISIONAL and re-derived from Phase 2–3 evidence at the Phase-5 entry gate (§7.1).

---

## 3. Safety invariants (the "do not break" contract)

| # | Invariant | How it is guaranteed |
|---|---|---|
| **S1** | **Additive only.** No existing line of any workflow, prompt, or skill is deleted or reworded. | **Phase 2** edits prose **only where a bound or a marker is added** — including the canonical `max <N>` form required by §4.3.1, which is *appended*, never a rewrite of the surrounding sentence. Component A (Phase 3) appends frontmatter keys. Components B and C are new files. |
| **S2** | **Frontmatter parser safety & regex non-collision.** | All 23 workflows already contain YAML frontmatter (`description:`). Frontmatter additions MUST be valid YAML and MUST NOT introduce string values containing `Call /name` or `System/Agents/*.md` to prevent false matches in script scanners (`smoke_workflows.py`, `check_prompt_references.py`, installer scripts, `vendors.yaml`, and LLM harnesses). |
| **S3** | **No new runtime dependency.** | Runtime scripts (`run_stack.py`) use Python stdlib only (`json`, `fcntl`, `os`, `time`). CI validator (`check_loop_contract.py`) may use `PyYAML==6.0.3` (pinned in `requirements-dev.txt`) with an explicit pip install step in CI. |
| **S4** | **Warn-only first.** | Component B ships returning exit 0 with `WARN:` lines, flipping to exit 1 only in Phase 4. |
| **S5** | **Component C is opt-in per workflow.** | Workflows not calling `run_stack.py` remain byte-identical in behavior. |
| **S6** | **Fail-open at runtime.** | If `run_stack.py` is missing, unreadable, or errors, the workflow logs a warning and continues using prose bounds. |
| **S7** | **Zero new gitignore/installer surface.** | State lives in `.agent/sessions/stack.json` (already ignored by `.gitignore`). |
| **S8** | **Rollback in reverse phase order.** | Reverting Phase 5 removes Component C; reverting Phase 4 restores warn-only; reverting Phase 3 removes the frontmatter and the validator; reverting Phase 2 removes the prose bounds and the `<!-- loop:<id> -->` markers. Reverting out of order strands a `site` that names a marker no longer present. *(Rev 5 stated this pair inverted — a leftover of the pre-D7 numbering.)* |
| **S9** | **`latest.yaml` schema is untouched.** | Frame stack uses sibling file `.agent/sessions/stack.json`. |
| **S10** | **No existing bound value is changed.** | Phase 2 only *adds* bounds where missing; it never alters an existing numeric cap in a workflow body. **Boundary:** `System/Docs/WORKFLOWS.md:220` states a framework-wide "2 attempts" as *documentation of* the workflows, not as a bound any loop executes; §7.2's lockstep update of that line is a doc correction, not an S10 violation. S10 governs workflow bodies. |

---

## 4. Component A — Loop Contract (frontmatter)

### 4.1 Placement

Extends the existing YAML frontmatter of `.agent/workflows/*.md`. All 23 workflows currently contain a frontmatter block with a `description:` key.

### 4.2 Grammar

Restricted to standard YAML block mappings, block sequences, scalars, `null`, integers, and booleans:

```yaml
---
description: Run the full robust pipeline (…)      # unchanged, still first
contract:
  version: 1
  loops:
    - id: audit_remediation
      what: "fix → re-run audit until clean"
      site: "<!-- loop:audit_remediation -->" # or line:45-60
      default_max: 3
      override: allowed
      on_exhaust: escalate_user
  calls:
    - workflow: security-audit
      kind: invoke
      binds:
        audit_remediation:
          max: 3
          exit_bar: "no CRITICAL/HIGH findings"
---
```

### 4.3 `contract.loops[]` — every retry/iteration loop this workflow **owns**

| Key | Type | Required | Meaning |
|---|---|---|---|
| `id` | string, `snake_case`, unique | yes | Stable handle. Referenced by callers' `binds` and `run_stack.py`. |
| `what` | string | yes | One-line human description. |
| `site` | string | yes | Machine-resolvable locator, **exactly one of two forms** — see §4.3.1. Free-form prose (`"§4c"`, `"Step 2D"`) is a validator error, not a fallback. |
| `default_max` | int ≥ 1 \| `null` | yes | Numeric cap applied when no caller overrides it. Must be `null` if `override: required`. **May** be `null` — and only then — if `judgment_terminated: true` or `gated_by: hitl`; a numeric backstop *under* a judgment bar or a HITL gate stays legal, and is the common case (D8). One value only: a second, differently-scoped counter over the same loop is not expressible in v1 — see §4.3.3. |
| `override` | `forbidden` \| `allowed` \| `required` | no, default `forbidden` | Caller-side rebinding policy. See §4.4. |
| `scope` | `per_run` \| `per_item` \| `global` | no, default `per_run` | Counter scope. `per_item` = counter resets per task, finding, **or critic category** (`vdd-multi` re-spawns per category and reports `L=<Nl>, S=<Ns>, P=<Np>` at `vdd-multi.md:207`). |
| `on_exhaust` | `escalate_user` \| `stop_success` \| `warn_continue` \| `needs_human` | yes | Declared escalation path. |
| `recursive` | bool | no, default `false` | Loop re-enters this same workflow. |
| `judgment_terminated` | bool | no, default `false` | Loop terminates via structured verdict against a written bar. Requires an `exit_bar` in the §4.3.2 citation form (R10). |
| `exit_bar` | string | required when `judgment_terminated: true` | Written termination condition, quoted verbatim from the body at `site` — §4.3.2. |
| `gated_by` | `hitl` | no | Every iteration requires blocking human decision. |
| `window` | int ≥ 1 | no, default `12` | Lines after a marker `site` that R3 and R10 search. Narrow it where two loops sit close enough to share a window — see §4.3.1. |

#### 4.3.1 `site` grammar — the rule R3 stands on

R3 is the only thing keeping the frontmatter number and the prose number from disagreeing
silently, and it is worth exactly as much as `site` is resolvable. Rev 3 defined `site` as a
free-form string and let R3 fall back to *"the digit appears anywhere in the body"*. Both halves
failed: **every** bound in Appendix A is 1, 2 or 3, and **all 23** workflow bodies contain those
digits in their numbered step lists, so the fallback passed unconditionally; and the example
anchors (`"§4c"`, `"Step 2b"`, `"§1.3"`) occur in **none** of the files they name. A rule that
cannot fail is not a rule, and a `--strict` CI gate advertising it is worse than no gate.

**Exactly two forms are legal. There is no third, and no fallback.**

| Form | Example | Resolves to | Use when |
|---|---|---|---|
| Marker | `<!-- loop:audit_remediation -->` | The line carrying the marker, plus the following `window` lines (default 12) | **Preferred.** Survives every edit above it |
| Line range | `line:45-60` | Those lines of the body, frontmatter excluded from the count | Only where a marker cannot be placed |

`<name>` in the marker MUST equal the loop's `id`. The marker is an HTML comment: inert in every
renderer, invisible to `smoke_workflows.py`'s `CALL_RE` and to `check_prompt_references.py`
(S2), and it is the same device `documentation-standards` §4.3 already mandates for addressing an
authored section by structure rather than by prose.

**Anything else is `SITE_UNRESOLVABLE` — an error, never a pass.** A line range whose bounds fall
outside the body is the same error. This is the one property that makes R3 falsifiable, so it is
stated as a hard failure rather than a preference.

**The bound needs a grammar too — R3 stands on two resolvable things, and rev 5 gave only one of
them a form.** "Must match prose bound" is undefined until *prose bound* is. The corpus writes the
same fact seven ways (`Max 2 attempts`, `max 3 fix-and-rerun attempts`, `Max 3 iterations`,
`max 2 review cycles`, `max 2 fix-and-rerun rounds total`, `bounded loop, max 3 iterations`) —
and twice **in words**: `full-robust.md:43` (`re-run the coverage gate **once**`) and `:58`
(`**one** retry of the failed sub-step`). A digit matcher errors on those two correctly-bounded
loops; a matcher loose enough to accept them is on the road back to rev 3's vacuity.

**Canonical form:** `max <digits>`, case-insensitive, as a whole word, inside the resolved window —
regex `(?i)\bmax(?:imum)?\s+(\d+)\b`. **All** matches in the window must agree, and their digit must
equal `default_max`. Zero matches is `BOUND_UNRESOLVABLE`; disagreeing digits is `BOUND_AMBIGUOUS` —
both errors, neither a pass. `default_max: null` (A.3/A.4) exempts the loop from R3 entirely; its
termination is policed by R10 instead. Where the existing prose states the bound in words,
**Phase 2 appends the canonical form** (`… **one** retry of the failed sub-step (max 1)`) rather
than rewording the sentence — an addition, so S1 holds.

**The window is a declaration, because the default collides in the real corpus.** Simulating this
rule against `.agent/workflows/` before writing it down: a marker on `light-02-develop-task.md:25`
(`max 3 fix-and-rerun attempts`) pulls `:34`'s `max 2 review cycles` into a 12-line window and
reports `BOUND_AMBIGUOUS` on a correctly-declared loop. Two adjacent loops in one section is the
normal case, not the exotic one — `01-start-feature`'s two review loops sit 8 lines apart and are
saved only by both being `2`. So `window` is an **optional per-loop key** (§4.3), and narrowing it
until exactly one loop's bound is in view is the author's job, which `BOUND_AMBIGUOUS` exists to
make them do. Appendix A carries the narrowed value wherever the default does not hold — two rows
after a site-by-site walk of the corpus (`light-02.light_fix_loop`, `full-robust.coverage_fix_retry`).
Every other site was checked and clears the default, three of them only because the neighbouring
bound happens to carry the same digit; marker insertion shifts line numbers, so Phase 3 re-checks
rather than trusting this walk.

**Ordering consequence, stated because it bit rev 4 and was mis-stated in rev 5.** The markers do
not exist yet — the corpus carries none. So a `site` cannot be authored before the marker it names
is inserted. Under D7 that puts **marker insertion in Phase 2**, the phase that writes the bounds,
while the `site` values referencing them are authored in **Phase 3** with the rest of the contract.
R3 is enforced from Phase 3 — the first phase in which the marker, the prose bound and the
frontmatter number all exist — and is listed against Phase 3 in §5.2.

**Negative fixture is a deliverable, not a suggestion.** Component B ships with a fixture whose
frontmatter says `default_max: 3` over prose saying `Max 2`, and CI fails if that fixture passes.
Without it, "R3 works" is the same unguarded claim R3 exists to prevent — and the repository has
already shipped this exact failure once: `check_prompt_references.py` matched zero references for
its entire life while printing `OK: checked 42 files` (fixed in TASK 095).

#### 4.3.2 `exit_bar` grammar — the same problem as `site`, and the same fix

`judgment_terminated: true` is what lets a loop declare `default_max: null` legally. Rev 3 asked
only that `exit_bar` be **non-empty**, so `exit_bar: "until done"` turned any unbounded loop into
a fully compliant declaration, and Phase 4's `--strict` gate — advertised as *"unbound loops fail
CI"* — would have been asserting that an author typed a string. Every loop in Appendix A.1 could
have been closed that way instead of receiving a bound.

**Form:** `"<verbatim substring quoted from the body at `site`>"`. The validator resolves `site`
per §4.3.1 and requires the substring to occur inside that window. The bar therefore cannot drift
from the prose that states it, for the same reason and by the same mechanism as R3.

```yaml
- id: adversarial_cycle
  site: "<!-- loop:adversarial_cycle -->"
  judgment_terminated: true
  exit_bar: "0 CRITICAL, 0 legitimate logic/security/slop findings, only bikeshedding remains"
```

A bar the author cannot quote from the body is a bar the body does not state — which is the
finding, not an inconvenience. Write it into the prose first; that is Phase 2's job anyway.

> **Rev 6 applied this to the spec's own data.** A.3 shipped `exit_bar: "clean pass |
> bikeshedding-only"`; `grep -F` returns **zero** hits for that string in `vdd-multi.md`. The one
> worked example of a bar nobody can quote was this document's. Corrected in A.3.

#### 4.3.3 What v1 deliberately cannot express

One loop carries **one** counter. Two real loops carry two, and v1 records only the inner one:

- `heal-issues` — `max 3` iterations *per run* (`heal-issues.md:80`) **and** a cross-run
  `max_attempts_per_issue: 2` (`:58`) that survives process death in `.agent/feedback/heal-state.json`.
- `vdd-multi` — three independent per-category counters. `scope: per_item` (item = critic category)
  names the shape; it does not carry three values.

Rev 5 papered over the first by writing `3 (+ cross-run max_attempts_per_issue: 2)` into an
Appendix-A cell — a string that is not a legal `int ≥ 1 | null`, which a Phase-3 author would have
copied verbatim into YAML. **v1 declares the per-run counter and says so.** The outer counter is
recorded as a known non-expressible fact here and as §7.1 item 10; inventing a `secondary_bound`
key for two call sites is the over-engineering §4.6's test forbids. If Phase 5 finds a third case,
that is the evidence for adding the key.

### 4.4 The `override` enum

| `override` | Meaning | `default_max` | Caller `binds` entry |
|---|---|---|---|
| `forbidden` | Workflow owns bound outright. Caller may not rebind. | int; `null` permitted only with `judgment_terminated`/`gated_by` | Error (R9) |
| `allowed` | Workflow has default; caller **may** re-scope. | int; `null` permitted only with `judgment_terminated`/`gated_by` | Optional |
| `required` | Workflow states no cap; caller **must** bind one. | must be `null` | Mandatory on non-optional edges (R2) |

### 4.5 `contract.calls[]` — sub-workflows invoked

| Key | Type | Required | Meaning |
|---|---|---|---|
| `workflow` | string (basename) | yes | Callee basename without `.md`. Must resolve to `.agent/workflows/<name>.md`. |
| `kind` | `invoke` \| `escalate` | no, default `invoke` | `invoke` = sub-workflow execution; `escalate` = handoff/switch workflow. |
| `partial` | string | no | Indicates fragment delegation (e.g. `"Step 3"` for `vdd-05` calling `vdd-03`). |
| `suppresses` | list of string | no | List of callee `loop_id`s suppressed by invocation flags (e.g. `--no-fix`). |
| `binds` | mapping `loop_id → {max, exit_bar?}` | conditional | Rebinding mapping for callee loops. |
| `optional` | bool | no, default `false` | Edge is conditional. |

**Two constraints on `binds`, both learned from mis-attributions in this document's own appendix:**

1. **`partial` bounds what is bindable.** On an edge carrying `partial`, only loops *inside the
   delegated fragment* may be bound; binding anything else is R12. Rev 5 recorded `vdd-05`'s
   `Max 3` (`vdd-05-run-full-task.md:17`) as a bind on `vdd-03-develop.dev_review_loop` — but
   `vdd-05:15` delegates to **Step 3** only and never enters vdd-03's step-4 loop. The cap is
   vdd-05's **own** loop, already inventoried as `dev_delegate_loop`. A caller cannot rebind a
   loop it never reaches; when it caps a fragment it invoked, that is an owned loop, not a bind.
2. **A wrapper retry around a call is an owned loop, not an edge property.** `calls[]` has no
   retry count and will not gain one: `full-robust` §2 and §4 each retry a sub-workflow **once**,
   and both are declared in `full-robust`'s own `loops[]` (A.5). The edge records *that* the call
   happens; the loop records *how many times*.

**Recursion (the R5 exception).** A loop with `recursive: true` MUST be accompanied by a `calls[]`
self-edge (`workflow: <own basename>`, `kind: invoke`); R5's exception is keyed on that pairing and
tolerates exactly the self-edges so paired. Without the self-edge the exception has no edge to
apply to — rev 5's state — and R5 would fire on the first author who declared one.

### 4.6 `contract.gates[]` — ships with Component C (Phase 5)

| Key | Type | Meaning |
|---|---|---|
| `id` | string | Stable handle for gate. |
| `site` | string | Locator in body. |
| `kind` | `script` \| `review_verdict` \| `hitl` \| `non_blocking` | Gate classification. |
| `command` | string | Verbatim command executed for `kind: script`. |
| `bar` | string | Objective written bar for `kind: review_verdict`. |
| `claims` | string | Token contributed to completion line (e.g. `"Security ✓"`). |

### 4.7 Negative declaration (`loops: []`)

Workflows without retry loops declare `loops: []`. The validator enforces a heuristic check: if `loops: []` is declared on a body containing retry keywords (`Repeat`, `GOTO`, `Go to Step`, `until clean`), the validator emits a warning.

---

## 5. Component B — `check_loop_contract.py`

### 5.1 Placement

`System/scripts/check_loop_contract.py`.

### 5.2 Rules

| # | Rule | Severity | Phase | Rationale |
|---|---|---|---|---|
| **R1** | `default_max: null` requires `override: required`, `judgment_terminated: true`, or `gated_by: hitl`. Otherwise error. **One direction only** — an int alongside `judgment_terminated`/`gated_by` is legal (D8). | error | 3 | Eliminates un-bounded loops. Phase 2 has already written every prose bound, so there is no transitional state to accommodate — see D7. |
| **R2** | `override: required` loops must be bound by all non-optional caller edges. | error | 3 | Ensures required overrides are supplied. |
| **R3** | Frontmatter `default_max` must equal the digit of the **single** canonical `max <N>` match (§4.3.1) inside the anchored `site` window (`line:NN-MM` or `<!-- loop:<id> -->`). No match → `BOUND_UNRESOLVABLE`; two different digits → `BOUND_AMBIGUOUS`. Negative test fixture required. | error | 3 | Prevents frontmatter/prose drift. Both halves — locator *and* bound form — are grammars, or the rule degrades to rev 3's digit-anywhere pass. |
| **R4** | Every `calls[].workflow` basename must resolve to an existing `.agent/workflows/<name>.md`. | error | 3 | Ensures call-graph integrity. Scoped to the **authored** list, consistent with R5: the three prose spellings (`Call /x`, `Execute .agent/workflows/x.md`, ``Call workflow `x```) are authoring guidance for §1.2, never a validator input — rev 5's wording implied a prose scan R5 forbids. |
| **R5** | `calls` graph must be acyclic, except a self-edge paired with a `recursive: true` loop in the same workflow (§4.5). Graph built from authored `calls` lists only. | error | 3 | Prevents unintended workflow call recursion. |
| **R6** | Every workflow MUST contain a `contract:` block with `version` and `loops`. | error | 3 | Forces explicit declaration across all 23 workflows — including the ones whose loops are already bounded, which is how `full-robust` stopped being invisible (Appendix A.5). |
| **R7** | `on_exhaust` required on every loop. | error | 3 | Mandates escalation path. |
| **R8** | `scope: per_run` loops inside list-iterating workflows generate warning if unnoted. | **warn** | **5** | Prevents counter scoping confusion — but **has no input at Phase 3**: D6 removed `for-each` from `loops[]`, so nothing declares that a workflow iterates a list, leaving only the prose detection §5.2 refuses everywhere else. Deferred to Component C, which observes iteration at runtime — the same treatment §4.6 gives `gates[]`, and for the same reason. |
| **R9** | Caller cannot `bind` a loop declared `override: forbidden` by callee. | error | 3 | Enforces ownership boundaries. |
| **R10** | `judgment_terminated: true` requires an `exit_bar` in the §4.3.2 citation form, and the quoted substring must be found in the body at `site`. | error | 3 | "Non-empty" is satisfied by `"until done"`, which converts any unbounded loop into a compliant declaration — the §1.1 defect re-legalized through the escape hatch. |
| **R11** | Completion claim tokens (`claims`) must map to a recorded gate. | error | **5** | Ensures verifiable completion claims. |
| **R12** | Every key in caller `binds` must match a valid `loops[].id` in callee. | error | 3 | Catches invalid bind references. |

### 5.3 CLI Contract & CI Wiring

```bash
python3 System/scripts/check_loop_contract.py --root . [--strict] [--json]
```

Exit codes:
- `0`: Success (or warnings with `--strict` off)
- `1`: Rule violations with `--strict`
- `2`: Invocation / file access error
- `3`: YAML parsing error

CI job in `.github/workflows/framework-gates.yml`:

```yaml
  loop-contract:
    name: Loop contract
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Dependencies
        run: pip install -r requirements-dev.txt
      - name: Check workflow loop contracts
        run: python System/scripts/check_loop_contract.py --root .
```

Job names aligned with CI workflow: `tooling-tests`, `skill-validate`, `reference-integrity`, `security-lint`, `workflow-smoke`, `loop-contract`.

---

## 6. Component C — `run_stack.py` (PROVISIONAL)

> [!IMPORTANT]
> **PROVISIONAL.** Component C details will be re-derived against Phase 2–4 evidence at the Phase-5 entry gate (§7.1).

### 6.1 Placement & Storage
- File: `.agent/skills/skill-session-state/scripts/run_stack.py`
- State: `.agent/sessions/stack.json`
- Synchronization: `fcntl.flock` with `fsync` (see `claims.py:56`).
- Platform boundary: POSIX systems use `fcntl`; on Windows platforms without `fcntl`, `run_stack.py` logs a warning and falls back to prose bounds (S6).

### 6.2 CLI & Verbs
- `push --workflow X --run-id R [--bind W.loop=N]`
- `pop --workflow X`
- `tick --loop L` (returns exit `7` on bound exhaustion)
- `gate --id G --outcome pass|fail|skipped`
- `status [--json]`
- `owns --concern retro` (exit `0` if outermost, exit `6` if sub-workflow)

---

## 7. Phased delivery

> **Phase 2 closes the defect and owes nothing else.** Per D7 it ships alone: prose bounds plus the
> `<!-- loop:<id> -->` markers, no frontmatter, no new script, no CI job. If the project stops
> there, §1.1 is still closed — that is the property the order was chosen for. Components A and B
> answer a different question (drift), and are worth re-examining *after* Phase 2 lands rather than
> assumed now.


| Phase | Deliverable | Gate to advance | Revert cost |
|---|---|---|---|
| **1** | Design spec rev 5 (this spec) | Operator sign-off — **granted 2026-08-02**, D7 included | Delete file |
| **2** | **Close §1.1.** Write the missing bound + escalation path in the prose of the **9** loops of A.1/A.2 (7 files); append the canonical `max <N>` form (§4.3.1) wherever an existing bound is spelled in words; and insert the `<!-- loop:<id> -->` marker at **every** loop site in Appendix A — all **25**, including the 14 already-bounded ones, whose marker is all Phase 2 owes them | Every loop in Appendix A.1/A.2 has a bound and an `on_exhaust` in its own body; every A.1–A.5 site carries its marker and exactly one canonical `max <N>` (A.3/A.4 excepted — they are `null` by D1); `smoke_workflows.py` green. **No frontmatter, no new script, no CI job** | `git revert` |
| **3** | Components A **+** B together: frontmatter on all 23 workflows, `check_loop_contract.py` warn-only, R3 negative fixture | Full pytest green; `smoke_workflows.py` / `check_prompt_references.py` green; **the R3 negative fixture FAILS the validator** (a fixture that passes means R3 is vacuous again); validator warnings match `docs/design/095-phase3-expected-warnings.txt` via `diff -q` | `git revert` |
| **4** | Enable `--strict` in CI | Phase 3 green for 1 full framework-upgrade cycle | Remove `--strict` flag |
| **5** | Component C (`run_stack.py`) + `contract.gates[]` | §7.1 entry gate passed; unit tests green; fail-open verified | Delete script |
| **6** | Retro `claim` integration | 3 consecutive clean runs | Keep `claims.py` |

### 7.1 Phase-5 entry gate

Component C is committed (D5) but §6 is written against the framework as it stands **before** any
other component exists. Phases 2–4 are the first real evidence this design has ever had, so
Phase 5 opens with a re-derivation, not with code. **Deliverable:** spec rev 6, §6 rewritten
against the answers below. **Exit bar:** every item answered from the Phase 2–4 record, not from
recollection. Phase 5 may not start on rev 5.

| # | Question | What the answer changes |
|---|---|---|
| 1 | **Did drift actually occur?** How many times did R3 fire between Phase 3 and Phase 4? | Near zero → the counter half of C is speculative; C narrows to `owns` + gate outcomes. Frequent → `tick` is the point of the component. |
| 2 | **Which bounds actually exhausted in real runs?** Harvest escalations from `.agent/sessions/latest.yaml` `active_blockers` and the run-feedback journal. | Reorders §6 adoption. A loop that never exhausts does not need runtime enforcement. |
| 3 | **Was `override: required` ever used?** No loop uses it today. | Never used → drop the value and R2 with it. |
| 4 | **Were `override: allowed` defaults ever re-bound to a different number?** Only two genuine rebindings exist (§1 property 2). | Never → `binds`, R9, R12 and the ancestor-resolution machinery in `tick` are ceremony. |
| 5 | **Did authors write a contract unprompted, and correctly?** | The schema's usability test. Systematic mistakes → fix §4.3 before C consumes it. |
| 6 | **Have `claims.py`, `heal-state.json`, or `envelope.py` changed?** §6 copies the first two and assumes exit code **7** is free (`envelope.py:20-25` allocates 0–5, `run_feedback.py:45` allocates 6). | Any drift there invalidates the corresponding part of §6 outright. Re-check, do not assume. |
| 7 | **Is `contract.gates[]` still worth it?** Count completion announcements (`✓` lines) and how often one was emitted after a skipped or failed gate. | Zero observed false claims → drop `gates[]`, R11 and `claims --verify`; keep C's counters only. |
| 8 | **Did the workflow set change?** New workflows, renamed ones, new callers. | Re-run §1.2; Appendix A categories may move. |
| 9 | **Multi-agent dispatch:** does a frame stack survive parallel critics (`vdd-multi`, `skill-parallel-orchestration` §1.1)? | `per_run` vs `per_item` scope is incoherent if three critics share one frame. May force a schema change before C. |
| 10 | **Did a third two-level counter appear?** v1 declares one counter per loop; `heal-issues` and `vdd-multi` are the two known exceptions (§4.3.3). | Two → leave it non-expressible and documented. Three or more → add the key, with the evidence §4.6's test demands. |

**If items 1 and 7 both come back empty** — no drift, no false completion claims — the honest
outcome is to ship a **smaller** C than §6 describes, or to record that Phases 2–4 sufficed. That
is a legitimate result of this gate, not a failure of it: the framework's own precedent is to not
build automation whose need has not been demonstrated (`heal-issues` §Scheduling). Items 6 and 7
were dropped in the rev-4 compression and are restored here, because they are the two that can
conclude *against* Component C, and a gate that can only ratify is not a gate.

### 7.2 Downstream Integration & Documentation Sync
- **Downstream Framework Installs:** Installer scripts resolve symlinks in `.agent/workflows/` and detect project-local overrides (`LOCAL_OVERRIDE`).
- **Documentation Sync:** `System/Docs/WORKFLOWS.md` holds a **third** copy of every bound
  (`:148`, `:152`, `:161`, `:163`) plus the framework-wide rule at `:220` — *"the Doer gets **2
  attempts**"* — which D1's `max = 3` for the VDD entrypoints contradicts head-on. It MUST be
  updated in lockstep during **Phase 2**, the phase that changes the prose it documents (rev 5 said
  Phase 3, a leftover of the pre-D7 numbering). Its call map is stale in the same way §1.2 was
  (`:98`, `:99` name edges `vdd-enhanced.md` does not contain) and is corrected in the same edit.
  See S10 for why this is a doc correction and not a bound change.

---

### 7.3 Field evidence — arrived before Phase 2, from a different direction (TASK 095)

§7.1 asks Phases 2–4 for evidence. Some arrived first, unasked, from a downstream project running
`/vdd` on Russian-language artifacts — **`onchain-analytics`** work-items WI-30 / WI-31 / WI-32,
filed 2026-08-02 (`provenance: machine`; see `docs/TASK.md:12`). The project name is load-bearing:
this repository's backlog uses the same flat `WI-<n>` namespace, so a bare "WI-30" resolves to the
wrong ledger. The evidence bears on this spec's **Component C** and is recorded here so the Phase-5
gate answers from a record rather than from recollection. **None of it is a decision.** Nothing in
this section commits Phase 5 to anything.

**E1 — a gate that never ran is indistinguishable from a gate that passed. Observed, not theorized.**
The reporting project found that `validate.py --mode task` had not passed on the *previous* task
either. Nobody noticed until the next task failed for a different reason. That is the exact state
`gates[]` + `run_stack.py gate --outcome` exist to make visible (§4.6). It is one observation, in
one project, and it says the *problem* is real; it does not say this design solves it.

**E2 — three ways a green verdict was produced without verification, all exiting 0.** From the same
run: (a) the gate was verified with a **narrower invocation than CI runs** — a formatter filtered to
one package picked up that package's ignore file, while CI's root invocation does not read it;
(b) the exit code was taken **after a pipe** (`… | tail`), so it reported on `tail` — twice;
(c) the command **never ran** — a package manager answers a non-matching filter with exit 0 and
"no project matched" — and the report was positive. Three occurrences in one task, by an operator
specifically hunting that defect class.

This is direct evidence for the `kind: script` + `command` fields of `gates[]`: a wrapper that
**runs** the command owns the true exit code (closing (b)), records the invocation verbatim so it
can be compared against CI (closing (a)), and distinguishes "did not run" from "passed"
(closing (c)). One mechanism, three failure modes. **It is also the strongest argument found so far
for Component C**, which is worth stating plainly because §7.1 items 1 and 7 were framed to look for
reasons to *shrink* C, and this cuts the other way.

**E3 — what TASK 095 did instead, and why.** The prose half of E2 landed as
`developer-guidelines` §6.3 (TIER 1). No wrapper was built. Building one now would put a second
mechanism beside the one this spec already designs — and the honest reading of E2 is that only
failure mode (b) has a portable mechanical fix at all: `System/scripts/installer/*` ships `.agent/`
and `System/` but **never** `.github/`, so any runner keyed to `framework-gates.yml` cannot travel
downstream. A downstream gate manifest would be a second source of truth that drifts from real CI —
re-creating failure mode (a) one layer up. **§7.1 item 7 should be re-read with that in mind:** the
question is not only "were false completion claims observed" but "is there any *portable* mechanism
other than C", and the answer found here is no.

**E4 — an instance of the same class inside this repository's own CI, found by the review below.**
`System/scripts/check_prompt_references.py` matched **zero** references for its entire existence
(`\\.` inside a raw string requires a literal backslash) while printing
`OK: checked 42 files; all System/Agents references resolve` and exiting 0. Fixed in TASK 095; the
summary line now reports the reference count and a zero-reference run fails.

This matters to *this spec* for a reason beyond the anecdote: **§7's frontmatter phase cites
`check_prompt_references.py` still being green as evidence that frontmatter is inert** — the
Phase-**3** exit gate under D7's numbering (rev 3 placed it in Phase 2, and rev 5's text still said
so). That gate was green by construction until TASK 095. Any evidence resting on it must be
gathered after the fix, never carried over from a run that predates it.

## 8. Decisions — operator review rounds 1–2, independent review round 3

| # | Question | Decision | Consequence |
|---|---|---|---|
| **D1** | Bounds for unbound loops | **`max = 3` accepted** across Category 1 and 2 | 7 Category-1 loops gain cap 3 (`forbidden`); 2 Category-2 loops gain default cap 3 matching their real caller bind (`allowed`); Category 3 & 4 remain `null`. `WORKFLOWS.md:220`'s framework-wide "2 attempts" is corrected in the same phase (§7.2). |
| **D2** | `framework-upgrade` GOTO loops | In scope. Two loops in Appendix A.1; both get a bound in **Phase 2** like every other Category-1 loop | Rev 3 put them out of scope, which left `framework-upgrade` the only workflow of 23 with no category — the state the review's finding 5 named. |
| **D3** | `contract.gates[]` | Ship with Component C in Phase 5 | Kept out of Phase 2 frontmatter. |
| **D4** | Document language | **English** | Standard across design docs. |
| **D5** | Does Component C ship? | **Yes — committed**, but re-derived in §7.1 | Phase 5 gated by §7.1 re-derivation. |
| **D6** | Is list iteration a loop? | **No** — `for-each` over finite list is not a retry loop | `loops[]` tracks retries only. |
| **D7** | Ship order: does Component A go before or after the prose bounds? | **ACCEPTED 2026-08-02 — prose bounds first, alone (Phase 2). A and B ship together, after.** | Reverses rev 3/rev 4. The independent review measured it; rev 6 re-measured against the corrected inventory: the §1.1 defect is **9 loops needing ~20 lines in 7 files**, while A+B is ~700–850 new lines across 23 files plus a CI job. Rev 3 called frontmatter *"the highest-value / lowest-risk step"*; on either measurement the inverse holds. Two consequences fall out: `pending_bound` disappears (it existed only to make a legal declaration possible *before* the bounds were written), and A stops being described as valuable alone — §4.6's own over-engineering test says it is not. |
| **D8** | `default_max` under a judgment bar or a HITL gate: forbidden, or permitted? | **Permitted.** `null` is *required* only under `override: required`; under `judgment_terminated`/`gated_by` it is *allowed*, and an int backstop stays legal | Rev 5's §4.3 said `default_max` **must** be `null` whenever `judgment_terminated: true` — and its own A.2 then declared `adversarial_cycle` with `default_max: 3` *and* `judgment_terminated: true`, because that is what `vdd-adversarial` actually is: a judgment bar (Objective Convergence) with a caller cap of 3 behind it. The inventory was right and the rule was wrong. R1's one-directional form is kept; the reverse implication is deleted. |

---

## 9. Explicitly out of scope
- Statechart DSLs or FSM engines.
- XML prompt markup.
- Modifying existing numeric bounds.
- Altering `latest.yaml` schema.

---

## Appendix A — Loop inventory (25 loops, 23 workflows)

> **The `Site` column is a contract, not a description.** Rev 3 filled it with prose
> (`"§4c"`, `"Step 2D"`) and the review verified that **none** of those strings occur in the files
> they name — so a Phase-3 author copying this table would have authored `site` values that
> resolve to nothing, and R3 would pass on all of them. Each row now carries the loop's `id` and
> the exact `site` value to write. The `<!-- loop:<id> -->` markers do not exist in the corpus
> yet; **inserting them is part of Phase 2**, in the same edit that writes the bound (§4.3.1).
>
> **Coverage is the property this appendix is checked on, and rev 5 failed it.** 6+3+1+1+12 = 23
> loops across **22** workflows under a header that said 23 — `full-robust` had no category at all,
> which is verbatim the defect D2 was written to fix for `framework-upgrade`. Its two loops are now
> in A.5. Totals: **25 loops across 23 workflows** — 7+2+1+1+14, with the six loop-free workflows of
> A.6 accounting for the remaining files. Re-add these before publishing any revision: an inventory
> that does not tile the corpus is the one artifact here nothing else can catch.

### A.1 Category 1 — Copy-drift / missing bounds (7 loops across 5 workflows)

| Workflow | Site | Today | Decision |
|---|---|---|---|
| `vdd-01-start-feature` | `task_review`<br/>`site: "<!-- loop:task_review -->"` — marker inserted at step 4 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-01-start-feature` | `arch_review`<br/>`site: "<!-- loop:arch_review -->"` — marker inserted at step 5 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-02-plan` | `plan_review`<br/>`site: "<!-- loop:plan_review -->"` — marker inserted at step 3 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `framework-upgrade` | `spec_audit_retry`<br/>`site: "<!-- loop:spec_audit_retry -->"` — marker inserted at **§1.3, the Meta-Audit gate** (`framework-upgrade.md:19`) in Phase 2 | *"If Audit fails, GOTO Step 2"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `framework-upgrade` | `plan_audit_retry`<br/>`site: "<!-- loop:plan_audit_retry -->"` — marker inserted at **§2.3, the Meta-Audit gate** (`framework-upgrade.md:27`) in Phase 2 | *"If Audit fails, GOTO Step 2"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-05-run-full-task` | `builder_red_loop`<br/>`site: "<!-- loop:builder_red_loop -->"` — marker inserted at step 2 Step B in Phase 2 | *"Red tests force a Builder loop"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-03-develop` | `dev_review_loop`<br/>`site: "<!-- loop:dev_review_loop -->"` — marker inserted at step 4 in Phase 2 | *"Go to Step 2.1"* — **none** | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |

> **The `framework-upgrade` rows are stated as section-and-step because rev 5's were wrong.**
> `spec_audit_retry`'s cell said "step 2" — that is the GOTO *target*, not the gate — and
> `plan_audit_retry`'s said "step 4", where `## 4.` is *Documentation & Finalization* and holds no
> loop. Both gates read *"If Audit fails, GOTO Step 2"* and both are section-local: §1.3 returns to
> §1.2 (draft TASK), §2.3 returns to §2.2 (draft PLAN). Phase 2 disambiguates the prose in the same
> edit that adds the bound.
>
> **`vdd-03-develop.dev_review_loop` moved here from Category 2 (F10 of the independent review,
> unapplied until rev 6).** Its listed binder — *"`vdd-05` step 2D: Max 3"* — does not exist:
> `vdd-05-run-full-task.md:15` delegates to `vdd-03-develop.md` **Step 3** only, never entering
> vdd-03's step-4 loop, and the Max 3 at `vdd-05:17` is vdd-05's own loop, already in A.5 as
> `dev_delegate_loop`. With no binder, `override: allowed` had nothing to justify it and the loop is
> simply unbounded — Category 1. See §4.5 constraint 1.

### A.2 Category 2 — Default + caller override (2 loops)

*Exactly the two genuine rebindings §1 property 2 names — the count now matches on both ends.*

| Workflow | Site | Caller bind today | Decision |
|---|---|---|---|
| `vdd-adversarial` | `adversarial_cycle`<br/>`site: "<!-- loop:adversarial_cycle -->"` — marker inserted at step 2b in Phase 2 | `vdd-enhanced` §4.3: max 3 | `default_max: 3`, `override: allowed`, `recursive: true`, `judgment_terminated: true`, `exit_bar: "0 CRITICAL, 0 legitimate logic/security/slop findings, only bikeshedding remains"` (verbatim at `vdd-adversarial.md:64`), plus the `calls[]` self-edge R5 requires (§4.5) |
| `security-audit` | `audit_remediation`<br/>`site: "<!-- loop:audit_remediation -->"` — marker inserted at step 4c in Phase 2 | `full-robust` §3: Max 3 + redefined exit bar | `default_max: 3`, `override: allowed` |

### A.3 Category 3 — Judgment-terminated (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `vdd-multi` | `multi_fix_loop`<br/>`site: "<!-- loop:multi_fix_loop -->"` — marker inserted at Phase 3 in Phase 2 | `default_max: null`, `override: allowed`, `judgment_terminated: true`, `scope: per_item` (item = critic category, §4.3.3), `exit_bar: "no legitimate findings remain — only style/nits"` (verbatim at `vdd-multi.md:188`) |

*(Rev 5's value here was `"clean pass | bikeshedding-only"`, which occurs nowhere in `vdd-multi.md` —
the §4.3.2 grammar rev 5 introduced, failed by rev 5's own data. The replacement was `grep -F`'d.)*

### A.4 Category 4 — HITL-gated (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `iterative-design` | `design_iteration`<br/>`site: "<!-- loop:design_iteration -->"` — marker inserted at Phase 5 step 7 in Phase 2 | `default_max: null`, `override: forbidden`, `gated_by: hitl` |

### A.5 Category 5 — Already bounded (14 loops across 9 workflows)

| Owner | Site | `default_max` | `override` | `on_exhaust` |
|---|---|---|---|---|
| `01-start-feature` | `task_review`<br/>`site: "<!-- loop:task_review -->"` — at the **TASK-review** verification loop, `01-start-feature.md:7-8` | 2 | forbidden | escalate_user |
| `01-start-feature` | `arch_review`<br/>`site: "<!-- loop:arch_review -->"` — at step 5 | 2 | forbidden | escalate_user |
| `02-plan-implementation` | `plan_review`<br/>`site: "<!-- loop:plan_review -->"` — at step 3 | 2 | forbidden | escalate_user |
| `03-develop-single-task` | `dev_review`<br/>`site: "<!-- loop:dev_review -->"` — at step 4 | 2 | forbidden | escalate_user |
| `05-run-full-task` | `task_retry`<br/>`site: "<!-- loop:task_retry -->"` — at step 3 | 2 | forbidden | escalate_user |
| `light-02-develop-task` | `light_fix_loop`<br/>`site: "<!-- loop:light_fix_loop -->"` — at §1.5, **`window: 6`** (the default pulls §2.4's `max 2` into view — §4.3.1) | 3 | forbidden | escalate_user |
| `light-02-develop-task` | `light_review_loop`<br/>`site: "<!-- loop:light_review_loop -->"` — at §2.4 | 2 | forbidden | escalate_user |
| `vdd-05-run-full-task` | `dev_delegate_loop`<br/>`site: "<!-- loop:dev_delegate_loop -->"` — at step 2D | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `task_validate_retry`<br/>`site: "<!-- loop:task_validate_retry -->"` — at §1.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `plan_validate_retry`<br/>`site: "<!-- loop:plan_validate_retry -->"` — at §2.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `regression_retry`<br/>`site: "<!-- loop:regression_retry -->"` — at §3.2 | 2 (`scope: per_run`) | forbidden | escalate_user |
| `full-robust` | `coverage_fix_retry`<br/>`site: "<!-- loop:coverage_fix_retry -->"` — at step 2, `full-robust.md:42-43`, **`window: 4`** (the default reaches §3's `Max 3 iterations` at `:52`). `optional: true` — the coverage gate is opt-in | 1 | forbidden | escalate_user |
| `full-robust` | `docs_update_retry`<br/>`site: "<!-- loop:docs_update_retry -->"` — at step 4, `full-robust.md:58-59` | 1 | forbidden | escalate_user |
| `heal-issues` | `heal_attempt_loop`<br/>`site: "<!-- loop:heal_attempt_loop -->"` — at Phase 2 | 3 (`scope: per_run`) | forbidden | needs_human |

**Two notes this table earns its shape from.**

*(1) Ownership — a loop the callee declares belongs to the callee's `loops[]` and appears in the
caller only as `binds`. Four rows violated that. Two are recorded in §A.2 as rebinds
(`full-robust` §3 → `security-audit.audit_remediation`; `vdd-enhanced` §4.3 →
`vdd-adversarial.adversarial_cycle`), and the fourth was the inverse error — rev 5 recorded
`vdd-05`'s own cap as a bind on a loop it never reaches (F10; moved to A.1 in rev 6). Rev 4
corrected two, rev 5 claimed **"3 of 3"**, and the true denominator was 4. **4 of 4 now.**)*

*(2) `full-robust` §4's wrapper around `04-update-docs` was the third of those rows, dismissed by
rev 5 as belonging to `calls[]`. It does not: `calls[]` records that a call happens and carries no
retry count, and `04-update-docs` owns no loop for a `binds` entry to name. A caller-owned wrapper
is a loop **the caller owns** — so both of `full-robust`'s wrappers are declared here, which is also
what gives this workflow a category at all. Both spell their bound in words (`once`, `one` retry);
per §4.3.1, Phase 2 appends the canonical `(max 1)` beside each, or R3 reports
`BOUND_UNRESOLVABLE` on two loops that are, in fact, correctly bounded.)*

### A.6 Category 6 — No retry loops (`loops: []`, 6 workflows)

`04-update-docs`, `base-stub-first`, `light-01-start-feature`, `product-full-discovery`, `product-market-only`, `product-quick-vision`.

---

## Appendix B — Evidence index

| Claim | Source |
|---|---|
| Slash commands frontmatter-free | `.claude/commands/vdd.md`, `.claude/commands/full.md` |
| Reader scripts scan frontmatter | `check_prompt_references.py:17,50-61`, `smoke_workflows.py:36,40` |
| `check_prompt_references.py` regex fixed | TASK 095 fix — comment `check_prompt_references.py:21-29`, corrected regex `:30` |
| `vdd-adversarial` calls `03-develop-single-task` | `.agent/workflows/vdd-adversarial.md:62` |
| `vdd-05` delegates to a **fragment** of `vdd-03` (§4.5 constraint 1) | `.agent/workflows/vdd-05-run-full-task.md:15` ("Step 3") vs the loop at `vdd-03-develop.md:24` |
| `full-robust` owns two wrapper retries | `.agent/workflows/full-robust.md:42-43`, `:58-59` |
| `vdd-multi` exit conditions (source of A.3's `exit_bar`) | `.agent/workflows/vdd-multi.md:187-189` |
| `heal-issues` two-level counter (§4.3.3) | `.agent/workflows/heal-issues.md:80` (per-run 3) + `:58` (cross-run 2) |
| Exit codes 0–6 allocated, 7 free | `feedback_lib/envelope.py:20-25`, `run_feedback.py:45` |

> **Every row above was re-resolved on 2026-08-03**, and three of them had already moved: an
> unrelated edit to `vdd-adversarial.md` inserted 19 lines above the anchors, shifting `:43`→`:62`
> and `:45`→`:64` **inside the session that cited them**. This is §4.3.1's argument for markers over
> line ranges, observed rather than argued — and the reason this index is a Phase-2 re-check item,
> not a table anyone may trust on sight.
| `vdd-enhanced` calls non-VDD `01`/`02` | `vdd-enhanced.md` §1.1, §2.1 |
| `vdd-multi` `--max-iterations` default | `.agent/workflows/vdd-multi.md:190` |
| Counter non-composition text | `.agent/workflows/vdd-enhanced.md:56-58` |
| `flock` in `claims.py` | `claims.py:56` |
| Framework retry limit in docs | `System/Docs/WORKFLOWS.md:220` |

---

## Appendix C — Changelog

### rev 6 — 2026-08-03, after the rev-5 adversarial pass ([review-095-rev5-adversarial.md](../reviews/review-095-rev5-adversarial.md))

> **The pattern rev 5 named, rev 5 repeated.** Its own changelog diagnosed revs 3–4 as *"the rule
> was tightened and the data it governs was not"* — and then shipped a `site` grammar with two wrong
> locators, an `exit_bar` grammar its own A.3 value fails, and a D7 phase reversal applied to §5/§7
> but not to §3's safety invariants. Rev 6 closes 18 findings; the six HIGH ones are all instances
> of that same pattern.

| Change | Driver |
|---|---|
| **`full-robust` given a category (A.5 ×2)** — `coverage_fix_retry` and `docs_update_retry`, the two wrapper retries it owns; §1 property 2 gains the §2 wrapper row; Appendix A totals restated as **25 loops / 23 workflows** and re-added per category | C-01 — it was the only 1 of 23 workflows with no category, verbatim the defect D2 fixed for `framework-upgrade`; A.5's "across 9 workflows" was true only with it |
| **F10 applied at last** — `vdd-03-develop.dev_review_loop` moved A.2 → A.1; §4.5 gains the rule that a `partial` edge bounds what is bindable and that a wrapper retry is an owned loop; the ownership note's denominator corrected to **4 of 4** | C-02 — rev 5 claimed "3 of 3" against a review whose F10 named a fourth; A.2 now contains exactly the two rebindings §1 property 2 claims |
| **D8 — `default_max` under a judgment bar**: `null` required only under `override: required`, merely *permitted* under `judgment_terminated`/`gated_by`; R1 keeps one direction only; A.2's `adversarial_cycle` gains the `exit_bar` R10 requires | C-03 — rev 5's §4.3 forbade the exact combination its own A.2 declared, and the inventory was the correct half |
| **A.3's `exit_bar` replaced with a `grep -F`-verified substring**; §4.3.2 gains the note that the spec failed its own new grammar | C-04 — `"clean pass \| bikeshedding-only"` occurs nowhere in `vdd-multi.md` |
| **Status line and finding references made resolvable** — the cited review has **5** blocking findings (1–5), not 9, and its CRITICAL is #1 | C-05 — the readiness claim in the header was itself an ungated claim, which is E1's thesis applied to this document |
| **D7 renumbering propagated to S1, S8, S10, R6, §4.3.1, §7.2 and §7.3/E4** — S8 in particular had the rollback pair *inverted* | C-06 — a safety invariant that names the wrong revert is worse than none |
| **Counts re-added from the inventory** — 11 loops without a numeric bound, **9** getting one in Phase 2 across **7** files (~20 lines); Phase 2's "13 already-bounded" → 14; A.5 header → 14 / 9 | M-01 — four totals disagreed with the appendix they summarized; "~15 lines / 5 files" was the review's pre-D2 figure, quoted after D2 and F12 had invalidated it |
| **R3's second half given a grammar (§4.3.1)** — canonical `max <N>`, all matches in the window must agree; `BOUND_UNRESOLVABLE` / `BOUND_AMBIGUOUS`; `null` exempt; Phase 2 appends the digit form where the corpus spells a bound in words (`full-robust`'s `once` / `one`). Plus the `window` key (§4.3), added after simulating the rule on the corpus: the 12-line default makes `light-02`'s two loops share a window and false-positive | M-02 — rev 5 defined how `site` resolves and left "prose bound" undefined, so R3 still rested half on nothing |
| **§4.3.3 added — what v1 cannot express**; `heal-issues`'s illegal `3 (+ cross-run …: 2)` cell replaced by a legal value plus a stated limitation; `scope: per_item` extended to critic categories; §7.1 gains item 10 | M-03 — an Appendix-A cell held a value that is not an `int ≥ 1 \| null`, which a Phase-3 author would have copied into YAML |
| **R5's recursion exception given an edge** (self-edge paired with `recursive: true`, §4.5); **R4 scoped to the authored basename** and the three prose spellings demoted to authoring guidance; **R8 deferred to Phase 5** | M-04 / M-05 / M-06 — one exception with nothing to except, one rule contradicting R5, one with no input after D6. "A rule that cannot fail is not a rule" applies to the rule table too |
| **`framework-upgrade`'s two `site` cells corrected** to §1.3 and §2.3 | M-07 — "step 2" was the GOTO target; "step 4" was a section with no loop |
| **Five LOW corrections** — §7.3's dangling "below" / stale rev-3 verdict; `check_prompt_references.py:21` → `:21-29` + `:30`; "exit codes 7 and 8" → 7; WI-30/31/32 attributed to `onchain-analytics` (this repo's ledger uses the same `WI-<n>` namespace); `01-start-feature`'s duplicate step "4." noted at the marker site | L-01 … L-05 |

Not changed, deliberately: D1's `max = 3` (an operator judgment, unaffected by the recount — but
§7.2 now states its collision with `WORKFLOWS.md:220` and S10 states which governs); §6, which is
PROVISIONAL and rewritten at §7.1 by construction; R2, whose disposal is already §7.1 item 3.

### rev 5 — 2026-08-02, closing the review findings rev 4 left open

> **D7 accepted by the operator on 2026-08-02.** The spec is decision-complete: Phase 2 is the
> prose bounds alone, and nothing in Phases 1–4 is now waiting on a call. The reversal is a phase
> order, not an architecture change — reverting it means re-ordering §7 and restoring
> `pending_bound`, both single edits.

Rev 4 addressed all five **blocking** findings of `review-095-independent.md` and most of its
F1–F24 corrections — several better than asked (S2 became an authoring constraint rather than a
restated claim). What rev 5 closed was the residue in Themes A–D and the Scope challenge, which had
one shape in common: **the rule was tightened and the data it governs was not.**

> **Reference note added in rev 6.** The drivers below originally read "Finding 6 / 8 / 9". The
> cited review has **five** blocking findings, numbered 1–5, whose CRITICAL is #1 — those numbers
> resolved to nothing, and the status line built on them ("6 of the 9") was the same ungated claim
> E1 describes. Each driver is re-pointed at the anchor it actually rests on.

| Change | Driver |
|---|---|
| **`site` given a canonical grammar (§4.3.1)** — marker or line range, no third form, no "or section anchor" fallback; `SITE_UNRESOLVABLE` is an error. R3's negative fixture made a Phase deliverable, and its passing made a CI failure | **Blocking finding 1** (R3 vacuity, the CRITICAL) — rev 4 fixed R3's wording but left the escape hatch in §4.3 and free-form prose in every Appendix A `Site` cell |
| **Appendix A `Site` column converted to real locators** — all rows carry the loop `id` and the exact `site` string to author | **Blocking finding 1** — a Phase-3 author copying rev 4's table would have written sites that resolve to nothing (two still did; corrected in rev 6, M-07) |
| **`exit_bar` given the same treatment (§4.3.2)** — a verbatim substring quoted from the body at `site`, which the validator must find | **Theme A**, bullet *"`judgment_terminated` + `exit_bar` is an unpoliced escape hatch"* — "non-empty" is satisfied by `"until done"` |
| **Ship order reversed (D7, §2, §7)** — prose bounds ship first and alone as Phase 2; A and B ship together after; `pending_bound` deleted as obviated; §2 stops calling A "valuable alone" | **Scope challenge** + **blocking finding 5** — the measured one, untouched by rev 4 |
| **Third double-count removed** — `vdd-enhanced` §4.3 was in A.5 as an owned loop while A.2 records it as the rebind of `vdd-adversarial.adversarial_cycle`; A.5 count 13 → 12 | **F8 / F9 / F10** — rev 4 corrected 2 of the 4 sites, rev 5 a 3rd while claiming "3 of 3"; F10 waited for rev 6. **4 of 4 now** |
| **Phase-5 entry gate restored and extended, 5 → 9 questions** — the two dropped by the rev-4 compression were `gates[]`-worth-it and `claims.py`/`envelope.py` drift, i.e. the two that can conclude against Component C | Regression introduced by rev 4's compression; D5 rests on this gate |
| **Field evidence restored (§7.3)** — WI-30/WI-31, including the three ways a green verdict was produced without verification | Regression introduced by rev 4's compression. It contains the strongest argument found anywhere *for* Component C, so its loss cut against the spec's own case |

Not changed, deliberately: rev 4's fixes to S2, §1.2, `pending_bound`'s replacement of the illegal
Phase-2 state (superseded by D7 rather than reverted), `framework-upgrade`'s inventory entry, the
`loops: []` keyword heuristic, property 2's 5 → 2 correction, and the PyYAML install step.

### rev 4 — 2026-08-02, after independent review (review-095-independent.md)

| Change | Driver |
|---|---|
| **R3 anti-drift rule fixed**: Eliminated vacuous "anywhere in body" digit matching; required `site` locators (`line:NN-MM` or `<!-- loop:<id> -->`) and negative test fixtures | Finding 1 in `review-095-independent.md` |
| **S2 invariant corrected**: Re-derived S2 enumerating all script/LLM readers (`check_prompt_references.py`, `smoke_workflows.py`, `installer/`, `vendors.yaml`, LLMs) and restated parser non-collision safety | Finding 2 in `review-095-independent.md` |
| **Phase 2 state & gate fixed**: Introduced temporary `pending_bound: N` for Phase 2; replaced empty WARN list comparison with `docs/design/095-phase2-expected-warnings.txt` verified via `diff -q` | Finding 3 in `review-095-independent.md` |
| **Complete workflow inventory**: Added `framework-upgrade.md` (2 loops) and `vdd-05` Builder loop to Appendix A; added validator heuristic warning for `loops: []` on bodies containing retry keywords | Finding 4 in `review-095-independent.md` |
| **Call graph & spellings updated**: Added `vdd-adversarial` → `03-develop-single-task` edge; documented 3 invocation syntax spellings; distinguished sub-workflow calls from escalations/handoffs | F4 & F5 in `review-095-independent.md` |
| **Schema & rule enhancements**: Added `calls[].kind`, `partial`, `suppresses`; added R12 (`binds` key validation); updated CI job names (`tooling-tests`, `skill-validate`, `reference-integrity`, `security-lint`, `workflow-smoke`) | Themes A–D & F18–F19 in `review-095-independent.md` |
| **Inventory double-counting fixed**: Corrected `full-robust` §3 rebind attribution and `05-run-full-task` row; updated line number citations in Appendix B | F6–F17 in `review-095-independent.md` |

### rev 3 — 2026-08-02, after operator review round 2
Operator review additions (D5, D6, §7.1 entry gate).

### rev 2 — 2026-08-02, after operator review round 1
Enum `override`, `judgment_terminated`, `gated_by: hitl`, `contract.gates[]`.

### rev 1 — 2026-08-02
Initial draft.
