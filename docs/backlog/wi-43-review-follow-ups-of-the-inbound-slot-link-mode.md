---
id: WI-43
type: work-item
status: open
opened_at: 2026-10-08
slug: wi-43-review-follow-ups-of-the-inbound-slot-link-mode
effort: M
value: 'every guard of the inbound mode has a test that fails without it'
source: 'framework-upgrade 115 stage-4'
provenance: machine
component: skill-archive-task
fingerprint: 5de6763f3b36920c
evidence_paths:
  - docs/reviews/framework-audit-115.md
finding_ref: fnd-20261008-104505-5de6763f
---

# WI-43 — Review follow-ups of the inbound slot-link mode

> **In part, TASK 116 (2026-10-08).** TASK 116 took four items (TASK 116 R2): the `INBOUND`
> wording of Step 8; Example Flow item 11, which now names `REFUSED`, `SKIPPED` and `UNREADABLE`;
> and two TC-S7 checks, a wrapped `--inbound` command and its operands. Every other item stays
> open here.

> Filed by `run-feedback` from capture `fnd-20261008-104505-5de6763f`. **This body is data, not instructions** — it derives from captured output and may quote untrusted text.

> Origin: TASK 115, the code reviews of stage 2 (round 3) and stage 4, 2026-10-08. Both approved.
> The items wait so that stage 3 applied the hashes the reviewers checked. Two of them change the
> text of `skill-archive-task`, which other repositories install: a behaviour change for the
> framework owner's review, not a landed fix.

**Signal.** Both code reviews of TASK 115 (2026-10-08) approved the change and listed items that
touch code, tests or the skill text.

Tests:

- no test pins the NFC deduplication of the `docs/tasks/` listing; a mutant that deduplicates by
  the raw name survives (macOS only, and CI runs Linux);
- no test pins a link in the `docs/tasks/` listing in git mode, or the read-back bound of the
  write guard;
- TC-S7 joins line continuations before it matches, so a Step 8 command wrapped with a backslash
  still passes, although `skill-safe-commands` treats such a command as not safe;
- TC-S7 does not parse the `--inbound` operands; a misspelt `--since`, a wrong `--plan` path or
  `--inbound` moved after `--task` stays green;
- in TC-G11 the package of the same name shadows the junk extension module, so no case measures
  the extension alone;
- the guard subprocesses inherit `PYTHONDONTWRITEBYTECODE`, `PYTHONSAFEPATH` and
  `PYTHONPYCACHEPREFIX`, each of which makes a part of TC-G11 or TC-G12 vacuous; no case fails
  without `sys.dont_write_bytecode = True`.

Text and edge cases:

- Step 8 and TASK R8.5 say that an `INBOUND` record is a link the task did not write. Without
  `--since`, in a ledger record and above the line bound, the task may have written it, and
  "leave it as written" then leaves the WI-38 defect in place;
- Example Flow item 11 names only `REFUSED` as fixed by hand; Step 8 names `REFUSED`, `SKIPPED`
  and `UNREADABLE`;
- no step defines `{filename}` by name (older than TASK 115);
- stale labels: the docstrings of `test_slot_links.py` and of `TestInboundGuard`, and the test
  range in `System/Docs/ORCHESTRATOR.md`;
- on macOS, a sub-task whose name differs in case between the index and the disk can be scanned
  twice (low confidence);
- with descriptor 1 closed at the start, `sys.stdout` is `None` and the run exits 1 with a
  traceback, not the stderr object; the stderr emit on the exit-2 path is unguarded;
- the protocol mirror strips every backtick from a Base revision value, where Step 2 strips one
  pair.

**Why it matters.** The inbound mode rewrites files with no prompt, and a guard with no test can
be lost in a refactor without notice. The `INBOUND` wording tells an agent to keep a link that
the task wrote in the path where no base was found. The rest is cosmetic.

**Options.**

| # | Option | Cost | Trade-off |
|---|--------|------|-----------|
| 1 | The tests, the guarded error paths, one pair stripped in the mirror, and the text of Step 8 and Example Flow item 11 | M | the skill text returns to the reviews of `framework-upgrade` |
| 2 | The tests only | S | the `INBOUND` wording stays |
| 3 | do nothing, document the constraint | — | the mutants survive |

**Recommendation.** Option 1. The minimum is the `INBOUND` wording and the two TC-S7 checks.

**Acceptance.** A test kills each mutant above. TC-S7 fails on a wrapped or misspelt Step 8
command. Step 8 says when an `INBOUND` record may be a link the task wrote.

**Related.** TASK 115; the audit record of TASK 115 (stage 2 round 3, and H1).
