# Design Spec 095 — Workflow Loop Contract & Run Frame Stack

**Status:** DRAFT rev 3 — operator review rounds 1–2 applied; **decision-complete**. Nothing implemented.
**Author:** Orchestrator (self-improvement mode)
**Date:** 2026-08-02
**Supersedes:** nothing. **Blocks:** nothing.
**Prime constraint:** *do not break the current framework.* Every element below is additive,
inert-by-default, and revertible with a single `git revert`. See §3.
**Decisions applied:** D1–D6 in §8 — no open questions remain. Changelog in Appendix C.

---

## 1. Problem statement

The framework's orchestration layer is not a flat state machine. It is a **hierarchical,
composable protocol** with five properties that no existing artifact records mechanically:

1. **A call stack up to 5 deep.**
   `full-robust` → `vdd-enhanced` → `05-run-full-task` → `03-develop-single-task` →
   developer↔reviewer loop.

2. **Caller-side rebinding of callee bounds.** A sub-workflow declares an open-ended loop; the
   caller closes it at the call site. Five instances exist today, all in prose:

   | Caller | Callee | What the caller rebinds |
   |---|---|---|
   | `full-robust` §3 | `security-audit` §4c | `"until clean"` → `no CRITICAL/HIGH`, **max 3 iterations** |
   | `full-robust` §2 | `vdd-multi` | coverage gate → materialize fixes, **re-run once** |
   | `full-robust` §4 | `04-update-docs` | **one** retry of the failed sub-step |
   | `vdd-enhanced` §3 | `05-run-full-task` | **max 2** fix-and-rerun rounds *total* |
   | `vdd-enhanced` §4 | `vdd-adversarial` | **max 3** adversarial cycles |

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

**Ten loops have no bound in the workflow that owns them.** Some are bounded only when reached
through a specific caller; invoked directly they run unbounded. Full inventory in Appendix A.

The most significant finding is not random scatter but a **systematic regression in the VDD
family** — the VDD variants dropped the bounds their non-VDD twins have:

| Non-VDD workflow | Bound | VDD twin | Bound |
|---|---|---|---|
| `01-start-feature` step 4 (TASK review) | Max 2 attempts → STOP | `vdd-01-start-feature` step 4 | *"repeat the review"* — **none** |
| `01-start-feature` step 5 (ARCH review) | Max 2 attempts → STOP | `vdd-01-start-feature` step 5 | *"repeat the review"* — **none** |
| `02-plan-implementation` step 3 | Max 2 attempts → STOP | `vdd-02-plan` step 3 | *"repeat the review"* — **none** |
| `03-develop-single-task` step 4 | Max 2 attempts → STOP | `vdd-03-develop` step 4 | *"Go to Step 2.1"* — **none** |

The invariant asserted in `full-robust`'s header — *"Every retry loop is **bounded** with an
explicit escalation path"* — holds only inside that call tree.

### 1.2 The call graph (load-bearing for §8 D1)

Derived from every `.agent/workflows/<name>.md` reference inside each workflow body.

| Callee | Callers (in-degree) |
|---|---|
| `01-start-feature` | `base-stub-first`, `light-01-start-feature`, `light-02-develop-task`, **`vdd-enhanced`** |
| `02-plan-implementation` | `base-stub-first`, **`vdd-enhanced`** |
| `03-develop-single-task` | `05-run-full-task`, `full-robust`, `vdd-enhanced` |
| `05-run-full-task` | `base-stub-first`, `vdd-enhanced` |
| `04-update-docs` | `full-robust` |
| `security-audit` | `full-robust` |
| `vdd-multi` | `full-robust` |
| `vdd-enhanced` | `full-robust` |
| `vdd-adversarial` | `vdd-enhanced` |
| `vdd-03-develop` | `vdd-05-run-full-task` |
| `light-02-develop-task` | `light-01-start-feature` |
| **`vdd-01-start-feature`** | **none** |
| **`vdd-02-plan`** | **none** |
| **`iterative-design`** | **none** |
| **`framework-upgrade`**, **`heal-issues`**, **`product-*`** | **none** |

Two consequences that shape the whole design:

- **`vdd-enhanced` calls the NON-VDD `01-start-feature` / `02-plan-implementation`**, not the
  VDD variants. Therefore `vdd-01-start-feature` and `vdd-02-plan` have **no caller at all** —
  they exist only as the `/vdd-start-feature` and `/vdd-plan` entrypoints. A
  `override: required` declaration is meaningless for them; they must own their bound.
- Every workflow except `light-02-develop-task` has a slash command in `.claude/commands/`, so
  **every workflow is directly invocable**. A loop bounded only by its caller is therefore
  unbounded on its own entrypoint. This is why category 2 in Appendix A needs *both* a default
  and an override.

> **Correction to R5 (see §5.2):** the table above was machine-derived by path-mention, which
> reports a false cycle `vdd-03-develop` ↔ `vdd-05-run-full-task`. The back-edge is a footer
> **documentation pointer** (*"Для прогона всей цепочки задач — см. `/vdd-develop-all`"*), not a
> call. `contract.calls[]` therefore means **invokes**, never **mentions**, and the validator
> reads the authored list — it must not derive the graph by grepping paths.

### 1.3 What is explicitly NOT the problem

- **Not a missing FSM diagram.** A flat state table cannot express caller-side rebinding
  (property 2) or counter scoping (property 3). Adding one would document less than the prose does.
- **Not a format problem.** XML instruction blocks are rejected: the difficulty is composition
  semantics, which markup does not address, and XML tagging is an Anthropic-specific prompting
  convention — adopting it would *reduce* vendor neutrality, which is the framework's stated goal.
- **Not enforcement-by-prose.** The framework already discovered empirically that the only
  binding enforcement is a **process exit code** (`validate.py`, `flock`, `diff -q`,
  `claim` → 6). Prose bounds are documentation, not invariants.

---

## 2. Design principle

> **The exit code is the vendor-agnostic interface.**

Everything specified here reduces to files that any runtime can read and scripts that any
runtime can run. No component depends on a model capability, a subagent primitive, or a
vendor's prompt format. A bound becomes real when a script can refuse.

Three components, each valuable alone:

| # | Component | Kind | Effect if the others never ship |
|---|---|---|---|
| **A** | Loop Contract — machine-readable frontmatter in each workflow | Declaration | Documentation improves; nothing changes at runtime |
| **B** | `check_loop_contract.py` — CI/dev-time validator | Gate | Undeclared and unbound loops fail CI |
| **C** | `run_stack.py` — runtime frame stack, counters, gate outcomes | Enforcement | Bounds become refusable; completion claims become verifiable |

Ship order is **A → B → C**. B is worthless without A. **`contract.gates[]` (§4.6) ships with C,
never before** — per decision D3 it is defined here so C has a schema to consume, but it is not
part of Phase 2.

**All three are committed** (D5). §6 and §4.6 are nevertheless marked **provisional**: they are
designed against the framework as it stands today, and Phases 2–4 will produce the first real
evidence about drift rate, which bounds actually exhaust, and whether the schema survives contact
with authors. Component C is therefore re-derived from that evidence at the Phase-5 entry gate
(§7.1) before a line of it is written.

---

## 3. Safety invariants (the "do not break" contract)

Every one of these is a requirement on the implementation, verifiable at review time.

| # | Invariant | How it is guaranteed |
|---|---|---|
| **S1** | **Additive only.** No existing line of any workflow, prompt, or skill is deleted or reworded. | Component A appends frontmatter keys. Components B and C are new files. The one exception is Phase 3, which edits prose **only where a bound is added**, and only for the loops the operator approved in D1. |
| **S2** | **Frontmatter is inert for every consumer.** | Verified: `.claude/commands/*.md` are thin wrappers with **no frontmatter of their own** that merely say *"Read and execute the workflow defined in `.agent/workflows/X.md`"* — the workflow file is never parsed as a slash-command definition. The only reader of `.agent/workflows/*.md` today is `System/scripts/smoke_workflows.py`, which regex-matches the **body** (`CALL_RE`) and ignores frontmatter. |
| **S3** | **No new runtime dependency.** | `update_state.py` hand-rolls `parse_simple_yaml`/`generate_yaml`; `.agent/rules/skill_standards.yaml` carries the explicit note *"Must be compatible with Simple 'Vanilla Python' Parser. No advanced YAML features."* Component C is stdlib-only (`json`, `fcntl`, `os`, `time`) exactly like `claims.py`. Component B may use PyYAML — it runs in CI and dev only, where `requirements-dev.txt` already pins `PyYAML==6.0.3`. |
| **S4** | **Warn-only first.** Component B ships returning exit 0 with `WARN:` lines. It flips to exit 1 only in a separate commit, after the inventory is green. | Phase gate in §7. |
| **S5** | **Component C is opt-in per workflow.** A workflow that never calls `run_stack.py` behaves **byte-identically** to today. | No workflow is edited to *require* the script in Phase 1–4. Adoption is per-workflow, one at a time, each its own commit. |
| **S6** | **Fail-open at runtime.** If `run_stack.py` is missing, unreadable, or errors, the calling workflow proceeds on its prose bound and logs one line. A broken counter must never brick a pipeline. | Mirrors the existing retro-claim rule (*"non-blocking"*) and the TTL-based stale-claim recovery in `claims.py` (`DEFAULT_TTL_HOURS = 24`). |
| **S7** | **Zero new gitignore/installer surface.** | Stack state lives at `.agent/sessions/stack.json`; `.gitignore:9` already ignores `.agent/sessions/`. `.agent/rules` and `.agent/tools` are `link_folder` in `System/scripts/vendors.yaml`, and `.agent/skills` is `link_per_item` — a new script under an existing skill propagates to every vendor with no installer change. |
| **S8** | **Single-commit rollback.** Reverting Component A leaves valid workflows (frontmatter removed, prose untouched). Reverting B removes a CI gate. Reverting C removes an unused script. | No migration, no data format change to `latest.yaml`. |
| **S9** | **`latest.yaml` schema is not modified.** The frame stack is a *sibling* file, not a new key. | Protects `skill-session-state`, `test_concurrent_state.py`, and every workflow's persist step. |
| **S10** | **No existing bound value is changed.** Phase 3 *adds* bounds where none existed (D1 categories 1–2); it never edits a number that is already there, and never tightens a documented CLI default (D1 category 3). | The inventory (Appendix A) separates "add" from "record". |

---

## 4. Component A — Loop Contract (frontmatter)

### 4.1 Placement

Extends the existing YAML frontmatter of `.agent/workflows/*.md`. Today every workflow has
exactly one key (`description:`); some have none. Both cases are handled.

### 4.2 Grammar (deliberately minimal)

Restricted to the subset the vanilla parser convention allows: block mappings, block sequences,
scalars, `null`, integers, booleans, double-quoted strings. **No** anchors, flow mappings,
multi-line scalars, or complex keys.

```yaml
---
description: Run the full robust pipeline (…)      # unchanged, still first
contract:
  version: 1
  loops:
    - id: audit_remediation
      what: "fix → re-run audit until clean"
      site: "§4c"
      default_max: 3
      override: allowed
      on_exhaust: escalate_user
  calls:
    - workflow: security-audit
      binds:
        audit_remediation:
          max: 3
          exit_bar: "no CRITICAL/HIGH findings"
---
```

### 4.3 `contract.loops[]` — every retry/iteration loop this workflow **owns**

| Key | Type | Required | Meaning |
|---|---|---|---|
| `id` | string, `snake_case`, unique in file | yes | Stable handle. Referenced by callers' `binds` and by `run_stack.py tick --loop`. |
| `what` | string | yes | One-line human description. Enables review of the declaration against the prose. |
| `site` | string | yes | Where in the body the loop lives (`"§4c"`, `"Step 2D"`). Anchors R3. |
| `default_max` | int ≥ 1 \| `null` | yes | The iteration cap **this workflow applies when nobody overrides it** — i.e. on direct slash-command invocation. `null` = this workflow states no numeric cap. |
| `override` | `forbidden` \| `allowed` \| `required` | no, default `forbidden` | Caller-side rebinding policy. See §4.4. |
| `scope` | `per_run` \| `per_item` \| `global` | no, default `per_run` | Encodes property 3 (§1). `per_item` = counter resets per task/finding. |
| `on_exhaust` | `escalate_user` \| `stop_success` \| `warn_continue` \| `needs_human` | yes | The declared escalation path. Must match the prose. |
| `recursive` | bool | no, default `false` | The loop re-enters this same workflow (`vdd-adversarial` §2b). |
| `judgment_terminated` | bool | no, default `false` | The loop's **primary** exit is a structured verdict against a written bar; any numeric cap is a backstop, not the mechanism. Requires a non-empty `exit_bar`. |
| `exit_bar` | string | only when `judgment_terminated: true` | The written termination condition, stated or cited. |
| `gated_by` | `hitl` | no | Every iteration passes through a **blocking** human gate, so the loop cannot run away unattended. Legitimizes `default_max: null`. |

> **What is not a loop (D6).** `loops[]` records **retry** constructs — re-entering the same work
> because it failed or was rejected. A `for-each` over a finite, statically-known list is **not**
> a loop and is not declared: it terminates by exhausting its input, not by a bound. The
> canonical case is `05-run-full-task` step 2, which iterates the tasks in `docs/PLAN.md`; that
> workflow declares exactly one loop (step 3's fix-and-rerun), not two. Same for `vdd-05` step 2's
> per-task chain and `vdd-multi` Phase 1's per-critic fan-out. Stated here so Phase 2 authors do
> not re-litigate it per file.

### 4.4 The `override` enum (replaces the rev-1 `bound_by_caller` boolean)

Rev 1 modelled the caller relationship as one boolean, which could not express the most common
real case: *a workflow that has its own working default **and** is legitimately re-scoped by a
caller* — `security-audit`, `vdd-adversarial`, `vdd-03-develop`. Since every one of these is also
a direct entrypoint (§1.2), it needs both. Hence one numeric key named `default_max` — the number
is a **default**, not an absolute — plus an explicit policy:

| `override` | Meaning | `default_max` | Caller `binds` entry |
|---|---|---|---|
| `forbidden` | The workflow owns this bound outright. No caller may loosen or tighten it. | must be an int, **or** `null` with `judgment_terminated`/`gated_by` | **error** (R9) |
| `allowed` | The workflow has a working default; a caller **may** re-scope it. | must be an int, **or** `null` with `judgment_terminated` | optional |
| `required` | The workflow deliberately states no cap; every caller **must** bind one. | must be `null` | **mandatory** on every non-`optional` edge (R2) |

`override: required` therefore carries exactly the rev-1 `bound_by_caller: true` semantics, and
is now one value of a 3-state enum rather than a boolean that could be combined nonsensically.

**Design note.** As of D1 no loop in the framework uses `override: required` — every
caller-parameterized loop turned out to also be an entrypoint, so `allowed` fits all of them.
The value is retained because it is the correct declaration for a future workflow that genuinely
must not be run standalone, and because R2 exists to police it.

### 4.5 `contract.calls[]` — every sub-workflow this workflow invokes

| Key | Type | Required | Meaning |
|---|---|---|---|
| `workflow` | string (basename, no `.md`) | yes | Callee. Must resolve to `.agent/workflows/<name>.md`. **Invocation only** — a documentation pointer to another workflow is not a call (§1.2 correction). |
| `binds` | mapping `loop_id → {max, exit_bar?}` | required for the callee's `override: required` loops; optional for `allowed`; error for `forbidden` | Caller-side rebinding. `exit_bar` re-states the callee's termination condition in the caller's terms. |
| `optional` | bool | no, default `false` | Call is conditional (`full-robust` §2 is opt-in). Suppresses R2 for that edge. |

**A loop the caller wraps around a call, which the callee does not itself declare, belongs in the
caller's own `loops[]`, not in `binds`.** The single instance is `full-robust` §4's one-retry
around `04-update-docs`, which has no retry loop of its own. This keeps `04-update-docs` honest
(`loops: []`) and requires no new vocabulary.

### 4.6 `contract.gates[]` — ships with Component C (Phase 5), per D3

Records the gate taxonomy that currently lives only in prose (`full-robust` header,
`vdd-enhanced` header, session decision 084). **Deliberately not part of Phase 2**: declaring
data that nothing reads is the over-engineering this design otherwise avoids. It is specified
here so that Component C has a schema to consume the moment it ships.

| Key | Type | Meaning |
|---|---|---|
| `id` | string, `snake_case` | Stable handle; referenced by `run_stack.py gate --id`. |
| `site` | string | Where in the body the gate is stated. |
| `kind` | `script` \| `review_verdict` \| `hitl` \| `non_blocking` | See below. |
| `command` | string | required when `kind: script` — the command whose exit code is the gate. |
| `bar` | string | required when `kind: review_verdict` — the **written** objective bar, stated or cited. |
| `claims` | string | optional — the token this gate contributes to a completion announcement (e.g. `"Security ✓"`). |

| `kind` | Definition | Example |
|---|---|---|
| `script` | Deterministic process exit code / test run | `validate.py --mode task` |
| `review_verdict` | Structured PASS/FAIL against a **written** objective bar | `vdd-adversarial` Objective Convergence |
| `hitl` | Human decision required; no automated pass | `vdd-05` §3 inter-task gate |
| `non_blocking` | May fail without changing the workflow's outcome | Retro (Global Protocol) |

**Why it earns its place only alongside C.** With `run_stack.py gate --id X --outcome …` writing
per-frame gate outcomes, the `claims` key makes a completion announcement *verifiable*:
`full-robust`'s final line `VDD ✓ · Coverage ✓|skipped · Security ✓ · Docs ✓` can be checked
against recorded outcomes, so a ✓ with no recorded gate outcome is a detectable false claim.
That is the same class of defect `vdd-enhanced` §4.5 currently has to close in prose
(*"Cap reached with an orchestrator-applied fix still un-reviewed → the verdict is **WARNING,
never PASS**"*). Without C, `gates[]` is inert documentation and must not ship.

### 4.7 Worked example — `vdd-adversarial.md`

Current frontmatter:
```yaml
---
description: VDD Adversarial Refinement
---
```

Proposed (prose body untouched in Phase 2; Phase 3 adds the "max 3" sentence per D1):
```yaml
---
description: VDD Adversarial Refinement
contract:
  version: 1
  loops:
    - id: adversarial_cycle
      what: "critique → fix → re-critique (recursive self-call)"
      site: "Step 2b"
      default_max: 3
      override: allowed
      recursive: true
      judgment_terminated: true
      exit_bar: "Objective Convergence — full test run executed, 0 CRITICAL, no legitimate logic/security/slop findings, only bikeshedding remains"
      on_exhaust: escalate_user
  calls:
    - workflow: 03-develop-single-task
---
```

This declaration makes the defect machine-visible and then closes it: the primary exit stays
Objective Convergence (unchanged behaviour), `vdd-enhanced`'s existing `max: 3` bind is now
explicit rather than prose-only, and direct `/vdd-adversarial` invocation — which today has no
cap whatsoever — inherits the same 3 as a backstop.

### 4.8 A negative declaration is still a declaration

Workflows with no loops must write `loops: []`. That empty list is a **falsifiable claim** a
reviewer can check against the body. Absence of the key is a validator error (R6), not a pass.

---

## 5. Component B — `check_loop_contract.py`

### 5.1 Placement

`System/scripts/check_loop_contract.py`, alongside `validate_skills.py`,
`check_prompt_references.py`, `security_lint.py`, `smoke_workflows.py`.

**Not** merged into `smoke_workflows.py`: that script is already wired into the
`workflow-smoke` CI job and its failure currently means "a workflow file or call target is
missing". Keeping the new gate separate preserves that signal and makes the new gate revertible
without touching a working one (S1, S8).

### 5.2 Rules

| # | Rule | Severity | Phase | Rationale |
|---|---|---|---|---|
| **R1** | `default_max: null` is legal **only** with `override: required`, `judgment_terminated: true`, or `gated_by: hitl`. Otherwise: error. | error | 2 | An unbounded loop that nobody claims will be bound, and that neither a written bar nor a human gate terminates, is the defect in §1.1. |
| **R2** | Every `override: required` loop must be bound by **every** non-`optional` caller edge that reaches it (transitively through `calls`). A workflow with **no** callers and such a loop is reported `ENTRYPOINT_UNBOUND`. | error | 2 | Polices the one declaration that delegates responsibility upward. |
| **R3** | A numeric `default_max: N` must appear as a digit in the body within the `site` region (fallback: anywhere in the body). | error | 2 | Anti-drift: frontmatter and prose cannot disagree silently. Solves the `Planning: 2` vs `2 (1 rev)` class of divergence. |
| **R4** | Every `calls[].workflow` resolves to an existing file. | error | 2 | Extends today's coverage: `CALL_RE` in `smoke_workflows.py` matches only `Call /name`, so the far more common `Execute \`.agent/workflows/X.md\`` form is **currently unchecked**. |
| **R5** | The `calls` graph is acyclic, except edges whose target declares `recursive: true` with a resolved bound. The graph is built **from the authored `calls` list only** — never by grepping path mentions, which produces false cycles (§1.2). | error | 2 | `vdd-adversarial` self-recursion is legal *when bounded*; the `vdd-03` ↔ `vdd-05` "cycle" is not a cycle. |
| **R6** | Every workflow has `contract.version` and a `loops` key (possibly `[]`). | error | 3 | Forces the negative declaration (§4.8). |
| **R7** | `on_exhaust` is present on every loop. | error | 2 | An escalation path is the second half of a bound. |
| **R8** | A `scope: per_run` loop inside a workflow that iterates a list should say so in `what`. | **warn** | 2 | Heuristic, never an error — catches the `vdd-enhanced` §3 "total, not per task" class. |
| **R9** | A caller must not `bind` a loop the callee declares `override: forbidden`. | error | 2 | Makes the ownership boundary enforceable in both directions. |
| **R10** | `judgment_terminated: true` requires a non-empty `exit_bar`; `kind: review_verdict` gates require a non-empty `bar`. | error | 2 / 5 | The framework's own standard: a verdict gate is only legitimate against a **written** bar. |
| **R11** | Every `claims` token in a completion announcement line has a `gates[]` entry that produces it. | error | **5** | Makes a `✓` traceable to a gate. Requires `gates[]`, hence Phase 5. |

### 5.3 Honest limitation (must be stated in the script's docstring)

> The validator enforces **declaration**, not **truth**. It cannot detect a retry loop that the
> author simply did not declare — prose loop-detection by regex is unreliable in both directions
> and is deliberately not attempted. The initial inventory (Appendix A) is a one-time human-
> reviewed audit; R3 and R6 prevent drift *after* that point.

Stated explicitly because the framework has a standing precedent against documenting automation
stronger than what actually runs (`heal-issues` §Scheduling, *"never document automation whose
runner does not exist"*).

### 5.4 CLI contract

```
python3 System/scripts/check_loop_contract.py --root . [--strict] [--json]
```

Exit codes follow the existing convention (`smoke_workflows.py`; `feedback_lib/envelope.py:20-25`):

| Code | Meaning |
|---|---|
| `0` | All rules pass — or violations found while `--strict` is off (Phase 2 warn-only) |
| `1` | Rule violations with `--strict` |
| `2` | Usage error / `.agent/workflows` missing |
| `3` | A workflow's frontmatter is unparseable |

### 5.5 CI wiring

One new job in `.github/workflows/framework-gates.yml`, modeled on `workflow-smoke`:

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
      - name: Check workflow loop contracts
        run: python System/scripts/check_loop_contract.py --root .   # --strict added in Phase 4
```

Added as a **separate job**, so a red loop-contract gate never masks a red `workflow-smoke`,
`skills`, `prompt-references`, or `security-lint` gate.

---

## 6. Component C — `run_stack.py` (runtime frame stack)

> [!IMPORTANT]
> **PROVISIONAL (D5).** Component C is committed, but this section is a design *from today's
> evidence*. It is deliberately **not** the implementation brief. Phases 2–4 will change what is
> known — the real drift rate, which bounds actually exhaust, whether `override: required` is ever
> used, and whether `claims.py` / `heal-state.json` (which §6.5 copies) have themselves moved.
> §6 is re-derived against that evidence at the **Phase-5 entry gate (§7.1)** before implementation.
> Treat every number, adoption order, and CLI verb below as a starting hypothesis, not a decision.

### 6.1 Relationship to what already exists

This **generalizes `claims.py`, it does not duplicate it.** `claims.py` is a single-slot
ownership flag answering one question ("am I the outermost workflow, for retro purposes?").
The frame stack answers it for *any* concern, and additionally carries per-frame counters and
gate outcomes.

Migration path for retro: `run_feedback.py claim` keeps its current CLI and exit code 6
**unchanged**; internally it may later delegate to the stack. **Phase 6 at the earliest, and only
if the stack has proven itself.** No workflow's retro line changes in this spec.

### 6.2 Placement

`.agent/skills/skill-session-state/scripts/run_stack.py`

Rationale: `skill-session-state` is TIER 0 (always loaded), already owns `.agent/sessions/`,
already performs `fcntl` locking with a concurrency test (`tests/test_concurrent_state.py`), and
`.agent/skills` is `link_per_item` in `vendors.yaml` — the script reaches every vendor with no
installer change (S7).

State file: `.agent/sessions/stack.json` — sibling of `latest.yaml`, inside the already-ignored
`.agent/sessions/` (`.gitignore:9`). **`latest.yaml` is not touched** (S9).

### 6.3 State shape

```json
{
  "v": 1,
  "frames": [
    {
      "workflow": "full-robust",
      "run_id": "full-robust-095-loop-contract",
      "entered_at": 1785000000.0,
      "counters": {},
      "binds": {"security-audit": {"audit_remediation": {"max": 3}}},
      "gates": {"vdd_pipeline": "pass"}
    },
    {
      "workflow": "security-audit",
      "run_id": "full-robust-095-loop-contract",
      "entered_at": 1785000123.0,
      "counters": {"audit_remediation": 2},
      "binds": {},
      "gates": {"automated_scan": "pass"}
    }
  ]
}
```

### 6.4 CLI

| Command | Behavior | Exit |
|---|---|---|
| `push --workflow X --run-id R [--bind W.loop=N]` | Append a frame; record caller binds | `0` |
| `pop --workflow X` | Remove the top frame; error if it is not `X` | `0` / `1` |
| `tick --loop L` | Increment the top frame's counter for `L`; resolve the effective bound — the frame's own `default_max`, overridden by the nearest ancestor bind | `0` under bound · **`7` = bound exhausted** |
| `gate --id G --outcome pass\|fail\|skipped` | Record a gate outcome in the top frame *(Phase 5, consumes `contract.gates[]`)* | `0` |
| `claims --verify "VDD ✓ · Security ✓"` | Check every `✓` token against recorded gate outcomes *(Phase 5)* | `0` · **`8` = unsupported claim** |
| `status [--json]` | Print the current stack: `depth`, `workflow`, counters, gate outcomes | `0` |
| `owns --concern retro` | Is the top frame the outermost? (the `claim`/exit-6 question, generalized) | `0` owns / `6` denied |
| `reset --force` | Clear a stale stack | `0` |

New exit codes extend `envelope.py` (which defines 0–5, plus `EXIT_CLAIM_DENIED = 6` in
`run_feedback.py`):

- **`7` = `EXIT_BOUND_EXHAUSTED`** — distinct so a workflow can tell "bound blown" (escalate to
  user) from "script failed" (S6: proceed on the prose bound).
- **`8` = `EXIT_UNSUPPORTED_CLAIM`** — a completion announcement contains a `✓` with no recorded
  gate outcome behind it.

### 6.5 Crash recovery

Adopts the two mechanisms already proven in this repo:

- **TTL staleness** — a frame older than `STACK_TTL_HOURS` (default 24, matching
  `claims.py:DEFAULT_TTL_HOURS`) is silently discarded, so a dead session never bricks the next run.
- **Orphan surfacing** — `status` reports frames whose `run_id` differs from the current one, in
  the spirit of `heal-issues` Phase 0 orphan detection, which exists precisely because a run
  *did* die mid-flight (`heal-state.json`, recorded incident).

`fcntl.flock` for every mutation, `fsync` before returning — copied from `claims.py:43-48`, which
is already covered by `tests/test_concurrent_state.py`'s concurrency discipline.

### 6.6 Adoption (per workflow, one commit each)

A workflow adopts the stack by adding **two lines** — nothing is removed:

```markdown
> **Frame (optional):** `python3 .agent/skills/skill-session-state/scripts/run_stack.py push
> --workflow security-audit --run-id "<run-id>"` at entry; `pop` at every exit path.
> Non-blocking: a non-zero exit other than 7 is logged in one line and ignored (the prose bound
> below remains authoritative).
```

and, at the loop site:

```markdown
- **Bound:** `run_stack.py tick --loop audit_remediation` → **exit 7 = bound exhausted**:
  STOP and escalate. (Prose bound: max 3 — authoritative if the script is unavailable.)
```

**Recommended adoption order** — lowest risk first, each independently revertible. *Provisional:
Phase 2–4 evidence on which loops actually exhaust may reorder this (§7.1 item 2).*

1. `heal-issues` — already has lock + journal + counters; the stack is a *read-only* addition
   used for `status` only. Proves the mechanism against the workflow that needs it least.
2. `security-audit` — one loop, most-cited defect, single caller.
3. `vdd-adversarial` — the recursion case.
4. `full-robust` / `vdd-enhanced` — the binders (`push --bind`), then `gate` + `claims --verify`
   on `full-robust`'s completion line, which is the payoff for §4.6.
5. Everything else, or never — S5 means non-adopters keep working forever.

---

## 7. Phased delivery

Each phase is a separate commit with its own gate and its own revert. **No phase depends on a
later phase.**

| Phase | Deliverable | Gate to advance | Revert cost |
|---|---|---|---|
| **1** | This spec, reviewed and approved | Operator sign-off. **Round 1 complete** — D1–D4 recorded in §8 | delete a file |
| **2** | Component A frontmatter (`loops` + `calls`, **no `gates`**) on all 23 workflows + Component B warn-only (`--strict` off) | Full suite green (`pytest`, `run_tests.py`); `smoke_workflows.py`, `validate_skills.py`, `check_prompt_references.py`, `security_lint.py` still green; the validator's WARN list matches Appendix A **exactly** — no surprises | `git revert`; frontmatter is inert (S2) |
| **3** | Apply D1: add the 6 missing bounds to prose **and** frontmatter in lockstep; record the 2 no-change loops | R3 + R6 pass on every workflow; **prose edited only at the 6 bound sites** — no rewording elsewhere; diff reviewable line-by-line | `git revert`; prose returns to today's text |
| **4** | `--strict` in CI (gate flips to failing) | Phase 3 green for one full framework-upgrade cycle | remove `--strict` |
| **5** | Component C (`push`/`pop`/`tick`/`status`/`owns`) + `contract.gates[]` (§4.6) + `gate`/`claims --verify` + R10/R11; adopted by `heal-issues` and `security-audit` only | **§7.1 entry gate passed first** (§6 re-derived from Phase 2–4 evidence), then: new unit tests green; both workflows verified to behave identically with the script **absent** (S6) | delete script; `gates[]` inert; the two `>` blocks are inert prose |
| **6** *(optional, separate decision)* | Retro `claim` delegates to the stack; `full-robust`/`vdd-enhanced` adopt binds + claim verification | 3 consecutive clean runs, mirroring the `heal-issues` scheduling precedent (*"start only after ≥3 consecutive manual runs"*) | keep `claims.py` as-is until then |

**Phase 2 is the highest-value / lowest-risk step and can stand alone indefinitely.** If review
stops after Phase 2, the framework has gained a complete machine-readable inventory and a
warn-only drift detector, and has lost nothing.

### 7.1 Phase-5 entry gate — re-derive §6 before implementing it (D5)

Component C is committed, but §6 is written against the framework as it stands **before** any of
Components A/B exists. Phases 2–4 are the first real evidence this design has ever had; building C
straight from rev 3 would mean implementing against assumptions that a working validator has
since falsified. So Phase 5 opens with a re-derivation pass, not with code.

**Deliverable:** spec 095 **rev 4** — §6 (and §4.6) rewritten against the answers below. Same
document, new revision, reviewable as a diff. **Exit bar:** every item answered with evidence from
the Phase 2–4 record, not from recollection.

| # | Question Phases 2–4 will answer | What it changes in §6 |
|---|---|---|
| 1 | **Did drift actually occur?** How many times did R3 (frontmatter ↔ prose disagreement) fire between Phase 2 and Phase 4? | Near zero → the counter half of C is speculative; C narrows to `owns` + `status` + gate outcomes. Frequent → `tick` is the point of the whole component. |
| 2 | **Which bounds actually exhausted in real runs?** Harvest escalations from `.agent/sessions/latest.yaml` `active_blockers` and the run-feedback journal. | Reorders §6.6 adoption. A loop that never exhausts does not need runtime enforcement; the one that exhausts weekly goes first. |
| 3 | **Was `override: required` ever used?** As of D1 no loop uses it (§4.4 design note). | Never used and no new workflow needs it → drop the value and R2 with it, simplifying both the enum and the validator. |
| 4 | **Were the `override: allowed` defaults ever re-bound to a *different* number by a caller?** | Never → `binds` is ceremony and the caller-override machinery in `tick` can be dropped. |
| 5 | **Did authors of any new/edited workflow write a contract unprompted, and correctly?** | The schema's real usability test. Systematic mistakes → fix §4.3 before C consumes it. |
| 6 | **Have `claims.py`, `heal-state.json`, or `envelope.py` changed?** §6.5 copies the first two; §6.4 assumes exit codes 7 and 8 are free. | Any drift there invalidates the corresponding part of §6 outright. Re-check, do not assume. |
| 7 | **Is `contract.gates[]` still worth it?** Count how many completion announcements (`✓` lines) exist and how often one was emitted after a skipped or failed gate. | Zero observed false claims → drop `gates[]`, R11, and `claims --verify`; keep C's counters only. |
| 8 | **Did the workflow set change?** New workflows, renamed ones, new callers. | Re-run the §1.2 call graph; category assignments in Appendix A may move. |

**If item 1 and item 7 both come back empty** — no drift, no false completion claims — the honest
outcome is to ship a **smaller** C than §6 describes, or to record that Phases 2–4 were sufficient.
That is a legitimate result of the gate, not a failure of it: this framework's own precedent is to
not build automation whose need has not been demonstrated (`heal-issues` §Scheduling).

### 7.2 Field evidence — arrived before Phase 2, from a different direction (TASK 095)

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

### 7.3 Independent review of rev 3

Before any phase is committed to, rev 3 was reviewed by four independent lenses, each CRITICAL/HIGH
finding then put through a separate reviewer instructed to **refute** it: **57 findings raised, 30
CRITICAL/HIGH verified, 11 survived refutation.** Report:
[`docs/reviews/review-095-independent.md`](../reviews/review-095-independent.md).

**Verdict: rev 3 is not ready to enter Phase 2.** The load-bearing items, three of which were raised
independently by two lenses:

| # | § | Finding |
|---|---|---|
| 1 | §5.2 R3 | **R3 is vacuous** — every bound in Appendix A is 1, 2 or 3, and all 23 workflow bodies contain those digits in their step lists, so "fallback: anywhere in the body" passes unconditionally. `site` cannot rescue it: the spec's own example anchors (`§4c`, `Step 2b`, `§1.3`) do not occur in the files they name. R3 is the sole justification for a second machine-readable copy of every bound. |
| 2 | §3 S2 | **S2 is false.** `check_prompt_references.py:17` is a second CI-gating reader of `.agent/workflows/*.md` and scans frontmatter lines; `smoke_workflows.py` does not strip frontmatter either. S2 is the only basis for calling Phase 2 zero-risk. |
| 3 | §1.2 | **The call graph, labelled "load-bearing", omits `vdd-adversarial → 03-develop-single-task`** — an edge §4.7's own worked example declares. Three invocation spellings exist in the corpus; the derivation used one. |
| 4 | §7 Phase 2 | **Phase 2 has no rule-legal declaration** for the six A.1 loops whose prose bound does not exist until Phase 3, and its exit gate compares a warn list against a decision inventory. |
| 5 | §4.8 | **The negative declaration has no falsifier**, and `framework-upgrade` is the only one of 23 workflows with no Appendix-A category while having two real unbounded loops. |
| 6 | §5.2 R1/R10 | **`judgment_terminated` + any non-empty `exit_bar` re-legalizes an unbounded loop** — `exit_bar: "until done"` satisfies the gate. |
| 7 | §1 property 2 | **Inflated 5 → 2.** Three of the five cited rebindings are caller-owned wrappers. §1.3 rejects the FSM alternative on this count, and §4.4 justifies the three-state enum on it. |
| 8 | Appendix A | **Three rows double-count** one prose bound as both a callee loop and a caller loop. |
| 9 | §2 / §4.6 | **Scope challenge:** A+B fail the over-engineering test §4.6 applies to `gates[]`. The measured defect is 6 loops in 5 files (~15 lines); Phase 2 is ~700–850 new lines. **Phase 3 alone closes §1.1.** |

Item 9 is the one to settle first, because it changes what the rest is for. §8's *"open questions:
none"* no longer holds.


---

## 8. Decisions — review rounds 1–2

| # | Question | Decision | Consequence |
|---|---|---|---|
| **D1** | Bounds for the unbound loops | **`max = 3` accepted** across the board, per the category table in Appendix A.1 | 3 loops gain a cap they never had (VDD entrypoints); 3 gain a default matching their existing caller bind (no behaviour change through the caller); 2 record an existing mechanism with no number |
| **D2** | `framework-upgrade` "GOTO Step 2" — unbounded **and** ambiguous (Step 2 of which section?) | **Out of scope here.** Handled as a separate `/light` task | Removes 2 loops from Appendix A; the ambiguity is a prose bug, not a contract gap |
| **D3** | `contract.gates[]` | **Ship with Component C (Phase 5), not before** | §4.6 defines the schema now so C has something to consume; R11 and the `claims --verify` command are its consumers. Nothing lands in Phase 2 |
| **D4** | Document language | **English** — matches `docs/design/`, `docs/reviews/`, and the framework SOT | — |
| **D5** | Does Component C ship at all? | **Yes — committed.** But §6 is re-derived from Phase 2–4 evidence at the Phase-5 entry gate (§7.1) before implementation | §2 marks C committed; §6 and §4.6 marked PROVISIONAL; §7.1 adds an 8-item re-derivation gate producing spec rev 4; Phase 5 cannot start on rev 3 |
| **D6** | Is `05-run-full-task`'s per-task iteration a loop? | **No** — a `for-each` over a finite list terminates by exhausting its input, not by a bound | `loops[]` means *retry* only. Stated as a general rule in §4.3 so Phase-2 authors do not re-decide it per file; also covers `vdd-05` step 2 and `vdd-multi` Phase 1 |

**Naming decision inside D1.** The numeric key is `default_max`, not `max`, because for half the
loops the number *is* a default that a caller may re-scope (§4.4). Rev 1's `bound_by_caller`
boolean could not express "has a default **and** is overridable" and has been replaced by the
`override: forbidden | allowed | required` enum.

### 8.1 Open questions: none

Rounds 1–2 closed every question this spec raised. The document is **decision-complete for
Phases 1–4** and may proceed to implementation on operator command.

Phase 5 is committed in principle (D5) but **not** specified to implementation depth: it opens
with the §7.1 re-derivation gate, whose output is spec rev 4. That is a deliberate deferral of
detail, not an open question — the decision ("C ships") is made; only its shape waits on evidence
that does not exist yet.

---

## 9. Explicitly out of scope

- Any change to the four-stage dispatch tables in `System/Agents/01_orchestrator.md` §3 and
  `skill-orchestrator-patterns`. Their duplication is real but is a **documentation** issue an
  order of magnitude smaller than the loop protocol; folding it in would widen the blast radius.
- A statechart DSL, an FSM interpreter, or a pipeline runtime. The interpreter is the LLM.
- XML anywhere. The one arguably useful use — wrapping *data* inside a prompt
  (`<review_comments>…</review_comments>`) to harden the DATA-not-instructions boundary that
  `CLAUDE.md` already asserts for ledger record bodies — is a prompt-hygiene change unrelated to
  loop control and belongs in its own task.
- Changing any bound value that already exists.
- Changing `latest.yaml`, `heal-state.json`, or the `claim`/`release` CLI.
- `framework-upgrade`'s GOTO ambiguity (D2).

---

## Appendix A — Loop inventory (23 workflows, audited 2026-08-02)

### A.1 Loops requiring a decision — resolved by D1

Eight loops, four categories. `framework-upgrade` ×2 removed per D2.

#### Category 1 — copy-drift. The VDD twin lost its bound. (3 loops)

Reachable **only** by direct slash command — `vdd-enhanced` calls the non-VDD variants (§1.2),
so no caller exists to bind them. They must own the bound.

| Workflow | Site | Today | Decision |
|---|---|---|---|
| `vdd-01-start-feature` | step 4 (TASK review) | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-01-start-feature` | step 5 (ARCH review) | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |
| `vdd-02-plan` | step 3 (PLAN review) | *"repeat the review"* | `default_max: 3`, `override: forbidden`, `on_exhaust: escalate_user` |

**Why 3 and not the twin's 2.** The VDD family already has its own convention: `vdd-enhanced`
§1.3 and §2.3 both use *"Max 3 retries"* for exactly these two review loops. Taking 2 from the
non-VDD twin would introduce a third number into a family that already has two.
**Behaviour change: yes** — a cap appears where none existed, on `/vdd-start-feature` and
`/vdd-plan` only.

#### Category 2 — default + caller override. (3 loops)

Each has a caller with an existing bound **and** its own slash command. The default is set to the
caller's existing number, so **nothing changes when reached through the caller** — only direct
invocation gains protection.

| Workflow | Site | Caller bind today | Decision |
|---|---|---|---|
| `vdd-03-develop` | step 4 (`Go to Step 2.1`) | `vdd-05` step 2D: Max 3 | `default_max: 3`, `override: allowed` |
| `vdd-adversarial` | step 2b (recursive self-call) | `vdd-enhanced` §4.3: max 3 | `default_max: 3`, `override: allowed`, `recursive: true`, `judgment_terminated: true` (Objective Convergence) |
| `security-audit` | step 4c (*"until clean"*) | `full-robust` §3: Max 3 + redefined exit bar | `default_max: 3`, `override: allowed` |

**Behaviour change: none through the caller; a backstop appears on `/vdd-develop`,
`/vdd-adversarial`, `/security-audit`.**

#### Category 3 — judgment-terminated. Record, do not number. (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `vdd-multi` | Phase 3 fix loop | `default_max: null`, `override: allowed`, `judgment_terminated: true`, `exit_bar: "clean pass \| bikeshedding-only \| diminishing returns (Phase 3.1–3.3)"` |

Unbounded here is **documented and deliberate**: `--max-iterations` is a CLI flag whose default
is explicitly "unbounded", and the loop already has three written exit conditions. Assigning a
number would silently change a documented CLI default — barred by S10.
**Behaviour change: none.**

#### Category 4 — HITL-gated. Exemption, made explicit. (1 loop)

| Workflow | Site | Decision |
|---|---|---|
| `iterative-design` | Phase 5 step 7 (*"trigger Phase 3 again"*) | `default_max: null`, `override: forbidden`, `gated_by: hitl` |

Every iteration passes through Phase 4's hard **STOP** awaiting user feedback. A loop that
consumes a human decision per turn cannot run away unattended — a materially different risk class
from the other seven. Putting a number on it would misdescribe the mechanism and set a precedent
that every loop needs a number, including those where one is harmful.
**Behaviour change: none.**

### A.2 Already bounded — record as-is (16 loops)

| Owner | Site | `default_max` | `override` | `on_exhaust` |
|---|---|---|---|---|
| `01-start-feature` | step 4 | 2 | forbidden | escalate_user |
| `01-start-feature` | step 5 | 2 | forbidden | escalate_user |
| `02-plan-implementation` | step 3 | 2 | forbidden | escalate_user |
| `03-develop-single-task` | step 4 | 2 | forbidden | escalate_user |
| `05-run-full-task` | step 3 | 2 | allowed (`vdd-enhanced` §3 re-scopes to 2 *total*, `scope: per_run`) | escalate_user |
| `light-02-develop-task` | §1.5 | 3 | forbidden | escalate_user (→ standard pipeline) |
| `light-02-develop-task` | §2.4 | 2 | forbidden | escalate_user (→ standard pipeline) |
| `vdd-05-run-full-task` | step 2D | 3 | forbidden | escalate_user (persist `failed_sarcasmotron`) |
| `vdd-enhanced` | §1.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | §2.3 | 3 | forbidden | escalate_user |
| `vdd-enhanced` | §3.2 | 2, `scope: per_run` | forbidden | escalate_user |
| `vdd-enhanced` | §4.3 | 3 | forbidden | escalate_user |
| `full-robust` | §2 | 1 | forbidden | escalate_user |
| `full-robust` | §3 | 3 | forbidden | escalate_user |
| `full-robust` | §4 *(caller-owned wrapper around `04-update-docs`, §4.5)* | 1 | forbidden | escalate_user |
| `heal-issues` | Phase 2 | 3 (+ cross-run `max_attempts_per_issue: 2`, `scope: global`) | forbidden | needs_human |

### A.3 No retry loops — declare `loops: []` (7 workflows)

`04-update-docs` · `base-stub-first` · `light-01-start-feature` · `product-full-discovery` ·
`product-market-only` · `product-quick-vision` · `vdd-01/02` outside their review loops.

Every Retro step in every workflow is a `non_blocking` gate by definition, never a loop.

> **`04-update-docs` resolution.** Rev 1 flagged it as the one case where a caller bounds a loop
> the callee never declares. Per §4.5 the retry is now recorded in **`full-robust`'s own
> `loops[]`** (row 15 of A.2), leaving `04-update-docs` truthfully at `loops: []`. No prose edit,
> no new vocabulary, R2 has nothing to fire on.

---

## Appendix B — Evidence index

| Claim | Source |
|---|---|
| Slash commands are frontmatter-free wrappers (S2) | `.claude/commands/vdd.md`, `.claude/commands/full.md` |
| Only `smoke_workflows.py` reads workflow files, body-only | `System/scripts/smoke_workflows.py:19,34-50` |
| `CALL_RE` misses the `Execute .agent/workflows/X.md` form (R4) | `System/scripts/smoke_workflows.py:18-19` |
| `vdd-enhanced` calls the NON-VDD `01`/`02` (§1.2) | `.agent/workflows/vdd-enhanced.md` §1.1, §2.1 |
| `vdd-01-start-feature` / `vdd-02-plan` / `iterative-design` have no callers | call-graph scan of all 23 workflow bodies |
| `vdd-03` ↔ `vdd-05` back-edge is a doc pointer, not a call (R5) | `.agent/workflows/vdd-03-develop.md` footer |
| VDD family's own retry convention is 3 (D1 cat. 1) | `.agent/workflows/vdd-enhanced.md` §1.3, §2.3 |
| `vdd-multi` unbounded default is deliberate & documented (D1 cat. 3) | `.agent/workflows/vdd-multi.md` Parameters table + Phase 3.1–3.4 |
| `iterative-design` loop passes a hard HITL STOP (D1 cat. 4) | `.agent/workflows/iterative-design.md` Phase 4 |
| Prose cannot carry nesting; flock claim file instead | `.agent/skills/run-feedback/scripts/feedback_lib/claims.py:1-9` |
| Exit-code conventions | `feedback_lib/envelope.py:20-25`; `run_feedback.py:45` |
| No runtime YAML dependency (S3) | `skill-session-state/scripts/update_state.py:54,95`; `.agent/rules/skill_standards.yaml:2-3` |
| PyYAML available in CI/dev only | `requirements-dev.txt` |
| `.agent/sessions/` already gitignored (S7) | `.gitignore:9` |
| Installer propagation of skills/rules/tools (S7) | `System/scripts/vendors.yaml` `defaults.agent_components` |
| CI gate structure | `.github/workflows/framework-gates.yml` |
| A run really did die mid-flight | `.agent/feedback/heal-state.json` → `runs[0].note` |
| Caller-side rebinding, 5 instances | `full-robust.md:38-59`; `vdd-enhanced.md:45-58` |
| Counter non-composition stated in prose | `vdd-enhanced.md:49-52` |
| "Every retry loop is bounded" invariant | `full-robust.md:8-9` |
| Unverifiable completion claim closed in prose (motivates §4.6) | `vdd-enhanced.md` §4.4–4.5; `full-robust.md` Completion line |

---

## Appendix C — Changelog

### rev 3 — 2026-08-02, after operator review round 2

| Change | Driver |
|---|---|
| **D5 recorded**: Component C is committed, not conditional (§2, §8) | O1 answered "yes" |
| New **§7.1 Phase-5 entry gate** — an 8-item re-derivation pass over §6 against Phase 2–4 evidence, output = spec **rev 4**; Phase 5 may not start on rev 3 | O1's second half: "его надо будет обновить после фаз 2–4" |
| §6 and §4.6 marked **PROVISIONAL**, with an explicit callout that every number, CLI verb, and adoption order in §6 is a hypothesis | Same — prevents rev 3's §6 being mistaken for an implementation brief |
| §6.6 adoption order flagged as reorderable by §7.1 item 2 | Same |
| **D6 recorded** + a general rule in §4.3: `loops[]` means **retry**; a `for-each` over a finite list is not a loop (covers `05-run-full-task` step 2, `vdd-05` step 2, `vdd-multi` Phase 1) | O2 accepted; generalized so Phase-2 authors do not re-decide it 23 times |
| §8.1 rewritten from "still open" to **"none"**; spec declared decision-complete for Phases 1–4 | Rounds 1–2 closed everything |
| §7.1 states the honest null result: if drift and false-completion counts both come back zero, ship a **smaller** C — or none — citing the `heal-issues` §Scheduling precedent | Guards against the gate becoming a rubber stamp |

### rev 2 — 2026-08-02, after operator review round 1

| Change | Driver |
|---|---|
| `max` → **`default_max`**; `bound_by_caller: bool` → **`override: forbidden\|allowed\|required`** enum (§4.3, §4.4) | D1 naming decision — the number is a default for half the loops, and rev 1 could not express "has a default **and** is overridable" |
| Added **`judgment_terminated` + `exit_bar`** (§4.3) | D1 category 3 — `vdd-multi` Phase 3 is legitimately capless; rev 1's grammar would have failed it under R1 |
| Added **`gated_by: hitl`** (§4.3) | D1 category 4 — `iterative-design` cannot run away; rev 1 had no way to say so |
| `contract.gates[]` promoted from "optional / deferred" to a specified Phase-5 deliverable with two consumers (`run_stack.py gate`, `claims --verify`) and two rules (R10, R11) — §4.6, §6.4, §7 | D3 — ship with C |
| New **§1.2 call graph** with in-degree table | D1 analysis: `vdd-enhanced` calls the non-VDD variants, so `vdd-01`/`vdd-02` have no caller — this is what forces category 1 to own its bound |
| **R5 corrected**: `calls[]` means *invokes*, never *mentions*; graph built from the authored list | The path-mention scan reported a false `vdd-03` ↔ `vdd-05` cycle |
| New **R9** (no binding a `forbidden` loop), **R10** (`exit_bar`/`bar` required), **R11** (`claims` traceable to a gate) | Follow-on from the enum and from `gates[]` |
| Exit code **`8` = `EXIT_UNSUPPORTED_CLAIM`** added alongside `7` | `claims --verify` needs a distinct signal |
| `04-update-docs` resolved: the retry moves to `full-robust`'s own `loops[]` (§4.5, A.3 note) | Rev 1 left it open; this avoids both a prose edit and new vocabulary |
| Appendix A restructured from a flat list into 4 decided categories, with per-category behaviour-change statements | D1 |
| §8 rewritten from open questions to decisions D1–D4 + two non-blocking open items (O1, O2) | Review round 1 closed |
| S10 reworded: "no bound value is *changed*" (adding a missing bound is in scope; editing an existing number is not) | D1 adds bounds, so the rev-1 wording was too strong |

### rev 1 — 2026-08-02

Initial draft. Three components, ten safety invariants, six phases, four open questions.
