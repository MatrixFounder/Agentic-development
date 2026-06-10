# Technical Specification: OWASP Top 10 Checklist Re-map to 2025 Final (C-09)

### 0. Meta Information
- **Task ID:** 070
- **Slug:** `owasp-top10-2025-remap`
- **Mode:** Framework Upgrade (meta-operation — modifies the security-audit skill checklist, SKILL.md, and scanner docstrings)
- **Type:** P1 modernization, roadmap item 4. Closes audit-067 claim C-09 (checklist titled "2025" but laid out on the 2021 taxonomy → compliance mappings exported to Jira/Snyk are wrong).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни ### 4. 🔜 [C-09]" + `docs/verification_roadmap.md` item 4 + `docs/reviews/verification-stack-currency-audit-067.md` (claim C-09).

## 1. General Description

`references/checklists/owasp_top_10.md` claims "OWASP Top 10:2025 (Final Release)" in its header but its ten sections follow the **2021 taxonomy** (A03 = Injection, A10 = SSRF, A05 = Misconfiguration…). The actual 2025 final — **verified 2026-06-10 directly against owasp.org/Top10/2025/** — is:

| # | 2025 Category (official name) | Relation to 2021 |
|---|---|---|
| A01 | Broken Access Control | unchanged #1; **absorbs 2021-A10 SSRF** |
| A02 | Security Misconfiguration | ↑ from #5 |
| A03 | Software Supply Chain Failures | **NEW** (broadens 2021-A06; absorbs supply-chain items of 2021-A08) |
| A04 | Cryptographic Failures | ↓ from #2 |
| A05 | Injection | ↓ from #3 |
| A06 | Insecure Design | ↓ from #4 |
| A07 | Authentication Failures | renamed (was "Identification and Authentication Failures") |
| A08 | Software or Data Integrity Failures | renamed ("and"→"or"); supply-chain items re-homed to A03 |
| A09 | Security Logging and Alerting Failures | renamed (was "…Logging and Monitoring Failures") |
| A10 | Mishandling of Exceptional Conditions | **NEW** (CWE-209/390/754/636; error handling, fail-open) |

Blast radius (established by repo-wide grep, 2026-06-10): the checklist itself, 6 lines in `security-audit/SKILL.md` (§2 scope tags ×4, §3 Top Checks ×2), and 4 docstrings in `scripts/audit/scanners.py`. **Evidence-based correction of the roadmap assumption:** `patterns.py` carries **no** OWASP A-number category tags (findings are tagged with `category` strings + CWE only); the A-number tags live in `scanners.py` docstrings. `10_security_auditor.md`, `.claude/agents/`, and the other checklists contain no 2021-numbered references. CHANGELOG history entries describing past states stay untouched (immutable history).

## Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | **Re-section `references/checklists/owasp_top_10.md` to the 2025 final** | Yes | (a) ten sections renumbered/renamed per the verified table above, source line updated (no false "Q4 2025" claim; cite owasp.org/Top10/2025, verified 2026-06-10); (b) content moves: old-A10 SSRF checks → A01; old-A05 → A02; old-A02 → A04; old-A03 → A05; old-A04 → A06; old-A06 + supply-chain items of old-A08 (CI/CD tampering, code signing, unsigned updates, `npm audit` class) → **A03 Software Supply Chain Failures**; deserialization + integrity verification stay in A08; (c) **new A10 section** (Mishandling of Exceptional Conditions): fail-closed on error, no stack-trace leakage (CWE-209 — moves here from old-A05), unhandled-exception paths (CWE-754/390), resource cleanup on error paths, fail-open security controls (CWE-636); (d) per-section CWE header lines stay consistent with the moved content (A01 gains CWE-918) |
| R2 | **`security-audit/SKILL.md` re-tag + version bump** | Yes | (a) §2 scope list: Secrets `A02`→`A04`, Dependencies `A06/A08`→`A03` (supply chain), Code Patterns/Injection `A03`→`A05`, Config/Misconfiguration `A05`→`A02`; (b) §3 Web/API Top Checks: "Injection (A03)"→"(A05)"; "SSRF (A10)" → folded into A01 check; freed slot → "Supply Chain (A03)" check; add "(A10) Mishandling of Exceptional Conditions" check; (c) version 3.4 → 3.5 (frontmatter + H1 header + any synced version strings in `run_audit.py` / `audit/__init__.py`) |
| R3 | **`scripts/audit/scanners.py` docstring re-tag** (comment-only, zero behavior change) | Yes | 4 docstrings: supply chain `A06/A08`→`A03:2025`; secrets `A02`→`A04:2025`; dangerous patterns `A03`→`A05:2025`; configuration `A05`→`A02:2025` |
| R4 | **No stale 2021-numbered references** (acceptance gate) | Yes | `grep -rn "A0[0-9]\|A10"` over `.agent/skills/security-audit/`, `System/Agents/`, `.claude/agents/` → every hit is 2025-correct (ASI hits and API Top 10:2023 `API1…` hits are out of scope and remain) |
| R5 | **Docs & registry sync** | Yes | (a) `System/Docs/SKILLS.md` security-audit row: v3.4→v3.5, mention 2025-final alignment; (b) CHANGELOG.md + CHANGELOG.ru.md entry; (c) `docs/verification_roadmap.md` item 4 → ✅ DONE with verification note |

## 2. Constraints & Out of Scope
- **No behavior change:** scanner logic, pattern lists, finding `category`/`cwe` fields, severities, and tests' assertions are untouched — this is a taxonomy/documentation re-map. If any test asserts an A-number string, the test updates with it (same commit).
- **Out of scope:** API Top 10:2023 and LLM Top 10 v2.0 checklists (audited Current); item 10's two-layer methodology; historical CHANGELOG entries.
- **Lockstep rule:** none of the edited lines exist in multiple synced copies (verified by grep) — no lockstep edits required beyond SKILL/registry version sync.

## 3. Acceptance Criteria (from roadmap item 4)
1. Checklist header ↔ taxonomy consistent (2025 label on 2025 layout, primary-source citation).
2. SKILL §3 and scanner A-number tags consistent with the checklist.
3. Stale-reference grep (R4) clean.
4. Skill quality gate: `validate_skill.py` 43/43 across `.agent/skills/*/`.
5. `python3 -m pytest` for the audit scripts green (proves zero behavior change).

## 4. Open Questions
None — taxonomy verified against primary source in-session; blast radius established by grep.
