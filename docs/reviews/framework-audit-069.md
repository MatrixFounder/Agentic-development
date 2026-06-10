# Framework Audit: Agentic/MCP Security Upgrade (Task 069)

**Date:** 2026-06-10
**Auditor:** Self-Improvement Verificator
**Target:** `docs/TASK.md`
**Status:** **APPROVED** (Mode A — Specification Audit)

## 1. Compliance Checklist (Mode A)

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Meta-Information** | ✅ Pass | ID 069, slug `mcp-agentic-security-upgrade`, Mode = Framework Upgrade, source traced to roadmap item 3 + audit-067 claims C-11/C-14 + user request (2026-06-10). |
| **Root Integrity** | ✅ Pass | Additive coverage upgrade in the framework's own home domain. Anti-hallucination honored: ASI01–ASI10 names, NSA CSI controls, and scanner CLI (`snyk-agent-scan`) were **web-verified this session** against primary sources (genai.owasp.org, nsa.gov U/OO/6030316-26, github.com/snyk/agent-scan) instead of trusting model memory — the release dates straddle the knowledge cutoff. Atomicity: R1–R7 independently verifiable. Stub-First applies to R2 (new `scan_mcp_agentic`) — **carry-forward to PLAN**. |
| **Skill Compatibility** | ✅ Pass | No new agents/prompts/workflows. `10_security_auditor.md` edit is additive (threat-model subsection + checklist ref); its TIER 0 loading block untouched. New checklist is a reference file, not a skill — `init_skill.py` gate correctly N/A (documented in TASK §4). |
| **Documentation** | ✅ Pass | R7 covers CHANGELOG EN+RU, roadmap status flip, **and** the registry refresh — `System/Docs/SKILLS.md:87` was caught as stale-specific ("v3.2", "121 automated regex patterns") and added to scope; without R7(i) this upgrade would have widened existing registry drift. |
| **Migration** | ✅ Pass (N/A) | `--scan-type mcp` is additive; `all` gains one scanner. Projects WITH MCP artifacts will see new findings — that is the feature, severity-capped at high (no new critical) so existing `--fail-on critical` CI gates cannot newly break. No persisted state. |

## 2. Failure-Condition Scan
- Removing `core-principles`/`skill-safe-commands` from any agent? ❌ No.
- Modifying a bootstrap file (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md`) without `System/Docs` update? ❌ No bootstrap file touched.
- Creating a new Workflow without defining its Trigger? ❌ No new workflow.
→ **No blocking conditions.**

## 3. Risk Analysis

- **R1 — False-positive storm on agentic repos (incl. this one).** The tool-description poisoning heuristic could fire on legitimate imperative prose (skill/agent `description:` frontmatter in `.md` files all begin "Use when…"). *Mitigation:* TASK restricts the heuristic to JSON/code tool-definition surfaces; **PLAN must lock the file-set**: markdown agent files are explicitly the LLM-review class (the R4(c) limitation note), not regex targets. Calibration check performed pre-audit: repo-wide grep for `autoApprove`/`alwaysAllow`/`dangerously-skip`/`npx -y` over `.claude/` and all JSON → **zero hits**, so UC-2 (zero MCP findings on this repo) is achievable, not aspirational.
- **R2 — Multi-line JSON vs line-level scanning.** Pretty-printed MCP configs put `"env": {` and the secret on different lines; line-local patterns would silently miss them (false-negative class). *Mitigation:* PLAN must specify whole-file matching for the MCP scanner with the existing IaC-style ReDoS guard (skip file if any line > `MAX_LINE_LENGTH`) — precedent already in `scan_iac`.
- **R3 — `SKIP_DIRS` swallows `.vscode/mcp.json`.** The generic walk prunes `.vscode` everywhere, so the canonical VS Code MCP config location is invisible to a naive implementation. *Mitigation:* PLAN must give `scan_mcp_agentic` its own prune set (`SKIP_DIRS − {'.vscode'}`) — cheap because the scanner is filename-targeted; R6 has a dedicated regression test for exactly this hole.
- **R4 — Finding duplication with `scan_secrets`.** An inline key in an MCP `env` block may be flagged by both scanners. *Acceptable:* different framing (CWE-798 secret vs ASI03 privilege-abuse surface); both are real. Noted so the reviewer doesn't "fix" it by weakening either scanner.
- **R5 — Doc/CLI drift.** `--scan-type` choices appear in `run_audit.py` argparse + docstring, SKILL §2 usage block, and the registry line. *Mitigation:* R4(d) sync list + R7(i); PLAN verification step greps for the stale choice-string.
- **R6 — External-tool safety.** `snyk-agent-scan` can start MCP servers to probe them; an audit script must never do that implicitly. *Mitigation:* R3(b) hard-bans `--dangerously-run-mcp-servers`; consent stays with the operator.

## 4. Verdict
**APPROVED.** The specification is evidence-anchored (all post-cutoff facts verified against primary sources this session), scope-fenced against neighboring roadmap items (4, 10, 11), severity-disciplined, and regression-aware. Proceed to Planning.

**Carry-forward for the PLAN:**
1. Stub-First sequencing for `scan_mcp_agentic` (skeleton + red tests → logic → green).
2. Lock the heuristic file-set (JSON/code only; `.md` = LLM-review class).
3. Whole-file matching + IaC-style ReDoS guard for the MCP scanner.
4. Custom prune set (`SKIP_DIRS − {'.vscode'}`) + the `.vscode/mcp.json` regression test.
5. Backup step before edits (workflow §3.1); explicit `validate_skill.py` + pytest + repo-green `run_audit.py` gates; rollback instructions.
6. Version/doc lockstep greps (3.4 sync across frontmatter/header/docstring/`__version__`; scan-type list in SKILL §2).

---

# Mode B — Plan Audit (Task 069)

**Target:** `docs/PLAN.md` · **Status:** **APPROVED**

| Check | Status | Observation |
| :--- | :--- | :--- |
| **Verification Step** | ✅ Pass | T6 is a dedicated gate: full pytest, `run_audit.py` repo-green with zero-MCP-findings assertion (UC-2), `validate_skill.py` single + 43/43 baseline loop, drift greps, diff-scope check vs backups. Per-phase atomic verifies in T1–T5. |
| **Rollback** | ✅ Pass | T0 backs up all 10 edit targets + bootstrap files to `.agent/archive/`; new files (checklist, tests) documented as delete-to-rollback; restore path = workflow §5. |
| **Atomic Updates** | ✅ Pass | T1–T7 map 1:1 to RTM R1–R7; strict order with stop-on-gate-failure; lockstep wording rule for severity/category/CWE strings across patterns ↔ checklist ↔ SKILL §2. |
| **Test Coverage** | ✅ Pass | T2a stubs verified importable → T2b 12 tests written Red (incl. the three audit-risk regressions: `.vscode` prune hole, multi-line env block, pinned-vs-unpinned npx negative case) → T2c Green. Self-exclusion regression retained. |

**Carry-forward checks honored:** all 6 Mode A items appear as concrete PLAN steps (T2a; T2c file-targeting block; T2c matching-mode block; `MCP_SCAN_PRUNE` + test #3; T0/T6; T4.3 + T6.4).

**Residual risks accepted:** (i) pattern 4 (`"args"` JSON form) may double-fire with pattern 3 on one-line configs — dedup not required, both findings are true; (ii) `snyk-agent-scan "."` path semantics differ slightly from machine-wide default scan — acceptable, non-fatal external.

**Verdict: APPROVED.** Proceed to Execution (T0 backup first).
