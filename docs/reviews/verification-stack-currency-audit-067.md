# Verification Stack Currency Audit — Task 067

- **Date:** 2026-06-10
- **Auditor:** Orchestrator (VDD Framework Audit mode), web research via 3 parallel research agents (access date 2026-06-10)
- **Target:** K1 `vdd-adversarial` (v1.1) · K2 `vdd-sarcastic` (v1.1) · K3 `vdd-multi` (v3.19.0 + critic agents + `skill-adversarial-{security,performance}`) · K4 `System/Agents/10_security_auditor.md` (v3.6.0) · K5 `security-audit` (v3.3)
- **Framework version:** v3.19.1
- **Status:** COMPLETE — 16 claims scored; 2 Harmful (P0), 7 Outdated (P1), 5 Aging (P2), 2 Unsubstantiated
- **Scope exclusions:** Objective-Convergence exit-bar design (hardened v3.18.0/v3.19.0, 2026-05-29 — only residuals checked); live cross-vendor runs; A/B experiment execution (designed in Appendix A, not run — user decision 2026-06-10).

---

## 1. Methodology

Components are audited **as claims, not files**. Each load-bearing claim is anchored (file:line, verified at v3.19.1 HEAD), graded against external evidence gathered 2026-06-10, and rolled up per component.

**Dimensions:** D1 behavioral-assumption validity · D2 capability leverage · D3 threat-landscape currency · D4 cross-vendor parity · D5 effectiveness evidence · D6 internal consistency.

**Currency verdicts:**
- **Current** — supported by ≥1 external source ≤12 months old; no credible contradiction found.
- **Aging** — correct at write-time; superseded standard/practice exists but it still works.
- **Outdated** — contradicted by ≥2 independent 2025–26 sources, or premised on facts no longer true.
- **Harmful** — actively degrades outcomes today (requires [R]+[W] evidence).
- **Unsubstantiated** (orthogonal tag) — zero supporting evidence in either direction.

**Evidence grades:** `[R]` repo fact (file:line) · `[W]` web source with date · `[I]` inference. No verdict rests on [I] alone.

---

## 2. Claims Register

| # | Claim | Anchor(s) [R] | Dim | Verdict | Key external evidence [W] |
|---|-------|---------------|-----|---------|---------------------------|
| C-01 | "Forced Negativity bypasses LLM politeness filters" | `vdd-sarcastic/SKILL.md:40`; `vdd-adversarial/references/vdd-methodology.md:44`; `vdd-adversarial/SKILL.md:24`; `skill-adversarial-security/SKILL.md:16` | D1 | **Outdated** | Sycophancy now trained out vendor-side: GPT-5 system card (2025-08) −70–75% in prod A/B; Claude Opus 4.5/4.6 system cards (2025-11/2026-02) low audited rates. Rudeness benefit = one GPT-4o-only MCQ preprint (arXiv:2510.04950, Oct 2025), never replicated on code or 2026 models; persona prompts give no correctness gain (EMNLP 2024 Findings, arXiv:2311.10054). Harsh/elaborate critic prompts *increase* false positives (arXiv:2603.00539, Feb 2026; arXiv:2604.16790, Apr 2026). No vendor doc endorses adversarial tone as mitigation. |
| C-02 | Fresh context per review prevents "relationship drift — the AI becoming too agreeable over time" | `vdd-sarcastic/SKILL.md:24`; `vdd-adversarial/SKILL.md:25`; `vdd-methodology.md:23,46` | D1 | **Current (practice) / Aging (mechanism)** | Practice strongly supported: −39% multi-turn degradation (arXiv:2505.06120, May 2025); "context rot" (Chroma, Jul 2025); Anthropic context-engineering + subagent-isolation guidance (2025-09). Mechanism misattributed: documented causes are context interference + assumption lock-in; agreeableness drift appears only under user pushback (TRUTH DECAY, arXiv:2503.11656; SYCON-Bench), not spontaneously. |
| C-03 | "Meanness is the mechanism" — tone causally improves detection | `vdd-sarcastic/SKILL.md:38` | D1/D5 | **Outdated · Unsubstantiated as causal** | Zero studies on sarcastic reviewer personas (absence finding, 2026-06-10). Tone effects small/unstable/direction-flipping across generations (arXiv:2510.04950 vs arXiv:2402.14531 vs arXiv:2512.12812). Anthropic Opus 4.7/4.8 migration guidance: review recall is driven by *reporting-threshold instructions*, not aggression. |
| C-04 | Sarcasm "provokes the developer into defending their code" | `vdd-sarcastic/SKILL.md:19` | D5 | **Unsubstantiated** | Human-psychology claim; in-pipeline the "developer" is the Builder AI. No evidence either way. |
| C-05 | Security-critic termination requires "at least one snarky comment" | `skill-adversarial-security/SKILL.md:68` | D6 | **HARMFUL** | [R] Directly contradicts the framework's own v3.18/v3.19 doctrine ("approval bound to the objective bar", `vdd-sarcastic/SKILL.md:30`). Tone-as-success-criterion forces noise on clean code; [W] judge-harshness/overcorrection literature (arXiv:2603.00539) shows exactly this inflates false positives. The one residual the 065/066 hardening missed. |
| C-06 | All critics pinned `model: opus` | `.claude/agents/critic-{logic,security,performance}.md:5`; `security-auditor.md` | D2/D4 | **Aging** | Alias still valid → resolves to Opus 4.8 (Claude Code subagent docs, fetched 2026-06-10). But: `fable` tier now exists above it; `CLAUDE_CODE_SUBAGENT_MODEL` env silently overrides frontmatter pins; `effort` field unused; Opus 4.7+ follows severity-threshold instructions literally (vendor migration note) — critic prompts should say "report everything with confidence+severity, filter downstream". |
| C-07 | Sequential role-switching fallback for non-Claude vendors, "functionally equivalent" | `vdd-multi.md:163–171`; `skill-parallel-orchestration` §1 (Gemini/Cursor stubs) | D4 | **Outdated** | The premise (no parallel primitives elsewhere) is now false: Gemini CLI native subagents (Google blog, Apr 2026), OpenAI Codex CLI custom agents w/ parallel spawn (OpenAI docs, Mar 2026), Cursor subagents + background agents (Jan 2026). Vendors need parallel-dispatch adapters, not sequential fallbacks. "Functionally equivalent" also never validated (KNOWN cap: Unvalidated). |
| C-08 | Severity escalation when "two critics independently flagging the same location" | `vdd-multi.md:106`; `skill-parallel-orchestration` §6 | D2 | **Outdated (reasoning)** | Same-base-model "independence" is illusory: LLMs erring pick the same wrong answer ~60% of the time, worst for same-model pairs (Correlated Errors, ICML 2025, arXiv:2506.07962); persona-differentiated same-model ensembles share priors and failure modes (arXiv:2601.12307, Jan 2026). Dual-flag = weak signal (survives prompt variation), not independent confirmation. |
| C-09 | Checklist labeled "OWASP Top 10:2025" | `security-audit/SKILL.md:70`; `references/checklists/owasp_top_10.md:1–79` | D3 | **Outdated (mislabeled)** | File header says 2025 but layout is the **2021 taxonomy** (A03 Injection, A10 SSRF). The actual 2025 final (Jan 2026): A03 = Software Supply Chain Failures (new), A05 = Injection, A10 = Mishandling of Exceptional Conditions (new), SSRF absorbed into A01. Compliance mappings exported to Jira/Snyk would be wrong. Counter-finding: API Top 10:2023 ref is **Current** (still latest, confirmed); LLM Top 10 v2.0 ref is **Current** (still latest LLM list). |
| C-10 | Regex scanner + external tools + manual checklist walk as primary methodology ("Humans miss regex patterns. EXECUTE the script") | `security-audit/SKILL.md:12,45` | D2 | **Aging** | Still a legitimate deterministic floor; external tool roster verified alive (semgrep licensing changed → CE + Opengrep fork, Jan 2025 — footnote needed). But frontier moved to hybrid LLM-driven analysis: DARPA AIxCC final (Aug 2025, 18 real 0-days found), Google Big Sleep CVEs, OpenAI Aardvark→Codex Security (Mar 2026), Anthropic Claude Code Security. Regex categorically cannot detect tool-description poisoning. |
| C-11 | MCP/agentic threats covered | one-liners only: `llm_security.md:35,70–75`; **zero** patterns in `patterns.py`; no MCP checklist | D3 | **Outdated (coverage)** | Since the checklists were written: OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10, released 2025-12-09); NSA CSI "MCP Security Design Considerations" (May 2026); CVE-2025-6514 (mcp-remote, 9.6), CVE-2025-49596 (MCP Inspector, 9.4), MCP STDIO design flaw → 11 CVEs (Apr 2026); first in-the-wild malicious MCP server (postmark-mcp, Sep 2025); s1ngularity malware weaponizing AI CLIs; Shai-Hulud npm worm (CISA alert); slopsquatting (USENIX Sec 2025). Scanners exist (Invariant mcp-scan → Snyk agent-scan). One-line checklist items with no detection are demonstrably below the mid-2026 bar — **in the framework's own home domain (agentic development)**. |
| C-12 | Stack effectiveness evidenced by anecdotes ("3 real bugs caught by Verify→Roast") | session logs / CHANGELOG; no benchmark artifact in repo | D5 | **Unsubstantiated** | No published A/B of adversarial/sarcastic-persona review vs plain thorough review exists anywhere (absence confirmed 2026-06-10). Anecdotes are confounded: cannot distinguish "the roast helped" from "a second fresh-context pass helped". Methodology to test exists (CriticGPT seeded-bug protocol, arXiv:2407.00215; SWR-Bench). |
| C-13 | Critics restricted to `tools: Read, Grep, Glob` (no Bash) while the objective bar requires "full test run executed" | `.claude/agents/critic-*.md:4`; `vdd-adversarial/SKILL.md:29` | D2 | **Aging** | Critics cannot run tests or verify scanner output — condition (1) of their own exit bar is unverifiable by them; they must trust the orchestrator's claim. 2026 practice for review agents is prove-with-execution (CriticGPT-style; vendor security agents run tools). |
| C-14 | Security Auditor role prompt: taint analysis as manual 3-step read; no agentic/MCP threat model | `10_security_auditor.md:35–38`; absence of ASI/MCP content | D2/D3 | **Outdated** | Same evidence base as C-10/C-11: OWASP ASI taxonomy + NSA MCP guidance + hybrid-LLM methodology now define the bar for a "Security Auditor" of agentic systems. |
| C-15 | "Mock the results if you cannot run it directly, but assume standard tool outputs" | `skill-adversarial-security/SKILL.md:29` | D6/D2 | **HARMFUL** | [R] Instructs a *security critic* to fabricate scanner results — direct contradiction of `core-principles` §3 (anti-hallucination) and of `security-audit/SKILL.md:12` ("EXECUTE the script"). Compounding: `critic-security` has no Bash (C-13), so in every `/vdd-multi` run the fabrication branch is the *default path*, not the exception. [W] Fabricated-evidence risk in LLM judging is exactly the failure class documented by the overcorrection/judge-bias literature (arXiv:2603.00539, 2604.16790). |
| C-16 | `skill-adversarial-performance` termination: "all categories reviewed / remaining issues are micro-optimizations" | `skill-adversarial-performance/SKILL.md:73–79` | D6 | **Aging** | Pre-065-style exit: no test-run condition, no 3-state convergence enum (the wrapper `critic-performance.md:13` adds the enum, masking the drift). Minor inconsistency with the v3.18/19 doctrine. |

**Distribution:** 2 Harmful · 7 Outdated · 5 Aging · 2 Unsubstantiated · API-2023/LLM-v2.0/Solidity/Solana references and fresh-context practice confirmed Current.

---

## 3. Component scorecards

> Rubric: component verdict = worst load-bearing claim; distribution shown so one residual doesn't silently condemn sound mechanics.

### K1 `vdd-adversarial` — **Verdict: Outdated rationale, Current mechanics → net AGING**
- **Current:** Objective Convergence exit bar (§2, fresh from v3.18); mandatory critique template + Hallucination Check (§6); decision tree / failure simulation; fresh-context practice (C-02).
- **Outdated:** "Forced Negativity to bypass politeness filters" as principle №2 (C-01) — the justifying theory, not the mechanics.
- **Fix cost:** one-paragraph reword (replace politeness-filter rationale with exhaustive-reporting rationale: "report everything with confidence + severity; filter downstream"). Mechanics untouched.

### K2 `vdd-sarcastic` — **Verdict: OUTDATED**
- The component's *entire unique value-add* (sarcastic tone) rests on C-01/C-03/C-04: zero direct evidence, contradicted adjacent evidence, plausibly FP-inflating on current models. What works in it (objective bar §4, anti-rationalization §1) is inherited from K1.
- Honest positioning per evidence: "stylistic choice, no evidence base" — keep as opt-in skin with that disclaimer, or deprecate. Testable via Appendix A arm C-vs-B.

### K3 `vdd-multi` + critic set — **Verdict: OUTDATED with one HARMFUL residual**
- **Current:** parallel spawn for latency + context isolation (vendor-validated pattern); location dedup; bikeshedding filter (objective, v3.19.0); `--diff-only/--fail-on` CI surface.
- **Harmful:** C-15 ("mock the results") sits inside its security critic's skill, and C-13 makes that branch the default path.
- **Outdated:** C-07 (sequential-fallback premise — all 3 target vendors now have native parallel subagents), C-08 (severity escalation double-counts one model's prior).
- **Aging:** C-06 (opus pin: works; tier/override/effort/severity-literalism notes missing).
- **Cost model (design property):** first pass ≥3× single-review tokens (3 opus critics) + unbounded per-category re-spawns by default. 2026 evidence: a single strong reviewer matches same-base-model persona ensembles on quality (arXiv:2601.12307; arXiv:2604.02460); parallelism is defensible on wall-clock and isolation, not detection quality. Cost-matched alternative worth testing: one Fable-tier reviewer ≈ 1.5–2 Opus critics.

### K4 `10_security_auditor.md` — **Verdict: OUTDATED**
- **Current:** severity discipline, BLOCKER semantics, report contract, supply-chain prime directive.
- **Outdated:** no agentic/MCP threat model (C-14) — for an agentic-development framework this is the role's primary blind spot; methodology pre-dates hybrid LLM-driven analysis (C-10).

### K5 `security-audit` skill — **Verdict: OUTDATED (coverage + label), strong Current core**
- **Current (confirmed, do not touch):** OWASP API Top 10:2023 ref (still latest); LLM Top 10 v2.0 ref (still latest LLM list); Solidity/Solana checklists (March 2026 — verify Token-2022 hooks; EthTrust successor expected 2H 2026); external tool roster all alive (semgrep needs licensing footnote + Opengrep mention); regex floor with honest known-limitations note.
- **Outdated:** C-09 — "OWASP Top 10:2025" label on 2021 taxonomy (compliance mappings wrong); C-11 — agentic/MCP threats at one-liner depth with zero detection patterns while OWASP ASI01–ASI10, NSA CSI, 10+ CVEs, in-the-wild incidents and shipping scanners (mcp-scan/agent-scan) define the current bar.
- **Aging:** C-10 — regex+checklist as *primary* methodology; should become the deterministic floor under an explicit LLM semantic-review pass.

---

## 4. Effectiveness assessment — "does it actually give better results?"

Decomposed into five separable layers (they have different evidence statuses):

| Layer | Evidence status (2026-06-10) |
|---|---|
| 1. Fresh context per review | **Supported** — multi-turn degradation −39%; context rot; vendor subagent-isolation guidance. |
| 2. Second/extra review pass | **Supported (generic)** — multi-pass aggregation lifts review F1 up to +43.67% (SWR-Bench, Sep 2025). Note: this supports *re-review*, not *adversarial tone*. |
| 3. Role-specialized parallel critics | **Contested** — same-base-model persona ensembles matched by one strong reviewer at ~⅓ cost (Jan/Apr 2026 preprints); parallelism earns latency + isolation, not quality. Heterogeneous-model critics would restore independent signal. |
| 4. Forced negativity (harsh instruction) | **Unsupported, risk-bearing** — no gain evidence; FP-inflation evidence on harsh/elaborate judge prompts. |
| 5. Sarcastic tone | **No evidence at all** (absence confirmed); adjacent evidence neutral-to-negative. |

**Can conclude:** the stack's *architecture* (isolated fresh-context re-review with structured output and an objective exit bar) is well-aligned with 2026 best practice; its *theatrical layer* (4–5) is unsupported and the field's evidence points the other way; its *security coverage* lags the threat landscape it is supposed to defend against.

**Cannot conclude:** that the pipeline beats a plain "review thoroughly, report everything with confidence+severity, fresh context, structured output" baseline — no internal benchmark exists, the repo's anecdotes ("3 real bugs caught by the Verify→Roast loop") cannot attribute the catch to the roast vs the extra fresh-context pass, and no published study fills the gap (that absence is itself a finding: nobody has shown adversarial personas help). Resolution requires Appendix A.

---

## 5. Modernization backlog

Priority mapping: Harmful→P0 · Outdated→P1 · Aging→P2 · Unsubstantiated→P2-experiment. All items trace to claim IDs. Framework edits go through a follow-up cycle with the `skill-self-improvement-verificator` gate.

### P0 — Harmful (one-line-class fixes, continue the 065/066 hardening)
1. **[C-05]** `skill-adversarial-security/SKILL.md` §7: delete the "at least one snarky comment" termination condition; bind termination to the objective bar (automation executed + no Critical/High + bikeshedding-only).
2. **[C-15]** `skill-adversarial-security/SKILL.md` §3: delete "Mock the results…"; replace with: "If the script cannot be executed in your context, report `scan: NOT RUN` and proceed with manual review only — never fabricate scanner output. The orchestrator runs `run_audit.py` and passes results into the critic prompt." (Pairs with item 11.)

### P1 — Outdated
3. **[C-11, C-14]** Agentic/MCP security upgrade: new `references/checklists/mcp_agentic_security.md` mapped to OWASP ASI01–ASI10 (Dec 2025) + NSA MCP CSI (May 2026); regex patterns for MCP config artifacts (`mcp.json` provenance, auto-approve flags, unpinned `npx -y` servers, missing lockfile/hash pinning); add `mcp-scan`/Snyk `agent-scan` to the external-tool roster; add agentic threat model section to `10_security_auditor.md`.
4. **[C-09]** Re-map `owasp_top_10.md` to the actual 2025 final taxonomy (A03 Software Supply Chain Failures, A05 Injection, A10 Mishandling of Exceptional Conditions, SSRF→A01) — or relabel honestly as 2021 until done. Compliance mappings depend on it.
5. **[C-01, C-03 / K2]** Retire the "politeness-filter bypass" rationale across K1/K2/methodology; replace Forced Negativity wording with exhaustive-reporting instruction ("report every issue incl. low-confidence, attach confidence+severity, filter downstream" — matches Opus 4.7+ vendor guidance). Reposition `vdd-sarcastic` as opt-in stylistic skin with an explicit "no evidence base; tone is not the mechanism" note (or deprecate after Appendix A).
6. **[C-07]** Graduate vendor references from sequential-fallback stubs to parallel-dispatch adapters: Gemini CLI subagents (Apr 2026), Codex CLI custom agents (Mar 2026), Cursor subagents (Jan 2026). Sequential fallback demoted to last-resort for primitive-less runtimes.
7. **[C-08]** Re-scope severity escalation: same-model dual-flag = weak corroboration (no escalation, or +0 with note); offer optional model-heterogeneous critic config (different base models per critic) which restores genuinely independent agreement.

### P2 — Aging
8. **[C-02]** Re-ground the fresh-context rationale (context interference/assumption lock-in + pushback-driven sycophancy), drop "relationship drift/AI becomes agreeable" wording. Practice unchanged.
9. **[C-06]** Document `fable` tier, `CLAUDE_CODE_SUBAGENT_MODEL` override, `effort` field; audit critic prompts for severity-threshold literalism on Opus 4.7+.
10. **[C-10]** Position regex layer as deterministic floor; add explicit LLM semantic-review pass to `security-audit` methodology (only way to catch tool-description poisoning); semgrep CE licensing footnote + Opengrep alternative.
11. **[C-13]** Resolve the critic capability asymmetry: either grant critics test/scanner execution, or restructure so the orchestrator supplies execution evidence (test output, scan JSON) as critic input — making exit-bar condition (1) verifiable.
12. **[C-16]** Align `skill-adversarial-performance` termination with the 3-state convergence enum + objective bar.

### P2-experiment
13. **[C-12]** Execute the pre-registered A/B (Appendix A). Publishable: no such study exists as of 2026-06-10.

---

## Appendix A — Pre-registered A/B experiment protocol (design only)

**Question:** Does the adversarial stack beat a plain thorough-review baseline, and which layers earn their cost?

- **Corpus:** 24 seeded bugs in 8 realistic files (~150–400 LoC each): 8 logic, 8 security, 8 performance; severity-stratified (8 CRITICAL / 8 HIGH / 8 MEDIUM). Ground truth (file, line, class, severity) sealed in `tests/fixtures/ab-corpus/ground_truth.json` **before** any arm runs; clean-file controls (2 files, 0 bugs) included to measure FP floor.
- **Arms (same model + version, fresh context per run, N=3 runs/arm/file):**
  - **A** — plain baseline: "Review thoroughly; report every issue incl. low-confidence, with confidence + severity; structured output." No persona.
  - **B** — `vdd-adversarial` (neutral adversarial, no sarcasm).
  - **C** — `vdd-sarcastic` (full Sarcasmotron).
  - **D** — `/vdd-multi --no-fix` (3 parallel opus critics + merge).
  - **E (optional, cost-matched):** single top-tier (`fable`) reviewer with arm-A prompt, to test RQ4's "one strong reviewer" hypothesis against D.
- **Metrics:** seeded-bug recall (by class & severity); false positives per file (on controls and seeded files); bikeshedding ratio (style nits / total findings); tokens; wall-clock.
- **Pre-registered decision rules (fixed before runs):**
  1. Sarcasm survives only if recall(C) − recall(B) > pooled run variance **and** FP(C) ≤ FP(B). Otherwise → deprecate K2 (backlog item 5 hard form).
  2. Multi-critic survives its ≥3× token cost only if recall(D) − recall(max(A,E)) ≥ +10pp at equal-or-lower FP. Otherwise → default to single strong reviewer; keep `/vdd-multi` for latency-critical CI only.
  3. Forced negativity (B vs A) judged the same way as rule 1.
- **Effort estimate:** 1–2 days; runnable inside the framework (`--no-fix --output`); analysis is a ~100-line script over structured findings.

---

## Bibliography (access date 2026-06-10)

**Prompting/sycophancy/context:** arXiv:2510.04950 (Mind Your Tone, Oct 2025) · arXiv:2402.14531 (Should We Respect LLMs, 2024) · arXiv:2311.10054 (persona ineffectiveness, EMNLP 2024 Findings) · arXiv:2603.00539 (reviewer overcorrection, Feb 2026) · arXiv:2604.16790 (judge bias audit, Apr 2026) · arXiv:2502.08177 (SycEval) · OpenAI sycophancy postmortems (2025-04-29 / 2025-05-01) · GPT-5 system card (2025-08-13) · Claude Opus 4.5 / 4.6 system cards (2025-11 / 2026-02) · arXiv:2511.17220 (PARROT) · arXiv:2505.06120 (Lost in Multi-Turn, May 2025) · Chroma context-rot report (Jul 2025) · Anthropic "Effective context engineering" (2025-09-29) · arXiv:2503.11656 (TRUTH DECAY) · arXiv:2505.23840 (SYCON-Bench).
**Ensembles/models:** arXiv:2601.12307 (Strong Single Agent Baseline, Jan 2026) · arXiv:2604.02460 (single vs multi under equal budgets, Apr 2026) · arXiv:2506.07962 (Correlated Errors, ICML 2025) · arXiv:2511.07784 (Can LLM Agents Really Debate) · arXiv:2509.01494 (SWR-Bench) · arXiv:2407.00215 (CriticGPT seeded bugs) · Anthropic multi-agent research system (Jun 2025) · Claude Code subagent docs (fetched 2026-06-10) · Google Developers Blog: Gemini CLI subagents (Apr 2026) · OpenAI Codex subagents docs (Mar 2026) · Cursor 2.4 subagents (Jan 2026, secondary).
**Security:** OWASP Top 10:2025 final (Jan 2026) · OWASP API Security Top 10:2023 (confirmed latest) · OWASP LLM Top 10 v2.0 (confirmed latest) · OWASP Top 10 for Agentic Applications 2026 / ASI01–ASI10 (2025-12-09) · NSA CSI "MCP Security Design Considerations" (May 2026) · MCP Security Best Practices (modelcontextprotocol.io) · CVE-2025-6514 · CVE-2025-49596 · CVE-2025-53773 · CVE-2025-54135 · MCP STDIO design flaw + 11 CVEs (Apr 2026) · postmark-mcp incident (Sep 2025) · s1ngularity/Nx (Aug 2025, Wiz) · Shai-Hulud worm (CISA alert 2025-09-23; Datadog/Microsoft) · USENIX Security 2025 slopsquatting study · CSA slopsquatting note (Apr 2026) · Invariant mcp-scan → Snyk agent-scan · Semgrep CE licensing / Opengrep fork (Jan 2025) · DARPA AIxCC final (Aug 2025) · Google Big Sleep (2025) · OpenAI Aardvark → Codex Security (Mar 2026) · EEA EthTrust SL v3 (Mar 2025).
