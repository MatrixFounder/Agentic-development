# Development Plan: Task 069 — Agentic/MCP Security Upgrade (C-11 / C-14)

**Source spec:** `docs/TASK.md` (Task 069) · **Gate:** `skill-self-improvement-verificator` (Mode B)
**Architecture impact:** none — additive scanner module + reference checklist inside the existing Tier-2 `security-audit` skill, plus an additive subsection in an existing role prompt. `docs/ARCHITECTURE.md:173` (security-auditor wrapper, "uses `run_audit.py`") stays accurate; **no ARCHITECTURE.md edit**.

## Phase 0 — T0: Backup (Rollback safety) — workflow §3.1
1. `mkdir -p .agent/archive`
2. Bootstrap files: `for f in CLAUDE.md AGENTS.md GEMINI.md; do [ -f "$f" ] && cp "$f" ".agent/archive/$f.bak"; done` (none will be edited; backed up per workflow anyway).
3. Edit targets:
   - `cp .agent/skills/security-audit/SKILL.md .agent/archive/security-audit.SKILL.md.bak`
   - `cp .agent/skills/security-audit/scripts/audit/patterns.py .agent/archive/patterns.py.bak`
   - `cp .agent/skills/security-audit/scripts/audit/scanners.py .agent/archive/scanners.py.bak`
   - `cp .agent/skills/security-audit/scripts/audit/helpers.py .agent/archive/helpers.py.bak`
   - `cp .agent/skills/security-audit/scripts/audit/external.py .agent/archive/external.py.bak`
   - `cp .agent/skills/security-audit/scripts/audit/config.py .agent/archive/config.py.bak`
   - `cp .agent/skills/security-audit/scripts/audit/__init__.py .agent/archive/audit.__init__.py.bak`
   - `cp .agent/skills/security-audit/scripts/run_audit.py .agent/archive/run_audit.py.bak`
   - `cp .agent/skills/security-audit/tests/test_smoke.py .agent/archive/test_smoke.py.bak`
   - `cp System/Agents/10_security_auditor.md .agent/archive/10_security_auditor.md.bak`
4. **Verify:** all `.bak` files exist.

**Rollback plan:** restore each edited file from `.agent/archive/<name>.bak`; the new checklist file and new tests are pure additions (delete to roll back). No state migration.

## Phase 1 — T1: [R1] Checklist `references/checklists/mcp_agentic_security.md` (new file)
Sections, in order: header (sources + verified-on date) → **ASI01…ASI10** (one `##` each, 1:1, checkbox items embedding the named attack patterns: tool poisoning, rug pull, tool shadowing, full-schema poisoning → ASI01/02/04/06; confused deputy, token passthrough, session hijacking → ASI03/07) → **NSA CSI controls** section (least-privilege tokens, context labeling, cryptographic isolation, audit logging, outgoing filtering proxy/DLP, signed provenance, registry hardening, sandboxing, local MCP scans) → **incident calibration block** (CVE-2025-6514, CVE-2025-49596, MCP-STDIO 11-CVE cluster, postmark-mcp, s1ngularity, Shai-Hulud) → **scanner-floor note** (which checks the regex layer automates vs which require LLM/manual review). Target 80–110 lines, matching house checklist style (`owasp_top_10.md` format).
**Verify (atomic):** file exists; exactly 10 `ASI` section headers; all 7 named attack patterns present verbatim; line count in range.

## Phase 2 — T2: [R2] Scanner — Stub-First (carry-forward #1)

**T2a — Stubs (importable, zero behavior):**
1. `config.py`: add `MCP_CONFIG_FILENAMES = {'mcp.json', '.mcp.json', 'claude_desktop_config.json'}` + `MCP_SCAN_PRUNE = SKIP_DIRS - {'.vscode'}` (carry-forward #4).
2. `patterns.py`: add `MCP_AGENTIC_PATTERNS: list` (empty stub with format docstring: 5-tuples `(regex, name, severity, category, cwe)`, ASI ID carried in `category`).
3. `scanners.py`: add `scan_mcp_agentic(project_path) -> Dict` stub returning the standard empty result shape (`tool="mcp_agentic_scanner"`, `status="[OK] No MCP/agentic risks detected"`).
4. Registration: `audit/__init__.py` exports `scan_mcp_agentic`; `run_audit.py` scanners dict gains `"mcp": ("mcp_agentic", scan_mcp_agentic)` + argparse choices gain `mcp`; `helpers.detect_project_types` gains `"mcp"` type (stub: never true yet).
5. **Verify stubs:** `python3 -m pytest` existing suite green; `run_audit.py . --scan-type mcp` runs, reports empty `[OK]`.

**T2b — Tests first (Red):** extend `tests/test_smoke.py` (new section "MCP / Agentic (v3.4)"):
1. provenance finding for `mcp.json` (low, `MCP Config Present`); 2. `autoApprove` flagged (high, ASI03); 3. `.vscode/settings.json` `chat.tools.autoApprove` + `.vscode/mcp.json` found **despite SKIP_DIRS** (carry-forward #4); 4. unpinned `npx -y` flagged / `npx -y pkg@1.2.3` NOT flagged; 5. cleartext `"url": "http://…"` flagged / `http://localhost` NOT flagged; 6. **multi-line** `env`-block inline secret flagged (proves whole-file matching, carry-forward #3) / `${VAR}` reference NOT flagged; 7. shell `"command": "bash"` flagged (ASI05); 8. imperative tool-description heuristic flagged in a `.py` server file (ASI01/ASI06); 9. `<IMPORTANT>` marker flagged; 10. clean project → zero findings, `[OK]` status; 11. `detect_project_types` returns `mcp` for a dir with `mcp.json`; 12. self-exclusion: `scan_mcp_agentic(skill_dir)` → zero findings.
**Verify:** new tests FAIL (red) against stubs; old tests still green.

**T2c — Logic (Green):** implement in `patterns.py` (10 patterns) + `scanners.py`:
- **Pattern set (severity · category(ASI) · CWE):** 1) auto-approve keys (`chat.tools.autoApprove` / `"autoApprove":` / `"alwaysAllow":` / `"auto_approve":`) — high · Excessive Agency (ASI03) · CWE-862; 2) permission-bypass flags (`--dangerously-skip-permissions`, `--trust-all-tools`, `--yolo`) — high · Privilege Abuse (ASI03) · CWE-862; 3) unpinned `npx -y`/`--yes` (no `@<digit>` pin; `@latest` counts as unpinned) — high · Agentic Supply Chain (ASI04) · CWE-829; 4) unpinned `"args": […"-y"…]` JSON form — high · ASI04 · CWE-829; 5) `mcp-remote` usage — medium · ASI04 · CWE-494 (CVE-2025-6514 class); 6) `"url": "http://"` non-localhost — high · Insecure Transport (ASI07) · CWE-319; 7) inline secret in `env` block (value not `${…}`/`$VAR`/`%VAR%`) — high · Identity & Privilege Abuse (ASI03) · CWE-798; 8) shell-spawning `"command"` (`bash|sh|zsh|cmd|powershell`) — high · Unexpected Code Execution (ASI05) · CWE-78; 9) imperative-language-in-description heuristic — medium · Tool Poisoning (ASI01/ASI06) · CWE-1427; 10) `<IMPORTANT>` hidden-instruction marker — medium · Tool Poisoning (ASI01/ASI06) · CWE-1427. **No `critical` severities** (TASK NFR: regex can't prove exploitability of config).
- **File targeting (carry-forward #2):** known MCP config basenames (`MCP_CONFIG_FILENAMES`) → all patterns + provenance finding (low · ASI04 · CWE-829); other `CONFIG_EXTENSIONS` files → patterns 1, 2, 3, 5 only; `CODE_EXTENSIONS` files → patterns 9, 10 only. **`.md` files are NOT scanned** — markdown agent/skill prose is the LLM-review class (R4(c) note).
- **Matching mode (carry-forward #3):** whole-file `re.finditer` with `re.IGNORECASE | re.MULTILINE`, line numbers from match offset; ReDoS guard = IaC-style whole-file skip if any line > `MAX_LINE_LENGTH`.
- **Walk:** `os.walk(..., followlinks=False)` pruned with `MCP_SCAN_PRUNE`; self-exclusion via `is_self_path`; size guard via `MAX_FILE_SIZE`; `detect_project_types` flags `mcp` on any `MCP_CONFIG_FILENAMES` hit (same prune set).
**Verify:** full pytest green; `run_audit.py . --scan-type mcp` on this repo → 0 findings (UC-2); fixture dir spot-check matches UC-1.

## Phase 3 — T3: [R3] External tool roster (`external.py`)
After the language-specific blocks: `if "mcp" in types:` → `run_command(["snyk-agent-scan", "."], cwd=cwd)` with fallback `run_command(["mcp-scan"], cwd=cwd)`; code comment: *formerly Invariant mcp-scan; detects tool poisoning/shadowing/toxic flows; NEVER pass `--dangerously-run-mcp-servers` — an audit must not auto-start untrusted MCP servers* (carry-forward from Mode A risk R6). Missing tools stay non-fatal via `run_command`.
**Verify (atomic):** `python3 -c` import check; grep confirms the ban comment exists.

## Phase 4 — T4: [R4] `security-audit/SKILL.md` integration + version lockstep (carry-forward #6)
1. §2: usage string gains `mcp` in `--scan-type`; scope list gains the **MCP / Agentic** line (config provenance, auto-approve, unpinned servers, poisoning heuristics — CWE+ASI tagged); external-tools line gains `snyk-agent-scan` (ex-`mcp-scan`) with "when MCP config artifacts detected" trigger.
2. §3: new subsection **"Agentic / MCP (OWASP ASI Top 10 2026 + NSA CSI)"** — MANDATORY read `references/checklists/mcp_agentic_security.md`; Top Checks: (1) Goal Hijack (ASI01) — untrusted content reaching agent instructions? (2) Tool Poisoning / Rug Pull (ASI01/ASI04) — descriptions clean? definitions pinned + provenance-verified? (3) Excessive Agency (ASI03) — auto-approve off? least-privilege tokens? (4) Supply Chain (ASI04) — servers version-pinned, registries trusted? + **limitation note**: *semantic tool-description poisoning requires LLM review — the regex layer is only the deterministic floor.*
3. Version sync 3.3 → 3.4: frontmatter `version:`, H1 header, §2 mention if any; `run_audit.py` docstring; `audit/__init__.py.__version__`; frontmatter `description:` gains MCP/agentic.
**Verify (atomic):** `grep -rn "3\.3" SKILL.md scripts/run_audit.py scripts/audit/__init__.py` → no stale version; `grep -n "mcp" SKILL.md` shows scan-type + §3 subsection.

## Phase 5 — T5: [R5] `System/Agents/10_security_auditor.md`
1. §4 Execution Loop: insert **"Step 1.5: Agentic Threat Model (OWASP ASI Top 10 2026)"** — applies whenever scope contains agents/LLM tools/MCP configs: goal-hijackable (ASI01)? tool calls tamperable/poisoned (ASI02)? identities & privileges scoped, no auto-approve (ASI03)? supply chain pinned + provenance-verified (ASI04)? memory/context poisonable (ASI06)? inter-agent messages trusted blindly (ASI07)? — with pointer to `mcp_agentic_security.md` + `run_audit.py --scan-type mcp`.
2. §2 TIER 1: add the checklist reference for agentic/MCP targets (skill list itself unchanged — TIER 0 block untouched).
3. Header version v3.6.0 → v3.7.0.
**Verify (atomic):** `grep -n "ASI\|MCP" 10_security_auditor.md` non-empty (roadmap acceptance); TIER 0 block byte-identical to backup.

## Phase 6 — T6: [R7a–d] Verification gate
1. `python3 -m pytest .agent/skills/security-audit/tests/` → all green.
2. `python3 .agent/skills/security-audit/scripts/run_audit.py . --output summary` → exit 0; **zero MCP findings on this repo** (UC-2); pre-existing scan results unchanged vs baseline run.
3. `python3 .agent/skills/skill-creator/scripts/validate_skill.py .agent/skills/security-audit` green; then all-skills loop → baseline 43/43 holds.
4. Drift greps: `grep -rn "scan-type all|deps" .claude/ .agent/ System/ --include='*.md'`-class check for stale scan-type enumerations; `grep -rn "121 automated regex patterns\|v3\.2" System/Docs/SKILLS.md` → updated in T7; no references to a non-existent `mcp_agentic_security.md` path elsewhere (path correctness).
5. Diff-scope check vs backups: edits confined to the TASK §3 file list.

## Phase 7 — T7: [R7e–i] Documentation & finalization
1. `CHANGELOG.md` + `CHANGELOG.ru.md`: **v3.20.0 — Agentic/MCP Security Upgrade** (C-11/C-14, audit 067 → roadmap item 3): new checklist, new `mcp` scan type (10 patterns, CWE+ASI), external roster, auditor threat model. README.md / README.ru.md version headers → v3.20.0 (house convention from v3.19.x commits).
2. `System/Docs/SKILLS.md:87`: refresh security-audit line — version v3.4, updated pattern count (recount at edit time), add MCP/agentic + ASI to capability list.
3. `docs/verification_roadmap.md`: item 3 → ✅ DONE (commit ref + date); P1 header note if needed.
4. Session state update (phase boundary) + final summary to user. Commit only on user request (house rule).

## Execution discipline
- Atomic order: T0 → T1 → T2a → T2b (red) → T2c (green) → T3 → T4 → T5 → T6 → T7; stop on any gate failure, fix forward or roll back from `.agent/archive/`.
- Session state persisted after Planning approval (now), after T6 (execution verified), after T7 (done).
- Lockstep wording: severity/category/CWE strings in `patterns.py` ↔ checklist §scanner-floor ↔ SKILL §2 scope line must agree (grep-checked in T6.4).
