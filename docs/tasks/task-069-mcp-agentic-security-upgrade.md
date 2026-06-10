# Technical Specification: Agentic/MCP Security Upgrade (C-11 / C-14)

### 0. Meta Information
- **Task ID:** 069
- **Slug:** `mcp-agentic-security-upgrade`
- **Mode:** Framework Upgrade (meta-operation — modifies the security-audit skill, its scanner scripts, and a System/Agents prompt)
- **Type:** P1 modernization, roadmap item 3 (highest real-world risk). Closes audit-067 claims C-11 (zero MCP/agentic detection coverage) and C-14 (Security Auditor role has no agentic threat model).
- **Workflow:** `/framework-upgrade` (with `skill-self-improvement-verificator` gate, Modes A + B).
- **Source:** User request (2026-06-10): "выполни 3. 🔜 [C-11, C-14] Agentic/MCP security upgrade" + `docs/verification_roadmap.md` item 3 + `docs/reviews/verification-stack-currency-audit-067.md` (claims register C-11, C-14; bibliography).

## 1. General Description

Audit 067 graded the framework's agentic/MCP security coverage **Outdated**: the entire topic is covered by one-liners in `llm_security.md:35,70–75`, `patterns.py` has **zero** MCP/agentic detection patterns, and `10_security_auditor.md` has no agentic threat model — while the framework's own domain **is** agentic development. Since those checklists were written the external bar moved:

- **OWASP Top 10 for Agentic Applications 2026** (ASI01–ASI10, released 2025-12-09) — verified 2026-06-10 against genai.owasp.org + 5 independent secondary sources. Categories: ASI01 Agent Goal Hijack · ASI02 Tool Misuse & Exploitation · ASI03 Identity & Privilege Abuse · ASI04 Agentic Supply Chain Vulnerabilities · ASI05 Unexpected Code Execution (RCE) · ASI06 Memory & Context Poisoning · ASI07 Insecure Inter-Agent Communication · ASI08 Cascading Failures · ASI09 Human-Agent Trust Exploitation · ASI10 Rogue Agents.
- **NSA AISC CSI "Model Context Protocol: Security Design Considerations for AI-Driven Automation"** (U/OO/6030316-26, 2026-05-20, v1.0) — verified 2026-06-10 via nsa.gov press release + PDF listing. Controls: least-privilege tokens per tool/action, context labeling, cryptographic isolation, audit logging, filtering outgoing proxy / enterprise DLP for external MCP connections, signed provenance for dynamic discovery, registry hardening + rate limits, sandboxing.
- **Real-world incidents:** CVE-2025-6514 (mcp-remote, CVSS 9.6), CVE-2025-49596 (MCP Inspector, 9.4), MCP-STDIO design flaw → 11-CVE cluster (Apr 2026), postmark-mcp rug pull (first in-the-wild malicious MCP server, Sep 2025), s1ngularity (AI-CLI-weaponizing malware), Shai-Hulud npm worm (CISA alert).
- **Shipping scanners:** Invariant `mcp-scan` → **Snyk `agent-scan`** (`snyk-agent-scan` CLI, github.com/snyk/agent-scan — verified 2026-06-10; detects tool poisoning, tool shadowing, toxic flows; consent-gated server startup).

This task adds a dedicated MCP/agentic checklist (1:1 ASI mapping + NSA CSI controls + concrete attack patterns), a regex-detectable floor in the scanner (new `mcp` scan type, ≥8 patterns with CWE/ASI mapping), external-tool roster entries (`snyk-agent-scan`/`mcp-scan`), and an Agentic Threat Model subsection in the Security Auditor role prompt.

## Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
|----|-------------|------|--------------|
| R1 | **[C-11] New checklist** `.agent/skills/security-audit/references/checklists/mcp_agentic_security.md` (~80–100 lines) | Yes | (a) ten sections mapped **1:1** to ASI01–ASI10 (verified names above), each with concrete checkbox items; (b) NSA CSI controls section (least-privilege tokens, context labeling, isolation, audit logging, outgoing filtering proxy/DLP, signed provenance, registry hardening, sandboxing, local MCP scans); (c) concrete attack patterns named and checkable: tool poisoning (hidden instructions in tool descriptions), rug pull (post-approval definition mutation), tool shadowing, full-schema poisoning, confused deputy, token passthrough, session hijacking (per modelcontextprotocol.io Security Best Practices); (d) incident/CVE calibration block (CVE-2025-6514, CVE-2025-49596, MCP-STDIO cluster, postmark-mcp, s1ngularity, Shai-Hulud) |
| R2 | **[C-11] Regex floor** in `scripts/audit/patterns.py` + new scanner | Yes | (a) new `MCP_AGENTIC_PATTERNS` list, **≥8 patterns**, each tagged with a real CWE **and** an ASI ID (ASI ID carried in the `category` field, e.g. `"Tool Poisoning (ASI01/ASI06)"`); minimum set: auto-approve flags (`chat.tools.autoApprove`, `"autoApprove": [...]`, `"alwaysAllow": [...]`), permission-bypass flags (`--dangerously-skip-permissions`-style), unpinned `npx -y`/`uvx` server commands (incl. `@latest`), `mcp-remote` usage, plain-`http://` MCP server URLs, inline secrets in MCP `env` blocks, shell-spawning `command` values, imperative-language heuristic in tool-description strings (incl. `<IMPORTANT>`-marker PoC pattern); (b) new `scan_mcp_agentic()` in `scanners.py`: targets well-known MCP config artifacts by filename (`mcp.json`, `.mcp.json`, `claude_desktop_config.json`) during the walk **plus explicit probes** for configs inside pruned dirs (`.vscode/mcp.json`, `.cursor/mcp.json` — `.vscode` is in `SKIP_DIRS`); emits a low-severity provenance finding for every MCP config found (presence ⇒ review provenance); applies the tool-description heuristic to agent/tool definition files; (c) registered in `run_audit.py` as `--scan-type mcp`, included in `--scan-type all`; exported from `audit/__init__.py`; (d) `detect_project_types()` gains `"mcp"` type (same artifact set) |
| R3 | **[C-11] External tool roster** `scripts/audit/external.py` | Yes | (a) when `"mcp"` in detected types: run `snyk-agent-scan` with fallback to legacy `mcp-scan`; (b) **never** pass `--dangerously-run-mcp-servers` (no consent-bypassing server startup from an audit script) — comment in code; (c) SKILL §2 external-tools line updated to mention them with the MCP-artifact trigger |
| R4 | **[C-11] SKILL.md integration** (`security-audit/SKILL.md`) | Yes | (a) §2 scope list gains the MCP/Agentic line + usage string gains `mcp` scan type; (b) §3 gains subsection "Agentic / MCP (OWASP ASI Top 10 2026)" with **MANDATORY** read of the new checklist + Top Checks (goal hijack, tool poisoning/rug pull, least-privilege/auto-approve, supply-chain pinning); (c) **honest limitation note**: semantic tool-description poisoning requires LLM review — regex is only the deterministic floor (full two-layer methodology is roadmap item 10, out of scope here); (d) version bump 3.3 → 3.4 (frontmatter + header + run_audit docstring + `__init__.__version__` stay in sync); (e) frontmatter `description:` gains MCP/agentic in its scope list (triggering accuracy) |
| R5 | **[C-14] Security Auditor prompt** `System/Agents/10_security_auditor.md` | Yes | (a) new "Agentic Threat Model" subsection in §4 execution loop: can the agent be goal-hijacked (ASI01)? can tool calls be tampered/poisoned (ASI02)? are agent identities/privileges scoped (ASI03)? is memory/context poisonable (ASI06)? are inter-agent messages trusted blindly (ASI07)? are MCP servers provenance-verified and pinned (ASI04)?; (b) §2 TIER 1 loading references the new checklist for agentic/MCP targets; (c) prompt version header bump v3.6.0 → v3.7.0; (d) prompt explicitly mentions ASI/MCP (acceptance criterion from roadmap) |
| R6 | **Tests** `tests/test_smoke.py` | Yes | (a) new test class/section for `scan_mcp_agentic`: ≥8 assertions covering — autoApprove flagged; permission-bypass flag flagged; unpinned `npx -y` flagged; version-pinned `npx -y pkg@1.2.3` NOT flagged; `.vscode/mcp.json` found despite SKIP_DIRS prune; provenance finding emitted for `mcp.json`; plain-http URL flagged; inline env secret flagged; shell `command` flagged; tool-description imperative heuristic flagged; clean project → zero MCP findings; (b) existing self-exclusion regression must stay green |
| R7 | **Verification gate & docs** | Yes | (a) `python3 -m pytest .agent/skills/security-audit/tests/` green; (b) `run_audit.py` on this repo runs green (exit 0, no critical/high MCP findings); (c) `validate_skill.py` green for `security-audit` (and baseline 43/43 across `.agent/skills/*/` unchanged); (d) wrapper-drift grep: no stale references to removed/renamed content in `.claude/agents/`, `.agent/`; (e) CHANGELOG entry EN + RU (v3.20.0) tracing to C-11/C-14; (f) `docs/verification_roadmap.md` item 3 flipped to ✅ DONE with commit ref; (g) backups of every edited file in `.agent/archive/` before edits; (h) session state persisted at phase boundaries; (i) registry refresh: `System/Docs/SKILLS.md:87` security-audit line is **stale-specific** (says "v3.2", "121 automated regex patterns") — update version, pattern count, and add MCP/agentic to the capability list |

## 2. Use Cases

### 2.1 UC-1: Auditor scans a project that ships MCP servers/configs (main)
**Actors:** Security Auditor agent (or developer running the script).
**Preconditions:** Target project contains `mcp.json` / `.mcp.json` / `claude_desktop_config.json` / `.vscode/mcp.json` / `.cursor/mcp.json`, or agent/tool definition files.
**Main scenario:**
1. Agent runs `run_audit.py <path>` (or `--scan-type mcp`).
2. Scanner emits provenance findings for each MCP config + pattern findings (auto-approve, unpinned servers, http URLs, inline secrets, poisoning heuristics), each with CWE + ASI tags.
3. `detect_project_types` includes `mcp` → external phase attempts `snyk-agent-scan` (fallback `mcp-scan`); missing tools are non-fatal.
4. Auditor reads `mcp_agentic_security.md` and manually verifies the semantic classes regex cannot catch (tool-description poisoning, rug-pull dynamics), guided by the Agentic Threat Model subsection of the role prompt.
**Acceptance criteria:**
- ✅ Each MCP config artifact produces at least a provenance finding (including `.vscode/mcp.json` despite dir pruning).
- ✅ All findings carry a real CWE and an ASI ID in `category`.
- ✅ External MCP scanners attempted only when MCP artifacts detected; never auto-start servers.

### 2.2 UC-2: Auditor scans a project with no MCP/agentic surface (regression)
**Main scenario:** `run_audit.py` on a project with no MCP artifacts (e.g., this repo).
**Acceptance criteria:**
- ✅ `mcp` scan reports zero findings, status `[OK]`; overall exit code 0; no external MCP scanner invoked (no `mcp` type detected).
- ✅ All pre-existing scans behave exactly as before (no regression in deps/secrets/patterns/config/iac/sbom).

### 2.3 UC-3: Security Auditor role audits an agentic feature (C-14)
**Main scenario:** Orchestrator dispatches `10_security_auditor.md`; auditor loads TIER 1 skills, reaches Agentic Threat Model step, answers the ASI-mapped questions, reads the checklist for any MCP/agent surface in scope.
**Acceptance criteria:**
- ✅ Prompt contains the agentic threat-model questions with ASI references and points to `mcp_agentic_security.md`.

## 3. Non-functional Requirements
- **Minimal-diff invariant:** no edits outside — new checklist file, `patterns.py`, `scanners.py`, `helpers.py` (`detect_project_types`), `external.py`, `run_audit.py`, `audit/__init__.py`, `tests/test_smoke.py`, `security-audit/SKILL.md`, `System/Agents/10_security_auditor.md`, CHANGELOGs, roadmap, session/archive bookkeeping.
- **No scope creep:** roadmap item 4 (OWASP 2025 remap — `owasp_top_10.md` untouched), item 10 (two-layer methodology — only the one-line limitation note ships now), item 11 (orchestrator-supplies-evidence) stay separate cycles.
- **Scanner philosophy preserved:** regex-only line-level floor, ReDoS guard honored (line-local patterns; multi-line only with the IaC-style whole-file guard), self-exclusion intact, missing external tools non-fatal.
- **Severity discipline:** provenance/presence = low; heuristics (tool-description language) = medium (FP-tolerant by design, manual verify); auto-approve / unpinned / cleartext / inline secrets / shell commands = high; nothing critical by default (regex cannot prove exploitability of a config — avoids false CI blocks via `--fail-on critical`).
- **Rollback:** backups in `.agent/archive/`; restore per workflow §5 Fallback.

## 4. Constraints & Assumptions
- ASI01–ASI10 names and NSA CSI control list were **web-verified 2026-06-10** (genai.owasp.org announcement 2025-12-09; nsa.gov CSI U/OO/6030316-26; snyk/agent-scan GitHub). The audit-067 bibliography is the in-repo citation anchor.
- `snyk-agent-scan` availability on operator machines is not assumed — `run_command` already degrades gracefully (`[!] Tool not found`).
- The checklist is a reference document (not a skill) — `init_skill.py` gate does **not** apply; it follows the existing `references/checklists/*.md` format.
- Baseline before edits: skill gate 43/43; `run_audit.py` exit 0 on this repo.

## 5. Open Questions
- None. Scope, file set, and acceptance criteria are fixed by roadmap item 3; all external facts verified this session.
