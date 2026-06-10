# Development Plan: Task 070 — OWASP Top 10 Checklist Re-map to 2025 Final (C-09)

**Source spec:** `docs/TASK.md` (Task 070) · **Gate:** `skill-self-improvement-verificator` (Mode B)
**Architecture impact:** none — content re-map inside the existing Tier-2 `security-audit` skill + comment-only docstring edits. **No ARCHITECTURE.md edit.**
**Behavior contract:** zero functional change — pattern lists, finding fields, severities, CLI untouched. Proof: pytest 30/30 identical, `run_audit.py` repo finding counts identical to pre-edit baseline (note: full summary output legitimately differs by the v3.4→v3.5 header line — `run_audit.py:99` embeds `AUDIT_VERSION`).

## Phase T0 — Backup (Rollback safety) — workflow §3.1
1. `mkdir -p .agent/archive`
2. Bootstrap files (none edited; backed up per workflow): `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done`
3. Edit targets → `.agent/archive/`: `owasp_top_10.md`, `security-audit/SKILL.md`, `audit/scanners.py`, `run_audit.py`, `audit/__init__.py`, `System/Docs/SKILLS.md`, `docs/verification_roadmap.md`, `CHANGELOG.md`, `CHANGELOG.ru.md`.
4. Capture pre-edit baselines: `python3 -m pytest .agent/skills/security-audit/tests/ -q` (expect 30 passed) and `run_audit.py . --output summary` counts.

## Phase T1 — R1: Re-section `references/checklists/owasp_top_10.md`

**Content-move map (every 2021 item accounted — carry-forward #1):**

| 2025 section | Content source | Notes |
|---|---|---|
| A01 Broken Access Control | old-A01 (7) + old-A10 SSRF (6) | old-A01's single SSRF line merges with old-A10's "URL Allowlist" (dedup −1) → net +5. Header: CWE-284, 639, 918 |
| A02 Security Misconfiguration | old-A05 minus stack-trace check | CWE-209 item **moves to new A10**. Header: CWE-16, 611 |
| A03 Software Supply Chain Failures | old-A06 (all 6) + from old-A08: deps-audit, CI/CD tampering, code signing | Header: CWE-1104, 829, 494 |
| A04 Cryptographic Failures | old-A02 (all 6) | Header: CWE-259, 327, 331 |
| A05 Injection | old-A03 (all 6) | Header: CWE-79, 89, 78 |
| A06 Insecure Design | old-A04 (all 5) | Header: CWE-256, 501, 657 (drop 209 — now canonical in A10) |
| A07 Authentication Failures | old-A07 (all 6), section renamed | Header: CWE-287, 384 |
| A08 Software or Data Integrity Failures | old-A08 minus 3 supply-chain items; renamed "and"→"or" | Keeps: deserialization (CWE-502), artifact-signature verification, unsigned auto-update. +1 new: untrusted plugin/model load (CWE-829→cross-ref A03). Header: CWE-502, 345 |
| A09 Security Logging and Alerting Failures | old-A09 (all 6), section renamed | Header: CWE-778 |
| A10 Mishandling of Exceptional Conditions | **NEW** | Checks: stack-trace leakage (CWE-209, moved from old-A05), fail-open controls (CWE-636), unchecked return values/unusual conditions (CWE-754/252), swallowed exceptions/empty catch (CWE-390), resource cleanup on error paths (CWE-404/772), partial-failure rollback consistency |

Also:
- Header/source line: cite `owasp.org/Top10/2025/`, **verified 2026-06-10**; drop the false "(Final Release, Q4 2025)" framing.
- Append a compact **2021→2025 mapping table** at file end (compliance-remap aid for stale Jira/Snyk exports — the C-09 driver).
- **Conservation check:** old file = 61 checkboxes; new file = 61 − 1 (SSRF dedup) + 5 new-A10 + 1 new-A08 = **66**; verify with `grep -c '^- \[ \]'`.

## Phase T2 — R2: `security-audit/SKILL.md` re-tag + version 3.4 → 3.5
1. §2 scope list: Secrets `(OWASP A02, …)` → `(OWASP A04:2025 Cryptographic Failures, …)`; Dependencies `(A06/A08, …)` → `(A03:2025 Software Supply Chain Failures, …)`; Code Patterns/Injection `(A03, …)` → `(A05:2025, …)`; Config/Misconfiguration `(A05, …)` → `(A02:2025, …)`.
2. §3 Web/API Top Checks → 4 checks: A01 (IDOR + SSRF-absorbed note), A03 supply chain (pinning/lockfiles/SCA), A05 injection, A10 exceptional conditions (fail-closed, no stack traces).
3. Version sync (carry-forward #3): frontmatter `version: 3.5`, H1 `v3.5`, `run_audit.py` docstring `v3.5`, `audit/__init__.py __version__ = "3.5"`. Verify: `grep -rn "3\.4" SKILL.md scripts/run_audit.py scripts/audit/__init__.py` → empty.

## Phase T3 — R3: `scripts/audit/scanners.py` docstrings (comment-only)
- `:33` `(OWASP A06/A08, CWE-1104)` → `(OWASP A03:2025 Software Supply Chain Failures, CWE-1104)`
- `:136` `(OWASP A02, CWE-798)` → `(OWASP A04:2025 Cryptographic Failures, CWE-798)`
- `:230` `(OWASP A03 Injection, …)` → `(OWASP A05:2025 Injection, …)`
- `:299` `(OWASP A05 Misconfiguration, …)` → `(OWASP A02:2025 Security Misconfiguration, …)`
- Pre-checked (carry-forward #4): test suite contains **no** A-number literals → docstring edits cannot break tests.

## Phase T4 — R5: Docs & registry
1. `System/Docs/SKILLS.md:87`: `v3.4` → `v3.5`, "OWASP Top 10" → "OWASP Top 10:2025 (final taxonomy)".
2. `CHANGELOG.md` + `CHANGELOG.ru.md`: v3.20.1 entry — checklist re-mapped to verified 2025 final; renumbering flagged for downstream compliance exports; historical entries untouched.
3. `docs/verification_roadmap.md` item 4: 🔜 → ✅ DONE (commit ref, verification note, patterns.py-assumption correction).

## Phase T5 — Verification gates (all must pass; failure → fix or rollback via T0 backups)
1. **Conservation:** checkbox count 66; every old item findable in new layout (diff review).
2. **Stale-reference grep (objective gate, carry-forward #5):** `grep -rn "A0[0-9]\|A10" .agent/skills/security-audit/ System/Agents/ .claude/agents/ --include="*.md" --include="*.py"` → every hit is 2025-correct. Named exclusions: ASI/API/LLM identifiers don't match the pattern; CHANGELOG + `docs/reviews/` + archived tasks are outside grep scope by design.
3. **Skill gate:** `validate_skill.py .agent/skills/security-audit` pass + full 43/43 baseline loop.
4. **Behavior proof:** pytest 30/30; `run_audit.py . --output summary` counts byte-identical to T0 baseline.
5. **Diff scope:** `git status` touches only the 9 declared files + `docs/TASK.md`/`PLAN.md`/audit artifact/session state.

## Rollback
Restore any file from `.agent/archive/<name>.bak` (workflow §5). New content is confined to existing files — no file creations/deletions to reverse (checklist edited in place).
