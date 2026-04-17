[Русская версия](CHANGELOG.ru.md) | [English version](CHANGELOG.md)

<!--
## [Unreleased]

### 🇺🇸 English
#### Added
- ...

#### Changed
- ...

#### Fixed
- ...
-->

## 🇺🇸 English Version (Primary)

### **v3.14.0 — `skill-parallel-orchestration` vendor-agnostic rewrite + per-vendor reference files**

**Motivation**: the previous `skill-parallel-orchestration/SKILL.md` was authored as vendor-agnostic documentation but in practice encoded Claude Code primitives throughout (`Agent` tool, `.claude/agents/`, `subagent_type`, `TeamCreate`/`SendMessage`, "Claude Code harness permits up to 3 Explore agents"). Agents running on Gemini CLI, Cursor, Antigravity, or any other runtime had no way to apply the skill.

This release splits the methodology (universal) from the invocation syntax (vendor-specific), without breaking the Claude Code reference implementation.

#### **Added**

* **Vendor-agnostic core** — [`SKILL.md`](.agent/skills/skill-parallel-orchestration/SKILL.md) rewritten to v3.0. Now contains only universal concepts: Orchestrator/Teammate roles, Layer A vs Layer B decision criterion, three-phase protocol (Decompose → Spawn → Merge), Red Flags, Best Practices, Exploration-default-ONE rule, Merge rules. No Claude-specific tool names, paths, or syntax.

* **Per-vendor reference files** in `references/`:
  - [`references/claude-code.md`](.agent/skills/skill-parallel-orchestration/references/claude-code.md) — **complete**. Claude Code primitives: `Agent` tool, `.claude/agents/` convention, `subagent_type`, single-message multi-tool-call pattern, `requestId` parallelism verification, Layer B (`TeamCreate`/`SendMessage`) with v3.13.0 probe findings, tools whitelist convention. Paired with the existing `examples/usage_example.md`.
  - [`references/sequential-fallback.md`](.agent/skills/skill-parallel-orchestration/references/sequential-fallback.md) — **complete, universal**. Role-switching through a single session for any runtime lacking a parallel-spawn primitive. Documents trade-offs (N× slower, loses per-teammate context isolation, no Layer B), concrete single-session persona-swap protocol, and anti-patterns specific to single-session execution ("don't let critic B see critic A's output").
  - [`references/gemini-cli.md`](.agent/skills/skill-parallel-orchestration/references/gemini-cli.md), [`references/cursor.md`](.agent/skills/skill-parallel-orchestration/references/cursor.md), [`references/antigravity.md`](.agent/skills/skill-parallel-orchestration/references/antigravity.md) — **stubs**. Contain a contribution checklist and direct users to the universal fallback until filled in by someone running the framework on that vendor.

* **Reference-selection protocol** — parent `SKILL.md` §1 now mandates loading the matching reference before applying the protocol, with a runtime-indicator table (`CLAUDE.md` + `.claude/agents/` → `claude-code.md`; `GEMINI.md` → `gemini-cli.md`; `.cursor/` → `cursor.md`; fallback to `sequential-fallback.md`).

#### **Changed**

* **`examples/usage_example.md`** — header updated to mark the example as Claude Code–specific and point vendor-agnostic users at the parent `SKILL.md` + the matching reference file. Example body unchanged (it was already a Claude-specific walk-through).

* **`docs/ROADMAP.md` Wave 5** — updated from "Not started" to "Partially unlocked at v3.14.0". The methodology-level vendor split is now in place; what remains is the subagent-definition portability layer (`.agent/agents/*.md` SOT + generator script) — unblocked when a second vendor is actually adopted.

#### **Not changed**

* No changes to existing wrappers in `.claude/agents/` (still 16, unchanged).
* No changes to `/vdd-multi` workflow or its v3.13.0 parameter set.
* No behavior change for Claude Code users — the reference file preserves all v2.0 semantics.
* Deprecated `scripts/spawn_agent_mock.py` remains retired; retained only for `fcntl`-locking regression tests.

#### **Impact**

* Framework's multi-vendor claim (stated in README and CLAUDE.md) is now real at the methodology layer: universal concepts are cleanly separated from Claude-specific invocation syntax.
* Agents on non-Claude runtimes get an explicit, vendor-neutral fallback path (sequential persona-swap) that preserves all universal concepts.
* Extension point established: adopting a new vendor is a matter of filling in its `references/<vendor>.md` plus adding subagent definitions (Wave 5 remaining scope), not rewriting the skill.

---

### **v3.13.1 — External-feedback integration: 2 immediate fixes + roadmap absorption**

Applied actionable lessons from a multi-hour VDD session in an external project (captured in [docs/agentic-refine.md](docs/agentic-refine.md)). Two small high-value fixes shipped immediately; the rest integrated into [docs/ROADMAP.md](docs/ROADMAP.md) with explicit reopen criteria.

#### **Fixed — silent false-positive tests_pass (Rec #1, small)**

The `developer` subagent previously returned `tests_pass: true` in its structured output regardless of whether tests actually executed — a shadow-pass that propagated unverified claims to the orchestrator. The wrapper's return contract now requires concrete evidence:

* `tests_pass: true` is **forbidden without `verification_evidence`** (test output, report path, or command transcript).
* `tests_pass: "syntax_only"` — parser/linter ran but no runtime tests.
* `tests_pass: null` — cannot execute tests (no runtime access, sandbox, etc.); reason goes in `blocking_questions`.

This closes a known class of silent-bug propagation where developers without execution rights shadow-passed tests. The feedback source caught a real SQL-migration bug that would have shipped had the main session trusted the false `tests_pass: true`.

#### **Changed — Explore parallelism default 3 → 1 for reconnaissance (Rec #3, small)**

Added §5.1 "Explore parallelism — default to ONE" to [.agent/skills/skill-parallel-orchestration/SKILL.md](.agent/skills/skill-parallel-orchestration/SKILL.md). The Claude Code harness permits up to 3 parallel Explore agents, but the ceiling is a scalability tool, not a quality tool. First-pass reconnaissance should spawn one well-scoped Explore; fan out to 2–3 only when objectively orthogonal subsystems are identified (frontend + backend + infra, no shared files).

Observed symptom from the feedback source: three parallel Explores returned ~20k words of reference material with ~30% load-bearing content. One sharper prompt would have returned the same signal at ⅓ the cost.

#### **Deferred to [docs/ROADMAP.md](docs/ROADMAP.md) — remaining 5 recommendations + meta-observation**

Integrated as new ROADMAP entries with explicit reopen criteria:

* **Drift detection before apply-to-live operations** (Deferred, conditional on apply-to-live workflows appearing).
* **`/vdd-recover` + `/vdd-post-deploy-watch` workflows** (Deferred, conditional on Deploy-phase epic or second friction incident).
* **Deploy-as-a-phase** (potential new epic — idea level, large scope).
* **Structured drift reports from reviewers** (Nice-to-have, triggers on first human hunting through prose).
* **MCP tool truncation documentation** (Nice-to-have, conditional on MCP adoption).
* **TodoWrite nag rate-limiting** → out-of-scope (Claude Code harness-level, not this framework's source).

Full feedback artifact preserved at [docs/agentic-refine.md](docs/agentic-refine.md) for future reference.

#### **Impact**
* No behavior change in Layer A `/vdd-multi` (same 16 wrappers, same parallel critic flow).
* Developer subagent's machine-readable output is now honest about test execution status.
* Analysis/Architecture phases spawn fewer Explores by default when reconnoitering.

---

### **v3.13.0 — `/vdd-multi` parameters + Wave 4 runtime probe findings**

Adds first-class parameters to `/vdd-multi` for scoped runs, CI integration, PR reviews, and fixture preservation. Also documents the Native Teams (Layer B) runtime probe — what works, what's broken, and why Wave 4 is deferred.

#### **Added — `/vdd-multi` parameters**

Previously `/vdd-multi <path>` took only a target path. Now accepts 5 inline flags:

* `--scope=logic|security|performance|all` (comma-separated list supported) — run only selected critic(s). Saves tokens when area is known.
* `--no-fix` — skip Phase 3 iterative fix loop (report-only mode). For CI, smoke tests, pre-merge review bots.
* `--fail-on=critical|high|medium|low|none` — surface a PASS/FAIL verdict when any finding meets/exceeds the threshold. Workflow always completes; flag only controls the terminal verdict.
* `--output=<path>` — write merged report to file instead of inline; orchestrator returns a short pointer. For persistent artifacts under `docs/reviews/`.
* `--diff-only` — bound review to files in `git diff` vs `main`. Auto-on when no target is given. Critics receive changed files + per-file diff context. Primary use case: PR review.

Example CI invocation: `/vdd-multi --diff-only --no-fix --fail-on=high --output=docs/reviews/pr-42.md`.

Workflow file [.agent/workflows/vdd-multi.md](.agent/workflows/vdd-multi.md) rewritten:
* Added "Invocation / Parameters" section with flag table + examples.
* New Phase 0 ("Parse invocation") normalizes flag input + derives `git diff` target list when `--diff-only`.
* Phase 2 "Merge & deduplicate" honors `--severity` filter and derives verdict from `--fail-on`.
* Phase 3 "Iterative fix loop" skipped when `--no-fix`.
* Termination line now includes verdict + output-path pointer.
* Sequential fallback (non-Claude-Code vendors) honors all flags.

#### **Added — Wave 4 Native Teams runtime probe**

Ran a minimal `TeamCreate` + `Agent(team_name, name)` + `SendMessage` + `TeamDelete` smoke cycle to verify Layer B runtime (experimental flag `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` already set). Documented findings:

**Works**:
* `TeamCreate` creates `~/.claude/teams/<name>/config.json` + `~/.claude/tasks/<name>/.lock`.
* `Agent(team_name, name, subagent_type)` spawns teammate asynchronously (returns immediately with `agent_id`; teammate runs in background).
* Teammate executes task correctly (verified by counting `.md` files — returned 16, matches actual wrapper count).
* `SendMessage` delivers to inbox file (`~/.claude/teams/<name>/inboxes/<recipient>.json`) as JSON array with `from`, `text`, `summary`, `timestamp`, `color`, `read`.
* Shutdown round-trip (`shutdown_request` → `shutdown_approved`) completes within ~2 seconds.

**Broken or surprising** (new entries in [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)):
* **`TeamDelete` does NOT clean up after protocol shutdown**: `config.json` members array is not updated on `shutdown_approved`; `TeamDelete` fails with `Cannot cleanup team with N active member(s)`. Error message references `requestShutdown` which is not an available tool. Workaround: manual `rm -rf ~/.claude/teams/<name>/ ~/.claude/tasks/<name>/`.
* **Async spawn ≠ sync return**: unlike Layer A where `Agent` returns the subagent's result, Layer B `Agent(team_name)` returns immediately. Lead must poll inbox file or await an auto-delivered turn.
* **Model inheritance inconsistent**: `subagent_type: "Explore"` teammate defaulted to `model: "haiku"` regardless of lead's model. Must override explicitly if Opus needed.
* **Runtime sends structured JSON despite docs**: `{"type":"idle_notification",...}` and `{"type":"shutdown_approved",...}` are auto-delivered to lead's inbox even though docs say "Do NOT send structured JSON status messages". Parsers must handle both.

**Decision**: Wave 4 (full Layer B `/teams-vdd-multi` workflow) remains deferred. Layer A (parallel `Agent` spawn in one message) handles the current `/vdd-multi` use case fully, is proven twice under smoke tests (Sonnet + Opus), and has none of the Layer-B gotchas above. Wave 4 reopens only when a concrete peer-debate scenario makes the extra complexity justified.

#### **Changed**
* [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) — Native Teams section expanded with 3 new findings from the probe (TeamDelete cleanup, async spawn, model inheritance, runtime JSON messages).
* [docs/TASK.md](docs/TASK.md) — Completed Waves table adds `Wave 4 probe + /vdd-multi parameters (v3.13.0)` row.

#### **Not changed (explicit)**
* No new subagent wrappers (still 16).
* No changes to Layer A behavior — `/vdd-multi` without flags runs identically to v3.12.0.
* No Layer B workflow (`/teams-vdd-multi`) — deferred.

---

### **v3.12.0 — Agent Teams Mode Wave 3: Product-Pipeline Subagent Wrappers**

#### **Added**
* **4 new product-pipeline subagent wrappers** in `.claude/agents/` — brings total wrapper count to **16** (3 Wave-1 critics + 9 Wave-2 dev-pipeline + 4 Wave-3 product):
  - **`strategic-analyst`** (sonnet) — The Researcher. Produces `docs/product/MARKET_STRATEGY.md` (TAM/SAM/SOM, competition, timing, pre-mortem, verdict score). SOT: `System/Agents/p01_strategic_analyst_prompt.md`.
  - **`product-analyst`** (sonnet) — The Visionary. Produces `docs/product/PRODUCT_VISION.md` with INVEST stories, SMART KPIs, 10-factor viability score. SOT: `System/Agents/p02_product_analyst_prompt.md`.
  - **`product-director`** (opus) — The Gatekeeper / VC Proxy. Applies Adversarial-VDD Acid Test (hallucination check, moat check, fluff check) to Strategy + Vision. Produces `docs/product/APPROVED_BACKLOG.md` (with WSJF + `APPROVAL_HASH` via sign-off script) or `REVIEW_COMMENTS.md`. SOT: `System/Agents/p03_product_director_prompt.md`.
  - **`solution-architect`** (sonnet) — The Pragmatist. Verifies `APPROVAL_HASH` at entry (stops if missing/invalid — security violation). Produces `docs/product/SOLUTION_BLUEPRINT.md` (WHAT to build: requirements, UX flows, ROI — NOT HOW). SOT: `System/Agents/p04_solution_architect_prompt.md`.

* **`docs/ARCHITECTURE.md` §5.1** — new Wave 3 catalog table (4 rows: SOT path, tools, model, role); Model policy block updated to **10 Opus + 6 Sonnet**.

#### **Changed**
* **`planner` wrapper model: sonnet → opus** (was silently updated post-v3.11.2; now formally documented). Rationale: plan decomposition (Stub-First, atomicity, RTM coverage) has verifier-like rigor — a weak plan corrupts every downstream developer invocation. Matches the verifier-tier pattern.
* **Model policy documentation** now lists 10 Opus + 6 Sonnet roles and explains the inclusion of `planner` and `product-director` in the Opus tier.
* **`docs/TASK.md`** — TASK-060 (Wave 3) now the current active task; Completed Waves table updated with `Hardening (v3.11.1)`, `Opus upgrade (v3.11.2)`, and `Wave 3 (v3.12.0)` rows.

#### **Design decisions**
* **`product-director` is a "verifier that writes"** (unlike dev-pipeline reviewers which return text reports). SOT prescribes specific output filenames (`APPROVED_BACKLOG.md`, `REVIEW_COMMENTS.md`) that downstream agents consume contractually (`solution-architect` requires `APPROVED_BACKLOG.md` with valid hash). Wrapper body documents this exception explicitly.
* **`solution-architect` verifies `APPROVAL_HASH` at entry** — if missing/invalid, subagent STOPS and reports a security violation rather than producing a blueprint. This honors the Logic Locker from SOT §4.3.
* **No workflow rewrites in Wave 3** — consistent with Wave 2: wrappers are infrastructure. Product workflows (`/product-full-discovery`, `/product-market-only`, `/product-quick-vision`) keep working via sequential role-switching; wrappers enable parallel or named-type spawn when useful.
* **`p00_product_orchestrator_prompt.md` not wrapped** — orchestrator roles (`01`, `p00`) stay as main-agent personas because Claude Code native Teams do not support nested teams.

#### **Verified**
* All 16 wrappers: YAML frontmatter valid, `name` matches filename, thin-adapter body size unchanged (7–8 lines).
* No regression: `git diff` limited to new Wave 3 files + `docs/ARCHITECTURE.md` §5.1 + `docs/TASK.md` + changelog/readme. Wave 1/2 artifacts untouched.

#### **Out of Scope (future waves)**
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.

---

### **v3.11.2 — Verifier subagents upgraded to Opus**

All 8 verifier wrappers now run on `model: opus`; 4 builder wrappers stay on `sonnet`.

#### **Changed**
* **8 verifiers → opus**:
  - 3 adversarial critics: `critic-logic`, `critic-security`, `critic-performance`
  - 4 pipeline reviewers: `task-reviewer`, `architecture-reviewer`, `plan-reviewer`, `code-reviewer`
  - `security-auditor` (full-audit role)
* **4 builders stay on sonnet**: `analyst`, `architect`, `planner`, `developer`

#### **Rationale**
Verification is a quality gate — missed bugs, missed vulnerabilities, and approved broken architecture cost orders of magnitude more than the extra token spend. Opus's deeper reasoning, stronger adversarial thinking, and more calibrated doubt (resistance to "it probably works" rationalization) justify the cost for the verifier tier. Creation tasks are template-driven under Stub-First and follow the SOT structure; Sonnet produces equivalent artifact quality there at ~5× lower cost and lower latency.

Smoke-test cost impact: three parallel Opus critics in `/vdd-multi` ≈ 3–5× Sonnet's token cost per run. A single missed SQLi or logic regression in production easily exceeds that by orders of magnitude.

#### **Impact on behavior**
* `/vdd-multi` parallel critique now runs on Opus critics — expect slightly slower wall-clock per critic (Opus latency) but higher finding rates on edge cases and subtle adversarial scenarios. Merge/dedup rules unchanged.
* Builder-stage workflows (`analyst` → `architect` → `planner` → `developer`) see no latency or cost change.

#### **Documentation**
* [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §5.1 — added `Model` column to the 12-wrapper catalog + Model policy block explaining the split.

---

### **v3.11.1 — Thin-Wrapper Refactor + Adversarial Review Fixes**

Self-review of v3.10.0 and v3.11.0 surfaced 3 real bugs and 7 anti-patterns. This release fixes them.

#### **Fixed (HIGH — real bugs)**
* **`.agent/tools/task_id_tool.py`**: added CLI main block (`argparse` + JSON output to stdout). Was referenced in [CLAUDE.md](../CLAUDE.md#L29) (`python3 .agent/tools/task_id_tool.py <slug>`) and in the v3.11.0 `planner` wrapper, but the module had no `if __name__ == "__main__":` — running it produced empty output. Now emits `{"filename": "task-NNN-<slug>.md", "used_id": "NNN", "status": "generated|corrected", "message": null}`.
* **`.claude/agents/security-auditor.md`**: removed `Bash(python3 -m bandit:*)` from tools — bandit is not installed in the default environment, so declaring the tool was a false promise.
* **`.claude/agents/` — Bash tool syntax**: removed non-standard `Bash(cmd:*)` colon pattern from all wrappers. The subagent-frontmatter `tools` field and project [.claude/settings.json](../.claude/settings.json) `permissions.allow` are distinct mechanisms; subagent tools now list simple names only (`Read, Grep, Glob, Bash`), and settings.json governs which Bash sub-commands auto-approve vs prompt. Reviewers/critics without `Bash` in tools cannot invoke any shell command, making the read-only guarantee actually enforced.

#### **Changed — Thin-Wrapper Refactor (MED)**
All 12 wrappers rewritten as **true thin adapters**. The v3.10.0/v3.11.0 wrappers had grown to 50–90 lines each with duplicated skill lists, paraphrased SOT guardrails, and restated return-format blocks. This was a drift hazard: on SOT edits, wrappers would silently fall behind.

* **Size**: `.claude/agents/` total went from **842 lines → 160 lines** (−81%). Each wrapper is now 13–14 lines (7–8 lines body) and contains only:
  1. Frontmatter (`name`, `description`, `tools`, `model`).
  2. One-line SOT pointer: `You are the <Role> teammate. Full system prompt ... lives in [SOT path] — read and follow strictly.`
  3. `Subagent adaptations`: 1–3 bullets covering only what differs from SOT when running as subagent (primarily "return text report to orchestrator instead of writing `docs/reviews/…`").
* **No duplicated skill lists**: wrappers no longer restate SOT §2 skill loads. SOT is authoritative.
* **No cargo-cult guardrails**: wrappers no longer paraphrase SOT Prime Directives. Guardrails live in SOT.
* **No invented return formats**: wrappers link to SOT's contract; orchestrator handles the schema.
* **Consistent description grammar**: all 12 start with an infinitive action verb (`Transform`, `Review`, `Design`, `Decompose`, `Implement`, `Perform`) for more predictable auto-routing.
* **Cross-reference between `critic-security` and `security-auditor`**: both wrappers now disambiguate in their `description` field (lightweight parallel critic vs. full audit).
* **Removed aspirational `files_modified` merge claim** from `developer.md` — no such merge logic exists in the orchestrator.

#### **Changed — Docs**
* **`docs/ARCHITECTURE.md` §5.1 wrapper catalog table**: tools column now shows exact frontmatter values (no vague "git read-only" or phantom "bandit"); added a "Tools note" explaining the division between subagent `tools` frontmatter and settings.json `permissions`; design convention block updated to reflect actual ~15-line size target.

#### **Impact on behavior**
* **None expected**. Critics and reviewers continue to read the same SOT files; the SOT is where methodology lives. Wave 1 smoke-test behavior should reproduce identically (same SOT → same critique quality).
* **Maintenance improved**: edits to SOT (e.g., new skill added to `02_analyst_prompt.md` §2) propagate automatically to the `analyst` subagent on next spawn — no wrapper update needed.

#### **Verified (smoke-test on `docs/tasks/task-dummy.md`)**
* **Parallel spawn**: single LLM `requestId` (`req_011Ca9FA2hNt4PVJGVTYajEX`) across three critic `Agent` tool_uses in one message — parallelism preserved.
* **Seeded flaw coverage**: critic-logic 2/2, critic-security 4/4, critic-performance 5/5 — matches or exceeds the Wave 1 baseline (v3.10.0: 2/2, 4/4, 5/5).
* **Overlap detection**: both expected cross-category overlaps detected (line 20 flaw #5 SQLi+N+1, line 51/57 flaw #9 file-handle leak); severity escalation rule 3 applied (flaw #9: logic:HIGH + perf:HIGH → CRITICAL).
* **No hallucinations**. Bonus findings grew vs v3.10.0 (path-traversal, missing input validation, no conn pooling, `returncode` check, second-order SQL injection, ambiguous return types) — evidence that thin wrappers do not lose SOT access.
* **Fixture integrity**: `git diff docs/tasks/task-dummy.md` empty; read-only tool whitelist physically enforced (reviewers/critics without `Bash` cannot invoke shell).

---

### **v3.11.0 — Agent Teams Mode Wave 2: Dev-Pipeline Subagent Wrappers**

#### **Added**
* **9 new dev-pipeline subagent wrappers** in `.claude/agents/` (12 total after Wave 1's 3 critics). Each wrapper is a thin Claude Code adapter over `System/Agents/XX_*.md` source of truth, following Option D pattern established in Wave 1:
  - **Builders** (Write/Edit access to their artifact path):
    - `analyst` → TASK.md generator (RTM + acceptance criteria)
    - `architect` → ARCHITECTURE.md designer (Data Model → Components → Interfaces)
    - `planner` → PLAN.md + `docs/tasks/*.md` under Stub-First (uses `task_id_tool` Bash)
    - `developer` → implements atomic tasks with full Bash access
  - **Reviewers** (read-only, return text reports to orchestrator):
    - `task-reviewer` → gates Analysis→Architecture
    - `architecture-reviewer` → gates Architecture→Planning (focus: Data Model, Security, YAGNI)
    - `plan-reviewer` → gates Planning→Execution (RTM coverage, Stub-First, atomicity)
    - `code-reviewer` → gates Execution→Merge (three pillars: Compliance, Quality, Testing) with git read-only
  - **Security-auditor** → full OWASP audit with scoped scanner Bash (`run_audit.py`, `bandit`). Distinct from the Wave 1 lightweight `critic-security` used in `/vdd-multi`.
* **`docs/ARCHITECTURE.md` §5.1 — extended wrapper catalog** with all 12 wrappers, SOT paths, tools whitelist per row, and explicit "wrapper design convention" block (body ≤ ~30 lines, SOT never duplicated).

#### **Design Decisions**
* **No workflow rewrites**: unlike Wave 1 (which rewrote `/vdd-multi`), Wave 2 is pure infrastructure — existing dev-pipeline workflows (`01-04`, `vdd-*`, `develop-all`) keep working through sequential role-switching. Wrappers are *available* for parallel spawn when orchestrator decides (e.g., parallel reviewer pairs, parallel developers for independent tasks).
* **Reviewers return text reports, do not write files**: avoids giving reviewers broad filesystem Write access. Orchestrator persists to `docs/reviews/…` if needed. Same pattern as Wave 1 critics.
* **Strict tools whitelist per role**: builders write to their artifact path only; reviewers are read-only; developer has full Bash (testing, build, scripts). Enforced via frontmatter `tools` field. Verified: attempting Write inside a reviewer subagent fails with permission error.
* **Sonnet model for all 12 wrappers**: baseline choice. Future waves may downgrade specific wrappers to Haiku for cost (e.g., simple reviewers).
* **`security-auditor` ≠ `critic-security`**: full audit role (OWASP Top 10, taint analysis, CVE check, formal `docs/audit/` report) vs. lightweight parallel critic for `/vdd-multi`. Wrappers explicitly document the distinction.

#### **Changed**
* **`docs/TASK.md`** → Wave 2 (TASK-059) is now the current active task; Wave 1 (TASK-058) referenced in the Completed Waves table.
* **`docs/ARCHITECTURE.md` §5.1** — Layer A section expanded from "Wave 1 wrappers" to full 12-wrapper catalog with design convention documentation.

#### **Verified**
* YAML frontmatter validation passes for all 12 wrappers (`name` matches filename, required fields present).
* No regression: `git diff` on Wave 1 artifacts (`.agent/workflows/vdd-multi.md`, Wave 1 critic wrappers) — untouched.

#### **Out of Scope (future waves)**
* Wave 3: 4 product-pipeline wrappers (`strategic-analyst`, `product-analyst`, `product-director`, `solution-architect`).
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.
* Orchestrator prompts (`01_orchestrator.md`, `p00_product_orchestrator_prompt.md`) — native Teams don't support nested teams, these stay as main-agent role personas.

---

### **v3.10.0 — Agent Teams Mode Wave 1: Parallel VDD Multi-Adversarial Critics**

#### **Added**
* **`.claude/agents/` directory** with three thin Claude Code subagent wrappers (Option D — thin adapters over existing SOT skills):
  - `critic-logic` (read-only tools, points to `.agent/skills/vdd-adversarial/SKILL.md`)
  - `critic-security` (read-only + `git log/diff/show`, points to `.agent/skills/skill-adversarial-security/SKILL.md` + `references/prompts/sarcastic.md`)
  - `critic-performance` (read-only tools, points to `.agent/skills/skill-adversarial-performance/SKILL.md`)
* **`System/Agents/01_orchestrator.md` §5.1 — Teams Dispatch**: scenario→layer dispatch table (Layer A: `Agent` tool parallel spawn; Layer B: native `TeamCreate`/`SendMessage` — Wave 4 stub). Role-switching remains primary mode.
* **`docs/ARCHITECTURE.md` §5.1 — Two-Layer Teams Model** with ASCII diagram, shared infrastructure description (`fcntl`-locked session state, SOT-in-skills convention), vendor-portability notes.
* **`docs/KNOWN_ISSUES.md`** — Native Teams gotchas (no session resumption, task status lag, one team per session, no leadership transfer, higher token costs) + Wave 1 wrapper/SOT drift risk.
* **`docs/TASK.md` + `docs/tasks/task-058-teams-mode-wave-1.md`** — RTM with 12 acceptance criteria (R1–R12) across 8 Issues. Smoke-test passed.
* **`docs/tasks/task-dummy.md`** — deterministic smoke fixture with 9 labelled flaws (seeded across logic/security/perf) and two cross-category overlaps for verifying severity-escalation logic. Repeatable — fixture intentionally left un-fixed.

#### **Changed**
* **`.agent/workflows/vdd-multi.md`** rewritten from sequential role-switching to **parallel three-critic spawn** in a single assistant message via `Agent` tool. Phase 2 adds merge rules (location dedup ±3 lines, cross-category re-attribution, severity escalation on overlap, hallucination filter). Phase 3 iterative fix-loop uses single-critic re-spawn (cheaper than re-parallelizing). Sequential fallback documented for non-Claude-Code vendors.
* **`.agent/skills/skill-parallel-orchestration/SKILL.md` → v2.0**: removed `spawn_agent_mock.py` instructions; now references native `Agent` tool with parallel tool-uses in one message. Added Layer B stub (decision criterion: "use iff teammates need inter-teammate communication"). Red Flags and DO/DO-NOT tables updated to reflect native-spawn reality.
* **`.agent/skills/skill-parallel-orchestration/examples/usage_example.md`** rewritten around VDD multi-critic scenario; old "frontend+backend decomposition" example moved to the Layer B (Wave 4) slot.
* **`docs/ARCHITECTURE.md` §5 Parallel Execution Model (POC)** marked `[SUPERSEDED]` — retained for historical context; `fcntl`-locking notes carried forward into §5.1.
* **`.claude/settings.json`**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env flag (activates native Teams for Wave 4). Already enabled prior to commit; now formally part of Wave 1 scope.
* **`CLAUDE.md`**: added Workflow Dispatch point 3 — notes that `/vdd-multi` is parallel in Claude Code with sequential fallback elsewhere; points to orchestrator §5.1 for the layer-decision rule.

#### **Deprecated**
* **`.agent/skills/skill-parallel-orchestration/scripts/spawn_agent_mock.py`** and **`tests/test_mock_agent.py`** — module-level `DEPRECATED` docstrings. Scripts retained only to exercise `fcntl`-locking regression tests in `update_state.py`; do not reference from new workflows.
* **`docs/POC_PARALLEL_AGENTS.md`** → moved to `docs/archives/POC_PARALLEL_AGENTS.md` with `SUPERSEDED` header. Open Question #1 (CLI agent-spawn availability) marked closed — native `Agent` tool fills the gap.

#### **Verified**
* Smoke test: single LLM `requestId` observed across all three critic `Agent` tool_uses (`req_011Ca9BWa5rbziH6xcocS57c`) — parallel spawn confirmed via JSONL log analysis. All three critics returned structured `issues-found` reports; merged report deduped 14 issues with 2 cross-category escalations (flaws #5 SQLi+N+1 on fixture line 23, flaw #9 file-handle leak on lines 56–57). No hallucinations; bonus findings (path-traversal, dead API_KEY, missing authn) validated that critics correctly loaded SOT checklists.
* Regression: standard `/vdd` (sequential role-switching) untouched — verified by inspection.

#### **Out of Scope (future waves)**
* Wave 2: 9 wrappers for `System/Agents/02–10` (dev pipeline).
* Wave 3: 4 wrappers for product pipeline (`p01–p04`).
* Wave 4: Layer B implementation (`/teams-vdd-multi` workflow using native `TeamCreate`/`SendMessage`).
* Wave 5: portable generator if a second vendor (Codex, Antigravity) needs subagent support.

---

### **v3.9.17 — Developer Discipline: Karpathy Guidelines Integration**

#### **Added**
* **§1.5 Think Before Implementing** (`developer-guidelines`): Graduated ambiguity handling protocol — critical ambiguity goes to TASK.md Open Questions, implementation-level decisions are made by the developer with brief documentation, trivial decisions are made silently.
* **§1.6 Implementation Discipline** (`developer-guidelines`): Two-level decision framework — architectural decisions (new modules, public API, data models) must come from PLAN.md/ARCHITECTURE.md; implementation details (internal patterns, helpers, abstractions) are the developer's professional judgment. Speculative complexity is prohibited.
* **§6.2 Multi-Step Tasks** (`developer-guidelines`): Generalized Verification Protocol with `Step → verify: [check]` pattern, extending the Bug Fixing Protocol to all multi-step work.
* **Before/after code examples** (`developer-guidelines/examples/coding-anti-patterns.md`): 3 real-world examples — drive-by refactoring, speculative features vs. plan-driven implementation, silent interpretation vs. surfacing ambiguity. Adapted from Karpathy Guidelines for complex product development context.

#### **Improved**
* **Red Flags** (`developer-guidelines` §0): +2 entries — against silent architectural changes and speculative features.
* **Strict Adherence** (`developer-guidelines` §1): +2 entries — Task Traceability (every change must serve the task, professional choices within scope are OK) and Style Matching (match existing code style).
* **Rationalization Table** (`developer-guidelines` §9): +3 entries covering speculative additions, silent plan deviation, and drive-by improvements.
* **Atomicity & Traceability** (`core-principles` §1): Added Verification Checkpoints for multi-step tasks.
* **Minimizing Hallucinations** (`core-principles` §3): Added Ambiguity Protocol with cross-reference to developer-guidelines §1.5.
* **Token budget** (`skill-phase-context`): Updated Development phase estimate from ~768 to ~1,100 to reflect expanded developer-guidelines.

#### **Design Decisions**
* **"Implementation Discipline" instead of "Simplicity First"**: Karpathy's "minimum code" principle was adapted for complex product development — architectural complexity is valid when plan-driven; only speculative complexity is prohibited.
* **Graduated Ambiguity instead of "ask everything"**: Three-tier protocol prevents bombarding users with questions while ensuring critical decisions are surfaced.
* **No new standalone skill created**: All changes integrated into existing `developer-guidelines` (Tier 1) and `core-principles` (Tier 0) to avoid skill bloat and tier conflicts.

---

### **v3.9.16 — Security Audit v3.2: Smart Contract Patterns & Modular Architecture**

#### **Added**
* **Solidity/Smart Contract patterns** (16 new): Reentrancy (`.call{value:}`, `.send()`, `.transfer()`), arbitrary execution (`delegatecall`, `selfdestruct` EIP-6780, `suicide()`), access control (`tx.origin`, public/external without modifier), oracle manipulation (`getReserves()`, `latestRoundData()`), unchecked return values, unprotected initializers, integer overflow (pre-0.8.0), locked ether, inline assembly.
* **VDD Round 3 critique** document with real hack coverage matrix (Dec 2025 – Mar 2026).
* **Real-world hack validation**: Scanner tested against contracts simulating SwapNet ($13.4M), Truebit ($26.4M), YieldBlox ($10.2M), Aperture ($4M) attack vectors — 7/10 vectors fully detected.

#### **Improved**
* **Modular scanner architecture**: Refactored 886-line monolith `run_audit.py` into 7-file package (`audit/config.py`, `audit/patterns.py`, `audit/helpers.py`, `audit/scanners.py`, `audit/external.py`, `audit/__init__.py`).
* **MAX_FILE_SIZE consistency**: Added 5MB file size guard to `scan_configuration()` and `scan_iac()`.
* **Pattern count**: 105 → 121 total patterns (28 secret + 62 dangerous + 25 IaC + 6 config).

#### **Fixed**
* **VDD Round 2** (8 issues): `os.popen()` CWE misclassification, missing `subprocess.run shell=True`, Flask open redirect regex, SQL `%` formatting detection, IaC false positives on non-IaC YAML, symlink following, SSRF pattern expansion.

---

### **v3.9.15 — Claude Code Integration**

#### **Added**
* **Claude Code entry point**: Created `CLAUDE.md` (136 lines) adapted from `GEMINI.md` with native Claude Code tool references (Read, Write, Edit, Bash, Grep, Glob), session state bootstrap, and explicit tier-based skill loading protocol.
* **Claude Code hooks**: Added `.claude/settings.json` with `PostToolUse` hook and `.claude/hooks/validate_skill_hook.sh` for automatic skill validation on file modification.
* **Claude Code commands**: Created 20 slash command files in `.claude/commands/` covering all 21 workflows (delegator pattern — single source of truth in `.agent/workflows/`).
  * Core: `/start-feature`, `/plan`, `/develop`, `/develop-all`, `/light`
  * VDD: `/vdd`, `/vdd-start-feature`, `/vdd-plan`, `/vdd-develop`, `/vdd-adversarial`, `/vdd-multi`
  * Pipelines: `/full`, `/security-audit`, `/base-stub-first`, `/framework-upgrade`, `/iterative-design`
  * Product: `/product-full-discovery`, `/product-market-only`, `/product-quick-vision`
  * Docs: `/update-docs`
* **Migration specification**: Added `docs/migration-to-claude.md` with full platform comparison, tool mapping, hook adaptation guide, and validation checklist.

#### **Improved**
* **AGENTS.md**: Added missing "Session State Persistence" instruction (`update_state.py` on phase boundaries), achieving parity with `GEMINI.md`.
* **SESSION_CONTEXT_GUIDE.md**: Added Section 5 "Platform Memory Integration" documenting how framework session state complements platform-specific memory systems (Claude Code, Cursor, Gemini).
* **README.md / README.ru.md**: Updated "Option C: Claude Code" section — replaced manual setup instructions with ready-to-use configuration and full command list.

---

### **v3.9.14 — Enterprise Hardening Wave (BI-001..009)** (Security / Reliability / Governance)

#### **Added**
* **Governance docs**:
    * Added `System/Docs/SOURCE_OF_TRUTH.md` with authoritative mappings for prompts, skills, workflows, tools, and command conventions.
    * Added `System/Docs/RELEASE_CHECKLIST.md` with release gates and mandatory validation commands.
* **Validation and guardrail scripts**:
    * Added `System/scripts/check_prompt_references.py`, `System/scripts/security_lint.py`, `System/scripts/smoke_workflows.py`, `System/scripts/validate_skills.py`, and `System/scripts/doctor.py`.
* **CI gatekeeping**:
    * Added `.github/workflows/framework-gates.yml` to enforce tooling tests, skill validation, workflow smoke checks, reference integrity, and security linting.
* **Regression coverage**:
    * Added `tests/test_tool_runner_security_contract.py`, `tests/test_spec_validator.py`, and `tests/test_product_handoff_scripts.py`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Structured Evals Workflow**: Added a full section for defining and running vendor-agnostic tests (evals) for skills using LLM-as-a-judge (`evals/evals.json`).
    * **Agent Prompts**: Moved 3 ready-to-use prompts to `agents/` for automated skill evaluation (`grader.md`, `comparator.md`, `analyzer.md`).
    * **Reporting Scripts**: Added infrastructure to `scripts/` for processing evaluator results (`aggregate_benchmark.py`, `generate_report.py`, `generate_review.py`).
    * **JSON Schemas**: Added `references/eval_schemas.md` defining a Single Source of Truth for 8 JSON evaluation formats.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Phase 1.7 (Behavioral Analysis)**: Added a new audit phase to review usage logs and recommend extracting FAQs to `references/` and helpers to `scripts/`.

#### **Improved**
* **Tool execution security (BI-001)**:
    * Hardened `System/scripts/tool_runner.py` command policy (`shell=False`, disallowed shell chars/operators, allowlist checks, timeout handling, normalized `cwd` checks).
    * Expanded and aligned tool schemas in `.agent/tools/schemas.py`; updated runtime docs in `System/Docs/ORCHESTRATOR.md`.
* **Workflow and path integrity (BI-002, BI-009)**:
    * Repaired stale prompt/workflow references across workflow files and READMEs.
    * Standardized command conventions to canonical `run <workflow-name>` with explicit slash alias notes.
* **Python environment standardization (BI-004)**:
    * Added pinned dev dependencies (`requirements-dev.txt`) and setup guidance in `README.md` and `README.ru.md`.
* **Skills standardization, technical scope (BI-007)**:
    * Added missing `tier`/`version` metadata where absent.
    * Relaxed strict CSO prefix enforcement for existing stable skills to avoid forced legacy rewrites.
* **Meta-skill execution policy hardening**:
    * Updated `.agent/skills/skill-creator/SKILL.md` and `.agent/skills/skill-creator/assets/SKILL_TEMPLATE.md` with explicit sections: `Execution Mode`, `Script Contract`, `Safety Boundaries`, and `Validation Evidence`.
    * Extended `.agent/skills/skill-creator/scripts/validate_skill.py` with warning-first execution-policy checks and optional strict mode (`--strict-exec-policy`).
    * Extended `.agent/skills/skill-enhancer/scripts/analyze_gaps.py` with execution-policy gap detection (missing contract sections + script/scope safety signals).
    * Updated `.agent/skills/skill-enhancer/references/refactoring_patterns.md` with migration patterns: prompt-only -> hybrid, ad-hoc script -> governed script, unsafe mutation -> scoped mutation.

* **Skill validator operational alignment (BI-007 follow-up)**:
    * Added `validation.inline_exempt_skills` in `.agent/rules/skill_standards.yaml` for legacy full-context skills that must keep large inline blocks.
    * Updated `.agent/skills/skill-creator/scripts/validate_skill.py` to skip inline-size enforcement for explicitly exempted skills while keeping the default limit for new skills.
* **Skill-creator defaults discoverability**:
    * Added `.agent/skills/skill-creator/references/default_parameters.md` with configuration resolution order, bundled defaults, runtime fallbacks, and maintenance rule.
    * Updated `.agent/skills/skill-creator/SKILL.md` to reference the defaults map and `skill_utils.py` for effective merged-config inspection.
* **Release checklist scope tuning**:
    * Updated `System/Docs/RELEASE_CHECKLIST.md`: product handoff safety checks are optional and required only when modifying `skill-product-handoff`.
* **skill-creator v1.3 (Anthropic Skill Standards Sync)**:
    * **Graduated Instructions**: Replaced strict `MUST/ALWAYS` constraints with a two-tier approach (`MUST + explanation` for safety, `explain why + do` for behavioral tuning).
    * **Description Pushiness Optimization (CSO)**: Expanded SEO-optimization guidelines for skill descriptions, advocating for more aggressive triggers.
    * **Behavior Iteration Loop**: Added a step in skill creation to extract repetitive agent code/questions into `scripts/` or `references/`.
    * **Environment Adaptation**: Added recommendations for Fallback strategies for skills relying on specific CLIs or browsers.
    * **Target Audience Selection**: Guidelines now require explicitly defining the target audience before writing.
* **skill-enhancer v1.2 (Anthropic Skill Standards Sync)**:
    * **Graduated Language Check**: `analyze_gaps.py` and pipeline instructions now evaluate using the two-tier motivation system. Updates internal VDD checklists and refactoring patterns.
    * **Description Pushiness Check**: Added rules to verify the "aggressiveness" of triggers in skill descriptions.
    * **Test Coverage Check**: Final VDD Check now enforces the presence of at least 2-3 test prompts (either in `evals.json` or text).
    * **Generalization Check**: Added audit to prevent overfitting of skills to overly narrow examples.
    * **Agent References**: Local references to SSoT agents (`skill-creator/agents/`) updated.

#### **Fixed**
* **Spec validator correctness (BI-003)**:
    * Fixed requirement ID matching logic in `.agent/skills/skill-spec-validator/scripts/validate.py` (literal token handling + regression tests).
* **Product handoff hardening (BI-008)**:
    * Hardened `.agent/skills/skill-product-handoff/scripts/sign_off.py`, `.agent/skills/skill-product-handoff/scripts/verify_gate.py`, and `.agent/skills/skill-product-handoff/scripts/compile_brd.py` with argparse CLI, explicit file args, and safe path validation.
* **Artifact memory hardening, technical part (BI-006)**:
    * Extended `.agent/skills/skill-update-memory/scripts/suggest_updates.py` with deterministic bootstrap controls:
        * Added `--mode bootstrap` + `--create-missing` for controlled initial memory file generation.
        * Added explicit development scope via `--development-root` (default: `src`).
        * Added hard exclusions for `/.agent/skills/*` and `/.cursor/skills/*` to prevent unintended memory-file creation in skills catalogs.
        * Preserved graceful behavior when `.AGENTS.md` is missing (no hard failure).
    * Aligned workflow/docs contract for migration usage:
        * Updated `.agent/workflows/04-update-docs.md` bootstrap command to use `--development-root src`.
        * Updated `System/Docs/SOURCE_OF_TRUTH.md` and skill docs to reflect optional `.AGENTS.md` + scoped bootstrap policy.
* **skill-creator v1.3**:
    * Updated `validate_skill.py`: `agents/` and `evals/` directories are now whitelisted to avoid false-positives during strict checks.
    * Corrected typos in JSON keys in `SKILL.md` examples for strict schema compliance (`input_files` -> `files`, `expected_outcomes` -> `expectations`).
* **skill-enhancer v1.2**:
    * `analyze_gaps.py`: Improved markdown parsing to prevent false-positives for missing `Phase/Step` prefixes inside JSON blocks.
    * Cleaned up phantom links to "(Coming in Iteration 2)" — all declared architecture now actually exists.

#### **Verified**
* `System/scripts/check_prompt_references.py --root .` and `System/scripts/smoke_workflows.py --root .` pass in the target repository.
* Backlog status alignment: BI-001..006, BI-008, and BI-009 are marked `Done` in `Backlog/archive/framework_improvements_20260219.md`.

---

### **v3.9.13 — Security Audit Enhancement & Workflow Alignment** (Feature / Maintenance)

#### **Added**
* **Developer Guidelines**:
    * **Security Quick-References**: Added condensed guides for 10 frameworks (Flask, Django, FastAPI, Express, Next.js, React, Vue, jQuery, JS General, Go).
    * **Dynamic Loading**: Updated `SKILL.md` (v1.1) to dynamically load strict security references based on project context.

#### **Refactored**
* **`security-audit` Workflow**:
    * **Unified Script**: Updated `.agent/workflows/security-audit.md` to use the unified `run_audit.py` script.
    * **Modernization**: Removed outdated prompt references and aligned manual review steps with the "Think Like a Hacker" protocol.
* **`skill-adversarial-security` (v1.1)**:
    * **Gold Standard**: Added strict "Red Flags" (Anti-Rationalization) and "Rationalization Table" (Developer Excuses).
    * **Cleanup**: Removed duplicate sections and updated script execution commands to match v2 standards.
    * **Verification**: Verified integration with `vdd-adversarial` and `vdd-multi` workflows.

#### **Improved**
* **`security-audit` (v2.1)**:
    * **Unified Scanner**: Merged `run_audit.py` to combine internal static analysis (Secrets, Dangerous Patterns) with external tool runners (`slither`, `bandit`, `npm audit`).
    * **Gold Standard Compliance**: Added "Red Flags" (Anti-Rationalization), detailed reporting standards, and mandatory "Think Like a Hacker" checklists.
    * **OWASP 2025**: Updated checks to match the latest OWASP Top 10:2025 standards (Supply Chain Security, Exceptional Conditions).
    * **Checklist Restoration**: Explicitly linked and mandated usage of `solana_security.md`, `solidity_security.md`, and `fuzzing_invariants.md`.

#### **Fixed** *(VDD Adversarial Hardening)*
* **Security References**:
    * Fixed factual inaccuracies in `flask.md` (deprecated `FLASK_ENV`, `safe_join` CVE) and `django.md` (middleware ordering) via VDD Adversarial Review.
* **`run_audit.py`**:
    * Silent `except: pass` → stderr logging + `skipped_files` counter in report.
    * Self-flagging false positives → self-exclusion via `_is_self_path()`.
    * Substring-based `SKIP_DIRS` → basename matching (`dirs[:]` pruning).
    * `run_command` now captures and reports external tool exit codes.
    * Added 120s timeout on all `subprocess.run` calls.
    * Extended `SKIP_DIRS` with `.cache`, `.idea`, `.vscode`, `vendor`, `tmp`, `coverage`.
* **`SKILL.md`**: Fixed OWASP category mappings (Secrets→A02, Deps→A06, Patterns→A03, Config→A05). Added Rationalization Table (Section 6).
* **`owasp_top_10.md`**: Resolved duplicate A10 (merged SSRF into unified A10). Merged A08 into A03.


---


### **v3.9.12 — Framework Consistency, Parallel Agents & Safety Fixes** (Feature / Bugfix)

#### **Added**
* **Parallel Agent Architecture (POC)**:
    * **New Skill: `skill-parallel-orchestration` (Tier 2)**: Protocol for decomposing tasks into parallel sub-tasks and spawning sub-agents (mock runner).
    * **Concurrent State Safety**: `update_state.py` now uses `fcntl` file locking for atomic read-modify-write on `latest.yaml`, preventing race conditions.
    * **Mock Agent Runner**: `spawn_agent_mock.py` simulates async agent execution with state updates.
    * **Documentation**: `docs/POC_PARALLEL_AGENTS.md` guide and `docs/ARCHITECTURE.md` updated with Parallel Execution Model.
* **Skill Validation Hook**:
    * **`.gemini/hooks/validate_skill_hook.sh`**: `AfterTool` hook that auto-validates skills via `validate_skill.py` on every write to `.agent/skills/`.
    * **`.gemini/settings.json`**: Hook configuration with `$GEMINI_PROJECT_DIR` fallback for cross-runner compatibility.
    * **Skill Creation Gate**: Added mandatory `init_skill.py` rule to `GEMINI.md` and `AGENTS.md` Development Phase. Manual skill creation is now prohibited.

#### **Improved**
* **VDD Skills (v1.1)**:
    * **`vdd-adversarial`**: Added **Red Flags** (Anti-Rationalization), **Rationalization Table**, and explicit `examples/` reference.
    * **`vdd-sarcastic`**: Added **Red Flags** (Anti-Rationalization), **Rationalization Table**, and explicit `examples/` reference.

#### **Fixed**
* **Data Loss Prevention**: Patched `trigger_technical.py` to abort if `docs/TASK.md` already exists, preventing accidental overwrites during product handoff.
* **Protocol Integrity**: Updated `light-02-develop-task` workflow to enforce mandatory `.AGENTS.md` updates, preventing memory drift in Light Mode.
* **Standardization**: Updated `vdd-01-start-feature` to use the authoritative `skill-archive-task` protocol instead of hardcoded manual steps.
* **Shell Injection (VDD)**: Replaced heredoc interpolation with `jq -n` in `validate_skill_hook.sh` to prevent malformed JSON from `validation_output`.
* **Invalid Mode (VDD)**: Fixed `spawn_agent_mock.py` using non-existent mode `"Wrapper"` → `"EXECUTION"`.

---



### **v3.9.11 — Hardened Pipeline & Self-Improvement System** (Feature)

#### **Added**
* **New Skill: `skill-spec-validator` (Tier 2)**:
    * **RTM Validation**: Mechanically enforces that `docs/TASK.md` contains a Requirements Traceability Matrix.
    * **Atomic Planning**: Mechanically enforces that `docs/PLAN.md` covers every RTM item with an ID-tagged task (e.g., `[R1]`).
* **New Skill: `skill-self-improvement-verificator` (Tier 3)**:
    * **Meta-Audit**: Acts as a "Guardian" for the framework itself. Audits specifications for `framework-upgrade` to prevent regression.
* **New Workflow: `/framework-upgrade`**:
    * Specialized pipeline for upgrading Prompts, Skills, and System Logic.
    * Integrates `skill-self-improvement-verificator` gates at Analysis and Planning stages.
* **Documentation**:
    * **Claude Code & Gemini CLI**: Added native integration guides (Options C & D) in READMEs.
    * **Concept Deep Dive**: Added "Blueprint vs Driver" explanation to clarify `00_agent_development.md` vs `AGENTS.md` roles.
    * **Usage Scenarios**: Added practical examples for Standard, Light Mode, and Session Restoration workflows.

#### **Improved**
* **Workflows**:
    * **`/vdd-enhanced`**: Upgraded to "Hardened Mode". Now includes `skill-spec-validator` checkpoints with auto-correction loops (Max 3 retries).
* **Agent Prompts**:
    * **Analyst**: Mandates RTM table generation (except for `[LIGHT]` tasks).
    * **Planner**: Mandates Atomic Checklists with Strict ID linking.
    * **Developer**: Enforces Strict Stub-First methodology (except for `[LIGHT]` tasks).
* **Reliability**:
    * **`skill-creator`**: now outputs mandatory cleanup instructions to prevent debris.
    * **`validate.py`**: robustness fix for parsing Markdown tables with escaped characters.

---


### **v3.9.10 — Skill Creator Cleanup & Brainstorming 2.1** (Optimization)

#### **Improved**
* **`skill-creator`**:
    * **Cleanup Protocol**: Added specific instructions to remove unused placeholder directories (`scripts/`, `assets/`, `references/`) after skill initialization.
    * **Validation**: Verified that `validate_skill.py` supports "lean" skills without empty folders.
* **`brainstorming`** (v2.1):
    * **Universal Gold Standard**: Upgraded to v2.1 with "Universal" compatibility (tool agnostic).
    * **3-Tier Assessment**: Implemented **Trivial/Medium/Complex** complexity classification with tailored protocols for each.
    * **Safety Guardrails**: Added strict "No Coding without Design" rules and Handover Templates.

---

### **v3.9.9 — Skill Resources Migration & Validation Hardening** (Optimization)

#### **Refactored**
* **Skill Standardization (Gold Standard)**:
    * **Directory Hygiene**: Migrated `resources/` folders to `assets/` (templates) and `references/` (knowledge) across all skills.
    * **Legacy Removal**: Deprecated `resources/` directory to strictly enforce Semantic Folder Structure.

#### **Fixed**
* **Validation**:
    * **Config Support**: Updated `validate_skill.py` to explicitly allow `config/` directories (restoring support for `skill-product-solution-blueprint`).
    * **CSO Violations**: Fixed description prefixes in 6 skills (`developer-guidelines`, `requirements-analysis`, etc.) to meet "Gold Standard" compliance (`Use when`, `Guidelines for`).

#### **Verified**
* **Global Audit**: Ran verification script on all migrated skills to ensure 0 broken links and 100% validation pass rate.

---

### **v3.9.8 — Meta-Skills Independence** (Refactoring)
#### **Decoupled**
* **Project-Agnostic Meta-Skills**: `skill-creator` and `skill-enhancer` are now fully portable and independent of the Antigravity project.
    * **Configurable**: Policies (Tiers, Banned Words, File Rules) are now loaded from `.agent/rules/skill_standards.yaml` instead of hardcoded Python dicts.
    * **Zero-Dependency**: Removed `PyYAML` dependency. Implemented a custom "Vanilla Python" parser (`skill_utils.py`) to ensure tools run on any environment without `pip install` or `venv`.
    * **Documentation**: Removed hardcoded references to `System/Docs/SKILLS.md` and "Gemini/Antigravity". Replaced with generic "Skill Catalog" concepts.

#### **Added**
* **New Manual**: `System/Docs/skill-writing.md` — A portable User Guide for using the meta-skills (Install, Config, Usage).
* **Resilience**: Scripts now include a **Bundled Default Config** (`skill_standards_default.yaml`) for instant drop-in usage if project config is missing.

#### **Refined**
* **Hybrid Folder Structure**: Refactored `skill-creator` and `skill-enhancer` to use a semantic folder standard:
    * `examples/` (Train): Few-shot examples for the agent.
    * `assets/` (Material): User-facing templates and output files.
    * `references/` (Knowledge): Heavy context, specs, and guidelines.
    * `scripts/` (Tools): Python automation.
    * *Deprecated `resources/` in favor of more specific `assets/` and `references/`.*

#### **Verified**
* **E2E Testing**: Validated proper functioning of dynamic tiers, parser correctness (including edge cases like inline dicts), and gap analysis on a test skill.
* **Migration**: Successfully migrated `skill-creator` and `skill-enhancer` to the new structure without data loss.

---

### **v3.9.7 — Skill Best Practices & AGI-Agnostic Hardening** (Optimization)

#### **Added**
* **Extended Best Practices Integration**:
    * **Checklist Workflows**: Added native support for the "Checklist Pattern" in `SKILL_TEMPLATE.md` and `skill_design_patterns.md`.
    * **Gerund Naming**: `init_skill.py` now advises users to use Action-Oriented naming (e.g., `processing-files`).
    * **POV Detection**: `analyze_gaps.py` now flags First/Second person POV ("I can...", "You can...") to enforce Third-Person objectivity.
    * **Anti-Patterns**: `analyze_gaps.py` now detects Windows-style paths (`back\slashes`) to ensure cross-platform compatibility.
* **Logic Hardening**:
    * **"Solve, Don't Punt"**: Explicitly banned "Try to..." language in favor of deterministic scripts.
    * **Rationalization Table**: Built-in to default templates to preemptively block agent excuses.

#### **Improved**
* **`analyze_gaps.py`**:
    * **False Positive Reduction**: Fixed regex to ignore quoted words (e.g., prohibiting "should" no longer flags the rule itself) and Markdown tables.
    * **Robust Parsing**: Enhanced Windows path detection to handle mixed text/code contexts.
* **`skill-creator`**:
    * **Self-Sufficiency**: Added `skill_design_patterns.md` resource to decouple the skill from external docs.
    * **TDD Integration**: Evaluation-Driven Development is now a core pattern.

#### **Verified**
* **VDD Round 3**: Created an adversarial `bad-skill-helper` with intentional violations. The system successfully detected and flagged all anti-patterns (Vague Name, POV, Windows Paths).

---

### **v3.9.7 — Iterative Design & VDD Robustness** (Feature)

#### **Added**
* **New Workflow: `/iterative-design`**:
    * **Concept Loop**: brain storm -> Spec Draft -> VDD Audit -> Human Review -> Refinement.
    * **Human-in-the-Loop**: Explicit checkpoints for user feedback before coding.
* **New Skill: `brainstorming` (Tier 2)**:
    * **Pre-Planning**: Specialized instructions for research and idea generation.
    * **Anti-Hallucination**: Strict "NO CODING" rules during brainstorming phase.

#### **Fixed**
* **VDD Artifact Consistency**:
    * **Logic Gap Closed**: Fixed issue where `iterative-design` requested a report but `vdd-adversarial` had no template.
    * **Templates**: Added `resources/template_critique.md` to `skill-vdd-adversarial` for standardized auditing.
    * **Rich Skill**: Refactored `vdd-adversarial` to meet `skill-enhancer` standards (Resources separation).

---

### **v3.9.6 — Evolved TDD & Strict Reliability** (Feature)

#### **Added**
* **New Skill: `tdd-strict` (Tier 3)**:
    * **High Assurance Mode**: Enforces "Mechanical Verification" (Failing test MUST match `EXPECTED_FAIL_REASON`).
    * **Law of Minimalism**: Explicitly bans speculative coding and dead code.
    * **Self-Contained**: Can be loaded independently of Tier 1 skills.
* **Bug Fixing Protocol (Universal)**:
    * Added to `developer-guidelines` (Section 6).
    * Mandates "Reproduce First" rule for ALL bug fixes (Tier 1).

#### **Improved**
* **Checklists**:
    * **`code-review-checklist`**: Added "High Assurance" section for verifying strict TDD compliance.
    * **`plan-review-checklist`**: Added check for planning Strict Mode usage.
* **Workflows**:
    * Updated `/full-robust` pipeline to automatically load `tdd-strict` for maximum reliability.
* **Documentation**:
    * Updated `System/Docs/SKILLS.md` with Tier 3 definitions.
    * Updated `System/Docs/WORKFLOWS.md` to reflect strict integration.

---

### **v3.9.5 — Skill Hardening & Gold Standard Refactoring** (Optimization)

#### **Refactored (Gold Standard)**
* **`documentation-standards`**:
    * **Token Optimization**: Extracted inline templates to `resources/templates/` (60%+ reduction).
    * **Richness**: Added `examples/good_documentation.py` (Gold Standard example).
    * **Resilience**: Added "Red Flags" and "Rationalization Table".
* **`skill-planning-format`**:
    * **Token Optimization**: Extracted massive templates (`PLAN.md`, `TASK.md`) to `resources/templates/`.
    * **Richness**: Added `examples/PLAN_EXAMPLE.md` and `examples/TASK_EXAMPLE.md`.
* **`skill-task-model`**:
    * **Richness**: Extracted inline Use Case examples (Good/Bad) to `examples/`.
    * **Resilience**: Added "Red Flags" and "Rationalization Table".

#### **Fixed**
* **`light-mode`**: Fixed YAML syntax error (`[LIGHT]` tag unquoted) and CSO violation in description.
* **`skill-safe-commands`**: Updated documentation to allow `AGENTS.md` configuration.

#### **Improved**
* **System Resilience**:
    * **No-Dependency Parsing**: Removed `PyYAML` dependency from `validate_skill.py` and `analyze_gaps.py`.
    * **Robust Parsing**: Implemented manual YAML parser handling quotes, lists, and comments gracefully.
* **CSO Schemas**: Updated `skill-creator` and `skill-enhancer` to allow richer description prefixes: `Use when`, `Guidelines for`, `Standards for`, `Defines`, `Helps with`.

---

### **v3.9.4 — Product Skills Deepening & Refactoring** (Optimization)

#### **Refactored**
* **Strategic Analyst (`p01`):**
    * Refactored Prompt: Removed inline template, added `Execution Loop` with Deconstruct/Timing/Moat steps.
    * Updated Skill `skill-product-strategic-analysis`:
        * Added `market_strategy_template.md` (Core Thesis, Moat Score, Risks).
        * Added Example `01_strong_ai_assistant.md` (Strong Go).
        * Added Example `02_nogo_vertical_video.md` (No-Go).
* **Product Analyst (`p02`):**
    * Refactored Prompt: Added `User Refinements` input, delegated Vision generation to Skill.
    * Updated Skill `skill-product-analysis`:
        * Updated `vision_template.md` (Core Pillars, Moat Score, Emotional Logic).
        * Added rigorous examples: `01_strong_go_devboost`, `02_consider_talentflow`, `03_nogo_quickbites`.
* **Solution Architect (`p04`):**
    * Refactored Prompt: Removed duplicated template.
    * Updated Skill `skill-product-solution-blueprint`:
        * Updated `solution_blueprint_template.md` (Unit Economics, Verdict).
        * Updated `calculate_roi.py` to output ARPU, CAC, LTV/CAC.
        * Added examples: `01_simple_flexarb` and `02_advanced_loyaltyhub`.
* **Director (`p03`):**
    * Refactored Prompt: Integrated `skill-product-backlog-prioritization`.
    * Added Step 3: Auto-Prioritization (WSJF) before sign-off.
    * Added Step 4: Auto-Hash generation via `sign_off.py`.

#### **Improved**
* **Consistency:** All Product Agents (`p01`, `p02`, `p04`) now use a unified "Prompt → Skill → External Template" architecture.
* **Scoring:** Implemented quantitative scoring (10-factor matrix) and "Verdict" logic across all product artifacts.

---

### **v3.9.3 — Documentation Hygiene & JSON Enforcement** (Maintenance)

#### **Changed**
* **Documentation Standardization:**
    * **JSON Enforcement:** Updated `skill-product-solution-blueprint` to strictly enforce `.json` for `calculate_roi.py` inputs (removed ambiguous YAML references).
    * **Path Hygiene:** Standardized temporary artifact location to `docs/product/` (e.g., `docs/product/stories.json`).
* **Resource Structure:**
    * Flattened template structure in `skill-product-solution-blueprint` (moved `resources/templates/` -> `resources/`).
    * Updated `SKILL.md` to reference the canonical `solution_blueprint_template.md`.

---

### **v3.9.2 — Product Skills Refactoring & Math Hardening** (Optimization)

#### **Added**
* **Advanced Financials:** `calculate_roi.py` now supports:
    * **Granular Sizing:** T-Shirt sizes (XS-XXL) mapped to hours via `sizing_config.json`.
    * **LLM Acceleration:** "Friendliness" score discounting based on global factors.
    * **Metrics:** NPV (3yr), LTV, CAC, and Payback estimations.
* **Product Scoring:** New `score_product.py` implementing 10-Factor Matrix (Problem Intensity, Moat, etc.).
* **Documentation:**
    * `System/Docs/PRODUCT_CALCULATIONS_MANUAL.md`: Detailed "Magic Math" FAQ.
    * Updated `System/Docs/PRODUCT_DEVELOPMENT.md` with Calculation Manual reference.

#### **Optimized**
* **Prioritization:** `calculate_wsjf.py` now natively supports T-Shirt sizes (S, M, L) mapped to Fibonacci.
* **Security (VDD):**
    * Hardened `calculate_roi.py` against "Time Travel" bugs (negative duration).
    * Clamped `score_product.py` inputs (1-10) to prevent overflow.
    * Removed `PyYAML` dependency for lighter execution.

---

### **v3.9.1 — Documentation Sync & Cleanup** (Maintenance)

#### **Optimized**
* **Documentation Synchronization:**
    * Updated `README.md` and `README.ru.md` to fully reflect Product Development capabilities (Agents, Workflows, Artifacts).
    * Refactored `00_agent_development.md` description to "Meta-System Prompt".
* **Standards Enforcement (O6a):**
    * Updated `System/Docs/SKILLS.md` and `SKILL_TIERS.md` to strictly enforce "Script-First" and "Example Separation" patterns.
    * Removed legacy references to `Backlog/agentic_development_optimisations.md`.
* **Cleanup:**
    * Archived `Backlog/agentic_development_optimisations.md` as all optimization milestones (O1-O7) are complete and documented in System Docs.

---

### **v3.9.0 — Product Discovery & Handoff** (Feature)

#### **Added**
* **Completed Product Phase:** Full "Venture Builder" pipeline with 5 new agents (`p00`-`p04`).
    * **Strategy:** `skill-product-strategic-analysis` (TAM/SAM/SOM).
    * **Vision:** `skill-product-analysis` (Crossing the Chasm).
    * **Solution:** `skill-product-solution-blueprint` (ROI, Risk, Text-UX).
* **Quality Gate (VDD):**
    * **Adversarial Director (`p03`):** Blocks handoff if "Moat" is weak.
    * **Cryptographic Handoff:** `sign_off.py` -> `verify_gate.py` chain ensures only approved backlogs reach developers.
* **Workflows:**
    * `/product-full-discovery`: End-to-end Venture Building.
    * `/product-quick-vision`: For internal tools.
    * `/product-market-only`: For rapid idea validation.
* **Documentation:**
    * `System/Docs/PRODUCT_DEVELOPMENT.md`: Comprehensive playbook.
    * `System/Docs/WORKFLOWS.md`: Updated with Product workflows.

---

### **v3.8.0 — Phase 0: Product Bootstrap** (Feature)

#### **Added**
* **Product Management Module:**
    * **New Skills:** `skill-product-analysis` (Vision) and `skill-product-backlog-prioritization` (WSJF).
    * **New Agents:** `p01_product_analyst` (Creator) and `p02_product_reviewer` (VDD Critic).
    * **New Documentation:** [`System/Docs/PRODUCT_DEVELOPMENT.md`](System/Docs/PRODUCT_DEVELOPMENT.md) with usage scenarios.
* **Native Tool Integration:**
    * **Product Tools:** `init_product` and `calculate_wsjf` registered in `schemas.py`.
    * **Tool Runner:** Updated `System/scripts/tool_runner.py` to dispatch these tools via native subprocess calls.
    * **Scripts Root:** Moved scripts from `scripts/` to `System/scripts/` to align with framework standards.

#### **Changed**
* **Documentation:**
    * Updated `ORCHESTRATOR.md` with new supported tools.
    * Updated `SKILLS.md` with Product Management section.
    * Updated `SKILL_TIERS.md` with new Tier 2 skills.

---

### **v3.7.2 — O7: Session Context Persistence** (Optimization)

#### **Added**
* **New Skill: `skill-session-state`**: TIER 0 capability to persist/restore session context.
    * **Script-First**: `update_state.py` handles atomic YAML updates.
    * **Protocol**: Defines Boot (Read) and Boundary (Write) triggers.
* **Boot Protocol**: Updated `GEMINI.md` and `AGENTS.md` to restore state from `.agent/sessions/latest.yaml` on session start.
* **Agent Updates**: All 10 Agent Prompts updated to include `skill-session-state` in TIER 0 list.


### **v3.7.1 — Light Mode** (Feature)

#### **Added**
* **Light Mode:** New fast-track workflow for trivial tasks (typos, UI tweaks, simple bugfixes).
    * Skips Architecture and Planning phases (~50% token savings).
    * Workflows: `light-01-start-feature.md`, `light-02-develop-task.md`.
    * Skill: `light-mode` (Tier 2) with escalation protocol and security sanity checks.
    * Updated `GEMINI.md`, `AGENTS.md`, `WORKFLOWS.md`, `SKILLS.md`.

---

### **v3.7.0 — Skills Refactoring & Security Hardening** (Optimization)

#### **Added**
* **Security Automation:** Added `run_audit.py` to `security-audit` skill. Auto-detects project type (Solidity/Rust/Python/JS) and runs relevant tools (`slither`, `bandit`, `cargo audit`).
* **High-Grade Checklists:**
    * `solidity_security.md`: DeFi patterns, Flash Loans, Upgradability.
    * `solana_security.md`: Anchor validation, PDAs, Arithmetic.
* **Architecture Patterns:** Added `clean_architecture.md` and `event_driven.md` to `architecture-design` resources.
* **LLM Security:** Added Prompt Injection, Jailbreaking, and System Prompt Leakage checks to `skill-adversarial-security`.

#### **Optimized**
* **Skills Refactoring (O6):**
    * **Example Separation:** Extracted inline templates from `requirements-analysis`, `testing-best-practices` to `resources/`.
    * **Script-First:** Replaced manual instructions with script mandates.
    * **Sarcastic Persona:** Extracted prompt examples to `resources/prompts/sarcastic.md`.
* **Documentation:** Updated `System/Docs/SKILLS.md` to mandate V2 standards (Script-First, Example-Separation).

#### **Verified**
* **Global Validation:** All 6 refactored skills passed `validate_skill.py`.
* **Safety:** TIER 0 skills (`core-principles`) verified intact.

---

### **v3.6.5 — Configuration Standardization** (Refactoring)

#### **Changed**
* **Project Structure:**
    * Moved `.gemini/GEMINI.md` to `./GEMINI.md` (Project Root).
    * Renamed `.cursorrules` to `AGENTS.md` (Project Root) for clarity.
* **Documentation:** Updated `README.md`, `README.ru.md` and `docs/ARCHITECTURE.md` to reflect the new configuration structure.

---

### **v3.6.4 — O7 Prep & System Manifesto** (Documentation)

#### **Optimized**
* **System Manifesto (O11):** Rewritten `System/Agents/00_agent_development.md` to be the single source of truth for v3.6+ architecture.
    * Aligned with O1 (Skill Tiers) and O2 (Orchestrator Patterns).
    * Added section on **Agentic Mode** and `task_boundary` usage.
    * Included `10. Security Auditor` role.
* **O7 Specification:** Refined Session Context Management optimization.
    * Added alignment with `task_boundary` tool.
    * Added "Start Prompt" for O7 implementation.
* **README:** Updated Installation section to explicitly mention `.gemini/` folder copy.

---

### **v3.6.3 — O6a: Skill Structure Optimization** (Optimization)

#### **Changed**
* **Large Skills Refactoring:** Transformed 4 "heavy" skills (>4KB) to use `scripts/` + `examples/` pattern:
    * `architecture-format-extended`: Extracted inline templates to `examples/` (-65% size).
    * `skill-reverse-engineering`: Replaced NL traversal valid with `scan_structure.py` (-64% size).
    * `skill-update-memory`: Replaced NL git logic with `suggest_updates.py` (-63% size).
    * `skill-phase-context`: Removed redundant ASCII art layers (-49% size).

#### **Added**
* **Automation Scripts**: Added python automation for deterministic skill execution.
* **Infographic Update**: Added *Model Impact Analysis* and *References* to [O6_OPTIMIZATION_INFOGRAPHIC.md](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md).

### **v3.6.2 — Skill Creator & Automation** (Feature)

#### **Added**
* **New Skill: `skill-creator`**: Meta-skill for creating new skills containing Anthropic standards + Project Tiers (verified structure).
    *   **Automation:** Includes `scripts/init_skill.py` for compliant scaffolding.
    *   **Validation:** Includes `scripts/validate_skill.py` for ensuring frontmatter and strict folder hygiene.

---

---

### **v3.6.1 — O6: Logic Integrity & Documentation Polish** (Post-Release Fix)

#### **Fixed**
* **Orchestrator Logic Integrity:** Restored missing stages 11-14 (Review/Fix cycle) and Workflows section in `01_orchestrator.md` to guarantee 100% logic parity with v3.2.
* **Documentation:** Consolidated `CHANGELOG.md` entry for v3.6.0 logic clarity.

#### **Updated**
* **Infographics:** Updated [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) and [O6 Optimization Infographic](archives/Infographics/O6_OPTIMIZATION_INFOGRAPHIC.md) with final v3.6.1 verification stats (-20% Orchestrator compression vs -36% initial estimate).

---

### **v3.6.0 — O5: Skill Tiers & O6: Standardization (Optimization)** (Stability)

#### **Added**
* **O6 Standard:** All 10 Agent Prompts (`01`–`10`) now use a unified 4-section schema with mandatory TIER 0 skills validation.
    * **New Names:** Standardized filenames to `_prompt.md`.
* **O5 Skill Tiers:** New document `System/Docs/SKILL_TIERS.md` — authoritative source for loading rules (TIER 0, 1, 2).

#### **Changed**
* **Skills Metadata:** All 28 skills now explicitly declare `tier: [0|1|2]`.
* **Agent Efficiency (O6):**
    * `04 Architect`: **-29%** tokens.
    * `06 Planner`: **-33%** tokens.
    * `08 Developer`: **-31%** tokens.
    * `01 Orchestrator`: **-20%** tokens (adjusted for guaranteed logic retention).
* **Safety (O6):**
    * Reviewers (`07`, `09`) and Auditor (`10`) now strictly enforce TIER 0 safety skills (+43% size for zero hallucinations).

#### **Verified**
* **VDD Audit:** All 10 standardized agents passed Logic Retention checks against v3.2 backups.
* **Localization:** All Russian prompts synchronized.

---


### **v3.5.5 — O2: Orchestrator Compression (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-orchestrator-patterns`**: Stage Cycle pattern and dispatch table for Orchestrator.
    * Reusable Init → Review → Revision flow pattern.
    * Stage Dispatch Table with agents, reviewers, and iteration limits.
    * Decision logic tables for common branching.
    * Expected result schemas for all agent types.
    * Exception documentation (Completion, Blocking).

#### **Changed**
* **`01_orchestrator.md`**: Compressed from 492 lines to 170 lines using patterns + dispatch table.
* **`Translations/RU/Agents/01_orchestrator.md`**: Updated with same compression logic.
* **`System/Docs/SKILLS.md`**: Added `skill-orchestrator-patterns` entry.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| File size | 11,195 bytes | 4,522 bytes | **-60%** |
| Lines | 492 | 170 | **-65%** |
| Tokens (~) | ~2,799 | ~1,130 | **-60%** |

> **Note:** All 14 scenarios preserved. Backup at `01_orchestrator_full.md.bak`.
>
> 📊 **See:** [Token Optimization Infographic](archives/Infographics/TOKEN_OPTIMIZATION_INFOGRAPHIC.md) for a visual breakdown of savings.

---

### **v3.5.4 — O1: Skill Phase Context (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `skill-phase-context`**: Skill loading tiers protocol for optimized token consumption.
    * **TIER 0** (Always Load): `core-principles`, `skill-safe-commands`, `artifact-management` (~2,082 tokens).
    * **TIER 1** (Phase-Triggered): Phase→Skills mapping table for on-demand loading.
    * **TIER 2** (Extended): Specialized skills loaded only when explicitly requested.
    * Loading rules and flow diagram for agent reference.

#### **Changed**
* **`.gemini/GEMINI.md`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`.cursorrules`**: Added explicit TIER 0 Skills section with bootstrap loading instructions.
* **`System/Docs/SKILLS.md`**: Added `skill-phase-context` entry in Core & Process section.

#### **Optimization Impact**
| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Baseline session load | ~9,772 tokens | ~2,082 tokens | **-79%** |
| TIER 1 skills | All loaded upfront | On-demand per phase | -3,000 to -5,000 tokens |

> **Note:** Automation (safe-commands) preserved — `mv`, `git`, tests still auto-run.

---

### **v3.5.3 — O3: architecture-format Split (Optimization)** (Token Savings)

#### **Added**
* **New Skill: `architecture-format-core`**: Minimal template for architecture documents (~150 lines, TIER 1).
    * Core sections: Task Description, Functional Architecture, System Architecture, Data Model (conceptual), Open Questions.
    * Default skill for most architecture updates.
    * Loading conditions table for decision-making.
* **New Skill: `architecture-format-extended`**: Full templates with examples (~400 lines, TIER 2).
    * Complete sections 3-10 with JSON samples, diagrams, and detailed templates.
    * Loaded only for: new systems, major refactors, complex requirements.
    * Cross-reference to core skill.

#### **Changed**
* **`04_architect_prompt.md`**: Updated with conditional loading table for core/extended skills.
* **`Translations/RU/Agents/04_architect_prompt.md`**: Updated with same conditional loading logic.
* **`System/Docs/SKILLS.md`**: Replaced single `architecture-format` entry with two tier-based entries.

#### **Token Savings**
| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Minor architecture update | ~2,535 | ~996 | **-60%** |
| New system / major refactor | ~2,535 | ~3,357 | +32% (more examples) |

---

### **v3.5.2 — Scripts Consolidation & Installation Simplification** (Refactoring)

#### **Changed**
* **Moved `scripts/` → `System/scripts/`**: Tool Dispatcher is now part of System folder.
    * **Installation simplified**: Only 2 folders to copy (`System/` + `.agent/`) instead of 3.
    * **Clear separation**: Framework files (`System/`) vs project files.

#### **Updated**
* **README.md / README.ru.md**: Simplified installation instructions and directory structure diagrams.
* **System/Docs/ORCHESTRATOR.md**: All import paths updated to `System.scripts.tool_runner`.
* **tests/test_tool_runner.py**: Updated import path.

---

### **v3.5.1 — Protocol Conflict Resolution & IDE-Agnostic Fixes** (Framework Bugfix)

#### **Fixed**
* **`skill-archive-task`**: Removed strict dependency on `generate_task_archive_filename` tool. Added manual fallback for filename generation using shell commands.
* **`skill-archive-task`**: Replaced hardcoded example IDs (`032`, `033`) with generic placeholders (`{OLD_ID}`, `{NEW_ID}`) to prevent agent confusion.
* **`artifact-management`**: Removed hardcoded absolute path in skill reference. Fixed outdated tool reference.
* **`artifact-management`**: Added "Dual State Tracking" section to resolve conflict between Agentic Mode internal `task.md` and project `docs/TASK.md`.
* **`core-principles`**: Added IDE-agnostic "Bootstrap Protocol" (Section 0) instructing agents that `<user_rules>` injected by IDE **override** internal defaults.

#### **Root Causes Addressed**
| Issue | Solution |
|-------|----------|
| Context Blindness | Bootstrap Protocol now clarifies priority |
| Internal vs Project `task.md` | Dual State Tracking section added |
| Missing Tool Blocker | Manual fallback in skill-archive-task |
| Hardcoded Examples | Replaced with `{PLACEHOLDER}` syntax |

---

### **v3.5.0 — Memory Automation** (Task 035)


#### **Added**
* **New Skill: `skill-update-memory`**: Auto-update `.AGENTS.md` files based on code changes.
    * Analyzes `git diff --staged` to detect new, modified, and deleted files.
    * Strict filtering: ignores `*.lock`, `dist/`, `migrations/`, config files.
    * Human knowledge preservation: protects `[Human Knowledge]` sections.
    * Integration points: `09_agent_code_reviewer`, `04-update-docs`.
* **New Skill: `skill-reverse-engineering`**: Regenerate architecture documentation from codebase analysis.
    * Iterative strategy: folder-by-folder analysis → local summaries → global synthesis.
    * Updates `ARCHITECTURE.md` and discovers hidden knowledge for `KNOWN_ISSUES.md`.
    * Context overflow mitigation: never loads entire codebase at once.

#### **Documentation**
* Updated `System/Docs/SKILLS.md` with new skills in Core & Process section.
* Updated roadmap in `Backlog/potential_improvements-2.md`.

#### **Integration**
* `09_agent_code_reviewer.md`: Added `skill-update-memory` to verify `.AGENTS.md` updates.
* `04-update-docs.md` workflow: Added references to both skills for structured docs maintenance.
* `README.md` / `README.ru.md`: Updated "Reverse Engineering" section with skill-based prompts.

---

### **v3.4.2 — Framework Documentation Consistency Fixes** (Task 034 Phase 3)

#### **Fixed**
* **Broken References**: Identified and fixed stale references to moved files (`System/Docs/` vs `docs/`) in `README.md`, `.cursorrules`, and agent prompts.
* **Path Error**: Fixed incorrect path in `Translations/RU/Agents/01_orchestrator.md` (`docs/ORCHESTRATOR.md`) to align with user project structure.
* **Typos**: Corrected formatting errors in Russian Orchestrator prompt.

#### **Improved**
* **Installation Instructions**: Clarified `README.md` and `README.ru.md` to explicitly instruct users to copy `System/Docs/ORCHESTRATOR.md` to their local `docs/` folder, preventing path conflicts for distributed agents.

---

### **v3.4.1 — Workflow Integrity & Artifact Fixes** (Task 034 Phase 2)

#### **Fixed**
* **Workflow "Phantom" References**: Fixed critical bugs in `base-stub-first.md` (and consequently `vdd-enhanced`) which referenced non-existent workflows (`/analyst-task`, etc.) instead of valid ones. This restored the mandatory Analysis/Architecture phases.
* **VDD Adversarial Loop**: Corrected `vdd-adversarial.md` to use valid workflow calls (`/03-develop-single-task`) instead of non-existent actions (`/developer-fix`).
* **Artifact Consistency**: Created missing `docs/KNOWN_ISSUES.md` placeholder to satisfy workflow requirements.
* **Security Audit**: Clarified `security-audit.md` instructions regarding `.AGENTS.md` updates to handle missing files gracefully.

#### **Verified**
* Performed a full audit of all 14 workflow definitions to ensure every cross-reference points to an existing file.

### **v3.4.0 — VDD Multi-Adversarial** (Task 034)

#### **Added**
* **New Skill: `skill-adversarial-security`**: OWASP security critic in adversarial/sarcastic style.
    * Injection attacks (SQLi, XSS, Command Injection, Path Traversal).
    * Authentication & Authorization flaws.
    * Secrets exposure (hardcoded keys, passwords, API tokens).
    * Input validation failures.
* **New Skill: `skill-adversarial-performance`**: Performance critic in adversarial/sarcastic style.
    * N+1 queries, missing indexes.
    * Memory leaks, unbounded allocations.
    * Blocking operations in async code.
    * Algorithm complexity issues.
* **New Workflow: `/vdd-multi`**: Sequential execution of multiple specialized adversarial critics.
    * Phase 1: General logic review (`skill-vdd-adversarial`).
    * Phase 2: Security review (`skill-adversarial-security`).
    * Phase 3: Performance review (`skill-adversarial-performance`).

#### **Documentation**
* Updated `docs/SKILLS.md` with new VDD skills.
* Updated `Backlog/potential_improvements-2.md` with v3.4 status.

---

### **v3.3.2 — Auto-Tests for Archiving Protocol** (Task 033 Phase 2)

#### **Added**
* **Archive Protocol Tests**: 15 new automated tests for the 8 archiving scenarios using VDD adversarial approach:
    * Core scenarios: new task with existing TASK.md, no TASK.md, refinement, ID conflict.
    * VDD adversarial: missing Meta Information, malformed Task ID, permission denied, tool error simulation.
* **Testable Protocol Module**: `archive_protocol.py` — Python implementation of the 6-step archiving protocol for unit testing.
* **Test Fixtures**: 3 TASK.md variants (`task_with_meta.md`, `task_without_meta.md`, `task_malformed_id.md`).

#### **Verification**
* 44 total tests pass (29 existing + 15 new).
* Run: `cd .agent/tools && python -m pytest test_archive_protocol.py -v`

---

### **v3.3.1 — Portability, VDD Audit & UX Improvements** (Task 033)

#### **Fixed**
* **Circular Logic in Safe Commands**: Eliminated the documentation loop. Added explicit copy-paste list to `skill-safe-commands` for IDE configuration.
* **Agent Hallucinations**: Corrected `01_orchestrator.md` references to non-existent tools (`git_ops` -> `git_status`, etc.) revealed by VDD Audit.
* **IDE Configuration**: Fixed documentation for "Allow List" to address `mv` command token matching issues.
* **Portability**: Made `docs/ORCHESTRATOR.md` reference optional (`if available`) to prevent errors in lightweight projects or when transferring agents.

#### **Refactored**
* **Mandatory Skill Pattern**: Enforced `skill-safe-commands (Mandatory)` across all agents to ensure native tool safety.
* **Developer Guidelines**: Introduced explicit "Tooling Protocol" enforcing `native tools` (like `run_tests`) over shell commands.

### **v3.3.0 — Skill Encapsulation & Safe Commands Centralization** (Task 033)

#### **Added**
* **New Skill: `skill-archive-task`**: Complete, self-contained protocol for archiving `docs/TASK.md`. Single source of truth for archiving logic, eliminating duplication across 7+ files.
    * 6-step archiving protocol with decision logic (new vs refinement).
    * Error handling for missing Meta Information.
    * Validation and rollback guidance.
* **New Skill: `skill-safe-commands`**: Centralized list of commands safe for auto-execution without user approval.
    * 7 command categories: read-only, file info, git read, archiving, directory ops, tool calls, testing.
    * Pattern matching rules for IDE integration.
    * IDE-specific instructions (Antigravity/Gemini, Cursor).

#### **Refactored**
* **Duplication Eliminated**: Reduced archiving protocol duplication from 7 files to 1:
    * `.gemini/GEMINI.md` → skill reference
    * `.cursorrules` → skill reference
    * `System/Agents/02_analyst_prompt.md` → skill reference
    * `System/Agents/01_orchestrator.md` → skill reference
    * `System/Agents/00_agent_development.md` → skill reference (30 lines → 14)
    * `.agent/skills/artifact-management/SKILL.md` → skill import
    * `.agent/workflows/01-start-feature.md` → skill reference
* **Safe Commands Centralized**: All 4 files with duplicate Safe Commands now reference `skill-safe-commands`.

#### **Documentation**
* Updated `docs/SKILLS.md` with new skills.
* Added Implementation Summary to `docs/TASK.md` (Task 033).

---

### **v3.2.5, v3.2.6 — Task Archive ID Tool & Auto-Run Protocol**

#### **Added**
* **New Tool: `generate_task_archive_filename`**: Deterministic tool for generating unique sequential IDs when archiving tasks. Eliminates manual ID assignment errors and ID gaps.
    * Auto-generates next available ID (`max + 1` strategy).
    * Validates proposed IDs and handles conflicts (`allow_correction` flag).
    * Normalizes slugs (lowercase, dashes).
    * Future-proofed: supports IDs beyond 999 (regex `\d{3,}`).
* **Dispatcher Integration**: Tool registered in `scripts/tool_runner.py` for native execution.
* **Unit Tests**: 29 comprehensive tests covering all use cases.

#### **Improved**
* **Safe Commands Protocol**: Expanded list of auto-run commands in `skill-artifact-management` and Orchestrator prompt:
    * Read-only: `ls`, `cat`, `head`, `tail`, `find`, `grep`, `tree`, `wc`
    * Git read: `git status`, `git log`, `git diff`, `git show`, `git branch`
    * Archiving: `mv docs/TASK.md docs/tasks/...`
    * Tools: `generate_task_archive_filename`, `list_directory`, `read_file`
* **Agent Prompts**: Updated Orchestrator (`01`) and Analyst (`02`) with explicit tool usage for archiving.

#### **Documentation**
* Updated `docs/ARCHITECTURE.md`, `docs/ORCHESTRATOR.md`, and `docs/SKILLS.md`.
* Added Python installation requirements to README.
* Consolidated `docs/USER_TOOLS_GUIDE.md` into `docs/ORCHESTRATOR.md` (removed duplicate file).
* Synchronized `.gemini/GEMINI.md` and `.cursorrules` with v3.2.5+ protocol.

---

### **v3.2.4 — Workflow Documentation Enhancement**

#### **Added**
* **Workflow Call Sequences**: Added comprehensive "Getting Started" section to `docs/WORKFLOWS.md` with:
    * One-Step vs Multi-Step approach comparison table.
    * TDD pipeline examples (`base-stub-first`, `01`→`02`→`03/05`→`04`) with pros/cons.
    * VDD pipeline examples (`vdd-enhanced`, `full-robust`, VDD atomic steps) with pros/cons.
    * Decision flowchart (Mermaid diagram) for choosing the right approach.
    * Quick reference summary table for common scenarios.

---

### **v3.2.3 — Archiving Protocol Refinement**

#### **Changed**
* **Archiving Scope**: Removed mandatory archiving of `docs/PLAN.md`. Only `docs/TASK.md` requires archiving before new tasks.
* **Documentation**: Updated version references in `README.md` (v3.1→v3.2) and `docs/ORCHESTRATOR.md` (v3.1.2→v3.2.2).

#### **Improved**
* **Auto-Run Protocol**: Added explicit `SAFE TO AUTO-RUN` instruction to Analyst prompt and `skill-artifact-management`. The archive command for `docs/TASK.md` no longer requires user approval.

---

### **v3.2.2 — System Integrity & Archiving Protocols**

#### **Fixed**
* **Critical Restoration**: Restored missing (empty) Russian agent prompts (`Translations/RU/Agents/01, 02, 04, 06`) using v3.2.0 logic.
* **Data Loss Prevention**: Fixed a critical gap in `skill-artifact-management` where the "Archiving Protocol" was missing.
* **Protocol Enforcement**: Updated Orchestrator (`01`), Analyst (`02`), and Planner (`06`) to strictly enforce archiving of `docs/TASK.md` and `docs/PLAN.md` before overwriting.

#### **Improved**
* **System Prompts**: Synchronized `.gemini/GEMINI.md` and `.cursorrules` with the Tool Execution Protocol (v3.2.0), explicitly enabling native tool calling.
* **Consistency**: Completed a full audit of the prompt system to ensure zero contradictions between System and Agent prompts.

---

### **v3.2.1 — Skills System Optimization**

#### **Added**
* **Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
* **Rules**: Added `.agent/rules/localization-sync.md` to enforce bilingual documentation updates.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Localization**: Synced `README.ru.md` with English version (added Tool Calling section).
* **Russian Agents**: Updated `Translations/RU/Agents/*.md` to match v3.2.0 optimizations (Tool Calling logic, Skills extraction, Path Hygiene).

---

### **v3.2.0 — Structured Tool Calling & Path Hygiene**

#### **Added**
* **Tool Execution Subsystem**: The Orchestrator now natively supports structured tool calling (Function Calling).
* **New Skills**:
    * `skill-task-model`: Standardized examples and rules for `docs/TASK.md`.
    * `skill-planning-format`: Standardized templates for `docs/PLAN.md` and Task Descriptions.
    * `skill-architecture-format`: Consolidated architecture document templates.
* **Standard Tools**: Added `run_tests`, `git_ops`, `file_ops` to `.agent/tools/schemas.py`.
* **Documentation**: Added `docs/ORCHESTRATOR.md`.

#### **Improved**
* **Prompt Engineering**: Significantly reduced the size of Analyst (`02`), Architect (`04`), and Planner (`06`) agents by extracting static templates into the Skills System.
* **Maintenance**: Centralized critical document templates (TASK, PLAN, Architecture) in `.agent/skills/` to ensure consistency and easier updates.
* **Workflows**: Refactored `03-develop-task` -> `03-develop-single-task` and updated `base-stub-first`.

#### **Changed**
* **Test Reports**: Standardized storage location. Reports moved from `docs/test_reports` to `tests/tests-{Task ID}/`.
* **Path Enforcement**: Updated all Agent prompts to use strictly project-relative path examples.
* **Agents**: Updated Orchestrator, Developer, and Reviewers to enforce new protocols.

#### **Fixed**
* **Cleanup**: Removed legacy `docs/test_reports` directory.

---

### **v3.1.3 — Skills Cleanup & Cursor Integration Fix**

#### **Changed**
* **Project Structure**: Removed redundant `.cursor/skills` directory to eliminate duplication.
* **Cursor Integration**: Updated `README.md` to instruct users to simply symlink `.cursor/skills` -> `.agent/skills`, ensuring a single source of truth.
* **Orchestrator**: Updated `.cursorrules` to reference the correct symlinked path and fixed legacy "tz" terminology in comments.
* **Workflows**: Archived `docs/TASK.md` to `docs/tasks/task-014-cleanup-skills.md`.

---

### **v3.1.2 — Analyst Protocol & YAML Fixes**

#### **Fixed**
* **Skills**: Fixed YAML syntax error in `core-principles` skill (quoted description).

#### **Improved**
* **Analyst Agent**: Added "CRITICAL PRE-FLIGHT CHECKLIST" to `02_analyst_prompt.md` to strictly enforce:
    * Archiving of existing `docs/TASK.md` before starting new work.
    * Mandatory inclusion of Section 0 (Meta Information: Task ID, Slug).
* **Skills**: Updated `skill-requirements-analysis` to mark Meta Information as **MANDATORY**.
* **Documentation**: Enforced "Relative Paths Only" rule for Artifacts in `skill-documentation-standards` and `06_agent_planner.md`.

#### **Refactored**
* **Skills**: Audited and fixed YAML frontmatter in `code-review-checklist`, `developer-guidelines`, `security-audit` and `artifact-management`.
* **PLAN.md**: Converted absolute paths to relative paths.

---

### **v3.1.1 — Plan & Structure Fixes**

#### **Fixed**
* **Agent Prompts**: Corrected `plan.md` file path references to `docs/PLAN.md` in Planner and Reviewer agents (both English and Russian versions).
* **Agent Prompts**: Corrected `open_questions.md` file path references to `docs/open_questions.md` in Planner agent.
* **Project Structure**: Removed the `verification/` directory to comply with `docs/ARCHITECTURE.md`.

---

### **v3.1.0 — Global "TZ" to "TASK" Refactor**

#### **Changed**
* **Terminology**: Global refactoring of "TZ" (Техническое Задание) to "TASK" (Task/Specification) to improve internationalization and consistency.
* **Артефакты**: Переименован `docs/TZ.md` в `docs/TASK.md`.
* **Системные Агенты**: Обновлены все промпты агентов (Analyst, Reviewer, Architect и др.) для использования терминологии "TASK".
* **Навыки**: Переименован `skill-tz-review-checklist` в `skill-task-review-checklist`.
* **Документация**: Обновлены `README.ru.md`, `WORKFLOWS.md`, `SKILLS.md` и `.gemini/GEMINI.md` для соответствия новому стандарту.

#### **Исправлено**
* **Согласованность**: Устранено смешанное использование "ТЗ" и "Task Specification" во всем фреймворке.
* **Сценарии (Workflows)**: Исправлена критическая ошибка в `01-start-feature` и `vdd-01-start-feature`, из-за которой старое ТЗ перезаписывалось без архивации. Добавлен явный шаг архивирования.

#### **Инструкция по миграции**
Для обновления с v3.0.x до v3.1.0:
1. **Переименование**: `mv docs/TZ.md docs/TASK.md`
2. **Обновление Агентов**: Замените `System/Agents/` на новую версию (Важно: `03_tz_reviewer_prompt.md` -> `03_task_reviewer_prompt.md`).
3. **Обновление Навыков**: Замените `.agent/skills/` на новую версию.

---

### **v3.0.3 — Синхронизация документации и артефакты**

#### **Исправлено**
* **Документация**: Заменены устаревшие ссылки на `UNKNOWN.md` на `docs/open_questions.md` в `README.md` и `README.ru.md` для соответствия реальным промптам Агентов.

#### **Добавлено**
* **Артефакты**: Добавлен отсутствующий шаблон `docs/open_questions.md` для отслеживания нерешенных вопросов.

---

### **v3.0.2 — Примеры и Доработка Документации**
  
#### **Добавлено**
* **Примеры (Examples)**:
    * `examples/skill-testing/test_skill.py`: Python скрипт для изолированного тестирования навыков.
    * `examples/skill-testing/n8n_skill_eval_workflow.json`: n8n workflow с подсказками (Sticky Notes) для проверки промптов.
* **Документация (Skills)**:
    * В `docs/SKILLS.md` добавлены разделы "Dynamc Loading", "Isolated Testing" и "Best Practices".
    * Добавлены прямые ссылки на файлы примеров.

---

### **v3.0.1 — Улучшение Системы Навыков**

#### **Улучшено**
* **Документация Навыков**:
    * Расширен `docs/SKILLS.md`: добавлено "Как это работает", принципы и ссылки на официальную документацию.
    * Добавлены матрицы "Используется в сценариях" и "Используется агентами".
    * Уточнено понятие **Adversarial Agent** как "Virtual Persona" (Виртуальная Персона) в режиме VDD.
* **README**:
    * Восстановлены пропущенные разделы "Команда Агентов" и "Системный Промпт".
    * Исправлены инструкции по установке Системы Навыков.

---

### **v3.0.0 — Система Навыков и Глобальная Локализация**

#### **Ключевые изменения**
* **Система Навыков**: Внедрена модульная библиотека `.agent/skills/`. Агенты теперь динамически загружают "навыки" вместо использования монолитных промптов.
* **Архитектура Локализации**: Новая структура директории `Translations/`. Полная поддержка переключения между Английским и Русским контекстами.
* **Документация**:
    * Добавлен `docs/SKILLS.md`: Полный каталог доступных навыков.
    * Обновлены `README.md`, `README.ru.md`, `docs/ARCHITECTURE.md`.

#### **Удалено**
* **Legacy**: Удалена директория `/System/Agents_ru` (заменена на `Translations/RU`).

---

### **v2.1.3 — Документация и согласованность сценариев**

#### **Исправлено**
* **ARCHITECTURE.md**: Обновлен для соответствия реальной структуре проекта (добавлены папки `.agent` и `docs`).
* **Workflows**: `full-robust.md` теперь явно вызывает `/security-audit` (Агент 10) вместо заглушки.

### **v2.1.2 — Исправление генерации .AGENTS.md**

#### **Исправлено**
* **Конфликт промптов**: Устранен конфликт, из-за которого Developer пропускал создание `.AGENTS.md`, так как Planner не ставил это в задачу, а правило "без лишних файлов" запрещало самодеятельность.
* **Planner Agent**: Теперь явно требует создания `.AGENTS.md` для новых папок.
* **Developer Agent**: Получил явное разрешение (исключение) на создание `.AGENTS.md`, даже если этого нет в task-файле.

### **v2.1.1 — Верификация процессов и безопасность**

#### **Добавлено**
* **Обязательная верификация**: Все основные сценарии (Standard и VDD) теперь включают явные циклы проверки (Analyst -> TZ Review и т.д.).
* **Лимиты безопасности**: Внедрен механизм **Max 2 Retries** для предотвращения бесконечных циклов "Исполнитель-Ревьюер".

---

### **v2.1.0 — Вложенные сценарии (Nested Workflows) и аудит безопасности (Security Audit)**

#### **Добавлено**
* **Поддержка вложенных сценариев**: Возможность вызывать одни workflows из других (например, `Call /base-stub-first`).
* **Новые сценарии**:
  * `/base-stub-first`: Базовый пайплайн Stub-First.
  * `/vdd-adversarial`: Изолированный цикл адверсариальной проверки.
  * `/vdd-enhanced`: Комбинация Stub-First + VDD.
  * `/full-robust`: Полный пайплайн с будущим аудитом безопасности.
  * `/security-audit`: Standalone security vulnerability assessment workflow.
* **Документация**: Обновлены `WORKFLOWS.md`, `README.md` и `GEMINI.md`.

---

### **v2.0.0 — Public Release: Multi-Agent Software Development System**

#### **Key Highlights**

* **9-Agent Ecosystem**: A comprehensive orchestration of **9 specialized agents** (Analyst, Architect, Planner, Developer, Reviewer, Orchestrator, and others) covering the full SDLC.
* **VDD (Verification-Driven Development)**: Built-in adversarial testing with the **Sarcasmotron** agent to ensure logic consistency and high reliability.
* **Stub-First Methodology**: Strict TDD-inspired flow where architecture, E2E tests, and stubs are defined before a single line of production code is written.
* **Long-Term Memory**: Advanced artifact management using `.AGENTS.md` and structured logs to maintain context across long development sessions.
* **Native IDE Integration**: Seamless support for **Antigravity** (`.gemini/GEMINI.md`) and **Cursor** (`.cursorrules`).

#### **🚀 Quick Start**

1. **Copy agents**: Move the `/System/Agents` folder into your project root.
2. **Configure IDE**: Copy `.gemini/GEMINI.md` (for Antigravity) or `.cursorrules` (for Cursor) to your project root to enable agent instructions.
3. **Initialize**: Use the `02_analyst_prompt.md` prompt to start the session.
4. **Follow Guidelines**: Refer to the **Pre-flight Check** in the README for the full workflow.
