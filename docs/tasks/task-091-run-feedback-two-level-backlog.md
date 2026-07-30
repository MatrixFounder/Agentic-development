# Technical Specification: two-level work-item ledger for `run-feedback`

### 0. Meta Information
- **Task ID:** 091
- **Slug:** run-feedback-two-level-backlog

## 1. General Description

`run-feedback` has two filing paths and they have diverged. The **defect** path
(`ledger_issues.py`) writes a per-record file **plus** a thin index line, in lockstep, with
rollback. The **work-item** path (`ledger_backlog.py`) only ever does
`lines.insert(anchor_idx + 1, bullet)` where the bullet is
`" ".join(str(body).split())` — the record body is **collapsed into one line and inlined into the
index**. No record file is ever created.

Filed as **WI-23** in `onchain-analytics`
(`docs/backlog/wi-23-run-feedback-work-item-path-flattens-two-level-backlogs.md`), observed in the
TASK-009 retro: three work-items had to be filed by hand; `--dry-run` previewed a ~1 800-character
bullet with a table folded into a single line. That project's `docs/BACKLOG.md` documents the
opposite convention *and why*: one entry once reached **7 849 characters in a single bullet** and
"could not be read, diffed, or closed in parts". The script produces exactly the shape the
convention exists to prevent. This framework's **own** `docs/BACKLOG.md` (11 lines, one ~900-char
bullet) is the second live instance of the same defect.

Generalized statement of the defect, free of any stack: **if the target registry is an INDEX over
record files, an appender that writes only the index line is not a filing mechanism for it.** It
either loses the body or makes the index unreadable, and in both cases silently.

Two decisions taken with the framework owner before this spec (both confirmed):

1. **Two ledgers stay two ledgers.** Work-items are NOT merged into `docs/KNOWN_ISSUES.md`.
   Rationale: `KNOWN_ISSUES.md` is read by the Analysis phase of every pipeline run and by
   `/heal-issues`; folding enhancement signal into it dilutes the anti-regression channel. The
   status vocabularies genuinely differ (`open/fixed/documented/by-design/mitigated/wontfix` +
   `severity`/`category` vs `open/done/dropped` + `effort`/`value`/`source`), and
   `list_issues()` already filters on `type == "known-issue"`, so co-located work-items would be
   invisible to every reader — the "single registry" gain is zero while the index becomes mixed.
   The skill's whole triage contract is *defect vs work-item*; one file makes that distinction
   unobservable.
2. **One format contract, not two.** The real duplicate is the **mechanics** (thin index +
   per-record file + hand-maintained lockstep + create-only). `known-issues-format` is generalized
   to state those mechanics ONCE and parameterize them per registry. No new format skill: two
   near-identical contracts are exactly the drift that produced this defect.

## 2. List of Use Cases

### UC-01: file a work-item into a two-level backlog

**Actors:** Orchestrator / any agent running the Retro or `/run-feedback`; `run_feedback.py`.
**Preconditions:** a triaged finding classified `work-item`; `backlog_path` configured;
`backlog_anchor` present in that file.

**Main Scenario:**
1. Agent authors the body in a real file (`--body-file`), as for a defect.
2. `file --as work-item --title T --body-file PATH --dry-run` previews the allocated ID
   (`WI-<n>`), the record path, and the exact index line — zero writes.
3. Agent runs the same command without `--dry-run`.
4. Engine allocates `WI-<n>` = max existing + 1 over `backlog_dir/*.md` frontmatter `id:`.
5. Engine writes `docs/backlog/<slug>.md`: contract frontmatter (`id`, `type: work-item`,
   `status: open`, `opened_at`, `slug`, optional `effort`/`value`/`source`, then automation
   extension keys) + `# <ID> — <title>` + the body **verbatim**.
6. Engine inserts ONE index line directly after `backlog_anchor` (newest first).
7. Finding is consumed to `filed/` and journaled with `filed_as.id = WI-<n>`.

**Alternative Scenarios:**

**A1: anchor missing (at step 6)**
1. Exit 4 `FilingConflict` with remediation, and **no record file is left behind** — the anchor is
   validated BEFORE the record is written.

**A2: index write fails after the record was written (at step 6)**
1. Record file is unlinked; no half-state. (Same rollback discipline as `file_defect`.)

**A3: slug already exists (at step 5)**
1. Exit 4 `FilingConflict` — create-only, never overwrite a live record.

**A4: `backlog_path` configured but the file does not exist (at step 6)**
1. Engine seeds it from `known-issues-format`'s `backlog_md_template.md` (rules preamble + anchor),
   then inserts. Symmetric with how a missing `KNOWN_ISSUES.md` is seeded.

**A5: repo genuinely wants a single-file backlog (`backlog_layout: "flat"`)**
1. Legacy one-bullet append is used, **but** a body that does not fit one line (multi-line, or over
   the configured cap) is **refused** with exit 4 instead of being silently flattened.

**Postconditions:** `docs/backlog/<slug>.md` exists with the body intact; `docs/BACKLOG.md` grew by
exactly one line; both or neither.

**Acceptance Criteria:**
- ✅ **R1** A filed work-item produces a record file whose body is byte-identical to `--body-file`
  content (modulo one trailing newline), and an index line of ≤ ~200 chars.
- ✅ **R2** `WI-<n>` allocation is `max + 1` over the record dir, tolerant of messy IDs, never
  gap-filling.
- ✅ **R3** Missing anchor / existing slug → exit 4, zero writes anywhere.
- ✅ **R4** Failed index write → record file rolled back.
- ✅ **R5** `--dry-run` previews ID + record path + index line and leaves the repo tree
  byte-identical.
- ✅ **R6** `backlog_layout: "flat"` refuses a body that would be flattened (never silently
  collapses it) — option 2 of WI-23 preserved as the guard on the legacy path.
- ✅ **R7** `known-issues-format` states the shared thin-index mechanics once and parameterizes
  both registries; `check_contract_sync.py` gates BOTH seed templates against it.
- ✅ **R8** A pre-existing config (`{backlog_path, backlog_anchor}` only, as in `onchain-analytics`
  and this repo) keeps working unchanged and lands on the two-level layout by default — no
  `config.v` bump, no unknown-key warnings.
- ✅ **R9** This repo's own `docs/BACKLOG.md` is migrated to the two-level layout (index + one
  record file), i.e. the framework dogfoods the contract it ships.
- ✅ **R10** Existing suite stays green; new tests cover R1–R6.

### UC-02: read the format contract when maintaining a ledger by hand

**Actors:** any agent or human adding/closing a record.
**Preconditions:** none.
**Main Scenario:**
1. Reader loads `known-issues-format`.
2. Shared mechanics are stated once; a per-registry table gives index path, record dir, `type:`
   literal, ID scheme, status vocab, rank key, grouping rule, index-line grammar, writers, readers.
3. Reader follows the "adding a record" recipe for the registry they are in.

**Acceptance Criteria:**
- ✅ Neither registry's rules are stated twice in different words.
- ✅ `python3 scripts/check_contract_sync.py` exits 0 and fails on drift in either template.

## 3. Non-functional Requirements
- **Performance:** irrelevant at this scale (tens of records); allocation is one frontmatter scan.
- **Security:** no new write surface — `file` still writes only under `issues_dir`, `index_path`,
  `backlog_path`, and now `backlog_dir` (all repo-visible, all create-only). No network.
- **Compatibility:** `config.v` stays `1`. New keys (`backlog_dir`, `backlog_prefix`,
  `backlog_layout`) are additive with defaults; configs written before this task load unchanged.
  Downstream repos consume both skills by **symlink** (`Universal-skills`, `onchain-analytics`), so
  the edit lands there on merge — no copy-sync step, and therefore no divergent copies to keep.

## 4. Constraints and Assumptions
- Insertion for the backlog stays **anchor-based, newest-first** (not `## <category>` + ID order as
  for issues): the backlog is human-ranked, and the anchor is what `file`/`doctor` are wired to.
- Closed records are moved to a `## Closed` group **by hand** — the engine remains create-only and
  never flips a status (same boundary as the issues ledger; `/heal-issues` owns defects only).
- Canonical index-line grammar mirrors the issues grammar with `severity` → `effort`. The live
  `onchain-analytics` ledger uses a local variant (`— opened <date>, effort \`S\`: <gist>`);
  readers tolerate local variants, new automated writes emit the canonical one.
- `docs/BACKLOG.md` is a per-project artifact; `artifact-management` gains it as a living Global
  Artifact with format delegated to `known-issues-format`, mirroring `KNOWN_ISSUES.md`.
- Assumption: no consumer parses the current one-bullet format. Verified: nothing outside
  `ledger_backlog.py` + its tests reads `BACKLOG.md`; `/heal-issues` reads the issues ledger only.

## 5. Open Questions
- None blocking. (Both design forks were resolved by the owner before this spec — §1.)
