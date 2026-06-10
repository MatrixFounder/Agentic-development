# OWASP Top 10 for Agentic Applications 2026 + MCP — Security Checklist

> **Sources:** OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10, genai.owasp.org, 2025-12-09) ·
> NSA AISC CSI "MCP: Security Design Considerations for AI-Driven Automation" (U/OO/6030316-26, May 2026) ·
> MCP Security Best Practices (modelcontextprotocol.io). Verified against primary sources: 2026-06-10.
> **Scope:** Any project that ships or consumes AI agents, LLM tool-calling, or MCP servers/clients/configs.
> **Automation:** `run_audit.py --scan-type mcp` covers the regex floor (see "Scanner floor" below). Everything else here is manual/LLM review.

## ASI01: Agent Goal Hijack
- [ ] **Instruction/Data Separation:** Can untrusted content (web pages, RAG docs, tool outputs, emails) reach the agent as instructions rather than data?
- [ ] **Tool Poisoning:** Are tool *descriptions* free of hidden instructions? (Poisoned descriptions steer the agent before any user input — including `<IMPORTANT>`-style markers.)
- [ ] **Goal Integrity:** Is the agent's objective restated/validated server-side, not derived solely from accumulated context?
- [ ] **Output-to-Action Gate:** Are agent-proposed actions validated against the original goal before execution?

## ASI02: Tool Misuse & Exploitation
- [ ] **Tool Shadowing:** Can a malicious server register a tool whose name/description shadows a trusted tool and intercept its calls?
- [ ] **Full-Schema Poisoning:** Are *all* tool-schema fields (names, parameter names, types, defaults, error strings) treated as untrusted input — not just descriptions?
- [ ] **Argument Injection:** Are tool arguments validated/typed server-side (no shell/SQL/path pass-through of agent-supplied strings)?
- [ ] **Allowlist:** Are callable tools restricted to a reviewed allowlist per agent role?

## ASI03: Identity & Privilege Abuse
- [ ] **Confused Deputy:** Can a low-privilege caller route requests through the agent/MCP server to reach high-privilege resources? (Per-request authorization, not per-session.)
- [ ] **Token Passthrough:** Does the MCP server mint/scope its own credentials instead of passing the client's tokens through to upstream APIs?
- [ ] **Least-Privilege Tokens (NSA CSI):** One narrowly-scoped token per tool/action; no broad PATs in agent reach.
- [ ] **Auto-Approve:** Are auto-approve / always-allow settings (`chat.tools.autoApprove`, `alwaysAllow`, permission-bypass flags) disabled for destructive or external-effect tools?

## ASI04: Agentic Supply Chain Vulnerabilities
- [ ] **Server Provenance:** Is every MCP server installed from a verified publisher (registry trust, signatures) — not a lookalike/slopsquatted package?
- [ ] **Version Pinning:** Are servers version-pinned with lockfile/hash (no `npx -y pkg` / `pkg@latest` runtime fetches)?
- [ ] **Rug Pull:** Can a server mutate its tool definitions *after* user approval? (Pin definition hashes; re-prompt on change — postmark-mcp class.)
- [ ] **Dependency Scanning:** Are agent frameworks, MCP SDKs, and skills covered by dependency/CVE scans (e.g., `snyk-agent-scan`)?

## ASI05: Unexpected Code Execution (RCE)
- [ ] **Sandboxing (NSA CSI):** Do MCP servers and agent-generated code run sandboxed (container/VM, no host FS/network beyond need)?
- [ ] **Shell Surface:** Do any tool/server `command` entries spawn shells (`bash -c`, `cmd /c`) or interpreters with agent-controlled strings?
- [ ] **Eval Paths:** Is agent/LLM output ever passed to `eval`/`exec`/template engines without sandboxing?
- [ ] **STDIO Trust:** Are local STDIO servers treated as code execution on the host (MCP-STDIO 11-CVE cluster, Apr 2026)?

## ASI06: Memory & Context Poisoning
- [ ] **Memory Writes:** Is content written to persistent memory/RAG validated and attributed (source labels) before storage?
- [ ] **Context Persistence:** Can injected instructions survive across turns/sessions via memory, summaries, or scratchpads?
- [ ] **Context Labeling (NSA CSI):** Are context segments labeled by origin/trust level so downstream steps can filter?
- [ ] **Poisoned Retrieval:** Can an attacker seed documents that reliably surface into agent context (relevance attacks)?

## ASI07: Insecure Inter-Agent Communication
- [ ] **Transport:** Are remote MCP/agent links TLS-only (no plain `http://` URLs in configs) with token audience binding?
- [ ] **Session Hijacking:** Are MCP session IDs non-guessable, rotated, and bound to the authenticated principal (per modelcontextprotocol.io best practices)?
- [ ] **Message Trust:** Do agents validate/schema-check messages from other agents instead of executing them as instructions?
- [ ] **Cryptographic Isolation (NSA CSI):** Are channels between trust domains mutually authenticated and isolated?

## ASI08: Cascading Failures
- [ ] **Blast Radius:** Is the worst-case chain (agent → tool → agent → tool…) bounded by depth/cost/permission budgets?
- [ ] **Circuit Breakers:** Do failures/anomalies in one tool or agent halt the chain instead of propagating bad state?
- [ ] **Loop Guards:** Are recursive agent↔tool invocation loops detected and capped?

## ASI09: Human-Agent Trust Exploitation
- [ ] **Overwhelm/Approval Fatigue:** Can the agent flood the human with prompts until they rubber-stamp? (Batch + summarize approvals; never default-allow.)
- [ ] **Deceptive Output:** Are agent claims about performed actions verifiable against audit logs (not self-reported only)?
- [ ] **Provenance Display:** Does the UI show which server/tool produced content the user is about to trust?

## ASI10: Rogue Agents
- [ ] **Registration & Identity:** Is every running agent registered, identified, and attributable (no orphaned/forgotten agents with live credentials)?
- [ ] **Kill Switch:** Can any agent be revoked/terminated centrally (tokens + runtime)?
- [ ] **Behavioral Monitoring:** Are agent action patterns monitored for drift from declared purpose?

## NSA CSI Operational Controls (MCP deployments)
- [ ] **Outgoing Filtering Proxy / DLP:** External MCP connections pass through a filtering proxy or enterprise DLP; resource URLs and access methods pinned.
- [ ] **Audit Logging:** Every tool call (caller, args digest, result status) logged tamper-evidently.
- [ ] **Signed Provenance for Dynamic Discovery:** Dynamically discovered servers/tools require signed provenance; otherwise discovery is disabled.
- [ ] **Registry Hardening:** Internal MCP registries treated as API gateways — authn, rate limits, review-before-publish.
- [ ] **Local MCP Scans:** `snyk-agent-scan` (ex-Invariant `mcp-scan`) run against local MCP configs/skills in CI or pre-install.

## Incident Calibration (why these checks exist)
- **CVE-2025-6514** (mcp-remote, CVSS 9.6 — RCE via malicious server URL) · **CVE-2025-49596** (MCP Inspector, 9.4 — browser-reachable RCE).
- **MCP-STDIO design flaw** → 11-CVE cluster (Apr 2026): local servers = host code execution.
- **postmark-mcp** (Sep 2025): first in-the-wild malicious MCP server — benign for 15 versions, then BCC-exfiltrated mail (rug pull).
- **s1ngularity** (Aug 2025): malware weaponizing installed AI CLIs for recon · **Shai-Hulud** (CISA alert): self-replicating npm worm hitting agent toolchains via unpinned installs.

## Scanner floor vs. LLM review (honest limitation)
- **Regex floor (`--scan-type mcp` automates):** MCP config presence/provenance prompts; auto-approve keys; permission-bypass flags; unpinned `npx -y`/`uvx`/`@latest`; `mcp-remote` usage; cleartext `http://` URLs; inline secrets in `env` blocks; shell-spawning `command` values; crude imperative-language and `<IMPORTANT>` markers in tool definitions.
- **LLM/manual only:** *semantic* tool-description poisoning (benign-sounding steering), rug-pull dynamics (requires definition-hash history), toxic flow composition across tools, confused-deputy authorization logic. A clean regex scan is **not** clearance for these classes.
