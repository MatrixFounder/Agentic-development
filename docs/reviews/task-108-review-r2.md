# TASK 108 review, round 2 — `task-reviewer` on TASK revision 2

- **Reviewer:** `task-reviewer` (read-only subagent), 2026-10-02.
- **Reviewed:** `docs/TASK.md` revision 2, sha256 prefix `e61faf4087e3121d` as the brief supplied it.
- **Evidence in the brief:** `scan_register.py docs/TASK.md` → `0 warn / 2 info`;
  `check_positional_refs.py --all docs/TASK.md` → `OK: 13 of 13`.
- **Kept by:** the orchestrator, from the reviewer's hand-back. The verdict, the round-1 status
  table and every MAJOR finding are kept with their claim and fix; the MINOR findings are condensed.
  TASK revision 3 answers this round (§8 there maps each finding).

---

**Verdict: APPROVED WITH CHANGES. 0 BLOCKING, 13 MAJOR, 18 MINOR.** The verdict covers TASK.md
only: other files changed while the reviewer read them, so citations into them are not pinned.

## Round-1 findings

| Finding | Status | What remains |
| :--- | :--- | :--- |
| B1 | partly resolved | MAJOR-1 |
| B2 | resolved | MINOR-5 |
| M1 | resolved | the new D8 criterion "M1" has its own defect (MAJOR-2) |
| M2 | partly resolved | MAJOR-2, MAJOR-3 |
| M3 | partly resolved | MAJOR-4 |
| M4 | resolved | MINOR-4 (the rule's severity is unstated) |
| M5 | resolved | MINOR-13 |
| M6 | partly resolved | MAJOR-5 |
| M7 | resolved | MINOR-14 |
| M8 | resolved | MAJOR-10 is a new finding, on D9 |
| M9 | resolved | MINOR-16 |
| M10 | partly resolved | MAJOR-13; the missing step in UC-5 is part of MAJOR-4 |
| M11 | partly resolved | MAJOR-12 |
| M12 | resolved | MINOR-12 |
| M13 | resolved | MAJOR-6 is a new finding |
| M14, M15 | resolved | none |
| m1–m23 | cannot be assessed one by one | the round-1 report was not saved |

## MAJOR

- **MAJOR-1 — the run writes outside the repository beyond the three kinds §3 lists:** renderer
  installs and viewer bundles already in the scratch directory; the npm cache under `~/.npm`;
  Claude Code session transcripts of the eval runs; the browser's temporary profile. "None is a copy
  of a repository file" is false (the skill text inside transcripts; manifests copied by `npm ci`),
  and `framework-upgrade` §3.1 has a second rule, "No copy of any file is written outside version
  control". Fix: redirect what can be redirected (npm cache, session persistence off, browser
  profile), list the rest in §3, cite both rules, confirm the complete list with the operator.
- **MAJOR-2 — D8 sends failures a revision cannot fix into the revision round, and Δ_H is
  undefined.** V1–V3 and the lower half of criterion "M1" cannot move with a skill revision; "≤ 0.2
  without the skill" measures baseline habit; Δ_H has no unit, no case set, no rule for a run
  without a figure. Fix: evaluate validity first and fix the instrument without spending the round;
  report the without-skill contract rate for information; define Δ_H inside D8.
- **MAJOR-3 — the 60 USD cap has no measure and no stop rule.** Fix: sum `total_cost_usd`, refuse
  a run that would cross the cap, project a round's cost before it starts, run round 2 on
  `with_skill` only, and mark criteria `not evaluated (budget)` when the money runs out.
- **MAJOR-4 — the calibration procedure cannot be followed.** UC-5 has no labelling step; no rule
  reaches 3 positives per defect type; κ names no second rater; F1 and F2 outputs are not figures;
  the labels' location is unstated. Fix: run, render, seeded stratified sample over all outputs,
  label, commit, grade; a top-up rule; κ as label-versus-detector agreement.
- **MAJOR-5 — the dark render is mandatory in name only.** `--no-dark` drops it with no effect on
  the verdict; nothing measured differs between light and dark; the corpus gets no dark render.
  Fix: measure text contrast against its actual background per render, a 4.5:1 dark threshold,
  `--no-dark` reported as `not rendered`, a dark render in the corpus.
- **MAJOR-6 — every `text` fence is treated as an ASCII figure.** ARCHITECTURE §2 holds a 45-entry
  directory tree in a `text` fence. Fix: a marker in the info string; listings are not figures.
- **MAJOR-7 — caption and legend have no fixed position, yet the contract checks position.** Fix:
  caption above and legend below for the lint and the contract check; either side for the headline.
- **MAJOR-8 — stored geometry is not tied to the figure it measures.** Fix: each entry records the
  fence's sha256 and the renderer and browser versions; the test recomputes the hash.
- **MAJOR-9 — sequence message and note lengths have no unit.** Fix: characters per line and a
  maximum line count, as D25 does for nodes and edges.
- **MAJOR-10 — D9's "only `--check`" cannot be enforced as written.** Fix: `--write` and `--check`
  mutually exclusive, `--check` writes nothing, the lint writes no file, exact patterns in R10.
- **MAJOR-11 — the form cases have no defined bundle and no acceptable form.** Fix: the key names
  the kind as the prompt states it and the acceptable forms; F1 and F2 get `SKILL.md` alone; C8's
  acceptable forms stated.
- **MAJOR-12 — R7's setup and safety requirements trace to no acceptance criterion.** Fix:
  criteria for the not-rendered exit, the setup dry run, the template renders, and the security
  round's check of sandbox, `strict` and request blocking.
- **MAJOR-13 — UC-1 has no path for a failing render and no pass condition for the document.**
  Fix: an alternative for exit 1 with at most 3 rounds, then a simpler form; 0 `error` on the
  fences the edit adds or touches.

## MINOR (condensed)

1 figure scope of §1 (six more figures outside archives); 2 the line-49 quote not verbatim;
3 D20's reference to §7.4; 4 undefined lint rules (one edge per pair across kinds, structure vs
decision flow, planarity severity, line counts, edges through labels); 5 R8 wording (compared
properties, `status` in the Markdown block, exits without markers, plans under 8 tasks); 6 render
environment (browser build, font, no cached browser, output format and directory); 7 environment
variables and effort (authentication kept, effort overridden); 8 C0 undefined, two spellings of
H-core, criterion "M1" colliding with finding M1; 9 hashes "recorded first" uncheckable;
10 routing table found by an English header; 11 bundle word limit untested; 12 rule ids compared
one way; 13 the forbidden-value list of the wiring test; 14 use-case verdicts (UC-4 A1, UC-6 with
absent renderers); 15 minor findings mapped as one block; 16 assumptions and a performance target;
17 the 10.9.3 claim not re-checkable; 18 F1 does not test how D2 delivers the medium rule.

## Order of fixes the reviewer set

Before the hashes of R11.10: MAJOR-2, -3, -4, -11, MINOR-8, -9. Before merging the lint, the
render check and the plan generator: MAJOR-5 to -10, -12, -13. Before the next write outside the
repository: MAJOR-1.
