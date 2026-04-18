# VDD Critique: Security Audit Skill — Round 4 (v3.2 → v3.3 release gate)

## 1. Executive Summary
- **Verdict**: **PASS** after R4 fixes applied. `issues-found` at adversarial entry → `clean-pass` after remediation.
- **Confidence**: High — all 10 findings empirically reproduced in `/tmp/*` fixtures and verified after fix via [`tests/test_smoke.py`](../tests/test_smoke.py) (17/17 pass).
- **Summary**: Round 3 (v3.2) closed the critical Solidity-pattern gap. Round 4 audited the v3.3 patch itself and found that the initial R3-driven "green smoke test" masked 4 dead regex patterns, 1 behavior regression (pip-compile false positive), 1 perf regression (SBOM rglob on monorepos), 1 reliability issue (semgrep sub-timeout), and 3 hygiene gaps (ReDoS scope, tests absent, version split across files). All fixed pre-release.

## 2. Risk Analysis

| # | Severity | Category | Issue | Fix |
| :--- | :--- | :--- | :--- | :--- |
| H1 | HIGH | Dead regex | Go `math/rand\.(?:Int...)` never matches real Go call-sites (imports alias to `rand.`, not `math/rand.`). Confirmed via `/tmp/sec_go_test`. | Replaced with `\brand\.(?:Intn\|Int31n?\|Int63n?\|Float32\|Float64\|Read\|NewSource\|Perm\|Shuffle)\b`; accepts some cross-language noise per v3.2 philosophy. Test: `test_go_rand_call_site_flagged`. |
| H2 | HIGH | Dead regex | ApolloServer `\{[^}]*\}` never matches multi-line configs (scan is line-by-line). Confirmed via `/tmp/sec_gql`. | Simplified to `new ApolloServer\s*\(\|ApolloServer\s*\(\s*\{` — flags on constructor line, prompts manual depth/complexity review. |
| H3 | HIGH | Perf regression | `Path.rglob` traverses `SKIP_DIRS` first, filters after. On monorepos with `node_modules` (~300k files) this takes tens of seconds. | Switched to `os.walk` with `dirs[:] = [d for d in dirs if d not in SKIP_DIRS]` pre-prune. Also: case-insensitive match (`SBOM.json` now caught). Tests: `test_sbom_*`. |
| H4 | HIGH | Behavior regression | R3 made `requirements.txt` NOT count as lock. True literally, but pip-tools hash-pinned output (`--hash=sha256:...`) IS a de-facto lock. R3 flagged those projects as "missing lock". Confirmed via `/tmp/sec_pip_hashes`. | Added `_python_has_hash_pinned_requirements(base)` check: scans first 1MB of requirements.txt for `--hash=sha256:`; if present, ecosystem is considered locked. Test: `test_hash_pinned_requirements_accepted_as_lock`. |
| M5 | MED | Scope gap | ReDoS guard (`MAX_LINE_LENGTH=4000`) only in `scan_code_patterns`. `scan_secrets` reads whole content; `scan_iac` uses multi-line `re.finditer`. | `scan_secrets`: filter long lines before `re.findall` (all SECRET_PATTERNS are line-local). `scan_iac`: skip file entirely if any line > limit (IaC patterns span lines — can't filter). Test: `test_long_line_skipped_by_redos_guard`. |
| M6 | MED | Overclaim | CHANGELOG v3.14.2 claimed "Rust, Go, and GraphQL codebases now receive first-class in-process regex coverage". Given H1/H2, Go/GraphQL coverage was shallow. | Softened to "**initial** coverage; external tools (gosec, govulncheck, semgrep) remain primary for depth". EN + RU CHANGELOG both updated. |
| M7 | MED | Reliability | `run_command` `timeout=120` is global; semgrep on non-trivial repos exceeds it and gets killed silently. | Raised default to `timeout=600` (10 min) + parameterized per-call. No change in caller signatures (backward compatible). |
| L8 | LOW | Dead regex (pre-existing) | Solidity "public mutator" pattern didn't match `returns (...)` or `payable` between `public` and `{`. Real mutators often have one. | Widened tail: `(?:\s+(?:payable\|nonpayable\|returns\s*\([^)]*\)))*`. Functions with custom modifiers (e.g. `onlyOwner`) correctly excluded. Tests: `test_solidity_public_payable_returns_flagged`, `test_solidity_modifier_not_flagged`. |
| L9 | LOW | Test gap | Zero automated tests despite v3.2 Round 3 fix and v3.3 Round 3 patches. | Added `tests/test_smoke.py` — 17 regression tests covering every R3+R4 fix. Offline; no external deps. |
| L10 | LOW | Version sprawl | `SKILL.md` said v3.3, `run_audit.py` hardcoded `v3.3` in 3 places, package modules had no `__version__`. Drift-prone. | Added `__version__ = "3.3"` in `audit/__init__.py` as SOT; `run_audit.py` imports it for CLI `description` and summary header. Test: `test_version_is_exposed`. |

## 3. Hallucination Check

- [x] **Files**: All cited paths verified via `Read` tool prior to editing.
- [x] **Empirical reproduction (4/4 HIGH)**: Each HIGH finding demonstrated on a minimal fixture in `/tmp/` with actual scanner output before claiming the bug exists. Post-fix, each fixture re-run to confirm correct behavior.
- [x] **Regression suite**: 17/17 `pytest` pass locally on `Python 3.14.2` (see [pytest output captured during R4](.pytest_cache)).
- [x] **No fabricated line numbers or files**: [scanners.py:232](../scripts/audit/scanners.py) `re.search(pattern, line, ...)` confirmed; [helpers.py:24](../scripts/audit/helpers.py) `timeout=120` confirmed (then raised).

## 4. Convergence Assessment

| Round | Findings | Real / Hallucinated |
| :--- | :--- | :--- |
| R3 (v3.1 → v3.2) | 3 (1 CRITICAL Solidity-patterns-absent + 2 minor robustness) | 3/0 |
| R4 (v3.2 → v3.3) | 10 (4 HIGH + 3 MED + 3 LOW) | 10/0 |

Both rounds produced entirely real findings — **no hallucinations yet**. Convergence is NOT achieved; R5 on v3.3 would likely surface 2-3 more items (e.g., `gitleaks --no-banner` flag volatility across versions; semgrep auto-config network dependency under air-gapped CI; `rand.*` pattern noise on Python `random.randint`).

**Exit condition not met — but diminishing returns.** Defer R5 until a concrete integration concern triggers it, per ROADMAP discipline.

## 5. Changes Applied in Round 4

### Files modified
- [scripts/audit/patterns.py](../scripts/audit/patterns.py) — H1, H2, L8
- [scripts/audit/scanners.py](../scripts/audit/scanners.py) — H3 (SBOM os.walk), H4 (pip hash-pin), M5 (ReDoS guard extension)
- [scripts/audit/config.py](../scripts/audit/config.py) — SELF_DIR widened to skill root (caught by L9 test)
- [scripts/audit/__init__.py](../scripts/audit/__init__.py) — L10 `__version__`
- [scripts/audit/helpers.py](../scripts/audit/helpers.py) — M7 `timeout=600`
- [scripts/run_audit.py](../scripts/run_audit.py) — L10 import `__version__` for CLI
- [tests/test_smoke.py](../tests/test_smoke.py) — L9 (new file, 17 tests)
- [../../CHANGELOG.md](../../../../CHANGELOG.md) + `CHANGELOG.ru.md` — M6 softening

### Non-changes (rejected during R4)
- Not done: adding Python `random.randint` exclusion to Go `rand.*` pattern. Acceptable noise per v3.2 philosophy; would require file-extension-aware pattern dispatch (architectural change).
- Not done: semgrep `--config auto` offline fallback. Semgrep installs rules from network by default; hard to cache within the skill. External-tool failures remain non-fatal per `run_command` contract.

## 6. Release Readiness

- [x] All HIGH issues fixed, verified by test.
- [x] All MED issues fixed.
- [x] All LOW issues fixed.
- [x] 17/17 pytest smoke tests pass offline.
- [x] No behavior regression for Claude Code users (new `--max-size` is additive; existing flags unchanged).
- [x] CHANGELOG v3.14.2 accurate + R4 softening applied.

**Recommendation**: v3.3 ready for release tag. Supersedes vdd-round3-critique.md conclusion ("Round 4 would likely produce only hallucinated or out-of-scope critiques") — in practice Round 4 produced 10 real findings. Lesson: adversarial convergence signal ≠ exit signal; keep going until hallucination-rate > 50% of findings.
