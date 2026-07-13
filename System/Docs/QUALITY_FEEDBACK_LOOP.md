# Quality Feedback Loop (`run-feedback` + `/heal-issues`)

**Version:** 1.0 (framework v3.21.0, task-089)
**Status:** Shipped & dogfooded — Stage 0 trust gate passed 2026-07-13 (3/3 pilot heals merged without correction).

> [!NOTE]
> **What this closes:** errors from runs used to evaporate — a gate failed, got retried, and the
> knowledge died with the session. This subsystem is the closed loop
> **capture → triage → file → heal → verify**: deterministic scripts own every file mutation,
> LLM judgement owns classification and fix authorship, and the existing ledgers
> (`known-issues-format` + the project backlog) stay the single source of truth. No new
> tracker, no repo-level cron, nothing invisible.

## Table of Contents
- [Architecture](#architecture)
- [Component 1: the `run-feedback` engine](#component-1-the-run-feedback-engine)
- [Component 2: capture surfaces](#component-2-capture-surfaces)
- [Component 3: the `/heal-issues` harness](#component-3-the-heal-issues-harness)
- [Setting up a consumer project](#setting-up-a-consumer-project)
- [Operations: Stage 0 → Stage 1](#operations-stage-0--stage-1)
- [Verified limitations](#verified-limitations)
- [Dogfood evidence](#dogfood-evidence)
- [Related documents](#related-documents)

## Architecture

```
Capture                          Engine (.agent/skills/run-feedback)      Ledgers (consumer repo)
───────                          ───────────────────────────────────      ───────────────────────
Retro step (Global Protocol) ─┐                                     ┌─► docs/issues/<slug>.md
/run-feedback (ad-hoc)        ├─► collect ─► .agent/feedback/ ──────┤    + KNOWN_ISSUES.md (lockstep)
SessionEnd hook + mine-on-end ┘    inbox/ + journal/ (gitignored)   ├─► backlog anchor (work-items)
                                        │                           └─► dismissed/ (noise, with reason)
                                   triage ─► LLM classification ─► file --dry-run → file

Consume: /heal-issues ─► issues --json ─► SELECT → REPRODUCE → FIX (branch, gates) → VERIFY & FILE
Schedule: operator-side only (Stage 1), never a repo artifact.
```

Two things ship in the framework and reach every consumer via the installer
(`.agent/skills/run-feedback/`, `.agent/workflows/heal-issues.md`, `.claude/commands/*`):

| Piece | Kind | One-liner |
| :--- | :--- | :--- |
| **`run-feedback`** | TIER 2 skill, hybrid | Capture/triage/file engine: stdlib CLI + LLM triage protocol + Retro Global Protocol |
| **`/heal-issues`** | workflow + command | Bounded self-healing over the issues ledger: pick ONE opted-in issue, re-prove red, fix on a branch under hard rails, flip status, never touch main |

## Component 1: the `run-feedback` engine

**CLI:** `python3 .agent/skills/run-feedback/scripts/run_feedback.py <subcommand>` — stdlib-only,
no venv, runs from anywhere inside the repo (walks up to the root).

| Subcommand | Does | Writes to |
| :--- | :--- | :--- |
| `collect` | Queue one finding (idempotent: repeated fingerprint → merge, `sources[]` union, exit 0) | inbox + journal |
| `triage` | Table of open findings + duplicate candidates (fingerprint + index-title overlap) | — (read-only) |
| `file` | `--as defect` → issue file + index line **lockstep with rollback**; `--as work-item` → backlog anchor append; `--as noise` → dismiss with reason. `--dry-run` previews ID + exact index line with ZERO writes | ledgers |
| `journal` | Append `## [ts] <event_type> \| <subject>` (flock+fsync, monthly rotation) | journal |
| `issues` | Ledger feed for the harness (`--status open --auto-fixable --json`) | — (read-only) |
| `mine` | Deterministic transcript extractor (tool errors, exit codes, envelopes, retry aggregation; redaction + excerpt caps; incremental byte offsets) | inbox |
| `claim` / `release` | Retro ownership for nested workflows (exit 6 = you are nested → skip retro) | `.agent/feedback/` |
| `doctor` | Readiness report `{v, ready, components, remediation}` | — (read-only) |

**Finding model:** the dedup `fingerprint` deliberately EXCLUDES the capture source, so a hook
capture and a transcript capture of the same failure collapse into one finding. Machine state
lives under gitignored `.agent/feedback/` (inbox/filed/dismissed + journal); the repo-visible
trace is the ledgers themselves plus heal reports.

**Judgement stays prompt-side** (SKILL.md §7): classification (defect / work-item / noise),
severity (`SEV-2/3/4/LOW` — write vocabulary owned by `known-issues-format`; reading tolerates
per-project extensions), and issue-body authorship. Every defect body MUST carry a fenced `sh`
`## Reproduction` block that exits non-zero while the bug exists — prose repros are not
auto-healable (see Component 3).

## Component 2: capture surfaces

| Surface | Portability | Mechanism |
| :--- | :--- | :--- |
| **Retro step** (Global Protocol) | Any vendor | Terminal workflows end with: `claim` → gather evidence (session state, failed/retried gates) → ONE question *"Что прошло НЕ гладко?"* → `collect` each signal → triage → file → `release`. Non-blocking by contract: a retro failure NEVER changes the workflow verdict. Nested workflows skip via `claim` exit 6. |
| **`/run-feedback`** | Any vendor | Ad-hoc collection in any session (no claim/release); `mine` hint runs the miner first. |
| **SessionEnd hook + mine-on-end** | Claude Code only, opt-in | `RUN_FEEDBACK_HOOKS=1` → the SessionEnd hook journals a session-end marker; `RUN_FEEDBACK_MINE_ON_END=1` → it also auto-mines the just-ended session's transcript into the inbox. Fail-silent; inbox-only; worktree captures land in the MAIN working tree. This is the **primary automatic capture path**. |
| **Transcript miner** | Claude Code only | `run_feedback.py mine` over `~/.claude/projects/<derived>/*.jsonl` — historical or scheduled sweeps; same noise policy and fingerprints as the hook path. |

Layering is explicit: the loop is COMPLETE with the portable surfaces alone; the Claude-Code
surfaces only raise recall.

## Component 3: the `/heal-issues` harness

`/heal-issues [issue-id] [--max-issues=K] [--dry-run] [--scheduled]` — full spec in
[`.agent/workflows/heal-issues.md`](../../.agent/workflows/heal-issues.md).

**Phases:** SELECT (run-lock, clean tree, base branch; eligibility = `status: open` AND explicit
`auto_fixable: true` AND attempts < 2 AND a configured gate exists) → REPRODUCE (fenced `sh`
blocks ONLY — never synthesized from prose; no runnable repro → `repro-blocked`, attempt NOT
consumed) → FIX (branch `fix/<id>-<slug>`, ≤3 iterations, gates re-run each iteration) →
VERIFY & FILE (ledger flip **in the same commit** as the fix + run report under
`docs/feedback/heal-reports/`) → REPORT (no silent outcomes).

**Hard rails (non-negotiable):**

| Rail | Effect |
| :--- | :--- |
| Branch-only | NEVER commits to the base branch, never pushes/merges/opens PRs — output is a PR-ready branch for HUMAN review |
| Explicit opt-in | `auto_fixable: true` is a human decision per issue; absence = not eligible (protects honest-scope/by-design entries) |
| Bounded everything | ≤3 fix iterations, ≤2 lifetime attempts per issue (then `needs-human`), K=1 issue per run by default |
| Repro contract | Red before fix (fenced block re-run in-run), green after — plus the component's own gates (unit / e2e / validator) with per-gate timeouts |
| Consumer-repo protocols | Replication rules (e.g. Universal-skills CLAUDE.md §2 master/replica), protected paths (LICENSE/NOTICE, settings, configs), diff guard (≤300 lines / ≤10 files), no new dependencies |
| Session hygiene | `RUN_FEEDBACK_HOOKS=0` for the whole run; surgical staging (explicit paths, never `git add -A`) |

**Human review loop:** `git branch --list 'fix/*'` → read the run report on the branch →
optionally re-run gates → merge (the ledger flip lands with the merge) → delete the branch.

## Setting up a consumer project

Start from the shipped templates — do not write the configs from scratch:

```sh
mkdir -p docs/feedback
cp .agent/skills/run-feedback/assets/templates/feedback_config_template.json docs/feedback/config.json
cp .agent/skills/run-feedback/assets/templates/heal_config_template.json     docs/feedback/heal-config.json
```

1. Install/update the framework (the installer symlinks the skill, workflow, and commands).
2. Fill `docs/feedback/config.json` — ledger paths, the `component→prefix` map (`_default`
   plus one row per component; every new prefix also gets a row in the ledger's
   prefix→category table — the engine warns), and the backlog anchor: either a heading from
   `backlog_section` or the explicit `<!-- feedback:discovered-issues -->` comment inside it
   (missing anchor → `file --as work-item` exits 4, never appends blindly).
3. Fill `docs/feedback/heal-config.json` — per-component **gates** map: only components with
   REAL checks (each command must exit 0 for `status: fixed`); declare `venv` only where one
   exists (a declared-but-missing venv makes the component ineligible); `replication` only
   where a master/replica protocol applies. Adjust `human_only_categories` and
   `protected_paths` to the repo; `scheduling: {enabled: false}` stays `false` in git.
   **No gate → not auto-fixable** — that is honest scope, not a gap.
4. Ensure the ledger exists per `known-issues-format` (create-if-absent from its template).
5. Optional Claude Code auto-capture: add the SessionEnd hook block to `.claude/settings.json`
   (see `run-feedback/references/capture_surfaces.md`) and set `RUN_FEEDBACK_HOOKS=1` +
   `RUN_FEEDBACK_MINE_ON_END=1` in personal `settings.local.json` `env`.
6. If `.agent/` is a real tracked tree in the project (it is in agentic-development itself),
   gitignore `.agent/feedback/` and `.agent/sessions/` explicitly.
7. Smoke: `run_feedback.py doctor --json` → `ready: true`; `/heal-issues --dry-run` → clean NO-OP.

## Operations: Stage 0 → Stage 1

- **Stage 0 (manual, mandatory first):** run `/heal-issues` by hand; a human reviews and merges
  every branch. Marking pilots `auto_fixable: true` is itself a human act. **Exit criterion:
  ≥3 consecutive runs whose branches merged without correction.**
- **Stage 1 (operator-side schedule, optional):** only after the gate — (1) close the headless
  permission gap (branch-switching git commands + every configured gate command must be
  allowlisted; an unattended run stalls on the first prompt); (2) flip
  `scheduling.enabled: true` in `heal-config.json` in a human commit; (3) create a user-level
  weekly scheduled task running `/heal-issues --scheduled` (e.g. Sat 09:00).
  **Kill-switches:** delete the scheduled task · `scheduling.enabled: false` (soft, survives
  task re-creation) · `git branch -D fix/...` (nothing ever leaves the machine).
- **Never repo-level cron/CI/git-hooks** for this loop, and the documented contract stays
  *manual invocation* — a schedule is an operator convenience, not a promise (honest-scope
  precedent: Universal-skills backlog xlsx-10 / review R2-H2 — never document automation whose
  runner may not exist).
- With an empty `auto_fixable` queue the harness NO-OPs politely — the system idles until the
  capture surfaces file new work; that is the intended steady state.

## Verified limitations

- **HK-1 (Claude Code 2.1.207, verified live 2026-07-13):** `PostToolUse` fires ONLY on
  successful tool calls and its payload carries no exit code — a per-command failure hook is
  impossible. Do NOT wire one; mine-on-SessionEnd is the automatic path.
  (`hooks/posttooluse_filter.py` is kept + tested for runtimes where such an event exists.)
- Old hand-authored issues without fenced repros are `repro-blocked` by design — add a
  verified-red fenced block (run it verbatim from the issue file before committing) to make
  them healable.
- Heal attempt counters live in gitignored `.agent/feedback/heal-state.json` — per-machine by
  design; a fresh clone re-tries (still bounded to 2) rather than the bot committing state to
  the base branch.

## Dogfood evidence

Rollout day (2026-07-13, Universal-skills + this repo):
- Historical harvest: 27 session transcripts → 91 candidates → 77 deduped findings → 2 filed
  (framework `SS-1`; one backlog work-item), 77 dismissed with per-bucket reasons.
- The loop healed its own host: `SS-1` (session state resolved relative to CWD) and `SS-2`
  (tracked `latest.yaml` dirtied the tree) were found by mining, filed by the engine, fixed
  same-day.
- Stage 0 gate: three pilot heals (`PDF-4`, `DOCX-MERMAID-EXECSYNC`,
  `XLSX-PREVIEW-PNG-ASSERT`), each fixed in **1 iteration** with all gates green, each
  ff-merged by the human without correction.

## Related documents

- [`.agent/skills/run-feedback/SKILL.md`](../../.agent/skills/run-feedback/SKILL.md) — the skill (Red Flags, Script Contract, triage + retro protocols)
- [`.agent/skills/run-feedback/references/`](../../.agent/skills/run-feedback/references/) — finding schema, CLI reference, capture surfaces, ledger contracts
- [`.agent/workflows/heal-issues.md`](../../.agent/workflows/heal-issues.md) — the harness spec
- [`.agent/skills/known-issues-format/SKILL.md`](../../.agent/skills/known-issues-format/SKILL.md) — the ledger contract (incl. optional automation keys)
- [`WORKFLOWS.md`](WORKFLOWS.md) · [`SKILLS.md`](SKILLS.md) · [`SESSION_CONTEXT_GUIDE.md`](SESSION_CONTEXT_GUIDE.md)
