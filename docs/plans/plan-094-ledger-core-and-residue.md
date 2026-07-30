# Development Plan — TASK 094: one ledger write path (WI-9) + the residue (WI-8)

**Scope:** `run-feedback` library + CLI + tests + SKILL.md. No contract change, so
`known-issues-format` and its templates are untouched and `check_contract_sync.py` must stay green
without edits. No workflow, agent, or bootstrap-file change.

**Rollback:** clean tree at `d2053e6`. Per-step `git checkout -- <path>`; task-wide
`git reset --hard d2053e6`.

**RED-before-GREEN, per guard** (standing rule from audit 093): every new guard's test is run before
its fix and observed to fail, or mutation-checked after with the confirmation recorded. For the
*refactor* steps the discipline inverts and is stronger — see Step 0.

## Step 0 (R2, R18) — freeze the regression net BEFORE touching anything

- [ ] Record the current suite as the baseline: `286 passed`. **Do not edit a single existing test
      during Steps 1–3.** A refactor whose tests change alongside it proves nothing; the value of
      these 286 is precisely that they were written against the old code.
- [ ] **Freeze the tree for any review that runs against it** — iteration 3's `critic-security` read
      two different versions of one file because I was editing during the review, and correctly
      refused to certify the exit bar. If a critic is spawned in this task, no edits until it returns.
- [ ] Capture the five iteration-3 exploit probes as a shell script in the scratchpad so they can be
      re-run by hand after the refactor (they are already unit tests; this is belt and braces on the
      exact commands that reproduced them).

**Verify:** `python3 -m unittest discover -s tests` → 286, and the probe script exits clean.

## Step 1 (R1, R2, R3) — extract `feedback_lib/ledger_core.py`

- [ ] `Registry` descriptor carrying only what differs: `noun`, `records_dir`, `index_path`,
      `status_vocab`, `rank_vocab` + `rank_name`, `seed_text()`, `insert(index_text, line, where)`,
      `build_meta(...)`, `format_line(...)`, `link_for(...)`, `result_map`.
- [ ] `file_record(config, reg, record_id, slug, title, body, ...)` — the single choreography, in one
      fixed order (vocab → lexists → `assert_id_free` → `guard_config_body` → meta → banner → record
      text → index line → index insert → symlink refusal → `O_EXCL|O_NOFOLLOW` create → rollback →
      index write → rollback). Every guard exactly once.
- [ ] Both `file_defect` / `file_work_item` become descriptor construction + a result-key remap.
      **Signatures and result keys unchanged** (R2).
- [ ] Delete the now-dead duplicates: `_rollback`, `_write_atomic`, the two create blocks.

**Verify:** the 286 baseline passes **unmodified**. Then `grep -c "O_EXCL"` across `feedback_lib/`
must be exactly 1 — the mechanical proof that the choreography is no longer duplicated.

## Step 2 (R3, R17) — one parameterized guard-inventory test

- [ ] `tests/test_ledger_core.py`: a table of every guard from iterations 1–3, each exercised against
      **both** registries through the public API. This is the test that makes "fixed on one path only"
      structurally impossible to reintroduce, and it replaces nothing — the older per-registry tests
      stay as the refactor's net.
- [ ] **The inventory records WHICH registry each guard fired for** (audit 094 Required Action 1). A
      test that only asserts "some registry refused" could pass with a guard live on one path and a
      coincidental failure on the other — which is precisely the hazard this task exists to close, so
      the instrument meant to pin it must not have the same blind spot.

**Verify:** new tests green; then mutation-check by removing one guard from `file_record` and
confirming the inventory test reddens with **both** registry entries flipped (a single-registry
failure would mean the descriptor still carries per-registry logic).

## Step 3 (R4, R5) — the residue fixes that live in the core

- [ ] **R4 / L-16** seed when the index is missing **or blank** (`not text.strip()`).
- [ ] **R5 / sec-L-07** immediately before the create, re-verify `os.path.realpath(records_dir)`
      equals the configured resolved path; refuse otherwise. Closes the TOCTOU window on intermediate
      components that `O_NOFOLLOW` (final component only) cannot see.

**Verify:** two new tests per registry via the parameterized helper; both fail before the fix.

## Step 4 (R6, R9, R10) — `atomic` + `frontmatter`

- [ ] **R6 / sec-L-08** `write_atomic`: refuse a symlink target; mode from `os.lstat`.
- [ ] **R9 / L-22** `_strip_comment`: quoted only when a closing quote exists and only whitespace or
      ` #` follows; otherwise keep the raw text. Re-check the `was_quoted` coercion guard still holds.
- [ ] **R10 / sec-L-01** `parse`: refuse a duplicate key in one block.

**Verify:** the `parse(serialize(m)) == m` property test still passes — it is the assertion that would
catch a regression in this area at once.

## Step 5 (R7, R8) — the two index-insertion fixes

- [ ] **R7 / L-20** exact-match placeholder + collapse the orphaned blank line.
- [ ] **R8 / L-24** sorted-heading placement for a new category.

**Verify:** direct unit tests on the pure functions (iteration 3 noted these had none).

## Step 6 (R11, R12, R13, R14, R15) — CLI, config, and the two perf items

- [ ] **R11 / L-17** `doctor` evaluates every validating property inside its guarded block.
- [ ] **R12 / sec-L-09** `feedback_dir` gets the forbidden-root check (`.git` at minimum) while the
      `.agent/feedback` default keeps working — this is the exception that made `ledger=False` exist,
      so the fix is a narrower exemption, not removing the guard. **Acceptance is a PAIR** (audit 094
      Required Action 2): `.agent/feedback` must still load **and** `.git/objects` must be refused.
      One assertion without the other either breaks every consumer or changes nothing.
- [ ] **R13 / sec-L-11** escape the triage table cells properly.
- [ ] **R14** stat-then-refuse in `_read_maybe_stdin` for `--body-file`.
- [ ] **R15** `write_atomic(..., durable=False)` for inbox/journal writes; ledgers stay durable.

**Verify:** per-item unit tests; `doctor --json` on this repo still `ready: true`.

## Step 7 (R16) — the two under-pinning tests

- [ ] Exercise `_within` directly with a NUL path; assert the filename-invariant test against the
      **glob** rather than a proxy. Mutation-check both.

## Step 8 (R18, R19) — prove nothing broke

- [ ] Full sweep: both suites, `test_e2e.sh`, `check_contract_sync.py`, `validate_skills.py`,
      `doctor`, `run_audit.py` (expect hits only under `tests/`).
- [ ] Re-run the Step 0 exploit probe script by hand — all five must still be refused.
- [ ] **Mutation sweep on the refactor**: disable, one at a time, the guards that the extraction
      moved (`O_EXCL`, the `BaseException` rollback, `assert_id_free`, `guard_config_body`, the
      lexists pre-check) and confirm the inventory test reddens for both registries. Restore.
- [ ] Confirm both live consumer configs still load and validate.

## Step 9 (R20) — close the ledger, release notes

- [ ] Close WI-8 and WI-9 in lockstep; WI-8's resolution **must** state that sec-L-10 was not fixed
      and why (TASK §4), plus any other row left open.
- [ ] CHANGELOG (EN + RU), session state, archive TASK/PLAN in lockstep.
