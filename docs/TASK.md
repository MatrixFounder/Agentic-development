# TASK 142 — [LIGHT] The remaining drifted copies match canonical, and Universal-skills checks its copies

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 142 |
| Slug | drifted-skill-copies |
| Type | Light Mode with an exception (D1, D2) |
| Source | the operator's requests of 2026-11-07 |
| Base revision | `d685fb040c11d73a6e9410c96a833be01e59d1f6` |
| Universal-skills base | `82001cf` |
| Archive name | `task-142-drifted-skill-copies.md` |
| Revision | 3 |

**Request.** After TASK 141 the operator asked to bring the other drifted copies in order. Six
skills of `Universal-skills/skills/` are full copies of canonical skills. Each copy must work
outside this framework.

**Findings of 2026-11-07** (`diff -rq -x .DS_Store -x __pycache__` of each canonical skill
against its copy):

1. `hooks-creator`: the copy is ahead. Copy v1.1 has §3 Execution Mode, §4 Safety Boundaries,
   pass criteria and a worked example in Phase 3; canonical v1.0 has none of them. The Security
   Gate example stands in both, at another place.
2. `skill-enhancer`: the copy is ahead. Its `analyze_gaps.py` exempts a bracket span with no
   letter, such as `[0.028, 0.195]`, from the placeholder rule, and `test_rule_scoping.py` has
   two tests for it. Canonical has neither.
3. `brainstorming`: canonical is ahead. Canonical v3.2 picks the form of a figure through
   `mermaid-authoring-guidelines` and redraws the figure of `examples/demo_complex.md`. That
   skill is not published in `Universal-skills`. Without it, canonical v3.2 allows a list or a
   table only, so a standalone copy loses the Mermaid rule of v3.1.
4. No check compares a copy with canonical. The drift was found by a manual `diff`.

**Revision 2** follows the code review of cycle 1: CHANGES REQUESTED, with one MAJOR, eight
MINOR and twelve NIT findings, none BLOCKING. The fix pass:
- the MAJOR: `Universal-skills/AGENTS.md` carries the rule too (R7);
- the script checks `skills/` before the skip, reports a symlink as drift and an unreadable
  file or directory with exit 2 (R5); the test proves each branch and the `__pycache__` entry;
- `hooks-creator` Phase 3 checks for exactly one JSON object with `jq -s`;
- the fallback of `brainstorming` keeps the two Mermaid exceptions of the chat case, and names
  the absent skill once per conversation (R3);
- rule 4 of R7 allows a framework skill named with its fallback and lists the open exceptions;
  `docs/CONTRIBUTING.md` points to the rule;
- `tests/test_skill_refs.py` also pins `hooks-creator` (R9 of TASK 141).

**Revision 3** follows cycle 2: APPROVED, with four MINOR and eighteen NIT findings. The fixes
land in place, with no further review round (D8):
- rule 4 lists `vdd-sarcastic` among the open exceptions (R7);
- the script exits 2 on a closed stdout, with a quiet stderr. It also exits 2 on a directory
  it cannot list, and on a sibling link to a tree without `.agent/skills` (R5);
- it reports as drift a copy that is a symlink, a special file such as a FIFO, and a lost
  executable bit (R5);
- `hooks-creator` Phase 3 writes to `mktemp` files and applies the `jq` check to exit-0 runs;
  `examples/security_gate.sh` checks for `jq` as Phase 2 requires.

## 1. Decisions

- D1, 2026-11-07, operator: `/light`, with the exception of D2. The run has the edits, the
  tests, one code reviewer in at most two cycles, and the security sanity check.
- D2, 2026-11-07, operator: the check adds two files to `Universal-skills`:
  `scripts/check_framework_copies.py` and `tests/test_framework_copies.py`.
  **Why.** The condition "no new files" of `light-mode` escalates such a task; the operator kept
  Light Mode. The script reads files and writes only its report.
- D3, 2026-11-07, operator: `brainstorming` keeps Mermaid when `mermaid-authoring-guidelines` is
  absent: Mermaid in a Markdown file whose renderer shows it, as in v3.1. A chat reply keeps the
  rule of v3.2 (R3). Rejected: canonical v3.2 as it is — the standalone copy
  loses Mermaid; publishing `mermaid-authoring-guidelines` — a separate, large task.
- D4, 2026-11-07, operator: the check runs locally in `Universal-skills`. Without the sibling
  repository it reports `SKIPPED` and exits 0.
- D5, orchestrator: the list of copies is derived. A directory of `skills/` is a copy when
  `.agentic-development/.agent/skills/<name>` is a directory. A new copy needs no edit of the
  script.
- D6, orchestrator: the copies of `hooks-creator` and `skill-enhancer` move into canonical as
  they are. Canonical has no edit that the copies lack. The review fixes of `hooks-creator` then
  land in canonical, and the copy takes them back.
- D7, orchestrator: the framework release is v3.56.2. The commits wait for the operator.
- D8, orchestrator, under the operator's standing rule of 2026-10-16: the MINOR and NIT
  findings of the approved cycle 2 are fixed in place, with the tests and the mutants re-run and
  no review round 3. NIT-14 stays: residual 5.

## 2. Requirements

- **R1** Canonical `hooks-creator/SKILL.md` equals the copy (v1.1).
- **R2** Canonical `skill-enhancer/scripts/analyze_gaps.py` and
  `scripts/tests/test_rule_scoping.py` equal the copy.
- **R3** Canonical `brainstorming/SKILL.md` (v3.2 → v3.3): without `mermaid-authoring-guidelines`,
  - a figure in a Markdown file is Mermaid where the reader's renderer shows it, otherwise ASCII
    or a list;
  - a figure in a chat or a terminal is a list, a table or ASCII. A Mermaid fence goes into a
    reply only when the user asks for Mermaid source, or inside a document the user saves;
  - the skill tells the user once per conversation that the skill is absent.
- **R4** The copies of `brainstorming`, `hooks-creator` and `skill-enhancer` are byte-identical
  to canonical, with `.DS_Store` and `__pycache__` excluded.
- **R5** `Universal-skills/scripts/check_framework_copies.py`:
  - lists each copy of D5 as `ok` or `DRIFT`, and under `DRIFT` each entry as `differs`,
    `mode differs`, `only in canonical`, `only in copy`, `symlink in …`, `special in …`, or a
    copy that is itself a symlink;
  - compares bytes; it skips `.DS_Store`, `__pycache__`, `.venv`, `node_modules`,
    `.pytest_cache`, `.mypy_cache`, `.ruff_cache` and `*.pyc`;
  - follows no symlink inside a skill and reads no special file;
  - exit 0: every copy matches, or `SKIPPED` when `.agentic-development` does not resolve;
  - exit 1: drift;
  - exit 2, which takes precedence over 1:
    - `skills/` or a canonical directory is absent or cannot be listed;
    - no copy is found, or an entry is `unreadable`;
    - stdout closes early;
  - the check of `skills/` comes before the skip;
  - takes its human channel per `CLI I/O encoding` of `Universal-skills/CLAUDE.md`.
- **R6** `Universal-skills/tests/test_framework_copies.py` covers each branch of R5 on fixtures,
  and runs the script on the repository itself. The `test harness` job of
  `.github/workflows/office-skills.yml` runs it.
- **R7** `Universal-skills/CLAUDE.md`, `GEMINI.md` and `AGENTS.md` state the rule: a copy of a
  framework skill is edited in canonical, copied, and checked with the script. A copy may name
  a framework skill together with what to do without it; `skill-creator`, `skill-enhancer` and
  `vdd-sarcastic` are the open exceptions. `docs/CONTRIBUTING.md` §2 points to the rule.
- **R8** `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md` and `README.ru.md` carry v3.56.2. The
  commit also carries WI-63 of the TASK 141 retro.
- **R9** `tests/test_skill_refs.py::TestStandaloneBundle` also holds `hooks-creator`.

## 3. Files

- agentic-development: `.agent/skills/hooks-creator/SKILL.md`, `examples/security_gate.sh`;
  `.agent/skills/skill-enhancer/scripts/analyze_gaps.py`, `scripts/tests/test_rule_scoping.py`;
  `.agent/skills/brainstorming/SKILL.md`; `CHANGELOG.md`, `CHANGELOG.ru.md`, `README.md`,
  `README.ru.md`; `tests/test_skill_refs.py`; `docs/TASK.md`; the archive of TASK 141;
  `docs/BACKLOG.md` and the record of WI-63.
- Universal-skills: `skills/brainstorming/SKILL.md`, `examples/demo_complex.md`;
  `skills/hooks-creator/SKILL.md`, `examples/security_gate.sh`;
  `scripts/check_framework_copies.py`; `tests/test_framework_copies.py`;
  `.github/workflows/office-skills.yml`; `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`;
  `docs/CONTRIBUTING.md`.

<!-- contract:acceptance -->

## 4. Acceptance

- TC-1 — `python3 scripts/check_framework_copies.py` in `Universal-skills` → exit 0, six copies
  `ok`.
- TC-2 — `python3 tests/test_framework_copies.py` → pass, also under `PYTHONIOENCODING=cp1252`.
  It fails when the script drops a branch of R5.
- TC-3 — the tests of canonical `skill-enhancer` and `tests/test_inline_efficiency.py` → pass.
- TC-4 — `validate_skill.py` on the three skills, in both repositories → pass;
  `analyze_gaps.py` → no blocking gap.
- TC-5 — `python3 tests/run_tests.py`, `validate_skills.py`, `check_prompt_references.py` and
  `smoke_workflows.py` in agentic-development → pass.
- TC-6 — `python3 tests/test_shared_gate_logic.py`, `test_file_codec.py` and
  `test_subprocess_decode.py` in `Universal-skills` → pass.
- TC-7 — `scan_register.py` on the edited text → no warn-level finding that this run adds.

## 5. Out of scope and residuals

1. `skill-creator` and `skill-enhancer` name framework paths such as `.agent/` and
   `docs/issues/`. Whether those two copies work standalone is a separate question.
2. `vdd-sarcastic` keeps its framework references (TASK 141, residual 1).
3. The check does not run in CI on real copies: CI has no sibling repository (D4).
4. WI-63 stays open; it is a separate `/light` task.
5. Both figures of `brainstorming/examples/demo_complex.md` pass `render_check.py` with a
   `lifeline_through_label` warning each, inherited from canonical: a label crosses the DB
   lifeline. A new participant order is a layout task of its own.
6. `Universal-skills/CLAUDE.md` names only `GEMINI.md` as its lockstep twin, while `AGENTS.md`
   mirrors it too; the cycle-1 MAJOR came from that gap.
