---
name: security-audit
description: Use when performing security vulnerability assessment (OWASP, secrets, dependencies, IaC, LLM, API, MCP/agentic) or when "thinking like a hacker" to find exploits.
tier: 2
version: 3.12
---

# Security Audit v3.12

## 0. Methodology — Two Layers (audit-067 C-10)

This skill runs **two complementary layers**; neither substitutes for the other:

1. **Deterministic floor (§2)** — regex patterns + external scanners. Reproducible, cheap, CI-gateable (`--fail-on`), zero judgment. It is a *floor*, not the audit: a clean scan is **not** clearance, because regex is categorically blind to semantic classes — business-logic authz, cross-file taint flows, semantic MCP tool-description poisoning (§3 Agentic limitation note).
2. **LLM semantic pass (§3–§4)** — long-context taint/logic review against the checklists plus threat modeling: the layer that catches what regex cannot. Frontier evidence that LLM-driven semantic review finds real vulnerabilities beyond pattern matching: DARPA AIxCC finals (2025), Google Big Sleep, Codex Security / Claude Code Security review agents (full citations: audit-067 §Bibliography).

> **Licensing footnote (semgrep):** the open-source offering is **Semgrep CE** since the Dec 2024 licensing change; **Opengrep** (community fork, Jan 2025) is a drop-in alternative where CE constraints matter. The external-tool roster treats either as the same scanner slot.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll skip the script because I just checked the code manually" -> **WRONG**. Humans miss regex patterns. **EXECUTE** the script.
- "I have no way to run it, so I'll write down what it would have said" -> **WRONG, and the worst of them.** Inventing scanner output manufactures a passed gate nobody can see through. There is exactly ONE legitimate way not to execute — §2's `NOT RUN` branch — and it is legitimate precisely because it is *visible*.
- "This is an internal tool, so AuthZ doesn't matter" -> **WRONG**. Zero Trust applies everywhere.
- "Dependencies are probably fine" -> **WRONG**. Supply chain attacks are the #1 vector.
- "I don't have time for a full audit" -> **WRONG**. Breach cleanup takes 100x longer.
- "The LLM output is safe to use directly" -> **WRONG**. LLM output is untrusted input. Sanitize it.

## 2. Automated Detection

> **First, check whether you CAN execute.** Some roles that load this skill are declared without an
> execution tool at all (`critic-security` is `Read, Grep, Glob` — read-only by design, see
> `skill-parallel-orchestration` §2.4). If a scan result was supplied to you in an execution-evidence
> block, **ingest it and do not re-run**. If you have no execution tool and no supplied result,
> record the line `scan: NOT RUN (no execution tool in this role)` and go straight to §3's manual
> review. **Do not spend your turn attempting the command** — that is a measured failure mode, not a
> hypothetical: subagents have stalled for 600 s doing it. And never write down output you did not
> get: §1's "I have no way to run it" Red Flag. (Named, not numbered — this cross-reference said
> "third" and pointed at an unrelated bullet, because the new one was inserted second.)

**EXECUTE** the unified audit script to detect vulnerabilities:
```bash
python3 .agent/skills/security-audit/scripts/run_audit.py [project_path] \
  [--scan-type all|deps|secrets|patterns|config|iac|mcp|sbom|external] \
  [--fail-on critical|high|medium] [--output json|summary] \
  [--no-limit] [--max-size MB]
```
- **Analysis**: Review the output. If tools fail or report Critical/High issues, they are **BLOCKERS**.
- **Scope**: The script checks:
  - Secrets (OWASP A04:2025 Cryptographic Failures, CWE-798) — 30+ patterns including cloud, AI, SaaS keys + entropy detection
  - Dependencies / Supply Chain (OWASP A03:2025, CWE-1104) — real lock files only
    (Pipfile.lock/poetry.lock/uv.lock/pdm.lock for Python; package-lock/yarn.lock/pnpm-lock for JS;
    Cargo.lock; go.sum)
    - `npm audit --package-lock-only` runs once for every npm lockfile, below the root included, in
      a temporary copy of the lockfile and its `package.json`; SKIP_DIRS are skipped
    - a lockfile without its own `package.json` is not audited; npm would audit an ancestor's
      project
    - a finished audit yields one finding per npm severity with a non-zero count: `critical`,
      `high`, `moderate` as `medium`, `low` and `info`; a severity outside the five is a `low`
      finding "of unknown severity"
    - `npm_audit_counts` holds the six counts of each finished audit, also when every count is 0
    - an audit that does not finish is an `info` finding naming its lockfile, with
      `"audited": false`; the section status counts them, and each is a part not run (exit 3)
  - Code Patterns / Injection (OWASP A05:2025, CWE-79/89/78) — eval, XSS, SQLi, SSTI, SSRF, path traversal, prototype pollution, deserialization
  - **Smart Contract / Solidity** — reentrancy, delegatecall, selfdestruct (EIP-6780), tx.origin, oracle manipulation, unchecked returns, unprotected initializers
  - **Rust** — `unsafe{}`, `transmute`, `mem::forget`, `unwrap_unchecked`, weak RNG
  - **Go** — `math/rand` for security, SQL concat, missing TLS, command injection
  - **GraphQL** — introspection/playground enabled in prod, missing depth limits
  - Config / Misconfiguration (OWASP A02:2025, CWE-16) — debug mode, CORS, headers
  - IaC / Containers — Docker, Kubernetes, Terraform, CloudFormation patterns
  - **MCP / Agentic (OWASP ASI Top 10 2026)** — MCP config provenance (`mcp.json`, `.mcp.json`, `claude_desktop_config.json`, incl. `.vscode/`), auto-approve keys, permission-bypass flags, unpinned `npx -y`/`uvx` servers, `mcp-remote`, cleartext MCP URLs, inline env secrets, shell-spawning servers, tool-description poisoning heuristics — all findings CWE+ASI tagged
  - SBOM — recursive Software Bill of Materials presence check (honors SKIP_DIRS)
- **External Tools** (when `--scan-type all` or `--scan-type external`): one record per tool in the
  report's `external` section, also for a project with no detected type. MCP servers are never
  started: `snyk-agent-scan` runs with no auto-start flag (servers stay consent-gated). See
  **External layer** below.
- **`npm audit` (external)** runs in each npm lockfile directory, as the dependency scan does.
- **`yarn audit` (external)** runs in a temporary copy of the root `yarn.lock` and its
  `package.json`, so the project's `.yarnrc` and `.yarnrc.yml` take no part (TASK 112 R5.1).
- **`--scan-type external`** runs **ONLY** external tools and SKIPS the in-process regex scans. Use `--scan-type all` (default) to run both.
- **CI/CD Gate**: Use `--fail-on critical` to exit with code 1 in CI pipelines. See **Exit codes**
  below.
- **`--max-size MB`**: default 15 MB per file. Increase for large minified bundles (vendor.js/bundle.js can be 20+ MB).
- **ReDoS guard**: lines longer than 4000 chars are skipped during pattern scanning (prevents catastrophic backtracking on minified code).
- **Self-Exclusion**: The scanner skips its own source files to prevent false positives.
- **Files that are not regular**: the in-process scans read a file only when it is a regular file
  within the size limit, checked on the opened file. A FIFO, a device or a socket, or a link to
  one, is skipped and counted in `skipped_files`, and stderr names the reason; the scan does not
  wait on it. A link to a regular file inside the scanned root is read; a file whose real path
  leaves the root is skipped and counted, with the reason `outside the scanned root`.
- **CWE Mapping**: All findings include CWE identifiers for compliance integration.
- **Known Limitation**: The scanner uses **regex-only** (no AST parsing). It WILL match patterns inside comments, docstrings, and string literals. This is a deliberate trade-off: false positives on comments are preferable to false negatives on real vulnerabilities. Always **manually verify** findings before acting.

### External layer (TASK 118)

Each external tool fills a **slot**. A fallback tool fills the slot of the tool it replaces, and
starts only when the first tool is not installed or timed out. A slot is selected when it holds a
record.

| Slot | Tools, first to fallback | Selected for |
| :--- | :--- | :--- |
| `sast` | semgrep | every scan |
| `secrets-tree` | gitleaks, trufflehog | every scan |
| `secrets-history` | gitleaks | every scan |
| `solidity` | slither | type solidity |
| `python-sast` | bandit | type python |
| `python-deps` | pip-audit | type python |
| `npm-audit:<lockfile>` | npm | each npm lockfile |
| `yarn-audit` | yarn | type javascript, with a root `yarn.lock` |
| `rust-deps`, `rust-lint` | cargo audit, cargo clippy | type rust |
| `go-deps`, `go-sast` | govulncheck, gosec | type go |
| `iac`, `iac-misconfig` | checkov, trivy | type iac |
| `mcp` | snyk-agent-scan, mcp-scan | type mcp |

- **Record.** Each record holds `slot`, `tool`, `command`, `where`, `status`, `exit_code` and
  `reason`. `status` is `ran` (with the exit code), `killed` (a signal ended it; a negative exit
  code), `not_installed`, `timed_out` (600 s), `not_run` (the scanner declined, with a reason) or
  `not_applicable` (no input, with a reason). A `killed` record does not complete its slot.
- **Lockfiles.** A lockfile or `package.json` whose copy fails, such as a FIFO, is not audited:
  reason `the lockfile could not be copied`.
- **Section status.** `NOT_RUN` when no tool ran; `COMPLETE` when every selected slot has a `ran`
  or `not_applicable` record; `PARTIAL` otherwise.
- **Secrets.** `secrets-tree` runs `gitleaks detect --no-git`, which reads the files of the working
  tree, uncommitted and ignored ones included; its fallback is `trufflehog filesystem --fail`.
  `secrets-history` runs gitleaks in git mode when the scanned root, or a parent of its real path,
  holds a `.git` directory or file or is a bare repository. A `.git` link, a special file, an
  unreadable `.git` or a bare repository that holds a link is `not_run`; no repository on the path
  is `not_applicable`.
- **Git mode runs git in the scanned tree's repository.** git reads that repository's
  configuration, and the configuration can name commands that git runs. Scan the history of an
  untrusted tree only in an isolated environment, such as a container that holds no credentials
  (WI-49).
- **No `trufflehog git`.** No slot runs trufflehog's `git` mode: CVE-2025-41390 (Talos
  TALOS-2025-2243) executed the `core.fsmonitor` command of a scanned repository's `.git/config`.
  trufflehog runs in `filesystem` mode only. The bullet above still applies to gitleaks.
- **Tools that run project code.** `cargo clippy` builds the crate and runs its `build.rs`;
  `slither` compiles through the project's build framework; `checkov` reads the project's
  configuration and can load checks from it (WI-37, dropped).
- **Configuration in the scanned tree.** A tool can read configuration files that the tree holds,
  such as `.gitleaks.toml`, `.gitleaksignore`, `.semgrepignore` and `.trivyignore`. Such a file can
  silence the tool, which then exits 0 (WI-50).
- **Text from the tree.** In the scanner's own lines, paths and messages from the scanned tree are
  printed with each control, format, line-separator or paragraph-separator character escaped as
  `\xNN`, `\uNNNN` or `\UNNNNNNNN`, and a backslash is doubled; the JSON keeps the escaping of
  `json.dumps`. The external tools' own output reaches stderr as they print it, unescaped.
- **`mcp-scan` fallback.** It runs with no argument. Whether it then scans the scanned tree or the
  operator's own MCP configuration is not verified.
- **Exit on a finding.** trufflehog runs with `--fail` and trivy with `--exit-code 1`, so a finding
  exits non-zero. Under `--fail-on`, npm runs with `--audit-level` at the threshold (`medium` as
  `moderate`). yarn's exit is not ranked: any advisory exits non-zero.
- **Output.** A tool's stdout and stderr go to the scanner's stderr, so `--output json` prints one
  JSON document on stdout.

**Toolset of a complete local run.** A run is complete when each selected slot has one installed
tool that finishes within 600 s; a `not_applicable` slot needs none. Every scan selects `sast`,
`secrets-tree` and `secrets-history`; a Python project also selects `python-sast` and
`python-deps`. With Homebrew:

```bash
brew install semgrep gitleaks trufflehog bandit pip-audit
```

The Python tools also install with `pipx install semgrep`, `pipx install bandit` and
`pipx install pip-audit`. No CI job of this repository runs the external layer; a missing tool
leaves the scan incomplete.

### Exit codes and summary (TASK 118)

| Exit | Condition |
| :--- | :--- |
| 0 | every requested part ran, and no `--fail-on` cause |
| 1 | `--fail-on` given, and a finding at the threshold or above, or a non-empty `summary.tool_exits` |
| 3 | no `--fail-on` cause, and a requested part did not run (`summary.scan_complete` is `false`) |
| 1 | a JSON `error` and no report: a missing directory or a non-positive `--max-size` |
| 2 | a usage error, from argparse |

- `summary` holds `total_findings`, `critical`, `high`, `medium`, `low`, `info`, `not_run`,
  `scan_complete`, `tool_exits` and `overall_status` for every scan type, counted before each
  section is cut to 30 findings.
- `summary.not_run` names each part that did not run: `external <slot>: <tool> <status>`, or
  `dependencies: <message>` for an unaudited lockfile. A non-empty list prints `[INCOMPLETE]` and
  the list on stderr, on exit 3 and beside `[GATE]` on exit 1.
- `summary.tool_exits` names each tool that ran and exited non-zero: `<tool> exited <N> (<slot>)`.
  The exit is a finding or an error; the tool's output says which. Exit 1 prints `[GATE]` and its
  causes on stderr.
- `overall_status` is never `[OK] SECURE` while a part did not run or a tool exited non-zero. A
  critical or high finding still ranks first (§6.2: `FAIL` before `INCOMPLETE`).
- A scan with exit 3, or a non-empty `summary.not_run`, is `scan_status: NOT_RUN` for an auditor;
  a non-empty `summary.tool_exits` is at least `scan_status: findings`, and `NOT_RUN` when the
  tool's output shows an error. A run that prints no report, such as exit 1 with a JSON `error` or
  exit 2, is `NOT_RUN`.

## 3. "Think Like a Hacker" (Adversarial Review)

**Refuse to merge/approve until you have manually verified the code against the relevant checklist.**

### Smart Contracts (Solidity)
**MANDATORY:** Read `references/checklists/solidity_security.md`.
**Top Checks:**
1. **Reentrancy**: Are checks-effects-interactions followed? `nonReentrant` used?
2. **Access Control**: Who owns the contract? `onlyOwner` checks? Two-step transfer?
3. **Price Manipulation**: Are spot prices used? (Use Oracles + TWAP).
4. **EIP-6780**: `selfdestruct` semantics changed post-Dencun — accounted for?
5. **ERC-4337**: Account Abstraction validation and paymaster checks.
6. **Fuzzing**: See `references/checklists/fuzzing_invariants.md`.

### Smart Contracts (Solana/Rust)
**MANDATORY:** Read `references/checklists/solana_security.md`.
**Top Checks:**
1. **Account Validation**: Are ALL accounts checked for ownership and signer status?
2. **PDA bumps**: Are bumps strictly validated (canonical bump)?
3. **Arithmetic**: Is `overflow_checks` on? Using `checked_*` methods?
4. **Token-2022**: Are transfer hooks, fees, and extensions handled correctly?
5. **CPI Guard**: Is CPI Guard used where appropriate?

### Web/API (OWASP Top 10:2025)
**MANDATORY:** Read `references/checklists/owasp_top_10.md` (2025 final taxonomy — A-numbers changed vs 2021; mapping table at file end).
**Top Checks:**
1. **Broken Access Control (A01)**: Can user A access user B's data? (IDOR; SSRF — absorbed into A01 in 2025: validate user-supplied URLs against an allowlist).
2. **Software Supply Chain (A03)**: Lock files committed? Versions pinned? SCA + dependency audit clean?
3. **Injection (A05)**: Are queries parameterized? Is output escaped?
4. **Exceptional Conditions (A10)**: Do security controls fail closed? No stack traces to users?

### API Security (OWASP API Top 10:2023)
**MANDATORY:** Read `references/checklists/api_security.md`.
**Top Checks:**
1. **BOLA (API1)**: Object-level authorization on every endpoint?
2. **BOPLA (API3)**: Mass assignment prevention? Excessive data exposure?
3. **Rate Limiting (API4)**: Per-user, per-endpoint rate limits?

### AI/LLM Applications (OWASP LLM Top 10 v2.0)
**MANDATORY:** Read `references/checklists/llm_security.md`.
**Top Checks:**
1. **Prompt Injection (LLM01)**: Can user input override system prompts?
2. **Insecure Output Handling (LLM02)**: Is LLM output sanitized before use in HTML/SQL/shell?
3. **Excessive Agency (LLM06)**: Does the agent have minimal permissions? Human-in-the-loop for destructive actions?
4. **Supply Chain (LLM05)**: Are models from trusted sources? Plugins verified?

### Agentic / MCP (OWASP ASI Top 10 2026 + NSA MCP CSI)
**MANDATORY:** Read `references/checklists/mcp_agentic_security.md`.
**Top Checks:**
1. **Goal Hijack (ASI01)**: Can untrusted content (tool outputs, RAG docs, web pages) reach the agent as instructions?
2. **Tool Poisoning / Rug Pull (ASI01/ASI04)**: Are tool descriptions clean of steering language? Are definitions pinned + provenance-verified (post-approval mutation = rug pull)?
3. **Excessive Agency (ASI03)**: Auto-approve disabled for destructive tools? Least-privilege token per tool/action? No confused-deputy / token passthrough?
4. **Supply Chain (ASI04)**: Every MCP server version-pinned (no `npx -y pkg` / `@latest`), from a trusted registry?
> **Limitation (honest floor):** the regex layer (`--scan-type mcp`) only catches crude markers. **Semantic** tool-description poisoning, rug-pull dynamics, and toxic flow composition require LLM/manual review — a clean scan is not clearance for those classes.

## 4. Threat Modeling
Before declaring "Secure", perform lightweight threat modeling:
**MANDATORY:** Read `references/checklists/threat_model.md`.
1. **STRIDE Analysis**: Evaluate each component for Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege.
2. **DREAD Scoring**: Rate each threat by Damage, Reproducibility, Exploitability, Affected Users, Discoverability.
3. **Attack Surface Mapping**:
   - **Entry Points**: APIs, forms, file uploads, webhooks, LLM interfaces.
   - **Data Flows**: Where does user input go? (Logs? DB? Shell? LLM prompt?).
   - **Assets**: Secrets, PII, Money, Model weights.
   - **Trust Boundaries**: Internet <-> DMZ <-> Internal <-> AI/Agent scope.

## 5. Secret Remediation
When secrets are found:
**MANDATORY:** Read `references/checklists/secret_rotation.md`.
1. **Rotate immediately** — the secret is compromised.
2. **Clean git history** — BFG or git-filter-repo.
3. **Prevent recurrence** — pre-commit hooks (gitleaks/trufflehog).

## 6. Reporting
- **Critical**: Immediate Blocker (RCE, Auth Bypass, Secrets Exposed, Prompt Injection). **Fix immediately**.
- **High**: Must fix before release (XSS, CSRF, Dep Vulns, SSRF, Mass Assignment).
- **Medium**: Document in Backlog (Missing headers, weak crypto, best practices).

All findings include **CWE identifiers** for integration with vulnerability management systems (Jira, Snyk, Sonar).

### 6.1 A finding in a dependency

A **dependency finding** is a vulnerability that no public advisory describes yet, in code the
project uses but does not maintain: a library, a CLI tool, a pinned binary. It affects every user
of that dependency, so its maintainers learn of it before the public does. A vulnerability with a
public advisory is cited by its advisory identifier (CVE or GHSA).

Until a public advisory describes it:

1. **Report it privately.** The dependency's security policy (`SECURITY.md`) names the channel; on
   GitHub it is the repository's Security tab, *Report a vulnerability*. A public issue, pull
   request or discussion is a disclosure. With no private channel, the operator asks the
   maintainers for one and gives no detail.
2. **Keep the detail out of everything published with the repository**: files, commit messages,
   branch and tag names, pull request and release text, and the records that tools write
   (ledgers, eval corpora, session summaries). A record states only the dependency, the affected
   versions, a severity, this project's mitigation and the status of the report; nothing on how
   the defect works or what reaches it. Anyone who reads the repository reads the detail, and it
   is a working attack on every user of the dependency.
3. **Hand the report to the operator.** The draft is written outside the repository, and the
   operator sends it. An agent posts to an external service only when the operator asks for it in
   their own message.
4. **Record the status.** The channel, the date the report was sent and, where one exists, the URL
   of the private report are recorded at once: they show nothing to anyone else. With no channel, or no answer 90 days after the send,
   the operator decides in their own message what follows, and the record states the decision.
5. **After the advisory**, a record cites it and restates nothing beyond it. An operator's
   recorded decision to disclose without one lifts step 2 as far as the decision states.

Five other duties of an audit give way while the rule holds:

- a test pins this project's mitigation and never exercises the dependency's defect;
- a patch to a vendored copy waits for the advisory, because its diff shows the defect;
  isolation or configuration mitigates better than a narrow guard in the project's code, which
  shows it too;
- the exploit scenario a review role writes goes into the operator's draft, not into the record;
- the CWE identifier that §6 asks for waits for the advisory, because it names the defect's class;
- the finding is filed as a work-item, not as a defect, whose record requires a reproduction
  (`run-feedback`).

Detail that was public before a finding came under this rule is not repeated or extended; a new
record cites the existing record by its id. The rule holds for a private repository too: a
private repository is cloned, forked and made public later. (TASK 110 drafted such a report inside
a public repository; its security review caught the draft before a commit.)

### 6.2 A review that cannot finish

An audit has two parts: the scan and the manual adversarial review. Its verdict is one of three:

- `PASS`: both parts ran to completion and found no CRITICAL or HIGH issue;
- `FAIL`: a part found a CRITICAL or HIGH issue, whether or not the other part completed;
- `INCOMPLETE`: a part did not run to completion, and neither part found a CRITICAL or HIGH issue.

When either part does not run to completion, the audit is never `PASS`, and the report names that
part. The causes include a refused tool, a stopped turn, a missing environment and a scan with
`scan_status: NOT_RUN`. An auditor whose turn stops returns no report, so the orchestrator records
the audit as `INCOMPLETE` itself.

1. **Re-run once.** The orchestrator re-runs that part once, in a fresh agent or session, on the
   round's frozen tree. A fix round does not reset the count: each part gets one re-run in a run.
2. **Then the operator decides.** If the re-run does not complete either, the operator chooses in
   their own message, and the record quotes it. The choices are to ship the control with the gap
   recorded, to defer it to a work-item, or to remove it.
3. **No unverified security claim.** A security control whose bypass hunt never finished does not
   ship as protection. Its changelog and documents say it is unverified, or it moves to a
   work-item.
4. **Tests are not the hunt.** Tests and a mutation run with a passing baseline show that the tests
   pin the specification. They do not show that the specification closes the threat.

(TASK 111's retro wrote this rule. The bypass hunt on its anchor hook had stopped, and the
operator had deferred the hook to a work-item.)

## 7. Rationalization Table

| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "The script reported [OK], so it's clean" | Check `skipped_files` count. Silent skips = false negatives. |
| "This is a test/dev environment" | Attackers pivot from dev to prod. Zero Trust applies everywhere. |
| "Dependencies are only dev dependencies" | `devDependencies` run during build. Supply chain attacks don't discriminate. |
| "The flag is a false positive" | Verify manually. Never dismiss without proof. |
| "I'll fix it later" | Later = Never. Critical/High = Blocker NOW. |
| "The LLM generated this code, it's fine" | LLMs hallucinate vulnerabilities. Treat output as untrusted. |
| "The IaC is only for staging" | Staging configs often get copy-pasted to production. Secure from day one. |
| "We don't need an SBOM" | EU Cyber Resilience Act and US EO 14028 require it. Regulators disagree. |
| "The repository is ours, so the reproduction can sit in the review record" | Every reader of the repository gets a working attack before the advisory exists (§6.1). |
