# Framework Audit 095 — Meta-Audit (Modes A and B)

# Mode A: SPECIFICATION AUDIT

**Subject:** `docs/TASK.md` (TASK 095 — Structural anchors and gate honesty)
**Auditor skill:** `skill-self-improvement-verificator` (Mode A)
**Date:** 2026-08-02
**Verdict:** **PASS** (one gap found and closed before sign-off; no bypass flags used)

---

## Checklist

| # | Check | Result | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | **Root Integrity** — respects `core-principles` (Atomicity, Stub-First, No Assumptions) | PASS | Every RTM row is independently verifiable and maps to one artifact. No requirement rests on an unverified claim from the source work-items: each was re-run against this repo (§1.1). |
| 2 | **Skill Compatibility** — new Agents/Prompts load TIER 0 | N/A → PASS | The task creates no agent and no prompt. It edits `02_analyst_prompt.md` only in the RTM-format clause; its TIER 0 loads are untouched. |
| 3 | **Documentation** — includes updating `System/Docs/` | **GAP → CLOSED** | The first draft's RTM had no `System/Docs` row, while the task changes four skills and two workflows that `SKILLS.md:62,66,67,87` and `WORKFLOWS.md:148` describe. **R13 added.** |
| 4 | **Migration** — describes migration of existing sessions/artifacts | PASS | R6 plus §5 Out of Scope: anchors are optional on read and emitted on write, so no artifact, session, or downstream project requires migration. `.agent/sessions/latest.yaml` schema is untouched. |

## Blocking failure conditions (§4 of the skill)

| Condition | Status |
| :--- | :--- |
| Removing `core-principles` or `skill-safe-commands` from any Agent | **Not triggered.** R8 explicitly requires `core-principles` to gain **zero** lines; A5 pins its line count. Nothing is removed from it. |
| Modifying a bootstrap file without a `System/Docs` update | **Not triggered.** `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` are not in scope; R13 covers `System/Docs` regardless. |
| Creating a new Workflow without a declared trigger | **Not triggered.** No new workflow. `vdd-enhanced.md` and `vdd-adversarial.md` are edited in place; their triggers are unchanged. |

## Bypass flags

None. No `[BYPASS_TIER_PROTECTION]`, `[BYPASS_DOCS_CHECK]` or `[OVERRIDE_VERIFICATION]` was used or
is needed.

## Auditor notes

**Where this specification is stronger than the reports it derives from.** The source work-items are
`provenance: machine` bodies and were read as data. Three of their claims did not survive
re-verification unchanged and the RTM reflects the corrected version, not the reported one:

- WI-30 attributes the failure to the section *heading*. The heading matcher already accepts a bare
  `RTM` token; the actual exit-1 came from the **column-name** check
  ([`validate.py:105`](../../.agent/skills/skill-spec-validator/scripts/validate.py#L105)).
- WI-30 describes one coupling. There are **three**, and the third
  ([`validate.py:145`](../../.agent/skills/skill-spec-validator/scripts/validate.py#L145)) fails
  `--mode plan` independently — so R3 exists to stop this task shipping a half-fix.
- WI-31's recommended option 1 (three rules into `core-principles`) is rejected on measurement:
  43 lines, TIER 0, +7 % for the minimum form and +23 % for the honest one, charged to every
  session including roles that never run a gate. R8 lands the rules in TIER 1 instead.

**One risk the specification carries deliberately.** R5 anchors every required section of TASK/PLAN,
including sections no script reads today. By the framework's own test — the one spec 095 §4.6 applies
to `gates[]`, *"declaring data that nothing reads is over-engineering"* — this is a knowing
exception. The justification is that the cost is a comment line per section emitted by a template,
while the alternative has already failed once: the RTM anchor would have been the second one-off
after `known-issues-format`, and `calculate_wsjf.py` shows a third site of the same defect that
nobody filed. The exception is recorded here rather than left implicit.

---

# Mode B: PLAN AUDIT

**Subject:** `docs/PLAN.md` (TASK 095)
**Verdict:** **PASS** — no gaps, no bypass flags.

| # | Check | Result | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | **Verification Step** — explicit `pytest` / validation-script run | PASS | Stage 4 `T-095-07` runs the skill suite, all six CI-gated pytest files, and all four `System/scripts/` gates — quoted as the byte-identical commands from `.github/workflows/framework-gates.yml`, which is the plan practising its own `T-095-05` rule. |
| 2 | **Rollback** | PASS | §0 backs up all 16 files to `.agent/archive/095/` before Stage 1, with a single restore command. No migration and no data-format change, so restore is sufficient at any point. |
| 3 | **Atomic Updates** | PASS | Ten tasks, each mapped to RTM IDs, plus four explicit ordering constraints (§3) that state *why* each order is load-bearing rather than merely listing a sequence. |
| 4 | **Test Coverage** | PASS | `T-095-02` is split Red/Green with the failing non-English fixture required in **both** validator modes before any logic; `T-095-04` requires a failing test per sibling defect; `T-095-07` re-measures the corpus in both repositories and treats a non-rising count as a failure. |

## Auditor notes

**The plan's strongest property** is `T-095-02`'s insistence that `validate.py:105` and `:145` close
in one commit. Fixing only the reported site would have shipped WI-30's fix carrying WI-32's defect —
and both work-items came from the same run, so the plan is being audited against evidence it
generated itself.

**One risk the plan does not fully retire.** `T-095-09` closes WI-30/31/32 in the *reporting*
project's ledger, i.e. in a second repository, where this plan's regression suite does not run. The
plan mitigates by ordering (`T-095-09` after `T-095-07`) and by citing the `known-issues-format`
rule that "sent for review is not closed", but the verification there remains a `git diff` read by a
human rather than a gate. Recorded, not solved.
