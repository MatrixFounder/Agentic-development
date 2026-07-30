# Technical Specification: one ledger write path (WI-9) + the iteration-3 residue (WI-8)

### 0. Meta Information
- **Task ID:** 094
- **Slug:** ledger-core-and-residue

## 1. General Description

Two work-items, done in one task **in this order on purpose**: **WI-9** extracts the duplicated write
choreography of `ledger_issues` / `ledger_backlog` into one `ledger_core`, and **WI-8** then applies
16 recorded findings — several of which live inside that choreography, so fixing them after the
extraction lands each one **once, for both registries, by construction** instead of twice by hand.
Doing WI-8 first would mean editing the same 110 near-parallel lines in two modules and then moving
them, which is the exact habit that produced the class.

**Why WI-9 now.** Writer asymmetry has produced a confirmed finding in **every** adversarial
iteration over this code — three for three (WI-23 origin; iteration 2's V12; iteration 3's L-1, L-2,
L-4, L-5, L-6, H-04). TASK 093 was *specifically about* that class and produced six more instances
while fixing it. Iteration 3 already extracted the shared **mechanisms** (`markdown.py`,
`ids.assert_id_free`, `atomic.read_verbatim`, `body.guard_config_body`); what remains duplicated is
the **choreography** — vocab check, lexists pre-check, id guard, body guard, meta build, record text,
index line, index insert, symlink refusal, `O_EXCL|O_NOFOLLOW` create, rollback, dry-run payload.

**The safety property that makes this reviewable:** both public functions (`file_defect`,
`file_work_item`) keep their **exact signatures and exact result-dict keys**. Only their bodies
become thin registry descriptors over one core. That makes the existing 286 tests a true regression
net for the refactor rather than something to be rewritten alongside it — a refactor whose tests
change with it proves nothing.

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | Verification |
|----|-------------|--------------|
| R1 | `feedback_lib/ledger_core.py` holds ONE `file_record()` implementing the whole write choreography, driven by a per-registry descriptor (noun, dirs, vocab, seed, index inserter, line builder, meta builder, result-key map). | Both writers reduced to descriptors; `file_record` is the only place `O_EXCL` / rollback / lexists appear. |
| R2 | `file_defect` and `file_work_item` keep byte-identical signatures and result-dict keys (`issue_id`/`issue_path`/`index_path`/`seeded_index` · `item_id`/`record_path`/`backlog_path`/`seeded_backlog`/`layout`), so no caller or test changes. | The full pre-existing suite passes **unmodified**; `git diff` shows no edits to the assertions that pin those keys. |
| R3 | Every guard from iterations 1–3 is present for **both** registries by construction: vocab, lexists pre-check (with its distinct message), `ids.assert_id_free`, `body.guard_config_body`, provenance banner + key, `CONTRACT_KEYS`-driven meta, symlink-dir refusal, `O_EXCL\|O_NOFOLLOW`, `except BaseException` rollback, index-write rollback, `provisional_id`. | A test enumerating the guard list runs it against both registries through the public API. |
| R4 | (L-16) An index file that exists but is **empty or whitespace-only** is seeded from the template instead of producing a preamble-less ledger. Both registries. | Unit test per registry: a 0-byte index yields a record plus a full preamble. |
| R5 | (sec-L-07) The record directory is re-verified immediately before the create: if its realpath differs from the configured resolved path (an intermediate component swapped to a symlink after the config check), the write is refused. Both registries. | Unit test planting a symlinked intermediate directory after config resolution. |
| R6 | (sec-L-08) `atomic.write_atomic` refuses to replace a path that is a **symlink**, and takes its mode from `lstat`, so a symlink cannot widen the replacement's permissions. | Unit tests: a symlinked target is refused; mode is preserved for a regular file. |
| R7 | (L-20) The placeholder strip matches the seeded placeholder text exactly, not a wildcard that would delete a human's italic note; the blank line it leaves behind is collapsed. | Unit tests: exact placeholder removed; a similar-shaped legitimate note kept. |
| R8 | (L-24) A new category section is placed by comparing against the **sorted** heading list, so an unsorted ledger does not receive it in the wrong place. | Unit test with out-of-order existing sections. |
| R9 | (L-22) `frontmatter._strip_comment` treats a value as quoted only when a matching closing quote exists and nothing but whitespace or a `#` comment follows; otherwise the raw text is kept. | Unit tests: `"The Big Bug" (again)` keeps `(again)`; `'tis a thing` keeps the apostrophe. |
| R10 | (sec-L-01) `frontmatter.parse` refuses a **duplicate key** in one frontmatter block — the "a human reads the first value, a tool reads the second" primitive. | Unit test; a tolerant read of unknown keys still works. |
| R11 | (L-17) `doctor` evaluates every validating config property (`id_prefixes`, `excerpt_max_chars`, `body_max_chars`, `backlog_prefix`) and reports `ready: false` when one is unusable, so it can no longer say go while every `file` exits 3. | Unit test: `body_max_chars: 0` makes `doctor` not-ready and names the key. |
| R12 | (sec-L-09) `feedback_dir` refuses `.git` and the other executable-surface roots. The documented `.agent/feedback` default still works. | Unit tests both ways. |
| R13 | (sec-L-11) `cmd_triage`'s table escapes every character that could forge a row, not only `\|`; a multi-line mined message cannot splice a fake row into the table the model reads. | Unit test with a newline- and pipe-bearing message. |
| R14 | (perf) `_read_maybe_stdin` refuses an over-ceiling `--body-file` **without reading it whole**, so a multi-GB file is a clean exit 2 rather than an OOM the cap cannot prevent. | Unit test with a stat-mocked huge file asserting no full read. |
| R15 | (perf) Inbox/journal writes do not `fsync`; ledger writes still do. Machine state under `.agent/feedback/` is regenerable, and the barrier sat inside the collect flock. | Unit test asserting `fsync` is called for a ledger write and not for an inbox write. |
| R16 | (L-18, L-19) The two under-pinning tests are corrected: `_within`'s NUL path is exercised directly, and the filename-invariant test asserts against the **glob itself** rather than a proxy. | Both tests fail when their guard is removed (mutation-checked). |
| R17 | Every fix in R4–R15 that applies to both registries is verified against both, in one parameterized test rather than two copies. | Test file review: no per-registry duplication of a shared guard. |
| R18 | All prior exploits stay closed after the refactor: S-01…S-05, F1–F17, V1–V22, H-01…H-04, L-1/L-2/L-8. | The complete existing suite (286) plus the new tests, all green; the five iteration-3 exploits re-probed by hand. |
| R19 | Gates green: both unit suites, `test_e2e.sh`, `check_contract_sync.py`, `validate_skills.py` 45/45, `doctor ready: true`, and the security scanner clean **outside** `tests/`. | Full sweep. |
| R20 | WI-8 and WI-9 closed in lockstep, with any row deliberately not implemented stated in the resolution rather than omitted. | `git diff` of `docs/BACKLOG.md` + `docs/backlog/*`. |

## 3. Non-functional Requirements
- **No behaviour change is permitted except the 16 recorded fixes.** The refactor is
  behaviour-preserving by contract; every observable difference must trace to an R4–R15 row.
- **Compatibility:** `config.v` stays `1`. Python 3.9+, stdlib only. Both consuming repos
  (`Universal-skills`, `onchain-analytics`) consume these skills **by symlink**, so every change is
  live for them on save and no existing config key may change meaning.
- **Performance:** the extraction must not add file reads or process spawns per filing.

## 4. Constraints and Assumptions
- **The result-dict keys are the compatibility surface.** `cmd_file` and several tests read
  `result["issue_path"]`, `result["record_path"]`, `result["index_line"]`, `result["seeded_*"]`,
  `result["layout"]`, `result["provisional_id"]`. R2 forbids renaming any of them here; a rename is a
  separate change with its own callers to update.
- **One deliberate ordering change is in scope and must be stated:** today the backlog resolves its
  anchor *before* the body guard while the defect path guards the body first, so the two report
  different errors for the same doubly-invalid input. The core picks one order (vocab → lexists → id →
  body → meta → index) and both registries then agree. Nothing is written in either order, so the
  zero-writes invariant is unaffected.
- **sec-L-10 is NOT fixed** (a repo-shipped `.git` file relocating `data_root`): that mechanism is how
  linked worktrees legitimately work, and the documented reason `data_root` exists at all. Hardening it
  risks breaking worktree support, which is a real supported use. Recorded in WI-8's resolution.

## 5. Open Questions / Observations (recorded, not fixed here)
- After R1 the two `insert_*` functions remain genuinely different (anchor-after vs sorted-section),
  which is correct — they implement different documented layouts. Only the choreography unifies.
- `frontmatter` is still a hand-rolled emitter/reader, not YAML. R9/R10 close the two divergences
  iteration 3 named; they do not make it a conforming parser.
- The remaining fd-leak nits (`cmd_file`'s lock fd opened before its `try`, `write_atomic`'s fd if
  `fdopen` itself raises) are cosmetic in short-lived processes and are left recorded.
