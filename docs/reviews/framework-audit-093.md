# Framework Audit: closing the WI-2…WI-7 tail (TASK 093)

**Date:** 2026-07-30
**Auditor:** Self-Improvement Verificator (Mode A + Mode B, single pass — TASK and PLAN authored together)
**Target:** `docs/TASK.md` **and** `docs/PLAN.md`
**Status:** **BLOCKED → APPROVED** — three required changes applied to the plan before Step 1 began (§3 disposition). Ran **before** execution, unlike audit 092.

## 0. Emergency Bypass
- [ ] `[BYPASS_TIER_PROTECTION]`
- [ ] `[BYPASS_DOCS_CHECK]`
- [ ] `[OVERRIDE_VERIFICATION]`

**Justification:** none — no flag set. No TIER 0 skill is modified. The three vendor bootstrap files
(`CLAUDE.md`, `GEMINI.md`, `AGENTS.md`) are edited **additively** by R6 (one clause, identical in all
three); that is not a tier bypass, and §4 of this skill's blocking list is satisfied because no
`GEMINI.md` edit ships without the matching `System/Docs/` update (Step 2 covers
`QUALITY_FEEDBACK_LOOP.md`, the subsystem's architecture doc).

## 1. Compliance Checklist

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | TASK ID `093`, slug `wi-tail-hardening`, allocated via `task_id_tool.py` (`status: generated`). No live `docs/TASK.md`/`PLAN.md` existed at authoring time, so `skill-archive-task` had nothing to rotate — verified on disk, not assumed. |
| **Tier Protection** | ✅ Pass | `core-principles`, `skill-safe-commands`, `artifact-management`, `skill-session-state` untouched. Two TIER 2/3 skills change (`run-feedback`, `known-issues-format`); the bootstrap edit is one additive clause. |
| **Skill Compatibility** | ✅ Pass | No new agent, prompt, or workflow — so no new TIER 0 load list and no §4 "workflow without a trigger" exposure. `known-issues-format` keeps its directory name (four repos symlink it — the constraint audit 091 established still holds). |
| **Documentation** | ✅ Pass | R3 (SKILL.md §5) · R5 (contract + both templates) · R6 (three bootstrap files) · Step 2 (`System/Docs/QUALITY_FEEDBACK_LOOP.md`) · Step 9 (CHANGELOG EN+RU). `docs/ARCHITECTURE.md` correctly untouched: it documents agents and workflows and has never described the ledgers. |
| **Migration** | ✅ Pass | `config.v` stays `1`; `body_max_chars` is additive with a default (64000) no honest body reaches. `provenance` is an **optional extension** key, so every existing record stays valid and no consumer may require its presence — R4 must be absence-tolerant on the read side, which `list_issues`'s `meta.get` already is. Verified both consuming configs by hand (see Risk 1). |
| **Verification Step** | ✅ Pass | Every step carries an executable verify line; Step 9 names the full sweep; Step 8 requires three hand-run mutations. |
| **Rollback** | ✅ Pass | Clean tree at `4b2a65e` (the release commit), per-path checkout or task-wide reset. `.bak` copies declined consistently with audits 091/092. |
| **Atomic Updates** | ✅ Pass | 9 steps; the ordering rationale is stated and correct — shared primitives (1–2) precede both ledger passes (4–5), which is the only ordering that prevents re-creating the asymmetry WI-7 exists to close. |
| **Test Coverage** | ⚠️ **Fail** | 24 requirements, each with a named verification — but the plan never says the new tests must be shown to **fail before the fix**. See Required Action 1: this is the one finding that matters, because R21 is itself "three tests passed for the wrong reason". |
| **Root Integrity (Stub-First)** | ⚠️ Pass, by exemption | Stub-First does not apply literally — every target already exists and this is a hardening pass, so there is no stub. The applicable form of the same discipline is RED-before-GREEN per guard, which is exactly what Required Action 1 restores. |

## 2. Risk Analysis

- **Risk 1 — R16's new validation could break filing in two live repos on save.** Both consume these
  skills by symlink, so a validation that rejects a value they already use breaks them with no merge
  step to catch it. *Checked, not assumed:* `Universal-skills` ships `id_prefixes` values `TF-X`,
  `WIKI-INGEST`, `HTML2MD`, `DOCX`… and `onchain-analytics` ships no `id_prefixes` at all and no `v`
  key. All pass the proposed `^[A-Za-z][A-Za-z0-9_-]{0,31}$` (the `-` in the charset is load-bearing —
  a regex without it would have broken `TF-X` immediately). Both `backlog_anchor` values are the
  default. **Mitigation:** the plan already requires validating this repo's config before writing the
  tests; extend that to a one-time check of both consumer configs (done here) and pin `TF-X` as a
  test case so a future tightening cannot silently drop it.
- **Risk 2 — R13's fence rewrite is the highest-blast-radius change in the plan.** `anchor_positions`
  gates *all* work-item filing, and the F3 regression it was built for (an anchor documented inside a
  code fence must never be written into) is a defect this repo already shipped once. A CommonMark
  rewrite that gets the toggle wrong fails **open**, which is strictly worse than the fail-closed
  nuisance it is fixing. *Mitigation:* the plan names the F3 test as the gate for this step; the audit
  adds that the fence rewrite must be the **only** change in its commit-sized unit, so a bisect points
  at it unambiguously.
- **Risk 3 — the module-level memo in R7 introduces a staleness class for no measurable gain.** With
  `data_root` cached per instance, the remaining spawn count is one per `Config` that actually reads
  `feedback_dir` — the memo only helps a process that builds several `Config`s over the *same* root,
  which is the test suite, and there the memo becomes a cache that outlives the tmp repo it describes.
  A test that recreates a different repo at the same path in one process would silently get the old
  answer. **Required Action 2:** drop the module memo, keep the per-instance cache.
- **Risk 4 — per-instance caching is not optional and the plan is right to say so.** Turning
  `data_root` into an uncached property would spawn `git` on *every* `cfg.feedback_dir` access — a
  performance regression disguised as a fix. Called out so no reviewer "simplifies" it away.
- **Risk 5 — R4's banner touches the record body region of a contract that promises verbatim bodies.**
  The banner is inserted between the H1 and the body, i.e. into the record *file*, not into the body
  text, and the writer already emits an H1 the operator did not supply. *Mitigation:* R4's own test
  must assert the body bytes are unchanged, and the `known-issues-format` wording must distinguish
  "the body" from "the record file" so the next reader does not see a contradiction. Note the direct
  tension with WI-2, which TASK §1.1 resolves explicitly — the audit endorses that resolution: a
  refusal is honest, a silent rewrite of evidence is not.
- **Risk 6 — R9 narrows dedup to a filename convention.** Stated in TASK §4 with the fallback
  deliberately rejected, and the rejection is correct (the miss case is the common case, so a fallback
  scan would restore the O(k²) it removes). *Mitigation:* the invariant belongs in the docstring **and**
  in a test that fails if `finding.save` ever stops deriving the filename from `finding_id`.
- **Risk 7 — R2's credential screen is a new refusal on a path that used to always succeed.** A false
  positive blocks real filing. *Mitigation:* the narrow pattern set (TASK §1.1) excludes the two rules
  that actually over-match prose, and R2 requires a positive test proving `token: [PLACEHOLDER]` prose
  and an email address still file. **Required Action 3:** add one more positive case — a body quoting a
  *redacted* secret (`sk-[REDACTED]`, `AKIA…` inside a `[REDACTED]` marker), since a work-item
  describing this very fix will contain exactly that shape and must not refuse itself.
- **Risk 8 — 24 requirements in one task is large for one pass.** Mitigated by grouping: no step
  spans two modules whose contracts differ, and Steps 4/5 are deliberately the *same* fix list applied
  twice. Splitting further would re-open the asymmetry the task exists to close, so the size is
  accepted rather than reduced.
- **Risk 9 — the plan changes six error/message surfaces that existing tests assert on** (doctor
  checks, dry-run human lines, rollback messages). Expect red tests that are *correct* to update.
  *Mitigation:* stated here so a message-assertion failure is not mistaken for a behaviour regression —
  and conversely, so no behaviour regression is waved through as "just a message change".

## 3. Verdict & Actions

**BLOCKED** pending three changes. None is a re-plan; all three are edits to the plan's own text.

**Required actions:**
1. **RED-before-GREEN, per guard (blocking).** The plan must state that every new guard test is run
   *before* its fix and observed to fail — or, where that is impractical, mutation-checked after, with
   the confirmation recorded. Without it this task ships ~30 new tests under the same defect R21 is
   fixing: a test that passes for the wrong reason is indistinguishable from a test that works, and
   TASK 092 already learned this once. Step 8's discipline must apply to Steps 1–6, not just to the
   three known-bad tests.
2. **Drop the module-level memo in R7** (Risk 3); keep the per-instance cache and `timeout=2`.
3. **Add the `[REDACTED]`-shaped positive case to R2** (Risk 7), so a record describing this fix does
   not trip its own screen.

**Carried into execution as standing constraints:**
4. R13 lands as its own isolated unit and must not weaken the F3 guarantee — accuracy and a better
   message, never permission to write (TASK §4 says this; the audit makes it a gate).
5. Pin `TF-X` as an `id_prefixes` test case (Risk 1) so a future tightening cannot silently break a
   live consumer.
6. Any WI row not implemented must say so in that work-item's resolution blockquote (R24). WI-2's
   deviation from its own recommendation is the one already known; if a WI-7 row is skipped for risk,
   it stays `open` with the reason, and WI-7 does **not** get `status: done`.

**Disposition — all three applied before execution began:**
1. `docs/PLAN.md` now carries a standing **RED-before-GREEN, per guard** clause above Step 1, binding
   Steps 1–6 to the discipline Step 8 already had.
2. The module-level memo is struck from Step 3 and from TASK R7; the per-instance cache and
   `timeout=2` remain, with the reasoning inline so it is not re-added.
3. Step 2's verify line and TASK R2 now require the `[REDACTED]`-shape positive case.

**APPROVED for execution.** Standing constraints 4–6 remain open obligations, verified at Step 9.
