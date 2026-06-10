# Technical Specification: Complete Item 6 In-Repo — Antigravity + 6d + 6e (C-07)

### 0. Meta Information
- **Task ID:** 081
- **Slug:** `vendor-adapters-6d-6e-antigravity`
- **Mode:** Framework Upgrade (1 new reference, 1 generator script + manifest, 12 generated wrappers, workflow + skill edits, KNOWN_ISSUES; zero security-scanner change)
- **Type:** P1, roadmap item **6** — finishes the **in-repo** portion: adds the Google Antigravity adapter (4th vendor), demotes sequential-fallback (6d), and ships the Wave-5 wrapper generator + extended drift-grep (6e). After this, item 6's ONLY remaining piece is **operator e2e validation**.
- **Workflow:** `/framework-upgrade` (verificator Modes A+B).
- **Source:** User request (2026-06-10): "Сделай сейчас 6d … + добавь google Antigravity subagents … + 6e drift-grep + Wave-5 генератор". Antigravity primitives verified via web (primary docs JS-empty; corroborated across antigravity.google/docs/agent-manager, DataCamp, Medium/Google-Cloud, GitHub gemini-cli discussion #27305).

## 1. Antigravity findings (verified 2026-06-10)

- **Two subagent modes:** (a) **dynamic subagents** — the orchestrator defines+spawns them on the fly, **no config files** (the headline feature); (b) **custom agents** — `agent.json` at `~/.gemini/antigravity-cli/agents/<name>/agent.json`, fields `name`, `description`, `hidden`, custom system-prompt sections.
- **Parallel:** ✅ asynchronous subagents run concurrently (`/agent <task>` dispatches background agents, several in parallel); isolated context windows.
- **Config/skills:** `AGENTS.md → GEMINI.md → built-in` priority; skills at `<root>/.agent/skills/` (workspace) + `~/.gemini/antigravity/skills/` (global). Custom-agent config also from `.agents/`.
- **⚠️ Detection ambiguity:** Antigravity shares `AGENTS.md` (with Codex) and `~/.gemini/` paths (with Gemini CLI). No clean unique project root marker in the docs — the scaffold uses a provisional `.antigravity/` marker and documents the ambiguity + tie-break.
- **Architectural note:** Antigravity is **dynamic-first** — static critic wrappers map to its *custom agents* (agent.json), but its native style spawns specialists on demand. The reference documents both.

## 2. RTM

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| R1 | `references/antigravity.md` stub→full: §1 findings, concept-map, dynamic-vs-static note, `agent.json` format, parallel ✅, detection ambiguity, ⚠️ scaffold banner, validation gate | `references/antigravity.md` | file read; G1 |
| R2 | **Wave-5 generator (6e):** `scripts/wrappers_manifest.json` (3 critics × {name, domain, sot_skill, description, scope, evidence_note}) + `scripts/generate_wrappers.py` emitting per-vendor wrappers in native format (Gemini MD+YAML, Codex TOML, Cursor MD+YAML, Antigravity JSON). **Claude excluded** (validated reference/donor — documented). Idempotent | `scripts/generate_wrappers.py`, `scripts/wrappers_manifest.json` | run produces 12 files; G3 |
| R3 | Regenerate all scaffold wrappers from the manifest (replaces the 9 hand-written from 080 with generated-equivalent + adds 3 Antigravity = **12**) | `.gemini/agents/`, `.codex/agents/`, `.cursor/agents/`, `.antigravity/agents/` | file counts; G3 |
| R4 | SKILL §1.1 detection: Antigravity row updated (provisional `.antigravity/` marker + ambiguity note); scaffold-status note covers 4 vendors | `SKILL.md` §1.1 | file read |
| R5 | **6d:** `vdd-multi.md` "Fallback (Sequential)" → "**Vendor dispatch**" — resolve runtime per skill §1 → native adapter; sequential = documented **last resort** (primitive-less runtimes / single-session debug / 1-slot CI). Remove "Functionally equivalent" (vdd-multi + SKILL §7). All flags honored on every path | `vdd-multi.md`, `SKILL.md` §7 | G2 grep; file reads |
| R6 | **6e drift-grep:** KNOWN_ISSUES wrapper-drift entry extended to **all** wrapper dirs (`.claude/agents/`, `.gemini/agents/`, `.codex/agents/`, `.cursor/agents/`, `.antigravity/agents/`) + note the generator regenerates scaffolds | `docs/KNOWN_ISSUES.md` | file read |
| R7 | SKILL 3.6→3.7 + §9 History; bookkeeping CHANGELOG EN+RU v3.20.10, README×2, roadmap item 6 (6a–6e ✅ in-repo · validation ⏳), audit `framework-audit-081.md`, session-state | standard set | file reads |

## 3. Gates
- **G1:** antigravity.md carries ⚠️ scaffold banner + states the detection ambiguity + parallel ✅.
- **G2:** `grep -rn "Functionally equivalent" .agent/` → empty (C-07 claim removed); "Vendor dispatch" present in vdd-multi; sequential explicitly "last resort".
- **G3:** `generate_wrappers.py` runs clean, emits 12 wrappers; all 12 reference their SOT skill + convergence enum; Codex TOML + Antigravity JSON parse; skill sweep **43/43**.
- **G4:** pytest security-audit 30/30; no security-scanner edits.
- **G5 (honesty):** Antigravity dynamic-vs-static + detection ambiguity stated; all 4 vendors ⚠️ unvalidated; roadmap item 6 **validation still ⏳** (not ✅ done).

## 4. Out of Scope
e2e validation (operator+hardware), antigravity dynamic-subagent runtime integration (only the static custom-agent wrappers are scaffolded), Claude wrapper regeneration (stays hand-maintained reference). Generator is a script (not a skill — `init_skill.py` N/A).

## 5. Open Questions
None blocking. Judgment: (a) Claude excluded from generation (it is the donor/reference, keeping it source-not-derived); (b) Antigravity `.antigravity/` marker is provisional, ambiguity documented; (c) 6d demotes sequential-fallback per user request even though adapters are scaffold-status — the "Vendor dispatch" section honestly notes adapters are documented-not-validated, so sequential stays the safe path until graduation.
