# TASK 108 review, round 1 — `task-reviewer` on TASK revision 1

- **Reviewer:** `task-reviewer` (read-only subagent), 2026-10-02.
- **Reviewed:** `docs/TASK.md` revision 1, base `ee69bf2`, before the PLAN existed.
- **Kept by:** the orchestrator, from the reviewer's hand-back, as TASK 108 §8 requires. The header,
  the assessment and both BLOCKING findings are verbatim. Each MAJOR and MINOR finding is kept as
  its claim and its fix, condensed. TASK revision 2 answered this round.

---

**Verdict: REJECTED.** Status BLOCKING: 2 blocking findings. Most MAJOR findings need only one or
two added sentences, or one of the operator questions listed near the end.

- **Date:** 2026-10-02
- **Reviewer:** task-reviewer (read-only subagent), applying `System/Agents/03_task_reviewer_prompt.md` and `task-review-checklist`.
- **Tree fingerprint:** none in the brief. These findings are not pinned to a tree state, so APPROVED was never available on this reading. I read the working tree as it stood at session start: HEAD `ee69bf2`, which equals the TASK's Base revision, with `M docs/TASK.md`, `D docs/PLAN.md` and the 107 archive pair untracked.
- **Execution evidence:** none was supplied, so two checklist sections stay unverified.
  - **Register scan (checklist §6):** NOT RUN — no execution tool in this role, and no output in the brief. I did a manual reading pass instead (m8).
  - **Positional-reference resolver (§7):** NOT RUN, same reason. I checked 5 coordinates by hand: 4 hold, 1 points at the wrong line (m2).
  - **`skill-session-state` §3:** skipped, because this role is read-only.
- **Review file:** I did not write `docs/reviews/task-108-review.md`; persisting this text is yours.

## General assessment

The TASK is well evidenced:
- Renderer versions are measured.
- Every decision records its rejected alternative.
- Eval keys are written and hashed before any run.
- The grader imports the lint rather than copying it (ARCHITECTURE §7.6).
- The two eval arms differ in one input, and a byte-for-byte selftest checks that (L5 holds).
- Captions and legends are detected by position, not by words (L1 holds there).

I verified the cited counts:
- `WORKFLOWS.md:37` has 26 nodes.
- `WORKFLOWS.md:383` has 15 nodes and 16 edges.
- `demo_complex.md:68` has 8 participants.
- `architecture-format-extended:48` is the PlantUML line.

The defects fall into five groups:
1. The run needs things the framework-upgrade workflow forbids: writes outside the repo and a commit.
2. The plan chart has no input source in the framework's own plan template, and the obvious way to parse it breaks L1.
3. The eval headline partly measures the skill's own conventions, and nothing says what happens if the eval fails.
4. Integration misses the caller side of review evidence and leaves a reversed form ladder in `brainstorming`.
5. Several numbers in the requirements contradict decisions D14 and D4.

## How the operator's asks are covered

| Ask | Covered by | Gap |
| :--- | :--- | :--- |
| Professional look | R3, R4, R7.6, R9 | — |
| Colourings | R4.4, R3.8, palette as a contract check | No palette requirement; colour not in the headline (M1, m22) |
| Legend | R3.7, D13 | Position check proves presence only (m19) |
| Structure | R3.1, R3.4, R6.3 | — |
| Planarity | R3.3, R6.3, R2.4 | Lint bound misses K3,3 (M4) |
| Several kinds incl. plan chart | R4, R8 | No input source in the template (B2) |
| Best practices | R9 (draft pairs), R5 | No external sources (m22) |
| Integrate wherever figures are made | R10 | Caller side, brainstorming, settings, chat trigger (M7, M8) |
| skill-creator process | R1 | Its eval tooling unused, no decision recorded (M14) |
| Evals proving a large gap | R11, D8 | No failure path, no budget, validity gaps (M1–M3) |
| ASCII/table for simple figures; not Mermaid everywhere | R2, D7, UC-3 | Trigger never reaches terminal answers (M8); ASCII untested in documents (m23) |

## BLOCKING

**B1 — The run writes outside the repository and needs a commit; the workflow forbids both.**
TASK lines 185-186, 196, 248-250, 259, 260-262, 331, 333, 335, 394-395.

- `.agent/workflows/framework-upgrade.md:87-88` says "No path outside this repository is edited during the run."
- `:79-80` says "The run commits nothing", and the Fallback's step 0 (`:119-123`) STOPs if a commit exists.
- The TASK nevertheless requires, during this run: renderer installs in `~/.cache/...` (R7.2); renders written outside the repo (R7.8); `claude -p` runs in temp directories (R11.4); render evidence for A3, A5, A7, R9.3 and R4.3; D8 "committed before the first paid run" (R11.9).
- D10 claims the TASK complies with §3.1, which contradicts all of the above.
- Lines 23-24 cite scratch renders from this run. If those sit outside the repo, the deviation has already happened.

**Fix:** add operator question OQ-A and record the answer as a Deviation, using the authoring
contract's form. Option (a): the operator licenses the renderer cache, a named render scratch
directory and the eval temp directories for this run. Option (b): move the render-evidence and
campaign work to a run after the operator's commit. In R11.9, replace "committed" with "written to
`<path>`, with its sha256 recorded in `docs/reviews/framework-audit-108.md`, before the first paid
run". If the campaign stays in this run, give its files deterministic names so §2.2 can declare
every path.

**B2 — The plan chart has no language-independent input.** TASK lines 200-201, 226-227, 234-235, 301.

- R8.1 accepts "a plan in the `skill-planning-format` template form".
- That template (`plan_md_template.md:25-29`) has `Use Cases`, `Description File`, `Priority` and `Dependencies`. It has no estimate field and no stage id.
- So UC-2's precondition, "tasks with estimates", never holds for a plan written from the template. R10.3 still requires the planner to include a chart it cannot generate.
- Parsing the template form means matching `Task`, `Stage` and `Dependencies:`. Those are English prose fields that consumer projects translate.
- That contradicts invariant L1 (`docs/ARCHITECTURE.md:237`), which the TASK applies to captions in D13 but not here.

**Fix:** one machine-readable line per task in the plan template, or a JSON block under a
registered anchor; estimates are integer hours; `plan_gantt.py` reads only that; the planner prompt
makes estimates mandatory for plans of 8 or more tasks; a test proves a plan with Russian headings
and labels produces the same chart.

## MAJOR

- **M1 — The headline partly measures the skill's own conventions** (caption/legend by position,
  budgets; fidelity matching unspecified; form cases unscored; colouring missing; the plan-chart
  case cannot run tool-less). Fix: move position rules and soft budgets to the contract family,
  hard budgets only in the headline, aliases and families per key, contrast and "colour is not the
  only cue" in the headline, and a plan chart left out of the campaign or pre-generated.
- **M2 — No failure path and no budget for the paid campaign.** A7 passes as soon as `report.json`
  exists; Δ_H ≥ 0.25 is the orchestrator's reading of "much worse"; 66 runs at `xhigh` have no
  token estimate, cap or approver (about 5–6M tokens at 85k per run). Fix: operator question OQ-B
  (thresholds, budget and cap, failure path) and an acceptance criterion naming the chosen path.
- **M3 — The calibration set and case provenance are under-specified.** No set size, no minimum
  positives per defect type, no agreement metric; a model labeller is same-model corroboration;
  the skill author writes the cases in the same run. Fix: at least k positives and k negatives per
  type sampled before grading; Cohen's kappa or per-class precision/recall; OQ-C for the labeller,
  V2 marked `corroborated` when the model labels; record that cases and keys were hashed before the
  skill content existed, or have a separate agent write them.
- **M4 — The planarity lint misses the TASK's own example.** `E ≤ 3V − 6` is necessary, not
  sufficient; K3,3 has V=6, E=9 and 9 ≤ 12. Fix: an exact planarity test (LR or Boyer–Myrvold,
  feasible at ≤ 18 nodes in the standard library), or at minimum `E ≤ 2V − 4` for triangle-free
  graphs; a non-planar finding points to a table or a split.
- **M5 — R2.5, R4.5 and R3.2 contradict D14** (ASCII 8 vs 8/12, ER 8 vs 8/10, a tree exemption
  for a figure that is not a tree). Fix: cite D14; the exemption becomes "a figure that passes the
  R7.6 thresholds".
- **M6 — D4 says every figure gets a dark render; R7.4 makes it optional.** Fix: dark by default
  for UC-1, A5 and R9.3, or narrow D4 and add a lint rule against a pinned `theme`.
- **M7 — Missing render evidence would stall every review gate**, and the caller side is missing
  from the checklists' Script Contracts. Fix (OQ-E): lint output required, render output optional,
  `not rendered (<reason>)` distinct from `NOT RUN`, both commands in each Script Contract, a UC-4
  postcondition.
- **M8 — Integration leaves contradictions and gaps:** `brainstorming` orders Mermaid before ASCII
  and lists; D2's trigger misses terminal answers; `.claude/settings.json` is edited but not listed.
  Fix: a Step 0 pointer in brainstorming, the medium rule in the bootstrap files, settings in R10.
- **M9 — No non-functional, security or compatibility requirements** (lockfiles and
  `npm ci --ignore-scripts`; sandbox and `securityLevel: strict`; no network at render time; no
  browser → exit 3; the permission scope as OQ-D; Python and Node floors; OS).
- **M10 — Use cases are incomplete** (UC-3 precondition and alternatives; UC-4 postcondition; UC-5
  preconditions and alternatives; UC-2 re-plan and > 60 bars; a living document with an old figure;
  UC-1 A3 "draws nothing" loses information).
- **M11 — Acceptance criteria don't trace to the RTM, and three can't be executed as written**
  (A3 without a measurement; A5 without persisted evidence; A9 omitting `selftest_scan.py`
  TC-SHIP-08 and `check_prompt_references.py`). Fix: an Acceptance column, A3 as bar start against
  the computed early start read from the SVG, render evidence as JSON with versions, A9 as "every job
  of `framework-gates.yml` passes", R12.3 extended to TC-SHIP-08.
- **M12 — The lint's rule list is checked against itself.** Fix: the test holds the rule ids as a
  literal list (ARCHITECTURE §7.5 records the "17/17 detectors live" failure).
- **M13 — "The lint is CI-gated" has no defined scope.** Fix: gate only the skill's own files; run
  any repo-wide sweep as advisory.
- **M14 — The eval ignores skill-creator's eval tooling and records no reason.** Fix: a decision per
  departure (subagents inherit `CLAUDE.md`, which breaks L5), skill-creator schemas where they fit,
  a CI pin that rebuilds `report.json` from the committed files.
- **M15 — The scope does not fit one framework-upgrade run.** Fix: three runs, or an operator
  decision (OQ-F).

## MINOR

m1 population of the "7 figures"; m2 wrong line cited for the "diagrams" claim; m3 an ambiguous
list in R8.3; m4 marker syntax `generated:plan-gantt start` breaks §4.3 (use `-start` / `-end`);
m5 exit codes disagree across the scripts and with ARCHITECTURE §7.4; m6 `status` field vs D11;
m7 OQ1 is not in the Open Question form; m8 register points (a three-sentence Goal; R2.1
uncheckable; R3.3 reads as "every pair"; D5 unclear; R7.6 better as a list); m9 label length in
characters, not words; m10 "a chat" may render Mermaid; m11 statistics of H3 and the sign test;
m12 `CLAUDE_*` does not match `CLAUDECODE`, and why reps are odd; m13 A10 and A11 scope; m14
clipped labels need DOM measurement, and a named render directory; m15 JetBrains ships 10.9.3;
m16 the gerund naming departure; m17 single source — surfaces restate no threshold; m18 P15 has no
negative, and each negative must fail a named rule; m19 a caption is a paragraph, a legend one item
per encoding; m20 unspecified changes (reverse-engineering, blueprint, 05 line 49); m21 process
(`analyze_gaps.py`, a token budget for SKILL.md and bundles); m22 sources and palette (WCAG SC
1.4.3, crossing literature, Okabe–Ito); m23 ASCII untested inside documents.

## Open questions (owner: operator)

OQ-A licence for writes outside the repo; OQ-B thresholds, budget and failure path; OQ-C the
calibration labeller; OQ-D auto-run commands in `.claude/settings.json`; OQ-E review evidence
without renders; OQ-F one run or three.

## Recommendation

Return the TASK to the analyst. B1 needs an operator decision; B2 needs a requirement change
before Architecture. Re-review only the changed sections, with a tree fingerprint and the outputs of
the register scan and the reference resolver in the next brief.
