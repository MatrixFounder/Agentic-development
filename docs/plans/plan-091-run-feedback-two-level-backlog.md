# Development Plan — TASK 091: two-level work-item ledger for `run-feedback`

**Scope:** `known-issues-format` (format authority, generalized to two registries) +
`run-feedback` (engine, CLI, tests, docs) + framework docs + this repo's own backlog migration.
**Strategy:** Stub-First — contract & tests before behavior. Every step is independently
verifiable; the suite is green at every step boundary.

**Rollback:** the whole change is inside one git repo on branch `main` with a clean tree at start
(`git status` clean, HEAD `4281c96`). Rollback = `git checkout -- <path>` per step, or
`git reset --hard 4281c96` for the whole task. No file is deleted; the one migrated artifact
(`docs/BACKLOG.md`) is rewritten in place with its content moved, not dropped. No `.bak` copies:
they would be untracked litter next to a git checkout that already provides the snapshot.

---

## Requirements coverage (RTM)

| Req | Covered by step |
|---|---|
| R1 body verbatim in record file | Step 3, Step 4 (test), Step 6 |
| R2 `WI-<n>` allocation max+1 | Step 4 (test), Step 6 |
| R3 exit 4, zero writes | Step 4 (test), Step 6 |
| R4 rollback on index failure | Step 4 (test), Step 6 |
| R5 dry-run previews + tree identical | Step 4 (test), Step 6, Step 7 |
| R6 flat layout refuses flattening | Step 4 (test), Step 6 |
| R7 one contract, both templates gated | Step 1, Step 2, Step 8 |
| R8 old configs keep working | Step 5, Step 4 (test), Step 11 |
| R9 dogfood: migrate own BACKLOG.md | Step 10 |
| R10 suite green + new tests | Steps 4, 12 |

---

## Step 1 (R7) — `known-issues-format`: generalize the contract

- [ ] Restructure `SKILL.md` → v2.0: `## Format Contract` becomes
      **§Shared mechanics** (thin index, per-record file, hand-maintained lockstep, create-only,
      closed records keep their file, body verbatim) stated ONCE, then
      **§Registry parameters** — one table: index path · record dir · `type:` literal · ID scheme ·
      status vocab · rank key · grouping/insertion rule · index-line grammar · automated writer ·
      readers.
- [ ] Add the work-item frontmatter block + index-line grammar + "adding a work-item" recipe +
      create-if-absent pointer to the new backlog template.
- [ ] Extend `description:` so the skill triggers on backlog/work-item filing too (it is now the
      authority for both) — keep the **name** (`Universal-skills` and `onchain-analytics` symlink
      this directory by name; a rename breaks those links).
- [ ] Bump `version: 1.0 → 2.0`, extend `## Safety Boundaries` and `## Validation Evidence`.

**Verify:** `python3 System/scripts/validate_skills.py` green for the skill.

## Step 2 (R7) — `known-issues-format`: backlog seed template + drift gate

- [ ] New `assets/templates/backlog_md_template.md` — Purpose + Rules/Conventions preamble
      (work-item frontmatter, status vocab, effort vocab, index-line grammar, adding/closing
      recipe), the `<!-- feedback:discovered-issues -->` anchor, and a `_No work-items recorded
      yet._` placeholder with the same seed-comment discipline as the issues template.
- [ ] Rewrite `scripts/check_contract_sync.py` to a **registry-scoped** comparison: slice
      `SKILL.md` and each template on `<!-- contract:defects -->` / `<!-- contract:work-items -->`
      markers, then compare status vocab, rank vocab, frontmatter key set, index-line format per
      registry. Exit 0 in sync · 1 drift (names the registry + field) · 2 extraction error.

**Verify:** `python3 .agent/skills/known-issues-format/scripts/check_contract_sync.py` exits 0;
deliberately mutate one vocab word → exits 1 naming the registry; revert.

## Step 3 (R1) — engine stub: `ledger_backlog.file_work_item`

- [ ] Rewrite `feedback_lib/ledger_backlog.py` with the module docstring stating the discipline,
      and these functions:
      `format_index_line(...)` (pure) · `seed_backlog_text()` (from the Step-2 template) ·
      `insert_after_anchor(text, anchor, line)` (pure; raises on missing anchor) ·
      `file_work_item(config, item_id, slug, title, body, …, dry_run)` (record file + index line,
      lockstep with rollback, create-only) · `append_work_item(...)` retained for
      `backlog_layout: "flat"` **with the flatten-refusal guard**.
- [ ] Order of operations inside `file_work_item`: validate slug-free → resolve/seed index text →
      **locate the anchor** → write record → write index → on index failure unlink record. Anchor
      validated before any write (R3).
- [ ] Link in the index line is `os.path.relpath(record_path, index_path.parent)` in posix form, so
      a non-default `backlog_dir` still links correctly.

**Verify:** `python3 -c "import feedback_lib.ledger_backlog"` + the Step-4 tests fail RED for the
right reason before Step 6 wires the CLI.

## Step 4 (R1–R6, R8, R10) — tests FIRST (Red)

- [ ] Extend `scripts/tests/test_backlog_append.py`:
      `TestTwoLevelFiling` — record file created with contract frontmatter in key order; body
      byte-preserved; index line matches the canonical grammar and is short; ID = max+1 over the
      record dir (incl. a messy `WI-7X` neighbour); create-only conflict → exit 4; missing anchor →
      exit 4 **and no record file left**; index-write failure (read-only index) → record rolled
      back; dry-run leaves the tree byte-identical while previewing ID + record path + index line;
      seeding path when `BACKLOG.md` is absent.
      `TestFlatLayout` — multi-line / oversized body → exit 4 with remediation; genuine one-liner
      still appends after the anchor (legacy behavior preserved).
- [ ] Extend `tests/_fixtures.py` with a two-level backlog fixture + a record writer
      (`write_work_item`), mirroring `write_issue`.
- [ ] Extend `tests/test_dry_run.py` with the work-item tree-hash case, and `tests/test_config.py`
      with the new-key defaults + `backlog_layout` validation + **old-config compatibility**
      (`{backlog_path, backlog_anchor}` only → two-level defaults, no unknown-key warning).

**Verify:** suite RED on exactly the new assertions, green elsewhere.

## Step 5 (R8) — config surface

- [ ] `config.py`: `DEFAULTS` += `backlog_dir: "docs/backlog"`, `backlog_prefix: "WI"`,
      `backlog_layout: "index+files"`; properties `backlog_dir` / `backlog_prefix` /
      `backlog_layout` (unknown layout → `EXIT_CONFIG` with the allowed values); `CONFIG_VERSION`
      unchanged at `1`.
- [ ] `assets/templates/feedback_config_template.json` += the three keys with comments-by-example
      values.

**Verify:** `test_config.py` green; a v1 config with only the old keys loads with no warning.

## Step 6 (R1–R6) — CLI wiring (Green)

- [ ] `run_feedback.py` work-item branch: allocate `WI-<n>` via `ids_mod` over `cfg.backlog_dir`
      (honor `--slug`), collect extension keys (`component`, `fingerprint`, `evidence_paths`,
      `finding_ref` — **no `auto_fixable`**: the heal harness selects defects only), derive
      `source` from the finding's run context unless `--source` is given, call `file_work_item`,
      and report ID + record path + index line. `filed_as.id` becomes `WI-<n>` (was `None`).
- [ ] Add `--source` to the `file` parser; keep `--effort` / `--value`.
- [ ] `doctor`: report `backlog_layout`, `backlog_dir` presence/writability, and keep the anchor
      check; remediation lines for each.
- [ ] `init`: todo text describes seating the anchor **and** the record dir for the two-level
      layout.

**Verify:** full suite green: `cd .agent/skills/run-feedback/scripts && python3 -m unittest
discover -s tests`; then `bash tests/test_e2e.sh`.

## Step 7 (R5) — end-to-end dogfood in a scratch repo

- [ ] In a mktemp git repo: `init` → seat anchor → `collect` → `triage` → `file --as work-item
      --dry-run` → real `file` → assert record file + one-line index entry + journal entry.
- [ ] Repeat with `backlog_layout: "flat"` and a table-bearing body → assert exit 4, not a
      flattened bullet.

**Verify:** transcript of both runs pasted into the run report.

## Step 8 (R7) — `run-feedback` skill documentation

- [ ] `SKILL.md` → v1.4: §1 red flag "I'll let the script inline the body into the backlog index"
      (replacing nothing — added); §2 capability wording (work-items now lockstep too); §4 config
      keys; §5 allowed scope += `backlog_dir`; §7 triage step 5 extended: a work-item body is
      authored in a REAL file from the new template, same discipline as a defect;
      §9 DO/DON'T rows; §11 resources.
- [ ] New `assets/templates/work_item_body_template.md` (Signal / Why it matters / Options /
      Recommendation / Related) — the work-item counterpart of `issue_body_template.md`.
- [ ] `references/cli_reference.md`: rewrite the work-item paragraph (ID allocation, record path,
      index line, layouts, exit 4 cases).

**Verify:** `python3 System/scripts/validate_skills.py` green for both skills.

## Step 9 (R7) — framework docs

- [ ] `System/Docs/QUALITY_FEEDBACK_LOOP.md`: ASCII pipeline (backlog now index+files), the `file`
      row in the subcommand table, the Setup section (backlog_dir/layout), and a short
      "why two ledgers" note recording the decision from TASK 091 §1.
- [ ] `System/Docs/SKILLS.md`: rows for `known-issues-format` (now both registries) and
      `run-feedback` (work-item lockstep).
- [ ] `.agent/skills/artifact-management/SKILL.md` → v1.4: add `BACKLOG.md` as a LIVING
      hand-maintained thin index with format delegated to `known-issues-format` +
      create-if-absent from the new template (mirrors the `KNOWN_ISSUES.md` bullet); extend the
      skill `description:` accordingly.
- [ ] `CLAUDE.md`: the `docs/KNOWN_ISSUES.md` pipeline line gets its backlog sibling named, so the
      Analysis phase knows which ledger holds what.

**Verify:** `grep` for stale claims ("appends the whole body", "one bullet") across
`System/Docs/`, both skills, and `CLAUDE.md` → no hits.

## Step 10 (R9) — migrate this repo's own backlog (dogfood)

- [ ] `docs/BACKLOG.md`: rewrite as a thin index from the new template's preamble, keeping the
      anchor; move the existing ~900-char bullet into
      `docs/backlog/wi-1-skill-spec-validator-unit-tests.md` (`opened_at: 2026-07-20`, from the
      bullet's own date; `source: TASK 090`) with its text **preserved verbatim**; leave one
      canonical index line.

**Verify:** `git diff --stat` shows content moved, not lost; the record file's body contains every
clause of the old bullet (word-diff check).

## Step 11 (R8) — downstream: close WI-23 truthfully

- [ ] Verify by `git diff` in THIS repo what actually landed (their ledger's own rule: report what
      remained in the files, not what was proposed).
- [ ] In `onchain-analytics`: flip `docs/backlog/wi-23-…md` to `status: done` +
      `resolved_at: 2026-07-29` + `resolved_by: framework edit (agentic-development)` with a
      resolution blockquote naming which of the three options landed; move its index line to
      `## Закрытые`; and replace the now-false `⚠️ Про run_feedback.py file --as work-item`
      warning block in `docs/BACKLOG.md` with the current behavior.
- [ ] No config edit needed there — the new keys default to that repo's existing layout (assert by
      running `doctor` against it).

**Verify:** `doctor` in `onchain-analytics` reports `ready: true`; a `--dry-run` work-item filing
there previews a record path under `docs/backlog/` and a one-line index entry.

## Step 12 (R10) — final verification & review gate

- [ ] `cd .agent/skills/run-feedback/scripts && python3 -m unittest discover -s tests` — green.
- [ ] `bash .agent/skills/run-feedback/scripts/tests/test_e2e.sh` — green.
- [ ] `python3 .agent/skills/known-issues-format/scripts/check_contract_sync.py` — exit 0.
- [ ] `python3 System/scripts/validate_skills.py` — no new findings.
- [ ] Code-review pass (`code-review-checklist`) + security pass on the new write surface
      (`backlog_dir` path handling, slug normalization, no path escape).
- [ ] Session state update at each phase boundary; final one-line run report.
