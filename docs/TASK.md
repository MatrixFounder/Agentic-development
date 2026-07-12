# Technical Specification: run-feedback engine — quality feedback loop (collect → triage → file)

### 0. Meta Information
- **Task ID:** 089
- **Slug:** `run-feedback-engine`
- **Mode:** Framework Upgrade (new tier-2 skill with scripts + workflow/command wiring)
- **Type:** New capability. Implements the approved cross-repo plan
  (`~/.claude/plans/lexical-gliding-matsumoto.md`, v2 after a 3-critic VDD-adversarial pass).
- **Workflow:** `/framework-upgrade` discipline (verificator gates on plan already passed externally).

### 1. Problem Description
Errors from runs of composite commands, workflows, and skills evaporate today: no workflow has a
retro step, failures are not aggregated, and nothing feeds the `known-issues-format` ledger or the
product backlogs systematically. Consumers of this framework (e.g. Universal-skills) need a
closed loop: **capture → triage → file → (later) auto-heal**.

### 2. Requirements (RTM)

| ID | Requirement | Verify |
|----|-------------|--------|
| R1 | New framework skill `.agent/skills/run-feedback/` (tier 2, hybrid): stdlib-only CLI `scripts/run_feedback.py` with subcommands `collect / triage / file / journal / issues / mine / claim / release / doctor`. | `--help` per subcommand; unit tests green. |
| R2 | Finding model v1: fingerprint = `sha256(component + envelope.type|exit:<code> + normalized_message)[:16]` (NO source in preimage); `sources[]` union on dedup-merge; collect is idempotent (exit 0 on dedup). | `tests/test_fingerprint.py`, `tests/test_inbox_collect.py`. |
| R3 | All machine state under `<repo>/.agent/feedback/` (inbox/filed/dismissed, journal `YYYY-MM.md` flock+fsync append-only, mine_state, locks). No ledger writes from collect. | `tests/test_journal.py` (multiprocess hammer), `tests/test_inbox_collect.py`. |
| R4 | `file --as defect`: contract frontmatter per `known-issues-format` + optional keys AFTER `slug` (`component, fingerprint, evidence_paths, auto_fixable, finding_ref`); index line routed into the correct `## <category>` section (create alphabetically; preamble `## Rules`/`## How to add` untouched); lockstep rollback (issue file first, index failure removes it); both write paths under one flock. | `tests/test_file_lockstep.py` (placement regression), `tests/test_dry_run.py`. |
| R5 | ID allocation tolerant of the real messy namespace (`TF-X-7`, `XLSX-10B-DEFER`, `HTML2MD-11-BUG`): per configured prefix `^{prefix}-(\d+)(?:[A-Z-].*)?$`, max+1; mandatory `component→prefix` map in per-repo config. | `tests/test_id_allocation.py` seeded with real IDs. |
| R6 | `file --as work-item`: bullet appended at the seeded anchor `<!-- feedback:discovered-issues -->`; missing anchor → exit 4 (no blind EOF append). | `tests/test_backlog_append.py`. |
| R7 | Ledger reads are tolerant (live `handled`, `MED/MEDIUM`, missing severity accepted); writes strict per contract vocab. `issues --json` normalizes unknown/missing severity to lowest rank. | `tests/test_triage.py`, `tests/test_issues_feed.py`. |
| R8 | Own JSON error envelope `{v:1,error,code≠0,type,details}` — schema-compatible with, but NOT a byte copy of, the proprietary office `_errors.py` (license firewall). | code review; no byte-identical file. |
| R9 | Contract self-test: frontmatter keys + index-line format asserted against `known-issues-format` SKILL.md/template in-repo. | `tests/test_contract_sync.py`. |
| R10 | Retro ownership is deterministic: `claim --run-id` / `release` via flock file `.agent/feedback/retro_owner` (first workflow claims; nested workflows skip). | `tests/test_claim.py`. |
| R11 | `mine`: enumerate ALL `~/.claude/projects/` dirs decoding under repo root; incremental byte-offset state; noise-policy shared with hooks; retry aggregation (≥3 same fingerprint → repeated-failure); redaction; excerpts ≤400 chars; `--dry-run`. | `tests/test_mine.py` with fixture jsonl. |
| R12 | Hooks scripts ship with the skill (`scripts/hooks/`): PostToolUse filter + SessionEnd marker; run ONLY when `RUN_FEEDBACK_HOOKS=1`; fail-silent; data dir resolved via `git rev-parse --git-common-dir`. | `tests/test_hook_filter.py` (synthetic payloads). |
| R13 | Wiring: `/run-feedback` command; retro step (claim-or-skip, non-blocking) inserted into the 17 terminal workflows; Global Protocols line in CLAUDE.md + GEMINI.md (lockstep); `known-issues-format` optional keys documented in SKILL.md AND seed template identically (check_contract_sync.py stays green). | grep; `check_contract_sync.py` exit 0. |
| R14 | `/heal-issues` workflow + command per approved plan Component 3 (strict `auto_fixable: true` opt-in, run-lock, branch-only, bounded, gate timeouts, notification; never push/merge). | workflow review vs plan; dry-run on pilot. |

### 3. Out of scope
Per-repo config/anchor/hooks-block in consumer repos (done in the consumer repo, e.g.
Universal-skills), publication of the engine as a product-catalog skill, and any cron creation
(user-level, staged rollout Stage 0 = manual only).

### 4. Constraints
- stdlib-only Python 3.9+; no venv; no network at runtime.
- Never mutate existing issue files or index lines (create-only writes; resolving stays with
  `known-issues-format` discipline / heal harness).
- `check_contract_sync.py` must remain green after contract edits.
