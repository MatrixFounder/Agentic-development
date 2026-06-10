# Verification Stack Modernization Roadmap

- **Source:** `docs/reviews/verification-stack-currency-audit-067.md` (Task 067, 2026-06-10) — claims register C-01…C-16, evidence, bibliography live there. This file is the **working backlog**; the audit report stays immutable.
- **Status legend:** ✅ DONE · 🔜 READY (no blockers) · ⏳ BLOCKED-BY (see Dependencies) · 🧪 EXPERIMENT
- **Item numbering** matches the audit's Modernization backlog (items 1–13) for traceability.

## How to execute any item (cold-session protocol)

1. Each item = its own `/framework-upgrade` cycle (these are framework-component edits → `skill-self-improvement-verificator` gates TASK and PLAN).
2. Global gates after edits, every time:
   - Skill quality gate: `python3 .agent/skills/skill-creator/scripts/validate_skill.py <skill-dir>` for every edited skill (baseline: 43/43 across `.agent/skills/*/`).
   - Wrapper-drift grep (KNOWN_ISSUES §Wave-1/2): `grep -rl '<old-path-or-old-wording>' .claude/agents/ .agent/` → must be empty.
   - Lockstep rule edits (065/066 discipline): when a rule exists in multiple synced locations, all copies change byte-identically in one commit.
3. Update `CHANGELOG.md` + bump skill `version:` in frontmatter of edited skills.
4. Session-state at phase boundaries: `python3 .agent/skills/skill-session-state/scripts/update_state.py ...`

---

## P0 — Harmful (✅ DONE)

### 1. ✅ [C-05] Remove tone-as-success-criterion termination
- **File:** `.agent/skills/skill-adversarial-security/SKILL.md` §7
- **Done in:** commit `a9c032a` (skill v1.1 → v1.2). §7 is now "Termination — Objective Convergence": automation executed (or honestly `scan: NOT RUN`) + no Critical/High + bikeshedding-only. Explicit: "The persona is the delivery style, never a success criterion."
- **Verified:** 2026-06-10, file read + `validate_skill.py` pass.

### 2. ✅ [C-15] Remove "Mock the results" fabrication instruction
- **File:** `.agent/skills/skill-adversarial-security/SKILL.md` §3, §5
- **Done in:** commit `a9c032a`. §3 now: if script can't run (critic-security has no Bash), report `scan: NOT RUN`, manual review only, **never fabricate scanner output**; orchestrator is responsible for running `run_audit.py` and passing results into the critic prompt. §5 step 1 synced.
- **Verified:** 2026-06-10.
- **Residual (tracked in item 11):** the orchestrator side of the contract — `vdd-multi.md` Phase 1 does not yet instruct the orchestrator to run `run_audit.py` and inject results into the critic-security prompt. Until item 11 lands, critic-security legitimately reports `scan: NOT RUN` on every `/vdd-multi` run.

---

## P1 — Outdated

### 3. ✅ [C-11, C-14] Agentic/MCP security upgrade — *highest real-world risk*
- **Done in:** Task 069 / v3.20.0 (2026-06-10), gate artifact `docs/reviews/framework-audit-069.md`. New `mcp_agentic_security.md` checklist (1:1 ASI01–ASI10 + NSA CSI + 7 named attack patterns + incident block); `--scan-type mcp` with 10 CWE+ASI-tagged patterns (incl. `.vscode` descent, whole-file matching, HIGH ceiling); `snyk-agent-scan`/`mcp-scan` in the external roster (no server auto-start); `10_security_auditor.md` v3.7.0 Step 1.5 Agentic Threat Model. ASI names / NSA controls / scanner CLI verified against primary sources in-session.
- **Verified:** pytest 29/29 (12 new); repo audit byte-identical to baseline + 0 MCP findings; skill gate 43/43.
**Why:** since the checklists were written, the bar moved: OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10, 2025-12-09), NSA CSI "MCP Security Design Considerations" (May 2026), CVE-2025-6514 (9.6) / CVE-2025-49596 (9.4) / MCP-STDIO 11-CVE cluster (Apr 2026), in-the-wild incidents (postmark-mcp rug pull, s1ngularity, Shai-Hulud), shipping scanners (Invariant mcp-scan → Snyk agent-scan). The framework's own domain is agentic development; current coverage is one-liners in `llm_security.md:35,70–75` with **zero** detection patterns.

**Work:**
1. New `.agent/skills/security-audit/references/checklists/mcp_agentic_security.md` (~80–100 lines), sections mapped 1:1 to ASI01–ASI10 + NSA CSI controls (sandboxing, output filtering, DLP, local MCP scans). Concrete attack patterns: tool poisoning (hidden instructions in tool descriptions), rug pull (post-approval definition mutation), tool shadowing, full-schema poisoning, confused deputy / token passthrough / session hijacking (per modelcontextprotocol.io Security Best Practices).
2. Regex patterns in `scripts/audit/patterns.py` (regex-detectable floor): `mcp.json` / `.cursor/mcp.json` / `claude_desktop_config.json` presence+provenance, auto-approve flags (`chat.tools.autoApprove`, `--dangerously-skip-permissions`-style), unpinned `npx -y` MCP servers, missing lockfile/hash pinning, imperative language in tool-description strings (heuristic).
3. External tool roster (`scripts/audit/external.py` + SKILL §2): add `mcp-scan` / Snyk `agent-scan` (trigger: MCP config artifacts detected).
4. `System/Agents/10_security_auditor.md`: add Agentic Threat Model subsection (can agent be goal-hijacked? tool calls tampered? memory/context poisoned? inter-agent messages trusted?) + reference the new checklist in TIER 1 loading.
5. Honest limitation note: semantic tool-description poisoning requires LLM review, not regex (ties into item 10).
- **Acceptance:** new checklist exists + referenced from SKILL §3; ≥8 new patterns with CWE/ASI mapping + tests; `run_audit.py` runs green on this repo; 10_security_auditor mentions ASI/MCP.

### 4. ✅ [C-09] Re-map OWASP Top 10 checklist to the real 2025 final
- **Done in:** Task 070 / v3.20.1 (2026-06-10), gate artifact `docs/reviews/framework-audit-070.md`. Checklist re-sectioned to the 2025 final (verified in-session against owasp.org/Top10/2025/ — which also caught the A09 paraphrase in this roadmap; official name: "Security Logging and **Alerting** Failures"): SSRF → A01 subsection, old-A06 + supply-chain items of old-A08 → new A03, new A10 Mishandling of Exceptional Conditions (CWE-209/390/754/636), 2021→2025 mapping table appended for stale compliance exports. `security-audit` SKILL 3.4→3.5 (§2 tags, §3 Top Checks ×4); 4 `scanners.py` docstrings re-tagged.
- **Assumption corrected:** `patterns.py` has **no** A-number category tags (findings carry `category` strings + CWE only) — the A-number tags lived in `scanners.py` docstrings.
- **Verified:** checkbox conservation 61→66 accounted; stale-ref grep clean; skill gate 43/43; pytest 30/30 + repo audit findings/counts unchanged vs pre-edit baseline — only output diff is the intentional v3.4→v3.5 summary header (zero behavior change). Adversarial pass: `docs/reviews/adversarial-review-070.md`.
**Why:** `references/checklists/owasp_top_10.md` was titled "2025" but used the **2021 taxonomy**. Actual 2025 final (Jan 2026): A03 = Software Supply Chain Failures (new), A05 = Injection, A10 = Mishandling of Exceptional Conditions (new), SSRF absorbed into A01, Security Misconfiguration #5→#2. Compliance mappings exported to Jira/Snyk were wrong.

### 5. ✅ [C-01, C-03, K2] Retire the politeness-filter rationale; reposition vdd-sarcastic
- **Done in:** Task 071 / v3.20.2 (2026-06-10), gate artifact `docs/reviews/framework-audit-071.md`. Rationale replaced with the exhaustive-reporting instruction in K1 (§2 principle now "Exhaustive Reporting (supersedes 'Forced Negativity')", §7 row) + methodology §V.2 (with retirement note); K2 repositioned as opt-in stylistic skin (§2 disclaimer "no evidence base; mechanism = exhaustive reporting + objective bar, not meanness"; §1/§3/§5 reworded; example gains Severity+Confidence columns + a low-confidence finding); `skill-adversarial-security` §2 MANDATORY persona → optional style (+§1 red flag now targets severity-threshold literalism per item 5.1 parenthetical), wrapper `critic-security.md` synced; `skill-adversarial-performance` "State the problem sarcastically" → optional framing. Versions: vdd-adversarial 1.2, vdd-sarcastic 1.2, skill-adversarial-security 1.3, skill-adversarial-performance 1.1. Deprecate-vs-keep for K2 still waits on item 13 (unchanged).
- **Verified:** 2026-06-10 — `grep -ri "politeness filter" .agent/ System/` empty (hardened bare-token grep over `.agent/ System/ .claude/` also empty; scope excludes `.agent/archive/` rollback copies + `.agent/sessions/` runtime state); mandate-token grep empty; "Forced Negativity" only in the 2 supersedes-notes; skill gate 43/43; pytest 30/30. Known out-of-repo drift: `Universal-skills/skills/vdd-{sarcastic,adversarial}` are independent stale copies (symlinked from `~/.claude/skills/`) — manual sync recommended.
**Why:** "Forced Negativity bypasses LLM politeness filters" is GPT-4-era theory: vendors now train sycophancy out (GPT-5 system card −70–75%; Opus 4.5/4.6 cards); harsh judge prompts inflate false positives (arXiv:2603.00539, 2604.16790); zero evidence for sarcasm; vendor-documented recall lever is *reporting-threshold instruction*, not tone.
**Work:**
1. Replace "bypass politeness filters" rationale in: `vdd-adversarial/SKILL.md:24` (Forced Negativity principle), `vdd-adversarial/references/vdd-methodology.md:44` (§V.2), `vdd-sarcastic/SKILL.md:40` (rationalization table). New wording: **exhaustive-reporting instruction** — "report every issue including low-confidence ones, attach confidence + severity, filter downstream" (matches Opus 4.7+ migration guidance; also audit critic prompts for severity-threshold literalism — see item 9).
2. `skill-adversarial-security/SKILL.md` §1 line 16 ("Sarcasm breaks complacency. Use it.") and §2 MANDATORY persona — soften to optional style note (left intact by P0 on purpose; it belongs here).
3. `vdd-sarcastic/SKILL.md`: add explicit disclaimer — "tone is a stylistic choice with no evidence base; the mechanism is exhaustive reporting + objective bar, not meanness" (or deprecate the skill outright after item 13's experiment).
4. Keep everything else in K1 untouched — its mechanics (objective bar, template, hallucination check) scored Current.
**Acceptance:** `grep -ri "politeness filter" .agent/ System/` → empty; sarcasm nowhere mandatory; disclaimers in place; examples updated.

---

### 6. 🔜 [C-07] Parallel-dispatch adapters for non-Claude vendors — *detailed*

**Why:** the sequential-fallback premise ("other vendors have no parallel primitives") is factually obsolete: **Gemini CLI** shipped native subagents (Google Developers Blog, Apr 2026), **OpenAI Codex CLI** shipped custom agents with parallel spawn (developers.openai.com/codex/subagents, Mar 2026), **Cursor** shipped subagents (2.4, ~Jan 2026) + background agents (up to 8 parallel). Current state: `references/gemini-cli.md` and `references/cursor.md` are stubs that redirect to `sequential-fallback.md`; **Codex CLI has no reference and is not even in the §1.1 detection table**.

**Files involved:**
- `.agent/skills/skill-parallel-orchestration/SKILL.md` (§1.1 detection table, §1.2 tie-break, §7 fallback caveat)
- `.agent/skills/skill-parallel-orchestration/references/{gemini-cli.md, cursor.md, codex-cli.md(new), sequential-fallback.md, _stub-template.md, claude-code.md(structure donor)}`
- `.agent/workflows/vdd-multi.md` (section "Fallback (Sequential) — non-Claude-Code vendors")
- Per-vendor critic wrapper sets (new; see 6e)

**Sub-tasks (one `/framework-upgrade` cycle each, or 6a–6c in one cycle + 6d–6e in a second):**

**6a — Gemini CLI adapter** (`references/gemini-cli.md`: stub → full reference, depth of `claude-code.md`)
- Map parent SKILL §2 concepts to Gemini primitives: teammate definition (custom subagent files: own tools/MCP servers/context — verify exact location/format against geminicli.com/docs/core/subagents/), spawn syntax (explicit delegation; concurrent subagents/instances), single-invocation multi-spawn equivalent (or document the closest atomic pattern), tool whitelisting, per-subagent model selection.
- Define the 3 critic teammates for Gemini as thin wrappers referencing the same SOT skills (`vdd-adversarial`, `skill-adversarial-security`, `skill-adversarial-performance`) — same convergence enum `clean-pass | issues-found | bikeshedding-only`.
- Runtime detection: marker `GEMINI.md` (already in §1.1) — unchanged.

**6b — Codex CLI adapter** (NEW `references/codex-cli.md` + detection-table entry)
- Codex custom agents: TOML files in `~/.codex/agents/` or `.codex/agents/` — fields `name`, `description`, `developer_instructions`, plus `model`/`effort`/`sandbox`/MCP/skills overrides. Parallel orchestration: Codex spawns specialized agents in parallel and consolidates results in one response.
- Runtime detection: add row to §1.1 — marker `.codex/` directory (note: `AGENTS.md` alone is NOT a Codex marker — it's cross-vendor; tie-break via §1.2).
- 3 critic agents as TOML wrappers referencing the SOT skills; `developer_instructions` = the wrapper body, pointing at `.agent/skills/...` paths.
- Mind v3.19.1's symlink-aware prompt-discovery work (commit `6caf8ad`) — Codex path resolution must survive symlinked framework dirs.

**6c — Cursor adapter** (`references/cursor.md`: stub → full reference)
- Cursor 2.4 subagents (independent context windows) + background agents (cloud, up to 8 parallel). ⚠️ Audit research verified this only via **secondary** sources — first implementation step is verifying against primary cursor.com docs; if subagents lack a programmatic spawn-N-and-merge pattern, document the closest achievable Layer A approximation and keep the honest gap note.
- Distinguish in-session subagents (interactive) vs background agents (async, closer to Layer B semantics — likely out of scope, mark deferred like Claude's Layer B).

**6d — Dispatch demotion (sequential → last resort)**
- `SKILL.md §1.1/§7`: detection table rows for Gemini/Codex/Cursor flip from "→ sequential-fallback" to "→ native adapter"; §7 caveat rewritten: sequential-fallback applies only to (i) primitive-less runtimes, (ii) deterministic single-session debugging, (iii) CI with one agent slot.
- `vdd-multi.md` "Fallback (Sequential)" section → "**Vendor dispatch**": resolve runtime per skill §1 → use native parallel adapter; sequential role-switching only as documented last resort. All flags (`--scope/--no-fix/--fail-on/--output/--diff-only`) honored on every path (already true for sequential; assert for adapters).

**6e — Wrapper governance (anti-drift)**
- Per-vendor critic wrappers multiply the Wave-1/2 wrapper/SOT-drift surface ×4. Mitigations: (i) extend the KNOWN_ISSUES drift-grep to all wrapper dirs (`.claude/agents/`, `.gemini/...`, `.codex/agents/`, cursor equivalent); (ii) preferably implement the **Wave-5 multi-vendor generator** sketched in skill history — one manifest (critic name, scope line, SOT path, enum) → generated wrappers per vendor, so hand-sync disappears. Generator script lives in `skill-parallel-orchestration/scripts/`, gated by `init_skill.py` rules NOT applying (it's a script, not a skill).

**Validation gate (applies to 6a/6b/6c separately):**
- An adapter graduates ⚠️ stub/Unvalidated → ✅ validated **only after one end-to-end `/vdd-multi --no-fix` run on the real runtime** (rule already embedded in the stubs). Until then the ⚠️ banner stays, reworded from "no primitive known" to "primitive documented, run not yet validated".
- These runs require machines with the actual CLIs installed (Gemini CLI / Codex CLI / Cursor) — **operator action, not in-repo work**. Record each validation run's date + version in the reference file header.

**Acceptance (whole item 6):** 3 references at claude-code.md depth; §1.1 table has 5 runtime rows incl. Codex; vdd-multi dispatch section rewritten; sequential-fallback demoted everywhere ("functionally equivalent" claim removed — C-07); drift-grep extended; gate 43/43.

---

### 7. ⏳(R3a/R3b/R3d ✅ · R3c pending) [C-08] Severity-escalation redesign — *detailed*

- **R3a/R3b/R3d done in:** Task 072 / v3.20.3 (2026-06-10), gate artifact `docs/reviews/framework-audit-072.md`. Merge rule 3 redesigned in lockstep across all 4 locations (byte-identical modulo the pre-existing critics↔teammates noun split, normalized-diff-verified): same-mechanism agreement → `corroborated` tag + severity = max, no +1 (R3a); different-failure-mechanism overlap at the same location keeps +1 with a documented mechanism-difference test (R3b); sequential fallback explicitly never escalates — tag only, `priority` flag at most for cross-mechanism (R3d). Do-not-touch list respected (rules 1/2/4/5, iteration caps). `skill-parallel-orchestration` 3.0→3.1.
- **Verified:** old-wording greps empty (scope excludes `.agent/archive/` + `.agent/sessions/`); `escalate severity by one level` survives only inside the new R3b bullets; skill gate 43/43; pytest 30/30 (security-audit; parallel-orchestration has no test suite — its SKILL §8 reference to `tests/test_mock_agent.py` is pre-existing drift, flagged not fixed).
- **Remaining:** R3c only (gradation table + per-critic model config + env-override warning) — tier-diverse form available now in Claude Code, cross-vendor form ⏳ BLOCKED BY item 6. Item 11 still pairs naturally with the R3c/vdd-multi edit.

**Why:** the rule "two critics independently flagging the same location → escalate severity by one level" assumes critic independence. All critics are the same base model with different personas; Correlated Errors (ICML 2025, arXiv:2506.07962): same-model pairs pick the *same wrong answer* ~60% of the time when erring; persona-differentiated same-model ensembles share priors and failure modes (arXiv:2601.12307). Same-model agreement therefore **double-counts one model's prior** — it is corroboration (survived prompt variation), not confirmation.

**The rule lives in 4 synced locations (lockstep edit, byte-identical where shared):**
1. `.agent/workflows/vdd-multi.md` — Phase 2, merge rule 3 (line ~106)
2. `.agent/skills/skill-parallel-orchestration/SKILL.md` — §6 rule 3
3. `.agent/skills/skill-parallel-orchestration/references/sequential-fallback.md` — merge step (rule 3)
4. `.agent/skills/skill-parallel-orchestration/examples/usage_example.md` — merge walkthrough

**New rule design:**

**R3a — Same-model agreement: no auto-escalation.** Replace "+1 severity" with a `corroborated` tag on the merged finding: *"flagged by N critics — finding survived persona/prompt variation (weak positive signal; NOT independent confirmation)"*. Severity = max of the duplicates (dedup rule 1 unchanged). The "Overlaps" report section stays, listing corroborated findings.

**R3b — Cross-category, different-mechanism exception (escalation survives here).** If two critics flag the same location with **different failure mechanisms** (e.g., critic-logic: unhandled edge case; critic-security: exploitable injection at the same line), that is two distinct analyses, not duplicate detection → escalation by one level remains legitimate (or at minimum a `priority` flag). Mechanism-difference test: the exploit/failure scenarios are not paraphrases of each other — orchestrator judgment, documented in the merged report.

**R3c — Re-earning full escalation via model heterogeneity (⏳ depends on item 6 for the cross-vendor form).** Add optional per-critic model config to `/vdd-multi` (e.g., `--models=logic:opus,security:fable,performance:sonnet` or a config block in the workflow). Signal-strength gradation to encode in the rule text:
| Critic pair | Independence | Escalation on agreement |
|---|---|---|
| Same model, different persona | none (~60% shared-error) | no (+`corroborated` tag) — R3a |
| Same vendor, different tier (fable/opus/sonnet) — available in Claude Code today | partial (correlated within family; large accurate models correlate even cross-provider) | +1 only for CRITICAL/HIGH candidates; tag `tier-diverse` |
| Different vendors (Claude/Gemini/GPT critics — needs item 6 adapters) | quasi-independent | full +1 escalation restored |
Note `CLAUDE_CODE_SUBAGENT_MODEL` env override (silently overrides frontmatter pins) — the workflow must warn when the override flattens an intentionally heterogeneous config.

**R3d — Sequential mode: explicit no-escalation.** In role-switching mode independence is weakest (same session window, same instance) — `sequential-fallback.md` merge step gets its own sentence: agreement between sequential personas never escalates; tag only.

**Migration/discipline:**
- Lockstep edit of all 4 locations + `grep -rn "escalate severity by one level" .agent/ .claude/ System/` → only new wording remains.
- `validate_skill.py` on skill-parallel-orchestration; wrapper grep; CHANGELOG.
- Do NOT touch: dedup rule 1 (±3 lines), cross-category re-attribution rule 2, bikeshedding filter rule 4 (v3.19.0, objective), `--severity` filter rule 5, iteration caps.

**Sequencing note:** R3a/R3b/R3d are pure text changes — **shippable immediately, independent of item 6**. R3c's tier-diverse form is also available now (Claude Code only); its cross-vendor form unlocks after 6a/6b/6c validate.

**Acceptance:** 4 locations byte-consistent; old wording grep-clean; gradation table present in SKILL §6; vdd-multi accepts per-critic model config (documented + parsed in Phase 0); sequential path explicitly never escalates.

---

## P2 — Aging

### 8. 🔜 [C-02] Re-ground the fresh-context rationale
Replace "relationship drift / AI becoming too agreeable over time" with the documented mechanisms: multi-turn context interference + assumption lock-in (−39%, arXiv:2505.06120), context rot (Chroma 2025), pushback-driven sycophantic belief updates (TRUTH DECAY/SYCON). **Practice unchanged** (fresh context per review stays mandatory — it scored Current). Files: `vdd-adversarial/SKILL.md:25`, `vdd-sarcastic/SKILL.md:24`, `vdd-methodology.md:23,46` ("Entropy Resistance" wording).

### 9. 🔜 [C-06] Model-pin hygiene for critic agents
Document in `references/claude-code.md` + critic wrappers: `fable` tier exists above `opus`; `CLAUDE_CODE_SUBAGENT_MODEL` env silently overrides frontmatter; `effort` field available. Audit critic prompts for severity-threshold literalism (Opus 4.7+ follows "only report high-severity" literally → recall drops; correct pattern: "report everything with confidence+severity, filter downstream" — same wording as item 5.1). Consider `model: opus` → explicit comment why not fable (cost) or adopt tier-diverse config from R3c.

### 10. 🔜 [C-10] Position regex layer as deterministic floor; add LLM semantic-review pass
`security-audit/SKILL.md`: methodology section gets an explicit two-layer model — (1) deterministic floor: regex + external tools (reproducible, cheap, CI-gateable); (2) LLM semantic pass: long-context taint/logic review + tool-description poisoning check (the class regex categorically cannot catch). Add semgrep licensing footnote (CE since Dec 2024; Opengrep fork as drop-in alternative). Reference frontier evidence (AIxCC, Big Sleep, Codex Security / Claude Code Security) as rationale.

### 11. 🔜 [C-13] Resolve critic capability asymmetry (orchestrator-supplies-evidence contract)
Critics (`tools: Read, Grep, Glob`) cannot execute tests/scanners, yet their exit bar requires "full test run executed". Chosen direction (consistent with P0 item 2 residual): **orchestrator supplies execution evidence** — `vdd-multi.md` Phase 1 prompt template includes: test-run output (or `tests: NOT RUN`), `run_audit.py` JSON for critic-security. Critics treat supplied evidence as input; absence → finding "exit-bar condition unverifiable", not approval. Alternative (rejected for now): granting critics Bash — widens attack/cost surface, breaks read-only critic guarantee.

### 12. 🔜 [C-16] Align skill-adversarial-performance termination with the objective bar
`.agent/skills/skill-adversarial-performance/SKILL.md:73–79`: add test-execution/evidence condition + the 3-state convergence enum (`clean-pass | issues-found | bikeshedding-only`) so the SKILL matches its own wrapper `critic-performance.md:13`. Bump version, gate.

---

## P2-experiment

### 13. 🧪 [C-12] Run the pre-registered A/B (sarcasm & multi-critic effectiveness)
Protocol fully specified in the audit report, **Appendix A** (do not redesign — it is pre-registered): 24 seeded bugs / 8 files + 2 clean controls; arms A (plain exhaustive), B (adversarial), C (sarcastic), D (`/vdd-multi --no-fix`), E (single fable reviewer, cost-matched); N=3; metrics recall/FP/bikeshedding-ratio/tokens/wall-clock; decision rules fixed (sarcasm survives only if recall(C)−recall(B) > variance with FP(C) ≤ FP(B); multi survives only if recall(D)−recall(max(A,E)) ≥ +10pp). Outcome feeds item 5 (keep-vs-deprecate vdd-sarcastic) and item 7/R3c (single-strong-reviewer vs 3 critics). ~1–2 days. Publishable: no such study exists as of 2026-06-10.

---

## Dependencies & recommended order

```
3 (MCP/agentic security)  — independent, highest risk → FIRST
4 (OWASP remap)           — independent, small, fixes compliance mappings
5 (retire politeness)     — independent; final form (deprecate K2?) waits on 13
6 (vendor adapters)       — independent; per-vendor validation needs operator machines
7 R3a/R3b/R3d             — ✅ DONE (Task 072 / v3.20.3)
7 R3c (cross-vendor)      — BLOCKED BY 6 (tier-diverse form available now in Claude Code)
8, 9, 10, 12              — independent, small
11                        — pairs naturally with 7 (both edit vdd-multi Phase 1/2) → one cycle
13 (experiment)           — anytime; informs 5 and 7/R3c final decisions
```

Suggested cycles: **(1)** item 3 → **(2)** item 4 → **(3)** items 7-R3a/b/d + 11 together (one vdd-multi/skill-parallel-orchestration cycle) → **(4)** item 5 → **(5)** item 6 (sub-cycles 6a–6c, then 6d–6e) → **(6)** items 8/9/10/12 batched → **(7)** experiment 13 → revisit 5 and 7-R3c with data.

## Key evidence quick-refs (full citations in audit §Bibliography)

- Correlated errors / ensembles: arXiv:2506.07962 (ICML 2025) · arXiv:2601.12307 · arXiv:2604.02460
- Tone/persona/sycophancy: arXiv:2510.04950 · arXiv:2311.10054 · arXiv:2603.00539 · arXiv:2604.16790 · GPT-5 system card · Opus 4.5/4.6 system cards
- Context: arXiv:2505.06120 · Chroma context-rot (2025-07) · Anthropic context engineering (2025-09)
- Agentic security: OWASP ASI Top 10 2026 (2025-12-09) · NSA MCP CSI (2026-05) · CVE-2025-6514 / -49596 / -53773 / -54135 · mcp-scan→agent-scan
- Vendor parallel primitives: Gemini CLI subagents (2026-04) · Codex CLI subagents (2026-03) · Cursor 2.4 subagents (2026-01)
