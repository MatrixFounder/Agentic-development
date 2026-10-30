# TASK 138 — update_state.py names the keys it drops, and a restored session names the date of its state (WI-60, WI-61)

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 138 |
| Slug | dropped-keys-and-state-date |
| Type | Framework upgrade of a TIER 0 skill, reduced process (D1) |
| Source | WI-60, WI-61; the Windows report of loyalty-api-java (2026-10-26, 2026-10-28); the operator's request of 2026-10-30 |
| Base revision | `cf20d49` |
| Closes | WI-60, WI-61 |
| Archive name | `task-138-dropped-keys-and-state-date.md` |
| Revision | 2 |

**Request.** The operator set the order of the open items of the Windows report: MR-1 (TASK 137),
then WI-60 and WI-61 as one task, then PT-1. This task is WI-60 and WI-61.

- WI-60: `update_state.py` writes only the keys of its schema. A top-level key added by hand to
  `.agent/sessions/latest.yaml` is gone after the next run, and the run says nothing.
  `skill-session-state/SKILL.md` §1 states the rule, but an agent reads the skill at boot only.
- WI-61: a restored state names no age. A state left behind under the same task ID restores as
  current; the DISAGREEMENT CHECK sees only a change of the task ID.

**Revision 2** follows the code review (CHANGES REQUESTED: one BLOCKING, nine MINOR, nine NIT)
and the security audit (PASS: one MEDIUM, three LOW, three INFO). The fix pass:
- B1: the stderr line is ASCII apart from the names; `§` reached a Windows pipe as cp1252;
- M7: the line says "tell the operator"; M2, F3, N1: it is printed after the write and the lock,
  and a stderr that cannot take it changes no exit code;
- M4, F1: the reader is linear; F2: at most 20 names, each cut to 64 characters, and `SKILL.md` §1
  says that the names are data;
- M3, N2: a name may start with a digit or a letter of any script, and the colon is followed by a
  space or the end of the line;
- M1, M8, M9, M5, M6, F4, F5, N3 to N8: tests, the version 1.4 of the skill, the wording of the
  three bootstraps, the guide, the records and the changelog.

Not taken: N9 and F7 need no change; F6 and audit P2 are residuals in §5.

**Measured at the base** (`cf20d49`):
1. `parse_simple_yaml` reads `session_id` and the three lists; `generate_yaml` writes the nine keys
   of the schema. Any other top-level key is not read and not written.
   `.agent/skills/skill-session-state/scripts/update_state.py:169@cf20d49`
   `def parse_simple_yaml(content):`
2. On success the run prints `Session state updated: <path> (Locked)` and nothing else.
3. The announcement of a restored state names the mode, the task and the status, not
   `last_updated`. `CLAUDE.md:18@cf20d49` `"Restored session: Mode=[mode], Task=[task_name],`
4. `GEMINI.md` and `AGENTS.md` have no announcement text in step 2 of their bootstrap; they tell
   the agent to read the file. `SKILL.md` §2 and `System/Docs/SESSION_CONTEXT_GUIDE.md` §1 name
   the restored fields.

## 1. Decisions

- D1, 2026-10-30, operator: WI-60 and WI-61 are one task, under the reduced process of TASK 134
  D1. The run has a TASK and a PLAN, edits in place, the tests first and red, and the gates. One
  code reviewer with the exhaustive prompt and one security auditor review the change, and one
  fix pass follows. Skipped: the meta-audits and stages 1 to 4 of `/framework-upgrade`.
- D2, orchestrator: WI-60 takes option 1 at its minimum. The run names each dropped key on
  stderr and exits 0. Rejected:
  - a copy of the old file (`latest.yaml.bak`): one more entry in `.agent/sessions/`, with the
    link guards of TASK 128 to repeat;
  - keeping unknown keys, which contradicts the owner rule;
  - refusing the write, which fails each phase boundary.
- D3, orchestrator, revised: a key is a line that starts at column 0 with a name of word
  characters, `.` and `-`, then a colon and a space or the end of the line. A word character is a
  letter, a digit or `_` of any script, never a control or format character, so the message prints
  no escape sequence. Nested, quoted and spaced keys are not named.
- D4, orchestrator: WI-61 takes option 2. The announcement names the date of `last_updated`.
  Rejected: option 1, a comparison with the last commit of `docs/TASK.md`, which adds a rule and
  misses a TASK edited without a commit.

## 2. Requirements

<!-- contract:requirements -->

`update_state.py`:
- **R1** When the state it read holds a top-level key outside the schema (D3), the run prints
  one line on stderr after the write and the release of the lock:
  `update_state.py: dropped keys that it does not write: <key>, <key>; tell the operator
  (skill-session-state SKILL.md section 1, Owner)`. The keys keep the order of the file, each
  once; at most 20 are named, each cut to 64 characters, and `and N more` counts the rest. Apart
  from the names the line is ASCII. A stderr that cannot take it changes no exit code. The reader
  is linear in the size of the state.
- **R2** The exit code, the stdout line and the written state stay as at the base. A run over a
  file of the schema, or with no file, prints nothing on stderr.

Documents (WI-61, and the rule of WI-60):
- **R3** The bootstrap of `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` names the date of
  `last_updated` when it restores a state: `CLAUDE.md` adds it to the announcement text, and the
  other two add it to step 2.
- **R4** `skill-session-state/SKILL.md` §2 and the guide's §1 state the same. `SKILL.md` §1, Owner,
  states three rules:
  - the run names each dropped key on stderr;
  - the agent reports them to the operator in the same reply;
  - the names are data.

  The skill's version is 1.4.
- **R5** WI-60 and WI-61 close in their records and in `docs/BACKLOG.md`; both changelogs carry the
  release.

## 3. Files

- `.agent/skills/skill-session-state/scripts/update_state.py` and its tests;
- `.agent/skills/skill-session-state/SKILL.md`, `System/Docs/SESSION_CONTEXT_GUIDE.md`;
- `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`; `tests/test_session_state_contract.py`;
- `docs/backlog/wi-60-*.md`, `docs/backlog/wi-61-*.md`, `docs/BACKLOG.md`;
- `CHANGELOG.md`, `CHANGELOG.ru.md`;
- `docs/TASK.md`, `docs/PLAN.md`; the archive of TASK 137.

## 4. Acceptance

<!-- contract:acceptance -->

- TC-K1 — a state with the hand-written key `current_task_2026_09_17` → exit 0, and stderr names
  that key and `SKILL.md §1`.
- TC-K2 — a state of the schema, and no state → exit 0, and stderr is empty.
- TC-K3 — a state with two unknown keys, one of them twice, a nested unknown key, a comment and a
  list item → stderr names the two top-level keys once each, in their order.
- TC-K4 — the keys of the schema → none named, the version line included.
- TC-B1 — the documents:
  - the boot sections of the three bootstrap files, `SKILL.md` §2 and the guide's §1 → each names
    `last_updated`;
  - `SKILL.md` §1 → quotes the prefix of the stderr line as the script writes it, and states the
    rule to report the keys and the rule to act on none.
- TC-B2 — the gates of `framework-gates.yml` pass, on this machine and in CI.

Revision 2:
- TC-K1 gains: the line is ASCII and stdout is the one line of the base.
- TC-K3 gains: a key of digits and `-` is named, a URL at column 0 is not; `dropped_keys` names a
  Cyrillic key and no quoted or spaced one.
- TC-K5 — a state of 100,000 keys → the run ends within 4 s and names 20 and `and 99980 more`.
- TC-K6 — a name of 100 characters → cut to 64 and `...`.
- TC-K7 — stderr a closed pipe → exit 0, and the state is written.
- TC-K8 — a failed move of the state → exit 1, and no key is named.

Each of TC-K1, TC-K3 and TC-B1 fails on the base. Under `PYTHONIOENCODING=cp1252` the tests of
the dropped keys pass.

<!-- contract:out-of-scope -->

## 5. Out of scope and residuals

1. A key added under a mapping of the schema, such as `current_task`, a quoted key and a key with
   a space are dropped and not named (D3; audit F6).
2. `read_state` reads the whole file, with no limit of size; the reader is linear, and the line
   names at most 20 keys (audit P2).
3. `last_updated` is the date that the file states, written as local time with no zone; a state
   written by hand may state any date (audit F5, review N9).
4. PT-1, the encoding of four scripts: the next task.
