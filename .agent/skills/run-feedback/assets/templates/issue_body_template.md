> Owning decision: [backlog row / task / review that defers or scopes this]. Remove if none.

**Symptom.** What is observably wrong, one paragraph. Quote the error message verbatim (redacted).

**Reproduction.**

```sh
# runnable commands only — /heal-issues executes this block verbatim (Phase 1).
# No prose steps; include cd/env setup; keep it offline-safe.
```

**Workaround.** How to live with it today. "None" is a valid answer.

**Fix path.** The concrete change that would resolve it (file paths, functions, approach).
If the fix is mechanical and verifiable by the component's gates, say so — that justifies
`auto_fixable: true` in the frontmatter.

**Related.** Sibling issues (`[label](…)`), backlog rows, review findings, finding_ref.

**Do-not.** Traps for the future fixer: approaches already tried and rejected, protocols that
MUST be honored (e.g. office replication masters), files that must not be touched.
