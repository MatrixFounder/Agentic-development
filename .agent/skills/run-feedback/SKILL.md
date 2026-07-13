---
name: run-feedback
description: 'Use when a run of a workflow, skill, command, or test produced errors or friction worth keeping, or when executing the end-of-run Retro Global Protocol — collect findings into the feedback inbox, triage them (defect / work-item / noise), and file defects into the known-issues ledger or work-items into the backlog. Triggers: "собери фидбек по прогону", "file run errors", "retro this run", "/run-feedback".'
tier: 2
version: 1.0
---
# Run Feedback

**Purpose**: Errors from runs evaporate today — a gate fails, gets retried, and the knowledge dies
with the session. This skill closes the loop: deterministic **capture** (retro step, hooks, transcript
miner) → LLM **triage** → deterministic **filing** into the existing ledgers (`docs/issues/` +
`docs/KNOWN_ISSUES.md` per `known-issues-format`, or the project backlog). Filed issues marked
`auto_fixable: true` feed the `/heal-issues` harness. Machine state lives under the gitignored
`.agent/feedback/`; the repo-visible trace is the ledgers themselves.

## 1. Red Flags (Anti-Rationalization)
**STOP and READ THIS if you are thinking:**
- "I'll append a line to KNOWN_ISSUES.md without creating the issue file" -> **WRONG**. Lockstep or
  nothing — the `file` subcommand writes both or neither. Never hand-edit one side.
- "This finding is obviously a dup, I'll file it anyway for completeness" -> **WRONG**. A duplicate
  goes to `--as noise --reason "duplicate of <ID>"`; the recurrence is already counted by the
  fingerprint merge.
- "I'll classify straight from the inbox JSON without running `triage`" -> **WRONG**. Dup candidates
  come from the script (fingerprint + title overlap). Eyeballing misses them.
- "I'll invent severity `HIGH` / status `handled` for a new issue" -> **WRONG**. The write vocabulary
  is owned by `known-issues-format` (`SEV-2/3/4/LOW`; `open/fixed/documented/by-design/mitigated/wontfix`).
  Reading tolerates local extensions; writing never emits them.
- "The filing is simple, I'll skip `--dry-run`" -> **WRONG**. Dry-run first, always — it previews the
  allocated ID and the exact index line; a mis-filed ID pollutes a hand-maintained ledger.
- "I'll edit a finding JSON in the inbox by hand" -> **WRONG**. Only the CLI mutates inbox state;
  hand edits break fingerprint dedup and the audit trail.
- "The retro step failed, I should retry it / fail the workflow" -> **WRONG**. The retro is
  non-blocking by contract: report one line and move on; it NEVER changes the calling workflow's verdict.

## 2. Capabilities
- Queue findings from any surface (`collect`) with cross-source dedup by fingerprint.
- Prepare a triage table with duplicate candidates (`triage`).
- File defects into `docs/issues/` + `KNOWN_ISSUES.md` in lockstep, work-items into the backlog
  anchor, dismiss noise — all create-only, dry-runnable (`file`).
- Mine historical Claude Code session transcripts for failures (`mine`).
- Deterministic retro ownership for nested workflows (`claim` / `release`).
- Feed the self-heal harness (`issues --status open --json`).

## 3. Execution Mode
- **Mode**: hybrid.
- **Why this mode**: capture, dedup, filing, journaling are deterministic file mutations (script-first,
  per SKILL_EXECUTION_POLICY §5); classification, severity, and issue-body authorship are judgement
  (prompt-side, §7 below).

## 4. Script Contract
- **Command**: `python3 .agent/skills/run-feedback/scripts/run_feedback.py <subcommand> …`
  (stdlib-only; no venv; run from anywhere inside the target repo, or pass `--repo-root`).
- **Subcommands**: `collect · triage · file · journal · issues · mine · claim · release · doctor`
  — full flag reference in [`references/cli_reference.md`](references/cli_reference.md).
- **Config**: `docs/feedback/config.json` per repo (ledger paths, `component→prefix` map, backlog
  anchor). Resolution: `--config` → `RUN_FEEDBACK_CONFIG` env → repo default → built-ins.
- **Exit codes**: `0` ok (incl. dedup) · `1` unexpected · `2` usage · `3` config/env (also
  `doctor` not-ready) · `4` filing conflict (slug exists, vocab violation, missing backlog anchor) ·
  `5` finding not found · `6` claim denied.
- **Failure semantics**: with `--json-errors`, failures emit one JSON line
  `{"v":1,"error",…,"code",…}` on stderr; exit code equals `code`.
- **Idempotency**: `collect` is fire-and-forget safe — a repeated fingerprint merges
  (`occurrences`+1, sources union) and exits 0. `file` is create-only and conflicts loudly.
- **Dry-run**: `file --dry-run` previews ID, paths, and the exact index line with ZERO writes.

## 5. Safety Boundaries
- **Allowed scope**: writes ONLY to `.agent/feedback/**` (machine state, gitignored) and — from
  `file` exclusively — the configured `issues_dir`, `index_path`, `backlog_path`.
- **Create-only ledger writes**: never edits or deletes an existing issue file or index line;
  resolving/flipping statuses belongs to humans or `/heal-issues` under `known-issues-format` rules.
- **Lockstep**: issue file written first; if the index write fails the issue file is rolled back.
- **No network, no secrets**: excerpts are redacted (tokens/keys/emails) and hard-capped before
  they are stored; transcripts are read locally and never scanned beyond tool errors (+ opt-in
  frustration markers).
- **Hooks are opt-in and fail-silent**: `RUN_FEEDBACK_HOOKS=1` required; a broken feedback path
  must never break a session (`|| true; exit 0`).

## 6. Validation Evidence
- **Local verification**: `cd .agent/skills/run-feedback/scripts && python3 -m unittest discover -s tests`
  (fingerprint stability, messy-ID allocation, index placement regression, lockstep rollback,
  dry-run tree-hash, journal multiprocess hammer, miner fixtures) and `bash tests/test_e2e.sh`
  (zero-test guard + scripted pipeline in a mktemp repo).
- **Expected evidence**: green suite; `doctor --json` reports `ready: true` in a configured repo.
- **Contract sync**: `python3 ../known-issues-format/scripts/check_contract_sync.py` stays green.

## 7. Instructions

### Triage protocol (the core judgement loop)
1. **MUST** run `triage` first — the table carries dup candidates you cannot see from raw JSON.
2. For every dup candidate, open the referenced issue file. Genuinely the same defect → do NOT
   file; dismiss with `--as noise --reason "duplicate of <ID>"` (the fingerprint merge already
   recorded the recurrence).
3. Classify each remaining finding:
   - **defect** — reproducible wrong behavior with a fix path → issues ledger;
   - **work-item** — enhancement / polish / signal without a broken contract → backlog;
   - **noise** — transient environment, operator error, already-fixed → dismiss with a reason.
4. For defects: severity strictly from `SEV-2/SEV-3/SEV-4/LOW`; category from the ledger's
   prefix→category table; author the body from
   [`assets/templates/issue_body_template.md`](assets/templates/issue_body_template.md)
   (Symptom / Reproduction / Workaround / Fix path / Related / Do-not), citing `evidence` paths.
   **MUST** make `## Reproduction` a fenced `sh` block with runnable commands — it is the input
   `/heal-issues` executes; prose repros are not auto-healable.
   Add `--auto-fixable` ONLY when the fix is mechanical and gate-verifiable — this is the explicit
   opt-in the heal harness selects on.
5. **MUST** run `file … --dry-run`, read the previewed ID + index line, then run for real.
6. Finish by reporting filed IDs, dismissed counts, and any new prefix that needs a row in the
   ledger's prefix→category table (the script warns; the table edit is yours).

### Retro protocol (Global Protocol — end of every terminal workflow)
1. **Claim**: at workflow START run
   `run_feedback.py claim --run-id "<workflow>-<task-slug>"`. Exit 6 → another workflow owns this
   run's retro → SKIP the retro step entirely (you are nested).
2. At workflow END (owner only), gather evidence — `.agent/sessions/latest.yaml` blockers, gates
   that failed or retried this run, fresh `docs/reviews/coverage-*` artifacts — and ask the user ONE
   question: *"Что прошло НЕ гладко в этом прогоне?"* with the observed candidates pre-listed.
   Non-interactive runs proceed with observed signals only.
3. `collect` each signal (`--source workflow --kind gate-failure|test-failure|review-finding|blocker|user-friction`,
   with `--workflow`, `--task-id`, `--phase` context). Then run the Triage protocol above.
4. **Release**: `run_feedback.py release --run-id "<same id>"`.
5. **Non-blocking guarantee**: any failure inside this protocol → report one line, continue the
   workflow's normal completion. Never retry-loop the retro, never change the workflow verdict.

### Ad-hoc (`/run-feedback` command)
Same as the retro protocol without claim/release: gather friction from the CURRENT session (failed
commands, retries, blockers), scoped by the user's hint; `mine` first when the hint says so.

## 8. Workflows
```markdown
- [ ] claim (workflow start, terminal workflows only)
- [ ] collect observed signals + the one retro question
- [ ] triage → classify → dry-run → file
- [ ] release + one-line report
```

## 9. Best Practices & Anti-Patterns

| DO THIS | DO NOT DO THIS |
| :--- | :--- |
| `file --dry-run` before every real filing | Hand-edit `KNOWN_ISSUES.md` or inbox JSON |
| Dismiss duplicates with the original's ID in the reason | File a second issue for a known fingerprint |
| Runnable fenced `sh` repro in every defect body | Prose-only "point the tool at a slow source" repros |
| Mark `--auto-fixable` only for mechanical, gate-verifiable fixes | Mark honest-scope / design decisions auto-fixable |

### Rationalization Table
| Agent Excuse | Reality / Counter-Argument |
| :--- | :--- |
| "The inbox item is obviously noise, I'll just delete the JSON" | Dismissal is `file --as noise --reason …` — it journals and keeps the audit trail. |
| "I remember this issue already exists, no need to check" | Run `triage`; fingerprints and title-overlap candidates are computed, not remembered. |
| "The retro question annoys the user, I'll skip asking" | One question per run, pre-filled — that's the contract. Skipping loses the only human-signal channel. |
| "Exit 6 from claim is an error I should fix" | Exit 6 = you are NESTED. Skipping the retro is the correct behavior, not a failure. |

## 10. Examples (Few-Shot)
See [`examples/usage_example.md`](examples/usage_example.md) for a full capture→triage→file walk.

**Input:** a workflow's coverage gate failed twice, then passed after a fix.

**Output (abridged):**
```sh
python3 .agent/skills/run-feedback/scripts/run_feedback.py collect \
  --source workflow --kind gate-failure --component vdd-multi \
  --message "coverage gate failed 2x: security critic timeout" \
  --workflow full-robust --phase "Step 2" --context task=task-089
```
…then `triage`, classify as defect, `file --dry-run`, `file`.

## 11. Resources
- `scripts/run_feedback.py` — the CLI (see §4); `scripts/feedback_lib/` — the engine modules.
- `scripts/hooks/` — opt-in Claude Code SessionEnd capture: session-end marker +
  auto-mine of the ended session (`RUN_FEEDBACK_HOOKS=1` + `RUN_FEEDBACK_MINE_ON_END=1`). See
  [`references/capture_surfaces.md`](references/capture_surfaces.md) for the layering (retro step =
  portable; hooks/miner = Claude-Code-only accelerators) and the verified PostToolUse limitation
  (fires only on SUCCESSFUL tool calls — cannot capture failures; do not wire it).
- `assets/templates/issue_body_template.md` — defect body skeleton.
- `assets/templates/feedback_config_template.json` + `heal_config_template.json` — per-repo
  config starters for new consumer projects (copy into `docs/feedback/`, then fill the
  prefix map and gates; recipe: `System/Docs/QUALITY_FEEDBACK_LOOP.md` §Setup).
- `references/finding_schema.md` — Finding v1 field-by-field spec.
- `references/cli_reference.md` — full flag reference per subcommand.
