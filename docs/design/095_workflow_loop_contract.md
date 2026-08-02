# Design Spec 095 — Workflow Loop Contract & Run Frame Stack

**Status:** DRAFT rev 5 — rev 4 closed 6 of the 9 blocking review findings; rev 5 closes the remaining 3 ([review-095-independent.md](../reviews/review-095-independent.md)).
**Author:** Orchestrator (self-improvement mode)
**Date:** 2026-08-02
**Supersedes:** DRAFT rev 4. **Blocks:** nothing.
**Prime constraint:** *do not break the current framework.* Every element below is additive,
inert-by-default, and revertible with a single `git revert`. See §3.
**Decisions applied:** D1–D7 in §8 — **decision-complete**. D7 (ship order reversed) accepted by the
operator 2026-08-02. Changelog in Appendix C.

---

## 1. Problem statement

The framework's orchestration layer is not a flat state machine. It is a **hierarchical,
composable protocol** with five properties that no existing artifact records mechanically:

1. **A call stack up to 5 deep.**
   `full-robust` → `vdd-enhanced` → `05-run-full-task` → `03-develop-single-task` →
   developer↔reviewer loop.

2. **Caller-side rebinding of callee bounds.** A sub-workflow declares an open-ended loop; the
   caller closes it at the call site. Two genuine caller-side rebindings exist today (with three additional caller wrapper or skip mechanisms):

   | Caller | Callee | Mechanism / Rebinding |
   |---|---|---|
   | `full-robust` §3 | `security-audit` §4c | Genuine rebind: `"until clean"` → `no CRITICAL/HIGH`, **max 3 iterations** |
   | `vdd-enhanced` §4 | `vdd-adversarial` | Genuine rebind: **max 3** adversarial cycles |
   | `full-robust` §2 | `vdd-multi` | Caller flag: passes `--no-fix`, callee skips Phase 3 fix loop entirely |
   | `full-robust` §4 | `04-update-docs` | Caller-owned wrapper: **one** retry around single-pass sub-workflow |
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

**Twelve loops have no bound in the workflow that owns them.** Some are bounded only when reached
through a specific caller; invoked directly they run unbounded. Full inventory in Appendix A.

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
| `03-develop-single-task` | `05-run-full-task`, `full-robust`, `vdd-enhanced`, **`vdd-adversarial`** (`.agent/workflows/vdd-adversarial.md:43`) |
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
3. ``Call workflow `<name>` `` (e.g. `.agent/workflows/vdd-adversarial.md:43`)

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

**The defect in §1.1 is closed by prose, not by any component.** Twelve loops need a bound
written where they live: roughly fifteen lines across five files, in the idiom
`.agent/workflows/01-start-feature.md:11-12` already uses. That work is **Phase 2** and it stands entirely alone.
Rev 3 shipped it *after* 23 files of frontmatter and a CI gate, and justified the ordering by
calling frontmatter "the highest-value / lowest-risk step" — the independent review refuted that
by measurement (~700–850 new lines to protect ~15). See **D7**.

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
| **S1** | **Additive only.** No existing line of any workflow, prompt, or skill is deleted or reworded. | Component A appends frontmatter keys. Components B and C are new files. Phase 3 edits prose **only where a bound is added**. |
| **S2** | **Frontmatter parser safety & regex non-collision.** | All 23 workflows already contain YAML frontmatter (`description:`). Frontmatter additions MUST be valid YAML and MUST NOT introduce string values containing `Call /name` or `System/Agents/*.md` to prevent false matches in script scanners (`smoke_workflows.py`, `check_prompt_references.py`, installer scripts, `vendors.yaml`, and LLM harnesses). |
| **S3** | **No new runtime dependency.** | Runtime scripts (`run_stack.py`) use Python stdlib only (`json`, `fcntl`, `os`, `time`). CI validator (`check_loop_contract.py`) may use `PyYAML==6.0.3` (pinned in `requirements-dev.txt`) with an explicit pip install step in CI. |
| **S4** | **Warn-only first.** | Component B ships returning exit 0 with `WARN:` lines, flipping to exit 1 only in Phase 4. |
| **S5** | **Component C is opt-in per workflow.** | Workflows not calling `run_stack.py` remain byte-identical in behavior. |
| **S6** | **Fail-open at runtime.** | If `run_stack.py` is missing, unreadable, or errors, the workflow logs a warning and continues using prose bounds. |
| **S7** | **Zero new gitignore/installer surface.** | State lives in `.agent/sessions/stack.json` (already ignored by `.gitignore`). |
| **S8** | **Rollback in reverse phase order.** | Reverting Phase 3 restores prose; reverting Phase 2 removes frontmatter; reverting Phase 5 removes Component C. |
| **S9** | **`latest.yaml` schema is untouched.** | Frame stack uses sibling file `.agent/sessions/stack.json`. |
| **S10** | **No existing bound value is changed.** | Phase 3 only *adds* bounds where missing; it never alters existing numeric caps. |

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
| `default_max` | int ≥ 1 \| `null` | yes | Numeric cap applied when no caller overrides it. Must be `null` if `override: required`, `judgment_terminated: true`, or `gated_by: hitl`. |
| `override` | `forbidden` \| `allowed` \| `required` | no, default `forbidden` | Caller-side rebinding policy. See §4.4. |
| `scope` | `per_run` \| `per_item` \| `global` | no, default `per_run` | Counter scope. `per_item` = counter resets per task/finding. |
| `on_exhaust` | `escalate_user` \| `stop_success` \| `warn_continue` \| `needs_human` | yes | Declared escalation path. |
| `recursive` | bool | no, default `false` | Loop re-enters this same workflow. |
| `judgment_terminated` | bool | no, default `false` | Loop terminates via structured verdict against a written bar. Requires non-empty `exit_bar`. |
| `exit_bar` | string | required when `judgment_terminated: true` | Written termination condition / verifiable citation. |
| `gated_by` | `hitl` | no | Every iteration requires blocking human decision. |

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

**Ordering consequence, stated because it bit rev 4.** The markers do not exist yet — the corpus
carries none. So a `site` cannot be authored before the marker it names is inserted, which makes
**marker insertion part of the same phase that writes the contract**, not a later cleanup. §7
sequences it accordingly; R3 is enforced from the phase in which both the marker and the bound
are present, and is listed against that phase in §5.2 rather than an earlier one.

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

### 4.4 The `override` enum

| `override` | Meaning | `default_max` | Caller `binds` entry |
|---|---|---|---|
| `forbidden` | Workflow owns bound outright. Caller may not rebind. | must be an int (or `null` with `judgment_terminated`/`gated_by`) | Error (R9) |
| `allowed` | Workflow has default; caller **may** re-scope. | int, or `null` with `judgment_terminated`/`gated_by` | Optional |
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
| **R1** | `default_max: null` requires `override: required`, `judgment_terminated: true`, or `gated_by: hitl`. Otherwise error. | error | 3 | Eliminates un-bounded loops. Phase 2 has already written every prose bound, so there is no transitional state to accommodate — see D7. |
| **R2** | `override: required` loops must be bound by all non-optional caller edges. | error | 3 | Ensures required overrides are supplied. |
| **R3** | Frontmatter `default_max` must match prose bound within the anchored `site` window (`line:NN-MM` or `<!-- loop:<id> -->`). Negative test fixture required. | error | 3 | Prevents frontmatter/prose drift. |
| **R4** | All `calls[].workflow` entries must resolve to existing workflow files across all 3 call syntax spellings (`Call /x`, `Execute .agent/workflows/x.md`, ``Call workflow `x```). | error | 3 | Ensures call graph integrity. |
| **R5** | `calls` graph must be acyclic (except explicit `recursive: true` loops). Graph built from authored `calls` lists only. | error | 3 | Prevents unintended workflow call recursion. |
| **R6** | Every workflow MUST contain a `contract:` block with `version` and `loops` (Phase 2). | error | 3 | Forces explicit declaration across all workflows. |
| **R7** | `on_exhaust` required on every loop. | error | 3 | Mandates escalation path. |
| **R8** | `scope: per_run` loops inside list-iterating workflows generate warning if unnoted. | **warn** | 3 | Prevents counter scoping confusion. |
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
| **2** | **Close §1.1.** Write the missing bound + escalation path in the prose of the 12 unbounded loops; and insert the `<!-- loop:<id> -->` marker at **every** loop site in Appendix A — including the 13 already-bounded ones, whose marker is all Phase 2 owes them | Every loop in Appendix A.1/A.2 has a bound and an `on_exhaust` in its own body; `smoke_workflows.py` green. **No frontmatter, no new script, no CI job** | `git revert` |
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
| 6 | **Have `claims.py`, `heal-state.json`, or `envelope.py` changed?** §6 copies the first two and assumes exit codes 7 and 8 are free. | Any drift there invalidates the corresponding part of §6 outright. Re-check, do not assume. |
| 7 | **Is `contract.gates[]` still worth it?** Count completion announcements (`✓` lines) and how often one was emitted after a skipped or failed gate. | Zero observed false claims → drop `gates[]`, R11 and `claims --verify`; keep C's counters only. |
| 8 | **Did the workflow set change?** New workflows, renamed ones, new callers. | Re-run §1.2; Appendix A categories may move. |
| 9 | **Multi-agent dispatch:** does a frame stack survive parallel critics (`vdd-multi`, `skill-parallel-orchestration` §1.1)? | `per_run` vs `per_item` scope is incoherent if three critics share one frame. May force a schema change before C. |

**If items 1 and 7 both come back empty** — no drift, no false completion claims — the honest
outcome is to ship a **smaller** C than §6 describes, or to record that Phases 2–4 sufficed. That
is a legitimate result of this gate, not a failure of it: the framework's own precedent is to not
build automation whose need has not been demonstrated (`heal-issues` §Scheduling). Items 6 and 7
were dropped in the rev-4 compression and are restored here, because they are the two that can
conclude *against* Component C, and a gate that can only ratify is not a gate.

### 7.2 Downstream Integration & Documentation Sync
- **Downstream Framework Installs:** Installer scripts resolve symlinks in `.agent/workflows/` and detect project-local overrides (`LOCAL_OVERRIDE`).
- **Documentation Sync:** `System/Docs/WORKFLOWS.md` (specifically line 220 retry limits and call maps) MUST be updated in lockstep during Phase 3.

---

### 7.3 Field evidence — arrived before Phase 2, from a different direction (TASK 095)

§7.1 asks Phases 2–4 for evidence. Some arrived first, unasked, from a downstream project running
`/vdd` on Russian-language artifacts (work-items WI-30 / WI-31 / WI-32, 2026-08-02). It bears on
this spec's **Component C** and is recorded here so the Phase-5 gate answers from a record rather
than from recollection. **None of it is a decision.** Nothing in this section commits Phase 5 to
anything; see the independent review below, which concludes rev 3 is not ready to build from.

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

This matters to *this spec* for a reason beyond the anecdote: **§7's Phase-2 exit gate cites
`check_prompt_references.py` still being green as evidence that frontmatter is inert.** That gate
was green by construction. Any Phase-2 evidence resting on it must be re-gathered after the fix.

## 8. Decisions — operator review rounds 1–2, independent review round 3

| # | Question | Decision | Consequence |
|---|---|---|---|
| **D1** | Bounds for unbound loops | **`max = 3` accepted** across Category 1 and 2 | 3 VDD entrypoints gain cap 3; 3 gain default cap 3 matching caller bind; Category 3 & 4 remain `null`. |
| **D2** | `framework-upgrade` GOTO loops | In scope. Two loops in Appendix A.1; both get a bound in **Phase 2** like every other Category-1 loop | Rev 3 put them out of scope, which left `framework-upgrade` the only workflow of 23 with no category — the state the review's finding 5 named. |
| **D3** | `contract.gates[]` | Ship with Component C in Phase 5 | Kept out of Phase 2 frontmatter. |
| **D4** | Document language | **English** | Standard across design docs. |
| **D5** | Does Component C ship? | **Yes — committed**, but re-derived in §7.1 | Phase 5 gated by §7.1 re-derivation. |
| **D6** | Is list iteration a loop? | **No** — `for-each` over finite list is not a retry loop | `loops[]` tracks retries only. |
| **D7** | Ship order: does Component A go before or after the prose bounds? | **ACCEPTED 2026-08-02 — prose bounds first, alone (Phase 2). A and B ship together, after.** | Reverses rev 3/rev 4. The independent review measured it: the §1.1 defect is 12 loops needing ~15 lines in 5 files, while A+B is ~700–850 new lines across 23 files plus a CI job. Rev 3 called frontmatter *"the highest-value / lowest-risk step"*; on the measurement the inverse holds. Two consequences fall out: `pending_bound` disappears (it existed only to make a legal declaration possible *before* the bounds were written), and A stops being described as valuable alone — §4.6's own over-engineering test says it is not. |

---

## 9. Explicitly out of scope
- Statechart DSLs or FSM engines.
- XML prompt markup.
- Modifying existing numeric bounds.
- Altering `latest.yaml` schema.

---

## Appendix A — Loop inventory (23 workflows)

> **The `Site` column is a contract, not a description.** Rev 3 filled it with prose
> (`"§4c"`, `"Step 2D"`) and the review verified that **none** of those strings occur in the files
> they name — so a Phase-3 author copying this table would have authored `site` values that
> resolve to nothing, and R3 would pass on all of them. Each row now carries the loop's `id` and
> the exact `site` value to write. The `<!-- loop:<id> -->` markers do not exist in the corpus
> yet; **inserting them is part of Phase 2**, in the same edit that writes the bound (§4.3.1).

### A.1 Category 1 — Copy-drift / missing bounds (6 loops across 4 workflows)

| Workflow | Site | Today | Decision |
|---|---|---|---|
| `vdd-01-start-feature` | `task_review`<br/>`site: "<!-- loop:task_review -->"` — marker inserted at step 4 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-01-start-feature` | `arch_review`<br/>`site: "<!-- loop:arch_review -->"` — marker inserted at step 5 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-02-plan` | `plan_review`<br/>`site: "<!-- loop:plan_review -->"` — marker inserted at step 3 in Phase 2 | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `framework-upgrade` | `spec_audit_retry`<br/>`site: "<!-- loop:spec_audit_retry -->"` — marker inserted at step 2 in Phase 2 | *"If Audit fails, GOTO Step 2"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `framework-upgrade` | `plan_audit_retry`<br/>`site: "<!-- loop:plan_audit_retry -->"` — marker inserted at step 4 in Phase 2 | *"If Audit fails, GOTO Step 2"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-05-run-full-task` | `builder_red_loop`<br/>`site: "<!-- loop:builder_red_loop -->"` — marker inserted at step 2 in Phase 2 | *"Red tests force a Builder loop"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |

### A.2 Category 2 — Default + caller override (3 loops)

| Workflow | Site | Caller bind today | Decision |
|---|---|---|---|
| `vdd-03-develop` | `dev_review_loop`<br/>`site: "<!-- loop:dev_review_loop -->"` — marker inserted at step 4 in Phase 2 | `vdd-05` step 2D: Max 3 | `default_max: 3`, `override: allowed` |
| `vdd-adversarial` | `adversarial_cycle`<br/>`site: "<!-- loop:adversarial_cycle -->"` — marker inserted at step 2b in Phase 2 | `vdd-enhanced` §4.3: max 3 | `default_max: 3`, `override: allowed`, `recursive: true`, `judgment_terminated: true` |
| `security-audit` | `audit_remediation`<br/>`site: "<!-- loop:audit_remediation -->"` — marker inserted at step 4c in Phase 2 | `full-robust` §3: Max 3 + redefined exit bar | `default_max: 3`, `override: allowed` |

### A.3 Category 3 — Judgment-terminated (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `vdd-multi` | `multi_fix_loop`<br/>`site: "<!-- loop:multi_fix_loop -->"` — marker inserted at Phase 3 in Phase 2 | `default_max: null`, `override: allowed`, `judgment_terminated: true`, `exit_bar: "clean pass \| bikeshedding-only"` |

### A.4 Category 4 — HITL-gated (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `iterative-design` | `design_iteration`<br/>`site: "<!-- loop:design_iteration -->"` — marker inserted at Phase 5 step 7 in Phase 2 | `default_max: null`, `override: forbidden`, `gated_by: hitl` |

### A.5 Category 5 — Already bounded (12 loops across 9 workflows)

| Owner | Site | `default_max` | `override` | `on_exhaust` |
|---|---|---|---|---|
| `01-start-feature` | `task_review`<br/>`site: "<!-- loop:task_review -->"` — at step 4 | 2 | forbidden | escalate_user |
| `01-start-feature` | `arch_review`<br/>`site: "<!-- loop:arch_review -->"` — at step 5 | 2 | forbidden | escalate_user |
| `02-plan-implementation` | `plan_review`<br/>`site: "<!-- loop:plan_review -->"` — at step 3 | 2 | forbidden | escalate_user |
| `03-develop-single-task` | `dev_review`<br/>`site: "<!-- loop:dev_review -->"` — at step 4 | 2 | forbidden | escalate_user |
| `05-run-full-task` | `task_retry`<br/>`site: "<!-- loop:task_retry -->"` — at step 3 | 2 | forbidden | escalate_user |
| `light-02-develop-task` | `light_fix_loop`<br/>`site: "<!-- loop:light_fix_loop -->"` — at §1.5 | 3 | forbidden | escalate_user |
| `light-02-develop-task` | `light_review_loop`<br/>`site: "<!-- loop:light_review_loop -->"` — at §2.4 | 2 | forbidden | escalate_user |
| `vdd-05-run-full-task` | `dev_delegate_loop`<br/>`site: "<!-- loop:dev_delegate_loop -->"` — at step 2D | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `task_validate_retry`<br/>`site: "<!-- loop:task_validate_retry -->"` — at §1.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `plan_validate_retry`<br/>`site: "<!-- loop:plan_validate_retry -->"` — at §2.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | `regression_retry`<br/>`site: "<!-- loop:regression_retry -->"` — at §3.2 | 2 (`scope: per_run`) | forbidden | escalate_user |
| `heal-issues` | `heal_attempt_loop`<br/>`site: "<!-- loop:heal_attempt_loop -->"` — at Phase 2 | 3 (+ cross-run `max_attempts_per_issue: 2`) | forbidden | needs_human |

*(Ownership note — a loop the callee declares belongs to the callee's `loops[]` and appears in the
caller only as `binds`. Three rows violated that and are recorded elsewhere, not here:
`full-robust` §3 rebinds `security-audit.audit_remediation` → §A.2;
`vdd-enhanced` §4.3 rebinds `vdd-adversarial.adversarial_cycle` → §A.2;
`full-robust` §4 wraps `04-update-docs`, which owns no loop → `calls[]`.
Rev 4 corrected the first and third; the second was found on re-review — **3 of 3 now**.)*

### A.6 Category 6 — No retry loops (`loops: []`, 6 workflows)

`04-update-docs`, `base-stub-first`, `light-01-start-feature`, `product-full-discovery`, `product-market-only`, `product-quick-vision`.

---

## Appendix B — Evidence index

| Claim | Source |
|---|---|
| Slash commands frontmatter-free | `.claude/commands/vdd.md`, `.claude/commands/full.md` |
| Reader scripts scan frontmatter | `check_prompt_references.py:17,50-61`, `smoke_workflows.py:36,40` |
| `check_prompt_references.py` regex fixed | TASK 095 fix (`check_prompt_references.py:21`) |
| `vdd-adversarial` calls `03-develop-single-task` | `.agent/workflows/vdd-adversarial.md:43` |
| `vdd-enhanced` calls non-VDD `01`/`02` | `vdd-enhanced.md` §1.1, §2.1 |
| `vdd-multi` `--max-iterations` default | `.agent/workflows/vdd-multi.md:190` |
| Counter non-composition text | `.agent/workflows/vdd-enhanced.md:56-58` |
| `flock` in `claims.py` | `claims.py:56` |
| Framework retry limit in docs | `System/Docs/WORKFLOWS.md:220` |

---

## Appendix C — Changelog

### rev 5 — 2026-08-02, closing the review findings rev 4 left open

> **D7 accepted by the operator on 2026-08-02.** The spec is decision-complete: Phase 2 is the
> prose bounds alone, and nothing in Phases 1–4 is now waiting on a call. The reversal is a phase
> order, not an architecture change — reverting it means re-ordering §7 and restoring
> `pending_bound`, both single edits.

Rev 4 closed six of the nine blocking findings — several better than asked (S2 became an
authoring constraint rather than a restated claim). Three had the same shape left over: **the rule
was tightened and the data it governs was not.**

| Change | Driver |
|---|---|
| **`site` given a canonical grammar (§4.3.1)** — marker or line range, no third form, no "or section anchor" fallback; `SITE_UNRESOLVABLE` is an error. R3's negative fixture made a Phase deliverable, and its passing made a CI failure | Finding 1 — rev 4 fixed R3's wording but left the escape hatch in §4.3 and free-form prose in every Appendix A `Site` cell |
| **Appendix A `Site` column converted to real locators** — all 23 rows now carry the loop `id` and the exact `site` string to author | Finding 1 — a Phase-3 author copying rev 4's table would have written sites that resolve to nothing |
| **`exit_bar` given the same treatment (§4.3.2)** — a verbatim substring quoted from the body at `site`, which the validator must find | Finding 6 — "non-trivial, verifiable" had no grammar, and A.3's own value was a bare string |
| **Ship order reversed (D7, §2, §7)** — prose bounds ship first and alone as Phase 2; A and B ship together after; `pending_bound` deleted as obviated; §2 stops calling A "valuable alone" | Finding 9 — the CRITICAL one, untouched by rev 4. ~15 lines close §1.1; A+B is ~700–850 |
| **Third double-count removed** — `vdd-enhanced` §4.3 was in A.5 as an owned loop while A.2 records it as the rebind of `vdd-adversarial.adversarial_cycle`; A.5 count 13 → 12 | Finding 8 — rev 4 corrected 2 of the 3 sites; **3 of 3 now** |
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
