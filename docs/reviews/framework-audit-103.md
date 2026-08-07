# Framework Audit: TASK 103 — Anchored positional references

**Date:** 2026-08-07
**Auditor:** Self-Improvement Verificator (Mode A — SPECIFICATION AUDIT)
**Target:** `docs/TASK.md`
**Status (round 1):** **BLOCKED**
**Status (round 2):** **APPROVED**

## 0. Emergency Bypass

- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

No flag set. No bypass claimed.

## 1. Compliance Checklist — round 1

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | Pass | ID 103, slug `anchored-positional-references`, archive name present |
| **Tier Protection** | Pass | No TIER 0 skill is modified or removed. `core-principles` and `skill-safe-commands` untouched |
| **Root Integrity** | Pass | RTM is 10 atomic requirements each bound to an acceptance criterion. Every figure states its method and revision |
| **Skill Compatibility** | N/A | No new agent or prompt is created, so the TIER 0 loading obligation has no subject |
| **Documentation** | **Fail** | See F-1 |
| **Migration** | Pass | R2 + 103-D1 + UC-4 state the zero-migration property, measured across 17 repositories |
| **Internal consistency** | **Fail** | See F-2 |

### F-1 — `System/Docs/` is not in scope (checklist item 3)

R10 requires both changelogs and the routed ledger record. Nothing requires the registry.

Measured: `System/Docs/SKILLS.md:68` carries the `documentation-standards` row
(`Docstrings, "The Why" comments, Markdown structure, register rules (§5.5) — see the note below`)
and a note at `:98`. Neither names `check_positional_refs.py`, §4.1, or §4.2. This task gives the
skill a new normative rule, four finding kinds, two new CLI surfaces and a write mode, and would
leave the registry describing the skill as it was.

This is the failure-condition class the skill lists as blocking — a framework component changed
without a corresponding `System/Docs/` update.

**Required action:** add a requirement covering `System/Docs/SKILLS.md`, and an acceptance criterion
that fails when the row is unchanged.

### F-2 — R4 contradicts the tool's own stated design constraint

`check_positional_refs.py:17` states, as one of three design constraints in its module docstring:

> * **Read-only.** The tool never writes to the repository.

R4 introduces `--fix`, which writes to the repository. The TASK requires the behaviour and does not
require the docstring to change with it. Shipping as specified leaves the file asserting an
invariant its own CLI breaks — the same class of silently-false claim this entire task exists to
close, reproduced inside the fix.

**Required action:** require the constraint to be restated in the same change, narrowed to what
stays true (the check never writes; the separately-invoked fix mode does, and never to an anchor).

## 2. Risk Analysis

- **R-1 — symlink fan-out.** `.agent/skills/documentation-standards` is a symlink target in at least
  five consumer repositories (`Universal-skills`, `onchain-analytics`, `obsidian-llm-wiki`,
  `dynamic-test`, `travel-bootstrap`). Any edit here is live in all of them at commit time, with no
  per-repo adoption step. **Mitigated by 103-D1** (unanchored → not examined) and pinned by A3, which
  is the acceptance criterion that must not be weakened.
- **R-2 — a write mode inside a checking tool.** `--fix` mutating a tracked file is the hazard
  `verify-provenance.mjs` names when it keeps `--update` out of its gate. **Mitigated by 103-D4** —
  the boundary is anchor (never written) versus derived number (recomputable) — and by requiring
  fix to be a separate invocation, not a side effect of the check.
- **R-3 — `ANCHOR_ABSENT` false positives on normalization.** A correctly-written anchor that fails
  to match because of pipe-escaping or line wrapping reports a real reference as broken, which is how
  a gate earns distrust. R1's normalization clause is the mitigation; A2 must pin both cases.
- **R-4 — scope creep into wiring.** OQ-1 and §7 hold the line; the task ships a capability and no
  enforcement. Nothing in the RTM edits a workflow.

## 3. Verdict & Actions — round 1

**BLOCKED.**

1. Bring `System/Docs/SKILLS.md` into the RTM with its own acceptance criterion (F-1).
2. Require the module docstring's read-only constraint to be restated in the same change (F-2).

## 4. Round 2 — re-audit after redraft

Both required actions were applied to `docs/TASK.md`:

| Action | Evidence in the redraft |
| :--- | :--- |
| F-1 | R11 added; A9 added, failing when the `SKILLS.md` row is unchanged |
| F-2 | R4 extended with the docstring clause; A4 extended to fail when the constraint still reads unconditionally |

| Check | Status |
| :--- | :--- |
| Meta-Information | Pass |
| Tier Protection | Pass |
| Root Integrity | Pass |
| Skill Compatibility | N/A |
| Documentation | **Pass** |
| Migration | Pass |
| Internal consistency | **Pass** |

**APPROVED for §2 Planning.** Two obligations carry forward into the PLAN audit (Mode B), which
gates them, not this one:

1. Stub-First is not addressed by a TASK and must appear in the PLAN — new finding kinds and CLI
   surface declared and test-red before implementation.
2. Rollback: §3.1 of the workflow backs up bootstrap files only. The files this upgrade edits are a
   script, two skill documents, a test file, two changelogs and a registry — the PLAN must name its
   own backup set.

## 5. Mode B — PLAN AUDIT

**Target:** `docs/PLAN.md` · **Status (round 1):** **BLOCKED** · **Status (round 2):** **APPROVED**

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | Pass | Seven clusters, each ending in an executed gate: A6, B8, C4, D4, E4, F5, G4 |
| **Rollback** | Pass | Backup set enumerated; rollback names ten paths and states why the three outside the backup set matter |
| **Atomic Updates** | Pass | Each cluster is independently revertible; no cluster moves or deletes a tracked file |
| **Test Coverage** | Pass | Cluster B pins R2–R7 before any logic exists; baselines measured (89 passed, 46/46) |
| **Stub-First** | Pass | Cluster A declares surface and asserts 89 passed before logic — the carried obligation from §4 |
| **Evidence sufficiency** | **Fail** | See F-3 |
| **Write safety** | **Fail** | See F-4 |
| **Stated residuals** | **Fail** | See F-5 |

### F-3 — the property with the widest blast radius is verified on the narrowest corpus

G5 runs the tool against this repository's living corpus: **six** references. The property it is
supposed to establish — an unreferenced coordinate stays *not examined* — protects **324**
references across four repositories reached by symlink at commit time. Six references cannot
distinguish "the rule holds" from "this corpus is too small to fire it".

**Required action:** add a step running the shipped tool against at least one consumer repository's
living corpus read-only, and record the finding count. `Universal-skills` (36 references) is the
smallest corpus large enough to be evidence; `obsidian-llm-wiki` (99) is stronger. The run must
report zero findings for unreferenced coordinates.

### F-4 — `--fix` writes in place with no assertion about the rest of the file

D1 rewrites a line number inside a tracked document. B4 asserts the referent is byte-identical after
the write. Nothing asserts that **the rest of the document** is. A rewrite that also normalizes line
endings, strips trailing whitespace, or drops a final newline would pass every stated case while
silently editing files across the corpus it was pointed at.

**Required action:** B4 asserts the fixed document differs from its input in exactly the intended
character range and nowhere else.

### F-5 — an ungated pair is shipped without saying so

F1 writes the rule into `documentation-standards` §4.1 and F3 writes the mirroring row into
`artifact-formalizer/references/authoring-contract.md`. Nothing compares them after landing:
`check_contract_sync.py` reaches only `known-issues-format` and its two seed templates. WI-16 §5.3
met the same situation and **stated it** — "The pair is ungated" — so a later reader does not assume
a gate exists. This task inherits the situation and inherits the obligation to declare it.

**Required action:** state the residual in `docs/TASK.md` §7. Not a blocker on its own; blocking
only because an undeclared gap reads as a covered one.

## 6. Verdict & Actions — Mode B

**BLOCKED**, three required actions: F-3, F-4, F-5.

### Round 2 — re-audit after redraft

| Action | Evidence in the redraft |
| :--- | :--- |
| F-3 | PLAN G5 split: G5 this repository, **G6 a consumer corpus** read-only with its count recorded |
| F-4 | PLAN B4 extended: the fixed document differs in exactly the intended range and nowhere else |
| F-5 | TASK §7 gains the ungated-pair residual, citing the WI-16 §5.3 precedent |

**APPROVED for §3 Execution.** No bypass flag set; no TIER 0 skill modified; the acceptance set
A1–A9 is unchanged by this round.
