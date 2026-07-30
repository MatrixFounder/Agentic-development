---
id: WI-6
type: work-item
status: done
opened_at: 2026-07-30
slug: wi-6-finding-accepts-any-path-and-consume-unlinks-it
effort: S
value: 'restores the documented write boundary'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: fa9fecf1f5b98f74
finding_ref: fnd-20260730-105029-fa9fecf1
resolved_at: 2026-07-30
resolved_by: TASK 093
---

# WI-6 — --finding accepts any path and consume unlinks it

> **✅ DONE 2026-07-30 (TASK 093).** Option 1: `inbox.resolve` accepts a bare path only when it
> resolves inside `inbox_dir`/`filed_dir`/`dismissed_dir`; anything else is exit 2 that **deletes
> nothing**. Id and filename resolution are untouched, and the E2E plus every existing test uses
> ids, so nothing in-tree relied on the old behaviour.
>
> Two details beyond the WI. `Path.resolve()` raises **`ValueError`**, not `OSError`, on an embedded
> NUL byte — that was an uncaptured iteration-2 finding (V-12 security) and is now caught, so
> `--finding $'fnd-\x00-nope'` is a clean CLI error instead of a traceback. And the error explains
> the *reason* rather than just refusing: filing **moves** the record, so an out-of-tree path would
> be unlinked — copy it into the inbox first.
>
> The generalized rule from this WI is now in `SKILL.md` §5 and `cli_reference.md`: a tool that
> documents "writes only inside X" must enforce containment on every path it **deletes or moves**,
> not only on the ones it creates.

> Origin: vdd-multi review of TASK 091/092 (2026-07-30), `critic-security` S-08. Pre-existing path,
> outside the TASK 091 diff. **Behaviour change for the owner's review.**

**Signal.** `--finding` accepts an arbitrary filesystem path: `inbox.resolve` returns any existing
file whose JSON has a `finding_id` and `status: new`. On success `inbox.consume` copies the record
into `.agent/feedback/filed/` and then **unlinks the original** — i.e. `file --finding
./somebody/state.json --as noise --reason x` deletes a file outside every configured ledger path,
which `SKILL.md` §5 says is the whole allowed write scope.

**Why it matters.** It is a footgun rather than an exploit (the operator supplies the path), but it
contradicts the documented boundary, and the deletion is silent and irreversible.

**Generalized.** A tool that documents "writes only inside X" must enforce containment on every path
it deletes or moves, not only on the ones it creates.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Require the resolved path to live under `inbox_dir`/`filed_dir`/`dismissed_dir` | XS | a deliberate out-of-tree finding needs a copy-in first |
| 2 | Keep the bare-path branch but never unlink outside the feedback dir | XS | leaves a copy behind, half-consumed |
| 3 | Document the behaviour instead | — | boundary claim stays false |

**Recommendation.** Option 1 — `resolve` already knows those directories.

**Acceptance.** `file --finding /etc/hosts` exits with a usage error and deletes nothing; normal
id/filename resolution is unaffected.

**Related.** `docs/reviews/vdd-multi-091-092.md` · `feedback_lib/inbox.py` · `run-feedback` SKILL.md §5.
