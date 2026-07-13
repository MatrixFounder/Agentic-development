# run_feedback.py — CLI reference

Global flags (before the subcommand): `--repo-root PATH`, `--config PATH`, `--json-errors`.

## collect — queue a finding (idempotent)

```
collect --source {workflow|skill|command|test|ci|hook|transcript}
        --kind {tool-error|gate-failure|test-failure|review-finding|blocker|repeated-failure|user-friction|session-end}
        --component NAME --message TEXT
        [--command CMD] [--exit-code N]
        [--error-envelope '<json>' | @path | -]      # verbatim {"v":1,...} stderr envelope
        [--session-id S] [--task-id T] [--workflow W] [--phase P] [--step N]
        [--context K=V]... [--evidence-path P]... [--excerpt-file P]
        [--propose {defect|work-item|noise|unknown}] [--severity SEV] [--category C]
        [--json]
```

Dedup: same fingerprint (component + failure kind + normalized message; SOURCE EXCLUDED on
purpose) → merge: `occurrences`+1, `sources` union, evidence paths union. Exit 0 either way.
Never touches ledgers. Message and excerpts are redacted; excerpts capped at
`excerpt_max_chars` (config, default 2000).

## triage — table + duplicate candidates

`triage [--json]` — one row per inbox finding: sources, kind, component, failure
(envelope type or `exit:N`), ×occurrences, message, dup candidates from
(a) `fingerprint:` frontmatter across `docs/issues/*.md`, (b) ≥2 shared ≥4-char tokens with an
index-line title. Classification is NOT automated — see SKILL.md §7.

## file — deterministic filing (create-only, lockable, dry-runnable)

```
file --finding <id|path> --as defect  --title T --category C [--severity SEV-2|SEV-3|SEV-4|LOW]
     [--prefix P] [--slug S] [--component C] [--auto-fixable] --body-file PATH|- [--dry-run] [--json]
file --finding <id|path> --as work-item --title T --body-file PATH|- [--effort E] [--value V] [--dry-run]
file --finding <id|path> --as noise --reason TEXT [--dry-run]
```

Defect: allocates `<PREFIX>-<n>` (prefix from `--prefix`, else config `id_prefixes[component]`,
else `_default`; tolerant of messy live IDs like `TF-X-7`/`XLSX-10B-DEFER`), writes
`docs/issues/<slug>.md` (contract frontmatter; optional keys `component/fingerprint/
evidence_paths/auto_fixable/finding_ref` AFTER `slug`) + the index line into the matching
`## <category>` section (created alphabetically; preamble untouched), lockstep with rollback.
Index seeded from the known-issues-format template when absent. Both writing paths run under
`.agent/feedback/.filing.lock`.

Work-item: bullet `- **<title> (<date>)** — <body>[ · Effort: E · Value: V]` inserted directly
after the configured `backlog_anchor` comment. Missing anchor → exit 4.

Noise: requires `--reason`; moves the finding to `dismissed/` and journals it.

## journal / issues / claim / release

- `journal --event-type T --subject S [--detail K=V]...` — append to
  `.agent/feedback/journal/YYYY-MM.md` (flock+fsync, monthly rotation).
- `issues [--status S] [--component C] [--auto-fixable] [--json]` — tolerant frontmatter feed,
  sorted by severity rank (unknown/missing → lowest) then age. The `/heal-issues` input.
- `claim --run-id ID` — exit 0 = you own the retro; exit 6 = nested, skip. TTL 24h (stale claims
  from crashed runs are overwritable). `release --run-id ID [--force]`.

## mine — transcript backfill

```
mine [--transcripts-dir D]... [--since YYYY-MM-DD] [--session UUID]
     [--include-active] [--frustration] [--limit N] [--dry-run] [--json]
```

Default dirs: every `~/.claude/projects/` entry whose decoded path is at/under the repo root
(Claude Code shards transcripts per-cwd — a session launched in `skills/html` lands in its own
dir). Incremental via byte offsets in `.agent/feedback/mine_state.json`; active sessions
(mtime < 10 min) skipped unless `--include-active`; ≥3 same-fingerprint failures in one session
collapse into a single `repeated-failure` candidate. `--dry-run` prints candidates, writes
nothing (no state, no inbox). First run on a repo: ALWAYS `--dry-run` and eyeball the yield.

## init — bootstrap configs from templates (create-only)

```
init [--json]
```

Copies `assets/templates/feedback_config_template.json` → `docs/feedback/config.json` and
`heal_config_template.json` → `docs/feedback/heal-config.json`. **Never overwrites** — existing
files are reported as `skipped`. Seeds `id_prefixes` from the existing ledger: for every
`docs/issues/*.md` with both `id:` and `component:`, the prefix is the id up to the first
`-<digit>` (`TF-X-7` → `TF-X`, `XLSX-10B-DEFER` → `XLSX`); a component with conflicting
prefixes is reported in `conflicts` and left unseeded. Output `{v, created, skipped,
seeded_prefixes, conflicts, todo}` — the `todo` list is the judgement the agent must finish
(backlog anchor, heal gates, prefix-table rows; SKILL.md §7 Bootstrap protocol). Exit 0; 3 when
the shipped templates are unreachable.

## doctor

`doctor [--json]` — `{v, ready, checks, remediation}`; exit 0 ready / 3 not. Checks: repo/data
roots, config source (built-in defaults → remediation suggests `init`), ledger paths, backlog
anchor presence, seed template reachability, feedback-dir writability.
