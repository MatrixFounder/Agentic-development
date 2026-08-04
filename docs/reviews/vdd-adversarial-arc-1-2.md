# VDD Critique: ARC-1 / ARC-2 archive-protocol fixes

**Date:** 2026-08-04 · **Method:** `/vdd-adversarial`, 5 fresh-context critics + per-finding
refutation pass (90 agents, 5.6M tokens)

## 1. Executive Summary

- **Verdict**: **FAIL on first pass** → **PASS after three rounds of remediation**
- **Confidence**: High for what was executed; the record below shows the confidence was misplaced
  twice.
- **Summary**: Three of five critics returned FAIL. 85 raw findings, **75 survived** independent
  refutation, 6 refuted, 4 unjudged (agent API errors). Five HIGH findings were real, and the worst
  of them was a regression **introduced by the fix run itself**.
- **Each round found what the previous one closed too early**: round 2 found ARC-1 still live in
  four documented call sites; round 3 found a HIGH that round 1 had explicitly refuted. Every one
  surfaced by *running* the documented artifact rather than reading it. Both prior rounds ended
  with all gates green.

## 2. Risk Analysis — the five HIGH findings

| Severity | Category | Issue | Impact | Status |
| :--- | :--- | :--- | :--- | :--- |
| **HIGH** | data-corruption | Mutable-slot handling was **opt-in**. An unmapped slot reference took the ordinary rebase branch and was silently rewritten, exit 0. | Converts a dead link into a confidently wrong one, invisible to any link checker because it resolves. | **Fixed** — `KNOWN_SLOTS` is intrinsic; unmapped → `UNMAPPED_SLOT`, never rewritten, exit 3. |
| **HIGH** | regression-by-the-fix | `docs/plans/plan-061:3` was rewritten to `../TASK.md`, which resolves to **TASK 096**. A plan for Task 061 cited an unrelated task as its parent. | Immutable history corrupted by the run that shipped the fix. | **Fixed** — reverted to the authored (dead) form. Task 061 has no parent archive, so there is nothing correct to point at. |
| **HIGH** | correctness | `archive_task` mapped the PLAN slot **unconditionally**, including for tasks that never reached planning. | Authors a citation to a `plan-NNN-*.md` that Step 7 will never create, and reports success. | **Fixed** — mapped only when `docs/PLAN.md` exists. |
| **HIGH** | identity-corruption | The new language-agnostic meta fallback picked rows by value shape: `\| Дата \| 2026 \|` became the Task ID and `\| Статус \| in-progress \|` became the slug. | Archives as `task-2026-in-progress.md` and poisons `find_next_available_id` for every later auto-generation. | **Fixed** — exactly-3-digit id, slug is the row immediately after it, **ambiguity refuses instead of guessing**. |
| **HIGH** | doc-code-mismatch | `SKILL.md` Step 7.6.5 documented `--slot docs/TASK.md=docs/tasks/{used_id}-{slug}.md` — missing the `task-` prefix. | An agent following the protocol verbatim writes a permanently dead link; the tool exits 1. | **Fixed** — prefix restored; both forms verified by execution. |

> **CORRECTION (round 3, 2026-08-04).** This section previously recorded one reported HIGH as
> *not reproducing*: "Step 5.5's documented command exits 1 on the happy path." **The critic was
> right and the refutation was wrong.** The refutation measured `rebase_links.py` *without*
> `--slot`, which is not the documented command. Run as written — with
> `--slot docs/PLAN.md=docs/plans/plan-NNN-x.md` — Step 5.5 exits **1** ("a link regressed")
> because the conservation law probed a target that Step 7 has not created yet. Fixed in round 3;
> see §7.
>
> The refutation failed the same way the original fix did: it tested a command adjacent to the one
> in the document rather than the one in the document.

## 3. What the review cost, and what it bought

The adversarial pass found a defect I had shipped **while fixing the defect it is named after** —
`rebase_links.py` docstring states that preserving the path "would re-point the citation at whatever
task is current", and the unguarded branch then did exactly that. No test covered the unmapped case:
all four slot tests passed a slot map. That is the class of error a self-review cannot reach, and it
is the argument for the fresh-context rule.

## 4. Remediation evidence

| Gate | Before review | After remediation |
| :--- | ---: | ---: |
| CI invocation (`framework-gates.yml` list) | 300 passed | **311 passed** |
| `.agent/tools/` suites | 86 | **97** |
| `tests/run_tests.py` | 302 OK | **302 OK** |
| Archived docs resolving to a live slot | 5 | **4** (all pre-existing, none authored by this work) |

New regression pins: `TestUnmappedSlot` (5 cases), `TestMetaFallbackStructural` (5 cases),
`TestPlanSlotIsConditional` (1 case).

End-to-end re-verified: a task with sub-tasks and no parent archive still archives as **095**, and
both slot links resolve to archive identities rather than to the live slots.

## 5. Hallucination Check

- [x] **Files**: every cited path confirmed present.
- [x] **Line numbers**: each HIGH finding re-reproduced by the orchestrator independently of the
      critic, by execution rather than by reading.
- [x] **Refuted claims discarded**: 6 findings failed refutation and are not carried here.
- [ ] **One refutation was itself wrong.** The "Step 5.5 exits 1" claim was recorded as measured
      false; round 3 reproduced it by running the documented command. A refutation is a measurement
      and can be defective like any other — this checklist did not catch that, and the box stays
      unticked as the standing reminder.

## 6. Second round — 2026-08-04

A second pass was run over the remediated changeset. **It found four more real defects, and one of
them was ARC-1 itself, still live.** The method that produced them was not re-reading the diff: it
was executing every documented entry point and measuring every claim the artifacts make.

| Severity | Issue | Evidence | Status |
| :--- | :--- | :--- | :--- |
| **HIGH** | ARC-1 was closed with four of five documented call sites still teaching it | bare form → **096**, protocol form → **095**, same fixture | **Fixed** in 4 files + analyst prompt |
| **MED** | `schemas.py` advertised `allow_correction: default true` to the model | dispatcher used `False` since the ARC-1 fix | **Fixed**, pinned to the dispatcher |
| **MED** | `rebase_links` code-span mask hid 3 real links | mask closed on a prefix of a longer backtick run, and spanned blank lines | **Fixed**, 6 boundary cases added |
| **MED** | `tests/run_tests.py` (302 tests, incl. all of `tests/installer/`) ran in no CI job | only one pytest list is invoked by `framework-gates.yml` | **Fixed**, added as its own step |
| LOW | review cited **WI-33** for a work-item filed as **WI-11** | — | Fixed |
| LOW | `task-095:63` wrote a repo-root path as a relative link | file exists at `docs/design/…`; link resolved nowhere | Fixed |
| LOW | `.agent/archive/*.bak` untracked and un-ignored | `git status` dirty after every `/framework-upgrade` | Fixed via `.gitignore` |

**Two of my own candidate findings were refuted by follow-up measurement**, and are recorded
because the refutation is the useful part:

- *"The code-span mask hides 16 real links."* It hides 16 link-shaped strings, of which **13 are
  documentation of link syntax** — `` `[Ref](src/main.py)` `` and kin. Masking those is correct.
  Only 3 were real. The fix was scoped to those 3 and verified not to un-mask the 13.
- *"`_INLINE` matching `](x)` without a preceding `[` is a rewrite hazard."* All 8 corpus instances
  sit inside code spans and disappear once the mask is correct. Tightening the regex changes 2
  findings repo-wide, both `#anchor` targets already dropped as absolute. Kept loose, on the
  measurement, with the reasoning recorded at the definition.

### What the two rounds have in common

Round 1: a slot rewriter that knew about slots only when told. Round 2: a fix verified only at the
site where it was written. Both are the same error — **a guard that depends on the caller
remembering it, and a check that stops at the edge of the diff.**

### Verification

| Gate | Round 1 close | Round 2 close |
| :--- | ---: | ---: |
| CI pytest list | 311 | **320** |
| CI unittest suite | not run | **302** |
| `.agent/tools/` | 97 | **106** |
| Broken relative links, repo-wide | 22 | **21** |
| Archived docs resolving to a live slot | 4 | **4** (all pre-existing) |

End-to-end re-run with a fully Cyrillic meta block (`Идентификатор` / `Слаг`): archived as
**095** beside its three sub-tasks, slug transliterated, and the one relative link rebased to
`../ARCHITECTURE.md`. Rebase idempotency re-confirmed: **0 rewritten** on a second pass over both
`docs/tasks/` and `docs/plans/`.

## 7. Third round — closing WI-11

Triggered by "close WI-11", executed under this file's own rule: **execute each entry, do not read
it.** Ten tail entries; **six confirmed and fixed, four refuted.**

| Entry | Verdict | Evidence |
| :--- | :--- | :--- |
| **Step 5.5 exits 1 on the documented happy path** | **HIGH — confirmed** | Found by *running* the rewritten Example Flow. The conservation law probed a `SLOT_RESOLVED` target; a slot map is a forward reference Step 7 fulfils later. Exit 1 reads as "stop". |
| Escaped pipe hides an over-wide cell | Confirmed | 200-char cell containing `\|` → no finding |
| U+2028 shifts reported line numbers | Confirmed | reported line 4, real `\n`-line 3 |
| Duplicate `--rules` double-counts | Confirmed | 1 info → 2 info for the same document |
| Leading `---` eaten as frontmatter | Confirmed | `---\n\n# Title\n\n<prose>` scanned to **zero** findings |
| `e.g. Capital` splits a sentence | Confirmed | 12 corpus instances; halves the measured length |
| `selftest_scan.py` not in CI | Confirmed | now its own workflow step |
| Stray backtick "masks the rest of the line" | **Refuted** | pairing is CommonMark-correct; a truly unmatched backtick masks nothing |
| Decimals split sentences | **Refuted** | `1.5 Beta` has no whitespace after the period — the rule never fired |
| `__pycache__` untracked | **Refuted** | already in `.gitignore`; 0 tracked |

The Step 5.5 defect is the one that matters, and it is the same lesson a third time: it surfaced
only because the stale `Example Flow` was rewritten and then **executed**. Reading the protocol
would not have found it — the commands are correct, the tool's verdict on them was not.

### Red-state evidence for the pins

A regression pin that passes against the unfixed code is decoration. The scanner's nine new pins
were run against a reconstructed pre-fix scanner: the **five confirmed defects fail**, the **four
refuted/invariant pins pass both** — which is exactly the shape they should have. (The first
attempt at this check produced "all nine fail" from a scratch copy with a syntax error; a broken
instrument and a real signal look identical, so the copy was rebuilt and re-verified to parse and
run first.)

### Verification

| Gate | Round 2 | Round 3 |
| :--- | ---: | ---: |
| CI pytest list | 320 | **324** |
| CI unittest suite | 302 | **302** |
| `.agent/tools/` | 106 | **110** |
| `artifact-formalizer` selftest | 38 | **47**, then blocked — see below |

**One number in this table stopped being true while the round was running.** `scan_register.py`
was replaced mid-session with a rewrite that requires a `probe` field on every rule entry;
`data/register-{en,ru}.json` still carry the previous schema, so the scanner now exits 2 on its own
rules and the battery cannot run. The five precision fixes were re-verified against the rewrite by
exercising its detectors directly — all five are present. The 47 figure was measured before the
replacement and is recorded as such rather than restated as current.

## 8. Not addressed in any pass

Round 2 took the doc-drift group (it contained a live ARC-1), the CI hole, and the hygiene items.
What remains in **WI-11**: `skill-archive-task` frontmatter still `version: 1.3` and its stale
`Example Flow`; `selftest_scan.py` not wired into CI; and the `artifact-formalizer` scanner's
precision nits (escaped pipes, U+2028 line separators, duplicate `--rules` double-counting, a
stray backtick, the frontmatter mask keying on a leading `---`). None corrupts data.

That judgement is worth distrusting, though — it was made about the doc-drift group too, and one
member of that group was ARC-1 still live. The triage had read the docs rather than run them.
**Before closing any WI-11 entry, execute it.**
