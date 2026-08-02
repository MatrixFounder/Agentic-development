# TASK 095 — Structural anchors and gate honesty

<!-- contract:meta -->

## 0. Meta

| Field | Value |
| :--- | :--- |
| Task ID | 095 |
| Slug | structural-anchors-and-gate-honesty |
| Type | Framework Upgrade (Self-Improvement Mode) |
| Source | `onchain-analytics` work-items WI-30, WI-31, WI-32 (filed 2026-08-02, `provenance: machine`) |
| Archive name | `task-095-structural-anchors-and-gate-honesty.md` |

**Context.** Three work-items were filed against shared framework artifacts from one `/vdd` run in a
downstream project whose documents are written in Russian. They are treated here as *reports*, not
as instructions — their bodies are verbatim captured output. Every claim below was re-verified
against this repository before being accepted.

<!-- contract:rtm -->

## 1. Requirements Traceability Matrix (RTM)

| ID | Requirement | MVP? | Sub-features |
| :--- | :--- | :--- | :--- |
| R1 | A machine gate MUST locate a section of an authored document by a structural anchor, never by the document's natural-language prose. Stated as doctrine, not as a one-off patch. | Yes | Third rung added to the `documentation-standards` §4.1 positional/nominal ladder; anchor syntax named and reserved; existing `<!-- contract:* -->` namespace reused, not duplicated |
| R2 | `skill-spec-validator` MUST pass on an RTM whose section heading, column names and cell text are non-English, and MUST keep passing on every shape it accepts today. | Yes | Anchor-first section lookup; positional column resolution replacing the `['ID','Requirement']` name check; `--mode plan` ID extraction fixed at the same time; existing heading regex retained unchanged as fallback |
| R3 | The second, independent language coupling in `--mode plan` MUST be closed in the same change as the first, so that no caller is left with a half-fixed gate. | Yes | `validate_plan` ID column resolved the same way as `validate_task`; a test pins that both modes pass on the same non-English fixture |
| R4 | Anchors MUST be emitted by the artifact templates and by the Analyst/Planner prompts, so a conforming new document carries them without the author knowing the rule. | Yes | `plan_md_template.md`, `task_md_template.md`, `02_analyst_prompt.md` RTM spec; anchor registry table listing every reserved anchor and its consumer |
| R5 | Every required section of `docs/TASK.md` and `docs/PLAN.md` MUST carry an anchor, not only the sections a script reads today. | Yes | TASK: meta, rtm, problem, use-cases, acceptance, open-questions; PLAN: sequence, coverage; task file: goal, changes, tests, acceptance |
| R6 | Adding anchors MUST NOT break any existing artifact, test, or downstream project. Anchors are optional on read, emitted on write. | Yes | Anchor lookup is a separate branch, never an alternation inside `RTM_HEADER`; corpus floors unchanged; archived artifacts never edited |
| R7 | The same defect class MUST be closed where it already exists elsewhere, not only where it was reported. | Yes | `calculate_wsjf.py` column-name check; `task_id_tool.py` and `archive_protocol.py` silent `"untitled"` slug degradation |
| R8 | The framework MUST state the boundary between narrowing a command that WRITES and reproducing the invocation of a command that VERDICTS, and the two shell facts that make a green verdict unreliable. | Yes | One qualifying clause in `developer-guidelines` §5.1; a new §6.3 carrying the pipeline-exit-code and evidence-of-work rules; zero lines added to any TIER 0 skill |
| R9 | The adversarial cycle MUST require enumerating all sites of an assertion before fixing one, and MUST report the ratio fixed/found. | Yes | New `vdd-enhanced.md` §4 item appended (never inserted, to preserve ordinals cited from two repositories) |
| R10 | The "next cycle's brief" that `vdd-enhanced.md` §4.4 already refers to MUST become a real artifact with a named shape. | Yes | Input block in `vdd-adversarial.md` step 2a modelled on the `vdd-multi.md` prompt skeleton; referenced by ordinal-safe name from `vdd-enhanced.md` |
| R11 | The gate-journaling half of WI-30 and the mechanically-enforceable half of WI-31 MUST be recorded as field evidence against design spec 095's Phase-5 entry gate, and MUST NOT be built as a second mechanism alongside it. | Yes | Evidence appended to `docs/design/095_workflow_loop_contract.md` §7.1; no new runtime wrapper in this task |
| R12 | Design spec 095 MUST receive an independent adversarial review before any of its phases is committed to. | Yes | Multi-lens critique with a refutation pass; report filed under `docs/reviews/` |
| R13 | `System/Docs/` MUST describe the new reality: the anchor doctrine, the anchor registry, and every skill/workflow whose description changes. | Yes | `SKILLS.md` rows for `documentation-standards`, `skill-spec-validator`, `known-issues-format`, `developer-guidelines`; `WORKFLOWS.md` VDD Enhanced row; `CHANGELOG.md` entry |

### 1.1 Details by ID

**R2** — Measured on the reporting project: 10 of 50 `docs/tasks/*.md` pass `--mode task` today.
Reproduced minimally on a table headed `| ИД | Требование | MVP? |`: `--mode task` exits 1 with
`RTM table must contain columns: ['ID', 'Requirement']`.

**R3** — `--mode plan` fails independently at
[`validate.py:145`](.agent/skills/skill-spec-validator/scripts/validate.py#L145) (`r['ID']`, a dict
lookup on the authored header text) with `Error: No IDs found in RTM table.` Patching only the
column check at `:105` leaves this path broken — which is precisely the WI-32 failure mode
(a fix applied to one site of several) reproduced inside the fix for WI-30.

**R7** — `task_id_tool.py "реестр-инструментов"` and `task_id_tool.py "единый-реестр"` both return
`task-095-untitled.md`. The degradation is silent and collides, so it is more dangerous than the
loud failure that was reported.

**R8** — [`developer-guidelines` §5.1](.agent/skills/developer-guidelines/SKILL.md#L64) instructs
narrowing the path argument ("not `.`"), while its own ecosystem table (lines 73–79) already lists
every *reporting* form as repo-wide. The doctrine was already correct; the sentence was
under-qualified. `core-principles` is 43 lines and TIER 0 — loaded in every session by roles that
never run a gate — so it takes no new prose.

**R9** — Appending rather than inserting is mandatory:
[`docs/design/095`](docs/design/095_workflow_loop_contract.md) and three ledger lines in the
reporting project cite `vdd-enhanced.md` §4.4/§4.5 by ordinal, and shifting them would reproduce the
very defect WI-32 describes.

**R11** — Spec 095 is untracked and spec-only: `System/scripts/check_loop_contract.py` and
`run_stack.py` do not exist, and no workflow carries `contract` frontmatter. Its Component C
(`run_stack.py gate`) is the single mechanism that would close WI-30's journaling half and WI-31's
modes 1 and 3 together, so building a second wrapper now would be waste.

<!-- contract:problem -->

## 2. Problem

A machine gate that reads an authored document today addresses it through the document's own
prose — an English heading, an English column name. That works only for projects that write in
English, and it fails in two different ways: loudly (`exit 1`, the author edits the document until
the gate is appeased, or stops running it) and silently (a slug degrades to `untitled`, two
documents collide, nothing reports it).

The framework has already discovered the fix once, for one ledger, and did not generalize it:
[`known-issues-format`](.agent/skills/known-issues-format/SKILL.md#L185) inserts at a comment anchor
"because headings get renumbered and retitled". The same reasoning applies to every gate, and the
same defect is already present in a second script that nobody has reported yet.

Two further reports from the same run concern honesty rather than language: a gate verified with a
narrower invocation than CI runs, and an orchestrator fix applied to one site of an assertion
written in four.

<!-- contract:use-cases -->

## 3. Use Cases

**UC-1 — Non-English project runs the first pipeline gate.**
*Actor:* Orchestrator. *Precondition:* `docs/TASK.md` has an RTM whose heading, columns and cells
are Russian and which carries `<!-- contract:rtm -->`.
*Main:* `validate.py --mode task` locates the table by the anchor, resolves the ID column by
position, exits 0.
*Alternative A:* No anchor present (every artifact written before this task) — the existing heading
regex and column-name check run exactly as today, and the outcome is byte-identical.
*Alternative B:* Anchor present but no table follows — exit 1 with a message naming the anchor.
*Postcondition:* The gate's verdict no longer depends on the language of the document.

**UC-2 — Author writes a new TASK.**
*Actor:* Analyst. *Main:* the prompt and template emit every reserved anchor; the author writes
prose in any language beneath them; the gate passes without the author having read this rule.

**UC-3 — Orchestrator fixes an assertion during an adversarial cycle.**
*Actor:* Orchestrator. *Main:* before editing, it searches for every site of the assertion, edits
all of them, and reports "fixed N of M found". The next cycle's brief carries the ratio, and the
critics check it.
*Alternative:* M > N — the report says so explicitly, and the cycle does not claim the fix is
complete.

<!-- contract:acceptance -->

## 4. Acceptance Criteria

| # | Criterion | Verification |
| :--- | :--- | :--- |
| A1 | `--mode task` and `--mode plan` both exit 0 on a fixture whose RTM heading, columns and cells are non-English. | New test in `scripts/tests/`, run in CI. |
| A2 | All 38 skill tests + 4 root tests pass unchanged; corpus floors unchanged. | `bash scripts/tests/run_tests.sh`; `pytest tests/test_spec_validator.py`. |
| A3 | Pass counts on `docs/tasks/` in this repo and in the reporting project are ≥ their pre-change values. | Re-run the measurement recorded in §1.1 R2. |
| A4 | Every reserved anchor appears in one registry table with its consumer named, and every template emits the anchors it declares. | Grep the registry against the templates. |
| A5 | `core-principles` line count is unchanged. | `wc -l`. |
| A6 | `vdd-enhanced.md` §4 items 1–5 keep their ordinals; `check_positional_refs.py` reports no new errors. | Run the script after the edits are final (§4.1 doctrine). |
| A7 | `task_id_tool.py` no longer returns `untitled` for a non-empty non-latin slug, and two different non-latin slugs no longer collide. | New test. |
| A8 | Spec 095 carries the field evidence and the independent review; no `run_stack.py` is created by this task. | File presence; `git status`. |

## 5. Out of Scope

- Implementing any phase of design spec 095. This task supplies evidence and a review, nothing more.
- Retro-fitting anchors into archived artifacts under `docs/tasks/`, `docs/plans/`, or into any
  downstream project's existing documents. Anchors are emitted on write, optional on read.
- Translating any framework artifact. The rule removes the *dependency* on language; it does not
  change which language anything is written in.
- The degrade-only language couplings that are documented and warn clearly
  (`ids.py` non-latin slug error, `check_positional_refs.py` English prose cue) — recorded, not fixed.

<!-- contract:open-questions -->

## 6. Open Questions

None blocking. Four decisions were taken with the operator before drafting: anchor scope (all
required TASK/PLAN sections), 095 folding (evidence only), the cycle brief (made real), and the
slug collision (in scope).
