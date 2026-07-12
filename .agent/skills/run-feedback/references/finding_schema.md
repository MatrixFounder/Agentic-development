# Finding schema v1

One JSON file per finding: `.agent/feedback/inbox/<finding_id>.json`, moved to `filed/` or
`dismissed/` on consumption (never deleted — audit trail).

```json
{
  "v": 1,
  "finding_id": "fnd-20260712-235321-614ee37f",
  "fingerprint": "614ee37f7fb28554",
  "status": "new",
  "captured_at": "2026-07-12T23:53:21+0300",
  "first_seen": "2026-07-12T23:53:21+0300",
  "last_seen": "2026-07-12T23:53:21+0300",
  "occurrences": 2,
  "sources": ["hook", "transcript"],
  "kind": "tool-error",
  "run": {
    "session_id": null, "task_id": null, "workflow": null,
    "phase": null, "step": null, "cwd": "/path",
    "extra": {"later_runs": []}
  },
  "subject": {
    "component": "transcript-fetcher",
    "command": "python3 fetch.py <url>",
    "exit_code": 7,
    "error_envelope": {"v": 1, "error": "...", "code": 7, "type": "MissingDependencyError"},
    "message": "redacted, human-oriented one-liner"
  },
  "evidence": {
    "paths": ["path/to/artifact"],
    "excerpts": [{"text": "redacted tail <= cap", "source": "hook", "path": "optional"}]
  },
  "proposed": {"classification": "defect", "severity": "SEV-3", "category": "robustness"},
  "filed_as": null
}
```

Field rules:

- `finding_id` = `fnd-<UTC-compact-ts>-<fingerprint[:8]>`; filename = `<finding_id>.json`.
- `fingerprint` = `sha256(component \x00 kind \x00 normalized_message)[:16]` where kind =
  `error_envelope.type` if present else `exit:<code>` else `unknown`. **The capture source is NOT
  in the preimage** — hook- and transcript-captures of one failure must collapse. Normalization:
  timestamps→`<ts>`, paths→`<path>`, hex≥8→`<hex>`, digits→`<n>`, lowercase, whitespace collapsed.
- `status` lifecycle: `new` → `filed` | `dismissed`. `filed_as` =
  `{"ledger": "issues"|"backlog", "id": "RF-3"|null, "path": "..."}`.
- `sources` is a union list, extended on every dedup-merge; `run` keeps the FIRST capture's
  context, later contexts append under `run.extra.later_runs`.
- `proposed.*` are capture-side hints ONLY — triage (the LLM) decides; enum
  `defect|work-item|noise|unknown`.
- `error_envelope` is the verbatim producer envelope when captured, never re-synthesized.
- All stored text (message, excerpts) is redacted (tokens/keys/emails) and length-capped.
