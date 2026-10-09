# Framework Audit 118 — The security-audit scan reports for each tool whether it ran

- **Task:** 118 `security-audit-scan-status`. It archives to
  `docs/tasks/task-118-security-audit-scan-status.md`.
- **Workflow:** `/framework-upgrade`. **Meta-skill:** `skill-self-improvement-verificator` v1.1,
  Modes A and B.
- **Date:** 2026-10-09. **Base revision:** `e1fb36200ff474957611497f1d0826c51499d31a`, clean tree
  at start.
- **Source:** WI-42, with the operator's request of 2026-10-09 and the decisions D1 to D4.
- **Independence:** each audit round runs in a separate read-only agent. Same-model agreement is
  corroboration, not independent confirmation.

## 0. Emergency Bypass

None.

## Archive (§1)

TASK 117 archived under ID 117 with `task_id_tool.py "slot-archive-bound-and-stage2-review-bound"
--proposed-id "117" --no-correction` (`generated`). TASK 117 had no PLAN. The commands, as run:

```sh
python3 .agent/tools/archive_move.py docs/TASK.md docs/tasks/task-117-slot-archive-bound-and-stage2-review-bound.md
python3 .agent/tools/rebase_links.py docs/tasks/task-117-slot-archive-bound-and-stage2-review-bound.md --from docs --to docs/tasks
python3 .agent/tools/rebase_links.py --inbound --task docs/tasks/task-117-slot-archive-bound-and-stage2-review-bound.md --since 9e407e5
```

- The move: `"ok": true`, method `link`.
- Step 5.5: 2 rewritten, exit 0. Step 7: skipped, no `docs/PLAN.md`.
- Step 8: exit 3, 0 re-targeted, 2 `INBOUND`, 3 slot links in archived documents. The two
  records are `CHANGELOG.md:3219` and `CHANGELOG.ru.md:3226`, in the v3.13.0 entry of
  2026-04-17; they carry no reason and stay. Step 8 rewrote no file.

## Operator decisions (2026-10-09)

The four questions of the analysis, with the answers as chosen:

- D1, exit on a part not run: "Exit 3 always (Recommended)".
- D2, a non-zero tool exit: "Fails --fail-on gate (Recommended)".
- D3, npm advisories below high: "Findings at every severity (Recommended)".
- D4, where the external layer runs: "Local toolset in SKILL.md (Recommended)".

## Mode A — SPECIFICATION AUDIT

### Round 1 — TASK revision 1: FAIL

A read-only `task-reviewer` agent, with no execution tool and no fingerprint in its brief. It
checked the five positional references of §1 by hand: all resolve. It found no
`skill-self-improvement-verificator` §4 failure condition.

| # | Severity | Finding | Applied in revision 2 |
| :--- | :--- | :--- | :--- |
| 1 | BLOCKER | `tests/run_tests.py`, a listed script, imports `test_lockfile_audit`; §3 step 4 applies | R7, D5 revised |
| 2 | MAJOR | the version bump breaks the pinned `SKILLS.md` row; R5.5 text inside a pinned block | R7.6, R5.5 new blocks, TC-3b |
| 3 | MAJOR | no detected type → no external tool runs, and exit 0 | R1.4, R1.7 order, A11, TC-E15 |
| 4 | MAJOR | "every slot" undefined for unselected slots | §3 selected slot |
| 5 | MAJOR | external `npm audit` exits 1 on any advisory; UC-3 contradicts D2 | R2.10 `--audit-level`, D6, UC-3 scoped to `deps` |
| 6 | MAJOR | truncation at 30 precedes the summary and the gate; deps findings unsorted | R2.5, R3.6, A12, TC-E17 |
| 7 | MAJOR | no requirement fixes `overall_status` | R2.9, TC-E12 |
| 8 | MAJOR | the routers miss `security-audit.md` step 2; `tool_exits` mapping | R5.5 |
| 9 | MAJOR | the migration list is incomplete | R6.2 |
| 10 | MINOR | A1 vs `not_applicable` | A1, TC-E1 |
| 11 | MINOR | record fields under-specified | R1.1, R1.3, R1.5, R2.1 |
| 12 | MINOR | yarn reason missing | R1.6 |
| 13 | MINOR | the not-audited marker's severity | R3.4 |
| 14 | MINOR | TC-E3 exit; COMPLETE/PARTIAL untested; `PATH` | TC-E3, TC-E16, §7 fake tools, R7.5 |
| 15 | MINOR | SKILL.md §2 bullets and the example stale | R5.1, R5.6 |
| 16 | MINOR | closing fields of WI-42 | R6.3 |
| 17 | MINOR | `.git` file or link leads outside | R4.2, §8 |
| 18 | NIT | two lines, timeout constant, `exec sleep` | §1 O-2, TC-E4, §7 |
| 19 | NIT | use-case postconditions | §5 |

Verified by the orchestrator before revision 2: #1 against `framework-upgrade.md` §3 step 4 and
the `load_tests` of `tests/run_tests.py`; #3 at `run_audit.py:187`; #5 by the npm default of
`--audit-level`; #6 at `run_audit.py:73`.

### Round 2 — TASK revision 2: FAIL

The same agent, resumed, at fingerprint `7d74b668192e`, which it quoted at its start and end; the
caller recomputed it on return: equal. All 19 findings of round 1: RESOLVED. R2.9 matches §6.2;
D6 matches D2's text.

| # | Severity | Finding | Applied in revision 3 |
| :--- | :--- | :--- | :--- |
| N1 | MAJOR | `test_disclosure_rule.py` `TestVersionMirrors` pins the `SKILL.md` version and title, the `SKILLS.md` row and `VDD.md` to one version | R6.1, R7.6, R7.7 |
| N2 | MAJOR | a subdirectory scan drops the history that the base's git mode read, and reads complete | R4.2 walk up, D8, TC-E6, A8 |
| N3 | MINOR | `_load()` runs at import; R7.4 as written cannot set the package name | R7.4 three routes, `__file__` assertion |
| N4 | MINOR | `tests/test_*_next.py` matches pytest's `test_*.py` | R7.1 `tests/staged_*.py` |
| N5 | MINOR | TC-E17 cannot fail once R3.6 sorts | TC-E17 in process, stub scanner, A12 |
| N6 | MINOR | stages 2 and 4 and the §6.2 path are not stated | R7.9, R7.10 |
| N7 | MINOR | yarn's unranked exit is not named | R2.10 note, R6.2 |
| N8 | MINOR | documents that land before stage 3 stay after a restore | R7.11 |
| N9 | MINOR | `config.py` and `patterns.py` neither staged nor declared unchanged | R7.1 |
| N10 | NIT | a `.git` of another file type | R4.2 |

The orchestrator's own change in revision 3: slot `secrets-history` has no trufflehog fallback
(D7). `trufflehog git` executed the scanned repository's `core.fsmonitor` command
(CVE-2025-41390, CVSS 7.8, TruffleHog 3.90.2; Talos TALOS-2025-2243, read 2026-10-09).

### Round 3 — TASK revision 3: FAIL

The same agent, resumed, at fingerprint `4fd81d3e94d1`, quoted at its start and end; the caller
recomputed it on return: equal. N1, N2, N4 to N10: RESOLVED; N3: PARTIAL (P3). It could not check
the CVE (no network); the caller read the Talos report (round 2 above).

| # | Severity | Finding | Proposed for revision 4 |
| :--- | :--- | :--- | :--- |
| P1 | MAJOR | the seven coordinates of §1 point at base lines that stage 3 changes; after stage 3 the living-corpus gate of CI reports them | pin each as `path:line@e1fb362`; the resolver joins the R7.6 gates |
| P2 | MINOR | R7.7 forbids any `SKILL.md` edit before stage 3, against R5.1 to R5.4 | R7.7 names the version strings only |
| P3 | MINOR | `run_audit.py` imports `audit` by name; the in-process route of mode `next` reaches the base package | mode `next` also registers `audit` and `audit.*`, and asserts on them; §7 admits in-process exit-code tests |
| P4 | MINOR | the walk's path: lexical or `realpath`; the skip of TC-E6 | walk from `os.path.realpath`; an upper bound a test can set |
| P5 | MINOR | R7.8 restores on a stage-3 failure only; the Failure rule also restores on a failed focused review | R7.8 states restore, §6.2 re-run, operator |
| P6 | MINOR (low confidence) | R5.3 names no trufflehog version with the CVE fix; a second point concerns a dependency and is handled under `security-audit` §6.1 | R5.3 states the mode and cites the CVE |
| P7 | NIT | the yarn reasons of R1.6 and the slot of TC-E4 have no case | two cases |

**Bound reached.** `spec-audit-retry` allows 3 rounds; the third failed. §1.3: STOP and escalate to
the operator with the outstanding findings.

**Operator decision (2026-10-09), quoted.** D9, on the bound: "Apply rev 4, continue
(Recommended)". TASK revision 4 applies P1 to P7; the run enters §2 with no fourth spec round. The
register scan reports 0 `WARN`, and the resolver resolves every unpinned coordinate of the TASK;
the seven coordinates of its §1 carry `@e1fb362`.

**Mode A verdict:** APPROVED by operator decision D9 after the bound, on revision 4.

## §2.1 — Architecture

`docs/ARCHITECTURE.md` names `run_audit.py` once, as the tool of the `security-auditor` role. The
change alters the script's output contract and no component, role or data flow of the system, so
the document is not edited.

## Mode B — PLAN AUDIT

### Round 1 — PLAN revision 1: FAIL

A read-only `plan-reviewer` agent at fingerprint `3e892d6d690a`, quoted at its start and end; the
caller recomputed it on return: equal. No BLOCKER and no `skill-self-improvement-verificator` §4
condition. The caller ran the checks the agent could not: `plan_gantt.py --check` exit 0, and
`scan_register.py` 0 `WARN` on both documents.

| # | Severity | Finding | Applied in PLAN revision 2 / TASK revision 5 |
| :--- | :--- | :--- | :--- |
| 1 | MAJOR | no step sets the `run_audit.py` header to v3.12 | B1 |
| 2 | MAJOR | the stubs of B1 break base cases: `run_command` removed, the tuple return, no recorded call | B1 stubs keep base behaviour; B4 names TC-L7 and TC-Y1 |
| 3 | MAJOR | the Failure rule has no path for the expected `INCOMPLETE` stage-4 audit | I Failure bullet 2; TASK R7.10 |
| 4 | MINOR | mutants run in one process; stale `.pyc` | D2 fresh subprocess, `PYTHONDONTWRITEBYTECODE=1` |
| 5 | MINOR | no mutation row for `tool_exits` and for the `.git` link | D2, two rows |
| 6 | MINOR | D1 states no exact expected set | D1 |
| 7 | MINOR | G1 has no pass criterion | G1 |
| 8 | MINOR | the checks of R7.4 are in no step; base `audit.*` could load silently | A3, C4, B1 |
| 9 | MINOR | E can run before the base check | schedule: E after A |
| 10 | MINOR | at stage 2 the base scanner exits 0 with tools missing | H1 brief |
| 11 | MINOR | the `SKILLS.md` row text beyond the version is unrecorded | TASK R7.6 |
| 12 | MINOR | no path for a failed postcondition of I1 | I1 step 5 |
| 13 | MINOR | the skill's own `tests/` run in no step | G1, I2 |
| 14 | NIT | the moved fake's signature and return | B2 |
| 15 | NIT | no requirement coverage table; TC-3b id in B3 | Coverage, B3 |
| 16 | NIT (low confidence) | agent definitions may load at session start | H1 |

### Round 2 — PLAN revision 2: PASS

The same agent, resumed, at fingerprint `df787c0ed329`, quoted at its start and end; the caller
recomputed it on return: equal. Findings 1 to 4 and 6 to 16: RESOLVED; 5: PARTIAL (N3). Every
branch of the Failure rule ends in completion, a STOP or the operator.

| # | Severity | Finding | Applied in PLAN revision 3 / TASK revision 5 |
| :--- | :--- | :--- | :--- |
| N1 | MINOR | the stub of `run_external_tools` keeps the base body, which starts real tools | B1: `return []` only |
| N2 | MINOR | `audited` in both B1 and C1; TC-E10 may pass on the base | B1; TASK TC-E10 assertions |
| N3 | MINOR | the `tool_exits` mutant survives TC-E10 | D2 row: TC-E3 only |
| N4 | MINOR | the second `INCOMPLETE` branch states a fact, not a condition | I Failure bullet, three conditions |
| N5 | MINOR | TASK revision 5 after D9 records no decision | TASK D10 |
| N6 | NIT | the bootstrap checks nothing | `bootstrap_next.py` exits 70 on a mismatch |
| N7 | NIT | J's scratch files after the second branch; §4.1 vs §4.2 | J1; TASK R7.6 |

**Mode B verdict:** APPROVED, PLAN revision 3.

## §3 — Execution

### Cluster A — staged copies

- A1, the §3.1 base check: `HEAD` equals the base; the 18 edited paths are tracked; the 8 created
  paths give `git check-ignore` exit 1; every path matches `[A-Za-z0-9._/-]+`.
- A2: the seven staged files were byte copies of their base files, one SHA-256 per pair.
- A3: `stage_driver.py` mode `next` and mode `base`, 33 cases each, 0 failures; the checks of
  TASK R7.4 held.

### Cluster B — stubs and tests (Red)

- B1: the stubs of PLAN B1. A stub defect was found by B4's first run: `external_next.py` did not
  import `run_tool`, so the moved cases could not patch it. The import was added to the stub.
- `init_next.py` also exports `incomplete_slots`, which `run_audit_next.py` uses for
  `summary.not_run` and the external status; PLAN B1 names two exports, the code has three.
- B4, mode `next`, 59 cases: 23 failures, 15 errors. Of the base cases only TC-L7 and TC-Y1 fail;
  TC-L8, TC-L9c, TC-Y2 and TC-Y3 pass. TC-3b fails on its four blocks. Every new case fails or
  errors.

### Cluster C — logic (Green)

- C1 to C3 replaced the stubs. C4, mode `next`, 59 cases: 4 failures, all of TC-3b (the three
  blocks of E2 and the `SKILLS.md` row of the patch). The checks of TASK R7.4 held.
- Python 3.11: NOT RUN (no 3.11 interpreter installed); CI runs 3.11 after the commit. The main
  version, 3.14.4, ran every case.

### Cluster D — base-fail and mutation runs

- D1, mode `base`, 59 cases: 8 failures, 31 errors. Exactly as PLAN D1 states: the 27 new cases
  of B2 and B3 fail or error, the six moved cases error, and TC-3's `SKILLS.md` row fails on its
  v3.12 pin, which B3 moved. No other case fails.
- D2, `mutation_driver.py`, each mutant in a fresh subprocess with `PYTHONDONTWRITEBYTECODE=1`:
  8 of 8 killed; SHA-256 of the four staged files equal after the restore.

  | Mutation | Killed by |
  | :--- | :--- |
  | `exit_code` ignores `scan_complete` | TC-E1, TC-E11 (fail) |
  | the critical-and-high filter returns | TC-D1 (fail) |
  | the summary is counted after the cut | TC-E17 (fail) |
  | `secrets-tree` without `--no-git` | TC-E7 (fail) |
  | the tool's stdout on descriptor 1 | TC-E8 (error: stdout is no JSON document) |
  | a trufflehog fallback for `secrets-history` | TC-E5 (fail) |
  | `exit_code` ignores `tool_exits` | TC-E3 (fail) |
  | `find_git_entry` follows a `.git` link | TC-E6 (fail, both cases) |

  The first build of the third mutant removed the summary instead of moving it, and TC-E17 died
  on a `KeyError`; the rebuilt mutant moves it after the cut, and TC-E17 fails on its assertion.

### Cluster E — documents and records

- E1: `security-audit` §2 gains the deps bullets of R3, the subsection **External layer** (slot
  table, records, section status, secrets, the CVE line, exit-on-finding options, output, the
  toolset and `brew install semgrep gitleaks trufflehog bandit pip-audit`) and the subsection
  **Exit codes and summary**. The five Homebrew formulae answered HTTP 200 on 2026-10-09;
  trufflehog's stable formula is 3.99.2. The version and title stay 3.11 until stage 3.
- E2: one new block each in `.claude/agents/security-auditor.md`,
  `System/Agents/10_security_auditor.md` and step 2 of `.agent/workflows/security-audit.md`, as
  TC-3b pins them; no block of `POINTERS` changed.
- E3: `examples/usage_example.md` shows the summary output and the exit 3. The staged summary
  printer drops the parenthesis of a record with neither exit code nor reason (R1.8).
- E4: `CHANGELOG.md` and `CHANGELOG.ru.md`, v3.40.0, with each item of R6.2.
- E5: WI-42 `status: done`, `resolved_at`, `resolved_by: 'TASK 118'`, a resolution blockquote; its
  index line moved under `## Closed`. The record body is byte for byte.
- E6: `regcheck.py` (scan_register, its `WARN` lines matched to the lines added since the base):
  0 on each of the nine files.

### Cluster F — the stage-3 patch

- F1: `gen_stage3_patch.py` wrote `docs/reviews/framework-audit-118-stage3.diff`, 17 file
  sections: the seven final paths, the seven deletions, `SKILL.md`, `SKILLS.md`, `VDD.md`.
- F2: `git apply --check` passes. In memory, the version mirrors of `TestVersionMirrors` read 3.12,
  and the patched `SKILLS.md` row equals TC-3's pinned block.

### Cluster G — gates before stage 2

- `run_gates.sh`, the 17 `run:` steps of the check jobs of `framework-gates.yml`: 17 PASS.
  `tests/run_tests.py` ran 569 tests on the base code: OK.
- `pytest .agent/skills/security-audit/tests/`: 30 passed, on the base code.
- `stage_driver.py --mode next`: 59 cases, 1 failure, the `SKILLS.md` subtest of TC-3, which the
  patch of I satisfies.
- Register: 0 `WARN` on added lines. Declared paths: every entry of `git status` is declared.

### Stage 2, round 1 — fingerprint `2876ba4fc365`

Both agents quoted the fingerprint and the eight SHA-256 prefixes at their start and end; the caller
recomputed the fingerprint on return: equal. The brief gave the security auditor the `scan_status`
mapping of TASK R5.5, because its definition may have loaded before E2.

**Code review: CHANGES REQUESTED.** It applied in-memory mutants: 47 in-process cases stayed green
under three of them, and two control mutants were caught.

| # | Severity | Finding |
| :--- | :--- | :--- |
| C1 | MAJOR | TC-D7 cannot fail on the sort of R3.6: one lockfile's findings are already in order |
| C2 | MAJOR | TC-E6 checks a `.git` file and a parent `.git` at the classifier only; `entry == "dir"` survives |
| C3 | MINOR | no case pins `[OK] Secure` for an info-only advisory (R3.5) |
| C4 | MINOR | `[INCOMPLETE]` also prints beside `[GATE]` on exit 1; R2.8, §2 and the example say exit 3 |
| C5 | MINOR | the exit table omits exit 1 with a JSON `error` and argparse's exit 2 |
| C6 | MINOR | the `, <reason>` suffix of R2.1 and the five count lines of R3.7 are not asserted |
| C7 | NIT | an `lstat` error reads "not a directory or a regular file" |
| C8 | NIT | TC-E10 relies on the SBOM finding and asserts no specific `not_run` entry |
| C9 | NIT | the subprocess cases depend on what stands above the system temporary directory |
| C10 | NIT | the literal 30 appears three times |
| C11 | NIT | §2's "one installed tool per slot" omits `not_applicable` and the timeout |

**Security audit: FAIL**, `scan_status: NOT_RUN`. The base scanner exited 0 with the five tools
missing, and its stdout held npm's text before the JSON (O-2, which R1.9 fixes). The staged
scanner, run through `bootstrap_next.py`, exited 3 with one JSON document.

| # | Severity | Finding | New in this change? |
| :--- | :--- | :--- | :--- |
| H1 | HIGH | the history slot runs git inside a `.git` that comes from the scanned tree; git documents that a repository's configuration can name commands it runs. §2 presents the trufflehog removal as if it closed the class | no; the change makes gitleaks a required slot |
| H2 | HIGH | `cargo clippy`, `slither` and `checkov` can execute the scanned project's code or configuration | no; WI-37's class, dropped by the operator on 2026-10-06 |
| M1 | MEDIUM | a tool that errors, or is killed by a signal, records `ran` and completes its slot | yes |
| M2 | MEDIUM | the scanned tree can ship configuration files that silence the external tools | no |
| L1 | LOW | a FIFO named `package-lock.json` raises `shutil.SpecialFileError`: exit 1, empty stdout | no |
| L2 | LOW | a bare repository at the scanned root reads `not_applicable` | yes |
| L3 | LOW | names from the scanned tree reach stderr and summary output with control characters | partly |
| I1–I3 | INFO | a `.git` file naming another repository (TASK §8); pip-audit's target (TASK §8); the real `PATH` after the fake npm in the base test helper | — |

The auditor's report held one block for the operator's draft under `security-audit` §6.1. It
concerns a dependency and is not recorded here; it went to the operator in the session.

**Operator decisions (2026-10-09), quoted:**

- D11, on H1: "Keep, state it, file WI (Recommended)". The history slot keeps the base's git mode;
  §2 states what git mode reads; a work-item holds an isolated history scan.
- D12, on H2: "Covered by WI-37 drop (Recommended)". No code change; §2 names the three tools.
- D13, on M1: "Signal + doc rule (Recommended)". A tool killed by a signal is a part not run; the
  auditor documents say that a tool error shown in its output is `NOT_RUN`.
- D14, on M2: "File a work-item (Recommended)". §2 states it; a work-item holds the fix.

### Fix round 1

TASK revision 6 and PLAN revision 4 state the round. Tests first, then the staged code.

- Tests first (FR1.1): the new and strengthened cases failed against the staged code of round 1,
  but TC-D6's info-only case and TC-D7, whose behaviour the code already had; their mutants
  below fail without it. One test defect was fixed before the code: the gitleaks log of TC-E6
  holds the working-tree run as well, so the case compares the git-mode runs only.
- Code (FR1.2): `killed`; `LockfileCopyError` and the reason `the lockfile could not be copied`;
  `printable`, also on the ten `[WARN] Skipped {filepath}` lines of the in-process scanners; the
  bare repository and the unreadable `.git`; `MAX_FINDINGS`. A misplaced `@contextmanager`
  decorator was caught by the base cases at once and moved back.
- Documents (FR1.3): §2 (records, lockfiles, git mode, tools that run project code, configuration
  in the tree, text from the tree, toolset, exit table, `[INCOMPLETE]`); the three router blocks
  with the D13 sentence; both changelogs; WI-42's blockquote; WI-49 and WI-50 with their index
  lines. Register: 0 `WARN` on added lines of every edited file.
- C4: 63 cases, 1 failure, the `SKILLS.md` row of stage 3.
- D1, mode `base`: 63 cases, 5 failures and 35 errors: the 30 new cases of the lockfile module,
  the 6 moved cases and the `SKILLS.md` row. TC-3b's block cases pass in mode `base`: they read
  documents that landed in E2, not code.
- D2: 14 of 14 mutants killed, the 8 of round 1 and 6 new ones (only a `.git` directory starts
  git mode, the sort removed, an info-only advisory below high, a copy error not caught, a killed
  tool as `ran`, `printable` escaping nothing). SHA-256 equal after the restore.
- F1/F2: the patch regenerated, 17 sections; `git apply --check` passes; the in-memory mirror and
  pin checks pass.
- G1: `run_gates.sh` 17 PASS; the skill's tests 30 passed; declared paths: 23 entries, each
  declared.

### Stage 2, round 2 — fingerprint `70f10f4cb977`

Both agents, resumed, quoted the fingerprint and the eight prefixes at their start and end; the
caller recomputed the fingerprint on return: equal.

**Code review: APPROVED.** C1 to C8, C10 and C11 RESOLVED; C9 PARTIAL. Its in-memory mutants of
round 1 are killed; the `unreadable` branch read as `not_applicable` survives.

| # | Severity | Finding |
| :--- | :--- | :--- |
| R2-C1 | MINOR | the `unreadable` and `other` record branches are pinned only at the classifier |
| R2-C2 | MINOR | pre-existing: a FIFO `.json` blocks the in-process secrets scan; the CHANGELOG and A14 read as if a FIFO lockfile is handled under every scan type |
| R2-C3 | MINOR | §2 says tree text is printed escaped; the external tools' own output is not |
| R2-C4 | MINOR | `printable` leaves U+2028 and U+2029; a Cf character above U+FFFF prints five digits |
| R2-C5 | NIT | TASK R1.10 names control characters and `\xNN` only |
| R2-C6 | NIT | an unwrapped line in §2 and in a docstring |
| C9 | PARTIAL | the docstring says no subprocess case depends on the history slot; TC-E3 does |

**Security audit: INCOMPLETE**, `scan_status: NOT_RUN`; no CRITICAL or HIGH open. H1 and H2
ACCEPTED-BY-DECISION (D11, D12); M1 and M2 ACCEPTED-BY-DECISION (D13, D14), M1 verified; L1
RESOLVED; L2 RESOLVED for an ordinary bare root; L3 RESOLVED for the scanner's own lines. The
round-1 draft block for the operator appears in no record, the new work-items included.

| # | Severity | Finding |
| :--- | :--- | :--- |
| R2-S1 | LOW | a bare root whose `objects`, `refs` or `HEAD` is a link reads `not_applicable` |
| R2-S2 | LOW | U+2028 and U+2029 pass `printable`; §2 overstates the escaping |
| R2-S3 | INFO | the routers do not map exit 1 with a JSON `error`, exit 2, or no report to `NOT_RUN` |
| R2-S4 | INFO | a `killed` tool gives exit 3, not 1, under `--fail-on` (consistent with D13) |
| M1 residual | — | a wrapper that reports its child's death as a positive code reads `ran` (accepted with D13) |
| I2, I3 | INFO | the mcp-scan fallback's target; the real `PATH` after the fake npm in a test helper |

**Operator decisions (2026-10-09), quoted:**

- On the scan gap the operator first asked, in Russian, which tools were missing and what to do
  with them. The session listed the slots this repository selects (`python`, `javascript`):
  semgrep, gitleaks, bandit and pip-audit are missing; npm is present.
- D17, on the `INCOMPLETE` scan part (`security-audit` §6.2 rule 2): "Отгрузить с записанным
  пробелом (Recommended)". The option stated that the decision covers stage 4 for the same part
  and the same cause, in the terms of TASK R7.10.
- D18, on the LOW and MINOR findings of round 2: "Fix cheap ones, round 3 (Recommended)". The
  pre-existing items go to one backlog record.

### Fix round 2

TASK revision 7 and PLAN revision 5 state the round.

- Tests first (FR2.1): TC-E6's `bare-link` case, the declined-record cases, TC-E19b and TC-3b's
  blocks failed against the code of round 2. The declined-record cases for `link`, `other`,
  `unreadable` and none passed at once; their mutant below fails without the code.
- Code (FR2.2): `printable` escapes Cc, Cf, Zl and Zp, with `\UNNNNNNNN` above U+FFFF; a bare
  repository with a link is `bare-link`, `not_run`.
- Documents (FR2.3): §2, the three router blocks ("no report" is `NOT_RUN`), both changelogs
  (A14's scope; WI-51), WI-42's blockquote; WI-51 and its index line. Register: 0 `WARN` on added
  lines.
- C4: 65 cases, 1 failure, the `SKILLS.md` row of stage 3.
- D1, mode `base`: 65 cases, 5 failures and 37 errors: the 32 new cases of the lockfile module,
  the 6 moved cases and the `SKILLS.md` row.
- D2: 17 of 17 mutants killed, three of them new (a bare repository with a link read as none,
  `printable` leaving Zl and Zp, an unreadable `.git` read as `not_applicable`). SHA-256 equal
  after the restore.
- F1/F2: the patch regenerated, 17 sections; `git apply --check` passes; the in-memory checks
  pass.
- G1: `run_gates.sh` 17 PASS; the skill's tests 30 passed; declared paths: 24 entries, each
  declared.

### Stage 2, round 3 — fingerprint `569b4163eb23`

Both agents, resumed, quoted the fingerprint and the eight prefixes at their start and end; the
caller recomputed the fingerprint on return: equal. Round 3 is the last of `stage2-review-retry`.

**Code review: APPROVED.** R2-C1 to R2-C6 and C9 RESOLVED; 14 of 14 in-memory mutants caught.
Two NITs: the module docstring lists TC-E19 but not TC-E19b (R6.5); the auditor bullet of §2 lacks
the routers' "no report is `NOT_RUN`" sentence.

**Security audit: INCOMPLETE**, on the scan gap alone, which D17 decided; the manual review ran to
completion with no open CRITICAL or HIGH. R2-S1 to R2-S3 RESOLVED and verified; R2-S4, I2 (mcp-scan)
and I3 FILED in WI-51; H1 to M2 ACCEPTED-BY-DECISION (D11 to D14). One INFO: `printable` does not
escape the backslash, so a file name holding the text `\x0a` prints as an escaped newline does;
the output is ambiguous, and no line can be forged. §6.1 hygiene of WI-49, WI-50, WI-51 and this
record: no reproduction detail.

**Stage 2 passes** under D17: the code review approved, and the security audit's only unfinished
part is the scan gap the operator decided. The two NITs and the INFO would change reviewed files
after the last round, so they are not applied. WI-51 holds them as residuals.

## §4 — Documentation

- §4.1: `System/Docs/SKILLS.md` and `System/Docs/VDD.md` change in the stage-3 patch (the version
  and the per-tool scan status); `security-audit` §2 changed in E1 and the fix rounds.
- §4.2: `System/Docs/WORKFLOWS.md`'s Security Audit row still holds: `scan_status: NOT_RUN` gives
  `INCOMPLETE`. No workflow and no skill was added, so no registry row is added.
- §4.3: the prompts of the `security-auditor` role changed; the final message asks for a restart.

## §4.5 — Reference resolver

`check_positional_refs.py --targets-changed`, then with `--fix`: 546 references in 23 documents,
9 errors and 15 warnings, the same on both runs. `--fix` touched no file: the tree fingerprint was
`ecf3896fce8a` before and after it.

- No error is `REFERENT_MOVED`. Eight are `UNRESOLVABLE` references in old `CHANGELOG.md` and
  `CHANGELOG.ru.md` entries to `.ts` files of another repository; one is a `REFERENT_ABSENT` in
  `docs/reviews/review-095-independent.md` to `check_prompt_references.py`, which this change does
  not touch. None is in the living corpus that CI gates.
- The warnings are `DRIFT_SUSPECT` and `ESCAPES_ROOT` references into files this change edits,
  in archived documents and two ledger records; they stay advisory.

## Stage 3

### I1 — before the apply

1. §4.5 above: no repair.
2. The patch and the staged files hash to the values that the reviewers of round 3 quoted:

   ```text
   4df5d37cc73a12b01b1add6a699cb85fc51298b7453af6f76eff1b2396f900ee  docs/reviews/framework-audit-118-stage3.diff
   68d8f7bcc88615cddb3c67488cb452312cc39cc9726a28fedc691b9a19d2fada  .agent/skills/security-audit/scripts/audit/init_next.py
   22884bbfef9c8aa386ba20587ce4c078c75556b948129da43c451e6bf4be29e0  .agent/skills/security-audit/scripts/audit/helpers_next.py
   8f51b2b11888aa779e9d1ea28c81457c4469cc7b23d6fd62b823b11d5af44606  .agent/skills/security-audit/scripts/audit/scanners_next.py
   e6b67fdc35db79383328ec79ddfee4ddfe5d0e592c65ed6f4ee11cc2e6e31ce1  .agent/skills/security-audit/scripts/audit/external_next.py
   f9d5f2ee91c052c86165011f2e6cfb5235ea4e5828e17131f8c83fcbe314306c  .agent/skills/security-audit/scripts/run_audit_next.py
   1bc4c753a2ec67ed267088f72329a05c6ea36257e69f47677a85694597a15cfe  tests/staged_lockfile_audit.py
   e18dd6a674ecd9ffcc68405447711591d18469557a7739839b174ad6c1c8084a  tests/staged_run_safety_rules.py
   ```

3. SHA-256 and mode of every file the patch touches, before the apply:

   | File | SHA-256 | Mode |
   | :--- | :--- | :--- |
   | `.agent/skills/security-audit/scripts/audit/__init__.py` | `69eb60154b7dd48f83d141d527111634615564e844fbb21682e0deafa9e9487d` | `644` |
   | `.agent/skills/security-audit/scripts/audit/helpers.py` | `a0f761a19fff4c5e446c500fd94a10e878864cb1c9f246ff311ebe2ddc8da161` | `644` |
   | `.agent/skills/security-audit/scripts/audit/scanners.py` | `534f8f7e82e35ca27a524cc4e08570d45ad7aa38b4613e36dcbca836c02a881a` | `644` |
   | `.agent/skills/security-audit/scripts/audit/external.py` | `e3231e97ecefd9adf76e0b917b50a71a4a4f6b185b3709b24481921e548e7877` | `644` |
   | `.agent/skills/security-audit/scripts/run_audit.py` | `4c279f3a207e81abc3fbbf8df5f114810915ac4622ff8fc34a228c61fc7e9899` | `755` |
   | `tests/test_lockfile_audit.py` | `2b6eb65950a62efd382206be22e7ebbf2e8c55c734bd9780fc5d79e3552446a6` | `644` |
   | `tests/test_run_safety_rules.py` | `335a513e334d7a13cb3a90672708792607c46ab18efb072f76930052b4bc38e3` | `644` |
   | `.agent/skills/security-audit/scripts/audit/init_next.py` | `68d8f7bcc88615cddb3c67488cb452312cc39cc9726a28fedc691b9a19d2fada` | `644` |
   | `.agent/skills/security-audit/scripts/audit/helpers_next.py` | `22884bbfef9c8aa386ba20587ce4c078c75556b948129da43c451e6bf4be29e0` | `644` |
   | `.agent/skills/security-audit/scripts/audit/scanners_next.py` | `8f51b2b11888aa779e9d1ea28c81457c4469cc7b23d6fd62b823b11d5af44606` | `644` |
   | `.agent/skills/security-audit/scripts/audit/external_next.py` | `e6b67fdc35db79383328ec79ddfee4ddfe5d0e592c65ed6f4ee11cc2e6e31ce1` | `644` |
   | `.agent/skills/security-audit/scripts/run_audit_next.py` | `f9d5f2ee91c052c86165011f2e6cfb5235ea4e5828e17131f8c83fcbe314306c` | `755` |
   | `tests/staged_lockfile_audit.py` | `1bc4c753a2ec67ed267088f72329a05c6ea36257e69f47677a85694597a15cfe` | `644` |
   | `tests/staged_run_safety_rules.py` | `e18dd6a674ecd9ffcc68405447711591d18469557a7739839b174ad6c1c8084a` | `644` |
   | `.agent/skills/security-audit/SKILL.md` | `4f063798ca5b7e138252a6e52f866d5f4112d7b33e4d6a106c54726231affc96` | `644` |
   | `System/Docs/SKILLS.md` | `1d5e0c481c234b22cfa078c5904c912ad73aece051aa7cdbfa73376d780dd47f` | `644` |
   | `System/Docs/VDD.md` | `25280fd93ad9a5484c62d4e6483378f2d5b74fe51f835c735b390e2d10bd53e3` | `644` |

The patch text, as applied:

~~~~diff
diff --git a/.agent/skills/security-audit/scripts/audit/__init__.py b/.agent/skills/security-audit/scripts/audit/__init__.py
--- a/.agent/skills/security-audit/scripts/audit/__init__.py
+++ b/.agent/skills/security-audit/scripts/audit/__init__.py
@@ -4,7 +4,7 @@
 run_audit.py CLI header must match `__version__` on each release.
 """
 
-__version__ = "3.11"
+__version__ = "3.12"
 
 from .config import SEVERITY_ORDER
 from .scanners import (
@@ -16,8 +16,8 @@
     scan_mcp_agentic,
     scan_sbom,
 )
-from .external import run_external_tools
-from .helpers import detect_project_types
+from .external import external_section, find_git_entry, incomplete_slots, run_external_tools
+from .helpers import detect_project_types, printable
 
 __all__ = [
     "__version__",
@@ -30,5 +30,9 @@
     "scan_mcp_agentic",
     "scan_sbom",
     "run_external_tools",
+    "external_section",
+    "find_git_entry",
+    "incomplete_slots",
+    "printable",
     "detect_project_types",
 ]
diff --git a/.agent/skills/security-audit/scripts/audit/helpers.py b/.agent/skills/security-audit/scripts/audit/helpers.py
--- a/.agent/skills/security-audit/scripts/audit/helpers.py
+++ b/.agent/skills/security-audit/scripts/audit/helpers.py
@@ -2,6 +2,7 @@
 
 import math
 import os
+import unicodedata
 import shutil
 import subprocess
 import sys
@@ -19,30 +20,68 @@
 )
 
 
-def run_command(cmd, cwd=None, shell=False, capture=False, timeout=600) -> Optional[subprocess.CompletedProcess]:
-    """Run a shell command, capture exit code, and report status.
+#: Seconds one external tool may run before its record says `timed_out` (TASK 118 R1.1).
+#: `run_tool` reads it at each call. External SAST tools like semgrep can exceed 120 s on a
+#: non-trivial repository; a shorter limit killed them mid-scan.
+TOOL_TIMEOUT = 600
 
-    timeout: seconds (default 600s / 10min). External SAST tools like semgrep can easily
-    exceed 120s on non-trivial repos; earlier default silently killed them mid-scan.
+
+def run_tool(cmd: List[str], cwd: str, slot: str, where: str = ".") -> Dict:
+    """Run one external tool and return its tool record (TASK 118 R1.1).
+
+    The record's `status` is `ran` with the tool's `exit_code`, `not_installed` when the executable
+    is not found, or `timed_out` past `TOOL_TIMEOUT`. The tool's stdout goes to file descriptor 2,
+    beside its stderr, so the scanner's stdout holds its report alone (R1.9).
     """
-    cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
+    record = {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where,
+              "status": "ran", "exit_code": None, "reason": None}
+    cmd_str = " ".join(cmd)
     print(f"[*] Running: {cmd_str}", file=sys.stderr)
+    sys.stderr.flush()
     try:
-        result = subprocess.run(
-            cmd, cwd=cwd, shell=shell, check=False, timeout=timeout,
-            capture_output=capture, text=capture
-        )
-        if result.returncode != 0:
-            print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
-        return result
+        result = subprocess.run(cmd, cwd=cwd, check=False, timeout=TOOL_TIMEOUT, stdout=2)
     except FileNotFoundError:
-        tool_name = cmd[0] if isinstance(cmd, list) else cmd.split()[0]
-        print(f"[!] Tool not found: {tool_name}", file=sys.stderr)
-        print(f"    Install: see project docs or run via Docker", file=sys.stderr)
-        return None
+        print(f"[!] Tool not found: {cmd[0]}", file=sys.stderr)
+        record["status"] = "not_installed"
+        return record
     except subprocess.TimeoutExpired:
-        print(f"[!] Timeout: {cmd_str} exceeded {timeout}s limit", file=sys.stderr)
-        return None
+        print(f"[!] Timeout: {cmd_str} exceeded {TOOL_TIMEOUT}s limit", file=sys.stderr)
+        record["status"] = "timed_out"
+        return record
+    record["exit_code"] = result.returncode
+    if result.returncode < 0:
+        # A signal ended the process: the tool did not finish its scan (TASK 118 D13).
+        record["status"] = "killed"
+        print(f"[!] {cmd_str} was killed by signal {-result.returncode}", file=sys.stderr)
+    elif result.returncode != 0:
+        print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
+    return record
+
+
+#: The Unicode categories `printable` escapes: control, format, line and paragraph separator.
+ESCAPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")
+
+
+def printable(text) -> str:
+    """`text` with each control, format or separator character escaped (TASK 118 R1.10).
+
+    A path or a message from the scanned tree can hold a newline, an ANSI escape, a bidirectional
+    override or a line separator, and with it forge a line of the scanner's output. The categories
+    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`.
+    """
+    out = []
+    for char in str(text):
+        if unicodedata.category(char) in ESCAPED_CATEGORIES:
+            code = ord(char)
+            if code <= 0xFF:
+                out.append(f"\\x{code:02x}")
+            elif code <= 0xFFFF:
+                out.append(f"\\u{code:04x}")
+            else:
+                out.append(f"\\U{code:08x}")
+        else:
+            out.append(char)
+    return "".join(out)
 
 
 def is_self_path(filepath: str) -> bool:
@@ -88,6 +127,10 @@
     return found
 
 
+class LockfileCopyError(Exception):
+    """The lockfile or its `package.json` could not be copied, such as a FIFO (TASK 118 D16)."""
+
+
 @contextmanager
 def npm_audit_dir(lockfile: Path) -> Iterator[Optional[Path]]:
     """A temporary directory holding copies of `lockfile` and its `package.json` (TASK 111 R5.2).
@@ -95,15 +138,19 @@
     npm reads `.npmrc` from the directory it runs in, and an audited subdirectory may be vendored
     code: its `.npmrc` could redirect the registry or the cache. A copy leaves it behind; the
     operator's own npm configuration still applies. Yields `None` when no regular `package.json`
-    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead.
+    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead. Raises
+    `LockfileCopyError` when a copy raises `OSError`; `shutil` refuses a FIFO before it opens one.
     """
     package = lockfile.parent / "package.json"
     if not package.is_file() or package.is_symlink():
         yield None
         return
     with tempfile.TemporaryDirectory(prefix="npm-audit-") as tmp:
-        shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
-        shutil.copyfile(package, Path(tmp) / "package.json")
+        try:
+            shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
+            shutil.copyfile(package, Path(tmp) / "package.json")
+        except OSError as exc:
+            raise LockfileCopyError(str(exc)) from exc
         yield Path(tmp)
 
 
diff --git a/.agent/skills/security-audit/scripts/audit/scanners.py b/.agent/skills/security-audit/scripts/audit/scanners.py
--- a/.agent/skills/security-audit/scripts/audit/scanners.py
+++ b/.agent/skills/security-audit/scripts/audit/scanners.py
@@ -20,9 +20,11 @@
     SKIP_DIRS,
 )
 from .helpers import (
+    LockfileCopyError,
     find_npm_lockfiles,
     is_self_path,
     npm_audit_dir,
+    printable,
     shannon_entropy,
     sort_findings_by_severity,
 )
@@ -38,70 +40,98 @@
 #: Seconds one `npm audit` may run before its lockfile is reported as not audited (TASK 111 R5.2).
 NPM_AUDIT_TIMEOUT = 60
 
-
-def _npm_audit(lockfile: Path, project_path: str) -> list:
-    """The findings of `npm audit` for one lockfile (TASK 111 R5.2, R5.3, R5.6).
+#: npm's advisory severity → the scanner's severity (TASK 118 R3.1).
+NPM_SEVERITY = {"critical": "critical", "high": "high", "moderate": "medium", "low": "low",
+                "info": "info"}
+
+
+def _npm_audit(lockfile: Path, project_path: str):
+    """`(rel, findings, counts)` of `npm audit` for one lockfile (TASK 111 R5.2, R5.3, R5.6).
 
     `--package-lock-only` reads the lockfile without `node_modules`, in a temporary copy of the
     lockfile and its `package.json`. An audit that does not finish yields an `info` finding naming
-    the lockfile and the reason, never a silent pass.
+    the lockfile and the reason, never a silent pass; its `counts` is `None` (TASK 118 R3.3).
     """
     rel = os.path.relpath(lockfile, project_path).replace(os.sep, "/")
-    with npm_audit_dir(lockfile) as workdir:
-        if workdir is None:
-            return [_not_audited(rel, "no package.json beside it")]
-        try:
-            result = subprocess.run(
-                ["npm", "audit", "--json", "--package-lock-only"],
-                cwd=workdir, capture_output=True, text=True, timeout=NPM_AUDIT_TIMEOUT,
-            )
-        except FileNotFoundError:
-            return [_not_audited(rel, "npm is not installed")]
-        except subprocess.TimeoutExpired:
-            return [_not_audited(rel, f"npm audit ran past {NPM_AUDIT_TIMEOUT} s")]
+    try:
+        with npm_audit_dir(lockfile) as workdir:
+            if workdir is None:
+                return rel, [_not_audited(rel, "no package.json beside it")], None
+            try:
+                result = subprocess.run(
+                    ["npm", "audit", "--json", "--package-lock-only"],
+                    cwd=workdir, capture_output=True, text=True, timeout=NPM_AUDIT_TIMEOUT,
+                )
+            except FileNotFoundError:
+                return rel, [_not_audited(rel, "npm is not installed")], None
+            except subprocess.TimeoutExpired:
+                return rel, [_not_audited(rel, f"npm audit ran past {NPM_AUDIT_TIMEOUT} s")], None
+    except LockfileCopyError:
+        return rel, [_not_audited(rel, "the lockfile could not be copied")], None
     try:
         audit_data = json.loads(result.stdout)
     except json.JSONDecodeError:
-        return [_not_audited(rel, "npm audit printed no JSON")]
+        return rel, [_not_audited(rel, "npm audit printed no JSON")], None
     if not isinstance(audit_data, dict):
-        return [_not_audited(rel, "npm audit printed no JSON object")]
+        return rel, [_not_audited(rel, "npm audit printed no JSON object")], None
     if "error" in audit_data:
         error = audit_data["error"]
         detail = (error.get("code") if isinstance(error, dict) else None) or audit_data.get("message")
-        return [_not_audited(rel, f"npm audit reported an error ({str(detail or 'no detail')[:120]})")]
+        reason = f"npm audit reported an error ({str(detail or 'no detail')[:120]})"
+        return rel, [_not_audited(rel, reason)], None
     vulnerabilities = audit_data.get("vulnerabilities")
     if vulnerabilities is not None and not isinstance(vulnerabilities, dict):
-        return [_not_audited(rel, "npm audit printed no vulnerability map")]
-    return _npm_audit_findings(audit_data, rel)
+        return rel, [_not_audited(rel, "npm audit printed no vulnerability map")], None
+    return rel, _npm_audit_findings(audit_data, rel), _npm_audit_counts(audit_data)
 
 
 def _not_audited(rel: str, reason: str) -> dict:
+    """The `info` finding of a lockfile that was not audited; `audited` marks it (TASK 118 R3.4)."""
     return {
         "type": "npm audit",
         "severity": "info",
         "cwe": "CWE-1104",
         "message": f"{rel}: not audited, {reason}",
+        "audited": False,
     }
 
 
+def _npm_audit_counts(audit_data: dict) -> dict:
+    """The counts of a finished `npm audit` per npm severity, and `unknown` (TASK 118 R3.2, R3.3).
+
+    An entry that is not a map, or holds no severity, counts as `low`, as before TASK 118; a
+    severity outside npm's five counts as `unknown`.
+    """
+    counts = dict.fromkeys((*NPM_SEVERITY, "unknown"), 0)
+    for vuln in (audit_data.get("vulnerabilities") or {}).values():
+        sev = str(vuln.get("severity") or "low").lower() if isinstance(vuln, dict) else "low"
+        counts[sev if sev in NPM_SEVERITY else "unknown"] += 1
+    return counts
+
+
 def _npm_audit_findings(audit_data: dict, rel: str) -> list:
-    """One finding per severity, critical and high, of a finished `npm audit`."""
-    severity_count = {"critical": 0, "high": 0}
-    for vuln in (audit_data.get("vulnerabilities") or {}).values():
-        sev = str(vuln.get("severity", "low")).lower() if isinstance(vuln, dict) else "low"
-        if sev in severity_count:
-            severity_count[sev] += 1
-    return [{
+    """One finding per npm severity of a finished `npm audit`, at every severity (TASK 118 R3.1)."""
+    counts = _npm_audit_counts(audit_data)
+    findings = [{
         "type": "npm audit",
-        "severity": sev,
+        "severity": NPM_SEVERITY[sev],
         "cwe": "CWE-1104",
         "message": f"{rel}: {count} {sev} vulnerabilities in dependencies",
-    } for sev, count in severity_count.items() if count]
+    } for sev, count in counts.items() if sev in NPM_SEVERITY and count]
+    if counts["unknown"]:
+        findings.append({
+            "type": "npm audit",
+            "severity": "low",
+            "cwe": "CWE-1104",
+            "message": f"{rel}: {counts['unknown']} vulnerabilities of unknown severity",
+        })
+    return findings
 
 
 def scan_dependencies(project_path: str) -> Dict[str, Any]:
     """Validate supply chain security (OWASP A03:2025 Software Supply Chain Failures, CWE-1104)."""
-    results = {"tool": "dependency_scanner", "findings": [], "status": "[OK] Secure"}
+    results = {"tool": "dependency_scanner", "findings": [], "status": "[OK] Secure",
+               "npm_audit_counts": {}}
 
     # Ecosystem -> (type markers, accepted lock files).
     # `requirements.txt` lists deps but does NOT pin a full transitive graph
@@ -159,19 +189,25 @@
     # and a failed run produced no finding, so an offline scan read as a clean one.
     not_audited = 0
     for lockfile in find_npm_lockfiles(project_path):
-        found = _npm_audit(lockfile, project_path)
-        not_audited += sum(1 for f in found if f["severity"] == "info")
+        rel, found, counts = _npm_audit(lockfile, project_path)
+        not_audited += sum(1 for f in found if f.get("audited") is False)
         results["findings"].extend(found)
-    if not_audited:
-        # A critical or high finding below still sets its own status (TASK 111 R5.7).
+        if counts is not None:
+            results["npm_audit_counts"][rel] = counts
+    results["findings"] = sort_findings_by_severity(results["findings"])
+
+    # The first match sets the status (TASK 118 R3.5): a critical or high finding outranks an
+    # unaudited lockfile (TASK 111 R5.7), which outranks a finding below high.
+    max_sev = min((SEVERITY_ORDER.get(f.get("severity", "low"), 99) for f in results["findings"]),
+                  default=99)
+    if max_sev == 0:
+        results["status"] = "[!!] Critical vulnerabilities"
+    elif max_sev == 1:
+        results["status"] = "[!] HIGH: Dependency issues"
+    elif not_audited:
         results["status"] = f"[?] Not audited: {not_audited} npm lockfile(s)"
-
-    if results["findings"]:
-        max_sev = min(SEVERITY_ORDER.get(f.get("severity", "low"), 99) for f in results["findings"])
-        if max_sev == 0:
-            results["status"] = "[!!] Critical vulnerabilities"
-        elif max_sev == 1:
-            results["status"] = "[!] HIGH: Dependency issues"
+    elif any(f.get("severity") in ("medium", "low") for f in results["findings"]):
+        results["status"] = "[?] Dependency issues below high"
 
     return results
 
@@ -203,7 +239,7 @@
             try:
                 if filepath.stat().st_size > _config.MAX_FILE_SIZE:
                     results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {filepath}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
+                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                     continue
             except OSError:
                 continue
@@ -227,7 +263,7 @@
                     # no trailing empty element — emitting a phantom "skipped 1 line" WARN.)
                     skipped_lines = len(all_lines) - len(safe_lines)
                     if skipped_lines > 0:
-                        print(f"[WARN] {filepath}: skipped {skipped_lines} line(s) > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
+                        print(f"[WARN] {printable(filepath)}: skipped {skipped_lines} line(s) > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
                     for pattern, secret_type, severity, cwe in SECRET_PATTERNS:
                         matches = re.findall(pattern, safe_content, re.IGNORECASE)
                         if matches:
@@ -258,7 +294,7 @@
                             results["by_severity"]["high"] += 1
             except Exception as e:
                 results["skipped_files"] += 1
-                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)
+                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
 
     results["findings"] = sort_findings_by_severity(results["findings"])
 
@@ -296,7 +332,7 @@
             try:
                 if filepath.stat().st_size > _config.MAX_FILE_SIZE:
                     results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {filepath}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
+                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                     continue
             except OSError:
                 continue
@@ -323,7 +359,7 @@
                                 })
             except Exception as e:
                 results["skipped_files"] += 1
-                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)
+                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
 
     results["findings"] = sort_findings_by_severity(results["findings"])
 
@@ -376,7 +412,7 @@
                             })
             except Exception as e:
                 results["skipped_files"] += 1
-                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)
+                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
 
     results["findings"] = sort_findings_by_severity(results["findings"])
 
@@ -431,7 +467,7 @@
                     # never has >4k-char lines; only minified blobs do.
                     if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
                         results["skipped_files"] += 1
-                        print(f"[WARN] Skipped IaC {filepath}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
+                        print(f"[WARN] Skipped IaC {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
                         continue
 
                     # Heuristic: for generic YAML/JSON files, only apply patterns
@@ -465,7 +501,7 @@
                             })
             except Exception as e:
                 results["skipped_files"] += 1
-                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)
+                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
 
     results["findings"] = sort_findings_by_severity(results["findings"])
 
@@ -596,7 +632,7 @@
                 # classes, so (IaC-style) skip the entire file on pathological lines.
                 if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
                     results["skipped_files"] += 1
-                    print(f"[WARN] Skipped MCP scan of {filepath}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
+                    print(f"[WARN] Skipped MCP scan of {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
                     continue
 
                 lines = content.splitlines()
@@ -615,7 +651,7 @@
                         })
             except Exception as e:
                 results["skipped_files"] += 1
-                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)
+                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
 
     results["findings"] = sort_findings_by_severity(results["findings"])
 
diff --git a/.agent/skills/security-audit/scripts/audit/external.py b/.agent/skills/security-audit/scripts/audit/external.py
--- a/.agent/skills/security-audit/scripts/audit/external.py
+++ b/.agent/skills/security-audit/scripts/audit/external.py
@@ -2,11 +2,12 @@
 
 import json
 import os
+import stat
 from pathlib import Path
-from typing import List
+from typing import List, Optional
 import sys
 
-from .helpers import find_npm_lockfiles, npm_audit_dir, run_command
+from .helpers import LockfileCopyError, find_npm_lockfiles, npm_audit_dir, printable, run_tool
 
 
 #: The `package.json` fields the yarn copy keeps (TASK 112 R5.1). `packageManager` and
@@ -28,76 +29,224 @@
     return True
 
 
-def run_external_tools(project_path: str, types: List[str]):
-    """Run external security tools based on project type.
-
-    Tool availability is checked by `run_command` (prints [!] Tool not found and returns None).
-    Missing tools are non-fatal — run_audit.py always continues.
+#: `--fail-on` → the `npm audit --audit-level` that makes npm exit non-zero at that threshold
+#: (TASK 118 R2.10).
+NPM_AUDIT_LEVEL = {"critical": "critical", "high": "high", "medium": "moderate"}
+
+#: The working-tree secret scan: `--no-git` reads the files, the uncommitted ones included
+#: (TASK 118 R4.1).
+GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
+#: The history secret scan: git mode reads the committed history (TASK 118 R4.2).
+GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
+
+
+def _bare_repository(directory: str) -> Optional[str]:
+    """`"bare"` for a regular `HEAD` and the directories `objects` and `refs`; `"bare-link"` when
+    the three exist and one is a link (TASK 118 R4.2); `None` otherwise."""
+    try:
+        modes = [os.lstat(os.path.join(directory, name)).st_mode
+                 for name in ("HEAD", "objects", "refs")]
+    except OSError:
+        return None
+    if any(stat.S_ISLNK(mode) for mode in modes):
+        return "bare-link"
+    head, objects, refs = modes
+    if stat.S_ISREG(head) and stat.S_ISDIR(objects) and stat.S_ISDIR(refs):
+        return "bare"
+    return None
+
+
+def find_git_entry(root: str, stop: Optional[str] = None) -> Optional[str]:
+    """The kind of the first repository at or above `root` (TASK 118 R4.2).
+
+    The walk starts at the real path of `root`, as git does, and checks each parent up to the
+    filesystem root, or up to `stop` included. At each directory it reads `.git` with `os.lstat`,
+    so a link is reported as `"link"` and never followed, and then checks whether the directory is
+    itself a bare repository. Returns `"dir"`, `"file"`, `"link"`, `"other"`, `"unreadable"`,
+    `"bare"`, `"bare-link"`, or `None` when nothing matches on the path.
+    """
+    current = os.path.realpath(root)
+    last = os.path.realpath(stop) if stop is not None else None
+    while True:
+        try:
+            mode = os.lstat(os.path.join(current, ".git")).st_mode
+        except (FileNotFoundError, NotADirectoryError):
+            bare = _bare_repository(current)
+            if bare:
+                return bare
+        except OSError:
+            return "unreadable"
+        else:
+            if stat.S_ISLNK(mode):
+                return "link"
+            if stat.S_ISDIR(mode):
+                return "dir"
+            if stat.S_ISREG(mode):
+                return "file"
+            return "other"
+        parent = os.path.dirname(current)
+        if current == last or parent == current:
+            return None
+        current = parent
+
+
+def incomplete_slots(records: List[dict]) -> List[tuple]:
+    """`(slot, last record)` of each slot with no `ran` and no `not_applicable` record (TASK 118 §3).
+
+    A slot is selected when it holds a record, so a slot with no record is never listed. Slots are
+    listed in the order of their first record.
+    """
+    slots = {}
+    for record in records:
+        slots.setdefault(record["slot"], []).append(record)
+    return [(slot, held[-1]) for slot, held in slots.items()
+            if not any(r["status"] in ("ran", "not_applicable") for r in held)]
+
+
+def external_section(records: List[dict]) -> dict:
+    """The external section of the report: its status and its records (TASK 118 R1.7).
+
+    The first match sets `status`: `NOT_RUN` when no record ran, `COMPLETE` when every selected
+    slot has a `ran` or a `not_applicable` record, `PARTIAL` otherwise.
+    """
+    if not any(r["status"] == "ran" for r in records):
+        status = "NOT_RUN"
+    elif incomplete_slots(records):
+        status = "PARTIAL"
+    else:
+        status = "COMPLETE"
+    return {"status": status, "tools": records}
+
+
+def _declined(slot: str, cmd: List[str], where: str, status: str, reason: str) -> dict:
+    """The record of a tool the scanner did not start (`not_run` or `not_applicable`)."""
+    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": status,
+            "exit_code": None, "reason": reason}
+
+
+def run_external_tools(project_path: str, types: List[str], fail_on=None) -> List[dict]:
+    """Run the external tools and return one tool record per tool (TASK 118 R1).
+
+    The slots `sast`, `secrets-tree` and `secrets-history` run for every project, also one with no
+    detected type; the others run for the project types that select them. A fallback starts only
+    when the first tool of its slot is `not_installed` or `timed_out`. A missing tool is non-fatal:
+    its record says so, and `run_audit.py` reports the slot as a part not run.
     """
     print(f"\n{'='*60}", file=sys.stderr)
     print(f"External Tools Scan: {', '.join(types)}", file=sys.stderr)
     print(f"{'='*60}", file=sys.stderr)
 
     cwd = project_path
-
-    # --- Cross-cutting scanners (run for any project type) ---
+    records = []
+
+    def run(slot, cmd, where=".", workdir=None):
+        record = run_tool(cmd, workdir or cwd, slot, where)
+        records.append(record)
+        return record
+
+    def run_with_fallback(slot, first, fallback):
+        if run(slot, first)["status"] in ("not_installed", "timed_out"):
+            run(slot, fallback)
+
+    # --- Cross-cutting scanners (run for any project, also with no detected type) ---
 
     # semgrep — de-facto SAST standard (2024+); auto-config picks rules by language.
-    run_command(["semgrep", "--config", "auto", "--error", "--quiet", "--timeout", "60", "."], cwd=cwd)
-
-    # Secret scanners — stronger than regex-only; run at least one.
-    # gitleaks is the more common; trufflehog is a fallback.
-    if not run_command(["gitleaks", "detect", "--no-banner", "--redact", "-s", "."], cwd=cwd):
-        run_command(["trufflehog", "filesystem", "--no-update", "."], cwd=cwd)
+    run("sast", ["semgrep", "--config", "auto", "--error", "--quiet", "--timeout", "60", "."])
+
+    # Secret scanners — stronger than regex-only. The working tree first, then the history.
+    # trufflehog exits 0 on a finding unless `--fail` is given (R2.10).
+    run_with_fallback("secrets-tree", GITLEAKS_TREE,
+                      ["trufflehog", "filesystem", "--no-update", "--fail", "."])
+    # The history slot has no fallback: `trufflehog git` ran the scanned repository's
+    # `core.fsmonitor` command (CVE-2025-41390), so only gitleaks reads the history (R4.3).
+    entry = find_git_entry(cwd)
+    if entry in ("dir", "file", "bare"):
+        run("secrets-history", GITLEAKS_HISTORY)
+    elif entry == "unreadable":
+        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
+                                 ".git could not be read"))
+    elif entry == "bare-link":
+        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
+                                 "the bare repository holds a symbolic link"))
+    elif entry == "link":
+        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
+                                 ".git is a symbolic link"))
+    elif entry == "other":
+        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
+                                 ".git is not a directory or a regular file"))
+    else:
+        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_applicable",
+                                 "no .git at or above the scanned root"))
 
     # --- Language/stack-specific scanners ---
 
     if "solidity" in types:
-        run_command(["slither", "."], cwd=cwd)
+        run("solidity", ["slither", "."])
 
     if "python" in types:
-        run_command(["bandit", "-r", ".", "-q"], cwd=cwd)
+        run("python-sast", ["bandit", "-r", ".", "-q"])
         # pip-audit replaces safety (Safety DB went commercial in 2024)
-        run_command(["pip-audit"], cwd=cwd)
+        run("python-deps", ["pip-audit"])
 
     # npm audit in each lockfile directory, whatever the detected types (TASK 111 R5.4); a project
-    # without an npm lockfile runs none, since npm stops with ENOLOCK there (R5.5).
+    # without an npm lockfile runs none, since npm stops with ENOLOCK there (R5.5). Under
+    # `--fail-on`, `--audit-level` makes npm exit non-zero at that threshold only (TASK 118 R2.10).
+    npm = ["npm", "audit", "--package-lock-only"]
+    if fail_on in NPM_AUDIT_LEVEL:
+        npm.append(f"--audit-level={NPM_AUDIT_LEVEL[fail_on]}")
     for lockfile in find_npm_lockfiles(cwd):
-        label = os.path.relpath(lockfile, cwd)
-        with npm_audit_dir(lockfile) as workdir:
-            if workdir is None:
-                print(f"[!] npm audit skipped for {label}: no package.json beside it", file=sys.stderr)
-                continue
-            print(f"[*] npm audit for {label}", file=sys.stderr)
-            run_command(["npm", "audit", "--package-lock-only"], cwd=str(workdir))
+        label = os.path.relpath(lockfile, cwd).replace(os.sep, "/")
+        slot = f"npm-audit:{label}"
+        try:
+            with npm_audit_dir(lockfile) as workdir:
+                if workdir is None:
+                    reason = "no package.json beside it"
+                else:
+                    reason = None
+                    print(f"[*] npm audit for {printable(label)}", file=sys.stderr)
+                    run(slot, npm, where=label, workdir=str(workdir))
+        except LockfileCopyError:
+            reason = "the lockfile could not be copied"
+        if reason:
+            print(f"[!] npm audit skipped for {printable(label)}: {reason}", file=sys.stderr)
+            records.append(_declined(slot, npm, label, "not_run", reason))
     # yarn reads `.yarnrc` and `.yarnrc.yml` where it runs, and `yarnPath` there names a script it
     # executes. It runs in a copy of the lockfile and its `package.json`, as npm does, and the copy
     # keeps the dependency fields only: a corepack `yarn` shim would fetch and run the version that
     # `packageManager` or `devEngines` names (TASK 112 R5.1).
     yarn_lock = Path(cwd) / "yarn.lock"
     if "javascript" in types and (yarn_lock.exists() or yarn_lock.is_symlink()):
+        yarn = ["yarn", "audit"]
         if yarn_lock.is_symlink() or not yarn_lock.is_file():
-            print("[!] yarn audit skipped: yarn.lock is a link or not a regular file", file=sys.stderr)
+            reason = "yarn.lock is a link or not a regular file"
         else:
-            with npm_audit_dir(yarn_lock) as workdir:
-                if workdir is None:
-                    print("[!] yarn audit skipped: no package.json beside yarn.lock", file=sys.stderr)
-                elif not _keep_dependency_fields(workdir / "package.json"):
-                    print("[!] yarn audit skipped: package.json is not a JSON object", file=sys.stderr)
-                else:
-                    run_command(["yarn", "audit"], cwd=str(workdir))
+            reason = None
+            try:
+                with npm_audit_dir(yarn_lock) as workdir:
+                    if workdir is None:
+                        reason = "no package.json beside yarn.lock"
+                    elif not _keep_dependency_fields(workdir / "package.json"):
+                        reason = "package.json is not a JSON object"
+                    else:
+                        run("yarn-audit", yarn, where="yarn.lock", workdir=str(workdir))
+            except LockfileCopyError:
+                reason = "the lockfile could not be copied"
+        if reason:
+            print(f"[!] yarn audit skipped: {reason}", file=sys.stderr)
+            records.append(_declined("yarn-audit", yarn, "yarn.lock", "not_run", reason))
 
     if "rust" in types:
-        run_command(["cargo", "audit"], cwd=cwd)
-        run_command(["cargo", "clippy"], cwd=cwd)
+        run("rust-deps", ["cargo", "audit"])
+        run("rust-lint", ["cargo", "clippy"])
 
     if "go" in types:
-        run_command(["govulncheck", "./..."], cwd=cwd)
-        run_command(["gosec", "./..."], cwd=cwd)
+        run("go-deps", ["govulncheck", "./..."])
+        run("go-sast", ["gosec", "./..."])
 
     if "iac" in types:
-        run_command(["checkov", "-d", "."], cwd=cwd)
-        run_command(["trivy", "fs", "--scanners", "misconfig", "."], cwd=cwd)
+        run("iac", ["checkov", "-d", "."])
+        # trivy exits 0 on a finding unless `--exit-code` is given (R2.10).
+        run("iac-misconfig", ["trivy", "fs", "--scanners", "misconfig", "--exit-code", "1", "."])
 
     if "mcp" in types:
         # snyk-agent-scan (formerly Invariant mcp-scan): tool poisoning, tool
@@ -105,5 +254,6 @@
         # SAFETY: NEVER pass --dangerously-skip-permissions-style flags here
         # (e.g. --dangerously-run-mcp-servers) — an audit must not auto-start
         # untrusted MCP servers; starting them is the operator's consent-gated call.
-        if not run_command(["snyk-agent-scan", "."], cwd=cwd):
-            run_command(["mcp-scan"], cwd=cwd)  # legacy Invariant CLI fallback
+        run_with_fallback("mcp", ["snyk-agent-scan", "."], ["mcp-scan"])  # legacy Invariant CLI
+
+    return records
diff --git a/.agent/skills/security-audit/scripts/run_audit.py b/.agent/skills/security-audit/scripts/run_audit.py
--- a/.agent/skills/security-audit/scripts/run_audit.py
+++ b/.agent/skills/security-audit/scripts/run_audit.py
@@ -1,17 +1,21 @@
 #!/usr/bin/env python3
 """
 Skill: security-audit
-Script: run_audit.py v3.11
+Script: run_audit.py v3.12
 Purpose: CLI entry point for security audit scanner.
 Usage: python run_audit.py [project_path] [--scan-type all|deps|secrets|patterns|config|iac|mcp|external|sbom]
        [--fail-on critical|high|medium] [--output json|summary] [--no-limit]
+Exit: 0 every requested part ran and no gate cause; 1 a `--fail-on` cause (a finding at the
+      threshold or above, or an external tool's non-zero exit), or a JSON `error` for a missing
+      directory or a non-positive `--max-size`; 2 a usage error (argparse); 3 a requested part did
+      not run.
 """
 import argparse
 import json
 import os
 import sys
 from datetime import datetime
-from typing import Any, Dict
+from typing import Any, Dict, List
 
 # Fix Windows console encoding for Unicode output
 try:
@@ -24,6 +28,9 @@
     SEVERITY_ORDER,
     __version__ as AUDIT_VERSION,
     detect_project_types,
+    external_section,
+    incomplete_slots,
+    printable,
     run_external_tools,
     scan_code_patterns,
     scan_configuration,
@@ -35,21 +42,26 @@
 )
 from audit import config as _audit_config
 
-
-def run_full_scan(project_path: str, scan_type: str = "all", no_limit: bool = False) -> Dict[str, Any]:
-    """Execute security validation scans and produce a unified report."""
+#: The severities the summary counts (TASK 118 R2.4).
+SUMMARY_SEVERITIES = ("critical", "high", "medium", "low", "info")
+#: Findings each section keeps unless `--no-limit` is given; the summary counts all of them.
+MAX_FINDINGS = 30
+
+
+def run_full_scan(project_path: str, scan_type: str = "all", no_limit: bool = False,
+                  fail_on=None) -> Dict[str, Any]:
+    """Execute the requested scans and produce a unified report.
+
+    The in-process scans of `scan_type` run first, then the external layer for `all` and
+    `external`, also for a project with no detected type (TASK 118 R1.4). The summary counts every
+    finding before each section is cut to `MAX_FINDINGS` (R2.5). `fail_on` sets npm's
+    `--audit-level` (R2.10).
+    """
     report = {
         "project": project_path,
         "timestamp": datetime.now().isoformat(),
         "scan_type": scan_type,
         "scans": {},
-        "summary": {
-            "total_findings": 0,
-            "critical": 0,
-            "high": 0,
-            "medium": 0,
-            "overall_status": "[OK] SECURE"
-        }
     }
 
     scanners = {
@@ -62,48 +74,95 @@
         "sbom": ("sbom", scan_sbom),
     }
 
-    max_findings = 999999 if no_limit else 30
-
     for key, (name, scanner) in scanners.items():
         if scan_type == "all" or scan_type == key:
             print(f"[*] Running {name} scan...", file=sys.stderr)
-            result = scanner(project_path)
-
-            # Truncate findings (already sorted by severity)
-            if len(result.get("findings", [])) > max_findings:
-                truncated = len(result["findings"]) - max_findings
-                result["findings"] = result["findings"][:max_findings]
-                result["truncated"] = truncated
-
-            report["scans"][name] = result
-
-            for finding in result.get("findings", []):
-                sev = finding.get("severity", "low")
-                report["summary"]["total_findings"] += 1
-                if sev in report["summary"]:
-                    report["summary"][sev] += 1
-
-    if report["summary"]["critical"] > 0:
-        report["summary"]["overall_status"] = "[!!] CRITICAL ISSUES FOUND"
-    elif report["summary"]["high"] > 0:
-        report["summary"]["overall_status"] = "[!] HIGH RISK ISSUES"
-    elif report["summary"]["total_findings"] > 0:
-        report["summary"]["overall_status"] = "[?] REVIEW RECOMMENDED"
+            report["scans"][name] = scanner(project_path)
+
+    if scan_type in ("all", "external"):
+        types = detect_project_types(project_path)
+        report["external"] = external_section(run_external_tools(project_path, types, fail_on))
+
+    report["summary"] = summarize(report)
+
+    # Truncate findings (already sorted by severity), after the summary counted them all.
+    if not no_limit:
+        for result in report["scans"].values():
+            if len(result.get("findings", [])) > MAX_FINDINGS:
+                result["truncated"] = len(result["findings"]) - MAX_FINDINGS
+                result["findings"] = result["findings"][:MAX_FINDINGS]
 
     return report
 
 
+def summarize(report: Dict[str, Any]) -> Dict[str, Any]:
+    """The summary of a report (TASK 118 R2.1 to R2.4, R2.9)."""
+    summary = {"total_findings": 0, **dict.fromkeys(SUMMARY_SEVERITIES, 0)}
+    not_run: List[str] = []
+    for name, result in report["scans"].items():
+        for finding in result.get("findings", []):
+            summary["total_findings"] += 1
+            sev = finding.get("severity", "low")
+            if sev in summary:
+                summary[sev] += 1
+            if finding.get("audited") is False:
+                not_run.append(f"{name}: {finding.get('message')}")
+
+    records = report.get("external", {}).get("tools", [])
+    for slot, last in incomplete_slots(records):
+        entry = f"external {slot}: {last['tool']} {last['status']}"
+        if last["status"] == "not_run":
+            entry += f", {last['reason']}"
+        not_run.append(entry)
+    tool_exits = [f"{r['tool']} exited {r['exit_code']} ({r['slot']})"
+                  for r in records if r["status"] == "ran" and r["exit_code"] != 0]
+
+    summary["not_run"] = not_run
+    summary["scan_complete"] = not not_run
+    summary["tool_exits"] = tool_exits
+
+    if summary["critical"] > 0:
+        summary["overall_status"] = "[!!] CRITICAL ISSUES FOUND"
+    elif summary["high"] > 0:
+        summary["overall_status"] = "[!] HIGH RISK ISSUES"
+    elif not_run:
+        summary["overall_status"] = f"[?] INCOMPLETE: {len(not_run)} part(s) did not run"
+    elif summary["total_findings"] > 0 or tool_exits:
+        summary["overall_status"] = "[?] REVIEW RECOMMENDED"
+    else:
+        summary["overall_status"] = "[OK] SECURE"
+    return summary
+
+
+def gate_causes(report: Dict[str, Any], fail_on) -> List[str]:
+    """Each cause of exit 1 under `--fail-on` (TASK 118 R2.6, R2.8); empty without `fail_on`."""
+    if not fail_on:
+        return []
+    summary = report["summary"]
+    threshold = SEVERITY_ORDER[fail_on]
+    causes = [f"{summary[sev]} {sev} finding(s)" for sev, order in SEVERITY_ORDER.items()
+              if order <= threshold and summary.get(sev, 0) > 0]
+    return causes + list(summary["tool_exits"])
+
+
+def exit_code(report: Dict[str, Any], fail_on) -> int:
+    """1 on a `--fail-on` cause, else 3 when a requested part did not run, else 0 (R2.6, R2.7)."""
+    if gate_causes(report, fail_on):
+        return 1
+    return 0 if report["summary"]["scan_complete"] else 3
+
+
 def print_summary(report: Dict[str, Any]):
-    """Print human-readable summary to stdout."""
+    """Print human-readable summary to stdout; text from the scanned tree is escaped (R1.10)."""
+    summary = report["summary"]
     print(f"\n{'='*60}")
-    print(f"Security Scan v{AUDIT_VERSION}: {report['project']}")
+    print(f"Security Scan v{AUDIT_VERSION}: {printable(report['project'])}")
     print(f"Timestamp: {report['timestamp']}")
     print(f"{'='*60}")
-    print(f"Status: {report['summary']['overall_status']}")
-    print(f"Total Findings: {report['summary']['total_findings']}")
-    print(f"  Critical: {report['summary']['critical']}")
-    print(f"  High: {report['summary']['high']}")
-    print(f"  Medium: {report['summary']['medium']}")
+    print(f"Status: {summary['overall_status']}")
+    print(f"Total Findings: {summary['total_findings']}")
+    for sev in SUMMARY_SEVERITIES:
+        print(f"  {sev.capitalize()}: {summary[sev]}")
 
     total_skipped = sum(s.get('skipped_files', 0) for s in report['scans'].values())
     if total_skipped > 0:
@@ -113,10 +172,19 @@
     if total_truncated > 0:
         print(f"  Truncated: {total_truncated} findings hidden (use --no-limit)")
 
+    if summary["not_run"]:
+        print("Not run:")
+        for entry in summary["not_run"]:
+            print(f"  - {printable(entry)}")
+    if summary["tool_exits"]:
+        print("Tool exits:")
+        for entry in summary["tool_exits"]:
+            print(f"  - {printable(entry)}")
+
     print(f"{'='*60}\n")
 
     for scan_name, scan_result in report['scans'].items():
-        print(f"\n{scan_name.upper()}: {scan_result['status']}")
+        print(f"\n{scan_name.upper()}: {printable(scan_result['status'])}")
         for finding in scan_result.get('findings', [])[:10]:
             sev = finding.get('severity', 'INFO').upper()
             desc = finding.get('type') or finding.get('pattern') or finding.get('issue')
@@ -130,10 +198,20 @@
                 f_str += f":{finding['line']}"
             if 'message' in finding:
                 f_str += f" - {finding['message']}"
-            print(f_str)
-
-
-def main():
+            print(printable(f_str))
+
+    if "external" in report:
+        print(f"\nEXTERNAL: {report['external']['status']}")
+        for record in report["external"]["tools"]:
+            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
+            if record["status"] in ("ran", "killed"):
+                line += f" (exit {record['exit_code']})"
+            elif record["reason"]:
+                line += f" ({record['reason']})"
+            print(printable(line))
+
+
+def main(argv=None):
     parser = argparse.ArgumentParser(description=f"Security Audit Tool v{AUDIT_VERSION}")
     parser.add_argument("project_path", nargs="?", default=".", help="Project directory")
     parser.add_argument("--scan-type",
@@ -142,14 +220,15 @@
     parser.add_argument("--output", choices=["json", "summary"], default="summary",
                         help="Output format")
     parser.add_argument("--fail-on", choices=["critical", "high", "medium"],
-                        default=None, help="Exit with code 1 if findings >= this severity (for CI/CD)")
+                        default=None, help="Exit with code 1 if findings >= this severity, or an "
+                                           "external tool exits non-zero (for CI/CD)")
     parser.add_argument("--no-limit", action="store_true",
                         help="Do not truncate findings list")
     parser.add_argument("--max-size", type=int, default=None, metavar="MB",
                         help=f"Max file size to scan in MB (default: {_audit_config.MAX_FILE_SIZE // (1024*1024)}). "
                              "Increase for large minified bundles.")
 
-    args = parser.parse_args()
+    args = parser.parse_args(argv)
 
     if args.max_size is not None:
         if args.max_size <= 0:
@@ -161,33 +240,26 @@
         print(json.dumps({"error": f"Directory not found: {args.project_path}"}))
         sys.exit(1)
 
-    exit_code = 0
-
-    # Run Pattern Matching Scans
-    if args.scan_type != "external":
-        result = run_full_scan(args.project_path, args.scan_type, args.no_limit)
-
-        if args.output == "summary":
-            print_summary(result)
-        else:
-            print(json.dumps(result, indent=2))
-
-        # CI/CD gate: exit with error if findings meet threshold
-        if args.fail_on:
-            threshold = SEVERITY_ORDER[args.fail_on]
-            for sev_name, sev_order in SEVERITY_ORDER.items():
-                if sev_order <= threshold and result["summary"].get(sev_name, 0) > 0:
-                    exit_code = 1
-                    print(f"\n[GATE] --fail-on {args.fail_on}: Found {sev_name} issues. Exit code 1.")
-                    break
-
-    # Run External Tools
-    if args.scan_type == "all" or args.scan_type == "external":
-        types = detect_project_types(args.project_path)
-        if types:
-            run_external_tools(args.project_path, types)
-
-    sys.exit(exit_code)
+    report = run_full_scan(args.project_path, args.scan_type, args.no_limit, args.fail_on)
+
+    if args.output == "summary":
+        print_summary(report)
+    else:
+        print(json.dumps(report, indent=2))
+    sys.stdout.flush()
+
+    code = exit_code(report, args.fail_on)
+    causes = gate_causes(report, args.fail_on)
+    if causes:
+        print(f"\n[GATE] --fail-on {args.fail_on}:", file=sys.stderr)
+        for cause in causes:
+            print(f"  - {printable(cause)}", file=sys.stderr)
+    if not report["summary"]["scan_complete"]:
+        print("\n[INCOMPLETE]", file=sys.stderr)
+        for entry in report["summary"]["not_run"]:
+            print(f"  - {printable(entry)}", file=sys.stderr)
+
+    sys.exit(code)
 
 
 if __name__ == "__main__":
diff --git a/tests/test_lockfile_audit.py b/tests/test_lockfile_audit.py
--- a/tests/test_lockfile_audit.py
+++ b/tests/test_lockfile_audit.py
@@ -21,6 +21,32 @@
 * the copy holds the original `package.json`, never a linked one (``TC-L16``, ``TC-L17``);
 * a finding outranks an unaudited lockfile in the status; an unexpected vulnerability field and a
   timeout yield a named `info` finding (``TC-L18`` to ``TC-L20``).
+
+TASK 118 (WI-42) adds the status of each external tool and the findings of every npm severity. Its
+fake tools are `/bin/sh` scripts in a `bin` directory that is the whole `PATH`, so a tool installed
+on the runner does not start. This file pins:
+
+* `run_audit.py` reports each external tool and exits 3 when a part did not run (``TC-E1``,
+  ``TC-E11``, ``TC-E13``, ``TC-E15``); a tool's record says `ran`, `not_installed` or `timed_out`
+  (``TC-E2``, ``TC-E4``), and a fallback fills its slot (``TC-E5``);
+* a tool's non-zero exit fails `--fail-on` (``TC-E3``, ``TC-E10``), and the options that make a
+  finding exit non-zero are passed (``TC-E9``);
+* the secret scan reads the working tree with `--no-git`, and the history slot follows the `.git`
+  at or above the scanned root, never through a link (``TC-E6``, ``TC-E7``);
+* stdout holds one JSON document (``TC-E8``); the summary output lists each tool (``TC-E14``); the
+  external status and the overall status (``TC-E12``, ``TC-E16``); the summary counts every
+  finding before the cut (``TC-E17``);
+* npm advisories of every severity are findings, with a count map per lockfile, and an unaudited
+  lockfile carries `audited: false` (``TC-D1`` to ``TC-D7``; ``TC-D1`` replaces ``TC-L23``); a
+  lockfile that cannot be copied is not audited, and the scanner still prints its report
+  (``TC-D8``);
+* a tool killed by a signal leaves its slot a part not run (``TC-E18``), and text from the scanned
+  tree reaches printed output with its control characters escaped (``TC-E19``).
+
+`RUN_AUDIT_PATH` and `RUN_AUDIT_CMD` name the `run_audit.py` that the tests load and start; a test
+reads them at call time. The in-process cases stop the `.git` walk at their temporary directory;
+the subprocess cases cannot. TC-E1 accepts either status of the history slot, and TC-E3 assumes
+no `.git` link or special file above the system temporary directory.
 """
 import importlib
 import importlib.util
@@ -37,6 +63,8 @@
 PROJECT_ROOT = Path(__file__).resolve().parent.parent
 PACKAGE = PROJECT_ROOT / ".agent" / "skills" / "security-audit" / "scripts" / "audit"
 NAME = "security_audit_scanner_under_test"
+RUN_AUDIT_PATH = PACKAGE.parent / "run_audit.py"
+RUN_AUDIT_CMD = (sys.executable, str(RUN_AUDIT_PATH))
 
 
 def _load():
@@ -48,10 +76,28 @@
         sys.modules[NAME] = module
         spec.loader.exec_module(module)
     return (importlib.import_module(f"{NAME}.scanners"),
-            importlib.import_module(f"{NAME}.external"))
-
-
-scanners, external = _load()
+            importlib.import_module(f"{NAME}.external"),
+            importlib.import_module(f"{NAME}.helpers"))
+
+
+scanners, external, helpers = _load()
+
+
+def _run_audit_module():
+    """`RUN_AUDIT_PATH`, loaded while `audit` names the package under test."""
+    saved = sys.modules.get("audit")
+    sys.modules["audit"] = sys.modules[NAME]
+    try:
+        spec = importlib.util.spec_from_file_location("security_audit_run_audit_under_test",
+                                                      RUN_AUDIT_PATH)
+        module = importlib.util.module_from_spec(spec)
+        spec.loader.exec_module(module)
+    finally:
+        if saved is None:
+            del sys.modules["audit"]
+        else:
+            sys.modules["audit"] = saved
+    return module
 
 FAKE_NPM = """#!/bin/sh
 printf '%s\\t%s\\t%s\\t%s\\n' "$PWD" "$(ls -A | tr '\\n' ' ')" "$*" "$(cat package.json)" >> "$FAKE_NPM_LOG"
@@ -59,6 +105,15 @@
 """
 HIGH = {"vulnerabilities": {"x": {"severity": "high"}}}
 COPY = "package-lock.json package.json"
+GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
+GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
+ZERO_COUNTS = dict.fromkeys(("critical", "high", "moderate", "low", "info", "unknown"), 0)
+
+
+def _ran(cmd, slot, where="."):
+    """The tool record of a tool that ran and exited 0."""
+    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": "ran",
+            "exit_code": 0, "reason": None}
 
 
 class AuditTestCase(unittest.TestCase):
@@ -272,11 +327,16 @@
         with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
             self.assertEqual(self.scan()["status"], "[?] Not audited: 2 npm lockfile(s)")
 
-    def test_l23_a_moderate_advisory_is_no_finding(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
+    def test_d1_every_npm_severity_is_a_finding(self):
+        """TC-D1 (TASK 118 R3.1), in place of TC-L23: the base kept critical and high only."""
+        self.lockfile("sub")
+        self.set_reply({"vulnerabilities": {"a": {"severity": "moderate"}, "b": {"severity": "low"},
+                                            "c": {"severity": "info"}}})
         findings = [f for f in self.scan()["findings"] if f.get("type") == "npm audit"]
-        self.assertEqual(findings, [])
+        self.assertEqual([(f["severity"], f["message"]) for f in findings], [
+            ("medium", "sub/package-lock.json: 1 moderate vulnerabilities in dependencies"),
+            ("low", "sub/package-lock.json: 1 low vulnerabilities in dependencies"),
+            ("info", "sub/package-lock.json: 1 info vulnerabilities in dependencies")])
 
     def test_l15_each_audit_has_a_60_second_timeout(self):
         self.lockfile("sub")
@@ -291,11 +351,12 @@
     def external(self, types):
         recorded = []
 
-        def record(cmd, cwd=None, **_kw):
+        def record(cmd, cwd=None, slot=None, where=".", **_kw):
             entries = " ".join(sorted(os.listdir(cwd))) if cwd else ""
             recorded.append((list(cmd), Path(cwd).resolve() if cwd else None, entries))
-
-        with mock.patch.object(external, "run_command", side_effect=record):
+            return _ran(cmd, slot, where)
+
+        with mock.patch.object(external, "run_tool", side_effect=record):
             external.run_external_tools(str(self.project), types)
         return recorded
 
@@ -334,12 +395,13 @@
         (self.project / ".yarnrc.yml").write_text("yarnPath: evil.js\n")
         copies = []
 
-        def record(cmd, cwd=None, **_kw):
+        def record(cmd, cwd=None, slot=None, where=".", **_kw):
             if cmd[:1] == ["yarn"]:
                 copies.append((list(cmd), Path(cwd).resolve(), " ".join(sorted(os.listdir(cwd))),
                                json.loads((Path(cwd) / "package.json").read_text())))
-
-        with mock.patch.object(external, "run_command", side_effect=record):
+            return _ran(cmd, slot, where)
+
+        with mock.patch.object(external, "run_tool", side_effect=record):
             external.run_external_tools(str(self.project), ["javascript"])
         self.assertEqual(len(copies), 1, copies)
         cmd, where, entries, package = copies[0]
@@ -371,5 +433,502 @@
                 self.assertEqual(yarn, [])
 
 
+class TestDependencySeverities(AuditTestCase):
+    """TC-D2 to TC-D7 (TASK 118 R3): npm advisories at every severity."""
+
+    def npm_findings(self, result):
+        return [f for f in result["findings"] if f.get("type") == "npm audit"]
+
+    def test_d2_a_moderate_advisory_fails_fail_on_medium_only(self):
+        self.lockfile("sub")
+        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
+        run_audit = _run_audit_module()
+        report = run_audit.run_full_scan(str(self.project), "deps", fail_on="medium")
+        self.assertEqual(run_audit.exit_code(report, "medium"), 1)
+        self.assertEqual(run_audit.exit_code(report, "high"), 0)
+
+    def test_d3_an_info_advisory_is_audited_and_a_missing_npm_is_not(self):
+        self.lockfile("sub")
+        self.set_reply({"vulnerabilities": {"x": {"severity": "info"}}})
+        result = self.scan()
+        self.assertFalse(result["status"].startswith("[?] Not audited"), result["status"])
+        self.assertEqual([f.get("audited", True) for f in self.npm_findings(result)], [True])
+        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
+            [finding] = self.npm_findings(self.scan())
+        self.assertEqual((finding["severity"], finding["audited"]), ("info", False))
+
+    def test_d4_an_unknown_severity_and_an_entry_that_is_not_a_map(self):
+        self.lockfile("sub")
+        self.set_reply({"vulnerabilities": {"x": {"severity": "weird"}}})
+        result = self.scan()
+        self.assertEqual(result["npm_audit_counts"]["sub/package-lock.json"]["unknown"], 1)
+        self.assertEqual([(f["severity"], f["message"]) for f in self.npm_findings(result)], [
+            ("low", "sub/package-lock.json: 1 vulnerabilities of unknown severity")])
+        self.set_reply({"vulnerabilities": {"x": "high"}})
+        counts = self.scan()["npm_audit_counts"]["sub/package-lock.json"]
+        self.assertEqual((counts["low"], counts["unknown"]), (1, 0))
+
+    def test_d5_each_finished_audit_has_all_six_counts(self):
+        self.lockfile("sub")
+        self.assertEqual(self.scan()["npm_audit_counts"], {"sub/package-lock.json": ZERO_COUNTS})
+        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "low"}}})
+        self.assertEqual(self.scan()["npm_audit_counts"]["sub/package-lock.json"],
+                         dict(ZERO_COUNTS, low=2))
+        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
+            self.assertEqual(self.scan()["npm_audit_counts"], {})
+
+    def test_d6_section_status_first_match_wins(self):
+        self.lockfile("sub")
+        for label, reply, status in (
+                ("critical", {"vulnerabilities": {"x": {"severity": "critical"}}},
+                 "[!!] Critical vulnerabilities"),
+                ("high", HIGH, "[!] HIGH: Dependency issues"),
+                ("moderate", {"vulnerabilities": {"x": {"severity": "moderate"}}},
+                 "[?] Dependency issues below high"),
+                ("low", {"vulnerabilities": {"x": {"severity": "low"}}},
+                 "[?] Dependency issues below high"),
+                ("info only", {"vulnerabilities": {"x": {"severity": "info"}}}, "[OK] Secure"),
+                ("none", {"vulnerabilities": {}}, "[OK] Secure")):
+            with self.subTest(case=label):
+                self.set_reply(reply)
+                self.assertEqual(self.scan()["status"], status)
+        with self.subTest(case="not audited outranks moderate"):
+            self.lockfile("other", content='{"name": "broken"}')
+            self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
+            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")
+
+    def test_d7_summary_counts_low_and_info_and_findings_are_sorted(self):
+        self.lockfile("sub")
+        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "info"},
+                                            "c": {"severity": "critical"}}})
+        report = _run_audit_module().run_full_scan(str(self.project), "deps")
+        summary = report["summary"]
+        self.assertEqual((summary["critical"], summary["low"], summary["info"]), (1, 1, 1))
+        # Two lockfiles each yield a critical and a low finding: unsorted, a low one precedes the
+        # second critical one.
+        self.lockfile("tub")
+        self.set_reply({"vulnerabilities": {"a": {"severity": "low"},
+                                            "c": {"severity": "critical"}}})
+        severities = [f["severity"] for f in self.scan()["findings"]]
+        self.assertEqual(severities, ["critical", "critical", "low", "low"])
+
+    def test_d8_a_lockfile_that_cannot_be_copied_is_not_audited(self):
+        sub = self.project / "sub"
+        sub.mkdir()
+        os.mkfifo(sub / "package-lock.json")
+        (sub / "package.json").write_text('{"name": "x"}')
+        [info] = self.infos(self.scan()["findings"])
+        self.assertEqual((info["message"], info["audited"]),
+                         ("sub/package-lock.json: not audited, the lockfile could not be copied",
+                          False))
+        proc = subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", "deps",
+                               "--output", "json"], capture_output=True, text=True, timeout=120)
+        self.assertEqual(json.loads(proc.stdout)["summary"]["scan_complete"], False)
+        self.assertEqual(proc.returncode, 3, proc.stderr)
+
+
+class ToolCase(unittest.TestCase):
+    """A temporary project, and a `bin` directory of fake tools that is the whole `PATH`.
+
+    The `.git` walk of `run_external_tools` stops at the temporary directory, so a `.git` above it
+    takes no part.
+    """
+
+    def setUp(self):
+        self.tmp = Path(tempfile.mkdtemp()).resolve()
+        self.addCleanup(shutil.rmtree, self.tmp)
+        self.project = self.tmp / "project"
+        self.project.mkdir()
+        self.bin = self.tmp / "bin"
+        self.bin.mkdir()
+        patcher = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
+        patcher.start()
+        self.addCleanup(patcher.stop)
+        walk = external.find_git_entry
+        stopped = mock.patch.object(external, "find_git_entry",
+                                    side_effect=lambda root, stop=None: walk(root, stop=self.tmp))
+        stopped.start()
+        self.addCleanup(stopped.stop)
+
+    def tool(self, name, body="exit 0"):
+        path = self.bin / name
+        path.write_text(f"#!/bin/sh\n{body}\n")
+        path.chmod(0o755)
+
+    def tools(self, *names):
+        for name in names:
+            self.tool(name)
+
+    def records(self, types=(), fail_on=None):
+        return external.run_external_tools(str(self.project), list(types), fail_on=fail_on)
+
+    @staticmethod
+    def slot(records, slot):
+        return [r for r in records if r["slot"] == slot]
+
+    def cli(self, *args):
+        """`run_audit.py` as a subprocess, with `PATH` the fake tools only."""
+        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
+        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), *args], env=env,
+                              capture_output=True, text=True, timeout=120)
+
+    def cli_json(self, *args):
+        proc = self.cli(*args, "--output", "json")
+        return proc, json.loads(proc.stdout)
+
+
+class TestToolRecords(ToolCase):
+    """TC-E2, TC-E4 to TC-E7, TC-E9, TC-E13, TC-E15, TC-E16 drive `run_external_tools` in process."""
+
+    def test_e2_a_tool_that_exits_0_is_ran(self):
+        self.tool("semgrep")
+        [record] = self.slot(self.records(), "sast")
+        self.assertEqual((record["status"], record["exit_code"], record["tool"], record["where"]),
+                         ("ran", 0, "semgrep", "."))
+        self.assertIsNone(record["reason"])
+
+    def test_e2_a_missing_tool_is_not_installed(self):
+        [record] = self.slot(self.records(), "sast")
+        self.assertEqual((record["status"], record["exit_code"]), ("not_installed", None))
+
+    def test_e4_a_timeout_starts_the_fallback_of_the_tree_slot_only(self):
+        self.tool("gitleaks", "exec /bin/sleep 5")
+        self.tool("trufflehog")
+        (self.project / ".git").mkdir()
+        with mock.patch.object(helpers, "TOOL_TIMEOUT", 1):
+            records = self.records()
+        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
+                         [("gitleaks", "timed_out"), ("trufflehog", "ran")])
+        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-history")],
+                         [("gitleaks", "timed_out")])
+        self.assertIn("secrets-history", [slot for slot, _ in external.incomplete_slots(records)])
+
+    def test_e5_the_fallback_fills_the_tree_slot_and_the_history_slot_has_none(self):
+        self.tool("trufflehog")
+        (self.project / ".git").mkdir()
+        records = self.records()
+        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
+                         [("gitleaks", "not_installed"), ("trufflehog", "ran")])
+        self.assertEqual([r["tool"] for r in self.slot(records, "secrets-history")], ["gitleaks"])
+        missing = [slot for slot, _ in external.incomplete_slots(records)]
+        self.assertIn("secrets-history", missing)
+        self.assertNotIn("secrets-tree", missing)
+
+    def test_e6_the_git_entry_at_or_above_the_root(self):
+        find = external.find_git_entry.side_effect
+        self.assertIsNone(find(str(self.project)))
+        cases = (("a directory", lambda g: g.mkdir(), "dir"),
+                 ("a file", lambda g: g.write_text("gitdir: elsewhere\n"), "file"),
+                 ("a link", lambda g: g.symlink_to(self.tmp / "real", target_is_directory=True),
+                  "link"),
+                 ("a fifo", lambda g: os.mkfifo(g), "other"))
+        (self.tmp / "real").mkdir()
+        for label, make, kind in cases:
+            with self.subTest(case=label):
+                git = self.project / ".git"
+                make(git)
+                try:
+                    self.assertEqual(find(str(self.project)), kind)
+                finally:
+                    shutil.rmtree(git) if git.is_dir() and not git.is_symlink() else git.unlink()
+        with self.subTest(case="in the parent"):
+            (self.tmp / ".git").mkdir()
+            self.assertEqual(find(str(self.project)), "dir")
+            (self.tmp / ".git").rmdir()
+        with self.subTest(case="a root through a link"):
+            sub = self.tmp / "repo" / "sub"
+            sub.mkdir(parents=True)
+            (self.tmp / "repo" / ".git").mkdir()
+            (self.tmp / "alias").symlink_to(sub, target_is_directory=True)
+            self.assertEqual(external.find_git_entry(str(self.tmp / "alias"), stop=self.tmp), "dir")
+
+    def test_e6_the_history_slot_by_git_entry(self):
+        log = self.tmp / "gitleaks.log"
+        self.tool("gitleaks", f'printf "%s|%s\\n" "$PWD" "$*" >> "{log}"')
+        [record] = self.slot(self.records(), "secrets-history")
+        self.assertEqual((record["status"], record["reason"], record["command"]),
+                         ("not_applicable", "no .git at or above the scanned root", GITLEAKS_HISTORY))
+        (self.project / ".git").symlink_to(self.tmp, target_is_directory=True)
+        [record] = self.slot(self.records(), "secrets-history")
+        self.assertEqual((record["status"], record["reason"]), ("not_run", ".git is a symbolic link"))
+        (self.project / ".git").unlink()
+        expected = f"{self.project}|{' '.join(GITLEAKS_HISTORY[1:])}"
+        cases = (("a directory at the root", lambda: (self.project / ".git").mkdir()),
+                 ("a file at the root",
+                  lambda: (self.project / ".git").write_text("gitdir: elsewhere\n")),
+                 ("a directory in the parent", lambda: (self.tmp / ".git").mkdir()),
+                 ("a bare repository at the root", lambda: self.bare(self.project)))
+        for label, make in cases:
+            with self.subTest(case=label):
+                make()
+                if log.exists():
+                    log.unlink()
+                try:
+                    [record] = self.slot(self.records(), "secrets-history")
+                    self.assertEqual((record["status"], record["command"]),
+                                     ("ran", GITLEAKS_HISTORY))
+                    runs = [run for run in log.read_text().splitlines() if "--no-git" not in run]
+                    self.assertEqual(runs, [expected])
+                finally:
+                    for path in (self.project / ".git", self.tmp / ".git", self.project / "HEAD",
+                                 self.project / "objects", self.project / "refs"):
+                        if path.is_dir():
+                            shutil.rmtree(path)
+                        elif path.exists():
+                            path.unlink()
+
+    def bare(self, root):
+        (root / "HEAD").write_text("ref: refs/heads/main\n")
+        (root / "objects").mkdir()
+        (root / "refs").mkdir()
+
+    def test_e6_a_bare_repository_and_an_unreadable_directory(self):
+        find = external.find_git_entry.side_effect
+        self.bare(self.project)
+        self.assertEqual(find(str(self.project)), "bare")
+        shutil.rmtree(self.project / "objects")
+        (self.tmp / "objects").mkdir()
+        (self.project / "objects").symlink_to(self.tmp / "objects", target_is_directory=True)
+        self.assertEqual(find(str(self.project)), "bare-link")
+        for name in ("HEAD", "objects", "refs"):
+            path = self.project / name
+            shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()
+        if os.geteuid() == 0:
+            self.skipTest("root reads a directory without its search permission")
+        locked = self.project / "locked"
+        locked.mkdir()
+        locked.chmod(0o600)
+        self.addCleanup(locked.chmod, 0o700)
+        self.assertEqual(find(str(locked)), "unreadable")
+
+    def test_e6_each_declined_history_record(self):
+        for kind, status, reason in (
+                ("link", "not_run", ".git is a symbolic link"),
+                ("other", "not_run", ".git is not a directory or a regular file"),
+                ("unreadable", "not_run", ".git could not be read"),
+                ("bare-link", "not_run", "the bare repository holds a symbolic link"),
+                (None, "not_applicable", "no .git at or above the scanned root")):
+            with self.subTest(kind=kind):
+                external.find_git_entry.side_effect = lambda root, stop=None, kind=kind: kind
+                records = self.records()
+                [record] = self.slot(records, "secrets-history")
+                self.assertEqual((record["status"], record["reason"], record["command"]),
+                                 (status, reason, GITLEAKS_HISTORY))
+                missing = [slot for slot, _ in external.incomplete_slots(records)]
+                self.assertEqual("secrets-history" in missing, status == "not_run")
+
+    def test_e7_the_tree_slot_reads_the_working_tree(self):
+        self.tool("gitleaks")
+        [record] = self.slot(self.records(), "secrets-tree")
+        self.assertEqual(record["command"], GITLEAKS_TREE)
+
+    def test_e9_options_that_make_a_finding_exit_non_zero(self):
+        self.tools("trufflehog", "checkov", "trivy", "npm")
+        lock = self.project / "package-lock.json"
+        lock.write_text("{}")
+        (self.project / "package.json").write_text('{"name": "x"}')
+        records = self.records(["iac"])
+        [tree] = [r for r in self.slot(records, "secrets-tree") if r["tool"] == "trufflehog"]
+        self.assertIn("--fail", tree["command"])
+        [trivy] = self.slot(records, "iac-misconfig")
+        self.assertEqual(trivy["command"][-3:], ["--exit-code", "1", "."])
+        for fail_on, level in ((None, None), ("medium", "moderate"), ("high", "high"),
+                               ("critical", "critical")):
+            with self.subTest(fail_on=fail_on):
+                [npm] = self.slot(self.records(fail_on=fail_on), "npm-audit:package-lock.json")
+                levels = [a for a in npm["command"] if a.startswith("--audit-level")]
+                self.assertEqual(levels, [f"--audit-level={level}"] if level else [])
+
+    def test_e13_each_skip_reason_is_a_not_run_record(self):
+        self.tools("npm", "yarn")
+        sub = self.project / "sub"
+        sub.mkdir()
+        (sub / "package-lock.json").write_text("{}")
+        [npm] = self.slot(self.records(), "npm-audit:sub/package-lock.json")
+        self.assertEqual((npm["status"], npm["reason"], npm["where"]),
+                         ("not_run", "no package.json beside it", "sub/package-lock.json"))
+        shutil.rmtree(sub)
+        real = self.tmp / "real.lock"
+        real.write_text("")
+        lock, package = self.project / "yarn.lock", self.project / "package.json"
+        for label, reason in (("link", "yarn.lock is a link or not a regular file"),
+                              ("no package.json", "no package.json beside yarn.lock"),
+                              ("not an object", "package.json is not a JSON object")):
+            with self.subTest(case=label):
+                for path in (lock, package):
+                    if path.is_symlink() or path.exists():
+                        path.unlink()
+                if label == "link":
+                    lock.symlink_to(real)
+                else:
+                    lock.write_text("")
+                if label == "not an object":
+                    package.write_text("[]")
+                records = self.records(["javascript"])
+                [yarn] = self.slot(records, "yarn-audit")
+                self.assertEqual((yarn["status"], yarn["reason"], yarn["where"]),
+                                 ("not_run", reason, "yarn.lock"))
+                self.assertIn("yarn-audit", [slot for slot, _ in external.incomplete_slots(records)])
+                summary = _run_audit_module().summarize(
+                    {"scans": {}, "external": external.external_section(records)})
+                self.assertIn(f"external yarn-audit: yarn not_run, {reason}", summary["not_run"])
+        for path in (lock, package):
+            if path.is_symlink() or path.exists():
+                path.unlink()
+        with self.subTest(case="a lockfile that cannot be copied"):
+            os.mkfifo(self.project / "package-lock.json")
+            package.write_text('{"name": "x"}')
+            [npm] = self.slot(self.records(), "npm-audit:package-lock.json")
+            self.assertEqual((npm["status"], npm["reason"]),
+                             ("not_run", "the lockfile could not be copied"))
+
+    def test_e15_three_slots_run_for_a_project_with_no_type(self):
+        self.assertEqual(scanners_types(self.project), [])
+        report = _run_audit_module().run_full_scan(str(self.project), "external")
+        slots = [r["slot"] for r in report["external"]["tools"]]
+        for slot in ("sast", "secrets-tree", "secrets-history"):
+            self.assertIn(slot, slots)
+
+    def test_e16_external_section_status(self):
+        def rec(slot, status):
+            return {"slot": slot, "status": status}
+        section = external.external_section
+        self.assertEqual(section([rec("a", "ran"), rec("b", "not_applicable")])["status"],
+                         "COMPLETE")
+        self.assertEqual(section([rec("a", "ran"), rec("b", "not_installed")])["status"],
+                         "PARTIAL")
+        self.assertEqual(section([rec("a", "not_installed"), rec("a", "ran")])["status"],
+                         "COMPLETE")
+        self.assertEqual(section([rec("a", "not_installed"), rec("b", "not_applicable")])["status"],
+                         "NOT_RUN")
+
+
+def scanners_types(project):
+    return sys.modules[NAME].detect_project_types(str(project))
+
+
+class TestRunAudit(ToolCase):
+    """TC-E1, TC-E3, TC-E8, TC-E10 to TC-E12, TC-E14, TC-E17 drive `run_audit.py`."""
+
+    def test_e1_every_tool_missing_is_not_run_and_exits_3(self):
+        # base-fail: the base prints no report for `external` and exits 0.
+        proc = self.cli("--scan-type", "external", "--output", "json")
+        report = json.loads(proc.stdout)
+        statuses = {r["status"] for r in report["external"]["tools"]}
+        self.assertLessEqual(statuses, {"not_installed", "not_applicable"}, report["external"])
+        self.assertIn("not_installed", statuses)
+        self.assertEqual(report["external"]["status"], "NOT_RUN")
+        self.assertEqual(report["scans"], {})
+        self.assertFalse(report["summary"]["scan_complete"])
+        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
+        self.assertEqual(proc.returncode, 3, proc.stderr)
+
+    def complete_python_project(self):
+        (self.project / "app.py").write_text("x = 1\n")
+        self.tools("semgrep", "gitleaks", "pip-audit")
+        self.tool("bandit", "exit 1")
+
+    def test_e3_a_tool_exit_fails_fail_on_and_is_listed_without_it(self):
+        self.complete_python_project()
+        proc = self.cli("--scan-type", "external", "--fail-on", "critical")
+        self.assertEqual(proc.returncode, 1, proc.stderr)
+        self.assertIn("[GATE] --fail-on critical:", proc.stderr)
+        self.assertIn("bandit exited 1 (python-sast)", proc.stderr)
+        proc, report = self.cli_json("--scan-type", "external")
+        self.assertEqual(proc.returncode, 0, proc.stderr)
+        self.assertEqual(report["summary"]["tool_exits"], ["bandit exited 1 (python-sast)"])
+        self.assertTrue(report["summary"]["scan_complete"], report["summary"]["not_run"])
+
+    def test_e8_stdout_holds_one_json_document(self):
+        self.tool("semgrep", "echo semgrep-stdout; exit 1")
+        self.tool("gitleaks", "echo gitleaks-stdout")
+        proc = self.cli("--scan-type", "external", "--output", "json", "--fail-on", "critical")
+        report = json.loads(proc.stdout)
+        self.assertEqual(report["scan_type"], "external")
+        self.assertNotIn("semgrep-stdout", proc.stdout)
+        self.assertIn("semgrep-stdout", proc.stderr)
+        self.assertNotIn("[GATE]", proc.stdout)
+        self.assertIn("[GATE]", proc.stderr)
+        self.assertEqual(proc.returncode, 1)
+
+    def test_e10_a_breach_and_a_part_not_run_exit_1(self):
+        # The breach: the SBOM scan's medium finding for a project with no SBOM.
+        proc, report = self.cli_json("--scan-type", "all", "--fail-on", "medium")
+        self.assertIn("medium", [f["severity"] for f in report["scans"]["sbom"]["findings"]])
+        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
+        self.assertIn("[GATE] --fail-on medium:", proc.stderr)
+        self.assertIn("[INCOMPLETE]", proc.stderr)
+        self.assertEqual(proc.returncode, 1)
+
+    def test_e11_deps_with_npm_missing_exits_3(self):
+        sub = self.project / "sub"
+        sub.mkdir()
+        (sub / "package-lock.json").write_text("{}")
+        (sub / "package.json").write_text('{"name": "x"}')
+        proc, report = self.cli_json("--scan-type", "deps")
+        self.assertEqual(report["summary"]["not_run"],
+                         ["dependencies: sub/package-lock.json: not audited, npm is not installed"])
+        self.assertIn("[INCOMPLETE]", proc.stderr)
+        self.assertEqual(proc.returncode, 3)
+
+    def test_e12_overall_status(self):
+        run_audit = _run_audit_module()
+        report = run_audit.run_full_scan(str(self.project), "external")
+        self.assertTrue(report["summary"]["overall_status"].startswith("[?] INCOMPLETE: "),
+                        report["summary"])
+        self.complete_python_project()
+        report = run_audit.run_full_scan(str(self.project), "external")
+        self.assertEqual(report["summary"]["overall_status"], "[?] REVIEW RECOMMENDED")
+
+    def test_e14_summary_prints_one_line_per_record(self):
+        self.tools("semgrep", "gitleaks")
+        _proc, report = self.cli_json("--scan-type", "external")
+        out = self.cli("--scan-type", "external").stdout
+        for record in report["external"]["tools"]:
+            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
+            with self.subTest(slot=record["slot"], tool=record["tool"]):
+                self.assertEqual(sum(1 for x in out.splitlines() if x.startswith(line)), 1, out)
+        for label in ("Critical", "High", "Medium", "Low", "Info"):
+            self.assertIn(f"\n  {label}: 0\n", out)
+
+    def test_e18_a_killed_tool_leaves_its_slot_not_run(self):
+        self.tool("semgrep", "kill -9 $$")
+        records = self.records()
+        [record] = self.slot(records, "sast")
+        self.assertEqual(record["status"], "killed")
+        self.assertLess(record["exit_code"], 0)
+        self.assertIn("sast", [slot for slot, _ in external.incomplete_slots(records)])
+
+    def test_e19_printable_escapes_control_format_and_separator_characters(self):
+        self.assertEqual(helpers.printable("a\x1bb\nc\u202ed\u2028e\u2029f\U000e0001g h"),
+                         "a\\x1bb\\x0ac\\u202ed\\u2028e\\u2029f\\U000e0001g h")
+
+    def test_e19_tree_text_is_escaped_in_printed_output(self):
+        sub = self.project / "a\x1b[31mb"
+        sub.mkdir()
+        (sub / "package-lock.json").write_text("{}")
+        (sub / "package.json").write_text('{"name": "x"}')
+        summary = self.cli("--scan-type", "deps")
+        for stream in (summary.stdout, summary.stderr):
+            self.assertNotIn("\x1b", stream)
+        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stderr)
+        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stdout)
+        proc, report = self.cli_json("--scan-type", "deps")
+        self.assertNotIn("\x1b", proc.stdout)
+        self.assertIn("dependencies: a\x1b[31mb/package-lock.json: not audited, npm is not installed",
+                      report["summary"]["not_run"])
+
+    def test_e17_the_summary_counts_every_finding_before_the_cut(self):
+        run_audit = _run_audit_module()
+        findings = [{"type": "t", "severity": "low"}] * 30 + [{"type": "t", "severity": "critical"}]
+        stub = {"tool": "stub", "findings": findings, "status": "[?]"}
+        with mock.patch.object(run_audit, "scan_secrets", return_value=stub):
+            report = run_audit.run_full_scan(str(self.project), "secrets")
+        self.assertEqual((report["summary"]["total_findings"], report["summary"]["critical"]),
+                         (31, 1))
+        self.assertEqual(len(report["scans"]["secrets"]["findings"]), 30)
+        self.assertEqual(run_audit.exit_code(report, "critical"), 1)
+
+
 if __name__ == "__main__":
     unittest.main()
diff --git a/tests/test_run_safety_rules.py b/tests/test_run_safety_rules.py
--- a/tests/test_run_safety_rules.py
+++ b/tests/test_run_safety_rules.py
@@ -10,7 +10,10 @@
 * `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
   no unverified control, tests are not the hunt (``TC-2``);
 * each place that routes an audit, as the whole paragraph, list item or table row that holds its
-  pointer, and `full-robust` §3's gate on `audit_status: PASS` and a scan that ran (``TC-3``).
+  pointer, and `full-robust` §3's gate on `audit_status: PASS` and a scan that ran (``TC-3``);
+* each place that turns the scanner's exit code and summary into `scan_status`, as a block of its
+  own: exit 3 or `summary.not_run` gives `NOT_RUN`, and `summary.tool_exits` gives at least
+  `findings` (``TC-3b``, TASK 118 R5.5).
 
 The pinned texts below are written as they stand in their files, wrapped; the tests compare them
 with whitespace collapsed. A change to a pinned rule changes this file in the same edit, where a
@@ -184,15 +187,16 @@
         passed".""",
     ),
     "System/Docs/SKILLS.md": (
-        """| **`security-audit`** | Vulnerability assessment v3.11 (two-layer model: deterministic
+        """| **`security-audit`** | Vulnerability assessment v3.12 (two-layer model: deterministic
         regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping
         table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance,
         auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity
         reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC
         (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool
-        integrations (incl. `snyk-agent-scan`), private disclosure of a dependency finding (§6.1),
-        an unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or
-        HIGH issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |""",
+        integrations (incl. `snyk-agent-scan`), a status for each external tool and exit 3 for a
+        scan part that did not run, private disclosure of a dependency finding (§6.1), an
+        unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH
+        issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |""",
     ),
     "System/Docs/WORKFLOWS.md": (
         """| **Security Audit** | Runs the security auditor agent. Remediation loop bounded at **max
@@ -200,6 +204,33 @@
         definition of "clean". A `scan_status: NOT_RUN` yields `INCOMPLETE`, or `FAIL` when the
         manual review found a CRITICAL or HIGH issue, never clean (`security-audit` §6.2). | `run
         security-audit` |""",
+    ),
+}
+
+#: TC-3b (TASK 118 R5.5): each router that reads the scanner states how its exit code and summary
+#: set `scan_status`, in a block outside the blocks of `POINTERS`.
+SCAN_STATUS_POINTERS = {
+    WRAPPER: (
+        """- **The scanner's exit code and summary set the floor of `scan_status`.** Exit 3, or a
+        `summary.not_run` list that is not empty, means a part of the scan did not run:
+        `scan_status: "NOT_RUN"`. A `summary.tool_exits` list that is not empty means an external
+        tool reported a finding or failed: `scan_status` is at least `"findings"`, and
+        `"NOT_RUN"` when the tool's output shows an error (`security-audit` §2). A run that prints
+        no report, such as exit 1 with a JSON `error` or exit 2, is `"NOT_RUN"`.""",
+    ),
+    "System/Agents/10_security_auditor.md": (
+        """- The scanner sets the floor of `scan_status`. Exit 3, or a `summary.not_run` list that
+        is not empty, gives `"NOT_RUN"`. A `summary.tool_exits` list that is not empty gives at
+        least `"findings"`, and `"NOT_RUN"` when the tool's output shows an error
+        (`security-audit` §2). A run that prints no report, such as exit 1 with a JSON `error` or
+        exit 2, gives `"NOT_RUN"`.""",
+    ),
+    ".agent/workflows/security-audit.md": (
+        """- **A partial scan is `NOT_RUN`.** Exit 3, or a `summary.not_run` list that is not
+        empty, records `scan_status: NOT_RUN (<the parts it names>)`. A `summary.tool_exits` list
+        that is not empty records at least `scan_status: findings`, and `scan_status: NOT_RUN`
+        when the tool's output shows an error (`security-audit` §2). A run that prints no report,
+        such as exit 1 with a JSON `error` or exit 2, records `scan_status: NOT_RUN`.""",
     ),
 }
 
@@ -291,6 +322,15 @@
                 with self.subTest(file=rel, block=block[:50]):
                     self.assertIn(block, blocks)
 
+    def test_each_router_maps_the_scanner_status(self):
+        """TC-3b (TASK 118 R5.5)."""
+        for rel, expected in SCAN_STATUS_POINTERS.items():
+            blocks = _blocks(_read(rel))
+            for block in expected:
+                block = _flat(block)
+                with self.subTest(file=rel, block=block[:50]):
+                    self.assertIn(block, blocks)
+
     def test_blocks_split_at_items_rows_and_blank_lines(self):
         text = "- one\n  two\n- three\n\npara\nline\n| a | b |\n| c | d |\n"
         self.assertEqual(_blocks(text), ["- one two", "- three", "para line", "| a | b |",
diff --git a/.agent/skills/security-audit/scripts/audit/init_next.py b/.agent/skills/security-audit/scripts/audit/init_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/init_next.py
+++ /dev/null
@@ -1,38 +0,0 @@
-"""Security Audit Scanner — modular static analysis engine.
-
-Single source of truth for package version. SKILL.md frontmatter and
-run_audit.py CLI header must match `__version__` on each release.
-"""
-
-__version__ = "3.12"
-
-from .config import SEVERITY_ORDER
-from .scanners import (
-    scan_dependencies,
-    scan_secrets,
-    scan_code_patterns,
-    scan_configuration,
-    scan_iac,
-    scan_mcp_agentic,
-    scan_sbom,
-)
-from .external import external_section, find_git_entry, incomplete_slots, run_external_tools
-from .helpers import detect_project_types, printable
-
-__all__ = [
-    "__version__",
-    "SEVERITY_ORDER",
-    "scan_dependencies",
-    "scan_secrets",
-    "scan_code_patterns",
-    "scan_configuration",
-    "scan_iac",
-    "scan_mcp_agentic",
-    "scan_sbom",
-    "run_external_tools",
-    "external_section",
-    "find_git_entry",
-    "incomplete_slots",
-    "printable",
-    "detect_project_types",
-]
diff --git a/.agent/skills/security-audit/scripts/audit/helpers_next.py b/.agent/skills/security-audit/scripts/audit/helpers_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/helpers_next.py
+++ /dev/null
@@ -1,180 +0,0 @@
-"""Utility functions for the security audit scanner."""
-
-import math
-import os
-import unicodedata
-import shutil
-import subprocess
-import sys
-import tempfile
-from contextlib import contextmanager
-from pathlib import Path
-from typing import Dict, Iterator, List, Optional
-
-from .config import (
-    MCP_CONFIG_FILENAMES,
-    SELF_DIR,
-    SEVERITY_ORDER,
-    SKIP_DIRS,
-    IAC_FILENAMES,
-)
-
-
-#: Seconds one external tool may run before its record says `timed_out` (TASK 118 R1.1).
-#: `run_tool` reads it at each call. External SAST tools like semgrep can exceed 120 s on a
-#: non-trivial repository; a shorter limit killed them mid-scan.
-TOOL_TIMEOUT = 600
-
-
-def run_tool(cmd: List[str], cwd: str, slot: str, where: str = ".") -> Dict:
-    """Run one external tool and return its tool record (TASK 118 R1.1).
-
-    The record's `status` is `ran` with the tool's `exit_code`, `not_installed` when the executable
-    is not found, or `timed_out` past `TOOL_TIMEOUT`. The tool's stdout goes to file descriptor 2,
-    beside its stderr, so the scanner's stdout holds its report alone (R1.9).
-    """
-    record = {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where,
-              "status": "ran", "exit_code": None, "reason": None}
-    cmd_str = " ".join(cmd)
-    print(f"[*] Running: {cmd_str}", file=sys.stderr)
-    sys.stderr.flush()
-    try:
-        result = subprocess.run(cmd, cwd=cwd, check=False, timeout=TOOL_TIMEOUT, stdout=2)
-    except FileNotFoundError:
-        print(f"[!] Tool not found: {cmd[0]}", file=sys.stderr)
-        record["status"] = "not_installed"
-        return record
-    except subprocess.TimeoutExpired:
-        print(f"[!] Timeout: {cmd_str} exceeded {TOOL_TIMEOUT}s limit", file=sys.stderr)
-        record["status"] = "timed_out"
-        return record
-    record["exit_code"] = result.returncode
-    if result.returncode < 0:
-        # A signal ended the process: the tool did not finish its scan (TASK 118 D13).
-        record["status"] = "killed"
-        print(f"[!] {cmd_str} was killed by signal {-result.returncode}", file=sys.stderr)
-    elif result.returncode != 0:
-        print(f"[!] {cmd_str} exited with code {result.returncode}", file=sys.stderr)
-    return record
-
-
-#: The Unicode categories `printable` escapes: control, format, line and paragraph separator.
-ESCAPED_CATEGORIES = ("Cc", "Cf", "Zl", "Zp")
-
-
-def printable(text) -> str:
-    """`text` with each control, format or separator character escaped (TASK 118 R1.10).
-
-    A path or a message from the scanned tree can hold a newline, an ANSI escape, a bidirectional
-    override or a line separator, and with it forge a line of the scanner's output. The categories
-    of `ESCAPED_CATEGORIES` become `\\xNN`, `\\uNNNN` or `\\UNNNNNNNN`.
-    """
-    out = []
-    for char in str(text):
-        if unicodedata.category(char) in ESCAPED_CATEGORIES:
-            code = ord(char)
-            if code <= 0xFF:
-                out.append(f"\\x{code:02x}")
-            elif code <= 0xFFFF:
-                out.append(f"\\u{code:04x}")
-            else:
-                out.append(f"\\U{code:08x}")
-        else:
-            out.append(char)
-    return "".join(out)
-
-
-def is_self_path(filepath: str) -> bool:
-    """Check if file is within the scanner's own directory (false positive prevention)."""
-    try:
-        return str(Path(filepath).resolve()).startswith(SELF_DIR)
-    except (OSError, ValueError):
-        return False
-
-
-def sort_findings_by_severity(findings: List[Dict]) -> List[Dict]:
-    """Sort findings by severity (critical first) to ensure important items are not truncated."""
-    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.get("severity", "low"), 99))
-
-
-def shannon_entropy(s: str) -> float:
-    """Calculate Shannon entropy of a string."""
-    if not s:
-        return 0.0
-    prob = [float(s.count(c)) / len(s) for c in set(s)]
-    return -sum(p * math.log2(p) for p in prob if p > 0)
-
-
-#: npm lockfiles in the order npm reads them: `npm-shrinkwrap.json` wins over `package-lock.json`.
-NPM_LOCKFILES = ("npm-shrinkwrap.json", "package-lock.json")
-
-
-def find_npm_lockfiles(root_dir: str) -> List[Path]:
-    """One npm lockfile per directory under `root_dir` (TASK 111 R5.1).
-
-    The audit of a lockfile below the root was missing: `npm audit` ran at the root only. Skips the
-    directories of `SKIP_DIRS`, `node_modules` among them, and follows no symbolic link, to a
-    directory or to a lockfile. A directory holding both lockfiles yields `npm-shrinkwrap.json`.
-    """
-    found = []
-    for root, dirs, files in os.walk(root_dir, followlinks=False):
-        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
-        for name in NPM_LOCKFILES:
-            path = Path(root) / name
-            if name in files and not path.is_symlink():
-                found.append(path)
-                break
-    return found
-
-
-class LockfileCopyError(Exception):
-    """The lockfile or its `package.json` could not be copied, such as a FIFO (TASK 118 D16)."""
-
-
-@contextmanager
-def npm_audit_dir(lockfile: Path) -> Iterator[Optional[Path]]:
-    """A temporary directory holding copies of `lockfile` and its `package.json` (TASK 111 R5.2).
-
-    npm reads `.npmrc` from the directory it runs in, and an audited subdirectory may be vendored
-    code: its `.npmrc` could redirect the registry or the cache. A copy leaves it behind; the
-    operator's own npm configuration still applies. Yields `None` when no regular `package.json`
-    stands beside the lockfile (R5.6): npm would then audit an ancestor's project instead. Raises
-    `LockfileCopyError` when a copy raises `OSError`; `shutil` refuses a FIFO before it opens one.
-    """
-    package = lockfile.parent / "package.json"
-    if not package.is_file() or package.is_symlink():
-        yield None
-        return
-    with tempfile.TemporaryDirectory(prefix="npm-audit-") as tmp:
-        try:
-            shutil.copyfile(lockfile, Path(tmp) / lockfile.name)
-            shutil.copyfile(package, Path(tmp) / "package.json")
-        except OSError as exc:
-            raise LockfileCopyError(str(exc)) from exc
-        yield Path(tmp)
-
-
-def detect_project_types(root_dir: str) -> List[str]:
-    """Detect project types based on file extensions and config files."""
-    types = set()
-    for root, dirs, files in os.walk(root_dir, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-        if any(f.endswith(".sol") for f in files):
-            types.add("solidity")
-        if any(f.endswith(".py") for f in files):
-            types.add("python")
-        if any(f.endswith(".js") or f.endswith(".ts") for f in files):
-            types.add("javascript")
-        if any(f.endswith(".rs") for f in files) or "Cargo.toml" in files:
-            types.add("rust")
-        if any(f.endswith(".go") for f in files) or "go.mod" in files:
-            types.add("go")
-        if any(f in IAC_FILENAMES for f in files) or any(f.endswith(".tf") for f in files):
-            types.add("iac")
-        if any(f in MCP_CONFIG_FILENAMES for f in files):
-            types.add("mcp")
-    # .vscode is in SKIP_DIRS (pruned above) but is the canonical mcp.json home —
-    # probe the project root explicitly so detection still triggers.
-    if (Path(root_dir) / ".vscode" / "mcp.json").exists():
-        types.add("mcp")
-    return list(types)
diff --git a/.agent/skills/security-audit/scripts/audit/scanners_next.py b/.agent/skills/security-audit/scripts/audit/scanners_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/scanners_next.py
+++ /dev/null
@@ -1,664 +0,0 @@
-"""Core scanning functions for the security audit scanner."""
-
-import json
-import os
-import re
-import subprocess
-import sys
-from pathlib import Path
-from typing import Any, Dict
-
-from . import config as _config
-from .config import (
-    CODE_EXTENSIONS,
-    CONFIG_EXTENSIONS,
-    IAC_EXTENSIONS,
-    IAC_FILENAMES,
-    MCP_CONFIG_FILENAMES,
-    MCP_SCAN_PRUNE,
-    SEVERITY_ORDER,
-    SKIP_DIRS,
-)
-from .helpers import (
-    LockfileCopyError,
-    find_npm_lockfiles,
-    is_self_path,
-    npm_audit_dir,
-    printable,
-    shannon_entropy,
-    sort_findings_by_severity,
-)
-from .patterns import (
-    CONFIG_PATTERNS,
-    DANGEROUS_PATTERNS,
-    IAC_PATTERNS,
-    MCP_AGENTIC_PATTERNS,
-    SECRET_PATTERNS,
-)
-
-
-#: Seconds one `npm audit` may run before its lockfile is reported as not audited (TASK 111 R5.2).
-NPM_AUDIT_TIMEOUT = 60
-
-#: npm's advisory severity → the scanner's severity (TASK 118 R3.1).
-NPM_SEVERITY = {"critical": "critical", "high": "high", "moderate": "medium", "low": "low",
-                "info": "info"}
-
-
-def _npm_audit(lockfile: Path, project_path: str):
-    """`(rel, findings, counts)` of `npm audit` for one lockfile (TASK 111 R5.2, R5.3, R5.6).
-
-    `--package-lock-only` reads the lockfile without `node_modules`, in a temporary copy of the
-    lockfile and its `package.json`. An audit that does not finish yields an `info` finding naming
-    the lockfile and the reason, never a silent pass; its `counts` is `None` (TASK 118 R3.3).
-    """
-    rel = os.path.relpath(lockfile, project_path).replace(os.sep, "/")
-    try:
-        with npm_audit_dir(lockfile) as workdir:
-            if workdir is None:
-                return rel, [_not_audited(rel, "no package.json beside it")], None
-            try:
-                result = subprocess.run(
-                    ["npm", "audit", "--json", "--package-lock-only"],
-                    cwd=workdir, capture_output=True, text=True, timeout=NPM_AUDIT_TIMEOUT,
-                )
-            except FileNotFoundError:
-                return rel, [_not_audited(rel, "npm is not installed")], None
-            except subprocess.TimeoutExpired:
-                return rel, [_not_audited(rel, f"npm audit ran past {NPM_AUDIT_TIMEOUT} s")], None
-    except LockfileCopyError:
-        return rel, [_not_audited(rel, "the lockfile could not be copied")], None
-    try:
-        audit_data = json.loads(result.stdout)
-    except json.JSONDecodeError:
-        return rel, [_not_audited(rel, "npm audit printed no JSON")], None
-    if not isinstance(audit_data, dict):
-        return rel, [_not_audited(rel, "npm audit printed no JSON object")], None
-    if "error" in audit_data:
-        error = audit_data["error"]
-        detail = (error.get("code") if isinstance(error, dict) else None) or audit_data.get("message")
-        reason = f"npm audit reported an error ({str(detail or 'no detail')[:120]})"
-        return rel, [_not_audited(rel, reason)], None
-    vulnerabilities = audit_data.get("vulnerabilities")
-    if vulnerabilities is not None and not isinstance(vulnerabilities, dict):
-        return rel, [_not_audited(rel, "npm audit printed no vulnerability map")], None
-    return rel, _npm_audit_findings(audit_data, rel), _npm_audit_counts(audit_data)
-
-
-def _not_audited(rel: str, reason: str) -> dict:
-    """The `info` finding of a lockfile that was not audited; `audited` marks it (TASK 118 R3.4)."""
-    return {
-        "type": "npm audit",
-        "severity": "info",
-        "cwe": "CWE-1104",
-        "message": f"{rel}: not audited, {reason}",
-        "audited": False,
-    }
-
-
-def _npm_audit_counts(audit_data: dict) -> dict:
-    """The counts of a finished `npm audit` per npm severity, and `unknown` (TASK 118 R3.2, R3.3).
-
-    An entry that is not a map, or holds no severity, counts as `low`, as before TASK 118; a
-    severity outside npm's five counts as `unknown`.
-    """
-    counts = dict.fromkeys((*NPM_SEVERITY, "unknown"), 0)
-    for vuln in (audit_data.get("vulnerabilities") or {}).values():
-        sev = str(vuln.get("severity") or "low").lower() if isinstance(vuln, dict) else "low"
-        counts[sev if sev in NPM_SEVERITY else "unknown"] += 1
-    return counts
-
-
-def _npm_audit_findings(audit_data: dict, rel: str) -> list:
-    """One finding per npm severity of a finished `npm audit`, at every severity (TASK 118 R3.1)."""
-    counts = _npm_audit_counts(audit_data)
-    findings = [{
-        "type": "npm audit",
-        "severity": NPM_SEVERITY[sev],
-        "cwe": "CWE-1104",
-        "message": f"{rel}: {count} {sev} vulnerabilities in dependencies",
-    } for sev, count in counts.items() if sev in NPM_SEVERITY and count]
-    if counts["unknown"]:
-        findings.append({
-            "type": "npm audit",
-            "severity": "low",
-            "cwe": "CWE-1104",
-            "message": f"{rel}: {counts['unknown']} vulnerabilities of unknown severity",
-        })
-    return findings
-
-
-def scan_dependencies(project_path: str) -> Dict[str, Any]:
-    """Validate supply chain security (OWASP A03:2025 Software Supply Chain Failures, CWE-1104)."""
-    results = {"tool": "dependency_scanner", "findings": [], "status": "[OK] Secure",
-               "npm_audit_counts": {}}
-
-    # Ecosystem -> (type markers, accepted lock files).
-    # `requirements.txt` lists deps but does NOT pin a full transitive graph
-    # with hashes, so it is NOT counted as a lock file by default. Exception:
-    # pip-compile output with `--hash=sha256:` lines IS effectively a lock.
-    ecosystems = {
-        "javascript": {
-            "markers": ["package.json"],
-            "locks": ["package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml"],
-        },
-        "python": {
-            "markers": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
-            "locks": ["Pipfile.lock", "poetry.lock", "uv.lock", "pdm.lock"],
-        },
-        "rust": {
-            "markers": ["Cargo.toml"],
-            "locks": ["Cargo.lock"],
-        },
-        "go": {
-            "markers": ["go.mod"],
-            "locks": ["go.sum"],
-        },
-    }
-
-    def _python_has_hash_pinned_requirements(base: Path) -> bool:
-        """pip-compile output: requirements.txt with `--hash=sha256:` is a de-facto lock."""
-        req = base / "requirements.txt"
-        if not req.exists():
-            return False
-        try:
-            with open(req, 'r', encoding='utf-8', errors='ignore') as f:
-                # Stop scanning after 1MB; hash lines appear early in real pip-compile output.
-                sample = f.read(1024 * 1024)
-            return '--hash=sha256:' in sample
-        except OSError:
-            return False
-
-    for eco, spec in ecosystems.items():
-        base = Path(project_path)
-        is_type = any((base / m).exists() for m in spec["markers"])
-        if not is_type:
-            continue
-        has_lock = any((base / f).exists() for f in spec["locks"])
-        if not has_lock and eco == "python" and _python_has_hash_pinned_requirements(base):
-            has_lock = True  # pip-compile hash-pinned requirements.txt counts as lock
-        if not has_lock:
-            results["findings"].append({
-                "type": "Missing Lock File",
-                "severity": "high",
-                "cwe": "CWE-1104",
-                "message": f"{eco}: No lock file found (expected one of: {', '.join(spec['locks'])}). Supply chain integrity at risk."
-            })
-
-    # npm audit, once per lockfile directory (TASK 111 R5). The audit used to run at the root only,
-    # and a failed run produced no finding, so an offline scan read as a clean one.
-    not_audited = 0
-    for lockfile in find_npm_lockfiles(project_path):
-        rel, found, counts = _npm_audit(lockfile, project_path)
-        not_audited += sum(1 for f in found if f.get("audited") is False)
-        results["findings"].extend(found)
-        if counts is not None:
-            results["npm_audit_counts"][rel] = counts
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    # The first match sets the status (TASK 118 R3.5): a critical or high finding outranks an
-    # unaudited lockfile (TASK 111 R5.7), which outranks a finding below high.
-    max_sev = min((SEVERITY_ORDER.get(f.get("severity", "low"), 99) for f in results["findings"]),
-                  default=99)
-    if max_sev == 0:
-        results["status"] = "[!!] Critical vulnerabilities"
-    elif max_sev == 1:
-        results["status"] = "[!] HIGH: Dependency issues"
-    elif not_audited:
-        results["status"] = f"[?] Not audited: {not_audited} npm lockfile(s)"
-    elif any(f.get("severity") in ("medium", "low") for f in results["findings"]):
-        results["status"] = "[?] Dependency issues below high"
-
-    return results
-
-
-def scan_secrets(project_path: str) -> Dict[str, Any]:
-    """Validate no hardcoded secrets (OWASP A04:2025 Cryptographic Failures, CWE-798)."""
-    results = {
-        "tool": "secret_scanner",
-        "findings": [],
-        "status": "[OK] No secrets detected",
-        "scanned_files": 0,
-        "skipped_files": 0,
-        "by_severity": {"critical": 0, "high": 0}
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CODE_EXTENSIONS and ext not in CONFIG_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
-                    content = f.read()
-                    # ReDoS guard: filter out pathologically long lines before regex.
-                    # All SECRET_PATTERNS are line-local (no multi-line matches in the
-                    # current pattern set, including BEGIN...KEY which is one-line marker).
-                    all_lines = content.splitlines()
-                    safe_lines = [
-                        ln for ln in all_lines
-                        if len(ln) <= _config.MAX_LINE_LENGTH
-                    ]
-                    safe_content = "\n".join(safe_lines)
-                    # Count only genuinely over-long lines. (A prior `count("\n") + 1`
-                    # over-counted by 1 on newline-terminated files — splitlines() yields
-                    # no trailing empty element — emitting a phantom "skipped 1 line" WARN.)
-                    skipped_lines = len(all_lines) - len(safe_lines)
-                    if skipped_lines > 0:
-                        print(f"[WARN] {printable(filepath)}: skipped {skipped_lines} line(s) > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                    for pattern, secret_type, severity, cwe in SECRET_PATTERNS:
-                        matches = re.findall(pattern, safe_content, re.IGNORECASE)
-                        if matches:
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "type": secret_type,
-                                "severity": severity,
-                                "cwe": cwe,
-                                "count": len(matches)
-                            })
-                            if severity in results["by_severity"]:
-                                results["by_severity"][severity] += len(matches)
-
-                    # High-entropy string detection for suspicious variable names
-                    entropy_pattern = r'(?:secret|private[_-]?key|auth[_-]?token|api[_-]?key|password|credential)\s*[=:]\s*["\']([^"\']{16,})["\']'
-                    for match in re.finditer(entropy_pattern, safe_content, re.IGNORECASE):
-                        value = match.group(1)
-                        entropy = shannon_entropy(value)
-                        if entropy > 4.5:
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "type": "High-Entropy Secret",
-                                "severity": "high",
-                                "cwe": "CWE-798",
-                                "count": 1,
-                                "entropy": round(entropy, 2)
-                            })
-                            results["by_severity"]["high"] += 1
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    if results["by_severity"]["critical"] > 0:
-        results["status"] = "[!!] CRITICAL: Secrets exposed!"
-    elif results["by_severity"]["high"] > 0:
-        results["status"] = "[!] HIGH: Secrets found"
-
-    return results
-
-
-def scan_code_patterns(project_path: str) -> Dict[str, Any]:
-    """Validate dangerous code patterns (OWASP A05:2025 Injection, CWE-79/89/78)."""
-    results = {
-        "tool": "pattern_scanner",
-        "findings": [],
-        "status": "[OK] No dangerous patterns",
-        "scanned_files": 0,
-        "skipped_files": 0
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CODE_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped {printable(filepath)}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
-                    lines = f.readlines()
-                    for line_num, line in enumerate(lines, 1):
-                        # ReDoS guard: skip pathologically long lines (minified bundles, token blobs).
-                        if len(line) > _config.MAX_LINE_LENGTH:
-                            continue
-                        for pattern, name, severity, category, cwe in DANGEROUS_PATTERNS:
-                            if re.search(pattern, line, re.IGNORECASE):
-                                results["findings"].append({
-                                    "file": str(filepath.relative_to(project_path)),
-                                    "line": line_num,
-                                    "pattern": name,
-                                    "severity": severity,
-                                    "category": category,
-                                    "cwe": cwe,
-                                    "snippet": line.strip()[:100]
-                                })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if critical > 0:
-        results["status"] = f"[!!] CRITICAL: {critical} dangerous patterns"
-    elif high > 0:
-        results["status"] = f"[!] HIGH: {high} dangerous patterns"
-    elif results["findings"]:
-        results["status"] = "[?] Patterns found"
-
-    return results
-
-
-def scan_configuration(project_path: str) -> Dict[str, Any]:
-    """Validate security configuration (OWASP A02:2025 Security Misconfiguration, CWE-16)."""
-    results = {"tool": "config_scanner", "findings": [], "status": "[OK] Config secure", "skipped_files": 0}
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            ext = Path(file).suffix.lower()
-            if ext not in CONFIG_EXTENSIONS:
-                continue
-
-            filepath = Path(root) / file
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
-                    content = f.read()
-                    for pattern, issue, severity, cwe in CONFIG_PATTERNS:
-                        if re.search(pattern, content, re.IGNORECASE):
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "issue": issue,
-                                "severity": severity,
-                                "cwe": cwe,
-                            })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    if any(f["severity"] == "critical" for f in results["findings"]):
-        results["status"] = "[!!] CRITICAL: Config issues"
-    elif any(f["severity"] == "high" for f in results["findings"]):
-        results["status"] = "[!] HIGH: Config issues"
-
-    return results
-
-
-def scan_iac(project_path: str) -> Dict[str, Any]:
-    """Validate Infrastructure as Code security (Docker, K8s, Terraform)."""
-    results = {
-        "tool": "iac_scanner",
-        "findings": [],
-        "status": "[OK] IaC secure",
-        "scanned_files": 0,
-        "skipped_files": 0,
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-
-        for file in files:
-            filepath = Path(root) / file
-            ext = Path(file).suffix.lower()
-            is_iac_file = (ext in IAC_EXTENSIONS) or (file in IAC_FILENAMES) or file.startswith("Dockerfile")
-
-            if not is_iac_file:
-                continue
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
-                    content = f.read()
-
-                    # ReDoS guard: IaC patterns may span lines (re.MULTILINE). Instead of
-                    # filtering lines (breaks multi-line patterns), skip the entire file
-                    # if any line is pathologically long. Legit YAML/Dockerfile/Terraform
-                    # never has >4k-char lines; only minified blobs do.
-                    if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
-                        results["skipped_files"] += 1
-                        print(f"[WARN] Skipped IaC {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                        continue
-
-                    # Heuristic: for generic YAML/JSON files, only apply patterns
-                    # matching the detected IaC type (prevents false positives on docs)
-                    is_docker = file.startswith("Dockerfile") or file == "Containerfile"
-                    is_k8s = re.search(r'apiVersion\s*:', content) is not None
-                    is_terraform = ext in {'.tf', '.tfvars'}
-                    is_cloudformation = re.search(r'AWSTemplateFormatVersion|Resources\s*:', content) is not None
-                    is_compose = file in {'docker-compose.yml', 'docker-compose.yaml'}
-
-                    for pattern, name, severity, category, cwe in IAC_PATTERNS:
-                        # Skip category-specific patterns for non-matching file types
-                        if category == "Docker" and not (is_docker or is_compose):
-                            continue
-                        if category == "Kubernetes" and not is_k8s:
-                            continue
-                        if category == "Terraform" and not is_terraform:
-                            continue
-                        if category == "CloudFormation" and not is_cloudformation:
-                            continue
-
-                        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
-                            line_num = content[:match.start()].count('\n') + 1
-                            results["findings"].append({
-                                "file": str(filepath.relative_to(project_path)),
-                                "line": line_num,
-                                "pattern": name,
-                                "severity": severity,
-                                "category": category,
-                                "cwe": cwe,
-                            })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if critical > 0:
-        results["status"] = f"[!!] CRITICAL: {critical} IaC issues"
-    elif high > 0:
-        results["status"] = f"[!] HIGH: {high} IaC issues"
-    elif results["findings"]:
-        results["status"] = "[?] IaC patterns found"
-
-    return results
-
-
-def scan_sbom(project_path: str) -> Dict[str, Any]:
-    """Check for SBOM presence recursively via os.walk with early SKIP_DIRS prune.
-
-    Uses os.walk (not Path.rglob) because rglob traverses SKIP_DIRS first and only
-    filters after yielding — on a monorepo with node_modules, that is O(millions).
-    os.walk with `dirs[:] = ...` pruning skips those subtrees entirely.
-    """
-    results = {
-        "tool": "sbom_scanner",
-        "findings": [],
-        "status": "[OK] SBOM check passed",
-    }
-
-    # Compiled fnmatch-style checks; case-insensitive so "SBOM.json" is caught.
-    sbom_patterns_re = [
-        re.compile(r'.*sbom.*', re.IGNORECASE),
-        re.compile(r'^bom\.(?:json|xml)$', re.IGNORECASE),
-        re.compile(r'.*\.spdx.*', re.IGNORECASE),
-        re.compile(r'.*\.cdx\..*', re.IGNORECASE),
-        re.compile(r'^cyclonedx-bom\..*$', re.IGNORECASE),
-    ]
-
-    sbom_files = []
-    for current_dir, dirs, files in os.walk(project_path, followlinks=False):
-        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
-        for f in files:
-            if any(rx.match(f) for rx in sbom_patterns_re):
-                sbom_files.append(Path(current_dir) / f)
-
-    if not sbom_files:
-        results["findings"].append({
-            "type": "Missing SBOM",
-            "severity": "medium",
-            "cwe": "CWE-1104",
-            "message": "No SBOM (Software Bill of Materials) found. Required by EU CRA & EO 14028. "
-                       "Generate with: npx @cyclonedx/cdxgen -o sbom.json (or syft . -o cyclonedx-json > sbom.json)"
-        })
-        results["status"] = "[?] SBOM missing"
-    else:
-        results["status"] = f"[OK] SBOM found: {', '.join(f.name for f in sbom_files[:3])}"
-
-    return results
-
-
-def scan_mcp_agentic(project_path: str) -> Dict[str, Any]:
-    """Scan MCP/agentic surfaces (OWASP ASI Top 10 2026, NSA MCP CSI).
-
-    Targets: well-known MCP config artifacts (MCP_CONFIG_FILENAMES) with full
-    pattern set + provenance finding; other config files (auto-approve keys,
-    bypass flags, unpinned runners); code files (tool-description poisoning
-    heuristics). Walks with MCP_SCAN_PRUNE (descends into .vscode, unlike
-    other scanners). Markdown is deliberately NOT scanned — semantic prose
-    poisoning is the LLM-review class (see references/checklists/
-    mcp_agentic_security.md "Scanner floor").
-    """
-    results = {
-        "tool": "mcp_agentic_scanner",
-        "findings": [],
-        "status": "[OK] No MCP/agentic risks detected",
-        "scanned_files": 0,
-        "skipped_files": 0,
-    }
-
-    for root, dirs, files in os.walk(project_path, followlinks=False):
-        # Custom prune: unlike other scanners, descend into .vscode (canonical
-        # home of mcp.json / chat.tools.autoApprove). Filename-targeted, so cheap.
-        dirs[:] = [d for d in dirs if d not in MCP_SCAN_PRUNE]
-
-        for file in files:
-            filepath = Path(root) / file
-            ext = Path(file).suffix.lower()
-            is_mcp_config = file in MCP_CONFIG_FILENAMES
-
-            if is_mcp_config:
-                applicable = MCP_AGENTIC_PATTERNS
-            elif ext in CONFIG_EXTENSIONS:
-                applicable = [p for p in MCP_AGENTIC_PATTERNS if p[5] == "any-config"]
-            elif ext in CODE_EXTENSIONS:
-                applicable = [p for p in MCP_AGENTIC_PATTERNS if p[5] == "code"]
-            else:
-                continue  # .md and everything else: LLM-review class, not regex floor
-
-            if is_self_path(str(filepath)):
-                continue
-
-            try:
-                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
-                    results["skipped_files"] += 1
-                    continue
-            except OSError:
-                continue
-
-            results["scanned_files"] += 1
-
-            try:
-                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
-                    content = f.read()
-
-                rel = str(filepath.relative_to(project_path))
-
-                if is_mcp_config:
-                    results["findings"].append({
-                        "file": rel,
-                        "type": "MCP Config Present",
-                        "severity": "low",
-                        "category": "Agentic Supply Chain (ASI04)",
-                        "cwe": "CWE-829",
-                        "message": "MCP config detected — verify provenance, version pinning, and "
-                                   "registry trust of each server (see checklists/mcp_agentic_security.md).",
-                    })
-
-                # ReDoS guard: whole-file matching uses newline-crossing character
-                # classes, so (IaC-style) skip the entire file on pathological lines.
-                if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
-                    results["skipped_files"] += 1
-                    print(f"[WARN] Skipped MCP scan of {printable(filepath)}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
-                    continue
-
-                lines = content.splitlines()
-                for pattern, name, severity, category, cwe, _scope in applicable:
-                    for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
-                        line_num = content[:match.start()].count('\n') + 1
-                        snippet = lines[line_num - 1].strip()[:100] if line_num <= len(lines) else ""
-                        results["findings"].append({
-                            "file": rel,
-                            "line": line_num,
-                            "pattern": name,
-                            "severity": severity,
-                            "category": category,
-                            "cwe": cwe,
-                            "snippet": snippet,
-                        })
-            except Exception as e:
-                results["skipped_files"] += 1
-                print(f"[WARN] Skipped {printable(filepath)}: {e}", file=sys.stderr)
-
-    results["findings"] = sort_findings_by_severity(results["findings"])
-
-    high = sum(1 for f in results["findings"] if f["severity"] == "high")
-    if high > 0:
-        results["status"] = f"[!] HIGH: {high} MCP/agentic risks"
-    elif results["findings"]:
-        results["status"] = "[?] MCP/agentic surface present (review)"
-
-    return results
diff --git a/.agent/skills/security-audit/scripts/audit/external_next.py b/.agent/skills/security-audit/scripts/audit/external_next.py
deleted file mode 100644
--- a/.agent/skills/security-audit/scripts/audit/external_next.py
+++ /dev/null
@@ -1,259 +0,0 @@
-"""External security tool integration."""
-
-import json
-import os
-import stat
-from pathlib import Path
-from typing import List, Optional
-import sys
-
-from .helpers import LockfileCopyError, find_npm_lockfiles, npm_audit_dir, printable, run_tool
-
-
-#: The `package.json` fields the yarn copy keeps (TASK 112 R5.1). `packageManager` and
-#: `devEngines.packageManager` are left out: a corepack `yarn` shim fetches the version they name.
-YARN_KEPT_FIELDS = ("name", "version", "private", "workspaces", "resolutions", "dependencies",
-                    "devDependencies", "optionalDependencies", "peerDependencies")
-
-
-def _keep_dependency_fields(package: Path) -> bool:
-    """Rewrite the copied `package.json` with `YARN_KEPT_FIELDS` only; False when no JSON object."""
-    try:
-        data = json.loads(package.read_text(encoding="utf-8"))
-    except (OSError, UnicodeDecodeError, ValueError):
-        return False
-    if not isinstance(data, dict):
-        return False
-    kept = {key: data[key] for key in YARN_KEPT_FIELDS if key in data}
-    package.write_text(json.dumps(kept), encoding="utf-8")
-    return True
-
-
-#: `--fail-on` → the `npm audit --audit-level` that makes npm exit non-zero at that threshold
-#: (TASK 118 R2.10).
-NPM_AUDIT_LEVEL = {"critical": "critical", "high": "high", "medium": "moderate"}
-
-#: The working-tree secret scan: `--no-git` reads the files, the uncommitted ones included
-#: (TASK 118 R4.1).
-GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
-#: The history secret scan: git mode reads the committed history (TASK 118 R4.2).
-GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
-
-
-def _bare_repository(directory: str) -> Optional[str]:
-    """`"bare"` for a regular `HEAD` and the directories `objects` and `refs`; `"bare-link"` when
-    the three exist and one is a link (TASK 118 R4.2); `None` otherwise."""
-    try:
-        modes = [os.lstat(os.path.join(directory, name)).st_mode
-                 for name in ("HEAD", "objects", "refs")]
-    except OSError:
-        return None
-    if any(stat.S_ISLNK(mode) for mode in modes):
-        return "bare-link"
-    head, objects, refs = modes
-    if stat.S_ISREG(head) and stat.S_ISDIR(objects) and stat.S_ISDIR(refs):
-        return "bare"
-    return None
-
-
-def find_git_entry(root: str, stop: Optional[str] = None) -> Optional[str]:
-    """The kind of the first repository at or above `root` (TASK 118 R4.2).
-
-    The walk starts at the real path of `root`, as git does, and checks each parent up to the
-    filesystem root, or up to `stop` included. At each directory it reads `.git` with `os.lstat`,
-    so a link is reported as `"link"` and never followed, and then checks whether the directory is
-    itself a bare repository. Returns `"dir"`, `"file"`, `"link"`, `"other"`, `"unreadable"`,
-    `"bare"`, `"bare-link"`, or `None` when nothing matches on the path.
-    """
-    current = os.path.realpath(root)
-    last = os.path.realpath(stop) if stop is not None else None
-    while True:
-        try:
-            mode = os.lstat(os.path.join(current, ".git")).st_mode
-        except (FileNotFoundError, NotADirectoryError):
-            bare = _bare_repository(current)
-            if bare:
-                return bare
-        except OSError:
-            return "unreadable"
-        else:
-            if stat.S_ISLNK(mode):
-                return "link"
-            if stat.S_ISDIR(mode):
-                return "dir"
-            if stat.S_ISREG(mode):
-                return "file"
-            return "other"
-        parent = os.path.dirname(current)
-        if current == last or parent == current:
-            return None
-        current = parent
-
-
-def incomplete_slots(records: List[dict]) -> List[tuple]:
-    """`(slot, last record)` of each slot with no `ran` and no `not_applicable` record (TASK 118 §3).
-
-    A slot is selected when it holds a record, so a slot with no record is never listed. Slots are
-    listed in the order of their first record.
-    """
-    slots = {}
-    for record in records:
-        slots.setdefault(record["slot"], []).append(record)
-    return [(slot, held[-1]) for slot, held in slots.items()
-            if not any(r["status"] in ("ran", "not_applicable") for r in held)]
-
-
-def external_section(records: List[dict]) -> dict:
-    """The external section of the report: its status and its records (TASK 118 R1.7).
-
-    The first match sets `status`: `NOT_RUN` when no record ran, `COMPLETE` when every selected
-    slot has a `ran` or a `not_applicable` record, `PARTIAL` otherwise.
-    """
-    if not any(r["status"] == "ran" for r in records):
-        status = "NOT_RUN"
-    elif incomplete_slots(records):
-        status = "PARTIAL"
-    else:
-        status = "COMPLETE"
-    return {"status": status, "tools": records}
-
-
-def _declined(slot: str, cmd: List[str], where: str, status: str, reason: str) -> dict:
-    """The record of a tool the scanner did not start (`not_run` or `not_applicable`)."""
-    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": status,
-            "exit_code": None, "reason": reason}
-
-
-def run_external_tools(project_path: str, types: List[str], fail_on=None) -> List[dict]:
-    """Run the external tools and return one tool record per tool (TASK 118 R1).
-
-    The slots `sast`, `secrets-tree` and `secrets-history` run for every project, also one with no
-    detected type; the others run for the project types that select them. A fallback starts only
-    when the first tool of its slot is `not_installed` or `timed_out`. A missing tool is non-fatal:
-    its record says so, and `run_audit.py` reports the slot as a part not run.
-    """
-    print(f"\n{'='*60}", file=sys.stderr)
-    print(f"External Tools Scan: {', '.join(types)}", file=sys.stderr)
-    print(f"{'='*60}", file=sys.stderr)
-
-    cwd = project_path
-    records = []
-
-    def run(slot, cmd, where=".", workdir=None):
-        record = run_tool(cmd, workdir or cwd, slot, where)
-        records.append(record)
-        return record
-
-    def run_with_fallback(slot, first, fallback):
-        if run(slot, first)["status"] in ("not_installed", "timed_out"):
-            run(slot, fallback)
-
-    # --- Cross-cutting scanners (run for any project, also with no detected type) ---
-
-    # semgrep — de-facto SAST standard (2024+); auto-config picks rules by language.
-    run("sast", ["semgrep", "--config", "auto", "--error", "--quiet", "--timeout", "60", "."])
-
-    # Secret scanners — stronger than regex-only. The working tree first, then the history.
-    # trufflehog exits 0 on a finding unless `--fail` is given (R2.10).
-    run_with_fallback("secrets-tree", GITLEAKS_TREE,
-                      ["trufflehog", "filesystem", "--no-update", "--fail", "."])
-    # The history slot has no fallback: `trufflehog git` ran the scanned repository's
-    # `core.fsmonitor` command (CVE-2025-41390), so only gitleaks reads the history (R4.3).
-    entry = find_git_entry(cwd)
-    if entry in ("dir", "file", "bare"):
-        run("secrets-history", GITLEAKS_HISTORY)
-    elif entry == "unreadable":
-        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
-                                 ".git could not be read"))
-    elif entry == "bare-link":
-        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
-                                 "the bare repository holds a symbolic link"))
-    elif entry == "link":
-        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
-                                 ".git is a symbolic link"))
-    elif entry == "other":
-        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_run",
-                                 ".git is not a directory or a regular file"))
-    else:
-        records.append(_declined("secrets-history", GITLEAKS_HISTORY, ".", "not_applicable",
-                                 "no .git at or above the scanned root"))
-
-    # --- Language/stack-specific scanners ---
-
-    if "solidity" in types:
-        run("solidity", ["slither", "."])
-
-    if "python" in types:
-        run("python-sast", ["bandit", "-r", ".", "-q"])
-        # pip-audit replaces safety (Safety DB went commercial in 2024)
-        run("python-deps", ["pip-audit"])
-
-    # npm audit in each lockfile directory, whatever the detected types (TASK 111 R5.4); a project
-    # without an npm lockfile runs none, since npm stops with ENOLOCK there (R5.5). Under
-    # `--fail-on`, `--audit-level` makes npm exit non-zero at that threshold only (TASK 118 R2.10).
-    npm = ["npm", "audit", "--package-lock-only"]
-    if fail_on in NPM_AUDIT_LEVEL:
-        npm.append(f"--audit-level={NPM_AUDIT_LEVEL[fail_on]}")
-    for lockfile in find_npm_lockfiles(cwd):
-        label = os.path.relpath(lockfile, cwd).replace(os.sep, "/")
-        slot = f"npm-audit:{label}"
-        try:
-            with npm_audit_dir(lockfile) as workdir:
-                if workdir is None:
-                    reason = "no package.json beside it"
-                else:
-                    reason = None
-                    print(f"[*] npm audit for {printable(label)}", file=sys.stderr)
-                    run(slot, npm, where=label, workdir=str(workdir))
-        except LockfileCopyError:
-            reason = "the lockfile could not be copied"
-        if reason:
-            print(f"[!] npm audit skipped for {printable(label)}: {reason}", file=sys.stderr)
-            records.append(_declined(slot, npm, label, "not_run", reason))
-    # yarn reads `.yarnrc` and `.yarnrc.yml` where it runs, and `yarnPath` there names a script it
-    # executes. It runs in a copy of the lockfile and its `package.json`, as npm does, and the copy
-    # keeps the dependency fields only: a corepack `yarn` shim would fetch and run the version that
-    # `packageManager` or `devEngines` names (TASK 112 R5.1).
-    yarn_lock = Path(cwd) / "yarn.lock"
-    if "javascript" in types and (yarn_lock.exists() or yarn_lock.is_symlink()):
-        yarn = ["yarn", "audit"]
-        if yarn_lock.is_symlink() or not yarn_lock.is_file():
-            reason = "yarn.lock is a link or not a regular file"
-        else:
-            reason = None
-            try:
-                with npm_audit_dir(yarn_lock) as workdir:
-                    if workdir is None:
-                        reason = "no package.json beside yarn.lock"
-                    elif not _keep_dependency_fields(workdir / "package.json"):
-                        reason = "package.json is not a JSON object"
-                    else:
-                        run("yarn-audit", yarn, where="yarn.lock", workdir=str(workdir))
-            except LockfileCopyError:
-                reason = "the lockfile could not be copied"
-        if reason:
-            print(f"[!] yarn audit skipped: {reason}", file=sys.stderr)
-            records.append(_declined("yarn-audit", yarn, "yarn.lock", "not_run", reason))
-
-    if "rust" in types:
-        run("rust-deps", ["cargo", "audit"])
-        run("rust-lint", ["cargo", "clippy"])
-
-    if "go" in types:
-        run("go-deps", ["govulncheck", "./..."])
-        run("go-sast", ["gosec", "./..."])
-
-    if "iac" in types:
-        run("iac", ["checkov", "-d", "."])
-        # trivy exits 0 on a finding unless `--exit-code` is given (R2.10).
-        run("iac-misconfig", ["trivy", "fs", "--scanners", "misconfig", "--exit-code", "1", "."])
-
-    if "mcp" in types:
-        # snyk-agent-scan (formerly Invariant mcp-scan): tool poisoning, tool
-        # shadowing, toxic flows across MCP servers and agent skills.
-        # SAFETY: NEVER pass --dangerously-skip-permissions-style flags here
-        # (e.g. --dangerously-run-mcp-servers) — an audit must not auto-start
-        # untrusted MCP servers; starting them is the operator's consent-gated call.
-        run_with_fallback("mcp", ["snyk-agent-scan", "."], ["mcp-scan"])  # legacy Invariant CLI
-
-    return records
diff --git a/.agent/skills/security-audit/scripts/run_audit_next.py b/.agent/skills/security-audit/scripts/run_audit_next.py
deleted file mode 100755
--- a/.agent/skills/security-audit/scripts/run_audit_next.py
+++ /dev/null
@@ -1,266 +0,0 @@
-#!/usr/bin/env python3
-"""
-Skill: security-audit
-Script: run_audit.py v3.12
-Purpose: CLI entry point for security audit scanner.
-Usage: python run_audit.py [project_path] [--scan-type all|deps|secrets|patterns|config|iac|mcp|external|sbom]
-       [--fail-on critical|high|medium] [--output json|summary] [--no-limit]
-Exit: 0 every requested part ran and no gate cause; 1 a `--fail-on` cause (a finding at the
-      threshold or above, or an external tool's non-zero exit), or a JSON `error` for a missing
-      directory or a non-positive `--max-size`; 2 a usage error (argparse); 3 a requested part did
-      not run.
-"""
-import argparse
-import json
-import os
-import sys
-from datetime import datetime
-from typing import Any, Dict, List
-
-# Fix Windows console encoding for Unicode output
-try:
-    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
-    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
-except AttributeError:
-    pass  # Python < 3.7
-
-from audit import (
-    SEVERITY_ORDER,
-    __version__ as AUDIT_VERSION,
-    detect_project_types,
-    external_section,
-    incomplete_slots,
-    printable,
-    run_external_tools,
-    scan_code_patterns,
-    scan_configuration,
-    scan_dependencies,
-    scan_iac,
-    scan_mcp_agentic,
-    scan_sbom,
-    scan_secrets,
-)
-from audit import config as _audit_config
-
-#: The severities the summary counts (TASK 118 R2.4).
-SUMMARY_SEVERITIES = ("critical", "high", "medium", "low", "info")
-#: Findings each section keeps unless `--no-limit` is given; the summary counts all of them.
-MAX_FINDINGS = 30
-
-
-def run_full_scan(project_path: str, scan_type: str = "all", no_limit: bool = False,
-                  fail_on=None) -> Dict[str, Any]:
-    """Execute the requested scans and produce a unified report.
-
-    The in-process scans of `scan_type` run first, then the external layer for `all` and
-    `external`, also for a project with no detected type (TASK 118 R1.4). The summary counts every
-    finding before each section is cut to `MAX_FINDINGS` (R2.5). `fail_on` sets npm's
-    `--audit-level` (R2.10).
-    """
-    report = {
-        "project": project_path,
-        "timestamp": datetime.now().isoformat(),
-        "scan_type": scan_type,
-        "scans": {},
-    }
-
-    scanners = {
-        "deps": ("dependencies", scan_dependencies),
-        "secrets": ("secrets", scan_secrets),
-        "patterns": ("code_patterns", scan_code_patterns),
-        "config": ("configuration", scan_configuration),
-        "iac": ("iac", scan_iac),
-        "mcp": ("mcp_agentic", scan_mcp_agentic),
-        "sbom": ("sbom", scan_sbom),
-    }
-
-    for key, (name, scanner) in scanners.items():
-        if scan_type == "all" or scan_type == key:
-            print(f"[*] Running {name} scan...", file=sys.stderr)
-            report["scans"][name] = scanner(project_path)
-
-    if scan_type in ("all", "external"):
-        types = detect_project_types(project_path)
-        report["external"] = external_section(run_external_tools(project_path, types, fail_on))
-
-    report["summary"] = summarize(report)
-
-    # Truncate findings (already sorted by severity), after the summary counted them all.
-    if not no_limit:
-        for result in report["scans"].values():
-            if len(result.get("findings", [])) > MAX_FINDINGS:
-                result["truncated"] = len(result["findings"]) - MAX_FINDINGS
-                result["findings"] = result["findings"][:MAX_FINDINGS]
-
-    return report
-
-
-def summarize(report: Dict[str, Any]) -> Dict[str, Any]:
-    """The summary of a report (TASK 118 R2.1 to R2.4, R2.9)."""
-    summary = {"total_findings": 0, **dict.fromkeys(SUMMARY_SEVERITIES, 0)}
-    not_run: List[str] = []
-    for name, result in report["scans"].items():
-        for finding in result.get("findings", []):
-            summary["total_findings"] += 1
-            sev = finding.get("severity", "low")
-            if sev in summary:
-                summary[sev] += 1
-            if finding.get("audited") is False:
-                not_run.append(f"{name}: {finding.get('message')}")
-
-    records = report.get("external", {}).get("tools", [])
-    for slot, last in incomplete_slots(records):
-        entry = f"external {slot}: {last['tool']} {last['status']}"
-        if last["status"] == "not_run":
-            entry += f", {last['reason']}"
-        not_run.append(entry)
-    tool_exits = [f"{r['tool']} exited {r['exit_code']} ({r['slot']})"
-                  for r in records if r["status"] == "ran" and r["exit_code"] != 0]
-
-    summary["not_run"] = not_run
-    summary["scan_complete"] = not not_run
-    summary["tool_exits"] = tool_exits
-
-    if summary["critical"] > 0:
-        summary["overall_status"] = "[!!] CRITICAL ISSUES FOUND"
-    elif summary["high"] > 0:
-        summary["overall_status"] = "[!] HIGH RISK ISSUES"
-    elif not_run:
-        summary["overall_status"] = f"[?] INCOMPLETE: {len(not_run)} part(s) did not run"
-    elif summary["total_findings"] > 0 or tool_exits:
-        summary["overall_status"] = "[?] REVIEW RECOMMENDED"
-    else:
-        summary["overall_status"] = "[OK] SECURE"
-    return summary
-
-
-def gate_causes(report: Dict[str, Any], fail_on) -> List[str]:
-    """Each cause of exit 1 under `--fail-on` (TASK 118 R2.6, R2.8); empty without `fail_on`."""
-    if not fail_on:
-        return []
-    summary = report["summary"]
-    threshold = SEVERITY_ORDER[fail_on]
-    causes = [f"{summary[sev]} {sev} finding(s)" for sev, order in SEVERITY_ORDER.items()
-              if order <= threshold and summary.get(sev, 0) > 0]
-    return causes + list(summary["tool_exits"])
-
-
-def exit_code(report: Dict[str, Any], fail_on) -> int:
-    """1 on a `--fail-on` cause, else 3 when a requested part did not run, else 0 (R2.6, R2.7)."""
-    if gate_causes(report, fail_on):
-        return 1
-    return 0 if report["summary"]["scan_complete"] else 3
-
-
-def print_summary(report: Dict[str, Any]):
-    """Print human-readable summary to stdout; text from the scanned tree is escaped (R1.10)."""
-    summary = report["summary"]
-    print(f"\n{'='*60}")
-    print(f"Security Scan v{AUDIT_VERSION}: {printable(report['project'])}")
-    print(f"Timestamp: {report['timestamp']}")
-    print(f"{'='*60}")
-    print(f"Status: {summary['overall_status']}")
-    print(f"Total Findings: {summary['total_findings']}")
-    for sev in SUMMARY_SEVERITIES:
-        print(f"  {sev.capitalize()}: {summary[sev]}")
-
-    total_skipped = sum(s.get('skipped_files', 0) for s in report['scans'].values())
-    if total_skipped > 0:
-        print(f"  Skipped Files: {total_skipped} (see stderr)")
-
-    total_truncated = sum(s.get('truncated', 0) for s in report['scans'].values())
-    if total_truncated > 0:
-        print(f"  Truncated: {total_truncated} findings hidden (use --no-limit)")
-
-    if summary["not_run"]:
-        print("Not run:")
-        for entry in summary["not_run"]:
-            print(f"  - {printable(entry)}")
-    if summary["tool_exits"]:
-        print("Tool exits:")
-        for entry in summary["tool_exits"]:
-            print(f"  - {printable(entry)}")
-
-    print(f"{'='*60}\n")
-
-    for scan_name, scan_result in report['scans'].items():
-        print(f"\n{scan_name.upper()}: {printable(scan_result['status'])}")
-        for finding in scan_result.get('findings', [])[:10]:
-            sev = finding.get('severity', 'INFO').upper()
-            desc = finding.get('type') or finding.get('pattern') or finding.get('issue')
-            cwe = finding.get('cwe', '')
-            f_str = f"  - [{sev}] {desc}"
-            if cwe:
-                f_str += f" ({cwe})"
-            if 'file' in finding:
-                f_str += f" in {finding['file']}"
-            if 'line' in finding:
-                f_str += f":{finding['line']}"
-            if 'message' in finding:
-                f_str += f" - {finding['message']}"
-            print(printable(f_str))
-
-    if "external" in report:
-        print(f"\nEXTERNAL: {report['external']['status']}")
-        for record in report["external"]["tools"]:
-            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
-            if record["status"] in ("ran", "killed"):
-                line += f" (exit {record['exit_code']})"
-            elif record["reason"]:
-                line += f" ({record['reason']})"
-            print(printable(line))
-
-
-def main(argv=None):
-    parser = argparse.ArgumentParser(description=f"Security Audit Tool v{AUDIT_VERSION}")
-    parser.add_argument("project_path", nargs="?", default=".", help="Project directory")
-    parser.add_argument("--scan-type",
-                        choices=["all", "deps", "secrets", "patterns", "config", "iac", "mcp", "sbom", "external"],
-                        default="all", help="Type of scan")
-    parser.add_argument("--output", choices=["json", "summary"], default="summary",
-                        help="Output format")
-    parser.add_argument("--fail-on", choices=["critical", "high", "medium"],
-                        default=None, help="Exit with code 1 if findings >= this severity, or an "
-                                           "external tool exits non-zero (for CI/CD)")
-    parser.add_argument("--no-limit", action="store_true",
-                        help="Do not truncate findings list")
-    parser.add_argument("--max-size", type=int, default=None, metavar="MB",
-                        help=f"Max file size to scan in MB (default: {_audit_config.MAX_FILE_SIZE // (1024*1024)}). "
-                             "Increase for large minified bundles.")
-
-    args = parser.parse_args(argv)
-
-    if args.max_size is not None:
-        if args.max_size <= 0:
-            print(json.dumps({"error": "--max-size must be positive"}))
-            sys.exit(1)
-        _audit_config.MAX_FILE_SIZE = args.max_size * 1024 * 1024
-
-    if not os.path.isdir(args.project_path):
-        print(json.dumps({"error": f"Directory not found: {args.project_path}"}))
-        sys.exit(1)
-
-    report = run_full_scan(args.project_path, args.scan_type, args.no_limit, args.fail_on)
-
-    if args.output == "summary":
-        print_summary(report)
-    else:
-        print(json.dumps(report, indent=2))
-    sys.stdout.flush()
-
-    code = exit_code(report, args.fail_on)
-    causes = gate_causes(report, args.fail_on)
-    if causes:
-        print(f"\n[GATE] --fail-on {args.fail_on}:", file=sys.stderr)
-        for cause in causes:
-            print(f"  - {printable(cause)}", file=sys.stderr)
-    if not report["summary"]["scan_complete"]:
-        print("\n[INCOMPLETE]", file=sys.stderr)
-        for entry in report["summary"]["not_run"]:
-            print(f"  - {printable(entry)}", file=sys.stderr)
-
-    sys.exit(code)
-
-
-if __name__ == "__main__":
-    main()
diff --git a/tests/staged_lockfile_audit.py b/tests/staged_lockfile_audit.py
deleted file mode 100644
--- a/tests/staged_lockfile_audit.py
+++ /dev/null
@@ -1,934 +0,0 @@
-"""The dependency audit covers every npm lockfile (TASK 111 R5).
-
-Before TASK 111 the `security-audit` scanner ran `npm audit` at the project root only, and a failed
-run produced no finding. This repository holds three npm lockfiles under
-`.agent/skills/mermaid-authoring-guidelines/assets/renderers/` and none at the root. A fake `npm` on
-`PATH` records the directory it runs in, that directory's entries and its arguments, and prints a
-set reply. This file pins:
-
-* a lockfile below the root is audited, in a temporary copy of it and its `package.json`, so a
-  `.npmrc` beside the lockfile takes no part (``TC-L1``, ``TC-L13``);
-* each finding names its lockfile (``TC-L2``, ``TC-L12``);
-* `node_modules/` and symbolic links are skipped (``TC-L3``, ``TC-L11``), and a project without a
-  lockfile runs no audit (``TC-L4``);
-* an audit that does not finish yields an `info` finding and the section says so (``TC-L5``,
-  ``TC-L14``, ``TC-L15``);
-* one directory is audited once (``TC-L6``);
-* `run_external_tools` audits each lockfile, and only those (``TC-L7`` to ``TC-L9c``); it runs
-  `yarn audit` in a copy of `yarn.lock` and `package.json`, never through a link, and for a
-  javascript project only (``TC-Y1`` to ``TC-Y3``, TASK 112 R5.1);
-* a root `package.json` without a lockfile is reported, not audited (``TC-L10``);
-* the copy holds the original `package.json`, never a linked one (``TC-L16``, ``TC-L17``);
-* a finding outranks an unaudited lockfile in the status; an unexpected vulnerability field and a
-  timeout yield a named `info` finding (``TC-L18`` to ``TC-L20``).
-
-TASK 118 (WI-42) adds the status of each external tool and the findings of every npm severity. Its
-fake tools are `/bin/sh` scripts in a `bin` directory that is the whole `PATH`, so a tool installed
-on the runner does not start. This file pins:
-
-* `run_audit.py` reports each external tool and exits 3 when a part did not run (``TC-E1``,
-  ``TC-E11``, ``TC-E13``, ``TC-E15``); a tool's record says `ran`, `not_installed` or `timed_out`
-  (``TC-E2``, ``TC-E4``), and a fallback fills its slot (``TC-E5``);
-* a tool's non-zero exit fails `--fail-on` (``TC-E3``, ``TC-E10``), and the options that make a
-  finding exit non-zero are passed (``TC-E9``);
-* the secret scan reads the working tree with `--no-git`, and the history slot follows the `.git`
-  at or above the scanned root, never through a link (``TC-E6``, ``TC-E7``);
-* stdout holds one JSON document (``TC-E8``); the summary output lists each tool (``TC-E14``); the
-  external status and the overall status (``TC-E12``, ``TC-E16``); the summary counts every
-  finding before the cut (``TC-E17``);
-* npm advisories of every severity are findings, with a count map per lockfile, and an unaudited
-  lockfile carries `audited: false` (``TC-D1`` to ``TC-D7``; ``TC-D1`` replaces ``TC-L23``); a
-  lockfile that cannot be copied is not audited, and the scanner still prints its report
-  (``TC-D8``);
-* a tool killed by a signal leaves its slot a part not run (``TC-E18``), and text from the scanned
-  tree reaches printed output with its control characters escaped (``TC-E19``).
-
-`RUN_AUDIT_PATH` and `RUN_AUDIT_CMD` name the `run_audit.py` that the tests load and start; a test
-reads them at call time. The in-process cases stop the `.git` walk at their temporary directory;
-the subprocess cases cannot. TC-E1 accepts either status of the history slot, and TC-E3 assumes
-no `.git` link or special file above the system temporary directory.
-"""
-import importlib
-import importlib.util
-import json
-import os
-import shutil
-import subprocess
-import sys
-import tempfile
-import unittest
-from pathlib import Path
-from unittest import mock
-
-PROJECT_ROOT = Path(__file__).resolve().parent.parent
-PACKAGE = PROJECT_ROOT / ".agent" / "skills" / "security-audit" / "scripts" / "audit"
-NAME = "security_audit_scanner_under_test"
-RUN_AUDIT_PATH = PACKAGE.parent / "run_audit.py"
-RUN_AUDIT_CMD = (sys.executable, str(RUN_AUDIT_PATH))
-
-
-def _load():
-    """The scanner package under a name no other test module uses."""
-    if NAME not in sys.modules:
-        spec = importlib.util.spec_from_file_location(
-            NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
-        module = importlib.util.module_from_spec(spec)
-        sys.modules[NAME] = module
-        spec.loader.exec_module(module)
-    return (importlib.import_module(f"{NAME}.scanners"),
-            importlib.import_module(f"{NAME}.external"),
-            importlib.import_module(f"{NAME}.helpers"))
-
-
-scanners, external, helpers = _load()
-
-
-def _run_audit_module():
-    """`RUN_AUDIT_PATH`, loaded while `audit` names the package under test."""
-    saved = sys.modules.get("audit")
-    sys.modules["audit"] = sys.modules[NAME]
-    try:
-        spec = importlib.util.spec_from_file_location("security_audit_run_audit_under_test",
-                                                      RUN_AUDIT_PATH)
-        module = importlib.util.module_from_spec(spec)
-        spec.loader.exec_module(module)
-    finally:
-        if saved is None:
-            del sys.modules["audit"]
-        else:
-            sys.modules["audit"] = saved
-    return module
-
-FAKE_NPM = """#!/bin/sh
-printf '%s\\t%s\\t%s\\t%s\\n' "$PWD" "$(ls -A | tr '\\n' ' ')" "$*" "$(cat package.json)" >> "$FAKE_NPM_LOG"
-if grep -q broken package.json; then echo "not json"; else cat "$FAKE_NPM_REPLY"; fi
-"""
-HIGH = {"vulnerabilities": {"x": {"severity": "high"}}}
-COPY = "package-lock.json package.json"
-GITLEAKS_TREE = ["gitleaks", "detect", "--no-banner", "--redact", "--no-git", "-s", "."]
-GITLEAKS_HISTORY = ["gitleaks", "detect", "--no-banner", "--redact", "-s", "."]
-ZERO_COUNTS = dict.fromkeys(("critical", "high", "moderate", "low", "info", "unknown"), 0)
-
-
-def _ran(cmd, slot, where="."):
-    """The tool record of a tool that ran and exited 0."""
-    return {"slot": slot, "tool": cmd[0], "command": list(cmd), "where": where, "status": "ran",
-            "exit_code": 0, "reason": None}
-
-
-class AuditTestCase(unittest.TestCase):
-
-    def setUp(self):
-        self.tmp = Path(tempfile.mkdtemp())
-        self.addCleanup(shutil.rmtree, self.tmp)
-        self.project = self.tmp / "project"
-        self.project.mkdir()
-        self.bin = self.tmp / "bin"
-        self.bin.mkdir()
-        npm = self.bin / "npm"
-        npm.write_text(FAKE_NPM)
-        npm.chmod(0o755)
-        self.log = self.tmp / "npm.log"
-        self.reply = self.tmp / "reply.json"
-        self.set_reply({"vulnerabilities": {}})
-        env = {"PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
-               "FAKE_NPM_LOG": str(self.log), "FAKE_NPM_REPLY": str(self.reply)}
-        patcher = mock.patch.dict(os.environ, env)
-        patcher.start()
-        self.addCleanup(patcher.stop)
-
-    def set_reply(self, reply):
-        self.reply.write_text(reply if isinstance(reply, str) else json.dumps(reply))
-
-    def lockfile(self, rel, name="package-lock.json", package=True, content='{"name": "x"}'):
-        d = self.project / rel
-        d.mkdir(parents=True, exist_ok=True)
-        (d / name).write_text("{}")
-        if package:
-            (d / "package.json").write_text(content)
-        return d
-
-    def calls(self):
-        """`(directory, entries, arguments)` of each fake `npm` run."""
-        return [call[:3] for call in self.full_calls()]
-
-    def full_calls(self):
-        """`(directory, entries, arguments, package.json)` of each fake `npm` run."""
-        if not self.log.exists():
-            return []
-        return [tuple(part.strip() for part in line.split("\t"))
-                for line in self.log.read_text().splitlines()]
-
-    def scan(self):
-        return scanners.scan_dependencies(str(self.project))
-
-    def infos(self, findings):
-        return [f for f in findings if f.get("severity") == "info"]
-
-
-class TestScanDependencies(AuditTestCase):
-    """TC-L1 to TC-L6 and TC-L10 to TC-L15 drive `scan_dependencies`."""
-
-    def test_l1_lockfile_below_the_root_is_audited_in_a_copy(self):
-        # base-fail: the base runs npm audit only at a root package.json.
-        self.lockfile("sub")
-        self.scan()
-        [(where, entries, args)] = self.calls()
-        self.assertEqual(args, "audit --json --package-lock-only")
-        self.assertEqual(entries, COPY)
-        self.assertFalse(Path(where).resolve().is_relative_to(self.project.resolve()))
-
-    def test_l2_finding_names_its_lockfile(self):
-        self.lockfile("sub")
-        self.set_reply(HIGH)
-        findings = self.scan()["findings"]
-        high = [f for f in findings if f.get("severity") == "high" and f.get("type") == "npm audit"]
-        self.assertEqual(len(high), 1, findings)
-        self.assertTrue(high[0]["message"].startswith("sub/package-lock.json: 1 high"), high[0])
-
-    def test_l3_node_modules_is_skipped(self):
-        self.lockfile("node_modules/dep")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l4_no_lockfile_runs_no_audit(self):
-        (self.project / "package.json").write_text("{}")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l5_unfinished_audit_yields_an_info_finding(self):
-        self.lockfile("sub")
-        for label, reply in (("not json", "not json"), ("not an object", []),
-                             ("error object", {"error": {"code": "ENOAUDIT"}}),
-                             ("error message", {"message": "ECONNREFUSED", "error": {}})):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                info = self.infos(self.scan()["findings"])
-                self.assertEqual(len(info), 1, info)
-                self.assertTrue(info[0]["message"].startswith("sub/package-lock.json: not audited"))
-        with self.subTest(case="timeout"), mock.patch.object(
-                scanners.subprocess, "run",
-                side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
-            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)
-        with self.subTest(case="npm absent"), \
-                mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(len(self.infos(self.scan()["findings"])), 1)
-
-    def test_l5_error_message_reaches_the_reason(self):
-        self.lockfile("sub")
-        self.set_reply({"message": "request to registry failed, ECONNREFUSED", "error": {}})
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("ECONNREFUSED", info["message"])
-
-    def test_l6_one_directory_is_audited_once(self):
-        self.lockfile("sub")
-        (self.project / "sub" / "npm-shrinkwrap.json").write_text("{}")
-        self.set_reply(HIGH)
-        findings = self.scan()["findings"]
-        [(_where, entries, _args)] = self.calls()
-        self.assertEqual(entries, "npm-shrinkwrap.json package.json")
-        self.assertTrue(any(f.get("message", "").startswith("sub/npm-shrinkwrap.json:")
-                            for f in findings))
-
-    def test_l10_root_package_json_without_lockfile_is_reported_not_audited(self):
-        (self.project / "package.json").write_text("{}")
-        findings = self.scan()["findings"]
-        self.assertTrue(any(f.get("type") == "Missing Lock File" and "javascript" in f["message"]
-                            for f in findings), findings)
-        self.assertEqual(self.calls(), [])
-
-    def test_l11_symbolic_links_are_not_followed(self):
-        real = self.lockfile("../outside")
-        (self.project / "linked").symlink_to(real, target_is_directory=True)
-        d = self.project / "plain"
-        d.mkdir()
-        (d / "package.json").write_text("{}")
-        (d / "package-lock.json").symlink_to(real / "package-lock.json")
-        self.scan()
-        self.assertEqual(self.calls(), [])
-
-    def test_l12_critical_finding_names_its_lockfile(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "critical"}, "b": {"severity": "high"}}})
-        result = self.scan()
-        messages = sorted(f["message"] for f in result["findings"] if f.get("type") == "npm audit")
-        self.assertEqual(messages, ["sub/package-lock.json: 1 critical vulnerabilities in dependencies",
-                                    "sub/package-lock.json: 1 high vulnerabilities in dependencies"])
-        self.assertIn("Critical", result["status"])
-
-    def test_l13_npmrc_beside_the_lockfile_is_not_copied(self):
-        d = self.lockfile("sub")
-        (d / ".npmrc").write_text("registry=http://attacker.invalid/\n")
-        self.scan()
-        [(_where, entries, _args)] = self.calls()
-        self.assertEqual(entries, COPY)
-
-    def test_l14_lockfile_without_package_json_is_not_audited(self):
-        self.lockfile("sub", package=False)
-        [info] = self.infos(self.scan()["findings"])
-        self.assertEqual(info["message"], "sub/package-lock.json: not audited, no package.json beside it")
-        self.assertEqual(self.calls(), [])
-
-    def test_l15_section_status_names_unaudited_lockfiles(self):
-        self.lockfile("sub")
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")
-
-    def test_l16_copy_holds_the_original_package_json(self):
-        self.lockfile("sub", content='{"name": "pinned-content"}')
-        self.scan()
-        [call] = self.full_calls()
-        self.assertEqual(call[3], '{"name": "pinned-content"}')
-
-    def test_l17_linked_package_json_is_not_used(self):
-        d = self.lockfile("sub", package=False)
-        real = self.tmp / "elsewhere.json"
-        real.write_text("{}")
-        (d / "package.json").symlink_to(real)
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("no package.json beside it", info["message"])
-        self.assertEqual(self.calls(), [])
-
-    def test_l18_a_finding_outranks_an_unaudited_lockfile_in_the_status(self):
-        self.lockfile("a")
-        self.lockfile("b", content='{"name": "broken"}')
-        self.set_reply({"vulnerabilities": {"x": {"severity": "critical"}}})
-        result = self.scan()
-        self.assertEqual(len(self.infos(result["findings"])), 1)
-        self.assertIn("Critical", result["status"])
-
-    def test_l19_vulnerability_field_shapes(self):
-        self.lockfile("sub")
-        for label, reply, infos in (("null", {"vulnerabilities": None}, 0),
-                                    ("list", {"vulnerabilities": []}, 1),
-                                    ("entry not a map", {"vulnerabilities": {"x": "high"}}, 0)):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                findings = self.scan()["findings"]
-                self.assertEqual(len(self.infos(findings)), infos, findings)
-                self.assertFalse([f for f in findings if f.get("severity") in ("high", "critical")])
-
-    def test_l20_timeout_reason_names_the_limit(self):
-        self.lockfile("sub")
-        with mock.patch.object(scanners.subprocess, "run",
-                               side_effect=subprocess.TimeoutExpired(["npm", "audit"], 60)):
-            [info] = self.infos(self.scan()["findings"])
-        self.assertEqual(info["message"], "sub/package-lock.json: not audited, npm audit ran past 60 s")
-
-    def test_l21_error_code_reaches_the_reason(self):
-        self.lockfile("sub")
-        self.set_reply({"error": {"code": "ENOAUDIT"}})
-        [info] = self.infos(self.scan()["findings"])
-        self.assertIn("ENOAUDIT", info["message"])
-
-    def test_l22_status_counts_every_unaudited_lockfile(self):
-        self.lockfile("a")
-        self.lockfile("b")
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 2 npm lockfile(s)")
-
-    def test_d1_every_npm_severity_is_a_finding(self):
-        """TC-D1 (TASK 118 R3.1), in place of TC-L23: the base kept critical and high only."""
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "moderate"}, "b": {"severity": "low"},
-                                            "c": {"severity": "info"}}})
-        findings = [f for f in self.scan()["findings"] if f.get("type") == "npm audit"]
-        self.assertEqual([(f["severity"], f["message"]) for f in findings], [
-            ("medium", "sub/package-lock.json: 1 moderate vulnerabilities in dependencies"),
-            ("low", "sub/package-lock.json: 1 low vulnerabilities in dependencies"),
-            ("info", "sub/package-lock.json: 1 info vulnerabilities in dependencies")])
-
-    def test_l15_each_audit_has_a_60_second_timeout(self):
-        self.lockfile("sub")
-        with mock.patch.object(scanners.subprocess, "run", wraps=subprocess.run) as run:
-            self.scan()
-        self.assertEqual(run.call_args.kwargs.get("timeout"), 60)
-
-
-class TestExternalTools(AuditTestCase):
-    """TC-L7 to TC-L9c and TC-Y1 to TC-Y3 drive `run_external_tools` (R5.4, R5.5; TASK 112 R5.1)."""
-
-    def external(self, types):
-        recorded = []
-
-        def record(cmd, cwd=None, slot=None, where=".", **_kw):
-            entries = " ".join(sorted(os.listdir(cwd))) if cwd else ""
-            recorded.append((list(cmd), Path(cwd).resolve() if cwd else None, entries))
-            return _ran(cmd, slot, where)
-
-        with mock.patch.object(external, "run_tool", side_effect=record):
-            external.run_external_tools(str(self.project), types)
-        return recorded
-
-    def test_l7_external_tools_audit_each_lockfile_in_a_copy(self):
-        # base-fail: the base runs npm audit at the root, and only for a javascript project.
-        self.lockfile("sub")
-        npm = [r for r in self.external([]) if r[0][:1] == ["npm"]]
-        self.assertEqual(len(npm), 1, npm)
-        cmd, where, entries = npm[0]
-        self.assertEqual(cmd, ["npm", "audit", "--package-lock-only"])
-        self.assertEqual(entries, COPY)
-        self.assertFalse(where.is_relative_to(self.project.resolve()))
-
-    def test_l8_no_lockfile_runs_no_npm_audit(self):
-        npm = [r for r in self.external(["javascript"]) if r[0][:1] == ["npm"]]
-        self.assertEqual(npm, [])
-
-    def test_y3_yarn_audit_needs_a_javascript_project(self):
-        """TC-Y3 (TASK 112 R5.1), formerly TC-L9b."""
-        (self.project / "yarn.lock").write_text("")
-        (self.project / "package.json").write_text('{"name": "x"}')
-        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["yarn"]], [])
-
-    def test_l9c_lockfile_without_package_json_is_skipped(self):
-        self.lockfile("sub", package=False)
-        self.assertEqual([r for r in self.external([]) if r[0][:1] == ["npm"]], [])
-
-    def test_y1_yarn_audit_runs_in_a_copy(self):
-        """TC-Y1 (TASK 112 R5.1): yarn reads `.yarnrc.yml` where it runs; `yarnPath` there names a
-        script yarn executes. Base-fail: the base runs `yarn audit` in the scanned root."""
-        (self.project / "yarn.lock").write_text("")
-        (self.project / "package.json").write_text(json.dumps({
-            "name": "x", "packageManager": "yarn@4.0.0", "dependencies": {"a": "1"},
-            "devEngines": {"packageManager": {"name": "yarn", "version": "4.0.0"}},
-            "scripts": {"preinstall": "evil"}, "resolutions": {"b": "2"}}))
-        (self.project / ".yarnrc.yml").write_text("yarnPath: evil.js\n")
-        copies = []
-
-        def record(cmd, cwd=None, slot=None, where=".", **_kw):
-            if cmd[:1] == ["yarn"]:
-                copies.append((list(cmd), Path(cwd).resolve(), " ".join(sorted(os.listdir(cwd))),
-                               json.loads((Path(cwd) / "package.json").read_text())))
-            return _ran(cmd, slot, where)
-
-        with mock.patch.object(external, "run_tool", side_effect=record):
-            external.run_external_tools(str(self.project), ["javascript"])
-        self.assertEqual(len(copies), 1, copies)
-        cmd, where, entries, package = copies[0]
-        self.assertEqual(cmd, ["yarn", "audit"])
-        self.assertEqual(entries, "package.json yarn.lock")
-        self.assertFalse(where.is_relative_to(self.project.resolve()))
-        # A corepack `yarn` shim would fetch the version `packageManager` or `devEngines` names;
-        # the copy keeps the dependency fields only (TASK 112 R5.1).
-        self.assertEqual(package, {"name": "x", "dependencies": {"a": "1"}, "resolutions": {"b": "2"}})
-
-    def test_y2_no_regular_package_json_or_a_linked_lockfile_runs_no_yarn(self):
-        """TC-Y2 (TASK 112 R5.1)."""
-        real = self.tmp / "real.lock"
-        real.write_text("")
-        for case in ("no package.json", "linked package.json", "linked yarn.lock"):
-            with self.subTest(case=case):
-                for name in ("yarn.lock", "package.json"):
-                    path = self.project / name
-                    if path.is_symlink() or path.exists():
-                        path.unlink()
-                if case == "linked yarn.lock":
-                    (self.project / "yarn.lock").symlink_to(real)
-                    (self.project / "package.json").write_text('{"name": "x"}')
-                else:
-                    (self.project / "yarn.lock").write_text("")
-                    if case == "linked package.json":
-                        (self.project / "package.json").symlink_to(real)
-                yarn = [r for r in self.external(["javascript"]) if r[0][:1] == ["yarn"]]
-                self.assertEqual(yarn, [])
-
-
-class TestDependencySeverities(AuditTestCase):
-    """TC-D2 to TC-D7 (TASK 118 R3): npm advisories at every severity."""
-
-    def npm_findings(self, result):
-        return [f for f in result["findings"] if f.get("type") == "npm audit"]
-
-    def test_d2_a_moderate_advisory_fails_fail_on_medium_only(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
-        run_audit = _run_audit_module()
-        report = run_audit.run_full_scan(str(self.project), "deps", fail_on="medium")
-        self.assertEqual(run_audit.exit_code(report, "medium"), 1)
-        self.assertEqual(run_audit.exit_code(report, "high"), 0)
-
-    def test_d3_an_info_advisory_is_audited_and_a_missing_npm_is_not(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "info"}}})
-        result = self.scan()
-        self.assertFalse(result["status"].startswith("[?] Not audited"), result["status"])
-        self.assertEqual([f.get("audited", True) for f in self.npm_findings(result)], [True])
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            [finding] = self.npm_findings(self.scan())
-        self.assertEqual((finding["severity"], finding["audited"]), ("info", False))
-
-    def test_d4_an_unknown_severity_and_an_entry_that_is_not_a_map(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"x": {"severity": "weird"}}})
-        result = self.scan()
-        self.assertEqual(result["npm_audit_counts"]["sub/package-lock.json"]["unknown"], 1)
-        self.assertEqual([(f["severity"], f["message"]) for f in self.npm_findings(result)], [
-            ("low", "sub/package-lock.json: 1 vulnerabilities of unknown severity")])
-        self.set_reply({"vulnerabilities": {"x": "high"}})
-        counts = self.scan()["npm_audit_counts"]["sub/package-lock.json"]
-        self.assertEqual((counts["low"], counts["unknown"]), (1, 0))
-
-    def test_d5_each_finished_audit_has_all_six_counts(self):
-        self.lockfile("sub")
-        self.assertEqual(self.scan()["npm_audit_counts"], {"sub/package-lock.json": ZERO_COUNTS})
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "low"}}})
-        self.assertEqual(self.scan()["npm_audit_counts"]["sub/package-lock.json"],
-                         dict(ZERO_COUNTS, low=2))
-        with mock.patch.dict(os.environ, {"PATH": str(self.tmp / "empty")}):
-            self.assertEqual(self.scan()["npm_audit_counts"], {})
-
-    def test_d6_section_status_first_match_wins(self):
-        self.lockfile("sub")
-        for label, reply, status in (
-                ("critical", {"vulnerabilities": {"x": {"severity": "critical"}}},
-                 "[!!] Critical vulnerabilities"),
-                ("high", HIGH, "[!] HIGH: Dependency issues"),
-                ("moderate", {"vulnerabilities": {"x": {"severity": "moderate"}}},
-                 "[?] Dependency issues below high"),
-                ("low", {"vulnerabilities": {"x": {"severity": "low"}}},
-                 "[?] Dependency issues below high"),
-                ("info only", {"vulnerabilities": {"x": {"severity": "info"}}}, "[OK] Secure"),
-                ("none", {"vulnerabilities": {}}, "[OK] Secure")):
-            with self.subTest(case=label):
-                self.set_reply(reply)
-                self.assertEqual(self.scan()["status"], status)
-        with self.subTest(case="not audited outranks moderate"):
-            self.lockfile("other", content='{"name": "broken"}')
-            self.set_reply({"vulnerabilities": {"x": {"severity": "moderate"}}})
-            self.assertEqual(self.scan()["status"], "[?] Not audited: 1 npm lockfile(s)")
-
-    def test_d7_summary_counts_low_and_info_and_findings_are_sorted(self):
-        self.lockfile("sub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"}, "b": {"severity": "info"},
-                                            "c": {"severity": "critical"}}})
-        report = _run_audit_module().run_full_scan(str(self.project), "deps")
-        summary = report["summary"]
-        self.assertEqual((summary["critical"], summary["low"], summary["info"]), (1, 1, 1))
-        # Two lockfiles each yield a critical and a low finding: unsorted, a low one precedes the
-        # second critical one.
-        self.lockfile("tub")
-        self.set_reply({"vulnerabilities": {"a": {"severity": "low"},
-                                            "c": {"severity": "critical"}}})
-        severities = [f["severity"] for f in self.scan()["findings"]]
-        self.assertEqual(severities, ["critical", "critical", "low", "low"])
-
-    def test_d8_a_lockfile_that_cannot_be_copied_is_not_audited(self):
-        sub = self.project / "sub"
-        sub.mkdir()
-        os.mkfifo(sub / "package-lock.json")
-        (sub / "package.json").write_text('{"name": "x"}')
-        [info] = self.infos(self.scan()["findings"])
-        self.assertEqual((info["message"], info["audited"]),
-                         ("sub/package-lock.json: not audited, the lockfile could not be copied",
-                          False))
-        proc = subprocess.run([*RUN_AUDIT_CMD, str(self.project), "--scan-type", "deps",
-                               "--output", "json"], capture_output=True, text=True, timeout=120)
-        self.assertEqual(json.loads(proc.stdout)["summary"]["scan_complete"], False)
-        self.assertEqual(proc.returncode, 3, proc.stderr)
-
-
-class ToolCase(unittest.TestCase):
-    """A temporary project, and a `bin` directory of fake tools that is the whole `PATH`.
-
-    The `.git` walk of `run_external_tools` stops at the temporary directory, so a `.git` above it
-    takes no part.
-    """
-
-    def setUp(self):
-        self.tmp = Path(tempfile.mkdtemp()).resolve()
-        self.addCleanup(shutil.rmtree, self.tmp)
-        self.project = self.tmp / "project"
-        self.project.mkdir()
-        self.bin = self.tmp / "bin"
-        self.bin.mkdir()
-        patcher = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
-        patcher.start()
-        self.addCleanup(patcher.stop)
-        walk = external.find_git_entry
-        stopped = mock.patch.object(external, "find_git_entry",
-                                    side_effect=lambda root, stop=None: walk(root, stop=self.tmp))
-        stopped.start()
-        self.addCleanup(stopped.stop)
-
-    def tool(self, name, body="exit 0"):
-        path = self.bin / name
-        path.write_text(f"#!/bin/sh\n{body}\n")
-        path.chmod(0o755)
-
-    def tools(self, *names):
-        for name in names:
-            self.tool(name)
-
-    def records(self, types=(), fail_on=None):
-        return external.run_external_tools(str(self.project), list(types), fail_on=fail_on)
-
-    @staticmethod
-    def slot(records, slot):
-        return [r for r in records if r["slot"] == slot]
-
-    def cli(self, *args):
-        """`run_audit.py` as a subprocess, with `PATH` the fake tools only."""
-        env = {"PATH": str(self.bin), "PYTHONDONTWRITEBYTECODE": "1"}
-        return subprocess.run([*RUN_AUDIT_CMD, str(self.project), *args], env=env,
-                              capture_output=True, text=True, timeout=120)
-
-    def cli_json(self, *args):
-        proc = self.cli(*args, "--output", "json")
-        return proc, json.loads(proc.stdout)
-
-
-class TestToolRecords(ToolCase):
-    """TC-E2, TC-E4 to TC-E7, TC-E9, TC-E13, TC-E15, TC-E16 drive `run_external_tools` in process."""
-
-    def test_e2_a_tool_that_exits_0_is_ran(self):
-        self.tool("semgrep")
-        [record] = self.slot(self.records(), "sast")
-        self.assertEqual((record["status"], record["exit_code"], record["tool"], record["where"]),
-                         ("ran", 0, "semgrep", "."))
-        self.assertIsNone(record["reason"])
-
-    def test_e2_a_missing_tool_is_not_installed(self):
-        [record] = self.slot(self.records(), "sast")
-        self.assertEqual((record["status"], record["exit_code"]), ("not_installed", None))
-
-    def test_e4_a_timeout_starts_the_fallback_of_the_tree_slot_only(self):
-        self.tool("gitleaks", "exec /bin/sleep 5")
-        self.tool("trufflehog")
-        (self.project / ".git").mkdir()
-        with mock.patch.object(helpers, "TOOL_TIMEOUT", 1):
-            records = self.records()
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
-                         [("gitleaks", "timed_out"), ("trufflehog", "ran")])
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-history")],
-                         [("gitleaks", "timed_out")])
-        self.assertIn("secrets-history", [slot for slot, _ in external.incomplete_slots(records)])
-
-    def test_e5_the_fallback_fills_the_tree_slot_and_the_history_slot_has_none(self):
-        self.tool("trufflehog")
-        (self.project / ".git").mkdir()
-        records = self.records()
-        self.assertEqual([(r["tool"], r["status"]) for r in self.slot(records, "secrets-tree")],
-                         [("gitleaks", "not_installed"), ("trufflehog", "ran")])
-        self.assertEqual([r["tool"] for r in self.slot(records, "secrets-history")], ["gitleaks"])
-        missing = [slot for slot, _ in external.incomplete_slots(records)]
-        self.assertIn("secrets-history", missing)
-        self.assertNotIn("secrets-tree", missing)
-
-    def test_e6_the_git_entry_at_or_above_the_root(self):
-        find = external.find_git_entry.side_effect
-        self.assertIsNone(find(str(self.project)))
-        cases = (("a directory", lambda g: g.mkdir(), "dir"),
-                 ("a file", lambda g: g.write_text("gitdir: elsewhere\n"), "file"),
-                 ("a link", lambda g: g.symlink_to(self.tmp / "real", target_is_directory=True),
-                  "link"),
-                 ("a fifo", lambda g: os.mkfifo(g), "other"))
-        (self.tmp / "real").mkdir()
-        for label, make, kind in cases:
-            with self.subTest(case=label):
-                git = self.project / ".git"
-                make(git)
-                try:
-                    self.assertEqual(find(str(self.project)), kind)
-                finally:
-                    shutil.rmtree(git) if git.is_dir() and not git.is_symlink() else git.unlink()
-        with self.subTest(case="in the parent"):
-            (self.tmp / ".git").mkdir()
-            self.assertEqual(find(str(self.project)), "dir")
-            (self.tmp / ".git").rmdir()
-        with self.subTest(case="a root through a link"):
-            sub = self.tmp / "repo" / "sub"
-            sub.mkdir(parents=True)
-            (self.tmp / "repo" / ".git").mkdir()
-            (self.tmp / "alias").symlink_to(sub, target_is_directory=True)
-            self.assertEqual(external.find_git_entry(str(self.tmp / "alias"), stop=self.tmp), "dir")
-
-    def test_e6_the_history_slot_by_git_entry(self):
-        log = self.tmp / "gitleaks.log"
-        self.tool("gitleaks", f'printf "%s|%s\\n" "$PWD" "$*" >> "{log}"')
-        [record] = self.slot(self.records(), "secrets-history")
-        self.assertEqual((record["status"], record["reason"], record["command"]),
-                         ("not_applicable", "no .git at or above the scanned root", GITLEAKS_HISTORY))
-        (self.project / ".git").symlink_to(self.tmp, target_is_directory=True)
-        [record] = self.slot(self.records(), "secrets-history")
-        self.assertEqual((record["status"], record["reason"]), ("not_run", ".git is a symbolic link"))
-        (self.project / ".git").unlink()
-        expected = f"{self.project}|{' '.join(GITLEAKS_HISTORY[1:])}"
-        cases = (("a directory at the root", lambda: (self.project / ".git").mkdir()),
-                 ("a file at the root",
-                  lambda: (self.project / ".git").write_text("gitdir: elsewhere\n")),
-                 ("a directory in the parent", lambda: (self.tmp / ".git").mkdir()),
-                 ("a bare repository at the root", lambda: self.bare(self.project)))
-        for label, make in cases:
-            with self.subTest(case=label):
-                make()
-                if log.exists():
-                    log.unlink()
-                try:
-                    [record] = self.slot(self.records(), "secrets-history")
-                    self.assertEqual((record["status"], record["command"]),
-                                     ("ran", GITLEAKS_HISTORY))
-                    runs = [run for run in log.read_text().splitlines() if "--no-git" not in run]
-                    self.assertEqual(runs, [expected])
-                finally:
-                    for path in (self.project / ".git", self.tmp / ".git", self.project / "HEAD",
-                                 self.project / "objects", self.project / "refs"):
-                        if path.is_dir():
-                            shutil.rmtree(path)
-                        elif path.exists():
-                            path.unlink()
-
-    def bare(self, root):
-        (root / "HEAD").write_text("ref: refs/heads/main\n")
-        (root / "objects").mkdir()
-        (root / "refs").mkdir()
-
-    def test_e6_a_bare_repository_and_an_unreadable_directory(self):
-        find = external.find_git_entry.side_effect
-        self.bare(self.project)
-        self.assertEqual(find(str(self.project)), "bare")
-        shutil.rmtree(self.project / "objects")
-        (self.tmp / "objects").mkdir()
-        (self.project / "objects").symlink_to(self.tmp / "objects", target_is_directory=True)
-        self.assertEqual(find(str(self.project)), "bare-link")
-        for name in ("HEAD", "objects", "refs"):
-            path = self.project / name
-            shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()
-        if os.geteuid() == 0:
-            self.skipTest("root reads a directory without its search permission")
-        locked = self.project / "locked"
-        locked.mkdir()
-        locked.chmod(0o600)
-        self.addCleanup(locked.chmod, 0o700)
-        self.assertEqual(find(str(locked)), "unreadable")
-
-    def test_e6_each_declined_history_record(self):
-        for kind, status, reason in (
-                ("link", "not_run", ".git is a symbolic link"),
-                ("other", "not_run", ".git is not a directory or a regular file"),
-                ("unreadable", "not_run", ".git could not be read"),
-                ("bare-link", "not_run", "the bare repository holds a symbolic link"),
-                (None, "not_applicable", "no .git at or above the scanned root")):
-            with self.subTest(kind=kind):
-                external.find_git_entry.side_effect = lambda root, stop=None, kind=kind: kind
-                records = self.records()
-                [record] = self.slot(records, "secrets-history")
-                self.assertEqual((record["status"], record["reason"], record["command"]),
-                                 (status, reason, GITLEAKS_HISTORY))
-                missing = [slot for slot, _ in external.incomplete_slots(records)]
-                self.assertEqual("secrets-history" in missing, status == "not_run")
-
-    def test_e7_the_tree_slot_reads_the_working_tree(self):
-        self.tool("gitleaks")
-        [record] = self.slot(self.records(), "secrets-tree")
-        self.assertEqual(record["command"], GITLEAKS_TREE)
-
-    def test_e9_options_that_make_a_finding_exit_non_zero(self):
-        self.tools("trufflehog", "checkov", "trivy", "npm")
-        lock = self.project / "package-lock.json"
-        lock.write_text("{}")
-        (self.project / "package.json").write_text('{"name": "x"}')
-        records = self.records(["iac"])
-        [tree] = [r for r in self.slot(records, "secrets-tree") if r["tool"] == "trufflehog"]
-        self.assertIn("--fail", tree["command"])
-        [trivy] = self.slot(records, "iac-misconfig")
-        self.assertEqual(trivy["command"][-3:], ["--exit-code", "1", "."])
-        for fail_on, level in ((None, None), ("medium", "moderate"), ("high", "high"),
-                               ("critical", "critical")):
-            with self.subTest(fail_on=fail_on):
-                [npm] = self.slot(self.records(fail_on=fail_on), "npm-audit:package-lock.json")
-                levels = [a for a in npm["command"] if a.startswith("--audit-level")]
-                self.assertEqual(levels, [f"--audit-level={level}"] if level else [])
-
-    def test_e13_each_skip_reason_is_a_not_run_record(self):
-        self.tools("npm", "yarn")
-        sub = self.project / "sub"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        [npm] = self.slot(self.records(), "npm-audit:sub/package-lock.json")
-        self.assertEqual((npm["status"], npm["reason"], npm["where"]),
-                         ("not_run", "no package.json beside it", "sub/package-lock.json"))
-        shutil.rmtree(sub)
-        real = self.tmp / "real.lock"
-        real.write_text("")
-        lock, package = self.project / "yarn.lock", self.project / "package.json"
-        for label, reason in (("link", "yarn.lock is a link or not a regular file"),
-                              ("no package.json", "no package.json beside yarn.lock"),
-                              ("not an object", "package.json is not a JSON object")):
-            with self.subTest(case=label):
-                for path in (lock, package):
-                    if path.is_symlink() or path.exists():
-                        path.unlink()
-                if label == "link":
-                    lock.symlink_to(real)
-                else:
-                    lock.write_text("")
-                if label == "not an object":
-                    package.write_text("[]")
-                records = self.records(["javascript"])
-                [yarn] = self.slot(records, "yarn-audit")
-                self.assertEqual((yarn["status"], yarn["reason"], yarn["where"]),
-                                 ("not_run", reason, "yarn.lock"))
-                self.assertIn("yarn-audit", [slot for slot, _ in external.incomplete_slots(records)])
-                summary = _run_audit_module().summarize(
-                    {"scans": {}, "external": external.external_section(records)})
-                self.assertIn(f"external yarn-audit: yarn not_run, {reason}", summary["not_run"])
-        for path in (lock, package):
-            if path.is_symlink() or path.exists():
-                path.unlink()
-        with self.subTest(case="a lockfile that cannot be copied"):
-            os.mkfifo(self.project / "package-lock.json")
-            package.write_text('{"name": "x"}')
-            [npm] = self.slot(self.records(), "npm-audit:package-lock.json")
-            self.assertEqual((npm["status"], npm["reason"]),
-                             ("not_run", "the lockfile could not be copied"))
-
-    def test_e15_three_slots_run_for_a_project_with_no_type(self):
-        self.assertEqual(scanners_types(self.project), [])
-        report = _run_audit_module().run_full_scan(str(self.project), "external")
-        slots = [r["slot"] for r in report["external"]["tools"]]
-        for slot in ("sast", "secrets-tree", "secrets-history"):
-            self.assertIn(slot, slots)
-
-    def test_e16_external_section_status(self):
-        def rec(slot, status):
-            return {"slot": slot, "status": status}
-        section = external.external_section
-        self.assertEqual(section([rec("a", "ran"), rec("b", "not_applicable")])["status"],
-                         "COMPLETE")
-        self.assertEqual(section([rec("a", "ran"), rec("b", "not_installed")])["status"],
-                         "PARTIAL")
-        self.assertEqual(section([rec("a", "not_installed"), rec("a", "ran")])["status"],
-                         "COMPLETE")
-        self.assertEqual(section([rec("a", "not_installed"), rec("b", "not_applicable")])["status"],
-                         "NOT_RUN")
-
-
-def scanners_types(project):
-    return sys.modules[NAME].detect_project_types(str(project))
-
-
-class TestRunAudit(ToolCase):
-    """TC-E1, TC-E3, TC-E8, TC-E10 to TC-E12, TC-E14, TC-E17 drive `run_audit.py`."""
-
-    def test_e1_every_tool_missing_is_not_run_and_exits_3(self):
-        # base-fail: the base prints no report for `external` and exits 0.
-        proc = self.cli("--scan-type", "external", "--output", "json")
-        report = json.loads(proc.stdout)
-        statuses = {r["status"] for r in report["external"]["tools"]}
-        self.assertLessEqual(statuses, {"not_installed", "not_applicable"}, report["external"])
-        self.assertIn("not_installed", statuses)
-        self.assertEqual(report["external"]["status"], "NOT_RUN")
-        self.assertEqual(report["scans"], {})
-        self.assertFalse(report["summary"]["scan_complete"])
-        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
-        self.assertEqual(proc.returncode, 3, proc.stderr)
-
-    def complete_python_project(self):
-        (self.project / "app.py").write_text("x = 1\n")
-        self.tools("semgrep", "gitleaks", "pip-audit")
-        self.tool("bandit", "exit 1")
-
-    def test_e3_a_tool_exit_fails_fail_on_and_is_listed_without_it(self):
-        self.complete_python_project()
-        proc = self.cli("--scan-type", "external", "--fail-on", "critical")
-        self.assertEqual(proc.returncode, 1, proc.stderr)
-        self.assertIn("[GATE] --fail-on critical:", proc.stderr)
-        self.assertIn("bandit exited 1 (python-sast)", proc.stderr)
-        proc, report = self.cli_json("--scan-type", "external")
-        self.assertEqual(proc.returncode, 0, proc.stderr)
-        self.assertEqual(report["summary"]["tool_exits"], ["bandit exited 1 (python-sast)"])
-        self.assertTrue(report["summary"]["scan_complete"], report["summary"]["not_run"])
-
-    def test_e8_stdout_holds_one_json_document(self):
-        self.tool("semgrep", "echo semgrep-stdout; exit 1")
-        self.tool("gitleaks", "echo gitleaks-stdout")
-        proc = self.cli("--scan-type", "external", "--output", "json", "--fail-on", "critical")
-        report = json.loads(proc.stdout)
-        self.assertEqual(report["scan_type"], "external")
-        self.assertNotIn("semgrep-stdout", proc.stdout)
-        self.assertIn("semgrep-stdout", proc.stderr)
-        self.assertNotIn("[GATE]", proc.stdout)
-        self.assertIn("[GATE]", proc.stderr)
-        self.assertEqual(proc.returncode, 1)
-
-    def test_e10_a_breach_and_a_part_not_run_exit_1(self):
-        # The breach: the SBOM scan's medium finding for a project with no SBOM.
-        proc, report = self.cli_json("--scan-type", "all", "--fail-on", "medium")
-        self.assertIn("medium", [f["severity"] for f in report["scans"]["sbom"]["findings"]])
-        self.assertIn("external sast: semgrep not_installed", report["summary"]["not_run"])
-        self.assertIn("[GATE] --fail-on medium:", proc.stderr)
-        self.assertIn("[INCOMPLETE]", proc.stderr)
-        self.assertEqual(proc.returncode, 1)
-
-    def test_e11_deps_with_npm_missing_exits_3(self):
-        sub = self.project / "sub"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        (sub / "package.json").write_text('{"name": "x"}')
-        proc, report = self.cli_json("--scan-type", "deps")
-        self.assertEqual(report["summary"]["not_run"],
-                         ["dependencies: sub/package-lock.json: not audited, npm is not installed"])
-        self.assertIn("[INCOMPLETE]", proc.stderr)
-        self.assertEqual(proc.returncode, 3)
-
-    def test_e12_overall_status(self):
-        run_audit = _run_audit_module()
-        report = run_audit.run_full_scan(str(self.project), "external")
-        self.assertTrue(report["summary"]["overall_status"].startswith("[?] INCOMPLETE: "),
-                        report["summary"])
-        self.complete_python_project()
-        report = run_audit.run_full_scan(str(self.project), "external")
-        self.assertEqual(report["summary"]["overall_status"], "[?] REVIEW RECOMMENDED")
-
-    def test_e14_summary_prints_one_line_per_record(self):
-        self.tools("semgrep", "gitleaks")
-        _proc, report = self.cli_json("--scan-type", "external")
-        out = self.cli("--scan-type", "external").stdout
-        for record in report["external"]["tools"]:
-            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
-            with self.subTest(slot=record["slot"], tool=record["tool"]):
-                self.assertEqual(sum(1 for x in out.splitlines() if x.startswith(line)), 1, out)
-        for label in ("Critical", "High", "Medium", "Low", "Info"):
-            self.assertIn(f"\n  {label}: 0\n", out)
-
-    def test_e18_a_killed_tool_leaves_its_slot_not_run(self):
-        self.tool("semgrep", "kill -9 $$")
-        records = self.records()
-        [record] = self.slot(records, "sast")
-        self.assertEqual(record["status"], "killed")
-        self.assertLess(record["exit_code"], 0)
-        self.assertIn("sast", [slot for slot, _ in external.incomplete_slots(records)])
-
-    def test_e19_printable_escapes_control_format_and_separator_characters(self):
-        self.assertEqual(helpers.printable("a\x1bb\nc\u202ed\u2028e\u2029f\U000e0001g h"),
-                         "a\\x1bb\\x0ac\\u202ed\\u2028e\\u2029f\\U000e0001g h")
-
-    def test_e19_tree_text_is_escaped_in_printed_output(self):
-        sub = self.project / "a\x1b[31mb"
-        sub.mkdir()
-        (sub / "package-lock.json").write_text("{}")
-        (sub / "package.json").write_text('{"name": "x"}')
-        summary = self.cli("--scan-type", "deps")
-        for stream in (summary.stdout, summary.stderr):
-            self.assertNotIn("\x1b", stream)
-        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stderr)
-        self.assertIn("a\\x1b[31mb/package-lock.json", summary.stdout)
-        proc, report = self.cli_json("--scan-type", "deps")
-        self.assertNotIn("\x1b", proc.stdout)
-        self.assertIn("dependencies: a\x1b[31mb/package-lock.json: not audited, npm is not installed",
-                      report["summary"]["not_run"])
-
-    def test_e17_the_summary_counts_every_finding_before_the_cut(self):
-        run_audit = _run_audit_module()
-        findings = [{"type": "t", "severity": "low"}] * 30 + [{"type": "t", "severity": "critical"}]
-        stub = {"tool": "stub", "findings": findings, "status": "[?]"}
-        with mock.patch.object(run_audit, "scan_secrets", return_value=stub):
-            report = run_audit.run_full_scan(str(self.project), "secrets")
-        self.assertEqual((report["summary"]["total_findings"], report["summary"]["critical"]),
-                         (31, 1))
-        self.assertEqual(len(report["scans"]["secrets"]["findings"]), 30)
-        self.assertEqual(run_audit.exit_code(report, "critical"), 1)
-
-
-if __name__ == "__main__":
-    unittest.main()
diff --git a/tests/staged_run_safety_rules.py b/tests/staged_run_safety_rules.py
deleted file mode 100644
--- a/tests/staged_run_safety_rules.py
+++ /dev/null
@@ -1,341 +0,0 @@
-"""Two rules from the TASK 111 retro (R7), as TASK 112 R7 rewrote them.
-
-TASK 111 registered a PreToolUse hook in this repository while building it; the hook then asked
-for approval on the orchestrator's and the reviewers' own commands in Auto mode. Its bypass hunt
-stopped, and the operator deferred the hook to WI-34. This file pins the rules whole:
-
-* `framework-upgrade` §3 step 4, whole and up to the end of §3: what takes effect at once, the
-  scripts that allow rules run, the test-module exemption, the four stages, the failure branch;
-  and §3.1's fixture exception (``TC-1``);
-* `security-audit` §6.2, whole: the three verdicts, one re-run per part, the operator's decision,
-  no unverified control, tests are not the hunt (``TC-2``);
-* each place that routes an audit, as the whole paragraph, list item or table row that holds its
-  pointer, and `full-robust` §3's gate on `audit_status: PASS` and a scan that ran (``TC-3``);
-* each place that turns the scanner's exit code and summary into `scan_status`, as a block of its
-  own: exit 3 or `summary.not_run` gives `NOT_RUN`, and `summary.tool_exits` gives at least
-  `findings` (``TC-3b``, TASK 118 R5.5).
-
-The pinned texts below are written as they stand in their files, wrapped; the tests compare them
-with whitespace collapsed. A change to a pinned rule changes this file in the same edit, where a
-review sees both.
-"""
-import re
-import unittest
-from pathlib import Path
-
-PROJECT_ROOT = Path(__file__).resolve().parent.parent
-WORKFLOW = ".agent/workflows/framework-upgrade.md"
-SKILL = ".agent/skills/security-audit/SKILL.md"
-WRAPPER = ".claude/agents/security-auditor.md"
-
-
-def _flat(text):
-    return " ".join(text.split())
-
-
-STEP_4 = _flat("""
-4. **Hooks and permission rules take effect at once.** Claude Code applies a settings file to the
-   running session as soon as it changes, the reviewers' commands included. The step covers every
-   change that alters what runs, or what runs without a prompt. The list is not exhaustive:
-   - a hook in a settings file, or in the frontmatter of an agent or a skill;
-   - the script of a registered hook, code that script calls, and a new module it would import;
-   - a script that a committed allow rule names, code that script calls, and a new module it
-     would import;
-   - a permission rule, `additionalDirectories` or the permission mode, an agent's
-     `permissionMode` and the `allowed-tools` of a skill or a command among them;
-   - a settings key that names a command, such as `statusLine`, or sets a command's environment,
-     `env`;
-   - the MCP servers of `.mcp.json` or a settings file, and `enableAllProjectMcpServers`.
-
-   Test modules and fixtures that no rule names by path are exempt, and so is code that runs
-   without a prompt only through them. A test module is a `test_*.py` or `conftest.py` file that no
-   hook or listed script runs or imports; a fixture is a data file that a test reads.
-   `tests/run_tests.py` is named by a rule and is not exempt.
-
-   A change that only narrows what runs without a prompt, such as a removed allow rule, may land
-   at once: it runs nothing new, and at worst a command asks. Before the edit, a check shows that
-   it narrows, and the audit record holds the check's output:
-   - a base entry of the same list covers each new allow rule, `additionalDirectories` entry and
-     `allowed-tools` entry;
-   - each base deny or ask rule and `disallowedTools` entry is still present, or a new entry of the
-     same list covers it;
-   - every other key equals the base's;
-   - no code of the list above changes, and no new module appears that it would import.
-
-   The run registers nothing in `.claude/settings.local.json` or the user's settings; an edit
-   there waits for the operator's commit and their go-ahead.
-
-   Every other change runs in four stages. The audit record is
-   `docs/reviews/framework-audit-<ID>.md`; the security audit is the review of stage 2.
-   1. **Fixture.** The TASK states the exact registration: the event, matcher and command of a
-      hook, or the text of a rule or key. A hook's test builds a temporary root with its own
-      `.claude/settings.json` holding that registration, and removes it. Code of the list above
-      is edited under a new name.
-   2. **Reviews.** The code review and the security audit check the code and the registration.
-      Both must pass. An `INCOMPLETE` security audit blocks the registration: `security-audit`
-      §6.2 re-runs the unfinished part once, and then the operator decides.
-      <!-- loop:stage2-review-retry -->
-      - **Bound: max 3 review rounds.** A round is one code review and one security audit of the
-        same fingerprint. A round that does not pass returns the run to the fix of its findings.
-        The §6.2 re-run of an `INCOMPLETE` audit is not a round. Still failing after the 3rd
-        round: **STOP** and escalate to the operator with the open findings; the operator
-        decides what follows.
-      - **LOW routes of a fixed class.** A round whose findings are all LOW, each a route of a
-        class that an earlier round of this run fixed, proposes to the operator before the next
-        round: the scope of each route as a residual in the TASK, and one backlog record that
-        holds them. The operator chooses between that record and one more round. TASK 116 ran
-        seven rounds; from round 4 on, each found a narrower route of one class (WI-48).
-   3. **Registration.** After §4.5, the last edit of the change copies the registration verbatim
-      into its file, or the new code over the code it replaces, and removes the copy under the new
-      name. Only the retro's records follow this edit. The same edit adds a settings test that
-      pins the registration, and the gates run again.
-   4. **Focused review.** A code reviewer and a security auditor check the stage-3 diff on the new
-      fingerprint.
-
-   **Failure.** If the gates of stage 3 fail, or the focused review does not pass, the run
-   restores every file of stage 3's edit at once to its text before that edit. The restore brings
-   back the copy under the new name, if there is one, and the audit record holds the stage-3 diff.
-   - When an `INCOMPLETE` security audit is the only failure, `security-audit` §6.2 governs the
-     re-run, which reads that recorded diff. If the re-run passes, stage 3 applies the same diff
-     again, and stage 4 checks it on the new fingerprint.
-   - In every other case, a failed gate, a rejected code review or a `FAIL` among them, the
-     operator decides what follows. A registration, or the code it runs, whose text changes
-     returns to stage 1.
-
-   **Why.** TASK 111 registered a PreToolUse hook while building it, and the hook asked for
-   approval on the orchestrator's and the reviewers' own commands in Auto mode.
-""")
-SECTION_6_2 = (
-    'An audit has two parts: the scan and the manual adversarial review. Its verdict is one '
-    'of three: - `PASS`: both parts ran to completion and found no CRITICAL or HIGH issue; '
-    '- `FAIL`: a part found a CRITICAL or HIGH issue, whether or not the other part '
-    'completed; - `INCOMPLETE`: a part did not run to completion, and neither part found a '
-    'CRITICAL or HIGH issue. When either part does not run to completion, the audit is '
-    'never `PASS`, and the report names that part. The causes include a refused tool, a '
-    'stopped turn, a missing environment and a scan with `scan_status: NOT_RUN`. An auditor '
-    'whose turn stops returns no report, so the orchestrator records the audit as '
-    '`INCOMPLETE` itself. 1. **Re-run once.** The orchestrator re-runs that part once, in a '
-    "fresh agent or session, on the round's frozen tree. A fix round does not reset the "
-    'count: each part gets one re-run in a run. 2. **Then the operator decides.** If the '
-    're-run does not complete either, the operator chooses in their own message, and the '
-    'record quotes it. The choices are to ship the control with the gap recorded, to defer '
-    'it to a work-item, or to remove it. 3. **No unverified security claim.** A security '
-    'control whose bypass hunt never finished does not ship as protection. Its changelog '
-    'and documents say it is unverified, or it moves to a work-item. 4. **Tests are not the '
-    'hunt.** Tests and a mutation run with a passing baseline show that the tests pin the '
-    "specification. They do not show that the specification closes the threat. (TASK 111's "
-    'retro wrote this rule. The bypass hunt on its anchor hook had stopped, and the '
-    'operator had deferred the hook to a work-item.)'
-)
-#: Each router's pointers, as the whole block that holds each: a paragraph, a list item or a
-#: table row. A sentence appended inside the block changes it (TASK 112 R6.3).
-POINTERS = {
-    WRAPPER: (
-        """- **An unfinished part makes the audit `INCOMPLETE`.** A part is the scan or the
-        adversarial review. When a part found a CRITICAL or HIGH issue, the audit is `FAIL`. Name
-        the unfinished part. The orchestrator re-runs it once, then the operator decides
-        (`security-audit` §6.2).""",
-        """- **`scan_status` is a required field and it is not decoration.** `NOT_RUN` forces
-        `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or HIGH
-        issue — never `PASS`. Without that, a scan-less audit reported the same machine-readable
-        verdict as a clean one, and every consumer that gates on the footer (`full-robust` §3,
-        `security-audit.md` step 4) treated "we did not look" as "we looked and it was fine".
-        Reporting the gap in prose while the footer says `PASS` is the fabrication this replaced,
-        one layer down.""",
-    ),
-    "System/Agents/10_security_auditor.md": (
-        """5. **Unfinished parts:** a scan or an adversarial review that did not run to completion
-        makes the audit `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue, and the
-        summary names it (`security-audit` §6.2).""",
-        """- `scan_status` is `"clean" | "findings" | "NOT_RUN"` and is **required**. `"NOT_RUN"`
-        forces `audit_status: "INCOMPLETE"`, or `"FAIL"` when the manual review found a CRITICAL or
-        HIGH issue — never `"PASS"`. Without it a scan-less audit is machine- indistinguishable
-        from a clean one, and every consumer that branches on this footer treats "we did not look"
-        as "we looked and it was fine".""",
-    ),
-    ".agent/workflows/security-audit.md": (
-        """- A review that does not run to completion makes the audit `INCOMPLETE`, or `FAIL` when a
-        part found a CRITICAL or HIGH issue: name the part. The orchestrator re-runs it once, then
-        the operator decides (`security-audit` §6.2).""",
-        """- **If you cannot execute it** (no execution tool in your role, or the environment
-        refuses): record `scan_status: NOT_RUN (<reason>)`, continue to step 3, and carry that
-        status into the report. **Never invent the output** (`security-audit` §1). `NOT_RUN` makes
-        the audit `INCOMPLETE`, or `FAIL` when step 3 finds a CRITICAL or HIGH issue, never `PASS`
-        — step 4's "until clean" loop cannot be satisfied by a scan that never ran.""",
-        """- If findings exist: a. Fix implementation (apply patches, rotate secrets). b. Add
-        regression tests (security-focused). <!-- loop:audit-remediation --> c. Re-run audit
-        script until clean. **Bound: max 3 iterations** when this workflow is entered directly; a
-        caller may re-scope both the cap and the definition of "clean" (`full-robust` §3 does
-        exactly that). On exhaustion with findings still open → **STOP** and escalate the open
-        findings to the user. Per step 2, a `scan_status: NOT_RUN` never satisfies this loop: the
-        verdict is `INCOMPLETE` or `FAIL`, not clean, and `security-audit` §6.2 governs its one
-        re-run.""",
-    ),
-    ".agent/workflows/full-robust.md": (
-        """- **Gate:** the audit footer reads `audit_status: PASS`, the automated scan ran to
-        completion (`scan_status` is `clean` or `findings`), AND the manual review (per the
-        `security-audit` skill §3 checklists) emits a severity-labelled findings table with **no
-        CRITICAL/HIGH findings**. The table rules on each CRITICAL or HIGH hit of the scan: a
-        confirmed hit is a finding, and a rejected one is listed as a false positive. An
-        `INCOMPLETE` audit never meets it.""",
-        """- **A scan that did not run is not a scan that passed.** `scan_status: NOT_RUN`
-        (equivalently a `scan: NOT RUN (<reason>)` line) fails the scan conjunct: the gate is **not
-        met** and the verdict is `INCOMPLETE`, or `FAIL` when the manual review found a CRITICAL or
-        HIGH issue. The missing part is re-run once; if it still does not complete, the reason is
-        escalated to the user (`security-audit` §6.2). Left unstated, `NOT RUN` is neither clean
-        nor unclean and the undefined branch resolves in practice to "the other conjunct
-        passed".""",
-    ),
-    "System/Docs/SKILLS.md": (
-        """| **`security-audit`** | Vulnerability assessment v3.12 (two-layer model: deterministic
-        regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping
-        table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance,
-        auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity
-        reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC
-        (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool
-        integrations (incl. `snyk-agent-scan`), a status for each external tool and exit 3 for a
-        scan part that did not run, private disclosure of a dependency finding (§6.1), an
-        unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH
-        issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |""",
-    ),
-    "System/Docs/WORKFLOWS.md": (
-        """| **Security Audit** | Runs the security auditor agent. Remediation loop bounded at **max
-        3 iterations** when invoked directly; `full-robust` §3 re-scopes both the cap and the
-        definition of "clean". A `scan_status: NOT_RUN` yields `INCOMPLETE`, or `FAIL` when the
-        manual review found a CRITICAL or HIGH issue, never clean (`security-audit` §6.2). | `run
-        security-audit` |""",
-    ),
-}
-
-#: TC-3b (TASK 118 R5.5): each router that reads the scanner states how its exit code and summary
-#: set `scan_status`, in a block outside the blocks of `POINTERS`.
-SCAN_STATUS_POINTERS = {
-    WRAPPER: (
-        """- **The scanner's exit code and summary set the floor of `scan_status`.** Exit 3, or a
-        `summary.not_run` list that is not empty, means a part of the scan did not run:
-        `scan_status: "NOT_RUN"`. A `summary.tool_exits` list that is not empty means an external
-        tool reported a finding or failed: `scan_status` is at least `"findings"`, and
-        `"NOT_RUN"` when the tool's output shows an error (`security-audit` §2). A run that prints
-        no report, such as exit 1 with a JSON `error` or exit 2, is `"NOT_RUN"`.""",
-    ),
-    "System/Agents/10_security_auditor.md": (
-        """- The scanner sets the floor of `scan_status`. Exit 3, or a `summary.not_run` list that
-        is not empty, gives `"NOT_RUN"`. A `summary.tool_exits` list that is not empty gives at
-        least `"findings"`, and `"NOT_RUN"` when the tool's output shows an error
-        (`security-audit` §2). A run that prints no report, such as exit 1 with a JSON `error` or
-        exit 2, gives `"NOT_RUN"`.""",
-    ),
-    ".agent/workflows/security-audit.md": (
-        """- **A partial scan is `NOT_RUN`.** Exit 3, or a `summary.not_run` list that is not
-        empty, records `scan_status: NOT_RUN (<the parts it names>)`. A `summary.tool_exits` list
-        that is not empty records at least `scan_status: findings`, and `scan_status: NOT_RUN`
-        when the tool's output shows an error (`security-audit` §2). A run that prints no report,
-        such as exit 1 with a JSON `error` or exit 2, records `scan_status: NOT_RUN`.""",
-    ),
-}
-
-
-def _read(rel):
-    path = PROJECT_ROOT / rel
-    if not path.is_file():
-        raise AssertionError(f"{rel}: the file is missing")
-    return path.read_text(encoding="utf-8")
-
-
-def _section(text, heading):
-    m = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.M)
-    if not m:
-        raise AssertionError(f"heading {heading!r} is missing")
-    level = len(m.group(1))
-    end = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, m.end())
-    return text[m.end():end.start() if end else len(text)]
-
-
-def _step(section, number):
-    """The text of a top-level numbered step, up to the next one."""
-    m = re.search(rf"^{number}\. .*?(?=^\d+\. |\Z)", section, re.M | re.S)
-    if not m:
-        raise AssertionError(f"step {number} is missing")
-    return m.group(0)
-
-
-def _step_to_end(section, number):
-    """The text of a top-level numbered step, up to the end of the section (TASK 112 R6.3)."""
-    m = re.search(rf"^{number}\. ", section, re.M)
-    if not m:
-        raise AssertionError(f"step {number} is missing")
-    return section[m.start():]
-
-
-def _blocks(text):
-    """Each paragraph, list item and table row of `text`, whitespace collapsed."""
-    item = re.compile(r"^\s*(?:[-*+]|\d+\.)\s|^\s*\|")
-    blocks, current = [], []
-    for line in text.splitlines():
-        if not line.strip() or (item.match(line) and current):
-            if current:
-                blocks.append(_flat(" ".join(current)))
-            current = [line] if line.strip() else []
-            continue
-        current.append(line)
-    if current:
-        blocks.append(_flat(" ".join(current)))
-    return blocks
-
-
-class TestHookRegistration(unittest.TestCase):
-    """TC-1: a hook or a permission rule takes effect at once."""
-
-    maxDiff = None
-
-    def setUp(self):
-        self.section = _section(_read(WORKFLOW), "3. Execution (Atomic Updates)")
-
-    def test_step_4_is_the_reviewed_text_to_the_end_of_section_3(self):
-        self.assertEqual(_flat(_step_to_end(self.section, 4)), STEP_4)
-
-    def test_base_check_allows_the_fixture(self):
-        self.assertIn("A test fixture that the test itself creates in a temporary directory and "
-                      "removes is no such copy (step 4).", _flat(_step(self.section, 1)))
-
-
-class TestIncompleteReview(unittest.TestCase):
-    """TC-2: a review that cannot finish."""
-
-    maxDiff = None
-
-    def test_section_6_2_is_the_reviewed_text(self):
-        self.assertEqual(_flat(_section(_read(SKILL), "6.2 A review that cannot finish")),
-                         SECTION_6_2)
-
-
-class TestPointers(unittest.TestCase):
-    """TC-3: every place that routes an audit states the rule, in a block of its own."""
-
-    maxDiff = None
-
-    def test_each_router_states_the_rule_whole(self):
-        for rel, expected in POINTERS.items():
-            blocks = _blocks(_read(rel))
-            for block in expected:
-                block = _flat(block)
-                with self.subTest(file=rel, block=block[:50]):
-                    self.assertIn(block, blocks)
-
-    def test_each_router_maps_the_scanner_status(self):
-        """TC-3b (TASK 118 R5.5)."""
-        for rel, expected in SCAN_STATUS_POINTERS.items():
-            blocks = _blocks(_read(rel))
-            for block in expected:
-                block = _flat(block)
-                with self.subTest(file=rel, block=block[:50]):
-                    self.assertIn(block, blocks)
-
-    def test_blocks_split_at_items_rows_and_blank_lines(self):
-        text = "- one\n  two\n- three\n\npara\nline\n| a | b |\n| c | d |\n"
-        self.assertEqual(_blocks(text), ["- one two", "- three", "para line", "| a | b |",
-                                         "| c | d |"])
-
-
-if __name__ == "__main__":
-    unittest.main()
diff --git a/.agent/skills/security-audit/SKILL.md b/.agent/skills/security-audit/SKILL.md
--- a/.agent/skills/security-audit/SKILL.md
+++ b/.agent/skills/security-audit/SKILL.md
@@ -2,10 +2,10 @@
 name: security-audit
 description: Use when performing security vulnerability assessment (OWASP, secrets, dependencies, IaC, LLM, API, MCP/agentic) or when "thinking like a hacker" to find exploits.
 tier: 2
-version: 3.11
+version: 3.12
 ---
 
-# Security Audit v3.11
+# Security Audit v3.12
 
 ## 0. Methodology — Two Layers (audit-067 C-10)
 
diff --git a/System/Docs/SKILLS.md b/System/Docs/SKILLS.md
--- a/System/Docs/SKILLS.md
+++ b/System/Docs/SKILLS.md
@@ -139,7 +139,7 @@
 | - `code-review-checklist` | For checking Code implementation. | `03-develop-single-task` | Code Reviewer |
 | **`skill-spec-validator`** | **Automated Gatekeeper.** Validates RTM existence and Atomic Plan coverage. **Language-independent**: locates the RTM by the `<!-- contract:rtm -->` anchor and reads the id column positionally, with the English heading/column matchers kept as an unchanged fallback for anchorless documents (both modes share one locator). | `vdd-enhanced` | System / Orchestrator |
 | **`skill-self-improvement-verificator`** | **Meta-Auditor.** Verifies safety of Framework Upgrades. | `framework-upgrade` | System / Orchestrator |
-| **`security-audit`** | Vulnerability assessment v3.11 (two-layer model: deterministic regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance, auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool integrations (incl. `snyk-agent-scan`), private disclosure of a dependency finding (§6.1), an unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |
+| **`security-audit`** | Vulnerability assessment v3.12 (two-layer model: deterministic regex floor + LLM semantic pass): OWASP Top 10:2025 (final taxonomy, 2021→2025 mapping table included), **MCP/agentic (OWASP ASI Top 10 2026)** — config provenance, auto-approve, unpinned servers, tool-poisoning heuristics, smart contracts (Solidity reentrancy, delegatecall, oracle manipulation), secrets (28 patterns + entropy), IaC (Docker/K8s/Terraform), SBOM, CI/CD gates. 148 automated regex patterns + external tool integrations (incl. `snyk-agent-scan`), a status for each external tool and exit 3 for a scan part that did not run, private disclosure of a dependency finding (§6.1), an unfinished review reported as `INCOMPLETE`, or `FAIL` when a part found a CRITICAL or HIGH issue (§6.2). | `security-audit`, `full-robust` | Security Auditor |
 
 ### Executable Skills (Tools)
 | Skill | Description | Used By in Workflows | Used By Agents |
diff --git a/System/Docs/VDD.md b/System/Docs/VDD.md
--- a/System/Docs/VDD.md
+++ b/System/Docs/VDD.md
@@ -21,4 +21,4 @@
 *   When "good enough" is not enough.
 
 ## Integration with Security Audit
-VDD pairs naturally with the `security-audit` skill (v3.11). The adversarial loop can include automated scanning (`run_audit.py`) to verify that the scanner itself catches real-world vulnerability patterns. This was validated in VDD Rounds 1-3 against recent DeFi hacks (Dec 2025 – Mar 2026), resulting in 16 new Solidity-specific detection patterns.
+VDD pairs naturally with the `security-audit` skill (v3.12). The adversarial loop can include automated scanning (`run_audit.py`) to verify that the scanner itself catches real-world vulnerability patterns. This was validated in VDD Rounds 1-3 against recent DeFi hacks (Dec 2025 – Mar 2026), resulting in 16 new Solidity-specific detection patterns.
~~~~

### I1 — the apply

- `git apply --whitespace=nowarn docs/reviews/framework-audit-118-stage3.diff`: exit 0.
- Postcondition: each of the seven final paths hashes to its staged file's recorded value; the
  seven staged files are gone; `git apply --check -R` passes. `SKILL.md` reads `version: 3.12` and
  `# Security Audit v3.12`; `SKILLS.md` and `VDD.md` read v3.12.

### I2 — the gates of stage 3

- `run_gates.sh`: 17 PASS. `tests/run_tests.py` ran 601 tests on the new code: OK (569 before the
  patch).
- `pytest .agent/skills/security-audit/tests/`: 30 passed, on the new code.
- `validate_skill.py .agent/skills/security-audit`: exit 0, "PASSED with warnings"; the warnings
  name the skill's directory layout and its Execution Policy sections, which this change does not
  touch.
- `check_positional_refs.py --targets-changed`: 12 errors in 40 documents. The three beyond §4.5's
  nine are `UNRESOLVABLE` references to files of other repositories, in
  `docs/plans/plan-103-referent-carrying-positional-references.md` and
  `docs/reviews/framework-audit-105.md`, which the wider set of changed files now selects. No
  `REFERENT_MOVED` or `REFERENT_ABSENT` comes from the patch.
- Declared paths: every entry of `git status` is declared.

## Stage 4 — fingerprint `d4b372345a21`

Both agents, resumed, quoted the fingerprint at their start and end; the caller recomputed it on
return: equal.

- **Code review: APPROVED**, no finding. Each final file hashes to its approved staged text;
  `run_audit.py` kept mode 755; the version mirrors read 3.12. On the final paths:
  `test_lockfile_audit.py`, `test_run_safety_rules.py` and `test_disclosure_rule.py` 80 passed;
  the skill's tests 30 passed; `tests/run_tests.py` 601 tests OK. No setting, hook, test module or
  CI workflow names a staged file.
- **Security audit: INCOMPLETE**, on the scan gap alone; the manual check found no open CRITICAL or
  HIGH and nothing new in the diff. The scanner now on disk, run on this repository with
  `--scan-type all --output json`, exited 3 with one JSON document on stdout. `summary.not_run`
  named five slots (semgrep, trufflehog after gitleaks, gitleaks, bandit, pip-audit), and
  `external.status` was `PARTIAL`. `summary.tool_exits` named npm's exit 1 for the three renderer
  lockfiles. None of the in-process CRITICAL or HIGH hits is in a changed file; one MEDIUM in
  `tests/test_lockfile_audit.py` is a fixture path, a false positive.

**The Failure rule.** The `INCOMPLETE` audit is the only failure, and the three conditions of the
PLAN's second branch hold:

1. the unfinished part is the scan, which had its re-run at stage 2 for the same cause;
2. the code review of stage 4 passed;
3. the manual part ran to completion with no CRITICAL or HIGH finding.

D17 covers stage 4 (TASK R7.10): "Отгрузить с записанным пробелом (Recommended)". The run
therefore:

- restored stage 3 with `git apply -R --whitespace=nowarn` of the same patch: exit 0; each of the
  17 files equals the hash and mode of I1 step 3;
- applied I1 again with every step: §4.5 with `--fix` touched no file; the patch and the staged
  files hashed to the values of round 3; `git apply` exit 0; the postcondition held;
- ran I2 again: `run_gates.sh` 17 PASS, `tests/run_tests.py` 601 tests OK, the skill's tests 30
  passed, `validate_skill.py` exit 0, the resolver's 12 errors as before with no
  `REFERENT_MOVED`.

The fingerprint after the re-apply is `d4b372345a21`, the tree that stage 4 reviewed. Stage 4 is
not repeated.

**Gap recorded (D17).** The external layer did not run in any audit of this run: semgrep,
gitleaks, trufflehog, bandit and pip-audit are not installed on the operator's machine. The
in-process scans and the manual reviews ran to completion. TASK 118 adds no dependency.

**Scratch files deleted after stage 4:** `stage_driver.py`, `bootstrap_next.py`, `staging.py`,
`mutation_driver.py`, `gen_stage3_patch.py`, the outputs `d1.out`, `d2.out`, `d1.stderr`,
`status.txt`, `st-before.txt`, `patch-files.txt`, and the reviewers' scratch directories. The files
of K (`run_gates.sh`, `regcheck.py`, the gate logs, `refs-living.log`, `i1-full.txt`,
`i1-table.md`) are deleted with the restart notice.

## Retro (§6)

The retro question listed four candidates: the spec-audit bound, pip-audit's target and yarn's
unranked exit, the orchestrator's own slips, and the first §6.2 question that named no tool. The
operator answered, in Russian, that the question about the missing tools had stayed unanswered,
and asked to skip the rest. Nothing is filed; the claim `framework-upgrade-wi-42-scan-status` is
released. The final message answers the question.

## Scan after the tool install (2026-10-09)

After the run, the operator installed gitleaks 8.30.1, bandit 1.9.4, pip-audit 2.10.1 and semgrep
1.180.0 with Homebrew. Homebrew updated itself to 7.0.9 during the install. Its `openssl@4` keg
was left without `lib/` until the operator unlinked `openssl@3` and installed `openssl@4` again;
the operator's checks then passed: a TLS handshake with `openssl@4` verified, Homebrew's Python
3.14.8 reached HTTPS, and the pyenv Python 3.14.4 still loads `OpenSSL 3.6.2`. trufflehog, the
working-tree fallback, is not installed.

`run_audit.py . --scan-type external --output json`, on the tree after stage 3, 2026-10-09
07:47:39Z to 07:48:26Z:

- exit 0; `external.status: COMPLETE`; `summary.not_run` empty; `scan_complete: true`;
- `summary.tool_exits`: semgrep, gitleaks (both slots), bandit and npm (three lockfiles) exited 1;
  pip-audit exited 0. Each exit is a finding, by the tool's own summary: semgrep "3 Code
  Findings", gitleaks "leaks found", bandit's issue list, npm's advisories. No tool reported an
  error.

Triage against the files of this change:

- semgrep: 3 findings, in `measure_text.mjs`, `setup_renderers.sh` and `System/scripts/doctor.py`;
  none in a file of this change.
- gitleaks, rerun with a redacted JSON report to the scratchpad: 747 in the working tree and 746
  in the history, 737 of them in the eval corpus of `mermaid-authoring-guidelines`, the rest in
  reference documents and test fixtures. None in a file of this change.
- bandit: 8 LOW findings in files of this change. B404 and B603 at `audit/helpers.py` and
  `audit/scanners.py`, and B607 at `scanners.py`: the scanner starts tools by design, with an
  argument list and no shell. B404 and B603 in `tests/test_lockfile_audit.py`: the tests start the
  scanner and fake tools. No MEDIUM or HIGH in a file of this change.
- npm: the low katex advisories of WI-41.
- pip-audit audited its own environment (TASK §8).

The scan part now ran to completion with no CRITICAL or HIGH finding in this change. The gap that
D17 recorded is closed for TASK 118.
