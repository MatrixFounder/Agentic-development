# VDD Critique: Task 070 — OWASP Top 10:2025 Checklist Re-map (v3.20.1)

## 1. Executive Summary
- **Verdict**: WARNING (1 MEDIUM documentation-accuracy finding; no code/logic/security defects)
- **Confidence**: High
- **Summary**: The re-map itself is correct — taxonomy matches the primary source, content conservation holds at item level (not just count level), no stale references survive anywhere in the repo (including beyond the original gate's grep scope), and cross-repo copies are symlinks (no drift). However, the verification **evidence is overclaimed** in three shipped documents: "repo audit summary byte-identical" is false in the strict sense the words assert.

## 2. Risk Analysis

| Severity | Category | Issue | Impact | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **MED** | Documentation / Evidence honesty | CHANGELOG.md, CHANGELOG.ru.md, and roadmap item 4 claim "repo audit summary **byte-identical** to the pre-edit baseline". But `run_audit.py:99` prints `Security Scan v{AUDIT_VERSION}` in every summary, and this very release bumps `__version__` 3.4→3.5 — so the full summary **necessarily differs by one line**. What was actually verified: the four finding-count lines (22/10C/0H/12M) are identical; findings themselves are unchanged by code-level argument (comment-only + version-string diff). The PLAN's own wording ("**counts** byte-identical") was accurate; the qualifier was dropped during CHANGELOG/roadmap write-up. In a framework whose P0 fix this quarter was "never fabricate scanner output" (C-15), an evidence claim stronger than what was checked is a legitimate finding, not style. | Erodes the exact trust property the verification stack exists to provide; a future reader re-running the comparison will get a diff and conclude the gate lied. | Re-word all three locations: "finding counts and findings unchanged vs pre-edit baseline; only output diff is the intentional v3.4→v3.5 header line." |
| **LOW** | Consistency | New A10 item "**Partial Failure**" is the only checkbox in its section without a CWE reference (siblings carry CWE-209/636/252/754/390/404/772). | Slightly weakens the file's "CWE mapping for compliance integration" promise. | Tag it CWE-460 (Improper Cleanup on Thrown Exception). |
| **LOW** | Process / Rollback discipline | `README.md`/`README.ru.md` version-header bumps were added during Phase 4 outside the PLAN's declared file list and were **not backed up** to `.agent/archive/` — every other edited file was (T0 discipline). Self-flagged in the completion report, but the backup gap itself was left open. | Inconsistent rollback story (git-only for 2 files, `.agent/archive` for the rest). | `cp` both READMEs to `.agent/archive/` (one command); note scope addition in the audit artifact. |
| **INFO** | Style | Roadmap item 4's DONE entry drops the original **Work/Acceptance** text, while item 3's DONE entry retained its full original body. Traceability is preserved via TASK 070 / PLAN / framework-audit-070. | None material. | Optional: leave as-is; bikeshedding. |

## 3. Adversarial Checks Performed (fresh evidence, not the builder's gates)

| Attack | Result |
| :--- | :--- |
| Repo-wide stale-A-number grep, **wider scope than the T5 gate** (all dirs incl. `*.json`, skill `docs/`, workflows; excluding only archives/history) | ✅ Clean — zero stale 2021-numbered references |
| Item-level conservation diff (`comm` on bold check-names old vs new), not count-level | ✅ Old-only items = documented rename (`Dependencies`→`Dependency Audit`) + documented SSRF dedup; new-only = exactly the declared A10/A08 additions |
| Version-string leakage into scanner output (falsifies "byte-identical") | ❌ **Confirmed leak** — `run_audit.py:99` summary header embeds `AUDIT_VERSION` → MED finding above. JSON output verified version-free (`['project','timestamp','scan_type','scans','summary']`) |
| Cross-repo copy drift (Universal-skills, both `.claude/skills/` and `.agent/skills/` paths) | ✅ Both are symlinks → `agentic-development/.agent/skills/security-audit`; canonical content, no drift |
| CWE spot-check of newly introduced mappings (636/754/390/252/404/772/345/657/494/829) | ✅ All names/IDs correct (stable pre-cutoff CWE registry) |
| Re-run of test suite during review | ✅ 30/30 |
| Roadmap item 4 post-edit render | ✅ Coherent |

## 4. Hallucination Check
- [x] **Files**: All cited files exist (`framework-audit-070.md`, `owasp_top_10.md`, `scanners.py`, `.agent/archive/*.bak`, Universal-skills symlinks resolved).
- [x] **Line Numbers**: `run_audit.py:99` (`Security Scan v{AUDIT_VERSION}`) confirmed by grep this session; `scanners.py:33/136/230/299` docstrings confirmed post-edit.
- [x] **External claims**: 2025 taxonomy was fetched from owasp.org/Top10/2025/ during the build session; this review did not re-fetch (15-min cache window; same session evidence accepted).

## 5. Convergence Status
Not yet at the objective bar: 1 MEDIUM legitimate finding (evidence overclaim) outstanding. CRITICAL: 0. After the MED + 2 LOW fixes land and the stale-grep/count gates re-run green, the remaining residue (INFO item) is bikeshedding-only → convergence.

## 6. Resolution (same session)
- **MED fixed:** unqualified "byte-identical" re-worded in `CHANGELOG.md`, `CHANGELOG.ru.md`, roadmap item 4, `docs/PLAN.md` behavior contract, and the `framework-audit-070.md` Mode B observation — all now claim exactly what was verified (finding counts identical; only output diff = intentional version header). Remaining repo occurrences audited: all either correctly qualified ("counts byte-identical", "TIER 0 block byte-identical") or immutable prior-release history (v3.20.0 roadmap item 3 line).
- **LOW-1 fixed:** A10 "Partial Failure" tagged CWE-460.
- **LOW-2 fixed:** `README.md` / `README.ru.md` backed up to `.agent/archive/` (T0 discipline restored).
- **Gates re-run:** checkbox count 66 ✓ · stale-A-number grep clean ✓ · pytest 30/30 ✓.
- **Verdict upgrade:** WARNING → **PASS (Objective Convergence)** — full test run executed, 0 CRITICAL, 0 legitimate findings outstanding, only the INFO style note (roadmap entry format) remains = bikeshedding-only.
