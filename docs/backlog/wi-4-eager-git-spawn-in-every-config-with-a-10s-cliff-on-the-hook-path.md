---
id: WI-4
type: work-item
status: done
opened_at: 2026-07-30
slug: wi-4-eager-git-spawn-in-every-config-with-a-10s-cliff-on-the-hook-path
effort: S
value: 'removes a 10s stall risk from every hooked tool call'
source: 'vdd-multi task-091'
component: run-feedback
fingerprint: bfe2dc4364e03f1f
finding_ref: fnd-20260730-105029-bfe2dc43
resolved_at: 2026-07-30
resolved_by: TASK 093
---

# WI-4 — Eager git spawn in every Config, with a 10s cliff on the hook path

> **✅ DONE 2026-07-30 (TASK 093).** Option 1, minus the module-level memo.
> `Config.data_root` is now a lazy property with a **per-instance** cache, and
> `main_worktree_root`'s timeout dropped 10s → **2s**. `doctor`, `issues`, `triage` and every
> `--dry-run` now spawn **zero** `git`; the hook moved `load_config` **below** the `tool_name` and
> `should_capture` filters, so a discarded event costs no config read and no fork.
>
> Two decisions worth recording. **The per-instance cache is not an optimization but a correctness
> requirement**: `feedback_dir` is read many times per run, so an *uncached* lazy property would
> spawn `git` on every access — worse than the eager call it replaced. And the **module-level memo
> was dropped** (audit 093 Risk 3): once the property is lazy it buys nothing, while a cache keyed
> on a path outlives the temporary checkout it describes.
>
> The debug dump deliberately stays **above** the filters and pays for its own lazy load — it exists
> to diagnose *why* the filters discarded something, so moving it below them would have destroyed
> its only purpose. Pinned by `TestNoEagerGitSpawn` (a `subprocess.run` counter proving one spawn
> for five `feedback_dir` accesses, and zero for a plain config build) and
> `TestHookLoadsConfigOnlyWhenCapturing` (a non-Bash payload loads no config; debug mode still
> dumps it).

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
