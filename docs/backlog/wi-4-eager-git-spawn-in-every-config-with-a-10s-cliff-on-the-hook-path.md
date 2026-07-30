---
id: WI-4
type: work-item
status: open
opened_at: 2026-07-30
slug: wi-4-eager-git-spawn-in-every-config-with-a-10s-cliff-on-the-hook-path
effort: S
value: 'removes a 10s stall risk from every hooked tool call'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: bfe2dc4364e03f1f
finding_ref: fnd-20260730-105029-bfe2dc43
---

# WI-4 — Eager git spawn in every Config, with a 10s cliff on the hook path

> Origin: vdd-multi review of TASK 091/092 (2026-07-30), `critic-performance` M-01 + I-06.

**Signal.** `Config.__init__` computes `data_root` eagerly via `subprocess.run(["git","rev-parse",
"--git-common-dir"], timeout=10)`. `data_root` is only needed by `feedback_dir` and its children, so
`doctor`, `issues`, `triage`, and every `--dry-run` pay a fork+exec they never use. The test suite
builds a `Config` per fixture (~150-250 spawns per run, plausibly a large share of its ~2s), and the
opt-in PostToolUse hook loads config on **every** hooked tool call — before the two cheap filters that
discard most events.

**Why it matters.** The tail risk, not the milliseconds: a stale `.git` file, a network/FUSE mount, or
index.lock contention blocks **every** run-feedback invocation for up to 10 seconds, including the
synchronous session hook. Fail-silent is not fail-fast.

**Generalized.** A constructor should not perform process-spawning I/O for a value most call paths
never read; and an expensive load must sit below the cheap discard filters, not above them.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | Lazy `data_root` property + module-level memo + `timeout=2` | S | none identified |
| 2 | Lazy only | XS | still one spawn per process |
| 3 | Nothing | — | 10s cliff stays on the hook path |

**Recommendation.** Option 1, plus moving `load_config` below the hook's early-exit filters.

**Acceptance.** `doctor` and `file --dry-run` spawn no `git`; the suite's wall-clock drops measurably;
a hung `git` cannot stall a hooked tool call for more than ~2s.

**Related.** `docs/reviews/vdd-multi-091-092.md` · `feedback_lib/config.py` · `hooks/posttooluse_filter.py`.
