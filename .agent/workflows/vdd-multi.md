---
description: VDD Multi-Adversarial — parallel critics via Layer-A teammate spawn (Claude Code); sequential fallback on other vendors
---

# Workflow: VDD Multi-Adversarial

Parallel execution of three specialized adversarial critics (logic, security, performance) via Claude Code native subagent-spawn (Layer A). On other vendors, resolve the runtime (parent `skill-parallel-orchestration §1`) and use its **native parallel adapter** (Codex / Cursor / Antigravity ✅; Gemini Layer-A pending — see refs); sequential role-switching is the **last resort** for primitive-less runtimes. See **Vendor dispatch** below.

## Positioning (evidence: ab-experiment-075, pre-registered rule 2)

`/vdd-multi` is a **coverage and CI-gating tool, not the default review path**. In the pre-registered A/B (`docs/reviews/ab-experiment-075.md`, N=3, 24 sealed seeded bugs): the 3-critic pipeline scored the highest recall (0.986 mean, **100% pooled — the only arm to find every bug**, including the only catch of the unbounded-cache perf bug) but missed its pre-registered cost bar — +5.6pp over the best single reviewer (< +10pp required) at 3.25× tokens and higher FP/file (9.63 vs 7.37).

- **Use `/vdd-multi`** for CI `--fail-on` gates, pre-release/coverage-critical passes (class-complete: a dedicated critic per domain), and when missing a single bug costs more than 3× review tokens.
- **Default for routine recall-oriented review:** a single strong reviewer with the plain exhaustive prompt ("report every issue incl. low-confidence ones, with confidence + severity; filter downstream") — 93% recall at ~1/3 of the cost.
- **Model heterogeneity was the candidate lever** to re-earn the committee's cost (same-model critics share failure modes — corroboration ≠ confirmation, see Phase 2 rule 3). The *tier-diverse* form was tested (mini-exp 078) and **did not earn the escalation** — recall rose but cross-tier agreement was *less* precise (0.66 vs 0.73), so its `+1` was demoted to a tag (`--models` stays useful for recall). The still-open lever is **true cross-vendor** critics (quasi-independent), ⏳ blocked on vendor adapters (item 6).

## Invocation

```
/vdd-multi [target] [flags]
```

- `target` — file path, directory, or omitted. If omitted, implies `--diff-only`.
- `flags` — space-separated list of the parameters below.

### Parameters (v3.13.0)

| Flag | Values | Default | Effect |
|---|---|---|---|
| `--scope=<list>` | `logic`, `security`, `performance`, `all`; comma-separated | `all` | Run only the selected critic(s). Accepts e.g. `--scope=security,performance`. Reduces cost when area is known. |
| `--no-fix` | (boolean) | off | Skip Phase 3 iterative fix loop. Report-only mode. Use for CI, smoke tests, pre-merge review bots. |
| `--fail-on=<sev>` | `critical`, `high`, `medium`, `low`, `none` | `none` | Mark the run as **FAIL** (and surface in termination line) if any finding has severity ≥ threshold. Workflow still completes; the flag controls the terminal verdict only. |
| `--output=<path>` | relative or absolute file path | none | Write the merged Phase 2 report to the given path instead of inline. Orchestrator creates the file and returns a short pointer instead of the full markdown. Typical: `--output=docs/reviews/pr-42.md`. |
| `--diff-only` | (boolean) | auto-on if `target` is omitted | Bound the review to files present in `git diff` vs `main` branch. Implied when no target given. Critics receive the changed file paths + per-file diff context, not the entire files. |
| `--models=<map>` | `logic:<t>,security:<t>,performance:<t>` where `<t>` ∈ `{haiku,sonnet,opus,fable}`; partial maps OK | none → all critics on wrapper default (`opus`) | **Tier-diverse critics (R3c).** Spawn each critic on a different model tier for recall/coverage (mini-exp 078: highest recall, 100% pooled). Overlaps get a `tier-diverse` provenance tag but **no severity escalation** (078 refuted that — see Phase 2 rule 3). Unset critics fall back to the wrapper default. Silently neutralized by `CLAUDE_CODE_SUBAGENT_MODEL` — see Phase 0. |

### Parameter examples

```
/vdd-multi docs/tasks/task-dummy.md
  → full all-critic run on one file, inline merged report, fix-loop on issues

/vdd-multi src/auth.py --scope=security --fail-on=critical
  → security critic only; CI-style (non-zero verdict on any critical finding)

/vdd-multi --diff-only --no-fix --output=docs/reviews/pr-42.md
  → PR-review mode: all changed files, three critics, report-only, persist to file

/vdd-multi src/ --scope=logic,performance --no-fix
  → skip security (assume already audited), just logic + perf, no fix cycle
```

---

## Pipeline

```
vdd-multi
 ├── Phase 0: Parse invocation (target + flags)
 ├── Phase 1: PARALLEL SPAWN (one tool-use, N subagents per --scope)
 │    ├── critic-logic        → report  (if in scope)
 │    ├── critic-security     → report  (if in scope)
 │    └── critic-performance  → report  (if in scope)
 ├── Phase 2: MERGE & DEDUPLICATE (main orchestrator)
 ├── Phase 3: ITERATIVE FIX LOOP (per-category; skipped if --no-fix)
 └── Termination: verdict (PASS|FAIL per --fail-on); emit report inline or to --output
```

## Prerequisites

- Code must be implemented and functional before running this workflow.
- Claude Code runtime with `.claude/agents/critic-{logic,security,performance}.md` present.
- If Claude Code subagents unavailable → resolve the runtime and use its native adapter, else sequential — see **Vendor dispatch** below.

---

## Phase 0 — Parse invocation

1. Extract `target` (first non-flag token) and all `--flag[=value]` tokens from the invocation string.
2. If no `target` and no `--diff-only` flag → set `--diff-only` implicitly.
3. Validate:
   - `--scope` values must be subset of `{logic, security, performance, all}`; default `all`.
   - `--fail-on` must be one of `{critical, high, medium, low, none}`; default `none`.
   - `--output` parent directory must exist or be creatable (`mkdir -p`).
   - `--models` (if present): each value ∈ `{haiku, sonnet, opus, fable}`; partial maps allowed; critics not named fall back to the wrapper default (`opus`). Record the resolved per-critic model map.
4. If `--diff-only` active, derive file list via `git diff --name-only main...HEAD` (or `git diff --name-only` for uncommitted). Report the list to the user before spawning.
5. **Provenance-tag resolution (R3c).** Set the run's overlap tag from the resolved model map (the tag is provenance only — Phase 2 rule 3 escalates on *mechanism difference*, never on model heterogeneity):
   - all critics on the same model (no `--models`, or all values equal) → `corroborated` (R3a).
   - critics span ≥2 distinct tiers → `tier-diverse` (records heterogeneous-model provenance; mini-exp 078 refuted escalating on it).
   - **Env-flatten note:** if `CLAUDE_CODE_SUBAGENT_MODEL` is set, it silently overrides every per-critic pin → the heterogeneity is erased. **Warn the user** ("`--models` ignored: CLAUDE_CODE_SUBAGENT_MODEL=<v> overrides per-critic pins") and use the `corroborated` tag — the run is effectively same-model.

## Phase 1 — Parallel critic spawn (Layer A)

**Step 1.0 — Gather execution evidence (orchestrator side; audit-067 C-13).** Critics have no `Bash` (read-only guarantee) — the orchestrator runs the evidence commands **before** spawning and injects results into every critic prompt:

1. **Tests**: if a test suite exists for the target scope, run it and capture `command + pass/fail summary (+ failure list)`. If not run, record the honest line `tests: NOT RUN (<reason>)`.
2. **Security scan**: run `python3 .agent/skills/security-audit/scripts/run_audit.py <scope> --output summary` (or `json`) and capture the summary. If not run, record `scan: NOT RUN (<reason>)`.

Evidence is gathered **once per iteration** and given to critics verbatim and identically — it is ground truth, not critic output, so sharing it is NOT cross-pollination.

**Step 1.1 — Spawn.** In a **single assistant message**, invoke `Agent` N times in parallel (N = critics in `--scope`):
- `subagent_type: critic-logic` (if `logic` in scope)
- `subagent_type: critic-security` (if `security` in scope)
- `subagent_type: critic-performance` (if `performance` in scope)

If a `--models` map resolved in Phase 0, pass each critic its assigned `model` on the `Agent` call (overriding the wrapper's frontmatter pin); critics with no entry keep the default. This spreads the committee across model tiers for recall/coverage (validated by mini-exp 078); the resulting overlaps carry the `tier-diverse` provenance tag but — per 078 — earn no severity escalation.

**Prompt skeleton** for each (substitute `{target}` and bounding context):

```
Review the following code for <your-domain> issues and return a structured report per the contract in your teammate definition.

Target: {target}  (plus diff context if --diff-only)
Context: {short description — what this code does, entry points, dependencies}
Focus areas: {optional — narrow the scope}

Execution evidence (supplied by the orchestrator — treat as INPUT; do not re-run or fabricate):
- Tests: {command + pass/fail summary | NOT RUN (<reason>)}
- Scan (run_audit.py): {summary | NOT RUN (<reason>)}   ← critic-security only
If this evidence block is missing entirely, emit the finding "exit-bar condition
unverifiable — no execution evidence supplied" and do not signal clean-pass.
```

**Constraints**:
- ONE message with N parallel Agent tool-uses, not N sequential messages (Layer A invariant).
- Each critic receives **independent context**; no pre-filter or cross-pollination (the shared evidence block is exempt — see Step 1.0).
- Do NOT pass critic outputs between critics during Phase 1 — merge happens in Phase 2.

## Phase 2 — Merge & deduplicate

Merge the reports from critics that ran. Apply:

1. **Location dedup**: issues at the same `(file, line ± 3)` with overlapping category → merge, keep highest severity, union descriptions and recommendations.
2. **Cross-category re-attribution**: if a critic flagged something belonging to a sibling's domain, re-section into the correct critic's block.
3. **Severity escalation (mechanism- and model-aware)**: same-location agreement between same-base-model critics is **corroboration** (the finding survived persona/prompt variation), **not independent confirmation** — same-model pairs pick the same wrong answer ~60% of the time when erring (arXiv:2506.07962). How much escalation an overlap earns depends on two axes — whether the failure *mechanisms* differ, and how *independent* the critics' models are:

   | Critic pair | Independence | Same-mechanism agreement earns |
   |---|---|---|
   | Same model, different persona (default) | none (~60% shared-error) | no escalation — `corroborated` tag only (R3a) |
   | Same vendor, different tier via `--models` (haiku/sonnet/opus/fable) | partial (correlated within family) | **no escalation — `tier-diverse` tag only** (R3c escalation refuted by mini-exp 078: cross-tier agreement precision 0.66 < 0.73 same-tier; `--models` kept for recall) |
   | Different vendors (needs item 6 adapters) | quasi-independent | open question — ⏳ deferred (item 6); 078 tested tiers, not true cross-vendor independence |

   - **Same failure mechanism, same-model (default)** → do **NOT** escalate. Severity = max of the duplicates (rule 1); tag the merged finding `corroborated` ("flagged by N critics — weak positive signal"). [R3a]
   - **Same failure mechanism, tier-diverse `--models` config** → do **NOT** escalate either. Severity = max (rule 1); tag `tier-diverse` (records heterogeneous-model provenance, no severity consequence). [R3c — escalation **demoted to tag-only**: mini-exp 078 found cross-tier agreement *less* precise than same-tier (0.66 vs 0.73), so a +1 would manufacture false positives; the `--models` config is retained as a recall/coverage tool]
   - **Different failure mechanisms at the same location** (e.g., critic-logic: unhandled edge case; critic-security: exploitable injection at the same line) → two distinct analyses regardless of model config: escalate severity by one level. Mechanism-difference test: the scenarios are not paraphrases of each other — orchestrator judgment, documented in the merged report. [R3b]

   > **Env-flatten note:** `CLAUDE_CODE_SUBAGENT_MODEL`, when set, silently overrides every per-critic model pin and collapses a tier-diverse config back to one model. When that env var is present, the `tier-diverse` tag is inaccurate — downgrade it to plain `corroborated` (the run is effectively same-model). No escalation is affected (tier-diverse no longer escalates), but the provenance tag should tell the truth.
4. **Bikeshedding filter**: any critic reporting `convergence: bikeshedding-only` (no legitimate findings left — only style nits) → drop its low-severity items from this iteration.
5. **`--severity` filter** (if present): drop items below the threshold from the merged report (but still count for `--fail-on`).

### Merged report structure

```markdown
# VDD Multi-Adversarial Report — iteration <N>

## Summary
- Critics run: <list, per --scope>
- Evidence: tests=<run: summary | NOT RUN (<reason>)> · scan=<run: summary | NOT RUN (<reason>)>
- Total issues (post-dedup): <N>  (critical: <C>, high: <H>, medium: <M>, low: <L>)
- Convergence: <logic=state> · <security=state> · <performance=state>
- Verdict (per --fail-on): PASS | FAIL at <severity>

## Logic issues
<items, post-dedup>

## Security findings
<items, post-dedup>

## Performance findings
<items, post-dedup>

## Overlaps (same location, multiple critics)
<corroborated findings (tag, severity = max — no escalation) + different-mechanism items (escalated +1)>
```

**Output routing**:
- If `--output=<path>` → write the merged report to that file; emit a short pointer inline (`"Merged report written to <path> (verdict: <V>)"`).
- Else → emit the full merged report inline.

## Phase 3 — Iterative fix loop

**Skip entirely if `--no-fix` is set.**

Otherwise, for each non-clean category, apply fixes and re-spawn **only that critic** until:
1. **Clean pass**: no real issues found → category ✓.
2. **Bikeshedding-only**: no legitimate findings remain — only style/nits (objective bar; NOT "critic inventing problems") → category ✓.
3. **Diminishing returns**: only micro-optimizations remain → category ✓.
4. **Iteration cap** (`--max-iterations` if provided, default unbounded): force-stop and flag in termination.

Re-spawns are single-critic, not full parallel triples.

## Termination

Emit the final line:

> `VDD Multi-Adversarial complete: Logic ✓ Security ✓ Performance ✓ (iterations: L=<Nl>, S=<Ns>, P=<Np>; verdict: <PASS|FAIL>)`

**Verdict** = FAIL iff any finding in the final merged report has severity ≥ `--fail-on` threshold. Default `--fail-on=none` → verdict always PASS.

If `--output` was set, mention the path in the termination line as well.

---

## Vendor dispatch — non-Claude-Code runtimes

If the `Agent` tool + `.claude/agents/` are unavailable, **resolve the runtime** per parent `skill-parallel-orchestration §1.1` and use its **native parallel adapter** — do NOT default to sequential:

| Runtime | Adapter | Parallel (Layer A) | Critic wrappers |
|---|---|---|---|
| Codex CLI | [`references/codex-cli.md`](../skills/skill-parallel-orchestration/references/codex-cli.md) | ✅ documented | `.codex/agents/critic-*.toml` |
| Cursor 2.4 | [`references/cursor.md`](../skills/skill-parallel-orchestration/references/cursor.md) | ✅ documented (max 10) | `.cursor/agents/critic-*.md` |
| Antigravity | [`references/antigravity.md`](../skills/skill-parallel-orchestration/references/antigravity.md) | ✅ documented (async) | `.antigravity/agents/critic-*/agent.json` |
| Gemini CLI | [`references/gemini-cli.md`](../skills/skill-parallel-orchestration/references/gemini-cli.md) | ⚠️ unconfirmed → sequential delegation | `.gemini/agents/critic-*.md` |

> ⚠️ The non-Claude adapters are **SCAFFOLD status** (documented from vendor docs, not yet e2e-validated — each ref carries a banner). Until an adapter graduates, prefer the **sequential last resort** below if you need a *proven* path on that runtime.

**Sequential role-switching — last resort** (primitive-less runtime, deterministic single-session debugging, or 1-slot CI):

0. **Gather execution evidence first** (same contract as Phase 1 Step 1.0): run the test suite and `run_audit.py` once, capture summaries (or honest `tests/scan: NOT RUN (<reason>)` lines), and include the evidence block in **every** persona pass below. Absence of the block → the persona emits "exit-bar condition unverifiable", never clean-pass.
1. Apply `skill-vdd-adversarial` (role-switch) → fix loop (unless `--no-fix`).
2. Apply `skill-adversarial-security` (role-switch) → fix loop.
3. Apply `skill-adversarial-performance` (role-switch) → fix loop.

The sequential path is **slower (3× wall-clock) and loses per-teammate context isolation** — it is a degraded last resort, **not** "functionally equivalent" to parallel (C-07). All flags (`--scope`, `--no-fix`, `--fail-on`, `--output`, `--diff-only`) **and the execution-evidence contract** are honored on **every** path (native adapter and sequential).

---

## Integration

This workflow can be called from:
- `/full-robust` — after base implementation.
- Directly via `/vdd-multi` — for existing code review.
- PR/CI bots via `/vdd-multi --diff-only --no-fix --fail-on=high --output=docs/reviews/pr-<N>.md`.
