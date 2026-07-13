---
id: SS-2
type: known-issue
status: fixed
opened_at: 2026-07-13
resolved_at: 2026-07-13
resolved_by: direct fix 2026-07-13 (run-feedback dogfood, SS-2)
category: session-state
severity: SEV-3
slug: ss-2-session-state-latest-yaml-is-git-tracked-every-protocol-run-dirties-the-tree
component: skill-session-state
fingerprint: 42de547f667558c7
auto_fixable: true
finding_ref: fnd-20260713-110013-42de547f
---

# SS-2 — Session state latest.yaml is git-tracked — every protocol run dirties the tree

> **Resolved 2026-07-13.** `.gitignore` now ignores the whole `.agent/sessions/` runtime dir
> (replacing the lock-only line), `latest.yaml` untracked via `git rm --cached`, and
> `skill-session-state/SKILL.md` §1 documents the never-committed rule. Repro re-run: a
> protocol run leaves `git status` clean.

> Observed immediately after the SS-1 fix verification: the phase-boundary protocol run left
> ` M .agent/sessions/latest.yaml` in `git status` — the runtime state file is tracked.

**Symptom.** `.agent/sessions/latest.yaml` is committed to git while being per-machine runtime
state rewritten by every `update_state.py` call. Every phase boundary dirties the working
tree: PRs pick up state churn, and any clean-tree precondition (e.g. `/heal-issues` Phase 0)
is permanently tripped. The `.lock` sibling is already gitignored (line 8) — the yaml itself
was missed.

**Reproduction.**

```sh
cd <agentic-development-checkout>
python3 .agent/skills/skill-session-state/scripts/update_state.py \
  --mode Test --task t --status s --summary x
git status --porcelain .agent/sessions/   # " M .agent/sessions/latest.yaml" — BUG
```

**Workaround.** `git checkout -- .agent/sessions/latest.yaml` after protocol runs (loses the
persisted context the skill exists to keep).

**Fix path.** Ignore the whole runtime dir: replace the lock-only ignore with
`.agent/sessions/` in `.gitignore`, `git rm --cached .agent/sessions/latest.yaml`, and note in
`skill-session-state/SKILL.md` that session state is machine-local runtime data, never
committed. Session restoration is per-machine by design (SKILL.md bootstrap reads the local
file), so nothing depends on a committed copy.

**Related.** [[SS-1]] (same component, different defect: CWD anchoring); run-feedback VDD
review F2-core/F1-harness (tracked runtime files vs clean-tree preconditions).

**Do-not.** Do not keep a committed "seed" latest.yaml (stale state would be restored as if
current); do not auto-commit state from the protocol (unattended commits violate repo rules).
