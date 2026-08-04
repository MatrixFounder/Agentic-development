# Task 096.2 — Scaffold `artifact-formalizer`, define the schema, stub the scanner


> [!IMPORTANT]
> **Superseded in part, 2026-08-04 — recorded, not rewritten.**
>
> This file states the plan as approved. Execution diverged, and the divergence is listed here so
> the plan of record stays readable as history rather than being silently corrected.
>
> | This file says | What shipped | Recorded in |
> | :--- | :--- | :--- |
> | exit 2 only for a broken rule file or unreadable input | exit 2 also for a dead detector or inconsistent merged thresholds; exit 3 for a usage error | SKILL.md §3 |
>
> Every other statement in this file still holds. The mechanism, the measurements and the current
> contract live in `.agent/skills/artifact-formalizer/` — SKILL.md §5 for detector coverage,
> `references/measurement-baseline.md` §10 for why each divergence happened.

**Requirements:** R6, R7, R10 · **Stage:** 2 of 6 · **Dependencies:** 096.1

<!-- contract:goal -->

## Goal

Create the skill through the mandatory generator, fix the rule-file schema, and land a scanner
whose CLI is complete and whose logic is absent. The selftest battery is written here in full and
observed failing.

<!-- contract:changes -->

## Changes

### Scaffold (mandatory command, manual creation prohibited by CLAUDE.md)

```sh
python3 .agent/skills/skill-creator/scripts/init_skill.py artifact-formalizer --tier 2
```

### Schema `register-rules/v1`

```json
{"schema": "register-rules/v1",
 "thresholds": {"sentence_max_words": 35, "cell_max_chars": 120},
 "languages": {"<lang>": {"categories": [
   {"name": "...", "entries": [
     {"marker": "...", "pattern": "regex", "guidance": "...",
      "flags": "i", "severity": "warn|info", "note": "..."}]}]}}}
```

Two deliberate differences from the reference skill's `jargon-dictionary/v1`:

- `replacement` becomes `guidance`. A register defect has no single correct substitute; the entry
  tells the author what to do, and the author writes the sentence.
- `thresholds` is a root key. Structural bounds are data too, so tuning the sentence bound never
  edits code (R7).

### Files

- `scripts/scan_register.py` — full CLI, `validate_rules()` implemented, all detection returning
  empty. Structural checks and masking raise nothing and find nothing.
- `scripts/selftest_scan.py` — complete battery (see Test cases), expected **failing**.
- `data/register-en.json`, `data/register-ru.json` — seeded from the TASK §1.1 marker lists.
- `SKILL.md` — frontmatter, purpose, script contract table, execution mode.

### CLI contract

| Command | Purpose | Exit |
| :--- | :--- | :--- |
| `scan_register.py FILE… [--rules R.json…] [--lang auto\|<lang>] [--json]` | validate rules → scan | 0 always on findings; 2 on broken rules or unreadable input |
| `scan_register.py --list [LANG]` | render the rule set as a table | 0 / 2 |
| `selftest_scan.py` | acceptance battery | 0 / 1 |

<!-- contract:tests -->

## Test cases

Written here, failing here, passing by 096.4.

- **TC-SCHEMA-01…06** — non-object root; wrong `schema` value; empty `languages`; entry missing
  `marker`/`pattern`/`guidance`; pattern that does not compile; unknown entry key; bad `severity`.
  Each exits 2 and names the faulty path.
- **TC-MASK-01…04** — a marker inside a code span, a fenced block, a link target, and an HTML
  comment is **not** reported. One control: the same marker in plain prose **is** reported.
- **TC-STRUCT-01…03** — sentence over the threshold; table cell over `cell_max_chars`; emoji used
  as a severity marker.
- **TC-LEX-01…02** — a `warn` marker and an `info` marker, each reported at its own severity.
- **TC-LANG-01…03** — Cyrillic file resolves `ru`; Latin resolves `en`; a language with no rule
  file runs structural checks, reports zero lexical hits, and says so on stderr.
- **TC-EXIT-01** — a file full of findings exits **0** (R8).
- **TC-EXIT-02** — a malformed rule file exits 2 and does not scan.
- **TC-DATA-01** — a fixture rule file adds a new marker and it is reported, with **no** edit to
  `scan_register.py` (R7).

<!-- contract:acceptance -->

## Acceptance criteria

- [ ] Skill created by `init_skill.py`, not by hand
- [ ] `python3 -c "import scan_register"` succeeds
- [ ] Selftest **fails**, listing failing case names — not an import or syntax error
- [ ] `validate_rules()` is real: the six schema cases already pass at this stage
- [ ] Both data files load and declare `thresholds.sentence_max_words = 35` from 096.1

## Notes

**Why the schema checks pass at the stub stage.** Validation is the part that must never be a stub:
a scanner that silently accepts a broken rule file reports zero findings and looks clean. The
reference skill made the same choice, and it is the one behaviour worth copying verbatim.
