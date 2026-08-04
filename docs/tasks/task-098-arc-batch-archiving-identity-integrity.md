# TASK 098 — Archiving identity: close the ARC-3…ARC-12 defect batch

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 098 |
| Slug | arc-batch-archiving-identity-integrity |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | Operator request 2026-08-04: close `ARC-*`; `/heal-issues` returned NO-OP (zero eligible) |
| Depends on | TASK 096 (`tasks/task-096-artifact-register-formalization.md`) |
| Closes | ARC-3, ARC-4, ARC-5, ARC-6, ARC-7, ARC-8, ARC-9, ARC-10, ARC-11, ARC-12, WIR-10 |
| Archive name | `task-098-arc-batch-archiving-identity-integrity.md` |

<!-- contract:problem -->

## 1. Problem

Commit `992b3ef` closed ARC-1 and ARC-2. A 7-dimension adversarial review of that commit filed ten
further defects in `archiving`. Each was reproduced by an independent verifier against the committed
tree. All ten remain `status: open`.

`/heal-issues` cannot take them. Three rails refuse: `auto_fixable` is absent on all ten, no gate in
`docs/feedback/heal-config.json` maps their components, and no `## Reproduction` section carries a
fenced `sh` block. The bounded healer also caps a run at one issue and 300 lines.

The ten defects form four groups. Members of a group share one root cause and are fixed together.

**Group A — `allow_correction` polarity differs per call surface.** ARC-1 established that a renumbered
ID is reported as `conflict`, never applied. The commit flipped `schemas.py` and `System/scripts/tool_runner.py`. It
did not flip `.agent/tools/task_id_tool.py:165` (`allow_correction: bool = True`), and the CLI at
`:291-301` offers only the opt-out `--no-correction`. Two surfaces refuse a conflict, two renumber
it. Covers ARC-7, ARC-8, ARC-9.

**Why.** `test_schema_default_matches_tool_runner_default` asserts one schema literal ⇒ reverting
`tool_runner.py` to the pre-flip default leaves 39 tests green (measured by the ARC-9 verifier).

**Group B — the meta reader refuses an identity, the caller proceeds anyway.**
`archive_protocol.parse_task_meta` returns `task_id: None` when the meta table carries two 3-digit
values. Its comment at `:116-119` states that None routes to the caller's STOP path. `archive_task`
at `:244-249` has no such branch: None becomes the literal `untitled` and an auto-generated ID. The
Step 4 ID write-back at `:288` matches the English literal `Task ID`, while the read above it is
language-agnostic by construction. Covers ARC-3, ARC-12.

**Group C — `rebase_links.py` exit 1 is unreachable.** The conservation probe at `:347-353` re-joins
a path that `:249` produced by `relpath` from a path `:235` proved present. The probe therefore
reconstructs an existing path in every case, `failed` never becomes True, and `return 1` at `:388` is
dead. `SLOT_RESOLVED` appears in neither `ACTIONS_WARN` nor `_CONSERVED`, so a slot map naming an
absent target exits 0 with `"ok": true`. Covers ARC-5, ARC-6.

**Group D — the shipped protocol contradicts the tested rule.** `skill-archive-task` Step 5.5 passes
`--slot docs/PLAN.md=…` with no condition; `archive_protocol.py:363-366` maps that slot only when
`docs/PLAN.md` exists, pinned by `TestPlanSlotIsConditional`. Step 7.4 still instructs the agent to
prefer the post-correction `used_id` over the Meta block, which Step 4 forbids. `.claude/agents/planner.md:12`
tells the planner subagent to generate IDs, which `06_planner_prompt.md:40` forbids. Covers ARC-4,
ARC-10, ARC-11.

**Measured, this repository, 2026-08-04.** `python3 .agent/tools/task_id_tool.py "structural-anchors"`
returns `used_id: 097` while the live `docs/TASK.md` Meta row read `096`.

<!-- contract:rtm -->

## 2. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Closes |
| :--- | :--- | :--- | :--- |
| R1 | `allow_correction` carries one default across all four call surfaces | Y | ARC-7, ARC-8 |
| R2 | The four-surface test observes behaviour, not a schema literal | Y | ARC-9 |
| R3 | `archive_task` stops when a present meta block yields no readable identity | Y | ARC-3 |
| R4 | The ID write-back addresses the meta table by structure, not by a label | Y | ARC-12 |
| R5 | `rebase_links.py` exit code 1 is reachable and names one condition | Y | ARC-5, ARC-6 |
| R6 | `skill-archive-task` states the rule that `archive_protocol.py` implements | Y | ARC-4, ARC-6, ARC-10 |
| R7 | Every agent card states the planner's ID rule | Y | ARC-11 |
| R8 | Each fix carries a test that fails when the fix is reverted | Y | all |
| R9 | `System/Docs/` states the invocation form and the test count this task leaves behind | Y | all |

### 2.1 Sub-features

**R1.** The Python signature defaults to `False`. The CLI gains the opt-in `--allow-correction`. The
CLI keeps accepting `--no-correction`. One behavioural test covers each surface.

**R2.** The dispatcher is invoked with the argument omitted. The Python function is called without
the keyword. The CLI runs as a subprocess. Each of the three asserts `conflict`.

**R3.** `parse_task_meta` reports why it refused an identity. `archive_task` returns `status: error`
on a refusal. A meta block carrying no ID row still auto-generates.

**R4.** The target row is located inside the meta region. A table offering no single empty value cell
is refused. The result dict reports the write-back outcome.

**R5.** A caller declares that slot targets already exist. A declared-present target that is absent
sets the failure flag. The docstring exit table matches the code.

**R6.** Step 5.5 maps the PLAN slot on a condition. The Example Flow repeats that condition. Step
7.6.5 passes the existence assertion. Step 7.4 and the Edge Cases row cite the Meta block.

**R7.** `.claude/agents/planner.md` reuses the parent Meta ID. The card cites
`06_planner_prompt.md`. No card retains the bare generate-an-ID form.

**R8.** One test covers each of R1–R7. The revert that turns it red is named in its docstring. The
suites run under the repository CI workflow.

**R9.** `ORCHESTRATOR.md:8` states the shortest correct invocation. `ORCHESTRATOR.md:284` states the
current test count. `CHANGELOG.md` and `CHANGELOG.ru.md` receive a paired entry.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — an agent archives a task whose ID is already taken.**

1. The agent reads Meta ID `042` and runs the CLI without a correction flag.
2. `docs/tasks/task-042-*.md` exists as a parent archive.
3. The tool returns `status: conflict` and exits 1.
4. The agent stops and reports both paths to the operator.

*Alternative 3a.* The operator passes `--allow-correction`. The tool returns `status: corrected` and
the agent proceeds under an explicit instruction.

**UC-2 — a non-English TASK.md carries an ambiguous meta table.**

1. `docs/TASK.md` holds `| Приоритет | 001 |` and `| ИД задачи | 095 |` inside the meta region.
2. `parse_task_meta` finds two 3-digit values and refuses.
3. `archive_task` returns `status: error` with the refusal reason.
4. No file moves and `docs/TASK.md` stays in place.

**UC-3 — a new task carries an empty ID row in a non-English meta table.**

1. `docs/TASK.md` holds `| ИД задачи |  |` and `| Слаг | novaya-fitcha |`.
2. `parse_task_meta` finds no ID and one empty value cell.
3. `archive_task` auto-generates the ID and writes it into that row.
4. The result dict reports the write-back as performed.

**UC-4 — the agent mistypes a slug in the Step 7.6.5 slot map.**

1. The TASK archive is `task-077-login.md`; the agent passes `task-077-logn.md`.
2. `rebase_links.py` runs with the existence assertion enabled.
3. The declared target is absent, so the tool exits 1.
4. Step 7.7 fails its assertion and the agent stops before committing.

**UC-5 — a task reaches analysis but never planning.**

1. `docs/PLAN.md` does not exist.
2. Step 5.5 omits the PLAN slot, matching `archive_protocol.py:363-366`.
3. A link to `PLAN.md` is reported as an unmapped slot rather than rewritten.
4. The exit code is 3 and the agent reports the link.

**UC-6 — the planner writes sub-task files for TASK 096.**

1. The planner subagent reads Meta ID `096`.
2. The card instructs it to reuse that ID for every sub-task filename.
3. Files land as `task-096-01-*.md`.
4. No invocation of the ID tool occurs.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| ID | Criterion | Verification |
| :--- | :--- | :--- |
| A1 | `generate_task_archive_filename` signature reads `allow_correction: bool = False` | `grep -n "allow_correction" .agent/tools/task_id_tool.py` |
| A2 | The CLI without a flag returns `conflict` and exits 1 on a real parent collision | subprocess test in `test_task_id_tool.py` |
| A3 | The CLI with `--allow-correction` returns `corrected` and exits 0 | subprocess test in `test_task_id_tool.py` |
| A4 | The bare form with no `--proposed-id` still auto-generates and exits 0 | subprocess test in `test_task_id_tool.py` |
| A5 | Reverting `tool_runner.py` to the pre-flip default turns the four-surface test red | manual mutation, recorded in the report |
| A6 | An ambiguous meta table makes `archive_task` return `status: error` and move no file | `test_archive_protocol.py` |
| A7 | A meta table with no ID row still archives and writes the ID back in any language | `test_archive_protocol.py` |
| A8 | The archive result dict carries the write-back outcome | `test_archive_protocol.py` |
| A9 | `rebase_links.py` exits 1 when a declared-present slot target is absent | `test_rebase_links.py` |
| A10 | `rebase_links.py` exits 0 for a forward-reference slot when the assertion is off | `test_rebase_links.py` |
| A11 | The `rebase_links.py` docstring exit table lists only reachable codes | `grep -n "Exit codes" .agent/tools/rebase_links.py` |
| A12 | `skill-archive-task` Steps 5.5, 7.4, 7.6.5, the Example Flow and the Edge Cases row agree with `archive_protocol.py` | reviewer read against the cited line numbers |
| A13 | `.claude/agents/planner.md` contains no instruction to generate an ID | `grep -n "task_id_tool" .claude/agents/planner.md` |
| A14 | All three archiving suites pass | `python3 -m pytest .agent/tools/ -q` |
| A15 | The register scanner reports no new finding on `docs/TASK.md` and `docs/PLAN.md` | `python3 .agent/skills/artifact-formalizer/scripts/scan_register.py` |
| A16 | Ten issue files and ten `docs/KNOWN_ISSUES.md` index lines flip in lockstep | `grep -c "status \`fixed\`" docs/KNOWN_ISSUES.md` |
| A17 | `ORCHESTRATOR.md` cites the test count that `pytest -q` reports | `grep -n "tests)" System/Docs/ORCHESTRATOR.md` |
| A18 | Both CHANGELOG files carry the entry for this task | `grep -n "098" CHANGELOG.md CHANGELOG.ru.md` |

<!-- contract:open-questions -->

## 5. Open Questions

**OQ-1 — does WIR-10 close as a consequence of R1?** WIR-10 records the same polarity drift on the
CLI and library entry point. Blocks: whether its ledger row flips in this task. Owner: operator.

**Measured 2026-08-04, after R1.** Its reproduction was re-run verbatim against this repository:
`python3 .agent/tools/task_id_tool.py existing-feature --proposed-id 042` now returns
`{"status": "conflict", "message": "ID 042 is occupied. Suggested alternative: 098"}` with rc 1,
where the record measured `{"used_id": "097", "status": "corrected"}` with rc 0. The dispatcher call
returns the same `conflict`. The divergence the record describes does not survive R1.

**Resolved by the operator, 2026-08-04:** flip it. WIR-10 is recorded `fixed` under this task, its
resolution blockquote cites the measurement above, and its `docs/KNOWN_ISSUES.md` index line moves
in lockstep. Scope becomes ARC-3 … ARC-12 plus WIR-10.

**OQ-3 — the `skill-archive-task` validator reports three warnings.** `Execution Mode`,
`Script Contract` and `Validation Evidence` sections are absent. Blocks: nothing; the validator
passes in warning-first mode and the warnings predate this task. Owner: operator.

**OQ-2 — does the conservation probe stay after R5?** The ARC-5 verifier measured it as a tautology
over eight target shapes. Blocks: nothing; both options satisfy A9 and A11. Owner: this task.
Recorded as D3 below.

<!-- contract:decisions -->

## 6. Decisions

**D1, 2026-08-04, this task: the CLI keeps `--no-correction` as an accepted argument.** Rejected:
removing it — six documented invocation sites pass it (`CLAUDE.md:29`, `AGENTS.md:41`, `GEMINI.md:44`,
`ORCHESTRATOR.md:8`, `.agent/skills/skill-archive-task/SKILL.md:73@5c9da31`,
`.agent/skills/skill-archive-task/SKILL.md:310@5c9da31`), and removing it would turn every one into an
argument error.

**D2, 2026-08-04, this task: flipping the CLI default does not affect the bare new-ID form.** With
`proposed_id` absent, `generate_task_archive_filename` returns from the auto-generate branch at
`:206-217` before `allow_correction` is read. `02_analyst_prompt.md:48` and UC-6 are therefore
unchanged.

**D3, 2026-08-04, this task: the conservation probe is retained and stops being advertised as the
slot gate.** Rejected: deleting it — its tautology holds for the current `relpath` implementation,
and the probe is the postcondition that would detect a change to it. The reachable failure named in
the docstring becomes the declared-present slot target.

**D4, 2026-08-04, this task: refusal reasons are carried in the returned dict, not raised.**
Rejected: an exception — `archive_task` returns `status: error` for `tool_error` and `conflict`
already, and a third failure shape would split one contract across two mechanisms.

<!-- contract:out-of-scope -->

## 7. Out of scope

In scope: ARC-3 … ARC-12, and WIR-10 by operator authorisation once R1 made it verified-gone (OQ-1).
Out of scope: the remaining `WIR-*` and all `REG-*` ledger records (a later task);
`docs/feedback/heal-config.json` gate entries (operator, protected path); `auto_fixable` opt-in flags
(operator).
