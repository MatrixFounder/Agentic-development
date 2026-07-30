---
id: WI-5
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-5-find-by-fingerprint-rescans-the-whole-inbox
effort: S
value: 'turns a cumulative O(k^2) capture path into a glob'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: e783fb537a196b12
finding_ref: fnd-20260730-105029-e783fb53
---

# WI-5 — find_by_fingerprint rescans the whole inbox

> Origin: vdd-multi review of TASK 091/092 (2026-07-30), `critic-performance` M-02.

**Signal.** `inbox.find_by_fingerprint` opens and `json.loads` **every** file in the inbox to find one
record — while the fingerprint's first 8 hex chars are already **in the filename**
(`fnd-<ts>-<fp[:8]>.json`). It runs under an exclusive lock, so concurrent captures serialize behind
the full scan.

**Why it matters.** The inbox drains only when a human triages. A run capturing *k* findings without
triage does 1+2+…+k reads — cumulative **O(k²)**. At 200 stale findings that is ~20,100 file reads
and JSON parses to answer 200 yes/no questions, all inside the capture path meant to be
fire-and-forget.

**Generalized.** If a lookup key is encoded in the filename, the lookup is a glob, not a scan; and a
queue with no depth signal is how "it got slow" becomes a mystery.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | `glob("fnd-*-<fp8>.json")` + verify the FULL fingerprint on candidates | XS | none — prefix collisions still handled correctly |
| 2 | Add an index file | M | a second source of truth to keep in sync |
| 3 | Nothing | — | O(k²) grows with triage laziness |

**Recommendation.** Option 1 (behaviour-preserving), plus an inbox-depth line in `doctor`.

**Acceptance.** A capture into an inbox of 200 findings reads ~1 file, not 200; dedup behaviour
unchanged (a test with a colliding 8-char prefix still merges correctly).

**Related.** `docs/reviews/vdd-multi-091-092.md` · `feedback_lib/inbox.py` · `feedback_lib/finding.py`.
