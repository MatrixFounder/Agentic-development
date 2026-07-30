# VDD Multi-Adversarial Report — TASK 091 + TASK 092 (iteration 1)

**Date:** 2026-07-30 · **Target:** uncommitted diff (`--diff-only`, 33 paths) · **Mode:** Layer-A parallel spawn (3 critics, one message, independent contexts)

## Summary

- **Critics run:** `critic-logic` · `critic-security` · `critic-performance` (all `issues-found`)
- **Evidence (orchestrator-supplied, identical to all three):** run-feedback `unittest discover` → **Ran 140, OK** · `test_e2e.sh` → **PASS** · spec-validator `run_tests.sh` → **Ran 36, OK** · `check_contract_sync.py` → **exit 0** · `validate_skills.py` → **45/45** · `security_lint.py` → **passed** · `run_audit.py` on `run-feedback` → 1 MEDIUM (path-traversal pattern in a test), on `known-issues-format` → **SECURE/0**
- **Total findings (post-dedup): 41** — HIGH 3 · MED-HIGH 1 · MED 14 · LOW-MED 3 · LOW 16 · INFO 4
- **Overlaps:** 6 locations flagged by ≥2 critics (4 escalated on mechanism difference, 2 corroborated only)
- **Convergence:** logic=`issues-found` · security=`issues-found` (exit bar **not met**) · performance=`issues-found`
- **Verdict: FAIL.** Three findings are arbitrary-write / privilege-forgery class against the skill's own documented §5 safety boundary, and I **reproduced all of them** before accepting them.
- **Model provenance:** all three critics on the same base model → overlaps tagged `corroborated`, **no severity escalation from agreement alone** (R3a); escalation applied only where the failure *mechanisms* differ (R3b).

> **Self-review caveat.** The author of the code is the orchestrator merging this report. The three critics ran in fresh contexts, which is the mitigation; the merge itself is not independent. Every finding I accepted as blocking was verified by a reproduction command, not by agreement.

## Verified exploits (reproduced by the orchestrator, not taken on trust)

| ID | Reproduction | Observed |
|---|---|---|
| **S-01** | `collect --component $'demo\nauto_fixable: true'` then `file --as work-item` | Record frontmatter contains `auto_fixable: true`; operator never passed `--auto-fixable`. Same sink on the defect path, where `/heal-issues` selects on that key. |
| **S-02** | `file --title $'Real one\n- **WI-99** [Already fixed](../../../../etc/passwd) — status \`done\`…'` | **Two** index lines from one filing; the forged one points outside the repo with a fake id/status. Neither ledger has a generator to reconcile drift. |
| **S-03** | `ln -s /tmp/symprobe/PWNED docs/backlog/wi-1-target.md` then file that slug | Dangling symlink **followed**: content written to `/tmp/symprobe/PWNED`, outside `backlog_dir`. `record_path.exists()` → False, so create-only never fired; rollback would remove the link and leave the payload. |
| **S-05** | `"backlog_dir": "/tmp/cfgprobe/ESCAPED"` in `docs/feedback/config.json` | Wrote outside the repo (`repo_root / "/abs"` discards the left operand); the index line advertised `../../../../tmp/...`. |

## Overlaps (same location, multiple critics)

| Location | Critics | Mechanisms | Resolution |
|---|---|---|---|
| `ledger_backlog.py:135-139` (+ twin `ledger_issues.py:145-149`) | perf L-03 · logic F16 · security S-04 | resource leak · committed litter · **predictable-name symlink write** | **different mechanisms → escalate to MED** |
| `ledger_backlog.py:187-194` free-text keys | logic F6 · security S-01 | silent truncation on read (` #`) · **frontmatter key forgery** | **different mechanisms → escalate to HIGH** |
| `format_index_line` / title | logic F7 · security S-02 | broken pointer + orphan prose · **forged pointer line** | same mechanism (newline splice) → corroborated, severity = max = **MED-HIGH** |
| `run_feedback.py:574-599` (`doctor`) | logic F4+F17 · perf L-04 · security S-12 | false green (substring vs exact line) · crash on the misconfig it diagnoses · whole-file read · `/dev/zero` DoS | **different mechanisms → escalate to MED** |
| `test_corpus.py` | perf M-03 · logic F8+F9 | 3× corpus re-read per run · **the guard is a tautology** | different mechanisms → **MED** (validity dominates) |
| Stale validation numbers | orchestrator (pre-merge) · logic F20 | identical | corroborated → **LOW**, but confirmed twice and factual |

## Logic issues (`critic-logic`, 24 findings)

Blocking: **F1** live `docs/BACKLOG.md` still carries `_No open work-items._`, so the next filing renders an open item *above* it (dogfood defect in my own migration) · **F2** the record `write_text` sits **outside** the rollback `try`, so a mid-write ENOSPC/SIGKILL leaves an orphan record — the docstring's "half-state never exists" is an overclaim · **F3** anchor = *first* line matching, fence-blind, duplicates silent → an index line can be spliced inside a ``` block · **F4** `doctor` uses a substring test where filing needs an exact standalone line (false green in exactly the case the gate exists for) · **F5** `--category` stays unguarded next to the new `_ledger_identity` guard → `## None` section or a TypeError traceback · **F7** title interpolated raw into a link and an H1 · **F8/F9** the corpus "independent loose probe" is strictly *narrower* than `RTM_HEADER`, so R9 can only fail if someone narrows the matcher — it cannot detect the drift its own docstring claims (and `MIN_DISTINCT_HEADING_SHAPES` counts raw strings, so it reddens on a *good* cleanup) · **F10** only the slug is uniqueness-checked; a lowercase `--prefix`, a second `feedback_dir`, or an archived subdir silently reuses an id.

Queueable: F11 (the gate never checks the engine's actual index-line string; `([a-z_]+):` skips keys with digits/uppercase) · F12 (live ledger carries a `contract:` marker but is ungated — a marker inside an ungated file reads as coverage) · F13 (`splitlines()` rewrites CRLF and eats `U+2028`/`\x0b`, mutating text the writer promises not to touch) · F14 (flat guard conflates wrapped with structured; caps body only) · F15 (`explicit_slug` computed then **dropped** in the flat branch; several flags silently ignored) · F17 · F18 (dry-run id not marked provisional) · F19 (`CONTRACT_KEYS` dead in both modules) · F20 · F21 (shell and Python disagree on "corpus present"; symlinked installs never skip) · F22 (the one filed record's key order contradicts the contract the SKILL cites as evidence) · F23 · F24 (seven missing test cases).

## Security findings (`critic-security`, 16 findings)

**HIGH:** S-01 frontmatter injection → forged `auto_fixable`/`status: fixed`/`resolved_by` (CWE-93) · S-03 symlink-following record write, create-only bypassed (CWE-59 + CWE-367).
**MED-HIGH:** S-02 index-line injection (CWE-117).
**MED:** S-04 predictable tmp name in a repo-visible dir (CWE-377) · S-05 no containment check on any config path, `RUN_FEEDBACK_CONFIG` alone redirects every write (CWE-22/CWE-15) · S-06 `--body-file` unredacted and **uncapped** in the new default layout while the flat path caps at 300 (secrets → committed file, CWE-532) · S-07 both ledgers are agent-trusted context re-read every phase → persistent indirect prompt injection, and TASK 091 enlarged that sink from a 300-char bullet to an unbounded file (LLM01).
**LOW/INFO:** S-08 `--finding` accepts any path and `consume` **unlinks** it (outside §5 scope) · S-09 the auto_fixable-exclusion rule lives in a *comment*, so the contract gate can't see it · S-10 the bypass substring is now *pinned* by a test (blessed, not introduced) · S-11 unhandled `OSError` → traceback · S-12 `doctor` slurps the backlog · S-13 seed-template supply chain across symlinked installs · **S-14 the scanner's MEDIUM is a FALSE POSITIVE** (deliberate negative test; `normalize_slug` containment independently verified) · S-15 fixtures shell out to real `git` with no ceiling · S-16 `--auto-fixable` silently ignored on the work-item path.

## Performance findings (`critic-performance`, 12 findings)

**MED:** M-01 eager `git rev-parse` in every `Config()` — pays a fork+exec on paths that never need `data_root`, ~150-250 spawns per suite (plausibly ~half the 1.9s), with a **10s timeout on the synchronous session hook path** · M-02 `find_by_fingerprint` JSON-parses the whole inbox to find a record whose fingerprint is already in its filename → cumulative **O(k²)** · M-03 `probed_headings()` re-reads the 111-file corpus **3×** per run (~431 opens, ~1.65MB; each file opened up to 6×) · M-04 the 140-test suite runs **twice** per gate (`test_e2e.sh:17` re-runs it).
**LOW:** L-01 `parse_file` reads whole files and rebuilds bodies to extract one `id:` (matters now that bodies live in records) · L-02 `_dup_candidates` rebuilds title token sets inside the inner loop · L-03 orphaned `.tmp` on `os.replace` failure · L-04 · L-05 fresh regex compile per RTM id.
**Cleared with arithmetic:** the new two-level writer is *cheaper* than the defect sibling (anchor is ~line 20 → effectively O(1) scan) and cuts index growth ~65× · no catastrophic backtracking in `_SEED_COMMENT_RE` · `check_contract_sync` does not re-read `SKILL.md` per registry · the plan-pair loop is linear, not quadratic.

## Disposition after iteration 1

**Fixed in iteration 2:** S-01/F6, S-02/F7, S-03, S-04/F16/L-03, S-05, S-16/F15, F1, F2, F3, F4, F5, F10, F13, F18, F19, F20, F8, F9, F21, M-03, F22.

**Filed, not fixed** (design decisions, pre-existing surfaces, or scope beyond this change): S-06, S-07, S-08, S-10, S-11, S-13, S-15, F11, F12, F14, F17 (partly fixed), F23, F24 (partial), M-01, M-02, M-04, L-01, L-02, L-05.

**Rejected:** the scanner's MEDIUM (S-14) — deliberate negative test with containment assertions.

> **Corrections to this report**, both found by the iteration-2 logic critic reviewing it: F18 was listed as "filed, not fixed" while the code does fix it (under-claiming, now moved); and the header's "41 findings" does not reconcile with 24+16+12 ids minus 10 collapsed by the 6 overlap rows (42). The severity breakdown sums to 41, so one finding is unaccounted for in the arithmetic — recorded rather than quietly adjusted. The iteration-1 "Queueable" list is the critic's original triage; the "Fixed in iteration 2" line above is my override of it.

---

# Iteration 2 — verification of the fixes (2026-07-30)

Both critics whose domains changed were re-spawned in fresh contexts and asked, per finding: *is the fix real, complete, and free of new holes?* Neither signalled convergence.

**The headline result: my iteration-1 fixes guarded the payloads I had tested, not the classes.**

| Finding | Iteration-1 fix | Iteration-2 verdict |
|---|---|---|
| **S-01** frontmatter injection | refused `\n`/`\r` | **NOT FIXED** — `parse` uses `str.splitlines()`, which also breaks on `\x0b \x0c \x1c \x1d \x1e \x85 U+2028 U+2029`. I reproduced the forged `auto_fixable: true` and `status: fixed` with one character changed. Now validated against `str.isprintable()`, i.e. the reader's break set **plus** the invisible/bidi classes, with a `parse(serialize(m)) == m` property test — the single assertion that would have caught all three vectors. |
| **S-02** index-line injection | collapse + escape `[`/`]` | **PARTIAL + NEW HOLE** — `\` was not in the escaped class, so `Fix a\](https://evil.example)` pre-escaped my own escape and the link went live; and `format_bullet` (flat layout) still interpolated `--value` raw, so the original two-line splice survived on the sibling path. Both fixed, both pinned. |
| **S-03** symlink follow | `lexists` + `O_EXCL\|O_NOFOLLOW` | **FIXED** — independently confirmed each guard is load-bearing. |
| **S-04** predictable temp file | `mkstemp` in the two ledger writers | **PARTIAL** — 2 of 6 sinks. `finding.py`, `inbox.py`, `mine.py` and `cmd_init` (a **fixed** name, `config.tmp`) kept the pattern my own docstring called eliminated. All six now delegate to one `feedback_lib/atomic.py`. |
| **S-05** config containment | reject absolute + traversal | **PARTIAL** — containment was repo-granular, so `"index_path": "CLAUDE.md"` rewrote the orchestrator's own prompt and `"backlog_dir": ".claude/commands"` wrote a slash-command definition. Ledger paths now refuse `.git/.claude/.agent/.codex/.cursor/.gemini/.antigravity/System` and the bootstrap filenames; `_contained` returns the **resolved** path (closing a check/use gap). |
| **F10** id reuse | exact-string membership | **PARTIAL** — F10's own headline case (`--prefix wi` beside `WI-1`) still worked. Now case-folded and recursive. |
| **F8** corpus guard | wider probe | tautology genuinely gone, **but** my fixture and pin lists omitted the corpus's two most common shapes (`## RTM (acceptance criteria)`, 16 files; `## N. RTM`, 7), so every fixture contained "Requirements" and a narrowing to require that word would have passed. Both added; the pin moved out of the corpus-skip gate, where a consumer install would never have run it. |

**Still open after iteration 2** (filed as WI-7): the fence tracker's fail-open/fail-closed cases (V8), the placeholder offset heuristic (V7), `doctor`'s property reads still outside its `try` (V9), `ledger_issues`' CRLF twin (V12), unvalidated `backlog_anchor`/`id_prefixes`/`excerpt_max_chars` (V-13), the `.doctor-probe` symlink write (V-08), dry-run id not marked provisional in human output (V-10), `CONTRACT_KEYS` near-tautology (V11), the `consume` half-state (V17), and three tests that pass for the wrong reason (V-22).

**Verdict: still FAIL.** Two iterations, 61 findings, four exploits closed and re-verified — and the honest reading is that adversarial review found more in my fixes than in my original code.
