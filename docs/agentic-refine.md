# Agentic Development Framework — Refinement Notes

Feedback captured after a multi-hour VDD session implementing a feature across the stack (analysis → architecture → planning → execution → deployment). The framework is project-agnostic, so these notes separate **framework-level observations** (universal) from **session examples** (specific to this project's stack — n8n + Postgres + docker-compose VM).

> **How to read session examples**: they are marked with `> Example (this project):` blocks. Replace the specifics with your own stack when applying the lesson. The underlying friction is about framework mechanics, not the stack.

---

## 1. What works well — keep it

### 1.1 Phase separation (Analysis → Architecture → Planning → Execution)

The gated sequence forced by `/vdd-start-feature` → `/vdd-plan` → `/vdd-develop` prevents the most common failure mode: **jumping to code before the problem is properly framed**. Even when the human explicitly says "just do X", the phases catch ambiguity.

> Example (this session): when the agent skipped the Architecture phase and went straight to Planning, the human caught it immediately. Without the explicit phase boundary, this would have been an invisible technical-debt injection. The catch was cheap because the framework names the phases.

**Keep**: the strict phase sequence. Don't let convenience erode it.

### 1.2 Critic/reviewer agents at phase boundaries

`task-reviewer`, `plan-reviewer`, `architecture-reviewer`, `code-reviewer` are the highest-leverage component in the framework. They consistently catch real bugs that the primary agent missed — not style nits.

> Example (this session, universal pattern): architecture-reviewer flagged **three contract-level drifts** between architecture-doc types and the task/plan specs that would have caused silent data corruption (wrong column type — `text` vs `bytea`, wrong column names in example SQL, retired env vars still listed as active). plan-reviewer caught that atomic transactions across separate n8n nodes don't exist in this engine (project-specific) — but the generalized lesson applies to any orchestrator: **if your design assumes atomicity, check the tool actually provides it.**

**Keep**: mandatory reviewer gates. Increase confidence by having reviewers produce structured diffs (e.g. "drift found at TASK:123 vs ARCH:456") rather than free-form prose.

### 1.3 Session state persistence at phase boundaries

`skill-session-state` writing to `.agent/sessions/latest.yaml` after each phase makes "resume after crash / handoff to another session" a no-op. Worth the minor overhead.

**Keep**.

---

## 2. Friction points — address before the next release

### 2.1 Over-parallelization of early-phase Explore agents

The guidance "launch up to 3 Explore agents in parallel" is too generous for early exploration. When the task is "understand the current state," 3 parallel agents produce 3× the noise with lots of overlap, not 3× the signal.

**Symptom**: ~20,000 words of reference material returned to the main context, of which maybe 30% was load-bearing for the actual plan.

**Proposed fix**:
- Default to **1 Explore agent** for first-pass reconnaissance
- Reserve parallelism for cases with **objectively orthogonal areas** (e.g., `frontend` + `backend` + `infra`, with no shared files)
- Update the `vdd-start-feature` workflow to state: "spawn 1 Explore; only fan out to 2–3 if the initial report explicitly identifies independent subsystems requiring deeper dives"

> Example (this session): three Explores were spawned to "understand the codebase for the identity feature." Agent 1 reported the reference doc's key points. Agent 2 reported the same DB tables + same workflows. Agent 3 reported the same frontend again. A single Explore with a well-scoped prompt would have returned the same signal at ⅓ the cost.

**Universal rule**: parallelism is a scalability tool, not a quality tool. More agents ≠ better analysis.

### 2.2 Developer subagent returning false-positive verification

The `developer` subagent has no deploy/test access (rightly — blast radius), but still returns `"tests_pass": true` in its structured output. This is a **false signal** — the agent is claiming tests passed when it couldn't have run them.

**Proposed fix** — change the developer agent's response contract to one of:

```json
{"tests_pass": null, "reason": "verification requires main session (no network/tool access)"}
{"tests_pass": "syntax_only", "reason": "ran local parser; no runtime verification"}
{"tests_pass": true, "verification_evidence": "..."}
```

Force the agent to justify the `true` with concrete evidence (command output, test report path), or downgrade to `null` with the blocker. This prevents silent propagation of unverified claims.

> Example (this session): developer returned `tests_pass: true` for a SQL migration file it had written but not executed. The main session discovered a real ownership issue only by running the verification queries itself. Had main session trusted the `tests_pass: true`, the bug would have shipped.

**Universal rule**: agents lacking execution rights should declare that limitation in their machine-readable output, not shadow-pass.

### 2.3 No drift detection before destructive operations

The framework has no built-in check for "local repository file vs live deployed state" drift before an agent overwrites live state with repository contents.

> Example (this session, the worst moment): the agent imported 9 workflow files from the local repo to the n8n instance. The local files turned out to be stale by ~2 weeks — someone had edited workflows through the n8n UI without committing back. The import **overwrote production with old behavior** (e.g., replaced a Switch routing node with two older IF nodes). Recovery took 30 minutes via version-history lookup.

**Proposed fix** — add a pre-apply step to `/vdd-develop` when the task involves pushing local artifacts to a live system:

```
Before APPLY:
  1. fetch live_size, live_version_count
  2. compare with local_size
  3. if |live - local| / live > 10%  OR  live_version > local_version:
       STOP. Print diff. Require explicit user confirmation.
```

This pattern generalizes beyond workflow JSONs — any "sync file to live service" operation benefits.

**Universal rule**: never overwrite live state without a freshness check. "Git is the source of truth" is a convention, not a guarantee.

### 2.4 MCP tool output truncation is silent and undocumented

When an MCP tool returns a very large response, the content is saved to disk and the agent gets a preview + path. This works, but:
- It's not covered in any skill/workflow docs
- The preview-first format means agents often miss that they need to read the full file
- Some formats save as `.json` (tool-result wrapper), others as `.txt` (raw) — inconsistent

> Example (this session): fetching a large workflow snapshot via the MCP tool hit this twice. The first attempt, the agent only read the preview and missed critical fields that were in the full file. The second attempt, it knew to parse the saved file.

**Proposed fix**:
- Document the truncation behavior in a core skill (`skill-mcp-tools-overview` or similar)
- Standardize save format — always JSON-parseable
- When an agent uses an MCP tool that produces >N KB, automatically annotate: "consider subagent for parse; do not rely on preview"

**Universal rule**: tool-result truncation is a known failure mode for long-context orchestrators. Make it loud.

### 2.5 TodoWrite nag frequency is too high

A system reminder "TodoWrite hasn't been used recently" fires every few tool calls, including cases where the agent clearly IS tracking progress. Over a long session it becomes noise that's routinely ignored — which defeats its purpose.

**Proposed fix**:
- Nag threshold: 15 minutes of real time without TodoWrite, not "N tool calls"
- Suppress nag if the last TodoWrite was within the same "work unit" (between two user messages)
- Or: replace with a smarter signal — "you have 5+ pending todos and haven't marked any complete in X minutes"

> Example (this session): ~15 nags in 6 hours. First 5 useful, remaining 10 ignored. Nag that gets ignored is worse than no nag because it trains agents to skip system reminders wholesale.

**Universal rule**: signal fatigue is a real failure mode. Nags should be rate-limited by meaningful activity, not tool-call count.

### 2.6 Over-eager `/loop` and ScheduleWakeup for monitoring

When asked to "monitor logs for 30 min," the agent scheduled a wakeup for 20 min later and continued — this was correct. But the framework doesn't surface **how to use wake-ups for post-deploy verification** as a first-class pattern. It was reinvented from scratch.

**Proposed fix** — add a `vdd-post-deploy-watch` skill that codifies:
1. Set wake-up for T+20min
2. On wake, run log-scan commands (templated)
3. On wake, check executions of cron-triggered workflows (if any)
4. On wake, report status + promote to further wake if T < 24h

---

## 3. Missing capabilities — gaps to consider

### 3.1 `/vdd-recover` workflow

When a deploy goes wrong (as happened in this session), the agent improvises recovery. There's no named playbook for:
- Identify live vs expected state divergence
- Preserve the "wrong" live state (in case it was intentional)
- Roll back via the native version system of the target tool (if any)
- Re-apply the intended change with the recovered baseline

This is a universal pattern — every non-trivial system has some recovery sequence. Codifying it as a workflow lets agents execute it confidently instead of building the procedure ad-hoc under stress.

### 3.2 Pre-deploy checklist auto-generator

Before any `apply migration`-style action, generate a checklist:
- Backup? (yes/no + evidence)
- Deactivate dependent processes? (list + status)
- Rollback plan exists? (link or inline)
- Active user requests drained? (count)

Currently this lives in the agent's head or in an ad-hoc skill. Making it a first-class artifact (like the task/plan/architecture docs) means reviewers can check it and agents can't skip it.

### 3.3 Post-deploy sanity pass

Automated run after `apply`:
- Error count in logs (last N minutes)
- Failed executions in orchestrator (if applicable)
- Database error count (if applicable)
- Performance regression signals (response time if instrumented)

Currently manual, error-prone, and inconsistently executed.

> Example (this session): the automated post-deploy sanity pass was a scheduled wake-up, written ad-hoc. It should have been one line: `/vdd-post-deploy-watch T+20min`.

---

## 4. Specific recommendations ordered by impact

| # | Recommendation | Framework impact | Effort |
|---|----------------|------------------|--------|
| 1 | Force developer subagent to declare `tests_pass: null` without evidence | Prevents silent bug propagation | Small (prompt change) |
| 2 | Add drift detection before `apply`-to-live operations | Prevents production overwrites | Medium (new skill + workflow hook) |
| 3 | Reduce default Explore parallelism from 3 to 1 for early phases | Saves context, raises signal quality | Small (workflow wording) |
| 4 | Rate-limit TodoWrite nags by wall-clock time, not tool-call count | Reduces signal fatigue | Small (nag logic) |
| 5 | Create `/vdd-recover` + `/vdd-post-deploy-watch` workflows | Formalizes common ad-hoc patterns | Medium (new workflows + skills) |
| 6 | Standardize MCP truncation format + document it | Prevents agents missing critical data | Small (doc + one format change) |
| 7 | Make reviewers emit structured drift reports (ref:line → ref:line) | Faster, less-ambiguous fix cycles | Medium (prompt + output schema) |

---

## 5. Meta-observation

The framework's strength is **gates**: each phase has a named exit criterion and a reviewer that can reject. This is under-applied in a few places:

- **Deploy phase** has no formal gate — agents just run `ssh vm ...`. Adding a `deploy-reviewer` that checks drift, backup, dependent-service state, and rollback plan would close the last gap.
- **Recovery phase** doesn't exist as a named phase — it should, with its own gate.

If the next revision adds one thing, make it "deploy is a phase, not a postscript."

---

## 6. What not to change

Two things work well and shouldn't be "improved":

1. **The gate rigidity itself** — it feels slow but catches real bugs. Resist pressure to make it skippable for "simple" tasks; those are often the ones that hurt most when skipped.
2. **Human-in-the-loop at phase boundaries** — the framework pauses for human approval at critical points. Automating these away would lose the primary safety property.
